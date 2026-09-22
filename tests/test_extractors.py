from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import extract_dazhouxian_entries as dazhouxian  # noqa: E402
import extract_cbeta_xml as cbeta  # noqa: E402
import extract_plb_sea_article as plb_sea  # noqa: E402
import extract_plbtw_article as plbtw  # noqa: E402
import extract_wordpress_article as wordpress  # noqa: E402


CBETA_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xmlns:cb="http://www.cbeta.org/ns/1.0">
<text><body>
<cb:juan fun="open" n="1"/>
<list rend="no-marker"><head>第一卷</head><item>甲類</item></list>
<head>甲類</head>
<cb:div type="other"><head>甲一</head>
<p>甲一传。念佛。<note>校勘注</note>而终。</p>
<p>赞曰。甲一之赞。</p></cb:div>
<cb:div type="other"><head>乙一</head>
<p>乙一传。含附传。</p>
<cb:div type="other"><head>乙一附</head><p>附传内容。</p></cb:div></cb:div>
<cb:juan fun="close" n="1"/>
</body></text>
</TEI>
"""


class CbetaXmlExtractorTest(unittest.TestCase):
    def events(self) -> list[dict]:
        root = cbeta.ET.fromstring(CBETA_FIXTURE)
        body = root.find(f"{cbeta.TEI}text/{cbeta.TEI}body")
        return cbeta.stream_events(body)

    def test_entry_count_and_structure(self) -> None:
        entries = cbeta.extract_entries(self.events(), None, None)
        # 甲類 is structural (no following <p>); the <list> head is the TOC.
        self.assertEqual([entry["title"] for entry in entries], ["甲一", "乙一", "乙一附"])
        first = entries[0]
        self.assertEqual(first["volume"], "1")
        self.assertEqual(first["section"], "甲類")
        self.assertEqual(first["paragraphs"], ["甲一传。念佛。而终。", "赞曰。甲一之赞。"])

    def test_nested_entry_split_and_flag(self) -> None:
        entries = cbeta.extract_entries(self.events(), None, None)
        parent = next(entry for entry in entries if entry["title"] == "乙一")
        child = next(entry for entry in entries if entry["title"] == "乙一附")
        self.assertEqual(parent["nested_heads"], ["乙一附"])
        self.assertEqual(parent["paragraphs"], ["乙一传。含附传。"])
        self.assertEqual(child["paragraphs"], ["附传内容。"])

    def test_rerun_is_stable(self) -> None:
        first = cbeta.extract_entries(self.events(), None, None)
        second = cbeta.extract_entries(self.events(), None, None)
        self.assertEqual(first, second)

    def test_heading_scope(self) -> None:
        entries = cbeta.extract_entries(self.events(), "乙一", None)
        self.assertEqual([entry["title"] for entry in entries], ["乙一", "乙一附"])


class ExtractorSmokeTest(unittest.TestCase):
    def test_dazhouxian_repeated_headings(self) -> None:
        section = "甲\n甲。常念佛。\n\n乙\n乙者。亦念佛。"
        self.assertEqual(
            dazhouxian.extract_entries(section),
            [("甲", "甲\n甲。常念佛。"), ("乙", "乙\n乙者。亦念佛。")],
        )

    def test_wordpress_article(self) -> None:
        html = "<article><h1>Testimony</h1><p>First paragraph.</p><p>Second paragraph.</p></article>"
        self.assertEqual(
            wordpress.article_text(html),
            ("Testimony", "First paragraph.\n\nSecond paragraph."),
        )

    def test_plbtw_article_boundary(self) -> None:
        html = '<div id="in_right"><h2>念佛感應事蹟</h2><h3>案例</h3><p>正文</p><div id="page">stop'
        self.assertEqual(plbtw.article_text(plbtw.article_blocks(html)), ("案例", "正文"))

    def test_plb_sea_article_boundary(self) -> None:
        html = '<div class="article" id="article"><p class="subtitle">案例</p><p>正文</p><div style="text-align:center">stop'
        title, body = plb_sea.html_to_text(plb_sea.extract_article_html(html))
        self.assertEqual(title, "案例")
        self.assertEqual(body, "正文")


if __name__ == "__main__":
    unittest.main()
