# BASELINE_01: 従来方式(1)の既存成果物確認(再生成しない)

管理ID: FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 委任_01 / 2026-10-12 / Status: Trial(VALIDATED止まり)

## 特定した既存成果物(事実)
- Story本文(原出力): `er018_output/fiction_external_seed_selection_criteria_trial_02/stories/03_japanese_lit_2/story.md`(385語。タイトル `The Three-Day Promise`)
- Seed: 同ディレクトリ `seed.json`(Seed生成モデル gpt-5.6-luna、`seed_api_meta.json`)。Story Prompt: `story_prompt.txt`(Seed要素6件+conversion_plan+共通原則+A2・280〜420語・主人公のみ固有名)
- 生成メタ: `api_meta.json` = model `gpt-5.6-luna`、effort `high`、attempt 1で成功(response_id記録あり)
- Production化された版: `er026_output/family_z_production_e2e_01/melos/run_01/article.md`(383語)。Trial story.mdから決定論的な人名復元(Selinuntius/Dionysius、LLMなし、sha `ff93d8a5...`→`bd40ab4d...`)のみを施した版。Family Z Production Phase 1(Preview/Comment1/In One Line/KP)の入力。
- 費用記録: `er018_output/.../trial_02/cost.json` 全体(10 record)で約1.76円。Story 1 callの個別費用は `raw_usage_log.jsonl` から再算出可能(今回は再利用しないため未集計)

## 実際の工程(R0->R1->R2は存在しなかった)
**従来方式は単発生成**: Seed生成(gpt-5.6-luna) -> Story生成1 call(gpt-5.6-luna、effort=high、Developer=`WRITER_DEVELOPER_MESSAGE`、User=story_prompt.txt)のみ。R0/R1/R2(=Original->Revise->Revise)、B3、リビジョンは**存在しない**。Production runner(`er026`)でも本文は再生成せずTrial story.mdを再利用(人名復元のみ)。
- 注: Lunaのモデル世代は gpt-5.6-luna(当時のTrial時点の最新。現行Production routingの gpt-6-luna ではない)。

## 再利用可能性の判定
- (1)の本文・Seedは**再生成せず、story.md(原出力)をそのまま(1)として使用**する(Trial story.mdとProduction article.mdの差は人名復元のみ。比較は原出力で行い、人名ルール[主人公のみ固有名]を同一条件にするため)。
- Seedは(2)(3)と同一のraw seed(`story_prompt.txt`のSeedブロック逐語)を使用。
- 条件差の注意(比較の限界、Trial内で開示): (1)は gpt-5.6-luna 単発、(2)(3)は gpt-6.1-sol 3工程。比較は「現行従来方式 vs 提案方式」であり、モデル差と工程差が(1)と(2)の間で交絡する。(2)対(3)はB3Z有無のみの純粋比較。
- 語数: 385語、A2メトリクス: 平均7.26語/文、最長15語、長語候補6(executions, disappeared, attackers, whispered, remembered, execution)。
