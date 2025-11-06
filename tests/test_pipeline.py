import json
from pathlib import Path

from school_lab import ROOT
from school_lab.pipeline import PipelineRunner


def test_pipeline_dry_run() -> None:
    pipeline = ROOT / "pipelines/default.yml"
    runner = PipelineRunner(pipeline, dataset="dry-run-dataset")
    result = runner.run(dry_run=True)
    assert result["status"] == "validated"


def test_pipeline_execution(tmp_path: Path) -> None:
    pipeline = ROOT / "pipelines/default.yml"
    run_dir = tmp_path / "runs/default"
    run_dir.mkdir(parents=True)

    runner = PipelineRunner(pipeline, dataset="exec-dataset")
    result = runner.run(run_dir=run_dir)

    assert result["status"] == "succeeded"

    metadata_file = run_dir / "metadata.json"
    assert metadata_file.exists()

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert metadata["dataset"] == "exec-dataset"
    assert metadata["status"] == "succeeded"
    assert len(metadata["stages"]) == 3

    artifacts_dir = run_dir / "artifacts"
    assert artifacts_dir.exists()
    assert (artifacts_dir / "model.safetensors").exists()
    assert (artifacts_dir / "metrics.json").exists()
