# -*- coding: utf-8 -*-
"""er074 条件設計テスト(API呼出なし)。"""
import difflib
import re
import sys
import unittest

import er074_family_z_std_preview_comment_dependency_01 as m

RC = 0


def check(name, cond):
    global RC
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        RC = 1


P, a2gen, (c1, c2, std) = m.build_prompts()
er72 = open(f"{m.ER72}/prompt_std_full_01.txt", encoding="utf-8").read()
check("A prompt == er072 std prompt (sha一致)", P["A"][2] == er72)
for k in "ABCDE":
    check(f"{k}: 本文std.md全文を含む", std in P[k][2])
check("B: C1全文含む/C2全文含まない/(生成失敗)含む", c1 in P["B"][2] and c2 not in P["B"][2] and m.B_COMMENT2 in P["B"][2])
check("C: 第1文のみ(全文は含まない)", m.first_sentence(c1) in P["C"][2] and m.first_sentence(c2) in P["C"][2]
      and c1 not in P["C"][2] and c2 not in P["C"][2])
check("D: C1・C2全文含む/置換文言あり/旧文言なし", c1 in P["D"][2] and c2 in P["D"][2] and m.BULLET_D in P["D"][2]
      and m.INTRO_D in P["D"][2] and m.BULLET_ORIG not in P["D"][2])
E = P["E"][2]
sents = [s for s in re.split(r"(?<=。)", c1 + c2) if s.strip()]
check("E: C1・C2全文が無い", c1 not in E and c2 not in E)
check("E: C1・C2の各文が無い(%d文)" % len(sents), all(s not in E for s in sents))
check("E: 'Comment' / placeholder が無い", "Comment" not in E and "{comment" not in E)
terms = ["支配者", "死刑", "身代わり", "猶予", "結婚式", "橋のない", "血だらけ", "三人", "待つか", "家へ戻る", "代わりに命", "恐怖から"]
hit_prompt = [t for t in terms if t in E]
hit_std = [t for t in terms if t in std]
check("E: Comment固有語がprompt(本文以外)に無い (promptヒット=%s, 本文ヒット=%s)" % (hit_prompt, hit_std),
      not [t for t in hit_prompt if t not in hit_std])
E_wo = E.replace(std, "")
check("E: 本文を除いた部分にComment固有語が無い", not any(t in E_wo for t in terms))
check("E: 重複回避文言('重複')が残らない", "重複" not in E_wo)
d = [l for l in difflib.unified_diff(P["A"][2].splitlines(), E.splitlines(), lineterm="", n=0)
     if l[:1] == "+" and not l.startswith("+++")]
check("A->E: 追加行なし(除去のみ)", len(d) == 0)
dd = [l for l in difflib.unified_diff(P["A"][2].splitlines(), P["D"][2].splitlines(), lineterm="", n=0)
      if l[:1] in "+-" and not l.startswith(("+++", "---"))]
check("A->D: 変更行は4行(2箇所の-/+)", len(dd) == 4)
check("effortはProduction同一(high)", a2gen.REASONING_EFFORT == "high")


class ScriptChecksTest(unittest.TestCase):
    """unittest discovery用(TEST-HYGIENE-02、2026-10-22): 本fileはstandalone script形式(`python <file>`で実行、
    終了codeで判定)。モジュール読込時に全checkが実行済みなので、その結果を1件のtestとして検証する。"""
    def test_all_checks_pass(self):
        self.assertEqual(RC, 0)


if __name__ == "__main__":
    sys.exit(RC)
