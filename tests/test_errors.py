from __future__ import annotations

import templateer.errors as errors


def test_required_error_classes_are_importable() -> None:
    assert hasattr(errors, "TemplateerError")
    assert hasattr(errors, "TemplateURIValidationError")

    assert issubclass(errors.TemplateerError, Exception)
    assert issubclass(errors.TemplateURIValidationError, errors.TemplateerError)


def test_error_messages_include_actionable_context_when_provided() -> None:
    err = errors.TemplateURIValidationError(
        "Template URI is invalid",
        uri="templates/../secrets.mako",
        action="render",
    )

    message = str(err)
    assert "Template URI is invalid" in message
    assert "templates/../secrets.mako" in message
    assert "render" in message
