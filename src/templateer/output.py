"""Output helpers for writing generated template artifacts."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from templateer.services.metadata import RenderRunMetadata


def timestamp_label() -> str:
    """Return a UTC timestamp suitable for folder names."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def write_generation_artifacts(base_dir: Path, input_json: str, rendered_output: str) -> Path:
    """Write one generation record under a timestamped subdirectory.

    Files written:
    - ``input.json``
    - ``output.txt``
    """

    base_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(100):
        suffix = "" if attempt == 0 else f"-{attempt}"
        generation_dir = base_dir / f"{timestamp_label()}{suffix}"
        try:
            generation_dir.mkdir(parents=False, exist_ok=False)
            break
        except FileExistsError:
            continue
    else:
        raise FileExistsError(f"unable to create unique generation directory under {base_dir}")

    (generation_dir / "input.json").write_text(input_json, encoding="utf-8")
    (generation_dir / "output.txt").write_text(rendered_output, encoding="utf-8")
    return generation_dir


def persist_render_result(
    base_dir: Path,
    input_json: str,
    rendered_output: str,
    run_metadata: "RenderRunMetadata | None" = None,
) -> tuple[Path, "RenderRunMetadata | None"]:
    """Persist render artifacts and optionally enrich ``run_metadata``.

    Returns the created artifact directory and metadata with ``output_artifact_dir`` set
    when metadata was provided.
    """

    artifact_dir = write_generation_artifacts(base_dir, input_json, rendered_output)
    if run_metadata is None:
        return artifact_dir, None
    return artifact_dir, replace(run_metadata, output_artifact_dir=artifact_dir)
