# DEV.md
# Templateer Development Guide

## Prerequisites

- Python 3.10+
- uv for dependency management
- pytest for testing

## Step 1: Project Setup

### Development Tasks

1. Create project structure:
```
src/templateer/
├── __init__.py
├── model.py
└── py.typed
src/src/tests/
├── __init__.py
└── test_model.py
pyproject.toml
```

2. Configure `pyproject.toml`:
```toml
[project]
name = "templateer"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
    "jinja2>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

3. Create `src/templateer/__init__.py`:
```python
"""Templateer: Type-safe Jinja2 templates via Pydantic models."""

from .model import TemplateModel

__all__ = ["TemplateModel"]
```

4. Install dependencies:
```bash
uv sync
```

### Testing Tasks

1. Verify project structure exists
2. Run `uv sync` successfully
3. Verify imports work:
```python
import templateer
assert hasattr(templateer, 'TemplateModel')
```

### Success Criteria

- All files created
- Dependencies installed
- Package importable

---

## Step 2: TemplateModel Base Class with render()

### Development Tasks

Create `src/templateer/model.py`:

```python
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
        if not hasattr(self.__class__, '__template__'):
            raise AttributeError(
                f"{self.__class__.__name__} must define __template__ class variable"
            )
        
        env = jinja2.Environment()
        template = env.from_string(self.__class__.__template__)
        return template.render(**self.model_dump())
```

### Testing Tasks

Create `src/tests/test_model.py`:

```python
# src/tests/test_model.py
"""Tests for TemplateModel base class."""

from __future__ import annotations

import pytest
from templateer import TemplateModel


def test_simple_render():
    """Test basic template rendering."""
    
    class SimpleTemplate(TemplateModel):
        __template__ = TEMPLATE
        name: str
        value: int
    
    TEMPLATE = "Hello {{ name }}, value is {{ value }}"
    
    template = SimpleTemplate(name="World", value=42)
    result = template.render()
    assert result == "Hello World, value is 42"


def test_render_with_defaults():
    """Test rendering with default values."""
    
    class DefaultTemplate(TemplateModel):
        __template__ = TEMPLATE
        greeting: str = "Hi"
        name: str = "there"
    
    TEMPLATE = "{{ greeting }} {{ name }}"
    
    template = DefaultTemplate()
    assert template.render() == "Hi there"
    
    template = DefaultTemplate(greeting="Hello", name="World")
    assert template.render() == "Hello World"


def test_render_with_jinja_filters():
    """Test that Jinja2 filters work."""
    
    class FilterTemplate(TemplateModel):
        __template__ = TEMPLATE
        text: str
    
    TEMPLATE = "{{ text|upper }}"
    
    template = FilterTemplate(text="hello")
    assert template.render() == "HELLO"


def test_render_with_conditionals():
    """Test Jinja2 conditional logic."""
    
    class ConditionalTemplate(TemplateModel):
        __template__ = TEMPLATE
        show: bool
        value: str
    
    TEMPLATE = """
{% if show -%}
Value: {{ value }}
{% else -%}
Hidden
{% endif -%}
"""
    
    template = ConditionalTemplate(show=True, value="test")
    assert "Value: test" in template.render()
    
    template = ConditionalTemplate(show=False, value="test")
    assert "Hidden" in template.render()


def test_render_with_loops():
    """Test Jinja2 loop constructs."""
    
    class LoopTemplate(TemplateModel):
        __template__ = TEMPLATE
        items: list[str]
    
    TEMPLATE = """
{% for item in items -%}
- {{ item }}
{% endfor -%}
"""
    
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
```

Run tests:
```bash
uv run pytest src/tests/test_model.py -v
```

### Success Criteria

- All tests pass
- `render()` correctly renders templates
- Jinja2 features (filters, conditionals, loops) work
- Pydantic validation enforced
- Clear error messages

---

## Step 3: Add write_to() Method

### Development Tasks

Add to `src/templateer/model.py`:

```python
from pathlib import Path

class TemplateModel(BaseModel):
    # ... existing code ...
    
    def write_to(self, path: str | Path) -> None:
        """Render template and write to file.
        
        Creates parent directories if they don't exist.
        
        Args:
            path: File path to write to.
            
        Raises:
            PermissionError: If cannot write to path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render())
```

### Testing Tasks

Add to `src/tests/test_model.py`:

```python
import tempfile
from pathlib import Path


def test_write_to_file(tmp_path):
    """Test writing template to file."""
    
    class FileTemplate(TemplateModel):
        __template__ = "Content: {{ value }}"
        value: str
    
    template = FileTemplate(value="test")
    output_path = tmp_path / "output.txt"
    
    template.write_to(output_path)
    
    assert output_path.exists()
    assert output_path.read_text() == "Content: test"


def test_write_to_creates_directories(tmp_path):
    """Test that write_to creates parent directories."""
    
    class DirTemplate(TemplateModel):
        __template__ = "{{ text }}"
        text: str
    
    template = DirTemplate(text="hello")
    output_path = tmp_path / "nested" / "dir" / "file.txt"
    
    template.write_to(output_path)
    
    assert output_path.exists()
    assert output_path.read_text() == "hello"


def test_write_to_overwrites_existing(tmp_path):
    """Test that write_to overwrites existing files."""
    
    class OverwriteTemplate(TemplateModel):
        __template__ = "{{ content }}"
        content: str
    
    output_path = tmp_path / "file.txt"
    output_path.write_text("old content")
    
    template = OverwriteTemplate(content="new content")
    template.write_to(output_path)
    
    assert output_path.read_text() == "new content"


def test_write_to_accepts_string_path(tmp_path):
    """Test that write_to accepts string paths."""
    
    class StringPathTemplate(TemplateModel):
        __template__ = "{{ val }}"
        val: str
    
    template = StringPathTemplate(val="test")
    output_path = str(tmp_path / "file.txt")
    
    template.write_to(output_path)
    
    assert Path(output_path).exists()
```

Run tests:
```bash
uv run pytest src/tests/test_model.py -v
```

### Success Criteria

- All tests pass
- Files written correctly
- Parent directories created automatically
- Existing files overwritten
- Both string and Path objects work

---

## Step 4: Add __str__() for Auto-Rendering

### Development Tasks

Add to `src/templateer/model.py`:

```python
class TemplateModel(BaseModel):
    # ... existing code ...
    
    def __str__(self) -> str:
        """Return rendered template.
        
        Enables automatic rendering when template is used in Jinja2
        or converted to string.
        
        Returns:
            Rendered template string.
        """
        return self.render()
```

### Testing Tasks

Add to `src/tests/test_model.py`:

```python
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
```

Run tests:
```bash
uv run pytest src/tests/test_model.py -v
```

### Success Criteria

- All tests pass
- `str(template)` returns rendered output
- Nested templates auto-render
- Indent filter works with nested templates
- Multiple nesting levels work

---

## Step 5: Template Discovery

### Development Tasks

Create `src/templateer/discovery.py`:

```python
# src/templateer/discovery.py
"""Template discovery utilities."""

from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from typing import Type

from .model import TemplateModel


def discover_templates(directory: str | Path = ".templateer") -> SimpleNamespace:
    """Discover all TemplateModel subclasses in a directory.
    
    Args:
        directory: Directory to scan for template files.
        
    Returns:
        SimpleNamespace with template classes as attributes.
        
    Example:
        templates = discover_templates()
        my_template = templates.MyTemplate(field="value")
    """
    directory = Path(directory)
    
    if not directory.exists():
        return SimpleNamespace()
    
    templates: dict[str, Type[TemplateModel]] = {}
    original_path = sys.path.copy()
    
    try:
        # Add directory to path for imports
        sys.path.insert(0, str(directory.parent))
        
        # Find all .py files
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            # Calculate module name
            relative = py_file.relative_to(directory.parent)
            module_name = str(relative.with_suffix("")).replace("/", ".")
            
            try:
                # Import module
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find TemplateModel subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, TemplateModel) and 
                            attr is not TemplateModel):
                            templates[attr.__name__] = attr
            except Exception:
                # Skip files that fail to import
                continue
    finally:
        # Restore original path
        sys.path = original_path
    
    return SimpleNamespace(**templates)
```

Update `src/templateer/__init__.py`:

```python
"""Templateer: Type-safe Jinja2 templates via Pydantic models."""

from .model import TemplateModel
from .discovery import discover_templates

__all__ = ["TemplateModel", "discover_templates"]
```

### Testing Tasks

Create `src/tests/test_discovery.py`:

```python
# src/tests/test_discovery.py
"""Tests for template discovery."""

from __future__ import annotations

from pathlib import Path
import pytest
from templateer import TemplateModel, discover_templates


def test_discover_empty_directory(tmp_path):
    """Test discovery with no templates."""
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()
    
    templates = discover_templates(template_dir)
    assert not hasattr(templates, 'anything')


def test_discover_single_template(tmp_path):
    """Test discovering a single template."""
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()
    
    # Create template file
    template_file = template_dir / "simple.py"
    template_file.write_text("""
from templateer import TemplateModel

class SimpleTemplate(TemplateModel):
    __template__ = TEMPLATE
    value: str

TEMPLATE = "Value: {{ value }}"
""")
    
    templates = discover_templates(template_dir)
    assert hasattr(templates, 'SimpleTemplate')
    
    # Test using the template
    instance = templates.SimpleTemplate(value="test")
    assert instance.render() == "Value: test"


def test_discover_multiple_templates(tmp_path):
    """Test discovering multiple templates."""
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()
    
    # Create first template
    (template_dir / "first.py").write_text("""
from templateer import TemplateModel

class FirstTemplate(TemplateModel):
    __template__ = "First: {{ x }}"
    x: int
""")
    
    # Create second template
    (template_dir / "second.py").write_text("""
from templateer import TemplateModel

class SecondTemplate(TemplateModel):
    __template__ = "Second: {{ y }}"
    y: str
""")
    
    templates = discover_templates(template_dir)
    assert hasattr(templates, 'FirstTemplate')
    assert hasattr(templates, 'SecondTemplate')


def test_discover_skips_private_files(tmp_path):
    """Test that files starting with _ are skipped."""
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()
    
    # Create __init__.py
    (template_dir / "__init__.py").write_text("")
    
    # Create _private.py
    (template_dir / "_private.py").write_text("""
from templateer import TemplateModel

class PrivateTemplate(TemplateModel):
    __template__ = "{{ x }}"
    x: str
""")
    
    templates = discover_templates(template_dir)
    assert not hasattr(templates, 'PrivateTemplate')


def test_discover_nested_directories(tmp_path):
    """Test discovery in nested directories."""
    template_dir = tmp_path / ".templateer"
    nested_dir = template_dir / "nested"
    nested_dir.mkdir(parents=True)
    
    (nested_dir / "deep.py").write_text("""
from templateer import TemplateModel

class DeepTemplate(TemplateModel):
    __template__ = "Deep: {{ z }}"
    z: str
""")
    
    templates = discover_templates(template_dir)
    assert hasattr(templates, 'DeepTemplate')


def test_discover_nonexistent_directory(tmp_path):
    """Test discovery when directory doesn't exist."""
    template_dir = tmp_path / "nonexistent"
    
    templates = discover_templates(template_dir)
    assert not hasattr(templates, 'anything')


def test_discover_handles_import_errors(tmp_path):
    """Test that discovery continues when a file has errors."""
    template_dir = tmp_path / ".templateer"
    template_dir.mkdir()
    
    # Create file with syntax error
    (template_dir / "broken.py").write_text("""
from templateer import TemplateModel

class BrokenTemplate(TemplateModel):
    this is not valid python
""")
    
    # Create valid file
    (template_dir / "valid.py").write_text("""
from templateer import TemplateModel

class ValidTemplate(TemplateModel):
    __template__ = "{{ x }}"
    x: str
""")
    
    templates = discover_templates(template_dir)
    assert hasattr(templates, 'ValidTemplate')
    assert not hasattr(templates, 'BrokenTemplate')
```

Run tests:
```bash
uv run pytest src/tests/test_discovery.py -v
```

### Success Criteria

- All tests pass
- Templates discovered from directory
- Multiple templates work
- Nested directories supported
- Private files (_*.py) skipped
- Import errors handled gracefully
- Returns empty namespace if directory missing

---

## Step 6: Integration Testing

### Development Tasks

No new code - validate everything works together.

### Testing Tasks

Create `src/tests/test_integration.py`:

```python
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

class FunctionTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    body: str = "pass"


TEMPLATE = '''
def {{ func_name }}():
    {{ body|indent(4, true) }}
'''
""")
    
    # Discover templates
    templates = discover_templates(template_dir)
    
    # Create instance
    template = templates.FunctionTemplate(
        func_name="hello",
        body="return 'world'"
    )
    
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

class DocstringTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    summary: str
    returns: str | None = None


TEMPLATE = '''
\"\"\"{{ summary }}
{% if returns %}

Returns:
    {{ returns }}
{% endif %}
\"\"\"
'''
""")
    
    # Create function template that uses docstring
    (template_dir / "documented_function.py").write_text("""
from templateer import TemplateModel
from .docstring import DocstringTemplate

class DocumentedFunctionTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    docstring: DocstringTemplate
    body: str = "pass"


TEMPLATE = '''
def {{ func_name }}():
    {{ docstring|indent(4, true) }}
    {{ body|indent(4, true) }}
'''
""")
    
    # Discover and use
    templates = discover_templates(template_dir)
    
    doc = templates.DocstringTemplate(
        summary="A helpful function",
        returns="str: A greeting"
    )
    
    func = templates.DocumentedFunctionTemplate(
        func_name="greet",
        docstring=doc,
        body="return 'Hello!'"
    )
    
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

class DataclassTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    class_name: str
    fields: dict[str, str]  # name -> type
    methods: list[str] = []


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
""")
    
    templates = discover_templates(template_dir)
    
    template = templates.DataclassTemplate(
        class_name="Person",
        fields={"name": "str", "age": "int"},
        methods=[
            "def greet(self) -> str:\n    return f'Hi, I am {self.name}'"
        ]
    )
    
    output = tmp_path / "person.py"
    template.write_to(output)
    
    code = output.read_text()
    assert "@dataclass" in code
    assert "class Person:" in code
    assert "name: str" in code
    assert "age: int" in code
    assert "def greet(self)" in code
```

Run all tests:
```bash
uv run pytest src/tests/ -v --cov=src/templateer --cov-report=term-missing
```

### Success Criteria

- All integration tests pass
- End-to-end workflows work
- Nested template composition works
- Realistic code generation successful
- Code coverage >90%

---

## Step 7: Documentation and Examples

### Development Tasks

1. Create `examples/.templateer/` directory with sample templates
2. Create `examples/generate.py` showing usage
3. Verify README examples work
4. Add docstrings to all public functions/classes

### Testing Tasks

1. Run example code manually
2. Verify all README code snippets work
3. Check docstrings present on all public APIs

### Success Criteria

- Examples run without errors
- README accurate
- Public APIs documented

---

## Final Checklist

Before considering the library complete:

- [ ] All tests pass
- [ ] Code coverage >90%
- [ ] README accurate
- [ ] SPEC.md matches implementation
- [ ] Examples work
- [ ] Type hints on all public APIs
- [ ] Docstrings on all public APIs
- [ ] No TODO comments in code
- [ ] `py.typed` file present

## Running Full Test Suite

```bash
# Run all tests with coverage
uv run pytest src/tests/ -v --cov=src/templateer --cov-report=html

# Type check
uv run mypy src/

# Format check
uv run ruff check src/ src/tests/
```
