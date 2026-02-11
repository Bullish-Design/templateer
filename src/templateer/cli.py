"""CLI entrypoint for Templateer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mpt", description="Templateer CLI")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    return parser


def app(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print("templateer")
    return 0


if __name__ == "__main__":
    raise SystemExit(app())
