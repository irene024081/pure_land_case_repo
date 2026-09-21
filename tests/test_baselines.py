from __future__ import annotations

import hashlib
import json
import unittest
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BaselineTest(unittest.TestCase):
    def test_t02_v02_proposed_migration_matches_m2a_identity(self) -> None:
        baseline = json.loads(
            (ROOT / "data/baselines/M2A_ENT000001_P011.json").read_text(encoding="utf-8")
        )
        migration = json.loads(
            (ROOT / "data/migrations/T02_v0.2_CASE000001.json").read_text(encoding="utf-8")
        )
        entry = json.loads(
            (ROOT / "data/source_entries/public/ENT000001.normalized.json").read_text(encoding="utf-8")
        )
        with (ROOT / "data/source_catalogs/SRC0001/articles.csv").open(encoding="utf-8", newline="") as handle:
            catalog_row = next(row for row in csv.DictReader(handle) if row["source_entry_id"] == "ENT000001")

        self.assertEqual(migration["migration_status"], "proposed_review_only")
        self.assertEqual(migration["source_baseline_id"], baseline["baseline_id"])
        self.assertEqual(migration["source_pipeline_version"], baseline["pipeline_version"])
        self.assertEqual(migration["case"]["case_id"], baseline["case_id"])
        self.assertEqual(migration["source_item_id"], catalog_row["article_id"])
        occurrence = migration["source_occurrence"]
        segments = occurrence["supporting_source_segment_ids"]
        self.assertEqual(occurrence["source_entry_id"], entry["source_entry_id"])
        self.assertEqual(occurrence["source_id"], entry["source_id"])
        self.assertEqual(occurrence["source_item_id"], catalog_row["article_id"])
        self.assertEqual(len(segments), baseline["metrics"]["source_segment_count"])
        self.assertEqual(occurrence["locator"]["segment_ids"], segments)
        seed = "|".join((entry["source_entry_id"], migration["candidate_id"], *sorted(segments)))
        self.assertEqual(occurrence["occurrence_id"], "OCC" + hashlib.sha256(seed.encode()).hexdigest()[:16].upper())
        self.assertEqual(migration["case"]["discovery_occurrence_id"], occurrence["occurrence_id"])
        self.assertEqual(migration["case"]["earliest_known"]["status"], "earlier_unresolved")
        for anchor_name in ("primary_subject", "event_time_anchor", "event_place_anchor"):
            for fact_id in migration["case"][anchor_name]["case_fact_ids"]:
                self.assertRegex(fact_id, r"^CASE000001-FACT\d{4}$")
                self.assertLessEqual(int(fact_id[-4:]), baseline["metrics"]["case_fact_count"])
        self.assertEqual(occurrence["parent_links"][0]["target"]["state"], "unresolved_upstream")
        self.assertEqual(
            occurrence["parent_links"][0]["supporting_source_segment_ids"],
            ["ENT000001-SEG0007", "ENT000001-SEG0008"],
        )

    def test_m2a_records_match_accepted_baseline(self) -> None:
        baseline = json.loads(
            (ROOT / "data/baselines/M2A_ENT000001_P011.json").read_text(encoding="utf-8")
        )
        self.assertEqual(baseline["status"], "machine_accepted")
        self.assertEqual(baseline["metrics"]["unsupported_claim_count"], 0)
        self.assertEqual(baseline["metrics"]["contradicted_claim_count"], 0)
        self.assertEqual(
            set(baseline["metrics"]["rights_checked_output_ids"]),
            {"reader_generation", "creator_analysis"},
        )

        for run_key in ("article_run", "case_run"):
            expected = baseline[run_key]
            path = ROOT / expected["record_path"]
            content = path.read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), expected["record_sha256"])
            record = json.loads(content)
            self.assertEqual(record["run_id"], expected["run_id"])
            self.assertEqual(record["pipeline_version"], baseline["pipeline_version"])
            self.assertEqual(record["status"], "completed")
            for stage_id, output_hash in expected["stage_output_hashes"].items():
                self.assertEqual(record["stages"][stage_id]["status"], "completed")
                self.assertEqual(record["stages"][stage_id]["output_hash"], output_hash)


if __name__ == "__main__":
    unittest.main()
