# -*- coding: utf-8 -*-
"""blind対比較の準備(API 0、DEV/Trial専用)。前回R0g(baseline)と新稿(final)、新稿1回目(it1)と最終稿(it2)を、順序ランダム・ラベルなしの対にする。
出力: BLIND_PAIRS_01.md(本文のみ・設計意図/Sheet/出典ラベルなし)と BLIND_KEY_01.json(正解キー。別ファイル)。Opusへ渡すのはBLIND_PAIRS_01.mdのみ。"""
import json
import os
import random
import re
import sys

import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p

ROOT = "er110_output/family_y_persona_trial_01/school_phone_ban"
OLD = "er110_output/family_y_trial_01/school_phone_ban"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_02"


def rt(path):
    return open(path, encoding="utf-8").read()


def en_paras(path):
    return p.split_en_article(rt(path))["paragraphs"]


def main(final="it2", first="it1"):
    old_ja = y0.parse_article(rt(f"{OLD}/y_writer/gate_r0/article_final.md"))["paragraphs"]          # [lead,v1,v2,v3,final]
    old_std = en_paras(f"{OLD}/english_r0/a2/article.md")
    old_adv = en_paras(f"{OLD}/english_r0/b1b/article.md")
    f_ja = json.load(open(f"{ROOT}/{final}/gate_voices/final_texts.json", encoding="utf-8"))
    f_t = json.load(open(f"{ROOT}/{final}/gate_tension/final_texts.json", encoding="utf-8"))["tension"]
    f_std = en_paras(f"{ROOT}/{final}/english/a2/article.md")
    f_adv = en_paras(f"{ROOT}/{final}/english/b1b/article.md")
    i_ja = json.load(open(f"{ROOT}/{first}/gate_voices/final_texts.json", encoding="utf-8"))
    j = lambda xs: "\n\n".join(xs)       # noqa: E731
    pairs = [
        ("P1", "日本語・3人の語り(Voice部分のみ)", j(old_ja[1:4]), j([f_ja[s] for s in p.VOICE_SLOTS]), "baseline=前回R0g / final=新稿"),
        ("P2", "英語(Standard)・3人の語り(Voice部分のみ)", j(old_std[1:4]), j(f_std[0:3]), "baseline=前回R0g / final=新稿"),
        ("P3", "英語(Advanced)・3人の語り(Voice部分のみ)", j(old_adv[1:4]), j(f_adv[0:3]), "baseline=前回R0g / final=新稿"),
        ("P4", "日本語・最後のまとめ(1パート)", old_ja[4], f_t, "baseline=前回R0g / final=新稿"),
        ("P5", "英語(Standard)・最後のまとめ(1パート)", old_std[4], f_std[3], "baseline=前回R0g / final=新稿"),
        ("P6", "日本語・3人の語り(Voice部分のみ)", j([i_ja[s] for s in p.VOICE_SLOTS]), j([f_ja[s] for s in p.VOICE_SLOTS]), "first=新稿1回目 / final=新稿最終"),
    ]
    rng = random.Random(20261023)
    key, md = {}, []
    md.append("# BLIND_PAIRS_01: 順序ランダム・ラベルなしの対比較(本文のみ)\n")
    md.append("各対の2つの文章(Text 1 / Text 2)を読み、次の2問に答えてください。どちらが新しい/古いかは伏せてあります。設計意図・人物設定は渡していません。\n")
    md.append("- Q1. どちらのほうが「実在の人が自分の生活から語っている」と感じるか(各語り手の個性・感情・具体性・主張の明確さ)\n"
              "- Q2. どちらのほうが「優等生が丁寧に説明している」感が強いか\n"
              "- Q3(最後のまとめの対のみ P4/P5). 耳で一度聞いて分かりやすいのはどちらか\n"
              "- 回答形式: 対ごとに Q1: Text 1/Text 2、Q2: Text 1/Text 2、(P4/P5のみ Q3)、理由1〜2文\n")
    for pid, desc, a, b, role in pairs:
        flip = rng.random() < 0.5
        t1, t2 = (b, a) if flip else (a, b)
        key[pid] = {"description": desc, "roles": role, "Text 1": "final" if flip else ("baseline" if "baseline" in role else "first"),
                    "Text 2": ("baseline" if "baseline" in role else "first") if flip else "final"}
        md.append(f"\n---\n\n## {pid}({desc.split('・')[0]}・{desc.split('・')[1] if '・' in desc else ''})\n\n### Text 1\n\n{t1}\n\n### Text 2\n\n{t2}\n")
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/BLIND_PAIRS_01.md", "w", encoding="utf-8").write("\n".join(md))
    json.dump({"note": "正解キー(Opusには渡さない)。Text 1/Text 2の正体", "key": key}, open(f"{OUT}/BLIND_KEY_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", {k: (v["Text 1"], v["Text 2"]) for k, v in key.items()})


if __name__ == "__main__":
    main(*sys.argv[1:3])
