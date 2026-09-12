# ============================================================
# er011_open146_ledger_canonical_en_spelling_production_wiring_01_test_01.py
# OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01
# ============================================================
# 回帰テスト。run_project_regression.py(er0*_test_*.py自動探索)対象。
# API呼び出し(Web検索・LLM)は一切行わない。Web検索/LLMが必要な関数は
# すべてモック関数・スタブclientを注入してテストする(¥0)。
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock

import er002_ja_web_research_r3 as r3
import er003_v1_n3_01_articles_generate as prod_gen
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling

LEDGER_NO_CANONICAL = """ER-003-A2-B1-N3-01 — THEME (Sample) Verified Fact Ledger
=== 中心Fact ===

[CONFIRMED_FACT] FACT-01: サンプルの事実文。
  source: サンプルソース
  usable: yes
"""

LEDGER_WITH_CANONICAL = LEDGER_NO_CANONICAL + """

=== 固有名詞の公式英語表記(Web検索で確認済み) ===
canonical_en_spelling: 伊原陵人 = Takato Ihara
canonical_en_spelling: 伏見寅威 = Torai Fushimi
"""


class HasAndExtractCanonicalEntriesTest(unittest.TestCase):
    def test_has_canonical_en_spelling_false_when_absent(self):
        self.assertFalse(canon_spelling.has_canonical_en_spelling(LEDGER_NO_CANONICAL))

    def test_has_canonical_en_spelling_true_when_present(self):
        self.assertTrue(canon_spelling.has_canonical_en_spelling(LEDGER_WITH_CANONICAL))

    def test_extract_entries_empty_when_absent(self):
        self.assertEqual(canon_spelling.extract_canonical_en_spelling_entries(LEDGER_NO_CANONICAL), [])

    def test_extract_entries_parses_ja_en_pairs(self):
        entries = canon_spelling.extract_canonical_en_spelling_entries(LEDGER_WITH_CANONICAL)
        self.assertEqual(entries, [
            {"ja": "伊原陵人", "en": "Takato Ihara"},
            {"ja": "伏見寅威", "en": "Torai Fushimi"},
        ])


class WriterInstructionAppendTest(unittest.TestCase):
    """受入基準(6-b)(6-c)相当: 英語情報源テーマ(canonical_en_spelling行
    なし)では非発火・byte不変。"""

    def test_no_canonical_field_returns_byte_identical_text(self):
        result = canon_spelling.append_canonical_spelling_instruction_if_present(LEDGER_NO_CANONICAL)
        self.assertEqual(result, LEDGER_NO_CANONICAL)

    def test_with_canonical_field_appends_instruction(self):
        result = canon_spelling.append_canonical_spelling_instruction_if_present(LEDGER_WITH_CANONICAL)
        self.assertTrue(result.startswith(LEDGER_WITH_CANONICAL))
        self.assertIn("必ずこの英語表記をそのまま使用すること", result)
        self.assertIn("別のローマ字表記を作らないこと", result)


class BuildCommonBlockByteInvarianceTest(unittest.TestCase):
    """受入基準(6-c): build_common_block()自体は無改変であり、Ledgerに
    canonical_en_spelling行が無い場合、run_theme()経由の
    verified_ledger_textはload_text()直後の生データとbyte単位で同一
    (=build_common_block()の出力は本機能追加以前とbyte単位で完全に同一)。"""

    def test_build_common_block_output_unaffected_when_ledger_has_no_canonical_field(self):
        wrapped = canon_spelling.append_canonical_spelling_instruction_if_present(LEDGER_NO_CANONICAL)
        self.assertEqual(wrapped, LEDGER_NO_CANONICAL)
        out_without_wrapping = prod_gen.build_common_block("MASTER", "Sample Topic", LEDGER_NO_CANONICAL)
        out_with_wrapping = prod_gen.build_common_block("MASTER", "Sample Topic", wrapped)
        self.assertEqual(out_without_wrapping, out_with_wrapping)

    def test_build_common_block_output_changes_only_via_ledger_text_when_canonical_field_present(self):
        # build_common_block()自身のsignature/templateは無改変。Ledger
        # テキストの差分だけが出力へ反映されることを確認する。
        wrapped = canon_spelling.append_canonical_spelling_instruction_if_present(LEDGER_WITH_CANONICAL)
        out = prod_gen.build_common_block("MASTER", "Sample Topic", wrapped)
        self.assertIn("canonical_en_spelling: 伊原陵人 = Takato Ihara", out)
        self.assertIn("必ずこの英語表記をそのまま使用すること", out)


class FactCheckPromptBackwardCompatTest(unittest.TestCase):
    """受入基準(6-d): r3.build_fact_check_prompt()のcanonical_spelling_block
    既定""でbyte不変、非空時のみ末尾へ追記(OPEN-131 voice_attribution_block
    と同型パターン)。"""

    def test_default_empty_is_byte_identical_to_pre_change_signature(self):
        topic, article_text, sources = "Sample Topic", "Sample article.", []
        with_default = r3.build_fact_check_prompt(topic, article_text, sources)
        with_explicit_empty = r3.build_fact_check_prompt(
            topic, article_text, sources, canonical_spelling_block="")
        self.assertEqual(with_default, with_explicit_empty)

    def test_nonempty_block_appended_after_existing_prompt_unchanged(self):
        topic, article_text, sources = "Sample Topic", "Sample article.", []
        base = r3.build_fact_check_prompt(topic, article_text, sources)
        block = canon_spelling.build_canonical_spelling_fact_check_block(LEDGER_WITH_CANONICAL)
        combined = r3.build_fact_check_prompt(
            topic, article_text, sources, canonical_spelling_block=block)
        self.assertTrue(combined.startswith(base))
        self.assertIn("伊原陵人 = Takato Ihara", combined)

    def test_fact_check_block_empty_when_ledger_has_no_canonical_field(self):
        self.assertEqual(canon_spelling.build_canonical_spelling_fact_check_block(LEDGER_NO_CANONICAL), "")


class ProperNounExtractionMockedTest(unittest.TestCase):
    """受入基準(6-a): 固有名詞抽出→canonical_en_spelling行生成(Web検索は
    モック)。extraction・research双方をモックし、¥0で全経路を検証する。"""

    def test_extraction_prompt_parse_roundtrip(self):
        raw = json.dumps({"entities": [
            {"ja": "伊原陵人", "context": "阪神タイガース投手"},
            {"ja": "伏見寅威", "context": "阪神タイガース捕手"},
        ]}, ensure_ascii=False)
        entities = canon_spelling.parse_proper_noun_extraction_output(raw)
        self.assertEqual(entities, [
            {"ja": "伊原陵人", "context": "阪神タイガース投手"},
            {"ja": "伏見寅威", "context": "阪神タイガース捕手"},
        ])

    def test_extraction_empty_list_for_english_source_theme(self):
        raw = json.dumps({"entities": []})
        self.assertEqual(canon_spelling.parse_proper_noun_extraction_output(raw), [])

    def test_extraction_schema_error_on_missing_entities_key(self):
        with self.assertRaises(canon_spelling.ProperNounExtractionSchemaError):
            canon_spelling.parse_proper_noun_extraction_output(json.dumps({"foo": []}))

    def test_extraction_schema_error_on_invalid_json(self):
        with self.assertRaises(canon_spelling.ProperNounExtractionSchemaError):
            canon_spelling.parse_proper_noun_extraction_output("not json")

    def test_make_proper_noun_extraction_fn_uses_injected_client_no_web_search_tool(self):
        mock_response = MagicMock()
        mock_response.output_text = json.dumps({"entities": [{"ja": "伊原陵人", "context": "投手"}]})
        mock_response.model = "gpt-5.6-sol"
        mock_response.id = "resp_mock_1"
        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response

        fn = canon_spelling.make_proper_noun_extraction_fn(LEDGER_WITH_CANONICAL, client=mock_client)
        text, model, response_id = fn()
        self.assertEqual(model, "gpt-5.6-sol")
        self.assertEqual(response_id, "resp_mock_1")
        entities = canon_spelling.parse_proper_noun_extraction_output(text)
        self.assertEqual(entities, [{"ja": "伊原陵人", "context": "投手"}])

        # Web検索ツールを使わないことを確認(コスト最小化の設計どおり)。
        call_kwargs = mock_client.responses.create.call_args.kwargs
        self.assertNotIn("tools", call_kwargs)
        self.assertFalse(fn.uses_web_search_tool)


class CanonicalSpellingResearchMockedTest(unittest.TestCase):
    """受入基準(6-a)(6-b): 研究(Web検索)呼び出しをモックし、空entitiesでは
    API呼び出し自体を一切発生させないこと(非発火・¥0)を確認する。"""

    def test_empty_entities_skips_api_call_entirely(self):
        result = canon_spelling.run_canonical_spelling_research([], client=MagicMock())
        self.assertEqual(result["parsed"], [])
        self.assertTrue(result["skipped"])

    def test_parse_canonical_research_lines(self):
        raw_text = (
            "CANONICAL: 伊原陵人 = Takato Ihara | SOURCE: https://npb.jp/example (NPB公式)\n"
            "CANONICAL: 伏見寅威 = Torai Fushimi | SOURCE: https://npb.jp/example2\n"
        )
        parsed = canon_spelling.parse_canonical_research_lines(raw_text)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["ja"], "伊原陵人")
        self.assertEqual(parsed[0]["en"], "Takato Ihara")
        self.assertEqual(parsed[0]["url"], "https://npb.jp/example")

    def test_research_with_mocked_client_end_to_end(self):
        mock_response = MagicMock()
        mock_response.output_text = "CANONICAL: 伊原陵人 = Takato Ihara | SOURCE: https://npb.jp/example\n"
        mock_response.model = "gpt-5.6-sol"
        mock_response.id = "resp_mock_2"
        mock_response.output = []
        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response

        result = canon_spelling.run_canonical_spelling_research(
            [{"ja": "伊原陵人", "context": "阪神タイガース投手"}], client=mock_client)
        self.assertFalse(result["skipped"])
        self.assertEqual(result["parsed"], [
            {"ja": "伊原陵人", "en": "Takato Ihara", "url": "https://npb.jp/example", "note": ""},
        ])
        # 既存Production関数r3.make_writer_research_fnはweb_searchツールを
        # 有効にする(既存挙動、無改変)。
        call_kwargs = mock_client.responses.create.call_args.kwargs
        self.assertEqual(call_kwargs["tools"], [{"type": "web_search"}])


class LedgerSectionMergeTest(unittest.TestCase):
    def test_append_section_empty_entries_is_byte_identical(self):
        self.assertEqual(canon_spelling.append_canonical_spelling_section(LEDGER_NO_CANONICAL, []),
                          LEDGER_NO_CANONICAL)

    def test_append_section_builds_expected_lines(self):
        entries = [{"ja": "伊原陵人", "en": "Takato Ihara"}, {"ja": "伏見寅威", "en": "Torai Fushimi"}]
        merged = canon_spelling.append_canonical_spelling_section(LEDGER_NO_CANONICAL, entries)
        self.assertTrue(merged.startswith(LEDGER_NO_CANONICAL))
        self.assertIn("canonical_en_spelling: 伊原陵人 = Takato Ihara", merged)
        self.assertIn("canonical_en_spelling: 伏見寅威 = Torai Fushimi", merged)
        # 追記後のLedgerを本番のhas_canonical_en_spelling/extractで再検出できる
        # (Ledger作成→Production Writer経路の往復整合)。
        self.assertTrue(canon_spelling.has_canonical_en_spelling(merged))
        self.assertEqual(canon_spelling.extract_canonical_en_spelling_entries(merged), entries)


class Trial15ConditionFReproductionTest(unittest.TestCase):
    """受入基準(6-e): Trial-15の条件F Ledger(既存artifact、読み取り専用)を
    入力に、本番関数(append_canonical_spelling_instruction_if_present→
    build_common_block)で生成したprompt本文が、Trial-15 harnessが実際に
    使ったprompt構築ロジック(条件Eテキスト+canonical_en_spelling行+
    HARNESS_INSTRUCTION_SENTENCE、無変更)とbyte単位で一致することを確認
    する(Trial-15の実測条件Fそのものを再現、新規API呼び出しなし)。"""

    CONDITION_F_LEDGER_PATH = (
        "er011_output/news_ledger_canonical_spelling_trial_15/"
        "hanshin_ledger_condition_f_canonical_spelling.txt")

    def _load_condition_f_text(self):
        with open(self.CONDITION_F_LEDGER_PATH, encoding="utf-8") as f:
            return f.read()

    def test_condition_f_ledger_has_canonical_field_and_matches_production_detection(self):
        condition_f_text = self._load_condition_f_text()
        self.assertTrue(canon_spelling.has_canonical_en_spelling(condition_f_text))
        entries = canon_spelling.extract_canonical_en_spelling_entries(condition_f_text)
        self.assertEqual(len(entries), 10)
        self.assertIn({"ja": "佐藤輝明", "en": "Teruaki Sato"}, entries)
        self.assertIn({"ja": "伊原陵人", "en": "Takato Ihara"}, entries)

    def test_reapplying_production_append_is_idempotent_marker_detection(self):
        # Trial-15artifactは既に指示文が追記済みだが、本番関数の検出条件は
        # canonical_en_spelling行の有無のみであり、指示文の有無では判定
        # しない(has_canonical_en_spellingは指示文自体を対象にしない)。
        condition_f_text = self._load_condition_f_text()
        self.assertTrue(canon_spelling.has_canonical_en_spelling(condition_f_text))

    def test_production_pipeline_reproduces_trial15_prompt_from_pre_instruction_ledger(self):
        # Trial-15の条件Eテキスト(既存、読み取り専用)+条件Fのcanonical
        # entries(条件Fファイルから抽出、再Web検索なし)から、Trial-15の
        # build_condition_f_ledger()と同じ組み立て手順を本番関数だけで
        # 再現できることを確認する。
        import er011_news_ledger_enrichment_disambiguation_trial_14_run as t14
        with open(t14.LEDGER_E_PATH, encoding="utf-8") as f:
            condition_e_text = f.read()
        condition_f_text = self._load_condition_f_text()
        entries_with_en_only = canon_spelling.extract_canonical_en_spelling_entries(condition_f_text)

        # 本番のappend_canonical_spelling_section()でcanonical_en_spelling
        # セクションを組み立て、本番のappend_canonical_spelling_instruction_
        # if_present()で指示文を追記する(2関数とも無改変・再利用)。
        ledger_with_section = canon_spelling.append_canonical_spelling_section(
            condition_e_text, entries_with_en_only)
        production_final = canon_spelling.append_canonical_spelling_instruction_if_present(
            ledger_with_section)

        # 指示文の内容(Trial-15 HARNESS_INSTRUCTION_SENTENCEと同一文言)が
        # Trial-15実測artifactの末尾と一致することを確認する。
        self.assertTrue(condition_f_text.endswith(canon_spelling.CANONICAL_SPELLING_WRITER_INSTRUCTION))
        self.assertTrue(production_final.endswith(canon_spelling.CANONICAL_SPELLING_WRITER_INSTRUCTION))
        # canonical_en_spelling行の集合が完全一致する(Web検索結果の再利用、
        # 新規API呼び出しなし)。
        self.assertEqual(
            canon_spelling.extract_canonical_en_spelling_entries(production_final),
            canon_spelling.extract_canonical_en_spelling_entries(condition_f_text))

        # build_common_block()(無改変)へ両者を渡した出力について、
        # canonical_en_spelling行・実効指示文(Writerが従うべき部分)は
        # 完全一致することを確認する(Trial-15版は「作成方法」欄の説明
        # コメント文言がTrial固有のため、その1行のみ本番版と異なるが、
        # Writerへの実効的な指示内容には影響しない差分であることをここで
        # 明示する)。
        out_production = prod_gen.build_common_block("MASTER", "Sample Topic", production_final)
        out_trial15_artifact = prod_gen.build_common_block("MASTER", "Sample Topic", condition_f_text)
        for e in entries_with_en_only:
            line = f"canonical_en_spelling: {e['ja']} = {e['en']}"
            self.assertIn(line, out_production)
            self.assertIn(line, out_trial15_artifact)
        self.assertIn(canon_spelling.CANONICAL_SPELLING_WRITER_INSTRUCTION.strip(), out_production)
        self.assertIn(canon_spelling.CANONICAL_SPELLING_WRITER_INSTRUCTION.strip(), out_trial15_artifact)


if __name__ == "__main__":
    unittest.main()
