#!/usr/bin/env python3
""""Chain" — a short original tune in the spirit of the Faroese chain dance.

No instruments, as in the dance: a leader sings the verse lines, a chorus answers with the refrain,
and the dancers' feet keep time, six steps to a bar. Four rounds; each round one more voice joins the
chorus, the way the ring grows as people join the dance.

Pure standard library: writes chain.wav (mono, 22 kHz, 16-bit).
"""
import math
import random
import struct
import wave
from pathlib import Path

RATE = 22050
BPM = 104
BEAT = 60 / BPM
random.seed(7)

# D Dorian. (midi note, beats); every line is two bars of six beats.
VERSE_A = [(69, 1), (69, 1), (67, 1), (65, 1), (67, 1), (69, 1), (72, 2), (71, 1), (69, 1), (67, 2)]
VERSE_B = [(69, 1), (67, 1), (65, 1), (64, 1), (65, 1), (67, 1), (65, 1), (64, 1), (62, 2), (62, 2)]
REFRAIN = [(62, 1), (65, 1), (69, 2), (67, 1), (65, 1), (64, 1), (65, 1), (67, 1), (64, 1), (62, 2)]
ROUNDS = 4


def freq(note):
    return 440 * 2 ** ((note - 69) / 12)


def voice(buf, start, note, beats, gain, detune=0.0, vib_phase=0.0):
    """A plain sung vowel: a few harmonics, soft attack, slight vibrato."""
    f0 = freq(note) * (1 + detune)
    n = int(beats * BEAT * RATE)
    s0 = int(start * RATE)
    harmonics = [(1, 1.0), (2, 0.5), (3, 0.32), (4, 0.12), (5, 0.08)]
    phase = 0.0
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / 0.06) * min(1.0, (n - i) / (0.12 * RATE))
        vib = 1 + 0.006 * math.sin(2 * math.pi * 5.2 * t + vib_phase) * min(1.0, t / 0.3)
        phase += 2 * math.pi * f0 * vib / RATE
        s = sum(a * math.sin(h * phase) for h, a in harmonics)
        idx = s0 + i
        if idx < len(buf):
            buf[idx] += gain * env * s


def stamp(buf, start, heavy):
    """A foot on a wooden floor: a low thump plus a short scuff."""
    s0 = int(start * RATE)
    n = int(0.18 * RATE)
    gain = 0.55 if heavy else 0.3
    for i in range(n):
        t = i / RATE
        thump = math.sin(2 * math.pi * (70 - 120 * t) * t) * math.exp(-t * 28)
        scuff = (random.random() * 2 - 1) * math.exp(-t * 90) * 0.4
        idx = s0 + i
        if idx < len(buf):
            buf[idx] += gain * (thump + scuff)


def line(buf, start, notes, singers, drone=False):
    t = start
    for note, beats in notes:
        for k in range(singers):
            # Each extra singer is a little off in pitch and timing, like real people.
            voice(buf, t + k * 0.012, note - (12 if k % 3 == 2 else 0), beats,
                  # Slightly detuned voices add up roughly as sqrt(n), so n**-0.2 per voice lets the
                  # chorus grow (about n**0.3 overall) without swamping the leader.
                  gain=0.22 * singers ** -0.2, detune=(k - singers / 2) * 0.0025, vib_phase=k)
        t += beats * BEAT
    if drone:
        voice(buf, start, 50, 12, gain=0.07)
    return t


if __name__ == "__main__":
    bars = 1 + ROUNDS * 6
    total = bars * 6 * BEAT + 1.5
    buf = [0.0] * int(total * RATE)

    for beat in range(bars * 6):
        stamp(buf, beat * BEAT, heavy=beat % 6 in (0, 3))

    t = 6 * BEAT                      # one bar of feet alone, then the leader comes in
    for r in range(ROUNDS):
        t = line(buf, t, VERSE_A, singers=1)
        t = line(buf, t, VERSE_B, singers=1)
        t = line(buf, t, REFRAIN, singers=2 + r, drone=True)

    peak = max(abs(x) for x in buf) or 1
    with wave.open(str(Path(__file__).with_name("chain.wav")), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(32000 * x / peak)) for x in buf))
    print(f"{total:.1f}s, {bars} bars")
