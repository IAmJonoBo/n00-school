#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from school_lab import ROOT
from school_lab.pipeline import PipelineRunner


def load_payload() -> Dict[str, Any]:
    payload = os.environ.get("CAPABILITY_PAYLOAD") or os.environ.get("CAPABILITY_INPUT")
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[run-training] Invalid CAPABILITY payload: {exc}") from exc


def resolve_pipeline_path(pipeline: str) -> Path:
    candidate = Path(pipeline)
    if candidate.is_file():
        return candidate.resolve()
    if candidate.suffix in {".yml", ".yaml"}:
        candidate = Path("pipelines") / candidate
    else:
        candidate = Path("pipelines") / f"{pipeline}.yml"
    return (ROOT / candidate).resolve()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run n00-school training pipeline.")
    parser.add_argument(
        "pipeline", nargs="?", default=None, help="Pipeline name or path (YAML)."
    )
    parser.add_argument(
        "--dataset", default=None, help="Dataset slug (defaults to pipeline parameter)."
    )
    parser.add_argument(
        "--check", action="store_true", help="Validation mode; do not execute stages."
    )
    parser.add_argument(
        "--output", default=None, help="Optional path to write JSON metadata."
    )
    args = parser.parse_args(argv)

    payload = load_payload()
    dataset = args.dataset or payload.get("dataset") or "default"
    pipeline_name = args.pipeline or payload.get("pipeline")
    if not pipeline_name:
        parser.error("Pipeline name is required (argument or CAPABILITY payload).")

    pipeline_path = resolve_pipeline_path(pipeline_name)

    runner = PipelineRunner(pipeline_path, dataset)
    if args.check or payload.get("check"):
        runner.run(dry_run=True)
        print(
            f"[run-training] Validation succeeded for pipeline={pipeline_path.name} dataset={dataset}"
        )
        return 0

    result = runner.run()
    run_dir = result.get("run_dir")
    print(
        f"[run-training] Pipeline completed. Status={result['status']} run_dir={run_dir}"
    )

    if args.output or payload.get("output"):
        output_path = Path(args.output or payload["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"[run-training] Metadata written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
