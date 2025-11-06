# ADR-002: Telemetry Sync to Cortex

## Status
Accepted – 2025-11-04

## Context

- Training and simulation runs emit evaluation metrics that must inform workspace governance.
- Cortex exposes docs manifests and catalogs; n00t/n00-school should publish telemetry there automatically.
- Manual copy/paste of evaluation results leads to drift.

## Decision

1. Every training run writes `runs/<pipeline>/<timestamp>/telemetry.json` following a shared schema (TBD).
2. n00t publishes telemetry summaries back into Cortex by invoking a future `cortex.update-telemetry` capability.
3. Workspace release flow (`.dev/automation/scripts/workspace-release.sh`) verifies the most recent telemetry entry is not older than the release date.

## Consequences

- Positive: Cortex stays aligned with the latest evaluation evidence.
- Positive: Generators and downstream agents can query telemetry via Cortex MCP server.
- Negative: Additional automation is required to merge telemetry into catalogs safely.

## Follow-up

- Define the telemetry JSON schema and add validation to `.dev/automation/scripts/check-cross-repo-consistency.py`.
- Implement the `cortex.update-telemetry` capability once schemas land.
