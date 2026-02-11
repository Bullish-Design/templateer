# Step 2 — Errors + URI security boundary

## Goal
Lock in the error surface and **URI validation** rules so every later layer is consistent and safe.

## Deliverables
- `templateer/errors.py`
  - `TemplateError`
  - `RegistryError`, `TemplateNotFoundError`, `TemplateImportError`, `TemplateRenderError`, `OutputWriteError`
- `templateer/uri.py`
  - `validate_template_uri(uri: str) -> str` (returns normalized URI)
  - helpers for normalization and checks

## URI policy (enforce everywhere)
- Treat URIs as **posix paths**
- Must start with `templates/`
- Must not be absolute
- Must not contain backslashes
- Must not escape via `..` segments (after normalization)

## Tasks
- Implement canonical normalization (posix-style) and validation.
- Ensure errors include:
  - offending `uri`
  - action being attempted (render/include/build)
- Add unit tests for good/bad URIs.

## Acceptance criteria
- `validate_template_uri("templates/invoice/template.mako")` passes.
- `validate_template_uri("../secrets.mako")` fails with clear message.
- Backslashes or absolute paths fail.
