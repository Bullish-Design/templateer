# Templateer

**A self-generating Pydantic ⇄ Jinja toolkit for typed template development**

Templateer bridges the gap between dynamic template generation and static type safety by automatically creating Pydantic model stubs from Jinja templates, enabling type-safe template rendering with full IDE support.

## Core Concept

Traditional template systems require manual synchronization between template variables and data models. Templateer eliminates this friction through **template introspection**: it analyzes your Jinja templates, extracts required variables, and auto-generates corresponding Pydantic models that provide type safety and validation.

### The Self-Generating Workflow

1. **Write templates** in `.templateer/` with embedded `TEMPLATE` constants
2. **Auto-generate models** via template introspection (`--autogen`)
3. **Use typed models** to render templates with full IDE support
4. **Round-trip validation** ensures template-model consistency

## Key Features

- **Zero boilerplate**: Models auto-generate from template analysis
- **Type safety**: Full Pydantic validation and IDE completion
- **Configuration-driven**: Paths managed via Confidantic settings
- **Template discovery**: Automatic detection of template modules
- **Round-trip testing**: Syntax and import validation
- **CLI integration**: Command-line tools for generation and rendering

## Installation

```bash
uv add templateer jinja2 pydantic confidantic
```

## Quick Start

### 1. Create a Template Module

```python
# .templateer/greeting_template.py
from templateer import TemplateModel

class GreetingTemplate(TemplateModel):
    __template__ = "greeting_template.TEMPLATE"
    
    name: str
    greeting: str = "Hello"

TEMPLATE = """
{{ greeting }}, {{ name }}!
Welcome to the typed template system.
"""
```

### 2. Generate and Use

```bash
# Auto-generate Pydantic model stubs
python -m templateer --autogen

# Use the generated model
from templateer.models.greeting_model import GreetingTemplate

template = GreetingTemplate(name="Alice", greeting="Hi")
output = template.generate()  # Renders and writes to file
print(template.render())      # Just returns the string
```

## Directory Structure

```
project/
├── .templateer/              # Template modules
│   ├── __init__.py
│   ├── greeting_template.py  
│   └── class_template.py
├── templateer/
│   └── models/               # Auto-generated model stubs
│       ├── __init__.py
│       ├── greeting_model.py
│       └── class_model.py
├── TEMPLATE_DIR/             # Rendered output (configurable)
│   ├── greeting.py
│   └── class.py
└── .env                      # Optional configuration
```

## Configuration

Templateer uses Confidantic for type-safe configuration management:

```python
class TemplateerSettings(Settings):
    model_dir: Path = Field(
        default_factory=lambda: Path("templateer") / "models",
        alias="MODEL_DIR"
    )
    template_output_dir: Path = Field(
        default_factory=lambda: Path("TEMPLATE_DIR"), 
        alias="TEMPLATE_OUTPUT_DIR"
    )
```

Override via environment variables or `.env`:

```bash
# .env
MODEL_DIR=src/generated/models
TEMPLATE_OUTPUT_DIR=output/rendered
```

## Template Development

### Basic Template Structure

```python
# .templateer/my_template.py
from templateer import TemplateModel

class MyTemplate(TemplateModel):
    __template__ = "my_template.TEMPLATE"
    __output__ = "custom_filename.py"  # Optional override
    
    # Define your data fields
    variable_name: str
    optional_field: str | None = None

TEMPLATE = """
# Your Jinja template here
{{ variable_name }}
{% if optional_field %}
Optional: {{ optional_field }}
{% endif %}
"""
```

### Template Variable Discovery

Templateer uses Jinja's AST parser to automatically detect template variables:

```python
# Template with variables: name, items, show_header
TEMPLATE = """
{% if show_header %}
# {{ name }}
{% endif %}

{% for item in items %}
- {{ item }}
{% endfor %}
"""
```

Auto-generated model stub:
```python
class MyTemplate(TemplateModel):
    __template__ = "my_template.TEMPLATE"
    
    items: Any | None = None
    name: Any | None = None
    show_header: Any | None = None
```

### Complex Template Example

```python
# .templateer/python_class_template.py
class PythonClassTemplate(TemplateModel):
    __template__ = "python_class_template.TEMPLATE"
    
    class_name: str = "MyClass"
    attributes: dict[str, str] = {}
    methods: list[str] = []
    base_classes: list[str] = []

TEMPLATE = """
class {{ class_name }}{% if base_classes %}({{ base_classes|join(', ') }}){% endif %}:
    {% if not attributes and not methods -%}
    pass
    {% endif %}
    
    {% for name, default in attributes.items() -%}
    {{ name }}: Any = {{ default }}
    {% endfor %}
    
    {% for method in methods %}
    {{ method|indent(4, true) }}
    {% endfor %}
"""
```

## API Reference

### TemplateModel

Base class for all template models:

```python
class TemplateModel(BaseModel):
    __template__: str           # Required: module.TEMPLATE path
    __output__: str | None      # Optional: custom output filename
    
    def render(self) -> str:    # Render template to string
    def generate(self, write: bool = True) -> str:  # Render and optionally write
```

### Core Functions

```python
def autogen_models(verbose: bool = False) -> list[Path]:
    """Generate Pydantic stubs for all templates"""

def _discover_template_modules() -> Iterable[Path]:
    """Find all .py files in .templateer/"""

def _extract_template_vars(template_str: str) -> set[str]:
    """Extract variables from Jinja template"""
```

## Command Line Interface

```bash
# Generate model stubs only
python -m templateer --autogen

# Generate stubs and render all templates
python -m templateer --generate

# Show help
python -m templateer --help
```

## Testing

Templateer includes comprehensive round-trip testing:

```python
def test_generated_syntax():
    """Verify all generated files have valid Python syntax"""

def test_generated_imports(): 
    """Ensure all generated files can be imported"""
```

Run tests with pytest:
```bash
pytest templateer_mvp.py
```

## Advanced Usage

### Custom Jinja Environment

The library uses a pre-configured Jinja environment:

```python
ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_ROOT)),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)
```

### Template Inheritance

Templates can reference other templates:

```python
TEMPLATE = """
{% extends "base_template.j2" %}
{% block content %}
{{ custom_content }}
{% endblock %}
"""
```

### Dynamic Model Loading

```python
import importlib
import sys

# Add model directory to path
sys.path.insert(0, str(settings.model_dir))

# Dynamically load generated models
for stub in settings.model_dir.glob("*_model.py"):
    module_name = f"templateer.models.{stub.stem}"
    mod = importlib.import_module(module_name)
    template_class = next(
        cls for cls in mod.__dict__.values()
        if isinstance(cls, type) 
        and issubclass(cls, TemplateModel)
        and cls is not TemplateModel
    )
```

## Best Practices

1. **Keep templates focused**: One template per logical unit
2. **Use meaningful names**: Template files should reflect their purpose  
3. **Validate early**: Run `--autogen` frequently during development
4. **Version control models**: Include generated stubs in git for stability
5. **Test round-trips**: Use built-in testing for syntax validation

## Troubleshooting

### Common Issues

**Template variables not detected**: Ensure variables are used directly in Jinja expressions, not in nested contexts that the AST parser can't reach.

**Import errors**: Check that `.templateer` and model directories are in your Python path.

**Missing TEMPLATE constant**: Every template module must define a `TEMPLATE` string constant.

### Debug Mode

Enable verbose output:
```python
autogen_models(verbose=True)
```

## Contributing

The library is designed as a single-file MVP with minimal dependencies. Key extension points:

- Custom template loaders
- Alternative model generators  
- Additional CLI commands
- Extended configuration options

## License

[Add your license here]

---

**Templateer**: Where type safety meets template flexibility.