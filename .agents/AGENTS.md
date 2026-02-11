# AGENTS.md — Templateer refactor guidance (services + `just` workflows)

This repository is moving from a CLI-centric implementation to a **service-first architecture** where CLI commands, scripts, and `just` recipes all share the same Python orchestration layer.

Use this guide when making changes so implementation and docs stay aligned with `CODE_REVIEW.md` and `JUST_REFACTOR.md`.

## Current refactor direction

Templateer remains:
- Registry-authoritative (`templates/registry.json` is source of truth)
- Mako-based rendering
- Pydantic model validation

But workflow orchestration should converge on:
- `templateer.services.*` for reusable business logic
- Thin CLI wrappers (`templateer.cli`) for args + exit codes
- Thin scripts and `Justfile` recipes that call service APIs/entrypoints

---

## Definition of done for refactor-aligned changes

A change is “aligned” when:

1. **No new business logic is added directly to CLI command handlers** unless there is a short-term blocker.
2. **Reusable workflow logic lives in service modules**, not duplicated across CLI/scripts.
3. **`Justfile` remains declarative** (small recipes, minimal shell logic).
4. **Input parsing/validation behavior is unified** (single public parsing path per input type).
5. **Docs describe Mako + registry-first behavior accurately** (no legacy Jinja2 messaging).

---

## Architectural guardrails (do not break)

1. **Registry is authoritative**
   - `template_id -> template_uri + model_import_path` mapping comes from registry.
   - Do not let model classes override mapping at runtime.

2. **URI security boundary**
   - Template and include URIs are root-relative under `templates/**`.
   - No absolute paths, backslashes, or traversal (`..`).
   - Preserve symlink-friendly behavior (do not rely on realpath-based policy).

3. **Deterministic registry build**
   - Registry generation must not import arbitrary model modules.

4. **Composable pipeline stages**
   - Prefer explicit stages/functions: resolve entry, validate payload, render, persist artifacts.

---

## Recommended module shape (target)

- `templateer.services.registry_service`
  - build/load registry operations
- `templateer.services.render_service`
  - single render and multi-input render flows
- `templateer.services.scaffold_service`
  - template scaffold creation helpers
- `templateer.services.output_service`
  - artifact path creation + writes
- `templateer.commands`
  - optional thin command adapters used by CLI/scripts

If full extraction is too large for one change, move one workflow at a time and keep behavior identical.

---

## `just` and scripts conventions

- `Justfile` recipes should call Python entrypoints only.
- Complex looping/branching belongs in Python, not inline shell in recipes.
- Scripts under `scripts/` should be workflow-specific and import shared service modules.
- Avoid copy-paste orchestration between CLI and scripts.

---

## Error handling and DX

- User-facing errors should stay concise and contextual (`template_id`, action, relevant path).
- Keep structured context in custom exceptions.
- Preserve current non-zero exit behavior on command failures.

---

## Documentation alignment rules

When editing docs:
- Describe Templateer as **Mako + Pydantic + registry**.
- Reference `generate` / `generate-examples` command surface (current), while marking service extraction as ongoing refactor.
- Keep contributor guidance consistent with `JUST_REFACTOR.md` goals.

