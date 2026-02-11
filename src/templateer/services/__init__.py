"""Service-layer helpers for CLI/scripts orchestration."""

from templateer.services.generation_service import generate_examples, generate_single, process_jsonl_inputs
from templateer.services.input_service import parse_json_object
from templateer.services.runtime import resolve_project_root, template_dir
from templateer.services.scaffold_service import scaffold_template

__all__ = [
    "generate_single",
    "generate_examples",
    "parse_json_object",
    "process_jsonl_inputs",
    "resolve_project_root",
    "template_dir",
    "scaffold_template",
]
