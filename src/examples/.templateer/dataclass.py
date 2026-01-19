from __future__ import annotations
from templateer import TemplateModel



TEMPLATE = '''
from dataclasses import dataclass

@dataclass
class {{ class_name }}:
{% for name, field_type in fields.items() %}
    {{ name }}: {{ field_type }}
{% endfor %}
{% for method in methods %}
{{ method | indent(4, true) }}
{% endfor %}
'''


class DataclassTemplate(TemplateModel):
    __template__ = TEMPLATE

    class_name: str
    fields: dict[str, str]
    methods: list[str] = []
