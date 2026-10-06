"""unittest(pytest未導入のため標準unittest。pytestでも実行可)。"""
import unittest

import er052_open233_directional_trial_01 as t

LED_TXT = "The service is available in Japan."


def row(**kw):
    d = {"id": "1", "fact_id": "f", "ledger_fact_text": LED_TXT, "article_sentence": "It was shut down in Japan.",
         "expected_ledger_state": "AVAILABLE", "expected_article_state": "STOPPED", "subject_x": "the service"}
    d.update(kw)
    return d


class T(unittest.TestCase):
    def test_compare_all(self):
        cases = [("AVAILABLE", "AVAILABLE", "SAME"), ("AVAILABLE", "STOPPED", "REVERSED"),
                 ("AVAILABLE", "PAUSED", "REVERSED"), ("INCREASED", "DECREASED", "REVERSED"),
                 ("STARTED", "ENDED", "REVERSED"), ("EXPANDED", "NARROWED", "REVERSED"),
                 ("DECREASED", "INCREASED", "REVERSED"), ("PAUSED", "STOPPED", "SAME_FAMILY"),
                 ("STOPPED", "PAUSED", "SAME_FAMILY"), ("INCREASED", "NOT_MENTIONED", "NOT_MENTIONED"),
                 ("INCREASED", "UNCLEAR", "UNCLEAR"), ("UNCLEAR", "INCREASED", "UNCLEAR"),
                 ("INCREASED", "UNCHANGED", "UNCLEAR"), ("INCREASED", "bogus", "UNCLEAR"),
                 (t.NO_DIR, "STOPPED", "LEDGER_NO_DIRECTION")]
        for ls, a, exp in cases:
            with self.subTest(ls=ls, a=a):
                self.assertEqual(t.compare(ls, a), exp)

    def test_quote_missing_not_reversed(self):
        self.assertEqual(t.compare("AVAILABLE", "STOPPED", "", "q"), "UNCLEAR")
        self.assertEqual(t.compare("AVAILABLE", "STOPPED", "q", " "), "UNCLEAR")
        self.assertEqual(t.compare("AVAILABLE", "AVAILABLE", "", "q"), "UNCLEAR")

    def test_blind_prompt_has_no_ledger(self):
        for cfg in ("same_blind", "split_blind"):
            r = t.Runner(cfg, dry_run=True, model_article="dummy-model-B" if cfg == "split_blind" else None)
            res = r.process_row(row())
            art = [p for p in r.prompts if "[記事文]" in p]
            self.assertTrue(art)
            self.assertEqual(res["compare"], "REVERSED")
            for p in art:
                self.assertNotIn(LED_TXT, p)
                self.assertNotIn("AVAILABLE", p.split("[記事文]")[1])  # 記事文以降にLedger stateなし
                self.assertNotIn("is available", p)
                self.assertIn("the service", p)
            self.assertIn(LED_TXT, r.prompts[0])
            self.assertNotIn("shut down", r.prompts[0])

    def test_nonblind_one_call_has_both(self):
        r = t.Runner("same_nonblind", dry_run=True)
        self.assertEqual(r.process_row(row())["compare"], "REVERSED")
        self.assertEqual(r.calls, 1)
        self.assertIn(LED_TXT, r.prompts[0])
        self.assertIn("shut down", r.prompts[0])

    def test_budget_stops(self):
        r = t.Runner("same_blind", dry_run=True, budget_yen=0.0)
        with self.assertRaises(t.BudgetExceeded):
            r.process_row(row())
        self.assertEqual(r.calls, 0)

    def test_cache_same_fact_once(self):
        r = t.Runner("same_blind", dry_run=True)
        r.process_row(row(id="1"))
        r.process_row(row(id="2", article_sentence="Another sentence."))
        self.assertEqual(sum(1 for p in r.prompts if LED_TXT in p), 1)

    def test_enum_outside_is_unclear(self):
        self.assertEqual(t.norm_state("WEIRD"), "UNCLEAR")
        self.assertEqual(t.norm_state(None), "UNCLEAR")
        self.assertEqual(t.compare("AVAILABLE", "WEIRD"), "UNCLEAR")

    def test_unregistered_model_errors(self):
        with self.assertRaises(KeyError):
            t.cost_jpy("unknown-model", {"input_tokens": 1}, dry_run=False)


if __name__ == "__main__":
    unittest.main()
