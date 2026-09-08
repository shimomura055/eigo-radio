# OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04 実行報告

管理ID: OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04
背景: ユーザー決定2026-09-08(選択肢A・決定的置換、
`OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01_REPORT.md`参照)。
Git操作なし(Fableが統合)。rerun_03(`er011_output/
open112_trend_theme2_b_final_audio_rerun_03/`)は一切変更していない
(git diff 0件、確認済み)。

## 1. 例外の根拠(既存承認済みArtifactへの最小修正、DECISION_LOG本体は未編集)

タスク指示により、SSOT(`DECISION_LOG.md`)自体の編集は本タスクでは行わず、
根拠のみここに明記する(後続の統合タスクでFable/ユーザーがSSOTへ転記する
前提)。承認済み完成音声(rerun_03、音声品質ユーザー承認済み)の本文中、
`point_one_body`の"25.2%"・`point_two_body`の"44.7%"のみを、Evidence
Compression Editorを再実行せず決定的な文字列置換で"about 25%"/
"about 45%"へ修正した。Editorのjudgment ruleを経由しない機械的書き換えで
あり、Production標準経路としては例外的な扱い(監査Report 5-1節で
提示済みの選択肢A、ユーザーが選択)。

## 2. 置換diff(article.md / parts.json、各1箇所ずつ確認済み)

置換前に`article.md`・`parts.json`双方で対象文字列が本文中ちょうど1回
であることをスクリプトで機械assertし(`er011_open112_theme2_b1_numeric_
minimal_fix_rerun_04.py`)、2箇所とも1回であることを確認した(1回以外なら
AssertionErrorで即停止する実装)。

| ファイル | 旧 | 新 |
|---|---|---|
| article.md / parts.json point_one_body | "...put solo travel at 25.2%, while..." | "...put solo travel at about 25%, while..." |
| article.md / parts.json point_two_body | "...aged 29 and under, 44.7% were still..." | "...aged 29 and under, about 45% were still..." |

`article.md`と`parts.json`をdiffで突き合わせ、上記2行以外に差分が無いことを
確認済み(diff出力は本行のみ)。

### Preview/Comment/Key Phrase等への同一数値の残存確認(STOP判定)

置換後のrerun_04ツリー全体をgrepし、"25.2%"/"44.7%"の残存箇所を列挙した:
- `audit/tts_generation_results.json`(point_one/two更新前のrerun_03コピー、
  後続ステップで新attemptデータへ上書き済み)
- `key_phrases/canonicalization_prompt.txt`・`keyphrase_redundancy_qa_prompt.txt`・
  `keywords_selector_prompt.txt`(Key Phrase生成時にarticle本文を引用した
  **入力promptの実行ログ**。Key Phrase自体は今回再実行しないため、当時の
  記録としてそのまま残る。実際のKey Phrase出力`keywords_canonicalized.json`・
  `keyphrase_redundancy_qa.json`本体、Preview(`b1_support_texts.json`)、
  Comment 1〜4本文には対象数値が一切現れないことを個別に確認した)。

上記はいずれも「本文以外の実際に読み上げられる/表示されるcontent」への
混入ではなく、過去の生成過程ログのみであるため、STOP対象には該当しない
と判断し処理を継続した(Preview/Comment/Key Phrase出力自体への混入は
ゼロ件)。

## 3. TTS再生成(point_one・point_two、2segmentのみ)

現行Production関数(`er003_v1_n3_01_tts_generate.py::generate_b1_segments()`
がpoint_one/point_twoに実際に渡している引数と同一の
`news_tail_fix.generate_news_narration_wide_margin(disfluency_qa=False,
enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)`)
を、`TTS_EXECUTION_MODE=STANDARD`で実行(スクリプト:
`er011_output/open112_trend_theme2_b_final_audio_rerun_04/
point_one_two_regen_runtime_evidence.py`)。

| segment | attempt数 | status | asr_verified | audio_classification | repetition_qa flagged(方式D'best_run) | sha256(新) |
|---|---|---|---|---|---|---|
| point_one | 1 | OK | True | EXACT_MATCH | False(0.35秒) | `4fee44672f26452837a418c6a44db03cd4e5c1161de6b2da812227656da402df` |
| point_two | 1 | OK | True | NORMALIZED_MATCH | False(0.27秒) | `e76766b8aed1d290b992547ed6855c27615ce3be99847fa4134b3064c1a10afe` |

いずれも1回目の試行でPASS(Human Review Lock発動なし、承認代行の必要なし)。
`audit/tts_generation_results.json`のpoint_one/pointtwoエントリを、新attempt
の実データ(status/asr_text/canonical_text/sha256/attempts_log/
repetition_qa_evidence)へ更新した(rerun_03の`full_story_part1`更新時と
同一パターン)。

コスト実績(`raw_usage_log.jsonl`、`er005_output/cost_baseline_01/
pricing_snapshot.json`の単価で計算、1USD=160円):
- point_one: Gemini TTS $0.014103 + OpenAI ASR $0.000744
- point_two: Gemini TTS $0.013999 + OpenAI ASR $0.000716
- 合計 **$0.029562 ≒ ¥4.73**(上限¥100に対し実費¥4.73)

## 4. 他segmentのbyte-for-byte reuse確認

`verify_reuse_sha256.py`で、rerun_03/b1b配下の全ファイルとrerun_04/b1b
配下を突き合わせ、point_one/point_two本体・attempts・
`audit/tts_generation_results.json`・article.md・parts.json(いずれも
意図的に変更/更新対象)を除く**59ファイル全てでsha256が完全一致**する
ことを確認した(welcome/preview/comment_1-4/full_story_part1/2/
point_one_heading/point_two_heading/in_one_line/Key Phrase英日音声等、
narration・audit・key_phrases配下の全共有資産)。詳細は
`er011_output/open112_trend_theme2_b_final_audio_rerun_04/
reuse_sha256_verification.json`。

`audit/review_lock_state.json`はrerun_03からのコピー後、point_one/point_two
の新規Human Review Lock記録2件が追記された(Production関数自体が書く
副作用、既存の"kp*"エントリ8件は無変更のまま)。

## 5. 再Assembly

既存Production関数`er003_v1_n3_01_assemble.py::stage_assemble_b1`(無変更)
を新規出力先(`er011_output/open112_trend_theme2_b_final_audio_rerun_04/`)
へ実行(スクリプト: 同ディレクトリの`assemble_runtime_evidence.py`)。
Audio Validation Gate(`verify_episode_audio_validation_gate`)は例外を
投げず通過した。

| 項目 | rerun_03 | rerun_04 |
|---|---|---|
| duration | 343.044秒 | 339.594秒(-3.45秒、point_one -1.33秒・point_two -2.12秒) |
| peak | 0.75511(原因piece=Full Story Part 1) | 0.75511(同一、point_one/twoは無関係) |
| clipping | false | false |
| headroom safety valve | 不適用(peak_before=0.7551106) | 不適用(peak_before=0.7551106、閾値0.98未満、rerun_03と同値) |
| target_rms | 0.07389 | 0.07389(同一) |

## 6. player.html(標準フォーマット、Gate 7機械チェック)

`audio_review_player.py`共通関数(Source列なし、audio min-width 360px)で
新規生成(スクリプト: `build_player_runtime_evidence.py`)。Segment label→
text解決は`parts.json`・`b1_support_texts.json`・`timeline.json`・
`keywords_canonicalized.json`・p9a定数(固定テンプレート文言)のみから
構築し、推測補完なし(未解決0件、`unresolved=[]`)。

file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_04/player.html

Gate 7機械チェック結果(全19行+Key Phrase英日5件、実質29行、Pythonで検証):
- (a)〜(d)(g)(h)(l): タイムラインテーブルヘッダー4列・Source列なし → PASS
- 全29行(pause_行は表に含めず除外)が`<td>`4個+Seekボタンを保持 → PASS
- SFX/ジングル行7件(Intro/Notification1-3/Point Notification x2/Outro)は
  `<audio>`0個、かつ「効果音」または「ジングル」の文言を含む → PASS
- (h) 各行`<small>voice=...</small>`で使用voice名を明記(全29行) → PASS
- CSS中に`min-width: 360px`・`width: 400px`が存在 → PASS
- `class="missing"`行は0件(全segment解決済み、「未取得」表記なし) → PASS

## 7. 変更ファイル一覧

- 新規: `er011_open112_theme2_b1_numeric_minimal_fix_rerun_04.py`(root)
- 新規: `er011_output/open112_trend_theme2_b_final_audio_rerun_04/`
  (b1b/一式[point_one.wav・point_two.wav・関連attempts・tts_generation_
  results.json・review_lock_state.json・article.md・parts.jsonのみ実質変更、
  他59ファイルはbyte-for-byte reuse] + assembled/wav + audit/[gain_report/
  timeline/headroom_report] + run_summary_assemble.json + player.html +
  numeric_minimal_fix_diff.json + point_one_two_regen_run_summary.json +
  point_one_two_regen_runtime_evidence.py + assemble_runtime_evidence.py +
  build_player_runtime_evidence.py + verify_reuse_sha256.py +
  reuse_sha256_verification.json + raw_usage_log.jsonl)
- 更新: `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(本タスク専用、
  上書き前提)
- 副作用(既存Production関数がTTS/ASR呼び出し時に自動更新する共有台帳、
  タスク開始前から既に他タスクの変更で差分あり。本タスクの2回のTTS/ASR
  呼び出し分がさらに追記された): `er011_output/attempt_history.jsonl`
  (rerun_04関連2件追記を確認)・`er006_output/master_audio_store_01/
  manifest.json`・`er006_output/master_audio_store_01/reuse_telemetry.jsonl`・
  `er006_output/pronunciation_ledger_01/ledger.json`・`er006_output/
  audio_retry_cascade_prod_01/human_review_queue.jsonl`
- 不変(確認済み): `er011_output/open112_trend_theme2_b_final_audio_rerun_03/`
  (git diff 0件)、`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
  `HISTORY_INDEX.md`(いずれも本タスクでは編集していない)
- 本タスクと無関係な既存差分(発見のみ、編集・stageせず): 
  `er012_editorial_b_voices_trial_10_comment1.py`(本タスク開始前の
  別作業による差分と推定、本タスクでは一切触れていない)

## 8. 未確認事項・USER_DECISION_REQUIRED候補

- `DECISION_LOG.md`本体への正式転記は本タスク範囲外(タスク指示どおり、
  本Reportの2節が転記元根拠)。後続の統合タスクでFable/ユーザーが転記する
  必要がある。
- `OPEN_ITEMS.md`更新は本タスクの禁止事項に含まれるため未実施(rerun_03
  では実施していたが、本タスクでは意図的にスキップ)。
- 到達Statusは`USER_FINAL_AUDIO_REVIEW_REQUIRED`(ユーザー最終試聴待ち、
  `APPROVED_FOR_PRODUCTION`は本タスクでは判定しない)。
- 監査Report(WIRING-AUDIT-01)5-4節で言及されていた「News/Editorial型
  他ジャンルへの同種問題の遡及調査」は本タスク範囲外、未実施。
