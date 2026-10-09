# 委任ログ: WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_01c(2026-10-09)

- 委任元: sandwich-pm(Fable)。実行層: Sonnet。API支出: ¥0(評価LLMは呼んでいない)。Production/Checker/Writer変更なし。
- 範囲: Opus条件Aレビュー反映(ケース入替・事前登録追記・プロンプト/検証強化)、runner実装(未実行)、任意ブロック設計、MODEL_OPTIONSへのFable採用案追記。
- Opusレビュー(要約): docs/pm/opus_a_review_writer_eval_dual_llm_01.md
- ケース入替(10件維持): K05,K07を削除、K11(sw-p2r2-01、JA実Writer出力・逐語、Sonnet判定重大・ユーザー未確認)とK12(HC-012忠実文、ua6f EN実Writer出力・逐語、Rollback評価correct・ユーザー未確認)を追加、K10は境界へ(M2除外)。新規2件とも合成文ではなく実Writer出力。F-19(合成文)は不要だったため未使用。
- 事前登録: PREREGISTRATION_01.md 6節(M1段階判定、確認対象率2定義併記、C不一致率・両B件数、M3の件数表記、M4のtemperature扱い、限界欄追記)。
- プロンプト: 例示「撤回⇔再開」を「承認⇔却下」へ。検証: C+その他/なし、B+なし、A+なし以外を形式違反(1回再呼び出し)。
- runner: run_eval_01.py(未実行、dry-run出力は最終報告参照)、run_eval_01_test.py 20件PASS(API不要)。
- 成果物: er052_output/writer_eval_dual_llm_method_trial_01/{build_cases_01.py,cases_01.json,eval_items_01.json,CASES_01.md,eval_prompt_01.txt,EVAL_PROMPT_01.md,PREREGISTRATION_01.md,MODEL_OPTIONS_COST_01.md,RUN_PLAN_01.md,OPTIONAL_BLOCK_01.md,run_eval_01.py,run_eval_01_test.py}
- 判断が必要な点(Fable向け):
  1. K12はSonnet評価のみで、「put on hold」が台帳「ロールバック」と語が違うため、評価LLMがBを付ける可能性あり(M2が1件B許容なので即FAILにはならない)。それでもA対照として適切か。
  2. 任意ブロックの根拠ラベル(labels_merged.jsonl)は文単位でなくclaim単位、かつ全行ユーザー未確認。「文ごとSonnetラベル付き記事」は存在しない(OPTIONAL_BLOCK_01.md 2節)。
  3. DeepSeek単価登録(ユーザー承認事項)。
- 見つけた改善案(実装していない): なし。
