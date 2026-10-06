# -*- coding: utf-8 -*-
import hashlib
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_polysemy_nb_dev_01 as dev  # noqa: E402
import er019_family_x_storyline_b3_fact_selection_01 as b3  # noqa: E402

PROD = ["er003_v1_en_direct_vfl_01_generate.py", "er019_family_x_ja_writer_o_r1_r2_01.py",
        "er019_family_x_storyline_b3_fact_selection_01.py", "er019_family_x_entertainment_production_runner_01.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def test_a_import_leaves_original():
    assert b3.build_user_prompt.__name__ == "build_user_prompt"
    assert b3.build_user_prompt.__module__ == b3.__name__


def test_b_nb_appends_control_same():
    orig = b3.build_user_prompt
    base = orig("T", "LEDGER")
    with dev.patched_b3("nb", b3):
        assert b3.build_user_prompt("T", "LEDGER") == base + dev.SEP + dev.TRANSFER_BLOCK
    with dev.patched_b3("control", b3):
        assert b3.build_user_prompt("T", "LEDGER") == base


def test_c_restore_normal_and_exception():
    orig = b3.build_user_prompt
    with dev.patched_b3("nb", b3):
        assert b3.build_user_prompt is not orig
    assert b3.build_user_prompt is orig
    with pytest.raises(RuntimeError):
        with dev.patched_b3("nb", b3):
            raise RuntimeError("x")
    assert b3.build_user_prompt is orig


def test_d_production_sources_untouched():
    before = {p: sha(p) for p in PROD}
    with dev.patched_b3("nb", b3):
        pass
    assert before == {p: sha(p) for p in PROD}


def test_e_invalid_variant():
    with pytest.raises(ValueError):
        dev.resolve_variant({"OPEN233_B3_VARIANT": "bogus"})
    with pytest.raises(ValueError):
        with dev.patched_b3("bogus", b3):
            pass
    assert dev.resolve_variant({}) == "control"
    assert dev.resolve_variant({"OPEN233_B3_VARIANT": "nb"}) == "nb"


def test_f_existing_out_dir(tmp_path):
    with pytest.raises(SystemExit):
        dev.assert_fresh_out_dir(str(tmp_path), "phase1")
    with pytest.raises(SystemExit):
        dev.assert_fresh_out_dir(str(tmp_path), "phase2")


def test_g_dry_run_ledger_dest(tmp_path, monkeypatch, capsys):
    led = tmp_path / "l.txt"
    led.write_text("x", encoding="utf-8")
    out = "er052_output/open233_polysemy_trial_02/runs/_unit/nb/rep1"
    monkeypatch.setenv("OPEN233_B3_VARIANT", "nb")
    rc = dev.main(["--theme", "t", "--slug", "_unit", "--ledger-txt", str(led), "--out-dir", out, "--dry-run"])
    assert rc == 0
    assert dev.ledger_dest(out) == out + "/research_ledger/verified_fact_ledger.txt"
    assert "verified_fact_ledger.txt" in capsys.readouterr().out
    assert not os.path.exists(out)


def test_h_variant_dir_mismatch(tmp_path, monkeypatch):
    led = tmp_path / "l.txt"
    led.write_text("x", encoding="utf-8")
    monkeypatch.setenv("OPEN233_B3_VARIANT", "nb")
    with pytest.raises(SystemExit):
        dev.main(["--theme", "t", "--slug", "s", "--ledger-txt", str(led),
                  "--out-dir", "er052_output/open233_polysemy_trial_02/runs/s/control/rep1", "--dry-run"])


def test_i_runner_argv_stop_values():
    class A:
        theme = "t"; slug = "s"; out_dir = "o"; phase = "phase1"
    a = A()
    assert dev.build_runner_argv(a, 12)[-2:] == ["--stop-after", "writer"]
    a.phase = "phase2"
    assert dev.build_runner_argv(a, 10)[-2:] == ["--stop-after", "advanced"]


def test_j_note_prefix_env():
    assert dev.build_transfer_block({}) == dev.TRANSFER_BLOCK
    assert "『注意(多義):』" in dev.TRANSFER_BLOCK
    blk = dev.build_transfer_block({"OPEN233_NOTE_PREFIX": "注意(逆転):"})
    assert "『注意(逆転):』" in blk and "注意(多義):" not in blk
