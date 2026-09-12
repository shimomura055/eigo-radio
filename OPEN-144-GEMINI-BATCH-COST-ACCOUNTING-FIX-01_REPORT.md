# OPEN-144-GEMINI-BATCH-COST-ACCOUNTING-FIX-01 — Report

管理ID: `OPEN-144-GEMINI-BATCH-COST-ACCOUNTING-FIX-01`
(+`TTS-DEV-PROD-MODE-SEPARATION-01`、+`TOWELS-B1B-TAKE5-LISTENING-CLIP-01`)。
実施者: Sonnet(sonnet-worker)。追加費用: TTS/ASR/LLM API呼び出しは一切
発生していない(¥0、既存ログの再集計とローカルffmpeg/faster-whisperのみ)。

## Part 1: OPEN-144 費用集計バグ是正

### バグ内容
`provider=="gemini"`のみを判定し、Gemini Batch API経由の記録
`provider=="gemini_batch"`を判定しないため、該当分が0円計上(または一部
scriptではKeyError/ValueErrorで未検出)になっていた。

### 修正した13ファイル(トリガー1本+同型12本)
1本のみ集計ロジックの共通moduleは存在せず(各scriptが独自に
`_call_cost_usd`/`call_cost_usd`/`price()`を実装)、13ファイル個別へ
`gemini_batch`分岐(pricing_snapshot.jsonのBatch tier、Standard比50%)を
追加した。生成経路・API呼び出しコードは一切変更していない。

| script | 既存出力への実影響(修正前→修正後) |
|---|---|
| `er011_discovery_generalization_towels_trial_11_audio_run.py`(トリガー) | audio ¥12.76→**¥62.83**(実行し`cost_summary_audio_01.json`を実際に更新、既存手動概算¥62.83と一致) |
| `er011_no18_evidence_compression_a_precision_21r_cost_compute.py` | grand_total ¥12.5→**¥27.8**(audio ¥2.7→¥18.0。9件のgemini_batch記録が実在し、実行して`cost_summary_21r.json`を実際に更新) |
| `er011_household_unified_final_candidate_01_run.py` | 差分なし(gemini_batch記録0件、実行確認済み) |
| `er011_news_stage3_new_theme_ledger_trial_09.py` | 差分なし(同上。旧コードは`rec.get("batch")`という存在しないフィールドを見ており、tier変数も未使用の別バグも併せて是正) |
| `er011_transcript_style_normalization_trial_01.py` | 差分なし(gemini_batch記録0件、実行確認済み) |
| `er011_open121_tts_repetition_general_qa_trial_01/02.py` | 差分なし(同上) |
| `er011_connected_speech_equivalence_layer_trial_01/02.py` | 差分なし(同上) |
| `er011_no18_cost_compute_01.py` | 差分なし(¥90.9のまま、gemini_batch記録0件) |
| `er005_stage7_cost_compute.py` | 差分なし(対象log全体でgemini_batch記録0件) |
| `er006_pool_benches_luna_cost_compare.py` | 差分なし(対象テーマにgemini_batch記録なし) |
| `er006_model_routing_contract_01_cost_recompute.py` | 差分算出不可(下記「既知の制約」参照。対象テーマにgemini_batch記録なし=影響なしは静的確認済み) |
| `er006_pool_pilot_01_cost_time_compute.py` | 同上 |

すべて`.venv/Scripts/python.exe`で実行し、修正前(git HEAD版)と修正後
(patch後)を同一の現行ログに対して比較。差分が出た2件(トリガー・
no18 21r)は実際に出力ファイルを更新し、他11件は数値不変を確認した
(不要な過去artifactの巻き戻し1件[`pool_benches_sol_vs_luna_cost.json`、
ログ増分によるstale artifact由来の見かけ上の差分]は`git checkout`で
復元済み)。

### 既知の制約(修正未実施ではなく実行不能)
`er006_model_routing_contract_01_cost_recompute.py`と
`er006_pool_pilot_01_cost_time_compute.py`は、対象ログ
(`er006_output/pool_pilot_01/raw_usage_log.jsonl`)に`stage: null`の
レコードが混在するため、**本修正前のgit HEAD版でも同一の
`AttributeError: 'NoneType' object has no attribute 'startswith'`で
クラッシュする**ことを確認した(本修正が原因ではない、既存の別の未修正
不具合)。実行はできないが、対象テーマ(`pool_benches`/`pool_subscriptions`/
`pool_startups`)にgemini_batch記録が無いことは静的grepで確認済みのため、
本バグによる金銭的影響は0円と判断できる。このクラッシュ自体の修正は
本タスクの範囲外として実施していない(別途ユーザー判断が必要なら報告)。

### 過去費用報告への影響範囲(2026-09-01以降)
- **Trial-11タオル音声**: `OPEN_ITEMS.md` OPEN-144行に既に反映済み
  (¥12.76→¥62.83、総額¥130.48→¥180.55)。
- **No.18 Evidence Compression 21r**(`cost_summary_21r.json`、
  grand_total ¥12.5→¥27.8): DECISION_LOG/OPEN_ITEMS/既存ER reportに
  この具体的な金額(¥12.5)を引用した記述は見つからなかった(grep確認)。
  narrative SSOTの訂正は不要、artifact自体を上記の通り更新した。
- 他11scriptは実影響¥0(記録なし)のため、過去報告の訂正は不要。
- 範囲外の追加発見(参考・未修正): `pool_pilot_01/raw_usage_log.jsonl`には
  本タスクの13scriptが対象としない`pool_n4_supermarket`/`pool_n5_cafes`/
  `pool_n6_delivery`テーマのgemini_batch記録222件が存在するが、これらの
  費用は`compute_topic_cost.py`/`final_cost_reconciliation.py`が
  ログ内の事前計算済み`cost_usd`フィールドを直接参照する別方式であり、
  OPEN-144のバグパターン(トークンからの再計算ミス)には該当しないことを
  コード確認した。追加調査は本タスクの範囲外(必要なら別途ユーザー判断)。

## Part 2: TTS Dev/Prod mode分離

`er006_batch_tts_wiring_01.py`の`DEFAULT_TTS_EXECUTION_MODE`(Production
既定、Batch)を変更せず、`er011_discovery_generalization_towels_trial_11_
audio_run.py`(Trial harness)側にのみ
`os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")`を追加した
(呼び出し元が既に指定していればそちらを優先)。offline確認済み
(API呼び出しなし、¥0): 本Trialモジュールimport後は
`resolve_tts_execution_mode()`が`STANDARD`を返し、Production moduleを
素で読み込んだ場合は引き続き`BATCH`を返すことを確認した。

他のer011 Trial scriptへの同様の適用は本タスクでは行っていない(スコープ外
への拡大と判断、必要であれば別途対象scriptを列挙してユーザー判断を仰ぐ)。

## Part 3: B1B take5 試聴clip

`full_story_part1`take5(resume#2)から該当clause
`"...or after the laundry has dried, and these stages can overlap."`を
ローカルfaster-whisper(`er008_disfluency_qa_18.transcribe_verbatim`、¥0)で
word-level timestamp特定(該当箇所11.24s〜16.90s、前後約1秒)、
`imageio_ffmpeg`同梱ffmpegでwav/mp3を切り出した。

生成物(絶対パス):
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\human_review\take5_has_dried_clip.wav`
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\human_review\take5_has_dried_clip.mp3`
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\human_review\take5_review_player.html`
  (file:///C:/Users/tensh/eigo-radio/er011_output/discovery_generalization_towels_trial_11/b1b/human_review/take5_review_player.html)

ページにはclip・take5全体・canonical文・両ASR書き起こし(Production ASR記録
+ローカルfaster-whisper再実行、いずれも"had dried")を掲載。判断入力欄は
含めていない。

## Production採用範囲

本タスクはコスト集計ロジックの修正・Trial実行モード既定値の分離・試聴用
clip作成のみ。生成経路・Prompt・Production runnerの挙動・
`er006_batch_tts_wiring_01.py`のProduction既定値はいずれも変更していない。
SSOT(`OPEN_ITEMS.md`等)の編集・Git操作(add/commit/push)は実施していない
(Fableによる統合待ち)。
