# Claude Code／Fableへの正式指示
## Coffee E2E：Mandatory STOP解除・音声工程再開

**管理ID：FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01（継続）**

**現在Status：Text工程完了／音声工程のMandatory STOPに到達**

**今回の到達目標：Standard・Advanced音声完成、試聴ページ作成、Production Wiring最終照合**

### 1. ユーザー正式判断

**Coffee記事の音声化への進行を承認する。**

ResearchからStandard調整まで完了した既存runを引き継ぎ、Mandatory STOPを解除して次工程へ進めること。

対象run：
`er019_output/coffee_prices/run_fxpw_01`

既に生成したResearch・Fact Ledger・B3・Writer・英語記事を、理由なく再生成しない。

今回の承認は既存記事の音声化を認めるものであり、新しい仕様・改善Trialの採用を意味しない。

### 2. 実施内容

既存の`COFFEE_E2E_PLAN_01.md`と`SPEC_WIRING_MATRIX_01.md`に従い、正式Production経路で実施する。

1. Key Phraseの新規抽出・選定・解説生成
2. Standard／AdvancedのTTS生成
3. AUWによる音声品質判定
4. 正式Style適用の全Section照合
5. Assembly
6. Standard／Advanced試聴ページ作成
7. 必要なruntime evidence・費用・品質結果の記録

既存のMandatory Human Review、品質Gate、retry／fallbackルールは維持する。

### 3. 必須仕様

| 対象 | 正式仕様 |
|---|---|
| Full Story | PD06 |
| KP英語フレーズ | K2 |
| KP日本語意味（Standard） | P8 |
| KP英語解説（Advanced） | P7 |
| Preview（Advanced） | E1 |
| 日本語Preview／Comment（Standard） | R2 |
| KP抽出・選定 | M2P0＋A方式 |
| In One Line | 基本2文、必要時のみ3文 |
| Standard Full Story | PD06＋既存6％減速 |
| 音声QA | Production配線済みAUW |

Family Xの既定profile `fx_20261016` がCLIの特別指定なしで適用されることを、TTS開始前に確認する。

### 4. K2代替音声

既存`OPEN-399`で別管理する。

- 今回はfallback仕様を変更しない。
- CoffeeでK2代替音声が発生した場合、件数・対象フレーズ・原因を記録する。
- 代替Style音声をK2適用済みと誤表示しない。
- 完成報告で代替使用を明示する。
- 既存の必須品質Gateは緩和しない。

このOpen Itemの追加Trial・改修は今回行わない。

### 5. 費用管理

**Coffee E2E全体の承認上限：205円。**

Text工程実測：72.64円。

残予算：約132.36円。

音声工程の見積：期待約28円、最悪約67円。

今回の実走で、全工程の費用を記録すること。

また、完成後に以下を算出する。

- Coffee記事セット（Standard＋Advanced）の実測総費用
- 各工程の費用内訳
- 正式リリース後のBatch TTSを想定した量産原価
- 量産原価目標70円との差額
- 超過する場合の主な原因と改善余地

**今回はコスト削減の追加Trial・モデル変更・仕様変更を行わない。**

205円を超える見込みがある場合はSTOPする。

### 6. Production Wiring最終確認

Family Xは現時点で「配線・テスト完了、正式実走による最終証拠待ち」。

以下を確認する。

- 正式Production初回経路で承認済み仕様が適用されたか
- retry／fallback／regenerationとの整合
- B3／R0／R1／R2の実測model_id（既取得証拠を使用）
- 各音声SectionのStyle ID・version・Prompt SHA
- AUW判定とWARNING
- In One Lineの文数
- 必要Regression・Validator・integration test
- 仕様反映マトリクス全項目
- CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS
- 必要なcommit／push／merge

**すべてを満たすまでは`PRODUCTION_WIRED`と報告しない。**

### 7. 対象外

以下は行わない。

- 新しいPrompt・Styleの探索
- ResearchやWriterの不要な再実行
- K2代替音声方式の改修
- 新しい原価改善Trial
- Family A／B／Cの調査・開発
- Family Zの予防的改修
- Family Yの先行開発
- 無関係なOpen Itemの棚卸し
- Day 5・6の再開

DQIの10件前向き観察は既存運用のまま継続し、今回のCoffee作業の妨げにしない。

### 8. STOP条件

次の場合はSTOPして報告する。

- 既存のMandatory Human Review／品質Gateに到達
- 承認済み仕様との重大な不一致
- 音声・原稿・Styleの取り違え
- Coffee承認予算205円の超過見込み
- 新しいTrial・仕様変更が不可欠
- 正式Production経路が使用できない

非Blockingの確認事項を、勝手に新しいユーザー判断へ格上げしない。

### 9. 最終報告

以下を簡潔に報告する。

1. Standard／Advancedの試聴ページURL
2. 正式Style適用結果
3. AUW・音声品質判定
4. K2代替音声の有無・件数
5. 工程別実測費用と総額
6. Batch換算の量産原価・70円目標との差
7. Family XのProduction Wiring最終判定
8. 本当にユーザー判断が必要なBlocking事項のみ

FableはClaude Codeの完了報告を鵜呑みにせず、承認済み仕様・正式Production runtime evidence・テスト結果・QCDを照合して独立判定すること。

**完成音声と試聴ページを提示した段階で報告すること。ユーザーによる試聴評価を勝手にPASS扱いしない。**
