# 委任_02 PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 (2026-10-08)
(委任文の要約保存。Opusレビュー全文は docs/pm/opus_l2_review_production_model_routing_gpt6_wiring_01.md に逐語保存)

## 管理ID
PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(委任_02: Opus条件Cレビュー保存・計画書v2・Phase 0互換probe)。Production code編集なし。並行: FACTLOCK-WRITER-REDESIGN-TRIAL-01(書込先 er052_output/factlock_writer_trial_01/ と docs/pm/RESULT_PACKET_FACTLOCK.md には触れない)。

## 性質/到達上限Status/禁止事項
- 性質: 設計更新+互換性probe(Trial harness経由、Production code不変)。到達上限Status: PROBED。
- Production code編集禁止(er006_*/er019_*/er012_*/er003_*/er026_*/er018_*/gather_topic.py/er002_*/pricing_snapshot.json等は読み取りのみ)。
- 禁止: er052_output/factlock_writer_trial_01/・docs/pm/RESULT_PACKET_FACTLOCK.mdへの書込。git add -A・破壊的git禁止。
- 費用: 上限¥30(Guardrail、自動STOP閾値ではない)。probeは各工程1〜2 call、並列2まで。暴走疑い時のみSTOP。
- Opus条件C実施済み。Fable判断: M1〜M6採用、O1/O2/O3採用(O2はPhase 0 probe結果次第)。

## ユーザー指示(原文)
「判断7(新規): 全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」(2026-10-08)。

## 実行内容
1. 委任文保存+check_delegation_prompt。2. Opusレビュー保存+OPUS_FINDINGS_LEDGER登録。3. 計画書v2(Phase 0 probe→1 単価+fail-closed→2 定数+直書き一括→3 Production E2E 1本、F1/F2/F4/F5修正箇所一覧、M6 test更新案、切り戻し、受入M3、O3再評価トリガー)。4. er052_gpt6_wiring_probe_01.py(新規)で未確認工程を1〜2 call probe(--budget-jpy 30 --parallel 2)、PROBE_SUMMARY.md。5. 単体テストer052_gpt6_wiring_probe_01_test_01.py。6. git diff HEAD --statでProduction無差分確認。
SSOT: OPEN_ITEMS OPEN-241行末追記、ACTIVE_TASK更新、DECISION_LOG追記なし。
Git: 明示addのみ、コミットメッセージ「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_02: Opus条件C(M1-M6/O1-O3採用)・配線計画v2・Phase 0互換probe [OK x/NG y]、実費¥X/¥30、Production変更なし」、push origin main。
報告: docs/pm/RESULT_PACKET.md上書き(Status=PROBED、推奨は書かず事実のみ)。
固定ブロック E-1/D-1/G-1/F-1/T-0/T-1/T-2(TTS禁止)/T-3 適用。
KPI provenance: Phase 0 probe結果は fresh(probe harness、production_formal_pathではない)。E2E自己確認: No。
