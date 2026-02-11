from __future__ import annotations

import json

import pytest

from templateer.errors import ManifestError
from templateer.manifest import TemplateManifest, dump_manifest, load_manifest


def test_manifest_rejects_invalid_model_import_path(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"model_import_path": "not-valid"}), encoding="utf-8")

    with pytest.raises(ManifestError) as exc:
        load_manifest(path)

    assert "model_import_path" in str(exc.value)
    assert "pkg.module:ClassName" in str(exc.value)


def test_manifest_round_trip(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    manifest = TemplateManifest(
        model_import_path="myapp.models:InvoiceTemplate",
        description="Invoice renderer",
        tags=["billing"],
    )

    dump_manifest(manifest, path)
    loaded = load_manifest(path)

    assert loaded == manifest
