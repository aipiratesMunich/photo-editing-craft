# Compositing

## Decide fast
- Before cutting anything, check that light direction, camera height and lens perspective of the plates agree. If they do not, find another plate.
- Match in this order: perspective and scale, light direction, black and white points, color, contrast, sharpness and grain.
- Every inserted object needs a contact shadow. A cast shadow when the light is directional.
- Place plates as smart objects; correct each with clipped adjustment layers.

## Plate check before building

| Factor | How to read it | Tolerance (rule of thumb) |
|---|---|---|
| Light direction | where highlights and shadows fall on faces, edges, ground | within about 30 degrees horizontally |
| Light quality | hard (crisp shadows) vs soft (diffuse) | must match; hard into soft never sells |
| Camera height | where the horizon line crosses the subjects | same horizon height across plates |
| Lens | wide (strong convergence, stretched corners) vs long (flat) | similar focal length class |
| Depth of field | what is sharp at which distance | the insert's blur matches its distance |
| Resolution and noise | pixel detail at 100 % | the insert is not softer or cleaner than the plate |

Flipping a plate horizontally fixes a mirrored light direction, if no text or asymmetric detail gives it away. PhotoCraft: `edit.transform.flipHorizontal`.

## Perspective and horizon

- Draw the horizon line on a guide. Eyes of standing people shot from standing height sit on it, at any distance.
- Scale inserts so their size fits their distance on the ground plane. Feet of people at the same depth share a line.
- Use perspective warp on the insert to match converging lines. PhotoCraft: `layer.smartObjects.perspectiveWarp` (or `edit.perspectiveWarp`); scale with `edit.transform`.
- Vanishing point for planes (signs on walls, floor textures): `filter.vanishingPoint`.
- Guides: `view.newGuide` for horizon and vanishing lines.

## Matching color, contrast and grain

1. Black point: find the darkest point in each plate and match the insert's black to the background's. PhotoCraft: Levels or Curves clipped to the insert: `layer.newAdjustmentLayer.curves`, then `layer.createClippingMask`.
2. White point: match the brightest non-specular highlight the same way.
3. Color: compare a neutral or a midtone in both (sample average). Shift the insert with clipped curves per channel or Color Balance. PhotoCraft: `layer.newAdjustmentLayer.colorBalance` clipped.
4. Saturation: inserts often look too clean. Pull saturation 5 to 15 % with a clipped Hue/Saturation layer.
5. Atmosphere: distant objects get lower contrast and take on the haze color. A clipped solid fill of the haze color at 5 to 30 % does this.
6. Sharpness: blur the insert to the plate's depth of field. PhotoCraft: `filter.blur.gaussianBlur` or `filter.blur.lensBlur` as a smart filter.
7. Grain: add noise to the insert until 100 % crops look alike. PhotoCraft: `filter.noise.addNoise` (`monochromatic`, `gaussian`), or one grain layer over the whole image.
8. Color Match as a starting point: `image.adjustments.matchColor` on a copy, then mask.

A quick check trick: add a temporary Black & White layer at the top. Tone mismatches show more clearly without color. Delete it after.

## Shadows

- Contact shadow: dark, small, almost sharp, where the object touches the ground. Paint black on a new layer under the object, blend Multiply, 40 to 80 % opacity, then blur 2 to 6 px. PhotoCraft: `layer.new.layer`, `paint.stroke`, `layer.setProps` `"blend":"Multiply"`, `filter.blur.gaussianBlur`.
- Cast shadow: copy the object's silhouette, fill black, distort it along the light direction onto the ground plane, blend Multiply. It gets softer and lighter with distance: mask with a gradient. PhotoCraft: `layer.duplicate`, `edit.fill` with `"preserveTransparency":true`, `edit.transform`, `layer.newFillLayer.gradient` or gradient on the mask.
- Shadow color: never pure black on colored ground. Sample the darkest ground shadow color in the plate.
- Shadow density matches the plate's existing shadows: measure luma of an existing shadow and of yours.
- recipe: recipes/replace-background.json (cutout plus new background; add a contact shadow by hand).

## Edge blending

- Feather masks by 0.5 to 2 px for objects at the focus distance; more for out-of-focus objects.
- Light wrap: background light spilling around a backlit edge. Blur a copy of the background, clip it to the subject, mask it to a thin edge band, blend Screen at low opacity.
- Remove fringes: see craft/selection-and-masking.md (decontaminate, defringe, matte removal).
- Blend If hides the insert's darks or lights against the plate (smoke, clouds, fire). Split the sliders for soft transitions. PhotoCraft: `layer.layerStyle.blendingOptions` with `blendIf`.
- Auto Blend Layers merges overlapping exposures or panorama seams. PhotoCraft: `edit.autoAlignLayers`, `edit.autoBlendLayers`.

## Blend mode table

| Mode | Effect | Typical use |
|---|---|---|
| Normal | covers | plates, cutouts |
| Multiply | darkens, white disappears | shadows, ink textures, line art |
| Screen | lightens, black disappears | light leaks, fire, glow, light wrap |
| Overlay / Soft Light | contrast, 50 % gray disappears | dodge and burn layers, texture, high pass |
| Linear Light | strong contrast | frequency separation high layer |
| Color | hue and saturation from layer, luma from below | recolor, color fringes |
| Luminosity | luma from layer, color from below | contrast curves without saturation shift, sharpening |
| Darken / Lighten | keeps darker or lighter pixel | stacking stars, removing a white or black background from an element |
| Difference | shows differences | aligning two layers (black means aligned) |

PhotoCraft: `layer.setProps` with `"blend":"<Mode>"`, `opacity` and `fill` (fill opacity leaves layer styles at full strength).

## Smart objects and smart filters

- Place every external plate as a smart object: scale and warp without loss, filters stay editable. PhotoCraft: `file.placeEmbedded` or `file.placeLinked`; existing layers via `layer.smartObjects.convertToSmartObject`.
- Linked smart objects keep a shared source in sync across files (logo, product shot). Update with `layer.smartObjects.updateAllModifiedContent`.
- Swap a plate while keeping its transform and filters: `layer.smartObjects.replaceContents`.
- Smart filters: tune with `layer.smartFilter.setParams`, hide with `layer.smartFilter.setVisible`, mask with the filter mask.
- Rasterize only on output copies: `layer.smartObjects.rasterize`.

PhotoCraft has no Sky Replacement, Generative Fill or Generative Expand. Sky swaps are manual: `select.sky` or a channel mask, place the new sky below, then match color and edge haze as above.

## Check before done
- Black and white points of insert and plate within about 10 levels: measure both regions with `scripts/verify.py --region` and compare `mean_luma` of the darkest and brightest patches.
- Neutral or matching midtone areas agree: `regions` with `mean_rgb_near` against the plate's value, tolerance about 10.
- Contact shadow exists under every grounded object (named layer in the layer tree).
- Grain matches at 100 %: region `luma_std` on a flat patch of insert and plate within about 20 %.
- Plates are smart objects with clipped corrections; `layers_min` and the layer tree confirm structure.
- Black-and-white check layer removed.
