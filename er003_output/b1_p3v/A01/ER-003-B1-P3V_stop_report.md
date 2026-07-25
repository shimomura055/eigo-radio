# ER-003-B1-P3V 停止レポート(Phase 1で停止)

## 1. 結論

Phase 1(TTS API機能確認)の結果、ネイティブBreak・SSML `<break>`・
Mark/Bookmark/Timepoint・TTS由来Timestamp/SDK offset metadataの
いずれも、現在使用中のGemini TTS(`gemini-2.5-pro-preview-tts`、
`google-genai` SDK経由の`generate_content`呼び出し)では利用できないと
確認した。指示section 6の分岐(「いずれも使えない：停止して報告」)に
従い、Phase 2A(Break方式)・Phase 2B(Mark/Timestamp方式)のいずれにも
進まず、ここで停止する。

**句読点・ASR・最長無音方式へは戻っていない**(指示section 6・16の
明記通り)。ER-003-B1-P3Uで実装した方式(Azure STTによるalignment)へも
戻さず、本ステージは新しいTTS呼び出しも既存音声の加工も一切行っていない。

## 2. 判定の根拠

推測ではなく、実装コード(`er002_gemini_client.py`)とインストール済み
`google-genai` SDK(2.11.0)の型定義を直接調べた。

| 項目 | 対応 | 根拠 |
|---|---|---|
| ネイティブBreak | 非対応 | `SpeechConfig`のフィールドは`language_code`/`multi_speaker_voice_config`/`voice_config`の3つのみ |
| SSML `<break>` | 非対応 | `contents`はSSMLをパースするAPIパラメータを持たないplain textのprompt |
| Mark / Bookmark / Timepoint | 非対応 | `SpeechConfig`にmark/bookmark/timepoint系フィールドが存在しない |
| TTS由来Timestamp / offset metadata | 非対応 | `Part`のフィールドにtimestamp/offset系のものが存在しない(`part_metadata`はSDK利用者側の汎用dictでありサーバーから自動的にタイミング情報が入るものではない) |

詳細: [`capability/tts_capability_report.md`](capability/tts_capability_report.md)、
[`capability/tts_capability_result.json`](capability/tts_capability_result.json)

## 3. 実行内容

| 項目 | 結果 |
|---|---|
| Phase 1(API機能確認) | 実施済み |
| Phase 2A(Break方式) | 未実施(未到達) |
| Phase 2B(Mark/Timestamp方式) | 未実施(未到達) |
| 新規TTS呼び出し | 0回 |
| 日本語raw音声生成 | なし |
| 英語Key Phrase音声(再利用予定分含む)への加工 | なし |
| 完成音声(raw/final) | 生成なし |
| Pattern A全文生成 | なし |
| B1本文生成 | なし |
| 原稿変更 | なし(`source/`配下に統合原稿・日本語原稿・英語Key Phraseをそのまま保存) |

## 4. テスト

新規追加分(`er003_b1_p3v_capability.py`のcapability判定ロジック)に
対するテストのみ実施。共有コード(`er002_common.py`/`er002_gemini_client.py`
/`er003_b1_p3t_audio.py`等)は変更していない。

- `er003_test_b1_p3v_capability.py`: 7件、全件PASS

大規模なテスト追加・project-wide regressionは行っていない。

## 5. 対象外(本ステージでは判定・実施していない)

音声の生成・語順・間・decode・clipping・Dynamics3適用は、Phase 1停止に
より該当する音声が存在しないため、本レポートでは判定していません。
