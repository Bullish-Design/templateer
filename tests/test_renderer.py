from __future__ import annotations

import json
from pathlib import Path

import pytest

from templateer.env import TemplateEnv
from templateer.errors import TemplateRenderError
from templateer.renderer import render_template_id, render_uri


from templateer.model import TemplateModel


class RenderModel(TemplateModel):
    name: str


def _write_registry(project_root: Path, template_id: str = "invoice") -> None:
    registry_payload = {
        "templates": {
            template_id: {
                "template_uri": f"templates/{template_id}/template.mako",
                "model_import_path": "tests.test_renderer:RenderModel",
                "description": "",
                "tags": [],
                "readme_uri": f"templates/{template_id}/README.md",
            }
        }
    }
    (project_root / "templates" / "registry.json").write_text(json.dumps(registry_payload), encoding="utf-8")


def test_render_uri_strict_undefined_raises(tmp_path: Path) -> None:
    (tmp_path / "templates" / "invoice").mkdir(parents=True)
    (tmp_path / "templates" / "invoice" / "template.mako").write_text("Hello ${name} ${missing}", encoding="utf-8")

    env = TemplateEnv(tmp_path)

    with pytest.raises(TemplateRenderError) as exc:
        render_uri(env, "templates/invoice/template.mako", {"name": "Ada"})

    assert "render" in str(exc.value)
    assert "missing" in str(exc.value).lower()


def test_include_escape_attempt_fails_fast(tmp_path: Path) -> None:
    (tmp_path / "templates" / "invoice").mkdir(parents=True)
    (tmp_path / "templates" / "invoice" / "template.mako").write_text(
        '<%include file="../../secrets.mako"/>',
        encoding="utf-8",
    )

    env = TemplateEnv(tmp_path)

    with pytest.raises(TemplateRenderError) as exc:
        render_uri(env, "templates/invoice/template.mako", {})

    assert "include" in str(exc.value)
    assert "traversal" in str(exc.value).lower()


def test_include_shared_and_local_templates_work(tmp_path: Path) -> None:
    (tmp_path / "templates" / "_shared").mkdir(parents=True)
    (tmp_path / "templates" / "invoice").mkdir(parents=True)
    (tmp_path / "templates" / "_shared" / "header.mako").write_text("HDR ${name}\n", encoding="utf-8")
    (tmp_path / "templates" / "invoice" / "line.mako").write_text("LINE\n", encoding="utf-8")
    (tmp_path / "templates" / "invoice" / "template.mako").write_text(
        '<%include file="templates/_shared/header.mako"/><%include file="line.mako"/>',
        encoding="utf-8",
    )

    env = TemplateEnv(tmp_path)
    rendered = render_uri(env, "templates/invoice/template.mako", {"name": "Ada"})

    assert rendered == "HDR Ada\nLINE\n"


def test_symlinked_template_directory_renders_without_realpath(tmp_path: Path) -> None:
    source_root = tmp_path / "actual_templates"
    (source_root / "invoice").mkdir(parents=True)
    (tmp_path / "templates" / "_shared").mkdir(parents=True)

    (source_root / "invoice" / "template.mako").write_text(
        '<%include file="templates/_shared/header.mako"/>${name}', encoding="utf-8"
    )
    (tmp_path / "templates" / "_shared" / "header.mako").write_text("Hi ", encoding="utf-8")

    (tmp_path / "templates" / "invoice").symlink_to(source_root / "invoice", target_is_directory=True)
    (tmp_path / "templates" / "invoice" / "README.md").write_text("readme", encoding="utf-8")
    _write_registry(tmp_path)

    env = TemplateEnv(tmp_path)
    rendered = render_template_id(env, "invoice", {"name": "Ada"})

    assert rendered == "Hi Ada"
