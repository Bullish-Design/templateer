# Step 6 — Import model + validate input JSON

## Goal
Implement:
- importing `pkg.module:ClassName`
- validating input JSON against the model (extra fields forbidden)

## Deliverables
- `templateer/importers.py`
  - `import_model(path: str) -> type[pydantic.BaseModel]`
- JSON parsing helper used by CLI and renderer
- Optionally `templateer/model.py` with `TemplateModel` base (Pydantic) that sets `extra='forbid'`

## Tasks
- Import rules:
  - require exactly one `:`
  - import module, resolve class
  - verify it subclasses `pydantic.BaseModel`
- Validation rules:
  - parse JSON dict
  - instantiate model (should reject extras)
- Tests:
  - good import path
  - module missing
  - class missing
  - class not a Pydantic model
  - extra fields rejected

## Acceptance criteria
- Bad import path yields `TemplateImportError` with the original string and why it failed.
- Extra JSON keys cause a validation error surfaced cleanly to CLI stderr.
