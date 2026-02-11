# SKILLS.md — Testing strategy (MVP)

## Goal
Prove the invariants with fast, deterministic tests.

## Recommended test layers
### Unit tests
- URI validation utilities (table-driven)
- Import path parsing
- Filename validation
- Registry Pydantic validation

### Integration tests (temp project_root)
Create a temporary directory with:
- `templates/_shared/...`
- `templates/<id>/template.mako`, `README.md`, `manifest.json`
- build registry and render with sample JSON

### Symlink tests
- Make `templates/<id>` a symlink to another folder (still under temp root)
- Ensure rendering works without relying on realpath

## Helpful fixtures
- `make_project_root(tmp_path)` builds the expected tree.
- `write_registry(tmp_path, content)` for freshness tests.

## Non-goals for MVP tests
- Performance benchmarking
- Concurrency (unless you decide to make `TemplateEnv` thread-safe)
