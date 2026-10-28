# proto_unified_02 のtest (DEV/API 0)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/proto_unified_02_test_01.py -q
import hashlib, os, socket, subprocess, sys
import pytest

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proto_unified_02 as U
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
TAIL = "！その奥に潜む「岩の上着」の秘密"
F123 = U.Flags(True, True, True)
F13 = U.Flags(True, False, True)


@pytest.fixture(autouse=True)
def _no_net(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("API0 violation")
    monkeypatch.setattr(socket.socket, "connect", boom)


def J(c, p, s, f=U.Flags()):
    return U.judge(c, p, s, E.dummy_wav(), f)


# ---- 既定=L0同一(DefaultOffIsolation) ----
def test_default_flags_all_off():
    f = U.Flags()
    assert (f.l1, f.l2, f.l3) == (False, False, False) and f.name() == "L0"


def test_default_equals_production_adapter_and_leaves_no_patch():
    orig_num, orig_az = sec._numeric_value_equivalence, sec._azure_stt_strict
    cases = [(MOON, "月の詩は、8,900本超" + TAIL, "月の詩は8900本超" + TAIL), (MOON, "月のしわ、8,900本超" + TAIL, None), ("今日は一日中雨", "今日はついたち中雨", "今日は一日中雨"),
             (MOON, "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。")]
    for c, p, s in cases:
        direct = U._adapter(c, p, s, E.dummy_wav(), U.Flags(), [])["asr_judgement"]
        mine = J(c, p, s)
        assert (mine["state"], mine["reason"]) == (direct.get("state"), direct.get("reason_code"))
        assert mine["layers"] == []                      # L0では層の発火記録が空
    assert sec._numeric_value_equivalence is orig_num and sec._azure_stt_strict is orig_az   # 差替の後始末


def test_no_network_in_default_and_all_flags():
    for f in (U.Flags(), U.Flags(True), F123):
        J(MOON, "月の詩は、8,900本超え" + TAIL, "月の詩は8900本越え" + TAIL, f)       # socket guardがあるので呼出があれば例外


# ---- L1: 不規則読みガード ----
def test_l1_irregular_guard_blocks_ichinichi():
    c, p = "今日は一日中雨", "今日はついたち中雨"
    assert J(c, p, None, U.Flags(True))["cat"] == "NG"
    assert J(c, p, p, U.Flags(True))["cat"] == "NG"
    assert J(c, p, c, U.Flags(True))["cat"] == "NG"


def test_l1_still_rescues_particle_homophone():
    r = J(MOON, "月の死は、8,900本超" + TAIL, None, U.Flags(True))
    assert r["cat"] == "PASS_W" and r["layers"][0]["layer"] == "L1_v2_pron"


# ---- L3: 汎用規則・正例 ----
@pytest.mark.parametrize("k", ["超え", "越え", "こえ"])
def test_l3_rescues_generic_koe(k):
    for c, a in ((MOON, f"月のしわ、8,900本{k}" + TAIL), ("参加者は100人超でした", f"参加者は100人{k}でした"), ("売上は1,200円超です", f"売上は1,200円{k}です")):
        assert J(c, a, a, U.Flags(True))["cat"] == "NG"           # L3 OFF では救済されない
        r = J(c, a, a, F13)
        assert r["cat"] == "PASS_W" and any(x["layer"] == "L3_dict_koe" for x in r["layers"])


def test_l3_requires_both_engines():
    a = "月のしわ、8,900本超え" + TAIL
    assert J(MOON, a, None, F13)["cat"] == "NG"                    # Secondary無し=発火しない


# ---- L3: 負例(衝突test)。増分0が条件(L0がPASSの型はL0と同じ) ----
@pytest.mark.parametrize("a", [f"月のしわ、{v}本超え" + TAIL for v in ("8,800", "890", "89,000", "9,900")] + [f"月のしわ、8,900{u}超え" + TAIL for u in ("個", "枚", "人", "円")]
                         + ["月のしわ、8,900本を超え" + TAIL, "月のしわ、8,900超え" + TAIL, "月のしわ、本超え" + TAIL, "月のしわ、8,900本超え", "月のしわ、8,900本未満" + TAIL, "月のしわ、8,900本超えない" + TAIL, "月のすわ、8,900本超え" + TAIL])
def test_l3_neg_no_incremental_pass(a):
    l0 = J(MOON, a, a)["cat"]
    assert J(MOON, a, a, F123)["cat"] == "NG" or l0 != "NG"
    assert not (l0 == "NG" and J(MOON, a, a, F123)["cat"] != "NG")


@pytest.mark.parametrize("k", ["長", "帳", "蝶", "調", "町", "鳥"])
def test_l3_does_not_change_homophone_kanji(k):
    a = f"月のしわ、8,900本{k}" + TAIL
    assert J(MOON, a, a, F123)["cat"] == J(MOON, a, a)["cat"]      # L3は本長/本帳/本蝶に影響しない(L0と同一判定)


def test_l3_one_engine_wrong_value_not_fired():
    ok, bad = "月のしわ、8,900本越え" + TAIL, "月のしわ、8,800本超え" + TAIL
    assert J(MOON, bad, ok, F123)["cat"] == "NG" and J(MOON, ok, bad, F123)["cat"] == "NG"


def test_l3_not_attached_to_non_quantity_chou():
    c = "超高速で3回走る"
    assert J(c, "こえ高速で3回走る", "こえ高速で3回走る", F123)["cat"] == "NG"


def test_l3_no_hardcoded_moon_strings():
    src = open(U.__file__, encoding="utf8").read()
    for bad in ("月のしわ", "岩の上着", "8,900", "8900"):
        assert bad not in src, bad


# ---- L2/L4 ----
def test_l2_beta_via_secondary_value():
    p = "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"
    s = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
    r = J(MOON, p, s, U.Flags(True, True))
    assert r["cat"] == "PASS_W" and r["route"].startswith("L2_beta_composite")


def test_best_of_n_stops_at_first_pass_and_counts_calls():
    seq = [{"cat": "NG", "reason": "x", "route": "x"}, {"cat": "PASS_W", "reason": "y", "route": "y"}, {"cat": "PASS", "reason": "z", "route": "z"}]
    assert U.best_of_n(seq, 1)["cat"] == "NG"
    r = U.best_of_n(seq, 3)
    assert (r["cat"], r["stopped_at"], r["extra_openai_calls"]) == ("PASS_W", 2, 1)
    assert U.hyper_reach(4, 2, 1) == 0.5 and U.hyper_reach(4, 0, 4) == 0.0 and U.hyper_reach(4, 1, 4) == 1.0


def test_hr_candidate_never_changes_judgement_and_is_not_imported_by_judge():
    src = open(U.__file__, encoding="utf8").read()
    body = src.split("def judge(")[1].split("def best_of_n")[0]
    assert "hr_candidate" not in body                              # 判定関数は人間レビュー候補関数を参照しない(自動PASSパスなし)
    r = U.hr_candidate(MOON, [("スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。", "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。")])
    assert r["candidate"] is True
    assert U.hr_candidate(MOON, [("月のしわ、8,800個超" + TAIL, "月のしわ、8,800個超" + TAIL)])["candidate"] is False
    assert U.hr_candidate("今日は一日中雨", [("今日はついたち中雨", "今日はついたち中雨")])["candidate"] is False


def test_production_files_not_modified():
    r = subprocess.run(["git", "diff", "--quiet", "--", "er007_ja_secondary_asr_01.py", "er078_asr_unified_judge_01.py", "er078_asr_value_guard_01.py", "er007_ja_asr_validator_01.py"])
    assert r.returncode == 0


def test_deterministic():
    a = [J(MOON, "月野詩は8,900本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。", F123)["route"] for _ in range(3)]
    assert len(set(a)) == 1
