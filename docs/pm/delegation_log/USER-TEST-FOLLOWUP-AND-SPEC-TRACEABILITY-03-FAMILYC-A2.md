## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2(Family C / Home robots A2 v2: Comment 3修正+Comment 4削除+再Assembly)
並行タスク衝突確認: 並行して Family C B1生成(`er013_output/family_c_episode_trial_09/home_robots_b1/`、新規script `er013_family_c_episode_trial_09b_b1_run.py`)、Discovery(`.../discovery/`)、Trend命名整理、仕様追跡調査が走る。本タスクは`er013_output/family_c_episode_trial_09/home_robots_v2/`配下と`er013_family_c_episode_trial_09b_run.py`/`_09b_test_01.py`のみを書く(B1側のファイルは触らない)。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Family C)。ユーザー評価: v2の音声全体OK・Story良好。修正2点のみ。最大Status VALIDATED(Production採用禁止。Family C全体はProduction正式path未承認であることを記録)。
- (1) **Comment 3修正**: 現「お金や睡眠、仕事、安全について聞いても、今回はロボットのいつもの方法では答えが見つからないようです。」は誰が質問したか曖昧(マヤが質問したように聞こえる)。ユーザー指定文へ修正: 「お金や睡眠、仕事、安全についてロボットが問いかけ、マヤは答えましたが、今回はいつものようにロボットが最適解を示してくれることはありませんでした。」(意味・Factを変えない範囲で自然な日本語へ微調整可、微調整した場合は差分と理由を記録)。修正後TTS(既存経路、既存retry構成)→ASR一致→player表示一致を確認。
- (2) **Comment 4削除(ユーザー正式決定、Family C恒久仕様)**: Family CではComment 4を使用しない。構成原則=Comment 1(導入理解補助)/Comment 2(Story途中の自然な節目)/Comment 3(後半の自然な節目)/Comment 4なし。位置はsegment番号固定ではなくsemantic break・scene transition・turning point・前後text volume・前後audio durationで記事ごとに決める。v2からComment 4 segmentを除去し、Story終了後は既存Family A構成どおり(pause→Outro)。**`er013_family_c_episode_trial_09b_run.py`のComment構成を「Comment 1〜3、Comment 4なし」を既定とするよう変更**(B1側が同じ構成を使えるように。ただしB1 scriptは並行タスクが作るため触らない)。テスト(`_09b_test_01.py`)に「Comment 4が存在しない」「Comment 3が指定文」を追加。
- 再Assembly→Audio Validation Gate(緩和禁止)→mp3→player再生成(`home_robots_v2/player.html`、相対パス。旧版は`home_robots_v2/player_prev_comment4.html`として履歴保持せず上書きでよいが、旧assembled/mp3は`web/prev/`へ退避)→article/audio consistency・player/display/audio consistency再実行。Story本文不変(sha256)。再利用可能な既存音声(Story/Key Phrase/Comment 1・2/Intro/Outro)は再TTSしない。
- 費用上限: ¥10(Comment 3 TTS+ASRのみ)。**開発・Trial/検証費として記録**(Family C累計¥148.50に加算、予算枠超過額を更新)。
- 禁止: Story本文変更/Comment 1・2の変更/Key Phrase変更/Voice構成変更/Production(er003/er006/er011/er012)コード変更/Gate緩和/`approve_regenerate()`/Git commit・push/`.gitignore`変更/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: Comment 3 TTSがHuman Review Lock到達/Gate緩和が必要/費用上限超過見込み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> Family C / Home robots A2: 音声全体はOK、Storyも良好。Comment 3修正: 現Comment 3は日本語で誰が質問したのか曖昧。「お金や睡眠、仕事、安全についてロボットが問いかけ、マヤは答えましたが、今回はいつものようにロボットが最適解を示してくれることはありませんでした。」程度へ。意味・Factを変えない範囲で自然な日本語へ微調整可。修正後TTS・ASR・player一致を確認。Comment 4: Family CではComment 4を使用しない(恒久仕様)。構成原則: Comment 1導入/Comment 2途中の節目/Comment 3後半の節目/Comment 4なし。位置はsegment番号固定しない。Family C全体はまだProduction正式採用済みではない。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md` 全文(v2構成・Assembly順・Comment位置)。
2. `er013_family_c_episode_trial_09b_run.py`: Grep `comment|Comment|COMMENT|def build_timeline|def assemble|support|outro|def main|argparse` → Comment生成・timeline・再開ロジックの該当範囲のみ。
3. `er013_output/family_c_episode_trial_09/home_robots_v2/{comments_ja.md, comment_placement.json, segments.json}` 全文。
4. `er013_family_c_episode_trial_09b_test_01.py`: Grep `^    def test_|comment` → 既存テスト一覧。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `home_robots_v2/comments_ja.md`(Comment 3差し替え、Comment 4削除、旧文は`comments_ja_prev.md`へ)、`home_robots_v2/audio/comment_3.wav`(再生成)、`segments.json`(Comment 4除去)、`assembled/`・`web/episode mp3`(再生成、旧は`web/prev/`へ)、`audio_validation.json`、`player.html`、`article_audio_consistency.json`、`player_display_audio_consistency.json`、`comment_consistency.json`、`cost_summary.json`(加算)、`spec/episode_spec_v2.md`(Comment構成の恒久決定を追記: Comment 4なし・位置決定原則)。
- `er013_family_c_episode_trial_09b_run.py`: Comment既定を1〜3へ。`_09b_test_01.py`: テスト2件追加。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-A2_check.json`
2. `.venv\Scripts\python.exe er013_family_c_episode_trial_09b_run.py --fix-comment3 --drop-comment4 --reassemble --budget-jpy 10`(フラグは本タスクで実装、全文コマンド記録)
3. テスト: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09b_test_*.py"`
4. 確認: `Select-String -Path er013_output\family_c_episode_trial_09\home_robots_v2\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3`(exit 1)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにDECISION_LOG追記案(「Family C Comment 4なし」恒久Decision、Comment位置決定原則、Family C全体は未採用の注記)とOPEN-147末尾追記案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md`に: 1) 最終Status(VALIDATED候補・再試聴待ち)、2) Comment 3(旧→新、微調整の有無、TTS attempt、ASR一致、player表示一致)、3) Comment 4削除(segment除去、Assembly末尾構成)、4) Audio Validation、duration、mp3/player/予定URL(`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_v2/player.html`)、5) consistency結果、Story本文sha256、6) script/テスト変更とPASS件数、7) 費用(開発・Trial費、Family C累計・予算枠超過額)、8) model_id/TTS、9) commit対象候補一覧、10) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥10)
- [x] 並行タスク衝突回避あり(home_robots_v2限定・B1 script不可・Git操作なし)
