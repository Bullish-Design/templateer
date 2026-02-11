# SKILLS.md — Mako lookup configured for safe, root-relative URIs

## Goal
Create a Mako environment that:
- loads templates by root-relative URI (`templates/...`)
- enforces strict undefined
- validates both render target and include URIs against the URI policy
- avoids writing compiled modules into template trees

## Recommended approach
### 1) Use TemplateLookup rooted at `project_root`
Configure lookup directories to include `project_root` so that `templates/...` URIs map naturally.

Key knobs:
- strict undefined enabled
- encoding defaults (if needed) are consistent
- compiled modules disabled or redirected away from template trees

### 2) Intercept template resolution
Mako can resolve includes via the lookup; to enforce policy, wrap or subclass:
- Create `SafeTemplateLookup` with:
  - `get_template(uri)` override that validates `uri` with `validate_template_uri`
  - optionally also validate include rules if you can detect the requester (see below)

### 3) Enforce include rules
Mako includes can be invoked without telling you the “current template id”.
Pragmatic MVP enforcement:
- Enforce `templates/**` + no `..` for all includes (strong baseline).
- Additionally, to enforce “_shared or same-template only”, provide a helper macro or convention:
  - Require includes to use full URIs and accept that `templates/<template_id>/...` is allowed for any template.
  - OR implement a custom `TemplateLookup` that uses Mako’s `template.uri` and parses the current template id from it to enforce same-folder rules.

If you implement the stronger rule, document it and test it.

## Rendering
- Load template via `lookup.get_template(entry.template_uri)`
- Render with `template.render(**context)`
- Wrap Mako exceptions in `TemplateRenderError` including URI and (if available) line info

## Tests
- Strict undefined: missing variable errors.
- Include traversal: `templates/x/partials/../../_shared/...` must fail.
- Root-relative includes resolve with `templates/...` paths.
