# -*- coding: utf-8 -*-
"""P' DEVラッパのunit test(API非呼出、¥0)。"""
import copy
import hashlib
import inspect
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402

ORIG_R = vfl01.build_researcher_prompt
ORIG_V = vfl01.build_verification_prompt
import er052_open233_ledger_clarity_pprime_dev_01 as dev  # noqa: E402

TOPIC = "テスト用トピック"
LEDGER = {"facts": [{"fact_id": "F1", "claim": "x"}]}


def _fingerprint():
    return (
        hashlib.sha256(repr(vfl01.FACT_LEDGER_JSON_SCHEMA).encode()).hexdigest(),
        hashlib.sha256(repr(vfl01.VERIFICATION_JSON_SCHEMA).encode()).hexdigest(),
        hashlib.sha256(inspect.getsource(vfl01.build_verified_ledger_text).encode()).hexdigest(),
    )


def test_a_import_does_not_patch():
    assert vfl01.build_researcher_prompt is ORIG_R
    assert vfl01.build_verification_prompt is ORIG_V


def test_b_pprime_and_baseline_outputs():
    base_r = ORIG_R(TOPIC)
    base_v = ORIG_V(TOPIC, LEDGER)
    with dev.patched_prompts("pprime", vfl01):
        assert vfl01.build_researcher_prompt(TOPIC) == base_r + dev.SEP + dev.RESEARCHER_APPEND
        assert vfl01.build_verification_prompt(TOPIC, LEDGER) == base_v + dev.SEP + dev.VERIFICATION_APPEND
        assert vfl01.build_researcher_prompt(topic=TOPIC) == base_r + dev.SEP + dev.RESEARCHER_APPEND
    with dev.patched_prompts("baseline", vfl01):
        assert vfl01.build_researcher_prompt is ORIG_R
        assert vfl01.build_researcher_prompt(TOPIC) == base_r
        assert vfl01.build_verification_prompt(TOPIC, LEDGER) == base_v


def test_c_restored_after_exit_and_exception():
    with dev.patched_prompts("pprime", vfl01):
        assert vfl01.build_researcher_prompt is not ORIG_R
    assert vfl01.build_researcher_prompt is ORIG_R and vfl01.build_verification_prompt is ORIG_V
    with pytest.raises(RuntimeError):
        with dev.patched_prompts("pprime", vfl01):
            raise RuntimeError("boom")
    assert vfl01.build_researcher_prompt is ORIG_R and vfl01.build_verification_prompt is ORIG_V


def test_d_schema_enum_and_ledger_builder_unchanged():
    before = _fingerprint()
    schema_before = copy.deepcopy(vfl01.FACT_LEDGER_JSON_SCHEMA)
    with dev.patched_prompts("pprime", vfl01):
        assert _fingerprint() == before
        assert vfl01.FACT_LEDGER_JSON_SCHEMA == schema_before
    assert _fingerprint() == before
    enum = vfl01.VERIFICATION_JSON_SCHEMA["schema"]["properties"]["verifications"]["items"]["properties"]["verdict"]["enum"]
    assert set(enum) == {"VERIFIED", "AMBIGUOUS", "REJECTED"}


def test_e_invalid_variant_raises():
    with pytest.raises(ValueError):
        dev.resolve_variant({dev.ENV_NAME: "PPRIME"})
    with pytest.raises(ValueError):
        dev.resolve_variant({dev.ENV_NAME: ""})
    with pytest.raises(ValueError):
        with dev.patched_prompts("bogus", vfl01):
            pass
    assert dev.resolve_variant({}) == "baseline"
    assert dev.resolve_variant({dev.ENV_NAME: "baseline"}) == "baseline"
    assert dev.resolve_variant({dev.ENV_NAME: "pprime"}) == "pprime"


def test_f_block_contents():
    assert "どのフィールドにも改行を含めない" in dev.RESEARCHER_APPEND
    assert "同じ主体・同じ指標の時系列変化のときだけ" in dev.RESEARCHER_APPEND
    assert "別の出来事は別factのままにし、順序づけで結合しない" in dev.RESEARCHER_APPEND
    assert "原資料にない否定・因果・括弧・番号をclaimに入れない" in dev.RESEARCHER_APPEND
    assert "順序: 途中" in dev.RESEARCHER_APPEND and "語義: 原語=" in dev.RESEARCHER_APPEND
    assert "原資料より強い断定" in dev.VERIFICATION_APPEND and "AMBIGUOUS" in dev.VERIFICATION_APPEND


def test_g_fresh_out_dir_check(tmp_path):
    (tmp_path / "research_ledger").mkdir()
    with pytest.raises(SystemExit):
        dev.assert_fresh_out_dir(str(tmp_path))
    dev.assert_fresh_out_dir(str(tmp_path / "none"))


def test_h_dry_run_no_dir_created(tmp_path):
    out = tmp_path / "o"
    rc = dev.main(["--out-dir", str(out), "--dry-run"])
    assert rc == 0 and not out.exists()
    assert vfl01.build_researcher_prompt is ORIG_R
