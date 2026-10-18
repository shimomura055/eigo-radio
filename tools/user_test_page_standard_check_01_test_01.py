# -*- coding: utf-8 -*-
"""ユーザー試聴ページ標準適合check(X/Z/Y共通)のRegression。API呼出なし。
(1) ユーザー受入済みXページ(BAPE=Std+Adv / Coffee S3prod=Stdのみ)がPASS(Family X側ページは不変のまま標準に適合)
(2) Zの現行ページ(user_test/family_z_melos_02/index.html)がPASS
(3) 違反fixture(旧Z index=リンク+ASR警告中心 / 通し再生なし / 内部情報混入 / ASR警告が先頭 等)がFAIL
実行: .venv/Scripts/python.exe -I -m pytest tools/user_test_page_standard_check_01_test_01.py -q"""
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import er_user_listening_page_common_01 as uc  # noqa: E402

BAPE = os.path.join(ROOT, "user_test", "boredom_aggression_bape_e2e_01", "index.html")
COFFEE = os.path.join(ROOT, "user_test", "coffee_fxpw_e2e_01_s3prod", "index.html")
Z = os.path.join(ROOT, "user_test", "family_z_melos_02", "index.html")


def _rows(n=6):
    return [{"part": p, "start": float(i * 10), "dur": 5.0, "src": f"a{i}.mp3", "blocks": [uc.script_block(t)]}
            for i, (p, t) in enumerate([("Preview", "p text"), ("Comment 1", "c text"), ("Full Story Part 1", "s text"),
                                        ("Comment 2", "c2"), ("Full Story Part 2", "s2"), ("Comment 3", "c3")][:n])]


def _kp_rows():
    return [{"part": f"Key Phrase {i}", "start": float(100 + i), "dur": 3.0, "src": f"k{i}.mp3",
             "blocks": [uc.kp_block(["英語", "日本語の意味"], [f"phrase{i}", "意味です"])]} for i in range(1, 4)]


def _page(rows_std=None, aux_first=False, full_src="full.mp3", sort=True):
    rows = (rows_std or _rows()) + _kp_rows()
    if sort:
        rows.sort(key=lambda r: r["start"])
    lv = [{"id": "std", "label": "Standard", "full_src": full_src, "duration": 200, "rows": rows},
          {"id": "adv", "label": "Advanced", "full_src": full_src, "duration": 200, "rows": rows}]
    aux = "<h2 id='pww'>事後試聴リスト(PASS_WITH_WARNING)</h2><p>0件</p>"
    html = uc.render_standard_page("t", lv, aux_html="" if aux_first else aux)
    if aux_first:
        html = html.replace("<nav>", aux + "<nav>", 1)
    return html


def test_builder_output_passes():
    assert uc.check_page(_page())["overall"] == "PASS"


@pytest.mark.parametrize("path,levels", [(BAPE, ("Standard", "Advanced")), (COFFEE, ("Standard",)), (Z, ("Standard", "Advanced"))])
def test_accepted_x_pages_and_z_page_pass(path, levels):
    r = uc.check_file(path, levels=levels)
    assert r["overall"] == "PASS", {k: v for k, v in r["checks"].items() if not v["ok"]}


def test_old_z_index_link_and_asr_list_only_fails():
    old = ("<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>走れメロス 試聴</title></head><body>"
           "<h1>走れメロス 試聴</h1><ul><li><a href='standard.html'>Standard</a></li><li><a href='advanced.html'>Advanced</a></li></ul>"
           "<h2>Standard</h2><section id=\"pass-with-warning-listening-list\"><h2>事後試聴リスト(PASS_WITH_WARNING)</h2>"
           "<table><tr><td>x</td></tr></table></section><h2>Advanced</h2></body></html>")
    r = uc.check_page(old)
    assert r["overall"] == "FAIL"
    assert not r["checks"]["Standard:full_play_audio"]["ok"]
    assert not r["checks"]["Standard:script_rows_in_play_order"]["ok"]
    assert not r["checks"]["Standard:key_phrases_en_ja"]["ok"]


def test_no_full_play_audio_fails():
    html = _page().replace("id='main_std' controls", "id='main_std'")
    r = uc.check_page(html)
    assert not r["checks"]["Standard:full_play_audio"]["ok"]


def test_internal_info_in_script_fails():
    for leak in ("Voice: Aoede / Style: S3", "(音楽・通知音。読み上げなし)", "base_sha 9d905cfe6c04", "6%減速適用"):
        rows = _rows()
        rows[0]["blocks"] = [uc.script_block(leak)]
        r = uc.check_page(_page(rows_std=rows))
        assert not r["checks"]["Standard:no_internal_info_in_script"]["ok"], leak


def test_sfx_row_with_script_and_raw_id_label_fail():
    rows = _rows() + [{"part": "Notification 1", "start": 5.5, "dur": 2.0, "src": "n.mp3", "blocks": [uc.script_block("(通知音)")]}]
    assert not uc.check_page(_page(rows_std=rows))["checks"]["Standard:no_internal_info_in_script"]["ok"]
    rows = _rows()
    rows[2]["part"] = "full_story_part1_c1"
    assert not uc.check_page(_page(rows_std=rows))["checks"]["Standard:no_internal_info_in_script"]["ok"]


def test_play_order_violation_fails():
    rows = _rows()
    rows[1]["start"] = 999.0
    assert not uc.check_page(_page(rows_std=rows, sort=False))["checks"]["Standard:script_rows_in_play_order"]["ok"]


def test_asr_warning_before_levels_fails():
    r = uc.check_page(_page(aux_first=True))
    assert not r["checks"]["asr_warning_is_auxiliary_after_levels"]["ok"]


def test_kp_without_japanese_meaning_fails_for_standard():
    rows = _rows() + [{"part": f"Key Phrase {i}", "start": float(100 + i), "dur": 3.0, "src": "k.mp3",
                       "blocks": [uc.kp_block(["英語", "意味"], [f"p{i}", "meaning only english"])]} for i in range(1, 4)]
    lv = [{"id": "std", "label": "Standard", "full_src": "f.mp3", "duration": 100, "rows": rows}]
    r = uc.check_page(uc.render_standard_page("t", lv), levels=("Standard",))
    assert not r["checks"]["Standard:key_phrases_en_ja"]["ok"]


def test_cli_exit_code(tmp_path):
    import subprocess
    out = tmp_path / "o.json"
    cmd = [sys.executable, "-I", os.path.join(ROOT, "tools", "user_test_page_standard_check_01.py"), "--page", BAPE, "--out", str(out)]
    assert subprocess.run(cmd, capture_output=True).returncode == 0
    assert out.exists()
    bad = tmp_path / "bad.html"
    bad.write_text("<html><body><h2>Standard</h2></body></html>", encoding="utf-8")
    cmd[cmd.index(BAPE)] = str(bad)
    assert subprocess.run(cmd, capture_output=True).returncode == 1
