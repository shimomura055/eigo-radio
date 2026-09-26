# FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 REPORT

Status: **完走(3-A Real Story 1本 + 3-B Historical True Crime 1本、Sonnet仮分類
VALIDATED、詳細は§6)**。Trial専用、未承認draft実装。Production Fiction仕様への
反映は本タスクの対象外。到達上限VALIDATED。TTS/音声は使用していない(TTS call 0)。
**True Crime(3-B)はFable差し戻し(修正1回目)を受け改訂済み(284語→334語、
§4参照)。Real Story(3-A)は修正1回目の対象外であり不変。**

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

### Story全文(改訂版、334語、`true_crime/story.md`)

**改訂履歴**: attempt1(271語)→attempt2(284語、Fable初回レビューで却下。指摘:
「事件の面白さを消すほど無難」「最終段落が全体の再要約」)→Fable差し戻し
(修正1回目)を受けattempt3-9で試行錯誤(263/350[日付欠落]/259/288/245/259/292語、
いずれもSeed側の指示強化の途中経過。破棄せず`stories/true_crime_eugene_aram/
story_attempt{1..9}_*.md`に保存)→**attempt10(334語)を採用**。旧版284語は
`true_crime/story_attempt2_284w.md`に保存(破棄していない)。

改訂で反映したFable指摘3点: (1) Housemanが骨を手渡され叫んだ資料の逐語台詞
"This is no more Daniel Clarke's bone than it is mine!"と、それがなぜ疑いを
招いたか(Clarkeの骨でないとどうして分かるのか)、および「頭はさらに右」という
具体的埋葬地点の指示に従って掘ると指示どおりの位置から第二の骨格が出たこと、を
本文に明示。(2) 末尾を全体の再要約ではなく、執行の事実+短い結びに変更。
(3) 語数を280-420語の下限付近(284語)から300-400語目標の範囲内(334語)へ。

```
### The Second Skeleton

In the eighteenth century, in England, Daniel Clarke had silver and jewels. Eugene Aram and Richard Houseman persuaded him to walk out at night to discuss how to dispose of them. On that night, Aram and Houseman murdered Clarke.

At first, no one knew what had happened. People believed Clarke had disappeared. Eugene Aram, however, remained apparently respectable. He worked as a teacher. Fourteen years passed, and the missing man was still believed to be gone.

Then, near St. Robert's Cave, a labourer was digging for stone. He accidentally found a human skeleton. A coroner's inquest began. This was an official investigation into a death. Soon, suspicion fell on Aram and Houseman.

At the inquest, nobody could yet say that the first skeleton was Clarke. The discovery gave no clear name to the dead person. It only made the old disappearance seem connected to the two men.

During the inquiry, Richard Houseman was asked to handle a bone. He exclaimed, "This is no more Daniel Clarke's bone than it is mine!" His words made people suspicious. How could Houseman know it was not Clarke's bone? They wondered if he had seen the real bones before.

The first skeleton did not answer the main question. Was it Clarke? The people needed more evidence. Houseman's answer suggested that he knew more than he should. His strange certainty turned attention to the place where Clarke might really be buried.

Houseman later confessed. His confession identified the true burial place. Clarke's head was a little farther to the right than the first skeleton. Men dug there. They found a second skeleton exactly where Houseman said it was.

Eugene Aram was arrested and brought to trial. He wrote an eloquent written defence. It did not save him. He was quickly convicted. In private, he confessed his guilt to clergymen.

On 16 August 1759, Eugene Aram was executed at York. The ground had kept its secret for fourteen years. Then Houseman's strange words helped uncover it.
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

- **実行(初回)**: Seed化2 call + Story生成2 call + 品質判断による手動再生成1 call
  (true_crime、1回目271語・末尾反復のため同一prompt/model/effortで再生成) =
  Luna API call合計5回、すべて技術的に成功。
- **実行(Fable差し戻し・修正1回目)**: True Crime(Eugene Aram)のみ対象、
  Real Story(Nellie Bly)は再生成していない(`--only-key true_crime_eugene_aram`
  を追加し限定実行、`stories_all.md`のNellie Bly節が不変であることを確認済み)。
  Seed側(source_brief/conversion_plan)へ(1)Housemanの逐語台詞と疑いの因果関係、
  (2)具体的埋葬地点一致の詳細、(3)末尾反復禁止、(4)300-400語の目標、を段階的に
  強化する指示を追加しながらSeed化4回+Story生成8回(263/350[日付欠落を検知し
  さらに指示追加]/259/288/245/259/292/334語、最終334語を採用)を実行。すべて
  技術的に成功、全試行を破棄せず保存。
- **一次テキスト調査**: すべて直接HTTP GET(`requests`)、web_search呼び出し
  **0回・$0**。候補発見の補助にWikipedia API(著者没年・刊行年確認、
  検索エンジンではなく百科事典APIへの直接HTTP GET)、および
  `id.loc.gov`(Cloudflare非対象)を著者典拠確認にのみ使用。
  `chroniclingamerica.loc.gov`/`www.loc.gov`検索エンドポイントはCloudflare
  403で利用不可だった(詳細は§4方法論注記、`runtime_evidence.json`)。
- **費用**: 累計**$0.034513(約¥5.52)**(初回¥1.28+修正1回目の追加分約¥4.24)。
  修正1回目のGuardrail上限¥10に対し約55%。`cost.json`:
  `{"total_usd": 0.034513, "total_jpy": 5.52, "record_count": 17,
  "web_search_call_total": 0}`。
- **語数**: Real Story 388語(不変)、True Crime 334語(300-400語の目標範囲内、
  280-420語のGate範囲内)。
- **オフラインテスト**: `er018_fiction_real_story_and_true_crime_trial_01_test_01.py`
  (SEEDS構造検証・語数Gate判定関数・True Crime実名テンプレート分岐の5テスト)
  すべてPASS(API呼び出しなし、修正後のスクリプトに対して再実行済み)。
- **check_delegation_prompt.py**: `docs/pm/ACTIVE_TASK_FRC.md`に対し実行、
  status=FAIL(WARN扱いで記録、初回delegationと同じ理由)。本委任文は
  DELEGATION_STANDARD_TEMPLATE.mdの固定ラベル(E-1/D-1/G-1/F-1)形式ではなく、
  Fable-PM独自の自由記述形式で書かれているため、ツールの必須キーワード検出が
  該当せずFAILと判定された。修正1回目の差し戻し文も同様の自由記述形式で
  あったため同じくFAILだったが、内容自体は具体的かつ実行可能であり、実質的な
  委任文の質の問題ではないと判断しそのまま作業を継続した。詳細は
  RESULT_PACKET_FRC.md参照。

## §6 Sonnet仮分類

**VALIDATED**(委任文が定める到達上限)。3-A(Real Story追加1本)・3-B
(Historical True Crime 1本)ともにGate G1-G4(True CrimeはG1-G3+固有条件)を
満たす候補を複数比較のうえ選定し、Story生成・忠実性照合・一次資料保存まで
完走した。True Crimeにおける命名規則の意図的逸脱(§4)はProduction仕様への
反映ではなく、Trial限定の記録として明示している。Production Fiction仕様への
反映(`APPROVED_FOR_PRODUCTION`)は人間ユーザーの判断を要する。

## §7 Fable評価

(1) 選定Gate: Real Story(Nellie Bly "Ten Days in a Mad-House"、1887、著者1922年没→日本PD 1992年満了・米国PD)/True Crime(Eugene Aram事件、Camden Pelham "The Chronicles of Crime" 1841、筆名・1841年刊→日本PD公表後70年・米国PD)とも一次テキストをHTTP GETで直接確認(Gutenberg #59899/#46585)、日本+米国の権利根拠が明記されており、Trial-02のGate(一次テキスト・権利・短編化・4基準)を満たす。web_search 0回・費用合計¥5.52。(2) Real Story: 388語、原文Ch.XVIの中心的皮肉(正気を訴えるほど疑われる)を保持、忠実性表あり。編集者・医師・看護人は役割名(改名ではなく省略)で、人物名の無意味な変更はない。(3) True Crime: 初版(284語)はFableのEditorial Gateで差し戻し(核心ディテール[Housemanの一言"This is no more Daniel Clarke's bone than it is mine!"と指示どおりの場所からの第2骨格]の平板化、末尾の再要約、語数下限ぎりぎり)。修正版(334語、attempt10)はこの3点を解消し、実名・日付・経緯は資料どおり、創作台詞・動機なし。ただし第4段落と第6段落(「第1の骨格がClarkeとは断定できない」)がやや重複しており、Storytellingとしては引き締め余地がある(Fable所見、事実には影響なし)。(4) 語数の不安定性: True Crime再生成でLunaの出力語数が245〜350語でばらつき、Seed指示を4段階強化して300語超に到達(試行10回、全て保存)。True Crime系Seedは語数下限の指示を最初から強く入れる必要がある(運用所見)。(5) 命名規則: True Crimeでは「事実改変なし」を優先し実名を全保持(Fiction家族の「主人公のみ固有名」規則からの意図的逸脱)。正式化はユーザー判断。(6) Chronicling America/loc.gov検索エンドポイントはCloudflare 403でHTTP GET不可。代替(Newgate Calendar系PDコレクション)を使用。

## §8 分類

**VALIDATED**(Trial範囲。Production Fiction仕様への反映ではない。Story品質の最終判断はユーザー試読)。ユーザー判断事項: F-1 Real Story「Ten Days Inside」(Nellie Bly)の試読評価(Livingstone比)。F-2 True Crime「The Second Skeleton」(Eugene Aram)の試読評価。F-3 True Crimeにおける実名全保持を、Fiction家族命名規則(主人公のみ固有名)の正式な例外として記録するか(Fable推奨: 記録する。理由: 「事実を勝手に改変しない」条件と両立するのは実名保持のみ)。F-4 Chronicling Americaが直接取得不可の場合、Newgate Calendar系等のPD犯罪記録集を正規の代替Sourceとして認めるか(Fable推奨: 認める。ただしLOC APIの別経路[loc.gov JSON API等]を次回Trialで再試行)。
