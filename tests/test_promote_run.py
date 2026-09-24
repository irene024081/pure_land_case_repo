from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import canonical_store  # noqa: E402
import promote_run  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CASE_RUN_DIR = ROOT / "data" / "pipeline_runs" / "RUN-ENT000006-M2B-01" / "candidates" / "ENT000006-CAND0001"


def table_counts(conn) -> dict[str, int]:
    tables = (
        "cases", "case_facts", "entities", "case_tags", "source_occurrences",
        "text_versions", "identity_decisions", "rights_decisions", "dedup_index", "promotion_log",
    )
    return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}


class PromoteRunTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "canonical.db"
        self.conn = canonical_store.connect(self.db)

    def tearDown(self) -> None:
        self.conn.close()
        self.temp.cleanup()

    def test_promote_completed_case(self) -> None:
        result = promote_run.promote_one(self.conn, CASE_RUN_DIR)
        self.assertTrue(result.startswith("inserted: CASE000006"))
        counts = table_counts(self.conn)
        self.assertEqual(counts["cases"], 1)
        self.assertEqual(counts["case_facts"], 30)
        self.assertEqual(counts["source_occurrences"], 1)
        self.assertEqual(counts["identity_decisions"], 1)
        self.assertEqual(counts["rights_decisions"], 1)
        self.assertEqual(counts["dedup_index"], 1)
        case = canonical_store.get_case(self.conn, "CASE000006")
        self.assertEqual(case["publish_status"], "public")

    def test_promotion_is_idempotent(self) -> None:
        promote_run.promote_one(self.conn, CASE_RUN_DIR)
        before = table_counts(self.conn)
        result = promote_run.promote_one(self.conn, CASE_RUN_DIR)
        self.assertTrue(result.startswith("skipped"))
        self.assertEqual(table_counts(self.conn), before)

    def test_rejects_incomplete_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp) / "run"
            run_dir.mkdir()
            (run_dir / "run.json").write_text(
                json.dumps({"run_kind": "case", "status": "running", "run_id": "RUN-X"}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SystemExit, "not completed"):
                promote_run.promote_one(self.conn, run_dir)

    def test_rejects_broken_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp) / "ENT000006-CAND0001"
            shutil.copytree(CASE_RUN_DIR, run_dir)
            extraction_path = run_dir / "outputs" / "case_extraction.json"
            extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
            extraction["case_facts"][0]["supporting_source_segment_ids"] = ["ENT000006-SEG9999"]
            extraction_path.write_text(json.dumps(extraction), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "unknown IDs"):
                promote_run.promote_one(self.conn, run_dir)
            self.assertEqual(table_counts(self.conn)["cases"], 0)

    def test_rejects_superseded_run(self) -> None:
        promote_run.promote_one(self.conn, CASE_RUN_DIR)
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp) / "ENT000006-CAND0001"
            shutil.copytree(CASE_RUN_DIR, run_dir)
            run_path = run_dir / "run.json"
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run["run_id"] = "RUN-ENT000006-M2B-00-ENT000006-CAND0001"
            run["updated_at"] = "2000-01-01T00:00:00+00:00"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "superseded"):
                promote_run.promote_one(self.conn, run_dir)


if __name__ == "__main__":
    unittest.main()
