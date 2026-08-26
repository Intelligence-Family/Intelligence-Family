#!/usr/bin/env python3
"""
Flatten the "Russian doll" Federation directory structure, where each
version folder was committed containing a full nested copy of the
previous version's folder (v1.3.1/Intelligence-Family-Federation-v1.3.0/
containing v1.3.1/Intelligence-Family-Federation-v1.3.0/Intelligence-
Family-Federation-v1.2.0/, and so on).

Safety model:
  * DEFAULT is a dry run. Nothing is deleted unless you pass --apply.
  * A nested copy is only deleted automatically if it is a BYTE-FOR-BYTE
    duplicate of the corresponding top-level (canonical) directory of the
    same version.
  * If a nested copy differs from its canonical counterpart (someone
    edited the nested copy and not the canonical one, or vice versa),
    the script does NOT delete it — it prints a WARNING with both paths
    so a human can decide which content is actually current.
  * If a version referenced by a nested copy has no canonical top-level
    counterpart at all (e.g. an old version that was only ever nested),
    the script does NOT delete it either — it prints a WARNING, since
    deleting it would be the only copy of that content, not a duplicate.

Usage:
    python3 flatten_federation_tree.py            # dry run, report only
    python3 flatten_federation_tree.py --apply     # actually delete

Run from the repository root.
"""

from __future__ import annotations

import argparse
import filecmp
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(".").resolve()
FEDERATION_DIR_RE = re.compile(r"^Intelligence-Family-Federation(-v\d+\.\d+\.\d+)?$")
EXCLUDED_DIR_PARTS = {".git", "dist", "node_modules"}


def all_federation_dirs() -> list[pathlib.Path]:
    dirs = []
    for p in ROOT.rglob("*"):
        if p.is_dir() and FEDERATION_DIR_RE.match(p.name):
            if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
                continue
            dirs.append(p)
    return dirs


def is_top_level(path: pathlib.Path, all_dirs: list[pathlib.Path]) -> bool:
    """True if no other Federation dir in the set is an ancestor of `path`."""
    for other in all_dirs:
        if other == path:
            continue
        try:
            path.relative_to(other)
            return False
        except ValueError:
            continue
    return True


def dirs_are_identical(a: pathlib.Path, b: pathlib.Path) -> tuple[bool, list[str]]:
    """Recursively compare two directories. Returns (identical, differences)."""
    diffs: list[str] = []
    cmp = filecmp.dircmp(a, b)

    if cmp.left_only:
        diffs.append(f"only in {a}: {sorted(cmp.left_only)}")
    if cmp.right_only:
        diffs.append(f"only in {b}: {sorted(cmp.right_only)}")
    if cmp.diff_files:
        diffs.append(f"content differs: {sorted(cmp.diff_files)} (between {a} and {b})")
    if cmp.funny_files:
        diffs.append(f"could not compare: {sorted(cmp.funny_files)}")

    for common_dir in cmp.common_dirs:
        sub_identical, sub_diffs = dirs_are_identical(a / common_dir, b / common_dir)
        diffs.extend(sub_diffs)

    return (len(diffs) == 0), diffs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually delete confirmed-duplicate nested directories. "
             "Without this flag, only a report is printed.",
    )
    args = parser.parse_args()

    all_dirs = all_federation_dirs()
    top_level = {p.name: p for p in all_dirs if is_top_level(p, all_dirs)}
    nested = [p for p in all_dirs if p not in top_level.values()]

    if not nested:
        print("No nested Federation directories found. Nothing to flatten.")
        return 0

    print(f"Found {len(top_level)} top-level Federation package(s): "
          f"{', '.join(sorted(top_level))}")
    print(f"Found {len(nested)} nested Federation directory instance(s) to evaluate.\n")

    to_delete: list[pathlib.Path] = []
    warnings: list[str] = []

    # Evaluate deepest paths first so that once an outer nested dir is
    # deleted, we don't also try to individually evaluate things inside it.
    nested_sorted = sorted(nested, key=lambda p: len(p.parts))

    already_handled: set[pathlib.Path] = set()

    for nested_dir in nested_sorted:
        if any(nested_dir.is_relative_to(h) for h in already_handled):
            continue

        canonical = top_level.get(nested_dir.name)
        if canonical is None:
            warnings.append(
                f"{nested_dir}: no top-level counterpart named "
                f"'{nested_dir.name}' exists — NOT deleting (would be the "
                "only copy of this content). Move it to the repo root "
                "manually if it should be kept as its own version."
            )
            continue

        identical, diffs = dirs_are_identical(canonical, nested_dir)
        if identical:
            to_delete.append(nested_dir)
            already_handled.add(nested_dir)
        else:
            warnings.append(
                f"{nested_dir}: differs from canonical {canonical} — NOT "
                f"deleting automatically. Differences:\n    "
                + "\n    ".join(diffs)
            )

    print(f"Confirmed byte-for-byte duplicates safe to remove: {len(to_delete)}")
    for p in to_delete:
        print(f"  - {p}")

    if warnings:
        print(f"\n{len(warnings)} item(s) need manual review (NOT auto-deleted):")
        for w in warnings:
            print(f"  ! {w}")

    if not args.apply:
        print("\nDry run only — no files were deleted. Re-run with --apply to delete "
              "the confirmed duplicates listed above.")
        return 0 if not warnings else 2

    for p in to_delete:
        print(f"Deleting {p} ...")
        shutil.rmtree(p)

    print(f"\nDeleted {len(to_delete)} duplicate nested director{'y' if len(to_delete)==1 else 'ies'}.")
    if warnings:
        print(f"{len(warnings)} item(s) still need manual review — see above. Exiting with status 2.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
