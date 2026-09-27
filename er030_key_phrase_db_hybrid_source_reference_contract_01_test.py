# ============================================================
# er030_key_phrase_db_hybrid_source_reference_contract_01_test.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
# ============================================================
# API呼び出しを一切行わない構造unit test(Trial-06実データfixture[twins A2/
# Melos A2]を使うテストのみ、Stage1候補生成[ローカル決定論処理]のために
# Wiktionary APIを叩く既存挙動を引き継ぐ。新規APIコストはゼロ)。
#
# 実行: .venv/Scripts/python.exe -m unittest
#   er030_key_phrase_db_hybrid_source_reference_contract_01_test -v
# ============================================================

from __future__ import annotations

import os
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_min_unit as p2g
import er003_v1_n3_01_scaffold_generate as sc
import er023_key_phrase_db_ingest as ing
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref_contract

TWINS_A2_PATH = "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt"
MELOS_A2_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"


def _fixture_shortlist():
    return [
        {"surface_form": "digital twin", "canonical_form": "digital twin", "unit_type": "noun_phrase",
         "important_noun_phrase_candidate": True, "source_span": "digital twin",
         "context_sentence_id": "S3", "occurrence_count_in_article": 2,
         "matched_dbs": ["wiktionary"], "db_categories": ["multiword_term"]},
        {"surface_form": "take over", "canonical_form": "take over", "unit_type": "phrasal_verb",
         "important_noun_phrase_candidate": False, "source_span": "take over",
         "context_sentence_id": "S7", "occurrence_count_in_article": 1,
         "matched_dbs": ["ngsl"], "db_categories": []},
        {"surface_form": "audition", "canonical_form": "audition", "unit_type": "word",
         "important_noun_phrase_candidate": False, "source_span": "audition",
         "context_sentence_id": None, "occurrence_count_in_article": 3,
         "matched_dbs": ["cefr_j"], "db_categories": []},
    ]


def _fixture_sentence_reference():
    return {
        "S3": "Her digital twin appeared in the mirror",
        "S7": "The twin began to take over small tasks",
    }


class CandidateIdAssignmentTests(unittest.TestCase):
    def test_ids_are_sequential_and_unique(self):
        shortlist = _fixture_shortlist()
        result = src_ref_contract.assign_candidate_ids(shortlist)
        self.assertEqual(result["candidate_ids"], ["C1", "C2", "C3"])
        self.assertEqual(len(result["id_to_candidate"]), 3)
        self.assertEqual(result["id_to_candidate"]["C1"]["surface_form"], "digital twin")

    def test_original_shortlist_not_mutated(self):
        shortlist = _fixture_shortlist()
        src_ref_contract.assign_candidate_ids(shortlist)
        self.assertNotIn("candidate_id", shortlist[0])


class SchemaConstructionTests(unittest.TestCase):
    def test_source_span_and_source_sentence_removed_from_llm_schema(self):
        props = src_ref_contract.build_item_schema_properties(["C1", "C2", "C3"])
        self.assertNotIn("source_span", props)
        self.assertNotIn("source_sentence", props)
        self.assertIn("source_candidate_id", props)
        self.assertIn("surface_echo", props)
        self.assertEqual(props["source_candidate_id"]["enum"], ["C1", "C2", "C3"])

    def test_required_fields_match_properties_keys_exactly(self):
        candidate_ids = ["C1", "C2"]
        schema = src_ref_contract.build_json_schema(candidate_ids)
        item_schema = schema["schema"]["properties"]["items"]["items"]
        self.assertEqual(set(item_schema["required"]), set(item_schema["properties"].keys()))
        self.assertTrue(item_schema["additionalProperties"] is False)

    def test_item_count_fixed_at_5(self):
        schema = src_ref_contract.build_json_schema(["C1"])
        items_schema = schema["schema"]["properties"]["items"]
        self.assertEqual(items_schema["minItems"], 5)
        self.assertEqual(items_schema["maxItems"], 5)


class FamilyProfileGuardTests(unittest.TestCase):
    """Family別最終選定ルールの差込点: 現時点でサポートされているのは
    "family_x"のみであり、"family_z"は明示的にNotImplementedErrorになる
    こと(Family Z DB Hybrid Core v2全体の採用は本管理IDの対象外・未配線)。"""

    def test_family_x_supported(self):
        src_ref_contract._check_family_profile_supported("family_x")  # raiseしない

    def test_family_z_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            src_ref_contract._check_family_profile_supported("family_z")

    def test_build_lightweight_user_message_rejects_family_z(self):
        with self.assertRaises(NotImplementedError):
            src_ref_contract.build_lightweight_user_message(
                "Title", [], {}, "instructions", family_profile="family_z")

    def test_run_source_reference_contract_gate_rejects_family_z(self):
        # family_profile検査は実際にselector callを行う前(冒頭)で発生する
        # ため、make_selector_factoryには何も呼ばれないダミーを渡せば足りる。
        with self.assertRaises(NotImplementedError):
            src_ref_contract.run_source_reference_contract_gate(
                "ARTICLE_ID", lambda: None, "text", {}, {}, family_profile="family_z")

    def test_run_db_hybrid_selection_default_family_profile_is_family_x(self):
        # family_profileはrun_db_hybrid_selectionの最後の位置引数(既定値
        # 付き)であるため、__defaults__の最後の要素と一致する。
        self.assertEqual(db_hybrid.run_db_hybrid_selection.__defaults__[-1], "family_x")


class RestoreSourceFieldsTests(unittest.TestCase):
    """候補ID -> source_sentence/source_span復元の決定論性・複数出現候補の
    復元規則・enum外/防御的unresolvedケース・source_reference_contract
    タグ付与(Trial-06から昇格、Production module側で再検証)。"""

    def setUp(self):
        ids = src_ref_contract.assign_candidate_ids(_fixture_shortlist())
        self.id_to_candidate = ids["id_to_candidate"]
        self.sentence_reference = _fixture_sentence_reference()

    def test_deterministic_restoration_same_input_same_output(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"}]
        r1 = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        r2 = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(r1["items"][0]["source_span"], r2["items"][0]["source_span"])
        self.assertEqual(r1["items"][0]["source_sentence"], r2["items"][0]["source_sentence"])

    def test_source_sentence_restored_from_context_sentence_id(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"}]
        restored = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        item = restored["items"][0]
        self.assertEqual(item["source_span"], "digital twin")
        self.assertEqual(item["source_sentence"], "Her digital twin appeared in the mirror")

    def test_source_reference_contract_tag_default(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"}]
        restored = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(restored["items"][0]["source_reference_contract"], "candidate_id_v1")
        self.assertEqual(restored["items"][0]["resolved_candidate_id"], "C1")

    def test_candidate_without_context_sentence_id_falls_back_to_source_span(self):
        items = [{"rank": 1, "source_candidate_id": "C3", "surface_echo": "audition"}]
        restored = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        item = restored["items"][0]
        self.assertEqual(item["source_span"], "audition")
        self.assertEqual(item["source_sentence"], "audition")

    def test_unresolved_candidate_id_is_defensively_recorded(self):
        items = [{"rank": 1, "source_candidate_id": "C999", "surface_echo": "x"}]
        restored = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(len(restored["unresolved"]), 1)

    def test_surface_echo_mismatching_candidate_flagged_non_blocking(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "take over"}]
        restored = src_ref_contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertTrue(restored["items"][0]["candidate_mismatch_suspected"])
        self.assertEqual(restored["mismatch_count"], 1)
        # 非ブロッキング: 取り違え検知はsource_span/source_sentenceの復元結果には影響しない。
        self.assertEqual(restored["items"][0]["source_span"], "digital twin")


class ProductionValidatorUnchangedIntegrationTests(unittest.TestCase):
    """復元後の辞書が既存p2g.validate_min_unit_selection(無変更)をそのまま
    通せる形になっていること。"""

    def test_restored_item_has_all_required_fields_for_existing_validator(self):
        ids = src_ref_contract.assign_candidate_ids(_fixture_shortlist())
        item = {
            "rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin",
            "display_phrase": "digital twin", "ja_gloss": "デジタルツイン",
            "phrase_type": "noun_phrase", "normalization_type": "none", "normalization_note": "",
            "selection_reason": "reason", "listening_difficulty_reason": "reason",
            "inference_transparency": "MEDIUM", "topic_exposure_dependency": "MEDIUM",
            "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW",
            "spoiler_risk": "LOW", "portfolio_category": "domain_expression",
            "portfolio_substitution": False, "portfolio_substitution_reason": "",
        }
        restored = src_ref_contract.restore_source_fields(
            [item], ids["id_to_candidate"], _fixture_sentence_reference())
        restored_item = restored["items"][0]
        for field in p2g._ITEM_REQUIRED_FIELDS:
            self.assertIn(field, restored_item, f"missing field: {field}")
            self.assertIsInstance(restored_item[field], (str, int, bool))


class Stage1SourceSpanSemanticsRegressionTests(unittest.TestCase):
    """Stage 1 source_span整理(er030 core): `important_noun_phrase_
    candidate`(`repeated_compound_noun_heuristic`)カテゴリのみ、
    `source_span`が「句」(surface_form相当)へ補正され、旧「文全体」の
    値は`legacy_sentence_text`(deprecated)へ退避されること。他カテゴリ
    (n-gram一致・rare single word)は元々`source_span`=`surface_form`で
    あり無変化なこと。候補生成の実質的内容(canonical_form列)は無変更
    (既存equivalence testが別途検証)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_repeated_compound_noun_source_span_matches_surface_form_and_legacy_preserved(self):
        # "contract worker(s)"を記事中に2回以上出現させ、
        # find_repeated_compound_noun_candidates経由でimportant_noun_
        # phrase_candidateとして拾われることを狙ったfixture(既存Trial-06
        # REPORT §2で実データ発見したのと同種の構造)。
        text = (
            "In some calls through Muse, trained contract workers made the calls, not AI. "
            "The company said contract workers followed a script during every call."
        )
        result = core.run_stage1_for_article(text, self.dbs)
        candidates = [c for c in result["important_noun_candidates"]
                      if c["canonical_form"] == "contract workers"]
        self.assertEqual(len(candidates), 1, "fixtureがcontract workersを拾えていません")
        cand = candidates[0]
        self.assertIn("repeated_compound_noun_heuristic", cand["matched_dbs"])
        # 補正後: source_spanは短い句(surface_form)と一致する。
        self.assertEqual(cand["source_span"], cand["surface_form"])
        self.assertNotIn(cand["source_span"].lower(), ("in some calls through muse, trained "
                                                        "contract workers made the calls, not ai",))
        # 退避先: legacy_sentence_textには旧来の「文全体」の値が残っている
        # (silent semantic changeを避ける、値そのものは失わない)。
        self.assertIn("contract worker", cand["legacy_sentence_text"].lower())
        self.assertGreater(len(cand["legacy_sentence_text"]), len(cand["source_span"]))

    def test_other_candidate_categories_unaffected_by_normalization(self):
        # n-gram一致由来のphrase_survivors/word_survivorsは元々
        # source_span=surface_formであり、本Stage1整理による変化はない
        # (legacy_sentence_textフィールドも付与しない、対象カテゴリ外)。
        text = "The rare self-awakening phenomenon interested researchers deeply."
        result = core.run_stage1_for_article(text, self.dbs)
        for c in (result["phrase_survivors"] + result["word_survivors"]):
            self.assertEqual(c.get("source_span"), c.get("surface_form"))
            self.assertNotIn("legacy_sentence_text", c)

    def test_shortlist_canonical_form_content_unchanged_by_normalization(self):
        # KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-
        # WIRING-01の要件: 候補生成・shortlist内容(canonical_form列・
        # 件数)はStage1整理の前後で同一であること。_normalize_important_
        # noun_candidate_source_spanは値を書き換えるのみでcanonical_form
        # 自体は一切変更しないことを直接検証する。
        fixture = [
            {"surface_form": "contract worker", "canonical_form": "contract worker",
             "source_span": "a long full sentence containing contract worker somewhere"},
            {"surface_form": "sea blockade", "canonical_form": "sea blockade",
             "source_span": "another long full sentence containing sea blockade somewhere"},
        ]
        normalized = core._normalize_important_noun_candidate_source_span(fixture)
        self.assertEqual([c["canonical_form"] for c in normalized],
                          [c["canonical_form"] for c in fixture])
        self.assertEqual(len(normalized), len(fixture))
        for orig, new in zip(fixture, normalized):
            self.assertEqual(new["source_span"], new["surface_form"])
            self.assertEqual(new["legacy_sentence_text"], orig["source_span"])
        # 元のlistは変更されない(コピーして返す)。
        self.assertEqual(fixture[0]["source_span"],
                          "a long full sentence containing contract worker somewhere")


def _good_qa():
    return {field: "PASS" for field in kc.QA_FIELDS}


class CanonicalizationPassthroughTests(unittest.TestCase):
    """keywords_canonicalized.jsonへの追加フィールド(source_candidate_id/
    surface_echo/source_reference_contract/candidate_mismatch_suspected)の
    backward compatibleなpassthrough。これらのフィールドを持たない既存
    経路(Strategy L)の出力形は一切変化しないこと。"""

    GOOD_ITEM = {
        "rank": 1, "source_span": "digital twin", "source_sentence": "Her digital twin appeared.",
        "display_phrase": "digital twin", "ja_gloss": "デジタルツイン",
    }

    @staticmethod
    def _build_full_canon_item(rank):
        return {
            "rank": rank, "key_phrase": "digital twin", "changed_from_display_phrase": False,
            "normalization_reason": "", "reasoning": "ok", **_good_qa(),
        }

    def test_new_fields_passed_through_when_present(self):
        original = dict(self.GOOD_ITEM)
        original.update({
            "source_reference_contract": "candidate_id_v1", "source_candidate_id": "C7",
            "surface_echo": "digital twin", "candidate_mismatch_suspected": False,
        })
        canon_items = [self._build_full_canon_item(1)]
        merged = kc.merge_canonicalization_result([original], canon_items)
        item = merged["items"][0]
        self.assertEqual(item["source_reference_contract"], "candidate_id_v1")
        self.assertEqual(item["source_candidate_id"], "C7")
        self.assertEqual(item["surface_echo"], "digital twin")
        self.assertFalse(item["candidate_mismatch_suspected"])
        # 従来どおりsource_span/source_sentenceは無変更のまま保存される。
        self.assertEqual(item["source_span"], "digital twin")

    def test_legacy_items_without_new_fields_unaffected(self):
        # Strategy L等、これらのフィールドを一切持たない既存経路の
        # itemを渡した場合、mergeの出力に新フィールドは一切追加されない
        # (backward compatible、既存挙動の完全維持)。
        original = dict(self.GOOD_ITEM)
        canon_items = [self._build_full_canon_item(1)]
        merged = kc.merge_canonicalization_result([original], canon_items)
        item = merged["items"][0]
        for new_field in ("source_reference_contract", "source_candidate_id", "surface_echo",
                          "candidate_mismatch_suspected"):
            self.assertNotIn(new_field, item)


class FallbackContractMixingTelemetryTests(unittest.TestCase):
    """db_hybrid成功時はsource_reference_contract="candidate_id_v1"、
    fallback(Strategy L)発火時はsource_reference_contract=
    "free_text_strategy_l"がtelemetryへ記録され、両契約の混在を観測
    可能であること(API呼び出しなし、mockのみ)。"""

    def setUp(self):
        import tempfile
        self._tmp_dir = tempfile.mkdtemp(prefix="kp_src_ref_contract_telemetry_test_")
        self._tmp_telemetry_path = os.path.join(self._tmp_dir, "telemetry.jsonl")
        self._patcher = mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", self._tmp_telemetry_path)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def _read_new_lines(self):
        import json
        if not os.path.exists(self._tmp_telemetry_path):
            return []
        with open(self._tmp_telemetry_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def test_db_hybrid_success_tags_candidate_id_v1(self):
        fake_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [],
                        "model_id": "fake-model", "cost_jpy": 1.0, "shortlist_total_count": 20,
                        "cost_guard_exceeded": False, "source_reference_contract": "candidate_id_v1",
                        "candidate_mismatch_suspected_count": 0}
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         return_value=dict(fake_result)):
            sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_src_ref_contract_success", "TEST_SRC_REF_SUCCESS",
                "TEST_LEVEL", process=None, kp_backend="db_hybrid")
        entries = self._read_new_lines()
        self.assertTrue(any(e.get("source_reference_contract") == "candidate_id_v1" for e in entries))

    def test_fallback_tags_free_text_strategy_l(self):
        fallback_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": []}
        with mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection",
                         side_effect=db_hybrid.DbHybridFailure(
                             "SHORTLIST_TOO_SMALL", "forced for test",
                             telemetry={"shortlist_total_count": 3})), \
             mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                               return_value=dict(fallback_result)):
            sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_src_ref_contract_fallback", "TEST_SRC_REF_FALLBACK",
                "TEST_LEVEL", process=None, kp_backend="db_hybrid")
        entries = self._read_new_lines()
        self.assertTrue(any(e.get("source_reference_contract") == "free_text_strategy_l" and
                             e.get("fallback_triggered") for e in entries))

    def test_legacy_strategy_l_default_tags_free_text_strategy_l(self):
        fake_strategy_result = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []},
                                 "original_items": [], "model_id": "fake-legacy-model"}
        with mock.patch.object(sc, "_run_key_phrase_selection_strategy_l",
                                return_value=dict(fake_strategy_result)):
            sc.run_key_phrase_selection(
                "dummy article", "er030_output/_test_src_ref_contract_legacy", "TEST_SRC_REF_LEGACY",
                "TEST_LEVEL", process=None, kp_backend="strategy_l")
        entries = self._read_new_lines()
        self.assertTrue(any(e.get("source_reference_contract") == "free_text_strategy_l" for e in entries))


class LegacyInvariantTests(unittest.TestCase):
    """既定kp_backend("strategy_l")・Family Z(er026)の無配線は本管理IDに
    よって一切変化しないこと。"""

    def test_run_key_phrases_default_kp_backend_is_strategy_l(self):
        self.assertEqual(sc.run_key_phrases.__defaults__[-1], "strategy_l")

    def test_er026_family_z_text_runner_not_imported_by_new_contract_module(self):
        with open("er030_key_phrase_db_hybrid_source_reference_contract_01.py", encoding="utf-8") as f:
            lines = f.readlines()
        import_lines = [ln for ln in lines if ln.strip().startswith(("import ", "from "))]
        for ln in import_lines:
            self.assertNotIn("er026_", ln, f"Family Z text runnerへのimportが混入しています: {ln.strip()}")


if __name__ == "__main__":
    unittest.main()
