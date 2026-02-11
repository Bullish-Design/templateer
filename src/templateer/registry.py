"""Contracts and JSON helpers for template registry."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from templateer.errors import ManifestError, RegistryError, TemplateError
from templateer.manifest import TemplateManifest, _validate_model_import_path
from templateer.uri import validate_template_uri


@dataclass(eq=True)
class TemplateEntry(TemplateManifest):
    """Runtime template registry entry."""

    template_uri: str = ""
    readme_uri: str | None = None

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> TemplateEntry:
        if not isinstance(payload, dict):
            raise RegistryError("template entry must be a JSON object")

        allowed = {"template_uri", "model_import_path", "description", "tags", "readme_uri"}
        extra = set(payload) - allowed
        if extra:
            raise RegistryError("template entry contains unknown fields", fields=sorted(extra))

        if "template_uri" not in payload:
            raise RegistryError("template_uri is required")
        if "model_import_path" not in payload:
            raise RegistryError("model_import_path is required")

        template_uri = validate_template_uri(str(payload["template_uri"]), action="build")
        model_import_path = _validate_model_import_path(payload["model_import_path"])

        description = payload.get("description")
        tags = payload.get("tags", [])
        readme_uri = payload.get("readme_uri")

        if description is not None and not isinstance(description, str):
            raise RegistryError("description must be a string")
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise RegistryError("tags must be a list of strings")
        if readme_uri is not None:
            readme_uri = validate_template_uri(str(readme_uri), action="build")

        return cls(
            template_uri=template_uri,
            model_import_path=model_import_path,
            description=description,
            tags=list(tags),
            readme_uri=readme_uri,
        )

    def model_dump(self) -> dict[str, Any]:
        return {
            "template_uri": self.template_uri,
            "model_import_path": self.model_import_path,
            "description": self.description,
            "tags": list(self.tags),
            "readme_uri": self.readme_uri,
        }


@dataclass(eq=True)
class TemplateRegistry:
    """Loaded registry mapping template_id -> template entry."""

    templates: dict[str, TemplateEntry] = field(default_factory=dict)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> TemplateRegistry:
        if not isinstance(payload, dict):
            raise RegistryError("registry must be a JSON object")

        extra = set(payload) - {"templates"}
        if extra:
            raise RegistryError("registry contains unknown fields", fields=sorted(extra))

        raw_templates = payload.get("templates", {})
        if not isinstance(raw_templates, dict):
            raise RegistryError("templates must be an object of template_id -> entry")

        templates: dict[str, TemplateEntry] = {}
        for template_id, raw_entry in raw_templates.items():
            if not isinstance(template_id, str) or not template_id.strip():
                raise RegistryError("template_id cannot be empty")
            if "/" in template_id or "\\" in template_id:
                raise RegistryError("template_id must be a simple identifier", template_id=template_id)

            entry = TemplateEntry.model_validate(raw_entry)
            if entry.readme_uri is None:
                entry.readme_uri = validate_template_uri(f"templates/{template_id}/README.md", action="build")
            templates[template_id] = entry

        return cls(templates=templates)

    def model_dump(self) -> dict[str, Any]:
        return {"templates": {template_id: entry.model_dump() for template_id, entry in self.templates.items()}}

    def model_dump_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent)


def load_registry(path: str | Path) -> TemplateRegistry:
    """Load and validate the runtime registry JSON."""

    registry_path = Path(path)
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryError("registry file does not exist", path=str(registry_path)) from exc
    except json.JSONDecodeError as exc:
        raise RegistryError("registry is not valid JSON", path=str(registry_path), detail=str(exc)) from exc

    try:
        return TemplateRegistry.model_validate(payload)
    except (RegistryError, ManifestError, TemplateError) as exc:
        raise RegistryError("registry validation failed", path=str(registry_path), detail=str(exc)) from exc


def dump_registry(registry: TemplateRegistry, path: str | Path) -> None:
    """Write registry JSON to disk."""

    registry_path = Path(path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(registry.model_dump_json(indent=2) + "\n", encoding="utf-8")
