"""
Creates a tiny Click-based CLI entry point.
"""

from __future__ import annotations

import datetime as _dt
from pydantic import BaseModel
from templateer import TemplateModel


class CliEntrypointTemplate(TemplateModel):
    __template__ = TEMPLATE

    package_name: str
    options: list[dict[str, str]] = []  # [{"flag": "--name", "help": "Name …"}]


TEMPLATE = """
#!/usr/bin/env python
\"\"\"CLI entry point for {{ package_name }}.

Auto-generated {{ _dt.datetime.utcnow().isoformat() }}.
\"\"\"

import click

{% for opt in options -%}
@click.option("{{ opt.flag }}", help="{{ opt.help }}")
{% endfor -%}
@click.command()
def main(**kwargs):
    \"\"\"Dispatches CLI calls.\"\"\"
    click.echo(kwargs)

if __name__ == "__main__":
    main()
"""
