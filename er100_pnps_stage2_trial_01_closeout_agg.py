# -*- coding: utf-8 -*-
"""Closeout (A) 集計: prod_judge_replay.json -> baseline_table.json (API 0)。"""
import collections, json
CL = "er100_output/pnps_stage2_trial_01/closeout"
R = json.load(open(CL + "/prod_judge_replay.json", encoding="utf-8"))
items = R["items"]
HR = lambda v: v["verdict"] == "NG_HR"
PS = lambda v: v["verdict"].startswith("PASS")
t1 = [i for i in items if i["set"] == "r2_take1"]
t2 = {i["id"]: i for i in items if i["set"] == "r2_take2"}
out = {}
# (i) 独立30 segment (現行TTS take1)
by = collections.defaultdict(lambda: collections.Counter())
for i in t1:
    by[i["word"]][i["verdict"]] += 1
out["i_take1_30seg"] = {"by_word_verdict": {w: dict(c) for w, c in by.items()},
    "HR_total_all": sum(HR(i) for i in t1), "HR_excl_melos": sum(HR(i) for i in t1 if i["word"] != "melos"),
    "melos_HR": sum(HR(i) for i in t1 if i["word"] == "melos"),
    "PASS": sum(i["verdict"] == "PASS" for i in t1), "PASS_WITH_WARNING": sum(i["verdict"] == "PASS_WITH_WARNING" for i in t1),
    "HR_ids_excl_melos": [(i["id"], i["word"]) for i in t1 if HR(i) and i["word"] != "melos"],
    "melos_ids": [(i["id"], i["verdict"], i.get("reason_code")) for i in t1 if i["word"] == "melos"],
    "reason_codes": {f"{k[0]}|{k[1]}": v for k, v in collections.Counter((i["verdict"], i.get("reason_code")) for i in t1).items()},
    "m1_accepted_count": sum(i["m1_accepted"] for i in t1), "errors": sum(i["verdict"] == "ERROR" for i in t1)}
# take2 replication
rep = []
for i in t1:
    if i["id"] in t2:
        rep.append((i["id"], i["word"], i["verdict"], t2[i["id"]]["verdict"]))
out["i_take2_replication"] = {"n": len(rep), "rows": rep,
    "HR_t1": sum(r[2] == "NG_HR" for r in rep), "HR_t2": sum(r[3] == "NG_HR" for r in rep),
    "HR_both": sum(r[2] == "NG_HR" and r[3] == "NG_HR" for r in rep),
    "HR_either": sum(r[2] == "NG_HR" or r[3] == "NG_HR" for r in rep)}
# 現行TTS総音声(take1+take2) 語別
allcur = t1 + list(t2.values())
c2 = collections.defaultdict(collections.Counter)
for i in allcur:
    c2[i["word"]][i["verdict"]] += 1
out["i_all_current_tts_audio_by_word"] = {w: dict(c) for w, c in c2.items()}
# 負例
neg = [i for i in items if i["set"] == "r2_neg"]
out["neg_false_pass_check"] = {"n": len(neg), "verdicts": dict(collections.Counter(i["verdict"] for i in neg)),
    "kinds": dict(collections.Counter((i["kind"], i["verdict"]) for i in neg)).__repr__(),
    "passed_items": [(i["id"], i["kind"], i["verdict"], i["primary"], i["azure"]) for i in neg if PS(i)]}
# (ii) Khaite型 R arm
r3 = [i for i in items if i["set"] in ("r3", "r3b")]
arms = collections.defaultdict(collections.Counter)
for i in r3:
    arms[(i["word"], i["arm"], bool(i["wrong_supply"]))][i["verdict"]] += 1
out["ii_r3_by_word_arm"] = {f"{k[0]}/{k[1]}{'(wrong)' if k[2] else ''}": dict(v) for k, v in arms.items()}
kh_R = [i for i in r3 if i["word"] == "khaite" and i["arm"] == "R" and not i["wrong_supply"]]
kh_H = [i for i in r3 if i["word"] == "khaite" and i["arm"] == "H" and not i["wrong_supply"]]
kt1 = {i["id"]: i for i in t1 if i["word"] == "khaite"}
measured_segs = sorted({i["id"].split("_")[0] for i in kh_R})
seg_tab = []
for s in measured_segs:
    base = kt1[s]
    rs = [i["verdict"] for i in kh_R if i["id"].startswith(s + "_")]
    hs = [i["verdict"] for i in kh_H if i["id"].startswith(s + "_")]
    seg_tab.append({"seg": s, "base_current_prod": base["verdict"], "R_takes": rs, "H_takes": hs})
khaite_base_hr = [i["id"] for i in t1 if i["word"] == "khaite" and HR(i)]
unmeasured = [s for s in khaite_base_hr if s not in measured_segs]
rescued_measured = [t for t in seg_tab if t["base_current_prod"] == "NG_HR" and all(v.startswith("PASS") for v in t["R_takes"]) and t["R_takes"]]
out["ii_khaite_rescue"] = {"khaite_segments_HR_under_prod_take1": khaite_base_hr, "measured_segments_table": seg_tab,
    "measured_rescued_(HR->R all takes pass)": [t["seg"] for t in rescued_measured],
    "measured_rescued_count": len(rescued_measured),
    "estimated_same_type_untested_HR_segments": unmeasured, "estimated_count": len(unmeasured),
    "note": "推定=同型(Khaiteの綴り置換で追従)と仮定した未測定のKhaite HR segment。実測と分けて扱う。"}
# 誤供給対照
wrong = [i for i in r3 if i["wrong_supply"]]
out["ii_wrong_supply_controls"] = [(i["id"], i["verdict"], i["primary"], i["azure"]) for i in wrong]
# (iii) 保存HR 58
st = {}
for s in R["stored"]:
    st.setdefault(s["row"], s)
rows = list(st.values())
def cell(rs):
    return dict(collections.Counter(r["narr"]["last"]["verdict"] for r in rs))
tab = {}
for name, f in [("all_58", lambda r: True), ("excluded_test_contamination_25", lambda r: r["contamination"]),
                ("substantive_33", lambda r: not r["contamination"])]:
    sub = [r for r in rows if f(r)]
    tab[name] = {"n": len(sub), "last_pair_narr": cell(sub),
                 "last_pair_segid_none": dict(collections.Counter(r["none"]["last"]["verdict"] for r in sub)),
                 "any_pair_narr_passes": sum(r["narr"]["any_pass"] for r in sub)}
    for per, pf in [("pre_M1", lambda r: not r["post_M1"]), ("post_M1", lambda r: r["post_M1"])]:
        s2 = [r for r in sub if pf(r)]
        tab[name][per] = {"n": len(s2), "last_pair_narr": cell(s2), "any_pair_narr_passes": sum(r["narr"]["any_pass"] for r in s2)}
out["iii_stored_58_events"] = tab
sub = [r for r in rows if not r["contamination"]]
bw = collections.defaultdict(collections.Counter)
for r in sub:
    bw[r["word"]][r["narr"]["last"]["verdict"]] += 1
out["iii_substantive_by_word_last_pair_narr"] = {w: dict(c) for w, c in bw.items()}
out["iii_substantive_hr_remaining_by_word_excl_melos"] = {w: c.get("NG_HR", 0) for w, c in bw.items() if w != "melos"}
out["iii_pass_rows_substantive"] = [(r["row"], r["ts"][:10], r["word"], r["narr"]["last"]["verdict"], r["narr"]["last"].get("reason_code"),
                                      r["narr"]["last"].get("final_status")) for r in sub if r["narr"]["last"]["verdict"].startswith("PASS")]
out["iii_secondary_missing_rows"] = [r["row"] for r in rows if not r["narr"]["last"].get("secondary_used", True)]
out["iii_errors"] = [r["row"] for r in rows if r["narr"]["last"]["verdict"] in ("ERROR", "NO_STEPS")]
out["iii_m1_accepted_rows"] = [r["row"] for r in rows if r["narr"]["last"].get("m1_accepted")]
json.dump(out, open(CL + "/baseline_table.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))

# ---- 追加集計(distinct segment・M1後の実HR・r3 NG詳細) ----
ex = {}
sub = [r for r in rows if not r["contamination"]]
hrs = [r for r in sub if r["narr"]["last"]["verdict"] == "NG_HR"]
ex["substantive_33_distinct_canon"] = len({r["canon"] for r in sub})
ex["substantive_HR_29_distinct_canon"] = len({r["canon"] for r in hrs})
ex["substantive_HR_distinct_canon_by_word"] = {w: len({r["canon"] for r in hrs if r["word"] == w}) for w in sorted({r["word"] for r in hrs})}
ex["substantive_HR_events_by_word"] = dict(collections.Counter(r["word"] for r in hrs))
ex["substantive_HR_events_excl_melos"] = sum(1 for r in hrs if r["word"] != "melos")
ex["substantive_HR_distinct_canon_excl_melos"] = len({r["canon"] for r in hrs if r["word"] != "melos"})
ex["post_M1_real_HR_rows"] = [(r["row"], r["ts"], r["word"], r["narr"]["last"]["verdict"]) for r in sub if r["post_M1"]]
ex["pre_M1_resolved_now_by_M1_rows"] = [(r["row"], r["ts"][:10], r["word"]) for r in sub if (not r["post_M1"]) and r["narr"]["last"]["verdict"].startswith("PASS")]
ex["pre_M1_events"] = sum(1 for r in sub if not r["post_M1"])
ex["pre_M1_still_HR"] = sum(1 for r in sub if (not r["post_M1"]) and r["narr"]["last"]["verdict"] == "NG_HR")
ex["melos_substantive_11"] = {"HR_remaining": sum(1 for r in sub if r["word"] == "melos" and r["narr"]["last"]["verdict"] == "NG_HR"),
                              "resolved_by_M1": sum(1 for r in sub if r["word"] == "melos" and r["narr"]["last"]["verdict"].startswith("PASS"))}
ex["r3_khaite_R_NG_items"] = [(i["id"], i["take"], i["primary"], i["azure"], i.get("reason_code")) for i in kh_R if HR(i)]
ex["r3_altuzarra_N_H_pass"] = [(i["id"], i["arm"], i["take"], i["verdict"]) for i in r3 if i["word"] == "altuzarra" and PS(i)]
out["extra"] = ex
json.dump(out, open(CL + "/baseline_table.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ex, ensure_ascii=False, indent=1))
