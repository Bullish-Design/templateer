set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

python := "python"
project_root := "."

# Show available recipes
@default:
    just --list

# Build templates/registry.json from template manifests
build-registry:
    PYTHONPATH=src {{python}} -m templateer.cli registry build --project-root {{project_root}}

# Create a new template scaffold under templates/<template-id>/
create-template template_id model_import_path description="" tags="":
    {{python}} scripts/new_template.py \
      --project-root {{project_root}} \
      --template-id {{template_id}} \
      --model-import-path {{model_import_path}} \
      --description '{{description}}' \
      --tags '{{tags}}'

# Render examples for a specific template from templates/<id>/examples/sample_inputs.jsonl
run-template-examples template_id: build-registry
    PYTHONPATH=src {{python}} -m templateer.cli generate-examples --project-root {{project_root}} --template-id {{template_id}}

# Run the full test suite
run-tests:
    PYTHONPATH=src {{python}} -m pytest -q
