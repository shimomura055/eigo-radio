# ER-008-A2-STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01 完了報告

## 概要

「A2レベルの英語本文 + B1で使っているEnglish Intro/Comment」という中間
仕様が、既存資産(No.4〜6)の**流用だけ**で成立するかをAuditした。
Production仕様変更・新規記事生成・新規TTS・新規Writer生成は一切行って
いない。実際のscript(`parts.json`/`*_support_texts.json`)・Key Phrase
定義・TTS生成監査ログ(`tts_generation_results.json`)・音声組み立て
スクリプト(`er003_v1_n3_01_assemble.py`)を直接読み、内容を突き合わせた。

**結論を先に述べる**: No.4は完全流用可能。No.5・No.6は、Comment 4が
それぞれ1箇所ずつ、A2側のPoint Twoに存在しない内容を前提にしている
軽微な不整合を持つ(詳細は3〜5節)。全体判定は
**`FEASIBLE_WITH_LIGHT_ADJUSTMENT`**。

## 1. 現在のA2/B1 episode構造

`er003_v1_n3_01_assemble.py`の`build_a2_timeline()`/`build_b1_timeline()`
から、実際の組み立て順序をそのまま復元した。

### A2 (`build_a2_timeline`)

Intro → Welcome → Topic intro(Aoede、英語) → **Japanese title**(Aoede、
日本語) → Notification → Preview intro(共通定型文"Here's a quick
preview.") → **Point explanation**(共通定型文"Here's the point."、
A2のみに存在) → **Preview**(Aoede、日本語) → Notification → Key
phrases intro → **Key Phrase 1〜5**(英語Component+日本語gloss) →
Notification → Full story intro(共通定型文) → **Comment 1**(Aoede、
日本語) → **Full Story Part 1**(Aoede、英語) → **Comment 2**(Aoede、
日本語) → **Full Story Part 2**(Aoede、英語) → **Comment 3**(Aoede、
日本語) → Point Notification → **Point One heading+body**(Aoede、
英語) → Point Notification → **Point Two heading+body**(Aoede、英語) →
**Comment 4**(Aoede、日本語) → **In One Line**(Aoede、英語) → Outro

### B1 (`build_b1_timeline`)

Intro → Welcome(Charon) → **Topic intro**(Charon、英語) → Notification
→ Preview intro(Charon、共通定型文) → **Preview**(Charon、英語) →
Notification → Key phrases intro(Charon) → **Key Phrase 1〜5**(英語
Component+日本語gloss) → Notification → Full story intro(Charon) →
**Comment 1**(Charon、英語) → **Full Story Part 1**(Aoede、英語) →
**Comment 2**(Charon、英語) → **Full Story Part 2**(Aoede、英語) →
**Comment 3**(Charon、英語) → Point Notification → **Point One
heading+body**(Aoede、英語) → Point Notification → **Point Two
heading+body**(Aoede、英語) → **Comment 4**(Charon、英語) → **In One
Line**(Aoede、英語) → Outro

### segmentの分類(A2固有・B1固有・共通)

| segment | A2 | B1 | 備考 |
|---|---|---|---|
| Title(音声上のsegment名としてはTopic intro) | Aoede、英語title、A2固有本文由来 | Charon、英語title、B1固有本文由来 | **タイトル文言自体がA2/B1で異なる**(例: No.4 A2「The Supermarket Shuffle」/B1「The Supermarket Shelf Shuffle」) |
| Japanese title | あり(Aoede、日本語) | なし | A2のみの構造 |
| Preview/Intro | Aoede、**日本語** | Charon、**英語** | 言語もvoiceも異なる。中間仕様ではB1(英語)を使う想定 |
| Point explanation(定型文) | あり | なし | A2のみの構造(共通定型文なので内容依存なし) |
| Comment 1〜4 | Aoede、**日本語** | Charon、**英語** | 言語もvoiceも異なる。中間仕様ではB1(英語)を使う想定 |
| Full Story Part 1/2 | Aoede、英語、**A2固有本文** | Aoede、英語、**B1固有本文** | 本文テキスト自体がA2/B1で別物(CEFR適応で書き換え済み) |
| Point One/Two heading+body | Aoede、英語、**A2固有本文** | Aoede、英語、**B1固有本文** | 同上。さらに3節で述べる通り、**Point One/TwoへのFactの振り分け自体がA2/B1で異なる場合がある** |
| In One Line | Aoede、英語、**A2固有本文** | Aoede、英語、**B1固有本文** | 同上 |
| Key Phrase | A2独自セット(A2本文から抽出) | B1独自セット(B1本文から抽出) | 6節参照。**セットがほぼ別物**(語彙がA2/B1で異なるため) |
| Notification/Point Notification/Outro/Intro/Welcome/定型文(Preview intro等) | 共通 | 共通 | 内容依存なし、常に流用可能 |

## 2. 中間仕様の仮構成

ユーザー仕様の通り、以下を仮組みして評価した(実音声は生成していない、
scriptベースの机上組み立て)。

- Title/Topic intro: **A2**(理由: 直後にA2本文が続くため、内部一貫性
  重視。7節参照)
- Japanese title: **A2**(既存のまま保持を推奨、非対象外の判断ではない
  ため推奨に留める)
- Preview/Intro: **B1英語**
- Point explanation(定型文): 保持するかは意匠上の任意選択(11節)
- Key Phrase: **A2**(6節で確認、B1を使うと本文と噛み合わない語が多い)
- Full Story Part 1/2: **A2**
- Comment 1〜4: **B1英語**
- Point One/Two: **A2**
- In One Line: **A2**

## 3. No.4〜6 Intro compatibility

| Topic | 判定 | 根拠 |
|---|---|---|
| No.4 | `DIRECTLY_REUSABLE` | "In this episode, we look at the link between supermarket design and shopping choices..." — トピックレベルの一般的な導入のみで、B1本文固有の事実・人名・数字への言及なし |
| No.5 | `DIRECTLY_REUSABLE` | "In this episode, we look at how cafés are responding to people who work on laptops..." — 同上 |
| No.6 | `DIRECTLY_REUSABLE` | "When we are waiting and do not know what will happen next, we may check for updates again and again..." — 同上 |

3件ともPreviewはB1・A2どちらの本文とも矛盾しない、トピック要約レベルの
一般的な文言だった。指示語・固有名詞・具体的数値への依存なし。

## 4. No.4〜6 Comment 1〜4 compatibility

`DIRECTLY_REUSABLE` / `MINOR_MISMATCH` / `NOT_REUSABLE`で分類する。

### No.4(スーパーの棚配置)

| Comment | 判定 | 根拠 |
|---|---|---|
| Comment 1 | `DIRECTLY_REUSABLE` | "Listen for how the stores changed their layout." — 汎用的な聞き取り指示のみ |
| Comment 2 | `DIRECTLY_REUSABLE` | "the stores changed the layout to make healthy foods easier to see and sweets less prominent" — A2 Part1(果物・野菜エリア拡大、入口近くへ移動、菓子撤去)と一致 |
| Comment 3 | `DIRECTLY_REUSABLE` | "changing a store's layout can change what people buy, even when total sales stay about the same" — A2 Part2「total store sales did not change in a statistically significant way」と一致 |
| Comment 4 | `DIRECTLY_REUSABLE` | "some shelf changes can be planned with data, not only by eye" — A2 Point Two本文「A 2022 paper proposed using buying data...」と一致(A2のPoint TwoにもB1と同じ2022年データ駆動研究の記述がある) |

### No.5(カフェの座席問題)

| Comment | 判定 | 根拠 |
|---|---|---|
| Comment 1 | `DIRECTLY_REUSABLE` | "Listen for the four types of café described in the study." — A2もPart1(3類型)+Part2冒頭(4類型目PTP)で計4類型を提示しており一致 |
| Comment 2 | `DIRECTLY_REUSABLE` | "what choice did one café make when laptop users stayed for a long time?" — A2 Part2のThe Barnの1時間制限の記述と一致 |
| Comment 3 | `DIRECTLY_REUSABLE` | "Some try to serve both workers and social customers, while others set limits." — A2のCompromise places(両者に配慮)とThe Barnの時間制限の両方と一致 |
| Comment 4 | **`MINOR_MISMATCH`** | 前半「a café's design can guide how people use the space」はA2 Point One(「Space is also a business message」)と一致するが、後半**「customers who work there may offer the café more than their payment」はA2 Point Twoに存在しない**。A2 Point Twoの見出しは「The hard part is choosing clearly」で、本文は「customer-workersが常に良い/悪いとは言えない、方針を明確にすることが重要」という趣旨。B1 Point Twoの「顧客労働者は支払い以上の価値(閑散時間の座席利用・活気の演出)をもたらしうる」という主張はA2側に一切登場しない |

### No.6(配達追跡の確認衝動)

| Comment | 判定 | 根拠 |
|---|---|---|
| Comment 1 | `DIRECTLY_REUSABLE` | "Listen for who the researchers studied, what they were waiting for, and what changed as their worry grew." — 汎用的な聞き取り指示、A2 Part1と矛盾なし |
| Comment 2 | `DIRECTLY_REUSABLE` | "greater worry led people to look for updates more often...why people may keep checking" — A2 Part1・Part2の記述と一致 |
| Comment 3 | `DIRECTLY_REUSABLE` | "checking may offer a brief sense of control, even when the final result is out of their hands" — A2 Part2「Checking may create a weak and temporary feeling of control. It does not change the final result.」と一致 |
| Comment 4 | **`MINOR_MISMATCH`** | 「two sides of checking again: (1) 不確実な待機中の小さな行動、(2) 実験室で人はより難しい/不確実な時により多く確認した」という要約だが、**(2)の実験詳細(28名、動く点、判断の難易度)はA2ではPoint One本文に含まれており、Point Twoではない**(A2 Point Twoは「意識的/無意識的な不確実性の自覚が確認行動を予測するか」という別の論点)。B1側はPoint One=概念的枠組み、Point Two=実験詳細という配置のため、B1のComment 4がそのまま前提とする「直前にPoint Twoで聞いた実験の話」という文脈が、A2の構成では成立しない(実験の話はPoint Oneで既に終わっている) |

## 5. B1本文固有表現への依存箇所(4-1)

Comment/Preview本文全件を"phrase"/"heard"/"word"等のキーワードで機械的
に走査したが、「You just heard the phrase...」のような直接的なフレーズ
参照は**3 Topic中0件**だった。B1のCommentは全て意味内容の要約・橋渡し
であり、特定の語句そのものを指し示す構造にはなっていない。

## 6. B1本文固有Factへの依存箇所(4-2)

具体的な数字・研究者名・固有名詞への依存を個別に確認した。

- No.4: B1本文にのみ登場する研究者名「Vogel and colleagues」は、B1
  Comment/Previewのどこにも言及されていない(Comment側は一般的な要約
  のみ)
- No.5: B1本文にのみ登場する創業者名「Ralf Rüller」の引用は、B1
  Comment/Previewのどこにも言及されていない
- No.6: 研究者名「Howell and Sweeny」はB1・A2**両方**の本文に登場する
  ため、どちらを使っても問題なし

**Fact依存の直接的な問題は4節のComment 4(No.5・No.6)以外には見つから
なかった**。上記2件の研究者名依存は、たまたまCommentが人名レベルの
詳細まで踏み込んでいなかったため実害がなかった(設計上の安全マージン
というより、結果的に依存しなかっただけと解釈すべき)。

## 7. 指示語/参照先不整合(4-4)

Comment本文の指示語(this/that/these/the study等)を個別に確認した。
いずれも「the study」「that」等はA2・B1共通の同一研究(2021年の
研究等)を指しており、参照先の研究自体はA2/B1どちらの本文でも同一
であるため、指示語の参照先不明化は確認されなかった。No.5・No.6の
Comment 4で見つかった問題(4節)は、指示語の参照先不明化ではなく、
**「要約が指す内容自体がA2側に存在しない、またはA2側では別の場所
[別のPoint]で既出になっている」**という、指示語より一段上の論理構造
レベルの不整合である(4-3として分類)。

## 8. A2本文との論理不整合(4-3、5節の逆方向確認を含む)

Point One/Two heading+bodyのFact配分をA2/B1で突き合わせた。

| Topic | Point One | Point Two | 判定 |
|---|---|---|---|
| No.4 | A2「The store is part of the decision」/B1「The shelf can shape the shopping mood」— 同じGreece研究(205名)を土台に同じ趣旨 | A2「Moving shelves can serve two goals」/B1「Rearrangement can be driven by data」— 同じ2022年データ駆動研究が両方に含まれる(A2は追加で業界記事の理由も言及) | 整合 |
| No.5 | A2「Space is also a business message」/B1「Design can welcome—or quietly resist—work」— 同じ趣旨(空間デザインが店の意図を伝える) | **A2「The hard part is choosing clearly」(方針の明確さ)** vs **B1「The real product is the atmosphere」(支払い以上の価値)** — **異なる論点** | **不整合** |
| No.6 | **A2「Uncertainty makes checking more tempting」(実験詳細を含む)** vs **B1「A small action in a powerless wait」(概念枠組みのみ)** | **A2「Noticing doubt may keep the loop going」(意識/無意識の自覚)** vs **B1「The lab version of "check again"」(実験詳細)** — **実験詳細がPoint One/Twoで入れ替わっている** | **不整合(内容の入れ替わり)** |

**5節(A2本文側からの逆方向確認)の結論**: No.5のComment 4後半は、A2側
が聞いていない新しいFact(顧客労働者の「支払い以上の価値」)を、あたかも
「これまで聞いてきた内容」であるかのように語ってしまう。No.6の
Comment 4は、新しいFactの追加ではないが、「直前のPoint Twoで聞いた
はずの実験の話」として言及する内容が、実際にはA2のPoint Oneで既に
語られた内容であるため、時系列上の参照がずれる。いずれも「本文を
聞いていないと理解できない」ほど深刻ではないが、「本文を注意深く
聞いていた学習者ほど、わずかな違和感を覚えうる」種類の不整合である。

## 9. B1 support自体の難易度上の懸念(4-5)

新規CEFR評価は行わず、既存B1 script(Preview/Comment)の語彙・文長を
目視確認した。Full Story本文(B1)と比べ、Preview/CommentはA2の
日本語Comment同様、**短く平易な文が中心**(例: "Listen for how the
stores changed their layout.")であり、B1本文側に見られる高度な語彙
(例: "longitudinal study"、"association-rule mining"、"confectionery")
はComment/Preview本文には**登場しなかった**。ただし、"prominent"
(No.4 comment_2)、"interpreted"(該当なし、Point Two bodyのみ)等、
A2の日本語Commentと比べれば当然ながら英語のリスニング負荷は上がる
(これは中間仕様の前提そのものであり、問題ではなく設計上の特性として
記録する)。3 Topicとも、Comment単体で明らかに不適切な難易度(専門用語
の羅列・極端に長い複文)は確認されなかった。

## 10. Key Phrase推奨

`keywords_canonicalized.json`をA2/B1で突き合わせた。

| Topic | A2 Key Phrases | B1 Key Phrases | 重複 |
|---|---|---|---|
| No.4 | standard deviation, impulse buying, statistically significant, layout, move in the other direction | statistically significant, impulse buying, confectionery, intervention effect, association-rule mining | 2/5(statistically significant, impulse buying) |
| No.5 | customer-workers, third places, seat turnover, Status Quo places, clashes | customer-workers, third places, status quo, interpreted benefits, enforce their rules | 2/5(customer-workers, third places、"Status Quo places"/"status quo"は表記ゆれで実質同一なら3/5) |
| No.6 | out of our hands, information-seeking, move together, keep alive, outside conscious awareness | pull us back, feel available, regain a little control, fragile, causation | 0/5 |

**推奨: A2 Key Phrase一択**。理由:

1. B1 Key PhraseはB1本文固有の語彙・言い回し(例: No.6の「pull us
   back」はB1 Part1「the update button pulls us back」由来、A2本文には
   この言い回し自体が存在しない)から抽出されており、Full StoryにA2
   本文を使う中間仕様では、**聞いたはずのない言葉をKey Phraseとして
   提示することになる**(致命的な不整合)
2. A2 Key PhraseはA2本文からそのまま抽出されているため、Full Story
   (A2)との対応が保証されている
3. B1 CommentがB1 Key Phraseを名指しで前提にしている箇所は5節の通り
   0件のため、Key PhraseをA2へ差し替えてもComment側への副作用はない

## 11. 再利用可能audio segment数

1件のepisode(Notification/Outro/Intro/Welcome等の共通定型boilerplate
segmentを除く、コンテンツsegment)を19個と数える: Topic intro(1)、
Japanese title(1)、Preview(1)、Key Phrase(5)、Comment 1〜4(4)、
Full Story Part1/2(2)、Point One heading+body(2)、Point Two
heading+body(2)、In One Line(1)。

| Topic | そのまま流用可能 | script上は流用可能だがaudio mapping変更が必要 | 新規TTSが必要 |
|---|---|---|---|
| No.4 | 19/19 | 19/19(下記注) | 0 |
| No.5 | 18/19 | 19/19(下記注) | 1(Comment 4、修正する場合のみ) |
| No.6 | 18/19 | 19/19(下記注) | 1(Comment 4、修正する場合のみ) |

**注(全topic共通)**: 音声ファイル自体(WAV)は既存のまま一切変更不要
だが、`er003_v1_n3_01_assemble.py`の`build_a2_timeline()`は現状
「Comment 1〜4はA2自身の日本語segmentを使う」前提で書かれており、
B1側のnarrationディレクトリからComment/Previewを読む経路が存在しない。
また、A2のComment前後のpauseはEN→JA/JA→EN用の値
(`pause_1.0_en_to_ja`/`pause_0.8_ja_to_en`)を使っているが、B1英語
CommentをA2本文へ挿入する場合はB1側のEN→EN用pause値
(`AOEDE_TO_CHARON_PAUSE_SECONDS`/`CHARON_TO_AOEDE_PAUSE_SECONDS`)へ
差し替える必要がある。これは**新規TTS/ASRを伴わない、assembly
scriptの設定・分岐追加のみ**で対応可能な一度きりのエンジニアリング
作業である(本Auditの非対象事項「Production仕様変更」には該当しない、
実装作業そのものは行っていない)。

## 12. 新規TTS必要segment数

- No.4: **0 segment**(Comment 1〜4全てDIRECTLY_REUSABLE)
- No.5: **1 segment**(Comment 4。修正しMINOR_MISMATCHを解消する場合。
  修正せず現状のまま使う選択肢も残る、後述14節)
- No.6: **1 segment**(Comment 4。同上)

## 13. Writer再生成必要性

**不要と判断する**。既存scriptの文言自体は一切変更せず(No.4の場合)、
または1 Comment(1〜2文)の軽微な削除・言い換えのみ(No.5・No.6の場合)
で足りるため、記事全体のWriter再生成は必要ない。

## 14. Fact Check再実行必要性

**フルパイプラインの再実行は不要**。理由: 中間仕様は既存の(Fact
Check済み)segmentを新しい順序で組み合わせるだけであり、新しいFactを
本文へ導入しない(No.4)。No.5・No.6のComment 4修正についても、
「A2側に存在しない主張を除去する」方向の編集(Factを削るだけで、
新しいFactを追加しない)であれば、既存Ledger/Fact Checkの対象範囲は
一切広がらない。ただし、本Audit自体が「cross-level文脈整合性Check」
の役割を実質的に果たしており、この種の軽微な編集を行う場合は、
編集後のComment 4がA2本文と整合するかを人手で再確認する(小規模な
スポットチェックで足り、Fact Check/Ledger Deviationの自動パイプライン
再実行は不要)ことを推奨する。

## 15. 1 topicあたり追加cost概算

**Case A(既存segment完全流用、No.4相当)**

| 項目 | Cost |
|---|---|
| Writer cost | $0 |
| TTS cost | $0 |
| ASR cost | $0 |
| storage/assembly追加cost | 実質$0(既存WAVファイルの参照+組み立てスクリプトの一度きりの拡張のみ、API呼び出しなし) |

**Case B(Comment 4に軽微修正が必要、No.5・No.6相当)**

| 項目 | Cost概算 |
|---|---|
| Writer/LLM cost(1〜2文の言い換え、Claude/GPT 1回) | 数円未満(既存タスクの他の軽微修正実績から類推、$0.01未満) |
| TTS cost(英語Comment 1segment、150〜200文字) | 約$0.0001(Gemini TTS、既存の文字単価から算出) |
| ASR cost(検証、OpenAI mini、15〜20秒) | 約$0.001未満 |
| 合計/topic | **$0.01未満(¥数円未満)** |

いずれのCaseでも「ほぼ無料で1仕様増やせる」という仮説は**実際に正しい
と確認できた**。1 topicあたりの追加費用は、最大でも1桁円のオーダーに
収まる。

## 16. No.4判定

**`READY_AS_IS`**。Intro/Comment 1〜4全てDIRECTLY_REUSABLE、Point One/
Twoの論理構造もA2/B1で整合している。

## 17. No.5判定

**`READY_WITH_MINOR_ADJUSTMENT`**。Intro/Comment 1〜3はDIRECTLY_
REUSABLE。Comment 4のみ、「customers who work there may offer the
café more than their payment」という一節がA2 Point Twoに存在しない
主張であるため、当該一節の削除または言い換えを推奨する。

## 18. No.6判定

**`READY_WITH_MINOR_ADJUSTMENT`**。Intro/Comment 1〜3はDIRECTLY_
REUSABLE。Comment 4は、Point One/Two間で入れ替わった実験詳細の参照
順序により、直前に聞いた内容との対応がややずれる。深刻な誤りではない
が、"we have seen two sides..."という時系列を強く示唆する構造を、
より中立的な言い回し(例: 実験の言及順序に依存しない要約)へ言い換える
ことを推奨する。

## 19. 全体feasibility判定

**`FEASIBLE_WITH_LIGHT_ADJUSTMENT`**。

- 3 Topic中1件(No.4)は完全にそのまま流用可能
- 残り2件(No.5・No.6)も、各1 Comment(Comment 4)の軽微な言い換えのみ
  で解消できる不整合が1件ずつあるのみで、それ以外(Intro・Comment
  1〜3・Point構造の大半・Key Phrase)は問題なし
- 追加コストは1 topicあたり最大でも数円のオーダー
- ただし、No.5・No.6で見つかったPoint One/Two間のFact配分の違い
  (8節)は、**A2/B1のWriterが独立に「2つの論点」を選んでいるため
  発生する構造的な現象**であり、今後の新規Topicでも同様のケースが
  一定確率で発生しうる(21節)

## 20. 次にA/B試聴へ進む価値があるか

**あると判断する**。理由: (1) 3 Topic中の大半のsegmentが無修正で
使用可能であることが確認できた、(2) 唯一の技術的な作業(assembly
scriptのB1 narration参照対応・pause値の分岐)は新規TTS/ASRを伴わない
軽量な実装で足りる、(3) 発見された不整合は「聞くと明確な間違いとして
気づかれる」レベルではなく「注意深く聞くとわずかに引っかかる」レベル
であり、実際にユーザーが試聴して違和感の有無を判断する価値がある。
ただし、A/B試聴の前提として、No.5・No.6のComment 4を(a)現状のまま
試聴する、(b)14節の軽微修正を先に適用してから試聴する、のどちらに
するかはユーザー判断が必要(22節)。

## 21. 新規API Cost

本Audit自体では新規API呼び出しを一切行っていない(既存JSON/audit
ログの読み込みのみ)。

## 22. 残存Open Item

1. **No.5・No.6のComment 4修正要否**: 17・18節の軽微修正を実施する
   か、現状のまま(既知の軽微な不整合を許容して)試聴へ進むかはユーザー
   判断が必要
2. **Point One/Two間のFact配分の不一致(8節)**: No.5・No.6で発見された
   ように、A2とB1のWriterが独立に「2つの論点」を選ぶため、Point
   構造がレベル間で完全には一致しないことがある。今後この中間仕様を
   正式採用する場合、新規TopicでもComment 4(および同様にPoint構造を
   参照する他segment)の per-topic audit が必要になる可能性が高く、
   完全自動流用ではなく軽量な人手チェック工程が恒常的に必要になると
   想定される
3. **Title/Topic introの選択**: 2節で「A2を推奨」としたが、これは
   ユーザー未確定の意匠判断であり、正式に決定はしていない
4. **Point explanation定型文("Here's the point.")の扱い**: A2のみに
   存在しB1にはない構造上の差異。中間仕様で残すか省くかは意匠判断
   (11節)
5. **音声組み立てへの実装作業**: 11節で述べた通り、assembly script
   自体への変更(B1 narration参照・pause値分岐)は、本Auditの非対象
   事項(Production仕様変更)のため未実施。次段階(Production採用判断
   後)で必要になる
6. **No.1〜3は今回未評価**: タスク仕様の通り対象外としたが、量産
   最新仕様ではないため、正式採用時には別途確認が必要になる可能性が
   ある

## 非対象・完了

Production Level追加、Level名称決定、UI変更、No.7生成、新規Writer
生成、新規TTS、新規ASR、A2/B1既存script変更、Pricing変更、いずれも
実施していない。Audit完了後STOPする。
