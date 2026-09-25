# 适配器总账 / Adapter Ledger

本文件是所有适配器的唯一总账：每个适配器的目的、输入输出、验证状态、已知限制都在这里登记。别处（`../02-data-model/SOURCE_ENTRY_PIPELINE.md`、本目录 README）只放指引，细节以本文件为准。

**状态口径**：`已用于正式 Run` = 其产物进入过已完成的 Pipeline Run；`已验证` = 真实来源/真实文件上跑通且有数字证据；`mock 验证` = 只有合成 fixture 或模拟接口的测试；`未验证` = 只有实现。

## 总览表

| 适配器 | 类型 | 状态 | 验证来源 | 主要限制 |
|---|---|---|---|---|
| static_headings | 目录 | 已验证（未落库） | X78n1549 保存页，70 条 | 依赖页面标题结构稳定；范围靠起止标题 |
| wordpress_archive | 目录 | 已验证（未落库） | SRC0387 越南站，268 条 | 站点需是标准 WP 归档分页 |
| paginated_html | 目录 | **已落库** | SRC0003 plb.tw，481 条入目录 | 会话参数/栏目自链要靠 include/key 正则排除 |
| pdf_toc | 目录 | 已验证（未落库） | SRC0002 保存 PDF，109 条 | 依赖 pypdf；目录换行断行会被跳过 |
| cbeta_xml | 目录+正文 | **已用于正式 Run** | T51n2072 全书 263 条；ENT000009 | 只适用于 CBETA TEI P5 结构 |
| extract_dazhouxian_entries.py | 正文 | **已用于正式 Run** | SRC0001（ENT000001/6/7/8） | 内层标题拆分盲区（见下） |
| extract_plbtw_article.py | 正文 | 已用于条目捕获 | SRC0003（ENT000002） | 只覆盖该站文章页结构 |
| extract_plb_sea_article.py | 正文 | 已用于条目捕获 | SRC0004（ENT000003） | 同上 |
| extract_wordpress_article.py | 正文 | 已用于条目捕获 | SRC0005（ENT000005） | 同上 |
| extract_pdf_entry.py | 正文 | 已用于条目捕获 | SRC0002（ENT000004） | 依赖 pypdf；扫描版 PDF 无文本层则失败 |
| ai_adapter.py | AI 调用 | mock 验证 | 四厂商合成响应 | 真实厂商未联调（待密钥） |
| youtube_watch.py | YT 发现+文字稿 | mock 验证 | 合成 playlistItems/目录 | channel_id 待人工确认；文字稿第 3、4 级占位 |

---

## 一、目录适配器（inventory，发现"有哪些文章"）

实现位于 `../scripts/inventory_adapters.py`（四家族统一接口）+ `../scripts/run_inventory.py`（扫描与目录同步）。通用语义：已知键不动、新键追加为 unreviewed+pending、全量扫描中消失的标 removed 不删除、`--dry-run` 先出 diff；只取目录页、页间延迟可配。测试：`../tests/test_inventory_adapters.py`。

### static_headings 静态标题/列表页

- **目的**：把单张静态页面（古籍栏目页、简单目录页）里的链接或文字标题变成目录行。
- **输入**：`inventory.yml` 里 `mode: links`（容器选择器+链接规则）或 `mode: headings`（文字标题，复用 dazhouxian 标题判定，支持 start/end_heading 范围）。
- **输出**：条目键、标题、URL。
- **状态**：已验证，未落库。headings 模式在保存的 X78n1549 页面对"往生女人第九"发现 70 条，与该节既有清点一致。
- **限制**：页面结构变化需人工复核；无分页能力。
- **测试**：`test_inventory_adapters.py::StaticHeadingsTest`（links/headings 两模式）。

### wordpress_archive WordPress 归档分页

- **目的**：遍历 WordPress 分类/归档分页，收集文章链接。
- **输入**：`archive_url_template`（含 `{page}`）、容器选择器（默认 `article`）、键规则；空页/404 停止。
- **输出**：同上，键为 URL 路径段。
- **状态**：已验证，未落库。SRC0387（duongvecoitinh.com）真实走查 45 页发现 268 条；该来源尚未注册目录。
- **限制**：只认标准 WP 归档结构；栏目自链需 exclude_pattern 排除。
- **测试**：`WordpressArchiveTest`。

### paginated_html 自定义分页列表

- **目的**：遍历老网站的自定义分页列表页。
- **输入**：`list_url_template`（含 `{page}`）、include/key/url_strip 正则、页数上限。
- **输出**：同上。
- **状态**：**已落库**。SRC0003（plb.tw 往生故事栏目）31 页发现 481 条并写入 `data/source_catalogs/SRC0003/articles.csv`；既有试点行（story:id=1564）正确识别未动。验证中修掉两个真实问题：会话参数 `chk`/`param` 混入 URL（url_strip_pattern）、栏目自链误匹配（key 正则收紧为 `[?&]id=`）。
- **限制**：规则与站点模板绑定，改版需重配。
- **测试**：`PaginatedHtmlTest`（翻页、空页停止、增量稳定）。

### pdf_toc PDF 目录页

- **目的**：把按期发行的 PDF 刊物目录页解析成条目（标题+作者+页码）。
- **输入**：`pdf_path`（本地）、`toc_pages` 页码范围、条目正则（可覆盖）、`issue` 刊号。
- **输出**：条目键 `{issue}:p{页码}:{序号}`、标题、作者备注。
- **状态**：已验证，未落库。SRC0002 保存的受限 PDF（《当代念佛感应集》，534 页）目录 13–17 页解析出 109 条；只读目录页、不读正文，产物为纯元数据。
- **限制**：依赖 pypdf；扫描版 PDF（无文本层）不适用；目录换行断行的条目会被跳过（跳过行数输出到 stderr）。
- **测试**：`PdfTocTest`。

### cbeta_xml（兼具目录发现）

- 见下一节同名条目：其全书/全卷切分结果天然就是目录（条目键、卷、类、标题齐全），SRC0024 的 `inventory_adapter` 即登记为 `cbeta_xml`。

---

## 二、正文提取适配器（entry extraction，读出文章内容）

输出统一为 source_entry record（`source_entry_io.emit_records`）：稳定 ID、来源键、标题、原文、哈希、定位符、提取器名与版本、边界状态。

### extract_cbeta_xml.py（v0.1.0，extraction_method: cbeta_xml_tei_structure）

- **目的**：按 CBETA TEI P5 XML 的 `<head>`+`<p>` 结构切条目。
- **输入**：XML 文件路径/URL + source-id/title/url + 卷次标签、起止标题、ID 前缀等参数；`--output` JSONL/JSON。
- **状态**：**已用于正式 Run**（ENT000009 僧濟，RUN-ENT000009-M2B-01 → CASE000010）。冒烟：T51n2072《往生集》全书 263 条（卷/类结构与目录一致）；X78n1549《净土圣贤录》往生女人第九 79 条。重跑字节级稳定。
- **亮点**：嵌套条目按 cb:div 祖先关系正确拆分，父记录 notes 标 `contains_nested_entries`——修复了 dazhouxian 提取器的盲区（X78n1549 中温静文妻/任氏/王氏被正确拆成三条）。
- **限制**：只适用于 CBETA TEI 结构；卷名映射靠 `--volume-labels`。
- **测试**：`test_extractors.py::CbetaXmlExtractorTest`（合成 fixture：条目数、嵌套拆分+标记、重跑稳定、范围参数）。

### extract_dazhouxian_entries.py

- **目的**：从大zhouxiain 的 CBETA 风格 HTML 页按"重复标题"规则切古籍条目。
- **状态**：**已用于正式 Run**：SRC0001 的 ENT000001（M2A 基线）、ENT000006/7/8（M2B 第一批）。
- **已知限制**：**内层标题拆分盲区**——下一段不以标题开头的内层传记会被并入上一条（ENT000007 温静文妻条实际含三则传记未拆开，已在该条 notes 与目录中如实标注）。CBETA XML 适配器已无此问题；该书后续批量处理应优先走 CBETA 底本。
- **测试**：`test_extractors.py::ExtractorSmokeTest::test_dazhouxian_repeated_headings`。

### extract_plbtw_article.py / extract_plb_sea_article.py / extract_wordpress_article.py

- **目的**：分别从 PLBTW、PLB-SEA、WordPress 风格文章页提取标题与正文。
- **状态**：已用于条目捕获（ENT000002 / ENT000003 / ENT000005，均在受限存储）；正文未进任何正式 Run（版权 legal_review_required / restricted_internal）。
- **限制**：与各自站点模板绑定；模板改版需重验。
- **测试**：`ExtractorSmokeTest` 中各一条边界用例。

### extract_pdf_entry.py

- **目的**：按人工核定的页码范围从 PDF 提取条目文本。
- **状态**：已用于条目捕获（ENT000004，受限存储）。
- **限制**：依赖 pypdf；无文本层的扫描件不适用。
- **测试**：无独立用例（pypdf 为可选依赖）。

---

## 三、AI 调用适配器

### ai_adapter.py（+ run_pipeline.py `run-stage` 命令）

- **目的**：runner 直接调用 AI 厂商 API 完成一个 ready 阶段，替代"外部人工生成响应再 accept"；同一版本化 prompt 可切换厂商。
- **输入**：runner 生成的 request JSON（prompt+contract+inputs，先核哈希）；输出与 `accept` 同格式，走同一套 validator。
- **厂商**：OpenAI / Anthropic / Google / Kimi，配置在 Git 忽略的 `scripts/ai_providers.json`（模板 `ai_providers.example.json`），密钥走环境变量。
- **记录**：每次调用记 prompt 版本、模型、token、估算成本、重试次数、耗时到 Git 忽略的 `data/adapter_logs/calls.jsonl`；脱敏摘要进 run.json 阶段 `api_call` 并同步 run_records。
- **红线**：`external_processing` 非 allowed 时 `run-stage` 直接拒绝，与 accept 的外部拦截同一规则；受限原文无外发路径。
- **状态**：mock 验证（四厂商调用路径、重试、失败留痕、受限拦截、端到端）。真实联调待密钥。
- **测试**：`../tests/test_ai_adapter.py`（6 用例）。

---

## 四、YouTube 工具

### youtube_watch.py（发现 + 文字稿链）

- **目的**：把 YouTube 频道当"持续投稿渠道"管理：官方 Data API 发现新视频 + 按优先级链取文字稿。不爬 YouTube 网页和字幕（条款限制）。
- **发现**：`scan` 读频道 uploads 播放列表（playlistItems.list，1 quota/次），新视频追加 `data/youtube_watch/videos.csv`（含 case_hint 高召回关键词标记），按 video_id 去重；key 走 `YOUTUBE_API_KEY`，无 key 用 `--mock` 回放。
- **文字稿链**：`transcript` 按优先级——(1) 法师官网文字稿（频道登记的 repo 目录标题匹配 + 来源提取器抓正文）；(2) 视频 description 自带完整来信；**(3) 频道授权字幕、(4) 合法音视频的本地转写——占位未实现，待 T06 授权**。
- **频道登记**：`data/youtube_watch/channel_registry.csv` 预填五频道（净本/净平→SRC0159、道晟→SRC0176、净土宗官方→SRC0158、信愿→注册表无 repo 行已标 pending、净空体系→SRC0170）；channel_id 全部 pending 待人工确认。
- **状态**：mock 验证。
- **测试**：`../tests/test_youtube_watch.py`（8 用例）。

---

## 新增适配器的准入要求

1. **版本号**：提取器必须有 `extractor_version` 与明确的 extraction_method 名；行为变更必须升版本，不得原地改已用版本。
2. **测试**：`tests/` 里新增对应用例，覆盖至少：正常发现/提取、边界或嵌套场景、重跑输出稳定（哈希一致）。AI 适配器一律 mock，不依赖真实密钥。
3. **文档登记**：在本文件登记目的、状态、验证证据、限制；若引入新家族，同步 `../02-data-model/SOURCE_ENTRY_PIPELINE.md` 的家族清单。
4. **来源登记**：用新适配器接新来源前，来源目录（source.yml + articles.csv）与版权审核必须已就位；发现工具只登记元数据，不代表获准处理。
