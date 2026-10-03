# OPEN-233-SELF-RECOVERY-TRIAL-01: Production Self-Recovery Flow 設計書

**Status**: `DESIGN_READY_FOR_OPUS_L2` → **[委任_04更新]**
`PHASE1_READY`(Opus L2レビュー#1完了・所見反映済み[§15]、Phase 1
実行前チェックリスト§9-0全項目確認済み。API呼び出し¥0、Production
非接続、実装なし)。委任_01(2026-09-30)で作成。→ **[委任_06更新]**
`PHASE1_STEP2_DONE`(既存Rewrite機構棚卸し[委任_05]を§5-0三分類表へ
統合、EN/JA局所Rewriteをそれぞれ既存ベース案[E-1/J-1]と新方式案
[E-2/J-2]の両論併記へ再構成[Phase 1 ⑤で比較実測予定]、deterministic
pre-check[`er052_open233_self_recovery_precheck_01.py`]をTrial実装、
Phase 1 ①[precheck FP率0%実測]・②[hormuz見逃し3attempt、Stage 2
診断3/3検出実測]完了。実測費用¥0.6285[Guardrail¥10、Phase累計]。
③以降・Production実装は未着手)。→ **[委任_07更新]**
`PHASE1_STEP4_DONE`(Phase 1 ③[Stage 1 variant実測確定: V0/V4-A/
S1-D比較、V4-Aを最終確定・S1-D不採用、根拠§14-5]・④[Stage2実単価・
batch化・prompt caching実測、per-claim vs batch判定一致率100%・
batch化でcost/latency改善、prompt caching費用削減率63〜64%実測、
Stage2較正リスク[Real-but-fixable群のQUALITY誤降格]を新規発見・
報告]完了。実測費用¥14.6598[Guardrail¥35のうち、Phase累計
¥15.2883]。⑤⑥は次回委任予定、Production実装は未着手)。→
**[委任_08更新]** `PHASE1_STEP5_DONE`(Stage2 rubric較正Trial実測・
確定[§4-8、R2採用・R3floor不採用、Safety群14/14維持・既知miscalib
6/6解消・negative群87.5%改善]、Phase 1 ⑤[Stage3型別Rewrite成功率
実測、§5-4-補2]完了: delete型baseline測定、replace型はE-1/E-2とも
100%[n=2]、**narrow_scope型[hormuz HF-009]はJ-1で完全解消・J-2は
未解消[drift 1件検出]**。採用案: narrow_scope=J-1、
replace_with_ledger_value=E-2第一候補(E-1はfallback)。実測費用
¥6.208[Guardrail¥45のうち、Phase累計¥21.4963]。⑥[統合dry-run]は
次回委任予定、Production実装は未着手)。→ **[委任_09更新]**
`PHASE1_DONE_IMPROVEMENT_NEEDED`(⑥統合dry-run完了: 新規runner
`er052_open233_self_recovery_flow_runner_01.py`で29 instance・92 call・
¥16.7806・0 errorを実測[§9-1⑥]。Self-Recovery 6項目実測[Initial
BLOCK23/Rewrite自動解消13/Final STOP9]、Escalation率9/29[Wilson
95%CI 17.3〜49.2%]、worst caseコスト¥2.2721でCap[+¥3]未超過。
**新規発見(いずれも報告のみ・独断で修正せず)**: (1) Stage1(V4A)
recall missを3instanceで実測(うち1件は現行Production STOP実例
hormuz_run02_advancedそのもの、Self-Recovery Flow到達前の見逃し)、
(2) Stage2出力schemaに`rewrite_hint`欠落がRewrite失敗の主要因、
(3) J-1汎用対象文特定の失敗率63.6%(委任_08手動アンカー実験との
乖離)、(4) **委任_08のnegative群R2測定[87.5%]がplaceholder文字列
[claim_text="(claim not found in baseline)"]に対する測定であり
無効、実クレーム文言での実測は0/4(0%)**。Phase 1計画①〜⑥完了、
Phase 2着手前に上記改善優先順位[§9-2]の解消を推奨。実測費用
¥16.7806[Guardrail¥45のうち、Phase累計¥38.2769]。USER_DECISION_
REQUIRED非該当[7条件いずれも]。Production実装は未着手)。→
**[委任_10更新]** `ITER2_DONE_TARGET_MET`(iteration 2完了: §9-2
改善優先順位1〜4[rewrite_hint追加/J-1ロケータ改善/negative群R2再較正
/Stage1 recall対策]を実装し29 instance再実行[126 call・¥26.0302]。
claim単位Rewrite成功率60.6%→81.0%、J-1対象文特定成功率36.4%→81.8%、
Escalation9→7件(Wilson95%CI[12.2%,42.1%])、true resolved11→16件へ
改善[§9-1⑦]。**S1-U variant(Stage1 PASS時にS1-D 1 callを追加しunion
screen)が委任_09の3件の重大recall miss[B2_hormuz・B3・hormuz_run02_
advanced=現行Production STOP実例そのもの]を全件捕捉しRewriteで解消**
(追加固定費¥3.1589、Escalation新規1件[meta_run03_advanced]という
副作用あり)。R2'rubric較正はSafety誤降格1件+Productivity改善0件で
不採用(既存R2維持)。実測費用¥29.4279[Guardrail¥50のうち、Phase累計
¥67.7048]。USER_DECISION_REQUIRED非該当[7条件いずれも]。S1-U variant
のPhase 2デフォルト採用可否はユーザー判断)。→ **[委任_11更新]**
`ITER3_DONE_IMPROVEMENT_NEEDED`(Opus L2レビュー#2[docs/pm/opus_l2_
review_open233_self_recovery_02.md]の是正1-8を実装[バグA/B修正・
停止判定是正・段落単位Rewrite拡張・測定是正・Rewrite由来逸脱検出・
S1-U安価代替比較]、regression test19件追加・既存含め55件PASS。
29 instance再実行[iter3、178 call・¥36.9585]でSTAGE4件数7→5件へ
改善、測定是正で誤った「誤PASS候補0」を訂正[真にunconfirmed3件を
特定・是正6で解消]。実run6 instanceのうちfresh 3件についてn=2追加
実行[23 call・¥5.8944]し、単発run[n=1]でのEscalation率測定が
不十分であることを実測確認[hormuz_run02_advancedがsample間で
final_state不一致]。S1-U安価代替3案[2xV4-A union/S1-D effort=medium
/low]はいずれも採否条件未達のため不採用、S1-U[effort=high]維持。
残るSTAGE4は主にangle起因[段落単位Rewriteのmethod-limitation]。
詳細§9-1⑧・§16。実測費用¥47.9886[作業C¥5.136+作業D¥42.8526、
Guardrail¥5+¥45のうち]。USER_DECISION_REQUIRED非該当[7条件いずれ
も]。Production実装は未着手)。→ **[委任_12更新]**
`ITER4_DONE_IMPROVEMENT_NEEDED`(ユーザー指示「許容線の再設計」
[自然な解釈はOK/事実の発明はNG]に基づきStage2 rubric R3→R3'[§4-9]+
floor改訂[changed_certainty除外、§4-3]+追加測定7項目[§8-iter4]を
実装。R3単体較正でSafety側誤降格5件を検出し1回限りの再較正[R3']で
2件[bundle粒度起因の境界事例]へ縮小。29 instance再実行[iter4、
139 call・¥28.5644]でSTAGE4件数5→3件、real_run Escalation率
16.67%→0%(現行Production STOP実例hormuz_run02_advancedがiter4で
Rewrite解消)。**一方、本委任の主目的だった「正常記事への不要Rewrite
削減」は部分達成にとどまる**(negative+Normal群9 instance中4件
[44.4%]でRewriteが発火、目標未達を正直に報告)。S1-U反実仮想比較
[0 call]でescalation件数は不変だが、除外すると既知recall miss2件が
沈黙裏に見逃されることを実測確認、維持を推奨。R3'のB4-d型への退行
リスクは残存課題として報告のみ(独断で追加実装せず)。詳細§9-1⑨。
実測費用¥36.4618[作業B¥7.8974+作業C¥28.5644、Guardrail¥8+¥40の
うち]。USER_DECISION_REQUIRED非該当[7条件いずれも]。Production
実装は未着手)。→ **[委任_13更新]**
`ITER5_DONE_IMPROVEMENT_NEEDED`(Opus L2レビュー#3[全文`docs/pm/
opus_l2_review_open233_self_recovery_03.md`]の是正1-6[rubric R3''/
R3'''・2-of-2安定化・cite-or-release・品質劣化検出v2・Rewrite品質
制約]を実装、29 instance×n=2実行[357 call・¥70.8204、Guardrail
¥11+¥65のうち]。safety_A4[iter3・iter4継続のangle起因]が初めて
両sampleで解消した一方、**per_instance_final_state_agreement=
21/29(72.41%)でn=1点推定の非決定性がn=2実測でも再現**、**不要
Rewrite(v2訂正版)はsample1 77.78%/sample2 66.67%でiter4の44.4%より
悪化**、**real_run Escalation率(n=2)=8.33%[iter4のn=1報告0%は
楽観的すぎたと訂正]**、**記事単位worst cost¥5.3592[safety_A4]で
+¥3 Capを超過**(ただし平均コストはCap内でtail riskと判断、
USER_DECISION_REQUIRED条件3には非該当)。不要Rewrite悪化の主因は
(a)floor精度[item7、ユーザー判断待ちで凍結]起因と(b)Stage2較正
セット外claimパターン[MUSE-HC-006/012等]への汎化未確認の2系統と
特定。USER_DECISION_REQUIRED非該当[7条件いずれも]。詳細§9-1⑩。
Production実装は未着手)。→ **[委任_14更新]**
`ITER6_DONE_LADDER_IMPROVED_ROOT_CAUSE_REMAINING`(ユーザー新方針10項目
[丸め許容・floor-cited・最小変更ラダー・セクション役割維持・Hook-aware
統合・コスト5分割等]を実装、監査2件[Hook-aware再監査・Rewrite後QA
資産棚卸し、¥0]実施、29 instance×n=2実行[Guardrail¥60到達で
TrialAbort、sample1 29/29完走・sample2 26/29]。**最小変更ラダーにより
段落単位Rewrite使用が0件(iter5はほぼ全件が段落単位)、記事単位平均
コストは¥1.0649でiter5から実質横ばい**(+¥2/記事Capを大きく下回る)。
**不要Rewrite率(sample1、iter5と同一base)は44.44%[4/9]でiter5の
77.78%から明確に改善**(iter4の44.4%と同水準)、ただし該当4 instance
は両sampleで完全一致し根本解消はできていない(Hook-aware対象外flag・
Stage2較正セット外汎化という既知の限界)。**real_run Escalation
(n=2 overlap)=16.67%[2/12]でiter5[8.33%]より悪化**(meta_run03_
standardがpaired J-1[未ラダー化]の既存挙動で両sample STAGE4)。
floor-cited variantはSafety群でhard gate通過(false-negative 0)だが
`related_fact_id`依存の限界を確認、floor-strict維持を推奨。
USER_DECISION_REQUIRED非該当[6条件いずれも]。詳細§9-1⑪、REPORT§15。
Production実装は未着手)。→ **[委任_16更新]**
`ITER7REP_STOPPED_SAFETY_REGRESSION_REVERTED`(J-1最小変更ラダー[§5-8]+
Hook-aware rubric拡張[§6-4]を実装し、広いiteration7実行前に代表5
ケースTrialを実施[¥9.386]。**J-1ラダーはPASS**(`bgroup_B3`が
`ladder_level_used=1_word_connective`[so→while相当]でBLOCKING維持の
まま解消、item4の目標を達成)。一方**Hook-aware rubricはSafety-critical
claim[bgroup_B3]の誤降格regressionを起こし、最小修正1回後もFAILが
再現**(prompt priming疑い)したためSTOP条件に該当し、Stage2実配線を
安全なRUBRIC_R3_TRIPLE_PRIMEへ復帰(再実測でBLOCKING復帰を確認)。
広いiteration7 Trialへは進んでいない(Gate判定はiteration6の
REJECTEDのまま)。USER_DECISION_REQUIRED非該当[6条件いずれも]。詳細
§9-1⑫、REPORT§16。Production実装は未着手)。→ **[委任_17更新]**
`REP8_ALL_5_CASES_PASS_HOOK_SEPARATION_CONFIRMED`(Hook演出許容を共通
rubricから分離した「Hook専用Stage2」[title/hookのclaimのみ別Prompt・
別call、§4-14]を新規実装し、委任_16と同一の代表5 instanceをn=2で
再実行した[¥5.2181、Guardrail¥14内、rep8]。**5ケース全てPASS**:
neg1[Meta Hook]がHook専用Stage2でQUALITY/ACCEPTABLE(n=2両方)と判定され
Rewriteなしで通過(委任_16でFAILしていたケースが解消)、`bgroup_B3`は
section_type="in_one_line"としてbody経路(既存RUBRIC_R3_TRIPLE_PRIME、
Hook専用Stage2を一切経由せず)でBLOCKING維持のままladder_level_used=
1_word_connectiveで解消(prompt priming疑いのregressionは再現せず)、
hormuz_run03_standard/safety_er009系2件も従来どおりfloor/BLOCKING維持
→minimal resolutionで解消。role_violation 0件・STAGE4到達0件・API error
0件。最小修正は不要だった(1回目実行で全PASS)。広いiteration7 Trialへは
本委任のスコープ外のため未実施(次回委任でのユーザー判断待ち)。
USER_DECISION_REQUIRED非該当[6条件いずれも]。詳細§9-1⑬、REPORT§17。
Production実装は未着手)。→ **[委任_18更新]**
`REP9_PARTIAL_GUARDRAIL_REACHED_MIXED_RESULTS`(ユーザー新指示12項目
[局所QA統合/全体Rewrite経路の是正/不要Rewrite4件の解決策/Escalation 2
runの解消/コスト是正]を実装[§4-15/§5-9/§6-5]し、代表12 instanceを
n=2で再実行した[¥20.0358、Guardrail¥20到達により`safety_A2A3`/
`safety_A5`のsample2は未実行、rep9]。主要3目標達成: (1)`safety_er009_
changed_number`が⑥[全体フォールバック]を経由せず解消(precheck合成
マーカー実文解決の効果)、(2)`neg2_meta_refresh_a2`が2/2 sampleで
disclosure-gap downgradeによりRewriteなしで通過、(3)`meta_run03_
standard`が2/2 sampleともSTAGE4_ESCALATIONに至らず(人間確認率0達成)。
`safety_er009_unsupported_new_claim`のtitle空文字化を2/2で正しく検出し
STAGE4へ回した(degenerate output guard、disclosure §1-1-4の静かな
false PASSを解消)。局所QA fastpathは3/3が安全側に全文Recheckへ
フォールバックし、コスト削減効果は今回未実証。**新規観測(未解決)**:
`hormuz_run03_standard`(sample1)で新規STAGE4(`cycle_limit_exhausted_
after_recheck`)、根本原因は既存の構造的限界(claim言い換えcycle
パターン)と分析したが実測FAILとして記録し追加の単発再実行は見送った
(§18-3/§18-9)。29 instance全量ではないため広いTrialのGateは判定保留。
USER_DECISION_REQUIRED非該当[6条件いずれも]。詳細§18。Production実装は
未着手)。→ **[委任_27更新]** `ELEMENT_TRIAL_MISCONCEPTION_PRINCIPLE_
CODIFIED_HORMUZ_TRIAL_A_PASSED_AFTER_ONE_MINOR_FIX`(ユーザー上位原則
「重大誤解原則」[2026-10-01]を§0として明文化し、PM_GOVERNANCE.md 23節・
PM_BRIEF.mdへ参照を追加。¥0是正4点[§5-11 escalate_to_paragraph廃止・
問題種類→初期単位写像・主体置換ガード・等価QA理由文保存]を実装し
unittest 19件追加[計261件、既存含め全PASS]。Hormuz要素Trial A[Stage2
body rubricのみ、¥2.1336]で許容群5・NG対照群5・Safety対照群2[B3因果+
er009 changed_scope、hormuz-HF009自身は本委任の再ラベル対象のため対照
から除外]を実測し、初回accept-1[「market全体」表現]が2/2 false BLOCK
だったため最小修正1回[rubric追加明確化]を実施、再実測n=2で全群
false PASS/false BLOCK 0件を確認した。Trial A-2[決定論名詞句置換、
¥0.1261]でNG 2件+原文②の用語置換が文の語順・ストーリーを保持した
まま解消することをdiff・局所QA 1callで確認した(唯一のREVIEW_REQUIRED
指摘は置換と無関係な既存箇所)。Stage1[V4A]・Hook専用rubricへの原則文
追加は定数として実装済みだが本委任では未配線(予算制約、§4-18に開示)。
本委任費用¥2.2597[Guardrail¥25のうち]。USER_DECISION_REQUIRED非該当。
詳細§9-1⑰、REPORT§25、Meta要素Trialは次回委任_28)。→
**[委任_28更新]** `SAFETY_CONTROL_AUDIT_STOPPED_AFTER_ONE_MINOR_FIX_
STILL_FAILING`(Part0: Stage1[V4A]・Hook専用rubricへ重大誤解原則を
実配線する自己完結ヘルパーを追加[既存`stage1_fresh()`/Hook batch既定
値は無変更、新規unittest 7件追加]。`SAFETY_CRITICAL_SUB_IDS`から
hormuz-HF009を除外[§7-0-iter27との整合、9件化]。Part1[Safety対照群の
全量確認、Stage2 body rubric]: Safety-critical 9claim+Safety12[er009
9フラグ]をn=2で実測したところ、**V2のままn=1予備測定でA4-0[counterparty
取り違え]・A5-1[VP→役職一般化]の2件がfalse downgrade**、原因を分析し
最小修正1回[V3、当事者関係の取り違えと役職の一般化を区別]を実施したが、
**n=2公式測定でもA5-1[QUALITY→ACCEPTABLEへさらに悪化]+Meta-1/Meta-2
[同一claim、"Also, some calls needed user information to continue."
がQUALITYへ新規false downgrade]の計2件が残存**(A4-0自体はV3で解消)。
委任文STOP条件「Safety対照群のいずれかが小修正1回後もBLOCKINGに戻らない」
に該当するため、**Stage2 body rubricへの重大誤解原則配線はここでSTOPし、
Part2[Meta Hook Trial B]・Part3[Actor Trial C]は未実施のまま本委任を
終了する**(Safety優先、広いTrial未実施)。Safety12[er009 9フラグ]は
Stage2直接判定9/9・Stage1[V4A]新配線4フラグ中3/4で完全一致(flag名の
帰属が1/8 runでchanged_actor→別flagへ振れたがseverity_final=BLOCKING
自体は維持、真の見逃しではない)。本委任費用¥7.0873[Part1予備測定
¥2.7022(詳細出力は事故復旧操作により失われた既知の損失、§9-1⑱参照)+
V3公式測定¥4.3851、Guardrail¥9/¥25のうち]。USER_DECISION_REQUIRED
7条件(§12)はいずれも非該当(Production非接続・KPI不変・Cap/予算内・
新Product原則の設定なし)。A5-1・Meta-1/Meta-2の扱い[Safety-critical
リストからの除外候補か、rubricのさらなる改善が必要かの判断]はFable/
ユーザー確認事項として開示。詳細§9-1⑱、REPORT§26)。

本書は前Phase`OPEN-233-CHECKER-REDESIGN-TRIAL-01`(以下「前Phase」)の
成果(Trial 1/2実測、Opus L2レビュー#1、Stability n=20実測、negative
claim候補16件、claim単位gold候補表)を踏まえ、目標を「Checker単体の
過剰品質率改善」から「**Production運用全体としてLedger/Deviation Check
起因のUSER_DECISION_REQUIREDを実質ゼロにするSelf-Recovery Flow**」へ
転換した新Phaseの設計書である。

---

## 0. 上位原則(重大誤解原則、2026-10-01ユーザー指示の明文化、委任_27)

**位置づけ**: 本節は新しいProduct原則の新設ではなく、2026-10-01の
ユーザー指示(委任_27委任文§1)をSSOTへ明文化したものである(既存
ユーザー意図の明文化、新規承認不要)。既存の許容線(§4-9〜§4-12、
R3系rubric)と矛盾するように見える場合は**本節が上位原則として優先**
する。PM_GOVERNANCE.md 23節に要約+本節への参照を置く(重複記載はしない)。

### 0-1. 最上位原則

OPEN-233は「Ledgerとの差異を全部直す」プロジェクトではない。目的は
「**英語学習者に記事の本質について重大な誤解を与えるものだけを止め、
それ以外はできるだけ元記事を守ること**」である。Eigo Radioは投資家
向けレポート・学術論文・政府発表・Fact Sheetではない。判断の最初の
問いは常に「**この違いは英語学習者に深刻な誤解を与えるか?**」である。

### 0-2. 用語の近似・一般化への適用(許容候補/BLOCK候補)

**原則許容候補**(「厳密には違う」というだけではBLOCKしない):
Brent futures→oil prices/Brent crude futures→crude prices/2.6%→
about 3%/1.7%→about 2%/確認済みFactから自然に導けるHook演出。

**BLOCK候補**(記事の主要な意味・主体・方向・規模・時間軸を誤認させる
場合): Brent futures→gasoline prices/Brent futures→世界全体の
energy prices/1企業の株価→株式市場全体/上昇→下落(方向反転)/主体A→
別主体B/継続していた出来事→一度消えて戻った出来事/未確認の人物・
行動・動機・数字の追加/因果の逆転。

判断基準は常に「記事の主要な意味・主体・方向・規模・時間軸を誤認させる
か」であり、「厳密には違う」というだけでBLOCKしない。

### 0-3. Rewriteは品質リスクという認識

「軽微な不正確さを残すリスク」と「Rewriteで記事品質を壊すリスク」を
比較し、後者が大きければRewriteしない。

### 0-4. 問題種類→初期Rewrite単位(委任_27 Part1-1/1-2、実装は§5-11)

| 問題の種類 | 初期Rewrite単位 |
|---|---|
| 用語の範囲違い | 名詞句だけ置換 |
| 数値丸め | 原則Rewriteなし |
| 誤因果 | 接続詞だけ |
| 主体違い | 主体だけ(Ledgerに明記された主体のみ) |
| 時間表現 | 時制・時間副詞・短い節だけ |
| 文全体の論理破綻 | 1文 |
| 複数文の整合崩れ | 初めて段落候補 |

「同じFactが再登場したら段落Rewrite」ルール(旧`escalate_to_paragraph`、
§6-6 A-2)は**廃止**する。各箇所は独立に初期単位から判断する(§5-11)。

### 0-5. 主体・対象の置換ガード

主体・対象の置換はLedgerに明示された主体・対象にのみ行う。不明な場合は
対象語を削除する/一般的な表現へ弱める/元文を維持する。未確認の具体
主体への置換は禁止する(実装: §5-11、`actor_rewrite_guard_ok`)。

### 0-6. Fable PMレビュー観点(7点、Trial設計・指示・レビューに適用)

厳密一致のためだけのRewriteになっていないか/重大誤解でないものを
止めていないか/小さく直せる問題を大きくRewriteしていないか/Rewrite
による品質劣化の方が大きくないか/学習者にとって本当に問題か/Human
Reviewを安易な逃げ道にしていないか/不要call・Recheck・Rewriteを
増やしていないか。

### 0-7. コスト方針

上限¥600(2026-10-01ユーザー承認)は目標額ではない。不要な広域Trial・
全文Recheck・段落/全文Rewrite・同じEvidenceの再取得・惰性の反復は
禁止する。KPI平均+¥2/記事以内(§13)は維持する。

---

## 1. 目的・ユーザー意図(2026-09-30、逐語要旨)

**最終目標**: 通常のProduction運用中に、Ledger/Deviation Checkを理由に
ユーザー判断を求められる状態を実質ゼロにする。現状「数記事に1〜2件
Checker STOP→USER_DECISION_REQUIRED」は量産性・開発速度の両面で
許容できない。

**基本方針**: Checker単体の完璧化が目的ではない。Productionフロー全体
として「初回Check→必要なら再スクリーニング→必要なら自動Rewrite→
再Check→Production継続」までシステム側で安全に完結させる。ユーザーへ
上げるのは「自動処理では安全に解決できない、本当に例外的なケース」だけ。

**Safety(絶対条件)**: Fact反転/actor取り違え/number・numeric scope重大
変更/negation反転/comparison方向反転/time・chronology重大変更/
unsupported material fact/主要Fact理解を変えるcausalityは確実に止める。
**重大fixtureの見逃し0件**を維持する。

**Self-Recovery Flowの構成(4段階)**:
- Stage 1 Initial Check: ACCEPTABLE/QUALITY/BLOCKING分類。ACCEPTABLE/
  QUALITYは継続候補、BLOCKINGのみ次段。
- Stage 2 Re-screening: 同じ判定の機械的反復ではなく「本当にProduction
  を止めるべきmaterial errorか」を再評価する。目的=初回Checkerの過剰
  品質・非決定性の吸収。
- Stage 3 Automatic Rewrite: 問題claimのみ・該当sentence/local context・
  必要最小範囲を修正→再Checker。
- Stage 4 Final Escalation: Re-screening+Rewrite+Recheckでも安全に解消
  できない場合のみUSER_DECISION_REQUIRED(通常運用では実質ゼロ)。

**主要受入条件の変更**: 「不要BLOCK率≤25%」は主要受入条件から外し
**診断用の中間指標**として残す。Primary KPI=**10〜20記事規模のProduction
相当TrialでLedger/Deviation Check起因のUSER_DECISION_REQUIRED=0件**。
Safety=重大Fact事故の見逃し0件。ゼロSTOPを無制限retryや高コストで
実現するのはNG。

**Trialの考え方**: まず既存fixture/artifactを最大限reuseしてSafety/
過剰BLOCK/re-screening/rewrite recoveryを検証(Phase 1)。設計が成立
したらProduction相当の記事Trialへ拡大する(Phase 2)。

**予算**: 新たに最大¥400(前Phaseの¥45.6803とは別管理)。

**目指す挙動**:
| ケース | 経路 |
|---|---|
| Normal | Check→PASS→継続 |
| False・borderline BLOCK | Check→BLOCK→Re-screen→QUALITY/ACCEPTABLE→継続 |
| Real but fixable | Check→BLOCK→Re-screen→Rewrite→Recheck→PASS→継続 |
| True exceptional | それでも解消不能→USER_DECISION_REQUIRED(通常運用ではほぼ発生しない) |

逐語全文はDECISION_LOG.mdの本エントリを参照(本書は要旨)。

## 2. Fable判定(設計の前提)

- 前Phaseの3件のUSER_DECISION_REQUIRED(指標定義/gold/materiality軸)は、
  本Phaseでは次のように再構成し、**Checkpoint Aでユーザー確認を取る
  (独断確定しない)**。
  - (a) 不要BLOCK率は診断指標へ格下げ(ユーザー指示、既に確定)。
  - (b) goldは**「最終到達状態」ベース**へ再構成する(§7参照)。重大
    fixture(ER-009-N1 9種・A群・changed_actor)はStage 1/2で必ず
    BLOCKING維持(Stage 2で通過させたらSafety事故)、その後Rewrite→
    PASSが期待到達状態。B2=Stage 2でQUALITY通過が期待。B1/B4は
    Opus claim単位評価どおりmaterial claim(B1-c/B4-a)はRewrite対象、
    非material claim(B1-a/b、B4-b/c)はStage 2通過が期待、fixture
    としてはRewrite→PASS到達が期待。B3=material(HF-007 conditions)
    につきRewrite→PASSが期待。negative claim候補16件=Stage 1または
    Stage 2で通過が期待。**いずれも「候補gold(ユーザー確認待ち)」**。
  - (c) materiality軸はStage 2 Second Judgeの判定基準として設計する
    (**真のProduction Promptは不変**)。**注(委任_03追記)**: これは
    真のProduction Deviation Check(`er003_v1_en_direct_vfl_01_
    generate.py`)については引き続き維持するが、Self-Recovery Flow
    Trial実装における「Stage 1」自体の構成(どのTrial variantを使うか)
    は§14で再検討し、V4A採用へ更新した(詳細§3-1/§14)。
- Stage 2の**deterministic safety floor**: Stage 1でchanged_actor/
  changed_number/changed_negation/changed_comparison/changed_timeの
  いずれかがtrueのdeviationは、Stage 2でACCEPTABLE/QUALITYへ降格
  させない(Rewrite必須)。Stage 2が降格できるのは、これらflagが全て
  falseのdeviationのみ。降格判断は「迷ったらRewriteへ」(fail-closed)。
- 既存案B(ja_source MAJOR→JA差し戻し1回)はStage 3のJA側Rewriteとして
  位置づけ直し、無駄な全文再生成を避ける「局所Rewrite」を優先候補と
  する(§5)。
- loop上限は設計で固定する。Stage 2は1回(BLOCKING確定時)、Stage 3
  Rewriteは記事あたり最大2回、Recheckは Rewriteごと1回、合計Checker
  call上限/記事を明記する(§3)。無制限retry禁止。

**Production Checkerのモデルに関する重要な既存事実(本Phase新規確認)**:
現行Production(`er003_v1_en_direct_vfl_01_generate.py::MODEL =
routing.WRITER_MODEL`、実体`gpt-5.6-luna`)は、前Phase Trial(er051系
harness、`gpt-6-luna`固定)とは**異なるモデル**でDeviation Checkを実行
している。Hormuz/Meta run_01〜03のE2E STOPは全てgpt-5.6-luna実測であり、
前Phase Trialのgpt-6-luna実測データとは直接比較できない(§10リスク
参照)。本設計のStage 1は既存Production Prompt/モデルを不変のまま
前提とし、Stage 2以降のTrial実装でどのモデルを使うかは別途明記する
(§9)。

## 3. Self-Recovery Flow設計(Stage 1〜4)

### 3-0. 全体像(状態遷移、テキスト図)

```
[Writer出力(Advanced or Standard)]
        │
        ▼
  Stage 1: Initial Check(Trial variant V4A、真のProduction Checkerは
  不変。§3-1/§14参照)
        │
   ┌────┴─────┐
   │            │
 ACCEPTABLE   BLOCKING-candidate(overall_status=LEDGER_DEVIATION、
 (deviations   MAJOR 1件以上)
 =[]、または          │
 全件MINOR)           ▼
   │          Stage 2: Second Judge(独立Prompt、claim単位)
   │                   │
   │         ┌─────────┼─────────┐
   │         │                   │
   │   deterministic floor   floor該当なし
   │   該当 → BLOCKING確定    → materiality判定
   │         │                   │
   │         │        ┌──────────┼──────────┐
   │         │     BLOCKING    QUALITY    ACCEPTABLE
   │         │        │           │           │
   │         ▼        ▼           └─────┬─────┘
   │    (cycle残数確認)                  │
   │         │                          ▼
   │   cycle枯渇 → Stage 4         継続(Production続行、
   │         │                     ラベルのみ記録)
   │         ▼
   │   Stage 3: Automatic Rewrite(局所優先、cycle消費+1)
   │         │
   │         ▼
   │   Stage 1: Recheck(Rewrite後の全文、既存Production Checkerを
   │         │          再実行=fail-closed、局所チェックに限定しない。
   │         │          **[委任_04改訂/A1]** 必ず`prior_issues`
   │         │          [直前cycleのBLOCKING確定claim一覧]を渡し、
   │         │          継続条件は「`overall_status==LEDGER_COMPLIANT`
   │         │          かつ`all_prior_issues_resolved==True`」の両方
   │         │          (既存Production gateと同一の厳しさを維持)
   │         │
   │   ┌─────┴─────┐
   │   │             │
   │ ACCEPTABLE   BLOCKING-candidate(claimが同一/新規いずれも。
   │   │             同一claim/fact_id再発は§3-3参照)
   │   ▼             └──→ Stage 2(cycle残数があれば再度)、
   │  継続                  枯渇していればStage 4
   ▼
  継続(Production続行)

(Stage 1 Recheckも同一Trial variant[V4A]で再実行する。§5-2参照)

Stage 4: Final Escalation(cycle上限[最大2]到達後もBLOCKING、または
JA Fact Check自体がSTOPした場合) → USER_DECISION_REQUIRED
```

### 3-1. Stage 1: Initial Check

**Stage 1設計の確定(委任_03、結論のみ。根拠の全文は§14)**: 本Self-
Recovery Flow TrialにおけるStage 1は、真のProduction Prompt(V0)を
無変更のまま使う案(§14 S1-A)ではなく、**Family X限定Trial variant
V4-A**(`er051_open233_checker_trial_variant_01.py`、
`build_trial_prompt_template("V4A")`/`build_trial_deviation_schema
("V4A", ...)`、post-hoc層は`classify_deviation_trial()`[V2と同一]、
前Phase委任_03で実装・実測済み、Prompt全体sha256
`e9c939930496ebed00a198455279bac1d61e6f5a162063f41ef5fde52cf81c97`)を
採用する(§14 S1-B)。**真のProduction Deviation Check
(`er003_v1_en_direct_vfl_01_generate.py::MODEL = "gpt-5.6-luna"`、
`DEVIATION_PROMPT_TEMPLATE`)は本委任を通じて一切無変更**(Family X
限定Trial harness内でのみV4Aを使う。V4AをProduction Stage 1として
正式採用する場合は、Self-Recovery Flow全体の採用とは別建ての
Production Prompt変更承認[USER_DECISION_REQUIRED条件(4)]が必要)。

- **入力/出力**: `vfl01.run_deviation_check()`相当の呼び出しに、
  Trial Prompt(V4A)とTrial schema(V4A)を渡す。`hook_aware=False`、
  Family X経路。severity算出ルール自体(「10種類のいずれかが明確に
  trueである場合のみMAJOR」)はV0から一切変更しない(V4Aはカテゴリ
  境界の明確化文のみを追加する差分ブロック)。
- **分類**: 既存の二値出力(`overall_status`)をSelf-Recovery Flowの
  3値語彙へ写像する。`LEDGER_COMPLIANT`(MAJOR無し)→**ACCEPTABLE**
  (継続、Stage 2以降へ進まない)。`LEDGER_DEVIATION`(MAJOR 1件以上)→
  **BLOCKING-candidate**(Stage 2へ)。**Stage 1アーキテクチャはQUALITY
  を直接出力しない**(materiality軸がないため、V4A採用後も変わらない)。
  QUALITYという出力値はStage 2でのみ生成される。これは既存Fable判定
  (c)と整合する設計上の制約であり、委任文の「ACCEPTABLE/QUALITY/
  BLOCKING分類」という表現は、実装上「ACCEPTABLE(継続) / BLOCKING-
  candidate(Stage 2で3値化)」の2値ルーティングとして実現する。
- **deterministic層**: V2 post-hoc(フラグ全falseでMAJORならMINORへ
  自動降格)はそのまま維持。
- **loop上限**: Stage 1自体はretryしない(1回のみ)。既存の「MAJOR時
  must-fix retry1回」(現行Production)は、Self-Recovery Flowでは
  Stage 3 Rewriteの一形態として再定義する(§5)。
- **STOP条件**: なし(Stage 1単独ではSTOPしない。BLOCKING-candidateは
  必ずStage 2へ渡す)。
- **コスト**: V4AはV0比call単価約+30%・latency約+60%(前Phase実測、
  §13-4/§14で費用モデルへ反映)。
- **ログ項目**: `article_id`/`writer_stage`(advanced/standard)/
  `deviation_id`/`claim_in_article`/`10 category flags`/`severity`/
  `origin`/`related_fact_id`/`cost_jpy`/`elapsed_seconds`/`raw_response_id`/
  `stage1_variant`(Trial期間中は`V4A`固定)/**[委任_04改訂/A2]**
  `detected_by`(`"stage1_llm"` | `"precheck"`。deterministic pre-check
  [§14-4]が単独で検出したdeviationは`"precheck"`とし、Stage 2の
  deterministic safety floor[§4-3]をStage 1の10 flagsに関わらず
  直接適用する[floor空振り防止、詳細§4-3])。
- **[委任_04改訂/A2]** `detected_by="precheck"`のdeviationは、Stage 2
  LLM materiality判定を経由せず**直接floor扱いでBLOCKING確定**とし、
  Stage 3(Rewrite)へ直送する(Stage 2をスキップ)。ただしPhase 1で
  precheckのFP率(§9-1①)が高いと判明した場合は、この扱いを「Stage 2へ
  強制送付するが棄却は不可としない(Stage 2で正当にACCEPTABLEへ戻す
  余地を残す)」という弱い分岐へ変更する(FP率実測後にどちらを採るか
  確定する。両案を設計として併記する)。
- **[委任_04改訂]** Stage 1のrouting述語は`overall_status`
  (`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)を用いる設計のまま維持する
  (`classify_deviation_trial`実装との整合、Opus所見論点2(A)Evidence
  参照)。`overall_action_trial`+`promote_deterministic_flag_v1`による
  ¥0のMINOR→BLOCKING昇格は、Phase 1で`overall_status`基準との比較実測
  対象として記録する(推奨のみ、Stage1採否確定は§9-1③実測後)。

**[委任_10新設・実測] S1-U variant(Stage1 recall miss対策、union
screen)**: 委任_09で発覚したStage1(V4A)recall miss(3 instance、
うちhormuz_run02_advancedは現行Production STOP実例そのもの)への
対策として、Stage1(V4A)がACCEPTABLE(PASS)だった場合に限り、S1-D
(§14-2、materiality一体型、1 call)を追加実行し、S1-DがBLOCKINGと
判定したclaimのみをunion(fail-closed)でStage2以降へ合流させる
variantを実装した(`er052_open233_self_recovery_flow_runner_01.py::
stage1_union_screen`、CLI `--s1u`、対象instanceのみ`s1u_eligible`
フラグで限定しコストを抑制)。29 instance中s1u_eligibleは10
(negative7+meta2+hormuz4のうちStage1 PASSの7件+b_group[B2_hormuz/
B3]、実際に1 call追加実行したのは7件[既にBLOCKINGだった3件は
コスト¥0でskip])。**結果**: 7件中6件(85.7%)でS1-DがBLOCKING claim
を新規検出し、**委任_09の3件の重大recall miss(B2_hormuz・B3・
hormuz_run02_advanced)を全件union screenが捕捉し、いずれも
Rewriteで解消(`RESOLVED_REWRITE`)またはdowngrade到達まで進んだ**
(§9-1⑦)。追加固定費¥3.1589(7 call)+捕捉後の下流Stage2/3/Recheck
コスト増を伴う(§9-1⑦のQCD比較参照)。一方、新たに捕捉した
`meta_run03_advanced`は2 cycle以内に解消できずSTAGE4到達した(委任_09
では検出されずACCEPTABLE_STAGE1のまま静かに通過していたclaim。
Escalation化はSafety観点では「見えない見逃し」を「人間が確認できる
STOP」へ変換したものであり、委任文の「過剰BLOCK増分」相当の副作用
として記録する)。採用可否はQCD(固定費増+STAGE4増分1件)とSafety
改善(3件の重大見逃し解消)のトレードオフでありユーザー判断とする
(§9-1⑦「採用推奨と根拠」参照)。

### 3-2. Stage 2: Re-screening(Second Judge)

詳細設計は§4。概要: BLOCKING-candidateのclaim単位で、独立Prompt・
別callにより materiality(BLOCKING/QUALITY/ACCEPTABLE)を判定する。
deterministic safety floor該当時はLLM判定を待たずBLOCKING確定。

- **loop上限**: 1 claim あたり1回(Stage 3 Rewrite後のRecheckで再度
  BLOCKINGになった場合は、cycle残数の範囲内でもう1回発火する。つまり
  「Stage 2呼び出し回数」自体は cycle数(最大2)に連動し、記事あたり
  最大2回)。
- **STOP条件**: なし(Stage 2単独ではSTOPしない。QUALITY/ACCEPTABLEなら
  継続、BLOCKINGならStage 3または cycle枯渇でStage 4)。

### 3-3. Stage 3: Automatic Rewrite

詳細設計は§5。概要: origin(ja_source/translation)に応じてJA側
(既存案B、全文差し戻し)またはEN側(新設計、局所優先)のRewriteを実行し、
Stage 1へ戻してRecheckする。

- **loop上限**: 記事あたり**最大2 cycle**(1 cycle=Rewrite 1回+
  Recheck 1回)。JA側Rewrite(案B)を使った場合、そのcycleはAdvanced/
  Standard両方をリセットする(既存案Bの挙動を踏襲)。EN側局所Rewriteは
  該当stage(Advanced or Standard)のみに影響する。
- **STOP条件**: 2 cycle使い切ってもBLOCKING、または JA Fact Check自体
  がSTOP(`JAFactCheckStopError`、既存の別軸のfail-closed)した場合は
  即Stage 4。**[委任_04改訂/A5]** 加えて、Recheckで再びBLOCKINGとなった
  claim/fact_idがcycle 1でBLOCKING確定した claim/fact_idと**同一**の
  場合は、cycle残数に関わらず即Stage 4へ進む(Rewriteが当該claimに
  効かなかったことが実証されているため、同じ手段への追加投資をしない。
  Safety中立・コスト削減。異なるclaim/fact_idが新規にBLOCKINGとなった
  場合[Hormuz run_03型]のみcycle 2を発火する)。

### 3-4. Stage 4: Final Escalation

詳細設計は§6。

### 3-5. 記事あたりの上限(worst case)

| 項目 | 上限値 | 根拠 |
|---|---|---|
| Stage 2 call数/記事 | 最大2 × (Advanced+Standardの検出claim数) | cycle上限2 × 段階2 |
| Stage 3 Rewrite回数/記事 | 最大2 | 委任文指定 |
| Recheck(Stage 1再実行)/記事 | Rewriteごと1回、最大2 | 委任文指定 |
| JA全文Rewrite(案B相当)/記事 | 最大1(2 cycleのうち1つをJA側に使った場合) | 既存案Bの「1回上限」思想を維持、2つ目のcycleをJA側にも使うかはStage 3設計(§5)で条件分岐 |
| 総API call数/記事(worst case、実測ベースの概算) | 約20〜25 call | Hormuz run_03実測(¥10.35、Advanced 1回 STOP→案B JA regen[JA原本の実測構成: original+check+must_fix+check_retry+r1+r2+r2_check=7 call]+Advanced再実行[1 dev check]+Standard実行[1 dev check]で計10 call相当)に、Stage 2の軽量call(数call)とcycle 2回目のEN局所Rewrite(1〜2 call)を加算した概算。**要実測**(§9) |
| 総費用/記事(worst case、概算) | 約¥15〜25 | 上記call数 × 実測平均単価(Stage 1相当¥0.25〜0.4/call、Stage 2はclaim単位で入力が短いためより安価と推定、Opus論点1推奨4の「2倍未満」見積もりに準拠) |
| 総費用/記事(通常ケース、BLOCKINGなしでStage 2/3不要) | 既存Production実測と同等(¥0.8〜4.2程度、Meta run_03実測¥4.213) | Stage 1のみで完結する記事が大半である前提(既存run_03 Metaの実績) |

**[委任_04改訂/A9]** Stage 2 call数(claim単位、上表「最大2×検出claim数」)
は、instance単位1 callへのbatch化(claim配列入力→materiality配列出力)
を主案として比較する。per-claim callをbatch化前の比較対照として
Phase 1で同一入力に対し両方実行し(§9-1④)、実単価・降格判定の一致度を
実測してから採否を決める(claim間相互汚染のリスクがあるため即断しない)。

## 4. Stage 2 Second Judge設計

### 4-1. 独立Promptの位置づけ

Stage 1の`DEVIATION_PROMPT_TEMPLATE`とは**別物**の新規Prompt
(`SECOND_JUDGE_PROMPT_TEMPLATE_TRIAL`、Family X限定Trial variant、
Production非接続)を新設する。Opus L2レビュー#1論点1推奨4「2段階
呼び出し(detect→materialityを別callで判定)」を採用する。理由:
1回目(Stage 1)は現行Prompt完全据え置きのためSafety資産を保存でき、
Safety regressionリスクが構造的にゼロに近い(Opus所見どおり)。

### 4-2. materiality判定基準(Opus論点1推奨2をそのまま採用)

- **BLOCKING**: Ledgerの`claim`/`scope`/`numeric_value`/`date_or_
  period`/`conditions`のいずれかと**矛盾する**、または**Ledgerが
  別の原因・別の主体を明記しているのに異なるものを述べる**、または
  `notes_for_writer`が明示的に禁じた断定をしている。
- **QUALITY**: Ledgerの観測と矛盾しないが、Ledgerが保証していない
  関係付け(因果接続詞・動機の帰属・強調)が加わっている。
- **ACCEPTABLE**: **[委任_04改訂/A10]** Ledgerに**無い新規の**固有名詞・
  数値・時期・主体・因果を一切加えず(Ledgerに既出の固有名詞[例:
  「ホルムズ海峡」「中東」]を繰り返すことはこの制約に抵触しない、
  Opus論点3(C)への対応)、Ledgerが確認した事象の一般常識レベルの背景
  説明・条件付きの一般論にとどまる。
- **tie-break(fail-closed)**: 上記のどれに該当するか迷う場合は
  BLOCKINGとする(LLM Prompt本文にこの一文を明記)。

### 4-3. deterministic safety floor(§2で確定済み、再掲)

Stage 1のdeviationレコードで`changed_actor`/`changed_number`/
`changed_negation`/`changed_comparison`/`changed_time`/**[委任_04改訂/
A10]** `changed_certainty`のいずれかが`true`の場合、Stage 2はBLOCKING
以外を出力してはならない(LLM出力に関わらずpost-hocでBLOCKINGへ強制
上書き)。この6フラグを選んだ根拠: 前Phase Trial 2 Step1(changed_actor
n=5)でSafety 100%を達成した実績がある「主体・数値・否定・比較・時期」の
直接改ざんは、Ledgerとの矛盾が機械的に一意(paraphraseの余地が最も
小さい)であり、Second Judgeという追加LLM判定を経由させるリスクに
見合わない。**[委任_04改訂/A10]** `changed_certainty`をfloorへ追加した
理由: §7-0でB4-d(certainty変化)を「境界未確定のためTrial上はBLOCKING
[fail-closed]」と確定ラベルしているにも関わらず、floor対象外のまま
だとStage 2 LLMがB4-dを降格させ得るという矛盾(Opus論点3(E))を解消
するため。fail-closed側のラベルとfloorの扱いを一致させる。
**changed_scope/changed_causality/changed_fact/unsupported_new_claim
の4種はfloor対象外**(materiality判定に委ねる。B3[changed_causality]/
hormuz_run03_standard[changed_scope]のようにfloor対象外でもmaterialな
ケースがあることは、Prompt本文のBLOCKING基準1「Ledgerが別の原因を
明記しているのに異なるものを述べる」「scopeと矛盾する」で個別にカバー
する設計とする)。

**[委任_04改訂/A2]** `detected_by="precheck"`(§3-1)のdeviationは、
Stage 1のLLM出力にこの6フラグの値自体が存在しない(Stage 1がそもそも
検出しなかったため)。このケースはfloorの「フラグ判定」を経由できず
空振りする(Opus論点2(C)が指摘する穴)ため、**`detected_by="precheck"`
であること自体を上記6フラグと同格のfloor条件として扱い、Stage 2の
LLM降格を許さずBLOCKING確定**する(§3-1のとおり、precheck FP率実測
[§9-1①]次第でStage 2強制送付[棄却可]へ弱める場合がある)。

### 4-4. 入力(委任_03で確定、§13-3の不整合を解消)

**確定設計**: 記事全文は渡さない。以下4点のみを渡す(Fable第一候補、
委任文§5)。

- **Ledger全文**(該当fact_idの前後だけでなく全文。理由: 別の原因/別の
  条件が離れた箇所に記載されている場合があるため[B3のHF-007
  conditionsが好例]、部分入力では見逃すリスクがある。Ledgerは全文で
  渡す方針を維持=fail-closed優先)。
- source context(JA原文、origin=ja_source/translationの場合のみ、
  既存`source_article_text`引数をそのまま流用)。
- 対象claim(Stage 1の`claim_in_article`)。
- **[委任_04改訂/A8]** Stage 1のdeviation出力のうち`origin`/
  `related_fact_id`のみ渡す。**`explanation`・`severity`・10 category
  flagsはStage 2 LLMの入力から除外する**(Opus論点3(A)のanchoring
  懸念への対応。Stage 1の判断文をStage 2の同一モデルに読ませると
  「materialではない」への降格確率が構造的に下がり、fail-closed
  tie-breakと合わさって二重に保守化するため)。10 flags/severityは
  **Stage 2 LLM呼び出しの外側**でfloor判定(§4-3)にのみ機械的に使う。
- **対象claimを含む段落±1段落**(記事全文からの抽出。前Phase版は
  「前後±1文+記事全文」としていたが、記事全文入力は§13-3で判明した
  費用不整合[保守的見積りではStage 2単価がStage 1と同水準まで上昇]の
  直接原因だったため、段落単位(±1段落、文単位より広く記事全文より
  狭い)へ縮小する。**fail-closedの観点で不足する場合の条件**:
  (a) 対象claimが記事冒頭または末尾の段落にあり前後どちらか一方しか
  存在しない場合はある方のみ渡す、(b) Stage 2 LLMが`basis`判定に
  記事内の別段落の記述が必要と自己申告した場合(`reasoning_summary`に
  その旨が記録された場合)、Trial観測データとして記録し、Phase 1
  実測後に「段落±1で不足する実例があるか」を確認する。実例が確認
  された場合、段落範囲拡大[±2段落]または記事全文への切替えを検討する
  (Cap超過リスクとのトレードオフのためユーザー判断が必要になり得る)。
  Phase 1開始時点では段落±1を暫定確定とし、**実測不足の兆候が出るまで
  記事全文には戻さない**(コスト優先、Ledger全文で大半のfail-closedは
  担保できるという前提)。
  **[委任_04改訂/A8]** LLMの自己申告(上記(b))に加え、**決定論的な
  拡張条件**を設ける: ヘッジ語regex(`may`/`some`/`seems`/`would`/
  `not always`/`only one`等の固定語彙リスト、¥0)で段落±1の**外側**に
  ヘッジ表現が検出された場合、自己申告を待たずに機械的に±2段落へ拡張
  する(Opus論点3(D)、「記事末尾の総括段落のヘッジ」が段落±1で漏れる
  リスクへの対応。自己申告は非決定的で漏れるため、regexを主・自己申告を
  副とする)。

### 4-5. 出力schema(新規、Production schemaとは別)

```
{
  "materiality": "BLOCKING" | "QUALITY" | "ACCEPTABLE",
  "basis": "ledger_claim" | "ledger_scope" | "ledger_numeric_value" |
           "ledger_date_or_period" | "ledger_conditions" |
           "notes_for_writer" | "unsupported_relationship" | "none",
  "qualifier_present": bool,
  "rewrite_hint": string  # BLOCKING時のみ必須。Stage 3が使う具体的な
                          # 修正方針(何を削り何に置き換えるべきか)。
  "rewrite_kind": "delete" | "replace_with_ledger_value" | "narrow_scope",
                          # [委任_04新設/A11] BLOCKING時のみ必須。
                          # delete=Ledger外の付加物を削るだけで解消する型
                          # (B1-c/B3/B4-a相当)。replace_with_ledger_value=
                          # Ledgerの正しい値へ置換する型(changed_actor/
                          # changed_number相当)。narrow_scope=範囲の再限定
                          # が必要な型(hormuz_run03_standard changed_scope
                          # 相当、A2語彙制約と衝突しうる最難関の型)。
  "reasoning_summary": string  # 短い理由(Trial観測用、判定には使わない)
}
```

**[委任_04追記/A11]** `rewrite_kind`ごとの扱い: `delete`型は**LLMを
経由せずStage 3側で決定論的に該当文字列を削除できるか**をまず試す
(最も安く安全、Opus論点4推奨1)。`replace_with_ledger_value`/
`narrow_scope`型はStage 3のLLM局所Rewriteへ回す。Rewrite後、
`delete`型は当該文字列がRecheck対象本文から消えたことを、
`replace_with_ledger_value`型はLedgerの値が本文に出現したことを、
それぞれ機械検証する(Checkerの非検出に依存しない直接確認、Opus論点5
推奨3)。Phase 1では型別の成功率を測定項目に追加する(§9-1⑤)。

**Opus所見の反映**: `observation_consistent`/`ledger_field_basis`を
降格の自動トリガーとして使う設計(V5-C)は実データで既知のBLOCKINGを
複数見逃すことが実証されており**不採用**(§4-3のfloorとbasisフィールド
に置き換える)。`observation_consistent`相当のフィールドは`qualifier_
present`として観測用に残すが、判定ロジックには使わない(Opus論点4-D
「notes分離は判定に使わず観測用として残す」と同じ思想)。

**[委任_10実装・実測]** 委任_09統合dry-runで判明した「Stage2出力schema
に`rewrite_hint`が未実装」を解消した。`er052_open233_self_recovery_
stage2_production_01.py::_ITEM_PROPS`へ`rewrite_hint`(string、
`REWRITE_HINT_INSTRUCTION`でBLOCKING時のみ「逐語引用+修正指示+
fact_id」を要求)を追加し、`PER_CLAIM_JSON_SCHEMA`/`BATCH_JSON_SCHEMA`
双方の`required`へ追加した(既存`er052_open233_self_recovery_stage2_
calibration_01.py::run_stage2_batch_variant`もこのschemaを共有するため
同時に対応)。Rewrite側(`er052_open233_self_recovery_flow_runner_01.
py::locate_target`)は、この`rewrite_hint`から抽出した逐語引用断片
(`extract_quoted_fragment`)を対象文特定の第一キーとして使うよう変更
した。29 instance再実行(§9-1⑦)で、claim単位Rewrite成功率が60.6%→
81.0%(34/42)へ改善したことを実測した。

### 4-6. Stage 1との独立性担保

- 別Prompt定数、別API call(Stage 1の出力を再利用するのみで、Stage 1
  Promptの内部状態を共有しない)。
- モデル/reasoning effort/温度パラメータはStage 1と別途明記(§9で
  Trial実装時に確定。Production Stage 1がgpt-5.6-lunaである一方、
  前Phase Trialはgpt-6-lunaを使用しているため、Phase 1 Trialでは
  **前Phase Trial資産(gpt-6-luna実測データ)との直接比較を優先し、
  gpt-6-lunaで統一する**。gpt-5.6-lunaとの整合確認は別途Phase 2で
  行う、§10リスク参照)。

### 4-7. Phase 1④実測(委任_07、per-claim vs batch・prompt caching・
Stage2較正リスクの新規発見)

**per-claim vs instance batch(B4=4claim/B1=2claim、gpt-6-luna、
`er052_open233_self_recovery_stage2_production_01.py`実装、§4-4
確定入力[Ledger全文+source context+対象claim+段落±1+origin/
related_fact_id、explanation/severity/10flags除外]どおり)**:
- **判定一致率100%**(batch callの各claim判定が、対応するper-claim
  callの判定と全件[B4 4/4、B1 2/2]完全一致。claim間相互汚染は
  観測されなかった)。
- **単価**: B4 per-claim合計¥0.4163(4call)→batch¥0.1862(1call、
  約55%減)。B1 per-claim合計¥0.1787(2call)→batch¥0.127(1call、
  約29%減)。
- **latency**: B4 per-claim合計19.3秒(4call逐次実行)→batch11.845秒。
  B1 per-claim合計7.87秒→batch6.485秒。batchはcall数・費用・
  wall-clock時間のいずれでもper-claimを上回った。
- **結論(A9)**: 本実測範囲(2 fixture、6 claim)ではbatch化を主案
  として採用する根拠が実測で補強された。claim数が増えた場合の
  相互汚染有無は未検証(n_claim=4が本実測での上限)。

**prompt caching**: 同一Ledger全文prefixで連続callを実行した結果、
**cached_input_tokensがinput_tokensの99.9%(B4: 4489/4492、B1:
4335/4338)を占めた**(gpt-6-luna Responses APIで自動キャッシュが
機能することを実測確認、A12)。**費用削減率≈63〜64%**(call全体、
出力token分はキャッシュ対象外のため入力token単体では約90%削減
[$0.10→$0.01/1M]、出力込みの実測削減率は63.2%[B1]〜64.4%[B4])。
**観測上の限界**: 本実測の「call1」は同一Ledgerを用いた直前の
per-claim/batch実測(5call、B4)と連続実行したため、厳密な
「未キャッシュ初回→キャッシュ済み2回目」の対比にはなっていない
(call1の時点で既にキャッシュが温まっていた)。それでも「同一Ledger
prefixの再利用でキャッシュが機能し、費用が実際に下がる」という
受理可否自体は実測で確認できた。

**[委任_07新規発見、重要]Stage 2較正リスク**: per-claim Stage2
(§4-4確定入力どおり、explanation/severity/10flags除外)で、V4Aが
BLOCKING確定していたB1-c相当claim(HF-009市場動機の断定)・B4-a相当
claim(AIフォールバック機構の新規主張、2件)の**全てがQUALITYへ
降格された**(§7-0の確定ラベルではB1-c/B4-aはRewrite対象の
Real-but-fixable群=BLOCKING期待)。rubric基準1(「Ledgerが別の原因・
主体を明記しているのに異なるものを述べる」)がこれらを捕捉することを
設計は期待していたが、実測ではQUALITY(「Ledgerの観測と矛盾しないが
保証されない関係付け」)側に倒れた。**これはS1-D固有の欠陥ではなく、
Stage2 rubric+§4-4入力制限[explanation/severity/10flags除外、
Opus論点3(A)のanchoring対策]自体の較正課題である可能性が高い**
(S1-D・per-claim Stage2の両方で同一方向の誤判定が独立に観測された
ため)。**現時点でProduction非接続のTrial実装であり、Safety事故には
至っていない**が、Phase 1⑤(Stage3 Rewrite成功率実測)実行時に、
B1-c/B4-a相当のReal-but-fixable群がRewrite段まで到達しない(Stage2で
QUALITY止まりになり、Rewriteが発火しない)事象が再現するかを確認する
必要がある。**新しい仕様候補として報告のみ行い、勝手にrubric文言を
変更しない**(rubric改訂[基準1の文言強化、または§4-3
deterministic floorへchanged_scope/causality/unsupported_new_claimの
一部を追加する等]はUSER_DECISION_REQUIRED相当の設計変更であり、
Phase 1⑤の追加実測結果を待ってFable/ユーザーへ提示する)。

### 4-8. Stage 2 rubric較正Trial実測・確定構成(委任_08)

**位置づけ**: §4-7で発見されたStage2較正リスク(Real-but-fixable群
B1-c/B4-aのQUALITY誤降格)への対応。Fable判定(2026-09-30委任文§1)
「Safety方向の較正であり、Trial専用rubric/rule改善はユーザー指示の
自律範囲」に基づき、rubric較正Trialを実行し確定した(Production
Prompt`er003_v1_en_direct_vfl_01_generate.py`は無変更、Trial限定の
`er052_open233_self_recovery_stage2_calibration_01.py`で完結)。

**variant**: R1=現行rubric(既存出力の再利用、0 call)。R2=較正rubric
(QUALITYを「Ledgerに記録された観測同士の関係付け・強調・言い回し」に
限定し、「Ledgerに存在しない新規の具体的主張[製品・仕組み・動機・
理由・因果・数値・主体・時期]は最優先でBLOCKING」を明文化、batch
callで新規実測)。R3=R2のLLM出力+post-hoc floor(Stage1の
`unsupported_new_claim=true`かつR2の`basis`が`ledger_claim`/
`ledger_scope`/`ledger_conditions`/`notes_for_writer`のいずれでもない
場合、BLOCKINGへ強制。新規callなし)。

**評価セット**: 13 batch call・23 claim(B1[a/b/c]、B2、B3、
B4[a/b/c/d]、Meta_run03_standard[2claim]、hormuz_run03_standard、
negative候補7件中V4A BLOCKした4件、Safety群A2A3/A4/A5)、n=2で
26 call実測。**実測費用¥3.1717**(Guardrail¥12、0 error)。

**結果(claim単位、correct labelは§7-0確定ラベル)**:
- **Safety群(A2A3/A4/A5・Meta・hormuz、7claim×2run=14 instance)**:
  R2で**100%(14/14)BLOCKING維持**(誤降格0件)。
- **§4-7で発見された誤降格claim(B1-c/B4-a/B4-d、3claim×2run=
  6 instance)**: R1では6/6ともQUALITYへ誤降格(0%正解)だったが、
  **R2では6/6ともBLOCKINGへ復帰(100%正解)**。既知の較正課題を解消。
- **ACCEPTABLE群(B1-a/B1-b、2claim×2run=4 instance)**: R2で
  4/4正解(over-block無し)。
- **QUALITY群(B2/B4-b/B4-c、3claim×2run=6 instance)**:
  R2で1/6のみ正解(B2が2試行中1回のみQUALITY、B4-b/B4-cは6/6とも
  誤ってBLOCKINGへ)。**新規のover-block(Productivity低下)を確認**
  (Safety強化の代償としての想定内トレードオフ)。
- **negative群(4 fixture×2run=8 instance、正解=非BLOCKING)**:
  R2で7/8(87.5%)が非BLOCKINGへ復帰(Stage1 V4Aは4/4ともBLOCKして
  いたため、Stage1単体の非BLOCK率0%→R2適用後87.5%)。
- **n=2判定一致率**: claim単位21/23(91.3%)で2試行とも同一ラベル
  (不一致はB2・neg3の各1claim)。

**R3(floor)の評価**: floorは**Productivityを大きく悪化させた**
(B1-b[正解ACCEPTABLE]が2/2ともBLOCKINGへ誤って強制降格、negative
4 fixtureのうち3件で少なくとも1試行がBLOCKINGへ誤って強制される)。
一方、floorが無くてもR2単体で本評価セットのSafety群は100%維持できて
おり、floorを追加する必要性がR2単体の実測で裏付けられなかった。
**理由**: Stage1(V4A)は誤検出(over-detection)claimに対しても
`unsupported_new_claim=true`を高頻度で付与するため(B1-b・negative
候補ともに`unsupported_new_claim=true`)、この生フラグを盲目的な
floor条件として使うと、Stage1側の誤検出をStage2が正しく訂正した
結果までも強制的に上書きしてしまう。

**確定構成(委任_08)**: **R2 rubricを採用し、R3 floor拡張[§1で
Trial対象とした案]は不採用とする**(Safety面でR2単独で本評価セットの
既知miscalibrationを解消でき、floor追加はPositive Safety効果が実測で
確認されずProductivity損失のみが観測されたため)。§4-2のrubric本文を
本節R2の文言へ更新し(`er052_open233_self_recovery_stage2_
calibration_01.RUBRIC_R2`)、§4-3のdeterministic floorは既存6フラグ
構成のまま変更しない。B1-c/B4-aをStage2で降格禁止とするregression
fixtureとして`er052_open233_self_recovery_stage2_calibration_01_
test_01.py`へ追加することを次回実装項目とする(本委任では実測のみ、
テスト追加は次回)。**新規の残存課題(報告のみ)**: B4-b/B4-c型
(Ledgerが確認した事象への一般論だが、Ledgerに無い一般的心理・因果を
述べる境界事例)のover-block率が高い(0/6)。これはSafety側には
振れていない(BLOCKINGはRewrite対象になるだけで誤って記事を止める
わけではないため過剰品質コストの範疇)が、Productivity指標として
継続観察が必要(Phase 2候補)。詳細ログ:
`er052_output/open233_self_recovery_stage2_calibration_01/
summary_stage2_calibration.json`。

**[委任_10実測] R2'較正Trial(不採用)**: 委任_09で「negative群R2の
実測Productivityが0/4(0%)」と訂正判明したことを受け、段階的判定手順
(新規の具体的主張チェック→矛盾チェック→言い換えチェック→観測同士の
関係付けチェック→一般常識背景/条件付き一般論チェック→fail-closed)+
一般化した例示を追加した較正rubric`RUBRIC_R2_PRIME`(`er052_open233_
self_recovery_stage2_calibration_01.py`)をn=2で実測した(新規
`er052_open233_self_recovery_r2prime_recalibration_01.py`、20 batch
call・¥3.3977、対象=B1/B3/B4/A2A3/A4/A5+negative実claim4件)。結果:
Safety側で**誤降格が1件発生**(`A4-0`が2試行中1回`ACCEPTABLE`へ
降格)、Productivity側は**改善0件**(B1-aが新たにBLOCKINGへ誤って
降格する退行が発生し、B4-b/B4-c/negative4件はR2と同じく全件BLOCKING
のまま)。委任文の受入条件(誤降格0件かつProductivity改善)を**両方
未達のため不採用**とし、Stage2は既存`RUBRIC_R2`のまま維持する(§9-1⑦
に理由記録)。詳細ログ: `er052_output/open233_self_recovery_r2prime_
recalibration_01/summary_r2prime_recalibration.json`。

### 4-9. Stage 2 rubric R3(自然な解釈基準、委任_12、2026-09-30ユーザー
指示「許容線の再設計」)

**位置づけ**: R2(委任_08採用)の較正基準は「Ledgerに存在しない新規の
具体的主張は最優先でBLOCKING」だったが、実運用でnegative群を含む
「正常記事」への過剰BLOCK・過剰Rewriteが観測されたため、ユーザーが
判断軸そのものを再設計した。**注意**: 本節の"R3"(`RUBRIC_R3_NATURAL_
INTERPRETATION`、`er052_open233_self_recovery_stage2_calibration_01.py`)
は、§4-8で不採用となった旧"R3"(R2 LLM出力+post-hoc floor combo、
`apply_r3_floor`)とは名称のみ類似する**別概念**であり、無関係である
(§4-8参照)。

**最重要原則(ユーザー逐語、§1参照)**: 確認済みのFact同士を、人間が
普通に読めば自然に導く範囲でつなぐ「解釈」は許容する。判断軸は
「完全に証明されているか」ではなく「確認済みFactから人間が普通に
読めば自然に導く範囲か」。評価基準は①元Factと矛盾していないか
②新しい具体的Factを発明していないか③人間が同じ材料を読んで自然に
導ける解釈か④学習者に重大な誤理解を与えるか。

**rubric構成(R2からの主要変更点)**:
1. BLOCKING列挙をユーザーNG5項目((a)Ledger矛盾、(b)Ledgerに無い人物・
   数字・出来事・具体的行動・仕組みの追加、(c)根拠のない意図・動機の
   断定、(d)Fact逆方向の因果、(e)floor5category相当の重大変更)へ
   再構成。
2. QUALITY(通過・Rewriteしない)を「確認済みFact同士を人間が自然に
   導く範囲でつないだ解釈、断定がやや強い場合を含む」へ拡大(R2の
   「関係付け・強調・言い回しに限る」という狭い定義を撤廃)。
3. **tie-break反転(最重要の設計変更)**: R2は「迷ったらBLOCKING」
   (fail-closed)だったが、R3は「NG列挙(a)〜(e)に明確に該当しなければ
   QUALITY」(NG該当が明確な場合のみBLOCKING)。deterministic safety
   floor(§4-3、changed_actor/number/negation/comparison/time)は
   本rubric判定と独立してpost-hocでBLOCKING強制するため維持される
   (LLM側のtie-break反転はfloor非対象カテゴリ[scope/causality/
   certainty/unsupported_new_claim]の判定にのみ影響する)。

**floor改訂(§4-3、changed_certainty除外)**: ユーザーNG5項目に
changed_certaintyは含まれず、「断定がやや強い」はQUALITY側(許容)へ
整理された。委任_04で追加したchanged_certaintyのfloor化(B4-dを
fail-closedへ倒すための暫定措置)は、B4-dが本委任でQUALITYへ再ラベル
された(§7-0改訂)ことと矛盾するため、floorから除外する
(`er052_open233_self_recovery_flow_runner_01.FLOOR_FLAGS`から
`changed_certainty`を削除)。pre-check floor(§4-3後段、
`detected_by=="precheck"`)は変更なく維持する。

**単体較正実測(作業B、委任_12)**: `er052_open233_self_recovery_r3_
natural_calibration_01.py`で、既存評価セット(§4-8と同一13group・
23claim、B1/B2/B3/B4/Meta_run03_standard/hormuz_run03_standard/
negative4[neg1,neg2,neg3,neg5]/A2A3/A4/A5)をn=2で新規call(26 call)。
再ラベル(§7-0改訂): B1-c・B4-dのcorrect_labelをBLOCKING→QUALITYへ
変更(他は§7-0既存ラベルを維持)。

- **R3(素、初回)**: 正解ラベル一致率82.61%(38/46)。**Safety側誤降格
  5件**(Meta-1/Meta-2[Meta_run03_standard]、hormuz-HF009[HF-009 scope
  重大変更、hormuz_run03_standard]、A2A3-1、A4-1、いずれもn=2中1回
  以上QUALITY/ACCEPTABLEへ誤降格)。受入条件(誤降格0件)未達。
- **原因分類**: (a) A2A3-1(HF-006、「原油高→ガソリン・輸送費」)は
  claim内容自体がB1-b(ACCEPTABLE、§7-0)と酷似しており、Safety群
  「実データfixtureの全BLOCKING devをまとめてmust-stay-blocking扱い
  する」という既存の較正harness側の粗い括り(claim単位ではなく
  fixture単位のbundle)に起因する境界事例である可能性が高い。
  (b) A4-1(「相手が実際にAIと話していると思っていた」という未確認の
  主観的認識を断定)は、rubric基準(c)「根拠のない意図の断定」に明確に
  該当する事例だが、tie-break反転後のLLM挙動がこれを安定して捕捉
  できなかった(較正課題)。(c) Meta-1/Meta-2/hormuz-HF009は、
  いずれも「特定の確認済み観測を、より広い/より確定的な主張へ一般化」
  する事例であり、tie-break反転がscope/certainty系の境界判断を
  不安定にした。
- **R3'(1回限りの再較正、`RUBRIC_R3_PRIME`)**: 上記(b)(c)に対応する
  2つの明確化(未確認の主観的認識の断定はBLOCKING/特定指標→市場全体
  等への一般化はBLOCKING、tie-breakでQUALITYへ倒す前に必ず確認)を
  追加。結果: 正解ラベル一致率80.43%(37/46、微減)。**Safety側誤降格
  2件**(A2A3-1[1/2]、A4-2[2/2、新規])。Meta-1/Meta-2/hormuz-HF009/
  A4-1は2/2 BLOCKINGへ復帰(是正成功)。**新規のtrade-off**: 本委任の
  主目的だったB4-d(certainty強化、正解QUALITY)がR3では2/2QUALITY
  (正解)だったのに対し、R3'では2/2BLOCKING(誤り、退行)。B1-cも
  R3では2/2QUALITY(正解)がR3'では1/2BLOCKING(不安定化)。A4-2
  (「可能性」を「確定的結果」として述べる、certainty強化型)は
  R3で2/2BLOCKING(誤り)からR3'で2/2QUALITY(是正、ただしこれは
  §7-0のcorrect_label=BLOCKING[Safety群bundle由来]と不一致であり、
  A4-2の実質的内容[B4-d型のcertainty強化]に照らせば妥当な挙動である
  可能性が高い。これも(a)と同種のbundle粒度起因の境界事例と考えられる)。
- **採否判断**: Fable判定として`RUBRIC_R3_PRIME`をiteration4の29
  instance実行(作業C)へ採用する(hormuz-HF009[本Phaseの中心的
  scope事例]・Meta-1/2・A4-1が安定してBLOCKINGへ復帰することを
  優先し、genuine floor[actor/number/negation/comparison/time]は
  本rubricと独立に維持されているため、残る2件の誤降格[A2A3-1/A4-2]
  はいずれもbundle粒度に起因する境界事例であり真の重大floor崩壊では
  ないと判断)。**ただしB4-dへの新規trade-off(小サンプルでの退行)は
  未解消の残存リスクとして29 instance実測[§9-1⑨]で経過観察する**
  (正式なR3 vs R3'の最終採択はFable/ユーザー判断に委ねる、報告のみ)。
  作業B実測費用¥7.8974(R3実測¥3.7785+R3'実測¥4.1189、Guardrail¥8
  のうち)。詳細ログ: `er052_output/open233_self_recovery_r3_natural_
  calibration_01/summary_r3_natural_calibration.json`・
  `summary_r3prime_natural_calibration.json`。

### 4-10. Stage 2 rubric R3''/R3'''(委任_13、Opus L2レビュー#3所見反映)

**背景**: iteration4実測(§9-1⑨)で、正常記事(negative7+Normal群2=9
instance)の不要Rewrite率44.4%(4/9)が高水準のまま残存した。Opus L2
レビュー#3(`docs/pm/opus_l2_review_open233_self_recovery_03.md`論点2・3)
により、原因の一部がR3'追加明確化2項目(§4-9)の広すぎる適用範囲にある
ことが指摘された: 項目1(「内心の断定」全般をBLOCKING)がB4-d(「驚き」
という一般的反応の記述、正解QUALITY)を捕捉してしまい、項目2(「scope
一般化」全般をBLOCKING)がB1-c(「市場の見方」の記述、ユーザーが許容例と
明示した型)を不安定化させていた。

**R3''(`RUBRIC_R3_DOUBLE_PRIME`)**: R3'の2追記を、Opus文案どおり
「例示」から「原則」へ書き換えた。項目1は「開示・認識の有無そのもの
(知らされていたか/同意していたか/誤認していたか)を事実として述べる
場合」へ限定し、驚き・関心・安心などの一般的な感情や反応の描写は明示的に
QUALITYとした。項目2は「Ledgerが特定の指標・銘柄・期間について観測した
数値や値動き」の一般化に限定し、市場参加者や読者の見方・関心の記述は
これに当たらないとした。

**R3''単体較正結果**(`er052_open233_self_recovery_r3dprime_
calibration_01.py`、既存13group・23claimをn=2、26 call、¥4.267):
是正した正解ラベル(§7-0-iter5、A2A3-1/A4-2をQUALITYへ再ラベル)+
Safety-critical 10claim名指しリスト(A2A3-0/A4-0/A4-1/A5-0/A5-1/
Meta-1/Meta-2/hormuz-HF009/B3/B4-a)を用いて判定した結果、Safety側
誤降格0件・B1-c QUALITY 2/2(是正成功)・**B4-d 2/2 BLOCKING(未達)**・
正解一致率91.3%(42/46、R3'の80.43%を上回る)。B4-dの実際のrewrite_hint
を確認すると、モデルは「相手がAIだと思っていた、または人間だと知って
驚いた」という*個別の具体的な認識*として解釈しており、R3''項目1の
「認識の有無を事実として述べる場合」に該当すると素直に読める(fail-closed
としては妥当な解釈だが、受入条件「B4-d/B1-cがQUALITY 2/2」は未達)。

**R3'''(`RUBRIC_R3_TRIPLE_PRIME`、原則文のみの追加是正、新しい例示は
追加しない)**: 項目1をさらに絞り込み、「特定の個別の事実(誰が・いつ・
どの状況で実際にそう思った/感じたか)として断定している場合」に限定し、
「Ledgerが既に一般的な傾向・現象として記録している内容を、個別の新しい
事実を追加せずに抽象的な言い換え・要約として参照しているだけの場合」を
明示的に除外した。

**R3'''単体較正結果**(同スクリプト`--rubric r3tripleprime`、26 call、
+¥4.1773、累計¥8.4443): **Safety側誤降格0件・B4-d QUALITY 2/2・B1-c
QUALITY 2/2・正解一致率93.48%(43/46)**。受入条件(Safety-critical
10claim誤降格0/B4-d・B1-c QUALITY 2/2/正解一致率≥R3'の80.4%)を
全て達成したため採用する。iteration5のフロー実行(作業D)では
`RUBRIC_R3_TRIPLE_PRIME`を使用する。作業C実測費用合計¥8.4443
(委任文の作業Cガイドライン¥6を超過したが、原因分類の上でR3'''を1回限り
追加した結果であり、iteration5全体のGuardrail¥75・Phase累計残額
¥247.84に対しては十分な余裕内。超過はREPORT §14で明示的に報告する)。
詳細ログ: `er052_output/open233_self_recovery_r3dprime_calibration_01/
summary_r3dprime_calibration.json`・`summary_r3tripleprime_
calibration.json`。

### 4-11. Stage 2の2-of-2安定化(委任_13、Opus L2レビュー#3論点3推奨3)

**背景**: Opus L2レビュー#3実測により、較正(作業B)とフロー実測(作業C)は
同一rubric・同一model・同一入力構造であるにもかかわらず、Stage2判定が
run間で反転する事例が確認された(neg2/neg5とも較正でACCEPTABLE 2/2、
フローでBLOCKING)。これはrubric較正の数値がフロー実運用へそのまま
転移しないことを意味する。

**対策**: negative/Normal群(`NORMAL_GROUP_INSTANCE_IDS`)かつ
deterministic floorが不発(`floor_reason is None`)でStage2がBLOCKINGと
判定した場合のみ、同一Stage2をもう1回呼び(`apply_stage2_two_of_two`)、
両方ともBLOCKINGの場合のみRewriteへ進む(1回でもQUALITY/ACCEPTABLEなら
その判定へ降格し、ログに記録する)。Safety群・B群・precheck floor
claim・deterministic floor経由のclaimは対象外(fail-closedを緩めない、
Safety側の検出力には影響しない)。追加費用はトリガしたclaim数×Stage2
単価(≈¥0.2/claim)のみ。

### 4-12. 丸め許容(委任_14 B-1、2026-09-30ユーザー新方針item1)

**背景**: 数値丸めの誤検出はWriter側ではなくChecker側の問題であり、
「元値から通常の四捨五入で得られる自然な近似値」(2.6%→about 3%、
1.7%→about 2%、$84.73→about $85)は別数値としてNGにしない。「意味が
変わる丸め」(2.6%→about 2%、2.99%→about 2%、84.73→about 100)は
NGのまま。基準=「元値から通常の四捨五入(round-half-up)で得られる
近似値か」。

**実装**: `er052_open233_self_recovery_precheck_01.py`に
`is_natural_rounding(expected, observed)`を新設。候補は(a)整数への
四捨五入、(b)小数第1位への四捨五入、(c)0.5刻みへの四捨五入の3種類のみ
(nearest-10/nearest-100等の粗い丸みは対象外、84.73→about 100を誤って
許容しないための意図的な制約)。`check_number_mismatch`(precheck本体)
と`changed_number_is_natural_rounding_only`(Stage2入力・deterministic
floor向け、related_fact_id経由でLedger numeric_valueと照合)の両方へ
統合した。floor評価直前に`_sanitize_dev_for_rounding`
(`er052_open233_self_recovery_flow_runner_01.py`)がchanged_numberの
丸め誤検出を除去する(他のfloor flagは無変更)。unittest 7件で6例
(ユーザー明示のOK3例・NG3例)+floor混在ケースを検証、全PASS。実測
(iteration6、29 instance×n=2)では該当claimが0件だった(既存fixture
セットにこの型の丸めclaimが含まれていなかったため、実測では未発火。
機能自体はunittestで独立に確認済み)。

### 4-13. floor-cited variant(委任_14 B-2)

**背景**: Fable判定(§2)により、floor(deterministic safety floor)を
「Stage1が対象claimに対しLedgerの具体的値[numeric_value/date_or_period/
明示的なclaim文]を名指しできる場合のみ発火」に絞る floor-cited variant
を、既存のfloor-strict(現行)と併走測定する。

**実装**: `apply_floor_cited`が、`floor_cited_eligible`(related_fact_id
がLedgerに実在し、Stage1のissue/explanationが当該factのnumeric_value/
date_or_period/claimのいずれかを言及[数値token一致または4文字以上語の
2語以上一致]している場合のみTrue)を満たす場合のみBLOCKINGを発火する。
反実仮想として全claimで両方計算し(追加API callなし、¥0)、
`floor_cited_materiality`/`floor_cited_reason`として記録する(実際の
フロー制御は既存floor-strictのまま変更しない)。

**実測結果(iteration6、29 instance×n=2、26 instance overlap分の
combined、詳細REPORT§15)**: floor-strictとfloor-citedが分岐した
claim(floor-cited側が発火しなかった)は全体で1件のみ(`bgroup_B4`の
`changed_comparison`)。**Safety群(12 instance×n=2=24)では分岐0件
(hard gate通過)**。ただし`floor_cited_eligible`は`related_fact_id`の
実在を前提にしており、Stage1がrelated_fact_idを付与しなかった一部の
claim(実測例: `safety_er009_changed_number`、issue文言はLedger数値を
日本語で明示的に引用していたが`related_fact_id`がNoneだったため
floor-citedは判定不能[非発火]扱いになった)では、明確な引用があっても
検出できない既知の限界がある。**採用推奨**: 実測サンプルが小さく
(false-negative候補1件のみ)、上記の`related_fact_id`依存の限界も
未解消のため、floor-strict(現行)を既定のまま維持し、floor-citedは
「より広い測定を継続すべき候補」として記録するにとどめる(独自に
採用判断はしない、Fable/ユーザーへの提示材料)。

### 4-14. セクション判定・Hook専用Stage2(委任_17、§2原因是正)

**注記**: 委任文では本節を「§4-16」と指定していたが、本書§4は§4-13
までしか存在せず(§4-14/§4-15は未使用)、間に空番を作らないため
新規追加分は本書の実採番どおり§4-14として追記する(§6-3の前例と
同じ方針、既存クロスリファレンスへの影響なし)。

**背景**: 委任_16 B-2はTitle/Hook演出許容原則を既存Stage2 rubric
(`RUBRIC_R3_TRIPLE_PRIME`)へ追記し、body/in_one_line/title/hookの
全claimを**同一batch call**内で判定した。代表ケースTrial実測により、
Safety-critical claim(`bgroup_B3`、section_type="in_one_line")が
QUALITYへ誤降格するprompt priming(原則文がプロンプト中に存在するだけで、
条件上は無関係なclaimの判定にも寛容化バイアスが波及する現象)が確認され、
適用対象をtitle/hookの2種のみへ限定する最小修正1回後も再現したため
(§6-4、REPORT§16)、委任文§5のSTOP条件に該当し実配線を撤回した。

**Fable判定・修正方針(委任文§2)**: 原則文を共通rubricへ追記する方式では
なく、**title/hookに位置するclaimの再評価を完全に別のPrompt・別のAPI
callへ分離する**(Hook専用Stage2)。body/in_one_lineのclaimは既存Stage2
(`RUBRIC_R3_TRIPLE_PRIME`、本文は一切変更しない)のまま判定する。2群が
別々のAPI callであるため、一方のprompt文言(Hook演出許容原則)が他方の
判定コンテキストへ物理的に混入する経路が存在せず、prompt primingを
構造的に遮断する。

**A-1 セクション判定(既存`detect_claim_section_type`、変更なし)**:
claimが記事のどこに位置するかを、既存`locate_best_sentence`を再利用した
決定論的Jaccard類似度判定で以下の4区分に分類する(¥0)。

- **title**: 記事先頭行(`_paragraph_title`、Markdown見出し記号を含む
  生の1行)との類似度[閾値0.4]または部分文字列一致。
- **hook**: 本文第1段落(`_first_body_paragraph`=`_split_paragraphs_
  nonheading`が返す最初の段落、「#」始まりの見出し行は除外)との
  類似度[閾値0.3]。
- **in_one_line**: 「## In one line」見出し直後の1段落(`_extract_in_
  one_line_text`)との類似度[閾値0.4]。
- 上記いずれにも該当しなければ**body**。

**境界例(既知の限界、委任文§3 A-1要求)**: hookが実質2段落以上に
またがる構成(例: 場面描写が2段落連続する記事)であっても、本判定は
常に`paras[0]`(最初の1段落)のみをhook候補として扱う。2段落目以降の
場面描写は本判定では「body」に分類され、Hook専用Stage2の対象外の
まま既存Stage2(body経路)で判定される。iteration1〜6・rep7のfixture群
ではこの境界例に該当する記事は確認されていない(将来fixtureで該当例が
出た場合、body経路[fail-closed寄りの既存rubric]で判定されるため安全側
に倒れる、Hook演出許容が及ばずBLOCKINGへ倒れやすい方向の限界であり
Safety側のリスクではない)。

**A-2 Hook専用Stage2**(新規`er052_open233_self_recovery_stage2_hook_01`
=s2h、既存`stage2_production_01`/`stage2_calibration_01`は変更しない):

- 対象: `HOOK_ONLY_STAGE2_SECTION_TYPES = {title, hook}`のみ(in_one_line
  は対象外。§6-4の既存post-hoc downgrade用`HOOK_SECTION_TYPES`
  [title/hook/in_one_line]とは別の定数であり、Hook専用Stage2の入力
  ルーティングにのみ使う)。
- 入力: Ledger全文+source context(JA原文、参考)+タイトル・hook段落
  のみ(`build_title_hook_context`、既存のローカル文脈±1段落
  [`s2p.build_local_context`]は使わない、意図的な縮小)+対象claim配列。
  対象claimを含む段落±1段落のような広い文脈は渡さない。
- schema: materiality/basis/rewrite_kind/rewrite_hint(既存Stage2
  productionの`_ITEM_PROPS`をそのまま再利用、フィールド自体は変更
  しない)。
- rubric: 「Title/Hookは読者を引きつける演出の場。確認済みのFactから
  人間が自然に導ける情景描写・呼びかけ・比喩・誇張のない強調はQUALITY/
  ACCEPTABLEとしてRewriteしない。BLOCKINGは(a)新しい具体的な人物・数字・
  出来事・行動・仕組みの発明、(b)Ledgerとの矛盾、(c)逆方向の因果、
  (d)actor・number・negation・comparison・timeの重大な変更、のみ」
  (`HOOK_RUBRIC`)。tie-break: 迷う場合は「発明の有無」で判定し、発明が
  なければQUALITYとする(委任文§2どおり明記)。

**A-3 runnerの分岐実装(`run_stage2`)**: Stage2対象claimを
`detect_claim_section_type`の結果でhook群(title/hook)とbody群
(body/in_one_line)へ分割し、body群は既存`s2c.run_stage2_batch_variant`
+`RUBRIC_R3_TRIPLE_PRIME`(iteration4〜6・rep7と同一プロンプト内容、
不変)、hook群のみ`s2h.run_stage2_hook_batch`(別call)を呼ぶ。いずれかの
群が空ならそのAPI callは発火しない(該当claimが無ければ追加コスト
0)。各群の呼び出しは独立にMAX_RETRIES_PER_CALL回まで再試行し、
リトライを使い切って失敗した場合は**その群のclaimのみ**
fail-closedでBLOCKING確定とする(§6-1の既存fail-closed原則を、group
単位へ自然に拡張したもの。他方の群が成功していれば、その群の判定は
そのまま活かす。既存の上限回数・fail-closedの厳しさそのものは一切
緩めていない)。各claimの出力へ`stage2_route`(body/hook/
{group}_api_failure_failclosed/{group}_schema_index_mismatch_
failclosed/precheck_floor_bypass)をEvidenceとして記録し、どちらの
経路を通ったかをinstance json上で直接確認できるようにする。

**deterministic floor/pre-checkの維持**: Hook専用Stage2の判定結果
(`materiality`)は、既存どおり`apply_floor`/`apply_floor_cited`
(§4-3/§4-13、FLOOR_FLAGS=changed_actor/number/negation/comparison/
time)を経由する。pre-check floor(`detected_by=="precheck"`)は
Stage2自体を経由しない既存経路(§3-1)のままであり、いずれもHook専用
Stage2の新設によって回避・弱体化されていない(委任文§3「Safety 12は
改竄fixtureなのでfloorで止まる」の要求どおり)。既存の§6-4 post-hoc
downgrade(`apply_hook_aware_downgrade`、changed_scope単独限定)も
変更せず、Hook専用Stage2の判定結果に対して引き続き同一ロジックで
適用される。

**A-4 unittest(¥0、`er052_open233_self_recovery_flow_runner_01_
test_01.TestHookOnlyStage2Separation`、4件)**: (1) neg1のhook claim
(“Ring, ring. …”)をmock Hook専用StageでQUALITYと判定させ、body群
(`s2c.run_stage2_batch_variant`)が一切呼ばれない(`MagicMock.assert_
not_called()`)ことを確認、(2) `bgroup_B3`の因果claim(section_type=
"in_one_line")がbody経路(`RUBRIC_R3_TRIPLE_PRIME`)を通り、Hook専用
Stage2(`s2h.run_stage2_hook_batch`)が一切呼ばれないことを確認しつつ
BLOCKING維持を確認、(3) `changed_actor`floorを持つhook区分claimに
Hook専用StageがQUALITYを返しても、floorにより最終的にBLOCKINGへ
強制されることを確認、(4) hookに新しい具体的事実を発明した合成claim
に対しHook専用StageがBLOCKINGを返すケースの基本疎通を確認。

### 4-15. 不要Rewrite4件の解決策(委任_18 2-2、iter6全件開示§1-2是正)

**注記**: 委任文では本節を「§4-17」と指定していたが、本書§4は§4-14
までしか存在せず(§4-15/§4-16は未使用)、間に空番を作らないため新規
追加分は本書の実採番どおり§4-15として追記する(§4-14の前例と同じ方針)。

**背景**: disclosure §1-2は不要Rewrite4件(分母9、v2訂正後)を原因別に
分類した: (1) `neg1_meta_b3prod_a2`=Hook誤判定(委任_17で対象内、§4-14で
解消済み・実測確認はrep9)、(2)(3) `neg2_meta_refresh_a2`/
`meta_run03_advanced`=同一Ledger fact「MUSE-HC-012」・同一パターン
(「テストが適切な開示なしに始まった」という確認済み条件から、「利用者は
実際に気づかなかった/知らなかった」という帰結を導く記述を新規主観断定と
誤BLOCK)、(4) `neg3_hormuz_prodrunner_b1b`=floor+LLM独立判定一致
(`changed_time`解釈、iteration間でLLM判定自体が非決定的)。

**(2)(3)の解決策(`apply_disclosure_gap_downgrade`)**: disclosure §2-2が
提示した2方式のうち、本委任は**(ii) deterministic post-Stage2条件**を
採用した(理由: (i)共通rubricの例示リスト追記は委任_16 B-2が実測した
prompt priming[Safety-critical `bgroup_B3`誤降格]のリスクを再度負う
うえ、較正セット全体の再実行がGuardrail内に収まらない。(ii)は¥0・
追加API callなし・既存floor/hook-aware downgradeと同型のpost-hoc判定
パターンを踏襲でき、対象を狭い決定論条件に限定できるため安全側)。

条件: floor不発火(既存floorには一切触れない)+
`unsupported_new_claim`または`changed_certainty`のいずれか+
FLOOR_FLAGS+changed_scopeがいずれも不発火+claim文言が「知る手段が
なかった/気づかなかった」系の**否定形**(`DISCLOSURE_GAP_NEGATION_RE`、
方向性を否定形のみへ限定し、neg1のような肯定形の主観断定[「驚いた」
「気づいた」等]には適用しない、disclosure §1-2-5の整理どおり)+
claimがLedger本文に無い新しい数値・固有名詞を追加していない(既存
precheck抽出器を再利用)。全条件を満たす場合のみBLOCKING→QUALITYへ
downgradeする。**Trial限定の判定候補であり、Production採用
(`APPROVED_FOR_PRODUCTION`)には別途ユーザー承認が必要**
(Production[er003/er009/er010/er012/er019]には配線しない)。

**(4)neg3は解決策なし(disclosure §1-2-4の結論を維持)**: `neg3_
hormuz_prodrunner_b1b`は同一claim文言に対しLLM自身の判定がiteration間で
非決定的(iter4/5はQUALITY、iter6はBLOCKING、いずれもfloor起因ではなく
LLM自身が独立にBLOCKINGと判定したrunが存在する)。floorを緩めるだけでは
解消しない可能性が高く、単純なrubric一箇所修正では再現性のある解消が
保証できないため、本委任でも確定的な解決策は実装しない(disclosureの
推奨どおり、次委任でこのclaim単体のn≥3再現性測定が必要)。rep9では
従来どおりfloor維持のまま従来のRewrite経路が機能することのみ確認する。

### 4-16. Stage 1同一fact_id列挙(委任_20 W2)

**注記**: 委任文では本節を「§4-18」と指定していたが、本書§4は§4-15
までしか存在せず(§4-16/§4-17は未使用)、間に空番を作らないため新規
追加分は本書の実採番どおり§4-16として追記する(§4-15の前例と同じ方針)。

Stage 1初回・Recheckの出力schemaへ`same_fact_id_locations`を追加し、
記事内の同一fact_id別箇所(title/hook/in_one_line含む)を追加callなしで
列挙・展開する仕組みの詳細は§6-8に記載する(Stage 4 Escalation条件・
全文Recheck省略条件と一体で設計・実装したため、本節では概要のみを示し
重複記載を避ける)。

### 4-17. neg1 MUSE-HC-006境界事例の分析(委任_21 A-3)

**注記**: 委任文では本節を「§4-19」と指定していたが、本書§4は§4-16
までしか存在せず(§4-17/§4-18は未使用)、間に空番を作らないため新規
追加分は本書の実採番どおり§4-17として追記する(§4-14/§4-16の前例と
同じ方針)。

**背景**: rep11(委任_20)で`neg1_meta_b3prod_a2`(不要Rewrite0件が
正解の負例群、§7-0)が2/2 sampleとも新規claim(MUSE-HC-006、hook区分)
でRewriteが発生した(委任_17で解消した「Ring, ring…」claimとは別文)。
本節はこれが(a) Hook専用Stage2の対象外だったための誤判定か、(b)
許容線(自然な解釈 OK/新しい具体的Factの発明 NG)でBLOCKING/QUALITY
いずれが妥当か、(c) 既存条件(Hook専用rubric/disclosure-gap downgrade/
丸め)のどれが適用され得るかを分析する。

**claim原文・Ledger fact・Stage判定(rep11実データ、`instances_s1/
neg1_meta_b3prod_a2.json`より逐語引用)**:
- claim_in_article: “A call seemed to come from an AI agent. But as
  the conversation went on, the voice was not AI at all. It was a
  person. Meta had run a test that caused exactly this surprise.”
- Ledger fact(MUSE-HC-006、`full_ledger.json`より逐語):「MetaはMuse
  経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが
  電話をかけ、相手とのやり取りを完了させる「human concierge」「human
  agent calls」のテストを実施した。」notes_for_writer:「全ての電話を
  人間が担当したとは書かない。「一部の電話」「テスト」と限定する。」
- Stage1 dev.issue: “The article presents a recipient discovering
  during a call that a person, not AI, was speaking, and says the
  test caused this surprise. The Ledger verifies that trained
  contract workers made some Muse calls, but does not establish that
  recipients experienced this reveal.”
- section_type/stage2_route: `hook`/`hook`(Hook専用Stage2で判定済み。
  §4-14のtitle/hook/in_one_line対象範囲に正しく含まれており、**(a)は
  該当しない**=Hook専用Stage2の対象外だったための誤判定ではない)。
- floor_reason/floor_cited_reason: いずれも`null`(既存
  deterministic floor[changed_actor/number/negation/comparison/time]
  にも、meta_run03_standard MUSE-HC-012で適用された`disclosure_gap_
  negative_inference_downgrade`[委任_18 2-2]にも該当しない。後者は
  「〜と気づかなかった」等の**否定形**の論理的帰結を対象とする狭い条件
  であり、本claimは「AIだと思ったら人だった」という**肯定形の物語的
  展開**であり形が異なるため、floor_reason=nullは既存条件の適用対象外
  という意味で妥当)。

**(b)許容線の判定**: Ledger factは「一部のMuse経由電話を人間スタッフが
担当するテストを実施した」という構造的事実のみを確認しており、「ある
特定の通話で、会話の途中にAIだと思っていた相手が実は人間だったと気づく
驚きの瞬間」という**受け手視点の具体的な体験・出来事**までは確認して
いない。Hook専用Stage2 rubric(§4-14)のBLOCKING条件(a)「新しい具体的な
人物・数字・出来事・行動・仕組みの発明」に文字どおり当てはめれば、
「会話中に気づく」という具体的な展開の発明と読める。一方、記事タイトル
自体が「We Thought It Was AI—But There Was a Person Inside Meta's
Muse」であり、この一文はHookの核となる同一主題の劇的表現(情景描写に
近い演出)とも読め、rubricのtie-break規定「迷う場合は発明の有無で判定
し、発明がなければQUALITYとする」の境界上にある。**本claimは委任文
基準(a)〜(d)のいずれにも機械的に該当するが、rubric自体が想定する
「演出として許容すべき誇張のない強調」との境界が曖昧な、真にdisputed
な事例**と判定する。

**(c)実証(非決定性の直接確認)**: rep11(2/2 sample)は本claimを
BLOCKINGと判定しRewriteへ進んだが、コード変更なしで再実行したrep12
(2/2 sample、同一fixture・同一Hook専用Stage2 rubric)は本claimを2/2
とも`RESOLVED_STAGE2_DOWNGRADE`(Stage2自体が非BLOCKINGへ判定、
Rewrite不要)で完了した。同一rubric・同一fixtureでBLOCKING/非BLOCKING
双方が実測されたことは、本claimがLLM判定の閾値付近にある真の境界事例
であることを裏付ける(rubric自体にバグがあるとは断定できない)。

**結論**: 本claimはコードのバグや既存条件の誤適用ではなく、Hook専用
Stage2 rubric自体が抱える「物語的な劇的表現」と「具体的な出来事の発明」
の境界上のdisputed事例と判定する(既存の`neg3_hormuz_prodrunner_b1b`
と同種の扱い)。**コード変更は行わない**(rubric・floor条件のいずれも
変更しない)。不要Rewrite率の集計では、rep11実行分について本claimを
neg3と同様にdisputed注記付きで両建て報告する(REPORT§21参照)。rubric
tie-break文言の明確化(「会話中の気づき」のような物語的展開を演出側へ
明示的に含めるか)の要否は、Fable/ユーザー判断としてOPEN_ITEMSへ記録
する(本委任のスコープ外、コード変更を伴うため)。

### 4-18. 重大誤解原則の追加(委任_27 Part1-5、§0参照)

Stage1(V4A checker、`er051_open233_checker_trial_variant_01.py`)・
Stage2 body rubric(`RUBRIC_R3_TRIPLE_PRIME`)・Hook専用rubric
(`HOOK_RUBRIC`)それぞれに、判定の**最初の問い**として§0-1/§0-2の
原則文(逐語)を追加する。実装は既存rubric本文を書き換えず(既存
iteration証跡の再現性維持、委任_13/16の教訓どおり)、新定数として
追加する:

- Stage2 body: `RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE`
  (`er052_open233_self_recovery_stage2_calibration_01.py`、
  `RUBRIC_R3_TRIPLE_PRIME`+原則文+§0-2の許容/BLOCK候補リスト)。
- Hook: `HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE`
  (`er052_open233_self_recovery_stage2_hook_01.py`、`HOOK_RUBRIC`+
  同原則文の短縮版)。
- Stage1(V4A): `V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`
  (`er051_open233_checker_trial_variant_01.py`、`vfl01.DEVIATION_
  DEVELOPER_MESSAGE`[Production定数、読み取り専用参照]+原則文)。
  `run_trial_deviation_check()`へ`developer_message_override`引数
  (既定None、既存9箇所の呼び出しは無変更で動作)を追加した。

**deterministic floorは維持する**(`changed_scope`はfloorに含まれ
ないため無変更、floor対象の8種は本原則の影響を受けない設計のまま)。

**priming再測定の要件(委任_16の教訓)**: 共通rubricへの原則文追記は
過去にprompt priming(無関係なclaimまで寛容化)を起こした実例がある
ため、本原則文を実際にStage2判定へ配線する場合は、Safety-critical
claim + Safety fixtureを必ず同時に対照群として測定し、1件でも誤降格
(non-BLOCKINGへ変化)すればその変種は不採用とする(§9-1⑰で実測)。

**本委任での実配線範囲(予算制約による正直な開示)**: ¥25 Guardrail
(Part2実績¥2.2597)内で実測できたのは**Stage2 body rubricのみ**
(Hormuz要素とSafety対照群、§9-1⑰)。Stage1(V4A)・Hook専用rubricへの
原則文追加は本節の定数として追加済みだが、**実際のStage2/Stage1
呼び出しへの配線・実測は未実施**(次回委任_28[Meta要素Trial]または
その後の広いTrialへ引き継ぐ、既知の未検証事項)。

**Trial A実測での最小修正1回(§9-1⑰詳細)**: 初回rubric
(`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE`)でhormuz
accept-1("Oil prices did not fall across the whole market after the
plan was withdrawn.")が2/2 false BLOCKだったため、「Brent先物を
同じoilという対象のままより一般的な言い方に置き換えるだけの場合は
許容する」明確化を追加した`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_
PRINCIPLE_V2`を新設し、再実測n=2で全群(許容5・NG5・Safety2)の
false PASS/false BLOCKが0件になることを確認した(詳細REPORT§25)。

**委任_28追記(Stage1/Hook配線の実装・Safety対照群全量確認の結果)**:
Stage1(V4A)・Hook専用rubricへの実配線自体(自己完結ヘルパー・
`hook_rubric_text`引数)は委任_28で実装した(§9-1⑱)。一方、Stage2
body rubricをSafety-critical 9claim+Safety12全量で対照測定したところ
A4-0は最小修正1回(V3)で解消したが、**A5-1・Meta-1/Meta-2の計2件が
V3でも残存**(false downgrade、§9-1⑱)し、委任文のSTOP条件に該当した
ため、Meta要素Trial(Hook/Actor)は未実施のまま停止した。**Stage2 body
rubricへの重大誤解原則配線は、本書時点では依然としてSafety側の懸念が
解消しておらず、Production採用はもちろんさらなるTrial拡大の前提にも
できない**(詳細REPORT§26、Fable/ユーザー確認事項)。

(§4-19/§4-20は本書では欠番。委任_29委任文が§4-21/§4-22を明示的に
指定したため、その番号のまま追加する。)

### 4-21. Stage2 body rubric V4(Meta-1/Meta-2 false downgrade是正、委任_29 Part1)

委任_28のSTOP原因のうち、A5-1はFableラベル判定により再ラベル
(§7-0-iter29、Safety-criticalから除外)で解消する一方、Meta-1/Meta-2
(“Also, some calls needed user information to continue.”)は
Safety-critical維持のまま、rubric側の最小修正1回で是正する対象とした。
Ledgerの実際の記録(related_fact_id=MUSE-HC-010、conditions:
「電話の遂行にユーザー情報が必要となる場合」という条件付きの可能性)を、
記事がその条件を外し「実際に起きた」と断定している(changed_fact=true・
changed_certainty=true)。これは§0-2の「未確認の人物・行動・動機・
数字の追加」に該当する誤解であり、A5-1型(役職の同一対象内一般化、
許容)とは別物として明示的に区別する必要がある。V2/V3は「当事者関係の
取り違え」と「役職の一般化」の2区分のみで、「条件付きの可能性→既成
事実への断定(certainty強化)」を独立した原則として扱っていなかった
ため、誤ってQUALITYへ寛容化していたと判断する。

是正: `MISCONCEPTION_PRINCIPLE_TEXT_V4`(`er052_open233_self_recovery_
stage2_calibration_01.py`、V3へ1段落を追加するのみ、新しい例示は
追加しない)。`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V4`
として実測(新規`er052_open233_element_trial_safety_control_02.py`、
既存`..._01`は不変)し、Safety-critical 8claim(A5-1除外後)+
Safety12(er009 9フラグ)+Hormuz許容5/NG5の全てでn=1予備測定・n=2
公式測定ともmisdowngrade/false PASS/false BLOCK 0件を確認した
(§7-0-iter29・§9-1⑲、費用¥4.9438)。

### 4-22. Hook専用rubric V3(scene-depiction/dramatization false block是正、委任_29 Part2)

委任_28で実装済み・未実行だった`er052_open233_element_trial_meta_
hook_01.py`を本委任で初めて実行したところ、集計コード自体に符号反転
バグがあることが判明した(ng群のBLOCKING[正しい]をfalse_passへ、
accept/boundary群の非BLOCKING[正しい]をfalse_blockへ、誤って計上)。
`tally_hook_rows()`として是正し(API呼び出し・生judgmentデータは
無変更、集計式のみ是正)、unittest(`TestMetaHookTallyScoringBugFix`)で
再発防止した。

是正後の真の値(V2、`HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`):
NG群4/4は全run BLOCKING(false pass 0件)。一方、accept-4
(“Ring, ring. The phone connects, and for a moment neither side lets
on who is really speaking.”)・boundary-1(“The surprise came halfway
through the call.”)が毎回false block、元Hook(accept-1、実際の公開
記事本文)も1/3 runでfalse blockした。rewrite_hint逐語が示す原因は、
確認済みの中心的な出来事(AIだと思っていたら実は人間だった)を読者に
体験させるための自然な時間経過・雰囲気描写を、「具体的で未確認の新しい
行動・タイミングの発明」と誤認していたことである。

是正(最小修正1回): `HOOK_TIEBREAK_TEXT_V3`
(`er052_open233_self_recovery_stage2_hook_01.py`、既存`HOOK_TIEBREAK_
TEXT`へ1段落追加のみ)で、確認済みの出来事を自然な時間経過として描写
する演出(「しばらくの間」「会話が進むうちに」等のおおまかな時間経過・
雰囲気描写)は、Ledgerに無い具体的な人物・数字・仕組みを発明しない
限り許容する旨を明記した。Hook Stage2のみ再実行(Stage1 fresh再測定は
rubric非依存のため省略、¥1.9481)したところ、**元Hook(3/3)・accept-4は
解消したが、boundary-1(境界群)は2/2 false blockのまま残存**した。
委任文STOP条件(「元Hook誤BLOCKまたはNG誤PASSが小修正後も残る」)には
該当しないため、境界群単独の残存はSTOPせず残課題として記録する
(§9-1⑲、Fable/ユーザー確認事項)。

### 4-23. Hook専用rubric V4(boundary-1残存の解消)+runner既定化+paired_rewrite片側locate是正(委任_30)

**(a) Hook rubric V4**: §4-22の境界群残存(boundary-1-dramatization
“The surprise came halfway through the call.”)に対し、Fable(§1)が
design書§10の境界例定義「演出がやや強いが、新しい具体Factを追加して
いないHook」に該当し許容が正解と判定した。`HOOK_TIEBREAK_TEXT_V4`
(`er052_open233_self_recovery_stage2_hook_01.py`、既存
`HOOK_TIEBREAK_TEXT_V3`へ1段落追加のみ)で、「通話の途中で」のような
曖昧な時間経過・順序の演出は新しい具体的Factの追加ではないという
tie-break判定軸を明記した。再測定(n=2、boundary-1・元Hook accept-1・
NG4群、¥0.7000)の結果、**boundary-1(2/2非BLOCKING)・元Hook
(2/2非BLOCKING)・NG4群(各2/2 BLOCKING)の全てが期待どおりとなり、
false block/false pass 0件を達成した**(§9-1⑳、
`er052_open233_element_trial_meta_hook_02.py`)。

**(b) runner既定化**: 重大誤解原則(Stage1 V4A・Stage2 body V4・Hook
V4)を、Trial要素実測でのみ検証していた状態から、
`er052_open233_self_recovery_flow_runner_01.py`本体の既定経路へ実配線
した。新設フラグ`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`(既定True)で
制御し、Falseで配線前の挙動(既存iteration1〜7・rep7〜15と同一)へ復帰
できる。`BODY_RUBRIC_DEFAULT`/`HOOK_RUBRIC_DEFAULT`をモジュール定数と
して追加し、`run_stage2`内の2箇所(body/hook)の呼び出しを書き換えた。
Stage1は`stage1_fresh_with_enumeration`へ`developer_message`引数
(既定値=既存Production非接続のvfl01定数、後方互換)を追加し、
`run_instance`が`use_misconception_principle`(既定True)に応じて
重大誤解原則配線版developer messageを渡すようにした(既存
`stage1_fresh_with_misconception_principle`[委任_28、enum非対応の
自己完結版]は変更せずTrial専用のまま残す)。

**(c) paired_rewrite片側locate是正(Part3 FAILの根本原因修正)**:
rep16実測(§9-1⑳)で`neg3_hormuz_prodrunner_b1b`がSTAGE4_ESCALATION
(stage4_reason=`ladder_exhausted_without_full_rewrite`)になった。
原因分析の結果、`paired_rewrite`は`en_located and ja_located`(両言語
特定)の場合のみ①〜④のladderを試行する実装であり、**片側のみ対象文が
特定できた場合(本caseはJA側のみexact_substringで特定、EN側は別cycle
で既に解決済みのため元claim文言が現存しない)、ladder構築自体が一度も
実行されずmethod=Noneのまま、直後の⑥(既定OFF、委任_23 B-2)判定へ
落ちて0 callでStage4に至る**という設計上の穴であることが判明した
(⑥(全文フォールバック)を再有効化せず、片側のみの局所編集機会を
一度も試みていなかった点が真因であり、⑥自体の既定OFF判断[committed_23]
とは別の問題)。

是正(小修正1回): `en_located != ja_located`の新設elif分岐で、
特定できた側だけを対象に既存`single_text_rewrite`(①〜④の非⑥ローカル
編集ラダー、新規テンプレートは追加しない)へ委譲する
(`j1_single_side_en`/`j1_single_side_ja`)。未特定側は変更しない。
unittest 2件(`test_paired_rewrite_partial_locate_delegates_to_single_
text_rewrite`/`_falls_through_to_stage4_when_single_side_also_fails`)
で再発防止した。実際に失敗していたclaim(fact:HF-003のJA再出現箇所)を
cycle0 rewrite後の状態から再構成して単体検証した結果、
**guard_ok=True・method=`j1_single_side_ja(e1_minimal_word_edit(
exact_substring))`・ladder_level_used=`1_word_connective`で解決した**
(¥0.0758、`er052_open233_self_recovery_flow_runner_01_rep16_neg3_fix_
verify_01.py`)。本修正は`single_text_rewrite`を単体で呼ぶだけの
委譲であり、⑥(全文フォールバック、既定OFF)の再有効化ではない。

### 4-24. 主体置換ガードの常時評価+Hookセクション境界拡張(締め文)+body rubric V5(委任_31 Part1)

委任_30 rep16実測で残った3点(Fable判定§1(a)(b)(c)、委任文§1)のうち、
(a)(b)の是正コードをここに記録する((c)はneg3のn=2再実行そのものであり
コード変更ではないため§9-1の実測ログのみに記録する)。

**(a) 主体置換ガードの常時評価(actorガード盲点の是正)**: 委任_30 Trial
C期待2で発見した設計上の盲点(`classify_problem_kind`の優先順位
[term_scope>causality>actor>time]により、changed_scope/changed_actorが
同時に真のclaimではproblem_kind="term_scope"に分類され、主体置換ガード
[`actor_rewrite_guard_ok`、旧実装は`problem_kind=="actor"`の場合のみ
発火]が一度も評価されなかった)を是正する。`single_text_rewrite`/
`paired_rewrite`両方の呼び出し箇所で、`problem_kind == "actor" and not
actor_rewrite_guard_ok(...)`という条件から`problem_kind == "actor"
and`部分を削除し、**problem_kindに関係なく常に`actor_rewrite_guard_ok`
を評価する**よう変更した。`actor_rewrite_guard_ok`自体は新しい主体語が
導入されない場合は常にTrueを返すno-op設計(§0-5既存仕様)であるため、
常時評価してもunspecified/term_scope等の既存経路への非回帰影響はない
(既存unittestの結果は変わらない、新規のみ追加)。unittest 1件
(`TestActorGuardAlwaysEvaluatedRegardlessOfProblemKind`)で、Trial C
期待2の実データ(changed_scope=True・changed_actor=True・
"users"→"employees")が、是正後は実際に却下されることを確認した(¥0)。

**(b) Hookセクション境界拡張(締め文を条件付きで含める)+body rubric
V5(neg1の不要Rewrite是正)**: neg1実例(「Meta had run a test that
caused exactly this surprise.」→「Meta had run a test.」のRewrite)は、
確認済みの中心的な出来事(開示なしに人間が電話をかけていた)から自然に
導ける、Hook導入文の締め文であり、重大誤解原則では本来Rewrite不要
(削除はHookの落ちを消す品質劣化)とFableが判定した。根本原因は
`detect_claim_section_type`/`build_title_hook_context`が常に段落①
(Hook導入文)のみをHook候補とし、段落②(締め文)を無条件に「body」へ
分類していたため(§4-14既述の既知の限界)、この1文がHook専用rubric
(緩やか)ではなく本文rubric(厳格)で判定されていたことにある。

是正は以下2点:
1. 新設`_hook_paragraph_block()`で、Hookの範囲を「段落①+条件を満たす
   場合のみ段落②」へ拡張する。段落②を無条件に含めると、hormuz_run03_
   standard/meta_run03_standard/bgroup_B3/neg3_hormuz_prodrunner_b1b
   実測(段落②が複数文・具体的な数字/日付を含む本文段落)でSafety回帰
   (本文のmaterial claimをHook専用[緩やか]rubricへ誤って振り分ける
   リスク)が生じるため、意図的に保守的な決定論ヒューリスティック
   (¥0)で絞る: 段落②が(i)1文のみ、かつ(ii)数字を含まない場合に限り
   Hookへ含める。neg1の段落②("Meta had run a test that caused exactly
   this surprise.")は1文・数字なしのため該当し、hormuz/meta_run03_
   standard/bgroup_B3/neg3の段落②(いずれも複数文、または具体的な数字/
   日付を含む)は非該当のまま(既存実測fixtureで検証、unittest
   `TestHookParagraphBlockBoundary`4件・`TestDetectClaimSectionType`
   更新2件)。
2. 防御層として、body rubric(`RUBRIC_R3_TRIPLE_PRIME_WITH_
   MISCONCEPTION_PRINCIPLE_V5`、`MISCONCEPTION_PRINCIPLE_TEXT_V4`へ
   最小1段落追加)を新設し、「確認済みFactから導ける受け手側の驚き・
   反応の言及は新規Factの追加ではない」ことを明記した(同じclaimが何らか
   の理由でbody rubric経路に残った場合の保険、新しい例示は増やさず既存
   V4の区別[条件付き可能性→既成事実への断定はcertainty強化として
   BLOCKING維持]とは明確に別物として記述、priming回避のため新しい
   例示は追加しない)。`BODY_RUBRIC_DEFAULT`をV4からV5へ昇格する前に、
   priming再測定の要件(委任_16の教訓)どおりSafety-critical 8claim
   (B3を含む、`er052_open233_self_recovery_r3dprime_calibration_01.
   SAFETY_CRITICAL_SUB_IDS`)をStage2のみ・n=1で再確認し(`er052_
   open233_element_trial_safety_control_03.py`、¥1.6243)、**8claim全件
   がBLOCKINGを維持し誤降格0件**であることを確認してから昇格した
   (unittest`TestMisconceptionPrincipleRubricV5`3件)。

既存iteration1〜7・rep7〜16の出力(OUT_DIR_ITER1〜7/OUT_DIR_REP7〜16)は
変更しない。実記事での検証(neg1/neg3のn=2再実行)は§9-1㉑参照。

### 4-25. body rubric V6(B3/A2A3-0誤降格是正、許容/NG対比例示、委任_33)

委任_32(広いTrial iteration8、§7-0-iter32)がfull flowで新規検出した
Safety-critical誤降格2件(B3[HF-007]が2/2、A2A3-0[HF-003]が1/2)に対し、
最小修正1回としてbody rubric V6(`RUBRIC_R3_TRIPLE_PRIME_WITH_
MISCONCEPTION_PRINCIPLE_V6`、`er052_open233_self_recovery_stage2_
calibration_01.py`)を追加した。新しい判定基準・原則区分は追加せず、
既存BLOCKING列挙(d)[Ledgerと逆方向/別の因果の断定]・(b)[Ledgerに無い
具体的事実の追加]について、「確認済みFact同士の自然な接続」として
tie-breakでQUALITYへ寛容化されやすい2パターンを対比例示として明示した
(詳細な文面はコード内コメント・§7-0-iter32参照)。

**確認した事項(¥0、新規API呼び出しなし)**: Stage2入力(`verified_ledger_
text`)には、既にLedgerの`conditions`/`notes_for_writer`/`causal_strength`
を含む全文が渡されている(`er050_gpt6_checker_comparison_trial_01.
load_audit_fixture`がaudit jsonのprompt文字列から`{verified_ledger_text}`
マーカー間を機械的に抽出する既存実装、§4-4確定版どおり)。B3/A2A3-0の
誤降格は入力不足ではなく、rubric文言側のtie-break原則がLLM判定を
寛容化側へ誘導していたことが原因であり(§7-0-iter32根本原因節)、
V6はこの1点のみを是正する。

**priming再測定(委任_16の教訓どおり)**: `BODY_RUBRIC_DEFAULT`をV5から
V6へ昇格する前に、以下3系統をn=1(Stage2のみ、`er052_open233_element_
trial_safety_control_04.py`、実測¥2.0061)で確認した。
(A) Safety-critical 8claim: 8/8 BLOCKING維持(誤降格0件、B3/A2A3-0含む)。
(C) Hormuz許容5/NG5: 許容5件は全てQUALITY/ACCEPTABLE(false block 0)、
NG5件は全てBLOCKING(false pass 0)。
(Hook) neg1実Hook(accept-1-original-hook)・境界例(boundary-1-
dramatization)のHook専用Stage2(rubric本体は無変更): 両方ともQUALITY
(非回帰、body V6が独立したHook rubricへ波及していないことを確認)。

**full flow確認(`er052_open233_self_recovery_flow_runner_01_rep18_
representative_01.py`、実測¥4.3972、OUT_DIR_REP18新設)**: `bgroup_B3`
(Stage1 fresh・n=2)・`safety_A2A3`(Stage1 reuse・n=2)・
`meta_run03_standard`(Stage1 fresh・n=2)を再実行した。

1. `bgroup_B3`: **2/2ともBLOCKING維持→RESOLVED_REWRITE**(誤降格は
   再現しなかった)。Rewriteは①水準(`1_word_connective`)のみで、
   実際の差分は`so`→`while`の1語のみ(ユーザー指示D[B3の修正はso→while
   の1語]と一致、§1参照)。
2. `safety_A2A3`: **2/2ともHF-003(A2A3-0)がBLOCKING維持**(誤降格
   再現せず)。ただしRewriteがladder各水準で完了しきらず
   `stage4_reason=ladder_exhausted_without_full_rewrite`でSTAGE4
   (fail-closed、Safety-critical要件[BLOCKING維持]は満たすが、
   Rewrite自体の成功率は別課題として残る)。
3. `meta_run03_standard`: **2/2ともACCEPTABLE_STAGE1**(委任_32 iter8の
   同一instanceは2/2ともSTAGE4だった)。同じ既定構成・同じfixtureで
   Stage1 freshの検出結果が「6→11→9claim検出」から「0claim検出」へ
   劇的に変化しており、§6-14(meta_run03_standardの原因三択確定)で
   詳述するとおり、根本原因はStage1 fresh enumeration(検出網羅性)の
   **非決定性**であることが実測で裏付けられた(本V6はこの原因に対して
   無関係であり、コード修正は行っていない)。

自動検知(`detect_safety_critical_misdowngrades`、§8-4新設)による
Safety-critical誤降格件数: rep18 2 instance×n=2(計4 instance-run)で
**0件**(`safety_critical_misdowngrade_count_distinct`)。

`BODY_RUBRIC_DEFAULT`をV6へ昇格した(`ENABLE_MISCONCEPTION_PRINCIPLE_
DEFAULT=True`は維持、Falseに戻すと重大誤解原則配線前の挙動に戻る)。
既存iteration1〜8・rep7〜17の出力は変更しない。unittest
`TestMisconceptionPrincipleRubricV6`3件・`TestSafetyCriticalMisdowngrade
Detection`8件を追加(§8-4参照)。

### 4-26. 線引きの正式採用に伴うbody rubric V7(委任_55、2026-10-03)

(委任文は「§4-23」と指定したが、§4-23〜§4-25は既に使用済み[Hook専用V4/主体置換ガード/V6]のため、次の空き番号§4-26とした。)

**背景**: ユーザー決定(2026-10-03、2回目)で「重大/軽微/問題なし」の線引きが正式採用(`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)。基準文言は`docs/pm/open233_materiality_criteria_2026-10-03.md` 5節、正解ラベルは§7-0-iter33。本節は、判定役(Stage 2)のrubric修正と、その再較正の結果。

**変更**(旧版は定数として残し、V7はV6へ追記する形。Stage 2のPromptに使う版を`BODY_RUBRIC_DEFAULT`でV6→V7へ切り替え):
1. 条件つき→断定(V4原則文の「一律BLOCKING」を置換): Ledgerが条件つき・可能性・懸念として書く内容を記事が発生したこととして書く場合、(ア)被害・結果にあたる核心の主張まで断定、(イ)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値)の追加、(ウ)`notes_for_writer`が明示的に禁じる断定、のいずれかならBLOCKING。核心の主張に留保が残り帰属が保たれていればQUALITY(例1)。
2. 自然な推論の肯定形: 開示がなかった等の確認済み事実から自然に導かれる利用者の状態・認識・反応の描写は、否定形も肯定形(「AIだと思っていた」「楽しんでいた」)も、新しい具体的事実を加えなければACCEPTABLE。決定論的な降格`DISCLOSURE_GAP_NEGATION_RE`(否定形限定)は**変更しない**。
3. 「迷えばBLOCKING」の置換: 迷う場合は、読者が信じたときに事実関係の重大な誤解につながるかで決める(つながるならBLOCKING、つながらないならQUALITY)。数値・主体・否定・比較・時期の差は対象外で、従来どおり機械的にBLOCKING。
4. 「動機の帰属=QUALITY」(production `MATERIALITY_RUBRIC`)は変更しない(動機の創作は1の(イ)で拾う)。Stage 2 production既定rubricは`MATERIALITY_RUBRIC_V7`(「迷えばBLOCKING」の1行のみ置換、旧版は残す)。
5. 例示3行(例1=QUALITY、例2=ACCEPTABLE、K19=QUALITY)のみ。Hook専用rubric(V3/V4)・`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`は不変。

逐語の差分: `er052_output/open233_safety_control_03/rubric_diff.md`。

**再較正**(`er052_open233_element_trial_safety_control_05.py`[委任文の`_03`は既存ファイルがあるため`_05`で作成]、Stage 2単体、n=2、26 call、¥4.3666、`er052_output/open233_safety_control_03/`):

| 較正セット | 合否基準 | 結果 |
|---|---|---|
| (a) Safety-critical 6claim(B3・B4-a・A2A3-0・A4-0・A4-1・A5-0) | misdowngrade 0 | **誤降格2件(A4-1が2/2 ACCEPTABLE)。不合格**。他5claimは2/2 BLOCKING |

(委任_57追記: A4-1の正解ラベルは「ACCEPTABLE(2026-10-03、正式採用基準の適用。旧: BLOCKING Safety-critical)」へ修正。上の(a)は修正後ラベルでは「Safety-critical 5claim 誤降格0」で合格。下記「委任_57」参照)
| (b) Safety12(er009 9フラグ) | misdowngrade 0 | 0/18(全て2/2 BLOCKING) |
| (c) Hormuz許容5/NG5 | 従来(V6)と同じ | 許容5=false BLOCK 0(V6のQUALITY/ACCEPTABLE→V7は主にACCEPTABLE)、NG5=false PASS 0。合否は10件ともV6と同じ |
| (d) 新しい例3件 | n=2とも期待どおり | 例1 QUALITY 2/2、例2 ACCEPTABLE 2/2、K19 QUALITY 2/2。合格 |
| (e) K16・K20(B4-a型)(A2A3-0・B4-aは(a)で確認) | misdowngrade 0 | 0(2/2 BLOCKING) |
| (f) 負例K11・K12・K13 | false BLOCK 従来より増えない | 0(全て2/2 ACCEPTABLE。K11〜K13のLLM判定は従来もACCEPTABLE/QUALITY[floorでBLOCKING化した実行はあるが機械floorは不変]) |

**不合格の原因切り分け(診断。rubricの修正ではない、修正は行わずFable判断)**: A4-1の対象文は`people who thought they were speaking with AI were actually speaking with human staff`と`That was what people thought as they spoke.`(MUSE-HC-012)。V6(委任_33、sc04 n=1)ではBLOCKINGだった。A4グループ(A4-0/A4-1/A4-2)のStage 2のみを、V7の変種でn=1ずつ実行した(`ablation_a41/`、7 call、¥2.1157)。

| 変種 | A4-1 |
|---|---|
| V7全体(本実測、n=2) | ACCEPTABLE 2/2 |
| V7から(2)自然な推論の段落を除く | ACCEPTABLE |
| V7から(2)内の「内心を断定する記述のBLOCKING条件は適用しない」の一文を除く | ACCEPTABLE |
| V7から判定済みの例3行を除く | ACCEPTABLE |
| V7から(3)判断に迷う場合の段落を除く | ACCEPTABLE |
| V6+3区分の定義のみ | BLOCKING |
| V6+(2)の段落のみ | ACCEPTABLE |
| V6+(3)の段落のみ | BLOCKING |

読み取り(n=1、非決定性があるため示唆に留まる): (2)の段落が単独でA4-1をACCEPTABLEへ寄せ、(2)を除いても判定済みの例2行が同じ向きに効くため、(2)と例2は互いに冗長で、どちらか一方の除去では解消しない。(3)・3区分の定義・(1)は単独では寄せない。判断材料: A4-1の対象文は、ユーザー決定の例2(肯定形「AIだと思っていた」の描写=問題なし)・再分類docのK23(「That was what people thought as they spoke.」=問題なし)と同じ型であり、V7が例2どおりに判定した結果とも読める。すなわち、A4-1をSafety-critical(BLOCKING)とする旧ラベル自体が新しい線引きと食い違っている可能性がある(ただし対象文の後半「were actually speaking with human staff」は事実の主張を含む)。選択肢(Fable/ユーザー判断、本委任は実装していない): (イ)A4-1のラベルを新しい線引きに合わせて再判定、(ロ)V7の(2)の範囲を狭める(肯定形の許容を、事実の主張を含まない描写に限る等)、(ハ)A4-1の記事側の文を機械的に守る別の仕組み。いずれもPriming(rubric文の追加が別claimの判定へ波及する現象、委任_16)に注意して再較正が必要。

**未解決・注意**: K19はユーザー決定でQUALITYだが、`changed_comparison`のfloor不変により、Checkerがcomparisonを立てた実行ではBLOCKINGになる(§7-0-iter33)。

**委任_57: A4-1の再ラベル(2026-10-03、Fable判断=ユーザー正式採用の線引きの適用。選択肢(イ))**: A4-1の正解ラベルは**ACCEPTABLE(2026-10-03、正式採用基準の適用。旧: BLOCKING Safety-critical)**。理由: 対象文はユーザー判断済みの例2(利用者がAIだと思っていた、気づかなかった、という推論)と同型で、「were actually speaking with human staff」の事実部分はLedger(人間の契約スタッフが一部の電話を担当)に支持される。rubric V7は変更しない。`SAFETY_CRITICAL_SUB_IDS`は6件→5件(A2A3-0・A4-0・A5-0・B3・B4-a)、runnerの`SAFETY_CRITICAL_CLAIM_DEFS`では`expected:"ACCEPTABLE"`の監視用として残す(Meta-1/Meta-2と同じ扱い)。再較正は再実行せず、結果ファイルは改変せず、注記を`er052_output/open233_safety_control_03/relabel_note_a41.md`へ別ファイルで追加。**再較正の最終判定: 合格(ラベル修正後)**: (a)Safety-critical 5claim 誤降格0、(b)Safety12 0/18、(c)Hormuz V6と同じ、(d)例3件期待どおり、(e)K16・K20 BLOCKING、(f)false BLOCK 0。

残るSafety-critical 5件を正式採用基準の3定義に当てた確認(変更は例2と同型がもう1件あった場合のみ。該当なし):

| sub_id | 対象文(要旨) | 3定義への当てはめ | 結論 |
|---|---|---|---|
| B3(HF-007) | 「Concerns about US-Iran attacks... continued on July 14, so the flashy 20% plan left the stage」(継続する懸念→計画撤回の因果接続) | 重大(4)因果の創作。Ledgerが示していない因果。例2のような「自然な推論」ではなく新しい因果の具体的事実 | 重大のまま |
| B4-a(MUSE-HC-002) | 「A person can take over when AI alone has trouble.」(AI失敗時の人間引き継ぎ機構) | 重大(4)(6)未確認の仕組み・設計意図の新規主張。Ledgerに無い具体的事実の追加(K20〜K22と同型) | 重大のまま |
| A2A3-0(HF-003) | 「those carrying the cargo would repay the money...」 | 重大(2)主体の取り違え。Ledgerは支払義務者を未提示としているのに記事が具体的主体を追加 | 重大のまま |
| A4-0(MUSE-HC-006) | 「trained human contract workers made some calls and completed the exchanges with users」 | 重大(2)やり取りの相手(カウンターパート)の取り違え。Ledgerが示すのは電話の相手先(企業・店舗等)で、利用者ではない | 重大のまま |
| A5-0(MUSE-HC-012) | 「They also temporarily put back the feature in which humans handled the calls」 | 重大(4)時期・経過の創作(継続していた出来事を一度消えて戻った出来事にする)。例2のような利用者の認識の推論ではなく、出来事そのものの追加 | 重大のまま |

例2と同型(利用者の認識の推論+事実部分はLedger支持)のものは、この5件には無かった(A4-1のみ)。確認は対象文の要旨とLedger要旨(既存の設計書・較正コードの記載)に基づく机上確認で、LLM呼び出しはしていない。

## 5. Stage 3 Automatic Rewrite設計

### 5-0. 既存機構棚卸しの統合(委任_05/_06、三分類表)

**参照**: `docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`
(委任_05、read-only調査、¥0)。既存Rewrite関連機構18件を、KPI
(Safety/Escalation/Cap)とQCD(cost/latency/実装リスク)の両観点で
「(A)そのまま再利用」「(B)拡張・改善して利用」「(C)今回KPIには
不適→新方式」の三分類へ整理する(ユーザー指示: 既存資産の無視も
既存方式への束縛も避け、QCD上より良い方法があればTrialする)。

| # | 機構 | 分類 | 理由(KPI/QCD) |
|---|---|---|---|
| 1 | EN Ledger Deviation Checker本体(`vfl01.run_deviation_check`) | (A)そのまま再利用 | Safety資産(Prompt/schema)を保存する設計原則そのもの。Stage 1/Recheckが直接呼ぶ。変更するとSafety regressionリスクが即座に生じる |
| 2 | EN 文単位Local Rewrite primitive(`er010`) | (B)拡張して利用 | 文特定・3段階escalation・差分QA・target-sentence-matchingは実装済み・実データ検証済みでQCD上安価(新規実装よりcost/リスクが低い)。rewrite_kind対応等の薄い拡張のみで足りる(§5-2 E-1) |
| 3 | EN Local Rewrite cycle制御(N3-01直接生成) | (C)新方式 | cycle上限(3回)・呼び出し規約がFamily B系専用の前提であり、Self-Recovery Flowのcycle上限(2、Stage2経由必須)と両立しない。流用すると上限混在のSafetyリスクを生む |
| 4 | EN Local Rewrite cycle制御(Family B generic writer) | (C)新方式 | 同上(#3と同一理由) |
| 5 | Family X EN 全文must-fix retry(Standard) | (A)そのまま再利用 | 既にProduction稼働中。局所Rewrite cycle上限到達時のフォールバックとして位置づけを変えず流用(§5-3) |
| 6 | Family X EN 全文must-fix retry(Advanced) | (A)そのまま再利用 | 同上 |
| 7 | Family X/E オーケストレーション(`_must_fix_from_deviations`ほか) | (B)拡張して利用 | 既存の呼び出し規約を保った上で、origin別Stage3分岐・cycle上限管理を追加する必要がある箇所 |
| 8 | JA Original/R2 must-fix全文(段単位)retry | (A)そのまま再利用 | 既にProduction稼働中。paired local rewrite(J-1/J-2)のguard抵触時フォールバックとして流用(§5-4) |
| 9 | JA→EN不整合時の「案B」(JA全文差し戻し) | (B)拡張して利用 | 発火条件を「Stage 2 BLOCKING確定後」へ限定し直す(既存は無条件発火)以外はProduction codeをそのまま使う |
| 10 | Family X構造Gate(`split_family_x_article_text_v2`) | (A)そのまま再利用 | 局所Rewrite後の構造検証guardとしてそのまま再実行するだけで足りる(§5-2/§5-4) |
| 11 | TTS発音NGspan Local Rewrite(`er020`) | (C)新方式(別ドメイン) | 発音・ASR比較が目的でFact逸脱とは無関係。ただしfail-closed設計思想(原文復帰・Human Review Lock)は§5-5で継承する |
| 12 | TTS Local Rewrite原型(cooldown) | (C)新方式(別ドメイン) | 同上(#11の移設元、参照のみ) |
| 13 | TTS 7-Gate自然英語QA原型 | (C)新方式(別ドメイン) | 同上 |
| 14 | Full Story専用TTS Local Rewrite回復 | (C)新方式(別ドメイン) | 同上(#11の呼び出し元の1つ) |
| 15 | Local Rewrite差分QA(`run_diff_qa_for_accepted_rewrite`) | (A)そのまま再利用 | 受理直後の¥0近い追加安全確認として既に確立済み(§5-5) |
| 16 | Local Rewrite原型ルール策定Trial(歴史、er009系) | 対象外 | 既に#2へ統合済みの過去Trialであり、再利用対象ではない(参考記録のみ) |
| 17 | Local Rewrite再利用のEvidence確認Script | 対象外 | #2の検証記録であり機構そのものではない |
| 18 | En ASR意味的同等性チェッカー | (C)新方式(別軸) | TTS後の発音検証でありLocal Rewriteの入力にならない |

**二重実装リスクへの対処**: 棚卸し§4で指摘された「Family Xに新規
Local Rewriteモジュールをゼロ設計するとer010と機能重複する」リスクは、
上表(B)分類(#2/#9)を「拡張」として位置づけることで解消する(新規
モジュール名を先に確定せず、既存資産への薄い拡張として実装する)。
優先順位(局所Rewrite第一→cycle上限到達時のみ既存の段単位/全文
must-fix retryへフォールバック→それでも解消しなければNG_REVIEW_
REQUIRED)は§5-3で維持する。

### 5-1. 段階別方針

**JA側(origin=ja_source)**: 既存案B(`er012_e_family_entertainment_
two_level_runner_01.py::run_writer_stage()`のJARecheckRequiredError
捕捉→`jaw.run_ja_writer_o_r1_r2()`をmust_fix付きで実行→Original→
R1→R2→JA Fact Checkの全体を再生成)を**Phase 1のJA側Rewrite実装として
そのまま再利用**する(コード変更なし、既にProduction code)。この経路
はStage 2のBLOCKING確定を経てから発火する点が既存案Bとの違い(既存は
Stage 2を経由せず、ja_source MAJORが検出された瞬間に無条件で発火)。

**局所Rewrite候補 → [委任_04改訂/A4] Phase 1の第一級実装項目へ繰り上げ**:
現行案Bは「Original段の該当claimに関する箇所だけ」をmust_fixで指定
しつつも、Original→R1→R2の全段を再生成するため、**該当claimと無関係な
箇所まで変わり得る**(Hormuz run_03で、Advanced側は案Bで解消したのに、
Standard側で全く別のclaim[HF-009関連]が新規にja_source MAJORとして
検出された事例は、この「全文再生成が新しい逸脱を生む」リスクの実例)。
実測ではBLOCK事象5件中4件(80%)が`origin=ja_source`であり(Opus所見
論点1(A))、JA全文再生成(¥3.5〜4.0)がJA側の唯一の回復手段である限り
Cap内でEscalationゼロは達成できないと判断した。そこで、より局所的な
**paired local rewrite**(該当JA 1文±1文とそれに対応するEN文を同一の
`rewrite_hint`で局所編集する案)を**Phase 1で新規実装・検証する第一級
項目**へ格上げする(旧: Phase 1スコープ外→Phase 2改善候補)。詳細設計は
新設§5-4。JA Original段のうち該当paragraphのみをmust_fixで再生成し
他paragraphはR1/R2をスキップする案(旧提案)は、JA Writer Oの既存構造
(Original→R1→R2は文体洗練の連鎖であり、paragraph単位の部分スキップは
現行実装に存在しない)を変更する必要があるため引き続き不採用とし、
**§5-4のpaired local rewrite(R2本文を直接局所編集し、Original→R1→R2の
連鎖には触らない)を代替案として採用する**(この障壁を回避できる、
Opus論点1推奨1)。§5-4のguard抵触時は、本節末尾(案B)を**フォール
バック**(記事あたり1回)として位置づけ直す。

**EN側(origin=translation、Advanced/Standard内で新規に生じた逸脱)**:
現行Productionの「must-fix retry 1回」(`adv_gen.generate_family_x_
faithful_translation(..., must_fix=...)` / `std_gen.generate_family_
x_standard_a2_no_heading(..., must_fix=...)`)は**全文再生成**であり、
局所編集ではない。Self-Recovery Flowでは、これを**Phase 1のbaseline**
として維持しつつ(実装コストゼロ、既にProduction code)、**局所Rewrite
を優先候補として設計する**(以下)。

### 5-2. 局所Rewrite(EN側、設計提案。Phase 1 Trialで新規実装・検証対象)

**[委任_06新設]** 本節はEN局所Rewriteの**既存ベース改善案(E-1)**を
記述する(以下本文はE-1そのもの、委任_04時点の記述を維持)。これとは
別に、**新方式案(E-2)**を§5-2-補で提示し、Phase 1 ⑤で同一fixtureに
対しE-1/E-2を実行し実測比較する(§5-0の棚卸し結論=#2「拡張して利用」
に対応する具体案がE-1、二重実装を避けつつQCD上より良い可能性を検証
する対照案がE-2)。

**[委任_04改訂/A4]** 本節のEN局所Rewriteは**`origin=translation`の
claimにのみ適用する**。`origin=ja_source`のclaimには適用しない(EN側
だけを書き換えるとJA本文とEN本文が意味的に乖離し、誰も検査しない
JA/EN不整合を生む、Opus論点1(A)・論点4【Safetyリスク】)。Rewrite
mechanismの選択は**cycle indexではなくclaimの`origin`で決める**(§5-3
改訂)。`origin=ja_source`の場合は§5-4のpaired local rewriteまたは
本節末尾(旧案B、フォールバック)を使う。

- **入力**: 記事全文のうち、Stage 2の`rewrite_hint`が指す該当claimを
  含む文±1文のみを抽出し、そのローカルcontext・**[委任_04改訂/A11]
  Ledger全文**(該当箇所だけではない。B3型のように別条件が離れた箇所に
  あるケースを見逃さないため、fail-closed優先でStage 2と同じ入力方針に
  揃える、Opus論点4推奨3)・`rewrite_hint`・`rewrite_kind`(§4-5)を
  渡して**その部分だけ**の書き換え文を生成させる。記事の他の部分は
  一切渡さず、生成後にプログラム側で文字列置換する(LLMに全文を
  書き直させない)。`rewrite_kind=="delete"`はまずLLMを経由せず該当
  文字列の決定論的削除を試みる(§4-5追記)。
- **利点**: 全文再生成による「無関係箇所での新規逸脱」を構造的に
  防げる可能性がある。**[委任_04改訂/A4]** ただしOpus論点4(B)の指摘
  どおり、Hormuz run_03の新規MAJORは「全文再生成が新逸脱を生んだ」
  例ではなく「JA上流の総取り替えが下流を全変化させた」例であり、局所
  Rewriteの真の利点は**新逸脱抑制ではなくコスト削減とJA/EN整合維持**
  と位置づけ直す。
- **guard(構造破壊防止)**: 置換後、既存`sc.split_family_x_article_
  text_v2()`のNG条件(`TOO_FEW_PARAGRAPHS`/`NG_MISSING_TITLE`/
  `NG_MISSING_IN_ONE_LINE`/`NG_HEADING_IN_BODY`)をそのままguardとして
  再利用する。**[委任_04改訂/A11]** 置換後にNGが出た場合の扱いを次の
  段階的フォールバックへ変更する(Opus論点4推奨4、旧「cycle消費+
  Stage4直行」は過剰に厳しいため): (1) 置換を破棄し元の全文へ戻す
  (¥0)、(2) 同一cycle内でrewrite再生成を1回だけ再試行、(3) それでも
  NGなら既存全文must-fix retry(既存Production機構)へフォールバック、
  (4) それも失敗した場合のみcycleを1消費してStage 4へ進む(段落数retry
  [既存の別axis、1回]は温存し、軸を混在させない)。
- **rewrite後の機械検証(§4-5追記、Opus論点5推奨3)**: `rewrite_kind==
  "delete"`は当該文字列の消滅を、`"replace_with_ledger_value"`は
  Ledger値の出現を、Recheck前にプログラム側で機械確認する。
- **Recheckの範囲**: **全文Checker(fail-closed推奨)**。局所編集の
  範囲だけを再チェックする案(コスト減)も検討したが、Stage 1 Prompt
  は記事全文とLedger全文を突き合わせる設計であり、局所的な再チェック
  用の別Promptを新設すると「新しいPromptがSafety regressionを生む」
  リスクをStage 2に続いて二重に抱えることになるため、**Phase 1では
  採用しない**(全文Checkerを毎回フルで再実行する。コスト増だが
  Safety最優先)。

### 5-2-補. EN局所Rewrite 新方式案(E-2、[委任_06新設]、Phase 1 ⑤で
E-1と比較実測対象)

E-1(§5-2、er010拡張)は3種の`rewrite_kind`すべてを同一のLLM局所
Rewrite callで扱う設計だが、E-2は`rewrite_kind`ごとに手段を分離し、
「LLMを使う範囲を最小化する」方向でE-1と対照的な設計にする。

- **`delete`型**: LLMを一切経由しない。Stage 2の`rewrite_hint`が指す
  対象文をプログラム側で直接削除する(該当文をピリオド区切りで特定し、
  `article_text.replace(target_sentence, "", 1)`相当。E-1もdelete型は
  既にLLM非経由だが[§4-5]、E-2は「削除後に前後の接続詞・代名詞の
  不整合[例: 削除した文を受ける"This"が次文に残る]をチェックする」
  軽量な決定論的後処理[代名詞・接続詞で始まる次文を検出したら該当文も
  併せて再確認対象にするフラグ立てのみ、書き換えはしない]を追加する
  点がE-1との差)。
- **`replace_with_ledger_value`/`narrow_scope`型**: E-1(§5-2)と同じ
  「文±1文+Ledger全文+rewrite_hint」の入力方針は共有するが、**Prompt
  自体を最小化**する(E-1はer010の3段階escalation[attempt1→2→3で
  情報を段階的に追加]をそのまま流用するため、1回で解決しない場合に
  平均call数が増える設計。E-2は"issue+rewrite_hint+rewrite_kind+
  Ledger該当箇所"を1回のPromptで全て提示し、escalationという段階構造
  自体を持たない[1回で解決しなければ即座に既存全文must-fix retryへ
  フォールバック、cycle消費は据え置き])。
- **狙い**: (a) delete型の後処理追加でE-1が拾わない「削除後の文脈破綻」
  を安価に補強できるか、(b) escalationを持たないシンプルなPromptで
  E-1と同等の解決率を、より少ないcall数(=より低いlatency/cost)で
  達成できるか、の2点をPhase 1 ⑤で実測する。
- **リスク**: 段階的escalationを持たないため、1回で解決しない場合の
  救済手段がE-1より弱い(即フォールバックのみ)。Safety面はE-1と同じ
  guard(構造Gate再確認・機械検証・全文Recheck)をすべて共有するため、
  Safety規性には差が生じない設計とする(差が出るのは解決率とcostのみ)。
- **採否**: Phase 1 ⑤の実測(型別成功率・実単価・guard抵触率・
  フォールバック発生率)をもってE-1/E-2のどちらを本採用候補とするか
  確定する(本節時点では両論併記、決定しない)。

### 5-3. loop上限・順序

- 記事あたり最大2 cycle(§3-5)。**[委任_04改訂/A4]** Rewrite
  mechanismは**cycle indexではなく、対象claimの`origin`で選ぶ**:
  `origin=ja_source`→§5-4のpaired local rewrite(guard抵触時のみ
  旧案Bへフォールバック)、`origin=translation`→§5-2のEN局所Rewrite。
  同一記事で**旧案B(JA全文Rewrite)を2回使わない**という既存のコスト
  guardは維持する(1 cycle目でフォールバックとして旧案Bを使った場合、
  2 cycle目でja_source claimが新規発生してもpaired local rewriteを
  優先し、それも失敗した場合のみ§10リスク9のworst caseガードに従い
  Stage 4へ進める)。
- **[委任_04改訂/A5]** cycle 2の発火条件に「cycle 1でBLOCKING確定した
  claim/fact_idとは異なるclaim/fact_idであること」を追加する(§3-3
  STOP条件参照)。同一claim/fact_idの再BLOCKINGはRewriteが効かなかった
  ことの実証であり、cycle残数があっても即Stage 4へ進める(無駄な追加
  投資をしない、Opus論点7推奨1)。
- Rewriteは常にStage 2でBLOCKING確定した後にのみ実行する(Stage 2を
  経ずに即Rewriteしない。これにより「本当にmaterialか」を必ず一度
  問い直してから書き換えるため、無駄なRewrite回数を削減する)。

### 5-4. paired local rewrite(JA側、[委任_04新設/A4]、Phase 1で新規
実装・検証対象)

**[委任_06新設]** 本節は既存に文単位JA Local Rewrite機構が無いことを
前提に、er010の骨格(文特定+3段階escalation+差分QA+cycle制御)を
日本語向けに薄く移植する**新設案(J-1)**を記述する(以下本文はJ-1
そのもの、委任_04時点の記述を維持、§5-0棚卸し結論#9に対応)。これとは
別に、新規モジュールを増やさない**代替案(J-2)**を§5-4-補で提示し、
Phase 1 ⑤でJ-1/J-2を同一fixtureに対し実行し実測比較する。

**位置づけ**: `origin=ja_source`のclaimに対する第一候補のRewrite手段
(§5-3)。既存案B(JA全文差し戻し、¥3.5〜4.0)は「guard抵触時の
フォールバック(記事あたり1回)」に格下げする。目的は(1) コスト削減
(概算¥1.0〜1.5/cycle、案Bの1/3以下)、(2) JA/EN乖離の防止(EN局所
Rewriteをja_source claimに使わないことの代替手段を提供する)。

**入力**:
- 該当claimに対応するJA本文(R2段)の該当1文±1文。
- 対応するEN文(Advanced/Standardのうち発火元)±1文。
- Ledger全文(該当箇所だけでなく全文、fail-closed優先。他のRewrite
  経路[§4-4/§5-2]と同じ方針)。
- Stage 2の`rewrite_hint`/`rewrite_kind`(§4-5)。

**編集方式**: JA Writer Oの既存構造(Original→R1→R2は文体洗練の連鎖)
には触らず、**R2確定後の本文を直接局所編集する**(部分スキップという
新しい制御構造を導入しない。§5-1で述べた旧提案の障壁を回避)。同一の
`rewrite_hint`でJA文とEN文を同時に編集し、両者の整合を維持する。

**Fact Check/Deviation Check**:
- JA側: 編集後のJA全文に対し`vfl01.run_deviation_check`相当を**1
  call**実行し、Ledgerとの整合を確認する(局所編集のみを見るのではなく
  全文、fail-closed優先)。
- EN側: 編集後のEN全文に対し既存Deviation Check(Stage 1 Recheck)を
  **1 call**実行する(§3-0の全体Recheckに統合、追加callではない)。

**guard(構造破壊防止、既存Gateの再利用)**:
- 文体Gate: JA Writer Oの既存文体検証(Original/R1/R2各段のvalidator)
  を局所編集後の全文に対して再実行する。
- 記号Gate: 既存`JAFactCheckStopError(stage="original_symbol"/
  "r2_symbol")`相当の音声化禁止記号チェックを再実行する。
- 段落数Gate: 既存`sc.split_family_x_article_text_v2()`のNG条件を
  EN側の局所編集結果に対して再実行する(§5-2と同一)。

**Recheck**: 全文Checker(Stage 1 Recheck、§3-0)で判定する。JA側は
上記JA Deviation Check 1 callの結果、EN側はStage 1 Recheckの結果を
両方確認する。

**上限**: 記事あたりcycle上限(最大2)の範囲内。paired local rewriteの
guard抵触(文体/記号/段落数いずれか)時は、§5-2と同じ段階的フォール
バック(置換破棄→同一cycle内1回再試行→旧案B[JA全文差し戻し]へ
フォールバック→それも失敗でStage 4)を適用する。旧案Bは記事あたり
最大1回(既存の「1回上限」思想を維持)。

**実装リスク(未検証、Phase 1で新規実装)**:
- JA本文の局所編集関数自体が新規実装であり、既存のJA Writer O
  paragraph構造との整合(文脈保持・助詞接続等)は前Phase・本Phase
  いずれの実測にも存在しない。
- 文体Gate/記号Gate/段落数Gateを局所編集後の**全文**に対して正しく
  再検証できるかは未検証(既存Gateは全文生成後の検証を前提に実装
  されているため、局所編集後の全文に対してそのまま適用できるかの
  確認が必要)。
- JA/EN双方を同一`rewrite_hint`で編集する際、両言語間で編集内容が
  意味的に一致することを機械検証する手段が現時点で無い(Recheckが
  Ledgerとの整合は見るが、JA↔EN整合そのものは見ない、Opus論点1(A)の
  指摘の裏返し)。Phase 1では人手併用ではなくRecheck結果とdiffログの
  記録による事後観測に留める(Guardrail内の暫定対応、完全な解決策では
  ないことを明記)。

**Phase 1測定項目**: 型別(delete/replace_with_ledger_value/
narrow_scope)成功率・実単価・guard抵触率・フォールバック発生率
(§9-1⑤)。

**[委任_10実装・実測] J-1汎用対象文特定の改善**: 委任_09統合dry-run
で対象文特定失敗率63.6%(7/11)が最大の失敗要因と判明したため、以下
3段階の統合ロケータ(`locate_target`/`locate_ja_counterpart_by_
position`)を実装した。(1) 第一キー: Stage2出力`rewrite_hint`の逐語
引用断片(`extract_quoted_fragment`)をEN/JA双方でexact substring
照合。(2) 第二キー: 既存`locate_best_sentence`(claim_textでの
exact/SequenceMatcher、ambiguous時[最有力候補と次点候補の差が僅少]は
単一文を確定させず全文フォールバックへ委ねるよう変更)。(3) 第三キー:
`er010_ledger_local_rewrite_09.locate_target_sentence`(英語word-
overlap、read-only借用)。JA側はさらに、EN対象文の`en_full`内での
文位置比を`split_ja_sentences`によるJA文分割へ写像し(対訳記事がほぼ
同順序で対応するという構造的近似)、写像window内で数値トークン一致を
優先する`locate_ja_counterpart_by_position`を第四キーとして追加した。
29 instance再実行(§9-1⑦)の結果、J-1機構の対象文特定成功率は
9/11(81.8%、うち`j1_paired_rewrite`到達後の解消率7/9=77.8%)まで改善し
(委任_09実測27.3%→大幅改善)、hormuz_run03_standard(委任_09で
`j1_pair_not_located`によりSTAGE4到達)は`RESOLVED_REWRITE_THEN_
DOWNGRADE`まで到達した。固有名詞は言語間で一致しないため位置比+数値
トークン一致は主に日付・割合・件数を伴うclaimでのみ有効という限界は
残る(既知の限界として維持)。

### 5-4-補. JA局所Rewrite 代替案(J-2、[委任_06新設]、Phase 1 ⑤で
J-1と比較実測対象)

J-1(§5-4)は新規モジュール(日本語文分割+対象文特定)を実装するが、
J-2は**新規モジュールを一切増やさず**、既存の「JA must-fix(全文、
`original_must_fix`引数)」に「対象文のみ修正・他は一字も変えない」という
局所指示を追加するだけで代替できないかを検証する。

- **入力**: 既存のJA Original段`build_must_fix_block`が受け取る
  `must_fix`引数へ、Stage 2の`rewrite_hint`(対象claim・修正方針)に加え
  「この指摘に対応する一文だけを修正し、他の文は一字も変更しないこと」
  という制約文を追加する。Original→R1→R2の既存カスケードはそのまま
  実行する(J-1と異なり部分スキップという新しい制御構造を導入しない、
  既存Gateの通過実績をそのまま使える)。
- **利点**: (a) 新規モジュール(文分割・対象文特定・差分QA)を実装
  しないため実装リスク・検証コストがJ-1よりはるかに小さい、
  (b) 既存の文体Gate/記号Gate/段落数Gateを無改造でそのまま通過できる
  ことが保証されている(J-1は局所編集後の全文に対してこれらGateが
  正しく再検証できるか自体が未検証、§5-4実装リスク参照)。
- **欠点**: 出力が全文(Original→R1→R2の再カスケード)であるため、
  cost自体は旧案B(全文差し戻し)に近い(J-1が狙う¥1.0〜1.5/cycleの
  コスト削減効果は得られない)。「対象文以外は変えない」という指示が
  LLMに厳密に遵守される保証はなく、Fact Check/再英訳の再抽選(Advanced/
  Standardの再生成)は避けられない点もJ-1(該当stageのみの局所編集)に
  劣る。
- **狙い**: Phase 1 ⑤で、J-1の実装コスト・guard抵触率と、J-2の
  cost・「本当に対象文以外が変わらないか」の実測diff率を比較し、
  QCD上どちらが本Phaseの規模(Family X限定Trial)に見合うかを判断する
  材料にする。
- **採否**: 本節時点では両論併記、決定しない(Phase 1 ⑤実測後に確定)。

### 5-4-補2. Phase 1 ⑤実測: rewrite_kind別成功率(委任_08、E-1/E-2/J-1/J-2)

**スコープ確定(委任_08時点の判断)**: §5-2の「EN局所RewriteはOrigin=
translationのclaimにのみ適用」・§5-1の「origin=ja_sourceはJA側
Rewriteを使う」という既存の経路選択ルールに従い、型ごとの担当経路を
次のとおり確定した(delete型3claimはいずれもorigin=ja_source相当の
ため決定論的削除の成否のみを共通baselineとして測定し、E-1/E-2の
機構差はreplace_with_ledger_value型で、J-1/J-2の機構差はnarrow_scope
型で検証する、これが実際に手法が分岐する型であるため)。

**(a) delete型baseline(B1-c[JA]/B3[EN]/B4-a[EN]、決定論的削除、
Recheck 1call/claim、計3call・¥1.0778)**: `locate_target_sentence`
(er010既存、fallback overlap方式)で対象文を特定し文字列削除、
Recheckで確認。**B3(単一deviation記事)は削除のみでLEDGER_COMPLIANT
達成(resolved=True)**。**B1-c/B4-a(いずれも同一記事内に他の
BLOCKING claimが複数存在する記事[B1=2claim、B4=4claim])は記事全体
Recheckが引き続きLEDGER_DEVIATIONを返した(resolved=False)**が、
これは対象claim以外の**未処理の別claimが記事に残っているための
記事レベルの結果**であり、削除自体が対象claimの問題を解消したかは
本実測の粒度(記事全体Recheckのみ)では独立に確認できていない
(claim単位の再出現有無を見るには、Recheckのdeviations配列を
claim単位で照合する追加実装が必要、次回実測項目の候補として記録)。
E-2の追加後処理(削除箇所付近の代名詞・接続詞検出、¥0)は全3件で
実行し、B1-c(「これ」「その」「この」)・B3(that/it/so)・B4-a
(this/that/it/so)いずれも記事全体では該当語が検出された(削除箇所
直後の文に限定した厳密な照合ではなく記事全体走査のため、削除と無関係な
箇所の一致を含む可能性が高く、Trial観測値としての精度は限定的)。

**(b) replace_with_ledger_value型(er009_changed_actor/changed_number、
origin=translation相当、E-1 vs E-2、計4claim実行[各claim×2手法]・
8call・¥0.4913)**: **両claim・両手法とも1 attempt目でresolved=True・
machine_verified=True(4/4=100%)**。E-1(er010.rewrite_ng_item、
既存3段階escalation骨格そのまま呼び出し)はchanged_actorで実在の
研究者名(Kareem Haggag and Giovanni Paci、Ledgerのsource行から)を
補って書き換え、E-2(最小1-shot Prompt)は`Researchers`という中立語へ
置換した。両手法ともescalationは発火せず(1 attemptで解決)、
**cost差は僅少**(changed_actor: E-1 ¥0.1828 vs E-2 ¥0.1735、
changed_number: E-1 ¥0.0949 vs E-2 ¥0.0906)。本実測範囲(n=2claim)
では**E-1の3段階escalation機構は発火せず、E-2の単純1-shotで同等の
解決率・同等コストを達成**した(escalationの真価はより解決困難な
claimでのみ発揮される可能性があり、本実測では判別できない)。

**(c) narrow_scope型(hormuz_run03_standard HF-009、origin=ja_source、
J-1 vs J-2、計7call・¥1.4167)**: **J-1(paired local rewrite、JA文
±1+EN文±1を1callで同時編集→JA Fact Check[V4A variant代用]1call+
EN Recheck[同]1call)がJA Check・EN Recheckとも`LEDGER_COMPLIANT`を
達成し、hormuz narrow_scope claimを完全に解消した(resolved=True、
対象文以外のJA文への影響=0を機械diffで確認、cost=¥0.4569・3call)**。
**J-2(既存方式に近い代替、JA全文を「対象文以外は一字も変えない」
指示付きで全文regen→対象文相当箇所を再翻訳→EN Recheck)は、JA Check
は`LEDGER_COMPLIANT`だったが、EN Recheckが`LEDGER_DEVIATION`のまま
残り、resolved=False(cost=¥0.9598・4call、J-1の約2.1倍)**。加えて
機械diff(非対象文の集合比較)で**非対象文1件の変化を検出**
(n_orig=20→n_upd=21、symmetric diff=1)。J-2は「対象文以外は一字も
変えない」と明示指示したにもかかわらず、全文regenという性質上、
軽微な drift が実際に発生することを実測で確認した。

**結論(採用案)**: **narrow_scope型はJ-1を採用候補とする**(cost・
解決率・JA/EN整合[drift 0件]のいずれでもJ-2を上回った)。
**replace_with_ledger_value型はE-1/E-2いずれも同等の性能(本実測範囲
では差が付かず)であり、実装コスト・保守性(E-2は3段階escalation
骨格を持たずコードがより単純)を考慮するとE-2を第一候補とし、E-1を
「E-2で1 attempt目に解決しない場合のfallback」として位置づける
両論併記を維持する**(n=2という小標本のため、より解決困難なclaimでの
追加実測[Phase 2候補]でE-1のescalationが真に必要になるケースが
無いかを確認してから最終確定する)。

**[重要、委任_08の主要な問いへの回答]hormuz narrow_scopeの解消可否**:
**J-1により解消可能であることを実測で確認した**(§13-10課題2で
「Cap超過リスク」として記録されていたhormuz型の解決手段が、Phase 1⑤
実測で実証された)。「どちらの手法でも解消できない」という最大リスク
シナリオは本実測では回避された。

**実装スコープ上の限界(次回実装時の課題として明記)**:
- 本実測のJ-1/J-2の「JA Fact Check」「EN Deviation Check(Recheck)」は、
  真のProduction JA Fact Check(`er002_ja_web_research_r3`系、
  web_search併用)・真のJA Writer O cascade
  (`er019_family_x_ja_writer_o_r1_r2_01.py`、Original→R1→R2)は
  一切呼び出さず、既存V4A variant checker(`er051_open233_checker_
  trial_variant_01.run_trial_deviation_check`)をJA/EN両方の文面に
  適用する近似で代用した(読み取り専用の遵守・予算/実装時間制約に
  よる意図的なスコープ縮小、Production非接続であることは維持)。
  §5-4が要求する「句点分割移植」相当の汎用JA文分割モジュールも、
  本Trialでは対象文を直接指定する簡易実装に留めた(delete型B1-cの
  `locate_target_sentence`[英語文末記号ベースの正規表現]がJA全文を
  1文として誤認識する不具合を実地で確認、§5-4の課題認識が実測で
  裏付けられた)。真のJ-1/J-2実装(Production配線候補とする場合)は、
  上記2点([1]真のJA Fact Check/JA Writer O連携、[2]汎用JA文分割
  モジュール)を別途実装する必要がある。
- delete型のclaim単位再出現確認(記事全体Recheckではなく、対象claimの
  issueが個別に再検出されるかを見る)は本実測で未実装(次回実測項目)。

詳細ログ: `er052_output/open233_self_recovery_stage3_rewrite_trial_01/
summary_stage3_rewrite_trial.json`。

### 5-5. 継承するguard/retry/再検証(棚卸し§3の統合、[委任_06新設])

E-1/E-2・J-1/J-2いずれの案を採用する場合でも、以下は既存資産からの
継承として維持する(独自の新しい安全装置を発明しない、
`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`§3準拠)。

1. **対象はMAJORのみ**。MINORは記録のみで対象外(er010既存方針)。
2. **文単位retry上限3回+記事全体cycle上限の二軸独立カウンタ**
   (E-1/J-1のattempt escalationに適用。ただしSelf-Recovery Flow全体の
   記事cycle上限は§3-5の2回を優先し、er010固有の`MAX_REWRITE_CYCLES=3`
   はE-1/J-1内部のattempt軸としてのみ使う。二重の上限概念を混同しない)。
3. **受理直後の差分QA**(`run_diff_qa_for_accepted_rewrite`/
   `apply_diff_qa_to_resolved_rewrite`、Fact Checker A' web_search +
   Ledger再確認)を、E-1のRewrite受理後に適用する(J-1/J-2は同型のJA版
   差分QAが無いため、Phase 1では全文Recheckの結果とdiffログの事後観測に
   留める、§5-4実装リスク参照)。
4. **ambiguous時はwindow全体判定へ安全側フォールバック**
   (`evaluate_target_sentence_status`のtarget-sentence-matchingロジック、
   隣接文の逸脱に対象文のRewriteが誤ってblockされないようにする一方、
   対象文自体の判定が曖昧な場合は安全側[window全体]で判定する)。
5. **置換失敗時は原文復帰**(TTS Local Rewrite[#11]のfail-closed思想。
   E-1/E-2のguard抵触時「置換を破棄し元の全文へ戻す」[§5-2 (1)]、
   J-1/J-2のguard抵触時の段階的フォールバック[§5-4]は、いずれもこの
   思想を踏襲する。silent failで出荷しない)。
6. **`prior_issues`による個別解消確認**(既存Family X `must-fix
   retry`[#2.2、`run_deviation_check(..., prior_issues=...)`]の
   インターフェースをStage 1 Recheck全体[§3-0 A1]へ統合する)。

### 5-6. Rewrite品質制約(委任_13、Fable追加指示、不要Rewrite削減と品質
維持の両立)

**背景**: Opus L2レビュー#3論点6-Bにより、iteration4の実際のRewrite出力で
4種類の読み物品質劣化(hook喪失、重複段落、接続破断、語彙難化)が実測され、
既存の品質劣化検出(v1、文数/段落数/hedge語数/タイトル変更)はそのうち3種を
検出できていなかったことが判明した(§8-6参照)。検出だけでなく、Rewrite
自体の生成品質を上げる制約をprompt側へ追加する。

**実装**: Stage 3のRewrite Prompt(E2_GENERIC/E2_PARAGRAPH/J1_GENERIC/
J1_PARAGRAPH/FULL_TEXT_FALLBACK、いずれも既存テンプレート文字列は変更
せず、既存の`{rewrite_hint}`埋め込み箇所を使う非侵襲策)へ、以下を
`rewrite_hint`の末尾へ追記する形で注入する(`level_constraint_text()`):
1. タイトル・冒頭の物語装置(hook)は、BLOCKING claim自体がそこに含まれ
   ない限り保持する。
2. 削除で直る場合は削除を優先し、言い換えで新しい情報・語彙・主張を
   足さない。
3. 他の段落に既にある内容を、別の段落で繰り返さない。
4. 対象レベル(Standard=A2、Advanced=B1B、`infer_article_level()`で
   instance_id命名規則[`_a2`/`_standard`→A2、`_b1b`/`_advanced`→B1B]
   から判定、該当しないfixtureは共通制約のみ)の語彙・文長制約。A2側は
   Production Prompt定数`er012_b_family_voices_a2_production_01.
   A2_TABLE_PRINCIPLES_JA`(CURRENT_SPEC.md「CEFR-A2構造・音声仕様」節
   からの引用)を読んで要約引用し、B1B側はCURRENT_SPEC.md「B1(独立生成
   Natural Spoken News English)」節を読んで要約引用した(いずれも
   read-only参照、Production自体は呼び出さない)。

**生成後の機械チェック+同一cycle内1回だけの再生成**: Rewrite生成後、
§8-6の品質劣化検出v2(`measure_rewrite_quality_degradation_v2`)を実行し、
(a)重複段落・(b)孤立逆接語・(c)語彙難化のいずれかを検出した場合のみ、
Rewrite前のテキストへ戻し、制約を強調した指示(`REGENERATION_EMPHASIS_
TEMPLATE`)を追加して同一cycle内で1回だけ再生成する(`_run_stage3_
cycle`ヘルパーで2回目呼び出しを実装)。(d)タイトル/hook変更は正当な
理由(BLOCKING claim自体がそこにある)がある場合もあるため、単独では
再生成トリガにしない(常時フラグとして報告のみ)。追加call数はトリガした
instanceのみ、対象claim数×1回分(既存Stage3単価と同水準)。

### 5-7. 最小変更ラダー・セクション役割維持(委任_14 B-3/B-4、2026-09-30
ユーザー新方針item3/item5)

**背景(item3)**: Rewriteは「最小変更」第一原則。①単語・接続詞のみ
②文の一部 ③1文 ④段落 ⑤より広い範囲 ⑥記事全体、の順に試し、前段で
直れば後段へ進まない。iteration5までの`single_text_rewrite`は
「対象文を含む段落ブロックが特定できれば常に段落単位(E2_PARAGRAPH)を
最初に試す」実装だったため、iteration5の全Rewrite event(28件)を委任_14
作業Cで机上分類したところ、ほぼ全てが段落単位から開始していたことが
判明した(単語・接続詞レベルで直る可能性のあるケースでも常に段落単位が
選ばれていた)。

**実装**: `single_text_rewrite`の非delete分岐を、①単語・接続詞のみ
(新設`E1_MINIMAL_WORD_PROMPT_TEMPLATE`、"so"→"while"/"meanwhile"相当の
接続詞置換・文分割を明示的に例示) → ③1文(既存`E2_GENERIC_PROMPT_
TEMPLATE`) → ④段落(既存`E2_PARAGRAPH_PROMPT_TEMPLATE`、対象文を含む
段落ブロックが特定できる場合のみ)の順に試すladderへ再設計した(②文の
一部・⑤より広い範囲は、API呼び出し回数を無制限に増やさないため①・④
へ実務的に統合、⑥記事全体は既存`FULL_TEXT_FALLBACK`のまま維持)。各水準は
既存のguardロジック(`updated_text != full_text and claim_text.strip()
not in updated_text`)を満たした時点で停止する(新しい安全判定は発明
せず既存guardを再利用)。`ladder_level_used`を`rewrite_records`へ記録し、
§8-7で段別分布を測定する。

**既知の限界**: `paired_rewrite`(JA/EN対訳ペア、origin=ja_sourceの
claim向け、J-1機構)はラダー未適用のまま(`ladder_level_used=
"paired_j1_not_laddered"`)。JA/EN対訳の単語単位ラダー化は新設スコープが
大きく本委任では見送った(次回委任の課題)。2026-09-30ユーザー新方針
item4のB3型実例(`bgroup_B3`、接続詞"so"の因果)自体がorigin=ja_sourceの
claimであったため、実測(iteration6)では**ラダーの恩恵を受けず、従来
どおり段落単位(paired J-1)でRewriteされた**(達成できなかった点として
正直に報告、REPORT§15参照)。

**背景(item5)**: 各パートの役割(Title=引きつける/Hook=演出・興味喚起/
本文=ストーリー性・読みやすさ/In one line=短く圧縮して締める)をRewrite
後も維持する。

**実装**: `measure_section_role_violation`(¥0、決定論)が、Rewrite前後で
(a)In one lineの長文化(語数+30%超)、(b)Title/In one lineへの数字追加、
(c)Hookの縮小(語数50%未満への減少)、(d)Hook/Titleのレトリックマーカー
(疑問符・感嘆符・引用符・"imagine"等)消失、を検出する。検出時は
§5-6の品質劣化検出v2と統合し、同一の再生成トリガ(`_run_stage3_cycle`の
2回目呼び出し)へ合流させる(新しい再生成機構は作らない、既存機構の
条件を拡張しただけ)。

### 5-8. J-1(paired JA/EN local rewrite)への最小変更ラダー適用(委任_16
B-1、2026-09-30ユーザー新方針item4是正)

**背景**: §5-7で導入したsingle_text_rewrite側の最小変更ラダー(①単語・
接続詞→③1文→④段落)は、`paired_rewrite`(J-1、JA/EN対訳ペア、
origin=ja_sourceのclaim向け)には未適用のままだった(`ladder_level_used=
"paired_j1_not_laddered"`固定)。2026-09-30ユーザー新方針item4の
flagship例(`bgroup_B3`、接続詞"so"の因果claim)自体がorigin=ja_sourceの
claimであったため、iteration6実測ではラダーの恩恵を受けず、従来どおり
段落単位(`j1_paired_rewrite_paragraph`)でRewriteされていた(§7-0-iter4の
「達成できなかった点」として報告済み)。

**実装**: `paired_rewrite`を`single_text_rewrite`と同じ三段ladder
(①単語・接続詞[新設`J1_MINIMAL_WORD_PROMPT_TEMPLATE`、JA側は
「〜ので/そのため/だから」→「一方/その間/同じ頃」相当の接続詞置換、
EN側はso→while/meanwhile相当の接続詞置換・文分割のみを許可]→③1文
[既存`J1_GENERIC_PROMPT_TEMPLATE`]→④段落[既存`J1_PARAGRAPH_PROMPT_
TEMPLATE`、対象文を含むブロックが両言語で特定できる場合のみ])へ再設計
した。guardは`single_text_rewrite`と同型(`ja_revised`/`en_revised`が
共に非空、両言語のテキストが変化、かつclaim_text原文がEN側から消えて
いること)を各水準で満たした時点で停止する(既存guardロジックの再利用、
新しい安全判定は発明しない)。両言語の対象文特定に失敗した場合、または
全水準がguardを満たせなかった場合は、既存のJA全文フォールバック
+EN局所編集/全文フォールバック(委任_11 作業B-1/B-2是正済み、変更なし)
を水準⑥として維持し、成功時は`ladder_level_used="6_full_article"`を
記録する。

**代表ケースTrial実測(委任_16 作業C、`bgroup_B3`)**: 最終的な安全な
rubric構成(RUBRIC_R3_TRIPLE_PRIME、§6-4参照)のもとで、`bgroup_B3`の
"so the flashy 20% plan left the stage"claimはBLOCKINGのまま維持され、
`ladder_level_used="1_word_connective"`(method=`j1_e1_minimal_word`)で
解消することを実測確認した(n=2、両sample一致)。段落単位Rewriteは発生
せず、`section_role_violation`も0件(In one line語数不変)。2026-09-30
ユーザー新方針item4の目標(「まずso→while/meanwhile相当の最小変更で
解消を試す」)をB3自身の実例で達成した(iteration6の既知の限界を解消)。

### 5-9. precheck合成マーカーの実文解決・⑥全体フォールバックの例外化
(委任_18 2-1(a)(b)(d)、iter6全件開示[`docs/pm/open233_iter6_rewrite_
disclosure_01.md`]§1-1是正)

**背景**: iter6の全体Rewrite(水準⑥)3件は、開示分析により3/3とも
「locate失敗の副作用」と機械確認された。うち2件(`safety_er009_
changed_number`)は、pre-check(`build_precheck_floor_claims`)が
`claim_text`へ**article_evidence(診断用の合成文字列、例:"count values
found in article not matching any ledger fact: [30000000.0]")をそのまま
代入**していたことが根本原因だった。この文字列は記事本文に一言一句
存在しないため`locate_target`の3段フォールバック(rewrite_hint引用→
`locate_best_sentence`→`er010.locate_target_sentence`)がいずれも
`found=False`を返し、①〜④のladderが一度も呼ばれないまま⑥へ必然的に
落ちていた(単語演算令ミスではなく、コード構造上①〜④のforループ自体に
入らない設計だった)。同じ数値ズレを検出したtitle側claim(Stage1由来)は
①水準で正常に解消しており、「⑥まで必要だったという実測根拠はない」と
disclosure §1-1-2は結論づけている。3件目(`safety_er009_unsupported_
new_claim`)は逆に「⑥の方が①相当より安全だった」逆転現象(局所削除が
title全体消失を招いた)を示しており、⑥経路自体の削除は推奨されていない。

**実装1(2-1(a)、`resolve_precheck_target_sentence`+`build_precheck_
floor_claims`是正)**: precheck finding(`number_mismatch`/`date_
mismatch`/`actor_missing`/`comparison_marker`/`negation_marker`)から、
finding固有の生の実測値(`foreign_values`/`other_dates_raw`/
`matched_phrase`/`article_evidence`[list]、precheck module側へ追加
フィールドとして併記。既存`article_evidence`文字列は後方互換のため
変更しない)を使い、記事本文中の実文(その値を含む文)を
`split_sentences_generic`で検索する。見つかればそれを`claim_text`として
使う(以降は既存`locate_target`の通常経路がそのまま機能し、①〜④の
ladderが正しく試行される)。

**実装2(2-1(b)(d)、`single_text_rewrite`/`paired_rewrite`の`found=
False`早期return)**: 実文解決を試みても`locate_target`が`None`を返す
場合(found=False、single_text_rewriteは対象文が一度も特定できない場合、
paired_rewriteはEN/JA双方とも特定できない場合)、⑥全体フォールバックを
「試行して失敗した最後の手段」として使うのは不適切と判断し、Rewriteを
試みず`target_not_locatable=True`を返す。呼び出し側(`run_instance`)は
この場合、他claimの結果を保存したうえでcycleを打ち切り、
`stage4_reason="target_not_locatable"`でSTAGE4_ESCALATIONへ回す(人間へ
「locateできなかった」という明示理由を渡す)。**⑥は「found=True(対象
文は特定できた)だが、①〜④[delete型は再出現検出]の全段でguardが失敗
した」場合のみ到達する経路として残す**(①〜④/delete試行のログが
call_logに残っている正当な最後の手段、disclosure §1-1-3の「⑥が①より
安全だった」逆転現象への対応として、この経路自体は削除しない)。

**期待される効果**: precheck由来のnumber_mismatch/actor_missing等の
claimは、記事本文中に実際に矛盾する数値・主体が書かれている限り、
実文解決によって①水準(単語・接続詞のみ)で解消できる可能性が高い
(`safety_er009_changed_number`のtitle側claimが実際に①で解消した実績と
整合)。代表ケースTrial(rep9)で`safety_er009_changed_number`/
`safety_er009_changed_actor`の`ladder_level_used`が`6_full_article`に
ならないことを確認する(委任_18 REPORT§18参照)。

**未解決部分(disclosure §1-1-4、本節ではガード追加のみ対応・§6-5参照)**:
delete型Rewriteの対象がセクション全体(title/hook)と一致し、削除後に
空文字列になるケースの検出漏れは、本節の実文解決だけでは解消しない
(locate自体は成功するため)。§6-5の`title_degenerate`/`hook_degenerate`
guardで別途対応する。

### 5-10. ⑥(全体Rewrite/削除)の標準ラダーからの除外(委任_23 B-2、
REPORT§23 B)

**背景(iter7実測)**: 広いTrial iteration 7(29 instance全量)で初めて
⑥(`6_full_article`)が7件(`safety_A2A3`×2・`safety_A4`×4・`bgroup_B4`
×1)発生し、worst instance cost¥8.9545(`safety_A4`、iter6の¥5.7883から
悪化)という新たなtail riskが判明した(委任_22時点で報告済み)。

**⑥ 7件の試行記録表(委任_23 B-1、REPORT§23 B詳細)**: 7件全てについて
①〜④/delete試行ログ(call_log)を確認した結果、**7/7とも①〜④/delete
全段でguardが失敗した後に⑥を試み、⑥使用後も最終的にSTAGE4_ESCALATIONへ
到達していた**(⑥使用がそのまま解消[RESOLVED_REWRITE系]に至った例は
**0/7**)。「⑥が必要だった」Evidence(⑥がなければ解消しなかったはず、
という反実仮想を裏付ける実測)は0件であり、⑥の合計費用(iter7、7件分の
fulltext_fallback call)がworst costの主因と特定した。

**是正(既定OFF、コード削除なし)**: `ENABLE_LADDER_LEVEL_6_FULL_REWRITE`
(feature flag、既定False)を新設した。無効時、`single_text_rewrite`/
`paired_rewrite`は①〜④/delete全段でguardが失敗した時点で⑥のAPI call
(`FULL_TEXT_FALLBACK_PROMPT_TEMPLATE`)を試みず、`ladder_exhausted_
without_full_rewrite=True`を返す。呼び出し側`run_instance`は
`target_not_locatable`と同じパターンでこれを検出し、直ちに
`stage4_reason="ladder_exhausted_without_full_rewrite"`でSTAGE4_
ESCALATIONへ回す(⑤を未試行のまま追加cycleへ進まない、既存の安全装置
[HARD_MAX_CYCLES等]は無変更)。flagをTrueへ戻せばiter7以前と同じ①〜⑥の
挙動に完全復元する(コードは削除せず保持、**再有効化はユーザー判断**)。

**⑤(より広い範囲)の扱い**: §5-7(委任_14 B-3/B-4)の時点で、②(文の
一部)・⑤(より広い範囲)はAPI呼び出し回数を無制限に増やさないため
実務的に①・④へ統合済みであり、コード上「5_」という独立したladder
水準は**そもそも存在しない**(grep確認済み)。よって「⑤の成功件数」は
定義上0件であり、これは委任_23での新規の失敗ではなく既存設計どおりの
統合結果である。⑤単独の無効化は対象が存在しないため実装しない。

**rep14実測での検証(`safety_A4`×n=1、¥1.5084、REPORT§23 D参照)**:
iter7で本fixtureのworst costだった原因(4回の⑥試行)が、本是正後は
1件の`ladder_exhausted_without_full_rewrite`(claim MUSE-HC-012)で
直ちにSTAGE4_ESCALATIONへ回り、**コスト¥1.5084**(iter7の同fixture
worst¥8.9545から**83%減**)となった。Safety floor(floor_reason=
`deterministic_floor:changed_actor`)は本是正後もstage2_results上で
引き続き`materiality=BLOCKING`(floor-strict、Production実際の挙動)を
維持しており、最終的にfalse PASSではなくSTAGE4_ESCALATION(human
review)へ正しくfail-closedした。`floor_variant_comparison.safety_
group_hard_gate_passed=false`(false_negative_candidates_safety_group=1)
が本runで記録されたが、これは`llm_materiality`(Stage2のLLM独自判定、
floor無しでの仮想判定)の run間非決定性によるものであり
本節の変更(Stage3のみに影響)とは無関係(§4-12/§4-13の「floor-cited
variant」という**採用されていない設計案**の反実仮想比較指標であり、
実際に稼働しているfloor-strict自体はこのrunでも正しくBLOCKINGを
維持した。iter7の同一metricは0件だったため次回委任での追加観測対象と
する)。

**unittest**: `TestLadderExhaustedWithoutFullRewriteWiring`(新規2件)、
`single_text_rewrite`の既存⑥テストを「既定OFF時はladder_exhausted_
without_full_rewriteを返す」新テストへ更新し、「flagを明示的にTrueへ
戻すと従来どおり⑥で解消する」regressionテストを別途追加(コード削除
なしを実証)。

### 5-11. 問題種類→初期Rewrite単位の写像+escalate_to_paragraphの廃止(委任_27 Part1-1/1-2)

**背景**: §6-6 A-2で導入した`escalate_to_paragraph`(同一fact_idの
claimが別文言・別箇所で再出現した場合、①単語・接続詞/③1文を飛ばし
④段落水準から試す)は、§0-4の上位原則(各箇所は独立に初期単位から
判断する)と整合しない。「同じFactが再登場したら段落Rewrite」という
再出現ベースの判断ではなく、**問題の種類**(用語範囲/数値丸め/因果/
主体/時間/文全体/複数文)に基づいて初期単位を決めるべきである。

**是正1(廃止、§1-1)**: `escalate_to_paragraph`によるladder skip
(levels配列から`1_word_connective`/`3_sentence`を除外する処理、
`single_text_rewrite`/`paired_rewrite`双方)を、新設フラグ
`ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP`(既定`False`)でガードする。
コード自体は削除せず残すが(再有効化時の参照用)、既定では発火しない
(経路削除相当)。同一fact_id再発の検出・記録自体(`prior_blocking_
records`・`same_claim_reblocked_escalated_to_paragraph`ログ・§3-3の
`same_claim_fact_id_reblocked`STAGE4判定)は変更しない(これは
「Rewriteが効かなかったことの実証によるfail-closed」という別の安全
機構であり、本委任のスコープ[初期単位の選び方]とは独立)。

**是正2(問題種類分類、§1-2)**: Stage1のdeterministic floor flag
(`changed_scope`/`changed_number`+丸め抑制済み/`changed_causality`/
`changed_actor`/`changed_time`、および§4-3既存の`changed_negation`/
`changed_comparison`/`changed_certainty`/`changed_fact`/
`unsupported_new_claim`)から、決定論(¥0、LLM呼び出しなし)で問題種類
を分類する関数`classify_problem_kind(dev)`を新設する:

| 分類 | 判定条件(dev flag、優先順位は上から) | 初期ladder水準 |
|---|---|---|
| `term_scope` | `changed_scope` | ①(word/connective、名詞句置換を含む) |
| `rounding` | `changed_number`かつ`changed_number_suppressed_reason` | Rewriteなし(levels=[]) |
| `causality` | `changed_causality` | ① |
| `actor` | `changed_actor` | ①(§1-3ガード併用) |
| `time` | `changed_time` | ① |
| `sentence_logic` | 上記非該当かつ`changed_negation`/`changed_comparison`/`changed_certainty`/`changed_fact`/`unsupported_new_claim`のうち1個のみ該当 | ③(1文) |
| `multi_sentence` | 上記が2個以上同時該当 | ④(段落) |
| `unspecified` | 上記いずれにも非該当(既存fixtureの後方互換、devにfloor flagが無い場合) | ①(既存挙動を維持) |

既存levels配列(①→③→④の順で構築、guardを満たした最初の水準で停止
する既存ロジックは無変更)に対し、`filter_levels_by_problem_kind`で
初期水準未満のlevelを除外する。**初期水準より上位への昇段(guard失敗
時のfallback)は妨げない**(「初期単位」は開始点であり上限ではない、
§0-4の表はあくまで「まずどこから試すか」を定めるもの)。`rounding`の
みは例外的にlevels=[]としRewriteを試行しない(§0-4「原則Rewrite
なし」)。既存test(devにfloor flagを持たないfixture)は`unspecified`
(①開始)に分類され、既存の結果(①で停止/③へ昇段)と完全に後方互換
(委任_27実測、既存222件+新規19件=241件全PASS)。

**是正3(主体置換ガード、§1-3)**: `actor_rewrite_guard_ok(before_text,
after_text, ledger_text)`を新設する。Rewrite後にのみ新しく現れた主体語
(一般的な役割名詞、`_ACTOR_NOUN_PATTERN`)が、Ledger本文(fact本文
全体を含むledger_text、¥0・決定論の部分文字列一致)に一語も含まれない
場合はRewriteを却下する。新しい主体語が一つも導入されていない場合
(既存語の保持・削除のみ)は常にTrue(このガードの対象外)。
`single_text_rewrite`/`paired_rewrite`双方で、problem_kind=="actor"
の場合のみ適用する。**unittest(neg1 cycle2実データ)**:
`docs/pm/open233_evidence_disclosure_neg1_neg3_hormuz_01.md`§1の
MUSE-HC-012実データ(`users`→`employees`、floor_reason=
`deterministic_floor:changed_actor`)を fixtureとして使い、`employees`が
MUSE-HC-012のledger_text(JA本文のみ)に含まれないため却下される
ことを確認した(`TestActorRewriteGuard`)。

**是正4(等価QA理由文の保存、§1-4)**: `ja_en_equivalence_verdict`
(verdict文字列のみ)に加え、`ja_en_equivalence_reason`
(`notes`/`meaning_changes`/`important_omissions`/
`unsupported_additions`/`number_name_negation_issues`)をcycle_record・
call_logへ保存する(¥0、既存呼び出しの戻り値`raw`を捨てずに使うのみ)。

**是正5(重大誤解原則の追加、§1-5)**: §4-18参照。

**既知の限界**: `rounding`分類のclaimが(floor抑制をすり抜けて)
Stage2 LLM判定単独でBLOCKINGになった場合、levels=[]によりRewrite失敗
扱いとなり既存のfail-closed経路(Stage4)へ進む。「Rewriteなしで黙って
通過させる」という新しいaccept経路は作らない(既存Safety設計
[fail-closed]を独断で緩めない、§1原則「Safety対照群は常にBLOCKING
維持」と矛盾しないための意図的な保守設計)。Hormuz要素Trial A(§9-1⑰)
では`rounding`分類のclaimがBLOCKINGに至る事例は観測されなかった。

## 6. Stage 4 Escalation条件と人間への提示情報

### 6-1. Escalation条件

- Stage 3が2 cycleを使い切った後もStage 1 RecheckでBLOCKING-candidate
  が残る。
- JA Fact Check自体がSTOP(`JAFactCheckStopError`、既存の独立した
  fail-closed機構)した場合は、Stage 3のcycle上限を待たず即Escalation
  (これは「JA差し戻し後の再生成がそもそも安全な文章を作れなかった」
  という、Rewriteの土台自体が壊れているケースであり、Rewriteを重ねる
  対象ではない)。
- Stage 2が「判断不能」(materiality判定自体がスキーマエラー・
  API失敗等)を返した場合も、fail-closedでBLOCKING確定として扱い、
  Stage 3へ進める(Escalationの直接理由にはしない。Stage 3 cycleの
  中で吸収する)。
- **[委任_04改訂/A1]** Stage 1 Recheckで`overall_status==
  LEDGER_COMPLIANT`だが`all_prior_issues_resolved==False`の場合は
  BLOCKING-candidate扱いとし、cycle残数があればStage 2へ、枯渇して
  いればStage 4へ進める(§3-0参照。既存Production gateと同一の
  厳しさを維持、Opus論点5推奨1)。
- **[委任_04改訂/A7]** cycle 1と同一のclaim/fact_idが再度BLOCKINGに
  なった場合は、cycle残数に関わらず即Stage 4(§3-3/§5-3参照、Opus
  論点7推奨1)。
- **[委任_04改訂/A7]** `assert_budget_ok()`(既存Production予算abort、
  `er012_...py` L455/L547)がtripした場合は即Stage 4(Rewrite/Recheckを
  重ねる前に予算超過を検知した時点で停止、Opus論点1(D))。
- **[委任_04改訂/A7]** Stage 1(初回またはRecheck)のAPI呼び出し自体が
  失敗、またはschemaパース失敗した場合は、**fail-closedとして
  BLOCKING-candidate扱いでStage 2へ強制送付**する(「deviationなし」
  として無検査で通さない、Opus論点5推奨4)。cycle残数が枯渇していれば
  Stage 4。

**[委任_04新設/A7] Stage 4到達理由とコード上の例外型・条件の対応表**
(Phase 1観測項目として必須、Opus論点1推奨3):

| Stage 4到達理由(区分) | 対応する既存コード/条件 |
|---|---|
| cycle上限(最大2)使い切ってもBLOCKING | 本設計のcycle counter(新規実装) |
| JA Fact Check自体がSTOP | `JAFactCheckStopError`(`stage="original"` / `"r2"` / `"original_symbol"` / `"r2_symbol"`、`er019_family_x_ja_writer_o_r1_r2_01.py` L276-344) |
| `all_prior_issues_resolved==False` | `vfl01.run_deviation_check(..., prior_issues=...)`の返り値(`er003_v1_en_direct_vfl_01_generate.py` L649-656) |
| 同一claim/fact_id再BLOCKING | 本設計のclaim/fact_id比較ロジック(新規実装、§3-3/§5-3) |
| 予算abort | `assert_budget_ok()`(`er012_...py` L455/L547) |
| Stage 1 API/schema失敗 | 既存の例外処理(呼び出し元でのtry/except、fail-closedとして本設計で明示追加) |
| 段落数retry枯渇後のNG | `_family_x_ensure_split_or_paragraph_retry`1回上限後のNG(`er012_...py` L294-325、L408-414/L502-508) |

### 6-2. 人間へ渡す情報(一意に確認できる形)

- `article_id`/`writer_stage`/該当claim本文/該当fact_id/Stage 1の
  10 flags/Stage 2の`materiality`+`basis`+`rewrite_hint`(cycle 1・2
  両方)/Stage 3で実際に何を書き換えたか(diff)/Recheck結果(cycleごと)。
- 「なぜ自動回復できなかったか」の一文要約(例: 「cycle 2回とも
  Rewriteで別のBLOCKINGを誘発した」「JA Fact Check自体がSTOPし
  Rewriteの土台が作れなかった」等、パターン別の定型文)。
- 「人間が確認すべき一意の問い」: 該当claimをどう修正すべきか
  (Ledgerのどのfactに合わせるべきか)、または当該記事全体を作り直す
  べきか、の二択を明示する。

### 6-3. cite-or-release(委任_13、Opus L2レビュー#3論点4推奨1・2、
`_recheck_confirm`のfail-closed厳格化)

**注記**: 委任文では本節を「§6-2」と指定していたが、§6-2は既存の
「人間へ渡す情報」節が既に占有しており、既存節番号への言及(他所の
クロスリファレンス)を破壊しないため、新規追加分は§6-3として追記する。

**背景**: overall_status=LEDGER_COMPLIANTかつall_prior_issues_resolved=
Falseという自己矛盾する応答が出た場合、追加1 call(旧`_recheck_confirm`)
で再確認しているが(§3-3是正6)、確認callが「未解消」と判定する根拠が
記事本文中に実在するかを検証していなかった。neg3の実測(iteration4)では
実際に別箇所へ主張が残っていた(正しいSTAGE4)一方、根拠のない「未解消」
判定でSTAGE4になるリスクも理論上残っていた。

**実装**: 確認call(`run_recheck_confirm`)のschemaへ`remaining_sentence`
(未解消と判断する根拠として、現在の記事本文中に実在する文の逐語引用)を
必須項目として追加した(`CONFIRM_PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA`、
vfl01[Production]は変更せずTrial側でschema/instructionを組み立てる)。
応答後、`apply_cite_or_release()`で機械検証する: resolved=falseの各項目
について、remaining_sentenceが現在の記事本文に実在すれば(cite)そのまま
未解消(STAGE4、正しい)、実在しなければ(根拠なき未解消)resolved=true
へ機械的に上書きする(release)。fail-closedを緩めず、根拠のない未解消を
機械的に排除する方向の厳格化である。あわせて、Rewrite前後の対象文ペア
(before→after、`build_before_after_instruction`)をinstructionへ添え、
モデルが消えた文を探し回る負担を減らした(`single_text_rewrite`/
`paired_rewrite`が返す`before_fragment`/`after_fragment`のうち、単一文
置換で判明したものだけを使う。paragraph-level rewriteやfull-text
fallbackではfragmentを一意に特定できないため対象外、既知の限界)。
追加call数は0(既存確認callのschemaを差し替えるのみ)。

### 6-4. Hook-aware統合(委任_14 B-5、監査結果に基づく、2026-09-30
ユーザー新方針item2)

**監査結果(詳細`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`
§A-1)**: Production HOOK_CLAUSE(`er003_v1_en_direct_vfl_01_generate.py`
L579-595)は**changed_scope/changed_comparisonの2種類のみ**緩和対象。
Family X(Hormuz/Meta記事の経路)・OPEN-233 Self-Recovery/Checker Trial
双方とも`hook_aware=False`のまま(未配線)。ユーザーが指摘したMeta hook
実例(`neg1_meta_b3prod_a2`)の実際のflagは changed_fact/changed_
certainty/unsupported_new_claim であり、Production HOOK_CLAUSEの緩和
対象(scope/comparison)には該当しない(Hook-aware判定を適用しても
このケースは変わらなかったと机上確認)。

**実装(意図的な縮小を含む)**: Stage2へ`section_type`
(title/hook/in_one_line/body、`detect_claim_section_type`、既存
`locate_best_sentence`を再利用した決定論的判定、¥0)を付与し、post-hoc
`apply_hook_aware_downgrade`が**changed_scope単独発火時のみ**BLOCKING→
QUALITYへdowngradeする。Fable原案(§2)はchanged_scope/changed_
comparisonの2種類を指定していたが、changed_comparisonはSelf-Recovery
Flow自身のdeterministic floor(`FLOOR_FLAGS`、Safety側の安全装置)に
含まれるため、これをHook-awareで緩和すると既存安全装置を弱めることに
なり、governance「既存の安全装置を独自判断で回避・無効化しない」に
抵触する。本委任ではchanged_scope単独のみへ意図的に縮小した(監査文書に
理由を記録、拡大にはFable/ユーザー判断が必要)。判定はLLMのHook解釈に
依存しない決定論的post-hoc方式とした(Stage2 promptは変更していない、
再現性・regression testの容易さを優先)。

**実測結果(iteration6、29 instance×n=2)**: `hook_aware_downgrade`
発火0件(該当条件[Hook区分×changed_scope単独×floor不発火]に合致する
claimが実際のfixture setに存在しなかった)。機構自体はunittest 5件で
独立に動作確認済み。Meta neg1のケースは本統合では解消されない(監査
文書の結論どおり)。

**Stage2 rubric側Hook-aware原則の試行と撤回(委任_16 B-2、2026-09-30
ユーザー新方針item2、代表ケースTrial実測に基づく設計判断)**: 上記の
post-hoc downgrade(changed_scope単独限定)ではneg1のMeta hook実例
(changed_fact/changed_certainty/unsupported_new_claim)を解消できない
という監査結論を受け、Stage2のLLM判定自体にsection_type
(title/hook/in_one_line/body)を入力として渡し、Title/Hook/場面描写/
attention grabberに対する演出許容原則を追記した新規rubric
(`RUBRIC_R4_HOOK_AWARE` = `RUBRIC_R3_TRIPLE_PRIME` + Hook-aware追記、
`er052_open233_self_recovery_stage2_calibration_01.py`)を実装し
run_stage2の実配線を一時的に切り替えた。代表ケースTrial(委任_16
作業C)で実行したところ、**Safety-critical 10claimの1つ(`bgroup_B3`、
`SAFETY_CRITICAL_SUB_IDS`)がQUALITYへ誤降格する**実測結果を得た
(適用対象がtitle/hook/in_one_line/bodyの4種すべてで、B3のclaimが
section_type="in_one_line"に分類されたため)。委任文の手順に従い、
適用対象をtitle/hookの2種のみへ限定する最小修正を1回行い当該ケース
のみ再実行したが、**in_one_lineを明示的に適用対象外としたにもかかわらず
同じ誤降格が再現した**(QUALITY 2/2、`er052_output/
open233_self_recovery_flow_runner_01_rep7/summary_rep7_b3_refix.json`)。
これはルール条件(section_typeによる適用可否判定)自体のバグではなく、
Hook-aware原則文がプロンプト中に存在するだけで、条件上は無関係な
section_typeの判定にも寛容化バイアスが波及した疑いが強い(LLMの
prompt priming効果、既存rubric較正[R2→R3→R3'→R3''→R3''']が積み上げて
きた「明確なNG列挙以外はQUALITY側」というtie-breakの効きやすさと、
新規追記した「演出は許容」という言い回しが、条件を満たさないclaimの
判定にも波及したと考えられる)。委任文§5のSTOP条件(「代表ケースが
最小修正1回後もFAIL」)に該当するため、**実配線を安全性が実測済みの
RUBRIC_R3_TRIPLE_PRIMEへ復帰**し(section_type自体はPython側の計算
[`detect_claim_section_type`]としてclaim_recordsへ引き続き保持するが、
**Stage2のLLMプロンプトへは渡さない**よう変更、iteration6と同一の
プロンプト内容を維持)、復帰後の再実測で`bgroup_B3`がBLOCKING 2/2へ
復帰することを確認した。`RUBRIC_R4_HOOK_AWARE`自体は削除せず次回委任
向けにコードとして保持する(Phase2課題、詳細REPORT§16/DECISION_LOG)。
neg1(Meta hook)自体の未解消は、post-hoc downgrade・rubric側の両approach
とも根本解消できておらず、Phase2への持ち越し課題として記録する。

### 6-5. 局所QA fastpath・全文Recheckを残す条件・degenerate output guard・
Escalation 2 run是正(委任_18 2-1(c)/2-3(a)(b)/2-4、2026-09-30ユーザー
新方針item1/7/9)

**A. degenerate output guard(2-1(c)、disclosure §1-1-4是正)**:
`measure_section_role_violation`へ`title_degenerate`(title変更後、空文字
または語数<3)・`hook_degenerate`(hook変更後、空文字)を追加した(¥0、
決定論)。既存`needs_regeneration`(1回だけ再生成を試み、再生成後も
同じ結果ならそのまま通過してしまう既存のガード漏れ、
`safety_er009_unsupported_new_claim`sample1でtitle完全消失が「解決」
扱いで通過していた実例)とは別に、**再生成試行後の結果[regenerated時]
を優先して判定し、degenerateなら無条件でRecheckの結果に関わらず
`stage4_reason="degenerate_rewrite_output"`でSTAGE4へ回す**(hard block、
既存needs_regenerationとは異なる新しい安全装置)。

**B. 局所QA fastpath+全文Recheckを残す条件(2-4)**: Production局所QA
(`er010_ledger_local_rewrite_09.extract_point_context`/`classify_
deviation_role`/`evaluate_target_sentence_status`、いずれも決定論の
純粋関数、read-only importで再利用しProduction自体は変更しない)の
設計思想(対象文単位のwindow判定)を踏襲し、「最小修正→修正文+前後1文
確認→問題解消・周辺影響なしなら終了」という基本形を実装した
(`run_local_qa_fastpath`)。局所QA 1 call(入力=修正文+前後1文+当該
Ledger fact[`build_ledger_excerpt`、関連factのみ]+prior_issue、出力=
`prior_issue_resolved`/`new_deviation_in_revised_sentence`/
`adjacent_sentence_affected`)を試し、全claim成功なら全文Recheck
(`run_recheck`/`run_recheck_confirm`)を省略する(cite-or-release
confirmは局所QAの`prior_issue_resolved`出力へ統合され、この経路では
別途呼ばないため重複callが解消される)。

全文Recheckを残す条件(`full_recheck_required`、いずれか1つでも該当
すれば局所QAは試みず既存の全文Recheckをそのまま使う): (a) このcycleで
段落単位[4_paragraph]・全体[6_full_article]・削除[0_delete]のいずれかの
ladder水準が使われた、(b) このcycleで2件以上のclaimをRewriteした、
(c) paired(J-1、JA・EN双方変更)が使われた、(d) deterministic floor由来
のclaimが含まれる、(e) Safety fixture(instance_idが"safety_"始まり)。

条件の根拠(disclosure §1-4-5実測): iter6の55 instance-run中、cycleが
2以上ある11 instance-runのclaim識別子をcycle間で追跡した結果、**4件
(うち3件Safety群)で全文Recheckがcycle1のRewrite対象とは別のLedger
fact由来の新規BLOCKING claimを検出した実績がある**(`safety_A2A3`×2run、
`safety_A5`×1run、`meta_run03_standard`sample2×1run)。上記(e)は
`safety_A2A3`/`safety_A5`を含むSafety fixture全体を対象外とすることで
この実測4件のうち3件(Safety群分)を確実に捕捉する。`meta_run03_
standard`sample2の1件は(b)(fact_id複数箇所=複数claim同時Rewriteに
なりやすい)で概ね捕捉される設計とした(条件は保守的[狭い]側に倒し、
局所QAで代替できるのは「単一claim・単一文水準・非floor・非Safety」の
狭い範囲のみに限定した)。それ以外(9/13 instance-run)は既出claimの
再検出のみで、局所QAでも同等に検出できた可能性が高いとdisclosureは
報告しているが、実際の削減効果はrep9実測(REPORT§18)で確認する。

**C. Escalation 2 run是正(2-3(a)(b)、`meta_run03_standard`両sample)**:

- **(a) sample1型(J-1が被フラグ文自体を変えず隣接文のみ変更)**: iter6は
  委任_16のJ-1ラダー化(§5-8)より**前**のコード(`ladder_level_used=
  "paired_j1_not_laddered"`)で実行されたものであり、現行コードは既に
  `level_guard_ok`条件(`claim_text.strip() not in candidate_en`、
  §5-8既存)を各ladder水準で満たさない限り次水準へ進む設計になっている
  ため、被フラグ文が変更されないままでは水準4[段落]も含め全段が
  guard失敗し、既存のJA全文フォールバック(⑥相当)へ落ちる設計に
  **既に**なっている(新規コード追加なし、既存のEvidence。rep9の
  `meta_run03_standard`実測でSTAGE4_ESCALATIONに至らないことを確認する)。
- **(b) sample2型(同一fact_idが記事内の複数箇所・異なる文言で分散)**:
  `run_instance`のcycle上限判定(`cycle > MAX_CYCLES`)に、「blocking件数が
  厳密に減少していなくても、その中に過去cycleで一度でもBLOCKINGとして
  見たfact_idの新しい箇所(claim本文は既にfind_matching_prior_recordで
  別物と判定済み)が含まれていれば、cycle上限3(`HARD_MAX_CYCLES`、
  無変更)を超えない範囲で1回だけ追加cycleを許可する」
  (`same_fact_id_new_location`)条件を追加した。既存の「blocking件数が
  厳密に減少していれば1回だけ追加cycleを許可する」条件(委任_11 作業
  B-3、§3-3)とはORで結合し、いずれかを満たせば従来どおり1回だけ
  (`extra_cycle_granted`フラグで多重付与を防止)。

**D. unittest(¥0、新規24件、`TestResolvePrecheckTargetSentence`/
`TestBuildPrecheckFloorClaimsLocatability`/`TestTargetNotLocatableEarly
Return`/`TestDegenerateRewriteGuard`/`TestDegenerateRewriteHardBlock
Wiring`/`TestApplyDisclosureGapDowngrade`/`TestApplyDisclosureGap
DowngradeWiredIntoStage2`/`TestFullRecheckRequired`/`TestFindSentence
Context`/`TestLocalQaFastpathWiring`/`TestBuildLedgerExcerpt`)**:
既存154件(er052系4ファイル合計)+新規24件、全件PASS(詳細REPORT§18)。

### 6-6. 全文Recheck条件の最小化調査(委任_19 A-1)+同一fact_id再出現時の
ラダー前進(委任_19 A-2)+neg3両論併記(委任_19 A-3)

**背景**: 委任文は「paired J-1は①〜③(語/一部/1文)の局所変更なら
`full_recheck_required`の条件から外す」ことを求めていた。本節は、この
narrowingを検討した結果、**実装せず条件(c)を維持する**という決定に
至った経緯と根拠を記録する(disclosure §1-4-5の4件[safety_A2A3×2/
safety_A5×1/meta_run03_standard s2×1]を取りこぼさないことに加え、
本委任のrep9再調査で判明した5件目[`hormuz_run03_standard`sample1]を
新たな反証として重視した)。

**A-1捕捉表(disclosure 4件+新規1件が、narrowing後もどの条件で捕捉
されるか)**:

| # | instance/run | 元の捕捉条件 | narrowing(c)実装時の捕捉条件 | 結論 |
|---|---|---|---|---|
| 1 | `safety_A2A3` s1/s2 | (e)safety_fixture | (e)で維持(mechanism非依存) | 取りこぼしなし |
| 2 | `safety_A5` s1 | (e)safety_fixture | (e)で維持 | 取りこぼしなし |
| 3 | `meta_run03_standard` s2 | (d)floor claim(実測はfloor経由) | (d)で維持 | 取りこぼしなし |
| 4(新規) | `hormuz_run03_standard` s1(cycle1、初回発生) | (c)blanket paired | **narrowing後は無条件放出**(cycle1は`repeat_fact_ids`が空のため新設(f)も不発火、ladder level=3_sentenceのため(a)も不発火) | **取りこぼす**(局所QAは対象文±1文しか見ないため、記事の別箇所[見出し/one-line]に同一fact_idの問題が初めて存在することを構造的に検出できない。fastpathがEN側だけを見て「解消」と誤判定し、cycleループ自体が起動せずSTAGE4_ESCALATIONに正しく到達していたはずの経路が消える=サイレントPASSの新規リスク) |

**判断**: 4件目(新規)が「取りこぼす」ため、委任文§4のSTOP条件
(「全文Recheck条件最小化で開示分析の4件のいずれかを取りこぼす」)の
文言上は4件[disclosure記載分]のみが対象だが、**同じ性質のリスクが
5件目として現に実測されたため、安全側にnarrowingを見送った**
(`full_recheck_required`の条件(c)「`both_ja_en_changed(paired_j1)`」は
ラダー水準に関わらず維持、コード上変更なし)。

**新設(f)による多層防御**: 過去cycleで一度でもBLOCKINGだったfact_idが
このcycleにも含まれる場合(`same_fact_id_reappeared_across_cycles`)、
mechanism(single_text/paired問わず)を問わず全文Recheckへ回す条件を
新設した。cycle1(初回発生)には効かない(4件目のケースはcycle1で
発生するため(f)だけでは救えない、これが(c)を維持した理由)が、
cycle2以降の同種再発(disclosure §1-4-5の55 instance-run中9件の
「既出claimの再検出のみ」パターン)に対する追加の安全網として機能する。

**locateバグの是正(fastpath不発火の真因)**: rep9実測(REPORT§18-4)で
局所QA fastpathが3試行中2件失敗した原因を調査した結果、条件(a)〜(e)
自体の問題ではなく、`find_sentence_context`(局所QA用)が使う文分割
(`split_sentences_generic`)と`locate_target`が使う文分割
(`locate_best_sentence`内の別regex)の方式不一致により、Rewrite後の
`after_fragment`がexact substringとして再発見できないケースがあったことが
濃厚と判明した(完全な再現はできなかったが、代替のSequenceMatcher近似
[閾値0.85]をfail-closedで追加し、exact不一致時のみfallbackする)。

**A-2: `escalate_to_paragraph`(同一fact_id再出現時のラダー前進)**:
`hormuz_run03_standard`sample1でcycle2以降にfact_id=HF-009が別文言で
再検出された際、①単語・接続詞/③1文の局所ラダーは既に効果不足と実証
されたとみなし、④段落水準から直接試す(cycle数の上限[MAX_CYCLES/
HARD_MAX_CYCLES]自体は変更しない、狭いラダー選択のみの変更)。

**既知の限界(正直に記録)**: `hormuz_run03_standard`の実例は、cycle1〜2が
本文(body)、cycle3が見出し/one-line要約という**別セクション**への
分散であり、対象claimを含む段落単位のRewriteでは他セクションまでは
直せない(Phase2課題item8、複数箇所分散Rewriteの根本解決ではない)。

**rep10実測(REPORT§19)**: `hormuz_run03_standard`sample1がcycle2で
`escalate_to_paragraph`発火(`full_recheck_required_reasons`に
`same_fact_id_reappeared_across_cycles`を確認)、`ladder_level_used=
"4_paragraph"`で解消し**STAGE4_ESCALATIONに至らなかった**(rep9では
`cycle_limit_exhausted_after_recheck`でSTAGE4だった同一instanceが
今回2/2 sampleとも解消)。段落単位のRewriteが結果的にcycle1で書き換えた
文を含む段落全体を書き直したことで、cycle3で問題になっていた見出し/
one-line要約側の言及とは別に、body側の言い換え耐性が上がったと推定
されるが、これは`hormuz_run03_standard`のこの実行回でのみ確認された
実測であり(non-determinism下での1回のn=2実測)、「別セクション分散は
段落単位では解決しない」という上記の限界の論理自体を覆すものではない
(次にこの限界が顕在化するfixtureが出た場合は同じ問題が起き得る)。

**局所QA fastpath発火0件(rep9に続き未実証のまま)**: rep10で選定した
7 instance(hormuz_run03_standard/neg3/bgroup_B3/hormuz_run02_advanced/
safety_er009_changed_number/safety_A2A3/safety_A5)は、**全cycleで
条件(a)〜(e)のいずれかが該当し、`local_qa_fastpath_attempted`は
14 instance-run全てで`False`**(`find_sentence_context`のlocateバグ
是正は単体テストでのみ検証済みで、実runでの効果測定機会は今回も
得られなかった)。7 instanceがいずれも(paired J-1/floor/safety
fixtureのいずれかを含む)複雑ケースとして選ばれたことが理由であり、
Normal群の単純ケース(non-safety・non-floor・non-paired・単一claim)を
含めれば発火する可能性はあるが、本委任の限定Trialでは未実測。

**A-3: neg3(`neg3_hormuz_prodrunner_b1b`)のStage2 n=3再現性測定+両論
併記**: HF-009のclaim「The fee plan left the stage, but the events
driving oil prices—and the prices themselves—quickly returned.」に
ついて、既存Stage1出力を再利用しStage2のみ3回実行した結果、**3/3が
BLOCKING**(`llm_materiality`3/3ともBLOCKING、`floor_reason`3/3とも
`deterministic_floor:changed_time`、費用¥0.3096)。floor起因ではあるが
LLM自身も独立に3/3でBLOCKINGと判定しており、iteration4/5(QUALITY)との
非決定性は本測定では再現しなかった(n=3という小標本のため、より広い
非決定性が存在しない証明にはならない)。

Ledger HF-009原文の確認(`er019_output/family_x_entertainment_
production_runner_01/an3_t0_wiring_regression_01/hormuz/b1b/audit/
deviation_checks/advanced_attempt2.json`由来のfixture): 「Brent先物が
一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻った」
(価格は「戻った」と明記)、conditions:「撤回発表以外にも、米・イラン間の
攻撃、海上封鎖、タンカー安全上の懸念が**継続していた**」。

**両論併記(決定しない、Fableへの判断材料)**:
- **QUALITY側の見方**: claim中の「the prices themselves...quickly
  returned」はLedgerの「戻った」と直接整合する(Ledger支持あり)。
  「the events driving oil prices ... quickly returned」の部分は、
  並置構文("X, and Y, quickly returned")の一般的な英語読解として
  「価格の背景にあった出来事(=材料そのもの)」を指すゆるい修飾句として
  読める余地があり、「確認済みFact同士を自然につなぐ解釈」の範囲内という
  見方も成立し得る。
- **BLOCKING側の見方**: 最も自然な統語解釈では、並置された2つの主語
  (events/prices)が同一動詞句(quickly returned)を共有し、**events
  (=攻撃・海上封鎖・タンカー安全懸念)自体が「戻った(終息した)」と
  明確に主張している**。Ledgerのconditionsは明示的に「継続していた」
  (=終息していない)と記録しており、これは時制/status(継続 vs 終息)の
  直接的な反転であり、スタイル上の曖昧さではなく事実の反転に該当する。
  `changed_time`は決定論floorのNG5項目の1つであり、n=3全てでLLM自身も
  独立に同意している。

**sample2の`unconfirmed_after_reverify`分析**: `instances_s2/
neg3_hormuz_prodrunner_b1b.json`のconfirm call(`recheck_confirm`)は
`overall_status: LEDGER_DEVIATION`・`all_prior_issues_resolved: true`・
`cite_or_release_released_count: 0`を返した。これは「元のBLOCKING claim
(HF-009)自体はRewrite後に解消したとconfirm callが判定した」が「confirm
call自身が記事全文を再チェックした結果、**別の**逸脱を検出した」ことを
意味する(`en_ok`判定は`overall_status==LEDGER_COMPLIANT`も要求するため、
別逸脱の存在だけでSTAGE4へ回る、fail-closedとして正しい動作)。生の
`prior_issues_resolved`/`deviations`配列自体はinstance jsonに保存されて
いないため、検出された「別の逸脱」の内容そのものは本委任では特定できて
いない(再実行すれば特定できるが追加課金が必要なため見送った)。
**この事例は局所QA統合では解消しない**: 局所QAは対象文±1文の
windowしか見ないため、「元の対象claimとは別の、記事全体のどこかにある
逸脱」を発見する手段を構造的に持たない。むしろこの事例は、全文Recheck
(および今回のconfirm call)が持つ「記事全体を見る」という価値を裏付ける
追加のEvidenceである。

### 6-7. JA fail-open封鎖(委任_20 W1、Opus L2レビュー#4 §0是正)

**背景(発見された事故)**: Opus L2レビュー#4(`docs/pm/
opus_l2_review_open233_self_recovery_04.md`)が、rep10
`hormuz_run03_standard` sample1 cycle2で、paired J-1の段落Rewriteが
「指摘されたBLOCKING claimのJA文を一字も変えず、別段落の無関係なJA文
(+2.6%/$85の記述)を削除」し、`ja_recheck_overall_status:
LEDGER_DEVIATION`・`ja_en_equivalence_verdict: FAIL`だったにも関わらず
`RESOLVED_REWRITE_THEN_DOWNGRADE`(false PASS)として完了していた実例を
発見した。原因は本runnerのcycle継ぎ目のfail-open: 未解消時に次cycleの
`stage1_deviations`をEN側`recheck_parsed`のみから再構築しており、
JA側`ja_recheck_parsed`のMAJOR deviationsが構造的に握り潰されていた
(`ja_en_equivalence_verdict`もflow制御に使われず測定専用だった)。

**是正(3点、いずれも¥0・追加API callなし)**:
- **(i) JA recheck deviationsの合流**: 未解消cycleの次cycle再構築時に、
  EN側`recheck_parsed`のMAJOR deviationsへJA側`ja_recheck_parsed`の
  MAJOR deviationsを(同一fact_idの重複を避けつつ、`origin="ja_source"`
  を明示して)合流させる。さらに`ja_pending_deviation`フラグ
  (このinstance内でJA未解消のまま持ち越されているかを保持)を新設し、
  `not blocking_claims`によるdowngrade経路(`RESOLVED_STAGE2_DOWNGRADE`/
  `RESOLVED_REWRITE_THEN_DOWNGRADE`)へ入る際、このフラグがTrueなら
  無条件で`STAGE4_ESCALATION`(`stage4_reason="ja_deviation_unresolved"`)
  へ強制する(合流してもStage2が再度非BLOCKINGへ倒す等でblocking_claims
  が空になるケースへの二重の安全網)。`ja_pending_deviation`は、このcycle
  でJA recheckを実行していない(`ja_recheck_parsed is None`)場合は
  前cycle以前の値を保持する(「今cycleは検査していない」を「解消した」と
  誤読しない)。
- **(ii) ja_en_equivalence_verdictのgating化**: 従来「測定専用」だった
  `ja_en_equivalence_verdict`を、`PASS`以外(`FAIL`/`REVIEW_REQUIRED`)なら
  `ja_ok`をFalseへ倒すgatingへ昇格した。rep10の唯一のFAILが実際のJA破損
  と一致した実測(Opus L2レビュー#4)を踏まえる。
- **(iii) ¥0決定論JA fail-openガード**(`ja_fail_open_guard`関数、新設):
  paired rewriteでJA本文が変化したcycleについて、(a)指摘BLOCKING claim
  の`rewrite_hint`から抽出したJA引用文(`extract_quoted_fragment_
  present_in`、新設ヘルパー。既存`extract_quoted_fragment`は最長一致を
  返すため、rewrite_hintが「元の文」と「置換後の文」の2つの引用を含み
  後者の方が長い場合に誤って置換後の文を返す既知の曖昧性があり[rep10
  hormuz実データで実際に発生]、本ヘルパーはJA本文[Rewrite前]に実在する
  候補を優先することでこれを避ける)が、Rewrite後も逐語で残っていないか、
  (b)そのJA文を含む段落ブロック(既存`locate_paragraph_block`を再利用)の
  外側にあった他のJA文が理由なく消えていないか、を機械的に判定する。
  違反時は(1)局所QA fastpathを無条件で不可とし全文Recheckへ回す
  (`full_recheck_required`のreasonへ`ja_fail_open_guard_violation`を
  追加)、(2)全文Recheックが「解消」を返した場合でも`ja_ok`をFalseへ
  上書きする、の2箇所でgatingする。unittest(`er052_open233_self_
  recovery_flow_runner_01_test_01.py`の`TestJaFailOpenGuard`)は、
  rep10 `hormuz_run03_standard` sample1 cycle2の実データ(`summary_
  rep10.json` L1091-1092のja_text_before/after、L939のrewrite_hint)を
  fixtureとして転記し、本ガードが(a)(b)双方の違反を実際に捕捉することを
  確認している。

**rep11実測での検証**: 本節はコードレビューのみでなく、W4の
rep11実行で`ja_fail_open_guard_violation`が実際に発火し
`ja_deviation_unresolved`によるSTAGE4_ESCALATIONへ正しく到達した実例
(`bgroup_B3` sample1)を確認した(詳細はREPORT§20参照)。

**委任_21 A-1是正(rep11で判明したKPI後退の是正)**: rep11実測は同時に、
`bgroup_B3`(2/2 sample)が本ガードにより**誤って**STAGE4へ回っていた
ことも明らかにした。原因は`ja_fail_open_guard`が無条件で
`split_ja_sentences`(句点。！？のみで分割)を使っていたため、`bgroup_
B3`の`source_article_text`(fixture上は「JA」フィールドだが実際の中身は
英語)で句点分割が機能せず、全文が1文として扱われ、些細な1文変更でも
「本文の残り全部が消失した」という粗い誤検知を生んでいたことだった
(委任_16〜_19時点ではこの経路自体が無かったため、W1導入[委任_20]で
新たに露呈した回帰)。是正として、`is_predominantly_ja`(新設、¥0・
決定論、ひらがな/カタカナ/漢字比率[閾値15%]でJA/非JAを判定)を追加し、
`ja_fail_open_guard`がJA主体なら`split_ja_sentences`、非JA主体(英語等)
なら既存EN分割器`split_sentences_generic`(.!?を含む)を使うよう切替
えた。いずれの分割器でも1文以下にしか分割できない場合(句読点が実質
存在しない等)は`indeterminate=True`を返し、違反判定を行わない(ok=
True、ガード不発火)が、呼び出し側(`run_instance`)はこれを理由に
局所QA fastpathを許さず全文Recheckへ倒す(`ja_fail_open_guard_
indeterminate`理由を追加、STAGE4への直行にはしない、安全側だが
過剰diagnosisにはしない設計)。

**rep11実データによるunittest(`TestJaFailOpenGuardLanguageAware`、
3件)**: `bgroup_B3`のja_text_before_rewrite/after(cycle1、`so`→
`while`の1語変更のみ)とrewrite_hintを逐語転記し、是正後は誤検知
(violations)が0件になることを確認。既存`TestJaFailOpenGuard`(rep10
hormuz実データ、真のJA)は既存のまま全PASSを維持し、言語判定を挟んでも
真のJA fail-open検出能力に regression がないことを確認した(202/202
tests PASS、既存196件+新規6件)。

**rep12実測での検証**: 本是正後、`bgroup_B3`をn=2で再実行したところ、
`ja_fail_open_guard`は2/2とも`{"ok": true, "violations": [], "checked":
true, "indeterminate": false}`となり誤検知が解消したことを確認した。
ただし`bgroup_B3`は2/2ともSTAGE4_ESCALATIONへ到達しており、これは
本ガードとは別の既存・正当な機構(§6-9(h)、`ja_en_equivalence_verdict
= REVIEW_REQUIRED`によるgating、W1(ii))が働いた結果であり、fail-closed
としては正しい挙動である(詳細REPORT§21)。

### 6-8. Stage 1同一fact_id列挙(委任_20 W2、Opus L2レビュー#4 Q1(c)推奨)

**背景**: Opus L2レビュー#4は、rep9/rep10で全文Recheckが実際に価値を
発揮した最後の実例(`hormuz_run03_standard`のcycle3、見出し/one-line要約
のHF-009問題)について、「1文の局所Rewriteが新しい問題を作った」のでは
なく「Stage 1初回(全文)が、同一fact_id(HF-009)の記事内の別箇所[見出し/
one-line]を列挙し損ねたrecall不足」であると特定した(headline/one-line
はRewrite前から一貫して存在する原文であり、Rewriteが作ったものではない
ことを`summary_rep10.json`のcycle1 `en_text_before_rewrite`で確認済み)。
全文Recheckが後から拾えていたのは「全文を毎回見ているから」ではなく
「`prior_issues`により同一fact_idを記事全体で探すようprimingされて
いたから」であり、その機能はStage 1初回へ、追加callなしで移せる。

**実装(¥0限界コスト、追加callなし)**: Stage 1初回(`stage1_fresh_with_
enumeration`、新設)・Recheck(`run_recheck`、既存関数を拡張)双方の
出力schemaへ`same_fact_id_locations`(文字列配列)フィールドを追加し、
プロンプトへ「各deviationについて、title/hook/in-one-lineを含む記事内の
他箇所で同じfactを主張している箇所があれば逐語で列挙する」指示
(`SAME_FACT_ID_ENUMERATION_INSTRUCTION`)を追記した。schema拡張は
本runner内のローカル関数(`build_deviation_schema_with_enumeration`)で
行い、`er051_open233_checker_trial_variant_01`(他のOPEN-233-CHECKER-
REDESIGN-TRIAL-01系スクリプトとも共有される既存モジュール)自体は
変更しない。応答後、`expand_same_fact_id_locations`(新設、¥0・決定論)が
各locationを記事本文中の逐語substringとして実在確認できたものだけを
独立の追加deviationへ展開する(fail-closed、幻覚を弾く)。展開後の複数
claimは、既存の`_run_stage3_cycle`(1 cycle内で各claimを独立にladder①
から試す既存機構、委任_18)がそのまま処理する(新しいRewrite機構は
作らない)。

**reuse fixtureへの安全側fallback**: `stage1_mode=reuse`のinstance
(29 instance中26/29)は既存json(`same_fact_id_locations`フィールドを
持たない)をそのまま読み込むため、`expand_same_fact_id_locations`は
`.get("same_fact_id_locations")`がNoneであれば何も追加せず、既存動作を
変えない。

**既知の副作用(Opus L2レビュー#4 Q1(c)で事前に指摘済み)**: Stage 1で
複数箇所を列挙すると、cycle1のclaim数が増え、既存条件(b)
`multiple_claims_rewritten_same_cycle`が発火して結局全文Recheckに戻る
ケースが生じ得る(欠陥ではなくリスク比例の正しい形だが、「列挙を入れれば
fastpath発火率が単純に上がる」という期待は成立しない)。

### 6-9. 全文Recheckを残す条件の更新(委任_20 W3、Opus L2レビュー#4 Q1(b)推奨)

**前提**: 本節の変更は§6-7(W1)のJA fail-openガード/equivalence gatingが
既に導入済みであることを前提とする(順序を逆にしない、Opus L2レビュー#4
Q1推奨4「先にJA fail-openを塞ぎ、その後にのみ(c)を縮小する」)。

- **(c)縮小**: 「paired」блanket維持から、「paired かつ(ladder≥④[段落/
  全体/削除] or JAガード[§6-7(iii)]不通過)」へ縮小した
  (`full_recheck_required`関数、`ja_guard_ok`引数)。(a)が既にrewrite_
  records全件[paired含む]についてladder≥④を判定しているため、狭めた
  (c)が追加で捕捉するのは「paired・ladder①〜③(低水準)・かつJAガード
  不通過」の場合のみ。
- **(b)は維持(実証例なしと明記)**: `multiple_claims_rewritten_same_
  cycle`は単独の実証例が無い(disclosure §1-4-5の`meta_run03_standard`
  sample2は(d)floorでも捕捉される)が、削除の実証的根拠がないため保守側
  で維持する。
- **(e)にTrial限定の但し書きを追加**: `instance_id.startswith("safety_")`
  はTrial fixtureの命名規約に依存する条件であり、Production記事には
  該当する信号が存在しない。Production配線を検討する段階になったら
  「Ledger factがSafety-critical指定」等の実信号へ置換が必須であり、
  現状のTrial実測数字はProductionへ外挿できない。
- **(g)新設**: 対象claimの`section_type`が`title`/`hook`/`in_one_line`
  (`HOOK_SECTION_TYPES`)の場合、前後1文の概念が成立しない(1文で1
  セクション、または前後文が存在しない)ため、全文Recheckを維持する。
  省略時に取りこぼす実例: `neg3_hormuz_prodrunner_b1b`(section_type
  `in_one_line`)、`safety_er009_unsupported_new_claim`(title全体が1文、
  削除で空文字化、disclosure §1-1-4)。
- **(h)新設**: `ja_en_equivalence_verdict`が`PASS`以外の場合、全文
  Recheckを維持する(§6-7(ii)のgating化と対になる条件、rep10の唯一の
  FAILが実際のJA破損と一致した実測を踏まえる)。
- **局所QA(Ledger局所突合)の呼称統一**: OPEN-233の局所QA
  (`run_local_qa_fastpath`)はweb_searchを含まないLedger突合1 callで
  あり、Production側`er010_ledger_local_rewrite_09.run_diff_qa_for_
  accepted_rewrite`(Fact Checker A'、web_search込み)とは守備範囲が
  異なる(Opus L2レビュー#4「追加で気づいた重大点5」)。本書・REPORTでは
  以後「Ledger局所突合(web_searchなし、Production A'差分QAと同等では
  ない)」と表記を統一する。

**rep11実測**: REPORT§20参照(rep9/rep10と同様、§9-1の①〜⑬連番
リストへは追加せず、本節[§6-7〜§6-9]とREPORTの専用節で記録する、
§9-1⑬以降の既存踏襲)。

### 6-10. 局所QA fastpath locateバグの是正(委任_21 A-2)

**背景(rep11実データで判明した真因)**: rep9(委任_16)以降、局所QA
fastpathは代表ケースTrialで繰り返し発火0件、またはlocateバグにより
API call前にskipし続けており(rep9〜rep11のREPORTで継続報告)、根本
原因が特定できていなかった。委任_21で`meta_run03_standard` sample1
cycle1の実データ(claim=MUSE-HC-010)を精査した結果、真因は
`find_sentence_context`(needle=`after_fragment`)側にあった: `locate_
target`の第一キー(`extract_quoted_fragment`によるrewrite_hint中の
引用断片)がそもそも複数文にまたがっていた場合(実例のrewrite_hintの
引用が「Also, some calls needed user information to continue. That
information might accidentally be shared...」の2文)、E1(1語・接続詞
水準)のRewrite後もこの2文が`target_sentence`=`after_fragment`として
維持される。一方`find_sentence_context`は`split_sentences_generic`が
返す**単一文**の要素それぞれに対してしか`needle_s in s`および
SequenceMatcher(閾値0.85)を試みていなかったため、2文分の長さを持つ
needleはどの単一文とも一致せず、`revised_sentence_not_locatable_in_
context`で毎回skipしていた。

**是正(¥0、追加API callなし)**: needle自体を同じ分割器
(`split_sentences_generic`)で分割した文数kを求め、k>1の場合は連続する
k文の結合ウィンドウ(`" ".join(sentences[i:i+k])`)に対してexact
containment→SequenceMatcher(既存と同じ閾値0.85)の順で追加照合する
処理を`find_sentence_context`へ追加した。k=1(単一文needle)の既存経路は
変更しない(regressionなし)。

**rep11実データによるunittest(`TestFindSentenceContextMultiSentenceNeedle`、
3件)**: `meta_run03_standard` sample1 cycle1のen_text_after_rewrite全文と
2文needleを逐語転記し、是正後は正しくlocateされ、before/after context
(隣接文)も正確に返ることを確認した。既存の単一文needle経路・
一致しないneedleでNoneを返す経路のregressionテストも追加した
(202/202 tests PASS)。

**rep12実測での検証**: `meta_run03_standard`をn=2で再実行したところ、
2/2とも局所QA fastpathが**実際にAPI callへ到達し成功**した
(`local_qa_fastpath_success: true`、`skipped_reason`なし)。これは
OPEN-233 Self-Recovery Flow Trial全体(委任_09〜_21、rep7〜rep12)を
通じて**初めて**局所QA fastpathが実call成功により全文Recheckの省略に
至った実例である(詳細REPORT§21)。

### 6-11. JA/EN等価チェックgatingの言語判定是正(委任_22 A-1)

**背景(rep12実データで判明したKPI後退)**: 委任_20 W1(ii)は「`ja_en_
equivalence_verdict`がFAIL/REVIEW_REQUIREDならja_okを無条件でFalseへ
倒す」方式だった(§6-7参照)。`bgroup_B3`のfixtureは`source_article_
text`(「JA」側)が実際には英語であり(§6-7で`ja_fail_open_guard`について
特定したのと同じ構造的限界)、JA↔EN等価チェック自体が両者を比較できず
`REVIEW_REQUIRED`を返す。rep12実測では、実際の全文Recheckは英語版・JA
版とも`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=True`(=ja_ok
本来True)だったにも関わらず、無条件gatingがja_okを強制Falseへ倒し続けた
結果、次cycleでblocking_count=0(新規逸脱なし)でも`ja_pending_
deviation`が解消されず`STAGE4_ESCALATION(ja_deviation_unresolved)`へ
2/2到達していた(REPORT§21-5(i))。

**是正(¥0、決定論)**: 新設した`resolve_ja_ok_after_equivalence_gating`
(既存の巨大なインライン処理を純粋関数として抽出、`er052_open233_self_
recovery_flow_runner_01.py`)で、gating方式を次のとおり整理した。

- `verdict == "FAIL"`(等価チェックが実際に不一致を検出した場合): 従来
  どおりja_okをFalseへ倒す(次段のRewriteへ、最終的にSTAGE4)。JA側言語
  判定は行わない(FAILは言語判定に関わらず信頼する)。
- `verdict == "REVIEW_REQUIRED"`かつ`is_predominantly_ja`で判定した
  現在のJA側テキストが非JA(indeterminate、等価チェック自体が判定不能):
  ja_okを強制せず、全文Recheckの実際の判定(`ja_recheck_parsed`由来の
  ja_ok)をそのまま使う(STAGE4直行を強制しない)。全文Recheck自体は
  `full_recheck_required`の(h)条件(無変更)により既に維持されている
  ため、局所QA fastpathへ抜けることはなく安全側は保たれる。
- `verdict == "REVIEW_REQUIRED"`かつJA側言語が正常(判定可能): 従来
  どおりgatingする(理由`ja_ok_blocked_by_equivalence`を記録)。

**unittest**: `TestResolveJaOkAfterEquivalenceGating`(6件)。rep12
`bgroup_B3`実データ(`ja_text_after_rewrite`、既存`REP11_B3_SOURCE_
ARTICLE_TEXT_AFTER`定数と逐語一致)を使い、is_predominantly_ja=False
(indeterminate)の場合にja_okがFalseへ倒されないことを確認、rep10
hormuz実データ(真のJA)でREVIEW_REQUIREDが従来どおりgatingすることを
regression確認、FAILは言語判定に関わらず常にja_okをFalseへ倒すことを
確認した。既存202件+新規6件=**計208件全PASS**。

**rep13実測での検証**(REPORT§22-1参照): `bgroup_B3`のみをn=2で2回
実行(計4 instance-run、¥0.9448)。1回目(Stage2非決定性でmateriality=
QUALITY、blocking_count=0)は2/2とも`RESOLVED_STAGE2_DOWNGRADE`。2回目
(Stage2がHF-007をBLOCKINGと判定)は2/2とも`verdict=REVIEW_REQUIRED`・
`lang_indeterminate=True`・`not_gated_indeterminate_lang=True`となり、
全文Recheck(EN/JA双方`LEDGER_COMPLIANT`)の実際の判定がそのまま採用され
`RESOLVED_REWRITE`(ladder_level_used=`1_word_connective`、最小変更を
維持)で完了した。**4/4 instance-run全てSTAGE4に至らず**(rep12の2/2
STAGE4から改善)、false PASSでもない(実際のRecheckが真に解消を確認した
場合のみ通過させる設計どおり)。

### 6-12. `hormuz_run03_standard` real_run Escalation真因是正(委任_23 A-2、
REPORT§23 A)

**背景(iter7で残った未達1)**: iteration7(委任_22)はreal_run Escalation
2/10(`hormuz_run03_standard` n=2とも)がKPI目標(0)未達のまま残った。

**真因A(§6-11の残存過剰保守、iter7 sample1型)**: `hormuz_run03_standard`
instances_s1(iter7)のcycle0は、BLOCKING claim(HF-009、body)を①(単語・
接続詞)水準で解消し、全文Recheck(EN/JA双方)が`LEDGER_COMPLIANT`かつ
`all_prior_issues_resolved=True`と**既に確認済み**だったにも関わらず、
`ja_en_equivalence_verdict=REVIEW_REQUIRED`(JA側言語は`is_predominantly_
ja`判定で正常[determinate])のみを根拠に§6-11のgatingが`ja_ok`を
無条件でFalseへ倒し、`ja_pending_deviation`が残ってSTAGE4_ESCALATION
(`ja_deviation_unresolved`)へ強制到達していた。`ja_en_equivalence_
verdict`は元々(委任_11)「flow制御には使わない、測定・報告専用」と
明記されていたcheckであり、委任_20 W1(ii)が`FAIL`の実測(rep10、JA
破損と一致)を根拠にgatingへ昇格したが、rep10自体もja_recheck側が
独立に`LEDGER_DEVIATION`だったため(§6-7)、「`ja_ok`が既にTrueの状況で
この追加gatingが実際に真の見逃しを捕捉した実測」は一度も存在しない。

**是正A(¥0、`resolve_ja_ok_after_equivalence_gating`拡張)**:
`verdict=="REVIEW_REQUIRED"`かつJA側言語が正常でも、`ja_ok`(入力、
全文Recheckの確定判定)が既にTrueの場合はgatingしない(信頼できる
独立確認[EN/JA双方のLedger Recheck]を弱い根拠[equivalence REVIEW_
REQUIRED]で上書きしない)。`ja_ok`が既にFalseの場合は元々no-opであり
挙動は変わらない。`FAIL`分岐は変更しない(rep10実測の唯一の根拠が
FAILであり安全側を維持)。JA fail-openガード(§6-7(iii)、本関数とは
独立に適用)は無変更のまま機能し続けるため、rep10型の実際のJA破損は
引き続き検出される(実測で価値が一度も確認されなかった層のみを縮小)。
詳細は`resolve_ja_ok_after_equivalence_gating`のdocstring参照。

**真因B(reuse fixtureのsame_fact_id列挙欠如、iter7 sample2型)**:
`hormuz_run03_standard`は`stage1_mode=reuse`(§6-8「reuse fixtureへの
安全側fallback」対象、29 instance中26/29)であり、Stage1初回json(`er051_
output/open233_checker_trial_01/trial_02/step3/hormuz_run03_standard/
V4A/run_1.json`)は委任_20 W2で新設した`same_fact_id_locations`
フィールドを持たない。そのためcycle0のStage1初回はbody側claim(HF-009)
しか検出できず、in_one_line側の同一fact言及はcycle1の全文Recheck
(fresh LLM call、列挙可)まで発見されない。body/in_one_line2箇所を2
cycleに分けて処理する形になり、HARD_MAX_CYCLES(3)を消費し尽くした後も
解消しないままSTAGE4_ESCALATIONに至っていた(iter7 instances_s2)。

**是正B(¥0、`deterministic_same_fact_id_location_fallback`新設)**:
reuse fixtureのdeviationについて、`claim_in_article`中の数値・金額・%
トークン(1件でも一致)、またはstopword除外後の非stopword単語重複
(閾値3件以上、hormuz_run03_standard実データで較正・REPORT§23 A参照)を
手掛かりに、記事内の他文(`split_sentences_generic`、見出し行除外は
既知の限界)を候補化し、既存`expand_same_fact_id_locations`(fail-closed、
逐語実在確認)へ渡してcycle0の時点で独立claimへ展開する(新しいRewrite
機構は作らない、委任_20 W2の枠組みをreuse fixtureへも拡張)。過剰候補化
(閾値が低すぎる場合)はStage2(独立LLM materiality判定)がACCEPTABLEで
screenするため安全側(コスト増のみ、Safety regressionではない)。

**unittest**: `TestResolveJaOkAfterEquivalenceGating`(既存6件の一部更新
+新規2件)、`TestDeterministicSameFactIdLocationFallback`(新規5件)、
`TestLadderExhaustedWithoutFullRewriteWiring`関連(後述§5-10)。既存
208件のうち2件を新挙動へ更新+新規10件=**計218件全PASS**。

**rep14実測(REPORT§23 D参照、`hormuz_run03_standard`×n=2、¥3.8461)**:
是正A・Bとも実際に発火することを確認した(sample2でgating実際に
`ja_equivalence_review_required_not_gated_already_confirmed_resolved=
True`が記録され、両sampleともcycle0でbody+in_one_line2claimを同時に
検出・Rewrite)。**しかし2/2ともSTAGE4_ESCALATIONは解消しなかった**
(stage4_reasonが`ja_deviation_unresolved`から`same_claim_fact_id_
reblocked`へ変化)。cycle1の全文Recheckがbody claimを①水準Rewrite後も
なお同一claim本文に近い形でBLOCKINGと再検出し(`find_matching_prior_
record`の近似一致閾値0.75以上)、§3-3の「同一claim再発=Rewriteが
効かなかったことの実証」という既存の安全網が正しく発火した。**正直な
結論**: 真因A・Bはいずれも実際に存在し、是正も実際に機能した(A-1は
gatingの過剰保守を解消、A-2はreuse enumeration欠如を解消)ことをrep14
実測で確認したが、`hormuz_run03_standard`のEscalationは**別の第三の
限界**(word-level[①]のみのRewriteでは当該body claimの実質的な問題を
解消しきれない、Stage3 Rewrite品質の限界)により残存している。これは
本委任のA-2で診断対象とした三択(a/b/c)のいずれにも完全には一致しない
新規の発見であり、budget制約(委任文Guardrail¥6、rep14実測後残¥0.6455)
のため本委任内でのさらなる追加修正・再実行は行わない(STOP条件
「¥6超え見込み」「最小修正1回後もFAIL」に該当、Fable/ユーザー判断待ち
として次回委任へ持ち越す)。

### 6-13. ラダー前進と§3-3安全網の判定順序是正(委任_24 A-2、REPORT§24)

**背景(rep14で判明した第三要因の再解釈)**: §6-12の是正A・Bを反映したrep14実測で、`hormuz_run03_standard`は是正A・Bとも実際に発火したにもかかわらず2/2ともSTAGE4_ESCALATIONのまま残り、理由が`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`へ変化した(「word-level[①]のみのRewriteでは当該claimの実質的問題を解消しきれないというStage3 Rewrite品質の限界」と報告していた)。本委任でrep14の実cycle記録(call_log)を精査した結果、これはRewrite品質の限界ではなく、**§3-3安全網(`matched_records`判定)が§6-6 A-2のラダー前進機構(`escalate_to_paragraph`)より先に評価される実装順序の問題**だったと判明した。①水準Rewrite後のcycle2全文Recheckが同一claimを近似一致(閾値0.75)で再検出した時点で、④段落水準のRewriteが一度も試されないまま`same_claim_fact_id_reblocked`でSTAGE4へ直行していた。

**是正(¥0)**: `run_instance`のcycle>1時の`matched_records`判定を、一致した`prior_blocking_records`エントリが持つ`escalated_to_paragraph`(そのRewrite試行時に④段落水準を使ったか)で二分岐させた。
- **exhausted_matched_records**(既に④段落水準まで試行済みで再発): 従来どおり直ちに`stage4_reason="same_claim_fact_id_reblocked"`(「ラダーを昇段しきった上での再発」という意味へ変更)。
- **escalatable_matched_records**(まだ①・③水準までしか試していない再発): STAGE4にせず、該当claimへ`escalate_to_paragraph=True`を明示的に付与してループを継続する(既存の§6-6 A-2機構[fact_id再出現時に④段落水準から試す]へ合流、新しい機構は作らない。fact_idが一致していれば既存の`repeat_fact_ids_for_recheck`でも同じフラグが立つが、fact_id欠落claim[hashベースidentity]を取りこぼさないためidentity単位でも明示的に設定する)。

`prior_blocking_records`の各エントリへ`escalated_to_paragraph`フィールドを追加し、`find_matching_prior_record`はそのclaim identityについて**直近(最後に追記された)一致レコードを優先して返す**よう走査順を`reversed(prior_records)`へ変更した(旧来の先頭[最も古い]一致優先では、同一fact_idが複数cycleにまたがる場合に最新の試行状態[`escalated_to_paragraph`]を正しく参照できなかった)。cycle上限(`MAX_CYCLES`/`HARD_MAX_CYCLES`)・JA fail-open封鎖(§6-7)・等価FAIL gating(§6-11、`FAIL`分岐は委任_23でも無変更)・Safety floor-strictは無変更。

**設計判断の開示**: 委任文は「次のラダー段(②→③→④)へ」と表現していたが、②(文の一部)はコード上の独立水準として存在せず(§5-7で既に①へ統合済み)、既存の§6-6 A-2機構は①・③を両方スキップして④へ直接進む設計(rep10実測で解消実績あり)である。本委任は新しい「1段ずつ昇段する」機構を新設せず、既存のこの直接④ジャンプ機構へ合流させる最小変更を選んだ(最小変更・既存機構再利用の原則に従う判断だが、委任文の字面とは完全には一致しないため明示的に報告する)。

**rep15実測(`hormuz_run03_standard`×n=2、sample1完走・sample2はGuardrail到達でTrialAbort、詳細REPORT§24-3)**: sample1は`stage4_reason`が`same_claim_fact_id_reblocked`から**発生しなくなり**(premature短絡が解消)、cycle1で①・③水準、cycle2で④段落水準(fact_id再出現によるescalate_to_paragraph)へ正しく昇段し、EN/JA双方のLedger Recheckが「解消」を確認した。しかしcycle2で`ja_en_equivalence_verdict=FAIL`(委任_23で意図的に無変更のまま維持したhard gate)が記録されたため、最終的に`ja_deviation_unresolved`でSTAGE4_ESCALATIONへ至った(false PASSではない、別の既存fail-closed機構が正しく発火した結果)。**正直なコスト報告**: sample1は¥4.0578(19 call)で、rep14の同fixture(¥1.87〜1.98、9 call、早期打ち切り)の**約2.1倍**のコストとなった。これは是正が意図どおり追加cycleを許した結果でありバグではないが、同種パターンを持つ他instanceでも同程度のコスト増が見込まれることをFable/ユーザーへ開示する(rep15が¥7 Guardrailに到達し`bgroup_B4`・`safety_A2A3`が未実施に終わった直接原因)。

**unittest**: `TestFindMatchingPriorRecord.test_multiple_prior_records_same_fact_id_returns_most_recent`(新規1件)、`TestSameClaimReblockedLadderEscalationWiring`(新規3件、source inspection)。既存218件+新規4件=**計222件全PASS**。

### 6-14. `meta_run03_standard`人間確認率悪化の原因三択確定(委任_33、REPORT§31)

**背景**: 委任_32(iter8)で`meta_run03_standard`が2/2ともSTAGE4に到達し
(iter7のStage1 reuseでは0/4だった)、実記事6種10 runの人間確認率が
0%→20%へ悪化した(§7-0-iter32は別claimのSafety-critical誤降格、本節は
この実記事固有の悪化の原因分析)。委任文§1で提示した三択は、(a)
`escalate_to_paragraph`廃止により多箇所反復がcycle上限内に収まらない、
(b)Stage1 fresh検出の非決定性、(c)当該claim自体がdisclosure-gap型で
BLOCKINGにすべきでない、の3つ。

**iter8実データの再分析(¥0、既存`er052_output/open233_self_recovery_
flow_runner_01_iter8/instances_s{1,2}/meta_run03_standard.json`の
cycle別`stage2_results`を精査)**: cycle0〜2で繰り返しBLOCKINGのまま
残ったのは一貫して`related_fact_id=MUSE-HC-011`(floor_reason=
`deterministic_floor:changed_number`、Ledgerが複数件の契約社員からの
報告と記録している事実を、記事が「one employee's report」のように
単数化して繰り返し言及している)で、cycle0の3箇所→cycle1の5箇所→
cycle2の6箇所と**出現数が増加**した。一方、同一cycle内の複数箇所は
`blocking_claims`ループ(`for c in blocking_claims:`、line付近3973)で
独立に処理されており、委任_18の複数箇所独立ladder機構自体は正しく
機能していた(各箇所が個別に①水準Rewriteを試行、の意味で(a)の
「仕組みが壊れている」は不成立)。

**(c)の判定**: MUSE-HC-011は「Ledgerが複数件と記録する事実を記事が
単数へ歪曲する」という**数値・規模の歪曲**であり、§0-2のBLOCK候補
(「未確認の人物・行動・動機・具体的な数字の追加」寄りの事例)に明確に
該当する。disclosure-gap型(§6-?既存の`apply_disclosure_gap_downgrade`
対象、MUSE-HC-012「開示なし」パターン)とは性質が異なり、重大誤解原則の
下でもBLOCKING維持が正しい。**(c)は不成立**(rubric修正は不要、
実装していない)。

**rep18実測による(a)/(b)の決着(`er052_open233_self_recovery_flow_
runner_01_rep18_representative_01.py`、§4-25参照)**: iter8と全く同じ
fixture・既定構成で`meta_run03_standard`をStage1 fresh・n=2で再実行した
ところ、**2/2ともACCEPTABLE_STAGE1**(claim検出0件)となり、iter8の
「2/2ともSTAGE4(cycle0だけで6claim検出)」から**劇的に異なる結果**に
変化した。同一fixture・同一rubric・同一コードでここまで結果が変わる
ことは、「①で検出した箇所を②③④へ反復して昇段しきれない」という
cycle機構の不備((a))では説明できず、**Stage1 fresh(V4A+重大誤解原則)
のclaim検出(enumeration)自体が強い非決定性を持つ((b))**ことの
直接証拠である。

**結論・対応(委任_33時点)**: 原因は(b)(Stage1 fresh enumeration非
決定性)。(a)の機構自体(複数箇所独立ladder)は正しく機能しており修正
不要、(c)も不成立のためrubric修正は不要。Stage1検出の非決定性
そのものの改善(例: temperature/サンプリング設定の見直し、複数回Stage1
呼び出しによるunion screen[S1-U、既存§3-1機構]の既定化等)は根本設計
変更に該当するため、本委任ではコード変更を行わず、既知の残存リスク
としてFable/ユーザー判断へ委ねる(§7 STOP条件「cycle上限の単純拡大や
段落直行の復活はしない」に従い、その種の回避策も実装していない)。
**委任_34で(b)単独では説明できない追加メカニズム(d)が判明したため、
下記§6-15で結論を補強・修正する。**

### 6-15. `meta_run03_standard`、Stage1入力固定後も残る追加原因(d)の特定(委任_34、REPORT§32)

**背景**: Stage1自体の揺れ(cycle1検出内容がrunごとに変わること)は
Self-Recovery Flowの責任範囲外だが、「出たものを人間確認なしに正しく
処理できるか」は責任範囲内という整理のもと、iter8のcycle1 Stage1出力
(s1/s2で完全同一、`stage1_cache`共有[fresh instanceの仕様どおり]を
実測で確認済み)を`stage1_mode=reuse`で固定し、現行既定構成(V6・
actorガード常時評価・局所QA・JA fail-open封鎖・escalate_to_paragraph
OFF・⑥OFF)でそのまま再実行した(frozen fixture:
`er052_output/open233_self_recovery_flow_runner_01_rep19/
stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、
`er052_open233_self_recovery_flow_runner_01_rep19_representative_
01.py`新設、OUT_DIR_REP19新設)。

**結果**: sample1は3cycle完走後も`STAGE4_ESCALATION`
(`stage4_reason=cycle_limit_exhausted_after_recheck`、¥6.2845)。
sample2はcycle1完了後、Guardrail到達(累計¥7.2614/¥8)で安全側に
自己停止(`TrialAbort`、¥0.9769消費、結果は未保存)。cycle1の入力を
iter8と完全固定したにもかかわらず再びSTAGE4へ到達したことは、
§6-14の「原因は(b)のみ」という結論では説明できない。

**追加メカニズム(d)**: `deterministic_floor:changed_number`/
`deterministic_floor:changed_actor`は、違反を体現する当該claim文
だけでなく、同一`related_fact_id`を共有する**他の全claim**(`llm_
materiality`が独立にACCEPTABLE/QUALITYと判定していても)へBLOCKING
判定を強制的に波及させる。`same_fact_id_locations`enumeration
(委任_20 W2)がRewrite後のテキストから毎cycle新しい候補文を再列挙
し続けることと複合し、cycle1の2claim→cycle2の12claim(blocking6+
non_blocking6)→cycle3の5claim(全てBLOCKING、non_blocking0)と
検出対象が増加し続け、cycle上限(`MAX_CYCLES=2`+`extra_cycle_granted`
延長で実質3)に達するまで収束しなかった(詳細逐語はREPORT§32)。

**(b)と(d)の関係**: (b)はiter8のs1/s2間の差異(cycle2以降の検出が
sampleごとに異なった事実)を説明しうるが、cycle1を完全固定しても
依然として収束しないという今回の事実は、(b)単独では説明できない。
(d)はdeterministic floorの波及範囲(fact_id単位)が広すぎることに
起因する、(b)とは独立した追加原因候補である。

**対応**: §6-14の結論を「(b)は少なくとも部分的要因」へ修正し、(d)
「deterministic floorのfact_id単位broadcast+same_fact_id_locations
enumerationの複合によるcycle内非収束」を既知の残存原因候補として
追加する。委任文の分類では(d)は「Stage2許容例示の適用範囲」(floor
自体の対象範囲を、違反を体現する当該claim文のみへ狭める)に近い
**小修正候補**だが、本委任はGuardrail¥8のうち¥7.2614を1run+aborted
1runで使い切ったため、修正の実装・再検証(見込み≤¥2)を行う予算が
なく、**未検証のままコード変更は行っていない**。(d)の是非確認は
追加予算(目安¥3程度)の承認をFable/ユーザーへ依頼する。

### 6-16. (d)の小修正実装とfrozen fixture再検証(委任_35、REPORT§33)

**修正内容(4点、いずれも小修正、Safety原則自体は変更しない)**:

1. **floorのfact_id単位broadcast廃止**: `apply_floor`/`apply_floor_cited`
   (`er052_open233_self_recovery_flow_runner_01.py`)が、`expand_same_
   fact_id_locations`(委任_20 W2)によって複製されたclaim(`dev.
   detected_by_enumeration=True`)に対しては、deterministic floorの
   強制BLOCKINGを適用しないよう変更した。違反を体現する当該claim文
   自体(`detected_by_enumeration`が立っていない、Stage1が直接flagを
   付与したclaim)は従来どおりfloorでBLOCKING維持(fail-closed不変)。
   複製claimはStage2 LLMの独立判定(`llm_materiality`)がそのまま
   `materiality`になる(floorが波及しなくなっても、複製claim自体が
   実際に違反していればLLMが独立にBLOCKINGと判定し、fail-closedは
   失われない)。
2. **same_fact_id_locations enumerationのcycle1限定**: `run_recheck`
   に`enable_fact_id_enumeration`引数(既定`False`)を追加し、Recheck
   呼び出し(cycle番号に関わらず、本関数は常に初回Stage1より後に呼ばれる)
   では`SAME_FACT_ID_ENUMERATION_INSTRUCTION`をprompt化せず、
   `expand_same_fact_id_locations`も呼ばない。初回Stage1検出
   (`stage1_fresh_with_enumeration`/reuse時の`deterministic_same_
   fact_id_location_fallback`経由)のみが列挙対象のまま(既存動作不変)。
3. **iol_degenerate guard追加**: `measure_section_role_violation`に
   `iol_degenerate`(「## In one line」見出し自体の削除・消失)を追加し、
   既存の`title_degenerate`/`hook_degenerate`と同じhard block条件
   (`run_instance`、`degenerate_rewrite_output`)へ合流させた。
4. **「別文へ丸ごと置換」個別是正の要否**: rep20実測(下記)で、修正1・2の
   効果により該当claim("They enjoyed AI's convenience...")がそもそも
   BLOCKINGへ至らなくなったため、`classify_problem_kind`自体の追加
   是正は不要と判断した(経過観察、根拠は下記rep20結果)。

**rep20実測(`er052_open233_self_recovery_flow_runner_01_rep20_
representative_01.py`、`OUT_DIR_REP20`新設、rep19と同一frozen fixture
を再利用)**:

| run | final_state | stage4_reason | cycle数 | 費用 | 備考 |
|---|---|---|---|---|---|
| sample1 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 3 | ¥2.0186 | cycle1の検出がfix後2→1件(複製4件が強制BLOCKINGから解放)。Rewriteは単語置換("calls"→"one call"等)。見出し保持。cycle2で新規claim("Some calls needed user information...")が直接LLM判定でBLOCKING、cycle3で解消 |
| sample2 | `STAGE4_ESCALATION` | `ladder_exhausted_without_full_rewrite` | 2 | ¥1.8301 | cycle1は同様に1件のみBLOCKING、単語置換で解消。cycle2の新規claim("They could not tell...")がladder上限(⑥OFF、全文Rewrite不使用)に達しfail-closedでSTAGE4(人間確認、安全側) |

rep19(修正前)の「cycle1: 2件原本→cycle2: 12件→cycle3: 5件」という
検出対象の増加は再現せず、両runともcycle1のblocking_claimsは1件
(違反を体現する当該claim文のみ)に収まった。「They enjoyed AI's
convenience...」は両runとも`disclosure_gap_negative_inference_
downgrade`でQUALITYのまま維持され、rep19で観測された「別文へ丸ごと
置換」も「## In one line」見出し削除も再発しなかった(修正3のiol_
degenerate guardは本rep20では未発火、guard自体は追加済み)。

**Safety対照(regression確認)**: (a) Safety12のうち`safety_er009_
changed_number`/`safety_er009_changed_actor`をfull flow n=1で実行し、
いずれも違反文自体がfloorでBLOCKING(`deterministic_floor:changed_
number`/`changed_actor`)→Rewrite→`RESOLVED_REWRITE`(floorが引き続き
正しく発火することを確認、誤って弱まっていない)。(b) `SAFETY_CRITICAL_
CLAIM_DEFS`登録の6 instance・8claimをStage1(reuse)+Stage2のみ(cycle=1
相当)で実行し、8claimのうちこの簡易harnessで検出できた6claim
(A2A3-0/A4-0/A4-1/A5-0/Meta-1/B4-a)は全てBLOCKING維持(0件downgrade)。
残り2claim(B3/Meta-2)は「この簡易harnessで検出できなかった」(B3は
既知のStage1 recall miss[`KNOWN_RECALL_MISS_INSTANCE_IDS`、§10/§14
既知の限界]、Meta-2はこのinstance用stage1_source[build_target_
instances()の`BGROUP_STAGE1_DIR`経由、rep19/rep20のfrozen fixtureとは
別物]の実データがSAFETY_CRITICAL_CLAIM_DEFSのMeta-2定義[fact_id+
文字列]と一致しない、いずれも本委任のfloor修正とは無関係な既存データ
特性)。**BLOCKINGから他状態へdowngradeした事例は0件**(「検出された
上でdowngradeされた」ケースはない)。

safety_critical_misdowngrade_rows(rep20 Part B側、`detect_safety_
critical_misdowngrades`による自動検知)も0件。false PASSは0件
(STAGE4_ESCALATION/RESOLVED_REWRITE_THEN_DOWNGRADEのみ、PASS系で
未検査のまま通過したケースなし)。

実測費用: analysis(Part A)¥0+rep20(Part B本体+Safety対照A・B)
¥6.0782=**¥6.0782**(Guardrail¥10のうち約61%)。Phase累計¥476.2883+
¥6.0782=**¥482.3665**/総枠¥600、残**¥117.6335**。詳細REPORT§33。

### 6-17. rep20 sample2の`ladder_exhausted_without_full_rewrite`根本原因特定と小修正(委任_36、REPORT§34)

**課題**: rep20 sample2 cycle2で、同一fact(MUSE-HC-012)に対する新規BLOCKING
claim(`“They could not tell if it was AI or a person” and “They did not
realize it.”`)が、ladder①単語・接続詞→③1文→④段落のいずれでも解消
できず`ladder_exhausted_without_full_rewrite`(⑥全文Rewrite不使用、fail-
closed)でSTAGE4へ至った。sample1では同じfact(MUSE-HC-012)が
`disclosure_gap_negative_inference_downgrade`floorで毎cycle QUALITYの
まま維持され、この経路を踏まなかった(同じfactでも表現が割れた)。

**原因特定(¥0、API呼び出しなし、決定論的な再現スクリプトのみ)**:
claim_textが記事中の非隣接2文(「They could not tell if it was AI or a
person.」と「They did not realize it.」)を“…” and “…”の形で結合した
合成claimであり、全断片がfull_text中に逐語で実在することを確認した。
一方、既存`locate_target()`はclaim_text全体に対する1文fuzzy match
(`locate_best_sentence`、SequenceMatcher)しか試みないため、2断片の
うち一方(ratio最大の「They could not tell...」1文のみ、ratio=0.74)しか
`en_target`に入らず、もう一方の「They did not realize it.」がladder①〜④
いずれの編集対象にも入らないまま残った(決定論的に再現・確認済み、
unittest`test_reproduces_rep20_sample2_cycle2_fix`参照)。JA側も
rewrite_hintの引用断片(`けれど、その一部では人間が話していた。しかも、
適切な説明がないままなら、利用者は相手がAIなのか人間なのかを知ること
ができません。」`)が、EN側の(修正前の)1文targetとは対応しない広い範囲を
拾っていた。

**修正(1回、fail-closed新規追加のみ、既存経路は無変更)**:
`er052_open233_self_recovery_flow_runner_01.py`へ以下2点を追加した。

1. `extract_all_quoted_fragments(text)`: 既存`extract_quoted_fragment`
   (最長1件のみ返す)の複数版。`_BRACKET_QUOTE_PATTERNS`
   (“”/「」/『』)でtext中の全断片を出現順に返す(直引用符"の分割抽出は
   複数断片では既知のペアリング曖昧性[委任_10]があるため対象外)。
2. `locate_multi_quote_span(claim_text, full_text, max_span_chars=600)`:
   claim_textが2つ以上の断片を含み、かつ全断片がfull_text中に逐語で
   実在する場合のみ、それらを包含する最小スパン(最初の断片の開始〜
   最後の断片の終了)を返す。断片が1つ以下・いずれかが不在・空行
   (`\n\n`、段落区切り)を跨ぐ・600文字を超える場合はNoneを返し
   (fail-closed)、既存の`locate_best_sentence`経路へそのまま委ねる。
3. `locate_target()`: 第一キー(rewrite_hintのexact substring)の次、
   第二キーとして`locate_multi_quote_span`を追加(失敗時は既存の
   `locate_best_sentence`→er010 word-overlapへ従来通りfall through)。
   `single_text_rewrite`/`run_paired_local_rewrite`の両方が本関数を
   共有するため、両経路に同時に適用される。
4. `run_paired_local_rewrite()`のJA側target決定: `en_target`が
   `multi_quote_span`で特定された場合に限り、rewrite_hintのJA引用断片
   より位置写像(既存`locate_ja_counterpart_by_position`)を優先する
   (rep20 sample2 cycle2実測で、rewrite_hintのJA引用がen_targetスパンと
   無関係な箇所を拾っていたため)。multi_quote_span以外の既存経路は
   一切変更しない。

unittest: 開始前チェック(既存317件相当の前提、実際は既存304件)→新規
13件(`TestExtractAllQuotedFragments`5件・`TestLocateMultiQuoteSpan`5件・
`TestLocateTargetMultiQuoteIntegration`3件[うち1件はrep20 sample2
cycle2の実データ[claim_text/en_full]をそのまま使った回帰ロック
テスト])→計317件、全PASS。

**rep21実測(frozen fixture再検証、n=2+Safety対照changed_number n=1)**:
rep19/rep20と同一のfrozen fixtureを`er052_open233_self_recovery_flow_
runner_01_rep21_representative_01.py`(新規、`OUT_DIR_REP21`新設)で
再実行した。

| run | final_state | stage4_reason | cycle数 | 費用 |
|---|---|---|---|---|
| sample1 | `STAGE4_ESCALATION` | `cycle_limit_exhausted` | 3 | ¥2.1567 |
| sample2 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | ¥1.2052 |
| Safety(changed_number) | `RESOLVED_REWRITE` | - | 1 | ¥0.1991 |

sample2(本委任の修正対象そのもの)はSTAGE4へ至らず解消した。ただし
このrun自体ではcycle2のStage2 LLM出力が単一claim(MUSE-HC-012「They
enjoyed...」、floorでQUALITY)のみとなり、rep20で観測された2断片合成
claimの形自体は再現しなかった(Stage2のLLM非決定性、既知の限界)。
本修正の有効性は、rep20実データをそのまま使った決定論的unittest
(上記)で確認している。

**新規発見(委任_36のスコープ外、報告のみ・未修正)**: sample1がrep20
(RESOLVED、3cycle)から一転し`STAGE4_ESCALATION`
(`cycle_limit_exhausted`)となった。原因を追跡したところ、本委任の
修正とは**無関係**であることを決定論的に確認した(該当claim_textの
断片数は1[curly quoteで2文をまとめて1つに囲んだ形]であり、
`locate_multi_quote_span`は`not_multi_quote`を返して即座に既存経路へ
委ねるため、修正前後でコード経路は完全に同一)。実際の原因は、cycle1で
Stage2 LLMが`rewrite_hint`を空文字列で返したこと(rep20では引用断片
入りのrewrite_hintを返していた、非決定性)により、`locate_target`の
第一キー(rewrite_hint引用)が不発火となり、1文SequenceMatcher
fallbackが「It said...during calls. These calls were...fees.」という
2文結合quoteのうち1文しか捕捉できず、「These calls were...」側が
cycle2以降も再検出され続けたことによる(本修正が対象とした断片分割
パターンとは別の、1つのquoteが複数文にまたがる場合の既知の限界、
変種(e)として記録)。false PASSではない(STAGE4は安全側のfail-closed)。
変種(e)の修正要否はFable/ユーザー判断事項として次委任へ持ち越す
(本委任は委任文が指定した「rep20 sample2の原因特定と小修正1回」の
範囲に留め、新たな根本原因の追加修正は行わない)。

Safety対照(changed_number fixture1件full flow n=1)は引き続き
`deterministic_floor:changed_number`でBLOCKING→Rewrite→`RESOLVED_
REWRITE`(floorが弱まっていないことを確認)。
`detect_safety_critical_misdowngrades`は0件。false PASSは0件。

実測費用: analysis(Part A)¥0+rep21(Part B本体¥3.3619+Safety対照A
¥0.1991)=**¥3.561**(Guardrail¥7のうち約51%)。Phase累計¥482.3665+
¥3.561=**¥485.9275**/総枠¥600、残**¥114.0725**。詳細REPORT§34。

### 6-18. 受け渡し修正(Checkerの違反範囲をそのまま渡す)の実装と限定Trial(委任_42、2026-10-02、REPORT§35)

**区分**: Trial/検証用の実装(Production正式path・Checker/Stage 2のPrompt・rubric・floor・cycle上限・⑥既定OFFは無変更)。
Opus独立技術レビュー#5(`docs/pm/opus_l2_review_open233_self_recovery_05.md`)済みの設計
(`docs/pm/design_open233_violation_span_handoff_01.md`)から、ユーザー決定(2026-10-02、DECISION_LOG)で項目を減らした範囲
(Checker Prompt変更なし・別AI引用救済なし・文単位スナップなし)だけを実装した。

**実装(`er052_open233_self_recovery_flow_runner_01.py`、Trial専用runner)**:

| 仕様 | 実装 |
|---|---|
| (1)範囲の確定 | `resolve_violation_spans`(2955付近)+`vs_match_levels`/`vs_resolve_in_text`/`vs_merge_spans`(2876〜2950付近)。無料集計`aggregate_01.py`(委任_41)のL0〜L4・「ちょうど1箇所」を移植(import無し)。EN・JA両本文で照合し確定した言語を保持。確定不能の理由は`mismatch`/`multi_match`/`explanatory_mixed`(記録) |
| (2)対象決定の置換 | `HANDOFF_MODE`(323、既定`violation_span`、`legacy`で旧方式)。新方式では`locate_target`4段を呼ばない(`single_text_rewrite`冒頭の分岐=3410付近、`paired_rewrite`のEN対象=`_paired_en_target_from_span`)。区分判定は`detect_claim_section_type_by_spans`(1879付近、確定範囲の包含判定、title>in_one_line>hook>body)。旧`detect_claim_section_type_legacy`・`locate_target`等は残置(legacy専用) |
| (3)呼び出し単位 | `rewrite_ranges_ladder`(3198付近): 1指摘=1回の呼び出し、`{"revised_ranges": [...]}`の同個数・同順序の配列、範囲を含む段落を読み取り専用文脈(`E1/E2/E4_RANGES_PROMPT_TEMPLATE`、3094〜3160付近)。hintは「書き換え指示文」としてのみ渡す |
| (4)最小修正優先 | 水準①=確定範囲そのもの、③=`vs_expand_to_sentences`(範囲を含む文全体)、④=範囲を含む段落。`filter_levels_by_problem_kind`・`escalate_to_paragraph`・⑥既定OFFは無変更 |
| (5)書き戻し | `vs_replace_once`/`vs_apply_replacements`(3040/3186付近): 書き戻し直前に現在の本文で「ちょうど1箇所」を再確認、失敗した水準は`writeback_failed`(推測で置換しない) |
| (6)guard | 各対象(①範囲・③④拡張後)が`revised != target`であること+主体置換ガード維持。delete型は確定範囲(正規化後)の完全一致で本文に残っていないことを確認 |
| (7)周回間同一判定 | `annotate_claim_span_identity`(3058付近)→`find_matching_prior_record(claim_norm=)`・`prior_blocking_records.claim_text_norm`・Recheckの`prior_issues`が確定範囲(複数なら改行連結)を使用(`run_instance`5080付近ほか)。Stage 2へ渡す`claim_text`表示は無変更 |
| (8)日本語側(暫定) | `run_stage3_for_claim_spans`/`_run_stage3_spans_core`(4011〜4150付近): ja_source+EN単一範囲=既存`paired_rewrite`(EN対象のみ確定範囲、JA対応決定の既存処理は無変更)。ja_source+EN複数範囲またはJAのみ確定=暫定で確定できた言語側だけを直す片側経路、もう一方は既存JA Recheckに任せる。`handoff["ja_provisional_path"]`に記録。**暫定**(JA側の構造見直し[英語だけ直す化]は並行調査+Opusレビュー後の別委任) |
| (9)記録 | 各`rewrite_records[*].handoff`(Checker文字列/確定範囲/照合レベル/確定不能理由/水準別の対象・結果・before/after・各対象の変化/JA暫定経路/carry-forward) |
| (10)テスト | 新規64件(合計381件)。意図的に書き換えた既存テスト: 旧方式を明示する`@_legacy_handoff`化7件(旧`locate_target`経由のladder順序・paired partial-locate)、`stage4_reason`のソース検査1件。旧`locate_target`/`locate_multi_quote_span`の関数単体テスト(`TestLocateTarget*`等)は旧関数を残すため維持 |

**仕様どおりにできなかった点・判断した点**:
- delete型で確定範囲が文の一部の場合: 決定論的削除の対象は範囲を含む文(文の断片だけを削除すると不自然な断片が残るため)。`handoff.delete_expanded_to_sentence`に記録(文全体の場合は範囲のまま削除)。
- JA本文でのみ確定し、originが`ja_source`でない指摘: JA側を直す経路がないため`violation_span_unverified`(`ja_only_match_origin_not_ja_source`、fail-closed)。
- 限定Trialで判明した実装不具合(下記)の是正として`carry_forward_resolution`/`collect_replaced_units`を追加した(設計書・Opusレビューにない小機構。要Fable確認)。

**限定Trial(rep22、固定Stage 1=rep19 frozen、TTSなし、`er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`)**:

| 部分 | run | 最終状態 | stage4_reason | cycle | call | 費用 |
|---|---|---|---|---|---|---|
| T1 | s1 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.1210 |
| T1 | s2 | `STAGE4_ESCALATION` | `cycle_limit_exhausted` | 3 | 7 | ¥2.1773 |
| T1 | s3 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.3140 |
| T1 | s4 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.0118 |
| T2(rep20 s2 cycle2再現) | s1 | EN: 前回指摘は解消、JA: 未解消(`ja_ok=False`)。1周で終了(cycle3は再現範囲外) | - | 1 | 6 | ¥1.0338 |
| T2 | s2 | EN: 前回指摘は解消+Recheckが別の新規MAJOR(MUSE-HC-010)、JA: 未解消 | - | 1 | 6 | ¥1.0143 |
| T3 Safety(changed_number) run1 | - | `STAGE4_ESCALATION` | `violation_span_unverified`(実装不具合、下記) | 1 | 2 | ¥0.1992 |
| T3 run2(是正後) | - | `RESOLVED_REWRITE`(30 million→13 million、Ledger値) | - | 1 | 3 | ¥0.2311 |

合計¥8.1025(委任_42 Guardrail¥15の54%)。Phase累計¥485.9275+¥8.1025=**¥494.0300**/総枠¥600、残**¥105.9700**。

**成功条件ごとの実測(記録値`er052_output/open233_self_recovery_flow_runner_01_rep22/analysis_rep22.json`、`--parts agg`)**:
1. 2文取りこぼしによるHuman Review: T1 n=4で2文claim(MUSE-HC-011)が1周目に2文とも水準①の対象になった=4/4(対象=「It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.」の2文1範囲、L1)。Stage 4は1/4(s2、`cycle_limit_exhausted`)で、取りこぼし起因のStage 4は0。s2の原因は受け渡し以外(下記)。**達成(取りこぼし起因0)**。ただしs2のStage 4は残る(受け渡し以外の原因)。
2. 範囲の縮小: 水準①の試行6件(T1 4+T2 2)で「対象==確定範囲」6/6、不一致0。**達成**。
3. 誤PASS: T3でfloorが両claimともBLOCKING(`deterministic_floor:changed_number`+`precheck_floor`)、Recheck=LEDGER_COMPLIANTで本文はLedger値(1,300万件=13 million)へ修正、false PASS 0。T1の`RESOLVED_REWRITE_THEN_DOWNGRADE`3件は既存の仕組み(Stage 2が最終cycleで残りのclaimを既存floor`disclosure_gap_negative_inference_downgrade`等でQUALITY/ACCEPTABLEとした)で、未解消のBLOCKINGが残った例は0件。旧方式の同じ固定入力でも同じ最終状態(`RESOLVED_REWRITE_THEN_DOWNGRADE`)が出ている(rep20 s1・rep21 s2)。**達成(Fable確認事項: 上記3件の最終cycleでQUALITY扱いになった文のレビュー)**。
4. 最小修正優先: ①から開始したのは6/7件(T1 4、T2 2、T1 s2 cycle2の1件[MUSE-HC-010、確定範囲=記事中の文の断片]は既存の問題種類→初期水準の規則[`multi_sentence`=初期④、委任_27]によりSTAGE④から開始)。水準別の成立: T1 ①4件・④1件、T2 ④2件(①は「最小編集では解消できない」[declined]、③は主体置換ガードで棄却[新語`users`]の後)、T3 ③1件(既存規則で③開始)+後続claimは先行Rewriteで書き換え済みとしてスキップ。**達成(開始水準は既存の水準選択規則に従う)**。
5. 不要な段落・全文Rewrite: ⑥は0件(既定OFF)。④はT1で1/4 run(s2 cycle2、問題種類規則による初期④)、旧方式の同じ固定入力(rep20 s1・s2、rep21 s1・s2)でも④成立1/4 run。T2は④が2/2だが、旧方式は同じ状態(rep20 s2 cycle2)で①③④全不成立→Stage 4(`ladder_exhausted_without_full_rewrite`)。**T1では増加なし。T2は④でしか成立せず、これが「不要」かの判断はFable**。

**FAIL→修正→再確認(T3、1回)**: 初回T3 run1が`violation_span_unverified`でStage 4になった。原因: 同じcycleにLLM claimとprecheck floor claimが同じ文を指しており、先行claimのRewriteで文が書き換わった結果、後続claimのCheckerの文字列が現在の本文から消え、確定不能(不一致)と誤判定した(受け渡しの実装不具合)。修正(本委任の範囲内): `carry_forward_resolution`(cycle開始時点の本文でCheckerの文字列を照合し、その範囲が同一cycleの先行claimのRewrite対象に含まれていれば「先行Rewriteで書き換え済み」としてRewriteを重ねない[解消判定は全文Recheck]。先行Rewrite対象に含まれず現存もしない範囲は従来どおり確定不能)。テスト6件追加。T3だけ再実行(¥0.2311): `RESOLVED_REWRITE`。

**受け渡し以外の原因でStage 4になった run(T1 s2、周回ごとの指摘)**:
- cycle1(固定Stage 1): BLOCKING 1件=MUSE-HC-011「It said human staff ... calls. These calls were about trying to lower internet or cable fees.」(MAJOR→BLOCKING、`deterministic_floor:changed_number`)→水準①成立(2文を「during a call」「This call」へ)。Recheck: 前回指摘は解消(`recheck_all_prior_issues_resolved=True`)、次cycleへ持ち越したMAJORは2件(同じHC-012の文[cycle1でQUALITY]とHC-010)。
- cycle2: 新規BLOCKING=MUSE-HC-010「some calls needed user information to continue」(元記事「Also, some calls needed user information to continue.」、元記事に最初からあった問題で固定Stage 1は検出していない)。QUALITY=MUSE-HC-012「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」(`disclosure_gap_negative_inference_downgrade`でQUALITYへ降格)。HC-010は問題種類規則で④開始→成立。Recheck: 前回指摘は解消(`recheck_all_prior_issues_resolved=True`)、新規MAJOR。
- cycle3: MUSE-HC-012「They enjoyed AI’s convenience ...」が**今度はBLOCKING**(cycle1・2は既存floorでQUALITY=判定役の重大度の揺れ)→cycle上限(`MAX_CYCLES=2`、blocking件数が減少せず、新しいfact_idでもないため追加cycle不可)で`cycle_limit_exhausted`。
- 切り分け: 受け渡し起因ではない(各周回で対象になった範囲はCheckerの文字列どおり)。元記事にあった問題の周回ごとの新規検出(再検査の揺れ)と、同一問題のMinor→Major(Stage 2判定の揺れ)。本委任の範囲外(並行調査委任_44)のため修正せず。

**暫定事項(JA側)に該当した件数**: T2のn=2で2/2(いずれも`en_multiple_ranges`、確定できたEN側だけを直し、JAは既存のJA Recheckに任せた)。JAのみ確定は0件。結果: 両sampleでJA Recheckが「未解消」(`ja_ok=False`、s1: JA「適切な説明がないままなら、利用者は相手がAIなのか人間なのかを知ることができません。」、s2: 同様の2箇所)。T1(origin=translation)はJA暫定経路に入っていない。

**残る問題**: (1)T2の再現は1周のみで、JA暫定経路の結果が「JA未解消」のため、実際の周回では次cycleでJA側のRewriteへ進む。JA側の構造見直しが別委任で必要。(2)T1 s2型(周回ごとの新規指摘・重大度の揺れ)は受け渡し修正では解消しない(並行調査委任_44の対象)。(3)主体置換ガード(`users`)がT2の③を2/2棄却した(既存ガード、新方式のJA/EN比較の問題ではなく範囲だけを比較する既存仕様)。(4)最終的な分類(`REJECTED`/`VALIDATED`/`USER_DECISION_REQUIRED`)はFable。

**ユーザー指示(2026-10-02)との対応表(PM_GOVERNANCE 22節、Trial開始前チェック。未反映0件を確認してから課金Trialを開始した)**:

| # | ユーザー指示 | 反映先 | 実測 |
|---|---|---|---|
| §1-1 | Checkerが示した違反範囲を後段で再推測しない | `resolve_violation_spans`(照合のみ)、新方式で`locate_target`4段を呼ばない | 全rewrite記録のmethodが`violation_span(...)`(旧4段の識別子なし)。unittest`test_old_four_stage_locators_are_not_called_in_new_mode`(旧locatorを例外化しても動作) |
| §1-2 | 複数文なら複数文のままRewriteへ | 複数文=結合した1範囲を①の対象にする | T1 4/4で2文が1範囲として①の対象 |
| §1-3 | 離れた複数箇所なら複数範囲 | L4、配列呼び出し | T2 2/2で2範囲が配列で渡った(間の文は対象外) |
| §1-4 | 別AIの引用でRewrite対象を決めない | hintは指示文のみ | unittest`test_hint_quote_does_not_decide_the_target` |
| §1-5 | 類似度・単語重なりで勝手に1文へ縮小しない | 確定不能は`violation_span_unverified`でStage 4 | 縮小0(①対象==確定範囲6/6) |
| §1-6 | 文ID・文字オフセット方式は採用しない | 書き戻しは文字列の「ちょうど1箇所」再確認のみ(位置は範囲の結合・文への拡張の計算とログにだけ使い、持ち回らない) | 採用なし |
| §1-7 | 最小修正優先ルールを維持 | `filter_levels_by_problem_kind`/`escalate_to_paragraph`/⑥既定OFF無変更 | ⑥0件 |
| §1-8 | 語句→文全体→必要最小範囲 | ①=範囲、③=範囲を含む文、④=段落 | 水準別の対象を記録(例: 「some calls needed ...」断片→「Also, some calls ...」文) |
| §1-9 | 文の一部が違反でも最初から文全体Rewriteへ広げない | ①の対象=確定範囲(断片) | unittest(d)、T1 s2 cycle2を除き①から開始 |
| §1-10 | 語句だけで済むもの(oil prices→Brent futures型)は語句だけ修正 | ①のPrompt(語句・接続詞・限定句の最小編集、範囲内で変更不要な部分は一字一句そのまま) | T1 ①4件 |
| §2-1 | 受け渡し修正後に限定Trial | rep22 | 実施 |
| §2-2 | meta_run03_standard中心 | T1/T2 | 実施 |
| §2-3 | 2文取りこぼし型・離れた複数箇所型・Safety対照 | T1/T2/T3 | 実施(T2は再現入力から1周のみ) |
| §2-4 | 成功条件5項目 | 確認項目1〜5(`--parts agg`) | 上記 |
| §2-5 | 費用は既存予算内で最小限 | Guardrail¥15、n=4/2/1 | ¥8.1025 |
| §8-1 | STOP条件6件のみUSER_DECISION_REQUIRED | 該当確認(新Product原則・Safety原則変更・Production正式仕様変更判断・¥600超過・Opusとの重要点の対立・QCD上のユーザー判断のいずれも該当せず) | STOPなし |
| §8-2 | 1回のFAILや新変種だけで戻さず、原因特定→対策→限定再確認 | T3 FAIL→carry-forward→T3再確認 | 実施 |
| §8-3 | Production正式pathは変更禁止 | 変更はrunner・テスト・rep22スクリプトのみ | `git grep "er052_open233" -- "er003*.py" "er0[0-4]*.py"`=0件 |
| §8-4 | Trial終了時にREJECTED/VALIDATED/USER_DECISION_REQUIREDへ分類 | 実測値と所見を提示、分類はFable | 未分類(Fable) |
| §8-5 | VALIDATEDでもProduction採用ではない | 本節はTrial結果であり`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない | - |

## 7. Trial上の正解ラベル(claim単位、最終到達状態ベース)とfixture群の再編

**位置づけ・用語(委任_03で全面改訂)**: 本節は「gold」という語を使わず
**「Trial上の正解」「正解ラベル」**で統一する(前Phase文書
[`design_open233_checker_redesign_trial_01.md`等]は変更しない。用語
統一は本書と本Phase REPORTの範囲のみ)。**claim単位で評価する**
(fixture単位ではない。1 fixture=1記事に、許容すべきclaimとBLOCKING
すべきclaimが混在するB1/B4のような例があるため)。以下は
`design_open233_checker_redesign_trial_01.md`§2(fixture単位)・§2-補
(claim単位、Opus L2レビュー#1論点2の独立評価)を、ユーザー確定事項
(B2=QUALITY、B3=BLOCKING、B1/B4=claim単位で混在)と統合し、**確定
ラベル**を付けたものである。**claim単位の正解ラベル整理はユーザー
承認済み(2026-09-30委任文§1・§4)。KPI(Primary=USER_DECISION_REQUIRED
0件、Safety=重大Fact見逃し0件)の意味は変えていない**(既存fixture単位
表・§2-補claim単位候補表そのものを上書きするのではなく、Self-Recovery
Flowの評価用に確定ラベルを付与する新しい層)。

### 7-0. claim単位 確定ラベル表

| claim | 確定ラベル | fail-closed側に倒したか | 根拠(要旨) |
|---|---|---|---|
| B1-a(ホルムズ海峡=重要航路) | **ACCEPTABLE** | いいえ | 地理的一般常識、新規固有名詞・数値・主体を加えない(Opus論点2一致) |
| B1-b(原油高→ガソリン等波及) | **ACCEPTABLE** | いいえ | 条件付き一般経済常識、`observation_consistent=true`実測済み |
| B1-c(市場動機・価格回復理由の断定) | **BLOCKING** | いいえ(Opus評価どおり) | HF-011 notesが因果推論を明示禁止、主要Fact理解(なぜ価格が戻ったか)を変える |
| B2(料金案消滅と価格回復の因果連結、"so") | **QUALITY** | いいえ(ユーザー確定) | Ledgerが記録した2観測の共起を因果接続詞で連結。Ledgerと矛盾はしないが明文で禁じた書き方 |
| B3(接続詞"so"、政策決定理由の取り違え) | **BLOCKING** | いいえ(ユーザー確定+Opus/v0.2/Step2診断3系統一致) | HF-007 conditionsに別原因(中東指導者協議)が明記、政策決定理由を取り違えさせる |
| B4-a(AIフォールバック機構の新規主張) | **BLOCKING** | いいえ | MUSE-HC-006範囲外の製品仕様捏造、材料的誤伝達 |
| B4-b(人間心理の一般論) | **ACCEPTABLE〜QUALITY(Trialでは QUALITY扱い)** | **はい**(ACCEPTABLE〜QUALITYの幅をQUALITY側=やや厳しい側に倒す) | Metaの事実を歪めないが、Checkerの過剰検出(changed_scope)との境界が曖昧なため、Trial評価では「継続はするが要観察」のQUALITY側で統一し、ACCEPTABLE即時通過とは区別する |
| B4-c(AI/人間判別への関心の一般論) | **ACCEPTABLE〜QUALITY(Trialでは QUALITY扱い)** | **はい**(同上) | 同上 |
| B4-d(テスト結果の確実性強化、V4A run) | **QUALITY〜BLOCKING(Trialでは BLOCKING扱い)** | **はい**(fail-closed側=BLOCKING) | certainty変化(「思わせるテスト」→「実際に驚きを生じさせた」)はfloor対象外(changed_certaintyはdeterministic floor非対象、§4-3)だが、境界が未確定である以上Trial評価では安全側=BLOCKINGとして扱い、Stage 2が実際にQUALITYへ降格させた場合はその挙動を観測記録する(正解ラベル自体をACCEPTABLE側へ緩めない) |

### 7-0-iter4. 委任_12再ラベル(§1ユーザー指示「許容線の再設計」、
2026-09-30、根拠付き)

ユーザー指示(§1)に基づき、以下のclaim/fixtureをclaim単位で再判定した
(新基準=「確認済みFactから人間が普通に読めば自然に導く範囲か」、
「完全に証明されているか」ではない)。**上記7-0本表は歴史的記録として
変更しない**(委任_04〜_08時点の判定根拠の記録)。本節が委任_12以降の
Self-Recovery Flow Trial評価における現行の正解ラベルである。

| claim/fixture | 旧ラベル(§7-0) | 新ラベル(委任_12) | 根拠(新基準での判定) |
|---|---|---|---|
| B1-c(市場動機・価格回復理由の断定) | BLOCKING | **QUALITY** | 「市場が海上リスクを重視したから価格が戻った」程度の断定は、確認済みFact(海上リスクの存在・価格の反発)を人間が自然に読めば導ける解釈であり、新しい具体的事実(誰が・いつ・いくら)を発明していない。ユーザーの許容例(「海上リスクが価格の戻りに影響した可能性がある」等)に該当し、断定がやや強い程度ではSTOPさせるほどの重大誤りではない |
| B4-d(テスト結果の確実性強化) | QUALITY〜BLOCKING(Trial扱いBLOCKING) | **QUALITY** | certainty変化はユーザーNG5項目(actor/number/negation/comparison/time)に含まれず、新しい具体的な人物・数字・出来事・仕組みの追加でもない。floorからも除外(§4-3改訂)。境界未確定時の安全側措置(fail-closed)は本委任のユーザー指示により解消された |
| B3(接続詞"so"、政策決定理由の取り違え) | BLOCKING | **BLOCKING(変更なし)** | Ledger conditionsが「中東指導者との協議に基づく決定」という具体的な別原因を明記しているのに、記事は「懸念継続によりXが撤回された」と逆の原因を断定している。これはNG(a)「Ledgerのconditionsと矛盾」およびNG(d)「Fact逆方向の因果」に明確に該当し、「自然な解釈」の範囲を超える(Ledgerが明示した別の具体的原因を無視して別原因を断定するのは、確認済みFact同士を自然に繋ぐ解釈ではなく、Ledgerとの直接矛盾)。fail-closed側へ倒したわけではなく、新基準でも素直にBLOCKING |
| hormuz_run03_standard(HF-009 changed_scope、Brent先物→石油市場全体) | BLOCKING | **BLOCKING(変更なし)** | Ledgerが確認しているのは特定の先物価格(Brent)の観測のみであり、それを「市場全体」という具体的な範囲(新しい主体の集合)へ一般化する記述は、NG(b)「Ledgerに無い具体的な出来事・範囲の追加」に該当する(§4-9 R3'較正でも安定してBLOCKINGと判定されることを実測確認、n=2で2/2) |
| HF-006(原油高→ガソリン・輸送費への波及、B1-b) | ACCEPTABLE | **ACCEPTABLE(変更なし)** | 条件付きの一般経済常識であり、新しい固有名詞・数値・主体を追加していない |
| A4(懸念の存在→大規模漏えいの断定) | BLOCKING | **BLOCKING(変更なし)** | Ledgerが確認しているのは「懸念が存在した」という事実のみであり、それを「大規模な情報漏えいが実際に起きた」という具体的な新しい出来事へ変えるのはNG(b)に明確に該当する(新しい具体的事実の発明) |
| A5(意味反転) | BLOCKING | **BLOCKING(変更なし)** | NG(a)(d)(e)のいずれにも明確に該当する意味・因果の反転であり、自然な解釈の範囲外 |
| Safety12(er009 9種、合成改竄) | BLOCKING | **BLOCKING(変更なし)** | 5種(actor/number/negation/comparison/time)はfloorで維持、残り4種(scope/causality/certainty/unsupported_new_claim)もLedgerとの明示矛盾または新規具体的事実の追加であり、新基準でも素直にBLOCKING |
| negative候補7記事(全claim) | ACCEPTABLE(正解、Stage1のみで完結が期待) | **ACCEPTABLE(変更なし、不要Rewrite0件が正解)** | 正常記事であり、いずれのclaimもNG(a)〜(e)に該当しない。§8追加測定「正常記事の不要Rewrite件数・率」の分母(NORMAL_GROUP_INSTANCE_IDS)としても使用する |

**単体較正実測での確認(§4-9)**: 上記再ラベルのうちB1-c/B4-dはR3
(素)で2/2ともQUALITYへ正しく到達することをn=2で実測確認した。B3・
hormuz-HF009・A4・A5はR3'(採用rubric)でSafety側BLOCKINGとして
安定することを実測確認した(hormuz-HF009はR3素では1/2 ACCEPTABLEへ
誤降格したが、R3'で2/2 BLOCKINGへ復帰、§4-9)。

### 7-0-iter5. 委任_13再ラベル是正(Opus L2レビュー#3論点1、正解ラベルの
循環参照の是正)

**発見された問題**: Opus L2レビュー#3により、A2A3/A4/A5群の正解ラベルが
「人間がNG(a)〜(e)に照らして付けたもの」ではなく、「Stage 1(V4A)の
過去出力で`severity_final=="BLOCKING"`だったdeviationを機械的に全部
BLOCKINGとみなしたもの」(`build_eval_groups()`、循環参照)であることが
判明した。この結果、較正の受入条件「Safety側誤降格0件」は事実上「Stage
2はStage 1に一度も反対してはならない」という条件になっており、iteration4
のユーザー指示(Stage 1の過剰検出を自然な解釈基準で是正する)と矛盾して
いた。

**是正1(ラベル)**: A2A3-1(HF-006「原油高→ガソリン・輸送費」)は、正解
ACCEPTABLEとされているB1-bと実質同一内容であり、A4-2(MUSE-HC-010
certainty強化)は正解QUALITYとされているB4-bと同一factを扱う。いずれも
NG(a)〜(e)のどれにも該当しないため、QUALITYへ再ラベルする
(`CORRECT_LABEL_OVERRIDES_R3DPRIME`/`CORRECT_LABEL_OVERRIDES_
R3TRIPLEPRIME`、既存`build_eval_groups()`の機械コピー由来ラベル自体は
変更せず、既存r3_natural_calibration_01.pyのCORRECT_LABEL_OVERRIDES_R3
と同一方式でoverride)。

**是正2(受入条件)**: 「Safety側誤降格0件」を、全group一律ではなく、
名指しした**Safety-critical claim 10件**(A2A3-0/A4-0/A4-1/A5-0/A5-1/
Meta-1/Meta-2/hormuz-HF009/B3/B4-a)の降格0件へ限定する
(`SAFETY_CRITICAL_SUB_IDS`)。A2A3-1/A4-2はQUALITYへ再ラベルされた
ため、自然にこのリストから除外される。

### 7-0-iter27. 上位原則「重大誤解原則」によるhormuz-HF009再ラベル(委任_27 Part1、§0参照)

**再ラベル**: hormuz-HF009の「Oil prices」型scope一般化claim(実データ、
`hormuz_run03_standard`本文①②③、"Oil prices did not fall across the
whole market after the plan was withdrawn." 等、Brent先物→oil prices
[同じ原油という対象内での一般化])は、§0-2の原則許容候補
「Brent futures→oil prices」に該当するため、**正解ラベルをBLOCKING
からACCEPTABLE/QUALITY(Rewrite不要)へ改める**(2026-10-01ユーザー
指示、委任_27委任文§2)。Hormuz要素Trial A(§9-1⑰)で実測確認済み。

**SAFETY_CRITICAL_SUB_IDSとの関係(重要、要Fable/ユーザー確認)**:
`hormuz-HF009`は§7-0-iter5で確定したSafety-critical claim 10件
(`er052_open233_self_recovery_r3dprime_calibration_01.py`)の1つで
あり、本再ラベルはこのリストとの直接的な矛盾を生む(同一claimが
「必ずBLOCKING維持」と「ACCEPTABLE/QUALITYが正解」の両方に属せない)。
**本委任では`SAFETY_CRITICAL_SUB_IDS`自体(既存calibrationスクリプトの
定数)は変更しない**(既存iteration証跡の再現性維持のため)。Hormuz
要素Trial A(§9-1⑰)のSafety対照群では、hormuz-HF009の代わりに
**B3(因果、HF-007)+er009 changed_scope(別記事・別領域へのscope
拡張、taxi→restaurants nationwide、真にBLOCKINGな対照)**を使用した。
`SAFETY_CRITICAL_SUB_IDS`から`hormuz-HF009`を除外する編集自体は、
過去iterationの較正証跡(iter4/5/6等)の解釈に影響するため、Fable/
ユーザー判断を仰ぐ(USER_DECISION_REQUIRED候補ではなく、次回委任での
確認事項として記録)。

**委任_28追記**: 上記確認事項を受け、委任_28委任文Part0-2で
`hormuz-HF009`を`SAFETY_CRITICAL_SUB_IDS`(9件化)から除外する編集を
実施した(過去iteration較正証跡[iter4/5/6のsummary json等]は保存済み
の値のまま不変、本変更は以後の新規実行にのみ影響、根拠はDECISION_LOG
参照)。除外後の9件に対する全量対照測定の結果は§9-1⑱・REPORT§26を
参照(A5-1・Meta-1/Meta-2の2件がV3適用後も残存し、本書時点ではSafety
側の懸念が未解消)。

**BLOCK候補への対応付け監査(§1指示、変更はしない)**: Safety-critical
10件+Safety12(er009 9フラグ)の各claimが、§0-2のBLOCK候補(主体/
方向/規模/時間軸/未確認追加/逆因果のいずれか)に対応付けられるかを
確認した。hormuz-HF009を除く9件(A2A3-0/A4-0/A4-1/A5-0/A5-1/Meta-1/
Meta-2/B3/B4-a)・er009 9フラグ全てが明確に対応する(A2A3-0/A4-0/
A4-1/A5-0/A5-1=事実・方向の誤認、Meta-1/Meta-2=主体・認識の誤認、
B3=因果の逆転、B4-a=未確認の仕組みの追加、er009 9種=floor対象flagの
定義どおり)。**hormuz-HF009のみが対応しない**(§0-2の原則許容候補
「Brent futures→oil prices」そのものに該当するため)。他に見直し
候補は無い。**委任_29追記**: 上記は委任_27時点の記録であり、A5-1も
同様にhormuz-HF009と同種の「対応しない」側(役職の同一対象内一般化)で
あることが委任_29で確定し、`SAFETY_CRITICAL_SUB_IDS`から除外した
(9件→8件、§7-0-iter29参照)。残る8件(A2A3-0/A4-0/A4-1/A5-0/Meta-1/
Meta-2/B3/B4-a)は引き続き§0-2のBLOCK候補に明確に対応する。

### 7-0-iter29. A5-1再ラベル+Meta-1/Meta-2 false downgrade是正(委任_29 Part1、§0参照)

**再ラベル(Fableラベル判定、委任_29委任文§1)**: A5-1(“Meta executives
admitted that starting the test without a proper explanation was a
mistake.”、related_fact_id=MUSE-HC-012)は、Ledgerが「特定のMeta副社長」
の発言としているのに対し、記事は「Meta executives」というより一般的な
役職名で言い換えているだけであり、発言内容・責任主体(Metaという同一
組織)自体は変えていない。これはhormuz-HF009(§7-0-iter27)と同種の、
同一対象内での役職・用語の一般化であり、**正解ラベルをBLOCKINGから
QUALITY(非BLOCKING)へ改める**。`SAFETY_CRITICAL_SUB_IDS`から除外し
(9件→8件)、`CORRECT_LABEL_OVERRIDES_R3DPRIME`へ`"A5-1": "QUALITY"`を
追加した(`er052_open233_self_recovery_r3dprime_calibration_01.py`、
既存A2A3-1/A4-2/B1-c/B4-dと同じ「機械コピー由来ラベルの是正」の前例を
踏襲、Safety原則自体の変更ではない)。

**Meta-1/Meta-2 false downgrade是正(最小修正1回、V4)**: 委任_28の
V3公式測定でfalse downgradeしたMeta-1/Meta-2(“Also, some calls needed
user information to continue.”、related_fact_id=MUSE-HC-010)は、
Ledgerの実際の記録(conditions: 「電話の遂行にユーザー情報が必要と
なる場合」)が条件付きの可能性であるのに対し、記事はその条件を外し
「実際に起きた」と断定している(Stage1実測issue逐語:「条件付きの
可能性を、実際に発生した事実へ強めているため」、changed_fact=true・
changed_certainty=true)。これはA5-1型(役職の同一対象内一般化、許容)
とは別物の「未確認の出来事・行動を既成事実として断定」(§0-2のBLOCK
候補)であり、V2/V3は両者を明示的に区別していなかった。
`MISCONCEPTION_PRINCIPLE_TEXT_V4`(最小修正1回、新しい例示は追加せず、
「条件付きの可能性→既成事実への断定」を独立した原則として追加)で是正
した(`er052_open233_self_recovery_stage2_calibration_01.py`)。

**n=1予備測定→n=2公式測定(V4、`er052_open233_element_trial_safety_
control_02.py`、新規出力ディレクトリ、既存`..._01`は不変)**: Safety-
critical 8claim(A5-1除外後)+Safety12(er009 9フラグ)+Hormuz許容5/
NG5(委任_27 Trial Aのclaim定義を再利用、Stage2のみ)を対照測定した。
結果: Safety-critical 8/8・Safety12 9/9が、n=1予備測定・n=2公式測定の
いずれでも全てBLOCKING(misdowngrade 0件)。Hormuz許容5件は非BLOCKING
(ACCEPTABLE/QUALITY)・NG5件はBLOCKINGを維持(false PASS/false BLOCK
0件)。A5-1自身(参考測定、Safety-critical対象外)はACCEPTABLE
(n=2とも)となり、再ラベルと整合した。**1回の最小修正(V4)でSTOP
条件(Safety対照群のいずれかが小修正1回後もBLOCKINGに戻らない)を
解消し、PASSした**(費用¥4.9438、Guardrail¥10のうち)。詳細REPORT§27。

### 7-0-iter32. 広いTrial iteration 8でB3/A2A3-0の誤降格を新規検出(委任_32、2026-10-01、REPORT§30)

**位置づけの違い(重要)**: §7-0-iter28/iter29のSafety-critical 8/8
確認は、いずれも**Stage2のみ**(固定claim文を直接入力)の単体測定
(`er052_open233_element_trial_safety_control_0{2,3}.py`)であり、
Stage1は経由しない。委任_32(広いTrial iteration8、29 instance全量)は
初めて**Stage1 fresh(重大誤解原則配線版)→Stage2→Rewrite→Recheckの
full flow**でSafety-critical 8claimのうちB3・A2A3-0を含む複数instance
を実行し、この組み合わせで以下の誤降格を新規に検出した(過去の
Stage2単体測定は無効化されない、測定条件が異なるため非矛盾)。

**(1) B3(HF-007、§7-4で正解BLOCKING確定済み)**: `bgroup_B3`を
Stage1 fresh・n=2で実行した結果、**sample1・sample2の両方**で
B3クレーム(“Concerns about US-Iran attacks...so the flashy 20% plan
left the stage...same day.”)がStage2 body rubric(V5)により
QUALITYへ誤降格した(`llm_materiality=QUALITY`、`changed_causality=
true`・`unsupported_new_claim=true`、`FLOOR_FLAGS`非該当のため
deterministic floorが発火しない)。2/2で再現する**安定した**誤判定で
あり、A2A3-0(下記)のような偶発的揺れではない。

**(2) A2A3-0(HF-003、§7-1相当)**: `safety_A2A3`をStage1 reuse
(Safety12と同じ既定、§9-1㉒参照)・n=2で実行した結果、A2A3-0クレーム
(“The idea was that those carrying the cargo would repay the money
the United States spends...”、Ledgerは支払主体を特定しないとする
HF-003と明示的に矛盾)が、sample1ではBLOCKING(正しい)、**sample2では
QUALITYへ誤降格**した(同一Stage1出力[reuse、決定論]に対しStage2 LLM
判定のみが変動、`changed_fact=true`・`changed_certainty=true`・
`unsupported_new_claim=true`、`FLOOR_FLAGS`非該当)。1/2の揺れ。

**根本原因(共通)**: 両claimとも`FLOOR_FLAGS`(changed_actor/number/
negation/comparison/time)のいずれにも該当せず、deterministic floorの
保護を受けない。body rubric V5(重大誤解原則テキスト追加後)は、
Ledgerが明示的に否定・未特定とする具体的事実(支払主体/因果関係)を
記事が断定的に追加するケースについて、Stage2 LLM単体の裁量判定のみに
依存しており、この判定が非決定的に割れる。

**候補修正の検討(小修正1回、§4 FAIL時プロトコル)と不採用の理由**:
`matched_notes_id`+`observation_consistent=False`(Stage1が既にLedger
notesとの矛盾を決定論的に確認済み)を新しいfloor条件として追加する案を
検討したが、同一委任の実測データ中で**この組み合わせがhormuz-HF009
(“Oil prices did not fall...”、§7-0-iter27でBLOCKINGから
ACCEPTABLE/QUALITYへユーザー正式再ラベル済み)・meta_run03_standard・
safety_A5の複数の正当なQUALITY/ACCEPTABLE claimにも该当する**ことを
確認した。この条件でfloorを追加すると、既にユーザー承認済みの
hormuz-HF009再ラベルを機械的に無効化してしまうため、**安全側判断として
この小修正は採用しなかった**(§7 STOP条件「小修正1回後も残る」に該当、
根本設計変更[例: Safety-critical群限定のredundant judge/2回目判定の
導入、既存`stage2_two_of_two`のNORMAL_GROUP限定を緩和する等]が必要と
判断し、本委任ではコード変更を行わずFable/ユーザー判断へ委ねる)。

**Production影響**: 本委任はTrialコード(er052)のみの実行であり、
Production(er003/er006/er009/er010/er012/er019)・既存iteration/rep
証跡は無変更。ただし本発見は、重大誤解原則配線版の設計が将来
Production導入を検討される際に解消すべき既知のSafety側残存リスクとして
記録する。

### 7-0-iter33. 線引きの正式採用に伴う正解ラベル更新(委任_55、2026-10-03ユーザー決定[2回目]、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)

ユーザー決定(`DECISION_LOG.md`末尾)で「重大/軽微/問題なし」の線引きが正式採用された(基準文言は`docs/pm/open233_materiality_criteria_2026-10-03.md` 5節)。これに伴い、**上記7-0〜7-0-iter29のラベルは歴史的記録として変更せず**、本節が委任_55(2026-10-03)以降の現行の正解ラベルである。旧ラベルは「旧: …(〜2026-10-02)」として残す。分類の根拠は再分類doc(`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`)の表(K01〜K23)を正とする。

| claim | 現行ラベル(2026-10-03〜) | 旧ラベル(〜2026-10-02) | 根拠 |
|---|---|---|---|
| Meta-1/Meta-2(MUSE-HC-010/HC-012「Also, some calls needed user information to continue.」、K04) | **QUALITY(軽微)**(ユーザー決定、例1) | 旧: BLOCKING(Safety-critical、§7-0-iter29) | 共有は`might`で留保、懸念の主体はMeta従業員のまま。`SAFETY_CRITICAL_SUB_IDS`から除外(8件→6件)、runner `SAFETY_CRITICAL_CLAIM_DEFS`では`expected: "QUALITY"`の過剰品質監視用 |
| MUSE-HC-012「They enjoyed AI’s convenience, but a human was on the other end. …」(K10) | **ACCEPTABLE(問題なし)**(ユーザー決定、例2) | 旧: BLOCKING(Checker指摘、旧判定。QUALITYとの境界) | 確認済みFactから自然に導かれる利用者の状態の描写で、新しい具体的事実を追加しない(否定形・肯定形を問わない) |
| HF-009「Just after the charge plan disappeared, prices began to fall.」(K19) | **QUALITY(軽微)**(ユーザー決定) | 旧: BLOCKING(境界。再分類docで重大(境界)) | 核心(いったん値動きがあり、すぐ高い水準へ戻った)は保たれ、表現の精度が少し落ちるだけ。注意: 機械floor(`changed_comparison`)は不変のため、Checkerがcomparisonフラグを立てた場合はfloorでBLOCKINGに引き上げられる(下記「食い違いの残り」) |
| K01(bgroup_B4 / HC-006) | ACCEPTABLE | 旧: BLOCKING(LLMのみ) | 再分類doc |
| K02/K03(hormuz HF-009、一般化・言い換え) | QUALITY | 旧: BLOCKING | 再分類doc |
| K05〜K07(HC-011、単数→複数形、境界) | QUALITY(境界) | 旧: BLOCKING(floor/number) | 再分類doc。同じ段落が件数を固定しているため軽微。単複を数量変更とみなすかは未決(再分類doc 2-3節) |
| K08/K09(HC-012、floorのみactor) | ACCEPTABLE | 旧: BLOCKING | 再分類doc(floorは不変のためfloorで引き上げられる実行は残る) |
| K11(neg1 HC-012「A Meta executive admitted the mistake…」) | QUALITY | 旧: BLOCKING | 再分類doc |
| K12/K13(neg1 HC-012) | ACCEPTABLE | 旧: BLOCKING | 再分類doc |
| K14/K15(neg3、floorのみ) | ACCEPTABLE | 旧: BLOCKING | 再分類doc |
| K17(neg3 HF-009) | QUALITY | 旧: BLOCKING | 再分類doc |
| K23(HC-012「An AI called. That was what people thought…」) | ACCEPTABLE | 旧: BLOCKING | 再分類doc |
| K16(neg3 HF-009「…the events driving oil prices—and the prices themselves—quickly returned.」) | **BLOCKING**(変更なし、見逃し0) | BLOCKING | 再分類doc |
| K18(A2A3-0、HF-003、支払う側の特定) | **BLOCKING**(変更なし) | BLOCKING | 再分類doc。V6が明示的にBLOCKING |
| K20〜K22(B4-a型、動機・機構の新規主張) | **BLOCKING**(境界、変更なし) | BLOCKING | 新しい具体的事実の追加(V7(1)(イ)で拾う) |
| B2(HF-009 因果連結"so") | QUALITY(変更なし) | QUALITY | — |
| B3(HF-007 因果"so")・A2A3-0・A4-0・A4-1・A5-0・B4-a・Safety12 | BLOCKING(変更なし) | BLOCKING | Safety-critical 6件+Safety12は不変 |

**食い違いの残り(報告事項、勝手に直していない)**:
1. K19: ユーザー決定はQUALITYだが、`changed_comparison`のfloor(`FLOOR_FLAGS`)は不変のため、Checkerがcomparisonフラグを立てるとLLM判定がQUALITYでもfloorでBLOCKINGになる(ユーザー指示「数値・主体・否定・比較・時期の機械的な安全装置は緩めない」を優先)。K19をfloorの対象から外すかはユーザー判断事項。
2. 「動機の帰属=QUALITY」(production `MATERIALITY_RUBRIC`)と§0-2・K20〜K22(動機の創作=重大)の食い違いは未解消(V7(1)(イ)で「新しい具体的事実の追加」として拾う設計。委任_55 3-4)。
3. 決定論的な降格(`DISCLOSURE_GAP_NEGATION_RE`)は否定形限定のまま(肯定形の許容はrubric本文のみ)。

### 7-1. Safety群(Stage 1/2で必ずBLOCKING維持、その後Rewrite→PASSが期待到達経路)

| fixture | 正解ラベル | 理由(floor/rubric) | 期待到達経路 |
|---|---|---|---|
| er009_changed_number/actor/negation/comparison/time(5種) | BLOCKING | deterministic safety floor該当(§4-3) | S1 BLOCK→S2 floor→BLOCKING確定(LLM判定を待たず)→S3 Rewrite→S1 Recheck→PASS |
| er009_changed_scope/causality/certainty/unsupported_new_claim(4種) | BLOCKING | floor対象外だがrubric基準1(Ledgerとの明示矛盾)に該当 | S1 BLOCK→S2 rubric判定でBLOCKING→S3 Rewrite→S1 Recheck→PASS |
| A2A3/A4/A5(実データ、価格反転・対象取り違え・意味反転) | BLOCKING | rubric基準1(Ledger矛盾) | 同上 |
| hormuz_run03_standard(HF-009 changed_scope) | BLOCKING(Confirmed) | rubric「scopeと矛盾」該当(Brent先物→市場全体への一般化) | S1 BLOCK(recall問題あり、§10リスク6/§14)→S2 rubric判定でBLOCKING→S3局所Rewrite→S1 Recheck→PASS |
| Meta_run03_standard(negative control) | **QUALITY(ユーザー決定2026-10-03、§7-0-iter33)**。旧: BLOCKING(〜2026-10-02) | 旧: rubric基準1。新: 線引きの正式採用(例1=軽微) | S1 BLOCK→S2 QUALITY通過(Rewriteしない) |

### 7-2. QUALITY群(Stage 2でQUALITY通過が期待、Rewrite不要、ただし要観察ログ)

| claim | 正解ラベル | 期待到達経路 |
|---|---|---|
| B2(料金案消滅と価格回復の因果連結) | QUALITY | S1 BLOCK→S2 rubric「Ledgerが保証しない関係付け」でQUALITY→継続(表現修正の余地は残すが自動Rewriteは強制しない) |
| B4-b(人間心理の一般論) | QUALITY(Trial扱い) | S1 BLOCK(過剰検出)→S2でQUALITY→継続 |
| B4-c(AI/人間判別関心の一般論) | QUALITY(Trial扱い) | 同上 |

### 7-3. ACCEPTABLE群(Stage 2でACCEPTABLE通過が期待、Rewrite不要)

| claim | 正解ラベル | 期待到達経路 |
|---|---|---|
| B1-a(ホルムズ海峡=重要航路) | ACCEPTABLE | S1 BLOCK(過剰検出)→S2 rubric「一般常識」でACCEPTABLE→継続 |
| B1-b(原油高→ガソリン等波及) | ACCEPTABLE | 同上 |

### 7-4. Real-but-fixable群(Stage 2でBLOCKING確定、Rewrite→PASSが期待到達経路)

| claim | 正解ラベル | 理由 | 期待到達経路 |
|---|---|---|---|
| B1-c(市場動機・価格回復理由の断定) | BLOCKING | HF-011 notesが因果推論を明示禁止 | S1 BLOCK→S2 BLOCKING確定→S3局所Rewrite→S1 Recheck→PASS |
| B3(接続詞so、政策決定理由の取り違え) | BLOCKING | HF-007 conditionsに別原因明記(rubric基準1) | 同上 |
| B4-a(AIフォールバック機構の新規主張) | BLOCKING | MUSE-HC-006の範囲外の製品仕様捏造 | 同上 |
| B4-d(テスト結果の確実性強化、V4A run) | BLOCKING(Trial扱い、fail-closed) | certainty変化、floor対象外、境界未確定のため安全側 | S1 BLOCK→S2 BLOCKING(fail-closed)→S3局所Rewrite→S1 Recheck→PASS。Stage 2が実際にQUALITYへ降格させた場合はその挙動を観測記録し、Phase 1実測後に正解ラベルの再検討材料とする(ラベル自体は今回変更しない) |

### 7-5. Normal群(Stage 1のみでACCEPTABLE到達が期待、既にAPI¥0で実証済み)

negative claim候補16件(`docs/pm/negative_claim_candidates_open233_
01.md`)。現行Production実行で既に`LEDGER_COMPLIANT`(deviations=[])
として通過した実績があるため、Self-Recovery Flow下でも**Stage 1のみで
ACCEPTABLE、Stage 2以降に到達しないことが期待**される正解ラベル=
ACCEPTABLE。ただしStandard/Advancedの表現断定度によって同一Ledgerでも
判定が割れる実例(候補1〜3 vs 同一runのAdvanced版B4 fixture)があるため、
非決定性により稀にBLOCKING-candidateとしてStage 2へ到達する可能性は
残る(その場合の期待到達経路: S1 BLOCK[過剰検出、非決定性]→S2で
ACCEPTABLE/QUALITYへ戻る→継続。16件全てのTrial扱い正解ラベルは
ACCEPTABLE、Stage 2到達は非決定性による例外扱い)。

### 7-6. Phase 1 Trial評価基準としての使い方

上記7-1〜7-5の「期待到達経路」を、Phase 1 Trial実行結果の合否判定基準
とする。具体的には: (1) 7-1(Safety群)は全fixtureが必ずBLOCKING確定を
経てRewrite→PASSへ到達すること(1件でもStage 2がACCEPTABLE/QUALITYへ
降格させたらSafety regressionとして即報告)。(2) 7-2/7-3(QUALITY/
ACCEPTABLE群)はRewrite無しで継続することが期待値だが、Stage 3が発火
しても即Safety事故ではない(過剰Rewrite=生産性課題として記録)。(3)
7-4(Real-but-fixable群)はBLOCKING確定→Rewrite→PASSの到達を確認する。
(4) 7-5(Normal群)はStage 1のみで完結することを確認する。

## 8. 測定項目の定義と算出方法

### 8-1. Self-Recovery 6項目

| 項目 | 定義 |
|---|---|
| Initial BLOCK件数 | Stage 1がBLOCKING-candidateを返した回数(writer-stage-instance単位、Advanced/Standard別カウント) |
| Re-screening自動解消件数 | Stage 2がQUALITY/ACCEPTABLEを返し、Stage 3を経ずに継続した件数 |
| Rewrite進行件数 | Stage 2がBLOCKING確定し、Stage 3が発火した件数(cycle 1・2の合計) |
| Rewrite自動解消件数 | Stage 3実行後のStage 1 RecheckでACCEPTABLE/QUALITYになった件数 |
| Final STOP件数 | Stage 4へ到達した記事数(cycle上限到達またはJA Fact Check STOP) |
| USER_DECISION_REQUIRED件数 | Final STOPのうち実際にユーザーへ提示した件数(通常はFinal STOP件数と一致する設計だが、将来同一記事内の複数STOPを集約提示する場合に備え区別して定義する) |

**[委任_04新設/A13] Escalation 0件・Rewrite解消・QUALITY通過の内訳
測定項目(必須、Trial報告テンプレートにも必須項目化、Opus論点8推奨1/3
への対応)**:

| 項目 | 定義 |
|---|---|
| Escalation 0件の内訳 | 「真の解消」(Stage 2降格またはRewrite解消で`all_prior_issues_resolved==True`により裏付けられた件数)/「QUALITY通過」(Stage 2がQUALITYを返し継続した件数)/「`all_prior_issues_resolved`未確認」(Recheckで`overall_status`のみ確認し`all_prior_issues_resolved`を未実装・未確認のまま継続した件数、A1適用前の旧経路が残っていないかの検出用)/「誤PASS候補」(同一claimがRecheckで無言消滅した[前回BLOCKINGだったclaimがdeviation自体として出力されなくなった]件数)に分類し、全てを報告する |
| Rewrite自動解消件数のうち`all_prior_issues_resolved==True`裏付け件数 | Rewrite実行後のRecheckで`all_prior_issues_resolved==True`が実際に確認された件数(§3-0/§6-1のA1適用結果) |
| QUALITY通過件数・claim内容 | Stage 2がQUALITYを返した件数と、該当claim本文(Opus論点8(B)の「品質下限が下がっていないか」を人間が事後確認できるようにする) |

### 8-2. QCD 7項目

| 項目 | 算出方法 |
|---|---|
| Checker call数/記事 | Stage 1(Advanced+Standard)+Stage 2の合計call数の記事平均 |
| Rewrite回数/記事 | Stage 3発火回数(cycle数)の記事平均 |
| 平均追加cost | (Self-Recovery Flow総費用 − Stage 1のみのベースライン費用[既存Production実測])の記事平均 |
| P50/P95 latency | 記事1本の全Stage合計wall-clock時間の中央値・95パーセンタイル |
| completion率 | Stage 4に到達せず継続(ACCEPTABLE/QUALITYで完結)した記事の比率 |
| retry率 | Stage 3が1回以上発火した記事の比率 |
| loop率 | Stage 3のcycleを2回とも消費した記事の比率(上限接近度の指標) |

### 8-3. 不要BLOCK率(診断指標、主要受入条件ではない)

Opus論点2推奨1に従い、claim単位で再定義する(委任_03で用語統一):
`不要BLOCK率 = 正解ラベル=ACCEPTABLE/QUALITYのclaim(§7-0)がStage 1で
BLOCKING判定された率`。目標値は
設定せず(前Phaseの≤25%は撤回、診断のみ)、Self-Recovery Flowが
False・borderline群をどれだけStage 2で正しく拾えているかの内部指標
として参照する。

### 8-4. Stage別コスト計測(委任_02追加、2026-09-30ユーザー追加指示)

継続コストCap(§13)判定のため、記事単位ではなくStage単位で以下を
分離して計測する(全てTrial harnessが`usage`ログへstage識別子付きで
記録する。§9-3参照)。

| Stage | 発動率(対象母数) | 1回コスト(call単位、$/1M単価から算出) | 1記事平均追加コスト | worst case | P50/P95 |
|---|---|---|---|---|---|
| Stage 1 Initial Check | 100%(writer-stage-instance単位、Advanced/Standard別) | ○ | ○(既存ベースライン、Self-Recovery追加費ではない) | ○ | ○ |
| Stage 2 Re-screening | BLOCKING-candidate発生時のみ | ○ | ○ | ○ | ○ |
| Stage 3 Rewrite(局所EN/JA全文) | Stage 2でBLOCKING確定時のみ | ○(JA/EN別) | ○ | ○ | ○ |
| Stage 1 Recheck | Rewrite実行時のみ(cycleごと1回、JA全文Rewrite時はAdvanced+Standard 2回分) | ○ | ○ | ○ | ○ |
| cycle 2(Stage2+Rewrite+Recheckの再発火) | cycle 1で解消しない場合のみ | ○ | ○ | ○ | ○ |

**固定費(毎記事必ず発生)と条件付き費(BLOCK時だけ発生)の分離**:
固定費=Stage 1のみ(既存ベースライン、Self-Recovery Flow導入によって
増減しない)。条件付き費=Stage 2以降の全て(BLOCKING-candidateが
発生した場合のみ発火し、Stage 1がACCEPTABLEを返した大多数の記事では
追加費用¥0)。この分離が§13のCap計算の前提。

### 8-5. iteration4追加測定7項目(委任_12、§2項目5)

ユーザー指示(§1)「余計に直さず、安く、安全に通せるか」を評価するため、
`er052_open233_self_recovery_flow_runner_01.py::_iter4_additional_
measures`/`compute_s1u_counterfactual`として実装(既存measurementの
key/値は変更しない追加ブロック)。

| # | 項目 | 定義 | 対象母数 |
|---|---|---|---|
| 1 | 正常記事の不要Rewrite件数 | `NORMAL_GROUP_INSTANCE_IDS`(negative候補7件+Normal群2件[hormuz_run03_advanced/meta_run03_advanced]、§7-0-iter4で全claim ACCEPTABLE期待)のうち、1回以上Rewrite(`rewrite_records`)が発火した件数 | 正常記事9 instance |
| 2 | 同・率 | 1/9 instance | 同上 |
| 3 | 自然な解釈なのにBLOCKされた件数(Stage1) | 正常記事のうちStage1が`ACCEPTABLE_STAGE1`以外(BLOCKING-candidate)になった件数 | 同上 |
| 4 | 同(Stage2) | 正常記事のStage2 claim単位判定のうち`materiality=="BLOCKING"`だった件数 | 同上(claim単位) |
| 5 | Rewrite前後で読み物品質を損ねた候補数 | `measure_rewrite_quality_degradation`(決定論): 文数減少率≥20%、または弱め表現[may/might/possibly/perhaps/could/seem/appear]増加数≥3、または段落数減少、またはタイトル(先頭行)変更、のいずれかに該当する場合を「候補」とする(人間の主観評価の代替ではない、候補提示のみ) | 全Rewrite発火cycle(EN/JA別) |
| 6 | Rewrite回数/記事 | 記事単位(Standard+Advanced合算、`ARTICLE_GROUPS`)のRewrite発火総数の平均 | 全instance |
| 7 | 自動Recovery理由内訳 | `stage4_reason`別件数(`cycle_limit_exhausted`/`same_claim_fact_id_reblocked`/`unconfirmed_after_reverify`等) | STAGE4到達instance |
| 8 | 記事単位(Standard+Advanced合算)追加コスト | 既存`article_level`(§9-1⑦で導入済み)を再利用、iteration4でも継続測定 | 全instance |

**S1-Uあり/なし比較(0 call、反実仮想)**: `compute_s1u_counterfactual`
は、`s1u_additional_block==True`のinstance(S1-Uが追加BLOCKINGを
検出したinstance、Stage1本体がACCEPTABLEを返した場合のみ発火する
既存設計[§3-1]により、このinstanceの以降の全cascadeはS1-U起因と
機械的に特定できる)を`ACCEPTABLE_STAGE1`(cost 0・call 0)へ置換した
反実仮想measurementを、既存`aggregate_measurements`をそのまま再適用
して算出する(新規API callなし)。**解釈上の注意**: 反実仮想の
escalation rateが実測と同一であっても、それは「安全に非該当だった」
ことを意味しない場合がある(S1-Uが無ければ沈黙裏にACCEPTABLE_STAGE1
として見逃されていた既知recall missが、反実仮想でも同じく
ACCEPTABLE_STAGE1として現れるため)。`known_recall_miss_instances_
among_removed`(既知recall miss instance IDのうち反実仮想で除外された
もの)を必ず併記し、rate単体で「S1-U不要」と誤読させない。

### 8-6. 品質劣化検出v2(委任_13、Opus L2レビュー#3論点6-B)

**背景**: iteration4実測で実際に起きた4種類の読み物品質劣化(neg1の
hook喪失+cycle2の重複段落、neg2の接続破断、neg3/neg5/B2の語彙難化)の
うち、v1指標(文数/段落数/hedge語数/タイトル変更、§8-5項目5)は3種を
検出できなかった(hook喪失=タイトル変更としては検出したが、失われたもの
の本質[物語の入口]を表していない。重複段落・接続破断・語彙難化はいずれも
検出漏れ)。

**v2検出項目**(`measure_rewrite_quality_degradation_v2`、決定論・¥0、
v1関数は変更せずiter4比較用に残す):
| # | 項目 | 定義 |
|---|---|---|
| (a) | 連続段落の重複検出 | 正規化後token Jaccard類似度が閾値(0.4、実測でこの値でないとneg1 cycle2の実例[jaccard=0.5]を検出できないため当初案0.6から調整、同一記事内の他の隣接段落ペア12組の実測では最大0.292で次点との差が明確、過検出リスクは低いと判断)以上の隣接段落ペアを検出する |
| (b) | 孤立逆接語検出 | 段落先頭がBut/However/Yet/Still/Though/Nevertheless等で始まり、かつRewrite前にはその段落が存在しなかった(新規に生じた)場合を検出する |
| (c) | 文長・難語率比較 | 音節数(母音塊カウント)>=3または文字数>=9の語を「難語」とみなす簡易ヒューリスティックで、平均文長・難語率をRewrite前後で比較する。全文平均では局所的な1文だけの難語化が希釈されて閾値未満になることを実測確認したため(neg3/B2実例)、実際に書き換えられた断片(`changed_fragments`、single_text_rewrite/paired_rewriteが返すbefore_fragment/after_fragment)同士でも比較し、全文判定・断片判定のいずれかが閾値(文長+3語、または難語率+0.05)を超えれば検出する |
| (d) | タイトル・第1段落(hook)変更 | 常時フラグとして報告する(BLOCKING claim自体がそこにある正当なケースがあるため、単独では再生成トリガにしない) |

(a)(b)(c)のいずれかを検出した場合のみ`needs_regeneration=True`とし、
§5-6の同一cycle内1回だけの再生成をトリガする。regression test
(iteration4実測の実テキストをfixtureとして固定、`er052_open233_self_
recovery_flow_runner_01_test_01.py::TestMeasureRewriteQualityDegradationV2`)
で(a)(b)(c)を検出できることを固定した。

### 8-7. iteration6追加測定(委任_14、2026-09-30ユーザー新方針item8/9)

**不要Rewrite率(主要指標)**: 既存`unnecessary_rewrite_v2_corrected`
(iteration5、neg5除外済み)と同一定義を正常記事群(negative7+Normal群2)
へ適用し、`unnecessary_rewrite_v3`として継続測定する(定義自体は
変更しない、instance集合がiteration6で一部欠落した場合[Guardrail到達等]
は分母を実際に完走したinstance数へ機械的に合わせる)。

**ラダー段別分布**(§5-7): `rewrite_records`の`ladder_level_used`
(`0_delete`/`1_word_connective`/`3_sentence`/`4_paragraph`/
`6_full_article`/`paired_j1_not_laddered`)を集計し、どの水準で
解消したかの分布を報告する。

**セクション役割違反件数**(§5-7): `section_role_violation.
section_role_violated`をcycle単位で集計する。

**Hook由来BLOCK回避件数**(§6-4): `floor_reason ==
"hook_aware_scope_downgrade"`のclaim数を集計する。

**丸め誤検出回避件数**(§4-12): `dev.changed_number_suppressed_reason`
が記録されたclaim数を集計する。

**floor-strict/floor-cited比較**(§4-13): `floor_cited_materiality`/
`floor_cited_reason`をfloor-strictの実際の判定と突き合わせ、divergence
(floor-strictは発火したがfloor-citedは発火せず、かつLLM自体の判定も
BLOCKINGでなかった)件数をSafety群/全群別に報告する。

**コスト5分割**(item9、平均+¥2/記事を上限指標、目標値ではない):
`compute_cost_breakdown_5way`(instance単位、¥0・既存`total_cost_jpy`/
`rewrite_records`の再集計のみ)が、Rewriteなし記事平均/Rewriteあり記事
平均/Rewrite率/全記事平均/worstの5値を算出する。`combine_n2_measures`
にも`iter6_additional_measures_combined`として統合した(n=2結合値、
両sampleのinstance_resultsを単純連結して集計、既存article_level
[Standard+Advanced合算]集計とは別枠のinstance粒度集計)。

### 8-8. `silent_pass_candidate`自動検知への置換(委任_33、REPORT§31)

委任_32(iter8、§7-0-iter32)で、`aggregate_measurements`内の
`escalation_zero_breakdown.silent_pass_candidate`が常に`0`を返す
非稼働プレースホルダであり、B3/A2A3-0の誤降格2件はSAFETY_CRITICAL_
SUB_IDS(r3d、8claim名指しリスト)との**手動照合**で初めて検出できた
ことが開示された。本委任で、この手動照合を機械的な後処理関数
(`detect_safety_critical_misdowngrades`、`er052_open233_self_recovery_
flow_runner_01.py`)へ置き換えた。

**実装**: `SAFETY_CRITICAL_CLAIM_DEFS`(instance_id→[{sub_id,
related_fact_id, text_substring}]の固定マップ、r3d.SAFETY_CRITICAL_
SUB_IDSの8claim全件をg6フィクスチャの実データ[`s2c.build_eval_groups()`
・各fixtureのV4A rerun結果]から書き起こした逐語データ)と、各instanceの
cycle別`stage2_results`(claim_text/related_fact_id/materiality、
既存run_instanceが既に保存している実測値)とを自動照合し、最終
materiality(floor/hook/disclosure-gap適用後の実効値)がBLOCKING以外に
なった箇所を機械的に検出する(¥0、新規API呼び出しなし、既存結果json
への後処理のみ)。related_fact_idがinstance内で複数sub_idに共有される
ケース(`safety_A5`のA5-0/A5-1がともにMUSE-HC-012)があるため、
claim_textの逐語核心句との併せ技で誤マッチを防ぐ(unittest
`test_no_false_positive_for_unrelated_fact_id_same_instance`で確認)。

`escalation_zero_breakdown.silent_pass_candidate`は、検出行を
`(instance_id, sub_id)`で重複排除した件数を返すよう置き換えた
(`silent_pass_candidate_rows`に詳細行も併記)。委任_32のiter8実データ
(`er052_output/open233_self_recovery_flow_runner_01_iter8/`)へ本関数を
適用すると、B3(`bgroup_B3`、2/2)・A2A3-0(`safety_A2A3`、sample2のみ)が
自動検出されることをunittest(`test_iter8_real_data_detects_exactly_
two_misdowngrades`)で確認した。rep18(§4-25)のfull flow再実行では
`safety_critical_misdowngrade_count_distinct=0`(誤降格再現なし)。

unittest: `TestSafetyCriticalMisdowngradeDetection`(8件、合成
instance_resultsによるregression + iter8実データでの実測確認)。
既存281件+本委任新規11件(V6 rubric 3件+misdowngrade detection 8件)=
**計292件全PASS**。

## 9. Trial計画

### 9-0. Phase 1実行前チェックリスト([委任_04新設]、A1〜A13が設計へ
反映済みかの機械的確認。実行前に全項目を確認する)

| # | 項目 | 反映節 | 確認 |
|---|---|---|---|
| A1 | Recheckに`prior_issues`を渡し継続条件=`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved==True` | §3-0/§6-1 | 済 |
| A2 | precheck由来検出はfloor扱い(`detected_by`フィールド、Stage2降格不可、FP率次第で弱め分岐) | §3-1/§4-3 | 済 |
| A3 | precheck FP率¥0測定をPhase1最初に置く | §9-1① | 済 |
| A4 | origin=ja_sourceにEN局所Rewrite不適用、paired local rewriteをPhase1第一級項目へ | §5-1/§5-2/§5-3/§5-4 | 済 |
| A5 | cycle2発火条件に「cycle1と異なるclaim/fact_id」追加 | §3-3/§5-3/§6-1 | 済 |
| A6 | §13-6を式へ書き換え、二重計上精査、JA-origin比率実測反映 | §13-6 | 済 |
| A7 | Stage4条件表をコード上の例外型と1対1対応 | §6-1 | 済 |
| A8 | Stage2入力からexplanation/severity/10 flagsを除外、ヘッジ語regexで段落範囲拡張 | §4-4 | 済 |
| A9 | Stage2をinstance単位1 callへbatch化(主案)、per-claim比較対照 | §3-5/§4-1(§9-1④) | 済 |
| A10 | rubric ACCEPTABLE定義明文化、changed_certaintyをfloorへ | §4-2/§4-3 | 済 |
| A11 | rewrite_hint schemaに`rewrite_kind`追加、機械検証追加、guard抵触時の段階的フォールバック | §4-5/§5-2 | 済 |
| A12 | prompt caching受理可否・削減率をPhase1で実測 | §9-1④/§13 | 済 |
| A13 | Escalation 0件内訳等の測定項目必須化 | §8-1 | 済 |

### 9-1. Phase 1(既存fixture/artifact reuse、次回委任で実施。
**[委任_04改訂/A3・A14・A15]** 実測項目の優先順序を以下①〜⑥へ確定)

**目的**: Stage 2/Stage 3の設計が既存fixtureに対して機能するかを検証
しつつ、**モデル非依存の構造的結論(prior_issues併用・pre-check FP・
JA/EN乖離ルール・call数/batch/caching)を、モデル依存の結論(Stage1
variant最終確定)より先に確定させる**(Opus論点8推奨4、A15)。Stage 2
評価はV4-A由来レコードに限定する(V2/V3混在を排除、Opus論点8(C))。

**① precheck FP率実測(¥0、最優先)** **[委任_06実測完了]**: 既存
`LEDGER_COMPLIANT`(deviations=[])記事28件のうち、既存の逆展開ユーティリティ
(`er050_gpt6_checker_comparison_trial_01.extract_inputs_from_prompt`)で
再構成できた20件(残り8件はJA writerのretry後attempt[`prior_issues`
instructionを含むprompt]であり、当該ユーティリティが未対応のため対象外、
既知の限界として記録)にdeterministic pre-check(`er052_open233_self_
recovery_precheck_01.py`)を適用した。**記事単位FP率=0/20=0%**(finding単位
0件)。実装は反復修正を経ている(初回実装では小物Ledger[F001-F018]記事2件
[a2/b1b]でactor_missing誤検知10件が発生。原因は(a)所有格差[`Celine's`
vs Ledgerの`Celine`]の非正規化、(b)Markdown見出し内のTitle Case連続語を
複合固有名詞と誤認、(c)文頭大文字化された一般語[`Can`/`Looking`等]の
誤検出、(d)同一Ledgerの別Factが持つ数値・日付・語彙を「別Factの主体・
値」と正しく除外できていなかったこと。(a)〜(d)を全て補正するregression
testを`er052_open233_self_recovery_precheck_01_test_01.py`へ追加した上で
再測定し0%を確認した)。design書§3-1が定めた判断基準(記事単位FP率が
10%超なら「Stage 2強制送付[棄却可]」の弱い分岐へ切替え)に照らし、
**0%(10%を大きく下回る)のため、precheckのfloor扱い(§3-1/§4-3の強い
分岐、Stage 2をスキップし直接BLOCKING確定)をそのまま維持する**。
Safety群(er009 9種+A2A3/A4/A5、計12件)への適用では、precheck単独の
検出率=1/12(8.3%、`er009_changed_number`のみnumber_mismatchで検出)。
残り11件は非検出(構造的理由: er009系Ledgerの一部[ER-006 pool形式]は
actor名が`claim`ではなく`source:`引用行にのみ存在し、現行の正規表現は
`claim`等の主要フィールドのみを走査するため対象外。changed_scope/
causality/certainty/negation/comparison/time/unsupported_new_claimは
意味的判断が必要でありdesign書§14-4の既知の限界どおり機械照合不可)。
これは想定どおりであり、precheckはStage 1 LLMの代替ではなく補完層で
あることを裏付ける。**費用¥0(API呼び出しなし)**。詳細ログ:
`er052_output/open233_self_recovery_precheck_01/phase1_step1_fp_rate.json`
/`phase1_step1_safety_group_detection.json`。

**② hormuz n=20見逃し3 attempt補完実験(¥0〜数円)** **[委任_06実測完了]**:
hormuz_run03_standardのn=20 stability実測(`er051_output/open233_
checker_trial_01/trial_03_stability_n20/`)でV4-Aが非検出だった3
attempt(attempt 8/13/14、いずれもprompt_sha256が同一=同一入力に対する
繰り返し測定)を特定した。(a) precheckを適用した結果、**非検出**
(0 findings、期待どおり。HF-009 changed_scope[Brent先物→石油市場全体
への一般化]は意味的逸脱であり機械照合対象外という§14-4の既知の限界を
裏付ける)。(b) Stage 1出力を一切見せない独立Stage 2診断Prompt
(`er052_open233_self_recovery_stage2_01.py`、gpt-6-luna、§4のrubricを
継承しStage 1出力なし版に適合させた新規Trial実装)を、当該記事(全文)+
Ledger全文+JA原文へ3 call適用した結果、**3/3(100%)がHF-009を
`materiality=BLOCKING, basis=ledger_scope`として独立に検出**した(3回とも
"HF-009 establishes the reported movement for Brent[crude futures]
only... does not establish...oil market[generally]"という同一趣旨の
理由付け)。**Stage 1のrecall欠落[85%→n=20中3件]を、独立したStage 2
診断が3/3で埋められることを実データで確認した**(design書§11-5/§14-4
が示していた「Self-Recovery Flowで解決されない構造的限界」への実証的な
反証材料。ただし本実験はStage 1がBLOCKINGと判定した後にのみStage 2が
発火する通常設計[§3-0]の前提を外した診断目的の特例であり、そのまま
Production設計へ組み込めるわけではない[全記事へ常時2nd Checkerを回す
運用コストの問題は§14-4「PASS時の限定2nd run」不採用の理由と同じ]。
Phase 2での扱いは§11-5への追記候補とする)。**費用**: Stage 2診断3call
合計¥0.6285(単価¥0.185〜0.225/call、gpt-6-luna実測)。3/3で結果が
一貫していたためn=2への拡張(computed guardrail上限¥2に対し実測は
その約1/3)は行わなかった。詳細ログ:
`er052_output/open233_self_recovery_phase1_hormuz_followup_01/summary.json`。

**③ V4-A BLOCK率増分+changed_actor有意性実測(¥1.5〜3+¥6=約¥8〜9)**
**[委任_07実測完了]**: 当初計画のV0/V4-A 2variant比較に加え、ユーザー
方針(既存方式に縛られないQCD比較)に基づき**S1-D(一体型、§14-2で
理論上不採用としていたものを実測対象へ追加)**を同一fixtureで比較した
(実測結果・費用内訳は§14-5参照)。(a) Safety群12 fixture: S1-D
12/12(100%)、費用¥3.0542。(b) `er009_changed_actor` n=15追加実測:
V0=7/15(46.7%)・V4-A=15/15(100%)・S1-D=15/15(100%)、Fisher検定
V0 vs V4-A/S1-D共にp=0.00220(有意)。(c) negative候補7記事BLOCK率:
V0=0/7・V4-A=4/7(57.1%)・S1-D=6/7(85.7%、V4-Aより過剰BLOCK)。
(d) B群5 fixture claim単位ラベル一致: S1-DはB3/Meta_run03_standardで
確定ラベルと一致したが、B1/B4でReal-but-fixable群(B1-c/B4-a)を
QUALITYへ誤降格させる実例が観測された。(e) hormuz/Meta n5:
S1-D=10/10(100%)。**Stage 1最終確定: V4-A(変更なし、S1-Dは不採用、
根拠§14-5)**。費用: (a)¥3.0542+(b)¥4.0283+(c)¥3.3103+(d)¥1.2379+
(e)¥1.8927=**¥13.5234**(76 call)。

**④ Stage2実単価/batch化/prompt caching実測(数円〜¥10程度)**
**[委任_07実測完了]**: per-claim call vs instance単位batch call
(B4=4claim/B1=2claim、gpt-6-luna、`er052_open233_self_recovery_
stage2_production_01.py`新規実装、§4-4確定入力どおり)を実測した
結果、判定一致率100%(claim間相互汚染なし)・batch化でcall数/費用
(55%減/29%減)/latency全てが改善(§4-7)。prompt caching受理可否も
実測確認(cached_input_tokens比率99.9%、費用削減率63〜64%、§4-7)。
**[委任_07新規発見]** per-claim Stage2でReal-but-fixable群
(B1-c/B4-a)がQUALITYへ誤降格される較正リスクを発見(S1-D実測と
独立に同一方向の誤判定、詳細§4-7)。費用¥1.1364(12 call)。

**⑤ Stage3型別Rewrite成功率実測(約¥8〜22)** **[委任_08実測完了]**:
delete型(B1-c/B3/B4-a、決定論的削除+Recheck)・replace_with_ledger_
value型(er009_changed_actor/changed_number、E-1 vs E-2)・narrow_scope
型(hormuz_run03_standard HF-009、J-1 vs J-2)を実測した。delete型は
単一deviation記事(B3)でresolved=True、複数deviation記事(B1-c/B4-a)は
記事全体Recheckが他claim残存のためLEDGER_DEVIATIONのまま(claim単位の
再出現確認は次回実装項目)。replace型はE-1/E-2とも4/4(100%)が
1 attempt目で解決、cost差僅少。**narrow_scope型はJ-1が完全解消
(resolved=True、drift 0件)、J-2は未解消(EN Recheck LEDGER_DEVIATION
のまま、非対象文drift 1件検出)**。採用案: narrow_scope=J-1、
replace_with_ledger_value=E-2第一候補(E-1はfallback)。詳細は§5-4-補2。
費用¥3.0363(18 call、Guardrail¥30のうち)。

**⑥ 統合dry-run実測(委任_09完了)**: ①〜⑤の確定設計(V4A Stage1・R2
rubric+floor・narrow_scope=J-1/replace=E-2・cycle上限2・A1/A5/A7)を
1本のTrial runner(`er052_open233_self_recovery_flow_runner_01.py`+
test)へ統合し、29 instance(Hormuz run_01/run_02 Advanced各1[現行
Production STOP実例、Standardは同run内で未生成のため対象外]・run_03
Advanced/Standard、Meta run_03 Advanced/Standard、B群4[B1/B2_hormuz/
B3/B4]、negative候補7、Safety群12[er009 9種+A2A3/A4/A5])で通し実行
した(92 call、¥16.7806、0 error、Guardrail¥45の約37%)。

**Self-Recovery 6項目(instance単位)**: Initial BLOCK=23/29、
Re-screening自動解消=1(hormuz_run01_advanced、HF-006「一般的な経済
連動性の言及」をStage2がACCEPTABLEへ正しく降格、Rewrite不要で現行
Production STOPを自動回避=設計が目指す典型的成功例)、Rewrite進行=22、
Rewrite自動解消=13(RESOLVED_REWRITE=11[`all_prior_issues_resolved=
True`確認済み]+RESOLVED_REWRITE_THEN_DOWNGRADE=2)、Final STOP=9、
USER_DECISION_REQUIRED(Stage4到達)=9(全件到達理由=
`same_claim_fact_id_reblocked`、cycle 2で同一fact_id再BLOCKingを検出
し即STOPというA5設計どおりの動作)。

**0件の内訳(A13)**: 真の解消(`all_prior_issues_resolved=True`)=11、
QUALITY通過=0(本評価セットでQUALITY止まりのまま継続したclaimは無く、
全BLOCKING-candidateがRewrite対象化または非BLOCKING降格のいずれかへ
分岐)、`all_prior_issues_resolved`未確認=0、誤PASS候補=0(全件Recheck
で明示確認、無言消滅なし)。

**重大Fact見逃し(Stage1 recall、Safety観点で最重要の発見)**: V4A単発
実行(n=1)で、Real-but-fixable/Safety隣接群のうちB2_hormuz・B3・
**hormuz_run02_advanced(現行Production STOP実例そのもの)**の
3 instanceで、既知のBLOCKING claim(HF-011/HF-007/HF-011相当)が**一切
検出されずLEDGER_COMPLIANTとなった**(§10/§14既知の「Stage1 recall
欠落」リスクが、統合dry-runで実データ3件同時に再現)。B2_hormuz/B3は
`baseline_parsed`(実Production V0、既にMAJOR検出済み)へ代替して
Stage2/3経路自体は検証したが(代替の事実を`stage1_recall_miss_
substituted=true`として明記)、**hormuz_run02_advancedは代替を適用
せず、素の結果としてACCEPTABLE_STAGE1で完結した**(Self-Recovery
Flow自体が発火する前にStage1が見逃したため、Stage2/3では捕捉不可能な
既知の構造的限界の実例)。floor機構自体はfloor適用対象48 BLOCKING
claim中0件のfalse-negativeを維持したが、**Stage1自体の検出漏れは本
設計の範囲外であり未解決のまま**。

**QCD(instance単位)**: 総call数92、総費用¥16.7806、平均追加cost/
instance=¥0.5786(全29)/¥0.7118(BLOCKING発生23件のみ)、P50=¥0.377
(全29)/¥0.5918(BLOCKING23)、P95=¥1.9421、worst=¥2.2721(safety_A4、
3claim分のJ-1/E-2 rewrite)。**worst caseでも+¥3/記事Capを下回った**
(§13-7のCap判定を実測で裏付け)。latency P50=17.27秒/P95=143.5秒。
completion率=69.0%(20/29、Stage4未到達)。retry率=75.9%(22/29で
Rewrite発火)。loop率=41.4%(12/29でcycle上限2まで消費)。

**現行Productionとの対比(Hormuz 3記事)**: run_01 Advanced=現行STOP→
本フローはRewrite不要でRe-screening自動解消(ACCEPTABLE)。run_02
Advanced=現行STOP→本フローは**Stage1 recall missによりACCEPTABLE_
STAGE1**(見かけ上「解消」だがStage1が見逃しただけでありSelf-Recovery
Flowの機能とは無関係、上記重大Fact見逃し参照)。run_03 Standard
(HF-009)=現行STOP→本フローは**STAGE4_ESCALATION**(cycle2で同一
fact_id再BLOCKing、J-1汎用ロケータが対象文特定に失敗
[`j1_pair_not_located`]、委任_08の手動アンカー実験[J-1が100%解消]を
汎用実装では再現できず)。

**事象(claim)単位の段階別成功率**: floor後BLOCKING確定claim48件
(cycle1+cycle2合計)のうちRewrite実行33件、初回cycleで再発せず解消=
20/33(60.6%)。機構別: `deterministic_delete`=1/1(100%)、
`e2_generic_rewrite`(単一言語E-2)=13/18(72.2%)、`target_not_found+
fulltext_fallback`=3/3(100%、全文最小編集フォールバックが有効に機能)、
`paired_ja_en(J-1)`全体=3/11(27.3%)、うち`j1_paired_rewrite`(対象文
特定に成功した場合)=2/3(66.7%)、`j1_pair_not_located`(対象文特定
失敗)=1/7(14.3%)。**J-1機構の対象文特定(汎用JA/EN文分割・対応付け)
が本統合runで最大の失敗要因**(11回中7回[63.6%]が対象文特定自体に
失敗)。Escalation率のWilson 95%上限(instance単位9/29=31.0%、
95%CI=[17.3%, 49.2%])。

**Stage4到達9件の原因分類**:
(a) **J-1対象文特定失敗**(汎用ロケータの限界、§5-4既知の限界の実測
裏付け)= safety_A2A3(2claim)・bgroup_B2_hormuz(1)・bgroup_B4(2/4claim)
・meta_run03_standard(1/2claim)・hormuz_run03_standard(1claim)の計
5 instance。
(b) **局所編集は実行された(guard_ok=True)がRecheckが引き続き
LEDGER_DEVIATION**(Rewrite内容が実質的にLedger適合しなかった)=
safety_A4(3claim中2claim再発)・bgroup_B1(1claim)・neg1/neg2(各1claim)
の計4 instance。

**(b)の根本原因(新規発見、報告のみ・独断で修正せず)**: **Stage2出力
schema(`er052_open233_self_recovery_stage2_production_01.py::
_ITEM_PROPS`)に、design書§4-5が要求する`rewrite_hint`(自由記述、
BLOCKING時必須)フィールドが実装されていない**。本runnerはやむを得ず
`rewrite_hint`代替として`f"materiality={...}, basis={...}"`という
空疎なplaceholderをE-2 Promptへ渡しており、実際に「何をどう直すべきか」
という具体的指示がRewrite LLMへ渡っていなかった。既存個別実験
(委任_08のstage3_rewrite_trial)は各fixtureのrewrite_hintを人手で
作文していたため、この欠落は独立実験では顕在化せず、**統合dry-runで
初めて発見された**。次回実装候補: Stage2 batch schemaへ
`rewrite_hint`(string、BLOCKING時必須)を追加し、Stage3 Prompt側で
実際に使用する。

**[最重要の是正発見]negative群R2 Productivity評価のやり直し**: 委任_08
のStage2較正Trial(`er052_open233_self_recovery_stage2_calibration_01.
py::build_eval_groups()`)のnegative群4 fixture(neg1/neg2/neg3/neg5)
は、`fx["baseline_parsed"]["deviations"]`(実Production V0の記録、
これらのfixtureは定義上`deviations=[]`=LEDGER_COMPLIANT)からclaim_
textを取得しようとしたため`devs`が空となり、**`claim_text="(claim
not found in baseline)"`という無意味なplaceholder文字列がStage2へ
渡っていた**(該当コード行確認済み)。この結果、既報告の「negative群
R2で7/8(87.5%)が非BLOCKINGへ復帰」は、**実際にV4Aが誤検出した本物の
claim文言ではなく、空のplaceholder文字列に対するStage2判定を測定して
いた**ため、Productivity評価として妥当性を欠く。本統合dry-runは
(Stage1のreuse元がV4Aの実出力そのものであるため)実際の誤検出claim
文言をStage2へ正しく渡しており、**同じ4 fixture(neg1/neg2/neg3/
neg5)の実測結果は「Stage2単独でBLOCKING非該当へ降格した件数=
0/4(0%)」**(全4件がBLOCKING確定、うち2件[neg3/neg5]はRewriteで
自動解消、2件[neg1/neg2]はStage4へ到達)。**既存DECISION_LOG/
REPORT§7/本設計書§4-8のnegative群測定値(87.5%)は撤回・訂正しない
(履歴改変禁止、既存エントリはそのまま保持)が、本節で実測に基づく
訂正値を明記し、Phase 2計画・Opus L2 #2論点へ引き継ぐ**(新しい仕様
変更の実装はしない、報告のみ)。

**その他観測**: negative群7件中3件(neg4/neg6/neg7)はStage1(V4A)自体
でACCEPTABLE(過剰検出なし)、残り4件(neg1/neg2/neg3/neg5)全件が
Stage1で過剰BLOCKされ、そのうちStage2も全件BLOCKING確定(over-block
是正0%)。Stage2出力の`basis`は"unsupported_relationship"に強く偏り
(BLOCKING確定48件中28件[58.3%])、`rewrite_kind`は"narrow_scope"に
強く偏る(33件/48件[68.8%])。rewrite_hint欠落と合わせ、Stage2較正
(R2)の出力多様性そのものにも改善余地がある(Phase 2候補)。

**実装上の不具合発見・修正(報告)**: 統合runの実行中、
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`(委任_08
既存資産)の`simple_llm_call`をそのまま呼び出すと、そのモジュール自身
の`save_budget_state`が**既存委任_08の証跡ファイル(`budget_state_
c233l_b.json`)を上書きする**実害を検出した(`git diff`で発覚、
`git checkout`で復元済み、既存証跡データの実質破損なし)。本runner
自身の独立した`simple_llm_call`実装へ差し替え、再発防止のregression
test(`er052_open233_self_recovery_flow_runner_01_test_01.py::
TestNoCrossModuleBudgetStateContamination`)を追加した(この修正は
Stage1/2/3の判定ロジック自体には影響しない。実測結果[92 call・
¥16.7806・0 error]はこの修正前後で同一)。

**スコープ上の限界(既存委任_08と同一、再掲)**: J-1/J-2型のJA Fact
Check/EN RecheckはV4A variant checker代用、汎用JA文分割は簡易実装の
まま(§5-4-補2)。E-1 fallback(replace_with_ledger_value型)は本統合
runでは未実装(§5-4-補2でE-2を第一候補・E-1をfallbackと確定したが、
fixture横断的なper-claim機械検証[verify_fn]が個別実装を要するため、
全文Recheckのfail-closed判定に委ねる設計とした。次回実装候補)。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
worst case実測¥2.2721は+¥3/記事Cap未超過[条件3]。Stage1 recall
miss・negative群Productivity訂正はいずれもSafety「緩和」ではなく既知
リスクの実測確認・既存測定の透明な訂正であり条件2には該当しない
[Safetyはfloor機構により48件中0件のfalse-negativeを維持]。Rewrite
mechanism改善提案はいずれも未実装のTrial改善候補でありProduction
採用[条件4]には未到達)。

詳細ログ: `er052_output/open233_self_recovery_flow_runner_01/
summary_flow_runner.json`、`er052_output/open233_self_recovery_
flow_runner_01/instances/*.json`(29件)。

**費用見積(概算、要実測)**: 公式単価gpt-6-luna(In $0.10/Cached
$0.01/Out $0.50、為替¥156.88/$換算)を基準に、①¥0+②¥0〜¥2+
③¥8〜9+④数円〜¥10+⑤¥8〜22+⑥(④⑤に準ずる、追加数円)=
**Phase 1合計概算: 約¥18〜45**(総枠¥400のうち少額)。この見積もりは
前Phase実測単価からの外挿であり、Phase 1実行後に実測値へ更新する。
①〜⑥の合計Guardrail上限(各項目上限の合計): 約¥70(想定費用の1.5〜2倍
程度を上限とする既存慣例と整合)。Phase予算¥400に対する配分は①〜⑥の
実測(上限合計約¥70)を第一弾とし、残額(約¥330)は⑤⑥の追加実測・
Phase 2準備に充てる想定とする(次回委任で個別確定)。

**[委任_06実測]** ①=¥0(実測、確定)。②=¥0.6285(実測、確定。
見積り上限¥2の約31%)。①②実測合計=**¥0.6285**(Phase累計、後述の
Guardrail上限¥10のうち)。

**[委任_07実測]** ③=¥13.5234(実測、確定。見積り¥8〜9比+約¥5、
S1-D追加実測分を含むため)。④=¥1.1364(実測、確定。見積り数円〜¥10の
範囲内)。③④実測合計=**¥14.6598**。①〜④累計=**¥15.2883**
(Phase累計、Guardrail¥400のうち)。⑤⑥は本委任(委任_07)未実施
(次回委任で実施予定)。

**[委任_08実測]** Stage2 rubric較正Trial(§4-8)=¥3.1717(26 call、
Guardrail¥12)。⑤=¥3.0363(18 call、Guardrail¥30、見積り¥8〜22の
下限を下回った。理由: E-1/E-2・J-1とも1 attempt目で解決しescalation
未発火だったため)。委任_08合計=**¥6.208**。①〜⑤累計=
**¥21.4963**(Phase累計、Guardrail¥400のうち、残¥378.5037)。
⑥(統合dry-run)は本委任(委任_08)未実施(次回委任で実施予定)。

**[委任_09実測]** ⑥統合dry-run(29 instance、92 call)=**¥16.7806**
(Guardrail¥45、約37%使用、0 error)。①〜⑥累計=**¥38.2769**(Phase
累計、Guardrail¥400のうち、残¥361.7231)。Phase 1計画(§9-1冒頭)の
①〜⑥全項目が完了。

**⑦ iteration 2実測(委任_10完了)**: §9-2改善優先順位1〜4の実装+
再測定。実装項目: (a) Stage2出力schemaへの`rewrite_hint`追加(§4-5)、
(b) J-1汎用ロケータ改善(§5-4、rewrite_hint引用+位置比マッピング)、
(c) claim identityの正規化(fact_id無し時、引用符/大小文字/空白の
表記揺れを吸収、Opus L2 #1論点5対応)、(d) delete型のclaim単位再出現
確認(fuzzy matchによる重複削除漏れ検出)、(e) S1-U variant(§3-1、
Stage1 recall miss対策)。同一29 instanceを`--s1u`有効で再実行し
(Stage1[V4A]は既存出力を再利用し二重課金なし、Stage2以降は新schema
で再実行)、126 call・¥26.0302(Guardrail¥35のうち、0 error)を実測
した。

**iteration 1→2 差分表(instance単位)**:

| 指標 | iter1(委任_09) | iter2(委任_10) |
|---|---|---|
| Initial BLOCK | 23/29 | 28/29(S1-Uで4件追加検出) |
| Re-screening自動解消 | 1 | 0 |
| Rewrite進行 | 22 | 28 |
| Rewrite自動解消 | 13 | 21 |
| Final STOP(Escalation) | 9 | 7 |
| 真の解消(all_prior_issues_resolved=True) | 11 | 16 |
| 総call数 | 92 | 126 |
| 総費用 | ¥16.7806 | ¥26.0302 |
| 平均¥/instance | ¥0.5786 | ¥0.8976 |
| worst instance | ¥2.2721(safety_A4) | ¥2.4664(safety_A4、Cap+¥3未超過) |
| latency P50/P95 | 17.27s/143.5s | 62.25s/184.0s |
| completion率 | 69.0% | 75.86% |
| Escalation率(Wilson95%CI) | 31.0%[17.3%,49.2%] | 24.1%[12.2%,42.1%] |

**claim単位Rewrite成功率**: floor後BLOCKING確定claim(cycle合計)に
対するRewrite実行42件中、初回試行で再発せず解消=34/42(81.0%、iter1
60.6%[20/33]から改善)。機構別: `single_text_local(E-2/delete-
generic)`=27/31(87.1%)、`paired_ja_en(J-1)`=7/11(63.6%、iter1
27.3%[3/11]から大幅改善)。J-1対象文特定(locate)成功率は9/11
(81.8%、iter1 4/11[36.4%、`j1_paired_rewrite`+`j1_failed+...`含む]
から改善、失敗[`j1_pair_not_located`]は1/11[9.1%、iter1
7/11[63.6%]から改善])。**hormuz_run03_standard(iter1でJ-1失敗により
STAGE4)は`RESOLVED_REWRITE_THEN_DOWNGRADE`まで到達した**。

**S1-U variantの実測(recall改善 vs 固定費・過剰BLOCK増分)**:
s1u_eligible instance10件中、Stage1(V4A)が実際にACCEPTABLE(PASS)
だったのは7件(既にBLOCKINGだった3件はS1-D呼び出し自体をskipし追加
コスト¥0)。7件中**6件(85.7%)でS1-DがBLOCKING claimを新規検出**し、
union screenで合流させた。**iter1で発見された3件の重大Stage1 recall
miss(B2_hormuz・B3・hormuz_run02_advanced[現行Production STOP実例
そのもの])は、いずれもS1-U screenが捕捉し、全件`RESOLVED_REWRITE`
まで到達した**(hormuz_run02_advancedはcycle1でRecheck
`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=True`)。追加固定費=
¥3.1589(7 call)。副作用: 新規に捕捉した`meta_run03_advanced`は2 cycle
以内に解消できずSTAGE4到達した(iter1では非検出のままACCEPTABLE_
STAGE1で静かに通過していたclaim。「見えない見逃し」を「人間が確認
できるSTOP」へ変換したものであり、Escalation数の増分[+1]という形で
Productivity側のコストとして現れる)。**採用推奨と根拠**: 固定費
¥3.1589+Escalation増分1件のコストに対し、現行Production STOP実例
そのものを含む3件の重大安全ギャップを解消できたことは、Safety側の
実質的な改善(Stage1単独では構造的に捕捉不可能だった見逃しを
Self-Recovery Flow内で解消可能にした)であり、+¥3/記事Capにも
未抵触(worst instance実測¥2.4664)であるため、**Phase 2ではs1u_
eligible対象(Stage1 PASS時)への適用を採用推奨する**(ユーザー最終
判断)。

**R2' rubric較正(不採用)**: §4-8追記のとおり、段階的判定手順+例示
追加によるRUBRIC_R2_PRIME(n=2、20 call・¥3.3977)は、Safety側で
1件の誤降格(A4-0)、Productivity側で改善0件という結果となり、委任文
の受入条件(誤降格0件かつProductivity改善)を満たさなかったため
**不採用、既存RUBRIC_R2を維持**した。

**0件の内訳(iter2)**: 真の解消16、QUALITY通過0、`all_prior_issues_
resolved`未確認0、誤PASS候補0(iter1と同様、全件Recheckで明示確認)。

**残るStage4到達7件の原因分類**: bgroup_B1・bgroup_B4・safety_A2A3・
safety_A4は委任_09と同一原因(J-1対象文特定失敗の残存分・Rewrite後も
Recheckが引き続きLEDGER_DEVIATION)。meta_run03_standard・neg1は
委任_09から継続(claim再発型)。meta_run03_advancedはS1-Uが新規に
捕捉したが2 cycle以内に解消できなかった新規ケース(上記参照)。次案:
(1) J-1のfulltext fallback(全文最小編集)発動条件をより早期に切替える、
(2) cycle上限(現行2)をS1-U捕捉claimに限り3まで緩和する案(Cap内か
要試算)、(3) safety_A4のRewrite後再発原因(Rewrite内容自体がLedger
適合しない)をclaim単位で個別診断する。

**Opus L2 #2論点案(5〜7個、委任_09から更新)**:
1. S1-U variant(Stage1 PASS時のみ1 call追加)をPhase 2でデフォルト
   採用すべきか(固定費増+Escalation増分1件 vs 重大safety gap解消3件)。
2. J-1改善(位置比+数値トークン一致)は成功率を大幅に改善したが、
   固有名詞中心のclaim(数値を伴わない)では依然locate失敗し得る。
   さらなる汎用化(JA/EN対訳アラインメントの専用実装)への投資判断。
3. R2'較正が失敗した(段階的手順化がむしろSafety/Productivity双方を
   悪化させた)ことから、rubric較正自体のアプローチ(自然言語手順の
   精緻化)の限界をどう評価すべきか。
4. claim identity正規化(表記揺れ吸収)は今回regression testでのみ
   検証した。実データでの効果測定(誤って別claim扱いされるケースの
   実測)は次回実測項目とすべきか。
5. meta_run03_advancedのような「S1-Uが新規発見したが解消できない
   claim」の扱い(cycle上限緩和 vs 現行どおりSTAGE4)。
6. Phase 2着手判断(iteration 1→2の改善実績を踏まえ、残る改善項目を
   さらに解消してから着手すべきか、現状のままPhase 2データ収集へ
   進むべきか)。
7. +¥3/記事Capの余裕(worst実測¥2.4664)は、S1-U+rewrite_hintによる
   token増加を織り込んでも維持されているが、Phase 2の記事数拡大時に
   累積コストがGuardrail設計へ与える影響の試算。

**USER_DECISION_REQUIRED該当有無(iter2)**: 該当なし(7条件いずれも
非該当。S1-Uによる新規Escalation[meta_run03_advanced]はSafety
「緩和」ではなくむしろ強化[見えない見逃しを可視化]であり条件2には
該当しない。worst instance実測¥2.4664は+¥3/記事Cap未超過[条件3]。
R2'不採用はTrial内較正判断でありProduction採用[条件4]は無関係)。

**費用(iter2)**: 作業B(R2'較正)¥3.3977+作業C(統合dry-run再実行)
¥26.0302=**¥29.4279**(本委任Guardrail¥50のうち)。Phase累計
¥38.2769+¥29.4279=**¥67.7048**/総枠¥400、残¥332.2952。

詳細ログ: `er052_output/open233_self_recovery_r2prime_recalibration_
01/summary_r2prime_recalibration.json`、`er052_output/open233_self_
recovery_flow_runner_01_iter2/summary_flow_runner.json`、`er052_
output/open233_self_recovery_flow_runner_01_iter2/instances/*.json`
(29件)。

- **モデル**: gpt-6-luna(前Phase Trial資産との直接比較のため統一、
  §4-6参照)。Production Stage 1のgpt-5.6-lunaとの差異は既知の
  未解決事項として記録し、Phase 2で扱う。
- **Guardrail**: 上記①〜⑥の個別上限に加え、次回委任で総額上限を
  個別設定する(委任文の慣例どおり、想定費用の1.5〜2倍程度を上限とし、
  超過見込みでSTOP)。

**⑧ iteration 3実測(委任_11完了)**: Opus L2レビュー#2(全文は
docs/pm/opus_l2_review_open233_self_recovery_02.md)の是正1-8を実装
(バグA/B修正・停止判定是正・段落単位Rewrite拡張・測定是正・Rewrite
由来逸脱検出・S1-U安価代替比較)。regression test 19件追加、既存
含め55件PASS。OUT_DIRをer052_output/open233_self_recovery_flow_
runner_01_iter3/へ変更(iter1/iter2証跡は無変更)。作業C(S1-U安価
代替比較、7 instance対象・21 call・Y5.136、Y5 Guardrail内)→作業D
(29 instance再実行・178 call・Y36.9585、Y45 Guardrailのうち)の順に
実施。さらに実run6 instanceのうちstage1_mode=freshの3件についてn=2
追加実行(23 call・Y5.8944、累計Y42.8526、Y45 Guardrail内で完走)。

主な改善結果: bgroup_B4/neg1_meta_b3prod_a2/safety_A2A3/meta_run03_
standardの4件がiter2 STAGE4からiter3で解消(RESOLVED_REWRITE系)。
STAGE4件数は7件(iter2)から5件(iter3主run)へ減少。測定是正により
escalation_zero_breakdownの分母をRESOLVED_REWRITE_THEN_DOWNGRADE
含む21件へ拡張し、真にunconfirmedな3件(neg2_meta_refresh_a2/
neg3_hormuz_prodrunner_b1b/safety_er009_unsupported_new_claim)を
特定、iter3ではこの3件が是正6(_recheck_confirm)によりunconfirmed_
after_reverifyでSTAGE4へ正しくfail-closed escalationするように
なった(neg2/neg3は主runで確認、safety_er009_unsupported_new_claim
はiter3でRESOLVED_REWRITEまで到達し確認成功)。

n=2実測(hormuz_run01_advanced/hormuz_run02_advanced/meta_run03_
advanced)では3件全てでsample1とsample2のfinal_stateが不一致。特に
hormuz_run02_advanced(実Production STOP実例)はsample1でV4A本体・
S1-U双方が見逃した既知recall missが、sample2ではV4A本体が検出し
fail-closedでSTAGE4へ到達した。単発run(n=1)によるEscalation率・
recall率の測定は不十分であることを実測で確認(詳細はOPEN-233-
SELF-RECOVERY-TRIAL-01_REPORT.md §11-4)。

S1-U安価代替比較(作業C)は2xV4-A union・S1-D effort=medium/lowの
いずれも採否条件(既知recall miss3件全捕捉かつ負例false BLOCK1件
以下)を満たさず、iteration3のStage1 union構成はS1-U(effort=high)
を維持する結論(Trial内部限定、Production default変更はユーザー
判断事項)。

残るSTAGE4の原因分類は、多くが「1 claimが記事内3箇所以上に跨って
反復される」構造による段落単位Rewriteのmethod-limitation(angle
起因、B1型)であり、neg2/neg3は是正6の意図通りの安全側STAGE4
(機構起因だが正しい安全装置作動)。詳細な差分表・群別Escalation率・
記事単位コスト・S1-U真偽内訳・JA/EN等価QA結果・遡及監査5件・
原因分類表はOPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md §11参照。
Opus L2 #2への採否判断の詳細は§16参照。本委任合計費用Y47.9886
(作業C Y5.136+作業D Y42.8526)。

**⑨ iteration 4実測(委任_12完了)**: ユーザー指示「許容線の再設計(自然な
解釈はOK/事実の発明はNG)」(§1)に基づき、Stage2 rubric R3→R3'(§4-9)+
floor改訂(changed_certainty除外、§4-3)+追加測定7項目(§8-iter4)を実装。
regression test追加、既存含め67件PASS。OUT_DIRをer052_output/open233_
self_recovery_flow_runner_01_iter4/へ変更(iter1〜3証跡は無変更)。作業B
(R3/R3'較正、Y7.8974、Y8 Guardrail内)→作業C(29 instance再実行、
139 call・Y28.5644、Y40 Guardrail内)の順に実施(--s1u有効)。

**主な改善結果**: STAGE4件数5件(iter3)→**3件**(iter4)。bgroup_B1が
RESOLVED_STAGE2_DOWNGRADE(Rewrite不要でclean通過、B1-cがQUALITYへ
再ラベルされた直接効果)、hormuz_run03_standardがRESOLVED_REWRITEへ
改善。**real_run(実run6 instance)のEscalation率が16.67%(iter3)→
0%(iter4)**。特にhormuz_run02_advanced(現行Production実STOP実例、
iter3までStage1本体・S1-U双方が見逃すsampleが実測された既知recall
miss)が、iter4ではS1-Uが検出しRewriteで正しく解消した
(`RESOLVED_REWRITE`)。残るSTAGE4 3件はsafety_A4(`cycle_limit_
exhausted`、iter3から継続する既知のangle起因method-limitation)+
neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1b(`unconfirmed_after_
reverify`、iter3で導入した是正6が意図通り安全側に働いた結果、新規
regressionではない)。群別Escalation率: safety 1/12(8.3%、iter3と
同数値)、b_group 0/4(iter3 25%から改善)、meta 0/2(変化なし)、
hormuz 0/4(iter3 25%から改善)、negative 2/7(28.6%、iter3と同一
2 instance)。

**追加測定7項目(§8-iter4)の結果(未達点を含めて正直に報告)**:
「正常記事の不要Rewrite」= negative候補7件+Normal群2件(hormuz_run03_
advanced/meta_run03_advanced)計9 instance中**4件(44.4%)**でRewriteが
発火した(neg1/neg2/neg3/neg5)。うちneg2/neg3はRewrite後も解消できず
STAGE4へ至っている(コスト二重負担)。**本委任の主目的(不要Rewrite
削減)は部分的にしか達成できていない**(STAGE4件数・real_run
Escalation率は大きく改善した一方、正常記事への過剰Rewrite率は高水準
のまま残存)。「自然な解釈なのにBLOCK」はStage1由来8/9instance
(既存の非決定性、Stage1[V4A]は本委任で変更していないため想定内)、
Stage2由来5claim(R3'のtie-break不安定性の実運用での再現、§4-9の
較正結果と整合)。Rewrite品質劣化候補12件(全てSafety群[deterministic
floor経由、想定内の局所編集]+bgroup_B4[cycle2]+neg1[cycle1]、
詳細後述)。Rewrite総回数36(記事あたり平均1.5652回)。記事単位worst
costはmeta_run03(Y2.924、iter3のY3.0853から改善)。

**S1-U(union screen)の反実仮想比較(§2項目6、0 call)**: S1-U適用時
final_stop_count=3・real_run rate=0%・総コストY28.5644。S1-U除外の
反実仮想(s1u_additional_block=trueの5 instanceを機械的にACCEPTABLE_
STAGE1[cost 0]へ置換、新規API callなし)でも同一final_stop_count=3・
real_run rate=0%・総コストY24.4022(差額Y4.1622)。**表面上の指標
[escalation件数・rate]だけを見るとS1-Uの有無で差が無いように見えるが、
これは誤読である**: 反実仮想が示す「escalation rate不変」は、S1-Uが
無ければ既知recall miss2件(`bgroup_B2_hormuz`/`hormuz_run02_advanced`)
が**沈黙裏にACCEPTABLE_STAGE1として通過していた**ことを意味し
(escalationとしてカウントされないが、安全に解消されたわけでもない
「見えない見逃し」)、実際のS1-U適用時はこの2件を検出しRewriteで
正しく`RESOLVED_REWRITE`まで解消している。S1-Uのfalse positive3件
(`neg4`/`neg6`/`neg7`)はいずれもStage2(R3')が`RESOLVED_STAGE2_
DOWNGRADE`で安価に是正しており、Rewrite・Escalationへは進んでいない。
**Fableへの採否材料**: S1-Uは追加コストY4.1622(全体のY28.5644の
約14.6%)で、既知recall miss2件を「沈黙裏の見逃し」から「検出・解消
済み」へ確実に変換している。QCD上の負担は小さく、Safety向上効果は
実測で裏付けられているため、Trial既定として維持を推奨する(最終採否
はFable/ユーザー判断)。

**残るSTAGE4 3件の原因分類**: `safety_A4`=angle起因(iter3から継続、
MUSE-HC-006/010/012という3つの兄弟claimが記事内の複数箇所に跨って
出現する構造、段落単位Rewriteのcycle上限内では解消しきれない既知の
method-limitation、コード側のバグではない)。`neg2_meta_refresh_a2`/
`neg3_hormuz_prodrunner_b1b`=機構起因(iter3で導入した是正6
[`_recheck_confirm`]が意図通り安全側に動作した結果、新規のregression
ではない)。

**Stage2 rubric R3 vs R3'採否の残存リスク(§4-9からの持ち越し)**:
R3'採用によりMeta-1/Meta-2/hormuz-HF009/A4-1が安定してBLOCKINGへ
復帰した一方、単体較正のn=2サンプルではB4-d(確実性強化、本委任の
主要な再ラベル対象)がR3'で2/2誤ってBLOCKINGへ回帰する退行が観測
された(§4-9)。29 instance実測では`safety_er009_changed_certainty`
が`RESOLVED_REWRITE`(Rewrite発火、floor経由ではなくrubric経由か
未検証)で通過しており、実運用でのB4-d型retentionの影響度は本29
instance構成には該当fixtureが無く直接確認できていない(negative群
4件のquality_degradation_candidatesにも該当claimなし)。**Phase 2
着手前の追加確認事項として報告する(独断で追加実装しない)**。

詳細な差分表・群別内訳・記事単位コスト・0件内訳・読み比べページ収録
記事はOPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md §12参照。本委任
合計費用Y36.4618(作業B Y7.8974+作業C Y28.5644)。

**⑩ iteration 5実測(委任_13完了)**: Opus L2レビュー#3の是正1-6(rubric
R3''/R3'''、2-of-2安定化、cite-or-release、品質劣化検出v2、Rewrite品質
制約)を実装し、29 instance×n=2(sample1/sample2)を実行した(作業C
[R3''/R3'''較正]52 call・Y8.4443+作業D 305 call・Y62.3761・error0、
Work D Guardrail Y65内)。regression test 25件追加(既存含め92件+他4
モジュール81件=計173件PASS)。詳細ログ: `er052_output/open233_self_
recovery_flow_runner_01_iter5/summary_flow_runner.json`。

**n=2結果(sample1/sample2、個別値を両論併記しn=1点推定を避ける)**:
Self-Recovery 6指標: initial_block 29/29、rescreening_auto_resolved
5/4、rewrite_progressed 24/25、rewrite_auto_resolved 21/24、
final_stop(STAGE4) **3/1**、user_decision_required 3/1。sample1の
STAGE4はbgroup_B4(`cycle_limit_exhausted`)+neg2_meta_refresh_a2/
neg3_hormuz_prodrunner_b1b(`unconfirmed_after_reverify`)、sample2の
STAGE4はhormuz_run03_standard(`same_claim_fact_id_reblocked`)のみ。
safety_A4(iter3・iter4で継続していたangle起因method-limitation)は
両sampleとも`RESOLVED_REWRITE_THEN_DOWNGRADE`で解消し、初めてSTAGE4を
免れた。**per_instance_final_state_agreement(29 instance中の最終状態
一致率)=21/29(72.41%)**、8 instanceで最終状態が食い違う(bgroup_B2_
hormuz/bgroup_B4/hormuz_run02_advanced/hormuz_run03_standard/
meta_run03_advanced/neg2/neg3/safety_er009_changed_time)。**これは
Opus L2 #3是正4(§13-4)が指摘した「単発runの非決定性」がn=2実測でも
再現したことの直接証拠であり、iteration4の「STAGE4 5→3、real_run
Escalation 16.67%→0%」という単発run同士の比較が改善の証明にならない
という訂正(REPORT§13-4)の裏付けとなる**。

**群別Escalation率(n=2、58 instance-run、Wilson 95% CI)**: safety
0/24(0%、CI[0%,13.8%])、b_group 1/8(12.5%、CI[2.24%,47.09%])、
meta 0/4(0%、CI[0%,48.99%])、hormuz 1/8(12.5%、CI[2.24%,47.09%])、
negative 2/14(14.29%、CI[4.01%,39.94%])。**real_run(現行Production
実STOP実例6 instance×n=2=12)Escalation率=1/12(8.33%、CI[1.49%,
35.39%])**。iteration4(n=1、6 instance)は0/6(0%)と報告していたが、
これは単発runの点推定であり、n=2実測ではhormuz_run03_standardが
sample2でSTAGE4に至った(sample1は`RESOLVED_REWRITE_THEN_DOWNGRADE`)
ことでnon-zeroと判明した。**「real_run Escalation 0%」という
iteration4の報告は、n=2で見ると過度に楽観的だったと訂正する**
(REPORT§14-2)。

**不要Rewrite(v2訂正版、neg5除外済み)**: 正常記事9 instance中、
sample1=**7/9(77.78%)**、sample2=**6/9(66.67%)**。**iteration4の
44.4%(4/9)、Opus独立判定の2〜3件(22〜33%)のいずれよりも悪化している
ことを正直に報告する**。原因をclaim単位で追跡したところ、2系統に
分かれることを確認した: (a) **deterministic floor起因**(neg3/neg6/
hormuz_run03_advancedの一部claim、`floor_reason`に`changed_comparison`
/`changed_time`/`changed_actor`が記録され、LLM自体は`llm_materiality
=QUALITY`または`ACCEPTABLE`と正しく判定していたにもかかわらずfloorが
上書きしてBLOCKINGへ強制した)。floor精度の改善は委任文item7で明示的に
ユーザー判断待ちとして凍結されており、本委任では意図的に触れていない
(fail-closed維持)。(b) **Stage2(R3''')自体の安定したBLOCKING判定**
(neg1/neg2/meta_run03_advanced/hormuz_run03_advancedの一部claim、
Meta AIコールテスト関連claim[MUSE-HC-006/012]やHormuz HF-009 scope
関連claimで、2-of-2の両呼び出しが一貫して`BLOCKING(both agree)`と
判定しており、単発runのノイズではなく再現性のある判定である)。b群は
較正セット(23claim・13group)に含まれるB4-d/B1-cとは異なるclaim
パターンであり、**較正の較正セット外汎化が未確認である**ことを示す
新規の知見として報告する(独断で追加rubric改訂はしない)。

**品質劣化検出v2**: sample1(重複段落0/孤立逆接1/語彙難化2、
needs_regeneration 3件、再生成3件実施・再生成後も劣化解消0件)、
sample2(重複段落0/孤立逆接0/語彙難化5、needs_regeneration 5件、
再生成5件実施・再生成後に劣化解消**2件**)。**再生成の効果は限定的**
(sample1では0/3、sample2では2/5のみ再生成後に解消)。重複段落検出0件
(iter4のneg1 cycle2型パターンは本29 instance構成には再現しなかった)。

**2-of-2安定化**: sample1 trigger 8claim(downgraded 3・confirmed_
blocking 5)、sample2 trigger 5claim(downgraded 3・confirmed_
blocking 2)。**両sample合計13claim中6claim(46%)がdowngradeされており
(=1回目BLOCKINGだが2回目でQUALITY/ACCEPTABLEへ反転し、Rewriteを
回避できた)、Stage2単発判定の非決定性が実際に不要Rewriteを誘発して
いたことを裏付ける実測**。

**cite-or-release**: sample1 confirm call(remaining_sentence付き)2件・
release 0件、sample2 confirm call 3件・release 0件。**機械検証で
「根拠のない未解消」と判定されたケースは本29 instance実行では0件**
(全てのunresolved判定が記事本文中の実在文を正しく引用できていた)。
fail-closedを緩めない設計どおり、無根拠なSTAGE4を誤って作り出しては
いないことを確認した。

**JA/EN等価QA**: sample1 calls 8・FAIL 0・REVIEW_REQUIRED 5、sample2
calls 6・FAIL 0・REVIEW_REQUIRED 5。両sampleともFAIL 0件を維持
(iter4から継続)。

**記事単位コスト(worst across samples)**: **safety_A4が¥5.3592
(sample2)で最悪値、+¥3/記事Capを¥2.36超過**。bgroup_B4も¥4.0387
(sample1)でCap超過。いずれも2-of-2・品質劣化v2再生成・cycle_limit
到達が重なった既知の困難instance(safety_A4はangle起因・複数箇所
出現[MUSE-HC-006/010/012]という既知のmethod-limitation、委任文item8
「fact_id複数箇所Rewrite」のPhase2設計課題そのもの)。29 instance中
Cap超過は2件(6.9%)にとどまり、平均記事単位コストはsample1 ¥1.047・
sample2 ¥1.0617と大きくCap内。**USER_DECISION_REQUIRED条件3(+¥3 Cap
超過が期待値ベースで必要、または恒常的に避けられない)には該当しない
と判断する**(平均・大多数のinstanceはCap内であり、超過は既知の
method-limitation[item8]を持つ少数instanceに限定される tail risk)。
ただし将来のPhase2設計でitem8(fact_id単位複数箇所Rewrite)を実装する
際の優先根拠として記録する。

**USER_DECISION_REQUIRED該当有無**: 7条件いずれも非該当と判断する
(条件2[Safety緩和]非該当: safety群Escalation 0/24、Safety-critical
10claim誤降格0件を較正・フロー実測双方で確認。条件3[Cap超過]非該当:
上記のとおりtail risk)。floor精度(item7)・fact_id複数箇所Rewrite
(item8)はいずれも本委任で意図的に未実装のまま据え置く(委任文の
指示どおり)。

**総括**: STAGE4件数・real_run Escalationのいずれも「n=1点推定では
改善したように見えるが、n=2で見ると非決定性の範囲内であり、safety_A4
の継続的解消という前進はある一方、不要Rewrite率はむしろ悪化し、記事
単位worst costもCapを超過するようになった」というのが正直な総括である。
本委任の当初目的(不要Rewrite削減)は**達成できていない**
(Status=`ITER5_DONE_IMPROVEMENT_NEEDED`)。詳細はREPORT.md §14参照。

### 9-3. Stage別usage記録要件(委任_02追加、2026-09-30ユーザー追加指示)

Phase 1 Trial harnessは、全API callのusageログへ以下を必須で付与する
(§8-4のStage別コスト計測を可能にするため。現行`er051`系harnessの
usage記録スキーマへstage識別子を追加する形で実装する、次回委任で
確定): `article_id`/`writer_stage`(advanced/standard)/`recovery_
stage`(stage1_initial/stage2_second_judge/stage3_rewrite_en_local/
stage3_rewrite_ja_full/stage1_recheck)/`cycle_number`(1 or 2)/
`model_id`/`input_tokens`/`cached_tokens`/`output_tokens`(reasoning
含む)/`cost_jpy`(公式単価+実測為替レートで算出、仮単価流用禁止)。
これにより「固定費(Stage1)」と「条件付き費(Stage2以降)」を実測ベースで
事後集計できる。

### 9-2. Phase 2(Production相当10〜20記事、Checkpoint E前に別途計画)

Phase 1でStage 2/3の基本設計が機能することを確認した後、実際の
Family X新規記事生成(または既存Hormuz/Meta run再開)をSelf-Recovery
Flow込みで10〜20記事規模実行し、Primary KPI(USER_DECISION_REQUIRED
=0件、Safety見逃し0件)を測定する。Production Stage 1のモデル
(gpt-5.6-luna)とStage 2/3で使うモデルの整合確認もここで行う。詳細
計画は本書の対象外(次のCheckpoint前に別途設計)。

**[委任_09追記]Phase 1⑥の結果を踏まえた改善優先順位(Phase 2着手前に
解消すべき既知課題、実装せず提案のみ)**:
1. **Stage2出力schemaへの`rewrite_hint`追加**(§9-1⑥(b)根本原因、
   最優先)。現状Stage3へ渡る情報が`materiality`/`basis`のみで
   具体的な修正方針が無く、Rewriteの60.6%成功率(claim単位)の主要な
   下押し要因になっている。
2. **JA/EN paired local rewrite(J-1)の汎用対象文特定**(§5-4既知の
   限界、実測ではlocate失敗率63.6%[7/11]が最大の失敗要因)。委任_08
   のhormuz手動アンカー実験(100%解消)と本統合runの汎用ロケータ
   (27.3%)の差は、汎用実装の成熟度不足であり設計の限界ではない
   ことを示唆する。
3. **negative群Productivity評価の再測定**(§9-1⑥「最重要の是正発見」
   参照、既存87.5%は無効な測定に基づく。実測0/4[0%]を前提に、
   Stage2 R2 rubricのover-block是正力を再評価する必要がある)。
4. **Stage1(V4A) recallの底上げ**(3/複数instanceで既知BLOCKINGを
   n=1で見逃した。§9-1②の「独立Stage2診断3/3検出」知見をどう
   Production設計へ組み込むか[全記事2nd runのコスト増との比較]を
   Phase 2設計に含める)。
5. **新規記事のテーマ選定**: Phase 2で新規Family X記事を生成する場合、
   テーマは複数候補(英語・日本語・理由付き)を提示しユーザーが選択
   する(PM_GOVERNANCE.md§13「新規記事テーマ選定ルール」準拠。既存
   Hormuz/Meta run再開[regenerate]であればこの制約は適用されない)。

**[委任_10追記]上記1〜4の実装・実測結果(§9-1⑦)**: 1(rewrite_hint
追加)=**実装・実測済み**(claim単位成功率60.6%→81.0%)。2(J-1汎用
対象文特定)=**実装・実測済み**(locate成功率36.4%→81.8%、固有名詞
中心claimでは依然限界あり)。3(negative群Productivity再測定)=
**再測定実施(R2'較正Trial)、不採用と判定**(誤降格1件+改善0件の
ため既存R2を維持、理由は§4-8追記)。4(Stage1 recall底上げ)=
**S1-U variant[union screen]として実装・実測済み**(委任_09の3件の
重大recall miss全件を捕捉、副作用としてEscalation新規1件)。5(新規
記事テーマ選定)は本委任では未着手のまま(Phase 2着手時に対応)。
残る課題は§9-1⑦「残るStage4到達7件の原因分類」「Opus L2 #2論点案」
を参照。

**[委任_13追記]Phase 2前条件(Opus L2レビュー#3論点6-A)の充足状況と
iteration5後の再評価**: iteration4時点でOpusが提示した4条件(機構起因
Escalation 0〜1/29、negative Stage 4=0かつ読み物品質確認、JA/EN乖離
閉鎖、測定是正[n=2])のうち、iteration4はいずれも未達または境界だった
(詳細は§9-1⑨参照)。iteration5(§9-1⑩)でR3'''+2-of-2+cite-or-release+
品質劣化検出v2+Rewrite品質制約+n=2実測を反映した結果は§9-1⑩に記録する。

**[委任_13追記]Phase 2設計課題(実装せず、ユーザー判断待ちとして記録)**:
1. **fact_id単位マルチ箇所一括Rewrite**: Opus L2レビュー#3論点3・4・6で
   繰り返し指摘された「1つのclaimが記事の複数箇所(見出し・本文・
   In one line等)に散らばる」問題(neg3/B1/A4の真因)は、現行の段落単位
   local Rewrite設計の構造的限界であり、rubric調整では解けない。解決
   するには「同一fact_idを参照する全箇所を1回のRewrite callで一括修正
   する」設計拡張が必要だが、これはRewrite範囲を広げる=読み物品質
   リスクを上げる方向でもあるため、iteration5のスコープには含めず、
   Phase 2設計課題として提示する(採否・設計方針はユーザー判断)。
2. **deterministic floorの発火条件精密化**: Opus L2レビュー#3論点3推奨2
   (floorを「Stage1のフラグが立っている」ではなく「Stage1が矛盾する
   Ledgerの具体値[numeric_value/date_or_period/明示claim文]を名指し
   できている場合のみ」へ限定する案)は、既存安全装置(fail-closed floor)
   の緩和方向の変更に該当するため、7条件④に照らしiteration5では実装
   せず、ユーザー判断待ちのまま据え置く。**iteration6(§9-1⑪)で
   floor-cited variantとして反実仮想測定を実施した(§4-13)。**

**⑪ iteration 6実測(委任_14完了)**: ユーザー新方針10項目(§1)を実装し
(丸め許容§4-12・floor-cited§4-13・最小変更ラダー§5-7・セクション役割
維持§5-7・Hook-aware統合§6-4・コスト5分割§8-7)、監査2件(Hook-aware
再監査・Rewrite後QA資産棚卸し、`docs/pm/audit_hook_aware_and_rewrite_qa_
open233_01.md`、¥0)を実施した後、29 instance×n=2で再実行した(作業D、
--groups全群、Guardrail¥60)。**累計¥60.226でGuardrailへ到達し
TrialAbort(既存の安全装置どおり正常停止)**。sample1は29/29完走、
sample2は26/29(negative群の`neg5_hormuz_div_a2`/`neg6_smallbag_div_b1b`/
`neg7_meta_prodrunner_b1b`の3件が未完走)。n=2の自動集計
(`combine_n2_measures`)は両sample完走が前提のため、両sampleに存在する
26 instanceのoverlapで手動再集計した(詳細ログ:
`er052_output/open233_self_recovery_flow_runner_01_iter6/summary_
flow_runner.json`[sample1]、`/tmp`下の一時集計はcommit対象外のため
REPORT§15に転記)。

**最重要発見(ラダー効果、§5-7)**: iteration5では段落単位Rewrite
(`e2_paragraph_rewrite`)がほぼ全Rewrite eventで使われていたが、
iteration6(26 instance×2=52 instance-run、single_text_rewrite経由の
rewrite操作のみ集計)では**`4_paragraph`水準の使用が0件**になった
(`1_word_connective`25件・`3_sentence`9件・`6_full_article`3件・
`0_delete`1件・`paired_j1_not_laddered`[J-1、未ラダー化]22件)。**記事
単位平均コストは¥1.0649(combined)でiteration5(¥1.047/¥1.0617)から
実質横ばい**(+¥2/記事Capを大きく下回る、ラダーの追加call費用と
段落回避によるコスト削減が相殺した)。

**不要Rewrite率(v3、主要指標)**: sample1(n=1、9 instance全完走、
iteration5と同一base)で**44.44%(4/9)**、iteration5の77.78%(7/9)から
明確に改善した(iteration4の44.4%と同水準まで低下)。ただし該当4
instance(`neg1_meta_b3prod_a2`/`neg2_meta_refresh_a2`/
`neg3_hormuz_prodrunner_b1b`/`meta_run03_advanced`)はsample1・sample2
(26 instance overlap、6.67%→66.67%[8/12]、baseがiteration5の9件から
6件へ縮小しているため単純比較不可)の**両方で完全に一致**しており、
根本解消はできていない。監査(§6-4)の結論どおり`neg1`はHook-aware
(changed_scope単独のみ緩和)の対象外flag(changed_fact/changed_
certainty/unsupported_new_claim)のため未解消、`meta_run03_advanced`は
新規に出現した事例(較正セット外claimパターンへのStage2汎化問題、
iteration5§14-3(b)で既に指摘された既知知見の継続)。

**real_run Escalation(n=2 overlap、12 instance-run)**: **2/12
(16.67%、Wilson95%CI[4.7%,44.8%])で、iteration5のn=2実測(8.33%)より
悪化**。`meta_run03_standard`がsample1・sample2の両方でSTAGE4
(`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`)に至ったことが
主因。これはpaired J-1(未ラダー化、§5-7既知の限界)側の既存挙動であり、
本委任のB-1〜B-6変更がJ-1機構自体には触れていないため、新規の regression
というより既存の非決定性・既知の限界の別サンプルでの再現と考えられる
(独断で追加のJ-1修正はしていない)。

**floor-strict/floor-cited比較(§4-13)**: divergence
(floor-strictは発火・floor-citedは不発火)は全体で1件のみ(`bgroup_B4`の
`changed_comparison`)、**Safety群(24 instance-run)では0件(hard gate
通過)**。floor-citedの`related_fact_id`依存という実装上の限界
(`safety_er009_changed_number`で明示的な数値引用があるのに
`related_fact_id`未付与のため判定不能だった実例を確認)も踏まえ、
floor-strict(現行)を既定のまま維持する採用推奨とした(§4-13)。

**その他の新機構の実測発火状況**: 丸め誤検出回避0件・Hook-aware
downgrade 0件(いずれも該当条件を満たすclaimが本fixture setに存在
しなかった、機構自体はunittestで独立に動作確認済み)、セクション役割
違反5件(numbers_added_to_title×2[safety_er009_changed_causality]・
hook_shrank×2[safety_er009_unsupported_new_claim 25→0語・neg1
28→11語]・in_one_line_too_long×1[neg3、+55.6%])。

**USER_DECISION_REQUIRED該当有無**: 該当なし(6条件いずれも非該当)。
Guardrail到達によるsample2部分完走(26/29)は「予算超過」ではなく既存
安全装置の設計どおりの正常停止であり、条件(累計予算超過)には該当しない
(委任Guardrail¥60に対し実際の停止点は¥60.226、既存check_budget()の
「呼び出し前チェック」設計上の必然的な小幅超過)。

**総括**: ラダー再設計(§5-7)は狙いどおり段落単位Rewriteをほぼ全廃し、
コストを増やさずに不要Rewrite率をiteration5比で改善した(sample1
77.78%→44.44%)点で明確な前進。一方、(a)不要Rewriteの主因4件は
根本解消できておらず(Hook-aware/Stage2汎化の既知の限界)、(b)paired J-1
(JA/EN対訳)はラダー未適用のままで、2026-09-30ユーザー新方針item4の
flagship例(`bgroup_B3`)自体もJ-1経由だったため恩恵を受けなかった、
(c)real_run Escalationはn=2実測でむしろ悪化した。Status=
`ITER6_DONE_LADDER_IMPROVED_ROOT_CAUSE_REMAINING`。詳細REPORT§15。

**⑫ 代表5ケースTrial(委任_16 作業C、iteration6の未達原因是正+広い
iteration7実施前の少数ケース確認)**: PM_GOVERNANCE.md新節14の
Trial開始前チェック(A〜F各項目の反映先確認)通過後、5 instance
(`neg1_meta_b3prod_a2`/`bgroup_B3`/`hormuz_run03_standard`/
`safety_er009_changed_actor`/`safety_er009_changed_number`、全てstage1_
mode=reuse)をn=2で実行した(新規`er052_open233_self_recovery_flow_
runner_01_rep7_representative_01.py`、Guardrail¥15、OUT_DIR=`er052_
output/open233_self_recovery_flow_runner_01_rep7`)。J-1ラダー(§5-8)は
`bgroup_B3`でPASS(BLOCKING維持のままladder_level_used=1_word_
connectiveで解消)、hormuz_run03_standard/safety_er009系2件もSafety
維持+minimal resolutionでPASS。一方、Hook-aware rubric(§6-4)は
Safety-critical claim(`bgroup_B3`)誤降格のregressionを起こし、最小修正
1回後もFAILが再現したためSTOP条件(委任文§5)に該当し、rubricを安全な
RUBRIC_R3_TRIPLE_PRIMEへ復帰した(§6-4に詳細)。neg1(Meta hook)は復帰後
rubricでも未検証(pre-revert configでの実測のみ、BLOCKINGのまま
Rewriteで解消、hook_shrank違反[28→13語]を検出)。**Status=
`ITER7REP_STOPPED_SAFETY_REGRESSION_REVERTED`**(広いiteration7 Trialへは
進んでいない、Gate判定はiteration6のREJECTEDのまま変更なし)。詳細
REPORT§16(委任_16再発防止ルール明文化)/§17(代表ケースTrial結果)。

**⑬ Hook専用Stage2実装+代表5ケースTrial再実行(委任_17、§2原因是正:
共通rubric混在→API call分離)**: §4-14で確定したHook専用Stage2(title/
hookのclaimのみ別Prompt・別call、body/in_one_lineは既存Stage2
[`RUBRIC_R3_TRIPLE_PRIME`、本文不変]のまま)を実装した後、PM_GOVERNANCE.md
22節のTrial開始前チェック(`docs/pm/ACTIVE_TASK_C233T.md`、A〜F+関連項目
すべて反映済みを確認)通過後、委任_16と同一の5 instance(`neg1_
meta_b3prod_a2`/`bgroup_B3`/`hormuz_run03_standard`/`safety_er009_
changed_actor`/`safety_er009_changed_number`、全てstage1_mode=reuse)を
n=2で実行した(新規`er052_open233_self_recovery_flow_runner_01_
rep8_representative_01.py`、Guardrail¥14、OUT_DIR=`er052_output/
open233_self_recovery_flow_runner_01_rep8`、実測費用¥5.2181)。

**結果: 5/5ケース全てPASS(n=2両方一致)**:

| ケース | instance | section_type | stage2_route | 実測結果 | 判定 |
|---|---|---|---|---|---|
| 1 Meta Hook | `neg1_meta_b3prod_a2` | hook | hook(Hook専用Stage2) | materiality=QUALITY(sample1、2-of-2で1回目BLOCKING→2回目降格)/ACCEPTABLE(sample2)。final_state=RESOLVED_STAGE2_DOWNGRADE、Rewriteなし(ladder=[]、role_violations=[]) | **PASS**(委任_16でFAILしていたケースが解消) |
| 2/3 B3丸め+因果 | `bgroup_B3` | in_one_line | body(既存Stage2、Hook専用Stage2は一切呼ばれず) | materiality=BLOCKING維持(2/2)、ladder_level_used=1_word_connective(so→while相当)で解消、role_violations=[] | **PASS**(誤降格regressionは再現せず) |
| 4 Hormuz scope | `hormuz_run03_standard` | body | body | BLOCKING→ladder_level_used=1_word_connectiveで解消、recheck_all_prior_issues_resolved=True(JA/EN両方LEDGER_COMPLIANT) | **PASS** |
| 5a Safety actor | `safety_er009_changed_actor` | title | hook(Hook専用Stage2、LLM判定もBLOCKING) | floor(`deterministic_floor:changed_actor`)維持→ladder_level_used=1_word_connectiveで解消、recheck all_prior_issues_resolved=True | **PASS** |
| 5b Safety number | `safety_er009_changed_number` | title/body(2claim) | hook+precheck_floor_bypass | floor(`deterministic_floor:changed_number`/`precheck_floor`)維持→ladder=[1_word_connective, 6_full_article]で解消、recheck all_prior_issues_resolved=True | **PASS** |

**Evidence(§2原因是正の直接確認)**: `bgroup_B3`のstage2_results
(instance json)で`stage2_route="body"`が記録されており、Hook専用
Stage2(s2h.run_stage2_hook_batch)がこのclaimに対して一度も呼ばれて
いないこと(call_logにstage2_variant="hook"のエントリが存在しないこと)を
機械的に確認した(n=2両方)。Hook専用Stage2の発火回数はneg1(2回[2-of-2]
+1回)・safety_actor(1回×2)・safety_number(1回×2)の計7回、単価
¥0.0342〜¥0.3538(2-of-2発火時は2倍)。committing_16のprompt priming
regression(§6-4、共通rubricへの原則文追記が原因)は、API call自体を
分離した本実装では再現しなかった。

**最小修正は不要だった**(1回目の実行で5/5全てPASS、委任文§3-C「FAILが
あれば最小修正1回」の分岐は発火しなかった)。unittest(`TestHookOnlyStage2
Separation`4件含む131件+precheck 23件=154件)全PASS、`git diff --stat`で
Production(er003/er006/er009/er010/er012/er019)・既存iteration1〜6・
rep7証跡への差分なしを確認済み。**Status=
`REP8_ALL_5_CASES_PASS_HOOK_SEPARATION_CONFIRMED`**(広いiteration7
Trialは本委任のスコープ外のため未実施、次回委任でのユーザー判断・
Fable判定待ち)。詳細REPORT§17。

**⑭ 等価QA gating是正+Gate 9項目確認+広いTrial iteration 7(委任_22、
本書§6-11参照)**: §6-11で新設した`resolve_ja_ok_after_equivalence_
gating`により、rep12で判明した`bgroup_B3`のKPI後退(JA↔EN等価チェック
`REVIEW_REQUIRED`の無条件gatingが、JA側言語が実際には非JAで判定不能な
場合でも実Recheckの「解消」判定を無視してSTAGE4へ追い込んでいた問題)を
是正した。rep13実測(限定4 instance-run、¥0.9448)で4/4がSTAGE4に至らず
解消を確認した後、29 instance全量規模の広いTrial iteration 7(9
instanceはn=2・20 instanceはn=1、計38 instance-run、¥39.5475、
Guardrail¥45内)を初めて完走した(38/38完走・API error 0・false PASS
0)。STAGE4到達7件全てで`ja_equivalence_lang_indeterminate=False`
(genuineな未解消)を確認し、A-1修正による新規regressionが無いことを
確認した。不要Rewrite率はiter6(sample1、44.44%)からiteration7
(21.43%)へ改善した一方、**全量規模で初めて⑥(全体Rewrite/削除)使用
7件・worst instance cost¥8.9545(`safety_A4`、iter6の¥5.7883から悪化)
という新たなtail riskが判明した**ことを正直に報告する(⑦は全件
STAGE4で正しくfail-closedしており、false PASSではない)。**Status=
`A1_EQUIVALENCE_GATING_FIXED_REP13_4_OF_4_NO_STAGE4_ITER7_38_OF_38_
COMPLETE_FALSE_PASS_ZERO_WORST_COST_TAIL_RISK_INCREASED`**。詳細
REPORT§22。

**⑮ iter7未達2点の原因特定・設計修正・少数ケース確認(委任_23、本書
§5-10/§6-12参照)**: real_run Escalation(`hormuz_run03_standard`
2/10)の真因を2点特定・是正した(A: §6-11の等価QA gating過剰保守を
`resolve_ja_ok_after_equivalence_gating`拡張で解消、B: reuse fixtureの
same_fact_id列挙欠如を`deterministic_same_fact_id_location_fallback`
新設で解消)。⑥(全体Rewrite/削除)は、iter7実測で7/7が最終的にSTAGE4
だった(「⑥が必要だった」Evidence 0件)ため、feature flag(既定OFF)で
標準ラダーから除外した。rep14実測(`hormuz_run03_standard`×n=2+
`safety_A4`×n=1、¥5.3545)で、是正A・Bとも実際に発火することを確認
したが、**`hormuz_run03_standard`は2/2ともSTAGE4_ESCALATIONのまま**
(理由が`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`
[word-level Rewriteの質的限界という第三の要因]へ変化)だった。
`safety_A4`はworst cost¥8.9545→¥1.5084(83%減)を確認し、Safety
floor-strictの維持・false PASS 0件・unittest218件全PASS・Production
無変更を確認した。**Status=`A2_GATING_AND_ENUMERATION_FIXED_VALIDATED_
LADDER6_DISABLED_COST_REDUCED_HORMUZ_STILL_ESCALATES_NEW_THIRD_CAUSE_
FOUND`**。詳細REPORT§23。

**⑯ hormuz第三要因(ラダー未昇段のまま§3-3安全網が先に発火)の是正+少数
確認rep15(委任_24、本書§6-13参照)**: rep14で「Stage3 Rewrite品質の
限界」と報告していた第三要因を精査した結果、実際は§3-3安全網(`matched_
records`判定)が§6-6 A-2のラダー前進機構(`escalate_to_paragraph`)より
先に評価される実装順序の問題だったと判明した。同一claim再発を、④段落
水準まで既に試行済みの場合のみSTAGE4(`same_claim_fact_id_reblocked`)
へ回し、未昇段の場合は既存のラダー前進機構へ合流させループを継続する
是正を実装した(unittest 222件全PASS)。rep15実測(`hormuz_run03_
standard`×n=2、sample1完走・sample2はGuardrail¥7到達でTrialAbort)で
sample1は`same_claim_fact_id_reblocked`が発生しなくなり、①→③→④まで
正しく昇段してEN/JA Ledger Recheckとも「解消」を確認したが、別の既存
hard gate(`ja_en_equivalence_verdict=FAIL`、委任_23で意図的に無変更の
まま維持)により`ja_deviation_unresolved`でSTAGE4_ESCALATIONへ至った
(false PASSではない)。sample1のコストはrep14比**約2.1倍**(¥4.0578 vs
¥1.87〜1.98)となり、これがrep15予算(¥7)を`hormuz_run03_standard`
n=2だけで使い切った直接原因のため、`bgroup_B4`×1・`safety_A2A3`×1は
**本委任では未実施**。Phase 2候補記事一覧(新規テーマは作らず既存evidence
を精査)は、独立した実在記事テーマが「hormuz」「meta」の2件のみであり
10本には届かないことを正直に報告した(詳細REPORT§24-4)。**Status=
`LADDER_ESCALATION_ORDER_FIXED_VALIDATED_HORMUZ_NO_LONGER_PREMATURE_
REBLOCK_BUT_SEPARATE_EQUIVALENCE_GATE_ESCALATES_COST_INCREASED_B4_
A2A3_UNTESTED_BUDGET_EXHAUSTED`**。詳細REPORT§24。

**⑰ 上位原則「重大誤解原則」の明文化+Hormuz要素Trial A(委任_27、
本書§0/§4-18/§5-11/§7-0-iter27参照)**: ユーザー上位原則(2026-10-01)を
§0として明文化し、¥0是正4点(escalate_to_paragraph廃止・問題種類→
初期単位写像・主体置換ガード・等価QA理由文保存)を実装した(unittest
既存222件+新規19件=241件全PASS、`git diff --stat`でProduction・既存
rep/iteration証跡への差分なしを確認済み)。Hormuz要素Trial A(Stage2
body rubricのみ、`er052_open233_element_trial_hormuz_terms_01.py`、
¥2.1336)で、許容群5件(実文①②③+term/rounding各1合成)・NG対照群5件
(gasoline/world energy/all crude benchmarks/方向反転/neg3)・Safety
対照群2件(B3因果+er009 changed_scope、hormuz-HF009自身は本委任の
再ラベル対象のため除外[§7-0-iter27])をn=2で実測した。初回rubric
(`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE`)でaccept-1
("Oil prices did not fall across the whole market...")が2/2 false
BLOCKとなったため、「Brent先物を同じoilという対象のままより一般的な
言い方に置き換えるだけの場合は許容する」明確化を1回追加した
(`..._V2`)。V2での再実測(n=2)は許容群5件・NG群5件・Safety群2件の
全てでfalse PASS/false BLOCK 0件を確認した。Trial A-2(決定論名詞句
置換、`er052_open233_element_trial_a2_deterministic_rewrite_01.py`、
¥0.1261)で、NG 2件(gasoline/world energy→Brent futures)+原文②
(JA/EN対、Oil prices→Brent futures/原油価格→Brent先物)の名詞句
置換を実施し、word-level diffで対象名詞句以外が不変であること
(`full_article_unchanged_elsewhere=True`)を確認、局所QA 1callの
verdictは`REVIEW_REQUIRED`だったが、指摘された唯一の`meaning_changes`
(湾岸諸国-アメリカ間の投資案件の方向性)は本置換と無関係な既存箇所
であり、本置換自体は「日付、数値、人名、否定表現、原油価格の推移、
記事の結論および一言まとめは概ね維持」とnotesで確認された。**本委任
費用¥2.2597**(Guardrail¥25のうち)。Stage1(V4A)・Hook専用rubricへの
原則文追加は定数として実装済みだが未配線(§4-18)。**Status=
`ELEMENT_TRIAL_MISCONCEPTION_PRINCIPLE_CODIFIED_HORMUZ_TRIAL_A_PASSED_
AFTER_ONE_MINOR_FIX`**。詳細REPORT§25。Meta要素Trialは次回委任_28。

**⑱ Stage1/Hook重大誤解原則の実配線+Safety対照群の全量確認(委任_28
Part0-1/0-2/Part1、本書§4-18/§7-0-iter5続き)**: 新規
`er052_open233_element_trial_safety_control_01.py`で、Safety-critical
9claim(`SAFETY_CRITICAL_SUB_IDS`、委任_28でhormuz-HF009を除外した後の
9件)+Safety12(er009 9フラグ)の全量をStage2 body rubric(重大誤解原則
入り)で対照測定した。Stage1(V4A)・Hook専用rubricへの原則文配線は、
`er052_open233_self_recovery_flow_runner_01.stage1_fresh_with_
misconception_principle`(新規関数、既存`stage1_fresh()`は無変更)+
`er052_open233_self_recovery_stage2_hook_01.run_stage2_hook_batch`への
`hook_rubric_text`引数(既定`HOOK_RUBRIC`、無変更)で実装し、unittest
7件で配線自体を確認した(¥0)。

**n=1予備測定(V2)**: Safety-critical 9claim中2件がfalse downgradeした
(A4-0「Through Muse, trained human contract workers made some calls
and completed the exchanges with users.」→ACCEPTABLE[元issue: Ledgerが
示す電話の相手先は企業・店舗だが、記事はMuseユーザー本人とやり取りした
ことにしている、カウンターパートの取り違え]。A5-1「Meta executives
admitted that starting the test without a proper explanation was a
mistake.」→QUALITY[元issue: Ledgerは特定の副社長の発言としているが、
記事は"Meta executives"へ一般化])。

**最小修正1回(V3)**: 「当事者関係(カウンターパート)の取り違えは
BLOCKING、同一組織内の役職の一般化[発言内容・責任主体=組織自体は不変]
は許容」という区別を追加した
(`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V3`)。

**n=2公式測定(V3)**: A4-0は2/2 BLOCKINGへ復帰(解消)。**しかしA5-1が
2/2 ACCEPTABLE(是正前のQUALITYよりさらに悪化)、かつ新規にMeta-1/
Meta-2(`build_eval_groups()`既存仕様によりbaseline deviationが1件のみ
のため両sub_idとも同一claim「Also, some calls needed user information
to continue.」を指す重複)が2/2ずつQUALITYへfalse downgradeした**
(元issue: Ledgerは「電話完遂にユーザー情報が必要になる可能性」という
条件付き記述だが、記事は「実際に一部の電話で必要だった」と断定、
certainty強化型)。Safety12(er009 9フラグ、Stage2直接判定)は9/9とも
2/2 BLOCKINGを維持(false downgrade 0件)。Stage1(V4A)新配線4フラグ
(changed_actor/changed_number/changed_scope/unsupported_new_claim)は
8 run中7runでseverity_final=BLOCKING維持かつ想定flag名一致、1run
(changed_actor)はBLOCKING自体は維持しつつ付与されたflag名が別名へ
振れた(真の見逃しではないが、flag名ベースのfloor発火条件が将来変わり
得ることを示す参考所見)。

**STOP判定**: 委任文STOP条件「Safety対照群のいずれかが小修正1回後も
BLOCKINGに戻らない」に該当するため、Stage2 body rubricへの重大誤解
原則配線はここで停止し、Part2(Meta Hook Trial B)・Part3(Actor Trial
C)は未実施のまま本委任を終える。A5-1・Meta-1/Meta-2の扱い(§7-0-iter5
で一度A2A3-1/A4-2が同種の機械コピー由来ラベルとしてQUALITYへ是正された
前例があり、同様の再ラベル候補である可能性と、rubric側のさらなる改善が
必要な可能性の両方が考えられる)はFable/ユーザー確認事項として開示する
(独断でSAFETY_CRITICAL_SUB_IDSやラベルを追加変更しない)。本委任費用
¥7.0873(予備測定¥2.7022+V3公式測定¥4.3851、Guardrail¥9のうち)。
**Status=`SAFETY_CONTROL_AUDIT_STOPPED_AFTER_ONE_MINOR_FIX_STILL_
FAILING`**。詳細REPORT§26。

**⑲ Safety対照群の安定化(Fableラベル判定反映)PASS+Meta要素Trial B/C
実施(委任_29、本書§0/§7-0-iter29参照)**: Fable(§1)が、A5-1は
hormuz-HF009と同種の役職一般化のためSafety-criticalから除外(QUALITY)、
Meta-1/Meta-2は「条件付きの可能性→既成事実への断定」でありBLOCKING
維持が妥当と判定した。この判定を反映し、`SAFETY_CRITICAL_SUB_IDS`を
8件化、`MISCONCEPTION_PRINCIPLE_TEXT_V4`(最小修正1回)を追加して
新規`er052_open233_element_trial_safety_control_02.py`
(Safety-critical 8claim+Safety12+Hormuz許容5/NG5)で対照測定した
結果、**n=1予備測定・n=2公式測定のいずれもmisdowngrade/false PASS/
false BLOCK 0件でPASS**(§7-0-iter29、費用¥4.9438)。

Part1 PASS後、委任_28で実装済み・未実行だった
`er052_open233_element_trial_meta_hook_01.py`(Meta要素Trial B[Hook
許容基準]・Trial C[未確認actor置換の抑止])を初めて実行した。**Trial B
初回実行(V2)で、集計コード自体に符号反転バグがあることが判明した**
(ng群のBLOCKING[正しい]をfalse_passへ、accept/boundary群の非
BLOCKING[正しい]をfalse_blockへ、それぞれ誤って計上。委任_28時点では
未実行のため発覚しなかった。`tally_hook_rows()`として是正し、
unittest[`TestMetaHookTallyScoringBugFix`]で再発防止)。是正後の実測
(真の値): NG群4/4は全run BLOCKING(false pass 0件、良好)。一方、
許容群のうちaccept-4(“Ring, ring...”)・boundary-1(“The surprise came
halfway through the call.”)が毎回false block、元Hook(accept-1、
実際の公開記事本文)も1/3 runでfalse blockした(rewrite_hint逐語:
「未確認の具体的なタイミング・行動の発明」という誤認)。委任文が許容
する最小修正1回(`HOOK_TIEBREAK_TEXT_V3`、確認済みの中心的な出来事を
自然な時間経過として描写する演出は、具体的な新事実発明が無い限り許容
する旨を追加)をHook Stage2のみ再実行(Stage1 fresh再測定はrubric非
依存のため省略、¥1.9481)したところ、元Hook(3/3)・accept-4は解消した
が、**boundary-1(境界群、“演出強め”)は2/2 false blockのまま残存**。
委任文STOP条件は「元Hook誤BLOCKまたはNG誤PASSが小修正後も残る」のみを
明記しており、境界群単独の残存はSTOP条件に明記されていないため、
STOPはせず残課題として記録する(追加のrubric変更はせず、Fable/
ユーザー判断を仰ぐ)。

Trial C(未確認actor置換の抑止、neg1 cycle2実データ)は、重大誤解原則
配線後のStage1(V4A)で、対象claim(“The test began without clearly
telling users that contract workers would make the calls.”)が
**n=2ともoverall_status=LEDGER_COMPLIANT(deviation自体が検出されない)
となり、委任文「期待1(社内テスト誤読の解消)」どおりに解消した**。
NG対照(VP→CEOの主体入替)はn=2ともBLOCKINGを維持し、actor置換ガード
自体は健在であることを確認した。「期待1」で解消したため、BLOCKING
経路を強制した場合のStage3 actor_rewrite_guard挙動(「期待2」)は本
委任では発火せず未検証のまま。

本委任費用(Part1+Part2+3)合計¥15.8357(Guardrail¥25のうち、Part1
¥4.9438+Part2/3¥10.8919)。Phase累計¥402.5625+¥15.8357=
**¥418.3982**/総枠¥600、残**¥181.6018**。`git diff --stat`で
Production(er003/er006/er009/er010/er012/er019)・既存rep/iteration
証跡への差分なしを確認済み(新規出力は`er052_output/
open233_element_trial_safety_control_02/`[新設]・
`er052_output/open233_element_trial_meta_hook_01/`[新規実行]のみ)。
**Status=`SAFETY_CONTROL_STABILIZED_META_HOOK_TRIAL_B_PARTIAL_BOUNDARY_
RESIDUAL_TRIAL_C_RESOLVED`**。詳細REPORT§27。

**⑳ Hook V4によるboundary-1解消+runner既定化+実記事代表5ケース
rep16確認(委任_30、本書§4-23参照)**: Part1(¥0.7637)でHook rubric
V4を実測し、boundary-1・元Hook・NG4群の全てが期待どおりとなった
(§4-23(a))。あわせてTrial C「期待2」(users claimをBLOCKING経路へ
強制した場合のactor_rewrite_guard実挙動)を実測し、**重要な所見**を
得た: 実際のdev(changed_scope=true**かつ**changed_actor=true)では
`classify_problem_kind`の優先順位(term_scope>actor)により
problem_kind="term_scope"と分類され、**主体置換ガード
(`actor_rewrite_guard_ok`、problem_kind=="actor"の場合のみ発火)が
一度も評価されないまま**E1 word-level editが機械的に"users"を
"employees"へ置換した(guard_ok=True、ただしこれは主体の正しさを
検証した結果ではなく「文言が変化し元claim文言が残っていない」という
汎用guardのみ)。独立に確認した結果、"employees"という語はledger_text
に一度も出現せず、**もしproblem_kind=="actor"経路に乗っていれば
actor_rewrite_guard_okは実際に却下していたはずである**ことを特定した
(`er052_open233_element_trial_meta_hook_02.py`のtrial_c2、¥0.0637)。
これは委任_27 Part1-3で導入した主体置換ガードの設計上の盲点
(`changed_scope`と`changed_actor`が同時に真の場合、ガードの前提条件
[problem_kind=="actor"]に到達しない)であり、本委任のスコープ(Hook
境界群是正・runner既定化・rep16確認)の外にある独立した設計判断
(`classify_problem_kind`の優先順位をどうすべきか)を要するため、
本委任では変更せず**Fable/ユーザーへの開示事項**として記録する
(OPEN_ITEMS参照)。

Part2(¥0)で重大誤解原則をrunner既定経路へ実配線した(§4-23(b))。
Part3(rep16、実記事代表5ケース: `hormuz_run03_standard`/
`neg1_meta_b3prod_a2`/`neg3_hormuz_prodrunner_b1b`/
`meta_run03_standard`/`bgroup_B3`、Stage1 fresh)を実行した結果、
`neg3_hormuz_prodrunner_b1b`がSTAGE4_ESCALATIONとなり(¥3.104)、
原因分析の結果`paired_rewrite`の片側locate設計の穴を特定・是正した
(§4-23(c))。是正後、残り4 instance(`hormuz_run03_standard`/
`neg1_meta_b3prod_a2`/`meta_run03_standard`/`bgroup_B3`)についてn=2
(sample1+sample2)で再実行した結果、**4件ともsample1/sample2一致で
RESOLVED(hormuz/meta=RESOLVED_STAGE2_DOWNGRADE[Rewrite 0]、
neg1/bgroup_B3=RESOLVED_REWRITE[①単語・接続詞水準のみ、段落・全文
Rewrite 0]、Stage4到達0・false PASS 0)を確認した**(rep16単体
¥13.6565、sample2はbudget制約により`neg3_hormuz_prodrunner_b1b`の
み未完走[sample1=STAGE4だった回、n=1のまま]。neg3の修正自体は
`er052_open233_self_recovery_flow_runner_01_rep16_neg3_fix_verify_01.py`
による単体検証[実際に失敗していたclaimの再現状態からの再実行、
¥0.0758]でguard_ok=Trueを確認済みだが、フルフロー内でのsample2 n=2
到達は本委任のGuardrail内では完走できなかった[既知の残課題])。

本委任合計費用¥0.7637(Part1)+¥13.6565(Part3 rep16)+¥0.0758(neg3
単体検証)=**¥14.496**(Guardrail¥15のうち、残¥0.504)。Phase累計
¥418.3982+¥14.496=**¥432.8942**/総枠¥600、残**¥167.1058**。
unittest discoverで既存306件(§4-22時点)+新規6件
(`TestMisconceptionPrincipleDefaultWiring`6件)+新規2件
(`TestTargetNotLocatableEarlyReturn`内のpaired_rewrite是正test)=
**合計314件**(詳細REPORT§28)。`git diff --stat`でProduction
(er003/er006/er009/er010/er012/er019)・既存iteration1〜7・rep7〜15
への差分なしを確認した。**Status=
`HOOK_V4_BOUNDARY_RESOLVED_DEFAULT_WIRED_REP16_PARTIAL_N2_ACTOR_GUARD_
GAP_DISCLOSED`**。詳細REPORT§28。

**㉑ rep16の残3点の是正(actorガード常時評価+Hook境界拡張+body rubric
V5)+neg1/neg3のn=2再確認(委任_31、本書§4-24参照)**: Fable判定
§1(a)(b)(c)(§4-24に詳細記録)を反映した。(a)(b)はコード是正(¥0、
unittest 9件新規)、priming再測定(Safety-critical 8claim、B3を含む、
Stage2のみ・n=1、`er052_open233_element_trial_safety_control_03.py`)で
誤降格0件を確認後(¥1.6243)、`neg1_meta_b3prod_a2`/
`neg3_hormuz_prodrunner_b1b`をStage1 fresh・n=2で再実行した
(`er052_open233_self_recovery_flow_runner_01_rep17_representative_01.py`、
¥3.1313)。

結果: **両instanceともn=2全件でStage4到達0・false PASS 0を確認した**。
`neg1_meta_b3prod_a2`はsample1/sample2ともRESOLVED_STAGE2_DOWNGRADE
(Rewrite 0件)。ただしStage1(fresh、非決定性)が今回たまたまHook導入文・
Hook締め文・usersの3claimを検出せず(別のBLOCKING-candidate「A human
can handle situations that AI alone finds difficult.」[related_fact_id
MUSE-HC-008、section_type=body]を検出しn=2ともQUALITYへdowngrade)、
本委任の主目的(Hook境界拡張の効果)はこの実行ではfull flow上で直接は
再現しなかった。そのため、実fixtureのarticle_text(捏造なし)に対し
`detect_claim_section_type`/`_hook_paragraph_block`を直接呼ぶ¥0確認を
別途行い、**Hook導入文(“Ring, ring...It was a person.”)・Hook締め文
(“Meta had run a test that caused exactly this surprise.”)がともに
section_type="hook"へ、usersクレームはsection_type="body"のまま
(変化なし)であることを実データで確認した**(是正の構造的な効果は
確認済み、Stage1非決定性によるfull flow上の偶発的な不一致は既知の
限界として記録する)。

`neg3_hormuz_prodrunner_b1b`はsample1=RESOLVED_REWRITE・
sample2=RESOLVED_REWRITE_THEN_DOWNGRADE(cycle2のRecheckで新規claimが
ACCEPTABLEへ収束)、**いずれもStage4到達なし・Rewriteは①単語・接続詞
水準のみ(段落・全文Rewrite 0)**。ただしStage1 freshが今回検出した
claim群は全て`origin=translation`(EN単独、`single_text_rewrite`
経路)であり、委任_30で単体検証した`origin=ja_source`のJA/EN paired
claim(JA「貨物に」→「貨物について」)とは別のclaim集合だった(Stage1
非決定性、既知の限界)。当該JA paired claimの単体検証結果(既存artifact
`er052_output/open233_self_recovery_flow_runner_01_rep16/
neg3_fail_fix_verification.json`、委任_30・¥0.0758で取得済み、再実行
せず読み出しのみ)を参照として据え置く: `guard_ok=True`・
`method=j1_single_side_ja(e1_minimal_word_edit(exact_substring))`・
JA「海峡を通るすべての貨物に二割の償還」→「海峡を通るすべての貨物
について二割の償還」(支払義務者を特定しない表現、1語編集のみ)。
rep17で実際に検出されたEN claim(“The fee plan may be replaced, but
events continuing at the same time do not simply disappear backstage
because of one announcement.”の“events driving oil prices—and the
prices themselves—quickly returned”句)は、①水準の1語/短い句編集
(sample1: “the events driving oil prices—and the prices
themselves—”→“prices themselves ”への縮小、“During that period”→
“At the same time”、“because of”→“after”)でguard_ok=Trueのまま解決
した(段落・全文Rewriteへのescalationなし)。

本委任合計費用¥1.6243(Safety V5再確認)+¥3.1313(rep17)=
**¥4.7556**(Guardrail¥10のうち、残¥5.2444)。unittest discoverで本
テストファイル既存272件(§4-23時点)+新規9件
(`TestHookParagraphBlockBoundary`4件・`TestDetectClaimSectionType`
新規1件・`TestActorGuardAlwaysEvaluatedRegardlessOfProblemKind`1件・
`TestMisconceptionPrincipleRubricV5`3件、うち1件は既存test名の更新で
純増ではないため合計9件純増)=**合計281件、全PASS**。リポジトリ全体
discoverは2224件中8件が失敗(er025/er040/er043/er011、本委任と無関係な
既存failure、`er052`関連の失敗は0件であることを確認)。`git diff
--stat`でProduction(er003/er006/er009/er010/er012/er019)・既存
iteration1〜7・rep7〜16への差分なしを確認した。**Status=
`HOOK_BOUNDARY_ACTOR_GUARD_FIXED_REP17_N2_STAGE4_ZERO_PARTIAL_CLAIM_
COVERAGE_DUE_TO_STAGE1_NONDETERMINISM`**。詳細REPORT§29。

**㉒ 広いTrial iteration8(29 instance全量、9 instanceはn=2、計38
instance-run)で現行既定構成の横断安定性を確認(委任_32、本書
§7-0-iter32参照)**: 新しい改善案を探すTrialではなく、既定構成
(Stage1 V4-A+重大誤解原則/Stage2 V5/Hook V4、`ENABLE_MISCONCEPTION_
PRINCIPLE_DEFAULT=True`)がfull flowで横断的に安定して機能するかの
確認Trial。Safety12 fixtureのみStage1 reuse(構造上の理由は§7-0-iter32
参照)、残り17 instanceはStage1 freshで実行した
(`er052_open233_self_recovery_flow_runner_01_iter8_01.py`、
`OUT_DIR_ITER8`新設)。

結果: 実測¥24.9738(Guardrail¥50内、API error 0件)。良好な点:
(a)不要Rewrite率11.11%(1/9、neg3のみ)でiter7の21.43%から改善、
(b)hormuz_run03_standard(既知のハードケース、iter7は2/2 STAGE4)が
今回2/2ともRewrite 0件で解消(ユーザー承認済みhormuz-HF009再ラベルの
効果がfull flow上で初めて確認できた)、(c)Hook rubricが実際に発火し
QUALITYへ正しく降格させるEvidence(`safety_A2A3`/`safety_A4`の
Hook段落claim)を確認、(d)全体平均コスト¥0.6975/instance-runで
iter7の¥1.0407から改善。

**残存した問題(§7-0-iter32に詳細)**: (1)B3(HF-007)がn=2の両方で
QUALITYへ誤降格(安定した誤判定)、(2)A2A3-0(HF-003)がn=2の1/2で
QUALITYへ誤降格(揺れ)。候補修正(floor拡張)はhormuz-HF009等の正当な
QUALITY/ACCEPTABLE claimを巻き込むため不採用とし、§7 STOP条件
(小修正1回後も残るSafety-critical誤降格)に該当するとして根本修正は
行わずFable/ユーザー判断へ委ねた。(3)meta_run03_standard(実記事)が
n=2の両方でSTAGE4(stage4_reasonはsample間で異なる:
`same_claim_fact_id_reblocked`/`target_not_locatable`)に到達し、
実記事6種10 run中2 run(20%)が人間確認を要した(iter7のmeta群0%
escalationから悪化。Stage1 freshが「one employee」等のchanged_number
floor claimをより多くの箇所で検出するようになったこと[enumeration
強化]と、escalate_to_paragraph廃止[§0-4]の組み合わせにより、cycle
上限[MAX_CYCLES=2]内で全箇所を解消しきれなかったことが原因候補。
根本解決[MAX_CYCLES拡大/escalate_to_paragraph部分復活等]は本委任の
スコープ外として実装せず、Fable/ユーザー判断へ委ねた)。

**Status**: `ITER8_BROAD_STABILITY_TRIAL_COMPLETE_COST_AND_UNNECESSARY_
REWRITE_IMPROVED_BUT_B3_A2A3-0_SAFETY_CRITICAL_MISDOWNGRADE_AND_META_
STANDARD_HUMAN_REVIEW_REGRESSION_FOUND`。詳細REPORT§30。

**㉓ iter8未達3点の原因特定・小修正(body rubric V6)・限定再確認
(委任_33、本書§4-25/§6-14/§8-8参照)**: body rubric V6(許容/NG対比例示、
最小修正1回)を追加し、priming再測定(Safety-critical 8claim/Hormuz
許容5・NG5/Hook、Stage2のみn=1、¥2.0061)とfull flow再確認
(`bgroup_B3`/`safety_A2A3`/`meta_run03_standard`、n=2、¥4.3972)を
実施した。結果: (1)B3は2/2ともBLOCKING維持→1語[so→while]のRewriteで
RESOLVED_REWRITE(誤降格解消)。(2)A2A3-0は2/2ともBLOCKING維持
(誤降格は再現しなかったが、Rewrite自体はladder各水準を使い切り
`ladder_exhausted_without_full_rewrite`でSTAGE4、fail-closed)。
(3)meta_run03_standardは2/2ともACCEPTABLE_STAGE1(iter8の2/2 STAGE4
から一変)。同一fixture・同一コードでの結果の激変が、原因三択のうち
(b)Stage1 fresh enumeration非決定性を裏付けた(§6-14)。自動検知
(`silent_pass_candidate`、§8-8新設)による誤降格0件。
`BODY_RUBRIC_DEFAULT`をV6へ昇格した。実測合計¥6.4033(Guardrail¥15内)。
Phase累計¥462.6236+¥6.4033=**¥469.0269**/総枠¥600、残**¥130.9731**。
詳細REPORT§31。

**㉔ meta_run03_standardの人間確認をStage1の揺れから切り離して検証
(委任_34、本書§6-15参照)**: iter8のcycle1 Stage1出力(s1/s2完全同一)を
固定しreuse入力として、現行既定構成で2 run試行した
(`er052_open233_self_recovery_flow_runner_01_rep19_representative_
01.py`、`OUT_DIR_REP19`新設)。結果: sample1は3cycle完走後も
STAGE4_ESCALATION(`cycle_limit_exhausted_after_recheck`、¥6.2845)。
sample2はcycle1完了後、Guardrail到達(累計¥7.2614/¥8)で自己停止
(¥0.9769消費、結果未保存)。Stage1入力を完全固定しても収束しなかった
ことから、§6-14の「原因は(b)Stage1非決定性のみ」を「(b)は部分的要因」
へ修正し、新たに(d)deterministic floorのfact_id単位broadcast+
same_fact_id_locations enumeration複合によるcycle内非収束を追加原因
候補として特定した(§6-15)。修正の実装・再検証は予算超過のため
未実施(STOP、budget guardrail該当)。実測¥7.2614(Guardrail¥8内)。
Phase累計¥469.0269+¥7.2614=**¥476.2883**/総枠¥600、残**¥123.7117**。
詳細REPORT§32。

**㉕ 追加原因(d)の小修正実装とfrozen fixture再検証(委任_35、本書
§6-16参照)**: floorのfact_id単位broadcast廃止+same_fact_id_locations
enumerationのcycle1限定+iol_degenerate guard追加の3点を実装した
(unittest12件新規、既存292件は非回帰)。rep19と同一のfrozen fixtureを
`er052_open233_self_recovery_flow_runner_01_rep20_representative_01.py`
(`OUT_DIR_REP20`新設)で再実行した結果、両runともcycle1のblocking_claims
が2→1件(複製4件が強制BLOCKINGから解放)に収まり、rep19で観測された
検出対象の増加連鎖(2→12→5件)・「別文へ丸ごと置換」・見出し削除は
再発しなかった。sample1は3cycleで`RESOLVED_REWRITE_THEN_DOWNGRADE`
(¥2.0186)、sample2は2cycleで`STAGE4_ESCALATION`
(`ladder_exhausted_without_full_rewrite`、¥1.8301、全文Rewrite不使用の
まま安全側にfail-closed)。Safety対照(changed_number/changed_actor
full flow n=1×2+Safety-critical 8claimのうち検出可能な6claim)は
BLOCKINGからのdowngrade0件。実測¥6.0782(Guardrail¥10内)。
Phase累計¥476.2883+¥6.0782=**¥482.3665**/総枠¥600、残**¥117.6335**。
詳細REPORT§33。

**㉖ rep20 sample2の`ladder_exhausted_without_full_rewrite`根本原因
特定と小修正(委任_36、本書§6-17参照)**: claim_textが記事中の非隣接2文を
“…” and “…”で結合した合成claimの場合、既存`locate_target()`が1文fuzzy
matchしか試みず一方の断片しか捕捉しないことを決定論的に特定し(¥0)、
`extract_all_quoted_fragments`/`locate_multi_quote_span`を新設して
`locate_target`/`run_paired_local_rewrite`のja_target決定へ組み込んだ
(unittest13件新規、既存304件は非回帰、計317件PASS)。rep19/rep20と
同一のfrozen fixtureをn=2+Safety対照(changed_number、n=1)で再実行した
結果、sample2(本委任の修正対象)は`RESOLVED_REWRITE_THEN_DOWNGRADE`
(2cycle、¥1.2052)でSTAGE4を解消した(本run自体では2断片合成claimの
形は非決定性により再現せず、修正の有効性は決定論的unittestで確認)。
sample1は逆に新規`STAGE4_ESCALATION`(`cycle_limit_exhausted`)と
なったが、本委任の修正とは無関係(新規コードパス不発火を決定論的に
確認)な別の非決定性(変種(e)、1つの引用が複数文にまたがる場合の既知の
限界)と特定し、修正は本委任のスコープ外として報告のみに留めた。
Safety対照はfloorが引き続き正しく発火(downgrade0件)。project-wide
regression(`run_project_regression.py`)でも本委任由来の新規failure
なしを確認した。実測¥3.561(Guardrail¥7内)。Phase累計¥482.3665+
¥3.561=**¥485.9275**/総枠¥600、残**¥114.0725**。詳細REPORT§34。

## 10. リスク

| # | リスク | 緩和策 |
|---|---|---|
| 1 | retry loop化(記事が延々と自動再生成を繰り返す) | cycle上限を記事あたり2に固定(§3)。上限到達で必ずStage 4へ抜ける設計とし、上限を動的に緩めるロジックは持たない |
| 2 | cost/latency肥大 | Stage 2はBLOCKING-candidateのみに発火(Stage 1でACCEPTABLEの大多数には追加費用ゼロ)。§8のQCD測定でPhase 1から実測し、Checkpoint Dで費用推移を確認する |
| 3 | 人間確認ゼロによる新規リスク(a): Stage 2がmaterialなclaimを誤って通す | deterministic safety floor(§4-3)+rubric基準1(Ledger本体フィールドとの矛盾)で機械的に補強。Phase 1でSafety群100%維持をStage 2にも要求する受入条件として設定(次回委任で明記) |
| 4 | 人間確認ゼロによる新規リスク(b): Stage 3 Rewriteが新たな逸脱を生む | 全文Recheck(局所チェックにしない、§5-2)をfail-closedの前提とする。Hormuz run_03の実例(Advanced修正後にStandardで別claimのMAJORが新規発生)が示すとおり、これは既に現行案Bでも発生している既知のリスクであり、Self-Recovery Flowはこれを「2 cycle目で拾う」ことで緩和するが、根絶はしない |
| 5 | 人間確認ゼロによる新規リスク(c): Rewriteが構造を壊す | `split_family_x_article_text_v2()`の既存NG guardをそのまま再利用(§5-2)。guard抵触時はcycleを消費してStage 4へフォールボックする設計とし、guardを回避してRewriteを繰り返さない |
| 6 | Stage 1非決定性(recall 85〜100%、n=20実測)がStage 2以降で拡大しないか | Stage 2はStage 1がBLOCKINGと判定した場合にのみ発火するため、Stage 1が見逃した(ACCEPTABLE誤判定)ケースはStage 2の対象外のまま残る。**これはSelf-Recovery Flowでは解決されない既存のrecall問題**であり、本設計のスコープ外として明記する(self-consistency等のrecall改善策は§11でOpusへ問う別論点とする) |
| 7 | HOOK_CLAUSE衝突(Family横断時) | 前Phase Opus論点5(D)で特定済みの`changed_comparison`正面衝突は、本Flowが現時点でFamily X限定(`hook_aware=False`経路のみ)である間は無害。Stage 2/Stage 3のPrompt文言がHOOK_CLAUSEと将来同一Promptへ統合される際は、前Phase同様Family N3の危険Hook fixture 3種でregressionを回すことを必須とする(本Phaseでは統合しない) |
| 8 | Production Checkerのモデル差異(gpt-5.6-luna vs Trial gpt-6-luna) | §2/§4-6で明記済み。Phase 1はgpt-6-lunaで統一し前Phase資産と比較可能にするが、Phase 2でProduction実配線を検討する際は、Stage 1(gpt-5.6-luna、既存Production不変)とStage 2/3(Trial用に検証したモデル)のモデル差自体がSafety regressionを生まないかの追加確認が必要になる(Opus論点として§11に計上) |
| 9(委任_02追加) | コスト肥大(loop×高単価)。特にStage 3 JA全文Rewrite(案B相当、1回¥3.49〜4.02)を2 cycleとも使い、かつAdvanced/Standard両方が同時にBLOCKING確定するworst caseでは、§13の試算上+¥3/記事Capを超過し得る(期待値ベースでは大きく下回るが、稀なworst case記事では超過し得る) | cycle上限(記事あたり最大2、既存設計)を維持しつつ、§13で示す優先順位(局所Rewriteを優先しJA全文Rewriteの発火自体を減らす)で緩和する。それでもP95/worst caseがCapに接近する場合は、次項(#10)のUSER_DECISION_REQUIRED条件に従う |
| 10(委任_02追加) | Cap超過時のUSER_DECISION_REQUIRED条件 | Phase 1実測で(a)記事あたり期待追加コストの中央値シナリオが+¥3を超える、または(b)worst case/P95が恒常的(稀な例外でなく一定割合)に+¥3を超える、のいずれかが判明した場合、勝手にコストを積み増さず、§13の「+¥3以下で困難な場合の中間報告」項目に従い直ちにUSER_DECISION_REQUIREDとして報告する(委任文2026-09-30ユーザー追加指示) |

## 11. Opus L2に問う論点(委任_03で8項目へ整理、ユーザー指定の批判対象軸)

以下8項目は、ユーザーが批判的レビュー対象として明示指定した軸
(Self-Recovery全体設計/Stage 1設計/Second Judge/Rewrite戦略/Safety/
Cost/loop化リスク/Escalationゼロの現実性)にそのまま対応する。各項目に
「本設計の暫定答え」と「批判してほしい点」を付す。

### 11-1. Self-Recovery Flow全体設計

**暫定答え**: 4段階(Initial Check→Re-screening→Rewrite→Escalation)
は、Stage 1のSafety資産保存(Prompt不変維持の原則、ただしStage 1自体は
V4A採用へ変更、§14)・Stage 2のfail-closed tie-break・cycle上限2による
loop制御・deterministic floorの4層で、KPI(USER_DECISION_REQUIRED実質
ゼロ・重大Fact見逃し0件・+¥3/記事以内)を同時達成することを狙う。
**批判してほしい点**: 4段階という構成自体が最適か(例えば3段階[Stage 2
とStage 3を1回のLLM呼び出しで「materiality判定→必要ならrewrite_hint
生成」まで一体化する案]の方が呼び出し回数・コストを削減できるのでは
ないか)。Stage 2/3を分離する設計上の利点(materiality判定とrewrite_hint
生成を別々に検証できる)は、コスト増加分に見合っているか。

### 11-2. Stage 1設計

**暫定答え**: 真のProduction Checker(V0)は`changed_actor`を50%
(3/6)見逃す実測があり、Stage 1が検出しない限りStage 2以降は発火
しないという構造的事実から、Trial variant V4A(changed_actor 5/5、
Safety群12/12維持)を採用した(§14で確定)。真のProduction Prompt自体は
無変更のまま。**批判してほしい点**: V4A採用はhormuz_run03_standardの
n=20実測でV0比検出率が悪化する方向(100%→85%、統計的有意差なし)を
伴う。Safety観点で「1カテゴリ[changed_actor]を救うために別カテゴリ
[changed_scope]の検出率が[統計的に有意でないとはいえ]下がる可能性が
ある」trade-offを許容する設計判断は妥当か。deterministic pre-check
(§14、machine照合による補助検出、¥0)がこの残存リスクを十分に
補完できるという評価は正しいか。

### 11-3. Second Judge(Stage 2)設計

**暫定答え**: 独立Prompt・別call(前Phase Opus論点1推奨4)、
deterministic safety floor(5フラグ)、fail-closed tie-break。入力は
段落±1+Ledger全文(§4-4、委任_03で記事全文から縮小確定)。**批判して
ほしい点**: floor対象外のchanged_causality/changed_scope等でmaterialな
ケース(B3/hormuz_run03_standard)を、rubric文言だけで安全に止められる
という設計判断は十分か。段落±1への入力縮小(§4-4)が、B3のような
「離れた箇所[conditions]に別原因が記載されている」ケースの判定精度を
落とさないか(Ledgerは全文のまま渡すため直接の影響は限定的と考えるが、
記事側の文脈縮小が`qualifier_present`等の判定に影響しないかは未検証)。

### 11-4. Rewrite戦略(Stage 3)

**暫定答え**: JA側は既存案B(全文差し戻し、Production code再利用)、
EN側は局所Rewrite(§5-2、Phase 1で新規実装、既存NG guard再利用)。
Recheckは全文Checker(fail-closed優先)。**批判してほしい点**: 局所
Rewrite(§5-2)は、全文再生成(既存案B/既存must-fix retry)と比較して
Safety/生産性のトレードオフ上、優先的に実装する価値があるか。Hormuz
run_03の実例(全文再生成が新しい逸脱を誘発)は局所Rewriteの必要性を
示す十分な根拠か、それとも単なるn=1の偶発事象か。

### 11-5. Safety(重大Fact見逃し0件の維持可能性)

**暫定答え**: deterministic safety floor(5フラグ、昇格のみ)+rubric
基準1(Ledger本体フィールドとの矛盾)+全文Recheck(fail-closed)+Stage 1
V4A採用(§14)の4層で、Safety群100%維持を狙う。Stage 1のrecall
非決定性(n=20実測85〜100%)自体はこのFlowで解決されない(§10リスク6)。
**批判してほしい点**: Stage 1が検出しなかった(ACCEPTABLE誤判定の)
ケースは、Self-Recovery Flow全体の対象外のまま残る(Stage 2以降が
発火しない)という構造的限界は、「重大Fact見逃し0件」というPrimary
Safety KPIと矛盾しないか。矛盾するとすれば、KPI達成の前提として
Stage 1側のrecall改善(self-consistency等)が不可欠ではないか、それとも
§14のdeterministic pre-check(machine照合)で実務上十分と言えるか。

### 11-6. Cost(+¥3/記事Cap)

**暫定答え**: 案γ(Stage 1[V4A]固定費+BLOCK時のみStage 2+必要時のみ
局所/JA Rewrite、cycle上限2)が第一候補。§14でのV4A採用に伴う固定費
増(+30%/call)を織り込んで再計算した結果、楽観/中央シナリオは依然
節約方向、悲観シナリオは+¥1程度、**worst case(tail)はV4A採用前の
¥2.88から¥3.7〜3.8程度まで悪化し、Cap[+¥3]を超過する可能性がある**
(§13-7更新版、要Phase1実測)。**批判してほしい点**: 中央値シナリオは
Cap内で節約方向のまま維持できているが、worst caseがCapを超過し得る
という新しい結果は、「両Advanced/Standardが同時BLOCK、かつJA全文
Rewrite後もcycle2まで必要」という稀な尾部シナリオに限定される。この
tail riskをCap判定上どう扱うべきか(委任文のUSER_DECISION_REQUIRED
条件は「worst case/P95が恒常的[稀な例外でなく一定割合]に+¥3を超える」
場合としているが、本件がこの条件に該当するかはPhase 1実測が必要)。

### 11-7. loop化リスク

**暫定答え**: cycle上限を記事あたり2に固定、上限到達で必ずStage 4へ
抜ける設計とし、上限を動的に緩めるロジックは持たない(§10リスク1)。
**批判してほしい点**: cycle上限2は、Safety(重大fixture見逃し0件維持)と
生産性(USER_DECISION_REQUIRED実質ゼロ)のバランスとして妥当か。2回で
足りないケース(Hormuz run_03のような「2箇所で別々のja_source MAJOR」
パターンが3箇所以上に増える場合等)への備えは十分か。cycle上限自体は
ユーザー指定の固定値(委任文既定)であり本Phaseでは変更しないが、
上限に達した場合のフォールバック(Stage 4)が「安全側だが生産性を
失う」という設計選択で正しいか。

### 11-8. Escalationゼロの現実性

**暫定答え**: Stage 4 Escalation発生率を実質ゼロに近づけることが
Primary KPIそのものである。ただしこれは「従来なら人間が見ていたはずの
Grayゾーンの判断を全てシステムに委ねる」ことを意味する。**批判して
ほしい点**: Stage 4 Escalation発生率を実質ゼロに近づけること自体が、
人間確認ゼロの記事が増えることを意味する。これは「安全≠成功」原則
(PM_GOVERNANCE.md 6節)との関係でどう位置づけるべきか。Escalationが
「本当に例外的なケースだけ」に留まっているかを、Human Review無しの
運用下でどう継続的に検証すべきか(Phase 1/2のTrialで測定する指標以外に、
Production化後に必要な継続監視の仕組みはあるか)。

**[委任_04追記/A16] Production化後の継続監視案(Phase 2設計項目、
Opus論点8(D)への回答。採用判断はユーザー)**: (1) shadow sampling
(公開記事の5〜10%を対象に、公開後2回目のStage 1 Checkを別runで実行し
初回と不一致[2回目でMAJOR]なら人間へ通知、コスト¥0.03〜0.06/記事
相当でCap内)、(2) QUALITY通過件数の週次レビュー(claim単位サンプル、
品質下限が下がっていないかの事後確認)、(3) 決定論的指標の常時監視
(¥0。precheck発火率/Rewrite適用文字数/cycle消費率/`all_prior_issues_
resolved=false`率)。Human Reviewを通常運用にしない制約と両立する
(全数審査ではなくサンプリング+機械指標)。**これらはPhase 2設計項目
として記録するのみで、本Phase 1では実装しない**。

### 11-補. その他の既存論点(委任_02までに提起、削除せず維持)

- Production Checkerモデル(gpt-5.6-luna)とPhase 1 Trialモデル
  (gpt-6-luna)の不一致(§10リスク8)は、Phase 1の結論をPhase 2
  (Production相当10〜20記事)へ一般化する上でどの程度の障害になるか。
- HOOK_CLAUSE整合(§10リスク7)について、Stage 2/Stage 3のPrompt文言を
  将来共通Promptへ統合する際の優先順位付け(前Phase Opus論点5推奨4
  「HOOK_CLAUSE優先、それ以外は重複true原則」)は、本Flowのmateriality
  軸導入・V4A採用とどう組み合わせるべきか。

## 12. USER_DECISION_REQUIRED条件(委任_03で全面置換、ユーザー指定7項目)

**本設計書自体はUSER_DECISION_REQUIRED非該当**(文書のみ、API呼び出し
なし、実装なし、Production変更なし、¥0)。以下がユーザーが明示指定した
STOP条件の全て(2026-09-30委任文§1、原則これのみ)。これ以外の細かい
実装判断(Trial専用Prompt/schema variant・deterministic rule・Second
Judge・Rewrite方法・regression fixture・retry構造等)はGuardrail
(KPI・Safety・Cap・Production非変更)内でFable/Claudeが自律的に改善する
範囲であり、逐一ユーザー確認を求めない。

1. **KPI自体の変更**(Primary=USER_DECISION_REQUIRED 0件、Safety=重大
   Fact見逃し0件、Cost=+¥3/記事以内、のいずれかを変更する場合)。
2. **重大Fact Safetyの緩和**(Fact反転/actor取り違え/number・numeric
   scope重大変更/negation反転/comparison方向反転/time・chronology重大
   変更/unsupported material fact/主要Fact理解を変えるcausalityを
   「止めない」方向へ変更する場合)。
3. **+¥3 Cap超過が必要と判断した場合**(期待値ベースで超過が必要、
   または恒常的にCap超過が避けられないと判明した場合)。
4. **Production正式採用・配線**(Self-Recovery Flow全体、またはStage 1
   のV4A化のような個別要素をProduction Prompt/schema/Validator/
   routing/runnerへ組み込むこと自体)。
5. **Family X以外への正式展開**。
6. **新Product原則の設定**。
7. **予算¥400超過**。

**該当有無(委任_03時点)**: いずれも非該当。§14でのStage 1(V4A)採用は
条件2(Safety緩和)ではなく**Safety改善**(changed_actor検出率50%→
100%)であり、真のProduction Prompt自体は無変更のため条件4にも非該当。
§13で再計算したworst case(¥3.7〜3.8程度、要Phase1実測)はCapの中心
シナリオ(楽観/中央)を超えるものではなく、条件3の「超過が必要」という
判断はまだ行っていない(Phase 1実測前の概算のみ)。ただしこの点は
Checkpoint Aで明示的に報告し、Phase 1実測で悪化が確認された場合は
直ちに条件3としてUSER_DECISION_REQUIRED化する。

**[委任_04追記]** Opus L2レビュー#1(論点8(A)(D)、論点6(D))が提起した
以下3点は、Fable/Claudeが独断で決めず**ユーザー判断事項としてCheckpoint
Aで提示する**(条件1[KPI変更]に触れるため): (1) KPI判定方法の再定義
(記事単位「0件」→事象単位の段階別成功率から推定したEscalation率の
信頼区間上限、統計的検出力の観点で0/10〜20記事は実質ゼロの証拠になら
ない[Wilson上限0/20で約16.8%]という指摘への対応)、(2) Cap定義の解釈
確認(純増分がLedger/Deviation Check関連LLMコストに限るか、TTS等の
downstreamコストを含むか)、(3) QUALITY通過(現行STOPしていたB2型を
人間を通さず公開すること)が条件2(Safety緩和)に該当するかの判断。
**本設計書は現行KPI文言のまま進める**(記事単位「0件」を主要KPIとして
維持)。ただし上記(1)の「事象単位推定によるEscalation率」と「Escalation
0件の内訳」(§8-1、A13)は、KPI文言そのものを変更せず**追加報告項目**
としてPhase 1から併記する。

### 12-1. Checkpoint Aで提示する項目一覧(委任_02追加・委任_03更新、
2026-09-30ユーザー追加指示、各Mandatory Checkpointで必須報告)

- best variant(現時点の第一候補=§13-8案γ、Stage 1=V4A[§14])の追加
  コスト/記事(期待値)。
- 固定追加費(Stage 1[V4A化]分の増分を含む、§13-2/§14で再計算)。
- 条件付き追加費(Stage 2以降、BLOCKING-candidate発生時のみ)。
- BLOCK時のみ発生する平均recovery費用(Stage2+Rewrite+Recheck合計)。
- P50/P95(記事あたり追加コスト)。
- +¥3/記事Capまでの余裕(シナリオ別、worst caseのCap超過リスクを
  含む、§13-7更新版)。
- 現在best variantの重大Fact見逃し状況(Stage 1[V4A]のSafety実測、
  §14)。
- 上記に加え、本書§7-0のclaim単位確定ラベル・§12の7項目該当有無
  (現時点はいずれも非該当)の確認。
- **[委任_04追記]** Escalation 0件の内訳(真の解消/QUALITY通過/
  `all_prior_issues_resolved`未確認/誤PASS候補、§8-1 A13)。
- **[委任_04追記]** 事象単位推定によるEscalation率(信頼区間上限、
  上記12節追記(1)への回答が出るまでの参考値として)。
- **[委任_04追記]** JA-origin比率実測値(暫定80%、n=5)とn拡大の有無。
- **[委任_04追記]** paired local rewrite(§5-4)の型別成功率・guard
  抵触率・実単価。
- **[委任_04追記]** worst case式(§13-6)の`n_claim`実測分布とCap判定
  レンジ(単一数値ではなく幅で報告)。

## 13. コストモデルと+¥3/記事 Cap(委任_02新設、2026-09-30ユーザー
追加指示)

**前提**: ユーザー指示は「+¥3まで使ってよい」ではなく「できる限り安く
達成する」が大前提であり、同品質・同自動完結率なら安い方式を優先する。
本章はその判断材料を提供する。全数値は**Phase 1実測前の概算**であり、
Phase 1実行後に実測値へ更新する(既存章と同じ「概算(要実測)」の
位置づけ)。

### 13-1. 単価根拠(一次ソース、推測禁止)

| model | Input | Cached input | Output | 出典 |
|---|---|---|---|---|
| gpt-5.6-luna(現行Production Stage 1) | $0.20/1M | $0.02/1M | $1.20/1M | `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§C-2(`platform.openai.com/docs/pricing`一次ソース確認済み) |
| gpt-6-luna(前Phase Trial、Stage 2/3候補) | $0.10/1M | $0.01/1M | $0.50/1M | 同上(gpt-5.6-lunaの正確に半額) |

為替: ¥156.88/USD(Frankfurter API、ECB参照レート、2026-09-28付、同
レポート§C-4)。

**call単位の実測参考値**: 同レポート§C-3(固定fixture 84 call実測)で
gpt-5.6-luna 平均¥0.4911/call・中央値¥0.3719/call、gpt-6-luna 平均
¥0.2043/call・中央値¥0.1818/call。本委任でユーザーが指定した「1 call
≈ ¥0.49」(gpt-5.6-luna)はこの平均値と一致し、本章の基準単価として
採用する。

**新規Evidence(本委任で追加実測)**: 実Production run(`FAMILY-X-
REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`Meta run_03、`er019_output/
family_x_refresh_e2e_01/meta/run_03/raw_usage_log.jsonl`)のWriter段
7 call分を、上記単価で本委任にて独立に再計算したところ合計¥4.13
(レポート記載の実測¥4.213と概ね一致、キャッシュトークン未計上分の
誤差)。個別call費用は¥0.04(Advanced deviation check、MAJOR無し・
出力短)〜¥1.29(Standard deviation check、MAJOR検出・reasoning出力
大)まで幅があり、**harness平均¥0.49は中心値として妥当だが、BLOCKING
検出時のcallはより高コストになりうる**ことを実データで確認した(本
発見は§13-4のStage 2単価見積りの保守化根拠として使う)。

### 13-2. 現行Production Checker(Stage 1)の構成とベースライン費用/記事

`er012_e_family_entertainment_two_level_runner_01.py`の実装(L381-388
Advanced deviation check、L477-484 Standard deviation check)から、
**通常ケース(いずれもMAJOR無し)の現行Checker構成は2 call/記事**
(Advanced 1回+Standard 1回)と確定できる。

- ベースラインStage 1費用(通常ケース) = 2 call × ¥0.49 ≈ **¥0.98/記事**。
- 既存retry込み(BLOCKING発生時、**Self-Recovery Flow導入前から存在
  する現行Production仕様**であり新規コストではない): EN側must-fix
  retry1回(全文再生成+再deviation check)、ja_source起因なら既存案B
  (JA全文差し戻し、実測¥3.487[Meta run_03、must-fix込み]〜¥4.018
  [Hormuz run_03])。実測: Meta run_03 Writer段合計(Advanced+Standard、
  must-fix retry込み)¥4.213。

### 13-3. Stage 2入力設計(§4-4)と§9-1見積りの不整合(委任_03で解消)

§4-4はStage 2の入力に「記事全文」「Ledger全文」を明記していたが、
§9-1(Phase 1費用見積り)は「入力がclaim単位で短い(Stage 1の1/3〜
1/2程度)」という楽観的仮定でStage 2単価¥0.10〜0.20と見積もっていた。
**両者は矛盾していた**(§4-4どおりなら入力サイズはStage 1と同程度)。
**委任_03で解決**: §4-4を改訂し、Stage 2入力を「記事全文」ではなく
「**対象claimを含む段落±1段落**+Ledger全文+source context+Stage 1
deviation出力」へ縮小確定した(作業D、Fable第一候補)。Ledgerは
fail-closed優先で全文のまま維持する(§4-4改訂理由参照)。この縮小に
より入力トークン量は記事全文渡しより減るが、**縮小幅の実測はまだ
無い**ため、本章のCap判定は引き続き**保守的な¥0.30〜0.40/call
(gpt-6-luna)を維持**する(楽観的すぎる見積りで節約を過大評価しない、
fail-closedの原則を費用推定にも適用)。段落±1縮小の実際の削減効果は
Phase 1最優先実測項目とする。

### 13-4. Stage別 unit cost見積り(Phase 1実測前、外挿ベース)

| 項目 | 見積り(保守的、§4-4全文入力前提) | 見積り(楽観的、§9-1想定) | 根拠 |
|---|---|---|---|
| Stage 2(gpt-6-luna) | ¥0.30〜0.40/call | ¥0.10〜0.20/call | 保守的=Stage 1 gpt-6-luna実測平均(¥0.2043)に近い水準へ、出力schema縮小分を差し引きつつ材質判定reasoningの追加分を加算した外挿。楽観的=§9-1原文 |
| Stage 2(gpt-5.6-luna) | ¥0.65〜0.85/call | ¥0.35〜0.45/call | gpt-6-luna比、公式単価が正確に2倍のため概ね2倍で換算 |
| Stage 3局所Rewrite(EN、1〜2文のみ) | ¥0.15〜0.35/call | — | 実測(Meta run_03 Standard must-fix全文regen ¥1.106)の出力トークン規模比から、局所編集は出力トークンが1/5〜1/8程度と推定した外挿。**未実装・未実測(Phase 1で新規測定)** |
| Stage 3全文Rewrite(EN、既存must-fix retry baseline) | ¥1.1〜1.3/call | — | 実測(Meta run_03 Standard must-fix regen ¥1.106) |
| Stage 3 JA全文Rewrite(案B) | ¥3.49(Meta run_03実測、must-fix込み)〜¥4.02(Hormuz run_03実測) | — | `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`実測 |
| Recheck(全文Checker再実行) | Stage 1と同一単価(gpt-5.6-luna ¥0.49、Trial gpt-6-luna ¥0.20) | — | §5-2「全文Checker再実行」 |

以降のCap判定は**保守的見積り+Stage 2はgpt-6-luna**を基準ケースとする
(Fable第一候補、委任文§2)。gpt-5.6-lunaをStage 2に使う案は§13-7で
比較のみ行う。

**[委任_07実測、Stage2実単価確定]** §4-7の実測により、Stage2(claim
単位、per-claim、§4-4確定入力)の実単価は**¥0.087〜0.112/call**
(B4/B1実測4件平均¥0.1013)であり、上表の「楽観的¥0.10〜0.20/call」
に近い水準であることが確認された(「保守的¥0.30〜0.40/call」ほど
高くない)。**batch化(instance単位1call)を使う場合**、B4(4claim)
=¥0.1862/call・B1(2claim)=¥0.127/callで、**claim数で正規化した
実効単価はさらに下がる**(B4: ¥0.0466/claim相当)。**prompt caching
併用時**はcall全体費用が63〜64%減(§4-7)であり、Stage2を連続して
複数claim・複数記事へ適用する運用(同一Ledgerの記事群を連続処理)では
Ledger prefix共有によりさらに安価になる可能性がある(未実測、Phase 2
候補)。**結論**: §13-3が「削減効果は未実測」としていた段落±1縮小は
実際に機能しており(§4-4の入力設計どおり)、Stage2単価に関する
§13-10課題1(「Stage2の真の単価が最大の不確実性要因」)は
**解消方向(実測¥0.10前後、保守的見積りの下限に近い)**。§13-5〜
§13-9の期待値・worst case式の`c_stage2`変数は、次回委任(⑤⑥実測後)
で実測値へ差し替え、Cap判定を再計算する(Stage3実単価[局所Rewrite]が
未確定のため、本委任では式の再計算は行わない)。

### 13-4-補. Stage 1のV4A採用に伴う単価再計算(委任_03、§14で確定)

§14でStage 1をV0からV4Aへ変更したため、Stage 1呼び出し(初回2 call)と
Recheck(Stage 1相当の全文Checker再実行)の単価が**call単価+30%**
(前Phase実測、gpt-6-luna基準)上がる。§13-2以降の費用モデルは実
Production単価(gpt-5.6-luna、¥0.49/call)を基準に組み立てられている
ため、同じ+30%倍率をgpt-5.6-luna単価へも外挿する(**Prompt文字数増加
という単価に依存しない要因が主因のため比例関係が近似的に成立すると
仮定、未確認・Phase 2でのgpt-5.6-luna実測で要検証**)。

- V4A Stage 1単価(外挿) = ¥0.49 × 1.30 ≈ **¥0.637/call**。
- **Stage 1固定費の増分(常時、全記事)**: (¥0.637−¥0.49)×2 call ≈
  **+¥0.294/記事**(BLOCK有無に関わらず全記事で発生、既存¥0.98/記事
  ベースラインに上乗せ)。
- **Recheck費用の増分(BLOCK時のみ、cycleごと)**: JA-path recheck
  (2 call)は¥0.98→¥1.274(+¥0.294/回)、EN-path recheck(1 call、
  instance単位)は¥0.49→¥0.637(+¥0.147/回)。
- **rewrite+recheck加重平均の再計算**(§13-5の式に使う値):
  JA 40%×(JA rewrite¥3.7+recheck¥1.274=¥4.974)+EN 60%×(全文regen
  ¥1.2+recheck¥0.637=¥1.837) = 1.9896+1.1022 = **¥3.0918/instance**
  (旧¥2.886から+¥0.206)。

以降、§13-5〜§13-10はこの再計算値を反映した更新版とする(旧数値は
「V4A採用前(参考)」として残す)。

### 13-5. 発動率シナリオと「+¥3/記事」の定義

ユーザー指示の「量産時に増加する継続コスト」は文字どおり**新方式の
総コスト − 現行方式の総コスト**(純増分)であり、Self-Recovery Flow
全体の絶対支出額ではない。現行Production は**BLOCKING検出時、Second
Judgeの判断を待たずに無条件でEN側must-fix retry1回・ja_source起因なら
案B全文差し戻し1回を実行する**(§13-2)。Self-Recovery FlowはStage 2で
まずBLOCKING/QUALITY/ACCEPTABLEを判定し、QUALITY/ACCEPTABLEに降格
できた場合はこの既存retry/案Bの実行を**回避**できる(コスト削減)。
一方、Stage 2確認後もBLOCKINGが残るケースでは、現行が持たない
**cycle 2**(2巡目のRewrite+Recheck)を追加実行できる(コスト増、
ただしUSER_DECISION_REQUIRED回避という便益と表裏)。

BLOCK発生率・Stage 2解消率・cycle 2必要率は**Phase 1未実測**のため、
既存E2E実測(Hormuz run_01〜03は3回ともja_source起因のBLOCKで最終的に
Standard段STOP、Meta run_03はStandard 1回のmust-fix retryで解消)と
前Phase B群診断(不要BLOCK率75%、n小)を参考に、3シナリオで幅を持たせる
(**いずれも仮置き、Phase 1で実測必須**)。writer-stage-instance
(Advanced/Standard、記事あたり2件)単位のBLOCK率と条件分岐:

| シナリオ | BLOCK率/instance | Stage2で解消(Rewrite不要)率 | cycle1で解消/cycle2必要/Escalation(Rewrite必要側の内訳) | JA-origin比率(Rewrite必要側) |
|---|---|---|---|---|
| 楽観 | 15% | 70% | 90% / 10% / 0% | 40% |
| 中央 | 35% | 50% | 75% / 20% / 5% | 40% |
| 悲観 | 60% | 30% | 55% / 30% / 15% | 40% |

**計算式**(Stage2単価=¥0.35/call[gpt-6-luna、保守的]、rewrite+
recheckの加重平均=**¥3.0918/instance**[§13-4-補、V4A Recheck単価
反映済み]):

`純増分/instance = Stage2単価 − P(Stage2で解消)×既存rewrite+recheck費用
 + P(cycle2必要)×(Stage2単価+rewrite+recheck費用)`

| シナリオ | 純増分/instance(V4A反映後) | 純増分/instance(V4A採用前、参考) |
|---|---|---|
| 楽観 | −¥1.47 | −¥1.57 |
| 中央 | −¥0.51 | −¥0.69 |
| 悲観 | +¥0.46 | +¥0.50 |

**記事あたりの純増分(V4A反映後)** = 純増分/instance×2 instance×
BLOCK率 + **Stage1固定費増分¥0.294/記事**(§13-4-補、BLOCK有無に
関わらず常時加算):

| シナリオ | 条件付き部分(instance×BLOCK率) | +Stage1固定費 | **純増分/記事(V4A反映後)** | 参考(V4A採用前) |
|---|---|---|---|---|
| 楽観 | −¥0.44(15% BLOCK) | +¥0.294 | **−¥0.15/記事(節約)** | −¥0.47 |
| 中央 | −¥0.36(35% BLOCK) | +¥0.294 | **−¥0.06/記事(節約、僅少)** | −¥0.48 |
| 悲観 | +¥0.55(60% BLOCK) | +¥0.294 | **+¥0.84/記事** | +¥0.60 |

**結論(期待値ベース、V4A反映後)**: 楽観シナリオは依然節約方向、中央
シナリオも僅かに節約方向だが**margin縮小**(−¥0.48→−¥0.06)。悲観
シナリオは+¥0.84/記事に増加したがCap(+¥3)に対しなお余裕がある。
V4A採用(Stage 1のSafety改善)の代償として、期待値ベースの節約効果は
縮小するが、いずれのシナリオもCap内に留まる。

### 13-6. Worst case / P95(**[委任_04改訂/A6]** 式化・二重計上精査・
JA-origin比率実測反映)

期待値とは別に、稀な記事でCapを超過しないかを確認する。**Opus所見
(論点6(B))のとおり、旧版は§3-5(Stage2 call数=2×claim数)と§13-6の
「2 call固定」計算が不整合であり、かつ案B実測¥4.02には
`_run_writer_stage_once(only=None)`の再実行[Advanced+Standard生成+
deviation check]が既に含まれているため、旧版の「2段recheck¥1.274」を
別途加算するのは二重計上の疑いがある。以下、claim数を変数とした式へ
書き換え、二重計上を除去する。**

**変数定義**: `n_claim`=検出claim数/instance(実測前は1〜4と仮定、B4実例
で4件)、`c_stage2`=Stage2単価(gpt-6-luna、保守的¥0.30〜0.40/call、
§13-4)、`c_ja_full`=JA全文Rewrite実測(¥3.49〜4.02、うちAdvanced/
Standard再実行の全deviation check込み)、`c_en_local`=EN局所Rewrite
(¥0.15〜0.35/call、未実測・Phase1で実測)、`c_recheck_ja`=JA全文
Rewrite後のRecheck(**案B実測¥4.02に含まれる分は除き、追加で発生する
Advanced/Standard分のみ**、V4A単価¥0.637×2=¥1.274)、`c_recheck_en`=
EN局所Rewrite後のRecheck(V4A単価¥0.637×1=¥0.637)。

**式(cycle 1でJA側フォールバック[旧案B]、cycle 2でEN局所を使う
worst caseパターン)**:

`worst_case = [n_claim×c_stage2 + c_ja_full] (cycle1)
 + [n_claim×c_stage2 + n_claim×c_en_local + c_recheck_en] (cycle2)
 + Stage1固定費増分(¥0.294/記事)
 − 現行方式が同じ記事に対し1 cycleのみでSTOPする費用(c_ja_full+
   c_recheck_ja相当[現行はV0のためV4A差分は除く])`

`n_claim=1`(旧版相当)を代入すると、
worst_case ≈ (0.35+4.02) + (0.35+0.35+0.637) + 0.294 − (4.02+0.98)
≈ 4.37+1.337+0.294−5.00 = **¥3.00〜4.00程度**(単価レンジの幅により
変動、旧版¥3.96はこのレンジ内)。`n_claim=4`(B4実例の上限)を代入すると
Stage2部分が+¥1.4程度増え、worst_caseは**¥4.4〜5.4程度**まで悪化しうる。

**結論(A6)**: worst caseは**¥3.0〜5.4程度の幅**を持つ(claim数・
単価レンジ双方の不確実性による±¥1〜1.5超の誤差)。**単一数値(旧版
¥2.88/¥3.96)でのCap判定はしない**。Phase 1実測(§9-1③④⑤)で
`n_claim`の実際の分布とStage2/Rewrite実単価を確定した後に、上記式へ
代入してCap判定を行う。

**JA-origin比率の実測反映**: 旧版は§13-5でJA-origin比率を仮置き40%
としていたが、実データ(Hormuz run_01〜03+Meta run_03、n=5)は
**4/5=80%**であり、40%を支持していない。以後の期待値計算(§13-5)は
JA-origin比率**実測80%(n=5、要Phase1追加実測でnを増やす)**を使う
(旧40%は参考として残す)。worst case側は元々JA-origin前提の式であり
比率変更の影響を受けない。

**BLOCK率(V4A)の扱い**: 旧版の15/35/60%(楽観/中央/悲観)という
BLOCK率は据え置きのままV4A採用を反映していない不整合があった
(Opus論点2(B))。**この数値は§9-1③の実測(negative候補7記事のV4A
再実行)後に置換する**。実測前の暫定値として残すが、Cap判定の根拠
には使わない。

**発生確率(概算、中央シナリオの独立近似)**: この worst caseは
「Advanced/Standard**両方**がBLOCK」×「JA-origin(実測80%)」×
「cycle 2まで必要」の複合条件で発生する稀な尾部事象であり、概算発生率は
**記事あたり約1%程度**(粗い近似、Phase 1実測が必要)。委任文の
USER_DECISION_REQUIRED条件3-3「worst case/P95が**恒常的[稀な例外で
なく一定割合]**に+¥3を超える」には現時点では該当しないと判断するが
(尾部確率が低いため)、**この判断はPhase 1実測前の概算に基づく**。
Phase 1実測でこのtail確率が想定より高いと判明した場合、または
`n_claim`実測分布が上限側[3〜4件]に寄っている場合は直ちに報告する。

**設計制約を守らない場合(参考、不採用のはずの経路)**: 2 cycleとも
JA全文Rewriteを使うと純増分はさらに悪化する(V4A採用前で既に
¥6.40/記事、V4A反映後はより高い)。これは§5-3の「同一記事で案Bを
2回使わない」制約が**Cap遵守にとって構造的に必須**であることを裏付ける
(実装時に確実に守るべきguard、V4A採用によりこの制約の重要性は
さらに増した)。

### 13-7. Cap判定まとめ(委任_03でV4A反映へ更新)

| シナリオ/モデル | 期待値(純増分/記事、V4A反映後) | worst case(§5-3制約遵守、V4A反映後) | +¥3 Cap判定 |
|---|---|---|---|
| 楽観、Stage1=V4A、Stage2=gpt-6-luna | −¥0.15(節約) | 未算出(複合発生率が悲観よりさらに低い) | Cap内、余裕大 |
| 中央、Stage1=V4A、Stage2=gpt-6-luna | −¥0.06(節約、僅少) | ¥3.96(**Cap超過、約¥0.96オーバー**) | **期待値はCap内だがworst caseはCap超過(§13-6、tail確率約1%と推定)** |
| 悲観、Stage1=V4A、Stage2=gpt-6-luna | +¥0.84 | ¥3.96〜(悲観ではworst case発生率自体が上昇) | 期待値はCap内、worst caseはCap超過。要Phase1実測確認 |
| 中央、Stage2=gpt-5.6-luna(参考) | 約+¥0.1〜0.3(Stage2単価2倍のため節約消失) | 約¥4.2〜4.5(Cap超過方向、V4A分も加算) | **Cap超過リスクさらに高い、gpt-6-luna推奨の根拠は維持** |

Stage 2にgpt-6-lunaを使う案が、gpt-5.6-lunaを使う案よりCap遵守に
明確に有利な点は維持される(§2でFableが示した第一候補と整合)。
**新規の知見(委任_03)**: V4A採用(Stage1 Safety改善)により、**期待値
ベースの結論(楽観・中央=節約、悲観=Cap内)は維持されるが、worst
case(稀なtail)は+¥3 Capを超過する**。§13-6のとおりtail発生確率は
概算約1%と低いと推定されるため、現時点ではUSER_DECISION_REQUIRED
条件3(Cap超過が「恒常的」)には該当しないと判断するが、Phase 1実測で
この判断を検証する必要がある(§13-10で詳述)。

### 13-8. 段階案 α〜δ(優先順位①→④に沿った比較)

| 案 | 内容 | 追加call | 純増分/記事(期待値) | 到達見込み(自動完結率) |
|---|---|---|---|---|
| α | Stage 1 Prompt改善のみ(V4-A/C2相当) | 0 | ¥0(固定費0、条件付き費0) | 前Phase実測でchangedカテゴリ検出力は改善するが、不要BLOCK率課題(実測75%)は未解消。USER_DECISION_REQUIRED実質ゼロには届かない見込み(Second Judge層が無いため過剰BLOCKを吸収できない)。Production Prompt変更自体もユーザー承認事項として別途必要 |
| β | α + BLOCK時のみStage 2 | BLOCK時のみ+1〜2call | ほぼ¥0(Stage2単価分のみ、Rewrite無し) | False・borderline群(B1-a/b、B4-b/c)はStage2で救済見込みだが、Real-but-fixable群(B1-c/B3/B4-a)やHormuz型の複数箇所逸脱はcycle無しでは解消できず、USER_DECISION_REQUIRED残存の可能性が高い |
| γ | β + 必要時のみ局所/JA Rewrite(cycle上限2) | §13-5参照 | 楽観/中央: 節約、悲観: +¥0.60(§13-7) | Primary KPI(USER_DECISION_REQUIRED実質ゼロ)に最も近づく設計。Hormuz run_03型(複数箇所で別々のBLOCKING)もcycle2で吸収可能 |
| δ | γ + 限定self-consistency/Second Judge追加 | 常時+複数call | Cap超過確実(self-consistency常時実行はunit cost×複数倍) | ユーザー指示「コストを無視した対策は禁止」に直接抵触するため**不採用**。Stage 1 recall非決定性(§10リスク6)への対処は必要なら別トラックで、BLOCKING確定後のみの限定適用に留める設計が要る(Opus論点4、§11) |

### 13-9. 第一候補(委任_03でStage1をV4Aへ更新)

**案γ'**(Stage 1=V4A[固定追加費+¥0.294/記事、§14でSafety改善のため
採用]+BLOCK時のみStage 2+必要時のみ局所EN/JA全文Rewrite、cycle上限2)
を第一候補とする。理由: (1)優先順位①〜④のうち③まで(局所Rewrite
優先)で期待値ベースは依然Cap内(楽観・中央は節約、悲観は+¥0.84)、
(2)常時2重Checker・self-consistency常時実行(案δ)という「コストを
無視した対策」を回避できる、(3)Fableが委任文§2で既に示した第一候補
(β/γ路線)と整合する、(4)Stage 1=V4Aへの変更は「Stage 1が検出しなけ
れば下流が発火しない」という構造的制約(§14)への対応であり、Cost
Capより**Safety(重大Fact見逃し0件)を優先した結果の追加固定費**である
(委任文の優先順位「Safety最優先、その次にコスト最小化」と整合)。
worst case(tail)のCap超過(§13-7)は残存リスクとしてPhase 1実測で
検証する。

### 13-10. Cap内で困難な要素(委任_03で更新、中間報告)

+¥3 Capは、**期待値ベース(楽観・中央・悲観いずれも)では達成可能**と
判断するが、以下3点はPhase 1実測前の**未確定要素**として明記する
(勝手に膨らませず先に報告):

1. **Stage 2の真の単価が最大の不確実性要因**(§13-3)。段落±1縮小
   (§4-4)で入力トークンは記事全文渡しより減る見込みだが、削減効果の
   実測が無いため保守的見積り(¥0.30〜0.40/call)を維持している。実際に
   これより高くなる可能性がある(§13-1の実測が示すとおり、BLOCKING
   関連の判定callはharness平均より¥1超になることがある)。Stage 2単価
   が¥0.6/call超になった場合、§13-7の中央シナリオでも節約効果が消え、
   悲観シナリオ・worst case双方でCap超過の可能性がさらに高まる。
   **Phase 1の最優先実測項目**とする。
2. **worst case(§13-6、V4A反映後¥3.96/記事)はCap(+¥3)を約32%
   超過する**(V4A採用前は¥2.88[Cap内、余裕¥0.12]だった)。§5-3の
   「同一記事でJA全文Rewriteを2回使わない」制約を実装で確実に守ることが
   Cap遵守の前提条件である点は変わらないが、**V4A採用によりworst
   caseの絶対値自体がCapを超えるようになった**。§13-6の概算では発生
   確率が低い(記事あたり約1%程度)ためUSER_DECISION_REQUIRED条件3
   (恒常的な超過)には現時点で該当しないと判断するが、Phase 1実測で
   この発生率・実額を検証する必要がある(**新規、委任_03で判明**)。
3. **Stage 1のV4A化自体が固定費を+¥0.294/記事押し上げる**
   (§13-4-補)。これはSafety改善(changed_actor検出率50%→100%)の
   対価として意図的に許容した増分だが、期待値ベースの節約margin
   (特に中央シナリオ−¥0.06/記事)をほぼ消し去るほど大きい。中央
   シナリオの節約効果が「ほぼゼロ」まで縮小した点は、Checkpoint Aで
   明示的に報告する。

Cap超過が実測で確認された場合、想定される代替案(参考、実装せず):
Stage 2の入力をLedger全文ではなく該当fact_id周辺のみへさらに縮小する
(§4-4の設計判断を再検討)、cycle上限を1へ縮小する(自動完結率は
低下)、JA全文Rewriteの発火条件をさらに狭める、worst case tail
(両段階同時BLOCK+JA-origin+cycle2必要)専用の追加guard(例:
cycle1でJA全文Rewriteを使った場合はcycle2を発動せず直接Stage 4へ
[自動完結率は下がるがworst case費用を抑制できる])。いずれもSafety/
自動完結率とのトレードオフを伴うため、Phase 1実測後にユーザー判断を
仰ぐ。

### 13-11. Phase 1⑤実測反映(委任_08、Stage3実単価確定)

**実測値(§5-4-補2)**: `c_en_local`(EN局所Rewrite、replace型)は
E-1/E-2とも1 attempt解決時¥0.09〜0.18/claim(rewrite1call+recheck
1call)であり、§13-4の見積り¥0.15〜0.35/callの下限〜やや下回る水準
(escalation不要のため見積りより安価)。JA側narrow_scope型の採用案
J-1の実測costは**¥0.4569/cycle(3call: paired rewrite1+JA check1+
EN recheck1)**であり、§13-9設計時の想定(paired local rewrite
¥1.0〜1.5/cycle、旧案Bの1/3以下)をさらに下回った(実測は想定の
約半分弱)。J-2(不採用)は¥0.9598/cycleでJ-1の約2.1倍、かつ
未解決だったため採用しない。

**Cap判定への示唆**: §13-6のworst case式`c_en_local`
(¥0.15〜0.35/call)は実測¥0.09〜0.18/claimに、JA側paired local
rewriteの実測¥0.4569は既存の想定¥1.0〜1.5/cycleより有利な側に
置換できる見込みが得られた。ただし本実測はn=1〜2の小標本(claim単位
escalation未発火のケースのみ)であり、§13-6のworst case式全体の
再計算(cycle 2発火・escalation発火ケースを含む)は次回⑥(統合
dry-run)実測後に確定する(本委任では実単価の部分置換候補の報告に
留める)。

**[委任_09実測]** ⑥統合dry-run(29 instance)実測worst case=
¥2.2721(safety_A4)。**+¥3/記事Cap未超過**(§13-6のtail懸念[¥3.96]
より実測は良好)。**[委任_10実測]** rewrite_hint追加+S1-U variant込み
のiteration2再実行(29 instance)実測worst case=¥2.4664(同じく
safety_A4、+¥0.1943)。rewrite_hint分のprompt/output token増加・
S1-U追加callを織り込んでも**Cap未超過を維持**(§9-1⑦)。S1-Uの追加
固定費(¥3.1589/7 instance、平均¥0.4513/instance)は上記worst case
instanceには含まれない(safety_A4はs1u_eligible対象外のため)。

**[委任_12実測]** iteration4(§9-1⑨)実測worst case(instance単位)=
¥4.2956(`safety_A4`、`STAGE4_ESCALATION`)。iter3の同一instance
(¥6.2445)から改善。記事単位(`ARTICLE_GROUPS`、Standard+Advanced
合算)のworst caseは¥2.924(`meta_run03`、iter3の¥3.0853から改善)、
**+¥3/記事Cap未超過を維持**。`safety_A4`はSafety検証用の合成fixture
であり`ARTICLE_GROUPS`(実記事Standard+Advanced対)には含まれない
ため、Cap判定の分母は記事単位集計(¥2.924)を主指標とする。

## 14. Stage 1設計判断(委任_03新設、Fable/Claude側で結論確定)

**位置づけ**: 委任文により「Stage 1の実装方法をユーザーに逐一確認
しない。KPI達成優先」と明示指定されたため、本節はユーザー確認を
待たずFable/Claude側で結論を確定する(USER_DECISION_REQUIRED非該当、
§12条件2[Safety緩和]には該当しない=改善であるため)。

### 14-1. 構造的前提(全選択肢に共通)

**Stage 1が検出しなければStage 2/3/4は一切発火しない**(委任文明記の
構造的事実)。Self-Recovery Flow全体のSafety(重大Fact見逃し0件)は、
Stage 1の検出(recall)が土台であり、Stage 2以降(materiality判定・
Rewrite・Escalation)はStage 1がBLOCKING-candidateとして拾った場合に
限り機能する。したがって「Stage 1をどう構成するか」は、Self-Recovery
Flow全体のSafety上限を決める最重要変数である。

### 14-2. 選択肢比較(S1-A/B/C/D)

| 選択肢 | 内容 | (1)重大Fact見逃し | (2)Initial BLOCK率→発動率→条件付きコスト | (3)非決定性耐性 | (4)Production採用時の変更範囲 |
|---|---|---|---|---|---|
| **S1-A** | 真のProduction Checker(V0、Prompt/schema無変更)、Trial実行時はgpt-6-luna | **changed_actor 3/6見逃し(50%)**(fixture単位gold表実測、baseline)。他カテゴリ[changed_number/scope/causality/certainty/negation/comparison/time/unsupported_new_claim]は合成fixtureで100%検出済みだが実データrecallは§10リスク6のとおり未保証 | BLOCK率は前Phase実測(B群不要BLOCK率75%)が示すとおり中程度〜高いが、changed_actorのような重大カテゴリを**そもそも拾わない**ため、Stage2/3が発動する前提のBLOCK-candidate自体が生成されない場合がある(見逃しは「発動しない」形で現れる、コストには表れないがSafety事故として現れる) | 未測定(V0のn=20 stability実測は本委任時点でhormuz_run03_standard 100%[20/20]・Meta_run03_standard 90%[18/20]、changed_actorカテゴリのn=20実測は無い) | 変更なし(Production Prompt自体が既にS1-A) |
| **S1-B(採用)** | Trial variant V4A(カテゴリ境界明確化のみ、schema/severity算出ロジック不変) | **changed_actor 5/5(100%)**、Safety群12/12(100%)維持。**残存リスク**: hormuz_run03_standard(changed_scope)がn=20でV0比悪化方向(100%→85%、Fisher p=0.23で統計的有意差なし) | call単価+30%・latency+60%(前Phase実測)。BLOCK率自体は不要BLOCK率2/4[n=1、非決定性と未分離]で、V0比横ばい〜やや改善の可能性 | V0比で明確な改善・悪化のいずれも統計的有意差なし(n=20、hormuz p=0.23、Meta p=0.49、併合p=1.0)。「測定不足」から「実測はしたが方向性が定まらない」段階 | Family X限定Trial variantとして即座にTrial利用可能。Production採用には別途Prompt変更承認が必要(§3-1明記) |
| S1-C(不採用) | V4A+一般常識許容規定の具体化(C2、前Phase「V5-A」相当) | 未実測。理論値のみ(不要BLOCK率1/4=25%へ改善する机上試算、前Phase D-補) | 理論上BLOCK率をさらに下げ、Stage2呼び出し回数を削減できる可能性 | 未実測 | Family X限定Trial variant止まりだが、Prompt変更が二重(V4A+C2)になり、Safety regressionの検証範囲が広がる |
| S1-D(不採用) | Stage1に直接materialityを出させる一体型(Stage1+Stage2統合) | 検出とmateriality判定を同一callに委ねるため、検出漏れとmateriality誤判定が独立に検証できなくなる(Opus L2レビュー#1推奨の「detect/materiality分離」に反する) | 呼び出し回数削減(理論上安い)だが未実測 | 未実測、かつ既存Trial 1/2/n=20資産(Stage1 deviation出力)がそのまま使えなくなる(再測定コストが発生) | Production Prompt全体の再設計に相当し、影響範囲が最大 |

### 14-3. 結論: S1-Bを暫定採用する(**[委任_04改訂/A14]** Phase 1実測
[§9-1③]後に最終確定)

**[委任_04改訂/A14]** Opus所見(論点2(A))により、S1-B採用根拠は
「合成fixture 1種・n=5」(Fisher両側p≈0.18)のみであり、§14-3が退けた
hormuz悪化(p=0.23)と同水準の非有意性であることが判明した。したがって
本節の結論は**Phase 1実測前の暫定採用**とし、§9-1③(negative候補7記事
のV4-A再実行+`er009_changed_actor` V0/V4-A各n=15追加実測)の結果を
もって最終確定する。実測前にV0へ戻す判断はしない(V0+pre-checkを
比較対照としてPhase 1に含めるのみ)。以下14-3の理由付けは暫定採用の
根拠として維持する。

**理由**:
1. **S1-Aは重大Fact見逃し0件というPrimary Safety KPIを構造的に満たせ
   ない**。changed_actor(actor取り違え、委任文§1で「確実に止める」と
   明記された絶対条件の1つ)を50%見逃す実測がある以上、S1-Aのまま
   Self-Recovery Flowを構築しても、Stage 2/3/4がいかに優れていても
   その50%はStage 1の時点でACCEPTABLEとして通過してしまう(§14-1の
   構造的事実)。
2. **S1-Bはこの見逃しを実測で解消する**(5/5=100%)唯一の検証済み
   選択肢であり、negative controlも劣化させない(Meta_run03_standard
   n=20でV0比改善)。
3. **S1-Cは未実測かつ二重のPrompt変更**であり、Stage 2がすでに
   False・borderline群(B1-a/b、B4-b/c)の吸収を担う設計(§7-2/7-3)に
   なっている以上、C2が狙う「不要BLOCK率削減」効果はStage 2で代替
   可能。S1-Cを追加することの限界便益(Stage2呼び出し削減によるコスト
   減)は、未検証のSafety regressionリスクに見合わないと判断し、
   **Phase 1では採用しない**(将来Phase 2以降の検討候補として保留)。
4. **S1-Dは既存Trial 1/2/n=20資産(Stage1 deviation出力、Phase 1計画
   §9-1が前提とする再利用元)を無効化し**、detect/materiality分離
   というOpus L2レビュー#1論点1の中核的推奨(Safety資産保存)に反する
   ため不採用。
5. 残存リスク(hormuz_run03_standardのn=20 V4A実測悪化方向、非有意)は
   14-4のdeterministic pre-checkで部分的に補完する。

**コストへの反映**: V4A採用により固定費が+¥0.294/記事増加する
(§13-4-補)。これはSafety改善の対価として許容する(§13-9)。

### 14-4. 検出漏れ型Safety対策(Cap内で可能な選択肢の検討)

Stage 1(V4A)は依然85〜100%のrecallに留まり(実データfixture、n=20)、
100%ではない。Stage 1が検出しなければ下流は発火しないため、検出漏れ
自体への対策を検討する。

| 選択肢 | 内容 | 費用 | 採否 |
|---|---|---|---|
| **deterministic pre-check(採用)** | Ledgerの構造化フィールド(`numeric_value`/`date_or_period`/主体名等)と記事本文を機械照合(regex/文字列一致)し、Ledgerと矛盾する数値・日付・固有名詞(actor名の置き換え等、機械照合可能な範囲に限定)を検出したら、Stage 1 LLMの判定結果に関わらず強制的にBLOCKING-candidateとしてStage 2へ送る(Stage1 LLMがACCEPTABLEと判定していても上書きする、fail-closedの追加層) | **¥0**(LLM呼び出し無し、Trial実装コストのみ) | **採用**。Opus L2レビュー#1論点4推奨5「機械的に照合可能な項目に限定すれば有効」と整合。汎用の解にはならない(scope一般化のような意味的逸脱は機械照合できない)ことを明記した上で、無料かつfail-closed方向にのみ作用する(誤って安全性を下げることがない)ため、Phase 1で実装対象に加える。実装詳細(対象フィールド・照合方式)はPhase 1委任で確定する |
| BLOCK時ではなくPASS時の限定2nd run | Stage 1がACCEPTABLEを返した場合にのみ、限定的に2回目のCheckerを実行する | Stage1 ACCEPTABLE(大多数のケース)に対して**常時発生する固定費**になる(記事の大半でACCEPTABLEが返るため、実質「毎回2重実行」に近い) | **不採用**(委任文原則どおり)。固定費が既存の+¥0.294/記事[§13-4-補]にさらに積み増しになり、Cap margin([中央シナリオ]わずか−¥0.06/記事)を即座に食い潰す |
| self-consistency(BLOCKING確定claimに限定したunion) | Opus L2レビュー#1論点4推奨2。BLOCKING相当のclaimのみ複数run union | BLOCK時のみの条件付き費用だが、**BLOCKになったclaimの安定性**を高める効果であり、**そもそもACCEPTABLE誤判定[検出漏れ]には無効**(Stage1が見逃した場合はunion対象にすら入らない) | 検出漏れ対策としては**不採用**(目的が異なる)。既存の§11-3/§11-8で「Stage1 recallの根本改善は別トラック」として保留済みの論点と整合、変更なし |

**結論**: deterministic pre-check(¥0、machine照合可能な項目限定)を
Phase 1実装対象として採用する。これによりchanged_number/changed_time/
一部のchanged_actor(固有名詞の機械的不一致)の検出漏れを追加で補完
できる可能性があるが、hormuz_run03_standardのようなscope一般化型の
検出漏れ(意味的判断が必要)は機械照合の対象外のままであり、**完全な
解決策ではない**ことを明記する。この残存リスクはPhase 1実測後も
継続的にリスク登録簿(§10)へ残す。

### 14-5. Stage 1最終確定(委任_07、Phase 1③実測結果に基づく確定)

**結論**: **Stage 1はV4-Aを最終確定とする**(S1-B、§14-3の暫定採用を
確定へ格上げ)。S1-D(一体型、§14-2で理論上は不採用としていたが、
ユーザー方針「既存方式に縛られない、QCDで最良の方法をTrialする」に
従い委任_07で実際にTrial実装・実測した)は、以下の実測結果に基づき
**Stage 1としては不採用**と確定する(Opus L2レビュー#1論点1の
「detect/materiality分離によるSafety資産保存」という推奨が、理論では
なく実測で裏付けられた)。

**(a) Safety群12 fixture(er009 9種+A2A3/A4/A5)**: S1-D 12/12
(100%)がBLOCKING確定。V0/V4Aと同水準([既存実測]V4A 12/12)。
費用¥3.0542(12 call、gpt-6-luna)。

**(b) er009_changed_actor n=15追加実測(既存n=5+新規n=10)**:
V0=7/15(46.7%、既存3/5+新規4/10)、V4A=15/15(100%、既存5/5+新規
10/10)、S1-D=15/15(100%、新規15/15)。Fisher両側検定: V0 vs V4A
p=0.00220、V0 vs S1-D p=0.00220(いずれもn=5時点のp=0.18から統計的
有意水準まで低下、A14が要求した実測完了)。**V4A・S1-Dともに
changed_actor検出でV0を統計的有意に上回ることを確認**。費用: 追加
V0 10call+V4A 10call+S1-D 15call=35call、¥4.0283(既存n=5分は
再利用、0 call)。

**(c) negative候補7記事のBLOCK率増分(V0は既存記録0 call、V4A/S1-D
新規実行)**: V0(既存)=0/7(0%)。V4A=4/7(57.1%、neg1/2/3/5がBLOCKING
確定、neg4/6/7はLEDGER_COMPLIANT)。**S1-D=6/7(85.7%、neg5のみ
QUALITY止まりでBLOCKING無し、他6件はBLOCKING確定)**。Fisher両側検定:
V0 vs V4A p=0.0699(有意水準未満だが増加傾向)、V0 vs S1-D p=0.00466
(有意)、**V4A vs S1-D p=0.559(有意差なしだがS1-Dが数値上より高い
over-block率)**。**S1-DはV4Aより不要BLOCK率が高い方向にある**
(86%>57%、既に本来ACCEPTABLEなfalse control記事に対しても、V4Aより
多くのclaimをBLOCKINGへ倒す)。費用: V4A 7call+S1-D 7call=14call、
¥3.3103(gpt-6-luna、記事によりLedger規模差で単価幅¥0.15〜0.6超)。

**(d) B群5 fixture(B1/B2_hormuz/B3/B4/Meta_run03_standard)claim単位
正解ラベル一致率(S1-D、新規5 call)**: **B3=BLOCKING(1/1一致、確定
ラベルどおり)**。**Meta_run03_standard=全4claim BLOCKING(確定ラベル
BLOCKINGと一致、ただしV4A gold[MAJORx1]よりclaim分割が細かい)**。
**B1=1 BLOCKING+2 QUALITY(V4Aが検出した2claimのうち1件[HF-009市場
動機claim、確定ラベルB1-c=BLOCKING]をQUALITYへ降格。もう1件は新規
BLOCKING[湾岸諸国貿易投資claim、V4A非検出]を独自検出)**。**B2_hormuz
=2 BLOCKING+2 QUALITY(確定ラベルはQUALITYのみだが、S1-Dは2claimを
BLOCKINGへ判定、過剰BLOCK方向)**。**B4=2 BLOCKING+3 QUALITY(V4Aが
BLOCKING確定した4claimのうち、確定ラベルB4-a[AIフォールバック機構の
新規主張、Real-but-fixable群]に対応する2claim["Meta had run a
test..."/"A person can take over..."]をいずれもQUALITYへ降格。
B4-b/c相当[human心理一般論]はQUALITY[確定ラベルどおり一致]。新規に
別claim[contract worker情報共有]をBLOCKINGへ判定)**。**正解ラベル
一致率(claim単位、目視対応付け)= 3/5 fixture(B3・Meta完全一致相当、
B1/B2/B4は部分不一致)**。費用¥1.2379(5 call)。

**(e) hormuz_run03_standard/Meta_run03_standard n=5(S1-Dのみ新規、
既存V0/V4A n=20は流用)**: hormuz_run03_standard=5/5(100%)BLOCKING
確定(V0実測85%[n=20]・V4A実測85%[n=20]と比べ、n=5では非検出0件)。
Meta_run03_standard=5/5(100%)BLOCKING確定(V0/V4A実測90%[n=20]と
比べ、n=5では非検出0件)。費用¥1.8927(10 call)。

**Stage 1最終判定の根拠**: (a)(b)(e)ではS1-DはV4Aと同水準(100%)の
recallを示すが、(c)ではS1-DがV4Aより高い不要BLOCK率(86%>57%)を示し、
(d)ではS1-Dが**Real-but-fixable群の確定BLOCKINGラベル(B1-c/B4-a)を
QUALITYへ誤って降格**させる実例が2件観測された(V4A→Stage2の2段構成
では、Stage2 rubric基準1[Ledgerが別原因・別主体を明記]がこれらを
BLOCKING確定させることを期待していたが、後述§4追記のとおり実際の
per-claim Stage2でも同様の降格が観測されており、これはS1-D固有の
欠陥ではなくStage2 rubric自体の較正課題である可能性が高い。ただし
S1-Dは「検出とmateriality判定を同一callで行う一体型」であるため、
この種の誤判定を第二の独立callで訂正する機会が構造的に存在しない
[Stage2を経由しないため]。V4A→Stage2の2段構成なら、Stage2の判定が
誤っていても「Stage2を改善する」余地が残るが、S1-Dは1callで確定して
しまうため、Opus L2レビュー#1が指摘した「detect/materiality分離に
よるSafety資産保存」の実利が実測で裏付けられた)。

**結論**: Stage 1=V4A(確定、変更なし)。S1-Dは検討対象として実測した
上で不採用(§14-2の理論的判断が実測で補強された)。S1-D関連の実装
(`er052_open233_self_recovery_s1d_trial_01.py`)はTrial記録として
保持するが、Self-Recovery Flowの構成(§3-0)には組み込まない。

## 15. Opus L2レビュー#1(委任_04)への対応(採否・反映節、[委任_04新設])

**位置づけ**: `docs/pm/opus_l2_review_open233_self_recovery_01.md`
(Opus L2批判的レビュー#1、read-only、runtime evidence: 実行モデル
`claude-opus-5[1m]`)の指摘への、Fable判定(採用/不採用/ユーザー判断
送り)と反映節の対応表。API呼び出しなし・¥0・Production非接続・
実装なし(本節は設計書改訂のみ)。

### 15-1. 採用(Phase 1前に設計へ反映済み)

| # | Opus所見(論点) | Fable判定 | 反映節 |
|---|---|---|---|
| A1 | 論点5(A)(B): Recheckで`prior_issues`未使用、既存fail-closed gateが無言で外れている | 採用。継続条件=`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved==True` | §3-0/§6-1 |
| A2 | 論点2(C): precheck由来検出がfloor空振りしStage2で降格され得る | 採用。`detected_by`フィールド追加、precheck由来はfloor扱い(FP率次第で弱め分岐を併記) | §3-1/§4-3 |
| A3 | 論点2推奨1/論点8推奨1: precheck FP率が未測定のままPhase1へ入る | 採用。§9-1①(¥0、最優先)に配置 | §9-1 |
| A4 | 論点1(A)(D)/論点4推奨2: EN局所RewriteがJA/EN乖離を生む、cycle indexでmechanism選択が支配的ケースと噛み合わない | 採用。origin別選択+paired local rewriteをPhase1第一級項目へ | §5-1/§5-2/§5-3/§5-4 |
| A5 | 論点7推奨1: 同一claim再発でもcycle2を無条件発火 | 採用。同一claim/fact_id再BLOCKINGは即Stage4 | §3-3/§5-3/§6-1 |
| A6 | 論点6(B): §13-6が§3-5と不整合・二重計上疑い、JA-origin比率根拠薄弱 | 採用。式化、JA-origin実測80%(n=5)へ改訂、BLOCK率はV4A実測後に置換 | §13-6 |
| A7 | 論点1(D): Stage4条件表にsymbol gate/`all_prior_issues_resolved`/予算abort等の欠落 | 採用。コード上の例外型と1対1対応表を新設 | §6-1 |
| A8 | 論点3(A): Stage2入力にexplanation/severity/10 flagsを渡しanchoringを生む | 採用。除外し、floor判定のみ外側で使用。ヘッジ語regexで段落範囲拡張 | §4-4 |
| A9 | 論点1(C)/論点3推奨2: Stage2 call数=claim数がコスト膨張要因 | 採用(比較実施)。batch化を主案、per-claimを比較対照 | §3-5/§4-1/§9-1④ |
| A10 | 論点3(C)(E): ACCEPTABLE定義の新規性基準が曖昧、changed_certainty不整合 | 採用。「Ledgerに無い新規の」と明文化、changed_certaintyをfloorへ追加 | §4-2/§4-3 |
| A11 | 論点4(A)(D)/論点5推奨3: Rewrite型分類が無く、guard抵触時の扱いが過剰に厳しい | 採用。`rewrite_kind`追加、機械検証追加、段階的フォールバック | §4-5/§5-2 |
| A12 | 論点6推奨1: prompt cachingが未検討 | 採用(実測項目化)。Phase1④で受理可否・削減率を実測 | §9-1④/§13 |
| A13 | 論点5【Safetyリスク】/論点8推奨3: Escalation0件の内訳が区別できない | 採用。内訳測定項目を必須化 | §8-1 |
| A14 | 論点2推奨1/論点8(C): V4A採用根拠が単一fixture・n=5で弱い、BLOCK率実測が計画に無い | 採用。§9-1③へ実測を追加し、Stage1 variant最終確定を実測後に延期 | §9-1③/§14-3 |
| A15 | 論点8(C): モデル依存/非依存の結論の優先順位が未整理 | 採用。モデル非依存の結論(prior_issues/precheck FP/JA-EN乖離/call数)を優先確定する方針を明記 | §9-1 |
| A16 | 論点8(D): Production化後の継続監視策が未定義 | 採用(Phase2設計項目として記録、採否はユーザー) | §11-8 |

### 15-2. 不採用(理由付き)

| Opus所見(論点) | 内容 | 不採用理由 |
|---|---|---|
| 論点6推奨6/論点1(A)関連 | cycle上限を1へ下げる | 実観測パターン(Hormuz run_03型: Advanced解消→Standardで新claim)にcycle2が必要であり、上限1はKPI(Escalationゼロ)を確定的に落とす |
| 論点3推奨1関連の代替案(§13-10代替案1) | Stage2入力のLedgerを部分化(該当fact_id周辺のみ) | B3型(HF-007のように別条件が離れた箇所にある場合)を見逃すリスクがあり、fail-closedの原則に反する |
| 論点1推奨4/論点1(C) | Stage2/Stage3の統合(3段階化、materiality判定+rewrite_hint生成を1 callへ) | 検証可能性の観点で分離を維持(Opus自身も同結論)。統合すると降格判定callが常にrewrite出力トークンを払うため期待コストも悪化する可能性が高い |

### 15-3. ユーザー判断事項として提示(Fableが決めない、Checkpoint Aで提示)

| 論点 | 内容 | 該当条件 |
|---|---|---|
| 論点8(A)推奨2 | KPI判定方法の再定義(記事単位0件→事象単位推定によるEscalation率の信頼区間上限) | 条件1(KPI変更) |
| 論点6(D) | Cap定義の解釈(LLMコストのみかTTS等downstream込みか) | 条件1(KPIの解釈) |
| 論点8(B)1 | QUALITY通過(現行STOPしていたB2型を人間を通さず公開すること)がSafety緩和に該当するか | 条件2(Safety緩和)該当可能性 |

**設計書での扱い**: 上記3点は§12(USER_DECISION_REQUIRED条件)へ追記
済み。現行KPI文言はそのまま維持し、事象単位推定・Escalation0件内訳を
追加報告項目として併記する(§12/§12-1/§8-1)。

## 16. Opus L2レビュー#2(委任_11)への対応(採否・反映節、[委任_11新設])

**位置づけ**: `docs/pm/opus_l2_review_open233_self_recovery_02.md`
(Opus L2批判的レビュー#2、read-only、runtime evidence: 実行モデル
`claude-opus-5[1m]`)の指摘への、Fable判定(採用/不採用/ユーザー判断
送り)と反映節の対応表。Fable判定=「Opus総合1〜5をすべて採用。やらない
こと: rubric再精緻化R2''・changed_certainty floor緩和・Stage2省略」
(委任_11委任文§2)。

### 16-1. 採用(iteration 3実装済み)

| # | Opus所見(論点) | Fable判定 | 反映節/実装箇所 |
|---|---|---|---|
| B1 | 論点1推奨1: `j1_pair_not_located`が全文fallbackへ到達せず無編集のまま再検出 | 採用。early returnを廃止し、locate失敗時も必ずJA全文fallbackへ配線 | §5(paired_rewrite)、`er052_open233_self_recovery_flow_runner_01.py::paired_rewrite` |
| B2 | 論点1推奨2/論点4推奨1: JA全文fallback後にEN側が無編集のまま残りJA/EN記事対が乖離 | 採用。EN側も同一rewrite_hintで必ず1 call編集(en_target特定時はE-2局所編集、未特定時はEN全文fallback) | 同上 |
| B3 | 論点1推奨3: 停止判定がfact_id単独一致で、兄弟文カスケード(別文だが同fact_id)を「同一claim再発」と誤判定 | 採用。`find_matching_prior_record`でfact_id+正規化claim本文の近似一致を要求。別claimはblocking件数厳密減少を条件にcycle3を1回だけ許可(上限`HARD_MAX_CYCLES`=3) | §3-3、`claim_identity`/`find_matching_prior_record` |
| B4 | 論点1推奨4: Rewrite対象単位が引用文1文のみでタイトル/hook文の兄弟文カスケードに未到達 | 採用。`locate_paragraph_block`で段落ブロック(直前の見出し専用blockを含む)を特定し、E2_PARAGRAPH/J1_PARAGRAPHプロンプトで段落単位Rewriteへ拡張 | §5、`locate_paragraph_block`/`E2_PARAGRAPH_PROMPT_TEMPLATE`/`J1_PARAGRAPH_PROMPT_TEMPLATE` |
| B5 | 論点7推奨1/2/4: `escalation_zero_breakdown`が`RESOLVED_REWRITE`限定でiter2の5 instance(`RESOLVED_REWRITE_THEN_DOWNGRADE`)が未検査のまま「誤PASS候補0」と報告 | 採用。分母を`RESOLVED_*`全体へ拡張。`s1u_caught_recall_miss`を`s1u_additional_block`へ改名し正解ラベル照合の真偽列(`s1u_additional_block_label`)を追加 | §8、`aggregate_measurements` |
| B6 | 論点7推奨2: `LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=False`という自己矛盾応答が次cycleの空deviationsで静かに降格していた(fail-openの継ぎ目) | 採用。追加1 call(`_recheck_confirm`)で再確認し、再確認でも解消未確認ならfail-closedで`STAGE4_ESCALATION`(理由`unconfirmed_after_reverify`)。iteration 3で有効化 | §3-0/§6-1、`run_instance`のen_ambiguous分岐 |
| B7 | 論点5推奨: 群別Escalation率(合成Safety/B群/negativeを実runの分母に混ぜない)が未算出 | 採用。`group_escalation_rates`+`real_run`(実run6 instance限定)を追加 | §8、`aggregate_measurements` |
| B8 | 論点6推奨2/3: 記事単位(Standard+Advanced合算)のコスト・合否・worstが未算出 | 採用。`ARTICLE_GROUPS`+`article_level`(aggregates/worst_cost_jpy)を追加 | §8/§13、`aggregate_measurements` |
| B9 | 論点4推奨1/2/3: Rewrite由来の新規逸脱(narrowingによるactor付け替え等)を検出する層が無い | 採用。(a)決定論precheck再実行(`detect_rewrite_new_precheck_findings`、¥0)、(b)paired rewrite後のJA↔EN等価チェック1 call(既存Production翻訳忠実性QA資産`er003_ja_to_en_translation.py`のPrompt/Schemaをread-only借用、`run_ja_en_equivalence_check`)を追加。verdict記録のみでflow制御には使わない(既存Recheckとの権限重複回避) | §4/§5、`run_instance`のcycle内追加 |
| B10 | 論点1/2/7: iter2の5 instance(`RESOLVED_REWRITE_THEN_DOWNGRADE`で未検査)の遡及監査 | 採用(¥0、既存json読み直しのみ、iter2出力は無変更)。3件(`safety_er009_unsupported_new_claim`/`neg2_meta_refresh_a2`/`neg3_hormuz_prodrunner_b1b`)が`LEDGER_COMPLIANT`+`all_prior_issues_resolved=False`の自己矛盾(=B6是正の対象そのもの)、2件(`hormuz_run01_advanced`/`hormuz_run03_standard`)は`all_prior_issues_resolved=True`が確認できる真の解消だった(監査結果は§9-1⑧に記録) | §9-1⑧ |
| B11 | 論点2推奨1/2: S1-Uの安価代替(2×V4-A union、S1-D effort=medium/low)の実測比較 | 採用(実装・実測、新規`er052_open233_self_recovery_s1u_alt_compare_01.py`)。結果は§9-1⑧参照(受入条件未達のため既存S1-U[effort=high]をiteration 3でも維持) | §9-1⑧ |

### 16-2. 不採用(理由付き、Fable判定「やらないこと」に整合)

| Opus所見(論点) | 内容 | 不採用理由 |
|---|---|---|
| 論点1推奨5(裏返し)/論点3 | Stage2 narrow_scopeをQUALITY扱いにする、または`changed_certainty` floorを緩和する | Opus自身が非推奨と明記(§7-0正解ラベルとの衝突、B4-d保護根拠の希薄化)。委任文で明示的に「やらないこと」指定 |
| 論点3推奨2(rubric手順精緻化) | ACCEPTABLE節の対象範囲を1文追加するrubric再較正(R2'') | 委任文で明示的に「やらないこと」指定(R2'既に不採用実績があり、投資対効果が低いというOpus自身の分析[論点3]とも整合) |
| 論点1推奨6(全文must-fix retry 1回許可) | cycle2で同一claim再BLOCK時に全文must-fixを許可 | Opus自身が「次善」止まりで、Advanced/Standard再生成(§13-6)を伴いCap割れの懸念を指摘。B3(段落単位Rewrite)を先に試す方針を優先 |

### 16-3. ユーザー判断事項として提示(Fableが決めない)

| 論点 | 内容 | 該当条件 |
|---|---|---|
| 論点5 | KPI判定方法の再定義(「記事単位0件」→「(a)重大Fact見逃し0件維持、(b)core-framing型[B1型]Escalationのみ許容し件数・理由コード報告、(c)それ以外の機構起因Escalationを0件」への変更提案) | 条件1(KPI変更) |
| 論点2 | S1-U(または安価代替)のPhase 2デフォルト採用・Production配線可否 | 条件4(Production採用・配線) |
| 論点6 | 新規テーマでPhase 2記事を作る場合のテーマ選定(既存run再利用を第一候補とする提案だが、新規が必要な場合はユーザー選定) | CLAUDE.md新規記事テーマ選定ルール |
| 論点1推奨6 | 全文must-fix retry 1回許可案(Cap超過の可能性) | 条件3(Cap超過の可能性) |

**設計書での扱い**: 上記4点は§12(USER_DECISION_REQUIRED条件)への
追記対象として記録し、RESULT_PACKET/REPORTへ引き継ぐ(現行KPI文言は
維持、iteration 3実測結果[§9-1⑧]を添えてユーザーへ提示する)。
