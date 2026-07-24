# ER-003-B1-P3R 停止報告: A01 Preview音声生成が失敗

## 1. 結論

**通し音声プロトタイプは生成できませんでした。** 指示section 17に明記された停止条件「Aoedeで混在言語Previewを生成できない」に該当したため、指示section 17・18の指定通り、勝手に新しいTTS指示や別voiceへ切り替えず、ここで停止して報告します。

## 2. 何を試みたか

1. [ER-003-B1-P2でユーザーが採用したPattern A(Story/Drama)](../b1_p2/A01/listening_preview_raw.md)を、構造化JSONから直接抽出。
2. [ER-003-B1-P1でACCEPT済みのA01 B1本文](../b1_p1/A01/b1_article_raw.md)を、B2までに採用済みの台本schemaへ変換(新しい変換ロジックのみ追加、TTS instruction・音声処理は無変更)。
3. B2までに採用済みのTTS instruction(`er002_common.build_style_prefix()`、無変更)をPreviewの前に付与し、Aoedeで音声化を試行。

## 3. 失敗内容

Preview音声の生成(Structured Outputではなく、Gemini `gemini-2.5-pro-preview-tts`モデルへの`generate_content`呼び出し)が、以下のエラーで失敗しました。

```text
400 INVALID_ARGUMENT: Model tried to generate text, but it should only be used for TTS.
Make sure your instructions are clear to only generate audio from a given text transcript.
```

- 同一payloadで初回・再試行(技術的失敗時のみ許可された1回まで)ともに同一エラー。
- ネットワーク的な一時障害ではなく、**日本語と英語が混在するPreview本文**と、**採用済みnarration instruction**の組み合わせに対し、モデルが音声応答ではなくテキスト応答を試みたことによる、再現性のある拒否と判断しました。
- B1本文側のTTS呼び出しは、Previewが失敗した時点で一切実行していません(API呼び出し0件)。

## 4. 行っていないこと(指示section 17の明記通り)

- 別voiceへの切り替え
- Preview専用の新しいstyle instructionの追加
- 既存instructionの言い換え・拡張
- speed/pitch/rateの追加指定
- B1本文・Pattern A原稿の修正

## 5. 確認済み事項

- Pattern A source: `er003_output/b1_p2/A01/listening_preview_raw.md`(sha256: `0ed84df5...`)、無変更
- B1本文 source: `er003_output/b1_p1/A01/b1_article_raw.md`(sha256: `a5bdf3b8...`)、無変更
- 実行前後でsource sha256は一致(source変更0)

## 6. 次のステップ

この停止条件への対応方針(Preview本文の言語混在の扱いを変えるか、TTS instructionの見直しを別途正式に検討するか、等)は、ユーザーの判断が必要です。Claude Codeからは提案しません。

詳細な実行記録: [generation_stopped_status.json](generation_stopped_status.json)
