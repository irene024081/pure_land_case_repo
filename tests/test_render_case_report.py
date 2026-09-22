from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import render_case_report  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
COMPLETED_CASE_DIR = (
    ROOT / "data" / "pipeline_runs" / "RUN-ENT000006-M2B-01" / "candidates" / "ENT000006-CAND0001"
)


class RenderCaseReportTest(unittest.TestCase):
    def test_renders_completed_case_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out_dir = Path(temp)
            target = render_case_report.render_case(COMPLETED_CASE_DIR, out_dir)
            self.assertIsNotNone(target)
            page = target.read_text(encoding="utf-8")
            self.assertIn("CASE000006", page)
            self.assertIn("卢氏", page)
            self.assertIn("事实清单", page)
            self.assertNotIn(render_case_report.REDACTED, page)

            index = render_case_report.render_index({"CASE000006": COMPLETED_CASE_DIR}, out_dir)
            index_page = index.read_text(encoding="utf-8")
            self.assertIn('href="CASE000006.html"', index_page)

    def test_restricted_source_text_is_redacted(self) -> None:
        self.assertEqual(
            render_case_report.manifest_storage_class("ENT000002"),
            "local_restricted",
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_dir = root / "candidates" / "ENT999999-CAND0001"
            outputs = run_dir / "outputs"
            outputs.mkdir(parents=True)
            source_entry_path = root / "entry.json"
            source_entry_path.write_text(
                json.dumps({"source_entry_id": "ENT999999", "raw_text": "受限内容标记ABC"}),
                encoding="utf-8",
            )
            manifest_root = root / "manifests"
            manifest_root.mkdir()
            (manifest_root / "ENT999999.yml").write_text(
                "source_entry_id: ENT999999\nstorage_class: local_restricted\n", encoding="utf-8"
            )
            parent_dir = root
            (parent_dir / "outputs").mkdir(exist_ok=True)
            (parent_dir / "outputs" / "source_segmentation.json").write_text(
                json.dumps({
                    "source_entry_id": "ENT999999",
                    "segments": [{
                        "segment_id": "ENT999999-SEG0001",
                        "sequence": 1,
                        "start_offset": 0,
                        "end_offset": 7,
                        "segment_type": "narrative",
                        "content": "受限内容标记ABC",
                        "content_hash": "x",
                        "claim_mode": "hearsay",
                        "speaker_or_author": "source compiler",
                    }],
                }),
                encoding="utf-8",
            )
            run = {
                "run_id": "RUN-TEST-CAND0001",
                "run_kind": "case",
                "status": "completed",
                "case_id": "CASE999999",
                "candidate_id": "ENT999999-CAND0001",
                "source_entry_path": str(source_entry_path),
                "parent_article_run_path": str(parent_dir),
                "source_id": "SRC9999",
                "source_catalog_article_id": "SRC9999-ART000001",
                "pipeline_version": "0.2.0",
                "source_entry_hash": "x",
                "stages": {"case_extraction": {"status": "completed"}},
            }
            (run_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")
            (outputs / "reader_generation.json").write_text(
                json.dumps({
                    "case_id": "CASE999999",
                    "reader_title": "测试案例",
                    "paragraphs": [{
                        "paragraph_id": "P1",
                        "content": "白话段落",
                        "supporting_case_fact_ids": [],
                        "supporting_source_segment_ids": ["ENT999999-SEG0001"],
                    }],
                    "reader_summary": "摘要",
                }),
                encoding="utf-8",
            )

            original_root = render_case_report.MANIFEST_ROOT
            render_case_report.MANIFEST_ROOT = manifest_root
            try:
                target = render_case_report.render_case(run_dir, root / "reports")
            finally:
                render_case_report.MANIFEST_ROOT = original_root

            page = target.read_text(encoding="utf-8")
            self.assertIn(render_case_report.REDACTED, page)
            self.assertNotIn("受限内容标记ABC", page)

    def test_skips_incomplete_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp) / "run"
            run_dir.mkdir()
            (run_dir / "run.json").write_text(
                json.dumps({"run_kind": "case", "status": "running"}), encoding="utf-8"
            )
            self.assertIsNone(render_case_report.render_case(run_dir, Path(temp) / "out"))


if __name__ == "__main__":
    unittest.main()
