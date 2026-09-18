# Product And Research Workflow

## Recommended Sequence

先定义产品，再定义 PRD，再设计数据模型，再做采集和开发。

原因：数据模型必须服务真实使用场景。这个项目不是只收藏故事，而是要支持普通读者搜索阅读，也要支持检索、推荐、引用、去重和视频制作辅助。

## Phase 0: Product Definition

Outputs:

- `PRODUCT_DEFINITION.md`
- User profiles
- MVP scope
- Product principles

Stopping condition:

- 明确第一版服务谁，以及普通读者和创作者分别从什么问题开始使用产品。

## Phase 1: PRD

Outputs:

- `PRD_DRAFT.md`
- User journeys
- Feature list
- Ranking factors
- Success criteria

Stopping condition:

- 能从 PRD 推导出页面、数据字段和 Agent 任务。

## Phase 2: Data Model

Outputs:

- Source schema
- Case schema
- Citation schema
- Tag schema
- Creator metadata schema

Stopping condition:

- 一个案例可以同时支持研究审核和视频推荐。

## Phase 3: Seed Dataset

Outputs:

- 3-5 个来源。
- 50-100 个人工审核案例。
- 每个案例至少有摘要、标签、引用和证据等级。
- 数据处理 workflow。
- 10-case pilot。
- 50-case alpha。
- 80-100-case beta。

Stopping condition:

- 足够支撑网站 MVP 的搜索和推荐演示。
- 普通读者搜索、Case Detail、主题推荐、Creator Brief 都通过验收。

Detailed plan:

- `../02-data-model/SEED_DATASET_PLAN.md`
- `../02-data-model/DATA_PROCESSING_WORKFLOW.md`

## Phase 4: Website MVP

Outputs:

- Homepage
- Search
- Case detail
- Source detail
- Theme-to-case recommendation
- Case basket
- Creator brief

Stopping condition:

- 普通读者能搜索、阅读并核对出处。
- 创作者能从一个选题得到推荐案例，并生成可用 brief。

## Phase 5: Agent Workflow

Outputs:

- Source Scout
- Extractor
- Normalizer
- Provenance Agent
- Dedup Agent
- Editor Review Queue

Stopping condition:

- Agent 可以产生候选数据，但正式入库仍需人工确认。
