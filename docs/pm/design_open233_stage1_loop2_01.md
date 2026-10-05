# OPEN-233 Stage 1 ループ2 RCA・設計(委任_10、¥0、Opus#17前)

管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。Trial専用、到達上限`VALIDATED`、Production未配線、`APPROVED_FOR_PRODUCTION`ではない。KPI provenance: 既存fresh出力(段階A 42 run、rep30)の再集計と仮定付き積み上げ。E2Eではない。根拠・全数値: `er052_output/open233_kpi_recovery_02_offline_01/loop2_cost_structure_01.{py,json,md}`(以下「試算」)。表記: 【確認】=保存出力・コードで確かめた事実、【推測】=推論・仮定。

## 0. 結論(先に)

1. 費用主因【確認】: output token(reasoning含む)がcall費用の約9割。reasoning 57%(r5は68%、平均7.7k tok)、可視出力33%、入力10%。入力のLedger長は主因ではない(未cache入力でも10%)。r3の可視出力の53%はSUPPORTED単位(平均11単位x約179tok、逐語引用+support_fact_ids+空flags等の骨格)。+¥1.5/runの主因は「全文を判定させ、毎単位に構造化出力を強制する構造」と「r5の高いreasoning(¥0.88/call、r3は¥0.65)」。
2. 【重要・新規】r3単独の見かけの18/18は偽: A4-0のr3経路はs1/s2が**決定論の否定検査(誤発火)でのみ候補化**、モデル判定由来はr3 16/18・r5 17/18・∪18/18【確認】。よって(D)r5廃止と(B)否定検査是正を同時に行うとA4-0を2/3見逃す。2経路は独立に効いている。
3. SC候補の具体性【確認】: SC 18件・hold-out 9件の全gold候補が「fact実在+具体要素フラグ(因果/主体/否定/数値等)+issueに食い違いの記述」を持つ。(A)2層化でSC候補が「具体側」に残る根拠は(proxyだが)ある。ただしB3/B4-a/neg5は「Ledgerに無い因果(absence型)」で、(A)の具体性は「矛盾」だけでなく「fact Xにその要素が無い」も含める設計が必須。
4. (B)否定検査【確認】: 是正案aで旧149件→9件(unique 6)。真の可能性あり2件は残る(cannot型の留保)。gold/hold-out候補で否定検査だけで検出されたものは0件(A4-0のr3を除く、上記2)。「全行照合」案bは合成否定反転の決定論感度を失うため不採用。
5. Stage 2は既にbatch call【確認】: 束ね(C)の節約は入力分の上限¥0.39/記事。費用は候補数に比例(¥0.064/候補)。
6. 推奨F=B+A(+2経路維持)。見込み(rep30基準 NORMAL): +¥3.55(A+B)、reasoning半減の感度(未検証)で+¥2.94。KPI+2円: **基準点がrep24(0.44)ならNo寄り、Production 2.77ならYes見込み(NORMAL total 3.75)**。Human Review 0は不明(NORMALの期待追加BLOCKING 約1.1/記事、E2Eのみ)。見逃し0は「見込みYes(条件付き、n小)」。

## 1. 費用構造RCA(実測、段階A 83成功call)

| call | n | 入力tok | 出力tok(reasoning) | 可視出力 | ¥/call | reasoning比 | 可視出力比 |
|---|---|---|---|---|---|---|---|
| r3(3'-R、初回) | 42 | 5,160 | 7,290(3,465) | 3,825 | 0.651 | 42% | 46% |
| r3欠落再実行 | 0 | - | - | - | - | - | - |
| r5(5-lite) | 41 | 4,821 | 10,253(7,674) | 2,580 | 0.878 | 68% | 23% |

- 単価: 入力¥15.7/Mtok、出力¥78.4/Mtok。reasoning effortは`high`(`er003_v1_en_direct_vfl_01_generate.py` L58)で全Stage 1共通。cache命中は2/83のみ。
- 回帰(R2 0.965): r3可視出力=SUPPORTED 1単位179tok+CANDIDATE 1単位149tok。SUPPORTEDの内訳(逐語引用そのものの割合)は出力生文字が未保存で分離不能【推測: 骨格だけで100tok前後、引用は日本語数十字】。
- Stage 1 1 runの内訳(全run平均¥1.52。NORMALは¥2.04): r3 reasoning約0.27、r3可視0.30、r5 reasoning 0.60、r5可視0.20、入力0.15(概算)。主因=r5 reasoningとr3の全単位出力。
- Stage 2(rep30、n=30回帰): 候補1件¥0.064(入力local_context 2.7k tok分0.027+出力551tok分0.043)。Stage 2は**既にtitle/hook群・body群のbatch call**(+S1第2意見call)なので、委任_09の「個別判定」前提は不正確。(C)の同一fact束ねは候補19.7件→fact 5.1種へ束ねられるが、節約は入力分の上限¥0.39/記事で、出力・判定は候補ごとに必要【推測】。

## 2. SC候補の具体性(委任_09の未集計分)

規則(機械、gold・定義変更なし): strict=related_fact_idがLedgerに実在+7種要素フラグ(数値/主体/時期/確信度/因果/比較/否定)のいずれかが立つ。
- SC 6 claim x 3 run=18件: 全て strict(要素フラグ+fact実在)。B3/B3-same@neg5=因果(HF-007、issue「Soが…を理由として結び付けているがLedgerは因果を述べていない」)、B4-a=因果(MUSE-HC-006、「引き継ぐ条件はLedgerに無い」absence型)、A2A3-0=主体+確信度(HF-003/002、「支払義務者は示されていないのに貨物を運ぶ者と特定」)、A4-0=主体(MUSE-HC-006、「やり取りの相手をusersと置換」)、A5-0=否定(MUSE-HC-012、「put backは機能を再導入=Ledgerのロールバックと逆」)。
- hold-out 9種: 全て strict(各changed_*種別のフラグ+fact実在)。neg5=関係単位(So)のr3が3/3、r5は2/3(1 runはAPI失敗でr5欠落、判定誤りではない)。
- HF-011(監視、gold外): 検出1/3(r3のみ、changed_causality+certainty)。過適合しない監視項目。
- 候補全体(LLM由来)のstrict割合: NORMAL 133/237=56%、SC 150/249=60%。NORMAL先頭30件ラベル(推測)x strict: 真の逸脱R 4/4がstrict、迷って候補U 20件のうちstrictでないのは10件(SEMI 9+VAGUE 1)、N(自然)6件中2件がstrict。**flagsだけでは「U」を半分しか分離できない**【確認】(LLMが修辞文にも要素フラグを立てるため)。
- 含意: 機械proxyで落とせるのはNORMAL候補の約45%(24.0→13.2、UNSURE escalation e=0.2込み)。(A)の真の効果は「モデル自身に具体的discrepancyを書かせる新schema」でのみ測れ、fresh Trialが必須【推測】。

## 3. (B)否定極性検査の是正案の¥0検証(オフライン再実装、checker本体は無変更)

旧149件は、第1support factのみでの再現が149/149。是正案を試算スクリプト内で再実装した結果:
| 案 | 内容 | 旧149件のうち残る件数 | 合成否定反転(hold-out)への決定論感度 |
|---|---|---|---|
| 旧 | claim行(1行目)の日本語否定語のみ | 149 | あり |
| a | claim行のみ、対比構文(ほどなく/ではなく/でなく/意図せず…)除外、「なし」追加、英語Ledger行は英語否定語、単位側'not only'除外+dislike/lack等 | **9(unique 6)** | あり |
| b | aに加え、fact block全行で否定を探す(=「全行照合」) | 7 | **なし**(block 5行に別の否定語があり打ち消される) |
| c | 決定論の否定検査を外しLLM `changed_negation`へ一本化 | 0 | なし(LLM経路のみ) |
- aの残り9件(6単位): cannot型の留保がLedgerに無い2件=真の可能性あり(PLAUSIBLE_TRUE、極性反転ではなく「Ledgerに無い留保」。Stage 2に渡して良い)、「not X」型(large bags had not vanished等)3単位=Ledger claim行に無い主張でNORMALラベルRと同型、「only/still only」2単位=情報欠如の言い換えFP。FPとして残るのは2単位(only型)だけ。
- gold/hold-out: 否定検査**だけ**で検出されたgold/hold-out候補は0件。ただし**A4-0のr3経路のs1/s2は否定検査の誤発火でのみ候補化**(モデル判定はSUPPORTED)。a/b/cはいずれもこの2件のr3検出を失う。r5(A4-0 3/3 M)が救うため2経路維持なら∪は18/18のまま。
- hold-out changed_negation: r3・r5ともLLMが`changed_negation`付きで検出済み(M/M)。決定論感度はaで維持。
- 判断: **a採用が妥当**(誤発火を除きつつ、LLMが誤ってSUPPORTEDにした極性反転を拾う決定論の最終網を保つ)。b/cは「重大に甘くする」方向なので不採用。真の可能性あり2件は削らずに残る。

## 4. 設計案の比較(費用は試算§4、rep30同基準の+¥/run。NORMAL=本番に近い群、記事33=hold-out除く。vs2.77=total費用-Production check+mustfix平均2.77)

| 案 | 構造 | Safety影響と検出維持の根拠(SC 6/hold-out 9/neg5/HF-011) | 費用(NORMAL add / 記事33 add / NORMAL vs2.77) | 規模 | Opus論点 |
|---|---|---|---|---|---|
| S0 現行 | r3+r5 ∪、全候補をStage 2 | 基準: SC 18/18、hold-out 9/9、neg5 r3 3/3・r5 2/3 | +4.43 / +3.73 / +1.85 | - | - |
| (A)2層化 | CANDIDATE=fact_id+要素(数値/主体/時期/範囲/因果/確信度/否定/比較)+記事側値+fact側値(または「無い」)を必須。不能=UNSURE→小batch triage(1 call/記事、全UNSUREの個別ESCALATE/DISMISS+理由。決定論での自動DISMISS禁止) | SC 18/18・hold-out 9/9・neg5(3/3)は旧schemaのproxyで全てstrict具体側(§2)。B3/B4-a/neg5は「absence型」も具体に含めること必須。HF-011は1/3で元から弱く、UNSUREへ落ちる恐れ(監視)。新schemaでのgold位置は未測定=fresh必須 | A(e=0.2)+B: +3.55 / +2.80 / +0.98(e=0.1〜0.3で+3.46〜3.65)。triage ¥0.26/記事(推論2.5k仮定、4.5kなら+0.17) | 中(schema・prompt・triage関数・unit test) | UNSURE triageの独立性、DISMISS誤り、escalation率e |
| (B)決定論是正 | 否定検査を案aへ | §3。gold/hold-outの否定検査単独検出0。A4-0のr3 s1/s2(偶然のD検出)を失うがr5が救う | B単独: +4.02 / +3.20 / +1.44(-0.41) | 小(関数1つ+test) | 案aの残FP(only型)、2経路維持が前提 |
| (C)Stage 2束ね | 同一fact束ね(上限なし) | 候補は不変、Stage 2判定の質のみ影響(BLOCKING率維持は未測定) | 節約上限-0.39(入力分のみ。出力は削れない) | 中 | 効果小、判定質リスク |
| (D)経路整理 | r5廃止/縮小 | **r3単独のモデル判定16/18**(A4-0 2/3見逃し)=SC 3/3基準未達。r5単独17/18(neg5 1欠落)。2経路は独立に効いている | B+D: +2.70 / +2.12 / +0.12 **(Safety基準未達のため不可)** | 小 | 冗長性、A4-0型のr3単独救済策があるか |
| (E)出力軽量化 | SUPPORTEDはfact_idsのみ、引用省略 | quote_not_in_ledger検査(4件/42 run)を失い、3'-Rの網羅強制(Opus#16 論点1-2)が弱まる。候補側(gold)には影響しない見込みだが、偽OK抑止の効果は未測定 | B+E: +3.88(-0.13/run)。**効果が小さくSafety根拠が弱い→不採用推奨** | 小 | 引用の抑止効果 |
| (G)新: reasoning effort引下げ | 全Stage 1共通`high`→medium(または経路別) | 検出力への影響は未測定。SC/hold-outをn=3で再測定すれば検証可。検出が落ちれば不採用 | A+B+RS0.5: +2.94 / +2.27 / +0.36(RS=reasoning半減の仮定、**未検証**) | 小(パラメータ)だが要Trial | effortの効果と非決定性 |

## 5. 推奨構成(F)とKPI見込み

**F = (B)案a + (A)2層化(新schema+UNSURE小batch triage) + r3/r5の2経路維持。(G)reasoning effort引下げは同一Trial内の実験アームとして並走し、検出力が維持される場合のみ採否を検討。(C)(E)は不採用、(D)はA4-0型のr3単独救済策が実証されるまで不可。**
- 理由: (D)は最大の削減(-¥1.0)だが、モデル判定由来のr3単独は16/18でSC基準(各3/3)未達。「重大に対して甘くしない」に反するため、費用削減の主軸にしない。(B)(A)は費用を下げつつ、gold/hold-outの検出がstrict具体側に残る根拠(§2・§3)がある。
- UNSURE triageのSafety設計(必須): UNSUREは捨てず、決定論による自動DISMISS禁止。triageは個別にESCALATE/DISMISS+理由を返し、DISMISSされた単位は全件監査ログに残す。triageにはLedger全体と判定単位を渡す(factを絞らない)。SC/hold-out/neg5のgoldがUNSURE側に落ちたらSTOP。

| 見込み(rep30基準 add / rep24基準 add / Production基準 vs2.77) | NORMAL | 記事33 | ALL42 |
|---|---|---|---|
| S0 現行 | +4.43 / +4.18 / +1.85 | +3.73 / +4.29 / +1.96 | +3.01 / +3.46 / +1.13 |
| F(A+B、e=0.2) | +3.55 / +3.31 / +0.98 | +2.80 / +3.36 / +1.03 | +2.28 / +2.73 / +0.40 |
| F+G(reasoning半減、未検証) | +2.94 / +2.69 / +0.36 | +2.27 / +2.83 / +0.50 | +1.85 / +2.30 / -0.03 |
| (参考)A+B+D【Safety不可】 | +2.28 / +2.03 / -0.30 | +1.74 / +2.30 / -0.03 | +1.39 / +1.84 / -0.49 |

- KPI Cost(+2円): **基準点により逆転**【不明点】。rep24基準(0.44)ならFは+3.3(G併用でも+2.7)でNo。Production基準(check+mustfix平均2.77、total費用との差)ならFは+0.4〜+1.0でYes見込み(現行S0でもALL42 +1.13、NORMAL +1.85)。ループ1の「No」はrep24基準での判定だった【確認: 委任_09】。Opus#16も基準点未確認を指摘済み。Fableの確定が必要。
- KPI Human Review 0: **不明**。F後もNORMALで追加BLOCKING 約1.1/記事(rep30のBLOCKING率0.10を新候補へ適用した仮定【推測】)、追加Rewriteなしの確率は約3割。E2Eでのみ判定可。
- KPI 見逃し0: 見込みYes(条件付き)。2経路維持+(B)案a+(A)のgold具体側維持が前提。標本はSC 18/hold-out 9で、見逃し0の証明にはならない(Opus#16)。

## 6. 限定Trial計画と予算(残約¥174=枠¥238-使用¥64.20。単価は試算の仮定、誤差±30%)

0. **¥0 offline(実装後)**: 単体テスト、案aを旧149件へ再適用(9件再現)、保存出力のgold経路別M/D再集計、新schema validator。
1. **小規模fresh(Stage 1のみ、新schema+triage、2経路)**: SC 6x3=18+hold-out 9x1+NORMAL 6x1=33 run。Stage 1 約¥1.8/run(r3 0.65+r5 0.88+triage 0.26)=**約¥63**。判定: 6 claim各3/3、hold-out 9/9、gold・neg5がUNSURE側/DISMISSに落ちない、欠落ID<=5%、NORMAL候補/記事とUNSURE比率を記録。
1b. **(G)実験アーム(任意、1が合格し予算が残る場合)**: effort=mediumでSC 6x3の2経路=18 run、約¥20。検出が1つでも落ちれば不採用。
2. **E2E(1が全合格の場合のみ)**: NORMAL 6+SC 6+B2_hormuz 1+hold-out 3(number/causality/negation)=16 run x total約¥3.8=**約¥61**。測定: Human Review/STAGE4、Rewrite率、誤BLOCKING率、平均追加費用(3基準点併記)、worst run。
- 合計 約¥144(1b込み)。残り約¥30は予備。各段の累計が計画の1.3倍を超えたらSTOP。11-4の自律ループ(最大3回)の2回目に当たる。

## 7. STOP条件(Safety-Cost構造的両立不能の判定基準を含む)

1. 小規模freshでSC 6件のいずれかが3/3未満、hold-out見逃し、またはgold/neg5がUNSURE側・DISMISSへ落ちる → E2Eへ進まない。機構分析のみ(Prompt追加で追い込まない)。
2. 欠落IDが再実行後も5%超、H1(API失敗のPASS抜け)再発 → STOP。
3. **構造的両立不能の判定**: Safety基準(1の全項目)を満たす構成のうち最安(2経路維持、A+B、Gは検出維持時のみ)について、小規模fresh実測で再計算したNORMAL add(rep30基準)が+3.0を超え、かつKPI基準点がrep24基準で確定している場合 → 「現構造ではSafetyとCostが両立しない」としてSTOPし、ユーザーへ(1)KPI基準点の再確認 (2)冗長性縮小(Safety低下、非推奨)の可否 (3)対象絞り等の別方針を提示。Production基準なら+2は未達でない可能性が高く、この判定はE2Eのtotal費用で行う。
4. E2EでHuman Review 1件以上、またはworst run ¥6超 → STOP(報告)。

## 8. 確認/推測の区分、未確定、Fable・ユーザー判断が要る点

- 【確認】費用内訳・回帰・経路別M/D・否定是正の件数・Stage 2既にbatch・SC/hold-outの具体性は、保存出力(段階A 42 run、rep30)とコードの再集計。有料API・checker/runnerコード変更なし。gold・fixture・Safety-critical定義は不変。
- 【推測】SUPPORTED逐語引用そのものの割合(生出力文字が未保存)、triage 1 callの¥0.26(入力5k+推論2.5k+40tok/件の仮定)、escalation率e(0.1〜0.3の範囲)、追加BLOCKING率(rep30のNORMAL 0.10/全体0.289を新候補へ適用)、(G)のreasoning半減、E2E 1 runの総費用。strict tierは旧schemaのフラグでの機械proxyで、新schemaの挙動ではない。
- 【新しい仕様候補(実装せず報告)】(G)Stage 1のreasoning effort引下げ(探索深さの変更=Safety影響の可能性)、(A)の新schema・UNSURE triage(責務の再配分)。いずれも`APPROVED_FOR_PRODUCTION`ではなく、Opus#17→Fable評価→限定Trialまで実装しない。
- 【Fableへ】(1)KPI「平均追加+¥2/記事」の基準点: rep24(0.44)かProduction check+mustfix(2.77)か。これでCost KPIの結論が逆転する(§5)。(2)(D)r5廃止はSC基準未達のため推奨しないが、「r3のA4-0型見逃しを別機構で救えるか」はOpus#17の論点。(3)(A)のabsence型を具体側に含める定義はgold(B3/B4-a/neg5)の扱いを変えない前提だが、UNSURE側に落ちる単位が出ない確認がfreshで必須。
- 【再発防止】Opus#16の「判定方針を変えずに強制しても届かない」「重大度はStage 2」「HF-011は監視のみ」を維持。UNSURE triageは責務の再配分であり、自動DISMISS禁止・全件監査ログを必須とする。
- 【データ上の限界】n=18/9では見逃し0を証明できない。「LLMは揺れるから仕方ない」で終わらせず、揺れ(A4-0 r3 2/3がD、neg5 r5のAPI失敗)は2経路の独立性で吸収されていることを確認した上で、経路ごとの冗長性を維持する。
