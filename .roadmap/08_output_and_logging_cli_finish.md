# Step 8 — Output writing + logging + CLI finish

## Goal
Complete the MVP UX:
- `mpt render` writes to stdout by default
- `--write` writes timestamped files under `output/<template_id>/`
- all commands log to `log/mpt.log`

## Deliverables
- `templateer/output.py`
  - `validate_filename(name)` (no separators, no `..`)
  - `write_output(env, template_id, content, filename=None) -> Path`
- `templateer/logging_.py`
  - append-only log writer (JSONL or key=val)
- `templateer/cli.py`
  - commands: `registry build`, `registry show`, `render`, `render-uri`

## Tasks
- Output rules:
  - target dir `output/<template_id>/`
  - timestamp prefix `YYYYMMDD-HHMMSSZ_`
  - default filename `rendered.txt`
- CLI rules:
  - `--json -` reads stdin
  - non-zero exit codes on errors
  - concise stderr, detailed log
- Add end-to-end tests:
  - build registry
  - render sample template
  - write output file and assert naming

## Linux shortcuts
- `tail -f log/mpt.log`
- `ls -lt output/<id>/ | head`
- quick JSON injection: `printf '{"x":1}' | mpt render ... --json -`

## Acceptance criteria
- `mpt registry build` + `mpt render` cover the full MVP loop.
- logs include: timestamp, action, template_id, template_uri, model_import_path, output path (if any).
