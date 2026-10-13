# 委任_01 FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01 (2026-10-13、委任文全文)

## 管理ID

FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01 委任_01(初回)。前身: FAMILY-Z-STANDARD-PREVIEW-PROMPT-TRIAL-01(commit 90e08933、Status USER_DECISION_REQUIRED、OPEN-338)。並行タスク: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01(`er068_*`、SSOT編集中の可能性あり)、FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02(`er069_*`)が同時稼働。本委任のSSOT編集はOPEN-338行・DECISION_LOG末尾追記・CURRENT_SPEC(Trial中1行のみ)に限定し、**SSOT編集は最終工程で行う**。編集直前に`git status --porcelain OPEN_ITEMS.md DECISION_LOG.md CURRENT_SPEC.md docs/pm/USER_DECISION_REGISTER_01.md`を確認し、他agentの未commit変更があれば60秒待ち×5回まで再確認、残っていても自分の変更は該当行/末尾への追記のみとし他agentの変更を消さない。commit時は自分が変更した行を含むファイルのみ明示add(他agentの変更が混在する場合はその旨RESULT_PACKETに記録)。`.git/index.lock`存在時は30秒待ち×3回。commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。一時ファイル: `docs/pm/ACTIVE_TASK_FZPX.md`/`docs/pm/RESULT_PACKET_FZPX.md`。

## 性質/到達上限Status/禁止事項

- 性質: 設計方針確定済み(ユーザー判断: Family X Standard Preview Promptを基準に統一)に基づく、Prompt統一+入力条件統一(Comment 1・2)+最小Trial 1回+回帰評価。Production配線は禁止。
- 到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`宣言禁止。Trial結果が良好でもProduction実装へ進まない。
- 費用: 上限¥5(Guardrail。有料Trialは1案・1回のみ、gpt-6-luna 1 call 約¥0.1、出典`er006_model_routing_pricing_coverage_test_01.py` L50-52、USD/JPY=160)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。2案以上の生成・複数take・追加探索は禁止(ユーザー指示)。
- STOP条件(ユーザー指示): (1)Family X原文との差分に「News⇔物語の差に起因する必要最小限」と説明できないものが1つでもある→Trial実行前にSTOP(差分表を提示)。(2)追加のPrompt調整が必要/Family X側の仕様変更が必要/必要最小限の差分では成立しない/想定外の副作用→STOP。(3)Comment 1・2の両方を入力する構成が既存のComment生成順序・prior再利用と矛盾し、Production経路の変更なしにTrialで再現できない→STOPして設計案のみ報告。
- 禁止: 今回対象以外(Family X Prompt、Family Z Advanced Prompt、Comment、Writer本文、KP、TTS等)の変更。Production code(`er003_*`, `er026_*`, `er062_*`, `er063_*`, `er006_*`)の編集(読み取りのみ。Trialは新規script `er070_family_z_std_preview_x_alignment_01.py`で既存関数をimportして実行)。Family Z独自の品質改善ルールの追加。Trial結果だけを根拠にFamily Xにない仕様を追加すること。`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`のsource・値表示、秘密値の出力、`*.wav`・telemetry・log・`words/`のadd、`ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のcommit、Melos run_e2e_02配下・Master Store・HR queue・attempt_history・telemetryへの書込、Melos Production再生成・試聴ページ更新、外部停止プロセスの再起動、監督ループ/`timeout`ラッパ。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(Melos旧STOP_NOTICEはrun_e2e_01向け=非適用)。
- Opus独立技術レビューGate判定: **非該当**(既存Family X Promptへの整合であり新構造ではない。Production採用提案時に条件Cを別途)。
- 時間見込み: 60〜80分。並列化: 他2agentと並列。本委任内は直列。
- 最新モデル原則(PM_GOVERNANCE 25節): Production同一`gpt-6-luna`・reasoning effort high(例外理由=Production Preview生成との比較可能性)。応答model_id実測を記録。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。 D-1: Grep→該当行範囲Read基本。 G-1: git出力は最小化。 F-1: transcript退避不要。
T-0: 委任文全文を本ファイルへ保存し`check_delegation_prompt.py`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSなし(該当なし)。 T-3: 費用上限はGuardrail(上記定型文)。

## ユーザー指示(原文、2026-10-13、管理ID FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01)

「## 1. 目的 Family Z Standard(日本語)PreviewのPromptを、Family X Standardの正式Production Promptを基準として統一する。ユーザー判断: Family XとFamily ZのPreviewは、基本的に同じ設計思想・構造・指示内容とする。Newsと物語の違いに対応するための必要最小限の文言変更は許可する。それ以外の勝手な省略・修正・加筆は禁止。Family Z独自のPreview品質改善ルールを追加しない。
## 2. 現在の問題 前回のTrialではFamily X Standard Promptの一部を参考にしてFamily Z用Promptを作り直したが、次の不整合が残った。Family X Standardの指示内容を完全には継承していない。Comment 1・2の両方ではなく、Comment 1のみを重複回避に使用した。元Promptの一部を独自解釈で省略・変更した。その結果、あらすじ化は改善したものの、抽象的・評論調のPreviewとなった。これはユーザーが意図した「Family Xを基本とする」とは異なる。
## 3. 今回の対応 A. 正本確認: まずRepoの正式Production経路を確認する。基準: `er003_v1_iran01_a2_generate.py`の`PREVIEW_ROLE`。対象: `er026_family_z_fiction_production_runner_01.py`の`_FAMILY_Z_PREVIEW_ROLE_JA`。実際の使用経路: `er062_family_z_writer_01.py`の`run_support_std()`。CURRENT_SPECと既存のユーザー承認内容も確認すること。
B. Promptの統一: Family X Standardの`PREVIEW_ROLE`を基本として、次の方針でFamily Z Standard用Promptを構成する。変更を許可するもの: News→物語/ニュース本文→物語本文/ニュースの論点→主人公が直面する問題・対立など、物語に対応する表現/その他、Newsと物語の違いにより、そのままでは意味が成立しない箇所の必要最小限の置換。変更を禁止するもの: theme/problem/value/questionの独自省略・追加/分量や文数の独自変更/ネタバレ・結論・転換点に関する禁止条件の省略/Comment 1・2との重複回避条件の省略/興味喚起の目的の変更/Family Z専用の新しい構成ルールの追加/抽象化・具体化などを狙った独自のPrompt調整。Family X Standardに明記されている指示と、その意図を維持すること。Family X Standardにない仕様を、今回のTrial結果だけを根拠に追加しない。
C. 入力条件も統一: 現在、Family Z StandardはComment 1のみをPreview生成時の重複回避入力として使用している。これをFamily X Standardと同様に、Comment 1・2の両方を渡す構成にする。単なるPrompt文面の統一ではなく、実際のProduction呼出で両Commentが入力されることを確認する。既存のComment生成順序・再生成・prior再利用との整合も確認する。
## 4. 差分レビュー 作業前にFamily X Standardと変更後Family Z StandardのPromptを対比し、全ての差分を提示する。各差分には以下を付記する。Family Xの原文/Family Zへの変更後/変更理由/News⇔物語の差に起因する必要な変更か。必要最小限と説明できない差分が1つでもあればSTOP。独自改善の提案があっても、今回の作業には混ぜず、未採用の提案として報告する。
## 5. TrialとProductionの境界 現在Status: `USER_DECISION_REQUIRED`。今回許可する範囲: 1.既存仕様・Production経路の確認 2.Prompt差分と入力条件の整合設計 3.必要最小限のTrial 4.出力品質と回帰影響の評価。今回のユーザー判断は「Family Xを基準にする」という設計方針の確定であり、変更後Promptの品質検証を省略してProduction採用してよいという意味ではない。変更後Promptを無条件でProductionへ配線しないこと。今回の対象以外のFamily X Prompt、Family Z Advanced Prompt、Comment、Writer、KP、TTS等は変更禁止。有料Trialは1案のみ。既存のMelos本文・Commentを再利用し、無駄なLLM生成を避ける。追加探索はユーザー承認なしに行わない。
## 6. 受入条件・検証 Family X Standard Promptとの完全な差分表がある/差分はNews⇔物語の必要最小限に限定される/Comment 1・2が入力される/Family Xの既存指示が省略されていない/Trialで生成した日本語Previewの全文が確認できる/あらすじ化・興味喚起・ネタバレ・Comment重複・日本語の自然さを評価する/既存経路に対するRegressionを実施する/Productionの初回・retry・regeneration経路に不整合がないか確認する/Dangling Referenceがない/実際に検証した範囲と未検証事項を明示する。
## 7. 記録・STOP条件 CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、Trial報告を実態に合わせて更新する。ただし、未承認PromptをCURRENT_SPECの正式Production仕様として記載しない。Trial終了時は`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`のいずれかに分類する。Trial結果が良好でも、自動的にProduction実装へ進まない。追加のPrompt調整が必要、Family X側の仕様変更が必要、必要最小限の差分では成立しない、または想定外の副作用がある場合はSTOPして報告する。最後に、未処理のUSER_DECISION_REQUIRED、APPROVED_FOR_PRODUCTION未配線項目、SSOT・Decision Log・Open Itemsの未反映を確認する。
## 8. 最終報告 1.Family XとFamily ZのPrompt差分、および変更理由 2.Comment 1・2を含む入力条件の整合確認 3.改善後Preview全文と品質評価 4.Production採用に向けた残課題・ユーザー判断。最重要: Family Xと同じものを作ること。Family Z用に新しい正解を考え直すことではない。」

## KPI provenance欄 / Opus台帳

Trial Preview=`fresh`(Trial隔離の1 call)。比較対象BEFORE=`reuse`(run_e2e_02 `support/a2_support.json`のpreview)。fresh Production初回path E2E値: No。Opus台帳更新: 該当なし。

## 事前指定Grep一覧+追記位置・更新位置の手順(要旨)

er003 L160-230 PREVIEW_ROLE/呼出、er026 L460-520、er062_family_z_writer_01 run_support_std、er062_family_z_structure_01 lint_support_text、CURRENT_SPEC Preview原則、er067 TRIAL_REPORT_01 §1・§6・prompt_before_01.txt、er067 script、run_e2e_02 std.md/a2_support.json、OPEN-338行、USER_DECISION_REGISTER_01。
追記位置: OPEN_ITEMS OPEN-338行末(【2026-10-13 FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01】…)/DECISION_LOG末尾/CURRENT_SPEC既存Family Z Std Preview記載行末に1文のみ(「(2026-10-13 FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01: Family X基準へ統一する設計方針をユーザー決定。統一後Prompt・Comment 1・2入力はTrial中、Production未採用)」、該当行が無ければ追記せず記録)/USER_DECISION_REGISTER_01のFamily Z Std Preview (a)(b)(c)行を「判断済み(2026-10-13、Family X基準へ統一=新管理ID)」へ更新+新行+集計再計算/REPORT_LEDGER本ID行追加。

## 作業内容(要旨)

A. 正本確認 -> `er070_output/family_z_std_preview_x_alignment_01/PATH_AUDIT_01.md`(表)。
B. Prompt統一: X PREVIEW_ROLEを逐語の土台、News⇔物語で意味が成立しない箇所のみ置換。差分表`PROMPT_DIFF_01.md`(行ごとにX原文/Z変更後/理由/News⇔物語起因Yes/No)。Noが1つでもあればTrial実行せずSTOP。独自改善案は`UNADOPTED_PROPOSALS_01.md`へ分離。
C. 入力条件: Comment 1・2両方を渡す設計`WIRING_DESIGN_01.md`(実装しない)。Trialはa2_support.jsonのComment 1・2を読み込みscript側で再現。
D. Trial(1案・1call): `er070_family_z_std_preview_x_alignment_01.py`、出力`preview_after_01.txt`/`prompt_after_full_assembled_01.txt`/`cost_01.json`。lint実行。`TRIAL_REPORT_01.md`にBEFORE/前回Trial/今回AFTER 3列評価(採用判断は書かない)。
E. 回帰: er062_family_z_writer_01_test_01.py、er026_family_z_fiction_production_runner_01_test.py、er003 test相当。state_guard(run_e2e_02配下・Production py 5本sha256不変)。Dangling Reference確認。初回/retry/regeneration経路表。
F. Status分類、SSOT更新、未処理UDR・APPROVED未配線・SSOT未反映の確認。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01_01_check.json
set PYTHONUTF8=1
.venv\Scripts\python.exe er070_family_z_std_preview_x_alignment_01.py --mode diff --out-dir er070_output\family_z_std_preview_x_alignment_01
.venv\Scripts\python.exe er070_family_z_std_preview_x_alignment_01.py --mode trial --out-dir er070_output\family_z_std_preview_x_alignment_01 --budget-jpy 5
.venv\Scripts\python.exe er070_family_z_std_preview_x_alignment_01_test_01.py
.venv\Scripts\python.exe er062_family_z_writer_01_test_01.py
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01_test.py
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```
(`--mode trial`は差分表STOP判定がPASSの場合のみ。)

## Git

SSOT編集権あり(OPEN_ITEMS OPEN-338行、DECISION_LOG末尾、CURRENT_SPEC該当行1文、USER_DECISION_REGISTER_01、REPORT_LEDGER。PM_GOVERNANCEは編集しない)。明示add対象: er070 script/test、er070_output/.../*.{md,txt,json}、本委任文(+_check.json)、SSOT各ファイル。コミット2つ: (1)「FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01 委任_01: Family Z Std PreviewをFamily X基準へ統一(差分表+Comment1・2入力設計+Trial 1 call JPY<実費>、Status=<判定>、Production無変更)」(2)「...: SSOT記録」。trailer `Managed-ID: FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01`。secret_scan後、git status --porcelainで意図外ファイル不在確認、push。

## 報告

`docs/pm/RESULT_PACKET_FZPX.md`に(0)check結果・STOP確認 (1)PATH_AUDIT要約 (2)PROMPT_DIFF全表+STOP判定+未採用提案 (3)WIRING_DESIGN要約 (4)Preview全文3列+品質評価+lint (5)Status (6)回帰・state_guard・Dangling Reference (7)費用 (8)SSOT反映・未処理UDR等 (9)検証範囲/未検証/ユーザー判断候補 (10)commit hash+raw URL。`docs/pm/ACTIVE_TASK_FZPX.md`に固定ヘッダ。
