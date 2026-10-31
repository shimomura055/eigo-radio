# DELETION_LOG_01
全件の path/size/mtime/区分/結果は `deletion_raw_01.tsv`(712行)。削除は1ファイルずつ rm -f、削除後に不在確認。
| 区分 | 件数 | 容量 | 備考 |
|---|---|---|---|
| A1 task出力 >200MB かつ 60分以上前 | 10 | 44.10GB | 失敗0 |
| A2 過去セッションdirの .output 24h以上前 | 702 | 0.04GB | 失敗0 |
| A3 pip cache purge (.venv pip) | 1015 files | 0.64GB | 635.5MB |
| A3 %TEMP% / npm verify | 0 | 0 | 対象なし(7日超tmp/log/dmpなし)。npm cacheは未実施(0.41GB、効果小) |
| A4 scratchpad直下中間物 | 0 | 0 | 完了済み判定が確実でなく保留 |
削除したのは全て「Claude task出力」と「pip HTTP/wheel cache」のみ。repo・worktree・音声Store・SSOT・Playwright/HF/MFAは未接触。
