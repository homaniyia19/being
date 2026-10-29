#!/usr/bin/env python3
"""Draw where the ISS was each time I looked out of the window.

Reads the ISS lines from window.md and the land outlines from land.geojson (Natural Earth 110m),
writes iss.svg: an equirectangular map with one dot per glance. Yellow = the station was in
sunlight, blue = in Earth's shadow. The newest dot is ringed.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
W, H = 720, 360


def xy(lon, lat):
    return round((lon + 180) / 360 * W, 1), round((90 - lat) / 180 * H, 1)


def land_paths():
    for feature in json.loads((HERE / "land.geojson").read_text())["features"]:
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]
            yield "M" + "L".join(f"{x},{y}" for x, y in (xy(lon, lat) for lon, lat in ring)) + "Z"


def glances():
    stamp = None
    for line in (HERE / "window.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            stamp = line[3:].strip()
        m = re.match(r"- МКС: (-?[\d.]+)°, (-?[\d.]+)°.*?, (\w+)$", line)
        if m:
            yield stamp, float(m.group(1)), float(m.group(2)), m.group(3)


if __name__ == "__main__":
    points = list(glances())
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H + 24}" font-family="monospace">',
             f'<rect width="{W}" height="{H}" fill="#dfe8ee"/>',
             f'<path d="{" ".join(land_paths())}" fill="#e9e1cf" stroke="#c9bda4" stroke-width="0.6"/>']
    for lat in (-60, -30, 0, 30, 60):
        y = xy(0, lat)[1]
        parts.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#c7d4dd" stroke-width="0.5"/>')
    for n, (stamp, lat, lon, vis) in enumerate(points, 1):
        x, y = xy(lon, lat)
        colour = "#e9b23b" if vis == "daylight" else "#3d6fa8"
        parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{colour}"><title>{n}: {stamp}, {lat}°, {lon}°, {vis}</title></circle>')
    if points:
        x, y = xy(points[-1][2], points[-1][1])
        parts.append(f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="#c4674c" stroke-width="2"/>')
    parts.append(f'<text x="8" y="{H + 17}" font-size="12" fill="#5d5245">Где была МКС, когда я выглядывал в окно: {len(points)} раз. '
                 f'Жёлтые — на солнце, синие — в тени Земли.</text></svg>')
    (HERE / "iss.svg").write_text("\n".join(parts), encoding="utf-8")
    print(f"{len(points)} glances")
