# LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_11(B-wire): 配線後のGate(X M3 / Y style gate / Z style gate)のmock E2E(API 0・費用JPY0)。
# 保存runを一時dirへ複製し(run dirは書き換えない)、LRあり/Fallbackあり/異常Style/記録欠落/parity不一致のmockで通過・停止が仕様どおりかを確認する。
# 仕様=ユーザー原文 UD-3: 正常なLR/Fallbackは組立停止・HR要求の理由にしない(警告記録)、異常/UNKNOWN/記録不一致/品質NG/overlap/parity不一致は従来どおり停止。
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
import types
from unittest import mock

import pytest

import er019_family_x_style_profile_01 as xsp
import er063_family_z_audio_01 as z
import er129_lr_display_reflection_01 as e129
import er130_adopted_take_classifier_01 as c130

ROOT = os.path.dirname(os.path.abspath(__file__))
AI = os.path.join(ROOT, "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01")
TTH = os.path.join(ROOT, "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01")
YTRU = os.path.join(ROOT, "er121_output")
PROFILE = "fx_20261017"
LRK = "full_story_part1_k2"


def _need(p):
    if not os.path.isdir(p):
        pytest.skip(f"saved run absent: {p}")


def _copy_level(src_level_dir, tmp):
    dst = os.path.join(tmp, os.path.basename(src_level_dir))
    shutil.copytree(src_level_dir, dst, ignore=shutil.ignore_patterns("narration", "assembled", "study_text", "key_phrases", "tts_block_progress"))
    return dst


def _results(level_dir):
    return json.load(open(os.path.join(level_dir, "audit", "tts_generation_results.json"), encoding="utf-8"))


def _save(level_dir, d):
    json.dump(d, open(os.path.join(level_dir, "audit", "tts_generation_results.json"), "w", encoding="utf-8"), ensure_ascii=False)


@pytest.fixture()
def tmp():
    d = tempfile.mkdtemp(prefix="er130_wire_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _x_gate(level, level_dir, results, *, wired=True):
    if wired:
        return xsp.m3_assembly_gate(PROFILE, level, results, {}, level_dir=level_dir)
    return xsp.m3_assembly_gate(PROFILE, level, results, {})


# ------------------------------------------------------------------ X M3
@pytest.mark.parametrize("lv", ["a2", "b1b"])
def test_x_normal_lr_passes_with_warning_and_does_not_require_hr(lv, tmp):
    _need(AI)
    ld = os.path.join(AI, lv)
    res = _results(ld)
    old = _x_gate(lv, ld, res, wired=False)
    new = _x_gate(lv, ld, res)
    assert any(b["segment"] == LRK and "LOCAL_REWRITE_RECOVERY" in b["violations"] for b in old["blocked"])     # 旧: 正常LRでも停止(HR要求)
    assert new["status"] == "PASS" and new["blocked"] == []                                                 # 新: 組立停止・HR要求なし
    assert {w["warning"] for w in new["warnings"] if w["segment"] == LRK} == {"LR_APPLIED"}                # 警告として記録


def test_x_abnormal_mocks_still_block(tmp):
    _need(AI)
    src = os.path.join(AI, "a2")
    base = _results(src)
    cases = {}
    # (1) LR 7 Gate/Natural English QAが偽(異常LR)
    d = _copy_level(src, tmp + "/c1")
    r = copy.deepcopy(base)
    r["segments"][LRK]["local_rewrite_recovery"]["selection"]["selected"]["adoptable"] = False
    _save(d, r)
    cases["lr_not_adoptable"] = (d, r)
    # (2) 記録欠落: 採用attemptを特定できない(attempt記録が参照できない)
    d = _copy_level(src, tmp + "/c2")
    r = copy.deepcopy(base)
    for k in ("attempts_log", "slowdown_attempts_log"):
        r["segments"][LRK].pop(k, None)
    r["segments"][LRK]["path"] = "nonexistent/dir/full_story_part1_k2.wav"
    r["segments"][LRK]["sha256"] = "0" * 64
    _save(d, r)
    cases["record_missing"] = (d, r)
    for name, (d, r) in cases.items():
        g = _x_gate("a2", d, r)
        assert g["status"] == "BLOCK", name
        assert any(b["segment"] == LRK for b in g["blocked"]), name
    # (3) parity不一致: 台帳の三者一致判定がSTOP_PARITYのclipはM3でもBLOCK(検出はassemble入口のer132 Gate、反応はここ。検出自体はer132 testで固定)
    clips = c130.event_ledger_clips(src)
    clips[LRK] = dict(clips[LRK], verdict=e129.V_PARITY)
    with mock.patch("er130_adopted_take_classifier_01.event_ledger_clips", return_value=clips):
        g = _x_gate("a2", src, base)
    assert g["status"] == "BLOCK" and any("TEXT_AUDIO_PARITY_MISMATCH" in b["violations"] for b in g["blocked"])


def test_x_run_without_events_is_unchanged_by_wiring():
    _need(AI)
    ld = os.path.join(AI, "a2")
    res = _results(ld)
    for seg in list(res["segments"]):                                       # イベント(LR/Fallback)の無いrun相当=LR記録を落とした複製
        res["segments"][seg].pop("local_rewrite_recovery", None)
    with mock.patch("er130_adopted_take_classifier_01.event_ledger_clips", return_value={}):    # 台帳にイベントなし
        a = xsp.m3_assembly_gate(PROFILE, "a2", res, {}, level_dir=ld)
    b = xsp.m3_assembly_gate(PROFILE, "a2", res, {})
    assert a == b                                                           # level_dir有無で結果が変わらない(イベントclipだけが置換対象)


# ------------------------------------------------------------------ Z style gate
def _z_spec(role, cid, level, kind=""):
    return types.SimpleNamespace(role_key=role, level=level, clip_id=cid, kind=kind, rank=None)


def _z_row(level_dir, entry, cid, role, kind, *, clips):
    import er003_b1_p9a_audio as p9a
    return z._z_row_for_clip(_z_spec(role, cid, "b1b", kind), entry, True, {}, z.style_prefix_sha256(p9a.ENGLISH_STYLE_PREFIX), clips)


def test_z_normal_fallback_english_lock_passes_with_warning_and_abnormal_mocks_block(tmp):
    _need(TTH)
    ld = os.path.join(TTH, "b1b")
    res = _results(ld)
    ent = res["key_phrases"]["2"]["english"]
    clips = c130.event_ledger_clips(ld)
    assert "kp2_en" in clips
    # 保存runの記録(旧同定のstyle_actual=role Style・採用はENGLISH_LOCK)でも、採用take分類核がFALLBACK_APPLIED(承認済みENGLISH_LOCK)と確定して通す(M-10)
    row = _z_row(ld, ent, "kp2_en", "KP_EN", "kp_en", clips=clips)
    assert row["violations"] == [] and [w["kind"] for w in row["lr_fallback_warnings"]] == ["FALLBACK_APPLIED"]
    assert row["lr_fallback_class"]["verdict"] == "PASS_WITH_WARNING"
    old = _z_row(ld, ent, "kp2_en", "KP_EN", "kp_en", clips=None)
    assert old["violations"] == []                                             # 旧Zは採用attemptを誤同定してPASSしていた(K2記録)。新=正しい採用takeで通す
    # (異常Style) 採用takeのStyleが承認Fallbackでない: ENGLISH_LOCKの検証済みattemptを外し、未承認Styleのattemptだけが採用扱いになる記録 -> 停止
    bad = copy.deepcopy(ent)
    bad["english_lock_attempts_log"] = []
    bad["attempts"] = [{"phase": "standard", "style_prefix_sha256": "1" * 64, "verified": False},
                       {"phase": "fallback", "style_prefix_sha256": "2" * 64, "instruction_type": "minimal_fallback", "verified": True}]
    clips_bad = copy.deepcopy(clips)
    clips_bad["kp2_en"]["adopted_take"] = dict(clips_bad["kp2_en"]["adopted_take"], style_sha="2" * 64, kind="FALLBACK_MINIMAL_EN", how="attempts.verified")
    row = _z_row(ld, bad, "kp2_en", "KP_EN", "kp_en", clips=clips_bad)
    assert row["violations"], "未承認Styleのfallbackは停止"
    # (記録欠落) 採用take UNKNOWN -> 停止
    clips_unknown = copy.deepcopy(clips)
    clips_unknown["kp2_en"]["adopted_take"] = None
    row = _z_row(ld, ent, "kp2_en", "KP_EN", "kp_en", clips=clips_unknown)
    assert "ADOPTED_TAKE_RECORD_INCOMPLETE" in row["violations"]
    # (parity不一致) ledger verdictがSTOP_PARITY -> 停止
    clips_par = copy.deepcopy(clips)
    clips_par["kp2_en"]["verdict"] = e129.V_PARITY
    row = _z_row(ld, ent, "kp2_en", "KP_EN", "kp_en", clips=clips_par)
    assert "TEXT_AUDIO_PARITY_MISMATCH" in row["violations"]


def test_z_clip_without_style_actual_record_is_not_retroactively_judged():
    """記録のないclip(過去run)は従来どおり(遡及しない)。分類核の置換は記録のあるclipだけ。"""
    _need(TTH)
    ld = os.path.join(TTH, "b1b")
    ent = copy.deepcopy(_results(ld)["key_phrases"]["2"]["english"])
    ent.pop("style_actual", None)
    clips = c130.event_ledger_clips(ld)
    row = _z_row(ld, ent, "kp2_en", "KP_EN", "kp_en", clips=clips)
    assert row["check"] in ("unrecorded", "legacy_unrecorded") and "lr_fallback_class" not in row


# ------------------------------------------------------------------ B6: Z style_actualの採用attempt同定
def test_b6_style_actual_uses_resolve_adopted_take_for_english_lock_kp_en():
    import er063_family_z_audio_01_test_01 as base
    spec = [s for s in base.make_plan("a2")[0] if s.kind == "kp_en"][0]
    txt = z.style_text_for(spec)
    sha = lambda t: __import__("hashlib").sha256(t.encode("utf-8")).hexdigest()
    lock = __import__("er003_v1_repro01_main_generate").KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION
    res = {"status": "OK", "style_prefix": {"sha256": sha(txt), "len": len(txt), "head200": txt[:200]}, "fallback_used": True,
           "attempts_log": [{"attempt": 1, "verified": False, "style_prefix": {"sha256": sha(txt), "len": len(txt), "head200": txt[:200]}}],
           "english_lock_attempts_log": [{"attempt": 4, "verified": True}]}
    rec = z.build_style_actual_record(spec, res)
    assert rec["sha256"] == sha(lock) and rec["adopted_phase"] == "fallback" and rec["adopted_identification"].startswith("resolve_adopted_take")
    # 旧heuristic(fallback_attempts_log→標準段の末尾)は採用ENGLISH_LOCKを取り違えて標準段のStyleを実測値にしていた(M-8)
    assert rec["sha256"] != sha(txt)
    # 解決できない旧記録は従来heuristic(識別方法を記録に残す)
    res2 = {"status": "OK", "style_prefix": {"sha256": sha(txt), "len": len(txt), "head200": txt[:200]},
            "standard_attempts_log": [{"attempt": 1, "style_prefix": {"sha256": sha(txt), "len": len(txt), "head200": txt[:200]}}]}
    rec2 = z.build_style_actual_record(spec, res2)
    assert rec2["sha256"] == sha(txt) and rec2["adopted_identification"].startswith("legacy_heuristic")


# ------------------------------------------------------------------ Y style gate(保存の証跡run、一時複製上)
def test_y_gate_normal_lr_passes_with_warning_on_evidence_run():
    import glob
    cands = sorted(glob.glob(os.path.join(YTRU, "**", "run_tru_ev_y_adv_4b", "b1b", "audit", "tts_generation_results.json"), recursive=True))
    if not cands:
        pytest.skip("Y evidence run absent")
    import importlib.util
    spec = importlib.util.spec_from_file_location("bw_audit", os.path.join(ROOT, "docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/BWIRE_audit_01/audit_wired_gate_01.py"))
    aud = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aud)
    old, _, mo = aud.y_gate(cands[0], "b1b", False)
    new, warns, mn = aud.y_gate(cands[0], "b1b", True)
    assert old is not None and new is not None, (mo, mn)
    assert aud.verdict(old["y_voice_1"]) == "BLOCK" and "LOCAL_REWRITE_RECOVERY" in old["y_voice_1"]["viol"]
    assert aud.verdict(new["y_voice_1"]) == "PASS" and warns.get("y_voice_1") == "LR_APPLIED"
