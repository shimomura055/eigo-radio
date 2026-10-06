# estimate_02 (TRIAL-02, gpt-6-luna, effort=medium)
単価: in 0.10 / cached 0.01 / out 0.50 USD/1M, 156.88円/USD。
根拠: dry-run Ledger側30call=¥0.33(dry仮定)。TRIAL-01実績 154call=¥2.48(≒¥0.0161/call)。本件111call(Ledger30+記事81)。
- low : ¥1.3 (0.012/call)
- mid : ¥2.0 (0.018/call)
- high: ¥3.5 (0.031/call、推論1000tok/call相当)
mid ≤ ¥10 → 実行(STOPなし)。各processに--budget-yenで上限強制。
