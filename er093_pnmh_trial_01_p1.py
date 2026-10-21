# ============================================================
# er093_pnmh_trial_01_p1.py  (PNMH Trial 委任_04 / P1。Trial専用。Production経路は呼ぶだけで無変更)
# 使い方: python er093_pnmh_trial_01_p1.py manifest | tts | asr
#  - tts: 構成音声13本を Production TTS(TTS_EXECUTION_MODE=STANDARD、model=gemini-3.8-flash-lite-tts、voice Aoede[声A]/Charon[声B]、
#         ASR検証なしの単発関数 generate_english_component_minimal_instruction)で生成。再生成しない(既存logのclipはskip)。
#  - asr: Primary=OpenAI gpt-4o-mini-transcribe(Production routingと同一kwargs) / Secondary=Azure STT en-US(Phrase Listなし=Ledgerにbyus無し)。
#         既に結果のある(clip_id,method,rep)は再実行しない。reps: 全クリップ rep1、A5対象は rep2 まで。
# 費用は paid_calls.jsonl に実測(OpenAI=usage token、Azure=音声秒切上)を1呼出ずつ記録。累計>GUARD_JPYで新規呼出停止。
# 集計(層A/B/C)は er093_pnmh_trial_01_analyze.py(API 0)。
# ============================================================
from __future__ import annotations
import hashlib, json, math, os, sys, threading, time, wave
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT); sys.path.insert(0, ROOT)
OUT = "er093_output/pnmh_trial_01"
AUD = os.path.join(OUT, "audio"); os.makedirs(AUD, exist_ok=True)
MANIFEST = os.path.join(OUT, "dataset_manifest.json")
RAW = os.path.join(OUT, "asr_raw.jsonl")
PAID = os.path.join(OUT, "paid_calls.jsonl")
JPY_PER_USD = 160.0
OPENAI_IN_PER_M, OPENAI_OUT_PER_M = 1.25, 5.0       # er005_output/cost_baseline_01/pricing_snapshot.json(ASR3Wと同一)
AZURE_USD_PER_HOUR = 1.0
GUARD_JPY = 40.0                                    # Cap 50 の手前で新規有料呼出を停止
_lock = threading.Lock(); _spent = {"jpy": 0.0}

C1 = "LINE Manga has launched byUs, an AI service that lets you shape stories."
C2 = "Make one yourself with byUs."
VA, VB = "Aoede", "Charon"
# (clip_id, fid, carrier, spoken_token, voice, label(S1), aim)
SPEC = [
    ("F0_C1_A", "F0", C1, "byUs", VA, "UNLABELED(要試聴/多数決)", "TTSの実際の読み"),
    ("F0_C1_B", "F0", C1, "byUs", VB, "UNLABELED(要試聴/多数決)", "TTSの実際の読み"),
    ("F1_C1_A", "F1", C1, "bias", VA, "POS", "同音(1:1、現行でも救済)"),
    ("F2_C1_A", "F2", C1, "by us", VA, "POS", "同音(n:m、空白差)"),
    ("F3_C1_A", "F3", C1, "buy us", VA, "POS", "同音(n:m、綴り違い=本命)"),
    ("F3_C1_B", "F3", C1, "buy us", VB, "POS", "同音(n:m、綴り違い=本命)"),
    ("F3_C2_A", "F3", C2, "buy us", VA, "POS", "同音(n:m、綴り違い=本命)"),
    ("F4_C1_A", "F4", C1, "bios", VA, "NEG", "近音(BIOS)"),
    ("F4_C1_B", "F4", C1, "bios", VB, "NEG", "近音(BIOS)"),
    ("F5_C1_A", "F5", C1, "buys", VA, "NEG", "近音(Z/S)"),
    ("F7_C1_A", "F7", C1, "buy", VA, "NEG", "単語の脱落(us)"),
    ("F9_C1_A", "F9", C1, "B Y U S", VA, "NEG", "文字読み"),
    ("BI_C1_A", "BI", C1, "Bi-us", VA, "NEG(U-BI=NG維持)", "音節区切り(Bi-us)"),
]
REP2 = ["F0_C1_A", "F3_C1_A", "F4_C1_A", "F2_C1_A"]      # A5(同一音声のASR反復)対象


def wav_sec(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def spoken_of(c, tok):
    return c.replace("byUs", tok)


def cmd_manifest():
    rows = []
    for cid, fid, car, tok, voice, lab, aim in SPEC:
        p = os.path.join(AUD, cid + ".wav")
        r = {"clip_id": cid, "fid": fid, "carrier": car, "canonical": car, "spoken_text": spoken_of(car, tok), "spoken_token": tok, "voice": voice,
             "label_S1": lab, "aim": aim, "wav": p.replace("\\", "/")}
        if os.path.exists(p):
            r.update(wav_sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), duration_s=round(wav_sec(p), 3))
        rows.append(r)
    json.dump(rows, open(MANIFEST, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
    print("manifest", len(rows), "with wav", sum(1 for r in rows if "wav_sha256" in r))


def cmd_tts():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", "TTS_EXECUTION_MODE=STANDARD 必須"
    import er005_cost_logger as cl
    cl.install(os.path.join(OUT, "tts_raw_usage_log.jsonl"))
    import er003_v1_repro01_main_generate as gen
    log_path = os.path.join(OUT, "tts_log.jsonl")
    done = {json.loads(l)["clip_id"] for l in open(log_path, encoding="utf8")} if os.path.exists(log_path) else set()
    margin = gen.p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS
    for voice in (VA, VB):                     # p9a.VOICE_NAMEはprocess全体のglobal -> 声ごとに直列
        gen.p9a.VOICE_NAME = voice
        for cid, fid, car, tok, v, lab, aim in SPEC:
            if v != voice or cid in done:
                continue
            out = os.path.join(AUD, cid + ".wav"); t = time.time()
            r = gen.generate_english_component_minimal_instruction(spoken_of(car, tok), out, safety_margin_seconds=margin, tts_backend="speech_metadata_flash_lite")
            rec = {"ts": now(), "clip_id": cid, "spoken_text": spoken_of(car, tok), "status": r.get("status"), "reason": r.get("reason"), "path": out.replace("\\", "/"),
                   "sha256": r.get("sha256"), "duration_s": r.get("duration_seconds"), "model": r.get("model"), "voice": r.get("voice"), "call_count": r.get("call_count"),
                   "tts_backend": r.get("tts_backend"), "wall_s": round(time.time() - t, 2)}
            with open(log_path, "a", encoding="utf8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(rec, flush=True)
            if r.get("status") != "OK":
                print("TTS NOT OK -> 停止して報告", cid)
                return
    cmd_manifest()


def load_man():
    return json.load(open(MANIFEST, encoding="utf8"))


def load_done():
    s = set()
    if os.path.exists(RAW):
        for l in open(RAW, encoding="utf8"):
            if l.strip():
                r = json.loads(l); s.add((r["clip_id"], r["method"], r["rep"]))
    return s


def append(rec, jpy, detail):
    with _lock:
        open(RAW, "a", encoding="utf8").write(json.dumps(rec, ensure_ascii=False) + "\n")
        _spent["jpy"] += jpy
        open(PAID, "a", encoding="utf8").write(json.dumps({"ts": rec["ts"], "clip_id": rec["clip_id"], "method": rec["method"], "rep": rec["rep"], "jpy": round(jpy, 5),
                                                         "cum_this_process_jpy": round(_spent["jpy"], 4), **detail}, ensure_ascii=False) + "\n")


def openai_call(wav):
    import er006_asr_provider_routing_01 as routing
    client = routing._get_openai_client(); t = time.time()
    try:
        with open(wav, "rb") as f:
            kw = {"model": routing.ASR_ROUTING["en"]["model"], "file": f, "language": "en"}     # Production(_transcribe_openai_mini)同一kwargs。bodyなのでprompt無し
            resp = client.audio.transcriptions.create(**kw)
        u = getattr(resp, "usage", None)
        return {"text": resp.text, "error": None, "wall_s": round(time.time() - t, 3), "in_tok": getattr(u, "input_tokens", None), "out_tok": getattr(u, "output_tokens", None),
                "request_id": getattr(resp, "_request_id", None), "model": kw["model"]}
    except Exception as exc:
        return {"text": None, "error": str(exc)[:300], "wall_s": round(time.time() - t, 3), "in_tok": 0, "out_tok": 0}


def azure_call(wav):
    import er006_secondary_asr_01 as sec
    t = time.time()
    try:
        text, err = sec.get_full_text_via_azure_stt_with_phrase_list(wav, language="en-US", phrases=None)
    except Exception as exc:
        text, err = None, f"{type(exc).__name__}: {exc}"[:300]
    return {"text": text, "error": err, "wall_s": round(time.time() - t, 3)}


def job(r, method, rep):
    if _spent["jpy"] > GUARD_JPY:
        print("GUARD: 費用ガード超過 -> 新規呼出停止")
        return
    wav = r["wav"]; secs = wav_sec(wav)
    if method == "openai":
        x = openai_call(wav)
        jpy = ((x["in_tok"] or 0) * OPENAI_IN_PER_M + (x["out_tok"] or 0) * OPENAI_OUT_PER_M) / 1e6 * JPY_PER_USD
        rec = {"ts": now(), "clip_id": r["clip_id"], "method": "openai", "rep": rep, "text": x["text"], "error": x["error"], "wall_s": x["wall_s"], "audio_s": round(secs, 3),
               "in_tok": x["in_tok"], "out_tok": x["out_tok"], "request_id": x.get("request_id"), "model": x.get("model"), "jpy": round(jpy, 6)}
        append(rec, jpy, {"in_tok": x["in_tok"], "out_tok": x["out_tok"], "audio_s": round(secs, 3), "src": "usage tokens x pricing_snapshot.json $1.25/$5.0 per M, 160JPY/USD"})
    else:
        x = azure_call(wav); jpy = math.ceil(secs) * AZURE_USD_PER_HOUR / 3600.0 * JPY_PER_USD
        rec = {"ts": now(), "clip_id": r["clip_id"], "method": "azure", "rep": rep, "text": x["text"], "error": x["error"], "wall_s": x["wall_s"], "audio_s": round(secs, 3),
               "phrase_list": [], "jpy": round(jpy, 6)}
        append(rec, jpy, {"audio_s": round(secs, 3), "src": "Azure $1/audio-hour, ceil-seconds(er078_asr_unified_judge_01.py:110-113), 160JPY/USD"})


def cmd_asr():
    import er005_cost_logger as cl
    cl.install(os.path.join(OUT, "asr_cl_raw_usage_log.jsonl"))
    man = load_man(); done = load_done(); jobs = []
    for rep in (1, 2):
        for r in man:
            if rep == 2 and r["clip_id"] not in REP2:
                continue
            for m in ("openai", "azure"):
                if (r["clip_id"], m, rep) not in done:
                    jobs.append((r, m, rep))
    print("asr jobs", len(jobs))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda j: job(*j), jobs))
    print("done wall_s", round(time.time() - t0, 2), "spent_jpy(process)", round(_spent["jpy"], 4))


if __name__ == "__main__":
    {"manifest": cmd_manifest, "tts": cmd_tts, "asr": cmd_asr}[sys.argv[1]]()
