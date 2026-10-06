"""unittest。TRIAL-03: phase一意照合 + NONE限定フォールバック。"""
import json
import os
import tempfile
import unittest

import er052_open233_directional_trial_03 as t

LED = "The service was briefly stopped, then restored."
EV_I = {"subject_x": "service", "result_state": "STOPPED", "phase": "INTERIM", "quote": "briefly stopped"}
EV_F = {"subject_x": "service", "result_state": "AVAILABLE", "phase": "FINAL", "quote": "restored"}
EV_P = {"subject_x": "price", "result_state": "DECREASED", "phase": "SINGLE", "quote": "cut"}


def row(**kw):
    d = {"id": "1", "fact_id": "f", "label": "x", "ledger_fact_text": LED, "article_sentence": "It was stopped.",
         "expected_ledger_state": "AVAILABLE", "expected_article_state": "STOPPED", "subject_x": "service"}
    d.update(kw)
    return d


def runner(cache, cfg="Y", **kw):
    return t.Runner("t", cfg, dry_run=True, ledger_cache=cache, **kw)


class T(unittest.TestCase):
    def test_phase_unique_match(self):
        evs = [EV_I, EV_F]
        r = t.compare_phase(evs, "service", "STOPPED", "q", "INTERIM")
        self.assertEqual((r["compare"], r["matched_event_phase"]), ("SAME", "INTERIM"))
        for ap in ("FINAL", "UNSPECIFIED"):
            r = t.compare_phase(evs, "service", "STOPPED", "q", ap)
            self.assertEqual((r["compare"], r["matched_event_phase"]), ("REVERSED", "FINAL"))
        r = t.compare_phase([EV_P], "price", "DECREASED", "q", "FINAL")
        self.assertEqual((r["compare"], r["matched_event_phase"]), ("SAME", "SINGLE"))

    def test_phase_no_match_unclear(self):
        self.assertEqual(t.compare_phase([EV_F], "service", "STOPPED", "q", "INTERIM")["compare"], "UNCLEAR")
        self.assertEqual(t.compare_phase([EV_I], "service", "STOPPED", "q", "FINAL")["compare"], "UNCLEAR")
        self.assertEqual(t.compare_phase([EV_F], "other", "STOPPED", "q", "FINAL")["compare"], "UNCLEAR")

    def test_phase_missing_is_single(self):
        e = {"subject_x": "a", "result_state": "AVAILABLE", "quote": "q"}
        self.assertEqual(t.norm_lphase(e), "SINGLE")
        self.assertEqual(t.compare_phase([e], "a", "STOPPED", "q", "FINAL")["compare"], "REVERSED")

    def test_x_ignores_phase(self):
        r = t.compare_x([EV_I, EV_F], "service", "STOPPED", "q")  # SAME優先(INTERIMと一致)
        self.assertEqual(r["compare"], "SAME")

    def test_no_fallback_when_selected(self):
        r = runner({"f": {"rep1": [EV_F, EV_P]}})
        res = r.process_row(row())
        rep = res["repeats"][0]
        self.assertFalse(rep["fallback_used"])
        self.assertEqual((r.calls, r.fb_calls), (1, 0))

    def test_fallback_only_on_none(self):
        for cfg in ("X", "Y"):
            r = runner({"f": {"rep1": [EV_F, EV_P]}}, cfg)
            res = r.process_row(row(expected_article_state=""))
            rep = res["repeats"][0]
            self.assertTrue(rep["fallback_used"])
            self.assertEqual(rep["compare"], "NOT_MENTIONED")
            self.assertEqual(rep["fallback_calls"], 2)  # eventごと1 call
            self.assertEqual(r.calls, 3)

    def test_fallback_y_phase_filter(self):
        r = runner({"f": {"rep1": [EV_I, EV_F]}}, "Y")
        rep = r.process_row(row(expected_article_state=""))["repeats"][0]
        self.assertEqual([d["phase"] for d in rep["fallback_details"]], ["FINAL"])  # UNSPECIFIED→INTERIMは除外
        r = runner({"f": {"rep1": [EV_I, EV_F]}}, "X")
        self.assertEqual(r.process_row(row(expected_article_state=""))["repeats"][0]["fallback_calls"], 2)

    def test_aggregate(self):
        a = t.aggregate_fallback
        self.assertEqual(a(["SAME", "REVERSED", "UNCLEAR"]), "REVERSED")
        self.assertEqual(a(["UNCLEAR", "NOT_MENTIONED", "SAME_FAMILY"]), "SAME_FAMILY")
        self.assertEqual(a(["UNCLEAR", "NOT_MENTIONED"]), "NOT_MENTIONED")
        self.assertEqual(a(["NOT_MENTIONED", "NOT_MENTIONED"]), "NOT_MENTIONED")
        self.assertEqual(a(["UNCLEAR"]), "UNCLEAR")
        self.assertEqual(a([]), "NOT_MENTIONED")

    def test_blind_prompts(self):
        r = runner({"f": {"rep1": [EV_I, EV_F]}})
        r.process_row(row())
        body = r.prompts[0].split("[対象一覧]")[1]
        for bad in (LED, "briefly stopped", "restored", "AVAILABLE", "INTERIM", "FINAL", "SINGLE"):
            self.assertNotIn(bad, body)
        self.assertEqual(body.count("- service"), 1)  # 重複除去
        r = runner({"f": {"rep1": [EV_F]}})
        r.process_row(row(expected_article_state=""))
        fb = r.prompts[1]
        for bad in (LED, "restored", "AVAILABLE", "FINAL"):
            self.assertNotIn(bad, fb.split("\n\n", 1)[1])

    def test_ledger_prompt_has_phase(self):
        self.assertIn("INTERIM", t.ledger_prompt("x"))
        self.assertTrue(t.ledger_prompt("FACT").endswith("[fact block]\nFACT"))

    def test_no_events_no_call(self):
        r = runner({"f": {"rep1": []}})
        self.assertEqual(r.process_row(row())["final_compare_rep0"], "LEDGER_NO_DIRECTION")
        self.assertEqual(r.calls, 0)

    def test_heldout_flag(self):
        r = runner({"f": {"rep1": [EV_F]}})
        self.assertTrue(r.process_row(row(heldout=True))["is_heldout"])
        self.assertFalse(r.process_row(row())["is_heldout"])

    def test_shard_partition(self):
        rows = [{"id": f"I{k:02d}"} for k in range(10)]
        for n in (1, 3, 4):
            got = [x["id"] for i in range(1, n + 1) for x in t.shard_items(rows, i, n)]
            self.assertEqual(sorted(got), sorted(x["id"] for x in rows))

    def test_budget_stops(self):
        r = runner({"f": {"rep1": [EV_F]}}, budget_yen=0.0)
        with self.assertRaises(t.BudgetExceeded):
            r.process_row(row())

    def test_merge_hash_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            for i, h in ((1, "a"), (2, "b")):
                with open(os.path.join(d, f"run_meta_shard_{i}of2.json"), "w") as f:
                    json.dump({"shard": i, "n_shards": 2, "input_hash": h, "n_items_expected": 0, "calls": 0}, f)
                open(os.path.join(d, f"results_shard_{i}of2.jsonl"), "w").close()
            with self.assertRaises(SystemExit):
                t.merge(d)

    def _resume_env(self, d):
        rows = [dict(row(id=i, fact_id="f", repeat=2)) for i in ("A", "B", "C")]
        ts = os.path.join(d, "ts.json")
        json.dump(rows, open(ts, "w", encoding="utf-8"), ensure_ascii=False)
        cp = os.path.join(d, "cache.json")
        json.dump({"f": {"rep1": [EV_I, EV_F], "rep2": [EV_I, EV_F]}}, open(cp, "w", encoding="utf-8"))
        out = os.path.join(d, "out")
        base = ["--testset", ts, "--config", "Y", "--dry-run", "--out-dir", out, "--article-shard", "1/1", "--ledger-cache", cp]
        return base, out, cp

    def test_resume_skips_done_and_reruns_partial(self):
        with tempfile.TemporaryDirectory() as d:
            base, out, cp = self._resume_env(d)
            self.assertEqual(t.main(base + ["--only-ids", "A,B"]), 0)
            rp = os.path.join(out, "results_shard_1of1.jsonl")
            lines = [json.loads(x) for x in open(rp, encoding="utf-8")]
            self.assertEqual([r["id"] for r in lines], ["A", "B"])
            lines[1]["repeats"] = lines[1]["repeats"][:1]  # Bを部分完了に
            with open(rp, "w", encoding="utf-8") as f:
                f.writelines(json.dumps(r) + "\n" for r in lines)
            a_line = json.dumps(lines[0])
            self.assertEqual(t.main(base + ["--resume"]), 0)
            res = [json.loads(x) for x in open(rp, encoding="utf-8")]
            self.assertEqual([r["id"] for r in res], [r["id"] for r in res])
            self.assertEqual(sorted(r["id"] for r in res), ["A", "B", "C"])
            self.assertEqual(json.dumps(res[0]), a_line)  # 完了済みAは上書きされない
            self.assertTrue(all(len(r["repeats"]) == 2 for r in res))

    def test_resume_hash_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            base, out, cp = self._resume_env(d)
            t.main(base + ["--only-ids", "A"])
            json.dump({"f": {"rep1": [EV_P], "rep2": [EV_P]}}, open(cp, "w", encoding="utf-8"))
            with self.assertRaises(SystemExit):
                t.main(base + ["--resume"])

    def test_partial_merge_records_missing(self):
        with tempfile.TemporaryDirectory() as d:
            base, out, cp = self._resume_env(d)
            t.main(base + ["--only-ids", "A"])
            with self.assertRaises(SystemExit):
                t.merge(out)
            s = t.merge(out, None, True, ["A", "B", "C"])
            self.assertEqual(s["missing_ids"], ["B", "C"])
            self.assertTrue(json.load(open(os.path.join(out, "merge_meta.json")))["partial"])

    def test_v2_ported(self):
        self.assertEqual(t.compare("AVAILABLE", "STOPPED"), "REVERSED")
        self.assertEqual(t.compare("PAUSED", "STOPPED"), "SAME_FAMILY")
        self.assertEqual(t.compare("AVAILABLE", "STOPPED", "", "q"), "UNCLEAR")
        self.assertEqual(t.norm_state("WEIRD"), "UNCLEAR")


if __name__ == "__main__":
    unittest.main()
