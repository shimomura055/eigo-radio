# 委任_01A: JA-ASR-V2-BETA-PRODUCTION-WIRING-01 — 配線設計(実装前、API 0)
担当: sonnet-worker。Fable発。ユーザー原文=`docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md`(§1A・§3を全文読む。これが目的の正本)。

## 受入基準(Fable 4-2固定様式を適用。受領≠受入)
当初目的=ユーザー原文§3-1〜3-5。本委任はその「設計書」段階。成功最終成果物=`docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/WIRING_DESIGN_01.md`(+`COVERAGE_MATRIX_01.md`, `TEST_PLAN_01.md`)。失敗経路=設計上の矛盾・承認範囲外が判明したら、実装へ進まず`判断候補`として報告(ファイルはそのまま残す)。

## 開始時
- `tools/stop_scope_check_01.py --managed-id JA-ASR-V2-BETA-PRODUCTION-WIRING-01 --out docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/stop_check_01A.json`(rc=3なら停止)。run-dir無し=全NOTICE適用。
- 正本の読込: `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/{EVAL_UNIFIED_03.md, DESIGN_PROPOSAL_01.md, RESIDUAL_NG_ANALYSIS_01.md, OPUS_REVIEW_01.md, PREREGISTERED_03.md, proto_unified_03.py(+test)}`、`USER_DECISION_REGISTER.md`の#201〜#207(Grep)。

## やること(すべて読取+設計文書。Productionコード編集禁止)
1. **現行Production経路の特定(file:line)**: er078統一judge(Primary OpenAI→Secondary Azure→F1 READING_MATCH final AND / E3・E4 Candidate-E guard)、er007 secondary adapter(`JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED`等)、er011 variant層、X/Y/Z各runnerの日本語音声ASR呼出点、retry(3回NG→HR Lock)/fallback/regeneration/resume、er006 master_audio_store再利用(manifest・reuse_telemetry)、human_review_queue、HUMAN_APPROVED記録。
2. **COVERAGE_MATRIX_01.md**: Family X/Y/Z × Level(Std/Adv) × Section(日本語題/Preview/Comment/KP日本語意味/その他)で「日本語音声あり→ASR judge経路あり/なし(file:line)」「対象外の理由」。一部Familyだけで完了としない。
3. **WIRING_DESIGN_01.md**:
   (a) proto_unified_03のL1(v2読み規則+irregular-reading guard)・L2(β=SecondaryをValue witness)を、Production judgeのどの関数境界へどう移植するか(X/Y/Z共通の1箇所)。**持ち込まないもの**: L3別表、合意再試行M-3、ASR再試行、超→こえ辞書、R-1(持ち込まない=OFF。R-1コード自体を入れない案と入れて固定OFFにする案を比較し推奨を書く)。
   (b) 維持するもの: F1+F2、E3/E4(M-6構造ガード)、βのSecondary fail-closed(Secondary不可/不一致時は従来判定へ)、数値・桁・助数詞・脱落NG検出。
   (c) PASS_W識別: 判定結果schemaに`verdict`(PASS/PASS_W/NG/HR)・`warning_labels`・`rescue_basis`(v2|beta)・`judge_rule_version`を追加する案。保存先=ASR結果json・audit・Store manifest(再利用時に警告を引き継ぐ)。
   (d) 非ブロッキング: PASS_WはGate通過=PASSと同等に扱い、retryを終了し、HR Lock・human_review_queueへ送らない。通常NG・3回NG HR Lock・E3/E4 NG・既存明示HR Lock・HUMAN_APPROVED記録は不変。自動配信・公開機構は作らない。
   (e) 最終制作報告への掲載: X/Y/Zの各runnerの「最終制作報告」artifactを特定し(file:line)、対象音声・発生理由・警告内容を掲載する設計(共通helper)。
   (f) 既定ON(APPROVED_FOR_PRODUCTION)で配線。緊急OFF用flagの要否は論点として両案を書く(Fable/Opus判断)。
   (g) 汎用性: 題固有語・記事固有語を含まないことの担保(test)。
   (h) 変更ファイル一覧と影響範囲(Family A/B/Cへ共通基盤変更が及ぶ場合は互換性確認のみ)。
   (i) 撤去要否: 旧ルール・旧検査で不要になるもの(Charter原則8)。
4. **TEST_PLAN_01.md**: 既存regression(er078/er007/er011/各runner test)一覧+新test(月6本の保存draw→4 PASS_W/2 HR再現、N3 30負例+拡張負例の誤PASS増分、汎用題positive、PASS_W非ブロッキング[retry終了・HR未送]、Store再利用warning引継ぎ、resume、E3/E4整合、X/Y/Z runner integration[mock ASR])。runtime evidence計画(実音声でProduction judgeを実走: 月6本wav等、model_id・routing・判定規則の証跡、ASR実費見積)。
5. **費用見積**(委任_02A実走分。300円超なら事前承認要と明記)。
6. **UDR整合表**: ユーザー決定§1A-1〜4+PASS_W非ブロッキング ↔ UDR #201〜#207の対応(どれが判断済みになったか)。#203(月題採用)は本IDで扱わない。

## 範囲(PM_GOVERNANCE 11-8)
範囲内=ユーザー承認済み仕様(2026-10-29)の配線設計、承認済み仕様との矛盾の是正、Regression・検証。範囲外=受理面・閾値・方式の新設/拡大(L3別表、ASR再試行、超→こえ、新規読み規則、R-1 ON)、Family A/B/C、記事『月は少しずつ縮んでいる？』の公開差替え・FX-MOON-SHRINKING判断の代行、自動配信機構。公開前人間試聴必須条件の復活は禁止(原文§1A末尾)。

## 報告
`docs/pm/RESULT_PACKET_JAW1.md`(gitignore対象の一時ファイル)に: 整合/未承認機能/成果物と目的適合/撤去・残置/判断候補(停止根拠をfile:lineで)/費用/commit hash。`判定整合:`行を末尾に。本委任文は保存済み(本ファイル)。commit: 新規docsのみ`git add`明示→`git push origin HEAD:main`。`docs/pm/ACTIVE_TASK.md`の(I)行を結果で更新(他行は触らない。並行Worker(J)あり=編集直前にRe-Read)。
