# design_open233_stage2_safety_downgrade_01.md(委任_67、2026-10-04)

管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`。性質: rep25(委任_66)で発生したSafety-critical B3見逃しの原因診断と対策設計。
**実装なし・Production未変更・Production未接続(`PRODUCTION_WIRED`なし)。** 診断費用 ¥5.7761(55 call予定に対し実行50 call、(b)は後述の理由で省略)。
診断の生データ: `er052_output/open233_stage2_b3_misdowngrade_diag_01/`(`results_01.json`/`results_01.md`/各run生応答)。診断スクリプト: `er052_open233_stage2_b3_misdowngrade_diag_01.py`。
区別: 「確認できたこと」はログ・実測で裏付けのあるもの、「推測」は明記する。

## §0 結論(要約)

1. 見逃しの直接原因は、Stage 2(V7b、1 call)が、Checker MAJORの因果claimをACCEPTABLEへ降格した**1回の判定のブレ(非決定性)**。floor(5フラグ)は`changed_causality`を含まないため対象外で、既存の2-of-2は「BLOCKING→降格方向」専用のため適用外。降格方向には確認がない。
2. rep25と**同一入力**(prompt sha256一致)をV7bで10回再実行すると10/10 BLOCKING、V7では9/10 BLOCKING+1/10 ACCEPTABLE。V7b文言起因ではなく、非決定性による稀な外れ(推定: 数%程度、CI幅大)。入力差・batch構成差・Stage 1差は無い(rep24 cycle 1と同一入力でBLOCKINGだった)。
3. 単独LLM判定での降格は、非決定性のため重大見逃し0と構造的に両立しない。推奨は案S1(降格の2-of-2)。費用は1記事あたり約+¥0.11〜0.15(推定、+¥2以内)。

## §1 事実の確定(rep25 bgroup_B3 s1、`er052_output/open233_self_recovery_flow_runner_01_rep25/instances_s1/bgroup_B3.json`)

### 1-1 Stage 1入力の由来(確認できたこと)

- `stage1_call_used=false`、`stage1_recall_miss_substituted=true`。`build_target_instances()`(runner 6307-6326行)の`substitute_baseline_on_stage1_miss: True`(B2_hormuz/B3)により、**Stage 1(V4A再利用)はB3を検出せず(既知recall欠落、§10/§14)、fixtureの`baseline_parsed`(V0、MAJOR検出済み)が代替投入された**。fresh Stage 1でもreuseでもなく`substitute_baseline`。
- `all_deviations_raw`: `{"stage1": [], "rechecks": []}`(代替分は生記録に出ない。`residual_at_pass.defs[0].in_checker_raw_deviations_any_severity=[]`になるのはこのため。記録上の観測性の穴であり、本件の原因ではない)。
- Stage 1 deviationの内容は**rep24 B3 cycle 1と完全一致**(claim文言・issue・severity・全flag・related_fact_id。いずれも同一baseline_parsed由来)。

### 1-2 Stage 1の出力(逐語)

- claim_in_article: `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.`
- severity: `MAJOR`、related_fact_id: `HF-007`、origin: `ja_source`、`detected_by: stage1_llm`、`auto_downgraded: false`
- flag: `changed_causality=true`、その他(`changed_fact/scope/certainty/number/actor/negation/comparison/time`、`unsupported_new_claim`)はすべてfalse。
- issue(逐語): 「継続していた攻撃・封鎖・タンカー安全への懸念が、20％案の撤回・置換や価格回復の原因だったかのように読める。Ledgerは、撤回・置換の理由としてトランプ氏が「非常に生産的な協議」を挙げたことと、供給懸念が継続していたことを確認しているが、両者の因果関係は確認していない。」
- explanation(逐語): 「同日に生じた政策転換と市場の値動き、および継続する懸念を、接続語「so」により因果関係として結び付けている。」
- `dev`フラグ: runnerの`FLOOR_FLAGS`は`changed_actor/number/negation/comparison/time`の5つ(runner 552-555行)。**`changed_causality`は含まれない**。

### 1-3 Stage 2の入力・出力

- 入力: body route(`stage2_route=body`、`section_type=in_one_line`はtitle/hook[`HOOK_ONLY_STAGE2_SECTION_TYPES`、runner 2138行]に該当せず、Hook専用Stage 2は不関与)。rubric=`BODY_RUBRIC_DEFAULT`=body rubric **V7b**(runner 447-450行)。**batchは1 claim**(`stage2_results`が1件、call_logのStage 2 callが1件)。`prompt_sha256=85f6b9852656e40cdcb162ecad45e8b5cf7e92c907c08784e62d672f2d1a3f97`。診断で保存済み入力(本文・claim・local_context・Ledger)から再構成したpromptのsha256は**一致**(診断(a)V7b全10回で一致=同一入力を再現した)。
- local_context(逐語): `## In one line\n\nConcerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart's "not over yet" movement happened on the same day.`
- 出力: `materiality=ACCEPTABLE`、`basis=none`、`rewrite_kind=replace_with_ledger_value`(正規化)、`rewrite_hint=""`。Stage 2のschemaには`explanation`欄が無く、判定理由の文章は残らない(`basis`と`rewrite_hint`のみ)。
- usage(rep25実測): input 8300 / cached 0 / output 357 / reasoning 306 tokens、¥0.1582。
- floor: `floor_reason=null`、`floor_cited_materiality=ACCEPTABLE`。hook-aware downgrade(changed_scope限定)・disclosure-gap downgrade(否定形限定)は、いずれも「BLOCKINGを下げる」処理であり、LLM判定が最初から非BLOCKINGだった本件では不関与。

### 1-4 2-of-2が適用されなかった理由(確認できたこと)

`apply_stage2_two_of_two`(runner 2928-2956行、適格判定`stage2_two_of_two_eligible` 2918-2925行)の適用条件は次の全部。

1. Stage 2の`materiality=="BLOCKING"`(**BLOCKING→降格方向のみ**。本件は最初から非BLOCKINGで対象外)
2. `floor_reason is None`
3. 追加確認(floor_verify)で解放済みでない
4. `instance_id in NORMAL_GROUP_INSTANCE_IDS`(negative7件+hormuz_run03_advanced/meta_run03_advanced。`bgroup_B3`は含まれず、**条件4でも対象外**)

つまり既存の2-of-2は「通常記事で誤ってBLOCKINGになったものを救済する」ための機構であり、**「重大(MAJOR)を非BLOCKINGへ降格する判定」を確認する機構はない**。また`floor_verify`(委任_60、`FLOOR_VERIFY_MODE=time_only`)は「LLM非BLOCKING+floorだけがBLOCKING」の解放の確認で、本件(floor不発火)は対象外。

### 1-5 SAFETY_CRITICAL_CLAIM_DEFSのB3定義とresidual_at_pass

- 定義(runner 7438-7441行): `"bgroup_B3": [{"sub_id": "B3", "related_fact_id": "HF-007", "text_substring": "flashy 20% plan"}]`。本件claimは`flashy 20% plan`を含み`HF-007`と一致し、`detect_safety_critical_misdowngrades`(runner 7510行)が最終materiality非BLOCKINGとして検出した(委任_66でSTOPの根拠)。
- rep25の`residual_at_pass`: `applicable_defs=1`、`final_state=RESOLVED_STAGE2_DOWNGRADE`、`final_state_is_pass_family=true`、B3: `remains_in_final_en=true`、`ever_blocking_flagged=false`、`ever_flagged_but_never_blocking=true`、`in_checker_raw_deviations_any_severity=[]`、`pass_with_residual_unflagged=true`(※ `pass_with_residual_unflagged`のフラグ名は、代替投入された検出が生記録に無いため`true`になる。実際にはMAJORで検出されたが降格された事例)。

### 1-6 rep24 B3 s1との差

| 項目 | rep24 B3 s1 cycle 1 | rep25 B3 s1 cycle 1 |
|---|---|---|
| Stage 1の由来 | substitute_baseline(同) | substitute_baseline(同) |
| 本文・claim文言・dev(issue/flag/severity) | 同一 | 同一 |
| batch内の他claim | なし(1 claim) | なし(1 claim) |
| rubric | V7b | V7b |
| Stage 2判定 | BLOCKING(`unsupported_relationship`、`narrow_scope`、¥0.1996) | **ACCEPTABLE**(`none`、¥0.1582、reasoning 306 tokens) |
| 以降 | Rewrite→cycle 2(「so」→「and」)→cycle 2のRecheckで再度MAJOR→Stage 2 ACCEPTABLE(Rewrite後本文、解説のみ)→合格 | cycle 1でACCEPTABLE→Rewriteなし→合格(「so」残存) |

**確認できたこと**: 入力に差は無い。差は同一入力に対するStage 2判定結果のみ(非決定性)。

## §2 既存ログ全体の集計(Rewrite前=cycle 1のStage 2判定のみ。Rewrite後cycleは除外)

集計方法: `er052_output/open233_self_recovery_flow_runner_01{,_iter2〜8,_rep7〜25}`の全instance JSON(27ディレクトリ・計475 instance JSON、同一ディレクトリ内の重複除外)を走査し、`SAFETY_CRITICAL_CLAIM_DEFS`のdefs(runner `_safety_critical_defs`、期待BLOCKINGのみ)にrelated_fact_idと`text_substring`で一致するclaimのcycle 1の`llm_materiality`(Stage 2の素の判定)と最終`materiality`を抽出。rubric版はディレクトリ名から推定(推定: iter1-7・rep7-15=R3'''、rep16=V4、iter8・rep17=V5、rep18-22=V6、rep23-25=V7b。V7は`BODY_RUBRIC_DEFAULT`として実flowで使われた版が無い[委任_55後、V7bが委任_60で既定]ため0件と推定)。

### 2-1 claim別(cycle 1のLLM判定)

| claim | 観測数 | BLOCKING | QUALITY | ACCEPTABLE |
|---|---|---|---|---|
| B3 | 35 | 28 | 6 | 1 |
| A2A3-0 | 31 | 29 | 2 | 0 |
| A4-0 | 19 | 18 | 0 | 1(floor `changed_actor`でBLOCKING維持) |
| A5-0 | 16 | 16 | 0 | 0 |
| B4-a | 11 | 11 | 0 | 0 |
| 合計 | 112 | 102 | 8 | 2 |

(委任_66の「B3同claim 39件: BLOCKING 31/QUALITY 6/ACCEPTABLE 2」は全cycle合算。cycle 1のみ=35件で、cycle 2のACCEPTABLE 1件[rep24のRewrite後本文]と、BLOCKING 3件が差。)

### 2-2 rubric版別(cycle 1、非BLOCKINGの件数/観測数)

| claim | R3''' | V4 | V5 | V6 | V7b |
|---|---|---|---|---|---|
| B3 | 4/26(QUALITY 4) | 0/2 | 2/2(QUALITY 2) | 0/2 | 1/3(ACCEPTABLE 1、rep25) |
| A2A3-0 | 0/13 | - | 2/4(QUALITY 2) | 0/4 | 0/10 |
| A4-0 | 1/11(ACCEPTABLE、floorで救済) | - | 0/2 | - | 0/6 |
| A5-0 | 0/12 | - | 0/2 | - | 0/2 |
| B4-a | 0/9 | - | - | - | 0/2 |

### 2-3 最終結果(Safety-critical claimが最終的に非BLOCKINGになった件)

最終materiality非BLOCKINGで、Rewriteなしの合格系(`RESOLVED_STAGE2_DOWNGRADE`)になったのは**9件**。B3 7件(R3''' rep7×4、V5 iter8×2、**V7b rep25×1**)、A2A3-0 2件(V5 iter8)。うち、V5までの8件は、body rubric V6(委任_33)等で是正済みと扱われていた。A4-0の1件(iter5)はfloorでBLOCKING維持のため見逃しにならず、Rewrite→合格。**現行rubric(V7b)の実flow観測23件(B3 3、A2A3-0 10、A4-0 6、A5-0 2、B4-a 2)で見逃しは1件(rep25のB3)**。

### 2-4 rep24ログでの「Checker MAJOR→Stage 2非BLOCKING」件数(費用試算の基礎)

rep24(38 instance-run)で、Checker severity=MAJORのclaim 102件(+severity無し1件)のうち、Stage 2最終が非BLOCKINGは68件(ACCEPTABLE 45、QUALITY 23)。route: body 50、hook 18。cycle別: cycle 1が62、cycle 2が6。1 instance・1 cycle・1 route(body/hook)につき1 callで確認できるため、案S1の追加callは**30 call/38 instance-run**(body 20+hook 10)。Stage 2の実測単価(rep24、45 call平均)¥0.1402。

## §3 診断測定の結果(有料、`results_01.json`)

実施: 50 call、¥5.7761、error 0。各run 生応答は`a_V7b/run_*.json`、`a_V7/run_*.json`、`c_V7b/<group>/run_*.json`。

### 3-1 (a) rep25 B3 s1と同一入力

| 版 | n | BLOCKING | 非BLOCKING | 非BLOCKING率 | 備考 |
|---|---|---|---|---|---|
| V7b(既定) | 10 | 10 | 0 | **0%** | prompt sha256がrep25と一致(10/10) |
| V7 | 10 | 9 | 1(ACCEPTABLE、run7) | **10%** | rubric違いのためsha不一致(想定どおり) |

- V7bのみで出る、という仮説は**否定**(V7bは0/10、V7で1/10)。V7b文言(「方向・時期のニュアンスの差で事実関係の核心が保たれているものは、この限りではない」)が因果claimへ波及した証拠は、diag内のV7b非BLOCKING 0件のため確認できない。rep25の実flowでのV7b 1件は、診断でV7b n=10では再現しなかったため、**低確率の確率的外れ**と判断する(推測: V7bの外れ率は数%程度。n=10の0件は「率が10%以上」を排除しないが、95%上側限界は約26%)。
- basis逐語(BLOCKING代表): V7b run1: `unsupported_relationship`、`narrow_scope`、hint「「Concerns about ... so the flashy 20% plan left the stage」を修正してください。安全上の懸念が計画撤回の理由だったという因果を削り、HF-007に沿って、トランプ氏が中東指導者との協議に基づく決定だと説明したことを記述してください。」
- 非BLOCKING回(V7 run7): `ACCEPTABLE`、`basis=none`、`rewrite_hint=""`(理由文はschemaに無く残らない)。
- **観察(確認できた相関、因果は推測)**: ACCEPTABLEになった2回は、reasoning tokensが少ない回だった(V7 run7: 262 tokens、rep25の実flow: 306 tokens)。BLOCKINGの全18回は418〜893 tokens。n=2の相関であり、「推論が浅い回に降格が出る」仮説は未検証。

### 3-2 (b) 単独batchでの測定

**省略(確認できたこと)**: rep25 B3 s1のStage 2 batchは元から1 claim(単独と同一構成)で、(a)が「同一batch構成=単独」。別途(b)を実行しても同一入力の再測定になり、不要な再測定(委任の禁止事項)になるため行わなかった。batch構成の影響は、rep25自体がbatchに他claimを含まないため**原因ではない**。

### 3-3 (c) Safety-critical残り4件+K16+K20(V7b、n=5、委任_61と同じ入力)

| group | sub_id | 期待 | n | BLOCKING | 非BLOCKING |
|---|---|---|---|---|---|
| B4 | B4-a(Safety-critical) | BLOCKING | 5 | 5 | 0 |
| A2A3 | A2A3-0(Safety-critical) | BLOCKING | 5 | 5 | 0 |
| A4 | A4-0(Safety-critical) | BLOCKING | 5 | 5 | 0 |
| A5 | A5-0(Safety-critical) | BLOCKING | 5 | 5 | 0 |
| E1_neg3 | K16(時期) | BLOCKING | 5 | 5 | 0 |
| E2_a4 | K20(動機創作、B4-a型) | BLOCKING | 5 | 5 | 0 |

(同じbatchの他claimは参考: A2A3-1 5/5 BLOCKING、A4-2 5/5 BLOCKING、A4-1・A5-1は現在の定義[A4-1=ACCEPTABLE再ラベル済み、A5-1除外済み]どおり非BLOCKING5/5、B4-d・B4-b・B4-cは非Safety-critical[現定義]。委任_61のPart Aと同じ結果。)
Safety-critical 4件+K16/K20は 0/30(非BLOCKING率0%)。ただしn=5のため「見逃し率が数%以下」を排除できない(0/30の95%上側限界約10%)。

### 3-4 診断の限界(確認できたこと)

- V7bのB3観測は、実flow 1/3(rep23-25)+診断0/10で、**1/13(約8%)**(委任_61のn=2は集計に含めていない)。Safety-critical全体ではcycle 1実flow 1/23+診断0/30+(a)0/10で、**1/63程度(約1.6%)**。いずれも信頼区間は広く、「見逃し率0」とも「数%」とも断定できない。
- 同一promptの再呼び出しの独立性は、diagの(a)で観測された範囲(V7b 10回で0、V7 10回で1)では強く矛盾しない。ただし**claimごとの難しさによる相関**がある(B3はR3'''で4/26=15%、V5で2/2など、他claimより境界例)。pが全claim共通でないため、p²の単純計算は楽観的になりうる(論点としてOpusへ)。

## §4 対策の設計(実装しない)

### 4-1 前提

Stage 2は「Checkerが重大(MAJOR)と検出した指摘を、軽微/問題なしへ降格する」権限を持つ単独のLLM判定であり、§3のとおり非決定性で一定率で重大を取りこぼす。Safety KPI(重大見逃し0)に対し、単独判定での降格は構造的に不十分(確認できたこと: 同一入力10回でV7b 0/10・V7 1/10、V7bのB3実測は1/13程度)。

### 4-2 案S1「降格の2-of-2」(推奨)

内容: Checker severity=MAJORのclaimで、Stage 2の1回目の`llm_materiality`が非BLOCKING(QUALITY/ACCEPTABLE)のときだけ、独立した2回目のStage 2呼び出し(同rubric・同入力・既定temperature)を行い、**2回とも非BLOCKINGのときだけ降格を確定**する。1回でもBLOCKINGならBLOCKING(rewrite_hintは2回目のBLOCKING判定のものを採用)。2回目のAPI失敗・schema不整合はBLOCKING(fail-closed、既存の`stage2_api_failure_failclosed`と同じ向き)。

- 実装: **既存`apply_stage2_two_of_two`の拡張ではなく、別関数**(例: `apply_stage2_downgrade_confirm`)を推奨。理由: (i)既存関数は「1回目BLOCKING→2回目で降格」の逆方向で、適用条件(NORMAL群限定・floor不発・`floor_reason is None`)が異なり、同じ関数へ入れると意味が反転して読めなくなる、(ii)Opus#8が指摘した落とし穴(`run_stage2`を呼び直すと`apply_floor`が再適用され、2回目の`materiality`が常にBLOCKINGになる)を避けるため、判定は**必ず`llm_materiality`で比較**する、(iii)floor・hook-aware・disclosure-gap降格は「BLOCKINGを下げる」処理でLLM非BLOCKINGの本件構造とは別のため、これらの結果には触れない(2回目はLLM判定のみを取り、後段の既存処理はそのまま)。共通の内部呼び出し(`run_stage2`のbody/hookグループ呼び出し)は再利用してよい。
- 対象claimの絞り込み: `dev.severity=="MAJOR"`、`llm_materiality!="BLOCKING"`、最終`materiality!="BLOCKING"`(floor等で既にBLOCKINGのものは不要)、precheck floor claim(Stage 2非経由)は対象外、floor_verifyで解放済みのclaim(`floor_verify.released`)は既存の2回確認で扱い済みのため対象外(要Opus確認)。
- 呼び出し粒度: instance・cycle・route(body/hook)ごとに、対象claimを1 batchで1 call(最大2 call/cycle)。
- 結果の扱い: 2回目も非BLOCKINGなら、1回目の判定をそのまま維持(`materiality`は軽い方を採用せず、2回のうちBLOCKINGに近い方=重い方を採用するのが安全側。例: 1回目QUALITY、2回目ACCEPTABLEなら重いQUALITYを維持)。
- ログ: 新規keyを追加(`stage2_downgrade_confirm_log`)、既存`stage2_two_of_two_log`は不変。
- 重大見逃しへの効果(試算、独立の仮定): 1回判定の見逃し率をpとすると見逃し率はp²。診断データ: B3 p≈8%(1/13)なら約0.6%、Safety-critical全体 p≈1.6%(1/63)なら約0.03%。pの上限(B3 1/13の95%上側限界約36%)なら約13%。**0にはならない**(KPIは「構造的に0」ではなく「確率的に極小」)。claim難易度による相関があればp²より大きくなる。
- 過剰Major・不要Rewrite・Human Reviewへの影響: 降格が減る方向のみで、新しいBLOCKING判定の基準は追加しない(過剰Majorを増やす経路は「2回目だけBLOCKING」の揺れに限られる)。ただし、**増える可能性はゼロではない**: rep24の68件(ACCEPTABLE 45/QUALITY 23)のうち、2回目がBLOCKINGを出すclaimはRewrite対象になる。2回目のBLOCKING率qは**未測定**(下記・次工程の限定測定が必要)。Rewriteは既存のラダー(narrow_scope等)で、Human Review増加の見込みは「Rewriteが増えた結果のEscalation」に限られる。
- 費用(rep24ログ、確認できた数値からの試算): 追加30 call×実測単価¥0.1402=約¥4.2/38 instance-run(=約¥0.11/instance-run、29記事分母なら約¥0.145/記事)。q=10〜30%ならRewrite追加(推定: 1 Rewriteあたり約¥0.5〜0.8)で、さらに+約¥0.1〜0.3/記事(推定)。**合計でも+¥2/記事の範囲内(推定)**。診断(rep25)の実測では、cacheが効く場合の単価は約¥0.075(2回目は入力がほぼ同一でcacheされる可能性があり、実費はこれより小さくなりうる)。
- cycleごと/Recheck由来: Stage 2はcycleごとに呼ばれるため、S1もcycleごとに適用(Recheckで出たMAJORも同じ)。rep24の68件のうち6件がcycle 2(Rewrite後)。
- floor_verify/既存2-of-2との相互作用: 対象集合は互いに排他的(既存2-of-2=1回目BLOCKING、floor_verify=floorだけBLOCKING、S1=1回目LLM非BLOCKING)。既存2-of-2が降格した結果(1回目BLOCKING→2回目非BLOCKING)は1回目がBLOCKINGのためS1の対象外。ただし、**NORMAL群の2-of-2は「1回でも非BLOCKINGなら降格」で、S1と向きが逆**。Productionに「NORMAL群」という概念は無い(`NORMAL_GROUP_INSTANCE_IDS`は評価用の正解ラベル付きinstance集合)ため、Production配線時にS1(全MAJOR対象)と既存2-of-2(Normal群限定)をどう整合させるかは未決(論点7、Opus確認事項)。
- Production配線時の対応箇所(参考、実装しない): runner `run_stage2`(2689行)の後段、`apply_stage2_two_of_two`呼び出し直後(6810-6812行付近)、およびACCEPTABLE_STAGE1経路(6732行付近、要確認)。Production正式path側の対応は別途設計が必要。

### 4-3 案S2「Safety-critical相当の決定論ガード」(参考、推奨しない)

因果接続(`so`/`because`/`therefore`/`as a result`/`led to`等)でLedgerに因果が無い場合を、floor(`changed_causality`)として機械的に追加する案。
- 重大見逃しへの効果: 因果claimには決定論的に効く(本件も防げる)が、`changed_causality`はStage 1(LLM)のフラグであり、決定論は「Stage 1が因果を立てた後の降格防止」にすぎず、Stage 1の取りこぼし(recall miss、B3は既に代替投入)には効かない。
- 問題: (i)**新しい機械的安全装置の追加はユーザー判断事項**(ユーザー指示2026-10-03「機械的な安全装置については今回の採用内容だけを理由に勝手に緩めない」の逆方向だが、新設自体がSafety原則の変更に当たる)、(ii)因果のMAJOR(Checker)が全て重大とは限らず(例: neg5「So the flashy 20% plan left the stage.」はStage 2でACCEPTABLEと判定される自然な文)、**過剰Major・不要Rewrite・Human Reviewを増やす恐れが大きい**、(iii)Primary KPI(Human Review 0)に反する可能性、(iv)決定論floorの字面判定は、Opus#8が「K13・K14型を字面で区別できない」と指摘した問題と同型。→ 推奨しない。

### 4-4 案S3「V7b文言の限定」(診断により不要)

「この限りではない」の適用範囲を比較・時期の語に限定する案。診断(a)でV7bの非BLOCKINGは0/10でV7b文言起因の証拠が無いため、**今回は採用しない**。単独では効果の証拠が無く、rubric文言の変更は再較正(¥10〜30)を要する。S1と併用する必要もない。

### 4-5 案S4(参考): 2回目を別prompt化(反対尋問型)、3回多数決

2回目を「この文に、読者が重大な誤解をする読み方はあるか」と問う別promptにして独立性を高める案、および2-of-3等。独立性は上がる可能性があるが、**新promptはChecker/rubric変更に当たりPrompt・Schema変更禁止の範囲外**、かつ再較正が必要で、非決定性を増やす。S1で足りるか判断した後の次の段階として、Opusが必要と判断する場合のみ検討(今回は設計のみ)。

### 4-6 比較表

| 案 | 重大見逃しへの効果 | 過剰Major/不要Rewrite/HR | 追加費用(推定) | ユーザー承認 |
|---|---|---|---|---|
| S1 降格2-of-2 | p→p²(B3 8%→約0.6%、全体1.6%→約0.03%) | 降格が減るのみ。2回目だけBLOCKINGの揺れ(q未測定)分がRewriteへ | 約+¥0.11〜0.45/記事(推定) | 要(既存より厳しい) |
| S2 決定論ガード | 因果に決定論で効くがStage 1 recallには無効 | 増える恐れ大 | ほぼ0 | 要(新規安全装置) |
| S3 V7b文言限定 | 証拠なし(V7b 0/10) | - | 再較正¥10〜30 | 要(rubric変更) |
| S4 別prompt/多数決 | 独立性は上がる可能性 | 不明 | S1以上 | 要(Prompt変更) |
| 単独のまま(現状) | 見逃し率p(約1.6〜8%)が残る | - | 0 | - |
| 参考: MAJORは降格不可 | 見逃し0に最も近い | **rep24で68/102 MAJORがRewriteへ**(Rewrite嵐、Human Reviewが大きく増える。Primary KPIに反する) | 大 | - |

### 4-7 推奨と理由(KPI 3つ同時)

- **推奨: S1**。Safety(重大見逃し0): 見逃し率がpからp²へ(確率的に約1/13〜1/60)。Primary(HR 0): 降格が減るだけで、新しい判定基準を追加しない。Rewriteの増加はq次第(未測定)でありHR増の経路は既存ラダー内に限られる。Cost(+¥2以内): 追加は約¥0.11〜0.45/記事(推定)。
- **S1は既存より厳しくする変更**(降格が減る)であり、Safety KPI 0件のための対策。Production採用にはユーザー承認が必要(`USER_DECISION_REQUIRED`候補、下記)。
- 診断で確認できなかったこと: 2回目だけBLOCKINGになるqの実測(S1導入後に不要Rewrite/Escalationが増えるか)。実装前に、rep24の68件(または代表を抽出した限定入力)に対する2回目判定を限定測定する必要がある(次委任、概算30 call=約¥4)。
- 0%を保証しない点: S1でも約1/13のpが相関すればp²≠0。ユーザーKPI「0件」は確率的な極小化として扱う旨の確認が必要。

## §5 USER_DECISION候補

1. 降格の2-of-2(案S1)を、既存より厳しくする変更として検証用runnerへ実装・限定再確認してよいか(Opus条件A後)。
2. 「重大Fact見逃し0件」を、構造的な保証(決定論)ではなく、確率的な極小化(p→p²)として扱ってよいか。決定論floor(案S2)は過剰Majorとの両立が難しい。
3. NORMAL群の既存2-of-2(「1回でも非BLOCKINGなら降格」)とS1(「2回とも非BLOCKINGでなければ降格しない」)の関係を、Production配線時にどう整理するか(Production側にNORMAL群概念が無い)。

## §6 参考: 確認できたことと推測

- 確認できたこと: §1全項(rep25 JSON・runnerコード・call_log)、§2の集計(JSON走査、rubric版はdir名から推定)、§3(実測50 call)。
- 推測: 見逃し率pの値(CIが広い)、「reasoning tokensが少ない回に降格が出る」仮説、Rewrite追加費用(約¥0.5〜0.8/回)、q、S1の費用(¥0.11〜0.45/記事)。
