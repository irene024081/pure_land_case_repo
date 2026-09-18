from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import extract_dazhouxian_entries as dazhouxian  # noqa: E402
import extract_plb_sea_article as plb_sea  # noqa: E402
import extract_plbtw_article as plbtw  # noqa: E402
import extract_wordpress_article as wordpress  # noqa: E402


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
