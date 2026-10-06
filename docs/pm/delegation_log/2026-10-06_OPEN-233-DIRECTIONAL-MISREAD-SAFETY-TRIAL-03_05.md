## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_05: 見積→¥8判定→本実行(Ledger側phase付き再抽出→記事側X/Y×3 shard=6 process同時→merge)→集計・前回比)。**書込先: `er052_output/open233_directional_misread_trial_03/`配下(`estimate_03.md`、`run/`、`run/{X,Y}/shard_*/`、`trial_summary_03.*`、`regression_vs_trial02.*`)、`docs/pm/RESULT_PACKET_T03_05.md`、`docs/pm/delegation_log/`。scriptの修正は整合に必要な最小限のみ(集計側を合わせる。Trial scriptの判定ロジックは変えない)。testset_03.json/ledger_truth_03.jsonは凍結済み(変更禁止、実行前にsha256照合)。Production code・SSOT・git操作なし。**
作業方式: 説明最小、Bash heredoc不使用、長時間処理はbackground化しログをファイルへ。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安20分。

## 性質/到達上限Status/禁止事項
性質: 有料限定Trial(上限¥8、ユーザー承認済み「上限内なら追加承認なし、超過見込み時のみSTOP」)。到達上限: 集計完了(Status分類はFable)。禁止: 残11 run/Production変更/floor復活/gold・KPI変更/testset・正解の変更/¥8超過(各process `--budget-yen`で強制、累計管理)/合格基準未達時のTRIAL-04自動移行/新構造追加。Opus Gate: 設計承認済み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_05.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3(有料): 見積low/mid/highを`estimate_03.md`に記録→mid≤¥8で実行。累計¥8到達で停止し完了分のみ集計。実費はcall_logから算出し領収(¥)をRESULT_PACKETへ。

## ユーザー指示(原文、要点)
> Trial費用上限¥8。見込み約¥6。上限内なら追加承認なしで実施。¥8超過見込みの場合のみSTOP。本実行も同一条件・再現性・予算管理を維持できる範囲でshard/process並列化する。実行後に都合よくtestsetや正解を変更しないこと。合格基準8項目(HC-012 3/3/A5-0 3/3/D61≥2/3/held-out重大例平均≥2/3かつ全例≥1/3/正常43件+held-out正常例の不要重大判定0/不要Rewrite見込み0/新たな重大見逃し0/前回解消誤爆3件の再発なし)。未達でもTRIAL-04へ自動移行しない。

## Fable固定方針
- model gpt-6-luna、effort=medium(TRIAL-02と同じ)。Ledger側`--ledger-only --ledger-repeat 3`(10 fact=30 call)を1回実行し`run/ledger_cache.json`に固定。X/Yは**同一キャッシュ**を使用。
- 記事側: X/Y各`--article-shard 1/3,2/3,3/3`の6 processを同時background起動(各`--budget-yen`=(8−Ledger側実費)/6)。`--population`は**渡さない**(v3では行フィルタの意味)。フォールバックcallは各process内で発生(予算に含む)。
- 実行前: `FREEZE_03.json`のsha256とtestset_03.json/ledger_truth_03.jsonの現sha256を照合し一致を記録(不一致ならSTOP)。
- 基準7の解釈(Fable固定): 「新たな重大見逃し」=TRIAL-02(blind)でrep0 REVERSEDだったgold・事象リスト内人工反転が今回REVERSED以外になる件数。事象リスト外7件(outside_event_list)は参考集計。
- 集計: `aggregate_trial_03.py --results-x run/X/results_merged.jsonl --results-y run/Y/results_merged.jsonl --ledger-cache run/ledger_cache.json --truth ledger_truth_03.json --testset testset_03.json --population ../open233_directional_misread_trial_01/population_01.json --prev-summary ../open233_directional_misread_trial_02/trial_summary_02.json --prev-results ../open233_directional_misread_trial_02/run/results_merged.jsonl --out .`、`regression_vs_trial02.py`。key不整合は集計側で吸収。

## 作業内容
A. sha256照合→見積(dry-run出力のprompt文字数/3.5×単価+推論token≒300〜1000/call、Ledger30+記事側111+フォールバック見込み(dry-runの発動率は無意味のため、NONE率≈10%と仮定)でX/Y合計low/mid/high)→`estimate_03.md`。**mid>¥8ならSTOP**。
B. 実行(時刻を記録): Ledger側→6 process同時起動(ログ`run/{X,Y}/shard_i.log`)→完了待ち→X/Y各`--merge`。失敗callは1回retry→UNCLEAR。
C. 集計: 上記コマンド→`trial_summary_03.{json,md}`(合格基準表8行×X/Y、held-out別表、gold/誤爆3件/held-outのrepeat別内訳表(selected_subject/article_phase/matched_event_phase/ledger_state/article_state/compare/fallback_used)、フォールバック発動一覧、phase精度、AI揺れ、費用/run 3水準、前回比)。
D. `docs/pm/RESULT_PACKET_T03_05.md`: sha256照合結果、見積、実費(Ledger/X shard別/Y shard別/フォールバック分/合計)、実時間(Ledger開始→merge完了、各shard所要、6並列の実効短縮)、合格基準表X/Y、T-0、逸脱。

## 事前指定Read一覧
1. `docs/pm/RESULT_PACKET_T03_01.md`、`T03_02.md`、`T03_03.md`: 全文。
2. `er052_output/open233_directional_misread_trial_03/FREEZE_03.json`: 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
`er052_open233_directional_trial_03.py`: Grep `add_argument`→引数確認のみ。集計側修正が必要な場合は`aggregate_trial_03.py` Grep `def load|keys|get(`→範囲Read→最小Edit。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_05.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_05.md_check.json`
2. sha256照合(testset_03.json/ledger_truth_03.json)。
3. 本実行(RESULT_PACKET_T03_01.mdのコマンド例に`--effort medium --budget-yen <残額>`)。
4. 集計(上記)。

## SSOT追記文
なし(委任_06で反映)。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_T03_05.md`。最終報告12行以内(sha256一致、見積mid、STOP有無、実費、合格基準8項目のX/Y充足/未達、HC-012/A5-0/D61/held-out重大4件のk/3、正常文+held-out正常の誤重大件数、前回誤爆3件、フォールバック発動数、実時間)。
