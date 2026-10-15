# Output for screens and the web

## Decide fast
- Output from the master, on a copy: resize, then sharpen once, then convert to sRGB, then export.
- Photos: JPEG or WebP. Flat graphics, UI, text-heavy images, transparency: PNG or lossless WebP.
- Ship 2x pixels for anything shown sharp on high-density screens, and keep the file inside its size budget.
- Strip camera and location metadata; keep copyright if the client wants it.

## Resampling

| Method | Use | PhotoCraft `resample` |
|---|---|---|
| Bicubic Sharper | downsizing photos (may need less output sharpening) | `bicubicSharper` |
| Bicubic Smoother | upsizing, modest factors | `bicubicSmoother` |
| Lanczos | downsizing with fine detail, little ringing at moderate factors | `lanczos` |
| Preserve Details | upsizing with edge preservation (classical, not ML) | `preserveDetails` |
| Nearest neighbor | pixel art, screenshots at integer factors, hard-edged graphics | `nearest` |
| None | change ppi only, pixel count unchanged | `none` |

- Downsize in one step from the master. Repeated resizes add softness.
- Large downsizes (more than 4x): a light blur before the resize reduces moiré on fine patterns (rule of thumb 0.3 to 0.5 px per factor of 4).
- Upsizing beyond 150 % shows. PhotoCraft has no ML upscale. Ask for a larger source first.
- PhotoCraft: `image.imageSize` with `width`, `height`, `resample`. Crop to the ratio first with `image.crop`. recipe: recipes/resize-for-web.json

## Output sharpening by medium

Rules of thumb. Sharpen once, after the final resize, on a flattened copy or a stamped layer.

| Output | Unsharp Mask amount | Radius | Threshold |
|---|---|---|---|
| Web photo at 1x | 40 to 80 % | 0.3 to 0.6 px | 0 to 2 |
| Web photo at 2x | 30 to 60 % | 0.5 to 0.8 px | 0 to 2 |
| Social feed 1080 px | 50 to 90 % | 0.4 to 0.7 px | 0 to 2 |
| Portraits, skin | lower end; mask skin out | 0.4 to 0.6 px | 2 to 4 |
| Graphics, text, UI | none | | |

- Platforms recompress uploads; a touch of extra sharpening survives that, too much turns into halos.
- Sharpen luminance only to avoid color halos: set the sharpened layer to Luminosity. PhotoCraft: `layer.stampVisible`, `filter.sharpen.unsharpMask`, `layer.setProps` with `"blend":"Luminosity"`.
- Smart Sharpen for noisy sources: `filter.sharpen.smartSharpen` with `reduceNoise`.
- High Pass at 0.5 to 1.5 px in Overlay is an alternative that is easy to mask: `filter.other.highPass`.

## sRGB conversion and embedding

- Convert, do not assign. Convert keeps the look and changes the numbers; assign keeps numbers and changes the look. PhotoCraft: `edit.convertToProfile` with `"profile":"srgb"`, `"intent":"relative"` or `"perceptual"` for wide-gamut sources.
- Embed the sRGB profile, or at least ensure untagged output was converted to sRGB. Untagged non-sRGB files look dull or oversaturated in browsers.
- Display P3 is fine for sites that serve it deliberately; keep an sRGB fallback.
- Export dialogs that convert to sRGB on the way out: PhotoCraft `file.export.saveForWebLegacy` (`convertToSrgb`, `embedIcc`), `file.export.exportPreferences` (`convertToSrgb`).

## Format choice

| Format | Use | Notes | PhotoCraft |
|---|---|---|---|
| JPEG | photos, no transparency | quality 70 to 85 % for web (PhotoCraft `file.saveACopy` uses a 0..12 JPEG scale; rule of thumb 8 to 10; `photocraft-cli convert --quality` takes 1..100); progressive for large images | `doc_export` to `.jpg`, `file.saveACopy` with `quality`, `file.export.saveForWebLegacy` `"format":"jpeg"` |
| PNG-24/32 | graphics, text, screenshots, transparency | lossless, large for photos | `doc_export` to `.png`, `layer.quickExportAsPng` |
| PNG-8 | flat graphics with few colors | palette and dither choice matter | `file.export.saveForWebLegacy` `"format":"png8"` |
| WebP | photos and graphics where supported; smaller than JPEG at equal quality | lossy quality 75 to 85, or lossless | `doc_export` to `.webp`; `file.export.exportPreferences` `webpQuality`, `webpLossless` |
| AVIF | smallest photos for modern browsers | missing in PhotoCraft; export PNG or 16-bit TIFF and encode with an external encoder (avifenc, squoosh, sharp) | missing |
| GIF | simple animation only | 256 colors | `file.export.saveForWebLegacy` `"format":"gif"` |
| SVG | logos, icons | vector; raster editors are the wrong tool | missing; use a vector app |

## File size targets

Rules of thumb; check the site's performance budget.

| Asset | Target |
|---|---|
| Full-width hero (2x) | 150 to 400 KB |
| Content image | 50 to 200 KB |
| Thumbnail | 10 to 40 KB |
| Email header | under 200 KB; whole email images under 1 MB |
| Social upload | platform limits are large; quality matters more than size |

Over budget: lower quality in small steps (5 points), check flat areas and skin for blocks, then reduce pixel size before going below about 65 %.

## Metadata stripping

- Remove GPS, camera serials and editing history from public images unless the client wants them.
- Keep copyright and creator fields when the brief asks.
- PhotoCraft: `file.export.saveForWebLegacy` with `"metadata":"none"` or `"copyright"`; `file.export.exportPreferences` with `metadata`. Set fields beforehand with `file.fileInfo`.
- Generated assets: also strip C2PA, XMP and EXIF if the brief requires it, with an external tool (`exiftool -all=`). Check whether the client must disclose AI use before stripping provenance.

## 2x assets

- Export at twice the CSS pixel size (a 600 px wide slot gets a 1200 px file). Name `name@2x.jpg` if the site uses that convention.
- For responsive images, export a width ladder: 640, 960, 1280, 1920, 2560 (rule of thumb).
- Thin lines and small text: design at 1x on a pixel grid, check that the 2x is crisp and that the 1x does not fall between pixels.
- PhotoCraft: `layer.exportAs` with `scale`, `file.generate.imageAssets`, `file.export.layersToFiles`, `file.export.artboardsToFiles`.

## Batch processing

- Same steps for many files: record the steps once, run on a folder. PhotoCraft: `file.automate.batch` with `steps`, `input`, `output`, `format`, `quality`.
- Resize and convert only: `file.scripts.imageProcessor` (`width`, `height` fit without enlarging, `convertToSrgb`, `format`, `quality`).
- Recorded actions: `actions.record`, `actions.stop`, `actions.play`; droplets: `file.automate.createDroplet`.
- Recipes with layer references need `scripts/run_recipe.py` in a loop, not CLI batch (see recipes/watermark.json notes).
- Spot-check at least the first, the last and the smallest file of every batch.

## Check before done
- `scripts/verify.py out.jpg --expect '{"width":W,"height":H}'` matches each target.
- Color: output converted to sRGB (`edit.profileInfo` on the exported copy, or the export option set).
- Sharpening applied once; `render_preview` at 100 % shows no halos on edges or skin.
- File size within budget (`ls -l`), quality set, metadata level as briefed.
- Clipping did not appear from resizing or sharpening: `"clipped_max":1` unless the master already had it.
- Batch: count of output files equals inputs; `errors` from the batch result is empty.
