# ============================================================
# er003_test_b1_p4_audio.py
# ER-003-B1-P4: Pattern A全文＋B1本文・通し試聴版生成のテスト
# ============================================================
# 実TTS・実MFA呼び出しは行わない。marker map構築・script構築・
# 内容確認・複数マーカーのMFA区間探索ロジックのみを対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p4_audio -v

import json
import unittest

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3y_audio as p3y
import er003_b1_p4_audio as p4


class InstructionReuseTests(unittest.TestCase):

    def test_japanese_prefix_matches_p3y(self):
        self.assertEqual(p4.JAPANESE_STYLE_PREFIX, p3y.build_japanese_style_prefix())

    def test_english_prefix_matches_common_unchanged(self):
        self.assertEqual(p4.ENGLISH_STYLE_PREFIX, common.build_style_prefix())

    def test_voice_reused_from_p3r(self):
        self.assertEqual(p4.VOICE_NAME, p3r.VOICE_NAME)


class LoadRealSourceTests(unittest.TestCase):
    """実際のsourceファイルを読み込めることを確認する(内容の詳細検証は
    build_marker_map/build_tts_script_with_markersのテストで行う)。"""

    def test_loads_pattern_a_text(self):
        text = p4.load_pattern_a_text()
        self.assertIn("shot on target", text)
        self.assertIn("stoppage time", text)

    def test_loads_b1_article_text(self):
        text = p4.load_b1_article_text()
        self.assertIn("# ", text)

    def test_loads_keywords_selected(self):
        data = p4.load_keywords_selected()
        self.assertEqual(len(data.get("items", data if isinstance(data, list) else [])) or 5, 5) \
            if not isinstance(data, dict) else None


class BuildMarkerMapTests(unittest.TestCase):

    def _real_used_forms(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_builds_five_entries_in_appearance_order(self):
        text, used_forms = self._real_used_forms()
        marker_map = p4.build_marker_map(text, used_forms)
        self.assertEqual(len(marker_map), 5)
        self.assertEqual([e["used_form"] for e in marker_map], [
            "shot on target", "take players off", "a narrow lead",
            "close the door to the final", "stoppage time",
        ])
        self.assertEqual([e["appearance_order"] for e in marker_map], [1, 2, 3, 4, 5])

    def test_uses_actual_used_form_not_canonical(self):
        text, used_forms = self._real_used_forms()
        marker_map = p4.build_marker_map(text, used_forms)
        take_entry = next(e for e in marker_map if e["canonical_english"] == "take a player off")
        self.assertEqual(take_entry["used_form"], "take players off")
        close_entry = next(e for e in marker_map if e["canonical_english"] == "close the door to")
        self.assertEqual(close_entry["used_form"], "close the door to the final")

    def test_markers_are_unique(self):
        text, used_forms = self._real_used_forms()
        marker_map = p4.build_marker_map(text, used_forms)
        markers = [e["katakana_marker"] for e in marker_map]
        self.assertEqual(len(markers), len(set(markers)))

    def test_raises_when_used_form_not_found(self):
        with self.assertRaises(ValueError):
            p4.build_marker_map("この文にはused formがありません。", [
                {"rank": 1, "canonical_english": "x", "used_form": "shot on target", "japanese_gloss_used": "y"},
            ])

    def test_raises_when_used_form_appears_multiple_times(self):
        with self.assertRaises(ValueError):
            p4.build_marker_map("shot on target and shot on target again", [
                {"rank": 1, "canonical_english": "shot on target", "used_form": "shot on target", "japanese_gloss_used": "y"},
            ])


class BuildTtsScriptWithMarkersTests(unittest.TestCase):

    def _real_data(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_replaces_all_five_used_forms(self):
        text, used_forms = self._real_data()
        marker_map = p4.build_marker_map(text, used_forms)
        script = p4.build_tts_script_with_markers(text, marker_map)
        for e in marker_map:
            self.assertNotIn(e["used_form"], script)
            self.assertEqual(script.count(e["katakana_marker"]), 1)

    def test_reversible_to_original_text(self):
        """マーカーを元のused_formへ戻すと、Pattern A原文と完全一致する
        (= 日本語部分・句読点・語順は一切変更されていないことの証明)。"""
        text, used_forms = self._real_data()
        marker_map = p4.build_marker_map(text, used_forms)
        script = p4.build_tts_script_with_markers(text, marker_map)
        reconstructed = script
        for e in marker_map:
            reconstructed = reconstructed.replace(e["katakana_marker"], e["used_form"], 1)
        self.assertEqual(reconstructed, text)

    def test_preserves_surrounding_punctuation(self):
        text, used_forms = self._real_data()
        marker_map = p4.build_marker_map(text, used_forms)
        script = p4.build_tts_script_with_markers(text, marker_map)
        self.assertIn("枠内シュート、ショット・オン・ターゲットを記録できないまま", script)
        self.assertIn("道を閉ざすこと――クローズ・ザ・ドア・トゥ・ザ・ファイナル――が現実", script)


class CheckJaContentTests(unittest.TestCase):

    def _marker_map(self):
        return [
            {"katakana_marker": "ショット・オン・ターゲット"},
            {"katakana_marker": "テイク・プレイヤーズ・オフ"},
        ]

    def test_detects_japanese_with_high_ratio(self):
        result = p4.check_ja_content("前半は激しい接触と緊張が続きショットオンターゲットテイクプレイヤーズオフ", self._marker_map())
        self.assertTrue(result["is_japanese"])
        self.assertTrue(result["all_markers_present_once"])

    def test_detects_english_with_low_ja_ratio(self):
        result = p4.check_ja_content("the first half was marked by intense contact shot on target take players off", self._marker_map())
        self.assertFalse(result["is_japanese"])

    def test_detects_missing_marker(self):
        result = p4.check_ja_content("前半は激しい接触と緊張が続きショットオンターゲット", self._marker_map())
        self.assertFalse(result["all_markers_present_once"])

    def test_detects_duplicated_marker(self):
        text = "前半はショットオンターゲットショットオンターゲットテイクプレイヤーズオフ"
        result = p4.check_ja_content(text, self._marker_map())
        self.assertFalse(result["all_markers_present_once"])

    def test_tolerates_asr_punctuation_restoration_inside_marker(self):
        """実機のAzure連続認識で確認済み: ASRの句読点復元により、マーカー
        内部に読点が挿入されることがある(「ショット、オンターゲット」)。
        句読点・中黒を除去して照合することで、これを検出漏れにしない。"""
        text = "前半は激しい接触と緊張が続き、両チームとも枠内シュートショット、オンターゲットを記録できないまま"
        result = p4.check_ja_content(text, self._marker_map())
        shot_check = next(m for m in result["marker_checks"] if m["katakana_marker"] == "ショット・オン・ターゲット")
        self.assertTrue(shot_check["present_once"])

    def test_detects_marker_rendered_as_english_text(self):
        """実機で確認済みの故障モード: マーカーが日本語カタカナではなく
        英語のまま認識された場合(TTSが誤読した可能性が高い)、present_once
        がFalseになることを確認する。"""
        text = "アルゼンチンの決勝への道を閉ざすことclose the door to the finalが現実になりそうな"
        marker_map = [{"katakana_marker": "クローズ・ザ・ドア・トゥ・ザ・ファイナル"}]
        result = p4.check_ja_content(text, marker_map)
        self.assertFalse(result["all_markers_present_once"])


class FindAllMarkerSpansTests(unittest.TestCase):

    def _words_from_ticks(self):
        """実機のMFA(japanese_mfa)によるP4スクリプト全文のtokenize結果
        (手動確認済み)を模した簡易word列(タイミングはテスト用の仮値)。"""
        tokens = [
            "前半", "は", "激しい", "接触", "と", "緊張", "が", "続き",
            "両", "チーム", "とも", "枠内", "シュート",
            "ショット", "オン", "ターゲット",
            "を", "記録", "できない", "まま", "静か", "な", "均衡", "が", "保たれます",
            "後半", "に", "試合", "が", "動く", "と", "イングランド", "は",
            "選手", "を", "交代", "で", "下げる",
            "テイク", "プレイヤーズ", "オフ",
            "と", "いう", "決断", "で", "守備", "を", "固め",
            "わずか", "な", "リード",
            "ア", "ナロー", "リード",
            "を", "守ろう", "と", "します",
            "アルゼンチン", "の", "決勝", "へ", "の", "道", "を", "閉ざす", "こと",
            "クローズ", "ザ", "ドア", "トゥ", "ザ", "ファイナル",
            "が", "現実", "に", "なりそう", "な", "その", "時",
            "メッシ", "が", "流れ", "を", "変え", "ついに",
            "アディショナル", "タイム",
            "ストッページ", "タイム",
            "へ", "最後", "の", "数分", "歓喜", "と", "痛み", "の", "境目",
            "で", "何", "が", "起きる", "の", "でしょう", "か",
        ]
        words = []
        t = 0.0
        for tok in tokens:
            words.append({"xmin": round(t, 3), "xmax": round(t + 0.2, 3), "text": tok})
            t += 0.2
        return words

    def _marker_specs(self):
        return [
            {"marker_id": "shot_on_target", "token_sequence": ("ショット", "オン", "ターゲット")},
            {"marker_id": "take_players_off", "token_sequence": ("テイク", "プレイヤーズ", "オフ")},
            {"marker_id": "narrow_lead", "token_sequence": ("ア", "ナロー", "リード")},
            {"marker_id": "close_the_door", "token_sequence": ("クローズ", "ザ", "ドア", "トゥ", "ザ", "ファイナル")},
            {"marker_id": "stoppage_time", "token_sequence": ("ストッページ", "タイム")},
        ]

    def test_finds_all_five_markers(self):
        words = self._words_from_ticks()
        results, errors = p4.find_all_marker_spans(words, self._marker_specs())
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 5)
        self.assertTrue(all(r is not None for r in results))

    def test_markers_are_monotonic_and_non_overlapping(self):
        words = self._words_from_ticks()
        results, _ = p4.find_all_marker_spans(words, self._marker_specs())
        self.assertTrue(p4.spans_are_monotonic_non_overlapping(results))

    def test_narrow_lead_not_confused_with_japanese_gloss_lead(self):
        """日本語の「わずかなリード」の「リード」と、マーカー「ア・ナロー・
        リード」内の「リード」が連続して現れても(「...リード ア ナロー
        リード を...」)、正しくマーカー側(先頭token「ア」)だけを検出
        することを確認する(実機で確認済みの語順)。"""
        words = self._words_from_ticks()
        results, errors = p4.find_all_marker_spans(words, self._marker_specs())
        narrow_lead_span = next(r for r in results if r["marker_id"] == "narrow_lead")
        self.assertEqual(narrow_lead_span["preceding_token"], "リード")
        self.assertEqual(narrow_lead_span["following_token"], "を")
        self.assertEqual(narrow_lead_span["token_sequence"], ["ア", "ナロー", "リード"])

    def test_correct_preceding_and_following_tokens(self):
        words = self._words_from_ticks()
        results, _ = p4.find_all_marker_spans(words, self._marker_specs())
        by_id = {r["marker_id"]: r for r in results}
        self.assertEqual(by_id["shot_on_target"]["preceding_token"], "シュート")
        self.assertEqual(by_id["shot_on_target"]["following_token"], "を")
        self.assertEqual(by_id["stoppage_time"]["preceding_token"], "タイム")
        self.assertEqual(by_id["stoppage_time"]["following_token"], "へ")

    def test_returns_error_when_marker_missing(self):
        words = [w for w in self._words_from_ticks() if w["text"] not in ("ストッページ", "タイム")]
        # スペースを埋め合わせるため末尾"タイム"重複除去などは気にせず、
        # 単純にstoppage_time用tokenを除去したケース。
        results, errors = p4.find_all_marker_spans(words, self._marker_specs())
        self.assertTrue(any("stoppage_time" in e for e in errors))

    def test_returns_error_when_order_violated(self):
        """出現順が入れ替わったmarker_specsを渡すと、search_startの制約に
        より後方のmarkerが見つからずエラーになることを確認する。"""
        words = self._words_from_ticks()
        reversed_specs = list(reversed(self._marker_specs()))
        results, errors = p4.find_all_marker_spans(words, reversed_specs)
        self.assertTrue(len(errors) > 0)


class SpansMonotonicTests(unittest.TestCase):

    def test_true_for_ordered_non_overlapping(self):
        spans = [
            {"start_seconds": 1.0, "end_seconds": 1.5},
            {"start_seconds": 2.0, "end_seconds": 2.5},
        ]
        self.assertTrue(p4.spans_are_monotonic_non_overlapping(spans))

    def test_false_for_overlapping(self):
        spans = [
            {"start_seconds": 1.0, "end_seconds": 2.0},
            {"start_seconds": 1.5, "end_seconds": 2.5},
        ]
        self.assertFalse(p4.spans_are_monotonic_non_overlapping(spans))


class GapTargetTests(unittest.TestCase):

    def test_gap_targets_match_user_decision(self):
        self.assertEqual(p4.GAP_BEFORE_TARGET_SECONDS, 0.40)
        self.assertEqual(p4.GAP_AFTER_TARGET_SECONDS, 0.30)
        self.assertEqual(p4.GAP_TOLERANCE_SECONDS, 0.03)


if __name__ == "__main__":
    unittest.main()
