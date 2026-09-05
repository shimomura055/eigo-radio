# OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10 最終報告

## 1. 最終Status

`USER_DECISION_REQUIRED`

理由: 施策1(Entertainment/Engagement根底指示)は明確に効果があり安全上の問題も
出なかった一方、施策2(Reference Digest)は「安全に使える」ことは確認できたが、
今回1回ずつの比較では「施策1だけの場合と比べて明確に記事が良くなった」とまでは
言い切れなかった(§9参照)。また、今回のLedger検証作業自体からTrial-09に続く
3件目のLedger精度誤り(F-003のMOU署名日)が新たに見つかり、既存Fact Checkerが
それを実際に検知した。これらはいずれもユーザー判断を要する論点であり、
`REJECTED`(施策が使えない)でも単純な`VALIDATED`(そのまま採用でよい)でもない。

## 2. 使用テーマ

Trial-09と同一テーマ(米国・イラン紛争が「経済的消耗戦としての長期膠着状態」へ
移行しつつあること、ホルムズ海峡、2026年9月時点)。比較可能性を最大化するため、
`TREND_TOPIC_JA`の文面はTrial-09からそのまま再利用した。

## 3. Ledger verification

Trial-09のLedgerをベースに、2026-09-05に追加のWebSearch/WebFetchで一次報道を
再確認し、以下2件を修正した(詳細は`er011_output/open112_trend_engagement_reference_ab_trial_10/research/verified_fact_ledger.txt`注記4):

- **F-009の日付**: 「9月1日(月曜)」は誤りで、2026年のカレンダー上9月1日は火曜日。
  Fortune記事(2026-09-03)の直接引用により、Wright長官の発言対象日は
  「8月31日(月曜)」、CNBCでの発言・報道日は9月2日であると確認し修正した。
- **F-005の機雷個数**: 「100個以上の機雷」という単純化を修正。CENTCOM公式発表は
  具体的個数を明らかにしておらず、Axios経由の匿名米当局者情報は「200個超の
  mine-like objectsを掃海、うち実際の機雷は11個」という質的に異なる区分を
  報じている。この区別と、脅威レベルSEVERE継続という限定を明示する形に直した。

さらに、独立系タンカー追跡会社TankerTrackers.com(Samir Madani氏)による
Wright発言への直接反論(同日実績を約914万バレルと算出、Fortune 2026-09-03)を
新規Fact(F-012)として追加し、counter-signalを厚くした。

**新たに判明した3件目の精度誤り(本Trial実行中に発覚)**: 上記の検証作業でも
気づかなかった、F-003の「6月14日に停戦のmemorandum of understanding(MOU)に
合意」という記述について、Pattern AのFact Checkerが独立Web検索により
「6月14日は初期合意の日、14項目のMOUが正式に署名されたのは6月17日」という
矛盾を指摘し、FAIL判定の直接の原因となった(詳細は§9・§18)。この誤り自体は
Trial-09のLedgerに元から存在していたが、本Trialの事前Ledger Verificationでも
発見できなかった。既存Fact Checkerの独立Web検索によって初めて発覚した。

## 4. Entertainment / Engagement 根底Prompt

`ENTERTAINMENT_ENGAGEMENT_BLOCK`(A・B共通、Trend Synthesis Focus Moduleの
直後に追加)。要旨:
- 「続きを知りたくなる」「意外な関係に気づく」「話として面白い」を目標とするが、
  ENTERTAINING > FACTUALではないと明記。
- 事実の創作・unsupported causality・誇張・扇情表現・Ledgerにない具体例・
  根拠のない心理描写/未来予測を明示的に禁止。
- Main Storyを時系列列挙("A happened. Then B happened...")にしないことを明示し、
  Ledgerの範囲内で成立する場合に限り、contradiction/surprising contrast/
  tension/reversal/unexpected consequence/unanswered question/
  gap between appearance and realityのいずれかを検討するよう指示。

全文は`er011_output/open112_trend_engagement_reference_ab_trial_10/audit/candidate_template_A.txt`参照。

## 5. Reference Articles

2026-09-05にWebSearch/WebFetchで実際に収集した、同テーマ関連の高品質記事4本
(いずれもFact source禁止、構成・切り口の観察のみ):
1. Yahoo Finance「ホルムズ海峡通過量をめぐるエネルギー追跡会社とホワイトハウスの
   対立が今週深まった」— 逆説の出だし・数字の対比・he-said/she-said構成。
2. Al Jazeera「機雷除去の主張にもかかわらずホルムズ海峡がなお高リスクである理由」
   (2026-08-26)— 権威の主張→利害関係者の反論→専門家による問いの拡張。
3. Fortune「ホルムズ海峡が完全には閉鎖されていないため、イラン戦争は2027年まで
   長引く可能性がある」(2026-08-23)— 直感に反する逆転の論法。
4. NPR「ホルムズ海峡のタンカー乗組員はなお危険に直面している」(2026-08-08)—
   統計ではなく当事者の証言から始まる人間中心の構成。

いずれの記事についても、数字・日付・固有名詞・引用・因果関係などの具体的Factは
一切Digestへ持ち込まず、構成・切り口・見せ方だけを人間が観察した(§6参照)。

## 6. Reference Digest

`build_reference_digest()`が実LLM呼び出し(model=gpt-5.6-luna、既存の
`B1_WRITER`承認済みcontractを再利用、新規routing追加なし)で、上記の事実抜き
観察メモを整形して生成した。冒頭に「これはFact Ledgerではない」という警告文を
必須で含めさせ、Reference 1〜4の技法整理+統合Digest
(useful opening patterns / useful contrasts / useful story structures /
possible angles / techniques to avoid chronological listing)の構成で出力された。
全文は`er011_output/open112_trend_engagement_reference_ab_trial_10/research/reference_digest_block_used.txt`。
具体的な数字・固有名詞・引用は一切含まれておらず、混入は確認されなかった(§19で再確認)。

## 7. A記事全文(施策1のみ、Reference Digestなし)

```markdown
# The Iran Conflict: One Busy Day, and a War Still Stuck

The most important change in the US-Iran conflict is not one dramatic strike. It is pressure piling up without a political way out.

The conflict began on February 28, when the United States and Israel started airstrikes on Iran. A ceasefire memorandum was agreed on June 14, and the blockade was lifted four days later. But after Iran attacked three merchant ships outside approved routes in July, the blockade returned on July 14. The pause did not become a settlement.

Since then, the conflict has become harder to describe as simply open or closed. Hormuz depends on military control and continuing risk. Reports also describe pressure on Iran's energy sector, while diplomacy has produced no agreement. One report said a month-long lull had ended and the region was moving back toward a dangerous, increasingly unsustainable military stalemate.

A forecast moved its estimate for easing from September to the end of the year. Together, these signals make the conflict look less like a short crisis and more like a long economic contest.

Washington offers a different signal. The US says traffic may have recovered sharply on a recent day, and that Iran's ability to disrupt the strait is weakening. That tension is central. The question is not only whether ships can move today, but whether that movement can last and lead to a political exit.

### A record day is not a recovery yet

US Energy Secretary Chris Wright cited more than 17 million barrels through Hormuz on August 31. That was a one-day government claim. EIA data show a second-quarter average of about 5 million barrels a day, versus about 20 to 22 million before the war. TankerTrackers estimated about 9.1 million for the wider Arabian Sea that day, including routes outside Hormuz. The periods and routes differ, so the peak neither proves lasting recovery nor proves Wright wrong.

### The cost of keeping the corridor open

Traffic can improve while the conflict stays stuck. The US says it cleared a major lane, but its official statement gave no total. A separate report counted more than 200 mine-like objects, with only 11 confirmed as mines, while the warning stayed SEVERE. An opposition-linked Iranian outlet reported a petrochemical shutdown and a loss of about 230 million cubic meters a day in gas capacity. Talks ended without agreement, and a private forecast moved easing to year-end. Pressure is active, but no political exit has appeared.

## In one line...

The conflict appears to be moving toward a longer, costlier economic stalemate, but confidence should remain measured because the traffic evidence is still mixed.
```

パイプライン最終status: `NG_REVIEW_REQUIRED`(Fact CheckerがFAIL、§9参照)。

## 8. B記事全文(施策1+施策2、Reference Digestあり)

```markdown
# When a War Starts to Look Like an Economic Standoff

What looked like a short military crisis is beginning to look like something slower and harder to end.

The conflict began on February 28, when the United States and Israel started airstrikes against Iran. A June 14 memorandum brought a pause, and the blockade was lifted four days later. But the pause did not become a settlement. After Iran attacked three merchant ships outside an approved route in July, the blockade returned on July 14.

By September, the pressure was no longer limited to military action. Shipping, energy production, and diplomacy were all under strain. The 60-day negotiation period passed without an agreement. On August 18, President Trump said no talks with Iran were scheduled. A private political-risk group then moved its forecast for easing from September to the end of the year.

A report on September 4 said that a roughly month-long calm had ended. The region was moving back toward a dangerous and increasingly unsustainable military stalemate.

That does not prove what happens next. But it shows the shape of the problem. The conflict is becoming a long economic standoff, where damage and risk can continue to build even during a period of relative calm.

### One number cannot tell the whole story

One figure supports the U.S. administration's claim that Iran is losing leverage: more than 17 million barrels crossed Hormuz on August 31. But official quarterly data showed a much lower average in 2026's second quarter: 4.9 million barrels a day, compared with 20.4 to 21.6 million before the war. Another tracking source put the August 31 total across the Arabian Sea, including routes outside Hormuz, at about 9.1 million. Different windows, boundaries, and sources matter, so one headline number cannot decide who is winning.

### The cost is harder to reverse

An opposition media outlet reported an Arvand petrochemical shutdown and a loss of about 230 million cubic meters a day in gas capacity. U.S. forces said they cleared part of a main shipping lane. But an anonymous official was reported as saying more than 200 mine-like objects were swept up, while only 11 were confirmed mines. The threat level stayed SEVERE. With no agreement after the deadline, brief access does not by itself show that production or safety has returned.

## In one line...

The conflict is moving toward a longer economic standoff, but the evidence points to that direction more clearly than it identifies a winner.
```

パイプライン最終status: `OK`(Fact Checker REVIEW_REQUIRED=non-blocking、
Ledger Deviation `LEDGER_COMPLIANT`・deviations 0件)。

## 9. A/B品質比較(§9評価項目)

| # | 項目 | A | B |
|---|---|---|---|
| 1 | 読者を引き込むか | Yes(「一日の記録」対「膠着」という対比を軸に構成) | Yes(「短期危機に見えたものが、より遅く終わりにくいものへ」という反転の出だし) |
| 2 | 面白いか | Yes | Yes |
| 3 | 意外性 | 中(記録的数値 vs 統計の対立は明示、ただし新規性はB1B定番の対立軸) | 中(同種の対立軸。Aとの明確な差は小さい) |
| 4 | 聞き続けたいか | Yes | Yes |
| 5 | 人に話したくなるポイント | Wright発言とTankerTrackersの食い違い | 同左 |
| 6 | 時系列羅列になっていないか | 冒頭は反転構成、中盤はやや時系列的 | 同程度。冒頭の反転はAとほぼ同水準 |
| 7 | 一本のthroughline | Yes(「圧力は続くが政治的出口がない」) | Yes(「経済的膠着への移行」) |
| 8 | Referenceありの方が明確に改善したか | — | **明確な改善とは言えない**(§11参照) |

**総括**: 施策1(Entertainment原則)だけでも、Trial-09の3記事(時系列列挙寄り)から
明確に改善し、両パターンとも反転・対比を軸にした構成へ変化した。A・B間の
質的な差は、少なくとも今回の1回ずつの比較では小さく、Bが明確に優れているとは
言えなかった。

## 10. Main Story比較

- A: 「一つの劇的な攻撃ではなく、出口のない圧力の蓄積が最重要の変化」という
  逆説枠組みで開始。
- B: 「短期危機に見えたものが、より遅く終わりにくいものに見え始めている」という
  類似の逆説枠組みで開始。
- 両者とも、Trial-09の3記事(2月→6月→7月→8月→9月と出来事を順になぞる書き出し)
  とは異なり、最初に「変化の性格」を提示してから、必要な背景を差し込む構成に
  変わっている。

## 11. 時系列羅列の改善

Trial-09の3記事はいずれもMain Story冒頭が日付順の出来事の列挙だったのに対し、
今回のA・Bはいずれも「これは単なる軍事衝突ではなく、経済的膠着である」という
性格づけを先に示してから、背景説明に入る構成になった。ただし、背景説明部分
(6月合意→7月再開→8月圧力)自体は依然として時系列に近い順で書かれており、
「時系列を完全に解体した」とまでは言えない。改善は「冒頭の性格づけ」の部分に
限定的に表れている。

## 12. 面白さ

両記事とも、単一の記録的数字(Wright発言)と、それに矛盾する複数の独立した
反証(EIA統計・TankerTrackers)を並べる対比構成を採用しており、「政府の主張と
独立データの食い違い」という、聞き手が誰かに話したくなる具体的な材料を
含んでいる。この点はTrial-09の記事にも既にあった要素だが、今回は記事全体の
構成(冒頭の反転)がその対比を支える形により自然に統合されている。

## 13. 意外性

Ledgerが支持する範囲での意外性(記録的数値の主張が、独立統計・独立トラッキング
会社の両方から同時に疑問視されている)は両記事とも保持している。Ledgerを超える
「発明された」意外性は見つからなかった(§18のFact Safety確認結果と整合)。

## 14. Entertainment性

聞いて自然な、大人向けニュースの語り口を保ちながら、対比・反転の技法を使えている。
語数面では、Point One/Twoが2記事とも既存の目安(target 30〜60語、tolerance
25〜70語)を超える傾向が見られた(A: Point One 70語[tolerance内]・Point Two
83語[tolerance超]。B: Point One 78語・Point Two 78語[両方tolerance超])。
これはhard capではないため即座に問題ではないが、「面白く具体的に書こうとすると
Pointが長くなりやすい」という副作用として記録しておく。

## 15. Trend overclaim件数

- A: **測定不能**。Fact CheckerがFAILしたため、Ledger Deviation Checker
  (overclaim検知の主担当)は実行されなかった。
- B: **0件**(`overall_status: LEDGER_COMPLIANT`、`deviations: []`)。
  Trial-09(同種条件でPoint Two 4件のMINOR overclaimを検出)と比べ、明確な改善。

## 16. Overclaim修正前後 全件

**該当なし**。Bはdeviationsが0件のため、Local Rewrite・Diagnostic Full Retryの
いずれも発動しなかった(記事本文は初回生成のまま採用)。Aはこの工程まで
到達しなかった。§10で要求されている「Overclaim Case」形式の修正前後報告は、
今回のTrialでは1件も発生しなかったため、報告すべき事例なし。

## 17. 修正後のEntertainment impact 全件

**該当なし**(§16と同じ理由。修正が発生していないため評価対象がない)。

## 18. Fact Safety

- A: Fact Checker **FAIL**。原因はWriterの創作ではなく、Ledgerに元から存在した
  精度誤り(F-003、MOU署名日6月14日 vs 実際は6月17日)。Writer側の逸脱ではない。
- B: Fact Checker **REVIEW_REQUIRED**(non-blocking)。指摘4件:
  (1) 同じF-003の日付混同疑い(Aと同一の根本原因だが、Bの文面
  "A June 14 memorandum brought a pause"は「合意」と明言していないため、
  Fact Checkerは断定的な矛盾ではなくREVIEW_REQUIRED止まりと判定した)。
  (2) Eurasia Groupの予測変更の一次情報が確認できない。
  (3) TankerTrackersの約910万バレルという数値の独立確認ができない
  (Ledger自体のF-012に基づく記述だが、Fact Checker側では別出典から再確認
  できなかった)。(4) 機雷内訳(200個超・11個確認)の内訳がCENTCOM公式発表
  ではなく匿名当局者情報に基づく点。いずれもTrial-09で見られたのと同種の
  「具体的だが独立確認が難しい主張」パターン。
- Ledger Deviation: Bは0件(§15)。
- Directional Fact Precheck: B `DIRECTION_REVIEW_REQUIRED`。中身を確認したところ、
  Ledgerの地の文(「Fortune記事による直接引用の確認)は「Monday, August 31」を
  指しており、」のような、Ledger作成者自身の注記文)が機械的な文単位マッチャーに
  拾われたことによる誤検知で、Trial-09でも同種の限界が報告済み。新しい問題ではない。

## 19. Reference由来Fact混入

§12の要求どおり、A・B両記事本文およびPoint本文を、Reference Articles固有の
具体的要素(例: 特定トラッキング会社名Kpler、船舶数「5隻」、"TRUMP STRAIT"という
呼称、シュレディンガーの猫の比喩、名指しの業界団体担当者の発言、イランの機雷
保有数「2,000〜6,000発」、「2027年まで長引く」という具体的な時間予測、特定の
分析会社名Vortexa/Alpine Macro/Bourse & Bazaar、選挙がらみの論点)について
逐語チェックした。**いずれも混入していない**。Reference Digest自体にもこれらの
具体的要素は一切含まれていなかった(§6)。今回の設計(Fact抜きのDigestを、実LLM
呼び出しで整形し、冒頭に警告文を必須で含めさせる)は、少なくとも1回の試行では
意図どおりFact漏洩を防げた。

## 20. Point Overlap

A・Bとも、Point One/Two対Full Story、Point One対Point Twoのいずれも
**閾値0.40を大きく下回った**(A: 記録未保存だが正常終了・retry 0回。
B: Point One vs Full Story 0.082、Point Two vs Full Story 0.170、
Point One vs Point Two相互 0.102〜0.106)。Trial-09で問題になった「News/Trend
記事は固有名詞・事実語彙の共有によりPoint Overlapが閾値付近まで上がりやすい」
という懸念は、今回は両パターンとも発生しなかった。Point Value QAも両パターンとも
初回生成で全項目PASS(retry不要)。Entertainment/Storytelling原則がPointに
「別の意味づけ」を要求したことが、結果的にPoint同士の語彙的独立性も高めた
可能性がある(あくまで今回1回ずつの観察で、確定的な因果関係の主張ではない)。

## 21. API call比較

生ログ: `er011_output/open112_trend_engagement_reference_ab_trial_10/raw_usage_log_trial10.jsonl`

| Stage | A(呼び出し数) | B(呼び出し数) |
|---|---|---|
| Point Role Planning | 1 | 1(6,840トークン中6,837トークンがcache hit。Aで直前に同一Ledger/Topicを使ったためOpenAI側の自動prompt cachingが効いたと見られる) |
| Writer本体 | 1 | 1 |
| Evidence Compression Editor | 1 | 1 |
| Point Value QA | 1 | 1 |
| Fact Checker | 1 | 1 |
| Ledger Deviation Checker | **0**(Fact CheckerでFAILし到達せず) | 1 |
| Reference Digest生成(Bのみ) | — | 1 |
| **合計** | 5 | 7 |

**重要な注意**: A・Bの呼び出し数の差(5 vs 7)を単純にReference Digestの
コストと解釈しないこと。うち1件(Ledger Deviation Checker)は、AがFact Checker
FAILで早期終了したために呼ばれなかっただけで、Reference Digestとは無関係。
Reference Digestに直接起因する呼び出しは「Reference Digest生成」の**1回のみ**。

## 22. token比較

Writer本体呼び出し(実際にAugmentされたPromptを使う箇所)のinput tokens:
A=12,653トークン、B=14,255トークン(**差分+1,602トークンがReference Digest
ブロック追加分**)。Point Role Planning呼び出しは、AもBも同じTopic/Ledgerを
渡すため入力内容は同一(6,840トークン)で、Reference Digestの影響を受けない。

Reference Digest生成呼び出し単体: input 1,481トークン、output 1,725トークン。

全体合計(全stage、cache分含む): A input 131,281 / output 17,455トークン、
B input 138,552(うちcache 11,308) / output 18,355トークン。

## 23. runtime比較

A合計 266.2秒、B合計 236.9秒。**Bの方がやや速かった**(Reference Digest生成の
追加呼び出し[約15秒]を含めてもなお速い)。これは個々のLLM呼び出しの応答時間の
自然な変動によるもので、Reference Digest追加によって処理が体系的に遅くなる
という証拠は今回得られなかった。

## 24. 1記事あたり追加cost

既存の公式pricing snapshot(`er005_output/cost_baseline_01/pricing_snapshot.json`、
No.18等の既存cost計算[`er011_no18_cost_compute_01.py`]と同一参照元、
gpt-5.6-luna: input $0.20/1M、cached input $0.02/1M、output $1.20/1M)で算出。

Reference Digestに直接起因するコストのみを切り出すと:
- Reference Digest生成呼び出し: 約$0.00237(約¥0.38)
- Writer本体プロンプトの増分(+1,602トークン): 約$0.00032(約¥0.05)
- **合計、Digestを記事ごとに毎回新規生成した場合: 約$0.0027/記事(約¥0.43/記事)**

Digestは本来Ledgerと同様「テーマ単位」で1回作れば複数記事(A2・B1・複数run)へ
使い回せる性質のものであるため、同一テーマで2記事に使い回せば約¥0.24/記事、
5記事なら約¥0.13/記事まで低下する(§26参照)。

なお、A・Bの呼び出し数の単純な差(5 vs 7)から素朴に総コストを比較すると
A $0.0472(¥7.6)・B $0.0477(¥7.6)であり、この差のほとんどはLedger Deviation
Checkerの有無(§21の理由でAが早期終了したため)であり、Reference Digest自体の
コストではない。

## 25. 100 / 1,000 / 10,000記事換算

保守的に「Digestを記事ごとに毎回新規生成する」という最悪ケース(約¥0.43/記事)を
単純線形換算すると:

| 記事数 | 追加コスト(毎回新規生成) | 追加コスト(テーマ単位で5記事に使い回す想定) |
|---|---|---|
| 100 | 約¥43 | 約¥13 |
| 1,000 | 約¥430 | 約¥130 |
| 10,000 | 約¥4,300 | 約¥1,300 |

いずれのシナリオでも、既存のWriter+QAチェーン全体のコスト(No.18実測で
1テーマ数百円〜千円規模、`er011_no18_cost_compute_01.py`参照)と比べて
無視できる水準である。

## 26. Reference Digestの費用対効果

コストは無視できるほど小さい一方、§9・§11で見たとおり、今回の1回ずつの比較では
Reference Digestの追加による品質面の明確な優位性は確認できなかった
(施策1[Entertainment原則]だけでも同水準の反転構成・対比構成に到達した)。
費用対効果を「コストはほぼゼロ、効果は今回不明瞭」と評価する。効果が本当に
ないのか、たまたま今回1回ずつの生成でAがBに近い結果を出しただけなのかは、
追加のrunなしには判別できない(Loop Budgetの観点から、本Trialでは追加runを
行わずSTOPし、必要性の判断をユーザーに委ねる、§28参照)。

## 27. 新QA必要性

**不要と判断**。今回発生した問題(F-003の日付混同、TankerTrackers数値の
未確認、機雷内訳の情報源階層)はいずれも既存Fact Checkerが独立Web検索で
検知しており、新しいカテゴリのQAを追加する必要は見られなかった。Ledger
Deviation・Point Overlap・Point Valueもすべて既存QAのみで正常に機能した。

## 28. 残るUSER_DECISION_REQUIRED

1. **Reference Digestを今後も検証し続けるか**: コストはほぼゼロだが、
   今回1回の比較では明確な品質改善が確認できなかった。追加のrun(同一条件で
   もう1回ずつ、または他のテーマでの再検証)を行うかどうかはユーザー判断。
2. **Ledger自動化(既存の`er003_v1_en_direct_vfl_01_generate.py`の
   自動Researcherパイプライン)採用の緊急性**: Trial-09で2件、本Trialの
   ユーザー指示による事前修正後もさらに1件(合計3件目)、人手Ledgerの精度誤りが
   見つかった。いずれも既存Fact Checkerが最終的に検知しているため
   Production上の実害は出ていないが、「毎回Fact Checkerに頼る」設計を
   このまま続けるか、Ledger作成自体を自動化するかは、Trial-09から持ち越しの
   ままユーザー判断が必要。
3. **Point長さの目安超過**: 面白く具体的に書こうとすると、Point One/Twoが
   既存のtolerance(25〜70語)を超えやすい傾向が今回2記事とも見られた
   (hard capではないため即対応不要だが、目安の見直しが必要か観察を続けるか
   ユーザー判断)。

## 29. Production変更なし確認

`er003_v1_n3_01_articles_generate.py`を含む既存ファイルへの変更は一切行って
いない。新Validator・新Fact Checker・新LLM QAの追加なし。Point Overlap閾値
(0.40)・severityルールの変更なし。Topic Master(`POOL_TOPIC_MASTER.md`・
`topic_package_*.py`)への追加なし。Reference DigestはProduction routingへ
新規登録せず、既存の`B1_WRITER`承認済みcontractを再利用しただけ。
`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`のいずれにも到達していない。

## 30. 次アクション

- 上記§28の3論点についてユーザー判断を仰ぐ。
- ユーザーがReference Digestの追加検証を希望する場合、同一条件でのrun数を
  増やす、または別テーマでの再現性確認を行う(Loop Budgetの範囲内)。
- Ledger自動化の検討に進む場合は、既存の自動VFLパイプラインを使った
  Trial(新規実装なしで動くか確認)を別途設計する。
- 今回はB1のみを比較したため、A2での同様の比較が必要かどうかもユーザー判断
  次第(§8の指示により、B1の結果が明確でない場合はA2追加も可としていたが、
  安全上の重大な問題は出ていないため、今回はA2を追加実行していない)。

---

## 固定サマリーブロック

今回Status: USER_DECISION_REQUIRED
Entertainment指示: 効果あり(両パターンとも時系列列挙から反転・対比構成へ改善)
Reference Digest: 安全(Fact漏洩なし)・コストほぼゼロだが品質面の明確な優位性は今回未確認
A品質: 良好(FAIL自体はLedger精度誤りが原因でWriter起因ではない)
B品質: 良好(REVIEW_REQUIRED止まり、Ledger Deviation 0件)
A vs B: 明確な優劣差なし(今回1回ずつの比較)
Trend overclaim: A測定不能(Fact Check FAILで未到達)、B 0件
安全修正後の面白さ: 該当なし(修正発生せず)
Reference Fact leakage: なし(0件)
追加API calls: Reference Digest起因は+1回のみ(Writer他工程は既存構成と同一)
追加tokens: Writer本体で+1,602トークン、Digest生成呼び出し単体で input1,481/output1,725トークン
追加cost/article: 約¥0.43(毎回新規生成の場合)、テーマ単位で使い回せば¥0.1〜0.2台まで低下
New QA: 不要
Production変更: なし(確認済み)
USER_DECISION_REQUIRED: Reference Digestの追加検証要否/Ledger自動化の緊急性/Point長さ目安の見直し要否の3点
次に進めてよい工程: ユーザーが上記3論点を判断した後の追加Trial設計(新規Production実装は不可)
