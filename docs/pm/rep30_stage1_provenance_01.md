# rep30 Stage 1 実構成の確定(run単位、委任_06 / CORRECTION-01、0円・read-only)

管理ID: OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01。Status: `APPROVED_FOR_PRODUCTION`のまま(`PRODUCTION_WIRED`ではない)。
集計: `er052_output/open233_kpi_recovery_02_offline_01/agg_rep30_stage1_provenance_01.py`、出力json=同ディレクトリ`agg_rep30_stage1_provenance_01.json`(38 run全件+6 claim+prompt sha照合)。API呼び出しなし。

## 1. 確認した事実(コード・記録による)

- rep30の実行体は`er052_open233_self_recovery_flow_runner_01_rep30_full_01.py`。`runner.build_target_instances()`をそのまま使い、`--force_fresh_stage1`相当の上書きは**ない**。したがってStage 1区分は`build_target_instances()`の`stage1_mode`で決まる。
- `stage1_mode="fresh"`なのは3 instance(`meta_run03_advanced`、`hormuz_run01_advanced`、`hormuz_run02_advanced`)だけ。他26 instanceは`stage1_mode="reuse"`(過去に保存したV4A出力を`stage1_reuse()`で読むだけ、API呼び出し0)。
- reuseの出力元は`er051_output/open233_checker_trial_01/trial_02/step1|2|3/<id>/V4A/run_1.json`(2026-09-29生成)と`er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/c_negative/<id>/V4A/run_1.json`(2026-09-30生成)。いずれもmodel(またはmodel_returned)=`gpt-6-luna`。
- `bgroup_B2_hormuz`(1 run)・`bgroup_B3`(2 run)は`substitute_baseline_on_stage1_miss`により、V4A出力が非検出だったためfixtureの`baseline_parsed`(現行Production V0の記録、model=`gpt-5.6-luna`)へ**差し替え**られた(`stage1_recall_miss_substituted=True`)。
- freshのStage 1構成(`stage1_fresh_with_enumeration`): V4A prompt+`RELATED_FACT_ID_INSTRUCTION`(+origin)+`SAME_FACT_ID_ENUMERATION_INSTRUCTION`、developer message=`V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`(`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT=True`)、schema=`same_fact_id_locations`追加、model=`MODEL`=`gpt-6-luna`。call_logのprompt_sha256は3/3件が「列挙instruction付き」の再計算値と一致(確認済み)。
- reuse出力のprompt構成: reuse-mode 34 run(frozen 31+V0差替え元3)中25 runで、保存されたprompt_sha256が「V4A prompt+related_fact_id(+origin)のみ、列挙instructionなし」の再計算値と一致(確認済み)。残り9 run(frozen、safety_er009_*系の各1 run)は同方法で再現できず不一致(原因未特定)。
- reuse出力のdeveloper message: 保存jsonには記録されていない。`developer_message_override`引数(重大誤解原則の配線)が`er051`へ追加されたのは委任_27(2026-10-01)で、reuse出力(09-29/30生成)より後のため、**原則なしの`DEVIATION_DEVELOPER_MESSAGE`だったと推測**(コード履歴からの推測、保存データでは未確認)。
- reuse出力のschemaには`same_fact_id_locations`が無い(31 run全てで確認済み)。rep30では`deterministic_same_fact_id_location_fallback`(決定論、API 0)で同箇所列挙を補っている。
- deterministic pre-check: `precheck.run_precheck`はStage 1がLEDGER_DEVIATIONだったinstanceでbaseline計算が走り(ACCEPTABLE_STAGE1で早期returnするinstanceでは走らない)、`build_precheck_floor_claims`によるfloor claimがStage 2へ加わりうる。rep30でStage 2 cycle1に`precheck`由来が入ったのは`safety_er009_changed_number`の1 runのみ(確認済み)。
- `severity_final`: Stage 1出力のdeviationには`classify_deviation_trial`が`severity_final`を付けるが、`run_instance`のStage 2への受け渡しは`severity=="MAJOR"`のみで選別する(`severity_final`は選別に使っていない、コード確認済み)。MINOR+flagの昇格ルールも下流では効いていない。

## 2. run単位表(38 instance-run)

凡例: 区分=fresh(API実行)/fresh-cache(s1のfresh出力をsha一致で共有、0 call)/frozen(過去V4A出力のreuse)/V0差替え(Stage 1非検出のため現行Production V0記録へ置換)。model=fresh→runner MODEL、frozen→出力元json記録、V0差替え→V0記録(gpt-5.6-luna)。prompt構成: F=fresh構成(V4A+原則developer+列挙instruction、列挙sha一致)、Z=V4A+related(+origin)のみ・列挙なし(sha一致)、z?=原則なし推測・sha不一致(未再現)。schema列挙=same_fact_id_locationsを出力schemaに含むか。S1raw=Stage 1の指摘総数(MAJOR)、S2=cycle1でStage 2へ渡したclaim数(うち決定論の兄弟箇所列挙追加=enum、precheck由来=pre)。Stage 2へ渡すseverityは全件MAJOR。severity_final使用=選別には不使用(全run共通)。

| s | instance | 区分 | model | prompt構成 | schema列挙 | S1raw(MAJOR) | S2(enum/pre) |
|---|---|---|---|---|---|---|---|
| 1 | bgroup_B1 | frozen | gpt-6-luna | Z | 無 | 5(5) | 5(3/0) |
| 1 | bgroup_B2_hormuz | V0差替え | gpt-5.6-luna(V0記録) | V4A出力は非検出→V0 baseline_parsedへ置換 | - | 0(0) | 1(0/0) |
| 1 | bgroup_B3 | V0差替え | gpt-5.6-luna(V0記録) | V4A出力は非検出→V0 baseline_parsedへ置換 | - | 0(0) | 7(6/0) |
| 1 | bgroup_B4 | frozen | gpt-6-luna | Z | 無 | 10(10) | 11(7/0) |
| 1 | hormuz_run01_advanced | fresh | gpt-6-luna | F | 有 | 1(1) | 1(0/0) |
| 1 | hormuz_run02_advanced | fresh | gpt-6-luna | F | 有 | 0(0) | 0(0/0) |
| 1 | hormuz_run03_advanced | frozen | gpt-6-luna | Z | 無 | 0(0) | 0(0/0) |
| 1 | hormuz_run03_standard | frozen | gpt-6-luna | Z | 無 | 3(3) | 6(5/0) |
| 1 | meta_run03_advanced | fresh | gpt-6-luna | F | 有 | 0(0) | 0(0/0) |
| 1 | meta_run03_standard | frozen | gpt-6-luna | Z | 無 | 3(3) | 3(1/0) |
| 1 | neg1_meta_b3prod_a2 | frozen | gpt-6-luna | Z | 無 | 4(4) | 4(3/0) |
| 1 | neg2_meta_refresh_a2 | frozen | gpt-6-luna | Z | 無 | 2(2) | 2(1/0) |
| 1 | neg3_hormuz_prodrunner_b1b | frozen | gpt-6-luna | Z | 無 | 4(4) | 4(3/0) |
| 1 | neg4_smallbag_div_a2 | frozen | gpt-6-luna | Z | 無 | 0(0) | 0(0/0) |
| 1 | neg5_hormuz_div_a2 | frozen | gpt-6-luna | Z | 無 | 7(7) | 8(7/0) |
| 1 | neg6_smallbag_div_b1b | frozen | gpt-6-luna | Z | 無 | 0(0) | 0(0/0) |
| 1 | neg7_meta_prodrunner_b1b | frozen | gpt-6-luna | Z | 無 | 0(0) | 0(0/0) |
| 1 | safety_A2A3 | frozen | gpt-6-luna | Z | 無 | 6(6) | 10(8/0) |
| 1 | safety_A4 | frozen | gpt-6-luna | Z | 無 | 8(8) | 9(6/0) |
| 1 | safety_A5 | frozen | gpt-6-luna | Z | 無 | 5(4) | 4(3/0) |
| 1 | safety_er009_changed_actor | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_causality | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_certainty | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_comparison | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_negation | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_number | frozen | gpt-6-luna | z? | 無 | 1(1) | 2(0/1) |
| 1 | safety_er009_changed_scope | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_changed_time | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 1 | safety_er009_unsupported_new_claim | frozen | gpt-6-luna | z? | 無 | 1(1) | 1(0/0) |
| 2 | bgroup_B3 | V0差替え | gpt-5.6-luna(V0記録) | V4A出力は非検出→V0 baseline_parsedへ置換 | - | 0(0) | 7(6/0) |
| 2 | hormuz_run03_advanced | frozen | gpt-6-luna | Z | 無 | 0(0) | 0(0/0) |
| 2 | hormuz_run03_standard | frozen | gpt-6-luna | Z | 無 | 3(3) | 6(5/0) |
| 2 | meta_run03_advanced | fresh-cache | gpt-6-luna | F | 有 | 0(0) | 0(0/0) |
| 2 | meta_run03_standard | frozen | gpt-6-luna | Z | 無 | 3(3) | 3(1/0) |
| 2 | neg1_meta_b3prod_a2 | frozen | gpt-6-luna | Z | 無 | 4(4) | 4(3/0) |
| 2 | neg2_meta_refresh_a2 | frozen | gpt-6-luna | Z | 無 | 2(2) | 2(1/0) |
| 2 | neg3_hormuz_prodrunner_b1b | frozen | gpt-6-luna | Z | 無 | 4(4) | 4(3/0) |
| 2 | safety_A2A3 | frozen | gpt-6-luna | Z | 無 | 6(6) | 10(8/0) |

## 3. 集計

- 38 run: fresh 3(API実行、3 instance=`meta_run03_advanced`/`hormuz_run01_advanced`/`hormuz_run02_advanced`の各s1)+fresh-cache 1(`meta_run03_advanced` s2、s1出力の共有、0 call)+frozen 31+V0差替え 3(`bgroup_B2_hormuz` s1、`bgroup_B3` s1・s2)。
- frozen 31 runの生成元: model=gpt-6-luna(21 runは`model`記録あり、10 runのnegative群は`model_returned`のみ記録でgpt-6-luna)、variant=V4A。prompt=V4A+related_fact_id(+origin)。うち22 runはprompt sha再計算で「列挙なし」構成と一致、9 run(safety_er009_*)は未再現。developer messageは原則なしと推測(上記)、schemaに列挙フィールドなし、生成日は2026-09-29(21 run)/09-30(10 run)で、重大誤解原則(10-01)・列挙(W2)の配線前。
- V0差替え 3 run: 差替え元=現行Production V0の記録(`er019_output/.../hormuz/run_02/.../advanced_attempt1.json`等)、model=gpt-5.6-luna。
- 「Production候補として想定していたStage 1構成(V4A+原則+列挙+schema、昇格ルール除く、gpt-6-luna)」でfresh実行された記録がrep30内に何件か: **3 call(4 run)**。いずれも指摘は`hormuz_run01_advanced`の1件のみ(他はStage 1 PASS)。Safety群・B群・negative群・`meta_run03_standard`等ではrep30内にfresh記録は0件。
- 参考(rep30外、未精査の手がかり): iter8(Stage 1 fresh 16 call)では`bgroup_B4`がfreshでStage 2へ0件、`bgroup_B2_hormuz`はV0差替えとなっており、freshの候補構成はB4・B2_hormuzを拾えていない点は一貫する。rep30の採否根拠には使っていない。

## 4. 6 claim(K14 Phase 1の劣後6件)の出所(rep30内、逐語)

出典: `er052_output/open233_stage1_phase1_recall_check_01/agg_phase1.json`(6件)と`agg_rep30_stage1_provenance_01.json`の`six_claims`。

| claim | rep30でStage 2へ渡した出所 | 生成元のChecker構成・model |
|---|---|---|
| B4: "A person can take over when AI alone has trouble. As a system, ..."(MUSE-HC-006) | frozen(s1) | `er051_output/.../step2/B4/V4A/run_1.json`、V4A prompt(列挙・原則なし)、gpt-6-luna、2026-09-29 |
| B4: "People feel differently when they think they are speaking to a machine ..."(MUSE-HC-010) | frozen(s1) | 同上 |
| B4: "Names, plans, and private matters are easier to share ..."(MUSE-HC-010) | frozen(s1)(結合claimの一部+兄弟列挙) | 同上 |
| B4: "As AI makes calls and reservations, useful features make people want to know ..."(MUSE-HC-004) | frozen(s1) | 同上 |
| A2A3: "Just after the charge plan disappeared, prices began to fall."(HF-009) | **rep30のStage 1でも非検出**(frozen V4A出力に無く、Stage 2にも入っていない。s1・s2とも) | 検出したのは現行Production V0記録(`er037_output/.../A3_deviation.json`、gpt-5.6-luna)のみ |
| B2_hormuz: "The disappearance of the fee plan did not lead to a large, lasting fall in prices."(HF-011) | **V0差替え**(s1。frozen V4A出力は0件) | V0記録(`er019_output/.../hormuz/run_02/.../advanced_attempt1.json`、gpt-5.6-luna) |

## 5. 結論(ユーザー§5の判定)

判定: **Yes(6件については)/ 全体としては部分**。

- 6件について: rep30で「現行Production候補のStage 1構成(V4A+原則+列挙+schema、gpt-6-luna)をfreshで実行して検出した」ものは**0/6**。4件(B4)はfrozen(2026-09-29生成、原則なし・列挙なし、gpt-6-luna)、1件(B2_hormuz)はV0差替え(gpt-5.6-luna)、1件(A2A3 HF-009)はrep30でも非検出(frozen・V0差替えのどちらにも含まれず)。Phase 1で候補が0/2だったのは、rep30で検証された構成(frozen V4A)と候補(fresh+原則+列挙)が**一致していないこと**と整合する(因果は未検証、推測)。
- 全体として: rep30の38 runのうちStage 1が候補構成でfresh実行されたのは3 call(4 run)で、いずれもStage 1 PASS寄り(指摘1件)の3 instanceのみ。残りはfrozen 31(構成が異なる)+V0差替え 3。したがって「rep30でVALIDATEDされたStage 1」は主に**frozenのV4A出力+決定論fallbackによる同箇所列挙+V0差替え**であり、Productionで使うStage 1(fresh候補構成)の検出能力はrep30では未検証(B群・Safety群・negative群で0件)。
- これはユーザー§5の「Production wiringの未充足事項(Stage 1 Checkerの正式仕様が未検証)」に**該当する**。本委任はChecker仕様の新設・選定を行わない。STOPしてFableへ報告し、ユーザー判断が必要かはPM側で判断する(rep30構成の忠実再現は、frozenのreuse入力そのものをProductionでどう扱うか=Production初回pathでは「過去出力の再利用」が存在しない、という構造的論点を含む)。

## 6. 確認/推測の区別

- 確認済み: 区分(fresh/frozen/V0差替え)・件数・出力元path・生成日・model・Stage 2へ渡した件数・6 claimの出所・freshのprompt構成(sha一致)・frozen 22 runのprompt構成(sha一致)・列挙フィールドの有無。
- 推測: frozen出力のdeveloper messageが原則なしだったこと(コード履歴からの推測)、frozen 9 run(safety_er009_*)のprompt不一致の原因、Phase 1の0/2とrep30構成差の因果。
- 範囲外で未実施: rep30以前のiter等のfresh出力の精査、候補構成とfrozen構成のどちらがよいかの比較(行わない)。

## 7. A構成(rep30 frozen出力の生成構成)の復元(委任_08 / CORRECTION-02、0円で確定)

集計: `er052_output/open233_kpi_recovery_02_offline_01/agg_a_config_sha_check_02.py`(出力同名.json)。API呼び出しなし。

### 7-1. A構成の定義(再現可能な形)
- 生成元: `er051_open233_checker_trial_02_run.py`(09-29、step1/2/3)と`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`系(09-30、負例群)。いずれも`trial.run_trial_deviation_check(client, ledger_text, article_text, MODEL, "V4A", include_related_fact_id=fixture.get("include_related_fact_id", False), source_article_text=fixture.get("source_article_text"))`を呼ぶ(当時commit `3db494bc`のer051。HEADとの差は`developer_message_override`引数追加のみで、未指定=従来動作、コード差分で確認)。
- prompt組立: `build_trial_prompt_template("V4A")`(=`vfl01.DEVIATION_PROMPT_TEMPLATE`+`TRIAL_PROMPT_DIFF_BLOCK_V01`+`TRIAL_PROMPT_DIFF_BLOCK_V4A`).format(ledger,article) +(`include_related_fact_id`が真なら`RELATED_FACT_ID_INSTRUCTION`)+(sourceがあれば`ORIGIN_INSTRUCTION_TEMPLATE`)。列挙instructionなし。
- developer message: `vfl01.DEVIATION_DEVELOPER_MESSAGE`(重大誤解原則なし)。`er003`の同定数は09-27以降commitなし(`git diff`で確認)=当時と現在で同一。
- schema: `build_trial_deviation_schema("V4A", include_related_fact_id, include_origin)`(V4A標準、`same_fact_id_locations`なし)。
- model: `gpt-6-luna`、params: `reasoning={"effort": vfl01.REASONING_EFFORT}`のみ(temperature等の指定なし=コードにも記録jsonにも無い、確認)。post処理: `_apply_deviation_post_hoc_validation`→`classify_parsed_result_trial`(`severity_final`は付与されるが選別は`severity`のみ)。

### 7-2. sha一致と`safety_er009_*`不一致の原因(確認)
- 委任_06の不一致9 runの原因: er009合成fixtureは`include_related_fact_id`が**False**(er051 trial_02_runが`fixture.get("include_related_fact_id", False)`で呼ぶため`RELATED_FACT_ID_INSTRUCTION`が付かない)。委任_06の再計算は常にTrue扱いだった。
- fixtureフラグを反映して再計算した結果、reuse 26 instance(frozen run元)**26/26でsha256一致**(フラグ常時True扱いでは17/26)。委任_06の「22 run一致+9 run不一致」は同一原因(フラグ処理)で全て説明でき、未特定は0。
- developer message・paramsは保存jsonに記録がないため、コード(当時commit)と定数の不変性からの確認とする(保存データによる直接確認ではない)。

### 7-3. fresh限定確認の結果(委任_08、A構成、n=2、実費¥11.42、詳細はREPORT §65)
- 対象15 instance・32 call(30+A4補完2)、promptの`sha256`はfrozen記録と全件一致(sha比較可能な対象)。SC検出: B3 2/2、B4-a 2/2、A2A3-0 2/2、A5-0 2/2、A4-0 2/4(補完後)。neg5 B3-same 0/2、B2_hormuz HF-011 0/2。負例/NORMAL MAJOR run率 fresh 58.3%(7/12) vs rep30実使用54.5%(6/11)。claim一致率平均0.658。
- 復元差(prompt/schema/model/params)は見つからず、frozenが単発サンプルであることによるrun間変動が主因と見られる(推測)。
