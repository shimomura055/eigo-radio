# ER-003-A2-03 A2リスニング向け言語簡略化

**管理ID: ER-003-A2-03**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / UNDER_REVIEW`(CURRENT_SPECへは未反映、ユーザー確認待ち)**
**スコープ: テキスト生成・比較のみ。音声生成・TTS速度変更・構造変更・Key Phrase最終選定は行っていない。**

## 0. 結論(先に要約)

A2-02の情報量・Full Story比重(52〜65%)は3記事とも**維持**したまま、
文法単純化に加えて新規5仕様(語彙5語制限/抽象→具体/1文1数字/固有名詞
密度低減/spoken-first)を適用した。文長目標(平均11語以下・最長18語
以下)は3記事とも達成。ただし**語彙5語制限は3記事とも達成できず**
(実測10〜16語)、これは正直に未解決の課題として報告する。1文1数字は
2記事で完全達成、ADD03で1件残った(日付表記の扱いが仕様上未決定なため)。

## 1. 正式CEFR-A2語彙リストの有無(再確認)

`ER-003-A2-00`の監査結果を再確認し、`wordlist`/`cefr`/`ngsl`/`frequency
list`等の名前を持つファイルがリポジトリ内に存在しないことを再検索で
確認した(0件)。したがって、ご指示のとおりLLMによるsemantic QA
(`gpt-5.6-sol`、構造化出力)を補助的に使用した。この判定は**確定的な
頻度リスト照合ではなく、LLMの意味論的判断であることを明記する。**
判定に自信がない語は「uncertain」カテゴリへ分離するよう明示的に指示した。

判定方法: 記事本文(タイトル・見出しを除くFull Story+Points+In One
Line)から内容語(名詞・動詞・形容詞・副詞、機能語は除外)を抽出し、
a2_common(通常のA2語彙) / beyond_a2_general(A2超の一般語) /
proper_noun(固有名詞) / specialist_exception(専門語例外) /
uncertain(判定不確実)の5分類へ振り分けた。

## 2. 生成元

A2-01/A2-02と同じくNatural English Sourceから独立生成。B1・B2・A2-01・
A2-02いずれの本文も生成入力に使用していない(`generation_metadata.json`
の`*_body_used_as_input`はすべて`false`)。

## 3. 生成過程で発見した技術的な不具合(構造検証)

ADD03の初回生成で、構造検証が`TRANSLATION_STRUCTURE_INVALID`となった。
原因を調査した結果、2つの独立した原因が判明した。

1. モデルが見出し`## Today's Hormuz Risk Points`のアポストロフィを
   タイプグラフィ引用符(`’`、curly quote)で生成し、構造検証の正規表現
   (straight quoteのみを許容)に一致しなかった。
2. 「In One Line」の結びの文をmarkdown太字(`**...**`)のみで閉じ、
   文末が`.**`となったため、「記事本文が途中で切れている可能性がある
   (終端記号なし)」という判定に該当した。

いずれも共有の凍結モジュール(`er003_ja_to_en_translation_p1b.py`の
`validate_p1b_structure`)は変更せず、生成prompt側に「straight
apostropheを使う」「In One Lineをmarkdown太字で閉じない」という指示を
追加し、ADD03のみ再生成して解消した(A01・A02は初回から構造検証
PASSだったため再生成していない)。

また、独自実装した「1文1数字」検出の正規表現に、カンマ単体を数値と
誤認識するバグ(`[\d,]+`が数字を含まない`,`だけにもマッチしていた)を
発見し修正した(`\d[\d,]*`へ変更、数字を1つ以上含むことを必須化)。
修正前は3記事合計で5件の誤検知があったが、修正後は正確に1件のみに
なった(9節参照)。

## 4〜6. A2-03本文(3記事全文、ユーザー確認用)

### A01(サッカー記事)

> # Argentina Beat England After Two Late Goals
>
> England played Argentina in Atlanta on July 15.
> It was a World Cup game in 2026.
>
> The teams already knew each other from many big games.
> The first half was quiet, but both teams fought hard.
> Neither team had a shot on target before half-time.
>
> England went ahead in the 55th minute.
> Rogers sent the ball across the front of goal.
> Gordon got to the ball and scored.
>
> England had not reached a World Cup final since 1966.
> The team put more players at the back with five minutes left.
>
> But Messi changed the game in the 85th minute.
> He passed to Enzo Fernández.
> Enzo hit a very hard shot into the goal.
> The score was now 1–1.
>
> The referee then added more time.
> Messi sent the ball across goal from the right.
> Lautaro Martínez put it into the goal with his head.
> Lautaro had started the game on the bench.
>
> Argentina went from losing to winning in only seven minutes.
> The final score was England 1–2 Argentina.
>
> Argentina will now play Spain in the final.
> It can win two World Cup titles in a row.
> England went out after coming very close to the final.
>
> ## Today's Match-Turning Points
>
> ### Point One: Messi Made the Goals Happen
>
> Messi was 39 years old in this game.
> He was also Argentina's captain.
>
> Messi made two assists that night.
> He did not take the final shot for either goal.
>
> He helped Enzo by finding him in a good place.
> He helped Lautaro with a good ball from the right.
>
> Messi showed that a pass can be as important as a goal.
>
> ### Point Two: The Teams Made Different Changes
>
> England took Rice and some other players off.
> It moved more players near its own goal.
> England wanted to keep its lead.
>
> Argentina did the opposite.
> It wanted another goal.
>
> Argentina took defender Tagliafico off in the 81st minute.
> Striker Lautaro Martínez came on in his place.
> His goal sent Argentina to the final.
>
> England made changes to defend.
> Argentina made changes to score.
>
> ## In One Line
>
> Argentina turned the game around in seven minutes and ended England's dream.

全文: [er003_output/a2_p1_r3/A01/a2_article_raw.md](er003_output/a2_p1_r3/A01/a2_article_raw.md)

### A02(SNS規制記事)

> # UK Plans a Midnight Social Media Break for Teenagers
>
> Social media in the UK may soon say "goodnight" at midnight.
>
> The British government shared a new plan on July 15. It is for people aged 16 and 17. The government calls it a digital switch-off period. It would run from midnight to 6 a.m.
>
> During that time, apps under the plan would not open at first. This first setting is called a default. Notifications would stop. Autoplay would stop too. This tool starts the next video on its own.
>
> The apps would also stop feeds that pick posts for each person. These feeds can keep people scrolling for a long time.
>
> The government plans to start it in spring 2027.
>
> But it would not be a full ban. Teenagers could change the setting. Then they could use the apps late at night.
>
> The government wants this first setting to slow teenagers down. They would need to stop and make a clear choice. This small step may break the "just one more" habit. It may help more teenagers put down their phones and sleep.
>
> ## Today's Late-Night Scrolling Points
>
> ### Point One: Families Found the Night Rule Easiest
>
> In one test, 309 families joined. It tested three ways to cut screen time.
>
> Families said the night rule was easiest to use. The rule lasted from 9 p.m. to 7 a.m. Again and again, families said this rule helped them sleep better.
>
> Still, some teenagers moved their screen time instead. They used screens just before the rule began or after it ended. So the rule did not make the screen-time problem go away.
>
> ### Point Two: First Settings Can Change What Children Do
>
> Ofcom ran another test with children. For one group, a safer setting was on by default. It stopped suggestions for posts that could hurt them.
>
> Around seven in ten children kept that setting. For another group, no setting was chosen first. Around half then chose the safer setting.
>
> Children did not have to keep it. Still, the first setting changed what many children did. This helps explain why the UK chose a plan without a full ban.
>
> ## In One Line
>
> The UK hopes more teenagers will keep the night setting and simply go to sleep.

全文: [er003_output/a2_p1_r3/A02/a2_article_raw.md](er003_output/a2_p1_r3/A02/a2_article_raw.md)

### ADD03(ホルムズ海峡記事)

> # Trump Drops Hormuz Fee, but Oil Traders Still Worry
>
> On July 13, 2026, U.S. President Donald Trump announced a new plan. He wanted a 20 percent fee on all cargo using the Strait of Hormuz. He said the fee would help keep this important sea route safe. Much of the world's oil moves through the strait.
>
> Trump dropped the fee one day later. Gulf countries would make trade deals with the United States instead. They would also invest money there. Trump did not say how much money the deals would bring. He also did not say which Gulf countries would join.
>
> The plan became very different in only 24 hours. First, the message was, "Pay to pass." Then it was, "Invest in the United States."
>
> Oil prices fell after Trump dropped the plan. But oil traders still worried about the strait.
>
> The day before, Brent crude oil rose by about 10 percent. People worried about more fighting between the United States and Iran. The planned fee also helped push the price up.
>
> Brent then fell from its highest price that day. That price was above $87 a barrel. On July 14, Brent still ended the day higher. It closed at $84.73 a barrel. The price was about 2 percent higher than the day before. It was also Brent's highest price in a month.
>
> The fee was gone, but the danger was not. A blockade against Iran-linked ships was still in place. The blockade tried to stop those ships from moving through the area. Military attacks also continued.
>
> Traders asked a more important question: Could ships pass through safely?
>
> ## Today's Strait of Hormuz Points
>
> ### Point One: A Huge Bill for a Tanker
>
> A full Very Large Crude Carrier is a very big oil tanker. Under Trump's plan, this tanker could pay about $30 million. That is about 4.9 billion yen.
>
> Trump did not tell shipping companies about the plan before he spoke. People in shipping were shocked. Many also did not think the plan could work.
>
> ### Point Two: A Toll at Sea and International Law
>
> On July 13, the International Maritime Organization repeated an important rule. It said ships should not pay tolls or passage fees in the strait.
>
> That rule is part of international law. It protects freedom of navigation. This means ships should be free to travel through the strait. Trump's plan did not follow this basic rule.
>
> ## In One Line
>
> Trump dropped the toll, but oil traders will not relax until ships can pass safely.

全文: [er003_output/a2_p1_r3/ADD03/a2_article_raw.md](er003_output/a2_p1_r3/ADD03/a2_article_raw.md)

## 7. 文長QA

| 記事 | 総語数 | 文数 | 平均文長 | 最長文 | 18語超過 |
|---|--:|--:|--:|--:|--:|
| A01 | 332 | 41 | 8.10語 | 13語 | 0 |
| A02 | 335 | 38 | 8.82語 | 15語 | 0 |
| ADD03 | 372 | 41 | 9.07語 | 15語 | 0 |

3記事とも受入条件(平均11語以下・最長18語以下)を達成。

## 8. 語彙QA(LLM semantic QA、目標=beyond_a2_general最大5語)

| 記事 | a2_common(参考) | beyond_a2_general | 固有名詞 | 専門語例外 | 判定不確実 |
|---|--:|--:|--:|--:|--:|
| A01 | (共通語、多数、個別列挙省略) | **10** | 16 | 4 | 4 |
| A02 | 同上 | **12** | 3 | 8 | 2 |
| ADD03 | 同上 | **16** | 9 | 10 | 2 |

**目標の「最大5語」は3記事とも達成できなかった(実測10〜16語、目標の
2〜3倍)。** これは正直に未達として報告する。実際に検出された語は以下の
通り(各語1回のみ掲載)。

- **A01のbeyond_a2_general**: target, half-time, ahead, reach, bench, title, row, lead, defend, turn
- **A02のbeyond_a2_general**: aged, period, run, ban, step, break, habit, cut, still, move, suggestion, simply
- **ADD03のbeyond_a2_general**: announce, buyer, carrier, deal, goods, key, load, market, payment, reach, rise, seller, strike, warning

これらを見ると、"ahead"、"reach"、"lead"、"still"、"move"、"deal"、
"market"のように、一般的な感覚では比較的平易に思える語も含まれており、
LLM QAの判定基準がやや厳しめである可能性がある(正式wordlistがない
以上、この判定自体が絶対的な基準ではないことに注意)。一方で
"half-time"、"title"、"row"(a row=連続)、"payment"、"warning"のように、
確かにA2にはやや高いと考えられる語も含まれる。

**専門語例外(specialist_exception)として正しく分離された語の例**:
referee, assist, defender, striker(A01) / switch-off, setting, default,
notification, autoplay, feed, post, scroll(A02) / barrel, blockade,
crude, tanker, toll, freedom, navigation, strait(ADD03)。これらは
beyond_a2_generalの5語制限には含めていない。

**この結果をどう扱うか、ユーザー判断を仰ぎたい**([OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-17):
(a) 上限を緩和する、(b) QA結果を本文へフィードバックして反復修正する
仕組みを別途新設する(今回は未実装)、(c) 目安・努力目標として運用し
厳密なgateにはしない、のいずれかをご検討いただきたい。

## 9. 数字QA(1文1数字)

| 記事 | 数字を含む文数 | 複数数字となった文 |
|---|--:|--:|
| A01 | 4 | **0** |
| A02 | 6 | **0** |
| ADD03 | 9 | **1** |

ADD03で1件、"On July 13, 2026, U.S. President Donald Trump announced a
new plan."が複数数字(13と2026)として検出された。これは「月+日+年」の
日付表記を1つの数字表現として扱うべきかどうかがユーザー指定の例外
リスト(年齢範囲/スコア/時間帯)に含まれておらず、判定が未確定なため
生じている([OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-18)。日付を単位数字が
2つ連続する形で書くこと自体は、リスニング上大きな負荷になるとは
考えにくく、実質的な違反というよりは仕様の解釈余地の問題である
可能性が高い。

数字の丸めは行っていない($84.73、4.9 billion yen等、原数字の精度を
維持)。

## 10. 抽象語→具体的行動表現の代表例(5件以上)

| # | A2-02(抽象的) | A2-03(具体的) |
|---|---|---|
| 1 | "England changed its plan. The team focused on defense and tried to protect its lead."(A01) | "The team put more players at the back with five minutes left."(具体的な行動) |
| 2 | "The results show that default settings can guide people's choices."(A02) | "Still, the first setting changed what many children did."(誰が何をしたか) |
| 3 | "The government wants to make late-night scrolling less automatic."(A02) | "The government wants this first setting to slow teenagers down."(主語→動詞→目的語が明確) |
| 4 | "The main risks in the strait did not disappear."(ADD03) | "The fee was gone, but the danger was not."(対句で具体的な対比) |
| 5 | "Oil traders worried most about whether the route was safe."(ADD03) | "Traders asked a more important question: Could ships pass through safely?"(直接的な疑問文で提示) |
| 6 | "This came during growing tensions between the United States and Iran. The proposed charge also added to market fears."(ADD03) | "People worried about more fighting between the United States and Iran. The planned fee also helped push the price up."(「誰が」を明示) |

## 11. Spoken-firstの代表例(5件以上)

| # | A2-02(書き言葉寄り) | A2-03(spoken-first) |
|---|---|---|
| 1 | "With five minutes left, England changed its plan."(長い前置詞句が文頭) | "The team put more players at the back with five minutes left."(主語"The team"が最初) |
| 2 | "After the change, Brent fell from a daily high above $87."(前置詞句が文頭) | "Brent then fell from its highest price that day."(主語"Brent"が最初) |
| 3 | "This came during growing tensions between the United States and Iran."(代名詞"This"で始まり内容が遅れる) | "People worried about more fighting between the United States and Iran."(主語"People"、動詞"worried"がすぐ出る) |
| 4 | "The main risks in the strait did not disappear."(長い主語句"The main risks in the strait") | "The fee was gone, but the danger was not."(短い主語×2、対句) |
| 5 | "Oil traders worried most about whether the route was safe."(whether節が文末に来て最後まで聞く必要がある) | "Traders asked a more important question: Could ships pass through safely?"(疑問文化により構造が単純化) |

**注記(正直な観察)**: 全ての文で完全にspoken-firstが徹底されたわけ
ではない。例えばA02では逆にA2-02より前置詞句が文頭に増えた箇所がある
("During that time, apps under the plan would not open at first.")。
これはspoken-firstが「厳格な文法ルール」ではなくスタイル上の優先事項
として指示されているため、完全な徹底は保証されない。

## 12. 情報保持QA(A2-02主要factとの比較)

ER-003-A2-02の報告書(10節)で確認した主要fact一覧を基準に、A2-03での
状態を確認した。

**結果: 3記事・全fact(A01=11件、A02=10件、ADD03=10件、合計31件)が
全てretained。今回新たに削除されたfactは0件だった。**

特に、A2-02で回復させた「A01の連覇の可能性」「A02の"urge to watch"の
概念("just one more" habit)」「ADD03の課税名目・メッセージ転換の対比」
は、A2-03でもすべて保持されていることを確認した(ADD03のメッセージ
転換は、A2-03では直接引用"Pay to pass." / "Invest in the United
States."という形でさらに明瞭に提示されている)。

## 13. Full Story比重(A2-02との比較)

| 記事 | A2-02 FS:Points(比率) | A2-03 FS:Points(比率) |
|---|---|---|
| A01 | 206:152(1.35) | 200:140(1.43) |
| A02 | 197:165(1.19) | 179:167(1.07) |
| ADD03 | 256:127(2.02) | 260:123(2.11) |

A2-02で回復したFull Story優位の構造は、A2-03でも維持されている
(3記事ともFull Story語数がPoints語数を上回る状態を継続)。極端に
短くなる再発は確認されなかった。

## 14. 固有名詞密度(A2-02との比較)

既知の固有名詞トークンの出現回数を、A2-02とA2-03で比較した(同一の
語をカウント、複数語の名前は語ごとに数える)。

| 記事 | A2-02固有名詞トークン数 | A2-03固有名詞トークン数 |
|---|--:|--:|
| A01 | 49 | **40**(減少) |
| A02 | 6 | 6(変化なし、元々最小限) |
| ADD03 | 18 | **24**(増加) |

A01は"Fernández"(姓のみ)の反復が減り"Enzo"表記が増える等、ご指示
どおりの簡略化が確認できた。一方ADD03は"Trump"の反復が3回→8回に増加した。
これは、spoken-first・具体化(誰が何をしたか)を優先した結果、
「誰であるか自体がニュース理解に重要な人物は保持する」という原則
どおりTrumpを主語に据えた短文が増えたためであり、意図的な簡略化ルール
と、意図的な具体化ルールが競合した結果と考えられる。事実関係を曖昧に
した結果ではないため、原則には反していないが、正直な観察として報告する。

## 15. 構造について

構造(Preview/Key Phrases/Full Story/Point One/Point Two/In One Line)
は変更していない。ER-003-A2-STRUCT-01の2候補(ブロック分割+signpost、
Listening Questions)は引き続き[OPEN_ITEMS.md](OPEN_ITEMS.md)の
OPEN-13/OPEN-14に`CANDIDATE / NOT_ADOPTED`のまま記録されている。

## 16. Source of Truth更新

ER-003-A2-03のステータスは`PROTOTYPE / UNDER_REVIEW`のまま、
CURRENT_SPECへは反映していない。今回の検証結果は
[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-01(全体)・OPEN-17(語彙5語制限が
未達)・OPEN-18(1文1数字の日付例外が未決定)へ記録した。ユーザー承認後、
DECISION_LOG/CURRENT_SPECへ昇格する。

## 17. 作成・変更ファイル

- 新規: [er003_v1_translator_briefs/a2_p1_r3_prompt_template.txt](er003_v1_translator_briefs/a2_p1_r3_prompt_template.txt)
- 新規: [er003_v1_translator_briefs/a2_vocab_qa_prompt_template.txt](er003_v1_translator_briefs/a2_vocab_qa_prompt_template.txt)
- 新規: [er003_v1_a2_p1_r3_generate.py](er003_v1_a2_p1_r3_generate.py)
- 更新: [er003_a2_article.py](er003_a2_article.py)(語彙QA・数字QA関数を追加、数字正規表現のバグを修正。既存のB1/B2/A2-01/A2-02関数は変更なし)
- 新規: `er003_output/a2_p1_r3/{A01,A02,ADD03}/*`(A2-03生成テキスト・prompt・metrics・語彙QA結果)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)(OPEN-01更新、OPEN-17/18追加)
- 既存の凍結モジュール(`er003_ja_to_en_translation_p1b.py`等)は一切変更していない

## 18. テスト結果

プロジェクト全体回帰テスト: **1660件全合格**。

## 19. Git status / commit / push

commit済み(pushなし)。**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[ER-003-A2-02_INFO_BALANCE_VERIFICATION.md](ER-003-A2-02_INFO_BALANCE_VERIFICATION.md)
