# src/tests/test_model.py
"""Tests for TemplateModel base class."""

from __future__ import annotations

import pytest
from templateer import TemplateModel


def test_simple_render():
    """Test basic template rendering."""
    TEMPLATE = "Hello {{ name }}, value is {{ value }}"

    class SimpleTemplate(TemplateModel):
        __template__ = TEMPLATE
        name: str
        value: int

    template = SimpleTemplate(name="World", value=42)
    result = template.render()
    assert result == "Hello World, value is 42"


def test_render_with_defaults():
    """Test rendering with default values."""
    TEMPLATE = "{{ greeting }} {{ name }}"

    class DefaultTemplate(TemplateModel):
        __template__ = TEMPLATE
        greeting: str = "Hi"
        name: str = "there"

    template = DefaultTemplate()
    assert template.render() == "Hi there"

    template = DefaultTemplate(greeting="Hello", name="World")
    assert template.render() == "Hello World"


def test_render_with_jinja_filters():
    """Test that Jinja2 filters work."""
    TEMPLATE = "{{ text|upper }}"

    class FilterTemplate(TemplateModel):
        __template__ = TEMPLATE
        text: str

    template = FilterTemplate(text="hello")
    assert template.render() == "HELLO"


def test_render_with_conditionals():
    """Test Jinja2 conditional logic."""
    TEMPLATE = """
{% if show -%}
Value: {{ value }}
{% else -%}
Hidden
{% endif -%}
"""

    class ConditionalTemplate(TemplateModel):
        __template__ = TEMPLATE
        show: bool
        value: str

    template = ConditionalTemplate(show=True, value="test")
    assert "Value: test" in template.render()

    template = ConditionalTemplate(show=False, value="test")
    assert "Hidden" in template.render()


def test_render_with_loops():
    """Test Jinja2 loop constructs."""

    TEMPLATE = """
{% for item in items -%}
- {{ item }}
{% endfor -%}
"""

    class LoopTemplate(TemplateModel):
        __template__ = TEMPLATE
        items: list[str]

    template = LoopTemplate(items=["a", "b", "c"])
    result = template.render()
    assert "- a" in result
    assert "- b" in result
    assert "- c" in result


def test_missing_template_attribute():
    """Test error when __template__ not defined."""

    class NoTemplate(TemplateModel):
        value: str

    template = NoTemplate(value="test")
    with pytest.raises(AttributeError, match="must define __template__"):
        template.render()


def test_invalid_template_syntax():
    """Test error handling for invalid Jinja2 syntax."""

    class BadTemplate(TemplateModel):
        __template__ = "{{ unclosed"
        value: str

    template = BadTemplate(value="test")
    with pytest.raises(Exception):  # jinja2.TemplateSyntaxError
        template.render()


def test_pydantic_validation():
    """Test that Pydantic validation works."""

    class TypedTemplate(TemplateModel):
        __template__ = "{{ value }}"
        value: int

    template = TypedTemplate(value=42)
    assert template.render() == "42"

    with pytest.raises(Exception):  # pydantic.ValidationError
        TypedTemplate(value="not an int")
