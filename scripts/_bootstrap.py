"""Shared bootstrap helpers for scripts entrypoints."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_syspath() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    return repo_root
