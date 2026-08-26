#!/usr/bin/env python3
"""
Detect two structural problems that documentation previously claimed were
checked but were not actually enforced anywhere in CI:

1. "Russian doll" duplication: a Federation package directory
   (Intelligence-Family-Federation, or Intelligence-Family-Federation-vX.Y.Z)
   nested *inside* another Federation package directory, instead of living
   as a sibling. This is how v1.3.1 ended up physically containing full
   copies of v1.3.0, which itself contained a full copy of v1.2.0.

2. Generated/distribution archives (*.zip, *.tar, *.tar.gz, *.tgz) committed
   into the source tree, which the release workflow is supposed to produce
   fresh, not carry as source.

Exit code 0 = clean. Exit code 1 = problems found.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(".").resolve()
EXCLUDED_DIR_PARTS = {".git", "dist", "node_modules"}

FEDERATION_DIR_RE = re.compile(
    r"^Intelligence-Family-Federation(-v\d+\.\d+\.\d+)?$"
)
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}


def relevant_dirs():
    for p in ROOT.rglob("*"):
        if p.is_dir() and FEDERATION_DIR_RE.match(p.name):
            if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
                continue
            yield p


def find_nested_federation_dirs() -> list[tuple[pathlib.Path, pathlib.Path]]:
    """Return (outer, inner) pairs where a Federation dir sits inside another."""
    dirs = sorted(relevant_dirs(), key=lambda p: len(p.parts))
    findings = []
    for outer in dirs:
        for inner in dirs:
            if inner == outer:
                continue
            try:
                inner.relative_to(outer)
            except ValueError:
                continue
            findings.append((outer, inner))
    return findings


def find_duplicate_files_within_nested_federations() -> dict[tuple[str, str], list[pathlib.Path]]:
    """Find identical files only where nested Federation copies exist.

    Historical/versioned sibling packages may legitimately contain identical
    files. The integrity gate should not reject those normal copies; it should
    reject duplication caused by a Federation package being embedded inside
    another package.
    """
    groups: dict[tuple[str, str], list[pathlib.Path]] = defaultdict(list)
    nested = find_nested_federation_dirs()
    for _outer, inner in nested:
        for p in inner.rglob("*"):
            if not p.is_file():
                continue
            if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
                continue
            if p.suffix.lower() not in {".md", ".json", ".yml", ".yaml"}:
                continue
            try:
                digest = hashlib.sha256(p.read_bytes()).hexdigest()
            except OSError:
                continue
            groups[(p.name, digest)].append(p)
    return {k: v for k, v in groups.items() if len(v) > 1}


def find_archives() -> list[pathlib.Path]:
    found = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
            continue
        if p.suffix.lower() in ARCHIVE_SUFFIXES:
            found.append(p)
    return found

def main() -> int:
    problems: list[str] = []

    nested = find_nested_federation_dirs()
    if nested:
        problems.append(
            f"{len(nested)} nested Federation directory pair(s) found "
            "(a Federation package directory committed inside another one):"
        )
        for outer, inner in nested:
            problems.append(f"  - {inner}  is nested inside  {outer}")

    dup_groups = find_duplicate_files_within_nested_federations()
    if dup_groups:
        total_extra = sum(len(v) - 1 for v in dup_groups.values())
        problems.append(
            f"{len(dup_groups)} file group(s) duplicated inside nested Federation "
            f"trees across {total_extra} extra location(s):"
        )
        for (name, digest), paths in sorted(dup_groups.items()):
            problems.append(f"  - {name}  ({digest[:12]}...)")
            for p in paths:
                problems.append(f"      {p}")

    archives = find_archives()
    if archives:
        problems.append(f"{len(archives)} committed archive file(s) found in source tree:")
        for p in archives:
            problems.append(f"  - {p}")

    if problems:
        print("::error::Structural integrity problems detected:")
        for line in problems:
            print(line)
        print(
            "\nRelease packaging must not ship nested copies of prior "
            "Federation versions, and generated archives must not be "
            "committed to source control."
        )
        return 1

    print("No nested Federation directories, duplicate files, or committed archives found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
