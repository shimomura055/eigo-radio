## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_05: 見積→¥10判定→本実行(Ledger側→記事側shard×3並列→merge)→集計・前回比regression)。**書込先: `er052_output/open233_directional_misread_trial_02/`配下(`estimate_02.md`、`run/`、`run/shard_*/`、`trial_summary_02.*`、`regression_vs_trial01.*`)、`docs/pm/RESULT_PACKET_TRIAL02_05.md`、`docs/pm/delegation_log/`。scriptの修正は整合に必要な最小限のみ(`er052_open233_directional_trial_02.py`、aggregate_trial_02.py)。Production code・SSOT・gold・git操作なし。**
作業方式: 説明最小、Bash heredoc不使用、長時間処理はbackground化してログをファイルへ。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: 有料限定Trial(上限¥10、ユーザー承認済み「¥10以内なら追加承認なしで実行、超過見込みならSTOP」)。到達上限: 集計完了(Status分類はFable)。禁止: 残11 run/Production変更/floor復活/gold・KPI変更/新Safety原則/¥10超過(各process `--budget-yen`で強制、累計管理)/合格基準未達時の追加修正Trial(勝手に進まない)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_05.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3(有料): 見積low/mid/highを`estimate_02.md`に記録→mid≤¥10で実行。累計¥10到達で停止し完了分のみ集計。実費はcall_logから算出し領収(¥)をRESULT_PACKETへ。

## ユーザー指示(原文、要点)
> 費用: Trial上限¥10。¥10以内なら追加承認を待たず実行してよい。超過見込みならSTOPして報告する。
> Trial本実行も、順序依存がなく条件同一性を保てるなら複数processで並列化する。
> 合格基準(事前登録): HC-012 3/3、A5-0 3/3、正常文の誤重大判定2%以下、不要Rewrite見込み0.67の半分(0.335件/run)以下、前回誤爆3件(F-09/F-10/F-19)解消、新しい重大見逃しなし。

## Fable固定方針
- 構成: same_blind(TRIAL-01と同じmodel gpt-6-luna、effort=medium)。Ledger側`--ledger-repeat 3`(10 fact=30 call)。記事側はtestset_02の`repeat`に従う(Σ81 call)。
- 並列: Ledger側完了後、記事側を`--article-shard 1/3, 2/3, 3/3`の3 processを同時にbackground起動(各`--budget-yen`=(10−Ledger側実費)/3)。全shard完了後`--merge`(meta hash一致検証)。
- Ledger事象リスト外の人工反転7件(`outside_event_list=true`、S-01〜06/S-11): 実行はするが**合格基準の母数から除外し参考集計**。前回(TRIAL-01)検出していたものを今回見逃した場合は「新しい重大見逃し候補」として明記(判断はFable)。
- 集計は`aggregate_trial_02.py`(委任_03)+`regression_vs_trial01.py`。`ledger_truth_02.json`(委任_02)を`--truth`に使用。scriptと成果物のkey不整合があれば**集計側を合わせる**(Trial scriptの判定ロジックは変えない)。

## 作業内容
A. 見積: `--dry-run`のprompt文字数/3.5×単価+推論token(effort=medium≒300〜1000 tok/call)で、Ledger側30 call+記事側81 callのlow/mid/highを`estimate_02.md`へ。**mid>¥10ならSTOP**(実行せず報告)。
B. 実行: `docs/pm/RESULT_PACKET_TRIAL02_01.md`の本実行コマンド例に従い、(1)`--ledger-only`→`run/ledger_cache.json`(2)shard×3 background同時起動(ログ`run/shard_i.log`)→完了待ち(3)`--merge run/`→`run/results_merged.jsonl`+`summary`。失敗callは1回retry→UNCLEAR記録。
C. 集計: `aggregate_trial_02.py --results run/results_merged.jsonl --ledger-cache run/ledger_cache.json --truth ledger_truth_02.json --testset testset_02.json --population ../open233_directional_misread_trial_01/population_01.json --prev ../open233_directional_misread_trial_01/trial_summary_01.json --out .` → `trial_summary_02.{json,md}`(合格基準表6項目の充足/未達と根拠数値、outside_event_list別集計を含む)。`regression_vs_trial01.py`→差分表。
D. gold別・前回誤爆3件別のrepeat別内訳(選択subject/ledger_state/article_state/compare)を`trial_summary_02.md`末尾に表で出す(G-01/G-02/G-03/F-09/F-10/F-19/G-04〜06)。
E. `docs/pm/RESULT_PACKET_TRIAL02_05.md`: 見積・実費(Ledger側/shard別/合計)・並列実行の実時間(Ledger側開始〜merge完了、shard各所要)・合格基準表・T-0・逸脱・一覧外Read理由。

## 事前指定Read/Grep一覧
1. `docs/pm/RESULT_PACKET_TRIAL02_01.md`、`docs/pm/RESULT_PACKET_TRIAL02_03.md`、`docs/pm/RESULT_PACKET_TRIAL02_02.md`: 全文(短い)。
2. `er052_open233_directional_trial_02.py`: Grep `add_argument|def main|def merge` →範囲Read。
3. `testset_02.json`/`ledger_truth_02.json`: 先頭20行(構造)。

## 事前指定Grep一覧+追記位置・更新位置の手順
(上記「事前指定Read/Grep一覧」に同じ。追記位置: `docs/pm/RESULT_PACKET_TRIAL02_05.md`末尾、`trial_summary_02.md`末尾。SSOT追記なし。)

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_05.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_05.md_check.json`
2. 上記A〜Cのコマンド(RESULT_PACKET_TRIAL02_01.mdの例に引数を合わせる。`--effort medium --budget-yen <残額>`必須)。

## SSOT追記文
なし(Fableが委任_06で反映)。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL02_05.md`。最終報告10行以内(見積mid・STOP有無・実費・合格基準6項目の充足/未達・HC-012/A5-0/D61のk/3・前回誤爆3件の結果・正常文誤重大判定率・不要Rewrite見込み3水準・並列実時間)。
