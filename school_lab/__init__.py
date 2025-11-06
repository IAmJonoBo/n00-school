"""
School lab orchestration package.

This module exposes utility helpers used by the training orchestrator.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

__all__ = ["ROOT"]
