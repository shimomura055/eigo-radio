# F1+F2/E3/E4 の「正式runtime発火証拠」を保存済みrun記録(tts_generation_results.json)から集計する(API 0・読取専用)。
# FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03 調査2C。JA(lang=ja)のsegment最終asr_judgementについて、Family(X=er019_output/Z=er026_output/Y=er121_output)×Level(a2=Std/b1b=Adv)×Section別に
#   n(JA segment数) / r5(R-5 telemetry付き=Production commit 58cbf7786以降の判定コードを通った) / final_gate.applied(F1の最終Gateが走った) / f2.enabled / f2.fired / f1_rejected / candidate_e_* 監視field(発火時のみ出る) / state別
# を数える。r5 keyの有無で『07A+R-5以降のコードを通ったか』を判定する(コード存在でなくrun記録の実在で判断)。
# 対象: segment単位の最終judgement(/segments/<seg>, /key_phrases/<n>/japanese_meaning)。japanese_titleのようにSTOPPEDでsegment直下が無い場合は最後のattempts_logを使う。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_asr_wiring_matrix_scan_01.py
import collections, glob, json, re
ROOTS = {"X": "er019_output", "Z": "er026_output", "Y": "er121_output"}
rows = collections.defaultdict(collections.Counter)
runs = collections.defaultdict(set)
newest = {}
def sec_of(name):
    if name.startswith("comment"): return "comment"
    return re.sub(r"_k\d$", "", name)
def add(fam, lvl, sec, j, run, ts):
    r5 = j.get("r5"); key = (fam, lvl, sec); c = rows[key]
    c["n"] += 1; c["state_" + str(j.get("state"))] += 1
    if not r5: return
    c["r5"] += 1; runs[key].add(run); newest[key] = max(newest.get(key, ""), ts or "")
    fg = j.get("final_gate")
    if isinstance(fg, dict) and fg.get("applied"): c["final_gate_applied"] += 1
    f2 = r5.get("f2") or {}; f1 = r5.get("f1") or {}
    if f2.get("enabled"): c["f2_enabled"] += 1
    if f2.get("fired"): c["f2_fired"] += 1
    if f1.get("final_gate_rejected"): c["f1_rejected"] += 1
    if f1.get("demoted_p3"): c["f1_demoted"] += 1
    if f1.get("reading_match_primary_pass"): c["reading_match_primary_pass"] += 1
    if "candidate_e_full_diff" in j: c["e3_field"] += 1
    if "candidate_e_cascade_return" in j: c["e4_field"] += 1
for fam, root in ROOTS.items():
    for p in glob.glob(root + "/**/tts_generation_results.json", recursive=True):
        p = p.replace("\\", "/"); m = re.search(r"/([^/]+)/(a2|b1b)/audit/tts_generation_results.json$", p)
        if not m: continue
        run, lvl = m.group(1), m.group(2)
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception: continue
        for name, s in (d.get("segments") or {}).items():
            if not isinstance(s, dict): continue
            j = s.get("asr_judgement")
            if not (isinstance(j, dict) and j.get("lang") == "ja"):
                logs = (s.get("standard_attempts_log") or []) + (s.get("fallback_attempts_log") or []) + (s.get("attempts_log") or [])
                j = (logs[-1].get("asr_judgement") if logs else None)
                if not (isinstance(j, dict) and j.get("lang") == "ja"): continue
                ts = ((logs[-1].get("scg_info") or {}).get("timestamp"))
            else:
                ts = (s.get("scg_info") or {}).get("timestamp")
            add(fam, lvl, sec_of(name), j, run, ts)
        for n, kp in (d.get("key_phrases") or {}).items():
            jm = (kp or {}).get("japanese_meaning") if isinstance(kp, dict) else None
            j = jm.get("asr_judgement") if isinstance(jm, dict) else None
            if isinstance(j, dict) and j.get("lang") == "ja": add(fam, lvl, "kp_japanese_meaning", j, run, (jm.get("scg_info") or {}).get("timestamp"))
out = {}
for key in sorted(rows):
    c = rows[key]; out["|".join(key)] = dict(c, runs_with_r5=len(runs[key]), newest_r5_ts=newest.get(key))
    print("|".join(key), dict(c), "runs_with_r5=", len(runs[key]), "newest_ts=", newest.get(key))
json.dump(out, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_asr_wiring_matrix_scan_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
