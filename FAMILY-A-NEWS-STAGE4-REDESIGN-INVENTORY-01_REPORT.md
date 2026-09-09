# FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01 報告書

管理ID: FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01(Lane A、News再設計前の
整理、Sonnet委任、**¥0 offline限定**)。**読み取り専用の棚卸し+既存出力の
再集計**。新規API呼び出し(embedding含む)なし。Production/Prompt/QA/
Validator/retryコードは一切編集していない(er008_point_overlap_qa_18.py・
er009_diagnostic_full_retry_modules_12.py・er011_point_role_value_
planning_01.py・er003_v1_n3_01_articles_generate.pyは読み取り専用grep/引用
のみ、閾値0.40・Loop Budget 2は無変更)。Git操作・SSOT編集・
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`編集は行っていない。並列稼働中の
Discovery Trial-10(`er011_output/discovery_stage4_*`)は参照・接触していない。

---

## 1. News Point品質の現状構造

構造図・14仕組みの責任表(#1〜#14、目的/発火タイミング/入力/出力/承認
Status/重複競合)は`FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01_
REPORT.md` §1に既に確定版があり、本タスクはこれをSSOT的リファレンスとして
そのまま引用する(重複作成しない)。要点のみ再掲:

- **担当軸は5つ**: 重複回避(Full Story対Point/Point対Point)・価値・役割
  分担・多様性・事実性。
- **語彙重複を3層で扱う**(Writer Prompt原則#1→lexical Overlap QA#6→
  Diagnostic Full Retry診断section#8)が、実質は「1つの判定基準(閾値
  0.40)をprompt/QA/feedbackの3箇所で反復提示している」構造。
- **cross_point_overlap(#7、Point One対Point Two)は計算されるがretry判定
  未使用**(OPEN-133、CURRENT_SPEC記載は`DEFERRED`へ訂正済み)。
- **Point Role Planning(#3)はFocus Module(#4)を一切受け取らない**(コード
  確認済み、両者は独立した役割決定経路)。
- **retryは記事全体の非決定的な再生成**であり、lexical/value QAが同時に
  flagされた場合の「両方を同時に解消する保証」は構造上ない(§2-3で実データ
  実証、「もぐらたたき」)。

**E: retry段階の責務(何を固定し何を変えるか、現行コードの事実ベース)**

| 構成要素 | retry時に固定されるもの | retry時に変わるもの | 事実/推測 |
|---|---|---|---|
| Overlap診断section(#8、G1修正済み) | テンプレート文言、shared_words算出ロジック、前回Full Story全文、前回Point One/Two本文(G1修正後は実テキスト) | (次attemptの)算出値そのもの | 事実(コード確認済み) |
| Value QA診断メモ(#9) | `value_qa_flagged`時のみ追加という条件 | fail_fields/reasoningの内容 | 事実(コード確認済み) |
| Point Role Planning再抽選(#3) | 入力は`topic, verified_ledger_text`の2引数のみ(初回と完全同一、診断結果非依存の「盲目の再抽選」) | role/evidence_anchor/why_it_matters/重複禁止事項が独立LLM呼び出しとして毎回作り直される | 事実(コード確認済み、Stage1(g)) |
| Full Article再生成(Writer呼び出し) | topic, Verified Fact Ledger, Focus Module block(あれば), Prompt原則, 新しいRole Planningブロック, 診断section | Main Story全文・Point One/Two本文が非決定的LLM出力として毎回作り直される(Point単位の局所編集ではない) | 事実(コード確認済み) |
| Loop Budget(#11) | 上限2回(`POINT_OVERLAP_ARTICLE_RETRY_MAX`) | - | 事実 |

「Role Planningが診断結果を見ずに毎回作り直され、しかも診断sectionより
後ろに『必ず従うこと』という強い命令形で連結される」ことと、「Full
Article再生成が非決定的である」ことの組み合わせが、lexical/value QAの
「もぐらたたき」(§3-3参照)の構造的な土台になっていると考えられる
(**解釈**、Reconciliation Gate Report §2-3/§3-Gの解釈を踏襲)。

---

## 2. 既存証拠一覧(棚卸し)

| 資料 | 位置づけ | 主要な既存結論 |
|---|---|---|
| `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04_REPORT.md` | Hanshin、G1修正前、baseline/focus N=6ずつ | baseline NG 66.7%(4/6)、focus 50%(3/6) |
| `FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06_REPORT.md` | Hanshin、G1修正後、baseline/focus_hint N=6+hint_only N=2(bonus) | baseline NG **100%(6/6)**、focus_hint 50%(3/6)。G1修正後baselineがG1修正前より悪化して見える(原因未切り分け) |
| `FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md` | Hanshin gapfix(G1のみ実装)+Theme2 baseline/gapfix、N=2〜3 | G1のReconciliation判定=実装漏れ(承認済み範囲内)。NG 12本中5本(42%)はG1対象外原因(Value QA単独3件、Fact Checker FAIL 2件)。gapfix側に劇的収束例が複数あるが非単調な例も残り統計確定不可 |
| `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md` | CAR-T(新テーマ、mechanism/limitation構造)、focus_hint N=2×2レベル | 最終NG **0%(0/4)**。初期flag率(2/4=50%)はHanshin/Theme2と同水準だが、retry後の最終解消率は本Trial4/4に対しHanshin focus_hint3/6と題材依存の示唆。B1B full pipelineはTTS ASR NGでHUMAN_REVIEW_REQUIRED、Assembly `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で正常STOP |
| `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md` | Part A: value単独NG時にoverlap診断を条件分岐(N=6)、Part B: 閾値0.40の分布位置(¥0、既存240件) | Part A: **REJECTED**(NG率50%→83.3%、attempt数1.50→1.83、連鎖率改善なし=悪化方向で一致)。Part B: 閾値0.40は分布の57.92パーセンタイル、境界帯(±1語)に全観測の25%が集中するが、Focus系改善の実質性は境界効果に大きく依存しない(10〜28%) |
| `FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01_REPORT.md` | 14仕組みの構造図、重複・競合・不足の判定、Trial-06 NG原因分解A〜I | 語彙重複3層扱い、Role Planning/Focus Module役割決定二重化リスク、Value QA/Overlap QAの相互排他性欠如(もぐらたたき実証)、cross_point_overlap統合不足、Discovery Role収束の実例 |
| `FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01_REPORT.md` | Opus診断レビュー(Fable転記要旨) | もぐらたたき仮説は主因でない(flagされ続けているだけ)、Point長交絡はTrial-05のみ支持、Role Planning-Focus Module因果経路なし、G1語彙プライミング仮説は要検証 |
| `FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md` | Opus指摘の¥0再集計・完全再現確認 | overlap_ratio分母は異なり内容語数(1語≈0.037)。cross_point_overlap全240件平均0.1311・閾値0.40超0件。value単独NG→次attempt新規lexical flag率はTrial-06限定2/2(100%)だが全Trial合計4/9(44%)。Role Planning初回・retryとも同一2引数のみ(盲目の再抽選)確認 |
| OPEN-133/OPEN-134(OPEN_ITEMS.md) | cross_point_overlap統合未実装(SSOT記載訂正済み)/Point Overlap NG観測(Exit条件A-UDR-22、20 run観測中、現在2 run消化) | 分母固定化案(D_fixed=30)試算は現行より厳しい方向(flag率+5.4〜5.8pt)、採用せず |
| OPEN-135(Family A Completion Program) | News/Discovery Focus Module+Point Role hintの**現行Production採用案は不承認**(Focus Module/Point Role自体はREJECTEDではない) | 本タスクの直接の背景(「現状最良で採用判断へ戻す」ではなく広く再検討) |

---

## 3. ¥0再集計結果(offline recompute、本タスク新規実施分)

**方法**: 既存Trial出力(Hanshin Trial-04/06、Theme2 Trial-05 gapfix、
CAR-T Trial-09、Stage2 branch Trial-08、計48 run・248 Point-attempt観測)
を`point_overlap_article_retry_log.json`から読み取り、`er008_point_overlap_
qa_18.py`のtokenizerロジック(`_content_words`/`lexical_overlap_ratio`)を
読み取り専用で再実装(Production関数のimport実行なし、閾値0.40は無変更)。
script: `er011_news_stage4_redesign_inventory_01.py`(root)。出力:
`er011_output/news_stage4_redesign_inventory_01/`
(`stage4_recomputation_results.json`、`point_attempt_observations.csv`、
`fp_classification_all_flagged.json`、`fp_classification_sample.md`)。

**topic_structure定義**(題材の構造で3分類、目視+コード上のtheme確認):
`single_event_boxscore`=Hanshin(単一試合スコアライン、数値・固有名詞密度高)、
`survey_trend`=Theme2(複数調査の統計比較、Trend Synthesis mode)、
`mechanism_limitation`=CAR-T(単一研究発表、mechanism/limitation構造)。

### 3-1. (C) 閾値0.40の再評価材料

topic_structure×level×initial/retryのflag率・平均overlap:

| topic_structure | level | phase | n | flag率 | 平均overlap | 平均Point語数 |
|---|---|---|---|---|---|---|
| single_event_boxscore | A2 | initial | 36 | 58.3% | 0.413 | 28.3 |
| single_event_boxscore | A2 | retry | 64 | 45.3% | 0.376 | 27.8 |
| single_event_boxscore | B1B | initial | 36 | 52.8% | 0.411 | 30.0 |
| single_event_boxscore | B1B | retry | 58 | 37.9% | 0.380 | 30.9 |
| survey_trend | A2 | initial | 8 | 75.0% | 0.473 | 33.5 |
| survey_trend | A2 | retry | 12 | 25.0% | 0.329 | 38.3 |
| survey_trend | B1B | initial | 8 | 62.5% | 0.399 | 35.6 |
| survey_trend | B1B | retry | 10 | 40.0% | 0.381 | 36.0 |
| mechanism_limitation | A2 | initial | 4 | 25.0% | 0.310 | 38.5 |
| mechanism_limitation | A2 | retry | 4 | 25.0% | 0.268 | 36.5 |
| mechanism_limitation | B1B | initial | 4 | 25.0% | 0.327 | 34.5 |
| mechanism_limitation | B1B | retry | 4 | 25.0% | 0.300 | 38.75 |

topic_structure全体: single_event_boxscore flag率46.9%(n=194)、
survey_trend 47.4%(n=38)、mechanism_limitation 25.0%(n=16、既にN小)。

**flag例のFP候補仮分類(ルールベース、正解ラベルなしの仮分類と明記)**:
flag=True全113件について、`shared_words`中の固有名詞・数字語(語中頭文字
大文字化率≥50%の語+spelled-out数詞)の比率が0.5以上を「必要な固有名詞・
事実語の再利用候補」、それ未満を「意味の重複候補」と機械仮分類した:
- **全体FP候補率(ルール仮分類、厳格な多数決基準): 1.77%(2/113件)**
  (topic別: single_event_boxscore 2/91、survey_trend 0/18、
  mechanism_limitation 0/4)。
- 代表11件の目視(`fp_classification_sample.md`)では、single_event_
  boxscoreのentity_ratio 0.23〜0.33程度の中間的な件でも
  `hanshin/hiroshima/montero/ihara`等の固有名詞+`home/run/solo`等の
  試合描写語が混在しており、「意味の重複」と「固有名詞の必要な再利用」が
  **明確に分離できない**目視結果だった(box-score型は実況描写自体が
  固有名詞・数値密度が高いため)。survey_trendの代表例はentity_ratio
  0(固有名詞・数字語なし)で、`survey/travel/trip/week`等の一般語による
  重複であり、目視でも「意味の重複」寄りに見えた。

### 3-2. (B) 固有名詞・数値語を分子から除外した代替指標(Trial限定、Production Checker無変更)

同一分母(`point_word_count`、既存Production値)のまま、`shared_words`から
固有名詞・数詞を除いた場合の再計算(既存retry logの数値のみで再構成可能な
「分子のみ調整」版、attempt別のPoint/Full Story全文は最終attempt以外
保存されていないため分母側の完全再トークン化は不可、限界として明記):

| 区分 | n | 元の閾値0.40 flag率 | 固有名詞・数値除外後 flag率 |
|---|---|---|---|
| 全体 | 248 | **45.56%** | **13.31%** |
| single_event_boxscore | 194 | 46.91% | **7.73%** |
| survey_trend | 38 | 47.37% | 39.47% |
| mechanism_limitation | 16 | 25.00% | 18.75% |

flag解除(True→False)80件・新規flag(False→True)0件(分子のみ減らす調整の
性質上、新規flagは原理的に発生しない)。

**相関(全248観測)**: Point語数 vs overlap_ratio = **-0.133**(Stage1(a)の
-0.192と同方向、弱い負の相関、再確認)。shared_words中の固有名詞・数値語数
vs overlap_ratio = **+0.415**。「evidence density」(固有名詞・数値語数/
Point語数) vs overlap_ratio = **+0.461**(中程度の正相関、固有名詞・数値
密度が高いPointほどoverlap_ratioが高く出やすい)。

**事実と解釈の分離**: 「固有名詞・数値を分子から除くとsingle_event_
boxscoreのflag率が46.9%→7.7%へ劇的に下がる」のは**再計算上の事実**。
一方、3-1の目視結果(固有名詞と意味重複が混在し分離できない)を踏まえると、
「この劇的な低下=すべてFalse Positiveの是正」と解釈するのは**過大解釈**
であり、単純な固有名詞除外は「box-score型記事の実況描写そのものに必要な
語彙」も一緒に取り除いてしまっている可能性が高い(**解釈、断定しない**)。

### 3-3. (D) 代替指標候補の設計比較表(実装せず、embedding計算なし)

| 候補指標 | 概要 | 長所 | 短所・リスク | ¥0で検証可能か |
|---|---|---|---|---|
| 現行(lexical overlap coefficient、閾値0.40) | Point内容語のうちFull Story出現語の比率 | 既存、決定的、¥0、実データあり | box-score型で固有名詞・数値と意味重複を区別できない(3-1/3-2) | - |
| 固有名詞・数値除外overlap(本タスクTrial指標) | shared_wordsから固有名詞・数詞を除いた比率 | box-score型の過検知を軽減する可能性 | 分母未調整の限界、box-score型で「実況描写の必要語」も除去しうる過大補正リスク | 部分的に可(本タスクで実施済み、分母側は不完全) |
| semantic similarity(embedding) | Point/Full Story文をembeddingしcos類似度 | 言い換えの意味的検知に強い、固有名詞問題を自然に緩和しうる | **API課金必須**(¥0では実施不可)、閾値再設計が必要、Production Checker置換は大規模変更 | 不可(本タスク範囲外) |
| necessary factual overlap除外(Ledger由来語をLedger自体から抽出して除外) | Ledgerの固有名詞・数値をLedger原文から機械抽出し除外(本タスクの capitalization heuristicより正確) | 「そのテーマのLedgerが定義する必須事実語」を正確に特定できる | Ledger構造がテーマごとに異なり汎用抽出ロジックの設計コストが中〜大 | 部分的に可(¥0、Ledger jsonの読み取りのみ) |
| evidence anchor単位の指標 | Point Role Planningの`evidence_anchor`(Ledger内Factへの参照)単位で重複を測る | 役割計画(#3)の出力と直接連動、Fact由来の重複を意図的に許容できる | `evidence_anchor`はテキストの自由記述でありLedger Factへの機械対応が必要(現状フィールド定義に厳密なID紐付けなし) | 限定的(既存出力の目視突合のみ、¥0) |
| heading/body分離指標 | Point見出し(`###`行)とbody本文を別々に重複判定 | Trial-06のrole分類がPoint見出し寄りの言い回しを含むため、body側の純度を測れる可能性 | 見出しとbody一体で意味を成す設計との整合、閾値を2つ持つ複雑化 | 可(¥0、既存article.mdの見出し/body分割のみ) |
| point-to-story vs point-to-point別指標 | 現行のPoint対Full Story(#6)とPoint対Point(#7、cross_point_overlap)を別々に閾値運用 | 既にcross_point_overlapは計算済み(#7、未使用)、多様性軸として活用余地(OPEN-133と接続) | retry判定への統合はOPEN-133で`USER_DECISION_REQUIRED`のまま(閾値変更に該当しうる) | 可(¥0、既存データの分布比較のみ、Stage1(d)で実施済み) |

### 3-4. (G) topic_structure別の差(定量化)

| topic_structure | n runs | 初回attempt flag率(いずれかのPointがlexical/value flag) | 最終NG率(全体) | 最終NG率(baseline条件) | 最終NG率(treatment条件) | retry平均 | 真の入れ替わり率(true swap/transitions) |
|---|---|---|---|---|---|---|---|
| single_event_boxscore(Hanshin) | 36 | **91.7%** | **72.2%** | 83.3%(n=12) | 66.7%(n=24) | 1.69 | 11.5%(7/61) |
| survey_trend(Theme2) | 8 | 87.5% | 50.0% | 50.0%(n=4) | 50.0%(n=4) | 1.38 | 18.2%(2/11) |
| mechanism_limitation(CAR-T) | 4 | 50.0% | **0.0%** | (baseline条件なし、focus_hintのみ) | 0.0%(n=4) | 1.00 | 0.0%(0/4) |

**事実**: 初回attempt flag率は3構造とも50〜92%と高く(題材によらず
retryは高頻度で発火するというTrial-09の既存示唆と整合)、一方で最終NG率は
0%〜72%と構造間で大きく異なる。真の入れ替わり(もぐらたたき)率も
single_event_boxscore/survey_trendでは10〜18%観測されるがmechanism_
limitationでは0件(N=4と極小標本のため断定不可)。

**解釈上の注意(交絡)**: この比較はcondition構成が完全に揃っていない
(CAR-Tはfocus_hint条件のみでbaseline無し、single_event_boxscoreは
baseline/focus/focus_hint/hint_only/gapfix/branch_diagnosticの6条件・
N=36と最大母数、survey_trendはbaseline/gapfixのみ)。CAR-Tの0%はN=4の
小標本かつfocus_hint条件限定であり、Trial-09自身が明記する通り
「断定的な結論ではなく方向性の示唆」の域を出ない。

---

## 4. 改善候補(優先順位付き、3〜5件)

**優先順位1: 診断feedbackへの「トレードオフ回避」明示指示の追加(領域D/E)**

**優先順位2: Role Planning再抽選への診断結果フィードバック接続(領域E)**

**優先順位3: topic_structure(題材構造)を考慮したNews題材選定ガイダンス(領域H/G)**

**優先順位4: Ledger由来語ベースのnecessary factual overlap除外指標の精緻化(領域B/C/D、閾値変更ではなく観測指標としてまず追加)**

**(参考、再提案しない)条件分岐によるoverlap診断構築の変更(領域C)**: 既に
`FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08` Part AでN=6実測し
**REJECTED**(NG率50%→83.3%悪化、全指標が悪化方向で一致)。新たな証拠なしに
再提案しない。

---

## 5. 各候補の根拠・反証・リスク・コスト・最小Trial設計

### 候補1: 診断feedbackへの「トレードオフ回避」明示指示

- **原因仮説**: §2-3(Reconciliation Gate Report)・Stage1(b)(c)で実証
  された「もぐらたたき」(lexical/value QAが交互にflagされる)は、記事
  全体を再生成する設計上、Writerが一方の指摘を直そうとしてもう一方を
  再発させることに起因する可能性がある。現行の診断文言はどちらの軸も
  「直すべき理由」を提示するが、「両方を同時に満たすこと」という
  明示的な制約文言は無い(Stage1(b)(c)、Reconciliation Gate §2-3で
  コード確認済み)。
- **既存証拠**: Stage1(b) 真の入れ替わり全Trial合計7件、Reconciliation
  Gate §2-3の3例全例で軸の入れ替わりが実データ確認済み。
- **反証・留保**: Trial-08 Part Aは「診断構築を条件分岐する」という
  **別の変更**(overlap診断section自体を削除する分岐)を検証しREJECTEDと
  なった。これは「情報を削る」方向の変更であり、本候補(情報を追加する
  方向)とは正反対の変更のため、Trial-08のREJECTED判定は本候補への直接の
  反証にはならない。ただしTrial-08の結果(情報を減らすと悪化)は、
  「診断feedbackの量や質を変えること自体がWriterの非決定的な出力に
  敏感に影響する」ことを示しており、新たな文言追加もまた予測しにくい
  副作用を持ちうるという間接的な警告材料になる。
- **期待効果**: 不明(未検証)。真の入れ替わり率(全Trial合計7/120≒5.8%、
  Stage1(b))の低下が期待値だが、確証はない。
- **リスク**: Prompt文言追加はProduction Prompt変更(承認要)。役割固定化
  リスクは低い(役割自体には触れない文言)。安全側指標(Fact Checker/
  Ledger Deviation)への影響は未検証。
- **Productionへの波及範囲**: `er009_diagnostic_full_retry_modules_12.py`
  の`DIAGNOSTIC_SECTION_TEMPLATE`および/または`build_value_qa_diagnostic_
  note`文言追加のみ(既存関数の呼び出し構造・条件分岐は無変更)。
- **cost見積**: 1記事あたり追加課金なし(prompt文言の追加のみ、トークン数
  微増)。量産時: 無視できる程度のトークン増(数十トークン)。retry増減:
  不明(効果次第で減る可能性、悪化すれば増える可能性)。運用負荷: 低
  (既存の診断構築ロジックへの追記のみ)。
- **最小Trial設計**: (1)¥0: 既存retry logの「もぐらたたき」該当ケースの
  診断promptを目視し、追加すべき文言の具体案を作る。(2)harness最小比較:
  Trial-08と同型のharness(N=6、focus_hint固定)でcurrent_diagnostic vs
  トレードオフ回避文言追加版を比較(費用目安¥40〜60、Trial-08 Part Aと
  同水準)。(3)少数N runtime: 比較結果がVALIDATED方向ならN=10程度で再現性
  確認。
- **STOP条件該当**: 該当なし(閾値・QA定義・11-part構成・Point数・新
  subtype/mode・新規必須Validatorのいずれも変更しない、Prompt文言のみ)。
  ただしProduction Prompt変更自体はユーザー承認(`APPROVED_FOR_
  PRODUCTION`)が必要。

### 候補2: Role Planning再抽選への診断結果フィードバック接続

- **原因仮説**: Stage1(g)・Reconciliation Gate §2-3(G)で確認された
  「Role Planningは診断結果を一切見ない盲目の再抽選」が、retry間で
  役割自体が変わってしまい、新しい役割設計が新しい語彙重複または価値
  不足を生む一因になっている可能性。
- **既存証拠**: Stage1(g)でコード確認済み(初回・retryとも同一2引数のみ)。
  Reconciliation Gate §3-Gが「役割の再計画自体は前回の失敗を踏まえた
  診断sectionを見て行われるが、診断は主にlexical軸の情報」と指摘。
- **反証・留保**: Discovery Layer3 Trial-07のRole収束問題(mechanism/
  myth_correctionへの100%収束)はStage1(e)で「Focus Moduleとの因果経路が
  コード上存在しない」ことが確認済みであり、真因は依然不明。Role
  Planningへ診断結果を渡す変更が収束問題を解決する保証はない
  (Stage1 UDR候補(iv)がこの限界を既に明記)。
- **期待効果**: 不明(Stage1 UDR候補(iv)と同じ判定、効果を予測する根拠が
  無い)。
- **リスク**: 役割固定化・多様性喪失のリスクは、診断結果(=前回の失敗
  パターン)へRole Planningが過剰適応すると、むしろ役割の選択肢が狭まる
  可能性がある(候補1と同様、予測しにくい副作用)。
- **Productionへの波及範囲**: `run_point_role_planning()`のシグネチャ
  変更、呼び出し元2箇所(初回・retry)の整合、既存単体テスト
  (`er011_test_point_role_value_planning_01.py`)の更新。
- **cost見積**: 1記事あたり追加課金は僅少(promptへ診断結果の要約を追加
  する程度)。量産時: 無視できる程度。retry増減: 不明。運用負荷: 中
  (Role Planning関数のシグネチャ変更は他の呼び出し元との整合確認が必要)。
- **最小Trial設計**: (1)¥0: 現状のRole Planning呼び出し構造の詳細diff案
  作成。(2)harness最小比較: N=6(Hanshin focus_hint固定)でRole Planning
  診断非依存版 vs 診断結果を渡す版を比較(費用目安¥40〜60)。(3)少数N
  runtime: role分類の多様性(Reconciliation Gate §3-Iのキーワード分類
  ヒューリスティックを流用)も同時に集計し、多様性喪失の副作用有無を
  確認。
- **STOP条件該当**: **関数シグネチャ変更(新規引数追加)に該当する可能性
  あり**。retry方針の変更に近いため、Trialでの検証後、Production配線判断
  時にSTOP条件該当性を再確認する必要がある。

### 候補3: topic_structure(題材構造)を考慮したNews題材選定ガイダンス

- **原因仮説**: §3-4の定量化で、初回attempt flag率は題材構造によらず
  50〜92%と高いが、最終NG率は0%(CAR-T、mechanism/limitation構造)〜
  72.2%(Hanshin、single_event_boxscore)と大きく異なる。single_event_
  boxscore型(単一試合の実況)は、実況描写自体が固有名詞・数値密度が
  高く(§3-2、evidence density相関+0.461)、Point One/Twoが「別角度の
  掘り下げ」を作りにくい構造的な制約を持つ可能性がある。
- **既存証拠**: Trial-09自身が「mechanism(体内で直接CAR-T誘導する新方式)
  とlimitation(小規模第1相、大規模検証が必要)という、語彙がFull Story/
  Pointへ自然に分かれやすい構造」を選定理由に明記し、実際に最終NG
  0%を達成した。本タスクの§3-4集計はこれを48 run規模の集計で裏付けた
  (ただしCAR-TはN=4・focus_hint条件限定)。
- **反証・留保**: (1)CAR-TにはbaselineがないためFocus Module/hint効果と
  topic_structure効果が交絡している(Focus Moduleなしのbaselineで
  mechanism_limitation構造がどうなるかは未検証)。(2)N=4は極小標本
  (Trial-09自身が明記)。(3)Hanshinのような単一試合速報はNews Editorial
  Typeの主要な供給源の一つであり、「構造が不利だから避ける」という
  方針は、Newsカバレッジの多様性(スポーツ速報自体の価値)を損なう
  トレードオフを伴う。
- **期待効果**: 不明(方向性の示唆に留まる、Trial-09自身の限定)。
- **リスク**: 題材選定基準の変更はEditorial判断そのものへの介入であり、
  「特定の構造の題材を避ける/優先する」という方針は、報道範囲の偏り
  (スポーツ速報系Newsの扱い低下等)という別の質的リスクを生みうる。
  Fact Safetyへの直接リスクは低い。
- **Productionへの波及範囲**: コード変更は不要(Editorial判断・題材選定
  基準の追加のみ)。ただし将来Mode自動判定(OPEN-130、DEFERRED)を実装する
  場合の判定要素候補になりうる。
- **cost見積**: 追加API課金は基本的に無し(題材選定時の判断基準追加の
  み)。ただし比較のためのbaseline未検証(CAR-T)を埋めるTrialは¥100〜150
  程度必要。
- **最小Trial設計**: (1)¥0: 既存3構造のデータ(本タスクの集計)を用いた
  追加解釈。(2)harness最小比較: CAR-T Ledgerでbaseline(Focus Moduleなし)
  N=4程度を追加実行し、mechanism_limitation構造自体の効果とFocus Module
  効果を切り分ける(費用目安¥60〜80、Trial-09と同型)。(3)第3の
  mechanism/limitation型題材で再現性確認(N=4程度、費用目安¥60〜100)。
- **STOP条件該当**: 該当なし(コード変更を伴わない)。ただしNews題材選定
  方針自体の変更は編集方針判断でありユーザー承認が必要。

### 候補4: Ledger由来語ベースのnecessary factual overlap除外指標(観測指標としてまず追加、閾値運用はしない)

- **原因仮説**: §3-2で「固有名詞・数値を分子から除くとsingle_event_
  boxscore(Hanshin)のflag率が46.9%→7.7%へ劇的に下がる」ことを確認したが、
  §3-1の目視で「固有名詞と意味重複が混在し分離できない」ことも確認した。
  より正確には、Ledgerが実際に定義する固有名詞・数値(=記事が正確性の
  ために再利用すべき語)を、本タスクの粗い大文字化ヒューリスティックより
  厳密にLedger原文から抽出して除外指標を作れば、box-score型の過検知
  傾向をより精度良く切り分けられる可能性がある。
- **既存証拠**: §3-2(本タスク新規)、Trial-08 Part B(閾値0.40が分布の
  57.92パーセンタイル、境界帯に25%が集中するが、Focus系改善の実質性は
  境界効果に依存しない)。
- **反証・留保**: Trial-08 Part Bは既に「閾値・分母の変更を積極的に
  支持する根拠は弱い」と結論済み(D_fixed=30の固定分母化はflag率を
  +5〜6ptと逆方向に悪化させた)。本候補は閾値変更ではなく**観測指標の
  追加**(Production Checkerの判定自体は変えない)に限定することで、
  この既存の否定的結論と矛盾しない設計にする必要がある。
- **期待効果**: 不明(観測指標としての精度向上が主目的、NG率そのものを
  下げる効果を主張しない)。
- **リスク**: 「NG率だけを下げる目的化」に陥らないよう、本候補は
  **Production Checkerの閾値・判定ロジックには一切触れない**観測指標
  追加に限定する。閾値変更を伴う派生案が出た場合はA-UDR-7・OPEN-134の
  整合確認と別途のUDRが必要。
- **Productionへの波及範囲**: 無し(観測指標はTrial/分析スクリプト側に
  留める)。
- **cost見積**: ¥0(既存Ledger jsonの読み取りのみ)。
- **最小Trial設計**: (1)¥0: 既存3テーマのLedger(Hanshin/Theme2/CAR-T)から
  固有名詞・数値語を機械抽出し、本タスクの大文字化ヒューリスティックとの
  一致率を確認、より精密な除外指標を再計算(追加API呼び出し不要)。
  これのみで完結可能、harness実行や少数N runtimeは不要。
- **STOP条件該当**: 該当なし(観測指標のみ、閾値・QA定義は無変更)。

---

## 6. Opus設計レビューに掛けるべき論点

1. **候補1・候補2はいずれも「診断feedbackの内容を変える」方向の変更
   だが、Trial-08(情報を減らす方向)がREJECTEDだった経緯を踏まえると、
   「情報を追加する」方向の変更が本当に独立した仮説として妥当か、
   それとも同根の「診断feedbackをいじってもWriterの非決定性には勝てない」
   という限界の別表現に過ぎないか**、の判定。
2. **候補3(題材構造によるNews選定ガイダンス)がEditorial多様性(スポーツ
   速報等の扱い)とのトレードオフをどう評価すべきか**、Fable/ユーザーの
   編集方針判断が必要な領域とSonnetのデータ分析で判断できる領域の切り分け。
3. **§3-2の「固有名詞除外で box-score型のflag率が劇的に下がるが、
   目視では固有名詞と意味重複が分離できない」という一見矛盾する結果**を、
   より厳密な指標設計(候補4)でどこまで解消できるか、それとも
   box-score型自体がlexical overlap指標と本質的に相性が悪い(§3-3の
   代替指標比較表)と判断すべきか。
4. **Loop Budget=2という既存の安全装置設計**が、§3-4で確認された
   もぐらたたき率(single_event_boxscore 11.5%、survey_trend 18.2%)を
   踏まえてなお妥当か(本タスクでは変更を提案しない、Opus観点として
   提示のみ)。

---

## 7. 推奨する次の最小Trial(1件)

**推奨: 候補4(Ledger由来語ベースのnecessary factual overlap除外指標の
精緻化、¥0)を先に実施し、その結果を踏まえて候補1または候補3のいずれかを
選ぶ。**

理由: 候補4は¥0・Production非接触・既存データのみで完結し、§3-2の
「劇的な低下だが目視では分離できない」という未解決の矛盾に直接答える。
この結果次第で、候補1(feedback文言変更、Prompt変更を伴う)と候補3
(題材選定ガイダンス、Editorial判断を伴う)のどちらが「box-score型の
高NG率」に対してより筋の良い介入かが見えやすくなる(候補4がbox-score型の
flag要因を「本当にほぼ固有名詞由来」と示せば指標側の改善が筋が良く、
「実況描写の意味重複が主」と示せば候補1[feedback改善]や候補3[題材選定]
の方が筋が良い)。候補2(Role Planning診断接続)はTrial-07のRole収束
真因が未解明のままであり(Stage1 3-3で「段階2の優先調査対象」と申し送り
済み)、原因調査を先に行うべきで、本Trialの直後には推奨しない。

**具体的な最小Trial設計案(実施しない、提案のみ)**:
1. Hanshin/Theme2/CAR-Tの各Verified Fact Ledger原文から固有名詞・数値
   トークンを機械抽出(¥0、既存json読み取りのみ)。
2. 本タスクの大文字化ヒューリスティック除外指標と、Ledger直接抽出除外
   指標を比較し、一致率・差分を報告(¥0)。
3. 差分が大きい場合のみ、Ledger直接抽出版でsingle_event_boxscore/
   survey_trend/mechanism_limitationのflag率を再計算(¥0、追加生成なし)。
4. 結果を踏まえ、候補1(feedback文言)または候補3(題材選定ガイダンス)の
   いずれかについて、Trial-08と同型のN=6 harness比較(費用目安¥40〜80)を
   次段階としてユーザーへ提案する。

---

## 8. UDR候補(実装しない、ユーザー判断待ち)

1. **候補1〜4のいずれを次のTrial対象として承認するか**(本報告書§7の
   推奨=候補4先行、その後候補1または候補3)。
2. **OPEN-133(cross_point_overlapのstill_flagged統合)を今回のNews
   再設計の一部として再検討するか**、既存のDEFERRED方針を維持するか
   (本タスクでは新たな判断材料を追加していない、既存UDRの再確認のみ)。
3. **候補3(題材構造によるNews選定ガイダンス)を採用する場合、スポーツ
   速報等box-score型Newsの扱い(頻度・優先度)をどう位置づけるか**という
   編集方針レベルの判断。
4. **Loop Budget=2の妥当性再検討要否**(§6論点4、本タスクでは変更提案
   していない)。
5. **候補4で使うLedger由来語抽出ロジックを、将来的にProduction Overlap
   Checkerの観測指標(閾値運用ではない参考値)として定常的に記録するか**
   (OPEN-134の観測ログと同様の位置づけを想定できるか)。

---

## 9. 新規ファイル一覧

- `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01_REPORT.md`(本ファイル、root)
- `er011_news_stage4_redesign_inventory_01.py`(root、¥0 offline再集計
  script。Production関数のimport・monkeypatch・API呼び出しなし。
  `er008_point_overlap_qa_18.py`のtokenizerロジックを読み取り専用で
  再実装)
- `er011_output/news_stage4_redesign_inventory_01/`
  (`stage4_recomputation_results.json`、`point_attempt_observations.csv`
  [248行、point-attempt単位]、`fp_classification_all_flagged.json`
  [113件の全flag観測に対するルールベース仮分類]、
  `fp_classification_sample.md`[代表11件の目視用抜粋])

**費用**: ¥0(新規API呼び出しなし、既存Trial出力の読み取り再計算のみ)。
**Production/Prompt/QA/Validator/retryコード**: 無変更。**Git操作**: なし。
