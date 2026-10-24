# cost_cf_03.py -- 委任_03 OF-OOV-08: 修正後E2W(位置1語・Whisper正の一致・Ledger時系列)での本run費用の再計算(API 0)。単価は cost_cf_01.py と同一。
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
R = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/"
rows = [json.loads(l) for l in open(R + "raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
tts_sec = sum(r.get("output_audio_seconds_computed_from_pcm") or 0 for r in rows if r["provider"] == "gemini")
n_asr = sum(1 for r in rows if r["provider"] == "openai_asr")
GEM = 17.60 / tts_sec; ASRC = 4.64 / n_asr; AZ = 0.0444
PASS = ("EXACT_MATCH", "NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")
d = json.load(open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/trial03_stored_e2w.json", encoding="utf-8"))
segs = {}
for r in d: segs.setdefault((r["level"], r["seg"]), []).append(r)
def cost(sub):
    return (sum(a["dur"] for a in sub) * GEM, len(sub) * ASRC, sum(a["dur"] for a in sub if a["cls"] not in PASS) * AZ)
tot_a = [0, 0, 0]; tot_c = [0, 0, 0]
for k, atts in segs.items():
    first = next((i for i, a in enumerate(atts) if a.get("e2w_accepted") and a["ledger_before_seg"]), None)
    act = cost(atts)
    if first is None:
        cf = act
    else:
        sub = atts[:first + 1]; t, a_, z = cost(sub)
        z -= atts[first]["dur"] * AZ if atts[first]["cls"] not in PASS else 0   # 受理attemptはPrimary段で確定=Secondary不要
        cf = (t, a_, z)
    print(k, "attempts", len(atts), "e2w_first_accept_idx", first, "actual", [round(x, 2) for x in act], "cf", [round(x, 2) for x in cf])
    for i in range(3): tot_a[i] += act[i]; tot_c[i] += cf[i]
print("実績", round(sum(tot_a), 2), "cf", round(sum(tot_c), 2), "削減", round(sum(tot_a) - sum(tot_c), 2))
