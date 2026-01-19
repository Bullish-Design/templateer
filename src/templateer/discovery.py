# src/templateer/discovery.py
"""Template discovery utilities."""

from __future__ import annotations

import sys
import importlib.util
import types
from pathlib import Path
from types import SimpleNamespace
from typing import Type
from uuid import uuid4

from .models import TemplateModel


def discover_templates(
    directory: str | Path = ".templateer",
    cleanup: bool = False,
) -> SimpleNamespace:
    """Discover all TemplateModel subclasses in a directory.

    Loads each .py file under `directory` into a unique synthetic package so that
    relative imports between template modules (e.g., `from .x import Y`)
    work correctly during discovery and type identities match at runtime.

    If `cleanup` is True, synthetic modules are removed from `sys.modules` after
    discovery to avoid keeping temporary entries, but this means class identities
    from discovered templates are not preserved across calls.
    """
    directory = Path(directory)
    if not directory.exists():
        return SimpleNamespace()

    templates: dict[str, Type[TemplateModel]] = {}

    original_path = sys.path.copy()
    # Use a unique package name per discovery call to avoid cross-call collisions
    PACKAGE_NAME = f"_templateer_pkg_{uuid4().hex}"

    added_modules: list[str] = []

    try:
        # Create a synthetic package rooted at the template directory so
        # intra-template relative imports resolve (e.g., from .foo import Bar).
        pkg = types.ModuleType(PACKAGE_NAME)
        pkg.__path__ = [str(directory)]  # type: ignore[attr-defined]
        sys.modules[PACKAGE_NAME] = pkg
        added_modules.append(PACKAGE_NAME)

        # Allow absolute imports that might rely on the parent being importable.
        sys.path.insert(0, str(directory.parent))

        # Find all .py files (excluding private files)
        py_files = [f for f in directory.rglob("*.py") if not f.name.startswith("_")]

        loaded_modules: list[types.ModuleType] = []
        failed_files: set[Path] = set()

        # Multi-pass loading: retry files that failed due to missing dependencies
        # until we can't load any more modules
        max_passes = 10
        for _ in range(max_passes):
            progress_made = False
            remaining_files = [f for f in py_files if f not in failed_files]

            for py_file in remaining_files:
                if py_file in failed_files:
                    continue

                # Module name under our synthetic package (supports nested dirs)
                relative = py_file.relative_to(directory)
                module_name = ".".join((PACKAGE_NAME, *relative.with_suffix("").parts))

                # Skip if already loaded
                if module_name in sys.modules:
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    if not spec or not spec.loader:
                        failed_files.add(py_file)
                        continue

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    added_modules.append(module_name)
                    try:
                        spec.loader.exec_module(module)
                    except Exception as exc:
                        raise ImportError(
                            f"Failed to import template module from {py_file}"
                        ) from exc
                    loaded_modules.append(module)
                    progress_made = True
                except ImportError:
                    # File failed to import - will retry on next pass
                    failed_files.add(py_file)
                    pass

            # If no modules loaded this pass, we're done
            if not progress_made:
                break

        # Collect TemplateModel subclasses from all loaded modules
        for module in loaded_modules:
            try:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, TemplateModel) and attr is not TemplateModel:
                        templates[attr.__name__] = attr
            except Exception:
                continue
    finally:
        # Restore sys.path but keep the synthetic package in sys.modules to
        # preserve class identities across instances/validation unless cleanup
        # is requested.
        sys.path = original_path
        if cleanup:
            for module_name in reversed(added_modules):
                sys.modules.pop(module_name, None)

    return SimpleNamespace(**templates)
