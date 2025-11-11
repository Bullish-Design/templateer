from __future__ import annotations
from pathlib import Path
from templateer import discover_templates


def main() -> None:
    base = Path(__file__).parent
    out = base / "example_output"
    out.mkdir(parents=True, exist_ok=True)

    templates = discover_templates(base / ".templateer")

    # Example 1: simple function from a single template
    f = templates.MyFunctionTemplate(
        func_name="greet",
        params="name: str",
        return_type="str",
        body='return f"Hello, {name}!"',
        docstring="Return a friendly greeting.",
    )
    f.write_to(out / "greet.py")

    # Example 2: composition — a function that embeds a docstring object
    doc = templates.DocstringTemplate(
        summary="Greet someone",
        params=["name: Person to greet"],
    )
    g = templates.FunctionWithDocsTemplate(
        func_name="greet_person",
        docstring=doc,
        body="print('Hello!')",
    )
    g.write_to(out / "greet_person.py")

    # Example 3: dataclass with a simple method
    d = templates.DataclassTemplate(
        class_name="Person",
        fields={"name": "str", "age": "int"},
        methods=["def greet(self) -> str:\n    return f'Hi, I am {self.name}'"],
    )
    d.write_to(out / "person.py")


if __name__ == "__main__":
    main()
