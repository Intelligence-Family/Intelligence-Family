# Federation Integrity Gate — corrected deliverables

Generated after independently extracting and testing against the actual
contents of `Intelligence-Family-main-Family-Consolidated-Hardened.zip`.
Every check below was run against that real repository, not written
speculatively — the findings quoted are real outputs from these exact
scripts.

## Where each file goes

```
.github/workflows/federation-integrity.yml   <- the workflow
scripts/federation_integrity/*.py            <- what the workflow calls
scripts/maintenance/flatten_federation_tree.py  <- one-time cleanup tool
```

Copy the `.github/` and `scripts/` folders into the repo root as-is.

## What the workflow actually does now

| Step | Script | Replaces the claim in RELEASE_NOTES.md / ADR 0004 |
|---|---|---|
| Governance files present | `check_governance_files.py` | "validates governance documents" — now version-agnostic, so it won't silently stop checking after the next version bump the way the old hardcoded `test -f .../v1.3.1/SECURITY.md` did |
| JSON contract validation | `validate_schemas.py` | "validates JSON contracts" — actually parses and checks each `*.schema.json` is a well-formed JSON Schema, checks for duplicate `$id`s, and validates any instance document that declares itself against one of the schemas |
| Credential scan | `scan_secrets.py` | "detects common credential-bearing artifacts" — now scans `.md` files too (previously excluded — that was ~90% of the repo), and matches AWS/Slack/Google/Stripe/Anthropic/OpenAI/npm/JWT patterns, not just GitHub tokens and PEM headers |
| Structural integrity | `detect_nested_duplication.py` | "rejects nested release ZIPs" — extended to also catch nested *Federation directories* (the actual problem found), plus committed archive files |
| Workflow permissions | `audit_workflow_permissions.py` | "uses contents: read permissions" — checks every workflow file has an explicit, non-`write-all` permissions block, at both top level and per-job |

## What running these against the real repo actually found

- **`check_governance_files.py` fails on the delivered v1.3.1**: `CONTRACT_VERSIONING.md` exists in v1.3.0 and v1.2.0 but was dropped from v1.3.1's top level. This is a real regression the old hardcoded check could never have caught, since it only checked for `SECURITY.md` and two other files, not the full governance set.
- **`validate_schemas.py` fails**: `capability.schema.json`, `provider-adapter.schema.json`, and `agent-authorization.schema.json` each have the same `$id` duplicated across 2–4 physically different copies (v1.2.0 / v1.3.0 / nested v1.3.1 copies). Structurally valid JSON Schema, but not safe to treat as a single source of truth as shipped.
- **`detect_nested_duplication.py` fails**: 9 instances of a Federation package directory nested inside another one, and 33 filenames duplicated byte-for-byte across up to 6 locations each — this is the "Russian doll" structure from the original review.
- **`scan_secrets.py` passes clean** — no credential material found, even now that markdown is included in the scan.
- **`audit_workflow_permissions.py` passes clean** — the existing `ci.yml` and `federation-release.yml` do declare explicit, scoped permissions. This part of the original hardening claim holds up.

## Cleanup script: `flatten_federation_tree.py`

Removes the nested directory duplication safely:

```
python3 scripts/maintenance/flatten_federation_tree.py            # dry run — reports only, deletes nothing
python3 scripts/maintenance/flatten_federation_tree.py --apply    # deletes confirmed duplicates
```

Safety model, verified by test:

- Only deletes a nested copy if it is **byte-for-byte identical** (full
  recursive content comparison, not just file size/mtime) to the
  top-level version folder of the same name.
- If a nested copy has been edited and now **differs** from its
  canonical counterpart, it is left alone and reported as a warning —
  confirmed with a deliberate one-byte corruption test, which the script
  correctly caught and refused to delete.
- If a nested folder's version has **no top-level counterpart at all**,
  it's left alone and flagged, since deleting it would destroy the only
  copy of that content.

Run against a real copy of the repo, this removed the 5 fully-duplicated
nested directories (146 files → 64 files) and left the genuinely
version-to-version duplication between sibling top-level folders alone
(e.g. `v1.2.0/SECURITY.md` and `v1.3.0/SECURITY.md` being identical is
normal for a changelog-style version history — that's not a bug the way
one version being nested inside another is).

**What this script does not fix:** the duplicate `$id` values in the
schemas, and the missing `CONTRACT_VERSIONING.md` in v1.3.1. Those need
a content decision (pick one canonical schema location, restore or
consciously drop the file) — not something safe to auto-resolve.

## Note on `federation-release.yml`

Not modified here. It still zips the entire repo tree for each release,
so until the nested duplication is cleaned up (or excluded), every
future release artifact will keep re-embedding whatever duplication
exists in-tree at release time. Worth revisiting once the tree is flat.

## Additional hardening implemented

The corrected deliverable also includes `tests/test_integrity_tools.py`, `requirements-integrity.txt`, `.gitignore`, and `AUDIT_REPORT.md`. The structural duplicate detector intentionally ignores identical files in sibling version directories because unchanged version-history documents are legitimate; it only treats duplication inside nested Federation trees as an integrity problem.
