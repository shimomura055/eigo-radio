# -*- coding: utf-8 -*-
import os, sys, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
import er052_open233_b3_variant_dev_01 as dev
import er019_family_x_storyline_b3_fact_selection_01 as b3

LEDGER = "[VERIFIED] A-1: dummy\n  scope: x"
BASE = b3.build_user_prompt("TOPIC_X", LEDGER)


class T(unittest.TestCase):
    def test_variant_names(self):
        self.assertEqual(dev.VARIANT_NAMES, ("V0", "V1", "V2", "V3", "V5", "V6"))

    def test_v0_identical(self):
        self.assertEqual(dev.apply_variant(BASE, "V0"), BASE)
        with dev.patched_b3_variant("V0", b3):
            self.assertEqual(b3.build_user_prompt("TOPIC_X", LEDGER), BASE)

    def test_blocks_included(self):
        for v in ("V1", "V2", "V3", "V5", "V6"):
            out = dev.apply_variant(BASE, v)
            self.assertTrue(out.endswith(dev.VARIANTS[v]["append"]), v)
            self.assertNotEqual(out, BASE)

    def test_phrase_kept_or_replaced(self):
        for v in ("V1", "V2", "V3", "V5"):
            self.assertIn(dev.BASE_PHRASE, dev.apply_variant(BASE, v))
        for v in ("V6",):
            self.assertNotIn(dev.BASE_PHRASE, dev.apply_variant(BASE, v))

    def test_composition(self):
        a3 = dev.VARIANTS["V3"]["append"]
        self.assertIn(dev.BLOCK_V1, a3)
        self.assertIn(dev.BLOCK_V2, a3)
        self.assertIn(a3, dev.VARIANTS["V5"]["append"])

    def test_v5_is_v3_plus_tail_block_only(self):
        self.assertEqual(dev.VARIANTS["V5"]["replace"], [])
        self.assertEqual(dev.VARIANTS["V5"]["append"], dev.VARIANTS["V3"]["append"] + "\n\n" + dev.BLOCK_V5_EXTRA)
        self.assertEqual(dev.apply_variant(BASE, "V5"), dev.apply_variant(BASE, "V3") + "\n\n" + dev.BLOCK_V5_EXTRA)

    def test_v5_features(self):
        a = dev.VARIANTS["V5"]["append"]
        for k in ("示されていない", "未提示", "numeric_scope", "禁止notes"):
            self.assertIn(k, a)
        e = dev.BLOCK_V5_EXTRA
        for k in ("逐語", "fact_id", "5件", "採用の有無", "引用", "簡潔に"):
            self.assertNotIn(k, e)

    def test_forbidden_words(self):
        for v, spec in dev.VARIANTS.items():
            txt = spec["append"] + "".join(n for _, n in spec["replace"])
            for w in dev.FORBIDDEN_WORDS:
                self.assertNotIn(w, txt, f"{v}:{w}")

    def test_restore_after_context_and_on_exception(self):
        orig = b3.build_user_prompt
        with dev.patched_b3_variant("V3", b3):
            self.assertIsNot(b3.build_user_prompt, orig)
            self.assertIn("単一因果", b3.build_user_prompt("t", LEDGER))
        self.assertIs(b3.build_user_prompt, orig)
        with self.assertRaises(RuntimeError):
            with dev.patched_b3_variant("V6", b3):
                raise RuntimeError("x")
        self.assertIs(b3.build_user_prompt, orig)

    def test_sent_log_and_sha(self):
        sent = []
        with dev.patched_b3_variant("V1", b3, sent):
            p = b3.build_user_prompt("t", LEDGER)
        self.assertEqual(sent, [dev.sha256_text(p)])
        self.assertEqual(len({dev.instruction_sha(v) for v in dev.VARIANT_NAMES}), 6)

    def test_invalid_variant(self):
        with self.assertRaises(ValueError):
            with dev.patched_b3_variant("V4", b3):
                pass

    def test_developer_message_and_schema_untouched(self):
        msg, sch = b3.DEVELOPER_MESSAGE, b3.STORYLINE_B3_JSON_SCHEMA
        with dev.patched_b3_variant("V5", b3):
            self.assertIs(b3.DEVELOPER_MESSAGE, msg)
            self.assertIs(b3.STORYLINE_B3_JSON_SCHEMA, sch)

    def test_provenance(self):
        p = dev.provenance("V5", "abc")
        self.assertEqual(p["variant"], "V5")
        self.assertEqual(p["full_prompt_sha256"], dev.sha256_text("abc"))


if __name__ == "__main__":
    unittest.main()
