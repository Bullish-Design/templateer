# Step 1 — Project skeleton + conventions

## Goal
Create a minimal, testable Python package + CLI entrypoint for **Templateer** with the repo layout aligned to the plan.

## Deliverables
- `src/templateer/` package skeleton
- `pyproject.toml` configured for a `mpt` console script
- `tests/` skeleton
- `scripts/` helpers (Linux-focused)

## Tasks
- Create package modules (empty for now):
  - `errors.py`, `uri.py`, `manifest.py`, `registry.py`, `env.py`, `importers.py`, `renderer.py`, `output.py`, `logging_.py`, `cli.py`
- Add a CLI entrypoint:
  - `mpt` → `templateer.cli:app` (or equivalent)
- Add a tiny smoke test (imports + `--help`).
- Add `scripts/dev_watch` (optional) that reruns tests on change using `entr` if available.

## Acceptance criteria
- `python -m templateer.cli --help` works.
- `pytest` runs and passes the smoke test.

## Linux shortcuts
- Use `find`, `xargs`, `entr`, `rg`/`grep` to speed up iteration.
- Keep all path logic in Python rooted at `project_root`; avoid `realpath()` to stay symlink-friendly.
