# FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_08(Fable受入照合の補助): 不具合③(OPEN-283)の『正式経路統合test』。
# 既存fzaq2/fzaq3は、(a) `lr_result()`の固定dictを外側ループ/減速後再検証へ渡す、または (b) LR判定部だけ単体で検証する構成で、
# 『標準2回+fallback1回がNG -> 本物の`generate_english_segment_with_fallback`(本体)が本物の
# `_local_rewrite_recovery_for_english_segment_with_fallback`/`_retts_fn`経由でLR採用 -> 本物の外側ループ
# (`generate_a2_segment_with_slowdown`[Std]/`generate_with_a2_slowdown_outer_loop`[Dialogue/Voices]) -> 本物の
# `apply_a2_slowdown_postprocess` -> 本物の統一judge』という連鎖を1本で通すtestが無かった。本fileはその連鎖を通す。
# 差替え(API 0・費用JPY0): 標準経路(generate_narration_snippet_verified_strict)・fallback attempt(_run_a2_minimal_fallback_attempt。
# TTS+ASR+judgeを1回分差替え)・LRの候補生成/QA(run_local_rewrite_recovery。LLM呼出部のみ。retts_fnは本物を呼ぶ)・減速(ffmpeg)・
# 減速後ASR(routing.transcribe)・Secondary STT。Production moduleは無変更。記事非依存fixture。
import os

import er006_secondary_asr_01 as sec
import er011_human_review_lock_01 as review_lock
import er003_v1_crosslevel_audio_02_common as crosslevel
import er003_v1_n3_01_tts_generate as tg
from er020_lr_post_rewrite_expected_text_fzaq2_test_01 import (  # noqa: F401  (autouse fixture _iso/helperを再利用)
    CANON, REWRITTEN, ASR_REWRITTEN, ASR_WRONG, Az, _iso, _fake_stretch, _fallback_outcome, _spy_judge)

ASR_ORIG_NG = "Water came slowly through a crack in the rock. Mellos drank, got onto his knees, and stood up."


class Harness:
    """3回NG -> LR採用 -> 再TTSの連鎖で、各差替え点が受け取った文を記録する。"""

    def __init__(self, out):
        self.out = out
        self.fallback_texts, self.std_calls, self.lr_calls, self.retts_texts = [], 0, [], []


def _install(monkeypatch, tmp_path, *, lr_adopted=True, post_slowdown_asr=ASR_REWRITTEN):
    out = str(tmp_path / "theme_x" / "a2" / "narration" / "full_story_part3_c1.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    h = Harness(out)

    def std(*a, **k):                                   # 標準2回ともNG
        h.std_calls += 1
        open(out, "wb").write(b"STD")
        return {"status": "STOPPED", "attempts_log": [{"attempt": 1, "asr_text": ASR_ORIG_NG}, {"attempt": 2, "asr_text": ASR_ORIG_NG}]}

    def fb(text, out_path, max_len, hist, ecs, dq, erq, tts_backend="structured_separation", attempt_ctx=None):
        h.fallback_texts.append(text)
        open(out_path, "wb").write(b"FB_" + text[:8].encode())
        if text == CANON:                                # 通算3回目(fallback)もNG
            o = _fallback_outcome(False)
            o["asr_text"], o["stop_retrying"] = ASR_ORIG_NG, True
        else:                                            # LR再TTS(書換え後文)は合格
            o = _fallback_outcome(True)
            o["asr_text"] = ASR_REWRITTEN
        o["result"] = {"status": "OK", "path": out_path, "text": text, "sha256": None, "duration_seconds": 2.0}
        return o

    def lr(*, segment_id, canonical_text, last_asr_text, retts_fn, out_dir=None, **kw):
        h.lr_calls.append((segment_id, canonical_text, last_asr_text))
        if not lr_adopted:                               # 全候補QA不合格相当(LR非採用)
            return {"status": "HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA", "canonical_text": canonical_text,
                    "selection": {"selected": None}, "retts_result": None}
        h.retts_texts.append(REWRITTEN)
        rt = retts_fn(REWRITTEN)                         # 本物の_retts_fn(=_run_a2_minimal_fallback_attempt経由)を呼ぶ
        return {"status": "RESOLVED_BY_LOCAL_REWRITE" if rt.get("status") == "OK" else "HUMAN_REVIEW_LOCKED_RETTS_FAILED",
                "canonical_text": canonical_text,
                "selection": {"selected": {"id": "1", "rewritten_segment": REWRITTEN}}, "retts_result": rt}

    monkeypatch.setattr(crosslevel, "generate_narration_snippet_verified_strict", std)
    monkeypatch.setattr(crosslevel, "_run_a2_minimal_fallback_attempt", fb)
    monkeypatch.setattr(crosslevel.retry_primitive, "run_local_rewrite_recovery", lr)
    monkeypatch.setattr(crosslevel.retry_primitive, "maybe_cooldown_before_attempt", lambda *a, **k: None)
    monkeypatch.setattr(crosslevel.review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    # guarded_generate(Lock store読書き)を外した本体を、本物の関数としてそのまま使う
    real_body = crosslevel.generate_english_segment_with_fallback.__wrapped__
    monkeypatch.setattr(tg.c, "generate_english_segment_with_fallback", real_body)
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (post_slowdown_asr, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az())
    return h, real_body


def _assert_lr_chain(h, r, seen):
    assert h.std_calls == 1
    assert h.fallback_texts == [CANON, REWRITTEN]        # fallback(元原稿)がNG -> LRの再TTSは書換え後文
    assert [c[1] for c in h.lr_calls] == [CANON]         # LRへ渡る正解原稿は元原稿、last_asr_textは直近NG転写
    assert h.lr_calls[0][2] == ASR_ORIG_NG
    assert r["local_rewrite_recovery"]["status"] == "RESOLVED_BY_LOCAL_REWRITE"
    assert r["canonical_text_before_local_rewrite"] == CANON
    # 核心: 減速後再検証の期待テキストは書換え後文(Melos入りの旧原稿ではない)
    assert seen == [REWRITTEN]
    assert r["post_slowdown_expected_text_source"] == "local_rewrite_text"
    assert r["post_slowdown_asr_text"] == ASR_REWRITTEN
    assert r["slowdown_applied"] is True and r["status"] == "OK"


def test_std_path_generate_a2_segment_with_slowdown_lr_then_slowdown_uses_rewritten_text(tmp_path, monkeypatch):
    h, _ = _install(monkeypatch, tmp_path)
    seen = _spy_judge(monkeypatch)
    r = tg.generate_a2_segment_with_slowdown(CANON, h.out, "Water", enable_connected_speech_equivalence_layer=True)
    _assert_lr_chain(h, r, seen)
    assert [a["status"] for a in r["slowdown_attempts_log"]] == ["OK"]   # 減速後NGによる取り直しは起きない


def test_outer_loop_generate_with_a2_slowdown_outer_loop_lr_then_slowdown_uses_rewritten_text(tmp_path, monkeypatch):
    h, real_body = _install(monkeypatch, tmp_path)
    seen = _spy_judge(monkeypatch)
    r = tg.generate_with_a2_slowdown_outer_loop(
        "full_story_part3_c1", CANON, h.out,
        lambda max_attempts: real_body(CANON, h.out, "Water", max_attempts=max_attempts,
                                       enable_connected_speech_equivalence_layer=True))
    _assert_lr_chain(h, r, seen)


def test_precondition_lr_not_adopted_never_reaches_slowdown_and_expected_text_untouched(tmp_path, monkeypatch):
    h, _ = _install(monkeypatch, tmp_path, lr_adopted=False)
    seen = _spy_judge(monkeypatch)
    r = tg.generate_a2_segment_with_slowdown(CANON, h.out, "Water", enable_connected_speech_equivalence_layer=True)
    assert h.fallback_texts == [CANON] and seen == []    # 書換え再TTSなし、減速後judgeに到達しない(従来のSTOPPED経路)
    assert r["status"] != "OK" and "post_slowdown_expected_text_source" not in r   # 従来の不合格終了(ASR_VALIDATION_UNCERTAIN)


def test_final_ng_after_lr_still_reaches_hr_lock_with_canonical_key(tmp_path, monkeypatch):
    h, _ = _install(monkeypatch, tmp_path, post_slowdown_asr=ASR_WRONG)   # 書換え後文とも一致しない=本当のNG
    seen = _spy_judge(monkeypatch)
    rec = []
    monkeypatch.setattr(review_lock, "record_outcome",
                        lambda out_path, text, language, result, **k: rec.append((text, result.get("status"))) or {"state": "HUMAN_REVIEW_REQUIRED"})
    r = tg.generate_a2_segment_with_slowdown(CANON, h.out, "Water", enable_connected_speech_equivalence_layer=True)
    assert seen and set(seen) == {REWRITTEN}             # NGの判定も書換え後文との照合(旧原稿ではない)
    assert r["status"] == "STOPPED" and r["human_review_required"] is True
    assert rec == [(CANON, "STOPPED")]                   # Lock keyは元の原稿のまま(Lock/承認記録の同一性維持)
