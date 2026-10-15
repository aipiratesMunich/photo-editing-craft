# Color and tone

## Decide fast
- Fix tone before color: black point, white point, then midtone contrast.
- Find something that should be neutral (gray, white, concrete, paper) and measure it. Equal R, G, B there means no cast.
- Curves for anything beyond endpoints; Levels only for quick endpoints and gamma.
- Vibrance before Saturation. Skin is the first thing that breaks.
- Judge by numbers first, then by eye on a calibrated screen. A screenshot is not proof of neutral.

## Reading the histogram

| Shape | Meaning | Action |
|---|---|---|
| Bunched in the middle, gaps at both ends | flat, hazy | set endpoints, then an S-curve |
| Spike at the right wall | blown highlights | recover in raw if possible; pixels at 255 hold no detail |
| Spike at the left wall | crushed shadows | lift with a curve if detail exists; else accept |
| Combing (gaps, teeth) | prior heavy edits in 8-bit | work in 16-bit, use fewer stacked moves |
| Channels offset from each other | color cast | see Cast removal |

A low-key or high-key image is not wrong because the histogram sits to one side. Decide from the subject, not from the graph.

PhotoCraft: no histogram panel command; measure with `scripts/verify.py` (`mean_luma`, `luma_std`, `clipped_shadows_pct`, `clipped_highlights_pct`) and `image.analysis.info` or `document.pixel` at points.

## Neutral references

- Best: gray card or color checker in frame. Next: white paper, gray concrete, a white shirt in shade, chrome without colored reflections.
- Pick a midtone neutral (luma 100 to 200). Highlights clip and shadows are noisy.
- Place color samplers on 2 or 3 neutrals and keep them while you work. PhotoCraft: `view.colorSamplers.add`, `view.colorSamplers.list`.
- A neutral should read R = G = B within about 3 to 6 levels in 8-bit (rule of thumb).

## Levels vs curves

- Levels: black point, white point, one gamma. Fast and safe. PhotoCraft: `layer.newAdjustmentLayer.levels`.
- Curves: any number of points, per channel, targeted ranges. PhotoCraft: `layer.newAdjustmentLayer.curves` with `points`; `eyedropper` for gray/black/white point.
- Set endpoints just inside where the histogram starts and ends. Rule of thumb: darkest important shadow at 10 to 20, brightest detailed highlight at 240 to 248; specular highlights may go to 255.
- Auto Tone or Auto Contrast are fine as a first guess on a duplicate. PhotoCraft: `image.autoTone`, `image.autoContrast` (destructive; apply to a copy).

## Contrast

- S-curve: lower the quarter tone, raise the three-quarter tone, pin the midpoint. recipe: recipes/add-contrast-curve.json
- Curves raise saturation along with contrast. If colors get loud, set the curves layer blend to Luminosity. PhotoCraft: `layer.setProps` with `"blend":"Luminosity"`.
- Local contrast (clarity) on a smart object: High Pass on a copy set to Overlay or Soft Light, radius 20 to 60 px at 24 MP (rule of thumb). PhotoCraft: `filter.other.highPass`.
- Rule of thumb for luma std (0 to 255 scale): under 35 reads flat, 45 to 70 is typical for punchy photos, over 80 is graphic.
- Shadows/Highlights rescues backlit faces but halos at high amounts. PhotoCraft: `image.adjustments.shadowsHighlights` (no adjustment-layer version; use it on a smart object copy).

## Cast removal

1. Measure a neutral. The highest channel is the cast (high B = blue cast, high R and G = yellow).
2. Curves gray eyedropper on the neutral. recipe: recipes/fix-color-cast.json. PhotoCraft: `layer.newAdjustmentLayer.curves` with `"eyedropper":{"point":"gray","at":[x,y]}`.
3. No neutral: per-channel curves by eye, or Color Balance in midtones. PhotoCraft: `layer.newAdjustmentLayer.colorBalance`.
4. Mixed light (window plus tungsten): correct for the main subject, then mask a second correction for the other area.
5. Keep intentional warmth (sunset, candlelight). Neutralize, then add back 20 to 40 % warmth by lowering the correction layer opacity.

Photo Filter suits a global warm or cool shift. PhotoCraft: `layer.newAdjustmentLayer.photoFilter`.

## Saturation vs vibrance

- Vibrance raises muted colors more than saturated ones and protects skin. recipe: recipes/natural-saturation.json. PhotoCraft: `layer.newAdjustmentLayer.vibrance`.
- Saturation is uniform. Use it per range (reds, blues) in Hue/Saturation for targeted fixes. PhotoCraft: `layer.newAdjustmentLayer.hueSaturation` with `reds`, `blues`.
- Rule of thumb: vibrance +15 to +35, saturation within plus or minus 10 for natural work.
- Measure with `mean_chroma` before and after. A jump above about 1.5 times the start value usually reads overdone.

## Skin tones

- Healthy skin in RGB: R > G > B. Rule of thumb for light to medium skin: G about 75 to 85 % of R, B about 60 to 75 % of R. Darker skin keeps the same order with lower values and often slightly more B relative to G.
- In CMYK readings: yellow a little higher than magenta, cyan about a quarter to a third of magenta for light skin.
- Too red: lower reds saturation or shift reds hue toward yellow by a few degrees. Too green or gray: add magenta in midtones.
- Sample a lit cheek or forehead, not a highlight or a shadow. Use a 5 x 5 or larger average.

## Local dodge and burn

- Curves layer brightened (dodge) and one darkened (burn), both with black masks; paint white at low flow (2 to 10 %). PhotoCraft: two `layer.newAdjustmentLayer.curves`, then `layer.layerMask.hideAll` and paint the mask with `paint.stroke` and `"target":"mask"`.
- Alternative: 50 % gray layer in Soft Light, `paint.dodge` and `paint.burn` on it (`range`, `exposure`, `protectTones`). PhotoCraft: `layer.new.layer`, `edit.fill` with `"contents":"gray"`, `layer.setProps` `"blend":"Soft Light"`.
- Guide the eye: brighten the subject, darken edges and distractions. recipe: recipes/vignette.json
- Check by toggling the layers: the change should be visible only when switched off.

## Black and white

- Convert with control over color mapping. recipe: recipes/black-and-white.json. PhotoCraft: `layer.newAdjustmentLayer.blackWhite`.
- Darker blues for sky drama; brighter reds and yellows for skin. Avoid neighbouring colors that map to the same gray.
- Add a curves layer above for contrast. Channel Mixer in monochrome is an alternative. PhotoCraft: `layer.newAdjustmentLayer.channelMixer`.
- Toning: Gradient Map at low opacity or a split tone. PhotoCraft: `layer.newAdjustmentLayer.gradientMap`.
- Delivering grayscale: keep the master RGB, convert copies. PhotoCraft: `image.mode.grayscale` on a duplicate.

## Grading

- Grade after correction, on top, in its own group so it can be dialed down.
- Split tone with Curves: lift blue in shadows, lower blue in highlights (warm highlights, cool shadows). Keep skin out with a mask or Blend If. PhotoCraft: `layer.layerStyle.blendingOptions` with `blendIf`.
- LUTs: PhotoCraft `layer.newAdjustmentLayer.colorLookup` (list options with `image.adjustments.colorLookup.list`). Lower opacity to 30 to 70 % (rule of thumb).
- Match a reference frame: PhotoCraft `image.adjustments.matchColor` (destructive; run on a copy and mask in).

## Check before done
- Neutral region measured: `scripts/verify.py out.pcraft --expect '{"regions":[{"region":[x,y,w,h],"max_channel_spread":6}]}'`.
- Clipping: `"clipped_max":1` unless the brief allows blown speculars or a deliberate crush.
- Contrast in range: `luma_std_min` / `luma_std_max` set for the intended look.
- Saturation sane: `mean_chroma_min` met, and before/after chroma ratio under about 1.5 unless stylized.
- Skin sample follows R > G > B (`mean_rgb_near` on a skin region).
- All moves are adjustment layers, named, and toggle cleanly.
