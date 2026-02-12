# Templateer

Templateer is a registry-authoritative Python library + CLI for generating files from **Mako** templates with **Pydantic**-validated inputs.

This repository is currently in a refactor phase to support composable `just` workflows backed by shared Python service modules.

## What Templateer does today

- Builds a deterministic template registry from `templates/*/manifest.json`
- Validates input payloads against registered model import paths
- Renders registered Mako templates safely under `templates/**`
- Writes generation artifacts for single-input and example-driven runs

## Core concepts

- **Registry is source of truth**: `templates/registry.json` maps `template_id` to `template_uri` and `model_import_path`
- **URI safety policy**: templates/includes must remain under `templates/**` and cannot use traversal
- **Mako-first rendering**: strict rendering behavior with guarded template lookup
- **Environment freshness**: registry reads are reloaded when the on-disk file changes

## Project layout

```text
src/templateer/
  cli.py
  env.py
  registry.py
  manifest.py
  importers.py
  renderer.py
  output.py
  uri.py
  errors.py

templates/
  registry.json
  <template-id>/
    manifest.json
    template.mako
    examples/sample_inputs.jsonl
```

## CLI usage

### Build registry

```bash
PYTHONPATH=src python -m templateer.cli registry build --project-root .
```

### Show registry

```bash
PYTHONPATH=src python -m templateer.cli registry show --project-root .
```

### Generate one output from inline JSON

```bash
PYTHONPATH=src python -m templateer.cli generate \
  --project-root . \
  --template-id greeting \
  --input-json '{"name":"Ada","title":"Engineer"}'
```

### Generate from examples JSONL

```bash
PYTHONPATH=src python -m templateer.cli generate-examples \
  --project-root . \
  --template-id greeting
```

## `just` workflows

The `Justfile` is intended to stay thin and declarative.

Common recipes:

```bash
just build-registry
just create-template greeting my_app.models:GreetingModel
just run-template-examples greeting
just run-tests
```

### `build-registry`

**Purpose**

Builds `templates/registry.json` by scanning `templates/*/manifest.json` and validating each template entry.

**Inputs / arguments**

- No positional arguments.
- Uses `python` and `project_root` variables from `Justfile` (defaults: `python`, `.`).
- Effective command:

  ```bash
  PYTHONPATH=src python -m templateer.cli registry build --project-root .
  ```

**Resulting files / side effects**

- Creates or replaces `templates/registry.json` atomically.
- Fails fast if required template files are missing (`manifest.json`, `template.mako`, `README.md`).

**Common failures and likely fixes**

- `manifest file does not exist` / `manifest validation failed while building registry`
  - Add or fix `templates/<id>/manifest.json`.
- `manifest is not valid JSON`
  - Fix malformed JSON (trailing commas/comments are not allowed).
- `manifest contains unknown fields`
  - Keep only `model_import_path`, `description`, `tags`.
- `template missing required file`
  - Ensure each template folder contains `manifest.json`, `template.mako`, and `README.md`.

### `create-template <template_id> <model_import_path> [description] [tags]`

**Purpose**

Scaffolds a new template folder under `templates/<template_id>/` and rebuilds registry.

**Inputs / arguments**

- Required positional args:
  - `template_id` (must match `[a-zA-Z0-9][a-zA-Z0-9_-]*`)
  - `model_import_path` (expected `pkg.module:ClassName`)
- Optional positional args:
  - `description` (default empty string; scaffold service fills fallback text)
  - `tags` (comma-separated string)

**Resulting files / side effects**

- Creates these files/directories if missing:
  - `templates/<template_id>/manifest.json`
  - `templates/<template_id>/template.mako`
  - `templates/<template_id>/README.md`
  - `templates/<template_id>/examples/sample_inputs.jsonl`
  - `templates/<template_id>/gen/.gitkeep`
- Rebuilds `templates/registry.json`.

**Common failures and likely fixes**

- `template-id cannot be empty` / `template-id must match [a-zA-Z0-9][a-zA-Z0-9_-]*`
  - Provide a valid identifier (no spaces/slashes).
- `Template already exists and is not empty`
  - Choose another id, or clean/reuse existing template directory.
- Registry build errors after scaffold
  - Resolve the manifest/template/README issues in the newly created template and rerun `just build-registry`.

### `run-template-examples <template_id>`

**Purpose**

Builds registry, then renders each line in `templates/<template_id>/examples/sample_inputs.jsonl`.

**Inputs / arguments**

- Required positional arg: `template_id`.
- Implicit prerequisite: runs `build-registry` first.

**Resulting files / side effects**

- Reads `templates/<template_id>/examples/sample_inputs.jsonl`.
- For each valid JSON object line, writes a timestamped artifact directory under `templates/<template_id>/examples/` containing:
  - `input.json`
  - `output.txt`
- Prints a summary: `Processed examples: success=<n>, failure=<m>`.
- Returns non-zero exit code when any failures occur.

**Common failures and likely fixes**

- `line <n>: input is not valid JSON (...)`
  - Fix invalid JSON syntax in that JSONL line.
- `line <n>: input JSON must be an object at the top level`
  - Ensure each line is an object (`{...}`), not an array/string/number.
- `<template_id> not found in registry`
  - Run `just build-registry`, confirm template id, and check `templates/registry.json`.
- Render/URI errors such as `Template URI must remain under templates/`
  - Fix template include/render URIs so they stay within `templates/**`.

### `run-tests`

**Purpose**

Runs the full test suite via `pytest`.

**Inputs / arguments**

- No positional arguments.
- Effective command:

  ```bash
  PYTHONPATH=src python -m pytest -q
  ```

**Resulting files / side effects**

- Executes unit/integration tests.
- May create temporary test artifacts depending on test behavior.

**Common failures and likely fixes**

- `ModuleNotFoundError` or import errors
  - Confirm dependencies are installed and run from repo root with `PYTHONPATH=src`.
- Assertion failures in registry/manifest/URI tests
  - Rebuild registry, then inspect template manifests and URIs for policy compliance.

## Troubleshooting

### Missing `templates/registry.json`

Symptoms:

- `registry file does not exist`
- CLI commands that depend on registry fail (for example `registry show`, `generate`, `generate-examples`).

What to do:

1. Run `just build-registry` from repository root.
2. Confirm `templates/registry.json` now exists.
3. If build still fails, resolve the reported manifest/template file issues first.

### Malformed `templates/<id>/manifest.json`

Symptoms:

- `manifest is not valid JSON`
- `manifest validation failed`
- `manifest contains unknown fields`

What to do:

1. Ensure JSON is syntactically valid.
2. Keep only supported keys: `model_import_path`, `description`, `tags`.
3. Ensure `tags` is a list of strings and `description` is a string (if present).

### Invalid `model_import_path`

Symptoms:

- `model_import_path is required`
- `model_import_path must use 'pkg.module:ClassName' format`
- `model_import_path module must be a dotted python import path`
- `model_import_path class must be a valid python identifier`

What to do:

1. Use the exact `pkg.module:ClassName` format.
2. Ensure module segments are valid Python identifiers separated by dots.
3. Ensure class name is a valid Python identifier.

### Template URI policy violations under `templates/**`

Symptoms:

- `Template URI cannot be absolute`
- `Template URI cannot contain path traversal segments`
- `Template URI must remain under templates/`
- `Template URI must use POSIX separators and cannot contain backslashes`

What to do:

1. Keep all template and include URIs relative to `templates/`.
2. Do not use `..` traversal.
3. Do not use absolute paths.
4. Use forward slashes (`/`) only.

## Contribution guidance

When adding or refactoring code, keep responsibilities explicit:

- **Business logic**
  - Place orchestration/domain workflows in `src/templateer/services/*`.
- **Command adapters**
  - Keep CLI argument parsing and exit-code mapping in `src/templateer/cli.py`.
  - Keep script wrappers/adapters in `scripts/*`.
- **Schema/contracts**
  - Place manifest schema/validation contracts in `src/templateer/manifest.py`.
  - Place registry schema/validation contracts in `src/templateer/registry.py`.
  - Keep closely related contract/types modules aligned with those schema boundaries.


## CLI compatibility contract

The CLI command names are compatibility-sensitive and are treated as a public shell contract:

- `registry build`
- `registry show`
- `generate`
- `generate-examples`

Output semantics are also stable by design:

- success artifacts/results are printed to stdout
- user-actionable failures are printed to stderr
- failing operations return non-zero exit codes

## Refactor guardrails

- Keep `Justfile` declarative/orchestration-only.
- Keep CLI modules thin (argument parsing + output + exit-code mapping).
- Put reusable orchestration/business logic in `templateer.services`.

## Refactor direction (in progress)

As documented in `CODE_REVIEW.md` and `JUST_REFACTOR.md`, Templateer is moving to:

- Shared service modules for orchestration (`templateer.services.*`)
- Thin CLI wrappers (args + exit-code mapping only)
- Thin scripts and `just` recipes that call shared services
- Unified payload parsing/validation paths

Contributors should keep new changes aligned with this direction and avoid adding new duplicated orchestration paths.

## Development notes

- Python: 3.10+
- Tests: `PYTHONPATH=src python -m pytest -q`
- License: MIT
