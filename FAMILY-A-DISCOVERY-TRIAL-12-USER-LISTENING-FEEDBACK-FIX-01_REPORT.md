# FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01_REPORT.md

管理ID: FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01
対象: `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/`
2026-09-13ユーザー視聴Feedback(個別対応、**新しい一般仕様にはしない**)への対応。

## 1. 何が問題だったか(ユーザー視聴Feedback、2026-09-13)

1. 標準player・過去REPORTのユーザー向け表記が「B1B」のままだった(「B1B」は内部実装由来の表記であり、ユーザー向け表記は「B1」に統一すべき)。
2. A2 Comment 2の日本語が「決めた時間**に近く**起きられることはあるのでしょうか。」となっており、ユーザーの希望する言い回し「決めた時間**近くに**起きられることはあるのでしょうか。」と異なっていた。

## 2. 何を変更したか

### 2.1 Comment 2文言差替(A2、日本語)
- `a2_support_texts.json`の`comment_2`を差替。バックアップ: `a2_support_texts.json.backup_before_userfix_20260913_073407.json`。
  - 旧: 「ここまでで、体内時計は光や決まった生活リズムに合わせて動くことが分かりました。では、外から合図がなくても、決めた時間**に近く**起きられることはあるのでしょうか。」
  - 新: 「ここまでで、体内時計は光や決まった生活リズムに合わせて動くことが分かりました。では、外から合図がなくても、決めた時間**近くに**起きられることはあるのでしょうか。」
- 新規script `er011_wake_before_alarm_trial12_a2_comment2_userfix_01.py`(本タスクで新規作成)から、既存Production関数`tts_gen.generate_a2_japanese_with_reading_safety()`(`generate_a2_segments()`内でcomment_1〜4に使われているものと完全に同一の呼び出し)をcomment_2のみに対して直接呼んだ。新規ロジック・新しいTTS/ASR経路は作っていない。TTS Retry Cascade・Human Review Lock(`review_lock_state.json`)は既存機構がそのまま自動で読み書きした(バイパスなし)。
- 結果: **1回目attemptでPASS**(`status=OK`、`asr_verified=True`、`audio_classification=PHONETIC_MATCH`)。ASR書き起こし「...決めた時間近くに起きられることはあるのでしょうか?」で新文言と一致(「分かりました/わかりました」の漢字・かな表記ゆれのみ、既存PHONETIC_MATCH判定で許容範囲、内容差ではない)。
- **OPEN-145 JA表記ゆれ層(orthographic variant layer)の発火**: `reading_resolver_info=None`。数字を含まない文のため、OPEN-145層(数字の位取り正規化)の対象ケースに該当せず、**発火なし**(通常のPHONETIC_MATCH判定段階で解決)。
- `review_lock_state.json`のcomment_2エントリ: `state=RESOLVED`, `final_status=OK`, `cumulative_tts_attempts=1`, `cumulative_asr_calls=1`(既存機構が自動更新、手動編集なし)。
- `tts_generation_results.json`のsegments.comment_2、`run_summary_tts.json`のsegment_status.comment_2を新結果へ同期(バックアップ保存済み、他13segmentは無変更)。
- **他segmentへの影響なし**: full_story_part1等10segmentのnarration wav sha256を差替前後で比較し、**全て不変**であることを確認済み(evidence参照)。A2英語Full Storyの6% slowdown post-processは既適用のままであり、**再適用不要と確認**。

### 2.2 A2 Assembly(Audio Validation Gate)再実行
- 既存Production関数`run.assembly_stage("a2")`(内部で`asm.stage_assemble_a2()`→`asm.verify_episode_audio_validation_gate()`)をそのまま呼び、comment_2.wav差替を反映した`assembled/English_Your_Way_A2_...wav`を再生成。
- 結果: **Gate OFF経路PASS / Gate opt-in ON経路PASS**(共に既存判定どおり、独自の緩和・回避なし)。duration=327.0s(旧327.24s、comment_2短縮分-0.24s)、peak=0.89889、clipping=False。

### 2.3 標準player再生成+表示ラベル統一
- `er011_wake_before_alarm_trial12_std_player_01.py`のHTML出力文字列(ユーザー向け表示のみ、ファイル名・内部変数・関数名`build_b1b_section`等は無変更)を「B1B」→「B1」へ修正(見出し・タイムライン見出し・Key Phrase見出し・記事全文見出し・note文中の表記、計6箇所)。
- 古い`comment_2.mp3`/`a2_episode.mp3`(差替前wav由来のキャッシュ)を削除してから再生成スクリプトを実行し、新音声を反映したmp3へ差し替え済み(sha256的に新規ファイル、新規変換・TTS再生成ではない)。
- `player_std/index.html`を再生成。Comment 2行のScript列が新文言に更新されていることを確認済み。

## 3. 何が改善されるか

- ユーザー指摘の2点(表示ラベル「B1B」→「B1」、Comment 2文言)が両方反映され、既存の安全機構(Human Review Lock・Audio Validation Gate)を経由した検証済み状態で提示できる。
- 他segment・他レベル(B1)は一切変更していないため、既存VALIDATED判定への影響はない。

## 4. リスクや注意点

- 本修正は**個別対応**であり、新しい一般仕様・Production正式ルールとしては追加していない。
- **記事はユーザー再視聴待ちのまま未close**(`USER_LISTENING_PENDING`維持)。本タスクはProduction採用判断を一切行っていない。
- Git commit/pushは実施していない(本タスクの制約により後続統合タスクで実施)。

## 5. TTS+ASR検証結果(comment_2、詳細)

| 項目 | 値 |
|---|---|
| attempt数 | 1(標準経路1回目でPASS、リトライ・fallbackなし) |
| status | OK |
| asr_verified | True |
| audio_classification | PHONETIC_MATCH |
| OPEN-145層発火 | なし(数字非含有のため対象外) |
| duration_seconds | 13.68s(旧13.92s) |
| sha256(新comment_2.wav) | `0b604b9a33c3784ca98059aacc0ec3c55b82b3c4b058cf1663bcee359db44c7f` |
| Human Review Lock | RESOLVED / OK(既存機構が自動更新) |

## 6. Assembly結果

| 項目 | 値 |
|---|---|
| Gate OFF経路 | PASS |
| Gate opt-in ON経路 | PASS |
| duration_seconds | 327.0(旧327.24) |
| peak | 0.89889 |
| clipping_detected | False |
| headroom safety valve | 未適用(applied=false、旧同様) |
| full_story_part1等・対象外10segment | sha256全一致(不変確認済み) |

## 7. 費用(5区分、今回/Trial-12累計)

TTS_EXECUTION_MODE=STANDARD(同期呼び出し)で実行。既存`AUDIO_COST_LOG_PATH`(raw_usage_log_audio_01.jsonl)へ追記のみ(既存記録の上書きなし)、`compute_cost_jpy_so_far()`(既存Production関数)で前後比較。

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| ①今回実測合計(実際の実行経路=Standard同期) | **1.55** | comment_2 TTS 1回+ASR 1回(gemini +1.48, openai_asr +0.07) |
| ②今回実測(公式script報告値、`compute_cost_jpy_so_far`差分) | 1.55 | ①と同値(訂正不要) |
| ③量産想定(Batch適用時、机上換算・未実行) | 約0.81 | gemini分(¥1.48)をBatch tier(Standardの50%)換算+openai_asr分(¥0.07、Batch非対象)。実行はしていない |
| ④retry/Human Review由来の上振れ分(内数) | 0.00 | 1回目attemptで即PASS、リトライ発生なし |
| ⑤参考: 通常運用相当分(①-④) | 1.55 | 異常対応コストなし、全額が本修正に必要な実額 |

**Trial-12累計(本タスク反映後)**: audio側`compute_cost_jpy_so_far()`実測合計 **¥64.25**(a2=35.75, b1b=25.93, other=2.57、本タスク前は¥62.70)。記事生成側(既存・別タスク、無変更)¥78.98と合算した管理ID全体は **¥143.23**(上限¥300に対し47.7%、超過なし)。

## 8. 標準player監査(Gate 7補足(a)〜(m)、`docs/pm/PM_GOVERNANCE.md` 2節)

| 項目 | 判定 | 備考 |
|---|---|---|
| (a) 完成episode音声 | ○ | A2/B1とも`episode_audio_a2`/`episode_audio_b1b`、mp3化済み |
| (b) Preview | ○ | A2/B1双方に個別音声+Script列あり |
| (c) Comment全件 | ○ | A2 comment_1〜4全件、Comment 2は新文言で反映 |
| (d) 本文全section | ○ | full_story_part1/2・point_one/two等、既存構造どおり掲載 |
| (e) Key Phrase英語+日本語gloss | ○ | 「A2 Key Phrase表」「B1 Key Phrase表」あり |
| (f) Intro/Outro/SFX/固定文言 | ○ | Intro/Welcome/Notification等の固定行あり |
| (g) 実際のsegment order・開始秒・click-seek | ○ | timeline.json由来のstart secondsでSeekボタン生成、`addEventListener`スクリプトあり |
| (h) 各segmentの使用voice名 | ○ | 各行に`voice=Aoede/Charon`等を明記 |
| (i) A2/B1レベル別の明確な分離 | ○ | `<h2>A2 —`/`<h2>B1 —`で分離、`data-audio-target`でSeek scope分離 |
| (j) テキスト未取得segmentの明記 | ○ | 該当なし(「未取得」表記が必要な欠落segmentは0件) |
| (k) Standard/Batch等TTS方式の明記 | △ | B1セクションに`TTS_EXECUTION_MODE=STANDARD`明記(既存)。A2セクションのnote文には同文言が literal には無いが、本REPORT 7節で明記(pre-existing、本タスクでは触れていない箇所) |
| (l) 再生ボタンとscriptの同一行/直近配置 | ○ | 各行`<td class="txt">`直後に`<audio>`要素 |
| (m) ユーザー環境から実際に開けるリンク | ○ | 全リンクGitHub raw絶対URL(`file:///`は0件)。push後にHTTP到達確認が必要(本タスクでは未push、後続統合タスクで実施) |

Seek動作: `scoped_seek_script`(`data-audio-target`属性でA2/B1を分離してseekボタンのclickをbind)が生成HTMLに1回のみ出力されていることを確認済み(`addEventListener`出現2回=定義1箇所+使用、既存ロジック無変更)。

## 9. 変更ファイル一覧

**編集(既存Production/Trial成果物)**
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/a2_support_texts.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/tts_generation_results.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/run_summary_tts.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/review_lock_state.json`(既存機構が自動更新)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/assembly_and_gate_summary_audio_01.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/timeline.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/gain_report.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/run_summary_assemble.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/audit/cost_summary_audio_01.json`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/audit/raw_usage_log_audio_01.jsonl`(追記のみ)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/narration/comment_2.wav`(gitignore対象、*.wav)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/assembled/English_Your_Way_A2_DISCOVERY_GENERALIZATION_WAKE_BEFORE_ALARM_TRIAL_12.wav`(gitignore対象、*.wav)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/index.html`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/audio_mp3/a2/comment_2.mp3`
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/audio_mp3/a2_episode.mp3`
- `er011_wake_before_alarm_trial12_std_player_01.py`(B1B→B1表示ラベル修正、6箇所)

**新規作成**
- `er011_wake_before_alarm_trial12_a2_comment2_userfix_01.py`(本タスク専用fix script)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/user_listening_feedback_fix_01/userfix_evidence.json`(実行evidence)
- バックアップ3件(`.backup_before_userfix_20260913_073407.{json}`、a2_support_texts.json/tts_generation_results.json/run_summary_tts.json)
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/narration/attempts/comment_2_attempt2_standard.{json,wav}`(attempt履歴、既存retention仕様どおり)

**未commit**: 本タスクではGit操作を行っていない(管理ID指示によりGit操作禁止)。後続の統合タスクでcommit・push予定。

## 10. OPEN_ITEMS.md(OPEN-135 Discovery行)追記文案

以下はSSOT編集担当(Fable)向けの追記案であり、本タスクではOPEN_ITEMS.mdを編集していない。

> **追記(2026-09-13、FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01)**: ユーザー視聴Feedback(個別対応、新しい一般仕様ではない)を受け、Trial-12 A2 Comment 2の日本語文言を差替(「決めた時間に近く起きられることはあるのでしょうか。」→「決めた時間近くに起きられることはあるのでしょうか。」)。既存Production関数(`generate_a2_japanese_with_reading_safety`)をそのまま呼び出しcomment_2のみTTS再生成(1回目attemptでPHONETIC_MATCH・ASR検証PASS、Human Review Lock発火なし、OPEN-145 JA表記ゆれ層は数字非含有のため対象外)。他13segment(`full_story_part1`含む)は一切変更なし(sha256一致で確認)。A2 Assembly(Gate OFF/opt-in ON両経路)PASSを再確認。標準player(`player_std/index.html`)のユーザー向け表示ラベルを「B1B」→「B1」へ統一(ファイル名・内部IDは無変更)。本タスク増分費用は約¥1.55(Trial-12 audio側累計¥64.25、記事+Support/Audio合算¥143.23、上限¥300以内)。**A2/B1とも技術的完成のままであり、Production採用判断は行っていない。ユーザー再視聴待ち(`USER_LISTENING_PENDING`)は継続、close未了**。根拠: `FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01_REPORT.md`。

## 11. 試聴用リンク(push後に有効、本タスクでは未push)

`https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/index.html`
