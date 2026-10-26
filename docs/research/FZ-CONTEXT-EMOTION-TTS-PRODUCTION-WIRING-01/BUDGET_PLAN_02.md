# BUDGET_PLAN_02 — Phase 2 実証費用(見積。Phase 1は API 0 / JPY 0)

前提: 費用承認 PM_GOVERNANCE 7-7(承認済みScope内・案件見積300円以下はAI自律)。日次1,000円枠内。分割で境界回避しない(全体を1案件として300円以下を確認)。
単価根拠: Z dialogue clipの実績(1 TTS生成+ASR)。E-1はnotes LLM(level単位1 call)+全dialogue clipのctx TTS、E-2〜E-6は代表clip限定(`--only-clips`)。

| case | 内容 | 見積(円) |
|---|---|---|
| E-1 | 猿の手 a2+b1b Std、ctx経路の正常生成(全dialogue clip) | 約29 |
| E-2 | 強制NG 1・2回目->cooldown600s->従来3回目(1 clip) | 約3 |
| E-3 | E-2形+cooldown中kill->再開 | 約3 |
| E-4 | 3回強制NG->STOPPED->HR Lock(Std/Adv各) | 約4 |
| E-5 | 1回目のみNG+n=1後kill->再開 | 約1 |
| E-6 | Adv: 減速後判定でNG->外側ループ継続 | 約1 |
期待合計 約49円 / 保守 約62円 / 天井 約80円。全て300円以下=Fable自律枠。各runは`--budget-jpy`を各case上限に設定(E-1=60、他=15)。見積超過見込み・天井超過は即停止してFable報告。
Charter3: 量産単価への影響=notes LLM 1 call/level(低 reasoning、数円未満)+ctx TTSは同一回数。Phase 2でrunごとの実増分を計測して報告。
