# -*- coding: utf-8 -*-
"""fz_essence_dev_runner_01 のDefaultOffIsolation型test(API 0)。実行: .venv\\Scripts\\python.exe -m pytest <this file> -q"""
import os, sys, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pytest                              # noqa: E402
try:
    import fz_essence_dev_runner_01 as r  # noqa: E402  (chdir to ROOT)
except SystemExit as _e:                  # 案A昇格後は歴史的runnerがimport時に停止する(fail-fast guard、Opus必須修正5)
    pytest.skip("歴史的DEV runner(案A昇格済み): 本体への移植先=er062_family_z_source_essentials_test_01.py(narration系test)。理由: " + str(_e)[:80],
                allow_module_level=True)
import er062_family_z_writer_01 as w      # noqa: E402

PROD = "er026_output/family_z_production_e2e_01"
R0 = f"{PROD}/the_tell_tale_heart/run_sf_prod_01/writer/r0.md"
SEEDS = sorted(p.replace("\\", "/") for p in glob.glob(f"{PROD}/*/seed/seed.json"))
DEV_SEED = json.load(open(f"{r.DEV_SEED_TTH}/seed.json", encoding="utf-8"))


def _prod_ess(path):
    return json.load(open(path, encoding="utf-8")).get("source_essentials")


def teardown_function(_f):
    r.uninstall()


def test_no_voice_render_byte_identical_for_all_production_seeds():
    n = 0
    for p in SEEDS:
        ess = _prod_ess(p)
        if not ess:
            continue
        assert "narration_voice" not in ess, p
        for mode in ("full", "std"):
            assert r.render_dev(ess, mode) == r.ORIG["_render_essentials_block"](ess, mode)
        n += 1
    assert n >= 4


def test_arm_i_equals_production_r1_prompt_file():
    seed = json.load(open(f"{PROD}/the_tell_tale_heart/seed/seed.json", encoding="utf-8"))
    r.install("i")
    p = w.build_revise_prompt(w.rd(R0), "the_tell_tale_heart", essentials=w.build_essentials(seed))
    r.uninstall()
    ref = w.rd(f"{PROD}/the_tell_tale_heart/run_sf_prod_01/writer/r1_prompt.txt")
    assert p.strip() == ref.strip()


def test_arm_iii_on_seed_without_voice_equals_current_prompt():
    for p in SEEDS:
        ess_d = _prod_ess(p)
        if not ess_d:
            continue
        slug = p.split("/")[-3]
        if slug not in w.STORY_MAIN_CHARACTER:
            continue
        seed = json.load(open(p, encoding="utf-8"))
        ess = w.build_essentials(seed)
        base = w.build_revise_prompt("BODY", slug, essentials=ess)
        r.install("iii")
        got = w.build_revise_prompt("BODY", slug, essentials=w.build_essentials(seed))
        r.uninstall()
        assert got == base, slug
        assert "in third person" in got


def test_arm_ii_differs_only_in_phrase():
    seed = json.load(open(f"{PROD}/the_tell_tale_heart/seed/seed.json", encoding="utf-8"))
    base = w.build_revise_prompt("BODY", "the_tell_tale_heart", essentials=w.build_essentials(seed))
    r.install("ii")
    got = w.build_revise_prompt("BODY", "the_tell_tale_heart", essentials=w.build_essentials(seed))
    r.uninstall()
    assert got == base.replace(r.THIRD, r.REV_II, 1) and got != base


def test_arm_iii_with_voice_places_narration_before_key_people_in_full_and_std():
    r.install("iii")
    ess = w.build_essentials(DEV_SEED)
    for blk in (ess.block_full, ess.block_std):
        assert blk.index("- Narration:") < blk.index("- Key people:")
        assert "wording, length and sentence structure may change" in blk
        assert "exactly" not in blk.split("- Narration:")[1].split("\n")[0]
        assert "as in the original" not in blk.split("- Narration:")[1].split("\n")[0]
        assert "third person" not in blk.split("- Narration:")[1].split("\n")[0]
    p = w.build_revise_prompt("BODY", "the_tell_tale_heart", essentials=ess)
    r.uninstall()
    assert "in third person" not in p and r.REV_III in p
    assert "do not retell" not in json.dumps(DEV_SEED)          # 必須修正2: 作品別の禁止文をSeedへ入れない


def test_dev_seed_free_to_cut_does_not_swallow_voice_carrier():
    ftc = " ".join(DEV_SEED["source_essentials"]["free_to_cut"])
    assert "repetitions of the narrator's arguments that he is wise and cunning" in ftc
    assert "the narrator's repeated arguments" not in ftc
    assert "keep 1" not in DEV_SEED["source_essentials"]["narration_voice"].lower()   # 内容ノルマを入れない


def test_uninstall_restores_originals():
    r.install("iii")
    r.uninstall()
    assert w._render_essentials_block is r.ORIG["_render_essentials_block"]
    assert w.build_revise_prompt is r.ORIG["build_revise_prompt"]
    assert w.REVISE_USER_TMPL == r.ORIG["REVISE_USER_TMPL"]


def test_out_root_is_dev_only():
    assert r.OUT_ROOT.startswith("er026_output/family_z_dev_trials/")
    assert not r.OUT_ROOT.startswith(r.PROD_RUN_ROOT)
