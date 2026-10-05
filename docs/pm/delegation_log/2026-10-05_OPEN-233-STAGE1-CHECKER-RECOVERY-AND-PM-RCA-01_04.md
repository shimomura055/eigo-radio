# 委任_04 委任文(全文保存、2026-10-05)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_04、PM RCA軸の反映)。**並行タスクあり**: 委任_03(設計案比較・Opus packet: 新規文書`docs/pm/design_open233_stage1_redesign_01.md`/`docs/pm/opus_packet_open233_stage1_redesign_01.md`/`er052_output/open233_kpi_recovery_02_offline_01/stage1_redesign_offline_eval_01.*`のみ作成、git操作なし)。本委任はそれらに触れない。

## 性質/禁止事項

- 性質: ¥0・SSOT反映のみ。(a)ユーザー決定「予算追加+¥100」(下記原文)をDECISION_LOGへ逐語記録、(b)委任_02のPM RCA文書`docs/pm/pm_rca_open233_stage1_closeout_01.md`と委任_02ログをcommit、(c)再発防止A〜Fを`docs/pm/PM_GOVERNANCE.md`へ反映(Fable評価済み、下記)、(d)rep30の`VALIDATED`表記を`VALIDATED(条件付き: Stage 1はfrozen再利用31/V0差替え3/fresh4 run)`へ遡及再表記(CURRENT_SPEC/OPEN_ITEMS/REPORT §63)、(e)Opus指摘台帳の新設とOpus#8〜#15のbackfill(最低限#10の警告)、(f)`check_delegation_prompt.py`の必須語を現行テンプレートに整合。
- **Fable評価(逐語記録)**: 「委任_02の再発防止案A〜Fを以下のとおり採用する。A(KPI provenance 6区分: fresh/frozen/reuse/manual substitution/synthetic/Production formal path、件数内訳必須)・B(固定入力・差替えが1件でも含まれる場合は『E2E Safety KPI』と呼ばない=ユーザー文言どおり)・D(Closeout自己確認『このKPIはfresh Production初回pathを含むE2E値か』Yes/No必須、NoならE2E達成扱い禁止)・F(`VALIDATED(条件付き: <内訳>)`の修飾子方式、新Statusは作らない。条件付きVALIDATEDをProduction採用提案の材料にする際は経路内訳・自己確認結果・E2E未検証リスクの併記必須)を新設24節へ。C(Opus指摘トレーサビリティ: RAISED→FABLE_DECIDED→IMPLEMENTED/TRIALED→EVIDENCED→CLOSEOUT_CONFIRMEDの台帳`docs/pm/OPUS_FINDINGS_LEDGER.md`、Safety hole/BLOCKER/MAJOR相当とFable採用項目を『重要警告』として登録必須、未解決の重要警告がある状態でのCloseout禁止)を11-5へ。E(『第二段階』『別管理』『本委任では着手しない』『後回し』をdefer同等語として扱い、Safety未解決項目は独立Open ID・発火可能な再開条件・ユーザー明示承認なしにnon-blocking化禁止)を5節末尾へ追記し項目20(e)と統合。Closeout Mandatory Checkに項目27〜30(C・A+D・E・F)を追加。rep30は事実訂正として`VALIDATED(条件付き)`へ遡及再表記する(ユーザー決定2026-10-05の変更ではなく、その入力が条件付き値であった事実の明示)。委任文テンプレートに『KPI provenance欄』『Opus台帳更新』を追加。」
- 禁止: コード(Production/Trial runner)変更禁止。有料API禁止。委任_03の対象ファイルに触れない。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない(委任_02の2ファイルは本委任でadd)。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込み2,500文字以下。
- T-0: 本ログに全文保存(分割)、check実行・結果記録。ユーザー決定原文は本ログの````ブロックが転写元。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー決定(原文、全文。DECISION_LOGへ逐語記録)

````
予算追加
本管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 について、ユーザー判断により 追加で+¥100 の予算を認めます。
既存Phase残額とは別に、このタスクの改善・限定Trial・必要なE2E確認のために追加利用してよいです。
ただし、これは「使い切ってよい予算」ではありません。
- まず¥0分析
- 小規模確認
- KPI見込み確認
- 必要な範囲だけ追加Trial
の順を守ること。
無駄なN増し・重複Trial・不要なモデル比較は行わない。
3ループ以内でKPI達成を目指すための追加Guardrailとして+¥100を許可する。
想定外の大量API発火が必要になった場合は、追加予算が残っていてもSTOPして報告すること。
````

## 作業(要約)

1. T-0。
2. `DECISION_LOG.md`末尾: 見出し「## 2026-10-05 ユーザー決定 予算追加+¥100(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01)」+原文逐語(スクリプト転写)+Fable判断2行(「本管理IDの費用枠=Phase残額約¥138+追加¥100。順序¥0→小規模→KPI見込み→必要範囲のE2E。想定外の大量API発火はSTOP」)。続けて見出し「## 2026-10-05 Fable評価 PM運営Failure RCAと再発防止A〜F(同管理ID)」+上記Fable評価(逐語)+PM RCA文書パス。
3. `docs/pm/PM_GOVERNANCE.md`: Grep `^## `で構造確認→(i)新設24節「KPI provenance・条件付きKPIとE2E KPIの分離・Closeout自己確認・条件付きVALIDATED表記(2026-10-05ユーザー指示、OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01)」に24-1 A/24-2 B/24-3 D/24-4 Fを委任_02案文(`pm_rca_open233_stage1_closeout_01.md` §4)に基づき簡潔に(各≤12行)、(ii)11-5 Opus指摘トレーサビリティ(C)、(iii)5節末尾にE追記+項目20(e)参照、(iv)Closeout Mandatory Check項目27〜30追加、(v)委任文テンプレート(Grep `委任文テンプレート|RESULT_PACKET`)に「KPI provenance欄(6区分)」「Opus台帳更新」を追加。15節(コスト報告)との書式整合を確認し矛盾があれば注記。
4. `docs/pm/OPUS_FINDINGS_LEDGER.md`新設: 列=ID/日付/Opus#/区分(Safety hole・BLOCKER・MAJOR・採用項目)/指摘要旨(≤40字)/Fable採否/反映(委任#)/Evidence/Closeout確認/Status。backfill: Opus#10「Stage 1 recallが支配的リスク」「条件付きSafety値と代替なしE2E値の分離」→Status=OPEN(本管理IDで対応中)、Opus#11〜#15のSafety hole項目(各レビューの「Safety hole」節をGrepで列挙、採否は設計書§の記録に従う)、Opus#15 F1〜F4。
5. 遡及再表記: `CURRENT_SPEC.md`(Grep `rep30 VALIDATED|Trial結果: rep30`)→「rep30 VALIDATED(条件付き: Stage 1はfrozen再利用31 run/V0差替え3 run/fresh 3 call[4 run]。E2E Safety KPIではない。出典`rep30_stage1_provenance_01.md`)」。`OPEN_ITEMS.md`の`OPEN-233-KPI-RECOVERY-REDESIGN-02`行とOPEN-233本体行の`VALIDATED`表記に同修飾子。REPORT §63冒頭に同注記(1〜2行)。`docs/pm/production_wiring_report_open233_01.md` §1に同注記。
6. `docs/pm/tools/check_delegation_prompt.py`: 必須語リストを現行テンプレート見出し(「事前指定Read一覧」「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」「Git」「報告」「KPI provenance」等)に整合させ、見出し表記ゆれ(全角/半角・句読点)を許容。既存の委任ログ3件で動作確認(PASS/FAIL理由が妥当か)。
7. `OPEN_ITEMS.md`本管理ID行進捗「委任_04: 予算+¥100記録、PM RCA反映(PM_GOVERNANCE 24節/11-5/5節/Closeout 27〜30、Opus台帳新設)、rep30を条件付きVALIDATEDへ再表記。委任_03: 設計案比較・Opus#16 packet(並行)」。`REPORT_LEDGER.md`1行。`ACTIVE_TASK.md`(addしない)。
8. commit/push(明示add: DECISION_LOG、PM_GOVERNANCE、OPUS_FINDINGS_LEDGER、CURRENT_SPEC、OPEN_ITEMS、REPORT、wiring report、REPORT_LEDGER、tools script、PM RCA文書、委任_02ログ+check.json、委任_04ログ+check.json。index.lockは待って再試行)。メッセージ: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: 予算+¥100を逐語記録、PM運営Failure RCAと再発防止A〜FをPM_GOVERNANCEへ反映(24節/11-5/5節/Closeout 27〜30)、Opus指摘台帳新設、rep30をVALIDATED(条件付き)へ遡及再表記(委任_04、¥0)`

## 事前指定Read一覧

`docs/pm/pm_rca_open233_stage1_closeout_01.md` §4〜§5(全文可)。`PM_GOVERNANCE.md`: Grep `^## |^### |Closeout Mandatory|項目2[0-9]|委任文テンプレート|15\.`→該当節範囲のみ。Opusレビュー#10〜#15: Grep `Safety hole|BLOCKER|MAJOR`節のみ。`check_delegation_prompt.py`全文(短い)。CURRENT_SPEC/OPEN_ITEMS/REPORT: Grep限定。

## 事前指定Grep一覧+追記位置・更新位置の手順

上記3〜7のGrepと位置のとおり。DECISION_LOG末尾(スクリプト)。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_04.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_04.md_check.json
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py --dry-run ... → 本実行。
Git: `git status --porcelain`→明示add→commit→`git push origin main`→`git log --oneline -1`。

## SSOT追記文

上記作業2〜7のとおり(DECISION_LOG/PM_GOVERNANCE/OPEN_ITEMS/REPORT_LEDGER等)。

## Git

作業8のとおり。

## 報告(短く)

(1)結論5行以内、(2)PM_GOVERNANCE追加節の見出し一覧と行範囲、Opus台帳のbackfill件数、再表記箇所、(3)check script変更点と3件の動作確認結果、(4)T-0・commit・push・raw URL(PM_GOVERNANCE/OPUS_FINDINGS_LEDGER/DECISION_LOG)、一覧外Read、(5)Fableへの論点。
