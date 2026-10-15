#!/usr/bin/env python3
"""Look before you claim done: report measurable facts about an image and check expectations.

    verify.py IMAGE [--preview out.png] [--region x,y,w,h] [--expect '{...}' | --expect file.json]

Prints JSON facts (size, mode, layers, tone and color statistics). With --expect, exits 1 and
lists every failed assertion. Assertion keys:

    width, height, mode, depth, resolution        exact match (mode e.g. "Rgb", "Cmyk")
    layers_min, layers_max                        count of layers, groups included
    layer_kinds                                   list of kinds that must exist, e.g. ["Type"]
    has_mask                                      true: at least one layer has a mask
    mean_luma_between, luma_std_min, luma_std_max whole image, 0..255
    mean_chroma_min                               average max(rgb)-min(rgb), a saturation proxy
    clipped_max                                   % of pixels at pure black or white
    regions: [{"region":[x,y,w,h], "mean_luma_between":[a,b],
               "max_channel_spread":n, "mean_rgb_near":[[r,g,b], tol],
               "mean_chroma_min":n, "alpha_max":n}]
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from pclib import PhotoCraftError, Session, common_root, read_png, walk_layers


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def stats(px):
    n = len(px) or 1
    lum = [luma(r, g, b) for r, g, b, _ in px]
    mean = sum(lum) / n
    std = (sum((v - mean) ** 2 for v in lum) / n) ** 0.5
    rgb = [sum(p[i] for p in px) / n for i in range(3)]
    return {
        "mean_rgb": [round(c, 1) for c in rgb],
        "mean_luma": round(mean, 1),
        "luma_std": round(std, 1),
        "channel_spread": round(max(rgb) - min(rgb), 1),
        "mean_chroma": round(sum(max(p[:3]) - min(p[:3]) for p in px) / n, 1),
        "clipped_shadows_pct": round(100 * sum(v < 1 for v in lum) / n, 2),
        "clipped_highlights_pct": round(100 * sum(v > 254 for v in lum) / n, 2),
        "mean_alpha": round(sum(p[3] for p in px) / n, 1),
    }


def crop(width, height, px, region, scale):
    x, y, w, h = (int(round(v * scale)) for v in region)
    if x < 0 or y < 0 or x + max(w, 1) > width or y + max(h, 1) > height:
        raise PhotoCraftError(f"region {list(region)} lies outside the image "
                              f"({round(width / scale)} x {round(height / scale)})")
    w, h = max(w, 1), max(h, 1)
    return [px[(y + j) * width + x + i] for j in range(h) for i in range(w)]


def analyze(path, regions=(), preview=None, cli=None):
    path = Path(path).resolve()
    paths = [path] + ([Path(preview).resolve()] if preview else [])
    with tempfile.TemporaryDirectory(dir=path.parent) as tmp, \
            Session(cli, root=common_root(*paths, tmp)) as s:
        s.call("doc.open", {"path": str(path)})
        doc = s.call("doc.inspect")
        render = Path(tmp) / "render.png"
        max_side = 0 if max(doc["width"], doc["height"]) <= 2400 else 1200
        s.call("doc.render", {"path": str(render), "maxSide": max_side})
        if preview:
            s.call("doc.render", {"path": str(Path(preview).resolve()), "maxSide": 1024})
        w, h, px = read_png(render)
    scale = w / doc["width"]
    layers = [{"name": l["name"], "kind": l["kind"], "blend": l.get("blend"),
               "opacity": l.get("opacity"), "mask": l.get("hasMask"), "visible": l.get("visible"),
               "depth": d} for d, l in walk_layers(doc["layers"])]
    facts = {
        "file": str(path), "width": doc["width"], "height": doc["height"],
        "mode": doc["mode"], "depth": doc["depth"], "resolution": doc["resolution"],
        "layers": layers, "image": stats(px),
        "regions": [{"region": list(r), **stats(crop(w, h, px, r, scale))} for r in regions],
    }
    return facts


def between(value, bounds):
    return bounds[0] <= value <= bounds[1]


def check(facts, expect):
    fails = []

    def need(ok, msg):
        if not ok:
            fails.append(msg)

    for key in ("width", "height", "mode", "depth", "resolution"):
        if key in expect:
            need(facts[key] == expect[key], f"{key} is {facts[key]}, expected {expect[key]}")
    n = len(facts["layers"])
    if "layers_min" in expect:
        need(n >= expect["layers_min"], f"{n} layers, expected at least {expect['layers_min']}")
    if "layers_max" in expect:
        need(n <= expect["layers_max"], f"{n} layers, expected at most {expect['layers_max']}")
    kinds = {l["kind"] for l in facts["layers"]}
    for kind in expect.get("layer_kinds", []):
        need(kind in kinds, f"no layer of kind {kind} (found {sorted(kinds)})")
    if expect.get("has_mask"):
        need(any(l["mask"] for l in facts["layers"]), "no layer has a mask")
    img = facts["image"]
    if "mean_luma_between" in expect:
        need(between(img["mean_luma"], expect["mean_luma_between"]),
             f"mean luma {img['mean_luma']} outside {expect['mean_luma_between']}")
    if "luma_std_min" in expect:
        need(img["luma_std"] >= expect["luma_std_min"],
             f"luma std {img['luma_std']} below {expect['luma_std_min']} (too flat)")
    if "luma_std_max" in expect:
        need(img["luma_std"] <= expect["luma_std_max"],
             f"luma std {img['luma_std']} above {expect['luma_std_max']}")
    if "mean_chroma_min" in expect:
        need(img["mean_chroma"] >= expect["mean_chroma_min"],
             f"mean chroma {img['mean_chroma']} below {expect['mean_chroma_min']}")
    if "clipped_max" in expect:
        clipped = img["clipped_shadows_pct"] + img["clipped_highlights_pct"]
        need(clipped <= expect["clipped_max"], f"{clipped}% clipped, max {expect['clipped_max']}%")
    for spec, got in zip(expect.get("regions", []), facts["regions"]):
        label = f"region {spec['region']}"
        if "mean_luma_between" in spec:
            need(between(got["mean_luma"], spec["mean_luma_between"]),
                 f"{label}: mean luma {got['mean_luma']} outside {spec['mean_luma_between']}")
        if "max_channel_spread" in spec:
            need(got["channel_spread"] <= spec["max_channel_spread"],
                 f"{label}: channel spread {got['channel_spread']} > {spec['max_channel_spread']}"
                 f" (rgb {got['mean_rgb']})")
        if "mean_rgb_near" in spec:
            target, tol = spec["mean_rgb_near"]
            off = max(abs(a - b) for a, b in zip(got["mean_rgb"], target))
            need(off <= tol, f"{label}: rgb {got['mean_rgb']} not within {tol} of {target}")
        if "mean_chroma_min" in spec:
            need(got["mean_chroma"] >= spec["mean_chroma_min"],
                 f"{label}: mean chroma {got['mean_chroma']} below {spec['mean_chroma_min']}")
        if "alpha_max" in spec:
            need(got["mean_alpha"] <= spec["alpha_max"],
                 f"{label}: mean alpha {got['mean_alpha']} > {spec['alpha_max']}")
    return fails


def load_expect(value):
    p = Path(value)
    data = json.loads(p.read_text()) if p.is_file() else json.loads(value)
    return data.get("expect", data)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--preview", help="write a PNG preview (max side 1024) to look at")
    ap.add_argument("--region", action="append", default=[], help="x,y,w,h in document pixels")
    ap.add_argument("--expect", help="JSON assertions, a JSON file, or a recipe with 'expect'")
    ap.add_argument("--cli", help="path to photocraft-cli")
    a = ap.parse_args()
    expect = load_expect(a.expect) if a.expect else {}
    regions = [tuple(r["region"]) for r in expect.get("regions", [])]  # first: check() zips them
    regions += [tuple(map(float, r.split(","))) for r in a.region]
    try:
        facts = analyze(a.image, regions, a.preview, a.cli)
    except PhotoCraftError as e:
        sys.exit(f"error: {e}")
    print(json.dumps(facts, indent=1))
    fails = check(facts, expect)
    for f in fails:
        print("FAIL", f, file=sys.stderr)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
