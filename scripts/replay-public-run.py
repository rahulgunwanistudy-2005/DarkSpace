"""Rebuild the public completion cache from preserved raw outputs and replay with no provider."""

import argparse
import hashlib
import json
from pathlib import Path

from darkspace.cache import CompletionCache
from darkspace.cli import sample_run
from darkspace.freeze import ProtocolLock, verify
from darkspace.models import ProviderResult, Sample, SamplingConfig
from darkspace.sample import canonical, request_payload


def forbidden_provider(payload: dict[str, object]) -> ProviderResult:
    raise RuntimeError("Offline replay attempted a new model call.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    report = json.loads(raw)
    config = SamplingConfig.model_validate(report["config"])
    protocol_root = Path(".darkspace-local/protocols") / report["protocol_sha256"]
    protocol = verify(
        protocol_root if protocol_root.exists() else Path.cwd(),
        ProtocolLock.model_validate_json(Path("configs/freeze-current.json").read_bytes()),
    )
    if report["protocol_sha256"] != protocol:
        raise ValueError("The raw run belongs to a different frozen protocol.")
    originals = tuple(Sample.model_validate(row) for row in report["samples"])
    cache = CompletionCache(Path(".cache/reconstructed-public-completions.sqlite"))
    try:
        for row in originals:
            cache.put(
                cache.key(
                    request_payload(row.attempt), row.attempt.model.digest, report["runtime"]
                ),
                row.initial,
            )
            if row.repair is not None:
                cache.put(
                    cache.key(
                        request_payload(row.attempt, row.initial.text),
                        row.attempt.model.digest,
                        report["runtime"],
                    ),
                    row.repair,
                )
        samples, calls = sample_run(config, cache, report["runtime"], forbidden_provider)
    finally:
        cache.close()
    if calls != 0 or canonical([row.model_dump(mode="json") for row in samples]) != canonical(
        report["samples"]
    ):
        raise ValueError("Offline replay changed the counted public samples.")
    replayed = {**report, "samples": [row.model_dump(mode="json") for row in samples]}
    if canonical(replayed) != raw:
        raise ValueError("Offline replay was not byte-identical.")
    receipt = {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "protocol_sha256": protocol,
        "attempts": len(samples),
        "new_model_calls": calls,
        "byte_identical": True,
        "cache_origin": "Reconstructed from the preserved raw public completions; original cloud SQLite file was not imported.",
    }
    (args.source.parent / "offline-replay.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
