# ============================================================
# er064_kp_idiom_trial_01_test_01.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B 単体test(API・ネットワーク呼出なし)
# 実行: PYTHONPATH=. .venv/Scripts/python.exe -m unittest er064_kp_idiom_trial_01_test_01 -v
# ============================================================
import itertools
import os
import random
import re
import unittest

import er003_key_words_canonicalization as kc
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref
import er064_kp_idiom_trial_01_extractor as X
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
import er064_kp_idiom_trial_01_select as S

INPUTS = "er064_output/kp_idiom_trial_01/phase_a/inputs"
GEN = "generalize_person_dependent_reference"


def _units(text):
    return core.build_sentence_units(text)


class B1CanonicalizationRule7(unittest.TestCase):
    """Rule7(`_is_valid_person_generalization`、KEY_PHRASE_MAX_WORDS=5)の通過/INVALIDを固定する。
    Rule7の表は変更しない(OPEN-310、別管理ID)。ここは『現状の挙動』の固定test。"""

    def v(self, key, display, span, reason=None):
        return kc.validate_canonicalization_item(key, display, span, normalization_reason=reason)["ok"]

    def test_pumps_its_fist_to_pump_ones_fist_is_INVALID_when_display_keeps_inflection(self):
        # display_phrase=`pumps its fist`のままだと、pumps->pump(活用形の基本形化)は表にないためINVALID
        self.assertFalse(self.v("pump one's fist", "pumps its fist", "pumps its fist", GEN))

    def test_pump_its_fist_to_pump_ones_fist_is_PASS_when_display_is_base_form(self):
        # display_phrase=`pump its fist`(動詞のみ基本形、Template L7)ならits->one'sの1対1置換でPASS
        self.assertTrue(self.v("pump one's fist", "pump its fist", "pumps its fist", GEN))

    def test_pump_ones_fist_requires_generalize_reason(self):
        # normalization_reasonが違うとINVALID(reason依存)
        self.assertFalse(self.v("pump one's fist", "pump its fist", "pumps its fist", "other"))

    def test_keeping_inflection_with_ones_is_PASS(self):
        self.assertTrue(self.v("pumps one's fist", "pumps its fist", "pumps its fist", GEN))

    def test_unchanged_display_is_PASS(self):
        self.assertTrue(self.v("pump its fist", "pump its fist", "pumps its fist"))

    def test_pull_my_leg_to_pull_someones_leg_is_INVALID(self):
        # 表: my -> {one's} のみ。someone'sは許可されない
        self.assertFalse(self.v("pull someone's leg", "pull my leg", "pulling my leg", GEN))

    def test_pull_my_leg_to_pull_ones_leg_is_PASS(self):
        self.assertTrue(self.v("pull one's leg", "pull my leg", "pulling my leg", GEN))

    def test_pull_your_leg_to_pull_someones_leg_is_PASS(self):
        self.assertTrue(self.v("pull someone's leg", "pull your leg", "pulling your leg", GEN))

    def test_six_word_phrase_is_INVALID_by_max_words(self):
        self.assertEqual(kc.KEY_PHRASE_MAX_WORDS, 5)
        r = kc.validate_canonicalization_item("mark the date on your calendar", "mark the date on your calendar",
                                              "mark the date on your calendar")
        self.assertFalse(r["ok"])

    def test_mark_the_date_three_words_is_PASS(self):
        self.assertTrue(self.v("mark the date", "mark the date", "mark the date on your calendar"))


class AMatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = core.load_group1_dbs()
        cls.pats = M.build_pattern_index(cls.dbs)

    def hits(self, sentence):
        toks = _units(sentence)[0]["tokens"]
        return {(h["surface"].lower(), h["title"]) for h in M.match_sentence_tokens(toks, self.pats)}

    def test_recovers_possessive_idioms(self):
        self.assertIn(("bit her tongue", "bite one's tongue"), self.hits("She bit her tongue and said nothing."))
        self.assertTrue(any(t == "pull someone's leg" for s, t in self.hits("You are pulling my leg.")))
        self.assertIn(("lost her temper", "lose one's temper"), self.hits("She lost her temper at the meeting."))

    def test_no_object_slot_at_title_end(self):
        titles = {p["title"] for p in self.pats}
        self.assertNotIn("know someone", titles)
        for p in self.pats:
            self.assertNotIn(M.PLACE.get(p["toks"][-1]), ("OBJ",), p["title"])

    def test_no_something_and_no_possessive_s_titles(self):
        for p in self.pats:
            self.assertNotIn("something", p["toks"])
            for t in p["toks"]:
                if "'s" in t:
                    self.assertIn(t, M.PLACE)

    def test_requires_two_content_words(self):
        for p in self.pats:
            content = [t for t in p["toks"] if t not in M.PLACE and t not in M._CLOSED]
            self.assertGreaterEqual(len(content), 2, p["title"])

    def test_candidates_are_additive_only(self):
        units = _units("Please do not spill the beans. She bit her tongue.")
        c = M.placeholder_candidates(units, self.pats, self.dbs, existing_canonicals=set())
        surfaces = {x["surface_form"].lower() for x in c}
        self.assertIn("bit her tongue", surfaces)
        self.assertNotIn("spill the beans", surfaces)  # 既存DBヒットは置換・重複しない
        for x in c:
            self.assertEqual(x["evidence"], "placeholder_title")
            self.assertTrue(x["matched_title"])
        c2 = M.placeholder_candidates(units, self.pats, self.dbs, existing_canonicals={"bit her tongue"})
        self.assertNotIn("bit her tongue", {x["surface_form"].lower() for x in c2})


class B4ExtractorVerification(unittest.TestCase):
    TEXT = ("# Title\n\nTom said the new plan is a long shot, but he kept going. "
            "Then, out of the blue, Anna called. We left the room, quietly.\n")

    def setUp(self):
        self.units = _units(self.TEXT)

    def test_verify_ok_and_context(self):
        r = X.verify_span("out of the blue", self.units)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["candidate"]["surface_form"], "out of the blue")
        self.assertEqual(r["candidate"]["evidence"], "llm_noncompositional")

    def test_case_insensitive_surface_taken_from_article(self):
        r = X.verify_span("A LONG SHOT", self.units)
        self.assertTrue(r["ok"])
        self.assertEqual(r["candidate"]["surface_form"], "a long shot")

    def test_rejects_not_in_article(self):
        self.assertEqual(X.verify_span("a short cut", self.units)["reason"], "not_in_article_tokens")

    def test_rejects_modified_inflection(self):
        # 本文のまま書く契約。基本形化・言い換えは本文に無いので拒否される
        self.assertEqual(X.verify_span("keep going on", self.units)["reason"], "not_in_article_tokens")

    def test_rejects_crossing_punctuation(self):
        r = X.verify_span("room quietly", self.units)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "crosses_punctuation_or_format")

    def test_rejects_single_word_and_too_long(self):
        self.assertEqual(X.verify_span("plan", self.units)["reason"], "token_count_out_of_range")
        self.assertEqual(X.verify_span("one two three four five six", self.units)["reason"],
                         "token_count_out_of_range")

    def test_rejects_all_closed_class(self):
        self.assertFalse(X.verify_span("in the", self.units)["ok"])

    def test_empty_output_is_allowed(self):
        r = X.build_llm_candidates({"items": []}, self.units, set())
        self.assertEqual(r["accepted"], [])
        self.assertEqual(r["raw_item_count"], 0)

    def test_dedupe_cap_and_additive(self):
        items = [{"span": "out of the blue", "kind": X.KINDS[0], "reason_en": "x"},
                 {"span": "Out of the blue", "kind": X.KINDS[0], "reason_en": "x"},
                 {"span": "a long shot", "kind": X.KINDS[0], "reason_en": "x"},
                 {"span": "kept going", "kind": X.KINDS[2], "reason_en": "x"}]
        r = X.build_llm_candidates({"items": items}, self.units, {"a long shot"}, cap=5)
        self.assertEqual([c["canonical_form"] for c in r["accepted"]], ["out of the blue", "kept going"])
        self.assertEqual(len(r["duplicate_of_existing"]), 2)
        r2 = X.build_llm_candidates({"items": items}, self.units, set(), cap=1)
        self.assertEqual(len(r2["accepted"]), 1)
        self.assertTrue(any(x["reason"] == "over_cap" for x in r2["rejected"]))

    def test_attach_context_id_for_llm_candidate(self):
        import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
        c = X.verify_span("out of the blue", self.units)["candidate"]
        res = s1v3.attach_compact_context([c], self.units)
        self.assertTrue(res["shortlist"][0]["context_sentence_id"])
        sid = res["shortlist"][0]["context_sentence_id"]
        self.assertIn("out of the blue", res["sentence_reference"][sid].lower())


@unittest.skipUnless(os.path.exists(f"{INPUTS}/v4_std_article.md"), "Phase A input missing")
class B3ShortlistInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = core.load_group1_dbs()
        cls.pats = M.build_pattern_index(cls.dbs)
        cls.bases = {}
        cls.texts = {}
        for lv in ("std", "adv"):
            t = open(f"{INPUTS}/v4_{lv}_article.md", encoding="utf-8").read()
            cls.texts[lv] = t
            cls.bases[lv] = P.load_base(t)  # キャッシュ済み前提(未キャッシュなら公開Wiktionary APIを使う)

    def _fake_llm(self, lv, spans):
        units = self.bases[lv]["stage1"]["sentence_units"]
        out = []
        for sp in spans:
            v = X.verify_span(sp, units)
            if v["ok"]:
                out.append(v["candidate"])
        return out

    def test_v0_is_production_shortlist_object(self):
        for lv in ("std", "adv"):
            v0 = P.build_variant_shortlist(self.bases[lv], "V0")
            self.assertIs(v0["shortlist_info"], self.bases[lv]["shortlist_info"])

    def test_invariant_v0_subset_of_v1_v2_v3(self):
        for lv in ("std", "adv"):
            base = self.bases[lv]
            units = base["stage1"]["sentence_units"]
            existing = P._canon_set(base["stage1"])
            pc = M.placeholder_candidates(units, self.pats, self.dbs, existing)
            rc = M.rule_possessive_pattern_candidates(units, self.dbs, existing)
            # 任意のllm候補(本文中の連続2-3語を数本)
            toks = units[0]["tokens"]
            lc = self._fake_llm(lv, [" ".join(toks[i:i + 3]) for i in range(0, min(len(toks) - 2, 12), 2)])
            v0 = P.shortlist_keys(P.build_variant_shortlist(base, "V0")["shortlist_info"])
            for variant, kw in (("V1", {"placeholder_cands": pc}),
                                ("V2", {"placeholder_cands": pc, "llm_cands": lc}),
                                ("V3", {"rule_cands": rc})):
                vk = P.shortlist_keys(P.build_variant_shortlist(base, variant, **kw)["shortlist_info"])
                self.assertTrue(set(v0) <= set(vk), (lv, variant))
                # 先頭はV0と完全に同じ順序(追加は末尾の予約枠のみ)
                self.assertEqual(vk[:len(v0)], v0)
                self.assertLessEqual(len(vk) - len(v0), P.RESERVED_SLOT_CAP)

    def test_reserved_only_llm_or_placeholder_and_outside_cap15(self):
        lv = "adv"
        base = self.bases[lv]
        units = base["stage1"]["sentence_units"]
        toks = units[1]["tokens"]
        lc = self._fake_llm(lv, [" ".join(toks[i:i + 2]) for i in range(0, min(len(toks) - 1, 14))])
        r = P.build_variant_shortlist(base, "V2", llm_cands=lc)
        for c in r["reserved"]:
            self.assertIn(c["evidence"], ("llm_noncompositional", "placeholder_title"))
        self.assertLessEqual(len(r["reserved"]), P.RESERVED_SLOT_CAP)
        # phrase_survivorsのcap15は変更されない(V0と同じphrase_included_count + 予約枠)
        v0 = base["shortlist_info"]
        self.assertEqual(r["shortlist_info"]["phrase_included_count"], v0["phrase_included_count"] + len(r["reserved"]))
        self.assertLessEqual(v0["phrase_included_count"], 15)

    def test_reserved_order_deterministic_and_input_order_independent(self):
        lv = "std"
        base = self.bases[lv]
        units = base["stage1"]["sentence_units"]
        toks = units[2]["tokens"]
        lc = self._fake_llm(lv, [" ".join(toks[i:i + 2]) for i in range(0, min(len(toks) - 1, 14))])
        self.assertGreaterEqual(len(lc), 3)
        a = [c["canonical_form"] for c in P.build_variant_shortlist(base, "V2", llm_cands=lc)["reserved"]]
        random.Random(1).shuffle(lc)
        b = [c["canonical_form"] for c in P.build_variant_shortlist(base, "V2", llm_cands=lc)["reserved"]]
        self.assertEqual(a, b)

    def test_reserved_sort_key_rarity_then_alphabet(self):
        mk = lambda s, ev="llm_noncompositional": {"surface_form": s, "canonical_form": s, "evidence": ev}
        cs = [mk("the table"), mk("a table"), mk("a xylophone")]
        out = sorted(cs, key=P.reserved_sort_key)
        # xylophone(希少)が先、同じ希少度のtable同士はalphabet
        self.assertEqual([c["canonical_form"] for c in out], ["a xylophone", "a table", "the table"])
        # 由来優先: llm < placeholder
        self.assertLess(P.reserved_sort_key(mk("the table")), P.reserved_sort_key(mk("a table", "placeholder_title")))

    def test_cut_online_hits_flag_is_off_by_default(self):
        base = self.bases["adv"]
        r = P.build_variant_shortlist(base, "V1", placeholder_cands=[])
        self.assertEqual(r["reserved"], [])

    def test_trial_message_with_prod_guidance_equals_production_message(self):
        for lv in ("std", "adv"):
            base = self.bases[lv]
            si = base["shortlist_info"]
            ids = src_ref.assign_candidate_ids(si["shortlist"])
            corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], si["sentence_reference"])
            swi = corr["shortlist_with_ids"]
            static = selector01.extract_static_instructions(S.bk.load_prompt_template())
            title = selector01.extract_article_title(self.texts[lv])
            prod_msg = src_ref.build_lightweight_user_message(title, swi, si["sentence_reference"], static)
            trial_msg = S.build_message(title, swi, si["sentence_reference"], static, S.prod_guidance())
            self.assertEqual(prod_msg, trial_msg)


class D5GuidanceAndNoHardcode(unittest.TestCase):
    def test_guidance_replaces_exactly_one_block_and_keeps_rest(self):
        prod_g = S.prod_guidance()
        for lv in ("std", "adv"):
            tg = S.trial_guidance(lv)
            self.assertNotIn("区分を優先してください", tg)
            self.assertIn("区分を優先してください", prod_g)
            # 置換対象外の維持項目
            for keep in ("少なくとも1個は、[重要な単語・単語群候補]区分", "CEFR難易度・語彙レベルを主要な判断軸にしない",
                         "source_candidate_id", "backup_item", "候補に\n  無い新しい表現を作らない"):
                self.assertIn(keep, tg, keep)
            self.assertEqual(tg.count("llm_noncompositional"), 1)

    def test_shared_template_untouched(self):
        t = open("er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt", encoding="utf-8").read()
        self.assertIn("構成語から意味を容易に推測できる透明表現は、記事上重要でも優先度を下げてください", t)

    FORBIDDEN = re.compile(r"pump|fist|calendar|wallet|mark the date|coffee|barista|latte", re.I)

    def test_no_coffee_specific_strings_in_prompts_and_trial_code(self):
        texts = {"extractor_prompt": X.prompt_template(), "guidance_std": S.trial_guidance("std"),
                 "guidance_adv": S.trial_guidance("adv")}
        for f in ("matcher", "pipeline", "extractor", "select"):
            src = open(f"er064_kp_idiom_trial_01_{f}.py", encoding="utf-8").read()
            texts[f"code_{f}"] = src
        for name, t in texts.items():
            self.assertIsNone(self.FORBIDDEN.search(t), (name, self.FORBIDDEN.search(t)))

    def test_extractor_prompt_examples_are_generic(self):
        t = X.prompt_template()
        self.assertNotIn("pump", t.lower())
        self.assertIn("items を空配列", t)  # 0件出力の明示許可


if __name__ == "__main__":
    unittest.main()
