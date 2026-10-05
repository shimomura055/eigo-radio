# 段階A候補の内訳とStage 2負荷見込み(委任_09、¥0)

KPI provenance: 既存fresh出力(段階A 42 run、rep30)の再集計。E2Eではない。

## 1. 候補の発生源(1 runあたり平均)

| 群 | run | 判定単位 | 候補∪ | LLM両経路 | LLM r3のみ | LLM r5のみ | 決定論のみ | 候補/単位 |
|---|---|---|---|---|---|---|---|---|
| B2watch | 3 | 28.0 | 13.33 | 2.33 | 3.33 | 0.33 | 7.33 | 0.476 |
| SC | 18 | 28.33 | 17.83 | 5.5 | 8.22 | 0.11 | 3.89 | 0.629 |
| NORMAL | 12 | 31.17 | 24.0 | 8.17 | 10.92 | 0.67 | 4.25 | 0.77 |
| holdout | 9 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 |

instance別(平均/run、union・r3・r5・判定単位)

| instance | n | 判定単位 | r3 | r5 | ∪ |
|---|---|---|---|---|---|
| bgroup_B2_hormuz | 3 | 28.0 | 14.0 | 6.0 | 13.33 |
| bgroup_B3 | 3 | 27.0 | 9.67 | 1.0 | 9.67 |
| bgroup_B4 | 3 | 26.0 | 23.0 | 10.33 | 23.33 |
| neg1_meta_b3prod_a2 | 2 | 38.0 | 33.5 | 12.5 | 33.5 |
| neg2_meta_refresh_a2 | 2 | 33.0 | 22.5 | 5.5 | 23.0 |
| neg3_hormuz_prodrunner_b1b | 2 | 20.0 | 13.5 | 7.0 | 14.0 |
| neg4_smallbag_div_a2 | 2 | 36.0 | 25.5 | 27.5 | 27.0 |
| neg5_hormuz_div_a2 | 3 | 38.0 | 12.67 | 1.33 | 12.0 |
| neg6_smallbag_div_b1b | 2 | 26.0 | 19.0 | 20.0 | 20.5 |
| neg7_meta_prodrunner_b1b | 2 | 34.0 | 27.0 | 10.5 | 26.0 |
| safety_A2A3 | 3 | 22.0 | 14.0 | 7.33 | 14.0 |
| safety_A4 | 3 | 27.0 | 24.33 | 15.67 | 24.0 |
| safety_A5 | 3 | 30.0 | 24.0 | 6.67 | 24.0 |
| safety_er009_changed_actor | 1 | 1.0 | 1.0 | 3.0 | 1.0 |
| safety_er009_changed_causality | 1 | 1.0 | 1.0 | 1.0 | 1.0 |
| safety_er009_changed_certainty | 1 | 1.0 | 1.0 | 2.0 | 1.0 |
| safety_er009_changed_comparison | 1 | 1.0 | 1.0 | 1.0 | 1.0 |
| safety_er009_changed_negation | 1 | 1.0 | 1.0 | 1.0 | 1.0 |
| safety_er009_changed_number | 1 | 1.0 | 1.0 | 1.0 | 1.0 |
| safety_er009_changed_scope | 1 | 1.0 | 1.0 | 2.0 | 1.0 |
| safety_er009_changed_time | 1 | 1.0 | 1.0 | 2.0 | 1.0 |
| safety_er009_unsupported_new_claim | 1 | 1.0 | 1.0 | 2.0 | 1.0 |

全発生源(候補総数): {'LLM_both(r3+r5)': 213, 'LLM_r3only': 289, 'deterministic_only': 143, 'orphan(unknown_unit_id)': 2, 'LLM_r5only': 11}
決定論で戻した理由(r3経路): {'quote_not_in_ledger': 4, 'negation_polarity_mismatch': 149}
SUPPORTED割合(r3、決定論後/前): 0.329/0.485。r5: MATCH 0.519、UNMENTIONED(対応factなし) 0.235
LLM候補513件のフラグ分布: {'unsupported_new_claim': 456, 'changed_fact': 311, 'changed_scope': 246, 'changed_certainty': 147, 'changed_causality': 107, 'changed_time': 59, 'changed_comparison': 52, 'changed_actor': 49, 'changed_negation': 16, 'changed_number': 8}
issueあり率 1.0(平均72.14字)、related_fact_idあり 0.963、claim_in_articleあり 1.0
汎用フラグ(changed_fact/unsupported_new_claim/changed_scope)のみの候補: 0.398、フラグなし: 0.0

## 2. NORMAL 6 instance先頭5候補(30件、s1)のラベル(推測)

{'U': 20, 'R': 4, 'N': 6}、割合{'U': 0.667, 'R': 0.133, 'N': 0.2}。ラベルは推測(目視相当)。gold変更ではない。R=真の逸脱(軽微含む) N=自然な推論・言い換え U=迷って候補(事実主張が薄い導入・修辞・見出し・評価語)

| instance | unit | ラベル | claim |
|---|---|---|---|
| neg1_meta_b3pr | T | U | # We Thought It Was AI—But There Was a Person Inside Meta’s Muse |
| neg1_meta_b3pr | S1.1 | U | Ring, ring. |
| neg1_meta_b3pr | S1.2 | U | A call seemed to come from an AI agent. |
| neg1_meta_b3pr | S1.3 | R | But as the conversation went on, the voice was not AI at all. |
| neg1_meta_b3pr | S1.4 | N | It was a person. |
| neg2_meta_refr | S1.1 | U | There was a small twist. |
| neg2_meta_refr | S1.4 | N | This was part of a test. |
| neg2_meta_refr | S2.4 | U | If AI can handle difficult phone calls, it seems very useful. |
| neg2_meta_refr | S3.1 | N | But in some tests of its calling feature, trained human contract worke |
| neg2_meta_refr | S3.2 | N | They spoke with people until each conversation ended. |
| neg3_hormuz_pr | T | U | # The 20 Percent Fee Plan Is Withdrawn—But Oil Prices Quickly Return |
| neg3_hormuz_pr | S1.1 | U | Oil-price news sometimes gets its biggest twist not from a policy anno |
| neg3_hormuz_pr | S2.1 | N | On July 13, Trump posted that all cargo passing through the Strait of  |
| neg3_hormuz_pr | S2.2 | U | A large number suddenly appeared, making the proposal the story’s new  |
| neg3_hormuz_pr | H2 | U | ### The price refuses to follow |
| neg4_smallbag_ | T | U | # Bags Split the Job: Mini Bags Catch the Eye, Large Bags Carry the Lo |
| neg4_smallbag_ | S1.2 | U | Palm-sized clutches, small pouches, and eye-catching minaudières fill  |
| neg4_smallbag_ | S1.3 | U | Some are so small that you might ask, “Can you really fit anything in  |
| neg4_smallbag_ | S2.1 | R | But mini bags are not taking over. |
| neg4_smallbag_ | S2.2 | R | They are not pushing large bags away. |
| neg6_smallbag_ | T | U | # Bags Split the Job: Mini Bags Draw the Eye, Large Bags Carry the Loa |
| neg6_smallbag_ | S1.1 | N | Looking at fashion for 2026, mini bags are having a big moment. |
| neg6_smallbag_ | S1.2 | U | Palm-sized clutches, small pouches, and eye-catching minaudières are a |
| neg6_smallbag_ | S1.3 | U | Some are so small that you might ask, “Can you really fit anything in  |
| neg6_smallbag_ | S2.1 | R | But this is not a takeover, with mini bags pushing large bags out. |
| neg7_meta_prod | T | U | # It Was Supposed to Be an AI Call—Then a Human Appeared Backstage |
| neg7_meta_prod | S1.4 | U | In this convenient future, the AI on your screen handles everything fo |
| neg7_meta_prod | S2.2 | U | So it sounds like a simple story: you make a request, and AI takes car |
| neg7_meta_prod | S2.3 | U | But the picture changed once people looked behind the stage. |
| neg7_meta_prod | H1 | U | ### The call that was not made by AI |

## 3. negation_polarity_mismatch

発火149件(unique 70)。誤発火率(FP分類)=0.987、確定した真の極性不一致=0

| 分類 | 件数(全発火) |
|---|---|
| FP:字面(「ほどなく」の『なく』) | 60 |
| FP:対比構文(「AIではなく人間が」。単位は肯定側を述べており矛盾なし) | 40 |
| FP:修飾語(「意図せず共有」の『せず』。極性反転なし) | 21 |
| FP:マーカー欠落(日本語『なし(に)』が否定語リストに無い。withoutと整合) | 15 |
| FP:言語不整合(factが英語Ledgerで日本語否定語しか検査しない構造) | 4 |
| FP:英語動詞(disliked)で否定を表現、否定語リストに無い | 3 |
| FP:情報欠如の言い換え(単位はonly等で同義。極性反転なし) | 3 |
| PLAUSIBLE_TRUE(推測):単位の否定・留保がfactに無い。ただし極性反転ではなく『Ledgerに無い主張/留保』で、第1support factのみでの検査 | 2 |
| FP:慣用句(not only A but also B)は否定ではない | 1 |

確認=発火単位と第1support factの否定語(JA marker/EN regex)を実際に列挙し70 unique件を目視。極性反転の確定例は0。推測=PLAUSIBLE_TRUE 2種は極性反転ではなく『Ledgerに無い留保』。第1support factのみでの再現(全support factではない)

## 4. Stage 2負荷・KPI見込み

候補24/記事: Stage 2費用 線形fit ¥1.851/記事(cap10なら¥0.829)。rep30のBLOCKING率 全体0.289(35/121)、NORMAL 0.1(2/20)。
期待BLOCKING/記事: 保守(NORMAL率)2.4、保守(全体率)6.94、サンプルのR割合のみBLOCKINGなら3.2。0件(Rewriteなし)になる確率(Poisson近似): 0.091/0.041。
rep30: cycles>=2が4/38 run、Rewriteあり20 run、NORMALのRewrite {'neg1_meta_b3prod_a2': [0, 0], 'neg2_meta_refresh_a2': [0, 0], 'neg3_hormuz_prodrunner_b1b': [1, 1], 'neg4_smallbag_div_a2': [0], 'neg6_smallbag_div_b1b': [0], 'neg7_meta_prodrunner_b1b': [0]}。Rewrite+Recheck費用(Stage 2除く)≒¥0.314/Rewrite。fitは候補範囲[0,10]、24への外挿。線形とcap10の2通りを併記

| 群 | run | 平均候補 | Stage1 fresh | rep30費用(照合) | Stage2新(線形) | 追加BLOCKING | 合計/run(線形) | rep24比(線形) | rep24比(cap10) | rep24比(下限=Stage1のみ) |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 42 | 15.667 | 1.508 | 0.889 | 1.243 | 2.091 | 3.899 | +3.458 | +2.9 | +1.957 |
| NORMAL | 12 | 24.0 | 2.044 | 0.192 | 1.851 | 2.233 | 4.617 | +4.177 | +3.155 | +1.796 |
| SC | 18 | 17.833 | 1.653 | 1.667 | 1.401 | 2.796 | 4.904 | +4.464 | +3.884 | +2.88 |
| holdout | 9 | 1.0 | 0.372 | 0.494 | 0.172 | 0.0 | 0.858 | +0.418 | +0.418 | +0.426 |

## 結論

- KPI_cost_plus2: No(下限=Stage1新設だけで+1.957円/run vs rep24。線形fit込み+3.458、cap10でも+2.9。同一instance照合のrep30比でも下限+1.508、線形+3.01、cap10 +2.452。NORMAL群は線形+4.425)。基準+2円/記事を下限でも超えるか僅差、Stage 2・追加Rewriteを入れると超過。注意: hold-out 9本は判定単位が1文のみ(候補1/run)で記事規模の代表ではない
- KPI_human_review_zero: 不明(BLOCKING・Rewrite・cycle増で上限到達リスクは上がる。実測は段階Bのみ)
- KPI_safety_zero_miss: 見込みYes(Stage 1はSC 6/6・hold-out 9/9。ただしStage 2が候補過多でBLOCKING判定の質を保つかは不明)
