# SKILLS.md — Registry models & freshness

## Goal
Implement the on-disk JSON registry as the **only authoritative** mapping of `template_id` → (`template_uri`, `model_import_path`, metadata), with runtime freshness checks.

## Inputs
- `project_root: Path`
- `templates/registry.json` file on disk

## Outputs
- `TemplateRegistry` (validated Pydantic model)
- `TemplateEntry` for a given `template_id`
- Deterministic and debuggable errors (`RegistryError`, `TemplateNotFoundError`)

## Data models (Pydantic)
- `TemplateEntry`
  - `template_uri: str` (required)
  - `model_import_path: str` (required, `pkg.module:ClassName`)
  - `readme_uri: str | None` (default `templates/<id>/README.md`)
  - `description: str | None`
  - `tags: list[str] | None`
- `TemplateRegistry`
  - `version: str`
  - `templates: dict[str, TemplateEntry]`

## Freshness algorithm
Maintain an internal cache:
- `cached_registry: TemplateRegistry | None`
- `cached_stat: tuple[int, int] | None` where tuple is `(st_mtime_ns, st_size)`

On every lookup:
1. `stat = registry_path.stat()` (if missing → `RegistryError`)
2. `fingerprint = (stat.st_mtime_ns, stat.st_size)`
3. If fingerprint differs from `cached_stat`, read file, parse JSON, validate via Pydantic, store.
4. Return cached.

### Notes
- Use `mtime_ns` to reduce missed changes on fast edits.
- Do not debounce: the concept explicitly wants freshness checks on every lookup.

## Edge cases
- Invalid JSON → `RegistryError` with parse location if possible
- Schema validation errors → `RegistryError` including Pydantic errors
- Missing `template_id` key → `TemplateNotFoundError`

## Tests
- Change detection: write registry, load, rewrite with different content, ensure reload occurs.
- Validation: registry with a bad `model_import_path` or invalid URI should fail.
