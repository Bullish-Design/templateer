"""Pydantic model base class for template inputs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TemplateModel(BaseModel):
    """Base template input model with strict field validation."""

    model_config = ConfigDict(extra="forbid")
