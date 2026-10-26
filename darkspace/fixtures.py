"""Deterministic made-up data pipeline. Its authored-tag matcher is never used for real data."""

import argparse
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Tags(Strict):
    id: str
    audience: str
    problem: str
    mechanism: str


class Gallery(Tags):
    title: str
    tagline: str


class Forecast(Tags):
    idea: str
    cluster: str
    defaults: tuple[str, ...]


class Topic(Strict):
    id: str
    name: str
    question: str


class FixtureSource(Strict):
    dataLabel: Literal["sample data"]
    authorship: str
    topics: tuple[Topic, ...]
    gallery: tuple[Gallery, ...]
    forecast: tuple[Forecast, ...]
    control: tuple[Forecast, ...]


class FixtureConfig(Strict):
    protocol: Literal["darkspace-fixture-v1"]
    evidence: Literal["sample data"]
    source: str
    vectors: str
    matching: Literal["fixture-authored-tags-v1"]
    bootstrap_seed: Literal[42]
    bootstrap_resamples: Literal[10000]
    curve_budgets: tuple[int, ...]


class Contract(Strict):
    id: str
    digest: str
    dimensions: int


class Vectors(Strict):
    sourceSha256: str
    contract: Contract
    vectors: dict[str, tuple[float, ...]]


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def tags(row: Tags) -> tuple[str, str, str]:
    return row.audience, row.problem, row.mechanism


def hits(gallery: tuple[Gallery, ...], ideas: tuple[Forecast, ...]) -> tuple[str, ...]:
    available = {tags(row) for row in ideas}
    return tuple(row.id for row in gallery if tags(row) in available)


def quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def build_fixture(
    source: FixtureSource, vectors: Vectors, config: FixtureConfig
) -> dict[str, object]:
    if (
        len(source.forecast) != len(source.control)
        or len(source.forecast) < 11
        or not source.gallery
    ):
        raise ValueError(
            "Fixture arms must have equal budgets, at least 11 forecasts, and a nonempty gallery."
        )
    if len({row.id for row in (*source.gallery, *source.forecast, *source.control)}) != len(
        source.gallery
    ) + len(source.forecast) + len(source.control):
        raise ValueError("Fixture IDs must be unique.")
    for row in source.forecast:
        vector = vectors.vectors[row.id]
        if (
            len(vector) != vectors.contract.dimensions
            or not all(math.isfinite(value) for value in vector)
            or abs(sum(value * value for value in vector) - 1) > 0.001
        ):
            raise ValueError("Fixture vector contract failed.")
    event_hits = hits(source.gallery, source.forecast)
    control_hits = hits(source.gallery, source.control)
    denominator = len(source.gallery)
    delta = [float(row.id in event_hits) - float(row.id in control_hits) for row in source.gallery]
    generator = random.Random(config.bootstrap_seed)
    boot = [
        sum(generator.choices(delta, k=denominator)) / denominator * 100
        for _ in range(config.bootstrap_resamples)
    ]
    identity = {
        "config": config.model_dump(mode="json"),
        "source": source.model_dump(mode="json"),
        "vectors": vectors.model_dump(mode="json"),
        "pipeline": "authored-fixture-v1",
    }
    run_id = "fixture-" + hashlib.sha256(canonical(identity)).hexdigest()
    clusters = []
    points = []
    for group, topic in enumerate(source.topics):
        members = tuple(row for row in source.forecast if row.cluster == topic.id)
        if not members:
            continue
        counts = Counter(value for row in members for value in set(row.defaults))
        defaults = [
            {
                "id": key,
                "label": "Authored sample trait: "
                + ("shared record" if key == "shared-log" else "reminder"),
                "count": count,
                "denominator": len(members),
                "unknown": 0,
                "question": topic.question
                if key == "shared-log"
                else "What do you know about when a reminder helps, or gets ignored, in your own situation?",
            }
            for key, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
        ]
        nearest = []
        for row in members:
            nearest.append(
                min(
                    max(
                        0.0,
                        min(
                            2.0,
                            1
                            - sum(
                                a * b
                                for a, b in zip(
                                    vectors.vectors[row.id], vectors.vectors[other.id], strict=True
                                )
                            ),
                        ),
                    )
                    for other in members
                    if other.id != row.id
                )
            )
        clusters.append(
            {
                "id": topic.id,
                "name": topic.name,
                "memberIds": [row.id for row in members],
                "assignmentRadius": quantile(nearest, 0.95),
                "defaults": defaults,
                "defaultsStatus": "complete",
            }
        )
        for index, row in enumerate(members):
            points.append(
                {
                    "id": row.id,
                    "idea": row.idea,
                    "model": "Sample data",
                    "vector": vectors.vectors[row.id],
                    "clusterId": topic.id,
                    "x": float(group % 2 * 3) + (index % 2) * 0.3,
                    "y": float(group // 2 * 3) + (index // 2) * 0.3,
                    "dataLabel": "sample data",
                }
            )
    curve = [
        {
            "attempts": budget,
            "coverage": len(hits(source.gallery, source.forecast[:budget])) / denominator,
            "control": len(hits(source.gallery, source.control[:budget])) / denominator,
        }
        for budget in config.curve_budgets
    ]
    aggregate = {
        "runId": run_id,
        "evidence": "sample data",
        "eligible": denominator,
        "coverage": {"matched": len(event_hits), "rate": len(event_hits) / denominator},
        "control": {"matched": len(control_hits), "rate": len(control_hits) / denominator},
        "lift_pp": (len(event_hits) - len(control_hits)) / denominator * 100,
        "ci_pp": [quantile(boot, 0.025), quantile(boot, 0.975)],
        "curve": curve,
        "drop_counts": {"invalid": 0, "unknown": 0, "provider_errors": 0},
        "matching_rule": config.matching,
    }
    return {
        "runId": run_id,
        "bundleKind": "fixture",
        "dataLabel": "sample data",
        "event": "Made-up workshop event",
        "evidenceKind": "sample-data",
        "contract": vectors.contract.model_dump(),
        "points": points,
        "clusters": clusters,
        "gallery": [
            {
                **row.model_dump(),
                "dataLabel": "sample data",
                "forecastMatched": row.id in event_hits,
                "controlMatched": row.id in control_hits,
            }
            for row in source.gallery
        ],
        "backtest": aggregate,
        "provenance": {
            "attempted": len(source.forecast),
            "valid": len(points),
            "failures": 0,
            "noise_points": 0,
            "dataLabel": "sample data",
            "matching": "Authored fixture tags only. Not an LLM judge or evidence of real-world forecasting accuracy.",
            "layout": "Authored sample layout; density uses actual shared-WASM vectors.",
            "source_sha256": vectors.sourceSha256,
            "bootstrap_seed": 42,
            "bootstrap_resamples": 10000,
        },
    }


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run only the made-up public fixture pipeline.")
    parser.add_argument("--config", type=Path, default=Path("configs/fixture.yaml"))
    args = parser.parse_args(arguments)
    config = FixtureConfig.model_validate_json(args.config.read_bytes())
    for name in (config.source, config.vectors):
        if not Path(name).resolve().is_relative_to(Path("data/fixtures").resolve()):
            raise SystemExit("Fixture inputs must be inside data/fixtures.")
    raw = Path(config.source).read_bytes()
    source = FixtureSource.model_validate_json(raw)
    vectors = Vectors.model_validate_json(Path(config.vectors).read_bytes())
    if hashlib.sha256(raw).hexdigest() != vectors.sourceSha256:
        raise SystemExit("Fixture text changed; regenerate its shared-WASM vectors first.")
    bundle = build_fixture(source, vectors, config)
    directory = Path("data/runs") / str(bundle["runId"])
    directory.mkdir(parents=True, exist_ok=True)
    payload = canonical(bundle)
    target = directory / "bundle.json"
    if target.exists() and target.read_bytes() != payload:
        raise SystemExit("Refusing to overwrite a different completed fixture run.")
    target.write_bytes(payload)
    (directory / "aggregate.json").write_bytes(canonical(bundle["backtest"]))
    (directory / "manifest.json").write_bytes(
        canonical(
            {
                "runId": bundle["runId"],
                "files": {"bundle.json": hashlib.sha256(payload).hexdigest()},
                "dataLabel": "sample data",
            }
        )
    )
    print(
        json.dumps(
            {
                "fixture_run": bundle["runId"],
                "gallery": len(source.gallery),
                "forecast": len(source.forecast),
                "control": len(source.control),
                "dataLabel": "sample data",
                "aggregate": bundle["backtest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
