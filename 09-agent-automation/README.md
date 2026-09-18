# T09 可复现 Pipeline / Reproducible Pipeline

Pipeline 通过两类 Run 处理已保存的证据。聊天中的临时输出不能直接成为正式数据。

The Pipeline processes retained evidence through two Run types. Chat output never becomes canonical data directly.

## Run 类型 / Run Types

```text
Article Run / 文章运行
  已验证 Source Entry / verified Source Entry
  -> 完整原文分段 / complete source segmentation
  -> 检测 0..N 个案例候选 / detect 0..N Case Candidates
  -> 程序分配稳定 Case ID / program assigns stable Case IDs

Case Run / 案例运行，每个候选一个 / one per candidate
  原子事实 / atomic facts
  -> 实体与去重 / entities and deduplication
  -> 读者与创作者输出 / reader and creator outputs
  -> 独立事实与版权检查 / independent factual and rights checks
  -> 发布包 / publication package
```

当前 Stage Graph 是 `../pipeline/pipeline.v1.2.json`。Prompt、Contract、候选检索规则和 Pipeline 定义使用后不可修改；行为变化必须创建新版本。

The current Stage Graph is `../pipeline/pipeline.v1.2.json`. Prompts, Contracts, candidate-retrieval rules, and Pipeline definitions are immutable after use; behavior changes require a new version.

## 安全与溯源 / Safety And Provenance

- Source 登记、Manifest 完整性和版权预检属于确定性门槛。 / Source registration, Manifest integrity, and rights precheck are deterministic gates.
- 只有 `source.yml` 和 Rights Review 同时允许时，才能使用外部 AI；CLI 参数不能覆盖该规则。 / External AI use is allowed only when both `source.yml` and the Rights Review permit it; CLI arguments cannot override this policy.
- 完整 Request 和 Response 保存在 Git 忽略的 `data/pipeline_runs/`。 / Full Requests and Responses stay in ignored `data/pipeline_runs/`.
- 脱敏后的 Run 身份、模型、Stage 状态和哈希保存在 `data/run_records/`。 / Sanitized Run identity, model, Stage state, and hashes are tracked in `data/run_records/`.
- Runner 推进 Stage 时自动更新 Article Catalog。 / Runner transitions update the Article Catalog automatically.
- 去重 Request 会从本地已完成 Case Run 中确定性选择候选，并记录版本、得分、理由和候选集合哈希。 / Deduplication Requests deterministically select candidates from completed local Case Runs and record the version, scores, reasons, and candidate-set hash.
- 候选包含受限数据时，去重 Stage 只能使用本地 Adapter。 / A deduplication Stage containing restricted candidate data must use a local Adapter.
- 失败或完成的 Output 不会被覆盖；重跑使用新 Run ID。 / Failed or completed Outputs are never overwritten; reruns use new Run IDs.

## 命令 / Commands

校验 Catalog、查看状态并列出可批量处理的 Article：

Validate Catalogs, print status, and list batch-eligible Articles:

```bash
python3 scripts/manage_source_catalog.py validate
python3 scripts/manage_source_catalog.py status
python3 scripts/manage_source_catalog.py queue --source-id SRC0001
```

创建 Article Run、接收 AI Response、查看状态或标记失败：

Create an Article Run, accept an AI Response, inspect status, or mark a failure:

```bash
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

接收 `case_detection` 后，Runner 会在 `RUN-ENT000001-V1/cases/` 下自动创建子 Case Run。

Accepting `case_detection` automatically creates child Case Runs under `RUN-ENT000001-V1/cases/`.

回归验收规则位于 `REGRESSION_POLICY.md`。

Regression acceptance rules are in `REGRESSION_POLICY.md`.
