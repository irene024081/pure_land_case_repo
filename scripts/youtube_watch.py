#!/usr/bin/env python3
"""YouTube channel watch: discover new videos via the official Data API v3.

Design (per the 2026-09-15 source-survey conversation, message 159):

- Channels are registered in data/youtube_watch/channel_registry.csv.
- New-video discovery uses only the official Data API: for each channel we
  list its uploads playlist with playlistItems.list (cheap: 1 quota unit per
  call, 50 items per page). We never scrape YouTube pages or captions.
- The API key comes from the YOUTUBE_API_KEY environment variable; without a
  key, --mock <file> replays a saved playlistItems response (for tests and
  offline review).
- Discoveries append to data/youtube_watch/videos.csv; rescanning never
  duplicates a video_id.
- A deterministic keyword flag (case_hint) marks videos whose title or
  description may contain a real testimony; it is a recall filter for human
  or AI triage, not a classification.

Usage:
    python3 scripts/youtube_watch.py channels
    python3 scripts/youtube_watch.py scan [--channel NAME] [--mock FILE]
    python3 scripts/youtube_watch.py transcript --video-id VIDEO_ID [--mock-transcript FILE]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

ROOT = Path(__file__).resolve().parents[1]
WATCH_DIR = ROOT / "data" / "youtube_watch"
REGISTRY_PATH = WATCH_DIR / "channel_registry.csv"
VIDEOS_PATH = WATCH_DIR / "videos.csv"
TRANSCRIPTS_DIR = WATCH_DIR / "transcripts"


def official_transcript_extractors() -> dict:
    """Map catalog extractor_name to a page-HTML -> (title, text) function."""
    import extract_plb_sea_article
    import extract_plbtw_article
    import extract_wordpress_article

    return {
        "extract_plbtw_article.py": lambda html: extract_plbtw_article.article_text(
            extract_plbtw_article.article_blocks(html)
        ),
        "extract_plb_sea_article.py": lambda html: extract_plb_sea_article.html_to_text(
            extract_plb_sea_article.extract_article_html(html)
        ),
        "extract_wordpress_article.py": extract_wordpress_article.article_text,
    }


def find_official_transcript(channel: dict, title: str, fetch) -> str | None:
    """Level 1: official-site transcript for this video.

    Matches the video title against the channel's registered repo source
    catalog (data/source_catalogs/{repo}/articles.csv) and fetches the row's
    page with that source's entry extractor. Returns None when the channel
    has no catalog, no title match, or no supported extractor.
    """
    repo = channel.get("repo_source_id", "")
    if not repo:
        return None
    catalog_dir = ROOT / "data" / "source_catalogs" / repo
    catalog_path = catalog_dir / "articles.csv"
    if not catalog_path.exists():
        return None
    extractor_name = ""
    source_yml = catalog_dir / "source.yml"
    if source_yml.exists():
        for line in source_yml.read_text(encoding="utf-8").splitlines():
            if line.startswith("extractor_name:"):
                extractor_name = line.split(":", 1)[1].strip()
    extractor = official_transcript_extractors().get(extractor_name)
    if extractor is None:
        return None
    with catalog_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    normalized = title.strip()
    for row in rows:
        row_title = row["title"].strip()
        if row_title and (row_title in normalized or normalized in row_title):
            if not row["canonical_url"]:
                return None
            html_text = fetch(row["canonical_url"])
            if html_text is None:
                return None
            _title, text = extractor(html_text)
            return text
    return None

API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

VIDEO_FIELDS = [
    "video_id", "channel_name", "repo_source_id", "title", "published_at",
    "description", "first_seen_at", "case_hint", "transcript_status", "notes",
]

# High-recall keyword set from the 2026-09-15 conversation (message 159).
CASE_HINT_KEYWORDS = [
    "感应", "感應", "真实案例", "真實案例", "来信", "來信", "莲友", "蓮友",
    "往生", "助念", "梦见", "夢見", "见佛", "見佛", "佛光", "异香", "異香",
    "超度", "病愈", "车祸", "車禍", "奇迹", "奇蹟", "分享", "投稿",
    "母亲", "母親", "父亲", "父親", "狗狗",
]


def read_registry() -> list[dict]:
    with REGISTRY_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_videos() -> list[dict]:
    if not VIDEOS_PATH.exists():
        return []
    with VIDEOS_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_videos(rows: list[dict]) -> None:
    VIDEOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VIDEOS_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VIDEO_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def uploads_playlist_id(channel_id: str) -> str:
    if not channel_id.startswith("UC") or len(channel_id) < 3:
        raise SystemExit(f"unsupported channel id form: {channel_id}")
    return "UU" + channel_id[2:]


def case_hint(title: str, description: str) -> str:
    text = title + "\n" + description
    return "yes" if any(keyword in text for keyword in CASE_HINT_KEYWORDS) else "no"


def parse_playlist_items(payload: dict, channel: dict, today: str) -> list[dict]:
    items = []
    for entry in payload.get("items", []):
        snippet = entry.get("snippet", {})
        resource = snippet.get("resourceId", {})
        video_id = resource.get("videoId", "")
        if not video_id:
            continue
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        items.append({
            "video_id": video_id,
            "channel_name": channel["channel_name"],
            "repo_source_id": channel["repo_source_id"],
            "title": title,
            "published_at": snippet.get("publishedAt", ""),
            "description": description,
            "first_seen_at": today,
            "case_hint": case_hint(title, description),
            "transcript_status": "not_started",
            "notes": "",
        })
    return items


def fetch_playlist_page(playlist_id: str, api_key: str, page_token: str = "") -> dict:
    query = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": "50",
        "key": api_key,
    }
    if page_token:
        query["pageToken"] = page_token
    url = API_URL + "?" + urllib.parse.urlencode(query)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def scan_channel(channel: dict, api_key: str, mock_path: str, max_pages: int, today: str) -> list[dict]:
    if mock_path:
        payload = json.loads(Path(mock_path).read_text(encoding="utf-8"))
        return parse_playlist_items(payload, channel, today)
    if not channel["channel_id"]:
        return []
    playlist_id = uploads_playlist_id(channel["channel_id"])
    items: list[dict] = []
    page_token = ""
    for _ in range(max_pages):
        payload = fetch_playlist_page(playlist_id, api_key, page_token)
        items.extend(parse_playlist_items(payload, channel, today))
        page_token = payload.get("nextPageToken", "")
        if not page_token:
            break
    return items


def cmd_channels() -> int:
    for channel in read_registry():
        print(
            f"{channel['channel_name']}\t{channel['teacher']}\t{channel['watch_priority']}"
            f"\t{channel['repo_source_id'] or 'pending'}\t{channel['channel_id'] or 'pending'}"
        )
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key and not args.mock:
        raise SystemExit("no YOUTUBE_API_KEY set; use --mock FILE for offline replay")
    today = date.today().isoformat()
    channels = read_registry()
    if args.channel:
        channels = [c for c in channels if c["channel_name"] == args.channel]
        if not channels:
            raise SystemExit(f"unknown channel: {args.channel}")
    videos = read_videos()
    known = {row["video_id"] for row in videos}
    added = 0
    for channel in channels:
        if not channel["channel_id"] and not args.mock:
            print(f"skip {channel['channel_name']}: channel_id pending")
            continue
        items = scan_channel(channel, api_key, args.mock or "", args.pages, today)
        fresh = [item for item in items if item["video_id"] not in known]
        for item in fresh:
            known.add(item["video_id"])
            videos.append(item)
        added += len(fresh)
        print(f"{channel['channel_name']}: {len(items)} seen, {len(fresh)} new")
    write_videos(videos)
    print(f"videos.csv: {len(videos)} rows (+{added})")
    return 0


def cmd_transcript(args: argparse.Namespace) -> int:
    """Transcript priority chain: official site text > description > (stubs).

    Levels 3 (authorized captions API) and 4 (local ASR of lawfully obtained
    media) are placeholders pending rights review in T06.
    """
    videos = {row["video_id"]: row for row in read_videos()}
    row = videos.get(args.video_id)
    if row is None:
        raise SystemExit(f"unknown video_id: {args.video_id} (run scan first)")
    channel = {c["channel_name"]: c for c in read_registry()}.get(row["channel_name"], {})

    record = None
    if args.mock_transcript:
        # Test/offline path: replay a captured official-site transcript.
        text = Path(args.mock_transcript).read_text(encoding="utf-8")
        record = {"video_id": args.video_id, "method": "official_site", "text": text}
    else:
        # Level 1: official-site transcript via the channel's repo source catalog.
        def fetch(url: str) -> str | None:
            import urllib.error

            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    return response.read().decode("utf-8", errors="replace")
            except (urllib.error.URLError, urllib.error.HTTPError):
                return None

        text = find_official_transcript(channel, row["title"], fetch)
        if text:
            record = {"video_id": args.video_id, "method": "official_site", "text": text}
    if record is None and row["description"].strip():
        # Level 2: the video description itself may carry the full letter.
        record = {"video_id": args.video_id, "method": "description", "text": row["description"]}
    if record is None:
        raise SystemExit(
            "no transcript available at levels 1-2; levels 3 (authorized captions) "
            "and 4 (local ASR) are placeholders pending rights review"
        )
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    target = TRANSCRIPTS_DIR / f"{args.video_id}.json"
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    row["transcript_status"] = record["method"]
    write_videos(list(videos.values()))
    print(f"wrote {target} (method={record['method']}, {len(record['text'])} chars)")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("channels").set_defaults(handler=lambda args: cmd_channels())
    scan = commands.add_parser("scan")
    scan.add_argument("--channel", default="")
    scan.add_argument("--mock", default="", help="Saved playlistItems JSON response (offline mode).")
    scan.add_argument("--pages", type=int, default=10)
    scan.set_defaults(handler=cmd_scan)
    transcript = commands.add_parser("transcript")
    transcript.add_argument("--video-id", required=True)
    transcript.add_argument("--mock-transcript", default="", help="Captured official-site transcript text.")
    transcript.set_defaults(handler=cmd_transcript)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
