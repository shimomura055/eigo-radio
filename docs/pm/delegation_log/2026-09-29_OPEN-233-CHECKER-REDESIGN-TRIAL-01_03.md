管理ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01(委任_03: Step 2 診断実行+V4-A/V4-C 実装+Trial 2 実行+分析)
日付: 2026-09-29。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提(必ず最初に読む)
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節(禁止事項)。
- 直前委任の成果: docs/pm/RESULT_PACKET_C233B.md、OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md §9(Trial 1)、docs/pm/design_open233_checker_redesign_trial_01.md §2-補/§3-補(V4 案)、er051_open233_checker_trial_01_run.py、er051_open233_checker_trial_variant_01.py、er051_output/open233_checker_trial_01/trial_01/。
- ユーザー更新判断 1〜15(2026-09-29)は DECISION_LOG.md の直近エントリ(委任_02 で記録)を参照。要点: 総予算 ¥400、Trial→分析→改善→再 Trial を繰り返す、QUALITY=通過前提、不要 BLOCK 率目標 ≤25%(baseline 75%)、Family X 限定 Trial variant、gpt-6-luna のみ、Production Prompt/schema/Validator・gold は変更禁止、Trial/DEV 専用の Prompt/schema/rule/fixture 追加は都度確認不要。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233C.md / docs/pm/RESULT_PACKET_C233C.md を新規作成(commit 禁止、既存 *_C233A/B は削除・移動しない)。

## 1. Fable 判定(Trial 1 に対する差し戻し・方針)
- (1) Phase A §4 の「Step1 で Safety 100% 未達の variant は Step2/3 を実行しない」は、**受入判定上のルール**としては維持するが、**診断目的の Step 2 実行を妨げない**と改める(設計書へ追記)。理由: 最重要目標は Productivity(ユーザー判断 4)であり、post-hoc 層のみでは B 群 75% が不変と判明した以上、Prompt/schema variant の B 群実測なしに原因切り分けは不可能。
- (2) V4-A(Ledger の差分ブロックへの changed_actor/unsupported_new_claim 境界明確化)は実装・実行する。**fixture 固有の文言にしない**こと: 「Ledger の主体(行為者・被行為者・発言者)が別の主体に置き換わっている場合は、それが新規主張を含んでいても changed_actor を true にする(複数 category の同時 true を許容する)」という一般的な category 境界の記述にする。changed_number/negation/comparison についても同じ「同時 true 許容」原則を一文で明記する(ただし重大群 12 fixture を再実行して副作用がないことを確認する)。
- (3) V4-B(unsupported_new_claim+MINOR の昇格拡張)は **本委任では実装・実行しない**。Safety/Productivity トレードオフに該当し、Step 2 データが揃った後に Fable が Opus L2 へ回す。
- (4) V4-C(Trial 1 未昇格 3 件を negative regression fixture として freeze)は実装する(er051 の mock test に追加し、「LLM が changed_actor=false・unsupported_new_claim=true・MINOR を返したときに V1 ルールが昇格しない」ことを固定=将来ルール拡張時の影響検出用。gold は BLOCKING のままで「現行ルールでは未昇格」という事実を固定する fixture であることをコメントに明記)。
- (5) 本委任の Guardrail: ¥50(総枠 ¥400、累計 ¥7.2882、残 ¥392.7118)。

## 2. 実行内容(順番厳守)
### 2-1. Step 2 診断実行(V2/V3、各 5 fixture=10 call)
- 境界群 5 fixture(B1/B2_hormuz/B3/B4/Meta_run03_standard)を V2・V3 で各 1 回実行。出力先 er051_output/open233_checker_trial_01/trial_01_step2_diag/。
- 集計: 不要 BLOCK 率(B1/B2/B3/B4 中 BLOCKING 数/4)、Meta_run03_standard の検出可否(negative control)、schema variant 出力(qualifier_present/qualifier_text/ledger_field_basis/observation_consistent/matched_notes_id)。
- **B 群で BLOCKING のまま残った各件について原因分類(a. Prompt 判定基準 b. schema 情報不足 c. deterministic rule d. context handling/notes_for_writer e. gold の曖昧さ)を 1 件ずつ**。claim 本文、category flag、origin、severity、LLM 理由文、matched_notes_id、observation_consistent を表にする。B2_hormuz(gold=QUALITY)が BLOCKING のままなら、Prompt 側で QUALITY を選ばなかった理由文を必ず引用する。
### 2-2. V4-A/V4-C 実装
- er051_open233_checker_trial_variant_01.py に V4-A(V2 の Prompt 差分ブロック+境界明確化文、schema variant・post-hoc v2 は V2 と同一)を追加。差分ブロックの sha256 を設計書に記録。
- V4-C を er051_open233_checker_trial_variant_01_test_01.py に追加。python -m unittest で全 PASS。
### 2-3. Trial 2(V4-A のみ)
- Step 1: 重大群 12 fixture(12 call)+changed_actor n=5(5 call)。Safety 100%・changed_actor 5/5 が受入。
- Step 2: 境界群 5 fixture(5 call)。V2/V3 診断結果と比較し、V4-A の境界明確化が B 群 BLOCKING を増やしていないか(副作用)を確認。
- Step 3: Step 1・2 の結果が V2/V3 を下回らない場合のみ、V4-A で Hormuz run_03 4 fixture × n=5(20 call)を実行し Stability(判定一致率、V0 90% と比較)と QCD を計測。V4-A が Safety 未達なら Step 3 は最良 variant(V2)で実行してよい(診断目的、明記)。
- 出力先 er051_output/open233_checker_trial_01/trial_02/。
### 2-4. 想定 call 数・費用(実行前に ACTIVE_TASK_C233C.md へ記録)
Step 2 診断 10+Trial 2 Step1 17+Step2 5+Step3 20=最大 52 call。Trial 1 実測(34 call ¥7.29≈¥0.21/call)から想定 ¥11〜13。retry 上限 fixture あたり 2 回。モデル gpt-6-luna・reasoning="high"、Contract 非経由。費用は usage 実測 token × 公式単価(In $0.10/Cached $0.01/Out $0.50 per 1M)× ¥156.88。API key は環境変数のみ、表示/log/commit/REPORT 禁止。Production ファイル(er003_*/er006_*/er012_*/er019_*)・Master Store は変更しない。

## 3. 分析(本委任のスコープ)
- variant 別総括表: V0(GPT-6 Trial 実測)/V1/V2/V3/V4-A × Safety 重大群/changed_actor n=5/不要 BLOCK 率/Meta negative control/Stability/cost per call/latency。
- B 群残存 BLOCKING の原因分類(§2-1)に基づき、**≤25% 達成のために何を変えねばならないか**を、Prompt/schema/deterministic rule/context handling の別に具体化(V5 案。実装・実行はしない)。特に (i) B1(一般常識ブリッジ文の unsupported_new_claim)を QUALITY/ACCEPTABLE に落とすための判定基準案、(ii) B2(gold=QUALITY)が QUALITY にならない原因、(iii) B3/B4 が通過に必要か(gold 曖昧性リスクとして、通過させると Safety 上不当かどうかの一次分析)を分けて書く。
- Opus L2 に問うべき論点を 3〜5 個に絞って提案(V4-B のトレードオフ、B1/B2 の判定基準、B3/B4 の gold 曖昧性、Family 横断リスク、fail-closed 思想との整合 等)。
- ユーザー判断 11(gold 変更・BLOCKING 大幅緩和・fail-closed 撤廃・Production 変更等)に触れる事項の有無を明記。

## 4. 事後確認・記録・Git
- mock test 全 PASS、Production 定数 3 件 sha256 不変、git diff --stat で Production ファイル無変更を確認し REPORT に記載。
- REPORT §10「Step 2 診断+Trial 2(委任_03)」追記(実行条件、結果表、原因分類表、V5 案、Opus 論点、費用: 今回/累計/残、Status)。設計書へ §1 Fable 判定・V4-A 差分・V4-C・Trial 2 結果・V5 案を追記。
- SSOT(最小限、1 agent のみ): OPEN_ITEMS.md の OPEN-233 行に Trial 2 Status/累計費用へのポインタ追記。DECISION_LOG.md には Fable 判定 (1)〜(4) を 1 エントリ追加。CURRENT_SPEC.md 不変。REPORT_LEDGER は文案のみ。
- delegation_log: docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_03.md 作成+check_delegation_prompt.py 実行(FAIL 既知・non-blocking)。
- commit: パス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ(reset/amend/rebase/force push/stash/rm/git clean/削除/移動 禁止)。Trial 出力 json は API key 非含有を確認して commit。
- 報告(RESULT_PACKET_C233C.md と handback): 【現在の状態】【Step 2 診断結果(V2/V3)】【B 群残存 BLOCKING 原因分類表】【V4-A 差分と Trial 2 結果(Safety/changed_actor/不要 BLOCK 率/副作用)】【Stability/QCD】【variant 別総括表】【V5 案(設計のみ)】【Opus L2 論点案】【ユーザー判断 11 該当有無】【Dangling Reference/Production 無変更確認】【費用: 今回/累計/残予算(¥400)】【Git(hash・raw URL)】【Status】。Status は TRIAL2_DONE_TARGET_MET / TRIAL2_DONE_IMPROVEMENT_PROPOSED / STOPPED(理由) / USER_DECISION_REQUIRED のいずれか。

## 5. STOP 条件(本委任)
本委任累計 ¥50 超え見込み/API error 3 fixture 連続/harness 不具合/Production ファイル変更発生/ユーザー判断 11 該当。STOP 時は理由・それまでの結果・費用を報告して終了(自動 retry しない)。

## 6. 実行結果サマリ(委任完了後、事実記録)

- Step2診断(V2/V3、10 call、¥4.1258): B1/B2_hormuz/B3/B4全てLLM一次severity=MAJORとなり
  schema variant層(QUALITY/ACCEPTABLE分岐)に到達せず。不要BLOCK率=V2:4/4(100%)・
  V3:4/4(100%)、baseline 75%より悪化(B2_hormuz新規検出のため)。Meta_run03_standard
  (negative control)は両variantとも正しくBLOCKING検出。
- V4-A実装(TRIAL_PROMPT_DIFF_BLOCK_V4A、647文字、sha256=
  7d8229090910ec1979ac2dbadd2ada8715c14ea441a4acd6edf5279291efe1ad)。V4-C実装
  (V4CRegressionFixtureTest、3テスト)。mock test合計37件全PASS(既存29+新規8)。
- Trial 2(V4-A): Step1(17 call、¥3.8175)Safety 100%達成(重大群12/12・changed_actor
  n5 5/5)。Step2(5 call、¥1.9884)不要BLOCK率2/4(50%、n=1のためnon-determinismと
  区別不可、副作用なし)。Step3(20 call、¥4.8968)gold既知2fixture平均一致率80%
  (V0実測90%を未達、advanced改善/standard悪化)。QCD cost概算は概ねV0の1.5倍以内。
- V5案(設計のみ、未実装): V5-A(B1限定Prompt拡張、理論値25%到達可能、最有力)、
  V5-B(B2/B3/B4はgold再確認のみ)、V5-C(severity=MAJORでも降格を許す構造変更、
  fail-closed部分緩和の可能性ありユーザー判断11抵触可能性、実装・実行せず)。
- 費用: 委任_03合計¥14.8285(52 call、error 0)。累計¥22.1167/総枠¥400、残¥377.8833。
  Guardrail¥50中29.7%使用。
- Production/Dangling Reference: `git diff --stat`でProductionファイル無変更確認。
  API key漏洩なし。
- Status: `TRIAL2_DONE_IMPROVEMENT_PROPOSED`。
- 詳細: `docs/pm/design_open233_checker_redesign_trial_01.md`§4-補、
  `OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`§10、`DECISION_LOG.md`同日
  「OPEN-233-CHECKER-REDESIGN-TRIAL-01: Step2診断+V4-A/V4-C実装+Trial 2実行」エントリ。
