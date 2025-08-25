"""Command line interface."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import click

from .core import TemplateModel
from .generator import autogen_models
from .settings import settings


@click.group()
@click.version_option()
def main() -> None:
    """Templateer - self-generating template toolkit."""
    pass


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def autogen(verbose: bool) -> None:
    """Generate Pydantic model stubs from templates."""
    generated = autogen_models(verbose=verbose)
    
    if not verbose:
        click.echo(f"Generated {len(generated)} model stubs")


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def generate(verbose: bool) -> None:
    """Generate stubs and render templates."""
    generated = autogen_models(verbose=verbose)
    
    if verbose:
        click.echo(f"Generated {len(generated)} model stubs")
    
    sys.path.insert(0, str(settings.project_root))
    
    rendered_count = 0
    for stub in settings.model_dir.glob("*_model.py"):
        mod_name = f"templateer.models.{stub.stem}"
        
        try:
            mod = importlib.import_module(mod_name)
            tmpl_cls = next(
                c for c in mod.__dict__.values()
                if (isinstance(c, type) 
                    and issubclass(c, TemplateModel) 
                    and c is not TemplateModel)
            )
            
            instance = tmpl_cls()
            instance.generate()
            rendered_count += 1
            
            if verbose:
                rel_path = instance._output_path.relative_to(
                    settings.project_root
                )
                click.echo(f"[templateer] rendered → {rel_path}")
                
        except Exception as exc:
            if verbose:
                click.echo(f"⚠️  {stub.stem} could not render: {exc}")
    
    if not verbose:
        click.echo(f"Rendered {rendered_count} templates")


if __name__ == "__main__":
    main()
