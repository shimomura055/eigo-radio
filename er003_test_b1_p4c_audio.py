# ============================================================
# er003_test_b1_p4c_audio.py
# ER-003-B1-P4C: 「目印」マーカー・ASR表記揺れ許容ロジックのテスト
# ============================================================
# 実TTS・実MFA呼び出しは行わない。marker_token引数の再利用・
# check_chunk_contentの判定ロジックのみを対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p4c_audio -v

import json
import unittest

import er003_b1_p4b_audio as p4b
import er003_b1_p4c_audio as p4c


def _real_pattern_a_and_used_forms():
    with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
        data = json.load(f)
    pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
    return pattern_a["text"], pattern_a["used_forms"]


class StructuredSeparationTests(unittest.TestCase):
    """ER-005-AUDIO-INSTRUCTION-SEPARATION-01(DECIDED, CURRENT_SPEC.md):
    build_tts_prompt()がstyle instructionとspoken textを明示的に分離し、
    かつどちらの内容も一切変更しないことを確認する回帰テスト。"""

    def test_style_prefix_content_fully_preserved(self):
        style_prefix = "Speak the following text aloud naturally and clearly.\n\n"
        prompt = p4c.build_tts_prompt("some text", style_prefix)
        self.assertIn(style_prefix.strip(), prompt)

    def test_spoken_text_content_fully_preserved_verbatim(self):
        text = "A closer parent-child relationship was linked with fewer behavior problems."
        prompt = p4c.build_tts_prompt(text, "Style guidance.\n\n")
        self.assertIn(text, prompt)

    def test_style_and_text_are_delimited(self):
        prompt = p4c.build_tts_prompt("BODY_TEXT_MARKER", "STYLE_MARKER")
        self.assertIn("STYLE INSTRUCTIONS", prompt)
        self.assertIn("TEXT TO SPEAK", prompt)
        style_section_end = prompt.index("END STYLE INSTRUCTIONS")
        text_section_start = prompt.index("TEXT TO SPEAK (speak")
        # spoken textのマーカーは、STYLE区間の終わりより後に現れること
        # (=本文がSTYLE区間の外側、TEXT TO SPEAK区間の中にあることの確認)
        body_pos = prompt.index("BODY_TEXT_MARKER")
        self.assertGreater(body_pos, style_section_end)
        self.assertGreater(body_pos, text_section_start)

    def test_does_not_instruct_model_to_speak_style_section(self):
        prompt = p4c.build_tts_prompt("text", "style")
        self.assertIn("do not speak", prompt.lower())

    def test_japanese_text_preserved_verbatim(self):
        text = "内在化問題・感情や心の内側に表れやすい問題"
        prompt = p4c.build_tts_prompt(text, "日本語のstyle instruction")
        self.assertIn(text, prompt)

    def test_empty_style_prefix_does_not_crash(self):
        prompt = p4c.build_tts_prompt("text only", "")
        self.assertIn("text only", prompt)


class FallbackPathsUseStructuredSeparationTests(unittest.TestCase):
    """ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01 section 6: fallback pathも
    standard pathと同じStructured Separation契約を使うことを、実際の
    production関数のソースコードを検査して確認する(「本文とstyle
    instructionを直接文字列連結している」という抜け穴が新たに生まれて
    いないことの回帰テスト)。"""

    def _assert_uses_build_tts_prompt_not_raw_concat(self, module_name, func_name):
        import importlib
        import inspect
        mod = importlib.import_module(module_name)
        src = inspect.getsource(getattr(mod, func_name))
        self.assertIn("build_tts_prompt(", src,
                       f"{module_name}.{func_name} does not appear to call build_tts_prompt()")

    def test_a2_japanese_minimal_instruction_fallback(self):
        self._assert_uses_build_tts_prompt_not_raw_concat(
            "er003_v1_n3_01_tts_generate", "_generate_a2_japanese_minimal_instruction")

    def test_english_component_minimal_instruction_fallback(self):
        self._assert_uses_build_tts_prompt_not_raw_concat(
            "er003_v1_repro01_main_generate", "generate_english_component_minimal_instruction")

    def test_charon_japanese_minimal_instruction_fallback(self):
        self._assert_uses_build_tts_prompt_not_raw_concat(
            "er003_v1_sing01_voice01_generate", "generate_charon_japanese_minimal_instruction")

    def test_charon_japanese_standard_path(self):
        self._assert_uses_build_tts_prompt_not_raw_concat(
            "er003_v1_sing01_voice01_generate", "generate_charon_japanese")

    def test_charon_english_standard_and_fallback(self):
        self._assert_uses_build_tts_prompt_not_raw_concat(
            "er003_v1_sing01_voice01_generate", "generate_charon_english")

    def test_point_headings_standard_and_fallback(self):
        import importlib
        mod = importlib.import_module("er003_v1_sing01_point_headings_aoede")
        import inspect
        src = inspect.getsource(mod.generate)
        self.assertIn("build_tts_prompt(", src)

    def test_p9a_generate_narration_snippet_both_languages(self):
        # 英語・日本語どちらの分岐もbuild_tts_prompt()を通ることを確認
        # (以前は日本語分岐だけ直接連結していた抜け穴)。
        import inspect
        import er003_b1_p9a_audio as p9a
        src = inspect.getsource(p9a.generate_narration_snippet)
        self.assertEqual(src.count("p4c.build_tts_prompt("), 2,
                          "expected both the 'en' and 'ja' branches to call p4c.build_tts_prompt()")


class ChunkPlanReuseTests(unittest.TestCase):

    def test_build_chunk_plan_with_mejirushi_marker(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms, marker_token=p4c.MARKER_TOKEN)
        marker_chunks = [c for c in plan if c["chunk_type"] == "marker"]
        self.assertEqual(len(marker_chunks), 5)
        for c in marker_chunks:
            self.assertNotIn(c["used_form"], c["tts_text"])
            self.assertEqual(c["tts_text"].count("目印"), 1)
            self.assertEqual(c["tts_text"].count("合図"), 0)

    def test_chunk_plan_still_reconstructs_pattern_a(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms, marker_token=p4c.MARKER_TOKEN)
        reconstructed = "".join(c["source_text"] for c in plan)
        self.assertEqual(reconstructed, text)

    def test_default_marker_token_unchanged_for_p4b_callers(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan_default = p4b.build_chunk_plan(text, used_forms)
        marker_chunks = [c for c in plan_default if c["chunk_type"] == "marker"]
        for c in marker_chunks:
            self.assertEqual(c["tts_text"].count("合図"), 1)

    def test_verify_chunk_plan_static_with_mejirushi_marker(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms, marker_token=p4c.MARKER_TOKEN)
        result = p4b.verify_chunk_plan_static(plan, text, marker_token=p4c.MARKER_TOKEN)
        self.assertTrue(result["all_passed"], msg=result)
        self.assertEqual(result["total_marker_count"], 5)

    def test_verify_chunk_plan_static_default_still_checks_gou_zu(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan_mejirushi = p4b.build_chunk_plan(text, used_forms, marker_token=p4c.MARKER_TOKEN)
        # 「目印」入りchunkをデフォルト(「合図」)検証にかけると、
        # marker総数0で不合格になるはず(marker_tokenの取り違えを検知)。
        result = p4b.verify_chunk_plan_static(plan_mejirushi, text)
        self.assertEqual(result["total_marker_count"], 0)
        self.assertFalse(result["all_passed"])

    def test_marker_token_sequence_is_single_token(self):
        self.assertEqual(p4c.MARKER_TOKEN, "目印")
        self.assertEqual(p4c.MARKER_TOKEN_SEQUENCE, ("目印",))


class CheckChunkContentTests(unittest.TestCase):

    def _marker_chunk(self, tts_text, contains_last_few_minutes=False):
        return {
            "chunk_type": "marker", "tts_text": tts_text,
            "contains_last_few_minutes": contains_last_few_minutes,
        }

    def _normal_chunk(self, tts_text, contains_last_few_minutes=False):
        return {
            "chunk_type": "normal", "tts_text": tts_text,
            "contains_last_few_minutes": contains_last_few_minutes,
        }

    def test_passes_on_exact_kanji_marker(self):
        chunk = self._marker_chunk("わずかなリード、目印を守ろうとします。")
        r = p4c.check_chunk_content("わずかなリード目印を守ろうとします。", chunk)
        self.assertTrue(r["passed"], msg=r)
        self.assertTrue(r["marker_plausible"])

    def test_passes_on_hiragana_spelling_variant(self):
        chunk = self._marker_chunk("わずかなリード、目印を守ろうとします。")
        r = p4c.check_chunk_content("わずかなリードめじるしを守ろうとします。", chunk)
        self.assertTrue(r["passed"], msg=r)
        self.assertIn("めじるし", r["marker_spellings_found"])

    def test_passes_on_mixed_kanji_hiragana_variant(self):
        chunk = self._marker_chunk("わずかなリード、目印を守ろうとします。")
        r = p4c.check_chunk_content("わずかなリード目じるしを守ろうとします。", chunk)
        self.assertTrue(r["passed"], msg=r)
        self.assertIn("目じるし", r["marker_spellings_found"])

    def test_fails_when_no_marker_spelling_present_at_all(self):
        # P4Bのchunk05実機ログを「目印」文脈へ置き換えた再現ケース:
        # マーカー相当の語がどの表記でも一切現れない。
        chunk = self._marker_chunk("メッシが流れを変え、ついにアディショナルタイム、目印へ。")
        r = p4c.check_chunk_content("メッシが流れを変え、ついにアディショナルタイムアイズ。", chunk)
        self.assertFalse(r["passed"])
        self.assertFalse(r["marker_plausible"])

    def test_fails_when_chunk_becomes_english(self):
        chunk = self._marker_chunk("アルゼンチンの決勝への道を閉ざすこと――目印――が現実になりそうなその時、")
        r = p4c.check_chunk_content("close the door to the final", chunk)
        self.assertFalse(r["passed"])
        self.assertFalse(r["is_japanese"])
        self.assertFalse(r["no_unintended_english"])

    def test_fails_when_content_grossly_truncated(self):
        chunk = self._marker_chunk("前半は激しい接触と緊張が続き、両チームとも枠内シュート、目印を記録できないまま、静かな均衡が保たれます。")
        r = p4c.check_chunk_content("前半。", chunk)
        self.assertFalse(r["passed"])
        self.assertFalse(r["similarity_ok"])

    def test_normal_chunk_does_not_require_marker(self):
        # normal chunkはmarker_plausible=Falseでも合否に影響しない
        # (passed算出式のand節がchunk_type=="marker"の時だけ効く)。
        chunk = self._normal_chunk("最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。", contains_last_few_minutes=True)
        r = p4c.check_chunk_content("最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。", chunk)
        self.assertTrue(r["passed"], msg=r)
        self.assertFalse(r["marker_plausible"])

    def test_last_few_minutes_present_passes(self):
        chunk = self._normal_chunk("最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。", contains_last_few_minutes=True)
        r = p4c.check_chunk_content("最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。", chunk)
        self.assertIsNotNone(r["last_few_minutes_check"])
        self.assertTrue(r["last_few_minutes_check"]["present_in_recognized"])

    def test_last_few_minutes_missing_fails(self):
        chunk = self._normal_chunk("最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。", contains_last_few_minutes=True)
        r = p4c.check_chunk_content("最後に何が起きるのでしょうか。", chunk)
        self.assertFalse(r["last_few_minutes_check"]["present_in_recognized"])
        self.assertFalse(r["passed"])

    def test_tolerates_minor_asr_homophone_noise_elsewhere_in_sentence(self):
        # P4B実機ログ(chunk02)の「選手」→「戦士」のような、marker以外の
        # 軽微なASR誤変換では不合格にしない。
        chunk = self._marker_chunk("後半に試合が動くと、イングランドは選手を交代で下げる、目印という決断で守備を固め、")
        r = p4c.check_chunk_content("後半に試合が動くと、イングランドは戦士を下げる目印という決断で守備を固める。", chunk)
        self.assertTrue(r["passed"], msg=r)


if __name__ == "__main__":
    unittest.main()
