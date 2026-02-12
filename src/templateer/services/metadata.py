"""Metadata models for template generation attempts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal


InputSourceKind = Literal["inline_json", "jsonl"]


@dataclass(frozen=True)
class RenderRunMetadata:
    """Per-run metadata that can be enriched as pipeline stages complete."""

    output_artifact_dir: Path | None = None


@dataclass(frozen=True)
class RenderAttemptMetadata:
    """Metadata for a single template render attempt."""

    template_id: str
    run_timestamp: datetime
    input_source_kind: InputSourceKind
    input_path: Path | None
    line_number: int | None
    output_artifact_path: Path | None
    success: bool
    error_type: str | None = None
    error_message: str | None = None
    error_details: str | None = None
    run_metadata: RenderRunMetadata | None = None


@dataclass(frozen=True)
class GenerationBatchResult:
    """Collection of render attempt metadata for one batch run."""

    attempts: tuple[RenderAttemptMetadata, ...]

    @property
    def total(self) -> int:
        return len(self.attempts)

    @property
    def success(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.success)

    @property
    def failure(self) -> int:
        return self.total - self.success
