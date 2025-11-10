# src/templateer/__init__.py
"""Templateer - A self-generating Pydantic ⇄ Jinja toolkit."""

from __future__ import annotations

from .core import TemplateModel
from .generator import autogen_models
from .settings import settings

__version__ = "0.1.0"
__all__ = ["TemplateModel", "autogen_models", "settings"]
