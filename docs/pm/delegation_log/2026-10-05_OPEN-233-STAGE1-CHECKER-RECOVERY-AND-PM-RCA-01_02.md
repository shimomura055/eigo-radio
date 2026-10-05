# 委任_02 委任文(全文保存、2026-10-05)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_02、PM運営Failure RCA軸)。**並行タスクあり**: 委任_01(ユーザー指示の逐語記録・OPEN_ITEMS新行・Stage 1技術RCA文書・DECISION_LOG・REPORT_LEDGER・ACTIVE_TASKを編集、git操作あり)。**本委任は新規文書`docs/pm/pm_rca_open233_stage1_closeout_01.md`と自分の委任ログのみ作成し、他ファイルを編集しない。git commit/pushは行わない**(次委任でFableがaddさせる)。報告はhandback本文で行う(RESULT_PACKETに書かない)。

## 性質/禁止事項

- 性質: ¥0・プロセスRCA(責任追及ではなく同種事故の再発防止)。ユーザー§10の8問に、記録(DECISION_LOG・OPEN_ITEMS・ACTIVE_TASK履歴・REPORT・Opusレビュー・委任ログ・commit履歴)のEvidence付きで答え、§11の再発防止A〜Eを正式PMルール(`docs/pm/PM_GOVERNANCE.md`)への反映案として起案する(**本委任ではPM_GOVERNANCEを編集しない**。案文のみ)。
- 禁止: コード変更禁止。有料API禁止。上記以外のファイル編集禁止。`git add -A`/`stash`/`amend`/commit禁止。1回の書き込みは2,500文字以下(節ごとにEditで追記)。長文の逐語引用は避け、出典パス・行番号で示す(必要な引用は各40字以内)。
- T-0: 委任ログ`docs/pm/delegation_log/2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_02.md`に全文保存(分割)、check実行・結果をhandbackに1行。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分§10〜§11)

````
10. PM運営FailureのRCA
Checker技術改善と並行して、今回のPM Failureを別軸でRCAする。
最低限、以下を答えること。
1. Opus #10が「Stage 1 recallが支配的リスク」と警告していたのに、なぜrep30 Closeoutでblocking issueとして扱われなかったか。
2. Opusは「条件付きSafety値」と「代替なしE2E値」を分けるよう指摘していたが、実際にどう処理されたか。
3. Fable自身もその指摘を採用していたのに、なぜ最終KPI報告へ反映されなかったか。
4. Stage 1 recallはOPEN_ITEMS / ACTIVE TASK / KPI Gateのどこで管理され、どこで脱落したか。
5. 誰がnon-blocking / deferredと判断したのか。明示判断が無ければ、なぜ自然消滅したのか。
6. rep30の「重大Fact見逃し0」を算出するとき、なぜfrozen / V0差替えを含む条件付き評価だと検出できなかったか。
7. Trial closeoutで、Production初回pathを本当に通しているかをなぜ確認できなかったか。
8. Opusの警告を「レビュー済み」で終わらせず、Closeoutまで追跡する仕組みがなぜ働かなかったか。
責任追及ではなく、同種事故を防ぐためのプロセスRCAとする。
11. 再発防止
RCA後、最低限以下を正式PMルールへ反映する案を作り、Fableが評価すること。
A. KPI provenance
各KPIについて必ず、
- fresh
- frozen
- reuse
- manual substitution
- synthetic
- Production formal path
のどれで測ったかを記録する。
B. 条件付きKPIとE2E KPIの分離
固定入力や差替えが1件でも含まれる場合、
E2E Safety KPI
と呼ばない。
C. Opus指摘トレーサビリティ
重要なOpus警告は、
Opus指摘 → Fable採否 → 実装/Trial反映 → 検証Evidence → Closeout確認
まで追跡する。
未解決のBLOCKER / MAJOR / Safety警告がある状態でCloseout禁止。
D. Closeout自己確認
Trial終了時に必ず、
このKPIはfresh Production初回pathを含むE2E値か？

を明示的にYes/No判定する。
NoならE2E達成扱い禁止。
E. Open Item消失防止
Stage 1 recallのようなSafety未解決項目を、ユーザー合意なしにnon-blocking / deferred化しない。
````

## 作業: `docs/pm/pm_rca_open233_stage1_closeout_01.md`

§1 事実の時系列(Evidence付き): Opus#10(`docs/pm/opus_l2_review_open233_self_recovery_10.md`)のStage 1 recall警告と「条件付きSafety値/代替なしE2E値の分離」指摘の該当箇所(行番号)→Fableの採否記録(設計書`docs/pm/design_open233_stage2_safety_downgrade_01.md` §7〜§8、`design_open233_kpi_recovery_02.md`、DECISION_LOG Grep `Opus#10|Stage 1 recall|第二段階|条件付き|E2E|代替なし`)→rep24〜rep30の集計での扱い(runner `substitute_baseline_on_stage1_miss`導入commit・委任ログ、`summary_kpi_01.json`の`stage1_recall_miss_substituted`が報告に出たか: REPORT §42〜§63をGrep `差替え|substitute|frozen|reuse|fresh`)→KPI-RECOVERY-02ユーザー指示で「Stage 1 Checker recallは第二段階」とされた箇所(DECISION_LOG)→rep30 Closeout(委任_12/_13報告、REPORT §62/§63、`open233_closeout_check_2026-10-04.md`)で「重大見逃し0」がどう算出・表記されたか→Production採用決定(2026-10-05)→Gap棚卸し(委任_02/_03)でF1〜F4が判明→CORRECTION-01/02。
§2 §10の8問への回答(各: 事実/Evidence/判断の所在[Fable/Sonnet/Opus/ユーザー]/明示判断の有無)。特に: 問5は委任ログ・DECISION_LOGに「non-blocking」「deferred」「第二段階」「後回し」の明示記録があるか全件Grepし、無ければ「自然消滅」の経路(どの文書の更新で消えたか)を特定。問6は`residual_at_pass`・`stage1_recall_miss_substituted`等の計測が「見逃し0」の算出に組み込まれていたか(集計スクリプト`_rep30_agg_01.py`をGrep)。問7はCloseout Mandatory Check(`PM_GOVERNANCE.md` Grep `Closeout|Mandatory`)の項目に「Production初回path通過」「KPI provenance」があったか。
§3 根本原因(プロセス): 複数の寄与因子を「仕組みの欠落/判断の省略/用語の曖昧さ(VALIDATEDの意味)/報告フォーマットの欠落/委任文テンプレートの欠落」に分類。
§4 再発防止A〜Eの`PM_GOVERNANCE.md`反映案(案文。各案: 追加先の節番号候補[Grep `^## `で既存構造確認]、条文案[簡潔]、適用範囲、委任文テンプレート/RESULT_PACKET/REPORT/Closeout Checkへの追加項目、既存ルール[Gate 1〜7・Closeout Mandatory Check・11-3 Opusレビュー・11-4改善ループ]との整合と重複回避)。加えて、F: 「条件付き評価」で得たVALIDATEDをProduction採用判断の材料にする際の表記ルール案(ユーザーがProduction採用判断をした2026-10-05決定の入力がrep30の条件付き値だった事実を踏まえる)。
§5 Fable評価用チェックリスト(各案の採用/修正/不採用を判断するための論点)。

## 事前指定Read一覧

Opus#10結論部と「Stage 1」言及箇所(Grep)。設計書§7〜§8(Grep `Opus#10|採否`)。DECISION_LOG(Grep限定、全文Read禁止)。REPORT §42〜§63(Grep限定)。`open233_closeout_check_2026-10-04.md`(全文可、短い)。`PM_GOVERNANCE.md`(Grep `^## |Closeout|Mandatory|Gate|provenance`、該当節のみ範囲Read)。委任ログ`docs/pm/delegation_log/2026-10-0{2,3,4}_OPEN-233-*`(Grep `substitute|差替え|frozen|第二段階|recall`)。runner Grep `substitute_baseline_on_stage1_miss`(周辺コメント)。`git log -S substitute_baseline_on_stage1_miss --oneline`。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_02.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_02.md_check.json
Git: なし(commit禁止)。

## 報告(handback、短く)

(1)8問の回答要点(各1〜2行)、(2)根本原因分類、(3)再発防止A〜F案の要点と追加先節、(4)文書パス・T-0結果・一覧外Read・確認/推測、(5)Fableへの論点。

