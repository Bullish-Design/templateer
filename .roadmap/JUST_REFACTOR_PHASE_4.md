# JUST_REFACTOR_PHASE_4

## Objective
Refactor render flow into explicit, composable pipeline stages with structured run metadata.

## Scope
- Decompose rendering into discrete units that can be reused by CLI/scripts/services.
- Introduce metadata-rich execution context for observability and CI usage.

## Implementation Tasks
1. **Define pipeline stage APIs**
   - Introduce functions (module candidates: `src/templateer/services/pipeline.py`, `render_pipeline.py`) for:
     - resolve template entry from registry
     - validate/parse payload against model
     - render template
     - persist outputs

2. **Introduce run metadata model**
   - Add a dataclass/Pydantic-like struct (e.g., `RenderRunMetadata`) carrying:
     - `template_id`
     - run timestamp
     - input source (inline JSON, JSONL path, line number)
     - output artifact directory/path
     - success/failure state and error details (if any)

3. **Integrate metadata into output pathway**
   - Update `src/templateer/output.py` integration points so metadata can be emitted/logged.
   - Keep existing artifact structure backward compatible unless explicitly versioned.

4. **Refactor callers to pipeline API**
   - Update service and CLI layers to compose these stages rather than calling renderer/output ad hoc.

## Parallelization Notes
- Can run parallel with Phase 5 documentation work after stage contracts are drafted.
- Coordinate carefully with Phase 2 to avoid duplicate service abstractions.

## Testing Requirements
1. **Stage-level unit tests**
   - Add tests for each stage in isolation (resolve, validate, render, persist).
   - Include negative-path tests for URI violations, model validation failures, and render undefined errors.

2. **Metadata correctness tests**
   - Assert metadata fields are populated accurately for both single-run and examples JSONL runs.
   - Verify line-number attribution for JSONL failures.

3. **End-to-end regression checks**
   - Keep existing `tests/test_renderer.py`, `tests/test_uri*.py`, and CLI generation tests green.
   - Add at least one integration test proving pipeline composition produces current artifact outputs.

4. **Validation checklist for completion**
   - Render flow can be assembled from pipeline stages without CLI imports.
   - Metadata object is produced for every render attempt.
   - Existing external behavior remains compatible.
