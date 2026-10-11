# FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 報告 (2026-10-11)

Status: USER_DECISION_REQUIRED (設計案のみ。Production変更なし、有料API 0円)
使用モデル: 実行層 Sonnet 5.5。評価用の有料LLM/ASR/TTSは不使用。ローカルfaster-whisper small/mediumのみ(参考指標、費用0)。

## 成果物(すべて er056_output/en_asr_confirm_retry_redesign_01/)
- CURRENT_SPEC_SURVEY_01.md 現行仕様(a)-(g)・フロー図・SSOT/コード行索引・所見F-1..F-8
- COFFEE_NG_ROOTCAUSE_01.md Coffee Standard full_story_part2 NGの根本原因(確認済み証拠のみ)
- TARGET_FLOW_DESIGN_01.md 目標フロー差分(10項目)・例外表・リスクR-1..R-7・決定候補D-1..D-11
- FREE_VERIFICATION_01.md 保存音声/転記による無料検証(replay、ローカルASR、mutation test、medium追試)
- QCD_COMPARISON_01.md 報告11項目のQCD比較(過去160 call再計算)
- evidence_snapshot/(sha256付き、Coffee worktreeはread-onlyコピー)、er056_en_asr_retry_replay_01.py、er056_en_asr_local_wav_check_01.py、各result JSON/log

## 要点
- 根本原因: 6%減速後処理がPrimaryのみで再検証し、NGなら外側ループで全体を再実行する構造。fallback attemptのNGは強制Azureが原因(転記は重複排除で消失)。Local Rewriteは無関係な箇所を書き換えた。Coffeeの総費用にはAzure分が未計上。確定した音声欠陥の証拠はない(standard 1回目とLR音声は未確認)。
- Coffeeはmain未マージのworktree branch(F1.5 Style)で実行。mainとは差がある。
- 無料検証: AzureはOpenAI/ローカルASRと不一致が多く、権威ではなく救済用に限定すべき。ローカルASRは代替にならない(mediumでも対照13件中12件がNG判定=寄せ集めで偽PASS率の推定には使えない)。
- 設計案の概算: 完了率91.9-95.6%(現行93.1%)、1 call費用 約0.39円 vs 案0.23-0.25円。TTS最大3回。
- 追加Trial案(未実施): T-1 約80円(上限120円)、T-2 10-15円。有料のためSTOP。

## ユーザー決定が必要な点
D-1..D-11(TARGET_FLOW_DESIGN_01.md参照)。主なもの: Local Rewrite通常retryからの除去、minimal fallback廃止、6%減速の扱い(案B/C)、Secondaryの位置づけ、Trial実施可否と予算。

## Gate注意
新しい構造・処理フロー設計に該当するため、実装前にOpus独立レビュー(Gate条件A)が必須。本委任では未実施。Fableが手配すること。

## 禁止事項の遵守
ACTIVE_TASK.md/RESULT_PACKET.md、worktree eigo-radio-tone、Production code/Prompt/Validator/Routing、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSは未編集。SSOT記録は後続委任。
