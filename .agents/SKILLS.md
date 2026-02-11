# SKILLS.md — Refactor skill map for Templateer contributors

This file defines practical “skills” contributors should apply while executing the service-first refactor.

## Skill: service-extraction

**Use when:** CLI or script logic is growing and should be reusable.

**Objective:** Move orchestration into `templateer.services` without changing behavior.

**Checklist:**
1. Locate workflow logic currently in `templateer/cli.py` or standalone script.
2. Extract pure functions into a service module with explicit inputs/outputs.
3. Keep CLI/script layer as thin adapters (arg parsing, printing, exit codes).
4. Add or update tests around extracted service behavior.
5. Remove duplicate code paths after extraction.

---

## Skill: input-validation-unification

**Use when:** JSON/model payload parsing exists in multiple places.

**Objective:** Ensure one canonical parsing/validation path per input source.

**Checklist:**
1. Identify duplicate parsers (CLI helpers, importer utilities, script-level parsing).
2. Consolidate into shared function(s) in a stable module.
3. Normalize error messages and exception types.
4. Update callers to use the shared path.
5. Verify CLI output remains concise and predictable.

---

## Skill: just-workflow-design

**Use when:** Adding or changing automation recipes.

**Objective:** Keep `Justfile` declarative and minimal.

**Checklist:**
1. Keep recipes short and composable.
2. Call Python entrypoints/services; avoid embedded shell orchestration.
3. Standardize common variables (`project_root`, interpreter, paths).
4. Prefer one recipe per user-visible workflow.
5. Document recipe intent in README and/or inline comments.

---

## Skill: docs-consistency

**Use when:** Updating README, contributor docs, or template docs.

**Objective:** Keep docs aligned with current architecture and refactor direction.

**Checklist:**
1. Describe current implementation accurately (Mako, registry-authoritative flows).
2. Avoid stale references to Jinja2-centric behavior.
3. Distinguish current behavior from target refactor architecture.
4. Cross-check commands against `templateer.cli` and `Justfile`.
5. Keep examples runnable with existing command names.

---

## Skill selection guidance

- Prefer the smallest skill set needed for a change.
- Combine skills only when necessary (e.g., `service-extraction` + `docs-consistency`).
- If a change would add duplication, stop and apply `service-extraction` first.

