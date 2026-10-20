# -*- coding: utf-8 -*-
"""er083_c1_positive_control_01_test_01.py  (API 0)  C1陽性対照Trial harness のtest。"""
import json
import os
import re
import subprocess
import tempfile

import pytest

import er083_b3_background_fact_trial_01_lib as lib
import er083_c1_positive_control_01_build_ledger as bl
import er083_c1_positive_control_01_eval as ev
import er083_c1_positive_control_01_run as run

ROOT = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(ROOT, "docs", "research", "FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01", "c1_posctrl_matrix_01.json")
NEW_FILES = ["er083_c1_positive_control_01_run.py", "er083_c1_positive_control_01_eval.py", "er083_c1_positive_control_01_build_ledger.py"]


def design():
    return json.loads(lib.read_text(DESIGN))


def ids_of(text):
    return lib.b3.extract_fact_ids_from_ledger(text)


def test_matrix_has_12_cells_and_expected_facts_exist_in_ledgers():
    d = design()
    cells = run.all_cells(d)
    assert len(cells) == 12 and d["theme_tag"] == "C1_POSCTRL_01"
    roles = {L["id"]: L["role"] for L in d["ledgers"]}
    assert sorted(roles.values()) == ["negative", "positive", "positive"]
    for L in d["ledgers"]:
        text = lib.read_text(os.path.join(ROOT, L["ledger_path"]))
        ids = set(ids_of(text))
        for f in L["expected_core"] + L["expected_ok"] + L["prior_baseline_selection"]:
            assert f in ids, (L["id"], f)
        if L["role"] == "negative":
            assert not L["expected_core"] and not L["expected_ok"]
        else:
            assert L["expected_core"]
            # 陽性対照: 期待Factは過去のBaseline採用に含まれない(通常のB3で選ばれない可能性)
            assert not set(L["expected_core"]) & set(L["prior_baseline_selection"])


def test_test_ledger_keeps_base_bytes_and_added_facts_are_documented_real_sources():
    meta = json.loads(lib.read_text(bl.OUT_JSON))
    assert meta["is_test_ledger"] is True and "test_origin" in meta and "禁止" in meta["production_use"]
    base = open(bl.BASE_LEDGER, "rb").read()
    new = open(bl.OUT_TXT, "rb").read()
    assert new.startswith(base)                                    # run_mey_01 の11件は無改変
    assert os.path.commonpath([os.path.abspath(bl.OUT_TXT), os.path.join(ROOT, "er019_output")]) != os.path.join(ROOT, "er019_output")
    text = lib.read_text(bl.OUT_TXT)
    assert ids_of(text) == [f"F{i:02d}" for i in range(1, 15)]
    assert lib.b3.verified_fact_ids(text) == ids_of(text)
    assert not text.lstrip().startswith("#")                       # B3 promptに混入するヘッダ無し
    assert len(meta["added_facts"]) == 3
    for f in meta["added_facts"]:
        assert f["verification"] == "VERIFIED" and f["verification_basis"]
        assert f["source_urls"] and all(u.startswith("https://") for u in f["source_urls"])
        assert f["quotes_original"]
        assert f["quote_check"] and all(c["found"] for c in f["quote_check"])   # 取得原文と逐語一致
    for sid, s in meta["sources"].items():
        assert s["http_status"] == 200 and s["fetched_at_utc"].startswith("2026-10-20") and s["publisher"]
    assert meta["expected_set"]["E_core"] == ["F12"]


def test_baseline_prompt_is_production_identical_and_c1_only_appends():
    d = design()
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "er083_output")) as td:
        for cell in [("PC1_hormuz", "baseline", 1), ("PC1_hormuz", "C1", 1)]:
            meta = run.run_cell(d, cell, td, 1e9, True)
            L = run.ledger_by_id(d, cell[0])
            prod = lib.b3.build_user_prompt(L["topic"], lib.read_text(os.path.join(ROOT, L["ledger_path"])))
            sha = meta["calls"][0]["user_prompt_sha256"]
            if cell[1] == "baseline":
                assert sha == lib.sha256_text(prod)                 # 追記なし=Productionとバイト同一
            else:
                assert sha == lib.sha256_text(prod + lib.CANDIDATE_NOTES["C1"])
            assert meta["theme_tag"] == "C1_POSCTRL_01"


def test_dry_run_all_cells_ok_api_zero_and_rules_sha_unchanged():
    d = design()
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "er083_output")) as td:
        rc = run.main(["--design", DESIGN, "--out", td, "--dry-run"])
        assert rc == 0
        s = json.loads(lib.read_text(os.path.join(td, "_dryrun", "run_summary.json")))
        assert len(s["results"]) == 12 and all(r["status"] == "OK" for r in s["results"])
        assert s["cost"]["real_api_calls"] == 0 and s["cost"]["total_jpy"] == 0.0 and s["cost"]["stub_calls"] == 12
        assert len({r["rules_sha256"] for r in s["results"]}) == 1      # V5(rules_sha256)不変
        assert s["plan"]["n_b3_calls"] == 12
        rows = [json.loads(l) for l in open(os.path.join(td, "cost_log_dryrun.jsonl"), encoding="utf-8")]
        assert rows and all(r["theme"] == "C1_POSCTRL_01" for r in rows)


def test_paid_run_refused_without_explicit_flag_and_budget():
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "er083_output")) as td:
        assert run.main(["--design", DESIGN, "--out", td]) == 4
        assert run.main(["--design", DESIGN, "--out", td, "--paid-run-approved-by-fable"]) == 4
        assert not os.listdir(td)                                        # 何も書かれていない(API 0)
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "er083_output")) as td:
        open(os.path.join(td, "STOP"), "w").close()
        assert run.main(["--design", DESIGN, "--out", td, "--dry-run"]) == 3


def test_no_env_switch_no_runner_import_and_production_unchanged():
    for fn in NEW_FILES:
        src = lib.read_text(os.path.join(ROOT, fn))
        body = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        assert "os.environ" not in body
        assert "getenv" not in body
        assert not re.search(r"^\s*(import|from)\s+er019_family_x_entertainment_production_runner", body, re.M)
    prod = ["er019_family_x_storyline_b3_fact_selection_01.py", "er019_family_x_entertainment_production_runner_01.py",
            "er053_b3_deterministic_producer_01.py", "er053_family_x_factlock_ja_writer_01.py", "er053_b3_annotation_contract_01.py"]
    r = subprocess.run(["git", "diff", "--stat", "HEAD", "--"] + prod, cwd=ROOT, capture_output=True, text=True)
    assert r.stdout.strip() == ""
    assert not any(v for v in lib.generalization_report().values())     # 候補文に固有事例/Fact ID無し(仕様文不変)


def _row(ledger, cond, sample, selected, supp=(), min2_only=False):
    return {"_ledger": ledger, "_cond": cond, "_sample": sample, "_dir": "none", "status": "OK", "producer": {},
            "analysis": {"selected_fact_ids": list(selected), "supplement_fact_ids": list(supp), "n_selected": len(selected),
                         "min2_met_only_via_supplement": min2_only, "background_confirm_note": None}}


POS = {"id": "P", "role": "positive", "expected_core": ["X"], "expected_ok": ["Y"], "prior_baseline_selection": ["A", "B"]}
NEG = {"id": "N", "role": "negative", "expected_core": [], "expected_ok": [], "prior_baseline_selection": ["A", "B"]}


def _rows(ledger, base, c1):
    out = [_row(ledger, "baseline", i + 1, s) for i, s in enumerate(base)]
    out += [_row(ledger, "C1", i + 1, s, supp=[x for x in s if x not in ("A", "B")]) for i, s in enumerate(c1)]
    return out


def test_judge_positive_verdicts():
    assert ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B", "X"]] * 2))["verdict"] == "POS_ADDED_2of2"
    assert ev.judge_ledger(POS, _rows("P", [["A", "X"]] * 2, [["A", "X"]] * 2))["verdict"] == "NONDISCRIMINATING"
    assert ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B"]] * 2))["verdict"] == "POS_NOT_ADDED"
    assert ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B", "X"], ["A", "B"]]))["verdict"] == "POS_PARTIAL"
    assert ev.judge_ledger(POS, _rows("P", [["A", "B"]], [["A", "B", "X"]] * 2))["verdict"] == "POS_ADDED_2of2"   # baseline 1 sampleでもhit無し


def test_judge_flags_extras_unmarked_and_min2_only():
    j = ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B", "X", "Z"]] * 2))
    assert j["extras_total"] == 2 and j["verdict"] == "POS_ADDED_2of2"          # 期待外Z(各sample)を数える
    rows = _rows("P", [["A", "B"]] * 2, [["A", "B", "X"]] * 2)
    for r in rows:
        if r["_cond"] == "C1":
            r["analysis"]["supplement_fact_ids"] = []                            # マーカー無しの追加
    assert "CORE_ADDED_WITHOUT_MARKER" in ev.judge_ledger(POS, rows)["flags"]
    rows = _rows("P", [["A", "B"]] * 2, [["A", "B", "X"]] * 2)
    rows[2]["analysis"]["min2_met_only_via_supplement"] = True
    assert "MIN2_ONLY_VIA_SUPPLEMENT" in ev.judge_ledger(POS, rows)["flags"]


def test_judge_negative_and_overall_never_validates_zero_additions():
    assert ev.judge_ledger(NEG, _rows("N", [["A", "B"]] * 2, [["A", "B"]] * 2))["verdict"] == "NEG_PASS"
    assert ev.judge_ledger(NEG, _rows("N", [["A", "B"]] * 2, [["A", "B", "Z"]] * 2))["verdict"] == "NEG_FAIL"
    # 『追加しなかった』結果を成功扱いしない: 陽性で全く追加しない=REJECTED候補。VALIDATEDにならない
    pj = ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B"]] * 2))
    nj = ev.judge_ledger(NEG, _rows("N", [["A", "B"]] * 2, [["A", "B"]] * 2))
    assert ev.overall([pj, nj])["label"] == "REJECTED_CANDIDATE_MACHINE"
    good = ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B", "X"]] * 2))
    assert ev.overall([good, nj])["label"] == "VALIDATED_CANDIDATE_MACHINE"
    assert ev.overall([good, ev.judge_ledger(NEG, _rows("N", [["A", "B"]] * 2, [["A", "B", "Z"]] * 2))])["label"] == "REJECTED_CANDIDATE_MACHINE"
    part = ev.judge_ledger(POS, _rows("P", [["A", "B"]] * 2, [["A", "B", "X"], ["A", "B"]]))
    assert ev.overall([part, nj])["label"] == "MIXED_NEEDS_FABLE_REPLAN"
    nd = ev.judge_ledger(POS, _rows("P", [["A", "X"]] * 2, [["A", "X"]] * 2))
    assert ev.overall([nd, nj])["label"] == "MIXED_NEEDS_FABLE_REPLAN"


def test_eval_on_dry_run_traces_writer_path_deterministically():
    d = design()
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "er083_output")) as td:
        assert run.main(["--design", DESIGN, "--out", td, "--dry-run"]) == 0
        assert ev.main(["--design", DESIGN, "--out-root", td, "--dry-run"]) == 0
        res = json.loads(lib.read_text(os.path.join(td, "_dryrun", "c1_posctrl_eval.json")))
        assert res["n_cells"] == 12
        pos = [j for j in res["judged"] if j["role"] == "positive"]
        for j in pos:
            for p in j["c1"]:
                for f, t in p["trace"].items():
                    assert t["in_selected"] and t["in_sidecar_facts"] and t["contract_v1_v10"] == "PASS" and t["rules_sha256_unchanged"]
        assert "DRY-RUN" in res["overall"]["note"] and "機械判定のみ" in res["overall"]["note"]


def test_overall_excludes_nondiscriminating_positive_but_needs_one_discriminating_success():
    nd = ev.judge_ledger(POS, _rows("P", [["A", "X"]] * 2, [["A", "X"]] * 2))
    good = dict(ev.judge_ledger(dict(POS, id="P2"), _rows("P2", [["A", "B"]] * 2, [["A", "B", "X"]] * 2)))
    nj = ev.judge_ledger(NEG, _rows("N", [["A", "B"]] * 2, [["A", "B"]] * 2))
    assert ev.overall([nd, good, nj])["label"] == "VALIDATED_CANDIDATE_MACHINE"
    none = ev.judge_ledger(dict(POS, id="P3"), _rows("P3", [["A", "B"]] * 2, [["A", "B"]] * 2))
    assert ev.overall([nd, none, nj])["label"] == "REJECTED_CANDIDATE_MACHINE"     # 判別可能な陽性が全て追加0
