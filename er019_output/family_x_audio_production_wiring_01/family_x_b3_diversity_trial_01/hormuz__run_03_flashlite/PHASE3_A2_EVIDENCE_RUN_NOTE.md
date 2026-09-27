# Phase 3 A2 evidence run note(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01)

`a2/`ディレクトリはPhase 2で作成済みの`b1b/`と同じevidence run dir
(`hormuz__run_03_flashlite`)配下に追加した(既存Production artifact
`hormuz__run_02`は無変更)。

## 再利用したもの(新規LLM/TTS呼び出しを避けるため、既存run_02からコピー)
- `a2/parts.json`(記事本文の機械的split結果、LLM呼び出しではない)
- `a2/a2_support_texts.json`(preview/comment_1-4の既存scaffold text)
- `a2/key_phrases/keywords_canonicalized.json`(既存Key Phrase選定結果)
- `a2/narration/kp{1-5}_en.wav`/`meaning_{1-5}.wav`(既存Key Phrase音声、
  A2はKey Phrase Japanese meaningを`meaning_{i}.wav`という別命名で持つ)
- `a2/audit/tts_generation_results.json`は`key_phrases`セクションのみ
  投入した縮小キャッシュ(`segments`は空辞書、`path`フィールドは新run dir
  へ書き換え)。これにより`_generate_or_reuse_kp`はKey Phrase 5件(英/JA
  meaning計10ファイル)を新規TTS呼び出し無しで再利用し、`_generate_or_reuse`
  は主記事13segment(topic_intro/japanese_title/preview/comment_1-4/
  full_story_part1/in_one_line/full_story_part2[+見出し]/full_story_part3
  [+見出し])を必ず`generate_fn()`(=今回のtts_backend実行、6% slowdown
  post-process込み)で新規生成する。

## 新規に実際にAPI呼び出しを行った対象(本Phase 3の実測対象)
主記事13segment(EN 9件[topic_intro/full_story_part1/in_one_line/
full_story_part2/2_heading/3/3_heading]+JA 6件[japanese_title/preview/
comment_1-4])を`tts_backend=speech_metadata_flash_lite`
(`gemini-3.8-flash-lite-tts`)で新規生成。EN側`full_story_part1/2/3`+
`in_one_line`は既存A2 6% slowdown post-process
(`n3_tts.generate_a2_segment_with_slowdown`)をそのまま適用した
(backend非依存の既存実装、変更なし)。

## 変更していないもの
`hormuz__run_02`配下のファイルは一切変更していない(読み取り専用コピー元)。
Master Audio Store・cost logger・telemetryへの書き込みは既存Production
経路どおり(共有storeへの通常記録、意図的な回避なし)。
