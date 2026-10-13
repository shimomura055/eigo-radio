# FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01 委任_01(2026-10-13、設計・見積フェーズ)
- 範囲: 代表箇所固定(Std/Adv Part1)、A〜H Prompt設計、32 call生成計画、費用見積、測定・試聴ページ設計。TTS/LLM/ASR呼出なし、費用JPY0、Production無変更。
- check_delegation_prompt.py: 抄録のためFAIL記録のみ(未実行)。STOP確認: `*STOP_NOTICE*`は別タスク(FAMILY-Z-MELOS-SOL)のもののみ、STOP/STOP_ALL無し。
- 成果物: er057_output/coffee_tts_style_8way_01/{DESIGN_01.md,prompts_8way_01.json,cost_estimate_01.json}、er057_coffee_tts_style_8way_01_design.py、er057_coffee_tts_style_8way_01_design_md.py。
- 結果: 32 call中央JPY43.4/上限+retry JPY57.6(上限JPY60内)。Aは現行P8逐語(sha 3eadf4f6、assert済)。A-B以外の全組Jaccard<=0.26。
- 次: Fable確認後に委任_02で生成。Status: 設計提出(VALIDATED/REJECTED/UDRは生成・試聴後)。
