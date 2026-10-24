# trial_run_e2_02_neg2.py -- 追加の音声負例(有料・上限6円・1起動)。trial02の負例は n=4(有効)と少なく、1件でPrimary誤り(coal->cool)が出たため、
# 『Ledger語の同音語に近い別語』を意図的に読ませた音声を追加し、E2単独 / E2+ローカルWhisper非矛盾(E2W) の誤受理を測る。
# 今回は cl.install(log) でTTS/ASRの実コストも記録する(trial02では init_logger のみでTTS/ASRが未記録だった=reconstructionで補った)。
import copy, datetime, json, os, subprocess, sys, time, wave
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"; OUT = D + "/work/trial02_neg2"; SEG = "full_story_part1"
NEG = [  # (id, canonical, spoken)
    ("n2_lyft_left", "She booked a Lyft to the airport before sunrise.", "She booked a left to the airport before sunrise."),
    ("n2_skool_stool", "Her little brother is excited about skool this fall.", "Her little brother is excited about stool this fall."),
    ("n2_thicc_think", "Teenagers now say thicc to praise a very solid sandwich.", "Teenagers now say think to praise a very solid sandwich."),
    ("n2_phat_fact", "In old hip hop slang, phat meant something excellent.", "In old hip hop slang, fact meant something excellent."),
    ("n2_kewl_call", "He typed kewl under every photo his friend posted.", "He typed call under every photo his friend posted."),
    ("n2_kewl_coal", "Spelling words like kewl is common in old chat rooms.", "Spelling words like coal is common in old chat rooms."),
    ("n2_kewl_cowl", "He typed kewl under every photo his friend posted.", "He typed cowl under every photo his friend posted."),
]
BUDGET = 6.0
def main():
    os.makedirs(OUT + "/clips", exist_ok=True)
    p = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", "ASR-OOV-HOMOPHONE-ROOT-CAUSE-01", "--run-dir", D, "--out", OUT + "/stop_check_paid.json"])
    if p.returncode != 0: raise SystemExit("stop")
    import er005_cost_logger as cl
    cl.install(OUT + "/cost/usage_log.jsonl")
    import er006_asr_provider_routing_01 as routing
    import er006_preprod_hardening_01_validation as val
    import er006_m1_multi_candidate_01 as m1
    import trial_direct_ledger_phoneme_01 as T
    import er002_common as common, er003_b1_p4c_audio as p4c, er003_b1_p9a_audio as p9a
    import er006_batch_tts_wiring_01 as bw, er033_tts_flash_lite_backend_wiring_01 as flw
    import er008_disfluency_qa_18 as dq
    ledger = json.load(open(D + "/work/trial02/ledger_trial.json", encoding="utf-8"))
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    rows = []
    for cid, canonical, spoken in NEG:
        if os.path.exists(OUT + "/STOP"): raise SystemExit("STOP")
        wav = f"{OUT}/clips/{cid}.wav"
        call_fn, prompt = flw.resolve_tts_call_and_prompt(spoken, p9a.ENGLISH_STYLE_PREFIX, common.MODEL_NAME, p9a.VOICE_NAME, wav,
            tts_backend="speech_metadata_flash_lite", build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=bw.make_batch_tts_call_fn)
        with cl.segment_context(cid):
            pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
            if not ok:
                rows.append({"id": cid, "tts_error": str(err)}); continue
            open(wav, "wb").write(common.pcm_to_wav_bytes(pcm))
            ptext, perr = routing.transcribe(wav, language="en-US")
        words = dq.transcribe_verbatim(wav, language="en", model_size="small")
        wt = " ".join(w["text"].strip() for w in words).strip()
        started = datetime.datetime.now().isoformat(timespec="seconds")
        fz = m1.freeze_candidates(canonical, ledger_snapshot=copy.deepcopy(ledger), segment_started_at=started)
        base = val.classify_asr_match(canonical, ptext, segment_id=SEG)
        row = {"id": cid, "canonical": canonical, "spoken": spoken, "primary": ptext, "whisper": wt, "base": base.classification}
        if base.should_pass:
            row["outcome"] = "BASE_PASS(誤PASS: Primaryが正準語と書いた)"
        else:
            e2 = T.judge_direct(canonical, ptext, fz, segment_id=SEG, ledger=ledger)
            e2w = T.judge_direct(canonical, ptext, fz, segment_id=SEG, secondary_asr_text=wt, ledger=ledger)
            row.update(e2_accepted=e2["accepted"], e2_reason=e2["reason"], e2w_accepted=e2w["accepted"], e2w_reason=e2w["reason"], e2w_state=e2w.get("secondary_state"))
            row["outcome"] = "E2_ACCEPT(誤受理)" if e2["accepted"] else "REJECT:" + e2["reason"]
        rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    json.dump(rows, open(OUT + "/neg2_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
