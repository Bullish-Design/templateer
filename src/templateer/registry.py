"""Contracts and JSON helpers for template registry."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from templateer.errors import ManifestError, RegistryError, TemplateError
from templateer.manifest import TemplateManifest, _validate_model_import_path, load_manifest
from templateer.uri import validate_template_uri

_REQUIRED_TEMPLATE_FILES = ("template.mako", "manifest.json", "README.md")


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


def _as_project_relative(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


def _ensure_required_template_files(project_root: Path, template_id: str, template_dir: Path) -> None:
    missing = [name for name in _REQUIRED_TEMPLATE_FILES if not (template_dir / name).is_file()]
    if missing:
        raise RegistryError(
            "template folder is missing required files",
            template_id=template_id,
            path=_as_project_relative(template_dir, project_root),
            missing=",".join(missing),
        )


def build_registry(project_root: str | Path) -> TemplateRegistry:
    """Build an in-memory registry by scanning ``templates/*`` folders.

    The build is deterministic: template IDs are sorted lexicographically.
    """

    root = Path(project_root)
    templates_dir = root / "templates"
    if not templates_dir.is_dir():
        raise RegistryError(
            "templates directory does not exist",
            path=_as_project_relative(templates_dir, root),
        )

    entries: dict[str, dict[str, Any]] = {}
    for candidate in sorted(templates_dir.iterdir(), key=lambda path: path.name):
        if not candidate.is_dir():
            continue

        template_id = candidate.name
        if template_id == "_shared":
            continue

        _ensure_required_template_files(root, template_id, candidate)

        manifest_path = candidate / "manifest.json"
        try:
            manifest = load_manifest(manifest_path)
        except ManifestError as exc:
            raise RegistryError(
                "manifest validation failed while building registry",
                template_id=template_id,
                path=_as_project_relative(manifest_path, root),
                detail=str(exc),
            ) from exc

        entries[template_id] = {
            "template_uri": f"templates/{template_id}/template.mako",
            "model_import_path": manifest.model_import_path,
            "description": manifest.description,
            "tags": manifest.tags,
            "readme_uri": f"templates/{template_id}/README.md",
        }

    return TemplateRegistry.model_validate({"templates": entries})


def dump_registry_atomically(registry: TemplateRegistry, path: str | Path) -> None:
    """Write registry JSON to disk atomically using ``os.replace``."""

    registry_path = Path(path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    payload = registry.model_dump_json(indent=2) + "\n"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=registry_path.parent,
            prefix=f".{registry_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_name, registry_path)
    finally:
        if temp_name is not None:
            temp_path = Path(temp_name)
            if temp_path.exists():
                temp_path.unlink()


def build_registry_file(project_root: str | Path) -> Path:
    """Build and persist ``templates/registry.json`` for a project root."""

    root = Path(project_root)
    registry = build_registry(root)
    registry_path = root / "templates" / "registry.json"
    dump_registry_atomically(registry, registry_path)
    return registry_path


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

    dump_registry_atomically(registry, path)
