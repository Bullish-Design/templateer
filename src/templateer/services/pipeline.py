"""Composable generation pipeline stages."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from templateer.env import TemplateEnv
from templateer.importers import import_model, parse_model_input_data
from templateer.output import persist_render_result, write_generation_artifacts
from templateer.registry import TemplateEntry
from templateer.renderer import render_uri
from templateer.services.metadata import RenderRunMetadata


def resolve_registry_entry(env: TemplateEnv, template_id: str) -> TemplateEntry:
    """Resolve a template entry by ``template_id`` from the registry."""

    return env.get_entry(template_id)


def validate_payload_with_model_import_path(
    payload: Mapping[str, Any],
    model_import_path: str,
) -> dict[str, Any]:
    """Validate payload with the configured model and return render context."""

    model_class = import_model(model_import_path)
    model = parse_model_input_data(dict(payload), model_class)
    return model.model_dump()


def render_template_uri(env: TemplateEnv, template_uri: str, context: Mapping[str, Any]) -> str:
    """Render a template URI using the provided context."""

    return render_uri(env, template_uri, dict(context))


def persist_artifacts(base_dir: Path, payload: Mapping[str, Any], rendered_output: str) -> Path:
    """Write generation artifacts and return the created output directory."""

    input_json = json.dumps(dict(payload), indent=2) + "\n"
    return write_generation_artifacts(base_dir, input_json, rendered_output)


def persist_artifacts_with_metadata(
    base_dir: Path,
    payload: Mapping[str, Any],
    rendered_output: str,
    run_metadata: RenderRunMetadata | None = None,
) -> tuple[Path, RenderRunMetadata | None]:
    """Write artifacts and optionally return enriched run metadata."""

    input_json = json.dumps(dict(payload), indent=2) + "\n"
    return persist_render_result(base_dir, input_json, rendered_output, run_metadata)
