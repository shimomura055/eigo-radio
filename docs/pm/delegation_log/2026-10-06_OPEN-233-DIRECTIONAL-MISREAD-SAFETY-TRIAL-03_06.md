## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_06: 結果・Fable判定のSSOT追記、Dangling Reference確認、明示git add→commit→push)。
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録+Git(¥0)。Status: TRIAL-03=**REJECTED**(Fable判定)。禁止: TRIAL-04自動移行/Production変更/gold・KPI変更/新カテゴリ・新原則の追加(CURRENT_SPEC不変)/有料API/`git add -A`/amend・rebase・force push/Fable判定の変更。Opus Gate: 次回修正は11-3節条件B(同じ問題へ2回修正しても再発→3回目パッチ前)該当として記録。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力はhash・push結果のみ。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を本ファイルへ逐語保存しcheck_delegation_prompt.py実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 実費¥7.41(上限¥8)を領収記録。

## 記録する事実・作業内容(要点)
R1 費用: 実費¥7.41(上限¥8)、全73項目完走、sha256凍結一致。R2 合格基準: 1・2・5・6・7未達、3・8充足、4はX充足/Y未達。R3 退行trace: trace_hc012_regression_03.md。R4 Fable判定=REJECTED(TRIAL-04自動移行なし、次修正は条件BでOpus必須)。R5 未解決(a)〜(f)。
作業: 1 REPORT §86-6/§86-7置換、2 DECISION_LOG追記、3 OPEN_ITEMS進捗追記、4 ACTIVE_TASK更新、5 Dangling確認、6 明示git add、7 commit、8 push、9 RESULT_PACKET。(元の委任文の詳細はFable側の委任メッセージ原文を参照)

## 事前指定Read一覧
docs/pm/ACTIVE_TASK.md 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
REPORT(§86-6/§86-7)、DECISION_LOG(TRIAL-03 (d))、OPEN_ITEMS(OPEN-233-DIRECTIONAL-MISREAD行)をGrep→範囲Read→Edit。全文Read禁止。

## 実行コマンド全文
1. .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_06.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_06.md_check.json
2. git add <各ファイル> / git status --short / git commit / git push origin main

## SSOT追記文
REPORT §86-6/§86-7、DECISION_LOG (d)、OPEN_ITEMS進捗。

## Git
明示add、commit、push origin main。エラー時は中断。

## 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET.md。最終報告6行以内。
