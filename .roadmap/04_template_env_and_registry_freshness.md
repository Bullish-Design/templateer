# Step 4 — TemplateEnv + registry freshness reloading

## Goal
Build `TemplateEnv` that:
- anchors everything to `project_root`
- **freshness-checks** `templates/registry.json` on every lookup
- reloads and revalidates when it changes

## Deliverables
- `templateer/env.py`
  - `TemplateEnv(project_root: Path, clock=...)`
  - `.registry_path`
  - `.get_registry()` with freshness check
  - `.get_entry(template_id: str)` convenience
- Tests for reload behavior

## Freshness strategy
Track a signature like:
- `st_mtime_ns`
- `st_size`
- (optional) `st_ino`

If signature changes, reload JSON and Pydantic-validate.

## Tasks
- Implement env paths:
  - `templates_dir`, `output_dir`, `log_dir`
- Keep all user-facing messages root-relative.
- Add a test:
  - write registry v1
  - `get_entry()` reads v1
  - rewrite registry v2 (touch/replace)
  - `get_entry()` reads v2 without restarting

## Acceptance criteria
- Registry changes are observed on the next call.
- Missing registry file yields `RegistryError` with path + hint.
