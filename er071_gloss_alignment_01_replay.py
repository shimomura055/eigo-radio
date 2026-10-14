# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-PRODUCTION-01 OF-231/232: gloss再整合の有効性検証(実API少額、予算JPY10)。
実対象(R: 記録済みA'/census由来の再整合対象7件を2回)・対照(C: KP==displayで整合済み10件、過剰書換え検査)・
スロット罠(S: KPにスロット語があり「～」が正当なもの)を、Production関数(ga.build_user_message/run_alignment_gate、
承認済み規則抽出+決定論チェック込み)へ強制投入する。1バッチ<=5 item(量産のitem数と同じ規模)。
reasoning effortを引数で切替(high=現行 / medium=比較)。切替提案はしない(結果報告のみ)。
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_gloss_alignment_01_replay.py <effort> <out_json> [budget_jpy]
"""
import glob
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_gloss_alignment as ga
import er003_key_words_canonicalization as kc
import er006_model_routing_contract_01 as routing

DIR = "er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01"
effort = sys.argv[1]
out = sys.argv[2]
budget = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
assert effort in ("high", "medium")

# STOP確認(有料run直前)
rc = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", "KP-GLOSS-ALIGNMENT-PRODUCTION-01",
                     "--run-dir", DIR], capture_output=True, text=True).returncode
if rc != 0:
    print("STOP applicable; no API calls")
    sys.exit(3)

model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
real = json.load(open(f"{DIR}/aprime_targets_01.json", encoding="utf-8"))["unique_targets"]
census = json.load(open(f"{DIR}/census_01.json", encoding="utf-8"))["all_er_output"]["unique_target_triples"]


def item(d, k, g, s, tag):
    return {"rank": 0, "display_phrase": d, "key_phrase": k, "japanese_gloss": g, "source_sentence": s, "_tag": tag}


R = {}
for r in real:
    R[(r["display"], r["kp"], r["gloss"])] = item(r["display"], r["kp"], r["gloss"], r.get("source_sentence") or "", "R")
for c in census:
    key = (c["display"], c["kp"], c["gloss"])
    if c["gloss"] and key not in R:
        # source_sentenceは元recordから補完
        src = ""
        for it in json.load(open(c["file"], encoding="utf-8")).get("items", []):
            if it.get("key_phrase") == c["kp"]:
                src = it.get("source_sentence", "")
        R[key] = item(c["display"], c["kp"], c["gloss"], src, "R")
R = list(R.values())

# 対照C/スロット罠S: er073/er019/er071のM2P0 records + 全record
C, S = [], []
seenC, seenS = set(), set()
for p in sorted(glob.glob("er*_output/**/keywords_canonicalized.json", recursive=True)):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    for it in (d.get("items", []) if isinstance(d, dict) else []):
        g, kp, dp = it.get("japanese_gloss"), it.get("key_phrase"), it.get("display_phrase")
        if not (g and kp and dp and it.get("source_sentence")):
            continue
        if kc._normalize_for_match(kp) == kc._normalize_for_match(dp) and "～" not in g and "〜" not in g \
                and not ga.select_alignment_targets([it]) and kp not in seenC and len(C) < 10:
            seenC.add(kp)
            C.append(item(dp, kp, g, it["source_sentence"], "C"))
        if ga.kp_has_slot_word(kp) and ("～" in g or "〜" in g) and kp not in seenS and len(S) < 5:
            seenS.add(kp)
            S.append(item(dp, kp, g, it["source_sentence"], "S"))

# R x2(安定性) + C + S をバッチ(<=5)に分割
allitems = []
for rep in (1, 2):
    for r in R:
        allitems.append({**r, "_rep": rep})
allitems += [{**c, "_rep": 1} for c in C] + [{**s, "_rep": 1} for s in S]
batches = [allitems[i:i + 5] for i in range(0, len(allitems), 5)]
print(f"effort={effort} model={model} R={len(R)}x2 C={len(C)} S={len(S)} batches={len(batches)}")

cum = 0.0
results = []
for bi, b in enumerate(batches, 1):
    for j, it in enumerate(b, 1):
        it["rank"] = j
    art = "\n".join(x["source_sentence"] for x in b)
    msg = ga.build_user_message(b, art, rules=ga.preflight(True)["rules"])
    by_rank, status, attempts, mid, rid = ga.run_alignment_gate(
        lambda: ga.make_alignment_fn(msg, model=model, reasoning_effort=effort), b)
    cost = round(sum(a.get("cost_jpy") or 0 for a in attempts), 4)
    cum += cost
    print(f"batch {bi}/{len(batches)} status={status} attempts={len(attempts)} cost={cost} cum={cum:.3f}")
    for j, it in enumerate(b, 1):
        row = {"batch": bi, "tag": it["_tag"], "rep": it["_rep"], "display": it["display_phrase"], "kp": it["key_phrase"],
               "gloss_before": it["japanese_gloss"], "gate_status": status}
        if by_rank:
            a = by_rank[j]
            row.update({"gloss_after": a["japanese_gloss"], "verdict_consistent": a["current_gloss_consistent"],
                        "changed": a["japanese_gloss"].strip() != it["japanese_gloss"],
                        "tilde_violation": ga.gloss_has_unjustified_slot(it["key_phrase"], a["japanese_gloss"]),
                        "reasoning": a["reasoning"]})
        else:
            last = attempts[-1] if attempts else {}
            row.update({"gloss_after": None, "failed_reasons": last.get("reasons") or last.get("error")})
        results.append(row)
    if cum > budget:
        print("budget exceeded; stop"); break
json.dump({"effort": effort, "model": model, "total_cost_jpy": round(cum, 4), "n_batches": len(batches),
           "rows": results}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total cost", round(cum, 4))
