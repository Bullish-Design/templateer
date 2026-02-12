from __future__ import annotations

from pathlib import Path



def test_step_05_readme_documents_current_commands_and_just_recipes() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command_name in ("registry build", "registry show", "generate", "generate-examples"):
        assert command_name in readme

    for recipe_name in ("just build-registry", "just create-template", "just run-template-examples", "just run-tests"):
        assert recipe_name in readme



def test_step_05_readme_troubleshooting_keywords_cover_required_failure_classes() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Troubleshooting" in readme
    assert "templates/registry.json" in readme
    assert "manifest.json" in readme
    assert "model import path" in readme
    assert "URI" in readme



def test_step_05_readme_mentions_service_layer_and_thin_adapters_guidance() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "templateer.services" in readme
    assert "Thin CLI wrappers" in readme
    assert "Thin scripts and `just` recipes" in readme
