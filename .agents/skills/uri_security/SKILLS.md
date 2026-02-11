# SKILLS.md — URI validation & template sandboxing

## Goal
Enforce that all template and include targets are **root-relative URIs** under `templates/**`, preventing escape via `..` or absolute paths.

## Policy (must hold everywhere)
A valid template URI:
- Uses forward slashes (`/`) only
- Is not absolute (`/x` or `C:\...` style)
- Starts with `templates/`
- Normalizes without producing any `..` segment
- Does not contain backslashes

This is an **URI policy**, not a filesystem realpath policy. Do not resolve symlinks.

## Recommended implementation
Create utilities in `uri.py`:

- `normalize_uri(uri: str) -> str`
  - strip whitespace
  - reject backslashes
  - use `posixpath.normpath`
  - convert `.` to normalized form
- `validate_template_uri(uri: str) -> str`
  - call normalize
  - reject absolute
  - require prefix `templates/`
  - reject `..` after normalization (and also if input contains it)
  - return normalized uri

- `validate_include_uri(requesting_template_id: str, include_uri: str) -> str`
  - include must still be under `templates/**`
  - additionally, include must be within:
    - `templates/_shared/`
    - OR `templates/<template_id>/`

## Where to enforce
- Registry validation: validate `template_uri` on load
- Runtime rendering: validate render target URI before loading template
- Mako include resolution: validate every include URI (see Mako skill)

## Tests
- Good:
  - `templates/invoice/template.mako`
  - `templates/_shared/header.mako`
- Bad:
  - `../templates/x.mako`
  - `templates/../secrets.mako`
  - `/etc/passwd`
  - `templates\x.mako`
