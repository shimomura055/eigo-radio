# ER-003-A2-STRUCT-02 A02構造支援プロトタイプ(日本語コメント4種+Full Story 2分割)

**管理ID: ER-003-A2-STRUCT-02**
**実施日: 2026-08-09(確定版へ更新)**
**ステータス: `PROTOTYPE_BUILT / UNDER_EVALUATION`(テキストのみ、音声未生成、ユーザー評価待ち)**

> 本文書は同一管理IDの初版(Full Storyを3ブロック+signpost2文とした簡易版)を、
> ユーザー指定の正確な11パート構成・日本語コメント文言へ置き換えたものである。
> 初版の3ブロック案は本版に統合され、以後は本版を正式なプロトタイプとして扱う。

## 1. 目的

A2-03までで英語そのものの簡略化は十分に進んだが、ユーザー評価では
「読めば理解できるが、A2学習者が音声だけで追うにはまだ難しい」という
課題が残った。ここからは英語をさらに不自然に単純化するのではなく、
**途中で日本語による理解回収・次の聞きどころ提示を入れる構造支援**を
検証する。今回はA02のみを対象に、テキスト構造案を作成する。音声生成は
行わない。

## 2. 今回の構造(A02のみ)

既存の番組構造(日本語Preview→Key Phrases→Full Story→Point One→
Point Two→In One Line)を、A2のみ以下の11パートへ変更する。

1. 日本語Preview(既存承認版のまま)
2. Key Phrases(詳細仕様は今回変更しない)
3. 日本語コメント1
4. Full Story Part 1
5. 日本語コメント2
6. Full Story Part 2
7. 日本語コメント3
8. Point One
9. Point Two
10. 日本語コメント4
11. In One Line

番組全体の構造(Preview/Key Phrases/Full Story/Point One/Point Two/
In One Lineという骨格そのもの)は変更していない。Full Story内部を
分割し、日本語コメントを追加している。

## 3. 日本語コメントの基本思想

日本語コメントは**全文翻訳ではない**。役割は次の4つ。

- 次に何を聞くか示す
- 途中で理解を回収する
- 次の英語へ橋をかける
- Full Story/Pointsの意味を整理する

日本語でニュース全文を説明してしまわない。「コメント1」等のセクション名を
音声で読み上げることは想定していない。自然な日本語ナレーションとして
接続する。

## 4. A02プロトタイプ全文

### ① 日本語Preview(既存承認版、変更なし)

> 英国政府が、16歳と17歳を対象に、深夜0時から午前6時までSNSを止める計画を発表しました。通知やおすすめ表示は自動で止まりますが、設定を変えれば元に戻せます。果たしてこの仕掛けは、深夜のスクロールを止められるのでしょうか。

### ② Key Phrases

今回は構造検証が主目的のため、Key Phrase部分の詳細仕様(選定・件数・
語数等)は変更しない。A2本文確定後にA2本文から正式に選定する
([A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)参照)。

### ③ 日本語コメント1(Listening Focus)

> まずは、夜になるとSNSがどう変わるのかに注目して聞いてみましょう。

### ④ Full Story Part 1

> Social media in the UK may soon say "goodnight" at midnight.
>
> The British government shared a new plan on July 15. It is for people aged 16 and 17. The government calls it a digital switch-off period. It would run from midnight to 6 a.m.
>
> During that time, apps under the plan would not open at first. This first setting is called a default. Notifications would stop. Autoplay would stop too. This tool starts the next video on its own.
>
> The apps would also stop feeds that pick posts for each person. These feeds can keep people scrolling for a long time.
>
> The government plans to start it in spring 2027.

(107語。英文はER-003-A2-03のFull Storyから一切変更していない)

### ⑤ 日本語コメント2(Mid-story Recovery + Next Question)

> ここまでで、深夜にはSNSのいくつかの機能が自動で止まる計画だと分かりました。では、利用者はこの設定を自分で変えられるのでしょうか。

### ⑥ Full Story Part 2

> But it would not be a full ban. Teenagers could change the setting. Then they could use the apps late at night.
>
> The government wants this first setting to slow teenagers down. They would need to stop and make a clear choice. This small step may break the "just one more" habit. It may help more teenagers put down their phones and sleep.

(63語。英文はER-003-A2-03のFull Storyから一切変更していない)

### ⑦ 日本語コメント3(Story Meaning + Bridge to Points)

> 設定は自分で変えられるので、これは完全な禁止ではありません。それでも、最初から使えない状態にしておくだけで行動は変わるのでしょうか。ここからは、2つの実験を見ていきます。

### ⑧ Point One(A2-03のまま、変更なし)

> ### Point One: Families Found the Night Rule Easiest
>
> In one test, 309 families joined. It tested three ways to cut screen time.
>
> Families said the night rule was easiest to use. The rule lasted from 9 p.m. to 7 a.m. Again and again, families said this rule helped them sleep better.
>
> Still, some teenagers moved their screen time instead. They used screens just before the rule began or after it ended. So the rule did not make the screen-time problem go away.

### ⑨ Point Two(A2-03のまま、変更なし)

> ### Point Two: First Settings Can Change What Children Do
>
> Ofcom ran another test with children. For one group, a safer setting was on by default. It stopped suggestions for posts that could hurt them.
>
> Around seven in ten children kept that setting. For another group, no setting was chosen first. Around half then chose the safer setting.
>
> Children did not have to keep it. Still, the first setting changed what many children did. This helps explain why the UK chose a plan without a full ban.

### ⑩ 日本語コメント4(Point Recovery + Bridge to In One Line)

> 夜のルールだけですべて解決するわけではありません。でも、最初の設定を変えるだけで、人の行動が変わる可能性はありそうです。最後に、今日のニュースを英語一文でまとめます。

### ⑪ In One Line(A2-03のまま、変更なし)

> The UK hopes more teenagers will keep the night setting and simply go to sleep.

## 5. Full Story分割位置の根拠

Full Story(7段落、170語)を2分割した。境界は
**"The government plans to start it in spring 2027." の直後、
"But it would not be a full ban." の直前**とした。

理由: Part 1は一貫して「政府は何をするのか」を説明しており、Part 2の
冒頭"But it would not be a full ban."から論点が「完全禁止ではない」へ
転換する。ここが最も自然な意味境界であるため。均等な語数(Part1=107語、
Part2=63語)を狙った機械的分割ではなく、意味上のまとまりを優先した。

## 6. 日本語コメント4種類の役割定義(一般化用フレームワーク)

今後、他記事へ一般化する際に再利用する「役割」の定義。

| コメント | 役割名 | 機能 |
|---|---|---|
| Comment 1 | Listening Focus | 次の英語で何を聞くかを示す。答えは言わない |
| Comment 2 | Mid-story Recovery + Next Question | Full Story Part 1で最も重要な内容を1点だけ日本語で回収し、Part 2で確認する問いを提示する |
| Comment 3 | Story Meaning + Bridge to Points | Full Story全体の意味・論点を短く整理し、Point One/Twoを聞く理由を作る |
| Comment 4 | Point Recovery + Bridge to In One Line | Point One/Twoから得られた意味を短く回収し、最後の英語一文へつなぐ |

**重要ルール: 今回のA02の日本語文言を、他記事へそのままテンプレート
置換してはならない。** 一般化するのは上記の「役割」であり、文章その
ものではない。記事ごとに、Full Storyの意味上の転換点、Part 1/Part 2の
中心テーマ、Full Storyから導かれる論点、Point One/Twoとの関係を理解した
上で、日本語コメントを新たに書く必要がある。

## 7. Full Story分割ルール(優先順位、一般化用)

機械的に50:50で分割しない。優先順位は以下の通り。

1. 意味上の転換点
2. 時系列上の転換点
3. 問題→例外
4. 発表→反応
5. What happened → What happened next / Why it matters

A02では、優先順位1(意味上の転換点: 「政府は何をする」→「完全禁止では
ない」)に該当する位置を境界とした。

## 8. 日本語コメントの長さの目安(hard文字数は設定しない)

Podcastのテンポを壊さないための目安。

| コメント | 目安 |
|---|---|
| Comment 1 | 原則1文 |
| Comment 2 | 1〜2文 |
| Comment 3 | 2〜3文 |
| Comment 4 | 2〜3文 |

長い日本語解説にはしない。

## 9. ER-003-A2-03仕様の整理(再確認)

| 項目 | 判定 |
|---|---|
| Spoken-first | **ADOPTED**(継続候補) |
| A2超一般語最大5語 | **REJECTED**(未達だったことのみが理由ではない。CEFR語彙判定基盤の不在・運用複雑化・効果不十分の3点が理由) |
| 抽象語→具体的行動への一律変換 | **REJECTED_AS_GENERAL_RULE**(簡単になる場合もあるが、具体化でかえって分かりにくくなる場合もあるため) |
| 固有名詞密度低減 | **REJECTED**(効果が安定せず、ルール追加による複雑化に見合わないため) |
| 1文1数字 | **維持**(A2 Prototype仕様として継続。日付"July 13, 2026"は年齢範囲・スコア・時間帯と同様に1つの数字情報として扱う方向で整理。今回は`_EXEMPT_NUMBER_PATTERNS`への実装は行わない) |

詳細な理由は[DECISION_LOG.md](DECISION_LOG.md)、一覧は
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)を参照。

## 10. 期待している効果(仮説、検証はしていない)

音声化した場合、分割なしでは英語が170語連続で流れる構成になる。今回の
プロトタイプでは、英語が最大107語(Part 1)まで連続するのみで、途中に
日本語コメントが3回挟まる構成になる。**この効果は今回は検証していない
(音声化していないため)。**

## 11. 今回の確認対象(完了したこと)

- A02の全構造をテキストで組み立てた
- Comment 1〜4を指定内容でその通りに配置した
- Full Story Part 1/Part 2の境界を指定位置で分割した
- Point One/Two/In One LineはA2-03のまま変更していない
- Previewは既存承認版のまま変更していない

## 12. 非対象範囲(今回行っていないこと)

- A01への適用
- ADD03への適用
- 音声生成(TTS)
- TTS速度変更
- Key Phrase最終選定
- B2音声生成
- 構造の本番実装
- push

## 13. Source of Truth更新

ステータスは`PROTOTYPE / UNDER_REVIEW`のまま。[OPEN_ITEMS.md](OPEN_ITEMS.md)
のOPEN-13を本版の11パート構成に合わせて更新した。ユーザーがA02テキスト
構造を確認した後、必要なら音声プロトタイプへ進む。他記事への一般化は
その後の判断とする。

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[DECISION_LOG.md](DECISION_LOG.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)
