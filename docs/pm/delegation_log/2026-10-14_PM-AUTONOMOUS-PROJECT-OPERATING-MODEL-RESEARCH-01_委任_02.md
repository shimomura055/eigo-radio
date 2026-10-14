# PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 委任_02(要点保存、2026-10-14)

保存方針: ユーザー指示の要旨(§0)は逐語、その他は要約(要点保存。固定ブロックE-1/D-1/G-1/F-1/T-0〜T-3は要約)。

## 0. 目的(ユーザー指示の要旨・逐語)
テーマ:「人間がQCDとプロジェクト方針に関わる重要Decisionへ集中し、それ以外の開発・検証・不具合対応をAIが自律的に完遂するためのProject定義・権限・運営方式」。ユーザーが目的・期待仕様を提示したら、AI側が 目的理解→既存仕様照合→実行計画→実装・検証→問題検知→原因究明→対策立案→効果と副作用のTrial→承認済み範囲の是正・実装→Production確認→完了報告 を自律で進める体制。途中で問題が見つかっても直ちにHumanへ戻さない。新仕様が必要なら採用判断に必要なTrialまで行い、実例・効果・ネガ・QCD・推奨案を揃えてから提示する。無益な試行の反復は自律性ではない。**今回はResearch・分析・改善提案のみ。既存Project設定・CLAUDE.md・PM_GOVERNANCE・Agent定義・Productionコード・Prompt・SSOTの変更は禁止。実ファイル(規則)は変更せず設計案まで。Researchが完了した時点でSTOPし、新運営モデルを独自導入しない。** `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`の区別は維持。ユーザーの正式採用判断をAIが代行しない。大企業向けの複雑モデルを無批判に採用しない。個人開発・少人数運営での実現性を重視。

## 1-4 (要約)
- 入力: docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/ の EXTERNAL_RESEARCH_01.md / INTERNAL_DIAGNOSIS_01.md / sources_01.json ほか。
- 成果物3 OPERATING_MODEL_COMPARISON_01.md(3案以上、8比較項目、事例番号とR-ID明記) / 成果物4 RECOMMENDED_PROJECT_DEFINITION_01.md(Charter、PM/Worker権限、Human Decision Policy 8区分、Problem-Solving Loop、Trial/Production Gate状態ファイル、Cost Budget、DoD、Escalation、Agent分担、KPI、既存定義との差分表 維持/統合/削除/改訂/新設、文書vs仕組み、常駐文書総量目標) / 成果物5 ROLLOUT_AND_VALIDATION_PLAN_01.md(8指標、Phase0-3、撤退条件、候補案件) / 成果物6 FINAL_REPORT_01.md(冒頭8節 2,500〜4,000字目安)。
- Fable設計指針(照合用・反論可): 常駐文書最小化/機械強制+有効性監査/完了状態の構造化/不可逆性・方針変更・予算の3軸/run単位ハード上限。中核はR1/R3/R4/R20。R5は受入時独立検証手段を設計案として。Sonnet上限は同一failure mode 2回修正後再発→context破棄・再計画(+Opus条件B)型へ。UDR出自フィールド必須。診断書§5-3の維持事項は全て差分表に。
- 固定ブロック: E-1 Windows/.venv/PYTHONUTF8=1。D-1 SSOT・agents・Production等の編集禁止、有料API不使用、.env非source。G-1 commit対象はdocs/research/PM-AUTONOMOUS-.../配下全md/jsonと本管理IDのdelegation_log(01A/01B/_check.json/本委任_02)のみ、ファイル名明示add、secret_scan --staged必須、Managed-ID trailer、ACTIVE_TASK*/RESULT_PACKET*はgitignored。git add -A/-f/amend/rebase/force/stash/clean/reset --hard禁止。F-1 JPY0。T-2 ACTIVE_TASK_PMAR.md。T-3 RESULT_PACKET_PMAR.md(30行以内)+hand-back項目(1)比較結論と推奨案(2)差分表件数と常駐文書総量目標(3)真にユーザー判断が必要な事項(4)Fable指針への反論(5)commit hash・raw URL(6)JPY0確認。
- check_delegation_prompt.py は存在しないためスキップ。
