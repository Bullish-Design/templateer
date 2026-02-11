# SKILLS.md — End-to-end render flow (CLI + API)

## Goal
Implement rendering that always consults the registry, validates input via Pydantic, and renders a Mako template by registry URI.

## Core flow (authoritative registry)
Inputs:
- `project_root`
- `template_id`
- input JSON dict (from file/stdin)

Steps:
1. `entry = env.get_entry(template_id)` (freshness check happens inside)
2. `Model = import_model(entry.model_import_path)`
3. `model = Model.model_validate(input_data)` (extra fields forbidden)
4. `uri = entry.template_uri` (validate URI)
5. `text = renderer.render_uri(uri, context=model.model_dump())`
6. If writing: `path = output.write(template_id, text, filename=...)`
7. Return/print `text`

## TemplateModel convenience API
Provide a base class:
- `template_id: ClassVar[str]`
- `.render(env, write=False, filename=None)`

Implementation must still:
- fetch entry from registry by `self.template_id`
- use registry template_uri (authoritative)

## Tests
- Extra fields rejected (Pydantic forbid).
- Registry change between renders changes behavior.
- `.render()` uses registry URI even if model declares its own URI.
