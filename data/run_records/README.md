# 脱敏运行记录 / Sanitized Run Records

本目录进入 Git，保存 Run 身份、Pipeline 与 Prompt 版本、Stage 状态、模型与 Adapter 名称、时间戳和输入输出哈希。这里不保存完整原文、模型 Request 或模型 Response。

This tracked directory stores Run identity, Pipeline and Prompt versions, Stage status, model and Adapter names, timestamps, and input/output hashes. It never stores full source text, model Requests, or model Responses.

受限内容和体积较大的运行载荷保存在 Git 忽略的 `data/pipeline_runs/`。

Restricted and verbose runtime payloads remain under ignored `data/pipeline_runs/`.
