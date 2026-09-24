## 管理ID

`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`(Fableからの修正指示1回目、Step 1 STOPからの再開)。並行タスクあり: 別sonnet-workerが`TOPIC-SELECTION-SEARCH-TRIAL-03`(er016_output配下、一時ファイル`_TS3`接尾辞)を実行中。本タスクは`er016_*`に触らず、一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`を継続使用、commit時`index.lock`は10秒待ち再試行(最大3回)、自タスクのファイルのみ明示add。

## 性質/到達上限Status/禁止事項

前回委任(`docs/pm/delegation_log/NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01.md`)の性質・上限Status(`VALIDATED`)・禁止事項・費用上限(¥40、既使用¥1.47)・Prompt完全同一・R3禁止・主観評価禁止・SSOT無変更はすべてそのまま有効。本指示は以下の2点のみ変更する。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。本指示は`docs/pm/delegation_log/NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_fix01.md`へ保存。

## ユーザー指示(原文)

前回委任文に転記済み(変更なし)。関連箇所の再掲: 「Source選定: 既存Trialで使用済みのSource・検索結果・Research artifactを優先的に再利用する。不足時のみ検索してよい。ただし今回の目的はSource Discoveryではないため、新しい面白い切り口探し/Source数を無駄に増やす/関係の薄い関連記事を混ぜることはしない。10記事条件では、同一事象について事実補完できる記事を使う。」

## 事前指定Read一覧

- `er015_output/news_meta_source_volume_format_trial_01/sources_10.md`/`sources_10.json`/`search_log.json`/`stop_reason.json`: 全文(現状8記事・検索2回の内容)。
- 前回委任文(delegation_log)の「事前指定Grep一覧+追記位置・更新位置の手順」Step 2〜4: 該当節のみ(手順は変更なし)。
- その他は前回委任で読んだ内容を保持して再利用(E-1)。

## 事前指定Grep一覧+追記位置・更新位置の手順

### 変更点1: 補充検索を追加で2 callまで許可(Fable判断。Query語彙を変える)
- 前回の2 callと異なる語彙で最大2 call(例: 英語媒体向け `Meta Muse "human concierge" contractors phone calls Reuters` / 日本語媒体向け `Meta Muse 電話 代行 人間 コンシェルジュ 契約スタッフ`)。同一事象(Meta Museの人間コンシェルジュ試験、2026-09-22 Reuters報道)を扱う記事のみ採用。関係の薄い記事(Muse一般発表・別機能)は採用しない。取得不能(403等)は除外し記録。
- 到達数N(8〜10)を`sources_10.md`に確定記録。**Nが10未満でもSTOPせず、条件3・条件4を「N記事」として続行する**(Fable判断: ユーザー指示は「関係の薄い記事を混ぜない」を優先しており、同一事象の記事がN件しか無い事実そのものが結果の一部。REPORT/RESULT_PACKETで「条件3=N記事(目標10、到達N)」と明記し、10未満の理由を記載)。
- 検索・要約の費用を`cost.json`に累計。

### 変更点2: 条件3/4の名称
- ファイル名・条件名は`cond3`/`cond4`のまま、REPORTと`inputs/cond3.md`冒頭に「N記事(目標10、到達N)」を明記。

### それ以外
- 前回委任のStep 2(4条件入力確定)→Step 3(4条件×3段=12 call、P7逐語・Luna・effort high・`previous_response_id`連鎖・R3なし)→Step 4(blind_r2.md/blind_key.json/comparison_all.md/REPORT)を**そのまま実行**。条件4 Ledgerは条件3で使ったN記事の取得本文(`fetched/`)からLuna 1 call(effort medium、web_searchなし)でPhase B Ledger形式へ変換、`status: TRIAL_UNVERIFIED`、別Source追加禁止、URL集合一致の機械確認、`info_set_diff.md`作成。取得本文が無い記事は要点文で代替し明記。
- STOP条件は前回どおり(10記事未到達は本指示によりSTOP対象から除外)。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step sources --target 10 --extra-search-calls 2 --allow-partial
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step inputs
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step generate --conditions 1,2,3,4 --stages 0,1,2
.venv\Scripts\python.exe er015_news_meta_source_volume_format_trial_01.py --out-dir er015_output\news_meta_source_volume_format_trial_01 --step assemble
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_fix01.md --json-out docs\pm\delegation_log\NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_fix01.md_check.json
git status --short
```
(`--allow-partial`=到達数8以上なら続行するフラグを追加実装。`--extra-search-calls`=追加検索上限。)

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: 前回と同じ対象(`er015_news_meta_source_volume_format_trial_01.py`、`er015_output/news_meta_source_volume_format_trial_01/`配下[`fetched/`は除外]、`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01_fix01.md`、同`_check.json`)。
メッセージ: `NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01: 補充検索後N記事で4条件(1記事/前回Baseline/N記事要点/N記事Ledger)×Original→R1→R2を生成、ブラインド比較資料作成(Luna、Prompt同一、Production変更なし)`
trailer: `Management-ID: NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`

## 報告(RESULT_PACKET項目)

前回委任の報告項目0〜8をそのまま(項目2に「追加検索の内容・到達数N・10未満の理由」を追記)。加えて: 条件4 Ledgerのfact数・URL集合一致・`info_set_diff.md`要約、`blind_r2.md`/`blind_key.json`/`comparison_all.md`の絶対パス、12 callのmodel実値・費用合計(¥40以内か)、commit SHA・push結果。
