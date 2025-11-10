#!/usr/bin/env python3
"""Repo-local helper for n00-school."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def list_curricula() -> None:
    curricula_dir = REPO_ROOT / "curricula"
    if not curricula_dir.exists():
        print("No curricula directory found.")
        return
    for path in sorted(curricula_dir.iterdir()):
        if path.is_dir():
            print(f"- {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="n00-school helper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("curricula", help="List available curricula.")
    subparsers.add_parser("status", help="Show git status for n00-school.")

    args = parser.parse_args()
    if args.command == "curricula":
        list_curricula()
    elif args.command == "status":
        import subprocess

        subprocess.run(["git", "status", "-sb"], check=True, cwd=REPO_ROOT)
    else:  # pragma: no cover
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
