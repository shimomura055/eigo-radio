## 管理ID

USER-TEST-AUDIO-COMPLETION-01-TREND(継続CONT1、Fable修正指示1回目)
並行タスク衝突確認: 並行して Discovery音声化(`.../discovery/`)、Voices音声化継続(`.../voices/`)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。共有資産への書き込みは既存経路が自動で行う分のみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_TREND_2.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 前回(`docs/pm/RESULT_PACKET_UT_TREND.md`)でA2/B1BともHuman Review Cost Guardにより停止。**Fableが監査ログを照合した診断**: (1) A2 `full_story_part1/part2`・`point_two`のcanonical_text(TTS入力)にMarkdownリンク記法`[Google](https://blog.google/...)`のURL部分がそのまま含まれている(`a2/audit/tts_generation_results.json` L739/L860/L1197)。URLはTTSが読まず、ASR照合が構造的に不一致になる。前例記事(er011 Trend end-to-end)にはインラインリンクが無かったため顕在化しなかった前処理gap。(2) 「Alexa+」をASRが「Alexa Plus」と書き起こし、記号「+」が照合不一致になる。(3) B1B `comment_4`: TTSは正しく読んでいるがASRが"assistants"を"assistance"と誤認(3回とも)。(4) B1B `full_story_part1/part2/point_one`: 原因未確定(attempts_logのasr_textとcanonical_textを突合して特定すること。「Alexa+」「Wear OS」「Ray-Ban Meta」「Pixel Buds 2a」等の固有名詞・記号が候補)。
- **対応方針(Fable判断、既存仕様内)**: 記事本文(reader-facing canonical article)は一切変更しない。**driver側でTTS入力テキストの「読み整形」のみ**を行う(既存Production関数は無変更): (a) Markdownリンク`[text](url)`→`text`(表示テキストのみ残す)、(b) 記号読み: 「Alexa+」→TTS/ASR照合用に「Alexa Plus」(canonical_textにもこの読み形を使う。意味・語順は不変)、(c) B1B(4)で特定した固有名詞・記号について、意味を変えない読み形への置換のみ(語の追加・削除・言い換えは禁止。置換一覧を`trend/audio/tts_reading_transforms.json`に記録: 原文→読み形→理由)。この読み整形はTrial-09の「7:00→seven」と同種の、表示テキストを変えない前処理である。(d) B1B `comment_4`(ASR同音異義誤認): Comment/Previewは補助生成テキストであり、既存Scaffold経路(前回使用の`run_b1_scaffold`相当)でsupport textを再生成し(最大2回)、新しいcomment_4でTTSを行う。他のcomment/previewが既にOKなら、可能な限りcomment_4だけを差し替える(関数が全件生成しかできない場合は全件再生成・再TTSでよい、費用は小さい)。
- **Human Review Lockの扱い(重要)**: `approve_regenerate()`は**呼ばない**。上記(a)〜(d)により該当segmentのcanonical_textが変わる(=lockのキーである`canonical_text_sha256`が別になる)ため、新テキストに対する通常の初回TTS/ASR(既存上限どおり)を行う。旧lockエントリはそのまま残す(削除・編集禁止)。これは「同一テキストの再試行」ではなく「根本原因(URL・記号)を除いた別テキストの初回生成」であることをRESULT_PACKETに明記する。新テキストでも既存上限まで失敗した場合はSTOP(approve代行禁止)。
- 続き: Assembly(Intro/Outro/SFX既存仕様)→Audio Validation Gate(緩和禁止)→完成episode WAV+MP3(Family C並行タスクと同じ`soundfile.write(format="MP3")`方式、`er013_output/family_c_episode_trial_09/build_web_delivery.py`を参考)→標準Audio Review Player(相対パス、Title/level明記、A2/B1B別player)→記事⇔音声一致確認(読み整形前の記事本文と、TTS canonical_textの差分が`tts_reading_transforms.json`の置換のみであることを機械確認し`article_audio_consistency.json`へ)→gitignore確認・mp3<50MB→費用更新。
- 費用上限: 本タスク¥100(A2/B1Bの該当segment TTS再生成+comment再生成+ASR)。段階ごとに次段階見込み込みで事前判定。
- 禁止: 記事本文変更/語の追加・削除・言い換え/`approve_regenerate()`呼び出し/lockファイル編集/Gate緩和/retry上限変更/Production(er003/er006/er011)コード変更/`.gitignore`変更/pip install/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/読み整形後も既存上限まで失敗/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。片levelのみ完成した場合はその旨をStatusに明記。

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

> 完成済みcanonical articleを使い、既存正式audio completion経路で完成episode・Web試聴playerまで進める。記事内容を音声都合で勝手に変更しない。既存Production audio pathをそのまま使用できないgapがあれば、新仕様を作る前に既存資産で最小接続を優先する。今回の既存仕様・既存音声経路で完成できる限り、途中でユーザーへ戻さず進める。STOPは新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/想定外の大幅コスト増/技術的にWeb配信不可の場合のみ。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_UT_TREND.md` 全文(前回到達点)。
2. `er014_output/four_type_observation_01/trend/run_trend_audio_completion.py` 全文(前回driver。読み整形フック・comment再生成・Assembly以降を追加して`run_trend_audio_completion_2.py`を派生、または同driverに`--reading-transforms`段階を追加)。
3. `er014_output/four_type_observation_01/trend/audio/a2/audit/tts_generation_results.json`: Grep `"canonical_text": "` → full_story_part1/part2/point_twoのcanonical_text行(L739/L860/L1197付近)のみ。
4. `er014_output/four_type_observation_01/trend/audio/b1b/audit/tts_generation_results.json`: Grep `"segment_id": "(full_story_part1|full_story_part2|point_one|comment_4)"` -A 20 → 各attemptのasr_textと、Grep `"canonical_text": "` の該当行(L672/L837/L1002/L1322付近)→ 突合して不一致トークンを特定。
5. `er011_human_review_lock_01.py`: Grep `sha256|canonical_text|def check_before_generation|key` → lockキーの算出方法のみ(新テキストが別エントリになることの確認)。
6. `er013_output/family_c_episode_trial_09/build_web_delivery.py` 全文(MP3化方式の流用)。
7. `audio_review_player.py`: Grep `^def |title|level|src=` → 引数のみ。
8. `er014_output/four_type_observation_01/trend/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `trend/audio/tts_reading_transforms.json`(新規: level別の原文→読み形→理由)。
- driver更新(`run_trend_audio_completion_2.py`または既存driverへ段階追加): 読み整形→該当segmentの再TTS(新canonical)→comment_4再生成(B1B)→Assembly→Gate→WAV/MP3→player→consistency→cost。出力: `trend/audio/{a2,b1b}/{assembled/,audio_validation.json,player.html,web/episode.mp3,web/segments/*.mp3,article_audio_consistency.json}`、`trend/audio/cost_summary_audio.json`、`trend/audio/web_delivery.json`、`trend/production_set_cost.json`(Trend総原価=¥174.03+前回¥122.15+本タスク実費、差分明記)、`progress_log.md`1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_audio_completion_2.py --level a2` → `--level b1b`(budget_jpy=100を両level合計で管理。全文コマンド記録)
3. 確認: `Select-String -Path er014_output\four_type_observation_01\trend\audio\*\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)
4. `git check-ignore -v er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3`(exit 1=無視されない)
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案と、Open Item案「A-Family audio completionのTTS入力前処理: Markdownインラインリンク・記号(+)の読み整形が未実装(driver側で暫定対応)」を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_TREND_2.md`に: 1) 最終Status(A2/B1B)、2) 読み整形一覧(原文→読み形→理由、level別)と「語の追加削除なし」の機械確認結果、3) B1B(4)の原因特定結果、4) comment_4再生成(旧→新テキスト、Contract/QA結果)、5) TTS(新canonicalでのattempt数、retry/fallback、lock非バイパスの説明)、6) Audio Validation結果、7) 完成episode duration(A2/B1B)、8) 記事⇔音声一致確認、9) mp3一覧・player相対参照確認・予定URL・gitignore確認、10) 費用: 本タスク実費、**Trend Production 1生成セット総原価=¥174.03+¥122.15+本タスク=¥xx.xx**(音声化追加費の内訳)、11) model_id/TTS model、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥100)
- [x] 並行タスク衝突回避あり(trend/配下限定・Git操作なし)
