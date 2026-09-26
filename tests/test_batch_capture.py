from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import batch_capture  # noqa: E402
import verify_source_entry_storage  # noqa: E402
from source_catalog_io import FIELDS  # noqa: E402
from test_extractors import CBETA_FIXTURE  # noqa: E402


class BatchCaptureTest(unittest.TestCase):
    """Runs against a temp tree laid out like the repo (data/source_entries/...)."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.catalog_root = self.root / "catalogs"
        self.public_dir = Path("data/source_entries/public")
        self.manifest_dir = Path("data/source_entries/manifests")
        self.rights_dir = self.root / "rights"
        self.rights_dir.mkdir()
        source_dir = self.catalog_root / "SRCTEST"
        source_dir.mkdir(parents=True)
        (source_dir / "source.yml").write_text(
            "source_id: SRCTEST\nextractor_name: extract_cbeta_xml.py\n"
            "rights_review_id: RRTEST\ndefault_language: zh-Hant\n",
            encoding="utf-8",
        )
        xml_path = self.root / "fixture.xml"
        xml_path.write_text(CBETA_FIXTURE, encoding="utf-8")
        (source_dir / "inventory.yml").write_text(
            f"xml_path: {xml_path}\nsource_title: 测试集\nsource_url: https://example.invalid/\n"
            "sutra_no: T99n9999\nvolume_labels: 卷上\n"
            "source_version: TEST 1.0\nsource_revision: abc123\n",
            encoding="utf-8",
        )
        (self.rights_dir / "RRTEST.yml").write_text(
            "rights_review_id: RRTEST\nsource_id: SRCTEST\nrights_status: public_domain_verified\n"
            "internal_retention_basis: public_domain_historical_text\n",
            encoding="utf-8",
        )
        with (source_dir / "articles.csv").open("w", encoding="utf-8", newline="") as handle:
            csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n").writeheader()
        self._old_cwd = os.getcwd()
        self._old_root = batch_capture.ROOT
        os.chdir(self.root)
        batch_capture.ROOT = self.root

    def tearDown(self) -> None:
        batch_capture.ROOT = self._old_root
        os.chdir(self._old_cwd)
        self.temp.cleanup()

    def run_capture(self) -> dict:
        args = type("A", (), {
            "source_id": "SRCTEST", "xml": "", "juan": None, "dry_run": False,
            "catalog_root": self.catalog_root, "public_dir": self.public_dir,
            "manifest_dir": self.manifest_dir,
        })()
        source_config = batch_capture.parse_simple_yaml(self.catalog_root / "SRCTEST" / "source.yml")
        inventory_config = batch_capture.parse_simple_yaml(self.catalog_root / "SRCTEST" / "inventory.yml")
        self.assertEqual(
            batch_capture.rights_gate("SRCTEST", source_config, rights_dir=self.rights_dir), ""
        )
        return batch_capture.capture_cbeta_source(
            "SRCTEST", source_config, inventory_config, args,
            {"catalog_root": self.catalog_root, "public_dir": self.public_dir,
             "manifest_dir": self.manifest_dir, "rights_dir": self.rights_dir},
        )

    def test_capture_writes_entries_manifests_and_catalog(self) -> None:
        report = self.run_capture()
        self.assertEqual(len(report["captured"]), 3)
        self.assertEqual(len(report["failed"]), 0)
        self.assertEqual(len(list(self.public_dir.glob("ENT*.normalized.json"))), 3)
        manifests = list(self.manifest_dir.glob("ENT*.yml"))
        self.assertEqual(len(manifests), 3)
        # integration with the storage verifier: every manifest checks out
        for manifest in manifests:
            verify_source_entry_storage.verify_manifest(manifest)
        with (self.catalog_root / "SRCTEST" / "articles.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 3)
        parent = next(row for row in rows if row["title"] == "乙一")
        self.assertIn("contains_nested_entries", parent["notes"])

    def test_rerun_is_idempotent(self) -> None:
        first = self.run_capture()
        snapshot = {p.name: p.read_bytes() for p in self.public_dir.glob("*.json")}
        second = self.run_capture()
        self.assertEqual(len(first["captured"]), 3)
        self.assertEqual(len(second["captured"]), 0)
        self.assertEqual(len(second["skipped"]), 3)
        self.assertEqual(snapshot, {p.name: p.read_bytes() for p in self.public_dir.glob("*.json")})
        with (self.catalog_root / "SRCTEST" / "articles.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 3)

    def test_failure_is_recorded_and_batch_continues(self) -> None:
        calls = {"n": 0}
        original = batch_capture.write_manifest

        def flaky(*a, **k):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("disk full")
            return original(*a, **k)

        with unittest.mock.patch.object(batch_capture, "write_manifest", flaky):
            report = self.run_capture()
        self.assertEqual(len(report["captured"]), 2)
        self.assertEqual(len(report["failed"]), 1)
        self.assertIn("disk full", report["failed"][0][1])

    def test_rights_gate_blocks_unsettled_source(self) -> None:
        (self.rights_dir / "RRTEST.yml").write_text(
            "rights_review_id: RRTEST\nsource_id: SRCTEST\nrights_status: legal_review_required\n"
            "internal_retention_basis: provisional_research_copy\n",
            encoding="utf-8",
        )
        source_config = batch_capture.parse_simple_yaml(self.catalog_root / "SRCTEST" / "source.yml")
        reason = batch_capture.rights_gate("SRCTEST", source_config, rights_dir=self.rights_dir)
        self.assertIn("legal_review_required", reason)

    def test_inventory_rights_review_overrides_source_default(self) -> None:
        (self.rights_dir / "RROPEN.yml").write_text(
            "rights_review_id: RROPEN\nsource_id: SRCTEST\n"
            "rights_status: open_license_verified\nlicense_type: CC-BY-NC-SA-4.0\n"
            "license_url: https://creativecommons.org/licenses/by-nc-sa/4.0/\n"
            "terms_url: https://example.invalid/terms\nterms_checked_at: 2026-09-26\n"
            "internal_retention_basis: CC-BY-NC-SA-4.0\n"
            "public_display_policy: full_text_with_attribution\n",
            encoding="utf-8",
        )
        inventory_path = self.catalog_root / "SRCTEST" / "inventory.yml"
        inventory_path.write_text(
            inventory_path.read_text(encoding="utf-8") + "rights_review_id: RROPEN\n",
            encoding="utf-8",
        )

        report = self.run_capture()

        self.assertEqual(len(report["captured"]), 3)
        manifest = batch_capture.parse_simple_yaml(next(self.manifest_dir.glob("ENT*.yml")))
        self.assertEqual(manifest["rights_review_id"], "RROPEN")
        self.assertEqual(manifest["rights_status"], "open_license_verified")
        self.assertEqual(manifest["rights_basis"], "CC-BY-NC-SA-4.0")
        self.assertEqual(manifest["source_version"], "TEST 1.0")
        with (self.catalog_root / "SRCTEST" / "articles.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual({row["rights_review_id"] for row in rows}, {"RROPEN"})
        self.assertEqual({row["rights_status"] for row in rows}, {"open_license_verified"})


if __name__ == "__main__":
    unittest.main()
