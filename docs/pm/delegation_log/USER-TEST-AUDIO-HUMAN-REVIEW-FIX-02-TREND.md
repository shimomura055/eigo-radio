## 管理ID

USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND(Trend A2 `point_two` 承認付き再生成1回→完成)
並行タスク衝突確認: 並行して Family C(er013)、Discovery(`.../discovery/`)、Voices(`.../voices/`)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FIX02_TREND.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Trend A2の残り1 segment(`point_two`、「Alexa+」表記揺れでHuman Review Cost Guardロック中)について、**ユーザー承認(2026-09-15)**: 「同一テキストで追加再生成を1回だけ許可。時間差/run-to-run varianceの観測も兼ねる。同一canonical text/同一Production path/1回のみ/Human Review Lock承認付き/結果を時間差runとして記録。通れば完成。通らなければ自動retry継続禁止、OPEN-153へ再発例として記録」。
- 手順: (1) 現在のlock状態(`trend/audio/a2/audit/review_lock_state.json`の`point_two`エントリ、canonical_text_sha256、前回attempts)を記録。(2) `er011_human_review_lock_01.approve_regenerate()`を`point_two`に対して**1回だけ**呼ぶ(呼び出し時刻・引数・承認根拠=本委任文のユーザー承認をログに残す)。(3) 前回と**同一のcanonical text・同一のProduction関数・同一引数**(前回CONT1の`run_trend_audio_completion_2.py`が`point_two`に使った経路。読み整形はCONT1と同じ「Alexa+→Alexa Plus」適用済みテキストのまま変更しない)で1回生成→ASR検証。既存関数内部のretry構成(標準+fallback)は関数の既定どおり(それが「1回の再生成」)。(4) 結果を`trend/audio/a2/point_two_time_variance_run.json`に記録: 前回attempts(時刻・ASR結果・classification)と今回(時刻・ASR結果・classification)、経過時間、同一テキストsha256一致確認。(5) **通った場合**: A2 Assembly→Audio Validation Gate(緩和禁止)→WAV+mp3(B1Bと同方式)→標準player(`trend/audio/a2/player.html`、相対パス、Title/level=A2明記)→article/audio consistency(`trend/audio/tts_reading_transforms.json`の置換のみが差分であることを機械確認)→`web_delivery.json`→gitignore確認→費用更新。**通らなかった場合**: 追加retry禁止。lockは再びHUMAN_REVIEW_REQUIREDのまま。OPEN-153追記案(再発例: 時刻・ASR結果・揺れの方向)をRESULT_PACKETに記載しSTOP。
- なぜ既存QAで検出できなかったか(必須): 本件は「完成と報告」ではなくロックで正しく止まった例だが、ASR表記揺れ(記号ブランド名)が既存normalizerで吸収されない理由(該当関数・正規化ルール)を根拠付きで1段落記載。
- 費用上限: ¥40(point_two 1回+Assembly以降)。
- 禁止: `approve_regenerate()`の2回目以降/テキスト変更/読み整形の変更/Gate緩和/retry上限変更/Production(er003/er006/er011)コード変更/`.gitignore`変更/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 上記「通らなかった場合」/費用上限超過見込み/技術的にWeb配信不可。

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

> Trend A2 残り: point_twoのAlexa+。ユーザー承認: 同一テキストで追加再生成を1回だけ許可。目的は単純N増しだけでなく、時間差/run-to-run varianceの観測も兼ねる。同一canonical text/同一Production path/1回のみ/Human Review Lock承認付き/結果を時間差runとして記録。通れば完成。通らなければ自動retry継続禁止。その時点でOPEN-153へ再発例として記録。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_UT_TREND_2.md` 全文(前回到達点、point_twoの経路・テキスト)。
2. `er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py` 全文(point_two生成経路・Assembly以降の関数を再利用して`run_trend_audio_completion_3.py`を派生)。
3. `er011_human_review_lock_01.py`: Grep `def approve_regenerate|def check_before_generation|HUMAN_REVIEW_REQUIRED|approved` → 承認関数の引数・状態遷移のみ。
4. `er014_output/four_type_observation_01/trend/audio/a2/audit/review_lock_state.json`: Grep `"segment_id": "point_two"` -A 30 → 現エントリのみ。
5. `er014_output/four_type_observation_01/trend/audio/b1b/web_delivery.json` 全文(mp3/playerの生成方式を揃える)。
6. `er014_output/four_type_observation_01/trend/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver `trend/run_trend_audio_completion_3.py`(新規: approve→1回生成→記録→[PASS時]Assembly以降)。出力: `trend/audio/a2/point_two_time_variance_run.json`、`trend/audio/a2/{assembled/,audio_validation.json,player.html,web/episode.mp3,web/segments/*.mp3,article_audio_consistency.json}`、`trend/audio/web_delivery.json`(A2追記)、`trend/audio/cost_summary_audio.json`、`trend/production_set_cost.json`(Trend総原価=¥334.18+本タスク実費、差分明記)、`progress_log.md`1行。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_audio_completion_3.py --level a2 --approve-point-two-once`(budget_jpy=40。全文コマンド記録)
3. 確認: `Select-String -Path er014_output\four_type_observation_01\trend\audio\a2\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3`(exit 1)
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(A2完成/未完成)、OPEN-153追記案(時間差run結果: 通過/再発)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FIX02_TREND.md`に: 1) 最終Status(A2完成/未完成)、2) 承認記録(呼び出し時刻・対象・根拠)、3) 時間差run結果(前回/今回のASR・classification・経過時間・テキストsha256一致)、4) Audio Validation結果、5) duration、6) article/audio consistency、7) mp3・player・予定URL・gitignore確認、8) なぜ既存normalizerで表記揺れを吸収できないか(根拠)、9) 費用(本タスク実費、**Trend総原価=¥334.18+実費=¥xx.xx**)、10) model_id/TTS/ASR model、11) OPEN-153追記案、12) commit対象候補一覧、13) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥40)
- [x] 並行タスク衝突回避あり(trend/配下限定・Git操作なし)
