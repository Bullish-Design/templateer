# CODE REVIEW

## Scope
Static review of the current `templateer` codebase focused on architecture, maintainability, composability, and refactor readiness.

## Executive Summary
`templateer` already has a solid core shape: explicit contracts (`manifest`, `registry`, `uri`), clear error typing, and a predictable CLI workflow. The current code is small enough to evolve quickly, but there are early signs of coupling and duplication that will make multi-step template-generation pipelines harder to extend unless addressed.

Overall assessment:
- **Strong foundation** for a registry-authoritative rendering system.
- **Good safety posture** around template URI validation and strict input validation.
- **Needs modularization** around command orchestration and rendering pipeline stages to support script chaining/composable workflows.

---

## What’s Working Well

### 1) Clear domain boundaries (mostly)
- `manifest.py` and `registry.py` express contracts explicitly.
- `uri.py` centralizes path/URI policy checks.
- `errors.py` provides structured error classes with useful context payloads.

### 2) Registry freshness mechanism is pragmatic
- `TemplateEnv` caches registry with a file signature and reloads on change.
- This is practical for long-running dev loops while preserving correctness.

### 3) Rendering safety controls are present
- `_SafeTemplateLookup` and `validate_template_uri` enforce `templates/**` scoping.
- Include traversal checks are handled defensively.

### 4) Tests cover key workflows
- CLI generation and registry behavior have direct coverage.
- Stepwise test files suggest iterative development discipline.

---

## Key Risks / Improvement Areas

### 1) CLI orchestration owns too much workflow logic
`cli.py` mixes argument parsing, input decoding, rendering orchestration, and output writing. This will become harder to extend when adding chained lifecycle commands (scaffold/build/validate/render/package/publish).

**Impact:** hard to compose and reuse command logic across CLI, scripts, and potential API usage.

### 2) Duplicate parsing/validation responsibilities
There are multiple JSON parsing and input-validation pathways (`cli._parse_json_object`, `importers.parse_model_input_json`, `parse_model_input_data`).

**Impact:** duplicated behavior and inconsistent error surface over time.

### 3) Dataclass “model_*” API shape mimics Pydantic without using it
`TemplateManifest`/`TemplateRegistry` use dataclasses plus custom `model_validate` / `model_dump` methods.

**Impact:** custom validators are easy to drift; harder interoperability with tools expecting canonical Pydantic semantics.

### 4) Renderer and CLI are tightly coupled to sync single-shot flows
There is no explicit “pipeline step” abstraction (validate input, resolve template, render, write artifacts, log run metadata).

**Impact:** difficult to chain/compose generation scripts in a predictable way.

### 5) Script ecosystem is ad-hoc
There is one batch demo script and one watch script, but no coherent script module layout (`scripts/` as package with shared utilities).

**Impact:** reuse friction and copy-paste risk as process automation expands.

### 6) Documentation drift in README
README still references Jinja2 heavily while implementation uses Mako-centric renderer logic.

**Impact:** confusion for new contributors and template authors.

---

## Suggested Refactor Direction (High-level)

1. **Introduce an application-service layer** (e.g., `templateer.services`) that CLI and scripts both call.
2. **Define composable pipeline primitives** (e.g., `load_registry`, `validate_payload`, `render`, `persist_artifacts`).
3. **Unify JSON/model input validation** behind one public utility path.
4. **Normalize scripts into small Python entrypoints** that wrap service functions.
5. **Align docs with Mako + registry-authoritative workflow.**

---

## Candidate Module Layout for Better Composability

- `templateer.services.registry_service`
  - `build_registry(project_root)`
  - `load_registry(project_root)`
- `templateer.services.render_service`
  - `render_template_id(env, template_id, payload)`
  - `render_examples(env, template_id, input_jsonl_path)`
- `templateer.services.scaffold_service`
  - `create_template_scaffold(project_root, template_id, model_import_path, ...)`
- `templateer.services.output_service`
  - timestamp folder creation and artifact persistence
- `templateer.commands` (thin wrappers used by CLI)

This keeps the CLI mostly argument mapping and error-to-exit-code behavior.

---

## Tactical Cleanup Opportunities

- Replace broad `except Exception` catches with narrower error categories where possible.
- Add consistent type aliases for shared payload types (`dict[str, Any]` appears repeatedly).
- Standardize output file naming/extensions (`output.txt` may be too generic for code artifacts).
- Add structured logging hooks in generation paths (`template_id`, run id, elapsed time).
- Add smoke checks for missing template example files in CLI paths with better hints.

---

## Quality/Maintainability Rating (Current)

- Architecture clarity: **7/10**
- Safety/validation: **8/10**
- Composability for chained workflows: **5/10**
- Documentation consistency: **5/10**
- Test baseline: **7/10**

**Overall:** promising base; one focused refactor cycle can materially improve modularity and developer ergonomics.
