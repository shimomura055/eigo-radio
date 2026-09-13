管理ID: FAMILY-A-DISCOVERY-FOCUS-PART-A-STANDALONE-DESIGN-TRIAL-01
Status: 完了(¥0設計+最小Trial実施、実費¥33.94/見積上限150円、
Discovery残額253.53円以内)。Production配線・APPROVED_FOR_PRODUCTIONは
行っていない。

作業1(設計比較): 現行Production `run_one_pattern`はPoint Role Planning
(topic+ledgerのみ)→Writer(Main Story+Point全体を1回で生成)の順であり、
ユーザー基本設計「Point Role PlanningはMain Story成立後」と順序が矛盾する
ことを確認(News/Trend/Discovery共通)。S1(現行順序+Focusのみ)は既存
Trial結果で判断済み(再実行なし)。S2(Stage1 Main Story固定→Stage2 Role
Planning[Main Story本文を実際に読ませる]→Stage3 Point生成)を推奨案とした。

作業2(Trial): Trial専用driver
`er011_discovery_focus_part_a_standalone_trial_01_run.py`でS2をA2/B1各1本
実施。Main StoryはStage 1として新規生成せず既存Trial(discovery_focus_
module_revalidation_01のfocus腕)を再利用(無駄なコストを払わない)。結果:
A2=OK(fact PASS/LEDGER_COMPLIANT)、B1=OK(fact REVIEW_REQUIRED[non-
blocking]/LEDGER_COMPLIANT)。角度収束(案2で観察されたA2/B1同一役割)は
再発せず。Point Role Planning入力に実際のMain Story本文が渡った証拠を
`stage2_role_planning.json`で確認。

限界: Point Overlap/Value QA retry・Local Rewrite・Directional Fact
Precheckは本Trialで未実装(単発実行、fail-closed)。Production化する場合、
S2のretry単位(Stage1から作り直すか固定のままStage2/3のみやり直すか)は
USER_DECISION_REQUIRED。

詳細: `FAMILY-A-DISCOVERY-FOCUS-PART-A-STANDALONE-DESIGN-TRIAL-01_REPORT.md`
比較artifact: `er011_output/discovery_focus_part_a_standalone_trial_01/
comparison.md` + `index.html`

次アクション: Fable/ユーザーへGate 1判定材料を提示。S2をProduction化するか
どうか、7節のretry単位を先にユーザー判断してもらう必要あり。
