#!/usr/bin/env python3
"""Build the README demo GIFs from real recipe runs (before/after wipe).

    make_demo_media.py                  # runs on tests/fixtures/, writes docs/media/
    make_demo_media.py --only spots

Each demo runs a recipe with run_recipe.py on an input image, then animates a wipe from the
untouched input to the result. Needs photocraft-cli and Pillow (docs only; the skill itself
uses the standard library).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / "tests" / "fixtures"
MEDIA = ROOT / "docs" / "media"
WIDTH = 640
INK, PAPER, ACCENT, MUTED = "#061122", "#dceeff", "#f44594", "#32619a"  # docs/media/pixel/palette.json

# name: (input file, recipe, vars, caption). Inputs live in INPUTS; the test fixtures work too.
DEMOS = {
    "color-cast": ("cast.png", "fix-color-cast", {}, "fix-color-cast: warm cast removed"),
    "contrast": ("flat.png", "add-contrast-curve", {}, "add-contrast-curve: flat to punchy"),
    "spots": ("spots.png", "remove-spots", {}, "remove-spots: five dust spots healed"),
    "background": ("subject.png", "replace-background", {}, "replace-background: cut out, new backdrop"),
    "title": ("scene.png", "title-with-shadow", {}, "title-with-shadow: live type with shadow"),
}


def font(size):
    for name in ("/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def run_recipe(src, recipe, variables, out):
    cmd = [sys.executable, str(ROOT / "scripts/run_recipe.py"), str(ROOT / "recipes" / f"{recipe}.json"),
           "--in", str(src), "--out", str(out), "--force"]
    for k, v in variables.items():
        cmd += ["--var", f"{k}={v}"]
    subprocess.run(cmd, check=True, capture_output=True)


def fit(img):
    img = img.convert("RGB")
    return img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)


def label(draw, xy, text, fill):
    f = font(18)
    x, y = xy
    box = draw.textbbox((x, y), text, font=f)
    draw.rounded_rectangle((box[0] - 8, box[1] - 5, box[2] + 8, box[3] + 5), 6, fill=fill)
    draw.text((x, y), text, font=f, fill=PAPER)


def wipe_gif(before, after, caption, path):
    """Frames: hold before, wipe to after, hold after, wipe back."""
    w, h = before.size
    bar = 44
    frames, durations = [], []

    def frame(split):
        canvas = Image.new("RGB", (w, h + bar), INK)
        canvas.paste(before, (0, 0))
        if split > 0:
            canvas.paste(after.crop((0, 0, split, h)), (0, 0))
        d = ImageDraw.Draw(canvas)
        if 0 < split < w:
            d.rectangle((split - 1, 0, split + 1, h), fill=PAPER)
        if split <= w * 0.8:
            label(d, (w - 96, 12), "before", MUTED)
        if split >= w * 0.2:
            label(d, (14, 12), "after", ACCENT)
        d.text((14, h + 12), caption, font=font(18), fill=PAPER)
        return canvas

    steps = 12
    for split, ms in [(0, 900)] + [(round(w * i / steps), 45) for i in range(1, steps + 1)] \
            + [(w, 1600)] + [(round(w * i / steps), 35) for i in range(steps - 1, 0, -1)]:
        frames.append(frame(split))
        durations.append(ms)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    if shutil.which("gifsicle"):  # palette and lossy compression keep README GIFs small
        subprocess.run(["gifsicle", "-b", "-O3", "--lossy=60", "--colors", "160", str(path)],
                       check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--only", nargs="*", choices=sorted(DEMOS))
    names = ap.parse_args().only or list(DEMOS)
    MEDIA.mkdir(parents=True, exist_ok=True)
    report = {}
    with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmp:
        for name in names:
            src, recipe, variables, caption = DEMOS[name]
            out = Path(tmp) / f"{name}.png"
            run_recipe(INPUTS / src, recipe, variables, out)
            before, after = fit(Image.open(INPUTS / src)), fit(Image.open(out))
            wipe_gif(before, after, caption, MEDIA / f"{name}.gif")
            after.save(MEDIA / f"{name}-after.jpg", quality=86)
            report[name] = (MEDIA / f"{name}.gif").stat().st_size
            print(f"{name}: {report[name] // 1024} KB")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
