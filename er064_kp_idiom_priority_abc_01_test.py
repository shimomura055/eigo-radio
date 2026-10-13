import unittest

import er003_b1_p2_keywords as bk
import er030_key_phrase_db_hybrid_selector_01 as sel
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref
import er064_kp_idiom_priority_abc_01_run as R
import er064_kp_idiom_trial_01_select as S


class T(unittest.TestCase):
    def test_line_a_verbatim_in_template(self):
        self.assertEqual(bk.load_prompt_template().count(R.LINE_A), 1)

    def test_a_equals_production_static(self):
        R._tl.version = "A"
        a = sel.extract_static_instructions(bk.load_prompt_template())
        R._tl.version = None
        self.assertEqual(a, R._orig_static(bk.load_prompt_template()))

    def test_b_c_differ_only_in_priority_line(self):
        base = R._orig_static(bk.load_prompt_template())
        for v in "BC":
            R._tl.version = v
            s = sel.extract_static_instructions(bk.load_prompt_template())
            R._tl.version = None
            self.assertNotEqual(s, base)
            self.assertEqual(s.replace("優先順位は、" + R.PRIO[v] + "の順です。", R.LINE_A), base)

    def test_prod_guidance_unchanged(self):
        self.assertEqual(S.prod_guidance(), src_ref._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE)

    def test_message_equals_production_builder_without_llm_cands(self):
        import er064_kp_idiom_trial_01_pipeline as P
        t = open(R.ART["std"], encoding="utf-8").read()
        base = P.load_base(t)
        info = P.build_variant_shortlist(base, "V0")["shortlist_info"]
        ids = src_ref.assign_candidate_ids(info["shortlist"])
        corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], info["sentence_reference"])
        st = R._orig_static(bk.load_prompt_template())
        title = sel.extract_article_title(t)
        mine = S.build_message(title, corr["shortlist_with_ids"], info["sentence_reference"], st, S.prod_guidance())
        prod = src_ref.build_lightweight_user_message(title, corr["shortlist_with_ids"], info["sentence_reference"], st)
        self.assertEqual(mine, prod)


if __name__ == "__main__":
    unittest.main()
