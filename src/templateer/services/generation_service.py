"""Generation workflows shared by CLI and scripts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from templateer.env import TemplateEnv
from templateer.errors import TemplateError
from templateer.output import persist_render_result
from templateer.services.input_service import parse_json_object
from templateer.services.metadata import GenerationBatchResult, RenderAttemptMetadata, RenderRunMetadata
from templateer.services.pipeline import render_template_uri, resolve_registry_entry, validate_payload_with_model_import_path


def _classify_error_type(exc: Exception) -> str:
    """Return stable error categories for render-attempt metadata."""

    if isinstance(exc, TemplateError):
        return "TemplateError"
    return type(exc).__name__


def render_template_id(env: TemplateEnv, template_id: str, payload: dict[str, object]) -> str:
    """Render ``template_id`` for one payload after validation."""

    entry = resolve_registry_entry(env, template_id)
    context = validate_payload_with_model_import_path(payload, entry.model_import_path)
    return render_template_uri(env, entry.template_uri, context)


def generate_single(project_root: Path, template_id: str, payload: dict[str, object]) -> RenderAttemptMetadata:
    """Render one payload for a template and persist generation artifacts."""

    env = TemplateEnv(project_root)
    run_timestamp = datetime.now(timezone.utc)
    run_metadata = RenderRunMetadata()

    try:
        rendered = render_template_id(env, template_id, payload)
        template_dir = project_root / "templates" / template_id
        gen_dir = template_dir / "gen"
        input_json = json.dumps(payload, indent=2) + "\n"
        output_dir, run_metadata = persist_render_result(gen_dir, input_json, rendered, run_metadata)
        return RenderAttemptMetadata(
            template_id=template_id,
            run_timestamp=run_timestamp,
            input_source_kind="inline_json",
            input_path=None,
            line_number=None,
            output_artifact_path=output_dir,
            success=True,
            run_metadata=run_metadata,
        )
    except (TemplateError, ValueError) as exc:
        return RenderAttemptMetadata(
            template_id=template_id,
            run_timestamp=run_timestamp,
            input_source_kind="inline_json",
            input_path=None,
            line_number=None,
            output_artifact_path=None,
            success=False,
            error_type=_classify_error_type(exc),
            error_message=str(exc),
            run_metadata=run_metadata,
        )


def process_jsonl_inputs(
    project_root: Path,
    template_id: str,
    input_jsonl: Path,
    *,
    output_dir: Path,
    fail_fast: bool = False,
    count_empty_as_failure: bool = False,
    stderr: object = sys.stderr,
) -> GenerationBatchResult:
    """Render one template for each JSON object line in a JSONL file."""

    attempts: list[RenderAttemptMetadata] = []
    env = TemplateEnv(project_root)

    with input_jsonl.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            run_timestamp = datetime.now(timezone.utc)
            line = raw_line.strip()
            if not line:
                if count_empty_as_failure:
                    metadata = RenderAttemptMetadata(
                        template_id=template_id,
                        run_timestamp=run_timestamp,
                        input_source_kind="jsonl",
                        input_path=input_jsonl,
                        line_number=line_number,
                        output_artifact_path=None,
                        success=False,
                        error_type="EmptyLine",
                        error_message="empty line",
                        run_metadata=RenderRunMetadata(),
                    )
                    attempts.append(metadata)
                    print(f"line {line_number}: empty line", file=stderr)
                    if fail_fast:
                        break
                continue

            run_metadata = RenderRunMetadata()
            try:
                payload = parse_json_object(line)
                rendered = render_template_id(env, template_id, payload)
                input_json = json.dumps(payload, indent=2) + "\n"
                rendered_path, run_metadata = persist_render_result(output_dir, input_json, rendered, run_metadata)
                attempts.append(
                    RenderAttemptMetadata(
                        template_id=template_id,
                        run_timestamp=run_timestamp,
                        input_source_kind="jsonl",
                        input_path=input_jsonl,
                        line_number=line_number,
                        output_artifact_path=rendered_path,
                        success=True,
                        run_metadata=run_metadata,
                    )
                )
            except (TemplateError, ValueError) as exc:
                attempts.append(
                    RenderAttemptMetadata(
                        template_id=template_id,
                        run_timestamp=run_timestamp,
                        input_source_kind="jsonl",
                        input_path=input_jsonl,
                        line_number=line_number,
                        output_artifact_path=None,
                        success=False,
                        error_type=_classify_error_type(exc),
                        error_message=str(exc),
                        error_details=line,
                        run_metadata=run_metadata,
                    )
                )
                print(f"line {line_number}: {exc}", file=stderr)
                if fail_fast:
                    break

    return GenerationBatchResult(attempts=tuple(attempts))


def generate_examples(project_root: Path, template_id: str) -> GenerationBatchResult:
    """Render built-in sample_inputs.jsonl for a template."""

    template_dir = project_root / "templates" / template_id
    examples_jsonl = template_dir / "examples" / "sample_inputs.jsonl"
    return process_jsonl_inputs(
        project_root,
        template_id,
        examples_jsonl,
        output_dir=template_dir / "examples",
    )
