# RCA: OPEN-233 E2E neg7 Human Review発生(委任_22、2026-10-05、¥0・read-only)

管理ID: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01。provenance=fresh Stage 1 / E2E途中(frozen・reuse・代替なし)。VALIDATED不可、Production未反映。ラベルは【確認】=run json・runner・Ledger原文で確認、【推測】=私(Sonnet)の判定でありFable/ユーザー未確認。gold変更ではない。
抽出: `er052_output/open233_kpi_recovery_02_offline_01/e2e_neg7_rca_extract_01.py`(出力`e2e_neg7_rca_extract_01.json`)。有料call 0。

## 1. 結論(先に)

- Human Review KPI(0件)は**FAIL確定(1/9 run)**。neg7(meta、負例/NORMAL)がSTAGE4_ESCALATION(`blocking_structural_after_ladder`)。
- 【確認】neg7のSTAGE4は**構造要素でないのに`blocking_structural_after_ladder`として返された**。直接原因は、T(最終手段の決定論削除)が「同cycleで既にRewrite成功済みのclaim」を再度削除対象にし、文が既に変わっているため位置特定不能(`mismatch`/`no_verbatim_anchor_in_article`)→`_t_fail`→STAGE4。→ **分類① 単純な実装不具合(T経路のcarry-forward欠落)**。設計doc(design_open233_kpi_recovery_02.md L704)が「範囲外の観察」として既に指摘していた「T削除失敗経路は構造要素の検証なしでSTAGE4へ」と同型。
- 【確認】根本の上流は**②設計問題**: neg7のBLOCKING 12件中、Stage 2 LLMがBLOCKINGと判定したのは0件。全12件が`deterministic_floor`(Stage 1のchanged_*フラグ由来)による強制BLOCKING(`FLOOR_VERIFY_MODE=time_only`のため時期以外のfloorはLLM再確認・S1を通らない)。【推測】12件中、誤BLOCKING(問題なし/軽微)9、判断不能3、正当0。
- ③正当(本当の重大逸脱でRewrite不能)は**該当しない**【推測】。
- 非SC 8 run: 7 runでRewrite発火(hormuz_standardのみ0)。BLOCKING計35件、【推測】誤24/判断不能5/正当6。35件全件がfloor強制で、うち31件はStage 2 LLM判定がBLOCKING以外。増分の主因は**新Stage 1(r3主導)の候補数増(1 run 8〜32件)×floor強制BLOCKING**。OF-032(BLOCKING率0.10は過小評価)は**実測で裏付け**: BLOCKINGを持つrun率 E2E 7/8=0.88 vs rep30同instance 1/8=0.125(n小、推測を含む)。

## 2. neg7の経路(【確認】)

| 段 | 内容 |
|---|---|
| Stage 1 | r3(medium)+r5(high)、union 24候補(r3のみ20・両方4・r5のみ0・決定論のみ2)。29判定単位中24が候補=ほぼ全文が候補。HC-006/010/012/004/014に分散 |
| Stage 2 cycle1 | 24 claim中BLOCKING 9(HC-004×1、HC-006×2、HC-010×5、HC-012×1)。9件ともLLM materiality=ACCEPTABLE、floor_reasonが`changed_actor/comparison/negation`等。S1は降格確認15件のみ(全件`confirmed_downgrade=True`、split 0)。「S1が割れてBLOCKING」は**発生していない** |
| Rewrite cycle1 | 9 records: word×3、sentence(削除)×1、paragraph×4、先行Rewrite済みでcarry-forward×1。guard全通過。品質劣化regenが走り+9 call |
| Recheck cycle1 | prior 9件が全て未解消(`coverage scope recheck: candidate remains (model)`)。同fact_id内に候補が残る限り未解消にするfail-closed。Rewrite後の忠実な文(例: 「Meta employees worried ...」)自体がStage 1の候補になるため残る→NEXT_CYCLE |
| Stage 2 cycle2 | 13件中BLOCKING 3: (i)HC-004「So it sounds like a simple story ... someone takes care of the call.」floor=changed_causality、(ii)HC-010「The issue was not just that humans handled calls.」floor=changed_comparison、(iii)HC-010「Users might not know who was doing the work ... personal information might reach that person.」tier0:aux:issue_actor。残り10件はACCEPTABLE/QUALITY(S1一致) |
| Rewrite cycle2 | 5 records: (i)3_sentence削除成功。(ii)ladder枯渇: location_carryで前cycleに1_word・4_paragraph使用済み→計画level空、⑥無効→`ladder_exhausted_without_full_rewrite`(Rewrite未試行)。(iii)3_sentenceで「Employees raised concerns ...」へ置換成功。 |
| T(最終手段) | 枯渇claimの`fact:MUSE-HC-010`でT対象を選ぶ=同fact_idの**(ii)と(iii)の両方**が対象。(ii)は決定論削除成功。(iii)は直前のRewriteで既に置換済み(before→after確認済)のため本文に存在せず`span_unverified(mismatch)`、`target_not_locatable=True`、guard失敗 |
| STAGE4 | `_t_fail`あり→`blocking_structural_after_ladder`(許可リストで`allowed`)。`structural_reasons=[]`(構造要素でない)、`structural_ladder_exhausted_verified`はこの経路では呼ばれない(runner L9025-9035) |

## 3. 判定(c) neg7の12 BLOCKING(【推測】、Ledger原文と対比)

- 誤BLOCKING(9): 比喩・修辞・Ledgerの注意書きと整合する記述。例: 「It was like an AI-led play with a hidden supporting actor.」(比喩)、「A service that seemed simple now looked like a mystery story.」(比喩)、「No large information leak was confirmed.」(HC-010 notes_for_writer「大規模な情報漏えいが発生したと断定しない」と整合)、「The company did not stop Muse itself.」(HC-012 notes「サービス全体を停止したとは書かない」と整合=floor changed_negationの誤発火)、「The issue was not (just) that humans handled calls.」(×2、修辞的対比)、「That uncertainty turned convenience into a mystery.」、「So it sounds like a simple story ...」(×2、接続詞Soでfloor)。
- 判断不能(3): 「Imagine asking AI to book a haircut.」(HC-004は「散髪の予約を依頼できる」、AIが予約を完結と読める軽微な拡張)、「users could not know who ... personal information might reach」(HC-010は従業員の懸念、ユーザー一般へ主体拡張=軽微〜中、c1とc2で各1)。
- 正当(重大逸脱): 0。いずれもLedger事実の反転・数値・主体の置換ではなく、重大Fact見逃しにはならない水準【推測】。

## 4. (d) Recheckと「解消判定にならなかった」理由(【確認】)

cycle1のRecheck 9件全て未解消は、【確認】Rewriteが全9 recordでguard通過・文を変えた後に、Recheck(r3+r5v、scope 22単位)が同fact_id内にStage 1候補が残ると未解消とするため。Rewrite後の正しい文も候補化(Stage 1 r3が29単位中24を候補にする)→未解消→NEXT_CYCLE。cycle2のStage 2はそのうち10/13をACCEPTABLE/QUALITYに戻した=Recheckの未解消は「追加cycleでStage 2に再判定させる」役割を果たしたが、約¥1.2の再検査+追加cycleのコストを生んだ。Recheck新仕様自体の誤作動(解消済を未解消にした等)は未確認。主因はStage 1候補の過剰さ。
cycle2のdelete-genericは(ii)は成功、(iii)のみ失敗(上記T経路の重複対象)。

## 5. (f) 分類
- ①実装不具合(Human Review 1件の直接原因): T経路が同cycleのRewrite成功済みclaimを再対象化。非構造要素の失敗が構造要素用STAGE4理由に写像される(名前の洗い替え、委任_12で指摘された型の別経路)。
- ②設計問題(全件Rewriteの原因): (1)Stage 1 r3の候補過剰(r3のみ20/24)。(2)floorがLLM ACCEPTABLEを覆してBLOCKING化(時期以外のfloor_verifyなし、S1非経由)。(3)Recheckのfact_id粒度のfail-closed。(4)ladderのlocation_carryで同factの2度目は計画level空→即枯渇。
- ③正当: 該当なし。

## 6. 非SC 8 runのBLOCKING審査(【推測】ラベル、詳細はextract json)

| run | E2E BLOCKING(cycle) | floor強制/LLM非BLOCKING | 誤/判断不能/正当 | rep30同instance |
|---|---|---|---|---|
| hormuz_adv | 1 | 1/1 | 誤1(attacks by US and Iran、HF-009) | 候補なし(ACCEPTABLE_STAGE1) |
| hormuz_std | 0 | - | - | Stage2降格のみ(同) |
| meta_adv | 4(c1:3,c3:1) | 4/4 | 誤3(修辞的対比・規範)、正当1(HC-011単一事例の複数化) | 候補なし |
| meta_std | 5 | 5/3 | 誤3、正当2(HC-011、LLM自身がBLOCKING) | Stage2降格のみ |
| neg1(¥8.82) | 9(c1:7,c2:2) | 9/9 | 誤7、判断不能2(「voice was not AI at all」「A human can handle ...」) | Stage2降格のみ |
| neg2 | 2 | 2/2 | 誤1、正当1(HC-011複数電話化) | Stage2降格のみ |
| neg3 | 2 | 2/0 | 正当2(HF-003主体、HF-009因果。rep30もHF-009はBLOCKING=再現) | BLOCKING1(HF-009) |
| neg7 | 12(c1:9,c2:3) | 12/12 | 誤9、判断不能3、正当0 | 候補なし |
| 計 | 35 | 35 / 31 | 誤24・判断不能5・正当6 | BLOCKING 1件・Rewrite 1/8 run |

増分の分解(【確認】数、由来は【推測】): (a)新Stage 1候補数 8〜32件/記事(集計値平均19.8件/記事(9 run)、rep30の旧Stage 1は同instanceで多くが候補0)×(b)floor強制BLOCKING(35件全件floor。うちLLM非BLOCKING 31件)が主因。(c)Recheck未解消→追加cycle: 7 runでcycle3以上(cycle分布1/2/3/4=1/1/6/1)、費用は追加cycleとRecheck(平均¥0.87/記事)に表れる。(d)出口全文Exit 3'-R: 7 run実施、全件に候補あり(api失敗0)。neg1(¥8.82): cycle4、BLOCKING 9件(c1:7→c2:2)、Stage 1候補32件が最大で、Rewrite 9+追加cycle。
## 7. OF-032との関係
OF-032(BLOCKING率0.10は過小評価、Human Review 0見込みはE2Eでしか測れない)は実測で裏付け(BLOCKING run率7/8、n小)。OF-033(13〜24件への外挿): 候補24件のneg7はStage 2が24件を判定(cycle1 Stage 2費用 約¥1.19、body/hook+S1)、出力打ち切り・parse失敗は観測されず(call_logにapi/parse失敗なし)【確認】。ただしn=1のため外挿の安全は未確認。

## 8. 是正案(列挙のみ。実装・Trial開始は禁止、ユーザー/Fable判断待ち)

| 案 | 内容 | Safety影響 | ユーザー承認 |
|---|---|---|---|
| A | T経路: 同cycleでRewrite成功済み/carry-forward対象のclaimをT対象から除外(または未発見をcovered扱い) | なし(重大検出を減らさない) | 設計docの既存意図(I-2/T)に沿う不具合修正。コード変更のためFable委任とOpus要否判断。Stage 2構成は不変 |
| B | `_t_fail`等で`blocking_structural_after_ladder`を返す前に`structural_ladder_exhausted_verified`相当の検証を必須化(非構造は別処理=追加cycle/judge-only) | なし〜小(Human Reviewを減らすだけ、検出は減らさない) | 設計doc L704が「新仕様候補、Fable判断」としていた項目=ユーザー承認の要否はFable判断 |
| C | floor_verifyを時期以外(changed_comparison/negation/actor/number)へ拡張(LLM再確認/S1通過後にBLOCKING) | 中: 誤BLOCKING削減の反面、真の重大floorをLLMが降格し見逃すリスク(Stage 2のB3 mis-downgrade履歴あり) | 必要(Stage 2は承認済み構成の変更) |
| D | Stage 1 r3プロンプトで修辞・比喩・規範的コメントをchanged_comparison等の対象外と明示、または候補にしない | 中: Stage 1 recall低下の可能性(OF-001未測定) | 必要(prompt変更、承認済みStage 1構成の変更) |
| E | Recheckの未解消判定をfact_id粒度から「claim(文)単位」へ(Rewrite後の忠実文を未解消にしない) | 小〜中: 本当に残った逸脱を見逃す可能性、fail-closed緩和 | 必要(Recheck新仕様の変更) |
| F | ladderのlocation_carryで同fact再発時の「計画level空→即枯渇」を、構造要素以外では上位levelへ再試行 | なし | 軽微設計変更、Fable判断 |
| G | 判定不能/軽微なfloorは「BLOCKINGでなくQUALITY相当で記録」(閾値変更) | 大: Safety定義近傍。非推奨(重大検出を減らす) | 必須、現時点では勧めない |

【推測】Human Review 0のためには最低A+B(出口の誤写像是正)が必要。ただしそれだけでは全件Rewrite(コスト増・cycle増)は改善しない。コスト面の改善にはC/D/Eのいずれかが必要で、全てユーザー承認事項。

## 9. 残11 run(SC)の扱いの材料(結論はFable)

- 継続で得る情報: E2E下でのSafety見逃し0の実測(残SC 11 run分。現状はB3の1/1のみ)、SC runでのfloor/T経路の再現(同じ実装不具合の再発頻度)、Human Review分母の増加。費用は推測mid¥55〜70(残¥83.17、閾値¥20)。
- 継続しない場合に失う情報: 新Stage 1+現構成でのSafety見逃し0のE2E証拠(Safety Gate未判定のまま)。ただしHuman Review KPIは既にFAILで、継続しても覆らない。
- 注意【推測】: A〜Fのどれかを実装した後はSC結果が構成不一致となり再測定が必要。未修正コードで11 run(約¥55〜70)を使うと、修正後に再実行する費用と二重になる可能性が高い。
- 現状Safety: B3 1/1(Stage 1検出M、出口残存なし)、見逃し0。SCは旧A2A3 abort以外未実施。
