# EDITORIAL-B-FAMILY-VOICES-DESIGN-02 報告書

管理ID: **EDITORIAL-B-FAMILY-VOICES-DESIGN-02**
Lane: **Lane B / B Family(Voices-Perspective)**(Lane A: Discovery/News/Trend、OPEN-112/OPEN-117/ER-011系とは独立)
種別: **読み取り調査 + 設計提案(DESIGN / USER_DECISION_REQUIREDまで)**

**今回はTrial実行(LLM/TTS/Research API呼び出し)・Production/Prompt/Validatorコード変更・
Case Storyの本格設計・2 Reference Exampleのtemplate化のいずれも行っていません。
既存資産の読み取りとゼロベースの設計提案のみです。**

前提として、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)・
[ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md](ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md)・
[OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)・
[OPEN112_NO18_4LAYER_REVIEW_PACK_06.md](OPEN112_NO18_4LAYER_REVIEW_PACK_06.md)・
`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・`POOL_TOPIC_MASTER.md`・
`er003_v1_n3_01_articles_generate.py`(Read-only)を参照した。上記4本のReportは参考資料
(mock/DESIGN段階)であり、正式仕様ではない。

**重要な前提確認(今回の読み取りで判明)**: A Family 4層構造(Layer1 Common Writing
Contract / Layer2 A Family Common Skeleton / Layer3 Focus Module / Layer4 Article-specific
Inputs)自体、まだ`APPROVED_FOR_PRODUCTION`ではない。Discovery/Why Focus Moduleは
`VALIDATED`だが採否は`USER_DECISION_REQUIRED_WITH_RISK`のまま
([OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-112系、2026-09-04時点)、News/Trend Synthesisの
4層設計は`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`で設計のみ(Trial未実施)。
現行Production Writer本体(`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`)
は今も単一の巨大Discovery/Why専用文字列のままであり、4層構造のコードは
`er011_open112_a_family_4layer_prompt_trial_05.py`という**独立したTrial harness**にのみ
存在する(Production Writer本体は無変更)。したがって本Report全体は「まだ確定していない
4層構造」を前提にB Familyを設計する、という二重にDESIGN段階の提案であることに留意する。

---

## 1. Voices/Perspectiveの役割定義

**A Family既存資産の根拠**: A Familyは「Discovery/Why」(なぜそうなるかの解説)と
「News/Trend Synthesis」(何が起きた/何が変わりつつあるか)の2モードで構成される
([OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md) §0)。
いずれも「単一の中心的な筋(single throughline)」を核として持ち、Point One/Twoは
その筋への追加視点([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§5-B「Point One/Twoの役割定義(本文への追加視点。並立する複数の立場ではない)」)。

**提案**: Voices/Perspectiveは、A Familyの「単一の筋+その深掘り」という設計思想とは
根本的に異なり、**中心的な問い(Question)に対して、実在する複数の合理的な立場を
並立させ、その立場の違いの奥にあるTension(前提・利害・価値観・問いの立て方の違い)を
発見し、最後に一段深い理解へ着地する**、という役割を持つEditorial Typeとして定義する。
「正しい答えを1つ提示する」でも「賛否を並べる」でもなく、「なぜ同じ事象が立場によって
違って見えるのか」を読者に理解させることが中心目的であり、これはDiscovery/Why・
News/Trendのいずれとも異なる、A Familyには無い**新しい認知構造(複数主体の視点の
比較)**を扱う。

---

## 2. Discovery/Whyとの違い

| 観点 | Discovery/Why(A Family、既存) | Voices/Perspective(B Family、提案) |
|---|---|---|
| 中心構造 | 単一の現象・研究結果の「なぜ」を掘り下げる(単一throughline) | 単一の問いに対する**複数の立場**を並立させる |
| Main Story相当の役割 | 現象の核心を運ぶ長い本文([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md) §4「Main Storyの役割定義」) | 短いQuestion/Hook(Reference Example双方とも1節目は150語未満の導入のみ) |
| Point One/Twoの役割 | 本文への追加視点・深掘り(同上、本文の言い換え禁止が判定軸) | 各立場の合理性の描写(Perspective同士の類似度が判定軸になるべき、Main Storyとの重複ではない) |
| 対立の扱い | 対立を前提としない(現象の解説) | 対立(Tension)の発見そのものが記事の核 |
| 着地点 | In One Line=静かな要約(現象への一言理解) | Reference Exampleの"What This Tells Us"に相当する、Tensionから導かれる一段深い理解(単純な要約ではない、§13で詳述) |

**提案根拠**: Discovery/Whyの失敗モード(OPEN-91「Point Twoが調査レポート的になる」、
[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§10-6)は「事実の列挙になる」ことだが、Voicesの主要リスクは性質が異なり「賛成/反対の
単純な二項対立になる」ことである(タスク文書のユーザー意図、後述§10)。両者は似て
非なる失敗モードであり、Discovery向けに調整されたQA(Point Overlap QA閾値0.40等)を
そのまま流用すると誤った基準で判定するリスクがある(§11で詳述)。

---

## 3. News/Trend Synthesisとの違い

**A Family既存資産の根拠**: News/Trend Synthesisは「複数の独立したSignal(最近の
事実)を束ねたときに見える変化」を扱う([OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)
§3)。Point Twoは`counter-signal`/`limitation`を優先的に扱う設計(同§3追加ルール)。

**提案**: News/Trend Synthesisの「複数Signal」は**時間軸上の複数の事実**(同じ種類の
観測が複数時点・複数ソースに現れること)を束ねる。一方Voicesの「複数Perspective」は
**同一時点の同一事象に対する、異なる立場・利害・価値観からの見え方の違い**を扱う。
News/Trendの「counter-signal」は「主張を弱める反証」であるのに対し、Voicesの
「別のVoice」は反証ではなく「別の合理性」であり、いずれも「正しい/間違っている」の
軸ではなく「立場が違えば見え方が違う」という軸で成立する。この違いは、§11(Point
Overlap QA流用可否)・§12(Tensionの見つけ方)の設計に直接影響する: News/Trendの
Counter-signalルールは「反証Evidenceがあるか」を機械的に問えるが、Voicesの
Tensionは「なぜこの立場はこう考えるのか」という価値観・前提の掘り下げであり、
Evidence単体では判定できない(§12)。

---

## 4. Case Storyとの違い(境界のみ、本格設計はしない)

タスク範囲外のため本格設計はしないが、境界を明示する。既存資産に「Case Story」という
用語は存在しない(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS全文grepで0件、5 Editorial Type
構想自体が[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§2で「用語がリポジトリのどこにも存在しない、まったく新しい設計軸」と確認済み)。
想定される境界のみ記す: Case Storyが「単一の主体・具体的事例を深く追う」型だとすれば、
Voicesは「複数の主体を横断的に比較する」型であり、**主語の数**(単数 vs 複数)が
構造上の一次的な分岐点になると推測される。この点はB Family内の別Editorial Type設計
タスクで別途検討すべき事項であり、本Reportでは深入りしない。

---

## 5. B Family共通骨格の初期案

**A Family既存資産の根拠**:
- 現行4slot構造(Title/Main Story/`###`×2/`## In one line`)は、Point数=2という制約が
  `split_common_sections_for_point_qa()`の`h3_matches != 2`判定([er003_v1_n3_01_articles_generate.py](er003_v1_n3_01_articles_generate.py)、
  [ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md](ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md)
  §5「`###`見出し=ちょうど2つという制約」)だけでなく、**今回新たに確認した
  `er011_point_role_value_planning_01.py::run_point_role_planning()`/`run_point_value_qa()`
  (`point_one`/`point_two`の2キー固定、`_value_qa_item_schema()`、`er003_v1_n3_01_articles_generate.py`
  707-750行目付近で`sections_for_value_qa["point_one_body"]`/`["point_two_body"]`を直接参照)**
  にも同様に2固定でハードコードされている。Point Role Planning・Point Value QAは
  2026-09-04以降にProduction配線された比較的新しい機構であり、ER-010-01調査時点
  (2026-08-31)にはまだ存在しなかったため、ER-010-01の「2固定の依存箇所」一覧には
  含まれていない。**B Family設計はこの追加の2件も含めて依存箇所を数える必要がある**。
- 11パート音声構造(A2: Preview→KP→Comment1→FSP1→Comment2→FSP2→Comment3→
  PointOne→PointTwo→Comment4→In One Line、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
  §2)も同じ「本文1+Point2+結び1」という物理構造を前提とする。

**提案**: Voice数固定禁止という指示自体を尊重し、B Family共通骨格は「Question/Hook
(短い導入)+ 可変数のVoice section(2〜4)+ Tension section(独立、任意で統合可)+
Closing(一段深い着地)」という**Neutral Blockベースの新骨格**を初期案とする。
A Family骨格をそのまま流用するのではなく、以下の理由でA Familyとは別骨格が必要と判断する:

1. **物理的制約が2固定である**こと自体(§5冒頭の3つの依存箇所)が、タスクが明示的に
   禁止する「Voice数固定」と正面から矛盾する。A Family骨格をそのまま使う限り、
   3〜4 Voiceは技術的に不可能。
2. Reference Example 2本(Voice数2/4)が示す通り、Tensionは独立したsection
   (Reference Example 1の§4「Tension」、Example 2の§6「Tension」)として立つ方が、
   「各Voiceの奥にある前提の違い」を明示的に言語化しやすい。A Familyには
   Tensionに相当するslotが存在しない(Point One/Twoはいずれも「本文への追加視点」で
   あり「立場同士の緊張関係」ではない)。
3. Evidence sectionを独立させる設計(Reference Example双方の§5/§5相当箇所)も
   A Familyには存在しない概念であり、後述§8で詳述する。

Point Role Planning/Point Value QA/Audio Validation Gate必須segmentは、いずれも
**Voice数が可変になった時点でコード変更が必須**になる(§7で詳述)。したがって
「中間section数」は「Voice数(2〜4)+固定section(Question/Tension/Closing)」という
可変長構造として設計し、Evidenceは独立sectionにするか各Voiceに分散するかを
記事ごとに選べる設計とする(§8)。

---

## 6. Voices固有Focus Moduleの初期案

**A Family既存資産の根拠**: 4層構造は`Layer1 Common Writing Contract`(全Editorial Type
共通、Fact Ledger制約・Spoken-first数字ルール等)/`Layer2 Family Common Skeleton`
(Family内共通の物理構造)/`Layer3 Focus Module`(Editorial Type固有の役割定義・
Narrative美学)/`Layer4 Article-specific Inputs`(Topic/Ledger/Title)という設計
([OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md) §1)。

**提案(Prompt文言は案であり正式化しない)**: この4層をB Familyへ適用する場合、
Layer1(Fact Ledger制約・Spoken-first数字ルール・Model Routing等)はそのまま全Family
共通で流用可能(§14で詳述)。ただしLayer2は「B Family Common Skeleton」として
A Familyとは**別に**定義する必要がある(§5の結論)。Layer3 Voices Focus Moduleの
位置づけとしては:

- Master記事模倣に相当する仕組み(阪神記事スタイル参照、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
  §3)は、Voices用に別サンプルが必要(Reference Example 2本はそのまま正式サンプルには
  しない、というタスク指示と整合させ、模倣元は別途ユーザーと相談して選定するか、
  模倣方式自体をやめてrole説明文のみに頼るかを検討課題として残す、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
  §10 Open Question 3と同じ論点がB Familyでも再発する)。
- Voices Focus Moduleが持つべき指示の骨子(案): (a) Voice数はResearch結果に応じて
  2〜4の範囲で選ぶ(固定しない)、(b) 各Voiceは「その立場なら確かにそう見える」形で
  描く(反論のための藁人形にしない)、(c) Voice同士は異なる利害・前提・価値観を
  持つよう設計し、単純な「賛成/反対」の言い換えにしない、(d) Tensionは意見の
  違いそのものではなく、その違いを生む前提・利害・価値観・問いの立て方の違いを
  指す、(e) 着地(Closing)は「誰が正しいか」を決めず、一段深い理解を提示する。

---

## 7. Voice数可変の構造設計

**A Family既存資産の根拠(2固定のハードコード箇所、§5の再掲+新規発見分)**:

| コンポーネント | 2固定の実装 | 出典 |
|---|---|---|
| `split_common_sections_for_point_qa()` | `h3_matches != 2`ならNone | `er003_v1_n3_01_articles_generate.py`(ER-010-02 §5) |
| `section_word_counts()` | `point_one`/`point_two`固定2キー | `er003_v1_spoken_first_01_r1_generate.py`(ER-010-01 §4) |
| `SharedPointBlueprint` | `PointBlueprint`×2固定schema | `er008_shared_point_blueprint_01.py`(ER-010-01 §6.2、現状`blueprint=None`で未使用) |
| **Point Role Planning**(新規発見) | `_role_plan_item_schema()`の構造化出力を`point_one`/`point_two`として`build_role_planning_block()`へ渡す | `er011_point_role_value_planning_01.py` |
| **Point Value QA**(新規発見) | `_value_qa_item_schema()`の`properties`が`point_one`/`point_two`の2キー固定 | 同上、`er003_v1_n3_01_articles_generate.py`707-750行目付近の呼び出し |
| Audio Validation Gate必須segment | `point_one_heading`/`point_two_heading`等2つの固定名 | `er003_v1_n3_01_assemble.py`(ER-010-01 §4) |
| TTS/Disfluency QA | segment名`point_one`/`point_two`に名称依存 | `er003_v1_n3_01_tts_generate.py`(ER-010-01 §4) |

**提案**: 上記7箇所すべてがVoice数=2の場合はA Family既存Discovery/Whyと**技術的に
同じ物理slot数**に収まるため、コード変更ゼロで転用できる([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§6.2の結論と一致)。**3〜4 Voiceにする場合は上記7箇所すべてに構造拡張が必要**であり、
これは前回タスクの結論(「Voices Trial 1は2 Perspectiveに限定してPipeline変更を回避
する」)よりも影響範囲が広がっている(Point Role Planning/Point Value QAという2機構が
2026-09-04以降に新規追加されたため)。

段階的Trial設計案:
1. **第1段階(推奨)**: Voice数=2に限定したTrialから開始し、上記7箇所を無改造で
   転用する(§16のTrial設計もこの前提)。
2. **第2段階**: Voice数=2固定でも「単純な賛成/反対にしない」というユーザー意図を
   満たせることを確認できた段階で、3〜4 Voiceへの構造拡張(上記7箇所の一般化)を
   別タスクとして計画する。

音声化時の尺との関係: Voice数が増えるほど、記事全体語数目安(280〜420語、soft
range)の中でVoice1本あたりの割当語数が減る。Reference Example 2(4 Voice)は
Voice単体が約80〜100語程度で、Example 1(2 Voice)のVoiceが約120〜150語程度と
比較して短い。Point Value QA(「重複はしていないが新しい価値も無いPointを検知」、
[CURRENT_SPEC.md](CURRENT_SPEC.md)「QA / Human Review」節Evidence Compression近傍の
記載)は、Voice数が増えて1 Voice当たりの分量が減るほど「価値の薄いVoice」を
誤検知しやすくなるリスクがあり、Voice数可変を採用する場合はPoint Value QAの
判定基準もVoice数に応じて調整が必要になる可能性が高い(§16 STOP条件候補)。

---

## 8. Evidenceの扱い

**A Family既存資産の根拠**: Evidence Compression Editor(Lossless Editor、
`er003_v1_n3_01_evidence_compression_editor.py::run_lossless_editor()`)はWriter生成
**後**に動作し、記事全文blobに対してspoken layerのみを軽量化する構造非依存の実装
([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§4)。Fact Safety3段(Fact Checker/Ledger Deviation Checker v2/Directional Fact
Precheck)もすべて記事全文ベースで構造非依存([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§8)。

**提案**: Reference Example双方が「Evidence」を独立sectionとして持つ(Example 1
§5「A real article would test these perspectives against evidence」、Example 2は
Evidenceを各Voice内に埋め込む形)。3方式を比較する:

| 方式 | 利点 | 欠点 | Fact Safetyとの整合 |
|---|---|---|---|
| A. 独立section | Voice本文を「その立場ならどう見えるか」に集中させ短く保てる。TensionセクションがEvidenceを跨いで参照しやすい | 「Evidenceの後出し」感が出るリスク(Reference Example 1で実際に指摘されている構造上の弱点) | Evidence Compression Editorの適用対象が1箇所に集約でき、圧縮ロジックの再利用が最も単純 |
| B. 各Voiceへ分散 | 「その立場が何を根拠にしているか」が直接結びつき自然に読める(Reference Example 2の方式) | Voice同士でEvidenceの重複・粒度差が生じやすく、Point Overlap QA相当の判定が複雑化 | Ledger Deviation CheckerがVoiceごとに分散したFactを個別に追跡する必要があり、既存の記事全文一括チェックとの相性は問題ない(構造非依存のため) |
| C. Tensionへ統合 | 「なぜ立場が違うのか」の説明に直接Evidenceを使え、着地が強くなる | Tension部分が長くなりすぎるリスク、Voice本文の説得力が薄まる可能性 | 同上、構造非依存のため技術的な障害はない |

いずれの方式でも、Fact Checker・Ledger Deviation Checker v2・Directional Fact
Precheckは記事全文を渡すだけの設計のため**コード変更不要**([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§8「影響なし」)。ユーザー意図(「EvidenceはPerspectiveやTensionを成立させるために
使う」)と最も整合するのは方式B(各Voiceへ分散、根拠と立場を直接結びつける)だが、
Voice数可変(§7)と組み合わせると、Voiceが増えるほどEvidence分散量も増え記事全体が
冗長化しやすいというtrade-offがある。初回Trial(§16)では方式Bを基本としつつ、
Tension sectionでも横断的なEvidence参照を許容するハイブリッド(B+C)を推奨する。

---

## 9. ResearchからPerspectiveを選ぶ方法

**A Family既存資産の根拠**: 既存Research pipeline(`er006_pool_pilot_01_research.py`)は
Evidence Pack(`evidence_pack_schema()`)→Verified Fact Ledger(`vfl_schema()`)→
Verification(`run_stage_b4_verification()`、fact_idごとにVERIFIED/PARTIALLY_SUPPORTED/
AMBIGUOUS/REJECTED判定)という3段構成。加えて`run_exception_search()`が
Perplexity API(`PERPLEXITY_API_KEY`、`routing.require_provider("EXCEPTION_SEARCH",
"perplexity")`)による**独立した反証・例外探索**を行う仕組みが既に存在する。また
`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`§11で確認された既存Topic Package
(`topic_package_イラン_アメリカ_情勢_2026-07-14.py`)は、CONTESTED/SINGLE-SOURCE区分
(イラン側主張の未確認情報、国際海事機関の見解相違等)を既に持っている。

**提案**: 既存Research経路は「反証・例外」を探すために作られており(News/Trendの
Counter-signal用途)、これは「異なる立場」を探す目的とは近いが同一ではない。
`run_exception_search()`のクエリ設計を、単一の主張への反証ではなく「この事象について
誰が・どのような利害/経験/制度的立場から意見・データを持っているか」を問う形に
拡張すれば、既存のPerplexity経路をそのまま流用できる可能性が高い(新規API・新規
Providerは不要、既存`EXCEPTION_SEARCH`ロールのクエリ文言のみの変更で足りる設計)。
Perspective候補選定は次の順序を提案する: (1) Exception Search拡張で実在する立場・
発言・調査・企業事例・当事者経験を収集、(2) 各候補についてEvidence Pack同様の
Verification(VERIFIED/PARTIALLY_SUPPORTED/AMBIGUOUS)を実施、(3) Verification結果に
基づき「本当に存在する立場」のみを候補に残す(想像上の立場を除外)、(4) 候補間の
重複排除(§11)、(5) 「同じ事象を違う角度から見せるか」「Tension発見につながるか」
「なるほどを生むか」という質的基準(Evidence量だけで選ばない、タスク文書の
ユーザー意図と一致)で最終選択する。この(5)の質的基準は既存Validatorには存在せず、
人間レビューまたは新規LLM判定ステップが必要になる(§16のTrial設計で検討)。

---

## 10. 「単なる賛否紹介」にならないための設計条件

タスク文書のユーザー意図を踏まえ、以下を設計条件として提案する:

1. Voice数を2に固定しない(§7)、かつ2にする場合でも「賛成/反対」という対称的な
   ラベルをVoiceの見出しに使わない(Reference Example双方とも見出しは「誰の
   Voiceか」であり「賛成/反対」ではない)。
2. Voice同士は異なる**利害・立場の種類**(消費者/事業者/管理者/第三者等)から
   選ぶことで、同一の対立軸(例: 賛成派の強さ/弱さ)のバリエーションにならない
   ようにする。
3. Tension sectionを必須の独立section(または統合形)として持たせ、「意見紹介で
   終わらせない」ことを構造上強制する(§5の骨格提案)。
4. Closingで「どちらが正しいか」を判定させない指示をLayer3 Focus Moduleに明記する
   (§13で詳述)。
5. Evidenceは各Voiceの主張の飾りではなく、Tensionを成立させるための材料として
   選ぶ(§8のユーザー意図)。

これらはいずれもPrompt文言レベルの対応であり、新規Validatorコードを要求しない
(News/TrendのMode判定基準の設計思想、[OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)
§10「Prompt文言レベルの対応であり、新規Validatorコードは不要」と同じアプローチ)。

---

## 11. 「Perspective同士が似すぎる」ことを防ぐ方法(既存Point Overlap QAの流用可否)

**A Family既存資産の根拠**: Point Overlap QAは`lexical_overlap_ratio(text_a, text_b)`
という汎用実装で、閾値0.40はPoint-vs-Main Story(本文への言い換えでないか)の実データで
調整された値([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
§8)。今回`er003_v1_n3_01_articles_generate.py`707-780行目付近の実装を確認したところ、
現行は`point_one`/`point_two`双方の`before_overlap`(Main Storyとの重複)に加え、
`overlap_report.get("point_one_vs_point_two", {})`という**Point同士の比較**も既に
実装されていることを確認した(既存Discovery/Whyでも「Point One/Twoが互いに似すぎて
いないか」は既にチェック対象)。

**提案**: `point_one_vs_point_two`比較の仕組み自体は関数レベルで転用可能だが、
ER-010-01 §8が指摘する通り、閾値0.40はDiscovery/Why(Main Story言い換え検知)用に
調整された値であり、Voice同士(同じ話題を語るため自然に語彙が重なりやすい)へ
そのまま適用する保証はない。加えてVoice数が2を超える場合、比較ペアが
`C(n,2)`(n=Voice数)通りに増える(3 Voiceで3ペア、4 Voiceで6ペア)ため、
現行の「2ペアのみ」を前提にした実装は拡張が必要。初回Trial(Voice数=2限定)では
既存の`point_one_vs_point_two`比較をmonitoring専用(gateにしない)で流用し、
実データが集まってから閾値・Voice数拡張時のペア生成ロジックを再設計することを
推奨する(ER-010-01 §8の「Voices Trial 1ではmonitoring専用にとどめる」という
結論と同じ考え方を維持)。

---

## 12. Tensionをどう見つけるか

既存資産に「Tension抽出」に相当する機構は存在しない(News/TrendのCounter-signal
ルールは「反証Evidenceの有無」という機械的に問える設計だが、[OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)
§7、Tensionは「なぜ立場が違うのか」という前提・利害・価値観の掘り下げであり、
性質が異なる)。

**提案(手順案)**: 各Voiceの記述から以下4軸で「暗黙の前提」を抽出し、Voice間で
異なる軸を探すことをLayer3 Focus Moduleの指示として明文化する: (a) 何を測定・
評価の基準にしているか(例: Reference Example 1「コーヒー1杯の対価に何が含まれるか」)、
(b) 誰の利害を最優先しているか、(c) どのような価値観(効率/公平/自由/安全等)を
前提にしているか、(d) そもそもどのような問いを立てているか(同じ状況でも問いの
立て方が違えば結論も違う、Reference Example 2「remote versus officeが間違った
出発点かもしれない」)。この4軸抽出は現状Fact Ledgerの構造化データからは自動導出
できず、Writer(LLM)の解釈に依存する部分が大きい。Fact SafetyのInterpretation
scope(§13)との整合上、Tensionの記述自体はLedgerに含まれるFactの範囲内で
説明できる前提の違いに限定し、Ledgerにない新しい因果関係を創作しないことを
明記する必要がある。

---

## 13. 最後の着地を単なるsummaryにしない設計

**A Family既存資産の根拠**: In One Lineは「静かな要約」トーンとして設計されている
(Discovery/Why・News/Trend共通、[OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)
§2/§3)。Fact Safetyの「Interpretation scope」に相当する既存概念は、Ledger
Deviation Checker v2の`unsupported_new_claim`/`changed_certainty`/`changed_scope`
カテゴリ(Ledgerに書かれていない新しい因果・確信度・適用範囲の追加を検知、
[ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md](ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md)
§1-3)、および News設計で言及される「Evidence-bounded Interpretation」という
Layer1一般原則([OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)
§7)である。

**提案**: Voices ClosingをA FamilyのIn One Line(1〜2文の要約)とは異なる役割として
定義する。Reference Example双方の最終sectionは、単に「両方とも一理ある」と
要約するのではなく、Tensionから導かれる**新しい問い**(Example 1「コーヒーを
買うとき、他に何を買っているのか」)や**判断基準の転換**(Example 2「remote
vs officeではなく、何が同じ場所にいることで良くなるか」)を提示している。これは
既存のIn One Line設計(現象への一言理解)とは異なる役割であり、B Family Common
Skeletonでは「Meaning/Close」として別定義する(ER-010-01 §7でVoices向けに
既に示唆されている「勝者・正解を決めない、Perspectiveの違いから見えるものを
整理する」役割と一致)。この着地はLedger内のFactの範囲を超えて「一段深い意味」を
述べる必要があるため、既存のEvidence-bounded Interpretation原則との緊張関係が
生じる。**この緊張は本Reportでは解消しない**(Discovery/Why側でも同種の緊張が
Fact CheckerのREVIEW_REQUIRED指摘として現れている、[OPEN112_NO18_4LAYER_REVIEW_PACK_06.md](OPEN112_NO18_4LAYER_REVIEW_PACK_06.md)
§3-3)。Closingの「一段深い理解」は、Ledger内のFactが示す複数立場の**構造的な
違い**(前提・利害・価値観・問いの立て方)を言い換える形にとどめ、Ledgerにない
新しい因果関係・断定を創作しないことを明示的な制約とする。

---

## 14. A Family既存資産の分類(そのまま流用/要調整/B専用)

| 既存資産 | 分類 | 根拠(CURRENT_SPEC/コード該当箇所) |
|---|---|---|
| Common Writing Contract(Fact Ledger制約・Spoken-first数字ルール・語数目安の仕組み自体) | **そのまま流用** | `er003_v1_n3_01_articles_generate.py`188-216行目付近、[CURRENT_SPEC.md](CURRENT_SPEC.md)該当箇所、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md) §5-A |
| Storytelling First / No Jargon | **要調整**(参照自体が現行Prompt本体に存在しないDangling Reference、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md) §10 Item 7で既知バグとして記録。B Family導入時に併せて解消するか判断が必要) | `er009_diagnostic_full_retry_modules_12.py`83-84行目 |
| Fact Safety(Ledger/Deviation Checker/Fact Checker) | **そのまま流用**(記事全文blobに対する構造非依存実装) | `er002_ja_web_research_r3.py`、`er003_v1_en_direct_vfl_01_generate.py`、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md) §8 |
| Evidence Compression | **そのまま流用**(構造非依存) | `er003_v1_n3_01_evidence_compression_editor.py`、同上 |
| Point Overlap QA(閾値0.40) | **要調整**(比較対象は転用可能だが閾値はVoice用に再検証が必要、§11) | `er008_point_overlap_qa_18.py` |
| Point Value QA / Point Role Planning | **要調整**(2 Voice限定なら無改造転用可、3〜4 Voiceでは2固定schemaの拡張が必須、§5・§7) | `er011_point_role_value_planning_01.py` |
| Key Phrase選定・音声 | **そのまま流用**(確定済み最終本文から選ぶだけ、構造非依存) | [ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md) §4 |
| Preview/Comment生成 | **要調整**(Comment2「前半/後半回収」・Comment3「Points前振り」・Comment4「Points回収」はDiscovery固有の単一throughline前提、Voicesでは役割文言の再定義が必要) | `er003_v1_b1_scaffold_01_generate.py`、同上 §4・§7 |
| TTS/ASR Validator | **そのまま流用**(segment名ベースの機械QAで中身の意味に依存しない、2 Voice限定の場合) | `er003_v1_n3_01_tts_generate.py`、同上 §4・§8 |
| Human Review Lock | **そのまま流用** | [CURRENT_SPEC.md](CURRENT_SPEC.md)「QA / Human Review」節`HUMAN_REVIEW_LOCKED` |
| Assembly(Audio Validation Gate含む) | **そのまま流用(2 Voice限定)/要調整(3〜4 Voice)** | `er003_v1_n3_01_assemble.py`、同上 §4 |
| Master記事模倣(阪神記事参照) | **B専用**(Voices用の別サンプルが必要、または模倣方式自体の見直しが必要) | 同上 §4・§10 |
| Main Story/Point One/Two/In One Lineの役割定義文言そのもの | **B専用**(骨格自体が異なる、§5) | 同上 §5-B |

---

## 15. 最初の実Research Trial候補テーマ2〜3件

[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)の既存20 Topicを確認した。これらは
いずれもDiscovery/Why向けに選定された「単一の現象のなぜ」を問うTopicであり、
Voices向けの「実在する複数立場」を明示的に含む形では選定されていない。ただし、
**カフェの長時間滞在客テーマ(No.5「Cafes Are Rethinking the All-Day Customer」)は
Reference Example 1と主題が完全一致**しており、既存Ledger資産の流用可否を確認する
価値がある候補として記録する(ただしReference Example 1はmock記事であり、この
一致自体が「そのままVoices化してよい」ことを意味しない)。

- **候補A(Topic Master既存、No.5活用)**: 「カフェの長時間労働・学習利用」
  (顧客/店主/他の客、3 Voice想定)。POOL_TOPIC_MASTER.md No.5の既存Ledgerが
  Voices向けに転用可能かは未検証(Discovery/Why向けに収集されたFactのみの
  可能性が高く、店主側の経営データ・他の客の不満の実例等、追加Researchが
  必要な可能性が高い)。
- **候補B(Topic Master既存、No.7活用)**: 「固定席復活」(No.7「Assigned Desks
  Are Back in Some Offices」、`PLANNED`未生成)。在宅勤務を続けたい従業員/
  オフィス回帰を求める経営陣/新人育成担当という複数利害が[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
  §11 Step 4で既に候補として言及されており、日本の学習者にも身近(在宅勤務は
  日本でも一般的な話題)。
- **候補C(新規、Topic Master未登録)**: Reference Example 2そのものの主題
  「リモートワークをどこまで認めるべきか」。**Topic Master未登録のためこの
  採否はユーザー判断**(POOL_TOPIC_MASTER.mdはPool型20 Topic母集団の正式SSOTであり、
  本タスクで新規追加はしない)。候補Bと主題が重複するため、両方を採用する場合は
  差別化(候補Bは「固定席復活という制度変更」、候補Cは「リモート許容度という
  程度問題」)が必要。

いずれも日本の学習者にとって身近で、実在する複数立場のEvidence(企業事例・
調査・当事者発言)が取得できる見込みがあると判断したが、実際のEvidence充足度は
Research実行前のため未検証。

---

## 16. 最初のTrial設計案(実行しない、範囲・条件のみ)

- **範囲**: Voice数=2に限定(§7の第1段階)。候補Bまたは候補Aから1テーマのみ。
- **レベル**: B1のみ(A2併行は行わない)。理由: 新規Editorial Type導入初回は
  変数を絞るという既存の方法論([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
  §9 Delivery「全5 Editorial Typeを一度に作らず段階的に検証するのは妥当」と
  同じ考え方をB Family初回にも適用)、B1はA2より語数配分の柔軟性が高く
  Voice構造の検証に適する。
- **回数**: Article-onlyで1回(音声化は行わない、[OPEN112_NO18_4LAYER_REVIEW_PACK_06.md](OPEN112_NO18_4LAYER_REVIEW_PACK_06.md)
  の4層Discovery Trialと同じ「Article-onlyでまず記事内容を検証する」進め方)。
- **成功基準(案)**: (a) Fact Checker/Ledger Deviation Checkerが例外なく実行できる
  (構造非依存のため技術的失敗は想定しにくいが確認は必要)、(b) 2 Voiceが単純な
  賛成/反対の言い換えになっていない(人間レビュー、§10の設計条件を満たすか)、
  (c) Tension sectionが「意見紹介」で終わらず前提・利害・価値観の違いを言語化
  できている(人間レビュー)、(d) Closingが単なる要約になっていない(人間レビュー)。
- **STOP条件(案)**: Fact Checker`FAIL`(blocking、既存policy通り)、Ledger
  Deviation`LEDGER_DEVIATION`が2回のLocal Rewriteでも解消しない(既存機構の
  上限、§14「そのまま流用」の前提を守る)、Point Overlap QAが記事全体retry
  上限(既存`POINT_OVERLAP_ARTICLE_RETRY_MAX`)に達してもNGのまま。
- **TTS方式**: 音声化する場合は**Standard同期**([PM_GOVERNANCE.md](docs/pm/PM_GOVERNANCE.md)
  7-1のルールに従う、本Reportでは詳細を複製しない)。
- **コスト見込み**: 既存Discovery/Whyの4層Trial実測(A2/B1各1回、Writer1回+
  Diagnostic Full Retry最大2回+Evidence Compression+Fact Checker+Ledger
  Deviation、[OPEN112_NO18_4LAYER_REVIEW_PACK_06.md](OPEN112_NO18_4LAYER_REVIEW_PACK_06.md))
  と同程度のオーダー(記事生成のみ、数百円規模)を見込むが、Voice数2・Article-only
  ・B1のみという最小構成のため、既存Discovery Trial単体より低いコストになる
  見込み(実測はTrial実行時に確認)。
- 本節はいずれも**設計案の提示のみであり、実行は行っていない**。

---

## 17. ユーザー判断が必要な点の一覧(推奨付き)

1. **B Family Common Skeleton(§5)の採否**: A Familyとは別の可変長骨格
   (Question/Hook + 可変Voice + Tension + Closing)を新設することへの合意。
   推奨: 合意(A Family骨格の技術的制約[2固定]と正面から矛盾するため)。
2. **初回Trial(§16)のVoice数=2限定という制約への合意**: 推奨: 合意(既存7箇所の
   コード変更を避け、まず記事内容の質を検証することを優先)。
3. **初回Trialテーマ(§15候補A/B/C)の選定**: 推奨: 候補B(固定席復活、既存Topic
   Master内・複数利害が明確)。候補Cは新規Topic MasterエントリのためTopic選定
   ルート自体の判断が別途必要。
4. **Evidenceの扱い方式(§8のA/B/C)**: 推奨: B(各Voiceへ分散)を基本にTensionでの
   横断参照を許容するハイブリッド。ただし実際にドラフトして比較しないと判断は
   確定できない。
5. **Master記事模倣の扱い(§6・§14)**: Voices用の別サンプルを新規に用意するか、
   模倣方式自体をやめるか。推奨: 既存の類似論点([ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)
   §10 Item 3)が未解決のまま残っているため、初回Trialのドラフト2〜3案を比較して
   から判断する。
6. **Point Overlap QA/Point Value QAの初回運用方針(§11)**: 推奨: monitoring専用
   (gateにしない)、実データ収集後に閾値・基準を再設計。
7. **Storytelling First/No JargonのDangling Reference(§14)をB Family導入と
   同時に修正するか、別タスクにするか**: 推奨: 別タスク(本タスクの範囲外、
   既存OPEN Item化を検討)。
8. **4層構造自体(A Familyの前提)がまだ`APPROVED_FOR_PRODUCTION`でない状態で
   B Family設計を先行させてよいか**: 推奨: 設計(DESIGN)段階までは並行して問題ない
   (今回のタスクも実装は行っていない)が、B Familyの実Trial実行はA Family
   4層構造の採否確定(または独立採用の判断)を待つべきか、ユーザー判断が必要。

---

## 18. SSOTへ登録すべき内容(案)

以下はSSOT(OPEN_ITEMS.md等)への正式登録候補であり、**本タスクでは登録していない**
(タスク指示により後続タスクで実施)。

- **新規Open Item候補**: 「B Family Voices/Perspective設計(本Report)の採否」を
  `USER_DECISION_REQUIRED`としてOPEN_ITEMS.mdへ登録。参照先は本Report
  (`EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`)。
- **新規Open Item候補**: 「Point Role Planning/Point Value QAが2固定であること」を、
  既存のOPEN-113系(Point-context-only、`PRODUCTION_WIRED`)とは別の技術的制約として
  明示登録(将来Voice数可変化タスクの前提整理用)。
- **新規Open Item候補**: 「B Family用Research経路(Exception Search拡張によるPerspective
  収集)の設計・Trial要否」を`USER_DECISION_REQUIRED`として登録。
- **DECISION_LOG.md追記候補**: 本タスクの実施記録(読み取り調査+設計提案、
  Trial・Production変更なし)を、既存のER-010/OPEN-112系のエントリ形式に合わせて
  1エントリとして追記。
- **HISTORY_INDEX.md追記候補**: 本タスクの管理ID・日付・要旨を1行で追記。

---

**Status: DESIGN / USER_DECISION_REQUIRED — NOT VALIDATED, NOT APPROVED_FOR_PRODUCTION,
NOT PRODUCTION_WIRED, NO TRIAL EXECUTED**
