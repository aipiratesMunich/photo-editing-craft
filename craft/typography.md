# Typography

## Decide fast
- One message per layout. Decide which line is read first, second and third before choosing fonts.
- Two typefaces at most; one family with weights is often enough.
- Keep type live in the master. Rasterize only in output copies.
- Text over a photo must pass contrast: 4.5:1 for body text, 3:1 for large text (WCAG AA).
- Keep text inside the safe zone of every target the file feeds.

## Hierarchy

- Use size first, then weight, then color. Three levels cover most social and ad layouts: headline, support line, small print or call to action.
- Rule of thumb for size steps: each level 1.5 to 2 times the one below. Headline to body ratio of 3:1 or more on social graphics.
- Group related lines with tight spacing; separate groups with space at least twice the line gap.
- Align to one edge or one center axis per layout. Mixed alignments read as accidents.
- PhotoCraft: `type.create` for each line (`x`, `y`, `size`, `font`, `align`); `layer.align.leftEdges` / `layer.align.horizontalCenters` and `layer.distribute.vertically` for structure.

## Pairing

- Pair by contrast of role: a display or serif headline with a neutral sans for text, or one sans family in two weights.
- Avoid two fonts that are similar but different (two geometric sans). It looks like a mistake.
- Match x-heights roughly when fonts sit on the same line.
- Brand fonts override taste. If the brand font is missing, stop and say so. PhotoCraft: `type.fonts` to list, `type.resolveMissingFonts`, `type.replaceAllMissingFonts` only with approval.

## Tracking, kerning, leading

Rules of thumb. Tracking is in 1/1000 em (PhotoCraft and Photoshop use the same unit).

| Setting | Body text | Headlines | All caps | Small print |
|---|---|---|---|---|
| Tracking | 0 | -10 to -30 at large sizes | +50 to +100 | +10 to +25 |
| Leading | 120 to 145 % of size | 95 to 115 % | 100 to 120 % | 130 to 150 % |
| Kerning | metrics | optical, then fix pairs by hand | optical | metrics |

- German or other languages with umlauts in all-caps headlines: leading at least 102 % of size or diacritics collide with the line above.
- Hand-kern the obvious pairs at headline size: AV, To, Ty, LT, Wa, and around periods and quotes.
- PhotoCraft: `type.setStyle` with `tracking`, `leading`, `kerning` (`"metrics"`, `"optical"`, or a number with `range` for a pair), `caps`.

## Line length and text blocks

- Rule of thumb: 45 to 75 characters per line for reading text; 2 to 6 words per line for headlines on social graphics.
- Use paragraph text with a box for anything longer than a line. PhotoCraft: `type.create` with `box`; convert with `type.convertToParagraphText`.
- Avoid single words on the last line (widows) in headlines. Rebreak by hand.
- Left aligned for more than three lines. Justified only with good hyphenation and wide columns.
- Run a spell check before export. PhotoCraft: `edit.checkSpelling`; replace with `edit.findAndReplaceText`.

## Legibility over images

Order of preference:

1. Place text over a calm, even area of the photo (sky, wall, out-of-focus background). Crop or extend the canvas to create one.
2. Darken or lighten that area with a masked curves layer.
3. Scrim: a gradient fill from transparent to 40 to 70 % black (or white) behind the text. PhotoCraft: `layer.newFillLayer.gradient` with `from`, `to`, `angle`, then `layer.setProps` for opacity; place under the type layer.
4. Soft shadow: distance 0 to 2 px, size 8 to 20 px, opacity 30 to 60 % at 1080 px width (rule of thumb). PhotoCraft: `layer.layerStyle.dropShadow`. recipe: recipes/title-with-shadow.json
5. Solid box or band behind the text (`shape.create` or `layer.newFillLayer.solidColor` with a selection).

Avoid outlines and heavy glows for legibility. They look dated and thicken letterforms.

## Contrast for accessibility

- WCAG 2 contrast ratio from relative luminance: `(L1 + 0.05) / (L2 + 0.05)`, where L is computed from linearized sRGB channels.
- AA: 4.5:1 normal text, 3:1 large text (at least 24 px regular or about 19 px bold on screen). AAA: 7:1 and 4.5:1.
- Over a photo, take the background luminance as the worst case behind the letters, not the average of the image.
- PhotoCraft: measure the text color and the background region with `scripts/verify.py --region` (`mean_rgb`), or sample with `document.sampleColor` / `document.pixel`; compute the ratio.
- Do not rely on color alone for meaning (red price vs green price). Check with `view.proofSetup.colorBlindnessDeuteranopia` and `view.proofSetup.colorBlindnessProtanopia`.

## Social safe areas

- Platform UI covers the top and bottom of vertical formats and the corners of thumbnails. Specs change: check the current platform spec.
- Rule of thumb for 1080 x 1920: keep text and logos inside x 60 to 1020, y 250 to 1580.
- Rule of thumb for 4:5 feed posts: keep critical text inside the central 1:1 square too; grids and previews crop.
- Put the safe zone on guides in the master. PhotoCraft: `view.newGuideLayout` with `margin`, or `view.newGuide`.
- Minimum text size on a 1080 px wide social graphic, rule of thumb: 28 to 32 px for small print, 48 px or more for support lines.

## Live text and hand-off

- Keep each line or block as its own type layer, named after its content. PhotoCraft: `type.create` with `name`.
- Use character and paragraph styles when a layout has repeated levels. PhotoCraft: `type.characterStyle.new`, `type.paragraphStyle.new`, `type.characterStyle.apply`.
- Variable data (many versions with different text): `image.variables.define`, `image.variables.dataSets`, `file.export.dataSetsAsFiles`.
- PhotoCraft gaps: no type on a path; text features are behind Photoshop. For type on a path, set it in Photoshop or a vector tool and place the result as a smart object.
- Text image effects such as photo inside letters: recipe: recipes/image-inside-text.json. Watermark: recipe: recipes/watermark.json.
- Print: small text in 100 % K, not rich black. See craft/output-print.md.

## Check before done
- `scripts/verify.py master.pcraft --expect '{"layer_kinds":["Type"]}'`: type is live in the master.
- Contrast ratio computed for each text block against the worst background region; at least 4.5:1 (3:1 large).
- Text region readable: `regions` with `mean_luma_between` on the text box (pattern in recipes/title-with-shadow.json).
- All text sits inside the safe zone guides of every target.
- Spelling checked; brand fonts in use, no substitutes (`type.info` on each layer).
