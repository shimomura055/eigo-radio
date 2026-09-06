# EDITORIAL-B-FAMILY-VOICES-TRIAL-03 報告書

管理ID: **EDITORIAL-B-FAMILY-VOICES-TRIAL-03**
Lane: **Lane B / B Family(Voices-Perspective)**(Lane A: OPEN-112/OPEN-117/ER-011系とは独立)
種別: **初回Research Trial(実行)**。ユーザー承認済み(2026-09-06、
`EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`§17に対する回答)。

**今回はArticle-only(B1、Voice数=2)の1本のみを生成した。Production Prompt/
コード/Validatorの変更は一切行っていない。TTS/音声化は行っていない。**

前提: [EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md](EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md)
の設計案(§5〜§16)、[ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md](ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md)、
`er003_v1_n3_01_articles_generate.py`(Read-only importのみ、無変更)。

新規Trial script: [er012_editorial_b_voices_trial_03.py](er012_editorial_b_voices_trial_03.py)
出力: `er012_output/editorial_b_voices_trial_03/`

---

## 1. Research(Perplexity sonar-pro、既存承認済み呼び出しパターンの再実装)

Trial-11(`er011_open112_engagement_reference_cross_topic_ab_trial_11.py`)の
`_perplexity_call()`パターンを本ファイル内に再実装(新規Production
Researcherモジュールは作らない)。2段階で実行した:

1. **Stage 1(fact収集)**: テーマ「オフィスにおける固定席(assigned desk)
   復活」について、経営陣/オフィス戦略・従業員・新人教育担当・不動産/
   ワークプレイスコンサル・労組/従業員代表・ホットデスキング継続派、
   という複数の異なる立場を横断してPerplexity(sonar-pro)へ調査させ、
   15件のfactを取得(`research/raw_facts_research.json`、可読版
   `research/facts_research_readable.txt`)。
2. **Stage 2(独立verification)**: 別クエリで15件全てを独立に再検索させ、
   判定はCONFIRMED 12件・PARTIALLY_CONFIRMED 3件・COULD_NOT_CONFIRM/
   CONTRADICTED 0件(`research/raw_facts_verification.json`、可読版
   `research/facts_verification_readable.txt`)。**実在しない立場を
   LLMの想像で補う必要は生じなかった**(STOP条件に該当せず)。

Perspective候補抽出(4候補を検討し2つを選定、詳細と却下理由は
`research/perspective_candidates.json`):

| 候補 | 立場 | 採否 |
|---|---|---|
| 候補1 | 個別企業・ワークプレイスリーダーが集中力・企業文化・帰属意識を測定基準に固定席へ回帰 | **VOICE_1に採用** |
| 候補2 | 不動産・ワークプレイス戦略の集計データが示す、コスト効率・柔軟性を測定基準にした業界全体のデスク共有拡大 | **VOICE_2に採用** |
| 候補3 | 新人研修・メンタリングを担う人事/マネージャー(近接性重視) | 不採用(単一ソースVISのみ、候補1の変奏に近い) |
| 候補4 | 労組/従業員代表によるホットデスキングの公平性・健康面への批判(EU欧州委員会) | 不採用(PARTIALLY_CONFIRMEDにとどまり、対象が欧州公務員という特殊文脈) |

選定理由: 候補1・2は共に複数の独立ソースで厚く裏付けられ(候補2は全件
CONFIRMED)、かつ「賛成/反対」の対称ペアではなく、**同じ現象(固定席復活の
動き)を異なる測定基準(個別事例の従業員体験・文化 vs 不動産ポートフォリオ
全体のコスト効率)で見ている**という質的に異なる利害の違いを持つ。候補2には
候補1側に有利な材料(良く設計されたホットデスキングは固定席以上の満足度
[Lmi 72.8 vs 69.6]を生む)も含まれており、単純な藁人形になっていない。
Verified Fact Ledgerは`research/verified_fact_ledger.txt`(F-01〜F-10、
source/date/fact/number/actor/立場/利害/evidence strength/counter/time
window全項目を記載)。

---

## 2. 骨格マッピングの実装詳細(read-only事前確認、実測で裏付け)

`split_common_sections_for_point_qa()`は`###`見出しが**ちょうど2つ**でないと
`None`を返す(`er003_v1_n3_01_articles_generate.py`501-514行目)。Tensionを
3つ目の`###`見出しとして独立させると、この関数が`None`を返し、Point
Overlap QA・Point Value QAが両方ともスキップされ、モニタリングデータが
取得できなくなる(design報告§7で予告した通り)。

**採用した配置**: Tensionは新しい見出しを追加せず、`###`2つ目
(Voice 2)の本文の末尾・`## In one line`見出しの直前に、ラベルの無い
独立した段落として追加した。これにより`h3_matches`は常に2のまま
保たれ、`split_common_sections_for_point_qa`・`section_word_counts`
(`er003_v1_spoken_first_01_r1_generate.py`)・Point Role Planning・Point
Value QAは**無改造で正常動作することを実測で確認した**(後述§4)。
トレードオフとして、`point_two`として記録される語数・overlap値は
「Voice 2 + Tension」の合算になる(モニタリング用途としては許容範囲、
Reportに明記)。

**未検証の範囲**: 本TrialはArticle-onlyのため、Audio Validation Gate・
TTS/ASR Validator(`###`見出し名依存)は実行していない。設計報告§7の
「物理slot数が同じなら無改造で転用できる」という予測に沿う構造には
なっているが、**音声化工程での実動作確認は次Trialの課題として残る**。

---

## 3. Prompt構成(B Family Common Skeleton + Voices Focus Module)

既存のANCHOR挿入方式(Trial-05/09/10/11と同一手法)で、
`er003_v1_n3_01_articles_generate.COMMON_BLOCK_TEMPLATE`の
`【Spoken-first原則(数字の扱い)】`直前へ、新規ブロック
`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`を1箇所だけ挿入した。Phase A
(`run_phase_a()`)で、挿入後のtemplateが「baselineへこのブロックを
機械的に1回挿入した文字列」と完全一致することを確認済み
(`clean_single_insert_confirmed=True`、`er012_output/editorial_b_voices_trial_03/audit/phase_a_result.json`)。
既存文言(Layer1 Common Writing Contract、Master記事[阪神]模倣導入文含む)
は一切変更していない。

ブロックの内容(全文は`er012_output/editorial_b_voices_trial_03/audit/b_family_voices_focus_module_block.txt`):
Main Story slot=Question/Hook(100語未満、結論を先取りしない)、
`###`1つ目=Voice 1(見出しに"Voice 1"等のラベル禁止)、
`###`2つ目=Voice 2+Tension(新しい見出しを追加せず、4軸[測定基準/利害/
価値観/問いの立て方]に沿って立場の違いを言語化)、
`## In one line`=Closing(要約ではなく一段深い理解、Evidence-bounded
Interpretation厳守)。既存のPoint Balance原則・言い換え禁止は維持しつつ、
Point長さ目標(30-60語/許容25-70語)はVoiceセクションには適用されない旨を
明記した。

ユーザー決定#5に従い、Reference Example(Voice数2/4のmock記事)は
一切promptへ渡していない(役割説明文のみで生成)。

---

## 4. Writer Trial adapter(Point Overlap/Value QA monitoring専用化)

`gen.run_one_pattern()`はPoint Overlap/Value QAがflaggedの場合、記事全体を
最大2回retryし、それでもNGなら早期returnしてFact Checker以降を実行しない
設計(design報告§11の懸念通り、Discovery向け閾値0.40をVoiceにそのまま
適用するとgateとして働いてしまう)。ユーザー決定#6を満たすため、
`er012_editorial_b_voices_trial_03.py::run_voices_pattern()`という新規
Trial adapterを実装した。**Point Role Planning・Fact Checker・Ledger
Deviation Checker(+Local Rewrite)・Directional Fact Precheckは、呼び出す
関数・引数・順序をgen.run_one_pattern()から一切変更せずそのままコピー
した**。変更したのはPoint Overlap/Value QAのみで、single passで呼び出し・
記録し、flaggedでも記事全体retry・早期returnを発生させない。

実測結果(`b1b_run01/point_overlap_value_qa_monitoring.json`):
lexical overlap point_one_vs_point_two=0.301、point_two_vs_point_one=0.263
(閾値0.40未満、いずれもflagged=False)。Point Value QA=PASS(6項目すべて
PASS、reasoning付き)。したがって今回は実際にはflagされず、adapterの
「gateにしない」挙動は実測では発火しなかったが、コード上その経路が
正しく機能する設計になっていることは実装レビューで確認済み。

---

## 5. 生成結果

`er012_output/editorial_b_voices_trial_03/b1b_run01/article.md`(全文は
下記§10)。status=**OK**(NG_REVIEW_REQUIREDなし)。

- **Fact Checker**: verdict=REVIEW_REQUIRED(non-blocking、既存policy通り)。
  contradictions=0件。unsupported_specific_claims 3件: (1)Gensler共同議長
  自身の提言("週3日以上出社者に固定席")を記事が"the survey suggested"と
  調査結果であるかのように帰属、(2)Gartner調査回答者を記事は"business
  leaders"と一般化しているが実際は不動産・財務専門家127人、(3)Leesman
  Lmiデータを記事が"One UK analysis"と表現しているが実際はグローバル
  データ(英国限定ではない)。3件ともEvidence Compression(固有名詞削減)
  適用時に生じた帰属・地理表現のずれであり、design報告§8で予告された
  「固有名詞削減が新しい主張ドリフトを生むリスク」の軽微な実例として
  記録する(Fact自体の捏造・因果強化ではなく、帰属主体・対象範囲の
  ずれ)。
- **Ledger Deviation Checker**: overall_status=**LEDGER_COMPLIANT**、
  deviations=2件(いずれもMINOR、Local Rewrite発火なし)。内容は上記
  Fact Checker指摘と同系統(帰属のずれ1件、対象範囲の拡張1件)。
- **Directional Fact Precheck**: overall_status=DIRECTION_REVIEW_REQUIRED
  (non-blocking、ルールベースでLLM呼び出しなし)。全件`conflicts: []`
  (実際の方向反転は0件)。原因は本Trial独自のLedger形式(source/date/
  fact/number/actor/立場/利害/evidence_strength/counter/time_windowを
  ラベル付き行として構造化した形式)が、この機構の文分割正規表現に
  よって「number_or_stat: ...」等のメタデータ行が疑似文として抽出され、
  片側にしか方向語が無いため機械的に判定できない、というフォーマット
  起因の現象であり、実際のFact逆転ではない。次回Trialでは、この
  precheckとの相性を考慮し、Ledgerのメタデータ行をより散文的な文章に
  近づけるか検討する。
- **Point Overlap/Value QA(monitoring)**: 上記§4の通り、いずれもflagなし。

---

## 6. 内容面の評価(客観+根拠引用付き)

| 観点 | 結果 |
|---|---|
| (b) 単純な賛否の言い換えでないか | Voice 1(個別企業・集中力/文化/帰属意識、測定基準=事例ベースの体験指標)とVoice 2(業界集計データ・コスト効率/柔軟性、測定基準=採用率・計画統計)は対称的な賛成/反対ではない。Voice 2内にVoice 1に有利な事実(バラエティ豊富なホットデスクのLmi=72.8が固定席69.6を上回る)も含まれ、藁人形になっていない |
| (c) Tensionが前提差を言語化しているか | Voice 2末尾: "These figures measure space plans and future capacity. They do not directly measure how comfortable or focused workers feel each day."および"One side is counting adoption and efficiency. The other is asking what kind of work experience the design creates, and for whom." — 測定基準(軸a)・利害(軸b)の違いを明示。価値観(軸c)・問いの立て方(軸d)への言及はやや弱く、深化の余地あり |
| (d) Closingが要約でないか | "The real question is not simply, 'Fixed seats or free seats?' It is: 'What are we measuring, whose needs come first, and what design supports the choice?'" — 勝者を決めず、新しい問いへ転換している |
| (e) Point Overlap/Value QA(monitoring) | §4参照、いずれもflagなし |
| (f) 語数 | 全体413語(soft range 280-420内)。Hook=48語(100語未満の目安を満たす)、Voice1=171語、Voice2+Tension=167語(いずれもDiscovery向けPoint目標30-60/許容25-70を超過、Focus Module指示通りの想定内挙動)、Closing=27語 |
| (g) Reference Example定型表現の混入 | Reference Exampleは今回promptへ一切渡していない。"Imagine..."/"Now look at..."/"From this point of view..."/Voice A・B固定ラベルは検出されなかった。Closingの"The real question is not simply...It is:"は"Maybe the real question is..."と修辞的に類似するが逐語一致ではなく、供給源(Reference Example)を与えていないため直接混入ではない。今後のTrialで頻出するか要観察 |
| (h) No Jargon・Spoken-first | 専門用語なし、数字の同時比較は概ね2つ以内に収まっている(Spoken-first原則Dに整合) |
| (i) 「その立場なら確かにそう見える」か | 両Voiceとも具体的な実名企業・数値に基づき、その立場の合理性が読み取れる(Voice 1: Amazon/Scotiabank/Gensler、Voice 2: CBRE/Gartner/Leesman)。最終判断はユーザー |

---

## 7. Cost

- Perplexity(sonar-pro、Research 2 call): input 654+5,953=6,607 tokens、
  output 6,066+4,124=10,190 tokens。Perplexity料金は
  `er005_output/cost_baseline_01/pricing_snapshot.json`に記載が無いため、
  Trial-11と同様「金額不明」として扱う(参考: 一般的なsonar-pro料金
  水準で概算すると1ドル未満)。
- OpenAI(gpt-5.6-luna、Writer adapter一連: Point Role Planning・Writer・
  Evidence Compression・Point Value QA・Fact Checker[web_search 10回]・
  Ledger Deviation Check、計6 call): input 115,735 tokens、output 12,583
  tokens。`pricing_snapshot.json`のgpt-5.6-luna単価(input $0.20/1M、
  output $1.20/1M)で概算: 約$0.038。Fact CheckerのWeb Search tool fee
  ($10/1,000 call×10回)を加算すると約$0.138。
- 合計概算(Perplexity分は参考値扱い): **1記事あたり1ドル未満(¥500を
  大幅に下回る)**。¥500超過によるSTOPには該当しない。
- TTSは実行していない(Article-onlyのため)。

---

## 8. STOP条件チェック

- Fact Checker FAIL(blocking): 該当なし(verdict=REVIEW_REQUIRED、
  non-blocking)
- Ledger Deviation MAJORがLocal Rewrite上限でも未解消: 該当なし
  (MAJOR自体が0件)
- 実在する複数立場のEvidenceが取得できずLLMの想像で補う必要が生じた:
  該当なし(4候補全てが実在ソースに基づき、Stage2独立verificationで
  裏付けられた)
- 既存パーサ・QAを壊さずに骨格を置けない: 該当なし(§2・§4で実測確認)
- Cost超過(¥500見込み): 該当なし(§7)

**いずれのSTOP条件にも該当しない。**

---

## 9. Closeout分類・次Trial案・SSOT登録案

### Closeout分類

**今回Status: VALIDATED**(Voice数=2・B1・Article-only という限定範囲での
技術的検証。Production変更ゼロ、既存Fact Safety機構は無改造で正常動作、
Point Overlap/Value QAのmonitoring専用adapterも設計通り機能、実在する
Evidenceに基づく2つの非対称なVoiceとTension/Closingを含む記事1本を
生成できた)。

ただし以下は**USER_DECISION_REQUIRED**として残る(Production採用可否は
本Reportでは判断しない):

1. B Family Common Skeleton(Question/Hook+可変Voice+Tension+Closing)を
   正式採用するか(設計報告§17-1の再確認)。
2. Point長さ目標(30-60語/許容25-70語)がVoiceセクションに適用されない
   ことを踏まえ、B Family専用の長さ目安を別途定義するか、目安なしのまま
   運用するか。
3. Directional Fact Precheckとの相性を踏まえ、B Family用Verified Fact
   Ledgerのメタデータ行形式を見直すか(§5)。
4. Fact Checker/Ledger Deviationで見つかった帰属・地理表現ずれ(§5)を
   踏まえ、Evidence Compression(固有名詞削減)をB Family Voicesへ適用
   する際の追加ガードレールが必要か。
5. Tensionの価値観軸(c)・問いの立て方軸(d)がやや弱かった点(§6)を
   踏まえ、Focus Module文言の強化を追加Trialで試すか。
6. Master記事(阪神)模倣導入文をB Familyでもそのまま使い続けるか、
   将来的にB Family専用サンプルを検討するか(設計報告§17-5、今回は
   保留のまま据え置いた)。

### 次Trial案

- Voice数=3へ拡張(設計報告§7 第2段階、Point Role Planning/Point Value
  QA/Assembly/TTS Validatorの2固定schema拡張が前提として必要)。
- A2併行生成(今回はB1のみ)。
- Standard同期TTSによる音声化(PM_GOVERNANCE 7-1準拠)して、Audio
  Validation Gate・TTS/ASR Validatorが`###`見出し2つ構造で実際に動作
  するかを実測確認する(§2で残した未検証範囲)。
- 別テーマ(候補A「カフェの長時間滞在客」等)での再現性確認。

### SSOT登録案(本タスクでは登録していない、後続タスクで反映)

- **DECISION_LOG.md追記候補**: 「EDITORIAL-B-FAMILY-VOICES-TRIAL-03
  (Lane B、2026-09-06)でB Family Voices/Perspective初回Research Trial
  (固定席復活、Voice数2、B1 Article-only)を実行し、Production変更
  ゼロのままVALIDATED。Production採用は別途USER_DECISION_REQUIRED」を
  1エントリとして追記。
- **新規Open Item候補(OPEN Item化)**: 「B Family Voices/Perspective
  Skeletonの正式採用可否」「Voice数3以上への構造拡張」「B Family用
  Point長さ目安」の3点を`USER_DECISION_REQUIRED`として登録、参照先は
  本Reportおよび`EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`。
- **HISTORY_INDEX.md追記候補**: 本タスクの管理ID・日付・要旨を1行で
  追記。

---

## 10. 生成記事全文(原文、無編集)

```markdown
# The Office Seat Question: Fixed Desks Are Back — and Not Back

By September 2026, office seating is telling two stories at the same time.

Some companies and workplace leaders are bringing back assigned desks. But industry surveys show desk sharing continuing to grow.

So what are we really measuring: the worker's daily experience, or the company's use of office space?

### When a desk becomes a daily anchor

For some companies, a desk is more than a place to sit. It is linked to focus, culture, and a feeling of belonging.

One major company showed this clearly in 2024. It planned to bring back assigned desks in two major office locations, serving about 80,000 and 8,000 people. But this was not a company-wide return. Offices that already used hot-desking, including some in Europe, were not part of the change.

A bank's real estate chief later described a "quiet shift" toward more assigned seats and fewer flexible seats. One workplace survey also reported that 80% of workers in assigned-seat offices felt their office supported focused work, compared with 67% in hot-desk offices. And 60% of people using hot desks said they wanted a desk of their own.

This points to a more selective answer. The survey suggested assigned desks for people who come to the office three or more days a week, rather than giving everyone a permanent seat. In this view, frequent users may need continuity, while less frequent users can keep a flexible arrangement.

### Two rulers for the same office

The other view starts with the whole office portfolio. One industry survey found that the share of companies using assigned seating fell from 83% in 2021 to 55% in 2024. Desk-sharing models rose over the same period, from 12% to 36%. Another survey also found that 59% of business leaders planned shared desks for at least one-quarter of returning workers.

These figures measure space plans and future capacity. They do not directly measure how comfortable or focused workers feel each day. That is why they can rise while employee-focused evidence points in another direction.

The picture becomes more complicated still. One UK analysis found that fixed-seat workplaces had an average satisfaction score of 69.6, compared with 68.2 for hot-desking workplaces. But hot-desking offices with a wide variety of workspaces scored 72.8. And in Japan, 36.8% of people in flexible offices said seats often became informally fixed.

The label alone, then, does not tell the whole story. One side is counting adoption and efficiency. The other is asking what kind of work experience the design creates, and for whom.

## In one line…

The real question is not simply, "Fixed seats or free seats?" It is: "What are we measuring, whose needs come first, and what design supports the choice?"
```

---

**Status: VALIDATED(Voice数=2・B1・Article-only限定範囲の技術検証)、
Production採用は別途USER_DECISION_REQUIRED — NOT APPROVED_FOR_PRODUCTION,
NOT PRODUCTION_WIRED**
