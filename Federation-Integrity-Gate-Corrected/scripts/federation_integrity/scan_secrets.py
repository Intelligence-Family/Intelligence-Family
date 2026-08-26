#!/usr/bin/env python3
"""
Scan the working tree for likely credential material.

This replaces the previous CI step, which only matched PEM key headers and
GitHub token prefixes, and explicitly excluded every *.md file (i.e. ~90%
of this repository) from the scan entirely. This version:

  * scans every text file, including markdown
  * matches a wider set of common provider token formats
  * still excludes this script itself, the workflow file that calls it,
    and .git, so the patterns below don't trigger on their own source

This is still a pattern-based scanner, not a substitute for a maintained
tool like gitleaks/trufflehog — it is intentionally dependency-free so it
runs with no setup. Treat a clean run as "no obvious, common-format
secrets found," not as a formal guarantee.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(".").resolve()

EXCLUDED_DIR_PARTS = {".git", "dist", "node_modules"}
# Files that legitimately contain these patterns as literal text (this
# scanner and the workflow that documents it) must not scan themselves.
SELF_EXCLUDE_NAMES = {"scan_secrets.py", "federation-integrity.yml"}

# (label, compiled pattern)
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("PEM private key", re.compile(r"BEGIN (RSA|OPENSSH|EC|DSA|PGP|PRIVATE) KEY")),
    ("GitHub personal access token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("GitHub OAuth/app token", re.compile(r"\bgh[osu]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("AWS secret access key (assignment)", re.compile(
        r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?"
    )),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Slack webhook URL", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Stripe live secret key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
    ("Stripe restricted key", re.compile(r"\brk_live_[A-Za-z0-9]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}\b")),
    ("Generic bearer/API-key assignment", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*"
        r"['\"][A-Za-z0-9_\-/+=]{16,}['\"]"
    )),
    ("JWT-looking string", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b")),
    ("Slack legacy config token", re.compile(r"\bxoxp-[0-9]{10,}-[0-9]{10,}-[0-9]{10,}-[a-f0-9]{32}\b")),
]

TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".txt", ".env", ".cfg", ".ini", ".toml", ".sh", ".py"}


def iter_text_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
            continue
        if p.name in SELF_EXCLUDE_NAMES:
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.suffix != "":
            continue
        yield p


def main() -> int:
    findings: list[str] = []

    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for label, pattern in PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path}:{line_no}: possible {label}")

    if findings:
        print("::error::Possible credential material detected:")
        for f in findings:
            print(f"  - {f}")
        return 1

    print("No obvious credential material found in scanned files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
