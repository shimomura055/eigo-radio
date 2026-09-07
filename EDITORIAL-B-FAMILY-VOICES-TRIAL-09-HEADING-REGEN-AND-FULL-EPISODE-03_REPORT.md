# EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03

管理ID: EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03(Lane B)
日付: 2026-09-07

対象: `point_two_heading`("Another Voice: The freedom to move.")の
`HUMAN_REVIEW_LOCKED`を、ユーザー明示承認に基づき1回だけ再生成し、
PASSしたため1本化Assembly + Gate 7準拠player.htmlの完成episodeを作成した。

新規実装ファイル: `er012_editorial_b_voices_trial_09_heading_regen_03.py`
(root、新規)。既存Production/Trial関数は無変更のまま呼び出しのみ。

---

## 1. 承認記録

ユーザー決定(2026-09-07、明示承認):

1. `point_two_heading`の再生成を1回だけ承認(根拠: `EDITORIAL-B-FAMILY-
   VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02_REPORT.md`§8-2 (a))。
2. 再発防止候補(entity_like誤分類/delete型diff問題)はTrialとして起票の
   み(実装しない)。
3. `PM_GOVERNANCE.md`§8への追記承認。

`review_lock.approve_regenerate(out_path, text, approved_by="user")`
(Production、無変更)を1回だけ呼び、承認記録を
`er012_output/editorial_b_voices_trial_09_audio/b1b/audit/user_approval_
record_heading_regen_03.json`へ保存した(approved_by=user、
approved_at=2026-09-07T20:20:xx、rationale=上記根拠を明記)。この呼び出し
1回のみで、以降`approve_regenerate()`は再度呼んでいない。

## 2. 再生成attempt表

| 項目 | 値 |
|---|---|
| 承認前state | `HUMAN_REVIEW_REQUIRED`(final_status=ASR_VALIDATION_UNCERTAIN、cumulative_tts_attempts=1) |
| 承認後state(呼び出し直後) | `REGENERATE_APPROVED` |
| 使用関数 | `er003_v1_sing01_point_headings_aoede.generate()`(Production、無変更。Trial-09の`run_tts_new_segments`が使ったのと同一関数) |
| TTS_EXECUTION_MODE | `STANDARD`(本タスクscript冒頭で明示設定) |
| attempt1 instruction_type | `english_style_prefix` |
| attempt1 ASR(Primary、faster-whisper local disfluency evidence含む) | `"Another voice, the freedom to move."` |
| attempt1 classification | `NORMALIZED_MATCH` |
| attempt1 length_ok / verified | true / true |
| disfluency_checked | true(flagged=false、word_count=6) |
| 最終status | **OK**(1 attemptでPASS、Secondary ASR Cascadeは発火せず) |
| 音声長 | 3.74秒(Assembly timelineでの実測、attempt2ファイル: `b1b/narration/attempts/point_two_heading_attempt2_englishstyleprefix.wav`、旧attempt1[ASR_VALIDATION_UNCERTAIN、"the freedom to move"のみ]は`attempt1`として保全済み) |
| 承認後state(呼び出し直後) | `RESOLVED` |

Primaryの1回目でNORMALIZED_MATCH・verified=Trueに到達したため、Secondary
ASR Cascade(Azure等)は発火しなかった(`human_review_queue_detail_if_
reached`はnull、Human Reviewへ到達していないため)。

## 3. Assembly結果

`asm.load_b1_sources()`(Gate含む、Production、無変更)を通過するには、
`b1b/audit/tts_generation_results.json`(Gateが参照する監査記録、
`review_lock_state.json`とは別ファイル)側のpoint_two_headingもTrial-09
原実行時点のstale記録(HUMAN_REVIEW_LOCKED)のままだったため、本タスクで
得た新結果(status=OK)へこの1 segment分だけ更新した(`finalize_tts_
results()`が本来書くのと同じ形、Gate関数自体は無変更)。

Assembly実行結果(`trial09.run_voices_assembly()`、Trial-09既存の
`build_b1_voices_timeline_trial09` + Production `assemble_with_timeline`
/`apply_headroom_safety_valve`、いずれも無変更):

| 項目 | 値 |
|---|---|
| status | OK |
| duration_seconds | 301.795 |
| peak | 0.87786 |
| clipping_detected | False |
| headroom_safety_valve.applied | False(cause_piece="Voice B body (Erinome)"、peak_before=peak_after=0.8778587、閾値0.98未到達のため未適用) |
| out_path | `er012_output/editorial_b_voices_trial_09_audio/b1b/assembled/Voices_Trial09_B1B_VOICES_TRIAL09.wav` |
| voice_a / voice_b | Algieba / Erinome |

timeline(pause行を除く、開始秒・長さ・part):

| 開始秒 | 長さ | part |
|---|---|---|
| 0.00 | 10.74 | Intro |
| 10.74 | 2.05 | Welcome (Charon) |
| 13.29 | 4.36 | Topic intro (Charon) |
| 18.30 | 2.04 | Notification 1 |
| 20.74 | 1.48 | Preview intro (Charon) |
| 22.87 | 11.36 | Preview (Charon) |
| 34.73 | 2.04 | Notification 2 |
| 37.17 | 2.69 | Key phrases intro (Charon) |
| 40.36 | 8.74 | Key Phrase 1 |
| 49.10 | 7.93 | Key Phrase 2 |
| 57.04 | 9.38 | Key Phrase 3 |
| 66.42 | 7.93 | Key Phrase 4 |
| 74.35 | 9.17 | Key Phrase 5 |
| 83.53 | 2.04 | Notification 3 |
| 85.97 | 2.17 | Full story intro (Charon) |
| 88.94 | 5.28 | Comment 1 (Charon) |
| 95.02 | 9.25 | Hook Part 1: The Question (Aoede, no heading) |
| 104.52 | 11.81 | Hook Part 2: The Question (Aoede, no heading) |
| 117.13 | 11.25 | Comment 2 (Charon, bridge to Voices) |
| 128.88 | 1.78 | Point Notification (Voice A cue) |
| 130.66 | 3.89 | Narrator: One Voice heading (Aoede) |
| 135.25 | 37.26 | Voice A body (Algieba) |
| 173.01 | 1.78 | Point Notification (Voice B cue) |
| 174.78 | 3.74 | Narrator: Another Voice heading (Aoede)(本タスクで再生成) |
| 179.23 | 35.61 | Voice B body (Erinome) |
| 215.64 | 12.60 | Comment 3 (Charon) |
| 229.04 | 30.73 | Tension: Where the Difference Comes From (Aoede) |
| 260.57 | 11.72 | Comment 4 (Charon) |
| 273.09 | 21.76 | Closing: What the Seat Really Means (Aoede, In One Line) |
| 295.65 | 6.14 | Outro (Charon) |

## 4. Gate 7 (a)〜(l) 照合表

player.html: `er012_output/editorial_b_voices_trial_09_audio/player.html`
(`file:///C:/Users/tensh/eigo-radio/er012_output/editorial_b_voices_
trial_09_audio/player.html`)

| 項目 | 判定 | 備考 |
|---|---|---|
| (a) 完成episode音声 | 充足 | 1本化wav(301.795秒)、fallback per-segmentではない |
| (b) Preview | 充足 | timeline行 |
| (c) Comment全件 | 充足 | Comment 1-4全行 |
| (d) 本文全section | 充足 | Hook Part1/2・Voice A/B・Tension・Closing全行 |
| (e) Key Phrase英語+日本語gloss | 充足 | KP1-5をtimeline行+詳細表の両方に表示(表示用/TTS用が同一のため併記省略、差異があれば併記する設計) |
| (f) Intro/Outro/SFX/固定文言 | 充足 | Intro/Notification x3/Point Notification x2/Outroを「効果音(読み上げなし)」「音楽ジングル」と明記、Welcome/Preview intro/Key phrases intro/Full story introは固定テンプレート文言を表示 |
| (g) 実際のsegment order・開始秒・click-seek | 充足 | timeline.json由来の実測開始秒、各行seekボタンでepisode_audioをseek |
| (h) 各segmentの使用voice名 | 充足 | 各行に明記(Charon/Aoede/Aoede (Narrator)/Algieba/Erinome/SFX) |
| (i) レベル別の明確な分離 | 充足 | B1のみ(タイトル・注記に明記、A2は対象外と明記) |
| (j) テキスト未取得は「未取得」と明記 | 充足(該当なし) | 全27行とも実際のcanonical text/固定文言を特定済み。未特定時に「未取得」と表示する分岐は実装済み |
| (k) TTS方式の明記 | 充足 | 冒頭注記に「Standard同期」明記 |
| (l) 再生ボタン+voice+scriptの同一行配置 | 充足 | 全27行をtableの1行に統合(Seekボタン列/Segment名+voice列/Script列/個別音声列/Source列) |

## 5. cost/model/TTSモード

- TTS実行モード: `TTS_EXECUTION_MODE=STANDARD`(本タスクscript冒頭で明示設定、Trial-09と同一)。
- point_two_heading再生成の新規コスト: `cost_delta_jpy_this_call=0.0`
  JPY(1 attemptでPASS、`compute_cost_jpy_so_far()`はTrial-09と同一の
  token課金ベース計算式[Gemini TTS音声出力自体はtoken計上対象外のため
  0円表示、Trial-09本体でも同様の挙動]。予算上限¥100は未到達)。
- Assembly・player.html生成自体はAPI呼び出しを伴わない(ローカル処理のみ)。
- 使用model: TTS=`gemini-2.5-pro-preview-tts`(Aoede、Voice heading)、
  ASR Primary=`gpt-4o-mini-transcribe`。

## 6. SSOT・Governance変更

- `OPEN_ITEMS.md`: OPEN-120行へ本タスクの結果(承認根拠・attempt結果・
  Assembly結果)を追記。新規OPEN-125(entity_like誤分類/delete型diff問題、
  検証Trial起票のみ・未実装、`USER_DECISION_REQUIRED`)を登録。
- `DECISION_LOG.md`: 本タスクのユーザー決定・結果を新規エントリとして追記。
- `docs/pm/PM_GOVERNANCE.md`: §8へ「完了報告後の自動復帰禁止」(同一管理
  IDの成果物への無断作業再開・上書き禁止)を追記、冒頭changelogへも反映。

## 7. USER_DECISION_REQUIRED

完成episode(`player.html`)を実際に試聴した上で、以下をユーザーに判断
してほしい(いずれも未実装・未採用、Production採用ではない):

1. **Voice正式固定**: Voice A=Algieba、Voice B=Erinome、Narrator見出し=
   Aoede固定で問題ないか(候補voiceは技術的には全て利用可能、音質評価は
   ユーザー主観に委ねる)。
2. **Voices Comment Contract採用**: Comment 1-4のTrial限定Prompt(Voices
   Family専用のContract、`VOICES_COMMENT_*_ROLE`)をProduction採用するか。
3. **Tension slot正式追加**: 「Where the Difference Comes From」という
   追加section(Trial-08由来のEXTRA_SEGMENT_NAME)を正式構造へ追加するか。
4. **Key Phrase位置**: 現行はPreview直後(既存B1構造どおり)に据え置いて
   いるが、Closing直後へ移動する解釈もあり得る(Trial-09原Report記載の
   未確定点、本タスクでは変更していない)。
5. **一人称記述**: Voice A/B本文の一人称("I")表現をProduction採用する
   か(Trial-08でVoice B三人称化がGate停止した経緯あり、別途判断が必要)。

再発防止候補(entity_like誤分類/delete型diff問題、OPEN-125)についても、
別Trialでの検証要否をユーザーに判断してほしい(本タスクでは実装していない)。

## 8. 変更ファイル一覧

- `er012_editorial_b_voices_trial_09_heading_regen_03.py`(root、新規)
- `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03_REPORT.md`(root、新規、本ファイル)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/narration/point_two_heading.wav`(再生成)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/narration/attempts/point_two_heading_attempt2_englishstyleprefix.{wav,json}`(新規、attempt保全)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/review_lock_state.json`(point_two_headingがRESOLVEDへ更新)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/tts_generation_results.json`(point_two_headingをOKへ更新)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/user_approval_record_heading_regen_03.json`(新規)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/heading_regen_03_result.json`(新規)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/heading_regen_03_full_run_summary.json`(新規)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/assembled/Voices_Trial09_B1B_VOICES_TRIAL09.wav`(新規、完成episode)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/{timeline,gain_report,headroom_report}.json`(新規/更新)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/run_summary_assemble.json`(更新)
- `er012_output/editorial_b_voices_trial_09_audio/player.html`(全面再生成、Gate 7 (a)〜(l)準拠)
- `OPEN_ITEMS.md`(OPEN-120行追記、OPEN-125新規登録)
- `DECISION_LOG.md`(本タスクのエントリを1件追記)
- `docs/pm/PM_GOVERNANCE.md`(§8「完了報告後の自動復帰禁止」追記、冒頭changelog更新)
- `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(本タスク用に上書き)

Lane Aファイル(`er011_*`、`er006_*.py`、`er003_v1_*`)・Productionコード・
Prompt・Validator本体は一切変更していない(import・関数呼び出しのみ)。
`er012_editorial_b_voices_trial_09_audio.py`自体も編集していない
(importして既存関数を呼ぶだけ)。Git操作は実施していない(Fableが統合)。
