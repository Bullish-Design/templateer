from __future__ import annotations
from templateer import TemplateModel

TEMPLATE = '''\
def {{ func_name }}({{ params }}) -> {{ return_type }}:
{% if docstring %}
    """{{ docstring }}"""
{% endif %}
    {{ body }}
'''

class MyFunctionTemplate(TemplateModel):
    __template__ = TEMPLATE

    func_name: str
    params: str = ""
    return_type: str = "None"
    docstring: str | None = None
    body: str = "pass"
