# OPEN-258-JA-SECONDARY-ASR-PHASE0-TRIAL-01 委任_01 (2026-10-11)
範囲: V1方式のPhase 0限定検証(Trial専用script、Production未変更)。上限5円(Azure STTのみ)。

## 実施
- 事前登録 PREREGISTRATION_01.md(見積4.58円(保守)<=5円を確認後にAzure実行)
- 対象: META 3 + 設計書14群(保存音声全て存在、欠落0)+誤PASS検証C群5+プローブ1(計25 call)
- Azure 25回(Phrase Listなし、ja-JP)、whisper small/medium補助(課金0)
- 原稿はattempt_history/lock stateのsha256照合で確定(設計書のproxyと差がある例を記録)
- SSOT: DECISION_LOG Trial記録1エントリ、OPEN_ITEMS OPEN-258追記(close せず)。CURRENT_SPEC不変。Production code不変。
- 証跡: er053_output/open258_phase0_trial_01/(RESULT_01.md、results_01.jsonl 他)
- 実測費用: 約4.01円(音声90.2秒x0.0444円/秒、保守4.58円)。他課金0。
## 運用メモ
- 並行agentが同一working treeでDECISION_LOG/OPEN_ITEMS/ACTIVE_TASKを編集・stage中のため、自分のhunkだけを一時indexでcommit(他agent分は混ぜない)。
