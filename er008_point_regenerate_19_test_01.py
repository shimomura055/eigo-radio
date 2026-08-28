# ============================================================
# er008_point_regenerate_19_test_01.py
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19
# ============================================================
import unittest

import er008_point_regenerate_19 as pr


class BuildPromptTests(unittest.TestCase):
    def test_prompt_includes_all_required_context(self):
        prompt = pr.build_point_regenerate_prompt(
            "Point One", "old point text", "full story text", "other point text",
            "FACT-01: something", "overlap 0.5 with Full Story", "role spec text")
        for expected in ("old point text", "full story text", "other point text",
                          "FACT-01: something", "overlap 0.5 with Full Story", "role spec text"):
            self.assertIn(expected, prompt)

    def test_prompt_states_prohibitions(self):
        prompt = pr.build_point_regenerate_prompt("Point Two", "x", "y", "z", "w", "r", "s")
        self.assertIn("Do not introduce any new fact", prompt)
        self.assertIn("causal claim", prompt)
        self.assertIn("certainty level", prompt)
        self.assertIn("scope", prompt)


class ExtractContentWordsNotInSourcesTests(unittest.TestCase):
    def test_flags_words_absent_from_all_sources(self):
        new_text = "The airline introduced a brand new boarding lounge policy."
        story = "The airline changed its boarding gate policy this year."
        ledger = "FACT-01: the policy affects boarding gates."
        flagged = pr._extract_content_words_not_in_sources(new_text, story, ledger)
        self.assertIn("lounge", flagged)
        self.assertIn("introduced", flagged)

    def test_does_not_flag_words_present_in_story_or_ledger(self):
        new_text = "The airline changed its gate policy."
        story = "The airline changed its boarding gate policy this year."
        ledger = "FACT-01: nothing relevant"
        flagged = pr._extract_content_words_not_in_sources(new_text, story, ledger)
        self.assertNotIn("airline", flagged)
        self.assertNotIn("changed", flagged)
        self.assertNotIn("gate", flagged)
        self.assertNotIn("policy", flagged)


class FakeResponse:
    def __init__(self, text, model="fake-model", response_id="fake-id"):
        self.output_text = text
        self.model = model
        self.id = response_id


class FakeClient:
    """実APIを一切呼ばない、regenerate_point_onlyのcontrol flowだけを
    検証するためのfakeクライアント(responses.createの戻り値を固定する)。"""

    def __init__(self, texts):
        self._texts = list(texts)
        self.calls = []

    class _Responses:
        def __init__(self, outer):
            self._outer = outer

        def create(self, **kwargs):
            self._outer.calls.append(kwargs)
            text = self._outer._texts.pop(0)
            return FakeResponse(text)

    @property
    def responses(self):
        return FakeClient._Responses(self)


class RegeneratePointOnlyControlFlowTests(unittest.TestCase):
    """実LLM呼び出しをfakeに差し替え、validation/retryのcontrol flow
    (overlapがまだ高ければattempt 2へ進む、下がればOKで返す)だけを検証する。"""

    def test_passes_immediately_when_new_text_has_low_overlap(self):
        client = FakeClient(["A completely different angle about social behavior and imitation."])
        result = pr.regenerate_point_only(
            client, "Point One", "old point restating the story", "the story mentions costs and risks",
            "the other point about something else entirely", "FACT-01: some fact",
            "overlap too high", "role spec", model="fake-model")
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["validation"]["overlap_vs_full_story"]["flagged"])
        self.assertEqual(len(client.calls), 1)

    def test_retries_when_overlap_still_high_then_stops_after_max_attempts(self):
        # 両attemptともFull Storyとほぼ同じ語を使い続け、重複検証に落ち続けるケース。
        story = "airport passengers wait in line before boarding starts at the gate"
        client = FakeClient([story, story])
        result = pr.regenerate_point_only(
            client, "Point One", "old point", story, "other point text unrelated",
            "FACT-01: some fact", "overlap too high", "role spec", model="fake-model", max_attempts=2)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(client.calls), 2)

    def test_reasoning_effort_passed_through_when_given(self):
        client = FakeClient(["different angle text entirely unrelated to story words"])
        pr.regenerate_point_only(
            client, "Point One", "old", "story text here", "other point", "ledger",
            "reason", "role", model="fake-model", reasoning_effort="medium")
        self.assertEqual(client.calls[0]["reasoning"], {"effort": "medium"})

    def test_reasoning_omitted_when_not_given(self):
        client = FakeClient(["different angle text entirely unrelated to story words"])
        pr.regenerate_point_only(
            client, "Point One", "old", "story text here", "other point", "ledger",
            "reason", "role", model="fake-model")
        self.assertNotIn("reasoning", client.calls[0])


if __name__ == "__main__":
    unittest.main()
