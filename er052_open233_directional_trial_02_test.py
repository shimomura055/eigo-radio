"""unittest(標準unittest)。TRIAL-02: 事象選択のみ比較。"""
import json
import os
import tempfile
import unittest

import er052_open233_directional_trial_02 as t

LED_TXT = "The service is available in Japan."
EV_A = {"subject_x": "service", "result_state": "AVAILABLE", "quote": "available"}
EV_B = {"subject_x": "price", "result_state": "DECREASED", "quote": "cut"}
EV_C = {"subject_x": "price", "result_state": "INCREASED", "quote": "up"}


def row(**kw):
    d = {"id": "1", "fact_id": "f", "label": "x", "ledger_fact_text": LED_TXT,
         "article_sentence": "It was shut down in Japan.", "expected_ledger_state": "AVAILABLE",
         "expected_article_state": "STOPPED", "subject_x": "service"}
    d.update(kw)
    return d


def runner(cache, **kw):
    return t.Runner("shard_1of1", dry_run=True, ledger_cache=cache, **kw)


class T(unittest.TestCase):
    def test_selected_only_no_bruteforce(self):
        # 選択=price(DECREASED)がSAME。別event(service AVAILABLE)と逆方向になる状態でも比較しない
        r = t.compare_selected([EV_A, EV_B], "price", "DECREASED", "cut")
        self.assertEqual(r["compare"], "SAME")
        self.assertEqual(r["ledger_state"], "DECREASED")
        r = t.compare_selected([EV_A, EV_B], "service", "STOPPED", "q")
        self.assertEqual(r["compare"], "REVERSED")

    def test_same_subject_prefers_match(self):
        self.assertEqual(t.compare_selected([EV_B, EV_C], "price", "INCREASED", "up")["compare"], "SAME")
        self.assertEqual(t.compare_selected([EV_B, EV_C], "price", "NARROWED", "q")["compare"], "UNCLEAR")

    def test_none_and_outside_label(self):
        self.assertEqual(t.compare_selected([EV_A], "NONE", "STOPPED", "q")["compare"], "NOT_MENTIONED")
        self.assertEqual(t.compare_selected([EV_A], "other", "STOPPED", "q")["compare"], "UNCLEAR")
        self.assertEqual(t.compare_selected([EV_A], "__CALL_FAILED__", "UNCLEAR", "")["compare"], "UNCLEAR")

    def test_blind_prompt(self):
        r = runner({"f": {"rep1": [EV_A, EV_B]}})
        res = r.process_row(row())
        self.assertEqual(res["final_compare_rep0"], "REVERSED")
        self.assertEqual(r.calls, 1)  # 選択+抽出で1 call
        p = r.prompts[0]
        head, body = p.split("[対象一覧]")
        for bad in (LED_TXT, "is available", "DECREASED", "cut", "available"):
            self.assertNotIn(bad, body)
        self.assertNotIn("AVAILABLE", body)  # Ledger stateはprompt本体に無い(enum説明は先頭部のみ)
        self.assertIn("- service", body)
        self.assertIn("- price", body)

    def test_no_events_no_call(self):
        r = runner({"f": {"rep1": []}})
        self.assertEqual(r.process_row(row())["final_compare_rep0"], "LEDGER_NO_DIRECTION")
        self.assertEqual(r.calls, 0)

    def test_dummy_none_selected(self):
        r = runner({"f": {"rep1": [EV_A]}})
        self.assertEqual(r.process_row(row(expected_article_state=""))["final_compare_rep0"], "NOT_MENTIONED")

    def test_repeat_uses_same_rep_events(self):
        cache = {"f": {"rep1": [EV_A], "rep2": [dict(EV_A, subject_x="svc2")], "rep3": [EV_A]}}
        res = runner(cache).process_row(row(repeat=3))
        self.assertEqual([x["ledger_events_subjects"] for x in res["repeats"]],
                         [["service"], ["svc2"], ["service"]])
        self.assertEqual(len(res["final_compares"]), 3)

    def test_shard_partition(self):
        rows = [{"id": f"I{k:02d}"} for k in range(10)]
        for n in (1, 3, 4):
            got = [x["id"] for i in range(1, n + 1) for x in t.shard_items(rows, i, n)]
            self.assertEqual(sorted(got), sorted(x["id"] for x in rows))
            self.assertEqual(len(got), len(set(got)))

    def test_budget_stops(self):
        r = runner({"f": {"rep1": [EV_A]}}, budget_yen=0.0)
        with self.assertRaises(t.BudgetExceeded):
            r.process_row(row())
        self.assertEqual(r.calls, 0)

    def _meta(self, d, i, n, h):
        with open(os.path.join(d, f"run_meta_shard_{i}of{n}.json"), "w") as f:
            json.dump({"shard": i, "n_shards": n, "input_hash": h, "n_items_expected": 0, "calls": 0}, f)
        open(os.path.join(d, f"results_shard_{i}of{n}.jsonl"), "w").close()

    def test_merge_hash_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            self._meta(d, 1, 2, "aaa")
            self._meta(d, 2, 2, "bbb")
            with self.assertRaises(SystemExit):
                t.merge(d)

    def test_merge_missing_shard_stops(self):
        with tempfile.TemporaryDirectory() as d:
            self._meta(d, 1, 2, "a")
            with self.assertRaises(SystemExit):
                t.merge(d)

    def test_trial01_ported(self):
        self.assertEqual(t.compare("AVAILABLE", "STOPPED"), "REVERSED")
        self.assertEqual(t.compare("PAUSED", "STOPPED"), "SAME_FAMILY")
        self.assertEqual(t.compare("AVAILABLE", "STOPPED", "", "q"), "UNCLEAR")
        self.assertEqual(t.norm_state("WEIRD"), "UNCLEAR")
        with self.assertRaises(KeyError):
            t.t1.cost_jpy("unknown-model", {"input_tokens": 1}, dry_run=False)


if __name__ == "__main__":
    unittest.main()
