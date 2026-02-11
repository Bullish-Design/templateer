# JUST_REFACTOR

## Purpose
Outline the high-level refactor path needed to support composable `just`-driven template workflows, informed by `CODE_REVIEW.md`.

## Current State (from CODE_REVIEW)
- CLI contains core orchestration logic that should be reusable outside CLI.
- Input parsing/validation pathways are duplicated.
- Scripts are not yet a cohesive automation layer.
- Documentation has implementation drift (Jinja2 vs Mako).

## Refactor Goals
1. Make workflow steps composable and callable from:
   - `Justfile` recipes
   - standalone scripts
   - CLI commands
2. Minimize logic in `Justfile` itself; keep it as an orchestration surface.
3. Keep complex behavior in Python modules/scripts with tests.

## Recommended Refactor Plan

### Phase 1: Stabilize command surface
- Keep `Justfile` recipes small and declarative.
- Ensure recipes call Python entrypoints only (or thin CLI wrappers).
- Standardize environment assumptions (project root, python executable, output paths).

### Phase 2: Extract orchestration from CLI
- Move generation and example-run loops out of `cli.py` into service modules.
- Keep CLI as argument parsing + service invocation + exit code mapping.

### Phase 3: Normalize script architecture
- Create `scripts/` conventions:
  - one script per workflow
  - shared helper module for path/bootstrap behavior
- Replace one-off logic duplication with imports from `templateer.services`.

### Phase 4: Improve modularity in render pipeline
- Introduce explicit pipeline functions/stages:
  - resolve template entry
  - validate model payload
  - render template
  - persist outputs
- Consider run metadata object (`template_id`, timestamp, source input path, output path).

### Phase 5: Documentation and developer UX cleanup
- Update README terminology to Mako-first behavior.
- Add usage docs for `just` recipes with examples.
- Add short troubleshooting section for missing registry / malformed manifests.

## Additional Improvement Suggestions
- Add lint/format/typecheck recipes (`just lint`, `just fmt`, `just typecheck`) once tooling is agreed.
- Add `just run-all-examples` to iterate registry template IDs and run example generation for each.
- Add optional dry-run mode for scaffold and generation commands.
- Add structured log output (JSON lines optional) for CI ingestion.
- Introduce unit tests for any new service-layer modules before expanding features.

## Success Criteria
- CLI logic reduced to thin wrappers.
- `Justfile` remains short and readable.
- Scripts and CLI share the same underlying service functions.
- New workflows can be added without touching multiple command entrypoints.
