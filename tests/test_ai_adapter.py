from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import ai_adapter  # noqa: E402
import run_pipeline  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]

PROVIDER_RESPONSES = {
    "openai": lambda text: {
        "choices": [{"message": {"content": text}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        "model": "gpt-4o-mini",
    },
    "kimi": lambda text: {
        "choices": [{"message": {"content": text}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        "model": "kimi-k2-0711-preview",
    },
    "anthropic": lambda text: {
        "content": [{"text": text}],
        "usage": {"input_tokens": 100, "output_tokens": 50},
        "model": "claude-3-5-haiku-latest",
    },
    "google": lambda text: {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
        "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 50},
    },
}


def make_config(temp: Path, providers: list[str]) -> Path:
    config = {
        "retry": {"max_attempts": 3, "base_delay_seconds": 0, "max_delay_seconds": 0},
        "providers": {
            name: {
                "endpoint": "https://example.invalid/" + name + ("/{model}" if name == "google" else ""),
                "model": f"{name}-model",
                "api_key_env": "TEST_ADAPTER_KEY",
                "cost_per_1k_input": 0.001,
                "cost_per_1k_output": 0.002,
                "enabled": True,
            }
            for name in providers
        },
    }
    path = temp / "ai_providers.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def fake_request() -> dict:
    return {
        "run_id": "RUN-TEST",
        "stage": "case_detection",
        "prompt_version": "case_detection/v1.md",
        "prompt": "Detect cases.",
        "contract": {"stage": "case_detection"},
        "inputs": {"source_entry": {"source_entry_id": "ENT000001"}},
    }


class AiAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        os.environ["TEST_ADAPTER_KEY"] = "test-key"
        self.log_dir = Path(self.temp.name) / "logs"

    def tearDown(self) -> None:
        os.environ.pop("TEST_ADAPTER_KEY", None)
        self.temp.cleanup()

    def log_records(self) -> list[dict]:
        path = self.log_dir / "calls.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_all_providers_call_path(self) -> None:
        for name, responder in PROVIDER_RESPONSES.items():
            config = make_config(Path(self.temp.name), [name])
            payload = {"ok": True, "provider": name}
            with mock.patch.object(
                ai_adapter, "http_post_json", return_value=responder(json.dumps(payload))
            ):
                result = ai_adapter.call_with_retry(
                    name, fake_request(), config_path=config, log_dir=self.log_dir
                )
            self.assertEqual(result["response"], payload)
            summary = result["summary"]
            self.assertEqual(summary["attempts"], 1)
            self.assertEqual(summary["prompt_tokens"], 100)
            self.assertGreater(summary["estimated_cost_usd"], 0)
        records = self.log_records()
        self.assertEqual(len(records), len(PROVIDER_RESPONSES))
        self.assertTrue(all(record["status"] == "ok" for record in records))
        self.assertTrue(all("prompt_version" in record for record in records))

    def test_retry_on_retryable_status(self) -> None:
        config = make_config(Path(self.temp.name), ["openai"])
        calls = []

        def flaky(url, headers, payload):
            calls.append(url)
            if len(calls) == 1:
                raise ai_adapter.HttpStatusError(503, "unavailable")
            return PROVIDER_RESPONSES["openai"]('{"ok": true}')

        with mock.patch.object(ai_adapter, "http_post_json", side_effect=flaky):
            result = ai_adapter.call_with_retry(
                "openai", fake_request(), config_path=config, log_dir=self.log_dir
            )
        self.assertEqual(result["summary"]["attempts"], 2)
        self.assertEqual(len(calls), 2)

    def test_non_retryable_failure_is_logged(self) -> None:
        config = make_config(Path(self.temp.name), ["openai"])
        with mock.patch.object(
            ai_adapter, "http_post_json",
            side_effect=ai_adapter.HttpStatusError(400, "bad request"),
        ):
            with self.assertRaisesRegex(SystemExit, "1 attempt"):
                ai_adapter.call_with_retry(
                    "openai", fake_request(), config_path=config, log_dir=self.log_dir
                )
        records = self.log_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "error")
        self.assertEqual(records[0]["attempts"], 1)
        self.assertIn("400", records[0]["error"])

    def test_missing_api_key(self) -> None:
        os.environ.pop("TEST_ADAPTER_KEY", None)
        config = make_config(Path(self.temp.name), ["openai"])
        with self.assertRaisesRegex(SystemExit, "TEST_ADAPTER_KEY"):
            ai_adapter.call_with_retry(
                "openai", fake_request(), config_path=config, log_dir=self.log_dir
            )


class RunStageIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        os.environ["TEST_ADAPTER_KEY"] = "test-key"
        self.root = Path(self.temp.name)
        self.entry_path = ROOT / "data" / "source_entries" / "public" / "ENT000008.normalized.json"
        self.entry = json.loads(self.entry_path.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        os.environ.pop("TEST_ADAPTER_KEY", None)
        self.temp.cleanup()

    def make_run_dir(self, external_processing: str) -> Path:
        run_dir = self.root / "run"
        for sub in ("requests", "responses", "outputs", "checks"):
            (run_dir / sub).mkdir(parents=True)
        request = {
            "run_id": "RUN-TEST-ADAPTER",
            "pipeline_version": "0.2.0",
            "stage": "source_segmentation",
            "prompt_version": "source_segmentation/v1.md",
            "prompt": (ROOT / "pipeline" / "prompts" / "source_segmentation" / "v1.md").read_text(encoding="utf-8"),
            "contract": json.loads((ROOT / "pipeline" / "contracts" / "source_segmentation.v1.json").read_text(encoding="utf-8")),
            "inputs": {"source_entry": self.entry},
        }
        request_path = run_dir / "requests" / "source_segmentation.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
        run = {
            "run_id": "RUN-TEST-ADAPTER",
            "run_kind": "article",
            "pipeline_id": "pure-land-content-pipeline",
            "pipeline_version": "0.2.0",
            "source_id": "SRC0001",
            "source_entry_id": self.entry["source_entry_id"],
            "source_entry_path": str(self.entry_path),
            "source_entry_hash": "x",
            "source_catalog_article_id": "SRC0001-ART000004",
            "preexisting_case_ids": [],
            "rights_review_id": "RR0005",
            "rights_review_path": str(ROOT / "data" / "rights_reviews" / "RR0005.yml"),
            "external_processing": external_processing,
            "record_dir": str(self.root / "records"),
            "created_at": "2026-09-24T00:00:00+00:00",
            "updated_at": "2026-09-24T00:00:00+00:00",
            "status": "running",
            "stages": {
                "source_registration": {"status": "completed"},
                "rights_precheck": {"status": "completed"},
                "source_capture": {"status": "completed"},
                "source_segmentation": {
                    "status": "ready",
                    "request_hash": hashlib.sha256(request_path.read_bytes()).hexdigest(),
                },
                "case_detection": {"status": "pending"},
            },
            "case_runs": [],
        }
        (run_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False), encoding="utf-8")
        return run_dir

    def segmentation_payload(self) -> str:
        raw = self.entry["raw_text"]
        return json.dumps({
            "source_entry_id": self.entry["source_entry_id"],
            "segments": [{
                "segment_id": f"{self.entry['source_entry_id']}-SEG0001",
                "sequence": 1,
                "start_offset": 0,
                "end_offset": len(raw),
                "segment_type": "other",
                "content": raw,
                "content_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                "claim_mode": "unknown",
                "speaker_or_author": "mock adapter",
            }],
        }, ensure_ascii=False)

    def invoke_run_stage(self, run_dir: Path) -> None:
        config = make_config(self.root, ["openai"])
        args = argparse.Namespace(
            run_dir=run_dir, stage="source_segmentation", provider="openai", config=config,
        )
        with mock.patch.object(
            ai_adapter, "http_post_json",
            return_value=PROVIDER_RESPONSES["openai"](self.segmentation_payload()),
        ), mock.patch.object(run_pipeline, "update_article"), mock.patch.object(
            ai_adapter, "DEFAULT_LOG_DIR", self.root / "logs"
        ):
            run_pipeline.run_stage_with_adapter(args)

    def test_run_stage_blocked_when_external_processing_blocked(self) -> None:
        run_dir = self.make_run_dir("blocked")
        config = make_config(self.root, ["openai"])
        args = argparse.Namespace(
            run_dir=run_dir, stage="source_segmentation", provider="openai", config=config,
        )
        with self.assertRaisesRegex(SystemExit, "external adapter blocked"):
            run_pipeline.run_stage_with_adapter(args)

    def test_run_stage_end_to_end_with_mock(self) -> None:
        run_dir = self.make_run_dir("allowed")
        self.invoke_run_stage(run_dir)
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        state = run["stages"]["source_segmentation"]
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["adapter"], "openai")
        self.assertIn("api_call", state)
        self.assertEqual(state["api_call"]["prompt_tokens"], 100)
        self.assertGreater(state["api_call"]["estimated_cost_usd"], 0)
        record_path = self.root / "records" / "RUN-TEST-ADAPTER.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertIn("api_call", record["stages"]["source_segmentation"])


if __name__ == "__main__":
    unittest.main()
