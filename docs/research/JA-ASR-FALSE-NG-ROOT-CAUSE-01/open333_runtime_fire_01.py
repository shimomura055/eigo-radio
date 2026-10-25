# OPEN-333 E3 の runtime発火確認(API 0・費用0円)。保存済み転写(既存771+未知493+合成負例91)を、Productionの正式adapter
# (er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail。Azureはstub=呼出0、socket guard)へ注入し、
# E3拒否の発火(asr_judgement.candidate_e_full_diff)と、Candidate E経由PASSの件数を、E3 ON/OFF(rollback定数)で集計する。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_runtime_fire_01.py
import collections, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er007_ja_secondary_asr_01 as sec

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
ev = json.load(open(D + "open333_api0_eval_04.out.json", encoding="utf8"))
pairs = [(r["src"], r["id"], r["canon"], r["asr"]) for r in ev["rows"]]
E.api0_guard_on()
PASSING = E.uj.PASSING_STATES


def one(canon, asr):
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call")
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, asr, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig
    j = r["asr_judgement"]
    cls = r["classification"]
    e_pass = bool(j.get("state") in PASSING and "Candidate E" in (getattr(cls, "reason", "") or ""))
    return j, e_pass, r


res = {}
for label, on in (("ON(既定)", True), ("OFF(rollback定数False)", False)):
    VL.CANDIDATE_E_FULL_DIFF_CHECK = on
    VL.CANDIDATE_E_VALUE_GUARD_CHECK = on
    n = e_pass_n = fired = pairs_total = 0
    fired_rows, azure_calls = [], 0
    for src, ident, c, a in pairs:
        j, ep, r = one(c, a)
        n += 1
        e_pass_n += ep
        f = j.get("candidate_e_full_diff")
        azure_calls += (j.get("adapter") or {}).get("azure_real_calls", 0)
        if f:
            fired += 1
            pairs_total += f["rejected"]
            fired_rows.append((src, ident[-34:], f["rejected"], [(p["canonical"], p["asr"], p["kind"]) for p in f["pairs"]], j.get("state"), j.get("reason_code")))
    res[label] = {"attempts": n, "e_pass_primary": e_pass_n, "e3_fired_attempts": fired, "e3_rejected_pairs": pairs_total, "azure_real_calls": azure_calls}
    print(f"[{label}] attempts={n} Candidate E経由PASS={e_pass_n} E3拒否が発火したattempt={fired} (拒否pair計 {pairs_total}) azure実呼出={azure_calls}")
    for x in fired_rows:
        print("    fired:", x)
VL.CANDIDATE_E_FULL_DIFF_CHECK = True
VL.CANDIDATE_E_VALUE_GUARD_CHECK = True
E.api0_guard_off()
json.dump(res, open(D + "open333_runtime_fire_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, sort_keys=True)
