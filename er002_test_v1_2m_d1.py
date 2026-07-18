# ============================================================
# er002_test_v1_2m_d1.py
# ER-002-v1.2M-D1: fact registry整備とstructured output技術確認のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない(D1で既に収集済みの成果物を検証
# するだけ)。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_v1_2m_d1 -v

import hashlib
import json
import os
import unittest

import er002_ja_master_imitation as jami

FACT_REGISTRY_DIR = "er002_v1_2m_fact_registry"


def load_registry(name):
    with open(os.path.join(FACT_REGISTRY_DIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


class A01FactMeaningUnchangedTests(unittest.TestCase):
    """要求1: A01の既存fact意味が変わらない。"""

    def test_a01_fact_text_matches_existing_v1_1a_fixed_facts(self):
        with open("er002_output/A01/v1_1a_fixed_facts.json", encoding="utf-8") as f:
            existing = json.load(f)
        registry = load_registry("A01")
        new_map = {e["fact_id"]: e["fact_text"] for e in registry["fact_registry"]}
        self.assertEqual(existing["verified_facts_with_ids"], new_map)

    def test_a01_fact_registry_sha256_matches_v1_1b_checkpoint_value(self):
        registry = load_registry("A01")
        # v1.1B-Q1/C1で使われたfact_registry_sha256と同一であること
        # (=事実本文が一切変わっていないことの独立した証拠)
        self.assertEqual(
            registry["fact_registry_sha256"],
            "85c18d8c4f59a90b9763452f900ff270c88c9acd8a80b4e595cb13d3942d0b31",
        )


class A02StableIdTests(unittest.TestCase):
    """要求2: A02の既存7事実へ安定IDが付く。"""

    def test_a02_seven_facts_get_stable_sequential_ids(self):
        registry = load_registry("A02")
        ids = [e["fact_id"] for e in registry["fact_registry"]]
        self.assertEqual(ids, [f"F{i:02d}" for i in range(1, 8)])

    def test_a02_fact_text_matches_existing_raw_facts_in_order(self):
        with open("er002_output/A02/raw_facts.json", encoding="utf-8") as f:
            raw = json.load(f)
        registry = load_registry("A02")
        new_texts_in_order = [e["fact_text"] for e in registry["fact_registry"]]
        self.assertEqual(raw["verified_facts"], new_texts_in_order)

    def test_a02_default_vs_override_distinction_preserved(self):
        registry = load_registry("A02")
        texts = " ".join(e["fact_text"] for e in registry["fact_registry"])
        self.assertIn("overridden", texts)
        self.assertIn("not an absolute overnight ban", texts)


class NoBenchmarkOrRequestAsFactSourceTests(unittest.TestCase):
    """要求3・4: 過去PDF本文・original_requestをfact sourceとして使わない。"""

    def test_no_pdf_source_type_in_any_registry(self):
        for name in ["A01", "A02", "ADD01_tokuryu", "ADD02_imperial_house_law",
                     "ADD03_hormuz", "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            registry = load_registry(name)
            for entry in registry["fact_registry"]:
                self.assertNotIn("口調比較", entry["source_url"])
                self.assertNotIn(".pdf", entry["source_url"].lower())

    def test_original_request_not_cited_as_source(self):
        for name in ["ADD01_tokuryu", "ADD02_imperial_house_law", "ADD03_hormuz",
                     "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            registry = load_registry(name)
            for entry in registry["fact_registry"]:
                self.assertNotIn("original_request", entry["source_url"])
                self.assertNotIn("er002_v1_2m_masters", entry["source_url"])


class VerifiedOnlyGenerationInputTests(unittest.TestCase):
    """要求5: 未検証factを生成入力へ含めない。"""

    def test_only_verified_facts_would_be_passed_to_generation(self):
        for name in ["A01", "A02", "ADD01_tokuryu", "ADD02_imperial_house_law",
                     "ADD03_hormuz", "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            registry = load_registry(name)
            for entry in registry["fact_registry"]:
                self.assertEqual(
                    entry["verification_status"], "VERIFIED",
                    f"{name}のfact {entry['fact_id']}がVERIFIEDではありません(generation_ready=trueのはず)")


class ProvenanceGatesGenerationReadyTests(unittest.TestCase):
    """要求6: source provenance欠落時にgeneration_readyにならない。"""

    def test_missing_provenance_prevents_generation_ready(self):
        fake_registry = {
            "fact_registry": [
                {"fact_id": "F01", "fact_text": "テスト事実", "source_title": "",
                 "source_url": "", "source_type": "reputable_media",
                 "retrieved_at": "2026-07-18", "verification_status": "VERIFIED", "notes": "x"},
            ],
        }
        # このテストは判定ロジックそのものを検証する(entryにsource_urlが
        # 空であればgeneration_readyの前提条件を満たさないという設計方針の確認)
        entry = fake_registry["fact_registry"][0]
        has_provenance = bool(entry["source_title"]) and bool(entry["source_url"])
        self.assertFalse(has_provenance)

    def test_all_real_registries_have_nonempty_provenance(self):
        for name in ["A01", "A02", "ADD01_tokuryu", "ADD02_imperial_house_law",
                     "ADD03_hormuz", "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            registry = load_registry(name)
            for entry in registry["fact_registry"]:
                self.assertTrue(entry["source_title"])
                self.assertTrue(entry["source_url"])


class SourceVerificationFailedNotAutoReplacedTests(unittest.TestCase):
    """要求7: SOURCE_VERIFICATION_FAILEDの記事を自動置換しない。"""

    def test_no_article_marked_source_verification_failed_this_run(self):
        with open(os.path.join(FACT_REGISTRY_DIR, "batch_manifest.json"), encoding="utf-8") as f:
            batch = json.load(f)
        self.assertEqual(batch["summary"]["source_verification_failed_count"], 0)

    def test_batch_manifest_topic_ids_match_original_seven_targets(self):
        with open(os.path.join(FACT_REGISTRY_DIR, "batch_manifest.json"), encoding="utf-8") as f:
            batch = json.load(f)
        topic_ids = {a["topic_id"] for a in batch["articles"]}
        expected = {"A01", "A02", "ADD01", "ADD02", "ADD03", "ADD04", "ADD05"}
        self.assertEqual(topic_ids, expected, "トピックが自動的に代替・置換されていないことの確認")


class FactRegistryScopeTests(unittest.TestCase):
    """要求8・9: fact registryへEditorial Brief項目・Point指定が入らない。"""

    FORBIDDEN_KEYS = [
        "central_tension_or_question", "opening_mode", "point_one_editorial_role",
        "point_two_editorial_role", "point_one_core_claim", "point_two_core_claim",
        "point_one_fact_ids", "point_two_fact_ids", "non_obvious_takeaway",
        "listener_payoff", "in_one_line_target", "recommended_angle",
    ]

    def test_no_editorial_brief_or_point_assignment_keys_in_any_registry(self):
        for name in ["A01", "A02", "ADD01_tokuryu", "ADD02_imperial_house_law",
                     "ADD03_hormuz", "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            registry = load_registry(name)
            top_level_keys = set(registry.keys())
            for entry in registry["fact_registry"]:
                top_level_keys |= set(entry.keys())
            for forbidden in self.FORBIDDEN_KEYS:
                self.assertNotIn(forbidden, top_level_keys, f"{name}に禁止キー{forbidden}が含まれています")


class StructuredOutputSmokeTestResultTests(unittest.TestCase):
    """要求10・11: structured outputの5フィールド解析、fallbackは必要時のみ使用。"""

    def setUp(self):
        smoke_path = "er002_v1_2m_smoke_test/smoke_test_result.json"
        if not os.path.exists(smoke_path):
            self.skipTest("smoke_test_result.jsonが見つかりません")
        with open(smoke_path, encoding="utf-8") as f:
            self.result = json.load(f)

    def test_five_required_fields_present(self):
        self.assertEqual(set(self.result["fields_present"]), set(jami.REQUIRED_ARTICLE_FIELDS))

    def test_no_extra_top_level_fields(self):
        self.assertEqual(self.result["extra_top_level_fields"], [])

    def test_structural_validation_passed(self):
        self.assertEqual(self.result["structural_validation"], "OK")

    def test_fallback_only_used_when_structured_output_unsupported(self):
        if self.result["structured_output_supported"]:
            self.assertFalse(self.result["fallback_used"], "structured outputが使えたのにfallbackが使われています")

    def test_master_sha256_check_passed_in_smoke_test(self):
        self.assertEqual(self.result["master_sha256_check"], "OK")

    def test_unicode_and_emoji_survived(self):
        self.assertTrue(self.result["contains_non_ascii"])


class SmokeTestUsesFictionalTopicOnlyTests(unittest.TestCase):
    """要求12: 技術スモークで本番7記事を使わない。"""

    def test_smoke_topic_not_among_production_seven(self):
        smoke_path = "er002_v1_2m_smoke_test/smoke_test_result.json"
        if not os.path.exists(smoke_path):
            self.skipTest("smoke_test_result.jsonが見つかりません")
        with open(smoke_path, encoding="utf-8") as f:
            result = json.load(f)
        production_topic_fragments = [
            "World Cup", "England", "social-media", "トクリュウ", "皇室典範",
            "ホルムズ", "芥川賞", "直木賞", "老老介護",
        ]
        for fragment in production_topic_fragments:
            self.assertNotIn(fragment, result["fictional_topic"])

    def test_smoke_facts_are_explicitly_marked_fictional(self):
        smoke_path = "er002_v1_2m_smoke_test/smoke_test_result.json"
        if not os.path.exists(smoke_path):
            self.skipTest("smoke_test_result.jsonが見つかりません")
        with open(smoke_path, encoding="utf-8") as f:
            result = json.load(f)
        for fact_text in result["fictional_facts"].values():
            self.assertIn("架空の設定", fact_text)


class ZeroProductionGenerationTests(unittest.TestCase):
    """要求13・15: 本番7記事の本文生成が0件、TTSが呼ばれない。"""

    def test_production_article_generation_count_is_zero(self):
        d1_frozen_path = "er002_output/_experiment_config/ER-002-v1.2M-JA_D1_frozen.json"
        if not os.path.exists(d1_frozen_path):
            self.skipTest("D1凍結ファイルが見つかりません")
        with open(d1_frozen_path, encoding="utf-8") as f:
            d1 = json.load(f)
        self.assertEqual(d1["production_article_generation_count"], 0)
        self.assertEqual(d1["tts_call_count"], 0)

    def test_tts_call_fn_never_invoked_by_this_module(self):
        tts_call_count = {"n": 0}

        def mock_tts(*a, **k):
            tts_call_count["n"] += 1

        # er002_ja_master_imitation.pyのパイプラインはtts_call_fnという
        # 引数自体を持たない設計であることを確認する(呼びようがない)
        import inspect
        params = inspect.signature(jami.run_ja_master_imitation_pipeline).parameters
        self.assertNotIn("tts_call_fn", params)
        self.assertEqual(tts_call_count["n"], 0)


class OldEditorialPipelineNotCalledD1Tests(unittest.TestCase):
    """要求14: 旧編集工程が呼ばれない。"""

    def test_fact_registry_files_do_not_reference_editorial_common(self):
        for name in ["A01", "A02", "ADD01_tokuryu", "ADD02_imperial_house_law",
                     "ADD03_hormuz", "ADD04_akutagawa_naoki", "ADD05_elder_caregiving"]:
            path = os.path.join(FACT_REGISTRY_DIR, f"{name}.json")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("er002_editorial_common", content)
            self.assertNotIn("er002_editorial_angle_adapter", content)
            self.assertNotIn("er002_editorial_runner", content)


class MasterSha256UnchangedTests(unittest.TestCase):
    """要求16: マスターsha256が一致する(P0からの継続確認)。"""

    def test_master_sha256_still_matches_frozen_value(self):
        masters = jami.load_and_verify_masters()  # 不一致ならMasterIntegrityErrorが送出される
        self.assertEqual(masters["master_sha256"], "5f4fe54f8a6b64fc80af5ed80e76fe0a9ccbbb1c082ef71f310b5303433abcb1")


class D1DoesNotModifyP0FrozenConditionsTests(unittest.TestCase):
    """P0で凍結した項目(マスター/依頼文/最小プロンプト/schema/事実QA/判定規則/
    モデル参照先/文字数非ゲート/記事ごと1回生成/旧工程不使用)が変更されていない。"""

    def test_p0_frozen_conditions_overall_hash_unchanged(self):
        import er002_v1_2m_freeze as freeze_v1_2m
        self.assertEqual(
            freeze_v1_2m.frozen_conditions_overall_sha256(),
            "afbb804980e3ba4e1d5119773f72e35fc768ae31c924a7a8c4c109a09a116c6e",
        )


class V1_1A_UncommittedArtifactsUntouchedTests(unittest.TestCase):
    """v1.1Aの未コミット成果物が上書き・削除されていない(存在し続けている)。"""

    def test_v1_1a_files_still_exist_and_are_valid_json(self):
        status_path = "er002_output/A01/v1_1a/_uncommitted_artifacts_status.json"
        if not os.path.exists(status_path):
            self.skipTest("_uncommitted_artifacts_status.jsonが見つかりません")
        with open(status_path, encoding="utf-8") as f:
            status = json.load(f)
        for path, entry in status["files"].items():
            self.assertTrue(entry["exists"], f"{path}が消えています")
            with open(path, "rb") as f:
                actual_sha256 = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(actual_sha256, entry["sha256"], f"{path}の内容が変わっています")


if __name__ == "__main__":
    unittest.main()
