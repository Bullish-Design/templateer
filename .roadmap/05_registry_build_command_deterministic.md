# Step 5 — Registry builder (deterministic, no imports)

## Goal
Implement `mpt registry build`:
- scans `templates/*/` (excluding `templates/_shared`)
- reads `manifest.json`
- writes authoritative `templates/registry.json`
- **does not import** any model code

## Deliverables
- builder code (e.g., `templateer/registry.py` or `templateer/builder.py`)
- CLI command: `mpt registry build --project-root <path>`
- CLI command: `mpt registry show --project-root <path>`

## Tasks
- Scan rules:
  - template_id = folder name under `templates/`
  - require `template.mako`, `manifest.json`, `README.md`
- Construct `TemplateEntry` for each template:
  - `template_uri = templates/<id>/template.mako`
  - `model_import_path` from manifest
  - `readme_uri` default (or from manifest if you later extend)
- Write registry atomically:
  - write temp file then `os.replace()`

## Linux shortcuts
- For quick debugging:
  - `jq . templates/registry.json`
  - `find templates -maxdepth 2 -name manifest.json -print`

## Acceptance criteria
- `mpt registry build --project-root .` produces `templates/registry.json`.
- build fails clearly if a template folder is missing required files.
- build never imports arbitrary Python modules.
