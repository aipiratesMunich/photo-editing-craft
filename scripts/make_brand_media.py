#!/usr/bin/env python3
"""Render the pixel-art brand images from docs/media/pixel/*.svg.

    make_brand_media.py     # writes docs/media/social-preview.png and docs/media/banner.png

The SVGs are plain rectangles, so they are drawn here pixel-exact with Pillow (docs only).
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PIXEL = ROOT / "docs" / "media" / "pixel"
MEDIA = ROOT / "docs" / "media"
P = json.loads((PIXEL / "palette.json").read_text())
BG, PANEL, INK, MUTED = P["dark"], P["navy"], P["ice"], "#7f9cc4"
RECT = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" fill="(#[0-9a-fA-F]{6})"/>')


def font(size, bold=True):
    names = ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf" if bold else
             "/System/Library/Fonts/Supplemental/Courier New.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def sprite(name, scale):
    """Draw one asset at an integer scale; returns an RGBA image."""
    svg = (PIXEL / f"{name}.svg").read_text()
    w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
    img = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x, y, rw, rh, color in RECT.findall(svg):
        x, y, rw, rh = (round(float(v) * scale) for v in (x, y, rw, rh))
        if rw and rh:
            d.rectangle((x, y, x + rw - 1, y + rh - 1), fill=color)
    return img


def shadow_text(d, xy, text, size, fill, shadow=P["shadow"]):
    f = font(size)
    x, y = xy
    off = max(2, size // 14)
    d.text((x + off, y + off), text, font=f, fill=shadow)
    d.text((x, y), text, font=f, fill=fill)


def grid(d, w, h, step=32):
    for x in range(0, w, step):
        d.line((x, 0, x, h), fill="#0a1830")
    for y in range(0, h, step):
        d.line((0, y, w, y), fill="#0a1830")


def tag(d, xy, text, color):
    f = font(20)
    x, y = xy
    box = d.textbbox((x, y), text, font=f)
    d.rectangle((box[0] - 10, box[1] - 7, box[2] + 10, box[3] + 7), outline=color, width=2)
    d.text((x, y), text, font=f, fill=color)
    return box[2] + 26


def social_preview():
    w, h = 1280, 640
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    grid(d, w, h)
    d.text((64, 56), "~/ photo-editing-craft", font=font(24), fill=P["blue"])
    shadow_text(d, (60, 120), "RETOUCHER", 92, INK)
    shadow_text(d, (60, 220), "JUDGMENT", 92, P["blue"])
    shadow_text(d, (60, 320), "FOR AGENTS.", 92, INK)
    d.text((64, 440), "Color, retouch, cutouts, type, web + print.", font=font(24, False), fill=MUTED)
    d.text((64, 474), "14 tested recipes. Measured results.", font=font(24, False), fill=MUTED)
    x = 74
    for text, color in [("PHOTOCRAFT", P["green"]), ("PHOTOSHOP", P["blue"]), ("PSD", P["pink"]),
                        ("MIT", P["yellow"])]:
        x = tag(d, (x, 548), text, color)
    for name, px in [("designer", 846), ("artist", 990), ("editor", 1134)]:
        s = sprite(name, 2)
        img.paste(s, (px, 300), s)
    for i, name in enumerate(["photo-editing", "manipulation", "typography", "creative-effects"]):
        s = sprite(name, 1)
        img.paste(s, (870 + i * 96, 150), s)
    return img


def banner():
    w, h = 1600, 400
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    grid(d, w, h)
    shadow_text(d, (64, 92), "PHOTO-EDITING-CRAFT", 78, INK)
    d.text((70, 196), "An agent skill that edits images like a retoucher", font=font(28, False), fill=MUTED)
    d.text((70, 236), "and measures the result. PhotoCraft, Photoshop, PSD.", font=font(28, False), fill=MUTED)
    names = ["photo-editing", "digital-art", "graphic-design", "typography", "manipulation",
             "creative-effects", "open-source"]
    for i, name in enumerate(names):
        img.paste(sprite(name, 1), (72 + i * 84, 300), sprite(name, 1))
    for name, px in [("designer", 1140), ("hacker", 1290), ("artist", 1440)]:
        s = sprite(name, 2)
        img.paste(s, (px, 100), s)
    return img


def main():
    social_preview().save(MEDIA / "social-preview.png", optimize=True)
    banner().save(MEDIA / "banner.png", optimize=True)
    for name in ("social-preview", "banner"):
        p = MEDIA / f"{name}.png"
        print(p.relative_to(ROOT), p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
