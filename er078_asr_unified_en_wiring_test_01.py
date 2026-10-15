# AUW 委任_03: EN統一judge配線(adapter)・_is_numberマーカー拡張・PASS_WITH_WARNING registry配線・ページ節のtest。
# 全てmock(Primary ASR=routing.transcribe、Secondary=get_full_text_via_azure_stt_with_phrase_list)。API呼出0・費用JPY0。
import json
import os
import shutil
import tempfile
import wave

import pytest

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_pass_with_warning_registry_01 as reg

CANON = "Ottoni and colleagues published a study."
PRIMARY_NG = "A Tony and colleagues published a study."   # 固有名詞のみの差(Primary NG、保護差なし=P3)
CANON_NUM = "The study followed 2 groups of participants."


class Az:
    """Secondary(Azure)のmock。callsは実呼出回数。"""

    def __init__(self, result=(None, "no result"), raises=None):
        self.result, self.raises, self.calls = result, raises, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.result


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    # Primary#2が呼ばれたら失敗させる(廃止の確認)
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: pytest.fail("Primary#2(同一音声のOpenAI再転写)は廃止のはず"))
    monkeypatch.setattr(val, "aggregate_entity_like_sources", val.aggregate_entity_like_sources)
    yield
    sec.reset_secondary_cache()


def _wav(tmp_path, name="a.wav", seconds=1, rate=8000, fill=b"\x00"):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(fill * (rate * seconds))
    return str(p)


def run(canon, asr, wav, az, monkeypatch, **kw):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    kw.setdefault("cascade_enabled", True)
    return sec.evaluate_attempt_with_cascade_detail(canon, asr, [], wav, **kw)


# ---------------- 状態 -> 戻り値 ----------------
def test_primary_pass_no_secondary_and_audit_record(tmp_path, monkeypatch):
    az = Az(("never", None))
    d = run(CANON, CANON, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is True and d["stop_retrying"] is False and az.calls == 0
    j = d["asr_judgement"]
    assert j["state"] == uj.PASS and j["secondary"]["called"] is False
    assert j["audio_sha256"] and len(j["audio_sha256"]) == 64      # Primary PASSでも採用音声のsha256を記録
    assert j["adapter"]["azure_real_calls"] == 0


def test_primary_ng_secondary_pass_becomes_pass_with_warning(tmp_path, monkeypatch):
    az = Az((CANON, None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is True and az.calls == 1
    j = d["asr_judgement"]
    assert j["state"] == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in j["warnings"]
    assert j["primary"]["text"] == PRIMARY_NG and j["secondary"]["text"] == CANON
    assert any(s["step"] == "secondary_1" for s in d["steps"]) and d["cascade_invoked"] is True
    assert d["human_review_required"] is False and d["stop_retrying"] is False
    assert d["classification"].should_pass is True          # 旧互換: Secondary転写の分類(should_pass)


@pytest.mark.parametrize("res,raises", [((None, "azure error"), None), (("", None), None), (None, RuntimeError("boom"))])
def test_secondary_failure_is_ng_secondary_unavailable_never_pass(tmp_path, monkeypatch, res, raises):
    az = Az(res if res is not None else (None, None), raises=raises)
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE
    assert d["asr_judgement"]["secondary"]["unavailable"] is True and d.get("technical_stop")
    assert d["stop_retrying"] is False       # HR直行ではなく次attempt/slotへ(DESIGN_01 §4-4)


def test_value_guard_diff_ng_protected_even_if_secondary_would_pass(tmp_path, monkeypatch):
    az = Az((CANON_NUM, None))     # SecondaryはPASSするはずの転写
    d = run(CANON_NUM, "The study followed 3 groups of participants.", _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and az.calls == 0
    assert d["asr_judgement"]["state"] == uj.NG_PROTECTED and d["asr_judgement"]["reason_code"] == "p1_value_diff"


def test_percent_25_vs_26_is_protected_after_is_number_extension(tmp_path, monkeypatch):
    az = Az(("The rate is 25% today.", None))
    d = run("The rate is 25% today.", "The rate is 26% today.", _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED
    assert d["classification"].protected.number_mismatches    # 旧: 内容語差分へ流れていた穴


def test_negation_diff_ng_protected_no_secondary(tmp_path, monkeypatch):
    az = Az(("We can go home now.", None))
    d = run("We can go home now.", "We cannot go home now.", _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED


def test_ambiguous_value_goes_p3_and_same_surface_is_warning(tmp_path, monkeypatch):
    canon = "He waited for the bus."
    az = Az((canon, None))
    d = run(canon, "He waited 4 the bus.", _wav(tmp_path), az, monkeypatch)
    j = d["asr_judgement"]
    assert az.calls == 1 and j["p3_entry"] == "p3_primary_ng" and j["value_guard"]["primary"]["kind"] == "AMBIGUOUS"
    assert d["verified"] is True and j["state"] == uj.PASS_WITH_WARNING and uj.W_NUMERIC_AMBIGUOUS_SURFACE in j["warnings"]


def test_ambiguous_value_secondary_not_same_surface_is_ng(tmp_path, monkeypatch):
    canon = "He waited for the bus."
    az = Az(("He waited four the bus.", None))
    d = run(canon, "He waited 4 the bus.", _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] in (uj.NG_BOTH, uj.NG_PROTECTED)


def test_secondary_not_accepted_is_ng_both(tmp_path, monkeypatch):
    az = Az(("Something entirely different was said here today.", None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_BOTH and az.calls == 1


def test_primary_asr_failure_text_none(tmp_path, monkeypatch):
    az = Az((CANON, None))
    d = run(CANON, None, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_PRIMARY_ASR_FAILURE and az.calls == 0


# ---------------- 後方互換 ----------------
def test_cascade_disabled_is_plain_and_never_judges(tmp_path, monkeypatch):
    az = Az(("x", None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch, cascade_enabled=False)
    assert d["verified"] is False and az.calls == 0 and "asr_judgement" not in d


def test_return_dict_keeps_legacy_keys(tmp_path, monkeypatch):
    d = run(CANON, CANON, _wav(tmp_path), Az(), monkeypatch)
    for k in ("verified", "stop_retrying", "classification", "cascade_invoked", "steps", "final_status", "human_review_required",
              "canonical_text", "wav_path", "cost_guard_triggered", "non_latin_cascade_invoked",
              "connected_speech_equivalence_layer_invoked"):
        assert k in d, k


def test_tuple_wrapper_returns_val_shape_and_forwards_detail(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((CANON, None)))
    out = {}
    verified, stop, cls = sec.evaluate_attempt_with_cascade(CANON, PRIMARY_NG, [], _wav(tmp_path), detail_out=out)
    assert verified is True and stop is False and cls.should_pass and out["asr_judgement"]["state"] == uj.PASS_WITH_WARNING


# ---------------- Secondary重複呼出防止 ----------------
def test_non_latin_layer_and_judge_share_one_azure_call(tmp_path, monkeypatch):
    az = Az(("garbage text", None))     # 非ラテン層でもjudgeでもPASSしない転写
    d = run("new normal", "新常態", _wav(tmp_path), az, monkeypatch, enable_non_latin_cascade=True)
    assert d["non_latin_cascade_invoked"] is True and d["verified"] is False
    assert az.calls == 1, "非ラテン層とjudgeのSecondaryで同一wavのAzure呼出は1回のはず"
    assert d["asr_judgement"]["secondary"]["cached"] is True and d["asr_judgement"]["adapter"]["azure_real_calls"] == 1


def test_same_wav_second_evaluation_is_cache_hit_within_a_run(tmp_path, monkeypatch):
    sec.begin_secondary_run()       # opt-in: run単位の共有cache
    wav = _wav(tmp_path)
    az = Az((CANON, None))
    run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    d2 = run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    assert az.calls == 1 and d2["verified"] is True and d2["asr_judgement"]["secondary"]["cached"] is True


def test_failures_are_not_cached(tmp_path, monkeypatch):
    sec.begin_secondary_run()
    wav = _wav(tmp_path)
    az = Az((None, "err"))
    run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    assert az.calls == 2


def test_default_has_no_cross_call_cache_state(tmp_path, monkeypatch):
    wav = _wav(tmp_path)
    az = Az((CANON, None))
    run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    run(CANON, PRIMARY_NG, wav, az, monkeypatch)
    assert az.calls == 2        # 既定は呼出単位cache: test間・call間に結果を持ち越さない


def test_circuit_breaker_opens_after_consecutive_secondary_failures_when_run_started(tmp_path, monkeypatch):
    rs = sec.begin_secondary_run(circuit_breaker_threshold=2)
    az = Az((None, "err"))
    for i in range(3):
        d = run(CANON, PRIMARY_NG, _wav(tmp_path, f"c{i}.wav", fill=bytes([i + 1])), az, monkeypatch)
        assert d["verified"] is False
    assert rs.circuit_open is True and az.calls == 2     # 3回目はSecondaryを呼ばない(技術STOP)
    assert d["asr_judgement"]["reason_code"] == "secondary_circuit_open"
    assert d.get("technical_stop")


def test_nonexistent_wav_never_shares_cache_across_calls(monkeypatch):
    sec.begin_secondary_run()
    az = Az((CANON, None))
    run(CANON, PRIMARY_NG, "dummy.wav", az, monkeypatch)
    run(CANON, PRIMARY_NG, "dummy.wav", az, monkeypatch)
    assert az.calls == 2     # test間汚染防止(実在しないwavはprocess共有cacheを使わない)


# ---------------- force_secondary ----------------
def test_force_secondary_agree_is_plain_pass(tmp_path, monkeypatch):
    az = Az((CANON, None))
    d = run(CANON, CANON, _wav(tmp_path), az, monkeypatch, force_secondary=True)
    assert d["verified"] is True and az.calls == 1 and d["asr_judgement"]["state"] == uj.PASS
    assert any(s["step"] == "secondary_forced" for s in d["steps"])


def test_force_secondary_disagree_is_not_auto_passed(tmp_path, monkeypatch):
    az = Az(("Ottoni and colleagues LITHA a study.", None))
    d = run(CANON, CANON, _wav(tmp_path), az, monkeypatch, force_secondary=True)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_BOTH


# ---------------- COST_GUARD ----------------
def test_cost_guard_applies_actual_seconds_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "_wav_duration_seconds", lambda p: 181.0)      # $1/h換算で$0.0503 > $0.05
    az = Az((CANON, None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch)
    assert az.calls == 0 and d["cost_guard_triggered"] is True and d["verified"] is False
    assert d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE
    assert uj.COST_GUARD_IN_UNIFIED_JUDGE.startswith("APPLIED_AT_ADAPTER")


def test_cost_guard_not_triggered_for_normal_clip(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "_wav_duration_seconds", lambda p: 60.0)
    az = Az((CANON, None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch)
    assert az.calls == 1 and d["cost_guard_triggered"] is False and d["verified"] is True


# ---------------- 最後のslotだけHR queue ----------------
def test_human_review_only_on_last_slot(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)   # Ledger research(cost logger要)はmock
    az = Az(("Something entirely different was said here today.", None))
    d = run(CANON, PRIMARY_NG, _wav(tmp_path), az, monkeypatch, attempt_ctx={"is_last_slot": False})
    assert d["human_review_required"] is False
    d = run(CANON, PRIMARY_NG, _wav(tmp_path, "b.wav", fill=b"\x01"), az, monkeypatch, attempt_ctx={"is_last_slot": True})
    assert d["human_review_required"] is True and d["verified"] is False


def test_lr_rewritten_warning_when_script_v1(tmp_path, monkeypatch):
    d = run(CANON, CANON, _wav(tmp_path), Az(), monkeypatch, attempt_ctx={"script_version": "v1"})
    assert d["verified"] is True and d["asr_judgement"]["state"] == uj.PASS_WITH_WARNING and uj.W_LR_REWRITTEN in d["asr_judgement"]["warnings"]


# ---------------- _is_number マーカー拡張 ----------------
@pytest.mark.parametrize("tok,expected", [("25xpercentx", True), ("5xdollarx", True), ("3xdecimalpointx5", True),
                                          ("10xexpnegx16", True), ("25", True), ("28th", False), ("abc", False), ("xpercentx", False)])
def test_is_number_marker_tokens(tok, expected):
    assert val._is_number(tok) is expected


def test_is_number_extension_keeps_equal_value_passes():
    for a, b in [("The rate is 25% today.", "The rate is 25 percent today."), ("It costs $5.", "It costs 5 dollars."),
                 ("It grew 2.5 times.", "It grew 2 point 5 times.")]:
        assert val.classify_asr_match(a, b).should_pass, (a, b)
    for a, b in [("The rate is 25% today.", "The rate is 26% today."), ("It costs $5.", "It costs 5."), ("It grew 2.5 times.", "It grew 2.6 times.")]:
        assert not val.classify_asr_match(a, b).should_pass, (a, b)


# ---------------- end-to-end(mock): Primary NG + Secondary PASS -> 最終成果物でPASS_WITH_WARNING + 試聴リスト ----------------
def test_e2e_leaf_to_listening_list_and_page_section(tmp_path, monkeypatch):
    import numpy as np
    import er003_v1_sing01_news_tail_fix as ntf
    narration = tmp_path / "wiring_theme_auw3" / "b1b" / "narration"
    narration.mkdir(parents=True)
    out_path = str(narration / "full_story_part1.wav").replace("\\", "/")
    monkeypatch.setattr(ntf.common, "_call_tts_with_retry", lambda call_fn, prompt, max_retry=None, sleep_fn=None:
                        (np.zeros(4000, dtype=np.int16).tobytes(), 0, True, None))
    monkeypatch.setattr(ntf.p3u, "trim_english_keyword_silence", lambda samples, sr, safety_margin_seconds=None:
                        (np.zeros(sr, dtype=np.float32), {"raw_duration_seconds": 1.0}))
    monkeypatch.setattr(ntf.safety, "detect_duration_anomaly", lambda *a, **k: {"is_anomaly": False})
    monkeypatch.setattr(ntf.routing, "transcribe", lambda *a, **k: (PRIMARY_NG, None))     # Primary NG
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((CANON, None)))   # Secondary PASS
    result = ntf.generate_news_narration_wide_margin(CANON, out_path, max_attempts=3)
    # 最終成果物: 採用(status OK)され、asr_judgementがPASS_WITH_WARNINGで残る
    assert result["status"] == "OK" and result["asr_verified"] is True
    assert result["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    assert result["attempts_log"][-1]["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    # 生成完了hook(registry)で試聴リストへ
    run_dir = tmp_path / "wiring_theme_auw3" / "b1b"
    (run_dir / "audit").mkdir(exist_ok=True)
    (run_dir / "audit" / "tts_generation_results.json").write_text(
        json.dumps({"segments": {"full_story_part1": dict(result, sha256="abc", language="en")}}, ensure_ascii=False, default=str), encoding="utf-8")
    rep = reg.write_listening_list_safe(str(run_dir), standalone_html=True)
    assert rep["error"] is None and rep["count"] == 1
    lst = json.load(open(rep["json"], encoding="utf-8"))["entries"][0]
    assert lst["segment_id"] == "full_story_part1" and uj.W_SECONDARY_CONFIRMED in lst["warning_labels"]
    assert lst["primary_text"] == PRIMARY_NG and lst["secondary_text"] == CANON
    page = open(rep["html"], encoding="utf-8").read()
    assert "事後試聴リスト(PASS_WITH_WARNING)" in page and "full_story_part1" in page and "SECONDARY_CONFIRMED" in page


# ---------------- registry ----------------
def test_registry_value_guard_kind_in_entries():
    j = {"state": "PASS_WITH_WARNING", "warnings": ["NUMERIC_AMBIGUOUS_SURFACE"], "reason_code": "x", "primary": {"text": "p"},
         "secondary": {"text": "s"}, "value_guard": {"primary": {"kind": "AMBIGUOUS"}, "secondary": {"kind": "EQUAL"}}}
    es = reg.derive_listening_list({"segments": {"a": {"status": "OK", "text": "t", "path": "a.mp3", "sha256": "z", "asr_judgement": j}}})
    assert es[0]["value_guard_kind_primary"] == "AMBIGUOUS" and es[0]["value_guard_kind_secondary"] == "EQUAL"
    assert "AMBIGUOUS/EQUAL" in reg.render_html_section(es)


def test_registry_safe_never_raises_on_broken_results(tmp_path, capsys):
    run = tmp_path / "r"
    (run / "audit").mkdir(parents=True)
    (run / "audit" / "tts_generation_results.json").write_text("{broken", encoding="utf-8")
    rep = reg.write_listening_list_safe(str(run))
    assert rep["error"] and rep["json"] is None
    assert "WARN" in capsys.readouterr().err


def test_section_zero_and_n_entries():
    sec0 = reg.render_html_section([])
    assert "事後試聴リスト(PASS_WITH_WARNING)" in sec0 and "0件" in sec0 and reg.SECTION_ID in sec0     # 0件でも節を省略しない
    es = [{"segment_id": f"s{i}", "entry_key": f"s{i}", "role": "r", "warning_labels": ["SECONDARY_CONFIRMED"], "audio_path": f"a{i}.mp3",
           "canonical_text": "c", "primary_text": "p", "secondary_text": "s", "reason": "x", "inherited": False} for i in range(3)]
    secn = reg.render_html_section(es, href_fn=lambda e: "audio/" + e["audio_path"])
    assert "3件" in secn and secn.count("<audio") == 3 and 'href="audio/a0.mp3"' in secn
    assert "<audio" not in reg.render_html_section(es, href_fn=lambda e: "")


def test_z_page_sections_zero_and_n(tmp_path):
    import er063_family_z_audio_01 as z
    rows = [{"part": "Preview", "start": 0.0, "dur": 1.0, "file": "audio_standard/a2_00.mp3", "voice": "v", "style": "s", "script": "x", "notes": []}]
    h0 = z.build_listening_page_html("Standard", rows, [], "audio_standard/full.mp3", 1.0, warn_section_html=reg.render_html_section([]))
    assert "0件" in h0 and not any(z.lint_page_html(h0).values())
    es = [{"segment_id": "preview", "entry_key": "preview", "role": "preview", "warning_labels": ["SECONDARY_CONFIRMED"], "audio_path": "x",
           "canonical_text": "c", "primary_text": "p", "secondary_text": "s", "reason": "r", "inherited": False}]
    h1 = z.build_listening_page_html("Standard", rows, [], "audio_standard/full.mp3", 1.0,
                                     warn_section_html=reg.render_html_section(es, href_fn=lambda e: "audio_standard/a2_00.mp3"))
    assert "1件" in h1 and "SECONDARY_CONFIRMED" in h1 and not any(z.lint_page_html(h1).values())
    assert "事後試聴リスト" not in z.build_listening_page_html("Standard", rows, [], "audio_standard/full.mp3", 1.0)   # 既存呼出は無変更


# ---------------- Z/X/legacy: asr_judgementの引継ぎ・継承 ----------------
def test_z_build_entry_carries_asr_judgement_and_reuse_marks_inherited(tmp_path):
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec(clip_id="full_story_part1_c1", level="b1b", kind="narrator", text="Melos called.", voice="Aoede",
                      role_key=z.role_key_for("narrator", "b1b"))
    narr = tmp_path / "run" / "b1b" / "narration"
    narr.mkdir(parents=True)
    out = str(narr / spec.wav_name()).replace("\\", "/")
    open(out, "wb").write(b"RIFFxxxx")
    j = {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CONFIRMED"], "primary": {"text": "p"}, "secondary": {"text": "s"}}
    entry = z.build_entry(spec, out, {"status": "OK", "asr_judgement": j})
    assert entry["asr_judgement"] == j
    entry["reuse_key"] = z.build_reuse_key(spec)
    reused = z.generate_or_reuse_z(dict(entry, sha256=None), spec, out, lambda: pytest.fail("再生成されないはず"))
    assert reused["reused_from_previous_run"] is True and "asr_judgement" not in reused and reused["asr_judgement_inherited"] == j
    es = reg.derive_listening_list({"segments": {"c1": reused}})
    assert len(es) == 1 and es[0]["inherited"] is True


def test_x_reuse_moves_asr_judgement_to_inherited():
    import er019_family_x_audio_production_runner_01 as x
    d = {"status": "OK", "asr_judgement": {"state": "PASS_WITH_WARNING"}}
    x._mark_asr_judgement_inherited(d)
    assert "asr_judgement" not in d and d["asr_judgement_inherited"]["state"] == "PASS_WITH_WARNING"
    x._mark_asr_judgement_inherited(d)      # 冪等(2回目は何もしない)
    assert d["asr_judgement_inherited"]["state"] == "PASS_WITH_WARNING"


def test_master_store_roundtrip_keeps_asr_judgement_as_inherited(tmp_path, monkeypatch):
    import er006_master_audio_store_01 as store
    monkeypatch.setattr(store, "AUDIO_DIR", str(tmp_path / "audio"))
    monkeypatch.setattr(store, "MANIFEST_PATH", str(tmp_path / "manifest.json"), raising=False)
    mem = {}
    monkeypatch.setattr(store, "_load_manifest", lambda: dict(mem))
    monkeypatch.setattr(store, "_save_manifest", lambda m: mem.update(m))
    monkeypatch.setattr(store, "_log_telemetry", lambda *a, **k: None)
    k = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id="m", canonical_text="Hello there.")
    j = {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CONFIRMED"]}
    out1 = str(tmp_path / "o1.wav")

    def gen(path):
        open(path, "wb").write(b"RIFFdata")
        return {"status": "OK", "path": path, "sha256": "s", "asr_verified": True, "asr_judgement": j}
    r1 = store.get_or_generate(k, out1, gen)
    assert r1.get("asr_judgement") == j
    r2 = store.get_or_generate(k, str(tmp_path / "o2.wav"), lambda p: pytest.fail("再生成されないはず"))
    assert r2["reused"] is True and r2["asr_judgement_inherited"] == j


def test_post_slowdown_rescue_replaces_final_asr_judgement(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as tg
    from unittest import mock
    j_final = {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CORROBORATED"], "primary": {"text": "Mellos called."}, "secondary": {"text": "Melos called."}}
    detail = {"verified": True, "classification": None, "cascade_invoked": True, "final_status": "SECONDARY_ASR_CORROBORATED_MATCH",
              "steps": [], "asr_judgement": j_final}
    result = {"asr_judgement": {"state": "PASS", "warnings": []}}
    cls = type("C", (), {"classification": "ASR_VALIDATION_UNCERTAIN"})()
    with mock.patch.object(tg.secondary_asr, "evaluate_attempt_with_cascade_detail", return_value=detail), \
         mock.patch("er006_pronunciation_ledger_01.get_hint_for_text", return_value=[]):
        ok = tg._post_slowdown_cascade_rescue(result, "Melos called.", "Mellos called.", cls, str(tmp_path / "a.wav"), "full_story_part1")
    assert ok is True and result["asr_judgement"] == j_final and result["asr_judgement_pre_slowdown"]["state"] == "PASS"


# ---------------- 統合で判明した偽否定の是正(承認済みcontraction等価を最終ANDゲートが再否定しない) ----------------
@pytest.mark.parametrize("canon,asr", [
    ("The client cannot access the shared folder from home.", "The client can't access the shared folder from home."),
    ("We do not go there today.", "We don't go there today."),
    ("He will not go there today.", "He won't go there today."),
    ("It is not here today.", "It isn't here today."),
    ("We cannot go there today.", "We can not go there today."),
])
def test_approved_contraction_equivalence_is_not_rejected_by_negation_gate(tmp_path, monkeypatch, canon, asr):
    az = Az(("never", None))
    d = run(canon, asr, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is True and az.calls == 0, (canon, asr, d["asr_judgement"]["state"], d["asr_judgement"]["reason_code"])
    assert d["asr_judgement"]["state"] == uj.PASS


@pytest.mark.parametrize("canon,asr", [
    ("We can go there today.", "We can't go there today."),
    ("It is here today.", "It isn't here today."),
    ("We do not go there today.", "We do go there today."),
])
def test_negation_reversal_is_still_protected(tmp_path, monkeypatch, canon, asr):
    az = Az((canon, None))
    d = run(canon, asr, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED
