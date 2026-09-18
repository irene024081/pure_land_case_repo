from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BaselineTest(unittest.TestCase):
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
