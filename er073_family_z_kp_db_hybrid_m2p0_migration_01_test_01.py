# er073_family_z_kp_db_hybrid_m2p0_migration_01_test_01.py
# Trial runnerのAPI非使用test(mock注入)。Production module無変更・telemetry不変・budget/STOP guardを確認する。
import glob
import json
import os
import tempfile
import unittest

import er073_family_z_kp_db_hybrid_m2p0_migration_01_run as run

SPEC = {"path": "er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer/std.md",
        "source_level": "A2", "process": "A2_SUPPORT"}
ITEMS = [{"rank": i, "display_phrase": p, "key_phrase": p, "source_span": p, "key_phrase_role": "important",
          "japanese_gloss": "x"} for i, p in enumerate(["come back", "hold out", "far bank", "give up", "in time"], 1)]


def fake_select(text, kdir, aid, level, process=None, diagnostic_note=None, **kw):
    assert kw.get("kp_backend") == "db_hybrid" and "shortlist_cache" in kw
    return {"status": "KEY_WORDS_STRUCTURE_PASS", "original_items": ITEMS, "parsed": {"items": ITEMS},
            "kp_backend_used": "db_hybrid"}


def fake_canon(text, items, kdir, aid, process=None, **kw):
    return {"status": "CANONICALIZATION_PASS", "merged": {"items": ITEMS}}


def fake_red(text, items, kdir, aid, process=None, **kw):
    return {"status": "REDUNDANCY_PASS", "duplicate_pairs": []}


class RunnerTests(unittest.TestCase):
    def test_jaccard_and_norm(self):
        self.assertEqual(run.jaccard(["a", "b"], ["a", "b"]), 1.0)
        self.assertAlmostEqual(run.jaccard(["a", "b"], ["b", "c"]), 1 / 3)
        self.assertEqual(run.norm_phrase("  Come  Back "), "come back")

    def test_old_stop_notice_not_applied(self):
        # 旧(2026-10-12 run_e2e_01)通知は委任文により非適用。それ以外の新規STOPが無いこと。
        self.assertEqual(run.check_stop(), [], run.check_stop())

    def test_guard_budget_stop(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/t/x_run1")
            row = {"success": True, "model_id": "gpt-6-luna", "input_tokens": 1_000_000, "cached_input_tokens": 0,
                   "output_tokens": 1_000_000}
            with open(f"{d}/t/x_run1/cost_log.jsonl", "w") as f:
                f.write(json.dumps(row) + "\n")
            self.assertGreater(run.total_spend(d), 1.0)
            events = []
            g = run.make_guard(d, 0.5, 0.2, events)
            with self.assertRaises(run.BudgetExceeded):
                g("t")
            g2 = run.make_guard(d, 1e9, 0.2, events)
            g2("soft")
            self.assertTrue(events and events[0]["soft"])

    def test_mock_run_one_pass_no_prod_writes(self):
        before = run.state_snapshot()
        with tempfile.TemporaryDirectory() as d:
            import er003_v1_n3_01_scaffold_generate as sc
            orig = sc._log_kp_backend_telemetry
            sc._log_kp_backend_telemetry = lambda *a, **k: None
            try:
                r = run.run_one("melos_std", SPEC, "dbh_m2p0", 1, d, 50.0, 35.0, [],
                                select_base=fake_select, canon_fn=fake_canon, red_fn=fake_red)
            finally:
                sc._log_kp_backend_telemetry = orig
            self.assertEqual(r["stage_status"], "PASS")
            self.assertEqual(len(r["final_kp"]), 5)
            self.assertEqual(r["cost_jpy"], 0)
            self.assertEqual(r["title_passed"], "Before the Last Light")
            agg = run.aggregate(d)
            self.assertEqual(agg["table"]["melos_std/dbh_m2p0"]["pass"], 1)
        after = run.state_snapshot()
        self.assertEqual(before["prod_py_sha256"], after["prod_py_sha256"])
        self.assertEqual(before["telemetry_lines"], after["telemetry_lines"])
        self.assertEqual(before["run_e2e_02_digest"], after["run_e2e_02_digest"])

    def test_load_text_title_handling(self):
        art, title = run.load_text(SPEC, True)
        self.assertTrue(art.startswith("# Before the Last Light"))
        art2, _ = run.load_text(SPEC, False)
        self.assertFalse(art2.startswith("#"))
        lemon = {"path": "er055_output/family_z_d_predictive_validation_trial_01/L11/story_en.md"}
        art3, t3 = run.load_text(lemon, True)
        self.assertEqual(t3, "The Lemon on the Books")
        self.assertEqual(art3.count("The Lemon on the Books"), 1)


if __name__ == "__main__":
    unittest.main()
