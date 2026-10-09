# -*- coding: utf-8 -*-
"""run_eval_01.py の単体テスト(API不要)。 実行: python run_eval_01_test.py"""
import json
import os
import re
import tempfile
import unittest

import run_eval_01 as R

HERE = os.path.dirname(os.path.abspath(__file__))


def ok(label="A", mt="なし", cid="x1", reason="根拠"):
    return json.dumps({"case_id": cid, "label": label, "reason": reason, "misread_type": mt}, ensure_ascii=False)


class ValidateTest(unittest.TestCase):
    def v(self, text, cid="x1"):
        return R.validate_result(text, cid)

    def test_valid_cases(self):
        for lab, mt in [("A", "なし"), ("B", "その他"), ("B", "台帳と逆"), ("C", "主体対象入替"), ("C", "肯定否定方向反転"),
                        ("C", "数量時系列変更"), ("C", "台帳と逆")]:
            obj, viol, _ = self.v(ok(lab, mt))
            self.assertEqual(viol, [], (lab, mt))
            self.assertIsNotNone(obj)

    def test_C_with_other_or_none_is_violation(self):
        for mt in ("その他", "なし"):
            obj, viol, _ = self.v(ok("C", mt))
            self.assertIsNone(obj)
            self.assertIn("C_misread_must_be_one_of_four", viol)

    def test_A_requires_none(self):
        obj, viol, _ = self.v(ok("A", "その他"))
        self.assertIsNone(obj)
        self.assertIn("A_requires_misread_none", viol)

    def test_B_none_violation(self):
        obj, viol, _ = self.v(ok("B", "なし"))
        self.assertIn("B_misread_none_not_allowed", viol)

    def test_bad_json_and_fence(self):
        self.assertIsNone(self.v("not json")[0])
        self.assertIsNone(self.v("```json\n" + ok() + "\n```")[0])
        self.assertIn("not_a_json_object", self.v("[1,2]")[1])

    def test_enum_and_case_id(self):
        self.assertIn("label_invalid", self.v(ok("D", "なし"))[1])
        self.assertIn("misread_type_invalid", self.v(ok("A", "unknown"))[1])
        self.assertIn("case_id_mismatch", self.v(ok(cid="other"))[1])

    def test_reason_over_60_is_warning_only(self):
        obj, viol, warn = self.v(ok("A", "なし", reason="あ" * 61))
        self.assertIsNotNone(obj)
        self.assertEqual(viol, [])
        self.assertTrue(any(w.startswith("reason_over_60") for w in warn))

    def test_reason_missing(self):
        t = json.dumps({"case_id": "x1", "label": "A", "misread_type": "なし"})
        self.assertIn("reason_missing", self.v(t)[1])


class IsolationTest(unittest.TestCase):
    def test_user_message_has_only_five_keys(self):
        items = R.load_items()
        self.assertEqual(len(items), 10)
        for it in items:
            msg = json.loads(R.build_user_message(it))
            self.assertEqual(list(msg.keys()), list(R.PASS_KEYS))
            self.assertNotIn("context_source", msg)

    def test_items_file_has_no_human_or_checker_keys(self):
        allowed = set(R.PASS_KEYS) | {"context_source"}
        for it in R.load_items():
            self.assertTrue(set(it) <= allowed, set(it) - allowed)

    def test_source_never_opens_cases_json(self):
        src = open(os.path.join(HERE, "run_eval_01.py"), encoding="utf-8").read()
        self.assertIsNone(re.search(r"cases_01", src))
        self.assertIsNone(re.search(r"CASES_01", src))
        self.assertNotIn("human_tier", src)

    def test_prompt_example_changed_and_no_old_example(self):
        p = R.load_prompt()
        self.assertNotIn("撤回⇔再開", p)
        self.assertIn("承認⇔却下", p)


class GuardTest(unittest.TestCase):
    def test_deepseek_refused_without_flag(self):
        self.assertEqual(R.main(["--model", "deepseek-v4-flash", "--rep", "1"]), 2)

    def test_luna_requires_max_yen(self):
        self.assertEqual(R.main(["--model", "gpt-6-luna", "--rep", "1"]), 2)

    def test_dry_run_ok_both(self):
        self.assertEqual(R.main(["--model", "gpt-6-luna", "--dry-run", "--max-yen", "30"]), 0)
        self.assertEqual(R.main(["--model", "deepseek-v4-flash", "--dry-run"]), 0)

    def test_pricing_luna_registered_deepseek_not(self):
        self.assertIsNotNone(R.load_prices("gpt-6-luna"))
        self.assertIsNone(R.load_prices("deepseek-v4-flash"))


class RunLoopTest(unittest.TestCase):
    """call_model を差し替えた疑似APIで、再呼び出し上限・保存・上書き禁止を確認(実APIは呼ばない)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig_here = R.HERE
        self._orig_client = R._client
        self._orig_call = R.call_model
        R.HERE = self.tmp
        R._client = lambda cfg: object()
        self.calls = []

    def tearDown(self):
        R.HERE = self._orig_here
        R._client = self._orig_client
        R.call_model = self._orig_call

    def fake(self, responder):
        def call(client, model, cfg, prompt, user_msg, temperature, eff):
            cid = json.loads(user_msg)["case_id"]
            self.calls.append(cid)
            eff["temperature"] = 0.0
            return responder(cid, len([c for c in self.calls if c == cid])), {"input_tokens": 1000, "output_tokens": 500}, "rid", "m"
        R.call_model = call

    def rows(self):
        p = os.path.join(self.tmp, "results", "gpt-6-luna_rep1.jsonl")
        return [json.loads(x) for x in open(p, encoding="utf-8")]

    def test_one_format_retry_then_adopt(self):
        items = R.load_items()[:2]
        bad_cid = items[0]["case_id"]
        self.fake(lambda cid, n: "oops" if (cid == bad_cid and n == 1) else ok("A", "なし", cid))
        rc = R.run("gpt-6-luna", 1, items, "P", 30, 0.0)
        self.assertEqual(rc, 0)
        self.assertEqual(self.calls.count(bad_cid), 2)
        rows = [r for r in self.rows() if not r.get("_summary")]
        self.assertTrue(all(r["valid_json"] for r in rows))
        self.assertEqual(rows[0]["attempts"], 2)
        raw = [json.loads(x) for x in open(os.path.join(self.tmp, "logs", "gpt-6-luna_rep1_raw.jsonl"), encoding="utf-8")]
        self.assertEqual(len(raw), 3)  # 元の違反応答も保存
        self.assertEqual(raw[0]["response_text"], "oops")

    def test_persistent_violation_marks_invalid_and_does_not_loop(self):
        items = R.load_items()[:1]
        self.fake(lambda cid, n: ok("C", "その他", cid))
        R.run("gpt-6-luna", 1, items, "P", 30, 0.0)
        self.assertEqual(len(self.calls), 2)  # 初回+再呼び出し1回のみ
        r = [x for x in self.rows() if not x.get("_summary")][0]
        self.assertFalse(r["valid_json"])
        self.assertIsNone(r["label"])

    def test_refuses_overwrite(self):
        items = R.load_items()[:1]
        self.fake(lambda cid, n: ok("A", "なし", cid))
        self.assertEqual(R.run("gpt-6-luna", 1, items, "P", 30, 0.0), 0)
        self.assertEqual(R.run("gpt-6-luna", 1, items, "P", 30, 0.0), 3)

    def test_budget_cap_stops(self):
        items = R.load_items()[:3]
        self.fake(lambda cid, n: ok("A", "なし", cid))
        rc = R.run("gpt-6-luna", 1, items, "P", 0.0, 0.0)  # 上限0円 -> 最初の呼び出し前に停止
        self.assertEqual(rc, 4)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
