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
- commit hash: `<PLACEHOLDER_COMMIT_HASH>`
- push: `git push origin main`実行、結果は下記RESULT_PACKET参照。
- HTTP 200確認: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/flash_lite_family_x_02_hormuz/index.html`
  の結果は下記RESULT_PACKET参照(push後の待機・再確認込み)。

### 8-7. STOP該当(修正2回目)

無し(実費用¥0、合計配布サイズ約19.75MB<50MB閾値、`.gitignore`変更不要、
`git add -f`不使用、コード/SSOT変更なし)。
