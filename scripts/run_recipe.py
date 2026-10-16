#!/usr/bin/env python3
"""Run a recipe (recipes/*.json) on an image with PhotoCraft and save the result.

    run_recipe.py RECIPE.json (--in IMAGE | --new '{"width":1080,...}') --out OUT
                  [--master OUT.pcraft] [--var name=value ...] [--preview p.png] [--cli PATH]

Recipe steps are {"id": command, "params": {...}, "target": ref?, "as": name?}. Values in params
may reference earlier results instead of hardcoded layer ids:

    "$background"   bottom pixel layer of the document
    "$last"         layer id returned by the previous step
    "$<name>"       layer id returned by the step stored with "as": "<name>"
    "${var}"        a recipe variable (defaults in "vars", override with --var)
    "=expr"         arithmetic on width, height, numbers and vars, e.g. "=width*0.5-200"

"target" selects that layer before the step (filters and pixel tools need an active pixel layer).
"for_each": "${list}" repeats a step once per list item, with the item available as ${item}.
Prints a JSON report; exits 1 on the first failing step with the PhotoCraft error and a hint.
"""
import argparse
import ast
import json
import operator
import re
import sys
import time
from pathlib import Path

from pclib import PhotoCraftError, Session, background_layer, common_root, walk_layers

HINTS = {
    "filters need a pixel layer": 'add "target": "$background" (or another pixel layer) to the step',
    "position-locked": "run layer.new.layerFromBackground first; the Background cannot move",
    "no selection": "an earlier selection step selected nothing; check its coordinates",
    "no such layer": "use $background/$last/$name refs instead of literal layer ids",
    "invalid parameters": "check the parameter doc: photocraft-cli commands --filter <id>",
    "automation path rejected": "keep every file inside one folder tree (the automation root)",
}

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.USub: operator.neg}


def evaluate(expr, names):
    """Safe arithmetic: numbers, + - * / //, parentheses, and the given names."""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"unsupported expression: {expr}")
    value = ev(ast.parse(expr, mode="eval"))
    return int(round(value)) if isinstance(value, float) and value.is_integer() else value


class Resolver:
    def __init__(self, variables):
        self.vars = variables
        self.layers = {}
        self.doc = {}

    def names(self):
        nums = {k: v for k, v in self.vars.items() if isinstance(v, (int, float))}
        return {**nums, "width": self.doc.get("width", 0), "height": self.doc.get("height", 0)}

    def value(self, v):
        if isinstance(v, dict):
            return {k: self.value(x) for k, x in v.items()}
        if isinstance(v, list):
            return [self.value(x) for x in v]
        if not isinstance(v, str):
            return v
        if v.startswith("="):
            expr = re.sub(r"\$\{(\w+)\}", lambda m: str(self.vars[m.group(1)]), v[1:])
            return evaluate(expr, self.names())
        whole = re.fullmatch(r"\$\{(\w+)\}", v)
        if whole:
            return self.vars[whole.group(1)]
        if re.fullmatch(r"\$\w+", v):
            key = v[1:]
            if key not in self.layers:
                raise PhotoCraftError(f"unknown reference {v} (known: {sorted(self.layers)})")
            return self.layers[key]
        return re.sub(r"\$\{(\w+)\}", lambda m: str(self.vars[m.group(1)]), v)


def parse_vars(recipe, overrides):
    variables = dict(recipe.get("vars", {}))
    for item in overrides:
        key, _, raw = item.partition("=")
        try:
            variables[key] = json.loads(raw)
        except json.JSONDecodeError:
            variables[key] = raw
    return variables


def has_background(doc):
    return any(l.get("name") == "Background" and l.get("kind") == "Pixel"
               for _, l in walk_layers(doc["layers"]))


def hint_for(message):
    return next((h for k, h in HINTS.items() if k in message), None)


def expand(steps, resolver):
    """Unroll {"for_each": "${list}", ...}: one step per item, ${item} bound to each value."""
    for step in steps:
        if "for_each" not in step:
            yield step
            continue
        for item in resolver.value(step["for_each"]):
            resolver.vars["item"] = item
            yield {k: v for k, v in step.items() if k != "for_each"}


def run(recipe, session, resolver, report):
    for i, step in enumerate(expand(recipe["steps"], resolver)):
        resolver.doc = session.call("doc.inspect")
        resolver.layers["background"] = background_layer(resolver.doc)
        entry = {"step": i, "id": step["id"]}
        started = time.time()
        try:
            if "target" in step:
                session.run("layer.select", {"layer": resolver.value(step["target"])})
            params = resolver.value(step.get("params", {}))
            entry["params"] = params
            if step["id"] == "layer.new.layerFromBackground" and not has_background(resolver.doc):
                # documents from other apps (many PSDs) have no locked Background: nothing to unlock
                result = {"layer": resolver.layers["background"], "skipped": "no Background layer"}
            else:
                result = session.run(step["id"], params)
        except (PhotoCraftError, KeyError, ValueError) as e:
            entry.update(error=str(e), hint=hint_for(str(e)))
            report["steps"].append(entry)
            return False
        entry.update(result=result, ms=int(1000 * (time.time() - started)))
        report["steps"].append(entry)
        layer = result.get("layer") if isinstance(result, dict) else None
        if layer is not None:
            resolver.layers["last"] = layer
            if "as" in step:
                resolver.layers[step["as"]] = layer
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("recipe")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--in", dest="input", help="image to open")
    src.add_argument("--new", help="file.new params as JSON")
    ap.add_argument("--out", required=True, help="result; extension picks the format")
    ap.add_argument("--master", help="also save the layered document (.pcraft or .psd)")
    ap.add_argument("--var", action="append", default=[], help="name=value (JSON or text)")
    ap.add_argument("--preview", help="PNG preview to look at (max side 1024)")
    ap.add_argument("--report", help="write the JSON report here instead of stdout")
    ap.add_argument("--force", action="store_true", help="replace --out if it already exists")
    ap.add_argument("--cli", help="path to photocraft-cli")
    a = ap.parse_args()
    if a.input:
        src_path = Path(a.input).resolve()
        for target in (a.out, a.master):
            if target and Path(target).resolve() == src_path:
                sys.exit("error: output would overwrite the input; write to a new file")
    if Path(a.out).exists() and not a.force:
        sys.exit(f"error: {a.out} exists; pass --force to replace it")

    recipe = json.loads(Path(a.recipe).read_text())
    resolver = Resolver(parse_vars(recipe, a.var))
    files = [p for p in (a.input, a.out, a.master, a.preview, a.report) if p]
    for p in files[1:] if a.input else files:
        Path(p).resolve().parent.mkdir(parents=True, exist_ok=True)
    report = {"recipe": recipe.get("name"), "steps": []}
    ok = False
    try:
        with Session(a.cli, root=common_root(*files)) as s:
            if a.input:
                s.call("doc.open", {"path": str(Path(a.input).resolve())})
            else:
                s.call("doc.new", json.loads(a.new))
            ok = run(recipe, s, resolver, report)
            if ok:
                if a.master:
                    s.call("doc.save", {"path": str(Path(a.master).resolve())})
                out = Path(a.out).resolve()
                if out.exists():
                    out.unlink()  # --force given; PhotoCraft itself never replaces an export
                s.call("doc.save", {"path": str(out)})
                if a.preview:
                    s.call("doc.render", {"path": str(Path(a.preview).resolve()), "maxSide": 1024})
                report["output"] = str(out)
    except PhotoCraftError as e:
        report["error"] = str(e)
        report["hint"] = hint_for(str(e))
    text = json.dumps(report, indent=1)
    Path(a.report).write_text(text) if a.report else print(text)
    if not ok or "error" in report:
        failed = next((s for s in report["steps"] if "error" in s), report)
        print(f"FAILED at step {failed.get('step', '-')} {failed.get('id', '')}: "
              f"{failed.get('error')}" + (f"\nhint: {failed['hint']}" if failed.get("hint") else ""),
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
