# NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01_REPORT.md

管理ID: `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`
日付: 2026-09-24
実行: Sonnet(サンドイッチ委任、初回)
Production変更: なし(Trial(A)はProduction未配線出力のみ、SSOT記録(B)はCURRENT_SPEC/
DECISION_LOG/OPEN_ITEMSのドキュメント更新のみでProduction code/Prompt/routing/
retry/fallback/Audio配線は無変更)。

## 結果サマリ(重要)

**Trial(A)はbudget STOPで途中終了した。** 下水道Standard v2の1 call目(¥1.0828)
だけで、費用上限¥1を既に超過したため、Meta Standard v2(2 call目)は実行していない
(「多数試行禁止」「¥1超過見込みならSTOP」の両方に該当する二重のSTOP条件)。
下水道単体の機械計測では、平均語/文がAdvanced比13.62→9.51語/文(-4.11語)へ明確に
縮小し、9〜11語/文の目標レンジに入った。v1(13.48語/文、Advanced比-0.14語)との
差は大きい。Story構造・中心比喩・Ending logicは下水道単体では保持を確認したが、
Meta記事は未検証のため2記事横断の最終判断はできない。

**SSOT記録(B)はTrial(A)のSTOPと無関係に実施した**(ユーザー承認済み)。
CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdへの追記は完了している(§15〜§17)。

---

## §1 v2 Prompt全文 + v1差分

developer(v1・v2共通、逐語):
```
You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.
```

user template v2(逐語、`{advanced_article}`のみ差替え):
```
Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
Prefer common, high-frequency English words (roughly the 2,000 most common words).
Keep harder words only when they are necessary to understand the topic (for example, a technical term or a name). Do not add an explanation for a hard word; make the sentences around it simple instead.
Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).

Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
Do not turn the article into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, or new general observations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, limitations, and words of scope such as "some" or "all".

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Output only the English title and the English body.

[Article]
{advanced_article}
```

v1との主な変更点(詳細: `er015_output/news_standard_a2_prompt_v2_trial_01/prompt_diff_v1_v2.md`):
- 「Rewrite this entire article」「Rebuild the sentences. Do not just replace difficult words.」を明示追加(全文書き直しの強調)。
- 平均9〜11語/文の数値目標を明示(v1は数値指定なし)。
- 原因/補足/例外/結果を1文に詰め込まない、という具体的禁止を明示。
- 最頻出2,000語程度の語彙目標を明示。
- 比喩語(stage/backstage/lead role/curtain)をA2で理解可能なら保持、という具体例を追加(v1でMetaの`lead role`→`main part`になった反省)。
- 難語は必要語のみ残し、説明文を追加しない、という指示を明示化。

## §2 下水道Advanced全文(A-1、改変なし、Baseline)

“Merger”? Not Towns, but Household Wastewater

When a news report mentions a “combined septic tank,” you may wonder if it is about towns joining together. But the things being combined are not municipalities. They are toilet water, and water from the kitchen and bath.

Some municipalities are now considering replacing aging sewer systems with combined septic tanks. This does not mean getting rid of all sewers. In some areas, it means considering a change from a system that connects the whole town to one that treats wastewater near each home.

A sewer is like an invisible main artery beneath the town. It collects water from homes in underground pipes and carries it to a distant treatment plant. Most of the time, we hardly think about it. Turn on the tap, flush the toilet, and the underground system takes care of the rest.

But when those pipes grow old, the situation changes. Because they are underground, it is hard to find where they are damaged. Repairs are not easy, either. Since the system is connected over a long distance, the repairs can also become large-scale.

That is where combined septic tanks come in. They are small water-treatment facilities placed near homes. They treat not only toilet water, but also water from the kitchen and bath, for each home. Instead of sending the water to a distant treatment plant, they clean it near where it comes out.

It is like placing a small washing machine in each home instead of putting one huge washing machine in the town. The idea is to divide one large system into several smaller ones.

Of course, having a septic tank does not mean that nothing more is needed. Installation, inspections, and cleaning are still necessary. For people who use sewers, this also means that the hidden part of daily life will change.

Still, the interesting point is this: to protect convenience, we do not always need to make the system bigger. Instead of forcing an aging underground main artery to keep going, we can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.

## §3 下水道Standard v1全文(REJECTED、参考)

“Merger”? Not Towns, but Household Wastewater

When a news report mentions a “combined septic tank,” you may wonder if it is about towns joining together. But the things being combined are not towns. They are toilet water and water from the kitchen and bath.

Some municipalities, or town governments, are now thinking about replacing old sewer systems with combined septic tanks. This does not mean getting rid of all sewers. In some areas, it means thinking about a change. Instead of one system that connects the whole town, they may use a system that treats wastewater near each home.

A sewer is like an invisible main artery under the town. It collects water from homes through underground pipes and carries it to a treatment plant far away. Most of the time, we hardly think about it. We turn on the tap, flush the toilet, and the underground system takes care of the rest.

But when those pipes get old, things change. Because the pipes are underground, it is hard to find damaged places. Repairs are not easy, either. The system is connected over a long distance, so the repairs can also become very large.

That is where combined septic tanks come in. They are small places for treating water near homes. For each home, they treat not only toilet water, but also water from the kitchen and bath. Instead of sending the water to a treatment plant far away, they clean it near where it comes out.

It is like putting a small washing machine in each home instead of putting one huge washing machine in the town. The idea is to divide one large system into several smaller ones.

Of course, having a septic tank does not mean that nothing else is needed. Installation, inspections, and cleaning are still necessary. For people who use sewers, this also means that the hidden part of daily life will change.

Still, the interesting point is this: to protect convenience, we do not always need to make the system bigger. Instead of forcing an old underground main artery to keep working, we can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.

## §4 下水道Standard v2全文(本Trial、生成済み)

“Merger”? Not Towns, but Wastewater from Homes

A news report may mention a “combined septic tank.”
You may wonder if towns are joining together.
But the things being combined are not municipalities.
They are toilet water, kitchen water, and bath water.

Some local governments are considering replacing old sewer systems with combined septic tanks. This does not mean getting rid of all sewers. In some areas, they are considering a change. One system connects the whole town. Another treats wastewater near each home.

A sewer is like a hidden main artery under the town. It collects water from homes in underground pipes. Then it carries the water to a treatment plant far away. Most of the time, we hardly think about this system. We turn on the tap and flush the toilet. Then the underground system takes care of the rest.

But things change when those pipes grow old. Because they are underground, it is hard to find damage. Repairs are not easy either. The system is connected over a long distance. So repairs can also become large jobs.

That is where combined septic tanks come in. They are small water-treatment facilities near homes. They treat wastewater from toilets, kitchens, and baths for each home. The water does not go to a distant treatment plant. The tank cleans it near where it comes out.

It is like putting a small washing machine in each home. The town does not have one huge washing machine. The idea is to divide one large system into several smaller ones.

Of course, a septic tank is not the only thing needed. Installation, inspections, and cleaning are still necessary. For people who use sewers, the hidden part of daily life will change.

Still, there is an interesting point. To keep things convenient, we do not always need a bigger system. We do not have to keep an old underground main artery working. We can move water treatment closer to home. The future of sewers may come in a surprisingly familiar place—right near us.

## §5 Meta Advanced全文(Baseline、改変なし)

“Hello, I’m AI” — A Human Was Behind the AI Phone Call

Letting AI make phone calls sounds like a convenient service from the future. A person only needs to explain what they want. Then AI makes the call. That was the kind of phone service Meta was building.

The lead role was Muse, Meta’s personal AI agent. Meta was trying to give Muse the ability to make calls on a person’s behalf.

But when people looked backstage, they found something unexpected.

In internal tests, contract workers—not AI—handled some parts of the calls. Meta called these workers “human concierges.”

In other words, the sign out front said “AI phone service.” But in some cases, a human was handling the call. The stage looked as if AI were performing alone. In fact, a human understudy was waiting backstage.

That is the most interesting part of this story. You may think an AI phone call is truly impressive, only to find a human behind the curtain. It is like seeing a piano that seems to be playing by itself, then learning that another performer was hidden inside it.

Of course, there is nothing wrong with people helping. Humans can fill in the parts that AI is still not good at. That is a natural approach.

But phone calls can contain personal information. Meta employees raised privacy concerns, including the possibility that call content could leak outside the company. If people learned that contract workers had actually listened and responded to a conversation they thought they had left to AI, it would not be surprising if they were shocked.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold.

With an AI phone service, the important question may not be only whether it can make a call. Who is speaking on the stage? And who is behind the curtain? The more convenient the service, the more it may need to explain what is happening before people can truly feel safe trusting it.

## §6 Meta Standard v1全文(REJECTED、参考)

“Hello, I’m AI” — A Human Was Behind the AI Phone Call

Letting AI make phone calls sounds like a useful service from the future. A person only has to say what they want. Then AI makes the call. This was the kind of phone service Meta was building.

The main part was Muse, Meta’s personal AI agent. Meta was trying to give Muse the ability to make calls for a person.

But when people looked backstage, they found something unexpected.

In internal tests, contract workers—not AI—handled some parts of the calls. Meta called these workers “human concierges.”

In other words, the sign outside said “AI phone service.” But in some cases, a human was handling the call. The stage looked as if AI were performing alone. In fact, a human understudy was waiting backstage.

That is the most interesting part of this story. You may think an AI phone call is truly impressive, only to find a human behind the curtain. It is like seeing a piano that seems to be playing by itself, then learning that another performer was hidden inside it.

Of course, there is nothing wrong with people helping. Humans can do the parts that AI is still not good at. That is a natural approach.

But phone calls can contain personal information. Meta employees raised privacy concerns. They worried that call content could leak outside the company. If people learned that contract workers had actually listened and answered in a conversation they thought they had left to AI, it would not be surprising if they were shocked.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold.

With an AI phone service, the important question may not be only whether it can make a call. Who is speaking on the stage? And who is behind the curtain? The more convenient the service, the more it may need to explain what is happening before people can truly feel safe trusting it.

## §7 Meta Standard v2全文

**未生成(budget STOP)**。下水道Standard v2の1 call目完了時点で累計¥1.0828が
上限¥1を既に超過したため、Meta Standard v2(2 call目)は実行していない。
「多数試行禁止」の指示に従い、追加call・retryは行っていない。

## §8 Level比較(6記事中5記事のみ計測可、v1と同一の`_level_metrics()`関数を再利用)

| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |
|---|---|---|---|---|---|---|---|
| 下水道 Advanced(A-1) | 354 | 26 | 13.62 | 1.483 | 0.077 | 3.11 | 7.22 |
| 下水道 Standard v1(A-2) | 364 | 27 | 13.48 | 1.451 | 0.074 | 2.75 | 6.78 |
| 下水道 Standard v2 | 333 | 35 | **9.51** | 1.465 | 0.0 | 1.5 | 5.41 |
| Meta Advanced(Baseline) | 330 | 25 | 13.2 | 1.455 | 0.16 | 4.55 | 6.72 |
| Meta Standard v1(B-1) | 325 | 26 | 12.5 | 1.443 | 0.154 | 4.31 | 6.31 |
| Meta Standard v2 | 未生成(budget STOP) | — | — | — | — | — | — |

平均語/文の変化(下水道のみ、参考):
- Advanced 13.62 → v1 13.48(-0.14語、簡略化ほぼ無し) → v2 9.51語(Advanced比-4.11語、
  9〜11語/文目標レンジに到達)。
- long-sentence率(20語以上)はAdvanced 0.077 → v2 0.0へ低下。subordinator/100wは
  3.11 → 1.5へ低下。FK grade(heuristic)は7.22 → 5.41へ低下。

v1では「英語簡略化がほぼ起きない」というSTOP条件相当の弱い変化だったが、v2では
下水道記事について明確な簡略化を確認した。Meta記事は未検証。

## §9 Story preservation(下水道のみ確認、Meta未検証)

- 段落数: Advanced 8段落 / v1 8段落 / v2 8段落(段落構造を維持)。
- Reveal(「合併浄化槽が登場する」切り替え段落)は同じ順序で存在(○)。
- 中心比喩(`main artery`/`washing machine`)はAdvanced/v1/v2すべてで保持(○)。
- Ending logic(「未来は意外と身近な場所にやって来るかもしれない」の最終文)は
  v2でも同一文構造で保持(○)。
- 詳細: `er015_output/news_standard_a2_prompt_v2_trial_01/structure_map.md`

Meta記事(比喩語stage/backstage/lead role/curtain/understudy、Reveal「backstageに
人間がいた」、Ending「Who is speaking on the stage? And who is behind the
curtain?」)は本Trialでは未検証(budget STOPのため2 call目未実行)。v1では
`lead role`→`main part`に変化していたことが既知(既存v1 Trialで確認済み)。

## §10 Fact drift(下水道のみ、v1と同一の`_fact_tokens()`関数を再利用)

- numbers: Advanced/Standard v2ともに0件(数字drift対象なし)。
- scope words(some/all/every/only/part/parts): Advanced=Standard v2で完全一致
  (some=2, all=1, only=1, part=1、drift検出なし)。
- negation("not"): Advanced 6件 → Standard v2 8件(文分割により文数が増えたことに
  伴う増加。意味の反転drift自体は目視確認で無し)。
- proper_nouns(簡易ヒューリスティック=文頭大文字語の検出。固有名詞そのものの
  drift検出には使えない指標)は差分が出たが、これは文分割で文頭語("We"/"You"/
  "Then"等)が増えたことによるもので、実質的なFact drift(固有名詞の追加・削除)
  ではない。
- Meta「通話の一部」(some parts of the calls): Advanced Baseline原文
  "contract workers—not AI—handled **some parts of the calls**."は、v1で
  文言そのまま保持を確認済み(未変更)。v2は未生成のため確認不可。この曖昧さ
  (全体か一部かの一次情報未確認)は既存OPEN_ITEMSとして保持し、本Trialでは
  修正していない。
- 詳細: `er015_output/news_standard_a2_prompt_v2_trial_01/fact_diff_machine.json`

## §11 model・cost・latency・tokens・retry

| stage | model(実値) | effort | input | output(うちreasoning) | elapsed | cost_jpy | retried | fallback |
|---|---|---|---|---|---|---|---|---|
| a2v2_standard_sewer | gpt-5.6-luna | high | 832 | 5501(5091) | 50.918s | 1.0828 | false | false |
| b1v2_standard_meta | **未実行** | — | — | — | — | — | — | — |

合計: ¥1.0828(budget ¥1を超過、within_budget=false)。fallback発生なし
(response.model実値=リクエストどおりgpt-5.6-luna)。retry発生なし。
詳細: `er015_output/news_standard_a2_prompt_v2_trial_01/cost.json`、
`a2v2_standard_sewer.meta.json`、`raw_usage_log.jsonl`。

## §12 Fable参考評価

`[Fable記入]`

## §13 Standard v2 Trial分類

`[Fable記入]`(参考情報: 本Trialは費用上限到達によりSTOPし、2記事中1記事[下水道]
のみ生成・検証できた状態。下水道単体では平均9〜11語/文の目標を達成しStory構造・
比喩・Endingを保持、Fact driftも未検出という良好な結果だったが、Meta記事は
未検証のため、2記事横断でのVALIDATED判定はできない状態にある)

## §14 USER_DECISION_REQUIRED

`[Fable記入]`(参考論点: (1) budget-jpy上限を引き上げてMeta Standard v2の
1 callを追加実行し2記事横断の判定を完結させるか、(2) 下水道1記事の結果のみで
Standard v2 Promptの方向性[全文書き直し・9〜11語/文目標]自体は有望と判断し
別途追加予算で再Trialするか、(3) 現状の下水道単体の結果で十分と判断し
Standard(A2)の採否判断へ進むか)

## §15 CURRENT_SPEC更新内容(追記行、逐語)

`CURRENT_SPEC.md`「通常News(Major/Daily News)Reference仕様」節の表、既存行
「News記事(日本語Entertainment読み物)のEntertainment生成方式」の直後に1行追加
(既存行は無変更):

```
| Entertainment英語版生成方式(Advanced) | Advanced = Natural English Adaptation。Target level = CEFR B1。日本語完成Entertainment記事(Original→R1→R2のR2)→Natural English Adaptation(`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01` arm3 Prompt、developer/共通block/NATURAL ENGLISH arm block)。Editorial structure/angle/metaphor/surprise/endingを維持。新規Fact・一般論の追加禁止。Standard(A2)は「Trial中(v1 REJECTED、v2 `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`)、未採用」。 | `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(2026-09-24ユーザー正式承認。Production配線未完のため`PRODUCTION_WIRED`ではない) | `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(Meta)、`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(下水道で再現確認) |
```

## §16 DECISION_LOG更新内容(逐語)

`DECISION_LOG.md`末尾へ新規エントリ`## NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01: User
formally approved Natural English Adaptation as Advanced (B1)、SSOT正式記録
(ユーザー正式決定、2026-09-24)`を追記した(全文は`DECISION_LOG.md`該当箇所参照)。
主要項目: status=`APPROVED_FOR_PRODUCTION`(Advanced Natural English Adaptation、
B1のみ)、approval date=2026-09-24、supporting Trial=`NEWS-JA-TO-EN-ADAPTATION-
TRIAL-01`/`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`、Production wiring
incomplete(`PRODUCTION_WIRED`ではない)、Standard v1 REJECTED、Standard v2は
本管理IDでTrial実施しbudget STOP(2 call中1 callのみ実施)。

## §17 OPEN_ITEMS更新内容(逐語)

`OPEN_ITEMS.md`表へ新規1件(既存項目との重複なし、統合対象なし)を追加した。
OPEN番号: **OPEN-177**(既存最大番号OPEN-176の次番号)。

```
| OPEN-177 | **Advanced Natural English Adaptation Production配線残項目**(2026-09-24起票、`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`、ユーザーがAdvanced Natural English Adaptationを正式承認[`APPROVED_FOR_PRODUCTION`]したがProduction wiring未完了)。サブ項目: (1) Production official initial path wiring(日本語完成Entertainment記事[R2]→Natural English Adaptationを呼び出す正式経路の確定・実装。現状は`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`/`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`のTrialスクリプトのみで、Production module化されていない)。(2) retry・fallback consistency(既存Production Writer経路[`MAX_WRITER_ATTEMPTS`等]との整合)。(3) Production contract付与(2つの`### `節+`## In one line`等、既存News/Entertainment記事のProduction contract形式への適合)。(4) Audio path(TTS/Assembly/Audio Validation Gateへの接続)。(5) runtime evidence(実際のProduction呼び出し経路でのend-to-end実行記録)。(6) Fact・Ledger consistency(英語化時のLedger照合、Verified Fact Ledgerとの整合確認経路)。(7) Meta「通話の一部」(some parts of the calls)ambiguityの一次情報確認(Ledger MUSE-006の読みとの差、Baseline改変禁止のまま一次情報確認待ち)。(8) final regression・integration tests。Standard(A2)は本Open Itemの対象外(v1 REJECTED、v2 `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`でTrial中、別途採否判断待ち)。 | `OPEN`(`USER_DECISION_REQUIRED`ではなく配線作業待ち) | Advanced Natural English Adaptation Production配線(News Entertainment英語版生成) | Blocking対象なし(現行News生成経路には影響しない、Trial出力[Production未配線]のみで観測) | Production official initial path wiring・retry/fallback consistency・Production contract付与・Audio path・runtime evidence・Fact/Ledger consistency・Meta「通話の一部」一次情報確認・final regression/integration testsを、Fable/ユーザー判断のもと計画的に配線する。詳細: `DECISION_LOG.md`の`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`エントリ、`NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01_REPORT.md`。 |
```

Dangling Reference Check: `Grep "Natural English Adaptation" glob="*.py"` = 1件
(`er015_news_standard_a2_prompt_v2_trial_01.py`のコメント内のみ)。Production code
(`er003_*`/`er012_*`)への新規参照は0件を確認した。

## §18 Production未配線一覧

OPEN-177参照。要約: (1) Production official initial path wiring未実装、
(2) retry/fallback consistency未確認、(3) Production contract未付与、
(4) Audio path未接続、(5) runtime evidence未取得、(6) Fact/Ledger consistency
未確認、(7) Meta「通話の一部」一次情報未確認、(8) final regression/integration
tests未実施。いずれも本Trialでは着手していない(Production code側への変更なし)。

## §19 commit・push

`[実行後に記入。下記「Git」節参照]`

## §20 未解決

1. Meta Standard v2が未生成(budget STOP)のため、Standard v2 Promptの
   2記事横断VALIDATED判定ができていない。予算引き上げの要否はユーザー判断待ち
   (§14参照)。
2. Standard v2の最終採否(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFable
   参考評価(§12〜§13)を経てユーザーが判断する。
3. Meta「通話の一部」(some parts of the calls)の曖昧さは既存OPEN_ITEMSのまま
   未解決(本Trialでは修正していない、v2版での扱いはMeta未生成のため確認不可)。
4. OPEN-177(Advanced配線残項目)は新規未着手のまま。
5. 並行タスク`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(er016_*)には
   本タスクで一切触れていない(git addは自タスクパスのみ)。
