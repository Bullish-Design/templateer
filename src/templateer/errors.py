"""Exception hierarchy for Templateer operations."""

from __future__ import annotations

from typing import Any


class TemplateError(Exception):
    """Base exception for Templateer with contextual metadata.

    Args:
        message: Human-readable error description.
        uri: Offending template URI when available.
        action: Operation being attempted (for example: ``render`` or ``include``).
        context: Arbitrary additional key/value context useful for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        uri: str | None = None,
        action: str | None = None,
        **context: Any,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.uri = uri
        self.action = action
        self.context = context

    def __str__(self) -> str:
        details: list[str] = []
        if self.action:
            details.append(f"action={self.action}")
        if self.uri:
            details.append(f"uri={self.uri}")
        for key, value in self.context.items():
            if value is not None:
                details.append(f"{key}={value}")

        if not details:
            return self.message
        return f"{self.message} ({', '.join(details)})"


class ManifestError(TemplateError):
    """Raised when manifest operations fail."""


class RegistryError(TemplateError):
    """Raised when registry operations fail."""


class TemplateNotFoundError(TemplateError):
    """Raised when a template ID or URI cannot be found."""


class TemplateImportError(TemplateError):
    """Raised when a configured model import fails."""


class TemplateValidationError(TemplateError):
    """Raised when user-provided template input does not validate."""


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""


class OutputWriteError(TemplateError):
    """Raised when writing rendered output fails."""


# Backward-compatible aliases kept for earlier roadmap step tests.
TemplateerError = TemplateError
TemplateURIValidationError = TemplateRenderError
