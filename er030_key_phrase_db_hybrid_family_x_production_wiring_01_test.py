# ============================================================
# er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
# ============================================================
# 実行: .venv/Scripts/python.exe -m unittest
#       er030_key_phrase_db_hybrid_family_x_production_wiring_01_test -v
#
# API呼び出しは一切行わない(全てdeterministicなStage1/shortlist組み立て、
# またはmock/monkeypatchによるdispatch確認のみ)。実LLM呼び出しの
# runtime evidenceは別途`er030_output/family_x_kp_db_hybrid_evidence_01/`
# (Guardrail¥40)で取得する。
# ============================================================

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as v3run
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid
import er003_v1_n3_01_scaffold_generate as sc
import er006_model_routing_contract_01 as routing

# ------------------------------------------------------------
# Trial-04(er029)の12本文fixture(同一パス、既存Trial記録を
# read-onlyで再利用する。存在しない場合はskipする)。
# ------------------------------------------------------------
_EXISTING_6 = dict(run4.EXISTING_6_ARTICLES)
_ADDITIONAL_6 = run4._ADDITIONAL_6_RAW

_FAMILY_X_6 = {
    "meta_a2": "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md",
    "meta_b1b": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md",
    "hormuz_a2": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
    "hormuz_b1b": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
    "small_bag_a2": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md",
    "small_bag_b1b": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md",
}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class CoreEquivalenceWithTrial04Tests(unittest.TestCase):
    """er030_key_phrase_db_hybrid_core_01(Production module)がTrial-04
    baseline(er029、無変更のまま残る)と完全に同一のshortlist/stage1
    結果を返すこと(ロジック無変更で昇格したことの固定回帰、12本文)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def _check_one(self, article_key, article_path, title_override=None):
        if not os.path.exists(article_path):
            self.skipTest(f"fixture not present: {article_path}")
        text = _load(article_path)
        title = title_override or run4.base.extract_article_title(text)
        old = run4.run_stage1_and_shortlist_v4(text, self.dbs, title)
        new = core.run_stage1_and_shortlist(text, self.dbs, title)

        old_sl = [c["canonical_form"] for c in old["shortlist_info"]["shortlist"]]
        new_sl = [c["canonical_form"] for c in new["shortlist_info"]["shortlist"]]
        self.assertEqual(old_sl, new_sl, f"{article_key}: shortlist mismatch")

        for key in ("before_dedup_count", "after_dedup_count", "stage_a_survivors_count",
                    "stage_b_survivors_count", "sentences_total"):
            self.assertEqual(old["stage1"][key], new["stage1"][key], f"{article_key}: {key} mismatch")

        old_phrase = sorted(c["canonical_form"] for c in old["stage1"]["phrase_survivors"])
        new_phrase = sorted(c["canonical_form"] for c in new["stage1"]["phrase_survivors"])
        self.assertEqual(old_phrase, new_phrase, f"{article_key}: phrase_survivors mismatch")

        old_imp = sorted(c["canonical_form"] for c in old["stage1"]["important_noun_candidates"])
        new_imp = sorted(c["canonical_form"] for c in new["stage1"]["important_noun_candidates"])
        self.assertEqual(old_imp, new_imp, f"{article_key}: important_noun_candidates mismatch")

    def test_existing_6_articles_equivalent(self):
        for article_key, (path, _process) in _EXISTING_6.items():
            with self.subTest(article=article_key):
                self._check_one(article_key, path)

    def test_additional_6_articles_equivalent(self):
        for article_key, (path, _process, title_override) in _ADDITIONAL_6.items():
            with self.subTest(article=article_key):
                self._check_one(article_key, path, title_override=title_override)


class BugAToEFixtureNoRegressionTests(unittest.TestCase):
    """既知bug A〜E(discontinuous phrasal verb false positive/possessive
    noise/Fix A quote-aware split/Fix B rare word)が、Production module
    (er030_core)側でも再発しないこと(Trial-04 unit testと同一fixture、
    呼び出し先だけをcoreへ差し替えた固定回帰)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_bug_a_discontinuous_phrasal_verb_still_excluded(self):
        text = "The worker was pushing large bags out of the truck."
        r = core.run_stage1_for_article(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["phrase_survivors"]}
        self.assertNotIn("bags out", canonicals)

    def test_bug_c_possessive_noise_stripped(self):
        text = "The user's plan changed after the meeting."
        r = core.run_stage1_for_article(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["word_survivors"]}
        self.assertNotIn("user's", canonicals)

    def test_fix_a_consecutive_quoted_utterances_split(self):
        text = ('"Today is your audition," Echo said. "You asked me to wake you." '
                '"I did not." "You did not remember asking." Mara sat up. '
                'For ten years, she had given Echo almost everything.')
        units = core.build_sentence_units(text)
        raw_texts = [u["raw_text"] for u in units]
        self.assertIn("You asked me to wake you", raw_texts)
        self.assertIn("I did not", raw_texts)
        self.assertIn("Mara sat up", raw_texts)

    def test_fix_b_rare_single_word_candidates_selected(self):
        text = ("Researchers also study a related ability called self-awakening: "
                "waking near a planned time without an outside signal. "
                "Waking from deep sleep is linked with stronger grogginess "
                "than waking from lighter sleep.")
        units = core.build_sentence_units(text)
        selected = core.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertIn("grogginess", keys)
        self.assertIn("self-awakening", keys)

    def test_fix_b_frequency_unknown_dropped_without_wiktionary_confirmation(self):
        units = [{"tokens": ["a", "minaudi", "bag"], "raw_text": "a minaudi bag"}]
        selected = core.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        built = core.build_rare_single_word_evidences(selected, {"minaudi": False})
        self.assertNotIn("minaudi", [ev["canonical_form"] for ev in built["evidences"]])


class FamilyXNoRegressionOnRealArticlesTests(unittest.TestCase):
    """Family X通常記事(Meta/Hormuz/small_bag、6本文)で、Core(v4/Fix A+B
    適用)がTrial-03(v3、無変更)と比べて重要語(ユーザー例示語)を
    失っていないこと、既にKEY-PHRASE-DB-HYBRID-TRIAL-04_REPORT.md §3で
    実LLM実行により検証済みのshortlist件数と一致することを固定回帰化する
    (API呼び出しなし、機械screening段階のみの比較)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    # Trial-04 REPORT §3実測値(shortlist_total_count、Trial-03→Trial-04)。
    _EXPECTED_SHORTLIST_OLD_NEW = {
        "meta_a2": (21, 22), "meta_b1b": (22, 24),
        "hormuz_a2": (20, 20), "hormuz_b1b": (20, 20),
        "small_bag_a2": (20, 20), "small_bag_b1b": (20, 20),
    }

    def test_shortlist_counts_match_trial04_report_and_user_example_terms_retained(self):
        for article_key, path in _FAMILY_X_6.items():
            with self.subTest(article=article_key):
                if not os.path.exists(path):
                    self.skipTest(f"fixture not present: {path}")
                text = _load(path)
                title = v3run.extract_article_title(text)
                old = v3run.run_stage1_and_shortlist_v3(text, self.dbs)
                new = core.run_stage1_and_shortlist(text, self.dbs, title)

                old_count = old["shortlist_info"]["shortlist_total_count"]
                new_count = new["shortlist_info"]["shortlist_total_count"]
                expected_old, expected_new = self._EXPECTED_SHORTLIST_OLD_NEW[article_key]
                self.assertEqual(old_count, expected_old, f"{article_key}: Trial-03 shortlist count drifted")
                self.assertEqual(new_count, expected_new, f"{article_key}: Trial-04/Core shortlist count drifted")

                survivors = ({c["canonical_form"] for c in new["stage1"]["phrase_survivors"]} |
                             {c["canonical_form"] for c in new["stage1"]["important_noun_candidates"]})
                for term in v3run.USER_EXAMPLE_TERMS.get(article_key, []):
                    term_key = term.lower()
                    self.assertTrue(
                        any(term_key in c or c in term_key for c in survivors),
                        f"{article_key}: user example term '{term}' missing from machine-screened survivors")


class SentenceSplitDifferenceIsDocumentedTests(unittest.TestCase):
    """Fix A(quote-aware split)が、Family Xの平叙文記事でも会話文と無関係な
    箇所(記事中の引用符付きattribution等)で追加の分割を起こしうることを
    観測用に記録する(hormuz/small_bagで実測+1〜+2文、Trial-04 REPORTの
    「通常の平叙文は実質同一」という記述の限定的な例外条件として明示する。
    悪化ではないことは上のFamilyXNoRegressionOnRealArticlesTestsで確認済み)。"""

    def test_sentence_unit_count_delta_is_small_and_documented(self):
        for article_key, path in _FAMILY_X_6.items():
            with self.subTest(article=article_key):
                if not os.path.exists(path):
                    self.skipTest(f"fixture not present: {path}")
                text = _load(path)
                old_count = len(s1v3.build_sentence_units(text))
                new_count = len(core.build_sentence_units(text))
                # Fix Aは分割を増やす方向にのみ働く(閉じ引用符境界を追加で
                # 認識するだけで、既存の分割点を減らす変更は含まない)。
                self.assertGreaterEqual(new_count, old_count, f"{article_key}: split count decreased")
                self.assertLessEqual(new_count - old_count, 3, f"{article_key}: unexpectedly large split delta")


class DbHybridFallbackTriggerTests(unittest.TestCase):
    """DB Hybrid failure条件のうち、API呼び出し前に判定可能な
    SHORTLIST_TOO_SMALLが実際に送出されること(cost-free)。"""

    def test_shortlist_too_small_raises_before_any_api_call(self):
        tiny_out_dir = os.path.join("er030_output", "kp_backend_telemetry_01", "_test_tiny_shortlist")
        with mock.patch.object(db_hybrid, "_make_instrumented_selector_factory") as mocked_factory:
            with self.assertRaises(db_hybrid.DbHybridFailure) as ctx:
                db_hybrid.run_db_hybrid_selection(
                    "Cats sit. Dogs run.", tiny_out_dir, "TEST_TINY", "A2_SUPPORT", process=None)
            mocked_factory.assert_not_called()
        self.assertEqual(ctx.exception.reason_code, "SHORTLIST_TOO_SMALL")


class ScaffoldGenerateDispatchTests(unittest.TestCase):
    """kp_backend既定値("strategy_l")は全既存呼び出し元で無変更であり、
    db_hybrid経路(er030_key_phrase_db_hybrid_selector_01)には一切
    到達しないこと(legacy既定不変の固定回帰)。db_hybrid指定時は
    Primary/Fallbackの両方が正しくdispatchされ、telemetryが記録される
    ことを確認する(API呼び出しはmockで代替)。"""

    def test_default_kp_backend_never_touches_db_hybrid_module(self):
        with mock.patch.object(
                sc, "_run_key_phrase_selection_db_hybrid_with_fallback",
                side_effect=AssertionError("db_hybrid経路に到達してはならない")):
            with mock.patch.object(routing, "SUPPORT_MODEL", None):
                with self.assertRaises(routing.ModelContractViolation):
                    sc.run_key_phrase_selection(
                        "dummy article", "er030_output/_test_default_backend", "TEST_ID", "TEST_LEVEL",
                        process="B1_SUPPORT")

    def test_db_hybrid_backend_success_path_sets_kp_backend_used_and_logs_telemetry(self):
        fake_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                        "model_id": "fake-model", "cost_jpy": 1.2345, "shortlist_total_count": 20}
        telemetry_path = sc.KP_BACKEND_TELEMETRY_PATH
        existed_before = os.path.exists(telemetry_path)
        size_before = os.path.getsize(telemetry_path) if existed_before else 0
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         return_value=dict(fake_result)):
            result = sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_db_hybrid_success", "TEST_ID_2", "TEST_LEVEL",
                process=None, kp_backend="db_hybrid")
        self.assertEqual(result["kp_backend_used"], "db_hybrid")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS")
        with open(telemetry_path, encoding="utf-8") as f:
            f.seek(size_before)
            new_lines = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(e["article_id"] == "TEST_ID_2" and not e["fallback_triggered"] for e in new_lines))

    def test_db_hybrid_backend_failure_triggers_fallback_and_logs_telemetry(self):
        telemetry_path = sc.KP_BACKEND_TELEMETRY_PATH
        existed_before = os.path.exists(telemetry_path)
        size_before = os.path.getsize(telemetry_path) if existed_before else 0
        fallback_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": []}
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         side_effect=db_hybrid.DbHybridFailure(
                             "SHORTLIST_TOO_SMALL", "forced for test",
                             telemetry={"shortlist_total_count": 3})):
            with mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                                    return_value=dict(fallback_result)) as mocked_fallback:
                result = sc.run_key_phrase_selection(
                    "dummy article", "er030_output/_test_db_hybrid_fallback", "TEST_ID_3", "TEST_LEVEL",
                    process=None, kp_backend="db_hybrid")
        mocked_fallback.assert_called_once()
        self.assertEqual(result["kp_backend_used"], "strategy_l_fallback")
        self.assertEqual(result["kp_backend_fallback_reason_code"], "SHORTLIST_TOO_SMALL")
        with open(telemetry_path, encoding="utf-8") as f:
            f.seek(size_before)
            new_lines = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(e["article_id"] == "TEST_ID_3" and e["fallback_triggered"]
                             and e["fallback_reason_code"] == "SHORTLIST_TOO_SMALL" for e in new_lines))

    def test_run_key_phrases_default_kp_backend_is_strategy_l(self):
        self.assertEqual(sc.run_key_phrases.__defaults__[-1], "strategy_l")

    def test_family_x_runner_default_kp_backend_is_db_hybrid(self):
        import er019_family_x_audio_production_runner_01 as runner
        self.assertEqual(runner.run_theme_scaffold.__defaults__[-1], "db_hybrid")


if __name__ == "__main__":
    unittest.main()
