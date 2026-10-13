# FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_01(初回)

(注: sandwich-pm受領文の保存。長大な固定ブロック[E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3]は要旨で保存。)

## 管理ID
FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_01(初回)。親ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 §6「英文・音声分割の改善Trial」(ユーザーTrial実施承認済み、判定ロジック側と独立並行可)。並行タスク: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01(別sonnet-worker、ACTIVE_TASK_ASRGEN.md/RESULT_PACKET_ASRGEN.md、出力er068_output/、SSOT編集権あり)。本委任はSSOT編集権なし(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/USER_DECISION_REGISTER_01/REPORT_LEDGER/PM_GOVERNANCEを編集・addしない。追記文案はRESULT_PACKETに記載のみ)。一時ファイルはdocs/pm/ACTIVE_TASK_SPLIT.md/RESULT_PACKET_SPLIT.md。er068_*には触れない。git: .git/index.lock存在時は30秒待ち×3回、commit前にgit fetch origin && git merge --ff-only origin/main(不可ならgit pull --no-rebase、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Production非変更)。Phase 1=JPY0(原稿・分割ルール設計+既存原稿への机上適用+影響範囲)、Phase 2=有料小規模検証(TTS Standard同期+ASR、Trial隔離)。
- 到達上限Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED。APPROVED_FOR_PRODUCTION/Production自動採用は禁止。
- 費用: 上限JPY100(Guardrail。PM_GOVERNANCE 7-7によりFable判断承認済み)。T-3定型文に従う。Phase 2開始前に設計(セル数×take数×単価、出典付き、未確認は「未確認」)をplan_01.mdに事前登録。JPY100超見積は縮小。
- 禁止: git add -A/-f、amend/rebase/force push、stash/clean/reset --hard/checkout -f、.envのsource・値表示、秘密値出力、*.wav・**/telemetry.jsonl・**/evidence_*/**/*.log・words/のadd、ACTIVE_TASK*.md/RESULT_PACKET*.mdのcommit、Production経路ファイル(er062_*, er063_*, er013_*, er026_*, er003_*, er006_*, er011_*, er020_*, er021_*)の編集、Melos run_e2e_02配下・Master Store・HR queue・attempt_history.jsonl・pronunciation ledger・共有telemetryへの書込(出力はer069_output/配下に限定)、Melos Production再生成・試聴ページ更新・HR Lock操作、文章の不自然な書換え・音声構成の大幅変更の提案、外部停止プロセスの再起動、監督ループ/timeoutラッパ、有料runのkill、Batch TTS。
- STOP確認義務: 開始時にer026_output/family_z_production_e2e_01/配下のSTOP_NOTICE/STOP/STOP_ALLを確認し記録(Melos STOP_NOTICEはrun_e2e_01向け旧記録=本IDに非適用)。
- Opus独立技術レビューGate: 非該当(Production採用提案時に条件Cで別途)。
- 最新モデル原則: TTSはProduction同一gemini-3.8-flash-lite-tts(例外理由=比較可能性)、ASRはProduction同一(OpenAI gpt-4o-mini-transcribe+Azure STT Phrase List)、局所参照にfaster-whisper可。応答model_id実測を記録。

## ユーザー指示(原文)
(2026-10-13、ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 §6)「こちらはユーザーがTrial実施を承認済み。判定ロジック側の検討とは独立して並行実施してよい。検証対象: 固有名詞の語末と後続語頭の子音連続を避ける自然な英文構成/極端に短いナレーターclipを避ける分割方法/原文の自然さ、ストーリー性、音声品質への影響。ただし、文章の不自然な書き換えや、音声構成の大幅変更は避ける。このTrialも、Productionへの自動採用は禁止する。」「今回の目的は、Melosを通すことではなく、同種の問題が量産時に繰り返されない仕組みを確立すること。個別ケースがPASSしただけではTrial成功とは判定しない。」(§8)「有料検証を追加する場合は、既存の委任・予算承認範囲を確認し、未承認の費用が発生する場合はSTOPすること。」

## 作業内容(要旨)
Phase 1(JPY0): P1-1 現状棚卸し(Melos run_e2e_02 Std/Adv全clipの narrator語数分布、語末歯擦音+語頭歯擦音の境界[固有名詞/一般語別]、attribution clip一覧、他原稿3本)→inventory_01.md/json。P1-2 ルール候補R1(原稿側)/R2(分割側)の設計(作品非依存の音声的条件、適用先、変更規模、影響範囲、副作用)。P1-3 Melos原稿への机上適用before/after。P1-4 Phase 2設計の事前登録(plan_01.md、2x2交絡分離、費用見積)。
Phase 2(有料、上限JPY100、R1/R2候補成立時のみ): er069_attribution_clip_split_trial_01_gen.py/_measure.py。TTS_EXECUTION_MODE=STANDARD。出力er069_output/attribution_clip_split_trial_01/。cost_01.json、結果表(セル別PASS率、減速前/後/Adv、綴り一致率、HR相当率)、長さ効果/s+s回避効果/交互作用を分けて記載。state_guard_01.json。
Status: VALIDATED(R1/R2がMelos以外でも通過率改善+自然さ劣化なし+Production変更小規模+各セルn>=4)/REJECTED/USER_DECISION_REQUIRED。Melosの1clip PASSだけではVALIDATEDにしない。

## Git
SSOT編集権なし。明示add: er069_attribution_clip_split_trial_01_*.py、er069_output/attribution_clip_split_trial_01/**/*.{md,json}(wav/log不可)、本ファイル(+_check.json)。コミットメッセージ: 「FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_01: 固有名詞歯擦音境界・短尺narrator clip回避ルールのTrial(Phase1 JPY0 / Phase2 JPY<実費>、Status=<判定>、Production無変更・採用判断なし)」trailer Managed-ID: FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01。commit前にsecret_scan、git status --porcelainで意図外ファイル不在を確認。push。

## 報告
docs/pm/RESULT_PACKET_SPLIT.mdに(0)〜(9)(check結果・STOP確認、inventory要約、R1/R2案、before/after、Phase2設計と結果、Status、費用、SSOT追記文案、未解決、commit/URL)。docs/pm/ACTIVE_TASK_SPLIT.mdに固定ヘッダ。
