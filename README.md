# photo-editing-craft

An agent skill that edits images the way an experienced retoucher and designer would, in
[PhotoCraft](https://github.com/storytold/photocraft) (open source) or Adobe Photoshop.

Most Photoshop skills and MCP servers give an agent remote control: hundreds of commands and no
judgement. This skill adds the judgement and the proof:

- **Craft**: what to decide before touching pixels, the order of operations, which tool fits
  which edge, defect or output, with rules of thumb an agent can apply.
- **Two backends**: every technique names the PhotoCraft command id and the Photoshop menu path.
- **Tested recipes**: 14 recipes (color cast, contrast, spot removal, cutout, background swap,
  type, social and web export, CMYK print prep, watermark, black and white, vignette) run
  against generated fixtures, with pixel-level expectations that fail on the untouched image.
- **Measured results**: `scripts/verify.py` reports size, mode, ppi, layers, color, contrast,
  clipping and chroma, so the agent checks its work instead of trusting a status message.

## Install

Copy or symlink the folder into your agent's skill directory:

```sh
git clone https://github.com/<owner>/photo-editing-craft ~/.claude/skills/photo-editing-craft
```

Works with any agent that reads `SKILL.md` skills (Claude Code, Claude apps, other SKILL.md hosts).

For PhotoCraft, build it (`cargo build --release` in a checkout of storytold/photocraft) and either
put `photocraft-cli` on `PATH` or set `PHOTOCRAFT_CLI`. For its MCP server:

```sh
claude mcp add photocraft -- photocraft-cli mcp --automation-read-root ~/Pictures --automation-write-root ~/Pictures
```

For Adobe Photoshop, the skill gives menu paths and shortcuts; for automation pair it with a
Photoshop MCP such as [adb-mcp](https://github.com/mikechambers/adb-mcp).

## Use

Ask for the result, the skill does the rest:

> Remove the color cast from product.jpg, cut the product out, put it on #1e3c5a and export a 1080x1350 post.

Run a recipe yourself:

```sh
scripts/run_recipe.py recipes/fix-color-cast.json --in photo.jpg --out fixed.jpg \
  --master fixed.pcraft --var 'neutral=[812,440]' --preview look.png
scripts/verify.py fixed.pcraft --region 800,430,30,30
```

## Layout

```
SKILL.md            entry point: intake, order of operations, routing
craft/              decision guides, backend-neutral
backends/           photocraft.md, photoshop.md, photocraft-commands.tsv
recipes/            tested JSON recipes with expectations
scripts/            run_recipe.py, verify.py, test_all.py, make_fixtures.py, dump_commands.py
tests/fixtures/     generated, royalty-free test images
```

## Test

```sh
scripts/make_fixtures.py   # only if you change the generator
scripts/test_all.py        # runs every recipe and checks it; needs photocraft-cli
```

Python 3.9+, standard library only.

## License

MIT, see [LICENSE](LICENSE). The command registry in `backends/photocraft-commands.tsv` is
generated from PhotoCraft (MIT OR Apache-2.0). Adobe and Photoshop are trademarks of Adobe; this
project is not affiliated with Adobe.
