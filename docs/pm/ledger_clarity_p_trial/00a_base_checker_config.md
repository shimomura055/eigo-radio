# 00a ベースChecker構成の特定・固定(OPEN-233-LEDGER-CLARITY-P-TRIAL-01 委任_00a、read-only・¥0、2026-10-06)
判定: **STOP_RECOMMENDED(軽度・Fable/ユーザー判断要)**。理由は末尾。ユーザー承認は下表のDECISION_LOG行に逐語がある範囲のみ「確認」、無いものは「未確認」。

## 結論(1行)
ベース構成の管理ID=`OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01`(+Checker仕様の出自`OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02`)。設定=runner `OPEN233_APPROVED_FLOW_SWITCHES`(L496-523)。実測=`er052_output/open233_prod_e2e_02/`(9/20 run)。Status=APPROVED_FOR_PRODUCTION・**PRODUCTION_WIRED未**(DECISION_LOG L19990)。

## 4列表(runner=er052_open233_self_recovery_flow_runner_01.py、reclf=er052_open233_stage1_reclassify_01.py)
| 項目 | 管理ID/設定箇所 | ユーザー承認Evidence | 実測Evidence |
|---|---|---|---|
| (1)「Ledgerに書いていない」だけでは候補にしない | CHECKER-FLOOR-PRODUCTION-E2E-01。reclf L45規則1、runner `STAGE1_RECLASSIFY=True` L505、適用点`make_reclassify_filter`L1896 | 確認: DECISION_LOG L19987-19996(2026-10-06、指示原文「1.」を逐語引用、APPROVED_FOR_PRODUCTION)。直前に再分類Trial承認L19936 | 確認: prod_e2e_02 全9 runで`reclassify_status`あり(例 meta_run03_advanced.json L2815 "ok") |
| (2)矛盾・具体的新事実の追加を確認 | 同。reclf L40-42(3択SUPPORTED/NO_FACT_CLAIM/CANDIDATE。CANDIDATE=「Ledgerとの食い違い、または…具体的な新事実の追加」) | 確認: 同L19987-19996 | 確認: 同。Checker候補 旧151→新66(report_final/report_abcde.md) |
| (3)主体・相手先・範囲・限定条件の照合 | 同。reclf L48-53((i)主体(ii)相手先・対象(iii)対象範囲(iv)限定条件) | 確認: 同(指示原文「主体・相手先/対象・範囲・限定条件も照合する」) | 確認: 同 |
| (4)後段の機械的重大判定は数字のみ | 同。`FLOOR_MODE="number_only"` L499、`MECHANICAL_FLOOR_FLAGS=("changed_number",)` L849、`floor_fire_flags()` L855-859、`apply_floor`が使用 L2549。`PRECHECK_MODE="number_only"` L504、`PRECHECK_KINDS_NUMBER_ONLY=("number_mismatch",)` L8147 | 確認: 同(指示原文「2.」)。ただし**precheckの数字以外4種を外す点はFable解釈**(L20005(a)、ユーザーへ時間見込みは報告済み、個別逐語承認は未確認) | 確認: 全run `"FLOOR_MODE":"number_only"`(meta_run03_advanced.json L2872)。数字floor発火3(Y1/N2) |
| (5)主体・否定・比較・時期・因果は強制昇格しない | `CAUSAL_FLOOR=False` L501(モジュール既定も False L3369)、`FLOOR_VERIFY_MODE="off"` L500、`STAGE2_DOWNGRADE_VERIFY/TIER0_G_L_ENABLED=False` L502-503。`FLOOR_FLAGS`(5種)の残る参照は降格禁止/反実仮想記録(L2611 apply_floor_cited=実フロー制御に未使用、L2823 降格ガード、L2097/8177 記録)で強制重大化ではない【確認】 | 確認: 同(「数字以外の強制重大化は廃止」)。CAUSAL_FLOOR停止はL19987-19996の決定に包含 | 確認(本委任でgrep実測): prod_e2e_02/runs/*.json 9本で`changed_causality_floor`/`tier0:aux`=0件、`floor_reason`=`deterministic_floor:changed_number`のみ(meta_run03_standard/neg2/neg3) |
| (6)Stage 2等既存AI判定構成は変更しない | 承認構成のうちStage 2 V7b・S1(`STAGE2_SECOND_OPINION=True` L507)・REUSE/SIBLING L509-510は「旧E2Eから引き継ぎ」として固定(inventory表A/B) | 個別: V7b/REUSE/SIBLING/PIN/T/STAGE4許可リストはL18785(2026-10-05)の列挙で確認。**S1・disclosure_gap降格・hook_aware降格・Stage1 coverage_union系(F3/FAIL_CLOSED/否定案a)は包括またはFable判断のみ=個別逐語承認は未確認**(inventory表C) | 確認: 9 runすべて同一スイッチ(approved_switches_dump_worker1-3.json)。S1 BLOCKING化1件(N)あり |

## 現行Stage 1の問い(逐語)と案イの関係
- R3(coverage_checker L225)は現在も「少しでも疑いがあれば必ずCANDIDATEにする(迷えば候補)」。(1)(2)(3)は**R3の問いではなく、合流前の再分類filter(reclf L40-53)**で実現。
- reclf逐語: 「CANDIDATE: Ledgerとの食い違いがある、または、Ledgerにない具体的な新事実(数値・日付・固有名・因果・仕組みなど)の追加がある。」/「『Ledgerに明示されていない』だけでは CANDIDATE にしない。」
- 案イ(design_open233_stage1_loop3_prep_01.md L12。R3自体の問い転換+後段AI再確認)は議論メモで未決定のまま。DECISION_LOGに「案イ」「問いの転換」の語は0件【確認】。実際に採用されたのは別機構(reclf、RECLASSIFY-02 VALIDATED→2026-10-06ユーザー決定)。案イ=未承認・未実装として扱う。

## 注意(ベース固定時に要認識)
- 機械(決定論)候補(例 `negation_polarity_mismatch`、coverage_checker側)は再分類の対象外(DECISION_LOG(f)訂正)。HC-012見逃しはこの型(run出力 meta_run03_advanced.json L331-400)。
- reclf規則2は「数値・日付・固有名・因果・否定・比較を含む主張はLedgerと一致しない限りCANDIDATE(厳しく見る)」を含む。ユーザー(1)「書いていないだけではNGにしない」より厳しい側の補足であり、RECLASSIFY-02でVALIDATED済みの文言そのまま。
- OPEN_ITEMS L416のOPEN-233本体行ヘッダは2026-10-05時点の記述。2026-10-06のFLOOR-PRODUCTION-E2E-01はL726-728に別記載(Statusの最新化は本委任範囲外)。

## 実測Evidence(パス・run数のみ)
- 集計: `er052_output/open233_prod_e2e_02/e2e_summary_02.json`(n_done=9、failed/aborted=0、¥31.519)、`.../report_final/{report_abcde.md,critical_trace.md,label_sheet.csv}`、スイッチ`.../approved_switches_dump_worker{1,2,3}.json`、run出力`.../runs/<run_id>.json`。20 runのうち実行は9、残11 run未実行。
- 旧仕様Before(9 run、同一run id): `er052_output/open233_prod_e2e_01/baseline_old9/{report_abcde.md,.json,label_sheet.csv}`。
- metaテーマ run id(旧=baseline_old9/新=prod_e2e_02の両方に同名): meta_run03_standard、meta_run03_advanced、neg1_meta_b3prod_a2、neg2_meta_refresh_a2、neg7_meta_prodrunner_b1b。その他4 run: bgroup_B3、hormuz_run03_standard、hormuz_run03_advanced、neg3_hormuz_prodrunner_b1b。
- 「Before」の定義(旧仕様9 run vs 新仕様9 run、あるいはLEDGER-CLARITY適用前=新仕様9 run)は本委任では確定しない(Fable判断)。

## STOP_RECOMMENDED理由
1. (6)のS1/disclosure_gap/hook_aware/Stage1 coverage_union系は個別ユーザー承認逐語が未確認(包括L18785またはFable判断)。「現状ONのまま固定」は可能だが、承認済みとは言えない。
2. precheck数字以外4種の廃止はFable解釈(個別承認未確認)。
3. 案イ(R3問い転換)は未承認・未実装で、(1)-(3)はreclfで実現=ユーザー指示文と機構が一致するかの確認(上記注意の機械候補・規則2)。
(1)-(5)の設定箇所と実測はすべて特定済み。上記は「承認Evidenceなし/食い違いの可能性」に該当するため規定どおり報告。
