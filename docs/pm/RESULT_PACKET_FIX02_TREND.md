# RESULT_PACKET_FIX02_TREND

管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND

## 1. 最終Status
**A2: 完成(PASS)。Trend Production(A2+B1B)が両level完成。**
1回限りの承認付き再生成でpoint_twoがstatus=OK/verified=trueとなり、
Assembly(Gate OFF)→Audio Validation Gate(opt-in ON)→mp3変換→player→
article/audio consistency→web_delivery.json→cost集計まで完走。

## 2. 承認記録
`approve_regenerate()`呼び出し: 2026-09-14T23:55:59.311520+00:00(UTC)、
対象=`er014_output/four_type_observation_01/trend/audio/a2/narration/point_two.wav`、
根拠=本委任文中のユーザー承認原文(2026-09-15)。1回のみ呼び出し(2回目以降なし)。
戻り値`state=REGENERATE_APPROVED`。呼び出し前にcanonical text sha256が
前回lockエントリと完全一致することを機械確認済み(テキスト変更なしを保証)。
詳細: `er014_output/four_type_observation_01/trend/audio/a2/point_two_time_variance_run.json`。

## 3. 時間差run結果
前回(2026-09-14T20:25:16 UTC): final_status=`ASR_VALIDATION_UNCERTAIN`、
ASRが"Alexa+"のまま(canonical="Alexa Plus"待ち)書き起こし、verified=false。
今回(2026-09-15T08:56:47 UTC): final_status=`OK`、ASRが"Alexa Plus"と
書き起こしcanonicalと一致、classification=`NORMALIZED_MATCH`、verified=true。
経過時間=45091秒(約12時間31分)。canonical_text_sha256は両run完全一致
(`a30e5742a5e7a08f...`)。TTS attempt数=1(cumulative_tts_attempts 1→2)、
ASR呼び出し2回(標準ペースASR+6% time-stretch後の再検証ASR、
generate_a2_segment_with_slowdown内部の既定挙動どおり、追加retryなし)。

## 4. Audio Validation結果
gate_off=PASS(Assembly成功)。gate_on(`verify_episode_audio_validation_gate`、
緩和なし)=PASS。`er014_output/four_type_observation_01/trend/audio/a2/audio_validation.json`。

## 5. duration
415.42秒(約6分55秒)。`assembled/`(wav、.gitignore対象で非commit)。

## 6. article/audio consistency
`article_audio_consistency.json`: `all_pass=true`(content segment14件+
Key Phrase5件すべてOK)。article.md再読込→`split_article_text()`再実行が
parts.jsonとbyte-identical。`reading_transforms_applied_segments=
[full_story_part1, full_story_part2, point_two]`、
`reading_transforms_word_safety_all_pass=true`(読み整形前後で語の
追加削除がないことを独立機械確認、`tts_reading_transforms.json`参照)。

## 7. mp3・player・URL・gitignore確認
mp3合計30件(episode 1件+segment 29件)、合計7.062MB、`all_under_50mb=true`。
episode.mp3=4.448MB/415.42s。`player.html`のsrc/href属性にfile:///・絶対パス
(C:\)は0件(該当1件は本文中の日本語注記「file:///・絶対パス不使用」のみ、
実リンクではない)。`git check-ignore`はexit 1(mp3は無視されない、
コミット対象)。予定URL: raw.githubusercontent.com経由でcommit後に確定
(本タスクではcommit未実施)。

## 8. なぜ既存normalizerで表記揺れを吸収できないか
既存の記号・複合語対応(`er003_v1_n3_01_tts_generate.py`の
`_KP_COMPOUND_OVERRIDES`辞書、healthspan→health span等)は**単一方向の
固定テキスト置換**(TTS入力テキスト側を書き換えるだけ)であり、ASR側の
書き起こし表記そのものの揺れを予測・吸収する仕組みではない。
「Alexa+」は前回run(2026-09-14)ではASRが記号のまま"Alexa+"と書き起こし、
今回run(2026-09-15)では同一canonical text("Alexa Plus")に対しASRが
"Alexa Plus"と書き起こした。つまりASR側の表記ゆれが**双方向**(run次第で
記号/展開形のどちらにも振れる)であり、CONT1で適用した一方向置換
(Alexa+→Alexa Plus、TTS入力のみ変更)だけでは原理的に安定して吸収できない
(今回はたまたまASRがcanonicalと一致する側に振れてPASSしたに過ぎない)。
既存QAが「完成と誤報告」しなかったのは正しい(Human Review Cost Guardが
1 attemptで即座にロックし、0 API callで安全に停止した)。

## 9. 費用
本タスク実費=**¥3.36**(point_two 1回の再生成[TTS 1回+ASR 2回、標準+
6% time-stretch再検証]、Assembly/Gate/mp3変換/player生成はAPI費用なし)。
上限¥40以内(超過なし)。
本タスクで**cost aggregation bug**を発見・補正(詳細は13番参照): 補正前の
`cost_summary_audio.json`levels.b1b=¥160.16は実際にはa2初回パス分まで
混入した値だった。補正後: a2=¥93.98、b1b=¥69.54、combined=¥163.52。
**Trend総原価(補正後)=¥174.03(本文)+¥163.52(A2+B1B音声化)=¥337.55**
(旧報告の¥334.18/¥334.19はcost集計バグ発見前の値であり、本タスクの
規模自体はごく小さい[+¥3.36]ことに注意。差額の大部分はバグ補正による
再配分であり実際の追加支出ではない)。

## 10. model_id/TTS/ASR model
TTS: `gemini-2.5-pro-preview-tts`(voice: Aoede英語、既存A2構成のまま、
LLM/Scaffold呼び出しなし)。ASR: `gpt-4o-mini-transcribe`(openai_asr、英語、
2回呼び出し=標準ペース検証+6% time-stretch後の再検証)。前回run・CONT1と
同一Production経路(model_id変更なし)。

## 11. OPEN-153追記案
「Trend A2 point_two(Amazon Alexa+の表記)は、2026-09-14 runでASRが
"Alexa+"のまま書き起こしHuman Review Cost Guardでロック(0 API call、
安全に停止)。ユーザー承認に基づき2026-09-15に同一canonical textで
承認付き再生成を1回実施した結果、今回はASRが"Alexa Plus"と書き起こし
NORMALIZED_MATCH/PASSした(同一テキストに対しASR表記が双方向に揺れる
run-to-run varianceを実測。詳細:
`er014_output/four_type_observation_01/trend/audio/a2/
point_two_time_variance_run.json`)。恒久対応(tts_safe_en系への辞書拡張、
またはASR側の許容パターン拡張)は依然ユーザー承認要、今回はHuman Review
Lock経由の1回限り承認再生成で解消(再発防止の恒久対応ではない)」。

## 12. commit対象候補一覧(サイズ付き、wav除外・mp3必須)
- `er014_output/four_type_observation_01/trend/run_trend_audio_completion_3.py`(新規、約20KB)
- `er014_output/four_type_observation_01/trend/audio/a2/audit/review_lock_state.json`(更新)
- `er014_output/four_type_observation_01/trend/audio/a2/audit/tts_generation_results.json`(更新)
- `er014_output/four_type_observation_01/trend/audio/a2/audit/{gain_report.json,gate_opt_in_check.json,headroom_report.json,timeline.json,run_summary_assemble.json}`(新規、Assembly成果物)
- `er014_output/four_type_observation_01/trend/audio/a2/audit/attempts/point_two_attempt7_custom35d6860b.json`(新規、attempt記録。対応wavは.gitignore対象)
- `er014_output/four_type_observation_01/trend/audio/a2/article_audio_consistency.json`(新規、2.9KB)
- `er014_output/four_type_observation_01/trend/audio/a2/audio_validation.json`(新規、0.1KB)
- `er014_output/four_type_observation_01/trend/audio/a2/player.html`(新規、19.7KB)
- `er014_output/four_type_observation_01/trend/audio/a2/point_two_time_variance_run.json`(新規、2.7KB)
- `er014_output/four_type_observation_01/trend/audio/a2/run_result_audio_completion_fix02.json`(新規、4.2KB)
- `er014_output/four_type_observation_01/trend/audio/a2/web/`(新規、mp3 30件・合計7.06MB、episode.mp3+segments/*.mp3)
- `er014_output/four_type_observation_01/trend/audio/{cost_summary_audio.json,web_delivery.json,tts_reading_transforms.json,raw_usage_log_audio_completion.jsonl}`(更新)
- `er014_output/four_type_observation_01/trend/production_set_cost.json`(更新)
- `er014_output/four_type_observation_01/progress_log.md`(1行追記)
- `docs/pm/delegation_log/USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND.md`+`_check.json`(新規)
- 除外(wav、.gitignore対象): `narration/point_two.wav`・`narration/attempts/*.wav`・`assembled/*.wav`

## 13. T-0・事前指定外Read・STOP有無
T-0: PASS(`docs/pm/delegation_log/USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND_check.json`)。
事前指定外Read: (1) `er011_human_review_lock_01.py`の`guarded_generate`/
`guarded_generate_with_language_arg`デコレータ実装(L556-620付近、承認後の
実際の再生成呼び出しがcheck_before_generation/record_outcomeへどう配線
されているかの確認に必要だった)。(2) `er003_v1_n3_01_tts_generate.py`の
`generate_a2_segment_with_slowdown`(L189-248、CONT1と完全同一引数で
呼ぶための正確なシグネチャ確認)。(3)
`er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion_2.py`
のL270-312(guarded_generateが実際に見るtextがtts_safe変換後であることの
既存コード内コメントを確認するため、CONT1のcanonical_text記録と実際の
lock hash対象の差異を切り分けるために必要だった)。
(4) `er014_output/four_type_observation_01/trend/run_trend_audio_completion.py`の
`run_assembly`/`run_gate_opt_in_check`/`build_player_and_web_delivery`/
`update_shared_outputs`/`append_progress_log`/`cost_breakdown_by_stage`
(L100-192, 472-900、Assembly以降の関数を正確な引数で呼ぶために必要
だった)。
**本タスクで新たに発見した問題(禁止事項の範囲外、既存Production非該当の
driverスクリプト内バグ)**: `base.cost_breakdown_by_stage()`が共有ログ全体を
level非絞り込みで返すため、`base.update_shared_outputs()`を複数level分
呼ぶとlevel別費用が混入・二重計上される。本タスク内のローカル関数
(`cost_breakdown_by_stage_for_level`/`fix_cost_summary_and_production_
set_cost`、CONT1のbuild_consistency_check_fixed()と同じ手法)で補正し、
`cost_summary_audio.json`/`production_set_cost.json`を正しい値へ更新した
(base側ファイルは無変更)。Productionコード[er003/er006/er011]・Gate・
retry上限は無変更。
**STOP: なし**。point_two 1回限り承認付き再生成がPASSし、Trend Production
(A2+B1B)が完成した。
