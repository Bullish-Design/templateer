"""Shared runtime/bootstrap helpers for scripts and workflows."""

from __future__ import annotations

from pathlib import Path


def resolve_project_root(project_root: str | Path) -> Path:
    """Resolve a project-root argument to an absolute normalized path."""

    return Path(project_root).expanduser().resolve()


def template_dir(project_root: str | Path, template_id: str) -> Path:
    """Return templates/<template_id> under the provided project root."""

    root = resolve_project_root(project_root)
    return root / "templates" / template_id
