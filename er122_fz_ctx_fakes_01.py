# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: offline test用 fake backend(Production code ではない)。

`er012_b.generate_voice_body_wide_margin` / `er003_n3.generate_with_a2_slowdown_outer_loop` を、TTS/ASR/判定chainの
scriptされた偽物で駆動し、送信prompt列・attempt_ctx・attempts_log・戻り値を記録する。外部接続・有料API 0(全て差替え)。
同じfakeを (a) hook=None のgolden凍結(変更前コードで生成) (b) 新コードのparity test (c) hook有のpolicy test で共用する。
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import tempfile
from unittest import mock

import numpy as np

SCENARIOS = {
    # tts: TTS呼出ごとの成否(minimal fallback内の呼出も1呼出として数える)。eval: evaluate_attempt_with_cascade呼出ごとの (verified_content, stop_retrying, classification)
    "S1_success": {"max_attempts": 3, "tts": [True], "eval": [(True, False, "EXACT_MATCH")]},
    "S2_ng_then_ok": {"max_attempts": 3, "tts": [True, True], "eval": [(False, False, "TRUE_CONTENT_MISMATCH"), (True, False, "EXACT_MATCH")]},
    "S3_ng_ng_ok": {"max_attempts": 3, "tts": [True, True, True],
                    "eval": [(False, False, "TRUE_CONTENT_MISMATCH"), (False, False, "TRUE_CONTENT_MISMATCH"), (True, False, "EXACT_MATCH")]},
    "S4_all_ng": {"max_attempts": 3, "tts": [True, True, True],
                  "eval": [(False, False, "TRUE_CONTENT_MISMATCH")] * 3},
    "S5_technical_failure_minimal_ok": {"max_attempts": 3, "tts": [False, True], "eval": [(True, False, "EXACT_MATCH")]},
    "S6_technical_failure_minimal_fail": {"max_attempts": 3, "tts": [False, False, True], "eval": [(True, False, "EXACT_MATCH")]},
    "S7_stop_retrying": {"max_attempts": 3, "tts": [True, True], "eval": [(False, False, "TRUE_CONTENT_MISMATCH"), (False, True, "TRUE_CONTENT_MISMATCH")]},
    "S8_max_attempts_2_all_ng": {"max_attempts": 2, "tts": [True, True], "eval": [(False, False, "X"), (False, False, "X")]},
}
TEXT = "The quick brown fox jumps over the lazy dog."


class _Cls:
    def __init__(self, name):
        self.classification = name
        self.connected_speech_info = None


class World:
    """scriptされた偽backend。events に送信prompt/attempt_ctxを記録する。"""

    def __init__(self, tts_script, eval_script, tmp_root=None):
        self.tts_script = list(tts_script)
        self.eval_script = list(eval_script)
        self.tts_i = 0
        self.eval_i = 0
        self.prompts = []
        self.attempt_ctxs = []
        self.events = []          # 順序つき ("tts"|"eval"|"minimal_fallback", ...)
        self.tmp_root = tmp_root or tempfile.mkdtemp(prefix="fzcw_")
        self.out_path = os.path.join(self.tmp_root, "theme", "b1b", "narration", "full_story_part1_c3.wav").replace("\\", "/")
        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        self.history_path = os.path.join(self.tmp_root, "attempt_history.jsonl")
        self.hr_queue = []
        self.before_tts = None    # callable(world)->None : TTS呼出の直前に走る(crash注入用)
        self.asr_text = TEXT      # fake ASRの転写(stage testは短いclip用に短い文字列を指定)

    # ---- fake primitives ----
    def call_tts(self, call_fn, prompt, max_retry=0, sleep_fn=None):
        if self.before_tts is not None:
            self.before_tts(self)
        ok = self.tts_script[self.tts_i] if self.tts_i < len(self.tts_script) else True
        self.tts_i += 1
        self.prompts.append(prompt)
        self.events.append(("tts", ok))
        if not ok:
            return (None, 0, False, "tts down")
        return (np.zeros(4000, dtype=np.int16).tobytes(), 0, True, None)

    def evaluate(self, text, asr_text, classification_history, out_path, **kw):
        spec = self.eval_script[self.eval_i] if self.eval_i < len(self.eval_script) else (False, False, "X")
        self.eval_i += 1
        ctx = dict(kw.get("attempt_ctx") or {})
        self.attempt_ctxs.append(ctx)
        self.events.append(("eval", ctx.get("slot"), ctx.get("is_last_slot")))
        d = kw.get("detail_out")
        if isinstance(d, dict):
            d["asr_judgement"] = {"state": "PASS" if spec[0] else "NG", "fake": True}
            d["verified"] = spec[0]
        if ctx.get("is_last_slot") and not spec[0]:
            self.hr_queue.append({"slot": ctx.get("slot"), "text": text})   # ASR判定の最終slot NG->HR queue行(fake)
        return spec[0], spec[1], _Cls(spec[2])

    @contextlib.contextmanager
    def patched(self):
        import er002_common as common
        import er003_b1_p3u_audio as p3u
        import er003_audio_tts_asr_safety as safety
        import er006_asr_provider_routing_01 as asr_routing
        import er006_batch_tts_wiring_01 as bw
        import er006_secondary_asr_01 as secondary_asr
        import er008_disfluency_qa_18 as dq18
        import er011_human_review_lock_01 as review_lock
        import er011_open121_repetition_qa_production_01 as rq
        import er006_pronunciation_ledger_01 as pronun
        import er109_xz_scope_01 as xz_scope

        def trim(samples, sr, safety_margin_seconds=None):
            return (np.zeros(sr, dtype=np.float32), {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0})

        def transcribe(path, language="en-US"):
            return (self.asr_text, None)

        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(common, "_call_tts_with_retry", self.call_tts))
            st.enter_context(mock.patch.object(p3u, "trim_english_keyword_silence", trim))
            st.enter_context(mock.patch.object(safety, "detect_duration_anomaly", lambda *a, **k: {"is_anomaly": False}))
            st.enter_context(mock.patch.object(bw, "make_batch_tts_call_fn", lambda *a, **k: (lambda *x, **y: None)))
            st.enter_context(mock.patch.object(asr_routing, "transcribe", transcribe))
            st.enter_context(mock.patch.object(secondary_asr, "evaluate_attempt_with_cascade", self.evaluate))
            st.enter_context(mock.patch.object(dq18, "apply_disfluency_gate",
                                               lambda v, p, language="en", enabled=False: {"verified": v, "disfluency_checked": False, "disfluency_evidence": None}))
            st.enter_context(mock.patch.object(rq, "apply_repetition_qa_gate",
                                               lambda v, *a, **k: {"verified": v, "repetition_qa_checked": True, "repetition_qa_evidence": {"fake": True}}))
            st.enter_context(mock.patch.object(pronun, "get_hint_for_text", lambda *a, **k: []))
            st.enter_context(mock.patch.object(xz_scope, "is_active_for_run", lambda: False))
            st.enter_context(mock.patch.object(review_lock, "ATTEMPT_HISTORY_PATH", self.history_path))
            yield self

    def cleanup(self):
        shutil.rmtree(self.tmp_root, ignore_errors=True)


def normalize(obj, tmp_root):
    """tmp pathを除いたJSON互換へ(golden比較用)。"""
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return json.loads(s.replace(tmp_root.replace("\\", "/"), "<TMP>").replace(tmp_root.replace("\\", "\\\\"), "<TMP>"))


def run_single(name, **gen_kw):
    """generate_voice_body_wide_margin を1シナリオ駆動して記録を返す(gen_kw=hook等の追加引数。hook=Noneのgolden生成では空)。"""
    import er012_b_family_voices_production_01 as bv
    sc = SCENARIOS[name]
    w = World(sc["tts"], sc["eval"])
    try:
        with w.patched():
            r = bv.generate_voice_body_wide_margin(TEXT, w.out_path, "Puck", max_attempts=sc["max_attempts"], **gen_kw)
        rec = {"scenario": name, "prompts": w.prompts, "attempt_ctxs": w.attempt_ctxs, "events": w.events,
               "result": r, "tts_calls": w.tts_i, "eval_calls": w.eval_i}
        return normalize(rec, w.tmp_root)
    finally:
        w.cleanup()


def run_outer(name, gen_sequence, post_results, **kw):
    """generate_with_a2_slowdown_outer_loop を駆動。gen_sequence=gen_fnの各呼出が返す(status, n_attempt_rows)、
    post_results=apply_a2_slowdown_postprocess の各呼出が返すstatus。max_attemptsと呼出順を記録する。"""
    import er003_v1_n3_01_tts_generate as n3
    import er011_human_review_lock_01 as review_lock
    tmp = tempfile.mkdtemp(prefix="fzcw_outer_")
    out = os.path.join(tmp, "theme", "b1b", "narration", "full_story_part1_c3.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    calls = {"gen": [], "post": []}
    gi = {"i": 0}
    pi = {"i": 0}

    def gen_fn(max_attempts):
        status, nrows = gen_sequence[gi["i"]]
        gi["i"] += 1
        calls["gen"].append(max_attempts)
        return {"status": status, "attempts_log": [{"attempt": k + 1} for k in range(nrows)], "reason": "fake"}

    def post(name_, narration_dir, tts_input, result, is_last_slot=False, log_human_review=True, **k):
        st = post_results[pi["i"]]
        pi["i"] += 1
        calls["post"].append({"is_last_slot": is_last_slot})
        r = dict(result)
        r["status"] = st
        if st != "OK":
            r["reason"] = "fake post-slowdown NG"
        return r

    try:
        with mock.patch.object(n3, "apply_a2_slowdown_postprocess", post), \
                mock.patch.object(review_lock, "ATTEMPT_HISTORY_PATH", os.path.join(tmp, "h.jsonl")):
            r = n3.generate_with_a2_slowdown_outer_loop("full_story_part1_c3", TEXT, out, gen_fn, **kw)
        return normalize({"scenario": name, "calls": calls, "result": r}, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


OUTER_SCENARIOS = {
    "O1_first_pass_ok": ([("OK", 1)], ["OK"]),
    "O2_post_ng_then_ok": ([("OK", 1), ("OK", 1)], ["STOPPED", "OK"]),
    "O3_post_ng_thrice": ([("OK", 1), ("OK", 1), ("OK", 1)], ["STOPPED", "STOPPED", "STOPPED"]),
    "O4_inner_exhausted": ([("STOPPED", 3)], []),
    "O5_two_rows_one_iteration": ([("OK", 2), ("OK", 1)], ["STOPPED", "STOPPED"]),
    "O6_post_ng_ok_ng": ([("OK", 1), ("OK", 1)], ["STOPPED", "OK"]),
}


def build_golden():
    """変更前コード(hook=None)で全シナリオを記録した辞書を返す。"""
    g = {"single": {n: run_single(n) for n in SCENARIOS}, "outer": {}}
    for n, (seq, post) in OUTER_SCENARIOS.items():
        g["outer"][n] = run_outer(n, seq, post)
    return g


if __name__ == "__main__":
    import argparse
    import hashlib
    import subprocess
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", required=True, help="golden JSON出力path")
    a = ap.parse_args()
    g = build_golden()
    with open(a.freeze, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
    files = ["er012_b_family_voices_production_01.py", "er003_v1_n3_01_tts_generate.py", "er063_family_z_audio_01.py", "er011_human_review_lock_01.py"]
    man = {"frozen_at_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "baseline_commit_named_in_delegation": "ab111631c",
           "source_sha256": {f: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files},
           "golden_sha256": hashlib.sha256(open(a.freeze, "rb").read()).hexdigest()}
    with open(os.path.join(os.path.dirname(a.freeze), "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    print(json.dumps(man, indent=1))
