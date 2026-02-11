# SKILLS.md — Output writing & logging

## Goal
Write rendered outputs safely and emit useful, grep-friendly logs.

## Output rules
- Directory: `output/<template_id>/` (create if missing)
- Filename:
  - if user supplies `filename`, it must be a *simple filename* (no `/`, `\`, or `..`)
  - prefix with UTC timestamp: `YYYYMMDD-HHMMSSZ_`
  - default name: `rendered.txt`
- Return the full output path.

## Logging rules
- Append-only file: `log/mpt.log` (create parent dir if needed)
- Each entry includes at least:
  - UTC timestamp
  - level
  - action (e.g., `render`, `registry_build`)
  - template_id (when applicable)
  - template_uri
  - model_import_path
  - output path (when applicable)
  - exception info (when applicable)

JSONL format works well:
- one JSON object per line
- stable keys help grep/jq usage

## Tests
- Output filename validation rejects path traversal.
- Timestamp prefix format correct.
- Log file is appended to, not overwritten.
