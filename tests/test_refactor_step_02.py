from __future__ import annotations

import json
from pathlib import Path

import pytest

from templateer.cli import app
from templateer.services.generation_service import generate_examples
from templateer.services.input_service import parse_json_object


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


def test_step_02_cli_uses_service_layer_symbols() -> None:
    cli_text = Path("src/templateer/cli.py").read_text(encoding="utf-8")
    assert "from templateer.services.generation_service import generate_examples, generate_single" in cli_text
    assert "def _generate_single" not in cli_text
    assert "def _generate_examples" not in cli_text


def test_step_02_parse_json_object_contract() -> None:
    assert parse_json_object('{"ok": true}') == {"ok": True}

    with pytest.raises(ValueError, match="not valid JSON"):
        parse_json_object("{")

    with pytest.raises(ValueError, match="must be an object"):
        parse_json_object('["not","object"]')


def test_step_02_generate_examples_success_and_failure_counts(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    examples_dir = tmp_path / "templates" / "greeting" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    (examples_dir / "sample_inputs.jsonl").write_text('{"name":"Ada"}\n{"name": 3}\n', encoding="utf-8")

    batch = generate_examples(tmp_path, "greeting")

    assert batch.success == 1
    assert batch.failure == 1
