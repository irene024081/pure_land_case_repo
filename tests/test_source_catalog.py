from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from source_catalog_io import require_batch_eligible, validate_source_catalog  # noqa: E402


class SourceCatalogTest(unittest.TestCase):
    def test_current_catalogs_are_valid(self) -> None:
        for source_id in ("SRC0001", "SRC0002", "SRC0003", "SRC0004", "SRC0005"):
            self.assertEqual(validate_source_catalog(source_id), [])

    def test_unknown_rights_blocks_batch(self) -> None:
        row = {
            "article_id": "SRC9999-ART000001",
            "selection_status": "selected",
            "capture_status": "verified",
            "pipeline_status": "ready",
            "rights_status": "unknown",
        }
        with self.assertRaisesRegex(ValueError, "rights_status blocks"):
            require_batch_eligible(row)

    def test_unselected_item_blocks_batch(self) -> None:
        row = {
            "article_id": "SRC9999-ART000001",
            "selection_status": "unreviewed",
            "capture_status": "verified",
            "pipeline_status": "ready",
            "rights_status": "public_domain_verified",
        }
        with self.assertRaisesRegex(ValueError, "selection_status must be selected"):
            require_batch_eligible(row)


if __name__ == "__main__":
    unittest.main()
