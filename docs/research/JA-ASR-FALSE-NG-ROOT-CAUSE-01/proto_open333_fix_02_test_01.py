# proto_open333_fix_02 の単体test(API 0)。実行: PYTHONUTF8=1 .venv/Scripts/python.exe -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_open333_fix_02_test_01.py -q
import sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import pytest
import eval_common_02 as E
import proto_open333_fix_02 as P
import er007_ja_asr_validator_01 as javal

E.api0_guard_on()
PASSING = E.uj.PASSING_STATES
NEG = [("月のしわ、8,900本超", "月の巣は八千九百本長。"), ("月のしわ、8,900本超", "月のしば八千九百本長"), ("月のしわ、8,900本超", "月のす八千九百本長"),
       ("月のしわ、8,900本間", "月のしば八千九百本目"), ("月のしわ、8,900本超", "月のしわー八千九百本長")]
KEEP = [("月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密", "月の詩は八千九百本長。その奥に潜む岩の上着の秘密"),   # MOON#1: 助詞は=wa
        ("月のしわ、8,900本超", "月のしわ八千九百本長"), ("売上は8,900円超です", "売上は八千九百円長です"),
        ("このあと、3人の声を聞きます", "この後、三人の声を聞きます")]


def st(c, a, mode=None):
    if mode is None:
        return E.primary_stage(c, a, False)
    with P.apply_in_process(mode):
        return E.primary_stage(c, a, False)


@pytest.fixture(autouse=True)
def _flag():
    javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False


@pytest.mark.parametrize("mode", ("E1P", "E3P"))
@pytest.mark.parametrize("c,a", NEG)
def test_neg_blocked(mode, c, a):
    assert st(c, a, mode)["state"] not in PASSING


@pytest.mark.parametrize("mode", ("E1P", "E3P"))
@pytest.mark.parametrize("c,a", KEEP)
def test_keep_unchanged(mode, c, a):
    b, g = st(c, a), st(c, a, mode)
    assert (b["state"], b["label"]) == (g["state"], g["label"])


def test_moon1_is_base_pass_and_e1_breaks_it():
    c, a = KEEP[0]
    assert st(c, a)["state"] in PASSING
    assert st(c, a, "E1")["state"] not in PASSING and st(c, a, "E1P")["state"] in PASSING


@pytest.mark.parametrize("mode", P.MODES)
def test_no_new_pass(mode):
    for c, a in NEG + KEEP + [("三日間", "三日目"), ("今日は晴れ", "きょうははれ"), ("売上は8,900円です", "売上は八千九百ドルです")]:
        if st(c, a)["state"] not in PASSING:
            assert st(c, a, mode)["state"] not in PASSING


def test_particle_exemption_is_narrow():
    assert P.explained_p("しわ", "詩は") and not P.explained_p("しわ", "巣は") and not P.explained_p("しわ", "しば")
