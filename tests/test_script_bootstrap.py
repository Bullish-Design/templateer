from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_bootstrap_module(path: Path):
    spec = importlib.util.spec_from_file_location("script_bootstrap", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load bootstrap module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_can_resolve_repo_root_and_src_path() -> None:
    module = _load_bootstrap_module(Path("scripts/_bootstrap.py"))
    repo_root = module.ensure_src_on_syspath()

    assert repo_root == Path.cwd().resolve()
    assert (repo_root / "src").exists()
