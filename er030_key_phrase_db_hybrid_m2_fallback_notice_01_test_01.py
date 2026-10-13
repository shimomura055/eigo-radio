# ============================================================
# er030_key_phrase_db_hybrid_m2_fallback_notice_01_test_01.py
# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03: M2構築失敗時のStrategy L Fallbackの必須ユーザー報告
# (summary/notice file/標準出力の3点)をmockで固定する。API呼出は一切ない(全てmock、synthetic)。
# 実行: .venv\Scripts\python.exe er030_key_phrase_db_hybrid_m2_fallback_notice_01_test_01.py
# ============================================================
from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er019_family_x_audio_production_runner_01 as runner
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid

ARTICLE = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here.\n\nFourth one."


def _fallback_run_key_phrases(reason_code, article_id="FAMILY_X_AUDIO_unit_test_a2", level="a2"):
    out = tempfile.mkdtemp()
    with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                    side_effect=db_hybrid.DbHybridFailure(reason_code, "forced for test", telemetry={})), \
         mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                           return_value={"status": "KEY_WORDS_STRUCTURE_FAIL"}), \
         mock.patch.object(sc, "_log_kp_backend_telemetry"):
        return sc.run_key_phrases("dummy", out, article_id, level, kp_backend="db_hybrid")


class RecordContractTests(unittest.TestCase):
    def test_m2_supply_exception_records_all_keys(self):
        r = _fallback_run_key_phrases("M2_SUPPLY_EXCEPTION")
        evs = r["m2_fallback_events"]
        self.assertEqual(len(evs), 1)
        ev = evs[0]
        for k in sc.M2_FALLBACK_EVENT_KEYS:
            self.assertIn(k, ev)
        self.assertEqual(ev["family"], "X")
        self.assertEqual(ev["level"], "a2")
        self.assertEqual(ev["reason_code"], "M2_SUPPLY_EXCEPTION")
        self.assertTrue(ev["m2_related"])
        self.assertIn("strategy_l_fallback", ev["fallback_result"])
        self.assertIn("正常動作ではない", ev["kp_supply_actual"])

    def test_selector_exception_is_m2_related_and_other_reason_is_still_reported(self):
        self.assertTrue(_fallback_run_key_phrases("SELECTOR_EXCEPTION")["m2_fallback_events"][0]["m2_related"])
        ev = _fallback_run_key_phrases("SHORTLIST_TOO_SMALL")["m2_fallback_events"][0]
        self.assertFalse(ev["m2_related"])  # 区別するが、報告はする

    def test_no_fallback_gives_empty_events(self):
        out = tempfile.mkdtemp()
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                        return_value={"status": "KEY_WORDS_STRUCTURE_FAIL", "kp_supply": "m2"}), \
             mock.patch.object(sc, "_log_kp_backend_telemetry"):
            r = sc.run_key_phrases("dummy", out, "FAMILY_X_AUDIO_unit_test_a2", "a2", kp_backend="db_hybrid")
        self.assertEqual(r["m2_fallback_events"], [])

    def test_family_z_contract_default_strategy_l_has_empty_events_and_z_family_label(self):
        # Z KPは現状strategy_l固定=M2経路なし。summaryキー契約(m2_fallback_events=[])だけ満たすこと
        out = tempfile.mkdtemp()
        with mock.patch.object(sc, "_run_key_phrase_selection_strategy_l", return_value={"status": "KEY_WORDS_STRUCTURE_FAIL"}), \
             mock.patch.object(sc, "run_key_phrase_selection",
                               return_value={"status": "KEY_WORDS_STRUCTURE_FAIL", "cost_jpy": 0.0}):
            r = sc.run_key_phrases("dummy", out, "family_z_melos", "A2", process=None)
        self.assertEqual(r["m2_fallback_events"], [])
        rec = sc.build_m2_fallback_record("family_z_melos", "A2", "M2_SUPPLY_EXCEPTION", "x", "OK")
        self.assertEqual(rec["family"], "Z")
        self.assertEqual(set(rec), set(sc.M2_FALLBACK_EVENT_KEYS))


class ThreePointReportTests(unittest.TestCase):
    """Fallback発生時にsummary・notice・stdoutの3点が出ることを固定する(Family X runner)。"""

    def _run_scaffold(self, events):
        src = tempfile.mkdtemp()
        out = tempfile.mkdtemp()
        os.makedirs(f"{src}/a2")
        with open(f"{src}/a2/article.md", "w", encoding="utf-8") as f:
            f.write(ARTICLE)
        os.makedirs(f"{out}/a2")
        with open(f"{out}/a2/a2_support_texts.json", "w", encoding="utf-8") as f:
            f.write("{}")
        kp = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS", "kp_backend_used": "strategy_l_fallback" if events else "db_hybrid"},
              "canonicalization": {"status": "CANONICALIZATION_PASS"}, "m2_fallback_events": events}
        buf = io.StringIO()
        with mock.patch.object(sc, "run_key_phrases", return_value=kp), \
             mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}), \
             contextlib.redirect_stdout(buf):
            result = runner.run_theme_scaffold(None, src, out, ["a2"], scaffold_only="kp", kp_backend="db_hybrid")
            final_line = runner.print_m2_fallback_final_line(out)
        return out, result, buf.getvalue(), final_line

    def test_fallback_gives_summary_notice_and_stdout(self):
        ev = sc.build_m2_fallback_record("FAMILY_X_AUDIO_unit_test_a2", "a2", "M2_SUPPLY_EXCEPTION", "forced", "KEY_WORDS_STRUCTURE_PASS")
        out, result, stdout, final_line = self._run_scaffold([ev])
        # (1) summary
        with open(f"{out}/scaffold_run_summary.json", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["a2"]["m2_fallback"]["reason_code"], "M2_SUPPLY_EXCEPTION")
        self.assertEqual(len(summary["a2"]["m2_fallback_events"]), 1)
        for k in ("family", "article", "level", "stage", "reason_code", "reason", "fallback_result"):
            self.assertIn(k, summary["a2"]["m2_fallback"])
        # (2) notice file
        notice = os.path.join(out, "M2_FALLBACK_NOTICE.md")
        self.assertTrue(os.path.exists(notice))
        text = open(notice, encoding="utf-8").read()
        self.assertIn("M2P0正常動作ではありません", text)
        self.assertIn("reason_code: M2_SUPPLY_EXCEPTION", text)
        self.assertIn("level: a2", text)
        # (3) stdout(scaffold中+終了時)
        self.assertIn("[M2-FALLBACK][NOTICE]", stdout)
        self.assertIn("M2_SUPPLY_EXCEPTION", final_line)
        self.assertIn("M2_FALLBACK_NOTICE.md", final_line)

    def test_no_fallback_no_notice_and_explicit_none_line(self):
        out, result, stdout, final_line = self._run_scaffold([])
        self.assertFalse(os.path.exists(os.path.join(out, "M2_FALLBACK_NOTICE.md")))
        self.assertIsNone(result["a2"]["m2_fallback"])
        self.assertEqual(result["a2"]["m2_fallback_events"], [])
        self.assertIn("[M2-FALLBACK] 発生なし", final_line)
        self.assertNotIn("[M2-FALLBACK][NOTICE]", stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
