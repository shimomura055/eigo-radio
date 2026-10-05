# E2E実行計画書(OPEN-233 Stage 1 ループ2、委任_14作成、実行は委任_15・Fable確認後)

管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。Trial(DEV)専用。Production未変更。本書は計画のみ(実装・API実行なし)。KPI provenance=fresh/E2E(実行時)。`APPROVED_FOR_PRODUCTION`ではない。

## 1. 構成
- Stage 1(採用): r3(3'-R) reasoning=medium + r5(5-lite full) reasoning=high + 否定案a、`STAGE1_MODE=coverage_union`、`STAGE1_ROUTES=both`、F3_PRECHECK_ALWAYS=True、H1(STAGE1_FAIL_CLOSED)=True。
  - 根拠: G arm 33 run(medium/medium)でr3 M 16/18(合格)、r5 M 15/18(基準17未達)、∪M 17/18(A4-0の1/3を両経路が見逃し、基準18未達)。r5を段階A実測(high、A4-0 3/3)へ戻した構成。**この混合構成のfresh測定は未実施**(r5 highの∪寄与は段階A保存結果からの推測)。E2Eが初のfresh測定になる。
- 後段(rep30有効構成、突合済み): 下記2節。
- 追加(rep30にない): STAGE1_MODE=coverage_union、STAGE1_ROUTES=both、F3、H1、否定案a、Stage 1 reasoning(r3 medium/r5 high)。

## 2. rep30スイッチ値の突合(`rep30_switch_values_01.md` 対 実値)
突合元: (a) `er052_output/open233_self_recovery_flow_runner_01_rep30/run_log_main.json`の`switches`(実行時実値)、(b) `er052_open233_self_recovery_flow_runner_01_rep30_full_01.py`のassert、(c) `runner.apply_kpi_trial_switches()`適用後のモジュール値(venvで実測)。
- 結果: **不一致なし(0件)**。run_log switchesに記録のある項目(mdの該当19項目+参考5項目=24項目、CAUSAL_FLOOR_VOCAB/STAGE2_NORMAL_TWO_OF_TWO含む)は全値一致。run_logに記録のないSTAGE2_DOWNGRADE_VERIFY=False、TIER0_G_L_ENABLED=False、MAX_CYCLES=2/HARD_MAX_CYCLES=3、MODEL=gpt-6-lunaは、rep30_full_01.pyのassertと`apply_kpi_trial_switches`適用後の実値(venvで実測)で一致を確認。enable_s1u=Falseは`run_instance(..., enable_s1u=False)`(rep30_full_01.py L96)で確認。
- 注意(不一致ではないが要設定): モジュール既定ではSTAGE2_VERDICT_REUSE_NONBLOCKING=False、STAGE2_SIBLING_LOCATIONS_CYCLE1=False。rep30はCLI既定onでTrueにしている。E2E起動スクリプトで明示的にTrueを設定すること(これを忘れるとrep30と構成が違う)。STAGE1_MODEの既定はlegacy_v4aのためcoverage_unionの明示設定が必須。

## 3. Rewrite後Recheckの新Stage 1仕様(Opus#16 論点8/9)
- Grep確認結果: **未実装**。`STAGE1_MODE`はrunnerで初回検出(`stage1_coverage_fresh`分岐L1814、H1 L8080)にしか効かない。cycle内のRecheck(`run_recheck` L1995、呼び出しL9200/L9213)は常に旧V4A prompt(`build_trial_prompt_template("V4A")`)を使う。coverage checkerモジュールにはRecheck用関数が無い。
- 仕様(Opus#16): 「変更された単位とその前後1単位」を再判定、Rewrite発生記事は出口前に3'-R全文1回。単位IDは位置で決まるためRewrite後は`split_units`をやり直す。
- 実装範囲見積(委任_15、Trial専用・既定不変、フラグ`STAGE1_RECHECK_COVERAGE`既定False):
  1. `coverage_changed_scope(before_text, after_text)`: split_units前後差分から変更単位+前後1単位のIDを返す純関数、約30行。
  2. `run_recheck_coverage(...)`: scope内IDだけをr3(medium)で判定し、旧Recheckと同形の戻り値(`overall_status`/`deviations`/`prior_issues_resolved`)へ変換、約60〜80行。prior_issues解消判定は既存`normalize_recheck_outcome`へ渡せる形にする。
  3. 出口前の全文3'-R 1回(Rewrite発生記事のみ、判定が新規CANDIDATEならBLOCKING候補へ合流)、約30〜40行、`run_instance`出口付近1箇所。
  4. L9200の分岐(フラグでrun_recheck/run_recheck_coverageを切替)約10行。JA側(L9213)はJA_MODE=english_onlyのため対象外。
  5. 単体テスト約8〜10件(scope計算、変換、既定OFFでの不変)。合計約150〜200行、新規関数3つ+既存呼び出し点2箇所。
- 費用影響(見込み・推測): Recheck 1回=旧V4A約¥0.17→新3'-R部分判定約¥0.1〜0.2(変更単位数依存)。Rewrite発生記事(割合は約4〜6割、rep29/iter7 summaryは23/38 run、rep30値は未集計)の出口3'-R全文が約¥0.45(r3 medium)追加。

## 4. instance構成と費用見積(残予算 ¥238−累計¥139.71=約¥98)
Opus#16推奨は約26〜30 run(SC 7+負例/NORMAL 6をn=2+hormuz系n=2)。残予算で収まる最小構成を提案する。
| 案 | 構成 | run数 | 見込み費用 mid(範囲) |
|---|---|---|---|
| 最小 | SC 6(B3/A2A3/A4/A5/B4-a/neg5)n=2=12 + NORMAL/負例6(neg1,2,3,4,6,7)n=1=6 | 18 | ¥56(43〜77) |
| 推奨 | 最小 + B2_hormuz n=2(HF-011監視) | 20 | ¥62(48〜86) |
| 拡張(任意) | 推奨 + er009 hold-out 9 n=1 | 29 | ¥74(58〜100) |
- 推奨を提案。hold-outのStage 1検出はG arm 9/9で確認済みのため、拡張は「検出後のBLOCKING保持」確認が必要とFableが判断した場合のみ。拡張は残予算ギリギリ(上限側で超過の恐れ)。
- 1 run費用見積(推測、E2E実測で置換): Stage 1新構成 約¥1.23(G arm同mix実測: r3 medium ¥0.447+段階A r5 high ¥0.785)+後段(rep30実測 ¥0.57/run、Stage 2 ¥0.285+Rewrite ¥0.10+Recheck ¥0.17、旧Stage 1初回は¥0.02で凍結再利用)+Stage 2増分(NORMAL候補約22/記事×fit¥0.064が全件Stage 2へ行く場合の上限約¥1.4、実際は不明、見込み+¥0.3〜1.4)+出口3'-R全文(Rewrite発生記事のみ約¥0.22平均)+shadow V4A約¥0.3 = **約¥3.1/run(2.4〜4.3)**。Stage 1の「high構成¥1.39/run(同mix)」に対し新構成は約¥0.16/run減(推測、混合構成は未実測)。
- worstはSC重症instance(rep30でA2A3 ¥1.43、最悪¥4.14)で¥3超が出る可能性が高い。¥6超はSTOP。

## 5. shadow測定(現行Production V4A Stage 1の費用のみ記録)
- 同一run内(初回Stage 1と同時点、同じfixture)で`trial.run_trial_deviation_check(client, ledger_text, article_text, MODEL, "V4A", include_related_fact_id=fixture.get("include_related_fact_id", False), source_article_text=fixture.get("source_article_text"))`を1回呼ぶ(provenance §7 A構成と同一)。
- **判定には使わない**(結果はcall_logにlabel=`shadow_v4a`で記録、deviationsはRewrite/Stage 2へ渡さない)。cost_jpy/usageのみ集計し、(iii)差し引き額の実測とする(見込み約¥0.3/run。KPI基準点書面は¥0.12〜0.55の仮置き)。
- 実装はE2Eスクリプト内(Production経路とは無関係)。shadow callが失敗しても本run判定に影響させない(失敗は記録、再実行しない)。

## 6. 測定項目
Human Review/STAGE4出口(件数・理由)、重大見逃し(gold SC各instance∪検出+hold-out)、Rewrite率(実行run割合、NORMAL群の不要Rewrite率)、誤BLOCKING率(NORMAL/負例でBLOCKING確定した割合)、Stage 2発動率(候補→Stage 2到達件数/記事)、cycle数分布(≥2、≥3)、平均追加費用、worst run(¥3超は全件報告)、runtime。
- 平均追加費用の表示: 主表示=(iii)「差し引き0」基準(新フロー総費用−rep30総費用)、併記=shadow実測差し引き(新−V4A実費)、rep30同基準(rep30総¥21.79/38 run=¥0.57/run)との差。(iii)基準点は`kpi_cost_baseline_open233_stage1_01.md`(Trial前固定済み、動かさない)。
- Primary KPI: Human Review 0。Safety: 重大見逃し0。Cost: 平均追加+¥2/記事以内(G arm後の見込みでは(iii)でも超過の可能性が高い。E2E実測で判定)。KPI provenance=fresh/E2E。

## 7. STOP条件
Opus#16は「E2EでHuman Reviewまたはworst run ¥3超でSTOP」としている。本計画は、Human Review/STAGE4発生は合否の不合格要因として記録しつつ集計完了まで継続し報告、worst ¥3超は全件記録(停止は¥6超)とする案を採る【Fable判断要】。以下は即停止: 1 run ¥6超、見積+30%超、API失敗3 run超、gold SCのいずれかが∪で見逃し(原因機構を分析、Prompt追加で追い込まない)、hold-outで新規見逃し、欠落ID 5%超、想定外の大量API発火、累計がGuardrail超。
- 禁止: Production正式path変更、prompt定数/gold/fixture/Safety-critical定義/Stage 2変更。委任_15は(a)Recheck新仕様実装+単体テスト(¥0)、(b)E2Eスクリプト作成、(c)見積、(d)Fable確認後に本番、の順。
