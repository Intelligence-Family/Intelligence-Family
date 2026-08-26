#!/usr/bin/env python3
"""
Validate every *.schema.json file in the repository as a well-formed
JSON Schema (Draft 2020-12), and validate any instance documents that
declare themselves against one of those schemas.

This replaces the previously-claimed-but-never-shipped "JSON contract
validation" step referenced in RELEASE_NOTES.md (v1.3.0) and
ADR 0004 / RELEASE_NOTES_v1.3.1.md.

Exit code 0 = all schemas well-formed and all discovered instances valid.
Exit code 1 = at least one problem found.
"""

from __future__ import annotations

import json
import pathlib
import sys

try:
    import jsonschema
    from jsonschema.validators import validator_for
except ImportError:
    print("::error::jsonschema package is required (pip install jsonschema)")
    sys.exit(1)

ROOT = pathlib.Path(".").resolve()

# Directories we never want to walk into for this check.
EXCLUDED_DIR_PARTS = {".git", "dist", "node_modules"}


def iter_files(suffix_predicate):
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
            continue
        if suffix_predicate(p):
            yield p


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    except UnicodeDecodeError as exc:
        return None, f"invalid UTF-8: {exc}"


def main() -> int:
    problems: list[str] = []
    schema_files = sorted(iter_files(lambda p: p.name.endswith(".schema.json")))

    if not schema_files:
        print("::warning::No *.schema.json files found — nothing to validate.")
        return 0

    schemas_by_id: dict[str, tuple[pathlib.Path, dict]] = {}

    print(f"Found {len(schema_files)} schema file(s).")

    for path in schema_files:
        data, err = load_json(path)
        if err:
            problems.append(f"{path}: {err}")
            continue

        # Confirm this is actually a JSON Schema and that it is internally
        # self-consistent for the draft it declares (or the latest draft
        # if undeclared). This is the check that was previously missing:
        # a *.schema.json file existing is not the same as it being valid.
        try:
            cls = validator_for(data)
            cls.check_schema(data)
        except jsonschema.exceptions.SchemaError as exc:
            problems.append(f"{path}: schema is not a valid JSON Schema: {exc.message}")
            continue

        schema_id = data.get("$id") or str(path)
        if schema_id in schemas_by_id:
            other_path = schemas_by_id[schema_id][0]
            problems.append(
                f"{path}: duplicate $id '{schema_id}' also used by {other_path}"
            )
        schemas_by_id[schema_id] = (path, data)
        print(f"  OK  {path}  (title: {data.get('title', 'untitled')})")

    # Validate any instance documents that opt in via "$schema" pointing at
    # one of our schema $ids, or via a sibling "schemaRef" field. Today the
    # repository ships no populated registry/contract instances, so this
    # loop is expected to find zero candidates — but it is real code that
    # will fire the moment someone adds
    # docs/registry/<agent>.json or similar, rather than silently doing
    # nothing forever.
    instance_files = sorted(
        iter_files(lambda p: p.suffix == ".json" and not p.name.endswith(".schema.json"))
    )
    checked_instances = 0

    for path in instance_files:
        data, err = load_json(path)
        if err:
            problems.append(f"{path}: {err}")
            continue

        schema_ref = None
        if isinstance(data, dict):
            schema_ref = data.get("$schema") or data.get("schemaRef")
        if not schema_ref or schema_ref not in schemas_by_id:
            continue

        schema_path, schema_data = schemas_by_id[schema_ref]
        try:
            jsonschema.validate(instance=data, schema=schema_data)
            checked_instances += 1
            print(f"  OK  {path}  validates against {schema_path}")
        except jsonschema.exceptions.ValidationError as exc:
            problems.append(f"{path}: fails validation against {schema_path}: {exc.message}")

    print(f"Instance documents validated: {checked_instances}")

    if problems:
        print("::error::Schema validation failures:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("All schemas well-formed; all discovered instances valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
