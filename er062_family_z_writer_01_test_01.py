# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04B test(課金0、mock中心。実API呼出なし)。"""
import hashlib
import io
import json
import os
import re
import tempfile
import unittest
from contextlib import redirect_stdout

import er006_model_routing_contract_01 as routing
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w

SEED_DIR = "er026_output/family_z_production_e2e_01/melos/seed"
TRIAL_R0_PROMPT = "er059_output/melos_sol_b3z_trial_01/m2_sol_only/r0_prompt.txt"
TRIAL_R2 = "er059_output/melos_sol_b3z_trial_01/m2_sol_only/r2.md"

R2_TRUTH = {"q1_1": "melos", "q2_1": "king", "q4_1": "melos", "q4_2": "melos", "q5_1": "king", "q6_1": "friend",
            "q7_1": "king", "q9_1": "friend", "q16_1": "other", "q17_1": "melos", "q23_1": "melos", "q26_1": "friend",
            "q31_1": "melos", "q31_2": "melos", "q33_1": "melos", "q34_1": "friend", "q36_1": "king", "q36_2": "king"}


def _seed():
    with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
        return json.load(f)


def _r2():
    with open(TRIAL_R2, encoding="utf-8") as f:
        return f.read()


def _paras(text):
    _t, b = st.split_title_body(text)
    return st.clean_body_paragraphs(b)


def _attr_hook(mapping, bad=None):
    """属性判定callにmappingで答えるhook。他のcallはNone(Mockの既定動作)。"""
    def hook(kw):
        fmt = (kw.get("text") or {}).get("format", {})
        if fmt.get("name") != "z_dialogue_attribution":
            return None
        ids = re.findall(r"\[\[Q:(q\d+_\d+)\]\]", kw["input"][-1]["content"])
        m = dict(mapping)
        m.update(bad or {})
        return json.dumps({"attributions": [{"quote_id": i, "speaker": m.get(i, "melos"), "basis": "t"} for i in ids]})
    return hook


def _llm(hook=None, cap=1e9):
    return w.LLM(w.MockClient(hook), w.Budget(cap))


def _story_text(n_paras=10, words=50, tag="word"):
    return "# T\n\n" + "\n\n".join(" ".join([f"{tag}{i}"] * words) for i in range(n_paras)) + "\n"


class PromptAssemblyTest(unittest.TestCase):
    def test_developer_equals_trial(self):
        import er018_fiction_story_dna_e_axis_redesign_01 as e
        self.assertEqual(w.WRITER_DEVELOPER_MESSAGE, e.WRITER_DEVELOPER_MESSAGE)

    def test_unchanged_blocks_match_trial_r0(self):
        with open(TRIAL_R0_PROMPT, encoding="utf-8") as f:
            trial = f.read()
        for blk in (w.R0_BLOCK_COMMON, w.R0_BLOCK_LISTENING):
            self.assertIn(blk, trial)

    def test_r0_prompt_advanced_and_requirements(self):
        p, applied = w.build_r0_prompt(_seed())
        self.assertEqual(len(applied), 2)                        # Seed変換計画のA2/語数文言を置換
        self.assertIn("about 480 words (roughly 400-560", p)
        self.assertIn("B1-B2", p)
        self.assertNotIn("A2", p)                                # Advanced Promptにレベル指定A2が残らない
        self.assertNotIn("300–350", p)
        self.assertIn("Preservation conditions", p)              # 原作保持(中心Story・人物関係・結末)
        self.assertIn("ending's outcome", p)
        self.assertIn("Only the main character", p)              # 外国人名ルール(Melosのみ固有名)
        self.assertIn("literature", p)                           # Story Type metadata
        for e in _seed()["seed_elements"]:
            self.assertIn(e, p)
        self.assertNotIn("Story Brief", p)                       # B3Zなし

    def test_r0_override_appended_when_plan_drifts(self):
        s = dict(_seed(), conversion_plan="Totally different plan.")
        p, applied = w.build_r0_prompt(s)
        self.assertIn("override_appended", applied)
        self.assertIn("ignore any earlier A2", p)

    def test_revise_prompt(self):
        p = w.build_revise_prompt("BODY")
        self.assertIn("BODY", p)
        self.assertIn("400-560", p)
        self.assertNotIn("A2", p)

    def test_std_prompt_z_specific(self):
        import er003_v1_n3_01_standard_a2_generate as sa2
        adv = _story_text(8, 60)
        p = w.build_std_prompt(adv)
        self.assertIn(sa2.STANDARD_A2_NEW_VOCAB_BLOCK, p)          # X共有ブロックを逐語import
        self.assertNotIn("## In one line", p)                      # In one line要求は含めない
        self.assertNotIn("Keep the same Markdown structure", p)
        self.assertIn("exactly 8 paragraphs", p)                   # 段落整列契約
        self.assertIn("must not be the same text as the source", p)
        self.assertIn(adv.strip(), p)


class RoutingAndCallTest(unittest.TestCase):
    def test_models_via_routing(self):
        llm = _llm()
        for key, model in (("FAMILY_Z_WRITER_ADV_R0", "gpt-6.1-sol"), ("FAMILY_Z_STD_ADJUST", "gpt-6.1-sol"),
                           ("FAMILY_Z_STORY_SPLIT", "gpt-6-luna"), ("FAMILY_Z_DIALOGUE_ATTRIBUTION", "gpt-6-luna")):
            llm.call(key, "t", "hello", effort="low")
            self.assertEqual(llm.client.responses.calls[-1]["model"], model)

    def test_actual_model_mismatch_stops(self):
        llm = _llm()
        orig = llm.client.responses.create

        def create(**kw):
            r = orig(**kw)
            r.model = "gpt-other"
            return r
        llm.client.responses.create = create
        with self.assertRaises(st.FamilyZStop):
            llm.call("FAMILY_Z_WRITER_ADV_R0", "t", "x", effort="high")

    def test_budget_stop_before_call(self):
        llm = _llm(cap=1.0)
        with self.assertRaises(st.FamilyZStop):
            llm.call("FAMILY_Z_WRITER_ADV_R0", "t", "x", effort="high")
        self.assertEqual(len(llm.client.responses.calls), 0)


class GuardrailTest(unittest.TestCase):
    def test_adv_word_range_is_warn_not_fail(self):
        g = w.check_adv_guardrails(_story_text(8, 30))
        self.assertTrue(any("ADV_WORDS_OUT_OF_RANGE" in x for x in g["warnings"]))
        self.assertEqual(g["failures"], [])
        g = w.check_adv_guardrails(_story_text(8, 60))
        self.assertEqual(g["warnings"], [])

    def test_adv_name_rule_fail(self):
        g = w.check_adv_guardrails("# T\n\nDionysius spoke.\n")
        self.assertTrue(g["failures"])

    def test_std_checks(self):
        adv = _story_text(8, 60)
        std = _story_text(8, 55, "easy")
        g = w.check_std_guardrails(std, adv)
        self.assertTrue(g["std_adv_paragraph_count_match"])
        self.assertEqual(g["failures"], [])
        self.assertAlmostEqual(g["ratio"], 440 / 480, places=2)
        g2 = w.check_std_guardrails(adv, adv)                       # 同一本文
        self.assertTrue(any("STD_SAME_AS_ADV" in f for f in g2["failures"]))
        g3 = w.check_std_guardrails(_story_text(6, 55, "easy"), adv)  # 段落数不一致はWARN(独自分割)
        self.assertFalse(g3["std_adv_paragraph_count_match"])
        self.assertTrue(any("PARAGRAPH_COUNT_MISMATCH" in x for x in g3["warnings"]))
        g4 = w.check_std_guardrails(_story_text(8, 20, "easy"), adv)
        self.assertTrue(any("STD_WORDS_OUT_OF_RANGE" in x for x in g4["warnings"]))
        self.assertTrue(any("STD_ADV_RATIO" in x for x in g4["warnings"]))

    def test_identical_ratio_formula(self):
        a = ["He ran home. She stayed there."]
        self.assertAlmostEqual(st.identical_sentence_ratio(["He ran home. She sat down."], a), 0.5)


class SplitCandidateTest(unittest.TestCase):
    def test_enumeration_equal_paragraphs(self):
        c = st.enumerate_split_candidates([10] * 10)
        self.assertIn((3, 6), c)
        for b1, b2 in c:
            parts = [b1 * 10, (b2 - b1) * 10, (10 - b2) * 10]
            self.assertTrue(all(0.2 - 1e-9 <= p / 100 <= 0.45 + 1e-9 for p in parts), (b1, b2))
        self.assertNotIn((1, 5), c)      # Part1=10%
        self.assertNotIn((5, 6), c)      # Part2=10%

    def test_empty_candidates_stop_no_fixed_fallback(self):
        with self.assertRaises(st.FamilyZSplitStop):
            w.select_split(_llm(), ["a b c d e f g h i j " * 20, "x y"])   # 2段落では3分割不能

    def test_select_in_candidates_and_reason(self):
        paras = _paras(_r2())
        r = w.select_split(_llm(), paras)
        self.assertIn(tuple(r["boundaries"]), set(map(tuple, r["candidates"])))
        self.assertTrue(r["reason_ja"])
        self.assertEqual(r["split_model_id"], "gpt-6-luna")

    def test_out_of_candidates_rejected_then_reproposed(self):
        paras = _paras(_r2())
        calls = {"n": 0}

        def hook(kw):
            if (kw.get("text") or {}).get("format", {}).get("name") != "z_split_choice":
                return None
            calls["n"] += 1
            if calls["n"] == 1:
                return json.dumps({"part2_starts_at_paragraph": 1, "part3_starts_at_paragraph": 2, "reason_ja": "x"})
            return None
        r = w.select_split(_llm(hook), paras)
        self.assertEqual(calls["n"], 2)
        self.assertFalse(r["attempts"][0]["ok"])
        self.assertTrue(r["attempts"][1]["ok"])

    def test_out_of_candidates_twice_stops(self):
        paras = _paras(_r2())

        def hook(kw):
            if (kw.get("text") or {}).get("format", {}).get("name") == "z_split_choice":
                return json.dumps({"part2_starts_at_paragraph": 1, "part3_starts_at_paragraph": 2, "reason_ja": "x"})
        with self.assertRaises(st.FamilyZSplitStop):
            w.select_split(_llm(hook), paras)

    def test_prompt_lists_ranges_not_free_choice(self):
        paras = _paras(_r2())
        p = w.build_split_prompt(paras, st.enumerate_split_candidates(st.para_word_counts(paras)))
        self.assertIn("b1=8: b2 in 20..27", p)
        self.assertIn("MUST choose", p)


class PlanClipsTest(unittest.TestCase):
    def setUp(self):
        self.paras = _paras(_r2())
        self.quotes = st.extract_quotes(self.paras)
        self.speakers = dict(R2_TRUTH)

    def test_ids_renamed_and_no_part_crossing(self):
        b1, b2 = 12, 26
        clips = st.plan_clips(self.paras, self.speakers, b1, b2, "b1b", "x/b1b/narration")
        pat = re.compile(r"^full_story_part([1-3])_c([0-9]+)$")
        seen = {1: 0, 2: 0, 3: 0}
        for c in clips:
            m = pat.match(c["id"])
            self.assertTrue(m, c["id"])
            seen[int(m.group(1))] += 1
            self.assertEqual(int(m.group(2)), seen[int(m.group(1))])
            self.assertEqual(c["part"], st.part_of_paragraph(c["paragraph_index"], b1, b2))
            for i in c["source_paragraph_indices"]:
                self.assertEqual(st.part_of_paragraph(i, b1, b2), c["part"])
            self.assertRegex(c["narration_path"], r"/(a2|b1b)/narration/full_story_part[1-3]_c[0-9]+\.wav$")
            self.assertEqual(c["text_sha256"], hashlib.sha256(c["text"].encode()).hexdigest())
        self.assertTrue(all(v > 0 for v in seen.values()))

    def test_force_split_uses_single_planner_call(self):
        import er013_family_c_production_01 as fam_c
        real = fam_c.plan_story_segments
        calls = []

        def spy(flat, **kw):
            calls.append(kw)
            return real(flat, **kw)
        fam_c.plan_story_segments = spy
        try:
            st.plan_clips(self.paras, self.speakers, 12, 26, "b1b", "x/b1b/narration")
        finally:
            fam_c.plan_story_segments = real
        self.assertEqual(len(calls), 1)                               # 全文1回
        self.assertEqual(set(calls[0]["force_split_before_paragraphs"]), {12, 26})

    def test_voice_roles_all_quotes_dialogue_narration_only_narrator(self):
        clips = st.plan_clips(self.paras, self.speakers, 12, 26, "b1b", "x/b1b/narration")
        # 引用符を含むclipは全てdialogue、含まないclipはnarrator
        for c in clips:
            has_quote = bool(st.QUOTE_RE.search(c["text"].replace('"', "“", 1)) or '"' in c["text"])
            if c["speaker"] == "narrator":
                self.assertNotIn('"', c["text"], c["id"])
                self.assertEqual(c["voice_role"], "narrator")
            else:
                self.assertTrue(c["text"].startswith('"'), c["id"])
                self.assertEqual(c["voice_role"], f"dialogue:{c['speaker']}")
                self.assertTrue(has_quote)
        sp = {c["speaker"] for c in clips}
        self.assertTrue({"narrator", "melos", "king", "friend"} <= sp)

    def test_comment_after_ids_are_part_boundaries(self):
        clips = st.plan_clips(self.paras, self.speakers, 12, 26, "b1b", "x/b1b/narration")
        ca = st.comment_after_segment_ids(clips)
        p1 = [c for c in clips if c["part"] == 1][-1]["id"]
        p2 = [c for c in clips if c["part"] == 2][-1]["id"]
        self.assertEqual(ca, {"2": p1, "3": p2})

    def test_flat_chunks_reconstruct_text(self):
        flat = st.build_flat_chunks(self.paras, self.speakers)
        for i, para in enumerate(self.paras):
            joined = "".join(r for (p, _v, r) in flat if p == i)
            self.assertEqual(joined.replace(" ", ""), para.replace(" ", ""))


class PlanRunTest(unittest.TestCase):
    def test_adv_plan_and_std_alignment_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            adv = _r2()
            llm = _llm(_attr_hook(R2_TRUTH))
            plan = w.run_plan(llm, "b1b", adv, d, "melos", "t1")
            self.assertEqual(plan["split_method"], "deterministic_candidates_llm_select")
            self.assertEqual(plan["split_origin"], "llm_select")
            self.assertEqual(len(plan["parts"]), 3)
            for p in plan["parts"]:
                self.assertTrue(0.20 <= p["ratio"] <= 0.45)
            self.assertEqual(plan["dialogue_summary"]["quotes"], 18)
            # Std: 段落数一致 -> Advの境界を写像(独自分割しない)
            std = adv.replace("Melos", "Melos")                      # 同段落数(別本文は別test)
            plan2 = w.run_plan(llm, "a2", std, d, "melos", "t1", adv_plan=plan)
            self.assertEqual(plan2["split_origin"], "mapped_from_advanced")
            self.assertEqual(plan2["boundaries"], plan["boundaries"])
            self.assertTrue(plan2["std_adv_paragraph_count_match"])
            self.assertRegex(plan2["clips"][0]["narration_path"], r"/a2/narration/")

    def test_std_independent_when_paragraph_count_differs(self):
        with tempfile.TemporaryDirectory() as d:
            llm = _llm(_attr_hook(R2_TRUTH))
            adv_plan = w.run_plan(llm, "b1b", _r2(), d, "melos", "t1")
            std = _story_text(10, 40, "easy")
            plan2 = w.run_plan(_llm(), "a2", std, d, "melos", "t1", adv_plan=adv_plan)
            self.assertEqual(plan2["split_origin"], "llm_select")
            self.assertFalse(plan2["std_adv_paragraph_count_match"])
            self.assertIn("段落数不一致", plan2["split_note"])

    def test_dialogue_mismatch_stops_and_writes_override(self):
        with tempfile.TemporaryDirectory() as d:
            llm = _llm(_attr_hook(R2_TRUTH, bad={"q2_1": "melos"}))   # 決定論=king, LLM=melos
            with self.assertRaises(st.FamilyZDialogueMismatchStop):
                w.run_plan(llm, "b1b", _r2(), d, "melos", "t1")
            ov = json.load(open(f"{d}/dialogue_override.json", encoding="utf-8"))
            self.assertEqual([m["quote_id"] for m in ov["mismatches"]], ["q2_1"])
            self.assertFalse(os.path.exists(f"{d}/segment_plan_b1b.json"))

    def test_human_confirmed_override_resolves_only_matching_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            llm = _llm(_attr_hook(R2_TRUTH, bad={"q2_1": "melos"}))
            with self.assertRaises(st.FamilyZDialogueMismatchStop):
                w.run_plan(llm, "b1b", _r2(), d, "melos", "t1")
            ov = json.load(open(f"{d}/dialogue_override.json", encoding="utf-8"))
            row = ov["mismatches"][0]
            ov["human_confirmed"] = {"b1b": {"q2_1": {"speaker": "king", "text": "WRONG"}}}
            json.dump(ov, open(f"{d}/dialogue_override.json", "w", encoding="utf-8"))
            with self.assertRaises(st.FamilyZDialogueMismatchStop):
                w.run_plan(llm, "b1b", _r2(), d, "melos", "t1")
            self.assertIn("human_confirmed", json.load(open(f"{d}/dialogue_override.json", encoding="utf-8")))
            ov["human_confirmed"] = {"b1b": {"q2_1": {"speaker": "king", "text": row["text"]}}}
            json.dump(ov, open(f"{d}/dialogue_override.json", "w", encoding="utf-8"))
            plan = w.run_plan(llm, "b1b", _r2(), d, "melos", "t1")
            att = json.load(open(f"{d}/dialogue_attribution_b1b.json", encoding="utf-8"))
            self.assertEqual(att["human_overrides_applied"], ["q2_1"])
            self.assertEqual(att["final"]["q2_1"], "king")
            self.assertTrue(plan["clips"])


class DialogueFixtureTest(unittest.TestCase):
    def _run(self, text, kw=None, llm_map=None):
        paras = [text]
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, kw)
        llm = llm_map or {}
        return st.reconcile_attribution(paras, quotes, det, llm), det

    def test_melos_told_the_king_is_melos(self):
        rec, det = self._run('“I will return,” Melos told the king.', llm_map={"q0_1": "melos"})
        self.assertEqual(det["q0_1"], "melos")
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["final"]["q0_1"], "melos")

    def test_family_c_style_king_first_keywords_misassign_and_llm_disagreement_stops(self):
        # Family C既存の語順(王が先)では「王に誤割当」になる。LLM(melos)と不一致 -> STOP対象
        kw = {"king": ["king", "ruler"], "melos": ["melos"]}
        rec, det = self._run('“I will return,” Melos told the king.', kw, {"q0_1": "melos"})
        self.assertEqual(det["q0_1"], "king")
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["rows"][0]["status"], "mismatch")

    def test_said_to_his_friend(self):
        rec, det = self._run('“I am here,” he said to his friend.', llm_map={"q0_1": "melos"})
        self.assertEqual(det["q0_1"], "friend")                      # keywordは「言及」を拾い誤判定
        self.assertFalse(rec["ok"])                                  # LLM(melos)と不一致でSTOP

    def test_mention_only_name_not_speaker_when_no_keyword(self):
        rec, det = self._run('Dionysius waited. “Go,” he said.', llm_map={"q0_1": "king"})
        self.assertIsNone(det["q0_1"])                               # 判定不能 -> llm_only
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["rows"][0]["status"], "llm_only")

    def test_llm_missing_or_invalid_is_problem(self):
        rec, _ = self._run('“A,” he said. “B,” she said.', llm_map={"q0_1": "melos"})
        self.assertFalse(rec["ok"])
        rec, _ = self._run('“A,” he said.', llm_map={"q0_1": "wizard"})
        self.assertFalse(rec["ok"])

    def test_all_quotes_of_three_speakers_get_attributed(self):
        paras = _paras(_r2())
        rec = w.attribute_dialogue(_llm(_attr_hook(R2_TRUTH)), paras)
        self.assertTrue(rec["ok"])
        self.assertEqual(set(rec["final"]), set(R2_TRUTH))
        self.assertEqual(len(rec["calls"]), 1)                       # 1 call
        self.assertEqual(rec["calls"][0]["routing_key"], "FAMILY_Z_DIALOGUE_ATTRIBUTION")


class LintTest(unittest.TestCase):
    def test_ja_clean_passes(self):
        t = "羊飼いのメロスは、人を疑って処刑する王に不満を持っています。ある日、王のもとへ向かいます。"
        self.assertEqual(st.lint_support_text(t, "ja"), [])

    def test_ja_violations(self):
        cases = {"このニュースでは": "NEWS_WORD", "In One Lineで": "IN_ONE_LINE", "ここがポイントです": "POINT_LABEL",
                 "Part 1では": "STRUCTURE_LABEL", "Full Storyを": "STRUCTURE_LABEL", "聞いてみましょう": "LISTEN_INSTRUCTION",
                 "メロスは間に合います": "SPOILER:間に合", "セリヌンティウスが": "FORBIDDEN_NAME:セリヌンティウス",
                 "This is a true story.": "LITERATURE_INTRO_LABEL"}
        for text, code in cases.items():
            body = text if st.is_japanese_text(text) else "日本語の文章です。" + text
            self.assertIn(code, st.lint_support_text(body, "ja"), text)

    def test_en_violations_and_clean(self):
        ok = "A shepherd is arrested by a ruler who trusts no one. What will he do about his sister's wedding?"
        self.assertEqual(st.lint_support_text(ok, "en"), [])
        bad = {"This news story begins.": "NEWS_WORD", "Point One is next.": "POINT_LABEL",
               "In One Line, we see": "IN_ONE_LINE", "Part 2 begins.": "STRUCTURE_LABEL",
               "He arrives just in time.": "SPOILER:just in time", "Dionysius laughed.": "FORBIDDEN_NAME:Dionysius"}
        for text, code in bad.items():
            self.assertIn(code, st.lint_support_text(text, "en"), text)
        self.assertIn("LANG_NOT_EN", st.lint_support_text("日本語だけ", "en"))
        self.assertIn("LANG_NOT_JA", st.lint_support_text("English only text here.", "ja"))
        self.assertEqual(st.lint_support_text("", "en"), ["EMPTY"])

    def test_retry_once_then_stop(self):
        outs = iter(["The news says.", "Good clean line about a shepherd."])
        text, att = w.generate_with_lint(lambda i: next(outs), lambda t: st.lint_support_text(t, "en"))
        self.assertEqual(len(att), 2)
        self.assertEqual(text, "Good clean line about a shepherd.")
        with self.assertRaises(st.FamilyZLintStop):
            w.generate_with_lint(lambda i: "news again", lambda t: st.lint_support_text(t, "en"))


class SupportGenerationTest(unittest.TestCase):
    def setUp(self):
        self.parts = {1: "PART ONE SHEPHERD SCENE.", 2: "PART TWO RIVER SCENE.", 3: "PART THREE CITY SCENE."}

    def test_adv_uses_x_b1_roles_unmodified_and_no_comment4(self):
        import er003_v1_b1_scaffold_01_generate as b1s
        seen = []

        def fn(client, role, ctx, model=None):
            seen.append((role, ctx, model))
            return {"status": "OK", "text": "A shepherd faces a ruler and a hard choice."}
        out = w.run_support_adv(object(), self.parts, "FULL", en_support_fn=fn)
        roles = [r for r, _c, _m in seen]
        self.assertEqual(roles[0], b1s.COMMENT_1_ROLE)
        self.assertEqual(roles[1], b1s.COMMENT_2_ROLE)
        self.assertEqual(roles[2], b1s.COMMENT_2_ROLE)
        self.assertNotIn(b1s.COMMENT_4_ROLE, roles)
        self.assertNotIn(b1s.COMMENT_3_ROLE, roles)                  # Point橋渡し役割は使わない
        self.assertTrue(roles[3].startswith("あなたはPodcastの冒頭を担当するナビゲーター"))
        self.assertEqual(set(out["comments"]), {"1", "2", "3"})
        self.assertTrue(all(m == "gpt-6-luna" for _r, _c, m in seen))
        self.assertIn("ニュースではなく", seen[0][1])                  # 文脈側でnews前提を打ち消す(role無改変)
        self.assertIn("PART TWO", seen[2][1])

    def test_adv_lint_ng_retry_then_stop(self):
        n = {"i": 0}

        def fn(client, role, ctx, model=None):
            n["i"] += 1
            return {"status": "OK", "text": "In this news story, a man runs."}
        with self.assertRaises(st.FamilyZLintStop):
            w.run_support_adv(object(), self.parts, "FULL", en_support_fn=fn)
        self.assertEqual(n["i"], 2)                                 # retry 1回のみ

    def test_std_comment_facts_only_from_target_part(self):
        ctxs = []

        def fn(client, prompt, context, model=None):
            ctxs.append((prompt, context))
            return {"status": "OK", "text": "羊飼いのメロスは王の前に立たされています。妹の結婚式が近く、気がかりです。"
                                            "友人との関係も大切な場面になります。"}
        out = w.run_support_std(object(), self.parts, "FULL STORY", ja_support_fn=fn)
        self.assertEqual(set(out["comments"]), {"1", "2", "3"})
        # Comment1(2回目以降のcall含む)のcontextは対象Partのみ。他Partの本文は含めない
        c1_ctx = [c for _p, c in ctxs if "PART ONE" in c and "PART TWO" not in c]
        self.assertTrue(c1_ctx)
        c2_ctx = [c for _p, c in ctxs if "PART TWO" in c and "PART THREE" not in c]
        self.assertTrue(c2_ctx)
        self.assertTrue(any("これから聞く部分】\nPART THREE" in c for _p, c in ctxs))
        self.assertIn("プレビュー" if False else "preview", out)

    def test_std_preview_has_no_listen_instruction(self):
        def fn(client, prompt, context, model=None):
            return {"status": "OK", "text": "聞いてみましょう、羊飼いの話です。"}
        with self.assertRaises((st.FamilyZLintStop, RuntimeError)):
            w.run_support_std(object(), self.parts, "FULL", ja_support_fn=fn)


class KeyPhraseTest(unittest.TestCase):
    def test_kp_levels_and_processes_are_separate(self):
        calls = []

        def kp(text, kp_dir, article_id, level, process=None):
            calls.append((kp_dir, article_id, level, process))
            return {"ok": True}
        with tempfile.TemporaryDirectory() as d:
            w.run_kp_stage("a2", "std text", d, "melos", kp_fn=kp)
            w.run_kp_stage("b1b", "adv text", d, "melos", kp_fn=kp)
        self.assertEqual([c[2:] for c in calls], [("A2", "A2_SUPPORT"), ("B1", "B1_SUPPORT")])
        self.assertNotEqual(calls[0][0], calls[1][0])

    def test_phrase_sharing_only_for_identical_text(self):
        self.assertTrue(w.english_phrase_sharing_allowed("same", "same"))
        self.assertFalse(w.english_phrase_sharing_allowed("std", "adv"))


class ProvenanceChainTest(unittest.TestCase):
    def _run(self, d, hook=None, **kw):
        return w.run_writer_chain(_llm(hook), d, SEED_DIR, **kw)

    def test_full_chain_and_sha_links(self):
        with tempfile.TemporaryDirectory() as d:
            res = self._run(d, stages=("r0", "r1", "r2", "std_adjust"))
            prov = json.load(open(f"{d}/writer/provenance.json", encoding="utf-8"))
            ch = {e["stage"]: e for e in prov["chain"]}
            self.assertEqual(list(ch), ["r0", "r1", "r2", "std_adjust"])
            seed_sha = hashlib.sha256(open(f"{SEED_DIR}/seed.json", "rb").read()).hexdigest()
            self.assertEqual(prov["seed_sha256"], seed_sha)
            self.assertEqual(ch["r0"]["input_sha256"], seed_sha)
            self.assertEqual(ch["r1"]["input_sha256"], ch["r0"]["output_sha256"])
            self.assertEqual(ch["r2"]["input_sha256"], ch["r1"]["output_sha256"])
            self.assertEqual(ch["std_adjust"]["input_sha256"], ch["r2"]["output_sha256"])
            self.assertEqual(prov["adv_final_sha256"], ch["r2"]["output_sha256"])
            self.assertEqual(prov["std_sha256"], ch["std_adjust"]["output_sha256"])
            for s, e in ch.items():
                for k in ("routing_key", "requested_model", "actual_model_id", "effort", "response_id", "attempts",
                          "cost_jpy", "input_sha256", "output_sha256", "prompt_sha256"):
                    self.assertIn(k, e, (s, k))
                self.assertEqual(e["output_sha256"],
                                 hashlib.sha256(open(f"{d}/writer/{w.STAGE_FILE[s]}", "rb").read()).hexdigest())
            self.assertEqual(ch["r0"]["routing_key"], "FAMILY_Z_WRITER_ADV_R0")
            self.assertEqual(ch["std_adjust"]["routing_key"], "FAMILY_Z_STD_ADJUST")
            self.assertEqual(ch["r0"]["actual_model_id"], "gpt-6.1-sol")
            self.assertTrue(all(v["status"] == "generated" for v in res["stages"].values()))

    def test_resume_reuses_without_calls(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0", "r1", "r2"))
            llm = _llm()
            res = w.run_writer_chain(llm, d, SEED_DIR, stages=("r0", "r1", "r2"))
            self.assertEqual(len(llm.client.responses.calls), 0)
            self.assertTrue(all(v["status"] == "reused" for v in res["stages"].values()))

    def test_edited_r2_file_stops_never_regenerates(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0", "r1", "r2"))
            with open(f"{d}/writer/r2.md", "a", encoding="utf-8") as f:
                f.write("tampered\n")
            llm = _llm()
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.run_writer_chain(llm, d, SEED_DIR, stages=("r0", "r1", "r2"))
            self.assertEqual(len(llm.client.responses.calls), 0)

    def test_parent_sha_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0", "r1", "r2"))
            with open(f"{d}/writer/r1.md", "a", encoding="utf-8") as f:
                f.write("tampered\n")
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.run_writer_chain(_llm(), d, SEED_DIR, stages=("r2",))

    def test_file_without_entry_stops(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/writer")
            open(f"{d}/writer/r0.md", "w").write("orphan")
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                self._run(d, stages=("r0",))

    def test_seed_sha_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0",))
            p = f"{d}/writer/provenance.json"
            j = json.load(open(p, encoding="utf-8"))
            j["seed_sha256"] = "0" * 64
            json.dump(j, open(p, "w", encoding="utf-8"))
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                self._run(d, stages=("r0",))

    def test_regenerate_only_explicit_and_marks_downstream_stale(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0", "r1", "r2"))
            llm = _llm()
            w.run_writer_chain(llm, d, SEED_DIR, stages=("r0", "r1"), regenerate_stage="r1")
            self.assertEqual(len(llm.client.responses.calls), 1)       # r1のみ
            prov = json.load(open(f"{d}/writer/provenance.json", encoding="utf-8"))
            self.assertIn("r2", prov["downstream_stale"])
            self.assertEqual(len(prov["regenerations"]), 1)
            # staleのr2は自動再生成されない
            llm2 = _llm()
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.run_writer_chain(llm2, d, SEED_DIR, stages=("r0", "r1", "r2"))
            self.assertEqual(len(llm2.client.responses.calls), 0)
            # 明示指定でのみr2を再生成
            llm3 = _llm()
            w.run_writer_chain(llm3, d, SEED_DIR, stages=("r2",), regenerate_stage="r2")
            self.assertEqual(len(llm3.client.responses.calls), 1)
            prov = json.load(open(f"{d}/writer/provenance.json", encoding="utf-8"))
            self.assertNotIn("r2", prov["downstream_stale"])

    def test_std_same_as_adv_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._run(d, stages=("r0", "r1", "r2"))

            def hook(kw):
                if "Rewrite this entire story for CEFR A2" in kw["input"][-1]["content"]:
                    return open(f"{d}/writer/r2.md", encoding="utf-8").read()
            with self.assertRaises(st.FamilyZStop):
                self._run(d, hook, stages=("std_adjust",))

    def test_r2_name_violation_stops(self):
        with tempfile.TemporaryDirectory() as d:
            def hook(kw):
                if kw["input"][-1]["content"].startswith("Here is a short story"):
                    return "# T\n\n" + " ".join(["Dionysius"] * 450)
            with self.assertRaises(st.FamilyZStop):
                self._run(d, hook, stages=("r0", "r1", "r2"))

    def test_ensure_stage_downstream_input_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            prov = w.Provenance(f"{d}/p.json", "melos", "s" * 64)
            out = f"{d}/x.json"
            w.ensure_stage(prov, "plan_b1b", "A", out, lambda: ("{}", {}))
            r = w.ensure_stage(prov, "plan_b1b", "A", out, lambda: ("{}", {}))
            self.assertEqual(r["status"], "reused")
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.ensure_stage(prov, "plan_b1b", "B", out, lambda: ("{}", {}))


class CliTest(unittest.TestCase):
    def test_dry_run_has_no_side_effects(self):
        before = set(os.listdir("er026_output/family_z_production_e2e_01/melos")) if os.path.isdir(
            "er026_output/family_z_production_e2e_01/melos") else set()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = w.main(["--run", "dryrun_t", "--stage", "writer", "--mode", "dry-run"])
        self.assertEqual(rc, 0)
        self.assertIn('"dry_run": true', buf.getvalue())
        after = set(os.listdir("er026_output/family_z_production_e2e_01/melos"))
        self.assertEqual(before, after)
        self.assertFalse(os.path.exists("er026_output/family_z_production_e2e_01/melos/dryrun_t"))

    def test_real_requires_budget(self):
        with self.assertRaises(SystemExit):
            w.main(["--run", "x", "--stage", "writer", "--mode", "real"])


if __name__ == "__main__":
    unittest.main()
