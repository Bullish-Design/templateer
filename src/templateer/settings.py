# src/templateer/settings.py
"""Configuration settings with dotenv support."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field

# Load .env file if it exists
load_dotenv()


class TemplateerSettings(BaseModel):
    """Project-specific settings (override via env vars or .env)."""

    model_dir: Path = Field(default_factory=lambda: Path(os.getenv("MODEL_DIR", "templateer/models")))

    template_output_dir: Path = Field(default_factory=lambda: Path(os.getenv("TEMPLATE_OUTPUT_DIR", "TEMPLATE_DIR")))

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path.cwd()


# Global settings instance
settings = TemplateerSettings()

# Ensure directories exist
settings.model_dir.mkdir(parents=True, exist_ok=True)
(settings.model_dir / "__init__.py").touch(exist_ok=True)
settings.template_output_dir.mkdir(parents=True, exist_ok=True)
