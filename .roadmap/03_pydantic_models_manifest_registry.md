# Step 3 — Pydantic models: manifest + registry

## Goal
Implement the Pydantic contracts for:
- per-template `manifest.json` (source for build)
- on-disk `registry.json` (runtime authority)

## Deliverables
- `templateer/manifest.py`
  - `TemplateManifest` (min: `model_import_path`, optional: `description`, `tags`)
- `templateer/registry.py`
  - `TemplateEntry`
  - `TemplateRegistry` (`templates: dict[str, TemplateEntry]`)
- JSON helpers (load/dump) with crisp validation errors

## Tasks
- Model constraints:
  - `model_import_path` required, `pkg.module:ClassName` shape validation
  - `template_uri` validated via `uri.py`
  - set sensible defaults (e.g., `readme_uri` default to `templates/<id>/README.md`)
- Add tests for:
  - invalid manifests
  - invalid registry entries
  - round-trip JSON dump/load

## Acceptance criteria
- Invalid `model_import_path` is rejected with actionable `RegistryError`/`ManifestError` (or `RegistryError` if you keep one family).
- Registry validation rejects any URI not under `templates/**`.
