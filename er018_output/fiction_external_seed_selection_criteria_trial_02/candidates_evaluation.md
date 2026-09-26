# FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02 -- candidates_evaluation.md

Trial専用。Production Fiction仕様への反映は本タスクの対象外。到達上限VALIDATED。

## 0. 方法論上の重要な発見(前提として先に記す)

Trial-01では、LOC (`www.loc.gov`) の個別アイテムページ(カタログページ)への
直接HTTP GETがCloudflareの403ブロックを受け、「manuscript full textが確認
できない」という前提でSeed化が行われた。本Trialで、実際のマニュスクリプト
画像/OCRテキストは `www.loc.gov` ではなく `tile.loc.gov` の
storage-services経路(例: `https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-XXXXXXXX/wpalh-XXXXXXXX.pdf`)
でHTTP 200・平文OCRテキスト抽出可能であることを発見した(pypdfを`.venv`へ
追加インストールしテキスト抽出を確認)。

この発見により、LOC由来の4候補すべてで一次テキストを実際に読むことができた。
その結果判明したのは、**Trial-01の`candidates.md`の"ストーリー化に向く理由"
記述が、実際の一次テキストの内容と一致しない(誇張または創作)ケースが複数
あった**という、本Trialの目的そのものを裏付ける事実である(詳細は下表と§4)。

## 1. 01_life_history(実話・人生談)

| Source | 一次テキスト確認(URL/取得可否/冒頭引用) | 権利 | 必須Gate PASS/FAIL | A | B | C | D | PASS数 | 採用/非採用 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|
| A Wagon Train Encounter with a Runaway Ox (Mrs. Jane Lee Smith, "Brindy") | https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-29091808/wpalh-29091808.pdf / HTTP 200・OCR取得可 / 冒頭: "My father and mother crossed the plains in 1847... Among father's oxen was an old animal they called Brindy" | LOC rights statement(no known copyright、federal employee work) | Gate1 PASS(今回tile.loc.gov経由で新規に確認)/Gate2 PASS/Gate3 **FAIL** | 否 | 弱 | 否 | 否 | 0/4 | **非採用** | 実物は「ゲート」も「突進してくる牛」も存在しない。実際は雑多な逸話集(雷雨で子供死亡、Brindyが先住民女性を威嚇して家族を守る、ホーム女性の川転落、パラボアの卵詐欺 等)で、聞き取り者自身が末尾コメントで「話す事が少なくて残念」と明記。人種偏見的な記述("had it in for redskins")も含む。前回生成された"The Open Gate"はこの一次テキストとほぼ無関係な創作。 |
| The Barber Who Was Also the Town Dentist (Mrs. Clara Fergusson) | https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-20040609/wpalh-20040609.pdf / HTTP 200・OCR取得可 / 冒頭: "When I asked Mrs. Ferguson to tell me of her pioneer life in New Mexico..." | LOC rights statement | Gate1 PASS(新規確認)/Gate2 PASS/Gate3 **FAIL** | 否 | 中 | 中 | 否 | 1-2/4 | **非採用** | 実物はHuning一族(著名な地元名家)の広範な家族史・地域史インタビュー(鉄道到来、洪水、子供の葬列の風習等)で、「床屋兼歯科医」は挿話の一つに過ぎない。単一事件として抽出するには一次テキストにない創作が必要。 |
| A Young Immigrant Family's Journey to Nebraska (Mrs. John Donnelly) | https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-16120605/wpalh-16120605.pdf / HTTP 200だが実際の"Text of Interview"本文が未収録("Copies attached of interview"と記載されるのみで添付が本PDFに含まれない) | LOC rights statement | **Gate1 FAIL**(該当エピソード本文が確認不能) | - | - | - | - | - | **非採用** | Gate1未達のため以降評価せず。 |
| A Railroad Worker's Encounter on the Nebraska Frontier (I.B. Smith) | https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-16021304/wpalh-16021304.pdf / HTTP 200・OCR取得可(全4ページ) / 冒頭: "I was born in Providence Rhode Island. My mother was a Seminole Indian..." | LOC rights statement | Gate1 PASS(新規確認)/Gate2 PASS/Gate3 **FAIL** | 否 | 中 | 中 | 否 | 1/4 | **非採用** | 実物は「先住民との遭遇」ではなく、教育者・説教師・銀行員・郵便配達員という生涯の業績列挙(ジョージ・ワシントン・カーヴァーとの友情の逸話含む)。単一事件がなく、Trial-01の"story_fit_reason"(「先住民との遭遇」)は一次テキストに存在しない。 |
| **[新規]** The water-pump moment (Helen Keller, *The Story of My Life*) | https://www.gutenberg.org/ebooks/2397.txt.utf-8 / HTTP 200 / 冒頭: "...Miss Sullivan had tried to impress it upon me that 'm-u-g' is mug and that 'w-a-t-e-r' is water... somehow the mystery of language was revealed to me." | Public domain in the USA(Gutenberg #2397) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **採用** | 実在の有名な単一場面。人形を壊す怒り→ポンプでの言語獲得の閃き→後悔、という明確な中心事件と変化があり、A2圧縮でも魅力が失われない。 |

## 2. 02_historical(実話・歴史的逸話)

| Source | 一次テキスト確認(URL/取得可否/冒頭引用) | 権利 | 必須Gate PASS/FAIL | A | B | C | D | PASS数 | 採用/非採用 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|
| Franklin Arrives in Philadelphia with Three Rolls of Bread | https://www.gutenberg.org/cache/epub/148/pg148.html / HTTP 200(Trial-01で既取得、本Trialでも再確認) | Public domain(Gutenberg #148) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 中 | 是 | 4/4 | **前回採用済み(regenerate対象外)** | "Two Plus One"として生成済み(ユーザー評価「悪くない」)。本Trialでは再生成しない。参考: 実際の生成物は駅の朝食セット割引という現代的設定へ大幅に翻案されており、方針(1)(忠実な再話も許容)の観点では今後さらに一次テキストに近い再話も選択肢になり得る。 |
| A Confederate Stableman Changes Sides ("Autobiography of a Scalawag") | https://en.wikisource.org/wiki/Autobiography_of_a_Scalawag / HTTP 200 / 冒頭: "About forty-odd years ago, having Bin the younffest of 14 children..." | Public domain(Wikisource、1869年以前) | Gate1 PASS/Gate2 PASS/**「実話」要件 FAIL(新規判明)** | - | - | - | - | - | **非採用(新規判明の理由)** | Wikisourceページのヘッダーに著者名「G. W. Bagby and A. F. Stofer」の表記があることを本Trialで確認。G. W. Bagbyは実在の南部の風刺作家であり、本作は実際の元寝返り者の回想録ではなく**風刺フィクション**の可能性が高い。02_historicalは「実話・歴史的逸話」カテゴリのため、実話性が確認できない本候補は除外する(Trial-01の候補表はこの著者情報を記載していなかった)。 |
| A Missouri Diarist's Wartime Life (John Jay Johns diary) | https://en.wikisource.org/wiki/A_Short_History_of_My_Life / HTTP 200 / 全文取得・確認済み | Public domain worldwide(Wikisource、著者没後100年超) | Gate1 PASS/Gate2 PASS/Gate3 **FAIL** | 否 | 否 | 弱 | 否 | 0/4 | **非採用** | 実物は出生・結婚・転居・出産・死亡を淡々と列挙する年代記(奴隷所有についても事実として言及するのみ)であり、場面・対話・単一事件が皆無。圧縮すべき「物語」自体が存在しない。 |
| **[新規]** The lion attack (David Livingstone, *Missionary Travels and Researches in South Africa*) | https://www.gutenberg.org/ebooks/1039.txt.utf-8 / HTTP 200 / 該当箇所: "I saw the lion just in the act of springing upon me... Growling horribly close to my ear, he shook me as a terrier dog does a rat." | Public domain in the USA(Gutenberg #1039) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **採用** | 実在の有名な単一事件(ライオンに襲われ、恐怖を感じない奇妙な心理状態を経験)。生涯残る腕の損傷という結末もあり、圧縮しても魅力・意味が残る。 |

## 3. 03_japanese_lit(日本文学・青空文庫)

| Source | 一次テキスト確認(URL/取得可否/冒頭引用) | 権利 | 必須Gate PASS/FAIL | A | B | C | D | PASS数 | 採用/非採用 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|
| A Servant at the Rashomon Gate(芥川龍之介「羅生門」) | https://www.aozora.gr.jp/cards/000879/files/127_15260.html / HTTP 200 / 冒頭: 「ある日の暮方の事である。一人の下人が、羅生門の下で雨やみを待っていた。」/ 結末: 「下人は、すばやく、老婆の着物を剥ぎとった...下人の行方は、誰も知らない。」 | Aozora公開・没年1927(著作権切れ) | Gate1 PASS(本Trialで新規に全文取得・確認)/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **採用(新規生成)** | 中心的な道徳的転換(飢え死にか盗人になるか)、明確な結末、A2圧縮に強い二人劇構造。 |
| The Friend Who Must Run(太宰治「走れメロス」) | https://www.aozora.gr.jp/cards/000035/files/1567_14913.html / HTTP 200 / 冒頭: 「メロスは激怒した。」/ 結末: 「おまえらの望みは叶ったぞ。おまえらは、わしの心に勝ったのだ。」 | Aozora公開・没年1948(著作権切れ) | Gate1 PASS(本Trialで新規に全文取得・確認)/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **採用(新規生成)** | 時間制限のある救出劇、絶望からの再起という感情の核、圧縮しても失われない明確な構造。 |
| Two Hunters at the Strange Restaurant(宮沢賢治「注文の多い料理店」) | Trial-01で全文取得・確認済み(本Trialでも再確認、`files/1927_17906.html`) | Aozora公開・没年1933(著作権切れ) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **前回採用済み(regenerate対象外)** | "Kind Lodge"として生成済み(ユーザー評価「良い」)。本Trialでは再生成しない。 |
| A Night Encounter in a Narrow Street(梶井基次郎「交尾」) | https://www.aozora.gr.jp/cards/000074/files/423_504.html / HTTP 200 / 冒頭: 「星空を見上げると、音もしないで何匹も蝙蝠が飛んでいる。」 / 内容: 深夜の猫と河鹿(カジカ蛙)の交尾を観察する、雰囲気重視の一人称随筆的短編。 | Aozora公開・没年1932(著作権切れ) | Gate1 PASS(本Trialで新規に全文取得・確認)/Gate2 PASS/Gate3 **FAIL** | 否 | 弱 | 弱 | 否 | 0-1/4 | **非採用** | 中心的な事件・変化がなく、魅力は文体・感覚描写そのものにある。A2への簡略化はまさにその魅力を破壊する(Gate運用定義が事前に警告する「純文学・雰囲気重視」の典型例)。 |

## 4. 04_world_lit(世界文学)

| Source | 一次テキスト確認(URL/取得可否/冒頭引用) | 権利 | 必須Gate PASS/FAIL | A | B | C | D | PASS数 | 採用/非採用 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|
| **[新規]** The Bet(Anton Chekhov) | https://www.gutenberg.org/ebooks/55283.txt.utf-8 / HTTP 200 / 冒頭: "It was a dark autumn night. The old banker was pacing..." / 結末: "he had seen the man who lived in the wing climbing through the window into the garden... and disappear." | Public domain in the USA(Gutenberg #55283) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **採用(新規生成)** | 賭け・監禁・15年の内面変化・殺害計画・自発的放棄という明確な事件連鎖、圧縮耐性も高い。 |
| A Couple's Impossible Christmas Gifts(O. Henry, "The Gift of the Magi") | https://www.gutenberg.org/ebooks/7256.txt.utf-8 / HTTP 200 / 冒頭: "One dollar and eighty-seven cents. That was all." | Public domain(Gutenberg #7256) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | 採用可能(今回は非選択) | 全基準PASSだが、非常に有名で「オチ」が広く知られており、新鮮さの観点から今回は優先度を下げた(Trial-01時点でも同様の懸念が記載されていた)。 |
| The Signalman's Dangerous Decision(Vsevolod Garshin, "The Signal") | https://www.gutenberg.org/ebooks/68619.txt.utf-8 / HTTP 200(Trial-01で既取得、本Trialでも再確認) | Public domain(Gutenberg #68619) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | **前回採用済み(regenerate対象外)** | "Red Scarf"として生成済み(ユーザー評価「悪くない」)。本Trialでは再生成しない。 |
| A Woman Who Borrows a Necklace(Guy de Maupassant, "The Necklace") | https://www.gutenberg.org/ebooks/10483.txt.utf-8 / HTTP 200 / 冒頭: "THE NECKLACE (1885)... BY GUY DE MAUPASSANT" | Public domain(Gutenberg #10483) | Gate1 PASS/Gate2 PASS/Gate3 PASS | 是 | 是 | 是 | 是 | 4/4 | 採用可能(今回は非選択) | 全基準PASSだが、"The Gift of the Magi"と同様に非常に有名で「オチ」が広く知られている(Trial-01でも同懸念記載)。 |
| A Stranger Trapped Behind a Door(R. L. Stevenson, "The Sire de Maletroit's Door") | https://www.gutenberg.org/ebooks/21964.txt.utf-8 / HTTP 200 / 冒頭: "Denis de Beaulieu was not yet two-and-twenty..." | Public domain(Gutenberg #21964) | Gate1 PASS/Gate2 PASS/Gate3 中間 | 是 | 是 | 中 | 中 | 3/4 | 採用可能(今回は非選択) | 宮廷劇的な人物関係・剣戟・強制結婚という筋立てが濃く、300-350語への圧縮は他候補より難度が高い(4基準中3程度)。 |

## 5. 前回採用4作の再評価まとめ

| 前回のStory | 元候補 | 新基準での再評価 |
|---|---|---|
| The Open Gate(弱い) | LOC "Crossing the Plains"(Ox/Brindy) | Gate1は今回**PASS**(tile.loc.gov経由で確認可能と判明)。しかしGate3/Story基準(A/C/D)は**FAIL**。一次テキストは雑多な逸話集で「ゲート」も「突進する牛」も存在せず、Storyはほぼ全面創作だった。詳細は§6。 |
| Two Plus One(悪くない) | Franklin's Autobiography(パンの場面) | Gate1-3すべてPASS(4/4)。実際の一次テキストとの一致度は高い題材だが、生成されたStoryは現代の駅カフェへ大幅に翻案されており、方針(1)の「忠実な再話」寄りにも再挑戦し得る。 |
| The Kind Lodge(良い) | 宮沢賢治「注文の多い料理店」 | Gate1-3すべてPASS(4/4)。新基準でも最上位級の候補であることを確認。 |
| The Red Scarf(悪くない) | Garshin「シグナル」 | Gate1-3すべてPASS(4/4)。 |

## 6. "The Open Gate"の元候補(LOC "Crossing the Plains")に対する新Gateの明示的判定

**Gate1(一次内容を実際に確認可能): 今回PASSに変わった。**
Trial-01は`www.loc.gov`のカタログページがCloudflareで403ブロックされたため
「manuscript full textが確認できない」と結論したが、本Trialで
`tile.loc.gov`のPDF直リンク(`https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-29091808/wpalh-29091808.pdf`)
がHTTP 200で取得でき、pypdfでOCRテキストが抽出できることを発見した。
すなわち、この候補は「原理的に確認不能」だったのではなく、「Trial-01が
確認する前に生成へ進んでしまった」ケースである。

**Gate3(限られた尺へ圧縮しても中心Storyを保持可能): 今回もFAILのまま。**
実際に読んだ一次テキスト(Mrs. Jane Lee Smithへのインタビュー、1939年4月27日、
聞き取り者Sara B. Wrenn)は、雷雨で子供が死んだ話、去勢牛Brindyが先住民の
女性たちを威嚇して家族のイチゴを守った話、大きなスカートの女性が川で立ち
往生した話、パラボアの卵の詐欺話など、脈絡のない短い逸話の寄せ集めであり、
末尾のForm D(聞き取り者自身のコメント)には次のように明記されている:
「Possessing a keen sense of humor as she does, it is to be regretted that
Mrs. Smith had so little to tell」(ユーモアのセンスはあるものの、話す事が
とても少なかったのは残念だ)。"The Open Gate"に描かれた「ゲートを開けて
母を救う」という中心事件は、この一次テキストのどこにも存在しない。

**結論**: 一次テキストを実際に読める・読めないの問題と、読んだ内容が良い
Story素材であるかの問題は別である。本候補はGate1が新たにPASSに転じたにも
かかわらず、Gate3(および品質基準A/C/D)で依然FAILする、という結論になる。
これは「確認できれば良い候補になる」という単純な話ではなく、Trial-01時点
での候補選定プロセス自体(web_search要約のみに基づく"story_fit_reason"の
作文)に構造的な問題があったことを示す。

## 7. 予算実績

- 本Trialの一次テキスト調査はすべて直接HTTP GET(`requests`)で実施し、
  web_search呼び出しは0回・$0(pypdfを`.venv`へ追加インストールした以外の
  追加コストなし)。
- Seed化(5件)+Story生成(5件)のAPI呼び出しのみ課金対象で、合計
  $0.010976(約¥1.76)。上限¥60に対し大幅な余裕。詳細は`cost.json`。
