# -*- coding: utf-8 -*-
"""OPEN-479 (Fable承認2026-10-23) test: er012_b.generate_voice_body_wide_margin はX/Z run scope内のときだけ
segment_idを evaluate_attempt_with_cascade へ渡す(会話clip full_story_part{n}_c{k} -> FULL_STORY -> PNAP/RET/5role適用可能)。
scope外(Family B/C・単体呼出)は引数自体を渡さず従来どおり。全てmock(API 0・費用0)。"""
import ast
import os

import pytest

import er006_secondary_asr_01 as sec
import er006_asr_provider_routing_01 as routing
import er020_tts_retry_local_rewrite_01 as er020
import er103_proper_noun_alarm_policy_01 as pnap
import er109_xz_scope_01 as scope
from er078_asr_unified_wiring_05_test_01 import Az, CANON, _iso, _tts_mocks  # noqa: F401

ROOT = os.path.dirname(os.path.abspath(__file__))


def _run(tmp_path, monkeypatch, seg_name, scope_family):
    import er012_b_family_voices_production_01 as bv
    _tts_mocks(monkeypatch, [])
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (CANON, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((CANON, None)))
    calls = []
    real = sec.evaluate_attempt_with_cascade

    def spy(*a, **k):
        calls.append(dict(k))
        return real(*a, **k)
    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade", spy)
    out = str(tmp_path / "t_open479" / "b1b" / "narration" / f"{seg_name}.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if scope_family:
        with scope.run_scope(scope_family):
            r = bv.generate_voice_body_wide_margin(CANON, out, "Puck", max_attempts=2)
    else:
        r = bv.generate_voice_body_wide_margin(CANON, out, "Puck", max_attempts=2)
    return r, calls


@pytest.mark.parametrize("fam", ["Z", "X"])
def test_a_xz_scope_passes_segment_id_and_role_resolves(fam, tmp_path, monkeypatch):
    r, calls = _run(tmp_path, monkeypatch, "full_story_part1_c14", fam)
    assert calls and all(c.get("segment_id") == "full_story_part1_c14" for c in calls)
    assert er020.resolve_narrative_role(calls[0]["segment_id"]) == "FULL_STORY"
    assert er020.resolve_narrative_role(calls[0]["segment_id"]) in pnap.APPLICABLE_ROLES   # ROLE_NOT_APPLICABLEにならない


@pytest.mark.parametrize("seg", ["full_story_part1_c14", "point_one", "full_story_part2"])
def test_b_outside_scope_bc_keeps_legacy_call_without_segment_id(seg, tmp_path, monkeypatch):
    assert scope.current_scope() is None
    r, calls = _run(tmp_path, monkeypatch, seg, None)
    assert calls and all("segment_id" not in c for c in calls)


def test_b2_scope_off_flag_disabled_keeps_legacy(tmp_path, monkeypatch):
    import er109_asr_orthographic_equivalence_01 as e109
    monkeypatch.setattr(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False)
    r, calls = _run(tmp_path, monkeypatch, "full_story_part1_c14", "Z")
    assert calls and all("segment_id" not in c for c in calls)


def test_b3_dummy_path_outside_layout_no_segment_id(tmp_path, monkeypatch):
    import er012_b_family_voices_production_01 as bv
    _tts_mocks(monkeypatch, [])
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (CANON, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((CANON, None)))
    calls = []
    real = sec.evaluate_attempt_with_cascade
    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade", lambda *a, **k: (calls.append(dict(k)), real(*a, **k))[1])
    with scope.run_scope("Z"):
        bv.generate_voice_body_wide_margin(CANON, str(tmp_path / "dummy_out.wav"), "Puck", max_attempts=2)
    assert calls and all("segment_id" not in c for c in calls)


def test_c_narrator_path_unchanged_source():
    src = open(os.path.join(ROOT, "er003_v1_sing01_news_tail_fix.py"), encoding="utf-8").read()
    assert "if review_lock._has_valid_narration_layout(out_path):\n            _, _, segment_id = review_lock.derive_segment_key(out_path)" in src
    assert "segment_id=segment_id, detail_out=_aj" in src


def test_d_only_gated_call_site_has_segment_id_kw():
    """er012_b内のevaluate_attempt_with_cascade呼出は1箇所のみで、segment_idは**_seg_kw(scope限定)経由のみ。直接渡しがない。"""
    src = open(os.path.join(ROOT, "er012_b_family_voices_production_01.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    sites = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "evaluate_attempt_with_cascade"]
    assert len(sites) == 1
    assert not any(k.arg == "segment_id" for k in sites[0].keywords)
    assert any(k.arg is None for k in sites[0].keywords)   # **_seg_kw
    assert "xz_scope.is_active_for_run()" in src


def test_e_scope_not_left_behind():
    assert scope.current_scope() is None


def test_d_replay_after_only_tier3_label_changes():
    """固定済みreplay結果: verified/stateのPASS<->NG変化0、変化はTier3警告ラベル/監査layers追加のみ(2件)。"""
    import json
    p = os.path.join(ROOT, "er103_output", "ret_prod_z_evidence_01", "open479_replay_after.json")
    if not os.path.exists(p):
        pytest.skip("replay evidence not present")
    d = json.load(open(p, encoding="utf-8"))
    assert d["summary"]["l1_changed"] == 0 and d["summary"]["l2_errors"] == 0
    for x in d["level2"]:
        if not x["diff_keys"]:
            continue
        assert x["none"]["verified"] == x["sid"]["verified"]
        assert x["none"]["state"] == x["sid"]["state"]
        assert x["none"]["hr_required"] == x["sid"]["hr_required"]
        assert set(x["diff_keys"]) <= {"final_status", "cls", "reason_code", "warnings", "primary_warn", "secondary_called", "layers"}
        assert x["sid"]["layers"] == ["tier3"]
