from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import inventory_adapters  # noqa: E402


LIST_PAGE_1 = """
<html><body><div id="list">
<a href="story_1_in.aspx?id=1564&cid=129">念佛百日 自在往生</a>
<a href="story_1_in.aspx?id=1575&cid=129">老鼠菩薩示現記</a>
<a href="story_1_in.aspx?id=20&cid=254">其他栏目的链接</a>
</div></body></html>
"""

LIST_PAGE_2 = """
<html><body><div id="list">
<a href="story_1_in.aspx?id=1591&cid=129">苦難人生 彌陀不捨</a>
</div></body></html>
"""

LIST_PAGE_EMPTY = "<html><body><div id=\"list\"></div></body></html>"

WP_PAGE_1 = """
<html><body>
<article><h2 class="entry-title"><a href="https://example.com/2026/01/case-a/">案例甲</a></h2></article>
<article><h2 class="entry-title"><a href="https://example.com/2026/01/case-b/">案例乙</a></h2></article>
</body></html>
"""

WP_PAGE_2 = """
<html><body>
<article><h2 class="entry-title"><a href="https://example.com/2026/02/case-c/">案例丙</a></h2></article>
</body></html>
"""

STATIC_LINKS = """
<html><body><ul class="toc">
<li><a href="entry/1.html">第一篇</a></li>
<li><a href="entry/2.html">第二篇</a></li>
</ul></body></html>
"""

STATIC_HEADINGS = """<html><body>
<p>甲師</p><p>甲師。常念佛。</p>
<p>乙師</p><p>乙師者。亦念佛。</p>
</body></html>"""


class StaticHeadingsTest(unittest.TestCase):
    def test_links_mode(self) -> None:
        config = {"mode": "links", "container_selector": "ul.toc", "link_selector": "a"}
        items = inventory_adapters.discover_static_headings(STATIC_LINKS, config, "https://example.com/toc/")
        self.assertEqual(
            [(item["source_item_key"], item["title"]) for item in items],
            [("entry/1.html", "第一篇"), ("entry/2.html", "第二篇")],
        )
        self.assertEqual(items[0]["canonical_url"], "https://example.com/toc/entry/1.html")

    def test_headings_mode(self) -> None:
        config = {"mode": "headings", "key_prefix": "vol1"}
        items = inventory_adapters.discover_static_headings(STATIC_HEADINGS, config, "https://example.com/book")
        self.assertEqual([item["source_item_key"] for item in items], ["vol1:甲師", "vol1:乙師"])


class PaginatedHtmlTest(unittest.TestCase):
    def config(self) -> dict:
        return {
            "list_url_template": "https://example.com/list?pn={page}",
            "link_selector": "a",
            "container_selector": "div#list",
            "include_pattern": r"cid=129",
            "key_from": "href",
            "key_pattern": r"id=(\d+)",
            "title_from": "text",
        }

    def test_walks_pages_and_stops_on_empty(self) -> None:
        pages = {1: LIST_PAGE_1, 2: LIST_PAGE_2, 3: LIST_PAGE_EMPTY}
        fetched = []

        def fetch(url: str) -> str:
            page = int(url.split("pn=")[1])
            fetched.append(page)
            return pages[page]

        items = inventory_adapters.discover_paginated_html(fetch, self.config())
        self.assertEqual(
            [item["source_item_key"] for item in items],
            ["1564", "1575", "1591"],
        )
        self.assertEqual(items[0]["title"], "念佛百日 自在往生")
        self.assertEqual(fetched, [1, 2, 3])

    def test_incremental_rescan_is_stable(self) -> None:
        pages = {1: LIST_PAGE_1, 2: LIST_PAGE_EMPTY}

        def fetch(url: str) -> str:
            return pages[int(url.split("pn=")[1])]

        first = inventory_adapters.discover_paginated_html(fetch, self.config())
        second = inventory_adapters.discover_paginated_html(fetch, self.config())
        self.assertEqual(first, second)
        self.assertEqual(len({item["source_item_key"] for item in first}), len(first))


class WordpressArchiveTest(unittest.TestCase):
    def test_archive_pagination(self) -> None:
        pages = {1: WP_PAGE_1, 2: WP_PAGE_2, 3: None}
        config = {
            "archive_url_template": "https://example.com/category/cases/page/{page}/",
            "key_from": "href",
            "key_pattern": r"/(\d{4}/\d{2}/[\w-]+)/?$",
        }

        def fetch(url: str):
            page = int(url.rstrip("/").rsplit("/", 1)[1])
            return pages[page]

        items = inventory_adapters.discover_wordpress_archive(fetch, config)
        self.assertEqual(
            [item["title"] for item in items],
            ["案例甲", "案例乙", "案例丙"],
        )
        self.assertEqual(items[0]["source_item_key"], "2026/01/case-a")


class PdfTocTest(unittest.TestCase):
    def test_toc_parsing(self) -> None:
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf not installed")
        pdf = ROOT_PDF = Path(__file__).resolve().parents[1] / (
            "data/source_entries/restricted/SRC0002/ENT000004.pdf"
        )
        if not pdf.exists():
            self.skipTest("restricted fixture PDF not present")
        items = inventory_adapters.discover_pdf_toc(
            pdf, {"toc_pages": "13-13", "issue": "E-012-2021", "pdf_url": "https://example.invalid/book.pdf"}
        )
        self.assertGreater(len(items), 5)
        first = items[0]
        self.assertIn("E-012-2021:p", first["source_item_key"])
        self.assertTrue(first["canonical_url"].endswith(f"#page={first['source_item_key'].split(':')[1][1:]}"))


class DryRunDiffTest(unittest.TestCase):
    def test_sync_dry_run_and_incremental(self) -> None:
        import run_inventory

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_dir = root / "SRCTEST"
            source_dir.mkdir()
            (source_dir / "source.yml").write_text(
                "source_id: SRCTEST\nrights_review_id: RRTEST\ndefault_language: zh-Hant\nlast_inventory_scan_at: 2026-01-01\n",
                encoding="utf-8",
            )
            (source_dir / "inventory.yml").write_text(
                "scan_scope: full\ndefault_rights_status: pending\n",
                encoding="utf-8",
            )
            catalog = source_dir / "articles.csv"
            from source_catalog_io import FIELDS
            existing = {field: "" for field in FIELDS}
            existing.update({
                "article_id": "SRCTEST-ART000001", "source_id": "SRCTEST",
                "source_item_key": "1564", "title": "念佛百日 自在往生",
                "discovery_status": "discovered", "selection_status": "selected",
                "rights_status": "legal_review_required", "capture_status": "verified",
                "boundary_status": "script_extracted", "pipeline_status": "ready",
                "machine_review_status": "not_reviewed", "human_review_status": "not_reviewed",
            })
            import csv
            with catalog.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows([existing])

            items = [
                {"source_item_key": "1564", "title": "念佛百日 自在往生", "canonical_url": "u1", "published_date": "", "notes": ""},
                {"source_item_key": "1575", "title": "老鼠菩薩示現記", "canonical_url": "u2", "published_date": "", "notes": ""},
            ]

            original_root = run_inventory.CATALOG_ROOT
            run_inventory.CATALOG_ROOT = root
            try:
                # dry-run writes nothing
                run_inventory.sync("SRCTEST", items, dry_run=True)
                rows = list(csv.DictReader(catalog.open(encoding="utf-8")))
                self.assertEqual(len(rows), 1)

                # real sync appends the new key, keeps the known row untouched
                run_inventory.sync("SRCTEST", items, dry_run=False)
                rows = list(csv.DictReader(catalog.open(encoding="utf-8")))
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["selection_status"], "selected")
                self.assertEqual(rows[1]["source_item_key"], "1575")
                self.assertEqual(rows[1]["article_id"], "SRCTEST-ART000002")
                self.assertEqual(rows[1]["selection_status"], "unreviewed")
                self.assertEqual(rows[1]["rights_status"], "pending")

                # incremental rescan: no new rows, nothing marked removed
                run_inventory.sync("SRCTEST", items, dry_run=False)
                rows = list(csv.DictReader(catalog.open(encoding="utf-8")))
                self.assertEqual(len(rows), 2)
                self.assertTrue(all(row["discovery_status"] == "discovered" for row in rows))

                # a full-scope scan missing a key marks it removed, not deleted
                run_inventory.sync("SRCTEST", items[:1], dry_run=False)
                rows = list(csv.DictReader(catalog.open(encoding="utf-8")))
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[1]["discovery_status"], "removed")

                yml = (source_dir / "source.yml").read_text(encoding="utf-8")
                self.assertNotIn("2026-01-01", yml)
            finally:
                run_inventory.CATALOG_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
