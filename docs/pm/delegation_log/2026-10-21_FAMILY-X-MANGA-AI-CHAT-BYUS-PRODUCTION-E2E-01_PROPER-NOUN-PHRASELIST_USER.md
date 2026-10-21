# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_06(固有名詞・Ledger・Phrase List調査)
# Claude Code／Fableへの指示
## Family X 漫画AI（byUs）— 固有名詞・Pronunciation Ledger・Azure Phrase List調査

### 1. 調査目的

対象：Family X「漫画のキャラクターとAIで会話（byUs）」

Production run：`run_byus_01`

Advanced Full Story第1部・第3部で、ASRが以下のように認識した。

- byUs → Bias／BIOS／Buy Us／Byus／Baias／BAYAS／FAYAS
- LINE → Lion

これらの認識不一致によってTTS再試行が発生した。

**既存の固有名詞対策・読み登録・Azure Phrase Listが、今回のProductionで正しく機能していたか調査する。**

### 2. 必須確認事項

**① 固有名詞としての認識**

- `byUs` と `LINE` は固有名詞として抽出・分類されていたか。
- どの工程で、どのような分類結果になったか。
- 抽出されていなかった場合、その理由は何か。

**② Pronunciation Ledger／Phrase Listへの登録**

各語について、以下を確認する。

- Pronunciation Ledgerに登録されていたか。
- canonical spellingと登録された読み方は何か。
- 読み方の根拠・登録経路は何か。
- Azure Phrase Listに実際に渡されていたか。
- 渡されたPhrase Listの具体的な内容は何か。

**Pronunciation Ledgerへの登録と、Azure Phrase Listへの投入を区別して報告すること。**

**③ 重み2.0の実際の適用**

Repoでは `er006_secondary_asr_01.py` に以下の設定が存在する。

- `AZURE_PHRASE_LIST_WEIGHT = 2.0`
- Phrase Listが空でない場合、`setWeight(2.0)` を実行

確認すべきこと：

- 今回のAdvanced第1部・第3部で実際にこの経路が使用されたか。
- 各Azure呼び出し時のPhrase List内容と重み設定。
- `setWeight(2.0)` が実行された証拠。
- 設定されていたが期待どおりに認識されなかったのか、そもそもPhrase Listに対象語が存在しなかったのか。
- retry／Secondary再実行でも同じ設定が維持されていたか。

コード上の定数が2.0であるだけでは、正常動作の証拠としない。

Azure内部の重み付け効果そのものが直接観測できない場合は、**APIに渡した設定の確認と、実際の認識精度の評価を分けること。**

**④ 不一致・再試行への影響**

第1部・第3部の各Takeについて、次を整理する。

- Primary／Secondary ASRの転写結果
- 固有名詞が原因となった不一致
- 固有名詞以外の不一致
- 同音等価判定等が発動したか
- 最終PASS／NGとTTS再試行の理由

特に、`byUs → Bias／Buy Us` のような同音の可能性がある表記差が、なぜ既存の同音許容機構で解決しなかったのかを確認する。

### 3. 原因分析・Fable独立評価

問題が見つかった場合は、以下のどこに原因があるか特定する。

1. 固有名詞の抽出・分類
2. Pronunciation Ledgerへの読み登録
3. Azure Phrase Listへの受け渡し
4. 重み2.0の適用
5. ASR結果の同音等価判定
6. TTS自体の発音

単に「ASRが特殊な固有名詞に弱い」で終了しない。

Fableは原因分析と証拠を独立検証し、品質・再試行削減・量産単価への影響を評価する。

### 4. 作業範囲・STOP条件

今回は**調査・原因分析のみ**。

- 有料のTTS／ASR再実行は行わない。
- Productionのコード・Prompt・設定を変更しない。
- 未承認の読み方や例外ルールを追加しない。
- 新たなTrialを開始しない。
- 既存ログ・成果物・コード・承認履歴を再利用する。

原因が既存承認仕様からの逸脱だった場合は、是正案を提示する。新仕様・品質基準の変更が必要な場合はユーザー判断へ上げる。

### 5. 報告形式

まず以下の比較表を提示する。

| 確認事項 | byUs | LINE |
|---|---|---|
| 固有名詞として抽出・分類 | | |
| Pronunciation Ledger登録 | | |
| 登録された読み | | |
| Azure Phrase List投入 | | |
| Azure重み2.0の適用 | | |
| 実際のASR認識 | | |
| 問題・原因 | | |

続いて、以下を簡潔に報告する。

1. **既存の固有名詞対策は仕様どおり機能していたか。**
2. **重み2.0は今回の実行で適用されていたか。**
3. **なぜbyUs／LINEの認識不一致を解決できず、TTS再試行に至ったか。**
4. **既存仕様内で是正可能か、新たなユーザー判断が必要か。**
5. **再発防止によって削減可能と見込まれる再試行・費用・時間。**

GitHubのコード上で確認できることと、ローカルProduction実行ログでしか確認できないことを明確に区別する。

**証拠が存在しない項目は推測でPASSにせず、「未確認」と明記する。**
