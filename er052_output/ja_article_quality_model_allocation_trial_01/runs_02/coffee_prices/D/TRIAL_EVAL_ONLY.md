# TRIAL_EVAL_ONLY: coffee_prices D案 R2(2026-10-11、委任_06)

- 本記事(`export/r2.md`)は `ja_writer/audit/rejected_w1_r2_symbol.md` の逐語コピー(文字は一切変更していない)。
- **記号QA不合格**: 全角括弧「（」「）」残存(「USDA（米農務省）」)および波ダッシュ「〜」残存(「約2〜3か月」2箇所)。R2再実行1回でも残存し、`JASymbolCheckStopError`でSTOPした。
- **Trial評価専用・正式完成品ではない**。Production経路(W-1)では同じ出力はSTOPとなり、TTS/英訳等の下流へ進まない。
- ユーザー指示(2026-10-11)により、品質比較(Blind評価)の素材としてのみ使用する。Production採用・音声化・正式記事としての利用は不可。
- Blindページ(`user_test/ja_quality_model_allocation_02/coffee/index.html`)には、この判定情報は表示しない。
