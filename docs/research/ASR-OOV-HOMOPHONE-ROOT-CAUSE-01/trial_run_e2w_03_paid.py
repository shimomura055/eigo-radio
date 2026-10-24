# trial_run_e2w_03_paid.py -- 委任_03 OF-OOV-11: E2W(修正後)の負例20+正例10 実音声Trial(有料。上限10円、1起動のみ、再起動・監督ループ禁止)。
# 負例=Trial用Ledger語に対し1音素だけ違う近い語を意図的に読ませた音声。正例=X/Z本番voice(Charon[X Adv/Z Dionysius]・Erinome[Z Selinuntius])を含む。
# Ledger=Trial用コピー work/trial02/ledger_trial.json(共有Ledgerは触らない)。TTS=Production同経路(gemini-3.8-flash-lite-tts, speech_metadata_flash_lite, ENGLISH_STYLE_PREFIX)。
# Primary ASR=routing.transcribe(gpt-4o-mini-transcribe)。独立エンジン=Production既存の er006_secondary_asr_01._connected_speech_equivalence_local_asr_text(faster-whisper small, API 0)。
# 今回は cl.install(...) でTTS/ASRの実コストを必ず記録する。
import copy, datetime, json, os, subprocess, sys, time
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"; OUT = D + "/work/trial03"; SEG = "full_story_part1"
BUDGET = 10.0
POS = [  # (id, voice, text)  canonical==spoken
    ("p_gacha_aoede", "Aoede", "It's unexpected to find a gacha at the entrance, though."),
    ("p_gacha_charon", "Charon", "The boy kept spending coins at the gacha machine."),
    ("p_gacha_erinome", "Erinome", "She won a tiny prize from the gacha near the station."),
    ("p_thicc_charon", "Charon", "My cousin ordered a thicc milkshake after practice."),
    ("p_thicc_erinome", "Erinome", "The word thicc became a joke on social media."),
    ("p_skool_charon", "Charon", "Their old skool uniforms were bright green."),
    ("p_skool_erinome", "Erinome", "He wrote skool on the wall by mistake."),
    ("p_phat_charon", "Charon", "Back then, a phat beat could fill any dance floor."),
    ("p_lyft_charon", "Charon", "We took a Lyft home after the late show."),
    ("p_kewl_erinome", "Erinome", "She texted kewl and sent a smiling face."),
]
NEG = [  # (id, voice, canonical, spoken=1音素違いの近い語)
    ("n_thicc_tick", "Aoede", "My cousin ordered a thicc milkshake after practice.", "My cousin ordered a tick milkshake after practice."),
    ("n_thicc_thing", "Charon", "The word thicc became a joke on social media.", "The word thing became a joke on social media."),
    ("n_skool_skull", "Erinome", "He wrote skool on the wall by mistake.", "He wrote skull on the wall by mistake."),
    ("n_skool_scold", "Aoede", "Their old skool uniforms were bright green.", "Their old scold uniforms were bright green."),
    ("n_skool_spool", "Charon", "She was late for skool again this morning.", "She was late for spool again this morning."),
    ("n_phat_vat", "Aoede", "Back then, a phat beat could fill any dance floor.", "Back then, a vat beat could fill any dance floor."),
    ("n_phat_fit", "Erinome", "Back then, a phat beat could fill any dance floor.", "Back then, a fit beat could fill any dance floor."),
    ("n_phat_fad", "Charon", "Everyone said the phat sound was cool in those days.", "Everyone said the fad sound was cool in those days."),
    ("n_phat_pat", "Aoede", "Everyone said the phat sound was cool in those days.", "Everyone said the pat sound was cool in those days."),
    ("n_kewl_cull", "Erinome", "She texted kewl and sent a smiling face.", "She texted cull and sent a smiling face."),
    ("n_kewl_curl", "Aoede", "He typed kewl under every photo his friend posted.", "He typed curl under every photo his friend posted."),
    ("n_kewl_coil", "Charon", "Spelling words like kewl is common in old chat rooms.", "Spelling words like coil is common in old chat rooms."),
    ("n_kewl_keel", "Aoede", "She texted kewl and sent a smiling face.", "She texted keel and sent a smiling face."),
    ("n_lyft_laughed", "Charon", "We took a Lyft home after the late show.", "We took a laughed home after the late show."),
    ("n_lyft_gift", "Aoede", "She booked a Lyft to the airport before sunrise.", "She booked a gift to the airport before sunrise."),
    ("n_lyft_lived", "Erinome", "The driver of the Lyft waited outside for ten minutes.", "The driver of the lived waited outside for ten minutes."),
    ("n_grindr_grander", "Aoede", "The Grindr app changed how many people meet each other.", "The grander app changed how many people meet each other."),
    ("n_grindr_grinders", "Charon", "Researchers studied how people use Grindr in big cities.", "Researchers studied how people use grinders in big cities."),
    ("n_gacha_gaucho", "Aoede", "The boy kept spending coins at the gacha machine.", "The boy kept spending coins at the gaucho machine."),
    ("n_gacha_gotta", "Erinome", "She won a tiny prize from the gacha near the station.", "She won a tiny prize from the gotta near the station."),
]


def main():
    os.makedirs(OUT + "/clips", exist_ok=True)
    if os.path.exists(OUT + "/trial03_result.json"):
        raise SystemExit("already ran (no restart)")
    p = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", "ASR-OOV-HOMOPHONE-ROOT-CAUSE-01", "--run-dir", D, "--out", OUT + "/stop_check_paid.json"])
    if p.returncode != 0:
        raise SystemExit("stop")
    import er005_cost_logger as cl
    cl.install(OUT + "/cost/usage_log.jsonl")
    import er006_asr_provider_routing_01 as routing
    import er006_preprod_hardening_01_validation as val
    import er006_m1_multi_candidate_01 as m1
    import trial_direct_ledger_phoneme_01 as T
    import er002_common as common, er003_b1_p4c_audio as p4c, er003_b1_p9a_audio as p9a
    import er006_batch_tts_wiring_01 as bw, er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_secondary_asr_01 as sec
    ledger = json.load(open(D + "/work/trial02/ledger_trial.json", encoding="utf-8"))
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    items = [(i, v, t, t, "pos") for i, v, t in POS] + [(i, v, c, s, "neg") for i, v, c, s in NEG]
    rows = []; est = 0.0
    for cid, voice, canonical, spoken, kind in items:
        if os.path.exists(OUT + "/STOP") or os.path.exists(D + "/STOP"):
            raise SystemExit("STOP")
        est += 0.25
        if est > BUDGET:
            raise SystemExit("budget guard")
        wav = f"{OUT}/clips/{cid}.wav"
        call_fn, prompt = flw.resolve_tts_call_and_prompt(spoken, p9a.ENGLISH_STYLE_PREFIX, common.MODEL_NAME, voice, wav,
            tts_backend="speech_metadata_flash_lite", build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=bw.make_batch_tts_call_fn)
        with cl.segment_context(cid):
            pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
            if not ok:
                rows.append({"id": cid, "kind": kind, "tts_error": str(err)}); print(cid, "TTS_FAIL", err, flush=True); continue
            open(wav, "wb").write(common.pcm_to_wav_bytes(pcm))
            ptext, perr = routing.transcribe(wav, language="en-US")
        t0 = time.time(); wt = sec._connected_speech_equivalence_local_asr_text(wav); wsec = round(time.time() - t0, 1)
        started = datetime.datetime.now().isoformat(timespec="seconds")
        fz = m1.freeze_candidates(canonical, ledger_snapshot=copy.deepcopy(ledger), segment_started_at=started)
        base = val.classify_asr_match(canonical, ptext, segment_id=SEG) if ptext else None
        row = {"id": cid, "kind": kind, "voice": voice, "canonical": canonical, "spoken": spoken, "primary": ptext, "whisper": wt, "whisper_sec": wsec,
               "base": base.classification if base else None}
        if base is None:
            row["outcome"] = "PRIMARY_ASR_FAIL"
        elif base.should_pass:
            row["outcome"] = "BASE_PASS(Primaryが正準語と書いた。救済不要/既存挙動)"
        else:
            e2 = T.judge_direct(canonical, ptext, fz, segment_id=SEG, ledger=ledger)
            e2w = T.judge_e2w(canonical, ptext, fz, segment_id=SEG, whisper_text=wt, ledger=ledger)
            row.update(e2_accepted=e2["accepted"], e2_reason=e2["reason"], e2w_accepted=e2w["accepted"], e2w_reason=e2w["reason"],
                       whisper_state=e2w.get("whisper_state"), whisper_word=e2w.get("whisper_word"),
                       e2_ledger_key=(e2.get("sub") or {}).get("ledger_key"), e2_asr_word=(e2.get("sub") or {}).get("asr"))
            row["outcome"] = ("E2W_ACCEPT" if e2w["accepted"] else ("E2_ONLY_ACCEPT(E2Wが防止)" if e2["accepted"] else "NOT_RESCUED:" + str(e2["reason"])))
        rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    json.dump(rows, open(OUT + "/trial03_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
