# FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 ユーザー元指示(逐語)

出典: セッションtranscript(f2c17cf7-...jsonl) 6426行目 type=user メッセージ本文(全候補行: 6426, 6472[継続要約], 6564[agent-message], 6580[agent-message]; 最初の完全な指示文=6426を採用)
抽出日時: 2026-10-11
文字数: 3057
逐語(要約・改変なし)。以下、区切り線の間が本文。

-----


<pasted_content id="f6a1">
# Claude Code指示：Family X → Family Z 仕様横展開の事前整理

**管理ID：FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01**

## 1. 目的

Family Xで決定・整備した仕様のうち、Family Zにも適用できる共通仕様を洗い出す。

Family XとFamily Zの現行仕様、Production実装状況、承認済み変更を照合し、横展開候補と判断事項を整理する。

**今回は仕様調査・比較・提案のみ。実装・Trial・Production変更は禁止。**

## 2. 調査対象

まずRepoの以下を確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Family X／Family Zの設計資料
- 両FamilyのProductionコード・Prompt・Validator・音声生成経路
- 直近の承認済み仕様と進行中のProduction Wiring
- 過去のFamily Z関連Trial・改善提案

古い仕様や過去のTrialを、現在の正式仕様と混同しないこと。

## 3. 整理する内容

### A. Family Xの仕様一覧

Family Xの仕様を、可能な限り網羅的に整理する。

特に以下の領域を確認する。

1. Research・Fact抽出・Fact Ledger
2. Fact選択・Storyline・B3
3. 日本語記事生成・R0/R1/R2
4. 英語化・難易度調整
5. 記事構造・Comment・Preview・In One Line
6. Key Phrases・解説・レベル別仕様
7. 音声Voice・Style・TTS・速度
8. ASR・読み誤り・再生成・Secondary Confirm Gate
9. Validator・品質Gate・Review Queue
10. retry・fallback・regeneration・resume
11. 音声Assembly・Master Store・試聴ページ
12. コスト・runtime管理・運用ルール

上記は調査観点であり、新仕様を作る指示ではない。

### B. Family Zの現行仕様

同じ観点でFamily Zを調査し、以下を明確にする。

- Family Z固有の目的・記事構成・体験設計
- 現在の正式Production仕様
- 実装済み部分と未実装部分
- Family Xと既に共通化されている部分
- Family Xとは異なるが、意図的に設計された部分
- 過去の承認済み事項・未解決Open Item

Family Z固有の価値を損なう共通化は提案しないこと。

## 4. 横展開候補の分類

各仕様を次の5つに分類する。

| 分類 | 意味 |
|---|---|
| A：既に共通 | Family Zに同等仕様が正式実装済み |
| B：横展開推奨 | Family Zにも適用する価値が高い |
| C：条件付き | Family Z向けの調整・検証が必要 |
| D：対象外 | Family X固有でFamily Zに適用しない |
| E：判断保留 | 仕様や実装の確認が不足 |

各項目について、少なくとも以下を示す。

- Family Xの正式仕様とStatus
- Family Zの現行仕様とStatus
- 差分
- 横展開する場合の具体的な変更点
- 共通化による品質・コスト・開発効率への影響
- リスク
- 推奨分類と理由
- ユーザー判断の要否
- 根拠となるファイル・関数・決定記録

**VALIDATED、APPROVED_FOR_PRODUCTION、PRODUCTION_WIREDを厳密に区別すること。**

Trial成功だけの仕様は、正式採用済みの共通仕様として扱わない。

今回採用されたJ2／E2／F1.5についても、承認済み仕様とProduction配線の進捗を区別して記載すること。

## 5. 特に注意する点

- Family XのB3、Fact数、記事分割などをFamily Zに機械的に移植しない。
- 共通化できる品質原則と、Family固有のPrompt・記事構造を分ける。
- 共通コンポーネントの再利用と、同じ仕様をFamily Zへ個別実装することを区別する。
- 既存のFamily Z仕様を無断で上書きしない。
- Family X側の未完了Production Wiringを、Family Z展開の完了済み前提にしない。
- 新たな共通仕様名を作る場合、既存仕様との重複とDangling Referenceを確認する。
- 他Familyへの影響を明示する。

## 6. 成果物

### ① 両Familyの現状サマリ

非エンジニアのPMが理解できる形で、Family XとFamily Zの設計思想・記事構造・Production成熟度を比較する。

### ② 仕様対応表

Family Xの主要仕様ごとに、Family Zの対応仕様、差分、A〜E分類、根拠を示す。

### ③ 横展開推奨リスト

優先順位を付ける。

- P0：品質・安全性・重大な不整合の防止
- P1：ユーザー体験・記事品質の改善
- P2：効率化・保守性改善

各候補に概算の作業規模・費用影響・必要Trialを付記する。

### ④ ユーザー判断事項

採用可否を判断する必要がある項目を、重要度順にまとめる。

細かな技術判断はClaude側で整理し、ユーザーには**仕様・品質・費用・体験に影響する判断だけ**を提示する。

### ⑤ 既存Open Item・進行中作業との関係

特にAPPROVED_FOR_PRODUCTIONだが未配線の仕様、Family Z側の既存Open Item、重複開発・仕様競合を確認する。

## 7. 費用・作業制限

- 調査はRepoの既存情報を使用し、原則API費用¥0
- TTS・記事生成・Researchの新規実行は禁止
- 不要な大規模テストは禁止
- 今回はコード変更しない
- 仕様変更・採用・Trial・Production Wiringは行わない
- 文書成果物の作成・必要な記録更新は可

## 8. STOP条件・最終報告

未承認仕様のProduction展開、既存仕様との重大な矛盾、資料不足で重要な判断ができない場合は、推測で補わず未解決事項として報告する。

報告は原文の調査順ではなく、**PM判断への影響が大きい順**に整理する。

最後に以下を明示する。

1. すぐ横展開すべき仕様
2. Family Z向けの調整が必要な仕様
3. 横展開すべきでない仕様
4. ユーザー判断が必要な事項
5. 推奨する次の作業順序

**今回のStatus：調査・整理のみ。次工程は `USER_DECISION_REQUIRED` としてSTOP。**

ユーザーによる採用判断なしに、追加TrialやProduction実装へ進まないこと。
</pasted_content id="f6a1">

-----
