# 委任文 保存: PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 委任_01B (2026-10-14)
(T-0保存。「0. 目的(ユーザー指示の要旨)」は委任文どおり、他節は見出し付き要約。)

## 管理ID
PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 委任_01B(Repo内部診断。並行して委任_01A=外部Deep Researchが別agentで走る。領域分離)

## 0. 目的(ユーザー指示の要旨)
eigo-radioのAI開発体制を改善するためのResearch。テーマ:「人間がQCDとプロジェクト方針に関わる重要Decisionへ集中し、それ以外の開発・検証・不具合対応をAIが自律的に完遂するためのProject定義・権限・運営方式」。今回はResearch・分析のみ。既存Project設定・CLAUDE.md・PM_GOVERNANCE・Agent定義・Productionコード・Prompt・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)の変更は禁止。read-only調査。

ユーザーが指摘した繰り返し発生している問題:
1. 明らかな不具合でも、都度ユーザーへ仕様確認する
2. 原因を調べず、失敗した結果だけを報告してSTOPする
3. 原因調査が浅く、部分修正を提案する
4. 効果・副作用・Regression検証が不十分なまま、仕様やProduction変更を提案する
5. QCDを十分考慮せず、その場限りの対策を提案する
6. 量産性・運用コストを考えず、Human Reviewを常態化させようとする
7. 担当タスクの局所最適が優先され、Project全体の目的・既存仕様・将来運用との整合を見失う
8. Fable(PM層)が技術報告を整理・転送する役割に偏り、PMとして原因分析・優先順位・問題解決を主導できていない
9. 厳格なSTOP・ユーザー承認Gateが、本来許される調査や改善Trialまで阻害している可能性
10. ユーザーが技術的な進め方を毎回指示し、AI PMを使う便益が小さい

具体例(2026-10-12〜13): KP候補の短すぎるsource_span(OPEN-349、OF-Y1) / 最終英語KPとja_glossの不一致でHuman Review推奨(OPEN-352、UDR #57) / 同じKP INVALIDを再生成で繰り返し(Opus条件B->A') / 音声segment検証済み状態が引き継がれず(UDR #47/#50) / 承認済みN01音声再生成の逐次ユーザー判断要求 / M1 evidence runnerが旧STOP_NOTICE(別管理ID)のglob一致で停止、Coffee側agentは非適用と解釈(agent間不整合)

## 1. 担当範囲(要約)
read-only調査項目1〜9(有効規則/守られていない規則と実例/矛盾競合/自律性制限/形式過剰/強制力なし/Fable-Worker隙間/長大context重複/削除統合候補)。各問題を文書の欠陥・実装の欠陥・Agent運用の欠陥にラベル付けし、機能しなかった理由を事例ごとに特定。Fable自身の判断記録も分析対象。

## 2. 成果物(要約)
docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/INTERNAL_DIAGNOSIS_01.md(§1構造図+定量、§2事例6件トレース表、§3調査項目1〜9、§4根本原因分類と指摘1〜10対応表、§5削除統合/仕組み化/維持の3リスト、[事実]/[推測]区別)。

## 3. 固定ブロック(要約)
E-1 Windows/PowerShell, .venv\Scripts\python.exe, PYTHONUTF8=1, 集計scriptはscratchpad pmar_b。D-1 対象文書編集禁止、本番生成禁止、委任_01Aの出力に触れない、telemetry/evidence/wav/words/.logをadd禁止、有料run/API支出なし、.env禁止。G-1 今回はcommit/pushしない(委任_02でまとめる)、git add -A等禁止、git log/show/diff可。F-1 JPY0。T-0 本ファイル保存+check_delegation_prompt実行(FAILでも非blocking)。T-2 docs/pm/ACTIVE_TASK_PMAR_B.md(ACTIVE_TASK.md本体は触らない)。T-3 docs/pm/RESULT_PACKET_PMAR_B.md(20〜40行)+最終hand-backに(1)定量(2)事例6件の理由1行(3)矛盾上位5(4)削除統合上位5(5)欠陥比率(6)保存先。STOP確認: STOP_NOTICE/STOP_ALL存在確認を記録(2026-10-12 Melos STOP_NOTICEは旧記録=非適用)。
