# Family X 新規ニュース2記事 — 正式Production E2E制作指示

## 1. 目的・対象

以下のニュース2件を、Family Xの現行正式Production経路で制作してください。

各記事ともStandard／Advancedの2レベルを作成し、音声化・品質検査・最終試聴ページ公開まで完了させること。

### 記事A：AIと一緒に書いた小説に、文学賞が誕生

- 内容：フランスで、AIと人間が共同執筆したフランス語のフィクションを対象とする「Prix Pascal」という新しい文学賞が設立された。
- 参考記事：[RTÉ / AFP（2026年10月21日）](https://www.rte.ie/news/newslens/2026/1021/1596348-ai-literary-prize-france/)
- 注意：文学賞が新設されたのであり、すでに受賞作が決まったわけではない。審査員や賞金が未確定である点も正確に扱う。

### 記事B：TeslaとSpaceXが合併？ イーロン・マスクの巨大構想

- 内容：イーロン・マスクがTeslaとSpaceXの合併に前向きな姿勢を表明。両社が特別委員会を設け、合併の可能性を検討している。
- 参考記事：[Reuters（2026年10月21日）](https://www.marketscreener.com/news/tesla-spacex-deal-wall-st-says-inevitable-but-musk-says-it-s-not-certain-ce785cd8d081f227)
- 最新補足：[Reuters（2026年10月22日）](https://www.marketscreener.com/news/musk-s-public-endorsement-of-spacex-tesla-deal-may-throw-a-wrench-in-talks-ce785cd9df8ef622)
- 注意：合併は未決定。検討段階であること、株主承認などのハードルを正しく伝える。

両記事とも制作開始時点の最新情報を確認し、既存のResearch・Fact検証仕様を遵守すること。

## 2. 実行方針

- 新規Trialではなく、**現行承認済みProduction仕様をそのまま使用**する。
- 現行の正式初回Production経路から実行する。DEV／Trial専用経路で代替しない。
- 記事構成、B3、Fact管理、英語レベル、Key Phrase選定、音声Role、Voice、速度、TTS、ASR等はすべて現行仕様を適用する。
- Key Phrase音声は直近承認したPrimary（OpenAI）／Secondary（Azure）の両方PASS必須ルールを含め、最新の承認済み仕様に従う。
- retry／fallback／regeneration／resumeも正式経路の仕様を適用する。
- 新仕様や未承認の改善案を独断で採用しない。

## 3. QCD・実行効率

優先順位は **品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用**。

- 2記事および各レベルの独立工程は可能な限り並列実行。
- 共通リソースの競合がある工程のみ適切に直列化する。
- 不要な再調査、再生成、追加Trial、日付分割、待機を行わない。
- 承認済みの品質水準を満たしたら追加の磨き込みをせず完成させる。
- 量産単価70円／記事セットを目標に、品質を犠牲にしない範囲でコストを最適化する。
- 既存承認範囲内の技術的不具合はFable／Claudeで自律解決する。

既存の日次予算・個別承認枠・STOP条件を遵守すること。予算や承認範囲を超える場合は停止して報告する。

## 4. 完了条件

各記事・各レベルについて、以下を満たすこと。

1. 正式Production経路で本文・Key Phrase・音声を生成。
2. 必須Validator・ASR・品質検査がPASS。
3. 必要なretry／fallback処理との整合を確認。
4. 実際のProduction runtime evidenceを保存。
5. 全編通し再生・パート別再生が可能な試聴ページを公開。
6. Preview／Comment／Full Story／In One Line等の全スクリプトとKey Phrase（英語・意味・解説）を掲載。
7. 必要なSSOT・Git反映を実施。

試聴ページは従来のユーザー試聴ページと同等のシンプルな形式でよい。不要な装飾・新機能の開発は不要。

## 5. 最終報告

記事ごとに以下を簡潔に報告すること。

- Standard／Advancedそれぞれの完成Status
- 最終試聴URL
- 品質検査結果と未解決事項
- Production runtime evidenceの有無
- 実際に使用したモデル・Voice・主要routing
- 実費と記事セット当たりの量産単価見込み
- Git commit／SSOT反映状況

Fableは実装報告を独立検証し、Production Wiring Gateの充足を評価すること。

**最終ユーザー試聴PASSはユーザー本人の判断とし、AI側で代行しない。**

新たなユーザー判断が不要であれば、途中報告による停止を挟まず、2記事とも完成候補まで進めてください。