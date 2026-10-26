ユーザー指示原文(2026-10-26、Fable経由で逐語保存)

# Family X「AI島」記事｜現行版採用・Human Review実走指示

## 1. ユーザー決定

**切り口は①現行版を採用します。記事の再生成は不要です。**

今回の目的は、記事の面白さをさらに改善することではなく、**Key Phrase・文法Human Reviewシステムが正式Production経路で正しく機能することの検証**です。

- 現行R2本文・Standard／Advanced英訳を維持。
- B3・Writerの再実行は行わない。
- 記事の切り口を理由とした追加修正・Trialは不要。
- OPEN-526の切り口判断はユーザー決定済みとして記録。

## 2. Human Reviewの実施

以下の3項目について、既存の承認済みHuman Reviewシステムを使用してください。

1. Standard Key Phrase
2. Advanced Key Phrase
3. Advanced Part 2 文法・構文解説

**今回はHuman Reviewの実動作確認が主目的なので、AI推奨候補の自動確定で済ませず、人間による選択・確定経路を実走させます。**

現在の候補・AI推奨順位・選定理由を既存仕様どおり提示し、ユーザーによる選択を待ってください。

ユーザーの候補選定をClaudeやFableが代行してはいけません。

## 3. Human Review確定後のProduction継続

ユーザーが3項目を確定したら、正式Production経路から制作を再開してください。

以下を必ず確認します。

- Human Review候補の提示・選択・確定・保存が正常に動作する。
- AI推奨と異なる選択でも正しく反映される。
- 確定済みのKey PhraseがPart 1・TTS・公開ページまで一貫して反映される。
- 確定済み文法解説がAdvancedのPart 2に反映される。
- 再開時にResearch・B3・Writer等の不要な再生成が発生しない。
- retry／fallback／resumeとの整合が維持される。

その後、TTS・ASR・品質検査・組立を実施し、Standard／Advancedの完成版試聴ページを作成してください。

## 4. 品質・費用・進行管理

- 既存の承認済み品質基準・Production仕様を維持する。
- 新仕様の追加やPrompt変更は行わない。
- 不具合は委任範囲内で原因究明・修正・検証まで自律的に対応する。
- API費用は案件上限200円以内。
- 不要な待機・逐次処理を避け、独立作業は並列化する。
- 品質 ＞ 完成速度 ＞ 量産単価の優先順位を遵守する。

## 5. 完了条件

次の証拠を取得してください。

1. 3項目のHuman Review操作・確定記録
2. 確定結果と後続成果物の一致
3. 正式Production経路でのruntime evidence
4. 必須Regression／Integration／ASR検査PASS
5. Fable独立受入
6. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Git反映
7. Standard／Advanced完成版試聴URL
8. 実費・量産単価への影響・未解決事項

Human Reviewシステムの検証成功と、記事自体のユーザー最終試聴承認は区別してください。

**まず3項目のHuman Review候補をユーザーが選択できる状態で提示してください。確定後は、不要な再承認を求めず完成版まで進めてください。**
