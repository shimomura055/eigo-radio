# FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05 REPORT

日付: 2026-09-15
管理ID: `FAMILY-C-HOME-ROBOTS-B1-SUPPORT-VOICE-FIX-05`
対象: Family C / Home robots B1(Trial)のみ。A2 v2・Trend・Discovery・Voices・
OPEN-154/155は対象外(無変更)。

## 1. 目的・ユーザー正式判断

ユーザー試聴で判明したB1 Preview/Comment 1〜3のVoice不整合を修正する。
ユーザー正式判断(2026-09-15): B1の既存正式仕様(CURRENT_SPEC「B1 Voice」節、
Navigator/Support=Charon)どおり、Preview=Charon/Comment 1=Charon/Comment 2=
Charon/Comment 3=Charon/Robot=Charonとする。現在のAoede使用(修正1回目
[FIX-04]でnarrator維持した判断)は不採用。Family CでRobotもCharonであることを
理由にSupport voiceを別voiceへ変えない(同一Charonで可)。

## 2. 修正前Voice → 修正後Voice(4 segment)

| segment | 修正前 | 修正後 | 修正前evidence | 修正後evidence |
|---|---|---|---|---|
| preview_en (Preview) | Aoede(narrator)、`v2run.tts_narrator` | Charon(support)、`v2run.tts_robot`→`voice01.generate_charon_english` | player.html: "Aoede(narrator)"行(Preview row) | player.html: "Charon(support)"行 |
| comment_1_ja (Comment 1) | Aoede(narrator) | Charon(support) | 同上 | 同上 |
| comment_2_ja (Comment 2) | Aoede(narrator) | Charon(support) | 同上 | 同上 |
| comment_3_ja (Comment 3) | Aoede(narrator) | Charon(support) | 同上 | 同上 |
| story_017 (Robot、参考・無変更) | Charon(robot) | Charon(robot)(無変更) | segments.json voice="robot" | 同一(sha256/mtime完全一致) |

Grep結果(`er013_output/.../home_robots_b1/*.{json,html,md}`内`Aoede`):
- 修正前: player.html内「Aoede(narrator)」40件(Story narrator segments +
  Topic intro/Japanese title + **Preview/Comment 1〜3の4件を含む**)。
  speaker_map.json内1件(Mayaの台詞に関する記述コメント、対象外・正常)。
- 修正後: player.html内「Aoede(narrator)」36件(40−4、対象4件のAoedeは
  すべて解消)、新規「Charon(support)」4件(Preview1+Comment3)。
  speaker_map.json内のAoede記述コメントは無変更(正常、Maya台詞の話者設計
  説明であり今回の対象外)。旧player.html(`player_prev_support_aoede.html`)
  へ退避したものを除き、現行player.htmlに対象4segmentのAoede残存は**0件**。

## 3. canonical text不変確認

- `comments_en.md`・`preview_en.txt`は`git diff`で**差分なし**(バイト単位で
  実行前後一致、コミット済み内容と同一)。
- `tts_generation_results.json`のcanonical_text(4segment)は文言不変
  (curly apostropheを含め一致、下記4節参照)。

## 4. Charonであるruntime evidence

- 実装: `er013_family_c_episode_trial_09b_b1_run.py`に`--support-voice-charon`
  フラグを新設。Comment 1〜3・PreviewのTTS呼び出しを`v2run.tts_narrator`から
  `v2run.tts_robot`(`voice01.generate_charon_english`、Robot`story_017`と
  同一関数)へ切替。
- `raw_usage_log.jsonl`本実行分(2026-09-15T19:17:56〜19:18:52)のtts記録4件:
  `comment_1_ja`(19:17:56)/`comment_2_ja`(19:18:09)/`comment_3_ja`(19:18:24)/
  `preview_en`(19:18:46)、すべて`kind=tts, meta.status=OK`。
- `audit/tts_generation_results.json`のsha256は4segmentとも`None`(Robotと
  同一のTTS関数`generate_charon_english`が元々sha256フィールドを返さない
  実装のため。story_017も同様に`sha256=None`、既存仕様どおりで異常ではない)。

## 5. sha256不変確認(4 segment以外)・story_017回避bypass

- 実行前に全69 wavのsha256/mtimeを`fix05_pre_sha.json`へ保存。実行後比較:
  **同一65件、差分4件**(comment_1_ja/comment_2_ja/comment_3_ja/preview_en
  のみ変化)。story_017を含む他65件は完全一致。
- story_017: `--fix-robot-choice-second-person`は指定するたび無条件で
  wav+.okを削除し再TTSする既存実装(非冪等、ユーザー指示8で別タスク)のため
  再指定せず、本タスク限定bypass`--keep-robot-audio`を新設(tts_text/voice
  メタデータのみ二人称固定文/robotへ復元し、既存wav+.okは削除しない)。
  結果: sha256`701057d0...4332c037`・mtime`1789461276.577...`が実行前後で
  **完全一致**(再TTSされていないことを確認)。

## 6. ASR結果(現物音声、4/4 match=true)

`player_display_audio_consistency.json`(実行後、当該4segmentは名前ベース
キャッシュをbypassして必ず`v2run.asr_diag()`を新規実行、cache-hit無し):

- `preview_en`: canonical/ASRとも "This story is about Maya and a robot
  that has planned many parts of her daily life...no clear answer." で
  完全一致。match=**true**
- `comment_1_ja`: canonical "Listen for how the robot makes Maya's everyday
  choices and what happens when her mother asks her to choose."、ASR
  "...choices, and what happens..."(コンマの有無のみ差、正規化後一致)。
  match=**true**
- `comment_2_ja`: canonical/ASRほぼ同一(ASRのみ"Now, she"とコンマ挿入)。
  match=**true**
- `comment_3_ja`: canonical/ASR完全一致(apostrophe種別差のみ)。match=**true**

`comment_consistency.json`(Comment 1〜3、別経路の検証): 3/3 match=**true**。

`raw_usage_log.jsonl`本実行分の`asr_diag`エントリ: 4件
(`preview_en_asr_diag`/`comment_1_ja_asr_diag`/`comment_2_ja_asr_diag`/
`comment_3_ja_asr_diag`、他segment分は0件)。

## 7. Audio Validation・Consistency

- `audio_validation.json`: `status=PASS`、`level=FAMILY_C_TRIAL_09B_B1`。
- duration=**395.105秒**(前回393.375秒から+1.73秒、再TTS音声の尺差分)。
- player script/audio consistency: 上記6節のとおり全件match=true。

## 8. 回帰結果

`run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"`
→ collected=**71** passed=**71** failed=0 errors=0 skipped=0(既存69件+新規2件:
`test_support_segments_use_charon_voice`/`test_support_voice_flag_uses_robot_tts_path`)。

A2 v2 artifact無変更確認: `git status --porcelain
er013_output/family_c_episode_trial_09/home_robots_v2/` → 出力なし(空、無変更)。

## 9. 費用

`raw_usage_log.jsonl`実測値(本実行分のみ):
- TTS: ¥3.60(4件×¥0.90)
- ASR: ¥1.20(4件×¥0.30)
- その他(LLM等): ¥0
- **合計: ¥4.80**(費用上限¥10以内)

Family C累計: ¥285.00 + ¥4.80 = **¥289.80**

(`cost_summary.json`の`total_estimate_jpy`は全履歴累計の安全側推定[119.1→
125.4]であり、本実行分の実測差分¥6.3とは単価推定方式の違いによりわずかに
異なる。実費報告は`raw_usage_log.jsonl`の実測値¥4.80を正とする。)

## 10. player URL・direct audio URL・Web到達確認

- player: `https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html`
- direct audio (episode mp3): `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/web/family_c_home_robots_trial_09b_b1.mp3`
- Web到達確認: push後に別途確認しHTTP status結果を`docs/pm/RESULT_PACKET.md`
  に記録。

## 11. unresolved issue

- ユーザー指示8の4件(Trial script非冪等再生成/ASR cache名前キー/引用符なし
  Robot話者判定/A2退避上書き)は本タスクで恒久修正していない(別タスク扱い)。
  本タスクでの影響: (1)`--comments-en`再指定時のComment 1〜3無条件再TTSは
  今回の変更対象4segmentの範囲内で発生したため実害なし。(2)ASR cache名前
  キー問題は当該4segmentをコード側で明示的にbypassして直接再ASRすることで
  回避した(恒久修正はしていない)。(3)story_017は`--keep-robot-audio`
  bypassで回避、sha256/mtime完全一致を確認。(4)A2退避上書きは本タスクで
  A2側artifactに一切触れていないため非該当。
- STOP条件(1)〜(6)いずれも非該当。

## 12. final status

- Family C B1: **VALIDATED候補 / Trial / USER_LISTENING_PENDING**
  (Production未採用、不変)。ユーザー再試聴待ち。
- Family C A2 v2: ユーザー試聴OK済み・無変更(本タスクで一切変更なし)。

## 13. ユーザー再試聴用URL(Family C B1、1本のみ)

`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html`
