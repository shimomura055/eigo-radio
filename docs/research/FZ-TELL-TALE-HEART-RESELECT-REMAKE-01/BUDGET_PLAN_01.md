# BUDGET_PLAN_01 (FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 委任_01、2026-10-27)
Cap: 本案件 150円(新規run `run_reselect_01` 全体)。日次1,000円(JST)。2026-10-27当日の既消費は約111円(ACTIVE_TASK記載)。

## 見積り(根拠=実測先例)
| 工程 | 内容 | 見積(円) | 根拠 |
|---|---|---|---|
| Phase1-A `kp`(両level) | Part2文法候補抽出+Top1/Top2解説全文事前生成(両level)+KP候補生成(最大7+5/level)+gloss整合+QA | 8〜15 | AI島 文法事前生成 1.16円+scaffold 1.73円(GRAMMAR_PREP/BUILD_01)、run_chunk_01 kp stage 1.0円(再利用)+KP候補生成のLLM(Luna級)数円 |
| Phase1-B 本文TTS | Std/Adv story clip(Narrator/Dialogue、Adv chunk 4件)+ASR(Primary/Secondary)+retry | (Phase 2へ) | run_chunk_01実測 tts_b1b 6.85+tts_a2 9.68=16.5円。runnerはKP確定+文法確定前のTTS起動をload_level_inputsの入口assertで拒否するため選定前には走らせられない |
| Phase2(参考) | 確定後: Adv解説+Part1+訳+KP音声+本文TTS+assemble | 約25〜35 | run_chunk_01 計16.67円(KP再利用) + KP/解説音声・Part1・retry余裕 |
| 合計見込み | | 約33〜50円 | Cap 150円の1/3以内 |

判定: Cap 150円内(超過見込みなし)。Phase1の有料実行は `kp` stage 1回のみ(approved-budget-jpy 30)。各実行前後に stop_scope_check と cost_log実費を記録する(BUDGET_LOG_01.md)。
