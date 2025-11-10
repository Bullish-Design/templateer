# SPEC.md
# Templateer Library Specification

## Overview

Templateer is a minimal Python library that combines Pydantic models with Jinja2 templates to enable type-safe code generation.

## Core Components

### 1. TemplateModel (Base Class)

**Location:** `src/templateer/model.py`

```python
class TemplateModel(BaseModel):
    __template__: ClassVar[str]
    
    def render() -> str
    def write_to(path: str | Path) -> None
    def __str__() -> str
```

**Responsibilities:**
- Serve as base class for all user templates
- Render Jinja2 templates using Pydantic field values
- Enable auto-rendering via `__str__()` for nested templates
- Write rendered output to files

**Implementation Details:**
- `__template__` is a class variable, not an instance field
- `render()` uses `model_dump()` to get field values as dict
- `__str__()` calls `render()` to enable Jinja2 auto-conversion
- `write_to()` creates parent directories if needed
- Jinja2 environment uses default settings (no custom filters/extensions initially)

### 2. Template Discovery

**Location:** `src/templateer/discovery.py`

```python
def discover_templates(directory: str | Path = ".templateer") -> SimpleNamespace
```

**Responsibilities:**
- Scan directory for `.py` files
- Import modules and find `TemplateModel` subclasses
- Return namespace object with templates as attributes

**Implementation Details:**
- Use `importlib` for dynamic imports
- Handle relative imports within `.templateer/` directory
- Template class names become attribute names (e.g., `templates.MyTemplate`)
- Skip files starting with `_` (e.g., `__init__.py`)
- Return empty namespace if directory doesn't exist
- Log warnings for import errors but don't fail

**Algorithm:**
1. Add `.templateer/` to `sys.path` temporarily
2. Discover all `.py` files recursively
3. Import each module
4. Inspect for `TemplateModel` subclasses
5. Add to namespace using class name as key
6. Remove from `sys.path`

### 3. Package Structure

```
src/templateer/
├── __init__.py          # Exports: TemplateModel, discover_templates
├── model.py             # TemplateModel base class
└── discovery.py         # Template discovery logic
```

## Dependencies

- **Python:** 3.10+ (for `type | type` union syntax)
- **Pydantic:** 2.x (for BaseModel)
- **Jinja2:** 3.x (for template rendering)

## User Template Structure

Templates live in `.templateer/` at project root:

```
project/
├── .templateer/
│   ├── my_template.py
│   ├── another_template.py
│   └── nested/
│       └── deep_template.py
└── src/
```

**Template file format:**
```python
from __future__ import annotations
from templateer import TemplateModel

class MyTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    field1: str
    field2: int = 42


TEMPLATE = """
# Template content here
{{ field1 }}
{{ field2 }}
"""
```

## Template Composition

Templates can nest other templates as Pydantic fields:

```python
from .other_template import OtherTemplate

class ComposedTemplate(TemplateModel):
    __template__ = TEMPLATE
    
    nested: OtherTemplate
    value: str


TEMPLATE = """
{{ nested }}  # Auto-renders via __str__()
{{ value }}
"""
```

**Key behavior:** When Jinja2 encounters a `TemplateModel` instance, it calls `__str__()`, which calls `render()`, creating a cascading render chain.

## Rendering Process

1. User creates template instance: `t = MyTemplate(field1="hello")`
2. User calls `t.render()` or `t.write_to(path)`
3. `render()` calls `model_dump()` to get field values
4. Any nested `TemplateModel` fields remain as objects
5. Jinja2 template renders, calling `__str__()` on nested models
6. Nested models recursively render
7. Final string returned/written

## Edge Cases

### Empty .templateer/ directory
- `discover_templates()` returns empty namespace
- No error raised

### Invalid template syntax
- Jinja2 raises `TemplateSyntaxError` at render time
- Not validated at discovery time

### Circular dependencies
- Python import system prevents circular imports
- If circular reference occurs at runtime, Python's recursion limit applies

### Missing __template__
- Template class works but `render()` raises `AttributeError`
- Could add validation in `TemplateModel.__init_subclass__()` to fail early

### File permissions
- `write_to()` raises `PermissionError` if cannot write
- User handles exception

### Name collisions
- If multiple templates have same class name, last one wins
- Discovery order is filesystem-dependent
- Consider warning on collision (future enhancement)

## Testing Strategy

1. **Unit tests:**
   - `TemplateModel.render()` with various field types
   - `TemplateModel.__str__()` returns same as `render()`
   - `TemplateModel.write_to()` creates files correctly
   
2. **Integration tests:**
   - `discover_templates()` finds all templates
   - Nested template composition works
   - Template imports work correctly

3. **Edge case tests:**
   - Empty directory handling
   - Invalid Jinja2 syntax
   - Missing `__template__` attribute
   - File write errors

## Future Enhancements (Out of Scope v1)

- Custom Jinja2 filters/extensions
- Reverse parsing (files → Pydantic models)
- Multiple output files per template
- Template validation at discovery time
- Automatic template reloading in dev mode
- CLI tool for template scaffolding

## Non-Goals

- Build system integration
- Version control of generated files
- Diff/merge of template outputs
- IDE plugins or language servers
- Template marketplace/registry
