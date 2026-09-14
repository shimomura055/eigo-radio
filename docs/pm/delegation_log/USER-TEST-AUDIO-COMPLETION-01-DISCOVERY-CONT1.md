## 管理ID

USER-TEST-AUDIO-COMPLETION-01-DISCOVERY-CONT1(継続CONT1、Fable修正指示1回目)
並行タスク衝突確認: 並行して Trend音声化継続(`.../trend/`)、Voices音声化継続(`.../voices/`)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_DISCOVERY_2.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 前回(`docs/pm/RESULT_PACKET_UT_DISCOVERY.md`)でA2は完成(episode 480秒、player生成済み)、B1Bは`full_story_part2`が3回TRUE_CONTENT_MISMATCH→Human Review Cost Guardで停止。**Fable診断**(`audio/b1b/audit/review_lock_state.json` L504): ASR結果は「six minutes and **three** seconds」(原文「six minutes and 30 seconds」)、「silences」(原文「silence」)、「In one study that measured」(原文「In a study that measured」)、さらに原文の「In a study of 2,557 college students at 12 sites in 11 countries, … phone use.」の2文が音声から**欠落**している。数字の読み(30→three)と長文segmentでの文欠落が原因。
- **対応方針(Fable判断、既存仕様内)**: 記事本文は一切変更しない。driver側で**TTS入力の読み整形のみ**(既存Production関数は無変更): (a) 数字の読み形: 「30 seconds」→「thirty seconds」、「2,557」→「two thousand five hundred and fifty-seven」、「12 sites in 11 countries」→「twelve sites in eleven countries」、「46」→「forty-six」、「37 studies」→「thirty-seven studies」、「55 students」「15 minutes」「11 studies」等、full_story_part2に含まれる算用数字を英語の数詞に置換(意味不変、語の追加・削除・言い換え禁止)。置換一覧を`discovery/audio/tts_reading_transforms.json`(原文→読み形→理由)へ記録。この読み整形はTrial-09「7:00→seven」と同種で、表示テキストは変えない前処理である。(b) 読み整形後のテキストで、既存関数(`generate_b1_segments`相当/前回driverと同じ`news_tail_fix.generate_news_narration_wide_margin`等)により`full_story_part2`を通常の初回TTS/ASR(既存上限どおり)で生成。**`approve_regenerate()`は呼ばない**。新テキストはlockキー(`canonical_text_sha256`)が別になるため新規エントリとして扱う。旧lockエントリは削除・編集しない。「同一テキストの再試行ではなく、根本原因(数字読み)を除いた別テキストの初回生成」であることをRESULT_PACKETに明記。新テキストでも既存上限まで失敗(特に文欠落が再発)した場合はSTOP(承認代行禁止)。segment分割の変更(part3化等)は構造変更にあたるため禁止。
- 続き: B1B Assembly(既存仕様)→Audio Validation Gate(緩和禁止)→完成episode WAV+MP3(A2と同方式)→標準player(相対パス、Title/level=B1B明記、`discovery/audio/b1b/player.html`、`web/episode.mp3`、`web/segments/*.mp3`)→記事⇔音声一致確認(読み整形前の記事本文とTTS canonical_textの差分が`tts_reading_transforms.json`の置換のみであることを機械確認)→gitignore確認・mp3<50MB→費用更新(`discovery/audio/cost_summary_audio.json`、`discovery/production_set_cost.json`: Discovery総原価=¥548.78+本タスク実費、差分明記)、`progress_log.md`1行追記。A2側は完成済みのため再実行しない(A2のplayer/mp3が未生成の項目があれば生成のみ行う: `discovery/audio/a2/web/episode.mp3`・`web/segments/`・`web_delivery.json`を確認)。
- 費用上限: 本タスク¥60。段階ごとに次段階見込み込みで事前判定。
- 禁止: 記事本文変更/語の追加・削除・言い換え/segment構造変更/`approve_regenerate()`呼び出し/lockファイル編集/Gate緩和/retry上限変更/Production(er003/er006/er011)コード変更/Validator変更/`.gitignore`変更/pip install/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/読み整形後も既存上限まで失敗/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

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

> 完成済みA2/B1B記事+Key Phraseを用いて、既存正式audio completion経路で、TTS/A2 slowdown等/Comment・Preview等既存仕様/Assembly/Audio Validation/完成episode/Web試聴playerまで進める。A2/B1双方をユーザーが試聴できる状態にする。今回の既存仕様・既存音声経路で完成できる限り、途中でユーザーへ戻さず進める。STOPは新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/想定外の大幅コスト増/技術的にWeb配信不可の場合のみ。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_UT_DISCOVERY.md` 全文(前回到達点)。
2. `er014_output/four_type_observation_01/discovery/run_discovery_audio_completion.py` 全文(前回driver。読み整形段階を追加して`run_discovery_audio_completion_2.py`を派生)。
3. `er014_output/four_type_observation_01/discovery/audio/b1b/audit/review_lock_state.json`: Grep `"segment_id": "full_story_part2"` -A 40 → attempts_logのasr_text 3件と、Grep `"canonical_text": ` の該当行(full_story_part2のTTS入力原文)。
4. `er011_human_review_lock_01.py`: Grep `sha256|canonical_text|def check_before_generation` → lockキー算出のみ。
5. `er014_output/four_type_observation_01/discovery/audio/a2/web_delivery.json`(存在すれば)全文、`discovery/audio/a2/`: Glob `web/**` → A2配信物の有無確認。
6. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `discovery/audio/tts_reading_transforms.json`(新規)。driver `run_discovery_audio_completion_2.py`(`--level b1b`、budget_jpy=60)。出力: `discovery/audio/b1b/{narration/full_story_part2.wav(新), assembled/, audio_validation.json, player.html, web/episode.mp3, web/segments/*.mp3, article_audio_consistency.json}`、`discovery/audio/cost_summary_audio.json`、`discovery/audio/web_delivery.json`、`discovery/production_set_cost.json`、`progress_log.md`。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-DISCOVERY-CONT1.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-DISCOVERY-CONT1_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_audio_completion_2.py --level b1b`(全文コマンド記録)
3. 確認: `Select-String -Path er014_output\four_type_observation_01\discovery\audio\*\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)
4. `git check-ignore -v er014_output/four_type_observation_01/discovery/audio/b1b/web/episode.mp3`(exit 1=無視されない)
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案と、Open Item案「A-Family audio completionのTTS入力前処理: 算用数字(時間・人数)の読み整形と長文segmentでの文欠落」を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須、A2分含む)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_DISCOVERY_2.md`に: 1) 最終Status(A2/B1B)、2) 読み整形一覧と「語の追加削除なし」機械確認、3) TTS(新canonicalでのattempt数、文欠落の再発有無、lock非バイパスの説明)、4) Audio Validation結果(B1B)、5) 完成episode duration(A2/B1B)、6) 記事⇔音声一致確認、7) mp3一覧・player相対参照確認・予定URL(`https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/{a2,b1b}/player.html`、`https://raw.githubusercontent.com/.../audio/{a2,b1b}/web/episode.mp3`)・gitignore確認、8) 費用: 本タスク実費、**Discovery Production 1生成セット総原価=¥548.78+本タスク=¥xx.xx**、9) model_id/TTS model、10) Open Item候補、11) commit対象候補一覧、12) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥60)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
