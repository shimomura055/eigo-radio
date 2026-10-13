# -*- coding: utf-8 -*-
"""委任_03 D 集計(オフライン無料): 一般例+反例の『許容 / NG / HR』3分類判定表。"""
import collections, json, sys
sys.path.insert(0, ".")
import pronouncing
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er021_en_asr_semantic_equivalence_production_01 as _se
_se.append_telemetry_log = lambda *a, **k: None
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
md = []
def pct(a, b): return f"{a}/{b} ({100*a/b:.0f}%)" if b else "-"
# ---- D-1 base rate
br = json.load(open(OUT + "/d_base_rate_02.json", encoding="utf-8"))
md.append("## D-1. 実データ(Production tts_generation_results 2,149 text/ASR対のうち英語2,030対)における、語境界の子音連続の型別 出現数と『綴り差が境界付近に出た割合』\n")
md.append("母集団=Productionが実際に生成しASR照合した英語本文/Key Phrase等。『境界付近の綴り差』は同一対内の差分が境界の前後語に掛かる件数(境界と無関係な差分も含む上限値)。")
md.append("| 境界の型 | 境界数 | 境界付近に綴り差 | 割合(上限) |")
md.append("|---|---|---|---|")
names = {"GEMINATE_SAME": "同一子音の重なり(s+s,t+t,d+d,n+n,l+l,k+k...)", "SIBILANT_SEQ": "歯擦音連続(s+z,z+s)", "SIBILANT_PALATAL": "歯擦音+口蓋歯擦音(s+sh,z+ch...)",
         "YOD_COALESCENCE": "t/d/s/z+y(did you型)", "HOMORGANIC_STOPS": "同位置の破裂音連続", "STOP_STOP_UNRELEASED": "その他の破裂音+破裂音"}
for k, v in br["base_rate"].items():
    md.append(f"| {names.get(k,k)} | {v['n']} | {v['affected']} | {100*v['affected']/v['n']:.1f}% |")
# ---- D-2 実データの差分instance
I = json.load(open(OUT + "/d_instances_02.json", encoding="utf-8"))
md.append("\n## D-2. 実データの境界差分 124 instance(窓=差分語+前後1語)の判定: 現行Production vs Trial音韻判定\n")
md.append("| Trial音韻判定 | 件数 | 現行Production判定の内訳 |")
md.append("|---|---|---|")
for v in ("PHON_EXPLAINED_FUSION", "PHON_EXPLAINED_VOICING", "PHON_HOMOPHONE_ONLY", "NO_PHONOLOGICAL_EVIDENCE", "NOT_EXPLAINED"):
    xs = [i for i in I if i["phon_verdict"] == v]
    c = collections.Counter(i["prod_classification"] for i in xs)
    md.append(f"| {v} | {len(xs)} | {dict(c)} |")
md.append("\n### D-2a. Trialが『連結発音で説明可(FUSION/VOICING)』とした実データinstance全件と、現行Productionの扱い\n")
md.append("| 境界の型 | canonical窓 -> ASR窓 | 現行Production | 現行CS Validator | 現行EqLayer(cheap) | Trial | 出所 |")
md.append("|---|---|---|---|---|---|---|")
for i in I:
    if i["phon_verdict"] in ("PHON_EXPLAINED_FUSION", "PHON_EXPLAINED_VOICING"):
        md.append(f"| {','.join(sorted({e[1] for e in i['env']}))} | `{i['canonical_window']}` -> `{i['asr_window']}` | {i['prod_classification']} | {i['prod_cs_validator'].replace('UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING','UNCLASSIFIED')} | {i['prod_equivalence_cheap']} | {i['phon_verdict']} | {i['src'][:40]} |")
md.append("\n### D-2b. Productionが連結発音として受理(CONNECTED_SPEECH_ACCEPT/PWW)したがTrialでは『説明不能』となったinstance(= Productionの綴り水準規則がTrialの音素水準より広い範囲)\n")
for i in I:
    if i["phon_verdict"] == "NOT_EXPLAINED" and i["prod_classification"].startswith("CONNECTED_SPEECH"):
        md.append(f"- `{i['canonical_window']}` -> `{i['asr_window']}` ({i['prod_classification']}; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])")
# ---- D-3 一般語2語窓 (B-P2-4 の3分類版)
rows = json.load(open(OUT + "/b_records_02.json", encoding="utf-8"))
G = [x for x in rows if x["group"] == "p2_general"]
md.append("\n## D-3. 一般語2語窓(Production採用済み正常音声の実境界を切出し)の3分類: 現行Production vs Trial(独立証拠なし)\n")
md.append("正常音声(Production採用済み)を2語に切り出したclipのため、真値=『正常な連結発音』。許容=綴り一致、HR=音韻説明可だが綴り不一致、NG=連結発音で説明不能(=ASRの別語化)。")
md.append("| 型 | engine | 観測 | 現行Production PASS | Trial 許容(綴り一致) | Trial HR | Trial NG(説明不能) |")
md.append("|---|---|---|---|---|---|---|")
for ty in ("SS", "TT", "DD", "NN", "YOD", "SHS", "CTRL"):
    for eng in ("openai", "azure", "whisper:small", "whisper:medium"):
        xs = [x for x in G if x["cat"] == ty and x["engine"] == eng]
        if not xs: continue
        tw = collections.Counter(P.three_way(P.explain_diff(x["canon"], x["region"]) if x["region"].strip() else {"verdict": "NOT_EXPLAINED"})["class"] for x in xs)
        md.append(f"| {ty} | {eng} | {len(xs)} | {pct(sum(x['prod_pass'] for x in xs), len(xs))} | {pct(tw['許容'], len(xs))} | {pct(tw['HR'], len(xs))} | {pct(tw['NG'], len(xs))} |")
allx = [x for x in G if x["cat"] != "CTRL"]
tw = collections.Counter(P.three_way(P.explain_diff(x["canon"], x["region"]) if x["region"].strip() else {"verdict": "NOT_EXPLAINED"})["class"] for x in allx)
md.append(f"\n融合型(SS/TT/DD/NN/YOD/SHS)全体 n={len(allx)}: 現行Production PASS {pct(sum(x['prod_pass'] for x in allx), len(allx))} / Trial 許容 {pct(tw['許容'], len(allx))} / HR {pct(tw['HR'], len(allx))} / NG {pct(tw['NG'], len(allx))}")
ctl = [x for x in G if x["cat"] == "CTRL"]
tc = collections.Counter(P.three_way(P.explain_diff(x["canon"], x["region"]) if x["region"].strip() else {"verdict": "NOT_EXPLAINED"})["class"] for x in ctl)
md.append(f"対照(CTRL) n={len(ctl)}: 現行Production PASS {pct(sum(x['prod_pass'] for x in ctl), len(ctl))} / Trial 許容 {pct(tc['許容'], len(ctl))} / HR {pct(tc['HR'], len(ctl))} / NG {pct(tc['NG'], len(ctl))}")
# 非exactの全列挙(融合型)
md.append("\n### D-3a. 融合型で綴り不一致になった観測の全列挙(正常音声のASR別綴り/脱落)\n")
md.append("| 型 | engine | canonical -> ASR | 現行Production | Trial音韻 | Trial 3分類 | 現行CS Validator |")
md.append("|---|---|---|---|---|---|---|")
seen = set()
for x in sorted(allx, key=lambda x: (x["cat"], x["target"], x["engine"])):
    if x["exact"]: continue
    ex = P.explain_diff(x["canon"], x["region"]) if x["region"].strip() else {"verdict": "NOT_EXPLAINED"}
    k = (x["cat"], x["canon"], x["region"])
    if k in seen: continue
    seen.add(k)
    cs = csv3.classify_connected_speech(x["canon"], x["region"])["new_judgment"].replace("UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING", "UNCLASSIFIED") if x["region"].strip() else "-"
    md.append(f"| {x['cat']} | {x['engine']} | `{x['canon']}` -> `{x['region']}` | {x['prod_cls']} | {ex['verdict']} | {P.three_way(ex)['class']} | {cs} |")
# ---- D-4 反例(真の誤発音・語尾欠落・別語)
C = json.load(open(OUT + "/c_records_02.json", encoding="utf-8"))
md.append("\n## D-4. 反例(真値既知)の判定: 誤って『許容』にされないか\n")
md.append("出所: 委任_01 synthetic(既知欠陥を編集した音声)・natural_ng proxy・Melos 反例ASR。独立証拠を最大(音響OK+別engine一致)と仮定しても許容になるかを見る。")
ev_max = {"acoustic_geminate_ok": True, "second_engine_exact": True}
md.append("既知欠陥の観測に対し、Trial規則が**新たに**許容を増やすか(増分誤許容 = 現行ProductionがPASSにしない観測のうち、Trial(独立証拠最大)が許容にした数)を見る。")
md.append("| 群/欠陥種別 | 観測数 | 現行Production PASS(既存の誤許容) | Trial許容(証拠なし) | Trial許容(証拠最大) | 増分誤許容(証拠最大, 現行非PASS->許容) | 増分(例) |")
md.append("|---|---|---|---|---|---|---|")
cats = [("synthetic", "synthetic_final_consonant_loss"), ("synthetic", "synthetic_missing_word"), ("synthetic", "synthetic_wrong_name"), ("synthetic", "intact_control"),
        ("natural_ng", "proper_noun_mispronounced"), ("natural_ng", "final_consonant_added"), ("natural_ng", "context_guessable_homophone"),
        ("natural_ng", "final_consonant_drop"), ("natural_ng", "content_mispronounced")]
tot_inc = 0
for g, cat in cats:
    xs = [r for r in C if r["group"] == g and r["category"] == cat and r["src"] == "委任_01" and r["variant"] == "base" and r["region"].strip()]
    if not xs: continue
    t0 = [P.three_way(P.explain_diff(r["canon"], r["region"]))["class"] for r in xs]
    t1 = [P.three_way(P.explain_diff(r["canon"], r["region"]), ev_max)["class"] for r in xs]
    inc = [(r["canon"], r["region"]) for r, c in zip(xs, t1) if c == "許容" and not r["prod_pass"]]
    if cat != "intact_control": tot_inc += len(inc)
    md.append(f"| {g}/{cat} | {len(xs)} | {sum(r['prod_pass'] for r in xs)} | {t0.count('許容')} | {t1.count('許容')} | {len(inc)} | {sorted(set(inc))[:3]} |")
md.append(f"\n既知欠陥(intact_control除く)に対する増分誤許容 合計: **{tot_inc}** 件。intact_controlは欠陥のない対照で、増分許容=正しい救済。")
md.append("注: syn_B1_trunc*(`said`語末の切詰)は`Melos`のs+s領域に欠陥が無く、ASR転写はintactと同一(`mello said`)。Trial規則は語末切詰を検出も誤許容の増分も生まない(現行と同じ『ASR文字列では検出されない』限界はそのまま)。")
open(OUT + "/analysis_d_02.md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
