# RESULT_PACKET — USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(CONT1)

管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(継続CONT1、
Fable修正指示1回目: Comment 3主語明確化)

## 1) 最終Status

**VALIDATED候補(Trial、ユーザー試聴待ち)**。Audio Validation Gate:
**PASS**(`audio_validation.json`、緩和なし)。Production採用判断はしない
(禁止事項どおり)。決定的テスト**24件全件PASS**
(`er013_family_c_episode_trial_09b_b1_test_01.py`、23件既存+新規1件)。

## 2) Comment 3(旧→新)

- 旧: 「お金や仕事、睡眠、安全について答えても、今回はロボットのいつもの
  やり方だけでは答えが見つからないようです。」(誰が問いかけ誰が答えたか
  曖昧、A2 v2でユーザーが指摘した問題と同種、`comments_ja_prev.md`へ退避)。
- 新: 「ロボットがお金や仕事、睡眠、安全について問いかけ、マヤは一つずつ
  答えましたが、今回はいつものようにロボットが最適解を示してくれること
  はありませんでした。」(主語「ロボットが」/「マヤは」を明示、B1本文
  story_035「The robot asked about money, work, sleep, and safety.
  Maya answered each question, but the two plans remained on the wall.
  No answer became the right one.」の語順・内容と一致、Fact不変)。
- TTS: 既存経路(`v2run.tts_narrator`→`generate_narration_snippet_
  verified_strict`、Aoede、既存retry構成)、1 attemptでstatus=OK
  (`raw_usage_log.jsonl`実測、新規記録1件のみ)。
- ASR一致: `comment_consistency.json` comment=3、match=**true**(TTS生成
  時の内部ASR結果をそのまま使用、追加ASR診断コールは発生せず)。
- player表示一致: `player_display_audio_consistency.json`
  segment_id=comment_3_ja、match=**true**。player.html本文も新文に
  更新済み(目視確認)。

## 3) Audio Validation・duration・mp3/player/予定URL

- Gate: **PASS**。duration=**388.502秒**(旧383.672秒から+4.83秒、Comment
  3の尺が9.82秒→14.65秒[+4.83秒]へ伸びた差分とちょうど一致)。
  peak_before/after_headroom=0.8639(headroom_applied=false、変化なし)。
- episode mp3: `er013_output/family_c_episode_trial_09/home_robots_b1/
  web/family_c_home_robots_trial_09b_b1.mp3`(4,231,464 bytes、更新)。
  旧mp3/wavは`web/prev/family_c_home_robots_trial_09b_b1_pre_comment3_
  fix.{mp3,wav}`へ退避(削除せず保持)。旧player.htmlは
  `player_prev_pre_comment3_fix.html`へ保存。
- player: `er013_output/family_c_episode_trial_09/home_robots_b1/
  player.html`(相対パスのみ、`file:///`/`C:\`検出0件、`level=B1)`表記
  あり)。
- 予定player URL(commit・push後、本タスクではGit操作なし):
  `https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html`

## 4) consistency結果・Story本文不変

- Comment 1〜3全件match=true(`comment_consistency.json`)。Comment 1/2は
  内容不変のため既存comment_consistency.jsonのasr_textキャッシュを再利用
  (追加ASR診断コールなし)。
- `player_display_audio_consistency.json`: comment_3_jaのみ新規ASR照合、
  他全件(story 44件・nav/preview/key phrase等)は既存artifactのasr_text
  キャッシュを再利用(`--reassemble`)、新規ASRコールなし。
- `article_audio_consistency.json`: Story本文は無編集のため再実行しても
  内容不変(method/story_segment_concat_tts_text/article_normalized_text
  すべて同一)。`word_count.json`も597語で不変(Story側に変更なし)。
- `key_phrase_consistency.json`: 変更なし(既存キャッシュ再利用、5件とも
  再ASRなし)。

## 5) テスト件数

`run_project_regression.py --pattern "er013_family_c_episode_trial_09b_
b1_test_*.py"`: **collected=24 passed=24 failed=0 errors=0 skipped=0**
(既存23件+新規1件`test_comment3_fixed_text_override_states_explicit_
subjects`、Comment 3固定文が「ロボットが」「マヤは」を明示的に含むこと・
旧曖昧文と異なることを検証)。

## 6) 費用

本タスク実測差分: **¥0.90**(comment_3_ja TTS 1件のみ、
`raw_usage_log.jsonl`該当runの新規レコードは1件のみ、既存¥5.00上限の
範囲内で大幅未達)。低コスト化の内訳: Comment 1/2/Preview/Key
Phrase/Story全segmentは`_resumable_reuse()`+本タスクで追加した
ASRキャッシュ機構(`_load_prior_seg_asr_cache`/`_load_prior_comment_
asr_cache`/`_load_prior_kp_asr_cache`、v2の`--reassemble`機構と同一方針を
B1へ新規実装)により再TTS・再ASRともに発生せず。**開発・Trial/検証費として
記録**。

Family C累計(ユーザー提示の加算式どおり、本タスクでは独立再検証していない
参考値): ¥148.50 + ¥0.90(A2 Comment3修正) + ¥85.20(B1初回Trial) +
¥0.90(本タスク) = **¥235.50**。予算枠¥133.99に対する超過額 = **¥101.51**
(既にFix-02/A2時点で発生済みの超過が継続、本タスクの追加寄与は¥0.90のみ)。
正確な累計再集計はSSOT(OPEN-147)側の管理事項であり本タスクでは実施していない。

## 7) commit対象候補一覧(サイズ込み、wav除外・mp3必須、前回分含む)

新規/更新コード:
- `er013_family_c_episode_trial_09b_b1_run.py`(更新、62,487 bytes、
  `--fix-comment3`/`--reassemble`フラグ+ASRキャッシュ機構+web/prev退避
  ロジック追加)
- `er013_family_c_episode_trial_09b_b1_test_01.py`(更新、10,320 bytes、
  テスト1件追加)

更新生成物(`home_robots_b1/`配下):
- `player.html`(23,753 bytes)、`player_prev_pre_comment3_fix.html`
  (新規、23,684 bytes)
- `comments_ja.md`(531 bytes、更新)、`comments_ja_prev.md`(新規、462 bytes)
- `comment_placement.json`(2,189 bytes、note追記+comment3 duration更新)
- `comment_consistency.json`(2,355 bytes)、
  `player_display_audio_consistency.json`(27,026 bytes)、
  `article_audio_consistency.json`(6,946 bytes、内容不変)
- `audio_validation.json`(79 bytes)、`cost_summary.json`(664 bytes)
- `web/family_c_home_robots_trial_09b_b1.mp3`(更新、4,231,464 bytes、必須)
- `web/prev/family_c_home_robots_trial_09b_b1_pre_comment3_fix.mp3`
  (新規、4,180,848 bytes)
- `web/segments/comment_3_ja.mp3`(更新、102,864 bytes)
- `audit/tts_generation_results.json`(26,956 bytes)、
  `audit/run_summary_assemble.json`(13,671 bytes)、
  `audit/gain_report.json`(9,299 bytes)、
  `audit/headroom_report.json`(183 bytes)

T-0記録:
- `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-
  FAMILYC-B1-CONT1.md`(7,983 bytes)+`_check.json`(1,049 bytes)
- 本ファイル`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1_2.md`

前回(初回Trial)分の未commit候補は`docs/pm/RESULT_PACKET_FU03_FAMILYC_
B1.md`11節を参照(本タスクでは変更していない)。

除外(`.gitignore`の`*.wav`、`git check-ignore`実測exit=0で確認):
`home_robots_b1/audio/comment_3_ja.wav`(更新)・
`home_robots_b1/assembled/family_c_home_robots_trial_09b_b1.wav`(更新)・
`home_robots_b1/web/prev/family_c_home_robots_trial_09b_b1_pre_comment3_
fix.wav`(新規、73,665,004 bytes、mp3で代替済み)。episode mp3は
`git check-ignore`実測exit=1(除外されない、commit必須)を確認。

## 8) T-0・事前指定外Read・STOP有無

- T-0: `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-
  03-FAMILYC-B1-CONT1_check.json` → **status=PASS**(reasons無し)。
- 事前指定外Read: `er013_family_c_episode_trial_09b_run.py`の
  `_resumable_reuse`/`_mark_ok_if_success`/`tts_narrator`等の実装詳細
  (行383-497、事前指定Grep一覧の範囲外)を確認するために追加Read。
  理由: B1側に`--fix-comment3`/`--reassemble`相当の低コスト再Assembly
  機構を新規実装する必要があり、v2の`_load_prior_asr_cache`等の設計を
  正確に踏襲するには、reuse判定・.okマーカー方式の実装詳細を確認する
  必要があった(委任文Read一覧の範囲だけでは実装できなかったため)。
  `er013_family_c_episode_trial_09b_run.py`は本タスクでは**一切編集して
  いない**(import/参照のみ、禁止事項どおり)。なお同ファイルは`git
  status`上"M"(modified)と表示されるが、これは本タスク開始前の別タスク
  (A2 Comment3修正)による未commit差分であり、本タスクによる変更ではない
  (本セッション内でEdit/Write未実行のパスであることを確認済み)。
- 事前指定外Read(2): `er003_v1_repro01_main_generate.py`の
  `generate_narration_snippet_verified_strict`が返り値に`asr_text`を
  含むことの確認(Stage K/Lのキャッシュ設計で、新規TTS結果に追加ASR
  診断コールが不要であることを確認するため)。
- STOP: **なし**(Human Review Lock到達なし、Gate緩和不要、費用¥0.90で
  上限¥5内に収まった)。

## 9) SSOT追記案(OPEN-147末尾、本タスクではSSOT自体は未編集)

「2026-09-15追記: Family C B1のComment 3も、A2 v2と同種の主語曖昧問題
(誰が問いかけ誰が答えたかが不明瞭)をFable照合で検出し、ユーザー指定文と
同趣旨(主語「ロボットが」「マヤは」明示)へ修正済み(USER-TEST-FOLLOWUP-
AND-SPEC-TRACEABILITY-03-FAMILYC-B1 CONT1、詳細は`docs/pm/RESULT_PACKET_
FU03_FAMILYC_B1_2.md`)。Comment位置は不変。B1 scriptに`--fix-comment3`/
`--reassemble`(v2と同一方針の低コスト再Assembly機構)を新規実装した。」

## 実行ログ(要約)

1. T-0保存+check_delegation_prompt.py実行 → PASS。
2. `er013_family_c_episode_trial_09b_b1_run.py`へ`COMMENT_3_FIXED_TEXT_
   OVERRIDE`定数・`--fix-comment3`/`--reassemble`フラグ・stale音声無効化・
   ASRキャッシュ3種(`_load_prior_seg_asr_cache`/`_load_prior_comment_asr_
   cache`/`_load_prior_kp_asr_cache`)・web/prev退避ロジックを追加。
3. `er013_family_c_episode_trial_09b_b1_test_01.py`へテスト1件追加。
4. `run_project_regression.py --pattern "er013_family_c_episode_trial_
   09b_b1_test_*.py"` → 24 passed。
5. `.venv/Scripts/python.exe er013_family_c_episode_trial_09b_b1_run.py
   --fix-comment3 --reassemble --budget-jpy 5` → `[DONE]
   duration=388.502s gate=PASS cost_estimate=Y86.10 word_count=597`
   (86.10は`raw_usage_log.jsonl`全体の累計、本run差分は¥0.90)。
6. 生成物確認(Gate PASS、consistency全件match、player.htmlパス検証、
   git check-ignore実測)。
