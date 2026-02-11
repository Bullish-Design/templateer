#!/usr/bin/env python3
"""Scaffold a new template folder and refresh templates/registry.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    from _bootstrap import ensure_src_on_syspath
else:  # pragma: no cover
    from ._bootstrap import ensure_src_on_syspath

ensure_src_on_syspath()

from templateer.services.runtime import resolve_project_root
from templateer.services.scaffold_service import scaffold_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new template scaffold")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root containing templates/")
    parser.add_argument("--template-id", required=True, help="Template id and folder name under templates/")
    parser.add_argument("--model-import-path", required=True, help="Pydantic model import path, e.g. pkg.module:ClassName")
    parser.add_argument("--description", default="", help="Template description for manifest.json")
    parser.add_argument("--tags", default="", help="Comma-separated tag list")
    return parser


def app(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        template_dir, registry_path = scaffold_template(
            project_root=resolve_project_root(args.project_root),
            template_id=args.template_id,
            model_import_path=args.model_import_path,
            description=args.description,
            tags=args.tags,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Created template scaffold at: {template_dir}")
    print(f"Updated registry: {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(app())
