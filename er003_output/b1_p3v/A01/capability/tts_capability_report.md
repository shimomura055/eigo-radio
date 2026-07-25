# ER-003-B1-P3V Phase 1: TTS API機能確認レポート

推測ではなく、実装コード(`er002_gemini_client.py`)とインストール済み
`google-genai` SDKの型定義(実際のフィールド一覧)を直接調べた結果。

## 対象

- TTS model: `gemini-2.5-pro-preview-tts`
- SDK: `google-genai 2.11.0`
- request形式: `client.models.generate_content(model=common.MODEL_NAME, contents=<plain text prompt>, config=types.GenerateContentConfig(response_modalities=['AUDIO'], speech_config=types.SpeechConfig(language_code=..., voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=...)))))`
- response形式: `response.candidates[0].content.parts[*].inline_data.data (生PCMバイト列のみ。テキスト・タイムスタンプ・オフセット等は含まない)`

## 判定結果

| 優先順位 | 機能 | 対応 | 根拠 |
|---|---|---|---|
| 1 | ネイティブBreak | 非対応 | `SpeechConfig`のフィールドは `['language_code', 'multi_speaker_voice_config', 'voice_config']` のみで、break/pause/silence/mark系の専用フィールドは存在しない |
| 2 | SSML `<break>` | 非対応 | contentsはSSMLをパースするAPIパラメータを持たないplain textのpromptであり、<break>等のタグを埋め込んでもマークアップとして解釈される機構が存在しない(過去のER-003-B1-P3Rで、この方式のGemini TTSに日英混在テキストを渡した際、テキストとして誤読され400エラーになった実績があり、任意のタグ埋め込みが安全に無視・解釈される保証もない)。 |
| 3 | Mark / Bookmark / Timepoint | 非対応 | `SpeechConfig`にmark/bookmark/timepoint系フィールドが存在しない |
| 4 | TTS由来Timestamp / SDK offset metadata | 非対応 | `Part`のフィールドは `['code_execution_result', 'executable_code', 'file_data', 'function_call', 'function_response', 'inline_data', 'media_resolution', 'part_metadata', 'text', 'thought', 'thought_signature', 'tool_call', 'tool_response', 'video_metadata']` で、timestamp/offset系フィールドが存在しない。Part.part_metadataはSDK利用者側が任意の値を設定できる汎用dictフィールドであり、Gemini TTSのレスポンスとして音声タイミング情報が自動的に格納される仕組みではない(公式説明: 'Custom metadata associated with the Part')。 |

## 採用方式と根拠

上記4項目のいずれも利用できないと判定した。この環境のGemini TTS(`gemini-2.5-pro-preview-tts`、`google-genai`経由の`generate_content`呼び出し)は、plain textのpromptを渡して生PCMバイト列のみを受け取るインターフェースであり、SSML等のマークアップ解釈、Mark/Bookmark/Timepointの指定、生成結果に対する文字・単語レベルのタイムスタンプやaudio offsetメタデータの返却、のいずれにも対応していない。

指示section 6の分岐(「いずれも使えない：停止して報告」)に従い、Phase 2A/Phase 2Bへは進まず、ここで停止する。句読点・ASR・最長無音方式へは戻らない(指示section 6・16の明記通り)。
