# 委任_01A: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 1 棚卸A・C・E(read-only、JPY0)
2026-10-14。並行して委任_01B(読み込み量・予算調査)が別agentで走る。領域分離厳守。

## 0. ユーザー指示の要旨(逐語保存)
目的: 「問題が起きるたびにユーザーへ判断を求める」運営から「承認済みの目的・仕様をAIが自律的に完遂する」運営へ7日間で移行する。Research `PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01`の案D(短いCharter+Worker自律+最小限の機械的安全装置)をベースにするが、**原案の6〜8週間・18,000字常駐・新規管理機構の一括導入は採用しない(軽量版D)**。具体設計・Production適用は未承認。今回はDay 1のread-only棚卸。
正式合意済み基本方針: **Q>D>C≫開発コスト**(Q=ユーザー承認の品質ライン厳守、100%追求ではない/D=品質ラインを守りつつProduction完成時間を最小化/C=量産コスト上限**70円/記事セット**、恒久的な1〜2円増も軽視しない/開発コスト=有料API実行費の**日次共有予算1,000円**(日本時間)、増額はユーザー判断)。開発コストと量産コストを混同しない。
7つの行動原則(棚卸の評価基準。まだ定義ファイルは変更しない): 1.必要十分な品質で止める 2.品質を守りながら最速で完成 3.常に量産単価を見る(新Prompt/Validator/API/retry/HR提案時は70円への影響評価必須) 4.不具合は自律的に解決(原因究明→対策→効果・副作用検証→承認済み範囲の実装) 5.解決手段に固執せず必要なら問題の捉え方から見直す(無益な改善ループにも安易な断念にも陥らない) 6.Humanには重要Decisionだけ(品質ライン変更/新仕様正式採用/重大QDCトレードオフ/予算超過) 7.Project全体を見て判断(個別エラー消しのために量産費・速度・他Family品質を犠牲にしない)。
マイルストーン: M1 Day1棚卸→M2 Day2最小設計確定(ユーザー承認Gate)→M3 Day3-4最小実装→M4 Day5-6実案件2〜3件で新旧比較→M5 Day7採用判断。Day 1は既存設定・Agent・Production・SSOTをread-only。調査報告の新規ファイル保存とGit反映は可。**既存Researchを再実施しない**。既存成果(FINAL_REPORT_01/INTERNAL_DIAGNOSIS_01/RECOMMENDED_PROJECT_DEFINITION_01/OPERATING_MODEL_COMPARISON_01/ROLLOUT_AND_VALIDATION_PLAN_01、25原因・55変更候補・Opus所見OF-209〜224)を再利用し、実態確認不足部分のみ追加調査。受入条件の要: **Day 3〜4の実装対象を最小化**。確認できない事項は推測で埋めず「未確認」。巨大な新台帳・新設計書を作らない。STOP条件: 既存ユーザー承認事項と新方針の重大矛盾/Production実行・有料Trial・設定変更が必要/新運営仕様の採用判断が必要/安全機構・承認状態の不整合。

## 1. 担当(要約)
A. 現行Project定義の棚卸(CLAUDE.md/PM_BRIEF/PM_GOVERNANCE節単位/.claude/agents 4件/委任テンプレ固定ブロック)。各規則を7原則・Q>D>C≫開発費に照らし 維持/修正/統合/廃止候補に分類、RPD §12 #1〜#55対応ID付与、実使用 vs 存在のみ(grep根拠)、承認済み重要ルールは廃止候補にしない(DECISION_LOG/UDR_REGISTER ID添付)。答える: (i)原則1・2・6と矛盾する上位10件 (ii)「上限初回+3=UDR」「UDR文化踏襲」「Fableまたはユーザーへ」「不整合1件でSTOP」型の所在一覧 (iii)原則3(70円)相当の既存規則の有無。
C. 既存自動チェック機構の棚卸(提案5機構 state_gate/stop_check/budget_gate/docs_lint/Git hook+強制Regression vs 既存実装。STOPセンチネル/RUN_LOCK/RESTART_STORM/26-5/runnerごとのSTOP実装/Validator/secret_scan/check_delegation_prompt/.git/hooks/settings hooks/CI/run_project_regression/費用記録所在)。各提案: 既存機能/不足/既存拡張で足りるか/新設必須か/運用負荷。機構数を増やさず最小コスト。★★★★報告マーカー違反を既存軽量手段で防げるか。
E. 未完了作業・PM Gate引継ぎ(UDR_REGISTER #45〜#59中心、OPEN_ITEMS Status grep、ACTIVE_TASK*/RESULT_PACKET*(FZSL/FZPD/M1F1/M1OOV/XZC/PMAR)、CURRENT_SPEC未配線表記)。Coffee/ASR M1/F1/Family Z Preview(UDR #51)/Family Z記事再生成STOP等を必ず含める。**Day 1でこれらを進めない。**

## 2. 成果物
docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/ に DAY1_A_RULES_INVENTORY_01.md(A、12,000字以内)/DAY1_C_MECHANISMS_01.md(C、6,000字以内)/DAY1_E_HANDOVER_01.md(E、6,000字以内)。表中心、事実/推測/未確認を明示。

## 3. 固定ブロック(要約)
E-1 Windows/.venv/PYTHONUTF8=1、scratchpad rollout_a。D-1 read-only(既存規則・設定・Agent定義・コード・SSOT編集禁止、本番生成/有料API禁止、.env不使用、委任_01B出力に触れない)。G-1 **commit/pushしない**(委任_02で一括)。F-1 JPY0。T-0 本ファイル保存。T-2 ACTIVE_TASK_ROLL_A.md(ACTIVE_TASK.md本体は触らない)。T-3 RESULT_PACKET_ROLL_A.md(30行以内)、hand-back: (1)A分類件数と差分表55との差異 (2)矛盾上位10件 (3)5機構結論1行ずつ (4)引継ぎ件数とユーザー判断待ち一覧 (5)STOP条件該当有無 (6)保存先。STOP確認: *STOP_NOTICE*(2026-10-12 Melosは旧記録=非適用)・STOP_ALL確認を記録。
