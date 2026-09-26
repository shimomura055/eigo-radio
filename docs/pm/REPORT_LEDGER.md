# REPORT_LEDGER — 管理IDごとの「ユーザー初回正式報告」「Feedback」状態台帳

**このファイルはSSOTではない。** `CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`/`ER-*_REPORT.md`が引き続き正式SSOTである。本ファイルは、
Fableが★★★★報告★★★★を作る前に「初回報告 vs 再掲」「Feedback済みか」を
機械的に確認するための最小台帳であり、`docs/pm/PM_GOVERNANCE.md` 12節
(報告単位管理ルール)の運用補助として位置づける。

## 前提ルール(逐語、ユーザー明確化 2026-09-26)

1. 「初回報告」と「再掲」を絶対に混同しない。未報告なら初回報告として
   必要な結果を省略せず提示する(要約のみ・「詳細はREPORT参照」は不可)。
2. 再掲時は勝手に要約しない。前回 `★★★★報告★★★★` 内の内容を基本
   そのままコピーする。
3. REPORTファイルの存在・commit・Fable内部での完了は「ユーザーへ報告
   済み」を意味しない。ユーザー向け `★★★★報告★★★★` ブロックに実際に
   載せたかどうかで判断する。
4. 「初回報告済みか / ユーザーFeedback済みか / 累積再掲対象か」を区別
   できる最低限の仕組み(本ファイル)を維持する。過剰な新システムは
   不要。

関連: `docs/pm/PM_GOVERNANCE.md` 12節「報告単位管理ルール」(12-3未回答
再掲・12-4フルレポート再掲・12-4-1省略再掲禁止・12-11累積再掲)、
`docs/pm/templates/USER_REPORT_CHECKLIST.md`(報告前チェックリスト)。

## 運用

- Fableは各管理IDのTrial/作業が完了した時点で本表に行を追加する
  (Sonnet委任のcloseout時にもFable指示があれば行を追加してよい)。
- 実際に★★★★報告★★★★ブロックへ結果本体を載せた時点で「初回正式報告」
  列を日時ありで「済」にする。
- ユーザーから明示的なFeedback・判断を受けた時点で「ユーザーFeedback」
  列を日時ありで「済」にし、「累積再掲対象」列を`N`にする。
- 初回報告未・Feedback未の管理IDは「累積再掲対象」= `Y`のまま維持し、
  次回★★★★報告★★★★で省略せず再掲する(12-3/12-4/12-4-1/12-11)。

## 台帳

| 管理ID | Trial/作業完了日 | 初回正式報告(日時/有無) | ユーザーFeedback(日時/有無) | 累積再掲対象(Y/N) | 備考 |
|---|---|---|---|---|---|
| FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02 | 2026-09-26 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | 初期行作成時点の把握(2026-09-26)。 |
| TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02 | 2026-09-26 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | 同上。 |
| VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01 | 2026-09-26以前 | 済(2026-09-26) | 済(2026-09-26: 方針変更→`STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01`へ) | N | 本タスク(PM-REPORTING-LEDGER-INITIAL-VS-RESTATE-01)の契機事案。初回正式報告・Feedbackとも完了。 |
| NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-02 | 2026-09-26以前 | 済(2026-09-26) | 済(2026-09-26: B3[最小核基準]を`APPROVED_FOR_PRODUCTION`) | N | 同上。初回正式報告・Feedbackとも完了(Production採用はB3のみ、配線は別管理ID`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`)。 |
| FICTION-EXTERNAL-STORY-SEED-TRIAL-01 | 2026-09-26以前 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | `DECISION_LOG.md` PM-BUDGET-CAP-GUARDRAIL-POLICY-01の契機として言及済み。 |
| STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 | 2026-09-26以前 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | |
| TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01 | 2026-09-26以前 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | |
| NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01 | 2026-09-26以前 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | |
| ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01 | 2026-09-26 | 済(2026-09-26以前、会話ログ上) | 済(2026-09-26以前、会話ログ上) | N | `DECISION_LOG.md`に`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`確定として記録済み。 |
| STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26: `NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`方針で上書き) | N | `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01`のユーザーFeedbackによる方針変更後継。S-1/S-2/S-3はユーザー決定済み(上書き)。 |
| NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26: X-2決着、X-1はDiversity Trial/原因調査へ移管) | N(移管先で報告) | 配線PRODUCTION_WIRED(2026-09-26)、記事ユーザー確認待ち。 |
| FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26) | N | 差し戻し1回(True Crime再生成)後に初回報告。F-1/F-2 `VALIDATED`、F-3不採用(Family Z人名ルールへsupersede)、F-4条件付き採用。 |
| TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26 `PRODUCTION_WIRED`確定) | N | 差し戻し1回目(A2経路cool-down/Local Rewrite配線+topic_intro role漏れ修正)後、Fable Gate最終判定`PRODUCTION_WIRED`にユーザー異議なし確定。 |
| NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26: `NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`方針で上書き) | N | 語彙Band(6,000/10,000/14,000)を生成時点で制約するTrial。Meta記事は実質超過語0/0/0、Sewer記事は3条件とも実質超過語が残った(1〜6)。Band 10,000のSewerで引用句"combined septic tank,"が消失する事例あり。VB-1/VB-2/VB-3はユーザー決定済み(上書き)。 |
| FICTION-FAMILY-Z-PRODUCTION-E2E-01 | 進行中(2026-09-26、Phase 0完了+ユーザー確定ルールSSOT記録のみ) | 済(2026-09-26) | 済(Z-1〜Z-4すべて決着) | N(Phase 1実装は別途) | ユーザー確定ルール(Family定義/Story内容方針/Seed必須条件/外国人名ルール/story_type/TTS適用/PRODUCTION_WIRED条件)を`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`(OPEN-185)へ記録。Z-1(権利)〜Z-4(Voice参照先)まで2026-09-26に全て決着(`APPROVED_FOR_PRODUCTION`)、Production wiring自体(Phase 1実装)は別途未着手。 |
| EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01 | 2026-09-26 | 済(2026-09-26 最終レビュー報告) | 未(A-T) | Y | read-only Recon+Fable批判レビュー22項目完了→Tier 2/3安全性補完レビュー完了、Status=REVIEW_COMPLETED(Trial deferred)。`EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`Part 2追記、`OPEN_ITEMS.md` OPEN-186更新。推奨=段階導入Phase A/B/C、ユーザー判断A-T(Trial起票要否、Fable推奨(b) Phase A+B ¥10〜15)待ち。 |
| NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01 | 進行中(2026-09-26起票) | 済(2026-09-26) | 未 | Y | Family X B3 X-1(時制ドリフト)の原因調査。Fableレビュー(§13)完了、最小対策[a]観測性修正/[b]挙動修正(Trial必須)を提示、ユーザー判断待ち(`OPEN_ITEMS.md` OPEN-187新設)。 |
| FICTION-FAMILY-Z-RIGHTS-RECHECK-01 | 2026-09-26 | 済(2026-09-26) | 済(2026-09-26: 日本国内PD必須・米国PD非必須・走れメロス継続のユーザー決定) | N | Family Z Z-1(走れメロス著作権status)決着。権利Gateは日本国内PD/適法利用可能を必須、米国PDは必須条件にしない方針を`APPROVED_FOR_PRODUCTION`として採用(`OPEN_ITEMS.md` OPEN-185決着)。 |
| NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01 | 2026-09-26(Sonnet作業完了。small_bag完全成功、hormuzはAdvanced段でLedger Deviation MAJOR→既存Gate STOP[本文なし]、meta既存run_01のFact fidelity修正[MUSE-HC-012時制]込み) | 済(2026-09-26: SE-1 CLOSED[効果音なし・Comment接続設計採用]、small_bag/meta記事は試読待ち) | 未 | N | Trial、最大VALIDATED。効果音仕様は2026-09-26ユーザー正式決定によりSE-1 CLOSED(`PM-USER-DECISIONS-SSOT-CONSOLIDATION-04`、`CURRENT_SPEC.md`「Family X(Entertainment News)音声構造」節)、追加Trial不要。X-1(時制ドリフト)のFact fidelity修正対応を含む。Fable評価・分類を§8/§9へ記入済み。詳細は`er019_output/family_x_b3_diversity_trial_01/NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01_REPORT.md`。 |

## 違反事例記録

- 2026-09-26: `VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01`と
  `NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-02`の2件について、Trial結果
  本体をユーザーへ一度も★★★★報告★★★★していないにもかかわらず、累積
  報告の中で「前回までの未確認判断事項(再掲・要約)」として数行の要約
  のみを提示した。RepoにREPORTファイルが存在する・commit済み・Fable内部
  では完了している、という事実は「ユーザーへ報告済み」を意味しない
  (前提ルール3参照)。詳細は`docs/pm/PM_GOVERNANCE.md` 12-12節、
  `DECISION_LOG.md` `PM-REPORTING-LEDGER-INITIAL-VS-RESTATE-01`エントリ。
