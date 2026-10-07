# eval_assignment: 評価委任テンプレ (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01、M5反映版)

60記事(A4で確定: 5条件V0/V1/V3/V5/V6 x brief b1〜b4 x Writer1本)を3系統(テーマ別: meta / hormuz / space_weapons、各20記事)に分け、系統ごとに1委任。API呼び出し・記事生成・SSOT編集・git操作は行わない(¥0)。`<SLUG>`だけ差し替える。**匿名コードで評価し、variantは評価者に開示しない**(手順 `docs/pm/b3_trial_01/blinding.md`、事前に `tools/make_blind_copies.py --stage2` を実行(MAP_stage2.json生成))。brief_reviewは**別インスタンス**に別委任する(後述)。

## A. 記事評価の委任文テンプレ

```
管理ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 評価_<SLUG>
範囲: テーマ <SLUG> の匿名記事20本の評価のみ。API呼び出し・記事生成・SSOT編集・git操作・他テーマ・brief評価は禁止。
基準: docs/pm/b3_trial_01/eval_rubric.md に完全に従う(MATRIX-01 rubric継承。独自に定義を変えない)。
入力(これ以外は読まない。runs/配下、eval/blind/MAP.json、design_01.md、brief_features.json、他の条件・期待に関する資料は読まない):
- 記事: er052_output/open233_b3_trial_01/eval/blind/<SLUG>/<code>/{ja_writer/original.md(R0), ja_writer/revision1.md(R1), ja_writer/revision2.md(R2), b1b/article.md(EN)} (20個のcode)
- 台帳: er052_output/open233_polysemy_trial_02/ledgers/<SLUG>/control/research_ledger/verified_fact_ledger.txt
- ★fact一覧: docs/pm/allfact_e2e_02/theme_fact_watchlist.md(space_weapons は★なし。rubric 4節の参考扱い)
出力(1記事=1ファイル、docs/pm/b3_trial_01/article_schema.json 準拠。slug と code のみ記入。variant/b/wは書かない):
- er052_output/open233_b3_trial_01/eval/articles/<SLUG>_<code>.json (20ファイル)
- 任意の根拠メモ: er052_output/open233_b3_trial_01/eval/notes/<SLUG>.md
評価順序: codeの辞書順の逆順(条件順にならないため)。各記事とも台帳と照合して判定する。条件の定義・仮説・期待順位は知らない前提で、基準を記事ごとに変えない。
手順: rubric 8節(台帳->R2->EN->R0)。ng_items の件数は stages(s0_r0/s1_ja/s2_en)/regressions と必ず一致させる。ID形式 <slug>-<code>-NN。kindは必須、別fact連結由来ならcross_fact=true。
自己検算: 20ファイル作成後、JSONがschemaどおり読めること、IDが形式どおりで重複しないこと、stages件数=ng_items件数であることを確認する(aggregate_b3.pyは60本揃うまでFAILが正常なので使わない)。
報告(8行以内): 作成20ファイルの有無、重大NG件数と各ID、判定保留件数、rubricで解釈に迷った点。判定は単独評価で人間確認なしと明記。RESULT_PACKETには要約のみ、詳細は上記notesへ。条件別の集計はMAP未参照のため報告しない。
```

## B. brief_review の委任文(別インスタンス、記事評価とは別)
```
管理ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 brief_review_<SLUG>
範囲: テーマ <SLUG> の匿名brief(eval/blind/<SLUG>/_briefs/<bcode>/selected_brief.md)の目視記録のみ。記事本文・記事評価結果・MAP.json・runs/配下は読まない。API・生成・SSOT編集・git禁止。
定義: 評価単位=「箇条書き1項目、または句点区切り1文」(Storyline行は文ごとに1単位)。
記入: 台帳(er052_output/open233_polysemy_trial_02/ledgers/<SLUG>/control/research_ledger/verified_fact_ledger.txt)と照らし、units_total、omitted_units(台帳にある主体・対象・数値の掛かる先がbriefで落ちている単位。台帳自体が曖昧なものは数えずnotes)、omitted_rate(=omitted_units/units_total)、omitted_examples(最大3)、cross_fact_qualifier(別factの限定語が1単位内で連結)、unprovided_checklist_hits(docs/pm/b3_trial_01/unprovided_checklist_<SLUG>.md の各項目をbriefが「示されていない/不明/未提示」等で明記しているか stated:true/false)。
出力: er052_output/open233_b3_trial_01/eval/brief_review/<SLUG>_<bcode>.json(article_schema.json の x-brief_review_file 参照)。
```

## 運用メモ
- 3系統(+brief_review 3系統)は独立のため並列実行可。全60本+brief60本が揃ってから各1回実行:
  1. `python docs/pm/b3_trial_01/brief_features.py`(出力 `eval/brief_features.json`)
  2. `python docs/pm/b3_trial_01/aggregate_b3.py`(`eval/blind/MAP.json` で解決。出力 `eval/B3_SUMMARY.md`、`eval/b3_summary.json`)
- 評価委任文に条件の意味・期待順位を書かない。MAP.jsonは集計まで評価者に渡さない。

- A4注記: 段階2は `make_blind_copies.py --stage2`(既存MAP.jsonは上書きせず `eval/blind/MAP_stage2.json`)。aggregate_b3.py は旧前提(72記事・b1/b2・w1/w2・V2含む)のままのため、集計委任の前に60記事・b1〜b4多数同符号(design_01.md 5-A4)へ別途更新が必要(本A4では未着手)。
