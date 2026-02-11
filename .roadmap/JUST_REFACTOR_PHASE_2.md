# JUST_REFACTOR_PHASE_2

## Objective
Extract generation orchestration from `cli.py` into reusable service modules so CLI becomes a thin adapter.

## Scope
- Move `_generate_single`, `_generate_examples`, and JSON payload parsing flows out of CLI.
- Preserve user-visible CLI behavior and exit code semantics.

## Implementation Tasks
1. **Create service-layer modules**
   - Introduce `src/templateer/services/` package with modules such as:
     - `generation_service.py`
     - `registry_service.py`
     - `input_service.py`
   - Move command orchestration from `src/templateer/cli.py` into these modules.

2. **Define stable service functions**
   - Implement functions with clear contracts, e.g.:
     - `generate_single(project_root, template_id, payload) -> Path`
     - `generate_examples(project_root, template_id) -> tuple[int, int]`
     - `parse_json_object(raw_json) -> dict[str, object]`
   - Keep `TemplateError` and validation error boundaries explicit.

3. **Slim down CLI**
   - Update `src/templateer/cli.py` so `app()` only does:
     - argument parsing
     - service invocation
     - stdout/stderr formatting
     - exit code mapping
   - Remove embedded rendering/write loops from CLI.

4. **Keep compatibility guarantees**
   - Preserve output messages and non-zero behavior expected by current tests and automation.

## Parallelization Notes
- This phase can run in parallel with Phase 3 after service interfaces are agreed.
- Avoid editing `Justfile` in this phase to reduce merge conflicts with Phase 1/3.

## Testing Requirements
1. **Service unit tests**
   - Add tests under `tests/` for new `templateer.services` functions:
     - JSON object parsing failures/success
     - single generation happy path
     - example loop success/failure counters

2. **CLI regression tests**
   - Update `tests/test_cli_generate.py` and related CLI tests to verify no behavior drift.
   - Ensure stderr messages for malformed JSON and template errors are still surfaced.

3. **Validation checklist for completion**
   - `src/templateer/cli.py` contains no business-loop logic for render/write.
   - Service functions are directly callable from non-CLI code.
   - CLI test suite continues to pass with unchanged command UX.
