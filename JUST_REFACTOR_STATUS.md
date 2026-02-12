# JUST_REFACTOR_STATUS

## Refactor completion summary

### What moved into `templateer.services`
- Input parsing and top-level JSON object validation moved to `src/templateer/services/input_service.py`.
- Generation orchestration moved to `src/templateer/services/generation_service.py`:
  - single render workflow (`generate_single`)
  - JSONL batch workflow (`process_jsonl_inputs`)
  - examples workflow (`generate_examples`)
- Render pipeline stages were made explicit in `src/templateer/services/pipeline.py`:
  - registry resolution
  - payload validation against model import path
  - URI render stage
  - artifact persistence wrappers
- Shared runtime/bootstrap helpers are centralized in `src/templateer/services/runtime.py`.

### What stayed as adapters
- `src/templateer/cli.py` remains a thin command adapter:
  - argument parsing
  - invocation of service functions
  - stdout/stderr message and exit-code mapping
- `scripts/new_template.py` and `scripts/demo_generate_from_jsonl.py` remain thin script entrypoints over services.
- `Justfile` remains orchestration-only and delegates behavior to CLI/scripts.

### Quality gates
- Unit and integration tests under `tests/` cover services, CLI, scripts, and refactor steps.
- `just run-tests` is the baseline CI quality gate.
- Phase 6 parity/regression checks now include:
  - stable render-attempt error categorization for template failures (`TemplateError`)
  - CLI/script workflow parity checks for example generation outcomes
  - static checks that `Justfile` routes workflows through supported entrypoints

### Known follow-up items
- Add optional lint/type quality gates once tool choices are finalized (`just lint`, `just typecheck`).
- Consider adding machine-readable structured logs for CI ingestion.
- Add an explicit performance benchmark harness for large JSONL batch generation.
