# Working with Adobe Photoshop as an agent

Menu names and shortcuts as of Photoshop 2026 (version 27); check Edit > Keyboard Shortcuts if one differs.

## Contents
- Decide fast
- Mapping table
- Automation routes
- Moving files between Photoshop and PhotoCraft
- Check before done

## Decide fast
- The craft files apply unchanged; only the commands differ. Use the mapping table below to translate.
- For live control from an agent, use an MCP bridge over UXP (adb-mcp). For unattended batch jobs on a workstation, use UXP scripts or recorded Actions.
- Generative features (Generative Fill, Generative Expand, Neural Filters, Sky Replacement; names as of Photoshop 2026) have no PhotoCraft equivalent. Say which tool produced a result when it matters for disclosure.
- Hand over PSD files only after opening them in the target app and comparing layers, masks and blend modes.

## Mapping table

Shortcuts: Mac first, Windows second. Cmd = Ctrl, Opt = Alt. Shortcuts can be remapped per installation; check Edit > Keyboard Shortcuts when one does not respond.

| Task | Photoshop menu path or tool + shortcut (Mac / Win) | PhotoCraft id |
|---|---|---|
| New document | File > New, Cmd+N / Ctrl+N | `file.new` |
| Save a copy (other format) | File > Save a Copy, Cmd+Opt+S / Ctrl+Alt+S | `file.saveACopy` |
| Export for web (legacy) | File > Export > Save for Web (Legacy), Cmd+Opt+Shift+S / Ctrl+Alt+Shift+S | `file.export.saveForWebLegacy` |
| Quick export | File > Export > Quick Export as PNG | `file.export.quickExport` |
| File metadata | File > File Info, Cmd+Opt+Shift+I / Ctrl+Alt+Shift+I | `file.fileInfo` |
| Place embedded | File > Place Embedded | `file.placeEmbedded` |
| Place linked | File > Place Linked | `file.placeLinked` |
| Batch with an action | File > Automate > Batch | `file.automate.batch` |
| Image Processor | File > Scripts > Image Processor | `file.scripts.imageProcessor` |
| Undo | Cmd+Z / Ctrl+Z | `edit.undo` |
| Image size | Image > Image Size, Cmd+Opt+I / Ctrl+Alt+I | `image.imageSize` |
| Canvas size | Image > Canvas Size, Cmd+Opt+C / Ctrl+Alt+C | `image.canvasSize` |
| Crop | Crop tool, C | `image.crop` |
| Perspective crop | Perspective Crop tool, C (cycle) | `image.perspectiveCrop` |
| Straighten | Crop tool > Straighten, or Ruler tool > Straighten Layer | `image.analysis.straightenLayer` |
| Free transform | Edit > Free Transform, Cmd+T / Ctrl+T | `edit.transform` |
| Flip layer | Edit > Transform > Flip Horizontal | `edit.transform.flipHorizontal` |
| Content-aware scale | Edit > Content-Aware Scale, Cmd+Opt+Shift+C / Ctrl+Alt+Shift+C | `edit.contentAwareScale` |
| Perspective warp | Edit > Perspective Warp | `edit.perspectiveWarp` |
| Convert to profile | Edit > Convert to Profile | `edit.convertToProfile` |
| Assign profile | Edit > Assign Profile | `edit.assignProfile` |
| Convert to CMYK | Image > Mode > CMYK Color | `image.mode.cmyk` |
| 16 bits per channel | Image > Mode > 16 Bits/Channel | `image.mode.bits16` |
| Proof setup | View > Proof Setup > Custom | `view.proofSetup` |
| Proof colors | View > Proof Colors, Cmd+Y / Ctrl+Y | `view.proofColors` |
| Gamut warning | View > Gamut Warning, Cmd+Shift+Y / Ctrl+Shift+Y | `view.gamutWarning` |
| Guide layout | View > Guides > New Guide Layout | `view.newGuideLayout` |
| New layer | Layer > New > Layer, Cmd+Shift+N / Ctrl+Shift+N | `layer.new.layer` |
| Layer via copy | Layer > New > Layer via Copy, Cmd+J / Ctrl+J | `layer.new.layerViaCopy` |
| Background to layer | Layer > New > Layer from Background | `layer.new.layerFromBackground` |
| Group layers | Layer > Group Layers, Cmd+G / Ctrl+G | `layer.groupLayers` |
| Merge down | Layer > Merge Down, Cmd+E / Ctrl+E | `layer.mergeDown` |
| Stamp visible | Cmd+Opt+Shift+E / Ctrl+Alt+Shift+E | `layer.stampVisible` |
| Clipping mask | Layer > Create Clipping Mask, Cmd+Opt+G / Ctrl+Alt+G | `layer.createClippingMask` |
| Flatten | Layer > Flatten Image | `layer.flattenImage` |
| Rename, opacity, blend mode | Layers panel | `layer.setProps` |
| Curves adjustment layer | Layer > New Adjustment Layer > Curves | `layer.newAdjustmentLayer.curves` |
| Levels adjustment layer | Layer > New Adjustment Layer > Levels | `layer.newAdjustmentLayer.levels` |
| Hue/Saturation adjustment layer | Layer > New Adjustment Layer > Hue/Saturation | `layer.newAdjustmentLayer.hueSaturation` |
| Vibrance adjustment layer | Layer > New Adjustment Layer > Vibrance | `layer.newAdjustmentLayer.vibrance` |
| Black & White adjustment layer | Layer > New Adjustment Layer > Black & White | `layer.newAdjustmentLayer.blackWhite` |
| Color Balance adjustment layer | Layer > New Adjustment Layer > Color Balance | `layer.newAdjustmentLayer.colorBalance` |
| Gradient fill layer | Layer > New Fill Layer > Gradient | `layer.newFillLayer.gradient` |
| Solid color fill layer | Layer > New Fill Layer > Solid Color | `layer.newFillLayer.solidColor` |
| Mask from selection | Layer > Layer Mask > Reveal Selection | `layer.layerMask.revealSelection` |
| Blend If | Layer > Layer Style > Blending Options | `layer.layerStyle.blendingOptions` |
| Drop shadow | Layer > Layer Style > Drop Shadow | `layer.layerStyle.dropShadow` |
| Convert to smart object | Layer > Smart Objects > Convert to Smart Object | `layer.smartObjects.convertToSmartObject` |
| Replace smart object contents | Layer > Smart Objects > Replace Contents | `layer.smartObjects.replaceContents` |
| Select all / deselect / inverse | Cmd+A, Cmd+D, Cmd+Shift+I / Ctrl+A, Ctrl+D, Ctrl+Shift+I | `select.all`, `select.deselect`, `select.inverse` |
| Select subject | Select > Subject (ML in Photoshop) | `select.subject` (classical, weaker on busy backgrounds) |
| Select sky | Select > Sky | `select.sky` |
| Color range | Select > Color Range | `select.colorRange` |
| Select and Mask | Select > Select and Mask, Cmd+Opt+R / Ctrl+Alt+R | `select.refineEdge` (parameter dialog, not a workspace) |
| Feather | Select > Modify > Feather, Shift+F6 | `select.modify.feather` |
| Quick mask | Q | `select.editInQuickMaskMode` |
| Spot healing | Spot Healing Brush, J | `paint.spotHealing` |
| Healing brush | Healing Brush, J (cycle) | `paint.healingBrush` |
| Clone stamp | Clone Stamp, S | `paint.cloneStamp` |
| Remove tool | Remove tool, J (cycle) | `paint.remove` (patch-based, not ML) |
| Content-aware fill | Edit > Content-Aware Fill | `edit.contentAwareFill` |
| Dodge / burn | Dodge and Burn tools, O | `paint.dodge`, `paint.burn` |
| Fill | Edit > Fill, Shift+F5 / Shift+F5 | `edit.fill` |
| Type | Type tool, T | `type.create`, `type.setStyle` |
| Unsharp mask | Filter > Sharpen > Unsharp Mask | `filter.sharpen.unsharpMask` |
| Gaussian blur | Filter > Blur > Gaussian Blur | `filter.blur.gaussianBlur` |
| Add noise | Filter > Noise > Add Noise | `filter.noise.addNoise` |
| High pass | Filter > Other > High Pass | `filter.other.highPass` |
| Camera Raw filter | Filter > Camera Raw Filter, Cmd+Shift+A / Ctrl+Shift+A | `filter.cameraRaw` (fewer raw formats) |
| Liquify | Filter > Liquify, Cmd+Shift+X / Ctrl+Shift+X | `filter.liquify` |
| Lens correction | Filter > Lens Correction, Cmd+Shift+R / Ctrl+Shift+R | `filter.lensCorrection` |
| Record / play action | Window > Actions | `actions.record`, `actions.play` |
| Generative Fill / Expand | Edit > Generative Fill, Crop tool Generative Expand | missing, use `edit.contentAwareFill` or clone and patch |
| Neural Filters | Filter > Neural Filters | missing, do the edit by hand (curves, masks, liquify) |
| Sky Replacement | Edit > Sky Replacement | missing, use `select.sky` plus a placed sky and manual matching |
| Remove background (quick action) | Properties > Quick Actions > Remove Background | `layer.removeBackground` (classical) |

## Automation routes

| Route | What it is | Trade-off |
|---|---|---|
| adb-mcp (Mike Chambers) | MCP server plus a UXP plugin and a local proxy; the agent calls Photoshop operations as tools | Closest to interactive work with an agent; needs Photoshop running with the plugin loaded and the proxy started; tool coverage is what the project exposes |
| UXP scripts and plugins with batchPlay | JavaScript in Photoshop's UXP runtime (`.psjs` scripts or plugins); `batchPlay` sends raw action descriptors | Full access, current platform; descriptors are verbose and poorly documented, record them with the Actions panel or a descriptor listener |
| ExtendScript (`.jsx`) | Legacy JavaScript scripting with the DOM and Action Manager | Many old scripts work; legacy technology without modern JS; avoid for new work |
| Actions and Droplets | Recorded steps played on files or folders; Droplets run as standalone apps | No code needed, easy for humans to edit; no conditions or logic, brittle when documents differ |

Rules that apply to every route:

- Photoshop runs as a desktop app with a user session. Plan for dialogs that block automation (missing fonts, profile mismatch, missing links). Set color settings and profile policies before batch runs.
- Read layer identity from the document, as with PhotoCraft. Layer indices shift when layers are added.
- Save a PSD master before any flatten or mode change, the same as craft/workflow-order.md.
- Verify with exported PNG or TIFF and `scripts/verify.py`. The checks do not depend on which editor made the file.

## Moving files between Photoshop and PhotoCraft

- PSD exchange works for common files but is not fully reliable in both directions. After a round trip, compare the layer tree (`scripts/verify.py file.psd`) and the composite (render both, compare region means).
- Risky in exchange: smart objects with filters, layer styles beyond the common ones, adjustment layers with unusual options, type with advanced features, 32-bit files.
- Generative layers made in Photoshop arrive as plain pixel layers at best. Keep the Photoshop PSD as the source of truth for those.
- Color settings: make both apps use the same working RGB and CMYK profiles, or numbers drift on open.

## Check before done
- Every task in the job maps to a Photoshop step or a PhotoCraft id, or is flagged as missing with a workaround.
- PSD opened in the receiving app; layer count and names match (`scripts/verify.py file.psd --expect '{"layers_min":N}'`).
- Exported composites from both apps agree: region `mean_rgb_near` within a tolerance of about 3 on a few test regions.
- Use of generative features is listed in the hand-off when the client must disclose it.
