# -*- coding: utf-8 -*-
"""第2巡 有料生成: 現行TTS(Productionと同じmodel/voice/style設定値を読み取り、TTSクライアント関数を直接呼ぶ)で
 (take1/take2) HR事象30 segmentの実本文、(neg) 負例28本 を生成し、4エンジンで書き起こす。
 Production runner/Review Lock/Master Audio Store/HR queue/attempt_historyは経由せず、書込まない(実行前後でsha256を比較しassert)。
 phase: plan(0円) / take1 / neg / take2。各phaseは1回だけ起動する(再起動しない)。
 ASR: OpenAI Primary(routing.transcribe)・Azure(p4)はtarget文を含む窓(約12秒超の音声のみ)へ切り出して送る(費用上限のため。限界として開示)。
      ローカルWhisper small/mediumは全音声(0円)。窓位置はWhisper mediumの単語時刻とcanonicalのdifflib整列で決める。
 予算ガード: r2/paid_calls.jsonl 累計 >= GUARD_STOP のとき新規有料呼出をしない。"""
import difflib, hashlib, json, os, re, sys, threading, time
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_replay as RP

R2 = Path(OUT) / "r2"
AUD = R2 / "audio"
LEDGER = R2 / "paid_calls.jsonl"
MODEL = "gemini-3.8-flash-lite-tts"
VOICE = "Aoede"
GUARD_STOP = 75.0
USD_JPY = 160.0
LOCK = threading.Lock()
WLOCK = threading.Lock()

PROTECT = ["er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", "er011_output/attempt_history.jsonl",
           "er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl"]

# 負例の綴り替え(TTSへ渡す文字列): 語ごと{C=子音置換,V=強勢母音置換,S=音節(または語頭)脱落,F=語末子音脱落}
NEG_VARIANTS = {
    "khaite": {"C": "Bate", "V": "Kite", "S": "Ate", "F": "Kay"},
    "meink": {"C": "Teenk", "V": "Monk", "S": "Ink", "F": "Meen"},
    "altuzarra": {"C": "Ahl-poo-ZAH-rah", "V": "Ahl-too-ZOH-rah", "S": "Ahl-ZAH-rah", "F": "Ahl-too-ZAH-ah"},
    "toteme": {"C": "Poteme", "V": "Toh-TIME", "S": "Tem", "F": "Tote"},
    "zabelina": {"C": "Labelina", "V": "Zah-BOO-lee-nah", "S": "Zalina", "F": "Zabelia"},
    "canele": {"C": "Panele", "V": "Kah-NOO-lay", "S": "Kanay", "F": "Canel"},
    "melos": {"C": "Belos", "V": "Molos", "S": "Mos", "F": "Melo"},
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def protect_snapshot():
    snap = {}
    for p in PROTECT:
        if os.path.exists(p):
            snap[p] = {"sha256": sha(p), "lines": sum(1 for _ in open(p, "rb")), "size": os.path.getsize(p)}
        else:
            snap[p] = None
    return snap


def ledger_add(rec):
    with LOCK:
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ledger_total():
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l).get("cost_jpy", 0) for l in open(LEDGER, encoding="utf-8") if l.strip())


def tts_settings():
    import er019_family_x_style_profile_01 as xs
    text = xs.PD06_TEXT
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == xs.PD06_SHA256, "PD06 sha不一致"
    z_src = open("er063_family_z_audio_01.py", encoding="utf-8").read()
    assert xs.PD06_SHA256 in z_src or "PD06" in z_src
    return {"model": MODEL, "voice": VOICE, "style_label": "PD06", "style_sha256": xs.PD06_SHA256, "style_text": text,
            "source": "er019_family_x_style_profile_01.PD06_TEXT(FULL_STORY現行profile fx_20261017/Family Z NARRATOR_FULL_STORY=PD06、er063:165-172)、voice=Aoede(er019 runner Full Story Part=Aoede)、backend=speech_metadata_flash_lite(er063:72)",
            "not_replicated": "生成後6%減速(Std)・Production再試行/ASR検証ループ・Store再利用は経由しない"}


def plan():
    rows = load_rows()
    segs, order = {}, []
    for r in rows:
        lk = list((r.get("pronunciation_lookups") or {}).keys())
        t = [w for w in lk if w in TARGETS]
        if not t:
            continue
        c = r["canonical_text"]
        if c not in segs:
            segs[c] = {"words": set(), "events": 0, "first_ts": r["timestamp"], "wav": os.path.basename(r["wav_path"].replace("\\", "/"))}
            order.append(c)
        segs[c]["words"].update(t)
        segs[c]["events"] += 1
    est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
    seglist = []
    for i, c in enumerate(order, 1):
        d = segs[c]
        ws = sorted(d["words"])
        seglist.append({"id": f"s{i:02d}", "text": c, "words": ws, "family": "Z" if "melos" in ws else "X", "hr_events": d["events"], "first_ts": d["first_ts"], "orig_clip": d["wav"]})
    negs = []
    for w, vs in NEG_VARIANTS.items():
        sent = est[w]["sentence"]
        for k, rep in vs.items():
            pat = re.compile(r"\b" + re.escape({"canele": "Canele"}.get(w, w)) + r"\b", re.I)
            if not pat.search(sent):
                pat = re.compile(re.escape(w), re.I)
            tts_text = pat.sub(rep, sent, count=1)
            negs.append({"id": f"n_{w}_{k}", "word": w, "kind": k, "respell": rep, "canon": sent, "tts_text": tts_text})
    for k, rep in (("F2", "Melo"), ("C2", "Belos")):   # 縮約文脈(次語がS始まり)の負例: 真の語末子音脱落が縮約と区別できるか(S2R-03)
        negs.append({"id": f"n_melos_{k}", "word": "melos", "kind": k, "respell": rep, "canon": "Melos said.", "tts_text": f"{rep} said."})
    json.dump({"segments": seglist, "negatives": negs, "tts_settings": tts_settings()}, open(R2 / "plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(seglist), "segments", len(negs), "negatives")
    for s in seglist:
        print(s["id"], s["family"], s["words"], len(s["text"]), s["hr_events"])


# ---------------- 窓切り出し ----------------
def whisper_words(wav):
    from faster_whisper import WhisperModel
    with WLOCK:
        if "m" not in globals().get("_WM", {}):
            globals().setdefault("_WM", {})["m"] = WhisperModel("medium", device="cpu", compute_type="int8", local_files_only=True)
        segs, _ = _WM["m"].transcribe(wav, language="en", beam_size=5, vad_filter=False, word_timestamps=True)
        words, text = [], []
        for s in segs:
            text.append(s.text.strip())
            for w in (s.words or []):
                words.append((w.word, w.start, w.end))
    return " ".join(text), words


def whisper_small(wav):
    from faster_whisper import WhisperModel
    with WLOCK:
        if "s" not in globals().get("_WM", {}):
            globals().setdefault("_WM", {})["s"] = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
        segs, _ = _WM["s"].transcribe(wav, language="en", beam_size=5, vad_filter=False)
        return " ".join(s.text.strip() for s in segs)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def window_for(canon, words_in_canon, wwords, dur):
    """canonicalのtarget語を含む文群 -> (t0,t1,canon_sub)。整列失敗はNone。"""
    sents = sentences(canon)
    idx = [i for i, s in enumerate(sents) if any(w in norm_tokens(s) for w in words_in_canon)]
    if not idx:
        return None
    a, b = min(idx), max(idx)
    pre = [t for s in sents[:a] for t in norm_tokens(s)]
    mid = [t for s in sents[a:b + 1] for t in norm_tokens(s)]
    ctoks = norm_tokens(canon)
    wt = []
    for w, st, en in wwords:
        for t in norm_tokens(w):
            wt.append((t, st, en))
    sm = difflib.SequenceMatcher(a=ctoks, b=[x[0] for x in wt], autojunk=False)
    cmap = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                cmap[i1 + k] = j1 + k
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                cmap[i1 + k] = j1 + k
    i_start, i_end = len(pre), len(pre) + len(mid) - 1
    s_idx = next((cmap[i] for i in range(i_start, i_end + 1) if i in cmap), None)
    e_idx = next((cmap[i] for i in range(i_end, i_start - 1, -1) if i in cmap), None)
    if s_idx is None or e_idx is None or e_idx < s_idx:
        return None
    t0 = max(0.0, wt[s_idx][1] - (0.35 if i_start in cmap else 0.9))
    t1 = min(dur, wt[e_idx][2] + (0.45 if i_end in cmap else 1.0))
    return t0, t1, " ".join(sents[a:b + 1])


def cut(wav, t0, t1, out):
    import soundfile as sf
    d, sr = sf.read(wav, dtype="float32")
    sf.write(out, d[int(t0 * sr):int(t1 * sr)], sr, subtype="PCM_16")
    return (t1 - t0)


# ---------------- 有料呼出 ----------------
_tts_call = []


def tts_to_wav(text, out_wav, settings):
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1 as ST1
    if not _tts_call:
        _tts_call.append(ST1.make_tts_call_fn(MODEL, VOICE))
    t0 = time.time()
    raw = _tts_call[0](text, settings["style_text"])
    samples, _sr, _hdr = ST1.decode_audio_bytes_defensive(raw)
    trimmed, _info = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.EN_TRIM_SAFETY_MARGIN_SECONDS)
    use = trimmed if trimmed is not None else samples
    common.write_wav_float(str(out_wav), use, common.SAMPLE_RATE, 1)
    sec = len(use) / common.SAMPLE_RATE
    out_tokens = len(samples) / common.SAMPLE_RATE * 25
    in_tokens = max(1, int(len(text) / 4))
    usd = (in_tokens * 0.5 + out_tokens * 6.0) / 1e6
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "r2_tts", "model": MODEL, "voice": VOICE, "wav": str(out_wav), "sec": round(sec, 2), "cost_jpy": round(usd * USD_JPY, 4),
                "basis": "pricing_snapshot.json gemini-3.8-flash-lite-tts 0.5/6.0 USD per M tokens(出力25 tok/s換算); 入力tokens=len/4の概算", "fx": "USD_JPY=160(project default)", "elapsed_s": round(time.time() - t0, 1)})
    return sec


def api_asr(wav, sec):
    import er003_b1_p4_audio as p4
    import er006_asr_provider_routing_01 as routing
    out = {}
    pt, perr = routing.transcribe(str(wav), "en-US")
    out["primary"] = pt
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "r2_asr_openai", "model": "gpt-4o-mini-transcribe", "wav": str(wav), "sec": round(sec, 2),
                "cost_jpy": round(sec / 60 * 0.006 * USD_JPY, 4), "basis": "上限見積 USD0.006/min(秒換算単価は未確認のため上限)", "err": perr})
    at, aerr = p4.get_full_text_via_azure_stt_continuous(str(wav), language="en-US", timeout_seconds=90)
    out["azure"] = at
    ledger_add({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "r2_asr_azure", "wav": str(wav), "sec": round(sec, 2),
                "cost_jpy": round(sec / 3600 * 1.0 * USD_JPY, 5), "basis": "pricing_snapshot Azure STT $1.0/audio_hour", "err": aerr})
    return out


def process(item, settings, tag):
    """item: id,text(tts_text),canon,words。1音声の生成+4エンジン書き起こし。"""
    res = {k: item[k] for k in ("id", "kind", "word", "words", "family", "canon", "tts_text") if k in item}
    res["take"] = tag
    wav = AUD / f"{item['id']}__{tag}.wav"
    res["wav"] = str(wav)
    if ledger_total() >= GUARD_STOP:
        res["error"] = "BUDGET_GUARD_STOP(未生成)"
        return res
    try:
        sec = tts_to_wav(item["tts_text"], wav, settings)
        res["sec"] = round(sec, 2)
        mtext, words = whisper_words(str(wav))
        res["whisper_medium"] = mtext
        res["whisper_small"] = whisper_small(str(wav))
        scope, send, clip_canon = "full", str(wav), item["canon"]
        if sec > 12.0:
            w = window_for(item["canon"], item.get("words") or [item["word"]], words, sec)
            if w:
                t0, t1, csub = w
                cwav = AUD / f"{item['id']}__{tag}__clip.wav"
                cs = cut(str(wav), t0, t1, str(cwav))
                scope, send, clip_canon = f"clip[{t0:.2f}-{t1:.2f}s]", str(cwav), csub
                sec_send = cs
            else:
                sec_send = sec
                scope = "full(窓整列失敗)"
        else:
            sec_send = sec
        if ledger_total() >= GUARD_STOP + 4:
            res["error"] = "BUDGET_GUARD_STOP(ASR前)"
            return res
        a = api_asr(send, sec_send)
        res.update(primary=a["primary"], azure=a["azure"], api_scope=scope, api_sec=round(sec_send, 2), api_canon=clip_canon)
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    return res


def run(phase):
    plan_d = json.load(open(R2 / "plan.json", encoding="utf-8"))
    settings = plan_d["tts_settings"]
    AUD.mkdir(parents=True, exist_ok=True)
    before = protect_snapshot()
    json.dump(before, open(R2 / f"protect_before_{phase}.json", "w"), indent=1)
    if phase in ("take1", "take2"):
        items = [{"id": s["id"], "text": s["text"], "tts_text": s["text"], "canon": s["text"], "words": s["words"], "family": s["family"], "word": s["words"][0]} for s in plan_d["segments"]]
        if phase == "take2":
            items = [i for i in items if i["id"] in set(json.load(open(R2 / "take2_ids.json")))]
        tag = "t1" if phase == "take1" else "t2"
    else:
        items = [{"id": n["id"], "kind": n["kind"], "word": n["word"], "words": [n["word"]], "canon": n["canon"], "tts_text": n["tts_text"]} for n in plan_d["negatives"]]
        tag = "t1"
    out_path = R2 / f"gen_{phase}.json"
    results = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(lambda it: process(it, settings, tag), items):
            results.append(r)
            print(r["id"], r.get("sec"), r.get("api_scope"), r.get("error", ""), round(ledger_total(), 2), flush=True)
            json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    after = protect_snapshot()
    json.dump(after, open(R2 / f"protect_after_{phase}.json", "w"), indent=1)
    assert before == after, "保護対象ファイル(HR queue/attempt_history/Store)が変化した"
    print("PROTECTED_UNCHANGED", phase, "ledger total jpy", round(ledger_total(), 3))


if __name__ == "__main__":
    ph = sys.argv[1]
    plan() if ph == "plan" else run(ph)
