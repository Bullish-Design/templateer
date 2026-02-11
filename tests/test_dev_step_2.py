from __future__ import annotations

import pytest

import templateer.errors as errors
import templateer.uri as uri


REQUIRED_EXCEPTION_CLASSES = [
    "TemplateerError",
    "TemplateURIValidationError",
]


def test_step_2_expected_exception_classes_exist() -> None:
    for class_name in REQUIRED_EXCEPTION_CLASSES:
        cls = getattr(errors, class_name)
        assert isinstance(cls, type)
        assert issubclass(cls, Exception)


def test_step_2_validate_template_uri_exists() -> None:
    assert hasattr(uri, "validate_template_uri")
    assert callable(uri.validate_template_uri)


def test_step_2_representative_uri_acceptance_criteria() -> None:
    assert uri.validate_template_uri("templates/invoice/template.mako") == "templates/invoice/template.mako"
    assert uri.validate_template_uri("templates/a/../b/template.mako") == "templates/b/template.mako"

    with pytest.raises(errors.TemplateURIValidationError):
        uri.validate_template_uri("../secrets.mako")

    with pytest.raises(errors.TemplateURIValidationError):
        uri.validate_template_uri("/absolute/path.mako")

    with pytest.raises(errors.TemplateURIValidationError):
        uri.validate_template_uri(r"templates\\invoice\\template.mako")
