# trial_run_e2_02_paid.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02 §4: 合成正例・音声負例の実音声Trial(有料。上限40円、1起動のみ、再起動・監督ループ禁止)。
# 目的: 『CMU未収録で、CMUに同じ発音の語がある』語(Lyft/Fyre/Grindr/thicc/kewl/skool/luv/phat)を既存Production TTSで読み上げ→Primary ASR→
#       既存Production判定(classify→M1)→不成立のときE2(v2)で救済できるか(救済率)、意図的に別語を読ませた音声(負例)を誤受理しないか、を実測する。
#       Ledgerの読みは**既存の正式経路**(er006_secondary_asr_01._resolve_unresolved_entity_for_review=cascade_unresolved_entity型。gachaを作ったのと同じ関数)で登録し、
#       1語あたりの実費(供給側G)も計測する。Ledgerは**Trial用コピー**(work/trial02/ledger_trial.json)へ向け、共有Ledgerは変更しない(実行前後のsha256を記録)。
# 使用モデル(Production routingと同一): TTS=gemini-3.8-flash-lite-tts(speech_metadata_flash_lite、voice=Aoede(p9a.VOICE_NAME)、既定英語style)/
#       Primary ASR=gpt-4o-mini-transcribe(routing.transcribe)/Ledger調査=Perplexity sonar(research_pronunciations既定)。旧世代モデル使用なし。
# 実行: .venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_run_e2_02_paid.py --execute   (引数なし=dry-run)
import argparse, copy, hashlib, json, os, shutil, subprocess, sys, time, datetime
sys.path.insert(0, "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"); sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()

MANAGED_ID = "ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"
D = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01"
OUT = D + "/work/trial02"
BUDGET = 40.0
SEG = "full_story_part1"
SHARED_LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
SHARED_STATE = [SHARED_LEDGER, "er011_output/attempt_history.jsonl", "er006_output/master_audio_store_01/manifest.json",
                "er006_output/master_audio_store_01/reuse_telemetry.jsonl", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"]
EST = {"perplexity": 2.0, "tts": 0.4, "asr": 0.15}  # 事前ガード用の安全側概算(実額はcost logから後で集計)

WORDS = ["Lyft", "Fyre", "Grindr", "thicc", "kewl", "skool", "luv", "phat"]
# (id, canonical(TTS入力=正準), spoken(実際にTTSへ渡す文。正例は正準と同じ、負例は別語), kind)
POS = [
    ("lyft_1", "She booked a Lyft to the airport before sunrise.", "pos"),
    ("lyft_2", "The driver of the Lyft waited outside for ten minutes.", "pos"),
    ("lyft_x2", "A Lyft stopped at the corner, and another Lyft followed.", "pos_twice"),
    ("fyre_1", "The Fyre Festival promised luxury but delivered chaos.", "pos"),
    ("fyre_2", "Many guests still remember the Fyre story today.", "pos"),
    ("grindr_1", "The Grindr app changed how many people meet each other.", "pos"),
    ("grindr_2", "Researchers studied how people use Grindr in big cities.", "pos"),
    ("thicc_1", "Teenagers now say thicc to praise a very solid sandwich.", "pos"),
    ("thicc_2", "The word thicc became popular on social media.", "pos"),
    ("kewl_1", "He typed kewl under every photo his friend posted.", "pos"),
    ("kewl_2", "Spelling words like kewl is common in old chat rooms.", "pos"),
    ("skool_1", "Her little brother is excited about skool this fall.", "pos"),
    ("skool_2", "The sign said skool bus, but the spelling was wrong.", "pos"),
    ("skool_x2", "Skool is fun, and every skool day starts early.", "pos_twice"),
    ("luv_1", "He wrote luv at the bottom of every letter.", "pos"),
    ("luv_2", "The singer repeated the word luv in the chorus.", "pos"),
    ("phat_1", "In old hip hop slang, phat meant something excellent.", "pos"),
    ("phat_2", "People once said phat beats to praise a good song.", "pos"),
]
NEG = [  # (id, canonical, spoken=意図的に別の語として読ませる)
    ("neg_lyft_loft", "She booked a Lyft to the airport before sunrise.", "She booked a loft to the airport before sunrise."),
    ("neg_skool_scowl", "Her little brother is excited about skool this fall.", "Her little brother is excited about scowl this fall."),
    ("neg_thicc_thin", "Teenagers now say thicc to praise a very solid sandwich.", "Teenagers now say thin to praise a very solid sandwich."),
    ("neg_kewl_coal", "He typed kewl under every photo his friend posted.", "He typed coal under every photo his friend posted."),
    ("neg_thicc_sick", "The word thicc became popular on social media.", "The word sick became popular on social media."),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


class Guard:
    def __init__(self):
        self.est = 0.0

    def check(self, kind, what):
        if os.path.exists(OUT + "/STOP") or os.path.exists(D + "/STOP"):
            raise SystemExit("STOP sentinel present: 新規API呼出なしで停止")
        if self.est + EST[kind] > BUDGET:
            raise SystemExit(f"Guardrail {BUDGET}円 超過見込み({self.est:.2f}+{EST[kind]}) before {what}: 新規API呼出なしで停止")
        self.est += EST[kind]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--execute", action="store_true"); a = ap.parse_args()
    n_pos, n_neg = len(POS), len(NEG)
    print(f"plan: Ledger登録 {len(WORDS)}語(Perplexity) / 正例 {n_pos} clip + 負例 {n_neg} clip = TTS {n_pos+n_neg} + Primary ASR {n_pos+n_neg}。事前概算上限 "
          f"{len(WORDS)*EST['perplexity'] + (n_pos+n_neg)*(EST['tts']+EST['asr']):.1f}円 / Cap {BUDGET}円")
    if not a.execute:
        return
    os.makedirs(OUT + "/clips", exist_ok=True)
    p = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", D, "--out", OUT + "/stop_check_paid.json"])
    if p.returncode != 0:
        raise SystemExit(f"stop_scope_check rc={p.returncode}: 新規API呼出なしで停止")
    before_sha = {f: sha(f) for f in SHARED_STATE}
    # ---- Trial用Ledger(共有Ledgerのコピー)へ向ける ----
    trial_ledger = OUT + "/ledger_trial.json"
    shutil.copy(SHARED_LEDGER, trial_ledger)
    import er005_cost_logger as cl
    cl.init_logger(OUT + "/cost/usage_log.jsonl")
    import er006_secondary_asr_01 as S
    import er006_pronunciation_ledger_01 as pl
    pl.LEDGER_PATH = trial_ledger
    assert S.pronun_ledger.LEDGER_PATH == trial_ledger, "ledger path override failed"
    import er006_asr_provider_routing_01 as routing
    import er006_preprod_hardening_01_validation as val
    import er006_m1_multi_candidate_01 as m1
    import trial_direct_ledger_phoneme_01 as T
    import er002_common as common
    import er003_b1_p4c_audio as p4c
    import er003_b1_p9a_audio as p9a
    import er006_batch_tts_wiring_01 as batch_wiring
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er003_v1_sing01_voice01_generate as voice01
    g = Guard()
    log = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "ledger_registration": [], "clips": [], "budget_cap": BUDGET}

    # ---- 1. Ledger登録(既存の正式経路。cascade_unresolved_entity型) ----
    cl.logging_context("asr_oov_e2_trial02", "ledger_registration").__enter__()
    for w in WORDS:
        g.check("perplexity", "ledger:" + w)
        n_before = sum(1 for _ in open(OUT + "/cost/usage_log.jsonl", encoding="utf-8"))
        S._stage1_clear()
        info = S._resolve_unresolved_entity_for_review(w)
        s1 = S._stage1_take()
        recs = [json.loads(l) for l in list(open(OUT + "/cost/usage_log.jsonl", encoding="utf-8"))[n_before:]]
        row = {"word": w, "stage1_action": s1.get("action"), "info_present": bool(info),
               "confidence": (info or {}).get("confidence"), "ipa": (info or {}).get("expected_pronunciation_ipa"),
               "alt": (info or {}).get("alternate_pronunciations"), "evidence_tier": (info or {}).get("evidence_tier"),
               "entity_type": (info or {}).get("entity_type"), "n_sources": len((info or {}).get("sources") or []),
               "ledger_disabled": (info or {}).get("ledger_disabled"),
               "perplexity_calls": [{k: r.get(k) for k in ("model_id", "input_tokens", "output_tokens", "total_tokens", "success")} for r in recs if r.get("provider") == "perplexity"]}
        print("LEDGER", w, row["stage1_action"], row["confidence"], row["ipa"], row["perplexity_calls"], flush=True)
        log["ledger_registration"].append(row)
    ledger = json.load(open(trial_ledger, encoding="utf-8"))

    # ---- 2. 音声生成→Primary ASR→判定 ----
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

    def synth(text, out_path):
        call_fn, prompt = flw.resolve_tts_call_and_prompt(
            text, p9a.ENGLISH_STYLE_PREFIX, common.MODEL_NAME, p9a.VOICE_NAME, out_path, tts_backend="speech_metadata_flash_lite",
            build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
        pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            return {"ok": False, "error": str(err)}
        with open(out_path, "wb") as f:
            f.write(common.pcm_to_wav_bytes(pcm))
        return {"ok": True, "retries": retries}

    import wave
    def dur(pth):
        with wave.open(pth) as w_:
            return w_.getnframes() / w_.getframerate()

    items = [(i, c, c, k) for i, c, k in POS] + [(i, c, s, "neg") for i, c, s in NEG]
    for cid, canonical, spoken, kind in items:
        g.check("tts", cid); g.check("asr", cid)
        wav = f"{OUT}/clips/{cid}.wav"
        with cl.segment_context(cid):
            t = synth(spoken, wav)
            row = {"id": cid, "kind": kind, "canonical": canonical, "spoken": spoken, "tts": t}
            if not t["ok"]:
                log["clips"].append(row); print(cid, "TTS_FAIL", t, flush=True); continue
            row["wav_sec"] = round(dur(wav), 2); row["wav_sha256"] = sha(wav)
            ptext, perr = routing.transcribe(wav, language="en-US")
        row.update(primary_asr=ptext, primary_err=perr)
        if ptext is None:
            log["clips"].append(row); print(cid, "ASR_FAIL", perr, flush=True); continue
        started = datetime.datetime.now().isoformat(timespec="seconds")  # Ledger登録は全てこれより前(OF-179の時刻条件)
        fz = m1.freeze_candidates(canonical, ledger_snapshot=copy.deepcopy(ledger), segment_started_at=started)
        base = val.classify_asr_match(canonical, ptext, segment_id=SEG)
        row["base"] = base.classification
        if base.should_pass:
            row["outcome"] = "BASE_PASS(救済不要)"
        else:
            mr = m1.m1_multi_candidate_judge(canonical, ptext, fz, base_cls=base)
            row["m1"] = {"accepted": mr.accepted, "reason": mr.reason}
            if mr.accepted:
                row["outcome"] = "M1_ACCEPT"
            else:
                e2 = T.judge_direct(canonical, ptext, fz, segment_id=SEG, ledger=ledger)
                e2_lo = T.judge_direct(canonical, ptext, fz, segment_id=SEG, ledger=ledger, min_conf=("low", "medium", "high"))
                row["e2"] = {"accepted": e2["accepted"], "reason": e2["reason"], "sub": e2.get("sub")}
                row["e2_if_low_confidence_allowed"] = {"accepted": e2_lo["accepted"], "reason": e2_lo["reason"]}
                row["outcome"] = "E2_ACCEPT" if e2["accepted"] else "NOT_RESCUED:" + str(e2["reason"])
        log["clips"].append(row)
        print(cid, row["kind"], "|", ptext, "|", row.get("base"), "->", row["outcome"], "|", (row.get("e2") or {}).get("reason"), flush=True)
    # ---- 3. 集計 ----
    after_sha = {f: sha(f) for f in SHARED_STATE}
    log["shared_state_changed"] = {f: (before_sha[f], after_sha[f]) for f in SHARED_STATE if before_sha[f] != after_sha[f]}
    log["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(log, open(OUT + "/trial02_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("shared_state_changed:", log["shared_state_changed"])
    print("done; guard_est", round(g.est, 2))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
