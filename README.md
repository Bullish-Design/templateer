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

