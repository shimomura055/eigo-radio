# -*- coding: utf-8 -*-
"""U1 Trial 委任_03: API0 test。essentials無しSeed(メロス)で修正版B関数が現行Promptとbyte同一であること等。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sftrial_dev_runner_01 as r
w = r.w


def _melos_seed():
    return w.rj(f"{w.seed_dir_for('melos')}/seed.json")


def test_melos_r0_byte_same():
    seed = _melos_seed()
    assert "source_essentials" not in seed
    assert r.build_r0_prompt_t2(seed) == r.ORIG["build_r0_prompt"](seed)


def test_melos_revise_byte_same():
    seed = _melos_seed()
    assert r.make_revise(seed)("BODY", "melos") == r.ORIG["build_revise_prompt"]("BODY", "melos")


def test_melos_std_byte_same():
    seed = _melos_seed()
    adv = "# T\n\nPara one.\n\nPara two."
    assert r.make_std(seed)(adv) == r.ORIG["build_std_prompt"](adv)


def test_open_window_t2_has_block_all_stages_and_override():
    seed = w.rj("docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/sftrial_seeds/t2/seed.json")
    p, _ = r.build_r0_prompt_t2(seed)
    rv = r.make_revise(seed)("BODY", "the_open_window")
    sd = r.make_std(seed)("# T\n\nA.\n\nB.")
    for t in (p, rv, sd):
        assert "[Must-keep -- story essentials]" in t and "keep the name Vera" in t
    assert "Only the main character (the protagonist) may be given a personal name." not in p
    assert "only Framton Nuttel may have a personal name" not in rv
    assert "closing line (the final reveal)" in sd
    assert "Not before the ending" in p and "Not before the ending" in rv and "Not before the ending" not in sd


def test_production_state_restored_after_calls():
    assert w.STD_PROMPT_TAIL == r.ORIG["STD_PROMPT_TAIL"] and w.R0_TEMPLATE == r.ORIG["R0_TEMPLATE"]


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("PASS", k)
