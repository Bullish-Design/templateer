from __future__ import annotations

import json
from pathlib import Path

from templateer.cli import app


def _write_template(template_dir: Path, model_import_path: str) -> None:
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "template.mako").write_text("Hello ${name}!\n% if title:\n(${title})\n% endif", encoding="utf-8")
    (template_dir / "README.md").write_text("# Template", encoding="utf-8")
    (template_dir / "manifest.json").write_text(
        json.dumps({"model_import_path": model_import_path, "description": "desc", "tags": ["a"]}),
        encoding="utf-8",
    )


def _setup_project(tmp_path: Path) -> None:
    _write_template(tmp_path / "templates" / "greeting", "templateer.examples.models:GreetingModel")
    result = app(["registry", "build", "--project-root", str(tmp_path)])
    assert result == 0


def test_generate_writes_timestamped_artifacts_to_gen(tmp_path: Path) -> None:
    _setup_project(tmp_path)

    result = app(
        [
            "generate",
            "--project-root",
            str(tmp_path),
            "--template-id",
            "greeting",
            "--input-json",
            '{"name":"Ada","title":"Engineer"}',
        ]
    )

    assert result == 0

    generated = sorted((tmp_path / "templates" / "greeting" / "gen").iterdir())
    assert len(generated) == 1
    assert generated[0].is_dir()
    assert (generated[0] / "input.json").read_text(encoding="utf-8") == '{\n  "name": "Ada",\n  "title": "Engineer"\n}\n'
    assert (generated[0] / "output.txt").read_text(encoding="utf-8") == "Hello Ada!\n(Engineer)\n"


def test_generate_examples_writes_one_timestamped_dir_per_jsonl_object(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    examples_dir = tmp_path / "templates" / "greeting" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    (examples_dir / "sample_inputs.jsonl").write_text(
        '{"name":"Ada"}\n{"name":"Grace","title":"Rear Admiral"}\n',
        encoding="utf-8",
    )

    result = app(["generate-examples", "--project-root", str(tmp_path), "--template-id", "greeting"])

    assert result == 0
    generated = sorted(path for path in examples_dir.iterdir() if path.is_dir())
    assert len(generated) == 2

    inputs = [json.loads((path / "input.json").read_text(encoding="utf-8")) for path in generated]
    assert {payload["name"] for payload in inputs} == {"Ada", "Grace"}
    outputs = {(path / "output.txt").read_text(encoding="utf-8") for path in generated}
    assert "Hello Ada!\n" in outputs
    assert "Hello Grace!\n(Rear Admiral)\n" in outputs


def test_generate_single_returns_metadata(tmp_path: Path) -> None:
    from templateer.services.generation_service import generate_single

    _setup_project(tmp_path)
    metadata = generate_single(tmp_path, "greeting", {"name": "Ada"})

    assert metadata.success is True
    assert metadata.template_id == "greeting"
    assert metadata.input_source_kind == "inline_json"
    assert metadata.input_path is None
    assert metadata.line_number is None
    assert metadata.output_artifact_path is not None
    assert metadata.output_artifact_path.is_dir()
    assert metadata.run_metadata is not None
    assert metadata.run_metadata.output_artifact_dir == metadata.output_artifact_path


def test_process_jsonl_inputs_returns_metadata_for_failed_rows(tmp_path: Path) -> None:
    from templateer.services.generation_service import process_jsonl_inputs

    _setup_project(tmp_path)
    jsonl_path = tmp_path / "inputs.jsonl"
    jsonl_path.write_text('{"name":"Ada"}\n\n{"name": 3}\n', encoding="utf-8")
    output_dir = tmp_path / "out"

    batch = process_jsonl_inputs(
        tmp_path,
        "greeting",
        jsonl_path,
        output_dir=output_dir,
        count_empty_as_failure=True,
    )

    assert batch.total == 3
    assert batch.success == 1
    assert batch.failure == 2

    by_line = {attempt.line_number: attempt for attempt in batch.attempts}
    assert by_line[1].success is True
    assert by_line[1].output_artifact_path is not None
    assert by_line[1].run_metadata is not None
    assert by_line[1].run_metadata.output_artifact_dir == by_line[1].output_artifact_path

    assert by_line[2].success is False
    assert by_line[2].error_type == "EmptyLine"
    assert by_line[2].error_message == "empty line"
    assert by_line[2].run_metadata is not None
    assert by_line[2].run_metadata.output_artifact_dir is None

    assert by_line[3].success is False
    assert by_line[3].error_type == "TemplateError"
    assert by_line[3].error_message is not None
    assert by_line[3].error_details == '{"name": 3}'
    assert by_line[3].input_path == jsonl_path
    assert by_line[3].run_metadata is not None
    assert by_line[3].run_metadata.output_artifact_dir is None
