from __future__ import annotations
from templateer import TemplateModel
from .docstring import DocstringTemplate


TEMPLATE = '''
def {{ func_name }}():
{{ docstring | indent(4, true) }}
{{ body | indent(4, true) }}
'''



class FunctionWithDocsTemplate(TemplateModel):
    __template__ = TEMPLATE

    func_name: str
    docstring: DocstringTemplate
    body: str = "pass"
