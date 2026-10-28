# OPEN-515 R-6 (FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_04): Secondary受理への値等価層適用(R4)・桁区切り(R3)のtest。API 0(全てmock)。
import pytest

import er007_ja_secondary_asr_01 as ja
import er078_asr_unified_judge_01 as uj
from er078_asr_unified_ja_wiring_test_01 import Az, _iso  # noqa: F401  (autouse fixture再利用)

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
SEC_ONLY_PRIMARY = "えーと、あのー、" + MOON  # Primaryを非PASSにしてSecondary受理面だけを見る


def run(canon, primary, az, monkeypatch, **kw):
    monkeypatch.setattr(ja, "_azure_stt_strict", az)
    kw.setdefault("cascade_enabled", True)
    return ja.evaluate_attempt_ja_with_cascade_detail(canon, primary, "dummy.wav", **kw)


def test_rollback_constant_default_true_and_not_env_or_arg():
    assert ja.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED is True
    src = open(ja.__file__, encoding="utf-8").read()
    line = [l for l in src.splitlines() if l.startswith("JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED")]
    assert line == ["JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED = True"]  # 単一の定数定義(env/flag/引数から導出しない)


def test_secondary_comma_drop_accepted_when_nonnumeric_exact(monkeypatch):
    az = Az(("月のしわ、8900本超！その奥に潜む「岩の上着」の秘密", None))
    d = run(MOON, SEC_ONLY_PRIMARY, az, monkeypatch)
    assert d["verified"] is True and az.calls == 1
    assert "secondary_numeric_value_equivalence" in d["asr_judgement"]["adapter"]["layers"]


def test_secondary_comma_drop_not_accepted_when_flag_false(monkeypatch):
    monkeypatch.setattr(ja, "JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED", False)
    az = Az(("月のしわ、8900本超！その奥に潜む「岩の上着」の秘密", None))
    d = run(MOON, SEC_ONLY_PRIMARY, az, monkeypatch)
    assert d["verified"] is False


@pytest.mark.parametrize("asr", [
    "月の詩は、8900本超！その奥に潜む「岩の上着」の秘密",     # R1(しわ→詩は)は非受理のまま
    "月の詩は、8,900本超！その奥に潜む「岩の上着」の秘密",
    "月のしわ、8800本超！その奥に潜む「岩の上着」の秘密",     # 値DIFF
    "月のしわ、89000本超！その奥に潜む「岩の上着」の秘密",    # 10倍
    "月のしわ、890本超！その奥に潜む「岩の上着」の秘密",
    "月のしわ、8900人超！その奥に潜む「岩の上着」の秘密",     # 単位違い
    "月のしわ、8000900本超！その奥に潜む「岩の上着」の秘密",  # 値garble
    "月のしわ、8900本超！その奥に潜む「岩の下着」の秘密",     # 非数値差併存
])
def test_secondary_value_or_nonnumeric_difference_not_accepted(asr, monkeypatch):
    az = Az((asr, None))
    d = run(MOON, SEC_ONLY_PRIMARY, az, monkeypatch)
    assert d["verified"] is False
    assert "secondary_numeric_value_equivalence" not in d["asr_judgement"]["adapter"]["layers"]


def test_primary_comma_drop_value_equivalence_trigger(monkeypatch):
    # Primary側(resolver無し)でも桁区切り脱落のみは値等価で受理(R3)。DIFFは非受理。
    monkeypatch.setattr(ja.javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False, raising=False)
    az = Az((None, "unavailable"))
    d = run("売上は1,200円です", "売上は1200円です", az, monkeypatch)
    assert d["verified"] is True and d["final_status"] == ja.NUMERIC_VALUE_EQUIVALENT_MATCH and az.calls == 0
    for bad in ("売上は1,300円です", "売上は12000円です", "売上は1200ドルです", "売上は1200円ではありません"):
        d = run("売上は1,200円です", bad, Az((None, "unavailable")), monkeypatch)
        assert d["verified"] is False, bad


def test_irregular_reading_kana_for_numeral_nonnumeric_part_not_accepted(monkeypatch):
    # 数値atomでない不規則読み(二十日→はつか 等)は値等価層の対象外のまま
    d = run("二十日に会う", "はつかに会う", Az(("はつかに会う", None)), monkeypatch)
    assert "secondary_numeric_value_equivalence" not in d["asr_judgement"]["adapter"]["layers"]
