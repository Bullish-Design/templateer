"""Model stub autogeneration functionality."""

from __future__ import annotations

import re
import runpy
import sys
import textwrap
from pathlib import Path
from types import ModuleType
from typing import Iterable

from jinja2 import meta

from .core import jinja_env
from .settings import settings


class ModelGenerator:
    """Generates Pydantic model stubs from template modules."""

    def __init__(self) -> None:
        self.project_root = settings.project_root
        self.template_root = self.project_root / ".templateer"
        self.camel_re = re.compile(r"[_\-]([a-zA-Z])")

    def camelify(self, name: str) -> str:
        """Convert snake_or-kebab → CamelCase."""
        name = self.camel_re.sub(lambda m: m.group(1).upper(), name)
        return name[:1].upper() + name[1:]

    def discover_template_modules(self) -> Iterable[Path]:
        """Find all Python files in template root."""
        return self.template_root.glob("*.py")

    def extract_template_vars(self, template_str: str) -> set[str]:
        """Extract undeclared variables from Jinja template."""
        ast = jinja_env.env.parse(template_str)
        return meta.find_undeclared_variables(ast)

    def write_model_stub(
        self, 
        module: ModuleType, 
        template_attr: str, 
        vars_: set[str]
    ) -> Path:
        """Write Pydantic model stub to file."""
        stem = module.__name__.split(".")[-1]
        class_name = f"{self.camelify(stem)}Template"
        model_path = settings.model_dir / f"{stem}_model.py"
        
        if model_path.exists():
            return model_path  # Don't overwrite user edits

        field_lines = "\n".join(
            f"    {v}: Any | None = None" for v in sorted(vars_)
        ) or "    pass"

        stub = textwrap.dedent(
            f"""\
            from __future__ import annotations

            from typing import Any

            from templateer import TemplateModel


            class {class_name}(TemplateModel):
                \"\"\"Auto-generated from .templateer/{stem}.py\"\"\"
                __template__ = \"{module.__name__}.{template_attr}\"

            {field_lines}
            """
        )
        
        model_path.write_text(stub, encoding="utf-8")
        return model_path

    def autogen_models(self, verbose: bool = False) -> list[Path]:
        """Generate missing Pydantic stubs for every TEMPLATE."""
        generated: list[Path] = []
        sys.path.insert(0, str(self.template_root))
        
        for tpl_py in self.discover_template_modules():
            mod = runpy.run_path(tpl_py)["__loader__"].load_module()
            
            if not hasattr(mod, "TEMPLATE"):
                continue
                
            vars_ = self.extract_template_vars(mod.TEMPLATE)
            model_path = self.write_model_stub(mod, "TEMPLATE", vars_)
            
            if verbose:
                rel_path = model_path.relative_to(self.project_root)
                print(f"[templateer] model stub → {rel_path}")
                
            generated.append(model_path)
        
        return generated


# Convenience instance
generator = ModelGenerator()
autogen_models = generator.autogen_models
