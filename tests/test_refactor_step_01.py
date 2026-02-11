from __future__ import annotations

from pathlib import Path

from templateer.services.runtime import resolve_project_root


def test_step_01_justfile_is_thin_and_standardized() -> None:
    justfile = Path("Justfile").read_text(encoding="utf-8")

    assert "python - <<" not in justfile
    assert "create-template" in justfile
    assert "PYTHONPATH=src {{python}} scripts/new_template.py" in justfile
    assert "--project-root {{project_root}}" in justfile


def test_step_01_cli_command_names_are_documented() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for command_name in ("registry build", "registry show", "generate", "generate-examples"):
        assert command_name in readme


def test_step_01_runtime_bootstrap_resolves_absolute_root(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)

    resolved = resolve_project_root(nested)
    assert resolved.is_absolute()
    assert resolved == nested.resolve()
