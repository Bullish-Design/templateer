from __future__ import annotations

import os
import subprocess
import sys


def test_import_templateer() -> None:
    import templateer

    assert templateer.__version__


def test_cli_help() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [sys.executable, "-m", "templateer.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "Templateer CLI" in result.stdout
