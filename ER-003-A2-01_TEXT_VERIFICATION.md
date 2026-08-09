# ER-003-A2-01 A2暫定仕様でのテキスト生成検証

**管理ID: ER-003-A2-01**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / NOT_APPROVED`(テキストのみ、ユーザー判断待ち)**
**スコープ: テキスト生成・比較のみ。音声生成・構造変更・Key Phrase最終選定は行っていない。**

## 1. 使用したA2暫定仕様

チャットで提示された暫定仕様(平均文長11語以下・最長18語以下・1文1メッセージ、
関係詞/受動態/現在完了/過去完了/分詞構文/仮定法を原則回避、等位接続詞は使用可、
情報量はB1より明確に削減しつつ「何が起きたか→誰が→なぜ重要か→重要な数字→
背景・補足」の優先順位で削る、全体語数は今回固定しない)をそのままprompt化した。
[er003_v1_translator_briefs/a2_p1_prompt_template.txt](er003_v1_translator_briefs/a2_p1_prompt_template.txt)参照。

文長閾値(平均11語/最長18語)は**診断のみでgateではない**扱いとした(B1と同じ
方針。今回は暫定仕様の検証段階であり、まだ本番のretry gateへは組み込んでいない)。

## 2. 生成元

**Natural English Sourceから独立生成した**(`er003_output/p1b/{article}/
natural_source_approved.md`)。B1本文・B2本文は生成APIへ一切渡していない
(`b1_body_used_as_input: false`, `b2_body_used_as_input: false`を
`generation_metadata.json`に記録済み)。

これにより、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-02の矛盾点(独立生成 vs
B1からの派生)について、**今回の実行分では独立生成方式を採用した**ことを
明示する。恒久的な方針としてどちらを正式仕様とするかは、引き続きユーザー
判断待ち(OPEN-02は`DECIDED`(今回分のみ)のまま、恒久方針は`UNDER_REVIEW`)。

## 3〜5. 生成したA2本文

### A01(サッカー記事)

> # Argentina Beat England with Two Late Goals
>
> Argentina beat England 2–1 in Atlanta on July 15, 2026. England led until the 85th minute. Then Messi created two goals in seven minutes. Argentina reached the World Cup final against Spain.
>
> ## Today's Match-Turning Points
>
> ### Point One: Messi Created Both Goals
>
> The first half was quiet but tense. Neither team had a shot on target.
>
> England took the lead in the 55th minute. Rogers crossed the ball, and Gordon scored.
>
> England started to dream of the final. It was England's first possible final since 1966.
>
> But Argentina fought back in the 85th minute. Messi passed to Enzo Fernández. Enzo hit a powerful shot and made the score 1–1.
>
> Messi created another chance during stoppage time. He crossed from the right. Lautaro Martínez headed the ball into the goal.
>
> Messi, 39, made both assists. He did not score, but he controlled the ending.
>
> ### Point Two: Argentina Chose to Attack
>
> England tried to protect its lead. The team took off players including Rice. England also made its defense stronger.
>
> Argentina chose a different plan. In the 81st minute, Argentina took off defender Tagliafico. Striker Lautaro Martínez came onto the field.
>
> Lautaro then scored the winning goal. The teams' different choices changed the match.
>
> ## In One Line
>
> England tried to protect its lead, but Messi opened the way to Argentina's 2–1 win.

全文: [er003_output/a2_p1/A01/a2_article_raw.md](er003_output/a2_p1/A01/a2_article_raw.md)

### A02(SNS規制記事)

> # UK Plans a Midnight Social Media Break for Teenagers
>
> The UK plans a nighttime break from social media.
>
> The British government announced the plan on July 15. It covers teenagers aged 16 and 17. The plan should start in spring 2027.
>
> ## Today's Late-Night Scrolling Points
>
> ### Point One: A Nighttime Pause, Not a Full Ban
>
> Apps under the plan will be unavailable by default overnight. The break will last from midnight to 6 a.m.
>
> Notifications will pause during these hours. Autoplay will also stop. Autoplay starts a new video after one ends.
>
> Personal recommendation feeds will also stop. These feeds can keep users scrolling for hours.
>
> Teenagers can turn the settings off. So this is not a full ban. The plan adds one extra step before late-night use.
>
> A trial with 309 families tested three different plans. Families found the nighttime plan easiest to manage.
>
> It stopped screen use from 9 p.m. to 7 a.m. Families reported better sleep most consistently with this plan.
>
> However, some teenagers moved their screen time. They used screens just before or after the blocked hours.
>
> So a nighttime break may not fix the wider problem.
>
> ### Point Two: Default Settings Can Guide Choices
>
> Ofcom ran a separate test with children. One setting stopped apps from suggesting harmful content.
>
> For some children, the test turned on this setting first. About seven in ten of these children kept it.
>
> For another group, the test chose no setting first. Around half of this group chose the same setting.
>
> The setting was optional for everyone. Still, the results suggest defaults can guide people's choices.
>
> The UK plan uses the same idea. Teenagers must turn off the nighttime setting first.
>
> This small step may stop some late-night scrolling.
>
> ## In One Line
>
> The UK wants a nighttime pause to help more teenagers put down their phones and sleep.

全文: [er003_output/a2_p1/A02/a2_article_raw.md](er003_output/a2_p1/A02/a2_article_raw.md)

### ADD03(ホルムズ海峡記事)

> # US Drops 20% Fee Plan for Strait of Hormuz
>
> U.S. President Donald Trump announced a new fee on July 13, 2026.
>
> The fee covered all cargo passing through the Strait of Hormuz. It was 20 percent of the cargo's value.
>
> Trump dropped the plan one day later. Gulf nations would seek trade and investment deals with the United States instead.
>
> The countries and money amounts remained unclear. Oil prices fell, but the market stayed worried.
>
> ## Today's Hormuz Risk Points
>
> ### Point One: A Huge Cost Disappeared Overnight
>
> The proposed fee could cost one large oil tanker $30 million. That equals about 4.9 billion yen.
>
> The shipping industry received no warning before the announcement. The plan caused shock and doubt across the industry.
>
> The plan also raised questions about international law.
>
> The International Maritime Organization repeated an important rule on July 13. Ships should not pay fees to pass through the strait.
>
> This rule supports free travel at sea.
>
> ### Point Two: Oil Prices Stayed High
>
> Brent crude oil rose about 10 percent before Trump dropped the plan. U.S.-Iran tensions and the proposed fee pushed prices higher.
>
> Brent later fell from a daily high above $87 per barrel.
>
> Still, Brent ended July 14 at $84.73. This was about 2 percent higher.
>
> It was also the highest price in one month.
>
> Other dangers remained in the area. A blockade still targeted ships linked to Iran. Military attacks also continued.
>
> The market cared about more than the fee. Ships also needed safe travel through the strait.
>
> ## In One Line
>
> The 20 percent fee disappeared, but serious risks remained in the Strait of Hormuz.

全文: [er003_output/a2_p1/ADD03/a2_article_raw.md](er003_output/a2_p1/ADD03/a2_article_raw.md)

## 6〜8. 総語数・平均文長・最長文

| 記事 | B1総語数 | A2総語数 | 削減率 | B1平均文長 | A2平均文長 | B1最長文 | A2最長文 |
|---|--:|--:|--:|--:|--:|--:|--:|
| A01 | 290 | 199 | 68.6% | 9.67語 | 7.37語 | 15語 | 15語 |
| A02 | 339 | 270 | 79.6% | 10.59語 | 8.18語 | 19語 | 16語 |
| ADD03 | 358 | 231 | 64.5% | 10.53語 | 8.56語 | 17語 | 13語 |

3記事とも、A2の暫定目標(平均11語以下・最長18語以下)を**達成した**
(18語超過文は0件)。ただし目安として挙げられていた「情報量70〜80%残す
イメージ」に対しては、A01(68.6%)・ADD03(64.5%)がやや下回った
(A02は79.6%で範囲内)。これは`hard rule`ではないため不合格扱いにはしていないが、
削りすぎの懸念として11節・15節で扱う。

## 9. 文法・構文QA(正規表現ヒューリスティック、目安のみ)

**注意: NLPパーサー(spaCy等)がこの環境にないため、正規表現による近似検出。
確定判定ではなく、目視確認の補助情報として扱うこと。**

| 記事 | 指標 | B1 | A2 |
|---|---|--:|--:|
| A01 | 関係詞節候補 | 1 | 0 |
| A01 | 受動態候補 | 0 | 0 |
| A01 | 現在完了候補 | 0 | 0 |
| A01 | 過去完了候補 | 1 | 0 |
| A01 | 分詞構文候補 | 0 | 0 |
| A02 | 関係詞節候補 | 4 | 0 |
| A02 | 受動態候補 | 2 | 0 |
| A02 | 現在完了候補 | 0 | 0 |
| A02 | 過去完了候補 | 0 | 0 |
| A02 | 分詞構文候補 | 1 | 0 |
| ADD03 | 関係詞節候補 | 4 | 1 |
| ADD03 | 受動態候補 | 2 | 0 |
| ADD03 | 現在完了候補 | 1 | 0 |
| ADD03 | 過去完了候補 | 3 | 0 |
| ADD03 | 分詞構文候補 | 0 | 0 |

3記事とも、関係詞・受動態・完了形・分詞構文の候補件数がB1よりA2で
明確に減少(ほぼ0件)している。ADD03のみ関係詞候補が1件残っている
(後述12節で該当箇所を確認)。

## 10. 語彙QA(長語ヒューリスティック、目安のみ)

**注意: CEFR頻度リストが存在しないため、語長9文字以上を「難語候補」とする
粗い近似。頻度検証ではない。**

| 記事 | B1難語候補数 | A2難語候補数 |
|---|--:|--:|
| A01 | 7 | 5 |
| A02 | 28 | 13 |
| ADD03 | 20 | 11 |

A2側の難語候補には`Argentina`/`government`/`President`/`Organization`等の
固有名詞・制度名が多く含まれており、これらは暫定仕様どおり意図的に保持した
ものである(固有名詞は原則保持、というルールに合致)。

## 11. B1との数値比較(まとめ)

| 指標 | A01(B1→A2) | A02(B1→A2) | ADD03(B1→A2) |
|---|---|---|---|
| 総語数 | 290→199 | 339→270 | 358→231 |
| 文数 | 30→27 | 32→33 | 34→27 |
| 平均文長 | 9.67→7.37 | 10.59→8.18 | 10.53→8.56 |
| 最長文 | 15→15 | 19→16 | 17→13 |
| 18語超過文 | 0→0 | 1→0 | 0→0 |
| 関係詞候補 | 1→0 | 4→0 | 4→1 |
| 受動態候補 | 0→0 | 2→0 | 2→0 |
| 完了形候補(現在+過去) | 1→0 | 0→0 | 4→0 |
| 難語候補 | 7→5 | 28→13 | 20→11 |

## 12. B1→A2代表文比較

**A01**

- B1: "England could finally dream of their first World Cup final since 1966."(1文、13語)
  → A2: "England started to dream of the final. It was England's first possible final since 1966."(2文に分割)
- B1: "England took off players including Rice and made its defense stronger. The team wanted to protect its narrow lead."
  → A2: "England tried to protect its lead. The team took off players including Rice. England also made its defense stronger."(語順を並べ替え、3文へ分割)
- B1 In One Line: "England tried to close the door to the final. Messi slipped two keys through the gap."(比喩表現)
  → A2 In One Line: "England tried to protect its lead, but Messi opened the way to Argentina's 2–1 win."(比喩を平易な直接表現へ置換)

**A02**

- B1: "During these hours, covered apps would be unavailable under the standard settings. Notifications would pause, and autoplay would be switched off."(受動態複数)
  → A2: "Apps under the plan will be unavailable by default overnight... Notifications will pause during these hours. Autoplay will also stop."(能動態中心、3文へ分割)
- B1: "The government hopes this small extra step will slow the urge to watch 'just one more' video."(承認済みKey Phrase "urge to watch"を含む)
  → A2: "This small step may stop some late-night scrolling."(**"urge to watch"というフレーズ自体が本文から消えている**、後述15節)
- B1 In One Line: "The UK wants to switch off not the smartphone's light, but the endless scrolling that keeps teenagers awake."(対比のレトリック)
  → A2 In One Line: "The UK wants a nighttime pause to help more teenagers put down their phones and sleep."(対比構造を解消し直接的な表現へ)

**ADD03**

- B1冒頭: "Imagine a giant tollbooth suddenly appearing in the Strait of Hormuz."(比喩の導入文)
  → A2冒頭: **この文自体が存在しない**。A2は"U.S. President Donald Trump announced a new fee..."から直接始まる
- B1: "A blockade against ships linked to Iran was still in place. Military attacks were also continuing."(受動態的表現"was still in place"、承認済みKey Phrase "be in place"を含む)
  → A2: "A blockade still targeted ships linked to Iran. Military attacks also continued."("be in place"という言い回し自体が消えている)
- B1 In One Line: "The tollbooth sign is gone, but the smell of gunpowder still hangs over the strait."(承認済みKey Phrase "tollbooth"/"smell of gunpowder"を含む比喩)
  → A2 In One Line: "The 20 percent fee disappeared, but serious risks remained in the Strait of Hormuz."(**両方のKey Phrase比喩が完全に消えている**)

## 13. 削除した主な情報

- **A01**: 「7分間で歓喜と落胆が入れ替わった」という劇的な対比のフレーズ(B1の"In only seven minutes, England's joy had turned into pain.")は、事実("in seven minutes"という時間情報)は冒頭に残したが、感情的な対比表現は削除
- **A02**: "urge to watch just one more"という具体的な行動描写フレーズを削除(要約的な"stop some late-night scrolling"へ置換)
- **ADD03**: 冒頭の"giant tollbooth"比喩全体、および結びの"smell of gunpowder"比喩全体を削除。数字・金額・日付は全て保持

## 14. 残した専門語・固有語

3記事とも、人名・地名・組織名(Messi、Enzo Fernández、Lautaro Martínez、UK、
Ofcom、Trump、International Maritime Organization等)と、記事理解に必須の
数字(スコア、$87、$84.73、4.9億円、20%、309家族等)は暫定仕様どおり保持した。
"World Cup"、"Brent crude oil"のような固有の専門語も保持している。

## 15. A2として懸念が残る箇所

- **ADD03の比喩表現("tollbooth"/"smell of gunpowder")が完全に消えている**。
  この2語はB1で正式に承認されたKey Phraseであり、記事の印象的な導入・結び
  を構成していた。A2本文にこのままKey Phrase選定をかけても、これらは
  候補にすら上がらない。ニュースとしての印象の強さが失われている可能性がある
  ([OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-15)。
- **A02の"urge to watch"というフレーズも同様に消えている**(B1の承認済み
  Key Phrase)。
- 情報量の削減率がA01(68.6%)・ADD03(64.5%)で「70〜80%」の目安をやや
  下回っており、単なる文長調整以上に内容そのものが削られている可能性がある。
- ADD03のみ関係詞候補ヒューリスティックが1件検出された(該当箇所は
  `er003_output/a2_p1/ADD03/a2_metrics.json`の`long_word_candidates`ではなく
  `grammar_vocab_heuristics`内に記録。目視確認を推奨)。

## 16. 構造支援なしでの難易度評価

数値上は暫定仕様の目標(平均11語以下・最長18語以下)を3記事とも達成して
おり、構造支援(ブロック分割・Listening Questions)を入れなくても文レベルの
難易度は明確に下がっている。ただし、比喩表現の喪失(15節)により「面白さ」
「印象の強さ」が犠牲になっている可能性がある点は、構造支援の有無とは
別の課題として残る。構造支援が必要かどうかの最終判断はユーザーの通読に委ねる
(11節「人間確認の観点」参照、本監査では判定しない)。

## 17. ER-003-A2-STRUCT-01の記録

以下をCANDIDATE(未実装)として[OPEN_ITEMS.md](OPEN_ITEMS.md)へ記録した。

- OPEN-13: Full Storyブロック分割+日本語signpost(Candidate A)
- OPEN-14: Full Story前の簡易Listening Questions(Candidate B)

いずれも`CANDIDATE / NOT_ADOPTED`。今回は実装していない。

## 18. 作成・変更ファイル

- 新規: [er003_v1_translator_briefs/a2_p1_prompt_template.txt](er003_v1_translator_briefs/a2_p1_prompt_template.txt)
- 新規: [er003_a2_article.py](er003_a2_article.py)(汎用モジュール、B1/B2の生成関数パターンを踏襲)
- 新規: [er003_v1_a2_p1_generate.py](er003_v1_a2_p1_generate.py)(A01/A02/ADD03一括生成ドライバ)
- 新規: [er003_v1_a2_b1_compare.py](er003_v1_a2_b1_compare.py)(B1/A2比較スクリプト)
- 新規: `er003_output/a2_p1/{A01,A02,ADD03}/*`(生成テキスト・prompt・metrics・生成条件の記録)
- 新規: `er003_output/a2_p1/b1_vs_a2_comparison.json`
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)(OPEN-01/OPEN-02更新、OPEN-13/14/15追加)
- 既存の`er003_b1_article.py`等、凍結モジュールは一切変更していない

## 19. テスト結果

プロジェクト全体回帰テスト: **1660件全合格**(新規追加した生成・比較モジュールに
専用テストは未作成。既存モジュールへの変更がないため回帰は発生していない)。

## 20. Git status

新規7ファイル(prompt template・モジュール2本・比較スクリプト1本・本レポート・
成果物ディレクトリ)、既存1ファイル更新(OPEN_ITEMS.md)。

## 21. commit

コミット済み(詳細はcommitログ参照)。

## 22. push未実行確認

**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[OPEN_ITEMS.md](OPEN_ITEMS.md)、[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)
