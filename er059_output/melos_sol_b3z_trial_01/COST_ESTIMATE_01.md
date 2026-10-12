# COST_ESTIMATE_01 (実行前)

上限: 50円(ユーザー承認)。換算 1USD=160円。gpt-6.1-sol Standard: input $2.0 / cached $0.1 / output $10.0 per 1M tokens(pricing_snapshot.json、未変更)。
根拠実測(既存Family X W-1、gpt-6.1-sol、effort=high): R0 out約4.2k tok、R1 約1.7k、R2 約2.1k、storyline_b3 約4.4k(いずれも日本語長文。英語短編は同等以下の見込み)。
- 1call概算: output 2〜4k tok -> 約0.02〜0.04 USD = 約3〜6.5円
- (2) R0+R1+R2 = 3 call: 約9〜18円 / (3) B3Z+R0+R1+R2 = 4 call: 約12〜24円 / 生成合計 7 call: 約21〜42円(上振れ側)、中央想定 約25円
- 評価(Luna gpt-6-luna、$0.1/$0.5): 2 call、各約0.5円未満(合計1円以内)
- retry余地: 技術失敗時のみ各call最大1回。BudgetGuardが「累計+次call保守見積6円 > 50円」で実行前STOP。
- 合計見込み 約27円(上限50円以内)。上限超見込みなし -> 実行可。
