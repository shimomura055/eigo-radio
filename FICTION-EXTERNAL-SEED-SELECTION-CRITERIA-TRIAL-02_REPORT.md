# FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02 REPORT

Status: **完走(T-1候補再評価〜T-2 Story生成5本〜T-3評価、Sonnet仮分類
VALIDATED、詳細は§9)**。Trial専用、未承認draft実装。Production Fiction
仕様への反映は本タスクの対象外。到達上限VALIDATED。

## §1 目的・方針

`FICTION-EXTERNAL-STORY-SEED-TRIAL-01`(以下Trial-01)で生成した4本
(The Open Gate/Two Plus One/The Kind Lodge/The Red Scarf)へのユーザー評価
は、「The Open Gate(人生談)は弱い、だから何?という反応。素材選定側の問題
(元マニュスクリプト本文が確認できず骨格だけからAIが展開を作った)」
「Two Plus One/The Red Scarfは悪くない」「The Kind Lodgeは良い」であり、
総評として「ゼロから創作よりも外部Seed方式が大幅に良い。今後は素材選定
精度を改善」というものだった。本Trialの目的は、(a) 元作品・一次内容を
実際に確認できたかを必須Gateとして明文化し、(b) 4項目のStory品質基準
(A中心事件/B読者関心/C意味ある展開/D短編化耐性)で候補を再評価し、
(c) 前回採用作(Kind Lodge等)は再生成せず、新基準を満たす別の素材から
系統ごとに1〜2本(合計4〜6本)を生成すること。方針として、外部作品は
無理に改変せず(PDなら忠実な再話・現代化も許容)、尺調整のための簡略化
のみ明記する(前回の「捨てる要素」指示を「尺調整のための簡略化」へ置換)。

## §2 必須Gate/4基準の運用定義

**必須Gate(1つでも欠ければ除外)**:
1. 元作品・一次内容を実際に確認可能 -- 本Trialでは**直接HTTP GETで一次
   テキストを実際に取得し、URL・取得日時・冒頭数行(および可能な場合は
   結末部)の引用で証跡化**することを必須とした。web_searchの要約のみで
   「確認できた」とはみなさない。
2. 権利状態が利用目的上問題ない -- ソース自身の明示的なPD/CC0表示。
3. 限られた尺(A2、280〜420語)へ圧縮しても中心Storyを保持可能。

**Story品質基準(4項目中3項目以上でPASS)**:
- A. 中心となる出来事・変化(追える中心事件・行動・関係変化・選択)
- B. 読者の関心を維持する要素(Hook・緊張・意外性・疑問・人間関係・共感・
  皮肉・強い状況設定。派手なHook必須ではない)
- C. 意味のある展開・変化・余韻(明確なオチ必須ではない)
- D. 短編化(280〜420語)しても魅力が残る(文体・長い心理描写を削ると
  魅力が消える作品は不向き)

## §3 候補再評価表(4系統)

全文は`er018_output/fiction_external_seed_selection_criteria_trial_02/candidates_evaluation.md`
に保存。要約は以下のとおり(表は元ファイルそのまま、報告本文では割愛せず
主要ポイントのみ抜粋。詳細な引用・URLは同ファイル参照)。

### 方法論上の発見
Trial-01は`www.loc.gov`個別アイテムページがCloudflareで403ブロックされた
ため「manuscript full textが確認できない」としたが、本Trialで
`tile.loc.gov`のPDF直リンク(例: `https://tile.loc.gov/storage-services/service/mss/wpalh/wpalh-29091808/wpalh-29091808.pdf`)
がHTTP 200・OCRテキスト抽出可能であることを発見した(pypdfを`.venv`へ
追加インストール)。この結果、LOC由来4候補すべてを実際に読むことができ、
Trial-01の"story_fit_reason"記述の少なくとも3件(ox/barber/railroad)が
一次テキストの実際の内容と大きく食い違っている(誇張または創作)ことが
判明した。

### 01_life_history(実話・人生談)
| 候補 | Gate1 | Gate3 | PASS数 | 判定 |
|---|---|---|---|---|
| Ox/Brindy(Mrs. Jane Lee Smith) | PASS(新規確認) | FAIL | 0/4 | 非採用 |
| Barber/Dentist(Mrs. Clara Fergusson) | PASS(新規確認) | FAIL | 1-2/4 | 非採用 |
| Immigrant(Mrs. John Donnelly) | **FAIL**(該当インタビュー本文が未収録) | - | - | 非採用 |
| Railroad(I.B. Smith) | PASS(新規確認) | FAIL | 1/4 | 非採用 |
| **[新規]** Helen Keller の水の場面 | PASS | PASS | **4/4** | **採用** |

### 02_historical(実話・歴史的逸話)
| 候補 | Gate1 | Gate3/実話性 | PASS数 | 判定 |
|---|---|---|---|---|
| Franklin(パンの場面) | PASS | PASS | 4/4 | 前回採用済み(regenerate対象外) |
| "Autobiography of a Scalawag" | PASS | **「実話」要件FAIL(新規判明)** | - | 非採用 |
| Johns diary(年代記) | PASS | FAIL | 0/4 | 非採用 |
| **[新規]** David Livingstoneのライオン襲撃 | PASS | PASS | **4/4** | **採用** |

### 03_japanese_lit(日本文学・青空文庫)
| 候補 | Gate1 | Gate3 | PASS数 | 判定 |
|---|---|---|---|---|
| **[新規]** 芥川「羅生門」 | PASS(新規全文確認) | PASS | **4/4** | **採用** |
| **[新規]** 太宰「走れメロス」 | PASS(新規全文確認) | PASS | **4/4** | **採用** |
| 宮沢賢治「注文の多い料理店」 | PASS | PASS | 4/4 | 前回採用済み(regenerate対象外) |
| 梶井「交尾」 | PASS(新規全文確認) | FAIL | 0-1/4 | 非採用 |

### 04_world_lit(世界文学)
| 候補 | Gate1 | Gate3 | PASS数 | 判定 |
|---|---|---|---|---|
| **[新規]** Chekhov「賭け」 | PASS | PASS | **4/4** | **採用** |
| O. Henry「賢者の贈り物」 | PASS | PASS | 4/4 | 採用可能(今回非選択、有名すぎる懸念) |
| Garshin「シグナル」 | PASS | PASS | 4/4 | 前回採用済み(regenerate対象外) |
| Maupassant「首飾り」 | PASS | PASS | 4/4 | 採用可能(今回非選択、有名すぎる懸念) |
| Stevenson「マレトロワ氏の扉」 | PASS | 中間 | 3/4 | 採用可能(今回非選択、圧縮難度やや高) |

## §4 "The Open Gate"元候補の新Gate判定

**Gate1(確認可能): 今回PASSに変わった。** Trial-01時点では`www.loc.gov`
がCloudflareでブロックされたため「確認不能」としたが、本Trialで
`tile.loc.gov`のPDF直リンク経由での取得ルートを発見し、実際にOCR全文を
取得できた(§3参照)。つまりこの候補は原理的に確認不能だったのではなく、
「Trial-01が確認する前に生成へ進んでしまった」ケースだった。

**Gate3(圧縮しても中心Story保持可能): 今回もFAILのまま。** 実際の一次
テキスト(Mrs. Jane Lee Smithへのインタビュー、1939年4月27日)は、雷雨で
子供が死んだ話・去勢牛Brindyが先住民の女性を威嚇して家族のイチゴを守った
話・大きなスカートの女性が川で立ち往生した話・パラボアの卵の詐欺話など、
脈絡のない短い逸話の寄せ集めであり、聞き取り者Sara B. Wrenn自身が末尾
コメント(Form D)で「Possessing a keen sense of humor as she does, it is
to be regretted that Mrs. Smith had so little to tell」(ユーモアのセンス
はあるが、話す事がとても少なかったのは残念だ)と明記している。
"The Open Gate"に描かれた「暴れる牛からゲートを開けて母を救う」という
中心事件は、この一次テキストのどこにも存在しない。

**結論**: 「確認できるかどうか」と「確認した内容が良いStory素材かどうか」
は別の問題である。本候補はGate1が新たにPASSに転じたにもかかわらず、
Gate3および品質基準A/C/Dで依然FAILする。これはTrial-01の候補選定プロセス
自体(web_searchの要約のみに基づく"story_fit_reason"の作文、一次テキスト
を実際に読まないままSeed化へ進む運用)に構造的な問題があったことを示す。

## §5 Seed(各件)

5件のSeed全文は
`er018_output/fiction_external_seed_selection_criteria_trial_02/stories/{key}/seed.json`
に保存。各Seedの`conversion_plan`は共通して「忠実な再話・現代化を許容し、
オリジナル感のための機械的変更をしない」方針を明記している(前回の
「捨てる要素」指示を「尺調整のための簡略化」へ置換、方針(1)準拠)。

- `01_life_history_1`: Helen Kellerの水の場面。discarded_elementsは教師の
  実名、周辺の週数分の授業描写など(尺調整のための簡略化のみ)。
- `02_historical_1`: Livingstoneのライオン襲撃。discarded_elementsは
  同行者の実名(Mebalwe等、役割表現へ置換)。
- `03_japanese_lit_1`: 羅生門。もともと登場人物に固有名がなく、命名規則
  (主人公のみ固有名可)と完全に整合。
- `03_japanese_lit_2`: 走れメロス。主人公メロスのみ固有名を残し、友人・
  王は関係性表現へ。
- `04_world_lit_1`: 賭け。もともと固有名がなく(「銀行家」「若い弁護士」)、
  命名規則と完全に整合。

## §6 Story全文

5本の全文は下記に保存(ブラインド版は`blind.md`、正解は`blind_key.json`):
`er018_output/fiction_external_seed_selection_criteria_trial_02/stories_all.md`

### The Word in My Hand(01_life_history_1、Helen Keller)
367語。

### The Lion That Rose Again(02_historical_1、David Livingstone)
341語。

### Under the Ruined Gate(03_japanese_lit_1、芥川「羅生門」)
396語。

### The Three-Day Promise(03_japanese_lit_2、太宰「走れメロス」)
385語。

### The Door Before Midnight(04_world_lit_1、Chekhov「賭け」)
380語。

(本文全文は上記`stories_all.md`および`blind.md`を参照。字数はすべて
280-420語の許容範囲内。)

## §7 Sonnet所見

1. **前回の弱い素材は落ちたか**: 落ちた。01系統の4前回候補(ox/barber/
   immigrant/railroad)は、一次テキストを実際に読んだ結果すべて非採用と
   なった。02系統の「Autobiography of a Scalawag」は、本Trialで著者名
   (G. W. Bagbyという実在の南部風刺作家)が確認でき、「実話」ではなく
   風刺フィクションの疑いが強いことが新たに判明し除外した(Trial-01の
   候補表はこの著者情報を欠いていた)。
2. **良い素材をHook不足・結末不足だけで誤って落としていないか**: 大きな
   懸念は見られない。今回追加した5候補(Keller/Livingstone/Rashomon/
   Melos/Bet)はいずれも4/4で明確にPASSしており、逆に「Hookは弱いが
   実は良い」ボーダーライン候補として「A Stranger Trapped Behind a
   Door」(Stevenson)を3/4で記録した(圧縮難度がやや高いという理由で
   今回非選択としたが、除外ではなく「採用可能」と明記)。梶井「交尾」は
   Gate運用定義が事前に明記した「純文学・雰囲気重視でStoryが弱い」の
   典型例であり、これは基準の誤判定というより基準どおりの想定内除外。
3. **Literatureだけが有利になっていないか(系統別PASS率)**: 01系統は
   5候補中1件PASS(20%、ただし新規追加分)、02系統は4候補中1件PASS
   (25%、同前)、03系統は4候補中3件がPASS相当(75%、うち1件は前回採用
   済み)、04系統は5候補中4件PASS(80%、うち1件は前回採用済み)。
   文学系統(03/04)のPASS率が実話系統(01/02)より明確に高い。ただし
   これは基準がLiteratureへ有利に設計されているためではなく、**実話
   系のPD一次資料(特にLOCの生インタビュー記録)は、そもそも「小説家が
   すでに物語として整形した文学作品」と比べて、単一の中心事件を持つ
   確率が構造的に低い**ため(インタビューは通常、生涯の様々な出来事の
   雑多な集合になりやすい)と考えられる。実話系統でも、Keller/
   Livingstoneのように「単一の劇的場面」を含む一次資料を選べば同じく
   4/4でPASSしており、基準自体がLiterature優遇ではないことを示す。
4. **実話で面白い素材を選べたか**: 選べた。Helen Kellerの水の場面、
   David Livingstoneのライオン襲撃はいずれも、LOCの雑多なインタビュー
   記録よりも遥かに強い中心事件・感情の核を持つ、より適切なPD一次資料
   だった(LOC以外のPD一次資料を候補に含めてよいという委任文の許可を
   活用した結果)。

## §8 QCD

- **実行**: Seed化5 call + Story生成5 call = API call合計10回、全て成功
  (技術的retry 0回)。一次テキスト調査はすべて直接HTTP GET(`requests`)、
  web_search呼び出しは**0回・$0**。
- **費用**: 累計**$0.010976(約¥1.76)**、上限¥60に対し1.76/60 =
  約2.9%。`cost.json`: `{"total_usd": 0.010976, "total_jpy": 1.76,
  "record_count": 10, "web_search_call_total": 0}`。
- **語数**: 5本すべて280-420語の許容範囲内(341-396語)。
- **追加インストール**: `.venv`へ`pypdf`を追加インストール(LOCマニュスク
  リプトPDFのOCRテキスト抽出のため、読み取り専用の調査目的、Production
  コードへの影響なし)。

## §9 Sonnet仮分類

**VALIDATED**(委任文が定める到達上限)。T-1(候補再評価、必須Gate運用
定義の明文化、`The Open Gate`元候補の新Gate判定含む)〜T-2(Seed化・
Story生成5本、全て技術的成功)〜T-3(評価)を完走。前回の弱かった素材の
除外理由を一次テキストで裏付け、新たに4/4でPASSする5候補から5本を生成
した。Production Fiction仕様への反映は本タスクの対象外であり、
`APPROVED_FOR_PRODUCTION`は人間ユーザーの判断を要する。

## §10 Fable評価(ブラインド: blind.mdを先に読み、key開封後も判断不変。A=Chekhov『賭け』、B=Helen Keller、C=芥川『羅生門』、D=Livingstone、E=太宰『走れメロス』)

(1)選定Gateは機能した。前回『The Open Gate』の元候補(LOC Jane Lee Smith
インタビュー)は、今回tile.loc.govのPDFで一次テキストを実際に読めるように
なった結果、Gate1はPASSに転じたがGate3(中心Story保持)で明確にFAIL
(脈絡のない逸話集で『門を開けて母を救う』場面は原文に存在しない)。
Trial-01のLOC候補4件中3件の『story_fit_reason』が一次テキストと食い違って
いた(検索要約からの誇張/創作)ことも判明し、『一次テキスト確認不能はNG』
の方針の正しさが実データで裏付けられた。
(2)5本とも冒頭で何の話か分かり、中心事件・変化・余韻があり、280〜420語で
魅力が残っている。ゼロから創作の弱点(記憶技術収束・唐突な殺人・SFギミック)
はなし。実話系でもKeller(言語獲得の瞬間)・Livingstone(ライオン襲撃)の
ように『単一の劇的場面』を含む一次資料を選べば4/4で通り、文学だけが有利
ではない。
(3)**権利の訂正(Fable)**: Helen Keller『The Story of My Life』は1903年刊で
米国ではPublic Domainだが、著者没年1968年のため**日本の著作権(没後70年→
2038年まで)では保護期間内**。eigo-radioは日本で提供するサービスであり、
rights_check.mdの『well past copyright term』は米国基準のみで誤り。Story B
『The Word in My Hand』は必須Gate2(権利)FAILとして候補から除外し、本
Trialでは『実話系でも面白い素材を選べる』ことの例証としてのみ扱う。今後の
権利確認は『日本法(没後70年)と米国法の両方でPD』を条件にする。
(4)『走れメロス』は日本の学習者に極めて有名だが、方針(1)『忠実な再話も
許容』に従えば問題ない。ただし著名作の扱い(前回1-2)の判断次第。
(5)費用¥1.76(web_search 0回、一次テキストは直接HTTP GET)。

## §11 分類

**VALIDATED**(選定Gate+4基準は機能。Production Fiction仕様への反映は
行わない)。ユーザー判断事項:
①権利確認条件を『日本法+米国法の両方でPD(著者没後70年以上、または明確な
CC0等)』に固定するか(Fable推奨: 固定)。
②著名作(走れメロス・賢者の贈り物・首飾り等)の扱い: 忠実な再話として採用
可とするか、学習者の既知度が高い作品は避けるか(Fable推奨: 採用可。既知の
物語は英語学習では理解の助けになる)。
③次段階: 選定Gateを固定し、各系統3〜5本の素材リスト(Story未生成)を先に
作るか、生成まで進めるか(Fable推奨: 素材リスト先行、¥10程度)。
④前回Trial-01の4本のうち『The Open Gate』はGate3 FAILの素材由来として
不採用扱いでよいか(Fable推奨: 不採用)。
