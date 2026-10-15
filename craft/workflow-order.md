# Workflow order

## Decide fast
- Order: inspect, fix geometry, clean up, global tone, global color, local work, composite and type, then output copies.
- Every correction lives on its own layer (adjustment layer, empty retouch layer, smart filter, mask). The Background stays original.
- The layered master is the product. JPEG, PNG and PDF are disposable copies made from it.
- Destructive is fine on a duplicate, on a throwaway output copy, or when the step cannot be done any other way.

## Order of operations, with reasons

| Step | What | Why here | PhotoCraft |
|---|---|---|---|
| 1 Inspect | size, mode, profile, bit depth, histogram, defects | the plan depends on what is there | `document.inspect`, `edit.profileInfo`, `scripts/verify.py --preview` |
| 2 Raw and lens | exposure, white balance, lens profile | most latitude before any pixel edit | `filter.cameraRaw`, `filter.lensCorrection` |
| 3 Geometry | straighten, perspective, crop loosely | retouching then works on final framing; a tight crop too early leaves no room for compositing | `image.analysis.straightenLayer`, `image.perspectiveCrop`, `edit.transform` |
| 4 Cleanup | dust, spots, distractions | tone moves make spots more visible; clean first so you see them once | `layer.new.layer` then `paint.spotHealing`; recipe: recipes/remove-spots.json |
| 5 Global tone | black and white points, contrast | color judgments depend on tone | `layer.newAdjustmentLayer.levels`, `layer.newAdjustmentLayer.curves`; recipe: recipes/add-contrast-curve.json |
| 6 Global color | cast, saturation | needs correct tone first | recipes: recipes/fix-color-cast.json, recipes/natural-saturation.json |
| 7 Local | dodge and burn, selective color, masks | refines a balanced base | adjustment layers with masks |
| 8 Composite, type, graphics | plates, shadows, text | built on a finished base | see craft/compositing.md, craft/typography.md |
| 9 Look | grade, vignette, grain | last creative layer, easy to toggle | recipe: recipes/vignette.json |
| 10 Output | resize, sharpen, convert, export per deliverable | depends on final size and medium | see craft/output-web.md, craft/output-print.md |

Rule of thumb: if a later step makes you redo an earlier one, the order was wrong for this image. Move the step, do not stack corrections on top.

## Non-destructive principles

- Adjustments as adjustment layers. PhotoCraft: `layer.newAdjustmentLayer.*`; change later with `layer.setAdjustment`. The `image.adjustments.*` variants bake into pixels.
- Filters as smart filters. PhotoCraft: `layer.smartObjects.convertToSmartObject` (or `filter.convertForSmartFilters`), then `filter.*`; tune with `layer.smartFilter.setParams`.
- Hide, do not erase. PhotoCraft: `layer.layerMask.revealSelection`, `layer.layerMask.hideSelection`. Never `paint.backgroundEraser` or `paint.magicEraser` on the only copy.
- Retouch on empty layers sampling all layers below. PhotoCraft: `layer.new.layer`, then heal or clone onto it.
- Transform smart objects, not pixels. Repeated pixel transforms soften each time.
- Keep type live. Rasterize only on an output copy. PhotoCraft: `type.rasterize` is a last resort.

## When destructive is fine

- On a copy you can throw away: `layer.duplicate` or `layer.stampVisible` (merged copy above, originals stay).
- Dust removal on a raw scan where a retouch layer would be enormous: duplicate the Background first.
- Liquify, puppet warp or perspective warp on pixel layers when the smart object route is too slow. Keep the unwarped layer hidden below.
- Final output copies: flatten, convert, sharpen. Never on the master.
- Mode changes for output (CMYK, 8-bit, indexed). Do them on a duplicate document. PhotoCraft: `image.duplicate`.

## Master vs deliverables

- Master: full resolution, RGB, 16-bit where tone work is heavy, all layers, `.pcraft` plus `.psd` when a Photoshop user will open it.
- Deliverables: generated from the master per target, never edited afterwards. If a deliverable needs a fix, fix the master and regenerate.
- PhotoCraft saves: `doc_save` with `.pcraft` or `.psd` keeps layers; `.png`, `.jpg`, `.webp` flatten (warning `layers flattened`). PhotoCraft never overwrites on export; pick a new name.
- PSD round-trip with Photoshop is not fully reliable. Open the PSD in Photoshop and compare before handing it over.

## Layer naming and grouping

- Name every layer for what it does: `Neutralize cast`, `Dodge face`, `Retouch skin`, `Headline`. PhotoCraft: `layer.setProps` with `name`.
- Group by stage, bottom to top: `Base` (original plus cleanup), `Tone`, `Color`, `Local`, `Composite`, `Type`, `Look`. PhotoCraft: `layer.new.groupFromLayers`, `layer.groupLayers`.
- Use label colors for status if the team does (red = needs review). PhotoCraft: `layer.setLabelColor`.
- Delete hidden experiments before hand-off, or keep them in one group named `Unused` that is switched off. PhotoCraft: `layer.delete.hiddenLayers`.
- Layer comps for variants (with and without text, two crops) beat duplicate files. PhotoCraft: `layerComp.new`, `file.export.layerCompsToFiles`.

## Saving versions

- Save the master after each stage: `job_v01_cleanup.pcraft`, `job_v02_tone.pcraft`. Cheap insurance against a wrong turn several steps back.
- History is not a backup. One command is one history step, and `command_batch` is not a transaction: earlier steps stay applied after a failure.
- Name deliverables by target: `job_ig-4x5_1080x1350.jpg`, `job_A4_bleed_cmyk.pdf`.
- Keep the brief and assumptions next to the files, or in `file.fileInfo` `description`.

## Agent loop per step

1. State the intended change and a measurable expectation.
2. Run one command. Read the returned layer id; do not assume ids.
3. Render and look. PhotoCraft: `render_preview` or `scripts/verify.py --preview`.
4. Measure where possible (`--expect`). If it misses, change the parameter, not the order.

## Check before done
- `scripts/verify.py master.pcraft` layer tree shows named layers, grouped, Background unchanged.
- `--expect '{"layers_min":N}'` and, where masks were used, `"has_mask":true`.
- No adjustment was baked: no `image.adjustments.*` on the master unless stated.
- Each deliverable regenerates from the master; filenames name the target.
- Master saved as `.pcraft` (and `.psd` if requested); PSD opened in Photoshop when a client will use it.
