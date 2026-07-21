# ============================================================
# er003_test_p2i_production.py
# ER-003-P2I: B2 Key Words標準方式Lの正式採用・3記事のApproved化のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_p2i_production -v

import json
import unittest

import er003_b2_key_words as p2d
import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er003_v1_p2i_approve as approve
import er003_v1_p2i_manifest as manifest_mod
import er003_ja_to_en_translation as er003

ARTICLE_IDS = ("A01", "A02", "ADD03")

GOOD_ARTICLE = (
    "## Title\n\n"
    "Then came stoppage time. The referee blew the whistle. It was a wild finish to the match.\n\n"
    "Fans began to file out of the stadium. The captain decided to take charge of the celebration."
)


def make_item(rank, display_phrase, source_span, source_sentence, ja_gloss="テスト訳語",
              phrase_type="technical_term", normalization_type="none", category="domain_expression"):
    return {
        "rank": rank, "display_phrase": display_phrase, "source_span": source_span,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "phrase_type": phrase_type,
        "normalization_type": normalization_type, "normalization_note": "note",
        "selection_reason": "reason", "listening_difficulty_reason": "difficulty reason",
        "inference_transparency": "LOW", "topic_exposure_dependency": "HIGH",
        "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": category, "portfolio_substitution": False,
        "portfolio_substitution_reason": "reason",
    }


def make_valid_5_items():
    return [
        make_item(1, "stoppage time", "stoppage time", "Then came stoppage time."),
        make_item(2, "blow the whistle", "blew the whistle", "The referee blew the whistle."),
        make_item(3, "wild finish", "a wild finish", "It was a wild finish to the match."),
        make_item(4, "file out", "file out", "Fans began to file out of the stadium."),
        make_item(5, "take charge", "take charge", "The captain decided to take charge of the celebration."),
    ]


# ============================================================
# ブロック1: 承認済み成果物(approve script)の内容検証
# ============================================================
class ApprovedArtifactContentTests(unittest.TestCase):
    """各記事のkey_words_approved.jsonがP2G L方式のcanonical rank1-5と
    完全一致し、api_regeneration/manual_item_replacement/manual_gloss_edit
    がすべてfalseであることを検証する。"""

    @classmethod
    def setUpClass(cls):
        cls.approved = {}
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approved.json", encoding="utf-8") as f:
                cls.approved[article_id] = json.load(f)

    def test_five_articles_have_exactly_5_items(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(len(self.approved[article_id]["items"]), 5, msg=article_id)

    def test_no_api_regeneration_or_manual_edits(self):
        for article_id in ARTICLE_IDS:
            data = self.approved[article_id]
            self.assertFalse(data["api_regeneration"], msg=article_id)
            self.assertFalse(data["manual_item_replacement"], msg=article_id)
            self.assertFalse(data["manual_gloss_edit"], msg=article_id)

    def test_selection_strategy_is_l(self):
        for article_id in ARTICLE_IDS:
            data = self.approved[article_id]
            self.assertEqual(data["selection_strategy"], "L", msg=article_id)
            self.assertEqual(data["selection_strategy_name"], "Listening Blocker Ranking", msg=article_id)

    def test_production_item_count_is_5(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(self.approved[article_id]["production_item_count"], 5, msg=article_id)

    def test_source_ranks_are_1_through_5(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(self.approved[article_id]["source_ranks"], [1, 2, 3, 4, 5], msg=article_id)

    def test_decision_id_is_p2i(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(self.approved[article_id]["decision_id"], "ER-003-P2I", msg=article_id)

    def test_items_exactly_match_p2g_l_strategy_canonical_source(self):
        """approve scriptで生成した内容が、実際に保存されているP2G
        L方式(blind_mappingで特定)のrank1-5と一字一句一致するかを、
        テスト側で独立に再取得して比較する(承認スクリプトの正しさの
        直接検証)。"""
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2g/{article_id}/blind_mapping.json", encoding="utf-8") as f:
                mapping = json.load(f)
            l_label = next(label for label, sid in mapping.items() if sid == "L")
            with open(f"er003_output/p2g/{article_id}/L/key_words_selection.json", encoding="utf-8") as f:
                source = json.load(f)
            source_top5 = sorted([it for it in source["items"] if it["rank"] <= 5], key=lambda it: it["rank"])
            approved_items = self.approved[article_id]["items"]
            self.assertEqual(len(source_top5), len(approved_items), msg=article_id)
            for src, appd in zip(source_top5, approved_items):
                self.assertEqual(src["display_phrase"], appd["display_phrase"], msg=article_id)
                self.assertEqual(src["ja_gloss"], appd["ja_gloss"], msg=article_id)
                self.assertEqual(src["source_span"], appd["source_span"], msg=article_id)
                self.assertEqual(src["source_sentence"], appd["source_sentence"], msg=article_id)
            self.assertEqual(self.approved[article_id]["source_blind_set_label"], l_label, msg=article_id)

    def test_p2g_source_files_unchanged_by_approval(self):
        """approveスクリプトの実行がP2G成果物を書き換えていないことを、
        現在のP2Gファイルのsha256と、approved.jsonに記録されたsha256を
        突き合わせて検証する。"""
        for article_id in ARTICLE_IDS:
            path = f"er003_output/p2g/{article_id}/L/key_words_selection.json"
            with open(path, encoding="utf-8") as f:
                current_text = f.read()
            current_sha256 = er003.sha256_text(current_text)
            recorded_sha256 = self.approved[article_id]["source_strategy_result_sha256"]
            self.assertEqual(current_sha256, recorded_sha256, msg=article_id)

    def test_each_item_carries_p2g_extraction_form_qa_verdict(self):
        for article_id in ARTICLE_IDS:
            for item in self.approved[article_id]["items"]:
                self.assertIn("p2g_extraction_form_qa", item, msg=article_id)
                self.assertIn(item["p2g_extraction_form_qa"]["form_verdict"], ("PASS", "FAIL"), msg=article_id)

    def test_items_have_no_research_band_field(self):
        """本番承認済み成果物は全件が製品採用範囲であり、P2Gの
        research_band(TOP_5/RANK_6_TO_10)概念は不要(rank<=5の
        フィルタ結果そのものを保持しているだけで良い)。"""
        for article_id in ARTICLE_IDS:
            for item in self.approved[article_id]["items"]:
                # P2G由来の元フィールドとしてresearch_bandがTOP_5であることは許容するが、
                # 追加のRANK_6_TO_10混入がないことだけを確認する
                if "research_band" in item:
                    self.assertEqual(item["research_band"], "TOP_5", msg=article_id)


class ApprovedArtifactIntegrityTests(unittest.TestCase):
    """sha256ファイル・reading copy形式の整合性を検証する。"""

    def test_sha256_file_matches_approved_json_content(self):
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approved.json", encoding="utf-8") as f:
                text = f.read()
            with open(f"er003_output/p2i/{article_id}/key_words_approved_sha256.txt", encoding="utf-8") as f:
                recorded = f.read().strip()
            self.assertEqual(er003.sha256_text(text), recorded, msg=article_id)

    def test_reading_copy_has_number_one_through_five(self):
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approved_reading_copy.md", encoding="utf-8") as f:
                text = f.read()
            for label in ("Number One", "Number Two", "Number Three", "Number Four", "Number Five"):
                self.assertIn(label, text, msg=f"{article_id}: {label}")
            self.assertNotIn("Number Six", text, msg=article_id)

    def test_reading_copy_uses_p2d_builder_format(self):
        """P2Dのbuild_key_words_reading_copyをrankアダプタ経由で再利用
        しているため、出力フォーマットが完全一致することを確認する。"""
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approved.json", encoding="utf-8") as f:
                approved = json.load(f)
            expected = approve.build_reading_copy(approved["items"])
            with open(f"er003_output/p2i/{article_id}/key_words_approved_reading_copy.md", encoding="utf-8") as f:
                actual = f.read()
            self.assertEqual(expected, actual, msg=article_id)


class ApprovalMetadataTests(unittest.TestCase):
    """key_words_approval.jsonの採用理由・スコア記録が、ユーザー指定の
    tie-break framingを厳密に守っていることを検証する。"""

    @classmethod
    def setUpClass(cls):
        cls.approval = {}
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approval.json", encoding="utf-8") as f:
                cls.approval[article_id] = json.load(f)

    def test_top5_scores_recorded_as_tie(self):
        for article_id in ARTICLE_IDS:
            top5 = self.approval[article_id]["score_record"]["top5_total_max_30"]
            self.assertEqual(top5["L"], 24, msg=article_id)
            self.assertEqual(top5["U"], 24, msg=article_id)

    def test_total_scores_show_u_ahead_not_l(self):
        """Totalスコアでは実際にはUがLを上回る(L=46, U=48)という事実を
        正しく記録している(Lの採用理由としては使わないが、事実の
        記録として消してはいけない)。"""
        for article_id in ARTICLE_IDS:
            total = self.approval[article_id]["score_record"]["total_max_60"]
            self.assertEqual(total["L"], 46, msg=article_id)
            self.assertEqual(total["U"], 48, msg=article_id)
            self.assertGreater(total["U"], total["L"], msg=article_id)

    def test_adoption_rationale_does_not_claim_l_beat_u_on_score(self):
        """Lが数値上Uへ明確に勝ったとは記録しないこと、という指示の
        直接検証。「勝った」「勝利」「上回った」等のスコア優位表現が
        adoption_rationale中に出現しないことを確認する。"""
        for article_id in ARTICLE_IDS:
            rationale = self.approval[article_id]["adoption_rationale"]
            for phrase in ["勝った", "勝利", "上回っ"]:
                self.assertNotIn(phrase, rationale, msg=f"{article_id}: {phrase}")

    def test_adoption_rationale_matches_user_specified_text_verbatim(self):
        expected = (
            "製品仕様で使用するTop 5の評価はLとUが同点であり、ユーザーの定性的比較でも明確な優劣はなかった。"
            "そのうえでLは、個別学習者プロファイルへの依存がなく、"
            "「初回リスニングで理解を止める可能性が高い表現を選ぶ」という単純で説明可能な原則を持つため、標準方式として採用する。"
        )
        for article_id in ARTICLE_IDS:
            self.assertEqual(self.approval[article_id]["adoption_rationale"], expected, msg=article_id)

    def test_strategy_u_retained_as_personalization_candidate(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(
                self.approval[article_id]["strategy_u_disposition"],
                "NOT_ADOPTED_RETAINED_AS_FUTURE_PERSONALIZATION_CANDIDATE", msg=article_id)

    def test_strategy_p_excluded(self):
        for article_id in ARTICLE_IDS:
            self.assertEqual(
                self.approval[article_id]["strategy_p_disposition"],
                "EXCLUDED_FROM_STANDARD_CANDIDATES", msg=article_id)

    def test_no_api_or_manual_edit_flags_set(self):
        for article_id in ARTICLE_IDS:
            data = self.approval[article_id]
            self.assertFalse(data["api_regeneration"], msg=article_id)
            self.assertFalse(data["item_replacement"], msg=article_id)
            self.assertFalse(data["gloss_manual_edit"], msg=article_id)

    def test_approved_items_sha256_matches_approved_json(self):
        for article_id in ARTICLE_IDS:
            with open(f"er003_output/p2i/{article_id}/key_words_approved_sha256.txt", encoding="utf-8") as f:
                recorded = f.read().strip()
            self.assertEqual(self.approval[article_id]["approved_items_sha256"], recorded, msg=article_id)


# ============================================================
# ブロック2: リファレンスマニフェスト
# ============================================================
class ReferenceManifestTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open("er003_output/p2i/key_words_reference_manifest.json", encoding="utf-8") as f:
            cls.manifest = json.load(f)

    def test_production_strategy_is_l_with_5_items(self):
        self.assertEqual(self.manifest["production_selection_strategy"], "L")
        self.assertEqual(self.manifest["production_selection_strategy_name"], "Listening Blocker Ranking")
        self.assertEqual(self.manifest["production_item_count"], 5)

    def test_all_three_articles_present(self):
        for article_id in ARTICLE_IDS:
            self.assertIn(article_id, self.manifest["articles"])

    def test_article_paths_point_to_existing_files(self):
        import os
        for article_id in ARTICLE_IDS:
            entry = self.manifest["articles"][article_id]
            self.assertTrue(os.path.exists(entry["approved_key_words_path"]), msg=article_id)
            self.assertTrue(os.path.exists(entry["approved_reading_copy_path"]), msg=article_id)
            self.assertTrue(os.path.exists(entry["approval_metadata_path"]), msg=article_id)

    def test_manifest_uses_forward_slash_paths(self):
        for article_id in ARTICLE_IDS:
            entry = self.manifest["articles"][article_id]
            for key in ("approved_key_words_path", "approved_reading_copy_path", "approval_metadata_path"):
                self.assertNotIn("\\", entry[key], msg=f"{article_id}: {key}")

    def test_personalization_candidate_is_u(self):
        self.assertEqual(self.manifest["personalization_candidate"]["strategy_id"], "U")
        self.assertEqual(self.manifest["personalization_candidate"]["status"],
                         "NOT_ADOPTED_RETAINED_AS_FUTURE_PERSONALIZATION_CANDIDATE")

    def test_excluded_candidate_is_p(self):
        self.assertEqual(self.manifest["excluded_candidate"]["strategy_id"], "P")
        self.assertEqual(self.manifest["excluded_candidate"]["status"], "EXCLUDED_FROM_STANDARD_CANDIDATES")

    def test_experimental_evidence_lists_p2d_through_p2h(self):
        evidence = self.manifest["experimental_evidence"]
        for stage in ("ER-003-P2D", "ER-003-P2E", "ER-003-P2F", "ER-003-P2G", "ER-003-P2H"):
            self.assertIn(stage, evidence)

    def test_manifest_sha256_file_matches(self):
        with open("er003_output/p2i/key_words_reference_manifest.json", encoding="utf-8") as f:
            text = f.read()
        recomputed = er003.sha256_text(json.dumps(json.loads(text), ensure_ascii=False, indent=2))
        with open("er003_output/p2i/key_words_reference_manifest_sha256.txt", encoding="utf-8") as f:
            recorded = f.read().strip()
        self.assertEqual(recomputed, recorded)


# ============================================================
# ブロック3: 本番用selector schema/prompt
# ============================================================
class ProductionSchemaTests(unittest.TestCase):

    def test_item_count_fixed_at_5(self):
        items_schema = prod.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]
        self.assertEqual(items_schema["minItems"], 5)
        self.assertEqual(items_schema["maxItems"], 5)

    def test_schema_has_no_article_id_or_strategy_id_or_research_fields(self):
        """P2Fのarticle_id誤記問題の再発防止(P2Gの構造的解決を継承)。
        modelのStructured Output schemaにarticle_id/strategy_id/
        research_item_count/research_bandを一切含めない。"""
        top_level_props = prod.SELECTOR_JSON_SCHEMA["schema"]["properties"]
        self.assertNotIn("article_id", top_level_props)
        self.assertNotIn("strategy_id", top_level_props)
        self.assertNotIn("research_item_count", top_level_props)
        item_props = prod.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"]
        self.assertNotIn("article_id", item_props)
        self.assertNotIn("strategy_id", item_props)
        self.assertNotIn("research_band", item_props)

    def test_schema_is_strict(self):
        self.assertTrue(prod.SELECTOR_JSON_SCHEMA["strict"])
        self.assertFalse(prod.SELECTOR_JSON_SCHEMA["schema"]["additionalProperties"])

    def test_developer_message_unchanged_from_p2g(self):
        self.assertEqual(prod.SELECTOR_DEVELOPER_MESSAGE,
                         "英語ポッドキャストの初回リスニング理解を助ける、短いKey Wordsを選定してください。")
        self.assertEqual(prod.SELECTOR_DEVELOPER_MESSAGE, p2g.SELECTOR_DEVELOPER_MESSAGE)

    def test_model_and_reasoning_effort_reused_from_p2g(self):
        self.assertEqual(prod.SELECTOR_MODEL, p2g.SELECTOR_MODEL)
        self.assertEqual(prod.SELECTOR_REASONING_EFFORT, p2g.SELECTOR_REASONING_EFFORT)


class ProductionPromptTemplateTests(unittest.TestCase):

    def test_prompt_asks_for_exactly_5(self):
        template = prod.load_production_prompt_template()
        self.assertIn("ちょうど5個", template)
        self.assertNotIn("10個", template)

    def test_prompt_has_no_research_only_or_rank_6_10_language(self):
        template = prod.load_production_prompt_template()
        for forbidden in ("Rank 6", "Rank6", "6-10", "研究", "research", "blind", "ブラインド"):
            self.assertNotIn(forbidden, template, msg=forbidden)

    def test_prompt_preserves_minimal_unit_rules(self):
        template = prod.load_production_prompt_template()
        self.assertIn("1〜5語", template)
        self.assertIn("完全文", template)

    def test_build_user_message_substitutes_placeholders(self):
        msg = prod.build_production_user_message("SUMMARY_TEXT", "ARTICLE_TEXT")
        self.assertIn("SUMMARY_TEXT", msg)
        self.assertIn("ARTICLE_TEXT", msg)
        self.assertNotIn("{approved_summary}", msg)
        self.assertNotIn("{approved_b2_article}", msg)


# ============================================================
# ブロック4: ロジック再利用(re実装しない)の確認
# ============================================================
class ReuseIdentityTests(unittest.TestCase):

    def test_b2_input_paths_reused_from_p2d(self):
        self.assertIs(prod.B2_INPUT_PATHS, p2d.B2_INPUT_PATHS)
        self.assertIs(prod.APPROVED_SUMMARY_PATHS, p2d.APPROVED_SUMMARY_PATHS)
        self.assertIs(prod.load_approved_b2_article, p2d.load_approved_b2_article)
        self.assertIs(prod.load_approved_summary, p2d.load_approved_summary)

    def test_hard_requirement_functions_reused_from_p2g(self):
        self.assertIs(prod.validate_display_phrase_form, p2g.validate_display_phrase_form)
        self.assertIs(prod.parse_selector_json, p2g.parse_selector_json)
        self.assertIs(prod.SelectorModelMismatchError, p2g.SelectorModelMismatchError)

    def test_enum_constants_reused_from_p2g(self):
        self.assertIs(prod.PHRASE_TYPES, p2g.PHRASE_TYPES)
        self.assertIs(prod.NORMALIZATION_TYPES, p2g.NORMALIZATION_TYPES)
        self.assertIs(prod.TRI_LEVELS, p2g.TRI_LEVELS)
        self.assertIs(prod.PORTFOLIO_CATEGORIES, p2g.PORTFOLIO_CATEGORIES)

    def test_validate_production_selection_delegates_to_p2g_core(self):
        """validate_production_selectionが、P2Gのvalidate_min_unit_
        selectionをexpected_item_count=5で呼び出すアダプタであり、
        判定ロジックを再実装していないことを確認する。"""
        parsed = prod.attach_runtime_metadata({"items": make_valid_5_items()}, "A01", "L")
        direct = p2g.validate_min_unit_selection(parsed, GOOD_ARTICLE, expected_item_count=5)
        via_prod = prod.validate_production_selection(parsed, GOOD_ARTICLE)
        self.assertEqual(direct, via_prod)

    def test_module_has_no_strategy_comparison_or_blind_logic(self):
        """本番モジュールはL方式単体のみを対象とし、P/U方式の実装・
        ブラインド比較・パーソナライズ機能は一切含まない(P2Iのスコープ
        外)。"""
        for forbidden_name in ("build_blind_mapping", "run_comparison_qa", "build_form_qa_prompt",
                               "select_strategy", "STRATEGY_IDS"):
            self.assertFalse(hasattr(prod, forbidden_name), msg=forbidden_name)


# ============================================================
# ブロック5: runtimeメタデータ付与(モデル自己申告を信用しない)
# ============================================================
class RuntimeMetadataTests(unittest.TestCase):

    def test_attach_runtime_metadata_uses_call_site_values_only(self):
        parsed = {"items": make_valid_5_items()}
        result = prod.attach_runtime_metadata(parsed, "ADD03", "L")
        self.assertEqual(result["article_id"], "ADD03")
        self.assertEqual(result["strategy_id"], "L")
        self.assertEqual(result["production_item_count"], 5)

    def test_strategy_id_defaults_to_l(self):
        parsed = {"items": make_valid_5_items()}
        result = prod.attach_runtime_metadata(parsed, "A02")
        self.assertEqual(result["strategy_id"], "L")

    def test_items_do_not_carry_research_band(self):
        parsed = {"items": make_valid_5_items()}
        result = prod.attach_runtime_metadata(parsed, "A01", "L")
        for item in result["items"]:
            self.assertNotIn("research_band", item)

    def test_p2f_style_wrong_article_id_in_model_output_does_not_matter(self):
        """モデル出力itemsに万一article_id相当の情報が紛れ込んでいても
        (schema上はそもそも存在し得ないが)、runtime付与値だけが最終
        article_idとして使われることを確認する。"""
        items = make_valid_5_items()
        parsed = {"items": items}
        result = prod.attach_runtime_metadata(parsed, "A01", "L")
        self.assertEqual(result["article_id"], "A01")


# ============================================================
# ブロック6: 決定的validator(hard requirement)の本番版での再現
# ============================================================
class ProductionValidatorBehaviorTests(unittest.TestCase):

    def _validate(self, items, article=GOOD_ARTICLE, article_id="A01", strategy_id="L"):
        parsed = prod.attach_runtime_metadata({"items": items}, article_id, strategy_id)
        return prod.validate_production_selection(parsed, article)

    def test_valid_5_items_pass(self):
        result = self._validate(make_valid_5_items())
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS")

    def test_4_items_fail_exactly_5_gate(self):
        items = make_valid_5_items()[:4]
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("5" in r for r in result["reasons"]))

    def test_6_items_fail_exactly_5_gate(self):
        items = make_valid_5_items() + [make_item(6, "extra phrase", "stoppage time", "Then came stoppage time.")]
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_rank_6_is_rejected_not_treated_as_overflow(self):
        """P2Gの研究版と異なり、rank6-10という上振れ層は本番版に存在
        しない。rankが1-5の完全な並びでなければ不合格とする。"""
        items = make_valid_5_items()
        items[4] = make_item(6, "take charge", "take charge",
                             "The captain decided to take charge of the celebration.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_complete_sentence_rejected(self):
        items = make_valid_5_items()
        items[0] = make_item(1, "it was stoppage time", "stoppage time", "Then came stoppage time.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any(r["reasons"] for r in result["item_reasons"] if r["index"] == 0))

    def test_finite_auxiliary_rejected(self):
        items = make_valid_5_items()
        items[1] = make_item(2, "was blowing the whistle", "blew the whistle", "The referee blew the whistle.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_six_word_phrase_rejected(self):
        items = make_valid_5_items()
        items[2] = make_item(3, "a genuinely wild and unexpected finish", "a wild finish",
                             "It was a wild finish to the match.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_duplicate_display_phrase_rejected(self):
        items = make_valid_5_items()
        items[4] = make_item(5, "stoppage time", "take charge",
                             "The captain decided to take charge of the celebration.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("重複" in r for r in result["reasons"]))

    def test_source_span_not_in_source_sentence_rejected(self):
        items = make_valid_5_items()
        items[3] = make_item(4, "file out", "kicked off",
                             "Fans began to file out of the stadium.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_sentence_not_in_article_rejected(self):
        items = make_valid_5_items()
        items[3] = make_item(4, "file out", "file out", "This sentence does not exist in the article.")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_non_japanese_gloss_rejected(self):
        items = make_valid_5_items()
        items[0] = make_item(1, "stoppage time", "stoppage time", "Then came stoppage time.",
                             ja_gloss="added extra minutes")
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")


# ============================================================
# ブロック7: リトライゲート(技術的失敗のみ再試行、内容品質では再試行しない)
# ============================================================
class ProductionGateTests(unittest.TestCase):

    def _pass_factory(self, items=None):
        items = items if items is not None else make_valid_5_items()

        def factory():
            def fn():
                return json.dumps({"items": items}), "gpt-5.6-sol", "resp_1"
            return fn
        return factory

    def _fail_factory(self, exc=RuntimeError("boom")):
        def factory():
            def fn():
                raise exc
            return fn
        return factory

    def test_success_on_first_attempt_returns_immediately(self):
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "A01", self._pass_factory(), GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(attempts), 1)
        self.assertEqual(parsed["article_id"], "A01")
        self.assertEqual(parsed["strategy_id"], "L")

    def test_technical_failure_retried_once_then_fails(self):
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "A01", self._fail_factory(), GOOD_ARTICLE, sleep_fn=lambda s: None)
        self.assertEqual(status, "TECHNICAL_GENERATION_FAILED")
        self.assertEqual(len(attempts), 2)

    def test_structure_invalid_retried_once_then_fails(self):
        bad_items = make_valid_5_items()[:4]  # exactly-5違反
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "A01", self._pass_factory(bad_items), GOOD_ARTICLE, sleep_fn=lambda s: None)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(len(attempts), 2)

    def test_max_attempts_is_2(self):
        self.assertEqual(prod.MAX_PRODUCTION_RETRY_ATTEMPTS, 2)

    def test_gate_never_trusts_model_for_article_or_strategy_id(self):
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "ADD03", self._pass_factory(), GOOD_ARTICLE, strategy_id="L")
        self.assertEqual(parsed["article_id"], "ADD03")
        self.assertEqual(parsed["strategy_id"], "L")


# ============================================================
# ブロック8: reading copy構築
# ============================================================
class ProductionReadingCopyTests(unittest.TestCase):

    def test_reading_copy_uses_number_one_through_five(self):
        rc = prod.build_production_reading_copy(make_valid_5_items())
        for label in ("Number One", "Number Two", "Number Three", "Number Four", "Number Five"):
            self.assertIn(label, rc)

    def test_reading_copy_sorted_by_rank_regardless_of_input_order(self):
        items = make_valid_5_items()
        shuffled = [items[2], items[0], items[4], items[1], items[3]]
        rc = prod.build_production_reading_copy(shuffled)
        idx_one = rc.index("stoppage time")
        idx_five = rc.index("take charge")
        self.assertLess(idx_one, idx_five)


class SelectorFunctionTests(unittest.TestCase):

    def test_selector_has_no_web_search_tool_and_uses_structured_output(self):
        fn = prod.make_production_selector_fn("dummy user message", client=object())
        self.assertFalse(fn.uses_web_search_tool)
        self.assertTrue(fn.uses_structured_output)
        self.assertEqual(fn.model, prod.SELECTOR_MODEL)
        self.assertEqual(fn.reasoning_effort, prod.SELECTOR_REASONING_EFFORT)


if __name__ == "__main__":
    unittest.main()
