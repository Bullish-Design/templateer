from __future__ import annotations

from templateer.importers import import_model, parse_model_input_json
from templateer.model import TemplateModel


class _Step6Model(TemplateModel):
    value: int


def test_step_6_contracts_exist() -> None:
    assert callable(import_model)
    assert callable(parse_model_input_json)
    assert TemplateModel is not None


def test_step_6_import_and_validation_smoke() -> None:
    model_cls = import_model("tests.test_dev_step_6:_Step6Model")
    instance = parse_model_input_json('{"value": 7}', model_cls)

    assert instance.value == 7
