## 管理ID

PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 2 Phase A 委任_C(統合: DAY2_DESIGN_RECONCILIATION_01 / MINIMUM_CHANGE_PLAN_01 / USER_DECISIONS_01 作成。2026-10-15)。前委任: 委任_A=RULE_CHANGE_MATRIX_01(commit bc3f49718)、委任_B=AGENT_ROLE_DELTA_01+GATE_MECHANISM_MAP_01(commit 1f77f431c)。並行タスク: KGDC 委任_03(gloss Trial、`er071_output/.../gloss_alignment_correction_01/`とSSOT行OPEN-356等を書く)。あなたはSSOTを編集しないので衝突なし。git commit時`.git/index.lock`があれば30秒待ち再試行(最大5回)。

## 性質/到達上限Status/禁止事項

性質: read-only調査+設計統合文書(規則・Agent定義・SSOT・Production・Prompt・Gate・flag無変更、有料API・Opus呼出なし、費用JPY0)。到達上限Status: DAY2_PHASE_A_DRAFT_COMPLETE(Opus条件Aレビュー→Fable独立受入→ユーザー設計承認待ちSTOP)。
Opus独立技術レビューGate判定: 条件A該当。本委任完了後にFableが統合成果物へ依頼する(本委任では呼ばない)。
時間見込み: 60〜90分。並列化: 不要(統合は直列)。
禁止: `CLAUDE.md`/`.claude/agents/*`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`/SSOT全般/`.py`/Prompt/flagの編集、Day3〜4先行実装、新規Hook/Validator/台帳の作成、A/Bの成果物ファイルの編集(矛盾があれば本書で指摘し上書きしない)、`git add -A`/`-f`/amend/rebase/force push/stash/clean/reset --hard/checkout -f、既決事項の再質問、ユーザー承認済み規則の独断廃止・緩和。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ。G-1: git出力は--porcelain/--stat/--short等で最小化。F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を全文`docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_C.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記> --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_C_check.json`を実行し結果をRESULT_PACKETへ1行記録。
T-2: TTSなし。T-3: 費用JPY0。

## ユーザー指示(原文)

(ユーザー2026-10-15「Day 2 運営設計」§4E・§5・§7・最重要、逐語)
§4E「Day 3〜4の最小実装範囲: 候補となるCharter、Agent定義、PM_GOV、PM_BRIEF／ACTIVE_TASK、STOP共通化、UDR台帳、secret scan、日次費用集計などについて、必須／任意／後回しを分類する。Day 1案の『文書5＋機械3』を固定条件とはせず、今回のレビュー不全の教訓を踏まえて再評価する。各変更について、対象ファイル、目的、依存関係、概算工数、期待効果、QDC上のリスクを提示する。重複した新規管理制度・Hook・Validator・台帳の乱立を避ける。」
§5「ユーザー判断事項の整理: Day 1報告で提示された7項目も、今回のDay 2案に再照合する。CLAUDE.mdの速度・安定性表現/上限到達時のFable再計画/Git secret scan hook/70円／記事セットの定義/日次1,000円の管理方式/Day 5〜6のTrial案件/Human Review等の詳細方針。過去に既にユーザーが判断した事項を再質問しないこと。技術的な設計詳細はFableが判断し、本当にユーザーの承認が必要な規則・権限・予算・品質の変更だけを提示する。」
§7「成果物: 1 DAY2_DESIGN_RECONCILIATION_01: 設計案v1と既存環境の照合結果。2 RULE_CHANGE_MATRIX_01。3 AGENT_ROLE_DELTA_01。4 GATE_MECHANISM_MAP_01。5 MINIMUM_CHANGE_PLAN_01: Day 3〜4の最小変更案、依存関係、QDC影響。6 USER_DECISIONS_01: ユーザー判断が必要な事項と推奨案。最初に、非エンジニアのPMが判断できる超サマリを提示すること。」
最重要「今回の目的は、既存ルールを大量に書き換えることではない。8原則を共有し、Fableが本当にPMとして機能し、既存仕様との矛盾や未承認Production変更を防ぎながら、品質を守って開発を速めること。この目的に必要な最小限の変更だけを提案すること。」
Day2設計案v1(基準)の要旨: Charter「Q>D>C≫開発費用」+8原則(1必要十分な品質で止める/2品質を守りながら最速で完成/3常に量産単価を見る/4不具合は自律的に解決/5解決手段に固執せず問題の捉え方から見直す/6Humanには重要Decisionだけ/7Project全体を見て判断/8変更時は既存仕様と全体工程との整合性を必ず確認)、常駐Charter約1,000〜2,000字・安全承認境界は省略しない。Fable F1〜F5(F3独立受入を実効性ある業務に)。Sonnet実行担当・Opus独立レビュー。フロー1〜7、G1〜G4(新システムを作ることではない)。未承認新仕様はDEV/Trial専用経路または既定OFFで隔離、口頭運用に依存しない。
本日ユーザーが既に判断した事項(再質問禁止): (1)gloss再整合flagの既定OFF=承認・PRODUCTION_WIRED済み(「既定ON維持+凍結」案は不採用)。(2)「整合済みglossの不要書換えのような技術的改善はユーザー判断事項ではなく開発側で自律改善。問題を見つけるたびに報告せず、解決または目処をつけてから報告。ただし明示STOP・予算上限・承認範囲・重大な品質安全問題は守る」(KGDC ②)。(3)KGDC修正Trialの停止方式A'は設計承認(Production採用ではない)。(4)今回の運営規則変更は不要(KGDCの文脈)、包括改善はこのROLLOUTで行う。(5)第8原則追加・Charter反映・Agent役割権限変更・Day2実装・Opusレビュー新ルールはKGDC/KGORAの対象外で「別途ユーザーが判断」=本Phase Aの対象。
Fableからの事実: Fable(sandwich-pm)のツールはRead/Grep/Glob/Agentのみ。本セッションで利用可能なAgent typeはopus-consultantとsonnet-workerのみ(haiku-workerは一覧に無く起動不可=委任_Bの推測を裏付け)。Fableは本日、受入のためにDESIGN_DRAFT_01全文・FIX_02/VALIDATION_02の該当行をRead/Grepしており、特定ファイルの読取は実務上行っている(sandwich-pm.md L29の規則はディレクトリ走査・大量ログを意図したもので、特定ファイルの受入確認まで禁じる運用にはなっていない)。

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし(参照のみ)。

## 事前指定Read一覧

- day2/RULE_CHANGE_MATRIX_01.md、AGENT_ROLE_DELTA_01.md、GATE_MECHANISM_MAP_01.md: 全文
- DAY1_REPORT_01.md: §9・Day3-4必須・上位5問題 / DAY1_D_BUDGET_01.md: 全文
- er071_output/m2p0_n01_production_wiring_01/opus_review_root_cause_audit_01/AUDIT_REPORT_01.md: §8・§10
- er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/review_audit/DAY2_HANDOFF_NOTE_01.md: 全文
- RECOMMENDED_PROJECT_DEFINITION_01.md: Grep Charter等(Charter草案流用元)
- docs/pm/USER_DECISION_REGISTER_01.md: Grep(既決確認) / CLAUDE.md: Grep / PM_GOVERNANCE.md: Grep(7-6|15-8|70円|1,000円|日次)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. A/B間の不整合: 両文書のG1〜G4対応・矛盾一覧(A §3 C1〜C15、B §4 C1〜C10)・変更案を突合し、重複はID対応表で統合、食い違いは本書で裁定案(Fable最終判断用に両論併記)。
2. 7項目再照合: Day1 §9 #1〜#7それぞれに「既決(日付・出典)/今回のDay2案で変化/依然ユーザー判断が必要/Fable技術判断で足りる」を判定。本日の既決(上記(1)〜(5))を反映し、#2(上限到達=UDR→再計画)はKGDC②の「技術的改善はUDRにしない」と整合する形で選択肢を再構成。
3. 最小変更計画: Day1「文書5+機械3」を、A(必須17)・B(規則修正4件・機構変更0・任意2)・監査§8・01B §4と突合して必須/任意/後回しへ再分類。各項目: 対象ファイル・目的・依存関係・概算工数(時間)・期待効果(再発防止7項目のどれに効くか)・QDC上のリスク・ユーザー承認要否。重複する新規制度・Hook・Validator・台帳を作らない。Charterは常駐1,000〜2,000字の草案本文を添付(安全・承認境界を省略しない)。
4. Charter草案の文字数を数えて記載。
更新位置: 新規 day2/DAY2_DESIGN_RECONCILIATION_01.md・MINIMUM_CHANGE_PLAN_01.md・USER_DECISIONS_01.md・CHARTER_DRAFT_01.md(草案、採用はユーザー承認後)。

## 実行コマンド全文

- `.venv\Scripts\python.exe -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/CHARTER_DRAFT_01.md`
- T-0のcheck_delegation_prompt.py。git status --porcelain→明示add→commit→git push origin main。PATH上の素のpythonは使わない。

## SSOT追記文

本委任ではSSOT編集なし。USER_DECISIONS_01末尾に「ユーザー設計承認後にDECISION_LOG/USER_DECISION_REGISTERへ記録する文案」を置く。

## Git

SSOT編集権: なし。明示add: 上記4文書、delegation_log 2ファイル。RESULT_PACKET_ROLL2C.md/ACTIVE_TASK_ROLL.mdはgitignored確認のうえaddしない(ACTIVE_TASK_ROLL.mdのヘッダはStatus=DAY2_PHASE_A_DRAFT_COMPLETE_OPUS_REVIEW_PENDINGへ更新のみ)。
コミットメッセージ: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A 委任_C: 設計案v1照合(DAY2_DESIGN_RECONCILIATION_01)+最小変更計画(必須/任意/後回し、Charter草案)+ユーザー判断事項(Day1 7項目再照合、既決除外)。規則/SSOT/Production無変更、JPY0`、trailer `Managed-ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01`。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET_ROLL2C.md(35行以内): Status/T-0/超サマリ案(非エンジニア向け10行以内)/必須・任意・後回しの件数と必須一覧/機構変更(コード・script・hook)の件数/Charter草案文字数/A・B間の不整合と裁定案/本当にユーザー判断が必要な事項の一覧(各: 決めること・背景・選択肢と影響・推奨と根拠。既決は別表)/Phase A全体でFableが独立受入時に確認すべき証拠の所在(ファイル:節)/未確認事項/commit。
各成果物の構成:
- DAY2_DESIGN_RECONCILIATION_01.md: §0超サマリ/§1 v1の3層と既存環境の照合/§2 再発防止7項目→変更の対応表/§3 A/B統合(ID対応表・裁定案)/§4 既存仕様との重大競合の有無/§5 未確認。
- MINIMUM_CHANGE_PLAN_01.md: §0方針/§1 必須/§2 任意/§3 後回し(7属性表)/§4 依存関係図/§5 Day1「文書5+機械3」との差分と理由/§6 実装順序案と概算総工数/§7 QDC総括。
- USER_DECISIONS_01.md: §0 既決事項表/§1 今回ユーザー判断が必要な事項(推奨付き)/§2 Fable技術判断で進める事項/§3 承認後の記録文案。
- CHARTER_DRAFT_01.md: 常駐Charter草案本文(1,000〜2,000字)+採用時の配置先案。

(注: 本ファイルは受領した委任文の全文保存方針に従い作成。長大な構造は同内容を節ごとに忠実に再掲。Sonnet 5.5が保存。)
