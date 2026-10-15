# Driving PhotoCraft

PhotoCraft ([github.com/storytold/photocraft](https://github.com/storytold/photocraft), MIT OR Apache-2.0)
is an open-source image editor modelled on Photoshop's menus, layers and file formats. Its engine
commands mirror Photoshop's menus: `image.adjustments.curves` is Image > Adjustments > Curves,
`layer.newAdjustmentLayer.curves` is the non-destructive version.

## Contents
- Three ways to drive it
- Discover before you call
- Rules that prevent most failures
- Footguns seen in testing
- Files, roots and formats
- Checking results
- What PhotoCraft does not have

## Three ways to drive it

| Way | Use when | Entry point |
|---|---|---|
| MCP tools `photocraft:*` | interactive work in an agent session, with previews | `doc_new` / `doc_open` → `command_list` → `command_run` / `command_batch` → `render_preview` → `doc_save` |
| `scripts/run_recipe.py` | a known recipe on one image, layer ids resolved for you | `run_recipe.py recipes/X.json --in a.jpg --out b.jpg --master b.pcraft` |
| `photocraft-cli` directly | one-off pipelines, folders of files | `run <in> --cmd id --params '{}' ... --out f`, `batch --actions a.json --in dir --out dir` |

The MCP server starts with `photocraft-cli mcp --automation-read-root DIR --automation-write-root DIR`.
UI tools (`ui_inspect`, `ui_screenshot`, `ui_menu_invoke`) need the desktop app running in bridge mode.

## Discover before you call

Never guess a parameter. Each command documents its own:

```sh
photocraft-cli commands --filter curves            # ids, menus, shortcuts
grep -P '^layer\.newAdjustmentLayer\.curves\t' backends/photocraft-commands.tsv
```

In MCP: `command_list {"filter": "curves"}`; add `"enabled_only": true` to see what can run now.
Parameter docs show ranges and defaults, e.g. `"amount":1..500=100`. Regenerate the TSV after
upgrading PhotoCraft: `scripts/dump_commands.py`.

## Rules that prevent most failures

1. Read layer ids from `doc_inspect`; never assume them. Commands that create a layer return
   `{"layer": id}`. In a new document the Background is usually id 2, not 1.
2. The active layer receives filters and paint. After `type.create` or an adjustment layer, that
   new layer is active; select a pixel layer first (`layer.select {"layer": id}`, or `"target"`
   in a recipe step).
3. Prefer `layer.newAdjustmentLayer.*`, layer masks and `layer.smartObjects.convertToSmartObject`
   followed by `filter.*` (a smart filter) over destructive edits.
4. One command is one history step. `command_batch` is not a transaction; with
   `stop_on_error: true` it stops at the first failure and earlier steps stay applied.
5. A `points` list in a paint command (`paint.spotHealing`, `paint.stroke`, `paint.remove`) is one
   connected stroke. For separate clicks, send one command per point (`for_each` in recipes).
6. Render and look after every meaningful step (`render_preview`, `scripts/verify.py --preview`).

## Footguns seen in testing (2026-10)

| Message | Cause | Fix |
|---|---|---|
| `filters need a pixel layer (active layer is a Type layer)` | text or adjustment layer active | `layer.select` a pixel layer |
| `layer "Background" is position-locked` | moving or transforming the Background | `layer.new.layerFromBackground` first |
| `no such layer LayerId(1)` | guessed id | use the id from `doc_inspect` or the creating step |
| `no selection` | a selection step selected nothing (e.g. magic wand subtract on a flat area) | check coordinates on the real image |
| `automation path rejected: absolute paths must be inside the automation root` | file outside the allowed root | keep inputs and outputs under one directory tree |
| `layers flattened; layers, masks and blend modes are not kept` (warning) | saving to PNG/JPEG | also save a `.pcraft` or `.psd` master |
| `"photocraftManages" needs a "printerProfile"` | `file.print` color handling | pass a profile or use `printerManages` |
| export refuses an existing file | PhotoCraft never overwrites on export | delete the old file or pick a new name |

## Files, roots and formats

- File access is limited to the automation roots given at launch. `file.*` commands that take
  arbitrary paths are refused; use `doc_open`, `doc_save`, `doc_export` (MCP) or `doc.open`,
  `doc.save` (serve).
- The extension picks the format: `.pcraft` (native) and `.psd` keep layers; `.tif` keeps layers
  with `tiffLayers`; `.png`, `.jpg`, `.webp` are flattened exports.
- PSD exchange with Photoshop works for common files but is not yet fully reliable in both
  directions. When a client opens the file in Photoshop, test that before delivery.
- PDF output is raster only (no live text or vectors, single page).

## Checking results

`scripts/verify.py IMAGE --preview p.png --expect '{...}'` prints size, mode, ppi, the layer tree,
mean color, contrast (luma standard deviation), clipping and chroma, per region if asked, and
fails loudly when an expectation is missed. Examples:

```sh
# is the gray card neutral now?
verify.py out.pcraft --expect '{"regions":[{"region":[40,40,80,80],"max_channel_spread":6}]}'
# is the deliverable the right size and mode?
verify.py out.tif --expect '{"width":2480,"height":3508,"mode":"Cmyk","resolution":300.0}'
```

`document.pixel {"x":..,"y":..}` returns the composite RGBA (0..1) at one point.

## What PhotoCraft does not have

From the project's own gap list (`docs/gaps.md`, reviewed 2026-10-10); check it again before
relying on this:

- No ML or generative features: no Generative Fill or Expand, Neural Filters, Sky Replacement,
  Super Zoom, ML-based Select Subject. `select.subject` is a classical graph-cut segmentation:
  good on clear contrast, weak on busy backgrounds. Removal uses patch-based completion.
- Type on a path is missing; type depth is behind Photoshop.
- Camera Raw covers less (some raw formats unsupported).
- No hosting of Photoshop `.8BF` plug-ins, UXP or CEP panels.
- Video: a timeline, video layers and frame export exist; clip trimming, keyframes,
  transitions and audio are not available through commands.
- Some workspaces (Select and Mask) are parameter dialogs rather than interactive workspaces.
