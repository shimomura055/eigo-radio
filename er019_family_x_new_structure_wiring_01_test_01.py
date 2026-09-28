# ============================================================
# er019_family_x_new_structure_wiring_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W1)
# ============================================================
# Family X新記事構造(途中Heading廃止・忠実英訳・段落境界での決定論的
# 3分割・Comment1〜4・Heading Readout撤去)のProduction配線を検証する
# 単体テスト。API呼び出しは一切行わない(mock/read-onlyのみ、費用¥0)。
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_new_structure_wiring_01_test_01 -v
# ============================================================
from __future__ import annotations

import hashlib
import json
import unittest

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_standard_a2_generate as std_gen
import er012_e_family_entertainment_two_level_runner_01 as runner
import er019_family_x_audio_plan_01 as plan
import er019_family_x_audio_production_runner_01 as audio_runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er045_family_x_no_heading_segmentation_trial_01 as trial


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ============================================================
# 1. Prompt sha256同一性(er045 Trialからの逐語転記確認)
# ============================================================
class PromptVerbatimTranscriptionTests(unittest.TestCase):
    def test_faithful_translation_instruction_matches_er045(self):
        self.assertEqual(_sha(adv_gen.FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION),
                          _sha(trial.TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION))

    def test_in_one_line_instruction_matches_er045_v2(self):
        self.assertEqual(_sha(adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE),
                          _sha(trial.TRIAL_IN_ONE_LINE_V2_INSTRUCTION_TEMPLATE))

    def test_translator_developer_message_matches_er045(self):
        self.assertEqual(_sha(adv_gen.FAMILY_X_TRANSLATOR_DEVELOPER),
                          _sha(trial.TRIAL_DEVELOPER_MESSAGE))

    def test_prompt_builder_reuses_existing_vocab_rule_and_must_fix_block(self):
        """新Prompt定数は既存ADVANCED_VOCAB_RULE_V2_BLOCK/build_must_fix_block()
        (無変更のProduction既存資産)をそのまま流用すること(コピペしない)。"""
        prompt = adv_gen.build_family_x_faithful_translation_prompt("JAテキスト")
        self.assertIn(adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK, prompt)
        must_fix = [{"fact_id": "F1", "claim_in_article": "c", "issue": "i", "explanation": "e"}]
        prompt_mf = adv_gen.build_family_x_faithful_translation_prompt("JAテキスト", must_fix=must_fix)
        self.assertIn(adv_gen.build_must_fix_block(must_fix), prompt_mf)


# ============================================================
# 2. v2 split アルゴリズムがer045実出力(Hormuz/Meta)と一致すること
# ============================================================
class V2SplitMatchesEr045OutputTests(unittest.TestCase):
    def _check_article(self, article: str):
        base = f"er045_output/family_x_no_heading_segmentation_trial_01/{article}"
        with open(f"{base}/trial_translation.json", encoding="utf-8") as f:
            tt = json.load(f)
        with open(f"{base}/trial_split.json", encoding="utf-8") as f:
            expected = json.load(f)
        with open(f"{base}/trial_in_one_line.json", encoding="utf-8") as f:
            iol = json.load(f)
        text = f"# {tt['title']}\n\n{tt['body']}\n\n## In one line\n{iol['text']}"
        got = sc.split_family_x_article_text_v2(text)
        self.assertEqual(got["status"], "OK")
        self.assertEqual(expected["status"], "OK")
        self.assertEqual(got["paragraph_count"], expected["paragraph_count"])
        self.assertEqual(got["part1"], expected["part1"])
        self.assertEqual(got["part2"], expected["part2"])
        self.assertEqual(got["part3"], expected["part3"])
        self.assertEqual(got["word_counts"]["part1"], expected["word_counts"]["part1"])
        self.assertEqual(got["word_counts"]["part2"], expected["word_counts"]["part2"])
        self.assertEqual(got["word_counts"]["part3"], expected["word_counts"]["part3"])

    def test_hormuz_matches_er045_trial_split(self):
        self._check_article("hormuz")

    def test_meta_matches_er045_trial_split(self):
        self._check_article("meta")

    def test_audio_plan_v2_wrapper_delegates_to_scaffold_single_source_of_truth(self):
        text = "# T\n\nP one word count enough here today please.\n\nP two also enough words here today.\n\nP three also has enough words today.\n\n## In one line\nSentence."
        self.assertEqual(plan.split_family_x_article_text_v2(text), sc.split_family_x_article_text_v2(text))


# ============================================================
# 3. OPEN-228のgateが新経路では到達不能であることの証明
# ============================================================
class Open228GateUnreachableTests(unittest.TestCase):
    def test_v2_split_does_not_raise_for_two_paragraph_intro(self):
        """旧split_article_text()は本文(Title直後〜1つ目の見出し前)が
        段落数2未満でRuntimeError(OPEN-228の直接原因)を送出したが、新v2
        splitは見出し自体が存在しないため、本文全体が3段落以上あれば
        (見出し起因の細切れが無いぶんintro相当が短くなる問題自体が発生
        しない)必ずOKになる。"""
        text = ("# T\n\nParagraph one has enough words to count here today.\n\n"
                "Paragraph two also has enough words to count here today.\n\n"
                "Paragraph three also has enough words to count here today.\n\n"
                "## In one line\nOne sentence.")
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "OK")

    def test_old_split_article_text_gate_still_exists_unmodified_for_family_a(self):
        """旧gate(sc.split_article_text、Main Storyの段落数2未満で
        RuntimeError)はFamily A向けに削除せず残置されていることを確認する
        (Family Xの新経路から外しただけ、他Family非影響)。"""
        text = "# T\n\nOnly one paragraph.\n\n### H1\nBody1\n\n### H2\nBody2\n\n## In one line\nS."
        with self.assertRaises(RuntimeError):
            sc.split_article_text(text)

    def test_run_writer_stage_family_x_path_never_calls_old_split_article_text(self):
        """run_writer_stage()(Family X唯一のProduction呼び出し元)は
        sc.split_article_text()(h3見出し2つ前提)を一切呼ばないこと
        (docstring/comment内の言及は対象外、実コードのみ確認)。"""
        import ast
        import inspect
        src = inspect.getsource(runner.run_writer_stage)
        tree = ast.parse(src)
        calls = [ast.dump(n) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(any("split_article_text" in c and "split_family_x_article_text_v2" not in c
                              for c in calls))
        self.assertIn("split_family_x_article_text_v2", src)


# ============================================================
# 4. Advanced/Standardの段落数retry分岐(対称性)
# ============================================================
class ParagraphCountRetrySymmetryTests(unittest.TestCase):
    def test_ensure_split_returns_ok_without_regen_when_paragraphs_sufficient(self):
        text = ("# T\n\nP1 has enough words here today please read.\n\n"
                "P2 has enough words here today please read.\n\n"
                "P3 has enough words here today please read.\n\n"
                "## In one line\nS.")
        called = {"n": 0}

        def regen():
            called["n"] += 1
            return text

        outcome = runner._family_x_ensure_split_or_paragraph_retry(text, regen, "Test")
        self.assertFalse(outcome["paragraph_retried"])
        self.assertEqual(called["n"], 0)
        self.assertEqual(outcome["split"]["status"], "OK")

    def test_ensure_split_retries_once_then_succeeds(self):
        too_few = "# T\n\nOnly one paragraph here.\n\n## In one line\nS."
        fixed = ("# T\n\nP1 has enough words here today please read.\n\n"
                 "P2 has enough words here today please read.\n\n"
                 "P3 has enough words here today please read.\n\n"
                 "## In one line\nS.")
        called = {"n": 0}

        def regen():
            called["n"] += 1
            return fixed

        outcome = runner._family_x_ensure_split_or_paragraph_retry(too_few, regen, "Test")
        self.assertTrue(outcome["paragraph_retried"])
        self.assertEqual(called["n"], 1)
        self.assertEqual(outcome["split"]["status"], "OK")

    def test_ensure_split_stops_when_retry_still_insufficient(self):
        too_few = "# T\n\nOnly one paragraph here.\n\n## In one line\nS."

        def regen():
            return too_few  # 再生成後も段落数が変わらない(worst case)

        with self.assertRaises(RuntimeError):
            runner._family_x_ensure_split_or_paragraph_retry(too_few, regen, "Test")

    def test_advanced_and_standard_use_identical_retry_helper(self):
        """Standard/Advancedの非対称にならないこと(同一ヘルパー関数を
        run_writer_stage()内の両分岐が呼ぶことをソース上で確認)。"""
        import inspect
        src = inspect.getsource(runner.run_writer_stage)
        self.assertEqual(src.count("_family_x_ensure_split_or_paragraph_retry("), 2)


# ============================================================
# 5. Heading Readout不在・comment_4存在・組立順(v2 segment順序)
# ============================================================
class HeadingReadoutRemovedAndAssemblyOrderTests(unittest.TestCase):
    def test_b1_v2_order_has_no_heading_segment(self):
        ids = [seg for _, seg, _ in plan.FAMILY_X_B1_SEGMENT_ORDER_V2 if seg]
        self.assertNotIn("full_story_part2_heading", ids)
        self.assertNotIn("full_story_part3_heading", ids)
        self.assertIn("comment_4", ids)
        self.assertIn("full_story_part2", ids)
        self.assertIn("full_story_part3", ids)

    def test_a2_v2_order_has_no_heading_segment(self):
        ids = [seg for _, seg, _ in plan.FAMILY_X_A2_SEGMENT_ORDER_V2 if seg]
        self.assertNotIn("full_story_part2_heading", ids)
        self.assertNotIn("full_story_part3_heading", ids)
        self.assertIn("comment_4", ids)

    def test_v2_order_assembly_sequence_comment_body_alternation(self):
        for order in (plan.FAMILY_X_B1_SEGMENT_ORDER_V2, plan.FAMILY_X_A2_SEGMENT_ORDER_V2):
            ids = [seg for _, seg, _ in order if seg]
            body_start = ids.index("comment_1")
            tail = ids[body_start:]
            self.assertEqual(tail, ["comment_1", "full_story_part1", "comment_2", "full_story_part2",
                                     "comment_3", "full_story_part3", "comment_4", "in_one_line"])

    def test_old_heading_containing_order_unmodified(self):
        """旧FAMILY_X_B1_SEGMENT_ORDER/A2_SEGMENT_ORDER(heading込み)は
        後方互換のため無変更のまま残置されていること(削除しない)。"""
        ids = [seg for _, seg, _ in plan.FAMILY_X_B1_SEGMENT_ORDER if seg]
        self.assertIn("full_story_part2_heading", ids)

    def test_generation_functions_do_not_reference_heading_fields_source(self):
        """generate_family_x_b1/a2_segments()はheading1/body2/body3
        フィールドを一切参照しないこと(v2 parts形状[part1/2/3]のみ使用)。"""
        import inspect
        src_b1 = inspect.getsource(audio_runner.generate_family_x_b1_segments)
        src_a2 = inspect.getsource(audio_runner.generate_family_x_a2_segments)
        for src in (src_b1, src_a2):
            self.assertNotIn('parts["heading1"]', src)
            self.assertNotIn('parts["body2"]', src)
            self.assertNotIn('parts["body3"]', src)
            self.assertIn('parts["part2"]', src)
            self.assertIn('parts["part3"]', src)


# ============================================================
# 6. Connected Speech(er020、read-only)がfull_story_part1/2/3を
#    引き続き認識すること
# ============================================================
class ConnectedSpeechRoleRecognitionTests(unittest.TestCase):
    def test_full_story_parts_resolve_without_heading_subsegments(self):
        for seg_id in ("full_story_part1", "full_story_part2", "full_story_part3"):
            self.assertEqual(retry_primitive.resolve_narrative_role(seg_id), "FULL_STORY")
            self.assertTrue(retry_primitive.connected_speech_enabled_for(seg_id))

    def test_comment_segments_resolve_to_comment(self):
        for seg_id in ("comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertEqual(retry_primitive.resolve_narrative_role(seg_id), "COMMENT")


# ============================================================
# 7. In One Line語数超過でFAILにしないこと(絶対上限を設けない)
# ============================================================
class InOneLineNoHardWordLimitTests(unittest.TestCase):
    def test_generate_in_one_line_prompt_uses_rough_guide_wording_not_strict_rule(self):
        self.assertIn("Trial-only guidance, not a strict rule",
                      adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE)

    def test_split_v2_does_not_validate_in_one_line_word_count(self):
        """split_family_x_article_text_v2()はin_one_lineの語数を検証・
        制限しない(status/paragraph_countはbody側のみに依存)。"""
        long_sentence = "word " * 60  # 60語(目安12-18語を大幅に超過)
        text = ("# T\n\nP1 has enough words here today please read.\n\n"
                "P2 has enough words here today please read.\n\n"
                "P3 has enough words here today please read.\n\n"
                f"## In one line\n{long_sentence.strip()}")
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["in_one_line"], long_sentence.strip())


# ============================================================
# 8. Standard/Advancedの段構成対称性
# ============================================================
class StandardAdvancedStructuralSymmetryTests(unittest.TestCase):
    def test_both_new_prompts_forbid_headings_and_require_paragraph_preservation(self):
        self.assertIn("Do not add section headings", adv_gen.FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION)
        self.assertIn("Do not add section headings",
                       std_gen.FAMILY_X_STANDARD_A2_NO_HEADING_PRESERVE_SENTENCE)
        self.assertIn("do not merge, split, or reorder paragraphs",
                       std_gen.FAMILY_X_STANDARD_A2_NO_HEADING_PRESERVE_SENTENCE)

    def test_both_stages_produce_same_parts_shape_via_split_v2(self):
        advanced_like = ("# Advanced Title\n\nAP1 has enough words here today please.\n\n"
                          "AP2 has enough words here today please.\n\n"
                          "AP3 has enough words here today please.\n\n"
                          "## In one line\nAdvanced closing.")
        standard_like = ("# Standard Title\n\nSP1 simple words here today please.\n\n"
                          "SP2 simple words here today please.\n\n"
                          "SP3 simple words here today please.\n\n"
                          "## In one line\nStandard closing.")
        adv_split = sc.split_family_x_article_text_v2(advanced_like)
        std_split = sc.split_family_x_article_text_v2(standard_like)
        self.assertEqual(set(adv_split.keys()), set(std_split.keys()))
        for key in ("status", "part1", "part2", "part3", "in_one_line", "word_counts"):
            self.assertIn(key, adv_split)
            self.assertIn(key, std_split)

    def test_standard_no_heading_generator_reuses_existing_vocab_block_unmodified(self):
        self.assertIn(std_gen.STANDARD_A2_NEW_VOCAB_BLOCK, std_gen.FAMILY_X_STANDARD_A2_NO_HEADING_PROMPT)


# ============================================================
# 9. JA入力(er039 AN3-T0セル)の機械検証(¥0、read-only)
# ============================================================
# SYMBOL_PREVENTION_BLOCK_JA(er019_family_x_ja_writer_o_r1_r2_01.py)が
# 禁止する記号を機械的に検出する(Production側に専用チェック関数が無い
# ため、本テストファイル内に検証専用ロジックとして実装する。Production
# コード自体は変更しない)。
import re as _sym_re

_SYMBOL_PREVENTION_FORBIDDEN_RE = _sym_re.compile(
    r"[〜～…]|/|[()（）\[\]]|[:：;；]|https?://|[\w.+-]+@[\w-]+\.[\w.-]+|"
    r"[\U0001F300-\U0001FAFF☀-➿]"
)


def check_symbol_prevention_violations(text: str) -> list:
    return [m.group(0) for m in _SYMBOL_PREVENTION_FORBIDDEN_RE.finditer(text or "")]


AN3_T0_JA_PATHS = {
    "hormuz": "er039_output/family_xy_concreteness_control_trial_02/hormuz/cells/AN3-T0_ja.md",
    "meta": "er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN3-T0_ja.md",
}
AN3_T0_DEVIATION_PATHS = {
    "hormuz": "er039_output/family_xy_concreteness_control_trial_02/hormuz/cells/AN3-T0_deviation.json",
    "meta": "er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN3-T0_deviation.json",
}


class JaInputMachineVerificationTests(unittest.TestCase):
    """er039 AN3-T0セル(Hormuz/Meta)がE2E JA入力として採用可能かの機械
    検証。(b)(Prompt同一構成)は git log による commit時系列確認
    (42f63319がbuild_original_prompt()へCONCRETENESS_CONTROL_AN3_BLOCK
    追加前[1f47ff72]・reminder追加[1f47ff72]前に生成されたことの確認)で
    実施済み(REPORT参照、本テストではreminder不在[(b)の一部]のみ再確認)。"""

    def test_no_reminder_string_in_either_article(self):
        for article, path in AN3_T0_JA_PATHS.items():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("再び増やさない", text, f"{article}: reminder文字列が混入しています")

    def test_deviation_check_is_ledger_compliant(self):
        for article, path in AN3_T0_DEVIATION_PATHS.items():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("parsed", {}).get("overall_status"), "LEDGER_COMPLIANT",
                              f"{article}: deviation checkがLEDGER_COMPLIANTではありません")

    def test_symbol_prevention_zero_violations(self):
        for article, path in AN3_T0_JA_PATHS.items():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            violations = check_symbol_prevention_violations(text)
            self.assertEqual(violations, [], f"{article}: SYMBOL_PREVENTION違反={violations}")

    def test_paragraph_count_at_least_three(self):
        for article, path in AN3_T0_JA_PATHS.items():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            blocks = [p for p in text.strip().split("\n\n") if p.strip()]
            # 先頭ブロックはTitle(1行目)。本文段落数はTitleを除いた件数。
            body_paragraph_count = len(blocks) - 1
            self.assertGreaterEqual(body_paragraph_count, 3,
                                     f"{article}: 本文段落数={body_paragraph_count}<3")

    def test_sha256_computable_for_both_articles(self):
        # 実測sha256値はREPORT §W1の検証表へ記録する(certutil -hashfile
        # 実行結果)。本テストは「計算可能・64桁hex」という形式のみ確認する。
        for article, path in AN3_T0_JA_PATHS.items():
            with open(path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
