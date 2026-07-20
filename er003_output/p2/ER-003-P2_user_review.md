# ER-003-P2 ユーザー評価用レビュー

B2本文調整パイロット。Natural English Source(P1B確定版)を入力とし、CEFR B2学習者向けに語彙・文長・情報密度を調整しました。日本語原稿・P1/P1Bの生応答・Web検索結果・fact registry・英語マスターはB2 adapterへ一切渡していません。

このレビューには、英語の自然さ・感情・聞きやすさについてのClaude Code・adapter・QAモデル自身の主観評価は一切含まれていません。推定読み上げ時間は音声時間の保証ではない参考値、推定CEFRは機械的な確定値ではなく参考的な判断です。

リポジトリ内に既存の語彙・頻度リスト資源は見つからなかったため、新規の外部語彙リストは導入していません。

**ER-003-P2A訂正**: 文長計測ロジック(sentence splitter)に、段落境界とカーリークォートを正しく扱えないバグがあり、A02・ADD03で実在しない長文(59語・37語)を計測していました。ロジック修正後、B2本文を一切変更せずに再計測した結果、3記事すべて`B2_SENTENCE_METRICS_PASS`です。以下の表・ゲート記述は訂正後の値です。旧値は`sentence_metrics.json`(監査記録)および`P2A_metrics_supersession_manifest.json`に保存されています。

---

## A01: 2026年ワールドカップ準決勝のイングランド対アルゼンチン

| 指標 | Natural Source | B2版 |
|---|---|---|
| 英単語数(本文のみ/見出し込み) | 340語 | 298語 / 337語 |
| 平均文長 | 14.17語/文 | **11.46語/文** |
| 最長文 | 27語 | **24語** |
| 32語超の文数 | - | 0文 |
| 推定CEFR | B2-C1 | **B2** |

- **構造ゲート: 初回合格**(再試行なし)
- 生成された固定見出し: `Today's Match-Turning Points` / `Point One: Messi Wasn't the Scorer—He Was the Creator` / `Point Two: One Team Substituted to Defend; the Other, to Attack` / `In One Line`あり
- **B2整合性QA: PASS**
- **B2難易度QA: PASS**(above-B2候補: "renewed their famous rivalry" 等7件。必須専門語: shot on target, cross, stoppage time等)
- **文長ゲート: B2_SENTENCE_METRICS_PASS**(平均・最長文とも基準内)

### B2版全文

# ⚽ Five Minutes from the Final—Then the Champions Made Time Their Ally

July 15, 2026, in Atlanta.

England and Argentina renewed their famous rivalry in a match with an ending no one could have imagined after such a quiet first half.

Neither team managed a single shot on target before the break. The challenges were fierce, and the tension never went away. But neither team could find a goal.

Then, in the 55th minute, Rogers sent in a cross. Gordon met it, and England took the lead.

At last, England could dream of reaching their first World Cup final since 1966.

With five minutes left, England strengthened their defense and reached for the door to the final.

But in the 85th minute, Messi found Enzo Fernández. Enzo fired a powerful shot to make it 1–1.

Then came stoppage time.

Messi sent in a cross from the right. Substitute Lautaro Martínez powered a header into the net.

In just seven minutes, celebration and despair had traded places.

**England 1–2 Argentina**

## Today's Match-Turning Points

### Point One: Messi Wasn't the Scorer—He Was the Creator

At 39, the captain provided two assists that night. He did not take the final shots himself. Instead, he opened the way for Enzo and Lautaro to deliver the decisive blows.

Messi showed once again that you do not have to score to control a game—or to bring it to an end.

### Point Two: One Team Substituted to Defend; the Other, to Attack

England took off players including Rice and strengthened their defense, hoping to protect their lead.

Argentina went the other way. In the 81st minute, they replaced defender Tagliafico with striker Lautaro Martínez.

Lautaro then scored the winning goal.

The direction of each team's substitutions became the direction of its fate.

## In One Line

"England tried to close the door to the final. Messi slipped two keys through the gap."

Argentina now advance to face Spain, with back-to-back titles on the line. England are left with the crushing weight of those final five minutes.

### ユーザー評価(A01)

- B2学習者がリスニングで理解しやすい(はい / 一部 / いいえ): 
- Natural Sourceより理解しやすい(はい / 一部 / いいえ): 
- 英語として自然(はい / 一部 / いいえ): 
- 過度に単純化されている(いいえ / 一部 / はい): 
- 記事の勢いを維持している(はい / 一部 / いいえ): 
- 切り口を維持している(はい / 一部 / いいえ): 
- `In One Line`の魅力を維持している(はい / 一部 / いいえ): 
- 情報不足(なし / 少し / 大きい): 
- 難しい語彙が多すぎる(いいえ / 一部 / はい): 
- 長い文がまだ負担(いいえ / 一部 / はい): 
- B2版として採用可能(はい / 軽微修正後 / いいえ): 
- 総合判定(ACCEPT / LIGHT_EDIT_NEEDED / REWRITE_REQUIRED): 
- コメント: 

---

## A02: 英国の未成年向け夜間SNS設定

| 指標 | Natural Source | B2版 |
|---|---|---|
| 英単語数(本文のみ/見出し込み) | 418語 | 396語 / 435語 |
| 平均文長 | 19.90語/文 | **12.00語/文** |
| 最長文 | 61語 | **28語** |
| 32語超の文数 | - | 0文 |
| 推定CEFR | B2 | B2 |

- **構造ゲート: 初回合格**(再試行なし)
- 生成された固定見出し: `Today's Late-Night Scrolling Points` / `Point One: A Nighttime Pause Proved More Practical Than a Total Ban` / `Point Two: Even Optional Defaults Can Change Behavior` / `In One Line`あり
- **B2整合性QA: PASS**
- **B2難易度QA: PASS**(above-B2候補: "opt out", "shape the default experience" 等6件。必須専門語: digital switch-off period, autoplay, personalized recommendation feeds等)
- **文長ゲート: B2_SENTENCE_METRICS_PASS**(ER-003-P2Aで文分割ロジックを修正し再計測。旧計測の「59語」は段落境界の誤連結による誤計測で、本文には存在しない)

### B2版全文

# Midnight Means Goodnight: The UK's Quiet Plan to Limit Late-Night Scrolling

At midnight, social media may soon start saying "goodnight" to teenagers in the UK.

On July 15, the British government announced plans for a **digital switch-off period** for 16- and 17-year-olds. It would run from midnight to 6 a.m.

During those hours, apps covered by the plan would be unavailable by default. Notifications would also be paused.

Autoplay is the feature that keeps videos coming one after another. It would be switched off too.

Personalized recommendation feeds would also be turned off. These feeds are designed to keep users scrolling endlessly.

The new measures are expected to take effect in the spring of 2027.

But this would not be a locked gate.

Teenagers aged 16 and 17 would still be able to change the settings and opt out.

So, wouldn't everyone simply turn the restrictions off?

Perhaps. But the UK's strategy is not mainly about giving orders. It is about shaping the **default experience**.

To open an app in the middle of the night, users would first have to pause. Then they would need to actively choose to turn off the setting.

In other words, the plan puts a small speed bump before the automatic urge to watch "just one more."

## Today's Late-Night Scrolling Points

### Point One: A Nighttime Pause Proved More Practical Than a Total Ban

In a trial involving 309 families, nighttime restrictions ran from 9 p.m. to 7 a.m.

They were considered the easiest of three approaches to manage. They also produced the most consistent reports of better sleep.

However, some teenagers simply moved their screen time to just before or after the restricted hours. So, closing off the night does not automatically solve the wider problem.

### Point Two: Even Optional Defaults Can Change Behavior

In a separate experiment by Ofcom, around seven in ten children kept a safety setting when it was selected by default. The setting stopped harmful content from being recommended.

When no option was selected in advance, that figure fell to around half.

The setting was optional, not required. But the results suggest that defaults alone can be powerful enough to guide people's choices.

## In One Line

**"What the UK is trying to switch off is not the glow of the smartphone, but the endless current of scrolling that carries teenagers right up to bedtime."**

This midnight speed bump sits somewhere between a strict ban and a complete hands-off approach.

Its success will not depend on how many teenagers change the setting. It will depend on how many more nights they leave it untouched—and simply go to sleep.

### ユーザー評価(A02)

- B2学習者がリスニングで理解しやすい(はい / 一部 / いいえ): 
- Natural Sourceより理解しやすい(はい / 一部 / いいえ): 
- 英語として自然(はい / 一部 / いいえ): 
- 過度に単純化されている(いいえ / 一部 / はい): 
- 記事の勢いを維持している(はい / 一部 / いいえ): 
- 切り口を維持している(はい / 一部 / いいえ): 
- `In One Line`の魅力を維持している(はい / 一部 / いいえ): 
- 情報不足(なし / 少し / 大きい): 
- 難しい語彙が多すぎる(いいえ / 一部 / はい): 
- 長い文がまだ負担(いいえ / 一部 / はい): 
- B2版として採用可能(はい / 軽微修正後 / いいえ): 
- 総合判定(ACCEPT / LIGHT_EDIT_NEEDED / REWRITE_REQUIRED): 
- コメント: 

---

## ADD03: ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応

| 指標 | Natural Source | B2版 |
|---|---|---|
| 英単語数(本文のみ/見出し込み) | 407語 | 389語 / 428語 |
| 平均文長 | 16.28語/文 | **10.81語/文** |
| 最長文 | 40語 | **18語** |
| 32語超の文数 | - | 0文 |
| 推定CEFR | B2-C1 | B2-C1 |

- **構造ゲート: 初回合格**(再試行なし)
- 生成された固定見出し: `Today's Hormuz Risk Points` / `Point One: A Nearly $30 Million Shock for a Single Tanker` / `Point Two: Can You Legally Put a Tollbooth at Sea?` / `In One Line`あり
- **B2整合性QA: PASS**
- **B2難易度QA: REVIEW_REQUIRED**(above-B2候補: "on edge", "breathe a sigh of relief" 等6件。理由: 海運・原油市場・国際法に関する専門語彙が多く、予備知識のないB2学習者には部分的に難度がB2を超える可能性)
- **文長ゲート: B2_SENTENCE_METRICS_PASS**(ER-003-P2Aで文分割ロジックを修正し再計測。旧計測の「37語」は見出し直後の短文と引用ブロックの誤連結による誤計測で、本文には存在しない)

### B2版全文

# 🌊 The 20% Toll Disappeared Overnight—But the Oil Market Is Still on Edge

Imagine a giant tollbooth suddenly appearing in the Strait of Hormuz.

On July 13, 2026, U.S. President Donald Trump announced a new plan for the strait. He wanted to charge 20 percent of the value of all cargo passing through it.

Trump said the fee would pay for keeping this vital waterway safe.

But just one day later, the plan was withdrawn. Instead, Gulf nations would seek trade and investment deals with the United States.

How much money these deals would involve remained unclear. It was also unclear which countries would take part.

The message changed overnight from:

"If you want to pass through, pay 20 percent,"

to:

"Invest in the United States instead."

Within just 24 hours, a proposal that shook global energy supply routes had taken a completely different form.

So, did the markets breathe a sigh of relief?

Only partly.

Brent crude had jumped about 10 percent the day before. Tensions between the United States and Iran were rising, and markets were shocked by the proposed charge.

After the plan was dropped, prices fell from an intraday high above 87 dollars a barrel.

Even so, Brent closed on July 14 at 84 dollars and 73 cents. The price was still up about 2 percent and was Brent's highest in a month.

Why?

Because the toll was gone, but the blockade targeting ships linked to Iran was still in place. Military strikes were also continuing.

The market was never focused only on the price of passage. The bigger question was whether the strait was safe at all.

## Today's Hormuz Risk Points

### Point One: A Nearly $30 Million Shock for a Single Tanker

For a fully loaded Very Large Crude Carrier, the proposed fee could have reached about 30 million dollars. That is roughly 4.9 billion yen.

And the shipping industry had received no warning in advance.

So, it is hardly surprising that the industry reacted with both shock and doubt.

### Point Two: Can You Legally Put a Tollbooth at Sea?

On July 13, the International Maritime Organization restated an important principle under international law.

Ships passing through the Strait of Hormuz should not be charged tolls or transit fees.

In other words, the proposal did more than make the markets nervous. It also collided head-on with the basic principle of freedom of navigation.

## In One Line

**"The tollbooth sign is gone—but the smell of gunpowder still hangs over the strait."**

A change in policy may calm the headlines. But the market will not truly relax until ships can pass through the Strait of Hormuz without fear.

### ユーザー評価(ADD03)

- B2学習者がリスニングで理解しやすい(はい / 一部 / いいえ): 
- Natural Sourceより理解しやすい(はい / 一部 / いいえ): 
- 英語として自然(はい / 一部 / いいえ): 
- 過度に単純化されている(いいえ / 一部 / はい): 
- 記事の勢いを維持している(はい / 一部 / いいえ): 
- 切り口を維持している(はい / 一部 / いいえ): 
- `In One Line`の魅力を維持している(はい / 一部 / いいえ): 
- 情報不足(なし / 少し / 大きい): 
- 難しい語彙が多すぎる(いいえ / 一部 / はい): 
- 長い文がまだ負担(いいえ / 一部 / はい): 
- B2版として採用可能(はい / 軽微修正後 / いいえ): 
- 総合判定(ACCEPT / LIGHT_EDIT_NEEDED / REWRITE_REQUIRED): 
- コメント: 
