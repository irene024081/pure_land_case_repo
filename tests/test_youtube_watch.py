from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import youtube_watch  # noqa: E402


MOCK_PAYLOAD = {
    "items": [
        {
            "snippet": {
                "publishedAt": "2026-09-20T01:00:00Z",
                "title": "莲友来信：母亲念佛往生纪实",
                "description": "本期读一封莲友来信……（完整来信内容）",
                "resourceId": {"videoId": "VID001"},
            }
        },
        {
            "snippet": {
                "publishedAt": "2026-09-13T01:00:00Z",
                "title": "共修通知",
                "description": "",
                "resourceId": {"videoId": "VID002"},
            }
        },
    ]
}


class YoutubeWatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.watch = root / "youtube_watch"
        self.watch.mkdir()
        (self.watch / "channel_registry.csv").write_text(
            "channel_name,channel_id,teacher,repo_source_id,watch_priority,discovery_method,transcript_chain,notes\n"
            "测试频道,UCabc123,测试法师,SRC9999,high,youtube_data_api,,\n"
            "待定频道,,待定法师,,medium,youtube_data_api,,\n",
            encoding="utf-8",
        )
        self.mock_payload = root / "playlist.json"
        self.mock_payload.write_text(json.dumps(MOCK_PAYLOAD), encoding="utf-8")
        self.patches = {
            "WATCH_DIR": self.watch,
            "REGISTRY_PATH": self.watch / "channel_registry.csv",
            "VIDEOS_PATH": self.watch / "videos.csv",
            "TRANSCRIPTS_DIR": self.watch / "transcripts",
        }
        self.originals = {name: getattr(youtube_watch, name) for name in self.patches}
        for name, value in self.patches.items():
            setattr(youtube_watch, name, value)

    def tearDown(self) -> None:
        for name, value in self.originals.items():
            setattr(youtube_watch, name, value)
        self.temp.cleanup()

    def scan(self, channel: str = "") -> int:
        args = type("A", (), {"channel": channel, "mock": str(self.mock_payload), "pages": 1})()
        return youtube_watch.cmd_scan(args)

    def test_uploads_playlist_id(self) -> None:
        self.assertEqual(youtube_watch.uploads_playlist_id("UCabc123"), "UUabc123")

    def test_scan_appends_and_flags(self) -> None:
        self.scan()
        rows = youtube_watch.read_videos()
        self.assertEqual(len(rows), 2)
        by_id = {row["video_id"]: row for row in rows}
        self.assertEqual(by_id["VID001"]["case_hint"], "yes")
        self.assertEqual(by_id["VID002"]["case_hint"], "no")
        self.assertEqual(by_id["VID001"]["channel_name"], "测试频道")

    def test_rescan_is_idempotent(self) -> None:
        self.scan()
        self.scan()
        self.assertEqual(len(youtube_watch.read_videos()), 2)

    def test_transcript_from_description(self) -> None:
        self.scan()
        args = type("A", (), {"video_id": "VID001", "mock_transcript": ""})()
        youtube_watch.cmd_transcript(args)
        record = json.loads((self.watch / "transcripts" / "VID001.json").read_text(encoding="utf-8"))
        self.assertEqual(record["method"], "description")
        self.assertIn("莲友来信", record["text"])

    def test_transcript_mock_official_site(self) -> None:
        self.scan()
        text_file = Path(self.temp.name) / "transcript.txt"
        text_file.write_text("官网文字稿全文", encoding="utf-8")
        args = type("A", (), {"video_id": "VID002", "mock_transcript": str(text_file)})()
        youtube_watch.cmd_transcript(args)
        record = json.loads((self.watch / "transcripts" / "VID002.json").read_text(encoding="utf-8"))
        self.assertEqual(record["method"], "official_site")

    def test_transcript_unavailable(self) -> None:
        self.scan()
        args = type("A", (), {"video_id": "VID002", "mock_transcript": ""})()
        with self.assertRaisesRegex(SystemExit, "levels 1-2"):
            youtube_watch.cmd_transcript(args)

    def test_official_site_lookup_via_catalog(self) -> None:
        # channel's repo source has a catalog with a matching article row
        repo_dir = Path(self.temp.name) / "data" / "source_catalogs" / "SRC9999"
        repo_dir.mkdir(parents=True)
        (repo_dir / "source.yml").write_text("extractor_name: extract_wordpress_article.py\n", encoding="utf-8")
        (repo_dir / "articles.csv").write_text(
            "article_id,source_id,source_item_key,title,canonical_url\n"
            "A1,SRC9999,k1,莲友来信：母亲念佛往生纪实,https://example.com/t1\n",
            encoding="utf-8",
        )
        original_root = youtube_watch.ROOT
        youtube_watch.ROOT = Path(self.temp.name)
        # fake scripts dir resolution for the extractor import path is unchanged;
        # wordpress extractor works on simple html
        html = "<article><h1>莲友来信</h1><p>正文一。</p><p>正文二。</p></article>"
        try:
            text = youtube_watch.find_official_transcript(
                {"repo_source_id": "SRC9999"}, "莲友来信：母亲念佛往生纪实", lambda url: html
            )
        finally:
            youtube_watch.ROOT = original_root
        self.assertEqual(text, "正文一。\n\n正文二。")

    def test_scan_requires_key_or_mock(self) -> None:
        os.environ.pop("YOUTUBE_API_KEY", None)
        args = type("A", (), {"channel": "", "mock": "", "pages": 1})()
        with self.assertRaisesRegex(SystemExit, "YOUTUBE_API_KEY"):
            youtube_watch.cmd_scan(args)


if __name__ == "__main__":
    unittest.main()
