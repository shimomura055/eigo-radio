# BUDGET_LOG_01 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02 費用台帳。出典=各runの`raw_usage_log.jsonl`/`cost.json`[JPY換算は`er053_cost_aggregate_01`])
案件上限230円(Phase 1<=120円、Phase 2<=115円)。日次上限1,000円(JST、他案件含む)。
| 日時(JST) | 工程 | run dir | 実費(円) | 累計(円) | 備考 |
|---|---|---|---|---|---|
| 2026-10-25 | Phase 0〜実装・較正(委任_02) | - | 0 | 0 | API 0 |
| 2026-10-25 07:40-07:43 | B3 DEV x4(並列: 月s1,s2,s3 + 対照uk_train c1) | moon_shrinking/A/s1..s3, uk_train_speaker_playback/A/c1 | 11.067+10.608+10.685+10.326 = 42.686 | 42.69 | 出典=各raw_usage_log |
| 07:43-07:49 | chain A/s1,A/s3(R2記号STOPで終了) | moon_shrinking/A/s1,s3 | 約32.53(rounding 0.24含む) | 75.21 | 出力側正規化導入前の設計。有料run再起動0 |
| 07:50-07:53 | resume R2(A/s1,A/s3、R0/R1再利用) + Adv/Std | 同上 | 約7.25 | 82.46 | R1生出力へ決定論正規化→R2→EN |
| 07:56-07:58 | chain B/s1(規則9) | moon_shrinking/B/s1 | 12.127 | 94.6 | B3出力・丸めoverlay再利用 |
| 08:00-08:03 | B3 DEV x2(月s4,s5) | moon_shrinking/A/s4,s5 | 12.114+13.413 = 25.527 | **120.12** | s5でphase cap 120円を0.12円超過して発火 |
**Phase 1実費 120.12円(Fable設定のPhase 1上限120円を0.12円超過、案件上限230円内)。Phase 2 = 未実施(0円)。** 日次(2026-10-25 JST)の他案件分は未集計(日次1,000円の他案件合算はFable管理)。
