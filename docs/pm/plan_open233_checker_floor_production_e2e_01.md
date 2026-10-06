# 計画: OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(着手前スコーピング、委任_01、2026-10-06、¥0)

性質: 計画のみ(`PLAN_READY`)。コード・Prompt・SSOT変更なし、有料APIなし。Opus条件Aレビュー(実装前)対象。以降【確認】=今回Grep/Readで実在確認、【推測】=見積・仮定。

## §0 前提
- ユーザー決定(2026-10-06)2点=`APPROVED_FOR_PRODUCTION`(人間ユーザー承認済み)。E2E・runtime evidence・SSOT確認が済むまで`PRODUCTION_WIRED`としない。
  - (1) Checker仕様=RECLASSIFY-02でVALIDATED: 「Ledgerに書いていない」だけでは候補にしない/Ledgerとの食い違い・具体的新事実の追加を候補/主体・相手先・範囲・限定条件も照合(`docs/pm/reclassify_open233_checker_selectivity_02.md`)。
  - (2) 後段の機械判定(deterministic floor)は数字(`changed_number`)のみ残す。主体・否定・比較・時期・因果等の「AIを強制的に重大へ上書きする機械判定」は廃止(追加確認トリガー・時期verifyも廃止)。
- 旧仕様の完了9 runは新仕様の正式Evidenceにしない。新仕様で20 runを最初から行い、今回は9/20 runで区切り集計・報告(残り11 runはユーザー確認後)。9 run中は品質問題・重大Fact見逃し・Human Reviewでも止めず、技術障害(API障害・実行不能・データ破損)のみ例外。
- 実装の対象は`er052_open233_self_recovery_flow_runner_01.py`(Self-Recovery Flowの実装本体)。【確認】`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`は「配線STOP」状態(OPEN_ITEMS)で、er052 runnerをer012/er019等の量産経路へ接続する作業は本計画に含めない。E2Eは前回E2E-ACCEPTANCE-01と同じer052 runner上の「Production候補経路」で行う【Fable確認要: 委任文の「Production初回path含むE2E」はこの意味で良いか】。

## §1 変更箇所一覧
### 1-A Checker(Stage 1)側
【確認】VALIDATED仕様の実体は`er052_output/open233_reclassify_02/reclassify_candidates_02.py`の**再分類(post-filter)**: r3/r5(coverage checker)が出した候補のうちmodel由来(source=`model_r3`/`model_r5`)だけを1 call(run単位)で SUPPORTED/NO_FACT_CLAIM/CANDIDATE に再分類し、CANDIDATE以外は候補から落とす。決定論(`deterministic`)・`coverage_gap`由来は不変。API未返却は`CANDIDATE`扱い(fail-closed)。gpt-6-luna/effort=medium。r3/r5のprompt本文(coverage_checker L211-260)は変更しない(VALIDATED対象外、recall再測定が不要)。

| # | ファイル:箇所 | 現挙動 | 新挙動 |
|---|---|---|---|
| C1 | 新規`er052_open233_stage1_reclassify_01.py`(正本=reclassify_candidates_02.pyの`PROMPT_TEMPLATE`(L38-65)+`SCHEMA`(L67-78[actor/counterpart/scope/qualifier_match含む])を逐語移植) | なし | `reclassify_candidates(fixture, candidates, call_fn)`: model由来のみ対象、非CANDIDATEを除去、未返却/schema不一致/例外はCANDIDATE維持、audit(各claimのverdict・4観点・reason・費用)を返す |
| C2 | runner `stage1_coverage_fresh`(L1812、初回) | r3/r5∪候補をそのまま返す | `STAGE1_RECLASSIFY`ON時、`cov.run_stage1_coverage`後・`to_stage1_parsed`前に再分類を挿入 |
| C3 | runner `run_recheck_coverage`(L1823、Rewrite後Recheck) | Recheck候補をそのままdeviationsへ | 同再分類を挿入(prior_issue解消判定は再分類後の候補で行う) |
| C4 | runner `run_exit_check_coverage`(L1844、出口3'-R全文) | 同上 | 同再分類を挿入 |
| C5 | runner `make_stage1_call_fn`系(call_fn、`recovery_stage`ラベル) | stage1_*のみ | `stage1_reclassify`等のラベル追加。費用は`STAGE_MAP`(E2E script)で独立集計 |
| C6 | coverage_checker r3/r5 prompt・出力schema・`changed_*`フラグ生成 | 10フラグ生成 | **変更しない**(§2-1) |
【確認】Stage 1候補の入口はGrep(`stage1_fresh_dispatch`L8381/L8388[初回+同入口の再試行lambda]、`run_recheck_coverage`L9387、`run_exit_check_coverage`L8557)で3種のみ。全て`stage1_coverage_fresh`/`run_recheck_coverage`/`run_exit_check_coverage`に集約され、候補はdeviations→`run_stage2`(L3682、呼び出しL8639)に合流する。retry/fallback/regen専用の別Stage 1入口は見当たらない【推測: 実装時にGrep再確認】。旧仕様の過剰候補が後段で復活する経路を作らないため、**3関数全てに再分類を入れる**(初回だけだとRewrite後に旧仕様の過剰候補が戻り矛盾)。`run_recheck_confirm`(L9487、AI確認call)はfloor非関与のため変更なし。

### 1-B 後段機械判定(floor)側
【確認】floorの本体は`run_stage2`内(L3823 `apply_floor`)の1箇所。初回・Recheck由来・出口由来・retry・次cycleは全て`run_stage2`を通るため、`apply_floor`1点の変更で全経路に効く(経路別の修正は不要)。
| # | ファイル:箇所 | 現挙動 | 新挙動 |
|---|---|---|---|
| F1 | runner L779 `FLOOR_FLAGS`(5種: actor/number/negation/comparison/time) | floor発火+フラグ持ち回りの両方に使用 | **変更しない**(フラグ持ち回りL1985・L8043・`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`L2709が依存) |
| F2 | 新定数`MECHANICAL_FLOOR_FLAGS=["changed_number"]`+切替`FLOOR_MODE`("legacy_5flags"既定/"number_only") | なし | `apply_floor`(L2432)・`apply_floor_cited`(L2486)・`floor_verify_target`(L2868)が参照する発火集合のみを切替 |
| F3 | `apply_floor`L2437 `triggered=[k for k in FLOOR_FLAGS...]` | 5種のどれかで強制BLOCKING | number_only時はchanged_numberのみ。`precheck_floor`(L2433)・`detected_by_enumeration`複製claim除外(L2435)は不変 |
| F4 | `FLOOR_VERIFY_MODE`(L403、E2E scriptがtime_only[KPI_TRIAL_SWITCHES L425]を適用) | 時期floorだけ追加確認2回で解放 | E2E scriptで`off`を明示(時期floor自体が無くなるため)。コード(L2759-3060)は休眠のまま残置、number_only時は`floor_verify_target`がFalse(number=決定論のみ、L2761) |
| F5 | `CAUSAL_FLOOR`(L3254、KPI_TRIAL_SWITCHES L432でTrue)=Tier 0因果floor+補助ベルト(G_H/issue_actor)、`stage2_release_guard`L3361、適用L3920-3936 | changed_causality等でAI非BLOCKINGをBLOCKINGへ戻す | E2E scriptで`CAUSAL_FLOOR=False`を明示(【確認】旧9 runで`changed_causality_floor`1件・`tier0:aux:issue_actor`1件が発火)。`TIER0_G_L_ENABLED`は既定False維持 |
| F6 | `precheck_floor`(L8027 `build_precheck_floor_claims`、`run_precheck`L648が5種check: actor_missing/number_mismatch/date_mismatch/negation_marker/comparison_marker) | 5種全てStage 2を飛ばして直接BLOCKING(F3_PRECHECK_ALWAYS=Trueで常時実行) | **要判断**(§2-4): 数字以外4種もAI上書き機械判定。推奨=number_mismatchのみ残す(`PRECHECK_KINDS`絞り込みを追加)。【確認】旧9 runでprecheck_floor発火は0件 |
| F7 | `DISCLOSURE_GAP_DISQUALIFYING_FLAGS`(L2709=FLOOR_FLAGS+changed_scope)、`apply_hook_aware_downgrade`(L2520付近) | フラグ有でBLOCKINGからの降格を禁止 | **変更しない**(FLOOR_FLAGSを縮小しないためそのまま。降格禁止=AI BLOCKINGの維持であり、AIを重大へ上書きする機構ではない)。【Fable/Opus確認要】 |
| F8 | `STAGE2_SECOND_OPINION`(S1、AI第2意見、L4026-4088)・`classify_problem_kind`(L561、Rewrite水準選択) | AI判定・Rewrite水準の選択 | 変更しない(floorではない)。S1はAI判定のためON維持。S1対象は「非BLOCKING∧MAJOR」で候補減に比例して減る |


### 1-C E2E・集計script(新規、旧scriptは変更しない)
| # | ファイル | 内容 |
|---|---|---|
| E1 | 新規`er052_open233_e2e_acceptance_02.py`(`er052_open233_e2e_acceptance_01.py`のコピー改造) | 出力先を新規`er052_output/open233_e2e_acceptance_02/`(【確認】旧scriptは`os.path.exists(path)`で既存runをskipするため旧dir流用は不可)。`apply_switches`に新スイッチ(STAGE1_RECLASSIFY=True/FLOOR_MODE=number_only/FLOOR_VERIFY_MODE=off/CAUSAL_FLOOR=False/PRECHECK_KINDS)を明示、assertで値固定。`STAGE_MAP`に`stage1_reclassify`を追加し費用を独立集計。`--max-runs 9`(planの先頭9件で区切る) |
| E2 | 同E1内 停止条件 | 旧script(L243-275)はwaste flag・per-run cost・provenance違反・API失敗3run超でbreak。新仕様では**post-run waste flag(例`same_candidate_rewrite_gt_3`、旧9 runのneg7停止原因)とSTAGE4/Human Reviewでは止めない**(記録のみ)。止めるのは(a)TrialAbort(API連続エラー)、(b)例外2 instance以上、(c)budget枠超過、(d)provenance違反(Stage 1/再分類のcall無し等=Evidence無効化)。run内RunWaste(cost>¥20/call>80)は当該runをabort記録して次runへ続行する案を推奨【Fable判断要: 技術障害の範囲】 |
| E3 | 新規`er052_open233_e2e_acceptance_02_agg_01.py`(¥0、保存run jsonのみ読む) | 委任文A〜Eの数値を機械集計(§4-4) |

## §2 設計判断
### 2-1 数字以外の`changed_*`フラグの生成(両案、推奨=案B)
- 案A(生成を止める): r3/r5のprompt・schemaからactor/negation/comparison/time/causalityを外す。利点=Production単純化・フラグ不整合(Opus OF-043: absenceに"変更"フラグ)の根を断つ。欠点=r3/r5のprompt/schema変更は**VALIDATED対象外**でStage 1 recall再測定(gold 6件×n=3、有料)が要る(OF-001文化)。`classify_problem_kind`(L561、Rewrite水準選択)・フラグ持ち回り(L1985/L8043)・`DISCLOSURE_GAP`降格禁止(L2709)がフラグに依存しており波及修正が増える。
- 案B(生成は維持、floorで使わない): r3/r5は不変、`apply_floor`等の発火集合だけを数字に絞る。利点=VALIDATEDのr3/r5をそのまま使え回帰範囲が小さい、Rewrite水準選択・分析(「機械判定ならどのフラグが立っていたか」の反実仮想記録=§4-4のB項目)が維持できる。欠点=生成されるが使われないフラグが残る(Production仕様上は「記録・Rewrite水準選択用」と明記が必要)。
- **推奨=案B**。理由: 承認2点はいずれも「候補の絞り込み」と「機械上書きの廃止」であり、フラグ生成そのものの変更は承認範囲外。案Aは別途承認・再測定が必要。将来の簡素化はE2E結果後の別項目(新仕様候補として報告のみ)。

### 2-2 時期verifyの廃止
時期floorが無くなるため`FLOOR_VERIFY_MODE=off`で足りる。コード・既存28テスト(`TestFloorVerify60`)は休眠のまま残置(削除は差分と回帰リスクが大きく利益が小さい)。CURRENT_SPECの時期verify節(L2373-2389)は「廃止(休眠)」と更新。

### 2-3 Stage 2(後段AI)・S1は不変の確認
Stage 2のAI判定(rubric V7b、`BODY_RUBRIC_DEFAULT`、`run_stage2`内のLLM判定本体)、S1(第2意見)、Hook-aware/disclosure-gap降格、Rewriteラダー、cap(MAX_CYCLES=2/HARD_MAX_CYCLES=3)・上限回数は変更しない。変更は`apply_floor`系の発火集合・Tier 0 OFF・precheck種別・Stage 1再分類の4点のみ。

### 2-4 precheck_floorの扱い(要判断)
【確認】`run_precheck`(precheck L648-684)は数字以外にdate/actor/negation/comparisonのmarker検査を持ち、検出するとStage 2を経由せず直接BLOCKING(runner L8639以降)。ユーザー決定の「数字以外のAI強制上書き機械判定を廃止」を文言どおり適用するなら4種も廃止対象。ただし承認文が`changed_*`floor中心の記述のため、precheckまで含むかは**Fable/ユーザー確認が望ましい**。推奨=文言どおり数字(number_mismatch)のみ残す。旧9 runで発火0件のため安全影響は小さい【確認】。

### 2-5 再分類をpost-filterで入れる理由
VALIDATED対象は「旧Checker候補の再分類」(1 call/run)の形。r3/r5 promptへ4観点を直接入れる案は別物(未検証、recall再測定要)。post-filterなら初回/Recheck/出口の同一関数を3箇所へ呼ぶだけで済み、旧仕様との差分が明確。追加費用は初回約¥0.34/run(¥14.38/42 run)+Recheck/出口の再分類【推測】。

### 2-6 再分類とnumber floorの相互作用
再分類で非CANDIDATEになったmodel由来候補はfloorへ到達しない。`changed_number`フラグ付きのmodel候補が再分類で落ちると数字floorも発火しない(規則2で数値を含む主張は「Ledgerと一致しない限りCANDIDATE」の厳格側のため稀と推測)。決定論由来(数値の決定論検査・coverage_gap・precheck number)は再分類を通らず不変。E2Eで「changed_number付きだが再分類で除外」件数を必ず集計する(§4-4)。
### 2-7 S1の扱い
ON維持(Trial既定構成と同じ。AI判定の第2意見でありfloorではない)。Opus OF-045は「案4としてのS1」への評価であり、本計画のS1(既存構成)とは別。

## §3 test計画(¥0、実装委任で実施)
- 回帰基準: `run_project_regression.py --pattern "er052*_test_*.py"`=863件PASS(RECLASSIFY-02時点の基準)。内訳【確認】runner test 720、coverage checker 75、recheck_coverage 17、e2e 7ほか。新スイッチの既定は旧挙動(`FLOOR_MODE`=legacy_5flags、`STAGE1_RECLASSIFY`=False、`PRECHECK_KINDS`=全5種)のため、**既存テストの変更は原則0件**(floor関連: `TestApplyFloor`5・`TestFloorCitedVariant`4・`TestFloorVerify60`28・`TestNaturalRoundingFloorSuppression`7・`TestFloorFactIdBroadcastFix35`5・`TestCausalFloorAndS1_03`18は旧既定で不変)。削除テスト0。KPI_TRIAL_SWITCHES自体はE2E後の最終採用まで書き換えない(E2E scriptで明示設定)。
- 新規test(目安合計45〜55件):
  1. 再分類module(約14): prompt/schemaが`reclassify_candidates_02.py`とsha256一致、model由来のみ対象・決定論/coverage_gap不変、非CANDIDATE除去、未返却/schema不一致/例外=CANDIDATE維持(fail-closed)、候補0件でcall無し、4観点mismatch→CANDIDATE維持、費用・audit記録。
  2. 3関数への配線(約8): 初回/Recheck/出口の各々でON時のみ再分類、OFFで従来と完全同一、API失敗時の既存fail-closed(H1/`_recheck_api_failure`)維持。
  3. floor number_only(約12): actor/time/negation/comparison単独ではAI非BLOCKINGを上書きしない、number単独は強制BLOCKING、複数フラグ+numberはnumber理由で発火、precheck_floor(number)・enumeration複製除外は不変、`apply_floor_cited`・`floor_verify_target`がnumber_onlyで時期対象を返さない、CAUSAL_FLOOR=Falseでtier0不発、フラグ自体は持ち回り(L1985/L8043)・`classify_problem_kind`不変。
  4. precheck種別絞り込み(約4)。
  5. E2E script(約7): スイッチassert、旧dirを使わない、`--max-runs 9`、waste flag/Human Reviewで止まらない、API連続エラーで止まる、provenance(再分類call無し=違反)。
  6. integration(fake client、約4シナリオ): (a)数字不一致claim+AI=QUALITY→BLOCKING(number floor)、(b)主体フラグ+AI=QUALITY→上書きされない、(c)Rewrite後Recheck経路、(d)出口3'-R経路。各経路の`floor_reason`集計を保存。
  7. 静的走査test(1〜2): number_only時に非numberフラグでBLOCKINGを返す箇所が`apply_floor`/`apply_floor_cited`/`floor_verify`/Tier0/precheck以外に無いことをGrep結果と照合(残存確認)。
- runtime evidence(¥0): `--stage dryrun`(stub client)で初回→Rewrite→Recheck→出口→最終状態まで1 instance通し、各`stage2_results[*].floor_reason`・再分類call有無を保存。保存先=`er052_output/open233_e2e_acceptance_02/`配下(新規dir、既存`er0XX_output`構造内)+詳細は`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`の新§(§80以降)。
- 完了条件: 新規全PASS+全体回帰PASS(件数=基準863+新規件数)。失敗時はE2Eへ進まない。

## §4 E2E計画
### 4-1 構成・順序(前回計画を踏襲)
20 run=SC(bgroup_B3/safety_A2A3/safety_A4/safety_A5/bgroup_B4/neg5_hormuz_div_a2)×n=2(12)+Standard/Advanced対4(hormuz_run03・meta_run03)+負例4(neg1/neg2/neg3/neg7)。順序は`plan()`(対4→負例4→SC sample 1[6]→SC sample 2[6])。**今回の9 run=先頭9件=対4+負例4+bgroup_B3**(旧仕様の完了9 runと同一instance構成。旧結果は比較参照のみで新Evidenceにしない)。【確認】`plan()`と`SC_IDS`先頭=bgroup_B3。
- 注意【Fable確認要】: 9 runのSCはB3のみ。safety_A2A3/A4/A5/B4/neg5(gold 5件)は残り11 runまで検証されず、**9 runだけでは「重大Fact見逃し0」をSafety KPIとして主張できない**。報告に明記する。
### 4-2 実行設定
- 新`er052_open233_e2e_acceptance_02.py --stage main --yes-run-paid --budget-jpy <9 run用枠> --per-run-cap-jpy 20 --max-runs 9 --out-dir er052_output/open233_e2e_acceptance_02`。枠は§6のhigh見積+約20%で`¥60`を推奨【Fable判断要。残予算は`budget_state`/OPEN_ITEMSで要確認】。全run `stage1_cache=None`・baseline代替無効・frozen/reuseなし(provenance)。
- 停止=技術障害のみ(§1-C E2参照)。品質・Human Review(STAGE4)・重大見逃し・waste flagは記録のみで継続。問題を見つけてもその場でPrompt/仕様変更・追加対策はしない。
- 完了後は残り11 runを開始しない。報告のみ。
### 4-3 run別保存先
`er052_output/open233_e2e_acceptance_02/runs/s1/<instance_id>.json`(run単位)・`run_log_main.json`・`budget_state_*.json`・`e2e_aggregate.json`(agg出力)。
### 4-4 集計script(作成要)
新規`er052_open233_e2e_acceptance_02_agg_01.py`(旧`run_agg`[L573]を流用拡張)。¥0・保存jsonのみ読む。出力=`e2e_aggregate_02.json`+claim単位の「ラベル付け用シート」`labeling_sheet_02.json/.md`。
- A. Checker: 候補件数をsource別(AI=`model_r3`/`model_r5`[再分類後に残った分]、機械=`deterministic`/`coverage_gap`/precheck)に、AIのみ/機械のみ/両方重複(同一claim key)/延べ/重複除外後を機械集計。再分類前後の件数・除外件数・「changed_number付きで再分類除外」件数も出す(2-6)。
- B. 後段: Stage 2のAI判定(`llm_materiality`)の重大/軽微/問題なし件数、後段機械(number floor)=発火数、AI判定との重複(AIもBLOCKING)、機械のみで重大化した数。反実仮想として「旧5フラグなら発火していた件数」も記録(フラグは生成維持のため機械的に算出可能、案B)。
- C. Rewrite: 件数・発生run数・(必要/不要/再修正要は§4-5のラベル)。D. Human Review: STAGE4出口の全項目(対象英文・Ledger Fact・Checker AI/機械・後段AI/機械・Rewrite内容・Recheck結果・直接原因)。E. Safety・Cost: run別費用・合計・平均・Checker(Stage 1+再分類)/後段判定(Stage 2+S1)/Rewrite(+Recheck+出口)の分離、worst run。
### 4-5 KPI provenanceと事後評価ラベル
- provenance(全項目共通): Stage 1・再分類・Stage 2・Rewrite・Recheck・出口すべて**fresh(frozen/reuse/baseline代替なし)、Production候補初回経路を通るE2E=Yes**(`provenance_violations`で機械検証、違反は無効)。費用は`call_log`実測。
- 「真に問題/不要」ラベル(件数のうち機械で決まらない部分): ¥0でSonnetが、候補claimの逐語引用とLedger該当factの原文(claim/scope/conditions/`notes_for_writer`)を並べた表を作り、一致・不一致を**Ledger原文の逐語照合で**判定案を付ける(Ledgerの具体的値と食い違い/具体的新事実の追加=真に問題、言い換え・平易化・Ledger未記載のみ・修辞=不要)。判断不能は「判断不能」として別枠にし推測で埋めない。Sonnet推測ラベルは**Fable/ユーザーの確認が前提**で確定扱いしない(OF-048型の集計構造不備を避けるため、原因分類を正規表現でなく逐語照合表で行う)。確認位置=集計報告の前にFableが判断不能+境界例を確認、ユーザー報告ではラベル済/未確認を分けて記す。

## §5 時間見込み(【推測】、旧E2E実績=9 runで3,510秒[平均390秒/run、最大644秒]を基準)
| 工程 | 内容 | 見込み |
|---|---|---|
| 0 | Opus条件Aレビュー+Fable照合(実装前) | 30〜45分 |
| 1 | 実装: 再分類module(約150行)+3関数配線(約60行)+floor/precheck/スイッチ(約40行)+E2E script(約100行改造) | 60〜90分 |
| 2 | test: 新規45〜55件+全体回帰(863件+新規)+¥0 dryrun通し+runtime evidence保存 | 40〜60分 |
| 3 | 集計script作成(agg+ラベル用シート)と¥0 dryrunでの動作確認 | 30〜40分 |
| 4 | 9 run E2E本実行(再分類callで1 runあたり+60〜120秒、Rewrite減で相殺。1 run 6〜8分) | 55〜75分 |
| 5 | 集計・ラベル案作成・REPORT・RESULT_PACKET(Sonnet)+Fable照合・ユーザー報告 | 50〜70分 |
| 合計 | 実装〜9 run報告まで | **約4.5〜6.5時間(中央約5.5時間)**。うち「実装+test完了」まで約2.5〜3.5時間、「9 run E2E完了」まで約3.5〜5時間 |
委任回数の目安: 実装_01(module+配線+floor)、実装_02(E2E script+agg+test+dryrun)、E2E本実行_03、集計_04(+必要ならFable指示の修正1回)=4〜5回。Sonnet上限(初回+修正3回)内。

## §6 費用見積(9 run、¥)
基準【確認】旧E2E 9 run: 合計¥43.91(平均¥4.88/run、worst neg1 ¥8.82)。1 runあたりstage別平均: Stage 1 ¥1.40/Stage 2(+floor_verify+S1) ¥1.44/Rewrite ¥0.71/Recheck ¥0.87/出口3'-R ¥0.45。旧9 runのうち8 runでRewrite発動【確認】。
仮定【推測】: (a)再分類で候補が約半減(RECLASSIFY-02: NORMAL 24.2→10.75/run)→Stage 2費用が比例的に減る、(b)floor誤爆35件(旧9 run、うちnumber関連4件)が消えRewrite+Recheck+出口が減る、(c)時期floor_verify call(旧A2A3で¥0.78)が無くなる、(d)再分類callが初回+Recheck+出口に加わる(初回¥0.34/run実績、Recheck/出口は候補が少なく各¥0.10〜0.20【推測】)。
| 水準 | 仮定 | 1 run | 9 run |
|---|---|---|---|
| low | Stage 2×0.5、Rewrite/Recheck×0.4、出口×0.5、再分類¥0.4 | 約¥3.4 | **約¥30** |
| mid | Stage 2×0.7、Rewrite/Recheck×0.65、出口×0.7、再分類¥0.55 | 約¥4.3 | **約¥39** |
| high | Stage 2×0.9、Rewrite/Recheck減なし、出口×1.0、再分類¥0.8 | 約¥5.5 | **約¥50** |
推奨`--budget-jpy`は¥60(high+約20%)、1 run cap ¥20(旧script既定のユーザー承認値)維持。旧9 runの再現(Rewrite多数・減少なし)でも¥44前後でhigh内に収まる。残予算の実額は本計画では未確認【Fable確認要】(旧budget_stateは¥50.12が別枠で記録、総枠の残は不明)。

## §7 リスク
1. 時期floor廃止とOpus指摘(台帳OF-043〜OF-048、`opus_l2_review_open233_floor_selectivity_01.md`): Opusは「時期は承認済みverify維持」「hold-out(rep30)でneg3 gold[時期]を案1が見逃す」と指摘。ユーザー決定は時期floor/verifyとも廃止のため、**neg3型(時期ずれgold)を拾えるかはStage 1新仕様(再分類の4観点・限定条件照合)+Stage 2のAI判定に依存**し、機械の安全網がなくなる。E2Eで測定(neg3_hormuz_prodrunner_b1bは9 runに含まれる)。9 runだけではgold SCがB3のみ→残11 runまで未確認。
2. 主体・比較・否定のgold(A2A3/A5/B4等)は9 runに含まれず、機械floor廃止後の見逃しは11 run目以降まで測れない。9 run報告では「測定外」と明示。
3. 再分類の過検出/境界例: 「将来予測・一般傾向・ユーザー認識の推測文」がNO_FACTから再候補化(RECLASSIFY-02で9件)、Ledger未記載のみの境界例7件。Stage 2のAI判定が吸収する想定だが、軽微以下の不要候補が残りうる(E2Eで「不要候補化」を測定)。
4. Checkerコスト増: 再分類は¥0.34/run(初回)+Recheck/出口分。RECLASSIFY-02は01比+約¥0.09/run。Stage 2減との差し引きは§6。
5. 再分類がnumber floorを素通りさせる可能性(2-6)。決定論の数値検査は不変だが、モデル由来のchanged_number候補が除外された件数を必ず記録。
6. precheck(2-4)・`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`(F7)・S1ON維持の3点は文言解釈の余地があり、実装前にFable/Opusで確認(誤解釈のままE2Eすると9 runが無効になる)。
7. Stage 1の非決定性(OPEN_ITEMS: A構成fresh確認でSC 4/5・neg5 B3-same 0/2)。E2E 9 runの結果は単発サンプルでSafety判定には使えない(報告に明記)。
8. 作業工程リスク: 旧E2E scriptは`exists→skip`と停止条件が厳しいため、新script分離が必須(§1-C)。旧結果を混ぜない。

## §8 Existing Spec Check
- A(既存SSOT根拠): CURRENT_SPEC L2338-2417「OPEN-233 Self-Recovery Flow」節(線引き・時期verify L2373-2389・Trial Closeout L2391-2406[L2397にFLOOR_VERIFY_MODE=time_only]・Production Flow仕様L2408-)、OPEN_ITEMS L725-729(FLOOR-SELECTIVITY/KPI-RECOVERY/A1-PROD/SELF-RECOVERY-PRODUCTION-WIRING行)、OF-043〜048。
- B(既存と矛盾する点): 旧SSOT「比較/方向/主体/数値/否定は決定論維持」(OPEN_ITEMS L727)と「時期のみverify」(L2373)は本決定で数字のみへ置換。`CAUSAL_FLOOR`(Tier 0)ON構成(KPI_TRIAL_SWITCHES)も置換対象。いずれもユーザー承認済みの仕様変更であり矛盾ではなく更新対象。
- C(新規提案): 再分類のpost-filter実装形・`FLOOR_MODE`スイッチ・`PRECHECK_KINDS`絞り込み・案B(フラグ生成維持)は実装設計であり承認済み仕様の範囲内。precheck非数字種の廃止(2-4)のみ解釈確認が必要。
- CURRENT_SPEC更新箇所(実装委任・E2E後にFableが指示): L2373-2389(時期verifyを「廃止(休眠)」)、L2397(構成一覧からFLOOR_VERIFY_MODE=time_only削除、number-only floor+Stage 1再分類+CAUSAL_FLOOR OFFを追記)、L2408-以降(Production Flow仕様へ再分類・floor縮小を反映)。`PRODUCTION_WIRED`表記はしない。DECISION_LOG(2026-10-06承認)・OPEN_ITEMS(新ID行、Status=`APPROVED_FOR_PRODUCTION`、E2E前)もSSOT更新の対象(Sonnetは編集せず指示に従う)。

## §9 Opus条件Aレビューへ渡す論点案
1. 再分類を3関数(初回/Recheck/出口)へpost-filterで入れる構造は、旧仕様候補の復活経路を残さないか(Recheck prior_issue解消判定が再分類で歪まないか)。
2. 案B(`changed_*`フラグ生成維持・floor発火集合のみ縮小)で、フラグ不整合(OF-043)由来の悪影響が`classify_problem_kind`・降格禁止(F7)・Rewrite水準選択に残らないか。
3. 時期floor・verify廃止後、neg3(時期)goldをStage 1再分類+Stage 2でどの程度担保できるか。E2E 9 runの測定設計で足りるか。
4. precheck非数字4種を廃止対象に含める解釈の妥当性、`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`を旧5種のまま残す判断。
5. S1ON維持・CAUSAL_FLOOR OFFの組み合わせと、「重大見逃し0」KPIの9 runでの主張範囲(SC=B3のみ)。
6. 停止条件(技術障害のみ停止、waste/HR/品質では継続)とRunWaste(cost>¥20/call>80)の扱いの安全性。
7. 集計の「真に問題/不要」ラベル付け手順(逐語照合表+Fable/ユーザー確認)がOF-048型の構造的偏りを避けられるか。

