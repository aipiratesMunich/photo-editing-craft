---
name: photo-editing-craft
description: Edits photos and graphics with the judgment of an experienced retoucher and designer, in PhotoCraft (open-source, MCP and CLI) or Adobe Photoshop. Covers color and tone correction, retouching, cutouts and masks, compositing, type on images, web and social export, and print preparation, with tested recipes and a verify script that measures the result. Use when the user asks to fix, retouch, cut out, combine, label, resize, export or print-prepare an image, mentions Photoshop or PhotoCraft, or asks how to do an image-editing task well.
---

# Photo editing craft

Work like a professional: settle the brief, edit in a fixed order, stay non-destructive, and
measure the result before calling it done.

## Workflow checklist

Copy this and tick it off:

```
- [ ] 1. Brief: medium, size, color space, deliverables, master needed? (craft/intake.md)
- [ ] 2. Inspect the source: size, mode, layers, histogram, defects (scripts/verify.py)
- [ ] 3. Plan the steps in order (craft/workflow-order.md); pick recipes that fit
- [ ] 4. Edit non-destructively on a copy; never overwrite the original
- [ ] 5. Look and measure after each major step (preview + verify.py)
- [ ] 6. Output: resize, sharpen for the medium, convert color, export (craft/output-*.md)
- [ ] 7. Final check against the brief; save the layered master next to the deliverables
```

## Order of operations

1. Inspect: size, mode, profile, histogram, defects
2. Raw and lens: exposure, white balance, lens profile
3. Geometry: straighten, perspective, loose crop
4. Cleanup: dust, spots, distractions on empty layers
5. Global tone (levels, curves), then global color (cast, vibrance)
6. Local work: dodge, burn, masked adjustments
7. Cutouts, compositing, type and graphics
8. Look: grade, vignette, grain
9. Output copies: final crop and resize, sharpen for the medium, convert color, export

Clean up before tone moves make spots stand out. Tone before color, because contrast moves
saturation. Sharpen last, because the right amount depends on final pixel size. Details and exceptions: craft/workflow-order.md.

## Rules that always apply

- Keep the original untouched. Work on a copy; save a layered master (`.pcraft` or `.psd`).
- Prefer adjustment layers, masks and smart filters over edits that change pixels for good.
- Restrict a correction to one layer with a clipping mask; to an area with a layer mask.
- Do not invent facts in documentary or news images (no adding or removing content there).
- Ask before anything that cannot be undone on the user's files (overwrite, flatten, delete).
- Never call it done without looking: render a preview and check the measurable goal.

## Where to look

| Task | Read | Recipe(s) |
|---|---|---|
| Brief, target sizes, formats | craft/intake.md | |
| Order, master files, layers | craft/workflow-order.md | |
| Color cast, contrast, saturation, black and white | craft/color-and-tone.md | fix-color-cast, add-contrast-curve, natural-saturation, black-and-white, vignette |
| Spots, blemishes, distractions | craft/retouching.md | remove-spots |
| Cutouts, hair, masks | craft/selection-and-masking.md | cutout-to-mask |
| Combining images, new backgrounds, shadows | craft/compositing.md | replace-background |
| Headlines, captions, text over photos | craft/typography.md | title-with-shadow, image-inside-text, watermark |
| Web, social, email output | craft/output-web.md | social-export-4x5, resize-for-web |
| Print, CMYK, bleed, PDF | craft/output-print.md | print-prep-cmyk |
| Driving PhotoCraft (MCP, CLI, footguns) | backends/photocraft.md | |
| Photoshop menu paths, shortcuts, automation | backends/photoshop.md | |

## Choosing the backend

- **PhotoCraft MCP tools available** (`photocraft:command_run` and friends): use them. Read
  backends/photocraft.md first. Look up every command with `command_list {"filter": ...}` or
  `awk -F'\t' '$1=="<id>"' backends/photocraft-commands.tsv` before calling it.
- **photocraft-cli available, no MCP**: use `scripts/run_recipe.py` for recipes and
  `scripts/verify.py` for checks.
- **Adobe Photoshop**: give menu paths and shortcuts from backends/photoshop.md, or drive it
  through a Photoshop MCP if one is connected. The craft guidance is the same.
- **Generative edits** (generative fill, sky replacement, neural filters): Photoshop only.
  PhotoCraft has no ML features; offer the classical route or say it cannot be done there.

## Recipes

`recipes/*.json` are tested step lists with variables, a test fixture and pixel expectations.
Run one on a real image:

```sh
scripts/run_recipe.py recipes/<name>.json --in IN --out OUT --master OUT.pcraft \
  [--var key=value] --preview look.png
```

Steps use `$background`, `$last`, `$<name>` and `${var}` instead of layer ids, so they work on
any document. Adapt coordinates and values to the image (for example the neutral point for a
color cast), then check with verify.py. Through MCP, send the same steps with `command_batch`
after replacing the refs with real ids from `doc_inspect`.

## Verify before done

```sh
scripts/verify.py OUT.pcraft --preview look.png \
  --expect '{"width":1080,"height":1350,"regions":[{"region":[x,y,w,h],"max_channel_spread":6}]}'
```

Look at the preview image yourself. Then state what changed and what you measured, for example
"gray card spread 44 to 0.2; contrast (luma std) 15 to 27; 1080 x 1350 sRGB JPEG". If a check
fails or you could not look, say so.
