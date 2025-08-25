"""Configuration settings using Confidantic."""

from __future__ import annotations

from pathlib import Path

from confidantic import PluginRegistry
from confidantic import Settings
from confidantic import init_settings
from pydantic import Field


class TemplateerSettings(Settings):
    """Project-specific settings (override via env vars or .env)."""

    model_dir: Path = Field(
        default_factory=lambda: Path("templateer") / "models",
        alias="MODEL_DIR",
        description="Directory for generated *TemplateModel* stubs.",
    )

    template_output_dir: Path = Field(
        default_factory=lambda: Path("TEMPLATE_DIR"),
        alias="TEMPLATE_OUTPUT_DIR",
        description="Directory for files produced by generate().",
    )


def get_settings() -> TemplateerSettings:
    """Get or create settings singleton."""
    PluginRegistry.register(TemplateerSettings)
    settings = init_settings(PluginRegistry.build_class())
    
    # Ensure directories exist
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    (settings.model_dir / "__init__.py").touch(exist_ok=True)
    settings.template_output_dir.mkdir(parents=True, exist_ok=True)
    
    return settings


# Global settings instance
settings = get_settings()
