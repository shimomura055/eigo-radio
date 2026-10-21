# ============================================================
# er091_asr_three_way_trial_01_run.py  (ASR-THREE-WAY-COMPARISON-TRIAL-01 Phase 1/2 runner)
# 使い方: python er091_asr_three_way_trial_01_run.py manifest | whisper | whisper_par <N> | api | stab
# - manifest: dataset_manifest.jsonl(正常+問題+ledger Phrase List snapshot)を作る(API 0)
# - whisper:  faster-whisper small(cpu int8)を全音声に直列実行(Production = er008_disfluency_qa_18.transcribe_verbatim)。無料
# - api:      OpenAI gpt-4o-mini-transcribe(neutral/prod)・Azure Speech en-US(neutral/prod[Phrase List weight 2.0])を並列実行(有料)
# - stab:     安定性用の追加反復(短尺KP 20本 x 追加2回、3方式)
# 結果は results/asr_raw.jsonl に追記。既に結果のあるkey(id,method,cond,rep)は再実行しない(再課金防止)。
# Production codeは呼ぶだけ。Primary/Secondary/Validatorの変更は一切しない。共有ログへは書かない(cost loggerはTrial dir)。
# ============================================================
from __future__ import annotations
import hashlib
import json
import math
import os
import subprocess
import sys
import threading
import time
import wave
from concurrent.futures import ThreadPoolExecutor

OUT = "er091_output/asr_three_way_trial_01"
RES = os.path.join(OUT, "results")
os.makedirs(RES, exist_ok=True)
RAW = os.path.join(RES, "asr_raw.jsonl")
PAID = os.path.join(OUT, "paid_calls.jsonl")
MANIFEST = os.path.join(OUT, "dataset_manifest.jsonl")
JPY_PER_USD = 160.0                      # er078_asr_unified_judge_01.py:80
OPENAI_IN_PER_M, OPENAI_OUT_PER_M = 1.25, 5.0   # er005_output/cost_baseline_01/pricing_snapshot.json
AZURE_USD_PER_HOUR = 1.0                 # 同(Azure S0/S1 real-time)
GUARDRAIL_STOP_JPY = 200.0               # T-3 Guardrail 250 の手前で自動停止
_lock = threading.Lock()
_spent = {"jpy": 0.0}


def wav_sec(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def load_manifest():
    return [json.loads(l) for l in open(MANIFEST, encoding="utf-8") if l.strip()]


def load_done():
    done = set()
    if os.path.exists(RAW):
        for l in open(RAW, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                done.add((r["id"], r["method"], r["cond"], r["rep"]))
    return done


def append(rec, paid_jpy=0.0, paid_detail=None):
    with _lock:
        with open(RAW, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if paid_jpy or paid_detail:
            _spent["jpy"] += paid_jpy
            with open(PAID, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": rec["ts"], "id": rec["id"], "method": rec["method"], "cond": rec["cond"], "rep": rec["rep"],
                                    "jpy": round(paid_jpy, 5), "cum_this_process_jpy": round(_spent["jpy"], 4), **(paid_detail or {})},
                                   ensure_ascii=False) + "\n")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------- manifest
def cmd_manifest():
    import er006_pronunciation_ledger_01 as pl
    rows = [json.loads(l) for l in open(os.path.join(OUT, "dataset_manifest_normal.jsonl"), encoding="utf-8")]
    for r in rows:
        r.setdefault("problem_type", None)
    # 既知NG(ユーザー聴感「take tart」)
    src = os.path.join(OUT, "audio", "orig", "takepart_invalid_kp4_en.wav")
    rows.append({"id": "prob_kp_takepart_user_reported", "wav": src.replace("\\", "/"), "wav_sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                 "duration_s": round(wav_sec(src), 3), "kind": "kp", "canonical": "take part", "family": "X", "level": "Standard",
                 "article": "manga_ai_chat_byus", "segment": "kp4_en", "label": "problem", "label_class": "problem_known_user_reported",
                 "label_strength": "human_listened_user_report", "problem_type": "consonant_swap(p->t)_user_heard_take_tart",
                 "label_basis": "docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_KP-TAKE-PART_USER.md:16 ユーザー聴感『take tartのように聞こえる』。Task Aが無効化(kp4_en.invalid_20261021.wav、sha 675cd6b1…)",
                 "production_time_asr_text": "Take part.", "tags": ["kp_short_2w", "known_ng"]})
    # 過去Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01)の固有名詞minimal pair音声を再利用(構成ラベル: TTSにMelos/Mello/Melon/Mullosを読ませた)。
    pw = "er084_output/azure_phraselist_weight_trial_01/wav/"
    m1 = json.load(open(pw + "manifest_01.json", encoding="utf-8"))["audio"]
    m2 = json.load(open(pw + "manifest_02.json", encoding="utf-8"))["audio"]
    want_pos = {"P1_nonsib_Aoede_take1", "P2_sib_Aoede_take1", "P3_final_Aoede_take1", "P4_mid_Aoede_take1", "P5_repeat_Aoede_take1",
                "P7_compete_Aoede_take1"}
    for a in m1 + m2:
        isneg = a["label"] == "negative"
        if a.get("slow6") or a["voice"] != "Aoede":
            continue
        if not isneg and a["id"] not in want_pos:
            continue
        if isneg and not a["id"].startswith("NM_"):
            continue
        rows.append({"id": "plw_" + a["id"], "wav": a["path"], "wav_sha256": a["sha256"], "duration_s": a["duration_s"], "kind": "body",
                     "canonical": a["canonical_text"] if isneg else a["text"], "family": "Z", "level": "Standard", "article": "plw_trial_01",
                     "segment": a["id"], "label": "problem" if isneg else "normal",
                     "label_class": "problem_constructed_tts_plw" if isneg else "normal_constructed_tts_plw",
                     "label_strength": "construction(TTSにその綴りを読ませた; 過去Trial FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、人間試聴ではない)",
                     "problem_type": f"proper_noun_misreading({a['confusable']})" if isneg else None,
                     "spoken_text_requested": a["text"], "label_basis": f"{pw}manifest_0{'2' if a['id'].startswith('NM_') else '1'}.json id={a['id']}",
                     "tags": ["synthetic_tts", "proper_noun", "plw_trial_reuse"]})
    spl_all = []
    for nm in ("splice_log.json", "splice_log_v2.json"):
        pth = os.path.join(OUT, nm)
        if os.path.exists(pth):
            spl_all += json.load(open(pth, encoding="utf-8"))
    if True:
        for s in spl_all:
            rows.append({"id": s["id"], "wav": s["wav"], "wav_sha256": s["wav_sha256"], "duration_s": s["duration_s"], "kind": s["kind"],
                         "canonical": s["canonical"], "family": s["family"], "level": s["level"], "article": "splice_from_" + s["source_id"],
                         "segment": s["source_id"], "label": "problem", "label_class": "problem_constructed_splice",
                         "label_strength": "construction(word physically removed/duplicated; not human listened)",
                         "problem_type": s["error_type"], "label_basis": f"{s['op']} '{s['target_word']}' from {s['source_id']} (splice_log.json)",
                         "tags": ["synthetic_splice"]})
    tl = os.path.join(OUT, "tts_construct_log.json")
    tts_items = []
    if os.path.exists(tl):
        tts_items = json.load(open(tl, encoding="utf-8"))
    else:  # TTS実行中でも完了済みwavだけ取り込む
        import er091_asr_three_way_trial_01_tts_construct as tc
        for rid, kind, canon, spoken, etype in tc.ITEMS:
            p = os.path.join(OUT, "audio", "tts_construct", rid + ".wav")
            if os.path.exists(p):
                tts_items.append({"id": rid, "kind": kind, "canonical": canon, "spoken_text_requested": spoken, "error_type": etype,
                                  "status": "OK", "path": p})
    for t in tts_items:
        if t.get("status") != "OK" or not os.path.exists(t["path"]):
            continue
        rows.append({"id": t["id"], "wav": t["path"].replace("\\", "/"), "wav_sha256": hashlib.sha256(open(t["path"], "rb").read()).hexdigest(),
                     "duration_s": round(wav_sec(t["path"]), 3), "kind": t["kind"], "canonical": t["canonical"],
                     "family": "Z" if "melos" in t["id"] or "threedays" in t["id"] or "return" in t["id"] else "X", "level": "Standard",
                     "article": "tts_construct", "segment": t["id"], "label": "problem", "label_class": "problem_constructed_tts",
                     "label_strength": "construction(TTSに台本と異なる文面を読ませた; not human listened)",
                     "problem_type": t["error_type"], "spoken_text_requested": t["spoken_text_requested"],
                     "label_basis": f"er091_asr_three_way_trial_01_tts_construct.py: canonical='{t['canonical']}' / TTS requested='{t['spoken_text_requested']}'",
                     "tags": ["synthetic_tts"]})
    seen = {}
    for r in rows:
        r["ledger_phrases"] = [h["canonical_spelling"] for h in pl.get_hint_for_text(r["canonical"], min_confidence="low")]
        k = r["wav_sha256"]
        r["duplicate_of"] = seen.get(k)
        seen.setdefault(k, r["id"])
    with open(MANIFEST, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    import collections
    print(len(rows), collections.Counter((r["label"], r["kind"]) for r in rows), "dups", sum(1 for r in rows if r["duplicate_of"]))
    print("with ledger phrases:", [(r["id"], r["ledger_phrases"]) for r in rows if r["ledger_phrases"]])


def active_rows():
    return [r for r in load_manifest() if not r["duplicate_of"]]


# ---------------------------------------------------------------- whisper
def whisper_one(wav):
    import er008_disfluency_qa_18 as dq18
    t = time.time()
    c = time.process_time()
    words = dq18.transcribe_verbatim(wav, language="en", model_size="small")
    return {"text": " ".join(w["text"] for w in words).strip(), "words": words, "wall_s": round(time.time() - t, 3),
            "cpu_s": round(time.process_time() - c, 3)}


def cmd_whisper(reps=(1,), ids=None):
    import er008_disfluency_qa_18 as dq18
    dq18._get_model("small")   # モデルロード(初回)を計測から外す
    done = load_done()
    rows = active_rows()
    if ids:
        rows = [r for r in rows if r["id"] in ids]
    for rep in reps:
        for r in rows:
            if (r["id"], "whisper", "prod", rep) in done:
                continue
            x = whisper_one(r["wav"])
            append({"ts": now(), "id": r["id"], "method": "whisper", "cond": "prod", "rep": rep, "text": x["text"], "error": None,
                    "wall_s": x["wall_s"], "cpu_s": x["cpu_s"], "audio_s": round(wav_sec(r["wav"]), 3), "words": x["words"],
                    "config": "faster_whisper small cpu int8 language=en word_timestamps=True condition_on_previous_text=False vad_filter=False (dq18.transcribe_verbatim)"})
    print("whisper done")


def cmd_whisper_worker(listfile, outfile):
    import er008_disfluency_qa_18 as dq18
    dq18._get_model("small")
    ids = json.load(open(listfile, encoding="utf-8"))
    man = {r["id"]: r for r in load_manifest()}
    out = []
    t0 = time.time()
    c0 = time.process_time()
    for i in ids:
        x = whisper_one(man[i]["wav"])
        out.append({"id": i, "wall_s": x["wall_s"], "cpu_s": x["cpu_s"], "text": x["text"]})
    json.dump({"items": out, "total_wall_s": round(time.time() - t0, 3), "total_cpu_s": round(time.process_time() - c0, 3)},
              open(outfile, "w", encoding="utf-8"), ensure_ascii=False)


def cmd_whisper_par(n):
    """n個の独立processでWhisperを同時実行し、直列時の合計と比較する(同一サブセット)。"""
    rows = [r for r in active_rows() if r["duration_s"] <= 8][:24]
    ids = [r["id"] for r in rows]
    done = {}
    for l in open(RAW, encoding="utf-8"):
        x = json.loads(l)
        if x["method"] == "whisper" and x["rep"] == 1:
            done[x["id"]] = x["wall_s"]
    serial_sum = round(sum(done[i] for i in ids), 3)
    chunks = [ids[k::n] for k in range(n)]
    procs = []
    t0 = time.time()
    for k, ch in enumerate(chunks):
        lf = os.path.join(RES, f"_wpar{n}_{k}_list.json")
        json.dump(ch, open(lf, "w", encoding="utf-8"))
        of = os.path.join(RES, f"_wpar{n}_{k}_out.json")
        procs.append((subprocess.Popen([sys.executable, __file__, "whisper_worker", lf, of]), of))
    for p, _ in procs:
        p.wait()
    wall = round(time.time() - t0, 3)
    outs = [json.load(open(of, encoding="utf-8")) for _, of in procs]
    rec = {"n_processes": n, "n_items": len(ids), "audio_total_s": round(sum(r["duration_s"] for r in rows), 2),
           "serial_sum_wall_s(first pass, same items)": serial_sum, "parallel_total_wall_incl_model_load_s": wall,
           "per_process_total_wall_s": [o["total_wall_s"] for o in outs], "per_process_total_cpu_s": [o["total_cpu_s"] for o in outs],
           "per_item_mean_wall_s": round(sum(i["wall_s"] for o in outs for i in o["items"]) / len(ids), 3),
           "per_item_mean_wall_serial_s": round(serial_sum / len(ids), 3), "cpu_count": os.cpu_count()}
    with open(os.path.join(RES, "whisper_parallel.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(rec)


def cmd_whisper_medium():
    """smallの誤りがモデル容量由来かの確認(委任文: 実測で示された場合に限り1サイズ追加)。small単独verdictがNGの正常音声+全KPのみ(無料・ローカル)。"""
    import er008_disfluency_qa_18 as dq18
    import er091_asr_three_way_trial_01_analyze as an
    res = json.load(open(os.path.join(RES, "phase12_item_results.json"), encoding="utf-8"))
    bad = {r["id"] for r in res if r["method"] == "whisper" and r["cond"] == "prod" and not r["verdict_pass"]}
    rows = [r for r in active_rows() if os.environ.get("MEDIUM_ALL") or r["kind"] == "kp" or r["id"] in bad]
    done = load_done()
    dq18._get_model("medium")
    for r in rows:
        if (r["id"], "whisper_medium", "prod", 1) in done:
            continue
        t = time.time()
        c = time.process_time()
        words = dq18.transcribe_verbatim(r["wav"], language="en", model_size="medium")
        append({"ts": now(), "id": r["id"], "method": "whisper_medium", "cond": "prod", "rep": 1,
                "text": " ".join(w["text"] for w in words).strip(), "error": None, "wall_s": round(time.time() - t, 3),
                "cpu_s": round(time.process_time() - c, 3), "audio_s": round(wav_sec(r["wav"]), 3),
                "config": "faster_whisper medium cpu int8 language=en (dq18.transcribe_verbatim model_size=medium)"})
    print("whisper medium done", len(rows))


# ---------------------------------------------------------------- API
def openai_call(wav, prompt):
    import er006_asr_provider_routing_01 as routing
    client = routing._get_openai_client()
    t = time.time()
    try:
        with open(wav, "rb") as f:
            kw = {"model": routing.ASR_ROUTING["en"]["model"], "file": f, "language": "en"}   # Production(_transcribe_openai_mini)同一のkwargs
            if prompt:
                kw["prompt"] = prompt
            resp = client.audio.transcriptions.create(**kw)
        u = getattr(resp, "usage", None)
        return {"text": resp.text, "error": None, "wall_s": round(time.time() - t, 3), "in_tok": getattr(u, "input_tokens", None),
                "out_tok": getattr(u, "output_tokens", None), "request_id": getattr(resp, "_request_id", None), "model": kw["model"]}
    except Exception as exc:  # noqa: BLE001
        return {"text": None, "error": str(exc)[:300], "wall_s": round(time.time() - t, 3), "in_tok": 0, "out_tok": 0}


def azure_call(wav, phrases):
    import er006_secondary_asr_01 as sec
    t = time.time()
    try:
        text, err = sec.get_full_text_via_azure_stt_with_phrase_list(wav, language="en-US", phrases=phrases or None)
    except Exception as exc:  # noqa: BLE001
        text, err = None, f"{type(exc).__name__}: {exc}"[:300]
    return {"text": text, "error": err, "wall_s": round(time.time() - t, 3)}


def job(r, method, cond, rep):
    if _spent["jpy"] > GUARDRAIL_STOP_JPY:
        return
    from er006_asr_provider_routing_01 import _lang_key  # noqa: F401
    import er003_v1_repro01_main_generate as gen
    wav = r["wav"]
    secs = wav_sec(wav)
    if method == "openai":
        prompt = gen.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT if (cond == "prod" and r["kind"] == "kp") else None
        x = openai_call(wav, prompt)
        jpy = ((x["in_tok"] or 0) * OPENAI_IN_PER_M + (x["out_tok"] or 0) * OPENAI_OUT_PER_M) / 1e6 * JPY_PER_USD
        rec = {"ts": now(), "id": r["id"], "method": "openai", "cond": cond, "rep": rep, "text": x["text"], "error": x["error"],
               "wall_s": x["wall_s"], "audio_s": round(secs, 3), "prompt_sent": prompt, "in_tok": x["in_tok"], "out_tok": x["out_tok"],
               "request_id": x.get("request_id"), "model": x.get("model"), "jpy": round(jpy, 6)}
        append(rec, jpy, {"in_tok": x["in_tok"], "out_tok": x["out_tok"], "audio_s": round(secs, 3), "src": "pricing_snapshot.json $1.25/$5.0 per M, 160JPY/USD"})
    else:
        phrases = r["ledger_phrases"] if cond == "prod" else None
        x = azure_call(wav, phrases)
        jpy_ceil = math.ceil(secs) * AZURE_USD_PER_HOUR / 3600.0 * JPY_PER_USD
        jpy_exact = secs * AZURE_USD_PER_HOUR / 3600.0 * JPY_PER_USD
        rec = {"ts": now(), "id": r["id"], "method": "azure", "cond": cond, "rep": rep, "text": x["text"], "error": x["error"],
               "wall_s": x["wall_s"], "audio_s": round(secs, 3), "phrase_list": phrases or [], "phrase_list_weight": 2.0 if phrases else None,
               "jpy": round(jpy_ceil, 6), "jpy_exact_seconds": round(jpy_exact, 6)}
        append(rec, jpy_ceil, {"audio_s": round(secs, 3), "src": "Azure S0/S1 $1/audio-hour, ceil-seconds (er078_asr_unified_judge_01.py:110-113)"})


def plan_api(rows, rep=1):
    done = load_done()
    jobs = []
    for r in rows:
        # neutral
        for m in ("openai", "azure"):
            if (r["id"], m, "neutral", rep) not in done:
                jobs.append((r, m, "neutral", rep))
        # prod: 実際に条件が異なる場合のみ追加呼出(openai=KPのみ prompt付き / azure=Phrase Listがある場合のみ)
        if r["kind"] == "kp" and (r["id"], "openai", "prod", rep) not in done:
            jobs.append((r, "openai", "prod", rep))
        if r["ledger_phrases"] and (r["id"], "azure", "prod", rep) not in done:
            jobs.append((r, "azure", "prod", rep))
    return jobs


def run_jobs(jobs, workers=6):
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda j: job(*j), jobs))
    print("jobs", len(jobs), "wall", round(time.time() - t0, 2), "spent_jpy(process)", round(_spent["jpy"], 3))


def est(jobs):
    tot = 0.0
    for r, m, c, rep in jobs:
        if m == "openai":
            tot += 0.0022   # 約60in/6out token実績(er088)=JPY0.0154/回 を上限目安
        else:
            tot += math.ceil(r["duration_s"]) / 3600.0 * 160
    return round(tot, 3)


def stab_ids(rows):
    kp = [r for r in rows if r["kind"] == "kp"]
    prob = [r for r in kp if r["label"] == "problem"]
    norm = [r for r in kp if r["label"] == "normal"]
    pick = norm[:: max(1, len(norm) // (20 - len(prob)))][: 20 - len(prob)]
    return [r["id"] for r in pick + prob][:20]


def cmd_api(dry=False):
    import er005_cost_logger as cl
    cl.install(os.path.join(RES, "cl_raw_usage_log.jsonl"))
    rows = active_rows()
    jobs = plan_api(rows, 1)
    print("api jobs", len(jobs), "est_jpy", est(jobs))
    if dry:
        return
    run_jobs(jobs)


def cmd_stab(dry=False):
    import er005_cost_logger as cl
    cl.install(os.path.join(RES, "cl_raw_usage_log.jsonl"))
    rows = active_rows()
    ids = set(stab_ids(rows))
    sub = [r for r in rows if r["id"] in ids]
    jobs = []
    done = load_done()
    for rep in (2, 3):
        for r in sub:
            if (r["id"], "openai", "prod", rep) not in done:
                jobs.append((r, "openai", "prod", rep))
            if (r["id"], "azure", "prod", rep) not in done:
                jobs.append((r, "azure", "prod", rep))
    print("stab items", sorted(ids), "jobs", len(jobs), "est_jpy", est(jobs))
    json.dump(sorted(ids), open(os.path.join(RES, "stability_ids.json"), "w"))
    if dry:
        return
    run_jobs(jobs)
    cmd_whisper(reps=(2, 3), ids=ids)


if __name__ == "__main__":
    a = sys.argv[1:]
    c = a[0]
    if c == "manifest":
        cmd_manifest()
    elif c == "whisper":
        cmd_whisper()
    elif c == "whisper_medium":
        cmd_whisper_medium()
    elif c == "whisper_par":
        cmd_whisper_par(int(a[1]))
    elif c == "whisper_worker":
        cmd_whisper_worker(a[1], a[2])
    elif c == "api":
        cmd_api(dry=("--dry" in a))
    elif c == "stab":
        cmd_stab(dry=("--dry" in a))
