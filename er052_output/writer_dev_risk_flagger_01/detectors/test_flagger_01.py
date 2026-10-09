# -*- coding: utf-8 -*-
"""委任_01B ユニットテスト(API不要)。実行: python -X utf8 -m unittest test_flagger_01 (detectors/ で)"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate_flagger_01 as AG  # noqa: E402
import d0_directional as D0  # noqa: E402
import flagger_lib as L  # noqa: E402
import make_blind_01 as MB  # noqa: E402
import prompts_flagger as P  # noqa: E402
import run_flagger_01 as R  # noqa: E402

FACT = ("MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、"
        "機能を当面ロールバックしたと社内投稿で説明した。")
K01 = "The company also restored the human concierge feature to the way it had been before, at least for now."
K03 = "They also temporarily put back the feature in which humans handled the calls."
K12 = "The human concierge feature was then put on hold for the time being."
K02S = "Nor has anyone reported that an AI got out of the test environment."


def unit(sentence, fact=FACT, uid="u1"):
    return dict(unit_id=uid, facts=[dict(fact_id="F1", text=fact)], sentences=[dict(sid="s1", text=sentence, before="", after="")])


class D0Test(unittest.TestCase):
    def test_k01_k03_flagged_rollback(self):
        for s in (K01, K03):
            fl = D0.detect(unit(s))
            self.assertTrue(any(f["type"] == "rollback反転" and f["severity"] == "重大" for f in fl), s)

    def test_faithful_sentence_not_flagged(self):
        self.assertEqual(D0.detect(unit(K12)), [])

    def test_japanese_k04(self):
        s = "人間コンシェルジュ機能を当面、以前の状態に戻しました。"
        self.assertTrue(any(f["type"] == "rollback反転" for f in D0.detect(unit(s))))

    def test_reverse_direction(self):
        f = "The company restored the feature on Monday."
        fl = D0.detect(unit("The company withdrew the feature on Monday.", fact=f))
        self.assertTrue(any(x["type"] == "rollback反転" for x in fl))

    def test_absence_cue(self):
        fl = D0.detect(unit(K02S, fact="Anthropic reported three incidents of unauthorized access."))
        self.assertTrue(any(x["type"] == "不在断定" for x in fl))

    def test_quantity(self):
        fl = D0.detect(unit("About 300 people joined in 2025.", fact="About 200 people joined in 2025."))
        self.assertTrue(any(x["type"] == "数量時系列" for x in fl))
        fl2 = D0.detect(unit("About 200 people joined in 2025.", fact="About 200 people joined in 2025."))
        self.assertFalse(any(x["type"] == "数量時系列" for x in fl2))

    def test_flag_has_required_fields(self):
        f = D0.detect(unit(K01))[0]
        for k in ("unit_id", "sentence_id", "type", "fact_ids", "confidence", "severity", "question", "basis"):
            self.assertIn(k, f)
        self.assertTrue(f["question"].endswith("。"))

    def test_mapping_picks_overlapping_fact(self):
        facts = [dict(fact_id="A", text="Acme raised 50 million dollars in 2024."),
                 dict(fact_id="B", text="Zeta Corp suspended the Orion service in March.")]
        top = D0.map_facts("Zeta Corp restored the Orion service.", facts, top_k=1)
        self.assertEqual(top[0][1]["fact_id"], "B")
        u = dict(unit_id="x", facts=facts, sentences=[dict(sid="s1", text="Zeta Corp restored the Orion service.")])
        fl = D0.detect(u)
        self.assertTrue(any(x["fact_ids"] == ["B"] and x["type"] == "rollback反転" for x in fl))


class ValidateTest(unittest.TestCase):
    def good(self):
        return json.dumps({"flags": [dict(sentence_id="s1", type="rollback反転", fact_ids=["F1"], confidence=0.8,
                                          severity="重大", question="向きは台帳どおりですか。")]}, ensure_ascii=False)

    def test_ok(self):
        fl, v = R.validate_flags(self.good(), unit(K01), ("rollback反転",))
        self.assertEqual(v, [])
        self.assertEqual(fl[0]["sentence"], K01)

    def test_empty_flags_ok(self):
        fl, v = R.validate_flags('{"flags":[]}', unit(K01))
        self.assertEqual((fl, v), ([], []))

    def test_bad_cases(self):
        u = unit(K01)
        self.assertIsNotNone(R.validate_flags("not json", u)[1])
        self.assertIsNone(R.validate_flags("not json", u)[0])
        bad = json.loads(self.good())
        bad["flags"][0]["sentence_id"] = "s9"
        self.assertIn("flag0_sentence_id_invalid", R.validate_flags(json.dumps(bad), u)[1])
        bad = json.loads(self.good())
        bad["flags"][0]["fact_ids"] = ["Z"]
        self.assertIn("flag0_fact_ids_invalid", R.validate_flags(json.dumps(bad), u)[1])
        bad = json.loads(self.good())
        bad["flags"][0]["type"] = "否定反転"
        self.assertIn("flag0_type_invalid", R.validate_flags(json.dumps(bad), u, ("rollback反転",))[1])
        bad = json.loads(self.good())
        bad["flags"][0]["confidence"] = 1.5
        self.assertIn("flag0_confidence_invalid", R.validate_flags(json.dumps(bad), u)[1])
        bad = json.loads(self.good())
        bad["flags"][0]["question"] = ""
        self.assertIn("flag0_question_missing", R.validate_flags(json.dumps(bad), u)[1])

    def test_wrapped_json_rescued(self):
        fl, v = R.validate_flags("結果です\n" + self.good() + "\n以上", unit(K01))
        self.assertEqual(v, [])


class LabelSeparationTest(unittest.TestCase):
    CASES = {"cases": [dict(case_id="c1", fact=FACT, sentence=K01, context_before="x", article_path="a.md",
                            label="重大", known_incident="K01", type_label="rollback反転"),
                       dict(case_id="c2", fact=FACT, sentence=K12, article_path="a.md", label="問題なし")]}

    def test_make_blind_drops_labels(self):
        blind, labels = MB.split_cases(self.CASES)
        self.assertEqual(R.check_no_labels({"cases": blind}), [])
        self.assertEqual(labels["c1"]["label"], "重大")
        self.assertNotIn("label", blind[0])

    def test_runner_refuses_labeled_input(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cb.json")
            json.dump(self.CASES, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            with self.assertRaises(ValueError):
                R.load_units(p)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.main(["--input", p, "--detector", "d0", "--set", "t"])
            self.assertEqual(rc, 2)

    def test_runner_source_never_opens_labels_file(self):
        src = open(os.path.join(HERE, "run_flagger_01.py"), encoding="utf-8").read()
        self.assertNotIn("_labels.json", src)
        self.assertNotIn("labels_path", src)

    def test_llm_prompt_contains_no_label_info(self):
        u = R.case_to_unit(MB.split_cases(self.CASES)[0][0])
        msg = P.build_user(u)
        for w in ("重大", "known_incident", "label", "type_label", "K01"):
            self.assertNotIn(w, msg)


class RunnerTest(unittest.TestCase):
    def test_d0_end_to_end_and_no_overwrite(self):
        blind, _ = MB.split_cases(LabelSeparationTest.CASES)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cb_blind.json")
            json.dump({"cases": blind}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            old = R.RESULTS_DIR
            R.RESULTS_DIR = os.path.join(d, "results")
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    self.assertEqual(R.main(["--input", p, "--detector", "d0", "--set", "t"]), 0)
                    self.assertEqual(R.main(["--input", p, "--detector", "d0", "--set", "t"]), 3)  # 上書き禁止
                rows = [json.loads(x) for x in open(os.path.join(R.RESULTS_DIR, "d0_none_t.jsonl"), encoding="utf-8")]
            finally:
                R.RESULTS_DIR = old
        by = {r["unit_id"]: r for r in rows}
        self.assertTrue(by["c1"]["flags"])
        self.assertEqual(by["c2"]["flags"], [])
        self.assertEqual(by["c1"]["cost_jpy"], 0.0)

    def test_llm_requires_max_yen_and_dry_run_no_api(self):
        blind, _ = MB.split_cases(LabelSeparationTest.CASES)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cb_blind.json")
            json.dump({"cases": blind}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(R.main(["--input", p, "--detector", "d2", "--set", "t"]), 2)
                self.assertEqual(R.main(["--input", p, "--detector", "d1map", "--set", "t", "--dry-run"]), 0)
            out = buf.getvalue()
            self.assertIn("REFUSED", out)
            self.assertIn("呼び出し数(最小)=10", out)  # 2 units x 5 types

    def test_plan_calls_modes(self):
        facts = [dict(fact_id="A", text="Acme raised 50 million dollars in 2024."),
                 dict(fact_id="B", text="Zeta Corp suspended the Orion service."),
                 dict(fact_id="C", text="Foo Inc hired 10 staff."), dict(fact_id="D", text="Bar Ltd closed.")]
        u = dict(unit_id="x", facts=facts, sentences=[dict(sid="s1", text="Zeta Corp restored the Orion service.")])
        full = R.plan_calls("d1full", u)
        mp = R.plan_calls("d1map", u)
        self.assertEqual(len(full), 5)
        self.assertEqual(len(R.plan_calls("d2", u)), 1)
        self.assertEqual(len(json.loads(full[0][2])["facts"]), 4)
        self.assertLessEqual(len(json.loads(mp[0][2])["facts"]), 3)
        self.assertEqual(json.loads(mp[0][2])["facts"][0]["fact_id"], "B")

    def test_article_mode_units(self):
        with tempfile.TemporaryDirectory() as d:
            lp, ap_ = os.path.join(d, "l.json"), os.path.join(d, "a.md")
            json.dump({"facts": [dict(fact_id="F1", text="Acme paused the plan.")]}, open(lp, "w"))
            open(ap_, "w", encoding="utf-8").write("# Title\nAcme resumed the plan. It was big.\n\nNext para.")
            us = R.load_units(ledger=lp, article=ap_)
        self.assertEqual(len(us), 1)
        self.assertEqual(us[0]["sentences"][0]["text"], "Acme resumed the plan.")
        self.assertEqual(us[0]["sentences"][1]["text"], "It was big.")


class UnionTest(unittest.TestCase):
    def fl(self, t, c, sid="s1", q="q。"):
        return dict(unit_id="u", sentence_id=sid, type=t, fact_ids=["F1"], confidence=c, severity="重大", question=q)

    def test_dedup_and_keep_distinct_types(self):
        out = R.union_flags([("d0", [self.fl("rollback反転", 0.7, q="a。")]),
                             ("d1map", [self.fl("rollback反転", 0.9, q="b。"), self.fl("否定反転", 0.5)])])
        self.assertEqual(len(out), 2)
        rb = [x for x in out if x["type"] == "rollback反転"][0]
        self.assertEqual(rb["confidence"], 0.9)
        self.assertEqual(rb["question"], "b。")
        self.assertEqual(sorted(rb["sources"]), ["d0", "d1map"])


class AggregateTest(unittest.TestCase):
    def test_metrics(self):
        labels = {"c1": dict(label="重大", known_incident="K01", type_label="rollback反転"),
                  "c2": dict(label="重大", known_incident="K02", type_label="不在断定"),
                  "c3": dict(label="問題なし"), "c4": dict(label="問題なし"), "c5": dict(label="B")}
        f = lambda: [dict(type="rollback反転", confidence=0.7, severity="重大")]  # noqa: E731
        rows = [dict(unit_id="c1", flags=f(), valid_json=True, cost_jpy=1.0), dict(unit_id="c2", flags=[], valid_json=True, cost_jpy=1.0),
                dict(unit_id="c3", flags=f(), valid_json=True, cost_jpy=0.5), dict(unit_id="c4", flags=[], valid_json=True, cost_jpy=0.5),
                dict(unit_id="c5", flags=f(), valid_json=True, cost_jpy=0)]
        r = AG.aggregate(labels, rows)
        self.assertEqual(r["recall_severe"], 0.5)
        self.assertEqual(r["case_precision"], 0.5)
        self.assertEqual(r["missed_severe"], ["c2"])
        self.assertEqual(r["false_positive_cases"], ["c3"])
        self.assertEqual(r["border_flagged"], ["c5"])
        self.assertAlmostEqual(r["flags_per_unit"], 0.6)
        self.assertTrue(r["known_incidents"]["K01"]["hit"])
        self.assertFalse(r["known_incidents"]["K02"]["hit"])
        self.assertEqual(r["recall_by_type"]["不在断定"]["recall"], 0.0)
        self.assertAlmostEqual(r["cost_jpy"], 3.0)
        self.assertIn("Recall", AG.to_markdown([("x", r)]))

    def test_min_conf(self):
        labels = {"c1": dict(label="重大")}
        rows = [dict(unit_id="c1", flags=[dict(type="t", confidence=0.3, severity="重大")], valid_json=True, cost_jpy=0)]
        self.assertEqual(AG.aggregate(labels, rows, min_conf=0.5)["recall_severe"], 0.0)
        self.assertEqual(AG.aggregate(labels, rows, min_conf=0.2)["recall_severe"], 1.0)


class CostGuardTest(unittest.TestCase):
    def test_prices_registered_and_latest_only(self):
        for m in L.MODELS:
            self.assertIsNotNone(L.load_prices(m), m)
        self.assertEqual(L.load_prices("gpt-6.1-sol"), (2.0, 0.1, 10.0))
        self.assertEqual(L.load_prices("deepseek-v4-pro"), (1.32, 0.044, 3.96))
        for old in ("gpt-5.6-sol", "gpt-5.6-luna", "gpt-6-luna", "deepseek-v4-flash"):
            self.assertNotIn(old, L.MODELS)  # 最新原則: 旧モデルは使わない
        self.assertIsNone(L.load_prices("gpt-99-mystery"))

    def test_cost_formula(self):
        p = L.load_prices("gpt-6.1-sol")
        self.assertAlmostEqual(L.cost_yen(p, 1_000_000, 1_000_000), (2.0 + 10.0) * L.USD_JPY)

    def test_ledger_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "ledger.jsonl")
            L.ledger_append(dict(cost_jpy=1.5), p)
            L.ledger_append(dict(cost_jpy=2.0), p)
            self.assertAlmostEqual(L.ledger_total(p), 3.5)

    def test_cap_stops_before_call(self):
        # 台帳累計が上限以上なら、API呼び出し前に停止(戻り値4)。クライアントはダミーで差し替え。
        blind, _ = MB.split_cases(LabelSeparationTest.CASES)
        units = [R.case_to_unit(c) for c in blind]
        with tempfile.TemporaryDirectory() as d:
            oldp, oldr, oldc = L.LEDGER_PATH, R.RESULTS_DIR, L.client_for
            L.LEDGER_PATH = os.path.join(d, "l.jsonl")
            L.ledger_append(dict(cost_jpy=999.0), L.LEDGER_PATH)
            R.RESULTS_DIR, R.LOGS_DIR = os.path.join(d, "r"), os.path.join(d, "lg")
            L.client_for = lambda cfg: object()
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = R.run_llm(units, "d2", "gpt-6.1-sol", "t", 10.0, 900.0)
            finally:
                L.LEDGER_PATH, R.RESULTS_DIR, L.client_for = oldp, oldr, oldc
        self.assertEqual(rc, 4)


class FakeLLMTest(unittest.TestCase):
    def test_retry_once_on_bad_format_then_ok(self):
        blind, _ = MB.split_cases(LabelSeparationTest.CASES)
        units = [R.case_to_unit(blind[0])]
        good = json.dumps({"flags": [dict(sentence_id="s1", type="rollback反転", fact_ids=["F"], confidence=0.8,
                                          severity="重大", question="向きは台帳どおりですか。")]}, ensure_ascii=False)
        seq = ["garbage", good]
        calls = []

        def fake_call(client, model, system, user, max_out=None, effort="medium"):
            calls.append(1)
            return seq[len(calls) - 1], dict(input_tokens=1000, output_tokens=500, cached_tokens=0), "rid", model

        with tempfile.TemporaryDirectory() as d:
            saved = (L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model)
            L.LEDGER_PATH = os.path.join(d, "l.jsonl")
            R.RESULTS_DIR, R.LOGS_DIR = os.path.join(d, "r"), os.path.join(d, "lg")
            L.client_for = lambda cfg: object()
            L.call_model = fake_call
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = R.run_llm(units, "d2", "gpt-6.1-sol", "t", 50.0, 900.0)
                rows = [json.loads(x) for x in open(os.path.join(R.RESULTS_DIR, "d2_gpt-6.1-sol_t.jsonl"), encoding="utf-8")]
                total = L.ledger_total()
            finally:
                L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model = saved
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)  # 初回+再呼び出し1回(上限)
        self.assertTrue(rows[0]["valid_json"])
        self.assertEqual(len(rows[0]["flags"]), 1)
        self.assertGreater(total, 0)

    def test_second_failure_gives_up(self):
        blind, _ = MB.split_cases(LabelSeparationTest.CASES)
        units = [R.case_to_unit(blind[0])]
        calls = []

        def fake_call(client, model, system, user, max_out=None, effort="medium"):
            calls.append(1)
            return "garbage", dict(input_tokens=10, output_tokens=10, cached_tokens=0), "rid", model

        with tempfile.TemporaryDirectory() as d:
            saved = (L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model)
            L.LEDGER_PATH = os.path.join(d, "l.jsonl")
            R.RESULTS_DIR, R.LOGS_DIR = os.path.join(d, "r"), os.path.join(d, "lg")
            L.client_for = lambda cfg: object()
            L.call_model = fake_call
            try:
                with redirect_stdout(io.StringIO()):
                    R.run_llm(units, "d2", "gpt-6.1-sol", "t", 50.0, 900.0)
                rows = [json.loads(x) for x in open(os.path.join(R.RESULTS_DIR, "d2_gpt-6.1-sol_t.jsonl"), encoding="utf-8")]
            finally:
                L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model = saved
        self.assertEqual(len(calls), 2)
        self.assertFalse(rows[0]["valid_json"])


class PromptTest(unittest.TestCase):
    def test_d1_prompt_single_type(self):
        for t in P.TYPES:
            s = P.d1_system(t)
            self.assertIn("「%s」" % t, s)
            self.assertIn("1タイプだけ", s)
            self.assertIn("修正案", s)  # 修正案を出さない旨
        self.assertIn("軽微", P.d2_system())


if __name__ == "__main__":
    unittest.main()
