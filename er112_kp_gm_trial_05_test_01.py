# -*- coding: utf-8 -*-
"""委任_22 Trial_05 DEV: API 0のtest(message/schema組立・Production互換・旧制約句の撤去・Production非編集)。"""
import json, unittest
import er112_kp_gm_trial_05 as T5
import er112_kp_gm_trial_04_gen as G
import er003_key_words_gloss_alignment as ga


class T(unittest.TestCase):
    def setUp(self):
        A = T5.all_kps5()
        self.kp = [A["draw a line"]]
        self.tgt = G._targets(self.kp)

    def test_x_messages_have_no_reusable_constraint(self):
        for arm in ("X1", "X2"):
            _, msg, _ = T5.build(arm, self.tgt, self.kp[0]["article"])
            self.assertNotIn("他の文脈でも再利用できる", msg)
            self.assertNotIn("他の記事でも同じ意味", msg)
            self.assertNotIn("辞書に複数の語義がある表現で", msg)
            self.assertIn("本文固有の固有名詞・数値・この記事だけの出来事はグロスに入れないでください", msg)

    def test_x2_schema_order_and_production_fields(self):
        req = T5.x_schema("X2")["schema"]["properties"]["items"]["items"]["required"]
        i = req.index("japanese_gloss")
        self.assertEqual(req[i - 3:i], ["meaning_in_text_en", "naive_ja", "naive_ja_conveys"])
        for f in ("current_gloss_consistent", "qa_reflects_all_key_phrase_words", "added_word_mappings", "reasoning"):
            self.assertIn(f, req)
        self.assertNotIn("meaning_in_text_en", T5.x_schema("X1")["schema"]["properties"]["items"]["items"]["required"])
        self.assertEqual(set(T5.x_schema("X1")["schema"]["properties"]["items"]["items"]["required"]), set(ga.GLOSS_ALIGNMENT_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["required"]))

    def test_x2_yes_route_anti_anchoring_rule(self):
        _, msg, _ = T5.build("X2", self.tgt, self.kp[0]["article"])
        self.assertIn("naive_jaをそのまま写さず", msg)

    def test_b0_is_production_message(self):
        _, msg, schema = T5.build("B0", self.tgt, self.kp[0]["article"])
        self.assertEqual(msg, ga.build_user_message_corrected(self.tgt, self.kp[0]["article"]))
        self.assertIs(schema, ga.GLOSS_ALIGNMENT_JSON_SCHEMA)

    def test_person_text_replaced_in_x(self):
        A = T5.all_kps5()
        kp = [A["reach for someone's wallet"]] if "reach for someone's wallet" in A else None
        if kp is None:
            self.skipTest("no person KP")
        _, msg, _ = T5.build("X1", G._targets(kp), kp[0]["article"])
        self.assertNotIn("辞書に複数の語義がある表現で", msg)
        self.assertIn("人称の指示対象を決めるためには使わないでください", msg)

    def test_no_production_import_side_effect(self):
        self.assertTrue(str(T5.OUT5).endswith("kp_gm_trial_05"))


if __name__ == "__main__":
    unittest.main()
