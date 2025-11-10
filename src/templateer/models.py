# src/templateer/models.py
"""Base class for template models."""

from __future__ import annotations

import typing as _t
from pathlib import Path

from pydantic import BaseModel
import jinja2


# Shared default Jinja environment used unless a subclass overrides it.
_DEFAULT_ENV = jinja2.Environment(
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


class TemplateModel(BaseModel):
    """Base class for all templates.

    Subclasses must define ``__template__`` as a class variable containing
    a Jinja2 template string.

    Optional subclass hooks:
      - ``__env__``: a pre-configured :class:`jinja2.Environment` to use
        instead of the default environment.
      - ``__jinja_filters__``: a ``dict[str, _t.Callable]`` of extra filters
        to register on a *copy* of the default environment for this class.
    """

    # Expected to be overridden by subclasses
    __template__: str

    # Optional per-class environment override
    __env__: jinja2.Environment | None = None

    # Optional additional filters for this class only
    __jinja_filters__: dict[str, _t.Callable[..., _t.Any]] | None = None

    # --- Internal helpers -------------------------------------------------

    @classmethod
    def _get_environment(cls) -> jinja2.Environment:
        """Return the Jinja2 environment for this class.

        Priority:
        1) ``__env__`` if provided on the subclass (used as-is).
        2) A shallow copy of the default env with ``__jinja_filters__`` applied.
        3) The shared default environment.
        """
        if isinstance(getattr(cls, "__env__", None), jinja2.Environment):
            return cls.__env__  # type: ignore[return-value]

        if isinstance(getattr(cls, "__jinja_filters__", None), dict):
            # Make a copy so per-class filters don't leak globally.
            env = jinja2.Environment(
                autoescape=_DEFAULT_ENV.autoescape,
                trim_blocks=_DEFAULT_ENV.trim_blocks,
                lstrip_blocks=_DEFAULT_ENV.lstrip_blocks,
            )
            # Copy globals/filters/tests from the default env
            env.globals.update(_DEFAULT_ENV.globals)
            env.filters.update(_DEFAULT_ENV.filters)
            env.tests.update(_DEFAULT_ENV.tests)
            # Add class-provided filters
            env.filters.update(cls.__jinja_filters__ or {})
            return env

        return _DEFAULT_ENV

    @classmethod
    def _get_template(cls) -> jinja2.Template:
        """Compile and return the Jinja2 template for this class."""
        template_str = getattr(cls, "__template__", None)
        if not isinstance(template_str, str) or not template_str:
            raise AttributeError(f"{cls.__name__} must define __template__.")
        env = cls._get_environment()
        return env.from_string(template_str)

    # --- Public API -------------------------------------------------------

    def render(self) -> str:
        """Render the template using the model's fields as context."""
        template = self._get_template()
        return template.render(**self.model_dump())

    def write_to(self, path: str | Path) -> None:
        """Render template and write the result to ``path``.

        Creates parent directories if they don't exist.

        Args:
            path: File path to write to.

        Raises:
            PermissionError: If the file cannot be written due to permissions.
            OSError: For other I/O related failures.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.render())
