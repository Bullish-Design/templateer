# src/templateer/__init__.py
"""Templateer: Type-safe Jinja2 templates via Pydantic models."""

from .models import TemplateModel
from .discovery import discover_templates

__all__ = ["TemplateModel, discover_templates"]
