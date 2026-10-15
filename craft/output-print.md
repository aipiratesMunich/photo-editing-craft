# Output for print

## Decide fast
- Get the printer's spec sheet first: profile (or "send RGB"), total ink limit, bleed, file format, PDF standard.
- Keep the master in RGB. Make the CMYK version as a copy, after soft proofing with the printer's profile.
- 300 ppi at final size for offset and close viewing; less is fine for posters seen from a distance.
- PhotoCraft writes raster-only, single-page PDF. Anything needing live text, vectors or PDF/X goes through a layout app.

## Resolution (ppi)

| Use | ppi at final size (rule of thumb) |
|---|---|
| Offset, magazines, brochures, A4/A5 flyers | 300 |
| Fine art inkjet, photo books | 240 to 360 |
| Posters A2 and larger, viewed from 1 m or more | 150 to 200 |
| Roll-ups, banners, viewed from 3 m or more | 75 to 120 |
| Newsprint | 200 |

- Set ppi without resampling first to see the true print size: PhotoCraft `image.imageSize` with `"resample":"none"` and `resolution`. recipe: recipes/print-prep-cmyk.json
- Effective ppi below about 70 % of target: ask for a larger source or a smaller print size. Upsizing does not add detail.
- Print sharpening is stronger than screen sharpening because ink spreads (dot gain). Rule of thumb at 300 ppi: Unsharp Mask 100 to 200 %, radius 0.8 to 1.5 px. Judge at 50 % view, not 100 %. PhotoCraft: `filter.sharpen.unsharpMask` on a copy.

## Soft proofing

1. Set up the proof with the printer's profile. PhotoCraft: `view.proofSetup` with `profile` (path to the printer's `.icc`, or `coated-cmyk` as a generic fallback), `intent`, `bpc`, `simulatePaper`.
2. Toggle the proof. PhotoCraft: `view.proofColors`.
3. Turn on the gamut warning to see colors that will shift. PhotoCraft: `view.gamutWarning` (`threshold` in deltaE).
4. Fix in RGB on the master with proof-specific adjustment layers in a group named `Proof fixes`: lower saturation in the flagged range, shift hue slightly, or brighten deep saturated blues.
5. Proof with `simulatePaper` on: paper white and ink black look duller than the screen. That is the real print; do not push contrast to compensate beyond what the proof shows.

## Gamut handling

- Typical problems in CMYK: saturated RGB blues, purples, bright greens, neon oranges, deep reds.
- Select out-of-gamut areas directly: PhotoCraft `select.colorRange` with `"select":"outOfGamut"`, then a masked Hue/Saturation layer.
- Brand colors outside CMYK: use the brand's defined CMYK values or a spot color. Do not let the conversion pick. Spot channels: `channel.newSpot`.
- For digital or photo labs that want RGB, send RGB tagged with the profile they ask for (often sRGB or Adobe RGB).

## Rendering intents

| Intent | Behavior | Use |
|---|---|---|
| Relative colorimetric | in-gamut colors stay exact, out-of-gamut clip to the nearest | default for most photos and graphics; with black point compensation |
| Perceptual | compresses the whole gamut to fit | images with large areas out of gamut |
| Saturation | keeps vividness, shifts hue | charts and business graphics, rarely photos |
| Absolute colorimetric | simulates paper white | proofing one press on another |

Choose by proofing both relative and perceptual and keeping the one that looks closer. PhotoCraft: `intent` on `view.proofSetup`, `edit.convertToProfile`, `image.mode.cmyk`.

## When to convert to CMYK

- Convert when the printer asks for CMYK files and provides a profile.
- Do not convert when the printer wants RGB (many digital presses and photo labs), when the output also goes to screen, or when no profile is known.
- Convert once, at the end, on a copy. CMYK to RGB and back loses color.
- PhotoCraft: `image.duplicate`, then `image.mode.cmyk` with `profile` and `intent`, or `edit.convertToProfile` with a CMYK profile.
- Check after converting: no unexpected shifts in skin and brand colors; total ink within limit (see below).

## Rich black vs 100 K text

- Small text, thin lines and barcodes: 100 % K only (0/0/0/100). Rich black under small text shows color fringes when plates misregister.
- Large black areas and big headlines: rich black, a common choice is 60/40/40/100 (ask the printer). 100 K alone prints as a dark gray on large areas.
- Never 100/100/100/100 (400 %): it smears and will not dry.
- Black text should overprint so knock-outs do not leave white gaps. Set this in the layout app; PhotoCraft has no overprint control.
- Text in a raster image is no longer 100 K-only after conversion and gets rasterized at image ppi. Put body text in a layout app.

## Total ink limit

- Typical limits: coated offset 300 to 330 %, uncoated 260 to 300 %, newsprint 220 to 260 %. The printer's profile sets this when you convert with it.
- Measure the darkest areas after converting: sum C + M + Y + K. PhotoCraft: `image.analysis.info` or `document.sampleColor` at points; color samplers `view.colorSamplers.add` in a CMYK document.
- Over the limit: reconvert with the correct profile; do not fix numbers by hand except in small areas.

## Bleed and safe zone

- Bleed: extend background images and colors 3 mm past the trim on every side (some printers want 5 mm, large formats more).
- Safe zone: keep text and logos at least 3 to 5 mm inside the trim; 10 mm for perfect-bound books near the spine.
- Build the canvas as trim plus bleed. PhotoCraft: `image.canvasSize` (extend), then fill the extension with real image content, not a mirror of faces or text. `edit.contentAwareFill` or clone for the strip.
- Mark trim and safe zone with guides: `view.newGuide`, `view.newGuideLayout` with `margin`.
- Crop marks belong to the PDF export of a layout app. PhotoCraft does not add them.

## PDF/X basics

- PDF/X-1a: CMYK and spot only, flattened transparency. Oldest, safest for conservative printers.
- PDF/X-3: allows color-managed RGB with an output intent.
- PDF/X-4: keeps live transparency and layers; current default for many printers.
- All include an output intent (the press profile), fonts embedded, trim and bleed boxes.
- PhotoCraft cannot write PDF/X. Its PDF is raster-only and single page: no live text, no vectors, no trim box. Route: export a CMYK or RGB TIFF from PhotoCraft (`doc_export` to `.tif`, or `file.saveACopy`), place it in a layout app (InDesign, Affinity Publisher, Scribus), set type there, export PDF/X.
- PhotoCraft TIFF keeps layers only with `tiffLayers`; printers usually want flat TIFF.

## Check before done
- `scripts/verify.py print.tif --expect '{"width":W,"height":H,"resolution":300.0,"mode":"Cmyk"}'` (or `"Rgb"` if the printer wants RGB). Compute W and H from trim plus bleed: `mm / 25.4 * ppi`.
- Soft proof done with the printer's profile; gamut warning areas handled or accepted.
- Darkest area total ink within the printer's limit.
- Small text not in the raster, or set 100 K in the layout app.
- Bleed filled with image content on all sides; text inside the safe zone guides.
- RGB master saved separately; CMYK file is a copy.
- PDF/X made in a layout app when the printer requires it; PhotoCraft PDF only for raster proofs.
