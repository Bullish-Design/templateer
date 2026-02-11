"""Output helpers for writing generated template artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


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
