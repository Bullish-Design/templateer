# src/templateer/models.py
"""Base class for template models."""

from __future__ import annotations

import typing as _t
from collections.abc import Mapping, Sequence
from typing import ClassVar
from pathlib import Path

from pydantic import BaseModel
from jinja2 import Environment, StrictUndefined, Template

_DEFAULT_ENV_OPTIONS = {
    "autoescape": False,
    "undefined": StrictUndefined,
    "trim_blocks": True,
    "lstrip_blocks": True,
    "keep_trailing_newline": True,
}


class TemplateBase(BaseModel):
    __template__: ClassVar[str]
    __env__: ClassVar[Environment | None] = None
    __jinja_filters__: ClassVar[dict[str, _t.Callable[..., _t.Any]] | None] = None

    @classmethod
    def _get_environment(cls) -> Environment:
        if isinstance(getattr(cls, "__env__", None), Environment):
            return cls.__env__  # type: ignore[return-value]

        env = Environment(**_DEFAULT_ENV_OPTIONS)
        if isinstance(getattr(cls, "__jinja_filters__", None), dict):
            env.filters.update(cls.__jinja_filters__ or {})

        return env

    @classmethod
    def _get_template(cls) -> Template:
        template_str = getattr(cls, "__template__", None)
        if not isinstance(template_str, str) or not template_str:
            raise AttributeError(f"{cls.__name__} must define __template__")
        return cls._get_environment().from_string(template_str)

    @staticmethod
    def _stringify_templates(obj: _t.Any) -> _t.Any:
        """Recursively turn TemplateBase instances into their rendered strings.

        Handles nested structures (mappings, sequences, sets). Leaves other types unchanged.
        Set iteration order is nondeterministic, so output order is not guaranteed.
        """
        visited: set[int] = set()

        def _stringify(value: _t.Any) -> _t.Any:
            # If it's a template model, render it
            if isinstance(value, TemplateBase):
                return str(value)  # uses __str__ on TemplateModel

            if isinstance(value, (Mapping, Sequence, set)) and not isinstance(value, (str, bytes)):
                value_id = id(value)
                if value_id in visited:
                    return value
                visited.add(value_id)

            # Recurse through containers
            if isinstance(value, Mapping):
                return {k: _stringify(v) for k, v in value.items()}
            if isinstance(value, tuple):
                return tuple(_stringify(v) for v in value)
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                return [_stringify(v) for v in value]
            if isinstance(value, set):
                return {_stringify(v) for v in value}

            return value

        return _stringify(obj)


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
