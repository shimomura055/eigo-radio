# OPUS_FINDINGS_LEDGER(Opus指摘トレーサビリティ台帳)

新設: 2026-10-05(`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`委任_04)。運用規則の正本は`docs/pm/PM_GOVERNANCE.md` 11-5節(ここへは複製しない)。正式SSOTの複製ではなく、Opus重要警告の追跡専用台帳。

- 状態遷移: `RAISED → FABLE_DECIDED(ADOPTED/REJECTED/MANAGED_SEPARATELY) → IMPLEMENTED/TRIALED → EVIDENCED → CLOSEOUT_CONFIRMED`。
- 区分: Safety hole / BLOCKER / MAJOR / 採用項目。「未確認」は、backfill時点で採否・Evidenceを台帳作成者が一次資料で確認していないことを示す(確認済みと誤読しない)。
- backfill範囲: Opus#9〜#15のSafety hole相当(各レビュー文書の該当節から抽出)。#8以前は未backfill(対象外、必要ならFableが別委任)。

| ID | 日付 | Opus# | 区分 | 指摘要旨(≤40字) | Fable採否 | 反映(委任#) | Evidence | Closeout確認 | Status |
|---|---|---|---|---|---|---|---|---|---|
| OF-001 | 2026-10-04 | #10 | Safety hole | Stage 1 recallが支配的リスク(S1の外) | 採用(MANAGED_SEPARATELYとして別管理) | 同管理ID委任_01/02(RCA)、委任_03(再設計案) | `docs/pm/opus_l2_review_open233_self_recovery_10.md`論点8、`docs/pm/pm_rca_open233_stage1_closeout_01.md` | 未(rep30 Closeoutで脱落、RCA問3・問8) | OPEN(本管理IDで対応中) |
| OF-002 | 2026-10-04 | #10 | Safety hole | 条件付きSafety値と代替なしE2E値の分離 | 採用(修正3点の1つ) | 本管理ID委任_04(24-1〜24-4)。runner出力側は未 | 同上§結論の修正3。PM_GOVERNANCE 24節 | 未(E2E値は未測定) | OPEN(本管理IDで対応中) |
| OF-003 | 2026-10-04 | #9 | Safety hole | 穴A: アンカー外の語を捨てる縮小 | 未確認(設計書§要照合) | 未確認 | `docs/pm/opus_l2_review_open233_self_recovery_09.md`論点1 | 未 | UNVERIFIED_BACKFILL |
| OF-004 | 2026-10-04 | #9 | Safety hole | 穴B: 先頭/末尾アンカーの間隔整合が未検査 | 未確認(設計書§要照合) | 未確認 | 同上論点1 | 未 | UNVERIFIED_BACKFILL |
| OF-005 | 2026-10-04 | #11 | Safety hole | D*は穴を閉じない(別データ未検証等) | 未確認(設計書§要照合) | 未確認 | `docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`論点2 | 未 | UNVERIFIED_BACKFILL |
| OF-006 | 2026-10-04 | #11 | MAJOR | Human Reviewへの逃げ経路が未測定(最大リスク) | 未確認(設計書§要照合) | 未確認 | 同上論点6 | 未 | UNVERIFIED_BACKFILL |
| OF-007 | 2026-10-04 | #12 | Safety hole | 再確認の解消判定情報の喪失(穴の正体) | 未確認(設計書§要照合) | 未確認 | `docs/pm/opus_l2_review_open233_kpi_recovery_02_12.md`論点2 | 未 | UNVERIFIED_BACKFILL |
| OF-008 | 2026-10-04 | #13 | Safety hole | 同義語表の同値クラスが粗く近接主体を誤許容 | 未確認(設計書§要照合) | 未確認 | `docs/pm/opus_l2_review_open233_kpi_recovery_02_13.md`リスクまとめ1 | 未 | UNVERIFIED_BACKFILL |
| OF-009 | 2026-10-04 | #13 | Safety hole | 件数一致の実装穴3点(範囲外index等) | 未確認(設計書§要照合) | 未確認 | 同上論点4 | 未 | UNVERIFIED_BACKFILL |
| OF-010 | 2026-10-05 | #14 | Safety hole | H-1(重大): BLOCKING確定箇所がRecheck1回でPASS | 未確認(設計書§要照合) | 未確認 | `docs/pm/opus_l2_review_open233_kpi_recovery_02_14.md` Safety hole節 | 未 | UNVERIFIED_BACKFILL |
| OF-011 | 2026-10-05 | #14 | Safety hole | H-2: Stage 2単独降格・判定揺れ降格の禁止 | 未確認 | 未確認 | 同上 | 未 | UNVERIFIED_BACKFILL |
| OF-012 | 2026-10-05 | #14 | MAJOR | H-3: 残るHuman Reviewは構造要素だけは誤り | 未確認 | 未確認 | 同上 | 未 | UNVERIFIED_BACKFILL |
| OF-013 | 2026-10-05 | #14 | MAJOR | H-4(低): B′同一性は重なりで判定 | 未確認 | 未確認 | 同上 | 未 | UNVERIFIED_BACKFILL |
| OF-014 | 2026-10-05 | #15 | Safety hole | F1: B3/B2_hormuzのStage 1検出が未証明 | 採用(配線前実測必須。CORRECTION-01/02でSTOP) | CORRECTION-01(委任_07)/02(委任_08) | `docs/pm/opus_l2_review_open233_production_wiring_15.md`、CORRECTION-02のfresh確認FAIL(DECISION_LOG) | 未 | OPEN(Stage 1非決定性で未解決) |
| OF-015 | 2026-10-05 | #15 | Safety hole | F2: 昇格ルールの誤配線(rep30と不一致) | 未確認 | 未確認 | 同上 | 未 | UNVERIFIED_BACKFILL |
| OF-016 | 2026-10-05 | #15 | MAJOR | F3: Stage 1非検出だと決定論floorも走らない | 未確認 | 未確認 | 同上§4 | 未 | UNVERIFIED_BACKFILL |
| OF-017 | 2026-10-05 | #15 | 採用項目 | F4: 凍結V4A出力の生成条件が未確認(推測) | 未確認 | 未確認 | 同上(未確認事項節) | 未 | UNVERIFIED_BACKFILL |
| OF-018 | 2026-10-05 | #15 | Safety hole | 未検証経路: T使用済み時のsub_reason欠落 | 未確認 | 未確認 | 同上Safety hole節3 | 未 | UNVERIFIED_BACKFILL |

注記: OF-014〜OF-018のうちF1〜F4は、本委任の指示(Opus#15 F1〜F4をbackfill)に基づく。F3/F4の区分(MAJOR/採用項目)は台帳作成者による暫定分類で、Opus原文は番号付き所見のみ(重大度の明示なし)。OF-018はSafety hole節の項目3で、F番号とは別。
