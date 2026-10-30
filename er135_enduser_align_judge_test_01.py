# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A: 対応づけのLLM確認(M8、er135_enduser_align_judge_01)のtest。API 0(LLMはmock)。
M8は実装のみ。既定では呼ばれない(judge=None)ことと、呼ぶ場合も『DP候補の可否だけ』で新しい対応を作らないこと、応答不正は全て不採用であることを検査する。

実行: .venv\\Scripts\\python.exe -m pytest er135_enduser_align_judge_test_01.py -q
"""
import inspect
import json
import sys
import unittest
from pathlib import Path

import er135_enduser_align_01 as AL
import er135_enduser_align_judge_01 as J
import er135_enduser_page_01 as E

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "docs" / "research" / "ENDUSER-EN-JA-LINKED-HIGHLIGHT-01" / "gold"
sys.path.insert(0, str(ROOT / "tools"))


class J1_Parse(unittest.TestCase):
    def test_parse_ok_and_failures(self):
        self.assertEqual(J.parse('{"results":[{"id":1,"ok":true},{"id":2,"ok":false}]}', 2), [True, False])
        self.assertEqual(J.parse('```json\n{"results":[{"id":1,"ok":true}]}\n```', 1), [True])
        for bad in ("", "not json", '{"results":[{"id":1,"ok":true}]}', '{"results":[{"id":2,"ok":true},{"id":1,"ok":true}]}',
                    '{"results":[{"id":1,"ok":"yes"},{"id":2,"ok":true}]}', '{"x":1}', '[1,2]'):
            with self.assertRaises(J.JudgeError, msg=bad):
                J.parse(bad, 2)

    def test_prompt_lists_numbered_sentences_and_pairs(self):
        p = J.build_prompt(["A one.", "B two."], ["あ。", "い。", "う。"], [([0, 1], (0, 2)), ([1], (2, 3))])
        for s in ("E1. A one.", "E2. B two.", "J3. う。", "1. 英語 E1・E2 ↔ 日本語 J1・J2", "2. 英語 E2 ↔ 日本語 J3"):
            self.assertIn(s, p)

    def test_make_judge_requires_llm_and_failures_reject_all(self):
        with self.assertRaises(ValueError):
            J.make_judge(None)
        j = J.make_judge(lambda prompt: "garbage")
        self.assertEqual(j(["a"], ["あ"], [([0], (0, 1)), ([0], (0, 1))]), [False, False])
        self.assertEqual(j.stats["calls"], 1)
        self.assertEqual(len(j.stats["failures"]), 1)
        j2 = J.make_judge(lambda prompt: json.dumps({"results": [{"id": i, "ok": True} for i in range(1, 13)]}))
        self.assertEqual(sum(j2(["a"], ["あ"], [([0], (0, 1))] * 14)), 12)           # 12件ずつ分割: 2回目(2件)の応答件数不一致=その2件は不採用
        self.assertEqual(j2.stats["calls"], 2)

    def test_routing_and_default_off(self):
        import er006_model_routing_contract_01 as routing
        self.assertEqual(routing.PROCESS_MODEL_MAP[J.PROCESS], routing.SUPPORT_MODEL)
        self.assertIsNone(inspect.signature(AL.align_paragraph).parameters["judge"].default)
        self.assertIsNone(inspect.signature(AL.build_article_align).parameters["judge"].default)
        self.assertNotIn("judge", inspect.getsource(E.hook_run) + inspect.getsource(E.produce_enduser) + inspect.getsource(E.build_enduser))
        self.assertNotIn("judge", "".join(AL.PARAMS.keys()).replace("judge_tau", ""))


@unittest.skipUnless((GOLD / "ja_align_embed_v1.jsonl").is_file() and any(GOLD.glob("gold_*.txt")), "gold/が無い")
class J2_WithGold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ejh02_gold_eval_01 as G
        cls.G = G
        cls.store, cls.td = G._store()
        cls.gold, cls.texts = G.load_gold(), G.load_texts()

    def _cands(self):
        for k, gr in self.gold.items():
            en, ja = self.texts[k]
            if len(en) == len(ja) or min(len(en), len(ja)) == 1:
                continue
            yield k, gr, en, ja

    def test_default_never_calls_and_equals_plain(self):
        for k, gr, en, ja in self._cands():
            self.assertEqual(AL.align_paragraph(en, ja, self.store), AL.align_paragraph(en, ja, self.store, judge=None))

    def test_all_no_judge_changes_nothing_and_judge_only_adds_dp_candidates(self):
        added = 0
        for k, gr, en, ja in self._cands():
            plain = AL.align_paragraph(en, ja, self.store)
            no = AL.align_paragraph(en, ja, self.store, judge=lambda e, j, p: [False] * len(p))
            self.assertEqual(plain, no, k)
            calls = []
            yes = AL.align_paragraph(en, ja, self.store, judge=lambda e, j, p, c=calls: c.append(len(p)) or [True] * len(p))
            self.assertLessEqual(len(calls), 1)                                # 段落ごとに最大1 call
            self.assertEqual([g["en"] for g in plain], [g["en"] for g in yes])   # ENの群分けは不変(新しい対応を作らない)
            for a, b in zip(plain, yes):
                if a["ja"] is not None:
                    self.assertEqual(a, b)                                      # 既に採用された群は不変
                elif b["ja"] is not None:
                    added += 1
                    self.assertEqual(b["how"], "judge")
                    self.assertGreaterEqual(b["conf"], AL.PARAMS["judge_tau"])
        self.assertGreaterEqual(added, 10)                                      # 追加採用の余地(accept-all上限)

    def test_oracle_judge_adds_only_gold_correct_groups_and_verify_roundtrip(self):
        wrong = added = 0
        for k, gr, en, ja in self._cands():
            gm = self.G._gold_map(gr)

            def oracle(e, j, pairs, gm=gm):
                return [all(set(range(*cand)) <= gm[i] for i in ens) for ens, cand in pairs]
            res = AL.align_paragraph(en, ja, self.store, judge=oracle)
            for g in res:
                if g["how"] == "judge":
                    added += 1
                    wrong += 0 if all(set(range(*g["ja"])) <= gm[i] for i in g["en"]) else 1
        self.assertEqual(wrong, 0)
        self.assertGreater(added, 5)
        # verify往復: judge群を含むpartは『plain + accept-all』との照合で通り、judge群のja範囲を改竄すると不一致
        k, gr, en, ja = next(x for x in self._cands() if x[0][2] == "std_16" and x[0][0] == "moon")
        part = {"key": "k", "idx": 0, "paragraphs": [[{"sid": f"s{i}", "text": t, "html": t} for i, t in enumerate(en)]], "ja": ["".join(ja)]}
        # splitの再現: 結合した日本語段落をsplit_jaで再分割しても同じ文になること(ゴールド文は句点終わり)
        if [part["ja"][0][a:b].strip() for a, b in AL.split_ja(part["ja"][0])] != ja:
            self.skipTest("段落の再分割がゴールド文と一致しない")
        al, _ = AL.align_part(part, self.store, AL.PARAMS, judge=lambda e, j, p: [True] * len(p))
        part["ja_align"] = al
        if not any(g["how"] == "judge" for g in al):
            self.skipTest("この段落にjudge群なし")
        info = {"applicable": True, "degraded": [], "input_sha256": {"std": {"k": AL.part_input_sha(part)}}}
        art = {"levels": {"std": {"parts": [part]}}}
        v, _c = AL.verify_article_align(art, info, self.store)
        self.assertEqual(v, [])
        jg = next(g for g in part["ja_align"] if g["how"] == "judge")
        orig = list(jg["ja"])
        jg["ja"] = [orig[0], orig[1], max(orig[1] + 1, orig[2] - 3)]
        v2, _c2 = AL.verify_article_align(art, info, self.store)
        self.assertTrue(any("再計算" in m for m in v2), v2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
