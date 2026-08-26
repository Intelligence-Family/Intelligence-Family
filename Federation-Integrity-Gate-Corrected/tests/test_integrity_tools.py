from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.federation_integrity import detect_nested_duplication as duplication
from scripts.federation_integrity import check_governance_files as governance
from scripts.federation_integrity import audit_workflow_permissions as permissions


class IntegrityToolTests(unittest.TestCase):
    def test_sibling_version_duplicates_are_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for version in ("v1.2.0", "v1.3.0"):
                d = root / f"Intelligence-Family-Federation-{version}"
                d.mkdir()
                (d / "SECURITY.md").write_text("same", encoding="utf-8")
            with patch.object(duplication, "ROOT", root):
                self.assertEqual(duplication.find_nested_federation_dirs(), [])
                self.assertEqual(duplication.find_duplicate_files_within_nested_federations(), {})

    def test_nested_federation_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outer = root / "Intelligence-Family-Federation-v1.3.0"
            inner = outer / "Intelligence-Family-Federation-v1.2.0"
            inner.mkdir(parents=True)
            with patch.object(duplication, "ROOT", root):
                findings = duplication.find_nested_federation_dirs()
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0], (outer, inner))

    def test_governance_requires_contract_versioning(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "Intelligence-Family-Federation-v1.3.1"
            d.mkdir()
            for name in governance.REQUIRED_RELATIVE_PATHS:
                if name != "CONTRACT_VERSIONING.md":
                    (d / name).write_text("ok", encoding="utf-8")
            with patch.object(governance, "ROOT", root):
                self.assertEqual(governance.main(), 1)

    def test_workflow_permissions_reject_write_all(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "bad.yml").write_text(
                "name: bad\npermissions: write-all\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps: []\n",
                encoding="utf-8",
            )
            with patch.object(permissions, "ROOT", root), patch.object(
                permissions, "WORKFLOW_DIR", wf
            ):
                self.assertEqual(permissions.main(), 1)


if __name__ == "__main__":
    unittest.main()
