# proto_open333_fix_01 の単体test(API 0)。実行: PYTHONUTF8=1 .venv/Scripts/python.exe -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_open333_fix_01_test_01.py -q
import sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import pytest
import eval_common_02 as E
import proto_open333_fix_01 as P
import er007_ja_asr_validator_01 as javal

E.api0_guard_on()
PASSING = E.uj.PASSING_STATES

# (原稿, 転写) 糊付け型の誤PASS(現行Productionで通る/E1,E3で止めたい)
GLUE_NEG = [
    ("月のしわ、8,900本超", "月の巣は八千九百本長。"),      # N3-07
    ("月のしわ、8,900本超", "月のしば八千九百本長"),        # 糊付けが わ->ば になる並び
    ("月のしわ、8,900本間", "月のしば八千九百本目"),
]
# 通り続けるべき正例: 数値opcodeの残余が空/読み一致、または単独Eの正当な同音
POS = [
    ("月のしわ、8,900本超", "月のしわ八千九百本長"),         # 数値のみ+超長(従来PASS)
    ("売上は8,900円です", "売上は八千九百円です"),
    ("売上は8,900円超です", "売上は八千九百円長です"),
]


def st(c, a, mode=None):
    if mode is None:
        return E.primary_stage(c, a, False)
    with P.apply_in_process(mode):
        return E.primary_stage(c, a, False)


@pytest.fixture(autouse=True)
def _flag():
    javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False


def test_baseline_glue_pass_documented():
    # 現行Productionが糊付け型でPASSする(原因の再現)。N3-07。
    assert st(*GLUE_NEG[0])["state"] in PASSING


@pytest.mark.parametrize("mode", P.MODES)
def test_n3_07_blocked(mode):
    assert st(*GLUE_NEG[0], mode)["state"] not in PASSING


@pytest.mark.parametrize("mode", ("E1", "E3"))
@pytest.mark.parametrize("c,a", GLUE_NEG)
def test_glue_neg_blocked(mode, c, a):
    base = st(c, a)
    got = st(c, a, mode)
    assert got["state"] not in PASSING


@pytest.mark.parametrize("mode", ("E1", "E3"))
@pytest.mark.parametrize("c,a", POS)
def test_pos_unchanged(mode, c, a):
    assert (st(c, a)["state"], st(c, a)["label"]) == (st(c, a, mode)["state"], st(c, a, mode)["label"])


@pytest.mark.parametrize("mode", P.MODES)
def test_monotone_never_new_pass(mode):
    for c, a in GLUE_NEG + POS + [("三日間", "三日目"), ("海からの封鎖", "海からの風さ"), ("今日は晴れ", "きょうははれ")]:
        if st(c, a)["state"] not in PASSING:
            assert st(c, a, mode)["state"] not in PASSING


def test_non_number_entry_unchanged():
    # 数値を含まない従来のCandidate E(封鎖/風さ、三日間/三日目)はE1/E3で不変(OPEN-333本来の過許容は本protoの対象外)
    for c, a in [("海からの封鎖", "海からの風さ"), ("三日間", "三日目")]:
        for m in P.MODES:
            assert st(c, a)["state"] == st(c, a, m)["state"]


def test_strip_numerals():
    assert P.strip_numerals("しわ8,900") == "しわ" and P.strip_numerals("巣は八千九百") == "巣は"
