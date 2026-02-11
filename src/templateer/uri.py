"""URI validation helpers for template paths.

Template URIs are security-sensitive and must remain within ``templates/``.
"""

from __future__ import annotations

import posixpath
from pathlib import PurePosixPath

from templateer.errors import TemplateRenderError

_TEMPLATES_PREFIX = "templates"


def _reject_backslashes(uri: str, *, action: str) -> None:
    if "\\" in uri:
        raise TemplateRenderError(
            "Template URI must use POSIX separators and cannot contain backslashes",
            uri=uri,
            action=action,
        )


def _normalize_uri(uri: str) -> str:
    normalized = posixpath.normpath(uri)
    if normalized == ".":
        return ""
    return normalized


def _reject_absolute_path(uri: str, *, action: str) -> None:
    if uri.startswith("/") or PurePosixPath(uri).is_absolute():
        raise TemplateRenderError("Template URI cannot be absolute", uri=uri, action=action)


def _reject_traversal(uri: str, *, action: str) -> None:
    parts = PurePosixPath(uri).parts
    if any(part == ".." for part in parts):
        raise TemplateRenderError(
            "Template URI cannot contain path traversal segments",
            uri=uri,
            action=action,
        )


def _require_templates_prefix(uri: str, *, action: str) -> None:
    path = PurePosixPath(uri)
    if not path.parts or path.parts[0] != _TEMPLATES_PREFIX:
        raise TemplateRenderError(
            "Template URI must remain under templates/",
            uri=uri,
            action=action,
        )


def validate_template_uri(uri: str, *, action: str = "render") -> str:
    """Validate and normalize a template URI.

    Args:
        uri: Candidate template URI.
        action: Operation being attempted; included in raised errors.

    Returns:
        Canonicalized URI with POSIX separators.

    Raises:
        TemplateRenderError: If the URI violates security policy.
    """

    candidate = uri.strip()
    if not candidate:
        raise TemplateRenderError("Template URI cannot be empty", uri=uri, action=action)

    _reject_backslashes(candidate, action=action)
    _reject_absolute_path(candidate, action=action)

    normalized = _normalize_uri(candidate)
    _reject_traversal(normalized, action=action)
    _require_templates_prefix(normalized, action=action)

    return normalized
