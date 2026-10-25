# b_light_proto_01 のtest (DEV/API 0)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/b_light_proto_01_test_01.py -q
import glob, os, socket, sys
import pytest

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b_light_proto_01 as B

C = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
TAIL = "。その奥に潜む岩の上着の秘密。"
S_OK = "杉野氏は8900本超" + TAIL            # 値は正しいが読み(杉野)は原稿と違う Azure 実転写
S_WELL = "月の詩は8900本超" + TAIL


@pytest.fixture(autouse=True)
def _no_net(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("API0 violation")
    monkeypatch.setattr(socket.socket, "connect", boom)


def j(c, p, s, **k):
    return B.composite_judge(c, p, s, **k)


# ---- 救済(正例): 月題の実転写 ----
def test_moon_garble_digit_split_with_reading_ok_is_rescued():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    assert r.equal and r.label == B.COMPOSITE_LABEL
    assert B.W_FROM_SECONDARY in r.warnings and B.W_GARBLE_EXPLAINED in r.warnings


def test_moon_garble_digit_plus_kanji_is_rescued():
    r = j(C, "月のシワ、8000九百本超" + TAIL, S_OK)
    assert r.equal and B.W_GARBLE_EXPLAINED in r.warnings


def test_alpha_mode_does_not_rescue_garble():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK, allow_explained_garble=False)
    assert not r.equal and r.blocked_by == "primary_secondary_value_contradiction" and r.protected


# ---- (vi) 設計段階で通らないこと ----
@pytest.mark.parametrize("p", [
    "月のしわ、89,000本超" + TAIL,          # 桁違い(カンマ付き)
    "月のしわ、89000本超" + TAIL,           # 桁違い
    "月のしわ、八万九千本超" + TAIL,        # 桁違い(漢数字)
    "月のしわ、8万9千本超" + TAIL,          # 桁違い(混在)
    "月のしわ、8800本超" + TAIL,            # 値違い
    "月のしわ、千九百本超" + TAIL,          # 桁欠落(attempt2型)
    "月野詩は8000句800本超え" + TAIL,       # 復号不能(8000+800=8800≠8900)
])
def test_value_contradiction_is_not_rescued_even_if_secondary_equals_script(p):
    r = j(C, p, S_OK)
    assert not r.equal and r.protected, (p, r.why)


@pytest.mark.parametrize("p", ["月のすわ、8000900本超" + TAIL, "月の巣は8000900本超" + TAIL, "月のしば、8000900本超" + TAIL,
                               "月のし、8000900本超" + TAIL, "月のしわし、8000900本超" + TAIL])
def test_reading_difference_is_not_rescued(p):
    r = j(C, p, S_OK)
    assert not r.equal and r.blocked_by == "primary_reading", (p, r.why)


@pytest.mark.parametrize("c,p,s", [
    ("三日待った", "三日間待った。", "3日待った。"),              # みっか/さんにち (N3-21型)
    ("三日待った", "3日待った", "3日待った"),
    ("二十歳になった", "20歳になった", "20歳になった"),
    ("十月一日に会う", "10月1日に会う", "10月1日に会う"),
])
def test_irregular_reading_values_are_excluded(c, p, s):
    r = j(c, p, s)
    assert not r.equal and r.blocked_by == "A4a_irregular_reading"


# ---- Primary/Secondary の組合せ ----
def test_secondary_only_correct_primary_reading_wrong_is_not_rescued():
    r = j(C, "月野詩は8,900本超え" + TAIL, S_WELL)        # Azure完全正答でもPrimary読みが違えばNG(Secondary読みは使わない)
    assert not r.equal and r.blocked_by == "primary_reading"


def test_primary_only_correct_secondary_value_wrong_is_not_rescued():
    r = j(C, "月のしわ、8,900本超" + TAIL, "月のしわ、8800本超" + TAIL)
    assert not r.equal and r.blocked_by == "secondary_value" and r.protected


def test_both_wrong_is_not_rescued():
    assert not j(C, "月のしわ、8800本超" + TAIL, "月のしわ、8800本超" + TAIL).equal


def test_primary_8800_secondary_8900_is_contradiction():
    r = j(C, "月のしわ、8800本超" + TAIL, S_OK)
    assert not r.equal and r.blocked_by == "primary_secondary_value_contradiction"


def test_negation_difference_blocks():
    r = j("三人は行かない", "3人は行く", "3人は行かない")
    assert not r.equal
    r2 = j("彼女は来ない", "彼女は来る", "彼女は来ない")
    assert not r2.equal


def test_secondary_empty_or_none_blocks():
    assert j(C, "月の氏は8000900本超" + TAIL, None).blocked_by == "secondary_unavailable"
    assert j(C, "月の氏は8000900本超" + TAIL, "  ").blocked_by == "secondary_unavailable"


def test_primary_missing_numeric_run_blocks():
    r = j(C, "月の氏は本超" + TAIL, S_OK)
    assert not r.equal and r.blocked_by == "primary_value_missing"


def test_unit_mismatch_blocks():
    r = j(C, "月の氏は8000900冊超" + TAIL, S_OK)
    assert not r.equal


def test_comma_formatted_primary_number_is_not_explained():
    assert B.explain_garble("8,000,900", 8900) is None


def test_no_value_atoms_is_not_applicable():
    r = j("月のしわが多い", "月の詩が多い", "月のしわが多い")
    assert not r.equal and r.blocked_by == "not_applicable"


def test_primary_value_equal_and_reading_ok_is_composite_pass():
    r = j(C, "月野氏は八千九百本超、その奥に潜む岩の上着の秘密。", S_OK)
    assert r.equal and B.W_GARBLE_EXPLAINED not in r.warnings


# ---- explain_garble の境界 ----
@pytest.mark.parametrize("run,target,ok", [
    ("8000900", 8900, True), ("8000九百", 8900, True), ("8000800", 8900, False), ("89000", 8900, False),
    ("0900", 900, False), ("8900", 8900, False), ("80", 8900, False), ("1200300", 1500, False), ("1000500", 1500, True), ("1000200", 1200, True),
    ("9000", 8900, False),
])
def test_explain_garble_boundaries(run, target, ok):
    assert (B.explain_garble(run, target) is not None) == ok


# ---- 隔離 ----
def test_production_modules_do_not_import_prototype():
    hits = []
    for f in glob.glob("*.py"):
        if f.startswith("b_light"):
            continue
        try:
            t = open(f, encoding="utf8").read()
        except Exception:
            continue
        if "b_light_proto" in t:
            hits.append(f)
    assert hits == []


def test_prototype_has_no_network_or_llm_imports():
    src = open(B.__file__, encoding="utf8").read()
    for bad in ("openai", "requests", "azure", "anthropic", "urllib.request", "httpx"):
        assert f"import {bad}" not in src, bad


def test_deterministic():
    a = [j(C, "月の氏は8000900本超" + TAIL, S_OK).why for _ in range(3)]
    assert len(set(a)) == 1
