# T09 Reproducible Pipeline

The Pipeline processes retained evidence through two run types. Chat output is never canonical data.

## Run Types

```text
Article Run
  verified Source Entry
  -> complete source segmentation
  -> detect 0..N case candidates
  -> program assigns stable Case IDs

Case Run, one per candidate
  atomic facts
  -> entities and deduplication
  -> reader and creator outputs
  -> independent factual and rights checks
  -> publication package
```

The stage graph is `../pipeline/pipeline.v1.json`. Prompts and contracts are immutable after use; behavior changes require a new version.

## Safety And Provenance

- Source registration, manifest integrity, and rights precheck are deterministic gates.
- External AI use is allowed only when both `source.yml` and the rights review permit it. CLI arguments cannot override this policy.
- Full requests and responses stay in ignored `data/pipeline_runs/`.
- Sanitized run identity, model, stage state, and hashes are tracked in `data/run_records/`.
- Runner transitions update the Article Catalog automatically.
- Failed or completed outputs are never overwritten; reruns use new Run IDs.

## Commands

```bash
python3 scripts/manage_source_catalog.py validate
python3 scripts/manage_source_catalog.py status
python3 scripts/manage_source_catalog.py queue --source-id SRC0001

python3 scripts/run_pipeline.py create-article \
  --entry data/source_entries/public/ENT000001.normalized.json \
  --run-dir data/pipeline_runs/RUN-ENT000001-V1

python3 scripts/run_pipeline.py accept \
  --run-dir data/pipeline_runs/RUN-ENT000001-V1 \
  --stage source_segmentation \
  --response path/to/response.json \
  --adapter local \
  --model model-name

python3 scripts/run_pipeline.py status \
  --run-dir data/pipeline_runs/RUN-ENT000001-V1

python3 scripts/run_pipeline.py fail \
  --run-dir data/pipeline_runs/RUN-ENT000001-V1 \
  --reason "source boundary requires review"
```

Accepting `case_detection` automatically creates child Case Runs under `RUN-ENT000001-V1/cases/`.

Regression acceptance rules are in `REGRESSION_POLICY.md`.
