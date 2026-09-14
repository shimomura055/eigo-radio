## 管理ID

USER-TEST-AUDIO-COMPLETION-01-FAMILYC(Family C / Home robots Web試聴導線修正)
並行タスク衝突確認: 並行して Trend音声化(`er014_output/four_type_observation_01/trend/`)、Discovery音声化(`.../discovery/`)、Voices音声化(`.../voices/`、er012_*)が走る。本タスクは`er013_output/family_c_episode_trial_09/`配下と`er013_family_c_episode_trial_09_run.py`(player生成部のみ)だけを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_FAMILYC.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trial-09(VALIDATED)の**Web試聴導線修正のみ**。音声内容・Voice構成・Preview・Key Phrase・support・Story本文・segment構成は一切変更しない(再生成禁止)。Status上限: VALIDATEDのまま(Production採用ではない)。
- 確認済み問題(ユーザー指摘): `er013_output/family_c_episode_trial_09/home_robots/player.html`はRepoに存在するが音声参照が`file:///C:/...`のローカル絶対パス。完成WAV `assembled/family_c_home_robots_trial_09.wav`(48MB)はGitHub上に存在しない(前回commit `b124a4b7`に含まれていない可能性、または.gitignore対象)。
- やること: (1) `git ls-files er013_output/family_c_episode_trial_09 | head`と`git check-ignore -v er013_output/family_c_episode_trial_09/home_robots/assembled/family_c_home_robots_trial_09.wav`で「未add」か「gitignore」かを特定し記録。(2) 完成episode WAVを配信用MP3(既存repo内の変換手段を優先: Grep `mp3|ffmpeg|pydub|lameenc` in `*.py`で既存utilityを探す。無ければ`ffmpeg`コマンドの有無を確認し、あれば128kbps mono/stereoは元に合わせる。どちらも無ければSTOP候補=「技術的にWeb配信不可」ではなくPython実装で可能なら`.venv`にある既存ライブラリのみで実施、新規pip install禁止)へ変換: `home_robots/web/family_c_home_robots_trial_09.mp3`。個別segment 38件も同様にMP3化して`home_robots/web/segments/`へ(内容無変更、標準playerのsegment表が動くようにするため)。(3) player生成を修正: `er013_family_c_episode_trial_09_run.py`のplayer生成部(Grep `player|file:///|abspath|as_uri|audio_review_player`)を、**相対パス**(`./web/...`)を書くよう変更し、playerを`home_robots/player.html`として再生成(音声再生成なし、既存`segments.json`/`audio_validation.json`から再構成)。Title/level(FAMILY C TRIAL-09 / A2)/完成episode/segment表が判別できる標準Audio Review Player形式(`audio_review_player.py`)を再利用、新player仕様は作らない。(4) 生成後、player.html内に`file:///`・`C:\`・絶対パスが0件であることをGrepで確認。(5) 配信対象(mp3群+player.html)が`git check-ignore`で無視されないことを確認(無視される場合は理由を記録し、`.gitignore`は変更せず、無視されない配置先候補を提案してSTOP)。各mp3のサイズを記録(1ファイル50MB未満)。(6) 参照URL形式(統合タスクがpush後に検証): player=`https://raw.githack.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/player.html`、直接音声=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/web/family_c_home_robots_trial_09.mp3`。(7) ローカル再生可能性確認: 生成mp3を既存Python音声ライブラリでデコードしduration(≈257.8秒)・チャンネル・サンプルレートを記録。(8) `cost_summary.json`に「Web配信化追加費 ¥0(API不使用)」を追記(API使用があれば実額)。
- 費用上限: ¥5(原則API不使用)。
- 禁止: 音声・テキスト再生成、TTS呼び出し、Voice/segment構成変更、`.gitignore`変更、pip install、Git commit/push、Production(er003/er006/er011/er012)コード変更、`run_project_regression.py --pattern`に`_test`を含まないglob、PATH上の素`python`。
- STOP条件: 技術的にWeb配信不可(変換手段なし・配置先すべてgitignore等)/Trial-09の仕様変更が必要。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 既存Trial-09の採用済み完成音声を使って、完成episode音声をGitHub上で参照可能な形にする/必要なら配信用MP3へ単純変換/player.htmlのfile:///参照をWebアクセス可能なURLへ変更/個別segment音声もWeb playerで必要なら同様に参照可能にする/raw.githack等から実際に開けるplayerを作る/Repo上に実音声ファイルが存在することを確認/playerから完成episodeが再生できることを確認。これはTrial-09の仕様変更ではない。Voice構成/Preview/Key Phrase/support/Story本文/segment構成は変更しない。file:///のローカルリンクは最終報告に出さない。Trial-09は引き続きVALIDATED。

## 事前指定Read一覧

1. `er013_family_c_episode_trial_09_run.py`: Grep `player|file:///|as_uri|abspath|audio_review_player|def build_player|def write_player` → player生成関数の該当範囲のみ。
2. `audio_review_player.py`: Grep `^def |src=|audio_path|relative|href` → 音声パスの受け渡し引数のみ。
3. `er013_output/family_c_episode_trial_09/home_robots/segments.json` 全文(segment→音声ファイル対応)。
4. `er013_output/family_c_episode_trial_09/home_robots/player.html`: Grep `file:///|\.wav|<audio|src=` → 現在の参照形式のみ。
5. `.gitignore`: Grep `wav|mp3|er013|output|audio` → 無視ルール。
6. 変換utility探索: Grep `def .*mp3|ffmpeg|pydub|lameenc` in `*.py`(ルート直下のみ、`er0*_output`は除外)→ 見つかった関数の該当範囲のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力先: `home_robots/web/family_c_home_robots_trial_09.mp3`、`home_robots/web/segments/<segment_id>.mp3`、`home_robots/player.html`(上書き、相対参照)、`home_robots/web_delivery.json`(mp3一覧・サイズ・duration・変換手段・gitignore確認結果)。
- `er013_family_c_episode_trial_09_run.py`: player生成部のみ相対パス化(他は無変更)。`er013_family_c_episode_trial_09_test_01.py`に「player.htmlにfile:///が含まれない」テスト1件追加。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-FAMILYC.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-FAMILYC_check.json`
2. `git ls-files er013_output/family_c_episode_trial_09 | Measure-Object -Line` / `git check-ignore -v er013_output/family_c_episode_trial_09/home_robots/assembled/family_c_home_robots_trial_09.wav`(exit code含め記録)
3. 変換・player再生成(本タスクで作る`er013_output/family_c_episode_trial_09/build_web_delivery.py`または既存runの`--player-only`相当。全文コマンドを記録)
4. テスト: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09_test_*.py"`
5. 確認: `Select-String -Path er013_output\family_c_episode_trial_09\home_robots\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-147末尾追記案(Web試聴導線修正、mp3パス、追加費)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧(サイズ付き)」を列挙(統合タスクがadd/push/URL検証を行う)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_FAMILYC.md`に: 1) WAV未存在の原因(未add/gitignore)、2) 変換手段・mp3一覧(パス・サイズ・duration)、3) player.htmlの参照形式(相対パス、file:///=0件の確認結果)、4) 予定URL(player=raw.githack、直接音声=raw.githubusercontent)、5) ローカルデコード確認(duration/ch/sr)、6) テスト結果、7) 追加費用(¥)、8) commit対象候補一覧、9) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥5)
- [x] 並行タスク衝突回避あり(er013配下限定・Git操作なし)
