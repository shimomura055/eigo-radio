## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_11)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Step 7再ループの実装フェーズ(**¥0のみ**、有料APIなし)。Opus#14レビュー全文の保存、Fable評価(採用/不採用/修正採用)の逐語記録、採用設計の実装(Trial runner)、反実仮想replay・強制経路fixture・負例・許可リスト外STAGE4=0の¥0確認、第二段階案の¥0集計。有料の限定確認・rep30は次の委任_12で行う。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: `IN_PROGRESS`。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- 禁止事項: Production正式path(`er003*`/`er009*`/`er010*`/`er012*`/`er019*`)変更禁止、編集は`er052_open233_*`と文書のみ。Checker本体Prompt・Schema・判定規則・V7b・同義語表不変。Recheck/Rewrite promptは、Fable採用項目に明記した範囲(Rewrite promptへ「過去候補・元に戻す禁止」は**本委任では実装しない**)以外は変更しない。KPI緩和・Human Review温存を結論にしない。新しいretry loop・Human Reviewへ倒す新経路を作らない(許可リスト方式で出口を減らす方向のみ)。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。
- 費用上限: ¥0(有料API実行なし)。T-3: Capは暴走防止Guardrail。Phase累計¥695.39/¥900。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_11.md`。**委任文は全文そのまま保存(要旨化不可。下記Opus#14全文を含む)。** 一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
「AI1回で重大→問題なし」が可能な構造は禁止候補…
Opusから問題を指摘されたら、そのままユーザーへ投げず、採用/不採用/修正して採用をFable/Claudeで判断
レビュー後、必ずFable/Claudeで改善してからTrialへ進むこと。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
````

## 作業1: Opus#14全文保存(¥0)

`docs/pm/opus_l2_review_open233_kpi_recovery_02_14.md`へ、下記「Opus#14レビュー全文」を**一字一句そのまま**保存する(先頭にヘッダ: 管理ID、2026-10-04、条件B+ユーザー指示による必須レビュー、packet `opus_packet_open233_kpi_recovery_02_04.md`、追加Read約70k文字)。

## 作業2: Fable評価の逐語記録(¥0、設計書`docs/pm/design_open233_kpi_recovery_02.md` §18新設「Opus#14後のFable評価と採用設計」)

以下を逐語で記録する(変更しない):

**Fable評価(2026-10-04、Opus#14)**
1. **条件B判定「根本設計の問題」を採用。** 9件の原因型は「LLM自由文字列`claim_in_article`を各cycleの決定論処理が再解釈し、失敗するとSTAGE4へ直行する出口が6種類並ぶ」ことである。不変条件 **I-1(箇所=本文中の位置オブジェクトとして入口で確定し、以降は文字列でなく座標を引き継ぐ)** と **I-2(STAGE4は許可リスト方式: 「現行本文の具体的箇所についてStage 2(+S1)がBLOCKINGを確定し、その箇所の打ち手[ladder→T]が尽きた」場合のみ。形式・件数・位置特定不能はHuman Review理由にせず、funnel[Stage 2+S1]か次cycleへ)** を採用設計の中心に置く。
2. **I-1は最小実装で採用**: Rewrite後の範囲座標を`rewrite_records`等から置換ごとに写像し直して保持し、B′の「同一箇所」判定・A2の振動検出・D(ii)の写像に使う。claim文字列の再照合は新規claimにのみ行う。全面的なデータ構造再設計(全claimをオブジェクト化)は本Trialでは行わない(Production複雑化回避、QCD 6)。L2221の複数範囲skipは「`“A” and “B”`引用形式へ変換」で是正。
3. **I-2採用**: 許可reasonは `blocking_confirmed_unlocatable_after_cap` / `blocking_structural_after_ladder` / `post_T_new_blocking` / `api_failure`(parse失敗含む)の4種のみ。許可リスト外の理由でSTAGE4条件に達した場合は、記録(`stage4_allowlist_violation`)したうえでfunnel(判定だけのcycle)または次cycleへ戻す。既存の`same_claim_fact_id_reblocked`/`violation_span_unverified`/`ladder_exhausted`系/`cycle_limit_exhausted(_after_recheck)`は許可リスト外とし、出口としては廃止(記録名は保持してよい)。
4. **B′: 修正採用。** キーは位置のみ(fact_idは問わない。兄弟fact_idでも前Rewriteの出力箇所なら昇段)。同一箇所判定は「前cycleで置換した範囲(現行本文座標)と今回確定spanが1文字以上重なる」(逐語一致は使わない、H-4)。`escalated_to_paragraph`は「実際に`4_paragraph`を試行したか」(試行level一覧)へ是正。§0-4(「同じFactが別箇所に再登場したら段落Rewrite」の廃止)との関係: B′は「同じ箇所への前levelのRewrite結果が再びBLOCKING確定」という効果実証に基づく昇段で、§5-11「初期水準より上位への昇段を妨げない」のcycle横断適用と解釈し、衝突しないとFableが判断する。ユーザー原則の解釈であるため、Closeout報告の確認事項に記載する(実装は止めない)。
5. **A2(振動検出): 採用。** 箇所ごとの過去状態列(原文, c1後, c2後…)と候補を正規化(空白・引用符字形)後に完全一致で比較、範囲ごとに判定。一致したら候補を却下し同cycle内で上位levelへ(既存ladder内の判定)。
6. **A1(主体語残存チェック): 不採用**(誤検出2/3、不要Rewrite防止優先。B′で1cycle遅れで回収)。Rewrite promptへの「過去候補・元に戻す禁止」提示は後回し(本委任では実装しない)。
7. **D: 修正採用(H-1是正必須)。** (i)引用分割は決定論で採用。`VS_EXPLAIN_MAX_EN_WORDS`の緩和は「残りが閉じた語彙の位置語(headline/one_line等U-2要素)を含み、かつ逐語一致・隣接一致の棄却に当たらない場合」に限定。`explain_split`の棄却理由を`annotate_claim_span_identity`の記録に追加(実装前に、¥0)。(ii)写像はI-1最小実装+引用形式変換で対応。(iii)「Rewriteせず全文Recheck」は**位置の再取得に限定**し、**「書き換えられなかったBLOCKING」をcarry listに保持、listが空でない間は`normalize_recheck_outcome`がPASSを返さない**(決定論、H-1)。次cycleでも位置を取り直せなければ上限→G→`blocking_confirmed_unlocatable_after_cap`(正当な残余)。
8. **G: 修正採用。** 別機構にせず、`HARD_MAX_CYCLES`到達時のbreakを「判定だけのcycle」への遷移に変える(cycle==HARD_MAX_CYCLES+1ではループ冒頭のStage 2+S1のみ実行。Rewriteしない。same_claim/extra cycle判定を通らない)。Tier 0(因果floor)とS1を必ず適用(Stage 2単独で閉じない、H-2)。**本文が変わっていない箇所で過去にStage 2がBLOCKING確定したものはGで降格させない(BLOCKING固定)。** 非BLOCKINGなら既存`RESOLVED_REWRITE_THEN_DOWNGRADE`経路へ、BLOCKINGが残ればT。「上限はRewrite回数の上限であって判定回数の上限ではない」と定義。
9. **T(最終手段): 修正採用。** 構造要素以外の該当文を既存`0_delete`+全文Recheck 1回。1記事1回まで。T後のRecheckで新規BLOCKINGが出たら追わず`post_T_new_blocking`(許可リスト)。構造要素(タイトル等)でladder枯渇なら`blocking_structural_after_ladder`。
10. **S-4(同一本文の再判定)対策**: 「materialityを本文に紐づける」。キー=(箇所の正規化span集合, fact_id)。**BLOCKING固定は採用**(本文不変なら再判定でBLOCKINGを覆さない)。**一致した2-of-2非BLOCKINGの再利用はスイッチ`STAGE2_VERDICT_REUSE_NONBLOCKING`として実装し既定OFF**。rep30でONにする条件(事前固定): rep27〜29記録の¥0 replayで「再利用により抑制される判定のうち、正解ラベル上の重大が0件」。満たさなければOFFのまま。文単位への分解による再利用は禁止(span集合の完全一致のみ)。
11. **第二段階案(同fact_id兄弟箇所をcycle 1のStage 2 batchへ前倒し、Rewriteへは渡さない)**: ¥0集計①(後cycleの新規MAJORのうちcycle 1のfact_id列挙で覆えた割合)②(NORMAL群で列挙により増えるStage 2判定件数)を先に行う。採用条件(事前固定): ①>0。採用時はスイッチ`STAGE2_SIBLING_LOCATIONS_CYCLE1`としてrep30でON、不要Rewrite(NORMAL群)がrep29の5/14から増えた場合は不採用候補として記録。
12. **F1(品質regen条件)**: 本Trialでは**不採用(現状維持)**。記事品質規則の変更でProduction品質判定との整合が必要なため、Closeout報告の確認事項へ。
13. **H-3**: 「残るHuman Reviewは構造要素だけ」は撤回。残る正当な経路は ①上限後に位置特定できないBLOCKING ②T後の新規BLOCKING ③構造要素/削除すると記事の核が壊れる文(ladder枯渇) ④API失敗、の4つ(実例0件、経路としては存在)と設計書に明記。
14. **Trial設計**: Opus推奨の¥0準備(1)許可リスト関数(2)rep27〜29全instanceの反実仮想replay(3)強制経路fixture(4)H-1負例(5)explain_split棄却理由記録、を本委任で実施。事前基準に「許可リスト外STAGE4 0件」「G経路の降格は全件S1通過」「書き換えられていないBLOCKINGによるPASS 0件」を追加。その後、委任_12で限定確認(≈¥5)→rep30 1回(≈¥26〜30)。
15. **STOP条件照合**: KPI緩和・Human Review温存・Production/Checker変更の提案なし→非該当。Fable判断でTrial工程へ進む(Opusレビューをユーザー承認Gateにしない、CLAUDE.md/PM_GOVERNANCE 11-3)。ユーザー確認事項(Closeoutで提示): B′の§0-4解釈、F1、非BLOCKING再利用スイッチの扱い。

## 作業3: 実装(runner `er052_open233_self_recovery_flow_runner_01.py`、テスト`..._test_01.py`)

採用項目1〜11を実装する。全て`KPI_TRIAL_SWITCHES`で切替可能にし(既定ONの新スイッチ: `STAGE4_ALLOWLIST`, `LADDER_LOCATION_CARRY`(B′), `REWRITE_REVERT_GUARD`(A2), `SPAN_FALLBACK_CHAIN`(D), `JUDGE_ONLY_CYCLE_AFTER_CAP`(G), `LAST_RESORT_DELETE`(T), `MATERIALITY_BLOCKING_PIN`(S-4 BLOCKING固定); 既定OFF: `STAGE2_VERDICT_REUSE_NONBLOCKING`, `STAGE2_SIBLING_LOCATIONS_CYCLE1`)、`legacy`挙動はスイッチOFFで保持。
- 許可リスト関数: 1箇所に集約(`stage4_allowlist_decision(reason, context)`)。許可外は`stage4_allowlist_violation`を記録しfunnelへ。
- 強制経路fixture(¥0、記録済みLLM出力・stub): 上限到達→判定だけのcycle、振動、`\n`複数範囲、地の文入り引用、`multi_match`、位置特定不能のままのBLOCKING、T後の新規MAJOR、構造要素のladder枯渇、API失敗。各fixtureで終端reasonが許可リスト内か・funnelを通ったかを検証。
- 負例: H-1(書き換えられていないBLOCKINGがRecheck1回でPASSしない)、H-2(G経路でS1/Tier 0を飛ばした降格が起きない、BLOCKING固定が効く)、`rounding`(levels=[])のBLOCKINGがRewriteなしでPASSしないこと(Opusが推測した同型。コードで確認し結果を記録)。
- 反実仮想replay(¥0): rep27〜29の全instance(記録済みLLM出力)で新ロジックがどの終端へ行くかを決定論部分で追跡(LLM callが必要な分岐は「call必要」として件数化)。特にrep29のHuman Review 3件が許可リスト外出口で倒れないこと。出力 `er052_output/open233_kpi_recovery_02_offline_01/replay_counterfactual_rep27_29_01.{py,json,md}`。
- 第二段階案の¥0集計①②: `agg_sibling_locations_cycle1_01.{py,json}`。非BLOCKING再利用の¥0 replay(抑制される判定と正解ラベル照合): `replay_verdict_reuse_01.{py,json}`。結果に基づき、委任_12での両スイッチのON/OFFを事前基準どおり決めて記録。
- テスト: runner単体・er052回帰・全体回帰(基準11件以外新規なし)。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"` 0件。
- rep30スクリプト作成(未実行): `er052_open233_self_recovery_flow_runner_01_rep30_full_01.py`/`_rep30_agg_01.py`(rep29と同じ29 instance・38 run、KPI構成+新スイッチ、`--budget-jpy`既定28、集計にrep29/rep28/rep24/iter7比・許可リスト外STAGE4件数・G経路S1通過率・未書換BLOCKING PASS件数・スイッチ別発火を追加)。限定確認スクリプト `..._rep30a_limited_01.py`(`meta_run03_advanced` s1/s2、`safety_A4` s1、`--budget-jpy 7`)。

## 作業4: SSOT

`OPEN_ITEMS.md` KPI-RECOVERY-02行Statusに「委任_11: Opus#14保存、Fable評価(I-1最小/I-2許可リスト/B′修正/A2/D+H-1是正/G判定cycle/T/S-4固定 採用、A1・F1不採用)、実装・fixture・反実仮想replay【許可リスト外STAGE4 n件】、第二段階①=x%・再利用replay重大抑制y件→スイッチ判断。次: 委任_12 限定確認(≈¥5)→rep30(≈¥28)」。`docs/pm/REPORT_LEDGER.md`1行、REPORT §61、`docs/pm/ACTIVE_TASK.md`更新(addしない)。

## 事前指定Read/Grep

- runner: Opus#14の行番号(L311/5952, L1319, L1518, L2180-2233, L4374?/L374, L4630-4690, L4780-4985, L5472-5523, L5596-5608, L5995-6039, L6648, L6856/6869, L8040-8359, L8640-8749)→範囲Read。Grep `KPI_TRIAL_SWITCHES|apply_kpi_trial_switches|stage4_reason|normalize_recheck_outcome|rewrite_records|vs_apply_replacements|expand_same_fact_id_locations|vs_explain_split_resolve|annotate_claim_span_identity|HARD_MAX_CYCLES|RESOLVED_REWRITE_THEN_DOWNGRADE|0_delete|STRUCTURAL_ELEMENT_REWRITE`。構造変更箇所のみ全文Read許可(D-1)。
- 設計書§17、`docs/pm/rca_open233_rep29_stage4_01.md`、`docs/pm/opus_packet_open233_kpi_recovery_02_04.md`(c)。上位原則`docs/pm/design_open233_self_recovery_flow_01.md` §0-4・§5-11・§0-7。rep27/28/29出力(instance JSON、replay用)。rep29スクリプト(rep30の雛形)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。
T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_11.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_11.md_check.json
テスト: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py
¥0 replay/集計: 上記3スクリプトを作成→実行。
順序: T-0 → 作業1 → 2 → 3(実装→テスト→fixture→replay→集計→rep30/rep30aスクリプト作成) → 4 → commit/push → 報告。実装が10分制限や規模で分割が必要なら、commitを「設計・記録」「実装・テスト」「replay・集計・スクリプト」の最大3回に分けてよい。

## Git

明示add: Opus#14保存ファイル、設計書§18、runner、テスト、replay/集計スクリプト・出力、rep30/rep30aスクリプト、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、REPORT、委任ログ+check.json。メッセージ例: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Opus#14保存・Fable評価、STAGE4許可リスト化(I-2)・位置座標引継ぎ(I-1最小)・B′昇段・A2振動検出・D span fallback(H-1是正)・G判定専用cycle・T最終手段・BLOCKING固定を実装、強制経路fixture・反実仮想replay【許可リスト外STAGE4 n件】(委任_11、¥0)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(実装範囲、反実仮想replayでrep29の3件・rep27/28の6件がどの終端へ行くか、許可リスト外STAGE4件数、第二段階①②・再利用replayの結果とスイッチ判断)、(2)実装の要点(スイッチ別、行番号、legacy保持)、(3)fixture・負例(H-1/H-2/rounding)結果、(4)テスト結果、(5)replay・集計の表、(6)委任_12への費用概算(限定確認・rep30)と推奨`--budget-jpy`、(7)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(8)Fableへの論点(限定確認へ進めるか、Opus#14指摘で未対応のもの)。

## Opus#14レビュー全文(作業1で一字一句そのまま保存)

# Opus独立レビュー#14(条件B+ユーザー指示による必須レビュー)OPEN-233-KPI-RECOVERY-REDESIGN-02: location単位の履歴、上限後funnel、span fallback連鎖、ladder成功判定

## 結論

1. **条件Bの判定: 「個別バグが続いている」のではなく「根本設計の問題」と判定する(確認+解釈)。** 9件は症状としては別々ですが、原因の型は1つです。**LLMが書いた自由文字列(`claim_in_article`)を、各cycleで決定論の処理(照合、履歴一致、件数、出口)が再解釈している**こと、そして**その解釈に失敗するとHuman Review(STAGE4)へ直行する出口が、現在少なくとも6種類並んでいること**です(L8180 `same_claim`、L8225 `cycle_limit_exhausted`、L8346 `violation_span_unverified`、L8726 `cycle_limit_exhausted_after_recheck`、ladder_exhausted、unconfirmed等)。LLMの文字列形式は事実上いくらでも変わるので、出口の発火条件を1つずつ塞ぐ方式では終わりません。S-1〜S-3の指摘は正しいものの、まだ「出口ごとの補修」の形をしています。次の2点を**不変条件**として設計の中心に置くことを推奨します。
   - **(I-1)箇所は「本文中の位置(span)」というオブジェクトとして、入口で1回だけ確定し、以降は文字列ではなくそのオブジェクトを引き継ぐ**(S-2の強化。D(ii)とL2221の問題は、この不変条件の下では最初から発生しない)。
   - **(I-2)STAGE4は許可リスト方式にする**: 「現行本文の具体的な箇所について、Stage 2(+S1)がBLOCKINGを確定し、その箇所の打ち手(ladder→T)が尽きた」場合だけHuman Reviewへ進めてよい。それ以外の失敗(形式、件数、位置特定不能)はHuman Reviewの理由にせず、funnel(Stage 2+S1)か次cycleへ戻す。こうしておけば、rep30で未知の形式不整合が出ても、出口は1つの関数に集まります。
2. **推奨組合せの判定**: B′=修正して採用、A2=採用、A1=不採用、D=**修正して採用(Safety holeあり、後述H-1)**、G=修正して採用(独立の機構にせず、「判定だけを行うcycle」として既存ループへ組み込む)、T=修正して採用(1記事1回まで)。17-4の「残るのは構造要素だけ」は**言い過ぎ**です(後述H-3)。
3. **新しく指摘する構造S-4(Sonnet案に無い)**: **本文が変わっていない同じ箇所を、cycleごとに再判定している**。S1は「意見が割れたらBLOCKING」で安全側に倒す集約ですが、同じ文を何度も引き直すと、BLOCKINGが出る確率は単調に上がり、Stage 2+S1の費用も重なります。A4の費用37%とcycle 3のBLOCKINGは、これが一因と推測します。
4. **worst費用**: B′/D/Gは**A4のcycle数を減らしません**(A4のcycleを消費しているのはRewrite失敗ではなく、Stage 1の取りこぼしを毎回少しずつ見つけていく構造)。Gは上限到達時に+¥0.4〜0.5なので、worstは**むしろ悪化**します。Cap+¥3以内に収めるには、別の手(第二段階案、論点6)が必要です。

## 論点別判定

### 論点1 構造判定(条件B)【判定: 根本設計の問題。S-1〜S-3は妥当だが不足】
- **S-1(成功≠解消)**: 妥当です。ただし対策として、ladder内で毎回解消を確認する(追加call)ことはしないのが正解です。最終的にはcycle末の全文Recheckが解消を判定するので、S-1で閉じるべきなのは、決定論で¥0判定できる「明らかな非解消」(元の状態へ戻る振動=A2)と、「同じ箇所で同じlevelを繰り返す」こと(B′)だけで十分です。`no`→`little`のような表面だけの変更はRecheckに任せ、次cycleでB′により1段上げる。これで収束します。
- **S-2**: 「キーがclaimである」ことより根が深い問題です。**前段で得た位置情報を、文字列に戻して捨てている**(観点4への違反)。Rewriteした範囲とその置換後の文は`rewrite_records`に持っているのに、次cycleには`claim_in_article`の文字列として渡し、それを再照合しています(L2221、L6648の`\n`連結、L1319の類似度≥0.75)。
- **S-3**: 妥当です。ただし対策を「出口ごとのfunnel化」ではなく、I-2(許可リスト方式の出口)として実装することを推奨します。
- **S-4(追加)**: 上の結論3のとおりです。
- **残る未知の穴の候補(推測)**:
  (a)Recheckが本文に無い引用を作り出した(全断片が`fragment_not_in_article`、前Rewriteの範囲へも写像できない)。
  (b)`multi_match`(hookと本文に同じ文がある等)。現行は確定不能の扱い(L4802)。同じ文字列で同じ問題なら、全出現箇所を対象にできるはず。
  (c)T(削除)の後のRecheckが原文由来の新しいMAJORを出す(cycleが残っていない)。
  (d)最終cycleでのRecheckのAPI失敗、parse失敗。
  (e)`related_fact_id`が空のclaim(rep29a)。location単位にすれば影響は小さくなる。
  (f)`rounding`(levels=[]、Rewriteしない)のclaimをStage 2がBLOCKINGにした場合、Rewriteされないまま、Recheck1回でPASSしうる(H-1と同じ型。コードでは未確認、推測)。
  (g)同じcycle内で、先行claimの書き換えが後続claimの範囲を覆った結果のskip(`covered_by_earlier_rewrite_in_cycle`、L6856/6869)。後続のissueが実際には直っていない場合は、次cycleへ回る(費用が増える)。

### 論点2 G【修正して採用】
- **「AI1回で重大→問題なし」に抵触するか**: 次の条件付きで**抵触しない**と判断します。Recheckの出すMAJORは検出器の出力で、cycle 1のChecker MAJORと同じ位置づけです。各cycleの冒頭で、Recheck由来のMAJORは既にStage 2+S1を通っています(L8058〜8088、L8083-8084のコメント「毎cycle・Recheck由来にも同じ経路」)。Gは、上限到達時だけこの経路が飛ばされていた非対称(L8723-8727)を是正するもので、新しい降格経路ではありません。「重複であって新しい経路ではない」という整理は正しいです。
- **ただし条件があります**: (i)G経路でもTier 0(因果floor)とS1を**必ず**適用すること(`STAGE2_SECOND_OPINION`経路の再利用。Stage 2単独の非BLOCKINGで閉じない)。(ii)**本文が変わっていない箇所で、過去にStage 2がBLOCKINGと確定したものは、Gで降格させない**(BLOCKINGの固定、後述の「materialityは本文に紐づける」)。テキストが変わった箇所の降格は正当です。
- **実装の推奨(より単純な形)**: 別の機構を作らず、**L8724のbreakを「判定だけのcycle」への遷移に変える**。`cycle == HARD_MAX_CYCLES+1`ではループ冒頭のStage 2+S1(L8058〜8098)だけを実行し、`not blocking_claims`なら既存のL8131経路(`RESOLVED_REWRITE_THEN_DOWNGRADE`)へ、BLOCKINGが残ればTへ。「上限はRewriteの回数の上限であって、判定の回数の上限ではない」と定義すれば、§0-7とCapの考え方とも整合します。判定だけのcycleでは、L8147〜8227(same_claim、extra cycleの判定)を通らないように分岐すること。
- **「残ればHuman Reviewへ倒れるが、それは構造要素だけ」は本当か**: **本当ではありません**(H-3)。

### 論点3 D【修正して採用。現行案のままではSafety holeあり】
- **(iii)「Rewriteせず全文Recheck」はそのままでは禁止構造になる(確認)**: `normalize_recheck_outcome`はL2199で`_recheck_ok(recheck)`ならPASSを返します。prior issueが書き換えられたかどうかを見ていません。したがって、**Stage 2がBLOCKINGと確定した箇所を書き換えずに、Recheck1回の「解消/準拠」だけでPASSに至る**ことが可能になり、ユーザーの禁止構造そのものです。**是正**: 「書き換えられなかったBLOCKING」をcarry listに残し、そのlistが空でない間はPASSを禁止する(決定論)。(iii)の役割は「再判定」ではなく、「Recheckに現行本文の位置を言い直させる(位置の再取得)」に限定する。次cycleでもfact_idで位置を取り直せなければ、上限→G→BLOCKINGのまま位置特定不能となり、これが正当な残余です(H-3)。
- **(ii)の写像**: I-1を採用すれば不要になります。最低限の策としては、L2221で`\n`の複数範囲をskipせず`“A” and “B”`の引用形式へ変換すること。これでL4669の断片照合(接続詞だけの残り)が通ります。
- **(i)の引用分割**: 断片の抽出と一意照合は決定論で、十分です(既存の`vs_explain_split_resolve`、L4882〜)。ただし**s2では既存の分割は試行済みで、棄却されています**。棄却理由は記録から落ちています(後述)。残りの部分(`and, in the one-line summary, calls were handled by humans`)は10語あり、`VS_EXPLAIN_MAX_EN_WORDS=6`(L374)により`remainder_too_long`で棄却されたと推測します。**是正は「残りを一律に捨てる」ではなく、狭い緩和にすること**: 残りが閉じた語彙の位置語(headline/one_line。U-2でその要素が範囲へ追加される、L4950〜4958)を含み、かつ逐語一致・隣接一致の棄却(L4970〜4985。引用が不完全であることの兆候)に当たらない場合に限り、語数制限を外す。逐語一致・隣接一致の棄却は残す。
- **観測の穴(確認)**: `annotate_claim_span_identity`(L5603〜5606)は`explain_split`のkeyを記録に残しません。rep29 s2のJSON(`instances_s2/meta_run03_advanced.json` L1166〜1197)にも棄却理由がありません。実装の前に、この記録を追加すること(¥0)。

### 論点4 B′と§0-4/§5-11【修正して採用】
- **整合性**: §0-4が廃止したのは「**同じFactが別の箇所に再登場したら段落Rewrite**」です。B′は「**同じ箇所への前levelのRewrite結果**が再びBLOCKINGと確定した」という効果の実証に基づく昇段で、§5-11にある「初期水準より上位への昇段(guard失敗時)は妨げない」を、cycleをまたいで適用するものと解釈できます。衝突しないと判断します。ただし**fact_idによる判定を混ぜたとたんに、裏口から旧ルールが復活します**。キーは位置だけにすること(fact_idは問わない。s2のHC-006→HC-012のように、兄弟fact_idでも、前のRewriteの出力箇所なら昇段)。
- **「同一箇所」の判定**: 逐語一致ではなく、**前cycleで置換した範囲(現行本文での座標)と、今回確定したspanが1文字以上重なること**で判定する(置換のたびに座標を写像し直す。`vs_apply_replacements`の結果から決定論で得られる)。逐語一致だと、隣の文を足したclaim(A4のcycle 3)や部分的な再編集で同一性を見失います。
- **不要Rewrite**: 件数は増えません(既にBLOCKINGと確定した箇所だけが対象)。範囲は広がりますが、2度BLOCKINGと確定した箇所なので§0-3の比較でも正当です。NORMAL群は、初回のBLOCKINGで判定が決まるので影響しないと推測します。
- **簡素化の提案**: B′を入れると④までの昇段は最短でもcycle 3に達するので、`same_claim_fact_id_reblocked`(L8178〜8186)は**上限前にはほぼ発火しない出口**になります。**この出口を廃止し**、「④での再BLOCKING→T」に統合することを推奨します。出口が1つ減り、I-2の方針どおりになります。最低限、`escalated_to_paragraph`の記録をL8264のflagではなく、「実際に`4_paragraph`を試行したか」(`ladder_level_used`または試行したlevelの一覧)へ是正すること。
- **T(最終手段)は必要**: ただし (i)1記事1回まで、(ii)構造要素以外、(iii)削除後のRecheckで新しいBLOCKINGが出たら、それは追わずにSTAGE4にする(無限に後退しない)、という上限を明記すること。

### 論点5 A1/A2
- **A2【採用】**: 箇所ごとの過去の状態の列(原文, c1後, c2後…)と候補を、正規化(空白・引用符の字形)した上で完全一致で比べる。決定論です。範囲が複数ある場合は**範囲ごと**に比べること(一部の範囲だけが元に戻るケースを取りこぼさない)。誤検出がありうるのは「元の状態が実は正しかった」場合ですが、元の状態はStage 2がBLOCKINGと確定したから書き換えたものなので、戻すことを却下するのは原理的に正しいです。初回の誤った編集(`businesses`)は検出できませんが、B′+Recheckで1cycle遅れて回収されます。
- **A1【不採用】**: 誤検出が2/3(n=3)で、表に無い語も検出できません。A1の効果(cycle 1での昇段)は、B′によって1cycle遅れで得られます。費用差はA1の方が有利ですが、不要Rewriteの防止(QCDの優先順3)を優先します。任意の策として、Rewriteのpromptへ「この箇所の過去の候補(元に戻すことを禁止)」を渡す案があります(Checker本体の変更ではない)。これはA2の発火を減らすだけなので、後回しで構いません。

### 論点6 worst費用と第二段階案
- **B′/D/Gだけでは不足(推測、根拠あり)**: A4の3 cycleは、原文にあった新しいMAJORを順に発見していった結果です(新規MAJORの5件全てが原文由来)。B′はA4にほぼ無関係(17-2表)、Gは+¥0.4〜0.5です。
- **推奨する第二段階案(1つ)**: **「同じfact_idの兄弟箇所を、cycle 1のStage 2のbatchへだけ前倒しで入れる」**。既存の`expand_same_fact_id_locations`(L1518)の結果を、**Rewriteへではなく**cycle 1のStage 2(+S1)へ渡し、BLOCKINGと確定した箇所だけをRewriteする。Stage 2はinstance単位のbatch(§4-8/A9)なので、追加の費用は主にtokenで済みます。A4のHC-012(3箇所に分散)を1 cycleで処理でき、cycleを1つ減らせる見込みです(−¥1.1〜1.9)。**ただし(推測)**: HC-006のように、cycle 1で一度も出てこないfactには効きません。実装する前に、rep27〜29の記録で¥0の集計を行うこと: ①後のcycleで出た新規MAJORのうち、cycle 1のfact_idを列挙すれば覆えた割合、②NORMAL群で列挙により増えるStage 2の判定件数と、そのうちBLOCKINGになった件数(不要Rewriteの候補)。Checkerの全文2回は採用しないという指示に従っています。
- **S-4への対策(費用と判定の揺れ)**: 「materialityを本文に紐づける」。キー=(箇所の正規化span集合, fact_id)、本文が変わっていない限り再判定しない。BLOCKINGの固定(安全側、採用推奨)と、**一致した2-of-2の非BLOCKINGの再利用**(費用・Human Review側。ただし見逃しの再検出機会を1つ減らすので、**Fable判断**。採用する場合は、rep29の正解ラベルに照らした¥0 replayで「抑制されたラベル上の重大が0件」であることを条件にする)。A4の残余claimは隣の文を足したspan(「An AI called. That was…」)で、組合せになると因果のBLOCKINGが出たので、**文単位への分解による再利用は禁止**です(span集合の完全一致のみ)。
- **F1**: 品質regenの発火(+0.0083の微増)は閾値の問題です。A4では−¥0.4で、唯一の決定論的な節約手段ですが、品質規則の変更なのでFable/ユーザー判断です(17-2どおり)。

### 論点7 Trial設計
- **限定確認(≈¥5)→rep30(1回)という順序は妥当**です。ただし、rep30で上限到達や振動が起きるのは38 runs中1件程度で、**rep30でHuman Reviewが0件でも、経路が正しいことの証明にはなりません**。経路の保証は¥0で取ること。
- **事前に用意すべきもの(全て¥0)**:
  (1)**STAGE4の許可リスト関数**: 許可するreasonは`blocking_confirmed_unlocatable_after_cap`、`blocking_structural_after_ladder`、`post_T_new_blocking`、API失敗だけ。それ以外のreasonで発火したらassert失敗として記録し、funnelへ戻す。
  (2)**記録済みのLLM出力を使った反実仮想replay**: rep27〜29の全instanceについて、新しいロジックが記録上どの終端へ行くか。
  (3)**強制経路のfixture**: 上限到達、振動、`\n`の複数範囲、地の文入りの引用、`multi_match`、位置特定不能のままのBLOCKING、T後の新規MAJOR。
  (4)H-1の負例: 書き換えられていないBLOCKINGがRecheck1回でPASSしないこと。
  (5)`explain_split`の棄却理由の記録。
- **事前基準への追加**: 「許可リスト外のSTAGE4が0件」「G経路の降格は全件S1を通過している」「書き換えられていないBLOCKINGによるPASSが0件」の3つを追加すること。

## Safety hole

- **H-1(重大、確認)**: D(iii)をそのまま実装すると、Stage 2がBLOCKINGと確定した箇所を書き換えずに、Recheck1回でPASSできる(L2199)。carry listによるPASS禁止で塞ぐこと。同じ型が`rounding`のBLOCKINGにもありうる(推測。要確認)。
- **H-2(中)**: GでS1かTier 0を省くと、Stage 2単独で降格できてしまう。本文が変わっていない、過去にBLOCKINGと確定した箇所の降格(判定の揺れによる降格)も禁止すること。
- **H-3(中、誤った主張)**: 「残るHuman Reviewは構造要素だけ」は誤りです。少なくとも次の4つが残ります: ①上限後に位置を特定できないBLOCKING、②T後のRecheckで出た新規BLOCKING、③削除すると記事の核が壊れる文(唯一の根拠文)、④API失敗。実例は0件でも、経路としては存在すると明記すること。
- **H-4(低)**: B′の同一性を逐語一致で判定すると、昇段を取りこぼす(安全側への失敗で、費用が増えるだけ)。重なりで判定すること。

## 追加検討事項

- **12観点**: 新しいLLM処理はありません(第二段階案もbatchへの追加だけ)。非決定性は、S-4の対策をとれば減ります。過剰なRewriteはA1を不採用にすれば増えません。retryとの矛盾はありません(Gは判定だけのcycle、Tは1回まで)。
- **ladder内で局所的に解消を確認する(追加call)案は不採用**を推奨します(全文Recheckと重複し、費用が増える)。
- **`HARD_MAX_CYCLES=3`という回数による上限そのもの**は、費用の上限として維持してよいと考えます。問題は「発見でcycleを消費する」ことで、第二段階案で対処すべきです。

## STOP条件の該当有無(Opusから見た材料。最終の照合はFableが行う)

- KPIの緩和、Human Reviewの温存、Production・Checker本体の変更を提案していないので、非該当です。
- **Fableが判断すべき点**: (1)B′の§0-4解釈。Opusは「衝突しない」と判断しましたが、ユーザー原則の解釈なので、Fableがユーザー確認の要否を判断すること。(2)F1(品質規則)。(3)非BLOCKING判定の再利用(降格判定の扱いに関わる)。
- Production採用の可否について、Opusは判断しません。

## 追加で読んだファイルと概算文字数

- `docs/pm/opus_packet_open233_kpi_recovery_02_04.md`(全文、約14k)
- `er052_open233_self_recovery_flow_runner_01.py`: L405-444、L2180-2233、L3080-3098、L4630-4690、L4780-4985、L5472-5523、L5596-5608、L5995-6039、L8040-8359、L8640-8749(計約35k)
- `docs/pm/design_open233_self_recovery_flow_01.md`: §0(L219-296)、§5-11(L2376-2435)(約7k)
- `docs/pm/design_open233_kpi_recovery_02.md`: §17(L593-660)(約10k)
- `er052_output/open233_self_recovery_flow_runner_01_rep29/instances_s2/meta_run03_advanced.json`: L1150-1269とGrep(約5k)
- `docs/pm/rca_open233_rep29_stage4_01.md`: Grepのみ(約0.5k)
- 合計: 約70k文字

## 十分に答えられなかった点

- s2の`explain_split`の棄却理由は記録が無いため推測です(`remainder_too_long`)。
- `rounding`のBLOCKINGがRewriteされずにPASSする経路は、コードで未確認です。
- 第二段階案の効果は、¥0集計をしないと確定しません。
