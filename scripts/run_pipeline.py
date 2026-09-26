#!/usr/bin/env python3
"""Run article discovery and case enrichment with auditable state transitions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from source_catalog_io import (  # noqa: E402
    CATALOG_ROOT,
    find_entry_row,
    manifest_fields,
    parse_simple_yaml,
    read_catalog,
    require_batch_eligible,
    update_article,
)


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DEFINITIONS = {
    "0.1.0": ROOT / "pipeline" / "pipeline.v1.json",
    "0.1.1": ROOT / "pipeline" / "pipeline.v1.1.json",
    "0.1.2": ROOT / "pipeline" / "pipeline.v1.2.json",
    "0.2.0": ROOT / "pipeline" / "pipeline.v2.json",
}
DEFAULT_PIPELINE_VERSION = "0.2.0"
CONTRACT_DIR = ROOT / "pipeline" / "contracts"
PROMPT_DIR = ROOT / "pipeline" / "prompts"
DEDUP_RETRIEVAL_PATH = ROOT / "pipeline" / "retrieval" / "dedup_candidates.v1.json"
DEDUP_RETRIEVAL_V2_PATH = ROOT / "pipeline" / "retrieval" / "dedup_candidates.v2.json"
RIGHTS_DIR = ROOT / "data" / "rights_reviews"
DEFAULT_RECORD_DIR = ROOT / "data" / "run_records"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temp_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and Path(temp_name).exists():
            Path(temp_name).unlink()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def definition(pipeline_version: str = DEFAULT_PIPELINE_VERSION) -> dict[str, Any]:
    path = PIPELINE_DEFINITIONS.get(pipeline_version)
    if path is None:
        raise SystemExit(f"unsupported pipeline version: {pipeline_version}")
    value = load_json(path)
    if value.get("pipeline_version") != pipeline_version:
        raise SystemExit(f"pipeline definition version mismatch: {path}")
    return value


def stages_for(run: dict[str, Any]) -> list[dict[str, Any]]:
    key = "article_stages" if run["run_kind"] == "article" else "case_stages"
    return definition(run["pipeline_version"])[key]


def stage_definition(run: dict[str, Any], stage_id: str) -> dict[str, Any]:
    for stage in stages_for(run):
        if stage["id"] == stage_id:
            return stage
    raise SystemExit(f"unknown {run['run_kind']} stage: {stage_id}")


def output_path(run_dir: Path, stage_id: str) -> Path:
    return run_dir / "outputs" / f"{stage_id}.json"


def load_stage_output(run: dict[str, Any], run_dir: Path, stage_id: str) -> dict[str, Any]:
    local_path = output_path(run_dir, stage_id)
    if local_path.exists():
        return load_json(local_path)
    if run["run_kind"] == "case":
        parent_dir = Path(run["parent_article_run_path"])
        parent_path = output_path(parent_dir, stage_id)
        if parent_path.exists():
            return load_json(parent_path)
    raise SystemExit(f"missing upstream output: {stage_id}")


def validate_contract(
    response: dict[str, Any], contract: dict[str, Any], run: dict[str, Any], run_dir: Path
) -> None:
    errors: list[str] = []
    for field in contract["required_top_level"]:
        if field not in response:
            errors.append(f"missing top-level field: {field}")
    for array_name, rule in contract.get("array_rules", {}).items():
        items = response.get(array_name)
        if not isinstance(items, list):
            errors.append(f"{array_name} must be an array")
            continue
        if len(items) < rule.get("min_items", 0):
            errors.append(f"{array_name} has fewer than {rule['min_items']} items")
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{array_name}[{index}] must be an object")
                continue
            for field in rule.get("required_fields", []):
                if field not in item or item[field] in (None, "", []):
                    if rule.get("min_items") == 0 and field not in item:
                        errors.append(f"{array_name}[{index}] missing {field}")
                    elif item.get(field) in (None, "", []):
                        errors.append(f"{array_name}[{index}] missing {field}")
    allowed = contract.get("allowed_values", {})
    for field, values in allowed.items():
        if field in response and response[field] not in values:
            errors.append(f"invalid {field}: {response[field]}")
        for array_name in contract.get("array_rules", {}):
            for index, item in enumerate(response.get(array_name, [])):
                if field in item and item[field] not in values:
                    errors.append(f"invalid {array_name}[{index}].{field}: {item[field]}")
    for rule in contract.get("reference_rules", []):
        upstream = load_stage_output(run, run_dir, rule["source_stage"])
        valid_ids = {item[rule["source_id"]] for item in upstream[rule["source_array"]]}
        for index, item in enumerate(response.get(rule["array"], [])):
            references = item.get(rule["field"], [])
            if not isinstance(references, list) or not references:
                errors.append(f"{rule['array']}[{index}].{rule['field']} must be nonempty")
                continue
            missing = sorted(set(references) - valid_ids)
            if missing:
                errors.append(f"{rule['array']}[{index}].{rule['field']} has unknown IDs: {missing}")
    if errors:
        raise SystemExit("contract validation failed:\n- " + "\n- ".join(errors))


def validate_semantics(
    stage_id: str, response: dict[str, Any], run: dict[str, Any], run_dir: Path
) -> None:
    if "case_id" in response and response["case_id"] != run.get("case_id"):
        raise SystemExit("response case_id does not match run case_id")
    if "candidate_id" in response and response["candidate_id"] != run.get("candidate_id"):
        raise SystemExit("response candidate_id does not match run candidate_id")
    if stage_id in {"source_segmentation", "case_detection"}:
        if response["source_entry_id"] != run["source_entry_id"]:
            raise SystemExit("source_entry_id does not match run input")
    if stage_id == "source_segmentation":
        raw_text = load_json(Path(run["source_entry_path"]))["raw_text"]
        expected_start = 0
        seen_ids: set[str] = set()
        for expected_sequence, segment in enumerate(response["segments"], 1):
            if segment["sequence"] != expected_sequence:
                raise SystemExit("segment sequence must start at 1 and be contiguous")
            if segment["segment_id"] in seen_ids:
                raise SystemExit("segment_id values must be unique")
            seen_ids.add(segment["segment_id"])
            start = segment["start_offset"]
            end = segment["end_offset"]
            if not isinstance(start, int) or not isinstance(end, int):
                raise SystemExit("segment offsets must be integers")
            if start != expected_start or end <= start:
                raise SystemExit("segments must cover source text in order without gaps or overlap")
            if raw_text[start:end] != segment["content"]:
                raise SystemExit(f"segment offsets do not match source text: {segment['segment_id']}")
            if sha256_text(segment["content"]) != segment["content_hash"]:
                raise SystemExit(f"segment content_hash mismatch: {segment['segment_id']}")
            expected_start = end
        if expected_start != len(raw_text):
            raise SystemExit("segments do not cover the complete source text")
    if stage_id == "case_detection":
        candidate_ids = [item["candidate_id"] for item in response["case_candidates"]]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise SystemExit("candidate_id values must be unique")
        if run["pipeline_version"] == "0.2.0":
            for candidate_id in candidate_ids:
                if not re.fullmatch(r"[A-Za-z0-9_-]+", candidate_id):
                    raise SystemExit("candidate_id must be a safe path component")
    if run["pipeline_version"] == "0.2.0" and stage_id == "case_extraction":
        fact_ids = [item["case_fact_id"] for item in response["case_facts"]]
        if len(fact_ids) != len(set(fact_ids)):
            raise SystemExit("case_fact_id values must be unique")
        if not all(re.fullmatch(rf"{re.escape(run['candidate_id'])}-FACT\d{{4}}", value) for value in fact_ids):
            raise SystemExit("case_fact_id must use the candidate_id prefix before resolution")
        allowed_segments = set(run["case_candidate"]["supporting_source_segment_ids"])
        for fact in response["case_facts"]:
            if not set(fact["supporting_source_segment_ids"]) <= allowed_segments:
                raise SystemExit("case fact cites a Source Segment outside its candidate boundary")
    if run["pipeline_version"] == "0.2.0" and stage_id == "deduplication":
        request = load_json(run_dir / "requests" / "deduplication.json")
        expected_ids = {item["candidate_case_id"] for item in request["inputs"]["dedup_candidates"]}
        matches = response["candidate_matches"]
        actual_ids = [item["candidate_case_id"] for item in matches]
        if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != expected_ids:
            raise SystemExit("deduplication must compare every supplied candidate exactly once")
        if not isinstance(response["decision_reasons"], list) or not response["decision_reasons"]:
            raise SystemExit("deduplication requires decision reasons")
        decisions = {item["match_decision"] for item in matches}
        overall = response["overall_decision"]
        if overall == "new_case" and decisions - {"distinct_case"}:
            raise SystemExit("new_case requires every supplied candidate to be distinct")
        if overall == "same_case" and "same_case" not in decisions:
            raise SystemExit("same_case requires an identified matching candidate")
        if overall in {"possible_same_case", "needs_human_review"} and not (
            decisions & {"same_case", "possible_same_case", "needs_human_review"}
        ):
            raise SystemExit("review decision requires an ambiguous or matching candidate")
    if run["pipeline_version"] == "0.2.0" and stage_id == "source_occurrence":
        request = load_json(run_dir / "requests" / "source_occurrence.json")
        seed = request["inputs"]["occurrence_seed"]
        for field, value in seed.items():
            if response.get(field) != value:
                raise SystemExit(f"source_occurrence must preserve occurrence_seed.{field}")
        if not isinstance(response["locator"], dict) or not response["languages"]:
            raise SystemExit("source_occurrence requires a locator and language")
        known_ids = {item["occurrence_id"] for item in request["inputs"]["known_occurrences_for_case"]}
        for link in response["parent_links"]:
            target = link["target"]
            if not isinstance(target, dict) or target.get("state") not in {"known", "unresolved_upstream"}:
                raise SystemExit("parent link target needs known or unresolved_upstream state")
            if target["state"] == "known" and target.get("occurrence_id") not in known_ids:
                raise SystemExit("parent link points to an unknown occurrence")
            if target["state"] == "unresolved_upstream" and not target.get("description"):
                raise SystemExit("unresolved upstream needs a description")
            if not set(link["supporting_source_segment_ids"]) <= set(seed["supporting_source_segment_ids"]):
                raise SystemExit("parent link cites a segment outside this occurrence")
    if stage_id == "factual_check":
        unsupported = sum(c["verdict"] == "unsupported" for c in response["claims"])
        contradicted = sum(c["verdict"] == "contradicted" for c in response["claims"])
        if unsupported != response["unsupported_claim_count"]:
            raise SystemExit("unsupported_claim_count does not match claims")
        if contradicted != response["contradicted_claim_count"]:
            raise SystemExit("contradicted_claim_count does not match claims")
        expected = "pass" if unsupported == 0 and contradicted == 0 else "fail"
        if response["gate_result"] != expected:
            raise SystemExit(f"factual gate_result must be {expected}")
    if stage_id == "rights_check":
        if response["rights_review_id"] != run["rights_review_id"]:
            raise SystemExit("rights_check must use the run rights_review_id")
        expected_outputs = set(stage_definition(run, stage_id)["depends_on"])
        checked_outputs = [item["output_id"] for item in response["checks"]]
        if len(checked_outputs) != len(set(checked_outputs)):
            raise SystemExit("rights_check output_id values must be unique")
        missing_outputs = sorted(expected_outputs - set(checked_outputs))
        if missing_outputs:
            raise SystemExit(f"rights_check is missing required outputs: {missing_outputs}")
        unknown_outputs = sorted(set(checked_outputs) - expected_outputs)
        if unknown_outputs:
            raise SystemExit(f"rights_check contains undeclared outputs: {unknown_outputs}")
        if response["gate_result"] == "pass":
            failed_checks = [
                item["output_id"] for item in response["checks"]
                if item["policy_result"] != "pass"
            ]
            if failed_checks:
                raise SystemExit(f"rights_check cannot pass failed outputs: {failed_checks}")
        review = parse_simple_yaml(Path(run["rights_review_path"]))
        policy = review.get("public_display_policy", "")
        if policy.startswith("full_"):
            allowed = {"public", "public_excerpt_only", "internal", "restricted", "withheld"}
        elif "excerpt" in policy or "metadata_summary" in policy:
            allowed = {"public_excerpt_only", "internal", "restricted", "withheld"}
        elif "internal" in policy:
            allowed = {"internal", "restricted", "withheld"}
        elif "restricted" in policy:
            allowed = {"restricted", "withheld"}
        else:
            allowed = {"withheld"}
        if response["allowed_display_scope"] not in allowed:
            raise SystemExit("rights_check display scope exceeds source rights policy")


def sanitized_record(run: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "run_id", "run_kind", "pipeline_id", "pipeline_version", "source_id",
        "source_entry_id", "source_entry_hash", "source_catalog_article_id",
        "rights_review_id", "external_processing", "case_id", "candidate_id",
        "parent_article_run_id", "created_at", "updated_at", "status", "stages",
        "case_runs", "resolution_review",
    )
    return {key: run[key] for key in keep if key in run}


def write_run(run: dict[str, Any], run_dir: Path) -> None:
    atomic_json(run_dir / "run.json", run)
    record_dir = Path(run["record_dir"])
    atomic_json(record_dir / f"{run['run_id']}.json", sanitized_record(run))


def normalized_dedup_value(value: Any) -> str:
    normalized = unicodedata.normalize("NFKC", str(value)).strip().casefold()
    return re.sub(r"\s+", " ", normalized)


def dedup_features(
    extraction: dict[str, Any], tagging: dict[str, Any]
) -> dict[str, Any]:
    persons: set[str] = set()
    for person in tagging.get("persons", []):
        if person.get("name_status") in {"anonymous", "unknown", "redacted"}:
            continue
        for field in ("display_name", "source_name"):
            value = normalized_dedup_value(person.get(field, ""))
            if value:
                persons.add(value)

    places: set[str] = set()
    for place in tagging.get("places", []):
        for field in ("display_name", "source_name"):
            value = normalized_dedup_value(place.get(field, ""))
            if value:
                places.add(value)

    dates: set[str] = set()
    for fact in extraction.get("case_facts", []):
        if fact.get("fact_type") != "date":
            continue
        for field in ("date_value", "normalized_value"):
            value = normalized_dedup_value(fact.get(field, ""))
            if value:
                dates.add(value)

    tags: dict[str, str] = {}
    for item in tagging.get("tags", []):
        value = normalized_dedup_value(item.get("tag", ""))
        if value:
            tags[value] = item.get("tag_class", "default")
    return {"persons": persons, "places": places, "dates": dates, "tags": tags}


def score_dedup_candidate(
    current: dict[str, Any], candidate: dict[str, Any], same_source_entry: bool,
    config: dict[str, Any],
) -> tuple[int, list[str]]:
    weights = config["weights"]
    score = 0
    reasons: list[str] = []
    if same_source_entry:
        score += weights["same_source_entry"]
        reasons.append("same_source_entry")

    for value in sorted(current["persons"] & candidate["persons"]):
        score += weights["person_exact"]
        reasons.append(f"person_exact:{value}")
    place_matches = sorted(current["places"] & candidate["places"])
    date_matches = sorted(current["dates"] & candidate["dates"])
    for value in date_matches:
        score += weights["date_exact"]
        reasons.append(f"date_exact:{value}")
    for value in place_matches:
        score += weights["place_exact"]
        reasons.append(f"place_exact:{value}")
    if place_matches and date_matches:
        score += weights["place_and_date"]
        reasons.append("place_and_date")

    ignored_classes = set(config["ignored_tag_classes"])
    tag_weights = weights["tag_by_class"]
    for value in sorted(set(current["tags"]) & set(candidate["tags"])):
        tag_class = current["tags"].get(value) or candidate["tags"].get(value) or "default"
        if tag_class in ignored_classes:
            continue
        score += tag_weights.get(tag_class, tag_weights["default"])
        reasons.append(f"tag_exact:{tag_class}:{value}")
    return score, reasons


def dedup_candidate_context(run: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    config = load_json(DEDUP_RETRIEVAL_PATH)
    current_extraction = load_stage_output(run, run_dir, "case_extraction")
    current_tagging = load_stage_output(run, run_dir, "entity_tagging")
    current_features = dedup_features(current_extraction, current_tagging)
    runtime_root = Path(run["parent_article_run_path"]).parent

    latest_by_case: dict[str, tuple[Path, dict[str, Any]]] = {}
    for candidate_run_path in runtime_root.glob("*/cases/*/run.json"):
        candidate_run = load_json(candidate_run_path)
        candidate_case_id = candidate_run.get("case_id", "")
        if (
            candidate_run.get("run_kind") != "case"
            or candidate_run.get("status") != "completed"
            or not candidate_case_id
            or candidate_case_id == run["case_id"]
        ):
            continue
        previous = latest_by_case.get(candidate_case_id)
        if previous is None or candidate_run.get("updated_at", "") > previous[1].get("updated_at", ""):
            latest_by_case[candidate_case_id] = (candidate_run_path.parent, candidate_run)

    scored: list[dict[str, Any]] = []
    for candidate_case_id, (candidate_dir, candidate_run) in latest_by_case.items():
        extraction = load_json(output_path(candidate_dir, "case_extraction"))
        tagging = load_json(output_path(candidate_dir, "entity_tagging"))
        candidate_features = dedup_features(extraction, tagging)
        score, reasons = score_dedup_candidate(
            current_features,
            candidate_features,
            candidate_run.get("source_entry_id") == run["source_entry_id"],
            config,
        )
        if score < config["minimum_score"]:
            continue
        scored.append({
            "candidate_case_id": candidate_case_id,
            "source_id": candidate_run.get("source_id", ""),
            "source_entry_id": candidate_run.get("source_entry_id", ""),
            "pipeline_version": candidate_run.get("pipeline_version", ""),
            "external_processing": candidate_run.get("external_processing", "blocked"),
            "selection_score": score,
            "selection_reasons": reasons,
            "case_facts": extraction.get("case_facts", []),
            "persons": tagging.get("persons", []),
            "places": tagging.get("places", []),
            "tags": tagging.get("tags", []),
        })
    scored.sort(key=lambda item: (-item["selection_score"], item["candidate_case_id"]))
    selected = scored[:config["limit"]]
    requires_local = any(item["external_processing"] != "allowed" for item in selected)
    metadata = {
        "retrieval_version": config["retrieval_version"],
        "scope": config["scope"],
        "eligible_completed_case_count": len(latest_by_case),
        "scored_candidate_count": len(scored),
        "selected_candidate_count": len(selected),
        "limit": config["limit"],
        "minimum_score": config["minimum_score"],
        "requires_local_adapter": requires_local,
        "selection_rules": config["selection_rules"],
    }
    return {"metadata": metadata, "candidates": selected}


def completed_local_case_runs(runtime_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    paths = sorted(runtime_root.glob("*/cases/*/run.json"))
    paths += sorted(runtime_root.glob("*/candidates/*/run.json"))
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        value = load_json(path)
        if value.get("run_kind") == "case" and value.get("status") == "completed" and value.get("case_id"):
            result.append((path.parent, value))
    return result


def dedup_candidate_context_v2(run: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    config = load_json(DEDUP_RETRIEVAL_V2_PATH)
    current = dedup_features(
        load_stage_output(run, run_dir, "case_extraction"),
        load_stage_output(run, run_dir, "entity_tagging"),
    )
    runtime_root = Path(run["parent_article_run_path"]).parent
    grouped: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for candidate_dir, candidate_run in completed_local_case_runs(runtime_root):
        if candidate_run.get("run_id") != run["run_id"]:
            grouped.setdefault(candidate_run["case_id"], []).append((candidate_dir, candidate_run))

    scored: list[dict[str, Any]] = []
    for case_id, versions in grouped.items():
        best: dict[str, Any] | None = None
        occurrences: dict[str, dict[str, Any]] = {}
        for candidate_dir, candidate_run in versions:
            extraction = load_json(output_path(candidate_dir, "case_extraction"))
            tagging = load_json(output_path(candidate_dir, "entity_tagging"))
            score, reasons = score_dedup_candidate(
                current, dedup_features(extraction, tagging),
                candidate_run["source_entry_id"] == run["source_entry_id"], config,
            )
            occurrence_path = output_path(candidate_dir, "source_occurrence")
            if occurrence_path.exists():
                occurrence = load_json(occurrence_path)
                occurrences[occurrence["occurrence_id"]] = {
                    "occurrence_id": occurrence["occurrence_id"],
                    "source_id": occurrence["source_id"],
                    "source_entry_id": occurrence["source_entry_id"],
                    "locator": occurrence["locator"],
                    "parent_links": occurrence["parent_links"],
                }
            if best is None or (score, candidate_run.get("updated_at", "")) > (
                best["selection_score"], best["updated_at"]
            ):
                best = {
                    "candidate_case_id": case_id,
                    "source_id": candidate_run["source_id"],
                    "source_entry_id": candidate_run["source_entry_id"],
                    "pipeline_version": candidate_run["pipeline_version"],
                    "selection_score": score,
                    "selection_reasons": reasons,
                    "case_facts": extraction["case_facts"],
                    "persons": tagging["persons"],
                    "places": tagging["places"],
                    "tags": tagging["tags"],
                    "updated_at": candidate_run.get("updated_at", ""),
                }
        assert best is not None
        if best["selection_score"] >= config["minimum_score"]:
            best.pop("updated_at")
            best["source_occurrences"] = [occurrences[key] for key in sorted(occurrences)]
            best["external_processing"] = (
                "allowed" if all(item[1].get("external_processing") == "allowed" for item in versions)
                else "blocked"
            )
            scored.append(best)

    scored.sort(key=lambda item: (-item["selection_score"], item["candidate_case_id"]))
    selected = scored[:config["limit"]]
    metadata = {
        "retrieval_version": config["retrieval_version"],
        "scope": config["scope"],
        "eligible_completed_case_count": len(grouped),
        "scored_candidate_count": len(scored),
        "selected_candidate_count": len(selected),
        "limit": config["limit"],
        "minimum_score": config["minimum_score"],
        "requires_local_adapter": any(item["external_processing"] != "allowed" for item in selected),
        "selection_rules": config["selection_rules"],
    }
    return {"metadata": metadata, "candidates": selected}


def known_occurrences_for_case(run: dict[str, Any]) -> list[dict[str, Any]]:
    runtime_root = Path(run["parent_article_run_path"]).parent
    found: dict[str, dict[str, Any]] = {}
    for candidate_dir, candidate_run in completed_local_case_runs(runtime_root):
        if candidate_run["case_id"] != run["case_id"]:
            continue
        path = output_path(candidate_dir, "source_occurrence")
        if path.exists():
            occurrence = load_json(path)
            found[occurrence["occurrence_id"]] = {
                "occurrence_id": occurrence["occurrence_id"],
                "source_id": occurrence["source_id"],
                "source_entry_id": occurrence["source_entry_id"],
                "locator": occurrence["locator"],
            }
    return [found[key] for key in sorted(found)]


def occurrence_seed(run: dict[str, Any]) -> dict[str, Any]:
    entry = load_json(Path(run["source_entry_path"]))
    segment_ids = run["case_candidate"]["supporting_source_segment_ids"]
    key = "|".join((run["source_entry_id"], run["candidate_id"], *sorted(segment_ids)))
    return {
        "occurrence_id": "OCC" + sha256_text(key)[:16].upper(),
        "case_id": run["case_id"],
        "source_id": run["source_id"],
        "source_item_id": run["source_catalog_article_id"],
        "source_entry_id": run["source_entry_id"],
        "supporting_source_segment_ids": segment_ids,
        "locator": {"type": "source_segments", "source_locator": entry.get("locator_text", ""), "segment_ids": segment_ids},
        "languages": [entry.get("language") or "unknown"],
    }


def request_payload(run: dict[str, Any], run_dir: Path, stage: dict[str, Any]) -> dict[str, Any]:
    inputs: dict[str, Any] = {
        "source_entry": load_json(Path(run["source_entry_path"])),
    }
    if run["run_kind"] == "case":
        if "case_id" in run:
            inputs["case_id"] = run["case_id"]
        inputs["candidate_id"] = run["candidate_id"]
        inputs["case_candidate"] = run["case_candidate"]
        inputs["source_segmentation"] = load_stage_output(run, run_dir, "source_segmentation")
    for dependency in stage["depends_on"]:
        dependency_path = output_path(run_dir, dependency)
        if dependency_path.exists():
            inputs[dependency] = load_json(dependency_path)
        else:
            inputs[dependency] = run["stages"][dependency]
    if stage["id"] == "deduplication" and run["pipeline_version"] == "0.1.2":
        retrieval = dedup_candidate_context(run, run_dir)
        inputs["dedup_candidate_retrieval"] = retrieval["metadata"]
        inputs["dedup_candidates"] = retrieval["candidates"]
    if stage["id"] == "deduplication" and run["pipeline_version"] == "0.2.0":
        retrieval = dedup_candidate_context_v2(run, run_dir)
        inputs["dedup_candidate_retrieval"] = retrieval["metadata"]
        inputs["dedup_candidates"] = retrieval["candidates"]
    if stage["id"] == "source_occurrence" and run["pipeline_version"] == "0.2.0":
        inputs["occurrence_seed"] = occurrence_seed(run)
        inputs["known_occurrences_for_case"] = known_occurrences_for_case(run)
    inputs["rights_review"] = parse_simple_yaml(Path(run["rights_review_path"]))
    prompt_path = PROMPT_DIR / stage["prompt"]
    return {
        "run_id": run["run_id"],
        "pipeline_version": run["pipeline_version"],
        "stage": stage["id"],
        "prompt_version": stage["prompt"],
        "prompt": prompt_path.read_text(encoding="utf-8"),
        "contract": load_json(CONTRACT_DIR / stage["contract"]),
        "inputs": inputs,
    }


def next_ready_stage(run: dict[str, Any]) -> str:
    for stage in stages_for(run):
        if run["stages"][stage["id"]]["status"] == "ready":
            return stage["id"]
    return ""


def publication_blockers(run: dict[str, Any], run_dir: Path) -> list[str]:
    blockers: list[str] = []
    factual = load_stage_output(run, run_dir, "factual_check")
    rights = load_stage_output(run, run_dir, "rights_check")
    if factual["gate_result"] != "pass":
        blockers.append("factual_check_failed")
    if rights["gate_result"] != "pass":
        blockers.append("rights_check_failed")
    if run["pipeline_version"] == "0.1.2":
        dedup = load_stage_output(run, run_dir, "deduplication")
        if dedup["decision"] not in {"no_match", "distinct_case"}:
            blockers.append(f"deduplication_unresolved:{dedup['decision']}")
    if run["pipeline_version"] == "0.2.0":
        occurrence = load_stage_output(run, run_dir, "source_occurrence")
        if occurrence["review_status"] == "needs_review":
            blockers.append("source_occurrence_needs_review")
    return blockers


def publication_rights_notice(run: dict[str, Any]) -> dict[str, Any] | None:
    review = parse_simple_yaml(Path(run["rights_review_path"]))
    if review.get("rights_status") != "open_license_verified":
        return None
    manifest = manifest_fields(run["source_entry_id"])
    return {
        "rights_review_id": review["rights_review_id"],
        "rights_holder": review.get("rights_holder", ""),
        "license_type": review.get("license_type", ""),
        "license_url": manifest["license_url"],
        "terms_url": manifest["terms_url"],
        "source_version": manifest["source_version"],
        "source_revision": manifest["source_revision"],
        "modification_notice": manifest["modification_notice"],
        "commercial_use_policy": review.get("commercial_use_policy", ""),
        "dataset_distribution_policy": review.get("dataset_distribution_policy", ""),
    }


def complete_case_resolution(
    run: dict[str, Any], run_dir: Path, resolution_kind: str, decision_basis: str,
    reviewer_id: str = "", reason: str = "", target_case_id: str = "",
) -> None:
    if output_path(run_dir, "case_resolution").exists():
        raise SystemExit("case_resolution output already exists")
    if resolution_kind == "new":
        case_id = allocate_case_ids(1, Path(run["record_dir"]))[0]
    elif resolution_kind == "reuse":
        if not re.fullmatch(r"CASE\d{6}", target_case_id):
            raise SystemExit("reuse requires an existing CASE ID")
        candidate_ids = {
            item["candidate_case_id"] for item in
            load_json(run_dir / "requests/deduplication.json")["inputs"]["dedup_candidates"]
        }
        candidate_ids.update(run.get("preexisting_case_ids", []))
        if target_case_id not in candidate_ids or int(target_case_id[4:]) not in existing_case_numbers(Path(run["record_dir"])):
            raise SystemExit("reuse target is not a known candidate or prior catalog case")
        case_id = target_case_id
    else:
        raise SystemExit(f"unknown resolution kind: {resolution_kind}")
    if decision_basis == "human_review" and (not reviewer_id.strip() or not reason.strip()):
        raise SystemExit("human identity resolution requires reviewer and reason")
    result = {
        "candidate_id": run["candidate_id"],
        "case_id": case_id,
        "resolution_kind": resolution_kind,
        "decision_basis": decision_basis,
        "dedup_scope": load_json(run_dir / "requests/deduplication.json")["inputs"]["dedup_candidate_retrieval"]["scope"],
    }
    if decision_basis == "human_review":
        result["reviewer_id"] = reviewer_id.strip()
        result["reason"] = reason.strip()
        run["resolution_review"] = {"reviewer_id": reviewer_id.strip(), "reason": reason.strip(), "action": resolution_kind}
    atomic_json(output_path(run_dir, "case_resolution"), result)
    run["case_id"] = case_id
    run["stages"]["case_resolution"].update({
        "status": "completed", "completed_at": utc_now(),
        "output_hash": sha256_file(output_path(run_dir, "case_resolution")),
    })
    row = find_entry_row(run["source_id"], run["source_entry_id"])
    linked = [item for item in row.get("case_ids", "").split(";") if item]
    if case_id not in linked:
        linked.append(case_id)
        update_article(run["source_id"], run["source_catalog_article_id"], {"case_ids": ";".join(linked)})


def refresh(run: dict[str, Any], run_dir: Path) -> None:
    for stage in stages_for(run):
        stage_id = stage["id"]
        state = run["stages"][stage_id]
        if state["status"] != "pending":
            continue
        if not all(run["stages"][dep]["status"] == "completed" for dep in stage["depends_on"]):
            continue
        if stage_id == "case_resolution" and run["pipeline_version"] == "0.2.0":
            decision = load_stage_output(run, run_dir, "deduplication")["overall_decision"]
            if decision == "new_case" and not run["preexisting_case_ids"]:
                complete_case_resolution(run, run_dir, "new", "scoped_no_match")
                continue
            state["status"] = "review_required"
            state["reason"] = (
                "prior catalog case mapping requires review"
                if decision == "new_case" else f"deduplication decision: {decision}"
            )
            run["status"] = "blocked"
            return
        if stage_id == "publication_packaging":
            rights = load_stage_output(run, run_dir, "rights_check")
            publish_status = rights["allowed_display_scope"]
            blockers = publication_blockers(run, run_dir)
            if blockers:
                publish_status = "withheld"
            package = {
                "case_id": run["case_id"],
                "publish_status": publish_status,
                "withheld_reasons": blockers,
                "included_output_ids": ["reader_generation", "creator_analysis"],
                "provenance": {
                    "run_id": run["run_id"],
                    "pipeline_version": run["pipeline_version"],
                    "source_entry_hash": run["source_entry_hash"],
                },
            }
            rights_notice = publication_rights_notice(run)
            if rights_notice:
                package["rights_notice"] = rights_notice
            atomic_json(output_path(run_dir, stage_id), package)
            state.update({"status": "completed", "completed_at": utc_now(), "output_hash": sha256_file(output_path(run_dir, stage_id))})
            run["status"] = "completed"
            continue
        if stage.get("executor") == "deterministic":
            raise SystemExit(f"deterministic stage has no runner implementation: {stage_id}")
        request_path = run_dir / "requests" / f"{stage_id}.json"
        payload = request_payload(run, run_dir, stage)
        atomic_json(request_path, payload)
        state.update({"status": "ready", "request_hash": sha256_file(request_path)})
        retrieval = payload["inputs"].get("dedup_candidate_retrieval")
        if retrieval:
            state["external_processing"] = (
                "blocked" if retrieval["requires_local_adapter"] else run["external_processing"]
            )
            candidate_text = json.dumps(
                payload["inputs"]["dedup_candidates"], ensure_ascii=False,
                sort_keys=True, separators=(",", ":"),
            )
            state["candidate_set_hash"] = sha256_text(candidate_text)


def rights_precheck(entry: dict[str, Any], entry_path: Path) -> dict[str, Any]:
    source_id = entry.get("source_id", "")
    if not source_id:
        raise SystemExit("source entry must include source_id")
    config, _ = read_catalog(source_id)
    row = find_entry_row(source_id, entry["source_entry_id"])
    require_batch_eligible(row)
    review_id = row.get("rights_review_id", "") or config.get("rights_review_id", "")
    if not review_id:
        raise SystemExit("article catalog must identify a rights review")
    review_path = RIGHTS_DIR / f"{review_id}.yml"
    review = parse_simple_yaml(review_path)
    if review.get("source_id") != source_id:
        raise SystemExit("rights review source_id mismatch")
    if review.get("rights_status") != row["rights_status"]:
        raise SystemExit("rights review status differs from article catalog")
    manifest = manifest_fields(entry["source_entry_id"])
    if manifest.get("source_id") != source_id or manifest.get("raw_capture_status") != "persisted_verified":
        raise SystemExit("source manifest is not verified for this source")
    if manifest.get("rights_review_id") != review_id:
        raise SystemExit("source manifest rights review differs from article catalog")
    if manifest.get("rights_status") != review.get("rights_status"):
        raise SystemExit("source manifest rights status differs from rights review")
    if manifest.get("public_display_policy") != review.get("public_display_policy"):
        raise SystemExit("source manifest public display policy differs from rights review")
    if review.get("rights_status") == "open_license_verified":
        required_license_fields = (
            "license_url", "terms_url", "terms_checked_at", "source_version",
            "source_revision", "modification_notice",
        )
        missing = [field for field in required_license_fields if not manifest.get(field)]
        if missing:
            raise SystemExit(f"open-license source manifest is missing: {', '.join(missing)}")
    if manifest.get("normalized_storage_uri") != str(entry_path.relative_to(ROOT)):
        raise SystemExit("source manifest normalized path mismatch")
    if manifest.get("normalized_artifact_hash") != sha256_file(entry_path):
        raise SystemExit("source manifest normalized hash mismatch")
    external_allowed = (
        config.get("external_processing_default") == "allowed"
        and review.get("external_ai_processing_policy", "").startswith("allowed")
    )
    return {
        "config": config,
        "row": row,
        "review": review,
        "review_path": review_path,
        "external_processing": "allowed" if external_allowed else "blocked",
    }


def create_article_run(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.resolve()
    if run_dir.exists():
        raise SystemExit(f"run directory already exists: {run_dir}")
    entry_path = args.entry.resolve()
    entry = load_json(entry_path)
    if entry.get("raw_text_hash") != sha256_text(entry.get("raw_text", "")):
        raise SystemExit("source entry raw_text_hash does not match raw_text")
    precheck = rights_precheck(entry, entry_path)
    pipeline = definition(getattr(args, "pipeline_version", DEFAULT_PIPELINE_VERSION))
    run = {
        "run_id": run_dir.name,
        "run_kind": "article",
        "pipeline_id": pipeline["pipeline_id"],
        "pipeline_version": pipeline["pipeline_version"],
        "source_id": entry["source_id"],
        "source_entry_id": entry["source_entry_id"],
        "source_entry_path": str(entry_path),
        "source_entry_hash": sha256_file(entry_path),
        "source_catalog_article_id": precheck["row"]["article_id"],
        "preexisting_case_ids": [value for value in precheck["row"].get("case_ids", "").split(";") if value],
        "rights_review_id": precheck["review"]["rights_review_id"],
        "rights_review_path": str(precheck["review_path"]),
        "external_processing": precheck["external_processing"],
        "record_dir": str(args.record_dir.resolve()),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "status": "running",
        "stages": {stage["id"]: {"status": "pending"} for stage in pipeline["article_stages"]},
        "case_runs": [],
    }
    for stage_id, evidence in (
        ("source_registration", entry["source_id"]),
        ("rights_precheck", precheck["review"]["rights_review_id"]),
        ("source_capture", entry["raw_text_hash"]),
    ):
        run["stages"][stage_id] = {"status": "completed", "completed_at": utc_now(), "evidence": evidence}
    run_dir.mkdir(parents=True)
    for directory in ("requests", "responses", "outputs", "checks", "cases"):
        (run_dir / directory).mkdir()
    refresh(run, run_dir)
    write_run(run, run_dir)
    update_article(entry["source_id"], precheck["row"]["article_id"], {
        "pipeline_status": "running", "current_stage": "source_segmentation",
        "last_run_id": run["run_id"], "last_checked_at": utc_now()[:10],
    })
    print(f"created article run {run['run_id']}; next stage: source_segmentation")


def existing_case_numbers(record_dir: Path) -> set[int]:
    numbers: set[int] = set()
    for path in record_dir.glob("*.json"):
        match = re.fullmatch(r"CASE(\d{6})", str(load_json(path).get("case_id", "")))
        if match:
            numbers.add(int(match.group(1)))
    for pattern in ("data/legacy_m2/CASE*.md",):
        for path in ROOT.glob(pattern):
            match = re.match(r"CASE(\d{6})", path.name)
            if match:
                numbers.add(int(match.group(1)))
    for source_dir in CATALOG_ROOT.glob("SRC*"):
        if not source_dir.is_dir():
            continue
        _, rows = read_catalog(source_dir.name)
        for row in rows:
            for case_id in row.get("case_ids", "").split(";"):
                match = re.fullmatch(r"CASE(\d{6})", case_id)
                if match:
                    numbers.add(int(match.group(1)))
    return numbers


def allocate_case_ids(count: int, record_dir: Path) -> list[str]:
    used = existing_case_numbers(record_dir)
    next_number = max(used, default=0) + 1
    result: list[str] = []
    while len(result) < count:
        if next_number not in used:
            result.append(f"CASE{next_number:06d}")
        next_number += 1
    return result


def spawn_case_runs(article_run: dict[str, Any], article_dir: Path, candidates: list[dict[str, Any]]) -> None:
    record_dir = Path(article_run["record_dir"])
    preexisting = article_run.get("preexisting_case_ids", [])
    pipeline = definition(article_run["pipeline_version"])
    if article_run["pipeline_version"] == "0.2.0":
        for candidate in candidates:
            candidate_id = candidate["candidate_id"]
            child_id = f"{article_run['run_id']}-{candidate_id}"
            child_dir = article_dir / "candidates" / candidate_id
            child = {
                "run_id": child_id,
                "run_kind": "case",
                "pipeline_id": pipeline["pipeline_id"],
                "pipeline_version": pipeline["pipeline_version"],
                "parent_article_run_id": article_run["run_id"],
                "parent_article_run_path": str(article_dir),
                "source_id": article_run["source_id"],
                "source_entry_id": article_run["source_entry_id"],
                "source_entry_path": article_run["source_entry_path"],
                "source_entry_hash": article_run["source_entry_hash"],
                "source_catalog_article_id": article_run["source_catalog_article_id"],
                "preexisting_case_ids": preexisting,
                "rights_review_id": article_run["rights_review_id"],
                "rights_review_path": article_run["rights_review_path"],
                "external_processing": article_run["external_processing"],
                "record_dir": article_run["record_dir"],
                "candidate_id": candidate_id,
                "case_candidate": candidate,
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "status": "running",
                "stages": {stage["id"]: {"status": "pending"} for stage in pipeline["case_stages"]},
            }
            for directory in ("requests", "responses", "outputs", "checks"):
                (child_dir / directory).mkdir(parents=True, exist_ok=True)
            refresh(child, child_dir)
            write_run(child, child_dir)
            article_run["case_runs"].append({"candidate_id": candidate_id, "run_id": child_id, "status": "running"})
        article_run["status"] = "completed" if not candidates else "case_runs_active"
        article_run["updated_at"] = utc_now()
        update_article(article_run["source_id"], article_run["source_catalog_article_id"], {
            "pipeline_status": "completed" if not candidates else "running",
            "current_stage": "" if not candidates else "case_extraction",
            "machine_review_status": "passed" if not candidates else "not_reviewed",
            "last_checked_at": utc_now()[:10],
        })
        return
    case_ids = preexisting if len(preexisting) == len(candidates) else allocate_case_ids(len(candidates), record_dir)
    for case_id, candidate in zip(case_ids, candidates):
        child_id = f"{article_run['run_id']}-{case_id}"
        child_dir = article_dir / "cases" / case_id
        child = {
            "run_id": child_id,
            "run_kind": "case",
            "pipeline_id": pipeline["pipeline_id"],
            "pipeline_version": pipeline["pipeline_version"],
            "parent_article_run_id": article_run["run_id"],
            "parent_article_run_path": str(article_dir),
            "source_id": article_run["source_id"],
            "source_entry_id": article_run["source_entry_id"],
            "source_entry_path": article_run["source_entry_path"],
            "source_entry_hash": article_run["source_entry_hash"],
            "source_catalog_article_id": article_run["source_catalog_article_id"],
            "rights_review_id": article_run["rights_review_id"],
            "rights_review_path": article_run["rights_review_path"],
            "external_processing": article_run["external_processing"],
            "record_dir": article_run["record_dir"],
            "case_id": case_id,
            "candidate_id": candidate["candidate_id"],
            "case_candidate": candidate,
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "status": "running",
            "stages": {stage["id"]: {"status": "pending"} for stage in pipeline["case_stages"]},
        }
        for directory in ("requests", "responses", "outputs", "checks"):
            (child_dir / directory).mkdir(parents=True, exist_ok=True)
        refresh(child, child_dir)
        write_run(child, child_dir)
        article_run["case_runs"].append({"case_id": case_id, "candidate_id": candidate["candidate_id"], "run_id": child_id, "status": "running"})
    article_run["status"] = "completed" if not candidates else "case_runs_active"
    article_run["updated_at"] = utc_now()
    case_id_text = ";".join(case_ids)
    update_article(article_run["source_id"], article_run["source_catalog_article_id"], {
        "case_ids": case_id_text,
        "pipeline_status": "completed" if not candidates else "running",
        "current_stage": "" if not candidates else "case_extraction",
        "machine_review_status": "passed" if not candidates else "not_reviewed",
        "last_checked_at": utc_now()[:10],
    })


def sync_parent(child: dict[str, Any]) -> None:
    parent_dir = Path(child["parent_article_run_path"])
    parent = load_json(parent_dir / "run.json")
    for item in parent["case_runs"]:
        if item["run_id"] == child["run_id"]:
            item["status"] = child["status"]
            if "case_id" in child:
                item["case_id"] = child["case_id"]
    failed = any(item["status"] == "failed" for item in parent["case_runs"])
    blocked = any(item["status"] == "blocked" for item in parent["case_runs"])
    complete = all(item["status"] == "completed" for item in parent["case_runs"])
    parent["status"] = "failed" if failed else ("blocked" if blocked else ("completed" if complete else "case_runs_active"))
    parent["updated_at"] = utc_now()
    write_run(parent, parent_dir)
    update_article(parent["source_id"], parent["source_catalog_article_id"], {
        "pipeline_status": "failed" if failed else ("blocked" if blocked else ("completed" if complete else "running")),
        "current_stage": "" if complete else "case_runs",
        "machine_review_status": "failed" if failed else ("passed" if complete else "not_reviewed"),
        "last_run_id": child["run_id"],
        "last_checked_at": utc_now()[:10],
    })


def accept_response(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.resolve()
    run = load_json(run_dir / "run.json")
    stage = stage_definition(run, args.stage)
    if stage.get("executor") != "ai":
        raise SystemExit(f"stage does not accept an AI response: {args.stage}")
    state = run["stages"][args.stage]
    if state["status"] != "ready":
        raise SystemExit(f"stage is not ready: {args.stage} ({state['status']})")
    request_path = run_dir / "requests" / f"{args.stage}.json"
    if not request_path.exists() or sha256_file(request_path) != state["request_hash"]:
        raise SystemExit(f"request hash mismatch: {args.stage}")
    stage_processing = state.get("external_processing", run["external_processing"])
    if args.adapter != "local" and stage_processing != "allowed":
        raise SystemExit("external adapter blocked for this stage by source or candidate rights policy")
    response = load_json(args.response.resolve())
    contract = load_json(CONTRACT_DIR / stage["contract"])
    validate_contract(response, contract, run, run_dir)
    validate_semantics(args.stage, response, run, run_dir)
    response_target = run_dir / "responses" / f"{args.stage}.json"
    output_target = output_path(run_dir, args.stage)
    if response_target.exists() or output_target.exists():
        raise SystemExit("stage output already exists; create a new run instead of overwriting")
    shutil.copyfile(args.response.resolve(), response_target)
    atomic_json(output_target, response)
    state.update({
        "status": "completed", "completed_at": utc_now(), "adapter": args.adapter,
        "model": args.model, "response_hash": sha256_file(response_target),
        "output_hash": sha256_file(output_target),
    })
    run["updated_at"] = utc_now()
    refresh(run, run_dir)
    if run["run_kind"] == "article" and args.stage == "case_detection":
        spawn_case_runs(run, run_dir, response["case_candidates"])
    write_run(run, run_dir)
    if run["run_kind"] == "article" and args.stage != "case_detection":
        update_article(run["source_id"], run["source_catalog_article_id"], {
            "current_stage": next_ready_stage(run), "last_run_id": run["run_id"],
            "last_checked_at": utc_now()[:10],
        })
    if run["run_kind"] == "case":
        update_article(run["source_id"], run["source_catalog_article_id"], {
            "current_stage": next_ready_stage(run) or "case_runs",
            "last_run_id": run["run_id"], "last_checked_at": utc_now()[:10],
        })
        if run["status"] in {"completed", "blocked"}:
            sync_parent(run)
    print(f"accepted {args.stage}")


def run_stage_with_adapter(args: argparse.Namespace) -> None:
    import ai_adapter

    run_dir = args.run_dir.resolve()
    run = load_json(run_dir / "run.json")
    stage = stage_definition(run, args.stage)
    if stage.get("executor") != "ai":
        raise SystemExit(f"stage is not AI-executed: {args.stage}")
    state = run["stages"][args.stage]
    if state["status"] != "ready":
        raise SystemExit(f"stage is not ready: {args.stage} ({state['status']})")
    stage_processing = state.get("external_processing", run["external_processing"])
    if stage_processing != "allowed":
        raise SystemExit("external adapter blocked for this stage by source or candidate rights policy")
    request_path = run_dir / "requests" / f"{args.stage}.json"
    if not request_path.exists() or sha256_file(request_path) != state["request_hash"]:
        raise SystemExit(f"request hash mismatch: {args.stage}")
    request = load_json(request_path)
    result = ai_adapter.call_with_retry(
        args.provider,
        request,
        config_path=args.config,
        log_context={"run_id": run["run_id"]},
    )
    response_path = run_dir / "checks" / f"{args.stage}.adapter_response.json"
    atomic_json(response_path, result["response"])
    accept_args = argparse.Namespace(
        run_dir=run_dir,
        stage=args.stage,
        response=response_path,
        adapter=args.provider,
        model=result["model"],
    )
    accept_response(accept_args)
    response_path.unlink()
    run = load_json(run_dir / "run.json")
    run["stages"][args.stage]["api_call"] = result["summary"]
    write_run(run, run_dir)
    print(f"accepted {args.stage} via {args.provider}")


def fail_run(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.resolve()
    run = load_json(run_dir / "run.json")
    stage_id = args.stage or next_ready_stage(run)
    if not stage_id or stage_id not in run["stages"]:
        raise SystemExit("no stage available to fail")
    run["stages"][stage_id] = {"status": "failed", "failed_at": utc_now(), "reason": args.reason}
    run["status"] = "failed"
    run["updated_at"] = utc_now()
    write_run(run, run_dir)
    row = find_entry_row(run["source_id"], run["source_entry_id"])
    note = f"{row['notes']} | {args.reason}" if row["notes"] else args.reason
    update_article(run["source_id"], run["source_catalog_article_id"], {
        "pipeline_status": "failed", "current_stage": stage_id,
        "last_run_id": run["run_id"], "machine_review_status": "failed",
        "last_checked_at": utc_now()[:10], "notes": note,
    })
    if run["run_kind"] == "case":
        sync_parent(run)
    print(f"failed {run['run_id']} at {stage_id}")


def resolve_identity(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.resolve()
    run = load_json(run_dir / "run.json")
    if run["run_kind"] != "case" or run["pipeline_version"] != "0.2.0":
        raise SystemExit("identity resolution requires a v0.2 candidate run")
    if run["status"] != "blocked" or run["stages"]["case_resolution"]["status"] != "review_required":
        raise SystemExit("case_resolution is not awaiting human review")
    complete_case_resolution(
        run, run_dir, args.action, "human_review",
        reviewer_id=args.reviewer, reason=args.reason, target_case_id=args.case_id,
    )
    run["status"] = "running"
    run["updated_at"] = utc_now()
    refresh(run, run_dir)
    write_run(run, run_dir)
    sync_parent(run)
    update_article(run["source_id"], run["source_catalog_article_id"], {
        "current_stage": next_ready_stage(run) or "case_runs",
        "last_run_id": run["run_id"], "last_checked_at": utc_now()[:10],
    })
    print(f"resolved {run['candidate_id']} as {run['case_id']} ({args.action})")


def show_status(args: argparse.Namespace) -> None:
    run = load_json(args.run_dir.resolve() / "run.json")
    identity = run.get("case_id", run.get("candidate_id", run["source_entry_id"]))
    print(f"{run['run_id']} kind={run['run_kind']} pipeline={run['pipeline_version']} item={identity} status={run['status']}")
    for stage_id, state in run["stages"].items():
        print(f"{stage_id}: {state['status']}")
    for child in run.get("case_runs", []):
        print(f"{child.get('case_id', child['candidate_id'])}: {child['status']} ({child['run_id']})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-article")
    create.add_argument("--entry", type=Path, required=True)
    create.add_argument("--run-dir", type=Path, required=True)
    create.add_argument("--record-dir", type=Path, default=DEFAULT_RECORD_DIR)
    create.add_argument("--pipeline-version", choices=tuple(PIPELINE_DEFINITIONS), default=DEFAULT_PIPELINE_VERSION)
    create.set_defaults(handler=create_article_run)
    accept = commands.add_parser("accept")
    accept.add_argument("--run-dir", type=Path, required=True)
    accept.add_argument("--stage", required=True)
    accept.add_argument("--response", type=Path, required=True)
    accept.add_argument("--adapter", required=True)
    accept.add_argument("--model", required=True)
    accept.set_defaults(handler=accept_response)
    fail = commands.add_parser("fail")
    fail.add_argument("--run-dir", type=Path, required=True)
    fail.add_argument("--stage")
    fail.add_argument("--reason", required=True)
    fail.set_defaults(handler=fail_run)
    run_stage = commands.add_parser("run-stage")
    run_stage.add_argument("--run-dir", type=Path, required=True)
    run_stage.add_argument("--stage", required=True)
    run_stage.add_argument("--provider", required=True, help="Provider name from ai_providers.json.")
    run_stage.add_argument("--config", type=Path, default=SCRIPTS_DIR / "ai_providers.json")
    run_stage.set_defaults(handler=run_stage_with_adapter)
    resolve = commands.add_parser("resolve-identity")
    resolve.add_argument("--run-dir", type=Path, required=True)
    resolve.add_argument("--action", choices=("new", "reuse"), required=True)
    resolve.add_argument("--case-id", default="", help="Existing CASE ID when --action reuse.")
    resolve.add_argument("--reviewer", required=True)
    resolve.add_argument("--reason", required=True)
    resolve.set_defaults(handler=resolve_identity)
    status = commands.add_parser("status")
    status.add_argument("--run-dir", type=Path, required=True)
    status.set_defaults(handler=show_status)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    arguments.handler(arguments)
