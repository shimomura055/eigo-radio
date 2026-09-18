# ============================================================
# er003_test_key_phrase_source_gate_01.py
# 管理ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01
# ============================================================
# 実API呼び出しなし。すべて合成データ・一時ディレクトリで完結する
# ユニットテスト(er003_test_key_words_canonicalization.pyと同様の様式)。

import json
import os
import shutil
import tempfile
import unittest

import er003_key_phrase_source_gate_01 as gate
import er003_v1_n3_01_assemble as asm


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _kp_items(pairs):
    """pairs: [(rank, used_form, source_span), ...]"""
    return {"items": [
        {"rank": r, "used_form": u, "source_span": s, "source_sentence": s,
         "display_phrase": u, "key_phrase": u, "japanese_gloss": "テスト"}
        for r, u, s in pairs
    ], "overall_status": "PASS"}


class NormalizeTextTests(unittest.TestCase):
    def test_case_insensitive(self):
        self.assertEqual(gate.normalize_text("Opt Out"), gate.normalize_text("opt out"))

    def test_apostrophe_variants(self):
        self.assertEqual(gate.normalize_text("don’t"), gate.normalize_text("don't"))

    def test_html_entity_unescape(self):
        self.assertEqual(gate.normalize_text("rock &amp; roll"), gate.normalize_text("rock & roll"))

    def test_dash_variants(self):
        self.assertEqual(gate.normalize_text("opt–out"), gate.normalize_text("opt-out"))

    def test_collapse_whitespace(self):
        self.assertEqual(gate.normalize_text("push   off   the stage"), gate.normalize_text("push off the stage"))


class CheckKeyPhraseSourcePresenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _kp_path(self, items):
        path = f"{self.tmp}/keywords_canonicalized.json"
        _write_json(path, items)
        return path

    def test_all_present_pass(self):
        article = "They pushed big bags off the stage this year. Many chose to opt out entirely."
        kp_path = self._kp_path(_kp_items([
            (1, "push off the stage", "pushed big bags off the stage"),
            (2, "opt out", "opt out"),
        ]))
        result = gate.check_key_phrase_source_presence(article, kp_path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["present"], 2)
        self.assertEqual(result["missing"], [])

    def test_normalization_differences_still_pass(self):
        """大小文字/apostrophe/entity/空白の表記ゆれがあってもPASSする。"""
        article = "The team said it Wasn’t   easy, and prices went up &amp; down."
        kp_path = self._kp_path(_kp_items([(1, "wasn't easy", "wasn't easy")]))
        result = gate.check_key_phrase_source_presence(article, kp_path)
        self.assertEqual(result["status"], "PASS")

    def test_missing_source_span_fails(self):
        """本文が平易化・書き換えされ、旧source_spanが本文から消えた
        ケース(Free-Address A2/AI Hiring A2の実際の事故を模擬)。"""
        article = "The apartment can feel like a place I only borrow."
        kp_path = self._kp_path(_kp_items([(1, "liberating", "liberating")]))
        result = gate.check_key_phrase_source_presence(article, kp_path)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["reason"], "SOURCE_SPAN_NOT_FOUND_IN_ARTICLE")

    def test_falls_back_to_source_sentence_when_source_span_absent(self):
        path = f"{self.tmp}/keywords_canonicalized.json"
        _write_json(path, {"items": [
            {"rank": 1, "used_form": "opt out", "source_span": None,
             "source_sentence": "Many chose to opt out entirely."},
        ]})
        article = "Many chose to opt out entirely."
        result = gate.check_key_phrase_source_presence(article, path)
        self.assertEqual(result["status"], "PASS")

    def test_no_source_field_available_is_reported_not_silently_passed(self):
        path = f"{self.tmp}/keywords_canonicalized.json"
        _write_json(path, {"items": [
            {"rank": 1, "used_form": "opt out", "source_span": None, "source_sentence": None},
        ]})
        result = gate.check_key_phrase_source_presence("any article text", path)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["missing"][0]["reason"], "NO_SOURCE_FIELD_AVAILABLE")

    def test_mixed_present_and_missing(self):
        article = "Many chose to opt out entirely."
        kp_path = self._kp_path(_kp_items([
            (1, "opt out", "opt out"),
            (2, "liberating", "liberating"),
        ]))
        result = gate.check_key_phrase_source_presence(article, kp_path)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["present"], 1)
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0]["rank"], 2)


class AssertKeyPhraseReuseSourceMatchesTests(unittest.TestCase):
    def test_identical_text_passes(self):
        text = "Same article body for both source and target."
        result = gate.assert_key_phrase_reuse_source_matches(text, text)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["source_sha256"], result["target_sha256"])

    def test_different_text_raises(self):
        with self.assertRaises(RuntimeError) as ctx:
            gate.assert_key_phrase_reuse_source_matches("Source article body.", "Different target article body.")
        self.assertIn("KEY_PHRASE_REUSE_SOURCE_MISMATCH", str(ctx.exception))


class VerifyEpisodeAudioValidationGateIntegrationTests(unittest.TestCase):
    """Assembly入口(共有verify_episode_audio_validation_gate)で、本文を
    わざと改変したfixtureに対しGate (a)がRuntimeErrorになることを確認する
    統合テスト。既存のsegment/gate statusチェックとは独立した経路である
    ことを、tts_generation_results.jsonをVALIDATED済み状態で用意して示す。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out_dir = f"{self.tmp}/a2"
        os.makedirs(f"{self.out_dir}/audit", exist_ok=True)
        os.makedirs(f"{self.out_dir}/key_phrases", exist_ok=True)
        os.makedirs(f"{self.out_dir}/narration", exist_ok=True)
        # 既存Audio Validation Gateを通過させるための最小限のsegment記録
        # (VALIDATEDのみ、A2 slowdown/disfluency QA/asset hash系チェックに
        # 引っかからないようentryを空に保つ)。
        _write_json(f"{self.out_dir}/audit/tts_generation_results.json", {"segments": {}, "key_phrases": {}})
        _write_json(f"{self.out_dir}/key_phrases/keywords_canonicalized.json",
                    _kp_items([(1, "opt out", "opt out")]))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_article(self, text):
        with open(f"{self.out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(text)

    def test_gate_passes_when_source_span_present_in_article_file(self):
        self._write_article("Many chose to opt out entirely.")
        asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        with open(f"{self.out_dir}/audit/key_phrase_source_gate.json", encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["status"], "PASS")

    def test_gate_raises_when_article_rewritten_without_key_phrase_update(self):
        """本文平易化後にKey Phraseが追従していないケースを再現する。"""
        self._write_article("Everyone decided to leave the program instead.")
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("KEY_PHRASE_SOURCE_MISSING", str(ctx.exception))

    def test_gate_uses_caller_supplied_article_text_over_file(self):
        """呼び出し側がarticle_textを明示的に渡した場合、それを優先する
        (Family C等、out_dirにarticle.mdを永続化しない経路向け)。"""
        self._write_article("This file text should be ignored by the gate.")
        asm.verify_episode_audio_validation_gate(self.out_dir, "A2",
                                                  article_text="Many chose to opt out entirely.")

    def test_gate_not_applicable_when_no_key_phrase_segments_and_no_asset(self):
        """FIX-01: KP segmentもKP assetも無いepisodeはNOT_APPLICABLEを記録
        して続行する(silent skipではなく理由を残す)。"""
        shutil.rmtree(f"{self.out_dir}/key_phrases")
        self._write_article("Any text at all.")
        asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        with open(f"{self.out_dir}/audit/key_phrase_source_gate.json", encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["status"], "NOT_APPLICABLE")

    def test_gate_raises_when_key_phrase_segments_present_but_asset_missing(self):
        """FIX-01: tts_generation_results.jsonにKey Phrase segmentが記録
        されているのにkeywords_canonicalized.jsonが無い場合はfail-closed
        (silentlyスキップしない)。"""
        shutil.rmtree(f"{self.out_dir}/key_phrases")
        _write_json(f"{self.out_dir}/audit/tts_generation_results.json", {
            "segments": {},
            "key_phrases": {"1": {
                "english": {"status": "OK", "disfluency_checked": True},
                "japanese": {"status": "OK", "disfluency_checked": True},
            }},
        })
        self._write_article("Any text at all.")
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("KEY_PHRASE_SOURCE_GATE_ASSET_MISSING", str(ctx.exception))

    def test_gate_raises_when_key_phrase_segments_present_and_article_text_unresolvable(self):
        """FIX-01: KP segmentがあり、KP assetもあるが、article_textを
        本文からもcaller指定からも解決できない場合はfail-closed。"""
        _write_json(f"{self.out_dir}/audit/tts_generation_results.json", {
            "segments": {},
            "key_phrases": {"1": {
                "english": {"status": "OK", "disfluency_checked": True},
                "japanese": {"status": "OK", "disfluency_checked": True},
            }},
        })
        # article.md/article_normalized.txtのどちらも書かない(未resolve)。
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE", str(ctx.exception))


class ReuseKeyPhrasesA2GateBTests(unittest.TestCase):
    """FIX-01: `reuse_key_phrases_a2`のGate (b)常時有効化(target未指定でも
    解決不能なら流用不可)を確認する。実TTS呼び出しはmock化する。"""

    def setUp(self):
        import er012_b_family_voices_a2_production_01 as a2prod
        self.a2prod = a2prod
        self.tmp = tempfile.mkdtemp()
        self.kp_source_dir = f"{self.tmp}/source_episode"
        os.makedirs(f"{self.kp_source_dir}/key_phrases", exist_ok=True)
        with open(f"{self.kp_source_dir}/article.md", "w", encoding="utf-8") as f:
            f.write("Many chose to opt out entirely.")
        _write_json(f"{self.kp_source_dir}/key_phrases/keywords_canonicalized.json",
                    _kp_items([(1, "opt out", "opt out")]))
        self.target_a2_dir = f"{self.tmp}/target_episode/a2"
        self.kp_dir = f"{self.target_a2_dir}/key_phrases"
        self.narration_dir = f"{self.target_a2_dir}/narration"
        os.makedirs(self.target_a2_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_raises_when_target_text_unspecified_and_unresolvable(self):
        """target_article_text未指定かつtarget_a2_dir/article.mdも無い
        場合、流用を実行せずRuntimeErrorで停止する(Gate (b)迂回不可)。"""
        with self.assertRaises(RuntimeError) as ctx:
            self.a2prod.reuse_key_phrases_a2(self.kp_source_dir, self.kp_dir, self.narration_dir)
        self.assertIn("KEY_PHRASE_REUSE_TARGET_TEXT_UNAVAILABLE", str(ctx.exception))

    def test_raises_on_mismatch_when_target_text_resolved_from_article_md(self):
        """target_article_text未指定でも、target_a2_dir/article.mdから
        解決した本文が供給元と不一致ならRuntimeError(流用しない)。"""
        with open(f"{self.target_a2_dir}/article.md", "w", encoding="utf-8") as f:
            f.write("A completely different target article body.")
        with self.assertRaises(RuntimeError) as ctx:
            self.a2prod.reuse_key_phrases_a2(self.kp_source_dir, self.kp_dir, self.narration_dir)
        self.assertIn("KEY_PHRASE_REUSE_SOURCE_MISMATCH", str(ctx.exception))

    def test_reuse_succeeds_when_source_and_target_text_match(self):
        """同一本文なら流用成功する(英語/日本語TTS呼び出しはmock)。"""
        import unittest.mock as mock
        with mock.patch.object(
                self.a2prod.shared_narration, "ensure_key_phrase_english_component",
                return_value={"status": "OK"}), \
             mock.patch.object(
                self.a2prod.n3_tts, "generate_a2_japanese_with_reading_safety",
                return_value={"status": "OK"}), \
             mock.patch.object(
                self.a2prod.n3_tts, "resolve_key_phrase_ja_gloss_tts",
                return_value=("テスト", False)):
            result = self.a2prod.reuse_key_phrases_a2(
                self.kp_source_dir, self.kp_dir, self.narration_dir,
                target_article_text="Many chose to opt out entirely.")
        self.assertIn(1, result)
        self.assertEqual(result[1]["english"]["status"], "OK")


if __name__ == "__main__":
    unittest.main()
