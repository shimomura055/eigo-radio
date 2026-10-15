# -*- coding: utf-8 -*-
"""AUW 委任_11 test: U1発効(既定False)・A7維持・実音声harnessの事前検査(API 0)。
A3(length再評価)は条件付きSTOP s4により是正を保留したため、A3の挙動を固定するtestは置かない(IMPLEMENTATION_11.md §3)。"""
import json
import os

import pytest

import er078_asr_unified_judge_01 as uj
from er078_asr_unified_judge_01 import AttemptCtx, PrimaryResult, unified_judge


class _Sec:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def __call__(self, ctx):
        self.calls += 1
        return self.text


def _ctx(canon, **kw):
    return AttemptCtx(canonical_text=canon, wav_sha256="x" * 64, audio_seconds=3.0, segment_key="t", **kw)


def test_u1_released_by_default_low_similarity_goes_to_secondary():
    assert uj.U1_KEEP_C1_SIMILARITY_EXCLUSIONS is False
    sec = _Sec("今日は晴れ。")
    r = unified_judge(_ctx("今日は晴れ。"), PrimaryResult(False, "全然違う", signals={"similarity": 0.2}), sec, lang="ja", role="x")
    assert sec.calls == 1 and r.state == uj.PASS_WITH_WARNING


def test_u1_released_c1_proper_noun_goes_to_secondary():
    sec = _Sec("ガス会社に連絡してください。")
    r = unified_judge(_ctx("ガス会社に連絡してください。"), PrimaryResult(False, "カス会社に連絡してください。", signals={"c1_proper_noun_diff": True}),
                      sec, lang="ja", role="x")
    assert sec.calls == 1 and r.state == uj.PASS_WITH_WARNING


def test_a7_reading_protection_still_excludes_after_u1():
    sec = _Sec("Metaが新しい発表をしました。")
    r = unified_judge(_ctx("Metaが新しい発表をしました。"),
                      PrimaryResult(False, "METAが新しい発表をしました。", signals={"reading_dictionary_mismatch": True}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A7_READING_DICT_MISMATCH" and sec.calls == 0


def test_u1_rollback_flag_restores_previous_exclusion(monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", True)
    sec = _Sec("今日は晴れ。")
    r = unified_judge(_ctx("今日は晴れ。"), PrimaryResult(False, "全然違う", signals={"similarity": 0.2}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and sec.calls == 0


def test_a1_a2_a4_protections_unchanged_after_u1():
    sec = _Sec("店は午後三時に開きます。")
    r = unified_judge(_ctx("店は午後三時に開きます。"), PrimaryResult(False, "店は午後五時に開きます。"), sec, lang="ja", role="x")
    assert r.state == uj.NG_PROTECTED and sec.calls == 0
    r = unified_judge(_ctx("橋を渡ります。"), PrimaryResult(False, "箸を渡ります。", signals={"c2_homophone_candidate": True}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A4_C2_HOMOGRAPH"


def test_harness_requires_tension_body_before_any_api_call(tmp_path, monkeypatch):
    """委任_11 初回bnarrはparts.jsonにtension_bodyが無くKeyErrorで終了した(Hook/Tension/Closing生成前)。再発防止の事前検査。"""
    import er078_auw_runtime_evidence_11 as h
    assert "tension_body" in h.REQUIRED_PARTS_KEYS
    assert os.path.exists(h.DEFAULT_PARTS)
    d = json.load(open(h.DEFAULT_PARTS, encoding="utf-8"))
    assert all(d.get(k) for k in h.REQUIRED_PARTS_KEYS)
    bad = tmp_path / "parts.json"
    d2 = dict(d)
    d2.pop("tension_body")
    bad.write_text(json.dumps(d2), encoding="utf-8")
    with pytest.raises(SystemExit):
        h.run_bnarr(False, 16.0, str(bad))
