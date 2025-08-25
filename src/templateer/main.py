"""templateer – a **self‑generating** Pydantic ⇄ Jinja toolkit
=================================================================
This single‑file MVP now **integrates Confidantic** for configuration so all
paths (model directory, generated code directory, etc.) are driven by *typed*
settings that can be overridden via environment variables or `.env` files.

Key additions
-------------
* **TemplateerSettings** – a Confidantic mix‑in exposing two env‑driven paths:
  * ``MODEL_DIR`` → where auto‑generated model stubs live.
  * ``TEMPLATE_OUTPUT_DIR`` → where rendered code is written.
* **settings** – singleton created by ``confidantic.init_settings`` so every
  part of the library reads a *single* source of truth.

Everything else (template discovery, autogen, round‑trip tests) remains mostly
unchanged – they now reference ``settings.model_dir`` and
``settings.template_output_dir`` instead of hard‑coded paths.
"""

from __future__ import annotations

import os
import re
import runpy
import sys
import textwrap
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable

from confidantic import PluginRegistry, init_settings, Settings
from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta  # type: ignore
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# ---------------------------- Confidantic setup ----------------------------
# ---------------------------------------------------------------------------
class TemplateerSettings(Settings):
    """Project‑specific settings (override via env vars or .env)."""

    # Directory where auto‑generated Pydantic stubs will be written.
    model_dir: Path = Field(
        default_factory=lambda: Path("templateer") / "models",
        alias="MODEL_DIR",
        description="Directory for generated *TemplateModel* stubs.",
    )

    # Directory where rendered template outputs are stored.
    template_output_dir: Path = Field(
        default_factory=lambda: Path("TEMPLATE_DIR"),
        alias="TEMPLATE_OUTPUT_DIR",
        description="Directory for files produced by *TemplateModel.generate()*.",
    )


# Register the mix‑in *before* calling init_settings so it’s picked up
PluginRegistry.register(TemplateerSettings)
settings = init_settings(PluginRegistry.build_class())

# Ensure directories exist so downstream imports don’t fail
settings.model_dir.mkdir(parents=True, exist_ok=True)
(settings.model_dir / "__init__.py").touch(exist_ok=True)
settings.template_output_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# ----------------------- Jinja environment ---------------------------------
# ---------------------------------------------------------------------------
PROJECT_ROOT = settings.project_root
TEMPLATE_ROOT = PROJECT_ROOT / ".templateer"

ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_ROOT)),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


# ---------------------------------------------------------------------------
# ----------------------------- Core model ----------------------------------
# ---------------------------------------------------------------------------
class TemplateModel(BaseModel):
    """Base‑class binding arbitrary data to a Jinja *TEMPLATE* string."""

    # Dotted import path pointing to a ``TEMPLATE`` constant defined in a
    # module under ``.templateer`` (e.g. "example_template.TEMPLATE").
    __template__: str

    # Optional override for the output filename (relative to settings.template_output_dir)
    __output__: str | None = None

    # ------------------------------------------------------------------
    # Internals – subclasses generally don’t touch these
    # ------------------------------------------------------------------
    @property
    def _template_str(self) -> str:
        module_path, _, var_name = self.__template__.rpartition(".")
        mod = __import__(module_path, fromlist=[var_name])
        return getattr(mod, var_name)

    @property
    def _jinja_template(self):
        return ENV.from_string(self._template_str)

    @property
    def _output_path(self) -> Path:
        filename = (
            self.__output__
            or f"{self.__class__.__name__.removesuffix('Template').lower()}.py"
        )
        return settings.template_output_dir / filename

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def render(self) -> str:
        return self._jinja_template.render(**self.model_dump())

    def generate(self, write: bool = True) -> str:
        code = self.render()
        if write:
            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            self._output_path.write_text(code, encoding="utf-8")
        return code


# ---------------------------------------------------------------------------
# --------------------- Model stub autogeneration ---------------------------
# ---------------------------------------------------------------------------
_CAMEL_RE = re.compile(r"[_\-]([a-zA-Z])")


def _camelify(name: str) -> str:  # snake_or-kebab → CamelCase
    name = _CAMEL_RE.sub(lambda m: m.group(1).upper(), name)
    return name[:1].upper() + name[1:]


def _discover_template_modules() -> Iterable[Path]:
    return TEMPLATE_ROOT.glob("*.py")


def _extract_template_vars(template_str: str) -> set[str]:
    ast = ENV.parse(template_str)
    return meta.find_undeclared_variables(ast)


def _write_model_stub(module: ModuleType, template_attr: str, vars_: set[str]) -> Path:
    stem = module.__name__.split(".")[-1]
    class_name = f"{_camelify(stem)}Template"
    model_path = settings.model_dir / f"{stem}_model.py"
    if model_path.exists():  # don’t clobber user edits
        return model_path

    field_lines = (
        "\n".join(f"    {v}: Any | None = None" for v in sorted(vars_)) or "    pass"
    )

    stub = textwrap.dedent(
        f"""from __future__ import annotations

from typing import Any
from templateer import TemplateModel


class {class_name}(TemplateModel):
    \"\"\"Auto‑generated from .templateer/{stem}.py\"\"\"
    __template__ = \"{module.__name__}.{template_attr}\"

{field_lines}
"""
    )
    model_path.write_text(stub, encoding="utf-8")
    return model_path


def autogen_models(verbose: bool = False) -> list[Path]:
    """Generate missing Pydantic stubs for every `TEMPLATE` under `.templateer`."""
    generated: list[Path] = []
    sys.path.insert(0, str(TEMPLATE_ROOT))  # import helper modules directly
    for tpl_py in _discover_template_modules():
        mod = runpy.run_path(tpl_py)["__loader__"].load_module()  # type: ignore[attr-defined]
        if not hasattr(mod, "TEMPLATE"):
            continue
        vars_ = _extract_template_vars(mod.TEMPLATE)
        model_path = _write_model_stub(mod, "TEMPLATE", vars_)
        if verbose:
            print(f"[templateer] model stub → {model_path.relative_to(PROJECT_ROOT)}")
        generated.append(model_path)
    return generated


# ---------------------------------------------------------------------------
# ---------------------- Simple command‑line shim ---------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Templateer – self‑generating template toolkit"
    )
    p.add_argument(
        "--autogen",
        action="store_true",
        help="Only generate Pydantic stubs, don’t render templates.",
    )
    p.add_argument(
        "--generate",
        action="store_true",
        help="Generate stubs *and* render each template once.",
    )
    args = p.parse_args()

    if args.autogen:
        autogen_models(verbose=True)
    elif args.generate:
        autogen_models(verbose=True)
        sys.path.insert(0, str(PROJECT_ROOT))
        import importlib

        for stub in settings.model_dir.glob("*_model.py"):
            mod = importlib.import_module(
                f"{TemplateerSettings.__module__}.models.{stub.stem}"
            )
            tmpl_cls = next(
                c
                for c in mod.__dict__.values()
                if isinstance(c, type)
                and issubclass(c, TemplateModel)
                and c is not TemplateModel
            )
            try:
                instance = tmpl_cls()
                outfile = instance.generate()
                print(
                    f"[templateer] rendered → {Path(outfile).relative_to(PROJECT_ROOT)}"
                )
            except Exception as exc:
                print(f"⚠️  {tmpl_cls.__name__} could not render: {exc}")
    else:
        p.print_help()


# ---------------------------------------------------------------------------
# -------------------------- Round‑trip tests -------------------------------
# ---------------------------------------------------------------------------
if "pytest" in sys.modules:
    import importlib.util
    import pytest  # type: ignore
    from tree_sitter_languages import get_language  # type: ignore
    from pydantree import Parser, ParsedDocument

    PY_LANGUAGE = get_language("python")
    TS_PARSER = Parser(PY_LANGUAGE)

    @pytest.fixture(scope="session", autouse=True)
    def _bootstrap(tmp_path_factory):
        # Use *temp* dirs so tests don’t touch real workspace
        global settings  # noqa: PLW0603
        temp_models = tmp_path_factory.mktemp("models")
        temp_out = tmp_path_factory.mktemp("generated")
        os.environ["MODEL_DIR"] = str(temp_models)
        os.environ["TEMPLATE_OUTPUT_DIR"] = str(temp_out)
        settings = init_settings(PluginRegistry.build_class(), _force_reload=True)  # type: ignore[arg-type]
        autogen_models()
        sys.path.insert(0, str(temp_models))
        for stub in temp_models.glob("*_model.py"):
            spec = importlib.util.spec_from_file_location(stub.stem, stub)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            spec.loader.exec_module(mod)  # type: ignore[arg-type]
            tmpl_cls = next(
                c
                for c in mod.__dict__.values()
                if isinstance(c, type)
                and issubclass(c, TemplateModel)
                and c is not TemplateModel
            )
            tmpl_cls().generate()
        yield

    def test_generated_syntax():
        for py in Path(os.environ["TEMPLATE_OUTPUT_DIR"]).glob("*.py"):
            txt = py.read_text()
            doc = ParsedDocument(text=txt, parser=TS_PARSER)
            assert doc.root.type_name == "module"

    def test_generated_imports():
        for py in Path(os.environ["TEMPLATE_OUTPUT_DIR"]).glob("*.py"):
            spec = importlib.util.spec_from_file_location(py.stem, py)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            spec.loader.exec_module(mod)  # type: ignore[arg-type]
