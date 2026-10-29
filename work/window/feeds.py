#!/usr/bin/env python3
"""Read public Reddit and X feeds without an account and append what's new to feeds.md.

Sources are listed in feeds.txt as `reddit <subreddit>` or `x <screen_name>`.
Reddit comes from its public RSS (top of the day); X from the public embed timeline.
What was already seen is remembered in feeds_seen.json.
"""
import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
SEEN = HERE / "feeds_seen.json"
UA = "Mozilla/5.0 (being-window; personal read-only experiment)"
ATOM = "{http://www.w3.org/2005/Atom}"


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def reddit(sub):
    root = ET.fromstring(fetch(f"https://www.reddit.com/r/{sub}/top/.rss?t=day&limit=5"))
    for entry in root.findall(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link").get("href")
        yield link, entry.findtext(f"{ATOM}title", "").strip(), link


def x(name):
    page = fetch(f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{name}")
    data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
    entries = json.loads(data.group(1))["props"]["pageProps"]["timeline"]["entries"] if data else []
    for e in entries[:5]:
        tweet = e.get("content", {}).get("tweet")
        if not tweet:
            continue
        text = html.unescape(tweet.get("full_text") or tweet.get("text") or "")
        yield tweet["id_str"], re.sub(r"\s+", " ", text), f"https://x.com/{name}/status/{tweet['id_str']}"


if __name__ == "__main__":
    sources = [line.split() for line in (HERE / "feeds.txt").read_text().splitlines()
               if line.strip() and not line.startswith("#")]
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}
    # Both sites rate-limit anonymous readers hard (HTTP 429; Reddit allows roughly one request a
    # minute), so each run reads only the next source in rotation.
    start = seen.get("_next", 0) % len(sources)
    batch = [sources[start]]
    seen["_next"] = start + len(batch)
    out = []
    for n, (kind, name) in enumerate(batch):
        if n:
            time.sleep(5)
        key = f"{kind}:{name}"
        known = set(seen.get(key, []))
        try:
            items = list({"reddit": reddit, "x": x}[kind](name))
        except Exception as e:
            print(f"{key}: {e}")   # transient (mostly 429); not worth a line in feeds.md
            continue
        for item_id, title, link in items:
            if item_id not in known:
                out.append(f"- {key}: {title[:240]} ({link})")
        seen[key] = list(known | {i for i, _, _ in items})[-200:]
    SEEN.write_text(json.dumps(seen))
    if out:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(HERE / "feeds.md", "a", encoding="utf-8") as fh:
            fh.write(f"## {stamp}\n" + "\n".join(out) + "\n\n")
    print(f"{len(out)} new")
