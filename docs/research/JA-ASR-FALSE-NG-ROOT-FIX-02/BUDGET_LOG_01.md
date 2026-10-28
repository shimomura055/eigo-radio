# BUDGET_LOG_01 (JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B)
| 工程 | API呼出 | TTS | ASR | 実費(円) |
|---|---|---|---|---|
| 統一評価 eval_unified_01.py(2回実行) | 0 | 0 | 0 | 0 |
| 残NG分析 residual_analysis_01.py | 0 | 0 | 0 | 0 |
| 診断probe(Y/preview同読み表記ゆれの再判定) | 0 | 0 | 0 | 0 |
合計: **実費0円・API呼出0**(socket guardで強制。Azure転写は6音声すべて保存済みのため補完ASR不要)。stop_scope_check rc=0(stop_check_01B.json)。当日開発費への加算なし。
Phase 2見込み(未実行・要Fable承認): N3 30 wav × OpenAI 4 draw 再転写 ≈ ¥0.7(単価 ¥0.0056/本、上限¥1)。

## 委任_02B 追記(2026-10-28)
| 工程 | API呼出 | TTS | ASR | 実費(円) |
|---|---|---|---|---|
| N3 30wav × OpenAI gpt-4o-mini-transcribe 各4 draw 再転写(`n3_redraw_02.py`、1起動・再試行なし、全120呼出success、stop_check_02B_pre_paid.json rc=0) | 120(OpenAIのみ。Azure 0) | 0 | 120 | **約1.2〜1.6**(cost_log: input 2,012 tok/output 1,074 tok。公表単価[$1.25/$5 per Mtok]で¥1.18、分課金[$0.003/min × 206.6秒]で¥1.55、¥150/$。請求明細は未取得=推定) |
| 統一評価 eval_unified_02.py(2回実行sha一致)・render・pytest | 0 | 0 | 0 | 0 |
見積¥0.7(BUDGET_PLAN_02)を超過した原因: 見積は『6秒/本×¥0.0008/秒』だが、N3 wavは平均1.7秒/本で課金は分単位換算(または音声トークン換算)のため単価が約2倍。個別Cap ¥3以内・案件見積≪¥300・日次1,000円以内。記録先: `n3_redraw_02.cost_log.jsonl`(120行)、転写=`n3_redraw_02.json`(wav sha・draw・model・ts)。

## 委任_03 追記(2026-10-28)
| 工程 | API呼出 | TTS | ASR | 実費(円) |
|---|---|---|---|---|
| 正例拡張4 wav(mey_02 comment_2 / Z melos run_e2e_02 comment_1 / Y preview 2本、計62.27秒)× OpenAI gpt-4o-mini-transcribe 各4 draw(`redraw_03.py`、1起動・再試行なし、全16呼出success、stop_check_03_pre_paid.json rc=0) | 16(OpenAIのみ。Azure 0) | 0 | 16 | **約1.3〜1.9**(cost_log: input 2,488 tok/output 1,110 tok。公表単価[$1.25/$5 per Mtok]で¥1.30、分課金[$0.003/min × 249秒]で¥1.87、¥150/$。請求明細は未取得=推定) |
| 負例追加draw | 0 | 0 | 0 | 0(N3 30wavの新4 drawは委任_02Bで取得済み、再利用) |
| 統一評価 eval_unified_03.py(3回実行sha一致 819cc816…)・render・pytest | 0 | 0 | 0 | 0 |
見積¥1.9(BUDGET_PLAN_03)以内。上限¥15・案件見積≪¥300・日次1,000円以内。記録先: `redraw_03.cost_log.jsonl`(16行)、転写=`redraw_03.json`(wav sha・draw・model・ts)。
