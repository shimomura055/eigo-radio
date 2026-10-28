# PM_AUDIT_02_CROSSCHECK(A8 横展開点検、JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02A、read-only・API 0)

## 1. 方法と限界
- 対象: `OPEN_ITEMS.md`の`| OPEN-`行のうち「VALIDATED(限定)」「保留」「推奨現状維持」「実測後」「ユーザー判断待ち」「判断候補(D」のいずれかを含む行(機械抽出、script=一時、結果=本書)。全118行(POST_USER_VALIDATION[起票日>=2026-09-14]=94、PRE=24)。
- 各列は機械判定: **UDR登録**=`USER_DECISION_REGISTER_01.md`内に当該OPEN-IDを含む行があるか(#番号)。**再提示trigger/期限**=その登録行に「Deferred/再提示/トリガー/期限」の語があるか。**目的達成度**=OPEN行に「目的達成度」の語があるか(POSTでOPEN-515のみ[本委任で追記])。**見出し状態**=行頭420文字に未決語[OPEN候補/ユーザー判断待ち/USER_DECISION_REQUIRED/DEFERRED/未承認/保留/承認待ち/PENDING等]があり、完了語[CLOSED/RESOLVED/PRODUCTION_WIRED/REJECTED/SUPERSEDED/APPLIED等]が無いか。
- 限界: 本文後半の追記で解消済みの行は見出しだけでは判別できない(偽陽性あり)。登録有無・trigger語はID文字列一致で、意味的な適合(A4=指標が当該原因を測るか)は未判定。判断・登録・Status変更はFable。本書はOPEN/REGISTERを編集していない。Family A/B/Cに該当しうる行は「対象外(27-7)」とだけ記す(下表の列)。

## 2. 要注意: POST・見出し未決・UDR未登録(36件)
これらは「未決の語が見出しにあるのに登録も再提示triggerもない」行。多くは2026-10-11/12のOPEN候補群(C-18=10-12制定前後)。

|OPEN|起票日|見出し(抜粋)|ヒット語|UDR|trigger/期限|目的達成度|備考|
|---|---|---|---|---|---|---|---|
|OPEN-224|2026-09-28| T1(英語化Trial限定抑制追記)はHormuz/Meta双方で各1セルMAJOR Deviationを出しており、Production|保留|無|無|無|要確認|
|OPEN-229|2026-09-28| Production のJA音声(Standard preview/comment)に役割別Role Style機構が存在せず、常に長文i|ユーザー判断待ち|無|無|無|要確認|
|OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01|2026-10-05| OPEN-233 Stage 1 Checker再検証・改善Trial+PM Failure RCA(2026-10-05ユーザー指示、親|本文のみ|無|無|無|要確認|
|OPEN-237|2026-10-06| Fact台帳の明確化(上流対策)設計: `OPEN-233-LEDGER-CLARITY-DESIGN-01`、2026-10-06起票。|本文のみ|無|無|無|要確認|
|OPEN-238|2026-10-07| 承認済みChecker構成でRewriteが無関係文へ置換する誤動作(ai_control P2 rep2 cycle1、fact_id紐|ユーザー判断待ち|無|無|無|要確認|
|OPEN-248|2026-10-10| B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 Phase 2完了・Status提案=VA|本文のみ|無|無|無|要確認|
|OPEN-257|2026-10-11| PHONOLOGICAL-COLLISION-PROPER-NOUN-TTS-ASR-FAILURE-01 OPEN・包括対策は未承認、T|本文のみ|無|無|無|要確認|
|OPEN-263|2026-10-11| SCG-HETEROPHONE-GUARD-READING-DICTIONARY-GAP-01 OPEN候補・未承認(2026-10-11|本文のみ|無|無|無|要確認|
|OPEN-264|2026-10-11| FAMILY-Z-STORY-QUALITY-THRESHOLD-AND-HUMAN-READING-CALIBRATION-01 OPE|本文のみ|無|無|無|要確認|
|OPEN-265|2026-10-11| FAMILY-Z-LOW-SCORE-PREDICTS-EN-RETELLING-FAILURE-UNVERIFIED-01 OPEN候補|本文のみ|無|無|無|要確認|
|OPEN-266|2026-10-11| FAMILY-Z-ORIGINAL-LANGUAGE-SOURCE-AI-UNDERSTANDING-QUALITY-01 OPEN候補・|本文のみ|無|無|無|要確認|
|OPEN-267|2026-10-11| FAMILY-Z-STORY-POOL-L05-KOUBI-HANDLING-AND-SOURCE-EDITION-RIGHTS-01 O|本文のみ|無|無|無|要確認|
|OPEN-268|2026-10-11| ER054-STORY-POOL-TRIAL-02-TEST-CP932-MOJIBAKE-FIX-01 OPEN候補・未承認(2026-|本文のみ|無|無|無|要確認|
|OPEN-269|2026-10-11| FAMILY-Z-STORY-EVAL-METRIC-IMPROVEMENT-CROSSREF-01 OPEN候補・未承認(2026-10|本文のみ|無|無|無|要確認|
|OPEN-272|2026-10-11| PROPER-NOUN-HEURISTIC-TOO-COARSE-JA-C1-KATAKANA-RATIO-EN-CAPITALIZED-|本文のみ|無|無|無|要確認|
|OPEN-273|2026-10-11| TRANSIENT-API-FAILURE-CONSUMES-TTS-ATTEMPT-01 OPEN候補・未承認(2026-10-11起票|ユーザー判断待ち|無|無|無|要確認|
|OPEN-274|2026-10-11| LOCAL-REWRITE-RETTS-DEPENDS-ON-MINIMAL-FALLBACK-STYLE-CHANGE-AND-SPAN|本文のみ|無|無|無|要確認|
|OPEN-278|2026-10-12| AUDIO-ANOMALY-DETECTION-NONBLOCKING-WARNING-VALIDATOR-PROPOSAL-01 DEF|保留|無|無|無|要確認|
|OPEN-279|2026-10-11| TONE-TRIAL-AUDIO-TRIAL-ONLY-CONDITIONS-REGEN-NEED-ON-ADOPTION-01 OPEN|本文のみ|無|無|無|要確認|
|OPEN-282|2026-10-12| ATTEMPT-HISTORY-SIZE-MONITORING-ARCHIVE-DUPLICATES-REUSED-SEGMENTS-01|本文のみ|無|無|無|要確認|
|OPEN-285|2026-10-12| COST-AGGREGATORS-ZERO-YEN-FOR-UNPRICED-GEMINI-OPENAI-VS-AZURE-HALT-PO|ユーザー判断待ち|無|無|無|要確認|
|OPEN-286|2026-10-12| UNIFIED-FLOW-INTRODUCTION-PREREQUISITES-WARNING-LISTENING-LINK-LR-RET|ユーザー判断待ち|無|無|無|要確認|
|OPEN-287|2026-10-12| JA-NUMERIC-S1-KANJI-NUMERAL-BLIND-SPOT-NOTATION-VARIANT-FALSE-FIRE-01|ユーザー判断待ち|無|無|無|要確認|
|OPEN-288|2026-10-12| POINT-HEADINGS-STANDARD1-MINIMAL2-AND-PRIMARY-ONLY-PASS-OVERSIGHT-01 |ユーザー判断待ち|無|無|無|要確認|
|OPEN-289|2026-10-12| KP-SINGLE-PROMPT-CONTENT-P-A-P-B-V3-AND-MASTER-STORE-241-NOT-REUSABLE|ユーザー判断待ち|無|無|無|要確認|
|OPEN-290|2026-10-12| LOCAL-REWRITE-JA-NONE-FOR-NOW-AND-EN-AGREED-MISREAD-ONLY-TRIGGER-F5-P|ユーザー判断待ち|無|無|無|要確認|
|OPEN-291|2026-10-12| LANGUAGE-SPECIFIC-SECONDARY-SELECTION-JA-AZURE-EN-AZURE-OR-LOCAL-MEDI|ユーザー判断待ち|無|無|無|要確認|
|OPEN-293|2026-10-12| ADVANCED-FULLSTORY-PACE-PROMPT-ONLY-SLOWDOWN-INSUFFICIENT-OPTIONS-01 |ユーザー判断待ち|無|無|無|要確認|
|OPEN-294|2026-10-12| ADVANCED-FULLSTORY-WINDOW-WPM-250-WARNING-THRESHOLD-VALIDITY-01 OPEN候|ユーザー判断待ち|無|無|無|要確認|
|OPEN-297|2026-10-12| FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 結果の判断待ち OPEN候補・ユーザー判断待ち、20|ユーザー判断待ち|無|無|無|要確認|
|OPEN-331|2026-10-13| FAMILY-Z-HR-ADOPTED-TAKE-PLACEMENT-AND-STD-SLOWDOWN-EVIDENCE-01 USER_|本文のみ|無|無|無|要確認|
|OPEN-353|2026-10-13| KP-SUPPLY-FRAGMENT-PREVENTION-01 USER_DECISION_REQUIRED・C(2026-10-13起|ユーザー判断待ち|無|無|無|要確認|
|OPEN-369|2026-10-15| 欠陥②対策: 受入記録に失敗終了時最終成果物の目的要件照合を必須化(案・ユーザー承認待ち) 採用済み(2026-10-15ユーザー正式決定|本文のみ|無|無|無|要確認|
|OPEN-537|2026-10-26| FAMILY-Y-STYLE-PROFILE-WIRING-CHECK-01 種別=不具合(仕様と実装の乖離)、Status=是正実装完了|本文のみ|無|無|無|要確認|
|OPEN-561|2026-10-27| AI-ISLAND-FORM-PRODUCTION-01 AI島Std/Adv V3フォーム実運用・完成記事制作 種別=Productio|本文のみ|無|無|無|要確認|
|OPEN-565|2026-10-27| LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 LR・Fallback・M3 Gateの全Family横断監査(|ユーザー判断待ち|無|無|無|要確認|

## 3. 登録あり・trigger語なし・見出し未決(再提示条件が登録行から確認できない)
|OPEN|UDR|見出し(抜粋)|ヒット語|
|---|---|---|---|
|OPEN-306|#23| FAMILY-Z-MELOS-VOICE-APPROVAL-01 ユーザー承認待ち(2026-10-12起票、FAMILY-Z-MELOS|保留|
|OPEN-308|#23| FAMILY-Z-LEDGER-SYRACUSE-UNREGISTERED-MELOS-MISRECOGNITION-01 OPEN候補(|本文のみ|
|OPEN-316|#1,#99| COFFEE-STD-COMMENT4-BRIDGE-PROMPT-ADOPTION-01 USER_DECISION_REQUIRED・|本文のみ|
|OPEN-330|#119,#120| CONNECTED-SPEECH-PATTERN-A-STEM-FINAL-S-ACCEPTANCE-SCOPE-01 USER_DECI|本文のみ|
|OPEN-388|#83| AUW-A3-LENGTH-NG-IS-PRIMARY-DERIVED-NOT-INDEPENDENT-QA-01 OPEN候補・是正は委|本文のみ|
|OPEN-394|#85,#93,#94,#95| AUW-PRIMARY-LAYER-WRONG-TEXT-TTS-PASSES-AS-WRITTEN-01 USER_DECISION_R|本文のみ|
|OPEN-432|#5,#132| FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 PRODUCTION_TECH_COMPL|本文のみ|
|OPEN-474|#169,#171,#173,#178,#179| FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 2026-10-24 委任_20 Status|本文のみ|
|OPEN-497|#182,#185,#196| 最新Status=TRIAL08_VALIDATED_LIMITED(2026-10-25 委任_19: Fable独立評価でStatus|VALIDATED(限定)|
|OPEN-503|#188,#192,#193| FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 【2026-10-28最新: 公開版=Fenrir版でユーザ|本文のみ|

## 4. POST全件(94件)の機械判定表
|OPEN|起票日|ヒット語|UDR|trigger|目的達成度|見出し未決|見出し完了語|Family疑い|
|---|---|---|---|---|---|---|---|---|
|OPEN-165|2026-09-17|本文のみ|無|無|無|-|-||
|OPEN-179|2026-09-25|本文のみ|無|無|無|Y|Y||
|OPEN-186|2026-09-26|本文のみ|無|無|無|-|-||
|OPEN-211|2026-09-28|本文のみ|無|無|無|-|-|対象外(27-7)疑い|
|OPEN-220|2026-09-28|本文のみ|無|無|無|-|-||
|OPEN-221|2026-09-28|本文のみ|無|無|無|-|Y||
|OPEN-224|2026-09-28|保留|無|無|無|Y|-||
|OPEN-229|2026-09-28|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-231|2026-09-29|本文のみ|無|無|無|-|-||
|OPEN-233|2026-10-10|本文のみ|無|無|無|-|Y||
|OPEN-233-KPI-RECOVERY-REDESIGN-02|2026-10-04|本文のみ|無|無|無|-|Y||
|OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01|2026-10-05|本文のみ|無|無|無|Y|-||
|OPEN-237|2026-10-06|本文のみ|無|無|無|Y|-||
|OPEN-238|2026-10-07|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-240|2026-10-07|本文のみ|無|無|無|-|-||
|OPEN-241|2026-10-08|本文のみ|無|無|無|-|Y||
|OPEN-243|2026-10-08|本文のみ|#99|無|無|-|-||
|OPEN-244|2026-10-11|本文のみ|無|無|無|-|Y||
|OPEN-248|2026-10-10|本文のみ|無|無|無|Y|-||
|OPEN-255|2026-10-11|保留|無|無|無|Y|Y||
|OPEN-257|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-258|2026-10-11|本文のみ|無|無|無|-|Y||
|OPEN-263|2026-10-11|本文のみ|無|有|無|Y|-||
|OPEN-264|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-265|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-266|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-267|2026-10-11|本文のみ|無|有|無|Y|-||
|OPEN-268|2026-10-11|本文のみ|無|有|無|Y|-||
|OPEN-269|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-270|2026-10-12|本文のみ|無|無|無|-|Y||
|OPEN-271|2026-10-12|本文のみ|無|無|無|-|Y||
|OPEN-272|2026-10-11|本文のみ|無|有|無|Y|-||
|OPEN-273|2026-10-11|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-274|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-275|2026-10-12|本文のみ|無|無|無|-|Y||
|OPEN-276|2026-10-11|本文のみ|無|無|無|Y|Y||
|OPEN-277|2026-10-12|本文のみ|無|無|無|-|-||
|OPEN-278|2026-10-12|保留|無|無|無|Y|-||
|OPEN-279|2026-10-11|本文のみ|無|無|無|Y|-||
|OPEN-280|2026-10-12|本文のみ|無|無|無|-|Y||
|OPEN-281|2026-10-12|本文のみ|無|無|無|Y|Y||
|OPEN-282|2026-10-12|本文のみ|無|無|無|Y|-||
|OPEN-283|2026-10-12|ユーザー判断待ち|#119,#121|無|無|Y|Y||
|OPEN-284|2026-10-12|ユーザー判断待ち|無|無|無|Y|Y||
|OPEN-285|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-286|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-287|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-288|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-289|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-290|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-291|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-293|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-294|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-297|2026-10-12|ユーザー判断待ち|無|無|無|Y|-||
|OPEN-298|2026-10-12|ユーザー判断待ち|#100|有|無|Y|-||
|OPEN-300|2026-10-12|本文のみ|無|無|無|Y|Y||
|OPEN-306|2026-10-12|保留|#23|無|無|Y|-||
|OPEN-308|2026-10-12|本文のみ|#23|無|無|Y|-||
|OPEN-316|2026-10-12|本文のみ|#1,#99|無|無|Y|-||
|OPEN-320|2026-10-12|本文のみ|無|無|無|Y|Y||
|OPEN-330|2026-10-12|本文のみ|#119,#120|無|無|Y|-||
|OPEN-331|2026-10-13|本文のみ|無|無|無|Y|-||
|OPEN-338|2026-10-17|本文のみ|#23,#42,#44,#48,#51|無|無|Y|Y||
|OPEN-353|2026-10-13|ユーザー判断待ち|無|有|無|Y|-||
|OPEN-356|2026-10-14|保留|#70|無|無|Y|Y||
|OPEN-363|2026-10-15|本文のみ|#59,#62,#72,#79|有|無|-|-||
|OPEN-369|2026-10-15|本文のみ|無|無|無|Y|-||
|OPEN-388|2026-10-16|本文のみ|#83|無|無|Y|-||
|OPEN-394|2026-10-16|本文のみ|#85,#93,#94,#95|無|無|Y|-||
|OPEN-422|2026-10-21|本文のみ|#119,#120|無|無|-|Y||
|OPEN-423|2026-10-20|本文のみ|#123,#125|無|無|-|Y||
|OPEN-425|2026-10-20|本文のみ|#112,#123,#125,#128|無|無|-|Y||
|OPEN-428|2026-10-23|本文のみ|#157|無|無|Y|Y||
|OPEN-432|2026-10-21|本文のみ|#5,#132|無|無|Y|-||
|OPEN-463|2026-10-23|本文のみ|#163,#167,#170,#172,#175|有|無|Y|Y||
|OPEN-465|2026-10-23|本文のみ|#157,#161,#162,#163,#164|無|無|-|Y||
|OPEN-467|2026-10-23|本文のみ|#166,#169|無|無|-|Y||
|OPEN-474|2026-10-24|本文のみ|#169,#171,#173,#178,#179|無|無|Y|-||
|OPEN-497|2026-10-25|VALIDATED(限定)|#182,#185,#196|無|無|Y|-||
|OPEN-498|2026-10-24|本文のみ|#183,#186|有|無|-|-||
|OPEN-503|2026-10-28|本文のみ|#188,#192,#193|無|無|Y|-||
|OPEN-506|2026-10-26|本文のみ|#191|無|無|Y|Y||
|OPEN-510|2026-10-26|本文のみ|#191|無|無|Y|Y||
|OPEN-512|2026-10-25|保留|#197|無|無|Y|Y||
|OPEN-515|2026-10-28|保留|#201,#202,#203|無|有|Y|Y||
|OPEN-516|2026-10-26|本文のみ|無|無|無|-|Y||
|OPEN-520|2026-10-25|本文のみ|無|無|無|-|Y||
|OPEN-527|2026-10-26|ユーザー判断待ち|無|無|無|Y|Y||
|OPEN-528|2026-10-26|本文のみ|無|有|無|Y|Y||
|OPEN-531|2026-10-26|VALIDATED(限定)|無|無|無|Y|Y||
|OPEN-534|2026-10-27|VALIDATED(限定)|無|無|無|Y|Y||
|OPEN-537|2026-10-26|本文のみ|無|無|無|Y|-||
|OPEN-561|2026-10-27|本文のみ|無|無|無|Y|-||
|OPEN-565|2026-10-27|ユーザー判断待ち|無|無|無|Y|-||

## 5. PRE_USER_VALIDATION(一覧のみ、24件)
OPEN-83, OPEN-91, OPEN-106, OPEN-35, OPEN-63, OPEN-64, OPEN-117, OPEN-120, OPEN-121, OPEN-123, OPEN-125, OPEN-124, OPEN-129, OPEN-130, OPEN-132, OPEN-133, OPEN-135, OPEN-136, OPEN-137, OPEN-142, OPEN-144, OPEN-145, OPEN-146, OPEN-147

## 6. 所見(判断はFable)
- 目的達成度の記載があるPOST行はOPEN-515のみ(本委任で追記)。他の「VALIDATED(限定)・保留」系(OPEN-463/497/512/516/531/534等)は多くがPRODUCTION_WIRED/CLOSED/UDR登録済みで、課題Aと同型の「目的未達のまま完了語」候補は機械判定では見当たらない(個別の意味確認は未実施)。
- 同型リスクが最も高いのは§2の2026-10-12「OPEN候補・ユーザー判断待ち・未実装・未承認」群(OPEN-287〜294、297、353、331、565、561、229)。UDR未登録・再提示triggerなし。『Open Itemにあるだけ=UDRにしない(27-3)』でDeferred扱いが妥当か、既に別行で解消済みか、Fableが仕分け要。
- 判断候補(私見、A/B/C/D): 未登録行の登録要否は27-3で仕分けるべき事項。本書では**登録しない**。多数は C(独立)/B(開発側解決可)で非blockingの見込み=Deferred行化(trigger+期限付き)がC-18に整合。D該当の可能性は個別確認後。
