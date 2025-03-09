# Copier UV

[![ci](https://github.com/Bullish-Design/templateer/workflows/ci/badge.svg)](https://github.com/Bullish-Design/templateer/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://Bullish-Design.github.io/templateer/)

[Copier](https://github.com/copier-org/copier) template
for Python projects managed by [uv](https://github.com/astral-sh/uv).

This copier template is mainly for my own usage,
but feel free to try it out, or fork it!

## Features

- [uv](https://github.com/astral-sh/uv) setup, with pre-defined `pyproject.toml`
- Pre-configured tools for code formatting, quality analysis and testing:
  [ruff](https://github.com/charliermarsh/ruff),
  [mypy](https://github.com/python/mypy),
- Tests run with [pytest](https://github.com/pytest-dev/pytest) and plugins, with [coverage](https://github.com/nedbat/coveragepy) support
- Documentation built with [MkDocs](https://github.com/mkdocs/mkdocs)
  ([Material theme](https://github.com/squidfunk/mkdocs-material)
  and "autodoc" [mkdocstrings plugin](https://github.com/mkdocstrings/mkdocstrings))
- Cross-platform tasks with [duty](https://github.com/pawamoy/duty)
- Support for GitHub workflows
- Auto-generated `CHANGELOG.md` from Git (conventional) commits
- All licenses from [choosealicense.com](https://choosealicense.com/appendix/)
- Support for Insiders versions of projects 

## Quick setup and usage

Make sure all the
[requirements](https://Bullish-Design.github.io/templateer/requirements)
are met, then:

```bash
copier copy --trust "https://github.com/Bullish-Design/templateer.git" /path/to/your/new/project
```

Or even shorter:

```bash
copier copy --trust "gh:Bullish-Design/templateer" /path/to/your/new/project
```

See the [documentation](https://Bullish-Design.github.io/templateer)
for more details.
