# -*- coding: utf-8 -*-
"""委任_07 Trial module(er112_kp_gm_trial_02)の決定論test。API 0。Production module不変(import時副作用なし)。"""
import hashlib, subprocess
from pathlib import Path
import er112_kp_gm_trial_02 as T
import er019_family_x_kp_explanation_01 as kx

ROOT = Path(__file__).resolve().parent
KP = dict(key="draw a line", display="draw that line", sent="The words draw that line simply")


def test_e1_removes_gloss_row_and_reference_rule():
    m = T.expl_message("E1", KP, "一線を引く")
    assert "japanese" not in m.lower() and "一線" not in m
    assert 'phrase: "draw a line"' in m and "The words draw that line simply" in m
    assert "The explanation should still make sense" in m          # 承認済みB仕様の他の規則は維持


def test_e0_is_production_message_byte_identical():
    m = T.expl_message("E0", KP, "一線を引く")
    assert m == kx.build_explanation_user_message([{"display_phrase": "draw a line", "source_sentence": KP["sent"], "japanese_gloss": "一線を引く"}])


def test_e4_and_e1c_add_one_rule_and_schema_order():
    m4, mc = T.expl_message("E4", KP, "x"), T.expl_message("E1c", KP, "x")
    assert "usage_type" in m4 and "usage_type" not in mc and "core_sense" in mc
    k4 = list(T.expl_schema("E4")["schema"]["properties"]["explanations"]["items"]["properties"])
    assert k4 == ["phrase", "usage_type", "core_sense", "english_explanation"]
    kc = list(T.expl_schema("E1c")["schema"]["properties"]["explanations"]["items"]["properties"])
    assert kc == ["phrase", "core_sense", "english_explanation"]


def test_kpset_size_and_hard20():
    A = T.kpset()
    assert len(A) >= 75 and sum(1 for v in A.values() if v["tier"] == "hard") == 20


def test_production_unchanged_vs_head():
    files = ["er019_family_x_kp_explanation_01.py", "er003_key_words_gloss_alignment.py", "er019_family_x_audio_production_runner_01.py",
             "er026_family_z_fiction_production_runner_01.py"]
    out = subprocess.run(["git", "status", "--porcelain", "--"] + files, cwd=ROOT, capture_output=True, text=True).stdout
    assert out.strip() == ""
