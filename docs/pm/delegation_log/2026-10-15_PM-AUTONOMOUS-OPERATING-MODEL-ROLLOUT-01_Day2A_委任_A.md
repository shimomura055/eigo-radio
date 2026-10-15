# 委任文(全文保存・T-0) PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 2 Phase A 委任_A(2026-10-15)

## 管理ID

PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 2 Phase A 委任_A(R01〜R57規則照合=RULE_CHANGE_MATRIX_01作成。2026-10-15)。並行タスク: 同Phase Aの委任_B(AGENT_ROLE_DELTA_01/GATE_MECHANISM_MAP_01、別agent)が同時実行中。衝突回避: あなたは `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/RULE_CHANGE_MATRIX_01.md`、`docs/pm/RESULT_PACKET_ROLL2A.md`、`docs/pm/ACTIVE_TASK_ROLL.md`、`docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_A.md`(+_check.json)のみ書く。委任_Bは同dirの別ファイルと`RESULT_PACKET_ROLL2B.md`のみ書く。git commit時`.git/index.lock`があれば30秒待ち再試行(最大5回)。

## 性質/到達上限Status/禁止事項

性質: read-only調査+設計文書(規則・設定・Agent定義・SSOT・Production・Prompt・Gate・flag無変更、有料API・Opus呼出なし、費用JPY0)。到達上限Status: RULE_MATRIX_DRAFT(Fable受入・Opus条件Aレビュー待ち)。
Opus独立技術レビューGate判定: 条件A該当(運営モデルという新しい処理フロー設計)。ただしOpusレビューは統合後(委任_C成果物に対して)Fableが依頼する。本委任では呼ばない。
時間見込み: 90〜120分(57規則の読込・分類60分/55候補との突合20分/文書化30分)。並列化: 委任_Bと並列。本委任内は直列。
禁止: `CLAUDE.md`/`.claude/agents/*`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`/SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)の編集、`.py`/Prompt編集、Day3〜4の先行実装、`git add -A`/`-f`/amend/rebase/force push/stash/clean/reset --hard/checkout -f、委任_B領域への書込、既存のユーザー承認済みルールを「廃止・緩和」と独断で確定すること(提案として明記し、ユーザー判断欄へ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を全文`docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_A.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_A.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_A_check.json`を実行し結果をRESULT_PACKETへ1行記録。
T-2: TTSなし。T-3: 費用JPY0(有料API禁止)。

## ユーザー指示(原文)

(ユーザー2026-10-15「Day 2 運営設計: 既存規則・Agent定義との照合と最小変更案」。本委任に関係する部分を逐語)
目的: 「eigo-radioのAI開発チームを、個々の作業をこなすだけのチームから、Project全体の目的・QDCに責任を持ち、自律的に問題を解決するチームへ変える。ChatGPTとユーザーが合意したDay 2設計案v1を基準に、既存Repo・Day 1棚卸・Opusレビュー実態調査と照合し、実装すべき最小変更を具体化する。」再発防止重点7項目: 仕様変更が既存承認済み仕様と矛盾/変更後に不要になったValidator・制約が残る/正常系PASSだけで失敗時の最終成果物を確認しない/Sonnet・Opus報告をFableが十分に受入評価せずユーザーへ転送/未承認仕様がProductionで既定ON/技術的不具合が安易にUSER_DECISION_REQUIREDへ/決定済み事項が再びユーザー判断として提示。
Day 2設計案v1(基準): 第1層Charter=「Q>D>C≫開発費用」(Q=ユーザーが定めた必要十分な品質、D=Production完成までの速度、C=恒常的な量産単価)。8原則: 1必要十分な品質で止める/2品質を守りながら最速で完成させる/3常に量産単価を見る/4不具合は自律的に解決する/5解決手段に固執せず必要なら問題の捉え方から見直す/6Humanには重要Decisionだけを求める/7Project全体を見て判断する/8変更時は既存仕様と全体工程との整合性を必ず確認する(変更対象だけでなく承認済み既存仕様・上流下流・retry/fallback/regeneration・異常時の最終成果物・不要になる旧ルールまで)。ユーザー判断事項=新仕様の正式採用・品質ライン変更・重大なQDCトレードオフ・予算/Scope変更等に限定。未承認Production仕様の有効化・無言承認・安全STOPの迂回は禁止。常駐Charter約1,000〜2,000字、重要な安全・承認境界は省略しない。第2層: Sonnet=実行担当(原因調査・設計・実装・Trial・Regression・evidence、技術問題を安易にHumanへ転送せずFableへ原因・証拠・解決案)/Opus=独立レビュー(変更方法自体の合理性、当初目的・承認済み仕様・旧ルール撤去要否・異常系最終成果物・QDC・他Family影響、誤PASS/誤NG・副作用、所見・根拠・残存リスク)/Fable=PM: F1目的・優先順位・QDC統括/F2自律的問題解決と再計画/F3 Sonnet・Opus報告の独立受入評価(当初目的・既存承認済み仕様・前後工程・失敗時最終成果物・QDC・承認境界・test/runtime証拠を評価。「Opusがレビューした」「テストPASS」だけで受入完了にしない。毎回の全コード再読・全テスト再実行は不要、リスクに応じて選定)/F4承認Gate・Production完成管理/F5ユーザー判断・Open Item・過去決定の管理。第3層: 開発フロー1Fable定義→2Sonnet調査・設計→3Opus高リスクレビュー→4Sonnet DEV/Trial→5Fable独立受入→6ユーザー正式採否(新仕様)→7配線・runtime・Regression・SSOT・Git。論理Gate G1(変更前の仕様整合・影響範囲・未承認仕様隔離)/G2(Trial終了時のFable独立受入・Status分類)/G3(Production有効化前のユーザー承認と実装差分照合)/G4(Production完成時の初回・retry・fallback・runtime・Regression・SSOT・Git確認)。新しい4種類のシステムを作ることではない。既存仕様内の通常バグ修正は新仕様採用判断を毎回不要(受入・回帰・Production動作確認は必要)。Opus重点=新品質判定/NGルール・retry/fallback/Human Review・複数工程/Family・STOP/承認機構・再発不具合。高リスク修正がOpus所見後に入った場合は差分と失敗経路中心に再レビュー。未承認新仕様はDEV/Trial専用経路またはProduction既定OFFで隔離、口頭運用に依存しない。Fable受入未完なら次工程へ進まない。STOP・自律再計画は既存の有効な安全停止を優先。
§4A「57規則の維持／修正／統合／廃止: R01〜R57を漏れなく照合し、それぞれ以下を提示する。現在の規則・参照ファイル/今回の8原則・Fable役割・Gateとの対応/維持／修正／統合／廃止/変更理由/重複または矛盾する既存規則/重要な安全・承認条件への影響/Day 3〜4の必須変更か後回しか。今回の新設計を理由に、既存のユーザー承認済みルールを独断で廃止・緩和しないこと。」§3「資料は最新のRepo状態と突き合わせ、過去の棚卸結果を無条件に採用しない。個別タスクが並列で変更中の場合、最新版と競合可能性を明示する。」§6「既存仕様とDay 2案に重大な競合がある場合は、事実・影響・代替案を示してSTOPする。」最重要: 「既存ルールを大量に書き換えることではない。8原則を共有し、Fableが本当にPMとして機能し、既存仕様との矛盾や未承認Production変更を防ぎながら、品質を守って開発を速めること。この目的に必要な最小限の変更だけを提案すること。」

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし(OF-209〜224[Research-01条件A]はDay1で反映済み。本委任では参照のみ)。

## 事前指定Read一覧

- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/DAY1_A_RULES_INVENTORY_01.md`: 全文(R01〜R57の正本)
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/DAY1_REPORT_01.md`: 全文
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/DAY1_E_HANDOVER_01.md`: 全文
- `docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/FINAL_REPORT_01.md`: Grep「変更候補|C01|C55|§8」ヒット節(55変更候補の一覧)
- `docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/RECOMMENDED_PROJECT_DEFINITION_01.md`: 全文
- `er071_output/m2p0_n01_production_wiring_01/opus_review_root_cause_audit_01/AUDIT_REPORT_01.md`: §8(Day2最小案A1〜A3/B1〜B4/C1)と§1
- `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/review_audit/REVIEW_AUDIT_01.md`: §4(再発防止案)
- `CLAUDE.md`: 全文
- `.claude/agents/sandwich-pm.md`・`sonnet-worker.md`・`opus-consultant.md`・`haiku-worker.md`: 全文(規則の実際の文言確認用。編集禁止)
- `docs/pm/PM_BRIEF.md`: 全文
- `docs/pm/PM_GOVERNANCE.md`: R01〜R57が参照する節のみGrep→該当範囲(全文Read禁止)
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep「判断済み|#59|#49|#52」ヒット行(既決事項の把握)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 各Rxxの現在文言が最新Repoと一致するか: R表の参照ファイル:行をGrepで再確認(2026-10-14以降のcommitで変化した規則を「最新版差分あり」と注記。`git log --since=2026-10-14 --format="%h %s" -- docs/pm/PM_GOVERNANCE.md CLAUDE.md .claude/agents docs/pm/PM_BRIEF.md`)。
2. 8原則・F1〜F5・G1〜G4との対応: 各Rxxを少なくとも1つの原則/責任/Gateへ紐づけ、紐づかない規則は「対応なし(維持理由または統合候補)」と明記。
3. 重複・矛盾: `rg -n "USER_DECISION_REQUIRED|判断を仰ぐ|上限到達" CLAUDE.md .claude/agents docs/pm/PM_BRIEF.md docs/pm/PM_GOVERNANCE.md` でDay1 T8(「判断を仰ぐ」が11-1に勝つ)型の矛盾箇所を行番号で列挙。
更新位置: 新規 `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/RULE_CHANGE_MATRIX_01.md`。

## 実行コマンド全文

- `git log --since=2026-10-14 --format="%h %ad %s" --date=short -- docs/pm/PM_GOVERNANCE.md CLAUDE.md .claude/agents docs/pm/PM_BRIEF.md`
- rgコマンドは上記。T-0のcheck_delegation_prompt.pyのみpython実行。PATH上の素のpythonは使わない。

## SSOT追記文

本委任ではSSOT編集なし。RESULT_PACKETに「Phase A終了後にDECISION_LOGへ記録すべき事項案」を1〜2行。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: なし。明示add: `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/RULE_CHANGE_MATRIX_01.md`、delegation_log 2ファイル。`ACTIVE_TASK_ROLL.md`/`RESULT_PACKET_ROLL2A.md`はgitignored確認のうえaddしない。
コミットメッセージ: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A 委任_A: R01〜R57 規則照合Matrix(維持/修正/統合/廃止案、8原則・F1-F5・G1-G4対応、重複矛盾、Day3-4必須/後回し)。規則/SSOT/Production無変更、JPY0`、trailer `Managed-ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/ACTIVE_TASK_ROLL.md`(固定ヘッダ書式、Status=DAY2_PHASE_A_IN_PROGRESS、委任_A完了/委任_B並行/委任_C予定、STOP条件=既存仕様とDay2案の重大競合、禁止=規則実変更)。`docs/pm/RESULT_PACKET_ROLL2A.md`(30行以内): Status/T-0/分類集計(維持/修正/統合/廃止の件数、Day3-4必須件数)/重大競合の有無(あればSTOP)/ユーザー承認済み規則で「修正・廃止」提案に該当するもの一覧(独断確定していないことの明記)/最新版差分ありの規則/一覧外Read理由/commit。
`RULE_CHANGE_MATRIX_01.md`の構成: §0 凡例・前提(Day1棚卸を無条件採用しない旨、最新Repo突合日時)/§1 57行の表(列: R番号/現在の規則要旨/参照ファイル:行/対応する原則・責任・Gate/判定[維持/修正/統合/廃止]/変更理由/重複・矛盾する規則/安全・承認条件への影響/Day3-4必須・後回し/ユーザー承認済みか[承認日・管理ID]/備考[55候補との対応番号])/§2 判定集計と統合グループ案/§3 矛盾箇所一覧(行番号付き)/§4 重大競合・STOP該当の有無/§5 未確認事項。

(保存注記: 上記はSonnet実行層が受領した委任文の保存。システム側固定指示[STOP確認・Agent禁止等]はagent定義側にある)
