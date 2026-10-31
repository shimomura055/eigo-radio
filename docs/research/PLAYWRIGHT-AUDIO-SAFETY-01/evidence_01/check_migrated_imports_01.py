"""PLAYWRIGHT-AUDIO-SAFETY-01: 置換済み全scriptのimport行を、そのscriptの実位置(__file__)で実行して解決できることを確認(API 0・ブラウザ起動なし)。"""
import subprocess, sys, json
from pathlib import Path
root = Path(sys.argv[1]).resolve()
files = subprocess.run(["git", "grep", "-l", "PLAYWRIGHT-AUDIO-SAFETY-01: 無音", "--", "*.py"], cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.split()
ok = bad = 0; res = []
for rel in files:
    p = root / rel
    line = next(l for l in p.read_text(encoding="utf-8").split("\n") if "playwright_safe_01 import" in l).strip()
    code = line.split("  #")[0]
    g = {"__file__": str(p)}
    try:
        exec(code, g); assert callable(g["sync_playwright"]); ok += 1
        res.append((rel, "noplay" if "noplay" in code else "mute"))
    except Exception as e:
        bad += 1; print("BAD", rel, e)
print(f"files={len(files)} import_ok={ok} bad={bad} noplay={sum(1 for _, k in res if k=='noplay')}")
leftover = subprocess.run(["git", "grep", "-n", "-E", r"from playwright\.sync_api import sync_playwright", "--", "*.py"], cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
leftover = [l for l in leftover if l and "delegation_log" not in l]
print("leftover raw imports:", len(leftover)); [print(" ", l[:200]) for l in leftover[:10]]
