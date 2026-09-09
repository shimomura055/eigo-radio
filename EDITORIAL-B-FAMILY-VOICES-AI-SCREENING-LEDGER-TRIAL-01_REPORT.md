# EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01 Report

Lane: Lane B(B Family Voices-Perspective)。Trial(Production変更なし)。
4V本文Trial(テーマ固定、4V=案A)に先立ち、検証済み4-Voice Verified Fact
Ledgerを本Trialだけで先に作成した。Production Prompt/registry/本文生成・
SSOT・Git操作は一切行っていない。

## Reconciliation Check(結論のみ)
B-Family Voice Ledgerの実際の先例(Trial-04〜07)は、いずれも
`er011_open112_engagement_reference_cross_topic_ab_trial_11.py`由来の
`_perplexity_call()`パターン(Perplexity sonar-pro、Stage 1B fact
research/Stage 2B独立verification)を各Trialファイルへ無変更のまま
再実装したものであり、`er002_ja_web_research_r3.py`のWriter用web_search
関数(A-Family全文生成の一部として設計、schemaも異なる)ではない。本
Trialでは既存の`_perplexity_call()`実装を無変更のまま`er012_ai_screening_
ledger_trial_01.py`へコピーして再利用し、新規Research primitiveは実装
していない。詳細はledger_build_log.json参照。

## 実施内容
1. Research(Stage 1B/2B) Round 1: テーマ全体・4立場でfact 22件収集、
   20件CONFIRMED・2件PARTIALLY_CONFIRMED(Fact Safety優先で不採用)。
2. Round 1実査でNYC Local Law 144関連にfairness_legal_hr_governance側が
   偏っていることが判明したため、Round 2で追加Research(fact 19件、
   全件CONFIRMED)。個人の実例(BBC/CVS訴訟)・定量ROI事例(Hilton/IBM/
   Netscribes/Vitae.ai)・EU AI Act等を補充。
3. 手作業でcurationし、Voice各5件・CROSS_REFERENCE 2件(計22件)を主要
   根拠として`research/verified_fact_ledger.txt`(Trial-07形式)へ収録。
   不採用としたfactは理由付きでLedger末尾に明記。
4. `research/perspective_map.md`(4 Voice版)を作成。
5. 品質確認: `er012_b_family_editorial_type_registry_01.build_voice_
   attribution_block()`をread-only importで呼び出し、VOICE_1〜4タグを
   正しく抽出することを確認(OPEN-131修正タスクのregistry自体は無編集)。
   `er002_ja_web_research_r3.build_fact_check_prompt()`もread-only呼び出しで
   互換性確認(実際のFact Checker API呼び出しはしていない)。

## Gate 1分類: VALIDATED
形式互換(Trial-07とfield labels完全一致、タグ拡張のみ)・全22件
CONFIRMED・4 Voice代表性ありと判断。Production採用判断は本Trialの範囲外。

## 費用実測
Perplexity API公式usage.costの合算: 0.35173 USD(約53〜55円、上限¥150
に対し余裕あり)。内訳・生ログはledger_build_log.json、raw_usage_log_
ledger_trial01_research*.jsonl参照。

## 新規ファイル
- `er012_ai_screening_ledger_trial_01.py`(Trialスクリプト)
- `er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt`
- `er012_output/ai_screening_ledger_trial_01/research/perspective_map.md`
- `er012_output/ai_screening_ledger_trial_01/research/ledger_build_log.json`
- `er012_output/ai_screening_ledger_trial_01/research/raw_facts_research_4voice.json`
- `er012_output/ai_screening_ledger_trial_01/research/raw_facts_verification_4voice.json`
- `er012_output/ai_screening_ledger_trial_01/research/raw_facts_research_4voice_round2.json`
- `er012_output/ai_screening_ledger_trial_01/research/raw_facts_verification_4voice_round2.json`
- `er012_output/ai_screening_ledger_trial_01/qa/voice_attribution_block_output.txt`
- `er012_output/ai_screening_ledger_trial_01/qa/fact_check_prompt_compat_check.txt`
- `er012_output/ai_screening_ledger_trial_01/raw_usage_log_ledger_trial01_research.jsonl`
- `er012_output/ai_screening_ledger_trial_01/raw_usage_log_ledger_trial01_research_round2.jsonl`
