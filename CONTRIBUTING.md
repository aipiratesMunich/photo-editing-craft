# Contributing

Recipes are the most useful contribution. Fixes to the craft guides and to the Photoshop menu
map are welcome too, especially when you can point to the version you checked.

## Add a recipe

1. Generate a test image for it in `scripts/make_fixtures.py` (no third-party photos; they need
   a license we cannot check). Run the script to write it to `tests/fixtures/`.
2. Write `recipes/<name>.json`:
   - `name`, `summary`, `when` (the situation, in one or two sentences)
   - `vars` with sensible defaults, `steps` using `$background`, `$last`, `$<name>` and `${var}`
     instead of layer ids
   - `test` (`in`, optional `out_ext` and `vars`)
   - `expect`: assertions for `scripts/verify.py` that prove the edit happened
   - `photoshop`: the menu path for the same edit, `notes`: when it goes wrong
3. Look up every command and parameter first:
   `awk -F'\t' '$1=="<id>"' backends/photocraft-commands.tsv`
4. Run `scripts/test_all.py <name>` and open `tests/out/<name>.preview.png`.
5. Show that the expectation fails on the untouched fixture:
   `scripts/verify.py tests/fixtures/<image> --expect recipes/<name>.json` must exit 1 on a pixel
   check, not only on a layer count.
6. Add the recipe to the routing table in `SKILL.md` and to the table in `README.md`.

## Change a guide

Keep the format: a "Decide fast" box first, a PhotoCraft line per technique with real command
ids, and a "Check before done" list at the end. Write in your own words. Do not paste text from
books, courses or vendor documentation.

## Before a pull request

- `scripts/test_all.py` passes
- no new dependencies in the skill scripts (standard library only; Pillow is fine in the
  `make_*_media.py` docs scripts)
- one topic per pull request
