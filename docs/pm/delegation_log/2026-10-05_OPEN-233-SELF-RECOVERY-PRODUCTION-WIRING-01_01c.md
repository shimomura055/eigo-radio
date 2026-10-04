## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_01c = Closeout SSOT記録の残り)。並行タスク: 委任_02(`docs/pm/production_wiring_gap_open233_01.md`のみ作成、git操作なし)。本委任はそのファイルに触れない。

## 性質/到達上限Status/禁止事項

- 性質: ¥0・SSOT記録のみ(コード変更なし)。委任_01bでDECISION_LOGへユーザー決定原文(逐語)とFable評価転記は完了(commit 28969cc8)。残り: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`docs/pm/PM_GOVERNANCE.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §63、`docs/pm/REPORT_LEDGER.md`、`docs/pm/ACTIVE_TASK.md`(addしない)、委任_13ログ末尾注記。
- 到達上限Status: 対象仕様=`APPROVED_FOR_PRODUCTION`(ユーザー決定済み)。**`PRODUCTION_WIRED`にはしない**(完了条件1〜12達成後のみ)。新管理IDのStatus=`IN_PROGRESS`。
- **出力停止回避の方針**: 各ファイルへの追記は1回あたり短く(1ファイルずつEdit)、長い列挙は箇条書きで簡潔に。長文の逐語引用はせず、DECISION_LOGのエントリ(2026-10-05 ユーザー決定 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01)への参照で済ませる。
- **T-0の厳守**: 委任_01/_01bの委任ログは「要点保存版」で保存されT-0違反が続いている。本委任では、**この委任文全文を要約せずそのまま保存**する。長さのためにWriteが1回で収まらない場合は、Write後にEditで末尾へ続きを追記する形で複数回に分けてよい。要点版は禁止。
- 禁止事項: コード変更禁止。`DECISION_LOG.md`は編集しない(委任_01bで完了)。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。CLAUDE.mdは編集しない。
- 費用上限: ¥0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01c.md`。

## ユーザー指示(原文、該当部分。全文はDECISION_LOG末尾エントリ)

````
Cost KPI更新
従来の単発 +¥3/記事Capは撤回する。
今後のCost管理は、
- 平均追加費用を主要KPIとして継続監視
- 1記事/runで¥3を超えた場合は必ず報告・記録
- ¥3超だけを理由に自動STOP・KPI FAILとはしない
とする。
既存の平均費用KPIは変更しない。
F1「品質regen条件を緩めて費用削減」は、最終rep30では不採用なのでProductionへ入れないこと。
…
Opus / Fable改善ループの正式運用ルール
今回有効だった以下を今後の通常ルールとして記録する。
Opusレビュー
→ Fable評価
→ 実装
→ Fable再確認
→ Trial
ループ上限
最大3回までは自律的に実施してよい。
4回目以降が必要な場合は、その都度STOPし、
- 3回までの結果
- 現在残っている問題
- 次回Trialで何を変えるのか
- なぜ改善が期待できるのか
- 費用
をユーザーへ報告する。
ユーザーから明示的に4回目実施の指示を受けた場合でも、5回目以降も同じルールを継続する。
つまり、4回目以降は毎回ユーザーGateを通す。
ユーザーが別途ルール変更を明示した場合のみ例外とする。
このルールをPM_GOVERNANCE等の適切な正式運用SSOTへ反映すること。
````

## 作業(1ファイルずつ、短いEdit)

1. **CURRENT_SPEC.md** OPEN-233節(Grep `OPEN-233`→該当節の末尾に小節追加「2026-10-05 Trial Closeout・Production正式採用(`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)」):
   - Trial結果: rep30 VALIDATED(29ケース・38 run・Human Review 0・重大見逃し0・平均¥0.573/run・rep24比+¥0.13/run・不要Rewrite 3/14、worst +¥3.135[1/38 run、報告対象])。
   - 採用対象(`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`は完了条件1〜12達成後のみ): ユーザー列挙22項目(箇条書き、DECISION_LOG参照)+rep30有効スイッチ名の列挙(短く): HANDOFF_MODE=violation_span / VS_MATCH_EXT / VS_EXPLAIN_SPLIT(+Q, U-2(1)) / JA_MODE=english_only / V7b / FLOOR_VERIFY_MODE=time_only / VS_SENTENCE_RESTORE(L6、focus_absentは本文全体判定) / CAUSAL_FLOOR known6+issue_actor / STAGE2_SECOND_OPINION(S1) / RECHECK_MERGE_UNRESOLVED(N1′) / STRUCTURAL_ELEMENT_REWRITE / STRUCTURAL_PAIRS_TO_RECHECK / ACTOR_GUARD_MODE=ag1_strict+related_fact欠落時Ledger全体fallback+同義語表 / 件数一致index別集約 / prior_issues現行本文 / STAGE4_ALLOWLIST / LADDER_LOCATION_CARRY(B′) / REWRITE_REVERT_GUARD(A2) / SPAN_FALLBACK_CHAIN(D+carry list) / JUDGE_ONLY_CYCLE_AFTER_CAP(G) / LAST_RESORT_DELETE(T) / MATERIALITY_BLOCKING_PIN / STAGE2_VERDICT_REUSE_NONBLOCKING / STAGE2_SIBLING_LOCATIONS_CYCLE1 / degenerate是正。
   - 配線しない(REJECTED/OFF): F1 / 確認役(STAGE2_DOWNGRADE_VERIFY) / N3′(RECHECK_BEFORE_AFTER_PAIRS) / G_L(TIER0_G_L_ENABLED) / NORMAL群2-of-2(STAGE2_NORMAL_TWO_OF_TWO) / CAUSAL_FLOOR_VOCAB=inventory / A1 / C / E1 / E2 / F2。
   - Cost KPI(2026-10-05更新): 平均追加費用を主要KPIとして継続監視(基準不変)、1記事/runで¥3超は必ず報告・記録、¥3超のみで自動STOP/KPI FAILとしない、単発+¥3 Capは撤回。
   - 残る正当なHuman Review経路(許可リスト4種): blocking_confirmed_unlocatable_after_cap / blocking_structural_after_ladder / post_T_new_blocking / api_failure。
   - 既存`OPEN-233-A1-PROD`束は本決定の採用対象に合流。追加N増しTrialなし、Production運用中の問題は個別改善。
2. **OPEN_ITEMS.md**: (a)`OPEN-233-KPI-RECOVERY-REDESIGN-02`行Status→「VALIDATED(rep30)。2026-10-05ユーザー決定でUSER_DECISION解消(Cap撤回・B′承認・再利用承認)。Production配線は`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`へ」。(b)`OPEN-233-A1-PROD`行末尾に「2026-10-05: 本束は`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`の採用対象へ合流(rep30有効構成全体がAPPROVED_FOR_PRODUCTION)」。(c)新行`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`: Status IN_PROGRESS、完了条件1〜12のチェック欄(全て未)、進捗「委任_01b/01c: Closeout SSOT記録。委任_02: Gap棚卸し(並行)。次: 配線設計→Opus独立レビュー(条件A/C)→ユーザーへ変更範囲報告→実装」。(d)OPEN-233本体行Statusを「Trial VALIDATED・APPROVED_FOR_PRODUCTION・配線中(PRODUCTION-WIRING-01)」へ。
3. **PM_GOVERNANCE.md** 11節(Grep `^## 11|11-3`→11節末尾、11-3の後に小節`11-4`または既存番号体系に合わせて追加)「Opus/Fable改善ループの正式運用ルール(2026-10-05ユーザー決定、`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)」: 手順(Opusレビュー→Fable評価→実装→Fable再確認→Trial)、自律実施は最大3回、4回目以降が必要な場合はその都度STOPし(3回までの結果/残問題/次回Trialで何を変えるか/改善が期待できる理由/費用)を報告、ユーザーが4回目を明示指示しても5回目以降も同ルール(4回目以降は毎回ユーザーGate)、例外はユーザー明示のみ。既存の「Sonnet委任上限(初回+3)」「Opus難問診断1回」「Opus独立技術レビューGate(11-3)」とは別カウントであることを1行で明記。
4. **REPORT §63「Trial Closeout(VALIDATED)・Production正式採用」**(Grep `^## §62`→直後): 最終数値、Human Review推移(iter7 7→rep24 2→rep27 3→rep28 3→rep29 3→rep30 0)、Safety-critical 6件全て検出・解消、費用(Phase累計¥720.20、rep29 ¥24.67・rep30a ¥3.02・rep30 ¥21.79)、使用モデル(`gpt-6-luna`のみ、Sol未使用)、Opus#8〜#14の指摘と対応(各1行)、REJECTED/VALIDATED/USER_DECISION分類(DECISION_LOG参照)、未解決(配線時に扱う: `blocking_structural_after_ladder`未検証経路、`issue_focus_absent_recheck_only`、「and」版ACCEPTABLE判断ユーザー未確認)、未処理USER_DECISION(なし)、APPROVEDだが未配線(全対象)、未報告Trial(なし)、Dangling Reference(配線時に全件確認)。
5. `docs/pm/REPORT_LEDGER.md`1行。`docs/pm/ACTIVE_TASK.md`を新管理IDの固定ヘッダで書き直し(Status IN_PROGRESS、Phase、完了条件1〜12、次工程)(addしない)。委任_13ログ末尾に1行注記「T-0違反: 要約版保存(Fable運用メモ)」。
6. commit/push(明示add: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`docs/pm/PM_GOVERNANCE.md`、REPORT、`docs/pm/REPORT_LEDGER.md`、委任_13ログ、委任_01cログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: CURRENT_SPEC(採用対象・配線しない項目・Cost KPI更新)・OPEN_ITEMS・PM_GOVERNANCE 11節(改善ループ3回Cap)・REPORT §63 Closeoutを更新(委任_01c、¥0)`

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grep `OPEN-233` → 該当節の見出しと末尾のみ範囲Read(全文Read禁止)。
- `OPEN_ITEMS.md`: Grep `OPEN-233`(本体行・`KPI-RECOVERY-REDESIGN-02`・`OPEN-233-A1-PROD`、行番号は委任_01報告で662/726/727付近)。全文Read禁止。
- `docs/pm/PM_GOVERNANCE.md`: Grep `^## 11|^### 11-` → 11節の見出し構造と末尾のみ。
- REPORT: Grep `^## §6[0-3]` → §62の範囲。
- `docs/pm/REPORT_LEDGER.md`末尾5行、`docs/pm/ACTIVE_TASK.md`固定ヘッダ。

## 事前指定Grep一覧+追記位置・更新位置の手順

上記作業1〜5の各Grepと追記位置のとおり。

## 実行コマンド全文

T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01c.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01c.md_check.json
Git: `git status --porcelain` → 明示`git add` → commit → `git push origin main` → `git log --oneline -1`。

## 報告(RESULT_PACKET項目、短く)

(1)結論5行以内、(2)ファイル別の更新箇所(行範囲)とStatus表記、(3)PM_GOVERNANCE小節の全文(短い)、(4)T-0(PASS/FAIL・全文保存したか)・commit・push・raw URL(CURRENT_SPEC/OPEN_ITEMS/PM_GOVERNANCE/REPORT)、一覧外Read。(5)Fableへの論点。

(注: 保存時、システム側の補足としてコミットメッセージ末尾に `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` を付与する指示あり。)
