# ADR-001: Model Training Pipeline

## Status
Accepted – 2025-11-04

## Context
- We need a reproducible process for fine-tuning internal models using artefacts sourced from the federated workspace.
- Training must produce metadata that Cortex can index and generators can consume.
- Existing experimentation was ad-hoc notebooks without governance.

## Decision
1. Describe training workflows as declarative YAML files under `n00-school/pipelines/`.
2. Trigger runs through `n00-school/scripts/run-training.sh`, orchestrated by n00t capability `school.trainingRun`.
3. Persist run metadata in `n00-school/runs/<pipeline>/<timestamp>/metadata.json` so downstream systems can harvest provenance.
4. Require every pipeline to define ingest, fine-tune, and evaluate stages plus produced artefacts.

## Consequences
- Positive: Pipelines are versioned, reviewable, and invokable by agents.
- Positive: Run outputs are machine-readable and can sync to Cortex catalogs.
- Negative: Additional tooling is required to promote artefacts from `runs/` to long-term storage.
- Negative: Engineers must keep pipeline specs updated as datasets evolve.

## Follow-up
- Integrate evaluation telemetry with Cortex docs manifests.
- Hook artefact uploads into CI/CD once storage location is decided.
