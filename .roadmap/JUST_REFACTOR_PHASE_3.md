# JUST_REFACTOR_PHASE_3

## Objective
Normalize script architecture so scripts are thin entrypoints over shared services and can scale without copy-paste.

## Scope
- Standardize script conventions under `scripts/`.
- Ensure scripts call service-layer APIs instead of duplicating orchestration.

## Implementation Tasks
1. **Define script conventions**
   - Document conventions in `scripts/README` or root docs:
     - one script = one workflow
     - argument parsing only in script entrypoint
     - business logic in `templateer.services`

2. **Refactor existing scripts**
   - Update `scripts/new_template.py` and `scripts/demo_generate_from_jsonl.py`:
     - remove duplicated parsing/output logic
     - delegate to shared helpers/services
   - Evaluate `scripts/dev_watch` and align to same bootstrap/runtime assumptions.

3. **Add shared script utilities**
   - Create helper(s) for repetitive concerns:
     - path normalization
     - project-root discovery
     - common error printing / exit behavior
   - Keep these utilities minimal and generic.

4. **Wire `Justfile` recipes to normalized scripts/services**
   - Ensure each recipe targets a stable script or module command.
   - Avoid hidden coupling to implementation details.

## Parallelization Notes
- Can proceed alongside Phase 2 once service interfaces are available.
- Different contributors can own separate scripts if shared utility contracts are agreed early.

## Testing Requirements
1. **Script-focused tests**
   - Add tests for script argument handling and integration boundaries (prefer subprocess-style tests if already used in repo patterns).
   - Validate scripts fail fast and clearly on invalid arguments.

2. **Cross-path consistency checks**
   - For each workflow available via CLI and script, assert equivalent outputs for the same input.
   - Add regression tests to ensure script behavior does not diverge from service behavior.

3. **Validation checklist for completion**
   - No script duplicates core render/validation logic already available in services.
   - Shared utility is used by all maintained scripts.
   - `Justfile` recipes reference standardized entrypoints only.
