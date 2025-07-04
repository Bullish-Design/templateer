"""
Generates a minimal class with typed attributes and
optional custom methods.
"""

from __future__ import annotations

import typing as _t
from pydantic import BaseModel
from templateer import TemplateModel


class SimpleClassTemplate(TemplateModel):
    __template__ = TEMPLATE

    class_name: str = "MyClass"
    attributes: dict[str, str] = {}  # attr -> default value repr
    methods: list[str] = []  # raw code blocks (already indented 4)


TEMPLATE = """
class {{ class_name }}:
    {% if not attributes and not methods -%}
    pass
    {% endif %}

    {# ---- data attributes -------------------------------------------- #}
    {% for name, default in attributes.items() -%}
    {{ name }}: _t.Any = {{ default }}
    {% endfor %}

    {# ---- custom methods --------------------------------------------- #}
    {% for meth in methods %}

    {{ meth|indent(4, true) }}
    {% endfor %}
"""
