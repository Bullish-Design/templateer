"""Demo models used by example templates under ``templates/``."""

from __future__ import annotations

from templateer.model import TemplateModel


class GreetingModel(TemplateModel):
    """Input schema for ``templates/greeting/template.mako``."""

    name: str
    title: str | None = None


class EmailTemplateModel(TemplateModel):
    """Input schema for ``templates/email_with_shared_header/template.mako``."""

    from_name: str
    from_email: str
    to_name: str
    to_email: str
    subject: str
    body: str
