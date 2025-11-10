# src/tests/test_integration.py
"""Integration tests for complete workflows."""

from __future__ import annotations

from pathlib import Path
from templateer import TemplateModel, discover_templates


def test_end_to_end_workflow(tmp_path):
    """Test complete workflow: create template, discover, render, write."""

    # Create .templateer directory with templates
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()

    (template_dir / "function.py").write_text("""
from templateer import TemplateModel

TEMPLATE = '''
def {{ func_name }}():
    {{ body|indent(4, true) }}
'''

class FunctionTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    body: str = "pass"


""")

    # Discover templates
    templates = discover_templates(template_dir)

    # Create instance
    template = templates.FunctionTemplate(func_name="hello", body="return 'world'")

    # Render
    code = template.render()
    assert "def hello():" in code
    assert "return 'world'" in code

    # Write to file
    output = tmp_path / "output.py"
    template.write_to(output)
    assert output.exists()
    assert "def hello():" in output.read_text()


def test_nested_template_composition(tmp_path):
    """Test composing templates from other templates."""

    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()

    # Create docstring template
    (template_dir / "docstring.py").write_text("""
from templateer import TemplateModel


TEMPLATE = '''
\"\"\"{{ summary }}
{% if returns %}

Returns:
    {{ returns }}
{% endif %}
\"\"\"
'''


class DocstringTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    summary: str
    returns: str | None = None

""")

    # Create function template that uses docstring
    (template_dir / "documented_function.py").write_text("""
from templateer import TemplateModel
from .docstring import DocstringTemplate


TEMPLATE = '''
def {{ func_name }}():
    {{ docstring|indent(4, true) }}
    {{ body|indent(4, true) }}
'''


class DocumentedFunctionTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    docstring: DocstringTemplate
    body: str = "pass"

""")

    # Discover and use
    templates = discover_templates(template_dir)

    doc = templates.DocstringTemplate(summary="A helpful function", returns="str: A greeting")

    func = templates.DocumentedFunctionTemplate(func_name="greet", docstring=doc, body="return 'Hello!'")

    result = func.render()
    assert "def greet():" in result
    assert "A helpful function" in result
    assert "Returns:" in result
    assert "return 'Hello!'" in result


def test_realistic_class_generation(tmp_path):
    """Test generating a realistic Python class."""

    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()

    (template_dir / "dataclass.py").write_text("""
from templateer import TemplateModel


TEMPLATE = '''
from dataclasses import dataclass

@dataclass
class {{ class_name }}:
    {% for name, field_type in fields.items() -%}
    {{ name }}: {{ field_type }}
    {% endfor %}
    {% for method in methods %}

    {{ method|indent(4, true) }}
    {% endfor -%}
'''


class DataclassTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    class_name: str
    fields: dict[str, str]  # name -> type
    methods: list[str] = []

""")

    templates = discover_templates(template_dir)

    template = templates.DataclassTemplate(
        class_name="Person",
        fields={"name": "str", "age": "int"},
        methods=["def greet(self) -> str:\n    return f'Hi, I am {self.name}'"],
    )

    output = tmp_path / "person.py"
    template.write_to(output)

    code = output.read_text()
    assert "@dataclass" in code
    assert "class Person:" in code
    assert "name: str" in code
    assert "age: int" in code
    assert "def greet(self)" in code
