"""Generation workflows shared by CLI and scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from templateer.env import TemplateEnv
from templateer.errors import TemplateError
from templateer.output import write_generation_artifacts
from templateer.renderer import render_template_id
from templateer.services.input_service import parse_json_object


def generate_single(project_root: Path, template_id: str, payload: dict[str, object]) -> Path:
    """Render one payload for a template and persist generation artifacts."""

    env = TemplateEnv(project_root)
    rendered = render_template_id(env, template_id, payload)
    template_dir = project_root / "templates" / template_id
    gen_dir = template_dir / "gen"
    input_json = json.dumps(payload, indent=2) + "\n"
    return write_generation_artifacts(gen_dir, input_json, rendered)


def process_jsonl_inputs(
    project_root: Path,
    template_id: str,
    input_jsonl: Path,
    *,
    output_dir: Path,
    fail_fast: bool = False,
    count_empty_as_failure: bool = False,
    stderr: object = sys.stderr,
) -> tuple[int, int, int]:
    """Render one template for each JSON object line in a JSONL file.

    Returns a ``(total, success, failure)`` tuple.
    """

    total = 0
    success = 0
    failure = 0
    env = TemplateEnv(project_root)

    with input_jsonl.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            total += 1
            line = raw_line.strip()
            if not line:
                if count_empty_as_failure:
                    failure += 1
                    print(f"line {line_number}: empty line", file=stderr)
                    if fail_fast:
                        break
                continue

            try:
                payload = parse_json_object(line)
                rendered = render_template_id(env, template_id, payload)
                input_json = json.dumps(payload, indent=2) + "\n"
                write_generation_artifacts(output_dir, input_json, rendered)
                success += 1
            except (TemplateError, ValueError) as exc:
                failure += 1
                print(f"line {line_number}: {exc}", file=stderr)
                if fail_fast:
                    break

    return total, success, failure


def generate_examples(project_root: Path, template_id: str) -> tuple[int, int]:
    """Render built-in sample_inputs.jsonl for a template.

    Returns a ``(success, failure)`` tuple.
    """

    template_dir = project_root / "templates" / template_id
    examples_jsonl = template_dir / "examples" / "sample_inputs.jsonl"
    _total, success, failure = process_jsonl_inputs(
        project_root,
        template_id,
        examples_jsonl,
        output_dir=template_dir / "examples",
    )
    return success, failure
