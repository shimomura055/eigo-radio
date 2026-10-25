# OPEN-333 E4 の runtime発火確認(API 0・費用0円。委任_14)。保存済み転写(open333_e4_eval_01.out.json の real 1327 + sweep/old_sweep/e4)を
# Productionの正式adapter(er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail。Azureはstub、socket guard)へ注入し、
# E4 ON(既定)/OFF(rollback定数False=HEAD相当)で (a)candidate_e_cascade_return 発火件数 (b)HEAD(OFF)比の state 遷移 (c)Azure応答注入[原稿どおり/Primaryと同じ誤り]
# の結果を記録する。有料API・外部通信は0。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_e4_runtime_fire_01.py
import collections, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er007_ja_secondary_asr_01 as sec

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
ev = json.load(open(D + "open333_e4_eval_01.out.json", encoding="utf8"))
pairs = {}
for k in ("real", "sweep", "old_sweep", "e4"):
    for r in ev[k]:
        pairs[(k, r["canon"], r["asr"])] = 1
pairs = sorted(pairs)
E.api0_guard_on()
PASSING = E.uj.PASSING_STATES


def one(canon, asr, az_text=None):
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = (lambda p, language="ja-JP", timeout_seconds=90: (az_text, None)) if az_text is not None \
        else (lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call"))
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, asr, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig
    return r["asr_judgement"]


res, rows = {}, {}
for label, on in (("ON", True), ("OFF", False)):
    VL.CANDIDATE_E_CASCADE_DIFF_RETURN = on
    rows[label] = {k: one(k[1], k[2]) for k in pairs}
VL.CANDIDATE_E_CASCADE_DIFF_RETURN = True
fired = [k for k in pairs if rows["ON"][k].get("candidate_e_cascade_return")]
fired_off = [k for k in pairs if rows["OFF"][k].get("candidate_e_cascade_return")]
trans = collections.Counter((rows["OFF"][k]["state"], rows["ON"][k]["state"]) for k in pairs if rows["OFF"][k]["state"] != rows["ON"][k]["state"])
widen = [k for k in pairs if rows["OFF"][k]["state"] not in PASSING and rows["ON"][k]["state"] in PASSING]
res["attempts"] = len(pairs)
res["fired_on"] = len(fired)
res["fired_off"] = len(fired_off)
res["fired_by_source"] = dict(collections.Counter(k[0] for k in fired))
res["transitions_off_to_on"] = {f"{a}->{b}": n for (a, b), n in trans.items()}
res["non_pass_to_pass"] = len(widen)
# Azure応答注入(発火行のうち実データ real のみ詳細、全体は集計)
inj = collections.Counter()
detail = []
for k in fired:
    c, p = k[1], k[2]
    a = one(c, p, c)       # A: Azureが原稿どおり
    b = one(c, p, p)       # B: AzureがPrimaryと同じ誤り
    inj[("A_exact", a["state"])] += 1
    inj[("B_same_error", b["state"])] += 1
    if k[0] == "real":
        detail.append({"canon": c[:40], "primary": p[:40], "diffs": rows["ON"][k]["candidate_e_cascade_return"]["diffs"], "A": a["state"], "B": b["state"]})
res["azure_injection"] = {f"{x}:{st}": n for (x, st), n in inj.items()}
res["real_fired_detail"] = detail
res["azure_real_calls_total"] = sum((rows[l][k].get("adapter") or {}).get("azure_real_calls", 0) for l in rows for k in pairs)
E.api0_guard_off()
print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
json.dump(res, open(D + "open333_e4_runtime_fire_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, sort_keys=True)
