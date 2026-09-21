# 历史设计记录 / Historical Design Records

这些文件保存里程碑讨论、已被取代的 Workflow 和早期 Schema 决策。它们不是当前执行说明。

These files preserve milestone discussions, superseded Workflow descriptions, and early Schema decisions. They are not current operating instructions.

## 当前权威顺序 / Current Authority Order

1. `../../pipeline/pipeline.v2.json`：当前可执行 Stage 顺序。 / Current executable Stage order.
2. `../../pipeline/contracts/`：AI Output 要求。 / AI Output requirements.
3. `../../schemas/`：领域字段和受控值。 / Domain fields and controlled values.
4. `../../02-data-model/ARCHITECTURE.md`：系统边界。 / System boundaries.
5. `../../00-control/PROJECT_STATUS.md`：当前进度。 / Current progress.

历史 v0.1.x Pipeline 仍保留在 `../../pipeline/`，并由各 Run 自己记录的版本选用；v0.2 字段迁移规则见 `../../02-data-model/T02_V02_MIGRATION.md`。

Historical v0.1.x Pipeline definitions remain in `../../pipeline/` and are selected by each Run's recorded version; see `../../02-data-model/T02_V02_MIGRATION.md` for v0.2 field mapping.

历史记录可以用于解释决策，但不能用于运行当前 Pipeline。

Historical records should be cited when explaining a decision, not used to run the current Pipeline.
