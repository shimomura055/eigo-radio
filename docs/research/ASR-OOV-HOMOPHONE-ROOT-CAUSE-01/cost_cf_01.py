# cost_cf_01.py -- 本run(word_gacha run_wg_01)の履歴から、候補E2/Cを適用していたらの TTS再試行・Azure呼出・費用 を算出(API 0)。
import copy, glob, json, os, re, sys, collections
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
import soundfile as sf
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1
R = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/"
rows = [json.loads(l) for l in open(R + "raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
tts_sec = sum(r.get("output_audio_seconds_computed_from_pcm") or 0 for r in rows if r["provider"] == "gemini")
az_sec = sum(r.get("audio_duration_submitted_seconds") or 0 for r in rows if r["provider"] == "azure")
n_asr = sum(1 for r in rows if r["provider"] == "openai_asr")
print(f"gemini TTS 総秒 {tts_sec:.0f}s / azure 総秒 {az_sec:.0f}s ({az_sec*0.0444:.2f}円) / openai_asr呼出 {n_asr}")
# 単価: gemini = runtime evidence audio内訳17.60円 / 総秒; openai_asr = 4.64円/呼出数
GEM = 17.60 / tts_sec; ASRC = 4.64 / n_asr; AZ = 0.0444
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
tot_actual = collections.Counter(); tot_cf = collections.Counter(); detail = []
for level in ("a2", "b1b"):
    tgr = json.load(open(R + f"{level}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    for seg, s in tgr.items():
        canon_b = s.get("canonical_text_before_local_rewrite") or s.get("text")
        if "gacha" not in (canon_b or "").lower(): continue
        files = sorted(glob.glob(R + f"{level}/narration/attempts/{seg}_attempt*.json"), key=lambda f: int(re.search(r"attempt(\d+)_", f).group(1)))
        atts = []
        for f in files:
            j = json.load(open(f, encoding="utf-8")); wav = f[:-5] + ".wav"
            dur = sf.info(wav).duration if os.path.exists(wav) else 0
            atts.append({"n": j["attempt_number"], "asr": j["asr_text"], "cls": j.get("audio_classification"), "verified": j.get("verified"), "dur": dur})
        fz = m1.freeze_candidates(canon_b, ledger_snapshot=copy.deepcopy(L), segment_started_at="2026-10-24T18:10:00")
        first_acc = None
        for i, a in enumerate(atts):
            c = canon_b
            r = T.judge_direct(c, a["asr"], fz, segment_id=seg)
            a["e2"] = r["accepted"]
            if r["accepted"] and first_acc is None: first_acc = i
        # 実績: 全attempt(最後が採用)。Azure呼出は Primary非PASSの attempt すべて(統一judge: Primary NG->Secondary 1回)と仮定=保存分類が PASS系でない行
        def cost(sub):
            tts = sum(a["dur"] for a in sub) * GEM; asr = len(sub) * ASRC
            az = sum(a["dur"] for a in sub if a["cls"] not in ("EXACT_MATCH", "NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")) * AZ
            return tts, asr, az
        act = cost(atts)
        cf_sub = atts if first_acc is None else atts[:first_acc + 1]
        t, a_, z = cost(cf_sub)
        if first_acc is not None:   # E2受理attemptはSecondary不要(Primary段で受理)
            z -= (atts[first_acc]["dur"] * AZ if atts[first_acc]["cls"] not in ("EXACT_MATCH", "NORMALIZED_MATCH") else 0)
        cfc = (t, a_, z)
        detail.append({"level": level, "seg": seg, "attempts": len(atts), "cf_attempts": len(cf_sub), "e2_first_accept_index": first_acc, "actual(tts,asr,azure)": [round(x, 2) for x in act], "cf(tts,asr,azure)": [round(x, 2) for x in cfc],
                       "per_attempt": [(a["n"], a["cls"], a["e2"], round(a["dur"], 1)) for a in atts]})
        for k, v in zip(("tts", "asr", "azure"), act): tot_actual[k] += v
        for k, v in zip(("tts", "asr", "azure"), cfc): tot_cf[k] += v
for d in detail: print(json.dumps(d, ensure_ascii=False))
print("実績(gachaを含むsegmentのみ) 円:", {k: round(v, 2) for k, v in tot_actual.items()}, "計", round(sum(tot_actual.values()), 2))
print("E2適用 円:", {k: round(v, 2) for k, v in tot_cf.items()}, "計", round(sum(tot_cf.values()), 2))
print("削減", round(sum(tot_actual.values()) - sum(tot_cf.values()), 2), "円 (LR候補生成・HR待ち・cooldown 600秒の時間は別)")
json.dump({"detail": detail, "actual": dict(tot_actual), "cf": dict(tot_cf)}, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/cost_cf_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
