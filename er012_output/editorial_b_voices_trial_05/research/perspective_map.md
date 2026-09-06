# Perspective Map — EDITORIAL-B-FAMILY-VOICES-TRIAL-05-PERSPECTIVE-CONTRACT-01

テーマ: 固定席復活 / free-address(POOL_TOPIC_MASTER.md No.7)。Research出典は
すべて `er012_output/editorial_b_voices_trial_04/research/` の既存資産
(raw_facts_research_stakeholder.json、raw_facts_verification_stakeholder.json、
Trial-04 `perspective_candidates.json`)。新規Perplexity呼び出しは行っていない。

このファイルは、記事本文の執筆前に行うPerspective選定の作業記録(手作業
curation)であり、Writerへ直接渡すものではない。Writerへ渡す最終的なVoice
Cardは `er012_editorial_b_voices_trial_05.py` の
`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK` 内に埋め込まれているものが正本であり、
以下は同内容の作業用ドキュメントである。

## 候補一覧(Trial-04 `perspective_candidates.json` の再整理 + Diversity Check)

各候補について、想像で埋めず、根拠(fact_id)が無い項目は「(根拠なし)」と
明記する。

### 候補A: frequent_office_employee_wants_a_seat_of_their_own
- Who: 週の大半をオフィスで過ごす社員(実名ではなく、REAL VOICE #05の
  パート社員3名の証言に代表される属性グループ)。
- What situation are they actually in?: 毎朝、まだ誰にも使われていない
  空いている机を探して座る(ホットデスキング環境)。[A-02/fact_003、
  A-05/fact_007]
- What do they want to protect?: 職場での所属感と、集中して働ける感覚。
  [A-01/fact_001、A-04/fact_006]
- What makes their day difficult?: 他人が使った後の机やキーボードへの
  衛生的な不安、私物・資料を置く場所が無いこと、チームがばらばらに座る
  落ち着かなさ。[A-02/fact_003、A-05/fact_007]
- What do they notice that another stakeholder may not?: 「固定席が無い
  日」の毎日の小さな不便さ・不安の積み重ね(組織全体のコストのような
  俯瞰的視点からは見えにくい、個人の生活実感)。
- What responsibility・constraint・interest do they carry?: (根拠なし。
  座席運用の意思決定権を持つ立場としてのEvidenceは見つかっていない。
  個人としての経験・必要を語る立場)。
- What concrete lived situation supports this perspective?: 毎朝オフィスに
  着いて空いている机を探して座る、資料や私物の置き場に困る。
  [A-05/fact_007]
- What research/evidence supports that this perspective actually exists?:
  A-01(fact_001, Gensler調査, CONFIRMED)、A-02(fact_003, LinkedIn News,
  CONFIRMED)、A-03(fact_004, Forbes, CONFIRMED)、A-04(fact_006, Forbes
  寄稿/Oseland, CONFIRMED)、A-05(fact_007, note REAL VOICE #05,
  CONFIRMED)、A-06(fact_009, ITmedia MONOist, CONFIRMED)。
- **選定結果: VOICE_A として採用**(Trial-04から継続)。

### 候補B: flexible_minded_employee_chooses_by_mood_or_task
- Who: その日の気分・業務・関わりたい人に応じて座る場所を選びたい社員。
- What situation are they actually in?: 在宅勤務等で既に自分の作業環境を
  持ち、フリーアドレスで様々な部署の人と交流している。[fact_014、
  A-05/fact_007の一部]
- What do they want to protect?: 自由に場所を選べること、その日の業務に
  応じて環境を変えられること。[fact_012]
- What makes their day difficult?: 同じ場所・同じ人間関係に固定される
  ことによる息苦しさ。[fact_008]
- What do they notice that another stakeholder may not?: 「集中ゾーン」
  「協働ゾーン」のような、思考モードに応じた場所の使い分けの価値。
  [fact_012]
- What responsibility・constraint・interest do they carry?: (根拠なし。
  候補Aと同様、個人としての経験・希望を語る立場)。
- What concrete lived situation supports this perspective?: フリーアドレス
  で違う部署の人と話す機会が増えた経験。[A-05/fact_007]
- What research/evidence supports that this perspective actually exists?:
  fact_012(Carr Workplaces, 12リーダー, CONFIRMED)、fact_008(TOKYO MX+,
  PARTIALLY_CONFIRMED)、fact_014(CNET Japan, CONFIRMED)、A-05/fact_007
  (note REAL VOICE #05, CONFIRMED)。
- **Diversity Check結果: 不採用**(下記「Perspective Diversity Check」
  参照。候補Aとの違いが、個人の心理的な好み[一貫性・所属感 vs 自由・
  変化]という同じ軸の中の対称的なバリエーションに近く、責任・制約・
  リスクの種類が異なるとは言えないと判定した)。

### 候補C: workplace_strategy_leader_balances_cost_and_belonging
- Who: 会社全体のオフィス空間の使い方・座席運用を決める職務を持つ、
  ワークプレイス戦略責任者(実名の発言例: Scotiabank Global Head of
  Real Estate & Corporate Services、Linda Foggie氏)。
- What situation are they actually in?: ハイブリッド勤務が広がった結果、
  フロアの席の多くが日によっては空いたままになっている。それでも出社
  する社員は職場に自分の居場所を感じたいと望んでいる。[B-01/fact_005、
  B-02/fact_011]
- What do they want to protect?: 会社全体としてのオフィスの持続可能性
  (コスト)と、そこで働く一人ひとりの所属感の両立。[B-01/fact_005]
- What makes their day difficult?: フレックス席を広げすぎれば所属感・
  チームの一体感が損なわれ、固定席を戻しすぎればコストが膨らむという
  板挟み。どちらへ寄せすぎても責任を問われる。[B-01/fact_005、
  B-02/fact_011]
- What do they notice that another stakeholder may not?: 個々の社員には
  見えない、フロア全体で「多くの席が空いている」という現実、および
  経営層へのコスト説明責任。[B-02/fact_011]
- What responsibility・constraint・interest do they carry?: 経営層に
  対するスペースコストの説明責任。出社頻度も働き方も異なる全社員の
  ニーズに応える座席運用を設計する責任。[B-01/fact_005、B-02/fact_011、
  B-03/fact_010]
- What concrete lived situation supports this perspective?: 「静かに、
  固定席が増えフレックス席が減る方向へのシフトが起きている」という
  Linda Foggie氏の発言に象徴される、フレックス席中心の運用を見直し
  つつある状況。[B-01/fact_005]
- What research/evidence supports that this perspective actually exists?:
  B-01(fact_005, Bisnow/Linda Foggie発言, CONFIRMED)、B-02(fact_011,
  Ohio Society/CBREデータ, CONFIRMED)、B-03(fact_010, Desking.app
  コンサルタント, CONFIRMED)。
- **選定結果: VOICE_B として採用**(Trial-04では「測定データ偏重で
  Discovery型構図に戻るリスク」を理由に不採用とされていたが、Trial-05
  ではSupporting evidenceをVoice Cardから隔離する新方式のため、この
  リスクはAnalytical Leakage Checkで直接検証する対象とする、という
  判断で採用した)。

### 候補D: manager_responsible_for_onboarding_mentoring
- Who: 新人教育・チームのメンタリングに責任を持つマネージャー。
- 根拠: Trial-03のVIS(単一ソース、具体的な担当者名を伴わない一般論)の
  みで、Trial-04の追加Researchでも独立した新規Evidenceは見つからなかった。
- **選定結果: 不採用(Evidence不足のため、想像で補わない)**。Trial-04
  から変更なし。

### 候補E: facilities_operator_ghost_desk_utilization
- Who: 使われない予約席(ghost desk)・稼働率データを管理するファシリティ/
  オフィス運営担当者。
- 根拠: fact_010、fact_011(候補Cと同じEvidence基盤)。
- **選定結果: 不採用(候補Cとほぼ同じEvidence基盤で独立した第三の軸に
  ならないため、候補Cへ統合)**。Trial-04から変更なし。

## Perspective Diversity Check(採用2件の判定根拠)

判定基準(タスク文書): 「Are these two people different only because
they prefer different outcomes?」がYESなら弱い。「Do they face
meaningfully different experiences, responsibilities, constraints,
interests, risks, or definitions of what matters?」を満たす、実在
Perspectiveの中で最も意味の異なる2者を選ぶ。

- **候補A vs 候補B(Trial-04の組み合わせ)**: 候補Aは「一貫性・所属感を
  求める」、候補Bは「自由・変化を求める」。どちらも個人としての心理的
  好みであり、座席運用への意思決定権・組織的責任は双方とも「根拠なし」
  だった。差は「好みの方向」であり、責任・制約・リスクの種類そのものは
  同一(どちらも「個人として何を感じるか」という同じ次元)。したがって
  「Are these two people different only because they prefer different
  outcomes?」への回答はYESに近いと判定し、Trial-05ではこの組み合わせを
  採用しない。
- **候補A vs 候補C(Trial-05で採用)**: 候補Aは、座席運用について意思決定
  権を持たない個人が、日々の感覚(所属感・集中)として経験していること。
  候補Cは、個人の好みではなく、経営層へのコスト説明責任、および出社
  頻度も働き方も異なる全社員のニーズに応える責任を、組織全体の立場から
  負っている。両者は次の点で構造的に異なる: (1)責任の有無(候補Cのみ
  組織的な説明責任を負う)、(2)リスクの種類(候補Aのリスクは自分自身の
  日々の快適さ、候補Cのリスクはコスト超過と組織的な信頼の毀損の両方)、
  (3)「良い座席運用」の定義そのもの(候補Aにとっては自分が毎日どう
  感じるか、候補Cにとっては全社的に持続可能かどうか)。したがって
  「Do they face meaningfully different experiences, responsibilities,
  constraints, interests, risks, or definitions of what matters?」への
  回答はYESと判定した。
- **候補A vs 候補D/E**: 候補D/Eは前述の通りEvidence不足・重複により不採用
  のため、Diversity Check以前の段階(Evidence充足性)で除外。

**結論: VOICE_A=候補A、VOICE_B=候補C を採用する。**「必ずManager」
「必ず別職種」という固定ルールでこの結論に至ったのではなく、実在する
Evidenceの範囲内で「最も意味の異なる2者」を判定した結果である。
