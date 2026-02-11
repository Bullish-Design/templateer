from __future__ import annotations

import json

import pytest

from templateer.errors import RegistryError
from templateer.registry import TemplateRegistry, dump_registry, load_registry


def test_registry_rejects_uri_outside_templates_boundary(tmp_path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "templates": {
                    "invoice": {
                        "template_uri": "outside/invoice/template.mako",
                        "model_import_path": "myapp.models:InvoiceTemplate",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RegistryError) as exc:
        load_registry(path)

    message = str(exc.value)
    assert "templates/" in message
    assert "build" in message


def test_registry_round_trip_and_default_readme_uri(tmp_path) -> None:
    path = tmp_path / "registry.json"
    registry = TemplateRegistry.model_validate(
        {
            "templates": {
                "invoice": {
                    "template_uri": "templates/invoice/template.mako",
                    "model_import_path": "myapp.models:InvoiceTemplate",
                    "description": "Invoice renderer",
                    "tags": ["billing"],
                }
            }
        }
    )

    dump_registry(registry, path)
    loaded = load_registry(path)

    assert loaded.templates["invoice"].template_uri == "templates/invoice/template.mako"
    assert loaded.templates["invoice"].readme_uri == "templates/invoice/README.md"
    assert loaded.model_dump() == registry.model_dump()


def test_registry_rejects_invalid_model_import_path(tmp_path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "templates": {
                    "invoice": {
                        "template_uri": "templates/invoice/template.mako",
                        "model_import_path": "missing_colon",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RegistryError) as exc:
        load_registry(path)

    assert "model_import_path" in str(exc.value)
