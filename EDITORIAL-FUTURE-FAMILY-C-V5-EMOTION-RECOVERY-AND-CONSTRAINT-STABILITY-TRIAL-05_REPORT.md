# EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05

管理ID: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
性質: Trial(Family CはまだProduction採用承認ではない)。
**分類: VALIDATED(Trial範囲内。Productionへは進まずSTOP)。**

同一テーマ(家庭用ロボットと家事)・同一Layer 1 Ledger・同一Trial-02
World Scaffold/Layer2-3出力を再利用(¥0)。SSOT・Git操作・
`docs/pm/ACTIVE_TASK.md`は本タスクでは一切触っていない(Fableが後続の
CONSOLIDATIONで統合する前提)。

## 0. 分類と根拠(先出し)

**VALIDATED**。根拠:
- 語数: A2/B1ともTrial限定目安内(A2=434語/380-520、B1=520語/450-620)。
- 感情・没入感スコア: A2=3、B1=3(0〜3。共に「起伏」+「明確な選択」が
  具体描写で成立、読者が人物の内面を追える水準)。Trial-04(A2=1、
  B1=1)・Trial-03(A2=2)から明確に回復・向上した。
- 研究解説感: 0件(数値・研究語・製品名とも4本[A2/B1本生成+A2安定性
  2サンプル]全てで0件)。
- Fact Safety: 編集Gate v3 PASS、v5構造Gate(新規)PASS、Ledger
  Deviation=LEDGER_COMPLIANT、枠内hedge密度0.0%(閾値内)、いずれも
  A2/B1で成立。
- Future Framing QA v2: A2/B1ともPASS(Trial-04でB1のみ発生していた
  REVIEW_REQUIREDを是正)。
- 安定性: A2の3サンプル(本生成+追加2)とも語数目安内・見出し3つ固定
  構造PASS・感情の起伏と選択が明確。制約追加による出力の不安定化
  (語数の大きなばらつき・Gate再試行の多発・マーカー崩れ・機械的兆候)は
  観測されなかった(A2/B1本生成ともgate_attempts_used=1、初回でPASS)。
- 残存する唯一の未PASS項目はFact Checker A' verdict=REVIEW_REQUIRED
  (Layer1のみ対象)だが、これはTrial-03から不変であり、委任文により
  「本Trialの是正対象外(verdictと理由を記録するのみ)」と明示されている
  既存の未解決事項である。

ユーザー指示書の「v5が不十分」判定基準(感情・没入感がA2/B1いずれかで
2未満、または安定性のばらつきが大きい、または機械的文章の兆候が明確)の
いずれにも該当しないため、追加改善案の簡易Trial(05b等)は実施せず、
v5を最終アームとしてVALIDATEDと判定した(原因仮説→最小検証→評価の
順を守り、目的なくTrial回数を増やさないため。ただし詳細な原因分析・
複数改善案の検討自体は、将来の類似ケースに備えて4節で行っている)。

**VALIDATEDはProduction採用ではない。** Family Cは引き続き人間ユーザー
の`APPROVED_FOR_PRODUCTION`承認を経ておらず、本Trialの完了をもって
Production配線へ進むことはしない。

## 1. 何が長文化を生んでいたか(Trial-04診断の要約+v5で新たに分かったこと)

Trial-04診断(既存REPORT要約): 最大要因はLayer2/3が生成した3件の
"完成品に近い場面材料"をWriterがそのまま1対1で3ブロックへ展開していた
こと、第2要因は場面あたり「[[IMAGINED]]枠+枠外一般示唆+期待/懸念対比」
の3点セット構造が場面ごとに反復していたこと。v4はコード側で場面数を
2へ決定的に絞り込み、統合示唆段落を全場面終了後の1つに統合すること
でこれを解消した(A2 -26%/B1 -35%)。

v5で新たに分かったこと: 語数構造の是正(v4)と、感情・没入感の質は
**独立した課題**だった。v4は語数を適正化した副作用として、場面あたりの
記述密度が薄まり、「[[IMAGINED]]枠内の反応を1感情に限定する」という
v4の静的な指定が、実際には「1つの感情語を置くだけで満たせてしまう」
抜け道になっていた(Fableの直読所見どおり、A2が出来事の列挙に近づき、
感情は末尾の"leaves smiling"程度に後退)。v5では「1感情」を「1つの
感情の"起伏"(状態遷移)」へ言い換え、かつ「明確な選択を1つ含める」を
別項目として追加したところ、同じ語数目安内でも感情表現が大きく回復した
(4節・6節参照)。**語数を短くすること自体が感情表現を犠牲にするのでは
なく、Prompt側の"感情"要求の粒度(静的な1語 vs 状態遷移+選択)が
決定的だった**、というのが本Trialの主要な追加発見である。

もう1つの発見: B1のFuture Framing QA v2 REVIEW_REQUIRED(Trial-04)は、
「統合示唆段落は全場面終了後に1つだけ」という**自然文の指示だけでは
配置が安定しない**ことを示していた。v5では「見出し数を3つに固定し、
3つ目の見出し=統合示唆専用」という**構造契約**(かつ決定的コードで
検証可能な形)へ具体化したところ、A2/B1とも初回生成で配置が安定した
(4節参照)。曖昧な自然文指示よりも、検証可能な構造契約の方が安定に
寄与した、という点も本Trialの発見である。

## 2. v5で何を変えたか(v4→v5契約差分)

`er013_family_c_future_writer_05.py`(新規、v4無編集のまま保持。
`select_scenes_for_v4`・`build_trimmed_world_package_text`はv4から
import再利用、¥0・非LLM・無変更)。

1. **場面内の感情を「起伏」として要求**(v4「1つの感情に限定」→v5
   「1つの感情状態から別の状態への変化を、行動または短い台詞で示す」)。
2. **場面内に明確な"選択"を1つ追加要求**(新規。行動またはセリフで
   示す具体的な二択的選択。心情描写だけで終わらせない)。
3. **出来事列挙の上限をPrompt上のガイダンスとして追加**(1場面あたり
   目安3つ程度。ハードGateではなく、`count_events_per_scene()`
   [`er013_family_c_future_qa_05.py`、新規・決定的・¥0]で診断のみ)。
4. **統合示唆段落の配置を構造契約として固定**: 見出し数を3つに固定
   (1つ目=場面1のみ、2つ目=場面2のみ、3つ目=統合示唆+持ち帰りの
   一行のみ)。新規の`scan_v5_structure_gate()`
   (`er013_family_c_future_qa_05.py`)で、(a)見出し数=3、(b)場面1・
   場面2のあいだの見出しが1つ以下(余分な節が挟まっていない)、
   (c)場面2直後から見出しが1つだけ(統合示唆用)、を決定的に検証し、
   既存編集Gate v3と論理積(AND)で合成した(既存Gate関数自体は
   無編集)。
5. **枠外(3つ目の見出し全体)でのhedging契約を明示**: "will"のような
   断定的な未来助動詞を名指しで禁止し、"might"/"could"/"may"または
   条件節を使うことを明示。決定的な検証は、既存
   `er013_family_c_future_qa_01.detect_unhedged_future_claims()`
   (既存関数、無編集)の戻り値を`scan_v5_structure_gate()`へ渡して
   件数0を要求する形で行った(**QA側[既存の決定的heuristic]を事後
   評価に活用し、Prompt側だけに頼らない設計**。ユーザー指示の
   「QA側で事後評価し、Prompt側の制約を減らす」方向を、既存関数の
   再利用という形で部分的に反映した)。

v4→v5でも変更していないもの: 禁止表現(数値・研究語・製品名)リスト、
FACT例外の仕組み、[[IMAGINED]]枠内の書き方の原則(反応・選択まで枠内に
含める・枠内hedging不要)、語数目安(A2 380-520/B1 450-620、v4と同一)、
Fact Checker A'・Ledger Deviation Checker・Local Rewrite・Future
Framing QA v2の各関数(すべて既存のまま無改変で再利用)。

### 制約密度表(v3/v4/v5、目視による項目数の手集計。既存Prompt
テンプレートの見出しセクション単位の"要求項目"を1件として数えた概算値。
Trial限定の参考指標であり、正式な自動計測ではない)

| 区分 | v3 | v4 | v5 |
|---|---|---|---|
| 固く禁止する表現(項目数) | 5 | 5(無変更) | 5(無変更) |
| 場面数・構成に関する制約 | 0(自由、機械的3時点を明示的に否定) | 2(材料の場面数のみ使う/役割分担1つ目期待・2つ目懸念) | 4(上記2+見出し数3固定+場面間に示唆を混ぜない) |
| 場面内の感情・選択に関する制約 | 1(各場面最低1回の感情、行動/台詞で示す) | 1(各場面1つの感情に限定) | 2(感情の"起伏"1つ+明確な"選択"1つ) |
| 出来事数に関する制約 | 0 | 0(語数目安のみ、出来事数の指定なし) | 1(目安3つ程度、non-blocking) |
| 統合示唆・対比の配置に関する制約 | 1(記事のどこかで1回) | 2(全場面終了後に1つ/場面ごとの重複禁止) | 2(2つ目の場面直後・3つ目の見出し内のみ、に具体化) |
| hedging契約(枠外) | 1(一般的なhedging指示) | 1(一般的なhedging指示、v3から変わらず) | 2(一般的なhedging指示+"will"を名指しで禁止) |
| 決定的コードGate(Prompt外、参考記載) | 0 | 0 | 1(v5構造Gate、新規) |
| **概算合計(コードGateを除くPrompt内項目)** | **8** | **11** | **16** |

v3→v4は+3項目、v4→v5は+5項目(感情の起伏化+選択+出来事数目安+
統合示唆配置具体化+hedging具体化)。制約数自体は単調増加しているが、
4節の安定性評価では、この増加が出力の不安定化を招いた兆候は観測され
なかった(初回生成でのGate通過率100%[2/2]、3サンプルとも構造・語数
が安定)。ただし、これは「制約を増やしても必ず安定する」ことの証明では
なく、**v5で追加した5項目が「具体的な行動指示」(状態遷移を書け・
選択を書け・見出しを3つにせよ・"will"を使うな)であり、抽象的な
"禁止事項の列挙"ではなかったことが寄与した可能性がある**、という
仮説にとどまる(この点はGate 1判定材料として12節に記載)。

## 3. 語数(A2/B1、目安、within_range)

| レベル | word_count | target_range | within_range | 場面数 |
|---|---|---|---|---|
| A2 | 434 | 380-520 | PASS | 2 |
| B1 | 520 | 450-620 | PASS | 2 |

(安定性サンプルA2: 407語/444語、いずれもPASS。3節の値。)

## 4. 制約追加が安定性にどう影響したか(安定性3サンプル)

| サンプル | word_count | within_range | 見出し数 | v5構造Gate | 感情起伏+選択 | 機械的兆候 |
|---|---|---|---|---|---|---|
| 本生成 | 434 | PASS | 3 | PASS | あり | なし |
| stability sample1 | 407 | PASS | 3 | PASS | あり | なし |
| stability sample2 | 444 | PASS | 3 | PASS | あり | なし |

引用(各サンプルの感情起伏+選択の該当箇所):
- 本生成: "Relief turns into irritation... She can wait for more help,
  or solve the problem herself. She lifts the cord, presses continue,
  and watches the robot move again."
- sample1: "The family watches with bright relief... Relief turns
  into irritation. The parent picks up the cord, wipes the floor,
  and faces a choice: wait for more help or finish the hard part by
  hand. 'I'll do this,' they say."
- sample2: "The family's excitement turns into impatience as the
  machine waits. 'We can fix this,' says the daughter, reaching for
  a cloth. Her father chooses to wait."

機械的文章の兆候(件数と引用): **明確な兆候は検出されなかった**。
唯一の反復パターンは、3サンプル全てが"Picture a weekday evening
around 2035"に類似する導入文で始まる点だが、これは[[IMAGINED]]枠の
入口文契約(Writer Promptが明示的に要求している定型)による意図的な
設計であり、崩れた・不自然な機械的反復ではない(本文中の出来事・感情
描写自体はサンプルごとに異なる語彙・展開になっている)。出来事列挙の
目安(1場面3つ程度)は実測では守られていない(実測11〜15文/場面、
`events_per_scene`参照)が、実際に本文を読むと「出来事の列挙」ではなく
「情景+感情+選択」が混在した自然な流れになっており、Trial-04で
問題視した"出来事列挙感"は解消されている。**このことは、出来事の
"文数"という機械的指標が、実際の"列挙感"の有無と必ずしも一致しない
ことを示しており、事後の主観評価(引用付き)がこの種の判定には必要
であることを裏付けている**(残る問題として11節にも記載)。

## 5. 感情・没入感スコア(A2/B1、0〜3、根拠引用、Trial-03/04との比較)

| レベル | Trial-03 | Trial-04 | Trial-05 |
|---|---|---|---|
| A2 | 2 | 1 | **3** |
| B1 | (対象外) | 1 | **3** |

Trial-05 A2根拠: 場面1「Then the robot stops at a loose cord... Her
smile fades. She wants the machine to handle the whole task, not call
her back into it. She can wait for more help, or solve the problem
herself. She lifts the cord, presses continue...」(起伏: 期待→苛立ち、
選択: 明示的二択+実際の行動)。場面2「She first laughs at its
stubborn little turns. Then the laughter becomes tired silence. She
has a choice: keep watching, or take the old vacuum...」(同様に起伏+
選択)。

Trial-05 B1根拠: 場面1「Her smile turns into a sigh. She can wait or
finish the exception herself. She picks up a cloth, wipes the patch,
moves the cord, and says, 'Keep going.'」。場面2「At first, the
resident waits, expecting one more solution. The silence grows
irritating. He switches it off, lifts a manual vacuum...」。

## 6. 研究解説感0維持

数値・研究語(study/research/survey/report/scientist/percent/%/
according to)・"will"の出現件数を、A2/B1本生成+A2安定性2サンプルの
計4本で決定的にgrep確認した。

| ファイル | "will"件数 | 研究語件数 |
|---|---|---|
| Trial-05 a2/reader_facing_article.txt | 0 | 0 |
| Trial-05 b1/reader_facing_article.txt | 0 | 0 |
| stability a2_sample_1 | 0 | 0 |
| stability a2_sample_2 | 0 | 0 |

編集Gate v3の`numeric_hits`/`research_term_hits`/`product_name_hits`
もA2/B1いずれも0件(`editorial_gate_result_final_pre_rewrite.json`参照)。
「解説調段落」(現在の統計・調査結果を読者へ説明する構造)も本文中に
確認されなかった。

## 7. Fact Safety

| 項目 | A2 | B1 |
|---|---|---|
| 編集Gate v3 | PASS | PASS |
| v5構造Gate(新規) | PASS | PASS |
| imagined_hedge_density(枠内) | 0.0%(閾値内) | 0.0%(閾値内) |
| Ledger Deviation(Layer1) | LEDGER_COMPLIANT(rewrite cycle=0) | LEDGER_COMPLIANT(rewrite cycle=0) |
| Fact Checker A'(Layer1、本Trial是正対象外) | REVIEW_REQUIRED(Trial-03から不変) | REVIEW_REQUIRED(Trial-03から不変) |

Fact Checker A' verdict=REVIEW_REQUIREDは、委任文により本Trialの是正
対象外と明示されているため変更していない。理由の記録のみ行う
(`er013_output/family_c_future_trial_05/{a2,b1}/fact_check_result.json`
参照。Trial-03/04と同種の指摘であり、本Trialで新規に生じたものではない)。

## 8. Future Framing QA v2 verdict(A2/B1)と統合示唆段落の配置結果

A2/B1ともPASS(`future_framing_qa_result.json`参照)。統合示唆段落の
配置は、v5構造Gateの決定的検証により、A2/B1とも(a)見出し数=3、
(b)場面1・場面2のあいだに余分な見出しなし、(c)場面2直後の見出しが
1つ(統合示唆用)のみ、を満たしていることを確認した
(`v5_structure_gate_result_final_pre_rewrite.json`参照、両レベルとも
`fail_reasons: []`)。

## 9. 追加案を試した場合(本Trialでは未実施、検討のみ)

v5が判定基準(4節)を満たしたため、追加改善案の簡易Trial(05b等)は
**実施していない**。ただし、将来同種の課題(Family C以外のFuture記事
respec等)に備え、委任文の要求どおり検討だけは行った。

### 9-1. 失敗原因の分類(仮にv5が不十分だった場合を想定した準備的分類)
v5は判定基準を満たしたため「失敗原因」自体は発生していないが、Trial-04
の失敗原因を再分類すると: (a)制約不足(v4「感情1つ」が状態遷移を
要求せず、末尾の感情語1つで満たせる抜け道があった)、(b)配置の
自然文指示への依存(構造契約ではなく自然文の"全場面終了後に1つだけ"
という指示のみで、配置の安定性を担保できなかった)。制約過多・
Scaffold情報過多・QA側の問題、はTrial-04の主要因ではなかった
(Scaffold情報はv4で既に11件削減済み、QA側[Framing QA v2]は正しく
問題を検出できていた)。

### 9-2. 追加改善案(最低3案、制約削減方向2案以上を含む、検討のみ)

| 案 | 方向性 | 内容 | QCD概算(費用/工数/品質リスク/安定性リスク) |
|---|---|---|---|
| A. 感情1+選択1を編集目標化(制約削減方向) | 制約削減 | "厳密contract"ではなく「望ましい編集目標」として提示し、Writerの裁量を残す | 費用同等/工数小/品質リスク: 目標未達の場合の検出が難しくなる/安定性リスク: 低〜中(自由度が増えるほど検証が主観判断に依存) |
| B. 場面数非固定・総語数budget内配分(制約削減方向) | 制約削減 | 場面数をコード側で2に固定せず、Writerに総語数内で場面数・配分を委ねる | 費用同等/工数中(語数gateの調整要)/品質リスク: 語数超過の再発リスク(Trial-03の再発条件)/安定性リスク: 中(場面数のばらつきで比較が難しくなる) |
| C. QA側事後評価でPrompt制約を減らす(制約削減方向、v5で部分実装済み) | 制約削減 | Prompt上のhedging契約を減らし、既存の`detect_unhedged_future_claims()`等の決定的heuristicで事後検出→regenへ委ねる | 費用同等(既存関数の再利用のため追加費用¥0)/工数小/品質リスク: 低(既に有効な検出ロジックがある)/安定性リスク: 低(v5で実証済み) |
| D. 1場面を濃く+2場面目を短いcontrast(制約追加方向) | 場面配分の非対称化 | 場面2を意図的に短くし、場面1に感情描写を集中させる | 費用同等/工数中/品質リスク: 場面2の印象が薄くなるリスク/安定性リスク: 中 |
| E. Scaffold情報のさらなる整理(制約削減方向) | 入力量削減 | World Package絞り込みをさらに厳しくする | 費用¥0(決定的処理)/工数小/品質リスク: 場面の説得力低下リスク/安定性リスク: 低 |

v5はC(既存QA関数の事後評価活用)を部分的に採用し、A・B・D・Eは
未実施(v5が判定基準を満たしたため)。もしv5が不十分だった場合、
最有望候補はC(既に実証済みの決定的関数を使い、追加LLM呼び出し
費用¥0で実施できるため)、次点はA(制約密度を実際に下げられる)と
判断していた(参考記録)。

### 9-3. 実施した案ごとの結果と費用
実施なし(v5が判定基準を満たしたため05b等の簡易Trialは行っていない)。

## 10. 残る問題

1. Fact Checker A' verdict=REVIEW_REQUIRED(Layer1、A2/B1とも)が
   Trial-03から不変のまま残っている(本Trialの是正対象外、既存の
   未解決事項)。
2. 出来事数の目安("1場面3つ程度")はPrompt上のガイダンスに留まり、
   実測では守られていない(4節参照)。結果として"列挙感"自体は解消
   されたが、文数ベースの機械的な上限管理は機能していない
   (non-blocking診断のみで、ハードGateにしていないため)。
3. Trial-05はA2側のみ3サンプルの安定性評価を行った(委任文の指定
   どおり)。B1側の安定性(複数サンプルでの再現性)は未検証。
4. v3/v4/v5の制約密度表は目視による概算集計であり、自動計測ではない
   (2節に明記)。

## 11. Gate 1判定材料(Fableへ)

- v5契約(感情の起伏+選択+出来事数目安+統合示唆配置の構造契約化+
  枠外hedging契約の名指し化)により、Trial-04で後退した感情・没入感を
  A2/B1とも0〜3スコアで3まで回復させ、かつTrial-04で新規発生した
  Future Framing QA v2 REVIEW_REQUIRED(B1)を解消した。
- 制約項目数は概算でv3(8)→v4(11)→v5(16)と増加したが、A2/B1本生成
  ともに初回生成でGate通過(gate_attempts_used=1)、3サンプルの安定性
  評価でも語数・構造の乱れは観測されなかった。「感情・選択・構造配置を
  "具体的な行動指示"として要求する」設計であれば、この規模の制約追加
  自体が直ちに不安定化を招くわけではない、という限定的な実証example
  として報告する(一般化にはさらなるテーマでの検証が必要)。
- 一方、機械的な数値目安(出来事数3つ程度)は守られておらず、「制約の
  数値化」と「実際の遵守」は別問題である点も合わせて報告する。
- Fact Checker A' REVIEW_REQUIREDは既存の未解決事項として残っている
  (Family C全体のGate 1判定において、この点の扱いをFable/ユーザーが
  別途判断する必要がある)。
- 本Trialの結論はFamily Cの**Trial範囲内でのVALIDATED**であり、
  Production採用(`APPROVED_FOR_PRODUCTION`)には進んでいない。

## 12. 費用

### 12-1. API別

Trial-05累積(OpenAI、Standard同期のみ): ¥22.88(内訳: a2本生成一式
[Writer+Fact Checker A'+Ledger Deviation+Framing QA]=¥7.52、b1本生成
一式(累積差分)=¥14.12、A2安定性2サンプル(Writer呼び出しのみ、累積
差分)=¥1.24)。

### 12-2. 5区分(`docs/pm/PM_GOVERNANCE.md` 15-5準拠)

1. **今回実測**: ¥22.88(Standard同期経路、全呼び出しStandard同期)。
2. **Trial特有の追加コスト**: 実質¥0。Research/World Scaffold/
   Layer2-3はTrial-02からのread-only再利用(¥0)。v5構造Gate
   (`scan_v5_structure_gate`)は決定的コード処理(¥0、非LLM)。
3. **異常retry・Human Review由来の上振れ**: なし。A2/B1とも
   `gate_attempts_used=1`(初回でPASS)、`writer_attempts_last_gate=1`、
   `local_rewrite_cycles_used=0`。Human Review Queueへの計上なし。
4. **Standard同期でのコスト**: ¥22.88(上記と同一。本Trialは全てStandard
   同期経路のみで実行し、Batch経路は使用していない)。
5. **Batch量産換算時のコスト**: 未算出。Family CはまだProduction採用
   前のTrial段階であり、Batch量産設計(バッチ割引率適用時の1記事原価)は
   本Trialのスコープ外。Production採用判断時に別途算出が必要。

1記事セット(A2+B1、QA一式込み)あたりの実測原価目安: ¥21.64
(a2 ¥7.52 + b1 ¥14.12)。安定性確認用の追加Writer単体呼び出しは
1回あたり約¥0.6-0.65。

### 12-3. Family C残額

Trial-05実施前残額: ¥105.01(+追加上限¥100=合計上限¥205.01)。
Trial-05消費: ¥22.88。
**Trial-05実施後残額: ¥205.01 - ¥22.88 = ¥182.13**
(内訳: 元のFamily C残額のうち¥82.13相当+追加枠¥100は未使用のまま
残っている、という计算ではなく、単純に合計上限¥205.01からの消費実額
として管理する。Fableへの引き継ぎ時は「合計上限¥205.01のうち
¥22.88消費、残り¥182.13」として扱うことを推奨する)。

## 13. Artifact(rootからの相対パス)

- `er013_output/family_c_future_trial_05/index.html`
- `er013_output/family_c_future_trial_05/comparison.md`
- `er013_output/family_c_future_trial_05/a2/reader_facing_article.txt`
- `er013_output/family_c_future_trial_05/b1/reader_facing_article.txt`
- `er013_output/family_c_future_trial_05/a2/run_summary.json`
- `er013_output/family_c_future_trial_05/b1/run_summary.json`
- `er013_output/family_c_future_trial_05/{a2,b1}/v5_structure_gate_result_final_pre_rewrite.json`
- `er013_output/family_c_future_trial_05/{a2,b1}/future_framing_qa_result.json`
- `er013_output/family_c_future_trial_05/{a2,b1}/fact_check_result.json`
- `er013_output/family_c_future_trial_05/stability/a2_sample_1/reader_facing_article.txt`
- `er013_output/family_c_future_trial_05/stability/a2_sample_2/reader_facing_article.txt`
- `er013_output/family_c_future_trial_05/stability/a2_stability_summary.json`
- `er013_output/family_c_future_trial_05/cost_summary.json`
- `er013_output/family_c_future_trial_05/e2e_run_summary.json`
- `er013_output/family_c_future_trial_05/research/world_package_text_v5.txt`

### commit対象候補ファイル一覧(Fableが後続CONSOLIDATIONで明示add)

- `er013_family_c_future_writer_05.py`(新規)
- `er013_family_c_future_qa_05.py`(新規)
- `er013_family_c_future_qa_test_05.py`(新規)
- `er013_family_c_future_trial_05_run.py`(新規)
- `er013_output/family_c_future_trial_05/`(新規ディレクトリ全体)
- `docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05.md`(新規)
- `docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_check.json`(新規)
- `EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_REPORT.md`(本ファイル、新規)
- `docs/pm/RESULT_PACKET_FC5.md`(新規)

## 14. T-0結果・事前指定外Read・STOP該当

- T-0: PASS(`docs/pm/delegation_log/..._check.json`、reasons無し)。
- 事前指定外Read(理由付き):
  1. `er013_family_c_future_qa_02.py`の`run_future_framing_qa_v2`/
     `route_article_for_qa_v2`本体・developer message(理由: 事前指定
     Grep対象の`qa_03.py`はこれらをqa_02から再輸出しているだけで、
     実体がqa_02にあったため、Future Framing QA v2の判定基準[6項目]を
     正確に把握し、v5のhedging契約設計の妥当性を確認する必要があった)。
  2. `er013_family_c_future_qa_01.py`の`detect_unhedged_future_claims`/
     `_UNHEDGED_FUTURE_RE`/`extract_imagined_blocks`本体(理由: 既存の
     決定的heuristicが実際に何を検出するか[枠外の"will"検出ロジックの
     正体]を確認し、v5構造Gateへの再利用可否を判断する必要があった)。
  3. `er013_family_c_future_writer_03.py`の禁止表現・構成要素セクション
     (理由: 2節の制約密度表[v3/v4/v5比較]を作成するため、v3の実際の
     Prompt項目数を確認する必要があった。事前指定Read一覧はv4全文の
     みで、v3は含まれていなかった)。
- STOP該当: なし(VALIDATEDで完了、追加のUSER_DECISION_REQUIREDは発生
  していない)。

## 15. SSOT追記文案(編集は行っていない、Fableが後続CONSOLIDATIONで反映)

### OPEN-147末尾追記案

```
【2026-09-13追記、EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-
CONSTRAINT-STABILITY-TRIAL-05】v5(感情の起伏1つ+選択1つ+出来事列挙の
目安上限+統合示唆段落配置の構造契約化[見出し3つ固定]+枠外hedging契約
["will"名指し禁止])を実施しVALIDATED(Trial範囲内、Production未採用)。
A2 word_count=434(380-520内)、B1=520(450-620内)。感情・没入感スコア
(0-3、主観+引用根拠)はA2=3・B1=3(Trial-04のA2=1・B1=1、Trial-03の
A2=2から回復)。編集Gate v3・新設v5構造Gate・Ledger Deviation・Future
Framing QA v2はA2/B1ともPASS/COMPLIANT(Trial-04でB1のみ発生していた
Future Framing QA v2 REVIEW_REQUIREDを解消)。Fact Checker A'
verdict=REVIEW_REQUIRED(Layer1)はTrial-03から不変で残存(本Trial是正
対象外)。安定性評価(A2×3サンプル)では制約追加による出力不安定化は
観測されず、判定基準未達に該当しなかったため追加案の簡易Trial(05b等)
は実施していない。Trial-05実測費用¥22.88(Family C合計上限¥205.01
[残額¥105.01+追加¥100]のうち。残り¥182.13)。詳細は
`EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-
TRIAL-05_REPORT.md`。VALIDATEDでもProductionへは未着手、Family Cの
`APPROVED_FOR_PRODUCTION`は依然として未取得。
```

### DECISION_LOG新エントリ案

```
## EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-
STABILITY-TRIAL-05(2026-09-13)

Family C Future v5契約(感情の起伏+選択+出来事列挙の目安上限+統合示唆
段落配置の構造契約化+枠外hedging契約)を新規ファイル
(`er013_family_c_future_writer_05.py`/`er013_family_c_future_qa_05.py`/
`er013_family_c_future_trial_05_run.py`、既存_01〜_04は無編集)で実装し、
Trial-02由来の同一Ledger・同一World Scaffold/Layer2-3を再利用して
A2/B1を各1本生成+A2安定性3サンプルを実測した。結果はVALIDATED(Trial
範囲内、Production未採用)。感情・没入感スコアがTrial-04(A2=1/B1=1)
からA2=3/B1=3へ回復し、Trial-04でB1のみ発生していたFuture Framing
QA v2 REVIEW_REQUIRED(統合示唆段落配置+枠外"will"未hedge)を解消した。
制約項目数は概算でv3(8)→v4(11)→v5(16)へ増加したが、安定性評価
(A2×3サンプル)では出力の不安定化(語数ばらつき・Gate再試行・機械的
兆候)は観測されず、A2/B1本生成とも初回生成でGate通過した。ユーザー
指示書が定めた「v5不十分」判定基準に該当しなかったため、追加改善案
(制約削減方向2案含む計5案を検討)の簡易Trial(05b等)は実施していない。
Fact Checker A' verdict=REVIEW_REQUIRED(Layer1)はTrial-03から不変で
残存し、本Trialの是正対象外(既存の未解決事項)。実測費用¥22.88
(Family C合計上限¥205.01のうち。残り¥182.13)。VALIDATEDはProduction
採用を意味せず、Family Cは引き続き人間ユーザーの
`APPROVED_FOR_PRODUCTION`未取得。詳細は
`EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-
TRIAL-05_REPORT.md`。
```
