from __future__ import annotations

import pytest

from templateer.errors import TemplateRenderError
from templateer.uri import validate_template_uri


def test_validate_template_uri_accepts_valid_uri() -> None:
    assert validate_template_uri("templates/invoice/template.mako") == "templates/invoice/template.mako"


def test_validate_template_uri_normalizes_dot_segments() -> None:
    assert (
        validate_template_uri("templates/invoice/./partials/../template.mako")
        == "templates/invoice/template.mako"
    )


def test_validate_template_uri_rejects_absolute() -> None:
    with pytest.raises(TemplateRenderError) as exc:
        validate_template_uri("/templates/invoice/template.mako")

    assert "cannot be absolute" in str(exc.value)
    assert "action=render" in str(exc.value)


def test_validate_template_uri_rejects_backslashes() -> None:
    with pytest.raises(TemplateRenderError) as exc:
        validate_template_uri(r"templates\\invoice\\template.mako", action="include")

    message = str(exc.value)
    assert "cannot contain backslashes" in message
    assert "action=include" in message


def test_validate_template_uri_rejects_traversal() -> None:
    with pytest.raises(TemplateRenderError) as exc:
        validate_template_uri("templates/../../secrets.mako")

    assert "cannot contain path traversal segments" in str(exc.value)


def test_validate_template_uri_rejects_non_templates_root() -> None:
    with pytest.raises(TemplateRenderError) as exc:
        validate_template_uri("shared/template.mako", action="build")

    message = str(exc.value)
    assert "must remain under templates/" in message
    assert "action=build" in message
