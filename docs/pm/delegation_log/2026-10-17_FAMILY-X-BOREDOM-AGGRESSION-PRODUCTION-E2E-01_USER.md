# Claude Code／Fableへの指示
## Family X「退屈と攻撃性」新規Production E2E

**管理ID：FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01**

### 1. 目的

以前から次回候補として繰り越していた「退屈と攻撃性」を、新規Family X記事として制作する。

今回の主目的は、**最新のFamily X正式Production経路が、ResearchからStandard／Advanced音声完成まで問題なく動作するかを検証すること**。

新規記事の品質も評価するが、Prompt探索や新仕様開発は行わない。

### 2. 開始条件：S3 Production Wiring完了

先行タスク：

`FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01`

**このタスクが`PRODUCTION_WIRED`に到達したことを確認してから、本記事の有料実行を開始する。**

確認事項：

- S3がFamily X Standard日本語Preview／Comment1〜4の正式Styleとして配線済み
- 正式初回・retry・fallback・regeneration等の整合確認済み
- Production runtime evidence取得済み
- 必要テストPASS
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新済み
- 必要なGit反映完了
- Fable独立受入完了

Claude Codeの「実装済み」報告のみでは開始条件達成としない。

**S3配線完了前は、新規記事の有料生成を開始しない。**

### 3. 記事テーマ

**退屈と攻撃性（Boredom and Aggression）**

主題は、退屈を感じることと攻撃的な行動の関係。

ただし、現段階で特定の研究結果や因果関係を事実として固定しない。

Researchで信頼できる研究・報道・一次資料を確認し、そこから記事の切り口を構築すること。

特に、相関関係を因果関係として断定しないこと。研究の対象者・実験条件・限界を適切に扱うこと。

既存のFamily X方針どおり、事実性とエンターテイメント性を両立させる。

### 4. 実行範囲

正式Production runnerを使用し、以下を新規実行する。

1. Research
2. Verified Fact Ledger
3. B3（Storyline）
4. Writer W-1：R0→R1→R2
5. Advanced英語化・Standard調整
6. Key Phrase生成・選定・解説
7. Standard／Advanced TTS
8. AUWによる音声品質判定
9. Assembly
10. 試聴ページ作成
11. 最終品質・費用・Production E2E結果の報告

本文・音声とも、新規記事として正式Production経路から生成する。

過去の記事やTrial成果を完成品として流用しない。

既存の辞書・共通資産・正式キャッシュ等の通常Production機能は使用してよい。

### 5. 使用する仕様

**開始時点で正式採用され、Production Wiringが完了している最新仕様を使用すること。**

最低限、以下を確認する。

| 対象 | 正式仕様 |
|---|---|
| B3／Writer R0〜R2 | Sol、W-1 |
| Standard日本語Preview／Comment1〜4 | **S3** |
| Full Story | PD06 |
| KP英語フレーズ | K2 |
| Standard KP日本語意味 | P8 |
| Advanced KP英語解説 | P7 |
| Advanced Preview | E1 |
| KP候補・選定 | M2P0＋A方式 |
| In One Line | 原則2文、必要時のみ3文 |
| Standard Full Story | 既存6%減速 |
| 音声QA | 正式Production配線済みAUW |

既存のFact Lock・Risk Flagger・Review Queue・Mandatory Human Review・音声品質Gateを維持する。

仕様名が存在するだけで適用済みと判断せず、正式profile・Production path・runtimeから確認すること。

### 6. コスト：実測・報告のみ

Research／Verified Fact Ledgerのコスト改善は、別管理IDで並行検証中。

**今回のProduction記事には、未承認の検索上限方式やSelect-then-Verify方式を適用しない。**

現行Production仕様のまま実行し、費用を詳細に記録する。

最低限、以下の工程別Breakdownを報告する。

| 工程 | 記録項目 |
|---|---|
| Research | 実測円・Web検索回数・LLM費 |
| Verified Fact Ledger | 実測円・Web検索回数・LLM費 |
| B3 | 実測円 |
| Writer R0／R1／R2 | 各実測円 |
| Advanced英語化 | 実測円 |
| Standard調整 | 実測円 |
| Key Phrase関連 | 生成・選定・解説の各実測円 |
| TTS | Standard／Advanced別の実測円 |
| ASR | 実測円、推定の場合は区別 |
| retry／fallback等 | 追加費用 |
| **合計** | **実測総額** |

**円単位の表で報告する。パイチャートは不要。**

併せて、現行の量産原価目標（Standard＋Advancedで70円）との差額を報告する。

ただし、今回は原価削減策の追加提案・追加Trial・実装は行わない。

費用の実測・推定・未取得を区別すること。

### 7. 費用Gate

既存の開発費ルールを遵守する。

- 実行前に全体見積と工程別見積を確認
- 当日使用済み費用・残予算を確認
- 既存の自律実行権限を超える費用については、事前承認がなければSTOP
- 日次1,000円のsoft budgetを維持
- 必須品質Gateを費用削減目的で省略しない

**今回、記事制作の新たな個別上限金額は承認されていない。**

Coffeeの205円承認枠を流用しないこと。

### 8. E2E動作確認

各工程について以下を記録する。

- 正式Production entrypoint
- 実際のmodel_id／routing
- 適用されたPrompt・StyleとSHA
- 入出力artifact
- 使用したretry／fallback／regeneration
- 各Validator・品質Gateの結果
- Mandatory STOP／Human Reviewの発生状況
- コスト
- 後続工程への引き渡し結果

正式runnerのMandatory STOPに到達した場合は、既存の運用ルールに従って停止する。

**本指示は、将来発生する必須ユーザー確認Gateを一括解除するものではない。**

### 9. 成果物・試聴ページ

Standard／Advanced両方について、完成音声と試聴ページを用意すること。

ページには最低限以下を含める。

- 記事タイトル
- 通し再生
- 本文・Preview・Comment・In One Lineの原稿
- Key Phrase（英語＋各レベルの正式解説）
- 必要な品質警告・試聴確認事項

既存の正式Coffee E2Eの試聴ページ構成を参考に、過剰なデザイン開発は行わない。

### 10. 対象外

- Research／Ledgerコスト改善案のProduction適用
- 新しいWriter・TTS Style探索
- S3の再調整
- Family Z／Yへの変更
- Family A／B／Cの調査・開発
- Detective演出の仕様変更
- 無関係なOpen Itemの棚卸し

並行作業とのGit競合を避け、**commitを伴う作業は同時に1件のみ**とする。

### 11. STOP条件

以下の場合はSTOPし、事実・影響・必要な判断を報告する。

- S3の`PRODUCTION_WIRED`未達
- 既存のMandatory Human Review／ユーザー確認Gateへの到達
- 正式Production経路の不具合
- 重大なFact・記事品質問題
- 承認済み仕様との重大な不一致
- 費用Gate超過見込み
- 新しい仕様採用・追加Trialが必要

問題が起きても、独断で別の改善Trialや仕様変更を開始しない。

### 12. 最終報告・Closeout

冒頭に次の3点を簡潔に示す。

1. **Researchから音声完成まで正式Production E2Eが正常に動作したか**
2. **Standard／Advanced試聴ページURL**
3. **工程別費用Breakdownと総額**

続けて、正式仕様の照合結果、runtime evidence、品質判定、retry／fallback、未解決のBlocking事項を報告する。

FableはClaude Codeの報告をそのまま採用せず、CURRENT_SPEC・承認済み仕様・Production runtime evidence・実際の成果物・テスト結果と照合して独立評価する。

Trial上の新しい改善仕様は採用しない。

**今回の目的は、新規記事を通じて現在のProductionの完成度と安定性を確認することである。**
