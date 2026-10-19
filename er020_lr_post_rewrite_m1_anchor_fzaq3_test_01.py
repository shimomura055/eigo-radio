# FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03: Opus_H必須修正(条件1 M5 / 条件2 Z形entry / 条件3 HR queue行)の固定test。
# 全てmock(ASR/Secondary/TTS/ffmpegは差替え)。API呼出0・費用JPY0・新規TTS 0。HR queue等の書込先はtmp_pathへ退避。
import json
import os
import time as _real_time
import types

import pytest

import er006_m1_multi_candidate_01 as M
import er006_secondary_asr_01 as sec
import er011_human_review_lock_01 as review_lock
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er063_family_z_audio_01 as z
import er078_asr_unified_attempt_ctx_01 as actx_mod
import er003_v1_n3_01_tts_generate as tg
import er020_lr_post_rewrite_expected_text_fzaq2_test_01 as base  # lr_result/Az/_fake_stretch/定数を再利用

CANON = "Melos said it."          # 元原稿(LR前)
REWRITTEN = "Melos said."         # 書換え後(Melosを残す=問題span以外の書換え)
HIT = "Mello said."               # M1が受理する転写(Ledger候補がある場合のみ)

T0 = "2026-10-19T10:00:00"        # 元segment開始(anchor凍結時刻)
T1 = "2026-10-19T10:10:00"        # LR再TTS/減速後再検証の時刻(現在時刻で凍結するとこちらになる=旧バグ)


def _entry(updated_at):
    return {"surface": "melos", "entity_type": "cascade_unresolved_entity", "canonical_spelling": "Melos",
            "expected_pronunciation_ipa": "/ˈmiː.lɑːs/（米国英語の暫定候補）; /ˈmiː.lɒs/（英国英語）",
            "alternate_pronunciations": ["/ˈmɪlɒs/（英語での別読みとして提示される場合あり）",
                                     "/ˈmɛlɒs/ または /ˈmɛloʊs/（音楽用語・一般名詞としての英語の別読み）"],
            "confidence": "low",
            "sources": ["https://en.wiktionary.org/wiki/melos"], "updated_at": updated_at}


class _Clock:
    """sec.timeのstrftimeだけを固定値にする(他属性は実timeへ委譲)。"""
    def __init__(self, now):
        self.now = now

    def __getattr__(self, name):
        if name == "strftime":
            return lambda fmt, *a: self.now
        return getattr(_real_time, name)


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda *a, **k: None)
    monkeypatch.setattr(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None)
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", str(tmp_path / "hrq_en.jsonl"))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    monkeypatch.setattr(review_lock, "append_attempt_history_event", lambda *a, **k: None)
    yield
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()


def _melos_sources(fz):
    return [c.source for c in fz.word("melos").candidates]


def _freeze_anchor(monkeypatch, ledger):
    """元segmentの最初の試行前(T0)にanchorを凍結する。"""
    monkeypatch.setattr(sec, "time", _Clock(T0))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: ledger)
    return sec._m1_frozen_for(CANON)


# ---------- (i) 元segment開始より後にupsertされたLedgerエントリは、LR後の凍結でも候補から除外される ----------
def test_i_entry_upserted_after_original_segment_start_is_excluded_after_lr(monkeypatch):
    anchor = _freeze_anchor(monkeypatch, {})                                     # 元segment開始時点: Melosの調査結果なし
    assert anchor is not None and anchor.segment_started_at == T0
    # 同じsegment内でLR前にTier3調査がupsertされた(T0より後)→ LR再TTS(現在時刻T1)
    late = {"k1": _entry("2026-10-19T10:05:00")}
    monkeypatch.setattr(sec, "time", _Clock(T1))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: late)
    # 旧実装相当(anchorなし=現在時刻T1で凍結): 候補に入ってしまう(これがOF-179違反の再現)
    legacy = sec._m1_frozen_for(REWRITTEN)
    assert any(s.startswith("C2_ledger") for s in _melos_sources(legacy))
    sec._M1_FROZEN_CACHE.pop(REWRITTEN)
    # 新実装(anchor指定): 元segment開始(T0)で凍結 → 除外
    fz = sec._m1_frozen_for(REWRITTEN, anchor_text=CANON)
    assert fz is not None and fz.segment_started_at == T0
    assert not any(s.startswith("C2_ledger") for s in _melos_sources(fz))
    # 減速後再検証(apply_a2_slowdown_postprocess)も同じanchor経由=同じ凍結物(再計算しない)
    assert sec._m1_frozen_for(REWRITTEN, anchor_text=CANON) is fz


def test_i_end_to_end_lr_retts_judge_does_not_accept_late_candidate(monkeypatch):
    _freeze_anchor(monkeypatch, {})
    late = {"k1": _entry("2026-10-19T10:05:00")}
    monkeypatch.setattr(sec, "time", _Clock(T1))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: late)
    monkeypatch.setattr(sec.routing, "transcribe", lambda *a, **k: (None, None))
    ctx = actx_mod.build_attempt_ctx(1, 1, script_version="v1", m1_anchor_text=CANON)
    d = sec.evaluate_attempt_with_cascade_detail(REWRITTEN, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                 attempt_ctx=ctx)
    assert "m1_multi_candidate" not in d                 # 後から調べた候補でM1自動PASSしない
    sec._reset_m1_freeze_cache()
    _freeze_anchor(monkeypatch, {})
    monkeypatch.setattr(sec, "time", _Clock(T1))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: late)
    d2 = sec.evaluate_attempt_with_cascade_detail(REWRITTEN, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                  attempt_ctx={"slot": 1, "script_version": "v1", "is_last_slot": True})
    assert d2["verified"] and "m1_multi_candidate" in d2  # 旧経路(anchorなし)は現在時刻凍結で受理してしまう=修正の必要性の再現


# ---------- (ii) 開始前エントリは候補のまま ----------
def test_ii_entry_before_original_segment_start_stays_candidate(monkeypatch):
    early = {"k1": _entry("2026-10-19T09:00:00")}
    anchor = _freeze_anchor(monkeypatch, early)
    assert any(s.startswith("C2_ledger") for s in _melos_sources(anchor))
    monkeypatch.setattr(sec, "time", _Clock(T1))
    fz = sec._m1_frozen_for(REWRITTEN, anchor_text=CANON)
    assert any(s.startswith("C2_ledger") for s in _melos_sources(fz))
    monkeypatch.setattr(sec.routing, "transcribe", lambda *a, **k: (None, None))
    ctx = actx_mod.build_attempt_ctx(1, 1, script_version="v1", m1_anchor_text=CANON)
    d = sec.evaluate_attempt_with_cascade_detail(REWRITTEN, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                 attempt_ctx=ctx)
    assert d["verified"] and "m1_multi_candidate" in d   # 開始前の承認済み候補はLR後も従来どおり使える


# ---------- (iii) anchorが無い(未凍結)場合はM1不発 ----------
def test_iii_unfrozen_anchor_disables_m1_and_never_freezes_with_now(monkeypatch):
    monkeypatch.setattr(sec, "time", _Clock(T1))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {"k1": _entry("2026-10-19T09:00:00")})
    assert sec._m1_frozen_for(REWRITTEN, anchor_text=CANON) is None       # anchor(CANON)が凍結されていない
    assert sec._M1_FROZEN_CACHE == {}                                      # 現在時刻での凍結もキャッシュもしない
    sec._M1_FROZEN_CACHE[CANON] = None                                     # anchor凍結に失敗していた場合もM1不発
    assert sec._m1_frozen_for(REWRITTEN, anchor_text=CANON) is None
    monkeypatch.setattr(sec.routing, "transcribe", lambda *a, **k: (None, None))
    ctx = actx_mod.build_attempt_ctx(1, 1, script_version="v1", m1_anchor_text=CANON)
    d = sec.evaluate_attempt_with_cascade_detail(REWRITTEN, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                 attempt_ctx=ctx)
    assert "m1_multi_candidate" not in d


# ---------- (iv) LRなし経路はbyte-identical ----------
def test_iv_no_lr_path_is_unchanged(monkeypatch):
    # ctx組立て: anchor未指定なら従来のdictと完全一致(キー追加なし)
    assert actx_mod.build_attempt_ctx(2, 3, script_version="v0", max_len=10) == {
        "slot": 2, "is_last_slot": False, "script_version": "v0", "max_len": 10}
    calls = []
    real = sec._m1_frozen_for

    def spy(*a, **k):
        calls.append((a, k))
        return real(*a, **k)

    monkeypatch.setattr(sec, "_m1_frozen_for", spy)
    monkeypatch.setattr(sec, "time", _Clock(T1))
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {"k1": _entry("2026-10-19T09:00:00")})
    monkeypatch.setattr(sec.routing, "transcribe", lambda *a, **k: (None, None))
    d1 = sec.evaluate_attempt_with_cascade_detail(CANON, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                  attempt_ctx={"slot": 1, "is_last_slot": True})
    sec._reset_m1_freeze_cache()
    d2 = sec.evaluate_attempt_with_cascade_detail(CANON, HIT, [], "dummy.wav", language="en-US", cascade_enabled=True,
                                                  attempt_ctx=None)
    assert calls == [((CANON,), {}), ((CANON,), {})]       # 従来どおり引数1つ(anchor kwargなし)
    import re
    norm = lambda d: re.sub(r"\d{9,}", "N", json.dumps(d, sort_keys=True, default=str))  # object id等の非決定値のみ正規化
    assert norm(d1) == norm(d2)


# ---------- 配線: 減速後再検証はLR採用時のみanchor(元原稿)を渡す ----------
def _post(tmp_path, result, canonical=base.CANON, name="full_story_part3_c1", **kw):
    (tmp_path / f"{name}.wav").write_bytes(b"PRE")
    return tg.apply_a2_slowdown_postprocess(name, str(tmp_path), canonical, result, **kw)


def _ctx_spy(monkeypatch):
    seen = []
    real = sec.evaluate_attempt_with_cascade_detail

    def spy(expected, *a, **k):
        seen.append((expected, (k.get("attempt_ctx") or {}).copy()))
        return real(expected, *a, **k)

    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade_detail", spy)
    return seen


def test_wiring_slowdown_passes_anchor_only_when_lr_adopted(tmp_path, monkeypatch):
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})
    base._setup(monkeypatch, base.ASR_REWRITTEN, base.Az())
    seen = _ctx_spy(monkeypatch)
    _post(tmp_path, base.lr_result())
    assert seen[-1][0] == base.REWRITTEN and seen[-1][1].get("m1_anchor_text") == base.CANON
    seen.clear()
    plain = {"status": "OK", "text": base.CANON, "sha256": None, "duration_seconds": 2.0}
    _post(tmp_path, plain)
    assert seen[-1][0] == base.CANON and "m1_anchor_text" not in seen[-1][1]   # LRなし=従来のctx(キー追加なし)


def test_wiring_crosslevel_and_leaf_signatures_carry_anchor():
    import inspect
    import er003_v1_sing01_voice01_generate as v1
    import er003_v1_sing01_news_tail_fix as nt
    import er003_v1_crosslevel_audio_02_common as cl
    for fn in (v1.generate_charon_english.__wrapped__, nt.generate_news_narration_wide_margin.__wrapped__):
        assert inspect.signature(fn).parameters["m1_anchor_text"].default is None   # 既定None=既存呼出は不変
    src = inspect.getsource(cl._local_rewrite_recovery_for_english_segment_with_fallback)
    assert '"m1_anchor_text": text' in src
    assert "m1_anchor_text=text" in inspect.getsource(v1._local_rewrite_recovery_for_charon_english)
    assert "m1_anchor_text=text" in inspect.getsource(nt._local_rewrite_recovery_for_news_narration)


# ---------- 条件3: HR queue行へ元原稿(Lock/承認key)と正解原稿の出典を記録 ----------
def test_condition3_hr_queue_row_records_lock_canonical_text_and_source(tmp_path, monkeypatch):
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})
    base._setup(monkeypatch, base.ASR_WRONG, base.Az((base.ASR_WRONG, None)))
    r = _post(tmp_path, base.lr_result(), is_last_slot=True, log_human_review=True)
    assert r["status"] == "STOPPED"
    rows = [json.loads(l) for l in open(sec.HUMAN_REVIEW_LOG_PATH, encoding="utf-8")]
    assert len(rows) == 1
    assert rows[0]["canonical_text"] == base.REWRITTEN                    # 判定に使った文(書換え後)
    assert rows[0]["lock_canonical_text"] == base.CANON                   # 承認(record_human_approval)のkey=元の原稿
    assert rows[0]["expected_text_source"] == "local_rewrite_text"


def test_condition3_hr_queue_row_unchanged_without_lr(tmp_path, monkeypatch):
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})
    base._setup(monkeypatch, base.ASR_WRONG, base.Az((base.ASR_WRONG, None)))
    plain = {"status": "OK", "text": base.CANON, "sha256": None, "duration_seconds": 2.0}
    _post(tmp_path, plain, is_last_slot=True, log_human_review=True)
    rows = [json.loads(l) for l in open(sec.HUMAN_REVIEW_LOG_PATH, encoding="utf-8")]
    assert rows[0]["canonical_text"] == base.CANON and rows[0]["lock_canonical_text"] == base.CANON
    assert rows[0]["expected_text_source"] == "canonical_text"


# ---------- 条件2: Z形entry(audio_text_deviation)も単一参照点を通る ----------
def _z_entry(tmp_path, with_lr=True):
    wav = str(tmp_path / "full_story_part3_c1.wav")
    open(wav, "wb").write(b"x")
    spec = z.ClipSpec(clip_id="full_story_part3_c1", level="a2", kind="narrator", text=base.CANON, voice="v",
                      role_key="narrator")
    res = {"status": "OK", "asr_text": base.ASR_REWRITTEN}
    if with_lr:
        res.update(base.lr_result())
        res["asr_text"] = base.ASR_REWRITTEN
    try:
        return z.build_entry(spec, wav, res)
    except KeyError:  # role_keyがFAMILY_Z_ROLE_STYLEに無い場合は実在キーへ
        spec = z.ClipSpec(clip_id="full_story_part3_c1", level="a2", kind="narrator", text=base.CANON, voice="v",
                          role_key=next(iter(z.FAMILY_Z_ROLE_STYLE)))
        return z.build_entry(spec, wav, res)


def test_condition2_z_entry_resolves_to_rewritten_text(tmp_path):
    e = _z_entry(tmp_path)
    assert "local_rewrite_recovery" not in e and e["audio_text_deviation"]["audio_text_after"] == base.REWRITTEN
    assert retry_primitive.resolve_expected_text_after_local_rewrite(e, base.CANON) == (base.REWRITTEN, "local_rewrite_text")
    e0 = _z_entry(tmp_path, with_lr=False)
    assert e0["audio_text_deviation"] is None
    assert retry_primitive.resolve_expected_text_after_local_rewrite(e0, base.CANON) == (base.CANON, "canonical_text")
    # audio_text_afterが空/元原稿と同一ならLR採用扱いにしない(fail-safe)
    for bad in ("", "  ", None, base.CANON):
        ee = dict(e0, audio_text_deviation={"audio_text_after": bad})
        assert retry_primitive.resolve_expected_text_after_local_rewrite(ee, base.CANON)[1] == "canonical_text"


def test_condition2_z_entry_guard_and_rejudge_use_rewritten_text(tmp_path):
    import er019_family_x_validation_inheritance_01 as vi
    import er078_reuse_value_guard_01 as rvg
    e = _z_entry(tmp_path)
    ok = vi.rejudge_with_current_judge(e, "a2", "full_story_part3_c1", force_lang="en")
    assert ok["ok"] is True and ok["secondary_new_calls"] == 0
    assert "He drank" in ok["tts_input"] and "Melos" not in ok["tts_input"]
    assert rvg.guard_entry(e, label="x")["blocked"] is False
    # LR記録なしのZ entryは従来どおり旧原稿で照合(NG)
    e0 = _z_entry(tmp_path, with_lr=False)
    assert vi.rejudge_with_current_judge(e0, "a2", "full_story_part3_c1", force_lang="en")["ok"] is False
