# -*- coding: utf-8 -*-
"""JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: 配線test(adapter / retry loop / Master Audio Store・継承 / registry・完了ブロック / Y試聴ページ / hook)。
API 0(Azure=注入、ASR=転写文字列を直接渡す、socket guard、Reading Resolver無効)。TEST_PLAN_01 の T-P1/T-A1/T-NB/T-S/T-RP と Opus M-4/R-6/R-8/R-9。
実行: .venv\\Scripts\\python.exe -m pytest er078_ja_v2beta_wiring_test_01.py -q"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import types
from unittest import mock

import pytest

import er078_ja_v2beta_test_support_01 as T

import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_ja_v2beta_01 as v2b
import er078_pass_with_warning_registry_01 as pww
import er078_reuse_value_guard_01 as rvg
import er109_xz_scope_01 as xz

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
# 月タイトル6音声の決定対(OpenAI=記録時転写, Azure=当該wav)。EVAL_UNIFIED_03.md §1a / 委任文のR-1 OFF構成の期待
MOON6 = [
    ("ms_03 a1", "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。", "NG", "p1_value_diff", None),
    ("ms_03 a2", "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", "月の詩は8900本超。その奥に潜む岩の上着の秘密。", "PASS_W", "primary_pass", "v2"),
    ("ms_03 a3", "月の氏は8000900本超。その奥に潜む岩の上着の秘密。", "杉野氏は8900本超。その奥に潜む岩の上着の秘密。", "PASS_W", "ja_beta_composite", "beta"),
    ("reselect a1", "月野氏は8,900本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。", "PASS_W", "primary_pass", "v2"),
    ("reselect a2", "月の詩は八千九百本超。その奥に潜む岩の上着の秘密", "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。", "PASS_W", "primary_pass", "v2"),
    ("reselect a3", "スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。", "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。", "NG", "secondary_not_accepted", None),
]


# ============================================================
# T-P1: 月6本 -> 4 PASS_W / 2 HR
# ============================================================
@pytest.mark.parametrize("name,prim,az,verdict,reason,basis", MOON6)
def test_t_p1_moon_six_draws_four_pass_w_two_hr(name, prim, az, verdict, reason, basis):
    r, azc = T.judge(MOON, prim, az, attempt_ctx={"max_len": 400, "is_last_slot": True})
    j = T.aj(r)
    assert j["judge_rule_version"] == v2b.JUDGE_RULE_VERSION
    if verdict == "PASS_W":
        assert j["state"] == uj.PASS_WITH_WARNING and j["verdict"] == "PASS_W" and j["reason_code"] == reason and j["rescue_basis"] == basis, (name, j["reason_code"])
        assert r["verified"] is True and r["human_review_required"] is False
        assert any(w.startswith("JA_NEWLAYER_") for w in j["warnings"])
        assert j["rescue_reason_ja"]
    else:
        assert j["state"] not in uj.PASSING_STATES and j["reason_code"].startswith(reason), (name, j["reason_code"])
        assert r["verified"] is False and r["human_review_required"] is True and j["verdict"] == "HR" and j["rescue_basis"] is None
    if basis == "beta":
        # a3: Secondary(Azure)='杉野氏' の読み相違あり -> 証拠が最も弱いPASS_W。警告に残る(試聴は推奨・任意)
        assert v2b.W_SECONDARY_READING_CONFLICT in j["warnings"] and v2b.W_LISTEN_ADVISED in j["warnings"]
        assert j["ja_v2beta"]["weak_rank"] == 0


def test_t_p1_beta_asset_keeps_secondary_text_for_rejudge():
    r, _ = T.judge(MOON, MOON6[2][1], MOON6[2][2])
    j = T.aj(r)
    assert j["secondary"]["text"] == MOON6[2][2] and j["primary"]["text"] == MOON6[2][1]       # M-4: 採用転写(Secondary)の保存
    b = j["ja_v2beta"]["beta"]
    assert b["secondary_transcript"] == MOON6[2][2] and b["secondary_wav_sha256"] and b["secondary_engine"] == "azure" and b["phrase_list_hash"] == ""


# ============================================================
# T-A1: scope外 byte同一(配線前HEAD金型)
# ============================================================
GOLDEN_SHA_SCOPE_NONE_HEAD = "9c0f740fe0a6b41ad3e912275728d346b044052b295e8d21789dfce084ecbc82"


def test_t_a1_scope_none_output_is_byte_identical_to_head_golden(tmp_path):
    """配線前HEAD(8368add34)で同じtoolを実行した396判定(月6本+コーパス抽出×2ctx)の出力sha256と、現行コードのscope外出力が一致する。"""
    tool = os.path.join(ROOT, "docs", "research", "JA-ASR-V2-BETA-PRODUCTION-WIRING-01", "tools", "gen_golden_scope_none_01.py")
    out = tmp_path / "now.json"
    r = subprocess.run([PY, "-X", "utf8", tool, str(out)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=280,
                       env=dict(os.environ, PYTHONUTF8="1"))
    assert r.returncode == 0, r.stderr[-500:]
    assert f"sha256 {GOLDEN_SHA_SCOPE_NONE_HEAD}" in r.stdout, r.stdout[-300:]


# ============================================================
# T-NB1: PASS_Wは非ブロッキング(adapter / wrapper)
# ============================================================
def test_t_nb1_pass_w_is_non_blocking_in_adapter_and_wrapper(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(sec, "_log_human_review", lambda d: called.__setitem__("n", called["n"] + 1))
    wav = T.make_wav("nb1")
    detail = {}
    with T.api0(), xz.run_scope("X"):
        ok, stop, cls = sec.evaluate_attempt_ja_with_cascade(
            "今日の売上は1,200円でした。", "今日の売上わ1200円でした。", wav, cascade_enabled=True,
            attempt_ctx={"max_len": 400, "is_last_slot": True}, detail_out=detail)
    assert ok is True and stop is False and called["n"] == 0
    assert detail["human_review_required"] is False and T.aj(detail)["verdict"] == "PASS_W"
    # 通常NG(新層の対象外)は従来どおり最終slotでHR queueへ
    with T.api0(), xz.run_scope("X"):
        ok2, stop2, cls2 = sec.evaluate_attempt_ja_with_cascade(
            "今日の売上は1,200円でした。", "今日の売上は1,300円でした。", wav, cascade_enabled=True, attempt_ctx={"max_len": 400, "is_last_slot": True})
    assert ok2 is False and called["n"] == 1


def _drive_generate_charon_japanese(asr_texts, max_attempts=3):
    """実adapter(X scope内)で generate_charon_japanese の再生成loopを駆動(TTS/ASR転写はmock)。"""
    import numpy as np
    import er003_v1_sing01_voice01_generate as voice01
    dummy_trim = {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}
    with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
         mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
         mock.patch.object(voice01.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)) as mock_tts, \
         mock.patch.object(voice01.common, "pcm_bytes_to_float_mono", return_value=np.zeros(100, dtype=np.float32)), \
         mock.patch.object(voice01.p3u, "trim_english_keyword_silence", return_value=(np.zeros(100, dtype=np.float32), dict(dummy_trim))), \
         mock.patch.object(voice01.safety, "detect_duration_anomaly", return_value={"is_anomaly": False}), \
         mock.patch.object(voice01.common, "write_wav_float", return_value=None), \
         mock.patch.object(voice01.common, "measure_metrics", return_value={"clipping_detected": False}), \
         mock.patch.object(voice01.routing, "transcribe", side_effect=[(t, None) for t in asr_texts]), \
         mock.patch.object(sec, "_azure_stt_strict", return_value=(None, "api0_stub_no_secondary")):
        with T.api0(), xz.run_scope("X"):
            result = voice01.generate_charon_japanese("今日の売上は1,200円でした。", "dummy_out_v2beta.wav", "今日", max_attempts=max_attempts)
    return mock_tts, result


def test_t_nb2_retry_loop_ends_at_first_pass_w_attempt():
    mock_tts, result = _drive_generate_charon_japanese(["今日の売上わ1200円でした。"])
    assert mock_tts.call_count == 1 and result["status"] == "OK" and result["asr_verified"] is True
    assert result["asr_judgement"]["verdict"] == "PASS_W" and result["asr_judgement"]["rescue_basis"] == "v2"


def test_t_nb2_ng_then_pass_w_ends_at_second_attempt():
    mock_tts, result = _drive_generate_charon_japanese(["今日の売上は1,300円でした。", "今日の売上わ1200円でした。"])
    assert mock_tts.call_count == 2 and result["status"] == "OK" and result["asr_verified"] is True
    # (通算上限3回・NG終端の挙動は既存 er007_ja_tts_retry_path_fix_test_01 / er127 test が固定。PASS_W導入で不変)


# ============================================================
# Master Audio Store・継承・resume (T-S1〜S4 / Opus M-4)
# ============================================================
def _entry(canon, primary, azure, **kw):
    r, _ = T.judge(canon, primary, azure, **kw)
    assert T.aj(r)["state"] in uj.PASSING_STATES, (canon, primary)
    return {"asr_judgement": copy.deepcopy(T.aj(r)), "asr_text": primary, "text": canon, "status": "OK"}


V2_CASE = ("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None)
BETA_CASE = ("参加者は5,300人でした。", "参加者は5000300人でした。", "参加者は5300人でした。")
SEC_V2_CASE = ("今日の売上は1,200円でした。", "今日の運動は千二百円でした。", "今日の売上わ1200円でした。")


@pytest.mark.parametrize("case", [V2_CASE, BETA_CASE, SEC_V2_CASE], ids=["v2_primary", "beta", "v2_secondary"])
def test_m4_out_of_scope_and_flag_off_never_reuse_contributed_asset(case, monkeypatch):
    e = _entry(*case)
    assert v2b.contributed(e["asr_judgement"]) is True
    g = rvg.guard_entry(copy.deepcopy(e), canonical_text=case[0])                      # scope外(A/B/C・単体)
    assert g["blocked"] is True and g["reason"] == v2b.OUT_OF_SCOPE_BLOCK_REASON
    # 継承キー(asr_judgement_inherited)側だけに印があっても検出する
    e2 = {"asr_judgement_inherited": e["asr_judgement"], "asr_text": e["asr_text"], "text": e["text"]}
    assert rvg.guard_entry(e2, canonical_text=case[0])["blocked"] is True
    # KP voteゲートが後続する呼出でもskipされない(配置がkp_vote_gate_followsより前)
    assert rvg.guard_entry(copy.deepcopy(e), canonical_text=case[0], kp_vote_gate_follows=True)["blocked"] is True
    # scope内でもflag定数OFFなら再生成
    monkeypatch.setattr(v2b, "JA_V2_BETA_ENABLED", False)
    with xz.run_scope("X"):
        g2 = rvg.guard_entry(copy.deepcopy(e), canonical_text=case[0])
    assert g2["blocked"] is True and g2["reason"] == v2b.OUT_OF_SCOPE_BLOCK_REASON


@pytest.mark.parametrize("case", [V2_CASE, BETA_CASE, SEC_V2_CASE], ids=["v2_primary", "beta", "v2_secondary"])
def test_m4_in_scope_same_version_trusts_saved_judgement_without_rejudge(case, monkeypatch):
    e = _entry(*case)
    monkeypatch.setattr(v2b, "rejudge_contributed", lambda *a, **k: (_ for _ in ()).throw(AssertionError("版一致なら再判定しない")))
    with T.api0(), xz.run_scope("X"):
        g = rvg.guard_entry(copy.deepcopy(e), canonical_text=case[0])
    assert g["blocked"] is False and g["secondary_new_calls"] == 0 and g["api_calls"] == 0


@pytest.mark.parametrize("case", [V2_CASE, BETA_CASE, SEC_V2_CASE], ids=["v2_primary", "beta", "v2_secondary"])
def test_m4_version_mismatch_rejudges_api0_without_resolver_and_keeps_valid_asset(case):
    e = _entry(*case)
    e["asr_judgement"]["judge_rule_version"] = "ja_v2beta_OLD"
    seen = []
    real = sec.javal.classify_ja_asr_match

    def spy(*a, **k):
        seen.append(dict(k))
        return real(*a, **k)
    with mock.patch.object(sec.javal, "classify_ja_asr_match", spy), T.api0(), xz.run_scope("X"):
        ok, why = v2b.rejudge_contributed(e["asr_judgement"])
        g = rvg.guard_entry(copy.deepcopy(e), canonical_text=case[0])
    assert ok is True and why == "REJUDGE_OK" and g["blocked"] is False
    assert seen and all(k.get("allow_reading_resolver") is False for k in seen), "再判定はReading Resolver(LLM)を使わない"


def test_m4_version_mismatch_with_changed_rule_or_missing_provenance_blocks_regeneration():
    e = _entry(*BETA_CASE)
    e["asr_judgement"]["judge_rule_version"] = "ja_v2beta_OLD"
    bad = copy.deepcopy(e)
    bad["asr_judgement"]["secondary"]["text"] = "参加者は5400人でした。"       # Secondary値が原稿と違う -> βは現行規則で不成立
    with T.api0(), xz.run_scope("X"):
        g = rvg.guard_entry(bad, canonical_text=BETA_CASE[0])
    assert g["blocked"] is True and g["reason"].startswith("JA_V2BETA_REJUDGE_NG:beta_rejudge_ng")
    miss = copy.deepcopy(e)
    miss["asr_judgement"]["secondary"]["text"] = None                          # 採用転写(Secondary)の保存が欠ける -> fail-closed
    with T.api0(), xz.run_scope("X"):
        g2 = rvg.guard_entry(miss, canonical_text=BETA_CASE[0])
    assert g2["blocked"] is True and "provenance_missing" in g2["reason"]
    e3 = _entry(*V2_CASE)
    e3["asr_judgement"]["judge_rule_version"] = "ja_v2beta_OLD"
    e3["asr_judgement"]["primary"]["text"] = "今日の売上わ1300円でした。"           # 値が変わった保存転写 -> v2不成立
    with T.api0(), xz.run_scope("X"):
        g3 = rvg.guard_entry(e3, canonical_text=V2_CASE[0])
    assert g3["blocked"] is True


def test_m4_entries_without_the_new_mark_are_untouched_and_do_not_import_the_new_module():
    code = ("import sys\nimport er078_reuse_value_guard_01 as g\n"
            "e={'asr_judgement': {'state':'PASS_WITH_WARNING','warnings':['SECONDARY_CONFIRMED'],'primary':{'text':'x'}}, 'asr_text':'', 'text':'売上は100円です。'}\n"
            "r=g.guard_entry(e, canonical_text='売上は100円です。')\n"
            "assert 'er078_ja_v2beta_01' not in sys.modules, 'marker無しentryで新moduleをimportした'\nprint('OK', r['reason'])\n")
    out = subprocess.run([PY, "-c", code], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert out.returncode == 0 and "OK" in out.stdout, out.stderr[-500:]


@pytest.mark.parametrize("case", [V2_CASE, BETA_CASE], ids=["v2_primary", "beta"])
def test_t_s4_j11_inheritance_keeps_rescue_basis_and_passes_final_gate(case):
    import er019_family_x_validation_inheritance_01 as vi
    e = _entry(*case)
    with T.api0(), xz.run_scope("X"):
        rj = vi.rejudge_with_current_judge(copy.deepcopy(e), "a2", "japanese_title", force_lang="ja")
    assert rj["ok"] is True and rj["secondary_new_calls"] == 0
    inh = rj.get("asr_judgement_inherited")
    assert inh and inh["rescue_basis"] == e["asr_judgement"]["rescue_basis"] and inh["state"] == uj.PASS_WITH_WARNING and inh["warnings"] == e["asr_judgement"]["warnings"]
    # 値が違う採用転写では継承できない
    badj = copy.deepcopy(e)
    tgt = "primary" if case is V2_CASE else "secondary"
    badj["asr_judgement"][tgt]["text"] = badj["asr_judgement"][tgt]["text"].replace("1200", "1300").replace("5300", "5400")
    if case is V2_CASE:
        badj["asr_text"] = badj["asr_judgement"]["primary"]["text"]
    with T.api0(), xz.run_scope("X"):
        rj2 = vi.rejudge_with_current_judge(badj, "a2", "japanese_title", force_lang="ja")
    assert rj2["ok"] is False


def test_t_s1_registry_lists_inherited_pass_w_new_method_entry():
    e = _entry(*BETA_CASE)
    res = {"segments": {"japanese_title": {"status": "OK", "path": "a.wav", "sha256": "s1", "text": BETA_CASE[0], "asr_judgement_inherited": e["asr_judgement"]}}}
    ents = pww.derive_listening_list(res)
    assert len(ents) == 1 and ents[0]["inherited"] is True and ents[0]["rescue_basis"] == "beta" and ents[0]["verdict"] == "PASS_W"


# ============================================================
# registry / 完了ブロック / run単位JSON (T-RP1〜RP3, R-6, R-8)
# ============================================================
def _results_with_new_method(tmp_path):
    wavs = {}
    segs = {}
    cases = {"japanese_title": MOON6[2], "preview": MOON6[1], "comment_1": ("x", MOON, "今日の売上は1,200円でした。", "今日の売上わ1200円でした。")}
    # β(Secondary読み相違あり=最弱) / v2 / 通常のPASS_WITH_WARNING(旧方式)
    r_beta, _ = T.judge(MOON, MOON6[2][1], MOON6[2][2])
    r_v2, _ = T.judge("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None)
    r_old, _ = T.judge("売上は100円です。", "売り上げは100円です。", "売上は100円です。", scope=None)
    segs["preview"] = {"status": "OK", "path": str(tmp_path / "preview.wav"), "sha256": "sha_v2", "text": "今日の売上は1,200円でした。", "asr_judgement": T.aj(r_v2)}
    segs["japanese_title"] = {"status": "OK", "path": str(tmp_path / "title.wav"), "sha256": "sha_beta", "text": MOON, "asr_judgement": T.aj(r_beta)}
    segs["comment_1"] = {"status": "OK", "path": str(tmp_path / "c1.wav"), "sha256": "sha_old", "text": "売上は100円です。", "asr_judgement": T.aj(r_old)}
    return {"segments": segs}


def test_t_rp1_listing_has_all_required_fields_and_orders_weakest_first(tmp_path):
    res = _results_with_new_method(tmp_path)
    ents = pww.derive_listening_list(res)
    new = [e for e in ents if e.get("rescue_basis")]
    assert [e["segment_id"] for e in new] == ["japanese_title", "preview"]                           # R-6: 読み相違あり(β) が v2 より先頭
    assert [e["segment_id"] for e in ents][:2] == ["japanese_title", "preview"]
    b = new[0]
    for k in ("verdict", "rescue_basis", "rescue_reason_ja", "warning_labels", "canonical_text", "primary_text", "secondary_text", "audio_path", "adopted_sha256",
              "judge_rule_version", "weak_rank", "secondary_reading_conflict", "listen_advised"):
        assert k in b, k
    assert b["verdict"] == "PASS_W" and b["weak_rank"] == 0 and b["secondary_reading_conflict"] is True and b["listen_advised"] is True
    assert all(("rescue_basis" not in e) for e in ents if e["segment_id"] == "comment_1" and "judge_rule_version" not in e)
    s = pww.summarize_entries(ents)
    assert s["count_by_rescue_basis"] == {"beta": 1, "v2": 1} and s["secondary_reading_conflict_count"] == 1 and s["new_method_total"] == 2


def test_t_rp1_run_json_has_summary_and_health_only_when_ja_records_exist(tmp_path):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    json.dump(_results_with_new_method(tmp_path), open(run / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    p = pww.write_listening_list(str(run))
    data = json.load(open(p, encoding="utf-8"))
    sm = data["ja_v2beta_summary"]
    assert sm["count_by_rescue_basis"] == {"beta": 1, "v2": 1} and sm["health"]["attempt_records"] >= 2 and sm["health"]["errors"] == 0
    # scope外のみのresults(旧record)にはキー自体を作らない=従来と同一
    run2 = tmp_path / "run2"
    (run2 / "audit").mkdir(parents=True)
    r_old, _ = T.judge("売上は100円です。", "売り上げは100円です。", "売上は100円です。", scope=None)
    json.dump({"segments": {"x": {"status": "OK", "path": "x.wav", "sha256": "s", "text": "売上は100円です。", "asr_judgement": T.aj(r_old)}}},
              open(run2 / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    d2 = json.load(open(pww.write_listening_list(str(run2)), encoding="utf-8"))
    assert set(d2) == {"source", "count", "entries"}


def test_t_rp2_html_section_adds_columns_only_when_new_method_present(tmp_path):
    ents = pww.derive_listening_list(_results_with_new_method(tmp_path))
    html = pww.render_html_section(ents)
    assert "<th>新方式</th><th>救済理由</th>" in html and "試聴は推奨(任意)であり、制作・組立・納品候補作成は止めません" in html and "beta" in html
    old_only = [e for e in ents if not e.get("rescue_basis")]
    html_old = pww.render_html_section(old_only)
    assert "<th>新方式</th>" not in html_old and "新方式" not in html_old
    assert "0件(該当なし" in pww.render_html_section([])
    assert "導出失敗(要確認)" in pww.render_html_section(pww.ListeningListDerivationFailed("r", "err"))


def test_t_rp3_completion_block_text_hr_from_queue_and_lock_not_verdict(tmp_path, monkeypatch, capsys):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    json.dump(_results_with_new_method(tmp_path), open(run / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"title_lock": {"state": "HUMAN_REVIEW_REQUIRED", "segment_id": "title_lock", "language": "ja", "reason": "3回NG", "wav_path": str(run / "n.wav")},
               "ok_seg": {"state": "RESOLVED", "segment_id": "ok_seg"}}, open(run / "audit" / "review_lock_state.json", "w", encoding="utf-8"))
    q = tmp_path / "q.jsonl"
    q.write_text(json.dumps({"wav_path": str(run / "narration" / "q1.wav"), "canonical_text": "原稿", "final_status": "TRUE_CONTENT_MISMATCH", "timestamp": "t"}, ensure_ascii=False) + "\n"
                 + json.dumps({"wav_path": str(tmp_path / "other_run" / "z.wav"), "canonical_text": "他", "final_status": "x"}, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH_JA", str(q))
    rep = pww.emit_completion_block(str(run), "Family X a2(Standard)")
    out = capsys.readouterr().out
    assert rep["error"] is None and rep["json"] and os.path.exists(rep["json"])
    assert "【日本語ASR PASS_W(新方式)】Family X a2(Standard)" in out and "新方式(v2/β)のPASS_W: 2件" in out
    assert "title.wav" in out and "発生理由" in out and "JA_NEWLAYER_BETA_COMPOSITE" in out and "Secondary読み相違あり 1" in out
    assert out.index("読み相違あり(証拠が最も弱い)") < out.index("[v2/")                                   # 弱い順に先頭
    assert "要Human Review(HR Lock登録 1件 / JA HR queue行 1件): title_lock" in out
    assert "無効化(エラーで従来判定へ戻った)件数 0" in out
    data = json.load(open(rep["json"], encoding="utf-8"))
    assert data["hr"]["lock"][0]["segment_id"] == "title_lock" and len(data["hr"]["queue"]) == 1 and data["summary"]["new_method_total"] == 2


def test_m5_completion_block_counts_disabled_attempts_and_zero_case(tmp_path, capsys):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    r_err, _ = T.judge("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None)
    aj_err = copy.deepcopy(T.aj(r_err))
    aj_err["ja_v2beta"] = {"active": False, "scope": "X", "error": "begin:ImportError: No module named 'jaconv'"}
    for k in ("verdict", "rescue_basis", "judge_rule_version", "rescue_reason_ja"):
        aj_err.pop(k, None)
    json.dump({"segments": {"t": {"status": "OK", "path": "t.wav", "sha256": "e", "text": "x", "asr_judgement": {"state": "NG_BOTH"},
                                  "attempts_log": [{"attempt": 1, "asr_judgement": aj_err}]}}},
              open(run / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    pww.emit_completion_block(str(run), "Family Y a2(Standard)")
    out = capsys.readouterr().out
    assert "0件(該当なし)" in out and "無効化(エラーで従来判定へ戻った)件数 1" in out and "jaconv" in out


def test_completion_block_failure_never_raises(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pww, "collect_hr_items", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    rep = pww.emit_completion_block(str(tmp_path / "nonexistent"), "X")
    assert rep["error"] and "boom" in rep["error"]


def test_hook_prints_block_only_when_completion_label_is_given(tmp_path, capsys):
    run = tmp_path / "run"
    (run / "audit").mkdir(parents=True)
    json.dump(_results_with_new_method(tmp_path), open(run / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    rep0 = pww.write_listening_list_safe(str(run))
    assert "completion_block" not in rep0 and capsys.readouterr().out == ""
    rep1 = pww.write_listening_list_safe(str(run), completion_label="Family Z std")
    assert rep1["completion_block"]["error"] is None and "【日本語ASR PASS_W(新方式)】Family Z std" in capsys.readouterr().out


def test_hook_call_sites_for_x_y_z_pass_completion_label():
    pats = {"er019_family_x_audio_production_runner_01.py": 'completion_label="Family X a2(Standard)"',
            "er121_family_y_audio_01.py": "completion_label=(f\"Family Y {level}(Standard)\"",
            "er063_family_z_audio_01.py": 'completion_label=f"Family Z {level}"'}
    for f, needle in pats.items():
        assert needle in open(os.path.join(ROOT, f), encoding="utf-8").read(), f
    # A/B/C(legacy)のhookは従来どおり(completion_labelを渡さない)
    for f in ("er012_b_family_production_runner_01.py", "er013_family_c_production_runner_01.py", "er003_v1_n3_01_tts_generate.py"):
        assert "completion_label" not in open(os.path.join(ROOT, f), encoding="utf-8").read(), f


def test_y_listening_page_section_is_added_for_dev_only_and_lists_pass_w(tmp_path):
    import er121_family_y_runner_01 as yr
    import er_user_listening_page_common_01 as cp
    run_dir = tmp_path / "theme"
    (run_dir / yr.STD_LEVEL / "audit").mkdir(parents=True)
    pages = tmp_path / "pages"
    pages.mkdir()
    json.dump(_results_with_new_method(tmp_path), open(run_dir / yr.STD_LEVEL / "audit" / "tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    ctx = types.SimpleNamespace(out_dir=str(run_dir), pages_dir=str(pages))
    html_dev = yr._y_pww_aux_html(ctx, cp.AUDIENCE_DEV if hasattr(cp, "AUDIENCE_DEV") else "dev", cp)
    assert "pass-with-warning-listening-list" in html_dev and "title.wav" in html_dev and "新方式" in html_dev
    assert yr._y_pww_aux_html(ctx, cp.AUDIENCE_PUBLIC, cp) == ""
    # 導出失敗でもページ生成を失敗させない(節に『導出失敗(要確認)』)
    (run_dir / yr.STD_LEVEL / "audit" / "tts_generation_results.json").write_text("{broken", encoding="utf-8")
    assert "導出失敗(要確認)" in yr._y_pww_aux_html(ctx, "dev", cp)


# ============================================================
# R-9(c)(e): v2自身のA7/C2判定 / E0の書込み先
# ============================================================
def test_r9c_v2_blocks_on_registered_reading_mismatch_and_c2_homophone(monkeypatch):
    canon, asr = "今日の売上は1,200円でした。", "今日の売上わ1200円でした。"
    base, _ = T.judge(canon, asr, None)
    assert T.aj(base)["rescue_basis"] == "v2"
    # A7: 登録読み保護(Primaryが登録読み不一致を示した)ならv2は発火しない(Primary PASSにならず従来のNG経路=P2除外のまま)
    monkeypatch.setattr(sec, "_scg_reading_dict_reason", lambda cls: "reading_dictionary_mismatch:test")
    r, _ = T.judge(canon, asr, None)
    assert T.aj(r).get("rescue_basis") is None and T.aj(r)["state"] not in uj.PASSING_STATES and T.aj(r)["reason_code"].startswith("p2_exclusion:A7")
    monkeypatch.undo()
    # C2: 同形異音候補(順方向)ならv2の発音救済は発火しない。P2除外A4でSecondary不呼出のまま
    monkeypatch.setattr(sec, "_scg_c2_candidate", lambda cls: True)
    r2, az2 = T.judge(canon, asr, None)
    assert T.aj(r2).get("rescue_basis") is None and T.aj(r2)["state"] not in uj.PASSING_STATES and az2.calls == 0
    assert T.aj(r2)["reason_code"].startswith("p2_exclusion:A4")


def test_r9e_e0_runner_never_writes_to_production_results_store_or_human_approved():
    """E0/E1の実走script(docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/tools/runtime_evidence_01.py)は出力を一時out_dirに限り、
    Production results・Master Audio Store・HUMAN_APPROVED記録へのpathを一切参照しない(静的)。"""
    p = os.path.join(ROOT, "docs", "research", "JA-ASR-V2-BETA-PRODUCTION-WIRING-01", "tools", "runtime_evidence_01.py")
    if not os.path.exists(p):
        pytest.skip("runtime evidence script not created yet")
    src = open(p, encoding="utf-8").read()
    for banned in ("master_audio_store", "human_approved_segments", "record_human_approval", "HUMAN_REVIEW_LOG_PATH_JA ="):
        assert banned not in src, banned


def test_t_p3_offline_parity_with_frozen_proto_and_negative_increment_equals_known_eight_rows(tmp_path):
    """T-P3/T-R1/R-5: 凍結proto(proto_unified_03.judge, l1+l2, R-1 OFF)と全2103行一致、負例の誤PASS増分は既知8行(T1 6+T2 2)の行集合と同一、
    回帰(L0 PASS->NG)0、新層の例外0、Secondary側v2救済でE3/E4を持つ行0(R-4)。API 0(socket guard・Reading Resolver無効)。"""
    import json
    tool = os.path.join(ROOT, "docs", "research", "JA-ASR-V2-BETA-PRODUCTION-WIRING-01", "tools", "offline_recheck_01.py")
    corpus = os.path.join(ROOT, "docs", "research", "JA-ASR-FALSE-NG-ROOT-FIX-02", "eval_unified_03.out.json")
    if not (os.path.exists(tool) and os.path.exists(corpus)):
        pytest.skip("offline recheck tool / eval corpus missing")
    out = tmp_path / "recheck.json"
    env = dict(os.environ, PYTHONUTF8="1")
    cp = subprocess.run([sys.executable, "-X", "utf8", tool, str(out)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert cp.returncode == 0, cp.stderr[-2000:]
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["rows_compared"] == 2103
    assert d["parity_mismatch_count"] == 0, d["parity_mismatches"][:3]
    ident = d["neg_increment_identity_vs_known8"]
    assert ident["identical"] is True and d["neg_increment_count"] == 8 and not ident["unexpected_new_rows"], ident
    assert d["neg_regression_count"] == 0
    assert d["new_method_errors"] == {}
    assert d["r4_secondary_v2_rows_with_e3e4_in_cls_s"] == 0


def test_r6_health_scan_counts_one_attempt_once_even_when_recorded_in_entry_and_attempts_log():
    """採用entryのasr_judgementと attempts_log内の同一判定は二重計上しない。attempts_logに無い(引継ぎ/旧形式)entryは直下を数える。"""
    j = {"state": "PASS_WITH_WARNING", "judge_rule_version": v2b.JUDGE_RULE_VERSION, "ja_v2beta": {"active": True}}
    doc = {"segments": {"a": {"status": "OK", "asr_judgement": dict(j), "attempts_log": [{"attempt": 1, "asr_judgement": dict(j)}]},
                        "b": {"status": "OK", "asr_judgement_x": 1, "asr_judgement": dict(j)}}}
    h = pww.scan_v2beta_health(doc)
    assert h["attempt_records"] == 2 and h["active"] == 2, h      # a: attempts_log側1件 + b: 直下1件
