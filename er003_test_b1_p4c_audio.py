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
