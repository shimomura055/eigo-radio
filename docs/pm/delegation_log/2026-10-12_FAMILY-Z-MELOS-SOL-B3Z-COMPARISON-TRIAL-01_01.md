## 管理ID

FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 委任_01(2026-10-12、ユーザー承認済みTrial、費用上限50円)

## 委任内容(要旨。原文逐語はFable側記録)

『走れメロス』で (1)従来方式 / (2)Sol変更のみ / (3)Sol+B3Z の3方式を比較(テキスト生成・品質比較まで)。Production採用・音声化・Family Z正式Writer/Prompt/構成・CURRENT_SPEC変更は禁止。PC負荷確認(高負荷なら生成を後回し)、(1)は既存成果物を確認し再生成しない、B3ZはFamily X B3(storyline_b3)のFamily Z向け最小変更(新規出来事の創作禁止)、(2)(3)は同一R0/R1/R2・モデル・effortで差分はB3Zの有無のみ、Writer=GPT-6 Sol(routing/pricing確認のうえ最新原則でID決定)、評価はgpt-6-luna(N=2、Blind、AI評価と明記)、比較ページをuser_test配下へ、SSOT追記(DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER)。

## 実施結果

- PC負荷: 開始時 CPU 100%・メモリ81%(Pace Trial 02の python/whisper 多数稼働)。調査・設計(手順1〜3)を先行し、CPU 6%へ低下後に生成開始(既存タスクは停止せず、LLM呼出は直列)。
- (1)既存確認: `er059_output/melos_sol_b3z_trial_01/BASELINE_01.md`。単発生成(gpt-5.6-luna, effort=high)で、R0/R1/R2/B3は存在しない。再生成せず原出力story.md(381語)を(1)として使用。
- B3Z/工程設計: `B3Z_DESIGN_01.md`。費用概算: `COST_ESTIMATE_01.md`(見込み約27円)。
- 生成: mock乾式後に real(`--approved-budget-jpy 50`)、gpt-6.1-sol(gpt-6-solは未登録)、effort=high、7 call、実費20.22円、技術retry 0回。AI評価(gpt-6-luna 2 call)0.49円。合計約20.71円。
- 成果物: `er059_output/melos_sol_b3z_trial_01/`(m2_sol_only/, m3_sol_b3z/[B3Z brief含む], eval/, metrics_01.json, eval_summary_01.json, page_content_01.json, gen_summary.json, raw_usage_log.jsonl)。スクリプト: `er059_melos_sol_b3z_trial_01.py`(生成)、`_eval.py`(機械指標・AI評価)、`_page.py`(比較ページ生成)。
- 比較ページ: user_test/family_z_melos_sol_b3z_01/index.html
- 結果要点: AI評価平均 (1)4.10 / (2)4.20 / (3)4.10(N=2、有意差なし)。B3Zは追加脚色を抑え感情・結末は良いが中心Story(王の改心)は(1)に及ばず、B3Zの優位は確認できず。
- Production Writer/Prompt/Routing/pricing/CURRENT_SPEC は無変更(新規routing keyも追加せず、gpt-6.1-solはroutingのFAMILY_X_FACTLOCK_R0値とのassertのみ)。
