from __future__ import annotations

import importlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from . import ROOT


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_handler(handler_path: str) -> Callable[..., Any]:
    module_name, _, attr = handler_path.rpartition(".")
    if not module_name or not attr:
        raise ValueError(
            f"Invalid handler path '{handler_path}'. Expected 'module.attr'."
        )
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise ValueError(f"Handler '{handler_path}' not found") from exc


@dataclass
class StageContext:
    pipeline: Dict[str, Any]
    stage: Dict[str, Any]
    dataset: str
    workspace: Path
    run_dir: Optional[Path]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def expand(self, value: str) -> str:
        return value.format(
            dataset=self.dataset,
            workspace=str(self.workspace),
            run_dir=str(self.run_dir) if self.run_dir else "",
            timestamp=self.timestamp,
        )


@dataclass
class StageResult:
    name: str
    status: str
    started_at: str
    completed_at: str
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


class PipelineRunner:
    """
    Execute a training pipeline defined in YAML.
    """

    def __init__(self, pipeline_path: Path, dataset: str):
        self.pipeline_path = pipeline_path
        self.dataset = dataset
        self.workspace = ROOT
        self.pipeline = self._load_pipeline()

    def _load_pipeline(self) -> Dict[str, Any]:
        if not self.pipeline_path.exists():
            raise FileNotFoundError(
                f"Pipeline definition not found: {self.pipeline_path}"
            )
        with self.pipeline_path.open("r", encoding="utf-8") as fh:
            pipeline = yaml.safe_load(fh) or {}
        if "stages" not in pipeline or not isinstance(pipeline["stages"], list):
            raise ValueError(
                f"Pipeline {self.pipeline_path} missing 'stages' definition"
            )
        return pipeline

    def run(
        self, *, dry_run: bool = False, run_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        timestamp = utc_now()
        stages_result: List[StageResult] = []

        if dry_run:
            context = StageContext(
                pipeline=self.pipeline,
                stage={},
                dataset=self.dataset,
                workspace=self.workspace,
                run_dir=None,
                timestamp=timestamp,
            )
            self._validate_pipeline(context)
            return {"status": "validated", "timestamp": timestamp}

        run_dir = run_dir or self._create_run_dir(timestamp)
        context_base = StageContext(
            pipeline=self.pipeline,
            stage={},
            dataset=self.dataset,
            workspace=self.workspace,
            run_dir=run_dir,
            timestamp=timestamp,
        )

        status = "succeeded"
        for stage in self.pipeline["stages"]:
            stage_name = stage.get("name", "unnamed-stage")
            handler_path = stage.get("handler")
            if not handler_path:
                raise ValueError(
                    f"Stage '{stage_name}' missing handler in pipeline {self.pipeline_path}"
                )
            handler = resolve_handler(handler_path)

            started = utc_now()
            stage_context = StageContext(
                pipeline=self.pipeline,
                stage=stage,
                dataset=self.dataset,
                workspace=self.workspace,
                run_dir=run_dir,
                timestamp=timestamp,
                metadata={},
            )
            result = StageResult(
                name=stage_name,
                status="succeeded",
                started_at=started,
                completed_at=started,
            )

            try:
                outputs = handler(stage_context)
                completed = utc_now()
                result.completed_at = completed
                if isinstance(outputs, dict):
                    result.artifacts.extend(outputs.get("artifacts", []))
                    result.metrics.update(outputs.get("metrics", {}))
                    logs = outputs.get("logs") or outputs.get("log") or []
                    if isinstance(logs, str):
                        logs = [logs]
                    result.logs.extend(logs)
            except Exception as exc:  # pylint: disable=broad-except
                result.status = "failed"
                result.logs.append(f"{type(exc).__name__}: {exc}")
                completed = utc_now()
                result.completed_at = completed
                status = "failed"
                stages_result.append(result)
                self._write_metadata(run_dir, status, stages_result)
                raise

            stages_result.append(result)

        metadata_path = self._write_metadata(run_dir, status, stages_result)
        return {
            "status": status,
            "timestamp": timestamp,
            "run_dir": str(run_dir),
            "metadata_path": str(metadata_path),
        }

    def _create_run_dir(self, timestamp: str) -> Path:
        pipeline_name = self.pipeline.get("name") or self.pipeline_path.stem
        run_dir = self.workspace / "runs" / pipeline_name / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _write_metadata(
        self, run_dir: Path, status: str, stages: List[StageResult]
    ) -> Path:
        try:
            relative_pipeline = str(self.pipeline_path.relative_to(self.workspace))
        except ValueError:
            relative_pipeline = str(self.pipeline_path)

        data = {
            "pipeline": self.pipeline.get("name", self.pipeline_path.stem),
            "pipeline_file": relative_pipeline,
            "dataset": self.dataset,
            "status": status,
            "stages": [
                {
                    "name": stage.name,
                    "status": stage.status,
                    "started_at": stage.started_at,
                    "completed_at": stage.completed_at,
                    "artifacts": stage.artifacts,
                    "metrics": stage.metrics,
                    "logs": stage.logs,
                }
                for stage in stages
            ],
            "updated_at": utc_now(),
        }
        metadata_file = run_dir / "metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with metadata_file.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        return metadata_file

    def _validate_pipeline(self, context: StageContext) -> None:
        for stage in self.pipeline["stages"]:
            if "handler" not in stage:
                raise ValueError(f"Stage '{stage}' missing handler")
            handler_path = stage["handler"]
            handler = resolve_handler(handler_path)
            if hasattr(handler, "validate"):
                handler.validate(context)  # type: ignore[attr-defined]
