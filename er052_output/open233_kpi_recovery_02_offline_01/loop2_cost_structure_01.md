# Stage 1 ループ2 費用構造RCA・SC候補具体性・否定検査是正・案別費用見込み(委任_10、¥0)

KPI provenance: 既存fresh出力(段階A 42 run・rep30)の再集計と仮定付き積み上げ。E2Eではない。見込みは推測を含む。Trial専用、Production未配線、APPROVED_FOR_PRODUCTIONではない。

## 1. 費用構造(段階A 42 run、実測usage)

| call種別 | n | 入力tok | 出力tok | うちreasoning | 可視出力tok | ¥/call | 入力(未cache)% | reasoning% | 可視出力% |
|---|---|---|---|---|---|---|---|---|---|
| r3/r3 | 42 | 5160 | 7290 | 3465 | 3825 | 0.6511 | 12 | 42 | 46 |
| r5/r5 | 41 | 4821 | 10253 | 7674 | 2580 | 0.8783 | 8 | 68 | 23 |

全83 call平均¥0.7633/call。費用構成: 入力10%、reasoning 57%、可視出力33%(output tokenが約9割)。r3の欠落ID再実行callは0回(欠落ID 0%)。失敗call 2(r5 API失敗1+retry1)。cache命中は2 callのみ(cached=0が81/83)。単価=入力¥15.7/Mtok、出力¥78.4/Mtok。
r3の可視出力(平均3825tok)の回帰(R2=0.965、n=42): SUPPORTED 1単位≒179tok、CANDIDATE 1単位≒149tok(issue等の文字数は単位当たりに吸収)。平均SUPPORTED 11.2857単位x179=2023tok=可視出力の53%(逐語引用+support_fact_ids+空のflags/issue等の骨格を含む。逐語引用だけの内訳は出力生文字が未保存のため分離不能=推測)。
r5の可視出力回帰(R2=0.929): fact当たり19tok、対応単位当たり107tok。r5は可視出力が小さい(約2.6k)がreasoning平均7.7k tokで費用の約7割。

## 1b. Stage 2以降の構造(rep30実測)

Stage 2は既にtitle/hook群とbody群のbatch call(+S1第2意見call)で、候補ごとにlocal_contextを入力へ載せる。cycle1のcall数/instance平均2.4333。候補1件当たり(回帰、n=30): 入力2696tok(R2 0.712)、出力551tok(R2 0.853)、費用¥0.064/候補(入力分¥0.0269+出力分¥0.0432)。BLOCKING率: 全体0.289、NORMAL 0.1。Rewrite+Recheck¥0.314/回。
(C)束ね: 候補19.6667/記事に対し関連factは5.1212種(束ね可能14.55件)だが、Stage 2は既にbatchで、節約は入力分の上限¥0.391/記事のみ(出力・判定は候補ごと)。

## 2. SC候補の具体性(SC 18 run、hold-out 9 run、HF-011)

判定規則(機械、gold変更なし): strict=related_fact_idがLedgerに実在し、7種の具体要素フラグ(数値/主体/時期/確信度/因果/比較/否定)のいずれかが立つ。SEMI=factありだが具体要素フラグなし。VAGUE=fact不明/issue短い。

| instance | claim | run | 一致候補数 | flags(要素) | related fact | 経路 | tier |
|---|---|---|---|---|---|---|---|
| bgroup_B3 | B3 | s1 | 1 | causality,unsupported_new_claim | HF-007 | r3+r5 | CONCRETE |
| bgroup_B4 | B4-a | s1 | 1 | fact,causality,unsupported_new_claim | MUSE-HC-006 | r3+r5 | CONCRETE |
| neg5_hormuz_div_a2 | B3-same@neg5 | s1 | 1 | causality,unsupported_new_claim | HF-007 | r3+r5 | CONCRETE |
| safety_A2A3 | A2A3-0 | s1 | 1 | fact,certainty,actor,unsupported_new_claim | HF-003,HF-002 | r3+r5 | CONCRETE |
| safety_A4 | A4-0 | s1 | 1 | fact,scope,actor | MUSE-HC-006 | r3+r5 | CONCRETE |
| safety_A5 | A5-0 | s1 | 1 | fact,negation,unsupported_new_claim | MUSE-HC-012 | r3+r5 | CONCRETE |
| bgroup_B3 | B3 | s2 | 1 | causality | HF-007,HF-009 | r3+r5 | CONCRETE |
| bgroup_B4 | B4-a | s2 | 1 | fact,scope,causality,certainty,unsupported_new_claim | MUSE-HC-008,MUSE-HC-006 | r3+r5 | CONCRETE |
| neg5_hormuz_div_a2 | B3-same@neg5 | s2 | 1 | causality,unsupported_new_claim | HF-007 | r3+r5 | CONCRETE |
| safety_A2A3 | A2A3-0 | s2 | 1 | fact,scope,actor,unsupported_new_claim | HF-003,HF-002 | r3+r5 | CONCRETE |
| safety_A4 | A4-0 | s2 | 1 | fact,scope,actor,unsupported_new_claim | MUSE-HC-006,MUSE-HC-004 | r3+r5 | CONCRETE |
| safety_A5 | A5-0 | s2 | 1 | fact,negation | MUSE-HC-012,MUSE-HC-006 | r3+r5 | CONCRETE |
| bgroup_B3 | B3 | s3 | 1 | causality,unsupported_new_claim | HF-007 | r3+r5 | CONCRETE |
| bgroup_B4 | B4-a | s3 | 1 | fact,causality,unsupported_new_claim | MUSE-HC-006,MUSE-HC-008 | r3+r5 | CONCRETE |
| neg5_hormuz_div_a2 | B3-same@neg5 | s3 | 1 | causality | HF-007 | r3 | CONCRETE |
| safety_A2A3 | A2A3-0 | s3 | 1 | fact,actor,unsupported_new_claim | HF-003,HF-002 | r3+r5 | CONCRETE |
| safety_A4 | A4-0 | s3 | 1 | fact,scope,actor,unsupported_new_claim | MUSE-HC-006,MUSE-HC-004 | r3+r5 | CONCRETE |
| safety_A5 | A5-0 | s3 | 1 | fact,negation | MUSE-HC-012 | r3+r5 | CONCRETE |

SC 18件: {'CONCRETE': 18}、LLM判定由来(sub_reasonsにmodel)18/18。hold-out 9件: {'changed_actor': 'CONCRETE', 'changed_causality': 'CONCRETE', 'changed_certainty': 'CONCRETE', 'changed_comparison': 'CONCRETE', 'changed_negation': 'CONCRETE', 'changed_number': 'CONCRETE', 'changed_scope': 'CONCRETE', 'changed_time': 'CONCRETE', 'unsupported_new_claim': 'CONCRETE'}。
HF-011(監視、B2_hormuz): [0, 0, 1](run別一致候補数。検出1/3、r3経路のみ、flags=changed_causality+changed_certainty)。

候補全体のtier分布(LLM由来候補、strict/permissive):

| 群 | strict CONCRETE | SEMI | VAGUE |
|---|---|---|---|
| SC | 150 | 94 | 5 |
| B2watch | 12 | 6 | 0 |
| NORMAL | 133 | 89 | 15 |
| holdout | 9 | 0 | 0 |

NORMAL先頭30件ラベル(委任_09、推測)x tier: {'permissive:N|CONCRETE': 2, 'permissive:N|DETERMINISTIC_ONLY': 3, 'permissive:N|SEMI': 1, 'permissive:R|CONCRETE': 4, 'permissive:U|CONCRETE': 12, 'permissive:U|SEMI': 7, 'permissive:U|VAGUE': 1, 'strict:N|CONCRETE': 2, 'strict:N|DETERMINISTIC_ONLY': 3, 'strict:N|SEMI': 1, 'strict:R|CONCRETE': 4, 'strict:U|CONCRETE': 10, 'strict:U|SEMI': 9, 'strict:U|VAGUE': 1}

経路別のモデル判定由来検出(M=モデル判定、D=決定論検査のみ、-=無し。run順s1,s2,s3):

| gold/hold-out | r3 | r5 |
|---|---|---|
| B3 | MMM | MMM |
| B4-a | MMM | MMM |
| B3-same@neg5 | MMM | MM- |
| A2A3-0 | MMM | MMM |
| A4-0 | DDM | MMM |
| A5-0 | MMM | MMM |
| changed_actor | M | M |
| changed_causality | M | M |
| changed_certainty | M | M |
| changed_comparison | M | M |
| changed_negation | M | M |
| changed_number | M | M |
| changed_scope | M | M |
| changed_time | M | M |
| unsupported_new_claim | M | M |

SC 6件x3 run=18のモデル判定由来検出: r3 [16, 18]、r5 [17, 18]。M=その経路のモデル判定が候補化、D=決定論検査(SUPPORTED->CANDIDATE)でのみ候補化、-=その経路では候補なし。A4-0のr3はs1/s2がD(=誤発火の決定論否定検査が偶然goldに当たっただけ)

## 3. 否定極性検査の是正案(オフライン再実装、checker本体は無変更)

旧発火149件(第1support factのみでの再現149件)。是正案a(fact側=claim行のみ、対比構文「ほどなく/ではなく/でなく/意図せず」除外、「なし」追加、英語Ledger行は英語否定語で判定、単位側の英語は'not only'除外+dislike/lack/fail to/unable追加)で残る件数=9(unique 6)。是正案b(さらにfact block全行で否定を探す=「全行照合」)は7件だが、合成否定反転hold-out(er009 changed_negation)に対する決定論検査の感度が失われる(下記)。案c=決定論の否定検査を外す: 残0。
合成否定反転hold-out(LLMがSUPPORTEDと誤判定した場合の仮想感度): 旧検査=True、是正案a=True、是正案b(全行)=False(fact block5行に別の否定語がある)。実際のrunではこの単位はLLM両経路(r3+r5)がchanged_negation付きで検出済み(sub_reasons=['model'])。gold/hold-out候補のうち決定論の否定検査だけで検出されたもの: 0件。

是正案a後の残り(unique単位):

| instance | 単位 | 内容 | 判定(推測) |
|---|---|---|---|
| bgroup_B2_hormuz | S10.1 | Of course, this price movement alone cannot tell us that there was jus | cannot型の留保がLedgerに無い=真の可能性あり(PLAUSIBLE_TRUE 2件) |
| neg4_smallbag_div_a2 | S2.2 | They are not pushing large bags away. | 対比『not X』がLedger claim行に無い=Ledgerに無い主張(NORMAL先頭ラベルRと同型) |
| neg4_smallbag_div_a2 | S6.2 | Large bags had not disappeared. | 対比『not X』がLedger claim行に無い=Ledgerに無い主張(NORMAL先頭ラベルRと同型) |
| neg6_smallbag_div_b1b | S5.2 | This lineup matters: large bags had not vanished. | 対比『not X』がLedger claim行に無い=Ledgerに無い主張(NORMAL先頭ラベルRと同型) |
| bgroup_B2_hormuz | S3.4 | It was still only at the stage of announcing the policy. | 『only/still only』=情報欠如の言い換え(FP) |
| bgroup_B3 | S3.3 | For the moment, only a large number stood at center stage. | 『only/still only』=情報欠如の言い換え(FP) |

## 4. 案別費用見込み(rep30同基準、¥/run。add=rep30照合比、total=rep30費用+add、vs2.77=totalと Production check+mustfix 平均2.77の差)

仮定: 段階A 42 runの候補集合を各案で機械的に絞り直し、Stage 2費用=委任_09と同じ線形fit(¥0.099+0.073x候補)、追加BLOCKING=rep30 BLOCKING率(NORMAL 0.10/他0.289)x増分候補数、Rewrite+Recheck¥0.314/回。A=strict tierのみStage 2、他はUNSURE(triage1 callを¥0.26と仮定、escalation率e)。E=r3のSUPPORTED 1単位を40tokへ。RS/R5CAP=reasoning削減の感度(未検証)。

| 案 | NORMAL 候補→S2 | NORMAL add | NORMAL total | NORMAL vs2.77 | 記事33 add | 記事33 vs2.77 | ALL42 add | SC add |
|---|---|---|---|---|---|---|---|---|
| S0 現行(r3+r5、全候補) | 24.0 | +4.4252 | 4.618 | +1.848 | +3.7317 | +1.96 | +3.01 | +3.2365 |
| B 否定検査是正のみ | 20.0833 | +4.0163 | 4.209 | +1.439 | +3.1963 | +1.424 | +2.5893 | +2.6913 |
| D r5廃止(r3のみ) | 23.3333 | +3.1102 | 3.302 | +0.532 | +2.6542 | +0.882 | +2.1133 | +2.3229 |
| B+D【Safety基準未達: r3単独のモデル判定16/18】 | 19.4167 | +2.7013 | 2.894 | +0.124 | +2.1216 | +0.349 | +1.6948 | +1.7828 |
| E r3出力軽量化 | 24.0 | +4.2923 | 4.485 | +1.715 | +3.5748 | +1.803 | +2.8868 | +3.0763 |
| B+E | 20.0833 | +3.8834 | 4.076 | +1.306 | +3.0394 | +1.267 | +2.4661 | +2.5311 |
| B+R5推論cap2000(未検証) | 20.0833 | +3.2873 | 3.48 | +0.71 | +2.6323 | +0.86 | +2.145 | +2.2309 |
| A(e=0.1)+B | 12.2833 | +3.4637 | 3.656 | +0.886 | +2.7193 | +0.947 | +2.2146 | +2.1943 |
| A(e=0.2)+B | 13.15 | +3.5542 | 3.746 | +0.976 | +2.7986 | +1.026 | +2.2768 | +2.2738 |
| A(e=0.3)+B | 14.0167 | +3.6447 | 3.837 | +1.067 | +2.8778 | +1.106 | +2.3391 | +2.3533 |
| A(e=0.2)+B+E | 13.15 | +3.4213 | 3.614 | +0.844 | +2.6417 | +0.87 | +2.1536 | +2.1136 |
| A(e=0.2)+B+D | 12.8833 | +2.2799 | 2.472 | -0.298 | +1.7387 | -0.033 | +1.3939 | +1.3653 |
| A(e=0.2)+B+D+E | 12.8833 | +2.147 | 2.339 | -0.431 | +1.5818 | -0.19 | +1.2706 | +1.2051 |
| A(e=0.2)+B+E+R5cap2000(未検証) | 13.15 | +2.6923 | 2.885 | +0.115 | +2.0777 | +0.306 | +1.7092 | +1.6532 |
| B+RS0.5(両経路reasoning半減、未検証) | 20.0833 | +3.4022 | 3.595 | +0.825 | +2.6705 | +0.898 | +2.1596 | +2.2262 |
| A(e=0.2)+B+RS0.5(未検証) | 13.15 | +2.9401 | 3.132 | +0.362 | +2.2728 | +0.501 | +1.8472 | +1.8087 |
| A(e=0.2)+B+D+RS0.5(未検証) | 12.8833 | +2.1087 | 2.301 | -0.469 | +1.5709 | -0.201 | +1.258 | +1.2044 |

注: rep24基準(0.4401)でのaddは上記add+(rep30費用-0.4401)。KPI基準点がrep24かProduction 2.77かで結論が変わるため併記。cap10(Stage 2 fitの上限10候補)でのadd(記事33): {'S0 現行(r3+r5、全候補)': 3.0216, 'B+D【Safety基準未達: r3単独のモデル判定16/18】': 1.6482, 'A(e=0.2)+B+D': 1.5551, 'A(e=0.2)+B+D+E': 1.3982, 'A(e=0.2)+B+D+RS0.5(未検証)': 1.3873}

