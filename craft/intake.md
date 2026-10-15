# Intake: settle the brief before touching pixels

## Decide fast
- No edit starts until medium, final pixel size (or mm at ppi), color space and formats are written down.
- Unknown spec: ask once, then fall back to the defaults in the table below and say which you assumed.
- Rights unclear for any source image: stop and ask. Do not "fix it later".
- Layered master is the default. Skip it only for one-off throwaway exports the client said they will never revise.

## The eight questions

Ask these in one message, not one at a time. Write the answers into the job notes or the recipe vars.

| # | Question | Why it matters | If nobody answers |
|---|---|---|---|
| 1 | Where will it appear? (screen, print, both) | Decides color space, sharpening, resolution | Screen, sRGB |
| 2 | Final size? px for screen, mm plus ppi for print | Decides crop, resample, type size | Largest listed target |
| 3 | Bleed and safe zone? | Print trims; platforms overlay UI | 3 mm bleed, 5 mm safe for print |
| 4 | Color space and printer profile? | CMYK conversion needs the press profile | Keep RGB master; generic CMYK only on request |
| 5 | Deliverable formats and file size limits? | JPEG vs PNG vs WebP, PDF, TIFF | JPEG for photos, PNG for flat graphics |
| 6 | Layered master needed? Which format? | Client revisions, handover to Photoshop users | `.pcraft` plus `.psd` |
| 7 | Brand constraints? (fonts, colors as hex/CMYK/Pantone, logo clear space) | Wrong brand blue is a reject | Ask; never guess brand values |
| 8 | Rights and releases for every source? | Licence scope, model and property releases | Stop until confirmed |

## Source check

Inspect every source before planning edits.

- Pixel size vs target. Rule of thumb: upscaling beyond 150 % shows; beyond 200 % is a reshoot or a different image. PhotoCraft has no ML upscaler.
- Embedded profile. A missing or odd profile (wide gamut camera export, CMYK stock) changes how numbers read. PhotoCraft: `edit.profileInfo`, `edit.assignProfile` only when the profile is missing or wrong, never to "fix" color.
- Bit depth. Heavy tone work on 8-bit skies bands. PhotoCraft: `image.mode.bits16` before big curves, back to `image.mode.bits8` at export.
- Noise, compression artefacts, motion blur. These cap how far you can push contrast and sharpening.
- Metadata: author, copyright, camera. PhotoCraft: `file.fileInfo` with no keys reads it.

## Rights and ethics

- Stock: check licence tier (editorial vs commercial). Editorial-only images cannot sell a product.
- People: commercial use needs a model release. Minors need guardian consent.
- Logos, artworks, buildings in frame: property release or crop them out.
- Documentary or news image: only global tone and color, crop, dust removal. See craft/retouching.md.
- AI-generated or AI-edited sources: ask whether the client must disclose it.

## Common targets

Specs on social platforms move. Rule: check the current platform spec before delivery and treat this table as a starting point.

| Target | Pixels / size | Ratio | Color | Format | Notes |
|---|---|---|---|---|---|
| Instagram feed portrait | 1080 x 1350 | 4:5 | sRGB | JPEG | check current platform spec; recipe: recipes/social-export-4x5.json |
| Instagram / TikTok story, reel cover | 1080 x 1920 | 9:16 | sRGB | JPEG | keep text out of top ~250 px and bottom ~340 px; check current platform spec |
| Square post | 1080 x 1080 | 1:1 | sRGB | JPEG | grid previews may crop to 4:5 or 3:4; check current platform spec |
| LinkedIn / X link image | 1200 x 627 or 1200 x 675 | ~1.91:1 / 16:9 | sRGB | JPEG/PNG | check current platform spec |
| YouTube thumbnail | 1280 x 720 | 16:9 | sRGB | JPEG | bottom-right timestamp covers a corner |
| Web hero, full width | 2560 x 1440 (2x of 1280) or 1920 x 1080 | 16:9 or wider | sRGB | WebP + JPEG fallback | design for a center crop on mobile |
| Email header | 1200 x 400 to 600 (2x of 600 wide) | ~3:1 | sRGB | JPEG/PNG | many clients block images; never put the only copy of key text in the image |
| A4 print | 210 x 297 mm, file 216 x 303 mm with 3 mm bleed; 2551 x 3579 px at 300 ppi | 1:1.414 | printer CMYK or RGB per printer | PDF/X or TIFF | recipe: recipes/print-prep-cmyk.json |
| A5 print | 148 x 210 mm, file 154 x 216 mm with 3 mm bleed; 1819 x 2551 px at 300 ppi | 1:1.414 | as A4 | PDF/X or TIFF | |
| Poster A2 / A1 | 420 x 594 / 594 x 841 mm plus bleed | 1:1.414 | as A4 | PDF/X or TIFF | 150 to 200 ppi is enough at viewing distance over 1 m (rule of thumb) |

mm to px: `px = mm / 25.4 * ppi`. 300 ppi gives 11.81 px per mm.

## Turning the brief into a document

- Set the canvas to the full trim plus bleed, at final ppi. PhotoCraft: `file.new` or `image.canvasSize` on an existing image; `image.imageSize` with `"resample":"none"` to change ppi only.
- Mark trim, bleed and safe zone with guides. PhotoCraft: `view.newGuide`, `view.newGuideLayout` with `margin`.
- Store brand colors as swatches so every layer uses the same values. PhotoCraft: `swatches.add`, `swatches.use`.
- Note the brief in the file. PhotoCraft: `file.fileInfo` with `description`; `notes.add` for review notes.

## Brand constraints

- Get brand colors as numbers (hex for screen, CMYK and spot for print). Eyedropping a logo JPEG gives wrong values.
- Get the font files or names. A substitute font is a reject; if the font is missing, say so before setting type. PhotoCraft: `type.fonts`, `type.resolveMissingFonts`.
- Logo clear space and minimum size come from the brand guide. Measure them, do not eyeball.
- Do not recolor, stretch, shadow or outline a logo unless the guide allows it.

## Check before done
- Brief written down: medium, size, ppi, color space, bleed, formats, master format, brand values, rights status.
- `scripts/verify.py master.pcraft --expect '{"width":W,"height":H,"resolution":PPI}'` matches the trim plus bleed math.
- Source upscale factor stated; anything over 150 % flagged to the human.
- Every source image has a known licence and, where people appear, a release.
- Every assumption made without an answer is listed in the hand-off message.
