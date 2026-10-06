## 管理ID

OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02(委任_02: ユーザー承認[上限¥20]を受け、委任_01で準備済みの現行設計のまま本実行→集計→記録。委任_01は見積mid¥13.8>¥12で実行前STOPしていた)。並行タスクなし。本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限 **VALIDATED**(Production採用ではない)。最終分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFableが行う。Sonnetは事実と【確認】/【推測】ラベル付き所見を報告し、受入条件・STOP条件それぞれへの該当/非該当を事実として列挙する。
- **script・promptは委任_01で準備済みのものを変更しない**(`er052_output/open233_reclassify_02/reclassify_candidates_02.py`、4観点[主体/相手先・対象/範囲/限定条件]を個別確認する現行prompt、出力簡素化なし、モデルgpt-6-luna・effort=medium・run単位1 call、01と同一構成)。run/agg段階で未検証の不具合(例外・parse失敗等)が出た場合のみ最小修正し(prompt文言・判定規則は変えない)、修正内容を記録する。
- 禁止: 「Ledgerに明記されていない」だけでの候補化/修辞文の再候補化/機械Checker・後段AI・機械Safetyルール・Production Checker・gold定義・KPIの変更/E2E残11 run再開/runner・coverage_checker変更/01出力の上書き/新しい数値KPI設定/STOP時の勝手な改善実装。
- 費用: **ユーザー承認上限¥20**。`--budget-jpy 20`。実費または確実な見込みが¥20超となる時点でSTOP(以後のrunを実行せず、完了分だけ集計)。api/parse失敗は1回だけ再試行、再発runはskip記録(集計で欠損明示)。Fable/Sonnet判断で予算枠を拡大しない。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **非該当**(Trial用分類promptの実行・集計のみ、構造変更なし)。
- `git add -A`・`stash`・`amend`禁止。`ACTIVE_TASK.md`・`RESULT_PACKET.md`のadd禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ**逐語で(要約・圧縮せず、本委任文の全文をそのまま)**保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。委任_01はT-0 FAIL(要点圧縮版保存)だったため、今回は全文保存を厳守する。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTSを伴う委任は実行前に(1)差分再生成可否、(2)音声再利用キャッシュ、(3)`--budget`明示、(4)想定外の全再生成判明時はAPI実行前STOP、の4点を必須とする。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は通常「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。**ただし本委任はユーザーが「実費または確実な見込みが¥20超でSTOP・予算枠拡大禁止」を明示しているため、ユーザー承認済み上限¥20が優先し、超過見込み時点でSTOPする**(T-3の「ユーザー承認済みの総予算・個別run上限・STOP条件を優先」に基づく)。暴走疑い時(同じ失敗の無意味なretry loop・想定外の大量call・費用増加の原因が説明できない)も即STOPし、原因・既使用額・残作業を報告する。

## ユーザー指示(原文)

> 管理ID：OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02
> ユーザー判断：今回Trialの実行上限を ¥20 まで承認する。したがって、前回準備済みの現行設計のまま本実行へ進めてよい。
> 実行条件: 4観点(主体 / 相手先・対象 / 範囲 / 限定条件)を個別に確認する現行Promptを維持する／出力簡素化は不要／前回と同じ42 runを使用／Production Checkerは変更しない／KPI変更なし／gold変更なし／後段AI・機械Safetyルールは変更しない／E2E残11 runは再開しない
> 必ず確認すること: A4-0：3/3で候補として残るか／正式gold 6種類：すべて維持できるか／hold-out 9種類、K19、neg5等を悪化させないか／通常記事候補数：前回 9.83件/記事 からどう変化したか／AI由来候補数：前回 5.33件/記事 からどう変化したか／2方向和集合の結果／旧「何でも候補」仕様側へ戻っていないか／実費
> STOP条件: 実費または確実な見込みが ¥20超／goldを落とす／A4-0が安定して残らない／候補数が大きく旧過剰仕様へ戻る／新しいSafety問題を発見／Trial中に追加仕様変更が必要になる。STOP時は勝手に次の改善を実装しないこと。
> Status: 今回到達してよい最大Statusは VALIDATED。Trial終了時に必ず REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれかへ分類する。VALIDATEDでもProduction採用ではない。本実行 → 集計 → 必要な記録更新まで進め、結果を報告してください。

## KPI provenance欄

- Before(比較基準): reuse(段階A 42 run保存候補 `er052_output/open233_stage1_stageA_01/`)および前回Trial01結果(`er052_output/open233_reclassify_01/reclassify_aggregate.json`、frozen)。
- After: fresh(精緻化promptによる分類call 42回)をreuse候補集合へ適用。Checker本体再実行なし。
- E2E自己確認: No。
- 判定単位: run別・instance群別(SC 6×3/B2_hormuz n=3/NORMAL 6×2/hold-out 9)。gold 6件×sample別。

## Opus台帳更新

OF-027(EVIDENCED)に本Trial02の結果を1行追記(状態は変えない)。他は該当なし。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET.md`: 全文(委任_01の報告。見積内訳・prompt差分を引き継ぐ)。
2. `docs/pm/reclassify_open233_checker_selectivity_02.md`: 全文(委任_01で作成済みのTrial記録。結果節を追記)。
3. `docs/pm/reclassify_open233_checker_selectivity_01.md`: L1-L60(01の結果表、比較用)。
4. `er052_output/open233_reclassify_02/cost_estimate.json`: 全文。
5. `er052_output/open233_reclassify_02/reclassify_candidates_02.py`: Grep `def main|--stage|budget|agg` →stage分岐・集計関数の範囲のみ(動作確認用。変更しない)。
6. 実行後の出力(`er052_output/open233_reclassify_02/reclassify_aggregate.json`等): 集計結果のみRead(run別生出力を全件全文Readしない)。gold落ち・A4-0落ちがあった場合のみ該当runのclaim記録をGrepで該当範囲Read。
7. `docs/pm/ACTIVE_TASK.md`: 全文(固定ヘッダ踏襲)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `RECLASSIFY-02(2026-10-06、委任_01)` →同行の当該箇所の直後へ委任_02の結果を追記(実測値)。
- `docs/pm/REPORT_LEDGER.md`: Grep `RECLASSIFY-02 委任_01` →直後へ1行。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## §78|§78` →§78末尾へ「§78-2 本実行結果(委任_02)」を追記。
- `DECISION_LOG.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02` →既存エントリ末尾へ「ユーザー判断(上限¥20承認、現行設計のまま実行、逐語)」と結果を追記。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-027` →該当行へ結果1行追記。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(Status=「Trial02本実行完了・Fable分類待ち」+事実)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02_02.md_check.json`
2. 本実行: `.venv\Scripts\python.exe er052_output\open233_reclassify_02\reclassify_candidates_02.py --input-dir er052_output\open233_stage1_stageA_01 --out-dir er052_output\open233_reclassify_02 --stage run --yes-run-paid --budget-jpy 20`(内部見積midが予算を超えるとSTOPする仕様なので、予算¥20≥mid¥13.8で実行可能なことを確認)
3. 集計: `.venv\Scripts\python.exe er052_output\open233_reclassify_02\reclassify_candidates_02.py --input-dir er052_output\open233_stage1_stageA_01 --out-dir er052_output\open233_reclassify_02 --stage agg`
4. 記録: Trial記録02へ結果節追記、SSOT(上記)、ACTIVE_TASK、RESULT_PACKET。
5. `git status --porcelain`→明示add→commit→push。

集計で必ず出すもの(段階A Before/01/02を並記): 候補数(全体/NORMAL/SC/B2_hormuz/hold-out、all=決定論込み/llm=AI由来のみ、件/記事)、**NORMAL 01の9.83→02、AI由来 5.33→02**、経路別(r3/r5)と2方向和集合(01: 和集合8.12)、**gold 6件×sample別残存表(A4-0 3/3か。01は2/3)**、hold-out 9種、監視項目(neg5 B3-same 01:3/3、K19 01:3/3、HF-011 01:候補なし)、4観点のmismatch分布(actor/counterpart/scope/qualifier別件数、CANDIDATE化への寄与)、A4-0各sampleの4観点判定と理由テキスト、CANDIDATE/NO_FACT_CLAIM/SUPPORTED内訳(01: 190/177/159)、02で新たにCANDIDATEになった文の例10件(NORMAL、妥当性【推測】付き)、01でNO_FACT_CLAIMだったものが02でCANDIDATEへ戻った件数(修辞文の再候補化チェック)、「明記されていないだけ」でCANDIDATEになっている境界例の件数(01は2件)、実費(call数・token・円、較正済み見積mid¥13.8との差)、欠損run。

## SSOT追記文

- OPEN_ITEMS.md(RECLASSIFY-02委任_01記述の直後): 「委任_02(2026-10-06、ユーザー上限¥20承認): 本実行(¥X.XX): NORMAL候補 01の9.83→?件/記事(AI由来5.33→?)、全体?、r3 ?/r5 ?/和集合?、gold ?/6(A4-0 ?/3)、hold-out ?/9、neg5 ?/3、K19 ?/3、修辞文再候補化?件、境界例?件。Fable分類: [Fableが記入]。KPI・Checker本体・gold不変、Production未変更。」(Fable分類欄は「Fable分類待ち」と書く)
- REPORT_LEDGER.md: 「- 2026-10-06 | OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02 委任_02 | 4観点prompt本実行(¥X.XX): NORMAL候補9.83→?(AI由来5.33→?)、gold ?/6(A4-0 ?/3)、hold-out ?/9、和集合?。REPORT §78-2。」
- REPORT §78-2、DECISION_LOG追記、OF-027追記: 上記。

## Git

明示add対象のみ: `er052_output/open233_reclassify_02/`配下の新規・更新ファイル(runs/・reclassify_aggregate.json・budget_state.json等)、`docs/pm/reclassify_open233_checker_selectivity_02.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02_02.md`(+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET.md`はaddしない。
コミットメッセージ: `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02: 4観点prompt本実行(ユーザー上限¥20承認)【NORMAL候補9.83→?(AI由来5.33→?)、gold ?/6(A4-0 ?/3)、hold-out ?/9、和集合?、¥X.XX】、REPORT §78-2(委任_02)`(実測値で埋める)
SSOT編集権: あり(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/REPORT)。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`は編集しない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ(委任_01の内容は「委任_01経緯」として要約保持): 1. T-0結果。2. 実行構成が委任_01準備済み・01と同一(モデル/effort/入力)であることの確認、scriptの最小修正の有無。3. 実費・見積差・欠損run。4. 候補数Before→01→02(全区分)、NORMAL 9.83→?、AI由来5.33→?。5. gold 6件×sample表(A4-0 3/3か。落ちた場合は理由テキスト・4観点判定・Ledger原文並記)。6. hold-out/neg5/K19/HF-011(01比の悪化有無)。7. 2方向(r3/r5/和集合)と和集合でのgold残存。8. 4観点mismatch分布、A4-0各sampleの4観点判定、新規CANDIDATE例10件、修辞文再候補化件数、境界例件数。9. 【確認】/【推測】所見: 受入条件(A4-0 3/3・gold 6/6・検証セット悪化なし・削減効果維持)とSTOP条件(¥20超・gold落ち・A4-0不安定・旧過剰仕様回帰・新Safety問題・追加仕様変更要)の各項目へ該当/非該当を事実で列挙(最終分類はしない)。10. 一覧外Read理由。11. commit hash・push結果・raw.githubusercontent.com URL。12. 成果物一覧。
