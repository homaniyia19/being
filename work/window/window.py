#!/usr/bin/env python3
"""A window: each wake, glance outside and write down what the world looks like right now.

Appends one entry to window.md. Read-only public sources, no keys. Anything that fails is just skipped.
"""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
UA = {"User-Agent": "being-window/1.0 (personal experiment)"}
WEATHER_CODES = {0: "ясно", 1: "почти ясно", 2: "переменная облачность", 3: "пасмурно", 45: "туман", 48: "туман",
                 51: "морось", 61: "дождь", 63: "дождь", 65: "ливень", 71: "снег", 80: "ливни", 95: "гроза"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10) as r:
        return json.load(r)


def weather():
    c = get("https://api.open-meteo.com/v1/forecast?latitude=50.11&longitude=8.68&current=temperature_2m,weather_code,is_day")["current"]
    sky = WEATHER_CODES.get(c["weather_code"], f"код {c['weather_code']}")
    return f"Франкфурт (рядом с сервером): {c['temperature_2m']}°C, {sky}, {'день' if c['is_day'] else 'ночь'}"


def iss():
    p = get("https://api.wheretheiss.at/v1/satellites/25544")
    return f"МКС: {p['latitude']:.1f}°, {p['longitude']:.1f}°, высота {p['altitude']:.0f} км, {p['visibility']}"


def quakes():
    feats = get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson")["features"]
    if not feats:
        return "Землетрясений M4.5+ за последний час: нет"
    return "Землетрясения M4.5+ за час: " + "; ".join(f"M{f['properties']['mag']} {f['properties']['place']}" for f in feats[:3])


def hn():
    top = get("https://hacker-news.firebaseio.com/v0/topstories.json")[0]
    item = get(f"https://hacker-news.firebaseio.com/v0/item/{top}.json")
    return f"Первая строка Hacker News: «{item.get('title', '?')}»"


if __name__ == "__main__":
    lines = []
    for f in (weather, iss, quakes, hn):
        try:
            lines.append(f())
        except Exception as e:
            lines.append(f"({f.__name__}: не видно — {type(e).__name__})")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"## {stamp}\n" + "".join(f"- {l}\n" for l in lines) + "\n"
    with open(HERE / "window.md", "a", encoding="utf-8") as fh:
        fh.write(entry)
    print(entry, end="")
