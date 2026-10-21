# ============================================================
# er019_family_x_b3_min2_test_01.py
# FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 (委任_02): B3採用Fact下限2件(VERIFIEDのみ算入)のRegression
# ============================================================
# 実API呼び出しなし(LLMはmock)。対象:
#   - er019_family_x_storyline_b3_fact_selection_01.py(再評価1回・STOP・VERIFIED算入・Prompt差替え・soft warning)
#   - er019_family_x_entertainment_production_runner_01.py(STOP記録・supersede・assert_b3_min_verified合流点ガード)
# 実行: .venv/Scripts/python.exe -m pytest er019_family_x_b3_min2_test_01.py -q
# ============================================================
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er053_b3_deterministic_producer_01 as prod

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER_PY = os.path.join(HERE, "er019_family_x_entertainment_production_runner_01.py")
B3_PY = os.path.join(HERE, "er019_family_x_storyline_b3_fact_selection_01.py")

# 変更前(FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 実装前)のproducer rules_sha256(実測、委任_02 Phase A開始時)
# FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02: NUMのドット区切り数値列対応(26.10.10)で値を更新。
# 旧値(FACT-MIN2実装前/〜委任_02前) = 525f2309b5212e68a5891794e7fa6194fb25cbf92f1954727c286796597910d8
RULES_SHA256_BEFORE = "3b4b7fdf8dc6816cf8368b538c4b85485dba33ed2a114a8319b13a060050f723"
FACT_TEST_DEFINITIONS_SHA = "91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a"
DEVELOPER_MESSAGE_SHA = "b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a"
REEVAL_NOTE_TEMPLATE_SHA = "dcf4f2b40a9ddaccf6121ae39c6b5ccf1bd31edab3b012d7a65d8da05d4142dd"

LEDGER = """[VERIFIED] F01: Verified claim one.
  scope: x

[VERIFIED] F02: Verified claim two.
  scope: x

[VERIFIED] F03: Verified claim three.
  scope: x

[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F04: Ambiguous claim four.
  scope: x
"""
ALL_IDS = ["F01", "F02", "F03", "F04"]

LEDGER_ONE_VERIFIED = """[VERIFIED] F01: Verified claim one.
  scope: x

[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F04: Ambiguous claim four.
  scope: x
"""


def _parsed(selected, all_ids=None, storyline="S.", all_exclude_selected=()):
    all_ids = all_ids or ALL_IDS
    fts = []
    for fid in all_ids:
        sel = fid in selected
        if fid in all_exclude_selected:
            t = ("YES", "NO", "NO", "YES")    # 4テスト全て除外側
        elif sel:
            t = ("NO", "YES", "YES", "NO")
        else:
            t = ("YES", "NO", "NO", "YES")
        fts.append({"fact_id": fid, "test1_answer": t[0], "test2_answer": t[1], "test3_answer": t[2],
                    "test4_answer": t[3], "decision": "selected" if sel else "excluded", "reason": f"reason {fid}"})
    return {"selected_storyline": storyline, "fact_tests": fts, "selected_fact_ids": list(selected),
            "selected_fact_brief": "Brief " + ",".join(selected), "recheck_note": None}


def _client(*items):
    """items: parsed dict(成功応答) または Exception(送出)。"""
    client = mock.Mock()
    seq = []
    for it in items:
        if isinstance(it, Exception):
            seq.append(it)
            continue
        resp = mock.Mock()
        resp.output_text = json.dumps(it)
        resp.model = "gpt-6.1-sol-x"
        resp.id = f"resp_{len(seq)}"
        seq.append(resp)
    client.responses.create.side_effect = seq
    return client


def _run(client, ledger=LEDGER, **kw):
    return b3.run_storyline_b3_selection(client, "TOPIC-TEXT", ledger, model="gpt-6.1-sol", effort="high", **kw)


class SufficientFactsTests(unittest.TestCase):
    def test_case1_sufficient_verified_facts_gives_at_least_two_without_reeval(self):
        for sel in (["F01", "F02"], ["F01", "F02", "F03"], ["F01", "F02", "F03", "F04"]):
            parsed = _parsed(sel)
            client = _client(parsed)
            r = _run(client)
            self.assertEqual(client.responses.create.call_count, 1, sel)         # 再評価0回(case3)
            self.assertEqual(r["parsed"], parsed, sel)                           # parsedは入力と完全一致(既存正常例不変)
            self.assertFalse(r["min2_policy"]["reevaluated"])
            self.assertGreaterEqual(r["min2_policy"]["final_verified_n"], 2)

    def test_exactly_two_verified_has_no_reeval(self):
        parsed = _parsed(["F01", "F03"])
        client = _client(parsed)
        r = _run(client)
        self.assertEqual(client.responses.create.call_count, 1)
        self.assertEqual(r["parsed"]["selected_fact_ids"], ["F01", "F03"])


class ReevalTests(unittest.TestCase):
    def test_case2_old_behavior_one_fact_triggers_reeval_and_replaces_everything(self):
        first = _parsed(["F01"], storyline="FIRST STORYLINE")
        second = _parsed(["F01", "F02", "F03"], storyline="SECOND STORYLINE")
        client = _client(first, second)
        r = _run(client)
        self.assertEqual(client.responses.create.call_count, 2)
        self.assertEqual(r["parsed"], second)                                    # M4: 再評価call出力1回分で全置換(混ぜない)
        self.assertNotIn("FIRST STORYLINE", json.dumps(r["parsed"]))
        mp = r["min2_policy"]
        self.assertTrue(mp["reevaluated"])
        self.assertEqual(mp["first_pass_selected_ids"], ["F01"])
        self.assertEqual(mp["first_pass_verified_n"], 1)
        self.assertEqual(mp["first_attempt"]["selected_storyline"], "FIRST STORYLINE")   # 参考情報のみ
        self.assertEqual(mp["final_selected_ids"], ["F01", "F02", "F03"])

    def test_case5_verified_one_plus_ambiguous_one_triggers_reeval(self):
        first = _parsed(["F01", "F04"])           # 総数2だがVERIFIEDは1
        second = _parsed(["F01", "F02"])
        client = _client(first, second)
        r = _run(client)
        self.assertEqual(client.responses.create.call_count, 2)
        self.assertEqual(r["parsed"]["selected_fact_ids"], ["F01", "F02"])

    def test_reeval_prompt_contains_prohibition_topic_and_storyline_revision_clause(self):
        client = _client(_parsed(["F01"], storyline="FIRST"), _parsed(["F01", "F02"]))
        _run(client)
        user_prompt = client.responses.create.call_args_list[1].kwargs["input"][1]["content"]
        self.assertIn("TOPIC-TEXT", user_prompt)                                # topic(【テーマ】)
        self.assertIn("【テーマ】の範囲内で、中心Storylineを見直してかまいません", user_prompt)
        self.assertIn("【テーマ】から外れるStorylineは不可", user_prompt)
        self.assertIn("数合わせのために、関連性の低いFactや`[AMBIGUOUS]`のFactを検証済みとして扱ってはいけません", user_prompt)
        self.assertIn("テストの回答を変えずに採用判定だけを変えることは禁止", user_prompt)
        self.assertIn("初回のreasonは引き継がず", user_prompt)
        self.assertIn("初回のStoryline: FIRST", user_prompt)
        first_prompt = client.responses.create.call_args_list[0].kwargs["input"][1]["content"]
        self.assertNotIn("【再評価の指示】", first_prompt)                        # 初回Promptには再評価noteなし
        # 4テスト定義はそのまま(逐語)
        self.assertIn(b3.FACT_TEST_DEFINITIONS_JA, user_prompt)

    def test_case6_still_below_after_reeval_stops_with_record(self):
        client = _client(_parsed(["F01"]), _parsed(["F01", "F04"]))              # 再評価後もVERIFIED1(AMBIGUOUSは数えない)
        with self.assertRaises(b3.B3MinFactsStop) as cm:
            _run(client)
        self.assertEqual(client.responses.create.call_count, 2)                  # 無制限retryなし
        rec = cm.exception.record
        self.assertEqual(rec["reason"], "REEVAL_STILL_LT2")
        self.assertEqual(rec["selected_fact_ids"], ["F01", "F04"])
        self.assertEqual(rec["selected_verified_n"], 1)
        self.assertEqual({x["fact_id"] for x in rec["fact_reasons"]}, set(ALL_IDS))
        self.assertIn("timestamp", rec)

    def test_reeval_invalid_unknown_id_stops_no_third_call(self):
        bad = _parsed(["F01", "F02"])
        bad["selected_fact_ids"] = ["F01", "F99"]
        client = _client(_parsed(["F01"]), bad)
        with self.assertRaises(b3.B3MinFactsStop) as cm:
            _run(client)
        self.assertEqual(cm.exception.record["reason"], "REEVAL_INVALID")
        self.assertEqual(client.responses.create.call_count, 2)

    def test_reeval_call_exception_stops_as_reeval_invalid(self):
        client = _client(_parsed(["F01"]), RuntimeError("boom"))
        with self.assertRaises(b3.B3MinFactsStop) as cm:
            _run(client)
        self.assertEqual(cm.exception.record["reason"], "REEVAL_INVALID")
        self.assertEqual(client.responses.create.call_count, 2)

    def test_ledger_with_fewer_than_two_verified_stops_before_any_api_call(self):
        client = _client(_parsed(["F01"], ["F01", "F04"]))
        with self.assertRaises(b3.B3MinFactsStop) as cm:
            _run(client, ledger=LEDGER_ONE_VERIFIED)
        client.responses.create.assert_not_called()
        self.assertEqual(cm.exception.record["reason"], "LEDGER_VERIFIED_LT2")

    def test_code_never_adds_fact_ids(self):
        # コードはFactを選ばない: 最終selected_fact_idsは再評価応答のIDそのもの(補完・追加0)。
        second = _parsed(["F02", "F03"])
        client = _client(_parsed(["F01"]), second)
        r = _run(client)
        self.assertEqual(r["parsed"]["selected_fact_ids"], second["selected_fact_ids"])

    def test_min_verified_none_keeps_legacy_behavior_for_trial_callers(self):
        client = _client(_parsed(["F01"]))
        r = _run(client, min_verified_selected=None)
        self.assertEqual(client.responses.create.call_count, 1)
        self.assertEqual(r["parsed"]["selected_fact_ids"], ["F01"])
        self.assertFalse(r["min2_policy"]["enforced"])


class SoftWarningTests(unittest.TestCase):
    def test_case4_selected_despite_all_tests_exclude_is_recorded_as_soft_warning_only(self):
        parsed = _parsed(["F01", "F02", "F03"], all_exclude_selected=("F03",))
        client = _client(parsed)
        r = _run(client)
        self.assertEqual(client.responses.create.call_count, 1)                  # retry/再評価/STOPには使わない
        self.assertTrue(any(w.startswith("SELECTED_DESPITE_ALL_TESTS_EXCLUDE") and "F03" in w for w in r["soft_warnings"]))
        self.assertEqual(r["parsed"]["selected_fact_ids"], ["F01", "F02", "F03"])   # 採用数にも影響しない

    def test_no_warning_for_consistent_selection(self):
        r = _run(_client(_parsed(["F01", "F02"])))
        self.assertFalse(any("SELECTED_DESPITE" in w for w in r["soft_warnings"]))


class PromptAndShaTests(unittest.TestCase):
    def test_case7_unchanged_shas_and_pinned_reeval_note_sha(self):
        shas = b3.prompt_shas()
        self.assertEqual(shas["fact_test_definitions_sha256"], FACT_TEST_DEFINITIONS_SHA)
        self.assertEqual(shas["developer_message_sha256"], DEVELOPER_MESSAGE_SHA)
        self.assertEqual(b3.reeval_note_sha(), REEVAL_NOTE_TEMPLATE_SHA)

    def test_prompt_old_rule_removed_and_new_rule_present(self):
        p = b3.build_user_prompt("T", LEDGER)
        self.assertNotIn("3件未満でも", p)
        self.assertNotIn("目安は3〜5件", p)
        self.assertIn("`[VERIFIED]`のFactから最低2件を採用してください", p)
        self.assertIn("`[AMBIGUOUS]`のFactは採用してもかまいませんが、最低2件には数えません", p)
        self.assertIn("数合わせのための関連性の低いFactの追加は不可", p)
        self.assertNotIn("3件未満でも", b3.USER_PROMPT_TEMPLATE)

    def test_case8_producer_rules_sha256_unchanged(self):
        self.assertEqual(prod.rules_sha256(), RULES_SHA256_BEFORE)

    def test_json_schema_unchanged_keys(self):
        props = b3.STORYLINE_B3_JSON_SCHEMA["schema"]["properties"]
        self.assertEqual(sorted(props), ["fact_tests", "recheck_note", "selected_fact_brief", "selected_fact_ids",
                                         "selected_storyline"])


class CountingDefinitionTests(unittest.TestCase):
    def test_m3_verified_definition_is_producer_parse_ledger(self):
        facts, order = prod.parse_ledger(LEDGER)
        expected = [f for f in order if not facts[f]["ambiguous"]]
        self.assertEqual(b3.verified_fact_ids(LEDGER), expected)
        self.assertEqual(expected, ["F01", "F02", "F03"])
        self.assertEqual(b3.count_selected_verified(["F01", "F04", "F99"], LEDGER), 1)

    def test_m3_runner_guard_uses_the_same_function(self):
        with open(RUNNER_PY, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "assert_b3_min_verified")
        calls = [n.func.attr for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        self.assertIn("count_selected_verified", calls)


def _make_run_dir(selected, ledger=LEDGER, with_min2_key=False):
    d = tempfile.mkdtemp(prefix="b3min2_")
    os.makedirs(f"{d}/research_ledger")
    os.makedirs(f"{d}/storyline_b3/audit")
    with open(f"{d}/research_ledger/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
        f.write(ledger)
    with open(f"{d}/storyline_b3/selected_brief.md", "w", encoding="utf-8") as f:
        f.write("# Selected Fact Brief\nOLD\n")
    ev = {"selected_storyline": "OLD", "selected_fact_ids": list(selected)}
    if with_min2_key:
        ev["min2_policy"] = {"floor": 2}
    with open(f"{d}/storyline_b3/fact_selection_evidence.json", "w", encoding="utf-8") as f:
        json.dump(ev, f)
    return d


class RunnerGuardTests(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def mk(self, *a, **k):
        d = _make_run_dir(*a, **k)
        self.dirs.append(d)
        return d

    def test_guard_stops_on_old_one_fact_version(self):
        d = self.mk(["F01"])
        with self.assertRaises(b3.B3MinFactsStop) as cm:
            runner.assert_b3_min_verified(d)
        self.assertIn("--stage storyline_b3 --regenerate-stage storyline_b3", str(cm.exception))

    def test_guard_does_not_count_ambiguous(self):
        d = self.mk(["F01", "F04"])
        with self.assertRaises(b3.B3MinFactsStop):
            runner.assert_b3_min_verified(d)

    def test_guard_passes_existing_three_fact_run_without_min2_policy_key(self):
        d = self.mk(["F01", "F02", "F03"], with_min2_key=False)         # 判定根拠はselected_fact_idsのみ(既存3件以上runを止めない)
        runner.assert_b3_min_verified(d)

    def test_guard_stops_even_if_min2_policy_key_claims_floor(self):
        d = self.mk(["F01"], with_min2_key=True)
        with self.assertRaises(b3.B3MinFactsStop):
            runner.assert_b3_min_verified(d)

    def test_guard_passes_two_verified(self):
        runner.assert_b3_min_verified(self.mk(["F01", "F02"]))

    def test_run_storyline_b3_stop_writes_record_and_leaves_old_artifacts_untouched(self):
        d = self.mk(["F01"])
        brief = f"{d}/storyline_b3/selected_brief.md"
        ev = f"{d}/storyline_b3/fact_selection_evidence.json"
        os.utime(brief, (1_000_000_000, 1_000_000_000))
        os.utime(ev, (1_000_000_000, 1_000_000_000))
        before = (os.path.getmtime(brief), os.path.getmtime(ev), open(brief, encoding="utf-8").read())
        client = _client(_parsed(["F01"]), _parsed(["F01", "F04"]))
        with mock.patch.object(runner.routing, "require_model", return_value="gpt-6.1-sol"):
            with self.assertRaises(b3.B3MinFactsStop):
                runner.run_storyline_b3(client, "T", LEDGER, d)
        self.assertEqual((os.path.getmtime(brief), os.path.getmtime(ev), open(brief, encoding="utf-8").read()), before)
        rec = json.load(open(f"{d}/storyline_b3/b3_min2_stop_record.json", encoding="utf-8"))
        self.assertEqual(rec["reason"], "REEVAL_STILL_LT2")
        # 旧版(1件)が残った状態では合流点ガードが止める
        with self.assertRaises(b3.B3MinFactsStop):
            runner.assert_b3_min_verified(d)

    def test_ledger_lt2_stop_writes_record_without_api(self):
        d = self.mk(["F01"], ledger=LEDGER_ONE_VERIFIED)
        client = _client()
        with mock.patch.object(runner.routing, "require_model", return_value="gpt-6.1-sol"):
            with self.assertRaises(b3.B3MinFactsStop):
                runner.run_storyline_b3(client, "T", LEDGER_ONE_VERIFIED, d)
        client.responses.create.assert_not_called()
        rec = json.load(open(f"{d}/storyline_b3/b3_min2_stop_record.json", encoding="utf-8"))
        self.assertEqual(rec["reason"], "LEDGER_VERIFIED_LT2")

    def test_success_after_stop_supersedes_old_stop_record_and_records_min2_policy(self):
        d = self.mk(["F01"])
        with open(f"{d}/storyline_b3/b3_min2_stop_record.json", "w", encoding="utf-8") as f:
            json.dump({"reason": "REEVAL_STILL_LT2"}, f)
        client = _client(_parsed(["F01"]), _parsed(["F01", "F02"], storyline="NEW"))
        with mock.patch.object(runner.routing, "require_model", return_value="gpt-6.1-sol"):
            runner.run_storyline_b3(client, "T", LEDGER, d)
        names = os.listdir(f"{d}/storyline_b3")
        self.assertNotIn("b3_min2_stop_record.json", names)
        self.assertTrue(any(n.startswith("b3_min2_stop_record_superseded_") for n in names))
        ev = json.load(open(f"{d}/storyline_b3/fact_selection_evidence.json", encoding="utf-8"))
        self.assertEqual(ev["selected_fact_ids"], ["F01", "F02"])
        self.assertEqual(ev["selected_storyline"], "NEW")
        self.assertTrue(ev["min2_policy"]["reevaluated"])
        runner.assert_b3_min_verified(d)

    def test_case9_main_stage_writer_with_old_version_stops_at_guard_with_zero_api_and_no_producer(self):
        d = self.mk(["F01"])
        client = mock.Mock()
        argv = ["runner", "--theme", "T", "--slug", "s", "--out-dir", d, "--stage", "writer"]
        with mock.patch.object(sys, "argv", argv), \
                mock.patch.object(runner.cl, "install"), \
                mock.patch.object(runner.vfl01, "get_client", return_value=client), \
                mock.patch.object(runner, "run_research_and_ledger", return_value={"ledger_text": LEDGER}), \
                mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0), \
                mock.patch.object(runner, "run_annotation_producer") as prod_mock, \
                mock.patch.object(runner, "run_ja_writer") as writer_mock, \
                mock.patch.object(runner, "run_storyline_b3") as sl_mock:
            with self.assertRaises(b3.B3MinFactsStop):
                runner.main()
        prod_mock.assert_not_called()
        writer_mock.assert_not_called()
        sl_mock.assert_not_called()                   # 既存B3再利用経路(regenerateなし)でもガードに到達する
        self.assertEqual(client.mock_calls, [])       # API call 0

    def test_guard_is_called_immediately_before_run_annotation_producer_in_main(self):
        with open(RUNNER_PY, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        lines = {}
        for n in ast.walk(main):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                lines.setdefault(n.func.id, []).append(n.lineno)
        self.assertEqual(len(lines["assert_b3_min_verified"]), 1)
        self.assertEqual(len(lines["run_annotation_producer"]), 1)
        self.assertEqual(lines["run_annotation_producer"][0] - lines["assert_b3_min_verified"][0], 1)


class TrialCallerCompatTests(unittest.TestCase):
    def test_case10_er036_imports_and_runs_with_new_default(self):
        import er036_family_y_voice_structure_trial_01 as y
        client = _client(_parsed(["F01", "F02"]))
        with mock.patch.object(y, "save_json"):
            r = y.run_step1_fact_selection(client, "TOPIC", LEDGER, tempfile.gettempdir())
        self.assertEqual(r["parsed"]["selected_fact_ids"], ["F01", "F02"])
        self.assertEqual(r["min2_policy"]["floor"], 2)

    def test_producer_contract_and_trial_modules_unchanged_flags(self):
        # producer/契約はB3下限のために変更していない(参照のみ): B3MinFactsStop等の語を含まない
        for f in ("er053_b3_deterministic_producer_01.py", "er053_b3_annotation_contract_01.py"):
            with open(os.path.join(HERE, f), encoding="utf-8") as fh:
                src = fh.read()
            self.assertNotIn("B3MinFactsStop", src)
            self.assertNotIn("min_verified", src)


if __name__ == "__main__":
    unittest.main()
