<pasted_content id="a638">
# Claude Codeへの指示
## Key Phrase日本語意味 X2p' — XYZ共通Production Wiring

### 1. ユーザー正式承認

**X2p'をFamily X／Y／Z共通仕様として正式採用する。**

Status：`APPROVED_FOR_PRODUCTION`

目的は、`draw a line` →「線を引く」のように、文脈上の意味を取り違えた字義訳を防止すること。

採用する方式は、Trial_06で検証済みの **X2p'「本文中での語義を確定してから、その意味に沿って日本語訳を生成する」方式**。

- X限定ではなくXYZ共通。
- 改良Promptの追加Trial・再採否判断は不要。
- Trial_06で確認した軽微な訳の弱さは、ユーザーが実例を確認したうえで許容済み。
- ただし、実際の意味の誤りや不自然な訳を新たに許容するものではない。
- 既存のKey Phrase選定・一般化・日本語意味再整合仕様は維持する。

### 2. 実装前の整合確認

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、過去のTrial_05／Trial_06、Productionコードを確認する。

特に以下を区別すること。

- A-1：見出し語の一般化
- 課題②：所有格の一般化
- 既存gloss再整合：語の欠落・人称不整合への対応
- **X2p'：文脈に沿った日本語意味の生成**

これらは別仕様であり、X2p'によって既存の承認済み機能を壊したり、不要に重複させたりしない。

また、Trial専用PromptやDEV経路からの暗黙参照を残さないこと。

### 3. Production実装

X2p'を正式なKey Phrase日本語意味生成経路に組み込む。

対象はFamily X／Y／Z。

**Family共通の処理は原則として共有化し、Family別の重複実装を避ける。**

以下を確認する。

1. 新規記事の正式初回Production経路で適用されること。
2. retry／fallback／regeneration／resumeでも承認済み仕様との整合が保たれること。
3. 日本語意味の生成・再整合・Validator・音声化・表示まで、後続工程と矛盾しないこと。
4. X2p'がTrial専用コードに依存しないこと。
5. 既存のKey Phrase一般化・同音救済・音声検査の仕様を変更しないこと。

Family Yについては正式Production経路の実装状況を確認する。

Yの正式入口が未完成の場合、X2p'を共通処理へ実装しても、Yを `PRODUCTION_WIRED` と判定してはならない。

未完了理由と必要な対応をOPEN_ITEMSへ明記すること。既存の承認範囲外となるFamily Y全体の新規Production構築を、今回の作業として無断開始しない。

### 4. 品質検証

過去のTrial成果物・入力データを最大限再利用する。

確認項目：

- `draw a line` など既知の字義訳問題が改善されていること。
- 本文中の意味と日本語訳が一致すること。
- 正しく字義訳すべき表現を誤って比喩化しないこと。
- Trial_06の通常KPで確認した軽微なTHINを理由に、承認済み品質基準を独断で変更しないこと。
- 既存の正常なKey Phraseで重大なRegressionがないこと。
- Standard／Advanced双方で機能すること。
- X／Y／Zそれぞれの適用状況が明確であること。

**承認済み品質を満たした時点で検証を終了し、不要な追加Trialや磨き込みを行わない。**

### 5. 正式runtime evidence

`PRODUCTION_WIRED` の判定には、正式Production経路でX2p'が実際に発火した証拠が必要。

少なくとも以下を記録する。

- 正式入口・実行経路
- actual model_id
- 使用したX2p' Prompt／Version
- 入力本文・生成結果との対応
- X2p'適用のruntime evidence
- 必須Validator／Regression／integration test結果
- retry／fallback／regeneration／resumeとの整合
- Family別のProduction配線Status

DEV・Trial専用経路での成功だけをもってProduction Wiring完了としない。

### 6. QCD・自律解決

優先順位は **品質 ＞ 完成速度 ＞ 量産単価**。

Trial_06では、X2p'による追加費用は約0.44円／記事セットと報告されている。

Production実装後も、この水準から不必要に費用が増えないことを確認する。

- 独立作業は並列化。
- 既存成果物を再利用。
- 不要なLLM呼出や音声再生成を避ける。
- 承認済み予算・仕様・Gate内の技術的不具合はFable管理下で自律解決。
- 同じ失敗を繰り返す場合はアプローチを見直す。
- 重大な品質問題、予算超過、新仕様が必要になった場合のみSTOPしてユーザー判断を求める。

### 7. SSOT・Git反映

以下を更新・確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- 必要なProduction実装・テスト
- Runtime evidence
- Git commit／push

古い未承認PromptやTrial専用経路へのDangling Referenceがないことを確認する。

Fableによる独立受入評価を実施すること。

### 8. 関連する未完了記事

Family X『英国の電車マナー』は、`draw a line` の日本語意味問題によりKey Phrase修正後の最終版提出が保留されている。

X2p'のProduction Wiring完了後、承認済み仕様によるKey Phrase修正と必要部分の音声・表示更新を行い、Standard／Advancedの最終版を再提出すること。

修正対象外の完成済み音声・本文は再生成しない。

記事のユーザー最終試聴PASSは別途判断とし、自動承認しない。

### 9. 最終報告

次の順序で報告すること。

1. **結論：X／Y／Zそれぞれの最終Status**
2. X2p'の正式Production実装内容
3. 正式runtime evidence・テスト結果
4. 字義訳改善効果・既存品質への影響
5. 実測費用・量産単価への影響
6. 『英国の電車マナー』最終版試聴URL
7. Fable独立受入判定
8. SSOT／Git反映状況と残存Open Item

### 10. PM Gate

- ユーザー正式採用：**完了**
- Production Wiring：**今回の作業対象**
- 各Familyで全条件を満たした場合のみ `PRODUCTION_WIRED`
- 未配線Familyは理由を明記して追跡
- ユーザー判断を必要としない技術的問題で作業を止めない
- 新たな品質基準や追加仕様を独断で導入しない

**最終目標：X2p'をXYZ共通の承認済み仕様として正式Productionに反映し、実動作と品質を確認すること。**
</pasted_content id="a638">