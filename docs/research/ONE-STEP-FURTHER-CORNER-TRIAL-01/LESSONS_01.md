# One Step Further Trial 知見(記録保持、REJECTED後も保持)

- 同系列モデルによる自己監査は、意味対応NG(元の意味から離れた表現の紹介)を見逃す。別ベンダー監査(argon)+回帰セット(NG5類型+前回7件、12/12検出)で検出できた。
- 記事文脈を生成Promptに渡すと、本文に無い内容の作文が起きやすい。Step1-5の工程分離で抑制できた。
- 意味保持は改善したが、学習価値は◎2・○3・△3と安定せず、発見性も不足。
- 歩留まりと単価の課題: 1記事セット約¥15〜19(目標70円の21〜27%)。
- Trial費用累計¥170.4(¥59.93+¥32.23+¥78.22)。最終委任で上限¥70を¥8.22超過。
- 資産(Production非接触): user_test/one_step_further_trial_01/、docs/research/ONE-STEP-FURTHER-CORNER-TRIAL-01/、tools/osf0*_*.py
