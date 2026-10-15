#!/usr/bin/env python3
"""Run every recipe on its test fixture, then check the result with verify.py.

    test_all.py [recipe-name ...]

Outputs land in tests/out/ (result, layered .pcraft master, preview PNG, JSON report).
Exit code 1 if any recipe fails to run or misses its expectations.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out"


def last_lines(text, n=3):
    return " | ".join(text.strip().splitlines()[-n:])


def test(name):
    recipe_path = ROOT / "recipes" / f"{name}.json"
    t = json.loads(recipe_path.read_text())["test"]
    master = OUT / f"{name}.pcraft"
    run = [sys.executable, str(ROOT / "scripts/run_recipe.py"), str(recipe_path),
           "--in", str(ROOT / "tests/fixtures" / t["in"]),
           "--out", str(OUT / (name + t.get("out_ext", ".png"))),
           "--master", str(master), "--report", str(OUT / f"{name}.report.json")]
    for k, v in t.get("vars", {}).items():
        run += ["--var", f"{k}={json.dumps(v)}"]
    p = subprocess.run(run, capture_output=True, text=True)
    if p.returncode:
        return "FAIL run: " + last_lines(p.stderr)
    verify = [sys.executable, str(ROOT / "scripts/verify.py"), str(master),
              "--expect", str(recipe_path), "--preview", str(OUT / f"{name}.preview.png")]
    p = subprocess.run(verify, capture_output=True, text=True)
    if p.returncode:
        return "FAIL verify: " + last_lines(p.stderr, 5)
    return "PASS"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or sorted(p.stem for p in (ROOT / "recipes").glob("*.json"))
    failed = 0
    print(f"{'RECIPE':<22} RESULT")
    for name in names:
        result = test(name)
        failed += result != "PASS"
        print(f"{name:<22} {result}", flush=True)
    print(f"\n{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
