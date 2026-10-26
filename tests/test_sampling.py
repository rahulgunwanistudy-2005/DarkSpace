import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from darkspace.cache import CompletionCache
from darkspace.cli import sample_run
from darkspace.freeze import freeze, verify
from darkspace.models import AccessEvidence, ProviderResult, SamplingConfig
from darkspace.sample import (
    CONTROL,
    PERSONAS,
    assemble,
    attempts,
    canonical,
    digest,
    request_payload,
)


def config() -> SamplingConfig:
    return SamplingConfig.model_validate_json(Path("configs/current-event.json").read_bytes())


def valid(text: str = "An app helps teachers organize their class materials.") -> ProviderResult:
    return ProviderResult(
        text=json.dumps(
            {
                "idea": text,
                "audience": "teachers",
                "problem": "disorganized material",
                "mechanism": "organize files",
            }
        )
    )


def test_grid_and_control_isolation() -> None:
    current = config()
    grid = attempts(current)
    assert len(grid) == 384
    assert len({item.id for item in grid}) == 384
    for model in current.models:
        assert sum(item.model == model for item in grid) == 96
    assert {item.persona for item in grid} == set(PERSONAS)
    control = current.model_copy(update={"arm": "control"})
    for item in attempts(control):
        assert CONTROL in item.prompt
        assert "Devpost" not in item.prompt
        assert current.brief not in item.prompt
    for event, generic in zip(grid, attempts(control), strict=True):
        assert (event.persona, event.seed, event.template, event.model) == (
            generic.persona,
            generic.seed,
            generic.template,
            generic.model,
        )


def test_release_and_dataset_access_gates() -> None:
    raw = config().model_dump(mode="json")
    raw["event_start"] = "2024-01-01"
    with pytest.raises(ValidationError, match="strictly before"):
        SamplingConfig.model_validate(raw)
    with pytest.raises(ValidationError, match="every access gate"):
        AccessEvidence.model_validate(
            {
                "event": "GovHack 2025",
                "authorized_route": "https://hackerspace.govhack.org/",
                "license_evidence": "Historical license verification remains unresolved.",
                "historical_license_verified": False,
                "robots_verified": False,
                "pre_event_brief_verified": False,
                "protocol_sha256": "a" * 64,
            }
        )


def test_repairs_are_counted_and_cannot_invent_a_missing_idea() -> None:
    attempt = attempts(config())[0]
    assert assemble(attempt, valid()).status == "valid"
    malformed = ProviderResult(
        text='{"idea":"An app helps teachers organize their class materials.", invalid}'
    )
    repaired = assemble(attempt, malformed, valid())
    assert repaired.status == "repaired"
    assert repaired.initial == malformed and repaired.repair is not None
    invented = assemble(attempt, ProviderResult(text="I cannot provide an idea."), valid())
    assert invented.status == "invalid"
    assert invented.parsed is None
    assert "preserve" in (invented.parse_error or "")
    limited = ProviderResult(text=valid().text, done_reason="length")
    assert assemble(attempt, limited).status == "invalid"
    failed = assemble(attempt, ProviderResult(text="", error="model unavailable"))
    assert failed.status == "provider_error"


def test_cache_key_covers_runtime_weights_prompt_and_options() -> None:
    attempt = attempts(config())[0]
    payload = request_payload(attempt)
    key = CompletionCache.key(payload, attempt.model.digest, "0.40.11")
    assert key == CompletionCache.key(payload, attempt.model.digest, "0.40.11")
    assert key != CompletionCache.key(payload, attempt.model.digest, "other-runtime")
    assert key != CompletionCache.key(payload, "other-weights", "0.40.11")
    assert key != CompletionCache.key(
        {**payload, "prompt": "changed"}, attempt.model.digest, "0.40.11"
    )
    assert key != CompletionCache.key(
        {**payload, "options": {"seed": 999}}, attempt.model.digest, "0.40.11"
    )


def test_cached_pipeline_is_byte_identical_and_makes_zero_new_calls(tmp_path: Path) -> None:
    current = config()
    cache = CompletionCache(tmp_path / "cache.sqlite")
    calls = 0

    def provider(payload: dict[str, object]) -> ProviderResult:
        nonlocal calls
        calls += 1
        return valid()

    try:
        first, first_calls = sample_run(current, cache, "fake-test-runtime", provider)
        second, second_calls = sample_run(current, cache, "fake-test-runtime", provider)
        assert len(first) == 384
        assert first_calls == 384 and second_calls == 0 and calls == 384
        assert digest(canonical([value.model_dump(mode="json") for value in first])) == digest(
            canonical([value.model_dump(mode="json") for value in second])
        )
        assert len({value.parsed.idea for value in first if value.parsed is not None}) == 1
        assert len(first) == 384  # Duplicate draws retain their multiplicity.
        key = cache.key({"test": True}, "test", "test")
        cache.put(key, valid())
        with pytest.raises(ValueError, match="overwrite"):
            cache.put(key, valid("A different sentence changes the immutable completion."))
    finally:
        cache.close()


def test_provider_failures_are_cached_and_counted_without_silent_replacement(
    tmp_path: Path,
) -> None:
    cache = CompletionCache(tmp_path / "cache.sqlite")
    try:
        samples, calls = sample_run(
            config(),
            cache,
            "fake-runtime",
            lambda _: ProviderResult(text="", error="model unavailable"),
        )
        assert calls == 384
        assert len(samples) == 384 and all(value.status == "provider_error" for value in samples)
        repeated, calls = sample_run(
            config(), cache, "fake-runtime", lambda _: pytest.fail("cache miss")
        )
        assert calls == 0 and repeated == samples
    finally:
        cache.close()


def test_frozen_protocol_refuses_changes_before_any_model_call(tmp_path: Path) -> None:
    (tmp_path / "brief.txt").write_text("The original brief.")
    lock = freeze(tmp_path, ("brief.txt",))
    assert verify(tmp_path, lock) == lock.sha256
    (tmp_path / "brief.txt").write_text("A changed brief.")
    with pytest.raises(ValueError, match="inputs changed"):
        verify(tmp_path, lock)
