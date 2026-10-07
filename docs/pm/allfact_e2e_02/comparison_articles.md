# 人間比較用: 従来版(Noteなし) vs P2版(全fact一律の多義語Note) 全文比較資料

管理ID: OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02(委任_B1)。生成日: 2026-10-07。Trial/DEV限定、Production変更なし。AIによる面白さ採点なし(人間評価用)。

## 0. 比較条件表

| 項目 | 従来版(control) | P2版 | 同一/差異 |
|---|---|---|---|
| 台帳本文(verified_fact_ledger.txt) | open233_polysemy_trial_02/ledgers/<slug>/control/ のもの。hormuz sha256=9bd6834e68e7..., sewer sha256=42faae06f7fe... | er052_output/open233_allfact_note_e2e_02/ledger/<slug>/research_ledger/ のもの。hormuz sha256=f776197fd501..., sewer sha256=6322c220f9f2...(全行diffで確認: 差は notes_for_writer 行のみ。hormuz 12行・sewer 20行。fact本文・scope・conditions・numeric_value・date等は同一) | fact本文は同一。sha256が異なるのは notes_for_writer 行のみの差(下の行) |
| runner | er019_family_x_entertainment_production_runner_01.py (sha 164d8ef6214d...)、B3 module 93d0e31e7350...、JA writer module b3b5b9ff0eb6...、--stage advanced | 同一の er019 runner(runner_argv=er019 --stage advanced、Phase1=--stop-after writer、Phase2=--stop-after advanced)をDEVラッパー er052_open233_polysemy_nb_dev_01.py(sha ad4b9244b5cd...)経由で起動。freeze_t01_config_sha256=9ce135a93ae0...(従来版と同じ) | 同一(er019 runner・freeze_t01・stage)。差異はDEVラッパー側の_TRANSFER_TEMPLATE(転記規則)のみ |
| B3/JA/EN prompt | 承認済み現行prompt(b3_prompt_sent_sha256はprovenance参照) | 同じer019 runner・同じfreeze_t01_config_sha256のため同一(promptハッシュ個別の再照合は未実施。notes_for_writerの文面が変わるのでB3 promptへ送られる台帳テキストは異なる) | 同一(prompt本体)。送信されるfact本文の notes 部分は差異 |
| Checker構成 | 承認済みCheckerスイッチdump sha256=66d18a3a1b28...(5テーマ共通) | switch_dump_sha256=66d18a3a1b28679684d7dcbe6e7af161a4da4223da7415a7ac50e7450de777c1(全P2 run共通)、switches_equal_e2e02=true(6 run全てのmanifest.json・checker_after_provenance.jsonで確認)。Checker記録model_id=gpt-6-luna(従来版と同じ) | 同一(41キー一致) |
| notes_for_writer | 台帳の従来notesのみ(Noteなし。transfer_block=null=転記規則なし) | 従来notes(各行頭に「注意: 」を付与)+ 末尾に「 / 注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。」を全factへ一律追記(P2) | 差異(本試験の操作変数) |
| 生成日時 | 2026-10-07 06:34〜06:42(記録のローカル時刻) | 2026-10-07 10:29〜10:38(provenance started_at。hormuz rep1/2=10:29 Phase1、sewer rep1=10:29/10:32、rep2=10:33/10:37) | 差異(別run) |
| DEV runnerの転記規則差分 | なし(従来版はtransfer_block_sha256=null=転記規則なし。Noteなし) | DEVラッパーの_TRANSFER_TEMPLATE新版(「notes内容全体を転記」へ最小修正済み)を使用。全P2 runで transfer_block_sha256=e3b39ded427feaedde565ac2430572c708235ae81d14fe21a6890f87c2184c79。briefへの転記確認(brief_transfer_check)は6 run全てALL_PASS(hormuz rep1 2/2、rep2 3/3、sewer rep1・rep2 4/4) | 差異 |
| seed/揺れ | LLM出力は非決定。seed固定なし。N=1(rep1) | rep1/rep2(2回)。seed固定なし | 差異(run間揺れあり。内容差がNote由来とは限らない) |
| 使用model | B3/JA/EN: gpt-5.6-luna(requested=actual、fallbackなし)。Checker記録model_id: gpt-6-luna(記録値のまま) | Checker記録model_id=gpt-6-luna(P2 provenanceで確認)。writer側modelはP2側のruntime_evidence.json参照(本資料作成時は個別再照合せず) | 同一のはず(Checker側は確認済み) |

注意: 従来版は本来「別目的のTrial_04のcontrol」として生成されたもの。条件(台帳・runner・Checker)は同一だが、生成run自体は別なので、LLMの自然な揺れは差に含まれる。

追記(2026-10-07、委任_C3): P2の最終稿はrep1の ja_writer/revision2.md と b1b/article.md を全文収録(省略なし)。b1b/article.md はChecker前の記事ファイルであり、Checker後のEN(Rewrite反映後)とは一致しない場合がある(該当する場合は各記事の下に注記)。

## 1. 比較対象2記事の選定

- 記事A: hormuz(経済・市場速報型。時系列・数値・価格推移fact中心)
- 記事B: sewer(生活インフラ・制度解説型。統計・自治体事例・保守制度中心)
- 選定理由: 速報の時系列+市場反応(方向・状態変化factあり)と、統計・制度の解説という、記事構造・トーン・fact性質が最も異なる組。候補の性質: space_weapons=安全保障(比喩の多い物語調、用語整理)、ai_control=技術政策(事件+限定の語り)。推奨外の代替案はspace_weapons+sewer、または ai_control+sewer(hormuzと同系の「事件+解釈」型の重複を避けるなら)。

## 2. 記事A: hormuz

### 2-1. 従来版 JA最終稿(revision2.md)全文

二割の償還料が、翌日には貿易カードになった

ニュースの主役が、たった一日あまりで交代しました。

七月十三日午前十時十六分、トランプ氏は、ホルムズ海峡を通るすべての貨物について、米国が安全と警備を提供するための費用として、二割の率で償還を求めると投稿しました。

ただし、ここで料金表が完成したわけではありません。示されたのは二割という率です。誰が誰に支払うのか、どう計算するのか、どの通貨で集めるのか、免除はあるのか。こうした制度の細部は示されませんでした。つまり、重い数字は出たものの、仕組みの設計図までは見えていなかったのです。

そして、およそ二十四時間四十八分後の七月十四日午前十一時四分。トランプ氏は、その二割の償還料を、湾岸諸国による対米貿易や投資の案件に置き換えると投稿しました。理由として挙げたのは、中東の指導者たちとの「非常に生産的な協議」です。

さらに記者団には、ホルムズ海峡を通る船に誰も料金を課すべきではなく、料金という考え方自体を好まないとも述べました。前日に二割を提案し、翌日には料金そのものへの距離を示す。ニュースとしては、なかなか急な方向転換です。

市場はどう反応したのでしょうか。置き換えの発表後、ブレント原油先物は上げ幅をいったん縮めました。しかし、ほどなく発表前に近い高い水準へ戻り、記事の時点では二点六パーセント高の一バレル八十五ドル超でした。

この動きから分かるのは、料金案の置き換えだけで、供給への心配が消えたわけではないということです。米国とイランの間の攻撃、海上封鎖、タンカーの安全への懸念は続いていました。

投稿の中では、償還料の案が貿易や投資の案件へ姿を変えました。けれど原油市場では、海峡をめぐる不安が画面に残り続けた。政治の言葉はくるりと変わっても、海の緊張まで同じ速さで変わるとは限らない。今回の面白さは、そこにあります。

### 2-2. 従来版 EN(b1b/article.md)全文

# The 20% Reimbursement Fee Became a Trade Card the Next Day

The main story in the news changed in just over a day.

At 10:16 a.m. on July 13, Mr. Trump posted that the United States would seek reimbursement at a rate of 20 percent for all cargo passing through the Strait of Hormuz, to cover the cost of providing safety and security.

However, this did not mean that a fee schedule was complete. What was given was the rate: 20 percent. Who would pay whom, how it would be calculated, what currency would be used to collect it, and whether some would be exempt were not explained. In other words, a large figure had appeared, but the plan for how the system would work had not.

Then, about 24 hours and 48 minutes later, at 11:04 a.m. on July 14, Mr. Trump posted that the 20 percent reimbursement fee would be replaced with trade and investment deals involving the Gulf countries and the United States. The reason he gave was “very productive talks” with leaders in the Middle East.

He also told reporters that no one should charge ships passing through the Strait of Hormuz, and that he did not like the idea of charging a fee at all. He proposed 20 percent the day before, then the next day showed that he was backing away from the fee itself. As news, this was quite a sudden change in direction.

How did the market react? After the announcement that the fee would be replaced, Brent crude oil futures temporarily gave up some of their gains. But soon they returned to a high level close to where they had been before the announcement. When this article was written, they were up 2.6 percent, at more than 85 dollars a barrel.

This movement shows that replacing the fee plan alone did not remove worries about supplies. Concerns about attacks between the United States and Iran, a blockade at sea, and the safety of tankers continued.

In the post, the reimbursement fee plan changed into trade and investment deals. But in the oil market, unease over the strait remained on the screens. Political words may change direction suddenly, but tension at sea does not always change at the same speed. That is what makes this case interesting.

## In one line
Trump replaced a proposed 20 percent fee on Hormuz shipping with trade deals the next day, but oil fears remained.

### 2-3. P2版(今回、全fact一律の多義語Note) JA最終稿(rep1 ja_writer/revision2.md)全文

海峡の請求書が、翌日には商談になった

国際ニュースには、ときどき、昨日の主役が翌日には別の姿になることがあります。今回の舞台はホルムズ海峡です。登場したのは、料金所と外交交渉という、かなり違う二つの案でした。

まず七月十三日、トランプ氏は、ホルムズ海峡を通るすべての貨物に、二十パーセントの償還料を求めると投稿しました。

償還料というのは、米国が安全を確保するために使う費用を取り戻すためのお金です。言い換えると、海峡を通る荷物に、広く同じ割合で費用を負担してもらう案です。まだ料金所ができたわけではありませんが、もし実施されれば、通る貨物すべてが対象になる大きな仕組みでした。

ここで、話は急に動きます。

翌日の七月十四日、トランプ氏は、その二十パーセントの米国償還料案を撤回しました。そして代わりに、湾岸諸国による対米貿易と投資の案件へ置き換えると投稿しました。中東の指導者たちとの「非常に生産的な協議」に基づく決定だと説明しています。

このニュースの見どころは、料金が変わったことではありません。料金を集めるという発想そのものが、別の舞台へ移ったことです。

七月十三日は、海峡を通る貨物に一律の負担を求める案でした。ところが七月十四日には、湾岸諸国との貿易や投資を進める案になりました。昨日まで荷物に付いていた二十パーセントの値札が、翌日には国どうしの商談に姿を変えたように見えます。

同じ安全確保をめぐる話でも、入り口は二つあります。貨物に直接料金をかける方法と、相手国との協議を通じて貿易や投資につなげる方法です。今回の投稿は、その切り替えが一日で起きたことを示しました。

遠い海峡の話でも、荷物を運ぶ費用は、国家どうしの取引に変わることがあります。海の上の料金所が、次の日には外交のテーブルになった。そんな急展開が、今回のニュースです。

(rep2: 全文はパスとraw URLのみ。パス=er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2/ja_writer/revision2.md。raw URL=https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2/ja_writer/revision2.md 。P2側は未commit)

### 2-4. P2版(今回) EN(rep1 b1b/article.md)全文

# The Strait’s Bill Became Business Talks the Next Day

In international news, the main story of one day sometimes takes a different form the next day. This time, the setting is the Strait of Hormuz. The two ideas at the center were a toll booth and diplomatic talks, which were quite different from each other.

First, on July 13, Trump posted that he would seek a 20 percent fee on all cargo passing through the Strait of Hormuz.

A reimbursement fee is money meant to recover what the United States spends to provide security. In other words, the plan was to have all cargo passing through the strait share the cost at the same rate. There was no toll booth yet, but if the plan had been put into effect, it would have been a large system covering every piece of cargo that passed through.

This is where things suddenly changed.

On the next day, July 14, Trump withdrew the U.S. plan for a 20 percent reimbursement fee. Instead, he posted that it would be replaced with trade and investment deals between the Gulf states and the United States. He explained that the decision was based on “very productive talks” with Middle Eastern leaders.

The key point in this news is not that the fee changed. It is that the very idea of collecting a fee moved to a different setting.

On July 13, the plan was to charge all cargo passing through the strait at the same rate. But on July 14, it became a plan to promote trade and investment with the Gulf states. The 20 percent price tag that had been attached to cargo until the day before seemed to turn into business talks between countries the next day.

Even when the issue is about providing security, there are two ways in. One is to charge cargo directly. The other is to use talks with the other country to lead to trade and investment. This post showed that the switch happened in one day.

Even when the story is about a faraway strait, the cost of moving goods can turn into a deal between countries. A toll booth at sea became a diplomatic table the next day. That sudden turn is what this news was about.

## In one line
A planned cargo fee in the Strait of Hormuz became trade and investment talks the next day.

注記(Checker後との差): この記事ファイルはChecker前。hormuz rep1のCheckerは RESOLVED_REWRITE_THEN_DOWNGRADE(3 cycle、Rewrite1件、cycle1)。Rewrite後のENでは1文だけ変わる。
- Rewrite前(上の記事ファイル): "One is to charge cargo directly."
- Rewrite後: "One is to propose a charge on cargo."
(それ以外のRewrite前後の差分は無し。Rewrite後ENの全文ファイルは er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1/checker/runs/meta_run03_advanced.json の cycles[0].en_text_after_rewrite)

(rep2: 全文はパスとraw URLのみ。パス=er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2/b1b/article.md 。raw URL=https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2/b1b/article.md 。P2側は未commit。rep2のChecker=RESOLVED_REWRITE_THEN_DOWNGRADE、2 cycle、Rewrite有=記事ファイルとRewrite後ENは一致しない(HF-002/HF-003の2文が修正。詳細はcheckerのjson参照))

## 3. 記事B: sewer

### 3-1. 従来版 JA最終稿(revision2.md)全文

下水道の引っ越し作戦　長い管から家ごとの浄化槽へ

下水道に、引っ越し作戦が持ち上がっています。引っ越すのは人ではなく、汚水を処理する仕組みです。地域によって、地下の長い管でまとめて処理する方法から、家ごとの浄化槽で処理する方法へ、主役を交代させる考え方です。

背景には、地下で働く管の高齢化があります。

全国の下水道管路は、およそ五十万キロあります。そのうち、標準耐用年数の五十年を過ぎた管路は、現在およそ七パーセントです。十年後にはおよそ二十二パーセント、二十年後にはおよそ四十五パーセントになる見込みです。

ただし、五十年を過ぎたからといって、すぐに使えなくなるわけではありません。それでも、古くなった施設の維持管理や改築更新には、より多くのお金が必要になります。国土交通省の推計では、下水道施設の維持管理と更新にかかる費用は、二〇一八年度の約〇点八兆円から、二〇四八年度には約一兆三千億円になる見込みです。

そこへ人口減少が重なります。人口が減れば、下水道使用料の収入も減ります。収入は減るのに、老朽化した施設の改築更新費は増える。下水道の経営にとって、かなり難しいパズルです。

そこで福島県喜多方市は、汚水処理の地図を見直しました。集合処理区域では、地下の管を通して汚水をまとめて処理します。一方、集合処理区域の外側は、合併処理浄化槽を使う個別処理区域にします。浄化槽の設置費には、上乗せ補助を行う方針です。

環境省も、住宅が密集する地域では公共下水道などの集合処理が、住宅が分散する地域では浄化槽などの個別処理が、経済的に有利になり得ると説明しています。地域の家の並び方に合わせて、処理方法を選ぶわけです。

合併処理浄化槽は、トイレのし尿だけでなく、台所や風呂、洗濯から出る生活雑排水も処理します。微生物の働きを利用する設備ですが、設置すれば終わりではありません。保守点検、清掃、法定検査が必要です。

つまり、これは下水道をなくす話ではありません。地下の集合処理と、家ごとの個別処理を使い分ける話です。古くなった管に向き合いながら、地域に合う仕組みへ組み替える。下水道の未来は、意外にも地図の上で決まるのかもしれません。

### 3-2. 従来版 EN(b1b/article.md)全文

# A Sewer System Move: From Long Pipes to Septic Tanks for Each Home

A move is being planned for Japan’s sewer systems. What is moving is not people, but the system that treats wastewater. Depending on the area, the idea is to shift the main role from treating wastewater together through long underground pipes to treating it in septic tanks at each home.

The reason is that the pipes working underground are growing old.

Japan’s sewer pipes total about 500,000 kilometers. Of these, about 7 percent have already passed their standard service life of 50 years. This is expected to rise to about 22 percent in ten years and about 45 percent in 20 years.

However, passing 50 years does not mean that the pipes become unusable right away. Even so, maintaining, rebuilding, and replacing old facilities will require more money. The Ministry of Land, Infrastructure, Transport and Tourism estimates that the cost of maintaining and replacing sewer facilities will rise from about 0.8 trillion yen in fiscal 2018 to about 1.3 trillion yen in fiscal 2048.

At the same time, the population is declining. When the population falls, income from sewer fees also falls. Income goes down, while the cost of rebuilding and replacing old facilities goes up. This is quite a difficult puzzle for sewer system finances.

For this reason, Kitakata City in Fukushima Prefecture reviewed its map of wastewater treatment. In areas with shared treatment, wastewater is sent through underground pipes and treated together. Outside those areas, the city will create areas for individual treatment using combined-treatment septic tanks. The city plans to provide extra subsidies for the cost of installing septic tanks.

The Ministry of the Environment also explains that shared treatment, such as public sewers, can be more economical in areas where homes are close together, while individual treatment, such as septic tanks, can be more economical where homes are spread out. In other words, the treatment method is chosen to match how homes are arranged in each area.

Combined-treatment septic tanks treat not only human waste from toilets, but also household wastewater from kitchens, baths, and washing. They use the work of microorganisms, but installing one is not the end of the process. Regular checks, cleaning, and inspections required by law are necessary.

In other words, this is not a plan to get rid of sewers. It is a plan to use shared treatment underground and individual treatment at each home in different ways. As communities deal with aging pipes, they are changing to systems that fit their areas. The future of sewers may, surprisingly, be decided on a map.

## In one line
As Japan’s sewer pipes age, some areas may shift from shared treatment to septic tanks at individual homes.

### 3-3. P2版(今回、全fact一律の多義語Note) JA最終稿(rep1 ja_writer/revision2.md)全文

汚水の町には、二つのチームがいる

汚水の世界には、二つの選手がいます。ひとつは、家々を地下の管でつなぎ、まとめて処理する集合処理。もうひとつは、家の近くで働く合併処理浄化槽です。

ここで大事なのは、どちらが強いかを決めることではありません。町の形に合わせて、出場する選手を選ぶことです。

住宅が密集する地域では、公共下水道のような集合処理が経済的に有利になり得ます。一方で、住宅が分散する地域では、家ごとに設置する浄化槽が有利になり得ます。合併処理浄化槽は、トイレの水だけを扱う設備ではありません。台所や風呂、洗濯の水も受け止め、微生物の働きを利用して処理します。小さな施設ですが、仕事は一人前です。

この方式選びを実際に見直したのが、喜多方市です。市は、施設の老朽化にともなって更新などの維持管理費が増えること、人口減少によって使用料収入が減ることを踏まえ、汚水処理構想を見直しました。

その結果、集合処理区域以外を、合併処理浄化槽による個別処理区域としました。浄化槽の設置費には、上乗せ補助も実施するとしています。地下の管で全員をつなぐ作戦から、地域によっては家ごとに処理する作戦へ。町の形に合わせて、汚水のルートを組み替えたわけです。

ただ、全国の地下では、別の時計も動いています。下水道管路の総延長は、令和六年度末の時点で約五十万キロ。そのうち、標準耐用年数の五十年を過ぎた管路は約四万キロ、約七パーセントです。

国土交通省の推計では、十年後には約十一万キロ、約二十二パーセントに増え、二十年後には約二十三万キロ、約四十五パーセントになる見込みです。五十年を過ぎたからといって、すぐ使えなくなるわけではありません。それでも、人口減少で収入が減り、古い施設の更新費が増えることは、下水道事業を厳しくする要因になります。

つまりこれは、管を直すだけの話ではありません。町に合う仕組みを選び、地下の大チームと家のそばの小チームを、うまく配置する話なのです。

(rep2: 全文はパスとraw URLのみ。パス=er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2/ja_writer/revision2.md 。raw URL=https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2/ja_writer/revision2.md 。P2側は未commit)

### 3-4. P2版(今回) EN(rep1 b1b/article.md)全文

# Two Teams for a Town’s Wastewater

In the world of wastewater, there are two players. One is collective treatment, which connects homes with underground pipes and treats the wastewater together. The other is combined-treatment septic tanks that work near each home.

The important thing here is not deciding which one is stronger. It is choosing which player will take part based on the shape of the town.

In areas where homes are close together, collective treatment, such as a public sewer system, can be more economical. In areas where homes are spread out, septic tanks installed at each home may be better. Combined-treatment septic tanks do not handle only toilet water. They also take in water from kitchens, baths, and laundry, and treat it using the work of microorganisms. They are small facilities, but they do a full job.

Kitakata City actually reviewed this choice of system. As its facilities grew older, the costs of maintenance, including renewal, were rising. At the same time, a falling population was reducing revenue from user fees. Based on these facts, the city reviewed its wastewater treatment plan.

As a result, areas outside the collective-treatment area were designated as individual-treatment areas using combined-treatment septic tanks. The city also plans to provide extra subsidies for the installation costs of septic tanks. The strategy is changing from connecting everyone with underground pipes to treating wastewater at each home in some areas. In other words, the city rearranged its wastewater routes to fit the shape of the town.

But under the ground across Japan, another clock is also running. The total length of sewer pipes was about 500,000 kilometers at the end of fiscal 2024. Of that total, about 40,000 kilometers, or about 7 percent, had passed the standard service life of 50 years.

According to an estimate by the Ministry of Land, Infrastructure, Transport and Tourism, that figure is expected to grow to about 110,000 kilometers, or about 22 percent, in ten years. In 20 years, it is expected to reach about 230,000 kilometers, or about 45 percent. Pipes do not become unusable as soon as they pass 50 years. Even so, falling revenue caused by population decline and rising costs to renew old facilities make sewerage services more difficult to run.

In other words, this is not only about repairing pipes. It is about choosing a system that fits the town and placing the large team underground and the small teams near homes in the right way.

## In one line
Towns are rethinking wastewater treatment by matching shared sewers and household septic tanks to local conditions.

注記(Checker後との差): sewer rep1のCheckerは RESOLVED_STAGE2_DOWNGRADE(1 cycle、Rewrite無)のため、記事ファイル=Checker後のEN(差なし)。

(rep2: 全文はパスとraw URLのみ。パス=er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2/b1b/article.md 。raw URL=https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2/b1b/article.md 。P2側は未commit。rep2のChecker=RESOLVED_STAGE2_DOWNGRADE、1 cycle、Rewrite無=記事ファイルとChecker後は一致)

## 4. raw.githubusercontent.com URL(計8点: 記事A/B × 従来版/P2版 × JA/EN)

従来版4点: origin/mainにtracked済み(今すぐ有効)。P2版4点: 未commitのため「次のcommit(push)後に有効」(それまではraw URLは404)。

従来版(Noteなし):
- A hormuz JA最終稿(従来版): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/hormuz/control/rep1/ja_writer/revision2.md
- A hormuz EN(従来版): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/hormuz/control/rep1/b1b/article.md
- B sewer JA最終稿(従来版): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/sewer/control/rep1/ja_writer/revision2.md
- B sewer EN(従来版): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_polysemy_trial_04/runs/sewer/control/rep1/b1b/article.md

P2版 rep1(今回、全fact一律の多義語Note。次のcommit後に有効):
- A hormuz JA最終稿(P2 rep1): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1/ja_writer/revision2.md
- A hormuz EN(P2 rep1): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1/b1b/article.md
- B sewer JA最終稿(P2 rep1): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1/ja_writer/revision2.md
- B sewer EN(P2 rep1): https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1/b1b/article.md

P2版 rep2(参考、同じく次のcommit後に有効): 上記rep1のURLの「rep1」を「rep2」に置換したもの(hormuz/sewerのja_writer/revision2.md・b1b/article.md)。

注: b1b/article.md はChecker前の記事ファイル。hormuz rep1(P2)のみ、Rewrite後ENは1文異なる(2-4節の注記参照)。

## 5. 従来版インベントリ(5テーマ、すべて control/rep1、dir=er052_output/open233_polysemy_trial_04/runs/<slug>/control/rep1/)

| slug | JA R0/R1/R2 | EN | Checker結果 | final_state(cycle数) | 台帳sha256(先頭12) | 総費用(円) | 生成完了 |
|---|---|---|---|---|---|---|---|
| meta | あり | あり | あり | RESOLVED_REWRITE_THEN_DOWNGRADE(2、Rewrite1件) | ea0ce587e605 | 5.53 | 06:42 |
| hormuz | あり | あり | あり | RESOLVED_STAGE2_DOWNGRADE(1) | 9bd6834e68e7 | 5.803 | 06:42 |
| space_weapons | あり | あり | あり | RESOLVED_REWRITE_THEN_DOWNGRADE(3、Rewrite1件) | f172a253f24b | 5.381 | 06:42 |
| sewer | あり | あり | あり | RESOLVED_STAGE2_DOWNGRADE(1) | 42faae06f7fe | 7.547 | 06:42 |
| ai_control | あり | あり | あり | RESOLVED_STAGE2_DOWNGRADE(1) | 256c67216607 | 5.146 | 06:41 |

共通: freeze_t01_config_sha256=9ce135a93ae0...、runner sha=164d8ef6214d...、Checker switch dump sha256=66d18a3a1b28...(5件一致、approved_switches_dump_after_p01.json)、使用model gpt-5.6-luna(fallback検出なし)、transfer_block_sha256=null(Noteなし)。ファイル: ja_writer/{original,revision1,revision2}.md、b1b/article.md、checker/runs/meta_run03_advanced.json、nb_provenance_phase{1,2}.json、entry_point.json。

不整合・注意点:
1. Checker結果jsonのinstance_id/group/expected_group_labelは全slugで「meta_run03_advanced / meta / Normal群」(ラベル流用、内容はslug別。評価時にslugを取り違えない)。
2. Checker provenanceのledger_sha256(例 hormuz 83b2a09b...)は台帳txtのsha256(9bd6834e...)と一致しない(ハッシュ対象が異なる可能性。未調査)。
3. Checker記録model_idは gpt-6-luna、writer側は gpt-5.6-luna(記録値のまま転記。同一モデル表記ゆれか別名か未確認)。
4. 必須修正(must_fix)の発動段階はslugで異なる(meta=JA R0後、hormuz/sewer/ai_control=JA R2後、space_weaponsは発動なし)。
5. Checkerのfinal_stateは全件「RESOLVED_*」。ただしDOWNGRADE経由のため、最終記事にACCEPTABLE扱い指摘が残る(non_blocking 1〜22件。ai_control 22・sewer 16)。評価で妥当性を確認すること。
