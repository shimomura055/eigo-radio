# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02: 公開 `_03` ページ組立(API 0)。

run_style_fix_01/pages(runnerのpages stage出力)を user_test/family_y_production_redelivery_fee_03/ へ複製し、先頭に『比較節』を挿入する:
  - Voice 1〜3(Standard/Advanced 6 segment)を旧`_02`(default Style)と新版(承認PD06)で並べて個別再生(S9未評価・ユーザー判断項目。Opus M-3)
  - 話速WPM前後表(Opus R-1)
  - 部位別Style前後表(全segment: 旧prefix→新prefix・再生成/再利用)
旧`_01`/`_02`は一切変更しない(読み取りのみ)。旧音声は `_03/compare_old/` へ複製して自己完結にする。
使い方: .venv\\Scripts\\python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_03.py [--dest DIR] [--check-only]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUN = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
OLD = "user_test/family_y_production_redelivery_fee_02"
DEST = "user_test/family_y_production_redelivery_fee_03"
EVID = "docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/regen_evidence_01.json"
WPM = "docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/wpm_01.json"
ROW = re.compile(r"<tr><td><b>([^<]*)</b><br><span class='sec'>([^<]*)</span>.*?src='(audio/[a-z0-9_]+\.mp3)'", re.S)
STYLE_LABEL = {"3a680861": "PD06(承認:本文)", "060c08fd": "S3(承認:日本語補助)", "8862317f": "E1(承認:Adv Preview)", "9d905cfe": "K2(承認:KP英語)",
               "b12c8721": "P8-KP(承認:KP日本語意味)", "05180006": "P7(承認:KP英語解説)",
               "07d72dd6": "旧default(Adv本文)", "9293e0c3": "旧default(Std本文・減速指示連結)", "ae68e3e6": "旧default(日本語)", "2b0c7505": "旧default(KP英語)",
               "f44ef4e2": "旧default(KP解説)", "57c3fda6": "基底(Adv英語・変更なし)", "d16e099c": "基底(Topic intro・変更なし)"}


def _rows(page: str) -> list:
    return [(m.group(1), m.group(3)) for m in ROW.finditer(page)]


def _voice_map(page: str) -> dict:
    """{('std'|'adv', n): 'audio/xxx.mp3'} for 'Full Story: Voice n'(Introductionは除く)。"""
    out = {}
    for label, src in _rows(page):
        m = re.fullmatch(r"Full Story: Voice ([123])", label)
        if m:
            out[("std" if "/std_" in src else "adv", int(m.group(1)))] = src
    return out


def _style_cell(rec):
    if not rec or not rec.get("style"):
        return "-"
    s = rec["style"]["sha8"]
    return f"{STYLE_LABEL.get(s, s)} <span class='sec'>[{s}/{rec['style']['len']}字]</span>"


def build(dest: str, check_only: bool = False, pages: str | None = None) -> dict:
    os.chdir(ROOT)
    new_pages = pages or f"{RUN}/pages"
    page = open(f"{new_pages}/index.html", encoding="utf-8").read()
    old_page = open(f"{OLD}/index.html", encoding="utf-8").read()
    nv, ov = _voice_map(page), _voice_map(old_page)
    need = {(lv, n) for lv in ("std", "adv") for n in (1, 2, 3)}
    if set(nv) != need or set(ov) != need:
        raise SystemExit(f"Voice行の抽出に失敗: new={sorted(nv)} old={sorted(ov)}")
    wpm, evid = json.load(open(WPM, encoding="utf-8")), json.load(open(EVID, encoding="utf-8"))
    if check_only:
        return {"voice_rows": len(nv)}
    if os.path.exists(dest):
        raise SystemExit(f"{dest} が既に存在します(上書きしない)")
    shutil.copytree(new_pages, dest, ignore=shutil.ignore_patterns("listening"))
    os.makedirs(f"{dest}/compare_old", exist_ok=True)
    rows_html = []
    for lv, lvname, key in (("std", "Standard", "a2"), ("adv", "Advanced", "b1b")):
        for n in (1, 2, 3):
            old_rel = f"compare_old/{lv}_voice{n}_old_default.mp3"
            shutil.copyfile(f"{OLD}/{ov[(lv, n)]}", f"{dest}/{old_rel}")
            w = wpm[f"{key}:y_voice_{n}"]
            rows_html.append(
                f"<tr><td><b>{lvname} / Voice {n}</b></td>"
                f"<td class='play'><audio controls preload='none' src='{old_rel}'></audio><br><span class='sec'>旧 `_02`(default Style)</span></td>"
                f"<td class='play'><audio controls preload='none' src='{nv[(lv, n)]}'></audio><br><span class='sec'>新 `_03`(承認Style PD06)</span></td>"
                f"<td>{w['old_sec']}秒 → {w['new_sec']}秒<br><span class='sec'>{w['words']}語 / WPM {w['old_wpm']} → {w['new_wpm']}</span></td></tr>")
    style_rows = []
    for lv, lvname in (("a2", "Standard"), ("b1b", "Advanced")):
        for r in evid[lv]:
            if r["segment"].startswith("kp") and "phrase_repeat" in r["segment"]:
                continue
            n, o = r["new"], r["old"]
            changed = bool(n and o and n.get("style") and o.get("style") and n["style"]["sha8"] != o["style"]["sha8"])
            style_rows.append(f"<tr><td>{lvname}</td><td>{html.escape(r['segment'])}</td><td>{_style_cell(o)}</td><td>{_style_cell(n)}</td>"
                              f"<td>{'Style変更→再生成' if changed else 'Style不変(新runでも再生成)'}</td><td>{(n or {}).get('voice') or '-'}</td></tr>")
    section = (
        "<h2 id='compare'>旧版(`_02`)との比較: Voice 1〜3の聞こえ方(ユーザー判断項目)</h2>"
        "<div class='note'><b>S9未評価・ユーザー判断項目</b><br>"
        "承認済みの本文Style(PD06: 「smile in your voice」「reassuring」「like a favorite morning radio host」)を、"
        "ナレーターだけでなくVoice 1〜3の人物本文にも適用しています(承認記録A19/T10に基づく)。ただしこのStyleは司会者向けの文言で、"
        "批判的・不満を述べる人物の語りを平板にする可能性があります。承認時の条件「S9(人物の聞こえ方)を試聴で確認する」は未実施です。"
        "下の6組を聴き比べ、(a)新版のまま(PD06をVoice本文にも適用) (b)Voice本文だけ旧default Styleへ戻す(再生成の見込み: 約8円・約30分) のどちらかをご判断ください。</div>"
        "<table><thead><tr><th>音声</th><th>旧(default Style)</th><th>新(承認PD06)</th><th>長さ・話速</th></tr></thead><tbody>"
        + "".join(rows_html) + "</tbody></table>"
        "<details class='aux'><summary>部位別Style 前後表(全segment)</summary><table><thead><tr><th>level</th><th>segment</th><th>旧</th><th>新</th><th>区分</th><th>Voice</th></tr></thead><tbody>"
        + "".join(style_rows) + "</tbody></table></details>")
    out = page.replace("<h2 id='standard'>", section + "<h2 id='standard'>", 1)
    out = out.replace("<nav><a href='#standard'>", "<nav><a href='#compare'>旧版との比較</a><a href='#standard'>", 1)
    if out == page or "id='compare'" not in out:
        raise SystemExit("比較節の挿入に失敗")
    with open(f"{dest}/index.html", "w", encoding="utf-8") as f:
        f.write(out)
    return {"dest": dest, "voice_rows": len(rows_html), "style_rows": len(style_rows)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--pages", default=None, help="入力pages dir(既定=run_style_fix_01/pages。テスト用)")
    a = ap.parse_args()
    print(json.dumps(build(a.dest, a.check_only, a.pages), ensure_ascii=False))
