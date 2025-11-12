# Start Here: n00-school

n00-school houses training pipelines, evaluation harnesses, and datasets for n00tropic’s in-house assistants.

## If you only have 5 minutes

- Read the root [`README.md`](../README.md) for the pipeline overview.
- Inspect `pipelines/default.yml` to understand the declarative pipeline schema.
- Familiarise yourself with `scripts/run-training.sh`; it is the interface exposed via `n00t`’s `school.trainingRun` capability.

## Quick start (humans)

```bash
cd n00-school
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Dry-run validation
scripts/run-training.sh default --check

# Execute sample pipeline
scripts/run-training.sh default --dataset horizons-sample
```

Outputs land under `runs/default/<timestamp>/` with `metadata.json`, metrics, and artefacts.

## Agent hooks

- `scripts/run-training.sh` is invoked by `n00t`’s `school.trainingRun` capability; ensure new pipelines are registered in `capabilities/manifest.json`.
- Metrics generated under `runs/` should include human-readable summaries and structured JSON for ingestion by `n00-cortex`.
- Use `.dev/automation/artifacts/training/` for telemetry destined for cross-repo dashboards (gitignored by default).

## Key directories

| Path          | Purpose                                                                            |
| ------------- | ---------------------------------------------------------------------------------- |
| `pipelines/`  | YAML pipeline definitions referenced by the shell + Python orchestrators.          |
| `scripts/`    | Entry points (`run-training.sh`, `run-training.py`) used by humans and automation. |
| `school_lab/` | Implementation of training/evaluation handlers.                                    |
| `datasets/`   | Source datasets (anon/anonymised) used by pipelines.                               |
| `runs/`       | Outputs (artefacts, metrics, metadata) produced by pipeline executions.            |

## Contribution guardrails

- Keep sensitive training data out of the repo; use `99-Clients/` or encrypted storage for real datasets.
- Update tests under `tests/` and run `pytest` when adding pipelines or handlers.
- Document major additions with ADRs and cross-link into `n00-cortex data/catalog`.
