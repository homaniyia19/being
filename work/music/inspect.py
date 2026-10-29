#!/usr/bin/env python3
"""Check a tune I can't hear: pitch at a few moments, and a loudness envelope drawn as SVG."""
import math
import struct
import sys
import wave
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("chain.wav"))
with wave.open(str(path)) as w:
    rate = w.getframerate()
    data = struct.unpack(f"<{w.getnframes()}h", w.readframes(w.getnframes()))


def pitch(t, span=0.08):
    """Autocorrelation pitch estimate between 80 and 1000 Hz."""
    s = data[int(t * rate):int((t + span) * rate)]
    best, best_lag = 0, 0
    for lag in range(rate // 1000, rate // 80):
        c = sum(s[i] * s[i + lag] for i in range(0, len(s) - lag, 2))
        if c > best:
            best, best_lag = c, lag
    return rate / best_lag if best_lag else 0


beat = 60 / 104
for label, t in [("first leader note (A4=440)", 6 * beat + 0.2), ("refrain start (D4=293.7)", 30 * beat + 0.2),
                 ("refrain high note (A4=440)", 32 * beat + 0.25)]:
    print(f"{label}: {pitch(t):.1f} Hz")

step = rate // 20
env = [math.sqrt(sum(x * x for x in data[i:i + step:4]) / (step / 4)) for i in range(0, len(data), step)]
peak = max(env) or 1
W, H = 880, 120
pts = " ".join(f"{i * W / len(env):.1f},{H - e / peak * (H - 10):.1f}" for i, e in enumerate(env))
Path(path.with_suffix(".svg")).write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#f3ecdf"/>'
    f'<polyline points="{pts}" fill="none" stroke="#3d352b" stroke-width="1"/></svg>')
mean = lambda a, b: round(sum(env[int(a * 20):int(b * 20)]) / max(1, int((b - a) * 20)) / peak, 2)
# Each round is 36 beats: 24 of verse (leader alone), then 12 of refrain (chorus).
print("verse loudness per round:  ", [mean(6 * beat + r * 36 * beat, 6 * beat + r * 36 * beat + 24 * beat) for r in range(4)])
print("refrain loudness per round:", [mean(6 * beat + r * 36 * beat + 24 * beat, 6 * beat + (r + 1) * 36 * beat) for r in range(4)])
