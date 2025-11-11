from __future__ import annotations
from templateer import TemplateModel

TEMPLATE = '''"""{{ summary }}
{% if params %}

Args:
{% for param in params -%}
    {{ param }}
{% endfor %}
{% endif %}"""'''

class DocstringTemplate(TemplateModel):
    __template__ = TEMPLATE

    summary: str
    params: list[str] = []
