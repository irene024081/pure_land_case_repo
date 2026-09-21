# Pipeline 资源 / Pipeline Assets

本目录保存案例 Pipeline 不可变的生产输入。

This directory contains immutable production inputs for the Case Pipeline.

```text
pipeline.v1.json    不可变的 Pipeline 0.1.0 Stage Graph / immutable Pipeline 0.1.0 Stage Graph
pipeline.v1.1.json  不可变的 Pipeline 0.1.1 Stage Graph / immutable Pipeline 0.1.1 Stage Graph
pipeline.v1.2.json  历史 Pipeline 0.1.2 Stage Graph / historical Pipeline 0.1.2 Stage Graph
pipeline.v2.json    当前 Pipeline 0.2.0 Stage Graph / current Pipeline 0.2.0 Stage Graph
contracts/          机器可读 Output 要求 / machine-readable Output requirements
prompts/            版本化语义指令 / versioned semantic instructions
retrieval/          版本化候选检索规则 / versioned candidate-retrieval rules
```

Runner 是 `../scripts/run_pipeline.py`。运行时 Request 和 Response 写入 Git 忽略的 `data/pipeline_runs/`；脱敏后的溯源记录写入 Git 跟踪的 `data/run_records/`。

The Runner is `../scripts/run_pipeline.py`. Runtime Requests and Responses are written under ignored `data/pipeline_runs/`; sanitized provenance is written to tracked `data/run_records/`.

Prompt 或 Contract 版本一经使用便不能修改。需要改变行为时，新增版本并更新 Pipeline Version。

Do not edit a Prompt or Contract version after it has been used. Add a new version and update the Pipeline Version instead.

Pipeline 定义遵循同一规则。Runner 根据每个 Run 保存的 `pipeline_version` 选择定义，因此历史 Run 保留原依赖图。Pipeline 0.1.1 将 `creator_analysis` 加入 Rights Check 输入，并要求每个声明的 Output 都有版权判断。

Pipeline definitions follow the same rule. The Runner selects a definition from the `pipeline_version` stored in each Run, so historical Runs keep their original dependency graph. Pipeline 0.1.1 adds `creator_analysis` to the Rights Check inputs and requires one rights decision for every declared Output.

Pipeline 0.1.2 为去重请求加入版本化、本地确定性候选检索，并让 Factual Check 直接读取 `case_extraction`。候选检索只缩小比较范围，不作自动合并或同案判定。

Pipeline 0.1.2 adds versioned deterministic local candidate retrieval to deduplication Requests and gives Factual Check direct access to `case_extraction`. Retrieval only narrows the comparison set; it never merges cases or decides identity automatically.

Pipeline 0.2.0 创建以 Candidate ID 命名的 Run，在事实抽取和去重完成前不分配 Case ID。`case_resolution` 对无既有关联的新案例分配 ID；同案、疑似同案或已有 Source Item Case ID 需要人工明确 `new` 或 `reuse`。随后 `source_occurrence` 记录来源中的具体出现及有证据的传播边。历史 v0.1.x 输出不作原地迁移，字段映射见 `../02-data-model/T02_V02_MIGRATION.md`。

Pipeline 0.2.0 creates Candidate-ID Runs and assigns no Case ID before extraction and deduplication. `case_resolution` allocates a new ID when the item has no prior Case linkage and the decision is `new_case`; same/possible matches and existing item Case IDs require an explicit human `new` or `reuse` decision. `source_occurrence` then records the concrete source appearance and supported transmission edges. Historical v0.1.x outputs remain unchanged; see `../02-data-model/T02_V02_MIGRATION.md`.
