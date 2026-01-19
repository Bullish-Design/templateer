# src/templateer/models.py
"""Base class for template models."""

from __future__ import annotations

import typing as _t
from typing import ClassVar
from pathlib import Path

from pydantic import BaseModel
from jinja2 import Environment, StrictUndefined, Template

# Shared default Jinja environment used unless a subclass overrides it.
_DEFAULT_ENV = Environment(
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


class TemplateBase(BaseModel):
    __template__: ClassVar[str]
    __env__: ClassVar[Environment | None] = None
    __jinja_filters__: ClassVar[dict[str, _t.Callable[..., _t.Any]] | None] = None

    @classmethod
    def _get_environment(cls) -> Environment:
        if isinstance(getattr(cls, "__env__", None), Environment):
            return cls.__env__  # type: ignore[return-value]

        if isinstance(getattr(cls, "__jinja_filters__", None), dict):
            env = Environment(
                autoescape=_DEFAULT_ENV.autoescape,
                trim_blocks=_DEFAULT_ENV.trim_blocks,
                lstrip_blocks=_DEFAULT_ENV.lstrip_blocks,
            )
            env.globals.update(_DEFAULT_ENV.globals)
            env.filters.update(_DEFAULT_ENV.filters)
            env.tests.update(_DEFAULT_ENV.tests)
            env.filters.update(cls.__jinja_filters__ or {})
            return env

        return _DEFAULT_ENV

    @classmethod
    def _get_template(cls) -> Template:
        template_str = getattr(cls, "__template__", None)
        if not isinstance(template_str, str) or not template_str:
            raise AttributeError(f"{cls.__name__} must define __template__")
        return cls._get_environment().from_string(template_str)

    @staticmethod
    def _stringify_templates(obj: _t.Any) -> _t.Any:
        """Recursively turn TemplateBase instances into their rendered strings.

        Handles nested structures (dict, list, tuple, set). Leaves other types unchanged.
        """
        # If it's a template model, render it
        if isinstance(obj, TemplateBase):
            return str(obj)  # uses __str__ on TemplateModel

        # Recurse through containers
        if isinstance(obj, dict):
            return {k: TemplateBase._stringify_templates(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [TemplateBase._stringify_templates(v) for v in obj]
        if isinstance(obj, tuple):
            return tuple(TemplateBase._stringify_templates(v) for v in obj)
        if isinstance(obj, set):
            return {TemplateBase._stringify_templates(v) for v in obj}

        return obj


class TemplateModel(TemplateBase):
    """Thin public model: render and write-to-file APIs."""

    def render(self) -> str:
        """Render with nested TemplateModels converted to strings.

        Build context from live attributes (not model_dump) so nested models
        remain instances we can stringify.
        """
        template = self._get_template()
        # self.model_fields is Pydantic v2 API: field names -> FieldInfo
        ctx = {name: self._stringify_templates(getattr(self, name)) for name in self.model_fields}
        return template.render(**ctx)

    def write_to(self, path: str | Path) -> None:
        """Render template and write the result to ``path``.

        Creates parent directories if they don't exist.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.render())

    def __str__(self) -> str:
        """Return rendered template for implicit/nested rendering."""
        return self.render()
