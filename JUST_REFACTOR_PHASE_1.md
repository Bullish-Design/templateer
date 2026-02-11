# JUST_REFACTOR_PHASE_1

## Objective
Establish a stable execution surface so refactor work can proceed in parallel without churn in command invocations or path assumptions.

## Scope
- Keep `Justfile` orchestration-only.
- Pin command conventions used by CLI and scripts.
- Define shared runtime assumptions to prevent each phase from re-inventing bootstrap logic.

## Implementation Tasks
1. **Freeze command contract and naming**
   - Confirm and document canonical command names in `src/templateer/cli.py` (`registry build`, `registry show`, `generate`, `generate-examples`).
   - Document the expected output semantics (stdout for success artifacts, stderr for errors, non-zero exit on failure).
   - Add explicit notes that these command names are compatibility-sensitive for future `just` and script wrappers.

2. **Harden `Justfile` as a thin shell**
   - Keep only orchestration recipes in `Justfile`.
   - Ensure recipes call Python module/script entrypoints rather than embedding business logic.
   - Standardize environment flags (`PYTHONPATH=src`, `--project-root`) across all recipes.

3. **Create a shared script bootstrap utility**
   - Add a helper module (e.g., `scripts/_bootstrap.py` or `src/templateer/services/runtime.py`) that resolves:
     - project root
     - python path assumptions
     - common output directories
   - Refactor existing scripts (`scripts/new_template.py`, `scripts/demo_generate_from_jsonl.py`) to consume this helper.

4. **Define refactor guardrails**
   - Add a short contributor note in `README.md` or `CONCEPT.md` stating:
     - CLI is a public shell contract
     - orchestration belongs in services
     - `Justfile` should stay declarative

## Parallelization Notes
- This phase should land first.
- It provides stable interfaces for Phases 2–6 and minimizes branch drift.

## Testing Requirements
1. **Static checks**
   - Verify `Justfile` contains no inline Python logic beyond invoking entrypoints.
   - Verify each recipe passes `--project-root` where applicable.

2. **Behavioral tests to add/update**
   - Add/update CLI tests in `tests/test_cli_generate.py` and `tests/test_dev_step_5.py` to assert command names and help surfaces remain unchanged.
   - Add a script bootstrap unit test (new file under `tests/`) for root/path resolution behavior.

3. **Validation checklist for completion**
   - Existing command help snapshots still pass.
   - No duplicated project-root bootstrap code remains in `scripts/` entrypoints.
   - `Justfile` only orchestrates calls to modules/scripts.
