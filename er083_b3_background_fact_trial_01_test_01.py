# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_test_01.py
B3背景Fact補完Trial harness(Trial専用)のtest。API 0(StubClientのみ)。
目的: (1)Baseline=現行Production選定を再現する構成(同Prompt・同sha・同model/effort/schema、成果物byte同一) (2)候補はProduction Promptへの追記のみ
(3)仕様文に固有事例/Fact IDが無い (4)Production module不変 (5)下限2件の再評価はProduction経路に委ねられる (6)出力先guard・予算guard。
"""
import json
import os
import subprocess
import types

import pytest

import er006_model_routing_contract_01 as routing
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er083_b3_background_fact_trial_01_lib as lib
import er083_b3_background_fact_trial_01_eval as ev_mod
import er083_b3_background_fact_trial_01_writer_probe as probe

RUN = lib.PRODUCTION_MEY_RUN
THEME = "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く"
PROD_FILES = ["er019_family_x_storyline_b3_fact_selection_01.py", "er019_family_x_entertainment_production_runner_01.py",
              "er053_b3_deterministic_producer_01.py", "er053_family_x_factlock_ja_writer_01.py",
              "er053_b3_annotation_contract_01.py"]
pytestmark = pytest.mark.skipif(not os.path.isdir(RUN), reason="run_mey_01 not present")


def _ledger():
    return lib.read_text(os.path.join(RUN, "research_ledger", "verified_fact_ledger.txt"))


def _stored():
    return json.loads(lib.read_text(os.path.join(RUN, "storyline_b3", "fact_selection_evidence.json")))


def _run(tmp_path, cand, client=None, budget=0.0):
    out_root = str(tmp_path / "root")
    log = os.path.join(out_root, "cost_log_dryrun.jsonl")
    client = client or lib.StubB3Client(_stored(), log, synthetic_supplement_id="F01")
    meta = lib.run_candidate(client, candidate=cand, topic=THEME, ledger_text=_ledger(),
                             cand_dir=os.path.join(out_root, "art", cand, "s1"), out_root=out_root,
                             baseline_ids=lib.baseline_ids_from_production(), budget_jpy=budget, cost_log=log, dry_run=True)
    return meta, client, out_root


# ---- (1) Baseline == Production -------------------------------------------------
def test_baseline_note_is_empty_and_prompt_is_production_byte_identical(tmp_path):
    meta, client, _ = _run(tmp_path, "baseline")
    assert lib.CANDIDATE_NOTES["baseline"] == ""
    assert client.prompts[0] == b3.build_user_prompt(THEME, _ledger())          # Productionの組立関数と完全一致
    assert meta["calls"][0]["user_prompt_sha256"] == lib.sha256_text(b3.build_user_prompt(THEME, _ledger()))
    assert meta["calls"][0]["developer_sha256"] == lib.sha256_text(b3.DEVELOPER_MESSAGE)
    assert meta["calls"][0]["schema_name"] == b3.STORYLINE_B3_JSON_SCHEMA["name"]
    assert meta["model_requested"] == routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"]
    assert meta["effort"] == vfl01.REASONING_EFFORT == "high"
    assert len(meta["calls"]) == 1


def test_production_prompt_shas_equal_those_recorded_in_run_mey_01(tmp_path):
    meta, _, _ = _run(tmp_path, "baseline")
    prod = json.loads(lib.read_text(os.path.join(RUN, "storyline_b3", "runtime_evidence.json")))["prompt_shas"]
    assert meta["production_prompt_shas"] == prod
    assert prod["developer_message_sha256"] == "b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a"
    assert prod["user_prompt_template_sha256"] == "6cc7218432a685701ddeb9342fc63fd1da6d13a18e0f0e5dd842ed591808b796"
    assert prod["fact_test_definitions_sha256"] == "91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a"
    evid = _stored()
    assert evid["min2_policy"]["reeval_note_sha256"] == b3.reeval_note_sha()


def test_baseline_dry_run_reproduces_production_selection_and_artifacts(tmp_path):
    meta, _, out_root = _run(tmp_path, "baseline")
    assert meta["analysis"]["selected_fact_ids"] == ["F04", "F11"] == lib.baseline_ids_from_production()
    assert meta["analysis"]["supplement_fact_ids"] == [] and meta["analysis"]["min2_satisfied"] is True
    cdir = os.path.join(out_root, "art", "baseline", "s1", "storyline_b3")
    for name in ("selected_brief.md", "selected_brief_annotated.md", "annotation.json", "writer_constraints.txt", "full_ledger.json"):
        with open(os.path.join(cdir, name), "rb") as a, open(os.path.join(RUN, "storyline_b3", name), "rb") as b:
            ra, rb = a.read(), b.read()
            # 委任_02(FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01): 履歴run(run_mey_01)は旧rules_sha256で生成済み。producerの
            # NUMドット区切り対応でrules_sha256のみ変わるため、旧値を現行値へ置換して比較(それ以外はbyte同一を要求)。
            rb = rb.replace(b"525f2309b5212e68a5891794e7fa6194fb25cbf92f1954727c286796597910d8", __import__("er053_b3_deterministic_producer_01").rules_sha256().encode())
            assert ra == rb, name       # Production producer出力とbyte同一(rules_sha256除く)


# ---- (2) 候補=Promptへの追記のみ ---------------------------------------------------
@pytest.mark.parametrize("cand", ["C1", "C2", "C3"])
def test_candidate_prompt_is_production_prompt_plus_note_only(tmp_path, cand):
    meta, client, _ = _run(tmp_path, cand)
    base = b3.build_user_prompt(THEME, _ledger())
    assert client.prompts[0] == base + lib.CANDIDATE_NOTES[cand]
    assert client.prompts[0].startswith(base)
    assert meta["calls"][0]["developer_sha256"] == lib.sha256_text(b3.DEVELOPER_MESSAGE)
    assert b3.FACT_TEST_DEFINITIONS_JA in client.prompts[0]                       # 4テスト定義は不変のまま存在
    assert "最低2件" in client.prompts[0]                                          # 下限2件の指示も不変のまま存在
    assert meta["analysis"]["supplement_fact_ids"] == ["F01"] and meta["analysis"]["supplement_not_in_selected"] == []
    assert meta["analysis"]["background_confirm_note_present"] is True


# ---- (3) 一般化 -------------------------------------------------------------------
def test_candidate_notes_contain_no_case_specific_terms_or_fact_ids():
    rep = lib.generalization_report()
    assert rep == {"baseline": [], "C1": [], "C2": [], "C3": []}, rep
    assert lib.assert_generalized("フーシ派が") and lib.assert_generalized("F04を採用") and lib.assert_generalized("空港")


def test_run_candidate_refuses_note_with_banned_term(tmp_path, monkeypatch):
    monkeypatch.setitem(lib.CANDIDATE_NOTES, "C1", lib.CANDIDATE_NOTES["C1"] + "F04を必ず採用")
    with pytest.raises(RuntimeError, match="固有事例"):
        _run(tmp_path, "C1")


# ---- (4) Production非変更 ---------------------------------------------------------
def test_production_modules_unchanged_vs_git_head():
    try:
        r = subprocess.run(["git", "diff", "--stat", "HEAD", "--"] + PROD_FILES, cwd=lib.ROOT, capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001
        pytest.skip("git unavailable")
    assert r.returncode == 0 and r.stdout.strip() == "", r.stdout


def test_trial_modules_have_no_env_switch_and_do_not_import_runner():
    for f in ("lib", "run", "eval", "writer_probe"):
        src = open(os.path.join(lib.ROOT, f"er083_b3_background_fact_trial_01_{f}.py"), encoding="utf-8").read()
        assert "os.environ" not in src and "getenv" not in src, f
    # runnerはimportしない(Production呼出元に触れない)
    for f in ("lib", "run", "eval", "writer_probe"):
        src = open(os.path.join(lib.ROOT, f"er083_b3_background_fact_trial_01_{f}.py"), encoding="utf-8").read()
        assert "import er019_family_x_entertainment_production_runner_01" not in src


# ---- (5) 下限2件の再評価はProduction経路に委ねる -----------------------------------
class _ScriptedClient:
    """1回目はF11のみ(VERIFIED 1件)、2回目(再評価)はF04+F11を返す。受け取ったpromptを記録。"""

    def __init__(self):
        self.prompts, self.n = [], 0
        self.responses = types.SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.n += 1
        self.prompts.append(kw["input"][-1]["content"])
        st = _stored()
        sel = ["F11"] if self.n == 1 else ["F04", "F11"]
        for ft in st["fact_tests"]:
            ft["decision"] = "selected" if ft["fact_id"] in sel else "excluded"
        parsed = {"selected_storyline": st["selected_storyline"], "fact_tests": st["fact_tests"], "selected_fact_ids": sel,
                  "selected_fact_brief": st["selected_fact_brief_text"], "recheck_note": None}
        return types.SimpleNamespace(output_text=json.dumps(parsed, ensure_ascii=False), model=kw["model"], id=f"s{self.n}",
                                     usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))


def test_min2_reevaluation_is_delegated_to_production_and_candidate_note_goes_on_every_call(tmp_path):
    cl = _ScriptedClient()
    meta, _, _ = _run(tmp_path, "C1", client=cl)
    assert cl.n == 2 and meta["min2_policy"]["reevaluated"] is True and meta["min2_policy"]["final_verified_n"] == 2
    assert "【再評価の指示】" in cl.prompts[1] and "【再評価の指示】" not in cl.prompts[0]
    assert lib.CANDIDATE_NOTES["C1"] in cl.prompts[0] and lib.CANDIDATE_NOTES["C1"] in cl.prompts[1]
    assert meta["analysis"]["min2_satisfied"] is True and len(meta["calls"]) == 2


def test_min2_stop_is_recorded_not_swallowed(tmp_path):
    class OnlyOne(_ScriptedClient):
        def _create(self, **kw):
            r = super()._create(**kw)
            p = json.loads(r.output_text)
            for ft in p["fact_tests"]:
                ft["decision"] = "selected" if ft["fact_id"] == "F11" else "excluded"
            p["selected_fact_ids"] = ["F11"]
            r.output_text = json.dumps(p, ensure_ascii=False)
            return r
    meta, _, out_root = _run(tmp_path, "C2", client=OnlyOne())
    assert meta["status"] == "B3_MIN2_STOP:REEVAL_STILL_LT2"
    assert os.path.isfile(os.path.join(out_root, "art", "C2", "s1", "storyline_b3", "b3_min2_stop_record.json"))
    assert "analysis" not in meta       # STOP時は選定結果を作らない(Production同様)


# ---- (6) guard ---------------------------------------------------------------------
def test_output_path_guard_rejects_run_mey_01_and_outside(tmp_path):
    with pytest.raises(RuntimeError):
        lib.assert_under_out_root(os.path.join(RUN, "storyline_b3"), lib.OUT_ROOT)
    with pytest.raises(RuntimeError):
        lib.assert_under_out_root(str(tmp_path / "elsewhere"), lib.OUT_ROOT)
    lib.assert_under_out_root(os.path.join(lib.OUT_ROOT, "x", "C1"), lib.OUT_ROOT)


def test_budget_guard_blocks_when_estimated_next_call_exceeds_budget(tmp_path):
    log = str(tmp_path / "cost_log.jsonl")
    g = lib.BudgetGuard(log, 5.0, lib.EST_B3_CALL_JPY, dry_run=False)
    with pytest.raises(lib.BudgetStop):
        g.check("x")                                    # 0 + 7.6 > 5.0
    assert lib.BudgetGuard(log, 0.0, lib.EST_B3_CALL_JPY, dry_run=True).check("x") == {"dry_run": True}
    assert lib.BudgetGuard(log, 10.0, lib.EST_B3_CALL_JPY, dry_run=False).check("x")["budget"] == 10.0


def test_dry_run_cost_is_zero_real_calls(tmp_path):
    _, _, out_root = _run(tmp_path, "C1")
    cs = lib.cost_summary(os.path.join(out_root, "cost_log_dryrun.jsonl"))
    assert cs["real_api_calls"] == 0 and cs["total_jpy"] == 0.0 and cs["stub_calls"] == 1


# ---- 解析・eval・writer probe ----------------------------------------------------
def test_analyze_detects_over_cap_and_unmarked_additions():
    st = _stored()
    parsed = {"selected_storyline": "s", "selected_fact_ids": ["F04", "F11", "F01", "F02", "F03"], "recheck_note": None,
              "fact_tests": [dict(ft, decision="selected" if ft["fact_id"] in ("F04", "F11", "F01", "F02", "F03") else "excluded",
                                  reason=(lib.SUPP_PREFIX + "x") if ft["fact_id"] in ("F01", "F02", "F03") else ft["reason"])
                             for ft in st["fact_tests"]]}
    a = lib.analyze_selection(parsed, _ledger(), ["F04", "F11"])
    assert a["supplement_over_cap_2"] is True and a["n_supplement"] == 3
    parsed["fact_tests"][0]["reason"] = "x"       # F01のマーカーを外す
    a2 = lib.analyze_selection(parsed, _ledger(), ["F04", "F11"])
    assert "F01" in a2["added_without_supplement_marker"]


def test_eval_comparison_and_blind_pack_hide_candidate_names(tmp_path):
    for c in ("baseline", "C1"):
        _run(tmp_path, c)
    out_root = str(tmp_path / "root")
    rows = ev_mod.collect(out_root, "art", dry_run=False)
    assert [r["_label"] for r in rows][:2] == ["baseline(現行Production run_mey_01)", "baseline_rerun/s1"]
    md = ev_mod.render_md(rows, lib.generalization_report())
    assert "F01" in md and "C1" in md
    probe.run_probe(os.path.join(out_root, "art", "C1", "s1"), out_root, 0.0, True, cost_log=os.path.join(out_root, "cost_log_dryrun.jsonl"))
    rows = ev_mod.collect(out_root, "art", dry_run=False)
    key = ev_mod.blind_pack(rows, out_root)
    pack = open(os.path.join(out_root, "blind_pack.md"), encoding="utf-8").read()
    assert "C1" not in pack and "baseline" not in pack and set(key.values()) == {"C1/s1", "baseline(現行Production run_mey_01)", "baseline_rerun/s1"} and set(key) == {"A", "B", "C"}


def test_writer_probe_runs_production_w1_on_candidate_dir_only_and_refuses_production_dir(tmp_path):
    _, _, out_root = _run(tmp_path, "C3")
    cdir = os.path.join(out_root, "art", "C3", "s1")
    out = probe.run_probe(cdir, out_root, 0.0, True, cost_log=os.path.join(out_root, "cost_log_dryrun.jsonl"))
    assert os.path.isfile(out["revision2"]) and out["cost"]["real_api_calls"] == 0
    with pytest.raises(RuntimeError):
        probe.run_probe(RUN, out_root, 0.0, True)
