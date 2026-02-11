# AGENTS.md — Templateer (library + CLI) build guide

This repository implements **Templateer**, a convention-driven Python library + CLI for rendering **Mako** templates from **Pydantic** models, using an on-disk **JSON registry** as the single source of truth. This document translates the project concept into an implementation plan and acceptance criteria.

## What “done” means (MVP)

- You can run:
  - `mpt registry build --project-root <path>` to create `templates/registry.json` from per-template `manifest.json` files (no imports during build).
  - `mpt render <template_id> --project-root <path> --json <file|->` to validate JSON via the registered model and render the registered template.
- All template and include URIs are **root-relative**, must live under `templates/**`, and must be blocked from escaping via `..`.
- Registry lookups **always** freshness-check the file on disk and reload+revalidate when it changes.
- Rendering is **symlink-friendly**: operate on URIs + `project_root`, and avoid any logic that relies on `realpath()`.

---

## Repo shape (recommended)

```
src/templateer/
  __init__.py
  env.py
  registry.py
  manifest.py
  importers.py
  uri.py
  renderer.py
  output.py
  logging_.py
  errors.py
  cli.py
tests/
  ...
```

Keep the library independent of any “consumer project” layout beyond the required `project_root/` conventions.

---

## Architectural decisions (lock these in early)

### 1) Registry is authoritative
- The registry decides `template_uri` and `model_import_path`.
- Any per-model hints (e.g., a class attribute) are *advisory* only and may be used for drift detection, never as the source of truth.

### 2) URI-based security boundary
Treat `template_uri` and include URIs as **posix-style** paths (regardless of OS). Enforce:
- Must start with `templates/`
- Must not be absolute
- Must not contain `..` segments (after normalization)
- Must not contain backslashes

Do **not** try to “fix” URIs by resolving symlinks.

### 3) Deterministic registry build
Registry build reads manifests and filesystem structure only; it must not import arbitrary Python modules.

---

## Implementation plan (incremental)

### Phase A — Core models and errors
1. Implement exceptions (`errors.py`):
   - `TemplateError` base
   - `RegistryError`, `TemplateNotFoundError`, `TemplateImportError`, `TemplateRenderError`, `OutputWriteError`
2. Implement Pydantic models (`registry.py`, `manifest.py`):
   - `TemplateEntry`, `TemplateRegistry`
   - `TemplateManifest` (min: `model_import_path`, optional `description`, `tags`)
3. Implement URI validation utilities (`uri.py`).

**Acceptance checks**
- Invalid URIs are rejected with clear messages (include the offending URI).

### Phase B — Registry loading + freshness (`env.py`, `registry.py`)
1. `TemplateEnv` holds:
   - `project_root`, `templates_dir`, `output_dir`, `log_dir`
   - `clock` callable returning UTC `datetime`
2. Implement:
   - `env.registry_path` → `templates/registry.json`
   - `env.get_registry()` with freshness check:
     - capture `stat().st_mtime_ns` + `st_size` (or inode too) for change detection
     - on change: reload JSON, Pydantic-validate
   - `env.get_entry(template_id)` convenience

**Acceptance checks**
- Modify `registry.json` on disk; subsequent `get_entry()` sees changes without restarting the process.

### Phase C — Model import (`importers.py`)
Implement importing `pkg.module:ClassName`:
- Validate the format (`:` separator, non-empty class name)
- Import module, `getattr`, ensure it’s a Pydantic model subclass compatible with your `TemplateModel` base (or at least `BaseModel`)

**Acceptance checks**
- Bad import path yields `TemplateImportError` with actionable context.

### Phase D — Mako rendering (`renderer.py`, `uri.py`)
1. Create a safe Mako lookup that:
   - Accepts root-relative URIs like `templates/invoice/template.mako`
   - Enforces your URI policy for **both** render targets and includes
   - Uses strict undefined
   - Avoids compiled template cache output inside template trees

2. Render flow:
   - `env.get_entry(template_id)`
   - import model
   - parse input JSON → model instance (extra forbidden)
   - render with context = `model.model_dump()`

**Acceptance checks**
- Include attempts like `../secrets.mako` fail fast.
- Missing variables fail loudly (strict undefined).

### Phase E — Output + logging (`output.py`, `logging_.py`)
1. Output rules:
   - `output/<template_id>/`
   - safe filename validation: no separators, no `..`
   - prefix timestamp: `YYYYMMDD-HHMMSSZ_...`
2. Logging:
   - append-only file at `log/mpt.log`
   - JSONL or line-oriented key=val; include required fields from concept

**Acceptance checks**
- `--write` produces a file in the right folder with the right name shape.
- Logs contain template_id, template_uri, model_import_path, and output path if written.

### Phase F — CLI (`cli.py`)
Expose commands:
- `mpt registry build --project-root <path>`
- `mpt registry show --project-root <path>`
- `mpt render <template_id> --project-root <path> --json <file|-> [--write] [--filename ...]`
- `mpt render-uri <template_uri> ...` (same restrictions)

**Acceptance checks**
- `--json -` reads stdin.
- Exit codes are non-zero on errors; stderr has a concise message; logs contain details.

### Phase G — Tests (`tests/`)
Minimum suite:
- URI validation tests (good/bad cases)
- Registry reload tests (touch file, reload happens)
- Registry build tests (manifests → registry output)
- Rendering tests (strict undefined, include restrictions)
- Symlink scenario tests (template folders symlinked under templates/)

---

## Guardrails for agents

### Invariants (never break)
- Registry is the only mapping authority.
- Template/include URIs are validated and restricted to `templates/**`.
- Build must not import models.
- Rendering must not depend on symlink resolution.

### Code style
- Prefer small, composable functions with explicit inputs/outputs.
- Put policy decisions in one place (URI rules in `uri.py`, registry freshness in `TemplateEnv`).

### Error messages
- Include: `template_id` or `template_uri`, and the action being attempted.
- Prefer root-relative paths in user-facing errors.

---

## Suggested deliverables checklist
- [ ] Library API: `TemplateEnv`, `TemplateModel.render()`
- [ ] Registry models + loader with freshness
- [ ] Deterministic registry builder
- [ ] Safe Mako lookup (render + includes)
- [ ] CLI wired to the above
- [ ] Output writer + logger
- [ ] Tests covering invariants and edge cases
