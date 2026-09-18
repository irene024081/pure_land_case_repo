# Pipeline Assets

This directory contains immutable production inputs for the case pipeline.

```text
pipeline.v1.json    canonical Article Run and Case Run stage graphs
contracts/          machine-readable output requirements
prompts/            versioned semantic instructions
```

The runner is `../scripts/run_pipeline.py`. Runtime requests and responses are written under ignored `data/pipeline_runs/`; sanitized provenance is written to tracked `data/run_records/`.

Do not edit a prompt or contract version after it has been used. Add a new version and update the pipeline version instead.
