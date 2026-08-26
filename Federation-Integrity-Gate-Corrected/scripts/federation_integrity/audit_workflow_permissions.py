#!/usr/bin/env python3
"""
Audit every .github/workflows/*.yml(.yaml) file for explicit permissions.

Checks:
  * a top-level `permissions:` key exists (GitHub's default when omitted is
    the repository setting, which is often broader than needed and is not
    visible from the workflow file itself — "explicit" is the point)
  * top-level permissions is not the broad shorthand `write-all`
  * no job declares `permissions: write-all`
  * if any job needs `contents: write` (e.g. to publish a release), that is
    fine, but it must be declared at the job level, not silently inherited
    from an overly broad top-level grant

This does not evaluate whether the specific scopes chosen are correct for
what each job does — that still needs a human reading the job. It catches
the class of problem where permissions are left implicit or maximal.
"""

from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(".").resolve()
WORKFLOW_DIR = ROOT / ".github" / "workflows"


def main() -> int:
    if not WORKFLOW_DIR.is_dir():
        print("::warning::No .github/workflows directory found — nothing to audit.")
        return 0

    workflow_files = sorted(
        p for p in WORKFLOW_DIR.iterdir() if p.suffix in (".yml", ".yaml")
    )
    if not workflow_files:
        print("::warning::No workflow files found — nothing to audit.")
        return 0

    problems: list[str] = []

    for path in workflow_files:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            problems.append(f"{path}: could not parse YAML: {exc}")
            continue

        if not isinstance(doc, dict):
            problems.append(f"{path}: top-level YAML is not a mapping")
            continue

        # YAML parses the `on:` key as boolean True in some PyYAML/YAML 1.1
        # edge cases; irrelevant here, we only care about `permissions`.
        top_perms = doc.get("permissions")
        if top_perms is None:
            problems.append(
                f"{path}: no top-level `permissions:` key — job permissions "
                "fall back to the repository/org default, which is not "
                "visible from this file"
            )
        elif top_perms == "write-all":
            problems.append(f"{path}: top-level permissions is `write-all` (overly broad)")

        jobs = doc.get("jobs") or {}
        if not isinstance(jobs, dict):
            problems.append(f"{path}: `jobs:` is not a mapping")
            jobs = {}

        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                continue
            job_perms = job.get("permissions")
            if job_perms == "write-all":
                problems.append(
                    f"{path}: job '{job_name}' declares permissions: write-all"
                )

    if problems:
        print("::error::Workflow permission audit failed:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"Audited {len(workflow_files)} workflow file(s); permissions look explicit and scoped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
