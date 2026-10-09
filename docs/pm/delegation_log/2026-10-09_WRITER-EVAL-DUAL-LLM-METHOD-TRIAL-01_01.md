# 委任ログ: WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_01(2026-10-09)

- 委任元: sandwich-pm(Fable)。実行層: Sonnet。API支出: ¥0(評価LLMは呼んでいない)。Production/Checker/Writer変更なし。
- 範囲: 設計・ケース選定・費用概算まで。実行(評価LLM呼び出し)は別委任。
- 成果物: er052_output/writer_eval_dual_llm_method_trial_01/ 配下
  CASES_01.md / cases_01.json / eval_items_01.json / eval_prompt_01.txt / EVAL_PROMPT_01.md / MODEL_OPTIONS_COST_01.md / RESULT_TABLE_TEMPLATE_01.md / RUN_PLAN_01.md / PREREGISTRATION_01.md / build_cases_01.py
- ケース10件: 重大3(K01 meta restored、K02 ai_control jb9k、K03 A5-0 gold)、境界4(K04 JA「以前の状態に戻しました」、K05 changed...back、K06 space不在・非公開、K07 so因果)、明らかな問題なし3(K08〜K10)。
- 判断が必要な点(Fable向け):
  1. モデル構成(P1 luna+DeepSeek / P2 astra+DeepSeek / P3 +Claude subagent)。DeepSeek・Geminiテキストは単価未登録のため、登録承認が先。
  2. 事前登録の閾値(M2「6判定中B/C 1以下かつC=0」、M3参考線40/60%、K03をM1必須から外す)は委任者案。承認または修正が必要。
  3. K01は「Fable確定+ユーザー呼称」でありユーザー個別ラベルではない。K08〜K10はSonnet暫定+逐語照合のみ。
  4. 10件中5件が同一Fact(HC-012)に偏る。
- 見つけた改善案(実装していない): なし(新規仕様候補は無し)。
- Git: 個別指定でadd(`git add -A`不使用)。commit hash・raw URLは docs/pm/RESULT_PACKET.md(gitignore対象)と最終報告に記載。
