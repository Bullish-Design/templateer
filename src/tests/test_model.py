# src/tests/test_model.py
"""Tests for TemplateModel base class."""

from __future__ import annotations

import tempfile
from pathlib import Path
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


def test_write_to_file(tmp_path):
    class FileTemplate(TemplateModel):
        __template__ = "Content: {{ value }}"
        value: str

    template = FileTemplate(value="test")
    output_path = tmp_path / "output.txt"
    template.write_to(output_path)

    assert output_path.exists()
    assert output_path.read_text() == "Content: test"


def test_write_to_creates_directories(tmp_path):
    class DirTemplate(TemplateModel):
        __template__ = "{{ text }}"
        text: str

    template = DirTemplate(text="hello")
    output_path = tmp_path / "nested" / "dir" / "file.txt"
    template.write_to(output_path)

    assert output_path.exists()
    assert output_path.read_text() == "hello"


def test_write_to_overwrites_existing(tmp_path):
    class OverwriteTemplate(TemplateModel):
        __template__ = "{{ content }}"
        content: str

    output_path = tmp_path / "file.txt"
    output_path.write_text("old content")

    template = OverwriteTemplate(content="new content")
    template.write_to(output_path)

    assert output_path.read_text() == "new content"


def test_write_to_accepts_string_path(tmp_path):
    class StringPathTemplate(TemplateModel):
        __template__ = "{{ val }}"
        val: str

    template = StringPathTemplate(val="test")
    output_path = str(tmp_path / "file.txt")
    template.write_to(output_path)

    assert Path(output_path).exists()


def test_str_returns_rendered():
    """Test that __str__ returns rendered template."""

    class StrTemplate(TemplateModel):
        __template__ = "Value: {{ x }}"
        x: int

    template = StrTemplate(x=99)
    assert str(template) == "Value: 99"


def test_nested_template_auto_renders():
    """Test that nested templates auto-render via __str__."""

    class InnerTemplate(TemplateModel):
        __template__ = "Inner: {{ value }}"
        value: str

    class OuterTemplate(TemplateModel):
        __template__ = "Outer: {{ inner }}"
        inner: InnerTemplate

    inner = InnerTemplate(value="test")
    outer = OuterTemplate(inner=inner)

    result = outer.render()
    assert result == "Outer: Inner: test"


def test_nested_with_indent_filter():
    """Test nested templates work with Jinja2 indent filter."""

    class BlockTemplate(TemplateModel):
        __template__ = "def foo():\n    {{ content }}"
        content: str

    class NestedBlockTemplate(TemplateModel):
        __template__ = "{{ block|indent(4, true) }}"
        block: BlockTemplate

    inner = BlockTemplate(content="return 42")
    outer = NestedBlockTemplate(block=inner)

    result = outer.render()
    assert "def foo():" in result
    assert "return 42" in result


def test_deeply_nested_templates():
    """Test multiple levels of nested templates."""

    class Level1(TemplateModel):
        __template__ = "L1: {{ val }}"
        val: str

    class Level2(TemplateModel):
        __template__ = "L2: {{ inner }}"
        inner: Level1

    class Level3(TemplateModel):
        __template__ = "L3: {{ middle }}"
        middle: Level2

    l1 = Level1(val="deep")
    l2 = Level2(inner=l1)
    l3 = Level3(middle=l2)

    result = l3.render()
    assert result == "L3: L2: L1: deep"
