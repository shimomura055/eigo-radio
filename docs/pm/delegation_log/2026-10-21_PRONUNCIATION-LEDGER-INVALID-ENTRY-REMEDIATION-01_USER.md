# ユーザー指示原文(2026-10-21)
管理ID: PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01

## Claude Code指示：Pronunciation Ledger不正データ是正

**目的：** Pronunciation Ledgerの不正データを是正し、Azure Phrase Listへの誤った語句供給を防止する。

### 1. 対象

- `us → unknown`：不正なLedger登録を無効化する。
- `melos`：hint混入の内容・原因・正しい登録状態を確認し、必要な是正を行う。
- 同種の不正登録がないか、既存Ledgerを点検する。

### 2. 実施方針

1. CURRENT_SPEC・過去のTrial・承認済み仕様を確認する。
2. 不正登録の発生原因を特定する。
3. 不正データを是正し、既存の正しい登録は維持する。
4. 同じ問題が再発しないよう、既存の登録・検証機構を必要最小限で改善する。
5. Family X／Zの双方で、Azure Phrase Listへの供給が正しくなることを検証する。

**重要：**
- Azure Phrase Listの重み2.0は正式採用済み。変更禁止。
- 既存の品質基準・ASR判定ロジック・承認済み仕様を無断変更しない。
- 新しいTrialや大規模な仕組みの追加は不要。
- 不正なhintの除去によって認識結果が変わる可能性はあるため、PASS/NGの不変を前提とせず、golden再判定で影響を確認する。

### 3. 受入条件

- `unknown`など不正な語句がPhrase Listへ供給されない。
- `Melos`など正当な固有名詞の検出・供給が維持される。
- Family X／ZのRegression・ValidatorがPASS。
- 既存のPASS/NG判定に変化があれば、原因と品質影響を報告する。
- Production初回経路およびretry／fallback／resumeとの整合を確認する。
- CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSを必要に応じて更新し、Git反映する。

### 4. 自律解決・STOP条件

既存仕様の範囲内のデータ修正・原因究明・再発防止・検証は自律的に完了させる。

新しい品質基準・仕様変更が必要な場合、または品質への重大な影響が判明した場合はSTOPし、USER_DECISION_REQUIREDとして報告する。

品質を守りながら最短で完了させ、不要な追加Trial・逐次作業を避ける。

### 5. 完了報告

以下を簡潔に報告する。

- 修正した不正データと原因
- 同種問題の点検結果
- 再発防止策
- Family X／ZのProduction動作とRegression結果
- PASS/NGへの影響
- Git commit・SSOT反映状況
- 残存Open Itemと最終Status

**到達目標：PRODUCTION_WIRED（必要な証拠がすべて確認できた場合のみ）。**
