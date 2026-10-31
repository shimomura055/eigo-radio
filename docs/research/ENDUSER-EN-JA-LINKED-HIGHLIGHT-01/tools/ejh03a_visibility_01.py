# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A: 点灯した日本語訳が画面内に見えている割合(PC 1280x900 / mobile 390x844)の実測(API 0・UI変更なし)。

各dirの各levelで、ja_alignの対応済み群ごとに、群の最初の英語文の再生位置へシークし、ページ自身のスクロール追従後に
 - 英語文(.sent.on)が画面内か / 点灯した日本語(.jhl.on)が画面内(全体が見える)か / 日本語が一部だけ見えるか
を数える。自動scrollの追加などUI変更は行わない(可視性の改善はユーザー判断=委任_03A方針6)。
使い方: .venv\\Scripts\\python.exe docs\\research\\ENDUSER-EN-JA-LINKED-HIGHLIGHT-01\\tools\\ejh03a_visibility_01.py <公開dir> [<公開dir> ...] [--out json] [--base-url https://.../]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import er135_enduser_page_verify_01 as V  # noqa: E402

# 再生中(ページの自動追従がscrollする条件: 再生中・直近3.5秒にユーザーscrollなし)の状態で測る。再生速度0.25で文が短くても点灯が測定窓(1.4秒)に収まるようにする。
MAX_PER_LEVEL = 16
JS_SEEK = """([t, sid]) => new Promise(res => { const a=document.getElementById('aud'); a.playbackRate=0.25;
  const go=()=>{ a.play().catch(()=>{}); setTimeout(()=>{
    a.currentTime=t;                                   // 再生中のシーク=ページの自動追従(scroll)が働く条件
    setTimeout(()=>{
      const vh=innerHeight, r=(e)=>{ if(!e) return null; const b=e.getBoundingClientRect(); return {top:b.top, bottom:b.bottom, vis: b.top>=0 && b.bottom<=vh, part: b.bottom>0 && b.top<vh}; };
      const ja=[...document.querySelectorAll('.jhl.on')].map(r), en=[...document.querySelectorAll('.sent.on')].map(r);
      const act=(window.__EUP||{}).active; a.pause(); res({ja, en, active: act, same: act===sid}); }, 1500); }, 350); };
  a.pause(); a.currentTime=0; setTimeout(go, 250); })"""


def measure_dir(p, public_dir: Path, base_url: str | None) -> dict:
    srv = None
    if base_url is None:
        srv, base = V.serve(str(public_dir))
    else:
        base = base_url.rstrip("/")
    try:
        art = V._get_json(base + "/enduser/data/article.json")
        syncs = {lv: {r["sid"]: r for r in V._get_json(base + f"/enduser/data/sync_{lv}.json")["sentences"]} for lv in art["levels"]}
        out = {}
        for view, opts in V.VIEWS.items():
            browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
            page = browser.new_context(**opts).new_page()
            for lv, L in art["levels"].items():
                page.goto(base + f"/enduser/index.html?lv={lv}&cb={int(time.time() * 1000)}")
                page.wait_for_selector(".sent")
                page.wait_for_function("() => window.__EUP && window.__EUP.syncKind === 'real'", timeout=15000)
                page.wait_for_timeout(300)
                n = vis = part = en_vis = skipped = 0
                allg = [g for pt in L["parts"] for g in (pt.get("ja_align") or []) if g.get("ja")]
                step = max(1, -(-len(allg) // MAX_PER_LEVEL))              # 等間隔サンプリング(各level最大MAX_PER_LEVEL群。先頭・末尾を含む)
                for g in allg[::step] + ([allg[-1]] if allg and (len(allg) - 1) % step else []):
                    r = syncs[lv].get(g["sids"][0])
                    if not r:
                        continue
                    t = r["start"] + 0.3 if r["end"] - r["start"] > 0.7 else (r["start"] + r["end"]) / 2
                    st = page.evaluate(JS_SEEK, [t, g["sids"][0]])
                    if not st["ja"] or not st["same"]:
                        skipped += 1
                        continue
                    n += 1
                    vis += 1 if all(x["vis"] for x in st["ja"]) else 0
                    part += 1 if any(x["part"] for x in st["ja"]) else 0
                    en_vis += 1 if st["en"] and all(x["vis"] for x in st["en"]) else 0
                out[f"{view}_{lv}"] = {"groups_sampled": n, "ja_fully_visible": vis, "ja_partly_visible": part, "en_fully_visible": en_vis,
                                       "ja_fully_visible_rate": round(vis / n, 3) if n else None, "skipped_not_stable": skipped}
            browser.close()
        return out
    finally:
        if srv:
            srv.shutdown()


def main(argv):
    import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
    dirs = [a for a in argv if not a.startswith("--") and (not argv or argv[argv.index(a) - 1] not in ("--out", "--base-url"))]
    out_path = argv[argv.index("--out") + 1] if "--out" in argv else None
    base_url = argv[argv.index("--base-url") + 1] if "--base-url" in argv else None
    res = {}
    with sync_playwright() as p:
        for d in dirs:
            res[Path(d).name] = measure_dir(p, Path(d).resolve(), base_url)
            print(Path(d).name, json.dumps(res[Path(d).name], ensure_ascii=False))
    if out_path:
        Path(out_path).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
