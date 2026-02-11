# Scripts Conventions

This directory contains thin workflow entrypoints.

## Rules

- One script = one workflow.
- Scripts should only do argument parsing, basic I/O wiring, and exit codes.
- Business logic belongs in `templateer.services` modules.
- Script bootstrapping should use `scripts/_bootstrap.py` rather than duplicating path setup.

## Maintained scripts

- `new_template.py` → scaffold a template and rebuild `templates/registry.json`
- `demo_generate_from_jsonl.py` → run JSONL payloads through template rendering
- `dev_watch` → local test watcher helper
