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
        self.assertIn("about 400 words (roughly 330-470", p)   # 2026-10-19ユーザー指示④: Adv/Std共通400±70
        self.assertIn("B1-B2", p)
        self.assertNotIn("A2", p)                                # Advanced Promptにレベル指定A2が残らない
        self.assertNotIn("300–350", p)
        self.assertIn("Editorial policy", p)                     # 2026-10-12決定: エッセンス重視・自然なStorytelling優先
        self.assertIn("develop differently from the original", p)
        self.assertNotIn("Preservation conditions", p)           # 旧・原作保持条件(撤回)
        self.assertNotIn("ending's outcome", p)
        self.assertNotIn("in the same order of events", p)
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
        self.assertIn("330-470", p)
        self.assertNotIn("400-560", p)
        self.assertNotIn("A2", p)

    def test_std_prompt_z_specific(self):
        import er003_v1_n3_01_standard_a2_generate as sa2
        adv = _story_text(8, 60)
        p = w.build_std_prompt(adv)
        self.assertIn(sa2.STANDARD_A2_NEW_VOCAB_BLOCK, p)          # X共有ブロックを逐語import
        self.assertNotIn("## In one line", p)                      # In one line要求は含めない
        self.assertNotIn("Keep the same Markdown structure", p)
        self.assertIn("exactly 8 paragraphs", p)                   # 段落整列契約(構造契約、指示は維持)
        self.assertIn("about 400 words", p)                        # 語数目標はAdvと同じ(Adv語数に連動しない)
        self.assertIn("between 330 and 470", p)
        self.assertNotIn("Keep every fact exactly", p)             # 過度な忠実性要求の撤回
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
        g = w.check_adv_guardrails(_story_text(8, 45))        # 360語(330-470内)
        self.assertEqual(g["warnings"], [])

    def test_adv_name_rule_is_warn_only(self):
        # 2026-10-12決定: 固有名詞関連はブロックしない(WARNのみ)
        g = w.check_adv_guardrails("# T\n\nDionysius spoke.\n")
        self.assertEqual(g["failures"], [])
        self.assertTrue(any("NAME_RULE_NOTE" in x for x in g["warnings"]))

    def test_std_checks(self):
        adv = _story_text(8, 60)
        std = _story_text(8, 55, "easy")
        g = w.check_std_guardrails(std, adv)
        self.assertTrue(g["std_adv_paragraph_count_match"])
        self.assertEqual(g["failures"], [])
        self.assertAlmostEqual(g["ratio"], 440 / 480, places=2)   # 参考値(判定には使わない)
        self.assertFalse(hasattr(w, "STD_ADV_RATIO_RANGE"))       # Adv/Std語数比Guardrailは撤回
        g2 = w.check_std_guardrails(adv, adv)                       # 同一本文
        self.assertTrue(any("STD_SAME_AS_ADV" in f for f in g2["failures"]))
        g3 = w.check_std_guardrails(_story_text(6, 55, "easy"), adv)  # 段落数不一致はWARN(独自分割)
        self.assertFalse(g3["std_adv_paragraph_count_match"])
        self.assertTrue(any("PARAGRAPH_COUNT_MISMATCH" in x for x in g3["warnings"]))
        g4 = w.check_std_guardrails(_story_text(8, 20, "easy"), adv)
        self.assertTrue(any("STD_WORDS_OUT_OF_RANGE" in x for x in g4["warnings"]))
        self.assertFalse(any("RATIO" in x for x in g4["warnings"]))

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


class Comment3ContentFactsLimitTest(unittest.TestCase):
    """委任_12D Fable判断: Comment3のcontent_factsはPart3先頭約25%(最低2段落)かつ到着・結末段落を含めない。"""

    def _p3(self, n):
        return "\n\n".join(f"para{i}" for i in range(1, n + 1))

    def test_limit_ratio_and_min(self):
        sep = chr(10) * 2
        for n, k in ((10, 2), (8, 2), (3, 2), (1, 1), (16, 4)):
            self.assertEqual(w.limit_comment3_part(self._p3(n)), sep.join(f"para{i}" for i in range(1, k + 1)))

    def test_ending_paragraph_excluded(self):
        sep = chr(10) * 2
        paras = ["He remembered the hands.", "Water came; he drank.", "He took one step.", "At the city gates, the bell rang.",
                 "He raced to the square.", "The sword was raised.", "They held each other.", "The ruler spoke."]
        # 8段落 -> k=2。先頭2段落に結末マーカー無し
        self.assertEqual(w.limit_comment3_part(sep.join(paras)), sep.join(paras[:2]))
        # 16段落 -> k=4。4段落目(index3)が"city gates"なので除外され先頭3段落
        longp = paras[:3] + paras[3:4] + ["x"] * 12
        self.assertEqual(w.limit_comment3_part(sep.join(longp)), sep.join(paras[:3]))
        # 先頭段落が結末マーカーでも最低1段落は残す
        self.assertEqual(w.limit_comment3_part(sep.join(["He arrived at the gate.", "b", "c", "d"])), "He arrived at the gate.")

    def test_std_comment3_receives_only_front_part_and_prior_reused(self):
        # FZQI委任_06更新: fam_cモック前提 -> Adv同形の新経路(a2gen役割文)。Comment3のcontextはPart3先頭約25%のみ、
        # method一致のpriorならComment1/2/Previewは再利用されComment3のみ生成される。
        seen = []

        def fn(client, role, context, model=None):
            seen.append((role, context))
            return {"status": "OK", "text": "メロスは走ります。"}

        parts = {1: "a1", 2: "a2", 3: self._p3(10)}
        prior = {"method": w.STD_SUPPORT_METHOD_VERSION, "comments": {"1": "P1", "2": "P2"},
                 "attempts": {"comment_1": [], "comment_2": [], "preview": []}, "preview": "PV"}
        out = w.run_support_std(None, parts, "full", ja_support_fn=fn, prior=prior)
        self.assertEqual(len(seen), 1)
        c3 = seen[0][1]
        self.assertIn("para2", c3)
        self.assertNotIn("para3", c3)
        self.assertEqual(out["comments"]["1"], "P1")
        self.assertEqual(out["preview"], "PV")


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
        # FZQI委任_06更新: content_facts(fam_c)前提 -> Adv同形のcontext構成(Comment nは本文の該当範囲のみ)
        ctxs = []

        def fn(client, prompt, context, model=None):
            ctxs.append((prompt, context))
            return {"status": "OK", "text": "羊飼いのメロスは王の前に立たされています。妹の結婚式が近く、気がかりです。"
                                            "友人との関係も大切な場面になります。"}
        out = w.run_support_std(object(), self.parts, "FULL STORY", ja_support_fn=fn)
        self.assertEqual(set(out["comments"]), {"1", "2", "3"})
        c1_ctx = ctxs[0][1]
        self.assertIn("PART ONE", c1_ctx)
        self.assertNotIn("PART TWO", c1_ctx)
        c2_ctx = ctxs[1][1]
        self.assertIn("PART TWO", c2_ctx)
        self.assertNotIn("PART THREE", c2_ctx)
        self.assertIn("これから聞く本文(後半)】\nPART THREE", ctxs[2][1])
        self.assertIn("preview", out)

    def test_std_preview_listen_instruction_is_warn_not_blocking(self):
        # FZQI委任_06 L-1(Opus_E R-E4): LISTEN_INSTRUCTIONはZ Stdではblockingでなくlint_warn記録
        n = {"i": 0}

        def fn(client, prompt, context, model=None):
            n["i"] += 1
            return {"status": "OK", "text": "聞いてみましょう、羊飼いの話です。"}
        out = w.run_support_std(object(), self.parts, "FULL", ja_support_fn=fn)
        self.assertEqual(n["i"], 4)                                  # retryなし(4呼出)
        self.assertEqual(set(out["lint_warn"]), {"preview", "comment_1", "comment_2", "comment_3"})
        self.assertTrue(all(v == ["LISTEN_INSTRUCTION"] for v in out["lint_warn"].values()))
        # 関数の既定挙動は不変(明示optionなしはblocking)
        self.assertIn("LISTEN_INSTRUCTION", st.lint_support_text("聞いてみましょう、羊飼いの話です。", "ja"))


class StdSupportAdvMethodTest(unittest.TestCase):
    """FZQI委任_06 ②: Std Preview/Comment = Advanced方式の日本語適用(P-A)。"""
    OK = "羊飼いのメロスは王の前に立たされています。妹の結婚式が近く、気がかりです。"

    def setUp(self):
        self.parts = {1: "PART ONE SHEPHERD SCENE.", 2: "PART TWO RIVER SCENE.", 3: "PART THREE CITY SCENE."}

    def _run_std(self, text=None, **kw):
        seen = []

        def fn(client, role, ctx, model=None):
            seen.append((role, ctx, model))
            return {"status": "OK", "text": text or self.OK}
        out = w.run_support_std(object(), self.parts, "FULL", ja_support_fn=fn, **kw)
        return out, seen

    def test_input_composition_and_order_same_as_adv(self):
        _o, std_seen = self._run_std()
        adv_seen = []

        def fe(client, role, ctx, model=None):
            adv_seen.append((role, ctx, model))
            return {"status": "OK", "text": "A shepherd faces a ruler and a hard choice."}
        w.run_support_adv(object(), self.parts, "FULL", en_support_fn=fe)
        self.assertEqual(len(std_seen), 4)
        self.assertEqual([c for _r, c, _m in std_seen], [c for _r, c, _m in adv_seen])    # context構成が同一
        self.assertEqual([m for _r, _c, m in std_seen], [m for _r, _c, m in adv_seen])

    def test_roles_are_a2gen_objects_unmodified(self):
        import er003_v1_iran01_a2_generate as a2gen
        out, seen = self._run_std()
        roles = [r for r, _c, _m in seen]
        self.assertIs(roles[0], a2gen.COMMENT_1_ROLE)
        self.assertIs(roles[1], a2gen.COMMENT_2_ROLE)
        self.assertIs(roles[2], a2gen.COMMENT_2_ROLE)
        self.assertEqual(roles[3], a2gen.PREVIEW_ROLE.format(comment_1=out["comments"]["1"], comment_2=out["comments"]["2"]))
        self.assertNotIn(a2gen.COMMENT_3_ROLE, roles)
        self.assertNotIn(a2gen.COMMENT_4_ROLE, roles)
        self.assertTrue(all(m == "gpt-6-luna" for _r, _c, m in seen))

    def test_support_ja_principle_applied_via_build_support_prompt(self):
        import er003_v1_iran01_a2_generate as a2gen
        prompts = []

        class R:
            output_text = "羊飼いのメロスは王の前に立たされています。"
            model = "m"
            id = "r1"

        class C:
            class responses:
                @staticmethod
                def create(**kw):
                    prompts.append(kw["input"][1]["content"])
                    return R()
        w.run_support_std(C(), self.parts, "FULL")
        self.assertEqual(len(prompts), 4)
        self.assertTrue(all(a2gen.SUPPORT_JA_PRINCIPLE in p for p in prompts))

    def test_old_scene_transition_text_absent(self):
        _o, seen = self._run_std()
        joined = "\n".join(r + c for r, c, _m in seen)
        for old in ("ここまでの場面を聞き終えたところで、物語の続きに入ります", "さらに物語が進み、次の場面に入ります",
                    "これから聞く英文(下の【これから聞く部分】)に実際に書かれている事実のみ"):
            self.assertNotIn(old, joined)

    def test_family_c_path_and_old_preview_prompt_not_called(self):
        import er013_family_c_production_01 as fam_c
        import er026_family_z_fiction_production_runner_01 as er026
        orig = (fam_c.generate_family_c_a2_comment, er026.build_family_z_preview_prompt)

        def boom(*a, **k):
            raise AssertionError("旧経路が呼ばれた")
        fam_c.generate_family_c_a2_comment = boom
        er026.build_family_z_preview_prompt = boom
        try:
            out, _seen = self._run_std()
        finally:
            fam_c.generate_family_c_a2_comment, er026.build_family_z_preview_prompt = orig
        self.assertEqual(out["method"], w.STD_SUPPORT_METHOD_VERSION)

    def test_method_version_in_sha_and_adv_sha_unchanged(self):
        t, ps = "TEXT", "p" * 64
        adv_old = w.sha(t + ps)                                  # 従来式(委任_06以前)
        self.assertEqual(w.support_stage_input_sha("b1b", t, ps), adv_old)          # Adv shaは不変
        std = w.support_stage_input_sha("a2", t, ps)
        self.assertNotEqual(std, adv_old)
        self.assertEqual(std, w.sha(t + ps + "|" + w.STD_SUPPORT_METHOD_VERSION))
        old_ver = w.STD_SUPPORT_METHOD_VERSION
        try:
            w.STD_SUPPORT_METHOD_VERSION = "other_version"
            self.assertNotEqual(w.support_stage_input_sha("a2", t, ps), std)
            self.assertEqual(w.support_stage_input_sha("b1b", t, ps), adv_old)
        finally:
            w.STD_SUPPORT_METHOD_VERSION = old_ver

    def test_prior_ignored_when_method_mismatch(self):
        base = {"comments": {"1": "P1", "2": "P2"}, "attempts": {"comment_1": [], "comment_2": [], "preview": []},
                "preview": "PV"}
        out, seen = self._run_std(prior=dict(base))               # methodキー無し=旧方式
        self.assertEqual(len(seen), 4)
        self.assertNotEqual(out["comments"]["1"], "P1")
        self.assertNotEqual(out["preview"], "PV")
        out2, seen2 = self._run_std(prior=dict(base, method="old_family_c_v0"))
        self.assertEqual(len(seen2), 4)
        out3, seen3 = self._run_std(prior=dict(base, method=w.STD_SUPPORT_METHOD_VERSION))
        self.assertEqual(len(seen3), 1)
        self.assertEqual((out3["comments"]["1"], out3["preview"]), ("P1", "PV"))

    def test_old_method_cache_resume_is_provenance_mismatch_stop(self):
        t, ps = "TEXT", "p" * 64
        with tempfile.TemporaryDirectory() as d:
            prov = w.Provenance(f"{d}/p.json", "melos", "s" * 64)
            out_path = f"{d}/a2_support.json"
            old_sha = w.sha(t + ps)                                # 旧方式でのstage入力sha
            w.ensure_stage(prov, "support_a2", old_sha, out_path, lambda: ('{"old": 1}', {}))
            new_sha = w.support_stage_input_sha("a2", t, ps)
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.ensure_stage(prov, "support_a2", new_sha, out_path, lambda: ('{"new": 1}', {}))
            r = w.ensure_stage(prov, "support_a2", new_sha, out_path, lambda: ('{"new": 1}', {}), regenerate=True)
            self.assertEqual(r["status"], "generated")
            r2 = w.ensure_stage(prov, "support_a2", new_sha, out_path, lambda: ('{"x": 1}', {}))
            self.assertEqual(r2["status"], "reused")              # 新方式cacheは再利用される
            # Advは旧shaのまま再利用(影響なし)
            w.ensure_stage(prov, "support_b1b", w.support_stage_input_sha("b1b", t, ps), f"{d}/b1b.json",
                           lambda: ('{"adv": 1}', {}))
            r3 = w.ensure_stage(prov, "support_b1b", old_sha, f"{d}/b1b.json", lambda: ('{"adv": 2}', {}))
            self.assertEqual(r3["status"], "reused")

    def test_other_blocking_lint_codes_still_raise_and_listen_is_warn_only(self):
        for bad in ("このニュースは羊飼いの話です。", "メロスは間に合います。羊飼いの話です。", "セリヌンティウスが待っています。",
                    "Part 1では羊飼いが出ます。羊飼いの話です。"):
            with self.assertRaises(st.FamilyZLintStop, msg=bad):
                self._run_std(text=bad)
        # 英語出力(言語NG)もblocking
        with self.assertRaises(st.FamilyZLintStop):
            self._run_std(text="A shepherd faces a ruler.")
        # LISTEN_INSTRUCTION + blocking違反の併存はblocking
        with self.assertRaises(st.FamilyZLintStop):
            self._run_std(text="注目して聞いてください。このニュースは羊飼いの話です。")
        w_out = []
        v = st.lint_support_text("注目して聞いてください。羊飼いの話です。", "ja",
                                 allow_listen_instruction_as_warn=True, warn_out=w_out)
        self.assertEqual((v, w_out), ([], ["LISTEN_INSTRUCTION"]))
        # en側・既定は変わらない
        self.assertEqual(st.lint_support_text("A shepherd faces a ruler.", "en"), [])

    def test_overlap_notes_recorded_and_not_raising(self):
        texts = iter(["羊飼いは王様の前で立たされています。", "王様の前で立たされた羊飼いが戻ります。",
                      "川を渡る場面になります。", "羊飼いは王様の前で立たされた物語です。"])

        def fn(client, role, ctx, model=None):
            return {"status": "OK", "text": next(texts)}
        out = w.run_support_std(object(), self.parts, "FULL", ja_support_fn=fn)
        notes = out["overlap_notes"]
        self.assertIn("参考値", notes["note"])
        self.assertTrue(notes["ngram4_overlap"])                  # 重複あり(記録のみ・raiseしない)
        self.assertEqual(out["method"], w.STD_SUPPORT_METHOD_VERSION)
        # カタカナ固有名(メロス)は4-gram一致の対象外
        n2 = w.compute_support_overlap_notes({"preview": "メロスメロスメロス", "comment_1": "メロスメロスメロス"})
        self.assertEqual(n2["ngram4_overlap"], {})
        self.assertEqual(n2["katakana_names"]["preview"], ["メロスメロスメロス"])
        # 既存spoiler_ja辞書の出現を記録(結末語)
        n3 = w.compute_support_overlap_notes({"preview": "最後に間に合います", "comment_1": "ふつうの文です"})
        self.assertIn("間に合", n3["spoiler_ja_terms"]["preview"])


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

    def test_r2_name_note_does_not_stop(self):
        # 2026-10-12決定: 固有名詞はブロックしない(WARNのみ)。旧: NAME_RULE_VIOLATIONでSTOP
        with tempfile.TemporaryDirectory() as d:
            def hook(kw):
                if kw["input"][-1]["content"].startswith("Here is a short story"):
                    return "# T\n\n" + " ".join(["Dionysius"] * 450)
            res = self._run(d, hook, stages=("r0", "r1", "r2"))
            self.assertTrue(any("NAME_RULE_NOTE" in x for x in res["stages"]["r2"]["guardrails"]["warnings"]))

    def test_ensure_stage_downstream_input_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            prov = w.Provenance(f"{d}/p.json", "melos", "s" * 64)
            out = f"{d}/x.json"
            w.ensure_stage(prov, "plan_b1b", "A", out, lambda: ("{}", {}))
            r = w.ensure_stage(prov, "plan_b1b", "A", out, lambda: ("{}", {}))
            self.assertEqual(r["status"], "reused")
            with self.assertRaises(st.FamilyZProvenanceMismatchStop):
                w.ensure_stage(prov, "plan_b1b", "B", out, lambda: ("{}", {}))


class KpOuterRetryTest(unittest.TestCase):
    """委任_10: Z限定・暫定のKP外側retry(課金0、fake関数)。"""

    @staticmethod
    def _fakes(canon_script, red_script=None):
        calls = {"sel": [], "canon": 0, "red": 0}
        red_script = list(red_script or [])

        def sel(text, d, aid, lvl, process=None, diagnostic_note=None):
            calls["sel"].append(diagnostic_note)
            # KP-QUALITY-2ITEMS(2026-10-22): canonicalization後のCMU再確認(M2)を通るよう、fixtureの語はCMU登録語にする(旧: phrase1..5=数字入りでCMU未登録)。
            items = [{"rank": i, "display_phrase": w_} for i, w_ in enumerate(["apple pie", "brave dragon", "candle light", "dark forest", "early bird"], 1)]
            return {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": items}, "original_items": items}

        def canon(text, items, d, aid, process=None):
            st_ = canon_script[calls["canon"]]
            calls["canon"] += 1
            if st_ == "CANONICALIZATION_PASS":
                return {"status": st_, "merged": {"items": [dict(it, used_form=it["display_phrase"]) for it in items]}}
            return {"status": st_}

        def red(text, merged, d, aid, process=None):
            calls["red"] += 1
            s_ = red_script.pop(0) if red_script else "REDUNDANCY_OK"
            return {"status": s_, "duplicate_pairs": [{"rank_a": 1, "rank_b": 2, "reasoning": "r"}] if s_ == "REDUNDANCY_NG" else []}
        return calls, sel, canon, red

    def _run(self, d, canon_script, red_script=None):
        calls, sel, canon, red = self._fakes(canon_script, red_script)
        res = w.run_kp_with_outer_retry("text", d, "a", "A2", process="A2_SUPPORT",
                                        select_fn=sel, canon_fn=canon, redundancy_fn=red)
        return calls, res

    def test_pass_on_third_outer_attempt_with_generic_note_from_first(self):
        with tempfile.TemporaryDirectory() as d:
            calls, res = self._run(d, ["CANONICALIZATION_INVALID", "CANONICALIZATION_INVALID", "CANONICALIZATION_PASS"])
            self.assertEqual(len(calls["sel"]), 3)
            self.assertTrue(all(n and w.Z_KP_GENERIC_NOTE in n for n in calls["sel"]))
            self.assertEqual(res["canonicalization"]["status"], "CANONICALIZATION_PASS")
            log = json.load(open(f"{d}/outer_retry_log.json", encoding="utf-8"))
            self.assertEqual([a["canonicalization_status"] for a in log["attempts"]],
                             ["CANONICALIZATION_INVALID", "CANONICALIZATION_INVALID", "CANONICALIZATION_PASS"])
            self.assertTrue(os.path.isdir(f"{d}/outer_retry/attempt_3"))

    def test_exhausted_after_three_never_fourth(self):
        with tempfile.TemporaryDirectory() as d:
            calls, res = self._run(d, ["CANONICALIZATION_INVALID"] * 5)
            self.assertEqual(len(calls["sel"]), 3)
            self.assertEqual(calls["canon"], 3)
            self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
            self.assertEqual(w.Z_KP_OUTER_RETRY_MAX, 3)

    def test_note_is_generic_no_phrase_names(self):
        n = w.Z_KP_GENERIC_NOTE
        for forbidden in ("take my place", "my place", "someone's", "Melos", "メロス", "'", '"', "「"):
            self.assertNotIn(forbidden, n)
        self.assertIn("所有格人称代名詞", n)
        # 実呼出時のnoteにも個別phrase名(fake phrase1..5)が混入しない(最初のINVALID後でも同一note。fixture語=apple pie等)
        with tempfile.TemporaryDirectory() as d:
            calls, _ = self._run(d, ["CANONICALIZATION_INVALID", "CANONICALIZATION_PASS"])
            for note in calls["sel"]:
                self.assertEqual(note, n)
                for p_ in ("apple pie", "brave dragon", "candle light", "dark forest", "early bird"):
                    self.assertNotIn(p_, note)

    def test_redundancy_retry_separate_counter_and_appends_note(self):
        with tempfile.TemporaryDirectory() as d:
            calls, res = self._run(d, ["CANONICALIZATION_PASS", "CANONICALIZATION_PASS"], ["REDUNDANCY_NG", "REDUNDANCY_OK"])
            self.assertEqual(len(calls["sel"]), 2)
            self.assertTrue(calls["sel"][1].startswith(w.Z_KP_GENERIC_NOTE))
            self.assertGreater(len(calls["sel"][1]), len(w.Z_KP_GENERIC_NOTE))
            self.assertEqual(res["redundancy_qa"]["status"], "REDUNDANCY_OK")

    def test_ensure_stage_reuse_does_not_rerun(self):
        """b1b等のPASS済みstageは再実行しない(runnerを呼ばない)。"""
        with tempfile.TemporaryDirectory() as d:
            prov = w.Provenance(f"{d}/p.json", "melos", "s" * 64)
            out = f"{d}/key_phrases/b1b_result.json"
            w.ensure_stage(prov, "kp_b1b", "A", out, lambda: ("{}", {}))
            called = []
            r = w.ensure_stage(prov, "kp_b1b", "A", out, lambda: called.append(1) or ("{}", {}))
            self.assertEqual(r["status"], "reused")
            self.assertEqual(called, [])


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


def _body_n(n):
    return "# T\n\n" + " ".join(["word"] * n) + "\n"


class WordTarget400Test(unittest.TestCase):
    """2026-10-19 委任_04(ユーザー指示④): 目標400語・目安330-470(400±70)、WARNのみ。"""

    def test_constants_single_definition_and_er026_match(self):
        import er026_family_z_fiction_production_runner_01 as r26
        self.assertEqual(w.Z_WORD_TARGET, 400)
        self.assertEqual(w.Z_WORD_TOLERANCE, 70)
        self.assertEqual(w.TARGET_WORDS, 400)
        self.assertEqual(w.ADV_WORD_RANGE, (330, 470))
        self.assertEqual(w.STD_WORD_RANGE, (330, 470))
        self.assertEqual(r26.ACCEPT_WORD_RANGE, w.ADV_WORD_RANGE)

    def test_boundaries_warn_only_and_no_failures(self):
        def body(n):
            return _body_n(n)
        for n, warn in ((329, True), (330, False), (470, False), (471, True)):
            g = w.check_adv_guardrails(body(n))
            self.assertEqual(g["failures"], [], n)               # raise/STOP/failure化しない
            self.assertEqual(any("ADV_WORDS_OUT_OF_RANGE" in x for x in g["warnings"]), warn, n)
        adv = _story_text(8, 60)
        for n, warn in ((329, True), (330, False), (470, False), (471, True)):
            g = w.check_std_guardrails(body(n), adv)
            self.assertFalse(any("STD_WORDS_OUT_OF_RANGE" in x for x in g["failures"]), n)
            self.assertEqual(any("STD_WORDS_OUT_OF_RANGE" in x for x in g["warnings"]), warn, n)

    def test_prompts_contain_400_range_and_no_old_targets(self):
        p, _ = w.build_r0_prompt(_seed())
        self.assertIn("about 400 words (roughly 330-470", p)
        sp = w.build_std_prompt(_story_text(8, 60))
        self.assertIn("about 400 words", sp)
        self.assertIn("between 330 and 470", sp)
        rp = w.build_revise_prompt("BODY")
        self.assertIn("about 330-470 words", rp)
        s2 = dict(_seed(), conversion_plan="Totally different plan.")
        po, applied = w.build_r0_prompt(s2)
        self.assertIn("override_appended", applied)
        self.assertIn("about 400 words", po)
        self.assertIn("(roughly 330-470)", po)
        for prompt in (p, sp, rp, po):
            for old in ("350 words", "280-420", "280 and 420", "300–350"):
                self.assertNotIn(old, prompt)

    def test_old_targets_not_in_prompt_constants(self):
        texts = [w.R0_BLOCK_LENGTH_ADV, w._CONVERSION_OVERRIDE, w.REVISE_USER_TMPL, w.STD_PROMPT_TAIL]
        texts += [rep for _pat, rep in w._CONVERSION_SUBSTITUTIONS]   # 置換後文言(被置換正規表現は対象外)
        for t in texts:
            for old in ("350", "280", "420", "300"):
                self.assertNotIn(old, t, old)

    def test_melos_measured_counts_in_range_no_warn(self):
        # run_e2e_03実測(408/387語)は新範囲内=WARNなし(本文再生成不要の根拠)
        for n in (408, 387):
            g = w.check_adv_guardrails(_body_n(n))
            self.assertFalse(any("OUT_OF_RANGE" in x for x in g["warnings"]), n)


if __name__ == "__main__":
    unittest.main()
