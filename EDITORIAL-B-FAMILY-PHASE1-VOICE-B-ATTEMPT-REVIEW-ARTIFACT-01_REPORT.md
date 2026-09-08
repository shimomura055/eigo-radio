# EDITORIAL-B-FAMILY-PHASE1-VOICE-B-ATTEMPT-REVIEW-ARTIFACT-01_REPORT

## 背景
B-Family Phase 1(`er012_output/editorial_b_family_production_phase1_02/b1b`)
のVoice B(segment=`point_two`, voice=Erinome)が、repetition QA
(method_a_ngram)により3 attemptすべてで著者が意図した反復句
"do not need … do not need"(canonical textでは
"the people I need—or do not need—around me")を誤って重複判定し、
Assembly GATE_BLOCKED(`state: HUMAN_REVIEW_REQUIRED`)となっている。
ユーザーが3 attemptすべてを試聴のうえ判断するための専用artifactを作成した。

## 作業内容
- ソースは`b1b/audit/tts_generation_results.json`の`segments.point_two`
  (`attempts_log`3件)および`b1b/audit/review_lock_state.json`から特定。
  attempt保全wav/JSONは`b1b/narration/attempts/point_two_attempt{1,2,3}_
  englishstyleprefixwidemargin.{wav,json}`に実在を確認(3/3揃い、欠落なし)。
- `audio_review_player.py`の共通CSS(`PLAYER_STANDARD_CSS`)・
  `AUDIO_MIN_WIDTH_PX`(360px)・`abs_file_url()`を再利用し、
  Source列なし・Script列拡幅・個別`<audio controls>`常時再生ボタン表示の
  標準見た目を踏襲した新規ページを作成(既存の1本化episode timelineとは
  異なり、3独立attemptの並列比較用のためSeekボタンは対象外。ページ内に
  その旨を明記)。
- 新規ファイル: `er012_output/editorial_b_family_production_phase1_02/
  voice_b_attempt_review.html`のみ。既存wav/JSON/HTMLは一切変更していない
  (git status確認済み、read-onlyアクセスのみ)。
- TTS/ASR/LLM呼び出しは一切行っていない(既存JSON/wavの読み取りとHTML
  組み立てのみ、費用¥0)。`record_human_approval()`等の承認手続きは実行
  していない。

## 掲載内容(各attempt行、同一行配置)
- Attempt番号・voice(Erinome)・duration・TTS方式(`instruction_type=
  english_style_prefix_wide_margin`、全attempt共通)
- 個別`<audio controls>`(min-width 360px、file:///絶対パス)
- canonical script全文(2箇所の"do not need"を`<mark>`強調)
- QAがflagした箇所(method_a_ngramの検知秒・語句・canonical_repeat_count・
  gap秒・intentional値。attempt3のみmethod_d_spectral_long_lagも
  flagged=true、best_run_length=0.12s=decision_threshold同値)
- ASR transcript(faster_whisper実測)
- 確認してほしいこと(定型文)

## flag要約
| Attempt | 検知1回目 | 検知2回目 | gap | method_d_long_lag |
|---|---|---|---|---|
| 1 | 22.64s | 33.52s | 10.06s | flagged=false |
| 2 | 23.66s | 34.38s | 9.98s | flagged=false |
| 3 | 21.62s | 32.84s | 10.52s | flagged=true(境界値ぎりぎり) |

いずれもmethod_a_ngramの"do not need"3-gram一致(canonical_repeat_count=1、
著者が意図した1回分の反復を正しく検知しているが、intentional=falseの
ため機械的にflagされている)。

## Gate 7 (g)(h)(j)(k)(l)機械チェック
- (g) 実segment order・開始秒・click-seek: 本artifactは1本化episode
  timelineではなく3独立attemptの並列比較のため、click-seekは対象外。
  代わりにAttempt順序(1→2→3、試行順)と各attemptのduration/開始秒相当
  情報(QA flag位置の秒)をページ内に明記(ページ内に非該当理由を明記済み)。
- (h) 各segmentの使用voice名: 全行に`voice=Erinome`を明記。
- (j) テキスト未取得segmentの明記: 該当なし(3/3のwav/JSON・ASR
  transcriptとも取得済み、欠落なし)。
- (k) Standard/Batch等TTS方式の明記: 全行に
  `instruction_type=english_style_prefix_wide_margin`を明記。
- (l) 再生ボタンとscriptの同一行配置: 満たしている(Attempt/再生/Script/
  QA flag/ASR/確認事項を1テーブル行に配置、個別audio最低幅360px)。

## 未実施(範囲外・意図的)
- 承認手続き(`record_human_approval()`)は未実行。
- SSOT(`CURRENT_SPEC.md`等)・Git操作・Productionコード変更なし。
- `docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は未接触。
