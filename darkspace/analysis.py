# /// script
# requires-python = "==3.12.*"
# dependencies = ["numpy==2.5.4", "pydantic==2.14.1", "scikit-learn==1.9.1", "umap-learn==0.5.12"]
# ///
"""Public clustering stage; its isolated lock preserves the frozen sampling environment."""

import argparse
import hashlib
import json
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from typing import Literal, cast

import numpy as np
import umap  # type: ignore[import-untyped]
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sklearn.cluster import HDBSCAN  # type: ignore[import-untyped]

from darkspace.defaults import Codebook, assign


class PublicPoint(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    idea: str
    audience: str
    problem: str
    mechanism: str
    model: str
    vector: tuple[float, ...]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    digest: str
    dimensions: int = Field(gt=0)


class PublicInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_run_id: str
    sample_sha256: str
    event: str
    contract: Contract
    attempted: int
    failures: int
    points: tuple[PublicPoint, ...]

    @model_validator(mode="after")
    def validate_points(self) -> "PublicInput":
        if len(self.points) < 11 or len({point.id for point in self.points}) != len(self.points):
            raise ValueError("At least 11 uniquely identified real model samples are required.")
        for point in self.points:
            if len(point.vector) != self.contract.dimensions:
                raise ValueError("A public vector has the wrong dimensions.")
            values = np.asarray(point.vector)
            if not np.isfinite(values).all() or abs(float(np.linalg.norm(values)) - 1) > 0.001:
                raise ValueError("A public vector is not finite and normalized.")
        if self.attempted != len(self.points) + self.failures:
            raise ValueError("Successful and failed sample counts do not match attempts.")
        return self


class Default(BaseModel):
    id: str
    label: str
    count: int
    denominator: int
    unknown: int
    question: str


class Cluster(BaseModel):
    id: str
    name: str
    memberIds: tuple[str, ...]
    assignmentRadius: float
    defaults: tuple[Default, ...]
    defaultsStatus: Literal["complete"] = "complete"


class MapPoint(BaseModel):
    id: str
    idea: str
    model: str
    vector: tuple[float, ...]
    clusterId: str | None
    x: float
    y: float


class PublicForecast(BaseModel):
    runId: str
    event: str
    evidenceKind: Literal["model-forecast"] = "model-forecast"
    contract: Contract
    points: tuple[MapPoint, ...]
    clusters: tuple[Cluster, ...]
    provenance: dict[str, object]


class AnalysisEnvironment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    versions: dict[str, str]
    source_sha256: str
    codebook_sha256: str
    normalization_source_sha256: str


def analyze(
    data: PublicInput, environment: AnalysisEnvironment, codebook: Codebook
) -> PublicForecast:
    assignments = {
        point.id: assign(point.idea + "\n" + point.mechanism, codebook) for point in data.points
    }
    vectors = np.asarray([point.vector for point in data.points], dtype=np.float32)
    labels = cast(
        NDArray[np.int64],
        HDBSCAN(
            min_cluster_size=12,
            min_samples=5,
            metric="euclidean",
            n_jobs=1,
            allow_single_cluster=False,
            copy=True,
        ).fit_predict(vectors),
    )
    layout = cast(
        NDArray[np.float32],
        umap.UMAP(
            n_components=2,
            n_neighbors=min(15, len(vectors) - 1),
            min_dist=0.15,
            metric="cosine",
            random_state=42,
            n_jobs=1,
        ).fit_transform(vectors),
    )
    clusters = []
    for label in sorted({int(value) for value in labels} - {-1}):
        indices = [index for index, value in enumerate(labels) if int(value) == label]
        members = tuple(data.points[index] for index in indices)
        subset = vectors[indices].astype(np.float64)
        distances = np.clip(1 - subset @ subset.T, 0, 2)
        np.fill_diagonal(distances, np.inf)
        nearest_distances = np.min(distances, axis=1)
        radius = float(np.quantile(nearest_distances, 0.95, method="linear"))
        counts = Counter(rule_id for point in members for rule_id in assignments[point.id])
        defaults = tuple(
            sorted(
                (
                    Default(
                        id=rule.id,
                        label=rule.label,
                        count=counts[rule.id],
                        denominator=len(members),
                        unknown=0,
                        question=rule.question,
                    )
                    for rule in codebook.rules
                    if counts[rule.id]
                ),
                key=lambda value: (-value.count, value.id),
            )
        )
        topics = sorted(
            (rule for rule in codebook.rules if rule.topic and counts[rule.id]),
            key=lambda rule: (-counts[rule.id], rule.id),
        )
        name = topics[0].topic if topics else f"Constellation {label + 1}"
        clusters.append(
            Cluster(
                id=f"cluster-{label:02d}",
                name=name or f"Constellation {label + 1}",
                memberIds=tuple(point.id for point in members),
                assignmentRadius=radius,
                defaults=defaults,
            )
        )
    points = tuple(
        MapPoint(
            id=point.id,
            idea=point.idea,
            model=point.model,
            vector=point.vector,
            clusterId=None if int(labels[index]) == -1 else f"cluster-{int(labels[index]):02d}",
            x=float(layout[index, 0]),
            y=float(layout[index, 1]),
        )
        for index, point in enumerate(data.points)
    )
    provenance: dict[str, object] = {
        "source_run_id": data.source_run_id,
        "sample_sha256": data.sample_sha256,
        "attempted": data.attempted,
        "valid": len(points),
        "failures": data.failures,
        "noise_points": sum(point.clusterId is None for point in points),
        "codebook": codebook.model_dump(mode="json"),
        "codebook_sha256": environment.codebook_sha256,
        "normalization_source_sha256": environment.normalization_source_sha256,
        "default_assignments": assignments,
        "default_validation": "Literal wording only; no human semantic validation. Revised after exact-text counts yielded no majority defaults; current forecast is exploratory, not a held-out evaluation.",
        "clustering": {
            "algorithm": "sklearn.HDBSCAN",
            "min_cluster_size": 12,
            "min_samples": 5,
            "metric": "euclidean",
            "n_jobs": 1,
        },
        "layout": {
            "algorithm": "UMAP",
            "seed": 42,
            "n_neighbors": min(15, len(vectors) - 1),
            "min_dist": 0.15,
            "metric": "cosine",
            "n_jobs": 1,
        },
        "versions": environment.versions,
        "analysis_source_sha256": environment.source_sha256,
        "backtest_status": "not validated; no historical coverage or control result",
    }
    identity = json.dumps(
        {"input": data.model_dump(mode="json"), "analysis": provenance},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return PublicForecast(
        runId=hashlib.sha256(identity).hexdigest(),
        event=data.event,
        contract=data.contract,
        points=points,
        clusters=tuple(clusters),
        provenance=provenance,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze actual public forecast vectors; never private answers."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, default=Path("configs/default-codebook-v1.json"))
    args = parser.parse_args()
    data = PublicInput.model_validate_json(args.input.read_bytes())
    codebook_raw = args.codebook.read_bytes()
    codebook = Codebook.model_validate_json(codebook_raw)
    environment = AnalysisEnvironment(
        versions={
            name: version(name) for name in ("numpy", "scikit-learn", "umap-learn", "pydantic")
        },
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        codebook_sha256=hashlib.sha256(codebook_raw).hexdigest(),
        normalization_source_sha256=hashlib.sha256(
            Path(__file__).with_name("defaults.py").read_bytes()
        ).hexdigest(),
    )
    result = analyze(data, environment, codebook)
    payload = result.model_dump_json(indent=2).encode()
    if args.output.exists() and args.output.read_bytes() != payload:
        raise SystemExit("Refusing to overwrite a different completed public analysis.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        f"Public forecast: {len(result.points)} valid samples; {len(result.clusters)} clusters; {result.provenance['noise_points']} noise points. Backtest remains unvalidated."
    )


if __name__ == "__main__":
    main()
