# ユーザー指示原文(2026-10-22)
管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 正式採用判断・記事A再制作指示

# Claude Codeへの指示：Family X 数値丸め正式採用・記事A再制作

## 1. 正式採用判断

**Family Xの中核数値丸め仕様を正式採用する。**

Status：`APPROVED_FOR_PRODUCTION`

対象は**Family Xのみ**。Family Zへの展開は今回の承認範囲外。

承認仕様は以下のとおり。

- 判断モデル：GPT-6 Luna、reasoning effort = low。
- B3の既存方式で中核数値を選定した後、丸めの可否を判断する。
- Fact Lock規則(5)には、B3で正式指定した概数に限って例外を認める。
- 小数％は既存の概数化原則に従う。
- 既に概数の数値は再丸めしない。
- **V8を採用**：元の数値との相対誤差10％以内。既存90件のオフライン検証結果を再利用し、正式実装の回帰テストにも組み込む。
- **S5を条件付き採用**：`【概数表記】` のタグ漏れを検出する。まずTrial環境で修正後の検出・回帰テストを実施し、PASSを確認してからProductionへ実装する。PASSの場合、途中報告・追加ユーザー承認は不要。

丸めによって数値の意味、限定条件、比較方向、重要な閾値、Ledgerとの事実整合性を損なわないこと。

既存B3のFact選定・機械的な中核数値選定は変更しない。

## 2. 記事AをB3から全面再制作

対象記事：

**「給料が上がると、性格も変わる？」**

既存のResearch成果物・Verified Fact Ledgerを再利用し、**Research工程は再実行しない。**

新しい正式仕様をProductionへ実装・検証したうえで、記事Aについて以下をすべて再実行する。

1. B3：既存の正式B3処理から再実行し、新しい数値丸め判断を適用。
2. 日本語Writer：R0 → R1 → R2を再生成。
3. Standard／Advanced：両レベルの英語記事・解説・Key Phrases等、必要な全コンテンツを再生成。
4. TTS：新しい全文・関連コンテンツを正式Production経路で音声化。
5. ASR・Fact Safety・各種Validator・品質検査を実施。
6. 最終記事を組み立て、**ユーザー試聴ページを更新**する。

これは既存音声の数字部分だけの差し替えではなく、**Research以外の全工程の作り直し**である。

既存の完成候補・音声・試聴ページは比較・ロールバック可能な状態で保持すること。

再生成時には、数値丸め以外の承認済みFamily X仕様もすべて適用する。既存のASR・TTS・Key Phrase品質対策を後退させないこと。

## 3. 実装・検証・受入条件

正式初回Production経路に実装し、retry／fallback／regeneration／resumeでも同じ承認仕様が適用されることを確認する。

特に以下を検証する。

- V8が不適切な丸めを拒否し、正しい丸めを不必要に拒否しない。
- S5がタグ漏れを検出し、正常な文章には誤発火しない。
- Ledgerの元の正確な数値は変更されない。
- 数値丸めによって不要なSTOP・retry・Human Reviewが増えない。
- B3既存機能・他Familyの動作を変更しない。
- 実際に使用したmodel_id・reasoning effort・Prompt・routingの証拠を残す。
- 必須Regression・Validator・integration testをPASSする。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新し、Gitへ反映する。

既存仕様・承認予算内の技術的不具合は自律的に原因究明・修正・再検証する。独立作業は並列化し、不要な待機や日付分割を行わない。

**承認済み品質を満たしたら、追加Trialや磨き込みをせず完成させること。**

ただし、未承認の仕様変更、重大なFact Safety問題、解決不能なblocker、予算上限超過はSTOPして報告する。

## 4. 最終報告

Fableが独立評価したうえで、以下を報告すること。

1. Family X正式実装の結果と `PRODUCTION_WIRED` 判定根拠。
2. V8・S5の検証結果。
3. 記事Aで実際に使用された数値のBefore／After。**記事に使われなかった丸め候補は報告不要。**
4. Fact Lock・Ledger整合性・Risk Flagger・ASR・TTS・各種品質検査の結果。
5. Standard／Advancedの完成音声とユーザー試聴URL。
6. 記事セットの実費と量産時の追加原価。
7. 残存する品質問題と、ユーザー判断が必要な事項。

**完了の区別を厳守すること。**

- Family X数値丸め仕様：正式Productionでの配線・実走・証拠確認後に限り `PRODUCTION_WIRED`。
- 記事A：全工程・品質検査完了後も、ユーザー最終試聴PASSまでは「完成候補」。

最終的な記事品質の受入判断はユーザーが行う。

---
(記録: 本文2,224字、sha256[本文のみ]=08dc425861b4655befc678976284039d08320c5b5c8ba15b7296d4d256b0916b)
