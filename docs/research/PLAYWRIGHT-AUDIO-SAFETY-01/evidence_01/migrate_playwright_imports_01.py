"""PLAYWRIGHT-AUDIO-SAFETY-01: repo内の `from playwright.sync_api import sync_playwright` をtools/playwright_safe_01.py経由へ機械置換する(冪等。API 0)。
使い方: python migrate_playwright_imports_01.py <repo_root> [--dry]   (再適用可: 他workerとconflictした場合はorigin/mainを取り直してこれを再実行)
- 音声再生を使わない(本文に play/aud/audio が無い)scriptは sync_playwright_noplay(play()をno-op化)、それ以外は sync_playwright(無音: --mute-audio + init script)。
- helperはscript位置から親ディレクトリを辿って tools/playwright_safe_01.py を探す(深さ非依存)。"""
import re, subprocess, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve(); dry = "--dry" in sys.argv
PAT = re.compile(r"^(?P<ind>[ \t]*)from playwright\.sync_api import sync_playwright(?P<tail>[ \t]*(?:#.*)?)$")
FIND = ('import sys as _pws_sys, pathlib as _pws_p; '
        '_pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools"))')
files = subprocess.run(["git", "grep", "-l", "-E", r"from playwright\.sync_api import sync_playwright", "--", "*.py"], cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
changed, noplay, mute = [], [], []
for rel in files:
    rel = rel.strip().strip('"')
    if not rel or rel.startswith("tools/playwright_safe_01") or "delegation_log" in rel:
        continue
    p = root / rel
    txt = p.read_text(encoding="utf-8")
    if "playwright_safe_01" in txt:
        continue
    low = txt.lower().replace("playwright", "")
    use_noplay = not any(k in low for k in ("play", "aud"))
    name = "sync_playwright_noplay as sync_playwright" if use_noplay else "sync_playwright"
    out, n = [], 0
    for ln in txt.split("\n"):
        m = PAT.match(ln.rstrip("\r"))
        if m:
            eol = "\r" if ln.endswith("\r") else ""
            ln = f"{m['ind']}{FIND}; from playwright_safe_01 import {name}  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout{eol}"; n += 1
        out.append(ln)
    if n:
        changed.append(rel); (noplay if use_noplay else mute).append(rel)
        if not dry:
            p.write_text("\n".join(out), encoding="utf-8", newline="")
print(f"changed={len(changed)} noplay={len(noplay)} mute_only={len(mute)} dry={dry}")
for r in noplay: print("NOPLAY", r)
