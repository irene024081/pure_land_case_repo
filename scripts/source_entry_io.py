#!/usr/bin/env python3
"""Write normalized source-entry records without partial output files."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


def emit_records(records: Iterable[dict[str, Any]], output: str) -> None:
    materialized = list(records)
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".json":
            if len(materialized) != 1:
                raise SystemExit(".json output requires exactly one source-entry record")
            content = json.dumps(materialized[0], ensure_ascii=False, indent=2) + "\n"
        elif target.suffix == ".jsonl":
            content = "".join(
                json.dumps(record, ensure_ascii=False) + "\n" for record in materialized
            )
        else:
            raise SystemExit("output path must end in .json or .jsonl")

        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = handle.name
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, target)
        finally:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()
        return

    for record in materialized:
        print(json.dumps(record, ensure_ascii=False), file=sys.stdout)
