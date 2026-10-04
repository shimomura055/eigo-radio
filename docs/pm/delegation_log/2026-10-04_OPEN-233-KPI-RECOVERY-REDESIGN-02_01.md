## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_01)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー指示(2026-10-04、`OPEN-233-KPI-RECOVERY-REDESIGN-02`)の逐語記録と、Step 1(B3重大→問題なし誤降格の**構造的**根本原因分析)、必須作業4の技術是正3件の実装(prior_issuesに現行本文を渡す/L6をTrial構成で有効化/NORMAL群2-of-2を既定OFF)、必須作業5(説明文混入型の残り4件の決定論的解決可能性の分析)、Step 2の設計案比較(後段Safety設計A/B、Stage 1 recall改善の低コスト案比較、強モデル限定利用の比較前提[価格の実行時確認])、Opus批判レビュー用packet作成。**有料Trialは行わない**(¥0: 既存Evidence・オフラインreplay・既存ログの再利用のみ。価格確認はAPI課金ではない)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。診断目的の内訳計測は可。KPIの分割・緩和で達成扱いにしない。
- QCD優先順位: 1.重大見逃し0 2.Human Review 0 3.不要Rewriteを増やさない 4.平均追加費用+¥2以内 5.非決定性・追加callを最小化 6.Production運用が複雑になりすぎない。Safetyを理由にHuman Reviewへ逃がさない。
- 到達上限Status: 本委任は設計・是正・packetまで(Trial Statusは変えない)。到達可能なTrial Statusは`VALIDATED`/`USER_DECISION_REQUIRED`のみ。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。Checker Prompt・Schema・判定方法は変更しない(prior_issuesに渡す**内容**の是正は不具合修正であり対象外)。
  - 「Checkerを全面2回回す」「KPIを分ける」を第一候補にしない。「Human Reviewを少数残す」「LLMだから0保証は難しい」を結論にしない。
  - 新しい有料Trialをしない(本委任は¥0)。費用概算は出す。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: ¥0(API課金なし。全体回帰等のテストは課金なし)。Phase累計¥584.07、上限¥900、残¥315.93。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_01.md`。**委任文は全文そのまま保存(末尾のユーザー指示全文を含む。要旨化不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用`.md`をWriteツールが拒否する場合は、Pythonスクリプトからファイル出力する。全体回帰は`PYTHONIOENCODING`を設定しないシェルで実行。

## ユーザー指示(原文)

本委任文末尾の「参考(逐語): ユーザー指示 OPEN-233-KPI-RECOVERY-REDESIGN-02 全文」を、`DECISION_LOG.md`末尾へ「OPEN-233-KPI-RECOVERY-REDESIGN-02(2026-10-04、ユーザー指示: KPI変更・緩和禁止、後段誤降格の根本原因分析と後段設計の見直し、Opusを改善工程に組み込むループ、技術是正3件、Human Review残存4件の解消検討、Stage 1 recallは第二段階、強モデル限定利用の比較、Status/Closeout条件)」の見出しで**一字一句そのまま**引用する(作業0)。続けて「Fableの受け止めと分担」(前回報告の「KPI分割」「Human Review少数残存」「LLMだから0保証困難」の方向は撤回。委任_01=記録・Step 1・技術是正3件・必須作業5分析・Step 2設計案・Stage 1 recall案・強モデル比較前提・Opus packet。Opus批判レビュー#11→Fable評価→委任_02=設計改善+実装+Step 5限定確認→委任_03=Step 6[Safety-critical群+29件]→未達なら再ループ)。

## 作業1: Step 1 — B3重大→問題なし誤降格の構造的根本原因分析(¥0)

出力: `docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`。「同じ入力を10回回したら10/10重大だった」で完了としない。今回の1回がシステム上なぜ成立したかを**構造**として説明する。

最低限確認すること(各項目に実データの逐語・行番号を付ける):
1. 後段(Stage 2)に渡った**実際の入力**(rep25 B3 s1のStage 2 prompt全文: 本文・Ledger・claim・rubric。instance JSON/call_logから復元。prompt sha256付き)。
2. Checkerから渡された指摘内容(issue・severity・flags・related_fact_id)と、**そのうちStage 2 promptに含まれていた情報/含まれていなかった情報**(Opus#10の観察: issue・`dev`フラグはStage 2に渡っていない — calibration 649〜671行で確認)。
3. Ledger(HF-007)/記事本文/context(In one line行、周辺文)。
4. 後段Prompt(V7b本文全文)と、materiality基準(BLOCKING/QUALITY/ACCEPTABLEの定義文)。特に「ACCEPTABLE=確認済みFactから自然に導ける描写・推論」の文言が、因果の付加(`so`)を「自然な推論」と読める余地を残していないか。
5. deterministic safety rule(floor 5フラグ、precheck、hook/disclosure_gap降格、既存2-of-2)との関係: `changed_causality`はfloor対象外、なぜ対象外になったか(過去決定のGrep: `changed_causality`、`FLOOR_FLAGS`の設計経緯)。
6. 過去9件の同経路流出(委任_67集計: B3 7件[R3''' 4/V5 2/V7b 1]、A2A3-0 2件[V5])の共通点: claim型(因果付加/主体断定)、Stage 2入力の構成(batch内の他claim数・位置)、basis、rewrite_hint、reasoning tokens、rubric版、cycle、Stage 1の経路(fresh/reuse/代替投入)。
7. 1回だけ誤判定した理由: 乱数的揺らぎか、Prompt・入力構造・判定権限の設計上の弱点か。reasoning tokens(306/262 vs 418〜893)の観察を全降格事例で集計し、「浅い推論の回に見落とす」仮説を既存ログで検証(¥0)。
8. なぜ「重大→軽微(QUALITY)」ではなく「重大→問題なし(ACCEPTABLE)」まで一気に落とせたのか(schema上、ACCEPTABLEに追加の要件がない/basis=none・hint空で通る/Checkerの重大判定を打ち消すためのEvidence要件がない)。
9. Checkerの重大判定を後段が打ち消すための**現在の条件**を一文で定式化し、妥当かを評価(現状: 「Stage 2が1回、任意のbasisで非BLOCKINGを返す」=無条件の解除権限)。
10. 結論: 構造上の欠陥の列挙(例: (a)判定役がCheckerの指摘を知らずに再発見を要求される、(b)解除にEvidence要件がない、(c)ACCEPTABLEに追加要件がない、(d)1回判定、(e)因果が決定論ガード外)。

## 作業2: 必須作業4 — 技術是正3件の実装(Trial側、不具合是正)

- 2-1 **prior_issuesに現行本文を渡す**: `build_prior_issues_instruction`相当のrunner側呼び出しで、`claim_in_article`に渡しているRewrite前のspan textを、**現行本文(Rewrite後)の該当文**(handoff解決済みの範囲が置換された後の文。carry-forwardで`collect_replaced_units`にある置換後文)へ置き換える。置換後文が特定できない場合(unresolvable等)は従来どおり元textを渡し、`prior_issue_text_source`(`current_text`/`original_text`)を記録。er003側は変更しない(runnerが渡す引数内容の是正)。Checker Promptの文面は不変であることをテストで固定(prompt templateのバイト不変)。
- 2-2 **L6のTrial構成での有効化**: rep23/24構成に`VS_SENTENCE_RESTORE=True`を加えた「KPI確認構成」を定義(定数`KPI_TRIAL_SWITCHES`等)。既定OFFは維持。
- 2-3 **NORMAL群2-of-2の既定OFF**: `apply_stage2_two_of_two`(NORMAL群)をスイッチ化(`STAGE2_NORMAL_TWO_OF_TWO`、既定OFF)。KPI確認構成ではOFF。既存テストは旧挙動をスイッチONで維持。
- テスト: 新規(2-1の置換・fallback・prompt不変、2-2構成、2-3 OFF既定)、runner単体・er052回帰・全体回帰(基準11件以外に新規なし)。

## 作業3: 必須作業5 — 説明文混入型の残り4件の解決可能性分析(¥0)

出力: 設計書`docs/pm/design_open233_kpi_recovery_02.md` §5。(d)型5件(`remainder_too_long`×3、`fragment_not_in_article`×1、U-2(1)で解ける`dangling_position`×1)について、各件ごとに: Checker `claim_in_article`逐語/`issue`/記事の該当箇所(section・heading・周辺文)/現在のP-strict-closedのどのガードで棄却されるか/**原文のどの情報を使えば一意に特定できるか**(section・heading・surrounding sentence・claim・Ledger `related_fact_id`のfact本文と記事文の逐語一致・current article structure)/Checker出力を変えずに後段だけで決定論的に解けるか/解ける場合の規則案と誤範囲リスク/本当に解けない場合はその理由(Evidence)。例: `remainder_too_long`は「引用断片が記事に一意に逐語一致し、説明文の残余が記事に逐語で存在しない(=説明であり本文でない)なら、引用断片を含む完結文(L6)を範囲とする」規則で解けるか、Opus#7の懸念(説明文が別箇所を指す)を`related_fact_id`のfact本文との照合で排除できるか、を検討。

## 作業4: Step 2 — 後段設計の見直し(設計案比較、実装しない)

設計書 §2〜§4。KPIを維持したまま後段Safetyを改善する案を比較。少なくとも:
- A-1 解除条件の見直し: 「AI1回で重大→問題なし」を禁止候補とし、(i)deterministic ruleで守れる部分(Ledger `related_fact_id`のfact本文に、claimの述語・接続(因果語`so/because/led to/as a result/therefore`、主体、数値、否定、比較、時期)の根拠が逐語で存在するかの決定論検査)、(ii)CheckerのEvidence(issue・flags・related_fact_id・Checkerの引用)を後段へ強く引き継ぐ方法(primingの懸念[Opus#10]に対し、「Checkerの指摘を仮説として示し、Ledger逐語引用で反証できた場合のみ解除」とする形。F5型。反証引用は決定論でLedger逐語照合)、(iii)「問題なし」まで落とす条件の厳格化(ACCEPTABLEには「Checker指摘の反証となるLedger逐語引用」+「claimの各要素がfactに根拠あり」を必須。満たさなければQUALITY止まりか、BLOCKING維持)、(iv)Major→MinorとMajor→No issueで解除条件を分ける(Minor=核心は保たれるが精度が落ちる: 反証不要だが「核心が保たれている」根拠引用必須/No issue=反証必須)、(v)LedgerとChecker根拠を利用した決定論的Guard(例: Checkerのissueが因果・主体・数値・否定・比較・時期のいずれかを名指しし、該当要素がfact本文に逐語で無い場合はAI解除不可=BLOCKING固定)、(vi)confidenceや明示Evidence不足時はMajor維持(schemaに`ledger_citation`必須、空・非逐語はBLOCKING)、(vii)2回一致(S1)を上記の補助として位置づけ(単独では不十分)。
- A-2 各案について: 過去9件+rep25の見逃しを閉じるか(¥0 replay: 該当事例の実データで決定論部分を評価、LLM部分は既存応答から推定)、不要Rewriteへの影響(rep24の正当な降格68件・既存ログ471件のうち、新条件で解除できなくなる件数を¥0で試算。QUALITY/ACCEPTABLE別)、Human Reviewへの影響(0のまま)、追加call・費用(+¥/記事)、非決定性、Production複雑度。
- B 不要Rewriteとの両立: 既存原則「英語学習者に記事の本質について重大な誤解を与えるものだけを止める」を維持。「全てMajor固定」は不採用。新条件で解除できなくなる正当な降格の件数と、その内訳(Rewriteしても害がない軽微修正か、記事品質を落とす不要Rewriteか)を仮ラベル。
- 推奨案(組み合わせ可)とその根拠。KPI 4つ(重大見逃し0/Human Review 0/+¥2/Cap+¥3)の見通しを数値で。

## 作業5: 必須作業6(第二段階)・強モデル限定利用の比較前提

設計書 §6〜§7(比較のみ、実装しない)。
- §6 Stage 1 recall改善の低コスト案比較: Checker Prompt/入力改善(Checker Prompt変更はユーザー決定で不可だが入力改善[Ledgerの提示順・Safety系factの強調]は候補)/deterministic pre-check(precheckの拡張: 因果語・主体・時期)/Safety系Factだけの安価な補助check/Stage 1がPASSした場合だけ限定的に再確認(合格直前検査、委任_49実測の再利用)/特定risk flagだけ再確認/既存Ledger構造の再利用/Stage 2・後段Evidenceの利用/その他。各案の費用・recall改善見込み(既存Evidence: 委任_49のDET-A/B/C、Stage 1 recall miss実例B2_hormuz/B3)。「Checker全面2回」は第一候補にしない。
- §7 強モデル限定利用: 重大判定の解除判断など危険度の高い局所だけ強モデルを使う比較Trialの設計(発火条件=解除候補のみ、発火率試算[rep24: MAJOR 102件中68件が解除候補→高すぎるため、A-1の決定論Guard後に残る件数で再試算]、Luna等の安価経路を基本)。**最新価格を実行時に確認**: リポジトリ内の価格表(Grep `price|pricing|per_1m|cost_per`、`er0*_cost*`、`docs/`)とモデルID(`Sol`/`Luna`相当のモデルIDをGrep `sol|luna|model_id|MODEL`で特定。委任ログ`2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01*`参照)を確認し、価格が実行時に取得できる仕組み(環境変数・設定ファイル)があるか記録。平均+¥2/Cap+¥3以内に収まる発火率の上限を逆算。最初から全面強モデル化しない。

## 作業6: Opus批判レビュー用packet

`docs/pm/opus_packet_open233_kpi_recovery_02_01.md`(雛形(a)〜(g)、(g)の独立レビューブロック逐語貼付、条件A、既存Opus#8/#10との関係)。(a)論点はユーザー指定: なぜ重大→問題なしが可能だったか/新設計がその穴を本当に閉じるか/不要Rewriteを増やさないか/Human Reviewへ逃げていないか/より単純・決定論的な方法がないか/既存Evidenceを再利用できないか/Sol等の強モデルが本当に必要か/cost・nondeterminism・retry loopを増やしすぎないか、に加えて必須作業5の4件の解法の妥当性。(b)RCAの要点・過去9件の表・¥0試算表・B3のStage 2入力逐語(prompt全文は長ければ要点+ファイル参照)。(c)runner/calibration行範囲(Grep確認列)。2〜3万字以内。

## 作業7: SSOT

- `OPEN_ITEMS.md`: 新行`OPEN-233-KPI-RECOVERY-REDESIGN-02`(親OPEN-233、Status「IN_PROGRESS(委任_01: RCA・技術是正3件・設計案・Opus packet完了、Opus#11待ち)」、KPI 4つ、Step 1〜7の進捗欄、費用)。OPEN-233行Statusの冒頭に「(2026-10-04)ユーザー指示`OPEN-233-KPI-RECOVERY-REDESIGN-02`により、前回のUSER_DECISION_REQUIRED 7項目のうち(1)(2)(3)(5)(7)は撤回・技術是正/再設計へ、(4)(6)は技術是正として処理。KPI変更なし。再設計中」を追記。
- `docs/pm/REPORT_LEDGER.md`に新行。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §51「KPI-RECOVERY-REDESIGN-02 委任_01」。`docs/pm/ACTIVE_TASK.md` 固定ヘッダを新管理IDへ(Status=IN_PROGRESS、KPI、禁止事項、Step進捗)(addしない)。`CURRENT_SPEC.md`は編集しない。

## 事前指定Read一覧

- rep25 `bgroup_B3` s1 instance JSON+call_log(Stage 2 promptの復元)。`er052_open233_self_recovery_stage2_calibration_01.py` 560〜700(Stage 2入力構成、V7b全文)。`er052_open233_self_recovery_stage2_production_01.py` Grep `basis|ACCEPTABLE|QUALITY|BLOCKING`(schema・定義)。
- runner: Grep `prior_issues|build_prior_issues_instruction|collect_replaced_units|apply_stage2_two_of_two|NORMAL_GROUP_INSTANCE_IDS|FLOOR_FLAGS|changed_causality|run_stage2|KPI|switches` → 該当範囲(全文Read禁止)。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `build_prior_issues_instruction` → 該当範囲のみ(read-only)。
- 委任_67/68の設計書・診断結果: `docs/pm/design_open233_stage2_safety_downgrade_01.md`(§1〜§3、§8)、`er052_output/open233_stage2_b3_misdowngrade_diag_01/{results_01,recount_01}.md`、`er052_output/open233_stage2_downgrade_q_measure_01/results_01.md`。
- 既存ログ: 過去9件の見逃し事例(委任_67集計の出典instance JSON)、rep24の降格68件(Pythonで走査)。
- (d)型5件: `er052_output/open233_span_restore_offline_01/results_01.md`(型分類表)、`u2_position_word_replay_01.md`、該当instance JSON。`docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`: P-strict-closedの4ガード(Grep `ガード`)。
- Opus: `docs/pm/opus_l2_review_open233_self_recovery_08.md`(F5の定義、priming)、`_10.md`(観点4、論点2・3)。
- 価格・モデルID: Grep(上記)。`docs/pm/delegation_log/2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01_result.md`。
- テンプレート: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`、`OPUS_INDEPENDENT_REVIEW_BLOCK.md`。
- SSOT: Grep `委任_68`、`OPEN-233-A1-PROD` → 追記位置のみ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_01.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

¥0 replay/試算: `er052_output/open233_kpi_recovery_02_offline_01/`配下にスクリプトを作って実行(例 `replay_guards_01.py`)。

順序: T-0 → 作業0 → 1 → 2(テスト含む) → 1回目commit/push → 3 → 4 → 5 → 6 → 7 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `DECISION_LOG.md`末尾、`OPEN_ITEMS.md`(新行+OPEN-233行冒頭)、`REPORT_LEDGER.md`新行、REPORT。
- 1回目commit: `DECISION_LOG.md`、RCA文書、runner、runnerテスト、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: ユーザー指示(KPI変更禁止・後段再設計・改善ループ)を逐語記録、B3重大→問題なし誤降格の構造的RCA、技術是正3件(prior_issuesに現行本文/L6のKPI構成/NORMAL群2-of-2既定OFF)を検証用runnerへ実装(Production未変更)(委任_01)`
- 2回目commit: 設計書、packet、¥0 replay出力、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、REPORT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: 後段Safety設計案比較(解除条件・決定論Guard・Evidence引継ぎ・Major→Minor/No issue分離)、説明文混入4件の解法分析、Stage 1 recall低コスト案・強モデル限定利用の比較前提、Opus#11向けpacketを作成(委任_01)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内、(2)RCAの構造的結論(欠陥の列挙、過去9件の共通点表、reasoning tokens仮説の検証結果)、(3)技術是正3件の実装箇所とテスト、(4)(d)型5件の解法分析(各件: 解ける/解けない、規則案、誤範囲リスク)、(5)設計案比較表と推奨案、¥0試算(見逃し閉鎖率・解除不可になる正当降格件数・費用)、(6)Stage 1 recall案比較表、強モデル価格・発火率試算、(7)packet文字数、(8)SSOT更新箇所、(9)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。

---

## 参考(逐語): ユーザー指示 OPEN-233-KPI-RECOVERY-REDESIGN-02 全文

Claude Code 指示
管理ID：OPEN-233-KPI-RECOVERY-REDESIGN-02
目的
OPEN-233について、KPIを変更・緩和せず、現行KPIを達成するために設計をやり直すこと。
前回報告で提示された、
- Safety KPIを「Checkerが検出したものだけ」に分割する
- Human Reviewを少数残す
- LLMだから0件保証は難しいとしてKPI側を調整する
という方向は不採用です。
ユーザーが求めているのは「将来1万記事作って永久に流出ゼロを数学的に保証せよ」ではありません。
少なくとも現在のTrial規模・Safetyケース・29件横断程度では、Human Review 0件・重大見逃し0件にならなければProduction候補として成立しない、という意味です。
現行KPI — 変更禁止
- Primary：USER_DECISION_REQUIRED / Human Review 0件
- Safety：重大Fact見逃し 0件
- Cost：平均追加コスト +¥2/記事以内
- Cost Cap：+¥3/記事以内
診断目的で内訳を分けて計測することはよいですが、KPIそのものを分割・緩和して達成扱いにしてはいけません。
KPI変更が必要だとユーザーへ相談してよいのは、合理的な改善案を十分に検討・試行し、それでも達成困難であるEvidenceが揃った場合だけです。
今回の最優先問題
今回B3では、
1. Checkerは重大違反を検出できていた
2. 後段の重大度判定が、それを「問題なし」へ降格
3. Rewriteされず流出
という動作が起きています。
したがって、現時点で第一に疑うべきなのはCheckerではなく後段判定の設計です。
「Checkerを2回回す」「KPIを分ける」へ直行してはいけません。
必須作業1：重大→問題なし誤降格の根本原因分析
まずB3について、なぜ後段が重大を問題なしへ落としたのかを詳細に分析してください。
最低限確認すること：
- 後段に渡った実際の入力
- Checkerから渡された指摘内容
- Ledger / 記事本文 / context
- 後段Prompt
- materiality基準
- deterministic safety ruleとの関係
- 過去9件の同経路流出との共通点
- 1回だけ誤判定した理由が単なる乱数的揺らぎなのか、Prompt・入力構造・判定権限に設計上の弱点があるのか
- なぜ「重大→軽微」ではなく「重大→問題なし」まで落とせたのか
- Checkerの重大判定を後段が打ち消すための現在の条件が妥当か
「同じ入力を10回回したら10/10重大だった」だけで原因分析完了としないこと。
今回1回実際に流出した以上、なぜその1回がシステム上成立したのかを構造として説明してください。
必須作業2：後段設計を見直す
原因分析後、KPIを維持したまま後段のSafetyを改善する設計案を比較してください。
少なくとも以下を検討対象に含めること。
A. Checkerが重大としたclaimを後段が解除できる条件の見直し
現在の「AI1回で重大→問題なし」が可能な構造は禁止候補です。
ただし単純に2回確認へする前に、
- deterministic ruleで守れる部分
- CheckerのEvidenceを後段へ強く引き継ぐ方法
- 「問題なし」まで落とす条件を厳格化する方法
- Major→MinorとMajor→No issueで解除条件を分ける方法
- LedgerとChecker根拠を利用した決定論的Guard
- confidenceや明示Evidence不足時はMajor維持
等、より筋のよい方法を比較してください。
B. 不要Rewriteとの両立
Safetyを上げるために、すべてMajor固定にして不要Rewriteを増やすだけでは不十分です。
既存原則：
「英語学習者に記事の本質について重大な誤解を与えるものだけを止める」
を維持してください。
必須作業3：Opusを「レビューして終わる道具」にしない
今回、Opusレビュー自体は入っています。
問題は、
設計 → Opusレビュー → ユーザー報告
で止まっていることです。
今後は以下の改善ループを必須とします。
原因分析
→ 設計案作成
→ Opus批判レビュー
→ Fable / Claudeが指摘を評価
→ KPI内で直せるものは自律的に設計改善
→ 限定Trial
→ KPI確認
→ 未達なら再設計
→ 必要なら再度Opusレビュー
→ 本当に判断が必要な場合だけユーザーへ
Opusレビューは報告材料ではなく改善工程の一部です。
Opusから問題を指摘されたら、そのままユーザーへ投げず、
- 採用
- 不採用
- 修正して採用
をFable/Claudeで判断し、Guardrail内で改善してください。
必須作業4：今回すでに判明している技術是正
以下は新しいProduct判断としてユーザーへ戻さず、技術是正として処理してください。
1. Rewrite前の古い文章をCheckerへ渡していた問題
prior_issuesには現在のRewrite後本文を渡すこと。
これは仕様判断ではなく明確な不具合是正です。
2. 不完全spanの復元
Checkerの返却範囲が、
- 途中から始まる
- ...で省略される
- 1〜数語の余分な語を含む
場合でも、
記事内で逐語的な手掛かりから対象の完結文を一意に特定できるなら、その完結文へ復元する。
類似度推測で無理に選ばないこと。
複数候補になる場合は別途技術的に解消可能か検討する。
既知29件のHuman Review 2件はこの処理で0件にできる見込みなので、実flowで確認してください。
3. Trial専用NORMAL群2-of-2
現在の評価を見かけ上改善している可能性があるため、既定OFFで再測定すること。
Productionに存在しないTrial補助でKPI達成を演出してはいけません。
必須作業5：Human Review残存4件も放置しない
報告には、過去の説明文混入型5件のうち、
- 1件は決定論的に解決可能
- 4件は現時点で未解決
とあります。
Primary KPIはHuman Review 0件です。
したがって、
「4件は現時点では自動解決できない」

で終わらせないこと。
まず、
- なぜ現在の後段ガードでは解けないのか
- 原文のどの情報を使えば特定できるか
- section / heading / surrounding sentence / claim / Ledger / current article structureを使えないか
- Checker出力を変えず後段だけで解決できないか
- 決定論的処理が本当に不可能か
を検討してください。
それでも本当に解けない場合のみ、Evidence付きでSTOPしてください。
必須作業6：Stage 1 Checker見逃しは第二段階として対策
B3今回流出の直接原因は後段なので、まずそこを直してください。
その後、Stage 1 Checker自身のrecall不足を別途改善します。
単純なChecker全面2回実行は第一候補にしないこと。
コストをほぼ倍増させるため筋が悪いです。
まず以下を比較してください。
- Checker Prompt / 入力改善
- deterministic pre-check
- Safety系Factだけの安価な補助check
- Stage 1がPASSした場合だけ限定的に再確認
- 特定risk flagだけ再確認
- 既存Ledger構造の再利用
- Stage 2/後段Evidenceの利用
- その他、より低コストなrecall改善方法
強いモデルの限定利用も検討すること
後段設計を改善しても重大誤降格が残る場合には、
全面的なモデル置換ではなく、重大判定の解除判断など危険度の高い局所だけ、より強いモデルを使う比較Trial
を検討してください。
候補としてSolの限定利用も比較対象に含めること。
ただし、
- 最新価格を実行時に確認
- 発火率を測る
- 平均+¥2/記事、Cap+¥3/記事以内
- Luna等の安価な通常経路を基本とし、必要ケースだけ強モデル
を前提とすること。
最初から全面Sol化しない。
QCD上の優先順位
1. 重大見逃し0
2. Human Review 0
3. 不要Rewriteを増やさない
4. 平均追加費用+¥2以内
5. 非決定性・追加callを最小化
6. Production運用が複雑になりすぎない
Safetyを理由にHuman Reviewへ逃がさないこと。
Human Reviewゼロ自体がKPIです。
Trialの進め方
いきなり次の10本Trialへ行かないでください。
まず今回の既知問題を閉じます。
Step 1
B3重大誤降格の根本原因分析。
Step 2
改善案比較＋Opusレビュー。
Step 3
Fable/Claudeでレビュー内容を咀嚼し設計改善。
Step 4
必要な技術是正をTrial側へ実装。
Step 5
B3/A2A3等の既知caseで限定確認。
Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
費用
現在Phase累計：
¥584.07 / ¥900
残：
¥315.93
まず原因分析・既存Evidence再利用・オフラインreplayを優先してください。
新しいAPI Trialを行う前に費用概算を出し、既存予算内で最小限に実施すること。
現在Status
OPEN-233はまだProduction採用判断の段階ではありません。
今回の作業はTrial改善継続です。
今回到達してよいStatus：
- VALIDATED
- USER_DECISION_REQUIRED
のみ。
APPROVED_FOR_PRODUCTION / PRODUCTION_WIREDへ勝手に進まないこと。
既存の個別APPROVED項目のStatusも勝手に変更しない。
USER_DECISION_REQUIREDにしてよい条件
以下の場合のみSTOPしてユーザーへ上げてください。
- Productの価値判断が必要
- 現行KPIを守る合理的な技術案を十分試したが、Evidence上達成困難
- +¥3/記事Cap超過が不可避
- Safetyを緩和しなければ解決できない
- Production正式採用判断が必要
- 既存正式仕様と矛盾し、どちらを優先するかユーザー判断が必要
以下はUSER_DECISION_REQUIREDではありません。
- 実装バグ
- 古い本文を渡していた
- Trial補助が評価を歪めていた
- Promptや入力設計の改善余地がある
- 後段の判定ロジックにSafety holeがある
- Opusが改善案を出した
- 「LLMなので絶対保証は難しい」
- 「件数が少ないのでHuman Reviewでもよい」
Opusレビュー必須
今回の後段Safety設計変更は処理フローに関わるため、実装前にOpusレビューを入れること。
レビューでは特に、
- なぜ重大→問題なしが可能だったか
- 新設計がその穴を本当に閉じるか
- 不要Rewriteを増やさないか
- Human Reviewへ逃げていないか
- より単純・決定論的な方法がないか
- 既存Evidenceを再利用できないか
- Sol等の強モデルが本当に必要か
- cost / nondeterminism / retry loopを増やしすぎないか
を批判的に確認すること。
レビュー後、必ずFable/Claudeで改善してからTrialへ進むこと。
Productionとの区別
今回Production正式pathは変更禁止。
Trial成功だけでProduction採用扱いにしない。
後続のProduction採用時には改めて、
- initial path
- retry
- fallback
- regeneration
- runtime evidence
- actual model/routing
- regression/integration test
- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Git反映
- Dangling Reference
まで確認が必要。
Closeout
Trial終了時に必ず、
- REJECTED
- VALIDATED
- USER_DECISION_REQUIRED
のいずれかへ分類すること。
加えて、
- Human Review件数
- 重大見逃し件数
- 不要Rewrite
- 平均追加cost
- worst cost
- どのモデルをどの条件で使ったか
- Opusレビュー指摘と、それをどう改善したか
- 未解決事項
- 未処理USER_DECISION_REQUIRED
- APPROVEDだが未配線の既存項目
- 未報告Trial有無
- Dangling Reference
を確認すること。
「設計した→レビューした→報告した」で終わらない。
KPIを満たすまで、Guardrail内で自分たちで改善ループを回すこと。
