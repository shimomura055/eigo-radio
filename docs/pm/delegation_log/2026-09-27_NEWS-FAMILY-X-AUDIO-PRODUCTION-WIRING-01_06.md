# 委任文全文(NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01、Stage 3e後の診断、06)

管理ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01(Stage 3e後の診断、**read-only・¥0・API呼び出しなし・コード/SSOT編集なし**)。一時ファイル `docs/pm/ACTIVE_TASK_FXD1.md` / `docs/pm/RESULT_PACKET_FXD1.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_06.md` に保存(このファイルのみ後でcommit可、他は編集しない)。

## 事象
Stage 3e(REPORT `NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md` Stage 3e節、commit a8602a46)で、small_bag A2 `full_story_part2`/`full_story_part3`・small_bag B1B `full_story_part2` が、ブランド名("Khaite"→"Kite"/"Kate"、"minaudière"→"Minoudiere"等、"Altuzarra"→"Alta Zara")のASR不一致で retry予算を使い切りHUMAN_REVIEW_REQUIREDへ再Lock。本runは `ALLOW_PRONUNCIATION_WEB_LOOKUP=0`(cache-only)・逐次実行。

## 診断論点(承認済み仕様「未登録固有名詞は Detect→辞書/cache→resolver→trusted lookup→confidence→自動使用→store→TTS→validation→retry/fallback→Human Review最後」に照らす)
1. 各segment・各attemptで、EN resolver(`resolve_and_augment_en_style_prefix`)は発火したか、hits/hints_appliedは何か、Ledger(`er006_output/pronunciation_ledger_01/ledger.json`)に khaite/altuzarra/minaudière/elle 等のentryは存在するか(confidence・source・`tts_injection_disabled`)。cache-onlyが「lookupできず低confidenceのまま」の原因になっていたか(=web lookup有効なら救えた可能性)。artifact: `er019_output/.../small_bag__run_02/{a2,b1b}/audit/tts_generation_results.json`、raw_usage_log、review_lock_state、telemetry(`er025_output/pronunciation_resolution_core_telemetry_01/`)、`er021_output/.../telemetry.jsonl`。
2. ASR側: 既存のLedger Phrase List付きSecondary ASR cascade(OPEN-168の文脈、`er006_preprod_hardening_01_validation`/`er021_en_asr_semantic_equivalence_production_01`/cascade実装)は、このsegmentで Phrase List に brand名を渡して発火したか。TTS発話自体は正しかった可能性(ASRが綴れないだけ)を、ASR書き起こしと数値/否定/意味等価の判定ログから評価。
3. 上記に基づき「既存仕様のどの段が実装穴か/正常動作か」を分類: (A)実装穴(例: A2 fallback経路でresolver infoが落ちる=OPEN-203、Phrase Listが渡っていない、cache-only運用の副作用) / (B)正常動作(TTSは正しいがASR限界→Human Reviewが正しい最終非常口) / (C)新仕様が必要。**修正案は提案のみ**(実装しない)、各案の費用見積(再TTS回数)と必要なLock解除の有無。
4. small_bag B1B Key Phrase構造Gate(`KEY_WORDS_STRUCTURE_INVALID`、finite verb)について: 既存Strategy Lで再選定1回もNG。Family X用に承認済み(APPROVED_FOR_PRODUCTION、配線中)のDB Hybrid backend(`kp_backend="db_hybrid"`)で再選定した場合に構造Gateを通る見込み(Trial-03/04のsmall_bag B1Bはstructural PASSだった実績)を、既存artifact(`er028_output`/`er029_output` の small_bag_b1b 結果)から確認。

## 出力
`docs/pm/RESULT_PACKET_FXD1.md` に、segment×attemptの表(resolver発火/hits/Ledger状態/ASR書き起こし/判定理由)、分類A/B/C、推奨修正案(優先順・費用・Lock解除要否)、KP再選定の見込み。commitは delegation_log のみ(トレーラー `Management-ID: NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`、path指定add、他Agentのstageを外さない)。
