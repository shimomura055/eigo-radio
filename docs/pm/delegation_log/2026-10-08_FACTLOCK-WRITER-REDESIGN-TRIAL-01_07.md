# 管理ID: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_07 (R3-fresh を gpt-6-sol で N=1 [meta b2])

(委任文の要点保存。sandwich-pm(Fable)からの委任文を受領し、主要項目を保存。T-0)

- 性質: 探索Trial(N=1)。Status上限=MEASURED。推奨なし。並行タスク(04b/04c/配線E2E)のファイルには書き込まない。git・SSOT操作禁止。
- 書込先: er052_output/factlock_writer_trial_01/r3_minimal_01/sol_n1/ 配下、docs/pm/RESULT_PACKET_FACTLOCK_R3_SOL.md、本ファイル(+_check.json)のみ。run_r3_minimal.py編集禁止(sol_n1/run_sol_n1.pyに最小ラッパ)。Production code編集禁止。
- モデル差替: require_model_or_override("B1_WRITER","gpt-6-sol",override_reason="FACTLOCK R3 SOL N=1")
- 費用: 上限¥15 Guardrail(超過時は承認済みscope内・原因把握済み・異常retryでなければ記録して継続、暴走疑いのみSTOP)。見込み≈¥5。単価 gpt-6-sol Input $2.00/Cached $0.20/Output $10.00 per 1M、USD/JPY=160、raw usageから自前計算。
- Opus独立技術レビューGate: 非該当。時間見込み≈20分。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2(TTSなし)/T-3。
- ユーザー指示(原文): 「同じR3-FreshをN=1でSOLで作らせたら費用はいくらくらい?」(2026-10-08)。背景: ChatGPTで同じ1文指示のRevise版が大きく改善した例(セリフのフック・短段落・問いの連鎖・オチ)。6-lunaのR3-freshは語句の磨きに留まった。
- KPI provenance: sol R3出力・FC・pairwise=fresh。元R2=reuse。E2E自己確認=No。
- 実行内容: (1) sol R3-fresh 1 call(入力=元R2本文+指示1文「事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。」+記号禁止ブロック、台帳なし、reasoning high、不可ならmediumへ1回だけ下げ記録)。(2) JA FC(run_deviation_check、全台帳、gpt-6-luna)。(3) pairwise: sol対元R2、sol対6-luna R3-fresh、各2順序(judge 6-luna、R3 Trialと同じ中立判定文)。(4) 文体指標・記号Gate発火数・費用。
- 追記位置: sol_n1/r3_sol.md, fc_sol.json, pairwise_*.json, SUMMARY_SOL_N1.md
- コマンド: .venv\Scripts\python.exe -X utf8 er052_output\factlock_writer_trial_01\r3_minimal_01\sol_n1\run_sol_n1.py --slug meta --brief b2 --model gpt-6-sol --budget-jpy 15 --yes-run-paid
- 報告: docs/pm/RESULT_PACKET_FACTLOCK_R3_SOL.md (sol R3全文、費用/所要秒/FC/pairwise/文体指標/記号Gate表、構成変化の所見(事実のみ)、問題・残作業、check結果、一覧外Read。推奨は書かない)
