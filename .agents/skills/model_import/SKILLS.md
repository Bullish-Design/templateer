# SKILLS.md — Importing Pydantic models from `pkg.module:ClassName`

## Goal
Import the Pydantic model class specified by `model_import_path` and validate it is usable for parsing JSON input.

## Algorithm
1. Validate format contains a single `:` and both sides are non-empty.
2. `module = importlib.import_module(module_path)`
3. `cls = getattr(module, class_name)`; if missing → error
4. Validate type:
   - Ideally: `issubclass(cls, TemplateModel)` (your base)
   - Minimum: `issubclass(cls, pydantic.BaseModel)`
5. Return class.

## Error handling
Wrap and raise `TemplateImportError` with:
- the failing import path
- the underlying exception type/message

## Tests
- Valid import path works.
- Module not found, class not found, not a model: all raise `TemplateImportError`.
