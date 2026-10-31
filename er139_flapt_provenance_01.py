# ============================================================
# er139_flapt_provenance_01.py
# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02: Flap-T救済のためのTTS出自台帳(sha256(wav) -> {voice, model_id, path, source, transforms})。
# 出自 = API境界で『実際に送信した値』(Z voice_override・Batch/Standard・flash-lite/2.5-pro)。leafが『思う』Voiceではない。
# 構造(Opus条件A + Fable確定):
#   記録点(いずれも成功直後。cost logger未install・Standardでも落ちない):
#     (1) Batch   : er006_batch_tts_wiring_01._record() SUCCESS分岐(cost logger判定より前)。er006:make_batch_tts_call_fn と
#                   er033:make_speech_metadata_batch_call_fn の両方がここを通る。
#     (2) Standard: call_fn factory成功直後(er002_gemini_client.make_tts_call_fn / er003_b1_p7a_audio.make_tts_call_fn_for_model /
#                   er033_tts_flash_lite_backend_wiring_01.make_speech_metadata_call_fn)。
#   束縛 : er002_common.write_wav_float 末尾(mono 24kHz 書込みのみ・単一用途・失効120秒・thread-local単一slot・後着上書き)。
#   子登録: er008_a2_postprocess_slowdown_01.apply_a2_slowdown 内の1点(減速/高速化後wavへ親の出自+transform)。
#   判定 : er006_secondary_asr_01.evaluate_attempt_with_cascade_detail をdecoratorで包み judging_wav(sha) を張る(EN・X/Y/Z scope内のみ)。
#   hydrate: 保存音声の再judge(er019 rejudge_with_current_judge / er109_hr_lock_rejudge)は記録(sha/voice/model/tts_provenance)から復元。
#            出自のない保存音声は fail-closed(適用外)。
# 共有moduleの記録点は先頭で `_active()`(= er109 is_active_for_run ∧ Flap-T flag)を見て即return(Family A/B/C・scope外は完全no-op)。
# ============================================================
from __future__ import annotations

import contextlib
import contextvars
import datetime as _dt
import functools
import hashlib
import inspect
import json
import os
import threading
import time
from collections import OrderedDict
from typing import Optional

PENDING_TTL_SECONDS = 120.0
LEDGER_MAX = 4096
COVERAGE_FILENAME = "flapt_provenance_coverage.jsonl"
SAMPLE_RATE_BOUND = 24000

_LOCK = threading.Lock()
_LEDGER: "OrderedDict[str, dict]" = OrderedDict()
_TLS = threading.local()
_CTX: "contextvars.ContextVar[Optional[dict]]" = contextvars.ContextVar("flapt_judging_ctx", default=None)
_COVERAGE_DIR: Optional[str] = None


def _active() -> bool:
    """記録点・判定の入口で毎回確認(1-f)。X/Y/Z run scope内 ∧ 親flag ∧ Flap-T flag。それ以外は完全no-op。"""
    try:
        import er109_xz_scope_01 as xz
        import er139_flapt_equivalence_01 as fe
        return bool(xz.is_active_for_run() and fe.is_enabled())
    except Exception:  # noqa: BLE001
        return False


def file_sha256(path) -> Optional[str]:
    try:
        if path and os.path.isfile(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()
    except OSError:
        pass
    return None


def reset_for_tests() -> None:
    with _LOCK:
        _LEDGER.clear()
    _TLS.pending = None


# ---------------------------------------------------------------- 記録点(SDK境界)
def note_tts_sent(voice, model_id, source: str = "sdk_boundary") -> None:
    """TTS成功直後に『実送信voice/model』をpending(thread-local単一slot・後着上書き)へ。scope外/flag OFFでは何もしない。"""
    try:
        if not voice or not model_id or not _active():
            return
        _TLS.pending = {"voice": str(voice), "model_id": str(model_id), "source": str(source), "t": time.monotonic()}
    except Exception:  # noqa: BLE001  TTS生成を絶対に壊さない
        pass


def _register(sha: str, entry: dict) -> None:
    with _LOCK:
        _LEDGER[sha] = entry
        _LEDGER.move_to_end(sha)
        while len(_LEDGER) > LEDGER_MAX:
            _LEDGER.popitem(last=False)


def bind_pending(path, framerate, channels) -> Optional[str]:
    """write_wav_float末尾から呼ぶ。mono 24kHz書込みのみ束縛(組立wav channels=2は自然除外・pendingも消費しない)。"""
    try:
        p = getattr(_TLS, "pending", None)
        if p is None or int(channels) != 1 or int(framerate) != SAMPLE_RATE_BOUND or not _active():
            return None
        _TLS.pending = None                                  # 単一用途
        if time.monotonic() - p["t"] > PENDING_TTL_SECONDS:
            return None
        sha = file_sha256(path)
        if not sha:
            return None
        _register(sha, {"voice": p["voice"], "model_id": p["model_id"], "source": p["source"], "transforms": [], "transforms_known": True,
                        "bound_at": _dt.datetime.now().isoformat(timespec="seconds")})
        return sha
    except Exception:  # noqa: BLE001
        return None


def register_child(parent_path, child_path, transform: dict) -> Optional[str]:
    """減速/高速化後wavへ親の出自+transformを引き継ぐ(apply_a2_slowdown内の1点)。親の出自が無ければ何もしない。"""
    try:
        if not _active():
            return None
        psha = file_sha256(parent_path)
        ent = resolve(psha) if psha else None
        if ent is None:
            return None
        csha = file_sha256(child_path)
        if not csha:
            return None
        child = dict(ent)
        child["transforms"] = list(ent.get("transforms") or []) + [dict(transform)]
        child["parent_sha256"] = psha
        _register(csha, child)
        return csha
    except Exception:  # noqa: BLE001
        return None


def resolve(sha) -> Optional[dict]:
    if not sha:
        return None
    with _LOCK:
        e = _LEDGER.get(sha)
        return dict(e) if e is not None else None


def hydrate(sha, voice, model_id, *, source: str, transforms=None, transforms_known: bool = False, wav_path=None) -> bool:
    """保存記録から出自を復元(sha一致検証つき: wav_pathが存在するなら実ファイルのshaと一致必須)。"""
    try:
        if not sha or not voice or not model_id or not _active():
            return False
        if wav_path and os.path.isfile(wav_path) and file_sha256(wav_path) != sha:
            return False
        _register(sha, {"voice": str(voice), "model_id": str(model_id), "source": source, "transforms": list(transforms or []),
                        "transforms_known": bool(transforms_known)})
        return True
    except Exception:  # noqa: BLE001
        return False


def record_sha_and_provenance(rec, speedup_possible: bool = True) -> tuple:
    """保存record(attempt JSON / Store entry / asr_judgement)から (sha, voice, model_id, source, transforms, transforms_known) を取り出す。無ければsha以外None。"""
    if not isinstance(rec, dict):
        return None, None, None, None, None, False
    aj = rec.get("asr_judgement") if isinstance(rec.get("asr_judgement"), dict) else {}
    aji = rec.get("asr_judgement_inherited") if isinstance(rec.get("asr_judgement_inherited"), dict) else {}
    sha = rec.get("sha256") or rec.get("audio_sha256") or aj.get("audio_sha256") or aji.get("audio_sha256")
    tp = aj.get("tts_provenance") or aji.get("tts_provenance") or rec.get("tts_provenance")
    if isinstance(tp, dict) and tp.get("voice") and tp.get("model_id"):
        # 新規生成音声: attempt audit に保存した出自(transformsも記録済み=既知)。judge時のshaと一致する場合のみ
        a_sha = aj.get("audio_sha256") or aji.get("audio_sha256") or sha
        return a_sha, tp["voice"], tp["model_id"], "attempt_audit", list(tp.get("transforms") or []), bool(tp.get("transforms_known", True))
    if rec.get("voice") and rec.get("model"):
        # 変換履歴は保存されていない。速度後処理が高速化(Z Adv会話の1.06x)を含みうる文脈なら最も厳しい速度条件(fast106_confirmed)を要求。
        # 高速化があり得ない文脈(Std[a2]本文=減速なし/6%減速のみ、KP英語音声)は、減速なし/6.0=確認済み扱いで transforms_known=True。
        return sha, rec["voice"], rec["model"], "store_entry", [], (not speedup_possible)
    return sha, None, None, None, None, False


@contextlib.contextmanager
def rejudge_context(rec, tag=None, speedup_possible: bool = True):
    """保存音声の再judge用: 記録から出自をhydrateし judging_wav(sha) で包む。出自が無い/scope外ならそのまま(適用外=fail-closed)。"""
    if not _active():
        yield None
        return
    sha, voice, model_id, source, transforms, known = record_sha_and_provenance(rec, speedup_possible)
    if sha and voice and model_id:
        hydrate(sha, voice, model_id, source=source, transforms=transforms, transforms_known=known,
                wav_path=(rec.get("path") or rec.get("wav_path") if isinstance(rec, dict) else None))
    with judging_wav(sha, phase="rejudge", tag=tag) as ctx:
        yield ctx


def audit_provenance(sha) -> Optional[dict]:
    """attempt audit(asr_judgement)へ保存する出自: {voice, model_id, path, source, transforms, transforms_known}。scope外/未解決はNone(キー自体を付けない)。"""
    try:
        if not _active():
            return None
        e = resolve(sha)
        if e is None:
            return None
        import er139_flapt_equivalence_01 as fe
        row = fe.table_row(e.get("voice"), e.get("model_id"))
        return {"voice": e.get("voice"), "model_id": e.get("model_id"), "path": (row or {}).get("path"), "source": e.get("source"),
                "transforms": list(e.get("transforms") or []), "transforms_known": bool(e.get("transforms_known", True))}
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------- 判定context(sha束縛 + memo + sidecar)
def current_ctx() -> Optional[dict]:
    return _CTX.get()


def set_coverage_dir(path: Optional[str]) -> None:
    global _COVERAGE_DIR
    _COVERAGE_DIR = path


def coverage_path() -> str:
    d = _COVERAGE_DIR
    if d is None:
        try:
            import er005_cost_logger as cl
            lp = getattr(cl, "_LOG_PATH", None)
            if lp:
                d = os.path.dirname(os.path.abspath(lp))
        except Exception:  # noqa: BLE001
            d = None
    if d is None:
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er139_output")
    return os.path.join(d, COVERAGE_FILENAME)


def _write_coverage(ctx: dict) -> None:
    try:
        import er109_xz_scope_01 as xz
        import er139_flapt_equivalence_01 as fe
        sha = ctx["sha"]
        e = resolve(sha)
        rec = {"ts": _dt.datetime.now().isoformat(timespec="seconds"), "scope": xz.current_scope(), "phase": ctx.get("phase"),
               "tag": ctx.get("tag"), "wav_sha256": sha,
               "provenance_resolved": e is not None,
               "voice": (e or {}).get("voice"), "model_id": (e or {}).get("model_id"), "source": (e or {}).get("source"),
               "transforms": (e or {}).get("transforms"), "transforms_known": (e or {}).get("transforms_known"),
               "table_status": (fe.table_status(e.get("voice"), e.get("model_id")) if e else None),
               "flap_candidates": ctx["cands"], "run_warnings": list(fe.RUN_WARNINGS)}
        p = coverage_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001  telemetry失敗で判定を止めない
        pass


@contextlib.contextmanager
def judging_wav(sha, *, phase="generation", tag=None):
    """EN判定の間だけ『判定対象wavのsha』をcontextvarへ。範囲内で (canonical,text) ごとのflap判定をmemo(I-10)。入れ子は外側を維持。
    scope外/flag OFF/shaなしでは何も張らない(decide() は provenance_missing として fail-closed)。"""
    cur = _CTX.get()
    if cur is not None and cur.get("sha") == sha:
        yield cur
        return
    if not sha or not _active():
        yield None
        return
    ctx = {"sha": sha, "memo": {}, "cands": [], "phase": phase, "tag": tag}
    token = _CTX.set(ctx)
    try:
        yield ctx
    finally:
        _CTX.reset(token)
        _write_coverage(ctx)


def adapter_context(fn):
    """evaluate_attempt_with_cascade_detail 用decorator。EN・X/Y/Z scope内のときだけ wav_path の sha で judging_wav を張る。
    それ以外(A/B/C・JA・scope外)は fn をそのまま呼ぶ=完全に従来どおり。"""
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*a, **kw):
        if not _active():
            return fn(*a, **kw)
        try:
            b = sig.bind_partial(*a, **kw)
            wav = b.arguments.get("wav_path")
            lang = str(b.arguments.get("language", "en-US"))
            seg = b.arguments.get("segment_id")
        except TypeError:
            return fn(*a, **kw)
        if lang.lower().startswith("ja") or not wav:
            return fn(*a, **kw)
        with judging_wav(file_sha256(wav), phase="generation", tag=seg):
            return fn(*a, **kw)
    wrapper.__flapt_adapter_context__ = True
    return wrapper


def rejudge_entry_context(is_ja, speedup_possible=lambda entry, *a, **kw: True):
    """保存entryの再judge関数(第1引数=entry dict, 以降 level, label, force_lang)用decorator factory。X/Y/Z scope内で、EN(is_ja(...)がFalse)のときだけ、
    entryの記録(sha/voice/model/tts_provenance)から出自をhydrateして judging_wav(sha) を張る。出自が無い保存音声は fail-closed(従来どおり適用外)。
    scope外・JAは fn をそのまま呼ぶ。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(entry, *a, **kw):
            if not _active():
                return fn(entry, *a, **kw)
            try:
                ja = bool(is_ja(entry, *a, **kw))
            except Exception:  # noqa: BLE001
                ja = False
            if ja:
                return fn(entry, *a, **kw)
            tag = kw.get("label") if "label" in kw else (a[1] if len(a) > 1 else None)
            try:
                sp = bool(speedup_possible(entry, *a, **kw))
            except Exception:  # noqa: BLE001
                sp = True
            with rejudge_context(entry, tag=tag, speedup_possible=sp):
                return fn(entry, *a, **kw)
        wrapper.__flapt_rejudge_context__ = True
        return wrapper
    return deco
