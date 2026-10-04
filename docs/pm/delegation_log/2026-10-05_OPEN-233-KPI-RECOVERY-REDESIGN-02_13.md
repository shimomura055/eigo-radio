# 管理ID: OPEN-233-KPI-RECOVERY-REDESIGN-02(委任_13)
親: OPEN-233-SELF-RECOVERY-TRIAL-01。並行タスクなし。

## 性質/到達上限Status/禁止事項
- 性質: Status記録のみ(¥0、実装なし、有料APIなし)。委任_12の結果(rep30: Human Review 0・重大見逃し0・平均追加+¥0.13達成、worst追加+¥3.135[safety_A4 s1]でCap+¥3を¥0.135超過→KPI 3/4達成)を受け、FableがUSER_DECISION_REQUIREDでSTOPすると判断。その記録を行う。
- 到達Status: USER_DECISION_REQUIRED。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへ進まない。
- Fable判断: 「rep30でPrimary・Safety・Cost平均は達成。Cap(worst)は38 runのうちsafety_A4 s1の1 runが+¥3.135で¥0.135超過。rep30aでは同instance¥2.57(Cap内)で、超過は収束特性の変動幅による。残手段は(a)F1 品質regen条件の調整(ユーザー判断)、(b)同fact兄弟箇所のRewrite側拡張(QCD3と衝突)。n固定のため再実行しない。KPI緩和は提案しない。」
- 禁止: コード変更なし。CURRENT_SPEC/DECISION_LOG/PM_GOVERNANCE編集なし。git add -A/stash/amend禁止。ACTIVE_TASK/RESULT_PACKETはaddしない。

## 作業
1. ACTIVE_TASK.md Statusを USER_DECISION_REQUIRED へ。ユーザー判断事項: (1)Cap未達の扱い (2)B'の§0-4解釈 (3)非BLOCKING再利用スイッチ (4)issue_focus_absent_recheck_only本文全体判定 (5)blocking_structural_after_ladder未検証経路是正 (6)10本次TrialのGO
2. OPEN_ITEMS.md KPI-RECOVERY-02行Status更新、REPORT_LEDGER.md 1行。
3. commit/push(明示add)。
(固定ブロックE-1/D-1/G-1/F-1/T-0/T-2/T-3は委任元記載の通り。)
