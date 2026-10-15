# Retouching

## Decide fast
- Work on an empty layer above the image, sampling all layers. The original stays untouched.
- Pick the tool by defect and by what surrounds it (see table). Smallest tool that works.
- Keep texture. A retouch that removes pores, grain or fabric weave reads fake at 100 %.
- Documentary and news: dust and sensor spots only. Nothing that changes what happened.
- Review at 100 % and at final display size. Both lie in different ways.

## Tool choice by defect

| Defect | Surroundings | Tool | PhotoCraft |
|---|---|---|---|
| Dust, small spot, pimple | even texture | Spot Healing | `paint.spotHealing`; recipe: recipes/remove-spots.json |
| Spot near an edge or a pattern | edge or structure close by | Clone Stamp, hard edge, sample aligned | `cloneSource.set`, `paint.cloneStamp` |
| Wrinkle, crease, scar | skin, cloth | Healing Brush with a chosen source | `paint.healingBrush` |
| Larger area, even texture (wall, sky) | | Patch | `paint.patch` |
| Object to remove, varied background | | Remove tool or Content-Aware Fill, then clean with clone | `paint.remove`, `edit.contentAwareFill` |
| Move an object a little | | Content-Aware Move | `paint.contentAwareMove` |
| Red eye | | Red Eye | `paint.redEye` |
| Stray hair across a face | | Healing Brush in short strokes along the hair, clone near eyes | `paint.healingBrush`, `paint.cloneStamp` |
| Noise or JPEG blocks | whole image | Reduce Noise on a smart object, masked | `filter.noise.reduceNoise`, `filter.noise.dustAndScratches` |
| Shape (bulges, bent lines) | | Liquify on a smart object, small moves | `filter.liquify` |
| Uneven skin color, blotches | | Curves or Hue/Saturation layer masked to the area | `layer.newAdjustmentLayer.hueSaturation` |

PhotoCraft has no ML Generative Fill. `paint.remove` and `edit.contentAwareFill` use patch-based completion: good on texture, weak on structured scenes (faces, text, perspective lines). Rebuild structure with clone and transform in those cases.

## Working setup

1. Empty retouch layer: `layer.new.layer` with `name`, then `layer.select` it. Heal, clone and spot-heal with sample all layers.
2. One retouch layer per kind of work (`Retouch dust`, `Retouch skin`, `Remove sign`) so each can be reduced or deleted.
3. Brush size rule of thumb: 1.5 to 2 times the defect. Hardness 50 to 80 % for healing; 80 to 100 % for clone near edges.
4. One click per spot. In PhotoCraft a `points` list is one connected stroke; send separate commands per spot (`for_each` in recipes).
5. Sample from the same tonal zone and the same distance from the light. Wrong-source heals look gray or smeared.

## Texture preservation

- Healing blends tone and keeps source texture; clone copies both. Use healing where tone differs, clone where structure matters.
- Clone at 100 % opacity, then lower the layer opacity if needed. Low-opacity brush strokes stacked many times blur texture.
- For skin, keep pores. If an area gets smooth, add matching noise on that layer: `filter.noise.addNoise` with `monochromatic`, about 1 to 3 % (rule of thumb), masked to the area.
- Film or sensor grain over the whole image hides small retouch differences. Add it last, globally.

## Frequency separation (advanced)

Use for even skin tone or fabric where texture must stay and color blotches must go. Overkill for spot removal.

1. Duplicate the image twice. Lower copy: `Low`, upper: `High`.
2. Low: Gaussian Blur until pores vanish and only color and shading remain (rule of thumb 4 to 10 px at 24 MP for faces). PhotoCraft: `filter.blur.gaussianBlur`.
3. High: in 8-bit, Apply Image from Low with Subtract, scale 2, offset 128; in 16-bit, Add with Invert, scale 2, offset 0. Blend High as Linear Light. PhotoCraft: `image.applyImage` with `source`, `blending`, `scale`, `offset`; `layer.setProps` `"blend":"Linear Light"`. Tested in PhotoCraft: Low plus High in Linear Light rebuilds the original within 2 levels of 255.
4. Group both. The composite should match the original exactly; check before retouching.
5. Smooth color on Low with a soft brush or a mixer brush at low flow (`paint.mixerBrush`). Heal texture defects on High only.
6. Keep changes on Low subtle. Too much flattens shape, which is the plastic look.

Simpler alternative that often suffices: a masked Surface Blur layer at 20 to 40 % opacity (`filter.blur.surfaceBlur`).

## Failure smells

| Smell | Cause | Fix |
|---|---|---|
| Repeated patches, same cloud twice | clone from one source spot | sample from several places; flip or rotate the source (`cloneSource.set`, `cloneSource.resetTransform`) |
| Smears, gray halos at edges | healing too close to a contrasting edge | clone with a hard brush near edges; heal only in open areas |
| Plastic skin | blur or low-frequency smoothing too strong | lower opacity, add grain, keep lines that belong to the face |
| Mismatched grain | patch from a blurred or resized source | add noise to match; heal from same-size areas |
| Missing anatomy | removed a mole, line or freckle the person is known for | ask; identity marks stay by default |
| Wrong perspective in rebuilt areas | content-aware on lines | clone with transform, or rebuild with a transformed copy |
| Tonal step at the patch border | source from a different light zone | sample closer, or fix with a masked curves layer |

## Ethics

- News and documentary: allowed are crop (without changing meaning), global tone and color within what the scene showed, dust and sensor spot removal. Not allowed: adding, removing or moving content, compositing, changing faces or bodies.
- Advertising with people: body and face reshaping may be regulated in some markets and may require labels. Ask the human what applies.
- Before/after: keep the untouched original so edits can be shown on request.
- Record what was done in `file.fileInfo` `description` or `notes.add` when the image will be used editorially.

## Check before done
- Retouch work is on separate named layers: `scripts/verify.py master.pcraft` shows them above an untouched Background.
- Each treated defect region measured: `regions` with `mean_luma_between` matching the surroundings (the recipe recipes/remove-spots.json shows the pattern).
- Texture check: region `luma_std` of a retouched skin patch within about 20 % of an untouched patch nearby.
- No visible repeats at 100 % (render a crop: `render_preview` on the region).
- For editorial images: only permitted operations used, and they are noted.
