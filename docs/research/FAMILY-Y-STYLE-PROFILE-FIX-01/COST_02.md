# COST_02 — 委任_04の費用実績(run_style_fix_01 y_voice_1再生成)
出典: `run_style_fix_01/cost_log.jsonl`(108→111行)を`er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far`(runnerのbudget guardと同じ関数)で集計。
| 区分 | 円 |
|---|---|
| 委任_02 累計(COST_01) | 30.79 |
| 委任_04 後 累計 | 32.09 (Gemini 17.35 / OpenAI ASR 4.71 / Azure 10.03) |
| **委任_04 増分** | **1.30** (Gemini TTS 1回 +0.92 / OpenAI ASR 2回〔本take検証+減速後再検証〕+0.38) |
- Cap ¥10(Guardrail)に対し13%。接近なし。当日既使用 約594円+1.30 < 1,000円。案件300円以下(7-7)。
- 注: runnerの`--approved-budget-jpy`は累計(既使用30.79)との比較のため、委任文どおり`10`を指定すると新規API呼出前に`FAMILY_Y_BUDGET_STOP`(API 0・費用0)。増分Cap¥10を保つため累計上限`41`(=30.79+約10)で再投入した(1回)。
