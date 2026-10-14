# PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 委任_03 (要点保存)

日付: 2026-10-14 / 費用JPY0 / 範囲: Research・設計案のみ(規則ファイル・Agent定義・Production・Prompt・CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS変更禁止、有料API・.env不使用)

## 目的
委任_02成果物(commit a0c9bd2e)へのOpus独立レビュー(条件A)結論「方向性は支持、ただし要修正(致命的4件: OF-209/210/215/220)」を受け、Fable照合の結果**全所見OF-209〜OF-224を採用**し、設計文書の「_01」ファイルを直接改訂(版は増やさず、各ファイル末尾に改訂履歴)。ユーザー判断事項U1〜U4を追加。

## 反映所見(採否: 全件採用。OF-215/OF-220は対立点でOpus案を採用)
- 安全性: OF-209(出自に APPROVED_PROMPT_CHANGE 追加=7種、保護対象パス一覧+分類記録、強制はgit pre-commit hook)/OF-210(state_gateをspec_id/component単位、decision_refをtranscriptsと照合、WIRED仕様修正もstate_gate fix)/OF-211(R9除外から有料run再起動許可回数・予算envelopeを外す)/OF-212(pre-commitにsecret_scan --staged、差分表#25を維持+機械化)/OF-213(安全不変条件4点はCLAUDE.mdとsonnet-worker.mdに重複して残す、差分表#26)
- ループ上限: OF-214(failure_mode_idはFable付与、runner起動ログ+budget_gate予約記録で機械計数、管理ID単位委任回数は警告閾値、PARKED→QCD_TRADEOFF、再開は新仮説のみ)
- Fable中継化: OF-215(推奨を案3=SubagentStop hookでaccept_check確定実行→docs/pm/state/accept/<id>.json、案2は連結回避リスク注記、CMP R5を●→△)
- Decision Policy: OF-216(Production Gate厳格化・新品質基準もユーザー判断=U1)/OF-217(既定=シャドー運用=U2)/OF-218(STOP_NOTICE issuer欄、数値化されない品質項目は#1グレー規則へ)
- Loop: OF-219(仮説commitのgit順序検査、Opus往復は再発/保護対象修正の原因確定前のみ)
- 機械強制: OF-220(既存ブロック機構は最初からブロック維持、警告モードはlint系のみ、stop_checkは26-5の共通化、Claude hooks注意点)
- 常駐文書: OF-221(PM_GOVERNANCE縮小前に移行表必須、12-13節番号重複L2591/L2603を差分表#18で特定、CLAUDE.md PM層削除=U4)
- 予算: OF-222(日次または週次の合計ハード上限=U3、ロック不要、200倍は開発期のみ、+20%は承認枠内)
- KPI: OF-223(M9追加、保護対象分類の見逃し1件で即時中止、撤退条件を2つ以上該当、Phase 2にシャドー運用1件、M2基準値の偏り)
- FR誠実性: OF-224(Dの22件は自己採点と明記しR5訂正で21件解消・4件部分対処、安全性記述の修正、§8をU1〜U4統合の7項目に整理)

## 台帳記録(記録のみ、規則変更ではない)
- docs/pm/OPUS_FINDINGS_LEDGER.md にOF-209〜OF-224を追記(16行)
- docs/pm/USER_DECISION_REGISTER_01.md に統合エントリ#59を1件のみ追加(件数見出しは触れない)
- docs/pm/REPORT_LEDGER.md に本管理IDの1行を追加
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSは変更しない(ユーザー議論後に別管理IDで反映)

## 固定ブロック要点
E-1(PowerShell/.venv/PYTHONUTF8=1)、D-1(上記禁止)、G-1(明示git add、secret_scan --staged必須、Managed-ID trailer、git add -A/-f/amend/rebase/force push/stash/clean/reset --hard禁止)、F-1(JPY0)、T-2/T-3(ACTIVE_TASK_PMAR/RESULT_PACKET_PMAR更新)
