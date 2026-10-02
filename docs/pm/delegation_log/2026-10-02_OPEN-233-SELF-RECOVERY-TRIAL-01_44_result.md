<!-- 抽出元transcript: agent-a04340bc6b32522cb.jsonl(subagents配下。指定の.outputは0バイトで抽出不能だったため同内容のsubagent transcriptを使用)。抽出日時: 2026-10-02T21:37:24。本文(最後のassistantメッセージ)は改変していない。 -->

# 委任_44 報告: 2周目以降の新規指摘の原因切り分け+対策設計案(read-only、¥0、実装・git操作なし)

## 1. 結論(10行以内)
対象は、2周以上実行されたrun 69件(全277ファイル中)の「cycle 2以降の最終BLOCKING指摘」85行(K1=58、K2=27)。
- 1位は「元記事に最初から存在したのに前の周回で指摘されなかった」型(P2a+P2b)で34行(40%)。Checkerが1回で全件を出さない、または周回ごとに出たり出なかったりするためで、P2の分類は決定論的、理由は推定。
- 2位は「元記事にあり、前の周回では低い重大度だったものが後でBLOCKINGになった」型(P1)の15行(18%)。Checker自身のseverityは85行すべてMAJORで揺れていない。揺れたのはStage 2の最終判定で、その原因はChecker出力のboolean flag(特にchanged_scope)の出入りと、それに連動する決定論ルール(disclosure_gapの降格、floorの引き上げ)だった。
- 3位は「Rewriteが直した範囲、またはその付近が再度逸脱とされた」型(R、R1=19行+R_older=1行=20行、24%)。ただし20行中13行は、Stage 2が非BLOCKINGと判定した文をfloorがBLOCKINGへ引き上げた行(floor引き上げ)で、委任_35で廃止済みの「floorの同一fact_id一括適用」の副作用。修正後のrep20・rep21(4 run、該当4行)にはR行が0。
- P3(再発、8行・9%)は受け渡しの取りこぼしで、委任_39〜41の設計(未実装)が対象。新規提案はしない。
- 最大のリスクは見逃しのSafety側。MUSE-HC-010の文は固定Stage 1のどこにも無く、Recheck 8回のうち4回しか指摘されなかった。指摘された4/4回はStage 2が独立にBLOCKINGと判定している。指摘されなかった4回のうち、rep21 s2は残存したままPASS扱いで終わった。ただしHC-010が真にLedger逸脱かは未確認。
- 対策の骨子は、周回を増やさず1周目で網羅する方向(§7)。主案はE1(fact駆動の全件走査をCheckerへ追加、Trial専用)とE2(2サンプルunion)。重大度の揺れは、決定論ルールの緩和になるため、人間判断が要る選択肢(E3)と安全側のログ案(E4)に分けた。

## 2. 対象・分母・除外・判定不能
- 対象は `er052_output/open233_self_recovery_flow_runner_01_{iter5-8,rep7-21}/instances_*/*.json`。19ディレクトリ、277ファイル(委任_41と同一)。
  - `cycles`キーあり277ファイル。そのうち2周以上は69ファイル。Stage 4(STAGE4_ESCALATION)で2周以上のものは28ファイル。
  - 分母は「cycle≥2の最終materiality==BLOCKING」85行。内訳はK1=58、K2=27(同一fact_id列挙で複製された指摘)、K3(precheck)=0。
- 判定不能(U)は8行。理由は全件「説明文混在」(`“…” (in the passage…)`のように引用に説明が付いた形)。単一断片で救済できそうなものは2件(診断のみ。分類は変えていない)。
- 指摘文字列の確定は委任_41と同じ文字照合L0〜L4。記事本文は`en_text_before_rewrite`、なければ前周回の`en_text_after_rewrite`を使う(前周後=当周前の一致は委任_41で33組・不一致0を確認済み)。
- 「元記事」=cycle1の入力記事。

分類定義(スクリプト冒頭コメントに明記):
- P3: 同じ範囲の指摘が前の周回でBLOCKING。
- P1: P3でなく、同じ範囲の指摘が前の周回に非BLOCKINGで存在。
- P2a: 同じ範囲の指摘は前に無いが、同じfact_idの別箇所は前に指摘あり。
- P2b: そのfact_id自体が初出。
- R1/R2: 文字列が元記事に無く、直前周回のRewriteの編集に重なる。対象指摘に重なる編集ならR1、対象外の編集ならR2。
- 委任文のP1/P2aの定義は同一fact_id別範囲の扱いが重複していたため、「P1=同じ範囲」「P2a=同じfact_idの別範囲」と解釈した。

重要な限界:
- Checker自身がMINORとした指摘は、次周回の入力(runnerの`severity=="MAJOR"`フィルタ)から落ちるため記録に残らない。したがってP2は「MAJORとして出なかった」であり、「完全に見逃した」のか「MINORで出ていた」のかは記録から区別できない。
- 記録のseverityは85行すべてMAJOR。ユーザーの言う「Minor/Major」の揺れは、記録上はStage 2の最終判定(BLOCKING vs QUALITY/ACCEPTABLE)の揺れ。
- 各runは設定・コードの版が違う(iter5〜rep21、委任_35の修正前後)。

## 3. A: ケース別の切り分け

### 3-1. 固定Stage 1の中身
fixture: `rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`。deviationsは2件のみ。
- HC-012: 「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」
  - 列挙された他箇所: 「If no one explained this clearly… They could not tell if it was AI or a person.」と、In one lineの「Some calls through Meta’s AI assistant…」。
- HC-011: 「It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.」
  - 列挙された他箇所: 「News reports also cited one employee’s report.」と「However, this is only one report. It would be wrong to say all contract workers did this.」。

**HC-010「Also, some calls needed user information to continue.」は、deviationにも列挙にも無い。**
- 元記事には存在し、cycle1の検査対象本文にも7 run全てで存在した。
- つまり固定Stage 1が見逃していた文で、低い重大度での列挙もされていない。
- 固定Stage 1と判定した条件: iter8 s1/s2とrep19〜21の7 runで、cycle1のK1 claim集合がfixtureと一致。

### 3-2. 固定Stage 1の7 run、周回別表
記号: B=BLOCKING、Q=QUALITY、A=ACCEPTABLE。`llm`はStage 2 LLMの判定、`floor`はその後の決定論ルール(`dg↓`=disclosure_gap降格、`num↑`=changed_numberのfloor引き上げ、`actor↑`=changed_actorのfloor引き上げ)。
- 分類は2周目以降のBLOCKING行のみ。
- K2は「列挙された他箇所の複製」。
- 同じ表を非固定run(iter5・iter6・rep9・rep11等)にも適用した全行は、`cases_detail_01.csv`にある。

**iter8 s1**(STAGE4・same_claim_fact_id_reblocked、3周、委任_35前のコード)
- c1(固定Stage 1の出力):
  - HC-012「enjoyed…」 Q(llm=B、dg↓)
  - HC-011「It said human staff… These calls…」 B(num)
  - K2: HC-012「If no one explained…」 Q、HC-012「Some calls through Meta’s…」 A
  - K2: HC-011「News reports also cited one employee’s report.」 B(llm=A、num↑)
  - K2: HC-011「However, this is only one report. It would be wrong…」 B(llm=A、num↑)
- c2のBLOCKING:
  - HC-010「Some calls needed user information to continue.」: **P2b**(元記事に存在、c1の本文で未指摘)
  - HC-011「These calls were about trying to lower internet or cable fees.」: **P3**(c1で2文のclaimがBだった。委任_41のrelationは「現行⊂新、一部の文のみ対象」)
  - HC-012「Some calls through Meta’s AI assistant…」: **P1**(c1でA→Bに。llm A→B)
  - HC-011「News reports also cited one employee’s report of an inappropriate remark during a call.」: **R1**。c1のRewriteが「report.」→「report of an inappropriate remark during a call.」「calls.」→「a call.」と変えた編集に重なる。llm=A、floor引き上げ。
  - HC-011「It said human staff made inappropriate comments… during a call.」: **R1**(llm=Q、floor引き上げ)
  - HC-011「However, this is only one report.」: **P3**(c1の2文claimの前半だけ再指摘)
- c3のBLOCKING:
  - HC-012「They enjoyed…They did not realize it.」: **P1**(c1・c2ともQ → c3でB。llm=Bは不変。降格が発火しなかった理由は§5参照)
  - HC-012「They could not tell if it was AI or a person.」: **P1**(Q→B、同じ理由)
  - HC-011の5文: R1が4行+R_older1行。いずれもllm=A/Q、floor引き上げ。

**iter8 s2**(STAGE4・target_not_locatable、2周)
- c2のBLOCKING:
  - HC-011「These calls…」: **P3**
  - 「They enjoyed…」(fact_idはこのrunだけHC-007と付与): **P1**(c1のQ→B。cycle2のChecker出力でchanged_scopeがtrueになったため)
  - 「They could not tell…」: **P1**(llm Q→B)
  - HC-011「…during one call.」「However, this is only one case.」: **R1**×2(llm=A、floor引き上げ)
- HC-010はc1・c2とも指摘なし(c2の本文には存在)。

**rep19 s1**(STAGE4・cycle_limit_exhausted_after_recheck、3周、委任_35前)
- c2のBLOCKING:
  - HC-012「enjoyed…」: **P1**(Q→B、changed_scopeがtrue)
  - HC-010「some calls needed user information to continue.」: **P2b**
  - HC-011「These calls…」: **P3**(llm=Q、num↑)
  - HC-011 K2が3文: **R1**×3(llm=A、num↑)
- c3のBLOCKING(すべてfloorが`changed_actor`を新たに立てて引き上げ):
  - 「If no one explained… They could not tell…」: **P1**
  - 「People asking Muse to call might think AI was calling.」: **P1**
  - 「The problem was telling users who was speaking.」: **P2a**
  - 「But sometimes, a human was speaking instead.」: **P2a**
  - 「Meta said it was a mistake to start the test without clear notice.」: **R1**。c2のRewrite(3_sentence)が「They enjoyed… They did not realize it.」を別文へ置き換えたもの。

**rep20 s1**(RESOLVED_REWRITE_THEN_DOWNGRADE、3周、委任_35後)
- c1: HC-012 Q(dg↓)、HC-011 B、K2はA/Qのまま(floorが波及しない)。
- c2: HC-010「Some calls needed user information to continue.」が **P2b** でB(llm=B、floorなし)。HC-012は引き続きQ。
- c3: HC-012のQのみ → 解消。

**rep20 s2**(STAGE4・ladder_exhausted_without_full_rewrite、2周、委任_35後)
- c2: HC-012「“They could not tell if it was AI or a person” and “They did not realize it.”」が **P1** でB(c1でQ。flagの変化で降格が外れた)。
- HC-010は指摘なし(c2の本文には存在)。

**rep21 s1**(STAGE4・cycle_limit_exhausted、3周、委任_35後)
- c1: HC-012 Q、HC-011 B(llm=Q、num↑)。
- c2: HC-011「These calls…」が **P3** でB。HC-012はQ。
- c3: **HC-010「Some calls needed user information to continue.」が初出(P2b)** でB(llm=B)。HC-012はQ。

**rep21 s2**(RESOLVED_REWRITE_THEN_DOWNGRADE、2周、委任_35後)
- c2: HC-012のQのみ。HC-010は一度も指摘されず、**文は残ったまま解消(PASS系)**。

### 3-3. ユーザーの8項目への答え(固定7 runの共通と各runの差)
| 項目 | 答え |
|---|---|
| 1周目で何を検出したか | 固定Stage 1の6〜2件(HC-012とHC-011とそのK2)。HC-010は無し。 |
| 2周目 | iter8 s1・rep19 s1・rep20 s1がHC-010を初出(P2b)。HC-011の2文claimの後半が再出(P3)。HC-012の既出文が重大度を上げて再出(P1)。 |
| 3周目 | iter8 s1はHC-012のP1、HC-011のRewrite起因(R)。rep19 s1はHC-012の別文(P1・P2a)とR。rep21 s1はHC-010を初出(P2b)。 |
| Minor/Major | Checker severityは全てMAJOR。揺れたのはStage 2の最終判定(QUALITY↔BLOCKING)。 |
| 元記事に最初からあった問題か | HC-010、HC-011「These calls…」、HC-012の各文は全て元記事に存在(P)。 |
| Rewrite起因か | HC-011の「…of an inappropriate remark during a call」系(iter8 s1・rep19 s1)と、rep19 c3の「Meta said it was a mistake…」はRewrite起因(R1)。いずれも委任_35前のコード。 |
| Minor→Majorへ変化したか | HC-012の「enjoyed…」「They could not tell…」(Q→B、P1)と、「Some calls through Meta’s AI…」(A→B、P1)。 |
| 1周目で完全に見逃したMajorか | HC-010(P2b、固定Stage 1に無く、文は1周目から存在していた)。 |

run間で揺れた点:
- HC-010の指摘は、文が残っていてRecheckで検査された8回のうち4回(iter8 s1 c2、rep19 c2、rep20 s1 c2、rep21 s1 c3)。指摘なしは4回(iter8 s2 c2、rep20 s2 c2、rep21 s1 c2、rep21 s2 c2)。
- 同じ記事・同じ固定入力でも、rep21 s1はc3で初出し、rep20 s1はc2、rep21 s2は出ない。
- 設計書§6-14〜6-16の言う「Stage 1初回の揺れ」とは別の、Recheckでの検出揺れ。

### 3-4. 既知例の確認
- **HC-010**: 上記のとおり。固定Stage 1の出力(deviationsにもlocationsにも無し)に含まれていない。
  - 直接の根拠: iter8 s1/s2とrep19〜21の7 runのc1は全て「文は本文に存在、指摘なし」。
  - 指摘された4回は全て`llm=BLOCKING`・floorなし。
  - 推定: Checkerが1回の呼び出しで列挙する件数にばらつきがある。
- **HC-012「They enjoyed…They did not realize it.」「They could not tell…」**:
  - 固定7 runのc1は全て、llm=Bだがdisclosure_gap降格で最終Q。
  - 観測: iter8 s1 c3、iter8 s2 c2、rep19 c2でB。rep20 s1 c2〜3、rep21 s1 c2〜3、rep21 s2 c2はQのまま。
  - 判定がBになった回のChecker出力は、`changed_scope=true`(rep19 c3は`changed_actor=true`)が加わっている。
  - 詳細は§5。

### 3-5. 全記事の集計(cycle≥2のBLOCKING 85行)
| 分類 | 延べ行 | ユニーク(instance, claim)63件 |
|---|---|---|
| P1 | 15 | 11 |
| P2a | 18 | 12 |
| P2b | 16 | 11 |
| P3 | 8 | 3 |
| R1 | 19 | 17 |
| R_older | 1 | 1 |
| R2 | 0 | 0 |
| U | 8 | 8 |
- ユニークの内部不一致(同一文字列で分類が割れたもの)は5件。
- K1のみ(58行): P1=11、P2a=14、P2b=12、P3=7、R1=6、U=8。
- 記事別の延べ内訳:
  - meta_run03_standard(34行): P1=9、P2a=3、P2b=9、P3=7、R1=12、R_older=1
  - hormuz_run03_standard(11行): P2a=4、P3=1、R1=3、U=3
  - safety_A4(10行): P1=2、P2a=7、U=1
  - bgroup_B4(6行): P1=3、P2a=1、U=2
  - neg1_meta_b3prod_a2(6行): P2b=3、R1=1、U=2
  - neg3_hormuz_prodrunner_b1b(4行): P2a=1、P2b=3
  - safety_A2A3(4行): P1=1、P2a=2、P2b=1
  - safety_er009_changed_scope(2行): R1=2
  - safety_er009_changed_time(1行): R1=1

代表例(分類ごと、元の文字列を逐語):
- **P1**:
  - iter8 s1 c3: 「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」(c1・c2のQ → c3のB)
  - iter6 s1 bgroup_B4 c2: 「Names, plans, and private matters are easier to share when you know who is hearing them.」(c1のQ → B、floorで引き上げ)
  - iter6 s2 safety_A2A3 c2: 「with its distant danger reaching gasoline prices and the cost of moving goods through crude oil」(c1のA → B)
- **P2a**:
  - iter5 s1 safety_A4 c2: 「An AI called. That was what people thought as they spoke.」
  - iter6 s1 safety_A4 c2: 「when AI struggled, a person could help」
  - rep19 s1 c3: 「But sometimes, a human was speaking instead.」
- **P2b**:
  - rep21 s1 c3: 「Some calls needed user information to continue.」
  - iter6 s2 meta c2: 「It said human staff made inappropriate comments about race during calls. These calls were…」(このrunのc1はHC-011を未指摘)
  - iter6 s1 safety_A2A3 c2: 「Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level.」
- **P3**:
  - rep21 s1 c2: 「These calls were about trying to lower internet or cable fees.」
  - iter5 s2 hormuz c2: 「Oil prices did not fall across the whole market after the plan was withdrawn.」
  - iter6 s1 c2: 「They did not realize it.」
- **R1**:
  - iter8 s1 c2: 「News reports also cited one employee’s report of an inappropriate remark during a call.」
  - rep19 s1 c3: 「Meta said it was a mistake to start the test without clear notice.」
  - safety_er009_changed_scope c2: 「The taxi study's results have now been directly confirmed in restaurants nationwide…」(c1のRewriteが「restaurant」→「taxi」と編集)
- **U**: 「“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.」など。

## 4. B: 原因ごとの規模(85行、分母は§2)
| 原因 | 行 | 率 | 備考 |
|---|---|---|---|
| P1 重大度の揺れ | 15 | 17.6% | 下に内訳 |
| P2a 同一fact別箇所の取りこぼし | 18 | 21.2% | 「同一fact_idの別箇所の列挙」(`same_fact_id_locations`)に載っていたものは0件。 |
| P2b factが初出の見逃し | 16 | 18.8% | 同上。 |
| P3 書き換えで直らず再指摘 | 8 | 9.4% | 委任_41のrelationが「一部の文のみ対象」=5、「現行が拡大」=1、「同じ」=1、記録なし=1。受け渡しの取りこぼしが主。 |
| R1 | 19 | 22.4% | このうちK2が13行、floor引き上げが12行。 |
| R_older | 1 | 1.2% | 同上。 |
| R2 | 0 | 0% | |
| U | 8 | 9.4% | |

- P1の内訳(15行):
  - floor発火の有無が変わった=8。
  - Stage 2のllmが変わった=7。
  - Checkerのseverityが変わった=0。
  - llmとfloorの組み合わせ:
    - llm=Bでfloor無し=12(多くはdisclosure_gap降格が外れたもの)。
    - llm=Qでfloor引き上げ=3(`changed_actor`が2、`changed_comparison`が1)。
- floorによる引き上げ(llmが非BLOCKINGなのにfinalがBLOCKING): 85行中26行(31%)。
  - changed_number=14、changed_actor=9、changed_comparison=1、changed_time=2。
  - R行20のうち13、P2b 5、P1 3、P2a 3、P3 2。
- 委任_35の修正後(rep20・rep21): 4行のみ(P2b=2、P1=1、P3=1、R=0)。
- Stage 4(STAGE4_ESCALATION)のrun限定: 65行(Stage 4のrun23件)。
  - 全行: P1=11、P2a=13、P2b=10、P3=8、R1=15、R_older=1、U=7。
  - 最終周回の行(36行): P1=8、P2a=6、P2b=4、P3=4、R1=10、R_older=1、U=3。
  - Stage 4の理由別:
    - same_claim_fact_id_reblocked: R1=9、P3=4が目立つ。
    - ja_deviation_unresolved: P2a=5、P2b=3。
    - cycle_limit_exhausted(_after_recheck): P1=5、P2a=5、P2b=3、P3=3、R1=4。
- Stage 4以外(20行): P1=4、P2a=5、P2b=6、R1=4、U=1。
- 固定Stage 1のrunのみ(33行): R1=12、R_older=1、P1=9、P3=5、P2b=4、P2a=2。
- 同一文字列でStage 2の最終判定が変わった種類は、全記録で208種類のうち36種類。
  - QUALITYとBLOCKINGの両方が現れたのは23種類(観測233回)。meta_run03_standardが5種類。
  - この23種類のうち、llm_materiality自体が変わったのが18、llmは一定でfloor/降格が変わったのが5。
  - floorの有無自体が変わった種類は14。

## 5. C: なぜ起きるか

確認済み(コード・記録を直接確認):
1. **Recheckは「前回の指摘が直ったかの確認」ではなく、全文に対する独立のChecker呼び出し。**
   - runner `run_recheck`(e0ae8de0版1495〜1556行)が、Stage 1初回と同じV4A Prompt+全文+`build_prior_issues_instruction`(er003:678〜693)を組み立てる。
   - 次周回の入力は、Recheckが返したMAJORだけから作られる(4620付近)。
   - 同一fact_idの列挙(`SAME_FACT_ID_ENUMERATION_INSTRUCTION`)は委任_35でcycle1限定(既定False)。2-of-2確認は`run_recheck_confirm`で、「COMPLIANTだが解消未確認」の矛盾時に限って追加1回。新規指摘の検出をn=2にする仕組みは無い。
   - 結論: Recheckは1サンプルの単発判定。弱いのは「全文走査」ではなく「単発の非決定性」。
2. **Checker Promptに、件数上限・優先順位・「主要な逸脱のみ」という記述は無い。**
   - er003:502〜601と、er051のV4A差分ブロック。
   - 一方、「全件を網羅せよ」という指示も無い。「該当するdeviationがなければ空配列」とあるのみ。
   - また、同一fact_idの別箇所の列挙は「見つけた逸脱に対して他の箇所を探す」形。見つけられなかった逸脱(HC-010)には働かない。
3. **V4A差分ブロック(er051)が「10種類は排他的でなく、該当するものを全てtrueにせよ」と指示している。**
   - このため、changed_scope・changed_actorなどのboolean flagが回ごとに出たり出なかったりする。
   - これが次の決定論ルールへ直接つながる。
4. **disclosure_gap降格(runner 1950〜2002)が、Q/Bの揺れの直接の原因。**
   - 降格の条件は、floorなし、changed_*(scope含む)が全てfalse、unsupported_new_claimまたはchanged_certaintyがtrue、否定語を含む、新しい数値・固有名詞なし、の全て。
   - Stage 2のllm判定は、HC-012の「enjoyed…」で一貫してBLOCKING。最終がQとBに割れるのは、Checkerがchanged_scopeをtrueにするかどうかで降格が外れるため。
   - 同じ条件(llm=B・否定語・unsupported/certaintyあり)を満たす82回の観測のうち、42回が降格でQUALITY、29回がchanged_scope=trueでBLOCKINGのまま、11回は降格条件の他の要素で外れた(他の要素は不明)。
5. **deterministic floorの引き上げ。**
   - 修正前(rep19まで)は、複製claim(`detected_by_enumeration`)にもfloorが付与されていた。
   - 委任_35(runner `apply_floor`)で複製には付かなくなった。
   - 修正前のR1・K2・floor引き上げ(12行)は、これの副作用。
6. **Stage 2は1claimずつ、claim+前後1段落+Ledgerだけを見る。** Checkerのflagや理由は渡さない。ただし最終判定は、flagに連動するfloor/降格で変わる。
7. **周回の上限**: `MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`(runner 275・279)。追加1周は、BLOCKING数の減少か、同一fact_idの新箇所がある場合に限る。

推定(記録から断定できないもの):
- 「Recheckは前回の指摘に注意が偏り、他を拾いにくい」は未検証(`prior_issues`によるanchoringの影響は検証していない)。
- HC-010が毎回出ない原因は、Checkerの出力件数の揺れ。直接の確認はしていない。
- HC-010が真にLedger逸脱かどうかも未確認。
- Rewriteの水準(R1行の直前周回ラダー):
  - 1_word_connectiveを含むもの: 4+2+2+5=13行、3_sentenceを含むもの: 2+5+1+4+1=13行(重複あり)。4_paragraphを含むもの: 5行。
  - R2が0なので、「対象外を変えて新しい逸脱を作った」事例は記録から確認できない。

## 6. D: 既存の仕組み・過去の対策(PM_GOVERNANCE 21節 Existing Spec / Prior Trial Check)
A 既存仕様(重複提案しない):
- 設計書§4-16/§6-8: Stage 1の`same_fact_id_locations`列挙(委任_20 W2)。
- §6-16(委任_35): floorの一括適用廃止、列挙のcycle1限定。
- §4-11(委任_13): Stage 2の2-of-2(floorなしBLOCKINGのみ)。
- §6-6 A-2: 同一fact_id再出現でescalate_to_paragraph、追加1周条件(委任_11 B-3/委任_18 2-3b)、再出現時の全文Recheck(f)条件。
- precheck floor(数値・固有名詞の決定論検出)、disclosure_gap降格(委任_18 2-2、Trial限定)。
- S1-U variant(§3-1、Stage 1がPASSのときだけ+1 call、固定費約¥0.45/記事。Production既定採用はUSER_DECISION_REQUIRED)。
- 受け渡し設計(`design_open233_violation_span_handoff_01.md`、Opus L2レビュー#5): P3対応。実装は未着手。
- Opus L2レビュー#5は「受け渡しを直しても、再検査の新規指摘の揺れ・重大度の揺れは残る」と指摘済み(同レビュー18・129行)。

B 過去Trial・未採用:
- 2×V4-A union、S1-D effort=medium/low: 採否条件(既知recall miss3件全捕捉かつ負例false BLOCK≤1)未達で不採用(設計書§9-1⑧、68・4341行)。
- BLOCKING確定claimに限定したself-consistency union: 検出漏れ(見逃し)には無効で不採用(設計書5853行)。
- cycle上限の単純拡大・段落直行の復活: STOP条件で禁止(§6-14の結論)。
- Stage 1のtemperature見直し・複数回Stage 1の既定化: 根本設計変更に該当し保留(§6-14)。
- R2' rubric較正: Safety誤降格1件で不採用。

C 新規(今回の提案): E1(fact駆動の全件走査)、E4(判定履歴の揺れ検知ログ)。E2は2×V4-A unionと実質同じ機構で、目的と位置(cycle1での再利用)が違うため、Bの再試行扱い。

## 7. E: 対策設計案(実装していない)
共通: 以下は全てTrial(`er051`/`er052`のvariant)内で実現できる。Production正式path(er003など)は変更しない。全てPrompt・出力契約・見逃し対策に当たるため、実装前にOpus独立レビューが必要(条件A)。

優先順位は規模順(P2が最大)で、周回構造そのもの(周回数)ではなく「なぜ周回が必要になるか」を減らす方向で並べた。

**E1 fact駆動の全件走査(P2a・P2b対策、主案)**
- 何を変えるか: Checker PromptのTrial variantに追記。Ledgerの各fact_idについて、記事内でそのfactに触れる文を1つずつ全て確認し、重大度を問わず列挙させる。件数上限なし。出力schemaに「確認したfact_id一覧」を追加し、走査漏れを機械的に検査できるようにする。
- 追加LLM呼び出し: なし(出力量が増える分のコストは未算定)。基準は、Recheck 1回の平均¥0.427(n=13、rep19〜21の記録)。
- 効果の見込み: P2(40%)を1周目へ前倒しできる可能性。ただし根拠はHC-010が4/8で出たという小標本のみ。
- リスク: 候補が増えてStage 2とRewriteの費用・不要Rewriteが増える(Stage 2がQUALITY/ACCEPTABLEなら書き換えはしない)。Prompt変更によるprimingの前例(委任_16 B-2)がある。
- STOP条件: 検出を増やす方向であり、Safety緩和ではない。非該当と判断(ただしOpusレビュー対象)。

**E2 cycle1でChecker 2サンプルのunion(P2、E1の代替/併用)**
- 何を変えるか: cycle1のCheckerを独立に2回呼び、範囲の重なりで重複を除いた和集合をStage 2へ渡す。
- 追加LLM呼び出し: 1記事+1回(Checker 1回の平均¥0.43を基準に約+¥0.4〜0.5/記事。未実測)。Stage 2の追加分は別。
- 見込み: HC-010を1回で検出する確率を50%と仮定し(推定。独立性は未検証)、2回unionで約75%。
- 既存との関係: Bの再試行(2×V4-Aは不採用だった。ただし当時の目的は「Stage 1がPASSの記事の見逃し」で、今回は「2周目以降に出る指摘の前倒し」で測定指標が違う)。
- STOP条件: 非該当(ただしQCDトレードオフ=固定費増。最終判断は人間)。

**E3 重大度の揺れ(P1)に関する選択肢(ユーザー判断が要る可能性)**
- 事実: 揺れの直接原因は、changed_scopeのflagがdisclosure_gap降格の「外す条件」であること。
- 案3a: changed_scopeを降格の外す条件から外す、またはChecker側でflagの付け方を固定する。
  - これは決定論ルールの緩和(fail-closedを弱める)に当たる。**Safety原則の変更に触れる可能性が高く、ユーザーSTOP条件(Safety原則の変更)に該当しうる。** 実装せず判断を仰ぐ。
- 案3b: 緩和せず、揺れを可視化する(E4)。

**E4 判定履歴の揺れ検知ログ(P1の可視化、安全側)**
- 何を変えるか: 同一文字列が周回間でQ↔Bに変わった場合に、flag・llm・floorの差をStage 4レコードに記録する(決定論、¥0、Rewriteや判定は変えない)。
- 追加LLM呼び出し: なし。
- 効果: 揺れの原因(flagの出入り)が1件ごとに見える。Q/B判定自体は変わらない。

**P3(受け渡しの取りこぼし)**
- 新規提案なし。委任_39〜41の受け渡し設計(未実装)がそのまま対象。
- 実装順は、受け渡し修正 → P3の減少を測定 → 必要ならE1/E2。

**R(Rewrite起因)**
- 新規提案なし。委任_35の修正で、修正後は0/4行(n小)。
- 限定再確認で、R行が0のままか(R1が再発しないか)を確認する。Rewrite後QAの追加は、R2が0件のため今は不要と判断。

最小で効果が見込める組み合わせの所見(最終判断はFable・Opusレビュー後):
- 1) 受け渡し修正(P3)、2) E1(全件走査のPrompt追加、追加call無し)、3) E4(ログのみ)。この3つは、決定論ルールの緩和も周回数の増加も伴わない。
- E1の効果が不十分ならE2を足す。E3は人間判断が要るため、今は含めない。

限定再確認の骨子(実行していない、費用は概算):
- 目的: HC-010型の見逃しが1周目で拾えるか。
- 固定Stage 1fixture(meta_run03_standard、cycle1入力)のcycle1相当だけ、現行V4A vs E1 variant(vs E2)を各n=10。測るのは、HC-010の文を指摘した率。
  - 費用の目安: ¥0.43×10×2〜3 ≈ ¥9〜13(Checker 1回¥0.43を基準。output増は未算定)。
- 負例(正常な記事、bgroup normalなど)を各n=5、false BLOCKの増加を測る。≈¥2〜4。
- 次にflow全体をn=4(固定Stage 1)。1 runあたり約¥2(rep20・rep21の実測¥1.2〜2.2)。≈¥8。
- 合計の目安は¥20〜25。Phase累計¥482.37/総枠¥600の残枠内(未実行、概算)。
- 成功指標: HC-010の検出率の増加、負例のfalse BLOCKが増えないこと、cycle≥2のP2行の減少。

## 8. 検算・決定論確認・限界
- スクリプトは2回実行し、`results_01.json`(md5 3e96ffa6…)と`cases_detail_01.csv`(md5 3fa1cd4d…)が両方同一。標準出力も同一。
- 検算(i): rep21 s1 c3のHC-010「Some calls needed user information to continue.」は、cycle1入力記事に存在する文としてP2bと判定。固定Stage 1のdeviations・locationsには無い(`fixture_rel=not_in_fixture`)。c1・c2の本文にも存在し、どちらでも指摘されていない。
- 検算(ii): rep21 s1 c2「These calls were about trying to lower internet or cable fees.」は、c1のBLOCKING(2文のclaim)との重なりでP3と判定。委任_41のrelationは「現行⊂新、一部の文のみ対象」。
- 検算(iii): 無作為10件(seed 44)を目視。分類は定義どおり(R1: iter8 s2・rep19の複製文とsafetyの「restaurant→taxi」の編集など。P1/P2b/P3の例も定義と一致)。
- 限界:
  - Checker MINORの指摘は記録に残らず、P2を「完全な見逃し」と断定できない(§2)。
  - 版違いのrun(iter5〜rep21)を合算している。
  - R1の判定は直前周回のBLOCKING範囲との重なりのみ。R2が0件なのは、この基準による。
  - Uの8行は文字列確定不能。
  - 修正後(rep20・21)のサンプルは4行・4 runのみ。
  - HC-010が真にLedger逸脱かは未確認。
  - K2を「Recheckが返した指摘」に含めたかどうかで数値が変わる(K1のみは§3-5に併記)。
  - 偶然、無制限のgrep(`-r --include=*.py`)をバックグラウンドで1回起動したが、読み取りのみで完了した(副作用なし)。

## 9. 読んだファイルと作成ファイル
読んだ範囲(事前指定どおり):
- runnerコピー(`git show e0ae8de0`)の1100〜1190、1270〜1305、1468〜1700、4075〜4264、4490〜4660。
- `er003_v1_en_direct_vfl_01_generate.py` 502〜601。
- `er051_open233_checker_trial_variant_01.py` 175〜250。
- `er052_open233_self_recovery_stage2_production_01.py` 40〜130。
- 固定fixture(rep19)。
- 設計書: §6-14〜6-16(3118〜3292)、§6-6(2628〜2760)、§6-8冒頭(2851〜2900)。
- 委任_41の`aggregate_01.py`と`claims_detail_01.csv`。

一覧外の追加Read:
- runnerコピー: 1700〜1830、1900〜2010、2193〜2235、270〜282、430〜445(floor・降格・2-of-2・MAX_CYCLES)。
- `er003` 678〜693(`build_prior_issues_instruction`)。
- 設計書48〜76、4338〜4350。
- `opus_l2_review_open233_self_recovery_05.md`のGrep、`opus_l2_review_open233_self_recovery_02.md`・`design_open233_self_recovery_flow_01.md`のGrep(D項)。

T-0結果1行: **FAIL**(必須セクション「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」の見出しが無いと判定。委任文を要約して保存したためで、記録のみ、作業は継続)。

作成ファイル(全て未追跡、git add/commit/pushしていない):
- `C:\Users\tensh\eigo-radio\er052_output\open233_cycle_new_issue_analysis_01\analyze_01.py`
- `C:\Users\tensh\eigo-radio\er052_output\open233_cycle_new_issue_analysis_01\results_01.json`
- `C:\Users\tensh\eigo-radio\er052_output\open233_cycle_new_issue_analysis_01\cases_detail_01.csv`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_44.md`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_44.md_check.json`
- 既存ファイルは編集していない。コード・SSOT・RESULT_PACKETも触っていない。