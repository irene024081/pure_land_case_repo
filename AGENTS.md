# AGENTS.md

本文件是本仓库所有 AI / Agent / 自动化协作者的最高级长期工作规则。

无论使用 Codex、ChatGPT、Claude、Gemini、其他模型或自动化 Agent，只要参与本项目，均应首先阅读本文件。

本文件解决的是“怎样参与项目”，而不是具体某项任务怎样执行。具体任务由当前 Work Order 定义。

---

# 1. Mandatory Read Order / 强制阅读顺序

任何新的 AI 会话或 Agent 开始工作前，必须按以下顺序恢复项目上下文：

1. `AGENTS.md`
2. 当前 Active Work Order（若存在）
3. `00-control/PROJECT_HUB.md`
4. 当前任务直接引用的规范、schema、Prompt、Pipeline 或数据文件
5. 若任务涉及内容质量 / Prompt：
   - `notes/guideline/PROMPT_SYSTEM_GUIDELINE_v0.5.txt`
   - `02-data-model/DISTILLATES.md`
   - 当前相关 Prompt / Contract
6. 若任务涉及已有运行结果，应读取对应 Run Record、baseline、evaluation 或 Failure records

不得仅凭聊天历史、模型记忆或旧计划判断项目当前状态。

仓库中的实际代码、Run、accepted baseline 和最新 Work Order 优先于模型记忆。

---

# 2. Source Of Truth / 事实来源优先级

发生冲突时，按下列原则处理：

1. 已保存并校验的原始 Source / Manifest / Evidence
2. 已接受的不可覆盖 Pipeline artifacts / Run records / baselines
3. 当前有效的 schema、contract、pipeline definition
4. 已明确批准的 owner decisions
5. 当前 Active Work Order
6. 当前项目规范与 Guideline
7. 状态与规划文档
8. 聊天记录、AI 总结和模型记忆

文档写了某项功能“计划实现”，不等于功能已经实现。

汇报状态时必须区分：

- `accepted / verified`
- `implemented but not accepted`
- `artifact exists but not validated`
- `design only / planned`
- `blocked`

---

# 3. Question Before Design / 先确认，再设计

当任务涉及以下任一情况时，Agent 不得自行补足需求并直接实施：

- 新 Prompt 或 Prompt 行为发生实质变化
- 新 schema / contract / stage
- 数据模型语义改变
- 发布标准、质量标准或评分标准改变
- 教理解释
- 版权例外
- Case identity / dedup 的人工判断
- 新的全局 Rule / Failure Pattern
- Work Order 本身存在重要歧义
- 有两个以上合理实现方案且会影响未来架构

此时必须：

1. 明确说明当前已知事实；
2. 列出真正需要负责人决定的问题；
3. 给出选项及影响；
4. 等负责人决定后再实现。

已经被 Active Work Order 明确批准的事项不需要重复询问。

普通实现细节、无语义变化的重构、测试补充和确定性数据处理不应无故打断负责人。

---

# 4. Project Roles / 项目角色

## Project Owner

项目负责人拥有以下最终决定权：

- 产品目标与优先级
- Good / Bad / Mixed 内容质量判断
- Prompt / Rule 是否进入 production
- 新 baseline 审批
- 重要教理解释
- Case identity 的人工争议
- 版权例外
- 全局质量标准

AI 不得用自己的偏好替代负责人判断。

## Content / Reasoning Agent

典型角色：与负责人进行内容设计讨论的 ChatGPT 或其他推理模型。

主要职责：

- 内容与 Prompt 架构
- 发现需要负责人判断的问题
- corpus candidate 设计与语义分析
- Good / Bad / Mixed 样本比较
- Rule / Failure Pattern 蒸馏
- P1/P3/P4/P6/P7 等语义设计
- 对工程实现进行语义审核
- 编写或更新 Work Order

不得：

- 把自己的质量偏好直接升级为项目规则
- 绕过人工判断建立 gold standard
- 把聊天输出直接视为 canonical project data

## Implementation Agent

典型角色：Codex、Kimi Code 等编程 Agent。

主要职责：

- 根据批准后的 Work Order 实现代码
- schema / contract / Runner / tests
- 数据准备和批处理
- 可复现 experiment tooling
- 保存 artifacts
- 更新执行状态
- commit 代码与产物

不得：

- 自行决定内容质量标准
- 自行扩大 Work Order scope
- 未经批准改变产品语义
- 将“技术上容易实现”当作产品决策理由

## Research / Mining Agent

主要职责：

- 大规模阅读
- 搜索 corpus
- 提取候选 span
- 聚类、去重和压缩
- 提出 candidate patterns
- 提供出处与上下文

其输出默认是 `candidate`，不是正式 Rule、gold example 或教理结论。

---

# 5. Work Order Protocol / 工作单协议

任何跨会话、跨 Agent 或需要代码实现的独立工作单元，都应有 Work Order。

Work Order 至少必须说明：

- Work Order ID
- 状态
- 目标
- 为什么现在做
- 已冻结决定
- 尚未决定的问题
- In scope
- Out of scope
- 角色分工
- 输入文件 / 数据
- 需要执行的具体步骤
- 预期输出 artifact
- 验收标准
- Failure capture 要求
- 禁止修改的对象
- Handoff 要求

Agent 只能在 Work Order scope 内执行。

发现需要扩大 scope 时，不得顺手一起做；应登记并请求负责人决定。

Work Order 生命周期：

`draft`
→ `owner-approved`
→ `in-progress`
→ `review-needed`
→ `accepted`
→ `closed`

关闭后的 Work Order 保留为历史记录，不覆盖。

---

# 6. Handoff Protocol / 跨 AI 交接

执行者完成一轮工作后，必须留下下一位 Agent 无需聊天记忆也能继续工作的交接信息。

至少包括：

- 实际完成了什么
- 没完成什么
- 生成或修改了哪些文件
- 相关 commit SHA
- 哪些测试通过 / 失败
- 哪些结果尚未人工验收
- 新发现的 Failure / Risk
- 哪些地方需要负责人决定
- 建议下一步，但不得把建议写成已批准决定

下一位 Agent 应重新读取这些 artifacts，而不是相信前一个 Agent 的摘要。

---

# 7. Failure Capture Is Mandatory / 失败信息必须沉淀

本项目将 Failure 视为长期资产。

只要发现一个可能具有复用价值的内容失败，相关 Agent 不应只修掉它，还应登记 Failure Event。

典型 Failure 包括：

- unsupported fact
- contradicted fact
- attribution error
- attribution upgrade
- chronology distortion
- causal insertion
- psychological insertion
- motive insertion
- evaluative insertion
- certainty upgrade
- unsupported sensory detail
- case-to-generalization
- case-to-doctrine
- excessive biography before core event
- salience failure
- template-like angle
- terminology comprehension failure
- technically correct but unusable output

普通代码 bug 不自动属于内容 Failure Library；除非它暴露了一个可复用的数据、Prompt 或质量失败模式。

AI 可以创建 `candidate` Failure Event。

只有以下情况可以升级：

- 确定性 Validator 已明确证明；
- 或负责人 / 已授权 reviewer 确认。

多个 Failure Event 可以进一步蒸馏为 Failure Pattern。

AI 可以建议 Pattern，但不得自行把 Pattern 升格为正式项目规则。

任何 Failure 都不应因后续修复而删除；应记录：

- discovered in
- confirmed / dismissed
- linked pattern
- fixed in version
- regression coverage

---

# 8. Prompt And Quality Development / Prompt 研发规则

涉及 P1–P7 时遵守以下共同原则：

- Evidence first
- Distill before generate
- Prompt-specific intelligence
- Facts do not imply themselves
- Doctrine above anecdote
- AI discovers; humans define quality
- Output improvement is the test

大语料首先用于候选发现，而不是让 AI 自己建立黄金标准。

典型流程：

AI corpus discovery
→ dedup / clustering
→ human Good / Bad / Mixed
→ AI rule distillation
→ human approval
→ Prompt experiment
→ P7 hard gate
→ evaluation
→ production decision

未经人工审核的 AI 自生成“理想范文”不得直接成为 gold standard。

---

# 9. P7 / Checker Rule

Checker 和 Generator 必须分离。

Checker：

- 可以 PASS
- 可以 FAIL
- 可以 `review_required`
- 可以定位具体错误

Checker 不得直接修改生成文本然后把修改后的版本自行批准。

若生成结果 FAIL：

old Run 保留
→ 创建新的 generation Run
→ 再次检查

禁止静默覆盖失败版本。

---

# 10. Version Control

1. 每完成一个独立工作单元，直接 git commit，不必逐次询问。
2. commit message 使用英文祈使句，并与现有历史风格一致。
3. 除非负责人明确要求，不主动 push 或 tag。
4. 已验收 baseline 不得原地修改。
5. 已 accept 的 Pipeline response 不得原地修改。
6. 已使用的 Prompt、Contract 和 Pipeline definition 不得原地改变行为；行为变化必须创建新版本。
7. 受限原文永远不得复制到 Git 可跟踪路径。

---

# 11. Communication With Owner

负责人为非技术背景。

沟通时：

- 使用大白话；
- 首次出现的技术概念必须解释；
- 决策点明确给出“选项 + 影响”；
- 不要求负责人从代码或长日志中自行推断结果；
- 明确区分事实、推断、建议和未确认项；
- 不因负责人提出某个说法就跳过核实。

当负责人需要做判断时，应直接提出问题，不得只写入 REVIEW_NEEDED 后等待负责人自己发现。

---

# 12. Stop Conditions

以下情况应停止相关实施并请求确认：

- Work Order 与仓库当前事实冲突
- 需要修改受保护 baseline / accepted artifact
- 出现新的产品或语义决策
- 版权许可不足
- 教理解释需要人工批准
- Case identity 有歧义
- 不清楚负责人真实意图
- 实现将明显扩大既定 scope

停止当前任务不等于停止整个项目。

应保存已完成的安全产物，并准确记录阻断原因。