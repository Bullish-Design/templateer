from __future__ import annotations

import pytest

from templateer.cli import app
from templateer.registry import build_registry, build_registry_file


def test_step_5_contracts_exist() -> None:
    assert callable(build_registry)
    assert callable(build_registry_file)


def test_step_5_cli_registry_commands_exist() -> None:
    with pytest.raises(SystemExit) as build_help:
        app(["registry", "build", "--help"])
    assert build_help.value.code == 0

    with pytest.raises(SystemExit) as show_help:
        app(["registry", "show", "--help"])
    assert show_help.value.code == 0


def test_step_5_cli_generation_command_names_exist() -> None:
    with pytest.raises(SystemExit) as gen_help:
        app(["generate", "--help"])
    assert gen_help.value.code == 0

    with pytest.raises(SystemExit) as gen_examples_help:
        app(["generate-examples", "--help"])
    assert gen_examples_help.value.code == 0
