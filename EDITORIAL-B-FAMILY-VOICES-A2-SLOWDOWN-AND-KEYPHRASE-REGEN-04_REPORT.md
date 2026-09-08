# EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04

管理ID: EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04(Lane B)
日付: 2026-09-08

対象: `er012_output/editorial_b_voices_a2_free_address_03/`をbaselineに、
ユーザー決定(2026-09-08)の4項目(Voice A/B slowdown、Key Phrase「stay put」
比較再生成、11語超18/38許容、Fact Checker REVIEW_REQUIRED今回限り承認)を
反映し、`.../04/`へ再Assemblyした。

## 1. Voice A/B slowdown(既存B-A2-9への回答)

### 1-1. 既存実装の再確認

- 標準A2の6% slowdown対象segment(`A2_SLOWDOWN_TARGET_SEGMENTS`、
  `er003_v1_n3_01_tts_generate.py:107-110`): `point_one_heading`・
  `point_two_heading`・`full_story_part1`・`full_story_part2`・
  `point_one`・`point_two`・`in_one_line`。実装は
  `generate_a2_segment_with_slowdown()`(同ファイル189-248行目、無変更)
  = 通常ペース生成 + `apply_a2_slowdown_postprocess()`(6% time-stretch、
  `er008_a2_postprocess_slowdown_01.A2_SLOWDOWN_PERCENT=6.0`、無変更)。
- B-Family側でHook Part1/2(`full_story_part1/2`)・Narrator見出し・
  Tension・Closing(`in_one_line`)は既にこの標準関数をそのまま使用済み
  (`er012_editorial_b_voices_a2_trial02_runner.py`既存コード、対象segment
  定義どおり)。**対象外(Point Notification等SFX、Comment/Preview日本語、
  Key Phrase)は元々非対象のため今回も無変更。**
- Voice A/B本文(`point_one`/`point_two`)のみ、Voice指定TTS専用関数
  `b1prod.generate_voice_body_wide_margin()`を使用しており、標準A2の
  slowdown引数(`style_prefix_override`)を渡す手段が存在しなかった
  (前回`TRIAL-02`調査時点の既知の制約、`B-A2-9`としてUSER_DECISION_
  REQUIRED登録)。

### 1-2. 実施した修正(最小・後方互換)

- `er012_b_family_voices_production_01.py::generate_voice_body_wide_margin()`
  へ**完全後方互換の追加引数`style_prefix_override: str = None`のみ**を
  追加(既定Noneなら従来どおり`p9a.ENGLISH_STYLE_PREFIX`を使用、既存
  Production呼び出し[Phase 1 `er012_b_family_production_runner_01.py`
  含む]は本引数を渡さないため挙動・出力とも無変更)。関数内部ロジック
  (ASR Cascade・disfluency gate・repetition QA・connected speech
  equivalence layer・Human Review Lock・retry上限)は無改変。
- `er012_editorial_b_voices_a2_trial02_runner.py`へ新規合成関数
  `generate_voice_body_wide_margin_with_a2_slowdown()`を追加(既存関数
  2つを順に呼ぶだけ、新規TTS/ASR/time-stretchロジックなし):
  1. `b1prod.generate_voice_body_wide_margin(..., style_prefix_override=
     n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER, enable_connected_speech_
     equivalence_layer=True, enable_repetition_qa=True)`(標準A2の
     point_one/point_two相当と同じ引数値)。
  2. `n3_tts.apply_a2_slowdown_postprocess(...)`(標準A2と完全に同一関数、
     無変更)。
- `run_tts()`内のpoint_one/point_two呼び出しをこの新規関数へ切替。
  timelineラベルを`(voice, standard pace)`→`(voice, A2 slowdown)`へ
  更新(表示のみ)。

### 1-3. 再生成結果(TTS_EXECUTION_MODE=STANDARD)

| segment | voice | status | slowdown_pct_actual | asr再検証 |
|---|---|---|---|---|
| point_one | Algieba | OK | 5.967% | NORMALIZED_MATCH / asr_verified=True |
| point_two | Erinome | OK | 5.960% | NORMALIZED_MATCH / asr_verified=True |

両segmentとも1 attemptでPASS(retry無し)。`point_one_original.wav`/
`point_two_original.wav`(time-stretch前、標準A2と同じ保全規約)を新規に
保全。

## 2. Key Phrase「stay put」旧/新比較

- 既存の承認済み再生成経路: `review_lock.approve_regenerate()`(Trial-09
  heading regen-03前例と同一関数、無変更)を新規path
  (`kp4_en_new_v2.wav`)に対して1回だけ実行し、承認記録を
  `.../04/a2/audit/stay_put_regen_user_approval_04.json`へ保存。
- 実際の再生成は`repro01.generate_key_phrase_component_verified()`
  (Production、無変更。Master Audio Storeのgenerate_fnとして内部的に
  使われているのと同一関数)を**直接**呼び出した。**Master Audio Store
  (`er006_master_audio_store_01.py`のmanifest/cache)へは一切書き込んで
  いない**(共有・cross-episode資産のため、このタスクではshared cacheを
  更新せず、episode専用のローカルファイルとしてのみ新版を生成)。
- 結果: 旧版(`kp4_en_old_v1.wav`、_03のMaster Audio Store再利用分を保全)
  ・新版(`kp4_en_new_v2.wav`)とも`status=OK`・`asr_text="Stay put."`・
  `disfluency_checked=True(flagged=False)`。新版は`asr_verified=True`
  でQA PASSしたため、既存QA全通過(ASR照合・disfluency QA・pronunciation
  ledger込み)の判定に従い**新版を採用**(`kp4_en.wav`を新版へ差し替え、
  Assembly Gateが参照する`tts_generation_results.json`/
  `key_phrase_reuse_and_regen.json`のrank=4 englishエントリも更新)。
  旧版は削除せず`kp4_en_old_v1.wav`として保全。

## 3. Fact Checker REVIEW_REQUIRED(複合Voice帰属)

`record_human_approval()`(音声segmentのASR検証state専用、text QA
verdictには意味的に不適合と判断)を流用せず、同じ「明示的な承認記録を
書面で残す」思想の専用recordを新規作成:
`.../04/a2/audit/fact_checker_review_required_human_approval_04.json`
(approved_by=user、note="2026-09-08ユーザー決定・今回限り・恒久運用に
しない"を明記、scope=A2本文の複合Voice帰属)。

## 4. 11語超18/38文

新上限は追加せず、既存の`article.md`(_03から無変更でコピー)をそのまま
採用(許容、個別修正なし)。

## 5. Assembly結果

| 項目 | 値 |
|---|---|
| status | OK |
| duration_seconds | 349.962 |
| peak | 0.95049(headroom safety valve閾値0.98未満、`applied=false`) |
| clipping_detected | False |
| sample_rate/channels | 48000 / 2 |
| Audio Validation Gate level | `B_FAMILY_A2`(既存判断どおり変更なし、決定#5) |

## 6. sha256再利用件数

narration 41ファイル中、**38ファイルが_03とbyte-for-byte一致(sha256
一致、無変更再利用)**。差分3ファイル(`point_one.wav`・`point_two.wav`・
`kp4_en.wav`、いずれも本タスクの意図的な再生成対象)。新規追加4ファイル
(`point_one_original.wav`・`point_two_original.wav`・
`kp4_en_old_v1.wav`・`kp4_en_new_v2.wav`、いずれも比較・保全用)。

## 7. player.html

`er012_output/editorial_b_voices_a2_free_address_04/player.html`
(`file:///C:/Users/tensh/eigo-radio/er012_output/editorial_b_voices_a2_free_address_04/player.html`)。
標準player形式(Gate 7 (a)〜(l)、Seek+voice+script+個別音声を同一行)に
加え、「Key Phrase 4「stay put」旧/新比較」table(同一行に旧・新の再生
ボタン、QA summary、採用版)を追加。Voice A/B行のラベルは
`(voice, A2 slowdown)`へ更新。

## 8. 費用

このrun専用の新規コストログ(`_04`独自、`_03`以前の費用は含まず)で
**7.23 JPY**(gemini 6.52 + openai_asr 0.71)。上限¥100以内。

## 9. 回帰

- `er012_editorial_b_family_production_phase1_test_01.py`(b1prodの
  直接消費者、シグネチャ検査含む): 14 tests、全PASS(`generate_voice_
  body_wide_margin`への引数追加後も既定値・Phase 1呼び出しは無変更で
  あることを確認)。
- `run_project_regression.py`(全project、2195件収集): 2192 passed / 3
  failed。失敗3件(`er003_test_bad.FixtureTests.test_case_0`、
  `er003_test_p2j_investigate.py`の2件)はいずれも本タスクで変更した
  モジュールを一切importしておらず(該当テストのimport文で確認済み)、
  過去commit時点のfile countスナップショット照合という既知の無関係な
  drift(多数の過去Reportで言及済みの既知パターン)。本タスク由来の
  新規失敗は0件。

## 10. Gate / STOP

Gate 1 = VALIDATED(ユーザー再試聴前、`APPROVED_FOR_PRODUCTION`は宣言
しない)。STOP項目なし(4項目すべて完了)。

## 11. 変更・新規ファイル一覧

変更(Production、完全後方互換の引数追加のみ):
- `er012_b_family_voices_production_01.py`
  (`generate_voice_body_wide_margin`へ`style_prefix_override`引数追加)

変更(Lane B runner):
- `er012_editorial_b_voices_a2_trial02_runner.py`
  (新規関数`generate_voice_body_wide_margin_with_a2_slowdown`追加、
  point_one/point_two呼び出し切替、timelineラベル更新、
  `build_player_html`へ`stay_put_comparison`引数追加)

新規(Lane B、既存Production/Trialファイルは無変更):
- `er012_b_voices_a2_slowdown_keyphrase_regen_04_runner.py`
- `er012_output/editorial_b_voices_a2_free_address_04/`配下一式
  (narration/assembled/audit/player.html)

## 12. 補足(scope判断)

`generate_voice_body_wide_margin`への引数追加は、b1prodがLane B専用
ではなくPhase 1 Production runner(`er012_b_family_production_runner_01.py`)
とも共有するモジュールであるため、慎重を期し既定値保持・回帰テスト実測
(14件+project全体2195件)で無影響を確認した上で実施した。ユーザー決定
#1が既に「標準A2仕様の既存6% slowdownを適用」と明示していたため、
新規判断・新規仕様の追加ではなく既存決定の実装として扱った。
