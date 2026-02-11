from __future__ import annotations

from pathlib import Path

import pytest

from templateer.errors import TemplateImportError, TemplateValidationError
from templateer.importers import import_model, parse_model_input_json
from templateer.model import TemplateModel


class LocalValidModel(TemplateModel):
    name: str


class NotAModel:
    pass


def test_import_model_good_path() -> None:
    model = import_model("tests.test_importers:LocalValidModel")
    assert model is LocalValidModel


def test_import_model_module_missing() -> None:
    with pytest.raises(TemplateImportError) as exc:
        import_model("doesnotexist_pkg.module:Anything")

    message = str(exc.value)
    assert "doesnotexist_pkg.module:Anything" in message
    assert "failed to import model module" in message


def test_import_model_class_missing() -> None:
    with pytest.raises(TemplateImportError) as exc:
        import_model("tests.test_importers:MissingClass")

    message = str(exc.value)
    assert "tests.test_importers:MissingClass" in message
    assert "not found" in message


def test_import_model_symbol_not_pydantic_model() -> None:
    with pytest.raises(TemplateImportError) as exc:
        import_model("tests.test_importers:NotAModel")

    message = str(exc.value)
    assert "tests.test_importers:NotAModel" in message
    assert "BaseModel" in message


def test_import_model_requires_exactly_one_colon() -> None:
    with pytest.raises(TemplateImportError):
        import_model("tests.test_importers.LocalValidModel")

    with pytest.raises(TemplateImportError):
        import_model("tests.test_importers:LocalValidModel:extra")


def test_parse_model_input_json_rejects_extra_fields() -> None:
    with pytest.raises(TemplateValidationError) as exc:
        parse_model_input_json('{"name":"ok","extra":"nope"}', LocalValidModel)

    message = str(exc.value).lower()
    assert "validation" in message
    assert "extra" in message


def test_parse_model_input_json_rejects_non_object() -> None:
    with pytest.raises(TemplateValidationError):
        parse_model_input_json('["not", "an", "object"]', LocalValidModel)
