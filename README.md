# README.md
# Templateer

A minimal Python library for managing Jinja2 templates as Pydantic models.

## Installation

```bash
uv add templateer
```

## Quick Start

**1. Create a template in `.templateer/my_function.py`:**

```python
from __future__ import annotations
from templateer import TemplateModel

class MyFunctionTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    params: str = ""
    return_type: str = "None"
    docstring: str | None = None
    body: str = "pass"


TEMPLATE = """
def {{ func_name }}({{ params }}) -> {{ return_type }}:
    {% if docstring -%}
    \"\"\"{{ docstring }}\"\"\"
    {% endif -%}
    {{ body|indent(4, true) }}
"""
```

**2. Use it in your code:**

```python
from templateer import discover_templates

# Auto-discover all templates in .templateer/
templates = discover_templates()

# Render to string
template = templates.MyFunctionTemplate(
    func_name="greet",
    params="name: str",
    return_type="str",
    body='return f"Hello, {name}!"'
)
code = template.render()

# Or write directly to file
template.write_to("src/greet.py")
```

## How It Works

1. **Create templates** as Pydantic models in `.templateer/` directory
2. **Inherit from `TemplateModel`** to get rendering capabilities
3. **Define `__template__`** as a Jinja2 template string
4. **Use Pydantic fields** to define template variables
5. **Call `.render()`** for string output or `.write_to(path)` to write files

## Creating Templates

Templates are Python classes that combine:
- **Pydantic validation** for template data
- **Jinja2 rendering** for code generation
- **Type safety** via Python type hints

### Template Structure

```python
from __future__ import annotations
from templateer import TemplateModel

class YourTemplate(TemplateModel):
    __template__ = """
    {{ your_jinja2_template_here }}
    """
    
    # Define your fields with types and defaults
    field_name: str
    optional_field: int = 42
```

### Template Variables

All Pydantic fields become Jinja2 template variables:

```python
class ConfigTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    app_name: str
    debug: bool = False


TEMPLATE = """
APP_NAME = "{{ app_name }}"
DEBUG = {{ debug }}
"""
```

## API Reference

### `TemplateModel`

Base class for all templates. Provides:

**`.render() -> str`**
- Renders the template to a string
- Uses Pydantic field values as Jinja2 context

**`.write_to(path: str | Path) -> None`**
- Renders template and writes to file
- Creates parent directories if needed
- Overwrites existing files

### `discover_templates(directory: str | Path = ".templateer") -> object`

- Scans directory for Python files
- Imports all `TemplateModel` subclasses
- Returns namespace object with templates as attributes
- Template class names become attribute names

## Project Structure

```
your-project/
├── .templateer/
│   ├── function_template.py
│   ├── class_template.py
│   └── cli_template.py
├── src/
│   └── # your generated code here
└── generate.py  # your generation script
```

## Requirements

- Python 3.10+
- Pydantic 2.x
- Jinja2

## Template Composition

Templates can be nested as Pydantic fields. Nested templates auto-render when used in Jinja2:

**`.templateer/docstring.py`:**
```python
from __future__ import annotations
from templateer import TemplateModel

class DocstringTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    summary: str
    params: list[str] = []


TEMPLATE = """
\"\"\"{{ summary }}
{% if params %}

Args:
{% for param in params %}
    {{ param }}
{% endfor %}
{% endif %}
\"\"\"
"""
```

**`.templateer/function_with_docs.py`:**
```python
from __future__ import annotations
from templateer import TemplateModel
from .docstring import DocstringTemplate

class FunctionWithDocsTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    func_name: str
    docstring: DocstringTemplate
    body: str = "pass"


TEMPLATE = """
def {{ func_name }}():
    {{ docstring|indent(4, true) }}
    {{ body|indent(4, true) }}
"""
```

**Usage:**
```python
template = FunctionWithDocsTemplate(
    func_name="greet",
    docstring=DocstringTemplate(
        summary="Greet someone",
        params=["name: Person to greet"]
    ),
    body="print('Hello!')"
)
code = template.render()
```

Nested `TemplateModel` instances automatically render when referenced in templates - no need to call `.render()` explicitly.

## Design Principles

- **Simple**: Just Pydantic + Jinja2, nothing more
- **Type-safe**: Full editor support and validation
- **Discoverable**: Auto-find templates without imports
- **Minimal**: No magic, no complex abstractions
- **Composable**: Nest templates as Pydantic fields
- **Fast**: Render templates in milliseconds

## Limitations

- 1:1 template to output file mapping (one template class per output)
- No reverse parsing (generated files → Pydantic models)

## License

MIT
