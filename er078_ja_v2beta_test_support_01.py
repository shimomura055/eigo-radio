# -*- coding: utf-8 -*-
"""JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: test共通helper(API 0。Production codeではない)。

- `judge()`: Production adapter `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail` を、Azure(Secondary)だけ注入関数で差し替えて実行する。
  Reading Resolver(LLM)は無効化、socket接続は例外にする(API 0の機械的担保)。scope=None/"X"/"Y"/"Z"で`er109_xz_scope_01.run_scope`の内外を切替える。
- `make_wav()`: sha256が一意な短いwav(判定のprovenance[sha]用。TTS/ASRは呼ばない)。
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import socket
import tempfile
import wave

import test_state_isolation_01  # noqa: F401  Production監査ログ/HR queueへの書込みをtmpへ退避

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er109_xz_scope_01 as xz

_TMP = tempfile.mkdtemp(prefix="ja_v2beta_test_")
_REAL_CONNECT = socket.socket.connect


def _no_net(self, *a, **k):
    raise RuntimeError("API0 violation: network connect attempted")


@contextlib.contextmanager
def api0():
    """Reading Resolver(LLM)無効 + socket接続禁止。"""
    old_flag = javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED
    javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
    socket.socket.connect = _no_net
    try:
        yield
    finally:
        socket.socket.connect = _REAL_CONNECT
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = old_flag


def make_wav(tag: str, seconds: float = 3.0) -> str:
    """tagごとに異なる内容(=異なるsha256)の無音風wav。"""
    h = int(hashlib.sha256(tag.encode("utf-8")).hexdigest()[:4], 16) % 200
    p = os.path.join(_TMP, hashlib.sha256(tag.encode("utf-8")).hexdigest()[:16] + ".wav")
    if not os.path.exists(p):
        w = wave.open(p, "wb")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes((b"\x01\x00" * h) + b"\x00\x00" * int(16000 * seconds))
        w.close()
    return p


class Az:
    """Azure(Secondary)注入。texts=list[(text|None, err|None)]を順に返す。callsで呼出回数を数える。"""

    def __init__(self, text=None, err=None):
        self.text, self.err, self.calls = text, err, 0

    def __call__(self, path, language="ja-JP", timeout_seconds=90):
        self.calls += 1
        return (self.text, self.err)


def judge(canon, primary, azure=None, *, scope="X", wav=None, attempt_ctx=None, length_ok=True, expected_readings=None, cascade=True):
    """1 attempt分の判定を実行して(result dict, Azure注入object)を返す。azure=None -> Secondary呼出は『障害』(err)。"""
    az = azure if isinstance(azure, Az) else (Az(azure) if azure is not None else Az(None, "api0_stub_no_secondary"))
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = az
    wav = wav or make_wav(f"{canon}|{primary}|{azure if not isinstance(azure, Az) else azure.text}")
    try:
        with api0():
            ctxm = xz.run_scope(scope) if scope else contextlib.nullcontext()
            with ctxm:
                r = sec.evaluate_attempt_ja_with_cascade_detail(
                    canon, primary, wav, cascade_enabled=cascade, expected_readings=expected_readings, length_ok=length_ok,
                    attempt_ctx=({"max_len": 400} if attempt_ctx is None else attempt_ctx))
    finally:
        sec._azure_stt_strict = orig
    return r, az


def aj(r):
    return r["asr_judgement"]


def cat(r):
    """proto_unified_03.judge と同じ4区分(PASS / PASS_W_PROD / PASS_W_NEW / NG)。"""
    j = aj(r)
    if j["state"] not in uj.PASSING_STATES:
        return "NG"
    if j["state"] == uj.PASS:
        return "PASS"
    return "PASS_W_NEW" if j.get("rescue_basis") else "PASS_W_PROD"
