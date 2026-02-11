from __future__ import annotations

import json
import os

import pytest

from templateer.env import TemplateEnv
from templateer.errors import RegistryError


def _write_registry(project_root, template_uri: str, model_import_path: str) -> None:
    registry_path = project_root / "templates" / "registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "templates": {
            "invoice": {
                "template_uri": template_uri,
                "model_import_path": model_import_path,
            }
        }
    }
    registry_path.write_text(json.dumps(payload), encoding="utf-8")


def test_env_anchors_paths_to_project_root(tmp_path) -> None:
    env = TemplateEnv(tmp_path)

    assert env.templates_dir == tmp_path / "templates"
    assert env.output_dir == tmp_path / "output"
    assert env.log_dir == tmp_path / "log"
    assert env.registry_path == tmp_path / "templates" / "registry.json"


def test_env_reloads_registry_when_signature_changes(tmp_path) -> None:
    env = TemplateEnv(tmp_path)
    _write_registry(
        tmp_path,
        template_uri="templates/invoice/template_v1.mako",
        model_import_path="myapp.models:InvoiceTemplateV1",
    )

    first = env.get_entry("invoice")
    assert first.template_uri == "templates/invoice/template_v1.mako"
    assert first.model_import_path == "myapp.models:InvoiceTemplateV1"

    _write_registry(
        tmp_path,
        template_uri="templates/invoice/template_v2.mako",
        model_import_path="myapp.models:InvoiceTemplateV2",
    )

    second = env.get_entry("invoice")
    assert second.template_uri == "templates/invoice/template_v2.mako"
    assert second.model_import_path == "myapp.models:InvoiceTemplateV2"


def test_env_reloads_registry_when_content_changes_with_same_size_payload(tmp_path) -> None:
    env = TemplateEnv(tmp_path)
    registry_path = env.registry_path
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    first_payload = """{"templates":{"invoice":{"template_uri":"templates/invoice/template_v1.mako","model_import_path":"myapp.models:InvoiceTemplateAA"}}}"""
    second_payload = """{"templates":{"invoice":{"template_uri":"templates/invoice/template_v2.mako","model_import_path":"myapp.models:InvoiceTemplateBB"}}}"""

    assert len(first_payload) == len(second_payload)

    registry_path.write_text(first_payload, encoding="utf-8")
    first = env.get_entry("invoice")
    assert first.template_uri == "templates/invoice/template_v1.mako"
    assert first.model_import_path == "myapp.models:InvoiceTemplateAA"

    signature_before = env._cached_signature
    assert signature_before is not None

    registry_path.write_text(second_payload, encoding="utf-8")
    stat_after = registry_path.stat()

    if signature_before.inode is not None and stat_after.st_ino != signature_before.inode:
        pytest.skip("filesystem changed inode on rewrite; cannot assert inode stability")

    if stat_after.st_size != signature_before.size:
        pytest.skip("filesystem reported size change; cannot assert same-size rewrite")

        # if stat_after.st_mtime_ns != signature_before.mtime_ns:
    #    registry_path.touch(ns=(signature_before.mtime_ns, signature_before.mtime_ns))
    if stat_after.st_mtime_ns != signature_before.mtime_ns:
        # set mtime back to the prior value so size+mtime stay "stable"
        os.utime(registry_path, ns=(stat_after.st_atime_ns, signature_before.mtime_ns))

    second = env.get_entry("invoice")
    assert second.template_uri == "templates/invoice/template_v2.mako"
    assert second.model_import_path == "myapp.models:InvoiceTemplateBB"
    assert env._cached_signature != signature_before


def test_env_missing_registry_has_hint_and_relative_path(tmp_path) -> None:
    env = TemplateEnv(tmp_path)

    with pytest.raises(RegistryError) as exc:
        env.get_registry()

    message = str(exc.value)
    assert "templates/registry.json" in message
    assert "run the registry build command" in message
