# Claude Code／Fableへの正式指示
## Family X Standard日本語解説 S3 — Production Wiring

**管理ID：FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01（Phase B）**

### 1. ユーザー正式承認

ユーザーは、S3「親しみのあるニュースナレーター」を**Family X全体のStandard日本語解説の正式Styleとして採用することを承認した**。

- 対象：Standard Preview／Comment1〜4
- 旧正式Style：R2
- 新正式Style：S3
- Trial：`VALIDATED`
- 現在Status：`APPROVED_FOR_PRODUCTION`
- 今回の到達目標：`PRODUCTION_WIRED`

**追加のStyle選定・採用判断は不要。Production反映を進めること。**

### 2. 採用するStyle

`coffee_ja_style_trial_04`のS3を逐語で使用する。

共通指示込みのStyle全文（199字、SHA `060c08fd…`）を、既存Trial成果の正式記録と照合すること。

名称から推測して再構成したり、独自に調整したりしない。

基準資料：

`er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md`

Coffee Phase Aの実走証拠・差し替え成果も参照する。

### 3. Production配線

Family Xの既定Style profileを更新し、Standard日本語Preview／Comment1〜4の正式StyleをR2からS3へ変更する。

最低限、以下の全経路を確認する。

- Production正式初回生成経路
- retry
- fallback
- regeneration
- Local Rewrite等の関連経路
- 既定profileの自動適用
- Style解決失敗時の動作

**特別なCLI指定をしなくても、正式Production経路でS3が使用されること。**

DEV／Trial専用scriptへの実装だけで完了扱いにしない。

### 4. Phase Aで判明した注意点

OPEN-405に記録された次の3点を確認する。

**① 既存成果物への副作用**

正式Gate関数により、R2版のJSONパス表記が一時的に書き換わった。

Phase Bでは、既存成果物やMaster Audio Storeを意図せず改変しないことを確認する。

必要な修正は今回のS3配線に直接関係する範囲に限定する。

**② Previewの音量処理**

正式CoffeeではPreviewは無加工、Commentは既存RMS目標を使用している。

S3配線によって、Previewの音量処理が意図せず変わらないこと。

既存の音量仕様を勝手に統一・変更しない。

**③ 未承認Styleへの無警告fallback**

Style適用失敗時、未承認Styleが無警告で使われる既存経路があるとの報告。

今回の正式採用により、その経路がS3の適用保証を破らないか確認する。

未承認Styleへの無警告切替を、S3が正常適用されたものとしてPASS扱いしないこと。

必要な修正が既存の承認済み仕様の範囲で安全に行える場合は対応する。

**新しいfallbackの仕様選択が必要な場合は、ユーザー判断事項としてSTOPすること。**

### 5. Production runtime evidence

正式Production経路でS3が実際に発火したことを確認する。

証拠として以下を残す。

- Production entrypoint
- 適用されたStyle ID／version
- 実際に送信されたStyle全文のSHA
- actual model_id／Voice
- Preview／Comment1〜4の対象セクション
- TTS実行結果
- AUW／ASR等の品質結果
- 既定profileからS3が選択された証拠

必要な有料TTS実行については既存費用Gateを適用する。

Phase Aの試聴版が良好だったことだけで、正式Production配線のruntime証拠の代用としない。

### 6. テスト・整合性確認

必要なRegression／Validator／integration testを実行する。

特に次を確認する。

- Family X Standardの対象5セクションにS3が適用される
- Advanced側に影響しない
- Key Phrase仕様が変わらない
- Full Story／In One Line／効果音等が変わらない
- retry／fallback／regenerationでも承認仕様が維持される
- 既存R2成果物が変更されない
- Master Audio Storeに不正な上書きがない
- Dangling Referenceが存在しない

テスト未実施の経路を「動作確認済み」と報告しない。

### 7. SSOT・Decision管理

正式採用と実装状況を以下へ反映する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS（#105・OPEN-405等、関係項目）
- 必要なStyle profile記録
- runtime evidence
- テスト結果
- Git commit／push／merge

承認済みS3とProduction実装のStyle全文が一致していることを確認する。

### 8. 費用・作業範囲

**既存費用ルールを遵守すること。**

- 実行前に費用見積と当日累計を確認
- ¥100を超える新規実行は、既存承認範囲を確認
- 日次¥1,000のsoft budgetを維持
- 不要な音声再生成を避ける
- commitを伴う作業は同時に1件のみ

今回の対象外：

- 記事本文の修正
- S3の追加調整・別Style探索
- Advanced／Key Phraseの仕様変更
- Family Z／Yへの展開
- Family A／B／Cの開発
- Research／LedgerのコストTrial
- Detective演出の変更
- 無関係なOpen Itemの改修

### 9. STOP条件

次の場合のみSTOPして報告する。

- 新しい未承認仕様の採用が必要
- 重大な品質不一致
- 正式Production経路でS3を適用できない
- 必須Human Review／品質Gateに到達
- 費用Gateを超過する
- 既存成果物への意図しない破壊的変更
- 承認内容とruntime動作が一致しない

非Blocking事項を理由に、不必要な追加Trialや仕様開発を開始しないこと。

### 10. 最終報告・Closeout

Fableは実装報告を独立レビューし、以下を照合する。

1. Production正式初回経路でS3が適用されたか
2. retry／fallback／regenerationとの整合
3. actual model_id・Style SHA等のruntime evidence
4. 必要なテストのPASS
5. R2版成果物・Master Audio Storeの保全
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
7. commit／push／mergeの確認
8. 承認されたS3と実際のProduction挙動の一致
9. 未解決のBlocking事項・承認済み未配線事項の有無

**すべて満たした場合のみ `PRODUCTION_WIRED` と判定する。**

未確認項目がある場合は、実装済みであっても`APPROVED_FOR_PRODUCTION`のまま追跡する。

最終報告は、技術詳細の羅列ではなく、**「正式反映できたか・証拠は何か・残課題は何か」**を最初に簡潔に示すこと。

今回の承認事項をProductionへ確実に反映し、未配線のまま放置しないこと。
