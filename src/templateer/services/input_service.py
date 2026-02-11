"""Input parsing/validation helpers used by CLI and scripts."""

from __future__ import annotations

import json


def parse_json_object(raw_json: str) -> dict[str, object]:
    """Parse a JSON string and enforce object-at-top-level semantics."""

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"input is not valid JSON ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object at the top level")

    return payload
