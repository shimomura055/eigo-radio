# Round2 test: P5の静的不変条件(Coffee語句不在、6指標行逐語、P0同格文復活、出力契約再確認、Rule7への非干渉)、再利用整合、Round1資産不変
import json, os, sys, unittest
sys.path.insert(0, os.getcwd())
import er064_kp_int_01_prompts as PR
import er064_kp_int_01_test_01 as T1
import er064_kp_opt_01_prompt_build as B1

O2 = "er064_output/kp_integrated_opt_01/round2"
P0_SENTENCE = "未知単語、題材固有表現、短い複数語パターン、比喩・感情表現を同格の候補として扱ってください。構成語から意味を容易に推測できる透明表現は、記事上重要でも優先度を下げてください。"
RULE7_WORDS = ["所有格", "one's", "person", "代名詞", "his", "their", "活用形", "人称"]


class P5Rules(unittest.TestCase):
    def full(self, lv):
        return PR.head("P5", lv) + PR.tail("P5")

    def test_p0_sentence_restored_verbatim(self):
        self.assertIn(P0_SENTENCE, B1.before_static())  # 元がProduction逐語であること
        for lv in ("std", "adv"):
            self.assertIn(P0_SENTENCE, self.full(lv))

    def test_established_figurative_rule_present(self):
        for lv in ("std", "adv"):
            t = self.full(lv)
            self.assertIn("辞書の見出しになっている定着表現", t)
            self.assertIn("擬人的", t)
            self.assertIn("定着表現として評価", t)

    def test_low_priority_suppression_from_p3_kept(self):
        s = "学習者がすでに知っていそうな基本表現や、構成語から意味が分かる透明な表現は、価値の高い候補が残っている限り枠を使わないでください。候補が乏しいときは選んでかまいません。"
        self.assertIn(s, PR.P3)
        self.assertIn(s, PR.head("P5", "std"))
        self.assertIn("選ばなかった候補の中に、初見で理解しにくく、学んだあとの再利用価値も高いものが残っていないか", PR.head("P5", "std"))

    def test_output_contract_reconfirmation(self):
        for lv in ("std", "adv"):
            t = PR.tail("P5")
            self.assertIn("normalization_note", t)
            self.assertIn("括弧", t)
            self.assertIn("backup_item", t)
            self.assertIn("source_candidate_id", t)
            self.assertIn("【日本語グロス】", PR.head("P5", lv))

    def test_line_a_and_contract_terms(self):
        for lv in ("std", "adv"):
            h = PR.head("P5", lv)
            self.assertIn(PR.LINE_A, h)
            for term in ("ちょうど5個", 'key_phrase_role="topic"', 'key_phrase_role="important"', "1〜5語"):
                self.assertIn(term, h)

    def test_no_coffee_words(self):
        for lv in ("std", "adv"):
            t = self.full(lv).lower()
            for w in T1.BAN_PROMPT:
                self.assertNotIn(w, t, w)

    def test_rule7_non_interference(self):
        # 学ぶ単位段落(動詞は基本形へ)はP3と同一、P5に所有格/人称置換に触れる指示を追加していない
        def unit(s):
            a = s.index("【学ぶ単位】"); b = s.index("【役割】")
            return s[a:b]
        self.assertEqual(unit(PR.P3), unit(PR.P5))
        for lv in ("std", "adv"):
            t = self.full(lv)
            for w in RULE7_WORDS:
                self.assertNotIn(w, t, w)
        self.assertIn("動詞は本文の時制を残さず基本形へ直してください", PR.P5)

    # TEST-HYGIENE-02(2026-10-22): tiktokenは本体.venv非導入(隔離環境のTIKTOKEN_PATH運用)。未導入環境ではskip。
    @unittest.skipUnless(os.environ.get("TIKTOKEN_PATH") or __import__("importlib.util").util.find_spec("tiktoken"),
                         "tiktoken未導入(隔離環境のみ。TIKTOKEN_PATHを指定すれば実行)")
    def test_tokens_vs_p0(self):
        base = PR.tokens(PR.head("P0", "std")) + PR.tokens(PR.tail("P0"))
        for lv in ("std", "adv"):
            n = PR.tokens(PR.head("P5", lv)) + PR.tokens(PR.tail("P5"))
            self.assertLessEqual(n, base * 1.11, f"{lv} {n} vs {base}")

    def test_prompts_r2_sha(self):
        pj = json.load(open(f"{O2}/prompts_r2.json", encoding="utf-8"))
        for pid in ("P0", "P3", "P5"):
            for lv in ("std", "adv"):
                self.assertEqual(pj["prompts"][pid][lv]["head_sha256"], PR.sha(PR.head(pid, lv)))
                self.assertEqual(pj["prompts"][pid][lv]["tail_sha256"], PR.sha(PR.tail(pid)))
        self.assertTrue(pj["round1_sha_match_P0_P3"])


class ReuseAndR1(unittest.TestCase):
    def test_reuse_check_all_match(self):
        p = f"{O2}/reuse_check_r2.json"
        self.assertTrue(os.path.exists(p))
        self.assertTrue(json.load(open(p, encoding="utf-8"))["all_match"])

    def test_state_guard_if_present(self):
        p = f"{O2}/state_guard_r2.json"
        if not os.path.exists(p):
            self.skipTest("未作成")
        for k, v in json.load(open(p, encoding="utf-8")).items():
            if k.startswith("unchanged_"):
                self.assertTrue(v, k)

    def test_cost_within_cap(self):
        p = f"{O2}/cost_r2.json"
        if not os.path.exists(p):
            self.skipTest("未作成")
        c = json.load(open(p, encoding="utf-8"))
        self.assertLessEqual(c["cumulative_jpy"], 70.0)
        self.assertTrue(all(x["model"] == "gpt-6-luna" for x in c["calls"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
