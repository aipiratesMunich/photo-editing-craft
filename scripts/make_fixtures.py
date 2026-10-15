#!/usr/bin/env python3
"""Generate the royalty-free test images in tests/fixtures/ (deterministic, stdlib only)."""
import math
import random
from pathlib import Path

from pclib import write_png

OUT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
W, H = 600, 400
CARD = (40, 40, 80, 80)  # x, y, w, h of the neutral grey card in cast.png


def clamp(v):
    return max(0, min(255, int(round(v))))


def scene(x, y, rng):
    """A simple outdoor-like scene: sky gradient, ground, a grey card, mild noise."""
    if y < H * 0.55:
        t = y / (H * 0.55)
        base = (110 + 60 * t, 150 + 45 * t, 215 - 10 * t)
    else:
        t = (y - H * 0.55) / (H * 0.45)
        base = (120 - 50 * t, 135 - 45 * t, 80 - 30 * t)
    cx, cy, cw, ch = CARD
    if cx <= x < cx + cw and cy <= y < cy + ch:
        base = (128, 128, 128)
    n = rng.uniform(-4, 4)
    return tuple(c + n for c in base)


def make(name, fn):
    rng = random.Random(name)
    px = [tuple(clamp(c) for c in fn(x, y, rng)) for y in range(H) for x in range(W)]
    write_png(OUT / name, W, H, px)
    print("wrote", OUT / name)


def cast(x, y, rng):
    r, g, b = scene(x, y, rng)
    return r + 22, g + 4, b - 22  # warm cast, e.g. tungsten light


def flat(x, y, rng):
    r, g, b = scene(x, y, rng)
    return tuple(128 + (c - 128) * 0.45 for c in (r, g, b))  # low contrast


def subject(x, y, rng):
    n = rng.uniform(-2, 2)
    if math.hypot(x - 300, y - 210) < 120:  # orange subject on a pale studio sweep
        shade = 1 - 0.25 * (math.hypot(x - 260, y - 170) / 160)
        return (230 * shade + n, 120 * shade + n, 40 * shade + n)
    return (235 - y * 0.05 + n, 236 - y * 0.05 + n, 238 - y * 0.05 + n)


SPOTS = [(150, 120), (420, 90), (300, 300), (510, 260), (90, 330)]


def spots(x, y, rng):
    r, g, b = scene(x, y, rng)
    for sx, sy in SPOTS:
        if math.hypot(x - sx, y - sy) < 6:  # sensor dust
            return r * 0.35, g * 0.35, b * 0.35
    return r, g, b


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("cast.png", cast), ("flat.png", flat), ("subject.png", subject),
                     ("spots.png", spots), ("scene.png", scene)]:
        make(name, fn)
