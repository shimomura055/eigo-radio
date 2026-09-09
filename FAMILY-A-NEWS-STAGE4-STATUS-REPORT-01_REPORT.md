# FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01 報告書

管理ID: `FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01`(読み取り専用の編纂タスク、
Sonnet委任、¥0)。既存のNews(Family A News、段階4=Point/Full Story
overlap対策段階)に関する分析・レビュー・監査の結果を、正式SSOT
(`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`)および既存
Reportから編纂した状況報告書である。本タスクでは新規のAPI呼び出し・
コード変更・SSOT編集・Git操作を一切行っていない。

---

## エグゼクティブサマリー

News(記事のPoint One/Two=本文中の2つの掘り下げ段落)の重複対策(段階4)は、
既存の改善候補4件のうち1件(entity除外指標)が「棄却に近いが完全棄却では
ない」、2件(診断feedback文言追加・Role Planningへの診断結果接続)は根拠
不十分で見送り寄り、残る1件(題材選定ガイダンス)は「Ledger fact供給量/
evidence allocation」という新論点(論点H)と統合すべきと整理された。論点H
仮説(fact供給が乏しいテーマほどNG率が高い)は相関分析で部分的支持(anchor
衝突→語彙類似は支持、実際のNG判定経路は非支持)に留まり、N=3テーマの交絡は
未解消である。threshold 0.40は「通常Point 0.15〜0.35」を前提とした暫定
校正のまま題材別に未再校正であることが確認されたが、Trial実測では緊急の
再校正を強く支持する結果は出ていない。News関連のユーザー判断待ち事項は
本報告で7項目(内容名称付き)を再提示し、うち4項目はCONSOLIDATION-62で
既提示、2項目(N-3/N-4)は別系統、1項目(OPEN-140)はデータ品質問題である。
「News方針UDR 1〜6」という番号表記はSSOT上で内容と1対1に紐づいた記述が
存在せず、件数が偶然一致するのみで確定できない(詳細は7節)。

---

## 1. 何を調べたか

- **Stage4棚卸し**(`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORT.md`、
  ¥0 offline再集計、既存48 run・248 Point-attempt観測): News Point品質を
  扱う既存14仕組みの構造整理、topic_structure(題材構造)別flag率の新規
  集計、改善候補4件の根拠・反証・リスク・cost・最小Trial設計の整理。
- **topic_structure別flag率**: 題材を`single_event_boxscore`(単一試合
  速報、Hanshin)・`survey_trend`(複数調査の統計比較、Theme2)・
  `mechanism_limitation`(単一研究発表、CAR-T)の3構造に分類し、初回/
  retry・レベル別のflag率・overlap平均・NG率を集計(同Report §3-1/§3-4)。
- **Opus L2レビュー**(Report非作成、`DECISION_LOG.md`
  `PM-CLOSEOUT-CONSOLIDATION-62`エントリへ要旨記録): Sonnet整理の根拠・
  優先順位付けを診断目的でレビュー。
- **Evidence Allocation監査**(`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-
  AUDIT-01_REPORT.md`、¥0、既存48 run・124 attempt観測の読み取り再集計):
  Opus指摘の論点H(Ledger fact供給量/evidence allocation)を、anchor
  (Verified Fact Ledgerの各Factを指すID)衝突数とP1-P2語彙重複・実際の
  Gate指標・最終NGとの相関、テーマ別使用可能fact数とNG率の関係、候補4
  (entity除外overlap)の完全正規化版、連続量評価の検出力の4パートで検証。
- **Trial-05〜09の系譜**: `FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`
  (G1配線漏れ発見)→`FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-
  TRIAL-06`(Hanshin、Focus Module+hint比較)→`FAMILY-A-NEWS-STAGE2-
  DIAGNOSTIC-BRANCH-TRIAL-08`(value単独NG時の診断条件分岐/閾値分布
  再集計)→`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`(CAR-T新テーマ、
  題材依存の切り分け)の各Reportを確認。

---

## 2. 何が分かったか

1. **既存仕組みの構造的事実**(REDESIGN-INVENTORY §1、コード確認済み):
   語彙重複はWriter Prompt原則→lexical Overlap QA→Diagnostic Full Retry
   診断sectionの3層で反復提示されるが実質は同一閾値(0.40)の繰り返し。
   `cross_point_overlap`(Point One対Point Twoの語彙重複、#7)は計算される
   がretry判定には未使用(OPEN-133、`DEFERRED`)。Point Role Planning(#3、
   Point生成前にrole/evidence_anchor等を計画する独立モジュール)はFocus
   Module(#4)を一切受け取らない独立経路。
2. **retry(記事全体の再生成)の責務**(同§1表E): 診断section・Value QA
   診断メモは前回の実テキストを固定して提示するが、Role Planningは
   `topic, verified_ledger_text`の2引数のみで初回と完全に同一入力から
   「盲目の再抽選」を行い、診断結果を一切見ない。Full Article自体は
   非決定的LLM出力として毎回作り直される(Point単位の局所編集ではない)。
3. **topic_structure別の顕著な差**(REDESIGN-INVENTORY §3-4、48 run):
   初回attempt flag率はいずれの構造でも50〜92%と高いが、最終NG率は
   single_event_boxscore 72.2%(n=36)、survey_trend 50.0%(n=8)、
   mechanism_limitation 0.0%(n=4)と大きく異なる。
4. **固有名詞・数値除外の劇的低下と目視の矛盾**(§3-2/§3-1): 分子から
   固有名詞・数値語を除くと全体flag率45.56%→13.31%(single_event_
   boxscoreは46.91%→7.73%)へ劇的に下がるが、目視では「固有名詞と意味
   重複が混在し分離できない」ことも確認され、劇的低下=すべて誤検知の
   是正と解釈するのは過大解釈と整理された。
5. **論点H(Ledger fact供給量/evidence allocation)の部分的支持**
   (EVIDENCE-ALLOCATION-AUDIT §Part1): anchor衝突数とP1-P2語彙overlap
   はr=0.4623(正相関、支持)だが、実際のGate指標(Point対Full Story
   overlap、閾値0.40)とはr=0.1852、最終NG二値とはr=0.0997といずれも
   弱い(非支持)。テーマ別使用可能fact数(5/8/14)とNG率(72.2%/50.0%/
   0.0%)は単調な逆関係だがN=3テーマで交絡未分離。
6. **候補4(entity除外overlap)の完全正規化版**(同§Part2): flag率
   26.04%→11.46%、raw比率との順位相関r=0.9132、分類入替10.4%(10/96件)。
   entity辞書サイズの非対称性(Hanshin 45語/Theme2 9語/CAR-T 11語)、
   Point内容語に占めるLedger由来語割合(Hanshin 17.5% vs Theme2 3.3%・
   CAR-T 2.8%)が確認され、テーマ依存artifactとして棄却寄りと判定。
7. **連続量評価の検出力**(同§Part3): Trial-08(N=6)で実際のGate指標
   (Point対Full Story overlap)はNG群平均0.405・OK群平均0.321(差0.084、
   閾値0.40近傍で意味のある差)、対してcross_point_overlapの差は0.033に
   留まった(統計的有意性の主張ではない)。
8. **新規データ品質問題の発見**: Theme2 Verified Fact Ledgerの`F-210`
   (存在しない番号と自己訂正メモに明記)・`F-211`(central_claimがF-206と
   内容一致するが番号相違)を新規発見、`OPEN-140`として起票(未補正)。

---

## 3. 何が棄却されたか(理由付き)

- **§3-2の根拠指標そのもの(閾値未再校正のartifact)**: Opus L2レビュー
  (`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-62`)は、entity除外での
  flag率45.6%→13.3%という結果自体が、序数除去漏れ・entity辞書サイズの
  非対称性(45/9/11語)に起因する題材別ミスキャリブレーションの直接証拠
  であり、「候補案の根拠」として単純採用すべきでないと指摘した。
- **候補4(entity除外overlap)**: `EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`
  Part2で、完全正規化版でも順位相関r=0.91・分類入替10.4%となり、
  「テーマ依存アーティファクトである可能性が高い(棄却に近いが完全棄却
  ではない)」と判定(§Part2「判定」節)。
- **条件分岐によるoverlap診断構築の変更(value単独NG時にoverlap診断
  sectionを構築しない案、UDR候補(i))**: `FAMILY-A-NEWS-STAGE2-
  DIAGNOSTIC-BRANCH-TRIAL-08` Part A(N=6)で**Gate1=REJECTED**。NG率
  50%→83.3%、平均attempt数1.50→1.83と悪化方向、value単独NG→次attempt
  新規lexical flag率も条件分岐後5/5(100%)で連鎖は解消せず、新規Fact
  Checker FAIL 1件も発生した。
- **閾値・分母の緊急再校正(UDR候補(ii))**: 同Trial-08 Part B(¥0、既存
  240件再集計)で、固定分母案(D_fixed=30)は現行より厳しい方向(flag率
  +5〜6pt)へ動き長いPointに不利な逆方向の交絡を生むことを確認、
  「閾値・分母の緊急再校正を数値は強く支持しない」と結論(採否は
  ユーザー判断のまま、完全な棄却ではなく非推奨)。
- **Role再計画への診断結果受け渡し(UDR候補(iv)、候補2)**: 段階1
  (`FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md`)により
  「効果不明」のまま2026-09-09ユーザー決定(N-3=(b))で保留。REDESIGN-
  INVENTORY §5でも「Discovery Layer3 Trial-07のRole収束問題の真因が
  未解明のままであり、原因調査を先に行うべきで本Trialの直後には推奨
  しない」と位置づけられ、優先度は下がっている(完全な棄却ではない)。

---

## 4. 何が有力候補として残ったか

- **論点H(Ledger fact供給量/evidence allocation)を主軸に据えること**:
  Opus L2レビューが「最大の見落とし」と指摘し、監査で部分的支持を得た
  ため、4件のUDR候補(5節参照)の筆頭として提示中(未承認)。
- **候補4(Ledger由来語ベースのnecessary factual overlap除外指標)**:
  「棄却に近いが完全棄却ではない」段階に留まり、閾値運用ではなく**観測
  指標としてのみ**追加する案は選択肢として残っている(REDESIGN-INVENTORY
  §5候補4、§7推奨の起点)。
- **候補1(診断feedbackへの「トレードオフ回避」明示指示)・候補3
  (topic_structureを考慮したNews題材選定ガイダンス)**: いずれも
  「棄却」ではなく「候補4の結果を踏まえて次に選ぶ」という条件付き保留
  (REDESIGN-INVENTORY §7)。候補3は論点Hとの統合(「Ledger拡充」への
  読み替え)がCONSOLIDATION-62のUDRとして提示中。
- **評価量の連続量化(二値NG率→overlap_ratio等の連続値)**: Trial-08
  Part3の検出力向上の示唆を受け、Opus・監査の両方から提案されており、
  4件のUDR候補の1つとして残っている。

---

## 5. 論点H仮説の根拠(支持する根拠・支持しない根拠の両方)

**論点Hとは**: Opus L2レビューが提起した仮説で、「Verified Fact Ledger
(検証済み事実台帳)が供給するusable fact(利用可能な事実)の数・割当の
余裕度が、Point One/TwoとFull Storyの語彙重複NGの主因ではないか」という
もの(Hanshin実質usable fact数5 vs CAR-T 14という大きな差が出発点)。

### 支持する根拠

- anchor(Point Role PlanningのFACT-ID参照)衝突数とP1-P2語彙重複
  (cross_point_overlap系)の相関 **r=0.4623**(基準r>0.3を達成、
  `EVIDENCE-ALLOCATION-AUDIT-01` Part1(a)(c))。
- テーマ別使用可能fact数(Hanshin5/Theme2 8/CAR-T 14)とNG率(72.2%/
  50.0%/0.0%)が**単調な逆関係**(同Part1(d))。
- fact利用率(Point Role Planningが実際に参照したfact数/使用可能fact数)
  も95.6%/67.2%/37.5%と単調に低下し、Hanshinでは5個中ほぼ全て(4.78個)
  が毎回Pointに割り当てられる「逼迫」状態にある(同Part1(d))。
- initial→retryでanchorの76〜79%が新規組み合わせへ変わる(「盲目の
  再抽選」と整合、同Part1(b))。

### 支持しない根拠

- anchor衝突数と**実際にretry判定を左右するGate指標**(Point対Full
  Story overlap、閾値0.40)との相関は **r=0.1852**、最終NG二値とは
  **r=0.0997** で、いずれも基準(r>0.3程度)未達(同Part1(a)(c))。
  すなわち「anchor衝突→P1-P2語彙的類似」は支持されるが、「その語彙的
  類似が実際にNG判定を動かす」経路は支持されない。
- テーマ別fact供給量比較は**N=3テーマのみ**で、topic_structure
  (single_event_boxscore/survey_trend/mechanism_limitation)・条件構成
  (Hanshin N=36・6条件、Theme2 N=8・2条件、CAR-T N=4・focus_hint条件
  限定)と完全に交絡しており、fact供給量が原因か題材の性質(box-score型
  は固有名詞・数値密度が高い)が原因かは本データだけでは分離できない
  (同Part1(d)「交絡の明記」節)。
- N=3という極小標本のため統計的に確定的な結論を出せる段階にない(同上)。

**総合**: `EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`自身が「**部分的支持**」
と明記しており、支持・非支持のいずれかへ断定する材料はまだ揃っていない。

---

## 6. threshold 0.40 / Overlap Checker / retry / Point Role Planningの評価

### (a) threshold 0.40(Point対Full Storyのlexical overlap coefficientの
閾値、`er008_point_overlap_qa_18.py`)

**評価: 判断材料不足(緊急の再校正を強く支持する結果はないが、妥当性を
積極的に裏付ける結果もない)**。根拠: Opus L2レビューは、閾値0.40が
「通常Point 0.15〜0.35」を前提とした暫定校正のままであり、`_STOPWORDS`
がone/two/threeのみに限定されるなど題材別ミスキャリブレーションの直接
証拠があると指摘した(`DECISION_LOG.md` CONSOLIDATION-62)。一方、
Trial-08 Part Bの¥0再集計(既存240件)では、閾値0.40が観測分布の
**57.9パーセンタイル**に位置し境界帯(±1語、[0.363,0.437])内が
**25.0%(60/240件)**を占めるものの、Focus系施策の改善効果自体は境界
効果への依存度が10〜28%に留まり「閾値アーティファクトでは説明できない」
と整理された(OPEN-134行)。固定分母案の試算はむしろ悪化方向(3節参照)。

### (b) Overlap Checker(lexical overlap coefficient、Point対Full Story)

**評価: 要見直しの兆候はあるが、代替案は未確立**。box-score型
(single_event_boxscore)で固有名詞・数値と意味重複が指標上混在し、
目視でも分離できないことが確認された(2節4/REDESIGN-INVENTORY §3-1)。
semantic similarity(embedding)は代替候補として比較表に挙がったが
API課金必須のため¥0検証は不可、Production Checker置換は大規模変更と
位置づけられている(同§3-3)。

### (c) retry(Loop Budget・retry責務競合)

**評価: Loop Budget=2自体は本タスク範囲では変更提案されていない
(判断材料不足)。retry責務競合は構造的欠陥として事実確認済み(要見直し)**。
Role Planning(#3)が診断sectionより後ろに配置され、retry時も
`topic, verified_ledger_text`の2引数のみで初回と同一の「盲目の再抽選」
を行うことはコード・データ両面で確認された(2節2/Opusレビュー)。
Value QA×lexical Overlapが交互に介入する「もぐらたたき」現象も
Reconciliation Gate・段階1再集計で実証済み(全4Trial合計で真のswap
7件)。ただしLoop Budget=2という数値自体の妥当性再検討は、REDESIGN-
INVENTORY §6論点4で「Opus観点として提示のみ、本タスクでは変更を提案
しない」に留まり、正式な観測(A-UDR-22、Production正式path 20 run
観測)も2026-09-09時点で**20 run中2 runしか消化しておらず**、Production
実運用での判断材料は乏しい(OPEN-134行)。

### (d) Point Role Planning

**評価: 診断結果非依存の「盲目の再抽選」構造が要見直し候補だが、接続案
自体の効果は未検証**。Opus L2レビューは「retryで固定すべきはfact割当、
変えるべきは表現角度」という構造改善案を提示したが、REDESIGN-INVENTORY
候補2(Role Planningへの診断結果接続)は「Discovery Layer3 Trial-07の
Role収束問題の真因が未解明のままであり、原因調査を先に行うべき」として
優先度は下げられている(3節参照)。

### ユーザーの5つの問いへの回答

1. **Point切り口をより明確にできないか**: 候補3(topic_structureを
   考慮したNews題材選定ガイダンス)・候補2(Role Planning診断接続)が
   関連候補だが、いずれも単独では効果未実証。候補3は論点Hとの統合
   (「Ledger拡充」への読み替え)がUDRとして提示中。
2. **Overlap Checkerが厳しすぎないか**: 境界帯(±1語)に25%の観測が
   集中するという事実はあるが、Focus系改善効果は境界効果に大きく依存
   しないため、「厳しすぎることが主因」と断定する根拠は現時点で弱い
   (Trial-08 Part B)。
3. **threshold 0.40は本当に妥当か**: 暫定校正のまま題材別未再校正
   (Opus指摘)という構造的な弱点はあるが、Trial実測(固定分母案)は
   再校正がむしろ悪化方向になりうることを示しており、「妥当ではない」
   とも「妥当である」とも断定できない(判断材料不足)。
4. **指標そのものやretry構想を変えられないか**: 連続量評価
   (overlap_ratio)は検出力向上の示唆があり有力候補。Role Planningへの
   診断結果接続は構造的な問題提起はあるが効果未検証で優先度は下位。
5. **News構造自体を見直した方がよくないか**: 候補3(題材選定ガイダンス)・
   論点H(Ledger fact供給量)がこの問いに最も直結する候補だが、
   いずれもN=3テーマの交絡・N=4以下の小標本のため、構造見直しを正式
   決定できる段階には至っていない。

---

## 7. News方針で未決の事項(全件、内容名称付き)

**「News方針UDR 1〜6」という番号表記について**: `docs/pm/ACTIVE_TASK.md`
(`UDR-deferred`欄)に「News方針UDR 1〜6」という束ね表記が1箇所存在する
のみで、`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`のいずれにも
「UDR-1」〜「UDR-6」という番号とNews関連決定事項を1対1で紐づけた記述は
見つからなかった(Grep確認、`DECISION_LOG.md`内の`A-UDR-21`
`A-UDR-22`等は既存の別命名体系[Household/News段階1系の個別UDR番号]であり
「News方針UDR 1〜6」の番号とは異なる)。**SSOT上で番号と内容の対応関係は
内容特定不可**。以下、CONSOLIDATION-62で提示中の4点に、系統の異なる
News/Family A Completion Program関連の未決事項を合わせて全件を名称付きで
再提示する(件数が6件になるのは後述の通り偶然の一致の可能性が高く、
番号との対応を断定しない):

1. **UDR候補a「主軸を候補1/2(診断feedback文言追加/Role Planning診断
   接続)から論点H(Ledger fact供給量・evidence allocation)へ移すか」**
   (`DECISION_LOG.md` CONSOLIDATION-62、OPEN-135行)。
2. **UDR候補b「候補3(topic_structureを考慮したNews題材選定ガイダンス)
   を『Ledger拡充』へ読み替えるか」**(同上)。
3. **UDR候補c「候補2(Role Planning診断接続)を見送り可能か」**(同上)。
4. **UDR候補d「Trial評価量を二値NG率から連続量(overlap_ratio等)へ
   切り替えることを承認するか」**(同上)。
5. **N-3「News Focus Module + Point Role hintのProduction採用可否」**
   (OPEN-135行、`FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-
   TRIAL-06_REPORT.md`。判断に必要な項目6件[Focus Module/hint文言確定、
   `major_daily_news`の`EDITORIAL_TYPE_MODULE_BLOCKS`登録要否、hint接続の
   共有Writer配線範囲、baseline悪化とOPEN-134観測の関係、N数追加要否等]
   が未実装のまま提示中)。
6. **N-4「CAR-T新テーマTrial(`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-
   TRIAL-09`)のB1B `full_story_part1`がHUMAN_REVIEW_REQUIREDへ遷移した
   ままであり、再生成にはユーザー承認が必要」**(OPEN-135行、
   Assemblyは`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で正常STOP、player
   未生成)。
7. **OPEN-133「cross_point_overlapのstill_flagged(retry判定)統合を
   実装するか、または現状のDEFERRED方針を維持するか」**(2026-09-09、
   ユーザー正式決定A-UDR-21により(b)採用済み=当面実装しないが、統合の
   将来的な要否判断自体は本Open Itemを維持したまま別途行うとされている)。
8. **OPEN-134「Point Overlap NG観測(A-UDR-22 Exit条件)の継続、正式
   Production run 20件中2件消化、主要因判定・全体NG率の再対策閾値の
   到達待ち」**(OPEN-134行)。
9. **OPEN-137「A2 Japanese Title(日本語タイトル)供給の自動化要否」**
   (News/Trend Synthesis双方に影響する既知gap、現状は英語タイトルの
   直訳を人手供給。News Trial-09[N-4]・Household一本化候補でも同一gapの
   再発を確認、DEFERRED)。
10. **OPEN-140「Theme2 Verified Fact LedgerのID不整合(`F-210`/`F-211`)を
    是正するか、影響なしを確認した上で現状維持するか」**(2026-09-09
    起票、`USER_DECISION_REQUIRED`、是正要否未定)。
11. **OPEN-139「遡及QA方針」の未決事項4点**(2026-08-17以前承認の
    レガシーepisodeへの現行Audio Validation Gate遡及適用方針、News
    Completion Program量産時に発生頻度が増す可能性があるため間接的に
    News方針とも関連):
    - (1) 遡及QAの範囲(全episode対象か個別問題確定分のみか)未定。
    - (2) 修正方式(`HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02`
      方式の恒久標準化か個別都度承認継続か)未定。
    - (3) trigger(都度判断か量産段階でまとめて判断か)未定。
    - (4) 判断が必要な理由(「遡及修正不要」運用方針とFact Safety最上位
      原則の整合が未整理)。

---

## 8. ユーザー判断が必要な項目(blocking/deferred区分、推奨案付き)

| # | 項目 | 区分 | Fable/Sonnet側の推奨案(参考、決定権はユーザー) | 理由(短) |
|---|---|---|---|---|
| 1 | UDR候補a(主軸を論点Hへ) | **Deferred**(現行Production動作に影響しない、Trial設計判断) | 論点Hを主軸候補の1つとして次Trial(9節候補A)で検証する方向を支持 | 部分的支持の段階でありN=3交絡未解消、追加Trialでの検証が必要 |
| 2 | UDR候補b(候補3→Ledger拡充) | **Deferred** | 読み替えを支持(候補3単独[題材選定]よりLedger拡充の方が検証可能性が高い) | 候補3は編集方針判断を伴い単独では検証しにくい、論点Hとの統合で検証設計が明確になる |
| 3 | UDR候補c(候補2見送り) | **Deferred** | 見送りを支持(Discovery Role収束の真因調査を先行すべき) | REDESIGN-INVENTORY §5・§7が明記する既存の申し送り事項 |
| 4 | UDR候補d(連続量評価) | **Deferred** | 承認を支持(検出力向上の示唆があり¥0で試算可能) | Trial-08 Part3で差0.084 vs 0.033の具体的な検出力差を確認済み |
| 5 | N-3(News Focus Module Production採用) | **Blocking**(Production配線を伴う決定のため) | 現時点では非推奨(未実装6項目・NG率50%が高水準) | Trial-06自身がGate1=USER_DECISION_REQUIREDと判定、N数不足 |
| 6 | N-4(full_story_part1再生成) | **Blocking**(既存Human Review Lock・Audio Validation Gateが正常STOP中) | 再生成する場合は既存の承認済み再生成経路(1回)を使う方針を推奨 | Gateは意図通り機能しており安全実害はない、再生成はユーザー承認必須 |
| 7 | OPEN-133(cross_point_overlap統合) | **Deferred**(SSOT記載は既に訂正済み) | 現状維持(DEFERRED)を推奨、論点H検証の結果を待ってから再検討 | Part1でNG判定経路への直接的関与は非支持 |
| 8 | OPEN-134(観測継続) | **Deferred**(Non-blocking) | 観測継続(20 run到達まで) | 正式Exit条件が未到達(2/20) |
| 9 | OPEN-137(A2日本語タイトル自動化) | **Deferred**(Non-blocking、現行は人手供給で動作) | 量産段階前に自動化要否を判断することを推奨 | News Completion Program量産で発生頻度が増す可能性 |
| 10 | OPEN-140(Theme2 Ledger ID不整合) | **Deferred**(Non-blocking、実害未確認) | 是正を推奨(データ品質問題は早期に是正する方が量産前に望ましい) | 既存成果物への影響は限定的と見られるが未検証 |
| 11 | OPEN-139(遡及QA方針4点) | **Deferred**(Non-blocking) | Family A Completion Program量産段階に近づいた時点でまとめて判断する案(trigger(b))を推奨 | 都度判断は運用負荷が増す可能性がある一方、現時点で緊急性は低い |

---

## 9. 次Trial候補

### 候補A: Ledger拡充Trial A/B(Hanshin型、N=6)

- **目的**: 論点H(Ledger fact供給量/evidence allocation)の因果関係を、
  N=3テーマの交絡を解消する形で直接検証する(`EVIDENCE-ALLOCATION-
  AUDIT-01_REPORT.md` §USER_DECISION_REQUIRED候補1)。
- **設計概要**: single_event_boxscore型(Hanshin)題材でVerified Fact
  Ledgerのusable fact数を人為的に5→8程度へ増やす(現状スコープ外の
  FACT-06/07を条件付きでusable化する、または類似試合のbox-score型
  題材で追加の周辺事実を調査する)。fact利用率とNG率が実際に下がるかを
  N=6程度で検証。
- **N**: 6(A2/B1B構成は既存Trial-06/09と同型を想定)。
- **見込み費用**: 明記されている類似規模Trial実績(Trial-06 ¥85.6、
  Trial-09の候補3検証見積り¥60〜80)から**概算¥60〜150程度**。
- **期待される判断材料**: 論点H仮説の因果的な検証(fact供給を増やすと
  実際にNG率が下がるか)、UDR候補a(主軸を論点Hへ移すか)の判断材料。

### 候補B: 候補4(entity除外overlap)のテーマ別再校正 or 不採用の判断

- **目的**: 「棄却に近いが完全棄却ではない」段階の候補4を、観測指標
  としてのみ定常記録するか、不採用のまま終了するかを確定する
  (REDESIGN-INVENTORY §8 UDR候補5)。
- **設計概要**: ¥0(既存Ledger jsonの読み取りのみ)、Trial実行は不要。
  ユーザー判断のみで完結可能。
- **N**: 該当なし(判断のみ)。
- **見込み費用**: ¥0。
- **期待される判断材料**: 候補4を今後のObservationログ(OPEN-134の
  `point_overlap_observation_log.jsonl`と同様の位置づけ)へ組み込むか
  否かの確定。

### 候補C: 評価量の連続量化への切替Trial

- **目的**: Gate指標(Point対Full Story overlap)を二値NG率ではなく
  連続量(overlap_ratio)で評価する運用へ切り替えることの妥当性を、
  より大きなNで確認する(Trial-08 Part3の示唆[差0.084、N=6のみ]の
  再現性確認)。
- **設計概要**: 既存Trial harness(Trial-06/08と同型)を用い、NG群/OK群
  のoverlap_ratio分布を再測定、統計的検出力(効果量・分散)を確認。
  Production Checkerの判定ロジック自体は変更しない設計とすることで
  STOP該当性を回避できる可能性が高い(観測指標としての切替)。
- **N**: 既存Trial-06(N=14)・Trial-08(N=6)データの再利用+追加N=6〜10
  程度を推奨。
- **見込み費用**: 追加実行が必要な場合¥60〜100程度(既存Trial規模から
  類推)、既存データのみの再分析なら¥0。
- **期待される判断材料**: UDR候補d(連続量化承認)の判断材料、閾値0.40
  近傍での検出力の定量的な裏付け。

### 候補D: Role Planning-Discovery Role収束の真因調査(候補2の前提調査)

- **目的**: REDESIGN-INVENTORY §5が「候補2(Role Planning診断接続)の
  前に優先すべき」と位置づけたDiscovery Layer3 Trial-07のRole収束問題
  (mechanism/myth_correctionへの100%収束)の真因調査。News側の候補2
  検討の前提材料にもなる。
- **設計概要**: ¥0机上調査(既存Household Ledgerでの新規N=10抽選による
  Role分布再現性確認は段階1で実施済み[56%がbroader_dimension/other]、
  Trial-07実績[6/6がmechanism/myth_correctionのみ]との乖離の原因調査)。
- **N**: 該当なし(¥0机上調査、追加runtime evidenceが必要な場合は別途)。
- **見込み費用**: ¥0(机上)〜追加runtime evidenceが必要な場合は¥40〜60
  程度。
- **期待される判断材料**: UDR候補c(候補2見送り)の妥当性の再確認、
  候補2着手の可否判断材料。

---

## 10. QCD(Quality / Cost / Delivery)

### Quality(現行News品質指標の到達点と残課題)

- **到達点**: topic_structure別の最終NG率(single_event_boxscore 72.2%・
  survey_trend 50.0%・mechanism_limitation 0.0%、`EVIDENCE-ALLOCATION-
  AUDIT-01` Part1(d))、閾値0.40は観測分布の57.9パーセンタイルに位置
  (Trial-08 Part B)、Loop Budget=2・cross_point_overlap未統合・Role
  Planning盲目の再抽選という構造的事実はコードで確認済み。
- **残課題**: (1)論点Hはまだ部分的支持のみでN=3の交絡未解消、
  (2)Point Role Planningのretry診断非依存という構造改善の効果は未検証、
  (3)box-score型(Hanshin)のNG率72.2%は依然高水準、(4)News Focus Module
  Production採用(N-3)は未達成のまま保留、(5)Theme2 LedgerのID不整合
  (OPEN-140)が既存データの信頼性に未評価のリスクを残す。

### Cost(既実施Trialの累計費用と次Trial見込み)

News段階2〜4系(Trial-06以降、¥単位で確定値が記録されている範囲)の
累計実測費用: Trial-06(`FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-
COMPARISON-TRIAL-06`)¥85.6 + Trial-08 Part A ¥42.5(Part Bは¥0) +
Trial-09(`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`)¥240.49
(うち規律違反による無駄約¥2.56を含む) + Stage4 Redesign Inventory
¥0 + Evidence Allocation Audit ¥0 = **合計¥368.59**
(`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`各行より、出典明記)。これより前の
Trial-04(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04`)・
Trial-05(`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`)はルーティング制度
導入前・実測課金記録の欠落(cl.install()未設置)のためログにトークン数
のみ記録され¥単位の確定値は見当たらなかった(**SSOT上で数値確定不可**)。
次Trial見込みは9節の通り、候補A(¥60〜150)・候補B(¥0)・候補C(¥0〜100)・
候補D(¥0〜60)。

### Delivery(次の1手までの所要と依存関係)

次の1手は**ユーザーによるUDR候補a〜d(7節1〜4)の判断**であり、これが
確定しない限り新規Trial(9節候補A〜D)は着手できない(PM運用Gate上の
STOP原則、Production Prompt/QA変更を伴わない観測系Trialであっても
Fable/ユーザー提示中のUDRの裁定が先行する運用のため)。判断が出れば、
候補B(¥0、即日)→候補A/C/D(¥0〜150、既存Trial harnessの再利用のため
実行自体は1セッション程度)の順で著手可能と見込まれる。N-3
(News Focus Module Production採用)・N-4(B1B再生成)は論点Hの検証結果と
独立した別系統の判断であり、いずれもユーザー判断待ちのまま並行して
進めることが可能。

---

## 未提示のUSER_DECISION_REQUIREDが残っていないかのチェックリスト

SSOT上でNews関連(`OPEN-133`/`OPEN-134`/`OPEN-135`/`OPEN-137`/`OPEN-140`、
および`OPEN-139`[News量産と関連]、CONSOLIDATION-44/55/58/60/61/62の
News/Discovery Trial系エントリ)を全件Grepし、`USER_DECISION_REQUIRED`
または「ユーザー判断待ち」「起票のみ」と記された項目が7節に含まれて
いるかを照合した。

- [x] OPEN-133(cross_point_overlap統合可否) → 7節7
- [x] OPEN-134(Point Overlap NG観測Exit条件、A-UDR-22進捗2/20) → 7節8
- [x] OPEN-135 CONSOLIDATION-62提示中のUDR4点(主軸移行/候補3読み替え/
      候補2見送り/連続量化) → 7節1〜4
- [x] OPEN-135内 N-3(News Focus Module Production採用) → 7節5
- [x] OPEN-135内 N-4(full_story_part1再生成) → 7節6
- [x] OPEN-137(A2日本語タイトル自動化要否) → 7節9
- [x] OPEN-140(Theme2 Ledger ID不整合是正要否) → 7節10
- [x] OPEN-139(遡及QA方針、News量産と関連する持ち越し事項) → 7節11
- [x] `EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`末尾のUSER_DECISION_
      REQUIRED候補3件(Ledger拡充Trial/候補4再校正・不採用/OPEN-133
      再検討) → 9節候補A・候補B、7節7と重複整理済み
- [x] REDESIGN-INVENTORY §8のUDR候補5件(候補1〜4のいずれを次Trial対象
      とするか/OPEN-133再検討/候補3の編集方針判断/Loop Budget=2再検討
      要否/候補4のObservation定常化) → 7節1〜4・8節・9節へ反映
      (Loop Budget=2再検討要否は6節(c)で「判断材料不足」として明記)

**本チェックリストで新たに漏れは確認されなかった。** ただし、「News方針
UDR 1〜6」という番号表記自体はSSOT上で内容と1対1に対応した記述が
見つからなかったため、7節冒頭に明記した通り「内容特定不可」として
扱っている(件数が6件になったのは、CONSOLIDATION-62の4点+N-3+N-4を
数えた場合に一致するという確認であり、番号1〜6との対応そのものを
SSOTが保証しているわけではない)。

---

## 参照した主要ファイル(出典)

- `OPEN_ITEMS.md`(OPEN-133/134/135/136[参考、News以外]/137/138/139/140行)
- `DECISION_LOG.md`(`PM-CLOSEOUT-CONSOLIDATION-44/55/58/60/61/62`エントリ)
- `CURRENT_SPEC.md`(Point Overlap Checker/threshold 0.40/Point Role
  Planning/Diagnostic Full Retry/Loop Budget関連記述)
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(News関連Trial費用行)
- `docs/pm/ACTIVE_TASK.md`(「News方針UDR 1〜6」束ね表記)
- `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORT.md`
- `FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`
- `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md`
- `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`
- `FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06_REPORT.md`
