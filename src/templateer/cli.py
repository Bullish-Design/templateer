"""CLI entrypoint for Templateer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from templateer import __version__
from templateer.env import TemplateEnv
from templateer.errors import TemplateError
from templateer.output import write_generation_artifacts
from templateer.registry import build_registry_file, load_registry
from templateer.renderer import render_template_id


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


def _parse_json_object(raw_json: str) -> dict[str, object]:
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"input is not valid JSON ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object at the top level")

    return payload


def _generate_single(project_root: Path, template_id: str, payload: dict[str, object]) -> Path:
    env = TemplateEnv(project_root)
    rendered = render_template_id(env, template_id, payload)
    template_dir = project_root / "templates" / template_id
    gen_dir = template_dir / "gen"
    input_json = json.dumps(payload, indent=2) + "\n"
    return write_generation_artifacts(gen_dir, input_json, rendered)


def _generate_examples(project_root: Path, template_id: str) -> tuple[int, int]:
    env = TemplateEnv(project_root)
    template_dir = project_root / "templates" / template_id
    examples_jsonl = template_dir / "examples" / "sample_inputs.jsonl"
    success = 0
    failure = 0

    with examples_jsonl.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload = _parse_json_object(line)
                rendered = render_template_id(env, template_id, payload)
                input_json = json.dumps(payload, indent=2) + "\n"
                write_generation_artifacts(template_dir / "examples", input_json, rendered)
                success += 1
            except (TemplateError, ValueError) as exc:
                failure += 1
                print(f"line {line_number}: {exc}", file=sys.stderr)

    return success, failure


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
            payload = _parse_json_object(args.input_json)
            output_dir = _generate_single(Path(args.project_root), args.template_id, payload)
            print(output_dir)
            return 0

        if args.command == "generate-examples":
            success, failure = _generate_examples(Path(args.project_root), args.template_id)
            print(f"Processed examples: success={success}, failure={failure}")
            return 1 if failure else 0

        parser.print_help()
        return 0
    except (TemplateError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(app())
