import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import eval_sweep as e


def mk(w0, w1):
    return {"p|0": {"winner_label": w0}, "p|1": {"winner_label": w1}}


def test_score():
    assert e.score_from(mk("A", "B"), "p")["x_score"] == 1.0   # o0: x=A勝ち, o1: x=B勝ち
    assert e.score_from(mk("B", "A"), "p")["x_score"] == 0.0
    assert e.score_from(mk("A", "A"), "p")["x_score"] == 0.5
    assert e.score_from(mk("tie", "tie"), "p")["split"]


def test_empty_assert():
    import pytest
    with pytest.raises(AssertionError):
        e.judge_pair("x", "", "abc")


def test_clean_and_dirs():
    assert e.clean("a【事実1】b") == "ab"
    assert e.final_text(e.art_dir("S0", "space_weapons", 3))
