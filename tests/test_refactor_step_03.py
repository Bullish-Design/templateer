from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from templateer.cli import app


def _load_script_module(name: str, path: Path):
    scripts_dir = str(path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_template(template_dir: Path, model_import_path: str) -> None:
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "template.mako").write_text("Hello ${name}!", encoding="utf-8")
    (template_dir / "README.md").write_text("# Template", encoding="utf-8")
    (template_dir / "manifest.json").write_text(
        json.dumps({"model_import_path": model_import_path, "description": "desc", "tags": ["a"]}),
        encoding="utf-8",
    )


def test_step_03_scripts_use_shared_bootstrap_and_services() -> None:
    new_template = Path("scripts/new_template.py").read_text(encoding="utf-8")
    demo = Path("scripts/demo_generate_from_jsonl.py").read_text(encoding="utf-8")

    assert "from _bootstrap import ensure_src_on_syspath" in new_template
    assert "templateer.services.scaffold_service" in new_template

    assert "from _bootstrap import ensure_src_on_syspath" in demo
    assert "templateer.services.generation_service" in demo


def test_step_03_new_template_script_argument_and_service_boundary(tmp_path: Path) -> None:
    module = _load_script_module("new_template_script", Path("scripts/new_template.py"))

    exit_code = module.app(
        [
            "--project-root",
            str(tmp_path),
            "--template-id",
            "invoice",
            "--model-import-path",
            "templateer.examples.models:GreetingModel",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "templates" / "invoice" / "manifest.json").exists()
    assert (tmp_path / "templates" / "registry.json").exists()


def test_step_03_cli_and_script_jsonl_paths_are_consistent(tmp_path: Path) -> None:
    _write_template(tmp_path / "templates" / "greeting", "templateer.examples.models:GreetingModel")
    assert app(["registry", "build", "--project-root", str(tmp_path)]) == 0

    jsonl_path = tmp_path / "sample_inputs.jsonl"
    jsonl_path.write_text('{"name":"Ada"}\n{"name":"Grace"}\n', encoding="utf-8")

    script_module = _load_script_module("demo_generate_script", Path("scripts/demo_generate_from_jsonl.py"))
    script_code = script_module.app(
        [
            "--project-root",
            str(tmp_path),
            "--template-id",
            "greeting",
            "--input-jsonl",
            str(jsonl_path),
            "--output-dir",
            str(tmp_path / "script_out"),
        ]
    )
    assert script_code == 0

    examples_dir = tmp_path / "templates" / "greeting" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    (examples_dir / "sample_inputs.jsonl").write_text(jsonl_path.read_text(encoding="utf-8"), encoding="utf-8")

    cli_code = app(["generate-examples", "--project-root", str(tmp_path), "--template-id", "greeting"])
    assert cli_code == 0

    assert len([p for p in (tmp_path / "script_out").iterdir() if p.is_dir()]) == 2
    assert len([p for p in examples_dir.iterdir() if p.is_dir()]) == 2
