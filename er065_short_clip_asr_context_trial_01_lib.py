# -*- coding: utf-8 -*-
"""FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 (Trial / DEV only).

短尺clipのASR評価を文脈付き(前後clip結合)にしたときの安定性を実測するための共通部品。
Production経路には一切配線しない。作品固有語はconfig/引数で与える(ここにMelos固有値は無い)。

- write guard: sys.addaudithookで、許可dir外へのファイル書込をブロック+記録(Production state保護)。
- audio: wav読込/リサンプル/無音gap結合(オフライン、無料)。
- ASR: OpenAI gpt-4o-mini-transcribe(logprobs)、Azure STT(PhraseList+word timestamps)、local faster-whisper。
- 整列: 期待テキストと転写をdifflibで整列し、target領域の転写を抽出。
- cost: 呼出ごとにJSONLへ記録(USD/JPY=160)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import wave
from typing import Optional

import numpy as np

USD_JPY = 160.0
OPENAI_IN_USD_PER_M = 1.25   # pricing_snapshot.json gpt-4o-mini-transcribe input_tokens (OFFICIAL_SOURCE)
OPENAI_OUT_USD_PER_M = 5.0   # 同 output_tokens
AZURE_USD_PER_HOUR = 1.0     # pricing_snapshot.json azure audio_hour (Retail Prices API)

# ---------------------------------------------------------------- write guard
_GUARD = {"allowed": [], "blocked": [], "writes": [], "active": False}


def _norm(p) -> str:
    try:
        return os.path.normcase(os.path.abspath(str(p)))
    except Exception:
        return str(p)


def _audit(event, args):
    if event != "open" or not _GUARD["active"]:
        return
    path, mode = args[0], args[1]
    if isinstance(path, int) or path is None:
        return
    mode = mode if isinstance(mode, str) else ""
    flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
    is_write = any(c in mode for c in "wax+") or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT))
    if not is_write:
        return
    p = _norm(path)
    if "__pycache__" in p or os.path.basename(p).lower() in ("nul", "conout$", "conin$"):
        return
    for a in _GUARD["allowed"]:
        if p.startswith(a):
            _GUARD["writes"].append(p)
            return
    _GUARD["blocked"].append(p)
    raise PermissionError(f"er065 write guard: blocked write outside allowed dirs: {p}")


_hook_installed = False


def install_write_guard(allowed_dirs):
    global _hook_installed
    _GUARD["allowed"] = [_norm(d) for d in allowed_dirs]
    _GUARD["active"] = True
    if not _hook_installed:
        sys.addaudithook(_audit)
        _hook_installed = True


def write_guard_report() -> dict:
    return {"allowed_dirs": list(_GUARD["allowed"]), "blocked_write_attempts": list(_GUARD["blocked"]),
            "n_writes_inside_allowed": len(_GUARD["writes"]),
            "write_dirs_seen": sorted({os.path.dirname(w) for w in _GUARD["writes"]})}


def count_lines(path: str) -> Optional[int]:
    if not os.path.exists(path):
        return None
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return n


def file_fingerprint(path: str) -> dict:
    if not os.path.exists(path):
        return {"exists": False}
    st = os.stat(path)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"exists": True, "bytes": st.st_size, "lines": count_lines(path), "sha256": h.hexdigest()[:16]}


# ---------------------------------------------------------------- audio
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_wav_mono(path: str, target_sr: int = 24000) -> np.ndarray:
    with wave.open(path, "rb") as w:
        n, sr, ch, sw = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    if sw != 2:
        raise ValueError(f"unsupported sampwidth {sw}: {path}")
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    if sr != target_sr:
        t_old = np.arange(len(a)) / sr
        t_new = np.arange(int(len(a) * target_sr / sr)) / target_sr
        a = np.interp(t_new, t_old, a).astype(np.float32)
    return a


def wav_duration(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate()


def write_wav(path: str, samples: np.ndarray, sr: int = 24000):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = np.clip(samples, -32768, 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm)


def concat_parts(parts, gap_ms: int, sr: int = 24000):
    """parts: [{path,...}] -> (samples, spans[{start,end}] 秒)。clip間にgap_ms無音を挿入。"""
    chunks, spans, t = [], [], 0.0
    gap = np.zeros(int(sr * gap_ms / 1000), dtype=np.float32)
    for i, p in enumerate(parts):
        a = read_wav_mono(p["path"], sr)
        spans.append({"start": round(t, 3), "end": round(t + len(a) / sr, 3)})
        chunks.append(a)
        t += len(a) / sr
        if i < len(parts) - 1:
            chunks.append(gap)
            t += len(gap) / sr
    return np.concatenate(chunks), spans


# ---------------------------------------------------------------- text
_TOK_RE = re.compile(r"[a-z0-9']+")


def norm_tokens(text: str):
    t = (text or "").lower().replace("’", "'")
    return _TOK_RE.findall(t)


def region_by_alignment(expected_parts, target_index: int, asr_text: str) -> dict:
    """expected_parts(各clipの期待テキスト列)とasr全文をdifflib整列し、target_index番目clipに対応するasrトークンを返す。"""
    import difflib
    exp, bounds = [], []
    for s in expected_parts:
        tk = norm_tokens(s)
        bounds.append((len(exp), len(exp) + len(tk)))
        exp.extend(tk)
    asr = norm_tokens(asr_text)
    ts, te = bounds[target_index]
    sm = difflib.SequenceMatcher(a=exp, b=asr, autojunk=False)
    toks, assigned = [], False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        ov0, ov1 = max(i1, ts), min(i2, te)
        if tag == "equal":
            # equalブロックはtoken単位で対応付け(ブロックがtarget境界をまたいでも文脈tokenを混入させない)
            for i in range(ov0, ov1):
                toks.append(asr[j1 + (i - i1)])
                assigned = True
        elif tag == "replace":
            if ov0 < ov1:
                n_exp, n_asr = i2 - i1, j2 - j1
                a = j1 + round((ov0 - i1) / n_exp * n_asr)
                b = j1 + round((ov1 - i1) / n_exp * n_asr)
                toks.extend(asr[a:b])
                assigned = True
        elif tag == "insert":
            if ts < i1 < te:
                toks.extend(asr[j1:j2])
                assigned = True
    return {"region_tokens": toks, "region_text": " ".join(toks), "assigned": assigned,
            "n_expected_tokens": te - ts, "whole_similarity": round(sm.ratio(), 4)}


def region_by_words(words, start: float, end: float, margin: float = 0.12) -> dict:
    """words: [{w,start,end,conf}] 秒。中点がtarget区間(+-margin)に入る語。"""
    sel = [w for w in words if start - margin <= (w["start"] + w["end"]) / 2 <= end + margin]
    confs = [w.get("conf") for w in sel if w.get("conf") is not None]
    return {"region_tokens": [w["w"] for w in sel], "region_text": " ".join(w["w"] for w in sel),
            "n_words": len(sel), "min_conf": min(confs) if confs else None}


def strip_words_punct(words):
    out = []
    for w in words:
        t = " ".join(norm_tokens(w["w"]))
        if t:
            out.append({**w, "w": t})
    return out


def logprob_region(logprobs, region_tokens) -> Optional[dict]:
    """OpenAI token logprobsから、target領域に対応する文字範囲のtoken logprobを概算で抽出(最後に出現するregion語列を探す)。"""
    if not logprobs or not region_tokens:
        return None
    toks = [(x["token"] or "") for x in logprobs]
    full = "".join(toks).lower()
    needle = " ".join(region_tokens)
    # 領域語列(空白区切り)を全文から検索(句読点を除去した版で)
    clean_chars, idx_map = [], []
    pos = 0
    for ti, t in enumerate(toks):
        for ch in t.lower().replace("’", "'"):
            clean_chars.append(ch if re.match(r"[a-z0-9']", ch) else " ")
            idx_map.append(ti)
    clean = re.sub(r"\s+", " ", "".join(clean_chars))
    # idx_mapは空白圧縮でずれるため、再構築
    comp_chars, comp_map, prev_space = [], [], False
    for ch, ti in zip(clean_chars, idx_map):
        if ch == " ":
            if prev_space:
                continue
            prev_space = True
        else:
            prev_space = False
        comp_chars.append(ch)
        comp_map.append(ti)
    comp = "".join(comp_chars)
    k = comp.rfind(needle)
    if k < 0:
        return None
    tis = sorted(set(comp_map[k:k + len(needle)]))
    lps = [logprobs[i]["logprob"] for i in tis if logprobs[i].get("logprob") is not None]
    if not lps:
        return None
    return {"min_logprob": round(min(lps), 4), "mean_logprob": round(sum(lps) / len(lps), 4), "n_tokens": len(lps)}


# ---------------------------------------------------------------- cost log
class CostLog:
    def __init__(self, path: str):
        self.path = path
        self.total_jpy = 0.0
        self.by_engine = {}
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                try:
                    r = json.loads(line)
                    self.total_jpy += r.get("jpy", 0)
                    self.by_engine[r["engine"]] = self.by_engine.get(r["engine"], 0) + r.get("jpy", 0)
                except Exception:
                    pass

    def add(self, rec: dict):
        self.total_jpy += rec.get("jpy", 0)
        self.by_engine[rec["engine"]] = self.by_engine.get(rec["engine"], 0) + rec.get("jpy", 0)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- ASR engines
_oai = None


def openai_asr(path: str, prompt: Optional[str] = None, language: str = "en", logprobs: bool = True,
               model: str = "gpt-4o-mini-transcribe") -> dict:
    global _oai
    if _oai is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        _oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    kw = {"model": model, "language": language, "response_format": "json"}
    if prompt:
        kw["prompt"] = prompt
    if logprobs:
        kw["include"] = ["logprobs"]
    t0 = time.time()
    try:
        with open(path, "rb") as f:
            resp = _oai.audio.transcriptions.create(file=f, **kw)
    except Exception as exc:
        return {"engine": "openai", "ok": False, "error": str(exc)[:400], "elapsed": round(time.time() - t0, 3), "jpy": 0.0}
    el = round(time.time() - t0, 3)
    usage = getattr(resp, "usage", None)
    ui = uo = None
    if usage is not None:
        ui = getattr(usage, "input_tokens", None)
        uo = getattr(usage, "output_tokens", None)
    lp = getattr(resp, "logprobs", None)
    lps = None
    if lp:
        lps = [{"token": getattr(x, "token", None), "logprob": getattr(x, "logprob", None)} for x in lp]
    jpy = ((ui or 0) * OPENAI_IN_USD_PER_M + (uo or 0) * OPENAI_OUT_USD_PER_M) / 1e6 * USD_JPY
    return {"engine": "openai", "ok": True, "text": resp.text, "logprobs": lps, "input_tokens": ui, "output_tokens": uo,
            "elapsed": el, "jpy": round(jpy, 5), "prompt_used": bool(prompt)}


def azure_asr(path: str, phrases=None, language: str = "en-US", timeout: float = 90.0) -> dict:
    """Production helper(er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list)と同じ連続認識方式+
    word-level timestamps(Detailed出力)。Production helperはcost logger等の副作用があるため呼ばずに再実装。"""
    from dotenv import load_dotenv
    import azure.cognitiveservices.speech as speechsdk
    load_dotenv()
    cfg = speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_KEY"), region=os.getenv("SPEECH_REGION"))
    cfg.speech_recognition_language = language
    cfg.request_word_level_timestamps()
    cfg.output_format = speechsdk.OutputFormat.Detailed
    rec = speechsdk.SpeechRecognizer(speech_config=cfg, audio_config=speechsdk.audio.AudioConfig(filename=path))
    if phrases:
        pl = speechsdk.PhraseListGrammar.from_recognizer(rec)
        for p in phrases:
            pl.addPhrase(p)
    segs, words, done = [], [], {"f": False}

    def on_rec(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segs.append(evt.result.text)
            try:
                j = json.loads(evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
                nb = (j.get("NBest") or [{}])[0]
                for w in nb.get("Words", []):
                    words.append({"w": (w.get("Word") or "").lower(), "start": w["Offset"] / 1e7,
                                  "end": (w["Offset"] + w["Duration"]) / 1e7, "conf": w.get("Confidence")})
            except Exception:
                pass

    def on_stop(evt):
        done["f"] = True
    rec.recognized.connect(on_rec)
    rec.session_stopped.connect(on_stop)
    rec.canceled.connect(on_stop)
    t0 = time.time()
    rec.start_continuous_recognition()
    while not done["f"] and time.time() - t0 < timeout:
        time.sleep(0.2)
    rec.stop_continuous_recognition()
    el = round(time.time() - t0, 3)
    dur = wav_duration(path)
    jpy = dur / 3600.0 * AZURE_USD_PER_HOUR * USD_JPY
    if not done["f"]:
        return {"engine": "azure", "ok": False, "error": "timeout", "elapsed": el, "audio_seconds": dur, "jpy": round(jpy, 5)}
    return {"engine": "azure", "ok": True, "text": " ".join(s.strip() for s in segs), "text_joined_raw": "".join(segs),
            "words": words, "phrases": list(phrases or []), "elapsed": el, "audio_seconds": round(dur, 3),
            "jpy": round(jpy, 5)}


_wh = {}


def whisper_asr(path: str, model: str = "small", initial_prompt: Optional[str] = None) -> dict:
    from faster_whisper import WhisperModel
    if model not in _wh:
        _wh[model] = WhisperModel(model, device="cpu", compute_type="int8")
    t0 = time.time()
    segs, info = _wh[model].transcribe(path, language="en", word_timestamps=True, beam_size=5, temperature=0.0,
                                       condition_on_previous_text=False, initial_prompt=initial_prompt)
    words, texts = [], []
    for s in segs:
        texts.append(s.text.strip())
        for w in (s.words or []):
            words.append({"w": w.word.strip().lower(), "start": w.start, "end": w.end, "conf": round(w.probability, 4)})
    return {"engine": f"whisper-{model}", "ok": True, "text": " ".join(texts), "words": words,
            "elapsed": round(time.time() - t0, 3), "jpy": 0.0}
