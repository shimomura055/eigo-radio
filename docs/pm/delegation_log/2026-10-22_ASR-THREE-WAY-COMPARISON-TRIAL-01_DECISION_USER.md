[受領日2026-10-22 / 受領者Fable / 管理ID: ASR-THREE-WAY-COMPARISON-TRIAL-01(#136採用判断) / 本文751文字 / sha256(本文のみ)=810d3c7479e8f9964b9a328d2fb0727c8d7cd83d36018da824ad77554087e1b0]

## Claude Codeへの回答・指示：ASR 3方式比較Trialの採用判断

ASR-THREE-WAY-COMPARISON-TRIAL-01（#136）について、ユーザー判断を以下のとおり確定する。

### 1. 正式決定

1. **Primary：OpenAI `gpt-4o-mini-transcribe` を維持。**
2. **Secondary：Azure Speech STTを維持。**
3. **ローカルWhisperのProduction導入は不採用。** 運用複雑化を避ける。
4. Primary／Secondaryの入替は行わない。
5. 今回の比較Trialに基づく追加精度検証（Store 333件へのAzure追加検証等）は実施しない。

### 2. Key Phraseの両方PASS仕様

Key PhraseはPrimary／Secondaryの両方PASSを必須とする方針。

ただし、この仕様の実装状況・Production整合性については**別指示系統で確認中**。

今回の指示では調査・実装・追加Trialを行わない。重複作業を禁止する。

### 3. Closeout

- 今回のモデル比較Trialの採否を、上記ユーザー判断に従って整理する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／USER_DECISION_REGISTERに必要な記録を反映する。
- Gitへ反映する。
- **既存Productionコード・モデル構成は変更しない。**

記録更新後、変更ファイル・commit・残存Open Itemのみ簡潔に報告すること。

今回の指示による新規Trial・API呼出は不要。
