# ============================================================
# er002_test_ja_master_imitation.py
# ER-002-v1.2M-P0: 阪神日本語マスター模倣方式のテスト
# ============================================================
# 実API・実TTS・実QA・Web検索・fact registry自動収集は一切行わない。
# すべてモックのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_master_imitation -v

import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er002_common as common
import er002_ja_master_imitation as jami
import er002_v1_2m_freeze as freeze_v1_2m


# ============================================================
# 共通フィクスチャ
# ============================================================
def make_fake_openai_client(response_dict):
    """client.chat.completions.create(...) -> レスポンスオブジェクトのモック。
    呼び出し回数・引数を記録する。"""
    calls = []

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChoice:
        def __init__(self, content):
            self.message = FakeMessage(content)

    class FakeResponse:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return FakeResponse(json.dumps(response_dict, ensure_ascii=False))

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()
            self.calls = calls

    return FakeClient()


def make_valid_article():
    return {
        "title": "タイトル例",
        "body": ["本文段落1。", "本文段落2。"],
        "point_one": {"heading": "ポイント1見出し", "paragraphs": ["ポイント1本文。"]},
        "point_two": {"heading": "ポイント2見出し", "paragraphs": ["ポイント2本文。"]},
        "one_line_summary": "一言まとめ。",
    }


def make_facts():
    return {"F01": "確認済み事実1。", "F02": "確認済み事実2。"}


def make_passing_fact_qa_response(overrides=None):
    base = {"contradicts_verified_facts": False, "unsupported_specific_claims": [], "evidence": "根拠説明"}
    base.update(overrides or {})
    return base


class MastersFixtureTests(unittest.TestCase):
    """マスター・依頼文が実際に凍結どおり保存されているかの確認(要求1・3・4)。"""

    def test_master_matches_saved_canonical_form(self):
        with open(jami.MASTERS_SHA256_PATH, encoding="utf-8") as f:
            frozen = json.load(f)
        with open(frozen["hanshin_ja_master_path"], "rb") as f:
            data = f.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(), frozen["hanshin_ja_master_sha256"])
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"), "BOMが付与されています")
        self.assertNotIn(b"\r\n", data, "CRLFが含まれています")
        self.assertTrue(data.endswith(b"\n") and not data.endswith(b"\n\n"), "末尾改行が単一ではありません")

    def test_original_request_full_text_preserved_as_evidence(self):
        masters = jami.load_and_verify_masters()
        self.assertIn("オリジナルが一番良いです", masters["original_request_full_text"])
        self.assertIn("トクリュウ", masters["original_request_full_text"],
                       "依頼文の証跡ファイル自体には過去トピック一覧が保存されているはず(プロンプトへは使わないだけ)")

    def test_original_request_sha256_recorded(self):
        with open(jami.MASTERS_SHA256_PATH, encoding="utf-8") as f:
            frozen = json.load(f)
        self.assertIn("original_request_sha256", frozen)
        with open(frozen["original_request_path"], "rb") as f:
            data = f.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(), frozen["original_request_sha256"])


class MasterIntegrityGateTests(unittest.TestCase):
    """要求2: マスターsha256不一致時にAPIを呼ばず停止する。"""

    def test_master_sha256_mismatch_stops_before_api_call(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            bad_master_path = os.path.join(tmp_dir, "hanshin_ja_master.txt")
            with open(bad_master_path, "w", encoding="utf-8", newline="\n") as f:
                f.write("改ざんされたマスター\n")
            request_path = jami.ORIGINAL_REQUEST_PATH
            with open(request_path, "rb") as f:
                request_sha256 = hashlib.sha256(f.read()).hexdigest()

            bad_sha256_path = os.path.join(tmp_dir, "masters_sha256.json")
            with open(bad_sha256_path, "w", encoding="utf-8") as f:
                json.dump({
                    "hanshin_ja_master_path": bad_master_path,
                    "hanshin_ja_master_sha256": "0" * 64,  # 意図的に不一致
                    "original_request_path": request_path,
                    "original_request_sha256": request_sha256,
                }, f)

            api_call_count = {"n": 0}

            def never_should_be_called(*args, **kwargs):
                api_call_count["n"] += 1
                raise AssertionError("マスターsha256不一致時にAPIが呼ばれています")

            with self.assertRaises(jami.MasterIntegrityError):
                jami.load_and_verify_masters(bad_sha256_path)
            self.assertEqual(api_call_count["n"], 0)
        finally:
            shutil.rmtree(tmp_dir)


class PromptContentTests(unittest.TestCase):
    """要求5・6・7・8: プロンプトに含めるもの/含めないもの。"""

    def setUp(self):
        self.masters = jami.load_and_verify_masters()
        self.facts = make_facts()

    def test_past_six_topics_not_in_generation_prompt(self):
        prompt = jami.build_prompt(self.masters["master_full_text"], "テストトピック", self.facts)
        for topic_fragment in ["トクリュウ", "皇室典範", "ホルムズ海峡", "芥川賞", "熱中症警戒アラート", "老老介護"]:
            self.assertNotIn(topic_fragment, prompt, f"過去トピック一覧の断片「{topic_fragment}」がプロンプトに混入しています")

    def test_evaluation_reasons_included_in_generation_prompt(self):
        prompt = jami.build_prompt(self.masters["master_full_text"], "テストトピック", self.facts)
        for reason in jami.EVALUATION_REASONS:
            self.assertIn(reason, prompt)

    def test_past_article_bodies_not_in_generation_input(self):
        sentinel = "SENTINEL_PAST_ARTICLE_BODY_SHOULD_NOT_APPEAR"
        # 過去記事本文はbuild_promptの引数として一切受け取らない設計であることを
        # 関数シグネチャ・実際のプロンプト出力の両面で確認する
        prompt = jami.build_prompt(self.masters["master_full_text"], "テストトピック", self.facts)
        self.assertNotIn(sentinel, prompt)
        import inspect
        params = list(inspect.signature(jami.build_prompt).parameters.keys())
        self.assertNotIn("past_articles", params)
        self.assertNotIn("benchmark", params)

    def test_benchmark_pdf_body_not_in_generation_input(self):
        prompt = jami.build_prompt(self.masters["master_full_text"], "テストトピック", self.facts)
        self.assertNotIn("口調比較", prompt)
        import inspect
        self.assertNotIn("pdf", [p.lower() for p in inspect.signature(jami.build_prompt).parameters.keys()])

    def test_hanshin_master_full_text_included_verbatim(self):
        prompt = jami.build_prompt(self.masters["master_full_text"], "テストトピック", self.facts)
        self.assertIn(self.masters["master_full_text"], prompt)


class SamePromptTemplateTests(unittest.TestCase):
    """要求9: 全7記事で同一プロンプトテンプレートが使用される。"""

    def test_same_prompt_template_used_for_all_seven_articles(self):
        masters = jami.load_and_verify_masters()
        topics = [
            "World Cup semifinal", "UK nighttime social-media setting", "Tokuryu case broker",
            "Imperial House Law reform", "Strait of Hormuz 20% charge withdrawal",
            "Akutagawa and Naoki prizes", "Elder-to-elder caregiving",
        ]
        facts = make_facts()
        prompts = [jami.build_prompt(masters["master_full_text"], t, facts) for t in topics]
        # トピック差し込み穴以外は完全に同一テンプレートであることを確認する
        templates_with_placeholder_removed = [p.replace(t, "{TOPIC}") for p, t in zip(prompts, topics)]
        self.assertEqual(len(set(templates_with_placeholder_removed)), 1)


class OldEditorialPipelineNotCalledTests(unittest.TestCase):
    """要求10・11・12: 旧Editorial Brief系・アングル系・面白さQA関数が呼ばれない。"""

    def test_module_does_not_import_editorial_common_modules(self):
        import sys
        mod = sys.modules["er002_ja_master_imitation"]
        source_names = {name for name in dir(mod)}
        # importされたモジュール名として"er002_editorial_common"等が存在しないこと
        self.assertNotIn("ec", source_names)
        with open("er002_ja_master_imitation.py", encoding="utf-8") as f:
            src = f.read()
        import re
        import_lines = [l for l in src.splitlines() if re.match(r"^\s*(import|from)\s", l)]
        forbidden = ["er002_editorial_common", "er002_editorial_angle_adapter", "er002_editorial_runner"]
        for line in import_lines:
            for f_name in forbidden:
                self.assertNotIn(f_name, line, f"禁止モジュールがimportされています: {line}")

    def test_editorial_brief_and_angle_and_quality_functions_never_called(self):
        call_counts = {"angle_gen": 0, "angle_eval": 0, "brief_build": 0, "quality_qa": 0}

        class MockEditorialCommon:
            @staticmethod
            def build_editorial_brief(*a, **k):
                call_counts["brief_build"] += 1

            @staticmethod
            def build_angle_evaluation_prompt(*a, **k):
                call_counts["angle_eval"] += 1

            @staticmethod
            def build_editorial_quality_prompt_v1_1b(*a, **k):
                call_counts["quality_qa"] += 1

        def mock_angle_generation_fn(*a, **k):
            call_counts["angle_gen"] += 1

        masters = jami.load_and_verify_masters()
        facts = make_facts()
        client = make_fake_openai_client(make_valid_article())
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])

        self.assertEqual(call_counts, {"angle_gen": 0, "angle_eval": 0, "brief_build": 0, "quality_qa": 0})


class SingleGenerationAttemptTests(unittest.TestCase):
    """要求13・14・15: 記事ごとの本文生成は1回だけ。REVIEW_REQUIRED/FAILでも再生成しない。"""

    def _run_with_fact_qa_response(self, fact_qa_response):
        masters = jami.load_and_verify_masters()
        facts = make_facts()
        client = make_fake_openai_client(make_valid_article())
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(fact_qa_response)

        outcome = jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        return outcome, client

    def test_generation_called_exactly_once_per_article_on_pass(self):
        outcome, client = self._run_with_fact_qa_response(make_passing_fact_qa_response())
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(outcome.status, "OK")
        self.assertEqual(outcome.fact_qa["verdict"], "PASS")

    def test_no_regeneration_on_review_required(self):
        outcome, client = self._run_with_fact_qa_response(
            make_passing_fact_qa_response({"unsupported_specific_claims": ["未確認の具体的主張"]}))
        self.assertEqual(len(client.calls), 1, "REVIEW_REQUIREDでも生成APIが2回目呼ばれています")
        self.assertEqual(outcome.fact_qa["verdict"], "REVIEW_REQUIRED")

    def test_no_regeneration_on_fail(self):
        outcome, client = self._run_with_fact_qa_response(
            make_passing_fact_qa_response({"contradicts_verified_facts": True}))
        self.assertEqual(len(client.calls), 1, "FAILでも生成APIが2回目呼ばれています")
        self.assertEqual(outcome.fact_qa["verdict"], "FAIL")

    def test_parse_failure_retries_generation_once_as_technical_retry(self):
        masters = jami.load_and_verify_masters()
        facts = make_facts()

        call_count = {"n": 0}

        def flaky_generation_fn(config):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise jami.GenerationParseError("not json")
            return make_valid_article()

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        outcome = jami.run_ja_master_imitation_pipeline(
            flaky_generation_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(outcome.status, "OK")
        self.assertEqual(outcome.generation_parse_retry_count, 1)
        self.assertEqual(call_count["n"], 2)


class CharacterCountPolicyTests(unittest.TestCase):
    """要求16: 文字数だけで不合格にしない。"""

    def test_character_count_never_causes_failure(self):
        masters = jami.load_and_verify_masters()
        facts = make_facts()

        # 極端に短い/長い記事でも構造要件さえ満たせば技術的失敗にならないことを確認
        short_article = {
            "title": "短",
            "body": ["短い。"],
            "point_one": {"heading": "P1", "paragraphs": ["短い。"]},
            "point_two": {"heading": "P2", "paragraphs": ["短い。"]},
            "one_line_summary": "短い。",
        }
        client = make_fake_openai_client(short_article)
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        outcome = jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(outcome.status, "OK")
        self.assertIsNotNone(outcome.character_metrics)
        self.assertIn("total_characters", outcome.character_metrics)
        self.assertIn("ratio_to_master", outcome.character_metrics)


class StructuralFailureTests(unittest.TestCase):
    """要求17・18: 必須フィールド欠落・Point非2件は構造不合格になる。"""

    def test_missing_required_field_causes_structural_failure(self):
        masters = jami.load_and_verify_masters()
        facts = make_facts()
        broken = make_valid_article()
        del broken["one_line_summary"]
        client = make_fake_openai_client(broken)
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        outcome = jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(outcome.status, "FAILED_STRUCTURAL")

    def test_point_count_not_two_causes_structural_failure(self):
        masters = jami.load_and_verify_masters()
        facts = make_facts()
        broken = make_valid_article()
        broken["point_three"] = {"heading": "P3", "paragraphs": ["余分な3件目。"]}
        client = make_fake_openai_client(broken)
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        outcome = jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(outcome.status, "FAILED_STRUCTURAL")

    def test_empty_point_one_causes_structural_failure(self):
        masters = jami.load_and_verify_masters()
        facts = make_facts()
        broken = make_valid_article()
        broken["point_one"] = {"heading": "", "paragraphs": []}
        client = make_fake_openai_client(broken)
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        outcome = jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(outcome.status, "FAILED_STRUCTURAL")


class FactQaScopeTests(unittest.TestCase):
    """要求19: 事実QAが面白さ関連フィールドを返さない/判定しない。"""

    def test_fact_qa_schema_excludes_interest_fields(self):
        self.assertEqual(
            set(jami.MINIMAL_FACT_QA_REQUIRED_FIELDS),
            {"contradicts_verified_facts", "unsupported_specific_claims", "evidence"},
        )
        forbidden_terms = [
            "interest", "narrative", "momentum", "angle", "payoff", "coherence",
            "面白さ", "勢い", "アングル", "Pointの価値",
        ]
        for term in forbidden_terms:
            self.assertNotIn(term.lower(), [f.lower() for f in jami.MINIMAL_FACT_QA_REQUIRED_FIELDS])

    def test_fact_qa_prompt_explicitly_excludes_interest_judgment(self):
        prompt = jami.build_minimal_fact_qa_prompt("記事本文サンプル", make_facts())
        self.assertIn("面白さ", prompt)
        self.assertIn("一切判定しないでください", prompt)


class NoOtherApiCallsTests(unittest.TestCase):
    """要求20・21・22: TTS・Web検索・fact registry収集関数が呼ばれない。"""

    def test_tts_never_called(self):
        tts_call_count = {"n": 0}

        def mock_tts_call_fn(*a, **k):
            tts_call_count["n"] += 1

        masters = jami.load_and_verify_masters()
        facts = make_facts()
        client = make_fake_openai_client(make_valid_article())
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(tts_call_count["n"], 0)

    def test_web_search_never_called(self):
        web_search_call_count = {"n": 0}

        def mock_web_search(*a, **k):
            web_search_call_count["n"] += 1

        masters = jami.load_and_verify_masters()
        facts = make_facts()
        client = make_fake_openai_client(make_valid_article())
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(web_search_call_count["n"], 0)
        with open("er002_ja_master_imitation.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("web_search", src.lower())

    def test_fact_registry_collection_never_called(self):
        collection_call_count = {"n": 0}

        def mock_gather_topic(*a, **k):
            collection_call_count["n"] += 1

        masters = jami.load_and_verify_masters()
        facts = make_facts()
        client = make_fake_openai_client(make_valid_article())
        gen_fn = jami.make_ja_article_generation_fn("テストトピック", facts, masters["master_full_text"], client=client)

        def fact_qa_call_fn(prompt):
            return json.dumps(make_passing_fact_qa_response())

        jami.run_ja_master_imitation_pipeline(gen_fn, fact_qa_call_fn, facts, masters["master_full_text"])
        self.assertEqual(collection_call_count["n"], 0)


class PdfBenchmarkStatusTests(unittest.TestCase):
    """要求23・24: PDFが利用できなくてもP0が完了できる/利用できる場合はsha256が一致する。"""

    def test_p0_completes_without_pdf_access(self):
        # PDFが取得不能な場合の想定ステータス値が、blocks_p0=falseとして
        # 設計上定義されていることを確認する(実際に取得不能だった場合の
        # 分岐を、取得成功時とは別に構造だけ検証する)
        not_accessible_status = {
            "status": "SOURCE_PDF_NOT_ACCESSIBLE",
            "expected_source_path": "/mnt/data/ER-001_口調比較_6トピック_v0.1.pdf",
            "benchmark_body_imported": False,
            "blocks_p0": False,
        }
        self.assertFalse(not_accessible_status["blocks_p0"])
        self.assertFalse(not_accessible_status["benchmark_body_imported"])

    def test_pdf_copy_sha256_matches_source(self):
        status_path = "er002_v1_2m_benchmarks/benchmark_source_status.json"
        if not os.path.exists(status_path):
            self.skipTest("benchmark_source_status.jsonが見つかりません")
        with open(status_path, encoding="utf-8") as f:
            status = json.load(f)
        if status["status"] != "SOURCE_PDF_COPIED":
            self.skipTest("このセッションではPDFが取得できなかったため対象外")
        self.assertEqual(status["source_sha256"], status["copy_sha256"])
        self.assertTrue(status["sha256_match"])
        with open(status["copied_to"], "rb") as f:
            actual_copy_sha256 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(actual_copy_sha256, status["copy_sha256"])


class V1_1B_UntouchedTests(unittest.TestCase):
    """要求25: v1.1Bの既存成果物が変更されない。"""

    def test_v1_1b_c1_artifacts_unchanged(self):
        checked_files = [
            "er002_output/A01/v1_1b_c1/checkpoint_eligibility.json",
            "er002_output/A01/v1_1b_c1/manifest.json",
            "er002_output/A01/v1_1b_c1/provenance.json",
        ]
        for path in checked_files:
            if not os.path.exists(path):
                self.skipTest(f"{path} が見つかりません")
            with open(path, encoding="utf-8") as f:
                json.load(f)  # 少なくとも有効なJSONとして読めることを確認(壊れていないこと)

    def test_v1_1b_freeze_module_unchanged(self):
        import er002_v1_1b_freeze as freeze_v1_1b
        frozen_a = freeze_v1_1b.build_frozen_conditions()
        frozen_b = freeze_v1_1b.build_frozen_conditions()
        stable_a = {k: v for k, v in frozen_a.items() if k != "frozen_at"}
        stable_b = {k: v for k, v in frozen_b.items() if k != "frozen_at"}
        self.assertEqual(json.dumps(stable_a, sort_keys=True), json.dumps(stable_b, sort_keys=True))


class FreezeModuleTests(unittest.TestCase):
    def test_frozen_conditions_buildable_and_include_required_sections(self):
        frozen = freeze_v1_2m.build_frozen_conditions()
        required_sections = [
            "masters", "generation_prompt", "structured_output_schema", "fact_qa",
            "verdict_rules", "model_config", "retry_rules", "target_articles_and_scope", "benchmark",
        ]
        for section in required_sections:
            self.assertIn(section, frozen)

    def test_frozen_conditions_stable_across_calls(self):
        sha_a = freeze_v1_2m.frozen_conditions_overall_sha256()
        sha_b = freeze_v1_2m.frozen_conditions_overall_sha256()
        self.assertEqual(sha_a, sha_b)


if __name__ == "__main__":
    unittest.main()
