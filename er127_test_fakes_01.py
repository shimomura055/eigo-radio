# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: offline test用 fake backend(Production codeではない)。外部接続・有料API 0。

全leaf(voice01 / news_tail_fix / crosslevel / n3_tts / repro01 / er012_b)が共通で通る低レベルprimitive
(TTS呼出・trim・ASR転写・統一judge・disfluency/repetition gate・発音resolver・LLM(LR)・減速)を差し替え、scriptされた結果で駆動する。
`World.events` に TTS(prompt先頭・成否)/judge(slot・is_last_slot・force_secondary・text)/sleep(秒)/LR呼出 の順序つき記録を残す。
同じfakeを (a) 変更前コードでのgolden凍結(scope外) (b) scope内の新flow検証 で共用する(`tools: build_golden()`)。
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import tempfile
from unittest import mock

import numpy as np

TEXT = "The quick brown fox jumps over the lazy dog."
JA_TEXT = "これはテストです。"


class _Cls:
    def __init__(self, name):
        self.classification = name
        self.connected_speech_info = None
        self.semantic_equivalence_info = None
        self.reading_resolver_info = None
        self.scg_info = None
        self.protected = None


class FakeClock:
    """cooldown_coreのclock/sleep注入(実sleep 0)。sleepはt進行。"""

    def __init__(self, t0=1_000_000.0):
        self.t = t0
        self.sleeps = []

    def clock(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(float(s))
        self.t += float(s)


def judge(ok=True, stop=False, cls="EXACT_MATCH", state=None, asr_text=None):
    return {"ok": ok, "stop": stop, "cls": cls, "state": state or ("PASS" if ok else "NG_BOTH"), "asr_text": asr_text}


PASS = judge(True)
NG = judge(False, cls="TRUE_CONTENT_MISMATCH")
NG_STOP = judge(False, stop=True, cls="TRUE_CONTENT_MISMATCH")


class World:
    """scriptされた偽backend。tts/judgeは呼出順の配列。配列が尽きたら tts=True / judge=NG(=安全側)。"""

    def __init__(self, *, tts=(), judge=(), ja_judge=(), post_judge=(), asr_text=TEXT, seg="full_story_part1", level="b1b", theme="theme",
                 tmp_root=None, lr_candidate="The quick brown fox jumps over the lazy dog today.", lr_llm_fail=False, ng_span_found=True):
        self.tts_script = list(tts)
        self.judge_script = list(judge)
        self.ja_judge_script = list(ja_judge)
        self.post_script = list(post_judge)
        self.tts_i = self.judge_i = self.ja_i = self.post_i = 0
        self.asr_text = asr_text
        self.tmp_root = tmp_root or tempfile.mkdtemp(prefix="er127_")
        self.theme, self.level, self.seg = theme, level, seg
        self.out_path = self.path_for(seg)
        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        self.history_path = os.path.join(self.tmp_root, "attempt_history.jsonl")
        self.hr_path = os.path.join(self.tmp_root, "hr_queue.jsonl")
        self.hr_path_ja = os.path.join(self.tmp_root, "hr_queue_ja.jsonl")     # TRU-06: JA queue (er007 HUMAN_REVIEW_LOG_PATH_JA) is a separate file from EN
        self.events = []
        self.prompts = []
        self.judge_calls = []
        self.lr_calls = []
        self.clock = FakeClock()
        self.lr_candidate = lr_candidate
        self.lr_llm_fail = lr_llm_fail
        self.ng_span_found = ng_span_found
        self.before_tts = None          # callable(world): TTS直前(kill/STOP注入用)
        self.stop_after_sleeps = None   # N回sleepしたらSTOP例外(待機中STOP)
        self.slowdown_calls = []
        self.voices = []                # TTS呼出ごとの(voice名, model名)  ※resolve_tts_call_and_promptの引数を記録
        self.suppress_ja_hr = False     # True: JA judgeが最終slotでもHRQ行を書かない(disfluency単独NG・driver判定注入の再現。委任_04)
        self.dq_ng = False              # Trueならdisfluency/repetition gateが常にNG化(ASR一致でも不合格=U-03の再現)

    def path_for(self, seg):
        return os.path.join(self.tmp_root, self.theme, self.level, "narration", f"{seg}.wav").replace("\\", "/")

    # ---- primitives
    def call_tts(self, call_fn, prompt, max_retry=0, sleep_fn=None):
        if self.before_tts is not None:
            self.before_tts(self)
        ok = self.tts_script[self.tts_i] if self.tts_i < len(self.tts_script) else True
        self.tts_i += 1
        self.prompts.append(prompt)
        self.events.append(("tts", ok, prompt[:60]))
        if not ok:
            return (None, 0, False, "tts down")
        return (np.zeros(4000, dtype=np.int16).tobytes(), 0, True, None)

    def _next_judge(self, ja=False):
        if ja:
            spec = self.ja_judge_script[self.ja_i] if self.ja_i < len(self.ja_judge_script) else NG
            self.ja_i += 1
        else:
            spec = self.judge_script[self.judge_i] if self.judge_i < len(self.judge_script) else NG
            self.judge_i += 1
        return spec

    def evaluate(self, text, asr_text, classification_history, out_path, **kw):
        spec = self._next_judge()
        ctx = dict(kw.get("attempt_ctx") or {})
        self.judge_calls.append({"text": text, "asr_text": asr_text, "force_secondary": bool(kw.get("force_secondary")),
                                 "ctx": ctx, "segment_id": kw.get("segment_id"), "cs": kw.get("enable_connected_speech_equivalence_layer"),
                                 "vote": ctx.get("vote_required", False), "path": out_path})
        self.events.append(("judge", ctx.get("slot"), ctx.get("is_last_slot"), bool(kw.get("force_secondary")), ctx.get("script_version")))
        d = kw.get("detail_out")
        if isinstance(d, dict):
            d["asr_judgement"] = {"state": spec["state"], "fake": True}
            d["verified"] = spec["ok"]
            d["steps"] = [{"classification": spec["cls"], "asr_text": asr_text}]
        if ctx.get("is_last_slot") and not spec["ok"] and spec["state"] not in ("NG_SECONDARY_UNAVAILABLE", "NG_WHISPER_UNAVAILABLE"):
            self._write_hr(out_path, text, spec)
        return spec["ok"], spec["stop"], _Cls(spec["cls"])

    def evaluate_ja(self, text, asr_text, out_path, **kw):
        spec = self._next_judge(ja=True)
        ctx = dict(kw.get("attempt_ctx") or {})
        self.judge_calls.append({"text": text, "asr_text": asr_text, "force_secondary": False, "ctx": ctx, "ja": True, "path": out_path})
        self.events.append(("judge_ja", ctx.get("slot"), ctx.get("is_last_slot")))
        d = kw.get("detail_out")
        if isinstance(d, dict):
            d["asr_judgement"] = {"state": spec["state"], "fake": True}
        if ctx.get("is_last_slot") and not spec["ok"] and not self.suppress_ja_hr and spec["state"] not in ("NG_SECONDARY_UNAVAILABLE", "NG_WHISPER_UNAVAILABLE"):
            self._write_hr(out_path, text, spec, path=self.hr_path_ja)
        return spec["ok"], spec["stop"], _Cls(spec["cls"])

    def evaluate_detail(self, text, asr_text, prior, wav, **kw):
        """減速後の統一judge(post): scripted。"""
        spec = self.post_script[self.post_i] if self.post_i < len(self.post_script) else PASS
        self.post_i += 1
        ctx = dict(kw.get("attempt_ctx") or {})
        self.events.append(("post_judge", ctx.get("slot"), ctx.get("is_last_slot"), text[:30], ctx.get("m1_anchor_text") and ctx["m1_anchor_text"][:30]))
        self.judge_calls.append({"post": True, "text": text, "ctx": ctx})
        return {"verified": spec["ok"], "stop_retrying": spec["stop"], "classification": None, "final_status": spec["cls"],
                "steps": [{"classification": spec["cls"], "asr_text": asr_text}], "cascade_invoked": False,
                "human_review_required": (not spec["ok"]) and bool(ctx.get("is_last_slot")),
                "asr_judgement": {"state": spec["state"], "fake": True, "adapter": {"layers": []}},
                "canonical_text": text, "wav_path": wav, "cost_guard_triggered": False}

    def _write_hr(self, out_path, text, spec, path=None):
        with open(path or self.hr_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"canonical_text": text, "wav_path": out_path, "final_status": spec["cls"]}, ensure_ascii=False) + "\n")

    def hr_rows(self):
        if not os.path.exists(self.hr_path):
            return []
        return [json.loads(x) for x in open(self.hr_path, encoding="utf-8") if x.strip()]

    def hr_rows_ja(self):
        if not os.path.exists(self.hr_path_ja):
            return []
        return [json.loads(x) for x in open(self.hr_path_ja, encoding="utf-8") if x.strip()]

    # ---- LR fakes
    def lr_run(self, **kw):
        """er020.run_local_rewrite_recovery の差替え: identify_ng_span相当→(LLM)→retts。"""
        self.lr_calls.append({"canonical_text": kw["canonical_text"], "last_asr_text": kw["last_asr_text"], "depth": kw.get("depth", 0)})
        if self.ng_span_found:
            self.events.append(("lr_llm",))      # LLM呼出はNG spanが見つかったときだけ(NO_NG_SPANはLLM 0回)
        result = {"management_id": "fake", "segment_id": kw["segment_id"], "canonical_text": kw["canonical_text"],
                  "last_asr_text": kw["last_asr_text"], "ng_span": {"found": self.ng_span_found}, "status": None}
        if not self.ng_span_found:
            result["status"] = "HUMAN_REVIEW_LOCKED_NO_NG_SPAN"
            return result
        if self.lr_llm_fail:
            raise ValueError("fake LLM down")
        result["selection"] = {"selected": {"rewritten_segment": self.lr_candidate}}
        rr = kw["retts_fn"](self.lr_candidate)
        result["retts_result"] = rr
        result["status"] = "RESOLVED_BY_LOCAL_REWRITE" if rr.get("status") == "OK" else "HUMAN_REVIEW_LOCKED_RETTS_FAILED"
        return result

    # ---- install
    @contextlib.contextmanager
    def patched(self, *, scope=None, fake_clock=True, lr=True):
        import er002_common as common
        import er003_audio_tts_asr_safety as safety
        import er003_b1_p3u_audio as p3u
        import er008_a2_postprocess_slowdown_01 as a2_slowdown
        import er006_asr_provider_routing_01 as asr_routing
        import er006_batch_tts_wiring_01 as bw
        import er006_pronunciation_ledger_01 as pronun
        import er006_secondary_asr_01 as secondary_asr
        import er007_ja_secondary_asr_01 as ja_secondary
        import er008_disfluency_qa_18 as dq18
        import er011_human_review_lock_01 as review_lock
        import er011_open121_repetition_qa_production_01 as rq
        import er020_tts_retry_local_rewrite_01 as er020
        import er025_entity_pronunciation_resolver_core_01 as presolver
        import er109_xz_scope_01 as xz_scope
        import er127_tts_block_policy_01 as blk

        def trim(samples, sr, safety_margin_seconds=None):
            return (np.zeros(sr, dtype=np.float32), {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0,
                                                     "leading_margin_retained_seconds": 0.1, "trailing_margin_retained_seconds": 0.1})

        def transcribe(path, language="en-US", **k):
            return (self.asr_text, None)

        def fake_sleep(s):
            self.clock.sleep(s)
            self.events.append(("sleep", float(s)))
            if self.stop_after_sleeps is not None and len(self.clock.sleeps) >= self.stop_after_sleeps:
                raise blk.TtsBlockStopError("fake STOP during cooldown")

        def apply_slowdown(src, dst, pct=None):
            self.slowdown_calls.append((src, dst, pct))
            shutil.copyfile(src, dst)
            return {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06, "pct": pct}

        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(common, "_call_tts_with_retry", self.call_tts))
            st.enter_context(mock.patch.object(p3u, "trim_english_keyword_silence", trim))
            st.enter_context(mock.patch.object(safety, "detect_duration_anomaly", lambda *a, **k: {"is_anomaly": False}))
            st.enter_context(mock.patch.object(bw, "make_batch_tts_call_fn", lambda *a, **k: (lambda *x, **y: None)))
            st.enter_context(mock.patch.object(asr_routing, "transcribe", transcribe))
            st.enter_context(mock.patch.object(secondary_asr, "evaluate_attempt_with_cascade", self.evaluate))
            st.enter_context(mock.patch.object(secondary_asr, "evaluate_attempt_with_cascade_detail", self.evaluate_detail))
            st.enter_context(mock.patch.object(ja_secondary, "evaluate_attempt_ja_with_cascade", self.evaluate_ja))
            st.enter_context(mock.patch.object(secondary_asr, "HUMAN_REVIEW_LOG_PATH", self.hr_path))
            st.enter_context(mock.patch.object(ja_secondary, "HUMAN_REVIEW_LOG_PATH_JA", self.hr_path_ja))
            st.enter_context(mock.patch.object(dq18, "apply_disfluency_gate",
                                               lambda v, p, language="en", enabled=False: {"verified": bool(v) and not self.dq_ng, "disfluency_checked": bool(enabled), "disfluency_evidence": None}))
            import er033_tts_flash_lite_backend_wiring_01 as flw
            _orig_resolve = flw.resolve_tts_call_and_prompt

            def _resolve(text, style, model, voice, out_path, **kw):
                self.voices.append((voice, model))
                return _orig_resolve(text, style, model, voice, out_path, **kw)
            st.enter_context(mock.patch.object(flw, "resolve_tts_call_and_prompt", _resolve))
            st.enter_context(mock.patch.object(rq, "apply_repetition_qa_gate",
                                               lambda v, *a, **k: {"verified": v, "repetition_qa_checked": bool(k.get("enabled")), "repetition_qa_evidence": None}))
            st.enter_context(mock.patch.object(pronun, "get_hint_for_text", lambda *a, **k: []))
            st.enter_context(mock.patch.object(presolver, "resolve_and_augment_en_style_prefix",
                                               lambda style, text: (style, {"hints_applied": False, "cache_hits": []})))
            st.enter_context(mock.patch.object(review_lock, "ATTEMPT_HISTORY_PATH", self.history_path))
            st.enter_context(mock.patch.object(blk.RUNTIME, "clock", self.clock.clock))
            st.enter_context(mock.patch.object(blk.RUNTIME, "sleep", fake_sleep))
            # 旧600秒cooldown(scope外・golden): 既定引数に束縛された time.sleep を差し替える(er094と同方式)
            st.enter_context(mock.patch.object(er020.maybe_cooldown_before_attempt, "__defaults__", (fake_sleep, er020.COOLDOWN_SECONDS)))
            if lr:
                st.enter_context(mock.patch.object(er020, "run_local_rewrite_recovery", self.lr_run))
            st.enter_context(mock.patch.object(a2_slowdown, "apply_a2_slowdown", apply_slowdown))
            if scope:
                st.enter_context(xz_scope.run_scope(scope))
            yield self

    def cleanup(self):
        shutil.rmtree(self.tmp_root, ignore_errors=True)


def normalize(obj, tmp_root):
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return json.loads(s.replace(tmp_root.replace("\\", "/"), "<TMP>").replace(tmp_root.replace("\\", "\\\\"), "<TMP>"))
