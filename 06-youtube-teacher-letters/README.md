# T06 YouTube 与法师来信 / YouTube And Teacher Letters

目标：整理 YouTube、法师栏目、听众来信、投稿案例来源。

Goal: organize Case Sources from YouTube, teacher programs, audience letters, and submitted testimonies.

重点：持续产生一手或近一手案例的频道、官网文字稿、字幕、邮件栏目与投稿栏目。

Focus: channels that regularly publish first-hand or near-first-hand accounts, official transcripts, subtitles, mail columns, and submission columns.

## 架构（2026-09-15 对话 #159 第十、十一节）

YouTube 不当"视频收藏"，当持续产生新案例的投稿渠道；不爬 YouTube 网页和字幕（条款限制），发现走官方 Data API。

YouTube is treated as a submission channel, not a video collection. Discovery uses the official Data API only; scraping YouTube pages or captions is out of bounds.

## 现状 / Current State

- **频道登记表**：`../data/youtube_watch/channel_registry.csv`（频道名、频道 ID、法师、对应 repo source_id、监控优先级、发现方式、文字稿链备注）。已预填五个重点频道；channel_id 均 pending（需人工到频道页确认）；信愿法师在注册表中尚无 repo 行，已标注。
- **新视频发现**：`scripts/youtube_watch.py scan` 走官方 Data API v3（playlistItems.list 读 uploads 播放列表，1 quota/次），新视频追加到 `../data/youtube_watch/videos.csv`（含标题、发布日期、description、case_hint 关键词标记），重复扫描不产生重复行。API key 走 `YOUTUBE_API_KEY` 环境变量；无 key 用 `--mock <file>` 离线回放。
- **文字稿获取链**：`scripts/youtube_watch.py transcript --video-id <id>` 按优先级取稿——(1) 法师官网文字稿：频道对应 repo 来源目录中标题匹配的行，用该来源的条目提取器抓正文；(2) 视频 description 自带完整来信；(3) 频道授权字幕——占位未实现（需授权）；(4) 合法获得音视频的本地转写——占位未实现（留待 T06 授权后）。

```bash
python3 scripts/youtube_watch.py channels                                  # 查看频道表
python3 scripts/youtube_watch.py scan --mock playlist_response.json        # 离线回放
YOUTUBE_API_KEY=... python3 scripts/youtube_watch.py scan                  # 真实扫描
python3 scripts/youtube_watch.py transcript --video-id <id>                # 按优先级取文字稿
```
