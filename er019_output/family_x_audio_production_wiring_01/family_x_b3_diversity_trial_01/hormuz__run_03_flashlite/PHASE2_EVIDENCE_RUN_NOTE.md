# Phase 2 evidence run note(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01)

このディレクトリは既存Production artifact(`hormuz__run_02`)を上書きしない
新規evidence run dirである。

## 再利用したもの(新規LLM/TTS呼び出しを避けるため、既存run_02からコピー)
- `b1b/parts.json`(記事本文の機械的split結果、LLM呼び出しではない)
- `b1b/b1_support_texts.json`(preview/comment_1-4の既存scaffold text)
- `b1b/key_phrases/keywords_canonicalized.json`(既存Key Phrase選定結果)
- `b1b/narration/kp{1-5}_en.wav`/`kp{1-5}_ja_charon.wav`(既存Key Phrase音声)
- `b1b/audit/tts_generation_results.json`は`key_phrases`セクションのみ
  投入した縮小キャッシュ(`segments`は空辞書)。これにより
  `_generate_or_reuse_kp`はKey Phrase 5件(英日計10ファイル)を新規TTS
  呼び出し無しで再利用し、`_generate_or_reuse`は主記事12segmentを
  必ず`generate_fn()`(=今回のtts_backend実行)で新規生成する。

## 新規に実際にAPI呼び出しを行った対象(本Phase 2の実測対象)
主記事12segment(topic_intro/preview/comment_1-4/full_story_part1-3
[+見出し2件]/in_one_line)を`tts_backend=speech_metadata_flash_lite`
(`gemini-3.8-flash-lite-tts`)で新規生成。

## 変更していないもの
`hormuz__run_02`配下のファイルは一切変更していない(読み取り専用コピー元)。
Master Audio Store・cost logger・telemetryへの書き込みは既存Production
経路どおり(共有storeへの通常記録、意図的な回避なし)。
