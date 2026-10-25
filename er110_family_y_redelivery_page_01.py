# -*- coding: utf-8 -*-
"""er110_family_y_redelivery_page_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_27: 『宅配の再配達は有料にすべきか?』音声化Trialの限定試聴ページ生成(API 0、DEV/Trial専用)。

既存の標準形式 er110_family_y_audio_page_01(5パート版)の部品を、出力先・人物ラベル・日本語原稿の読み先だけprocess内で差し替えて再利用する。
限定共有: user_test/family_y_redelivery_audio_01/ (一覧・indexからリンクしない)、`<meta name="robots" content="noindex,nofollow">`、
ページ冒頭に『Trial・限定試聴・権利確認前のため転載不可』注記。出典URL・出典の引用文は載せない。
"""
from __future__ import annotations

import glob
import json
import os
import re

import er110_family_y_audio_page_01 as pg1
import er110_family_y_redelivery_audio_01 as rd

ROOT = os.path.dirname(os.path.abspath(__file__))
esc = pg1.esc

PERSON = {
    "full_story_part1": ("語り手(リード)", "女性ナレーター"),
    "full_story_part2": ("人物1: 現役の宅配ドライバー", "男性の声"),
    "full_story_part3": ("人物2: 共働きで家を空ける時間が長い受取人", "女性の声"),
    "full_story_part3_c2": ("人物3: 営業所やロッカーで受け取る工夫をしている受取人", "男性の声"),
    "full_story_part3_c3": ("語り手(まとめ)", "女性ナレーター"),
}


def _ja_paras() -> list:
    import er110_family_y_text_trial_01 as y0
    t = open(os.path.join(ROOT, rd.RD, "y_writer", "gate_r0", "article_final.md"), encoding="utf-8").read()
    return y0.parse_article(t)["paragraphs"]


def _ja_original(cand, idx):
    ps = _ja_paras()
    return ps[idx] if idx < len(ps) else ""


def cards_html():
    names = {"voice_1": "人物1(男性の声)", "voice_2": "人物2(女性の声)", "voice_3": "人物3(男性の声)"}
    rows = "".join(f"<tr><td><b>{esc(names[s])}</b><br>{esc(rd.SHEETS_R[s]['label'])}</td><td>{esc(rd.SHEETS_R[s]['claim'])}</td></tr>" for s in rd.SLOTS)
    return ("<details open><summary><b>3人の人物ラベルと立場の要点</b></summary><table><thead><tr><th>人物(声)</th><th>立場の要点(日本語R0の趣旨)</th></tr></thead><tbody>"
            + rows + "</tbody></table></details>")


def apply_overrides():
    pg1.WEB = os.path.join(ROOT, rd.WEB_DIR)
    pg1.AUD = os.path.join(pg1.WEB, "audio")
    pg1.THEME = os.path.join(ROOT, rd.AUDIO_ROOT)
    pg1.SRC_ROOT = os.path.join(ROOT, rd.RD)
    pg1.PERSON = PERSON
    pg1.CAND_LABEL = {"r0": "3人の声"}
    pg1.CAND_DESC = {"r0": "日本語R0(確定済み・無変更)を英訳した、リード+人物3人+まとめの5パート構成です。"}
    pg1._ja_original = _ja_original
    pg1.cards_html = cards_html


JS = ("<script>var L='std';function show(){for(const s of document.querySelectorAll('section.lv')){s.classList.toggle('hidden',s.id!=='r0_'+L);}"
      "for(const b of document.querySelectorAll('.tabs button')){b.classList.toggle('on',b.dataset.k===L);}history.replaceState(null,'','#'+L);}"
      "document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{L=b.dataset.k;show();});"
      "(function(){const h=location.hash.slice(1);if(h==='std'||h==='adv'){L=h;}show();})();</script>")


def main():
    apply_overrides()
    os.makedirs(pg1.AUD, exist_ok=True)
    for f in glob.glob(os.path.join(pg1.AUD, "*.mp3")):
        os.remove(f)
    built, secs = {}, []
    for lvl in ("a2", "b1b"):
        if not glob.glob(os.path.join(pg1.THEME, rd.CAND, lvl, "assembled", "*.wav")):
            raise SystemExit(f"{lvl}: 組立済み全編音声がありません(Gateを回避して通し音声は作りません)")
        d = pg1.build_level(rd.CAND, lvl)
        built[(rd.CAND, lvl)] = d
        secs.append(pg1.section(rd.CAND, lvl, d))
    title = "宅配の再配達は有料にすべきか?(Family Y・3人の声)限定試聴ページ"
    tabs = "<div class='tabs'><button data-k='std'>Standard</button><button data-k='adv'>Advanced</button></div>"
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name=\"robots\" content=\"noindex,nofollow\"><title>{esc(title)}</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{pg1.CSS}</head><body><h1>{esc(title)}</h1>"
          "<div class='trial'>Trial・限定試聴・権利確認前のため転載不可。一般公開ではありません。このページのURLを共有・転載しないでください。"
          "正式採用は決まっていません(Production採用・配線なし)。</div>"
          "<div class='note'>ネットなどで公開されている複数の意見をもとに組み立てた、実在の特定の人ではない3人の声です。同じ問い「宅配の再配達は有料にすべきか?」を、"
          "現役の宅配ドライバー、共働きの受取人、受け取り方を工夫している受取人の3人が、それぞれ自分の言葉で語ります。英訳と音声の品質、3人の聞き分けやすさを確かめるための試聴ページです。"
          "上のボタンでレベル(Standard/Advanced)を切り替えられます。</div>"
          + cards_html() + tabs + "".join(secs) + JS + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    assert not re.search(r"https?://", pg), "出典URL等の外部リンクは載せない"
    with open(os.path.join(pg1.WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    info = {f"{c}_{l}": {"rows": len(d["rows"]), "duration": round(d.get("duration", 0), 1)} for (c, l), d in built.items()}
    print("page written", json.dumps(info))
    chk = pg1.standard_check(built)
    with open(os.path.join(pg1.THEME, "page_standard_check.json"), "w", encoding="utf-8") as f:
        json.dump(chk, f, ensure_ascii=False, indent=1)
    print("standard check:", {c: v["overall"] for c, v in chk.items()})
    for c, v in chk.items():
        for k, cv in v["checks"].items():
            if not cv["ok"]:
                print("  FAIL", c, k, cv["detail"])
    return built


if __name__ == "__main__":
    main()
