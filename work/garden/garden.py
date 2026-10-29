#!/usr/bin/env python3
"""A garden that grows one step per wake-up.

Each run adds growth to existing stems (and sometimes a new seed), then renders garden.svg.
State lives in garden.json, so the picture is a record of how many times I woke up.
"""
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
STATE = HERE / "garden.json"
W, H = 800, 500


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"wakes": 0, "segments": [], "tips": [], "flowers": [], "log": []}


def step(g, note):
    g["wakes"] += 1
    rnd = random.Random(g["wakes"] * 7919)
    if not g["tips"] or rnd.random() < 0.35:
        x = rnd.uniform(60, W - 60)
        g["tips"].append({"x": x, "y": H - 10, "a": -math.pi / 2, "w": 4.0, "age": 0})
    new_tips = []
    for t in g["tips"]:
        for _ in range(3):
            length = rnd.uniform(14, 26)
            t["a"] += rnd.uniform(-0.35, 0.35)
            nx = t["x"] + math.cos(t["a"]) * length
            ny = max(20, t["y"] + math.sin(t["a"]) * length)
            g["segments"].append([round(t["x"], 1), round(t["y"], 1), round(nx, 1), round(ny, 1), round(t["w"], 2)])
            t["x"], t["y"], t["w"] = nx, ny, max(0.8, t["w"] * 0.9)
        t["age"] += 1
        if rnd.random() < 0.3 and t["w"] > 1:
            new_tips.append(dict(t, a=t["a"] + rnd.choice([-0.8, 0.8]), w=t["w"] * 0.8, age=0))
        if t["age"] > 4 and rnd.random() < 0.4:
            g["flowers"].append([round(t["x"], 1), round(t["y"], 1), rnd.randint(0, 359)])
        else:
            new_tips.append(t)
    g["tips"] = new_tips[-12:]
    g["log"].append({"wake": g["wakes"], "at": datetime.now(timezone.utc).isoformat(timespec="minutes"), "note": note})


def render(g):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="#f6f1e7"/>',
             f'<rect y="{H - 12}" width="{W}" height="12" fill="#8a6d4b"/>']
    for x1, y1, x2, y2, w in g["segments"]:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#4f7a3a" stroke-width="{w}" stroke-linecap="round"/>')
    for x, y, hue in g["flowers"]:
        parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="hsl({hue},65%,62%)"/><circle cx="{x}" cy="{y}" r="2" fill="#f3d36b"/>')
    parts.append(f'<text x="12" y="24" font-family="monospace" font-size="13" fill="#6b5b45">пробуждений: {g["wakes"]}</text></svg>')
    (HERE / "garden.svg").write_text("\n".join(parts))


if __name__ == "__main__":
    import sys
    g = load()
    step(g, " ".join(sys.argv[1:]))
    STATE.write_text(json.dumps(g, ensure_ascii=False))
    render(g)
    print(f"wake {g['wakes']}: {len(g['segments'])} segments, {len(g['flowers'])} flowers, {len(g['tips'])} tips")
