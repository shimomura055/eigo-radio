# Claude Code／Fableへの指示
## Family X Standard日本語解説 S3採用・Production Wiring

**管理ID：FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01**

### 1. 目的・ユーザー判断

Coffee Standard日本語解説Style Trialの結果、ユーザーは**S3「親しみのあるニュースナレーター」**を選定した。

対象はStandardの日本語Preview／Comment1〜4。

S3の温かみ・親しみやすさ・明瞭さを保ちながら、落ち着いたテンション・語尾・抑揚を実現することが目的。

**今回の到達目標はPRODUCTION_WIRED。ただし、正式採用のユーザー判断を途中Gateとして必須とする。**

- S3 Trial評価：`VALIDATED`
- Coffeeへの限定適用：検証用。正式Production仕様変更ではない
- Coffee試聴後：ユーザー正式採用判断
- 採用承認時：`APPROVED_FOR_PRODUCTION`
- 配線・テスト・証拠・SSOT／Git反映完了時：`PRODUCTION_WIRED`

ユーザー判断前にProduction配線を開始しないこと。

### 2. 正式Styleの特定

以下の既存Trial成果を使用する。

- Trial：`coffee_ja_style_trial_04`
- Style：**S3**
- 正式Coffee完成版のStandard Preview／Comment1〜4

S3のStyle全文は保存済みPrompt一覧から取得し、**共通指示を含む逐語一致の全文**を使用する。

名称からの再構成・要約・独自調整は禁止。

参考：

`er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md`

### 3. Phase A：Coffee限定差し替え

**到達可能Status：VALIDATED／USER_DECISION_REQUIRED**

正式Coffee完成版の日本語Preview／Comment1〜4のみ、S3で再生成する。

以下は変更しない。

- 日本語原稿
- 英語記事・英語音声
- Key Phraseの全仕様・音声
- Voice、モデル、速度、音量処理等の既存正式設定
- Assembly上の他のセクション
- Family XのProduction正式Style profile

TrialページではPreviewの音量処理が正式Coffeeと厳密に一致していなかったため、**今回のCoffee差し替えでは正式版の処理条件に合わせること。**

再生成した5セクションに既存AUW／ASR等の必要な品質確認を適用し、完成版Coffeeの試聴ページを更新または別版として提供する。

旧R2版は比較・復旧可能な状態で保持する。

**ユーザーがS3適用版を試聴し、正式採用を判断できる状態まで進めること。**

### 4. Phase A完了時のMandatory STOP

以下を報告してSTOPする。

1. S3差し替え版Coffeeの試聴URL
2. 対象5セクションの品質確認結果
3. 原稿・Voice・モデル・Style・音量処理の照合結果
4. 既存R2版との変更差分
5. 実測費用
6. 残存する品質上の問題

**この時点ではProduction採用を決定しない。**

ユーザーへ「S3をFamily XのStandard日本語解説の正式Styleとして採用するか」を確認する。

ユーザーが正式採用を承認した場合のみPhase Bに進む。

### 5. Phase B：Production Wiring

**開始条件：ユーザーによる正式採用承認**

承認後、S3をFamily X全体のStandard日本語Preview／Comment1〜4の正式Styleとして配線する。

確認対象：

- Production正式初回経路
- retry
- fallback
- regeneration
- Local Rewrite等の関連後続経路
- Style profileの既定選択
- 実送信Prompt全文・SHA
- actual model_id／Voice／音声処理条件
- Validator／Regression／integration test
- Dangling Reference Check

DEV／Trial専用定義をProductionから暗黙参照しないこと。

S3が適用できなかった際に、未承認Styleが無警告で使用される経路を見落とさないこと。

**新しいfallback仕様を独断で設計・採用しない。** 既存仕様との矛盾が見つかった場合はSTOPして報告する。

### 6. Production runtime evidence

コード変更や単体テストだけで完了扱いにしない。

正式Production経路でS3が実際に使用されることを確認し、以下を記録する。

- 正式Production entrypoint
- 適用されたStyle ID／version
- 送信Prompt SHA
- 実際のmodel_id／Voice
- 対象5セクションの出力結果
- AUW／ASRの品質判定
- retry／fallback等との整合確認結果

正式経路での発火を確認できない場合、`PRODUCTION_WIRED`とはしない。

### 7. SSOT・Git反映

正式採用承認後に必要な記録を更新する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Style profile／関連仕様
- 必要なテスト・runtime evidence
- commit／push／merge結果

Coffee限定の検証結果とFamily X全体の正式仕様を明確に区別する。

S3に関するTrial結果は、正式採用前にProduction仕様として記載しないこと。

### 8. 費用・QCD

既存の開発費ルールを遵守する。

Phase A・Phase Bそれぞれの事前費用見積を記録し、既存の承認権限・上限を超える場合はSTOPする。

不要な生成・重複Trialを避ける。

優先順位は**品質 ＞ 納期 ＞ コスト**。

S3の再調整、新候補の探索、別Styleの追加Trialは行わない。

### 9. 対象外

- Advanced音声
- Standard英語音声
- Key Phraseの全仕様
- 記事・日本語原稿の書き換え
- Detective演出の改善
- Family Z／Y
- Family A／B／C
- Research・Ledgerコスト最適化Trial
- 無関係なOpen Itemの改修

並行している別タスクとGit変更が衝突しないよう、**commitを伴う作業は同時に1件のみ**とする。

### 10. STOP条件・Closeout

以下の場合はSTOPする。

- Coffee S3版に重大な品質問題がある
- ユーザー正式採用判断が未取得
- 承認済み仕様とProduction挙動が一致しない
- 未承認の新仕様が必要
- Mandatory Human Review／品質Gateに到達
- 費用上限を超える見込み
- 正式経路のruntime evidenceが取得できない

Trial終了時は`REJECTED／VALIDATED／USER_DECISION_REQUIRED`のいずれかに分類する。

Phase B完了後はFableが独立受入を行い、Production Wiring Checklistを全項目照合する。

**未完了項目が1つでもあればPRODUCTION_WIREDと判定しない。**

今回の最初の報告は、Phase Aで作成した**Coffee S3差し替え版の試聴URLを先頭に提示**すること。

ユーザーの試聴・正式採用判断を待ち、その後にFamily X全体のProduction Wiringへ進むこと。
