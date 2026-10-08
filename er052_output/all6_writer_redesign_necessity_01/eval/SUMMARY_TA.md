# SUMMARY_TA(T-A 集計)

## 0. run状況
総run数=48。baseline: completed=19, stop_or_fail=5 / all6: completed=19, stop_or_fail=5

### 0-1. STOP/失敗runの内訳(exit_reason)
- hormuz/b1__baseline__r1 (baseline): phase2_error: JARecheckRequiredError('[STOP] JA_RECHECK_REQUIRED: Advanced deviation MAJORのうち1件がJA R2由来(origin=ja_source)と判定されました。Englishを盲目的に再生成せず、JA側の再確認が必要です。 (ja_recheck_attempts=1、案Bで再生成後もMAJORが解
- hormuz/b2__all6__r2 (all6): phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_prior_issues_resolved=True)。本文を手で直さずSTOPします
- hormuz/b3__baseline__r1 (baseline): phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_prior_issues_resolved=True)。本文を手で直さずSTOPします
- meta/b1__baseline__r2 (baseline): phase2_error: RuntimeError('[BUDGET_GUARD] cost so far 14.08 JPY > cap 12.0 JPY. Stopping (after advanced writer+deviation).')
- meta/b2__all6__r2 (all6): phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします。')
- meta/b3__all6__r1 (all6): phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします。')
- meta/b4__baseline__r2 (baseline): phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA R2 Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_prior_issues_resolved=True)。本文を手で直さずSTOPします。')
- space_weapons/b3__all6__r1 (all6): phase2_error: JARecheckRequiredError('[STOP] JA_RECHECK_REQUIRED: Advanced deviation MAJORのうち1件がJA R2由来(origin=ja_source)と判定されました。Englishを盲目的に再生成せず、JA側の再確認が必要です。 (ja_recheck_attempts=1、案Bで再生成後もMAJORが解
- space_weapons/b3__baseline__r1 (baseline): phase2_error: RuntimeError('[BUDGET_GUARD] cost so far 12.98 JPY > cap 12.0 JPY. Stopping (after standard writer+deviation).')
- space_weapons/b4__all6__r1 (all6): phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_prior_issues_resolved=True)。本文を手で直さずSTOPします

## 1. 副指標(群別)
| 指標 | baseline | all6 |
|---|---|---|
| run数 | 24 | 24 |
| completed | 19 | 19 |
| JA Fact Check: must-fix発動(original/r2の判定単位) | 12/44 | 12/44 |
| JA Fact Check: 最終status非COMPLIANT | 0/44 | 0/44 |
| JA Fact Check or Writer内部Gate STOP(run単位) | 5/24 | 5/24 |
| EN Advanced deviation must-fix(再生成)発動 | 0/19 | 6/19 |
| Checker stage1候補数/本(平均) | 8.26 | 5.95 |
| Checker call数/本(平均) | 8.95 | 7.47 |
| Checker final_state分布 | RESOLVED_STAGE2_DOWNGRADE:12, RESOLVED_REWRITE_THEN_DOWNGRADE:7 | RESOLVED_REWRITE_THEN_DOWNGRADE:2, RESOLVED_STAGE2_DOWNGRADE:17 |
| 費用/本(¥、Writer系再計算+Checker、completed) | 9.46 | 4.29 |
| 費用 合計(¥、全run) | 222.5 | 93.8 |
| 所要時間/本(秒、completed平均) | 491.47 | 341.12 |

## 2. 盲検評価(ジャッジ=LLM単独、人間確認なし)
評価済み記事数=38(baseline 19 / all6 19)
評価者(ジャッジ)別の記事数(armとの交絡確認): gpt-5.6-luna: baseline 10 / all6 10; gpt-6-luna: baseline 9 / all6 9

### 2-1. 全体 件数(NG項目の総数)
| 区分 | 指標 | baseline | all6 | 差(all6-base) | 比(all6/base) |
|---|---|---|---|---|---|
| JA R2 | 重大件数(n=19/19) | 0 | 1 | +1 | inf |
| JA R2 | 軽微件数(n=19/19) | 10 | 7 | -3 | 0.70 |
| EN | 重大件数(n=19/19) | 1 | 1 | +0 | 1.00 |
| EN | 軽微件数(n=19/19) | 14 | 12 | -2 | 0.86 |
| R0(修正前) | 重大件数(n=19/19) | 0 | 1 | +1 | inf |
| R0(修正前) | 軽微件数(n=19/19) | 11 | 12 | +1 | 1.09 |

### 2-2. 記事あたり(平均)
| 区分 | 指標 | baseline | all6 | 差 | 比 |
|---|---|---|---|---|---|
| JA R2 | 重大/記事 | 0.00 | 0.05 | +0.05 | nan |
| JA R2 | 軽微/記事 | 0.53 | 0.37 | -0.16 | 0.70 |
| EN | 重大/記事 | 0.05 | 0.05 | +0.00 | 1.00 |
| EN | 軽微/記事 | 0.74 | 0.63 | -0.11 | 0.86 |
| 全体 | 保留/記事 | 0.05 | 0.26 | +0.21 | 5.00 |
| JA R2 | majorを1件以上含む記事の割合 | 0/19 | 1/19 | | |
| JA R2 | minorを1件以上含む記事の割合 | 9/19 | 5/19 | | |
| EN | majorを1件以上含む記事の割合 | 1/19 | 1/19 | | |
| EN | minorを1件以上含む記事の割合 | 11/19 | 9/19 | | |

### 2-3. テーマ別(件数。JA R2+EN。重大/軽微)
| テーマ | 指標 | baseline | all6 |
|---|---|---|---|
| meta | major件数(n=6/6) | 1 | 1 |
| meta | minor件数(n=6/6) | 6 | 4 |
| hormuz | major件数(n=6/7) | 0 | 0 |
| hormuz | minor件数(n=6/7) | 2 | 3 |
| space_weapons | major件数(n=7/6) | 0 | 0 |
| space_weapons | minor件数(n=7/6) | 6 | 6 |

### 2-4. 評価者(ジャッジ)別(件数/記事。JA R2+EN、重大/軽微)
| 評価者 | arm | n | 重大/記事 | 軽微/記事 | 保留/記事 |
|---|---|---|---|---|---|
| gpt-5.6-luna | baseline | 10 | 0.00 | 0.90 | 0.00 |
| gpt-5.6-luna | all6 | 10 | 0.10 | 1.00 | 0.40 |
| gpt-6-luna | baseline | 9 | 0.11 | 0.56 | 0.11 |
| gpt-6-luna | all6 | 9 | 0.00 | 0.33 | 0.11 |

### 2-5. R0->R2で初出した件数(増幅。R0に無くR2に存在=in_r0=false,in_r2=true) / EN初出(R2に無くENのみ) / R0にあってR2で解消
| 区分 | baseline | all6 |
|---|---|---|
| R2で初出(退行/増幅) | 4(重大0/軽微4) | 5(重大1/軽微4) |
| ENで初出 | 5(重大1/軽微4) | 6(重大0/軽微6) |
| R0にありR2で解消 | 5(重大0/軽微5) | 10(重大1/軽微9) |

### 2-6. NG型分布(kind、JA R2+EN存在項目)
| kind | baseline 重大 | baseline 軽微 | all6 重大 | all6 軽微 |
|---|---|---|---|---|
| subject | 0 | 1 | 0 | 3 |
| object | 1 | 0 | 0 | 0 |
| scope | 0 | 2 | 1 | 6 |
| time | 0 | 2 | 0 | 0 |
| negation | 0 | 1 | 0 | 0 |
| causal | 0 | 1 | 0 | 0 |
| added_fact | 0 | 7 | 0 | 4 |
