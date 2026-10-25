# BUDGET_LOG_01 (cost_log実測のみ。2026-10-26 07:2x時点、HR待機で停止中)

| 項目 | 実測 | 出典 |
|---|---|---|
| text段(research 11.293/ledger 7.552/storyline_b3 14.268/b3_core_number_rounding 0.155/w1_r0 6.168/r1 2.660/r2 2.282/advanced 0.300/standard 0.264/risk_flag合計≈3.15) | 47.556円 | er019_output/ai_island_temple/run_ai_01/cost.json total_jpy |
| audio scaffold段(Comment/Preview/Part2抽出/KP候補、TTS未実行) | 4.01円 | audio runner "after scaffold" so far |
| 小計(runner報告) | 51.57円 | 47.556+4.01 |
| 小計(daily_dev_cost_01.py run dir別) | 47.03+4.01=51.04円 | `py docs/pm/tools/daily_dev_cost_01.py` top_run_dirs |
| 当日JST累計(全agent) | 74.98円(うち他agent=FZ trial 23.77円等) | 同上 |
| 記事セット原価(PM_GOVERNANCE 15-8 主指標) | **未確認**(TTS/ASR/組立が未実行。HR待機のため完走値なし) | — |
| 上限150円Guardrail | 未到達(51.57円)。TTS見込み約40〜50円 | — |
