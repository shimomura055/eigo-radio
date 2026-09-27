# Phase 3 並列rate limit観測ノート(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01)

このディレクトリ(`hormuz__run_04_parallel_a`)は既存Production artifact
(`hormuz__run_02`)・Phase 2 evidence run(`hormuz__run_03_flashlite`/
`hormuz__run_03_baseline`)のいずれも上書きしない新規run dirである。

対になる並列プロセスは`family_x_b3_production_wiring_01__run_02_parallel_b`
(Meta記事、既存Production artifact`family_x_b3_production_wiring_01__run_01`
とは別run dir)。両プロセスを同時起動し、Production同時実行数=2相当での
429/backoff/latency増加の有無を観測する(`ALLOW_PRONUNCIATION_WEB_LOOKUP=0`
でcache-onlyにし、Pronunciation Ledgerへの新規書込みを避ける[OPEN-196])。

## 再利用したもの
- `b1b/parts.json`/`b1b/b1_support_texts.json`(既存scaffold text)
- `b1b/key_phrases/keywords_canonicalized.json`(既存Key Phrase選定結果)
- `b1b/narration/kp{1-5}_en.wav`/`kp{1-5}_ja_charon.wav`(既存Key Phrase音声)
- `b1b/audit/tts_generation_results.json`は`key_phrases`セクションのみの
  縮小キャッシュ(`segments`は空辞書、`path`は新run dirへ書換済み)

## 新規に実際にAPI呼び出しを行った対象
主記事12segment(Hormuz B1B)を`tts_backend=speech_metadata_flash_lite`で
新規生成(並列相手Metaと同時実行)。
