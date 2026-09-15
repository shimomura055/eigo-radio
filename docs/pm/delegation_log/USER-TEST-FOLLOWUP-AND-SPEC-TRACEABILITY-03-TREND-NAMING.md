## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING(B1B→B1 名称整理)
並行タスク衝突確認: 並行して Discovery(`.../discovery/`)、Family C(er013)、仕様追跡調査(docs/pm調査文書)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下と`docs/pm/b1b_naming_investigation.md`(新規)のみを書く。CURRENT_SPEC/REPORT等のSSOT・正式文書は編集せず**修正案(行番号付き)を提示**する(統合タスクが反映)。Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FU03_TREND_NAMING.md`(新規)。API不使用(費用¥0)。

## 性質/到達上限Status/禁止事項

- ユーザー指示: Trend A2/B1(内部ID b1b)は試聴OK、追加作業なし。ただしユーザー向け名称として「B1B」は使用しない。まず「B1Bが内部compatibility identifierとして必要か/単なるhistorical namingか」を確認。内部コード上必要なら内部IDは残してよい。player表示・REPORT・CURRENT_SPEC・ユーザー向け名称・今後の完成報告は原則「B1」へ統一。既存runtimeを壊すためだけのdirectory renameは不要。Alexa+時間差再生成PASSはOPEN-153の観測evidenceとして保持(変更なし)。
- 調査(read-only): (1) `b1b`/`B1B`/`B1-B`が使われている箇所を分類: (a) コード上の識別子(level文字列比較、dict key、required_structure、cost集計key、ファイル/ディレクトリ名依存)=内部compatibility、(b) 表示文字列(player title/label、REPORT見出し、index.html、CURRENT_SPECのユーザー向け記述)、(c) 歴史的命名(B1A/B1B比較Trialの名残)。CURRENT_SPECで「B1B」の定義・由来(B1A/B1Bの選定履歴)を該当行だけ確認し記録。(2) 内部IDを残す/表示だけB1にする方針の妥当性を根拠付きで判定。
- 修正(表示のみ): Trend player(`trend/audio/b1b/player.html`)のTitle/level表示を「B1」に(内部パスは不変、注記「internal id: b1b」を小さく残す)。playerは音声・segment構成を変えず表示文字列のみ再生成(既存player生成関数の`level`表示引数で対応。無理ならHTMLの表示文字列のみ置換し、`file:///`不在を確認)。`trend/audio/web_delivery.json`・`index.html`は統合タスクが更新するため触らない(修正案を提示)。Discovery側の同様の変更はDiscoveryタスクが行うため触らない。
- 修正案の提示: CURRENT_SPEC/直近REPORT(`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`、`EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`)/`index.html`/PM_BRIEFのユーザー向け表記で「B1B」→「B1」へ置換すべき箇所を行番号付きで一覧(内部ID・過去の履歴記述はそのまま残す方針)。今後の完成報告での命名ルール文案(「ユーザー向け=B1、内部ID=b1b(必要な場合のみ注記)」)。
- 禁止: コード上の内部ID変更/ディレクトリrename/Production・Trialコード変更/SSOT編集/Git/API呼び出し。

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

> Trend B1B → B1名称整理: ユーザー向け名称としてB1Bは使用しない。まずB1Bが内部compatibility identifierとして必要か、単なるhistorical namingかを確認。内部コード上必要なら内部IDは残してよい。ただしplayer表示/REPORT/CURRENT_SPEC/ユーザー向け名称/今後の完成報告は原則B1へ統一。既存runtimeを壊すためだけのdirectory renameは不要。

## 事前指定Read一覧

1. Grep `b1b|B1B|B1-B` in `*.py`(ルート直下、`er0*_output`除外)→ 出現ファイル・行の一覧(count+content、head 120行)。level比較・dict key・required_structure・cost keyの該当行のみRead。
2. `CURRENT_SPEC.md`: Grep `B1B|B1A|B1-B` → 定義・由来行のみ。
3. `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`、`EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`、`er014_output/four_type_observation_01/index.html`、`docs/pm/PM_BRIEF.md`: Grep `B1B|b1b` → 行番号一覧のみ。
4. `er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py`: Grep `player|level|title|audio_review_player` → player生成呼び出しの該当範囲のみ。`audio_review_player.py`: Grep `^def |level|title` → 引数のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `docs/pm/b1b_naming_investigation.md`(分類表・判定・修正案一覧・命名ルール文案)、`trend/audio/b1b/player.html`(表示のみ更新)、`trend/build_player_b1_label.py`(表示更新script、音声無変更)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\build_player_b1_label.py`
3. 確認: `Select-String -Path er014_output\four_type_observation_01\trend\audio\b1b\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`Select-String -Path er014_output\four_type_observation_01\trend\audio\b1b\player.html -Pattern "B1B" | Measure-Object -Line`(内部ID注記の1件以下)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにCURRENT_SPEC/DECISION_LOG向けの命名ルール文案と置換箇所一覧を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_TREND_NAMING.md`に: 1) 判定(内部compatibility identifierか/historical namingか、根拠行)、2) 分類表要約(コード内部/表示/履歴)、3) Trend player表示更新結果、4) 置換箇所一覧(ファイル・行番号・旧→新)と命名ルール文案、5) commit対象候補、6) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(trend/配下+調査文書のみ・Git操作なし)
