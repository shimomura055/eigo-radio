# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_test_02.py
委任_02(2026-10-19)追加test: Opus独立レビューI 必須修正 M1〜M5 のharness反映の検証。API 0。
M1=実cost logger経由の行が集計される / M2=core・補完のみで下限充足 / M3=盲検パックにFact ID・候補名なし
M4=C3/C1文言+一般化維持 / M5=--sample・複数sample eval・事前固定判定規則。
"""
import json
import os
import re
import shutil

import pytest

import er005_cost_logger as cl_mod
import er006_model_routing_contract_01 as routing
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er083_b3_background_fact_trial_01_eval as ev_mod
import er083_b3_background_fact_trial_01_lib as lib
import er083_b3_background_fact_trial_01_run as run_mod
from er083_b3_background_fact_trial_01_test_01 import RUN, THEME, _ScriptedClient, _ledger, _run, _stored

pytestmark = pytest.mark.skipif(not os.path.isdir(RUN), reason="run_mey_01 not present")
B3_MODEL = routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"]


# ---- M1 -----------------------------------------------------------------------------
def test_m1_real_cost_logger_rows_with_overridden_inner_theme_are_counted(tmp_path, monkeypatch):
    log = str(tmp_path / "cost_log.jsonl")
    monkeypatch.setattr(cl_mod, "_LOG_PATH", log)
    monkeypatch.setattr(cl_mod, "_CONTEXT", {"theme": None, "stage": None, "segment": None})
    # 外側=Trial theme、内側=Production B3 _call_once が設定する b3.THEME_TAG(上書き)。stubでthemeを直接書かず、実loggerのrecordを通す
    with cl_mod.logging_context(lib.THEME_TAG, "b3_C1"):
        with cl_mod.logging_context(b3.THEME_TAG, "storyline_b3"):
            cl_mod.record({"provider": "openai", "api": "responses.create", "model_id": B3_MODEL, "success": True,
                           "input_tokens": 12000, "output_tokens": 6000, "usage_source": "OFFICIAL_API_RESPONSE"})
    rows = [json.loads(x) for x in open(log, encoding="utf-8")]
    assert rows[0]["theme"] == b3.THEME_TAG != lib.THEME_TAG          # 外側themeが上書きされることを実loggerで再現
    cs = lib.cost_summary(log)
    assert cs["real_api_calls"] == 1 and cs["total_jpy"] > 0, cs       # 旧実装(TRIAL_THEMES絞込)なら0円
    g = lib.BudgetGuard(log, cs["total_jpy"] + 0.1, 7.6, dry_run=False)
    with pytest.raises(lib.BudgetStop):                                 # BudgetGuardが実費を数えて止まる
        g.check("x")


def test_m1_cost_summary_tree_aggregates_per_run_logs_and_excludes_dryrun(tmp_path):
    for cand, tag in (("C1", "s1"), ("C3", "s2")):
        lib.append_jsonl(str(tmp_path / "art" / cand / tag / "cost_log.jsonl"),
                         {"theme": b3.THEME_TAG, "stage": "storyline_b3", "provider": "openai", "model_id": B3_MODEL,
                          "success": True, "input_tokens": 10000, "output_tokens": 5000})
    lib.append_jsonl(str(tmp_path / "cost_log_dryrun.jsonl"), {"theme": lib.THEME_TAG, "dry_run_stub": True})
    t = lib.cost_summary_tree(str(tmp_path))
    assert t["real_api_calls"] == 2 and len(t["per_log"]) == 2 and t["total_jpy"] > 0


# ---- M2 -----------------------------------------------------------------------------
def _parsed(sel, supp):
    st = _stored()
    return {"selected_storyline": "s", "selected_fact_ids": list(sel), "recheck_note": None,
            "fact_tests": [dict(ft, decision="selected" if ft["fact_id"] in sel else "excluded",
                                reason=(lib.SUPP_PREFIX + "x") if ft["fact_id"] in supp else ft["reason"]) for ft in st["fact_tests"]]}


def test_m2_core_ids_and_min2_met_only_via_supplement():
    a = lib.analyze_selection(_parsed(["F11", "F01"], ["F01"]), _ledger(), ["F04", "F11"])
    assert a["min2_satisfied"] is True and a["core_selected_ids"] == ["F11"] and a["core_verified_n"] == 1
    assert a["min2_met_only_via_supplement"] is True
    b = lib.analyze_selection(_parsed(["F04", "F11", "F01"], ["F01"]), _ledger(), ["F04", "F11"])
    assert b["core_selected_ids"] == ["F04", "F11"] and b["min2_met_only_via_supplement"] is False
    c = lib.analyze_selection(_parsed(["F04", "F11"], []), _ledger(), ["F04", "F11"])
    assert c["min2_met_only_via_supplement"] is False


def test_m2_guard_sentence_in_all_candidates_and_final_call_recorded(tmp_path):
    for c in ("C1", "C2", "C3"):
        assert "最低2件』に数えません" in lib.CANDIDATE_NOTES[c]
    meta, _, _ = _run(tmp_path, "C1")
    assert meta["final_result_call"] == "initial"
    meta2, _, _ = _run(tmp_path / "x", "C1", client=_ScriptedClient())
    assert meta2["final_result_call"] == "reeval"


# ---- M4 -----------------------------------------------------------------------------
def test_m4_wording_present_and_still_generalized():
    c3, c1 = lib.CANDIDATE_NOTES["C3"], lib.CANDIDATE_NOTES["C1"]
    assert "「もっと知りたい」" in c3
    assert "状況や経緯を述べるFactは「なぜ」への回答になりません" in c3
    for note in (c1, c3):
        assert "部分的に示されている前提は、欠落とみなしません" in note and "判定に迷う場合は、追加しません" in note
    assert "判定に迷う場合は、追加しません" not in lib.CANDIDATE_NOTES["C2"]
    assert lib.generalization_report() == {"baseline": [], "C1": [], "C2": [], "C3": []}


# ---- M5 -----------------------------------------------------------------------------
def test_m5_run_cli_sample_dirs_do_not_overwrite(tmp_path):
    out_root = str(tmp_path / "root")
    ledger_p = os.path.join(RUN, "research_ledger", "verified_fact_ledger.txt")
    for n in (1, 2):
        rc = run_mod.main(["--article", "art", "--ledger", ledger_p, "--theme", THEME, "--candidate", "baseline", "--sample", str(n),
                           "--out-root", out_root, "--budget-jpy", "0", "--dry-run"])
        assert rc == 0
    for n in (1, 2):
        assert os.path.isfile(os.path.join(out_root, "_dryrun", "art", "baseline", f"s{n}", "trial_meta.json"))
    rows = ev_mod.collect(out_root, "art", dry_run=True)
    assert [r["_label"] for r in rows][1:] == ["baseline_rerun/s1", "baseline_rerun/s2"]


def _stage_samples(tmp_path, spec):
    """spec: [(cand, n)] を dry-run で生成し <tmp>/rootX/art/<cand>/s<n> へ集める。"""
    dst_root = tmp_path / "rootX"
    for cand, n in spec:
        meta, _, _ = _run(tmp_path / f"{cand}{n}", cand)
        shutil.copytree(str(tmp_path / f"{cand}{n}" / "root" / "art" / cand / "s1"), str(dst_root / "art" / cand / f"s{n}"))
    return str(dst_root)


def test_m5_sample_consistency_rule_and_core_number_diff(tmp_path):
    root = _stage_samples(tmp_path, [("baseline", 1), ("baseline", 2), ("C1", 1), ("C1", 2)])
    rows = ev_mod.collect(root, "art", dry_run=False)
    sc = ev_mod.sample_consistency(rows)
    assert sc["C1"]["n_samples"] == 2 and sc["C1"]["consistent"] is True and sc["C1"]["outside_baseline_observed_range"] is True
    assert "補助指示の効果とみなす" in sc["C1"]["judgement"]
    assert sc["baseline"]["judgement"].startswith("Baseline自身")
    diffs = ev_mod.core_number_diffs(rows)
    assert len(diffs) == 4 and all(isinstance(d["added_vs_production_baseline"], list) for d in diffs)
    rows1 = [r for r in rows if r["_label"] != "C1/s2"]
    assert "判定不能" in ev_mod.sample_consistency(rows1)["C1"]["judgement"]


def test_m5_inconsistent_or_in_baseline_range_is_not_effect(tmp_path):
    root = _stage_samples(tmp_path, [("baseline", 1), ("C1", 1), ("C1", 2)])
    # C1/s2 を Baseline と同じ採用(補完なし)へ書換え -> 不一貫
    mp = os.path.join(root, "art", "C1", "s2", "trial_meta.json")
    m = json.loads(open(mp, encoding="utf-8").read())
    m["analysis"]["supplement_fact_ids"], m["analysis"]["core_selected_ids"], m["analysis"]["selected_fact_ids"] = [], ["F04", "F11"], ["F04", "F11"]
    open(mp, "w", encoding="utf-8").write(json.dumps(m, ensure_ascii=False))
    sc = ev_mod.sample_consistency(ev_mod.collect(root, "art", dry_run=False))
    assert sc["C1"]["consistent"] is False and "効果とはみなさない" in sc["C1"]["judgement"]


# ---- M3 -----------------------------------------------------------------------------
def test_m3_blind_pack_has_no_fact_ids_or_candidate_names(tmp_path):
    root = _stage_samples(tmp_path, [("baseline", 1), ("C1", 1), ("C3", 1)])
    rows = ev_mod.collect(root, "art", dry_run=False)
    ev_mod.blind_pack(rows, root, str(tmp_path / "pack.md"))
    pack = open(str(tmp_path / "pack.md"), encoding="utf-8").read()
    assert not re.search(r"(?<![A-Za-z0-9])F[0-9]{2}(?![0-9])", pack), "Fact ID leak"
    assert "C1" not in pack and "C3" not in pack and "baseline" not in pack and "採用Factの内容要約" in pack
    assert "採用Fact:" not in pack
    assert os.path.isfile(os.path.join(root, "blind_key.json"))
