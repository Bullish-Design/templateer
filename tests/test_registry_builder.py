from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from templateer.errors import RegistryError
from templateer.registry import build_registry, build_registry_file, load_registry


def _write_template(template_dir: Path, model_import_path: str = "acme.models:Invoice") -> None:
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "template.mako").write_text("hello ${name}", encoding="utf-8")
    (template_dir / "README.md").write_text("# Template", encoding="utf-8")
    (template_dir / "manifest.json").write_text(
        json.dumps({"model_import_path": model_import_path, "description": "desc", "tags": ["a"]}),
        encoding="utf-8",
    )


def test_build_registry_scans_templates_and_excludes_shared(tmp_path) -> None:
    templates_dir = tmp_path / "templates"
    _write_template(templates_dir / "zeta", "pkg.mod:ZetaModel")
    _write_template(templates_dir / "alpha", "pkg.mod:AlphaModel")
    _write_template(templates_dir / "_shared", "pkg.mod:SharedModel")

    registry = build_registry(tmp_path)

    assert list(registry.templates) == ["alpha", "zeta"]
    assert registry.templates["alpha"].template_uri == "templates/alpha/template.mako"
    assert registry.templates["alpha"].readme_uri == "templates/alpha/README.md"
    assert registry.templates["alpha"].model_import_path == "pkg.mod:AlphaModel"


def test_build_registry_fails_if_required_file_missing(tmp_path) -> None:
    template_dir = tmp_path / "templates" / "invoice"
    template_dir.mkdir(parents=True)
    (template_dir / "manifest.json").write_text(json.dumps({"model_import_path": "pkg.mod:Invoice"}), encoding="utf-8")

    with pytest.raises(RegistryError) as exc:
        build_registry(tmp_path)

    message = str(exc.value)
    assert "missing required files" in message
    assert "template.mako" in message
    assert "README.md" in message


def test_build_registry_does_not_import_model_modules(tmp_path) -> None:
    # Uses an import path that would fail if import execution were attempted.
    _write_template(tmp_path / "templates" / "invoice", "does.not.exist:NeverImported")

    registry = build_registry(tmp_path)

    assert registry.templates["invoice"].model_import_path == "does.not.exist:NeverImported"


def test_build_registry_file_writes_registry_json(tmp_path) -> None:
    _write_template(tmp_path / "templates" / "invoice", "pkg.mod:InvoiceModel")

    registry_path = build_registry_file(tmp_path)

    assert registry_path == tmp_path / "templates" / "registry.json"
    loaded = load_registry(registry_path)
    assert "invoice" in loaded.templates


def test_cli_registry_build_and_show(tmp_path) -> None:
    _write_template(tmp_path / "templates" / "invoice", "pkg.mod:InvoiceModel")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    build_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "templateer.cli",
            "registry",
            "build",
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert build_result.returncode == 0
    assert str(tmp_path / "templates" / "registry.json") in build_result.stdout

    show_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "templateer.cli",
            "registry",
            "show",
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert show_result.returncode == 0
    payload = json.loads(show_result.stdout)
    assert payload["templates"]["invoice"]["template_uri"] == "templates/invoice/template.mako"
