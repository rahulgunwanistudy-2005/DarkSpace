import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from darkspace.cache import CompletionCache
from darkspace.freeze import ProtocolLock, verify
from darkspace.models import ProviderResult, Sample, SamplingConfig
from darkspace.providers import generate, runtime_version, verify_model
from darkspace.sample import assemble, attempts, canonical, digest, request_payload


def sample_run(
    config: SamplingConfig,
    cache: CompletionCache,
    runtime: str,
    provider: Callable[[dict[str, object]], ProviderResult],
    progress: Callable[[int, Sample], None] | None = None,
) -> tuple[tuple[Sample, ...], int]:
    samples: list[Sample] = []
    calls = 0

    def cached(payload: dict[str, object], model_digest: str) -> ProviderResult:
        nonlocal calls
        key = cache.key(payload, model_digest, runtime)
        previous = cache.get(key)
        if previous is not None:
            return previous
        value = provider(payload)
        calls += 1
        cache.put(key, value)
        return value

    for attempt in attempts(config):
        initial = cached(request_payload(attempt), attempt.model.digest)
        sample = assemble(attempt, initial)
        if sample.status == "invalid" and initial.text:
            repair = cached(request_payload(attempt, initial.text), attempt.model.digest)
            sample = assemble(attempt, initial, repair)
        samples.append(sample)
        if progress is not None:
            progress(len(samples), sample)
    return tuple(samples), calls


def main() -> None:
    if sys.argv[1:2] == ["fixtures"]:
        from darkspace.fixtures import main as fixtures_main

        fixtures_main(sys.argv[2:])
        return
    parser = argparse.ArgumentParser(description="Public-data-only Dark Space pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    sample = commands.add_parser("sample")
    sample.add_argument("--config", type=Path, required=True)
    sample.add_argument("--cache", type=Path, default=Path(".cache/public-completions.sqlite"))
    sample.add_argument("--output", type=Path, default=Path("data/runs"))
    sample.add_argument("--lock", type=Path, default=Path("configs/freeze-current.json"))
    args = parser.parse_args()
    config = SamplingConfig.model_validate_json(args.config.read_bytes())
    lock = ProtocolLock.model_validate_json(args.lock.read_bytes())
    protocol_digest = verify(Path.cwd(), lock)
    if str(args.config) not in lock.files:
        raise SystemExit("The supplied config is not included in the frozen protocol lock.")
    runtime = runtime_version()
    for model in config.models:
        verify_model(model)
    cache = CompletionCache(args.cache)
    try:

        def progress(count: int, sample: Sample) -> None:
            if count % 12 == 0 or sample.status not in ("valid", "repaired"):
                print(
                    f"Public attempts {count}/384; model {sample.attempt.model.tag}; status {sample.status}",
                    flush=True,
                )

        samples, calls = sample_run(config, cache, runtime, generate, progress)
    finally:
        cache.close()
    identity: dict[str, object] = {
        "config": config.model_dump(mode="json"),
        "runtime": runtime,
        "protocol_sha256": protocol_digest,
    }
    run_id = digest(canonical(identity))
    directory = args.output / run_id
    directory.mkdir(parents=True, exist_ok=True)
    artifact: dict[str, object] = {
        "run_id": run_id,
        "config": config.model_dump(mode="json"),
        "runtime": runtime,
        "protocol_sha256": protocol_digest,
        "attempted": len(samples),
        "valid": sum(value.parsed is not None for value in samples),
        "repaired": sum(value.status == "repaired" for value in samples),
        "invalid": sum(value.status == "invalid" for value in samples),
        "provider_errors": sum(value.status == "provider_error" for value in samples),
        "initial_parse_failures": sum(value.status != "valid" for value in samples),
        "repair_attempts": sum(value.repair is not None for value in samples),
        "repair_failures": sum(
            value.repair is not None and value.parsed is None for value in samples
        ),
        "samples": [value.model_dump(mode="json") for value in samples],
    }
    encoded = canonical(artifact)
    target = directory / "samples.json"
    if target.exists() and target.read_bytes() != encoded:
        raise SystemExit("Refusing to overwrite a completed artifact with different bytes.")
    temporary = directory / "samples.json.tmp"
    temporary.write_bytes(encoded)
    temporary.replace(target)
    print(
        f"Public samples saved: {target}; valid {artifact['valid']}/{len(samples)}; new model calls {calls}"
    )
