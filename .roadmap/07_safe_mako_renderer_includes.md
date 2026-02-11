# Step 7 — Safe Mako rendering + include enforcement

## Goal
Render root-relative URIs like `templates/...` with Mako while enforcing the `templates/**` boundary for:
- render targets
- **includes**

## Deliverables
- `templateer/renderer.py`
  - `render_uri(env, template_uri, context: dict) -> str`
  - `render_template_id(env, template_id, json_data: dict) -> str`
- Mako lookup configured for:
  - strict undefined
  - no compiled cache written into template trees
  - safe include resolution through your URI validator

## Implementation notes
- Ensure every include path is validated through `uri.py`.
- If you need deeper control, use a custom loader/lookup wrapper that:
  - intercepts template loading
  - rejects invalid include URIs before file access

## Tests
- strict undefined: missing var raises
- include attempt `../x` fails fast
- include to `templates/_shared/...` and `templates/<id>/...` works
- symlinked template directory under `templates/` works without `realpath()`

## Acceptance criteria
- `mpt render <id> ...` fails loudly on missing variables.
- Includes cannot escape `templates/` even if the filesystem would allow it.
