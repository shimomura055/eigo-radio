# ユーザー指示原文(逐語、2026-10-29受領。管理ID: (U)HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01。仕様①候補提示前の品質検査・仕様②重複アラーム非ブロッキング=APPROVED_FOR_PRODUCTION(X/Y/Z・Std/Adv)、Family Y姓テーマ記事の選定確定(Std: old-fashioned、Adv: 元の選定維持))
<<<USER>>>
# Claude Codeへの指示｜Key Phrase等の選定フロー改善・重複アラーム非ブロッキング化

## 1. 目的・承認Status

以下2項目をユーザーが正式採用しました。

**Status：APPROVED_FOR_PRODUCTION**

対象は **Family X／Y／Z、Standard／Advancedの全組み合わせ**です。

承認済みの品質水準を維持しながら、選定後の不要な手戻りとProduction停止を解消してください。

両項目とも、正式Productionへの実装・検証・SSOT／Git反映まで進め、**PRODUCTION_WIRED**を目指してください。

## 2. 仕様①：品質検査を人間への候補提示前に実施

### 今回の記事への適用

Family Y「夫が妻の姓を選ぶとき、それぞれの声」Standardの選定について、

- 変更前：`old-fashioned about it`
- **変更後：`old-fashioned`**

とします。それ以外のユーザー選定内容は維持してください。

### 全Family／全レベル共通仕様

1. Key Phrase／Word、追加解説、本文意味等の候補を、人間に提示する前に品質検査する。
2. 品質上の問題がある候補は、原則として選択可能な候補として提示しない。
3. `REVIEW_REQUIRED`等の判定は、人間への候補提示前に解決し、必要な人手確認と選定フォームでの扱いを整合させる。
4. 人間が選定した後になって、提示前に検出できた品質問題を理由に再選定を求める運用を解消する。
5. 既存の承認済み品質基準・検査条件は変更しない。

候補生成、品質検査、Human Reviewフォーム、確定処理、Production後続経路を調査し、整合するよう修正してください。

## 3. 仕様②：意味・用法の重複アラームを非ブロッキング化

### 全Family／全レベル共通仕様

1. 人間が選定した表現同士に意味・用法の重複がある場合、従来どおりアラームを出す。
2. アラームの内容・対象表現・判定理由を人間が確認できるようにする。
3. **重複アラームだけを理由として、選定確定、音声生成、組立、正式Productionを停止しない。**
4. 人間の選定結果を維持し、後続工程へ進める。
5. 重複以外の品質Gate・安全条件は従来どおり維持する。

重複アラームは品質確認のための情報提供であり、Production停止条件ではありません。

### 今回のFamily Y Advancedへの適用

以下のユーザー選定を維持してください。

- Key Phrase：`let go of`
- 追加解説：`hold one's son back`
- 本文意味：`give something up`

重複アラームは記録・表示しますが、この重複を理由に選定を差し戻さず、後続工程に進めてください。

## 4. 実装・検証範囲

Family X／Y／ZのStandard／Advancedそれぞれについて、以下を確認してください。

- 正式Productionの候補生成からHuman Review、確定、後続工程までの一貫した動作
- 品質検査が候補提示前に実行されること
- 品質上不適切な候補が選択可能な状態で提示されないこと
- 重複アラームが表示・記録されてもProductionが停止しないこと
- retry／fallback／regeneration／resume／再選定との整合
- 既存の非重複品質Gateが維持されること
- DEV／Trial専用経路ではなく、正式初回Production経路に適用されていること

必要十分なRegression／Validator／integration testを実施し、各Family・各レベルの正式runtime evidenceを取得してください。

未承認の追加仕様や品質基準変更は行わないこと。

## 5. 既存仕様・過去Trialとの整合

作業前にCURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、関連コード・過去Trialを確認してください。

特に以下を整理してください。

- 候補提示前の品質検査と確定時検査の役割分担
- 既存のoverride機構との整合
- 重複判定を停止条件としている箇所の洗い出し
- 不要となった旧ブロック処理・旧検査の撤去要否
- Family間での仕様・実装差異
- 後続経路に未承認仕様や旧仕様へのDangling Referenceが残らないこと

旧検査を無条件に削除するのではなく、必要な検査は維持し、重複アラームの停止機能のみを変更してください。

## 6. Family Y記事の再開

今回の選定内容を反映し、既存承認・予算・作業範囲内で停止していた制作を再開してください。

- Standard：`old-fashioned`へ変更し、その他の選定は維持。
- Advanced：元の選定内容を維持し、重複アラームを記録したうえで確定。
- 他の選定を独断で変更しない。
- 音声生成以降は既存の承認済み制作手順・Gateに従う。

既存の予算上限・STOP条件を超える場合は、無断で進めないでください。

## 7. 完了条件・報告

以下をすべて確認してからPRODUCTION_WIREDと報告してください。

1. Family X／Y／ZのStandard／Advancedすべてに正式配線済み。
2. 正式runtimeでの発火証拠を取得。
3. 必須テストPASS。
4. retry／fallback／resume等との整合確認済み。
5. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新済み。
6. Git反映済み。
7. ユーザー承認仕様とProduction実動作が一致。
8. 未解決Open Item、未処理判断、Dangling Referenceがないことを確認。

Fableによる独立受入評価も実施してください。

報告では、①②それぞれのFamily別・レベル別Status、実動作証拠、残課題、QCD影響、Family Y記事の進捗を簡潔に示してください。

## 8. 自律解決・STOP条件

既存承認範囲内の不具合は、原因究明→修正→検証を自律的に進めてください。必要に応じて独立作業を並列化し、品質を守りながら最短で完了してください。

ただし、品質基準の変更、新たな未承認仕様、予算超過、重大な安全・品質問題、明示STOP条件に該当する場合は停止・報告してください。

**今回のユーザー決定について再承認を求める必要はありません。**
<<<END>>>
