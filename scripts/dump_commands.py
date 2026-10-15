#!/usr/bin/env python3
"""Regenerate backends/photocraft-commands.tsv from the installed photocraft-cli.

Columns: id, menu path, shortcut, parameter doc. Search it with grep instead of loading it whole.
"""
import datetime
import json
import subprocess
from pathlib import Path

from pclib import find_cli

OUT = Path(__file__).resolve().parent.parent / "backends" / "photocraft-commands.tsv"


def main():
    cli = find_cli()
    commands = json.loads(subprocess.run([cli, "commands", "--json"], check=True,
                                         capture_output=True, text=True).stdout)
    version = subprocess.run(["git", "-C", str(Path(cli).resolve().parents[2]), "log", "-1",
                              "--format=%h"], capture_output=True, text=True).stdout.strip()
    lines = [f"# PhotoCraft command registry, {len(commands)} commands, dumped "
             f"{datetime.date.today().isoformat()} from github.com/storytold/photocraft"
             f"{' @' + version if version else ''} (MIT OR Apache-2.0)",
             "# id\tmenu\tshortcut\tparams"]
    for c in sorted(commands, key=lambda c: c["id"]):
        row = [c["id"], " > ".join(c.get("menu") or []), c.get("shortcut") or "", c.get("params") or ""]
        lines.append("\t".join(v.replace("\t", " ").replace("\n", " ") for v in row))
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} ({len(commands)} commands)")


if __name__ == "__main__":
    main()
