# T09 可复现 Pipeline / Reproducible Pipeline

Pipeline 通过两类 Run 处理已保存的证据。聊天中的临时输出不能直接成为正式数据。

The Pipeline processes retained evidence through two Run types. Chat output never becomes canonical data directly.

## Run 类型 / Run Types

```text
Article Run / 文章运行
  已验证 Source Entry / verified Source Entry
  -> 完整原文分段 / complete source segmentation
  -> 检测 0..N 个案例候选 / detect 0..N Case Candidates
  -> 创建 Candidate Run，暂不分配 Case ID / create Candidate Runs without Case IDs

Candidate Run / 候选运行，每个候选一个 / one per candidate
  原子事实 / atomic facts
  -> 实体与去重 / entities and deduplication
  -> 身份解决并分配或复用 Case ID / identity resolution and Case ID assignment or reuse
  -> 来源出现与传播记录 / source occurrence and transmission
  -> 读者与创作者输出 / reader and creator outputs
  -> 独立事实与版权检查 / independent factual and rights checks
  -> 发布包 / publication package
```

当前 Stage Graph 是 `../pipeline/pipeline.v2.json`。Prompt、Contract、候选检索规则和 Pipeline 定义使用后不可修改；行为变化必须创建新版本。

The current Stage Graph is `../pipeline/pipeline.v2.json`. Prompts, Contracts, candidate-retrieval rules, and Pipeline definitions are immutable after use; behavior changes require a new version.

## 安全与溯源 / Safety And Provenance

- Source 登记、Manifest 完整性和版权预检属于确定性门槛。 / Source registration, Manifest integrity, and rights precheck are deterministic gates.
- 只有 `source.yml` 和 Rights Review 同时允许时，才能使用外部 AI；CLI 参数不能覆盖该规则。 / External AI use is allowed only when both `source.yml` and the Rights Review permit it; CLI arguments cannot override this policy.
- 完整 Request 和 Response 保存在 Git 忽略的 `data/pipeline_runs/`。 / Full Requests and Responses stay in ignored `data/pipeline_runs/`.
- 脱敏后的 Run 身份、模型、Stage 状态和哈希保存在 `data/run_records/`。 / Sanitized Run identity, model, Stage state, and hashes are tracked in `data/run_records/`.
- Runner 推进 Stage 时自动更新 Article Catalog。 / Runner transitions update the Article Catalog automatically.
- 去重 Request 会从本地已完成 Case Run 中确定性选择候选，并记录版本、得分、理由和候选集合哈希。 / Deduplication Requests deterministically select candidates from completed local Case Runs and record the version, scores, reasons, and candidate-set hash.
- 候选包含受限数据时，去重 Stage 只能使用本地 Adapter。 / A deduplication Stage containing restricted candidate data must use a local Adapter.
- 失败或完成的 Output 不会被覆盖；重跑使用新 Run ID。 / Failed or completed Outputs are never overwritten; reruns use new Run IDs.
- 接收 Response 前重新校验对应 Request 的哈希，防止运行过程中输入被改动。 / Recheck the Request hash before accepting a Response to detect changed stage inputs.

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
  --run-dir data/pipeline_runs/RUN-ENT000001-V2

python3 scripts/run_pipeline.py accept \
  --run-dir data/pipeline_runs/RUN-ENT000001-V2 \
  --stage source_segmentation \
  --response path/to/response.json \
  --adapter local \
  --model model-name

python3 scripts/run_pipeline.py status \
  --run-dir data/pipeline_runs/RUN-ENT000001-V2

python3 scripts/run_pipeline.py fail \
  --run-dir data/pipeline_runs/RUN-ENT000001-V2 \
  --reason "source boundary requires review"
```

接收 `case_detection` 后，Runner 会在 `RUN-ENT000001-V2/candidates/` 下创建 Candidate Run。若 `case_resolution` 停在 `review_required`，需明确做出身份决定；只能复用已知 Case ID，且必须填写审核人和理由。

Accepting `case_detection` creates child Candidate Runs under `RUN-ENT000001-V2/candidates/`. A `review_required` resolution needs an explicit identity decision; reuse is limited to a known Case ID and requires a reviewer and reason.

已有 v0.1.x Case Run 的事实和实体标签可以用 `migrate_candidate_outputs.py` 生成候选 ID 响应。脚本核对旧输出哈希并保留来源 Run ID；这是证据迁移，不是新版 Prompt 的质量评测。

## AI API 适配器 / AI API Adapter

`run-stage` 命令可以让 runner 直接调用 AI 厂商 API 完成一个 ready 阶段，代替"外部人工生成响应再 accept"。密钥与厂商配置不进入 Git：

```bash
cp scripts/ai_providers.example.json scripts/ai_providers.json   # 本地配置，已被 .gitignore
export OPENAI_API_KEY=...        # 各家密钥按配置里的 api_key_env 设置

python3 scripts/run_pipeline.py run-stage \
  --run-dir data/pipeline_runs/RUN-XXX \
  --stage source_segmentation \
  --provider openai              # openai | anthropic | google | kimi，切换只改这一个参数
```

- 厂商、端点、模型、单价在 `scripts/ai_providers.json` 配置；`--provider` 切换厂商，同一版本化 prompt 不变。
- 每次调用记录 prompt 版本、模型、token 用量、估算成本、重试次数、耗时到 Git 忽略的 `data/adapter_logs/calls.jsonl`；脱敏摘要写入 run.json 阶段的 `api_call` 字段并同步进 `data/run_records/`。
- 重试为指数退避（次数与间隔可在配置 `retry` 节调整）；最终失败写入日志并中止，不静默。
- 红线不变：阶段或来源的 `external_processing` 不是 `allowed` 时，`run-stage` 直接拒绝（与 `accept` 的外部 adapter 拦截同一规则），受限原文不会发往任何厂商。

Facts and entity tags from a completed v0.1.x Case Run may be converted with `migrate_candidate_outputs.py`. It checks legacy output hashes and records the source Run ID. This is an evidence migration, not an evaluation of the new Prompts.

```bash
python3 scripts/migrate_candidate_outputs.py \
  --legacy-case-dir data/pipeline_runs/RUN-ENT000001-M2A-P011/cases/CASE000001 \
  --candidate-id ENT000001-CAND0001 \
  --output-dir data/pipeline_runs/RUN-ENT000001-M2A-T02V02/candidates/ENT000001-CAND0001/submissions
```

```bash
python3 scripts/run_pipeline.py resolve-identity \
  --run-dir data/pipeline_runs/RUN-ENT000001-V2/candidates/ENT000001-CAND0001 \
  --action reuse --case-id CASE000001 --reviewer reviewer-id \
  --reason "same episode confirmed against the retained source"
```

回归验收规则位于 `REGRESSION_POLICY.md`。各阶段的目的、输入输出与验收标准见 `PIPELINE_STAGES.md`（面向人工审核）。

Regression acceptance rules are in `REGRESSION_POLICY.md`.
