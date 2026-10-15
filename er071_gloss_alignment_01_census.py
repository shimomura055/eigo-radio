# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-PRODUCTION-01 OF-231/234(b): 記録済みkeywords_canonicalized.jsonから再整合対象を集計(API 0円)。
出力: er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/census_01.json
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_gloss_alignment_01_census.py"""
# KGCPW 委任_02 (OF-KGCPW-13): 撤去済みlegacy方式に依存する過去証跡script。冒頭で停止する(有料APIを叩く前に落とす)。
raise SystemExit("HISTORICAL: 過去証跡(KP-GLOSS-ALIGNMENT Trial/census/replay)の再現用scriptです。KGCPW(2026-10-15)でlegacy方式(slot/fallback/mode)を撤去し修正版が唯一の方式になったため再実行不能・実行すると有料APIを叩く前に停止します(OF-KGCPW-13)。")
import glob, json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_gloss_alignment as ga
import er003_key_words_canonicalization as kc

OUT = "er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/census_01.json"
SLOT = ga.SLOT_TOKENS


def corpora():
    groups = {"M2P0_family_z_er073": "er073_output/**/keywords_canonicalized.json",
              "M2P0_coffee_er019_er071": None,
              "all_er_output": "er*_output/**/keywords_canonicalized.json"}
    return groups


def load(pattern):
    out = []
    for p in sorted(glob.glob(pattern, recursive=True)):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("items"), list):
            out.append((p.replace("\\", "/"), d["items"]))
    return out


def analyze(recs):
    n_items = n_rec = n_target = n_rec_with_target = 0
    uniq = {}
    shorter = []   # OF-234(b): KPがdisplayより短い/display内容語がKPに無い
    stale_slot = []  # OF-230相当: KPにスロット語なしでgloss「～」
    for p, items in recs:
        n_rec += 1
        t = ga.select_alignment_targets(items)
        n_items += len(items)
        n_target += len(t)
        if t:
            n_rec_with_target += 1
        for it in items:
            k = (it.get("display_phrase"), it.get("key_phrase"), it.get("japanese_gloss"))
            if it in t:
                uniq.setdefault(k, (p, it))
            dp, kp = it.get("display_phrase") or "", it.get("key_phrase") or ""
            dtoks = [x for x in ga._TOKEN_RE.findall(kc._normalize_for_match(dp)) if x not in ga._GENERIC_TOKENS and x not in {"a","an","the"}]
            ktoks = set(ga._TOKEN_RE.findall(kc._normalize_for_match(kp)))
            missing = [x for x in dtoks if ga._stem(x) not in {ga._stem(y) for y in ktoks} and not any(__import__("difflib").SequenceMatcher(None, ga._stem(x), ga._stem(y)).ratio() >= 0.7 for y in ktoks)]
            if missing and kc._normalize_for_match(dp) != kc._normalize_for_match(kp):
                shorter.append({"file": p, "rank": it["rank"], "display": dp, "kp": kp, "gloss": it.get("japanese_gloss"), "missing_display_words": missing})
            if ga.gloss_has_unjustified_slot(kp, it.get("japanese_gloss")):
                stale_slot.append({"file": p, "rank": it["rank"], "display": dp, "kp": kp, "gloss": it.get("japanese_gloss")})
    return {"records": n_rec, "items": n_items, "targets": n_target, "records_with_target": n_rec_with_target,
            "unique_target_triples": [{"display": k[0], "kp": k[1], "gloss": k[2], "file": v[0]} for k, v in uniq.items()],
            "kp_shorter_than_display_items": shorter, "tilde_gloss_without_kp_slot_items": stale_slot}


res = {}
m2 = load("er073_output/**/keywords_canonicalized.json")
coffee = load("er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/**/keywords_canonicalized*.json") + \
    load("er071_output/**/keywords_canonicalized.json")
allr = load("er*_output/**/keywords_canonicalized.json")
res["M2P0_family_z_er073"] = analyze(m2)
res["M2P0_coffee_er019_er071"] = analyze(coffee)
res["all_er_output"] = analyze(allr)
# 重複排除(display,kp,gloss)のunique三つ組数
tri = {(it.get("display_phrase"), it.get("key_phrase"), it.get("japanese_gloss")) for _, its in allr for it in its}
res["all_unique_triples"] = len(tri)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    if isinstance(v, dict):
        print(k, {x: (y if not isinstance(y, list) else len(y)) for x, y in v.items()})
    else:
        print(k, v)
