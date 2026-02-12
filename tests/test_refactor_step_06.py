from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from templateer.cli import app


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


def _run_subprocess(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def test_step_06_status_doc_exists_and_records_phase_convergence() -> None:
    status_text = Path("JUST_REFACTOR_STATUS.md").read_text(encoding="utf-8")

    assert "What moved into `templateer.services`" in status_text
    assert "What stayed as adapters" in status_text
    assert "Quality gates" in status_text
    assert "Known follow-up items" in status_text



def test_step_06_cli_and_script_generation_paths_preserve_failure_semantics(tmp_path: Path) -> None:
    _setup_project(tmp_path)

    examples_dir = tmp_path / "templates" / "greeting" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    sample_jsonl = examples_dir / "sample_inputs.jsonl"
    sample_jsonl.write_text('{"name":"Ada"}\n\n{"name": 3}\n', encoding="utf-8")

    cli_result = _run_subprocess(
        [
            sys.executable,
            "-m",
            "templateer.cli",
            "generate-examples",
            "--project-root",
            str(tmp_path),
            "--template-id",
            "greeting",
        ],
        cwd=Path.cwd(),
    )

    script_out = tmp_path / "script_out"
    script_result = _run_subprocess(
        [
            sys.executable,
            "scripts/demo_generate_from_jsonl.py",
            "--project-root",
            str(tmp_path),
            "--template-id",
            "greeting",
            "--input-jsonl",
            str(sample_jsonl),
            "--output-dir",
            str(script_out),
        ],
        cwd=Path.cwd(),
    )

    assert cli_result.returncode == 1
    assert script_result.returncode == 1

    assert "success=1, failure=2" in cli_result.stdout
    assert "success=1, failure=2" in script_result.stdout
    assert "line 2: empty line" in cli_result.stderr
    assert "line 3:" in cli_result.stderr
    assert "line 2: empty line" in script_result.stderr
    assert "line 3:" in script_result.stderr

    cli_generations = sorted(path for path in examples_dir.iterdir() if path.is_dir())
    script_generations = sorted(path for path in script_out.iterdir() if path.is_dir())
    assert len(cli_generations) == 1
    assert len(script_generations) == 1



def test_step_06_justfile_defines_expected_quality_gate_entrypoints() -> None:
    justfile_text = Path("Justfile").read_text(encoding="utf-8")

    assert "run-tests:" in justfile_text
    assert "python -m pytest -q" in justfile_text

    assert "run-template-examples template_id: build-registry" in justfile_text
    assert "python -m templateer.cli generate-examples" in justfile_text
    assert "--project-root {{project_root}}" in justfile_text

    assert "create-template template_id model_import_path" in justfile_text
    assert "scripts/new_template.py" in justfile_text
