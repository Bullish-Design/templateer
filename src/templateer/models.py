# src/templateer/model.py
"""Base class for template models."""

from __future__ import annotations

import typing as _t
from pydantic import BaseModel
import jinja2


class TemplateModel(BaseModel):
    """Base class for all templates.

    Subclasses must define __template__ as a class variable containing
    a Jinja2 template string.
    """

    if _t.TYPE_CHECKING:
        __template__: _t.ClassVar[str]

    def render(self) -> str:
        """Render the template using field values.

        Returns:
            Rendered template string.

        Raises:
            AttributeError: If __template__ not defined on subclass.
            jinja2.TemplateSyntaxError: If template has invalid syntax.
        """
        if not hasattr(self.__class__, "__template__"):
            raise AttributeError(f"{self.__class__.__name__} must define __template__ class variable")

        env = jinja2.Environment()
        template = env.from_string(self.__class__.__template__)
        return template.render(**self.model_dump())
