from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List

from .pipeline import StageContext


def _ensure_run_dir(context: StageContext) -> Path:
    if context.run_dir is None:
        raise ValueError("Stage requires run_dir but pipeline running in dry-run mode.")
    return context.run_dir


def prepare_dataset(context: StageContext) -> Dict[str, Any]:
    """
    Simulate dataset preparation by materialising a manifest and sample splits.
    """
    params = context.stage.get("params", {})
    dataset_root = Path(context.workspace, "datasets", context.dataset)
    dataset_root.mkdir(parents=True, exist_ok=True)

    splits = params.get("splits", {"train": 0.9, "eval": 0.1})
    seed = int(params.get("seed", 13))
    random.seed(seed)

    manifest = {
        "dataset": context.dataset,
        "generated_at": context.timestamp,
        "splits": splits,
        "records": random.randint(1000, 2000),
    }
    with (dataset_root / "manifest.json").open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    log = f"[prepare_dataset] Generated manifest for {context.dataset} with splits {splits}"
    artifacts = [
        {
            "name": "dataset_manifest",
            "type": "dataset",
            "path": str(dataset_root / "manifest.json"),
        }
    ]
    return {"artifacts": artifacts, "logs": [log]}


def fine_tune_model(context: StageContext) -> Dict[str, Any]:
    """
    Produce a mock model checkpoint artefact representing a fine-tuned model.
    """
    run_dir = _ensure_run_dir(context)
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = artifacts_dir / "model.safetensors"
    metadata = {
        "pipeline": context.pipeline.get("name"),
        "dataset": context.dataset,
        "created_at": context.timestamp,
        "parameters": context.stage.get("params", {}),
    }
    with checkpoint_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    log = f"[fine_tune_model] Wrote model checkpoint to {checkpoint_path}"
    artifacts = [
        {
            "name": "model_checkpoint",
            "type": "model",
            "path": str(checkpoint_path),
        }
    ]
    return {"artifacts": artifacts, "logs": [log]}


def evaluate_model(context: StageContext) -> Dict[str, Any]:
    """
    Generate evaluation metrics for the run.
    """
    run_dir = _ensure_run_dir(context)
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "accuracy": round(random.uniform(0.85, 0.98), 4),
        "bleu": round(random.uniform(0.3, 0.6), 3),
        "latency_ms_p99": random.randint(120, 250),
    }
    metrics_path = artifacts_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    logs: List[str] = [f"[evaluate_model] Metrics stored at {metrics_path}"]
    return {
        "artifacts": [
            {"name": "evaluation_metrics", "type": "metrics", "path": str(metrics_path)}
        ],
        "metrics": metrics,
        "logs": logs,
    }
