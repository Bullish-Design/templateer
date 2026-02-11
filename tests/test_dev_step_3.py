from __future__ import annotations

import json

import pytest

from templateer.errors import ManifestError, RegistryError
from templateer.manifest import TemplateManifest, load_manifest
from templateer.registry import TemplateRegistry, load_registry


def test_step_3_contracts_exist() -> None:
    assert TemplateManifest is not None
    assert TemplateRegistry is not None


def test_step_3_manifest_and_registry_acceptance(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"model_import_path": "bad_path"}), encoding="utf-8")
    with pytest.raises(ManifestError):
        load_manifest(manifest_path)

    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "templates": {
                    "invoice": {
                        "template_uri": "../secrets.mako",
                        "model_import_path": "myapp.models:InvoiceTemplate",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RegistryError):
        load_registry(registry_path)


def test_step_3_round_trip_json_helpers(tmp_path) -> None:
    registry_path = tmp_path / "registry.json"
    payload = {
        "templates": {
            "invoice": {
                "template_uri": "templates/invoice/template.mako",
                "model_import_path": "myapp.models:InvoiceTemplate",
            }
        }
    }
    registry_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = load_registry(registry_path)
    assert registry.templates["invoice"].readme_uri == "templates/invoice/README.md"
