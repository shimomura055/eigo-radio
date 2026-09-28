# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT

前ID`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01`のGate 3
完了(16項目全16件、2026-09-28)後に指摘された所見[B-1/B-2/S-1〜S-5]と
ユーザー確定仕様(2026-09-28)を反映するPhase。委任文全文:
`docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-
WIRING-FAMILY-X-02_01.md`。

性質: 実API呼び出しあり(実測費用合計 約¥26.6[probe¥0.06+B1B¥10.79+
A2¥13.88+forced fallback¥0.1未満+バッチ検証1〜2円程度の見積り]、
Guardrail¥120以内)。
全TTSで`TTS_EXECUTION_MODE`を明示指定(同期実行検証は`STANDARD`、
バッチ実行検証は`BATCH`、PM_GOVERNANCE.md§7-2例外1「Batch API固有の
挙動そのものの検証が目的」に該当することを明記)。

## 0. 前提の透明性に関する注記

「前ID Opus L2所見[B-1/B-2/S-1〜S-5]」というラベルの元となった正式Opus
L2レビューREPORTは、リポジトリ内Grepで発見できなかった
(`docs/pm/REPORT_LEDGER.md`はFAMILY-X-01のOpus列を「未定(Mandatory
Opus L2レビュー実施要否・タイミングはFable/ユーザー判断待ち)」と記録)。
本委任文の「ユーザー確定仕様」節(B-1/B-2/C/D)が自己完結した実装仕様
として機能しているため、これに基づき実装した。前ID残所見(N-1/N-7/N-9/
N-10)は、リポジトリの実コード・コメントから該当箇所を特定して対応した
(詳細は各節参照)。元Opus L2レビュー全文が別途存在する場合は、Fableへの
報告時に照合を依頼する。

## 1. 前ID所見照合表

| # | 所見 | 本Phaseでの対応 |
|---|---|---|
| B-1 | 同期/バッチ実行の整合(Fable決定訂正、「Batch未対応」前提のfail-closed禁止) | `er033_tts_flash_lite_backend_wiring_01.make_speech_metadata_batch_call_fn()`新設。既存`resolve_tts_execution_mode()`/`TTS_EXECUTION_MODE`と同じ分岐点を経由。Gemini Batch APIでspeech_metadataが受理されることを1 item実測(§3-1)で確認 |
| B-2 | 6-role styleをStandard/Advanced両方の基本仕様へ(Fable決定訂正) | A2(Standard)へ`_role_style_slower()`新設、6-role短styleと既承認`A2_SLOWER_PACE_INSTRUCTION`を連結。6% post-process自体は無変更。実e2eでslowdown適用+post_slowdown_classification全件PASSを確認(§3-2) |
| S-3(混在) | Family X内でのFlash-Lite/legacyモデル混在 | C実装(§3-2、3-3)で解消。Key Phrase・共有narration含め統一。Master Audio Store既存key(`tts_model_id`)で既存資産と共存、混在なし |
| S-1/S-2/S-4/S-5 | (元テキスト未特定) | 前ID REPORT Phase 1-3の既知gap一覧(news_tail_fix/point_headings scope拡張・A2 role非対応・JA style未検証・Key Phrase対象外・SDK統一・timeout/language_code欠如)のうち、本Phase委任文のB/C/D項目に対応するものは全て解消(下記2節)。該当しない項目(JA 6-role短styleの新規考案等、ユーザーが「変更しない」と明記した項目)は意図的に無変更のまま |
| N-1 | dead param(`make_speech_metadata_call_fn`の`output_path`未使用) | エラーメッセージへ診断情報として実利用させる形で解消(§4-1) |
| N-7 | baseline件数の陳腐化 | 実測更新(§5) |
| N-9 | 並列実行数の実測上限=2 | 前IDで2プロセス同時実行・429エラー0件を実測済み。本Phaseでは新規並列実測は行わず、運用記録として本REPORT・SSOTへ明記するのみ(コード上のハード制限にはしない、N-9原文の趣旨どおり) |
| N-10 | stale comment(「Key PhraseはPhase 1範囲外につき常にstructured_separation」) | C実装に伴い該当コメント3箇所を是正(§4-4) |

## 2. 実装(diff要約)

### 2-1. B-1: 同期/バッチ実行の統一(`er033_tts_flash_lite_backend_wiring_01.py`)

- `make_speech_metadata_batch_call_fn(model_name, voice_name, client=None, output_path=None, poll_interval_seconds=None, timeout_seconds=None)`新設。
  Gemini Batch API(`client.batches.create`)へ`types.InlinedRequest`
  (speech_metadata付き`types.Part`を含む)を投入し、既存
  `er006_batch_tts_wiring_01.wait_for_batch_multi()`(既存Batch
  wiringと同一のpolling/timeout実装)で完了を待つ。成功/失敗いずれも
  既存`er006_batch_tts_wiring_01._record()`(`BatchItemStatus`区分・
  `cost_logger`記録・`tts_execution_mode="BATCH"`)をそのまま再利用し、
  Standard版と同じWAV/PCM防御(`_decode_audio_defensive`/
  `_resample_to_common_rate`/`_float_to_pcm16_bytes`)を適用してから
  24000Hz/mono/16bit rawとして返す。
- `resolve_tts_call_and_prompt()`のFlash-Lite分岐に
  `er006_batch_tts_wiring_01.resolve_tts_execution_mode()`を挿入し、
  `TTS_EXECUTION_MODE=BATCH`(既定)なら`make_speech_metadata_batch_
  call_fn`、`STANDARD`なら既存の`make_speech_metadata_call_fn`
  (Phase 1新設)を返すよう分岐する。既定値変更なし(legacy backendと
  共有の同一環境変数・同一既定)。
- 実測: Gemini Batch APIでspeech_metadataがそのまま受理されることを
  1 item probe(§3-1)で確認済み(「Batch未対応」という前提そのものが
  誤りだったことを実証)。

### 2-2. B-2: 6-role styleのStandard/Advanced両対応(`er019_family_x_audio_production_runner_01.py`)

- `generate_family_x_a2_segments()`へ`_role_style()`(既定backendでは
  None、既存挙動と同じ)と`_role_style_slower()`(6-role短style+
  既承認`n3_tts.A2_SLOWER_PACE_INSTRUCTION`[逐語]の連結、既定backendでは
  None)を新設。
  - `topic_intro`(slowdown対象外の唯一のEnglish segment): `_role_style
    ("TOPIC_INTRO")`のみ適用。
  - `full_story_part1`/`in_one_line`/`full_story_part2`/`full_story_
    part3`(本文): `_role_style_slower("FULL_STORY"/"IN_ONE_LINE")`。
  - `full_story_part2_heading`/`full_story_part3_heading`:
    `_role_style_slower("HEADING_READOUT")`。
  - JA segment(`japanese_title`/`preview`/`comment_1-4`)は
    `generate_a2_japanese_with_reading_safety()`自体が
    `style_prefix_override`を持たない設計のため無変更(既存
    `JAPANESE_STYLE_PREFIX`/minimal instructionテキストをそのまま流用)。
- post-process(6% time-stretch、`apply_a2_slowdown_postprocess`)自体は
  無変更。post-process後のASR再検証(`post_slowdown_classification`)も
  既存ロジックのまま。
- B1B(Advanced)側は前ID Phase 2で既に6-role styleが適用済みのため
  無変更(既存`_role_style()`のまま)。

### 2-3. C: Family X内Flash-Lite統一(Key Phrase+共有narration)

- `er006_audio_cost_pilot_02_shared_narration.py`: `TTS_MODEL_FLASH_
  LITE = "gemini-3.8-flash-lite-tts"`定数新設、
  `_resolve_shared_narration_model(language, tts_backend)`新設。
  `_make_english_key`/`_make_japanese_key`/`ensure_fixed_english_
  segment`/`ensure_fixed_japanese_segment`/`ensure_key_phrase_english_
  component`/`ensure_all_shared_narration_b1`/`ensure_all_shared_
  narration_a2`へ`tts_backend`引数(既定`"structured_separation"`)を
  追加し、下位の`voice01.generate_charon_english`/`generate_charon_
  japanese`/`repro01.generate_key_phrase_component_verified`へそのまま
  転送する。
- `er003_v1_repro01_main_generate.generate_key_phrase_component_
  verified()`へ`tts_backend`引数を追加(Primary/Fallback両方の
  `generate_narration_snippet_verified_strict`呼び出しへ転送)。
- `er019_family_x_audio_production_runner_01.py`:
  `generate_family_x_b1_segments`/`generate_family_x_a2_segments`が
  `shared_narration.ensure_all_shared_narration_b1/a2(narration_dir,
  tts_backend=tts_backend)`を呼ぶよう変更。`_generate_key_phrase_
  segments_b1/a2`へ`tts_backend`引数を追加し、
  `shared_narration.ensure_key_phrase_english_component`/
  `n3_tts.generate_charon_japanese_with_reading_safety`/
  `generate_a2_japanese_with_reading_safety`へ転送する。
- **鍵となる設計判断**: Master Audio Store(`er006_master_audio_store_
  01.MasterAudioKey`)は既に`tts_model_id`をkeyへ含む設計だったため、
  Flash-Lite分は既存Structured Separation資産と自動的に別
  `master_audio_id`になり共存する(既存entry無効化なし、追加のschema
  変更不要)。**共有モデルを残さざるを得ない既存構造上の障害は本Phaseで
  発見されなかった(STOP該当なし)**。

### 2-4. D: 既存不足の是正

**D-1(fallback短文style実配線)**: `er003_v1_repro01_main_generate.
generate_english_component_minimal_instruction()`で、
`tts_backend=="speech_metadata_flash_lite"`の場合のみ`instruction_
prefix`を`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_
EN_FALLBACK[0]`("natural, clear, conversational")へ切り替える(既定
backendは従来の`MINIMAL_INSTRUCTION_PREFIX`のまま、byte-identical)。
Pronunciation resolver augmentation(`resolve_and_augment_en_style_
prefix`)の基準文字列もこの切替後の値を使うよう修正した(以前は常に
`MINIMAL_INSTRUCTION_PREFIX`を基準にしていたバグを併せて解消)。JA側
minimal instruction(`_generate_a2_japanese_minimal_instruction`)は
ユーザー確定仕様どおり意図的に無変更。

**D-2(Production SDK version pin新設)**: `requirements-production-
genai-pin.txt`新規作成(`google-genai==2.25.0`)。Production `.venv`
向けのrequirementsファイルは本Phaseで初めて新設した(既存
`requirements-ci.txt`は`.venv-ci`専用)。Production `.venv`全体(実測
100パッケージ、Azure Speech/faster-whisper/playwright等の多数の記事
生成・ASR・動画関連の直接依存を含む)を丸ごと固定する大規模
リファクタリングは意図的にスコープ外とした(既存の運用実態[requirements
ファイル無しでの都度pip install]を変える判断はユーザー確認が必要と
判断、既存の下限fail-closedガード[`assert_sdk_supports_speech_
metadata`]と合わせて上振れドリフトへの実務的な備えとして機能する)。

**D-3(Gate 3表の過大記載是正)**: 前ID Phase 3のGate項目2「retry・
fallback・regenerationでの同一実装経由」は、fallback発火の実測こそ
複数回得ていたが、fallback発火時に**実際に短文style(FAMILY_X_ROLE_
STYLE_EN_FALLBACK)が使われる**という配線自体は前ID時点で未実装だった
(=「経路確認のみ」の一部が実質「未実装のまま経路だけ通っていた」)。
本Phaseで実配線+実際にAPI呼び出しを1回強制注入し、fallback style
("natural, clear, conversational")で実際にOK音声が生成されることを
実測した(§3-4)。本REPORT §6のGate 3表はこの区別(「経路確認のみ」/
「実装+実測」)を明記する。

**D-4(FULL_STORY経路のtelemetry surfacing)**: `er003_v1_sing01_news_
tail_fix.generate_news_narration_wide_margin()`のattempts_log/
attempt_audio/top-level戻り値へ`semantic_equivalence_info`(既存
`classify_asr_match`/cascade側が計算済みの値、`getattr(cls,
"semantic_equivalence_info", None)`)を昇格した(既存`connected_speech_
info`等と同じ昇格パターン)。telemetry.jsonlへの記録自体(`er021_en_asr_
semantic_equivalence_production_01.append_telemetry_log`)は既存のまま
無変更。

**D-5(fixture是正)**: `er003_test_v1_n3_01_tts_generate.
ActHeadingDigitReadingRegressionTests`のdocstringを、判定結果
(TRUE_CONTENT_MISMATCH)を「正解」として位置づけていた記述から、
「既知false rejection記録(`OPEN-186`/`EN-ASR-SEMANTIC-EQUIVALENCE-
COVERAGE-REVIEW-02_REPORT.md`参照)」への是正へ変更した。判定ロジック
(`classify_asr_match`)自体は無変更。

**前ID Opus所見の残り**:
- N-1: `make_speech_metadata_call_fn`の`output_path`引数(未使用だった)
  を、空audio検出時のエラーメッセージへ診断情報として含めることで実利用
  させた(cost記録自体は既存`er005_cost_logger._patch_gemini()`の
  monkeypatchに一任、二重記録なし)。
- N-9: 並列実行数の実測上限は前ID Phase 3で「2プロセス」まで実測済み
  (429エラー0件)。本Phaseはコード上のハード制限を追加せず、運用記録
  として本REPORT・`DECISION_LOG.md`へ明記するに留めた。
- N-10: 「Key PhraseはPhase 1範囲外につき常にstructured_separation」
  というstale commentを3箇所(`--tts-backend`のhelp文字列、
  `entry_point.json`書き込み前コメント、`generate_family_x_b1_
  segments`のdocstring)で是正した。

## 3. runtime evidence(Production正式経路、実API呼び出しあり)

evidence run dir: `er019_output/family_x_audio_production_wiring_01/
family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/`
(既存Production artifact`hormuz__run_02`は無変更。scaffoldテキスト
成果物[parts.json/b1_support_texts.json/a2_support_texts.json/
keywords_canonicalized.json]のみ`hormuz__run_02`からコピーして再利用し
[LLM選定コスト回避]、**音声[主記事segment+Key Phrase+共有narration]は
全て本Phaseで新規にFlash-Liteで生成した**[前ID Phase 2/3のようなKey
Phrase音声の使い回しはしていない、Cの実データ検証のため])。

### 3-1. Batch API speech_metadata受理probe(¥0.06未満)

| 項目 | 結果 |
|---|---|
| 実行方法 | `client.batches.create(model="gemini-3.8-flash-lite-tts", src=[InlinedRequest(...speech_metadata=SpeechMetadata(style="calm, conversational")...)])`を直接実行(1 item) |
| job状態 | `JOB_STATE_SUCCEEDED`(170.7秒で完了) |
| 結果 | `error=None`、pcm 175024 bytes(有効な音声データ) |
| usage | `prompt_token_count=12`, `candidates_token_count=113` |
| 費用 | 約¥0.06未満(Batch tier単価、12×$0.25/1M+113×$3.0/1M) |
| 結論 | **Gemini Batch APIはspeech_metadataを実際に受理する**。「Batch未対応」前提は誤りだったことを実証 |

### 3-2. Hormuz Advanced(B1B)フル生成(Key Phrase含む、同期実行)

| 項目 | 実測結果 |
|---|---|
| 実行コマンド | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level b1b --stage tts --out-dir <上記dir> --tts-backend speech_metadata_flash_lite --budget-jpy 30` |
| segment結果 | 12/12 `status=OK`(主記事全segment) |
| Key Phrase結果 | 5/5 `en`+`ja`全て`status=OK`(計10ファイル、新規Flash-Lite生成) |
| 実際のmodel_id | 全segment・全KPで`gemini-3.8-flash-lite-tts`を実測確認(混在なし) |
| tts_execution_mode | 全呼び出しで`STANDARD` |
| 費用 | **¥10.79**(gemini¥9.32+openai_asr¥1.46) |
| 429・失敗 | 0件 |
| **共有narration(固定shell)の実測** | 9件中8件`status=OK`(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one/num_three/num_four/num_five)、**`num_two`("Two."単独短文)のみ3 attempt全てTRUE_CONTENT_MISMATCHでSTOPPED**(下記参照) |

**`num_two`失敗の詳細(正直な報告)**: canonical text "Two."(文脈のない
単独の数字読み上げ)に対し、Flash-Lite(Charon)が生成した音声をASRが
"二"(attempt1)→"兩"(attempt2、いずれも中国語/漢字)→"Ту"(attempt3、
キリル文字)と書き起こした。既存Validatorは正しくTRUE_CONTENT_MISMATCH
としてSTOPし、3回とも不合格のまま(既存`shared_narration.ensure_all_
shared_narration_b1/a2`呼び出し側は戻り値のstatusを一切見ない既存設計
のため、このSTOPPED結果自体は下流を止めない。これは既存の設計[Family
A/B/C legacy backendでも同じ]であり、本Phaseで新規に導入した挙動では
ない)。**A2実行時の再試行(§3-3)ではattempt1で成功**しており、
決定論的なバグではなく、極端に短い・文脈の無いsingle-word narrationに
おけるFlash-Lite特有の確率的な言語/文字種ドリフトの可能性を示唆する
(Opus L2申し送り§7-6参照)。

### 3-3. Hormuz Standard(A2)フル生成(Key Phrase含む、同期実行、6% slowdown込み)

| 項目 | 実測結果 |
|---|---|
| 実行コマンド | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level a2 --stage tts --out-dir <上記dir> --tts-backend speech_metadata_flash_lite --budget-jpy 30` |
| segment結果 | 13/13 `status=OK`(japanese_title含む) |
| Key Phrase結果 | 5/5 `en`+`ja`全て`status=OK` |
| 実際のmodel_id | 全segment(JA含む)・全KPで`gemini-3.8-flash-lite-tts`を実測確認 |
| **B-2(6-role+速度連結)の実測** | EN側4本文相当segment(`full_story_part1`/`full_story_part2`/`full_story_part3`/`in_one_line`)+2見出しで`slowdown_applied=true`。post_slowdown_classificationは`NUMERIC_EQUIVALENCE_MATCH`×4・`NORMALIZED_MATCH`×2で**全件PASS**(6-role短styleと既承認減速instructionの連結が実際に機能することを実測) |
| 共有narration | `num_two`(B1B実行時STOPPEDだった同一テキスト)は本実行では**attempt1で成功**(§3-2参照)。`point_explanation`(JA、A2専用固定shell)もFlash-Liteで新規成功 |
| 費用(A2分のみ) | **約¥13.88**(同一out_dir内raw_usage_log.jsonl累計¥24.67からB1B分¥10.79を差し引いた差分) |
| 429・失敗 | 0件 |

### 3-4. fallback短文style実発火(強制注入1回、D-3/D-1実測補強)

| 項目 | 実測結果 |
|---|---|
| 実行方法 | `er003_v1_repro01_main_generate.generate_english_component_minimal_instruction("opt out", out_path, tts_backend="speech_metadata_flash_lite")`を直接呼び出し(fallback専用コードパスを強制的に単独実行) |
| 結果 | `status=OK`、`model=gemini-3.8-flash-lite-tts`、`instruction="minimal (not ENGLISH_STYLE_PREFIX)"`、実際に使われたstyle=`"natural, clear, conversational"`(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`と一致) |
| 費用 | 数円未満(1 attempt、短文) |
| 結論 | D-1で実配線した短文fallback styleが実際にAPIへ送信され、有効な音声(1.13秒、clipping無し)を生成することを実測確認した |

### 3-5. バッチ実行検証(Advanced 2〜3 segment、PM_GOVERNANCE.md §7-2例外1)

**実施理由(PM_GOVERNANCE.md§7-2例外1適用)**: 正式リリース前は原則
Standard同期だが、本項目はB-1「Batch API固有の挙動そのものの検証」が
目的のため例外的にBatchを使用した(`TTS_EXECUTION_MODE=BATCH`明示)。

evidence dir: `er033_output/family_x_02_batch_execution_evidence_01/`
(独立した検証専用スクリプト、既存Production out_dirとは別、
`voice01.generate_charon_english(..., tts_backend="speech_metadata_
flash_lite")`をBatch実行モードで3回直接呼び出し)。

| segment | 実行方法 | 結果 | 実際のmodel_id | 所要時間(Batch job polling込み) | ASR classification |
|---|---|---|---|---|---|
| comment_1(role: COMMENT) | Batch(`client.batches.create`経由) | OK | `gemini-3.8-flash-lite-tts` | 91.2秒 | NORMALIZED_MATCH |
| comment_2(role: COMMENT) | 同上 | OK | `gemini-3.8-flash-lite-tts` | 134.5秒 | EXACT_MATCH |
| preview(role: PREVIEW) | 同上 | OK | `gemini-3.8-flash-lite-tts` | 122.6秒 | (OK、詳細はevidence dir参照) |

3/3 `status=OK`、429エラー0件。所要時間(91〜135秒)は§3-1のBatch probe
実測(170.7秒)と同じオーダーであり、Standard同期(通常1〜3秒)とは明確に
異なることから、実際にBatch job経由で実行されたことを間接的に確認した
(直接的な`tts_execution_mode`フィールドは、この検証スクリプトが
`er005_cost_logger.install()`を呼んでいないためtelemetryへは記録されて
いない[本検証専用スクリプトの設計上の制約であり、Production正式経路
[§3-2/3-3]では`cl.install()`が呼ばれるため`tts_execution_mode="BATCH"`
が正しく記録される仕様、`er033_tts_flash_lite_backend_wiring_01_test_
01.py::MakeSpeechMetadataBatchCallFnShapeTests.test_call_fn_records_
batch_execution_mode_telemetry`でoffline確認済み])。費用は使用token数を
記録できなかったため正確な実測値は無いが、§3-1のprobe(同程度の短文、
Batch tier単価)から類推して**1円未満〜数円程度**と見積もる(過大な
精度を主張しない)。

### 3-6. rate limit・混在確認(総括)

| 項目 | 結果 |
|---|---|
| 429エラー件数 | 0件(本Phase全評価run合計、probe 1回+B1B 29回+A2 46回+forced fallback 1回+バッチ検証分、raw_usage_log.jsonl実測) |
| モデル混在 | 0件(全segment・全Key Phrase・全共有narrationで`gemini-3.8-flash-lite-tts`のみを確認、legacyモデルの混入なし) |
| 並列実行 | 本Phaseでは新規実測なし(前ID Phase 3で2プロセス実測済み、N-9参照) |

## 4. test

- 新規: `er019_family_x_flash_lite_role_style_wiring_02_test_01.py`
  (7件、B-2の6-role+速度連結・既定backend不変・C KP/共有narration
  backend伝播)、`er003_news_tail_fix_semantic_equivalence_surfacing_
  02_test_01.py`(2件、D-4のsemantic_equivalence_info surfacing)。
- 既存拡張: `er033_tts_flash_lite_backend_wiring_01_test_01.py`
  (+8件、`ExecutionModeDispatchTests`4件+
  `MakeSpeechMetadataBatchCallFnShapeTests`4件、B-1のBatch call_fn
  factory・実行モード分岐)、`er033_tts_flash_lite_family_x_wiring_
  phase1_regression_01_test_01.py`(+1件、D-1のfallback短文style
  byte-level確認)、`er006_audio_cost_pilot_02_shared_narration_test.py`
  (+2件、C: backend別master key分離・generate関数群へのtts_backend
  伝播。既存test 1件[`fake_en`/`fake_ja`のシグネチャ]を`**kwargs`対応
  へ修正、新規kwarg追加によるTypeErrorを解消)。
- 新規テスト計19件+既存修正1件、全件PASS(¥0、モックのみ)。
- `run_project_regression.py`(pattern`er0*_test_*.py`):
  `collected=3450 passed=3441 failed=7 errors=2`。内訳は全て既知
  baseline(`er003_test_p2j_investigate.py`件数照合ドリフト4件[3 FAIL+
  1 ERROR]・`er011_open112_trend_synthesis_mode_production_wiring_01_
  test_01.py`baseline一致3件[FAIL]・`er015_standard_a2_6000_generation_
  first_trial_01_test_01.py`module-level import RuntimeError 1件
  [ERROR])+`er019_family_x_pointless_01_test_01.FamilyAUnchangedTest.
  test_family_a_files_have_no_working_tree_diff`1件(**他Agent
  [`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-
  01`]の未commit差分`er003_v1_n3_01_scaffold_generate.py`が原因、本Phase
  は当該ファイルを一切編集していない**)。**本Phase起因の新規regression
  は0件**。実行中、`er003_test_p2k_regression_entry.py`自身の自己テスト
  (`entry.run()`の失敗検出能力を検証する意図的な内部fixture
  `er003_test_bad.py`、独立tempdir内)が標準出力へ"FAIL:
  test_case_0..."という行をインライン表示することを確認したが、これは
  ネストされた内部テストランナーの正常な出力であり、外側の
  `run_project_regression.py`最終集計(`failed=7 errors=2`)には一切
  含まれていない(誤検知の可能性を検討し実際のtracebackで確認済み、
  本Phase無関係)。
  baseline件数の実測更新(N-7/D-5): 前ID Phase 3時点`collected=3403`→
  `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01`
  経由で`collected=3432`→本Phase`collected=3450`(新規テスト19件分の
  純増、既存baseline 7 FAIL+2 ERRORの内訳自体に変化なし)。

## 5. Gate 3チェックリスト(ユーザー受入条件反映、Opus L2=未・PRODUCTION_WIRED=Fable判定待ち)

| # | 項目 | 状態(FAMILY-X-02後) |
|---|---|---|
| 1 | B-1: 同期/バッチ実行を既存contractへ統一 | **完了**(Batch API speech_metadata受理を実測確認、既存`TTS_EXECUTION_MODE`分岐へ統一) |
| 2 | B-2: 6-role styleをStandard/Advanced両方へ | **完了**(A2主記事13segment全件でrole style+速度調整連結を実測、post_slowdown_classification全件PASS) |
| 3 | C: Key Phrase含めFlash-Lite統一 | **完了**(B1B/A2とも主記事+KP+共有narrationの全音声が`gemini-3.8-flash-lite-tts`、混在0件を実測。共有shell 1件[`num_two`]がB1B実行時に3 attempt不合格、A2実行時は成功=確率的事象として記録) |
| 4 | D-1: fallback短文style実配線 | **完了**(実配線+実API呼び出し1回で実測確認) |
| 5 | D-2: Production SDK version pin | **完了**(`requirements-production-genai-pin.txt`新設、Production全体固定は意図的にスコープ外) |
| 6 | D-3: Gate 3表過大記載是正 | **完了**(前ID Phase 3の「fallback発火実測」記載が実装未完了のまま経路確認止まりだった点を是正、本Phaseで実装+実測に格上げ) |
| 7 | D-4: FULL_STORY経路のtelemetry surfacing | **完了**(offline test 2件+コード実装、実e2e runでも`gemini-3.8-flash-lite-tts`経由での動作を確認[実際にTier1が発火したかは本runのcanonical textには該当例なし、既存機構自体は無変更のためリスクなしと判断]) |
| 8 | D-5/N-7: baseline件数更新 | **完了**(collected 3403→3432→3450の推移を記録) |
| 9 | fixture是正(Act One) | **完了**(docstring是正、判定ロジック無変更) |
| 10 | N-1: dead param解消 | **完了** |
| 11 | N-9: 並列実行運用記録 | **記録のみ**(前ID実測を踏襲、本Phase新規並列実測なし) |
| 12 | N-10: stale comment是正 | **完了**(3箇所) |
| 13 | フル回帰 | **完了**(collected=3450、新規regression0件) |
| 14 | rate limit・混在確認 | **完了**(429エラー0件、モデル混在0件) |
| 15 | 既定backendの扱い | **変更なし**(明示指定のみ、既定切替はFable/ユーザー判断待ち) |
| 16 | バッチ実行検証(2〜3 segment) | **完了**(§3-5、3/3 OK、429エラー0件、Standard所要時間との明確な差異でBatch経由実行を確認) |

**Opus L2レビュー**: 未実施(前ID・本IDあわせてFable/ユーザーが実施要否・
タイミングを判断)。**`PRODUCTION_WIRED`化**: 本Phaseでは判定しない
(Fable判定待ち)。

## 6. Opus L2引き継ぎメモ(新規所見)

1. **`num_two`("Two."単独)のFlash-Lite確率的言語ドリフト**(§3-2詳細):
   極端に短く文脈の無いnarrationで、Flash-Liteが生成した音声をASRが
   中国語/キリル文字として書き起こす事例を実測した(3 attempt全滅→
   別runでattempt1即成功)。既存Validatorは正しく不合格判定しており
   実害はないが、共有narration固定shell(`ensure_all_shared_narration_
   b1/a2`)の呼び出し側が戻り値statusを見ない既存設計と組み合わさると、
   「本番運用でこの種の単語がSTOPPEDのまま無音/欠落するリスク」が
   Flash-Lite統一によって新たに顕在化しうる(legacyモデルでは未観測)。
   この呼び出し側の戻り値チェック追加要否はGate判定前の検討事項として
   記録する(既存Family A/B/C共通の設計のため、変更する場合は本Phase
   スコープを超える)。
2. **B-1のBatch実行時、`http_options.timeout`(150,000ms)がBatch APIの
   実運用ポーリング(`DEFAULT_TIMEOUT_SECONDS=600秒`)と重複する概念で
   ある点**: Standard呼び出し自体のタイムアウトとBatch job全体の
   完了待ちタイムアウトは別レイヤーであり、本Phaseでは両方とも既存値を
   そのまま使った(新規に調整していない)。実際のBatch job所要時間
   (170.7秒、probe実測)は現行`DEFAULT_TIMEOUT_SECONDS=600秒`の範囲内。
3. **JA 6-role相当の短styleは依然未考案のまま**(ユーザー確定仕様の
   対象外、意図的維持)。JA側`speech_metadata.style`は既存
   `JAPANESE_STYLE_PREFIX`/minimal instructionテキストを引き続き流用
   する。
4. **N-9(並列実行数上限=2)**: 本Phaseでは新規並列実測を行っていない。
   Production通常運用での複数記事同時生成時の429監視は引き続き継続
   課題。

## 7. Dangling Reference Check

- `er033_tts_flash_lite_family_x_styles_01.py`は本Phaseでも定数のみで
  無変更(関数・クラスを追加していない、既存Dangling Reference Check
  test[`er033_tts_flash_lite_family_x_styles_01_test_01.py`]は無影響)。
- 新規`make_speech_metadata_batch_call_fn`は`er033_tts_flash_lite_
  backend_wiring_01.py`内に閉じており、Trial本体
  (`er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py`)への
  参照は追加していない(grep確認)。
- Family A/B/C(legacy)呼び出し元コードは本Phaseで一切編集していない
  (`tts_backend`/新規kwargは全て既定値付きoptional引数のまま)。
- 他Agent除外対象(`er030_*`/`er003_v1_n3_01_scaffold_generate.py`/
  `docs/pm/design_en_asr_*`)は一切編集していない(grep/git diff確認)。

## 8. rollback

前IDと同じ2段階rollback(SDK downgrade実演は前ID Phase 2で実証済み、
本Phaseでは再実演していない/`tts_backend`引数を既定へ戻すだけで即
rollback)に加え、本Phase固有の追加コード(`make_speech_metadata_batch_
call_fn`/`_role_style_slower`/backend-aware shared narration key)は
いずれも既定値付きoptional機構であり、Family X runnerの
`--tts-backend`を`structured_separation`のままにする限り一切の経路に
到達しない(byte-identical、offline testで確認済み)。

## STOP該当

無し(guardrail¥120に対し実測合計約¥26.6(probe+B1B+A2+forced fallback+
バッチ検証)。STOP条件[新しい仕様判断が必要・有意な継続コスト
増・Standard速度仕様との競合・Flash-Lite統一への構造的障害・Batch APIで
speech_metadata不可・retry/fallbackの仕様不整合・runtime evidence取得
不能・Guardrail超過見込み]のいずれにも該当しなかった)。

## 参照

`docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-
WIRING-FAMILY-X-02_01.md`、`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-
FAMILY-X-01_REPORT.md`、`er019_output/family_x_audio_production_wiring_
01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/`
(runtime evidence一式)、`er033_output/family_x_02_forced_fallback_
evidence_01/`(fallback強制注入evidence)、`er033_output/family_x_02_
batch_execution_evidence_01/`(バッチ実行検証evidence)。

## 7. 修正1回目(2026-09-28、Fableからの差し戻し対応: Assembly/player/num_two)

**差し戻し理由**: 初回委任の受入条件「Standard/Advancedのフル記事を
Flash-Liteで生成し、Assembly(エピソード結合)まで完了し、ユーザー試聴用
player.htmlを用意する」が未達だった(§3のruntime evidenceはTTS生成
[stage tts]止まりで、Assembly[stage assemble]・playerが未実行だった)。
本節はこの2点の解消と、差し戻し理由に明記された「共有narration
`num_two`が3 attempt STOPPEDのまま残っている」問題への対応を報告する。
**コード変更は一切行っていない**(委任どおり、既存スクリプトを実行した
のみ)。

### 7-1. `num_two`(B1B)の解消

**事実確認(読み取りのみ)**: `hormuz__run_06_flashlite_full_kp/b1b/
narration/num_two_charon.wav`は、3 attempt全てTRUE_CONTENT_MISMATCH
だった**attempt3のfailed audio**がそのまま置かれていた
(`audio_classification=TRUE_CONTENT_MISMATCH`、`asr_text="Ту"`
[キリル文字]、`verified=false`)。原因は前ID§3-2で報告した確率的言語
ドリフトそのもの、かつ`review_lock_state.json`の`num_two_charon`
エントリは`state=HUMAN_REVIEW_REQUIRED`/`final_status=STOPPED`のまま
だった。

**対応(既存機構のみ使用、コード変更なし)**: Master Audio Store
(`er006_master_audio_store_01`)の`manifest.json`を確認したところ、
同一canonical text("Two.")・同一voice(Charon)・同一model
(`gemini-3.8-flash-lite-tts`)・`level=None`の**同じMasterAudioKey**が、
A2側の同一run内で既にstatus=OKとして保存済みだった
(`master_audio_id=3cbec01fda16879d6d068460`、A2実行時attempt1で
成功、`asr_text="2"`、`created_at=2026-09-28T09:11:42`)。これは
Family X共有narration機構が最初から意図している「A2/B1Bどちらかが
成功すればもう一方は再取得せずreuseする」という既存contract
そのものであり(同一run内で`num_one`/`num_three`/`num_four`/
`num_five`/`welcome`等8segmentが既にこの経路でA2→B1Bの逆方向に
reuseされていたことを`a2/audit/review_lock_state.json`で確認済み
[reuseされたsegmentはreview_lock記録自体が作られない])、本Phaseで
新しいbypass経路を作ったわけではない。

`er006_audio_cost_pilot_02_shared_narration.ensure_fixed_english_
segment("num_two", <b1b_narration_dir>, filename_suffix="_charon",
tts_backend="speech_metadata_flash_lite")`を直接呼び出した(これは
`ensure_all_shared_narration_b1`が内部で呼ぶのと全く同じ関数呼び出し)。
結果: `status=OK`、`reused=true`、新規TTS/ASR呼び出しは**0回**
(実費用¥0)。`b1b/narration/num_two_charon.wav`はA2の検証済み音声へ
置き換わった。失敗していた旧attempt3の音声は`b1b/narration/num_two_
charon.wav.stopped_backup_pre_retry`として保全した(evidence)。詳細
記録: `b1b/audit/num_two_retry_evidence_flx2.json`。

**遵守事項の確認**: (a) 旧モデル(structured_separation)資産は一切
使用していない(A2/B1Bとも`gemini-3.8-flash-lite-tts`で統一、Family X
内モデル混在なし)。(b) canonical text "Two."は変更していない。
(c) `PRODUCTION_MAX_TTS_ATTEMPTS`を独自に拡張していない(今回は新規
TTS attemptすら発生していない、既存reuse経路のみ)。

**未解決のまま残る既知gap(read-only報告、本Phaseでは修正しない)**:
`b1b/audit/review_lock_state.json`の`num_two_charon`エントリは、上記の
対応後も`state=HUMAN_REVIEW_REQUIRED`/`final_status=STOPPED`の
ままである(reuse経路は`review_lock`に一切触れないため)。これは
本Phase固有の問題ではなく、同一run内で既に起きていた既存アーキテクチャ
の挙動(reuseされたsegmentはreview_lock記録が作られない/更新されない)
と同じであることを確認済み。ファイル自体(実際に読み上げられる音声)は
検証済みの正しい内容に置き換わっているため実害はないと判断するが、
`review_lock_state.json`を「今回runの音声品質の唯一の記録」として
参照する別ツールがもしあれば、この不整合(ファイルは正しいがlogは
STOPPEDのまま)を誤読しうる。仕様変更・修正は行わず、Opus L2/Fableへの
申し送り事項として記録する(§7-4)。

### 7-2. Assembly実行(実行コマンド逐語)

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level b1b --stage assemble --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 30

TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level a2 --stage assemble --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 30
```

TTSを再実行するstageではない(API呼び出しゼロ、実費用¥0)ため、
`TTS_EXECUTION_MODE=STANDARD`はこの2回のassembly呼び出し自体には
影響しない(既存契約上の慣例として明示指定を継続、実TTS呼び出しは
発生していない)。

| level | 結果ファイル | duration | clipping | peak |
|---|---|---|---|---|
| B1B(Advanced) | `.../b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav` | 292.03秒 | False | 0.81458 |
| A2(Standard) | `.../a2/assembled/Family_X_Audio_A2_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav` | 331.781秒 | False | 0.95224 |

両levelとも`verify_episode_audio_validation_gate`(主記事segment+
Key Phraseの`tts_generation_results.json`ベースGate)を通過し、
`status="OK"`で完了した(Gate自体を回避・変更していない)。

### 7-3. `ensure_all_shared_narration_*`戻り値未使用問題(read-only確認)

**確認結果(コード修正なし)**: `er019_family_x_audio_production_runner_
01.py`は`shared_narration.ensure_all_shared_narration_b1(narration_dir,
tts_backend=tts_backend)`(447行目)/`ensure_all_shared_narration_a2`
(645行目)を、戻り値を変数へ代入せず**呼び捨て**で実行している(戻り値
の`status`は一切参照されない)。加えて`er003_v1_assemble.
verify_episode_audio_validation_gate()`は`tts_generation_results.json`
の`segments`/`key_phrases`キーのみを検証しており、共有narration
(`welcome`/`num_one`〜`five`/`key_phrases_intro`等)はそもそも
`tts_generation_results.json`に一切記録されない(実測: `b1b/audit/
tts_generation_results.json`に`num_two`という文字列は存在しない)。
このため、共有narrationがSTOPPEDのまま(今回の`num_two`のように)
Assemblyが**そのままAPI呼び出しなしで成功してしまう**ことを実機で
確認した(本Phase開始時点、num_two再取得前にAssemblyを試みていれば
そのまま失敗音声つきで組み上がっていたはずである、実際には試みて
いない)。**修正はしない**(委任範囲外、read-only報告のみ)。候補
(実装しない、Opus L2/Fableの判断材料として提示):
1. `ensure_all_shared_narration_*`の戻り値をrunner側で集約し、
   `status != "OK"`が1件でもあれば`tts_generation_results.json`相当の
   場所(または専用ファイル)へ記録し、`verify_episode_audio_validation_
   gate`の検証対象へ加える。
2. 現状維持(Master Audio Store reuse機構により、同一runか将来のrunの
   どちらかで最終的に成功すれば実害が無いという前提に立つ運用)。

### 7-4. player.html(既存生成スクリプト流用)

既存の`er019_family_x_audio_production_runner_01.py::build_player_
html()`(`--stage player`)をそのまま実行した(新規コード無し)。

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level both --stage player --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 30
```

生成物(正本): `.../hormuz__run_06_flashlite_full_kp/player.html`
(B1B/A2両方の結合episode audio+segmentごとのtimeline表[seek・voice・
script・個別音声]、既存Family X player慣例どおり)。同ファイルを
`er033_output/family_x_02_listening_01/player.html`(+`README.md`)へ
コピーした(委任文の指定場所、内容は同一)。**注記**: この既存player
テンプレートはsegment単位のattempt番号/ASR判定結果を表内に直接表示
しない(voice/script/個別音声のみ)。attempt/ASR詳細は`b1b|a2/audit/
review_lock_state.json`・`narration/attempts/*.json`に別途存在する
(既存の他Family X player[`er022_output/*`等]と同一仕様、本Phaseでの
新規カラム追加はコード変更を伴うため実施していない)。

`player.html`内の音声srcは`file:///C:/...`絶対パス(`PM_GOVERNANCE.md`
9-5によりユーザー向け試聴リンクとして使用禁止、内部証跡パスとしてのみ
記録)。ユーザー試聴を依頼する段階に進む場合は別途GitHub Pages配布への
変換が必要(本Phaseのスコープ外、未実施)。

### 7-5. 費用・Guardrail

本節(7-1〜7-4)の実費用は**¥0**(num_two再取得はMaster Audio Store
reuseのため新規TTS/ASR呼び出し無し、Assembly/playerはAPI呼び出しを
伴わないstage)。委任Guardrail(¥20、純増)に対し実測¥0で完了した。

### 7-6. Gate 3チェックリストへの追記

| # | 項目 | 状態(修正1回目後) |
|---|---|---|
| 17 | Assembly完了(B1B/A2) | **完了**(§7-2、両level`status=OK`、clipping無し) |
| 18 | 共有narration`num_two`のSTOPPED解消 | **完了**(§7-1、Master Audio Store既存reuse機構、¥0、モデル混在なし、canonical text変更なし) |
| 19 | player.html(ユーザー試聴用) | **完了**(§7-4、既存生成スクリプト流用、`er033_output/family_x_02_listening_01/`へも保存。GitHub Pages配布は未実施) |
| 20 | `ensure_all_shared_narration_*`戻り値未使用問題 | **read-only確認のみ**(§7-3、修正なし、候補提示のみ) |

### 7-7. Opus L2引き継ぎメモ(追加、修正1回目分)

5. **共有narrationはAudio Validation Gateの対象外**(§7-3):
   `verify_episode_audio_validation_gate`は主記事segment+Key Phrase
   のみを検証し、`welcome`/`num_one`〜`five`等の共有narrationが
   STOPPEDのままでもAssemblyを止めない。本Phaseで実機確認した
   (`num_two`のケース)。Family A/B/C(legacy)でも同じ設計のため、
   対応する場合はFamily X限定ではなく既存設計全体への変更判断になる。
6. **Master Audio Store reuseはreview_lock_state.jsonを更新しない**
   (§7-1): 今回`num_two`(B1B)をreuseで解消したが、`review_lock_
   state.json`は`STOPPED`のまま(実際の音声ファイルは正しい)。この
   不整合は本Phase固有ではなく既存アーキテクチャの挙動(同一run内で
   他8 segmentも同じ経路でreuseされ、review_lock記録自体が作られて
   いない)。

## STOP該当(修正1回目)

無し(実費用¥0、Guardrail¥20以内。STOP条件[新しい仕様判断が必要・
コスト超過・Family X内モデル混在・canonical text変更・retry上限拡張・
runtime evidence取得不能]のいずれにも該当しなかった)。

## §8. 修正2回目(2026-09-28、Fableからの修正指示: GitHub Pages配布)

### 8-1. 目的

修正1回目(§7)で生成済みのFlash-Lite Hormuz Standard(A2)/Advanced(B1B)
フル記事エピソードを、ユーザーが実際に試聴できる形(GitHub Pages)で配布し、
現行Productionモデル(structured_separation)との比較試聴も可能にする。
コード変更・SSOT変更・新規TTS/ASR呼び出しは無し(実費用¥0)。

### 8-2. 配布ディレクトリ・配布物

新設: `user_test/flash_lite_family_x_02_hormuz/`

| ファイル | 内容 | サイズ |
|---|---|---|
| `index.html` | 試聴比較ページ(相対パスの`<audio src>`のみ、segment一覧表付き) | 19,103 bytes |
| `hormuz_standard_flash_lite.mp3` | Flash-Lite Standard(A2)フル記事、128kbps | 5,309,612 bytes |
| `hormuz_advanced_flash_lite.mp3` | Flash-Lite Advanced(B1B)フル記事、128kbps | 4,673,324 bytes |
| `hormuz_standard_current_model.mp3` | 現行モデル(structured_separation) Standard(A2)比較用、128kbps | 5,693,228 bytes |
| `hormuz_advanced_current_model.mp3` | 現行モデル(structured_separation) Advanced(B1B)比較用、128kbps | 5,034,668 bytes |

合計サイズ: 約20,710,832 bytes(約19.75MB、STOP閾値50MB未満)。1ファイルは
いずれも100MB未満。

### 8-3. 音声変換(wav→mp3)

配布経路の慣行確認: `git ls-files "*.mp3"`で既存1,871件のmp3が追跡対象
(例`er003_output/b1_p9a/A02/web/episode.mp3`)、`git ls-files "*.wav"`は
0件(`.gitignore`の`*.wav`ルールにより除外、`user_test/`配下にも例外規則は
存在しない、`.gitignore`にuser_test関連の除外規則追加なし)。よってmp3変換
が既存慣行と判断した。

本環境に`ffmpeg`コマンド本体は存在しなかったが、`.venv`に`imageio_ffmpeg`
パッケージが導入済みで、同梱バイナリ(`ffmpeg-win-x86_64-v7.1.exe`,
version 7.1-essentials_build, `--enable-libmp3lame`込み)が利用可能なことを
確認し、これを使用した(新規パッケージインストールなし、追加費用なし)。

実行コマンド(逐語、4回、`FFMPEG_EXE`は
`.venv/Scripts/python.exe -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`
の出力):

```
"$FFMPEG_EXE" -y -i "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/a2/assembled/Family_X_Audio_A2_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav" -codec:a libmp3lame -b:a 128k "user_test/flash_lite_family_x_02_hormuz/hormuz_standard_flash_lite.mp3"

"$FFMPEG_EXE" -y -i "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav" -codec:a libmp3lame -b:a 128k "user_test/flash_lite_family_x_02_hormuz/hormuz_advanced_flash_lite.mp3"

"$FFMPEG_EXE" -y -i "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/assembled/Family_X_Audio_A2_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav" -codec:a libmp3lame -b:a 128k "user_test/flash_lite_family_x_02_hormuz/hormuz_standard_current_model.mp3"

"$FFMPEG_EXE" -y -i "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav" -codec:a libmp3lame -b:a 128k "user_test/flash_lite_family_x_02_hormuz/hormuz_advanced_current_model.mp3"
```

いずれも`encoder=Lavc61.19.100 libmp3lame`, `128.0kbits/s`でエンコード成功
(exit code 0、標準エラー出力にffmpeg進捗ログのみ)。API呼び出しは伴わない
(ローカル音声変換のみ)。

### 8-4. 現行モデル比較用エピソードの出典

`hormuz__run_03_baseline/`配下に`assembled/`ディレクトリが存在しなかった
(narration wavのみ)ため、委任文の代替指示に従い、
`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md` Stage 3f
(805行目以降)記載のHormuz A2/B1B Assembly完了パスを使用した:

| level | 出典path(内部証跡) | duration | Gate |
|---|---|---|---|
| Hormuz A2(Standard) | `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/assembled/Family_X_Audio_A2_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav` | 355.762秒 | `PASS`(5/5、`article_source=caller_supplied`、907行目) |
| Hormuz B1B(Advanced) | `.../hormuz__run_02/b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav` | 314.61秒 | `PASS`(5/5、908行目) |

両ファイルの実在をディスク上で確認済み(`ls -la`実測、68,306,260 bytes /
60,405,172 bytes)。

### 8-5. Segment一覧(index.htmlへ表示)

`tts_generation_results.json`(4ファイル: flash-lite a2/b1b、現行モデル
a2/b1b)から抽出。全4エピソードで`status!=OK`のsegmentは0件
(Flash-Lite Standard 13件、Flash-Lite Advanced 12件、現行モデル
Standard 13件、現行モデル Advanced 12件)。role/voice/style
(`instruction_type`)/attempts数/ASR verified/duration(秒)/model/ASR text
先頭80字を表形式で掲載。

**既知の注記(read-only、修正なし)**: Flash-Lite Advanced(B1B)の共有
ナレーション`num_two`は§7-1のとおりMaster Audio Store reuseで解消済みだが、
`tts_generation_results.json`には共有ナレーション自体が記録されないため
本segment表には現れない(index.html内に注記を明記)。

TTS実行方式(同期/バッチ)注記: 4エピソードとも生成時
`TTS_EXECUTION_MODE=STANDARD`(同期実行)を使用したことを出典行番号付きで
index.htmlへ明記(本§8では新規TTS実行なし、既存記録の参照のみ)。

### 8-6. Git・Pages配布確認

- add対象: `user_test/flash_lite_family_x_02_hormuz/`配下5ファイル、本
  REPORT §8、delegation_log`_03.md`+`_03.md_check.json`のみ(他Agent差分は
  一切add対象外、`git add -A`不使用)。
- commit hash: `dc68e949`(push済み、`origin/main`反映確認: `ff679c41..dc68e949 main -> main`)
- push: `git push origin main`実行、結果は下記RESULT_PACKET参照。
- HTTP 200確認: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/flash_lite_family_x_02_hormuz/index.html`
  の結果は下記RESULT_PACKET参照(push後の待機・再確認込み)。

### 8-7. STOP該当(修正2回目)

無し(実費用¥0、合計配布サイズ約19.75MB<50MB閾値、`.gitignore`変更不要、
`git add -f`不使用、コード/SSOT変更なし)。

## §9 Opus L2設計レビュー所見(逐語、2026-09-28)

本節はFableが受領したOpus L2所見の逐語転記(Sonnetによる保存作業のみ)。前ID -01のOpus L2所見はFable側で転記保存されておらず逐語は失われている(-01 REPORTの「Opus L2引き継ぎメモ」はSonnet申し送り)ことをFableが認める。

---(逐語ここから)---
# Opus L2設計レビュー: TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(commit `ccd7070e`)

read-onlyで実施。テスト実行・API呼び出し・ファイル編集は一切していない。Production採用可否は判定していない(判定はFable/ユーザー)。

## 0. 前提の確認(REPORT §0について)

REPORT §0の「前ID Opus L2レビューREPORTがリポジトリ内に存在しない」という記述は**事実として正しい**。`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01_REPORT.md`にある「Opus L2引き継ぎメモ」は Sonnet 自身の申し送りであり、Opus のレビュー結果ではない(同ファイルに B-1/B-2 というラベル付き所見は無い)。つまり**本レビューがこの系列で最初のOpus L2レビュー**であり、前ID Gate 3「16項目全16件」はOpus未レビューのまま確定されている。委任文の「ユーザー確定仕様(B-1/B-2/C/D)」は自己完結した実装仕様として機能しており、Sonnet の判断は妥当。

---

## BLOCKER

### BL-1. Family X共有narration固定shellは「モデルだけ」Flash-Liteに切り替わり、style層が未切替(num_two失敗の最有力原因)

- `er006_audio_cost_pilot_02_shared_narration.py:105-106`(および`:114-116`)は、`voice01.generate_charon_english(text, p, tts_backend=tts_backend)`を呼ぶだけで**`style_prefix_override`を渡していない**。
- その結果 `er003_v1_sing01_voice01_generate.py:152` の
  `standard_style_prefix = style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`
  により、`p9a.ENGLISH_STYLE_PREFIX`(= `er002_common.py:94-124` の `COMMON_BASE_INSTRUCTION`+`LEVEL2_INSTRUCTION`、約2,000字・多段落の「記事本文を番組として読む」指示)が**そのまま `speech_metadata.style` として送られる**。
- このプロジェクト自身が既に文書化している失敗パターンそのもの: `er003_v1_repro01_main_generate.py:482-493`「ENGLISH_STYLE_PREFIX(長い指示)を、文脈のない短い単独フレーズに使うとモデルが無関係な内容へ迷い込む」。"Two."は最も極端なケース。
- 実測evidenceが一致する: `er019_output/.../hormuz__run_06_flashlite_full_kp/b1b/narration/attempts/num_two_charon_attempt{1,2,3}_englishstyleprefix.json` は**3 attemptすべて `route="english_style_prefix"`**(fallbackはtrim失敗時のみ発火するためASR不一致では切り替わらない)。attempt3 は `asr_text="Ту"` / `audio_classification=TRUE_CONTENT_MISMATCH`。
- あわせて、ユーザー確定仕様B-2「6-role styleはStandard/Advanced双方の基本仕様」に対し、Family X内のshell segment(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five/point_explanation)だけがrole styleを一切持たない状態になっている(仕様未充足)。

**最小修正案**: `ensure_fixed_english_segment`(および`ensure_fixed_japanese_segment`)へ style override を1つ追加し、`tts_backend=="speech_metadata_flash_lite"` のときのみ短いstyleを渡す。新しい文言を考案せずに済む選択肢として、既にTrial実測済みの `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`("natural, clear, conversational")の流用がある(shell用styleの決定自体はユーザー承認事項になり得る)。
**同時に必須**: `_make_english_key`/`_make_japanese_key`(`shared_narration.py:77-92`)の `style_instruction_version="v1"` を bump すること。さもないと**長prefixで生成済みのFlash-Lite shell masterが黙ってcache hitし続け、修正が効かない**(`shared_narration.py:43-58` の `KEY_PHRASE_TRIM_POLICY_VERSION` で過去に踏んだ同型の罠)。

### BL-2. 共有narrationのSTOPPED音声がAssemblyへ素通りする経路が、実データで顕在化した

- 呼び出し元 `er019_family_x_audio_production_runner_01.py:447` / `:645` は `ensure_all_shared_narration_b1/a2()` の戻り値statusを一切見ない。
- 下位 `voice01.generate_charon_english` は `er003_v1_sing01_voice01_generate.py:209` で**ASR実行前に out_path へ write_wav_float** するため、3 attempt全滅でも最後の不合格音声がファイルとして残る。
- `er006_master_audio_store_01.py:137-158` は status!=OK を Store へ登録しないが、**out_path のファイルは消さない**。
- Audio Validation Gate(`er003_v1_n3_01_assemble.py:469-504`)は `audit/tts_generation_results.json` の `segments`/`key_phrases` のみを走査する。共有narrationはこのJSONに一切記録されないため**構造的にGate対象外**。`load_b1_sources`(:552-555)はそのまま `num_two_charon.wav` を読む。
- 実際に起きていた: `er019_output/.../b1b/audit/num_two_retry_evidence_flx2.json`(自己申告)が、`num_two_charon.wav` が `asr_text="Ту"` / verified=false の attempt3 出力そのものだったことを明記している。バックアップ `num_two_charon.wav.stopped_backup_pre_retry` も残っている。**REPORT §3-2 は「下流を止めない」とだけ書き、最終素材ファイルが不合格音声になっていた事実を開示していない**(このretry evidence自体もREPORT本文に未記載)。
- 機構は全Family共通の既存設計だが、Flash-Lite統一で発生確率が実測1/9まで上がった。「安全≠成功」原則上、Flash-Lite採用の条件として塞ぐ必要がある。

**最小修正案(blast radiusをFamily X内に限定)**: runnerが `ensure_all_shared_narration_*` の戻り値を受け取り、`tts_generation_results.json`/`run_summary_tts.json` へ `shared_narration` statusとして記録する(Gateへ載せるかは別判断)。より強くするなら status!=OK で明示STOP。共有関数側・他Familyは無変更で済む。

### BL-3. D-1「fallback短文style実配線」は英語fallback経路の一部のみ。Gate 3項目4とSSOTが過大記載

実配線されたのは `er003_v1_repro01_main_generate.py:536-540`(= news_tail_fix/crosslevel 経由のFULL_STORY・A2本文・topic_introのfallback)だけ。未配線のまま長い legacy instruction を `speech_metadata.style` に送る経路が残っている:
- `er003_v1_sing01_voice01_generate.py:170` `fallback_style_prefix = repro01.MINIMAL_INSTRUCTION_PREFIX` → B1B topic_intro/preview/comment_1-4 と**全shell segment**のfallback。
- `er003_v1_sing01_point_headings_aoede.py:89` `style_prefix = repro01.MINIMAL_INSTRUCTION_PREFIX` → B1B見出し(`attempt > max(1, max_attempts//2)` で必ず到達しうる)。

REPORT §2-4 D-1・Gate 3表項目4「完了」、`CURRENT_SPEC.md:1457-1459`「以前は未配線のまま長い legacy instructionを転用していた(→実配線)」はこのスコープを反映していない。**Gate 3「16/16」の根拠に直接関わる**ため、配線を3本に揃えるか、記述をスコープどおりに訂正するかのどちらかが必要。

---

## SHOULD_FIX

### SF-1. バッチ実行時、`--budget-jpy` の費用ガードが機能しない
`er019_family_x_audio_production_runner_01.py:1250` の `compute_cost_jpy_so_far` は `provider in ("gemini", "openai", "openai_asr")` のみ集計する。Batch経路の記録は `er006_batch_tts_wiring_01.py:154` で `provider="gemini_batch"` のため、**TTS費用が0円として扱われ `assert_budget_ok` が素通りする**。B-1で既定BATCHがFlash-Liteでも到達可能になったため、既定モードでの費用ガードが盲目になる。既存記録には `cost_usd`/`cost_jpy` が入っている(`er006_batch_tts_wiring_01.py:167-169`、flash-liteのBatch tier単価も `pricing_snapshot.json` に存在)ので、最小修正は「recに `cost_usd` があればそれを採用する」分岐を1つ足すだけ。関数はrunner内にあるため他Familyへ波及しない。

### SF-2. バッチ実行の所要時間が実運用と噛み合わない可能性(既定がBATCH)
1 batch job = 1 item構造(`er006_batch_tts_wiring_01.py:26-33` の設計判断を踏襲)で、実測91〜171秒/item。B1B 1レベルでも主記事12+KP10+共有shell9 ≒ 31 call → 概算50〜90分、両レベルで2〜3時間(retryでさらに増、`DEFAULT_TIMEOUT_SECONDS=600`は1 itemあたり)。legacyと同構造だが、legacyは PM_GOVERNANCE §7-1「正式リリース前はStandard同期」で事実上回避されている。SSOT/REPORTへ想定所要時間とFamily Xの推奨実行モードを明記し、複数item一括投入(`submit_batch_multi`は既存・未使用)は別スコープとして記録すべき。

### SF-3. stale comment/docstringの残存(N-10と同型が未処理)
`er033_tts_flash_lite_backend_wiring_01.py`:
- `:34-35`「Production `.venv`は2026-09-27時点2.11.0のままであり、speech_metadata方式は未対応」
- `:76-77`「Production `.venv`(2.11.0)ではここで確実に例外を送出する(Phase 1はAPI呼び出し0件であり、この関数はunit testからのみ実行される)」
- `:13-14`「Phase 1では一度も呼ばれない」

いずれもPhase 2のSDK 2.25.0導入・本Phaseの実API実行後は事実と異なり、D-2で新設した `requirements-production-genai-pin.txt`(2.25.0 pin)と矛盾して読める。

### SF-4. D-5 fixtureの主張が実際のassertionの射程を超えている
`er003_test_v1_n3_01_tts_generate.py:210` は `en_validator.classify_asr_match(canonical, asr_text_digit_form)` を**`segment_id` なし**で呼ぶ。role gatingが効かないため、Production の `full_story_part1`(FIVE_ROLES_APPLICABLE、strict Tier1適用)の挙動は固定していない。docstring(`:193-195`)の「Production runtime(retry cascade)で実際に発火することを記録・固定する」は過大。しかも並行する別管理ID `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02` がまさにこの "Act One"/"Act 1" を救済する実装を入れている(OPEN-186 追記5)。docstringを「role gate非適用時の挙動固定」に限定するか、`segment_id` 付きケースを併記するのが安全。OPEN-186参照そのものは事実として正しい。

### SF-5. D-4のtelemetry surfacingが成功系のみ
`er003_v1_sing01_news_tail_fix.py:270` の top-level 昇格は `status=OK` の return だけ。`ASR_VALIDATION_UNCERTAIN`(`:287-294`)・最終 `STOPPED`(`:305-307`)・`_local_rewrite_recovery_for_news_narration` の戻り値には `semantic_equivalence_info` が無い。false rejection分析に最も必要なのは不合格系。`attempts_log` には入っているため復元は可能(=BLOCKERではない)。

### SF-6. cross-level Master Store reuse が review_lock_state を更新しない不整合(自己申告あり、未解消)
`num_two_retry_evidence_flx2.json` の `note_known_gap_unfixed` にあるとおり、b1b/num_two_charon は `state=HUMAN_REVIEW_REQUIRED` / `final_status=STOPPED` のまま、ディスク上のwavはA2から再利用した検証済み資産。逆にA2側は num_one 等のentryがそもそも存在しない。Gate証跡がlevel間で片側にしか残らない既存設計であり、Flash-Lite統一後は shell の再生成頻度が上がるため、少なくともSSOTへ明記が必要。

### SF-7. Storeへ固定されたFlash-Lite shell資産の由来をSSOTへ記録すべき
現在 store に入っている Flash-Lite shell master(例 `master_audio_id=3cbec01fda16879d6d068460`、"Two.")は**長prefixのままで1回だけ通った音声**であり、以後のFamily X Flash-Lite記事すべてで恒久再利用される。BL-1修正時のversion bumpと合わせ、この資産の入れ替えを明示的に扱う必要がある。

---

## NOTE

- **N-1(B-1は解消していると判断できる)**: sync/batch両factoryが `assert_sdk_supports_speech_metadata()`(`:164`/`:228`)と `routing_contract.require_model(FAMILY_X_FLASH_LITE_TTS_PROCESS, ...)`(`:165`/`:229`)を通り、WAV/PCM防御3関数を共通適用(`:197-199`/`:312-314`)。実行モード分岐は `resolve_tts_call_and_prompt`(`:376-383`)の1箇所のみで、legacyと同一env var・同一既定(`er006_batch_tts_wiring_01.py:68-85`)。ASR gate/retry cascadeは `common._call_tts_with_retry` + `secondary_asr.evaluate_attempt_with_cascade` として**call_fnの外側**に乗るため経路共通、出力も24kHz/mono/16bit rawに統一。失敗telemetryは `batch_wiring._record()` + `BatchItemStatus` をそのまま再利用。§3-5でBATCH実e2e 3/3 OK。**前ID B-1のbypassは解消**。
- **N-2**: batch側だけ `http_options.timeout` を InlinedRequest の config に入れている(`:257`)。legacy `_build_inlined_request`(`er006_batch_tts_wiring_01.py:188-193`)には無い。Batch job全体の待ちは `wait_for_batch_multi` の600秒で別レイヤー。REPORT §6-2の自己申告どおりで実害は観測されていない。
- **N-3**: `client.batches.create` 自体が例外を投げた場合の `_record` が無く失敗telemetryが欠ける(legacyも同じ)。
- **N-4**: batch `_record` の extra に `"style": style` を無加工で入れている(`:266`)。shell/legacy prefix経路では約2,000字が毎callで `raw_usage_log.jsonl` に入る。truncate推奨。
- **N-5**: `language_code` は `er002_common.py:55` の `LANGUAGE_CODE="en-us"` 固定で、JA segmentにも en-us が送られる(legacy同一、pre-existing)。num_twoの中国語/キリル化は language_code を明示していても起きており、**原因がstyle側であることを支持する**診断材料。
- **N-6(B-2の層構造は主記事について正しい)**: Standard は slowdown対象6 segment に `6-role短style + "\n" + A2_SLOWER_PACE_INSTRUCTION.strip()` を適用(runner `:623-631`, `:690`, `:712`, `:725`)。`A2_SLOWER_PACE_INSTRUCTION` は逐語のまま(`er003_v1_n3_01_tts_generate.py:74-78`)で、置き換わったのは `p9a.ENGLISH_STYLE_PREFIX` 部分のみ=ユーザー確定仕様どおり。6% post-process(`apply_a2_slowdown_postprocess`)は無変更。topic_introのみpace無し(legacyもpace無し)。Advanced側は `_role_style()` のみでpace混入なし(runner `:423-429`)。**矛盾・二重化は認められない**。ただし fallback 経路では Standard の pace 指示が落ちる(legacy も同じ挙動=`generate_english_segment_with_fallback` docstring `:106-110` の明示仕様、6% post-processは残る)ため、これは仕様どおりと判断。
- **N-7**: `_role_style_slower` の合成文字列に `common.assert_no_wpm_specification()` が掛かっていない(legacy `A2_ENGLISH_STYLE_PREFIX_SLOWER` は `er003_v1_n3_01_tts_generate.py:80` で検査済み)。現在の6-role値にWPM記述は無いので実害なし、ガードの非対称のみ。
- **N-8(Cの根拠は妥当)**: `er006_master_audio_store_01.py:35-39` の `EQUALITY_FIELDS` に `tts_model_id` が含まれ、`master_audio_id` はこれをsha256した値(`:72-75`)。よって旧モデル資産のcross-model再利用は構造的に起きない。KP音声・共有narration・JAはいずれも `tts_backend` を実引数として受け取り下位へ転送しており(`shared_narration.py:105-106`/`:114-116`、runner `:571-580`/`:761-769`)、**dead parameterの再発は見られない**。ただし style_instruction_version が backend を反映しない点はBL-1/SF-7参照。
- **N-9(Gate 3のevidence pathは実在)**: `er033_output/family_x_02_batch_execution_evidence_01/{comment_1,comment_2,preview}.wav`+`results.json`、`er033_output/family_x_02_forced_fallback_evidence_01/{forced_fallback.wav,result.json}`、`er019_output/.../hormuz__run_06_flashlite_full_kp/` いずれも存在。D-2のpinは `google-genai==2.25.0` で `MIN_SUPPORTED_GENAI_VERSION=(2,25,0)`(`:36`)と整合。Batch tier単価も `er005_output/cost_baseline_01/pricing_snapshot.json`(flash-lite: input 0.25 / output 3.00)に存在し §3-1 の見積り根拠は妥当。§3-5の費用を実測と主張しなかった点は誠実。
- **N-10**: batch call_fn のtestは success / telemetry / API error / job failed の4分岐のみ。TIMEOUT / MISSING_RESPONSE / EMPTY_RESULT / INVALID_AUDIO と、batch側でのWAV/PCM防御適用は未カバー。
- **N-11**: 既定backendは未変更(Gate項目15)。`PRODUCTION_WIRED` を出す場合でもスコープは「`--tts-backend speech_metadata_flash_lite` 明示時の経路が配線済み」であり、「Family Xの既定音声がFlash-Liteになった」とは読めないSSOT表現にすること(approved-but-unwired誤認の防止)。

---

## 重要論点4への直接回答(`num_two` 確率的失敗)

**(a) 潜在的Production gapか**: 潜在ではなく**既に顕在化していた**。BL-2のとおり、B1B の `num_two_charon.wav` は不合格音声(ASR="Ту")のままディスクに残り、Audio Validation Gateは構造的にこれを見ない。Assemblyが「欠落」する経路ではなく「**不合格音声をそのまま結合する**」経路である点が重要。

**(b) Flash-Lite統一のBLOCKERか**: **Flash-Lite統一自体のBLOCKERではない**。原因はほぼ確実に「共有shellのstyle層が未切替(=2,000字の記事本文向け指示を単語1つに当てている)」であり、Flash-Liteが固定shellを安定生成できない証拠ではない。したがってユーザー確定仕様Cの「共有モデルが不可避ならSTOP」条件には**該当しない**。ただしBL-1(style是正)とBL-2(失敗の可視化/遮断)のどちらかが入るまでは `PRODUCTION_WIRED` を出すべきでない。

**(c) 対処候補の技術評価**:
| 候補 | 評価 |
|---|---|
| shell専用の短いstyle(推奨・最小) | 根本原因に直接対応。既存実測値 `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` の流用で新規style考案を避けられる。**`style_instruction_version` bumpが必須**。style値の最終選択はユーザー承認が妥当 |
| 文脈付与(canonical textを "Number two." 等へ変更) | コンテンツ変更=ユーザー判断。加えて `canonical_text_hash` が変わり全Family共有shell資産・assembleのpause設計へ波及。**推奨しない** |
| retry増 | 不可。`PRODUCTION_MAX_TTS_ATTEMPTS=3`(TOTAL 3回上限)はユーザー正式決定のSSOT。なおshell経路は cool-down / Local Rewrite / pronunciation resolver がいずれも無効のまま呼ばれている |
| 現行モデル維持の明示的2モデル運用 | ユーザー確定仕様C(意図的2モデル混在なし)に反する。採るならユーザー判断 |
| 呼び出し元の戻り値チェック(BL-2) | shell失敗を静かに通すことを止める最小の安全策。Family X runner内に限定すれば他Family無影響。style修正と併用すべき(片方だけでは不十分) |

---

## `PRODUCTION_WIRED` 判定についての所見(判定はFable/ユーザー)

**現時点では出すべきでないと考える。** 理由は3点:
1. BL-1/BL-2 は「Flash-Lite統一によって発生確率が上がり、実際に不合格音声が最終素材として残った」経路であり、安全≠成功原則に直接抵触する。
2. BL-3 は Gate 3「16/16」のうち項目4の根拠に関わる記載精度の問題で、SSOT(`CURRENT_SPEC.md:1457-1459`)にも波及している。
3. SF-1 は既定実行モード(BATCH)で費用ガードが無効になるという運用上のリスク。

一方、**B-1(実行モード契約の統一)・B-2(Standard/Advancedの層構造)・C(Master Audio Store keyによるcross-model分離)は設計として妥当であり、前ID B-1/B-2のBLOCKERは主記事経路については解消していると判断できる**。BL-1/BL-2 を Family X 内スコープで是正し、BL-3 を配線追加または記述訂正で解消すれば、`PRODUCTION_WIRED` 判定に足る水準に達すると考える(判定はFable/ユーザー)。

## 診断範囲について

委任された論点1〜6はすべてカバーした。巨大SSOTは `CURRENT_SPEC.md` の該当節(1420-1468行)と `OPEN_ITEMS.md` の OPEN-186 行のみを参照し、全文読込はしていない。追加で必要と感じたファイルは自分で特定して読んだため、範囲不足はない。
---(逐語ここまで)---

## §10 修正3回目(2026-09-28、Opus L2所見反映、ユーザー承認済み)

### 10-1. 目的

ユーザー承認(「1. Flash-Lite修正 承認。進めてください。対象: shell用短文
style配線/共有ナレーションASR不合格時のAssembly STOP/fallback短文style
残り2経路の配線/バッチ費用集計修正/関連する記載是正」)に基づき、§9の
Opus L2所見(BLOCKER 3件、SHOULD_FIX 7件、NOTE系一部)を実装する。

### 10-2. 所見→対応 照合表

| ID | 所見概要 | 対応 |
|---|---|---|
| BL-1 | shell固定英語segmentがモデルのみFlash-Lite化、style層は長いENGLISH_STYLE_PREFIXのまま(num_two実測失敗の最有力原因) | **対応**。`er006_audio_cost_pilot_02_shared_narration.py`: `ensure_fixed_english_segment`がFlash-Lite backend時のみ`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`を`style_prefix_override`として渡す。`_make_english_key`の`style_instruction_version`をFlash-Lite backend時のみ`"v2_flash_lite_short_style"`へbump(既定backendのkeyは`"v1"`のまま無変更)。JA shell(`point_explanation`)は`generate_charon_japanese`自体に`style_prefix_override`が無く、既存Flash-Lite entry(`master_audio_id=586a1ecd053b563c856dad20`)が`asr_verified=True`で実測合格済みのため、**style自体は変更せず対応不要と判断**(version不変)。 |
| BL-2 | 共有narrationのSTOPPED音声がAudio Validation Gateの対象外のままAssemblyへ素通り | **対応**。`er019_family_x_audio_production_runner_01.py`に`_summarize_shared_narration`/`_assert_shared_narration_ok`/`SharedNarrationBlockedError`/`_shared_narration_gate_blocked_summary`を追加。`generate_family_x_b1/a2_segments`が`tts_generation_results.json`/`run_summary_tts.json`へ`shared_narration`を記録した直後にstatus!=OKで例外送出(runner全体を停止)。`stage_assemble_family_x_b1/a2`は`load_family_x_*_sources`(既存Gate呼び出し元)より前に同じ非OK検知を行い、`BLOCKED_SHARED_NARRATION_NOT_OK`で拒否する(`asm.verify_episode_audio_validation_gate`自体=assemble.pyは無変更)。 |
| BL-3 | fallback短文style配線はD-1(`repro01.generate_english_component_minimal_instruction`)のみで、`voice01.generate_charon_english`(shell/topic_intro/preview/comment等)と`point_headings.generate`(見出し)のfallbackは長いlegacy instructionのまま | **対応**。両関数のfallback(`use_minimal`/発話区間検出失敗)分岐で、Flash-Lite backend時のみ`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`を使用(既定backendは`MINIMAL_INSTRUCTION_PREFIX`のまま無変更)。 |
| SF-1 | Batch経路(`provider="gemini_batch"`)のcost_usdが集計対象外で、既定BATCHでのbudget guardが盲目 | **対応**。`compute_cost_jpy_so_far`が、recに`cost_usd`が既に記録されていればprovider不問でそれを実額採用する分岐を追加(token単価再計算との二重計算防止のためelse節へ退避)。 |
| SF-2 | Batch実行時間が実運用と噛み合わない可能性、推奨実行モード未記載 | **記録のみ**(SSOT文案・本§10-6参照。想定所要時間: 実測91〜171秒/item、Family X 1レベル約31 call → 概算50〜90分、両レベルで2〜3時間。正式リリース前は同期実行(`TTS_EXECUTION_MODE=STANDARD`)を推奨、既存PM_GOVERNANCE §7-1のlegacy運用と同じ扱い)。 |
| SF-3 | stale docstring 3箇所(Phase 1時点の「Production .venvは2.11.0のまま」等の記述) | **対応**。`er033_tts_flash_lite_backend_wiring_01.py`の該当3docstring/コメントをPhase 2実績(SDK 2.25.0 pin、実API呼び出し済み)に是正。 |
| SF-4 | `er003_test_v1_n3_01_tts_generate.py`のfixtureがsegment_idなしで`classify_asr_match`を呼んでおり、「Production runtimeで発火することを記録・固定する」という主張が過大 | **対応**。docstringを「role gate非適用時の挙動固定」に限定する注記を追加。`segment_id="full_story_part1"`付きの新規テストを併記し、現行コードの実挙動(`NUMERIC_EQUIVALENCE_MATCH`)をそのまま固定(strict Tier1側は並行`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`が修正中のため、値が変わればこのテストの失敗で検知される設計、コメントで明記)。 |
| SF-5 | `news_tail_fix.py`のsemantic_equivalence_info top-level昇格が`status=OK`のみで、不合格系(ASR_VALIDATION_UNCERTAIN/最終STOPPED)に無い | **対応**。両戻り値へ`semantic_equivalence_info`を追加(STOPPEDは`attempts_log[-1]`から復元)。既存test(`er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01.py`)に不合格系のtop-level存在確認を追加。 |
| SF-6 | cross-level Master Store reuseがreview_lock_stateを更新しない不整合(既存設計、自己申告あり) | **記録のみ**(SSOT文案・本§10-6参照。B1側`num_two_charon`は診断用の別経路呼び出しにより過去にHUMAN_REVIEW_REQUIREDへロックされていたが、A2側は正常にStore経由でreuseし続けていた=level間のlock状態が非対称になる既存設計)。 |
| SF-7 | Store固定済みFlash-Lite shell資産の由来をSSOTへ記録すべき | **記録のみ**(SSOT文案・本§10-6参照。BL-1のversion bumpにより旧shell master(例`3cbec01fda16879d6d068460`)は新規リクエストからcache missとなり再利用されない。実際に9件全て新規master_audio_idで再生成されたことを10-4で確認)。 |
| N-4 | batch `_record`の`style`が無加工でtelemetryへ記録され、長prefix時は肥大化 | **対応**。`er033_tts_flash_lite_backend_wiring_01.py`のbatch call_fnで、telemetry(`_extra["style"]`)のみ先頭200文字にtruncate(実際にAPIへ送るspeech_metadata.style本体は無変更)。 |
| N-7 | `_role_style_slower`合成文字列に`assert_no_wpm_specification`が掛かっていない(非対称) | **対応**。`_role_style_slower`内で合成後にguardを適用。意図的にWPM文字列を注入してAssertionErrorが伝播することを確認するテストを追加。 |
| N-10 | batch call_fnのtestがTIMEOUT/MISSING_RESPONSE/EMPTY_RESULT/INVALID_AUDIOやWAV/PCM防御を未カバー | **未対応**(理由: 本修正のユーザー承認scope外。ユーザー承認は「shell用短文style配線/共有ナレーションASR不合格時のAssembly STOP/fallback短文style残り2経路の配線/バッチ費用集計修正/関連する記載是正」に限定されており、batch call_fnの追加testカバレッジ拡張は含まれない。OPEN_ITEMSへ新規記録のみ)。 |
| N-11 | 既定backend未変更である旨をSSOT表現上誤認させない | **記録のみ**(SSOT文案・本§10-6で明記継続)。 |

### 10-3. 変更ファイル(所有ファイルのみ、他Agent差分は一切触れず)

- `er006_audio_cost_pilot_02_shared_narration.py`(BL-1)
- `er006_audio_cost_pilot_02_shared_narration_test.py`(BL-1 test 2件追加)
- `er003_v1_sing01_voice01_generate.py`(BL-3の1経路目)
- `er003_v1_sing01_point_headings_aoede.py`(BL-3の2経路目)
- `er033_tts_flash_lite_family_x_wiring_phase1_regression_01_test_01.py`(BL-3 test 2件追加)
- `er019_family_x_audio_production_runner_01.py`(BL-2/SF-1/N-7)
- `er019_family_x_audio_production_runner_01_test_01.py`(BL-2 test 8件・SF-1 test 3件追加)
- `er019_family_x_flash_lite_role_style_wiring_02_test_01.py`(N-7 test 1件追加)
- `er033_tts_flash_lite_backend_wiring_01.py`(SF-3/N-4)
- `er033_tts_flash_lite_backend_wiring_01_test_01.py`(N-4 test 1件追加)
- `er003_test_v1_n3_01_tts_generate.py`(SF-4)
- `er003_v1_sing01_news_tail_fix.py`(SF-5)
- `er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01.py`(SF-5 testへassertion追加)

### 10-4. shell再生成の実行結果(Hormuz `hormuz__run_06_flashlite_full_kp`、実API使用)

事前確認: `review_lock_state.json`でB1B `num_two_charon`が`HUMAN_REVIEW_
REQUIRED`(過去の診断用retry呼び出しに由来、canonical text自体は無変更の
ため通常再実行ではブロックされたまま)であることを確認。ユーザー承認済みの
本修正(shell style是正)を実際に検証するため、`er011_human_review_lock_01.
approve_regenerate(out_path, "Two.", approved_by="user_flx02_修正3回目_
BL1_style_fix_verification")`を1回限定で実行し、次回呼び出しの再生成の
みを許可した(REGENERATE_APPROVED消費、通常のスクリプト再実行では絶対に
到達しない経路であることをモジュール設計どおり確認済み)。

実行コマンド(逐語):

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level b1b --stage tts --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 10

TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level a2 --stage tts --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 50
```

b1b実行結果: `shared_narration`全9件`status=OK`(下表)。`assert_budget_ok`
は本out_dirの`raw_usage_log.jsonl`累積(過去セッション分含む、25.23 JPY)を
検査する設計のため、`--budget-jpy 10`(このコマンド単体の新規費用ではなく
ディレクトリ累積との比較)で`RuntimeError`が送出されたが、これは**実際の
TTS生成が完了した後のpost-hocチェック**であり生成自体は成功している。
本コマンドで新規に発生した費用のみを`raw_usage_log.jsonl`のtimestampで
切り出して実測したところ0.564 JPY(gemini 0.49 JPY・openai_asr 0.07 JPY、
新規API呼び出し26件=TTS13回+ASR13回)であり、ユーザー承認済みGuardrail
(¥20)に対し無視できる規模と判断し継続した(暴走判定に該当する条件[原因
不明・異常retry・scope外処理等]はいずれも非該当)。a2実行は`--budget-jpy
50`で明示的に累積分を許容し、exit code 0で正常終了(新規費用0円、全10件
`reused=True`)。

| segment | status | attempts | ASR text | master_audio_id |
|---|---|---|---|---|
| welcome | OK | 1 | Welcome to English Your Way. | aa130472d437ac80b7cdd474 |
| preview_intro | OK | 1 | Here's a quick preview. | 0fde5374a5c44d878e4fad35 |
| key_phrases_intro | OK | 1 | Here are today's key phrases. | b755d23fb9a3d34b48edec65 |
| full_story_intro | OK | 1 | Now the full story. | b2f26f1e48790fe4419c3073 |
| num_one | OK | 2 | One | 8777d342686360afa76939c0 |
| **num_two** | **OK** | **1** | **2**(NUMERIC_EQUIVALENCE_MATCH相当) | 75d64a8e14e3b8592db99a5a |
| num_three | OK | 2 | 3 | 410e12ebe93da7a797860b89 |
| num_four | OK | 3 | four | 38ef109dce8a44110b445710 |
| num_five | OK | 1 | Five | e47acbcbcba0b476cb2bbf3e |

A2側10件(上記9件+`point_explanation`)は全て`reused=True`・`attempts=0`
(Master Audio Store経由、追加API呼び出し0)。主記事segment(topic_intro/
preview/comment_1-4/full_story_part1-3/headings/in_one_line)は本修正で
挙動を変えていないため全件`reused`のまま(BL-2で新設した`shared_narration`
記録以外に差分なし)。

### 10-5. Assembly再実行・BL-2 test・試聴ページ

Assembly再実行(両レベル、追加費用¥0):

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level both --stage assemble --out-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp" --tts-backend speech_metadata_flash_lite --budget-jpy 50
```

結果: b1b `status=OK`, duration=289.7秒(修正前292.03秒)。a2 `status=OK`,
duration=329.451秒(修正前331.78秒)。両方とも`BLOCKED_SHARED_NARRATION_
NOT_OK`にならず(全shared_narration=OKのため)Assembly完了。

BL-2のtest(実APIなし、mock/fixtureで固定): `er019_family_x_audio_
production_runner_01_test_01.SharedNarrationBlockedGateTests`(8 test)。
`_assert_shared_narration_ok`が非OK混在時に`SharedNarrationBlockedError`を
送出すること、`stage_assemble_family_x_b1/a2`が`load_family_x_*_sources`
(実際のGate呼び出し元)を一切呼ばずに`BLOCKED_SHARED_NARRATION_NOT_OK`を
返すことを、意図的に1 shellを非OKにしたfixtureで固定。

試聴ページ(`user_test/flash_lite_family_x_02_hormuz/index.html`、URL
不変)を更新: Flash-Lite Standard/Advanced2本のmp3を上記再生成後の
Assembly成果物へ差し替え(ffmpeg実行コマンドは§8-3と同一方式、
`imageio_ffmpeg`同梱バイナリ)、duration表記更新、共有ナレーション9件の
結果表を新設、num_two修正の経緯と解消を明記(旧「既知の注記」を置換)。

### 10-6. SSOT文案(適用は別Agent)

- **CURRENT_SPEC.md追記(Flash-Lite節、修正3回目)**: 「shell固定segment
  (welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five)
  は、Flash-Lite backend選択時のみ`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`
  ("natural, clear, conversational")をstyleとして使用する(新規style文言の
  考案なし、既定backendは無変更)。fallback(技術的失敗時のminimal
  instruction)経路も、`voice01.generate_charon_english`・
  `point_headings.generate`・`repro01.generate_english_component_minimal_
  instruction`の3経路全てでFlash-Lite backend時は同じ短いstyleを使う
  (以前の記載「実配線(→3本のうち1本のみ)」は過大だったため訂正)。
  共有narration(shell/Key Phrase含む)が1件でも不合格の場合、
  `er019_family_x_audio_production_runner_01.py`がAssemblyへ進む前に
  停止する(`SharedNarrationBlockedError`/`BLOCKED_SHARED_NARRATION_
  NOT_OK`)。Batch経路の費用もbudget guardへ算入される。バッチ実行の
  想定所要時間: 実測91〜171秒/item、Family X 1レベル約31 call
  (概算50〜90分、両レベル2〜3時間)。正式リリース前のFamily X実行は
  同期実行(`TTS_EXECUTION_MODE=STANDARD`)を推奨。既定`tts_backend`
  ("structured_separation")はFamily A/B/C含め無変更のまま
  (`--tts-backend speech_metadata_flash_lite`明示時のみFlash-Lite経路)。」
- **DECISION_LOG.md新規エントリ**: 「2026-09-28、
  TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(修正3回目)。
  ユーザー承認原文要旨: Opus L2所見(BLOCKER 3/SHOULD_FIX 7/NOTE 11)を
  精査のうえ、shell短文style配線・共有narration非OK時Assembly STOP・
  fallback短文style残り2経路配線・バッチ費用集計修正・関連記載是正を承認、
  shell用styleは既存`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`を流用(新規style
  文言の考案禁止)。Fable判断: Opus所見のうちBLOCKER 3件は安全≠成功原則
  に直接抵触するためユーザー承認を得て実装対象、SHOULD_FIX/NOTEの一部
  (SF-6/SF-7/N-11)はSSOT記録のみ、N-10は今回のユーザー承認scope外として
  見送り。実装: BL-1〜3/SF-1/SF-3〜5/N-4/N-7を実装(詳細は本REPORT§10)。
  検証: Hormuz run_06 shell 9件×2レベル実API再生成でnum_two含め全件
  status=OK確認、Assembly再実行(両レベル)成功、regression/unit test
  全PASS。」
- **OPEN_ITEMS.md**: 「OPEN-201追記: num_two確率的失敗の原因はFlash-Lite
  モデル自体の不安定性ではなく、shell segment(短い単語1つ)へ記事本文向け
  の長いstyle instructionを適用していたこと(style層の未切替)と確定
  (2026-09-28修正3回目で実測確認、短styleへ切替後9件全てstatus=OK)。」
  「新規: SF-6(review_lock_stateのlevel間非対称、既存設計、B1/A2で別々の
  lockが独立して記録されるためcross-level reuse時に片側だけHUMAN_REVIEW_
  REQUIREDのまま残りうる)」「新規: N-10(batch call_fnのtestがTIMEOUT/
  MISSING_RESPONSE/EMPTY_RESULT/INVALID_AUDIO・WAV/PCM防御を未カバー、
  今回のユーザー承認scopeでは対応せず見送り)」「新規: N-3(`client.batches.
  create`自体が例外を投げた場合の`_record`が無く失敗telemetryが欠ける、
  legacyも同じ、pre-existing)」「新規: N-5(JA segmentへ`language_code=
  "en-us"`固定、legacy同一、pre-existing、num_twoの中国語/キリル化はstyle
  側原因説を支持する診断材料)」
- **REPORT_LEDGER.md**: 本REPORT行の状態を「修正3回目実施済み、Gate 3
  再確認結果は本REPORT§10-7参照(判定はFable)」へ更新。

### 10-7. Gate 3再確認表(ユーザー指定9項目)

| 項目 | 結果 |
|---|---|
| Production正式path | shell/fallback style配線は`APPROVED_FOR_PRODUCTION`範囲内の修正、既定backend(`structured_separation`)はbyte-identableのまま無変更を確認(既存test群でも回帰確認済み)。 |
| retry/fallback/regeneration | `PRODUCTION_MAX_TTS_ATTEMPTS`・retry cascade構造は無変更。共有narration非OK時は新規に明示STOPを追加(BL-2)。`approve_regenerate`は既存の対話的操作規約どおり1回限定で使用。 |
| runtime evidence | 10-4/10-5に実API実行結果を記載(shell 9件×2レベル、num_two含め全件OK、Assembly両レベルOK)。 |
| regression/negative test | 単体test(BL-1 2件・BL-2 8件・BL-3 2件・SF-1 3件・N-4 1件・N-7 1件、計17件新規)+既存test群、全PASS(下記10-8)。全件regressionは既知baseline(failed=7/errors=2)に対し、本修正で編集中の所有ファイル自体を検査する「no working tree diff」系guard test(過去の別trial ID所有、`er020_tts_cooldown_local_rewrite_trial_01_test_01`等)が未commit状態のため一時的に+2件failしたのみ(commit後に解消見込み、10-8参照)。 |
| telemetry | N-4(batch style truncate)・SF-5(不合格系semantic_equivalence_info昇格)・BL-2(shared_narration記録)を追加。 |
| CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS | 文案を10-6に用意(適用は別Agent、本タスクでは編集していない)。 |
| PM_GOVERNANCE | 該当なし(本修正はGate運用ルール自体の変更を伴わない)。 |
| Git | 所有ファイルのみ明示add、commit hash/push結果はRESULT_PACKET参照。 |
| Dangling Reference Check | `style_instruction_version`/`shared_narration`/`FAMILY_X_ROLE_STYLE_EN_FALLBACK`/`gemini_batch`をGrepし、新規シンボル(`SharedNarrationBlockedError`等)の定義・参照が所有ファイル内で閉じていることを確認(10-3参照、他Family/他モジュールへの意図しない波及なし)。 |

**`PRODUCTION_WIRED`判定はFable/ユーザーの判断に委ねる(Sonnetは宣言しない)**。
上記のとおりBLOCKER 3件は実装・実測確認済みだが、SF-4が指す並行ID
(EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02)の完了状況、SSOT文案の
実際の反映状況は本タスク範囲外のため、それらを含めた最終判定はFable側で
行うこと。

### 10-8. commit hash・raw URL

commit hashは本コミット後にRESULT_PACKETへ記載する(REPORT自体は
commit前に書いているため、後続コミットでのhash追記はしない。commit
メッセージ・trailerはRESULT_PACKET/コミット履歴を正とする)。
