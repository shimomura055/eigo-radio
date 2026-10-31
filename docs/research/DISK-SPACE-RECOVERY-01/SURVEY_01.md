# SURVEY_01 (DISK-SPACE-RECOVERY-01, 2026-10-31)
起点調査=scratchpad disk_survey_01.md(ENV-DISK-SPACE-SURVEY-01)を再計測。
- C: 総453.5GB。対応前 空き 1.92GB(本委任開始時, Get-PSDrive C)。対応後 約42.8GB(並行作業で変動)。
- 主因: Claude Code task出力 `%LOCALAPPDATA%\Temp\claude\C--Users-tensh-eigo-radio\<session>\tasks\*.output` 計44.1GB(10本)。うち9本が各約5.37GB(=出力上限で打切り)。既存調査では「対話モードpython(stdin無し)がWinError 123トレースバックを無限出力」。bhmu917ig(853MB, 10/31 11:50)のみ上限未到達で原因は未確認(削除済み)。
- eigo-radio 約63.5GB(mfa_tool 13.7 / er026 8.8 / er019 7.3 / er121 4.0 / .claude/worktrees 3.2 / .git 2.5)はC区分/B区分、未削除。
- pagefile 26.8GB・hiberfil 6.6GB・Windows\Installer 3.7GB: OS領域、未接触。
- ms-playwright 1.39GB / .cache 2.4GB(HF等) / npm-cache 0.41GB / pip cache 0.64GB(purge済)。
- %TEMP%直下: 11,930 entries, 7日超の .tmp/.log/.dmp は0件、pip-*/tmp*フォルダ7日超も0件 → A3(%TEMP%)該当なし。Temp合計約78GB、大半は scratchpad 配下の git worktree(claude\...\scratchpad\wt_*)。
- 急増: 10/30 22:46 の5.37GB task出力、.git/objects/pack、assembled wav。Trial/Production出力自体の異常増は確認せず。
