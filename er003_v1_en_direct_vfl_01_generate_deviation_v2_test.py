# -*- coding: utf-8 -*-
# ============================================================
# er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py
# ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02: Production配線した
# Ledger Deviation Checker v2の post-hoc validation ロジック(API呼び出し
# 不要、無料)の受入テスト。LLM自体の判定品質は
# er009_ledger_deviation_recalibration_02_test.py の9種類false negative
# fixture(実API呼び出し、全PASS確認済み)で別途検証している。
# ============================================================
from __future__ import annotations

import er003_v1_en_direct_vfl_01_generate as vfl01


def _base_deviation(severity: str, **flags) -> dict:
    d = {k: False for k in vfl01.DEVIATION_FLAG_KEYS}
    d.update(flags)
    return {"claim_in_article": "x", "issue": "y", "severity": severity, "explanation": "z", **d}


def test_major_with_true_flag_stays_major():
    raw = {"deviations": [_base_deviation("MAJOR", changed_number=True)]}
    parsed = vfl01._apply_deviation_post_hoc_validation(raw)
    assert parsed["deviations"][0]["severity"] == "MAJOR"
    assert parsed["deviations"][0]["auto_downgraded"] is False
    assert parsed["overall_status"] == "LEDGER_DEVIATION"


def test_major_with_all_flags_false_is_downgraded():
    raw = {"deviations": [_base_deviation("MAJOR")]}
    parsed = vfl01._apply_deviation_post_hoc_validation(raw)
    assert parsed["deviations"][0]["severity"] == "MINOR"
    assert parsed["deviations"][0]["auto_downgraded"] is True
    assert parsed["overall_status"] == "LEDGER_COMPLIANT"


def test_minor_with_all_flags_false_stays_minor_and_compliant():
    raw = {"deviations": [_base_deviation("MINOR")]}
    parsed = vfl01._apply_deviation_post_hoc_validation(raw)
    assert parsed["deviations"][0]["severity"] == "MINOR"
    assert parsed["overall_status"] == "LEDGER_COMPLIANT"


def test_no_deviations_is_compliant():
    parsed = vfl01._apply_deviation_post_hoc_validation({"deviations": []})
    assert parsed["deviations"] == []
    assert parsed["overall_status"] == "LEDGER_COMPLIANT"


def test_mixed_one_downgraded_one_real_major_still_deviation():
    raw = {"deviations": [
        _base_deviation("MAJOR"),  # 全フラグfalse -> 降格されるはず
        _base_deviation("MAJOR", changed_scope=True),  # 本物のMAJOR
    ]}
    parsed = vfl01._apply_deviation_post_hoc_validation(raw)
    severities = [d["severity"] for d in parsed["deviations"]]
    assert severities == ["MINOR", "MAJOR"]
    assert parsed["overall_status"] == "LEDGER_DEVIATION"


def test_schema_required_fields_include_all_flags():
    props = vfl01.DEVIATION_JSON_SCHEMA["schema"]["properties"]["deviations"]["items"]["properties"]
    for key in vfl01.DEVIATION_FLAG_KEYS:
        assert key in props, f"missing flag in schema: {key}"
        assert props[key]["type"] == "boolean"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"PASS: {t.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed")
