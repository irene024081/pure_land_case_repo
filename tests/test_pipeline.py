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
        config, rows = pipeline.read_catalog("SRC0001")
        ready_row = dict(rows[0])
        ready_row["pipeline_status"] = "ready"
        with patch.object(pipeline, "read_catalog", return_value=(config, [ready_row])), patch.object(
            pipeline, "find_entry_row", return_value=ready_row
        ):
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
                "run_kind": "case", "pipeline_version": "0.1.0",
            }
            response = {
                "case_id": "CASETEST001", "rights_review_id": "RRTEST",
                "allowed_display_scope": "public",
                "gate_result": "pass",
                "checks": [{
                    "output_id": "reader_generation", "quotation_status": "none",
                    "expression_similarity_risk": "low", "policy_result": "pass",
                }],
            }
            with self.assertRaisesRegex(SystemExit, "exceeds source rights policy"):
                pipeline.validate_semantics("rights_check", response, run, Path(temp))

    def test_pipeline_definitions_remain_version_addressable(self) -> None:
        old = pipeline.definition("0.1.0")
        previous = pipeline.definition("0.1.1")
        current = pipeline.definition("0.1.2")
        next_version = pipeline.definition("0.2.0")
        old_rights = next(stage for stage in old["case_stages"] if stage["id"] == "rights_check")
        previous_rights = next(stage for stage in previous["case_stages"] if stage["id"] == "rights_check")
        previous_factual = next(stage for stage in previous["case_stages"] if stage["id"] == "factual_check")
        current_factual = next(stage for stage in current["case_stages"] if stage["id"] == "factual_check")
        self.assertEqual(old_rights["depends_on"], ["reader_generation"])
        self.assertEqual(previous_rights["depends_on"], ["reader_generation", "creator_analysis"])
        self.assertEqual(previous_factual["depends_on"], ["reader_generation", "creator_analysis"])
        self.assertEqual(
            current_factual["depends_on"],
            ["case_extraction", "reader_generation", "creator_analysis"],
        )
        next_ids = [stage["id"] for stage in next_version["case_stages"]]
        self.assertLess(next_ids.index("deduplication"), next_ids.index("case_resolution"))
        self.assertLess(next_ids.index("case_resolution"), next_ids.index("reader_generation"))

    def start_v2_article(self, root: Path, candidates: list[dict[str, object]]) -> Path:
        article_dir = root / "RUN-V2"
        pipeline.create_article_run(Namespace(
            entry=self.make_entry(root), run_dir=article_dir,
            record_dir=root / "records", pipeline_version="0.2.0",
        ))
        raw_text = "甲念佛。乙听闻此事。"
        self.accept(article_dir, root, "source_segmentation", {
            "source_entry_id": "ENTTEST001",
            "segments": [{
                "segment_id": "ENTTEST001-SEG0001", "sequence": 1,
                "start_offset": 0, "end_offset": len(raw_text),
                "content": raw_text,
                "content_hash": hashlib.sha256(raw_text.encode()).hexdigest(),
                "segment_type": "narrative", "claim_mode": "unknown",
                "speaker_or_author": "source author",
            }],
        })
        self.accept(article_dir, root, "case_detection", {
            "source_entry_id": "ENTTEST001", "case_candidates": candidates,
        })
        return article_dir

    def v2_candidate(self, candidate_id: str) -> dict[str, object]:
        return {
            "candidate_id": candidate_id, "working_title": "甲念佛",
            "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
            "boundary_confidence": "high", "notes": "Candidate boundary in one segment.",
        }

    def accept_v2_evidence(self, root: Path, candidate_dir: Path, candidate_id: str) -> str:
        fact_id = f"{candidate_id}-FACT0001"
        self.accept(candidate_dir, root, "case_extraction", {
            "candidate_id": candidate_id,
            "case_facts": [{
                "case_fact_id": fact_id, "proposition_text": "甲念佛。",
                "fact_type": "practice", "claim_mode": "direct_source_statement",
                "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
                "uncertainty": "source_statement",
            }],
        })
        self.accept(candidate_dir, root, "entity_tagging", {
            "candidate_id": candidate_id, "persons": [], "places": [],
            "tags": [{"tag": "name_recitation", "tag_class": "practice", "supporting_case_fact_ids": [fact_id]}],
        })
        return fact_id

    def test_v2_assigns_case_only_after_dedup_and_records_occurrence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate_id = "ENTTEST001-CAND0001"
            row = {"article_id": "SRCTEST-ART000001", "case_ids": ""}
            with patch.object(pipeline, "rights_precheck", return_value=self.precheck(root)), patch.object(
                pipeline, "find_entry_row", return_value=row
            ), patch.object(pipeline, "update_article"):
                article_dir = self.start_v2_article(root, [self.v2_candidate(candidate_id)])
                child_dir = article_dir / "candidates" / candidate_id
                article = pipeline.load_json(article_dir / "run.json")
                child = pipeline.load_json(child_dir / "run.json")
                self.assertNotIn("case_id", article["case_runs"][0])
                self.assertNotIn("case_id", child)
                self.assertFalse((article_dir / "cases").joinpath(candidate_id).exists())
                fact_id = self.accept_v2_evidence(root, child_dir, candidate_id)
                dedup_request = pipeline.load_json(child_dir / "requests/deduplication.json")
                self.assertEqual(
                    dedup_request["inputs"]["dedup_candidate_retrieval"]["retrieval_version"],
                    "dedup_candidates/v2",
                )
                self.assertEqual(dedup_request["inputs"]["dedup_candidates"], [])
                self.assertNotIn("case_id", dedup_request["inputs"])
                self.accept(child_dir, root, "deduplication", {
                    "candidate_id": candidate_id, "overall_decision": "new_case",
                    "candidate_matches": [], "decision_reasons": ["No local candidates matched."],
                })
                child = pipeline.load_json(child_dir / "run.json")
                case_id = child["case_id"]
                self.assertRegex(case_id, r"^CASE\d{6}$")
                resolution = pipeline.load_json(child_dir / "outputs/case_resolution.json")
                self.assertEqual(resolution["decision_basis"], "scoped_no_match")
                self.assertEqual(resolution["case_id"], case_id)
                occurrence_request = pipeline.load_json(child_dir / "requests/source_occurrence.json")
                seed = occurrence_request["inputs"]["occurrence_seed"]
                self.accept(child_dir, root, "source_occurrence", {
                    **seed, "content_form": "biographical_entry", "voice": "third_person",
                    "parent_links": [], "review_status": "machine_checked",
                })
                self.accept(child_dir, root, "reader_generation", {
                    "case_id": case_id, "reader_summary": "甲念佛。",
                    "paragraphs": [{
                        "paragraph_id": "P0001", "content": "资料记载，甲念佛。",
                        "supporting_case_fact_ids": [fact_id],
                        "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
                    }],
                })
                self.accept(child_dir, root, "creator_analysis", {
                    "case_id": case_id, "creator_metadata": {"video_fit_level": "low"},
                    "interpretation_angles": [{
                        "angle_id": "ANGTEST001", "title": "资料中的念佛行为",
                        "core_claim": "资料只明确记载甲念佛。", "audience": ["researcher"],
                        "supporting_case_fact_ids": [fact_id],
                        "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
                        "doctrinal_boundary": "No doctrinal conclusion is established.",
                    }],
                })
                self.accept(child_dir, root, "factual_check", {
                    "case_id": case_id, "unsupported_claim_count": 0,
                    "contradicted_claim_count": 0, "gate_result": "pass",
                    "claims": [{
                        "claim_id": "CLMTEST001", "claim_text": "甲念佛。",
                        "source_output": "reader_generation",
                        "supporting_case_fact_ids": [fact_id],
                        "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
                        "verdict": "supported",
                    }],
                })
                self.accept(child_dir, root, "rights_check", {
                    "case_id": case_id, "rights_review_id": "RRTEST", "gate_result": "pass",
                    "allowed_display_scope": "public",
                    "checks": [
                        {"output_id": item, "quotation_status": "none", "expression_similarity_risk": "low", "policy_result": "pass"}
                        for item in ("reader_generation", "creator_analysis")
                    ],
                })
                package = pipeline.load_json(child_dir / "outputs/publication_packaging.json")
                self.assertEqual(package["case_id"], case_id)
                self.assertEqual(package["publish_status"], "public")
                self.assertEqual(pipeline.load_json(article_dir / "run.json")["status"], "completed")

    def test_v2_existing_case_ids_never_reused_by_candidate_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_id = "ENTTEST001-CAND0002"
            second_id = "ENTTEST001-CAND0001"
            row = {"article_id": "SRCTEST-ART000001", "case_ids": "CASE000001;CASE000002"}
            precheck = self.precheck(root)
            precheck["row"] = row
            with patch.object(pipeline, "rights_precheck", return_value=precheck), patch.object(
                pipeline, "find_entry_row", return_value=row
            ), patch.object(pipeline, "update_article"):
                article_dir = self.start_v2_article(root, [
                    self.v2_candidate(first_id), self.v2_candidate(second_id),
                ])
                first_dir = article_dir / "candidates" / first_id
                self.assertNotIn("case_id", pipeline.load_json(first_dir / "run.json"))
                self.accept_v2_evidence(root, first_dir, first_id)
                self.accept(first_dir, root, "deduplication", {
                    "candidate_id": first_id, "overall_decision": "new_case",
                    "candidate_matches": [], "decision_reasons": ["No local candidates matched."],
                })
                blocked = pipeline.load_json(first_dir / "run.json")
                self.assertEqual(blocked["stages"]["case_resolution"]["status"], "review_required")
                self.assertNotIn("case_id", blocked)
                pipeline.resolve_identity(Namespace(
                    run_dir=first_dir, action="reuse", case_id="CASE000002",
                    reviewer="test-reviewer", reason="Matched the second prior record by source identity.",
                ))
                resolved = pipeline.load_json(first_dir / "run.json")
                self.assertEqual(resolved["case_id"], "CASE000002")
                self.assertEqual(resolved["resolution_review"]["reviewer_id"], "test-reviewer")
                self.assertEqual(pipeline.load_json(article_dir / "run.json")["case_runs"][0]["case_id"], "CASE000002")

    def test_v2_rejects_missing_dedup_comparison_and_unknown_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate_id = "ENTTEST001-CAND0001"
            candidate_dir = root / "RUN-V2" / "candidates" / candidate_id
            row = {"article_id": "SRCTEST-ART000001", "case_ids": ""}
            with patch.object(pipeline, "rights_precheck", return_value=self.precheck(root)), patch.object(
                pipeline, "find_entry_row", return_value=row
            ), patch.object(pipeline, "update_article"):
                self.start_v2_article(root, [self.v2_candidate(candidate_id)])
                self.accept_v2_evidence(root, candidate_dir, candidate_id)
                request = pipeline.load_json(candidate_dir / "requests/deduplication.json")
                request["inputs"]["dedup_candidates"] = [{"candidate_case_id": "CASE000099"}]
                pipeline.atomic_json(candidate_dir / "requests/deduplication.json", request)
                with self.assertRaisesRegex(SystemExit, "request hash mismatch"):
                    self.accept(candidate_dir, root, "deduplication", {
                        "candidate_id": candidate_id, "overall_decision": "new_case",
                        "candidate_matches": [], "decision_reasons": ["No match."],
                    })
                with self.assertRaisesRegex(SystemExit, "every supplied candidate"):
                    pipeline.validate_semantics("deduplication", {
                        "candidate_id": candidate_id, "overall_decision": "new_case",
                        "candidate_matches": [], "decision_reasons": ["No match."],
                    }, pipeline.load_json(candidate_dir / "run.json"), candidate_dir)
                original_request = pipeline.load_json(candidate_dir / "run.json")["stages"]["deduplication"]["request_hash"]
                request["inputs"]["dedup_candidates"] = []
                pipeline.atomic_json(candidate_dir / "requests/deduplication.json", request)
                self.assertEqual(
                    pipeline.sha256_file(candidate_dir / "requests/deduplication.json"), original_request
                )
                self.accept(candidate_dir, root, "deduplication", {
                    "candidate_id": candidate_id, "overall_decision": "new_case",
                    "candidate_matches": [], "decision_reasons": ["No match."],
                })
                seed = pipeline.load_json(candidate_dir / "requests/source_occurrence.json")["inputs"]["occurrence_seed"]
                with self.assertRaisesRegex(SystemExit, "unknown occurrence"):
                    self.accept(candidate_dir, root, "source_occurrence", {
                        **seed, "content_form": "biographical_entry", "voice": "third_person",
                        "review_status": "machine_checked", "parent_links": [{
                            "relation": "derived_from", "target": {"state": "known", "occurrence_id": "OCCNOTRETAINED"},
                            "basis": "source_explicit", "supporting_source_segment_ids": ["ENTTEST001-SEG0001"],
                            "review_status": "needs_review",
                        }],
                    })

    def test_dedup_retrieval_selects_completed_exact_match_and_protects_rights(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            current_article = root / "RUN-CURRENT"
            current_dir = current_article / "cases" / "CASECURRENT"
            candidate_dir = root / "RUN-OLD" / "cases" / "CASEOLD"
            for directory in (current_dir / "outputs", candidate_dir / "outputs"):
                directory.mkdir(parents=True)

            current_extraction = {
                "case_id": "CASECURRENT",
                "case_facts": [{"fact_type": "date", "date_value": "1653"}],
            }
            current_tagging = {
                "case_id": "CASECURRENT",
                "persons": [{
                    "display_name": "陈妪", "source_name": "陈妪", "name_status": "partial",
                }],
                "places": [{"display_name": "常熟", "source_name": "常熟"}],
                "tags": [{"tag": "name_recitation", "tag_class": "practice"}],
            }
            candidate_extraction = {
                "case_id": "CASEOLD",
                "case_facts": [{"fact_type": "date", "date_value": "1653"}],
            }
            candidate_tagging = {
                "case_id": "CASEOLD",
                "persons": [{
                    "display_name": "陈妪", "source_name": "陈妪", "name_status": "partial",
                }],
                "places": [{"display_name": "常熟", "source_name": "常熟"}],
                "tags": [{"tag": "name_recitation", "tag_class": "practice"}],
            }
            pipeline.atomic_json(current_dir / "outputs/case_extraction.json", current_extraction)
            pipeline.atomic_json(current_dir / "outputs/entity_tagging.json", current_tagging)
            pipeline.atomic_json(candidate_dir / "outputs/case_extraction.json", candidate_extraction)
            pipeline.atomic_json(candidate_dir / "outputs/entity_tagging.json", candidate_tagging)
            pipeline.atomic_json(candidate_dir / "run.json", {
                "run_id": "RUN-OLD-CASEOLD", "run_kind": "case", "status": "completed",
                "case_id": "CASEOLD", "source_id": "SRCOLD", "source_entry_id": "ENTOLD",
                "pipeline_version": "0.1.1", "external_processing": "blocked",
                "updated_at": "2026-09-01T00:00:00+00:00",
            })
            run = {
                "case_id": "CASECURRENT", "source_entry_id": "ENTCURRENT",
                "parent_article_run_path": str(current_article),
                "run_kind": "case", "pipeline_version": "0.1.2",
            }

            context = pipeline.dedup_candidate_context(run, current_dir)

            self.assertEqual(context["metadata"]["eligible_completed_case_count"], 1)
            self.assertEqual(context["metadata"]["selected_candidate_count"], 1)
            self.assertEqual(context["candidates"][0]["candidate_case_id"], "CASEOLD")
            self.assertIn("person_exact:陈妪", context["candidates"][0]["selection_reasons"])
            self.assertTrue(context["metadata"]["requires_local_adapter"])

    def test_rights_check_must_cover_every_declared_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            rights_path = Path(temp) / "RR.yml"
            rights_path.write_text(
                "rights_review_id: RRTEST\npublic_display_policy: full_normalized_historical_text\n",
                encoding="utf-8",
            )
            run = {
                "case_id": "CASETEST001", "rights_review_id": "RRTEST",
                "rights_review_path": str(rights_path),
                "run_kind": "case", "pipeline_version": "0.1.1",
            }
            response = {
                "case_id": "CASETEST001", "rights_review_id": "RRTEST",
                "allowed_display_scope": "public", "gate_result": "pass",
                "checks": [{
                    "output_id": "reader_generation", "quotation_status": "none",
                    "expression_similarity_risk": "low", "policy_result": "pass",
                }],
            }
            with self.assertRaisesRegex(SystemExit, "creator_analysis"):
                pipeline.validate_semantics("rights_check", response, run, Path(temp))

    def test_unresolved_deduplication_withholds_v012_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            outputs = run_dir / "outputs"
            outputs.mkdir()
            pipeline.atomic_json(outputs / "factual_check.json", {"gate_result": "pass"})
            pipeline.atomic_json(outputs / "rights_check.json", {"gate_result": "pass"})
            pipeline.atomic_json(outputs / "deduplication.json", {"decision": "needs_human_review"})
            run = {"run_kind": "case", "pipeline_version": "0.1.2"}

            blockers = pipeline.publication_blockers(run, run_dir)

            self.assertEqual(blockers, ["deduplication_unresolved:needs_human_review"])

    def test_article_fans_out_to_case_and_completes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article_dir = root / "RUN-ARTICLE"
            record_dir = root / "records"
            with patch.object(pipeline, "rights_precheck", return_value=self.precheck(root)), patch.object(pipeline, "update_article"):
                pipeline.create_article_run(Namespace(
                    entry=self.make_entry(root), run_dir=article_dir, record_dir=record_dir,
                    pipeline_version="0.1.2",
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
                    "rights_check": {"case_id": case_id, "rights_review_id": "RRTEST", "gate_result": "pass", "allowed_display_scope": "public", "checks": [{"output_id": "reader_generation", "quotation_status": "none", "expression_similarity_risk": "low", "policy_result": "pass"}, {"output_id": "creator_analysis", "quotation_status": "none", "expression_similarity_risk": "low", "policy_result": "pass"}]},
                }
                for stage in ("case_extraction", "entity_tagging", "deduplication", "reader_generation", "creator_analysis", "factual_check", "rights_check"):
                    self.accept(case_dir, root, stage, responses[stage])
                package = pipeline.load_json(case_dir / "outputs/publication_packaging.json")
                self.assertEqual(package["publish_status"], "public")
                self.assertEqual(package["withheld_reasons"], [])
                dedup_request = pipeline.load_json(case_dir / "requests/deduplication.json")
                self.assertEqual(
                    dedup_request["inputs"]["dedup_candidate_retrieval"]["retrieval_version"],
                    "dedup_candidates/v1",
                )
                self.assertEqual(dedup_request["inputs"]["dedup_candidates"], [])
                factual_request = pipeline.load_json(case_dir / "requests/factual_check.json")
                self.assertIn("case_extraction", factual_request["inputs"])
                rights_request = pipeline.load_json(case_dir / "requests/rights_check.json")
                self.assertIn("reader_generation", rights_request["inputs"])
                self.assertIn("creator_analysis", rights_request["inputs"])
                self.assertTrue((record_dir / f"{article['run_id']}.json").exists())
                final_article = pipeline.load_json(article_dir / "run.json")
                self.assertEqual(final_article["status"], "completed")


if __name__ == "__main__":
    unittest.main()
