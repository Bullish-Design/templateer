from __future__ import annotations

import json
from pathlib import Path

from templateer.env import TemplateEnv
from templateer.errors import TemplateRenderError
from templateer.model import TemplateModel
from templateer.renderer import render_template_id, render_uri


class _Step7Model(TemplateModel):
    value: str


def _write_registry(project_root: Path) -> None:
    payload = {
        "templates": {
            "step7": {
                "template_uri": "templates/step7/template.mako",
                "model_import_path": "tests.test_dev_step_7:_Step7Model",
                "description": "",
                "tags": [],
                "readme_uri": "templates/step7/README.md",
            }
        }
    }
    (project_root / "templates" / "registry.json").write_text(json.dumps(payload), encoding="utf-8")


def test_step_7_renderer_contract_and_behavior(tmp_path: Path) -> None:
    (tmp_path / "templates" / "step7").mkdir(parents=True)
    (tmp_path / "templates" / "_shared").mkdir(parents=True)
    (tmp_path / "templates" / "_shared" / "prefix.mako").write_text("prefix-", encoding="utf-8")
    (tmp_path / "templates" / "step7" / "template.mako").write_text(
        '<%include file="templates/_shared/prefix.mako"/>${value}', encoding="utf-8"
    )
    (tmp_path / "templates" / "step7" / "README.md").write_text("step7", encoding="utf-8")
    _write_registry(tmp_path)

    env = TemplateEnv(tmp_path)

    assert callable(render_uri)
    assert callable(render_template_id)
    assert render_template_id(env, "step7", {"value": "ok"}) == "prefix-ok"

    (tmp_path / "templates" / "step7" / "template.mako").write_text("${missing}", encoding="utf-8")
    try:
        render_uri(env, "templates/step7/template.mako", {})
    except TemplateRenderError:
        pass
    else:
        raise AssertionError("strict undefined should fail on missing variable")
