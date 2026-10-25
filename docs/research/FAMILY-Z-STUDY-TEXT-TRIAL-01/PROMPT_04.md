# PROMPT_04(Trial-04 Phase 0。dry-runで生成した各工程のPrompt全文。DEV専用・Production未承認)

生成: `py run_trial_04.py dry-run` -> `_prompt_04_<work>_{p1a,p1b,stepA,stepB,p34}.txt`(3作品分)。sha/長さは`dryrun_04.json`。Part 3/4ブロックは03dと完全一致(`p34_prompt`がassert)。

## 1. Part 1 別LLM Prompt 案α(推奨・主。入力=KP英語表現のみ。作品はgiftの例)

```text
あなたは英語表現の解説を書く英語教育の専門家です。日本語話者の英語学習者(B1〜B2相当)向けに、下の英語表現それぞれの「一般的な解説」を日本語で書いてください。

# 前提
- 解説の対象は、英語表現そのものです。特定の文章・場面・物語には依存せず、その表現が英語で一般にどう使われるか、学習者が実際に使えるようになる知識を説明します。
- この依頼では、表現が使われていた記事・文脈は共有されていません。文脈を想像・推測して解説に織り込まないでください。

# 解説する英語表現
1. 英語表現: hand down
2. 英語表現: catch sight of
3. 英語表現: catch one's breath

# 解説の書き方
各表現について、学習者が自分の英語に取り入れられるように、次の観点から学習価値の高い内容を、必要十分な量の自然な日本語の文章で説明してください。すべての観点を機械的に列挙する必要はありません。
- 表現の核となる意味
- 主要な用法と、使われる場面
- よく使われるコロケーション(語の組み合わせ)
- 重要な類義語・近似表現との違い
- 自然に存在する比喩的・拡張的な用法
- 複合表現(語が組み合わさってできた語句)では、学習価値の中心となる語句(その語の一般的な使い方を知ると応用がきく部分)を中心に説明してよい。
- 使用頻度の順位(「最も一般的」「よく使われる順に」など)を、根拠なく断定しない。類義語との違いも、過度に断定せず、自然な英語として正確に説明する。
- 自然に存在する用法だけを書き、不自然な用法・用例を創作しない。すべての観点を無理に当てはめない。
- 文法の解説(構造・活用・語順など)には脱線しない。
- 説明の水増しをしない。「ほかの場面で使うと」という独立した追加例文は書かない(語句の組み合わせを示すコロケーションの表記は可)。

# 出力形式
Markdownのみ。表現ごとに次の形式で、前置き・後書きは付けない。
### 1. (英語表現)
(解説文。自然な日本語の文章。箇条書きは必要な場合のみ)
### 2. ...
```

## 2. Part 1 別LLM Prompt 案β(比較腕。入力=KP+本文での日本語意味)

```text
あなたは英語表現の解説を書く英語教育の専門家です。日本語話者の英語学習者(B1〜B2相当)向けに、下の英語表現それぞれの「一般的な解説」を日本語で書いてください。

# 前提
- 解説の対象は、英語表現そのものです。特定の文章・場面・物語には依存せず、その表現が英語で一般にどう使われるか、学習者が実際に使えるようになる知識を説明します。
- この依頼では、表現が使われていた記事・文脈は共有されていません。文脈を想像・推測して解説に織り込まないでください。
- 各表現には、参考として「本文での意味」(日本語、別工程で確定済み)が添えられています。これは、同じ形の表現が複数の意味・用法を持つ場合にどの意味の表現かを特定するための目印です。解説は、この意味に偏らず、表現の核となる意味と一般的な用法全体から説明してください。そのうえで、この意味が表現の用法全体の中でどこに位置づくかが自然に読み取れるようにし、この意味と矛盾する説明はしないでください。この意味そのものを言い換えて繰り返すことは目的ではありません。

# 解説する英語表現
1. 英語表現: hand down
   本文での意味: ～を後の世代に受け継がせる
2. 英語表現: catch sight of
   本文での意味: ～をふと目にする
3. 英語表現: catch one's breath
   本文での意味: 息を整える

# 解説の書き方
各表現について、学習者が自分の英語に取り入れられるように、次の観点から学習価値の高い内容を、必要十分な量の自然な日本語の文章で説明してください。すべての観点を機械的に列挙する必要はありません。
- 表現の核となる意味
- 主要な用法と、使われる場面
- よく使われるコロケーション(語の組み合わせ)
- 重要な類義語・近似表現との違い
- 自然に存在する比喩的・拡張的な用法
- 複合表現(語が組み合わさってできた語句)では、学習価値の中心となる語句(その語の一般的な使い方を知ると応用がきく部分)を中心に説明してよい。
- 使用頻度の順位(「最も一般的」「よく使われる順に」など)を、根拠なく断定しない。類義語との違いも、過度に断定せず、自然な英語として正確に説明する。
- 自然に存在する用法だけを書き、不自然な用法・用例を創作しない。すべての観点を無理に当てはめない。
- 文法の解説(構造・活用・語順など)には脱線しない。
- 説明の水増しをしない。「ほかの場面で使うと」という独立した追加例文は書かない(語句の組み合わせを示すコロケーションの表記は可)。

# 出力形式
Markdownのみ。表現ごとに次の形式で、前置き・後書きは付けない。
### 1. (英語表現)
(解説文。自然な日本語の文章。箇条書きは必要な場合のみ)
### 2. ...
```

## 3. Part 2 Step A(選定)Prompt(賢者の贈り物の例。作品別差替えは作品名・本文のみ)

```text
あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)から、日本語話者の学習者(B1〜B2相当)が読解でつまずきやすく、文法・構文の解説によって理解が深まる英文を選びます。この工程では解説文は書きません(解説は別の工程が行います)。選定だけを行ってください。

# 作品・レベル
- 作品: The Gift of the Magi(『賢者の贈り物』)
- レベル: Advanced

# 本文(段落番号[P1]〜[P30]は参照用。引用では番号を書かない)
[P1] One dollar and eighty-seven cents. Della counted the coins again, pressing each one against the table. Still the same. And tomorrow was Christmas.

[P2] She had saved every penny she could. How could she buy Jim something worthy of him?

[P3] For a while, she cried on their shabby couch. Then she caught sight of herself in the mirror.

[P4] They owned two things that made them proud. One was Jim’s gold watch, handed down from his grandfather to his father, and then to him. The other was Della’s long brown hair.

[P5] Slowly, she loosened her hair. It fell below her knees, shining in the pale light. She ran her fingers through it once. Then, before she could change her mind, she pulled on her coat.

[P6] Outside a hair-goods shop, she paused just long enough to catch her breath.

[P7] “Will you buy my hair?”

[P8] The owner lifted the heavy waves.

[P9] “Twenty dollars.”

[P10] “Cut it quickly, please.”

[P11] At the first touch of the scissors, Della shut her eyes.

[P12] For two hours afterward, she hurried from shop to shop. Finally, she found it: a simple platinum watch chain. Nothing showy, nothing unnecessary. Like Jim, it needed no decoration to prove its worth.

[P13] It cost twenty-one dollars.

[P14] She carried it home with eighty-seven cents left, imagining Jim replacing his worn leather watch strap with her beautiful gift.

[P15] By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror.

[P16] “Please let him still think I’m pretty,” she whispered.

[P17] Footsteps sounded. The door opened.

[P18] Jim stopped.

[P19] His eyes stayed on her hair. Della rushed toward him.

[P20] “I sold it, Jim. I couldn’t let Christmas come without giving you something. It’ll grow again!”

[P21] He put his arms around her. Then he gave her a package.

[P22] Inside were the tortoise-shell combs she had so often admired in a shop window.

[P23] She held them against her chest, smiling through tears.

[P24] “My hair grows quickly.”

[P25] Suddenly remembering, she brought out the chain.

[P26] “Look! Isn’t it perfect? Give me your watch.”

[P27] Jim sat down and smiled gently.

[P28] “I sold the watch to buy your combs.”

[P29] Della sat beside him and took his hand. Her hair was gone; the combs could not hold it. His watch was gone; the chain had nothing to carry. Each had sold their greatest treasure to buy the other a gift.

[P30] The magi were wise men who brought gifts on the first Christmas. Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers. They were the magi.

# 選定の観点
- 文法・構文の難しさ
- 文の構造を誤解しやすいか(主語・動詞・修飾関係・情報のつながりをつかみにくいか)
- 通常の語順・構造との違い
- 構文によって生じる意味やニュアンス
- 解説による学習価値(解説を読むと、その文の理解がどれだけ深まるか)
文法用語の難しさそのものは評価しない。
- 優先して検討する文の例: 語順が通常と異なる文、長い修飾語句・挿入・省略・並列・比較表現が重なって構造が見えにくい文、字面どおりに読むと意味を取り違えやすく構文の理解が必要な文。これらは例であり、該当する文が本文になければ無理に選ばない。
- 基礎的な文法項目(命令文、基本的な接続、前置詞句、分詞構文や付帯状況のwithなどの基本形、関係詞の基本用法、基本的な時制・受動態・比較・仮定法など)を説明するだけの選定はしない。特殊な用法や重要な表現効果がある場合に限る。
- 選ぶ文は0〜2個。解説価値の高い文が本文にない場合は0個とする。基礎的な文法項目を埋め草として選ばない。無理に2個選ばない。
- 本文全体から候補の文を複数検討し、解説価値が最も高い文を選ぶ。

# 出力(JSONオブジェクト1個のみ。前置き・後書き・コードフェンスなし)
{
  "candidates_considered": [{"para": "P4", "note": "検討した候補の文について、採否の理由を1行"}],
  "selected": [
    {
      "para": "P4",
      "sentence": "選んだ1文を本文から一字一句そのまま(逐語)",
      "construct_ja": "構文の名前(短く)",
      "points_ja": ["解説で押さえるべき点(最大3つ、短く)"],
      "context_ja": "その文の本文中での位置づけを1文で(本文に書かれた事実のみ。解釈や評価は書かない)",
      "reason_dev": "選定理由(開発者向けの記録。1〜2文。この欄はユーザー向け解説には使われない)"
    }
  ],
  "none_reason_dev": "selectedが空のとき、その理由を1文。空でなければ空文字"
}
- candidates_consideredは、検討した候補を最大5件(選んだ文を含む)。
- selectedは0〜2件。0件なら空配列。
```

## 4. Part 2 Step B(執筆)Prompt(<<…>>はStep A出力で差し替わる。例示は構造確認用プレースホルダ)

```text
あなたは英語学習の解説を書く執筆者です。別の工程で選ばれた英文と構文について、日本語話者の学習者(B1〜B2相当)が読んで理解できる解説を、自然で分かりやすい日本語で書いてください。この工程では英文の選定は行いません。渡された英文と構文をそのまま解説します。

# 解説する英文(別工程で確定済み)
[1] 英文: <<StepAが選んだ英文>>
   構文: <<構文名>>
   押さえる点:
     - <<要点>>
   本文での位置づけ: <<位置づけ>>

# 書き方
各英文について、次の順序で書く。
1. 日本語訳(自然な訳)
2. 文法・構文の仕組み: 渡された「構文」と「押さえる点」を、文のどの部分が何の働きをしているかを英文の該当箇所を示して具体的に説明する。教科書的な一般説明で終わらず、この英文を読み解く助けになる説明にする。
3. 通常の表現・語順との比較: 比較するとこの英文の仕組みが分かりやすくなる場合だけ書く。本文にない英文を示すときは「比較用」と明記し、本文の引用と区別する。不要なら、この項目自体を出力しない。
4. 意味・ニュアンス・表現効果: その構文によって、意味・ニュアンス・焦点・表現効果がどうなるか。「本文での位置づけ」の事実と結びつけて説明する。

- 学習者がそのまま読んで価値を感じられる、読みやすい文章にする。形式的・冗長な説明、同じ内容の繰り返しをしない。
- ユーザー向けの解説であり、選定理由・難易度の評価・品質の判定・工程への言及(「選ばれた」「学習価値が高い」「Advancedの学習者でも難しい」等)は一切書かない。
- 本文にない事実・登場人物の言動を作らない。「本文での位置づけ」に書かれた事実の範囲で述べる。
- 本文の英文を引用するときは、渡された英文から一字一句そのまま(逐語)引用する。
- 英文そのものの再掲(見出しとしての掲載)は不要(別途表示される)。

# 出力形式
Markdownのみ。前置き・後書きなし。英文ごとに、次の区切りと見出し行を使う。
=====ITEM 1=====
【日本語訳】
(...)
【文法・構文の仕組み】
(...)
【通常の表現・語順との比較】(不要なら、この見出し行と本文ごと出力しない)
(...)
【意味・ニュアンス・表現効果】
(...)
=====ITEM 2=====(英文が2つのときだけ。同じ形式)
```

## 5. Part 3/4 Prompt(03dのPart 3/4ブロックをそのまま。賢者の例)

```text
あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本(Advancedレベル)を読んだ学習者向けに、音声と連動して読む「英語学習テキスト解説」を日本語で書いてください。

# 作品・レベル
- 作品: The Gift of the Magi(『賢者の贈り物』)
- レベル: Advanced(CEFR B1を目標に書かれた英文。学習者はB1〜B2相当の日本語話者)

# 本文(段落番号[P1]〜[P30]は参照用。引用では番号を書かない)
[P1] One dollar and eighty-seven cents. Della counted the coins again, pressing each one against the table. Still the same. And tomorrow was Christmas.

[P2] She had saved every penny she could. How could she buy Jim something worthy of him?

[P3] For a while, she cried on their shabby couch. Then she caught sight of herself in the mirror.

[P4] They owned two things that made them proud. One was Jim’s gold watch, handed down from his grandfather to his father, and then to him. The other was Della’s long brown hair.

[P5] Slowly, she loosened her hair. It fell below her knees, shining in the pale light. She ran her fingers through it once. Then, before she could change her mind, she pulled on her coat.

[P6] Outside a hair-goods shop, she paused just long enough to catch her breath.

[P7] “Will you buy my hair?”

[P8] The owner lifted the heavy waves.

[P9] “Twenty dollars.”

[P10] “Cut it quickly, please.”

[P11] At the first touch of the scissors, Della shut her eyes.

[P12] For two hours afterward, she hurried from shop to shop. Finally, she found it: a simple platinum watch chain. Nothing showy, nothing unnecessary. Like Jim, it needed no decoration to prove its worth.

[P13] It cost twenty-one dollars.

[P14] She carried it home with eighty-seven cents left, imagining Jim replacing his worn leather watch strap with her beautiful gift.

[P15] By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror.

[P16] “Please let him still think I’m pretty,” she whispered.

[P17] Footsteps sounded. The door opened.

[P18] Jim stopped.

[P19] His eyes stayed on her hair. Della rushed toward him.

[P20] “I sold it, Jim. I couldn’t let Christmas come without giving you something. It’ll grow again!”

[P21] He put his arms around her. Then he gave her a package.

[P22] Inside were the tortoise-shell combs she had so often admired in a shop window.

[P23] She held them against her chest, smiling through tears.

[P24] “My hair grows quickly.”

[P25] Suddenly remembering, she brought out the chain.

[P26] “Look! Isn’t it perfect? Give me your watch.”

[P27] Jim sat down and smiled gently.

[P28] “I sold the watch to buy your combs.”

[P29] Della sat beside him and took his hand. Her hair was gone; the combs could not hold it. His watch was gone; the chain had nothing to carry. Each had sold their greatest treasure to buy the other a gift.

[P30] The magi were wise men who brought gifts on the first Christmas. Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers. They were the magi.

# 既存のKey Phrase(Part 1で使う。新たなフレーズ選定は禁止)
1. 英語表現: hand down
   日本語gloss: ～を後の世代に受け継がせる
   本文の該当文: One was Jim’s gold watch, handed down from his grandfather to his father, and then to him.
   既存の音声解説(英語・重複回避用): "to pass something to a younger person or a later generation"
2. 英語表現: catch sight of
   日本語gloss: ～をふと目にする
   本文の該当文: Then she caught sight of herself in the mirror.
   既存の音声解説(英語・重複回避用): "to see something suddenly or by chance"
3. 英語表現: catch one's breath
   日本語gloss: 息を整える
   本文の該当文: Outside a hair-goods shop, she paused just long enough to catch her breath.
   既存の音声解説(英語・重複回避用): "to pause and breathe normally again after effort"

# Part 2で扱う文(別工程で確定済み。Part 3はこれらと内容を重複させない)
<<StepAが選んだ英文(0件なら『なし』)>>

# 出力する内容(Part 3とPart 4のみ、この順序・この見出しで。Part 1・Part 2は別工程で作成済み)

## Part 3. Nuance & Deeper Understanding
本文から価値のある英語表現・ニュアンスのテーマを0〜1個選ぶ。適切なテーマがなければ0個とし、その旨を一文で書く。
- 単語の意味だけでは伝わりにくいニュアンス、似た表現との違い、表現による印象の違いなどを深掘りする。
- Part 1・Part 2と内容を重複させない。
- 物語の感想や一般論ではなく、英語学習としての価値を重視する。

## Part 4. Think & Express
作品の内容に関連して、学習者が自分の考えを英語で表現するための問いを1問作る。次の4点を書く: 英語の質問 / その日本語訳 / 英語の回答例 / その日本語訳。回答例は学習者が参考にできる自然な英語にする。

# 制約
- 本文の英文を引用するときは、本文から一字一句そのまま(逐語)引用する。改変・要約・つなぎ合わせをしない。
- 本文にない事実・登場人物の言動・表現を作らない。説明は本文の根拠に基づく。
- 日本語は学習者に読みやすく書く。
- 理解度チェック・クイズは書かない。
- 出力はMarkdownのみ。上記の見出し(## Part 3、## Part 4)構成を守り、前置き・後書きは付けない。
```

