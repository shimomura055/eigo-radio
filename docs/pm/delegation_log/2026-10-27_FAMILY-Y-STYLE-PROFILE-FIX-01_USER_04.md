# Claude Code指示｜Family Y再配達記事Closeout＋Style継承Production Wiring完了確認

## 1. ユーザー正式決定

対象：Family Y「宅配の再配達は有料にすべきか？」Standard／Advanced、およびFamily Yの正式Production音声経路。

以下を正式決定として受領してください。

**A. 再配達記事**

- Standard／Advancedともにユーザー最終試聴PASS・正式承認。
- 現行完成版 `_03` の音声・本文・Key Phrase・学習内容を承認。
- 表示修正に伴う音声再生成・再試聴は不要。

完成版：
https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html

**B. Voice説明文**

以下の文言を正式採用する。

「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」

- 今回の再配達記事に反映。
- Family Y共通の説明文として使用。
- 将来のアプリ表示でも同じ文言を使用する。
- 旧文言が正式Productionのテンプレート・公開ページ生成処理に残らないよう整合を確認。
- 実際の投稿意見に基づいて制作した記事に適用し、根拠のない出典主張を生成しない。

**C. 開発用Chunk境界マーカー**

- 実際のTTS Chunk分割境界だけを `⏸` で表示する。
- 秒数・タイムスタンプ・説明文は不要。
- ASRなどで検出した通常の音声ポーズは表示しない。
- **開発段階のユーザー確認用表示に限定する。**
- 量産時のエンドユーザー向けスクリプト・公開コンテンツ・将来のアプリには表示しない。
- X/Y/Z共通の表示仕様とする。
- 実際のChunk分割・追加ポーズ長・音声生成仕様は変更しない。

今回の再配達記事について、技術的なポーズ表示 `⏸0.70s@0:39.0` 等を撤去し、実際のChunk境界がある箇所だけ簡単な目印に置き換える。

表示修正のみのため、承認済み音声の再生成・再試聴は行わない。

## 2. OPEN-537｜Style継承のProduction Wiring確認【重要】

Family Yの音声StyleがFamily Xの承認済みStyleを継承していなかった不具合について、**PRODUCTION_WIREDの到達状況を改めて確認してください。**

既知の事実：

- 修正実装：commit `3af84a499`
- Y runnerが承認済みStyle profile `fx_20261017` を継承
- 課金前のStyle固定記録
- Style不一致を停止させるfail-closed Gate
- Style関連テスト37件PASS
- 再配達 `_03` の正式音声でStandard 18/18、Advanced 15/15のStyle一致
- `_03` はユーザー最終試聴PASS

ただし、直近のCURRENT_SPECでは、Y経路のPRODUCTION_WIRED判定は別途Fableが実施する旨の記述が残っており、最終受入・Closeoutは未確認です。

### 実施内容

まず、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／PM_GOVERNANCE／関連Git commit／runtime evidence／Fable受入記録を照合する。

**すでにPRODUCTION_WIREDなら：**

- Fable正式判定の証拠と日付を提示。
- OPEN-537のStatus、CURRENT_SPEC、DECISION_LOG、Git反映を確認。
- 記録漏れや古い「未完了」記述があれば是正。
- 重複した再実装・有料検証は行わない。

**まだPRODUCTION_WIREDでなければ：**

既存の承認済み作業範囲内で不足項目を解消し、PRODUCTION_WIREDまで進める。

確認条件：

1. Family Yの正式初回Production音声経路で `fx_20261017` が既定適用される。
2. Standard／Advancedの全対象部位で承認済みStyleと実際のStyleが一致する。
3. Style不一致時にfail-closed Gateが機能する。
4. retry／fallback／regeneration／resumeで承認済みStyle仕様が維持される。
5. DEV／Trial専用経路ではなく、正式runnerでのruntime evidenceがある。
6. actual model_id、routing、Style profile、Style実測記録を確認。
7. 必須Regression／Validator／Integration TestがPASSする。
8. SSOT／Git反映とFable独立受入を完了する。

今回の再配達 `_03` の実測証拠を優先して再利用し、既に満たした項目のために音声を再生成しないこと。

未確認項目があれば、その項目だけ必要十分な検証を行う。

**完成記事のユーザー試聴PASSをもって、Style継承機能のPRODUCTION_WIREDを自動認定しないこと。**

また、音声Styleの新たな変更・Voice変更・未承認のFallback仕様変更は行わない。

## 3. Family Y再配達記事のCloseout

以下を実施する。

1. `_03` のStandard／Advancedユーザー最終試聴PASSを正式記録。
2. 承認済みVoice説明文へ修正。
3. 開発用スクリプトのChunk境界表示を是正。
4. 正式公開ページ・今後のページ生成テンプレートとの整合を確認。
5. 音声ファイル・本文・KP・文法解説などの承認済み内容が不変であることを検証。
6. 必要な公開検査・Git反映・SSOT更新を完了。
7. Fableが表示修正・Closeoutを受入評価。

表示修正と無関係な記事改変は禁止する。

将来アプリ向けの文言は仕様として記録するが、今回のScopeにアプリ開発そのものは含めない。

## 4. X/Y/Z共通のChunk境界表示

開発用スクリプト表示について、Family X/Y/Zの既存生成経路を確認し、今回の承認済み表示仕様に統一する。

- 実際のChunk分割境界にのみ `⏸` を表示。
- 音声解析上のポーズとは区別。
- 開発／ユーザー確認用の表示と、エンドユーザー向け量産表示を分離。
- エンドユーザー公開物へのマーカー混入を防止。
- 不要になった旧表示処理・旧テストを整理。

全Familyで検証するが、既存の音声生成・Chunk分割方式そのものは変更しない。

## 5. QCD・実行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 独立したStyle受入確認、表示修正、SSOT確認は原則並列化。
- 既存evidence・テストを最大限再利用。
- 不要なAPI実行・TTS再生成・再試聴を禁止。
- 承認済み範囲内の不具合は原因究明から修正・検証まで自律実施。
- 日次開発費1,000円（JST）と個別承認枠を遵守。
- ユーザー未承認の新仕様・品質基準変更、重大なblocker、予算超過はSTOPして報告。
- 必要十分な品質に到達した時点で完了する。

## 6. 最終報告

以下の順に簡潔に報告してください。

1. **OPEN-537の最終Status：PRODUCTION_WIRED到達有無**
2. Style継承の正式runtime evidence・Fable受入結果
3. 再配達 `_03` のユーザー承認記録・Closeout結果
4. Voice説明文の正式反映結果
5. X/Y/Z共通Chunk境界表示の修正・公開検証結果
6. QCD実績
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git更新結果
8. 残る未解決事項（ある場合のみ）

**完了条件：OPEN-537の正式Production Wiringを証拠付きでCloseoutし、再配達記事の承認・表示修正・公開反映を完了すること。**

既に完了済みの作業は重複実行せず、未完了部分だけを補完してください。
