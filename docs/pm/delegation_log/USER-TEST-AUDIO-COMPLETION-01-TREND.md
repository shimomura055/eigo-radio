## 管理ID

USER-TEST-AUDIO-COMPLETION-01-TREND(Trend / The end of the smartphone as the main interface: A2/B1B音声化+Web試聴player)
並行タスク衝突確認: 並行して Family C(er013)、Discovery(`.../discovery/`)、Voices(`.../voices/`、er012_*)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。共有資産(`er006_output/master_audio_store_01/`、`pronunciation_ledger`、`er011_output/attempt_history.jsonl`等)への書き込みは既存経路が自動で行う分のみ許容(手動編集禁止)。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_TREND.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 完成済みcanonical article(A2 `trend/reader_facing_article.txt`=`trend/a2/article.md` 503語、B1B `trend/reader_facing_article_b1b.txt`=`trend/b1b/article.md` 479語)を、**既存正式audio completion経路**でA2/B1双方の完成episode+Web試聴playerまで仕上げる。新記事生成禁止、記事本文を音声都合で変更しない。
- 経路調査(先に実施): A-Family A2/B1Bの既存完成経路の実例=`er011_output/family_a_completion_a2_trend_end_to_end_01/`(Trend A2/B1Bをend-to-endで完成させた前例)。その生成scriptをGlob `er011_family_a_completion*.py`/`er011_*end_to_end*.py`で特定し、入口関数・入力(article path、Ledger、editorial_mode、level、out_dir)・出力(key_phrases/、preview、comment、tts、assembled/、audio_validation、player)を確認。Trend Synthesis記事(Point One/Two構造・Trend Gate)に対しその経路がそのまま使えるかを確認し、gapがあれば**新仕様を作らず既存資産で最小接続**(例: 既存の関数を順に呼ぶdriverを`trend/run_trend_audio_completion.py`として書く)。
- 実施内容(A2/B1Bそれぞれ): (1) 音声化に必要な既存付帯要素の確認・生成: Key Phrase(A2/B1B未生成→既存`run_key_phrases`正式経路で生成、Validator不合格時は入口再呼び出し最大3回)、Preview/Comment等の既存level仕様に含まれる要素(既存経路が生成するものをそのまま)。(2) TTS(既存retry/fallback、A2 slowdown等の既存level仕様)。(3) Assembly(Intro/Outro/SFX含む既存仕様)。(4) Audio Validation Gate(既存、緩和禁止)。(5) 完成episode(WAV)+配信用MP3(既存変換手段。Grep `mp3|ffmpeg|pydub` in ルート`*.py`。無ければffmpegコマンド。pip install禁止)。(6) Web試聴player: 標準Audio Review Player(`audio_review_player.py`)を再利用し、**相対パス参照のみ**(`file:///`・絶対パス禁止)、Title/level(A2/B1B)/完成episode/segment表が判別できること。A2とB1Bは別player(`trend/audio/a2/player.html`、`trend/audio/b1b/player.html`)。(7) 記事と音声内容の一致確認: TTS入力テキストがcanonical article(見出し・本文)と一致することを既存ASR検証結果(`tts_generation_results.json`等)とテキスト突合で確認し、`trend/audio/<level>/article_audio_consistency.json`に記録。(8) 配信対象が`git check-ignore`で無視されないこと、各mp3<50MBを確認。予定URL形式: player=`https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/player.html`(B1Bも同様)、直接音声=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3`。(9) 費用: `trend/audio/cost_summary_audio.json`(Key Phrase LLM/Preview・Comment LLM/TTS/その他を分離、level別)、`trend/production_set_cost.json`更新(Trend Production 1生成セット総原価=既報¥174.03+音声化追加費、差分明記、50:50配賦なし)。
- 費用上限: ¥150(A2+B1B合計。Key Phrase・Preview/Comment LLM・TTS一式。段階ごとに次段階見込み込みで事前判定)。
- 禁止: 記事本文変更/新記事生成/Fact Checker再実行(不要)/Gate緩和/retry上限変更/新player仕様/Production(er003/er006/er011)コード変更/`.gitignore`変更/pip install/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。片方のlevelだけ完成した場合はその旨をStatusに明記。

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

> 完成済みcanonical articleを使い、既存正式audio completion経路で、Key Phrase等音声化に必要な既存付帯要素の確認/TTS/A2 slowdown等既存level仕様/retry・fallback/Assembly/Intro・Outro・SFX/Audio Validation/完成episode/Web試聴playerまで進める。新しい記事生成は不要。記事内容を音声都合で勝手に変更しない。既存Production audio pathをそのまま使用できないgapがあれば、新仕様を作る前に既存資産で最小接続を優先する。完成条件: A2/B1双方について、完成episode音声あり/Audio Validation PASS/Web playerから再生可能/playerにlevelが明確/実際のcanonical articleと音声内容が一致。

## 事前指定Read一覧

1. Glob `er011_family_a_completion*.py`、`er011_*end_to_end*.py` → 見つかったscriptを Grep `^def |argparse|add_argument|editorial_mode|level|out_dir|run_key_phrases|assemble|verify_episode_audio_validation_gate|player` → 入口・引数・段階構成の該当範囲のみ。
2. `er011_output/family_a_completion_a2_trend_end_to_end_01/`: Glob `**/*.json` の一覧(ファイル名のみ)+`b1b/audit/tts_generation_results.json` L1-40(出力構造の把握)。
3. `CURRENT_SPEC.md`: Grep `A2 slowdown|A2.*speed|Intro|Outro|SFX|B1B.*Key Phrase|Audio Validation Gate` → 該当行のみ(level仕様の確認)。
4. `audio_review_player.py`: Grep `^def |src=|relative|title|level` → 引数のみ。
5. `er014_output/four_type_observation_01/trend/production_set_cost.json` 全文。
6. `er014_output/four_type_observation_01/trend/a2/`・`b1b/`: Glob `*.json`(ファイル名のみ。既存経路が要求する中間成果物[point structure等]の有無確認)。
7. `.gitignore`: Grep `wav|mp3|er014|output|audio`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver `trend/run_trend_audio_completion.py`(新規、既存関数を順に呼ぶ最小接続、budget_jpy=150、level引数a2/b1b)。出力: `trend/audio/a2/{key_phrases/,tts/,assembled/,audio_validation.json,player.html,web/episode.mp3,web/segments/*.mp3,article_audio_consistency.json}`、`trend/audio/b1b/`同構成、`trend/audio/cost_summary_audio.json`、`trend/production_set_cost.json`更新、`trend/audio/web_delivery.json`(mp3サイズ・duration・gitignore確認)。`er014_output/four_type_observation_01/progress_log.md`に1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-TREND.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-TREND_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_audio_completion.py --level a2` → 同 `--level b1b`(driver内でarticle path/out_dir/budget固定。全文コマンドを記録)
3. 確認: `Select-String -Path er014_output\four_type_observation_01\trend\audio\*\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)
4. `git check-ignore -v er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3`(exit code記録)
(回帰: Productionコード変更なしのため不要。driverはer014_output配下のTrial driver扱い。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(Trend音声化完成、duration、追加費、総原価)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外可・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_TREND.md`に: 1) 最終Status(A2/B1Bそれぞれ完成/未完成)、2) 使用した既存経路(script・関数名)とgap/最小接続の内容、3) Key Phrase A2/B1B(5件ずつ: phrase/gloss、Validator結果、再呼び出し回数)、4) Preview/Comment等の生成要素一覧、5) TTS(call数、retry/fallback発生、slowdown等の適用値)、6) Audio Validation結果(PASS/FAIL、segment数)、7) 完成episode duration(A2/B1B)、8) 記事⇔音声一致確認結果、9) mp3一覧(パス・サイズ・duration)、player相対参照確認、予定URL、gitignore確認、10) 費用: 音声化追加費(level別・要素別)、**Trend Production 1生成セット総原価=¥174.03+追加費=¥xx.xx**、11) model_id/TTS model、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥150)
- [x] 並行タスク衝突回避あり(trend/配下限定・Git操作なし)
