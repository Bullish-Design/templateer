"""Core TemplateModel class."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined
from pydantic import BaseModel

from .settings import settings


class JinjaEnvironment:
    """Jinja environment factory."""
    
    def __init__(self) -> None:
        project_root = settings.project_root
        template_root = project_root / ".templateer"
        
        self.env = Environment(
            loader=FileSystemLoader(str(template_root)),
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def from_string(self, template_str: str):
        """Create template from string."""
        return self.env.from_string(template_str)


# Global environment instance
jinja_env = JinjaEnvironment()


class TemplateModel(BaseModel):
    """Base class binding arbitrary data to a Jinja template string."""

    __template__: str
    __output__: str | None = None

    @property
    def _template_str(self) -> str:
        """Get template string from module."""
        module_path, _, var_name = self.__template__.rpartition(".")
        mod = __import__(module_path, fromlist=[var_name])
        return getattr(mod, var_name)

    @property
    def _jinja_template(self):
        """Get compiled Jinja template."""
        return jinja_env.from_string(self._template_str)

    @property
    def _output_path(self) -> Path:
        """Get output file path."""
        if self.__output__:
            filename = self.__output__
        else:
            base_name = self.__class__.__name__.removesuffix("Template")
            filename = f"{base_name.lower()}.py"
        
        return settings.template_output_dir / filename

    def render(self) -> str:
        """Render template with model data."""
        return self._jinja_template.render(**self.model_dump())

    def generate(self, write: bool = True) -> str:
        """Generate code and optionally write to file."""
        code = self.render()
        
        if write:
            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            self._output_path.write_text(code, encoding="utf-8")
        
        return code
