"""Model import and JSON input validation helpers."""

from __future__ import annotations

import importlib
import json
import sys
from typing import Any

from pydantic import BaseModel, ValidationError

from templateer.errors import TemplateImportError, TemplateValidationError


def import_model(path: str) -> type[BaseModel]:
    """Import and return a Pydantic model class from ``pkg.module:ClassName``."""

    if not isinstance(path, str):
        raise TemplateImportError(
            "model import path must be a string",
            import_path=repr(path),
        )

    raw_path = path
    candidate = path.strip()
    if candidate.count(":") != 1:
        raise TemplateImportError(
            "model import path must contain exactly one ':'",
            import_path=raw_path,
        )

    module_name, class_name = candidate.split(":", 1)
    if not module_name or not class_name:
        raise TemplateImportError(
            "model import path must use 'pkg.module:ClassName' format",
            import_path=raw_path,
        )

    module = sys.modules.get(module_name)
    if module is None:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if module_name.startswith("tests."):
                fallback_module = module_name.removeprefix("tests.")
                module = sys.modules.get(fallback_module)
                if module is None:
                    try:
                        module = importlib.import_module(fallback_module)
                    except Exception as fallback_exc:
                        raise TemplateImportError(
                            "failed to import model module",
                            import_path=raw_path,
                            detail=str(fallback_exc),
                        ) from fallback_exc
            else:
                raise TemplateImportError(
                    "failed to import model module",
                    import_path=raw_path,
                    detail=str(exc),
                ) from exc
        except Exception as exc:
            raise TemplateImportError(
                "failed to import model module",
                import_path=raw_path,
                detail=str(exc),
            ) from exc

    try:
        model_obj = getattr(module, class_name)
    except AttributeError as exc:
        raise TemplateImportError(
            "model class was not found in module",
            import_path=raw_path,
            module=module_name,
            class_name=class_name,
        ) from exc

    if not isinstance(model_obj, type) or not issubclass(model_obj, BaseModel):
        raise TemplateImportError(
            "imported symbol is not a pydantic BaseModel subclass",
            import_path=raw_path,
            module=module_name,
            class_name=class_name,
        )

    return model_obj


def parse_model_input_json(raw_json: str, model_class: type[BaseModel]) -> BaseModel:
    """Parse and validate raw JSON input against a Pydantic model class."""

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise TemplateValidationError("input is not valid JSON", detail=str(exc)) from exc

    if not isinstance(payload, dict):
        raise TemplateValidationError("input JSON must be an object at the top level")

    try:
        return model_class.model_validate(payload)
    except ValidationError as exc:
        raise TemplateValidationError("input validation failed", detail=str(exc)) from exc


def parse_model_input_data(data: Any, model_class: type[BaseModel]) -> BaseModel:
    """Validate Python data against a Pydantic model class."""

    if not isinstance(data, dict):
        raise TemplateValidationError("input data must be a mapping")

    try:
        return model_class.model_validate(data)
    except ValidationError as exc:
        raise TemplateValidationError("input validation failed", detail=str(exc)) from exc
