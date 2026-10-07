# -*- coding: utf-8 -*-
"""段階1操作確認表の生成(決定論)。入力: eval/brief_features.json + eval/stage1_manual_review.json(実行者の目視記録・非盲検)。
出力: eval/STAGE1_BRIEF_CHECK.md"""
import json, os
E = "er052_output/open233_b3_trial_01/eval"
F = json.load(open(E + "/brief_features.json", encoding="utf-8"))["briefs"]
M = json.load(open(E + "/stage1_manual_review.json", encoding="utf-8"))["briefs"]
VS = ["V0", "V1", "V2", "V3", "V6"]
TH = ["meta", "hormuz", "space_weapons"]


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def fm(v, d=2):
    return "-" if v is None else ("%." + str(d) + "f") % v


def rows(keys):
    n = len(keys)
    f = [F[k] for k in keys]
    m = [M[k] for k in keys]
    ut = sum(x["units_total"] for x in m)
    om = sum(x["omitted_units"] for x in m)
    return {"n": n, "facts": mean([x["n_fact_manual"] for x in m]), "lines": mean([x["lines"] for x in f]), "chars": mean([x["chars"] for x in f]),
            "g_led": mean([x["ledger_12gram_rate"] for x in f]), "g_notes": mean([x["notes_12gram_rate"] for x in f]),
            "neg_units": sum(x["neg_form_units"] for x in f), "neg_derived": sum(x["neg_note_derived_units"] for x in f),
            "story_link": mean([x["story_facts_linked"] for x in m]), "cross": sum(1 for x in m if x["cross_fact_qualifier"]),
            "units": ut, "omit": om, "rate": (om / ut) if ut else None}


H = ("| 区分 | briefs | 採用fact数 | 行数 | 文字数 | 12字一致率(台帳) | 12字一致率(notes) | 否定形文(件) | 否定形notes由来(件) | "
     "Storyline連結fact数 | Storyline別fact連結あり | 目視単位数 | 省略単位数 | 省略率 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(name, r):
    return "| %s | %d | %s | %s | %s | %s | %s | %d | %d | %s | %d/%d | %d | %d | %s |" % (
        name, r["n"], fm(r["facts"]), fm(r["lines"], 1), fm(r["chars"], 0), fm(r["g_led"]), fm(r["g_notes"], 3), r["neg_units"], r["neg_derived"],
        fm(r["story_link"]), r["cross"], r["n"], r["units"], r["omit"], fm(r["rate"]))


keys = lambda v=None, t=None, b=None: [k for k in sorted(F) if (v is None or k.split("|")[1] == v) and (t is None or k.split("|")[0] == t) and (b is None or k.endswith("|b%d" % b))]
L = ["# STAGE1_BRIEF_CHECK: B3 brief 操作確認表 (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 段階1、V0/V1/V2/V3/V6 x 3テーマ x 2 = 30本)",
     "", "決定論列(行数/文字数/12字一致率/否定形。採用fact数は段落形式のbriefで決定論のn_factが過小になるため目視の実数)は `docs/pm/b3_trial_01/brief_features.py`。目視列(Storyline連結fact数/別fact連結/目視単位数/省略単位数)は実行者(variantを知っている)による非盲検の操作確認(`eval/stage1_manual_review.json`)であり、"
     "M5の正式brief_review(別インスタンス・匿名)の代替ではない。V5は未実行。",
     "", "目視定義(固定): 単位=Selected Factsの箇条書き1項目、または句点区切り1文(Storyline節とSelected Facts内に複写されたStoryline文は単位外)。省略単位=台帳文にある主体(報道主体・発言者含む)・対象・数値/率の掛かる先・方向語が、削除または上位/曖昧語へ置換されている単位(台帳自体が曖昧な箇所は数えない)。"
     "Storyline別fact連結=Storyline文が2件以上のfactの限定語・条件を1文に連結して一つの主張にしているか(Storyline連結fact数=その文に反映されたfactの数)。", "",
     "## 条件別(全テーマ合算)", H]
for v in VS:
    L.append(line(v, rows(keys(v))))
for t in TH:
    L += ["", "## テーマ別: %s" % t, H]
    for v in VS:
        L.append(line(v, rows(keys(v, t))))
for b in (1, 2):
    L += ["", "## b%d のみ(全テーマ合算)" % b, H]
    for v in VS:
        L.append(line(v, rows(keys(v, None, b))))
L += ["", "## 判定(条件別: 効いている/効いていない/不明)", "",
      "N=6 brief/条件の小標本で、効果の大きさでなく操作が効いたかの確認。基準=設計の操作確認(V1/V3で省略率<V0、V2で連結減、V6で省略率・言い換え増)。", "",
      "| 条件 | 判定 | 根拠(全テーマ合算、b1/b2とも同方向か) |", "|---|---|---|",
      "| V1 | 効いている(床効果あり) | 省略率0.00(0/24)<V0 0.09(2/22)、b1/b2とも0.00<0.09。ただしV0側の省略が元々2単位と少なく差は小さい。12字一致率(台帳)0.81 vs 0.34で逐語化が大きく進む=H4共変量(Opus注意点2)が同時に動く。 |",
      "| V2 | 効いていない/弱い(不明寄り) | 別fact連結あり5/6 vs V0 6/6、Storyline連結fact数3.17 vs 3.67(採用fact数も3.17 vs 3.67に減る)。V0とほぼ同じ連結で、b2ではV2の連結数がV0と同じ3/3。省略率は0.16でV0より高い(V2は省略を狙っていないので想定内)。 |",
      "| V3 | 効いている(副作用あり) | 省略率0.00(0/17)<V0、連結あり3/6 vs 6/6(b1 2/3、b2 1/3)で両repとも減。ただし採用fact数2.50 vs 3.67、行数6.3 vs 8.0と大きく減る(単一因果化がfact削減を伴う)。space_weapons b2は採用1件に縮退。 |",
      "| V6 | 効いている(操作確認OK) | 省略率0.59(13/22)>V0 0.09(b1 0.67、b2 0.50で同方向)、12字一致率(台帳)0.18 vs 0.34、文字数416 vs 636=言い換え・短縮が増えた。 |", ""]
open(E + "/STAGE1_BRIEF_CHECK.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("\n".join(L))
