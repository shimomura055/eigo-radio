# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_03(C1陽性対照Trialの実走[R1 B3 12 call→eval→条件成立時R2 Writer probe最大4本→盲検rubric]+Trial Closeout文書+SSOT統合[Research原因・C1結果・PLW最終ラベル・OPEN-416更新])。2026-10-20。
並行タスク衝突確認: 並行委任なし(XRG 委任_01=30c694bbb、委任_02=b2e078267、PLW 委任_02b=de3297bb6 まで完了・push済み)。SSOT編集権: あり(`OPEN_ITEMS.md` OPEN-425/OPEN-424/OPEN-416/OPEN-423行、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md` #125/#124/#112行、`docs/pm/REPORT_LEDGER.md`。Grep→該当行のみ)。`CURRENT_SPEC.md`は編集しない(Production非変更)。

## Fableの照合結果と決定(前提)
- 委任_01(Research原因): 「誰が」=出典(国連特使声明10/11・国連発表10/9)に`Ansar Allah`明記→Researcherのclaim化で主体脱落(F01/F11)+検証に省略検知観点なし=**仕様の空白**(11-8乖離なし)。「なぜ」=収録出典に無し(正しい結果、外部未調査)。「つながり」=構造化で主体・文脈脱落、B3不採用は正当。是正=Research/検証Promptへ条件付き観点追加=**新仕様→ユーザー判断事項**(本委任では実装しない。Opus条件Aはユーザー承認後)。
- 委任_02(C1): 評価撤回SSOT済み。陽性対照PC1=hormuz(期待core HF-006)、PC2=中東11件+実在の国連出典Fact F12/F13/F14(VERIFIED付与は委任_02の原文照合=Production Verifierではない、test専用)、陰性NC1=coffee run_l3_01(追加0が正解)。設計=`C1_POSITIVE_CONTROL_DESIGN_01.md`、matrix=`c1_posctrl_matrix_01.json`、harness=`er083_c1_positive_control_01_{build_ledger,run,eval,test_01}.py`(dry-run 12セルOK、99 passed)。
- Fable決定: (1)実走を承認(ユーザー原文§3「陽性対照を用いた限定的な追加Trialは今回の指示範囲内」)。Cap=¥180(期待約150、R1 125/R2 55の内訳Guardrail)。案件合算≤300(現在0)。日次: 当日既使用JPY143.5(PLW含む)+180でも1,000内。(2)Opus再レビュー不要(C1文言・処理フロー・schema・producer不変、新規は評価系のみ。Opus_Iレビュー済み設計の延長)。(3)Muse/boredomの追加陽性は採用しない。(4)判定基準は設計書§の事前固定のまま変更しない。(5)PC2でbaselineもF12を採用した場合(NONDISCRIMINATING)は「C1不要でもLedgerにFactがあれば通常B3が拾う」という重要所見として記録(C1核心機能の判定はPC1と合わせて行う)。(6)W-1(Writer)はC1が期待coreを採用したセルのみ、最大4本。
- 禁止: Production Prompt/schema/producer/Writer/B3/Research Promptの変更。架空Fact。test Ledgerの`production_use`違反。過去テーマへの大規模展開。`git add -A/-u/-f`・amend・rebase・force push・stash。有料runの再起動(途中停止時は原因を記録しFableへ報告。skip-existing再開も委任文の明示許可が必要=本委任では**R1の途中停止に限り、原因がharness側で費用重複が無いことを確認できた場合に1回だけ再開を許可**し、再開の事実・原因・重複0をRESULT_PACKETに開示する)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV/Trial専用経路)+SSOT統合。
- 到達上限Status: `C1_POSITIVE_CONTROL_TRIAL_CLOSEOUT_PENDING_FABLE`(Trial StatusはVALIDATED候補/REJECTED/判断候補をevalが機械判定、最終ラベルはFable)。Production採用はユーザーのみ。
- 修正範囲の線引き(11-8): harnessの不具合は是正範囲内。Production判定・Promptは呼ぶのみ。
- Opus独立技術レビューGate(11-3): 非該当(上記(2))。
- 費用/日次: 当日既使用JPY143.5(出典RESULT_PACKET_PLW2b.md)/残JPY856.5/本委任見積JPY約150(R1 B3 12 call×実測8.67≈104、R2 W-1最大4本≈46)/承認区分C(ユーザー承認済みTrial範囲・案件合算≤300・日次内)。
- T-3: 上限¥180(Guardrail、R1 125/R2 55)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 時間見込み: 全体2.5〜3.5h(T-0 10分/R1実走+eval 40分/R2+盲検rubric 50分/Closeout 40分/SSOT 30分/報告15分)。並列化: R1のセルはprocess並列可(cost log分離)。盲検rubricは別process。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さずsession JSONLから抽出**(`extract_delegation_from_jsonl_01.py --role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`で管理ID行に`委任_03(C1陽性対照Trialの実走`を含む最初のもの。indexで特定できなければ委任_02と同様にJSONL行を直接抽出)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_03.md`。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記「性質」欄に記載済み。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md`、sha256 5033273b…)
> C1について、以下を検証する。1. 必要な背景Factを正しく追加するか。2. 不必要なFactを追加しないか。3. 中心Storyline・エンターテインメント性を維持するか。4. 選定した背景Factが既存のWriter入力経路に正しく反映されるか。5. 記事として実際に理解しやすくなるか。6. 誤帰属・根拠のない因果関係・過剰な網羅化が生じないか。
> 既存のB3下限2 Factと、今回の補完候補を混同しない。検証はDEV／Trial環境に限定し、既存ProductionのPrompt・schema・producer・Writer経路を無断で変更しない。
> ### Trial Closeout - 核心機能の成功と記事品質維持を確認できた場合：`VALIDATED`。Production採用は未承認。- 失敗した場合：原因を分析し、承認範囲・予算内で合理的な修正と再検証を実施する。- 改善見込みがない場合：`REJECTED` を提案。- 新仕様や品質基準の変更が必要な場合：`USER_DECISION_REQUIRED`。単に「追加しなかった」という結果を、背景補完能力の成功として扱わない。
> ## 4. (抜粋) C1によって実際に背景Factを追加できた場合は、そのFactが後続の決定論的producerを通じてWriterに正しく渡り、本文で使われることまで検証する。必要なschema・producer変更が判明した場合は、実装を独断で進めず、変更範囲・QCD・正式採用の必要性を報告すること。
> **最終報告は次の順序とする。** 1. Researchで3点の背景情報が欠落した根本原因（証拠付き）。2. 原因別の是正内容と再発防止の効果。3. C1の陽性対照Trial結果（採用FactのBefore／After）。4. 記事品質・ストーリー性の比較。5. QCD（実費、追加工程の時間、量産単価への影響）。6. Production配線・SSOT・Gitの状態。7. 残るユーザー判断事項と推奨案。

## 作業
W1. R1実走: `er083_c1_positive_control_01_run.py`で12セル({baseline,C1}×{PC1,PC2,NC1}×sample2)を実行(`--paid-run-approved-by-fable`付与、`--budget-jpy 125`)。各セルの採用ID・core/supplement区分・B3理由・`rules_sha256`不変・費用を記録。eval(`_eval.py`)で項目1・2・4(機械)を判定。
W2. R2(条件成立時のみ): C1が期待coreを採用したセル(PC1/PC2)について、baselineとC1の各1本(最大4本)をWriter probe(`er083_b3_background_fact_trial_01_writer_probe.py`再利用、`--budget-jpy 55`)で生成。producer→Writer入力への採用Fact到達を決定論的に追跡(契約V5、`rules_sha256` 525f2309…一致)し、本文で当該Factが使われたか(文単位の対応)を記録。
W3. 盲検rubric(項目3・5・6): 別process・記事ラベル隠蔽(前Trial `R1_BLIND_PACK_01.md`方式)で採点、採点者の出力をそのまま保存。
W4. 失敗時の扱い(ユーザー§3 Closeout): 陽性で追加0なら、原因分析(C1 note文言の読まれ方・Ledger内Factの記述形・B3の除外理由)を行い、**承認範囲内で合理的な修正があるか**を検討(C1 note文言の修正はTrial専用noteの改訂=範囲内。Production Prompt/schemaの変更=範囲外)。修正案がある場合、Cap残で再検証1回まで(sample 2、同じ陽性Ledger)。改善見込みなし→REJECTED案。
W5. Closeout `C1_POSITIVE_CONTROL_CLOSEOUT_01.md`: セル別結果表(Before/After採用ID、期待core採用可否、extras、NONDISCRIMINATING判定)、Writer到達・本文使用の追跡、盲検rubric結果、判定基準の評価と候補Status、Research原因(委任_01)との関係(「Ledgerに主体Factがあれば通常B3でも拾うか」の所見)、Production採用時に必要なschema/producer変更の有無、費用。
W6. SSOT: (a)OPEN-425: Research原因結論(委任_01の文案)+C1 Trial結果+候補Status。(b)OPEN-423: 「陽性対照Trial結果=<…>」追記。(c)**OPEN-424: Fable最終ラベル=REJECTED(2026-10-20、Trial Closeout承認、Production採用提案なし)**を追記。(d)**OPEN-416**: 「攻撃主体未特定」はLedgerの限界であって出典側には国連特使の帰属(Ansar Allah)が存在した旨へ更新(委任_01根拠)。(e)DECISION_LOG末尾: Research原因結論(委任_01文案)+C1 Trial結果+Fable決定(実走承認・Cap・Opus再レビュー不要)+PLW REJECTED確定。(f)REGISTER: #125行末にResearch原因・C1結果を追記、#124行末に「REJECTED確定(Fable 2026-10-20)」、#112(中東記事)行末に「Research原因判明により、音声化/再Research判断はResearch新観点の採否後へ(推奨)」。(g)REPORT_LEDGER更新。
W7. ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_POSITIVE_CONTROL_DESIGN_01.md`(全体)、`c1_posctrl_matrix_01.json`、`C1_LEDGER_CANDIDATE_SCAN_01.md`: Grep `HF-006|期待|NONDISCRIMINATING`
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/RESEARCH_GAP_ROOT_CAUSE_01.md`: §5・§6(Grep `^## 5|^## 6`)
- `docs/pm/RESULT_PACKET_XRG1.md`・`docs/pm/RESULT_PACKET_XRG2.md`(全体、短い)
- `er083_c1_positive_control_01_{run,eval,test_01}.py`(全体)、`er083_b3_background_fact_trial_01_writer_probe.py`: Grep `def |argparse|budget`
- `er083_output/c1_positive_control_01/test_ledgers/test_ledger_mey_positive_01.json`(全体)
- `docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/R1_BLIND_PACK_01.md`:1-60、`R1_BLIND_EVAL_01.md`:1-40(盲検手順)
- `OPEN_ITEMS.md`: Grep `^- OPEN-(416|423|424|425)`→該当行のみ
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #(112|124|125)\(`→該当行のみ

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: 上記4行の行末追記。`DECISION_LOG.md`: 末尾。`docs/pm/USER_DECISION_REGISTER_01.md`: 上記3行の行末。`docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-X-RESEARCH-BACKGROUND|FAMILY-Z-AZURE-PHRASELIST`→更新。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ4行。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(index走査) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_03.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_委任_03.md_check.json`
- test(実走前): `.venv\Scripts\python.exe -m pytest er083_c1_positive_control_01_test_01.py -q`
- R1 dry-run→実走: `.venv\Scripts\python.exe er083_c1_positive_control_01_run.py --design docs\research\FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01\c1_posctrl_matrix_01.json --out er083_output\c1_positive_control_01 --budget-jpy 125 --dry-run` → `--dry-run`を外し`--paid-run-approved-by-fable "Fable 2026-10-20 委任_03 Cap180(R1 125/R2 55)"`を付けて実走(引数名は実装に合わせる)
- eval: `.venv\Scripts\python.exe er083_c1_positive_control_01_eval.py --out er083_output\c1_positive_control_01 --report docs\research\FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01\C1_POSCTRL_R1_EVAL_01.md`
- R2: `.venv\Scripts\python.exe er083_b3_background_fact_trial_01_writer_probe.py --cell <cell_id> --out er083_output\c1_positive_control_01\writer --budget-jpy 55`(セルごと、実引数を記録)
- 費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
W6のとおり(実値で埋める。候補Statusは「eval機械判定=<X>(Fable最終ラベル待ち)」)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: R1結果(json/md、cost log)+eval。msg: `FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_03: C1陽性対照Trial R1(12 call、PC1/PC2/NC1、実費JPY<v>)+機械判定`
- commit 2: R2 Writer probe+盲検rubric+Closeout。msg: `… 委任_03: R2 Writer到達検証<n>本+盲検rubric+Closeout(eval判定=<X>)`
- commit 3: SSOT。msg: `… 委任_03: SSOT(OPEN-425/423/424 REJECTED確定/416更新、DECISION_LOG、REGISTER #125/#124/#112、REPORT_LEDGER)`
- trailer: `Delegation: FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/委任_03`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRG3.md`: (1)T-0 (2)R1セル別結果表(Before/After採用ID・期待core採用・extras・NONDISCRIMINATING) (3)R2 Writer到達・本文使用の追跡結果 (4)盲検rubric結果 (5)判定基準評価と候補Status、失敗時の原因分析・修正・再検証の有無 (6)Research原因との関係の所見 (7)Production採用時に必要なschema/producer変更の有無 (8)費用(R1/R2別、本委任実費、案件合算、当日累計)(9)SSOT差分(ファイル:行) (10)Git (11)判断候補(あれば、ラベル無し) (12)再開の有無と開示 (13)一覧外Read理由。判定整合行1行。