# trial_run_e2w_03_stored.py -- 委任_03 OF-OOV-08: 保存済み本run(word_gacha run_wg_01)の長segmentへ、修正後E2W(位置1語・fail-closed)を再評価(API 0)。
# ローカルWhisperは Production と同じ er006_secondary_asr_01._connected_speech_equivalence_local_asr_text(faster-whisper small)を使う。
# 時系列: Ledger entry(gacha)の updated_at より後に始まったsegmentだけが救済対象(各語の最初の発生は救えない)。
# 実行: .venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_run_e2w_03_stored.py
import copy, datetime, glob, json, os, re, sys
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import soundfile as sf
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1
import er006_secondary_asr_01 as sec
R = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/"
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/"
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
gk = [k for k, v in L.items() if str(v.get("surface", "")).lower() == "gacha"][0]
led_t = datetime.datetime.fromisoformat(L[gk]["updated_at"])
print("gacha ledger entry", gk, "updated_at", led_t, "confidence", L[gk].get("confidence"))
PASS = ("EXACT_MATCH", "NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")
rows = []
for level in ("a2", "b1b"):
    tgr = json.load(open(R + f"{level}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    for seg, s in tgr.items():
        cb = s.get("canonical_text_before_local_rewrite") or s.get("text")
        if "gacha" not in (cb or "").lower():
            continue
        files = sorted(glob.glob(R + f"{level}/narration/attempts/{seg}_attempt*.json"), key=lambda f: int(re.search(r"attempt(\d+)_", f).group(1)))
        for f in files:
            j = json.load(open(f, encoding="utf-8")); wav = f[:-5] + ".wav"
            dur = sf.info(wav).duration
            saved = datetime.datetime.fromtimestamp(os.path.getmtime(f))
            seg_start_est = datetime.datetime.fromtimestamp(os.path.getmtime(files[0])) - datetime.timedelta(seconds=dur + 30)
            rows.append(dict(level=level, seg=seg, n=j["attempt_number"], cls=j.get("audio_classification"), verified=j.get("verified"), dur=dur,
                             asr=j["asr_text"], canonical=(s.get("text") if (j["attempt_number"] == len(files) and s.get("canonical_text_before_local_rewrite")) else cb),
                             wav=wav, saved=saved.isoformat(timespec="seconds"), seg_start_est=seg_start_est, ledger_before_seg=(seg_start_est > led_t)))
out = []
for r in rows:
    row = {k: (v.isoformat(timespec="seconds") if isinstance(v, datetime.datetime) else v) for k, v in r.items() if k not in ("asr", "canonical", "wav")}
    if r["cls"] in PASS:
        row["verdict"] = "PRIMARY_PASS(対象外)"; out.append(row); continue
    fz = m1.freeze_candidates(r["canonical"], ledger_snapshot=copy.deepcopy(L), segment_started_at=r["seg_start_est"].isoformat(timespec="seconds"))
    e2 = T.judge_direct(r["canonical"], r["asr"], fz, segment_id=r["seg"], ledger=L)
    row["e2_single"] = e2["accepted"]; row["e2_reason"] = e2["reason"]
    if e2["accepted"]:
        wt = sec._connected_speech_equivalence_local_asr_text(r["wav"])
        row["whisper_text_head"] = (wt or "")[:0]
        w = T.judge_e2w(r["canonical"], r["asr"], fz, segment_id=r["seg"], whisper_text=wt, ledger=L)
        row.update(e2w_accepted=w["accepted"], e2w_reason=w["reason"], whisper_state=w.get("whisper_state"), whisper_word=w.get("whisper_word"))
        # 参考: 旧方式(文全体classify)での判定
        import er006_preprod_hardening_01_validation as val
        row["whisper_whole_sentence_class"] = val.classify_asr_match(r["canonical"], wt or "", segment_id=r["seg"]).classification
    out.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
json.dump(out, open(D + "work/trial03_stored_e2w.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
