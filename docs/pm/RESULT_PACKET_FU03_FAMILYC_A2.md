# RESULT_PACKET — USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2

## 1) 最終Status

**VALIDATED候補(ユーザー再試聴待ち)**。Audio Validation Gate: PASS
(`home_robots_v2/audio_validation.json`)。Family C全体はまだ
Production正式path未承認(`APPROVED_FOR_PRODUCTION`は人間ユーザーのみが
決定)。

## 2) Comment 3

- 旧: 「お金や睡眠、仕事、安全について聞いても、今回はロボットのいつもの
  方法では答えが見つからないようです。」(誰が質問したか曖昧)
- 新(ユーザー原文をそのまま採用、微調整なし): 「お金や睡眠、仕事、安全に
  ついてロボットが問いかけ、マヤは答えましたが、今回はいつものように
  ロボットが最適解を示してくれることはありませんでした。」
- 根拠確認: 記事本文 "The robot asked about money, sleep, work, and
  safety. Maya answered. Still, no answer came." と一致(Fact通り)。
- TTS: 既存経路(`tts_narrator`→`generate_narration_snippet_verified_
  strict`、Aoede)、1 attemptでstatus=OK(`raw_usage_log.jsonl`実測)。
- ASR一致: `comment_consistency.json` comment=3、match=true(ASR実測が
  新文と完全一致)。
- player表示一致: `player_display_audio_consistency.json`
  segment_id=comment_3_ja、match=true。

## 3) Comment 4削除

`COMMENT_NUMBERS=(1,2,3)`を既定化(`er013_family_c_episode_trial_09b_
run.py`)、Comment 4関連コード(role文言・segment・consistency・
placement・player表示)を全削除。Assembly末尾は「Story→pause(0.5秒、
A2既存値)→Outro」(Comment4→Outro遷移で使っていたpause_0.5秒をそのまま
適用、直前のpause_1.0_en_to_jaは不要になったため削除)。旧comments_ja.md
(Comment1-4)は`comments_ja_prev.md`へ保存。恒久仕様は`home_robots_v2/
spec/episode_spec_v2.md`に記録(Comment 4なし・位置決定原則
[semantic break/scene transition/turning point/前後text volume/前後
audio duration]、B1側も同構成を採用すべき旨)。

## 4) Audio Validation・duration・mp3/player

Gate: PASS。duration=315.573秒(旧319.593秒から-4.02秒、Comment3が
9.22秒→12.84秒[+3.62秒]・Comment4区間[pause1.0+本体6.64+pause0.5=
8.14秒]削除+新pause0.5秒[-7.64秒]の差分と整合)。
episode mp3: `home_robots_v2/web/family_c_home_robots_trial_09b.mp3`
(3.44MB)。旧wav/mp3は`home_robots_v2/web/prev/family_c_home_robots_
trial_09b_comment4.{wav,mp3}`へ退避(削除せず保持)。旧player.htmlは
`home_robots_v2/player_prev_comment4.html`へ保存(上書き、履歴保持なし)。
player.html: `file:///`/`C:\`/`C:/Users`検出0件(Select-String相当、grep -c
で確認)。予定URL(未commitのため現状404):
player=`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html`、
episode mp3=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3`。

## 5) consistency結果・Story本文sha256

`article_unchanged_sha256.json`: v1=v2=
`ee45d0b608c565cbf6a11e7178a2eb6e955bdbaeddc392d8c2e3477e6300ded1`
(identical=true、Story本文不変)。`player_display_audio_consistency.json`:
35行(旧36行からcomment_4行削除)。comment_1_ja/comment_3_ja match=true。
comment_2_ja match=false(既存の既知差分、「この後」漢字 vs 「このあと」
平仮名、読み同一・意味不変、今回は未変更のため前回の記録をそのまま
キャッシュ再利用)。他のstory/key phrase/nav行は前回結果をキャッシュ
再利用(内容不変のため再ASR診断していない、8節参照)。

## 6) script/テスト変更・PASS件数

`er013_family_c_episode_trial_09b_run.py`: `COMMENT_NUMBERS=(1,2,3)`
既定化、`COMMENT_3_FIXED_TEXT_OVERRIDE`追加、`--fix-comment3`/
`--drop-comment4`/`--reassemble`の3フラグ追加、既存artifactのASR
キャッシュ再利用機構(`_load_prior_asr_cache`/`_load_prior_comment_asr_
cache`)追加、Assembly/consistency/placement/player生成の全Comment関連
箇所をCOMMENT_NUMBERS駆動へ変更。`er013_family_c_episode_trial_09b_test_
01.py`: `CommentStructureTests`(2件: Comment4不在、Comment3固定文一致)
追加。`run_project_regression.py --pattern "er013_family_c_episode_
trial_09b_test_*.py"`: **collected=18 passed=18 failed=0 errors=0
skipped=0**。

## 7) 費用

本タスク実測: **¥0.90**(comment_3_ja TTS 1件のみ、`raw_usage_log.jsonl`
実測、count=1・status=OK)。¥10上限の範囲内(大幅未達)。既存artifactの
ASRキャッシュ再利用により、Key Phrase/story segment/nav項目の再ASR
診断コストは0件(`cost_summary.json`: asr_diag_call_count_estimate_basis
は前回run(72件)から変化なし、tts_call_count_estimate_basisのみ26→27
[+1])。**開発・Trial/検証費として記録**。Family C累計(全run合算、
`cost_summary.json`のtotal_estimate_jpy)=¥53.10。旧報告(Fix-02時点)の
Family C累計¥148.50は複数Trial(v1本番run含む)累計値であり、本タスク
差分(+¥0.90)を反映して更新が必要(SSOT追記は9節参照、予算枠¥90に
対する超過額は既にFix-02時点で発生済み・本タスクでは実質的に横ばい)。

## 8) model_id/TTS

Comment 3: 既存`repro01.generate_narration_snippet_verified_strict`
(Aoede narrator、既存retry構成そのまま)。Comment 1/2/Story/Key Phrase/
nav: 全て既存ファイル再利用(新規TTSなし)。

## 9) commit対象候補一覧(サイズ込み、wav除外・mp3必須)

| パス | サイズ/件数 | 種別 |
|---|---|---|
| `er013_family_c_episode_trial_09b_run.py` | 更新(~66K) | script(既存) |
| `er013_family_c_episode_trial_09b_test_01.py` | 更新(~9K) | test(既存) |
| `home_robots_v2/player.html` | 更新(18K) | player |
| `home_robots_v2/player_prev_comment4.html` | 新規(18K) | player旧版 |
| `home_robots_v2/web/family_c_home_robots_trial_09b.mp3` | 更新(3.44MB) | episode mp3 |
| `home_robots_v2/web/prev/family_c_home_robots_trial_09b_comment4.mp3` | 新規(3.47MB) | 旧episode mp3 |
| `home_robots_v2/web/segments/comment_3_ja.mp3`等(更新分) | 数十K | segment mp3 |
| `home_robots_v2/{comments_ja.md,comments_ja_prev.md,comment_consistency.json,comment_placement.json,article_audio_consistency.json,player_display_audio_consistency.json,audio_validation.json,cost_summary.json}` | 各数K〜20K | 中間・報告成果物 |
| `home_robots_v2/spec/episode_spec_v2.md` | 新規(3K) | 恒久spec |
| `home_robots_v2/audit/{tts_generation_results.json,run_summary_assemble.json,gain_report.json,headroom_report.json}` | 各数K | Assembly/Gate audit |
| `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2.md`+`_check.json` | 数K | T-0記録 |
| `docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md` | 本ファイル | 報告 |

除外(wav): `home_robots_v2/audio/comment_3_ja.wav`(更新)・
`home_robots_v2/assembled/family_c_home_robots_trial_09b.wav`(更新)・
`home_robots_v2/web/prev/family_c_home_robots_trial_09b_comment4.wav`
(新規、59MB)はcommitしない(mp3で代替済み)。`comment_4_ja.wav`/
`comment_4_ja.mp3`(旧、未使用のまま`audio/`・`web/segments/`に残存、
削除は本タスク範囲外)。

## 10) T-0・事前指定外Read・STOP有無

T-0: **PASS**(`docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-
TRACEABILITY-03-FAMILYC-A2_check.json`、reasons無し)。事前指定外Read:
Gate実装確認のため`er003_v1_n3_01_assemble.py::verify_episode_audio_
validation_gate`/`_segment_gate_status`/`_segment_asset_hash_stale`
(低コスト再Assembly設計がGateを正しく通ることを事前確認するため、
事前指定Grep一覧の範囲外)。`er003_v1_repro01_main_generate.py::
generate_narration_snippet_verified_strict`の戻り値仕様確認(asr_text
キーの有無、Comment 3の追加ASR診断要否を判断するため)。STOP: **なし**
(Human Review Lock到達なし、Gate緩和不要、費用¥0.90で上限¥10内に
収まった)。
