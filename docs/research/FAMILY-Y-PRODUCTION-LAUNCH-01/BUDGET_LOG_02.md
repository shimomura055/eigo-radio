# BUDGET_LOG_02 (FAMILY-Y-PRODUCTION-LAUNCH-01 委任_06 / 2026-10-25 JST)

| 項目 | 円 | 備考 |
|---|---:|---|
| 接続分(Part 2候補抽出 0.481 + Part 1解説 0.107 + 訳 0.059 + Step B 0.090) | 0.737 | E-1実API(L1b,L2)。C分析・Part Aのtestは API 0 |
| b1b y_voice_1 再試行(L3, TTS+ASR+Local Rewrite) | 5.579 | approve_regenerate 1回 |
| a2 preview/y_voice_1 再試行(L4) | 13.746 | approve_regenerate 2回(preview, y_voice_1) |
| **本委任合計** | **20.062** | run累計 52.134 |

- Y累計(Cap 170円): 約166.85円。残約3.15円。委任_05の較正費17.644円が委任文の「既支出129.14円」に未算入だったため、残40.86円は実際には約23円(Cap内)。
- 日次(JST、daily_dev_cost_01): 開始1,200.32 + 未捕捉94.28 = 約1,294.6円 → 終了1,229.16 + 94.28 = 約1,323.4円。日次1,500円内。
- 以後の追加有料作業(a2/b1bの再生成等)はY Cap 170円に残約3.15円のため、Cap増額の判断(Fable/ユーザー)なしに実行不可。
- 起動回数: 有料4起動(L1失敗[API 0]を含め5)。RESTART_STORM回避(150秒/5分3回)を遵守。stop_scope_check rc=0 ×4。
