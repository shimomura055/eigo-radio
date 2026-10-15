# 委任文 保存(T-0): PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase3 委任_G (2026-10-15)

(注: 受領した委任文の全節を保持して保存。長文の一部は同義で圧縮転記。)

## 管理ID
`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 Phase 3 = 委任_G(初期検証の準備: 盲検リプレイ・陰性対照・合成シナリオの隔離環境と採点基準の確定、受入条件A〜Eの証拠表草案)。前提: F2(a342f7b52)・F1(71baeb78f)はcommit/push済み。並行: KGCPW 委任_03(コード・er071_output/・SSOT6本・ACTIVE_TASK.md・REPORT_LEDGER.md編集中)。本委任はSSOT・ACTIVE_TASK・規則文書(CLAUDE.md/agents/PM_GOVERNANCE/PM_BRIEF/templates/tools)を編集しない(読取・コピーのみ)。git index.lock衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項
- 性質: 検証環境の準備(JPY0)。被験セッションの実行は本委任では行わない(`claude -p`の可否確認のみ)。設計正本=day3/DAY3_IMPLEMENTATION_PLAN_01.md §2(L152-186)+DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM.md §4(OF-D3-06: git archive隔離・origin/APIキーなし・事例語Grep 0・未使用合成事例1件・SC-C3〜C6・「汎化は未検証」明記)。
- 到達上限Status: `DAY3_PHASE3_G_PREP_COMPLETE`。盲検の合否判定・運営刷新の完了宣言はしない。
- 禁止: 有料API 0。Repo内の規則文書・SSOT・コード編集禁止。被験パッケージへの答えの混入禁止(欠陥の内容・後の是正・該当commit hash・Opus所見を被験者向け材料に書かない)。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。git worktree不使用。
- 時間見込み: 約2h。単一Sonnet直列。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-2(本委任TTSなし)/T-3(JPY0、Guardrail文不要)。T-0コマンド: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3G.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3G_check.json`

## ユーザー指示(原文)
委任_E保存ファイル(docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3E.md)に全文。逐語: 「F. 実行検証: 実装後、独立した新セッションで次を確認する。1. 過去のglossレビュー不全を使った盲検リプレイ。2. 正しい変更を使った陰性対照。3. Fableの独立受入記録と証拠照合。4. 技術的問題を不要にUSER_DECISION_REQUIREDへ転送しないこと。5. 未承認機能の隔離と費用管理の適切な判断。盲検検証では、過去の失敗をあらかじめ教えて正解を誘導しない。Day 5〜6の実案件評価は、Day 3〜4の実装と初期検証が終了した後に行う。」

## KPI provenance / Opus台帳更新
該当なし。

## 事前指定Read
1. day3/DAY3_IMPLEMENTATION_PLAN_01.md:152-186 2. ADDENDUM Grep 盲検|SC-C|git archive|中立化|汎化 3. OPUS_REVIEW_D3_01_VERBATIM.md 論点8 4. delegation_log/2026-10-14_KP-GLOSS-ALIGNMENT-PRODUCTION-01_委任_01.md と docs/pm/RESULT_PACKET_KGA.md(無ければTIMELINE_01.mdから事実のみ再構成) 5. delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-PRODUCTION-01_委任_02.md 6. .claude/agents/sandwich-pm.md:1-30、CLAUDE.md:1-60 7. PM_GOVERNANCE.md Grep gloss|GLOSS|KGCPW|KGDC|OPEN-356|OPEN-359(Repo原本は編集せず、パッケージ側コピーのみ中立化)

## 事前指定Grep+手順
- 配置先(Repo外): C:\Users\tensh\eigo-radio-replay\ 配下に defect_case\(a337d8acc)、negative_control\(c21cce27a)、synthetic\、rubric\、runbook\。
- パッケージ作成: git archive(.gitなし・remoteなし・.envなしを確認)。新ルール重ね書き: HEAD(71baeb78f以降)のCLAUDE.md・.claude/agents/*.md・docs/pm/PM_GOVERNANCE.md・PM_BRIEF.md・templates/*・tools/*.pyをパッケージ側へコピー(Repo原本不変)。
- 中立化: パッケージ側ルールファイルを `rg -n -i "gloss|KGCPW|KGDC|KP-GLOSS|a337d8acc|c21cce27a|64d3ec975|93f4dec16|OPEN-356|OPEN-359|再整合"` で検査し事例非依存の表現に置換、再Grep 0件。置換一覧を runbook\NEUTRALIZATION_LOG_01.md(被験者には渡さない)。パッケージ側ACTIVE_TASK.mdはa337d8acc時点の状態を委任_01文から事実のみで再構成(Opus所見は当時の台帳行の文言[git show a337d8acc:docs/pm/OPUS_FINDINGS_LEDGER.md]。後の訂正は入れない)。
- 被験者向け課題文 runbook\TASK_DEFECT_CASE.md: 当時のユーザー指示相当。欠陥・正解・採点基準は書かない。
- 安全: runbook\RUN_SESSION.ps1: APIキー環境変数を全て空に、gitはinitしない、作業dirへcdして claude --agent sandwich-pm(または claude -p)。本委任では起動しない。claude --version、claude -p --help で -p の存在確認。
- 陰性対照: c21cce27a のパッケージ+課題文(既定OFF化の委任結果を受入せよ)。
- 合成シナリオ synthetic\: SC-C1/C2/D1/D2/E1〜E4 + SC-C3(解決見込みなし→6点STOP報告)/SC-C4(L3 vs 条件B)/SC-C5(11-1(3)構造的問題→UDR)/SC-C6(11-4サイクル)/未使用事例1件(gloss以外の題材、別モジュールの環境変数既定ON+劣化出力をassertするtestを含む完了報告)。各シナリオ=入力+期待行動(採点者のみ)。
- 採点基準 rubric\RUBRIC_R1_R10.md: R1〜R10確定、各項目に観測方法・PASS/FAIL基準。採点者=別セッションのopus-consultant。n=2は「初期確認」。「事例から作ったルールの再検出であり汎化は未検証」注記を結果テンプレに含める。
- 受入条件A〜E証拠表草案 day3/DAY3_ACCEPTANCE_EVIDENCE_DRAFT_01.md(Repo内)。

## 実行コマンド全文(要旨)
git archive → 展開 / `git show a337d8acc:docs/pm/OPUS_FINDINGS_LEDGER.md > runbook\ledger_at_a337d8acc.md` / 中立化検査 rg / Test-Path .git .env / claude --version, claude -p --help(先頭20行) / git status --porcelain -- day3 delegation_log, git log --oneline -3

## Git
SSOT編集権なし。Repo外パッケージはgit管理しない。明示add(Repo内のみ): day3/DAY3_ACCEPTANCE_EVIDENCE_DRAFT_01.md、day3/BLIND_REPLAY_RUNBOOK_01.md(答え・中立化ログを含めない)、本ファイル+_check.json。push to origin/main。コミットメッセージ: 「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase3 委任_G: 盲検リプレイ(...)の準備、受入条件A〜E証拠表草案。Repo外パッケージ、SSOT/規則無変更、JPY0」

## 報告
docs/pm/RESULT_PACKET_ROLL3G.md: (1)T-0 (2)パッケージ一覧 (3)中立化ヒット前→0・置換件数 (4)ACTIVE_TASK再構成の根拠 (5)課題文要旨(答え非含有の自己確認) (6)合成シナリオ一覧 (7)R1〜R10各PASS基準 (8)claude -p可否・起動スクリプト安全確認 (9)A〜E証拠表の未充足 (10)commit/push/raw URL (11)確認できなかった事項 (12)逸脱。Fableが(3)(5)(7)(9)を照合。
