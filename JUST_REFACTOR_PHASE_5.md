# JUST_REFACTOR_PHASE_5

## Objective
Align documentation and developer UX with actual Mako-based architecture and new service-driven workflows.

## Scope
- Remove implementation drift in docs.
- Provide clear onboarding and troubleshooting for refactored workflows.

## Implementation Tasks
1. **README modernization**
   - Update `README.md` sections to be explicitly Mako-first.
   - Reflect service-layer architecture and thin CLI/Justfile patterns.
   - Add examples for direct service usage where appropriate.

2. **Document `just` workflows deeply**
   - Expand usage docs for each supported recipe:
     - expected inputs
     - expected outputs
     - common failures
   - Include sequence examples (e.g., scaffold -> build-registry -> generate-examples).

3. **Troubleshooting section**
   - Add concise troubleshooting for:
     - missing `templates/registry.json`
     - malformed `manifest.json`
     - invalid model import paths
     - template URI policy violations

4. **Developer contribution guidance**
   - Add short architecture notes on where to place:
     - business logic (`templateer.services`)
     - command adapters (`cli.py`, scripts)
     - schema/contract code (`manifest.py`, `registry.py`)

## Parallelization Notes
- Can run in parallel with engineering phases once interfaces stabilize.
- Merge near the end to reduce rework from code movement.

## Testing Requirements
1. **Docs consistency checks (static)**
   - Verify every documented command exists and uses current flags.
   - Verify module paths and filenames match actual repository structure.

2. **Executable example verification plan**
   - For each code snippet in README/Just docs, add or update a smoke test where feasible (or ensure snippets match tested commands in existing tests).

3. **Validation checklist for completion**
   - No Jinja2-first wording remains where implementation is Mako.
   - Docs mention service-layer architecture and thin adapters consistently.
   - Troubleshooting examples map to real error classes/messages.
