#!/usr/bin/env python3
"""
Confirm required governance files exist in the current (highest-version)
top-level Federation package directory.

The previous CI check hardcoded the version string
(`test -f Intelligence-Family-Federation-v1.3.1/SECURITY.md`), which
silently stops checking anything the moment the next version ships under
a new directory name, and gives no signal that it has gone stale. This
script finds the current top-level package automatically and fails loudly
if the expected files are missing from it.

"Top-level" deliberately excludes any Federation directory nested inside
another one — see detect_nested_duplication.py. If nesting exists, this
script picks the outermost/highest-version candidate and does not
inspect the nested copies (that's a separate problem, caught separately).
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(".").resolve()

FEDERATION_DIR_RE = re.compile(r"^Intelligence-Family-Federation(?:-v(\d+)\.(\d+)\.(\d+))?$")

REQUIRED_RELATIVE_PATHS = [
    "README.md",
    "SECURITY.md",
    "PRINCIPLES.md",
    "FEDERATION.md",
    "AGENT_AUTHORIZATION.md",
    "AGENT_REGISTRY.md",
    "CREDENTIAL_LIFECYCLE.md",
    "CONTRACT_VERSIONING.md",
]


def top_level_federation_dirs() -> list[pathlib.Path]:
    """Federation package directories at repo root, unversioned or versioned."""
    return [
        p for p in ROOT.iterdir()
        if p.is_dir() and FEDERATION_DIR_RE.match(p.name)
    ]


def version_key(path: pathlib.Path):
    m = FEDERATION_DIR_RE.match(path.name)
    if m.group(1) is None:
        return (-1, -1, -1)  # unversioned dir sorts before any versioned one
    return tuple(int(x) for x in m.groups()[0:3])


def main() -> int:
    candidates = top_level_federation_dirs()
    if not candidates:
        print("::error::No Intelligence-Family-Federation directory found at repo root.")
        return 1

    versioned = [p for p in candidates if version_key(p) != (-1, -1, -1)]
    target = max(versioned, key=version_key) if versioned else candidates[0]

    print(f"Checking governance files under current package: {target.name}")

    missing = []
    for rel in REQUIRED_RELATIVE_PATHS:
        if not (target / rel).is_file():
            missing.append(rel)

    if missing:
        print(f"::error::Missing required governance file(s) in {target.name}:")
        for m in missing:
            print(f"  - {m}")
        return 1

    print(f"All {len(REQUIRED_RELATIVE_PATHS)} required governance files present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
