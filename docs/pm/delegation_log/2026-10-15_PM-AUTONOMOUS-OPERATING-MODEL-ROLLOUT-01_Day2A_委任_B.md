# 委任_B 全文保存 (T-0) PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A

## 管理ID
PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 2 Phase A 委任_B(AGENT_ROLE_DELTA_01 + GATE_MECHANISM_MAP_01 作成。Opus監査結果の反映対応を含む。2026-10-15)。並行タスク: 同Phase Aの委任_A(RULE_CHANGE_MATRIX_01、別agent)が同時実行中。衝突回避: あなたは `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/AGENT_ROLE_DELTA_01.md`、同 `GATE_MECHANISM_MAP_01.md`、`docs/pm/RESULT_PACKET_ROLL2B.md`、本delegation_log(+_check.json)のみ書く。`ACTIVE_TASK_ROLL.md`と`RULE_CHANGE_MATRIX_01.md`は委任_Aのもので触れない。git commit時`.git/index.lock`があれば30秒待ち再試行(最大5回)。

## 性質/到達上限Status/禁止事項
性質: read-only調査+設計文書(規則・設定・Agent定義・SSOT・Production・Prompt・Gate・flag無変更、有料API・Opus呼出なし、費用JPY0)。到達上限Status: ROLE_GATE_DRAFT(Fable受入・Opus条件Aレビュー待ち)。
Opus独立技術レビューGate判定: 条件A該当(運営モデル設計)。Opusレビューは統合後(委任_C成果物)にFableが依頼。本委任では呼ばない。
時間見込み: 90〜120分。並列化: 委任_Aと並列。
禁止: CLAUDE.md/.claude/agents/*/docs/pm/PM_GOVERNANCE.md/docs/pm/PM_BRIEF.md/SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/REPORT_LEDGER.md/OPUS_FINDINGS_LEDGER.md/USER_DECISION_REGISTER_01.md)の編集、.py/Prompt/Gate/flag編集、Day3〜4先行実装、新規Hook/Validator/台帳の作成、git add -A/-f/amend/rebase/force push/stash/clean/reset --hard/checkout -f、委任_A領域への書込。

## 固定ブロック
E-1 同一task内で同一ファイル再読しない / D-1 Grep→該当行範囲Read基本、全文Readは構造変更時のみ / G-1 git出力は最小化 / F-1 transcript退避不要 / T-0 本ファイル保存+check_delegation_prompt.py実行、結果をRESULT_PACKETへ1行 / T-2 TTSなし / T-3 費用JPY0。

## ユーザー指示(原文、本委任関係部分)
Day 2設計案v1: 第1層Charter「Q>D>C≫開発費用」8原則(1必要十分な品質で止める/2品質を守りながら最速で完成/3常に量産単価を見る/4不具合は自律的に解決/5解決手段に固執せず問題の捉え方から見直す/6Humanには重要Decisionだけ/7Project全体を見て判断/8変更時は既存仕様と全体工程との整合性を必ず確認[承認済み既存仕様・上流下流・retry/fallback/regeneration・異常時の最終成果物・不要になる旧ルール])。ユーザー判断=新仕様正式採用・品質ライン変更・重大QDCトレードオフ・予算/Scope変更等に限定。未承認Production仕様の有効化・無言承認・安全STOP迂回は禁止。
第2層: Sonnet=実行担当(原因調査・設計・実装・Trial・Regression・runtime evidence/技術問題を安易にHumanへ転送せずFableへ原因・証拠・解決案/既存仕様整合を確認し未承認仕様採用はしない)。Opus=独立レビュー(変更方法自体の合理性/当初目的・承認済み仕様・旧ルール撤去要否・異常系最終成果物・QDC・他Family影響/誤PASS・誤NG・副作用/所見・根拠・残存リスク明示)。Fable=PM: F1目的・優先順位・QDC統括/F2自律的問題解決と再計画主導/F3 Sonnet・Opus報告の独立受入評価/F4承認Gate・Production完成管理/F5ユーザー判断・Open Item・過去決定管理。「特にF3を実効性のある業務とする。報告を受け取ったらFableは当初目的、既存承認済み仕様、前後工程、失敗時の最終成果物、QDC、承認境界、テスト・runtime証拠を評価する。『Opusがレビューした』『テストがPASSした』だけでは受入完了にしない。Fableが重要な証拠を独立に照合し、受入可否と根拠を記録する。毎回の全コード再読・全テスト再実行は求めず、リスクに応じて確認対象を選定する。」
第3層: フロー1Fable定義→2Sonnet調査設計→3Opus高リスクレビュー→4Sonnet DEV/Trial→5Fable独立受入→6ユーザー正式採否→7配線・runtime・Regression・SSOT・Git。G1変更前の仕様整合・影響範囲・未承認仕様隔離/G2 Trial終了時のFable独立受入・Status分類/G3 Production有効化前のユーザー承認と実装差分照合/G4 Production完成時の初回・retry・fallback・runtime・Regression・SSOT・Git確認。「新しい4種類のシステムを作ることではない。」既存仕様内の通常バグ修正は新仕様採用判断を毎回不要。Opus重点=新品質判定/NGルール・retry/fallback/Human Review・複数工程/Family・STOP/承認機構・再発不具合。高リスク修正がOpus所見後に入った場合は差分と失敗経路中心に再レビュー(無条件フル再レビュー不要)。未承認新仕様はDEV/Trial専用経路またはProduction既定OFFで隔離、口頭運用に依存しない。Fable受入未完なら次工程へ進まない。STOP・自律再計画は既存の有効な安全停止を優先。
§4B「Agent定義の具体的変更案。特にFableの定義を重点的に確認する。独立受入が現在のどの規則に存在し何が不足するか/報告の受領と受入判定を明確に区別できるか/Fableに必要な証拠照合手段が実際に使えるか/Opusの依頼範囲と所見原文の管理が適切か/Sonnetの技術的不確実性→ユーザー転送という既定動作をどう是正するか/Agent間のSTOP・承認・役割の矛盾をどう整理するか。Fableが必要な独立受入を実行できる構成になっているかを必ず確認すること。役割を文書に追加するだけで、手段・権限がなく実行不能になる設計は認めない。」
§4C「既存機構との対応表。G1〜G4について、現在どの機構が担っているか/文書上のみか実行時に強制されるか/機能していない箇所・重複・矛盾/最小限の是正方法/必要なテストと証拠。特に未承認機能が既定ONになる問題について、新しい大規模承認システムを作らず既存機構でどう防ぐかを具体化する。一方、単純なflag既定OFFだけで、すべての承認Gate違反が防げるとみなさないこと。」
§4D「Opus監査結果の反映。最低限: 変更目的と既存仕様の整合/不要になった機械NGルールの撤去確認/異常終了時の最終成果物/Opus所見原文と台帳の一致/所見採否の根拠/高リスク修正後の必要な差分レビュー/Fable独立受入の実行証拠について、既存機構の変更か運用の改善かを示す。レビューの回数や文書量をいたずらに増やさず実効性を重視する。」
Fable補足(事実): Fable(sandwich-pm)のツールはRead/Grep/Glob/Agentのみ(Bash・Edit・Writeなし)。Fableがtest実行やgit確認を自分で行う手段はなく、haiku-worker/sonnet-worker経由になる。F3の「証拠照合手段が実際に使えるか」はこの制約を前提に評価すること。KGORA監査では「Fableがhand-back後37秒・tool_use 0でユーザー報告」が記録されている。

## KPI provenance / Opus台帳更新
該当なし(参照のみ: OF-209〜224、OF-225〜235、OF-KGDC-01〜12)。

## 事前指定Read一覧
.claude/agents/{sandwich-pm,sonnet-worker,opus-consultant,haiku-worker}.md全文 / CLAUDE.md全文 / PM_BRIEF.md全文 / PM_GOVERNANCE.md Grep「^## 1\.|^## 7|^## 10|^## 11|^## 12|^## 14|^## 21|^## 26|11-1|11-3|11-5|8-Y」該当節のみ / templates DELEGATION_STANDARD_TEMPLATE・OPUS_INDEPENDENT_REVIEW_BLOCK・OPUS_CONTEXT_PACKET_TEMPLATE全文 / DAY1_C_MECHANISMS_01.md全文 / DAY1_REPORT_01.md §上位5問題・§T7〜T11・§9 / AUDIT_REPORT_01.md全文 / REVIEW_AUDIT_01.md §2・§4 / VALIDATION_OFF_01.md §1・§8 / tools/stop_scope_check_01.py・stop_all_family_z.py 1〜40行 / check_delegation_prompt.py 1〜60行 / USER_DECISION_REGISTER_01.md 1〜40行。

## 事前指定Grep
1. rg -n "STOP_ALL|STOP_NOTICE|RUN_LOCK|secret_scan|budget|approved-budget|HUMAN_REVIEW|verify_episode_audio_validation_gate|check_delegation_prompt" --glob "*.py" -l → G1〜G4表
2. rg -n "ENABLED\s*=\s*os\.environ|_ENABLED\s*=\s*\"1\"|default.*ON|既定ON" --glob "*.py" --glob "*.md" → 未承認既定ON事例、flag既定OFFで防げないGate違反列挙
3. rg -n "USER_DECISION_REQUIRED|判断を仰ぐ|ユーザー判断" .claude/agents CLAUDE.md docs/pm/PM_BRIEF.md → 転送根拠文言と是正文案
4. rg -n "受入|RESULT_PACKET|REPORT_LEDGER|Checklist|CHECKLIST" PM_GOVERNANCE.md PM_BRIEF.md → F3受入記録欄
更新位置: 新規 day2/AGENT_ROLE_DELTA_01.md・GATE_MECHANISM_MAP_01.md。

## 実行コマンド全文
(rgコマンド上記。T-0のcheck_delegation_prompt.pyのみpython実行。素のpython不使用)

## SSOT追記文
本委任ではSSOT編集なし。

## (旧見出し)実行コマンド・SSOT補足
rgコマンド。T-0のcheck_delegation_prompt.pyのみpython実行(.venv)。SSOT編集なし。

## Git
明示add: 上記2文書、delegation_log 2ファイル。RESULT_PACKET_ROLL2BはgitignoredならaddしないHEAD。コミットメッセージ: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A 委任_B: Agent役割差分(F1-F5実行可能性・Sonnet/Opus)+G1-G4既存機構対応表+Opus監査7項目の反映方式。規則/SSOT/Production無変更、JPY0`、trailer `Managed-ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01`。git push origin main。

## 報告
RESULT_PACKET_ROLL2B.md(30行以内): Status/T-0/F3実行可能性の結論/G1〜G4充足状況/flag既定OFFで防げないGate違反一覧/Opus監査7項目の反映方式/新規機構提案の有無と根拠/一覧外Read理由/commit。
AGENT_ROLE_DELTA_01.md構成: §0前提/§1 Fable(F1〜F5)/§2 Sonnet/§3 Opus/§4 矛盾一覧/§5 変更案一覧。
GATE_MECHANISM_MAP_01.md構成: §0前提/§1 G1〜G4対応表/§2 未承認機能既定ON防止/§3 Opus監査7項目対応表/§4 機能不全・重複・矛盾/§5 test・証拠/§6 未確認事項。
(注: 本ファイルは委任文の全項目を保存するが、一部は要約表記。原文はsandwich-pmの委任メッセージ。)
