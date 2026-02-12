#!/usr/bin/env python3
"""Batch demo renderer for template inputs stored as JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    from _bootstrap import ensure_src_on_syspath
else:  # pragma: no cover
    from ._bootstrap import ensure_src_on_syspath

ensure_src_on_syspath()

from templateer.services.generation_service import process_jsonl_inputs
from templateer.services.runtime import resolve_project_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render one template for each JSON object in a JSONL file.")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root containing templates/registry.json")
    parser.add_argument("--template-id", required=True, help="Template ID from templates/registry.json")
    parser.add_argument("--input-jsonl", type=Path, required=True, help="Path to line-delimited JSON input file")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory where timestamped generation folders are written")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on the first parse/validation/render failure")
    return parser


def app(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = resolve_project_root(args.project_root)
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = project_root / "templates" / args.template_id / "gen"

    try:
        batch = process_jsonl_inputs(
            project_root,
            args.template_id,
            args.input_jsonl,
            output_dir=output_dir,
            fail_fast=args.fail_fast,
            count_empty_as_failure=True,
        )
    except OSError as exc:
        print(f"failed to read {args.input_jsonl}: {exc}", file=sys.stderr)
        return 1

    print(f"Processed {batch.total} line(s): success={batch.success}, failure={batch.failure}")
    return 1 if batch.failure else 0


if __name__ == "__main__":
    raise SystemExit(app())
