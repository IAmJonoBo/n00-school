# Black vs isort Conflict

## Problem

- Trunk kept reporting `noxfile.py` as unformatted even after running `trunk fmt`, causing Black and isort to toggle the file back and forth.

## Cause

- `.trunk/trunk.yaml` invoked Black before isort, so Black would reflow imports after isort finished.
- `.isort.cfg` overrode the default Black-compatible settings (`line_length = 88`) with a 100-character line length, producing layouts Black immediately rewrote.

## Solution

- Reorder the Trunk linters so `isort@7.0.0` runs before `black@25.9.0`, making isort the canonical import sorter.
- Reset `.isort.cfg` to align with Black defaults (`profile = black`, `line_length = 88`) to avoid divergent wrapping rules.
- Document the formatter order in `docs/quality/formatting-style.md` so future agents know isort now owns import ordering.
