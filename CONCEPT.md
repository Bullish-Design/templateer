# CONCEPT.md — Templateer MVP: Pydantic Models + Mako Templates (devenv.sh-managed)

## Overview

This project is a small, convention-driven Python library + CLI for rendering **Mako** templates from **Pydantic** models. The **only authoritative mapping** between a `template_id` and its template/model is a **JSON registry** on disk (validated by Pydantic). Rendering is **symlink-friendly** by using **root-relative URIs** under a provided `project_root` and by avoiding reliance on `realpath()`.

Primary use case: `mpt render <template_id> --json ...` renders a template with validated input and optionally writes a timestamped file to `output/`.

---

## Core Principles

1. **Pydantic is the input contract**
   Input JSON must validate against the template’s Pydantic model. Extra fields are rejected.

2. **Registry is the source of truth (always)**

   * The registry determines `template_uri` and `model_import_path`.
   * Every lookup performs a disk freshness check; if the registry changed, it is reloaded before use.

3. **Root-relative template URIs under `project_root`**
   Templates and includes are referenced as URIs like `templates/invoice/template.mako`.

4. **Templates are restricted to `templates/**`**
   Includes and render targets must remain within the `templates/` tree (no escaping via `..`).

5. **Import paths are fully flexible**
   `model_import_path` can point to *any importable* module/class in the current Python environment (no requirement that models live under `templates/`).

---

## Project Root Layout

All operations are relative to a single `project_root`:

```
project_root/
  templates/
    registry.json
    _shared/
      ...shared partials...
    <template_id>/
      template.mako
      README.md
      manifest.json
      ...partials/ and other template-local files...
  output/
    <template_id>/
  log/
    mpt.log
  scripts/
    ...helper scripts (scaffold/generate/build)...
  src/
    <package_name>/
      ...
```

Notes:

* Template folders under `templates/<template_id>/` may be symlinks.
* The library must not require resolving symlinks; it should operate on paths/URIs relative to `project_root`.

---

## Template Folder Contract

Each template lives in `templates/<template_id>/` where `<template_id>` is the **folder name** (Option 6 = folder name is the ID).

Required files:

* `template.mako` — the main template
* `manifest.json` — metadata used by registry build (required)
* `README.md` — template documentation (required)

Optional files:

* Any partials/local files under the same directory (e.g., `partials/`, `macros.mako`, etc.)

### Includes

Allowed include targets:

* `templates/_shared/**`
* `templates/<template_id>/**`

Rule of thumb: includes should use **root-relative URIs** inside `templates/**`, e.g.

* `templates/_shared/header.mako`
* `templates/invoice/partials/line_item.mako`

The runtime must prevent template resolution outside `templates/` (e.g., via `..`).

---

## Registry (Authoritative)

Registry path:

```
templates/registry.json
```

### Data Model (Pydantic)

`TemplateRegistry`

* `version: str`
* `templates: dict[str, TemplateEntry]` keyed by `template_id`

`TemplateEntry`

* `template_uri: str` (required; root-relative; must be within `templates/**`)
* `model_import_path: str` (required; `pkg.module:ClassName`)
* `readme_uri: str` (optional; default `templates/<id>/README.md`)
* `description: str | None` (optional)
* `tags: list[str] | None` (optional)

### Registry Freshness

Any operation that uses the registry (CLI render, `env.get_entry`, etc.) must:

1. Check the registry file on disk (e.g., mtime/stat).
2. Reload and revalidate if it changed since last use.

This keeps CLI and library behavior aligned with “registry is authority.”

---

## Per-Template Manifest (Source for Registry Build)

Each template folder must include:

```
templates/<template_id>/manifest.json
```

Minimal schema:

```json
{
  "model_import_path": "myapp.template_models:InvoiceTemplate",
  "description": "Invoice renderer",
  "tags": ["billing"]
}
```

Rules:

* `model_import_path` is required.
* `description` / `tags` are optional.
* Build does **not** import model code (deterministic build; no side effects).

Helper scripts live in `scripts/` (e.g., `scripts/new_template`, `scripts/build_registry`) to reduce boilerplate and ensure manifests are consistent.

---

## Rendering Flows

### CLI (primary path)

1. Load registry (freshness check)
2. Resolve `template_id` → entry
3. Import model from `entry.model_import_path`
4. Parse JSON into model (Pydantic; extra fields forbidden)
5. Render template at `entry.template_uri`
6. Output to stdout; optionally write file under `output/<template_id>/`

### Python API (convenience)

A model instance can render itself by `template_id`, but it must still consult the registry at render time:

* The model must identify its `template_id` (usually via a `ClassVar[str]`).
* Rendering uses the registry’s `template_uri` (authoritative).
* If the model class also declares a `template_uri`, it is treated as advisory and may be validated against the registry to detect drift.

---

## Public API (MVP)

### `TemplateEnv`

Holds configuration and runtime services.

Fields:

* `project_root: Path`
* `templates_dir = project_root / "templates"`
* `output_dir = project_root / "output"`
* `log_dir = project_root / "log"`
* `clock` (callable returning “now”; default UTC)

Responsibilities:

* Registry loading with freshness checks
* Mako lookup configured so URIs like `templates/...` resolve
* Enforcement that template URIs remain within `templates/**`
* Output directory creation
* Logging to `log/mpt.log`

### `TemplateModel` (base)

A Pydantic base class for template inputs.

Defaults:

* `extra = "forbid"` (reject unknown fields)

Recommended subclass contract:

* `template_id: ClassVar[str]` (required for `.render(...)` convenience)

Method:

* `render(env: TemplateEnv, *, write: bool = False, filename: str | None = None) -> str`

Behavior:

1. Fresh-load registry; resolve entry by `self.template_id`
2. Render template with context = `self.model_dump()`
3. If `write=True`, write output file to `output/<template_id>/...`
4. Return rendered text

---

## Output + Logging

### Output files

Write target:

```
output/<template_id>/
```

Filename rules (safe by default):

* If `filename` is provided, it must be a **simple filename** (no `/`, `\`, `..`).
* Output filename is prefixed with a UTC timestamp:

  * `YYYYMMDD-HHMMSSZ_<filename>`
* Default filename if not provided:

  * `YYYYMMDD-HHMMSSZ_rendered.txt`

### Logging

Append-only log file:

```
log/mpt.log
```

Log entries should include (at minimum):

* UTC timestamp
* level
* action/command
* template_id
* template_uri
* model_import_path
* output path (if written)
* exception info (if any)

Format can be line-oriented structured text or JSONL; prioritize grep/tail friendliness.

---

## CLI (Unix-friendly)

Illustrative command set:

* `mpt registry build --project-root <path>`

  * Scans `templates/*/template.mako` excluding `_shared`
  * Uses folder name as `template_id`
  * Reads `templates/<id>/manifest.json` for `model_import_path` (and metadata)
  * Writes `templates/registry.json`

* `mpt registry show --project-root <path>`

  * Prints registry (validated) to stdout

* `mpt render <template_id> --project-root <path> --json <file|-> [--write] [--filename name.txt]`

  * `--json -` reads JSON from stdin
  * Writes to stdout unless `--write` is provided

* `mpt render-uri <template_uri> ...`

  * Escape hatch for direct URI rendering
  * Still restricted to `templates/**`

---

## Error Handling (MVP)

Exception set:

* `TemplateError` (base)
* `RegistryError` (missing/invalid registry, manifest issues, validation failures)
* `TemplateNotFoundError` (missing template file/URI)
* `TemplateImportError` (cannot import model class)
* `TemplateRenderError` (Mako rendering failure; include URI and helpful location info)
* `OutputWriteError` (invalid filename, permissions, etc.)

Errors should prefer root-relative paths in messages for clarity with symlinks.

---

## Runtime Defaults (MVP)

* Mako strict undefined: **on** (fail loudly on missing vars)
* Template lookup supports root-relative URIs like `templates/...`
* No compiled module cache by default (avoid writing into template trees)
* Deterministic registry build: **no importing** during build
* Clock default: **UTC** (injectable for tests)

---

## Minimal Example

`templates/invoice/manifest.json`

```json
{
  "model_import_path": "myapp.template_models:InvoiceTemplate",
  "description": "Invoice renderer",
  "tags": ["billing"]
}
```

`templates/registry.json` (built)

```json
{
  "version": "1",
  "templates": {
    "invoice": {
      "template_uri": "templates/invoice/template.mako",
      "model_import_path": "myapp.template_models:InvoiceTemplate",
      "readme_uri": "templates/invoice/README.md",
      "description": "Invoice renderer",
      "tags": ["billing"]
    }
  }
}
```

CLI:

* `mpt render invoice --project-root . --json input.json`
* `cat input.json | mpt render invoice --project-root . --json - --write --filename invoice.txt`

Python:

* `InvoiceTemplate(...).render(env, write=True, filename="invoice.txt")` (registry-driven)

---

If you want, next I can draft the **manifest schema** as a Pydantic model and the **registry build algorithm** in a short, implementation-ready outline (still keeping the concept doc clean).

