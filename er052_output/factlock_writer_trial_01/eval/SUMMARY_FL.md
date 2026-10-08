# SUMMARY_FL(3セル同一パック。しきい値なし・有意性は主張しない)

## 0. run状況
- baseline: 24本、completed=19、STOP/失敗=5
- all6: 24本、completed=19、STOP/失敗=5
- factlock: 24本、completed=19、STOP/失敗=5
  - factlock/hormuz/b1/r2: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします
  - factlock/meta/b1/r1: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします
  - factlock/meta/b1/r2: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします
  - factlock/meta/b4/r1: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=True)。本文を手で直さずSTOPします。
  - factlock/space_weapons/b4/r2: phase2_error: JARecheckRequiredError('[STOP] JA_RECHECK_REQUIRED: Advanced deviation MAJORのうち1件がJA R2由来(origin=ja_source)と判定されました。Englishを盲目的に再生成せず、JA側の再確認が必要です
  - all6/hormuz/b2/r2: phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_pri
  - all6/meta/b2/r2: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします
  - all6/meta/b3/r1: phase2_error: RuntimeError('[STOP] Advanced deviation check: 再生成後もMAJOR、または前回指摘の未解消あり(retry_for_deviation=True, all_prior_issues_resolved=False)。本文を手で直さずSTOPします
  - all6/space_weapons/b3/r1: phase2_error: JARecheckRequiredError('[STOP] JA_RECHECK_REQUIRED: Advanced deviation MAJORのうち1件がJA R2由来(origin=ja_source)と判定されました。Englishを盲目的に再生成せず、JA側の再確認が必要です
  - all6/space_weapons/b4/r1: phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_pri
  - baseline/hormuz/b1/r1: phase2_error: JARecheckRequiredError('[STOP] JA_RECHECK_REQUIRED: Advanced deviation MAJORのうち1件がJA R2由来(origin=ja_source)と判定されました。Englishを盲目的に再生成せず、JA側の再確認が必要です
  - baseline/hormuz/b3/r1: phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_pri
  - baseline/meta/b1/r2: phase2_error: RuntimeError('[BUDGET_GUARD] cost so far 14.08 JPY > cap 12.0 JPY. Stopping (after advanced writer+deviation).')
  - baseline/meta/b4/r2: phase1_error: RuntimeError('[STOP] JA_FACT_CHECK_STOP: JA R2 Fact Check、must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました(overall_status=LEDGER_DEVIATION, all_prior_iss
  - baseline/space_weapons/b3/r1: phase2_error: RuntimeError('[BUDGET_GUARD] cost so far 12.98 JPY > cap 12.0 JPY. Stopping (after standard writer+deviation).')

## 1. 副指標(セル別)
| 指標 | baseline(5.6現行) | all6(6現行) | factlock(6+FL) |
|---|---|---|---|
| run数/completed | 24/19 | 24/19 | 24/19 |
| JA FC must-fix発動(判定単位) | 12/44 | 12/44 | 6/48 |
| JA FC 最終非COMPLIANT | 0/44 | 0/44 | 0/48 |
| STOP/失敗(run単位=STOP率) | 5/24 | 5/24 | 5/24 |
| EN deviation再生成発動 | 0/19 | 6/19 | 0/19 |
| Checker stage1候補/本 | 8.26 | 5.95 | 4.68 |
| Checker call数/本 | 8.95 | 7.47 | 6.84 |
| Checker final_state | RESOLVED_STAGE2_DOWNGRADE:12, RESOLVED_REWRITE_THEN_DOWNGRADE:7 | RESOLVED_REWRITE_THEN_DOWNGRADE:2, RESOLVED_STAGE2_DOWNGRADE:17 | RESOLVED_STAGE2_DOWNGRADE:18, RESOLVED_REWRITE_THEN_DOWNGRADE:1 |
| 費用/本(Writer系再計算+Checker、全run平均、照合分は含まず※) | 9.27 | 3.91 | 4.94 |
| 費用 合計(JPY) | 222.5 | 93.8 | 118.5 |
| 所要時間/本(秒、全run平均。並列度は同一でない可能性あり) | 458 | 313 | 410 |

※ factlockの照合(LLM)は raw_usage_log に含まれるため再計算費用に含む(別掲が必要な場合は stage名で分離)。

## 2. 盲検評価(LLM単独判定、人間確認なし)
評価済み: baseline 24, all6 24, factlock 24
評価者別配分: gpt-5.6-luna: baseline12/all612/factlock12; gpt-6-luna: baseline12/all612/factlock12

本文の到達状況(STOP記事を母数に含めるが、生成されなかった段は評価対象外=NG0として現れる点に注意): baseline: R0有22/R2有22/EN有21(全24); all6: R0有22/R2有22/EN有19(全24); factlock: R0有24/R2有24/EN有19(全24)

### 2-1. 件数と記事あたり(factlock対all6 / factlock対baseline)
| 区分 | 指標 | baseline | all6 | factlock | FL-all6 | FL/all6 | FL-base | FL/base |
|---|---|---|---|---|---|---|---|---|
| JA R2 | 重大(件) | 0 | 1 | 0 | -1 | 0.00 | +0 | - |
| JA R2 | 重大/記事(分母=その段の本文がある記事: 22/22/24) | 0.00 | 0.05 | 0.00 | -0.05 | 0.00 | +0.00 | nan |
| JA R2 | 軽微(件) | 12 | 7 | 5 | -2 | 0.71 | -7 | 0.42 |
| JA R2 | 軽微/記事(分母=その段の本文がある記事: 22/22/24) | 0.55 | 0.32 | 0.21 | -0.11 | 0.65 | -0.34 | 0.38 |
| EN | 重大(件) | 1 | 1 | 0 | -1 | 0.00 | -1 | 0.00 |
| EN | 重大/記事(分母=その段の本文がある記事: 21/19/19) | 0.05 | 0.05 | 0.00 | -0.05 | 0.00 | -0.05 | 0.00 |
| EN | 軽微(件) | 17 | 13 | 6 | -7 | 0.46 | -11 | 0.35 |
| EN | 軽微/記事(分母=その段の本文がある記事: 21/19/19) | 0.81 | 0.68 | 0.32 | -0.37 | 0.46 | -0.49 | 0.39 |
| R0 | 重大(件) | 1 | 1 | 1 | +0 | 1.00 | +0 | 1.00 |
| R0 | 軽微(件) | 11 | 8 | 4 | -4 | 0.50 | -7 | 0.36 |
| 全体 | 保留/記事 | 0.46 | 0.33 | 0.21 | -0.12 | | -0.25 | |
| JA R2 | majorを1件以上含む記事 | 0/24 | 1/24 | 0/24 | | | | |
| JA R2 | minorを1件以上含む記事 | 11/24 | 6/24 | 5/24 | | | | |
| EN | majorを1件以上含む記事 | 1/24 | 1/24 | 0/24 | | | | |
| EN | minorを1件以上含む記事 | 12/24 | 11/24 | 5/24 | | | | |

### 2-2. テーマ別(JA R2+EN。重大/軽微 件数)
| テーマ | 指標 | baseline | all6 | factlock |
|---|---|---|---|---|
| meta | major | 1(n=8) | 0(n=8) | 0(n=8) |
| meta | minor | 8(n=8) | 4(n=8) | 3(n=8) |
| hormuz | major | 0(n=8) | 0(n=8) | 0(n=8) |
| hormuz | minor | 5(n=8) | 6(n=8) | 3(n=8) |
| space_weapons | major | 0(n=8) | 1(n=8) | 0(n=8) |
| space_weapons | minor | 6(n=8) | 4(n=8) | 2(n=8) |

### 2-3. 評価者別(件数/記事。JA R2+EN)
| 評価者 | セル | n | 重大/記事 | 軽微/記事 | 保留/記事 |
|---|---|---|---|---|---|
| gpt-5.6-luna | baseline | 12 | 0.08 | 0.67 | 0.67 |
| gpt-5.6-luna | all6 | 12 | 0.08 | 0.67 | 0.25 |
| gpt-5.6-luna | factlock | 12 | 0.00 | 0.33 | 0.25 |
| gpt-6-luna | baseline | 12 | 0.00 | 0.92 | 0.25 |
| gpt-6-luna | all6 | 12 | 0.00 | 0.50 | 0.42 |
| gpt-6-luna | factlock | 12 | 0.00 | 0.33 | 0.17 |

### 2-4. R2初出(R0に無くR2に存在)/ EN初出 / R0にありR2で解消
| 区分 | baseline | all6 | factlock |
|---|---|---|---|
| R2で初出(退行) | 5(重大0/軽微5) | 6(重大1/軽微5) | 1(重大0/軽微1) |
| ENで初出 | 8(重大1/軽微7) | 7(重大0/軽微7) | 3(重大0/軽微3) |
| R0にありR2で解消 | 5(重大1/軽微4) | 7(重大1/軽微6) | 1(重大1/軽微0) |
| R0に存在(重大+軽微) | 12(重大1/軽微11) | 9(重大1/軽微8) | 5(重大1/軽微4) |

### 2-5. NG型分布(kind。JA R2+EN存在項目。重大/軽微)
| kind | baseline | all6 | factlock |
|---|---|---|---|
| subject | 1/0 | 0/3 | 0/2 |
| object | 0/0 | 0/0 | 0/0 |
| scope | 0/10 | 0/5 | 0/5 |
| time | 0/1 | 0/0 | 0/0 |
| negation | 0/0 | 0/0 | 0/0 |
| causal | 0/4 | 0/2 | 0/0 |
| added_fact | 0/4 | 1/4 | 0/1 |

### 2-6. STOP/未完了runの評価結果(母数に含む)
- factlock/meta/b4/r1: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微0
- factlock/meta/b1/r1: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微0
- factlock/space_weapons/b4/r2: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微1
- all6/space_weapons/b4/r1: 到達段  / 重大0・軽微0
- baseline/hormuz/b3/r1: 到達段  / 重大0・軽微0
- baseline/meta/b1/r2: 到達段 original.md,revision1.md,revision2.md,article.md / 重大0・軽微2
- all6/space_weapons/b3/r1: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微0
- factlock/hormuz/b1/r2: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微1
- baseline/hormuz/b1/r1: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微1
- baseline/space_weapons/b3/r1: 到達段 original.md,revision1.md,revision2.md,article.md / 重大0・軽微0
- all6/meta/b3/r1: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微1
- all6/meta/b2/r2: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微0
- factlock/meta/b1/r2: 到達段 original.md,revision1.md,revision2.md / 重大0・軽微0
- baseline/meta/b4/r2: 到達段  / 重大0・軽微0
- all6/hormuz/b2/r2: 到達段  / 重大0・軽微0

## 3. 面白さ pairwise(副指標。6-luna LLM判定、順序入替2回、24対x2=48判定、人間確認なし)
勝敗(判定単位): factlock 13 / all6 35 / tie 0(位置バイアス確認 A:17 B:31 tie:0)
brief対単位(2回とも同方向): {'factlock一貫': 3, 'all6一貫': 14, '割れ/引分': 7}(n=24)

理由の抜粋(factlockが負けた判定の理由先頭8件):
- factlock/hormuz/b1/r2: 冒頭の「二割の数字は出た。説明書はない」が引きになり、相場の動きと海上の懸念も順を追って説明されていて、ラジオで聞きやすいです。Aは「幕」「探偵」「衣替え」「映画の筋書き」と比喩が重なり、話し言葉として少し作り込みすぎに感じます。
- factlock/hormuz/b1/r2: Aは「数字は派手に登場したのに、制度の説明書はまだ見当たらない」など、耳に残る表現を使いながら話の流れが自然です。Bは引き込もうとする工夫はありますが、ショー・探偵・映画の比喩が重なり、「相場が追っていた手がかり」などもやや不自然です。
- factlock/hormuz/b2/r1: Bはニュースの流れを順に追いながら、相場がすぐ落ち着かなかった理由も自然に説明していて、聞き手が内容をつかみやすいです。Aは舞台や衣装の比喩が重なり、少し作り込まれた印象になるうえ、同じ結論の繰り返しも目立ちます。
- factlock/hormuz/b3/r1: 舞台の比喩を軸にしつつ、出来事の順番と値動きが整理されていて、ラジオで聞いても追いやすいです。Aは比喩が重なり、「舞台の真ん中で値動きを見せる役」「衣装替えした料金案」などの表現がやや窮屈に感じられます。
- factlock/hormuz/b3/r2: 冒頭でニュースの見どころを示し、翌日の変化から原油相場へと順に進むため、ラジオ記事として流れを追いやすく引き込まれます。Aは「開幕」「舞台」「衣装」「幕」と比喩が重なり、少し窮屈に感じます。
- factlock/hormuz/b4/r1: 舞台の比喩を「主役交代」「降板」「退場」と一貫して使い、短い文や問いかけもあってラジオ記事として引き込まれます。Aは「投稿された日」「清算されました」など硬い表現が混じり、比喩も重なって少し窮屈に感じます。
- factlock/hormuz/b4/r1: 舞台の比喩を冒頭から結びまで一貫して使い、相場の動きを自然な話し言葉で追えるため、聞きやすく引き込まれます。Bは説明が具体的な一方、「舞台」「小道具」「代役」「カード」と比喩が重なり、「料金案が投稿された日」など硬く不自然な表現もあります。
- factlock/hormuz/b4/r2: 日付や価格を交えながら展開を順に追うため、何が起きたかが分かりやすく、ラジオ記事として引き込まれます。比喩はやや多めですが、Aより話の流れが自然で、結びまでまとまっています。
