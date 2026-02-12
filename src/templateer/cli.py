"""CLI entrypoint for Templateer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from templateer import __version__
from templateer.errors import TemplateError
from templateer.registry import build_registry_file, load_registry
from templateer.services.generation_service import generate_examples, generate_single
from templateer.services.input_service import parse_json_object


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

    generate_parser = subparsers.add_parser("generate", help="Render one template from input JSON")
    generate_parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")
    generate_parser.add_argument("--template-id", required=True, help="Template ID from templates/registry.json")
    generate_parser.add_argument("--input-json", required=True, help="JSON object string for template input")

    generate_examples_parser = subparsers.add_parser(
        "generate-examples",
        help="Render each sample input object from templates/<id>/examples/sample_inputs.jsonl",
    )
    generate_examples_parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")
    generate_examples_parser.add_argument("--template-id", required=True, help="Template ID from templates/registry.json")

    return parser



def app(argv: list[str] | None = None) -> int:
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

        if args.command == "generate":
            payload = parse_json_object(args.input_json)
            metadata = generate_single(Path(args.project_root), args.template_id, payload)
            if metadata.success:
                print(metadata.output_artifact_path)
                return 0
            print(metadata.error_message, file=sys.stderr)
            return 1

        if args.command == "generate-examples":
            batch = generate_examples(Path(args.project_root), args.template_id)
            print(f"Processed examples: success={batch.success}, failure={batch.failure}")
            return 1 if batch.failure else 0

        parser.print_help()
        return 0
    except (TemplateError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(app())
