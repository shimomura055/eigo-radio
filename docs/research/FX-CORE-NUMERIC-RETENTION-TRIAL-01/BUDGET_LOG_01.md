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

## 委任_03(案件上限230円→**300円**へ更新[Fable判断、自律枠の上限]。出典=各runの`raw_usage_log.jsonl`、集計=`er115.phase_spent_jpy`、合計285.68円)
| 日時(JST) | 工程 | run dir | 実費(円) | 累計(円) | 備考 |
|---|---|---|---|---|---|
| 08:15-08:25 | 無料: M1〜M5実装・test 46 PASS・事前登録02 commit・手順(i)0円 | - | 0 | 120.12 | commit 25da62900(生成前) |
| 08:25-08:27 | Phase 1b (ii) B3 v2 ×3(並列) | moon_shrinking/A/v2s1..3 | 11.364+10.543+12.429 = 34.336 | 154.46 | launch前見積37.5円、残額比較OK |
| 08:28-08:31 | Phase 1b (iii) chain ×2(並列、O-2'+M2+J2) | moon_shrinking/A/v2s1,v2s2 | 15.926+13.729 = 29.655 | 184.11 | B3費用除く |
| 08:33-08:34 | Phase 2 B3 v2 ×2(並列) | coffee_prices/A/p2, ig_nobel_2026/A/p2 | 13.063+8.645 = 21.708 | 205.82 | E=∅ ×2 |
| 08:37-08:40 | Phase 2 chain ×2(E=∅、測定用`--allow-empty-E`) | 同上 | 13.335+12.905 = 26.240 | 232.06 | launch前: 232+見積 <300 |
| 08:41-08:43 | Phase 2 B3 v2 ×3(並列再標本) | ig_nobel_2026/A/p3,p4, coffee_prices/A/p3 | 9.082+9.709+12.051 = 30.842 | 262.90 | ig_nobelのE=∅の再現性確認 |
| 08:43-08:46 | Phase 2 chain(coffee p3、E={4.30,41%}、O-2'で9.14・3%を付け替え) | coffee_prices/A/p3 | 14.117 | 277.01 | |
| 08:48 | Phase 2 診断B3(追記v1) | ig_nobel_2026/A/p5v1 | 8.662 | **285.68** | v2が原因かの切り分け。これ以降追加B3/chainは300円超の見込みで中止 |
**委任_03実費 165.56円(Phase 1b 63.99 + Phase 2 101.57)、案件累計 285.68円/上限300円(残14.32円)。** semiconductor_earnings(③)はB3+chain約26〜28円で300円を超える見込みのため事前登録どおり省略。再起動0。launch前の残額比較(Phase 1の0.12円超過の再発防止)を全launchで実施し、300円超過なし。日次(JST 2026-10-25)の他案件合算はFable管理。
