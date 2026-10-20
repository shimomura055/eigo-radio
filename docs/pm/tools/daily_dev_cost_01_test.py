"""daily_dev_cost_01 の unit test(合成ログ。API 0)。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daily_dev_cost_01 as d  # noqa: E402

PRICING = {"prices": [
    {"provider": "openai", "model": "m1", "meter": "input_tokens", "tier": "Standard", "price": 1.0},
    {"provider": "openai", "model": "m1", "meter": "output_tokens", "tier": "Standard", "price": 2.0},
    {"provider": "openai", "model": "N/A", "meter": "web_search_call", "tier": "Standard", "price": 10.0},
]}


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        w(os.path.join(self.root, d.PRICING_REL), json.dumps(PRICING))

    def tearDown(self):
        self.tmp.cleanup()

    def log(self, rows):
        w(os.path.join(self.root, "run1", "raw_usage_log.jsonl"), "\n".join(json.dumps(r) for r in rows))

    def test_jst_date_boundary(self):
        # UTC 10-14 15:30 = JST 10-15 00:30 / UTC 10-15 14:59 = JST 10-15 23:59 / UTC 10-15 15:00 = JST 10-16
        self.log([
            {"timestamp": "2026-10-14T15:30:00+00:00", "provider": "openai", "model_id": "m1", "input_tokens": 1000000},
            {"timestamp": "2026-10-15T14:59:00+00:00", "provider": "openai", "model_id": "m1", "input_tokens": 1000000},
            {"timestamp": "2026-10-15T15:00:00+00:00", "provider": "openai", "model_id": "m1", "input_tokens": 1000000},
            {"timestamp": "2026-10-14T14:59:00+00:00", "provider": "openai", "model_id": "m1", "input_tokens": 1000000},
        ])
        r = d.aggregate_logs(self.root, "2026-10-15", d.load_prices(self.root))
        self.assertEqual(r["records"], 2)
        self.assertAlmostEqual(r["total_jpy"], 2 * 1.0 * 160, places=2)

    def test_cost_usd_adopted_and_websearch(self):
        self.log([
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "x", "cost_usd": 0.5},
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "m1",
             "output_tokens": 1000000, "web_search_call_count": 100},
        ])
        r = d.aggregate_logs(self.root, "2026-10-15", d.load_prices(self.root))
        self.assertAlmostEqual(r["total_jpy"], (0.5 + 2.0 + 1.0) * 160, places=2)

    def test_unpriced_not_zero_priced(self):
        self.log([{"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "unknown",
                   "input_tokens": 5000}])
        r = d.aggregate_logs(self.root, "2026-10-15", d.load_prices(self.root))
        self.assertEqual(r["total_jpy"], 0.0)
        self.assertEqual(r["unpriced"], {"openai/unknown": 1})

    def test_synthetic_dryrun_rows_excluded_from_real_cost(self):
        # 正例: 実行(OFFICIAL_API_RESPONSE)/usage_source欠落は計上。負例: SYNTHETIC_DRYRUN_STUB・STUBは除外し別枠
        self.log([
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "m1", "input_tokens": 1000000,
             "usage_source": "OFFICIAL_API_RESPONSE"},
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "m1", "input_tokens": 1000000},
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "m1", "input_tokens": 1000000,
             "usage_source": "SYNTHETIC_DRYRUN_STUB"},
            {"timestamp": "2026-10-15T01:00:00Z", "provider": "openai", "model_id": "m1", "input_tokens": 500000,
             "usage_source": "STUB"},
        ])
        r = d.aggregate_logs(self.root, "2026-10-15", d.load_prices(self.root))
        self.assertEqual(r["records"], 2)
        self.assertAlmostEqual(r["total_jpy"], 2 * 1.0 * 160, places=2)
        self.assertEqual(r["excluded_synthetic"]["records"], 2)
        self.assertAlmostEqual(r["excluded_synthetic"]["jpy"], 1.5 * 160, places=2)

    def test_ledger_and_max(self):
        self.log([{"timestamp": "2026-10-15T01:00:00Z", "provider": "x", "cost_usd": 0.01}])
        led = os.path.join(self.root, "L.md")
        w(led, "- 2026-10-15 | A 費用JPY7.04(推定)\n- 2026-10-14 | B 費用JPY99\n- 2026-10-15 | C 費用JPY0\n")
        r = d.run("2026-10-15", self.root, led)
        self.assertEqual(r["ledger"]["total_jpy"], 7.04)
        self.assertEqual(r["ledger"]["rows"], 2)
        self.assertEqual(r["adopted_jpy"], 7.04)


if __name__ == "__main__":
    unittest.main()
