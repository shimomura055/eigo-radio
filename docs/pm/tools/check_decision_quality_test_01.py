"""check_decision_quality.py のpytest(正例=検出すべき/負例=検出しない、各4点以上)。

実行: .venv\\Scripts\\python.exe -m pytest docs/pm/tools/check_decision_quality_test_01.py -q
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_decision_quality as cdq  # noqa: E402


def run(packet, acceptance=None, register=None, mid=None, decided=()):
    return cdq.run_check(packet, acceptance, register, mid, set(decided))


def checks(res, level=None):
    return [f["check"] for f in res["findings"] if level is None or f["level"] == level]


# ---------------- 正例(検出すべき) ----------------
def test_pos_c1_severe_not_in_fix_or_stop():
    r = run("判定整合: 重大NG=[NG-1,NG-2] / 主因=[NG-1] / 是正対象=[NG-1] / STOP理由=[なし] / 提示=不可\n")
    c1 = [f for f in r["findings"] if f["check"] == "C1"]
    assert len(c1) == 1 and "NG-2" in c1[0]["message"]


def test_pos_c2_accepted_with_severe():
    r = run("最終受入判定: ACCEPTED\n判定整合: 重大NG=[NG-1] / 主因=[NG-1] / 是正対象=[NG-1] / STOP理由=[なし] / 提示=不可\n")
    assert "C2" in checks(r)


def test_pos_c2_main_cause_not_severe_and_present_ok():
    r = run("判定整合: 重大NG=[NG-1] / 主因=[X-9] / 是正対象=[NG-1] / STOP理由=[なし] / 提示=可\n")
    msgs = " ".join(f["message"] for f in r["findings"] if f["check"] == "C2")
    assert "主因" in msgs and "提示=可" in msgs


def test_pos_c2_unstructured_severe_with_accepted():
    r = run("(4)Fact保持=不一致(MAJOR意味反転)\n(5)最終受入判定: ACCEPTED\n")
    assert "C2" in checks(r)


def test_pos_c3_decided_number_reissued_as_udr():
    r = run("ユーザー判断が必要: REGISTER #88 の採否\n")
    assert [f["number"] for f in r["findings"] if f["check"] == "C3"] == [88]


def test_pos_c3_register_decided_via_register_text():
    reg = "- #120=**判断済み**(テスト)\n"
    r = run("USER_DECISION_REQUIRED: #120 を再確認したい\n", register=reg)
    assert 120 in [f.get("number") for f in r["findings"]]


def test_pos_c4_family_abc_in_decision_section():
    r = run("## ユーザー判断が必要なこと\n- Family C の再利用保証を決めたい\n\n## 補足\n- 別\n")
    assert "C4" in checks(r, "warn")


def test_pos_c4_open_list_and_other_managed_id():
    pk = "管理ID: `MY-TASK-ID-01`\n判断候補: OPEN-1, OPEN-2, OPEN-3 と OTHER-LONG-TASK-ID-01 の件\n"
    r = run(pk)
    msgs = " ".join(f["message"] for f in r["findings"] if f["check"] == "C4")
    assert "OPEN番号" in msgs and "管理ID" in msgs


def test_pos_c1_missing_line_with_acceptance_form_is_warn():
    r = run("受入記録:\n(4)Fact保持=不一致(MAJOR意味反転)\n(5)最終受入判定: NOT ACCEPTED\n")
    assert [(f["check"], f["level"]) for f in r["findings"]] == [("C1", "warn")]


# ---------------- 負例(検出しない) ----------------
def test_neg_covered_severe_not_accepted():
    r = run("最終受入判定: NOT ACCEPTED\n判定整合: 重大NG=[NG-1] / 主因=[NG-1] / 是正対象=[NG-1] / STOP理由=[なし] / 提示=不可\n")
    assert r["findings"] == [] and r["status"] == "OK"


def test_neg_normal_case_one_line():
    r = run("判定: ACCEPTED\n判定整合: 重大NG=なし\n")
    assert r["findings"] == []


def test_neg_accepted_fuka_wording_not_counted():
    r = run("重大NGがある場合はACCEPTED不可。最終受入判定: 条件付き差戻し\n判定整合: 重大NG=[NG-1] / 主因=[NG-1] / 是正対象=[NG-1] / STOP理由=[NG-1] / 提示=証拠のみ\n")
    assert r["findings"] == []


def test_neg_decided_number_cited_as_already_decided():
    r = run("USER_DECISION_REQUIRED には出さない: #88 は判断済み(再質問しない)\n")
    assert "C3" not in checks(r)


def test_neg_undecided_number_and_family_xz():
    r = run("判断候補: #300 の採否\n## ユーザー判断\n- Family X の配線範囲\n- Family Z は維持\n")
    assert r["findings"] == []


def test_neg_severe_token_with_negation_and_definition_text():
    r = run("(4)重大NGなし。意味反転は検出されなかった。\n最終受入判定: ACCEPTED\n")
    assert r["findings"] == []


def test_neg_family_abc_outside_decision_section():
    r = run("## 補足\n- Family C は開発停止(27-7)\n")
    assert "C4" not in checks(r)


def test_cli_always_exit0_and_json(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("ユーザー判断が必要: #88\n", encoding="utf-8")
    out = tmp_path / "o.json"
    rc = subprocess.run([sys.executable, str(Path(cdq.__file__)), "--packet", str(p), "--json-out", str(out)],
                        capture_output=True).returncode
    assert rc == 0 and json.loads(out.read_text(encoding="utf-8"))["non_blocking"] is True
    rc2 = subprocess.run([sys.executable, str(Path(cdq.__file__)), "--packet", str(tmp_path / "none.md")],
                         capture_output=True).returncode
    assert rc2 == 0
