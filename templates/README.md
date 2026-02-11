# Templates README.md

This directory contains all Templateer templates available to the user.

Each template should be in its own named folder (for example, `templates/greeting/`) and should include:

- `template.mako`
- `manifest.json`
- `README.md`
- `gen/` for timestamped single-generation runs
- `examples/sample_inputs.jsonl` for sample inputs

CLI behavior:

- `mpt generate --template-id <id> --input-json '<json object>'`
  - writes to `templates/<id>/gen/<timestamp>/input.json` and `output.txt`
- `mpt generate-examples --template-id <id>`
  - reads `templates/<id>/examples/sample_inputs.jsonl`
  - writes each rendered sample to `templates/<id>/examples/<timestamp>/input.json` and `output.txt`

Template files are copied to the appropriate location for external ingestion after CI/CD validation workflows complete.
