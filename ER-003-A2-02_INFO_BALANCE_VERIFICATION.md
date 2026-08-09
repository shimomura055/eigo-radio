# ER-003-A2-02 A2情報量・Full Story比重修正

**管理ID: ER-003-A2-02**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / NOT_APPROVED`(テキストのみ、ユーザー判断待ち)**
**スコープ: テキスト再生成・比較のみ。音声生成・構造変更・Key Phrase最終選定は行っていない。**

## 結論(先に要約)

ER-003-A2-01の問題(Full Storyの情報比重崩壊)を確認・修正した。
**Full Story語数シェアは3記事とも12.5〜29%からB1同等の52〜65%まで回復し、
総語数もB1と同程度(またはやや上回る水準)に戻った。** 文長仕様(平均11語
以下・最長18語以下・1文1メッセージ)は維持したまま達成している。

## 1. 変更したprompt(A2-01→A2-02)

- 「情報量はB1より明確に削減する」という考え方を廃止し、「総語数削減を
  目的にしない」旨を明記
- A2化の優先順位を明示: ①1文の情報量を減らす→②長文分割→③構文単純化→
  ④語彙平易化→⑤代名詞参照明確化→⑥それでも複雑な場合のみ周辺情報を削る
- 「11語以下にするために重要情報を削除するな。文を追加して分割することを
  優先せよ」を明記
- Full Storyは主要事実(何が起きたか・誰が・なぜ重要か・重要な数字)を
  単独で含む主役であり、Point One/Point Twoで初めて主要事実が登場する
  構造を禁止
- Point One/Point TwoはFull Storyの単純な反復ではなく、深掘り・背景・
  意味・注目点を提供する役割と明記

新旧prompt: [a2_p1_prompt_template.txt](er003_v1_translator_briefs/a2_p1_prompt_template.txt)(A2-01)、
[a2_p1_r2_prompt_template.txt](er003_v1_translator_briefs/a2_p1_r2_prompt_template.txt)(A2-02)

## 2. 生成元

A2-01と同じくNatural English Sourceから独立生成(B1・B2・A2-01いずれの
本文も入力に使用していない。`generation_metadata.json`の
`b1_body_used_as_input`/`b2_body_used_as_input`/`a2_r1_body_used_as_input`
はすべて`false`)。

## 3〜5. A2-02本文(3記事全文)

### A01(サッカー記事)

> # Argentina Beat England After Two Late Goals
>
> On July 15, 2026, Argentina beat England 2–1 in Atlanta. The World Cup match renewed the teams' famous rivalry.
>
> The game had a quiet first half. Neither team had a shot on target before half-time. The players made strong challenges. The match stayed tense, but no one scored.
>
> England broke the tie in the 55th minute. Rogers sent a cross into the box. Gordon reached the ball and put England ahead.
>
> England started to dream about the World Cup final. England last reached the final in 1966.
>
> With five minutes left, England changed its plan. The team focused on defense and tried to protect its lead.
>
> But Argentina scored in the 85th minute. Messi passed the ball to Enzo Fernández. Fernández hit a powerful shot to make the score 1–1.
>
> Argentina attacked again during stoppage time. Messi crossed the ball from the right. Substitute Lautaro Martínez scored with a strong header.
>
> Argentina turned the match around in only seven minutes. England's joy became pain. Argentina's pain became joy.
>
> The win sent Argentina to the World Cup final against Spain. Argentina can now win two World Cup titles in a row. England lost its chance to return to the final.
>
> ## Today's Match-Turning Points
>
> ### Point One: Messi Created Both Goals
>
> Messi did not score, but he still decided the match. At 39, Argentina's captain gave two assists.
>
> An assist is the final pass before a teammate scores. First, Messi found Enzo Fernández. Later, Messi crossed the ball to Lautaro Martínez.
>
> Enzo and Lautaro took the final shots. However, Messi opened the way for both goals. He showed that a player can control a game without scoring.
>
> ### Point Two: The Teams Made Opposite Choices
>
> The two teams made very different choices near the end.
>
> England took off players, including Rice. The team put more strength into its defense. England wanted to keep its 1–0 lead.
>
> Argentina chose to attack. In the 81st minute, Argentina took defender Tagliafico off. Striker Lautaro Martínez came onto the field.
>
> Lautaro later scored the winning goal. Argentina's attacking choice changed the result. England's defensive plan did not work.
>
> ## In One Line
>
> England tried to defend its lead, but Messi created two late goals for Argentina.

全文: [er003_output/a2_p1_r2/A01/a2_article_raw.md](er003_output/a2_p1_r2/A01/a2_article_raw.md)

### A02(SNS規制記事)

> # UK Plans a Night-Time Social Media Break for Teenagers
>
> At midnight, social media may soon say "goodnight" to UK teenagers.
>
> On July 15, the British government announced a new plan. The plan would affect teenagers aged 16 and 17.
>
> It would create a "digital switch-off period." This period would run from midnight until 6 a.m.
>
> Apps in the plan would be unavailable during these hours. This would be the normal setting on the apps. A normal setting is also called a default.
>
> Notifications would stop during the switch-off period. Autoplay would also stop. Autoplay starts a new video after another video ends.
>
> Personal recommendation feeds would stop too. These feeds choose posts and videos for each user. They can keep people scrolling for a long time.
>
> The new measures may start in spring 2027.
>
> However, the plan is not a complete ban. Teenagers could change the settings and opt out. They could then use the apps during the night.
>
> The government wants to make late-night scrolling less automatic. Teenagers would need to stop and change the setting first.
>
> This small extra step may stop the urge for "one more" video. The plan aims to support better sleep without a strict ban.
>
> ## Today's Late-Night Scrolling Points
>
> ### Point One: Night Limits May Help Sleep
>
> A trial studied 309 families. It compared three ways to control screen time.
>
> One approach blocked screens from 9 p.m. until 7 a.m. Families found this approach the easiest to manage.
>
> Better sleep was also reported more regularly with the night limits.
>
> However, some teenagers changed their screen time. They used screens just before or after the blocked hours.
>
> This shows one important problem. Night limits may help, but they cannot solve everything.
>
> ### Point Two: Default Settings Can Guide Choices
>
> Ofcom ran a separate experiment with children.
>
> One setting stopped apps from recommending harmful content. Ofcom made this setting the default for some children.
>
> About seven in ten children kept the default setting.
>
> Other children did not receive a default choice. Only about half of these children chose the safer setting.
>
> The setting was not required. Children could still change it.
>
> The results show that default settings can guide people's choices. They can change behavior without forcing anyone.
>
> ## In One Line
>
> The UK hopes a small night-time pause will help more teenagers stop scrolling and sleep.

全文: [er003_output/a2_p1_r2/A02/a2_article_raw.md](er003_output/a2_p1_r2/A02/a2_article_raw.md)

### ADD03(ホルムズ海峡記事)

> # Trump Ends Hormuz Fee Plan, but Oil Markets Stay Worried
>
> On July 13, 2026, U.S. President Donald Trump announced a new plan.
>
> All cargo passing through the Strait of Hormuz would face a charge. The charge would equal 20 percent of the cargo's value.
>
> Trump said the money would help keep the waterway safe. The strait is a vital route for the world's energy supplies.
>
> The plan could cost one giant oil tanker about $30 million. It also raised serious questions about international law.
>
> One day later, the plan was withdrawn. Instead, Gulf nations would seek trade and investment deals with the United States.
>
> The possible amount of investment stayed unclear. It was also unclear which countries would join.
>
> At first, the message was: pay 20 percent to pass. The next day, the message was: invest in the United States instead.
>
> The policy changed greatly in only 24 hours. However, oil markets did not fully relax.
>
> On July 13, Brent crude oil prices jumped about 10 percent. This came during growing tensions between the United States and Iran. The proposed charge also added to market fears.
>
> After the change, Brent fell from a daily high above $87. However, Brent closed at $84.73 a barrel on July 14.
>
> The price was still up about 2 percent that day. It was also at its highest level in one month.
>
> The main risks in the strait did not disappear. The blockade aimed at Iran-linked ships continued. Military strikes continued too.
>
> Oil traders worried most about whether the route was safe. Passing costs mattered, but ship safety mattered more.
>
> ## Today's Hormuz Risk Points
>
> ### Point One: A $30 Million Cost for One Tanker
>
> The $30 million example involved a fully loaded Very Large Crude Carrier. This is a very large tanker for crude oil.
>
> The possible fee was about 4.9 billion yen. Shipping businesses received no warning before Trump's announcement.
>
> This lack of warning caused shock and serious doubts across the industry.
>
> ### Point Two: A Toll May Break International Rules
>
> On July 13, the International Maritime Organization repeated a basic rule.
>
> Ships in the Strait of Hormuz should not face tolls or transit fees. This rule comes from international law.
>
> The rule supports freedom of navigation. This means ships can move freely through important international waterways.
>
> The fee plan therefore created more than market fear. It also went directly against this basic international rule.
>
> ## In One Line
>
> The fee is gone, but danger in the strait still worries oil markets.

全文: [er003_output/a2_p1_r2/ADD03/a2_article_raw.md](er003_output/a2_p1_r2/ADD03/a2_article_raw.md)

## 6. 総語数比較(B1 / A2-01 / A2-02)

| 記事 | B1総語数 | A2-01総語数 | A2-02総語数 |
|---|--:|--:|--:|
| A01 | 290 | 199 | **352** |
| A02 | 339 | 270 | **354** |
| ADD03 | 358 | 231 | **370** |

3記事ともA2-02はB1と同程度、またはB1をやや上回る語数になった
(短文分割により文が増えた自然な結果であり、意図的な語数目標は
設定していない)。

## 7. 平均文長・最長文

| 記事 | B1平均 | A2-01平均 | A2-02平均 | B1最長 | A2-01最長 | A2-02最長 |
|---|--:|--:|--:|--:|--:|--:|
| A01 | 9.67語 | 7.37語 | 8.00語 | 15語 | 15語 | 14語 |
| A02 | 10.59語 | 8.18語 | 8.43語 | 19語 | 16語 | 15語 |
| ADD03 | 10.53語 | 8.56語 | 9.25語 | 17語 | 13語 | 13語 |

3記事とも受入条件(平均11語以下・最長18語以下)を達成している。
A2-01よりわずかに平均語数が増えているが、これは短い文を複数追加して
情報を分割した結果であり、文の複雑さが増したわけではない(9節の
ヒューリスティックQA参照)。

## 8. Full Story比重(最重要指標)

| 記事 | B1 Full Story語数(シェア) | A2-01 Full Story語数(シェア) | A2-02 Full Story語数(シェア) |
|---|---|---|---|
| A01 | 155語(49.2%) | 36語(**16.5%**) | 206語(**55.4%**) |
| A02 | 179語(48.8%) | 37語(**12.5%**) | 197語(**52.3%**) |
| ADD03 | 237語(62.0%) | 73語(**29.0%**) | 256語(**64.6%**) |

**これがA2-01の核心的な問題だった。** A2-01ではFull Storyが記事全体の
語数の12.5〜29%しか占めておらず、主要事実の大半がPoint One/Point Twoへ
押し出されていた。A2-02では3記事ともB1と同等かそれ以上のFull Story比重
(52.3〜64.6%)を達成し、「Full Storyだけでニュースの中核を理解できる」
という受入条件を満たしている。

## 9. 文法ヒューリスティックQA(A2-01との比較)

| 記事 | 指標 | A2-01 | A2-02 |
|---|---|--:|--:|
| A01 | 関係詞候補 | 0 | 0 |
| A01 | 受動態候補 | 0 | 0 |
| A02 | 関係詞候補 | 0 | 0 |
| A02 | 受動態候補 | 0 | 0 |
| ADD03 | 関係詞候補 | 1 | 0 |
| ADD03 | 受動態候補 | 0 | 0 |

情報量を回復してもA2-01の文法単純化(関係詞・受動態の排除)は維持されている。
むしろADD03は関係詞候補が1件→0件へ改善した。

## 10. B1/A2-01/A2-02の主要fact保持状況(retained/simplified/removed)

**凡例: R=retained(そのまま保持) / S=simplified(平易化されたが事実は保持) /
X=removed(その版に存在しない)。Natural Source(NS)・B2は参考として併記。**

### A01(サッカー記事)

| # | 主要fact | NS | B2 | B1 | A2-01 | A2-02 |
|---|---|---|---|---|---|---|
| 1 | 日時・場所(2026/7/15、アトランタ) | R | R | R | R(FS) | R(FS) |
| 2 | 最終スコア(Argentina 2–1 England) | R | R | R | R(FS) | R(FS) |
| 3 | 前半無得点・拮抗 | R | R | R | R(FS) | R(FS) |
| 4 | England先制(Rogers→Gordon、55分) | R | R | R | R(FS) | R(FS) |
| 5 | England 1966以来の決勝進出への期待 | R | R | R | R(FS) | R(FS) |
| 6 | 残り5分、Englandが守備固め | R(比喩) | R(比喩) | S(比喩解消) | **X(Points内のみ)** | **R(FS復帰)** |
| 7 | Messiアシスト→Enzo Fernández同点、85分 | R | R | R | R(FS) | R(FS) |
| 8 | ロスタイム、Messiクロス→Lautaro決勝点 | R | R | R | R(FS) | R(FS) |
| 9 | Messiは無得点だが試合を支配 | R | R | R | R(Points) | R(Points) |
| 10 | 選手交代の対比(England守備的/Argentina攻撃的) | R | R | R | R(Points) | R(Points) |
| 11 | 決勝でスペインと対戦、連覇の可能性 | R(連覇言及あり) | R | R(連覇言及あり) | **X(連覇言及消失)** | **R(FS復帰、連覇言及も復活)** |

### A02(SNS規制記事)

| # | 主要fact | NS | B2 | B1 | A2-01 | A2-02 |
|---|---|---|---|---|---|---|
| 1 | UK政府が7/15に発表 | R | R | R | R(FS) | R(FS) |
| 2 | 16-17歳対象、深夜0-6時 | R | R | R | R(FS) | R(FS) |
| 3 | アプリ既定無効・通知停止・自動再生停止 | R | R | R | R(FS) | R(FS) |
| 4 | おすすめフィードも停止 | R | R | R | R(FS) | R(FS) |
| 5 | 2027年春開始予定 | R | R | R | R(FS) | R(FS) |
| 6 | opt-out可能(完全禁止ではない) | R | R | R | R(FS) | R(FS) |
| 7 | 「もう一本見たい衝動("urge to watch just one more")」という狙いの説明 | R | R | R | **X** | **R(FS復帰)** |
| 8 | 309家族の実験、9-7時が最も管理しやすい | R | R | R | R(Points) | R(Points) |
| 9 | 一部生徒が時間帯をずらした問題点 | R | R | R | R(Points) | R(Points) |
| 10 | Ofcom実験(約7割 vs 約5割) | R | R | R | R(Points) | R(Points) |

### ADD03(ホルムズ海峡記事)

| # | 主要fact | NS | B2 | B1 | A2-01 | A2-02 |
|---|---|---|---|---|---|---|
| 1 | Trump、7/13に20%課税案発表 | R | R | R | R(FS) | R(FS) |
| 2 | 課税の名目(航路の安全確保) | R | R | R | **X** | **R(FS復帰)** |
| 3 | 1日で撤回、代わりに投資取引を模索 | R | R | R | R(FS) | R(FS) |
| 4 | 金額・対象国が不明確 | R | R | R | R(FS) | R(FS) |
| 5 | メッセージの転換("pay 20%"→"invest instead") | R(引用構造) | R | R | **X** | **R(FS復帰)** |
| 6 | 原油価格反応(Brent+10%、米イラン緊張) | R | R | R | **X(Points内のみ)** | **R(FS復帰)** |
| 7 | 撤回後の価格推移($87超→$84.73、+2%、1ヶ月ぶり高値) | R | R | R | S(Points内) | R(FS復帰) |
| 8 | 高値継続の理由(封鎖・軍事行動が継続) | R | R | R | **X(Points内のみ)** | **R(FS復帰)** |
| 9 | Point One: タンカー1隻$30M、約4.9億円、無警告 | R | R | R | R(Points) | R(Points)、**要点はFSにも先出し** |
| 10 | Point Two: IMOのルール再確認、航行の自由の原則 | R(freedom of navigation) | R | R | S("free travel at sea"へ言い換え) | **R("freedom of navigation"の用語も復活)** |

**まとめ**: A2-01で実際に「完全に消えていた」fact(X)は各記事1〜3件程度
だったが、それに加えて**多くのfactがFull StoryからPointsへ場所を
移動していた**(この表で「Points内のみ」と注記した項目)。これが
Full Story比重崩壊の主因である。A2-02はこの両方――genuinely removed
だったfactの復元と、Full Storyへの再配置――を達成している。

**特に注意すべき点**: 「重要なfactがA2だからという理由だけで削除されて
いた」ケースは、A01の「連覇の可能性」、A02の「'urge to watch'という
狙いの説明」、ADD03の「課税の名目」「メッセージ転換の対比構造」の
4件程度に限られていた。残りの大多数は削除ではなく**配置の問題**
だったことが、この表で定量的に裏付けられた。

## 11. Full StoryとPointsの語数比率

| 記事 | B1(FS:Points) | A2-01(FS:Points) | A2-02(FS:Points) |
|---|---|---|---|
| A01 | 155:121(1.28) | 36:167(**0.22**) | 206:152(**1.35**) |
| A02 | 179:142(1.26) | 37:242(**0.15**) | 197:165(**1.19**) |
| ADD03 | 237:106(2.24) | 73:166(**0.44**) | 256:127(**2.02**) |

A2-01では3記事ともFull StoryよりPointsの方が語数が多く(比率1未満)、
「Pointsで初めて主要情報が大量に登場する」状態になっていた。A2-02では
3記事ともFull StoryがPointsと同等以上(比率1.19〜2.02)まで回復し、
B1の比率(1.26〜2.24)に近い水準になっている。

## 12. 比喩・Key Phrase相当語の扱いについて(OPEN-15の再整理)

ご指示のとおり、B1で承認済みだったKey Phrase相当の比喩("giant
tollbooth"、"smell of gunpowder"、"urge to watch"等)がA2本文にそのまま
残るかどうかは、今回の受入条件から外した。実際、A2-02でも"tollbooth"や
"smell of gunpowder"という単語そのものは登場しない(自然さを優先した結果)。
一方で、"urge to watch"の概念自体("urge for 'one more' video")と、
"freedom of navigation"という用語そのものは、A2-02では自然な形で復活
している。これは狙って残したわけではなく、Full Storyへ主要事実を
戻した結果として付随的に起きたことである。

[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-15を、「B1 Key Phrase語の消失」を
問題とする記載から、「対応不要、方針確定」へ更新した。A2 Key Phraseは
今後A2-02本文が確定した後、本文から方式L+Canonicalizationで改めて
選定する(B1と同じ手順)。

## 13. 構造について

今回も構造(Preview/Key Phrases/Full Story/Point One/Point Two/In One Line)
は変更していない。構造支援候補(Full Storyブロック分割+signpost、
Listening Questions)は引き続き[OPEN_ITEMS.md](OPEN_ITEMS.md)の
OPEN-13/OPEN-14に`CANDIDATE / NOT_ADOPTED`のまま記録されている。

## 14. 作成・変更ファイル

- 新規: [er003_v1_translator_briefs/a2_p1_r2_prompt_template.txt](er003_v1_translator_briefs/a2_p1_r2_prompt_template.txt)
- 新規: [er003_v1_a2_p1_r2_generate.py](er003_v1_a2_p1_r2_generate.py)
- 更新: [er003_a2_article.py](er003_a2_article.py)(セクション別語数計測`split_article_sections`/`compute_section_word_counts`を追加、既存関数は変更なし)
- 更新: [er003_v1_a2_b1_compare.py](er003_v1_a2_b1_compare.py)(A2-02を比較対象に追加)
- 新規: `er003_output/a2_p1_r2/{A01,A02,ADD03}/*`(A2-02生成テキスト・prompt・metrics)
- 新規: `er003_output/a2_p1_r2/b1_vs_a2r1_vs_a2r2_comparison.json`
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)(OPEN-15を再整理、OPEN-16を追加)
- 既存のA2-01成果物(`er003_output/a2_p1/`)は上書きせず保持(比較の証跡として維持)

## 15. テスト結果

プロジェクト全体回帰テスト: **1660件全合格**。既存の凍結モジュール
(`er003_b1_article.py`等)は変更していない。

## 16. Git status / commit / push

commit済み(pushなし)。詳細はcommitログ参照。**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[ER-003-A2-01_TEXT_VERIFICATION.md](ER-003-A2-01_TEXT_VERIFICATION.md)
