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
#
# 修正1回目(Opus L2所見反映、2026-09-27): 等価性test(S2)のWiktionary
# lookupを固定辞書fakeに差し替え、実APIを叩かないよう決定化した(下記
# `_FAKE_MULTIWORD_LOOKUP`/`_FAKE_UNIGRAM_LOOKUP`参照。old/new両方に
# 同一fakeを適用するため、等価性の判定[old==new]自体には影響しない)。
# FamilyXNoRegressionOnRealArticlesTests等、Trial-04 REPORT実測値との
# 一致を検証するtestは実APIのままとする(fake化するとその実測値との
# 一致という検証目的自体が失われるため)。
# ============================================================

from __future__ import annotations

import hashlib
import json
import os
import unittest
from unittest import mock

import er003_b1_p2_keywords as bk
import er003_key_phrase_source_gate_01 as source_gate
import er003_v1_n3_01_scaffold_generate as sc
import er006_model_routing_contract_01 as routing
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as v3run
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er029_key_phrase_db_hybrid_trial_04_stage1 as s1v4
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid

# ------------------------------------------------------------
# Trial-04(er029)の12本文fixture(同一パス、既存Trial記録を
# read-onlyで再利用する)。
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


def _require_fixture(test_case: unittest.TestCase, path: str) -> None:
    """修正1回目(Opus L2所見N6): fixture不在をskipではなくFAILへ変更する
    (無自覚なカバレッジ喪失防止。既存artifactが誤って削除・移動された
    場合に、testがGreenのまま検知漏れになることを防ぐ)。"""
    if not os.path.exists(path):
        test_case.fail(f"fixture not present: {path}(N6: skipではなくFAILとして扱う)")


# ------------------------------------------------------------
# 修正1回目(Opus L2所見S2): Wiktionary lookup 2関数の固定辞書fake。
# ------------------------------------------------------------
def _fake_multiword_lookup(candidates, batch_size=50, sleep_sec=1.5):
    unique = sorted(set(candidates))
    return {"results": {c: True for c in unique}, "api_calls": 0, "elapsed_sec": 0.0,
            "candidate_count": len(unique)}


def _fake_unigram_lookup(candidates, batch_size=50, sleep_sec=1.5):
    unique = sorted(set(candidates))
    return {"results": {c: True for c in unique}, "api_calls": 0, "elapsed_sec": 0.0,
            "candidate_count": len(unique)}


class CoreEquivalenceWithTrial04Tests(unittest.TestCase):
    """er030_key_phrase_db_hybrid_core_01(Production module)がTrial-04
    baseline(er029、無変更のまま残る)と完全に同一のshortlist/stage1
    結果を返すこと(ロジック無変更で昇格したことの固定回帰、12本文)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def _check_one(self, article_key, article_path, title_override=None):
        _require_fixture(self, article_path)
        text = _load(article_path)
        title = title_override or run4.base.extract_article_title(text)
        with mock.patch.object(ing, "wiktionary_multiword_targeted_lookup", side_effect=_fake_multiword_lookup), \
             mock.patch.object(s1v4, "wiktionary_unigram_lemma_lookup", side_effect=_fake_unigram_lookup), \
             mock.patch.object(core, "wiktionary_unigram_lemma_lookup", side_effect=_fake_unigram_lookup):
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
    (実Wiktionary APIを使用、実測値そのものとの一致を検証する目的のため
    S2のfake化対象外)。"""

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
                _require_fixture(self, path)
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
                _require_fixture(self, path)
                text = _load(path)
                old_count = len(s1v3.build_sentence_units(text))
                new_count = len(core.build_sentence_units(text))
                # Fix Aは分割を増やす方向にのみ働く(閉じ引用符境界を追加で
                # 認識するだけで、既存の分割点を減らす変更は含まない)。
                self.assertGreaterEqual(new_count, old_count, f"{article_key}: split count decreased")
                self.assertLessEqual(new_count - old_count, 3, f"{article_key}: unexpectedly large split delta")


class Er028UtilByteParityTests(unittest.TestCase):
    """修正1回目(Opus L2所見S6(a)): er030_key_phrase_db_hybrid_selector_01
    へ移設したSELECTION_GUIDANCE/util 4関数が、Trial run script
    (`er028_key_phrase_db_hybrid_trial_03_run.py`、無変更のまま残る)と
    byte-for-byte同一であることをsha256照合で固定回帰化する(将来の
    意図しない乖離を検知する)。Production module(`er030_*`)からTrial
    run scriptへのimportは本ファイル冒頭のimport一覧のとおりゼロである
    (er030_key_phrase_db_hybrid_selector_01.pyがimportするのは
    er030_key_phrase_db_hybrid_core_01のみ、`er028_*_run`はimportしない)。"""

    @staticmethod
    def _sha(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def test_no_trial_run_script_import_in_selector_module(self):
        with open("er030_key_phrase_db_hybrid_selector_01.py", encoding="utf-8") as f:
            lines = f.readlines()
        import_lines = [ln for ln in lines if ln.strip().startswith(("import ", "from "))]
        for ln in import_lines:
            self.assertNotIn("trial_03_run", ln, f"Trial run scriptへのimportが残っています: {ln.strip()}")
            self.assertNotIn("trial_04_run", ln, f"Trial run scriptへのimportが残っています: {ln.strip()}")

    def test_selection_guidance_byte_identical_to_trial(self):
        self.assertEqual(self._sha(db_hybrid.SELECTION_GUIDANCE), self._sha(v3run.SELECTION_GUIDANCE))

    def test_compact_evidence_string_byte_identical_to_trial(self):
        samples = [
            {"important_noun_phrase_candidate": True, "matched_dbs": ["repeated_compound_noun_heuristic"]},
            {"important_noun_phrase_candidate": True, "matched_dbs": ["wiktionary"],
             "db_categories": ["multiword_term"]},
            {"matched_dbs": ["cefr_j"], "db_categories": ["A2"], "irregular_verb_rescue": True},
            {"matched_dbs": [], "db_categories": [], "possessive_noise_stripped": True},
        ]
        for sample in samples:
            self.assertEqual(db_hybrid._compact_evidence_string(sample), v3run._compact_evidence_string(sample))

    def test_extract_article_title_byte_identical_to_trial(self):
        text = "intro line\n# The Real Title\nbody text"
        self.assertEqual(db_hybrid.extract_article_title(text), v3run.extract_article_title(text))

    def test_extract_static_instructions_byte_identical_to_trial(self):
        template = bk.load_prompt_template()
        self.assertEqual(self._sha(db_hybrid.extract_static_instructions(template)),
                          self._sha(v3run.extract_static_instructions(template)))

    def test_assert_no_full_article_body_same_behavior_as_trial(self):
        article_text = " ".join(["lorem"] * 150)
        safe_message = "totally different short message"
        db_hybrid.assert_no_full_article_body(safe_message, article_text)
        v3run.assert_no_full_article_body(safe_message, article_text)
        unsafe_message = article_text
        with self.assertRaises(AssertionError):
            db_hybrid.assert_no_full_article_body(unsafe_message, article_text)
        with self.assertRaises(AssertionError):
            v3run.assert_no_full_article_body(unsafe_message, article_text)


class LightweightPromptByteIdenticalToTrial04Tests(unittest.TestCase):
    """修正1回目(Opus L2所見S1): er030_key_phrase_db_hybrid_selector_01.
    build_lightweight_user_messageとer029_key_phrase_db_hybrid_trial_04_
    run.build_lightweight_user_message_v4が、同一の入力(12本文fixture)に
    対し出力文字列が完全一致することを実測範囲で確認する(旧REPORT
    「byte-identical shortlist」という表現は、shortlist内容[candidate列]
    の一致を指しており、prompt文字列そのものの一致は本testで新たに
    実測確認する。両者の表現の違いをここに明記する)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_prompt_string_identical_across_12_fixtures(self):
        static_instructions = v3run.extract_static_instructions(bk.load_prompt_template())
        all_fixtures = list(_EXISTING_6.items()) + \
            [(k, (p, proc)) for k, (p, proc, _t) in _ADDITIONAL_6.items()]
        title_overrides = {k: t for k, (_p, _proc, t) in _ADDITIONAL_6.items()}
        checked = 0
        for article_key, (path, _process) in all_fixtures:
            with self.subTest(article=article_key):
                if not os.path.exists(path):
                    self.fail(f"fixture not present: {path}(N6: skipではなくFAILとして扱う)")
                text = _load(path)
                title = title_overrides.get(article_key) or v3run.extract_article_title(text)
                with mock.patch.object(ing, "wiktionary_multiword_targeted_lookup",
                                        side_effect=_fake_multiword_lookup), \
                     mock.patch.object(s1v4, "wiktionary_unigram_lemma_lookup",
                                        side_effect=_fake_unigram_lookup), \
                     mock.patch.object(core, "wiktionary_unigram_lemma_lookup",
                                        side_effect=_fake_unigram_lookup):
                    old = run4.run_stage1_and_shortlist_v4(text, self.dbs, title)
                    new = core.run_stage1_and_shortlist(text, self.dbs, title)
                old_prompt = run4.build_lightweight_user_message_v4(
                    title, old["shortlist_info"], old["shortlist_info"]["sentence_reference"],
                    static_instructions)
                new_prompt = db_hybrid.build_lightweight_user_message(
                    title, new["shortlist_info"], new["shortlist_info"]["sentence_reference"],
                    static_instructions)
                self.assertEqual(old_prompt, new_prompt, f"{article_key}: prompt string mismatch")
                checked += 1
        self.assertEqual(checked, 12, "12本文全件を照合できていません")


class SourceSpanConsistencyTests(unittest.TestCase):
    """修正1回目(Opus L2所見S3): 選定item のsource_span/source_sentenceが
    生article_text(canonicalization前)に実在しない場合、
    DbHybridFailure("SOURCE_SPAN_NOT_IN_RAW_ARTICLE")が送出されること
    (fallback可)。er003_key_phrase_source_gate_01.normalize_textと同一の
    正規化基準を使う。"""

    def test_matching_source_span_passes(self):
        article_text = "The worker signed a new contract worker agreement yesterday."
        items = [{"rank": 1, "source_span": "contract worker", "source_sentence": None}]
        missing = db_hybrid._verify_source_spans_against_raw_article(items, article_text)
        self.assertEqual(missing, [])

    def test_mismatched_source_span_detected(self):
        article_text = "The worker signed a new agreement yesterday."
        items = [{"rank": 1, "source_span": "totally unrelated phrase", "source_sentence": None}]
        missing = db_hybrid._verify_source_spans_against_raw_article(items, article_text)
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["reason"], "SOURCE_SPAN_NOT_FOUND_IN_RAW_ARTICLE")

    def test_normalization_matches_source_gate_module(self):
        # apostrophe種の表記ゆれがnormalize_text経由で吸収されること
        # (er003_key_phrase_source_gate_01と同一基準)。
        article_text = "The worker’s plan changed after the meeting."
        items = [{"rank": 1, "source_span": "worker's plan", "source_sentence": None}]
        missing = db_hybrid._verify_source_spans_against_raw_article(items, article_text)
        self.assertEqual(missing, [])
        self.assertEqual(
            source_gate.normalize_text("worker's plan"),
            source_gate.normalize_text("worker’s plan"))


def _build_minimal_shortlist_info(n=12, phrase=3, important=3):
    shortlist = []
    for i in range(phrase):
        shortlist.append({"surface_form": f"phrase{i}", "canonical_form": f"phrase{i}",
                           "unit_type": "bigram", "important_noun_phrase_candidate": False,
                           "occurrence_count_in_article": 1, "context_sentence_id": "S1",
                           "matched_dbs": [], "db_categories": []})
    for i in range(important):
        shortlist.append({"surface_form": f"important{i}", "canonical_form": f"important{i}",
                           "unit_type": "word", "important_noun_phrase_candidate": True,
                           "occurrence_count_in_article": 1, "context_sentence_id": "S1",
                           "matched_dbs": [], "db_categories": []})
    remaining = n - phrase - important
    for i in range(max(remaining, 0)):
        shortlist.append({"surface_form": f"word{i}", "canonical_form": f"word{i}",
                           "unit_type": "word", "important_noun_phrase_candidate": False,
                           "occurrence_count_in_article": 1, "context_sentence_id": "S1",
                           "matched_dbs": [], "db_categories": []})
    return {"shortlist": shortlist, "shortlist_total_count": len(shortlist),
            "phrase_included_count": phrase, "important_noun_included_count": important,
            "word_included_count": max(remaining, 0), "sentence_reference": {"S1": "A test sentence."}}


class CostGuardAndArticleCostCapTests(unittest.TestCase):
    """修正1回目(Opus L2所見S4、Fable決定): 1呼び出しあたりのcost guardは
    PASS済み結果を破棄しない(cost_guard_exceeded=trueのみ記録)。記事単位
    の累積コスト上限超過はfallbackせずSTOP(KP_ARTICLE_COST_CAP_EXCEEDED)。"""

    def _fake_s1r(self):
        return {"stage1": {}, "shortlist_info": _build_minimal_shortlist_info()}

    def test_cost_guard_exceeded_does_not_discard_pass_result(self):
        with mock.patch.object(core, "run_stage1_and_shortlist", return_value=self._fake_s1r()), \
             mock.patch.object(db_hybrid, "_make_instrumented_selector_factory") as mocked_factory, \
             mock.patch.object(db_hybrid.prod, "run_production_selection_gate",
                                return_value=({"items": []}, "KEY_WORDS_STRUCTURE_PASS", [], "fake-model",
                                              "resp_1")), \
             mock.patch.object(db_hybrid.pricing, "cost_jpy_for_call", return_value=999.0):
            out_dir = os.path.join("er030_output", "kp_backend_telemetry_01", "_test_cost_guard")
            result = db_hybrid.run_db_hybrid_selection(
                "A test sentence with enough words to pass basic checks.",
                out_dir, "TEST_COST_GUARD", "A2_SUPPORT", process=None, dbs={})
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertTrue(result["cost_guard_exceeded"])
        mocked_factory.assert_called_once()

    def test_article_cost_cap_exceeded_stops_without_fallback(self):
        fake_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                        "model_id": "fake-model", "cost_jpy": 999.0, "shortlist_total_count": 20,
                        "kp_backend": "db_hybrid", "cost_guard_exceeded": True}
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         return_value=dict(fake_result)), \
             mock.patch.object(sc, "_run_key_phrase_selection_strategy_l") as mocked_strategy_l:
            result = sc.run_key_phrases(
                "dummy article text", "er030_output/_test_article_cost_cap", "TEST_COST_CAP", "TEST_LEVEL",
                process=None, kp_backend="db_hybrid")
        mocked_strategy_l.assert_not_called()
        self.assertEqual(result["status"], "KP_ARTICLE_COST_CAP_EXCEEDED")
        self.assertGreater(result["cumulative_cost_jpy"], db_hybrid.KP_ARTICLE_COST_CAP_JPY)


class ModelContractViolationStopsWithoutFallbackTests(unittest.TestCase):
    """修正1回目(Opus L2所見B3): 応答モデルが承認済みモデルと不一致の
    場合、DbHybridFailure(fallback_allowed=False)がfallbackせず伝播し、
    処理をSTOPすること(fail-closed)。"""

    def test_run_db_hybrid_selection_raises_fallback_disallowed_on_model_mismatch(self):
        fake_shortlist_info = _build_minimal_shortlist_info()

        def _fake_factory_maker(user_message, model, usage_sink, contract_violation_sink=None, client=None):
            def factory():
                def fn():
                    if contract_violation_sink is not None:
                        contract_violation_sink.append({"expected_model": model, "actual_model": "wrong-model"})
                    raise db_hybrid.prod.SelectorModelMismatchError("mismatch")
                fn.model = model
                fn.reasoning_effort = db_hybrid.prod.SELECTOR_REASONING_EFFORT
                fn.uses_web_search_tool = False
                fn.uses_structured_output = True
                return fn
            return factory

        with mock.patch.object(core, "run_stage1_and_shortlist",
                                return_value={"stage1": {}, "shortlist_info": fake_shortlist_info}), \
             mock.patch.object(db_hybrid, "_make_instrumented_selector_factory", side_effect=_fake_factory_maker):
            out_dir = os.path.join("er030_output", "kp_backend_telemetry_01", "_test_model_mismatch")
            with self.assertRaises(db_hybrid.DbHybridFailure) as ctx:
                db_hybrid.run_db_hybrid_selection(
                    "A test sentence with enough words to pass basic checks.",
                    out_dir, "TEST_MISMATCH", "A2_SUPPORT", process=None, dbs={})
        self.assertEqual(ctx.exception.reason_code, "MODEL_CONTRACT_VIOLATION")
        self.assertFalse(ctx.exception.fallback_allowed)

    def test_scaffold_generate_propagates_without_fallback_on_disallowed_failure(self):
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         side_effect=db_hybrid.DbHybridFailure(
                             "MODEL_CONTRACT_VIOLATION", "forced for test",
                             telemetry={"expected_model": "a", "actual_model": "b"}, fallback_allowed=False)), \
             mock.patch.object(sc, "_run_key_phrase_selection_strategy_l") as mocked_fallback:
            with self.assertRaises(db_hybrid.DbHybridFailure):
                sc.run_key_phrase_selection(
                    "dummy article", "er030_output/_test_model_mismatch_stop", "TEST_ID_MISMATCH", "TEST_LEVEL",
                    process=None, kp_backend="db_hybrid")
        mocked_fallback.assert_not_called()


class PerArticleTraceabilityMetadataTests(unittest.TestCase):
    """修正1回目(Opus L2所見B2): db_hybrid成功時・fallback時いずれも
    {kp_dir}/keywords_runtime_metadata.jsonへkp_backend関連フィールドが
    追記(既存内容を保持したままupdate)されること。"""

    def test_success_path_writes_top_level_metadata_file(self):
        fake_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                        "model_id": "fake-model", "cost_jpy": 1.0, "shortlist_total_count": 20,
                        "kp_backend": "db_hybrid", "cost_guard_exceeded": False, "attempts_detail": []}
        out_dir = os.path.join("er030_output", "kp_backend_telemetry_01", "_test_b2_success")
        metadata_path = os.path.join(out_dir, "keywords_runtime_metadata.json")
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         return_value=dict(fake_result)):
            sc.run_key_phrase_selection(
                "dummy article", out_dir, "TEST_B2_SUCCESS", "TEST_LEVEL", process=None, kp_backend="db_hybrid")
        with open(metadata_path, encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["kp_backend_used"], "db_hybrid")
        self.assertEqual(saved["kp_backend_model_id"], "fake-model")
        self.assertIsNone(saved["kp_backend_fallback_reason_code"])

    def test_fallback_path_preserves_attempted_db_hybrid_fact(self):
        fallback_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                            "model_id": "fake-fallback-model"}
        out_dir = os.path.join("er030_output", "kp_backend_telemetry_01", "_test_b2_fallback")
        metadata_path = os.path.join(out_dir, "keywords_runtime_metadata.json")
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         side_effect=db_hybrid.DbHybridFailure(
                             "SHORTLIST_TOO_SMALL", "forced for test",
                             telemetry={"shortlist_total_count": 3})), \
             mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                               return_value=dict(fallback_result)):
            sc.run_key_phrase_selection(
                "dummy article", out_dir, "TEST_B2_FALLBACK", "TEST_LEVEL", process=None, kp_backend="db_hybrid")
        with open(metadata_path, encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["kp_backend_used"], "strategy_l_fallback")
        self.assertEqual(saved["kp_backend_fallback_reason_code"], "SHORTLIST_TOO_SMALL")
        self.assertEqual(saved["kp_backend"], "db_hybrid_attempted")


class DbHybridFallbackTriggerTests(unittest.TestCase):
    """DB Hybrid failure条件のうち、API呼び出し前に判定可能な
    SHORTLIST_TOO_SMALLが実際に送出されること(cost-free、修正1回目の
    S5改訂[total>=12かつphrase+important>=5]後も同様に成立する)。"""

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
    ことを確認する(API呼び出しはmockで代替)。

    修正1回目(Opus L2所見B1): telemetry検証は実ファイル
    (`sc.KP_BACKEND_TELEMETRY_PATH`)を直接汚染せず、
    `mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tmp)`でtmpパスへ
    切り替える。"""

    def setUp(self):
        import tempfile
        self._tmp_dir = tempfile.mkdtemp(prefix="kp_backend_telemetry_test_")
        self._tmp_telemetry_path = os.path.join(self._tmp_dir, "telemetry.jsonl")
        self._patcher = mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", self._tmp_telemetry_path)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _read_new_lines(self):
        if not os.path.exists(self._tmp_telemetry_path):
            return []
        with open(self._tmp_telemetry_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def test_default_kp_backend_never_touches_db_hybrid_module(self):
        with mock.patch.object(
                sc, "_run_key_phrase_selection_db_hybrid_with_fallback",
                side_effect=AssertionError("db_hybrid経路に到達してはならない")):
            with mock.patch.object(routing, "SUPPORT_MODEL", None):
                with self.assertRaises(routing.ModelContractViolation):
                    sc.run_key_phrase_selection(
                        "dummy article", "er030_output/_test_default_backend", "TEST_ID", "TEST_LEVEL",
                        process="B1_SUPPORT")

    def test_legacy_default_backend_logs_telemetry(self):
        # 修正1回目(Opus L2所見B1): 既定"strategy_l"経路でもtelemetryが
        # 1行記録されること(旧: db_hybrid経路のみ記録)。
        fake_strategy_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []},
                                 "original_items": [], "model_id": "fake-legacy-model"}
        with mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                                return_value=dict(fake_strategy_result)):
            result = sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_legacy_telemetry", "TEST_ID_LEGACY", "TEST_LEVEL",
                process=None, kp_backend="strategy_l")
        self.assertEqual(result["kp_backend_used"], "strategy_l")
        entries = self._read_new_lines()
        self.assertTrue(any(
            e["article_id"] == "TEST_ID_LEGACY" and e["requested_backend"] == "strategy_l" and
            e["backend_used"] == "strategy_l" and not e["fallback_triggered"] and
            e["synthetic"] is False and e["spec_id"] == sc.KP_BACKEND_SPEC_ID and
            e["level"] == "TEST_LEVEL" and e["model_id"] == "fake-legacy-model"
            for e in entries))

    def test_db_hybrid_backend_success_path_sets_kp_backend_used_and_logs_telemetry(self):
        fake_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                        "model_id": "fake-model", "cost_jpy": 1.2345, "shortlist_total_count": 20,
                        "cost_guard_exceeded": False}
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         return_value=dict(fake_result)):
            result = sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_db_hybrid_success", "TEST_ID_2", "TEST_LEVEL",
                process=None, kp_backend="db_hybrid")
        self.assertEqual(result["kp_backend_used"], "db_hybrid")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS")
        entries = self._read_new_lines()
        self.assertTrue(any(e["article_id"] == "TEST_ID_2" and not e["fallback_triggered"] and
                             e["requested_backend"] == "db_hybrid" and e["backend_used"] == "db_hybrid"
                             for e in entries))

    def test_db_hybrid_backend_failure_triggers_fallback_and_logs_telemetry(self):
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
        entries = self._read_new_lines()
        self.assertTrue(any(e["article_id"] == "TEST_ID_3" and e["fallback_triggered"]
                             and e["fallback_reason_code"] == "SHORTLIST_TOO_SMALL" for e in entries))

    def test_run_key_phrases_default_kp_backend_is_strategy_l(self):
        self.assertEqual(sc.run_key_phrases.__defaults__[-1], "strategy_l")

    def test_family_x_runner_default_kp_backend_is_db_hybrid(self):
        import er019_family_x_audio_production_runner_01 as runner
        self.assertEqual(runner.run_theme_scaffold.__defaults__[-1], "db_hybrid")


if __name__ == "__main__":
    unittest.main()
