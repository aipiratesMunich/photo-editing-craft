# Selection and masking

## Decide fast
- Choose the method by edge type, not by habit (table below).
- Output to a layer mask. Never erase pixels you might need back.
- Hair and fur need edge refinement and color decontamination; hard product edges need a path.
- Judge every mask on black, on white and as the mask itself before calling it done.

## Method by edge type

| Edge | Example | Method | PhotoCraft |
|---|---|---|---|
| Hard geometric | box, screen, building | Rectangle or polygon lasso; pen path for curves | `select.rect`, `select.lasso`, `path.set`, `path.toSelection` |
| Hard organic, clean background | product on white | Subject or Object select, then refine | `select.subject`, `select.object`; recipe: recipes/cutout-to-mask.json |
| Strong edge contrast, irregular | leaf, tool | Quick selection or magnetic lasso | `select.quick`, `select.magneticLasso` |
| Uniform color area | sky, studio wall | Magic wand or color range | `select.magicWand`, `select.colorRange` |
| Sky behind buildings or trees | | Sky select or a channel mask | `select.sky`, see Channels |
| Hair, fur, smoke | portrait | Subject select plus edge refine plus decontaminate | `select.subject`, `select.refineEdge` |
| Tonal range | highlights only, shadows only | Color range by tone, or a luminosity mask | `select.colorRange` with `"select":"highlights"` |
| In-focus subject | shallow depth of field | Focus area | `select.focusArea` |
| Glass, veils, transparency | | Channel-based mask, partial gray values | Channels section |

PhotoCraft `select.subject` is classical graph-cut segmentation, not ML. It works on clear contrast and fails on busy or similar-colored backgrounds. For those, combine methods: rough select, then subtract and add with `select.quick` or `select.colorRange`, or build a channel mask.

## Refining

- Edge radius: small (1 to 3 px) for hard products, larger (8 to 30 px with smart radius) for hair. PhotoCraft: `select.refineEdge` with `radius`, `smartRadius`.
- Shift edge negative (-10 to -30) to pull a halo of background off the subject.
- Smooth for jagged lasso edges; contrast for crisp product edges. Do not use both heavily on hair.
- Paint refine strokes over hair zones only. PhotoCraft: `select.refineEdge` with `refineStrokes` (mode `add`).
- Output to `layerMask` directly, or to selection followed by `layer.layerMask.revealSelection`.
- Modify commands for fixes: `select.modify.contract`, `select.modify.expand`, `select.modify.smooth`, `select.grow`, `select.similar`.

## Hair

1. Start from a mask that is solid inside and roughly right outside.
2. Refine with a wide radius around the hair, small radius on the body and clothing.
3. Decontaminate colors so the old background tint leaves the strands (next section).
4. Missing fine strands: paint a few with a 1 to 2 px brush sampled from real hair on a separate layer, or accept them lost. Do not paint a solid helmet.
5. New background that differs a lot in brightness from the old one shows every flaw. Choose a similar luminance when you can.

## Decontaminating color fringes

- Edge pixels hold a blend of subject and old background. On a new background they show as a colored halo.
- PhotoCraft: `select.refineEdge` with `"decontaminate":true` and `amount`, or after masking `layer.matting.colorDecontaminate` (`amount`, `radius`).
- Light halo from a white background: `layer.matting.removeWhiteMatte`. Dark halo: `layer.matting.removeBlackMatte`. Generic fringe: `layer.matting.defringe` (1 to 2 px).
- Manual route: a layer clipped to the subject, blend Color, paint the hair color over the fringe at low opacity.
- Decontamination writes into pixels. Keep the unmatted layer hidden below.

## Channels

- Pick the channel with the most contrast between subject and background (often blue for sky, red for skin against green).
- Duplicate it, push contrast with Levels or Curves until subject is black or white and background the opposite, paint the rest by hand, load as selection.
- PhotoCraft: `channel.list`, `channel.duplicate`, `channel.target`, `image.adjustments.levels` or `image.adjustments.curves` on the target channel, `select.loadSelection`.
- Calculations combine two channels for harder cases: `image.calculations`.
- Save complex selections so work is not lost: `select.saveSelection`, reload with `select.loadSelection`.

## Masks vs erasing

| Need | Use |
|---|---|
| Hide part of a pixel layer | layer mask (`layer.layerMask.revealSelection`, `layer.layerMask.hideSelection`, `layer.layerMask.hideAll`) |
| Crisp scalable edge (product, shape) | vector mask (`layer.vectorMask.fromPath`, `layer.vectorMask.currentPath`) |
| Limit a layer to the shape of the layer below | clipping mask (`layer.createClippingMask`) |
| Restrict an adjustment | select first, then create the adjustment layer: the selection becomes its mask |
| Restrict a smart filter | filter mask on the smart object |
| Remove pixels for good | only on an output copy; `layer.layerMask.apply` |

Clipping masks: one base layer defines visibility for every layer clipped above it. Use them for texture inside type, a correction that affects only one plate in a composite, or a color shift on one product. recipe: recipes/image-inside-text.json. Release with `layer.releaseClippingMask`.

## Feather guidance

Rules of thumb at about 3000 px on the long side; scale with image size.

| Edge | Feather |
|---|---|
| Product, packaging, hard object | 0 to 1 px (anti-alias only) |
| Person, body outline | 1 to 2 px |
| Hair (after refine) | 0; the refine handles it |
| Local adjustment on skin or sky | 20 to 100 px or a soft brush |
| Vignette, large tonal area | 10 to 20 % of the short side |

Prefer feathering the mask over feathering the selection: masks stay editable. PhotoCraft: `select.modify.feather` for selections; for masks, `layer.layerMask.edit {"feather": px}`, which softens the mask without changing its pixels and can be changed again later (tested: an edge pixel went from alpha 0.08 to 0.47 at 8 px).

## Inspecting masks

- View the mask alone: hard edges, holes and gray speckles show at once. PhotoCraft: `view.layerMask`, or `layer.toggleMaskOverlay` for a red overlay.
- Put a solid black fill layer under the subject, then a white one. Each reveals the opposite halo. PhotoCraft: `layer.newFillLayer.solidColor` with `#000000` and `#ffffff`, `layer.arrange.sendToBack` (or move it directly below the subject).
- Check at 100 % along the whole edge, then at fit-to-screen for the silhouette.
- Mask interior should be pure white (255), exterior pure black (0). Stray grays inside show as a semi-transparent subject.

## Check before done
- `scripts/verify.py out.pcraft --expect '{"has_mask":true}'`: a mask exists, no pixels deleted.
- Background region transparent on a cutout: `regions` with `"alpha_max":10` (pattern in recipes/cutout-to-mask.json).
- Subject interior intact: `regions` with `mean_rgb_near` on a subject patch, tolerance about 30.
- Edge halo check: render over black and over white; edge region `mean_luma_between` close to the subject, not to the old background.
- Masks are named and live; no destructive erase on the master.
