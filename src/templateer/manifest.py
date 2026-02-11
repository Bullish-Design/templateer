"""Contracts and JSON helpers for per-template manifest files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from templateer.errors import ManifestError


@dataclass(eq=True)
class TemplateManifest:
    """Manifest metadata stored next to a template."""

    model_import_path: str
    description: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> TemplateManifest:
        if not isinstance(payload, dict):
            raise ManifestError("manifest must be a JSON object")

        allowed = {"model_import_path", "description", "tags"}
        extra = set(payload) - allowed
        if extra:
            raise ManifestError("manifest contains unknown fields", fields=sorted(extra))

        if "model_import_path" not in payload:
            raise ManifestError("model_import_path is required")

        import_path = _validate_model_import_path(payload["model_import_path"])
        description = payload.get("description")
        tags = payload.get("tags", [])

        if description is not None and not isinstance(description, str):
            raise ManifestError("description must be a string")

        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise ManifestError("tags must be a list of strings")

        return cls(model_import_path=import_path, description=description, tags=list(tags))

    def model_dump(self) -> dict[str, Any]:
        return {
            "model_import_path": self.model_import_path,
            "description": self.description,
            "tags": list(self.tags),
        }

    def model_dump_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent)


def _validate_model_import_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ManifestError("model_import_path must be a string")

    candidate = value.strip()
    if not candidate:
        raise ManifestError("model_import_path is required")

    if ":" not in candidate:
        raise ManifestError("model_import_path must use 'pkg.module:ClassName' format")

    module_part, class_part = candidate.split(":", 1)
    if not module_part or not class_part:
        raise ManifestError("model_import_path must use 'pkg.module:ClassName' format")

    if any(not segment.isidentifier() for segment in module_part.split(".")):
        raise ManifestError("model_import_path module must be a dotted python import path")

    if not class_part.isidentifier():
        raise ManifestError("model_import_path class must be a valid python identifier")

    return candidate


def load_manifest(path: str | Path) -> TemplateManifest:
    """Load a template manifest from JSON file."""

    manifest_path = Path(path)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError("manifest file does not exist", path=str(manifest_path)) from exc
    except json.JSONDecodeError as exc:
        raise ManifestError("manifest is not valid JSON", path=str(manifest_path), detail=str(exc)) from exc

    try:
        return TemplateManifest.model_validate(payload)
    except ManifestError as exc:
        raise ManifestError("manifest validation failed", path=str(manifest_path), detail=str(exc)) from exc


def dump_manifest(manifest: TemplateManifest, path: str | Path) -> None:
    """Persist manifest JSON to disk."""

    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
