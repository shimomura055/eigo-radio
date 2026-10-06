# 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01 委任_02(Phase 1 有料実行)。
要約: P'台帳→B3→JA→EN→Checker DEV run→決定論ツール。上限¥60(ユーザー上限¥100)。

# 性質/到達上限Status/禁止事項
Trial実行(有料API)。到達上限は実行完了+生データ出力、評価・合否判定なし。
禁止: Production変更、E2E state書込、seed追加、SSOT編集、git、スイッチ変更、prompt手直し。

# 固定ブロック
E-1予算: 全体¥60/台帳段¥40/Checker¥10。D-1: 実費はcost_summary_02.jsonへ。
G-1: 本TrialはVALIDATEDでもProduction採用ではない。F-1: 失敗時fail-closed。T-0/T-2: TTSなし、T-3対象外。

# ユーザー指示
Phase 1: 同Research条件でP'によるFact台帳生成。台帳→B3→Writer→NG→Checker判定まで比較。
予算超過見込みはSTOP。seed増加・記事追加・追加Trialはしない。

# 事前指定Read一覧
docs/pm/ledger_clarity_p_trial/01a_run_procedure.md のみ。

# 事前指定Grep一覧+追記位置・更新位置の手順
dry-run確認→advanced全連鎖→provenance確認→Checker DEV→決定論ツール4種→cost_summary→E2E state非混入確認。

# 実行コマンド全文
01a_run_procedure.mdの2・3と同一(--stage advanced / run_checker_after_p01.py --budget-jpy 10)。

# SSOT追記文
なし。

# Git
なし。

# 報告
RESULT_PACKET参照。
