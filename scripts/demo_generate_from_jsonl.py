#!/usr/bin/env python3
"""Batch demo renderer for template inputs stored as JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from templateer.env import TemplateEnv
from templateer.errors import TemplateError
from templateer.output import write_generation_artifacts
from templateer.renderer import render_template_id


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

    total = 0
    success = 0
    failure = 0

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = args.project_root / "templates" / args.template_id / "gen"

    env = TemplateEnv(args.project_root)

    try:
        with args.input_jsonl.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                total += 1
                line = raw_line.strip()
                if not line:
                    failure += 1
                    print(f"line {line_number}: empty line", file=sys.stderr)
                    if args.fail_fast:
                        break
                    continue

                try:
                    payload = json.loads(line)
                    if not isinstance(payload, dict):
                        raise ValueError("JSON value must be an object")

                    rendered = render_template_id(env, args.template_id, payload)
                    input_json = json.dumps(payload, indent=2) + "\n"
                    write_generation_artifacts(output_dir, input_json, rendered)
                    success += 1
                except json.JSONDecodeError as exc:
                    failure += 1
                    print(f"line {line_number}: invalid JSON ({exc.msg})", file=sys.stderr)
                    if args.fail_fast:
                        break
                except (TemplateError, ValueError) as exc:
                    failure += 1
                    print(f"line {line_number}: {exc}", file=sys.stderr)
                    if args.fail_fast:
                        break
    except OSError as exc:
        print(f"failed to read {args.input_jsonl}: {exc}", file=sys.stderr)
        return 1

    print(f"Processed {total} line(s): success={success}, failure={failure}")
    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(app())
