# ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01(初回) 委任文(要約保存)

注: 受領した委任文の全文ではなく、構造を保った要約保存(全文はFableが保持)。T-0記録用。

## 管理ID
ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01(初回)。並行: FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01(別agent、er069_*)。一時ファイルはACTIVE_TASK_ASRGEN.md/RESULT_PACKET_ASRGEN.md。

## 性質/到達上限Status/禁止事項
- 設計方針のRepo記録+既存機構ギャップ整理+一般化判定方式の設計+既存データでのread-only検証(費用JPY0)。Production code/Validator/Gate変更なし。
- 到達上限Status: 設計=DESIGN_DRAFT(Opus条件Aレビュー待ち)、検証=VALIDATED/REJECTED/USER_DECISION_REQUIRED。APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED宣言禁止。
- 費用上限JPY0。有料API禁止。
- 禁止: git add -A/-f、amend/rebase/force push、stash/clean/reset --hard、.env表示、秘密値出力、telemetry.jsonl/evidence log/wav/wordsのadd、ACTIVE_TASK*/RESULT_PACKET*のcommit、Production経路ファイル(er006/er011/er003/er020/er021/er025/er026/er062/er063)編集、er065既存test/script編集、共有telemetry追記、Melos専用hardcode、CURRENT_SPEC編集。
- STOP確認: er026_output/family_z_production_e2e_01配下のSTOP系を確認・記録。
- Opus条件A該当: 実装前の設計草案まで。

## 作業内容
A. docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md 新規(必須8項目+用語定義+判断手順+安全条件+Melo/Mello非対称)
B. er068_output/asr_phonetic_equivalence_generalization_01/GAP_MAP_01.md(7段x機構、6経路x配線4区分、PM_GOVERNANCE21節A/B/C)
C. DESIGN_DRAFT_01.md(推奨方式1つ、発音確認手段、7段判定表、安全条件、6経路適用、hardcode禁止担保、規模/回帰/費用、Opus論点)
D. er068_asr_phonetic_equivalence_generalization_01_offline.py + _test_01.py: Trial隔離プロトタイプ、既存データのみ、評価A/B、Pattern A比誤PASS増分、減速前後一致率、state_guard_01.json
E. SSOT: DECISION_LOG、OPEN-339新規、OPEN-122/318/327/328/330/331/335追記、UDR #41/#25追記、REPORT_LEDGER行。CURRENT_SPEC編集禁止。

## Git
コミット2つ(成果物/SSOT)。trailer Managed-ID。明示addのみ。secret_scan後push。
