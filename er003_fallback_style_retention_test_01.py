# ============================================================
# er003_fallback_style_retention_test_01.py
# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_06
# ============================================================
# fallback経路での承認Style維持(案1=Style保持型minimal、ユーザー正式決定③、
# Opus条件AレビューB1〜B6・追加必須)のunit test。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_fallback_style_retention_test_01 -v
#
# API呼び出し: 0(実TTS/ASR/LLM呼び出しは全てmock。TTS境界は
# er033_tts_flash_lite_backend_wiring_01のspeech_metadata call_fn factoryを
# 差し替え、実際に`speech_metadata.style`へ渡るpayload=(text, style)を捕捉する)。
#
# 本モジュールのHarnessは、モックprobe
# (er003_fallback_style_retention_probe_01.py)からも再利用する。
from __future__ import annotations

import collections
import inspect
import json
import os
import shutil
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_v1_crosslevel_audio_02_common as crosslevel
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er007_ja_secondary_asr_01 as ja_secondary
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock
import er011_open121_repetition_qa_production_01 as repetition_qa
import er019_family_x_audio_production_runner_01 as runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er025_entity_pronunciation_resolver_core_01 as pron_resolver_core
import er033_tts_flash_lite_backend_wiring_01 as flw
import er033_tts_flash_lite_family_x_styles_01 as fl_styles

FL = "speech_metadata_flash_lite"
SD = "structured_separation"


def _tone_pcm(duration_seconds: float, sample_rate: int = 24000) -> bytes:
    n = int(duration_seconds * sample_rate)
    t = np.arange(n) / sample_rate
    wave = 0.3 * np.sin(2 * np.pi * 220 * t) + 0.1 * np.sin(2 * np.pi * 330 * t)
    pad = np.zeros(int(0.3 * sample_rate))
    full = np.concatenate([pad, wave, pad])
    return (full * 32767).astype("<i2").tobytes()


def _wj(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def _seg_of(path: str) -> str:
    return os.path.splitext(os.path.basename(str(path).replace("\\", "/")))[0]


class Harness:
    """TTS境界(speech_metadata call_fn factory)・ASR・検証Cascade・Local Rewrite・発音resolverを
    差し替え、各TTS呼び出しで実際に渡ったstyle(=speech_metadata.style)を捕捉する。
    verdict_fn(seg, n): n回目(1始まり)のCascade判定がTrue(合格)か。
    tts_fail_fn(seg, n): n回目(1始まり)のTTS呼び出しを例外にするか(技術的失敗)。
    """

    def __init__(self, verdict_fn=None, tts_fail_fn=None, hint_suffix: str | None = None):
        self.calls: list[dict] = []        # TTS呼び出し(1技術retryごと)
        self.lr_calls: list[dict] = []     # Local Rewrite呼び出し
        self.verdict_fn = verdict_fn or (lambda seg, n: True)
        self.tts_fail_fn = tts_fail_fn or (lambda seg, n: False)
        self.hint_suffix = hint_suffix
        self._tts_n = collections.Counter()
        self._v_n = collections.Counter()
        self._last_text: dict[str, str] = {}
        self._stack = None
        self.tmpdir: str | None = None

    # ---- 差し替え実体 ----
    def _factory(self, *a, **kw):
        out_path = kw.get("output_path")
        voice = a[1] if len(a) > 1 else kw.get("voice_name")
        seg = _seg_of(out_path) if out_path else "?"

        def call_fn(payload):
            if isinstance(payload, tuple):
                text, style = payload
            else:
                text, style = payload, payload  # structured_separation(prompt文字列)
            self._tts_n[seg] += 1
            n = self._tts_n[seg]
            self.calls.append({"seg": seg, "n": n, "text": text, "style": style, "voice": voice,
                               "kind": "tts"})
            if self.tts_fail_fn(seg, n):
                raise RuntimeError("400 INVALID_ARGUMENT mock: Model tried to generate text")
            self._last_text[seg] = text
            lang = "ja" if any(ord(c) > 127 for c in text) else "en"
            dur = max(0.8, 0.5 * safety.estimate_max_reasonable_duration_seconds(text, lang))
            return _tone_pcm(dur)
        return call_fn

    def _transcribe(self, path, *a, **kw):
        return self._last_text.get(_seg_of(path), ""), None

    def _verdict(self, out_path):
        seg = _seg_of(out_path)
        self._v_n[seg] += 1
        v = bool(self.verdict_fn(seg, self._v_n[seg]))
        return v, types.SimpleNamespace(classification="EXACT_MATCH" if v else "TRUE_CONTENT_MISMATCH")

    def _cascade_en(self, text, asr_text, classification_history, out_path, *a, **kw):
        v, cls = self._verdict(out_path)
        return v, False, cls

    def _cascade_ja(self, text, asr_text, out_path, *a, **kw):
        v, cls = self._verdict(out_path)
        return v, False, cls

    def _lr(self, segment_id=None, canonical_text=None, last_asr_text=None, retts_fn=None, out_dir=None, **kw):
        self.lr_calls.append({"seg": segment_id})
        r = retts_fn(canonical_text)
        ok = r.get("status") == "OK"
        return {"status": "RESOLVED_BY_LOCAL_REWRITE" if ok else "NOT_RESOLVED", "retts_result": r}

    def _resolve_en(self, prefix, text):
        if self.hint_suffix:
            return prefix + self.hint_suffix, {"hints_applied": True, "cache_hits": [{"h": 1}]}
        return prefix, {"hints_applied": False, "cache_hits": []}

    def _augment_cached(self, prefix, hits):
        return prefix + (self.hint_suffix or "")

    # ---- context ----
    def __enter__(self):
        self.tmpdir = tempfile.mkdtemp(prefix="fb_style_retention_")
        stack = []

        def p(target, name, **kw):
            m = mock.patch.object(target, name, **kw)
            m.start()
            stack.append(m)

        p(flw, "make_speech_metadata_batch_call_fn", side_effect=self._factory)
        p(flw, "make_speech_metadata_call_fn", side_effect=self._factory)
        p(batch_wiring, "make_batch_tts_call_fn", side_effect=self._factory)
        p(routing, "transcribe", side_effect=self._transcribe)
        p(secondary_asr, "evaluate_attempt_with_cascade", side_effect=self._cascade_en)
        p(ja_secondary, "evaluate_attempt_ja_with_cascade", side_effect=self._cascade_ja)
        p(retry_primitive, "maybe_cooldown_before_attempt", return_value=None)
        p(retry_primitive, "run_local_rewrite_recovery", side_effect=self._lr)
        p(pronun_ledger, "get_hint_for_text", return_value=[])
        # disfluency/repetition QAは外部ASR(verbatim)を呼ぶため、合否素通しのstubへ差し替える
        p(dq18, "apply_disfluency_gate",
          side_effect=lambda verified, *a, **k: {"verified": verified, "disfluency_checked": False,
                                                 "disfluency_evidence": None})
        p(repetition_qa, "apply_repetition_qa_gate",
          side_effect=lambda verified, *a, **k: {"verified": verified, "repetition_qa_checked": False,
                                                 "repetition_qa_evidence": None})
        p(pron_resolver_core, "resolve_and_augment_en_style_prefix", side_effect=self._resolve_en)
        p(pron_resolver_core, "augment_style_prefix_with_cached_hits", side_effect=self._augment_cached)
        p(review_lock, "ATTEMPT_HISTORY_PATH", new=os.path.join(self.tmpdir, "attempt_history.jsonl"))
        self._stack = stack
        return self

    def __exit__(self, *exc):
        for m in reversed(self._stack):
            m.stop()
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        return False

    def out(self, seg: str, level: str = "a2", theme: str = "theme_x") -> str:
        d = os.path.join(self.tmpdir, theme, level, "narration")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, f"{seg}.wav")

    def styles(self, seg: str | None = None) -> list[str]:
        return [c["style"] for c in self.calls if seg is None or c["seg"] == seg]


def _slower_combined(base: str) -> str:
    return f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"


EN_TEXT = "Prices keep rising across the whole coffee market this year."
JA_TEXT = "コーヒーの値段は今年も上がり続けています。"


def _attempt_metadata(out_path: str) -> list[dict]:
    d = os.path.join(os.path.dirname(out_path), "attempts")
    res = []
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                with open(os.path.join(d, f), encoding="utf-8") as fh:
                    res.append(json.load(fh))
    return res


class StyleSourceHelperTests(unittest.TestCase):
    def test_describe_style_source(self):
        d = repro01.describe_style_source
        self.assertEqual(d(None), "fallback_default")
        self.assertEqual(d(fl_styles.JA_J2_BRIGHT), "approved_role_style:JA_J2_BRIGHT")
        self.assertEqual(d(fl_styles.EN_COMMENT_E2_UPBEAT), "approved_role_style:EN_COMMENT_E2_UPBEAT")
        self.assertEqual(d(_slower_combined(fl_styles.EN_FULLSTORY_F1_5)), "approved_role_style:EN_FULLSTORY_F1_5")
        self.assertEqual(d("something else"), "caller_override:unrecognized")


class DefaultsAndVersionTests(unittest.TestCase):
    def test_fallback_style_prefix_param_defaults_to_none_everywhere(self):
        for fn in (crosslevel.generate_english_segment_with_fallback.__wrapped__,
                   crosslevel._run_a2_minimal_fallback_attempt,
                   crosslevel._local_rewrite_recovery_for_english_segment_with_fallback,
                   repro01.generate_english_component_minimal_instruction,
                   voice01.generate_charon_english.__wrapped__,
                   voice01._local_rewrite_recovery_for_charon_english,
                   news_tail_fix.generate_news_narration_wide_margin.__wrapped__,
                   news_tail_fix._local_rewrite_recovery_for_news_narration,
                   n3_tts._generate_a2_japanese_minimal_instruction,
                   n3_tts.generate_a2_japanese_with_fallback.__wrapped__,
                   n3_tts.generate_a2_japanese_with_reading_safety,
                   n3_tts.generate_a2_segment_with_slowdown):
            params = inspect.signature(fn).parameters
            self.assertIn("fallback_style_prefix", params, fn.__name__)
            self.assertIsNone(params["fallback_style_prefix"].default, fn.__name__)

    def test_style_version_bumped_to_v5_fallback_style_retention(self):
        v = runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION
        self.assertTrue(v.startswith("v5_"), v)
        self.assertTrue(v.endswith("fallback_style_retention"), v)

    def test_old_v4_cache_is_not_reused_but_v5_is(self):
        tmp = tempfile.mkdtemp(prefix="fb_reuse_")
        try:
            wav = os.path.join(tmp, "x.wav")
            with open(wav, "wb") as f:
                f.write(b"RIFF")
            seg = {"status": "OK", "canonical_text": "t"}
            calls = []
            gen = lambda: calls.append(1) or {"status": "OK", "regenerated": True}
            old = {"style_version": "v4_j2_e2upbeat_f15_tone_refresh", "segments": {"x": seg}}
            r = runner._generate_or_reuse(old, "x", wav, gen, expected_text="t")
            self.assertTrue(r.get("regenerated"))
            self.assertEqual(len(calls), 1)
            new = {"style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "segments": {"x": seg}}
            r2 = runner._generate_or_reuse(new, "x", wav, gen, expected_text="t")
            self.assertTrue(r2.get("reused_from_previous_run"))
            self.assertEqual(len(calls), 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class CrosslevelEnglishFallbackTests(unittest.TestCase):
    """A2英語(Standard): Full Story=承認F1_5+減速連結を標準/fallback/Local Rewriteで維持。"""

    def _run(self, h, seg, std, fb, **kw):
        return crosslevel.generate_english_segment_with_fallback(
            EN_TEXT, h.out(seg), "Prices keep", max_extra_chars=30, style_prefix_override=std,
            fallback_style_prefix=fb, tts_backend=FL, **kw)

    def test_target_role_fallback_style_equals_standard_style(self):
        std = _slower_combined(fl_styles.EN_FULLSTORY_F1_5)
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            r = self._run(h, "full_story_part1", std, std)
            self.assertEqual(r["status"], "OK")
            self.assertTrue(r["fallback_used"])
            self.assertEqual(h.styles(), [std, std, std])  # 標準1・標準2・fallback
            fb_log = r["fallback_attempts_log"][0]
            self.assertEqual(fb_log["style_prefix"], std[:200])
            self.assertEqual(fb_log["style_source"], "approved_role_style:EN_FULLSTORY_F1_5")
            self.assertEqual(fb_log["tts_model_id"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)
            self.assertEqual(fb_log["tts_backend"], FL)
            self.assertNotIn(fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0], "".join(h.styles()[2:]))

    def test_non_target_role_fallback_keeps_legacy_fallback_style(self):
        std = fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"]
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            r = self._run(h, "topic_intro", std, None)
            self.assertEqual(h.styles(), [std, std, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]])
            fb_log = r["fallback_attempts_log"][0]
            self.assertEqual(fb_log["style_source"], "fallback_default")

    def test_pronunciation_hint_still_appended_to_retained_fallback_style(self):
        std = _slower_combined(fl_styles.EN_FULLSTORY_F1_5)
        with Harness(verdict_fn=lambda s, n: n >= 3, hint_suffix=" [HINT]") as h:
            r = self._run(h, "full_story_part2", std, std)
            fb_style = h.styles()[2]
            self.assertTrue(fb_style.startswith(std))
            self.assertTrue(fb_style.endswith("[HINT]"))
            # style_sourceはhint付与前の値で判定される
            self.assertEqual(r["fallback_attempts_log"][0]["style_source"], "approved_role_style:EN_FULLSTORY_F1_5")

    def test_local_rewrite_retts_uses_same_style_for_target_role(self):
        std = _slower_combined(fl_styles.EN_FULLSTORY_F1_5)
        with Harness(verdict_fn=lambda s, n: n >= 4) as h:
            r = self._run(h, "full_story_part3", std, std, enable_connected_speech_equivalence_layer=True)
            self.assertEqual(r["status"], "OK")
            self.assertEqual(len(h.lr_calls), 1)
            self.assertEqual(h.styles(), [std, std, std, std])  # 標準2+fallback1+Local Rewrite再TTS1
            self.assertEqual(r["style_source"], "approved_role_style:EN_FULLSTORY_F1_5")

    def test_local_rewrite_retts_non_target_stays_legacy(self):
        std = fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"]
        with Harness(verdict_fn=lambda s, n: n >= 4) as h:
            self._run(h, "topic_intro", std, None, enable_connected_speech_equivalence_layer=True)
            self.assertEqual(h.styles()[3], fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])

    def test_attempt_audio_metadata_records_four_evidence_fields_and_real_model(self):
        std = _slower_combined(fl_styles.EN_FULLSTORY_F1_5)
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            self._run(h, "full_story_part1", std, std)
            metas = [m for m in _attempt_metadata(h.out("full_story_part1")) if m.get("style_source")]
            fb = [m for m in metas if m.get("style_source") == "approved_role_style:EN_FULLSTORY_F1_5"
                  and m.get("tts_model_id")]
            self.assertTrue(fb, metas)
            m = fb[-1]
            self.assertEqual(m["style_prefix"], std[:200])
            self.assertEqual(m["tts_model_id"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)
            self.assertEqual(m["tts_backend"], FL)
            # B6: 従来のp9a.ENGLISH_MODEL_NAME固定記録ではなく実モデル名
            self.assertEqual(m["model"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)

    def test_default_backend_fallback_is_byte_identical_minimal_prompt(self):
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            crosslevel.generate_english_segment_with_fallback(
                EN_TEXT, h.out("topic_intro"), "Prices keep", max_extra_chars=30)
            # 既定backend(structured_separation)ではfallback promptにMINIMAL_INSTRUCTION_PREFIXが入る
            self.assertIn(repro01.MINIMAL_INSTRUCTION_PREFIX.strip(), h.calls[2]["style"])
            self.assertNotIn(repro01.MINIMAL_INSTRUCTION_PREFIX.strip(), h.calls[0]["style"])


class JapaneseFallbackTests(unittest.TestCase):
    def _run(self, h, seg, std, fb):
        return n3_tts.generate_a2_japanese_with_fallback(
            JA_TEXT, h.out(seg), "コーヒー", max_extra_chars=30, tts_backend=FL,
            style_prefix_override=std, fallback_style_prefix=fb)

    def test_target_role_fallback_uses_j2_verbatim_replacing_old_minimal(self):
        j2 = fl_styles.FAMILY_X_ROLE_STYLE_JA
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            r = self._run(h, "preview", j2, j2)
            self.assertEqual(r["status"], "OK")
            self.assertTrue(r["fallback_used"])
            self.assertEqual(h.styles(), [j2, j2, j2])
            # Opus B2: 旧minimal文との連結はしない(置換)
            self.assertNotIn(n3_tts._A2_JA_MINIMAL_INSTRUCTION_PREFIX.strip(), h.styles()[2])
            self.assertEqual(h.styles()[2], j2)
            fb = r["fallback_attempts_log"][0]
            self.assertEqual(fb["style_source"], "approved_role_style:JA_J2_BRIGHT")
            self.assertEqual(fb["style_prefix"], j2[:200])
            self.assertEqual(fb["tts_model_id"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)

    def test_default_none_keeps_old_minimal_sentence(self):
        j2 = fl_styles.FAMILY_X_ROLE_STYLE_JA
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            r = self._run(h, "preview", j2, None)
            self.assertEqual(h.styles()[2], n3_tts._A2_JA_MINIMAL_INSTRUCTION_PREFIX)
            self.assertEqual(r["fallback_attempts_log"][0]["style_source"], "fallback_default")

    def test_scg_fields_still_surface_on_fallback_attempt(self):
        # SCG(OPEN-258)のlength_ok/scg_info連携を壊していない: fallback attemptにscg_info keyが残る
        j2 = fl_styles.FAMILY_X_ROLE_STYLE_JA
        with Harness(verdict_fn=lambda s, n: n >= 3) as h:
            r = self._run(h, "comment_1", j2, j2)
            self.assertIn("scg_info", r["fallback_attempts_log"][0])
            self.assertIn("scg_info", r)

    def test_with_reading_safety_forwards_fallback_style_prefix(self):
        with mock.patch.object(n3_tts, "generate_a2_japanese_with_fallback",
                               return_value={"status": "OK"}) as m, \
             mock.patch.object(n3_tts.pron_resolver_core, "resolve_unknown_ja_tokens",
                               return_value={"reading_dictionary": {}}):
            n3_tts.generate_a2_japanese_with_reading_safety(
                JA_TEXT, "x/theme/a2/narration/preview.wav", "コーヒー", tts_backend=FL,
                style_prefix_override="S", fallback_style_prefix="F")
            self.assertEqual(m.call_args.kwargs["fallback_style_prefix"], "F")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], "S")

    def test_slowdown_forwards_fallback_style_prefix(self):
        with mock.patch.object(n3_tts.c, "generate_english_segment_with_fallback",
                               return_value={"status": "STOPPED"}) as m:
            n3_tts.generate_a2_segment_with_slowdown(
                EN_TEXT, "x/theme/a2/narration/full_story_part1.wav", "Prices", tts_backend=FL,
                style_prefix_override="S", fallback_style_prefix="F")
            self.assertEqual(m.call_args.kwargs["fallback_style_prefix"], "F")


class B1BTechnicalFallbackTests(unittest.TestCase):
    """Advanced(B1B): 技術的fallback(TTS例外)でも承認styleを維持。"""

    def _fail_first_standard_attempt(self):
        n_fail = common.MAX_TTS_TECHNICAL_RETRY_FOR_TEST if hasattr(common, "MAX_TTS_TECHNICAL_RETRY_FOR_TEST") \
            else voice01.p9a.MAX_TTS_TECHNICAL_RETRY + 1
        return lambda seg, n: n <= n_fail

    def test_voice01_target_role_technical_fallback_keeps_e2_upbeat(self):
        e2 = fl_styles.EN_COMMENT_E2_UPBEAT
        with Harness(tts_fail_fn=self._fail_first_standard_attempt()) as h:
            r = voice01.generate_charon_english(
                EN_TEXT, h.out("comment_1", "b1b"), style_prefix_override=e2, fallback_style_prefix=e2,
                tts_backend=FL)
            self.assertEqual(r["status"], "OK")
            self.assertEqual(r["instruction_type"], "minimal_fallback")
            self.assertEqual(set(h.styles()), {e2})
            self.assertEqual(r["style_source"], "approved_role_style:EN_COMMENT_E2_UPBEAT")
            self.assertEqual(r["style_prefix"], e2)
            log_ok = [a for a in r["attempts_log"] if a.get("status") == "OK"][0]
            self.assertEqual(log_ok["style_source"], "approved_role_style:EN_COMMENT_E2_UPBEAT")
            self.assertEqual(log_ok["tts_model_id"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)
            self.assertEqual(log_ok["tts_backend"], FL)

    def test_voice01_non_target_role_technical_fallback_keeps_legacy_style(self):
        std = fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"]
        with Harness(tts_fail_fn=self._fail_first_standard_attempt()) as h:
            r = voice01.generate_charon_english(
                EN_TEXT, h.out("topic_intro", "b1b"), style_prefix_override=std, tts_backend=FL)
            self.assertEqual(r["instruction_type"], "minimal_fallback")
            self.assertEqual(h.styles()[-1], fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])
            self.assertEqual(r["style_source"], "fallback_default")

    def test_voice01_hint_appended_to_retained_fallback_style(self):
        e2 = fl_styles.EN_COMMENT_E2_UPBEAT
        with Harness(tts_fail_fn=self._fail_first_standard_attempt(), hint_suffix=" [HINT]") as h:
            voice01.generate_charon_english(
                EN_TEXT, h.out("comment_2", "b1b"), style_prefix_override=e2, fallback_style_prefix=e2,
                enable_pronunciation_resolver=True, tts_backend=FL)
            self.assertEqual(h.styles()[-1], e2 + " [HINT]")

    def test_voice01_local_rewrite_forwards_fallback_style(self):
        with mock.patch.object(voice01, "_local_rewrite_recovery_for_charon_english",
                               return_value=None) as m, Harness(verdict_fn=lambda s, n: False) as h:
            voice01.generate_charon_english(
                EN_TEXT, h.out("comment_3", "b1b"), style_prefix_override="S", fallback_style_prefix="F",
                enable_connected_speech_equivalence_layer=True, tts_backend=FL)
            self.assertEqual(m.call_args.kwargs["fallback_style_prefix"], "F")

    def test_news_tail_fix_target_role_technical_fallback_keeps_f1_5(self):
        f15 = fl_styles.EN_FULLSTORY_F1_5
        with Harness(tts_fail_fn=self._fail_first_standard_attempt()) as h:
            r = news_tail_fix.generate_news_narration_wide_margin(
                EN_TEXT, h.out("full_story_part1", "b1b"), style_prefix_override=f15,
                fallback_style_prefix=f15, tts_backend=FL)
            self.assertEqual(r["status"], "OK")
            self.assertEqual(r["instruction_type"], "minimal_fallback")
            self.assertEqual(set(h.styles()), {f15})
            self.assertEqual(r["style_source"], "approved_role_style:EN_FULLSTORY_F1_5")
            self.assertEqual(r["style_prefix"], f15)  # 従来は標準style記録だった。fallbackの実styleを記録

    def test_news_tail_fix_non_target_role_keeps_legacy_fallback_style(self):
        std = fl_styles.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]
        with Harness(tts_fail_fn=self._fail_first_standard_attempt()) as h:
            r = news_tail_fix.generate_news_narration_wide_margin(
                EN_TEXT, h.out("in_one_line", "b1b"), style_prefix_override=std, tts_backend=FL)
            self.assertEqual(h.styles()[-1], fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])
            self.assertEqual(r["style_source"], "fallback_default")

    def test_news_tail_fix_local_rewrite_keeps_style_for_target_only(self):
        with mock.patch.object(news_tail_fix, "_local_rewrite_recovery_for_news_narration",
                               return_value=None) as m, Harness(verdict_fn=lambda s, n: False) as h:
            news_tail_fix.generate_news_narration_wide_margin(
                EN_TEXT, h.out("full_story_part2", "b1b"), style_prefix_override="S", fallback_style_prefix="F",
                enable_connected_speech_equivalence_layer=True, tts_backend=FL)
            self.assertEqual(m.call_args.kwargs["fallback_style_prefix"], "F")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], "S")
        # helper自体: 対象role(fallback指定あり)のみstyle_prefix_overrideを再TTSへ渡す
        with mock.patch.object(news_tail_fix.generate_news_narration_wide_margin, "__wrapped__",
                               return_value={"status": "STOPPED"}) as w, \
             mock.patch.object(retry_primitive, "run_local_rewrite_recovery",
                               side_effect=lambda **kw: (kw["retts_fn"]("t"), {"status": "X"})[1]), \
             Harness() as h:
            news_tail_fix._local_rewrite_recovery_for_news_narration(
                "t", h.out("full_story_part2", "b1b"), None, 15, False, True, False,
                fallback_style_prefix="F", style_prefix_override="S", tts_backend=FL)
            self.assertEqual(w.call_args.kwargs["style_prefix_override"], "S")
            self.assertEqual(w.call_args.kwargs["fallback_style_prefix"], "F")
            news_tail_fix._local_rewrite_recovery_for_news_narration(
                "t", h.out("in_one_line", "b1b"), None, 15, False, True, False,
                fallback_style_prefix=None, style_prefix_override="S", tts_backend=FL)
            self.assertIsNone(w.call_args.kwargs["style_prefix_override"])  # 非対象roleは従来どおり
            self.assertIsNone(w.call_args.kwargs["fallback_style_prefix"])


class RunnerRoleScopeTests(unittest.TestCase):
    """runnerが対象segmentにだけfallback_style_prefixを渡す(Opus B5)。"""

    def _dirs(self, tmp):
        a2 = os.path.join(tmp, "a2")
        b1b = os.path.join(tmp, "b1b")
        os.makedirs(a2)
        os.makedirs(b1b)
        parts = {"title": "T", "title_tts": "T", "part1": "P1.", "part2": "P2.", "part3": "P3.",
                 "in_one_line": "One line."}
        _wj(os.path.join(a2, "parts.json"), parts)
        _wj(os.path.join(b1b, "parts.json"), parts)
        _wj(os.path.join(a2, "a2_support_texts.json"),
            {k: "テスト。" for k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4")})
        _wj(os.path.join(b1b, "b1_support_texts.json"),
            {k: "Test." for k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4")})

    def _kw(self, mock_obj, key):
        return {c.args[0] if False else i: c.kwargs.get(key) for i, c in enumerate(mock_obj.call_args_list)}

    def test_a2_scope_flash_lite(self):
        tmp = tempfile.mkdtemp(prefix="fb_runner_a2_")
        try:
            self._dirs(tmp)
            ok = lambda *a, **k: {"status": "OK"}
            slower = lambda base: f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                   side_effect=ok) as topic, \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                   side_effect=ok) as ja, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=ok) as slow:
                runner.generate_family_x_a2_segments(tmp, "日本語タイトル", tts_backend=FL)
            # topic_intro(対象外)
            self.assertIsNone(topic.call_args.kwargs.get("fallback_style_prefix"))
            # japanese_title/preview/comment1-4(J2)
            self.assertEqual(len(ja.call_args_list), 6)
            for c in ja.call_args_list:
                self.assertEqual(c.kwargs["fallback_style_prefix"], fl_styles.JA_J2_BRIGHT)
                self.assertEqual(c.kwargs["fallback_style_prefix"], c.kwargs["style_prefix_override"])
            # full_story_part1-3は標準と同一の減速連結値、in_one_lineは対象外
            by = {c.args[1].rsplit("/", 1)[1]: c for c in slow.call_args_list}
            for name in ("full_story_part1.wav", "full_story_part2.wav", "full_story_part3.wav"):
                self.assertEqual(by[name].kwargs["fallback_style_prefix"], slower(fl_styles.EN_FULLSTORY_F1_5))
                self.assertEqual(by[name].kwargs["fallback_style_prefix"], by[name].kwargs["style_prefix_override"])
            self.assertIsNone(by["in_one_line.wav"].kwargs["fallback_style_prefix"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a2_default_backend_passes_none_everywhere(self):
        tmp = tempfile.mkdtemp(prefix="fb_runner_a2d_")
        try:
            self._dirs(tmp)
            ok = lambda *a, **k: {"status": "OK"}
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                   side_effect=ok) as topic, \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                   side_effect=ok) as ja, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=ok) as slow:
                runner.generate_family_x_a2_segments(tmp, "日本語タイトル")
            for m in (topic, ja, slow):
                for c in m.call_args_list:
                    self.assertIsNone(c.kwargs.get("fallback_style_prefix"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_b1b_scope_flash_lite(self):
        tmp = tempfile.mkdtemp(prefix="fb_runner_b1b_")
        try:
            self._dirs(tmp)
            ok = lambda *a, **k: {"status": "OK"}
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
                 mock.patch.object(runner.voice01, "generate_charon_english", side_effect=ok) as charon, \
                 mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                   side_effect=ok) as wide:
                runner.generate_family_x_b1_segments(tmp, tts_backend=FL)
            calls = {c.args[1].rsplit("/", 1)[1]: c for c in charon.call_args_list}
            self.assertIsNone(calls["topic_intro.wav"].kwargs.get("fallback_style_prefix"))
            for n in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
                self.assertEqual(calls[f"{n}.wav"].kwargs["fallback_style_prefix"], fl_styles.EN_COMMENT_E2_UPBEAT)
            wcalls = {c.args[1].rsplit("/", 1)[1]: c for c in wide.call_args_list}
            for n in ("full_story_part1", "full_story_part2", "full_story_part3"):
                self.assertEqual(wcalls[f"{n}.wav"].kwargs["fallback_style_prefix"], fl_styles.EN_FULLSTORY_F1_5)
            self.assertIsNone(wcalls["in_one_line.wav"].kwargs["fallback_style_prefix"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_standard_kp_japanese_meaning_gets_j2_and_kp_english_unchanged(self):
        kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "やめる",
                          "japanese_gloss_tts": "やめる"}]}
        tmp = tempfile.mkdtemp(prefix="fb_runner_kp_")
        try:
            ok = lambda *a, **k: {"status": "OK"}
            with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                   side_effect=ok) as en, \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                   side_effect=ok) as ja:
                runner._generate_key_phrase_segments_a2(kp, tmp, None, tts_backend=FL)
            self.assertEqual(ja.call_args.kwargs["fallback_style_prefix"], fl_styles.JA_J2_BRIGHT)
            # KP英語(Master Store経由)にはfallback_style_prefixを渡さない
            self.assertNotIn("fallback_style_prefix", en.call_args.kwargs)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_master_store_fixed_shell_does_not_receive_fallback_style_prefix(self):
        import er006_audio_cost_pilot_02_shared_narration as sn
        with mock.patch.object(sn.voice01, "generate_charon_english", return_value={"status": "OK"}) as m, \
             mock.patch.object(sn.store, "get_or_generate", side_effect=lambda key, out, fn: fn(out)):
            sn.ensure_fixed_english_segment("welcome", tempfile.gettempdir(), tts_backend=FL)
        self.assertNotIn("fallback_style_prefix", m.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
