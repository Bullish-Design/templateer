"""
Template-module for generating a single Python function.
Drop this file into .templateer/  – the library will detect it.
"""

from __future__ import annotations

from pydantic import BaseModel
from templateer import TemplateModel  # <- your MVP base class


class ExampleFunctionTemplate(TemplateModel):
    """Data required to render `TEMPLATE` below."""

    __template__ = TEMPLATE

    func_name: str
    docstring: str | None = None
    body: str = "pass"


# ---------------------------------------------------------------------- #
# Jinja template (used via ExampleFunctionTemplate.__template__)
# ---------------------------------------------------------------------- #
TEMPLATE = """
def {{ func_name }}(name: str) -> str:
    {% if docstring -%}
    \"\"\"{{ docstring }}\"\"\"
    {% endif -%}
    {{ body|indent(4, true) }}
"""
