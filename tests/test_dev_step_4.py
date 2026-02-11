from __future__ import annotations

from templateer.env import TemplateEnv


def test_step_4_contracts_exist() -> None:
    assert TemplateEnv is not None


def test_step_4_env_registry_path_convention(tmp_path) -> None:
    env = TemplateEnv(tmp_path)
    assert env.registry_path == tmp_path / "templates" / "registry.json"
