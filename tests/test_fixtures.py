import hashlib
import json
import subprocess
from pathlib import Path

from darkspace.fixtures import FixtureConfig, FixtureSource, Vectors, build_fixture, canonical


def fixture_bundle() -> dict[str, object]:
    config = FixtureConfig.model_validate_json(Path("configs/fixture.yaml").read_bytes())
    source = FixtureSource.model_validate_json(Path(config.source).read_bytes())
    vectors = Vectors.model_validate_json(Path(config.vectors).read_bytes())
    return build_fixture(source, vectors, config)


def test_fixture_pipeline_is_repeatable_and_keeps_the_zero_gap() -> None:
    first = fixture_bundle()
    second = fixture_bundle()
    assert canonical(first) == canonical(second)
    report = first["backtest"]
    assert isinstance(report, dict)
    assert report["coverage"]["matched"] == 6
    assert report["control"]["matched"] == 6
    assert report["lift_pp"] == 0
    assert report["ci_pp"] == [-50.0, 50.0]
    assert first["dataLabel"] == "sample data"
    gallery = first["gallery"]
    points = first["points"]
    assert isinstance(gallery, list) and isinstance(points, list)
    assert all(row["dataLabel"] == "sample data" for row in gallery)
    assert all(row["dataLabel"] == "sample data" for row in points)


def test_fixture_and_local_exports_cannot_be_silently_interchanged() -> None:
    bundle = fixture_bundle()
    path = Path("data/runs") / str(bundle["runId"]) / "bundle.json"
    result = subprocess.run(
        ["node", "scripts/export-bundle.mjs", "local", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "refuses fixture data" in result.stderr
    public = Path("web/static/data/current.json")
    original = hashlib.sha256(public.read_bytes()).hexdigest()
    result = subprocess.run(
        ["node", "scripts/export-bundle.mjs", "fixture", "data/backtest-summary.json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert hashlib.sha256(public.read_bytes()).hexdigest() == original
    summary = json.loads(Path("data/backtest-summary.json").read_text())
    assert summary["status"] == "not_run" and summary["coverage"] is None
