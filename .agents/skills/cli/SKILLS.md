# SKILLS.md — CLI command surface (`mpt`)

## Goal
Expose a Unix-friendly CLI matching the concept, delegating all core logic to the library.

## Commands
- `mpt registry build --project-root <path>`
- `mpt registry show --project-root <path>`
- `mpt render <template_id> --project-root <path> --json <file|-> [--write] [--filename name.txt]`
- `mpt render-uri <template_uri> --project-root <path> --json <file|-> [--write] [--filename name.txt]`

## Behaviors
- `--json -` reads stdin; otherwise read file.
- Default prints rendered output to stdout.
- `--write` additionally writes to `output/<template_id>/...` (or for render-uri, derive template_id from the URI folder if possible; otherwise require an explicit id).
- Errors:
  - concise message to stderr
  - non-zero exit code
  - detailed info goes to log

## Tests
- CLI smoke tests using subprocess with temp project roots.
- stdin reading test for `--json -`.
