# Templateer

A self-generating Pydantic ⇄ Jinja toolkit for code generation.

## Installation

```bash
uv add templateer
```

## Quick Start

1. Create template directory:
   ```bash
   mkdir .templateer
   ```

2. Add a template module (e.g., `.templateer/hello.py`):
   ```python
   TEMPLATE = """
   def {{ func_name }}():
       return "{{ message }}"
   """
   ```

3. Generate model stubs:
   ```bash
   templateer autogen
   ```

4. Use the generated model:
   ```python
   from templateer.models.hello_model import HelloTemplate
   
   template = HelloTemplate(
       func_name="greet", 
       message="Hello, World!"
   )
   code = template.generate()
   ```

## Commands

- `templateer autogen` - Generate Pydantic model stubs
- `templateer generate` - Generate stubs and render all templates

## Configuration

Set via environment variables or `.env`:

- `MODEL_DIR` - Model stub directory (default: `templateer/models`)
- `TEMPLATE_OUTPUT_DIR` - Generated code directory (default: `TEMPLATE_DIR`)

## Development

```bash
uv sync --dev
uv run pytest
```
