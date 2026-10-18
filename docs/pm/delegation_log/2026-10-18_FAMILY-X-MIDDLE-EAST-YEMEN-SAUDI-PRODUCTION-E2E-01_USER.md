# Claude Code／Fableへの指示
## Family X 新記事「中東情勢が悪化、イエメン・サウジ周辺で攻撃続く」

### 1. 目的

Family Xの正式Production E2Eを使用して、新しいNews記事をStandard／Advancedの両レベルで制作し、音声・試聴ページまで完成させる。

**記事テーマ：**
「中東情勢が悪化、イエメン・サウジ周辺で攻撃続く」

タイトルは仮題。Researchで確認した事実に基づいて、内容・見出しを最終決定すること。

### 2. 制作方針

前回の「退屈と攻撃性」と同じ承認済みProduction仕様を使用する。

- Research → Verified Fact Ledger → B3 → Writer R0/R1/R2
- Advanced英語化 → Standard調整
- KP選定 → TTS → AUW → Assembly → 試聴ページ
- Family Xの正式Production初回経路を使用
- 既存のretry／fallback／Human Review／品質Gateを維持
- 承認済み音声Style（PD06／E1／K2／P7／S3／P8-KP）およびStandard 6%減速を適用
- Risk Flagger、Fact Lock、重大誤解防止の既存仕様を遵守
- In One Line等のFamily X構成仕様を維持

未承認の新仕様、Prompt探索、追加Trialを行わない。

### 3. 今回のResearchで特に注意すること

中東情勢は変化が速く、報道間で数字や主張が異なる可能性がある。

以下を徹底すること。

1. 攻撃の**日時・場所・実行主体・標的・被害状況**を確認する。
2. フーシ派、イエメン政府、サウジアラビア、イラン等の立場・関与を混同しない。
3. 当事者の発表と、独立して確認された事実を明確に区別する。
4. 死傷者数、攻撃回数、被害施設などは報道時点を明示し、数字を安易に混ぜない。
5. 過去の攻撃と今回の新しい攻撃を混同しない。
6. 攻撃の目的・責任・報復関係について、確認できない推測を事実として書かない。
7. 特に重要なFactは複数の信頼できる情報源で照合する。

Reuters／AP／公的発表などを適切に参照し、公開日だけでなく事件発生日も確認すること。

**記事の狙い：**

事件を単に列挙するのではなく、「なぜイエメン周辺の紛争がサウジアラビアや地域全体に影響するのか」を、英語学習者にも分かりやすく、興味深いストーリーとして伝える。

ただし、面白さのために事実を誇張したり、政治的に一方的な解釈へ誘導したりしないこと。

### 4. 既存Production仕様の維持

以下を徹底する。

- Family Xの最新正式仕様をSSOTで確認
- CLI指定なしの既定Style Profileが正しく適用されることを確認
- B3／Writer／KP／TTS／AUWの既存Production経路をそのまま使用
- Storytelling品質と重大誤解防止の両立
- Risk Flaggerによる指摘を既存契約に従って処理
- 各音声RoleのStyle、Voice、actual model_id、routingを検証
- ASR・Validator・Integration・Assemblyの必要な検査をPASS

RLCTでTrial中のResearch／Ledgerコスト削減案は、Production採用前なので今回の正式経路へ混入させない。

Cross-Family同時配線原則も遵守する。ただし、今回が既存承認仕様による新記事制作である以上、Family Zで並行作業中の配線を無用に重複・競合させないこと。

### 5. 費用・効率

前回と同水準の**記事制作費上限JPY180**を想定する。

- 前回実績：JPY89.90
- 今回も同程度を目標とするが、情勢調査の難度により変動し得る
- 上限超過見込みの場合はSTOP
- 工程別の実費を記録
- 検索・再生成・retryの無駄を避ける
- 独立工程は安全な範囲で並列化する

JPY180は今回の制作管理上限とし、承認済みの他案件予算とは混同しない。別途の費用承認が必須となる契約・運用上の制約が見つかった場合は、有料実行前にSTOPして報告すること。

### 6. STOP条件

以下の場合は、独断で仕様変更・追加Trialを進めず報告する。

- 重要な事実関係を十分に検証できない
- 重大誤解・Fact Lock・Human Review等の必須Gateが発火
- 既存Production経路では解決できない品質問題が発生
- 費用上限超過が見込まれる
- 未承認仕様への変更が必要
- Production実行・音声検証に重大な問題がある

### 7. 最終報告

制作完了時には、以下を簡潔に提示すること。

1. 正式Production E2Eの完走結果
2. Standard／Advancedの試聴URL
3. 記事の要約と主要Fact
4. Fact Ledger／Risk Flaggerの結果
5. KP選定結果
6. TTS・AUW・ASR・Assemblyの品質結果
7. Style／model_id等のruntime evidence
8. 工程別実測費用と総額
9. commit／push、SSOT更新状況
10. 未解決Open Itemおよびユーザー判断事項

**音声・試聴ページまで完成させたらSTOPし、ユーザーの試聴判断を待つこと。**

Fableの技術的PASSとユーザー試聴PASSは区別する。

既存Productionに問題がなければ、途中の不要な報告や追加承認待ちを挟まず、前回同様、完成音声まで進めること。
