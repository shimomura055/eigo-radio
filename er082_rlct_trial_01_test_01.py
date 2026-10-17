# ============================================================
# er082_rlct_trial_01_test_01.py  (FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_04 CP1)
# API呼出0のunittest。テスト(a)〜(j)は委任文の指定、(k)以降は追加。
# ============================================================
import copy
import glob
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_en_direct_vfl_01_generate as vfl01
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er082_rlct_trial_01_inject as inj
import er082_rlct_trial_01_lib as lib
import er082_rlct_trial_01_run as run

TMP_ROOT = "er082_output/rlct_trial_01/_test_tmp"


def _mini_draft(n=8):
    return {"facts": [{"fact_id": f"F{i}", "claim": f"claim {i} 値は{i}0%", "subject": "s", "date_or_period": "2026",
                       "scope": "sc", "conditions": None, "numeric_value": f"{i}0%", "numeric_scope": "x",
                       "causal_strength": "NOT_APPLICABLE", "source_title": "t", "source_url": "u",
                       "source_type": "x", "support_level": "x", "ambiguity": None, "notes_for_writer": None}
                      for i in range(1, n + 1)]}


def _scenario(draft, verdicts, selected, story="story 値は10%"):
    return {"m0_verdicts": {k: {"fact_id": k, "verdict": v, "verification_notes": "n"} for k, v in verdicts.items()},
            "m0_evidence": {"selected_fact_ids": selected, "selected_storyline": story},
            "n_facts_all": len(draft["facts"]), "m0_total_ws_calls": len(draft["facts"])}


class RlctTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
        os.makedirs(TMP_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)

    def _budget(self, name, stage="1a", **kw):
        d = f"{TMP_ROOT}/{name}"
        os.makedirs(d, exist_ok=True)
        log = f"{d}/stub_usage_log.jsonl"
        return d, log, lib.Budget(log, stage, out_root=d, **kw)

    # (a) Production関連ファイルsha不変(+再利用成果物、共用Review Queue)
    def test_a_production_and_reused_sha_unchanged(self):
        arts = ["coffee_prices", "inbound_tourism"]
        before = lib.integrity_snapshot(arts)
        out = f"{TMP_ROOT}/a"
        rc = run.main(["--dry-run", "--article", "coffee_prices,inbound_tourism", "--method", "M0b,M2", "--out", out])
        self.assertEqual(rc, 0)
        after = lib.integrity_snapshot(arts)
        cmp_ = lib.compare_snapshots(before, after)
        self.assertTrue(cmp_["identical"], cmp_)
        self.assertTrue(all(v != "MISSING" for v in before["code"].values()))

    # (b) Trial Verifier Promptは既存Promptと上限文以外同一
    def test_b_verifier_prompt_identical_except_cap_suffix(self):
        sub = _mini_draft(2)
        prod = vfl01.build_verification_prompt("topic", sub)
        self.assertEqual(lib.build_verifier_prompt("topic", sub, False), prod)
        capped = lib.build_verifier_prompt("topic", sub, True)
        self.assertTrue(capped.startswith(prod))
        self.assertEqual(capped[len(prod):], lib.CAP_SUFFIX)
        self.assertIn("3回", lib.CAP_SUFFIX)
        diff = lib.prompt_diff_evidence()
        added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
        self.assertTrue(added)
        self.assertFalse([r for r in removed if r.strip("-").strip()])   # 本文の削除なし

    # (c) [UNVERIFIED]対応regex
    def test_c_unverified_regex(self):
        txt = "[VERIFIED] F01: a\n\n[UNVERIFIED] F02: b\n[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F03: c\n"
        self.assertEqual(lib.extract_ids_trial(txt), ["F01", "F02", "F03"])
        self.assertEqual(b3.extract_fact_ids_from_ledger(txt), ["F01", "F03"])    # 既存regexは[UNVERIFIED]を拾わない

    # (d) web_search 1回が費用に計上される(stub usage)。Production式と一致
    def test_d_web_search_cost_counted_same_formula_as_production(self):
        d, log, budget = self._budget("d")
        row = {"theme": lib.THEME_TAG, "stage": "1a|x|M1|ledger", "provider": "openai", "model_id": "gpt-6-luna",
               "input_tokens": 0, "output_tokens": 0, "web_search_call_count": 1,
               "timestamp": "2026-10-17T00:00:00+00:00"}
        lib.append_jsonl(log, row)
        c = lib.cost_by_stage_tag(log, theme=lib.THEME_TAG)["1a|x|M1|ledger"]
        self.assertAlmostEqual(c["web_search_jpy"], 10.0 / 1000 * lib.efam.USD_JPY, places=3)   # 1.6 JPY
        self.assertEqual(c["web_search_calls"], 1)
        self.assertGreater(budget.spent()["total"], 1.5)
        # Production式(token費用+web_search込み)と同額
        row2 = dict(row, stage="1a|x|M1|b3", model_id="gpt-6.1-sol", input_tokens=12345, output_tokens=2345,
                    web_search_call_count=3)
        lib.append_jsonl(log, row2)
        import er019_family_x_entertainment_production_runner_01 as prod
        ref = prod.compute_stage_cost_breakdown(log)
        mine = lib.cost_by_stage_tag(log, theme=lib.THEME_TAG)
        self.assertAlmostEqual(sum(v["total_jpy"] for v in mine.values()), ref["total_jpy"], places=2)

    # (e) REJECTED再選定の検知(REJECTED IDをB3が選び直すと技術的失敗として記録し、確定しない)
    def test_e_rejected_reselect_detected(self):
        draft = _mini_draft(6)
        verd = {f"F{i}": "VERIFIED" for i in range(1, 7)}
        verd["F3"] = "REJECTED"
        sc = _scenario(draft, verd, ["F1", "F2", "F3"])
        sc["b3_force_ids"], sc["b3_force_allow_unknown"] = ["F1", "F2", "F3"], True
        d, log, budget = self._budget("e")
        client = lib.StubClient(sc, log)
        res = lib.select_then_verify(client, "t", draft, work_dir=f"{d}/w", stage_prefix="1a|a|M2", budget=budget, cap=False)
        self.assertEqual(res["status"], "UNRESOLVED")
        self.assertTrue(res["rejected_reselected_detected"])
        self.assertNotIn("ledger_text", res)
        self.assertTrue(os.path.isfile(f"{d}/w/unresolved.json"))

    # 正常な再選定(REJECTEDを外し別Factを選ぶ)・検証済みの再利用
    def test_e2_reselect_replaces_rejected_and_reuses_verdicts(self):
        draft = _mini_draft(6)
        verd = {f"F{i}": "VERIFIED" for i in range(1, 7)}
        verd["F3"] = "REJECTED"
        sc = _scenario(draft, verd, ["F1", "F2"])
        sc["b3_initial_extra_ids"] = ["F3"]
        d, log, budget = self._budget("e2")
        client = lib.StubClient(sc, log)
        res = lib.select_then_verify(client, "t", draft, work_dir=f"{d}/w", stage_prefix="1a|a|M2", budget=budget, cap=False)
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["reselect_count"], 1)
        self.assertNotIn("F3", res["selected_fact_ids"])
        r1 = res["rounds"][1]
        self.assertTrue(set(["F1", "F2"]) <= set(r1["reused_verdicts"]))          # 検証済みは再検証しない
        self.assertTrue(r1["verified_now"] == [] or "F3" not in r1["verified_now"])
        self.assertNotIn("REJECTED", res["ledger_text"])

    # (f) 再選定上限到達で確定ファイルを出さない(run_methodのend-to-end)
    def test_f_reselect_limit_no_confirmed_files(self):
        # 合成src run(coffeeを複製し、全Factをstub上REJECTEDにする)
        src = f"{TMP_ROOT}/f_src"
        for rel in lib.INPUT_FILES:
            os.makedirs(os.path.dirname(f"{src}/{rel}"), exist_ok=True)
            shutil.copyfile(f"{lib.ARTICLES['coffee_prices']['src']}/{rel}", f"{src}/{rel}")
        vp = f"{src}/research_ledger/fact_ledger_verification.json"
        v = lib.load_json(vp)
        for x in v["verifications"]:
            x["verdict"] = "REJECTED"
        lib.save_json(vp, v)
        from unittest import mock
        with mock.patch.dict(lib.ARTICLES, {"synthetic_all_rejected": {
                "src": src, "stage": "1a", "b3_reusable": True, "known_defects": []}}):
            out = f"{TMP_ROOT}/f_out"
            os.makedirs(out, exist_ok=True)
            data = lib.load_article_inputs(lib.copy_inputs("synthetic_all_rejected", out))
            log = f"{out}/stub.jsonl"
            client = lib.StubClient(run._scenario(data), log)
            budget = lib.Budget(log, "1a", out_root=out)
            r = run.run_method("synthetic_all_rejected", "M2", "1a", client, budget, out, log, True)
            self.assertEqual(r["status"], "UNRESOLVED")
            mdir = f"{out}/synthetic_all_rejected/M2"
            self.assertFalse(os.path.exists(f"{mdir}/research_ledger"))
            self.assertFalse(os.path.exists(f"{mdir}/storyline_b3"))
            self.assertTrue(os.path.isfile(f"{mdir}/_work/unresolved.json"))
            self.assertEqual(r["reselect"]["reselect_count"], 2)    # 最大2回で止まる

    # (g) 入力複製後に元dirへ書込みが無い
    def test_g_copy_inputs_does_not_write_source(self):
        src = lib.ARTICLES["coffee_prices"]["src"]
        before_tree = lib.tree_listing(src)
        before_sha = lib.sha_manifest(lib.reused_artifact_paths("coffee_prices"))
        out = f"{TMP_ROOT}/g"
        dst = lib.copy_inputs("coffee_prices", out)
        self.assertTrue(os.path.isfile(f"{dst}/research_ledger/fact_ledger_draft.json"))
        # 複製側へ書込んでも元は不変
        with open(f"{dst}/storyline_b3/fact_selection_evidence.json", "ab") as f:
            f.write(b" ")
        with self.assertRaises(RuntimeError):
            lib.copy_inputs("coffee_prices", out)          # 複製が元と異なる場合は上書きせず停止
        self.assertEqual(lib.tree_listing(src), before_tree)
        self.assertEqual(lib.sha_manifest(lib.reused_artifact_paths("coffee_prices")), before_sha)

    # (h) budget guardがStage上限/累計上限で止まる(呼出前に止め、clientを呼ばない)
    def test_h_budget_guard_stops_at_stage_cap_and_cumulative_cap(self):
        d, log, budget = self._budget("h", stage="optA", stage_caps={"1a": 493.0, "1b": 493.0, "optA": 5.0})
        lib.append_jsonl(log, {"theme": lib.THEME_TAG, "stage": "optA|a|inject|x", "provider": "openai",
                               "model_id": "gpt-6-luna", "input_tokens": 0, "output_tokens": 0,
                               "web_search_call_count": 2, "timestamp": "2026-10-17T00:00:00+00:00"})   # 3.2 JPY
        class Boom:
            calls = 0
            class responses:
                @staticmethod
                def create(**kw):
                    raise AssertionError("API must not be called after budget stop")
        with self.assertRaises(lib.BudgetStop):
            lib.verify_facts_trial(Boom, "t", _mini_draft(2), ["F1"], cap=False, work_dir=f"{d}/w", label="x",
                                   stage_tag="optA|a|inject|y", budget=budget, est_jpy=3.0)   # 3.2+3.0>5
        self.assertTrue(os.path.isfile(f"{d}/STOP_BUDGET.json"))
        # 累計上限
        d2, log2, b2 = self._budget("h2", stage="1a", cum_cap=2.0)
        lib.append_jsonl(log2, {"theme": lib.THEME_TAG, "stage": "1b|a|M|x", "provider": "openai", "model_id": "gpt-6-luna",
                                "input_tokens": 0, "output_tokens": 0, "web_search_call_count": 1,
                                "timestamp": "2026-10-17T00:00:00+00:00"})
        with self.assertRaises(lib.BudgetStop) as cm:
            b2.check_before(1.0, "cum")
        self.assertIn("cumulative_cap", str(cm.exception))
        # 承認値の定数
        self.assertEqual((lib.STAGE_CAPS_JPY, lib.CUM_CAP_JPY, lib.EXPECTED_TOTAL_JPY),
                         ({"1a": 493.0, "1b": 493.0, "optA": 54.0}, 1040.0, 536.0))

    # (i) RF/producerの出力先がer082配下のみ(Trial領域外はSTOP)、共用Review Queue不変
    def test_i_outputs_confined_under_er082(self):
        with self.assertRaises(RuntimeError):
            lib.contract_check(lib.ARTICLES["coffee_prices"]["src"])
        with self.assertRaises(RuntimeError):
            lib.assert_under_out_root("er019_output/coffee_prices/run_fxpw_01/x")
        q_before = lib.tree_listing(lib.SHARED_QUEUE_ROOT)
        out = f"{TMP_ROOT}/i"
        rc = run.main(["--dry-run", "--article", "coffee_prices", "--method", "M0", "--out", out])
        self.assertEqual(rc, 0)
        self.assertEqual(lib.tree_listing(lib.SHARED_QUEUE_ROOT), q_before)
        r = lib.load_json(f"{out}/coffee_prices/M0/result.json")
        self.assertTrue(r["contract"]["all_pass"], r["contract"])
        self.assertTrue(r["contract"]["method_dir"].startswith(out))

    # (j) dry-runが5記事x全方式で完走(API 0、integrity一致)
    def test_j_dryrun_all_articles_all_methods(self):
        out = f"{TMP_ROOT}/j"
        rc = run.main(["--dry-run", "--all-articles", "--all-methods", "--out", out])
        self.assertEqual(rc, 0)
        s = lib.load_json(f"{out}/dryrun_summary.json")
        self.assertEqual(s["jobs"], 30)
        self.assertEqual(len(s["completed"]), 30)
        self.assertTrue(all(c["status"] == "COMPLETED" for c in s["completed"]))
        self.assertEqual(s["real_usage_log_rows"], 0)                 # 課金行なし(API呼出0)
        self.assertTrue(s["integrity_identical"])
        self.assertGreater(s["stub_usage_rows"], 0)
        # inboundのM2は再選定loopが動く(M0でREJECTEDを持つ唯一の記事)
        r = lib.load_json(f"{out}/inbound_tourism/M2/result.json")
        self.assertGreaterEqual(r["reselect"]["reselect_count"], 1)
        # M3はM2の初回B3選定を共有
        self.assertTrue(lib.load_json(f"{out}/coffee_prices/M3/result.json")["shared_initial_b3_from"])

    # (k) 候補Ledger描画が既存Ledgerと一致(全判定済み時)、REJECTEDは外れ、未検証は[UNVERIFIED]
    def test_k_render_candidate_ledger_matches_production(self):
        for art in ("coffee_prices", "inbound_tourism"):
            data = lib.load_article_inputs(lib.copy_inputs(art, f"{TMP_ROOT}/k"))
            txt = lib.render_candidate_ledger(data["draft"], data["m0_verdicts"])
            self.assertEqual(txt, data["m0_ledger_text"], art)
        d = _mini_draft(3)
        t = lib.render_candidate_ledger(d, {"F1": {"verdict": "REJECTED", "verification_notes": "x"}})
        self.assertNotIn("F1:", t)
        self.assertIn("[UNVERIFIED] F2:", t)

    # (l) 昇格(AMBIGUOUS/REJECTED->VERIFIED)検知、既知欠陥3値、model照合
    def test_l_metrics(self):
        m0 = {"A": {"verdict": "AMBIGUOUS"}, "B": {"verdict": "VERIFIED"}, "C": {"verdict": "REJECTED"}}
        new = {"A": {"verdict": "VERIFIED"}, "B": {"verdict": "AMBIGUOUS"}, "C": {"verdict": "REJECTED"}}
        t = lib.verdict_transitions(m0, new)
        self.assertEqual(t["promotions_to_verified_or_up"], ["A"])
        self.assertEqual(t["demotions_from_verified"], ["B"])
        st = lib.known_defect_status("coffee_prices", ["F12", "F07"], {"F12": {"verdict": "VERIFIED"}, "F07": {"verdict": "AMBIGUOUS"}})
        self.assertEqual(st["F12"], "b_selected_missed_NG")
        self.assertEqual(st["F07"], "a_selected_detected")
        self.assertEqual(st["F16"], "c_not_selected")

    # (m) 有料run防止: dry-runかトークン付きのどちらか一方のみ
    def test_m_paid_run_requires_token(self):
        with self.assertRaises(SystemExit):
            run.main(["--all-articles", "--all-methods", "--out", f"{TMP_ROOT}/m"])
        with self.assertRaises(SystemExit):
            run.main(["--paid-confirm", "WRONG", "--plan", "1a", "--out", f"{TMP_ROOT}/m"])
        with self.assertRaises(SystemExit):
            run.main(["--dry-run", "--paid-confirm", lib.PAID_CONFIRM_TOKEN, "--plan", "1a", "--out", f"{TMP_ROOT}/m"])

    # (n) 任意A: 故障注入。元draft不変、検出されるとcritical_ng=False、検出漏れ(VERIFIED)は重大NG
    def test_n_fault_injection(self):
        out = f"{TMP_ROOT}/n"
        for a in ("coffee_prices", "inbound_tourism"):
            self.assertEqual(inj.main(["--dry-run", "--article", a, "--out", out]), 0)
            r = lib.load_json(f"{out}/{a}/optA/result.json")
            self.assertGreaterEqual(r["n_injected"], 2)
            self.assertTrue(r["original_draft_unchanged"])
            self.assertFalse(r["critical_ng"])
            self.assertEqual({x["outcome"] for x in r["rows"]}, {"detected"})
        # 陰性対照: stubが検出漏れ(VERIFIED)を返すとharnessが重大NGとして拾う
        data = lib.load_article_inputs(lib.copy_inputs("coffee_prices", out))
        injected = inj.build_injected(data["draft"], data["m0_evidence"]["selected_fact_ids"])
        sc = {"m0_verdicts": data["m0_verdicts"], "m0_evidence": data["m0_evidence"], "n_facts_all": 17,
              "m0_total_ws_calls": 14, "inject_missed_ids": {injected[0]["fact"]["fact_id"]}}
        log = f"{out}/neg.jsonl"
        budget = lib.Budget(log, "optA", out_root=out)
        r = inj.run_injection("coffee_prices", lib.StubClient(sc, log), budget, out, log, True)
        self.assertTrue(r["critical_ng"])
        self.assertEqual(r["missed_critical_ng"][0]["outcome"], "MISSED_CRITICAL_NG")

    # (o) Productionがer082を参照しない(Trialが配線されていない)
    def test_o_no_production_reference_to_er082(self):
        hits = []
        for p in glob.glob("*.py"):
            if os.path.basename(p).startswith("er082_"):
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                if "er082_rlct" in f.read():
                    hits.append(p)
        self.assertEqual(hits, [])

    # (p) B3 Promptの差分は『検証済み』語のみ(allow_unverified時)
    # (q) aggregateキャプションは出力元で切替(MEASURED/SYNTHETIC/MIXED)、固定文言でない
    def test_q_aggregate_caption_switches_by_source(self):
        import er082_rlct_trial_01_aggregate as agg
        m = {"dry_run": False, "basis": "OFFICIAL_API_RESPONSE"}
        s = {"dry_run": True, "basis": "STUB"}
        self.assertTrue(agg._note([m, m]).startswith("MEASURED"))
        self.assertTrue(agg._note([s, s]).startswith("SYNTHETIC"))
        self.assertTrue(agg._note([m, s]).startswith("MIXED"))

    def test_p_b3_prompt_difference_limited(self):
        plain = lib.build_user_prompt_trial("t", "[VERIFIED] F1: a\n", False)
        self.assertEqual(plain, b3.build_user_prompt("t", "[VERIFIED] F1: a\n"))
        unv = lib.build_user_prompt_trial("t", "[VERIFIED] F1: a\n", True)
        self.assertEqual(unv.replace(lib.UNVERIFIED_PHRASE, lib.VERIFIED_PHRASE), plain)

    # ------------------------------------------------------------------
    # 委任_07 (ユーザー#107): 最終B3確認パス test_r1〜r7
    # ------------------------------------------------------------------
    def _stv(self, name, verdicts, selected, script=None, n=8):
        draft = _mini_draft(n)
        sc = _scenario(draft, verdicts, selected)
        for k in sc["m0_verdicts"]:
            sc["m0_verdicts"][k]["verification_notes"] = f"notes-{k}-{verdicts[k]}"
        if script is not None:
            sc["b3_script"] = script
        d, log, budget = self._budget(name)
        client = lib.StubClient(sc, log)
        res = lib.select_then_verify(client, "t", draft, work_dir=f"{d}/w", stage_prefix="1a|a|M2", budget=budget, cap=False)
        return d, client, res

    @staticmethod
    def _all_verified(n=8, **over):
        v = {f"F{i}": "VERIFIED" for i in range(1, n + 1)}
        v.update(over)
        return v

    # test_r1: 全VERIFIED→B3追加呼出0・confirm_pass NOT_NEEDED
    def test_r1_all_verified_no_extra_b3(self):
        d, client, res = self._stv("r1", self._all_verified(), ["F1", "F2", "F3"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(client.b3_n, 1)                              # 初回B3のみ
        self.assertEqual(res["b3_calls_after_initial"], 0)
        self.assertEqual(res["final_confirm_pass"], "NOT_NEEDED_ALL_VERIFIED")
        self.assertEqual(res["rounds"][0]["trigger"], "INITIAL")
        self.assertEqual(res["rounds"][0]["ambiguous_selected"], [])

    # test_r2: AMBIGUOUSのみ→確認パス1回・noteにID+notes+制約文・同じ集合なら確定・ambiguous_visible_to_b3=True
    def test_r2_ambiguous_only_one_confirm_pass(self):
        d, client, res = self._stv("r2", self._all_verified(F2="AMBIGUOUS"), ["F1", "F2", "F3"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual((res["reselect_count"], res["confirm_pass_count"], res["b3_calls_after_initial"]), (0, 1, 1))
        r0, r1 = res["rounds"]
        self.assertEqual(r0["confirm_pass"], "REQUIRED")
        self.assertFalse(r0["ambiguous_visible_to_b3"])               # 初回B3は検証前=AMBIGUOUSを知らない
        self.assertEqual(r0["ambiguous_unseen"], ["F2"])
        self.assertEqual(r1["trigger"], "CONFIRM_AMBIGUOUS")
        self.assertTrue(r1["ambiguous_visible_to_b3"])
        self.assertEqual(r1["confirm_pass"], "NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE")
        self.assertEqual(client.b3_n, 2)
        p = lib.load_json(f"{d}/w/b3_confirm1.json")["user_prompt"]     # B3へ実際に渡したprompt
        self.assertIn("AMBIGUOUS F2", p)
        self.assertIn("notes-F2-AMBIGUOUS", p)
        self.assertIn(lib.CONFIRM_CONSTRAINT, p)
        self.assertIn("Storylineの構成を再評価", p)
        self.assertIn("[AMBIGUOUS", p.split("【最終確認の指示")[0])        # 候補LedgerにAMBIGUOUSタグ
        self.assertIn("[UNVERIFIED] F4:", p)                            # 未検証候補は未検証のまま
        self.assertIn("新たに選んだFactだけを選定後に独立検証", p)
        self.assertEqual(res["rounds"][1]["verified_now"], [])          # 検証済みは再利用(再検証しない)

    # test_r3: 確認パスで新規未検証Factが選ばれ検証でAMBIGUOUS→2回目の確認パス→確定
    def test_r3_new_fact_ambiguous_second_confirm(self):
        d, client, res = self._stv("r3", self._all_verified(F2="AMBIGUOUS", F4="AMBIGUOUS"), ["F1", "F2"],
                                   script=[["F1", "F2"], ["F1", "F4"], ["F1", "F4"]])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual((res["reselect_count"], res["confirm_pass_count"], res["b3_calls_after_initial"]), (0, 2, 2))
        self.assertEqual(res["rounds"][1]["verified_now"], ["F4"])       # 新規Factだけ検証
        self.assertEqual(res["rounds"][1]["reused_verdicts"], ["F1"])
        self.assertEqual(res["rounds"][1]["confirm_pass"], "REQUIRED")  # F4は選定時に未検証だった
        self.assertEqual(res["rounds"][2]["confirm_pass"], "NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE")
        self.assertEqual(res["selected_fact_ids"], ["F1", "F4"])
        self.assertNotIn("F2:", res["ledger_text"])

    # test_r4: 確認パス2回で未達→UNRESOLVED、確定ファイル無し
    def test_r4_confirm_limit_unresolved(self):
        d, client, res = self._stv("r4", self._all_verified(F2="AMBIGUOUS", F3="AMBIGUOUS", F4="AMBIGUOUS"),
                                   ["F1", "F2"], script=[["F1", "F2"], ["F1", "F3"], ["F1", "F4"]])
        self.assertEqual(res["status"], "UNRESOLVED")
        self.assertEqual(res["reason"], "RESELECT_LIMIT_REACHED")
        self.assertEqual(res["unmet"], ["AMBIGUOUS_NOT_CONFIRMED"])
        self.assertEqual(res["b3_calls_after_initial"], 2)
        self.assertEqual(client.b3_n, 3)                                 # 初回+追加2回=3回で止まる
        self.assertNotIn("ledger_text", res)
        self.assertNotIn("selection", res)
        self.assertTrue(os.path.isfile(f"{d}/w/unresolved.json"))
        self.assertFalse(os.path.exists(f"{d}/w/research_ledger"))

    # test_r5: REJECTED+AMBIGUOUS混在→1回のnoteに両方、合算回数が2上限
    def test_r5_mixed_rejected_and_ambiguous(self):
        v = self._all_verified(F2="REJECTED", F3="AMBIGUOUS")
        d, client, res = self._stv("r5", v, ["F1", "F2", "F3"], script=[["F1", "F2", "F3"], ["F1", "F3", "F4"]])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["b3_calls_after_initial"], 1)
        self.assertEqual(res["rounds"][1]["trigger"], "RESELECT_REJECTED+CONFIRM_AMBIGUOUS")
        p = lib.load_json(f"{d}/w/b3_reselect1.json")["user_prompt"]
        self.assertIn("REJECTED F2", p)
        self.assertIn("選定禁止", p)
        self.assertIn("AMBIGUOUS F3", p)
        self.assertIn(lib.CONFIRM_CONSTRAINT, p)
        self.assertNotIn("F2:", p.split("【最終確認の指示")[0])           # REJECTEDは候補本文から外れる
        self.assertNotIn("F2", res["selected_fact_ids"])
        # 合算上限: 再選定+確認パスで2回使い切っても未達ならUNRESOLVED(3回目のB3は呼ばない)
        v2 = self._all_verified(F2="REJECTED", F3="AMBIGUOUS", F5="AMBIGUOUS", F6="AMBIGUOUS")
        d2, c2, res2 = self._stv("r5b", v2, ["F1", "F2", "F3"],
                                 script=[["F1", "F2", "F3"], ["F1", "F3", "F5"], ["F1", "F5", "F6"], ["F1", "F6"]])
        self.assertEqual(res2["status"], "UNRESOLVED")
        self.assertEqual(res2["b3_calls_after_initial"], 2)
        self.assertEqual(c2.b3_n, 3)
        self.assertEqual((res2["reselect_count"], res2["confirm_pass_count"]), (1, 1))   # 1回目=REJECTED起因、2回目=確認のみ
        self.assertEqual(res2["unmet"], ["AMBIGUOUS_NOT_CONFIRMED"])

    # test_r6: --correct-from は元M2を変更せずM2cへ出力、再利用初回B3のshaが一致
    def test_r6_correct_from_does_not_touch_source(self):
        out = f"{TMP_ROOT}/r6"
        self.assertEqual(run.main(["--dry-run", "--article", "inbound_tourism", "--method", "M2,M3", "--out", out]), 0)
        before = lib.tree_listing(f"{out}/inbound_tourism/M2"), lib.tree_listing(f"{out}/inbound_tourism/M3")
        self.assertEqual(run.main(["--dry-run", "--article", "inbound_tourism", "--correct-from", "M2,M3", "--out", out]), 0)
        after = lib.tree_listing(f"{out}/inbound_tourism/M2"), lib.tree_listing(f"{out}/inbound_tourism/M3")
        self.assertEqual(before, after)                                  # 元M2/M3のsha不変
        init_sha = lib.sha256_file(f"{out}/inbound_tourism/M2/_work/initial_b3.json")
        for m, mc in (("M2", "M2c"), ("M3", "M3c")):
            r = lib.load_json(f"{out}/inbound_tourism/{mc}/result.json")
            self.assertEqual(r["method"], mc)
            self.assertEqual(r["corrected_from"], m)
            self.assertEqual(r["reused_initial_b3_sha256"], init_sha)      # M3cもM2の初回B3を共有
            self.assertTrue(r["reused_verdict_ids"])
            self.assertIn("cost_correction_only", r)
            self.assertAlmostEqual(r["cost_production_equivalent"]["total_jpy"],
                                   r["pre_correction_cost_total_jpy"] + r["cost_correction_only"]["total_jpy"], places=2)
            src_r = lib.load_json(f"{out}/inbound_tourism/{m}/result.json")
            self.assertEqual(r["reselect"]["b3_calls_before_this_run"], len(src_r["reselect"]["rounds"]) - 1)   # 元の追加B3呼出は上限に合算
            self.assertLessEqual(r["reselect"]["b3_calls_after_initial"], 2)
            self.assertTrue(r["stage"] == "1a")
            self.assertTrue(all(k.startswith(("b3_confirm", "b3_reselect", "verify_sel")) for k in r["cost"]["by_step"]))
        # 実測dirを読み取り専用で参照(書込みなし)。元の判定(F05=AMBIGUOUS)から確認パスが発火する
        real = "er082_output/rlct_trial_01"
        if os.path.isfile(f"{real}/inbound_tourism/M2/result.json"):
            rb = lib.tree_listing(f"{real}/inbound_tourism")
            out2 = f"{TMP_ROOT}/r6b"
            self.assertEqual(run.main(["--dry-run", "--article", "inbound_tourism", "--correct-from", "M2",
                                       "--correct-source-root", real, "--out", out2]), 0)
            self.assertEqual(lib.tree_listing(f"{real}/inbound_tourism"), rb)
            r = lib.load_json(f"{out2}/inbound_tourism/M2c/result.json")
            self.assertEqual(r["reselect"]["rounds"][0]["trigger"], "RESUMED_FROM_SOURCE_FINAL")
            self.assertEqual(r["reselect"]["rounds"][0]["ambiguous_unseen"], ["F05"])
            self.assertEqual(r["reselect"]["rounds"][0]["confirm_pass"], "REQUIRED")
            self.assertGreaterEqual(r["reselect"]["b3_calls_after_initial"], 1)
            self.assertEqual(r["pre_correction_selected_fact_ids"], ["F01", "F02", "F04", "F05"])
        # 復元不能ならSTOP(推測で補わない)
        with self.assertRaises(RuntimeError):
            run._restore_source(f"{TMP_ROOT}/nonexistent", "inbound_tourism", "M2")

    # test_r7: conform_checkが既存1a実測に対し inbound M2/M3=FAIL(F05)、M0/M0b/M0p/M1=N/A、Coffee M2/M3は実測どおり
    def test_r7_conform_check_on_stage1a_results(self):
        import er082_rlct_trial_01_conform_check as cc
        real = "er082_output/rlct_trial_01"
        if not os.path.isfile(f"{real}/inbound_tourism/M2/result.json"):
            self.skipTest("Stage 1a実測が無い環境")
        rows = {(r["article"], r["method"]): r for r in (cc.check_method(real, a, m)
                for a in cc.ARTICLES_1A for m in lib.METHODS)}
        self.assertEqual(len(rows), 12)
        for a in cc.ARTICLES_1A:
            for m in ("M0", "M0b", "M0p", "M1"):
                self.assertEqual(rows[(a, m)]["conform_d1"], "N/A")
        for m in ("M2", "M3"):
            r = rows[("inbound_tourism", m)]
            self.assertEqual(r["conform_d1"], "FAIL")
            self.assertEqual(r["ambiguous_unseen_by_b3"], ["F05"])
            self.assertTrue(r["prompt_evidence"]["agrees_with_rounds"])   # 保存B3 promptの裏取りと一致
        for m in ("M2", "M3"):                                           # Coffeeは選定Fact全てVERIFIED(実測値どおりPASS)
            r = rows[("coffee_prices", m)]
            self.assertEqual(r["conform_d1"], "PASS")
            self.assertEqual(r["ambiguous_selected"], [])
            self.assertEqual(r["rejected_selected"], [])


if __name__ == "__main__":
    unittest.main()
