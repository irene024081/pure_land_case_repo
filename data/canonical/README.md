# Canonical Store / 正式库

正式库（canonical store）保存验收通过后的案例数据。它与 Run 证据的关系：
`data/pipeline_runs/` 是证据（requests/responses/outputs，Git 忽略），正式库是
由证据提升而来、供查询与产品使用的数据集。正式库必须能从 Run 证据完整重建。

## 内容

- `schema.sql` — 正式库结构（cases、case_facts、entities、case_tags、
  source_occurrences、text_versions、identity_decisions、rights_decisions、
  dedup_index、promotion_log、schema_migrations）。DDL 同时兼容 SQLite 与 Postgres。
- `canonical.db` — 本地 SQLite 落地文件（Git 忽略；随时可由提升命令重建）。
- `README.md` — 本文件。

## 引擎切换（D10）

当前后端是 SQLite（`scripts/canonical_store.py`，纯标准库）。生产目标按 D10 是
Postgres：schema 已避免引擎特有语法，切换时只需在存储层把连接替换为 Postgres
连接（psycopg），表结构不变。切换前请在 CI 对同一 schema 跑一次 Postgres 迁移演练。

## 提升

```bash
# 提升单个已完成的 Case Run
python3 scripts/promote_run.py promote --run-dir data/pipeline_runs/RUN-XXX/candidates/YYY

# 提升全部已完成的 Case Run（每个 case_id 取最新完成的 Run）
python3 scripts/promote_run.py promote --all

# 查看正式库状态 / 与 Run 证据做一致性校验
python3 scripts/promote_run.py status
python3 scripts/promote_run.py verify
```

规则：只接受 status=completed 的 Case Run；同一 case_id 已有更新的 Run 提升过时
拒绝旧 Run（superseded）；重复提升同一 Run 是无操作（幂等）；提升前校验所有
fact→segment、tag→fact、occurrence→entry、reader/creator/claims 引用完整性。
