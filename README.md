# n00-school

Future home for n00tropic's model curriculum and simulation lab. This space will:

- Curate datasets and prompts used to train and fine-tune internal assistants.
- Capture safety, evaluation, and red-teaming playbooks for agent rollouts.
- Provide reproducible training pipelines that can be invoked by `n00t`.
- Surface experiment logs back into `n00-cortex` so downstream consumers can reason about model provenance.

## Quick start

```bash
cd n00-school
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
scripts/run-training.sh default --dataset horizons-sample
```

This will:

1. Load `pipelines/default.yml`.
2. Prepare a stub dataset under `datasets/horizons-sample/`.
3. Produce a mock checkpoint + metrics in `runs/default/<timestamp>/artifacts/`.

`scripts/run-training.sh --check` validates pipeline definitions without executing handlers. The wrapper mirrors the `school.trainingRun` capability consumed by `n00t`.

## Repository layout

| Path                      | Purpose                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| `pipelines/`              | Declarative specs with handler references (`handler: school_lab.handlers.prepare_dataset`). |
| `scripts/run-training.py` | Python orchestrator that parses YAML, resolves handlers, and persists metadata.             |
| `scripts/run-training.sh` | CLI wrapper invoked by n00t / humans; forwards arguments and CAPABILITY payload.            |
| `school_lab/handlers.py`  | Built-in handler library (dataset prep, fine-tuning stub, evaluation).                      |
| `runs/`                   | Materialised outputs for each pipeline execution (`metadata.json`, artefacts, metrics).     |
| `requirements.txt`        | Runtime dependencies (`pyyaml`).                                                            |
| `tests/`                  | Unit tests executed via `pytest` to guarantee pipeline orchestration stays healthy.         |

## Pipeline anatomy

```yaml
version: 1
name: default
stages:
  - name: prepare-dataset
    handler: school_lab.handlers.prepare_dataset
    params:
      splits:
        train: 0.9
        eval: 0.1
  - name: fine-tune-model
    handler: school_lab.handlers.fine_tune_model
  - name: evaluate-model
    handler: school_lab.handlers.evaluate_model
```

- `handler` is an importable dotted path. Implement new handlers in `school_lab/handlers.py` (or any importable module) and return a dictionary containing `artifacts`, `metrics`, and `logs`.
- `params` are forwarded to the handler via `context.stage["params"]`.
- Any error raised by a handler fails the pipeline, writes metadata with the offending stage, and exits non-zero.

## Integrating with n00t

The `school.trainingRun` capability ships with the following payload contract:

```json
{
  "pipeline": "default",
  "dataset": "horizons-sample",
  "check": false,
  "output": ".dev/automation/artifacts/training/latest.json"
}
```

- `pipeline` and `dataset` are optional; the shell wrapper falls back to CLI arguments or defaults.
- When `check: true`, only validation runs ensuring handlers import correctly and pipeline schemas parse.
- `output` writes the orchestrator response (status, run directory, timestamp) for downstream ingestion (e.g. n00-cortex telemetry sync).

Update `n00t/capabilities/manifest.json` when adding new pipelines so the control centre exposes them automatically.

## Extending the lab

1. **Add a pipeline** — Create `pipelines/<name>.yml`, reference handlers, and document parameters.
2. **Implement handlers** — Add functions that accept a `StageContext` and return artefacts/metrics.
3. **Capture telemetry** — Ensure handlers write results to `runs/<pipeline>/<timestamp>/artifacts/` so `agent-runs.json` consumers can ingest.
4. **Document** — Draft an ADR per major change (see `ADR/`) and cross-link from `n00-frontiers`.

## Testing

Tests live alongside the orchestrator (`tests/test_pipeline.py`). They are executed via:

```bash
pytest
```

Meta-check pipelines (invoked by `n00t workspace.metaCheck`) run `scripts/run-training.sh default --check` to guarantee manifests stay valid.
