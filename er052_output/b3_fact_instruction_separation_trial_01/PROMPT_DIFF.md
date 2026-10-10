# PROMPT_DIFF: A'腕のTrial専用B3 Prompt(Productionとの差分は下の3箇所のみ)
- Production module: er019_family_x_storyline_b3_fact_selection_01.py sha256=93d0e31e735057ae874bbf27be48449fdd5bd5188e535b0a280eada9d314b758
- Trialコピー: b3sep_b3_aprime_01.py sha256=d5485f20396b668adcdad8519ad2e3b9e73f91b3ce6114ddfcfcc3384e7d48c4
- DEVELOPER_MESSAGE / FACT_TEST_DEFINITIONS_JA / schema / validate / retry は不変。

## 1. USER_PROMPT_TEMPLATE 手順5
- 旧: 5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章。冒頭にStorylineの1行を含める)を作成してください。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。
- 新: 5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章)を作成してください。Selected Fact Briefには、事実の記述文だけを書いてください。注意・禁止・書き方の指示(「〜しないこと」「〜と書かない」「〜と断定しない」など)は書かないでください。冒頭のStorylineの再掲も不要です。Writerへの注意は、システムが台帳から別途付けます。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。

## 2. 出力説明
- 旧: - selected_fact_brief: Writerへ渡すSelected Fact Brief本文(Storylineの1行を含む)
- 新: - selected_fact_brief: Writerへ渡すSelected Fact Brief本文(事実の記述文のみ。注意・指示・Storylineの再掲は含めない)

## 3. THEME_TAG(cost logger用ラベルのみ)
- 旧: THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"
- 新: THEME_TAG = "B3SEP_APRIME_TRIAL_01"
