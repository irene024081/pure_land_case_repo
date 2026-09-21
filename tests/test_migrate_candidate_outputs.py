from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "migrate_candidate_outputs", ROOT / "scripts" / "migrate_candidate_outputs.py"
)
assert SPEC and SPEC.loader
migration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migration)


class CandidateMigrationTest(unittest.TestCase):
    def test_rekeys_facts_and_tag_references_without_changing_evidence(self) -> None:
        extraction = {
            "case_id": "CASE000001",
            "case_facts": [
                {
                    "case_fact_id": "CASE000001-FACT0001",
                    "proposition_text": "The source reports a practice.",
                    "supporting_source_segment_ids": ["ENT000001-SEG0002"],
                }
            ],
        }
        tagging = {
            "case_id": "CASE000001",
            "persons": [{"entity_id": "PER0001", "display_name": "陈妪"}],
            "places": [],
            "tags": [{"tag": "name_recitation", "supporting_case_fact_ids": ["CASE000001-FACT0001"]}],
        }

        new_extraction, new_tagging = migration.migrate(
            extraction, tagging, "ENT000001-CAND0001"
        )

        self.assertEqual(new_extraction["candidate_id"], "ENT000001-CAND0001")
        self.assertNotIn("case_id", new_extraction)
        self.assertEqual(new_extraction["migration_source_case_id"], "CASE000001")
        self.assertEqual(
            new_extraction["case_facts"][0]["case_fact_id"], "ENT000001-CAND0001-FACT0001"
        )
        self.assertEqual(
            new_extraction["case_facts"][0]["supporting_source_segment_ids"],
            ["ENT000001-SEG0002"],
        )
        self.assertEqual(
            new_tagging["tags"][0]["supporting_case_fact_ids"],
            ["ENT000001-CAND0001-FACT0001"],
        )
        self.assertEqual(extraction["case_facts"][0]["case_fact_id"], "CASE000001-FACT0001")
        self.assertEqual(tagging["tags"][0]["supporting_case_fact_ids"], ["CASE000001-FACT0001"])

    def test_rejects_unmapped_tag_reference(self) -> None:
        extraction = {
            "case_id": "CASE000001",
            "case_facts": [{"case_fact_id": "CASE000001-FACT0001"}],
        }
        tagging = {
            "case_id": "CASE000001", "persons": [], "places": [],
            "tags": [{"tag": "x", "supporting_case_fact_ids": ["CASE000001-FACT9999"]}],
        }
        with self.assertRaisesRegex(ValueError, "unmapped fact"):
            migration.migrate(extraction, tagging, "ENT000001-CAND0001")


if __name__ == "__main__":
    unittest.main()
