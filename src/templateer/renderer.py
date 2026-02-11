"""Safe Mako rendering helpers."""

from __future__ import annotations

import posixpath
from pathlib import Path
from typing import Any

from mako.lookup import TemplateLookup
from mako import exceptions as mako_exceptions

from templateer.errors import TemplateRenderError
from templateer.importers import import_model, parse_model_input_data
from templateer.uri import validate_template_uri


class _SafeTemplateLookup(TemplateLookup):
    """TemplateLookup that enforces template URI policy for targets and includes."""

    def _resolve_template_uri(self, uri: str, relativeto: str | None = None, *, action: str) -> str:
        candidate = uri.strip()
        if not candidate:
            raise TemplateRenderError("Template URI cannot be empty", uri=uri, action=action)

        if action == "include":
            raw_parts = Path(candidate).parts
            if any(part == ".." for part in raw_parts):
                raise TemplateRenderError(
                    "Include URI cannot contain path traversal segments",
                    uri=uri,
                    action=action,
                )

        if not candidate.startswith("templates/") and relativeto:
            base_uri = posixpath.dirname(relativeto)
            candidate = posixpath.join(base_uri, candidate)

        return validate_template_uri(candidate, action=action)

    def adjust_uri(self, uri: str, relativeto: str) -> str:  # type: ignore[override]
        """Resolve include URIs using Mako's include hook."""

        return self._resolve_template_uri(uri, relativeto, action="include")

    def get_template(self, uri: str, relativeto: str | None = None):  # type: ignore[override]
        action = "include" if relativeto is not None else "render"
        safe_uri = self._resolve_template_uri(uri, relativeto, action=action)

        try:
            return super().get_template(safe_uri)
        except TemplateRenderError:
            raise
        except Exception as exc:
            raise TemplateRenderError(
                "Template lookup failed",
                uri=safe_uri,
                action=action,
                detail=str(exc),
            ) from exc


def _build_lookup(project_root: Path) -> _SafeTemplateLookup:
    return _SafeTemplateLookup(
        directories=[project_root.as_posix()],
        strict_undefined=True,
        filesystem_checks=True,
        module_directory=None,
    )


def render_uri(env: Any, template_uri: str, context: dict[str, Any]) -> str:
    """Render a template URI under ``templates/**`` with strict Mako behavior."""

    safe_uri = validate_template_uri(template_uri, action="render")
    lookup = _build_lookup(Path(env.project_root))

    try:
        template = lookup.get_template(safe_uri)
        return template.render(**context)
    except TemplateRenderError:
        raise
    except Exception as exc:
        detail = mako_exceptions.text_error_template().render().strip()
        raise TemplateRenderError(
            "Template rendering failed",
            uri=safe_uri,
            action="render",
            detail=detail or str(exc),
        ) from exc


def render_template_id(env: Any, template_id: str, json_data: dict[str, Any]) -> str:
    """Resolve a template by id from registry, validate input, and render."""

    entry = env.get_entry(template_id)
    model_class = import_model(entry.model_import_path)
    model = parse_model_input_data(json_data, model_class)
    context = model.model_dump()
    return render_uri(env, entry.template_uri, context)
