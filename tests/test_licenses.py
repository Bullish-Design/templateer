#!/usr/bin/env python3
import json
from pathlib import Path

import yaml
import reuse
from jinja2 import Environment


with open("copier.yml") as file:
    copier = yaml.safe_load(file)
licenses = {identifier: name for name, identifier in copier["copyright_license"]["choices"].items()}

with Path(reuse.__file__).parent.joinpath("resources", "licenses.json").open() as file:
    reuse_licenses = {ldata["licenseId"]: ldata["name"] for ldata in json.load(file)["licenses"]}

errors = []
for identifier, name in licenses.items():
    if identifier not in reuse_licenses:
        errors.append(f"License {identifier} is not supported by REUSE.")
    elif name != reuse_licenses[identifier]:
        errors.append(f"License {identifier} has a different name in REUSE: {name!r} != {reuse_licenses[identifier]!r}")

if errors:
    print(*errors, sep="\n")
    raise SystemExit(1)


env = Environment()
template = env.from_string(Path("templateer/templates/python_project/LICENSE.jinja").read_text())


for license in licenses:
    print(f"Testing license: {license}")
    rendered = template.render(
        project_name="Bullish-Design Testing",
        project_description="Testing this great template",
        author_fullname="Bullish Design",
        author_username="Bullish-Design",
        author_email="bullishdesignengineering@gmail.com",
        copyright_license=license,
        copyright_holder="Bullish Design",
        copyright_date="2025",
    )

    assert rendered, "License is empty!"
