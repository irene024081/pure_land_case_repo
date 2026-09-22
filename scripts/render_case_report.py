#!/usr/bin/env python3
"""Render human-readable HTML review reports for completed pipeline case runs.

Usage:
    python3 scripts/render_case_report.py --run-dir <case-or-article-run-dir>
    python3 scripts/render_case_report.py --all

Reports are written to data/reports/ (git-tracked). Restricted source text is
never rendered; entries whose manifest storage_class is not tracked_public
show a redaction placeholder instead of raw segment content.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_RUNS = ROOT / "data" / "pipeline_runs"
MANIFEST_ROOT = ROOT / "data" / "source_entries" / "manifests"
DEFAULT_OUT_DIR = ROOT / "data" / "reports"

REDACTED = "【受限原文：该来源的存储级别不允许在报告中展示，请到受限存储核对】"

CSS = """
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; margin: 2em; line-height: 1.6; color: #222; }
h1 { font-size: 1.5em; border-bottom: 2px solid #444; padding-bottom: .3em; }
h2 { font-size: 1.15em; margin-top: 2em; border-left: 4px solid #888; padding-left: .5em; }
table { border-collapse: collapse; width: 100%; margin: .8em 0; }
th, td { border: 1px solid #ccc; padding: .4em .6em; vertical-align: top; text-align: left; font-size: .92em; }
th { background: #f2f2f2; }
.meta { color: #555; font-size: .9em; }
.src { font-family: "Songti SC", serif; background: #fafaf5; }
.verdict-supported { color: #1a7f37; }
.verdict-partially_supported { color: #9a6700; }
.verdict-unsupported, .verdict-contradicted { color: #cf222e; font-weight: bold; }
.verdict-not_factual { color: #555; }
.gate-pass { color: #1a7f37; font-weight: bold; }
.gate-fail, .gate-legal_review_required { color: #cf222e; font-weight: bold; }
.badge { display: inline-block; padding: .1em .5em; border-radius: .4em; background: #eee; font-size: .85em; }
.note { background: #fff8e6; border: 1px solid #e0c97f; padding: .6em .8em; border-radius: .4em; }
"""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value))


def manifest_storage_class(source_entry_id: str) -> str:
    path = MANIFEST_ROOT / f"{source_entry_id}.yml"
    if not path.exists():
        return "unknown"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("storage_class:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def output_or_empty(run_dir: Path, stage: str) -> dict[str, Any]:
    path = run_dir / "outputs" / f"{stage}.json"
    return load_json(path) if path.exists() else {}


def stage_rows(run: dict[str, Any]) -> str:
    rows = []
    for stage_id, state in run["stages"].items():
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                esc(stage_id),
                esc(state.get("status", "")),
                esc(state.get("adapter", "")),
                esc(state.get("model", "")),
            )
        )
    return (
        "<table><tr><th>阶段</th><th>状态</th><th>adapter</th><th>model</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def render_case(run_dir: Path, out_dir: Path) -> Path | None:
    run = load_json(run_dir / "run.json")
    if run.get("run_kind") != "case" or run.get("status") != "completed":
        return None
    case_id = run["case_id"]
    entry = load_json(Path(run["source_entry_path"]))
    parent_dir = Path(run["parent_article_run_path"])
    segmentation = output_or_empty(parent_dir, "source_segmentation")
    seg_by_id = {s["segment_id"]: s for s in segmentation.get("segments", [])}

    storage_class = manifest_storage_class(entry.get("source_entry_id", ""))
    is_public = storage_class == "tracked_public"

    def seg_text(seg_id: str) -> str:
        segment = seg_by_id.get(seg_id)
        if segment is None:
            return f"（未找到分段 {seg_id}）"
        return segment["content"] if is_public else REDACTED

    extraction = output_or_empty(run_dir, "case_extraction")
    tagging = output_or_empty(run_dir, "entity_tagging")
    dedup = output_or_empty(run_dir, "deduplication")
    resolution = output_or_empty(run_dir, "case_resolution")
    occurrence = output_or_empty(run_dir, "source_occurrence")
    reader = output_or_empty(run_dir, "reader_generation")
    creator = output_or_empty(run_dir, "creator_analysis")
    factual = output_or_empty(run_dir, "factual_check")
    rights = output_or_empty(run_dir, "rights_check")
    packaging = output_or_empty(run_dir, "publication_packaging")

    title = reader.get("reader_title", entry.get("entry_title", case_id))
    parts: list[str] = []
    parts.append(
        "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<title>{esc(case_id)} {esc(title)}</title><style>{CSS}</style></head><body>"
    )
    parts.append(f"<h1>{esc(case_id)}　{esc(title)}</h1>")
    parts.append('<p><a href="index.html">← 返回总览</a></p>')

    # 基本信息
    publish = packaging.get("publish_status", "未知")
    parts.append("<h2>基本信息</h2><table>")
    info_rows = [
        ("Case ID", case_id),
        ("候选 ID", run.get("candidate_id", "")),
        ("来源", f"{entry.get('source_title', '')}（{run.get('source_id', '')} / {run.get('source_catalog_article_id', '')}）"),
        ("条目位置", occurrence.get("locator", {}).get("source_locator", entry.get("locator_text", ""))),
        ("语言", entry.get("language", "")),
        ("原文存储级别", storage_class),
        ("发布状态", publish),
        ("扣留原因", "、".join(packaging.get("withheld_reasons", [])) or "无"),
        ("身份裁定", f"{resolution.get('resolution_kind', '')}（{resolution.get('decision_basis', '')}）"),
        ("Run ID", run["run_id"]),
        ("Pipeline 版本", run.get("pipeline_version", "")),
        ("原文是否展示", "是（公版）" if is_public else "否（受限）"),
    ]
    for label, value in info_rows:
        parts.append(f"<tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>")
    parts.append("</table>")
    if not is_public:
        parts.append(f'<p class="note">{esc(REDACTED)}</p>')

    # 原文分段
    parts.append("<h2>原文分段</h2><table><tr><th>段</th><th>类型</th><th>报告性质</th><th>说话人/作者</th><th>原文</th></tr>")
    for seg in segmentation.get("segments", []):
        parts.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td class=\"src\">{}</td></tr>".format(
                esc(seg["segment_id"].split("-")[-1]),
                esc(seg.get("segment_type", "")),
                esc(seg.get("claim_mode", "")),
                esc(seg.get("speaker_or_author", "")),
                esc(seg["content"] if is_public else REDACTED),
            )
        )
    parts.append("</table>")

    # 读者文本与原文对照
    parts.append("<h2>读者文本（与所依据原文分段对照）</h2>")
    if reader:
        for para in reader.get("paragraphs", []):
            seg_ids = para.get("supporting_source_segment_ids", [])
            cited = "\n".join(seg_text(s) for s in seg_ids)
            parts.append("<table><tr><th style=\"width:50%\">白话段落</th><th>依据的原文分段</th></tr>")
            parts.append(
                f"<tr><td>{esc(para.get('content', ''))}</td>"
                f"<td class=\"src\">{esc(cited)}<br><span class=\"meta\">{esc('、'.join(seg_ids))}</span></td></tr></table>"
            )
        parts.append(f"<p><b>摘要：</b>{esc(reader.get('reader_summary', ''))}</p>")

    # 事实清单
    parts.append("<h2>事实清单</h2><table><tr><th>事实 ID</th><th>命题</th><th>类型</th><th>报告性质</th><th>不确定性</th><th>依据分段</th></tr>")
    for fact in extraction.get("case_facts", []):
        seg_ids = fact.get("supporting_source_segment_ids", [])
        cited = " / ".join(seg_text(s) for s in seg_ids)
        parts.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td class=\"src\">{}<br><span class=\"meta\">{}</span></td></tr>".format(
                esc(fact["case_fact_id"].split("-")[-1]),
                esc(fact.get("proposition_text", "")),
                esc(fact.get("fact_type", "")),
                esc(fact.get("claim_mode", "")),
                esc(fact.get("uncertainty", "")),
                esc(cited),
                esc("、".join(seg_ids)),
            )
        )
    parts.append("</table>")

    # 实体与标签
    parts.append("<h2>实体与标签</h2><table><tr><th>类别</th><th>名称</th><th>说明</th></tr>")
    for person in tagging.get("persons", []):
        parts.append(
            "<tr><td>人物</td><td>{}</td><td>{}（{}；{}）</td></tr>".format(
                esc(person.get("display_name", "")),
                esc(person.get("notes", "")),
                esc(person.get("name_status", "")),
                esc("、".join(person.get("roles", []))),
            )
        )
    for place in tagging.get("places", []):
        parts.append(
            f"<tr><td>地点</td><td>{esc(place.get('display_name', ''))}</td><td>{esc(place.get('notes', ''))}</td></tr>"
        )
    for tag in tagging.get("tags", []):
        parts.append(
            f"<tr><td>标签</td><td>{esc(tag.get('tag', ''))}</td><td>{esc(tag.get('tag_class', ''))}</td></tr>"
        )
    parts.append("</table>")

    # 去重比较
    parts.append("<h2>去重比较记录</h2>")
    if dedup:
        parts.append(f"<p><b>总体结论：</b>{esc(dedup.get('overall_decision', ''))}</p>")
        if dedup.get("candidate_matches"):
            parts.append("<table><tr><th>对比案例</th><th>判断</th><th>相同点</th><th>不同点</th><th>置信度</th></tr>")
            for match in dedup["candidate_matches"]:
                parts.append(
                    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                        esc(match.get("candidate_case_id", "")),
                        esc(match.get("match_decision", "")),
                        esc("；".join(match.get("similarities", []))),
                        esc("；".join(match.get("differences", []))),
                        esc(match.get("confidence", "")),
                    )
                )
            parts.append("</table>")
        else:
            parts.append("<p class=\"meta\">检索范围内没有可供比较的旧案例。</p>")
        parts.append("<ul>" + "".join(f"<li>{esc(r)}</li>" for r in dedup.get("decision_reasons", [])) + "</ul>")

    # 创作分析
    if creator:
        meta = creator.get("creator_metadata", {})
        parts.append("<h2>创作分析</h2>")
        risk_rows = [
            ("推荐用法", meta.get("recommended_usage", "")),
            ("避免用法", meta.get("avoid_usage", "")),
            ("误读风险", meta.get("misinterpretation_risk", "")),
            ("隐私风险", meta.get("privacy_risk", "")),
            ("版权风险", meta.get("copyright_risk", "")),
        ]
        parts.append("<table>" + "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in risk_rows) + "</table>")
        unresolved = meta.get("unresolved_questions", [])
        if unresolved:
            parts.append("<p><b>未决问题：</b></p><ul>" + "".join(f"<li>{esc(q)}</li>" for q in unresolved) + "</ul>")
        parts.append("<table><tr><th>角度</th><th>核心主张</th><th>受众</th><th>教理边界</th></tr>")
        for angle in creator.get("interpretation_angles", []):
            parts.append(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    esc(angle.get("title", "")),
                    esc(angle.get("core_claim", "")),
                    esc("、".join(angle.get("audience", []))),
                    esc(angle.get("doctrinal_boundary", "")),
                )
            )
        parts.append("</table>")

    # 事实检查
    if factual:
        gate = factual.get("gate_result", "")
        parts.append("<h2>事实检查</h2>")
        parts.append(
            f"<p>结论：<span class=\"gate-{esc(gate)}\">{esc(gate)}</span>　"
            f"无依据 {esc(factual.get('unsupported_claim_count', ''))} 条；矛盾 {esc(factual.get('contradicted_claim_count', ''))} 条</p>"
        )
        parts.append("<table><tr><th>claim</th><th>出处</th><th>裁决</th><th>依据</th></tr>")
        for claim in factual.get("claims", []):
            verdict = claim.get("verdict", "")
            refs = "、".join(claim.get("supporting_case_fact_ids", []))
            parts.append(
                "<tr><td>{}</td><td>{}</td><td class=\"verdict-{}\">{}</td><td class=\"meta\">{}</td></tr>".format(
                    esc(claim.get("claim_text", "")),
                    esc(claim.get("source_output", "")),
                    esc(verdict),
                    esc(verdict),
                    esc(refs),
                )
            )
        parts.append("</table>")

    # 版权检查
    if rights:
        gate = rights.get("gate_result", "")
        parts.append("<h2>版权检查</h2>")
        parts.append(
            f"<p>结论：<span class=\"gate-{esc(gate)}\">{esc(gate)}</span>　"
            f"允许公开范围：{esc(rights.get('allowed_display_scope', ''))}　"
            f"依据：{esc(rights.get('rights_review_id', ''))}</p>"
        )
        parts.append("<table><tr><th>输出</th><th>引用情况</th><th>相似风险</th><th>结论</th><th>说明</th></tr>")
        for check in rights.get("checks", []):
            parts.append(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    esc(check.get("output_id", "")),
                    esc(check.get("quotation_status", "")),
                    esc(check.get("expression_similarity_risk", "")),
                    esc(check.get("policy_result", "")),
                    esc(check.get("basis", "")),
                )
            )
        parts.append("</table>")

    # 审核状态
    parts.append("<h2>审核状态</h2>")
    parts.append(stage_rows(run))
    parts.append(f"<p class=\"meta\">报告生成自 {esc(run['run_id'])}；原文哈希 {esc(run.get('source_entry_hash', ''))}</p>")
    parts.append("</body></html>")

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{case_id}.html"
    target.write_text("\n".join(parts), encoding="utf-8")
    return target


def completed_case_runs(runs_root: Path) -> dict[str, Path]:
    """Latest completed case run directory per case_id."""
    latest: dict[str, tuple[str, Path]] = {}
    for pattern in ("*/candidates/*/run.json", "*/cases/*/run.json"):
        for path in runs_root.glob(pattern):
            run = load_json(path)
            if run.get("run_kind") != "case" or run.get("status") != "completed":
                continue
            case_id = run.get("case_id", "")
            if not case_id:
                continue
            key = run.get("updated_at", "")
            if case_id not in latest or key > latest[case_id][0]:
                latest[case_id] = (key, path.parent)
    return {case_id: pair[1] for case_id, pair in sorted(latest.items())}


def render_index(cases: dict[str, Path], out_dir: Path) -> Path:
    rows = []
    for case_id, run_dir in cases.items():
        run = load_json(run_dir / "run.json")
        entry = load_json(Path(run["source_entry_path"]))
        reader = output_or_empty(run_dir, "reader_generation")
        factual = output_or_empty(run_dir, "factual_check")
        creator = output_or_empty(run_dir, "creator_analysis")
        packaging = output_or_empty(run_dir, "publication_packaging")
        meta = creator.get("creator_metadata", {})
        risks = " / ".join(
            f"{label}:{meta.get(key, '-')}"
            for label, key in (("误读", "misinterpretation_risk"), ("隐私", "privacy_risk"), ("版权", "copyright_risk"))
        )
        gate = factual.get("gate_result", "-")
        rows.append(
            "<tr><td><a href=\"{0}.html\">{0}</a></td><td>{1}</td><td>{2}</td><td>{3}</td>"
            "<td class=\"gate-{4}\">{4}（无依据 {5} / 矛盾 {6}）</td><td>{7}</td></tr>".format(
                esc(case_id),
                esc(reader.get("reader_title", entry.get("entry_title", ""))),
                esc(f"{entry.get('source_title', '')}（{run.get('source_id', '')}）"),
                esc(packaging.get("publish_status", "-")),
                esc(gate),
                esc(factual.get("unsupported_claim_count", "-")),
                esc(factual.get("contradicted_claim_count", "-")),
                esc(risks),
            )
        )
    page = (
        "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<title>案例审核总览</title><style>{CSS}</style></head><body>"
        "<h1>案例审核总览</h1>"
        f"<p class=\"meta\">共 {len(rows)} 个已完成案例。点击 Case ID 进入单案例审核报告。</p>"
        "<table><tr><th>Case ID</th><th>标题</th><th>来源</th><th>发布状态</th><th>事实检查</th><th>风险提示</th></tr>"
        + "".join(rows)
        + "</table></body></html>"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "index.html"
    target.write_text(page, encoding="utf-8")
    return target


def run_dirs_from_args(args: argparse.Namespace) -> list[Path]:
    target = args.run_dir.resolve()
    run = load_json(target / "run.json")
    if run.get("run_kind") == "case":
        return [target]
    found = []
    for child in sorted(target.glob("candidates/*/run.json")) + sorted(target.glob("cases/*/run.json")):
        found.append(child.parent)
    if not found:
        raise SystemExit(f"no case runs under {target}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", type=Path, help="Case run directory or article run directory.")
    group.add_argument("--all", action="store_true", help="Render every completed case run under data/pipeline_runs.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    out_dir = args.out_dir
    if args.all:
        cases = completed_case_runs(PIPELINE_RUNS)
        if not cases:
            raise SystemExit("no completed case runs found")
        for case_id, run_dir in cases.items():
            target = render_case(run_dir, out_dir)
            if target:
                print(f"wrote {target}")
    else:
        for run_dir in run_dirs_from_args(args):
            target = render_case(run_dir, out_dir)
            if target:
                print(f"wrote {target}")

    index = render_index(completed_case_runs(PIPELINE_RUNS), out_dir)
    print(f"wrote {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
