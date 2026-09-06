# EDITORIAL-B-FAMILY-VOICES-TRIAL-04 報告書

管理ID: **EDITORIAL-B-FAMILY-VOICES-TRIAL-04**
Lane: **Lane B / Voices-Perspective**(Lane Aとは独立)
種別: **再Trial(ユーザー承認済み、2026-09-06)**。到達Status: 本Reportで
提案するのは**VALIDATED**(範囲: Voice数2・B1・Article-only・Focus Module
修正の効果検証)。Production採用・配線へは進んでいない。TTS未実行。

前提: [EDITORIAL-B-FAMILY-VOICES-TRIAL-03_REPORT.md](EDITORIAL-B-FAMILY-VOICES-TRIAL-03_REPORT.md)
に対するユーザー評価(Voice選びがDiscovery寄りのEvidence/分析軸比較になって
いた、体裁が硬い、構成が基本形から外れた)を踏まえ、同じテーマ「固定席復活」
(POOL_TOPIC_MASTER.md No.7)で、Focus Module修正によりVoicesらしい記事へ
改善できるかを検証した。

新規Trial script: [er012_editorial_b_voices_trial_04.py](er012_editorial_b_voices_trial_04.py)
(Trial-03のscriptをコピーして修正、Trial-03のscript自体は無変更)
出力: `er012_output/editorial_b_voices_trial_04/`

---

## 1. 前回からの変更点

### 1-1. Focus Module Block差分(原文)

`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`の全文diff(旧: Trial-03、新:
Trial-04)。抜粋ではなく全差分。

```diff
--- Trial-03 (old)
+++ Trial-04 (new)
@@ -1,59 +1,82 @@
-【B Family Voices/Perspective Focus Module(今回のTrialで追加する、\
-この記事タイプ専用の骨格再定義。EDITORIAL-B-FAMILY-VOICES-TRIAL-03、Production未採用)】
+【B Family Voices/Perspective Focus Module(今回のTrialで修正する、\
+この記事タイプ専用の骨格再定義。EDITORIAL-B-FAMILY-VOICES-TRIAL-04、Production未採用)】
 この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
 一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
 奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。以下は、上記の
 一般的な役割定義を置き換えるのではなく、この記事に限り、それぞれのslotが何を担うかを
 より具体的に上書きする指示です。今回の記事では、以下の役割定義を優先してください。
 
+【最も重要な前提: Voiceとは何か】
+Voiceとは、データセットでも、トレンドでも、主張(議論の一方の側)でもありません。Voiceとは、
+Researchで確認された、実在するstakeholderの視点そのものです。それぞれのVoiceは、その人物・
+その立場の人が、実際に何を経験し(experience)、何を大切にし(value)、何を必要とし(need)、
+何を心配し(worry about)、何に責任を持ち(are responsible for)、何を得て何を失うのか
+(gain or lose)から書いてください。「〜という調査結果がある」「〜というデータが示す」を
+主語にした説明ではなく、「その人にとって、これはどういう毎日なのか」を主語にして書いて
+ください。Evidence(発言・調査・事例)はVoiceを裏付けるために使うのであって、Evidence自体が
+Voiceになってはいけません。数字や調査結果を並べるだけの記述にならないよう、常に「この人は
+何を感じているか」に立ち返ってください。
+
+読み手がVoiceのセクションを読んだときに、「この立場なら、たしかにそう感じるだろうな」と
+思えることが最も重要なゴールです。反論のための藁人形にしないでください。
+
+【トーン(重要)】
+この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィング・リサーチサマリー
+のような読み味にしないでください。Light・conversational・human-centeredに、気軽に読める
+文章にしてください。専門用語や硬い分析用語(「測定基準」「利害」「対称的」等の学術的な
+言葉)を地の文で使うのではなく、日常の言葉でその人の感じ方を描いてください。Evidenceは
+必要ですが、記事の主役にはしないでください。
+
 【Main Story slotの役割(この記事ではQuestion/Hookとして書く)】
 (中略、Hookの役割定義は無変更)
 
-【### 見出し1つ目の役割(Voice 1)】
-実在する1つの立場(利害・経験・制度的立場を持つ当事者)を描いてください。(...)
-
-【### 見出し2つ目の役割(Voice 2 + Tension、新しい見出しを追加しない)】
-まず、Voice 1とは異なる利害・立場の種類(例: 経営側と従業員側、部門と個人、新人教育
-担当と柔軟な働き方を求める人)を持つ、もう1つの実在する立場を、(...)
+【### 見出し1つ目の役割(1つ目のVoice)】
+Verified Fact Ledgerで示された、実在する1つのstakeholder perspectiveを描いてください。(...)
+
+【### 見出し2つ目の役割(2つ目のVoice + Tension、新しい見出しを追加しない)】
+まず、1つ目のVoiceとは異なる、もう1つの実在するstakeholder perspectiveを、(...)
+2つのVoiceは、単に異なる数字・異なるデータを引用しているだけであってはいけません。
+責任(responsibility)・動機(incentive)・生きられた経験(lived experience)・
+制約(constraint)・価値観(value)・優先順位(priority)のうち、根本的な部分で
+異なっている必要があります。
 
 (Tensionの4軸)
-  (a) 何を測定・評価の基準にしているか、(b) 誰の利害を最優先にしているか、
-  (c) どのような価値観を前提にしているか、(d) そもそもどのような問いを立てているか
+「どちらのデータが正しいか」を決めようとしないでください。そうではなく、なぜ両方の
+Voiceが、それぞれの立場からは合理的に見えるのかを掘り下げてください。
+(なぜ両方とも理にかなって聞こえるのか / 前提の違い / 優先順位 / 何を測っているか /
+責任範囲の違い)

 【In One Line見出し以降(Closing)の役割】
 (要約ではなく一段深い理解、の趣旨は維持しつつ文言を明確化)

 【Point Balance原則...の扱いについて】
 (「異なる実在の立場」→「異なる実在のstakeholder perspective」に文言統一。
 末尾に「長さを揃えるためにVoiceの人間らしい描写を削らないでください」を追加)
```

全文は`er012_output/editorial_b_voices_trial_03/audit/b_family_voices_focus_module_block.txt`
(旧)と`er012_output/editorial_b_voices_trial_04/audit/b_family_voices_focus_module_block.txt`
(新)を参照。

### 1-2. TOPIC_JAの変更(Focus Module以外の変更、判断根拠を明記)

Trial-03のTOPIC_JAは「個別事例に注目する立場 vs 業界全体のデータに注目する
立場」という測定基準比較の枠組みを、Writerへ渡す背景説明の中で既に指定して
いた。この文言は`{topic}`として`【今回のテーマ】`という強い位置(マスター
記事の直下)にそのまま挿入されるため、Focus Moduleをどれだけ修正しても、
TOPIC_JA自体が「個別事例 vs 集計データ」という構図を明示的に指示していれば、
記事がその構図に引き戻されるリスクが高いと判断した。そのため今回は、テーマ
(固定席復活)自体は変更せず、TOPIC_JAから「個別事例に注目する立場と業界
全体のデータに注目する立場」という比較軸の指定を除去し、「実際にこの状況を
生きている複数の当事者が、それぞれ何を経験し、何を大切にし、何を心配し、
何に責任を持っているのかを描く」という中立的な記述に置き換えた。**この
変更はFocus Module以外の変更であり、指示された「Focus Module修正だけ」から
外れる可能性がある点を、Fableレビューへ明示的に報告する。** 変更しなかった
場合、TOPIC_JA自体がTrial-03と同じ構図を再指示してしまい、Focus Module
単体の効果を検証できないと判断したための決定だが、最終的にこれが「Focus
Module修正だけ」の範囲内かどうかはFableの判断を仰ぐ。

### 1-3. Research追加分

Trial-03のResearch成果(`research/raw_facts_research.json`等、既存ファイル、
無変更)を再利用しつつ、stakeholder perspective(当事者の経験・発言・利害)
が不足していたため、追加Research(Stage 1B/2B)を実施した。既存の承認済み
Perplexity(sonar-pro)呼び出しパターンをそのまま使用。

- Stage 1B(fact収集): 14件のfactを取得。集計統計中心だったTrial-03の
  Researchと異なり、実名個人の発言(Scotiabankの不動産責任者、ワークプレイス
  心理学者Dr. Nigel Oseland)、当事者への街頭インタビュー(TOKYO MX+、日本の
  会社員50人)、当事者へのインタビュー記事(note「REAL VOICE #05」、
  フリーアドレスで働くパート社員3名)、当事者の一人称の体験談(CNET Japan)
  など、生きた経験に基づくfactを重点的に収集した(`research/raw_facts_
  research_stakeholder.json`、可読版`research/facts_research_stakeholder_
  readable.txt`)。
- Stage 2B(独立verification): 14件中13件がCONFIRMED、1件がPARTIALLY_
  CONFIRMED(TOKYO MX+の賛否比率がStage 1Bの要約で「明示されていない」と
  誤って記載されていたのみの食い違いで、賛否双方の発言内容自体は独立に
  確認できた)。COULD_NOT_CONFIRM/CONTRADICTEDは0件(`research/raw_facts_
  verification_stakeholder.json`、可読版`research/facts_verification_
  stakeholder_readable.txt`)。

---

## 2. Perspective候補(3〜5件)と選定理由

詳細は`er012_output/editorial_b_voices_trial_04/research/perspective_
candidates.json`。

| 候補 | 立場 | 採否 |
|---|---|---|
| candidate_A | 週の大半をオフィスで過ごし、「自分の席」を必要としている社員 | **VOICE_Aに採用** |
| candidate_B | その日の気分・業務・関わりたい人に応じて座る場所を選びたい社員 | **VOICE_Bに採用** |
| candidate_C | オフィスポートフォリオ全体のコスト・稼働率に責任を持つ不動産/ワークプレイス戦略責任者(Linda Foggie等) | 不採用 |
| candidate_D | 新人教育・チームのメンタリングに責任を持つマネージャー | 不採用(Trial-03から継続) |
| candidate_E | 使われない予約席(ghost desk)・稼働率データを管理するファシリティ担当者 | 不採用 |

**選定理由**: candidate_A・Bは、いずれも実名個人の発言・街頭インタビュー・
当事者向け調査の生の回答・当事者自身の体験談に基づき、「同じオフィスの座席
という状況を、異なる心理的ニーズ(所属感・一貫性を求めるか、自由・変化を
求めるか)によってどう違って経験するか」という、対称的な賛成/反対ではなく
質的に異なる価値観の違いを描ける。

**却下理由**: candidate_C・Eは実在の発言(Linda Foggie等)に基づくものの、
Evidenceの中心が稼働率・コストの測定データに偏っており、**Trial-03で
問題視された「Evidence/分析軸の比較」の構図を再度招くリスクが高い**と判断
した。また両者はほぼ同じ論点(効率・柔軟性)に収斂し、独立した対立軸を
作りにくい。candidate_Dは、Trial-03に続き今回のResearchでも独立した厚い
Evidenceが見つからず、単一ソース(VIS)にとどまるため、想像で補うことを
避けて不採用とした(STOP条件「Researchから適切な2 Perspectiveを取れない」
には該当しない。candidate_A・Bで2つの十分なVoiceが確保できたため)。

---

## 3. Voice設計表(経験/価値/必要/心配/責任/得失 × 根拠)

根拠が無い項目は「(根拠なし)」と明記し、想像で埋めていない。

### VOICE_A: 週の大半をオフィスで過ごし、「自分の席」を必要としている社員

| 項目 | 内容 | 根拠 |
|---|---|---|
| 経験 | 毎日の席探し、他人が使った机への不安、私物や資料を置く場所がない不便さ、チームがばらばらに座る落ち着かなさ | A-02(LinkedIn News)、A-05(REAL VOICE #05) |
| 価値 | 所属感・集中しやすさ・チームとしての一貫性 | A-01(Gensler調査、所属感87% vs 74%、集中80% vs 67%)、A-04(Oseland) |
| 必要 | 同じような場所・同じ顔ぶれの近くにいられる予測可能性、私物を置ける場所 | A-05 |
| 心配 | 固定席が無いと職場が「非人間的」「方向感覚を失う」「精神的に疲れる」と感じられること | A-03(Forbes) |
| 責任 | **(根拠なし)**。このVoiceは個人としての経験・希望を語る立場であり、座席運用の意思決定責任を持つ立場としてのEvidenceは見つからなかった | — |
| 得失 | 固定席で所属感・集中を得るとするデータはある一方、何を失うかの直接的Evidenceは見つからなかった | A-01(得のみ) |

### VOICE_B: その日の気分・業務・関わりたい人に応じて座る場所を選びたい社員

| 項目 | 内容 | 根拠 |
|---|---|---|
| 経験 | 在宅勤務で既に自分の作業環境を持っている、フリーアドレスで他部署の人と話す機会が増えた経験 | B-03(CNET Japan)、B-04(REAL VOICE #05) |
| 価値 | 自由に場所を選べること、業務内容に応じて環境を変えられること | B-01(Carr Workplaces) |
| 必要 | その日の思考モードに合った場所(集中ゾーン・協働ゾーン等)へのアクセス | B-01 |
| 心配 | 同じ場所・同じ人間関係に固定される息苦しさ、人間関係から距離を取りたい時に逃げ場がなくなること | B-02(TOKYO MX+) |
| 責任 | **(根拠なし)**。VOICE_Aと同様、個人としての経験・希望を語る立場 | — |
| 得失 | 自由な選択・多様な交流を得るとする証言がある一方、同じインタビュー対象者が「自分の席が無いと落ち着かない」とも語っており、一貫性を失うことを示唆 | B-02、B-04(fact_007、両義的な発言) |

**両Voiceに共通する観察**: 「責任」の軸は、今回選定した2 Voiceのいずれにも
Evidenceが無かった(想像で補っていない)。これはVOICE_A/Bが「制度的な意思
決定者」ではなく「その状況を生きる個人」であることの自然な帰結であり、
Focus Moduleの6項目(経験/価値/必要/心配/責任/得失)全てを両Voiceで均等に
満たせたわけではない点を、Fableレビュー向けに率直に記録する。

---

## 4. Evidence配置表

各Factが実際の記事(Evidence Compression後の最終版)でどう使われたか、
帰属・範囲が保持されているかを全件記録する。

| Fact | 使用箇所 | 帰属・範囲の保持状況 |
|---|---|---|
| A-01(Gensler、16,000人超、所属感87/74・集中80/67) | Voice A、第2段落 | 出典名「Gensler」がEvidence Compressionで「a survey」へ一般化。所属感の87%/74%は厳密に保持。集中の80%/67%はPattern A(代表指標+補助トレンド)適用により具体数値を削り「showed the same pattern」という定性表現に圧縮(Fact自体は残存、数値のみ簡略化。ルール上許容された編集) |
| A-02(LinkedIn News、衛生・私物不安) | **不使用**(今回の生成では採用されなかった) | — |
| A-03(Forbes、impersonal/disorienting/mentally fatiguing) | **不使用** | — |
| A-04(Oseland quote) | **不使用** | — |
| A-05 / B-04(REAL VOICE #05、パート社員3名) | Voice A末尾(A-05の不便さの部分)。Point Role PlanningではB-04としてVoice Bのコミュニケーション面のメリットの根拠にも指定されていたが、最終文面ではA側(落ち着かなさ・置き場の不便さ)としてのみ明示的に描写された | 発言者の具体的人数(3名)は保持。個人名(矢萩さん・齋藤さん・吉田さん)は使われていない(一般化)。企業名は元のfactにも記載が無いため脱落なし |
| A-06(ITmedia MONOist、36.8%) | Voice A、第3段落「about 37 percent」 | 出典名「ITmedia MONOist」がEvidence Compressionで「one survey」へ一般化。36.8%→約37%への丸めはルール上許容範囲(方向・大きさを変えない) |
| B-01(Carr Workplaces、12人のリーダー、認知ゾーン) | Voice B、第2段落「Some workplace planners now describe areas for...」 | **Ledger Deviation CheckerがMINORとして検出**: 発言主体が「Carr Workplacesが取材した企業リーダー12人」から「workplace planners」へ変化(changed_actor=true)。認知ゾーンの内容自体はLedgerの範囲内 |
| B-02(TOKYO MX+、50人中40/10) | Voice B、第1段落 | 出典名「TOKYO MX+」がEvidence Compressionで「a survey of 50 Japanese office workers」へ一般化(対象人数・40/10という数値は保持)。B-02自体がPARTIALLY_CONFIRMEDだが、記事で使われた40/10という数値・発言内容自体はStage 2Bで確認済み |
| B-03(CNET Japan、在宅勤務で抵抗感が変化) | Voice B、第3段落「One report also described...」 | 出典名「CNET Japan」および年代(2020年)がEvidence Compressionで「One report」へ一般化。2020年という時点情報が失われ、2025-2026年時点の状況であるかのように読める余地がある(counter_or_limitationで元々「2020年のパンデミック初期の記事」と明記していた注意点が、圧縮後の記事には反映されていない) |
| X-01(Amazon、本社固定席復活) | Hook、第2段落「One company, for example,」 | 出典名「Amazon」がEvidence Compressionで「One company」へ一般化 |
| X-02(CBRE、83%→55%) | **不使用** | — |
| X-03(Desking.appコンサルタント、中間解の提案) | **不使用** | — |

**観察(Evidence Compression)**: Trial-03と同様、Evidence Compressionによる
出典名の一般化("Amazon"→"one company"、"Gensler"→"a survey"、"ITmedia
MONOist"→"one survey"、"TOKYO MX+"→"a survey"、"CNET Japan"→"one report")
が、後述のFact Checkerが独立検索で該当ソースを再特定できない一因になったと
考えられる(§6参照)。加えて、B-03では出典と同時に時点情報(2020年)も
失われており、記事の読み手には2020年の記事であることが伝わらない。これは
帰属・範囲(誰の発言か・いつの情報か)の圧縮が、Fact自体を歪めてはいない
ものの、記事の読み手にとっての時点の解像度を下げているケースとして記録
する。

---

## 5. 記事全文(原文、無編集)

```markdown
# The Office Desk Is Becoming a Question of Belonging and Choice

By September 2026, office seating is moving in two directions.

Some companies are bringing back assigned desks. One company, for example, ended hot desking at some headquarters that had used fixed seats before the pandemic. But it kept hot desking at some European offices where it was already in place.

Other companies continue to let workers choose a desk each day.

So what does a desk mean to the people who use it?

### For the worker who needs a place of their own

For an employee who spends most of the week in the office, a fixed desk can feel like more than furniture. It can offer a steady place to focus, keep work items, and feel connected to the workplace.

A survey of more than 16,000 office workers found higher reported belonging among people with assigned seats: 87 percent, compared with 74 percent among those without them. Concentration showed the same pattern, with higher reports from workers with assigned seats.

There is also a surprising detail. In one survey, about 37 percent of people working in free-address offices said their seating tended to become fixed anyway. The system offered choice, but daily needs often led people back to the same place.

That experience appeared in a Japanese company interview. Three part-time workers said that changing seats helped them talk with people from other departments. But they also said they felt unsettled without their own seat and did not know where to keep documents or personal items.

This suggests that opposition to hot desking is not always simple resistance to change. For some workers, continuity may be part of the basic condition for feeling settled and doing focused work.

### For the worker who needs to change the day

Another worker may want the opposite. A different seat can mean a different atmosphere, a chance to meet people, or a way to create distance from certain relationships.

In a survey of 50 Japanese office workers, 40 said free-address seating was acceptable. Some said they liked changing their environment with their mood. Others liked being able to move away when they wanted distance from workplace relationships. Ten said no, citing problems such as finding a seat and having less access to their teams.

Some workplace planners now describe areas for deep focus, teamwork, light conversation, and rest. The idea is that workers choose a place for the kind of work they need to do that day. One report also described how some employees became more comfortable with free-address offices after creating a personal work area at home. Their stable base was at home, so the office could become a place for movement and contact.

These two views sound reasonable because they ask different questions. The first worker asks, "Where can I settle and belong?" The second asks, "What do I need now, and how much contact do I want?" One values a steady base. The other values control over change.

## In one line…

A desk can be a home base for one worker and a way to adjust work and social space for another. The deeper issue is not simply where desks are placed, but what each person needs the office to provide.
```

---

## 6. 技術結果

- **Phase A(挿入確認)**: `clean_single_insert_confirmed=True`
  (`er012_output/editorial_b_voices_trial_04/audit/phase_a_result.json`)。
- **Writer**: 1回で`status=OK`(NG_REVIEW_REQUIREDなし、Local Rewrite
  cycleは発生せず=Ledger逸脱にMAJORが無かったため)。
- **Fact Checker**: verdict=**REVIEW_REQUIRED**(non-blocking、既存policy
  通り)。contradictions=0件。unsupported_specific_claims 4件、いずれも
  「独立検索でこの具体的な出典・数値を再特定できなかった」という性質
  (37%という丸め値、REAL VOICE #05の3名インタビュー、TOKYO MX+の50人
  40/10、CNET Japanの在宅ワーク因果関係)。**Trial-03と異なる観察**: 今回の
  原因は、Evidence Compressionが出典名(Gensler、ITmedia MONOist、TOKYO
  MX+、CNET Japan等)を一般化した結果、Fact Checker自身のWeb Search toolが
  どのソースを検索すべきか分からなくなり、独立検索で再確認できなかった
  ものと考えられる。これらのfactは全て本Trial自身の2段階Research(Stage
  1B/2B)で独立verification済み(§1-3参照)であり、捏造ではない。ニッチな
  日本語ソース(note記事、街頭インタビュー、地方局派生コンテンツ)を扱う
  今回のstakeholder型Ledgerでは、Fact CheckerのWeb Search toolの再現率が
  相対的に低い可能性がある、という観察として記録する。
- **Ledger Deviation Checker**: overall_status=**LEDGER_COMPLIANT**、
  deviations=1件(MINOR、changed_actor=true、§4参照)。Local Rewrite発火
  なし(MAJORが無かったため)。
- **Directional Fact Precheck**: overall_status=**PASS**(Trial-03の
  DIRECTION_REVIEW_REQUIREDから改善)。今回、Verified Fact Ledgerを
  Trial-03より散文寄りの記述形式にしたことが、この改善に寄与したと考え
  られる(Trial-03 §5・§9-3で予告した改善)。
- **Point Overlap QA(monitoring)**: lexical overlap point_one_vs_point_two
  =0.263、point_two_vs_point_one=0.253(閾値0.40未満、いずれもflagged=
  False)。
- **Point Value QA(monitoring)**: PASS(2 Point × 6項目すべてPASS、
  reasoning付き)。
- **語数**: 全体502語(参考: Trial-03のsoft range 280-420を超過。Focus
  Moduleの指示通り、Voiceセクションの長さ目標は適用しておらず、意図的な
  超過)。内訳: Hook=72語、Voice A=192語、Voice B(Tension含む)=198語、
  Closing=40語(`er012_output/editorial_b_voices_trial_04/b1b_run01/
  length_report.json`)。
- **Cost**: OpenAI(gpt-5.6-luna、Point Role Planning・Writer・Evidence
  Compression・Point Value QA・Fact Checker[web_search 14回]・Ledger
  Deviation Check、計6 call)input 148,908 tokens・output 14,597 tokens、
  pricing_snapshot.json単価(input $0.20/1M、output $1.20/1M)で概算
  約$0.047。Web Search fee($10/1,000 call×14回)を加算すると約$0.187。
  Perplexity(sonar-pro、追加Research Stage 1B/2B)input 8,681 tokens・
  output 12,536 tokens、料金はTrial-03同様pricing_snapshot.jsonに記載が
  無いため参考値扱い。**合計概算1記事あたり1ドル未満(¥500を大幅に下回る)**、
  Cost超過によるSTOPには該当しない。TTSは実行していない。

---

## 7. Sonnet自身の受入条件セルフチェック(Editorial条件1〜8、最終判定はFable)

1. **Voiceはデータセット・トレンド・主張ではなく実在するstakeholder
   perspectiveか**: 概ね達成。Voice本文は「For an employee who spends
   most of the week in the office, a fixed desk can feel like more than
   furniture.」のように、人の感覚を主語にして始まっている。ただし、
   「A survey of more than 16,000 office workers found...」「In a survey
   of 50 Japanese office workers, 40 said...」のように、Evidenceの提示
   そのものが文の主語になっている箇所も残っており、完全に「人」だけを
   主語にした記述にはなっていない(部分的達成)。
2. **経験/価値/必要/心配/責任/得失から書かれているか**: 経験・価値・
   必要・心配の4項目は両Voiceともある程度描けている(§3参照)。責任・
   得失の一部は根拠が無く空欄のままであり、6項目全てを満たしてはいない
   (想像で埋めなかったことの裏返しでもある)。
3. **「この立場なら、そう感じるのは分かる」と思えるか**: Voice Aの
   「felt unsettled without their own seat and did not know where to
   keep documents or personal items」、Voice Bの「a way to create
   distance from certain relationships」は、具体的で共感しやすい記述に
   なっていると考えられる。最終判断はFable。
4. **2つのVoiceが責任/動機/経験/制約/価値観/優先順位で根本的に異なるか
   (単なる数字の違いでないか)**: 達成。Voice Aは「一貫性・所属感」、
   Voice Bは「自由・社会的距離のコントロール」という異なる心理的価値観
   に基づいており、Trial-03の「個別事例データ vs 集計データ」という
   分析軸の比較とは異なる構図になっている。Tension段落の「The first
   worker asks, 'Where can I settle and belong?' The second asks, 'What
   do I need now, and how much contact do I want?'」がこれを明示している。
5. **EvidenceがVoiceを裏付けているだけで、Evidence自体がVoiceになって
   いないか**: 上記1と同様、部分的達成。数字が本文の一部に残っているが、
   Trial-03(「One UK analysis found that fixed-seat workplaces had an
   average satisfaction score of 69.6, compared with 68.2...」のような
   数字の並列)と比べると、数字より先に人の経験・感情の記述が来る構成に
   なっている。
6. **Tensionが「どちらのデータが正しいか」ではなく、前提・優先・測定・
   責任の違いを掘り下げているか**: 達成。「These two views sound
   reasonable because they ask different questions.」から始まり、
   両者が持つ異なる問い・価値観を言語化しており、「正しさ」を競わせて
   いない。
7. **Closingが要約でなく一段深い理解を示しているか**: 達成。「The
   deeper issue is not simply where desks are placed, but what each
   person needs the office to provide.」は要約ではなく、問いの立て方
   自体を転換している。
8. **トーンがLight・conversational・human-centeredで、業界レポート的で
   ないか**: Trial-03と比べて改善している(数字の羅列的な文が減り、
   人物の感情・体験の描写が増えた)が、「A survey of...」「In a survey
   of 50 Japanese office workers, 40 said...」のような調査報告的な文
   構造がまだ複数箇所に残っており、完全に払拭できたとは言い切れない。
   Reference Example固有の定型表現("Imagine..."等)は検出されなかった。

**総括(Sonnet自身の見立て、最終判定はFable)**: Trial-03で指摘された
「Voice選びがDiscovery寄り」「体裁が硬い」という2点については明確な改善が
見られた(§3のVoice設計・§7-4/6の分析が示す通り)。一方で、「Evidence自体
がVoiceになっている」箇所が完全には解消されておらず(§7-1/5/8)、Focus
Moduleの「経験・価値を主語にする」指示を、より強い禁止・書き換え例付きの
指示にする余地がある可能性がある。この点はUSER_DECISION_REQUIREDとして
残す(下記§9)。

---

## 8. Closeout分類案

**VALIDATED**(範囲: Voice数2・B1・Article-only、Focus Module修正の効果
検証。Production変更ゼロ、既存Fact Safety機構は無改造で正常動作、Point
Overlap/Value QAのmonitoring専用adapterも設計通り機能、Directional Fact
PrecheckはPASSへ改善)。

ただし以下は**USER_DECISION_REQUIRED**として残る:

1. Trial-04で残った「Evidence自体がVoiceになっている」箇所(§7-1/5/8)を、
   さらなるFocus Module修正で解消すべきか、それともこの程度は許容範囲か。
2. TOPIC_JAの変更(§1-2)が「Focus Module修正だけ」の範囲内と言えるか、
   それとも別の変更軸として扱うべきか。
3. Voice設計で「責任」軸のEvidenceが両Voiceとも見つからなかった点(§3)を
   踏まえ、将来「責任」を持つ立場(candidate_C/D/E)を第3のVoiceとして
   含める設計(Voice数3以上)を検討するか。
4. B Family Common Skeleton(Question/Hook+可変Voice+Tension+Closing)を
   正式採用するか(Trial-03設計報告§17-1の再確認、継続保留)。
5. Fact CheckerのWeb Search toolがニッチな日本語ソースを再確認できな
   かった点(§6)を踏まえ、B Family Voices用のEvidence Compressionで
   出典名の一般化を一部制限する(例: note記事・街頭インタビュー等の
   ソースは出典名を残す)ガードレールが必要か。
6. B-03(CNET Japan)で時点情報(2020年)がEvidence Compressionで失われた
   点(§4)を踏まえ、B Family Voices用のEvidence Compressionルールに
   「時点の解像度」への追加配慮が必要か。

---

## 9. SSOT登録案(本タスクでは登録していない、後続タスクで反映)

- **DECISION_LOG.md追記候補**: 「EDITORIAL-B-FAMILY-VOICES-TRIAL-04
  (Lane B、2026-09-06)で、Trial-03のユーザー評価を踏まえたFocus Module
  再Trialを実行し、Production変更ゼロのままVALIDATED(範囲限定)。Voice選び
  のDiscovery寄り傾向は改善したが、Evidence自体がVoiceになる傾向は部分的に
  残存。Production採用は別途USER_DECISION_REQUIRED」を1エントリとして追記。
- **既存Open Item(Trial-03由来)の更新候補**: 「B Family Voices/
  Perspective Skeletonの正式採用可否」等の既存Open Itemに、Trial-04の
  結果(§8の6項目)を追記。
- **HISTORY_INDEX.md追記候補**: 本タスクの管理ID・日付・要旨を1行で追記。

---

**Status: 本Reportの提案はVALIDATED(範囲限定の技術検証)、Production採用は
別途USER_DECISION_REQUIRED — NOT APPROVED_FOR_PRODUCTION, NOT
PRODUCTION_WIRED。最終判定・Editorial条件1〜8の合否判断はFableに委ねる。**

---

## 10. Fableレビュー修正1回目(run02、2026-09-06)

管理ID: **EDITORIAL-B-FAMILY-VOICES-TRIAL-04**(Sonnet委任1回目に対するFable
差し戻し、修正1回目)。§1〜9(run01)は無変更で保持し、本節を追記する。

run01記事に対するFableレビュー結果: Voice選び・Tension・Closing・Fact
Safetyは達成、TOPIC_JAの変更は範囲内としてFableが承認。一方で(1)Hookが
ニュース/分析調("By September 2026, office seating is moving in two
directions...")で人の情景から入っていない、(2)Evidenceが主語の文が4箇所
以上("A survey of...found..."等)、(3)Voice Bに第三者(workplace planners)
の視点が混入、(4)502語で長すぎる、という4点の修正指示を受けた。Tension・
Closingは維持指示。

### 10-1. Focus Module Block差分(原文)

`er012_editorial_b_voices_trial_04.py`のみを修正(Research/Verified Fact
Ledger/選定した2 Voice/骨格マッピングは無変更、記事本文の手作業書き換えは
行っていない)。`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`の末尾へ、Fable指示の
(f)〜(k)をそのまま英語で追加。ヘッダー行に`run02(Fableレビューによる修正
指示1回目)`を追記。差分全文:

```diff
--- run01 (old)
+++ run02 (new)
@@ ヘッダー行 @@
-この記事タイプ専用の骨格再定義。EDITORIAL-B-FAMILY-VOICES-TRIAL-04、Production未採用)】
+この記事タイプ専用の骨格再定義。EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02
+(Fableレビューによる修正指示1回目)、Production未採用)】
@@ ブロック末尾へ追加 @@
+
+【Hook・語り口に関する追加指示(EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02、Fableレビューに
+よる修正指示1回目。以下は上記の指示への追加であり、置き換えではありません。前回(run01)
+の記事はHookがニュース/分析調で始まり、Evidenceの提示自体が文の主語になっている箇所が
+複数あり、Voice Bに第三者の視点が混入していたため、その3点を修正するための指示です)】
+Apply the following rules (f)-(k) in addition to everything above.
+
+(f) Open with a small, concrete everyday scene involving a person (arriving at the office,
+looking for a seat, unpacking, choosing where to sit today), then pose the question. Do not
+open with company trends, dates, or "two directions".
+
+(g) Inside each Voice, the grammatical subject of nearly every sentence must be the person or
+people of that Voice (what they do, feel, need, worry about). Never write sentences whose
+subject is a survey, report, analysis, study, or figure ("A survey found...", "One report
+described...", "The data show..."). Do not use analyst phrasing such as "This suggests
+that...", "showed the same pattern", "reported belonging".
+
+(h) Use at most one number per Voice, and fold it into the person's perspective in spoken form
+("and they are not alone — most people with a fixed desk say they feel they belong"; "about
+four in ten workers in free-address offices find they drift back to the same seat"). Keep
+exact figures only where the Verified Fact Ledger requires them; otherwise prefer "most",
+"about four in ten" over exact percentages. The Spoken-first原則(数字の扱い)below still
+applies in full.
+
+(i) Do not import third-party viewpoints (planners, consultants, management) into a worker's
+Voice. If a design idea matters, express it as what this worker wants or notices.
+
+(j) Tone target: light, conversational, human-centered, as if explaining to a friend; short
+sentences; no report vocabulary.
+
+(k) Length: aim for roughly 350-420 words in total; achieve this by removing survey-style
+sentences, not by cutting the human details. Tension and Closing may stay close to the
+previous run's length and content.
```

全文は`er012_output/editorial_b_voices_trial_04/b1b_run02/audit/phase_a_
b_family_voices_focus_module_block.txt`(新、run02)と`er012_output/
editorial_b_voices_trial_04/audit/b_family_voices_focus_module_block.txt`
(旧、run01、無変更のまま保持)を参照。

コード上の変更点(差分は上記に加え):
- `LEVEL_OUT_DIR`をrun01固定から`RUN_ID`変数経由の`b1b_run02`へ変更
  (`b1b_run01/`は無変更のまま保持)。
- `run_phase_a()`の監査ファイル出力先を引数化し、run02では
  `b1b_run02/audit/`配下(`phase_a_candidate_template.txt`等)へ出力する
  ように変更。これによりrun01時代の`OUT_DIR/audit/`直下のファイル(tracked
  済み)を上書きしない。
- Writerのcost log出力先を`OUT_DIR/raw_usage_log_trial04_writer.jsonl`
  (run01、tracked)から`b1b_run02/raw_usage_log_trial04_writer_run02.jsonl`
  へ分離。
- Summary出力先を`OUT_DIR/trial04_summary.json`(run01、tracked)から
  `b1b_run02/trial04_summary_run02.json`へ分離。
- 上記により、run02の新規出力は全て`b1b_run02/`配下に閉じ込められている
  (`git status`で確認済み。run01・その他既存tracked出力への差分ゼロ)。

### 10-2. run02記事全文(原文、無編集)

```markdown
# The Desk You Return To, or the Desk You Choose?

Picture an employee arriving at the office. They put down a laptop, look across the room, and ask: "Where should I sit today?" In September 2026, some companies are bringing back assigned desks. Others are keeping hot desking, where workers choose a shared seat each day. So what should an office give people: a place that feels like theirs, or the freedom to choose a different place today?

### The worker who needs a place to return to

For an employee who spends most of the week in the office, a desk can feel like a small home base. They can keep papers nearby and return to a familiar place.

Some workers described shared desks as a loss of personal space. They worried about used keyboards and other people's desks.

In Japan, three part-time workers said changing seats made conversations with other departments easier. But having no personal place felt unsettling, and storing papers and personal items became difficult.

Employees with assigned desks more often reported belonging and concentration in a survey. In another survey, about 37% of free-address workers said seating tends to become fixed.

That hidden pull matters. A team zone, or a seat reserved when needed, may offer an anchor without making every desk permanent.

### The worker who needs room to move

For another employee, a desk is a choice, not a home base. They may want a quiet place for deep focus, a shared area for teamwork, or a spot for light conversation or rest. They can match the space to the task.

Some workers liked changing their environment with their mood. Some valued moving away when they wanted distance from a workplace relationship.

The three workers in another interview found it easier to talk with people from other departments when they changed seats. For this worker, movement helps control focus, contact, and distance through the day.

These workers are not answering the same question. The first asks, "Where can I feel settled enough to belong and focus?" The second asks, "What kind of space and contact do I need today?"

One protects continuity. The other manages change, collaboration, and distance. So the same shared floor can feel reassuring to one person and tiring to another. The seat is doing different work for each of them: it is either a place to return to or a way to shape the day.

## In one line…

The deeper question is not simply where desks are placed. It is what kind of control a worker needs over belonging, focus, and contact during the day.
```

保存先: `er012_output/editorial_b_voices_trial_04/b1b_run02/article.md`
(Local Rewrite cycle 1回適用後の最終版。Evidence Compression前の版は
`b1b_run02/audit/pre_editor_article.md`を参照)。

### 10-3. run01との差分要約

| 観点 | run01 | run02 |
|---|---|---|
| Hook | "By September 2026, office seating is moving in two directions."(企業動向の要約から開始) | "Picture an employee arriving at the office. They put down a laptop, look across the room, and ask: 'Where should I sit today?'"(人の情景+問いから開始) |
| Evidence主語文("A survey found..."等) | 4箇所以上("A survey of more than 16,000 office workers found...", "In one survey, about 37 percent...", "In a survey of 50 Japanese office workers, 40 said...", "This suggests that opposition to hot desking...", "Concentration showed the same pattern") | **0箇所**(全文精査。数字を含む文でも主語は"Employees with assigned desks"「約37%のfree-address workers」のように人・人数が主語になっており、"survey"/"report"/"data"が主語の文は検出されなかった) |
| 第三者視点の混入 | "Some workplace planners now describe areas for deep focus..."(Voice Bにplanner視点が混入) | **検出されず**(該当箇所は"They may want a quiet place for deep focus..."のように、この働き手自身が望むこととして書き換わっている) |
| 数字の数(Voice毎) | 未整理(複数の具体的%が各Voiceに散在) | Voice A: 2件("three part-time workers"という人数表記+「約37%」の1件、うち統計的数字は37%の1件のみ)。Voice B: 1件("three workers"、Voice Aと同じ人数の再言及)。(h)の「1 Voice内で数字は最大1個」を統計的数字(%等)に限れば両Voiceとも達成、実在の当事者の人数(three)まで含めると厳密には超過しており、Fableの判断を仰ぐ点として下記10-4・10-5に記録する |
| 語数 | 502語(Hook 72/Voice A 192/Voice B+Tension 198/Closing 40) | 403語(Hook 67/Voice A 129/Voice B+Tension 180/Closing 27)。目標350-420語の範囲内 |
| Tension・Closing | 維持指示どおり | 内容の骨格(2つの問いの対比、"One protects continuity. The other manages change...")は概ね維持されている(Writerは1回のみ実行、手での維持・書き換えは行っていない) |

### 10-4. 技術結果

- **Phase A**: `clean_single_insert_confirmed=True`
  (`er012_output/editorial_b_voices_trial_04/b1b_run02/audit/phase_a_
  result.json`)。
- **Writer**: 1回で`status=OK`。
- **Point Overlap QA(monitoring)**: lexical overlap point_one_vs_point_two
  =0.247、point_two_vs_point_one=0.229(閾値0.40未満、flagged=False)。
- **Point Value QA(monitoring)**: PASS(2 Point×6項目すべてPASS)。
- **Fact Checker**: verdict=**REVIEW_REQUIRED**(non-blocking、既存policy
  通り)。contradictions=0件。unsupported_specific_claims 3件(run01の4件
  から減少)、いずれも「独立検索でこの具体的な出典を再特定できなかった」
  という同じ性質(日本の3名パートタイム労働者の発言、環境変化を好む労働者
  の発言、共有デスクへの不満の発言)。run01と同様、Evidence Compressionに
  よる出典名の一般化(Gensler→a survey、ITmedia MONOist→another survey、
  TOKYO MX+/LinkedIn News/REAL VOICE→Some workers/another interview)が
  原因と考えられる(`b1b_run02/audit/pre_editor_article.md`と比較して確認)。
- **Ledger Deviation Checker**: 初回判定はLEDGER_DEVIATION(MAJOR 1件、
  Hookの「Others are keeping **or expanding** hot desking」の「拡大して
  いる」がLedgerに無い新規主張)。既存Local Rewrite機構(cycle 1/3、上限は
  無改変)が1サイクルで解消し、再判定でoverall_status=**LEDGER_COMPLIANT**、
  deviations=0件(`b1b_run02/audit/local_rewrite_cycles.json`)。
- **Directional Fact Precheck**: overall_status=**PASS**。
- **語数**: 全体403語(Hook=67、Voice A=129、Voice B+Tension=180、
  Closing=27、`b1b_run02/length_report.json`)。(k)の目標350-420語の範囲内。
- **Cost**: OpenAI(gpt-5.6-luna、Point Role Planning・Writer・Evidence
  Compression・Point Overlap QA・Point Value QA・Fact Checker[web_search
  10回]・Ledger Deviation Check・Local Rewrite 1件・再判定、計9 call)
  input 132,428 tokens・output 22,320 tokens、pricing_snapshot.json単価
  (input $0.20/1M、output $1.20/1M)で概算約$0.053。Web Search fee
  ($10/1,000 call×10回)を加算すると約$0.153。Perplexity呼び出しなし
  (Research再利用のため)。**1記事あたり1ドル未満**、Cost超過による
  STOPには該当しない。TTSは実行していない。

### 10-5. Sonnet自身のセルフチェック(条件1〜8、run02、根拠引用付き、最終判定はFable)

1. **Voiceは実在するstakeholder perspectiveか**: 改善。「For an employee
   who spends most of the week in the office, a desk can feel like a
   small home base.」のように人の感覚から始まる文が増え、Evidence自体が
   文の主語になる文は全文精査で検出されなかった(達成、根拠: 10-3表)。
   ただし「a desk can feel like...」「movement helps control...」「The
   seat is doing different work...」のように、人ではなく物・行為
   (desk/movement/seat)が文法上の主語になっている文が複数残っており、
   Fableが指摘した「Evidence主語」とは異なる種類だが、「ほぼ全ての文の
   主語が人であるべき」という(g)の文字通りの基準には完全には届いていない
   (部分的達成、この点はFableの判断を仰ぐ)。
2. **Hookが人の情景から入っているか**: 達成。「Picture an employee
   arriving at the office. They put down a laptop, look across the
   room, and ask: 'Where should I sit today?'」は、企業動向ではなく
   個人の具体的な動作から始まっている。**一方で、"Picture..."という
   開始語は、既存の禁止定型表現"Imagine..."と意味的に同義の呼びかけで
   あり、明示的に禁止されていた"Imagine.../Now look at..."等のカテゴリに
   抵触する可能性がある。これは意図せず発生した副作用であり、手作業では
   修正していない。USER_DECISION_REQUIREDとして下記に記録する**。
3. **Evidence主語文が解消されたか**: 達成(10-3表参照、全文精査で0件)。
4. **数字が1 Voiceあたり最大1個に抑えられているか**: 部分的達成。統計的
   数字(%等)は各Voiceとも1個以下(Voice A「約37%」1個、Voice Bは0個)。
   ただし実在の当事者の人数を表す「three part-time workers」
   「The three workers」がVoice A・Bの双方に出現しており、これを数字と
   数えると両Voiceとも1個を超える。この人数表記はVerified Fact Ledgerが
   要求する固有の当事者情報(架空でない実在の3名)であり、(h)が念頭に
   置いていた「調査統計の丸め」とは性質が異なると考えられるが、厳密な
   「最大1個」基準には届いていない。Fableの判断を仰ぐ。
5. **第三者視点の混入が解消されたか**: 達成(10-3表参照、
   「workplace planners」等の第三者への言及は検出されず)。
6. **トーン(light・conversational・human-centered)**: 改善。調査報告的な
   文構造("A survey of...found...")が解消され、短い文・平易な語彙が
   増えた。ただし4で述べた「a desk can feel like...」等、物を主語にした
   やや説明的な文もなお残る。
7. **Tension・Closingが維持されているか**: 維持指示どおり、Writerは1回
   のみ実行し手作業での維持・書き換えは行っていない。Tensionの骨格
   (「These workers are not answering the same question.」「One
   protects continuity. The other manages...」)、Closingの骨格
   (「The deeper question is not simply where desks are placed.」)は
   run01と概ね同じ趣旨を保っている。
8. **長さ(350-420語)**: 達成。403語(10-4参照)。

**総括(Sonnet自身の見立て、最終判定はFable)**: Fableが指摘した4点のうち、
(1)Hookの人の情景からの開始、(2)Evidence主語文の解消、(3)第三者視点の
排除、(4)長さの短縮は、いずれも改善・達成したと判断する。一方で、意図せず
副作用として、Hookの開始語"Picture..."が既存の禁止定型表現"Imagine..."と
同カテゴリに当たる可能性がある点、および実在の当事者の人数表記(three)を
厳密に「数字」として数えると(h)の「1 Voice最大1個」を超える点の2つが
新たにUSER_DECISION_REQUIREDとして残る。

### 10-6. USER_DECISION_REQUIRED(run02で新たに発見・確認された点)

1. Hookの"Picture an employee arriving at the office..."が、既存の禁止
   定型表現"Imagine.../Now look at..."と同じカテゴリ(呼びかけ型の
   scene-setting opener)に当たるか。当たる場合、Focus Moduleへ
   "Picture..."も明示的に禁止語として追加する必要があるか。
2. 実在の当事者の人数表記(例: "three part-time workers")を、(h)の
   「1 Voice最大1個」の対象に含めるべきか、それとも統計的数字とは区別し
   除外してよいか。
3. §8(run01)のUSER_DECISION_REQUIRED 1〜6は、本節の結果を踏まえてなお
   未決のまま残る(TOPIC_JAの変更範囲、Voice数3以上の検討、Fact Checker
   のWeb Search再現率、Evidence Compressionでの時点情報の扱い等)。

Status(run02を含む本Reportの提案): 引き続き**VALIDATED**(範囲: Voice数2・
B1・Article-only、Focus Module修正の効果検証)。Production採用は別途
USER_DECISION_REQUIRED — NOT APPROVED_FOR_PRODUCTION, NOT
PRODUCTION_WIRED。最終判定はFableに委ねる。

---

## 11. Fableレビュー往復2回目(run03、2026-09-06)

管理ID: **EDITORIAL-B-FAMILY-VOICES-TRIAL-04**(Sonnet委任2回目=往復2回目。
run02に対するユーザー評価6点の改善指示への対応)。§1〜10(run01・run02)は
無変更で保持し、本節を追記する。Lane B専用タスクであり、Lane A・
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`には触れていない。

run02記事に対するユーザー評価: Trial-03から大きく改善したと評価された一方、
(1)Voiceが「For an employee who...」のように外側から説明された人物に
なっている、(2)Evidenceが前に出すぎている、(3)構造が5区切り
(Hook→Voice A→Voice B→Tension→Closing)として明示的でない(Tensionが
Voice Bへ溶け込んでいる)、(4)ClosingがIn One Lineの言い換えに寄っている、
(5)Voice内に第三者(設計者・コンサル)の解決策が混入、(6)Hookの
"Picture..."が定型的な呼びかけ表現、という6点の改善指示を受けた。

### 11-1. Focus Module Block変更の概要(run02→run03、全面書き直し)

`er012_editorial_b_voices_trial_04.py`のみを修正した(Research/Verified
Fact Ledger/選定した2 Voiceは無変更、記事本文の手作業書き換えは行って
いない)。run02はrun01への追記(パッチ)方式だったが、run03は5区切り構造
という骨格そのものが変わるため、`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`を
全面的に書き直した(run02の(a)〜(k)の内容は整理・統合して引き継いだ)。
run02の全文は`er012_output/editorial_b_voices_trial_04/b1b_run02/audit/
phase_a_b_family_voices_focus_module_block.txt`(無変更のまま保持)、run03
の全文は`er012_output/editorial_b_voices_trial_04/b1b_run03/audit/phase_a_
b_family_voices_focus_module_block.txt`を参照(機械的な行単位diffは
ほぼ全行が変わる全面書き直しのため、可読性を優先し下記の変更点対応表と
run03全文の掲載[§11-1-2]で代替する)。

#### 11-1-1. ユーザー指示6点とFocus Module変更点の対応表

| ユーザー指示 | Focus Module Blockでの対応 |
|---|---|
| (1) Voiceが外側から説明された人物になっている | 新設【Voiceの書き始め方】節で"For [a/an] worker who..."という紹介文での書き出しを明示的に禁止し、Ledgerの具体的な状況(毎日していること・使っているもの)から書き始めるよう指示 |
| (2) Evidenceが前に出すぎている | 新設【Evidenceは脇役であること】節で、Evidence紹介文の連続を禁止し、人の経験・価値観の描写を主体にすることを明示 |
| (3) 5区切り構造が明示的でない | 新設【最重要・この記事だけの出力形式】節で、Hook(##)/Voice A(###)/Voice B(###)/Tension(##)/Closing(##)の5見出しをこの順序で必ず持つことを、具体的なMarkdownテンプレート付きで指示。Tensionは「2つ目のVoiceの続きの段落ではなく独立したセクション」と明記 |
| (4) ClosingがIn One Lineの言い換え | 【Closingの役割】節を、「2つのVoiceを見たことで問題の見え方自体がどう変わったか」への着地に書き換え(要約・In One Line言い換えを明示的に禁止) |
| (5) Voice内への第三者解決策の混入 | 新設【Voice内に第三者の視点・解決策を混ぜないこと】節で、run02の実例("A team zone...may offer an anchor")を挙げて明示的に禁止 |
| (6) Hookの"Picture..."定型表現 | 【Hookの役割と書き方】節で"Imagine/Picture/Think about/Consider/Now look at"を名指しで禁止し、三人称の具体的情景描写から始めるよう指示(コピー禁止の参考例文を提示) |

### 11-2. 5区切り実装の詳細(Trial adapterの処理)

5区切り構造(##×3+###×2)は、既存A Familyパーサの前提(`###`見出し
ちょうど2つ)から外れる。実装前にProduction側コードを読み取り調査した
結果を報告する:

- **Writer構造ゲート(`er002_ja_free_markdown_restore_r2.validate_point_
  structure`)**: `###`(レベル3)見出しの個数だけを検査し(`^#{3}...`の
  正規表現)、`##`(レベル2)見出しの個数・文言は一切検査しないことを
  コード読解で確認した。そのため、Voice A・Voice Bの2つだけを`###`に
  し、Hook・Tension・Closingの3つを`##`にすることで、既存ゲートを
  一切変更せずに5区切りを実現できると判断した。実際にrun03のWriterは
  1回目の呼び出しで`STRUCTURE_PASS`(`h3_count=2`)を得ており、この判断は
  実測でも裏付けられた(`er012_output/editorial_b_voices_trial_04/
  b1b_run03/audit/writer_attempts.json`)。
- **Point Overlap/Value QA(`gen.split_common_sections_for_point_qa`)**:
  この関数は`###`が2つあれば動作してしまう(Noneを返さない)が、
  Point Twoの終端を「`## In one line`」という特定文言でしか検出できず、
  run03の見出し("## Why They See It Differently"等)は終端として認識
  されない。合成テストで検証した結果、`point_two_body`にVoice B・
  Tension・Closingの内容が全て混入することを確認した(本タスクの検証
  ログに記録)。この関数をそのまま使うと不正確な結果を生むため、Trial
  adapter側に`split_five_voice_sections()`(新設)を実装し、Hook/Voice A/
  Voice B/Tension/Closingを見出し出現順にそのまま抽出する。Point
  Overlap/Value QAはこの5区切りparserが抽出したHook/Voice A/Voice Bを、
  Production側の同じprimitive関数(`er008_point_overlap_qa_18.flag_
  possible_paraphrase`、`er011_point_role_value_planning_01.run_point_
  value_qa`)へ個別に渡す形で実行した(ACTIVE_TASKの「個別に呼ぶ」の
  選択肢を採用。Production側の2関数自体は無変更)。
- **語数内訳(`sf1r1.section_word_counts`)**: 実測検証の結果、「in one
  line」を含まない`##`見出し(run03ではHook/Tension/Closingの3つ全て)の
  内容が集計から丸ごと落ちる(`intro=0`・`in_one_line=0`になる)ことを
  確認した。Voice A/Voice Bの値自体は、run03が`###`を常にちょうど2つ
  しか使わない設計のため実測上は正しいが、記事全体の内訳としては使えない。
  そのため`split_five_voice_sections()`から5区切り全ての正確な語数内訳を
  算出し、`five_section_length_report.json`へ別途保存した(既存の
  `length_report.json`・`sf1r1.section_word_counts()`呼び出し自体は参考値
  として維持し、スキーマ互換性を壊さない)。
- **Fact Checker/Ledger Deviation Checker/Local Rewrite/Directional Fact
  Precheck**: いずれも見出し構造に依存しない(生テキストを扱う)ことを
  個別にコード読解で確認済みのため、`run_voices_pattern()`の該当ロジック
  を一切変更せずそのままコピーした`run_voices_pattern_run03()`から、
  呼び出す関数・引数・順序とも同一のまま呼び出した。
- **Evidence Compression Editor(`er003_v1_n3_01_evidence_compression_
  editor.py::run_lossless_editor`)**: このProduction関数のprompt内には
  「Storyの論旨・構成を書き換えないこと(Title・Main Story・###見出し
  2つ・In One Lineの構成は維持する)」という記述、および出力形式の指示
  として「入力と全く同じMarkdown構造(# Title、Main Story、###見出し2つ、
  ## In one lineの結び)で出力してください」という記述があり、5区切り
  構造との不整合リスクがあると事前に判断した。この関数自体は変更せず
  (Production変更禁止)、実際にrun03の記事に対して無変更のまま適用し、
  出力を実測で確認した。結果、5見出し(## The Question / ### One Voice.../
  ### Another Voice.../ ## Why They See It Differently / ## What This
  Tells Us)は全て保持され、構造の破壊(見出しの削除・強制的な2見出しへの
  収束等)は発生しなかった(`er012_output/editorial_b_voices_trial_04/
  b1b_run03/audit/pre_editor_article.md`と`article.md`を比較して確認)。
  ただし、Evidence Compressionの許可編集ルール(Pattern A: Representative
  Metric + Supporting Trend)自体が例示する言い換え表現"showed the same
  pattern"が、Editorによって「Their reported ability to concentrate was
  80%, compared with 67%.」→「Their reported ability to concentrate
  showed the same pattern: 80%, compared with 67%.」という形で本文へ
  追加されたことを確認した。これはFocus Moduleが明示的に禁止した analyst
  phrasing("showed the same pattern")と文字列として一致するが、Evidence
  Compression EditorはFocus Moduleを見ておらず(別のsystem prompt)、
  Production側のPattern A許可リストにこの表現が例として含まれているために
  生じた。Writer自体はこの表現を使っていない(`pre_editor_article.md`には
  存在しない)。Production変更は行わず、事実として記録し、§11-7の
  USER_DECISION_REQUIREDへ追加する。

### 11-3. run03記事全文(原文、無編集、見出し込み)

Evidence Compression適用後の最終版(Local Rewrite cycleは発生していない、
Ledger MAJORが無かったため)。

```markdown
# A Desk Is More Than a Desk

## The Question

Monday morning, one worker walks straight to last week's desk. Another checks the room and chooses a seat near a shared task. By September 2026, office seating is moving in both directions. Amazon returned its Seattle-area and Arlington headquarters to assigned desks, while keeping hot desking in offices that had used it before the pandemic. Across companies, assigned seating fell from 83% to 55% by 2024. The question is not simply which system is better. It is what a desk means to the person using it.

### One Voice: The worker who needs a base

Keys, notebooks, and personal papers stay in one place when a desk waits each morning. Without that base, moving a keyboard and finding a place for belongings can feel tiring. Workers have described unassigned offices as impersonal, confusing, and mentally tiring. They have also raised worries about hygiene and personal space.

Workers with assigned desks reported a stronger sense of belonging in a study of more than 16,000 office workers: 87%, compared with 74% for workers without assigned desks. Their reported ability to concentrate showed the same pattern: 80%, compared with 67%. Among workers without a fixed desk, about six in ten wanted one. Yet about 37% of hot-desk workers said their seating had become fixed anyway. For someone in the office most days, a desk can feel less like a privilege than a steady place to begin.

### Another Voice: The worker who needs room to move

Another morning begins with a choice. Some offices offer places for deep focus, teamwork, light conversation, and rest. A worker can choose a setting that fits the task or the mood. Changing seats can also make contact with other departments easier—or create distance from a workplace relationship.

In one 2025 street interview with 50 Japanese office workers, four in five supported hot desking and one in five did not. Supporters mentioned changing their surroundings and moving away from people when needed. Some workers also became more comfortable with flexible office seating after creating a personal work area at home. Here, freedom means deciding how much contact the day should include.

## Why They See It Differently

These two views protect different kinds of control. One worker needs continuity: a familiar place can support a settled start and focused work. The other needs choice: the ability to change surroundings, meet people, or step back. One measures a good office through belonging and concentration. The other measures it through control over attention and social distance. That is why the same seating system can feel reassuring to one person and useful, or freeing, to another.

## What This Tells Us

After hearing both voices, fixed versus free no longer looks like a simple fight over furniture. It is a question of what workers need a workplace to provide: a dependable base, or room to change focus and distance from others. The desk is only the visible part. Underneath it are two different ideas of control.
```

保存先: `er012_output/editorial_b_voices_trial_04/b1b_run03/article.md`
(Evidence Compression後の最終版。Compression前の版は`b1b_run03/audit/
pre_editor_article.md`を参照)。

### 11-4. run02との差分表

| 観点 | run02 | run03 |
|---|---|---|
| Hookの書き出し | "Picture an employee arriving at the office..."(呼びかけ型) | "Monday morning, one worker walks straight to last week's desk. Another checks the room and chooses a seat near a shared task."(三人称の具体的情景から開始、"Imagine/Picture"系の禁止表現は検出されず) |
| Hookの後半 | Voice導入前の中立的な問い提示のみ | 情景の後、"By September 2026, office seating is moving in both directions."という、run01の禁止対象だった趣旨の文(トレンド要約)がAmazon固有名詞・83%→55%という数値とともに再度出現(§11-6-2で自己評価) |
| Voiceの書き始め方 | "For an employee who spends most of the week in the office, a desk can feel like a small home base."(人物を外側から紹介) | "Keys, notebooks, and personal papers stay in one place when a desk waits each morning."(具体的な物・状況から開始、"For [a/an] worker who..."型の紹介文は検出されず) |
| 5区切り構造 | Hook(見出しなし)→Voice A(###)→Voice B+Tension(###、同一見出し内)→Closing(## In one line) | Hook(## The Question)→Voice A(###)→Voice B(###)→Tension(## Why They See It Differently、独立見出し)→Closing(## What This Tells Us)。5見出しとも実装・実測確認済み |
| Evidence密度(Voice A) | "three part-time workers"/"a survey"/"another survey"/"37%"が連続 | 依然としてVoice A第2段落に4つの数値(87%/74%、80%/67%、six in ten、37%)が連続する箇所が残存(§11-6-2で自己評価、部分改善にとどまる) |
| 第三者解決策の混入 | "A team zone, or a seat reserved when needed, may offer an anchor..."(混入) | 検出されず。Voice Bの"Some offices offer places for deep focus, teamwork..."は、この当事者自身が使える選択肢の描写として書かれており、第三者(設計者等)の提案としては書かれていない |
| Closing | "The deeper question is not simply where desks are placed. It is what kind of control a worker needs..."(要約寄り) | "After hearing both voices, fixed versus free no longer looks like a simple fight over furniture. It is a question of what workers need a workplace to provide... The desk is only the visible part. Underneath it are two different ideas of control."(「両方のVoiceを聞いたことで見方が変わった」という明示的なフレーミング) |
| 語数 | 403語(Hook 67/Voice A 129/Voice B+Tension 180/Closing 27) | 454語(Hook 82/Voice A 132/Voice B 109/Tension 76/Closing 55、`five_section_length_report.json`) |

### 11-5. 技術結果

- **Phase A**: `clean_single_insert_confirmed=True`(`b1b_run03/audit/
  phase_a_result.json`)。
- **Writer**: 1回で`status=STRUCTURE_PASS`→`OK`(構造再試行なし、
  `h3_count=2`、`writer_attempts.json`)。
- **Point Overlap QA(monitoring、5区切り版)**: Voice A vs Hook=0.141、
  Voice B vs Hook=0.179、Voice A vs Voice B=0.156、Voice B vs Voice A=
  0.149(閾値0.40未満、いずれもflagged=False)。
- **Point Value QA(monitoring、5区切り版)**: PASS(Voice A・Voice B×6
  項目すべてPASS、reasoning付き、`point_overlap_value_qa_monitoring.json`)。
- **Fact Checker**: verdict=**REVIEW_REQUIRED**(non-blocking、既存policy
  通り)。contradictions=0件。unsupported_specific_claims 4件、いずれも
  run01・run02と同じ性質(Evidence Compressionによる出典名一般化のため
  独立検索で再特定できない。A-06の37%、B-03の在宅ワーク因果関係、A-03の
  Forbes表現、B-02の街頭インタビューの距離に関する記述)。
- **Ledger Deviation Checker**: overall_status=**LEDGER_COMPLIANT**、
  deviations=1件(MINOR、"had become fixed anyway"がA-06の「なりがち」を
  完了状態のように強めた、changed_certainty=true)。Local Rewrite発火なし
  (MAJORが無かったため)。
- **Directional Fact Precheck**: overall_status=**DIRECTION_REVIEW_
  REQUIRED**(run01・run02のPASSから後退)。3件中1件が"Their reported
  ability to concentrate showed the same pattern: 80%, compared with
  67%."という文で、Ledger側に「高い」という方向語があるのに対し、この文
  には明示的な方向語(higher/more等)が無く、機械的に一致/不一致を判定
  できないと判定された(`directional_fact_precheck.json`)。数値自体
  (80%/67%)はLedger通りで矛盾はなく、non-blocking(既存policy通り)。
  §11-2で述べた通り、この文はEvidence Compressionが"showed the same
  pattern"という表現を追加した文であり、この後退と無関係ではない可能性が
  ある(因果関係を断定はしない、観察として記録する)。
- **語数**: 全体454語(Hook=82、Voice A=132、Voice B=109、Tension=76、
  Closing=55、`b1b_run03/five_section_length_report.json`)。280〜420語
  という観察用の目安をやや超えているが、hard/soft gateではないため
  そのまま採用した。
- **Cost**: OpenAI(gpt-5.6-luna、Point Role Planning・Writer・Evidence
  Compression・Point Overlap/Value QA monitoring・Fact Checker[web_search
  12回]・Ledger Deviation Check、計6 call)input 134,367 tokens・output
  21,001 tokens、pricing_snapshot.json単価(input $0.20/1M、output
  $1.20/1M)で概算約$0.052。Web Search fee($10/1,000 call×12回)を加算
  すると約$0.172。Perplexity呼び出しなし(Research再利用のため、追加
  Researchは行っていない)。**1記事あたり1ドル未満**、Cost超過による
  STOPには該当しない。TTSは実行していない。

### 11-6. Sonnet自身の受入条件セルフチェック(10項目、根拠引用付き、最終判定はFable)

1. **Voiceが外側から説明された人物になっていないか**: 達成。Voice Aは
   "Keys, notebooks, and personal papers stay in one place when a desk
   waits each morning."、Voice Bは"Another morning begins with a
   choice."から始まり、"For [a/an] worker who..."型の紹介文は全文精査で
   検出されなかった(§11-4表参照)。
2. **Evidenceが脇役になっているか**: 部分的達成。Evidence-subject文
   ("A survey found..."等)自体は検出されなかったが、Voice A第2段落に
   87%/74%・80%/67%・six in ten・約37%という4つの数値が連続しており、
   「Evidenceの紹介が主役になる文を連続させない」という指示には完全には
   届いていない(§11-4表参照、Fableの判断を仰ぐ)。
3. **5区切り構造(Hook/Voice A/Voice B/Tension/Closing)が明示的か**:
   達成。5見出しとも実装され、`split_five_voice_sections()`で正しく
   抽出できることを実測確認した(§11-2、`writer_attempts.json`の
   `h3_count=2`)。
4. **Tensionが独立したセクションか(Voice Bへ溶け込んでいないか)**:
   達成。"## Why They See It Differently"という独立見出しの下に、
   "These two views protect different kinds of control."から始まる
   独立した段落として書かれている。
5. **Closingが要約でなく「見方の変化」を示しているか**: 達成。"After
   hearing both voices, fixed versus free no longer looks like a simple
   fight over furniture."という、Hookからの見方の変化を明示するフレーズ
   から始まっている。
6. **Voice内に第三者の解決策が混入していないか**: 達成。run02で問題視
   された"A team zone...may offer an anchor"のような第三者(設計者・
   コンサル)の提案は検出されなかった(§11-4表参照)。
7. **Hookが定型的な呼びかけ表現("Imagine.../Picture..."等)で始まって
   いないか**: 達成。"Monday morning, one worker walks straight to..."
   という三人称の情景描写から始まっており、禁止表現は検出されなかった。
8. **Hook全体がニュース/分析調に戻っていないか**: 未達成(部分的)。
   情景描写の直後に"By September 2026, office seating is moving in both
   directions."という文が続き、これはrun01で問題視された"office seating
   is moving in two directions"という文とほぼ同じ趣旨の記述であり、
   Amazonの固有名詞・83%→55%という数値とともに、Hookの後半がニュース
   要約調に戻っている(§11-4表参照、Fableの判断を仰ぐ)。
9. **固定ラベル("Voice A"/"Voice B")が使われていないか**: 達成。見出しは
   "One Voice: The worker who needs a base"/"Another Voice: The worker
   who needs room to move"であり、"ここから別のVoiceが始まる"ことが
   伝わる自然な表現になっている。
10. **Fact Safety(Fact Checker/Ledger Deviation Checker)が維持されて
    いるか**: 達成。contradictions=0件、Ledger MAJORなし、
    LEDGER_COMPLIANT(§11-5参照)。Directional Fact PrecheckのみREVIEW_
    REQUIREDへ後退したが、non-blockingであり数値自体の矛盾ではない。

**総括(Sonnet自身の見立て、最終判定はFable)**: ユーザー指示6点のうち、
(1)Voiceの書き始め方、(3)5区切り構造の明示化、(4)Closingの再定義、
(5)第三者解決策の排除、(6)Hookの禁止表現排除の5点は達成したと判断する。
(2)Evidenceの脇役化は部分的達成にとどまり(Voice Aの数値密度が依然として
高い)、また(6)に関連して、Hookの冒頭は改善したが後半がニュース要約調に
戻るという意図しない副作用が新たに生じた。これら2点はUSER_DECISION_
REQUIREDとして残す(下記§11-7)。

### 11-7. Closeout分類案・USER_DECISION_REQUIRED(run03で新たに発見・確認された点)

**Closeout分類案**: 引き続き**VALIDATED**(範囲: Voice数2・B1・
Article-only、5区切り構造への骨格変更を含むFocus Module再修正の効果検証。
Production変更ゼロ、既存Fact Safety機構は無改造で正常動作、Writer構造
ゲート・Point Overlap/Value QA・Evidence Compression Editorとも5区切り
構造下で実測動作を確認)。ただし以下はUSER_DECISION_REQUIREDとして残る:

1. Voice A第2段落の数値密度(87%/74%、80%/67%、six in ten、約37%が連続)
   をどこまで許容するか、さらなるFocus Module修正で減らすべきか。
2. Hook後半が"office seating is moving in both directions"というrun01
   由来のトレンド要約調に戻った点を、さらなる修正で排除すべきか、それとも
   Amazon等の背景事実をHookで簡潔に示すこと自体は許容範囲か。
3. Evidence Compression EditorのPattern A許可リストが例示する"showed the
   same pattern"という表現が、Focus Moduleが明示的に禁止したanalyst
   phrasingと文字列として一致する点(§11-2)。Voices記事タイプでは
   Evidence Compressionの許可編集リストに例外を設けるべきか、それとも
   これは通常のDiscovery/Why記事同様に許容してよいか。
4. Directional Fact PrecheckがDIRECTION_REVIEW_REQUIREDへ後退した点
   (§11-5)が、Evidence Compressionの"showed the same pattern"追加と
   関係している可能性があるかどうか(観察のみ、断定していない)。
5. §8(run01)・§10-6(run02)のUSER_DECISION_REQUIREDは、本節の結果を
   踏まえてなお未決のまま残る(TOPIC_JAの変更範囲、Voice数3以上の検討、
   Fact CheckerのWeb Search再現率、Evidence Compressionでの時点情報の
   扱い、"Picture..."系呼びかけ表現の扱い[run03では回避できたため実害は
   なかった])。

Status(run03を含む本Reportの提案): 引き続き**VALIDATED**(範囲: Voice数2・
B1・Article-only、Focus Module修正[5区切り構造]の効果検証)。Production
採用は別途USER_DECISION_REQUIRED — NOT APPROVED_FOR_PRODUCTION, NOT
PRODUCTION_WIRED。最終判定・Editorial条件のセルフチェックの合否判断は
Fableに委ねる。
