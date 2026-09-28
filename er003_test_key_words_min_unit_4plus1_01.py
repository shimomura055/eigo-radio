# ============================================================
# er003_test_key_words_min_unit_4plus1_01.py
# KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01: Phase B最小実装のテスト
# ============================================================
# 修正1回目(Opus L2所見S3、2026-09-28): 既存命名規約
# `er0NNN_test_*.py`(件数照合meta-test`er003_test_p2j_investigate.py`の
# combined/prefix両patternに一致)へrename(旧
# `er003_key_words_min_unit_4plus1_test_01.py`)。回帰regression収集自体は
# rename前後どちらの名前でも`run_project_regression.py`のdefault pattern
# に一致するが、meta-testの件数不変条件(prefix別合計=combined合計)は
# renameしないと崩れる(詳細REPORT §8参照)。
#
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ
# (Wiktionary API等の既存Stage1決定論処理も呼ばない、純粋なschema/
# validator/canonicalization/prompt-templateユニットテスト)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_key_words_min_unit_4plus1_01 -v
#
# カバー範囲(委任文の指定7項目):
#   1. schema伝播(Strategy L/DB Hybrid両経路)
#   2. validator 4+1 PASS/FAIL
#   3. B2 10件研究版ガード(4+1集計検証の対象外)
#   4. canonicalization passthrough(新規フィールド+旧artifact後方互換)
#   5. DB Hybrid reason_code合流(白箱: 既存INVALID分岐と同一のまま
#      detail_reason_codeタグのみ追加されることをsource inspectionで確認)
#   6. 旧artifact後方互換(canonicalization passthroughの一部として実施)
#   7. Strategy L structure invalid→retry合流(既存run_production_
#      selection_gateのretryループがrole構成不成立でも同じ経路で動くこと)

import inspect
import json
import tempfile
import unittest
from unittest.mock import patch

import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er003_v1_n3_01_scaffold_generate as sc
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref_contract

GOOD_ARTICLE = (
    "## Title\n\n"
    "Then came stoppage time. The referee blew the whistle. It was a wild finish to the match.\n\n"
    "Fans began to file out of the stadium. The captain decided to take charge of the celebration."
)


def make_item(rank, display_phrase, source_span, source_sentence, key_phrase_role="important",
              ja_gloss="テスト訳語", phrase_type="technical_term", category="domain_expression"):
    return {
        "rank": rank, "display_phrase": display_phrase, "source_span": source_span,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "phrase_type": phrase_type,
        "normalization_type": "none", "normalization_note": "note",
        "selection_reason": "reason", "listening_difficulty_reason": "difficulty reason",
        "inference_transparency": "LOW", "topic_exposure_dependency": "HIGH",
        "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": category, "portfolio_substitution": False,
        "portfolio_substitution_reason": "reason",
        "key_phrase_role": key_phrase_role,
    }


def make_valid_4plus1_items():
    return [
        make_item(1, "stoppage time", "stoppage time", "Then came stoppage time."),
        make_item(2, "blow the whistle", "blew the whistle", "The referee blew the whistle."),
        make_item(3, "wild finish", "a wild finish", "It was a wild finish to the match.",
                  key_phrase_role="topic"),
        make_item(4, "file out", "file out", "Fans began to file out of the stadium."),
        make_item(5, "take charge", "take charge", "The captain decided to take charge of the celebration."),
    ]


def make_items_10_research(role="important"):
    sentences = [
        "Gordon met it, and England took the lead.",
        "This was a huge moment for the team.",
        "The plan was withdrawn the next day, surprising everyone.",
        "Ships passed through the strait without incident.",
        "The weather stayed calm all day.",
        "Fans cheered loudly as the final whistle blew.",
        "Analysts debated the tactics for hours.",
        "The coach praised the team spirit.",
        "Injuries had tested their depth all season.",
        "A new stadium will host the next match.",
    ]
    article = "## Title\n\n" + "\n\n".join(sentences)
    items = [
        make_item(i + 1, f"phrase {i}", " ".join(sentences[i].split()[:2]), sentences[i], key_phrase_role=role)
        for i in range(10)
    ]
    return article, items


def _good_qa():
    return {field: "PASS" for field in kc.QA_FIELDS}


def _build_full_canon_item(rank):
    return {
        "rank": rank, "key_phrase": "digital twin", "changed_from_display_phrase": False,
        "normalization_reason": "", "reasoning": "ok", **_good_qa(),
    }


# ============================================================
# 1. schema伝播(Strategy L/DB Hybrid両経路)
# ============================================================
class SchemaPropagationTests(unittest.TestCase):

    def test_key_phrase_role_in_p2g_item_schema_properties(self):
        self.assertIn("key_phrase_role", p2g._ITEM_SCHEMA_PROPERTIES)
        self.assertEqual(
            p2g._ITEM_SCHEMA_PROPERTIES["key_phrase_role"]["enum"], ["important", "topic"])

    def test_key_phrase_role_is_required(self):
        self.assertIn("key_phrase_role", p2g._ITEM_REQUIRED_FIELDS)

    def test_strategy_l_production_schema_shares_same_object(self):
        # er003_key_words_production._ITEM_SCHEMA_PROPERTIES = p2g._ITEM_SCHEMA_PROPERTIES
        # (同一オブジェクト参照)のため、1箇所の追加が自動的に伝播する。
        self.assertIs(prod._ITEM_SCHEMA_PROPERTIES, p2g._ITEM_SCHEMA_PROPERTIES)
        self.assertIn("key_phrase_role", prod.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]["items"]
                      ["properties"])

    def test_db_hybrid_schema_includes_key_phrase_role(self):
        props = src_ref_contract.build_item_schema_properties(["C1", "C2", "C3"])
        self.assertIn("key_phrase_role", props)
        self.assertEqual(props["key_phrase_role"]["enum"], ["important", "topic"])
        required = src_ref_contract.build_item_required_fields()
        self.assertIn("key_phrase_role", required)

    def test_prompt_template_contains_topic_guidance_without_hardcoded_examples(self):
        # 実際に使われる唯一の共有ファイルはb1_p2_keywords_l_prompt_
        # template.txt(bk.load_prompt_template、Strategy L B1/DB Hybrid
        # 両経路が参照)。er003_key_words_production.load_production_
        # prompt_template()が読むb2_key_words_production_l_prompt_
        # template.txtは、Family X/Z本番runnerからは使われない別の
        # (P2I初期3記事パイロット向け)テンプレートであり対象外。
        template = bk.load_prompt_template()
        self.assertIn("key_phrase_role", template)
        self.assertIn("topic", template)
        self.assertIn("important", template)
        # ユーザー明示指示: 固有名詞枠ではない・例示hard-code禁止。
        for forbidden in ("人名・企業名・ブランド名・地名だから選ぶ",):
            self.assertIn(forbidden, template)  # 「優先しない」という否定文言の一部として存在すること
        self.assertNotIn("例えば", template)


# ============================================================
# 2. validator 4+1 PASS/FAIL
# ============================================================
class FourPlusOneValidatorTests(unittest.TestCase):

    def _validate(self, items):
        parsed = prod.attach_runtime_metadata({"items": items}, "A01", "L")
        return prod.validate_production_selection(parsed, GOOD_ARTICLE)

    def test_valid_4_important_1_topic_passes(self):
        result = self._validate(make_valid_4plus1_items())
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_zero_topic_fails(self):
        items = make_valid_4plus1_items()
        items[2] = {**items[2], "key_phrase_role": "important"}
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("key_phrase_role" in r for r in result["reasons"]), msg=result["reasons"])

    def test_two_topic_fails(self):
        items = make_valid_4plus1_items()
        items[0] = {**items[0], "key_phrase_role": "topic"}
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("key_phrase_role" in r for r in result["reasons"]), msg=result["reasons"])

    def test_invalid_enum_value_fails_per_item(self):
        items = make_valid_4plus1_items()
        items[0] = {**items[0], "key_phrase_role": "proper_noun"}  # ユーザーが禁止する固有名詞枠のような値
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        item0_reasons = next(r["reasons"] for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("key_phrase_role" in r for r in item0_reasons), msg=item0_reasons)

    def test_missing_key_phrase_role_field_fails_as_missing_required_field(self):
        items = make_valid_4plus1_items()
        del items[0]["key_phrase_role"]
        result = self._validate(items)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")


# ============================================================
# 3. B2 10件研究版ガード(4+1集計検証の対象外)
# ============================================================
class ResearchTenItemGuardTests(unittest.TestCase):

    def test_ten_item_all_important_passes_aggregate_guard_skipped(self):
        article, items = make_items_10_research(role="important")
        parsed = p2g.attach_runtime_metadata({"items": items}, "A02", "L")
        result = p2g.validate_min_unit_selection(parsed, article)  # expected_item_count既定=10
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_ten_item_still_requires_valid_enum_value_per_item(self):
        article, items = make_items_10_research(role="important")
        items[0]["key_phrase_role"] = "not_a_valid_role"
        parsed = p2g.attach_runtime_metadata({"items": items}, "A02", "L")
        result = p2g.validate_min_unit_selection(parsed, article)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_expected_item_count_5_still_enforces_aggregate_even_if_called_directly(self):
        # ガードはexpected_item_count==PRODUCTION_ITEM_COUNT_UNCHANGED(5)の
        # 場合のみ有効であり、10件呼び出しでは絶対に評価されないことの
        # 直接確認(逆に5件を明示指定すれば10件データでも集計評価される)。
        article, items = make_items_10_research(role="important")
        parsed = p2g.attach_runtime_metadata({"items": items[:5]}, "A02", "L")
        result = p2g.validate_min_unit_selection(parsed, article, expected_item_count=5)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("key_phrase_role" in r for r in result["reasons"]), msg=result["reasons"])


# ============================================================
# 4/6. canonicalization passthrough + 旧artifact後方互換
# ============================================================
class CanonicalizationPassthroughTests(unittest.TestCase):

    def test_key_phrase_role_passed_through_when_present(self):
        original = [{
            "rank": 1, "source_span": "digital twin", "source_sentence": "Her digital twin appeared.",
            "display_phrase": "digital twin", "ja_gloss": "デジタルツイン", "key_phrase_role": "topic",
        }]
        canon_items = [_build_full_canon_item(1)]
        merged = kc.merge_canonicalization_result(original, canon_items)
        self.assertEqual(merged["items"][0]["key_phrase_role"], "topic")

    def test_legacy_items_without_key_phrase_role_unaffected(self):
        """旧artifact(key_phrase_role欠落)は旧contractとして扱われ、
        KeyError等を発生させずmergeでき、merged itemにもフィールドが
        存在しない(後方互換)。"""
        original = [{
            "rank": 1, "source_span": "digital twin", "source_sentence": "Her digital twin appeared.",
            "display_phrase": "digital twin", "ja_gloss": "デジタルツイン",
        }]
        canon_items = [_build_full_canon_item(1)]
        merged = kc.merge_canonicalization_result(original, canon_items)
        self.assertNotIn("key_phrase_role", merged["items"][0])


# ============================================================
# 5. DB Hybrid reason_code合流(白箱: 既存INVALID分岐と同一のまま
#    detail_reason_codeタグのみ追加。新しい分岐点を作っていないことの
#    source inspectionによる確認)。
# ============================================================
class DbHybridReasonCodeMergeTests(unittest.TestCase):

    def test_validator_failure_message_contains_grep_target_substring(self):
        """detail_reason_code判定は`"key_phrase_role" in r`という文字列
        マッチに依存するため、その前提(validatorの実際のreason文言に
        'key_phrase_role'という部分文字列が含まれること)を直接確認する。"""
        items = make_valid_4plus1_items()
        items[2] = {**items[2], "key_phrase_role": "important"}  # topic=0にして不成立にする
        parsed = prod.attach_runtime_metadata({"items": items}, "A01", "L")
        result = prod.validate_production_selection(parsed, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("key_phrase_role" in r for r in result["reasons"]))

    def test_raise_site_still_uses_status_as_reason_code_no_new_branch(self):
        """run_db_hybrid_selectionのINVALID分岐がstatus(既存
        KEY_WORDS_STRUCTURE_INVALID)をそのままDbHybridFailureの
        reason_codeとして使い続けており(新しい分岐点を作っていない)、
        telemetry識別用のdetail_reason_codeキーのみが追加されている
        ことをsource inspectionで確認する。"""
        src = inspect.getsource(db_hybrid.run_db_hybrid_selection)
        self.assertIn('raise DbHybridFailure(\n            status,', src)
        self.assertIn("detail_reason_code", src)
        self.assertIn('"ROLE_STRUCTURE_INVALID" if role_structure_invalid else None', src)

    def test_db_hybrid_failure_default_fallback_allowed_still_true_for_structure_invalid(self):
        """KEY_WORDS_STRUCTURE_INVALID経路はfallback_allowedの既定値
        (True)を明示的に上書きしていない(=既存のfallback可能な分岐に
        そのまま合流する)ことを確認する。"""
        exc = db_hybrid.DbHybridFailure("KEY_WORDS_STRUCTURE_INVALID", "msg",
                                         telemetry={"reason_code": "KEY_WORDS_STRUCTURE_INVALID",
                                                    "detail_reason_code": "ROLE_STRUCTURE_INVALID"})
        self.assertTrue(exc.fallback_allowed)
        self.assertEqual(exc.reason_code, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(exc.telemetry["detail_reason_code"], "ROLE_STRUCTURE_INVALID")


# ============================================================
# 7. Strategy L structure invalid→retry合流
# ============================================================
class StrategyLRetryOnRoleInvalidTests(unittest.TestCase):

    def _pass_factory(self, items):
        def factory():
            def fn():
                return json.dumps({"items": items}), "gpt-5.6-sol", "resp_1"
            return fn
        return factory

    def test_role_structure_invalid_retried_once_then_fails_same_as_other_structure_invalid(self):
        zero_topic_items = make_valid_4plus1_items()
        zero_topic_items[2] = {**zero_topic_items[2], "key_phrase_role": "important"}
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "A01", self._pass_factory(zero_topic_items), GOOD_ARTICLE, sleep_fn=lambda s: None)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(len(attempts), prod.MAX_PRODUCTION_RETRY_ATTEMPTS)
        for a in attempts:
            self.assertEqual(a["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_valid_4plus1_passes_gate_on_first_attempt(self):
        parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
            "A01", self._pass_factory(make_valid_4plus1_items()), GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(attempts), 1)


# ============================================================
# 8. Strategy L retry最大2回+2回目到達時の報告記録(修正1回目、
#    ユーザー既決事項、2026-09-28)
# ============================================================
def make_db_hybrid_item(rank, display_phrase, candidate_id, surface_echo=None,
                         key_phrase_role="important", ja_gloss="テスト訳語"):
    return {
        "rank": rank, "display_phrase": display_phrase, "source_candidate_id": candidate_id,
        "surface_echo": surface_echo if surface_echo is not None else display_phrase,
        "ja_gloss": ja_gloss, "phrase_type": "technical_term", "normalization_type": "none",
        "normalization_note": "note", "selection_reason": "reason",
        "listening_difficulty_reason": "difficulty reason", "inference_transparency": "LOW",
        "topic_exposure_dependency": "HIGH", "comprehension_impact": "HIGH",
        "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": "domain_expression", "portfolio_substitution": False,
        "portfolio_substitution_reason": "reason", "key_phrase_role": key_phrase_role,
    }


class StrategyLRetryReachedSecondAttemptReportingTests(unittest.TestCase):
    """`bk.make_selector_fn`をmockし(実API呼び出しなし)、Strategy L経路の
    max_attempts=1固定(修正前の既存挙動)がProduction既定
    MAX_PRODUCTION_RETRY_ATTEMPTS(=2)へ揃ったこと、2回目到達時に
    `strategy_l_attempts`/`retry_reached_second_attempt`が
    runtime_metadata.jsonへ記録されることを確認する。"""

    def test_retry_reaches_second_attempt_and_passes_records_report_fields(self):
        call_count = {"n": 0}
        zero_topic_items = make_valid_4plus1_items()
        zero_topic_items[2] = {**zero_topic_items[2], "key_phrase_role": "important"}
        valid_items = make_valid_4plus1_items()

        def fake_make_selector_fn(user_message, **kwargs):
            call_count["n"] += 1

            def fn():
                items = zero_topic_items if call_count["n"] == 1 else valid_items
                return json.dumps({"items": items}), "gpt-5.6-sol", f"resp_{call_count['n']}"
            return fn

        with patch.object(bk, "make_selector_fn", side_effect=fake_make_selector_fn):
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = sc._run_key_phrase_selection_strategy_l(GOOD_ARTICLE, tmp_dir, "A01", "L")
                with open(f"{tmp_dir}/keywords_runtime_metadata.json", encoding="utf-8") as f:
                    runtime_metadata = json.load(f)

        self.assertEqual(call_count["n"], 2)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)
        self.assertEqual(result["strategy_l_attempts"], 2)
        self.assertTrue(result["retry_reached_second_attempt"])
        self.assertEqual(runtime_metadata["strategy_l_attempts"], 2)
        self.assertTrue(runtime_metadata["retry_reached_second_attempt"])

    def test_single_attempt_pass_does_not_report_second_attempt(self):
        def fake_make_selector_fn(user_message, **kwargs):
            def fn():
                return json.dumps({"items": make_valid_4plus1_items()}), "gpt-5.6-sol", "resp_1"
            return fn

        with patch.object(bk, "make_selector_fn", side_effect=fake_make_selector_fn):
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = sc._run_key_phrase_selection_strategy_l(GOOD_ARTICLE, tmp_dir, "A01", "L")

        self.assertEqual(result["strategy_l_attempts"], 1)
        self.assertFalse(result["retry_reached_second_attempt"])


# ============================================================
# 9. Opus L2所見S1: Strategy L経路のtelemetry観測性(INVALID時も
#    role_countsが失われないこと)
# ============================================================
class StrategyLRoleCountsObservabilityTests(unittest.TestCase):

    def test_role_counts_present_even_when_final_status_invalid(self):
        zero_topic_items = make_valid_4plus1_items()
        zero_topic_items[2] = {**zero_topic_items[2], "key_phrase_role": "important"}

        def fake_make_selector_fn(user_message, **kwargs):
            def fn():
                return json.dumps({"items": zero_topic_items}), "gpt-5.6-sol", "resp_1"
            return fn

        with patch.object(bk, "make_selector_fn", side_effect=fake_make_selector_fn):
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = sc._run_key_phrase_selection_strategy_l(GOOD_ARTICLE, tmp_dir, "A01", "L")

        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertIsNotNone(result.get("role_counts"))
        self.assertEqual(result["role_counts"], {"important": 5})


# ============================================================
# 10. DB Hybrid backup_item補完(修正1回目、ユーザー既決事項、2026-09-28):
#     topicが欠損/単独無効な場合のみ、backup_item(important役割の予備
#     候補)で機械的に置換する。曖昧・backup自体が使えないケースは
#     既存のINVALID経路へそのまま委ねる。
# ============================================================
def _db_hybrid_id_to_candidate():
    return {
        "C1": {"candidate_id": "C1", "surface_form": "stoppage time", "context_sentence_id": "s1"},
        "C2": {"candidate_id": "C2", "surface_form": "blew the whistle", "context_sentence_id": "s2"},
        "C3": {"candidate_id": "C3", "surface_form": "wild finish", "context_sentence_id": "s3"},
        "C4": {"candidate_id": "C4", "surface_form": "file out", "context_sentence_id": "s4"},
        "C5": {"candidate_id": "C5", "surface_form": "take charge", "context_sentence_id": "s5"},
        "C6": {"candidate_id": "C6", "surface_form": "the celebration", "context_sentence_id": "s5"},
    }


def _db_hybrid_sentence_reference():
    return {
        "s1": "Then came stoppage time.",
        "s2": "The referee blew the whistle.",
        "s3": "It was a wild finish to the match.",
        "s4": "Fans began to file out of the stadium.",
        "s5": "The captain decided to take charge of the celebration.",
    }


class DbHybridBackupSubstitutionTests(unittest.TestCase):

    def _factory(self, items, backup_item):
        def factory():
            def fn():
                return json.dumps({"items": items, "backup_item": backup_item}), "gpt-5.6-sol", "resp_1"
            return fn
        return factory

    def test_topic_missing_filled_by_backup_passes(self):
        items = [
            make_db_hybrid_item(1, "stoppage time", "C1"),
            make_db_hybrid_item(2, "blew the whistle", "C2"),
            make_db_hybrid_item(3, "wild finish", "C3"),
            make_db_hybrid_item(4, "file out", "C4"),
            make_db_hybrid_item(5, "take charge", "C5"),
        ]
        backup = make_db_hybrid_item(5, "the celebration", "C6")
        gate_result = src_ref_contract.run_source_reference_contract_gate(
            "A01", self._factory(items, backup), GOOD_ARTICLE,
            _db_hybrid_id_to_candidate(), _db_hybrid_sentence_reference())
        self.assertEqual(gate_result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=gate_result)
        self.assertTrue(gate_result["topic_slot_filled_by_backup"])
        self.assertEqual(gate_result["backup_substitution_reason"], "topic_missing")
        final_items = gate_result["parsed"]["items"]
        self.assertEqual(len(final_items), 5)
        self.assertEqual([it["key_phrase_role"] for it in final_items].count("important"), 5)
        self.assertEqual(final_items[4]["display_phrase"], "the celebration")

    def test_topic_present_but_invalid_item_filled_by_backup_passes(self):
        items = [
            make_db_hybrid_item(1, "stoppage time", "C1"),
            make_db_hybrid_item(2, "blew the whistle", "C2"),
            make_db_hybrid_item(3, "wild finish", "C3", key_phrase_role="topic", ja_gloss="broken gloss"),
            make_db_hybrid_item(4, "file out", "C4"),
            make_db_hybrid_item(5, "take charge", "C5"),
        ]
        backup = make_db_hybrid_item(5, "the celebration", "C6")
        gate_result = src_ref_contract.run_source_reference_contract_gate(
            "A01", self._factory(items, backup), GOOD_ARTICLE,
            _db_hybrid_id_to_candidate(), _db_hybrid_sentence_reference())
        self.assertEqual(gate_result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=gate_result)
        self.assertTrue(gate_result["topic_slot_filled_by_backup"])
        self.assertEqual(gate_result["backup_substitution_reason"], "topic_item_invalid")
        final_items = gate_result["parsed"]["items"]
        self.assertNotIn("broken gloss", [it.get("ja_gloss") for it in final_items])

    def test_backup_duplicate_candidate_skips_substitution_stays_invalid(self):
        items = [
            make_db_hybrid_item(1, "stoppage time", "C1"),
            make_db_hybrid_item(2, "blew the whistle", "C2"),
            make_db_hybrid_item(3, "wild finish", "C3"),
            make_db_hybrid_item(4, "file out", "C4"),
            make_db_hybrid_item(5, "take charge", "C5"),
        ]
        backup = make_db_hybrid_item(5, "stoppage time", "C1")  # 既存item0と重複するcandidate ID
        gate_result = src_ref_contract.run_source_reference_contract_gate(
            "A01", self._factory(items, backup), GOOD_ARTICLE,
            _db_hybrid_id_to_candidate(), _db_hybrid_sentence_reference())
        self.assertEqual(gate_result["status"], "KEY_WORDS_STRUCTURE_INVALID", msg=gate_result)
        self.assertFalse(gate_result["topic_slot_filled_by_backup"])
        self.assertEqual(gate_result["backup_substitution_reason"], "backup_candidate_duplicate_skip")


# ============================================================
# 11. Opus L2所見N7: 定数の二重管理の等価性(片方だけ変わると4+1検証が
#     黙って無効化されるリスクへの回帰防止)
# ============================================================
class ProductionItemCountEquivalenceTests(unittest.TestCase):

    def test_production_item_count_unchanged_equals_production_item_count(self):
        self.assertEqual(p2g.PRODUCTION_ITEM_COUNT_UNCHANGED, prod.PRODUCTION_ITEM_COUNT)


if __name__ == "__main__":
    unittest.main()
