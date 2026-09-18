from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_pipeline", ROOT / "scripts" / "run_pipeline.py")
assert SPEC and SPEC.loader
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


class PipelineTest(unittest.TestCase):
    def make_entry(self, directory: Path) -> Path:
        raw_text = "甲念佛。乙听闻此事。"
        path = directory / "entry.json"
        path.write_text(json.dumps({
            "source_id": "SRCTEST",
            "source_entry_id": "ENTTEST001",
            "raw_text": raw_text,
            "raw_text_hash": hashlib.sha256(raw_text.encode()).hexdigest(),
        }, ensure_ascii=False), encoding="utf-8")
        return path

    def precheck(self, directory: Path) -> dict[str, object]:
        rights_path = directory / "RRTEST.yml"
        rights_path.write_text(
            "rights_review_id: RRTEST\nsource_id: SRCTEST\nrights_status: public_domain_verified\npublic_display_policy: full_normalized_historical_text\n",
            encoding="utf-8",
        )
        return {
            "config": {"source_id": "SRCTEST"},
            "row": {"article_id": "SRCTEST-ART000001"},
            "review": {"rights_review_id": "RRTEST"},
            "review_path": rights_path,
            "external_processing": "blocked",
        }

    def write_response(self, directory: Path, stage: str, value: dict[str, object]) -> Path:
        path = directory / f"{stage}.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def accept(self, run_dir: Path, response_dir: Path, stage: str, value: dict[str, object]) -> None:
        pipeline.accept_response(Namespace(
            run_dir=run_dir,
            stage=stage,
            response=self.write_response(response_dir, stage, value),
            adapter="local",
            model="test-fixture",
        ))

    def test_segmentation_requires_complete_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = self.make_entry(root)
            run = {"source_entry_id": "ENTTEST001", "source_entry_path": str(entry)}
            content = "甲念佛。"
            response = {"source_entry_id": "ENTTEST001", "segments": [{
                "segment_id": "ENTTEST001-SEG0001", "sequence": 1,
                "start_offset": 0, "end_offset": len(content), "content": content,
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            }]}
            with self.assertRaisesRegex(SystemExit, "complete source text"):
                pipeline.validate_semantics("source_segmentation", response, run, root)

    def test_rights_policy_cannot_be_relaxed_by_run_command(self) -> None:
        entry_path = ROOT / "data/source_entries/public/ENT000001.normalized.json"
        result = pipeline.rights_precheck(pipeline.load_json(entry_path), entry_path)
        self.assertEqual(result["external_processing"], "blocked")
        self.assertEqual(result["review"]["rights_review_id"], "RR0005")

    def test_rights_output_cannot_exceed_source_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            rights_path = Path(temp) / "RR.yml"
            rights_path.write_text(
                "rights_review_id: RRTEST\npublic_display_policy: metadata_summary_link_and_minimal_excerpt\n",
                encoding="utf-8",
            )
            run = {
                "case_id": "CASETEST001", "rights_review_id": "RRTEST",
                "rights_review_path": str(rights_path),
            }
            response = {
                "case_id": "CASETEST001", "rights_review_id": "RRTEST",
                "allowed_display_scope": "public",
            }
            with self.assertRaisesRegex(SystemExit, "exceeds source rights policy"):
                pipeline.validate_semantics("rights_check", response, run, Path(temp))

    def test_article_fans_out_to_case_and_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article_dir = root / "RUN-ARTICLE"
            record_dir = root / "records"
            with patch.object(pipeline, "rights_precheck", return_value=self.precheck(root)), patch.object(pipeline, "update_article"):
                pipeline.create_article_run(Namespace(
                    entry=self.make_entry(root), run_dir=article_dir, record_dir=record_dir,
                ))
                raw_text = "甲念佛。乙听闻此事。"
                first = "甲念佛。"
                second = "乙听闻此事。"
                segments = [
                    {"segment_id": "ENTTEST001-SEG0001", "sequence": 1, "start_offset": 0,
                     "end_offset": len(first), "segment_type": "narrative", "content": first,
                     "content_hash": hashlib.sha256(first.encode()).hexdigest(),
                     "claim_mode": "unknown", "speaker_or_author": "source author"},
                    {"segment_id": "ENTTEST001-SEG0002", "sequence": 2, "start_offset": len(first),
                     "end_offset": len(raw_text), "segment_type": "narrative", "content": second,
                     "content_hash": hashlib.sha256(second.encode()).hexdigest(),
                     "claim_mode": "hearsay", "speaker_or_author": "source author"},
                ]
                self.accept(article_dir, root, "source_segmentation", {
                    "source_entry_id": "ENTTEST001", "segments": segments,
                })
                self.accept(article_dir, root, "case_detection", {
                    "source_entry_id": "ENTTEST001",
                    "case_candidates": [{
                        "candidate_id": "ENTTEST001-CAND0001", "working_title": "甲念佛",
                        "supporting_source_segment_ids": ["ENTTEST001-SEG0001", "ENTTEST001-SEG0002"],
                        "boundary_confidence": "high", "notes": "One event.",
                    }],
                })
                article = pipeline.load_json(article_dir / "run.json")
                self.assertEqual(len(article["case_runs"]), 1)
                case_id = article["case_runs"][0]["case_id"]
                case_dir = article_dir / "cases" / case_id
                responses = {
                    "case_extraction": {
                        "case_id": case_id, "dedup_status": "not_checked",
                        "case_facts": [{
                            "case_fact_id": f"{case_id}-FACT0001", "proposition_text": "甲念佛。",
                            "fact_type": "practice", "claim_mode": "direct_source_statement",
                            "supporting_source_segment_ids": ["ENTTEST001-SEG0001"], "uncertainty": "source_statement",
                        }],
                    },
                    "entity_tagging": {"case_id": case_id, "persons": [], "places": [], "tags": [{"tag": "name_recitation", "supporting_case_fact_ids": [f"{case_id}-FACT0001"]}]},
                    "deduplication": {"case_id": case_id, "decision": "no_match", "candidate_matches": [], "decision_reasons": ["No candidates supplied."]},
                    "reader_generation": {"case_id": case_id, "reader_summary": "甲念佛。", "paragraphs": [{"paragraph_id": "P0001", "content": "资料记载，甲念佛。", "supporting_case_fact_ids": [f"{case_id}-FACT0001"], "supporting_source_segment_ids": ["ENTTEST001-SEG0001"]}]},
                    "creator_analysis": {"case_id": case_id, "creator_metadata": {"video_fit_level": "low"}, "interpretation_angles": [{"angle_id": "ANGTEST001", "title": "资料中的念佛行为", "core_claim": "资料只明确记载甲念佛。", "audience": ["researcher"], "supporting_case_fact_ids": [f"{case_id}-FACT0001"], "supporting_source_segment_ids": ["ENTTEST001-SEG0001"], "doctrinal_boundary": "No doctrinal conclusion is established."}]},
                    "factual_check": {"case_id": case_id, "unsupported_claim_count": 0, "contradicted_claim_count": 0, "gate_result": "pass", "claims": [{"claim_id": "CLMTEST001", "claim_text": "甲念佛。", "source_output": "reader_generation", "supporting_case_fact_ids": [f"{case_id}-FACT0001"], "supporting_source_segment_ids": ["ENTTEST001-SEG0001"], "verdict": "supported"}]},
                    "rights_check": {"case_id": case_id, "rights_review_id": "RRTEST", "gate_result": "pass", "allowed_display_scope": "public", "checks": [{"output_id": "reader_generation", "quotation_status": "none", "expression_similarity_risk": "low", "policy_result": "pass"}]},
                }
                for stage in ("case_extraction", "entity_tagging", "deduplication", "reader_generation", "creator_analysis", "factual_check", "rights_check"):
                    self.accept(case_dir, root, stage, responses[stage])
                package = pipeline.load_json(case_dir / "outputs/publication_packaging.json")
                self.assertEqual(package["publish_status"], "public")
                self.assertTrue((record_dir / f"{article['run_id']}.json").exists())
                final_article = pipeline.load_json(article_dir / "run.json")
                self.assertEqual(final_article["status"], "completed")


if __name__ == "__main__":
    unittest.main()
