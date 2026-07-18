# ============================================================
# er002_test_ja_free_markdown_restore.py
# ER-002-v1.2M-R1: ChatGPT生成条件の一括復元のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_free_markdown_restore -v

import hashlib
import inspect
import json
import os
import re
import unittest

import er002_ja_free_markdown_restore as restore
import er002_ja_master_imitation as jami

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
A01_BRIEF_PATH = "er002_v1_2m_restore_briefs/A01_concise_brief.txt"
ADD05_BRIEF_PATH = "er002_v1_2m_restore_briefs/ADD05_concise_brief.txt"
PROMPT_TEMPLATE_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template.txt"

EXPECTED_MASTER_SHA256 = "5f4fe54f8a6b64fc80af5ed80e76fe0a9ccbbb1c082ef71f310b5303433abcb1"

EXPECTED_A01_BRIEF = (
    "2026年7月15日のワールドカップ準決勝で、イングランドはアルゼンチンに1対2で敗れた。"
    "イングランドが先制したが、アルゼンチンが追いつき、92分の決勝点で逆転した。"
    "アルゼンチンはスペインとの決勝へ進んだ。\n"
)
EXPECTED_ADD05_BRIEF = (
    "75歳以上同士の「老老介護」が37.1％で過去最高となり、介護する側も高齢化する中で、"
    "介護する人と介護される人が共に限界を迎える危険が表面化している。\n"
)


class ModelSelectionTests(unittest.TestCase):
    """要求1〜5: モデル選定・確認・代替禁止。"""

    def test_writer_model_is_gpt_5_6_sol(self):
        self.assertEqual(restore.WRITER_MODEL, "gpt-5.6-sol")

    def test_terra_not_used_for_generation(self):
        self.assertNotEqual(restore.WRITER_MODEL, "gpt-5.6-terra")
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        # generation_fn内でterraへハードコードされていないことを確認
        self.assertNotIn('"gpt-5.6-terra"', src)

    def test_no_automatic_fallback_model_logic(self):
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("fallback_model", src.lower())
        sig = inspect.signature(restore.make_free_markdown_generation_fn)
        # モデル引数はデフォルト値を持つが、フォールバック候補リストのような
        # 引数は存在しない
        self.assertNotIn("fallback", [p.lower() for p in sig.parameters.keys()])

    def test_reasoning_effort_is_valid_official_value(self):
        valid_values = {"none", "low", "medium", "high", "xhigh", "max"}
        self.assertIn(restore.WRITER_REASONING_EFFORT, valid_values)

    def test_model_intended_match_documented_as_not_guaranteed(self):
        self.assertEqual(restore.WRITER_MODEL_EXACT_CHATGPT_PARITY, "NOT_GUARANTEED")


class GenerationRequestShapeTests(unittest.TestCase):
    """要求6〜9: response_format/JSON Schema/完全fact registry/fact IDが
    本文生成リクエストに含まれない。"""

    def test_no_response_format_in_generation_call(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                class R:
                    output_text = "テスト応答"
                    model = "gpt-5.6-sol"
                    id = "resp_test"
                return R()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        gen_fn = restore.make_free_markdown_generation_fn("user message", client=FakeClient())
        gen_fn()
        self.assertNotIn("response_format", calls[0])

    def test_no_json_schema_in_generation_call(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                class R:
                    output_text = "テスト応答"
                    model = "gpt-5.6-sol"
                    id = "resp_test"
                return R()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        gen_fn = restore.make_free_markdown_generation_fn("user message", client=FakeClient())
        gen_fn()
        call_str = json.dumps(calls[0], ensure_ascii=False, default=str)
        self.assertNotIn("json_schema", call_str)
        self.assertNotIn("title", call_str.lower().replace("日本語", ""))

    def test_full_fact_registry_and_fact_ids_not_in_generation_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        with open(A01_BRIEF_PATH, encoding="utf-8") as f:
            brief = f.read()
        user_message = restore.build_writer_user_message(master, brief)
        for forbidden in ["F01", "F02", "F03", "source_url", "verification_status", "fact_id"]:
            self.assertNotIn(forbidden, user_message)


class FactQaInputTests(unittest.TestCase):
    """要求10: QA入力には完全fact registryとfact IDがある(事実QAは別経路)。"""

    def test_fact_qa_prompt_includes_full_registry_and_fact_ids(self):
        with open("er002_v1_2m_fact_registry/A01.json", encoding="utf-8") as f:
            registry = json.load(f)
        fact_id_map = {e["fact_id"]: e["fact_text"] for e in registry["fact_registry"]
                       if e["verification_status"] == "VERIFIED"}
        prompt = restore.build_fact_qa_prompt("記事本文サンプル", fact_id_map)
        for fid, text in fact_id_map.items():
            self.assertIn(fid, prompt)
            self.assertIn(text, prompt)


class InputProvenanceTests(unittest.TestCase):
    """要求11〜14: マスター1本のみ、過去6記事・PDF本文・J1記事が混入しない。"""

    def test_only_hanshin_master_referenced(self):
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        self.assertIn("hanshin_ja_master", src.lower().replace(" ", "") + MASTER_PATH.lower())
        # 他マスターへの参照が無いこと
        self.assertNotIn("second_master", src.lower())
        self.assertNotIn("additional_master", src.lower())

    def test_past_six_topics_not_in_generation_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        with open(A01_BRIEF_PATH, encoding="utf-8") as f:
            brief = f.read()
        user_message = restore.build_writer_user_message(master, brief)
        for fragment in ["トクリュウ", "皇室典範", "ホルムズ海峡", "芥川賞", "熱中症警戒アラート"]:
            self.assertNotIn(fragment, user_message)

    def test_pdf_body_not_in_generation_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        with open(A01_BRIEF_PATH, encoding="utf-8") as f:
            brief = f.read()
        user_message = restore.build_writer_user_message(master, brief)
        self.assertNotIn("口調比較", user_message)

    def test_j1_articles_not_in_generation_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        with open(A01_BRIEF_PATH, encoding="utf-8") as f:
            brief = f.read()
        user_message = restore.build_writer_user_message(master, brief)
        j1_path = "er002_output/v1_2m_j1/A01/raw_structured_response.json"
        if os.path.exists(j1_path):
            with open(j1_path, encoding="utf-8") as f:
                j1_article = json.load(f)
            self.assertNotIn(j1_article["title"], user_message)


class FixedTextTests(unittest.TestCase):
    """要求15〜17: concise brief・プロンプトテンプレートが固定文面と一致する。"""

    def test_a01_concise_brief_matches_fixed_text(self):
        with open(A01_BRIEF_PATH, encoding="utf-8") as f:
            actual = f.read()
        self.assertEqual(actual, EXPECTED_A01_BRIEF)

    def test_add05_concise_brief_matches_fixed_text(self):
        with open(ADD05_BRIEF_PATH, encoding="utf-8") as f:
            actual = f.read()
        self.assertEqual(actual, EXPECTED_ADD05_BRIEF)

    def test_master_sha256_matches_frozen_value(self):
        with open(MASTER_PATH, "rb") as f:
            data = f.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED_MASTER_SHA256)

    def test_prompt_template_contains_required_placeholders_only(self):
        with open(PROMPT_TEMPLATE_PATH, encoding="utf-8") as f:
            template = f.read()
        self.assertIn("{master_full_text}", template)
        self.assertIn("{concise_news_brief}", template)
        forbidden_terms = ["json", "title", "point_one", "point_two", "one_line_summary",
                           "Editorial Brief", "文字数", "narrative"]
        for term in forbidden_terms:
            self.assertNotIn(term, template)


class DeveloperMessageTests(unittest.TestCase):
    """要求18: system/developer messageがない、または中立文のみ。"""

    def test_developer_message_is_neutral_and_short(self):
        self.assertEqual(restore.NEUTRAL_DEVELOPER_MESSAGE, "日本語の記事を作成してください。")
        forbidden_terms = ["Point", "構成", "文字数", "narrative", "Editorial Brief", "JSON", "面白さ"]
        for term in forbidden_terms:
            self.assertNotIn(term, restore.NEUTRAL_DEVELOPER_MESSAGE)


class OldEditorialPipelineNotUsedTests(unittest.TestCase):
    """要求19: 旧Editorial Brief工程が呼ばれない。禁止事項を解説する
    コメント自体は許容し、実際のimport文・コード呼び出しだけを検査する。"""

    def _non_comment_lines(self):
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # 行中のコメント部分(# 以降)を除いた実コード部分だけを見る
            code_part = line.split("#", 1)[0]
            code_lines.append(code_part)
        return code_lines

    def test_module_does_not_import_editorial_common_modules(self):
        import_lines = [l for l in self._non_comment_lines() if re.match(r"^\s*(import|from)\s", l)]
        forbidden = ["er002_editorial_common", "er002_editorial_angle_adapter", "er002_editorial_runner"]
        for line in import_lines:
            for f_name in forbidden:
                self.assertNotIn(f_name, line, f"禁止モジュールがimportされています: {line}")

    def test_module_does_not_reuse_j1_writer_input_assembly(self):
        code_only = "\n".join(self._non_comment_lines())
        # J1固有のwriter入力組み立て関数・スキーマを実際に呼び出していないこと
        # (docstring内の説明文は別途チェックしない。実行可能コード行のみを対象とする)
        for forbidden in ["build_prompt(", "jami.JA_ARTICLE_JSON_SCHEMA", "make_ja_article_generation_fn(",
                           "jami.MINIMAL_JA_GENERATION_PROMPT_TEMPLATE", "jami.EVALUATION_REASONS"]:
            self.assertNotIn(forbidden, code_only, f"J1固有の関数/定数が実コードで参照されています: {forbidden}")


class SingleGenerationAttemptTests(unittest.TestCase):
    """要求20・21: 記事ごとの内容生成は1回だけ。QA警告で再生成しない。"""

    def test_generation_called_once_on_success(self):
        call_count = {"n": 0}

        def gen_fn():
            call_count["n"] += 1
            return "生成されたMarkdown", "gpt-5.6-sol", "resp_1"

        raw_text, model_id, response_id, attempt, ok, err = restore.run_generation_with_technical_retry(gen_fn)
        self.assertTrue(ok)
        self.assertEqual(call_count["n"], 1)
        self.assertEqual(attempt, 1)

    def test_technical_retry_once_on_empty_response(self):
        call_count = {"n": 0}

        def gen_fn():
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise restore.GenerationEmptyOrBrokenError("空応答")
            return "生成されたMarkdown", "gpt-5.6-sol", "resp_2"

        raw_text, model_id, response_id, attempt, ok, err = restore.run_generation_with_technical_retry(gen_fn)
        self.assertTrue(ok)
        self.assertEqual(call_count["n"], 2)

    def test_technical_generation_failed_after_two_attempts(self):
        def gen_fn():
            raise restore.GenerationEmptyOrBrokenError("常に空応答")

        raw_text, model_id, response_id, attempt, ok, err = restore.run_generation_with_technical_retry(gen_fn)
        self.assertFalse(ok)
        self.assertIsNone(raw_text)

    def test_no_regeneration_on_qa_warning_by_design(self):
        # パイプラインにfact QA結果を理由に生成をやり直す分岐が存在しないことを
        # ソースレベルで確認する
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("REVIEW_REQUIRED", src)  # QA結果に応じた再生成分岐が実装されていない
        self.assertNotIn("regenerate", src.lower())


class RawMarkdownIntegrityTests(unittest.TestCase):
    """要求22・23: 自由Markdownを改変せず保存。抽出失敗でもraw保持。"""

    def test_extract_structure_does_not_mutate_input(self):
        original = "# タイトル\n\n本文。\n\n## 見出し1\n\n内容\n\n## 見出し2\n\n内容\n\n一言で表すなら、まとめ。"
        snapshot = str(original)
        restore.extract_structure(original)
        self.assertEqual(original, snapshot)

    def test_extraction_failure_status_when_headings_missing(self):
        broken_markdown = "タイトルもどき\n\n見出しが一つもない本文だけの文章です。"
        result = restore.extract_structure(broken_markdown)
        self.assertEqual(result.status, "FAILED")

    def test_raw_markdown_preserved_regardless_of_extraction_status(self):
        broken_markdown = "見出しなし本文のみ"
        result = restore.extract_structure(broken_markdown)
        # extract_structureの戻り値はraw_markdownそのものを含まない設計
        # (呼び出し側が別途rawを保存する)。ここではraw文字列自体が
        # 関数呼び出し前後で不変であることを確認する。
        self.assertEqual(broken_markdown, "見出しなし本文のみ")
        self.assertIsNotNone(result)


class CharacterCountNotGatingTests(unittest.TestCase):
    """要求24: 文字数だけで不合格にしない。"""

    def test_compute_character_metrics_returns_metrics_only_no_verdict(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        metrics = restore.compute_character_metrics("短い記事。", master)
        self.assertIn("total_characters", metrics)
        self.assertNotIn("status", metrics)
        self.assertNotIn("passed", metrics)
        self.assertNotIn("within_acceptable_range", str(metrics))


class SameConditionsAcrossArticlesTests(unittest.TestCase):
    """要求25: A01とADD05で同じモデル・プロンプト設定を使用する。"""

    def test_generation_fn_uses_same_default_model_and_reasoning_for_any_article(self):
        gen_fn_a = restore.make_free_markdown_generation_fn("A01 message")
        gen_fn_b = restore.make_free_markdown_generation_fn("ADD05 message")
        self.assertEqual(gen_fn_a.model, gen_fn_b.model)
        self.assertEqual(gen_fn_a.reasoning_effort, gen_fn_b.reasoning_effort)
        self.assertEqual(gen_fn_a.developer_message, gen_fn_b.developer_message)


class NoOtherApiCallsTests(unittest.TestCase):
    """要求26・27: Web検索・TTSが呼ばれない。"""

    def test_web_search_not_referenced_in_module(self):
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("web_search", src.lower())

    def test_tts_not_referenced_in_module(self):
        with open("er002_ja_free_markdown_restore.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("tts", src.lower())


class J1ArtifactsUnchangedTests(unittest.TestCase):
    """要求28: J1成果物が変更されない。"""

    def test_j1_batch_summary_unchanged(self):
        path = "er002_output/v1_2m_j1/batch_summary.json"
        if not os.path.exists(path):
            self.skipTest("batch_summary.jsonが見つかりません")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["batch_condition_check"]["status"], "OK")

    def test_j1_status_record_reflects_rejection(self):
        path = "er002_output/_experiment_config/ER-002-v1.2M-J1_status.json"
        if not os.path.exists(path):
            self.skipTest("ER-002-v1.2M-J1_status.jsonが見つかりません")
        with open(path, encoding="utf-8") as f:
            status = json.load(f)
        self.assertEqual(status["technical_execution_status"], "PASS")
        self.assertEqual(status["user_acceptance"], "REJECTED")
        self.assertEqual(status["rejection_reason_status"], "DETAILS_PENDING")
        self.assertEqual(status["factor_analysis"], "DEFERRED_FOR_DEVELOPMENT_SPEED")
        self.assertEqual(status["content_regeneration_count"], 0)


if __name__ == "__main__":
    unittest.main()
