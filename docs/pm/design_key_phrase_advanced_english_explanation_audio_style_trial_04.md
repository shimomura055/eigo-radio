# design_key_phrase_advanced_english_explanation_audio_style_trial_04.md

管理ID: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`
(Sonnet委任、設計メモ)

## 1. 目的

ユーザー判断: TRIAL-03の After(`clear, precise, unhurried`)は**遅すぎた**
(不採用)。Before(`clear, precise, explanatory`)とunhurriedの**中間の自然
な速度感**を3パターン探索する。Phrase選定・英語解説text生成は一切やり直
さない(Hormuz既存5 Phrase + TRIAL-02 B候補英語解説textを逐語reuse)。

## 2. reuse元とデータフロー

`--source-dir` は `er042_output/key_phrase_advanced_english_explanation_
audio_style_trial_03/hormuz`(TRIAL-03の出力そのもの)。TRIAL-03が既に
Phrase EN音声・Before音声(explanatory)・After音声(unhurried)を作成済み
のため、TRIAL-04ではer041まで遡らずTRIAL-03出力を直接reuseする。

- `reused_audio_summary.json`(TRIAL-03): `phrase_en` / `before_explanation_en`
  ラベル5件ずつ(wav dst path、text、style_prefix_used等)。
- `after_audio_summary.json`(TRIAL-03): `generated_after_explanation_audio`
  5件(text、phrase、rank、style_prefix_used=`clear, precise, unhurried`、
  duration_seconds等)。

TRIAL-04の `cmd_reuse` は上記3系列(phrase_en / before(explanatory) /
reference_after(unhurried))を機械検証(style文字列完全一致・
`hints_applied==False`・`status==OK`)の上でコピーし、**参考列**として
試聴ページに表示する(新規TTS callなし、¥0)。

## 3. Style 3案(新規、A/B/C)

速度は数値指定しない(WPM等を書かない)。「clear, precise」を必ず含む。

| ラベル | Style文字列(TTSへそのまま渡す最終文字列) |
|---|---|
| A(少しだけ落ち着かせる) | `clear, precise, at a slightly relaxed pace` |
| B(中間) | `clear, precise, at a measured pace, without dragging` |
| C(やや丁寧) | `clear, precise, carefully paced for understanding, without slowing down` |

Before(`clear, precise, explanatory`)・Reference After(`clear, precise,
unhurried`、不採用だが速度感の参考として掲載)と並べて試聴ページに表示する。

## 4. 新規生成(cmd_variant_audio)

Production同一関数`generate_narration_snippet_verified_strict`
(`er003_v1_repro01_main_generate`)をTRIAL-03と全く同じ呼び出し形で使用し、
`style_prefix_override`のみA/B/C 3種に差し替える。Trial専用Master Store
(`role_trial.trial_master_audio_store(trial_store)`)で隔離し、
`TTS_EXECUTION_MODE=STANDARD`を必須化(未設定ならSTOP、TRIAL-03と同じ
Guardrail)。

5 Phrase × 3 Style = 15 call。既存ASR cascade(`max_attempts=2`)のまま。
budget-jpy 10でTRIAL-03と同じ`compute_cost_jpy_so_far`によるcumulative
チェック+超過時`stop_reason`書き出し(独自にGate回避しない)。

出力: `kp{rank}_variant_{A|B|C}_en.wav`、
`variant_audio_summary.json`(management_id / generated_variant_audio /
total_new_audio_cost_jpy / cost_by_provider)。

## 5. 試聴ページ

`user_test/kp_advanced_explanation_audio_trial_04/index.html`。5 Phrase
それぞれについて: Phrase EN(reuse) / 解説text(共通) / Before(参考、reuse)
/ A / B / C / Reference After(参考、reuse) の7列相当。各行にTTSへ渡した
Style全文(省略なし)・duration・ASR textを表示。

duration比較表(Before/A/B/C/Referrence Afterの秒数・語数/秒)を別セクショ
ンとして追加し、「速度感」の客観指標(words per second)を提示する。

## 6. Production無変更の保証

- 新規importはTRIAL-03と同一モジュール群のみ(`er003_v1_repro01_main_
  generate`, `er005_cost_logger`, `er019_family_x_audio_production_
  runner_01`, `er038_tts_all_spoken_role_style_trial_01`)。
- Key Phrase選定モジュール(`er003_v1_n3_01_scaffold_generate`等)・
  Production Master Store path(`er006_output/master_audio_store_01`)は
  コード中に一切出現しない(TRIAL-03と同じ`ProductionIsolationTest`を
  流用・踏襲)。
- `--stage all`は使わない。対象segmentはTrial script内で15 callに限定。

## 7. Trial Status

到達上限 `USER_DECISION_REQUIRED`(ユーザー試聴前は自己宣言しない)。
