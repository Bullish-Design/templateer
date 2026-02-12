from __future__ import annotations

from pathlib import Path

from templateer.output import persist_render_result
from templateer.services.metadata import RenderRunMetadata


def test_persist_render_result_preserves_artifact_file_names(tmp_path: Path) -> None:
    run_metadata = RenderRunMetadata()

    artifact_dir, updated_metadata = persist_render_result(
        tmp_path,
        '{"name":"Ada"}\n',
        'Hello Ada!\n',
        run_metadata,
    )

    assert artifact_dir.is_dir()
    assert (artifact_dir / 'input.json').read_text(encoding='utf-8') == '{"name":"Ada"}\n'
    assert (artifact_dir / 'output.txt').read_text(encoding='utf-8') == 'Hello Ada!\n'

    assert updated_metadata is not None
    assert updated_metadata.output_artifact_dir == artifact_dir
