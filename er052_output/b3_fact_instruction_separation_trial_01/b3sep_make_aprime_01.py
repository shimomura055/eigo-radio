# -*- coding: utf-8 -*-
"""A'腕用: Production B3 module(er019_family_x_storyline_b3_fact_selection_01.py)を読み取り、Prompt文言3箇所だけを置換した
Trial専用コピー b3sep_b3_aprime_01.py と PROMPT_DIFF.md を生成する。Production fileは変更しない。置換は各1回ずつ(件数が1でなければ中断)。"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3sep_common_01 import *
src = open(f"{REPO}/er019_family_x_storyline_b3_fact_selection_01.py", encoding="utf-8", newline="").read()
OLD5 = "5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章。冒頭にStorylineの1行を含める)を作成してください。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。"
NEW5 = ("5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章)を作成してください。"
        "Selected Fact Briefには、事実の記述文だけを書いてください。注意・禁止・書き方の指示(「〜しないこと」「〜と書かない」「〜と断定しない」など)は書かないでください。"
        "冒頭のStorylineの再掲も不要です。Writerへの注意は、システムが台帳から別途付けます。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。")
OLDS = "- selected_fact_brief: Writerへ渡すSelected Fact Brief本文(Storylineの1行を含む)"
NEWS = "- selected_fact_brief: Writerへ渡すSelected Fact Brief本文(事実の記述文のみ。注意・指示・Storylineの再掲は含めない)"
OLDT = 'THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"'
NEWT = 'THEME_TAG = "B3SEP_APRIME_TRIAL_01"'
out = src
for o, n in ((OLD5, NEW5), (OLDS, NEWS), (OLDT, NEWT)):
    assert out.count(o) == 1, ("replace count != 1", o[:30], out.count(o))
    out = out.replace(o, n)
hdr = "# Trial専用コピー(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 A'腕)。Production moduleからPrompt3箇所のみ置換。Production fileは不変。\n"
open(f"{HERE}/b3sep_b3_aprime_01.py", "w", encoding="utf-8", newline="\n").write(hdr + out)
diff = f"""# PROMPT_DIFF: A'腕のTrial専用B3 Prompt(Productionとの差分は下の3箇所のみ)
- Production module: er019_family_x_storyline_b3_fact_selection_01.py sha256={sha(src)}
- Trialコピー: b3sep_b3_aprime_01.py sha256={sha(hdr + out)}
- DEVELOPER_MESSAGE / FACT_TEST_DEFINITIONS_JA / schema / validate / retry は不変。

## 1. USER_PROMPT_TEMPLATE 手順5
- 旧: {OLD5}
- 新: {NEW5}

## 2. 出力説明
- 旧: {OLDS}
- 新: {NEWS}

## 3. THEME_TAG(cost logger用ラベルのみ)
- 旧: {OLDT}
- 新: {NEWT}
"""
open(f"{HERE}/PROMPT_DIFF.md", "w", encoding="utf-8", newline="\n").write(diff)
print("ok", sha(src)[:16], sha(hdr + out)[:16])
