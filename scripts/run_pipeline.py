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
PIPELINE_PATH = ROOT / "pipeline" / "pipeline.v1.json"
CONTRACT_DIR = ROOT / "pipeline" / "contracts"
PROMPT_DIR = ROOT / "pipeline" / "prompts"
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


def definition() -> dict[str, Any]:
    return load_json(PIPELINE_PATH)


def stages_for(run: dict[str, Any]) -> list[dict[str, Any]]:
    key = "article_stages" if run["run_kind"] == "article" else "case_stages"
    return definition()[key]


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
        "case_runs",
    )
    return {key: run[key] for key in keep if key in run}


def write_run(run: dict[str, Any], run_dir: Path) -> None:
    atomic_json(run_dir / "run.json", run)
    record_dir = Path(run["record_dir"])
    atomic_json(record_dir / f"{run['run_id']}.json", sanitized_record(run))


def request_payload(run: dict[str, Any], run_dir: Path, stage: dict[str, Any]) -> dict[str, Any]:
    inputs: dict[str, Any] = {
        "source_entry": load_json(Path(run["source_entry_path"])),
    }
    if run["run_kind"] == "case":
        inputs["case_id"] = run["case_id"]
        inputs["case_candidate"] = run["case_candidate"]
        inputs["source_segmentation"] = load_stage_output(run, run_dir, "source_segmentation")
    for dependency in stage["depends_on"]:
        dependency_path = output_path(run_dir, dependency)
        if dependency_path.exists():
            inputs[dependency] = load_json(dependency_path)
        else:
            inputs[dependency] = run["stages"][dependency]
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


def refresh(run: dict[str, Any], run_dir: Path) -> None:
    for stage in stages_for(run):
        stage_id = stage["id"]
        state = run["stages"][stage_id]
        if state["status"] != "pending":
            continue
        if not all(run["stages"][dep]["status"] == "completed" for dep in stage["depends_on"]):
            continue
        if stage_id == "publication_packaging":
            factual = load_stage_output(run, run_dir, "factual_check")
            rights = load_stage_output(run, run_dir, "rights_check")
            publish_status = rights["allowed_display_scope"]
            if factual["gate_result"] != "pass" or rights["gate_result"] != "pass":
                publish_status = "withheld"
            package = {
                "case_id": run["case_id"],
                "publish_status": publish_status,
                "included_output_ids": ["reader_generation", "creator_analysis"],
                "provenance": {
                    "run_id": run["run_id"],
                    "pipeline_version": run["pipeline_version"],
                    "source_entry_hash": run["source_entry_hash"],
                },
            }
            atomic_json(output_path(run_dir, stage_id), package)
            state.update({"status": "completed", "completed_at": utc_now(), "output_hash": sha256_file(output_path(run_dir, stage_id))})
            run["status"] = "completed"
            continue
        if stage.get("executor") == "deterministic":
            raise SystemExit(f"deterministic stage has no runner implementation: {stage_id}")
        request_path = run_dir / "requests" / f"{stage_id}.json"
        atomic_json(request_path, request_payload(run, run_dir, stage))
        state.update({"status": "ready", "request_hash": sha256_file(request_path)})


def rights_precheck(entry: dict[str, Any], entry_path: Path) -> dict[str, Any]:
    source_id = entry.get("source_id", "")
    if not source_id:
        raise SystemExit("source entry must include source_id")
    config, _ = read_catalog(source_id)
    row = find_entry_row(source_id, entry["source_entry_id"])
    require_batch_eligible(row)
    review_id = config.get("rights_review_id", "")
    if not review_id or row["rights_review_id"] != review_id:
        raise SystemExit("source config and article catalog must identify the same rights review")
    review_path = RIGHTS_DIR / f"{review_id}.yml"
    review = parse_simple_yaml(review_path)
    if review.get("source_id") != source_id:
        raise SystemExit("rights review source_id mismatch")
    if review.get("rights_status") != row["rights_status"]:
        raise SystemExit("rights review status differs from article catalog")
    manifest = manifest_fields(entry["source_entry_id"])
    if manifest.get("source_id") != source_id or manifest.get("raw_capture_status") != "persisted_verified":
        raise SystemExit("source manifest is not verified for this source")
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
    pipeline = definition()
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
    case_ids = preexisting if len(preexisting) == len(candidates) else allocate_case_ids(len(candidates), record_dir)
    pipeline = definition()
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
    failed = any(item["status"] == "failed" for item in parent["case_runs"])
    complete = all(item["status"] == "completed" for item in parent["case_runs"])
    parent["status"] = "failed" if failed else ("completed" if complete else "case_runs_active")
    parent["updated_at"] = utc_now()
    write_run(parent, parent_dir)
    update_article(parent["source_id"], parent["source_catalog_article_id"], {
        "pipeline_status": "failed" if failed else ("completed" if complete else "running"),
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
    if args.adapter != "local" and run["external_processing"] != "allowed":
        raise SystemExit("external adapter blocked by source and rights policy")
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
        if run["status"] == "completed":
            sync_parent(run)
    print(f"accepted {args.stage}")


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


def show_status(args: argparse.Namespace) -> None:
    run = load_json(args.run_dir.resolve() / "run.json")
    identity = run.get("case_id", run["source_entry_id"])
    print(f"{run['run_id']} kind={run['run_kind']} pipeline={run['pipeline_version']} item={identity} status={run['status']}")
    for stage_id, state in run["stages"].items():
        print(f"{stage_id}: {state['status']}")
    for child in run.get("case_runs", []):
        print(f"{child['case_id']}: {child['status']} ({child['run_id']})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-article")
    create.add_argument("--entry", type=Path, required=True)
    create.add_argument("--run-dir", type=Path, required=True)
    create.add_argument("--record-dir", type=Path, default=DEFAULT_RECORD_DIR)
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
    status = commands.add_parser("status")
    status.add_argument("--run-dir", type=Path, required=True)
    status.set_defaults(handler=show_status)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    arguments.handler(arguments)
