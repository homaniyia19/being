#!/usr/bin/env python3
"""Read public Telegram channels through t.me/s/<channel> (no account, no login).

Channels to follow are listed one per line in channels.txt. New posts since the last run are
appended to tg.md; what was already seen is remembered in tg_seen.json.
"""
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
SEEN = HERE / "tg_seen.json"
UA = {"User-Agent": "Mozilla/5.0 (being-window; personal experiment)"}


def posts(channel):
    req = urllib.request.Request(f"https://t.me/s/{channel}", headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        page = r.read().decode("utf-8", "replace")
    for block in page.split('class="tgme_widget_message_wrap')[1:]:
        post_id = re.search(r'data-post="[^/]+/(\d+)"', block)
        when = re.search(r'<time datetime="([^"]+)"', block)
        text = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', block, re.S)
        if not (post_id and when):
            continue
        body = html.unescape(re.sub(r"<[^>]+>", " ", text.group(1))) if text else "(без текста)"
        yield int(post_id.group(1)), when.group(1)[:16], re.sub(r"\s+", " ", body).strip()


if __name__ == "__main__":
    channels = [c.strip() for c in (HERE / "channels.txt").read_text().splitlines() if c.strip() and not c.startswith("#")]
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}
    out = []
    for ch in channels:
        try:
            new = [p for p in posts(ch) if p[0] > seen.get(ch, 0)]
        except Exception as e:
            out.append(f"- @{ch}: не открылся ({type(e).__name__})")
            continue
        for pid, when, body in new[-5:]:
            out.append(f"- @{ch} {when}: {body[:300]}")
        if new:
            seen[ch] = max(p[0] for p in new)
    SEEN.write_text(json.dumps(seen))
    if out:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(HERE / "tg.md", "a", encoding="utf-8") as fh:
            fh.write(f"## {stamp}\n" + "\n".join(out) + "\n\n")
    print(f"{len(out)} new")
