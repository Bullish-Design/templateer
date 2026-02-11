from __future__ import annotations

import pytest

import templateer.errors as errors
import templateer.uri as uri


def _uri_validation_error_type() -> type[Exception]:
    cls = getattr(errors, "TemplateURIValidationError", None)
    if cls is None or not isinstance(cls, type) or not issubclass(cls, Exception):
        pytest.fail("templateer.errors.TemplateURIValidationError must exist and subclass Exception")
    return cls


def test_validate_template_uri_accepts_valid_templates_path() -> None:
    validated = uri.validate_template_uri("templates/invoice/template.mako")

    assert validated == "templates/invoice/template.mako"


def test_validate_template_uri_rejects_parent_traversal_with_clear_error() -> None:
    error_type = _uri_validation_error_type()

    with pytest.raises(error_type) as exc_info:
        uri.validate_template_uri("../secrets.mako")

    message = str(exc_info.value).lower()
    assert ".." in message or "travers" in message
    assert "uri" in message


def test_validate_template_uri_rejects_absolute_path() -> None:
    error_type = _uri_validation_error_type()

    with pytest.raises(error_type):
        uri.validate_template_uri("/etc/passwd")


def test_validate_template_uri_rejects_backslash_paths() -> None:
    error_type = _uri_validation_error_type()

    with pytest.raises(error_type):
        uri.validate_template_uri(r"templates\\invoice\\template.mako")


def test_validate_template_uri_normalizes_and_enforces_templates_boundary() -> None:
    error_type = _uri_validation_error_type()

    normalized = uri.validate_template_uri("templates/a/../b/template.mako")
    assert normalized == "templates/b/template.mako"

    with pytest.raises(error_type):
        uri.validate_template_uri("templates/a/../../outside/template.mako")
