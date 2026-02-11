"""CLI entrypoint for Templateer."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from templateer import __version__
from templateer.errors import TemplateError
from templateer.registry import build_registry_file, load_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mpt", description="Templateer CLI")
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    subparsers = parser.add_subparsers(dest="command")

    registry_parser = subparsers.add_parser("registry", help="Registry operations")
    registry_subparsers = registry_parser.add_subparsers(dest="registry_command")

    registry_build = registry_subparsers.add_parser("build", help="Build templates/registry.json")
    registry_build.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")

    registry_show = registry_subparsers.add_parser("show", help="Show templates/registry.json")
    registry_show.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")

    return parser


def app(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.version:
            print(__version__)
            return 0

        if args.command == "registry" and args.registry_command == "build":
            registry_path = build_registry_file(args.project_root)
            print(registry_path)
            return 0

        if args.command == "registry" and args.registry_command == "show":
            registry_path = Path(args.project_root) / "templates" / "registry.json"
            registry = load_registry(registry_path)
            print(registry.model_dump_json(indent=2))
            return 0

        parser.print_help()
        return 0
    except TemplateError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(app())
