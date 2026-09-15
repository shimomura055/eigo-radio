## 管理ID

`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`(Fable修正指示2回目)
並行タスクなし。修正1回目(commit `7dc4f145`)の続き。

## 性質/到達上限Status/禁止事項

- 性質: 証跡ギャップの是正のみ。修正1回目で`--comments-en`/`--fix-robot-choice-second-person`フラグの非冪等性によりB1の`comment_1_ja`/`comment_2_ja`/`comment_3_ja`(実体は英語Comment 1〜3)と`story_017`(Robot選択肢)の音声が再TTSされたが、ASRは「全件キャッシュ再利用(`asr_diag`エントリなし)」と報告されている。つまり**現在episodeに含まれている新しい音声バイトに対するASR一致証跡が存在しない**。B1 Preview英語化と同じ実行での`preview_en`はASR実施済み(4者一致match=true)なので対象外。
- 到達上限Status: 不変(A2 v2・B1とも`VALIDATED候補/Trial`、`USER_LISTENING_PENDING`、Production未採用)。
- 対象外: A2 v2、Preview、Story本文、Trend/Discovery/Voices、`er012_*`/`er003_*`/`er011_*`、`CURRENT_SPEC.md`。voice変更(Aoede→Charon等)は行わない。
- 禁止: 再TTS(ASR実測のみ。TTSを1件も呼ばない)、再Assembly(episode mp3・player.htmlを変更しない。ASRが一致すれば現状維持)、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥5(ASR 4件)。
- STOP条件: (1)4 segmentのいずれかでASR不一致(canonicalとの差分がdisfluency/欠落/追加語に該当)→再TTSせずSTOPし、不一致内容(canonical/ASR全文)を報告。Fable/ユーザーが再TTS要否を判断する。(2)費用上限超過見込み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任のdelegation_log保存名: `docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix2.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-15、該当部分): 「QA: 全Commentについて、canonical/TTS input/ASR/player表示を一致確認。」「2-3. (中略)実施: canonical差し替え/Robot voice再TTS/ASR一致確認/player表示更新/episode再Assembly」

Fable判断: ユーザーが求める「ASR一致確認」は、episodeに実際に含まれる音声に対して成立していなければならない。修正1回目で音声バイトが変わった4 segmentについて、現物音声でのASR実測が必要。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET.md`: 72-137行(修正1回目の自分の報告)
- `er013_family_c_episode_trial_09b_b1_run.py`: Grepで`asr_diag|def .*asr|asr_cache|\.asr\.json|comment_consistency|player_display_audio_consistency`を位置特定→ASR実行関数・キャッシュ判定・consistency JSON生成関数の範囲Read(キャッシュキーが「テキスト」なのか「音声sha256」なのかを特定し報告)
- `er013_output/family_c_episode_trial_09/home_robots_b1/audit/tts_generation_results.json`: Grepで`comment_1_ja|comment_2_ja|comment_3_ja|story_017`を位置特定→各entry範囲Read(現在のsha256・pathを取得)
- `er013_output/family_c_episode_trial_09/home_robots_b1/comment_consistency.json`および`player_display_audio_consistency.json`: 全文(現在の証跡がどの音声に対するものかを`sha256`/timestamp等で確認)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. `Grep pattern="asr_diag" path=er013_output/family_c_episode_trial_09/home_robots_b1/ glob=*.jsonl output_mode=content`→修正1回目実行時刻以降の`asr_diag`エントリが4 segment分無いことを再確認(前提の裏取り)。
2. ASR実測後: `comment_consistency.json`・`player_display_audio_consistency.json`の当該4 entryを新しいASR結果で更新(既存スクリプトにASR強制再実行オプション[例`--force-asr`または対象segment指定]があればそれを使用。無ければ既存ASR関数を対象4 wavに対して直接呼ぶ最小pythonスニペットで実行し、JSONの当該entryのみ更新。スニペット全文を報告)。
3. SSOT追記位置: `Grep pattern="Fable修正指示1回目" path=DECISION_LOG.md`→その行の直後に修正2回目の1行を追記。`OPEN_ITEMS.md`OPEN-147は追記不要(費用のみ変わる場合はpythonで行末の累計値を更新)。
4. REPORT `FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`: 3b節末尾に「ASR実測(修正2回目)」段落を追加、8節費用を更新、10節unresolved issue(1)非冪等性の項に「再生成音声4件はASR実測で一致確認済み」を追記。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix2.md --json-out docs\pm\delegation_log\FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix2_check.json
```

ASR実測(既存スクリプトに強制ASRオプションがある場合の例。実名が異なれば調整し実引数全文を報告):
```
.venv\Scripts\python.exe er013_family_c_episode_trial_09b_b1_run.py --asr-only --segments comment_1_ja,comment_2_ja,comment_3_ja,story_017
```
オプションが無い場合は、既存ASR関数を`er013_output/family_c_episode_trial_09/home_robots_b1/audio/comment_1_ja.wav`・`comment_2_ja.wav`・`comment_3_ja.wav`・`story_017.wav`(実パスは`tts_generation_results.json`の`path`に従う)へ直接適用する最小スニペットを`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\asr_verify_fix2.py`に書いて実行し、結果を上記2つのconsistency JSONへ反映。

現物一致の証跡: 4 wavのsha256と、episode mp3が現在のwavからassembleされたこと(`audit/run_summary_assemble.json`のtimestamp/入力一覧)を確認し報告。

回帰(テスト変更なしだが証跡JSON更新後の確認として1回):
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09b_b1_test_*.py"
```

## SSOT追記文

`DECISION_LOG.md`(「Fable修正指示1回目」行の直後):
```
- 2026-09-15 Fable修正指示2回目: 修正1回目で副作用再TTSされたB1 Comment 1〜3・Robot選択肢(story_017)の4 segmentについて、現物音声でASR実測(<一致4/4 または 不一致内容>)。ASRキャッシュキー=<テキスト/音声sha256>。追加費用¥<実測>、本タスク累計¥48.00+¥<実測>=¥<合計>、Family C累計¥<合計>。commit <hash>。
```

`docs/pm/ACTIVE_TASK.md`: 費用累計・commit hashを更新(固定ヘッダ形式維持)。
`docs/pm/RESULT_PACKET.md`: 末尾に「## 修正2回目」節を追加。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象: `er013_output/family_c_episode_trial_09/home_robots_b1/comment_consistency.json`、同`player_display_audio_consistency.json`、同`audit/`配下で更新されたjson、同`raw_usage_log.jsonl`(存在しGit追跡済みなら)、`DECISION_LOG.md`、`OPEN_ITEMS.md`(更新した場合のみ)、`FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_REPORT.md`、`docs/pm/delegation_log/FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04_fix2.md`、同`_check.json`、スクリプトに`--asr-only`等を追加した場合は`er013_family_c_episode_trial_09b_b1_run.py`。
- コミットメッセージ: `FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04 (fix2): 副作用再TTS 4segmentのASR実測証跡`
- trailer: `Task-ID: FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04`
- push: `git push origin main`。STOP条件(1)該当時はcommitせず報告のみ。

## 報告(RESULT_PACKET項目)

「## 修正2回目」に:
1. T-0結果
2. ASRキャッシュキーの実装事実(ファイル:行)と、修正1回目でASRが走らなかった理由
3. 4 segment各: canonical全文/ASR全文/一致判定(match=true/false、差分があれば語単位)
4. 現物一致証跡(4 wav sha256、assemble入力との対応)
5. 費用(ASR実費、本タスク累計、Family C累計)
6. 回帰結果
7. commit hash・push結果(STOP時は「未commit」)
8. STOP該当有無
9. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一。
