from __future__ import annotations

import io
import json
from pathlib import Path

from templateer.cli import app
from templateer.services.generation_service import process_jsonl_inputs
from templateer.services.pipeline import (
    persist_artifacts,
    persist_artifacts_with_metadata,
    render_template_uri,
    resolve_registry_entry,
    validate_payload_with_model_import_path,
)



def _write_template(template_dir: Path, model_import_path: str) -> None:
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "template.mako").write_text("Hello ${name}!", encoding="utf-8")
    (template_dir / "README.md").write_text("# Template", encoding="utf-8")
    (template_dir / "manifest.json").write_text(
        json.dumps({"model_import_path": model_import_path, "description": "desc", "tags": ["a"]}),
        encoding="utf-8",
    )



def _setup_project(tmp_path: Path) -> None:
    _write_template(tmp_path / "templates" / "greeting", "templateer.examples.models:GreetingModel")
    result = app(["registry", "build", "--project-root", str(tmp_path)])
    assert result == 0



def test_step_04_pipeline_stages_are_explicit_and_callable() -> None:
    pipeline_text = Path("src/templateer/services/pipeline.py").read_text(encoding="utf-8")

    assert "def resolve_registry_entry" in pipeline_text
    assert "def validate_payload_with_model_import_path" in pipeline_text
    assert "def render_template_uri" in pipeline_text
    assert "def persist_artifacts" in pipeline_text
    assert "def persist_artifacts_with_metadata" in pipeline_text

    assert callable(resolve_registry_entry)
    assert callable(validate_payload_with_model_import_path)
    assert callable(render_template_uri)
    assert callable(persist_artifacts)
    assert callable(persist_artifacts_with_metadata)



def test_step_04_metadata_exists_for_each_render_attempt_and_jsonl_failures_have_line_numbers(tmp_path: Path) -> None:
    _setup_project(tmp_path)

    stderr = io.StringIO()
    jsonl_path = tmp_path / "inputs.jsonl"
    jsonl_path.write_text('{"name":"Ada"}\n\n{"name": 3}\n', encoding="utf-8")

    batch = process_jsonl_inputs(
        tmp_path,
        "greeting",
        jsonl_path,
        output_dir=tmp_path / "out",
        count_empty_as_failure=True,
        stderr=stderr,
    )

    assert batch.total == 3
    assert all(attempt.run_metadata is not None for attempt in batch.attempts)

    by_line = {attempt.line_number: attempt for attempt in batch.attempts}
    assert by_line[1].success is True
    assert by_line[1].run_metadata is not None
    assert by_line[1].run_metadata.output_artifact_dir == by_line[1].output_artifact_path

    assert by_line[2].success is False
    assert by_line[2].line_number == 2
    assert by_line[2].error_type == "EmptyLine"

    assert by_line[3].success is False
    assert by_line[3].line_number == 3
    assert by_line[3].error_type == "TemplateError"

    stderr_text = stderr.getvalue()
    assert "line 2: empty line" in stderr_text
    assert "line 3:" in stderr_text



def test_step_04_pipeline_integration_path_creates_expected_artifacts(tmp_path: Path) -> None:
    _setup_project(tmp_path)

    examples_dir = tmp_path / "templates" / "greeting" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    (examples_dir / "sample_inputs.jsonl").write_text('{"name":"Ada"}\n{"name":"Grace"}\n', encoding="utf-8")

    result = app(["generate-examples", "--project-root", str(tmp_path), "--template-id", "greeting"])
    assert result == 0

    generation_dirs = [p for p in examples_dir.iterdir() if p.is_dir()]
    assert len(generation_dirs) == 2

    for gen_dir in generation_dirs:
        assert (gen_dir / "input.json").exists()
        assert (gen_dir / "output.txt").exists()
