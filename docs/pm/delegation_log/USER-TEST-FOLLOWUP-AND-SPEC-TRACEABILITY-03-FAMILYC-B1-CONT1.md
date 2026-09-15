## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(継続CONT1、Fable修正指示1回目: Comment 3主語明確化)
並行タスク衝突確認: 並行タスクなし。本タスクは`er013_output/family_c_episode_trial_09/home_robots_b1/`配下と`er013_family_c_episode_trial_09b_b1_run.py`/`_b1_test_01.py`のみを書く。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1_2.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Family C B1)。Fable照合で、B1のComment 3「お金や仕事、睡眠、安全について答えても、今回はロボットのいつものやり方だけでは答えが見つからないようです。」が、A2 v2でユーザーが指摘した「誰が問いかけ誰が答えたか曖昧(マヤが質問したように聞こえる)」問題を再現していると判定。委任条件未達のため修正する。
- 修正: Comment 3を、A2 v2のユーザー指定文と同趣旨で主語を明確にした日本語へ差し替える(例: 「ロボットがお金や仕事、睡眠、安全について問いかけ、マヤは一つずつ答えましたが、今回はいつものようにロボットが最適解を示してくれることはありませんでした。」意味・Fact[B1本文: The robot asked about money, work, sleep, and safety. Maya answered each question…]を変えない範囲で自然な日本語へ微調整可、差分と理由を記録)。Comment 1・2・Preview・Key Phrase・Story音声は再利用(再TTSしない)。Comment 3のみ既存経路で再TTS(既存retry構成)→ASR一致→再Assembly→Audio Validation Gate(緩和禁止)→mp3(旧は`web/prev/`へ退避)→player再生成(相対パス、level=B1表記)→`comment_consistency.json`・`player_display_audio_consistency.json`・`article_audio_consistency.json`再実行。テストに「Comment 3が主語明示文である」1件追加。
- Comment 3位置は変更しない(前回の35%/65%語数比→段落境界スナップの結果を維持。位置決定方式はsemantic break・volume balanceの暫定実装であり恒久仕様ではない旨を`comment_placement.json`のnoteに追記)。
- 費用上限: ¥5(Comment 3 TTS+ASRのみ)。開発・Trial/検証費として記録(Family C累計に加算)。
- 禁止: Story本文変更/他Comment・Key Phrase変更/Voice構成変更/v2 script(`_09b_run.py`)編集/Production(er003/er006/er011/er012)コード変更/Gate緩和/`approve_regenerate()`/Git commit・push/`.gitignore`変更/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
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

> (A2 v2について)現Comment 3は、日本語では「誰が質問したのか」が曖昧で、Mayaが質問したように聞こえる。「お金や睡眠、仕事、安全についてロボットが問いかけ、マヤは答えましたが、今回はいつものようにロボットが最適解を示してくれることはありませんでした。」程度へ修正。意味・Factを変えない範囲で自然な日本語へ微調整可。修正後TTS・ASR・player一致を確認。(B1にも同原則を適用。)

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FU03_FAMILYC_B1.md` 全文(到達点・Comment生成経路・再開フラグ)。
2. `er013_family_c_episode_trial_09b_b1_run.py`: Grep `comment|Comment|COMMENT|argparse|add_argument|resume|def main|assemble|player` → Comment生成・再開・Assembly・player該当範囲のみ。
3. `er013_output/family_c_episode_trial_09/home_robots_b1/{comments_ja.md, comment_placement.json, segments.json}` 全文。
4. `docs/pm/RESULT_PACKET_FU03_FAMILYC_A2.md`: Grep `--fix-comment3|Comment 3|comment_3` → A2 v2で実装した修正経路の要点のみ(同方式をB1 script側に実装)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `home_robots_b1/comments_ja.md`(Comment 3差し替え、旧は`comments_ja_prev.md`)、`audio/comment_3*.wav`(再生成)、`assembled/`・`web/episode mp3`(再生成、旧は`web/prev/`)、`audio_validation.json`、`player.html`、consistency JSON 3件、`comment_placement.json`(note追記)、`cost_summary.json`(加算)。
- `_b1_run.py`: `--fix-comment3 --reassemble`相当のフラグ追加。`_b1_test_01.py`: テスト1件追加。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1-CONT1.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1-CONT1_check.json`
2. `.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --fix-comment3 --reassemble --budget-jpy 5`(全文コマンド記録)
3. テスト: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09b_b1_test_*.py"`
4. 確認: `Select-String -Path er013_output\family_c_episode_trial_09\home_robots_b1\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er013_output/family_c_episode_trial_09/home_robots_b1/web/episode.mp3`(exit 1、実ファイル名に合わせる)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-147末尾追記案(B1 Comment 3修正)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須、前回分含む)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_FAMILYC_B1_2.md`に: 1) 最終Status(VALIDATED候補・試聴待ち)、2) Comment 3(旧→新、TTS attempt、ASR一致、player表示一致)、3) Audio Validation、duration、mp3/player/予定URL(`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots_b1/player.html`)、4) consistency結果、Story本文sha256不変、5) テスト件数、6) 費用(本タスク実費、Family C累計=¥148.50+¥0.90+¥85.20+本タスク、予算枠¥133.99超過額)、7) commit対象候補一覧、8) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥5)
- [x] 並行タスク衝突回避あり(home_robots_b1限定・Git操作なし)
