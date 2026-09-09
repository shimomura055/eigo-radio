# FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01 報告書

管理ID: FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01(Lane A、¥0 offline
限定、読み取り集計のみ、Sonnet委任)。API呼び出しなし。Production/Prompt/
QA/Validator/retryコード編集なし。Git操作・SSOT編集・`docs/pm/ACTIVE_TASK.md`
/`RESULT_PACKET.md`編集は行っていない。並列稼働中のHousehold候補生成
(`er011_output/household_unified_final_candidate_01/`)は参照・接触していない。
出力: `er011_output/news_stage4_evidence_allocation_audit_01/`。script:
`er011_news_stage4_evidence_allocation_audit_01.py`(root)。

対象データ: 既存48 run(Hanshin Trial-04/06、Theme2 Trial-05 gapfix、CAR-T
Trial-09、Stage2診断分岐Trial-08 Part A)、`point_role_planning_{initial,
retry*}.json`の`evidence_anchor`自由記述テキストからFACT-ID(Hanshin:
`FACT-01`〜、CAR-T: `FACT-001`〜、Theme2: `F-201`〜、テーマごとに書式が
異なるため正規表現をテーマ別に切替)を機械抽出。**データ欠落: 0件**
(48 run全てで`point_role_planning`・`point_overlap_article_retry_log`が
揃っており、124 attempt観測を欠落なく取得)。

---

## Part 1: Evidence Allocation衝突監査

### (a)(c) 衝突率と相関

| 指標 | 値 | n |
|---|---|---|
| P1/P2 anchor衝突あり(run単位、初回attempt) | 41.7% | 48 run |
| P1/P2 anchor衝突あり(run単位、最終attempt) | 50.0% | 48 run |
| P1/P2 anchor衝突あり(attempt単位、全体) | 44.4%(55/124) | 124 attempt |
| 衝突の再燃率(同一FACTが以前のattemptでも衝突要因だった) | 23.6%(13/55) | 55衝突event |
| anchor conflict_count vs P1-P2語彙overlap_ratio(cross、Spearman) | **r=0.4623** | n=124 |
| anchor conflict_count vs 実際のGate指標(Point対Full Story overlapの最大値、Spearman) | **r=0.1852** | n=124 |
| anchor conflict_count vs lexical_flagged(attempt単位二値、Spearman) | r=0.1290 | n=124 |
| anchor conflict_count vs 最終NG(run単位二値、Spearman) | **r=0.0997** | n=124 |

**事実**: anchor衝突数はP1対P2の語彙重複(cross_point_overlap)とは中程度の
正相関(r=0.46)を示すが、実際にretry判定を左右するGate指標(Point対Full
Story overlap、閾値0.40)とはr=0.19、最終NGとはr=0.10と弱い。これは
`cross_point_overlap`(#7)がretry判定に未使用(OPEN-133、DEFERRED)という
既存の構造的事実と整合する—anchor衝突は「P1とP2が似た語彙になる」ことは
説明するが、「記事がNGになる」ことの主要因ではない(**事実、相関係数から
直接読める範囲**)。

### (b) initial→retryのanchor変化(retryのみ、n=76×2 Point)

| Point | fixed(同一) | changed(変更) | regressed(以前と完全一致に回帰) |
|---|---|---|---|
| Point One | 14.5%(11/76) | 78.9%(60/76) | 6.6%(5/76) |
| Point Two | 17.1%(13/76) | 76.3%(58/76) | 6.6%(5/76) |

**事実**: retry時にanchorが前回と完全一致する(fixed)のは15〜17%のみで、
大半(76〜79%)は新しいFACT-ID組み合わせへ変わる。これは既存報告(Role
Planningは`topic, verified_ledger_text`のみを入力とする「盲目の再抽選」)
と整合する。完全一致での回帰(regressed)は6.6%と少ないが、背景に記載された
実例(`daily_news_focus_layer_comparison_trial_04/a2/baseline/run1`、initial
P1=FACT-02/03/04・P2=FACT-01/02/05→retry2でP1=FACT-02/03/04/05・
P2=FACT-02/04/05)を本監査でも再現確認した(衝突数1→0→3、cross_overlap_
ratio 0.192→0.067→0.333)。厳密な集合一致に基づく`regressed`定義よりも
広い「以前に衝突要因だったFACTを再び使う」を測る衝突再燃率23.6%の方が、
この種の部分的な回帰を捉えている。

### (d) テーマ別fact供給量とNG率

| テーマ | 使用可能fact数(Ledger) | run数 | 最終NG率 | Pointが参照したfact数(平均) | fact利用率 |
|---|---|---|---|---|---|
| Hanshin(single_event_boxscore) | 5(FACT-01〜05、06/07はDISPENSABLE/scope除外) | 36 | **72.2%** | 4.78 | **95.6%** |
| Theme2(survey_trend) | 8(F-201〜209、F-207のみCOULD_NOT_CONFIRM) | 8 | **50.0%** | 5.38 | **67.2%** |
| CAR-T(mechanism_limitation) | 14(FACT-001〜015、FACT-005欠番) | 4 | **0.0%** | 5.25 | **37.5%** |

**事実**: 使用可能fact数(5→8→14)とNG率(72.2%→50.0%→0.0%)は単調な逆
関係にある。fact利用率(Point Role Planningが実際にanchor参照したfact数
/使用可能fact数)も95.6%→67.2%→37.5%と単調に低下し、Hanshinでは5個中
ほぼ全て(4.78個)が毎回Pointに割り当てられる一方、CAR-Tでは14個中5.25個
しか使われず大きな余裕がある。この利用率の方が生のfact数よりも「割当の
逼迫度」を直接表す指標として意味がある(**解釈**)。

**交絡の明記(既存報告と同一の限界)**: これはテーマ=3点のみの比較であり、
topic_structure(single_event_boxscore/survey_trend/mechanism_limitation)・
条件構成(Hanshinはbaseline/focus/focus_hint/hint_only/gapfix/branch_
diagnosticの6条件・N=36、CAR-Tはfocus_hint条件のみ・N=4)と完全に交絡
している。fact供給量が原因なのか、題材の性質(box-score型は固有名詞・数値
密度が高い、3-2節既知)が原因なのか、本データだけでは分離できない
(**FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORTの§3-4と同じ限界を
踏襲**)。

### Part 1 判定(Opus提示基準への照合)

基準: 「成功=衝突率とoverlap_ratioが正相関(r>0.3程度)かつテーマ別使用
可能fact数が最終NG率と単調関係→仮説支持。失敗=相関≈0、またはanchor十分
分離なのにoverlap高→仮説棄却」。

**結果は基準に完全には当てはまらない、部分的・条件付きの支持**:
- anchor衝突数とP1-P2語彙overlapの相関はr=0.46(>0.3)で基準を満たすが、
  この語彙overlap指標(`cross_point_overlap`)自体がProduction retry判定に
  **使われていない**(OPEN-133 DEFERRED)ため、「NGの主因」という主張には
  直結しない。
- anchor衝突数と実際にNGを決めるGate指標(Point対Full Story overlap)との
  相関はr=0.19、最終NG二値との相関はr=0.10で、いずれも基準の「r>0.3程度」
  を満たさない。
- テーマ別使用可能fact数と最終NG率は単調関係(基準を満たす)だが、N=3
  テーマのみで交絡未分離(上記)。

総合: **「fact供給不足/割当衝突」仮説は、P1-P2のanchor衝突が語彙的な
類似を生む経路については支持されるが、その語彙的類似が実際のNG判定
(Point対Full Story overlap閾値0.40)を動かす経路については支持されない**。
テーマ別fact供給量とNG率の単調関係は仮説と整合するが、交絡未分離のため
確定的ではない。

---

## Part 2: 候補4(entity除外指標)の再校正

分母もentity除外した完全正規化版を、最終attemptの全文(Main Story本文+
Point One/Two本文)から再トークン化して計算(N=96=48 run×2 Point、
`点attempt`ではなく`run×point`単位、最終attemptなので全文完全)。

| 指標 | 値 |
|---|---|
| 元の閾値0.40でのflag率(raw、本タスクで再実装した同一ロジック) | 26.04%(25/96) |
| 分子・分母ともentity/数値除外した完全正規化版のflag率(閾値0.40のまま) | **11.46%(11/96)** |
| 現行flag率(26.04%)に一致するパーセンタイルで再校正した候補指標の閾値 | 0.3333 |
| その閾値での候補指標flag率 | 32.29%(タイの影響で目標値と完全一致せず) |
| raw比率 vs 候補比率のSpearman順位相関 | **r=0.9132** |
| パーセンタイル整合閾値での分類入替件数(True→False/False→True) | **10件(10.4%、10/96)** |

**事実**: 分母もentity除外した完全正規化版でも、flag率は26.0%→11.5%へ
低下する(§3-2の分子のみ調整版45.6%→13.3%と同方向、より厳密な計算でも
劇的低下が再現)。raw比率と候補比率の順位相関はr=0.91と高いが、完全な
順位不変ではなく、パーセンタイル整合閾値でも10.4%(10/96件)は分類が
入れ替わる。

**Entity辞書の非対称性(Opus指摘の直接検証)**: 本タスクで再構築した
entity辞書サイズはHanshin 45語・Theme2 9語・CAR-T 11語で、既報告の非対称性
(45/9/11)を再確認した。Point内容語に占めるLedger由来語(entity辞書語+
数値語)の割合は、Hanshin A2 17.54%・B1B 17.41%に対し、Theme2 A2 3.26%・
B1B 1.41%、CAR-T A2 2.82%・B1B 0.60%と、Hanshinだけが際立って高い
(**事実**)。これは、entity除外という同一操作がHanshinのPoint内容語の
約6分の1を除去するのに対し、他2テーマではほぼ影響しないことを意味し、
flag率の劇的低下がHanshin(box-score型)に偏って起きる直接的な原因である
(§3-2の解釈と整合、より厳密な計算で再確認)。

### Part 2 判定(Opus基準(ii)への照合)

基準:「順位ほぼ不変なら候補4は無情報(棄却)」。r=0.91は高い順位相関だが
「ほぼ不変」と言い切れるほど完全ではなく(10.4%が入替)、かつentity辞書の
非対称性(17.5% vs 1.4〜3.3%)がHanshin/box-score型に集中して効いている
ことも確認された。**総合判定: 候補4(entity除外overlap)はraw指標と
高く冗長(順位相関0.91)であり、大部分は無情報に近いが、完全な冗長では
なく、その変化は主にHanshin(box-score型)のentity辞書の大きさに起因する
テーマ依存アーティファクトである可能性が高い(棄却に近いが完全棄却では
ない、テーマ依存の再校正なしでの単純採用は不適切)**(事実と解釈を分離、
断定しない)。

---

## Part 3: 測定設計(連続量 vs 二値NG率)

Trial-08(N=6 run、baseline相当vs branch_diagnostic)の最終attemptについて:

| 指標 | NG群平均 | OK群平均 | 差 |
|---|---|---|---|
| cross_point_overlap(P1対P2、retry未使用の指標) | 0.1396 | 0.1070 | 0.033(小さい、閾値0.40から遠い) |
| **実際のGate指標(Point対Full Story overlapの最大値)** | **0.4046** | **0.3210** | **0.084(閾値0.40の直近で意味のある差)** |

全48 run・124 attemptのcross_point_overlap分布: initial平均0.139
(sd 0.070、n=48)、retry平均0.126(sd 0.068、n=76)—分布は大きく重なる。

**事実**: 二値NG率(Trial-08、N=6、Fisher p≈0.55で検出力不足、背景記載
の既存結果)に対し、実際にNG判定を左右するGate指標(Point対Full Story
overlap)の連続値ではNG群/OK群の平均差が0.084と、閾値0.40近傍で意味のある
方向の差を示す。一方、retry判定に使われないcross_point_overlapは差が
0.033に留まり閾値から遠く、指標として二値NG率よりも情報量は残るものの
Gate近傍の識別力は弱い。**連続量への切り替えは、特にGate指標本体
(Point対Full Story overlap)について検出力向上の余地を示す(N=6のみの
例示であり統計的有意性の主張ではない)**。

---

## データ欠落・限界

- **データ欠落: 0件**(48 run全てで`point_role_planning_*`・
  `point_overlap_article_retry_log.json`が揃っていた)。
- Theme2 Ledgerには`F-211`(central_claimの記述はF-206内容と一致するが
  番号が異なる)・`F-210`(Trial-12の自己訂正メモ内で「Fact一覧に存在
  しない番号」と明記)というID不整合が存在する(Ledger自体の既存データ
  品質問題、本タスクでは補正せずそのまま観測)。
- Part 1(e)「Full Story anchorとPoint anchorの重なり」は、Full Story
  自体に`evidence_anchor`のような機械可読フィールドが存在しないため、
  直接測定できなかった。代替として「Pointがrun内で一度でも参照した
  usable fact数/usable fact総数」を「fact利用率」として算出した(Part 1
  (d)参照、直接測定ではなく代替指標である旨を明記)。
- Part 1のfact供給比較はテーマ数N=3のみで、topic_structureおよび条件
  構成と交絡している(既存報告と同一の限界、未解消)。
- Part 2の完全正規化版はSpearman順位相関(0.91)・分類入替率(10.4%)の
  2種類の指標で評価したが、いずれも「無情報」と「有意な追加情報」の
  中間的な結果であり、二値の判定を単純化しすぎないよう本文で両方の数値を
  併記した。

## USER_DECISION_REQUIRED候補(実施はしない、設計案のみ)

1. **Ledger拡充Trial(A/B)**: Hanshin型(single_event_boxscore)題材で
   Ledgerのusable fact数を人為的に5→8程度へ増やせるか(現状スコープ外
   のFACT-06/07を条件付きでusable化する、または類似試合のbox-score型
   題材で追加の周辺事実を調査するなど)を小規模Trial(N=6程度)で検証し、
   fact利用率とNG率が実際に下がるかを見る設計。Part 1の交絡(N=3テーマ)
   を解消する直接的な検証になりうる。
2. **候補4のテーマ別再校正 or 不採用の判断**: entity除外overlapを
   Production Checkerへ組み込む場合、Hanshin型题材に偏った効果である
   ことを踏まえ、テーマ非依存の閾値のまま採用するかどうかはUSER_DECISION_
   REQUIRED(本タスクでは棄却寄りの結果のみ提示、採用可否の判断はしない)。
3. **cross_point_overlapのretry統合(OPEN-133)再検討**: Part 1の結果は
   「anchor衝突→P1-P2語彙類似」は起きるが「それ自体はNG判定に使われて
   いない」ことを再確認した。cross_point_overlapをretry判定へ統合すべきか
   はOPEN-133として既にUSER_DECISION_REQUIREDのまま(本タスクは追加の
   定量根拠を提供するのみで、統合の可否は判断しない)。
