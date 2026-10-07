# eval_assignment: 評価委任テンプレ (OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01)

36記事を3系統(テーマ別: meta / hormuz / sewer、各12記事=6セル x rep2)に分け、系統ごとに1委任。API呼び出し・記事生成・SSOT編集・git操作は行わない(¥0)。`<SLUG>`だけ差し替える。

## 委任文テンプレ

```
管理ID: OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01 評価_<SLUG>
範囲: テーマ <SLUG> の12記事(T0/T1/T2 x M0/M1 x rep1/rep2)の評価のみ。API呼び出し・記事生成・SSOT編集・git操作・他テーマの評価は禁止。
基準: docs/pm/note_transfer_matrix_01/eval_rubric.md に完全に従う(監査OPEN-233-E2E-STAGEWISE-NG-AUDIT-01と同一定義。独自に定義を変えない)。
入力:
- 記事: er052_output/open233_note_transfer_matrix_01/runs/<SLUG>/nb/<T><M>/rep<k>/{ja_writer/original.md, ja_writer/revision1.md, ja_writer/revision2.md, b1b/article.md}
- 台帳: er052_output/open233_polysemy_trial_02/ledgers/<SLUG>/control/research_ledger/verified_fact_ledger.txt
- ★fact一覧: docs/pm/allfact_e2e_02/theme_fact_watchlist.md
出力(1記事=1ファイル、docs/pm/note_transfer_matrix_01/article_schema.json 準拠):
- er052_output/open233_note_transfer_matrix_01/eval/articles/<SLUG>_<T><M>_rep<k>.json
- 任意の根拠メモ: er052_output/open233_note_transfer_matrix_01/eval/notes/<SLUG>.md(ng_items根拠、判定保留・境界例)
手順: rubric 8節(台帳->R2->EN->R0の順)。評価中は条件(T/M)で基準を変えない。ng_items の件数は stages/regressions と必ず一致させる。
自己検算: 12ファイル作成後、`python docs/pm/note_transfer_matrix_01/aggregate_matrix.py --in <一時dir> --out <一時dir>` は使わない(36本揃うまでFAILは正常)。代わりにJSONがschemaどおり読めること、IDが<slug>-<T><M>r<rep>-NN形式で重複しないこと、stages件数=ng_items件数であることを確認する。
報告(8行以内): 作成12ファイルの有無、記事別 ①JA/②EN/退行の 重大/軽微、★3分類の合計、重大NG件数と各ID、判定保留件数、rubricで解釈に迷った点。判定は単独評価で人間確認なしと明記。RESULT_PACKETには要約のみ、詳細は上記notesへ。
```

## 運用メモ
- 3系統は独立(出力ファイル名が異なる)ため並列実行可。集計は36本揃ってから `aggregate_matrix.py` を1回実行(出力 `eval/MATRIX_SUMMARY.md`、`eval/matrix_summary.json`)。
- 評価者へは各記事のT/Mを隠す必要はないが、基準を条件で変えないこと(rubric 7節)。
