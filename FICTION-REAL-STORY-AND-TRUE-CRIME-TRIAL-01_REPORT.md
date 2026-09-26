# FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 REPORT

Status: **完走(3-A Real Story 1本 + 3-B Historical True Crime 1本、Sonnet仮分類
VALIDATED、詳細は§6)**。Trial専用、未承認draft実装。Production Fiction仕様への
反映は本タスクの対象外。到達上限VALIDATED。TTS/音声は使用していない(TTS call 0)。

## §1 目的

`FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02`(VALIDATED)で生成した
Real Story「The Lion That Rose Again」(David Livingstone実話)について、
ユーザー評価は「悪くはないが、文学作品群(羅生門・走れメロス・賢者の贈り物系)
と比較すると弱い」というものだった。Real Story 1本だけでは判断材料が不足する
ため、本Trialでは(3-A)別のReal Story(実話・回想録・探検記等)を1本、
(3-B)委任文で新規に指定されたHistorical True Crime(1930年以前の歴史的犯罪
記録)を1本、それぞれ選定してStoryまで作成した。選定GateはTrial-02の基準
(G1一次テキスト直接HTTP GET確認/G2日本+米国双方の権利確認/G3短編化可能/
G4 Story品質4基準A中心事件・B読者関心・C変化・D短編化適性)をそのまま流用した。

## §2 Gate運用(Trial-02から変更なし)

必須Gate:
1. 一次テキストを実際にHTTP GETで直接取得・確認(検索結果要約だけで選ばない)。
2. 日本+米国双方の権利条件確認(日本: 著者没後70年経過、原則没年明記。米国:
   1931年以前公表またはPD根拠明記。米国PDだが日本で未PDの候補は除外)。
3. 短編化可能(280-420語)。

Story品質4基準(3以上でPASS): A中心となる事件、B読者の関心、C意味のある変化、
D短編化適性。

True Crime(3-B)固有の追加条件: 1930年以前の事件・史料(現代事件は対象外)、
事実(日付・人物名・経緯)を勝手に改変しない、資料にない動機・台詞・心理描写を
創作しない(または創作箇所を明示して最小限)、センセーショナル化・過度な残虐
描写を避けつつ、事件の面白さを消すほど無難にもしない。

## §3 Real Story(3-A)

### 候補表(全文は`er018_output/fiction_real_story_and_true_crime_trial_01/candidates_real.md`)

| 候補 | Gate1 | Gate2(日/米) | Gate3 | G4 PASS数 | 判定 |
|---|---|---|---|---|---|
| **Nellie Bly, "Ten Days in a Mad-House"(1887)** | PASS(HTTP 200・全文確認) | PASS(没1922→日1992満了/米PD) | PASS | **4/4** | **採用** |
| Ernest Shackleton, *South* Ch.X「Across South Georgia」(1919) | PASS | PASS(没1922→日1992満了/米PD) | PASS | 4/4 | 採用可能(今回非選択、Livingstoneと同系統の肉体的サバイバル譚のため新鮮味を優先しBlyを選択) |
| Isabella Bird, *Unbeaten Tracks in Japan*(1880) | PASS(複数箇所読了、全数照合ではない) | PASS(没1904→日1974満了/米PD) | 中間〜FAIL(単一中心事件が薄い書簡体紀行文) | 0-2/4 | 非採用 |

### 選定理由

Nellie Blyの潜入取材譚は、Livingstoneの動物襲撃サバイバル譚とジャンルが異なり
(投獄詐術・社会正義・皮肉な逆説)、「正気を訴えるほど狂気の証拠とみなされる」
という明確な中心的転換を持つ。G1-G4すべてPASS(4/4)。

### 一次資料URL・権利根拠

- URL: https://www.gutenberg.org/ebooks/59899.txt.utf-8(HTTP 200)
- 著者: Elizabeth Cochrane Seaman(pen name Nellie Bly)、1864年5月5日-1922年1月
  27日没(Wikipedia確認)。日本: 没後1922+70=1992年で著作権満了。米国: Project
  Gutenberg #59899の権利表示でPublic domain確認(原著1887年刊、1931年より
  大幅に前)。

### Story全文(388語、`real_story/story.md`)

```
### Ten Days Inside

The night before my assignment, I stood alone in my room and practiced looking insane.

I opened my eyes very wide. I shook my head. I spoke in a strange voice. Then I stopped and looked at myself in the mirror.

"What if the doctors believe me?" I whispered. "What if they do not let me out?"

The newspaper editor had given me a dangerous job. I had to enter an asylum for women and write about what happened inside. To enter, I had to make people think I was ill.

The next morning, I went to a place where a judge and several doctors questioned me. I tried to look confused and afraid. They asked only a few questions.

"Do you know where you are?" one doctor asked.

"Yes," I said.

The judge looked at the doctors. They spoke quietly together. Soon, they decided that I was insane. No one carefully checked my story. No one asked my family or searched for proof.

A carriage took me to the asylum. The gate closed behind me with a hard sound.

Inside, I stopped acting. I spoke normally. I told the doctors that I was a reporter and that I did not need help.

They only smiled.

"You believe you are a reporter," one doctor said. "That is another sign of your illness."

I began to understand the danger. If I acted strangely, they would call me insane. If I acted normally, they would call me insane. There was no safe answer.

The women lived in cold rooms. The food was small and often bad. One morning, a nurse pushed a woman into a cold bath. The woman cried and begged her to stop. Another nurse laughed at her.

I wanted to fight, but I knew I might never leave.

For ten days, I watched and remembered everything. Then the newspaper editor arranged my release.

Outside the gate, I felt deep relief. But I also felt sad. I was leaving women who had no one to speak for them.

When my story appeared in the newspaper, people were shocked. Officials began to watch the asylum more closely, and conditions improved.

I had entered to pretend to be insane. The frightening truth was that, inside, speaking the truth was not enough to prove I was sane.
```

### 忠実性

保持: 夜間の鏡の前での練習、判事・医師による粗雑な審問、施設内で正気に振る舞う
ほど疑われるという中心的皮肉(原文Ch.XVIの逐語的裏付けあり)、劣悪な環境の実例、
10日後の釈放と残していく女性たちへの悲哀、報道後の監督強化という結末。
簡略化: 実名(編集者・判事・医師・看護人・他の患者)はすべて役割名に置換
(Fiction家族の既定命名規則、主人公Nellieのみ固有名)。詳細は
`fidelity_real.md`参照。

## §4 Historical True Crime(3-B)

### 方法論上の注記

委任文が例示した`chroniclingamerica.loc.gov`/`www.loc.gov`検索エンドポイント
は、本Trial実行時点でCloudflareチャレンジ(HTTP 403相当・JS実行必須)により
直接HTTP GETでの検索・取得ができなかった。代替として委任文が明示した
「Public Domainのhistorical crime collections(例: The Newgate Calendar等)」
の経路を採用し、Project Gutenberg上のCamden Pelham『The Chronicles of Crime;
or, The New Newgate Calendar』(1841年、vol.1、#46585)から3件を検討した。

### 候補表(全文は`candidates_true_crime.md`)

| 候補 | Gate1 | Gate2(日/米) | Gate3 | 判定 |
|---|---|---|---|---|
| **Eugene Aram事件(1745年殺人〜1759年処刑)** | PASS(全文確認) | PASS(Pelham1841年刊、pseud、公表後70年で日本PD満了/米国PD) | PASS | **採用** |
| Jonathan Bradford(誤判・冤罪処刑事件) | PASS(取得済みだが編纂者自身が「信頼できる詳細が集められなかった」と明記) | PASS | **FAIL**(情報量が薄すぎ、創作なしに280-420語を構成不可) | 非採用 |
| Mary Blandy(1752年、実父毒殺) | PASS | PASS | PASS(4/4) | 採用可能(今回非選択、家族毒殺というテーマの重さとAramの知的興味を比較しAramを優先) |

著者「Camden Pelham」はpseudonymであることをLibrary of Congress Name
Authority(`id.loc.gov`、Cloudflare非対象)で確認。日本の著作権法は無名・
変名著作物を公表後70年としており、1841年公表から70年(1911年)は遥かに経過
済みのため、没年不明でも日本PDは明確。

### 一次資料URL・権利根拠

- URL: https://www.gutenberg.org/ebooks/46585.txt.utf-8(HTTP 200)
- 著者: Camden Pelham(pseud)、1841年出版。日本: 公表後70年(1911年)で満了。
  米国: Project Gutenberg #46585の権利表示でPublic domain確認。

### Story全文(284語、`true_crime/story.md`)

```
## The Bones at St. Robert's Cave

Eugene Aram and Richard Houseman murdered Daniel Clarke. They had persuaded Clarke to go out at night with them. They said they wanted to discuss silver and jewels. After that night, Clarke disappeared.

For fourteen years, Aram continued to live a respectable life. He worked as a teacher. The murder was not solved, and there was no body to prove what had happened. Aram's public life gave no clear sign of the crime.

Then a labourer found human bones at St. Robert's Cave near Knaresborough. This discovery changed the case. The bones could be connected to the missing man, so people questioned Richard Houseman.

Houseman panicked when he was questioned. He then confessed and gave information about another burial site. His information led people to a second place where evidence of the crime could be found. The case now returned to Eugene Aram, who was arrested.

At his trial, Aram gave an eloquent defence. He spoke in a learned and careful way. His defence was strong in words. But the physical evidence was stronger. The bones and Houseman's confession gave the jury a clear answer. The jury was convinced quickly, and Aram was found guilty.

Aram's public defence was not the end of the story. Before he was executed, he privately admitted his guilt. He was executed at York on 16 August 1759.

For fourteen years, Eugene Aram had continued as a teacher while Daniel Clarke's fate remained hidden. Then a labourer found bones in a cave. Houseman's confession led to a second burial site, and the evidence finally broke through Aram's respectable public life. A missing man had left almost no answer -- until the ground gave one.
```

### 忠実性(照合表は`fidelity_true_crime.md`)

実在の人物名(Eugene Aram/Richard Houseman/Daniel Clarke)・日付(1745年2月8日、
1758年発見、1759年8月16日処刑)・経緯(潜伏14年、労働者による白骨の偶然発見、
Housemanの動揺と自白、雄弁だが失敗する法廷弁論)はすべて資料どおり保持した。
資料にない動機・台詞・心理描写の創作はしていない。省略した要素(法廷弁論全文、
処刑前夜の自殺未遂、遺体を鎖に吊るした事後処理)は「委任文の残虐描写回避」に
よる尺調整の省略であり、事実の書き換えではない。

**命名規則の逸脱(要ユーザー/Fable判断)**: True CrimeはFiction家族の既定命名
規則(主人公のみ固有名、他は役割名)を適用せず、実在人物の実名をすべて保持した
(委任文3-Bの「事実を勝手に改変しない」を優先)。これはSonnetが独自判断で
Fiction家族全体のルールを変更したものではなく、True Crimeという新カテゴリに
限定した意図的な逸脱である。今後True Crimeを継続する場合、この命名例外を
正式にSSOT化するかはユーザー判断が必要。

## §5 QCD

- **実行**: Seed化2 call + Story生成2 call + 品質判断による手動再生成1 call
  (true_crime、1回目271語・末尾反復のため同一prompt/model/effortで再生成) =
  Luna API call合計5回、すべて技術的に成功。
- **一次テキスト調査**: すべて直接HTTP GET(`requests`)、web_search呼び出し
  **0回・$0**。候補発見の補助にWikipedia API(著者没年・刊行年確認、
  検索エンジンではなく百科事典APIへの直接HTTP GET)、および
  `id.loc.gov`(Cloudflare非対象)を著者典拠確認にのみ使用。
  `chroniclingamerica.loc.gov`/`www.loc.gov`検索エンドポイントはCloudflare
  403で利用不可だった(詳細は§4方法論注記、`runtime_evidence.json`)。
- **費用**: 累計**$0.007988(約¥1.28)**。委任文の実測見込み(¥40-90)を
  大幅に下回った(web_search不使用のため)。上限¥200(Guardrail)に対し
  1.28/200 = 約0.6%。`cost.json`: `{"total_usd": 0.007988, "total_jpy": 1.28,
  "record_count": 5, "web_search_call_total": 0}`。
- **語数**: Real Story 388語、True Crime 284語(いずれも280-420語の範囲内)。
- **オフラインテスト**: `er018_fiction_real_story_and_true_crime_trial_01_test_01.py`
  (SEEDS構造検証・語数Gate判定関数・True Crime実名テンプレート分岐の5テスト)
  すべてPASS(API呼び出しなし)。
- **check_delegation_prompt.py**: `docs/pm/ACTIVE_TASK_FRC.md`に対し実行、
  status=FAIL(WARN扱いで記録)。本委任文はDELEGATION_STANDARD_TEMPLATE.md
  の固定ラベル(E-1/D-1/G-1/F-1)形式ではなく、Fable-PM独自の自由記述形式
  (管理ID+固定ルール+前提+3-A/3-B+成果物+RESULT_PACKET見出し)で書かれて
  いたため、ツールの必須キーワード検出(事前指定Read一覧・Grep一覧・実行
  コマンド全文セクション等)が該当せずFAILと判定された。委任文自体の内容は
  具体的かつ実行可能であり(URL・budget・成果物パスがすべて明記)、
  実質的な委任文の質の問題ではなくテンプレート形式不一致によるものと判断
  し、そのまま作業を継続した。詳細はRESULT_PACKET_FRC.md参照。

## §6 Sonnet仮分類

**VALIDATED**(委任文が定める到達上限)。3-A(Real Story追加1本)・3-B
(Historical True Crime 1本)ともにGate G1-G4(True CrimeはG1-G3+固有条件)を
満たす候補を複数比較のうえ選定し、Story生成・忠実性照合・一次資料保存まで
完走した。True Crimeにおける命名規則の意図的逸脱(§4)はProduction仕様への
反映ではなく、Trial限定の記録として明示している。Production Fiction仕様への
反映(`APPROVED_FOR_PRODUCTION`)は人間ユーザーの判断を要する。

## §7 Fable評価

(空欄、Fable記入待ち)

## §8 分類

(空欄、Fable記入待ち)
