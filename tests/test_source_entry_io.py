from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from source_entry_io import emit_records  # noqa: E402


class EmitRecordsTest(unittest.TestCase):
    def test_writes_single_record_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "entry.json"
            emit_records([{"source_entry_id": "ENT000001", "raw_text": "原文"}], str(output))

            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                {"source_entry_id": "ENT000001", "raw_text": "原文"},
            )

    def test_writes_multiple_records_as_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "entries.jsonl"
            records = [
                {"source_entry_id": "ENT000001"},
                {"source_entry_id": "ENT000002"},
            ]
            emit_records(records, str(output))

            actual = [
                json.loads(line)
                for line in output.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(actual, records)

    def test_rejects_multiple_records_for_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "entries.json"
            with self.assertRaisesRegex(SystemExit, "exactly one"):
                emit_records([{"id": 1}, {"id": 2}], str(output))
            self.assertFalse(output.exists())

    def test_rejects_unknown_output_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "entry.txt"
            with self.assertRaisesRegex(SystemExit, "must end"):
                emit_records([{"id": 1}], str(output))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
