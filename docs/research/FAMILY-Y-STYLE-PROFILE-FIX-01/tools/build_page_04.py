# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06: 通常の最終試聴ページ `_03/index.html` 組立(API 0)。

run_style_fix_01/pages(runnerのpages stage出力=通常構成: Std/Adv通し再生+パート別+原稿+Key Phrase等)を
`user_test/family_y_production_redelivery_fee_03/` へ複製し、末尾に『制作情報』節(Voice表・Style・model_id・Gate結果)と
先行版(`preview_segments_01.html`)へのリンク1行だけを足す。旧Style比較・Voice別S9・Take比較の節は置かない。
前提: 先行版は `preview_segments_01.html`(+`preview_audio_01/`)へ退避済み(index.html/audio/が空いていること)。
使い方: .venv/Scripts/python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_04.py
"""
from __future__ import annotations

import html
import json
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUN = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
DEST = "user_test/family_y_production_redelivery_fee_03"
NAMES = {"y_lead": "Lead", "y_intro_1": "Intro 1", "y_voice_1": "Voice 1", "y_intro_2": "Intro 2", "y_voice_2": "Voice 2",
         "y_intro_3": "Intro 3", "y_voice_3": "Voice 3", "y_closing": "Closing"}


def main() -> dict:
    os.chdir(ROOT)
    if os.path.exists(f"{DEST}/index.html") or os.path.exists(f"{DEST}/audio"):
        raise SystemExit("index.html または audio/ が既に存在(先行版の退避が未実施、または実行済み)")
    shutil.copytree(f"{RUN}/pages", DEST, dirs_exist_ok=True, ignore=shutil.ignore_patterns("listening"))
    page = open(f"{DEST}/index.html", encoding="utf-8").read()
    gs = json.load(open(f"{RUN}/gate_summary.json", encoding="utf-8"))
    rows = []
    summ = {}
    for lv, lvname in (("a2", "Standard"), ("b1b", "Advanced")):
        sv = json.load(open(f"{RUN}/{lv}/audit/style_actual_vs_approved.json", encoding="utf-8"))
        summ[lv] = {"profile": sv["profile_id"], "all_match": sv["all_match"], "rows": sv["rows_count"], "coverage": sv["coverage"]}
        if sv["profile_id"] != "fx_20261017" or not sv["all_match"]:
            raise SystemExit(f"Style実測が不一致: {lv}")
        for r in sv["rows"]:
            if r["segment"] in NAMES:
                rows.append(f"<tr><td>{lvname}</td><td>{NAMES[r['segment']]}</td><td>{html.escape(r['voice'])}</td><td>{html.escape(r['model'])}</td>"
                            f"<td>{'一致' if r['match'] else '不一致'}</td></tr>")
    sec = ("<h2 id='production'>制作情報</h2><div class='note'>Voice 1〜3は実在人物の発言ではなく、AIが編集した意見です。"
           f"Style: Family Xから継承した承認済み <b>{html.escape(summ['a2']['profile'])}</b>(全{summ['a2']['rows']}/{summ['b1b']['rows']}件 実測=承認の一致を確認済み、"
           f"Style Gate Standard {gs['a2']['status']} / Advanced {gs['b1b']['status']})。TTSモデル: gemini-3.8-flash-lite-tts。</div>"
           "<details class='aux'><summary>Voice・Style実測の一覧(技術情報)</summary><table><thead><tr><th>level</th><th>部位</th><th>Voice</th><th>model_id</th><th>Style(承認との一致)</th></tr></thead><tbody>"
           + "".join(rows) + "</tbody></table></details>"
           "<p class='sec'>先行公開ページ(制作途中の部位別試聴): <a href='preview_segments_01.html'>preview_segments_01.html</a></p>")
    out = page.replace("</body>", sec + "</body>", 1)
    out = out.replace("<a href='#advanced'>Advanced</a>", "<a href='#advanced'>Advanced</a><a href='#production'>制作情報</a>", 1)
    if "id='production'" not in out or "#production" not in out:
        raise SystemExit("制作情報節の挿入に失敗")
    open(f"{DEST}/index.html", "w", encoding="utf-8").write(out)
    return {"dest": DEST, "style": summ}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=1))
