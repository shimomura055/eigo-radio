# ユーザー指示原文(2026-10-22)
管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 追加指示(Luna化・N増し)

# Claude Code追加指示：B3中核数値丸めTrial — Luna低コスト化・Ledger整合性N増し検証

対象：`FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01`

現行Status：`USER_DECISION_REQUIRED`

## 1. 目的

既存Trialで確認した数値丸め機能について、次の2点を追加検証する。

1. **判断LLMをGPT-6.1 SolからGPT-6 Lunaへ変更し、品質を維持したまま原価・処理時間を削減する。**
2. **複数記事・複数数値パターンでFact整合性を検証し、丸めによって量産が頻繁にNG停止しないことを確認する。**

成功条件は、単に丸め判断が正しいことではなく、**既存のFact Lock・品質基準を守りながら、量産で安定して運用できること**。

今回もTrial限定。Production採用・配線は行わない。

## 2. Lunaへの変更

- 数値丸め判断に使用しているSolをLunaへ変更する。
- B3本体の既存Solモデル、Fact選定、構成判断は変更しない。
- 既存TrialのPrompt・入力・判定基準を原則維持し、モデル変更の影響を比較する。
- 必要なら、品質を保つ範囲で出力項目・effort・トークン量を最適化する。
- Solで確認した9件の評価セットを再使用し、Lunaの結果と比較する。
- Lunaの判断結果にも、既存の決定論的安全検証V1〜V7を適用する。

**モデル名・価格・routingはRepoの正式な定義で確認し、実際のmodel_idとAPI費用を記録すること。**

Lunaで品質が不足する場合、原因を分析し、最小限の改善を試す。ただし品質基準を引き下げないこと。

## 3. Ledger整合性のN増し検証

今回の記事Aだけでなく、既存のFamily X記事・過去Trial成果物から複数のケースを選ぶ。

対象には少なくとも以下を含める。

- 大きな人数・金額など、概数化が自然な数字
- 小数・割合・相関係数など、精度保持が重要な数字
- 閾値・境界値・僅差の比較
- 日付・回数・数量
- 複数の数字が関連するFact
- 既に「約」が付いている数字
- 同じ数字でも文脈によって丸めの適否が変わるケース

既存の機械的中核数値選定をそのまま使用すること。

実際に中核数値として選ばれた数字を主対象とし、人工fixtureは不足する境界条件の補完に限定する。

**検証対象は、単なる数字の件数だけではなく、独立した記事数・Fact数・丸め対象数をそれぞれ報告すること。**

## 4. Fact Lock・Ledgerチェック

今回最も重視する検証。

丸め後の数値が、元のVerified Fact Ledgerとの整合性を保っているか確認する。

- 元Factの意味・数量規模・比較方向・閾値・結論が維持されるか。
- 丸めによってFactの範囲・確信度が変化していないか。
- Fact Lock Writerの規則(5)に対するTrial限定例外が、指定された中核数値にしか適用されないか。
- 丸め指定のない数字が変更されないか。
- B3 → Writer → R0/R1/R2 → Standard/Advancedで数値の意味が保たれるか。
- 現行ProductionのRisk Flaggerと、既存Ledger Deviation Checkerの双方で整合性を検証する。

**重要：旧Ledger Deviation Checkerは現行Production経路から撤去済みであるため、旧CheckerのPASSだけで量産運用可能と判断しないこと。**

現行Productionの実際のFact Lock・Risk Flagger・停止条件で評価する。

## 5. 量産停止リスクの評価

今回の重要なゴールは、丸め機能を導入した結果、量産工程が頻繁に止まることを防ぐこと。

次を明確に区別して評価する。

1. 丸めによって実際にFactの意味が変わったNG
2. 丸めは正しいが、Checkerが誤ってNGにしたケース
3. 丸め以外のWriter生成揺れによるNG
4. 本来NGにすべき数値変更をCheckerが見逃したケース

各ケースについて、原因・再現性・影響を記録する。

Trialでは、現行仕様のControlとLuna丸め追加版を可能な限り同一条件で比較する。

**NG率だけでなく、丸め機能追加によるNG増分・retry増分・Human Review増分を評価すること。**

単なるChecker PASS率だけではなく、Productionの最終判定・停止まで確認する。

## 6. NGが発生した場合

原因を次のように切り分ける。

- Lunaの丸め判断の誤り
- 丸め粒度の不適切さ
- Writerへの伝達・追従の問題
- Fact Lockの例外処理の問題
- Checkerの誤判定
- 後続R1/R2・英訳工程による変化

既存仕様・承認範囲内の不具合は自律的に原因究明・修正・再検証する。

新たな品質基準・Validatorの判定緩和・Fact Lock仕様変更が必要な場合は、Productionへ適用せず、**原因・対策候補・誤PASSリスク・QCD影響を整理してユーザーへ提案すること**。

CheckerがNGを出すからという理由だけで、判定を緩めて通すことは禁止する。

## 7. 変更禁止事項

- B3本体のFact選定・構成判断
- 機械的な中核数値選定・件数上限・優先順位
- Verified Fact Ledgerの正確な数値
- 承認済みFact Safety基準
- Production Writer Prompt・Validator・Risk Flagger
- Family X／Zの正式Production経路

既存Trialのoverlay方式を維持し、丸め判断機能以外に意図しない変更を生じさせないこと。

## 8. QCD・実施方針

- 既存Trialデータ・記事・音声化前成果物を最大限再利用する。
- APIによる記事全文の再生成は、評価上必要な最小限にとどめる。
- 無料の差分検証・安全検証・回帰テストを優先する。
- 独立した検証は並列化し、不要な待機・日付分割をしない。
- 開発費は既存の日次予算1,000円（JST）および承認済み作業範囲を遵守する。
- Solとのコスト・速度比較には、実測モデルID・token usage・API料金を使用する。
- Lunaで必要十分な品質が得られた時点で、追加のモデル探索を停止する。

## 9. 最終報告・受入条件

以下を簡潔に報告する。

1. **Sol対Luna：丸め判断品質・原価・処理時間の比較**
2. 検証した記事数・Fact数・中核数値数・丸め件数
3. 丸めるべき数値／丸めてはいけない数値の正解率
4. Fact Lock／Risk Flagger／Ledger Deviation Checkerの検査結果
5. 真のFact NG、Checker誤NG、見逃しの件数と具体例
6. Control比のProduction停止率・retry・Human Reviewの増減見込み
7. B3既存機能・Writerへの情報伝達の不変性
8. NG発生時の根本原因と、品質を下げない対策案
9. 1記事セットあたりの追加原価・処理時間
10. Fable独立評価、最終Status、Production採用に必要なユーザー判断

Fableは、検証サンプルの偏り、Fact Safety、量産停止リスク、費用試算を独立評価すること。

Trialの終了時は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類する。

**VALIDATEDでもProductionには採用・配線しない。**

CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSとの整合を確認し、Trial記録・結果をGitへ保存する。

## 最終ゴール

**B3の既存仕様を変えず、機械的に選定された中核数値だけをLunaで適切に丸め、その結果がFact Lock・Ledgerチェックで安定して通過する、低コストな最小仕様を確立する。**

品質（Q）＞速度（D）＞量産単価（C）≫開発費用を厳守すること。

---
(記録: 本文3,588字、sha256[本文のみ]=4bb9d28325b5fab1ed7323fb7f5aced03dfd5c511f003a0680666cbdca0e7330)
