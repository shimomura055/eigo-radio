# FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 ユーザー原文(逐語、2026-10-28)

```
# Claude Codeへの指示｜Family X Standard Comment 3 Z方式正式採用・AI島再制作

## 1. 決定事項

ユーザー判断により、今回Trialで検証した**Family Z方式のComment 3をFamily X Standardに正式採用**します。

- Trial：`FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01`
- Status：**APPROVED_FOR_PRODUCTION**
- 目標：**PRODUCTION_WIRED**
- 対象：Family X Standard
- Family X Advanced、Family Y/Z：今回の仕様変更対象外

今回の採用範囲は、Comment 3のPromptとAIに渡す本文の参照範囲の両方です。

## 2. 新しいComment仕様

### Comment 3：Z方式を正式採用

- 前半の重要点を1つ回収する。
- 後半につながる具体的な問いを提示する。
- 原則1〜2文とする。
- Part 1＋Part 2に加え、Part 3冒頭を限定的に参照する。
- 結論・重要な結果を先取りしない。
- Family Zの物語固有のルールをニュース記事に機械的に適用しない。

今回のTrialで検証した方式を基準とし、必要なニュース向けの参照範囲制御を実装すること。結果の先取りを防ぐため、Part 3の一定割合を無条件に渡す実装にはしない。

### Comment 1・2・4、Preview

**現行仕様を維持し、Prompt・参照範囲は変更しない。**

今回のTrialで、Comment 1・2・Previewは既にX/Zで同じ方式だったことが確認されています。Comment 4はZに相当するものがありません。

今回の変更に伴う不要なPrompt改善や追加Trialは行わないこと。

## 3. Production Wiring

Family X Standardの正式初回生成経路に新仕様を組み込み、以下を確認してください。

1. Comment 3の新Prompt・参照範囲が正式Productionで使用される。
2. retry／fallback／regeneration／resumeでも仕様が一貫する。
3. DEV／Trial専用経路ではなく、正式経路で発火した証拠を取得する。
4. Comment 1・2・4、Previewの既存仕様にRegressionがない。
5. Part 3の結論・重要結果を先取りしないことを検証する。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／必要なGit反映を完了する。
7. Fableによる独立受入評価を行う。

全条件を満たした場合のみ、**PRODUCTION_WIRED**と報告してください。

技術的不具合は承認範囲内で原因究明・修正・再検証まで自律的に進めてください。

## 4. AI島の完成版への反映

### Advanced

**ユーザー承認済み。**

- 現行完成版を維持する。
- 本件を理由とする再生成・変更は不要。
- 承認Statusを正しく記録する。

### Standard

**新しいComment 3方式で作り直す。**

- 記事本文、Key Phrase、文法選定等の承認済み内容は維持する。
- Comment 3を正式採用したZ方式で再生成する。
- 変更が必要な音声のみ再生成する。
- 既存の使用可能な音声・成果物は最大限再利用する。
- TTS／ASR／正式組立／公開検査は、既存の承認済み品質基準に従う。
- Standard完成版の試聴ページを更新し、ユーザーに再提出する。

**Standardの完成版はユーザー最終試聴待ちとし、独断で承認済みにしないこと。**

## 5. QCD・実行方針

優先順位は **品質 ＞ 完成速度 ＞ 量産単価**。

- 品質基準は変更しない。
- 不要な全工程再実行を避ける。
- 独立した作業は並列化し、不要な待機・日付分割をしない。
- 新規モデル呼出、TTS、ASRは必要最小限にする。
- 開発費は既存の承認枠・日次原則1,000円（JST）を遵守する。
- 必要十分な品質に達したら追加の磨き込みをせず完成させる。

新しい品質基準・未承認仕様の追加やProduction採用範囲の拡大は行わないこと。

## 6. 最終報告

以下を簡潔に報告してください。

1. Family X Standard Comment 3のProduction Wiring Statusと実動作証拠
2. Comment 1・2・4、Previewが従来仕様のままであること
3. AI島Advancedの承認記録
4. AI島Standard完成版の試聴URLと、変更箇所・再利用箇所
5. 必須品質検査・Regression・Fable受入結果
6. 実費、量産単価への影響
7. SSOT／Git反映状況、未解決Open Item

**到達目標は、Family X Standardの新仕様をPRODUCTION_WIREDにし、AI島Standardの再制作・公開検査を完了してユーザー最終試聴へ提出することです。**

既存仕様・過去Trialとの整合を確認しながら、承認範囲内の問題は自律的に解決してください。
```
