# LANE_B_EUROPE_ASIA_CIVIC_01(FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 委任_01b / Lane b)

作成・確認日: 2026-10-29(JST。以下の「確認日」はすべて同日)。調査のみ。LLM API 0・費用0円・Production変更なし。
**本書の登録は「情報源・テーマ候補の記録」であり、Production継続利用の承認ではない。新サイト・新収集方式のProduction採用はユーザー判断待ち**(ユーザー原文§8)。`APPROVED_FOR_PRODUCTION`は人間ユーザーのみ。
範囲外(01a=英語圏Debate、01c=国内)のサイトは調べず、§5に名前だけ記録した。SOURCE_REGISTRY_01.md・SSOT・ACTIVE_TASKは編集していない(統合は委任_02)。

## 0. 先に結論(Fable向け3行)

1. **商用利用が明文で許容されている(◎)足を5つ確認**(Polisオープンデータ=CC BY 4.0 / 仏Grand Débat=Licence Ouverte 2.0 / 英国議会請願+Hansard=OGL v3.0・Open Parliament Licence / Climate Assembly UK=OGL v3.0 / Global Voices=CC BY 3.0)、○1(The Conversation=CC BY-ND 4.0)。いずれも「実在の発言を読み、論点・立場を参考に独自の3 Personaを作る」用途に明示の禁止は無い(法的保証ではない)。
2. 一方、**Family Y適性は◎なし(○1・△5。サイト単位)**。ライセンスが明確なサイトは「匿名の短文」「議員の演説」「専門家記事」で、掲示板のような人物の具体性が薄い。論点・対立軸の発掘(Debate系の役割)には強いが、Personaの肉付け(体験談系)は別の足が要る。**実際に確認した3立場がそろったテーマは4件(TH-B1〜B4)、弱い参考2件(B5・B6)**。
3. 欧州の「会話型」討論・フォーラム系の大半は、AI botのrobots拒否・TDM(テキスト・データマイニング)禁止・会員制・Cloudflare遮断のいずれかで**除外または未確認**(§3、19件)。禁止・未確認サイトで数を補っていない。

## 1. 探索方法・範囲

- 取得方法: 規約・robots.txt・討論ページ・公式オープンデータの**単発の手動閲覧相当のcurl**(1リクエスト1.5秒以上の間隔、クロール・ログイン・一括収集なし、LLM API呼出なし)。User-Agentは一般的なデスクトップブラウザ表記。Cloudflare等でHTTP 403/チャレンジの出たページは回避せず「アクセス遮断(未確認)」と記録した。**例外の開示**: Hansardの1ページ(請願700086の討論)は最初のcurlがCloudflareの"Just a moment"(403)となったため、20秒待って、先に成功していた同じ取得ツールで1回だけ再取得し200を得た(回避策は使っていない。URLの大小文字とAccept-Languageヘッダが違っていた)。
- 公式オープンデータの取得: ①GitHub `compdemocracy/openData` の`comments.csv`×12(各5KB〜1.3MB。CC BY 4.0の配布物)。②data.gouv.frの「Données ouvertes du Grand Débat National」から**最大級の64MBのCSVの先頭700KBのみ**をRange指定で取得(配布物。全量取得はしていない)。③UK Parliament請願のJSON×3(`petitions/<id>.json`、公開JSON)。
- 言語: 独語・仏語・中国語(繁体)は**agent自身が原文を読んで**日本語要旨にした(外部翻訳API不使用。引用の日本語訳は「agent訳」)。
- 既存成果の再利用: `SOURCE_REGISTRY_01.md`等を先に読み、既判定(Reddit=ユーザー決定で対象外、発言小町=除外、HN=未確認、Guardian/Mumsnet=利用不可、SE=補助のみ)は**再調査していない**。
- 発掘対象: Debating Europeを出発点に、市民パネル(EU・アイルランド・英)、熟議プラットフォーム(Polis/vTaiwan・Decidim・Make.org)、市民討論の公開データ(仏Grand Débat)、議会請願・討論(英)、欧州・アジアのメディア・フォーラム(ZEIT・Perspective Daily・gutefrage・Doctissimo・Carers UK・Munk・Naver・Zhihu・Straits Times・Rappler)、CC系メディア(Global Voices・The Conversation・openDemocracy)、国際機関の論点集(WEF・OECD)。**計25件に当たり、推奨候補は6件(商用◎5・○1)**。うち実テーマの本文まで確認できたのはP(Polis)・G(Grand Débat)・U(英国請願+Hansard)の3件で、C(Climate Assembly UK)・GV・TCは補助(精読の範囲は§2-1)。
- 時刻記録: 本書の取得は2026-10-29 07:29〜07:47(JST)。個別の取得時刻は§2・§3の確認日欄と各テーマに記載。

## 2. サイト評価表(推奨候補: 商用◎/○のみ)

凡例: 商用◎=想定用途(読み取り→独自3 Persona・一人称原稿をAI生成→商用提供)に該当する商用・二次利用・翻案が**明示的に許容**。○=明確な禁止・契約必須が確認されない。**ライセンスはテキスト自体への許諾であり、想定用途は着想の利用(逐語転載なし)**。CC系はいずれも**出典表示(BY)が条件**で、放送・配信での表示方法は新しい設計論点(§5)。

| サイト | 国・地域 | 言語 | 商用利用 | 規約URL・条項逐語・確認日 | Family Y適性 | 主なテーマ | 3軸の取りやすさ | Personaの作りやすさ | 注意事項 | 国固有除外判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| **P. Polis(Computational Democracy Project)オープンデータ**(`github.com/compdemocracy/openData`。vTaiwan Uber、オーストリア気候市民会議、NZ Scoop Hivemind[UBI・住宅・淡水・税]、Seattle最低賃金、London youth policing、Bowling Green等) | 台湾・オーストリア・NZ・米・英 | 繁体中国語・独語・英語 | **◎**(CC BY 4.0、データに限る) | https://raw.githubusercontent.com/compdemocracy/openData/master/README.md 「**All Polis data is licensed CC By 4.0**」「Each data set is a model of the opinions of a population ... containing anonymous human expressions」。帰属表示の定型文あり(「sub-licensed under CC BY 4.0 with Attribution to The Computational Democracy Project」)。2026-10-29 07:35 | **△**(論点・対立軸の発掘は優秀。人物は匿名の一文で具体性なし) | 自家用車・ライドシェア・UBI・住宅・最低賃金 | **高**: 賛否票の付いた市民の一文が数百件。対立の強い文(例: 速度制限 同意985/反対787)が見つけやすい | **低**: 職業・家族・感情はほぼ書かれない。自己申告の一文(「私はUberの運転手」等)が稀にある | ①対象は**オープンデータとして配布された会話のみ**。pol.is上のそれ以外の会話は規約(JSアプリ)を読めず未確認。②Seattle・football concussionsの文は他サイトのコメントから転記された形跡があり出所未確認(推奨対象外とする)。③参加者の一文の著作権は参加者に残りうる(CDPがCC BYで再許諾と宣言)。逐語転載せず着想のみ | 会話単位で判定。vTaiwan・オーストリアは国固有制度を含むが、論点(ライドシェア・車の使い方)は普遍。**除外しない**(§4で個別に判断) |
| **G. Grand Débat National 公開データ**(data.gouv.fr) | フランス | 仏語 | **◎**(Licence Ouverte/Open Licence Etalab、v2.0) | https://www.data.gouv.fr/datasets/donnees-ouvertes-du-grand-debat-national 「une licence qui promeut la réutilisation la plus large en autorisant **la reproduction, la redistribution, l'adaptation et l'exploitation commerciale des données**」。出典表示(paternité)を義務付け。API等での自動処理も明示(「rendant possible un traitement automatisé」)。data.gouv.frのrobots.txtは`ChatGPT-User/GPTBot`にカタログ出力のみ禁止(データ本体は対象外)。2026-10-29 07:38〜07:39 | **○**(生活事情を含む自由記述が多い) | エコ転換の負担(通勤・暖房・断熱・税)、民主主義、税、公共サービス | **中〜高**: 2019年の同一設問に市民が回答。農村/都市/低コスト志向の差が読める | **中**: 居住(郵便番号上2桁)・生活背景(「農村で公共交通がない」「病気の身内」)が回答に出る。名前・職業は通常なし | ①2019年のデータで古い(「黄色いベスト」運動の渦中)。②ファイルが非常に大きい(64〜1,200MB)。Rangeや設問単位で扱う。③「匿名化済み」とされるが自由記述に個人情報が混ざる可能性。識別子は取り込まない | **部分的に国固有**(フランスの税・行政が主題の回答が多い)。**普遍的な生活課題(車の依存・暖房費・環境の不安)の回答を選別して使う前提で除外せず**。税制度・国家組織の回答は対象外 |
| **U. UK Parliament 請願サイト+Hansard(Westminster Hall請願討論)** | 英国 | 英語 | **◎**(OGL v3.0 / Open Parliament Licence v3.0) | https://petition.parliament.uk/help 「All content is available under the **Open Government Licence v3.0**, except where otherwise stated」。https://www.parliament.uk/site-information/copyright-parliament/ 「Parliament encourages you to use material ... Use of Parliamentary material is governed by the terms of the **Open Parliament Licence**」。OPL本文(.../open-parliament-licence/) 「You are free to: copy, publish, ... **adapt** the information, **exploit the information commercially and non-commercially**」。petition robots.txtは管理系・署名者一覧等のみDisallow。hansard robots.txtは空(0バイト)。2026-10-29 07:40〜07:47 | **△**(議題は魅力的。発言者が議員で評論家寄り。親としての実体験の発言は含まれる) | 子どものSNS、学校週4日、労働時間(請願768839は題のみ確認)、AI・教育等 | **高**: 請願者の主張+政府回答+議員の多様な発言(親・教員・NSPCC・自由主義者)が1つの議題に集まる | **中**: 議員自身の子育て体験(「スマホを買ったことを後悔」「十代の子4人」)と、選挙区民・生徒の声の伝聞がある。子ども本人の直接の声は少ない | ①Westminster Hall討論は議員の発言で、政党の立場に引かれる。②請願本文は短く一方向(賛成側のみ)。③OGLは第三者の権利を除く(動画音声は対象外=動画は使わない) | 英国の政策論だが、**論点(子ども×SNS、学校の長さと親の就労)は普遍**。英国の制度・政党攻防・規制名称の説明が長い発言は対象外 |
| **C. Climate Assembly UK**(climateassembly.uk) | 英国 | 英語 | **◎**(OGL v3.0) | https://www.climateassembly.uk/ 「The content on Climate Assembly UK is licensed under the **Open Government Licence v3.0** except where otherwise stated.」2026-10-29 07:42 | **△**(市民会議の最終報告・資料中心。個人の声の本文は未確認) | 気候と生活(移動・食・住宅の暖房・消費) | 中(報告書に「支持の割合」が出る。**未精読**) | 低(市民議員個人の発言は資料の動画・記録に限られ、本文未確認) | 報告書本文・議事記録は**案内ページしか確認していない**(精読していない)。補助候補。動画・画像は対象外 | 英国の2050ネットゼロ目標が文脈。生活側の論点(移動・食・暖房)は普遍。**除外しない**が、英国政策の説明部分は使わない |
| **GV. Global Voices** | 世界(ボランティア翻訳・多言語) | 英語ほか60言語 | **◎**(CC BY 3.0。本文・翻案・商用を明示許容) | https://globalvoices.org/about/global-voices-attribution-policy/ 「all content created by Global Voices is published under a **Creative Commons Attribution-Only license**. ... **Adapt — remix, transform, and build upon the material for any purpose, even commercially**」「IMPORTANT: Photos, video, audio sourced from other creators may not always be available on the same terms.」robots.txtはCrawl-delay 10。2026-10-29 07:31〜07:32 | **△**(実在の個人の声は含むが、記者の報道・解説が主。討論ではない) | 若者の政治参加、AI規制、難民受け入れ、環境 | 低〜中(1記事に複数の当事者の引用がある程度。立場の対立は記事次第) | 中(実名の当事者の経験が引用される。**実名は使わず**経験の型のみ) | ①報道記事。第三者の画像・動画・SNS埋込は別許諾。②多くは地域固有。**記事単位で選別**が必要 | 記事単位で判定: 確認した2本(西アフリカの被選挙年齢=地域固有で除外相当、ポーランドのウクライナ難民支援=歴史問題が中心でやや固有)。**普遍的な記事を選別すれば使える補助源** |
| **TC. The Conversation** | 世界(英・豪・米・仏・西等) | 英語ほか | **○**(CC BY-ND 4.0。規約に読者のAI・自動取得の禁止条項は確認されず) | https://theconversation.com/global/republishing-guidelines 「we ... publish under a **Creative Commons — Attribution/No derivatives license**. ... You can't edit our material」「**Translations**: are technically a derivative ... and so require author approval」「You can't systematically republish all of our articles」。https://theconversation.com/uk/terms-and-conditions にAI・クロール等に関する読者向け条項は見つからず(キーワード検索で該当なし。authors向けに「do not use generative AI」のみ)。robots.txtは`/comments/*`・`/*/search?`等のみDisallow。2026-10-29 07:31 | **△**(専門家の解説。体験談・人物の具体性はほぼなし) | 教育、AI、社会保障、気候、メンタルヘルス | 低(1記事は1人の専門家の主張。複数記事を束ねて3軸) | 低(研究者の分析で一人称の生活は少ない) | ①**ND**: 記事の翻案を配布する形は不可。想定用途は「着想を参考にした独自原稿」で記事の改変配布ではないが、記事に近い構成・表現を再現すると翻案と解されるリスク→逐語・構成の近似を避ける。②コメント欄はrobotsで除外されており対象外 | 記事ごとに英国・豪など国固有が混ざる(確認した2本=英国予算、自閉症児のA&E=英国医療制度前提)。普遍的な記事のみ使う補助源 |

### 2-1 各サイトの補足(根拠の範囲)

- **P(Polis)**: 取得した文は`comments.csv`(ID・賛成数・反対数・本文)。オーストリア会話5本(各522〜2,138件)、vTaiwan Uber 197件、NZ UBI 71件・住宅165件、Seattle 54件、football 298件、London youth 39件。participants-votes.csvによる意見グループ(クラスタ)は**計算していない**ので、「グループA/B」ではなく**文の内容と賛成/反対数**で立場を見ている。
- **G(Grand Débat)**: 取得は`la-transition-ecologique.csv`(2019-01-31分、64,239,619バイト)の先頭約700KB(458行)のみ。設問は「環境の最も重要な具体的問題」「日常は気候変動の影響を受けているか」「移動の代替手段を使えるか」など15問。居住地は郵便番号上2桁のみを見て、個人は特定していない。
- **U(UK請願)**: 請願`700086`(16歳未満SNS禁止、署名132,102、討論2025-02-24)と`727514`(学校週4日、署名126,014、討論2026-01-05)のJSONを読み、Hansard討論は次の範囲で読んだ: 請願700086の討論=全69発言ブロックの冒頭と主要キーワード周辺を確認し、発言7・22・24・37・38・47・51は本文を読んだ(全発言の通読はしていない)。請願727514の討論=全8発言ブロックのうち、冒頭の議員発言(約4,000字)を本文まで、残りは冒頭約500字を確認。
- **C(Climate Assembly UK)**: トップ・「Wider society」・報告書案内ページのみ。個人の声を使えるかは未確認(精読していない)。
- **GV**: 2記事を本文まで読んだ(西アフリカ、ポーランド)。RSSでタイトル一覧のみ確認。
- **TC**: republishing guidelines・T&C・記事2本(トップ部分)。

## 3. 除外・未確認一覧(最終推奨に載せない。理由と根拠)

状態の定義: 除外=明確な禁止または契約・許諾必須 / 未確認=規約が読めない・条項不明確。**未確認を○にしていない**。いずれも確認日2026-10-29。

| # | サイト | 国 | 状態 | 理由・根拠(原語+要旨)・取得時刻 | 国固有判定・備考 |
|---|---|---|---|---|---|
| 1 | **Debating Europe**(debatingeurope.eu。出発点) | EU(ブリュッセル) | **未確認(対象外寄り)** | 現在はシンクタンクFriends of Europeの市民参加部門で、**公開の討論スレッドは確認できず**(アクティビティ一覧は調査レポート・イベント。コミュニティはログイン/登録制)。規約は「Privacy Policy & Code of Conduct」のみで、コンテンツの再利用・二次利用条項なし。フッター「©Debating Europe 2026」。robots.txtは制限なし。例「Voices for Choices – Is Europe ageing fairly?」(2026-05、欧州6か国の18〜35歳2,000人調査。内容はPDF、未取得)。https://debatingeurope.eu/ ・/about/ ・/cookies/ 07:29〜07:30 | 世代間負担という普遍論点だが、調査レポートで個別の声は未確認。PDFの再利用許諾は不明 |
| 2 | **Munk Debates** | カナダ | **未確認** | 利用規約ページが見つからず(/terms-of-use/は404、privacyのみ)。主要コンテンツは会員制(「Locked content / Join to watch」「Become a Supporter」)。登壇者は著名評論家(Kissinger、Murray等)で、**人物が評論家化**するためFamily Y適性も低い。robots: Crawl-delay 10。https://munkdebates.com/ ・/debates/gene-editing-debate/ 07:33 | 論点は普遍(AI、遺伝子編集)だが評論家型 |
| 3 | **ZEIT ONLINE(「Streit」等の読者討論)** | ドイツ | **未確認(強い否定シグナル)** | robots.txtが`ClaudeBot`/`anthropic-ai`/`GPTBot`/`CCBot`等のAI botを`Disallow: /`とし、`*/comment-thread?`もDisallow。利用規約`/agb`は**HTTP 403で読めず**。https://www.zeit.de/robots.txt 07:33 | 規約を読めず○にできない |
| 4 | **Perspective Daily** | ドイツ | **除外** | 会員制有料の建設的ジャーナリズム(討論サイトではない)。robots.txtに「perspective-daily.de expressly reserves the right to use its content for commercial text and data mining (§ 44 b UrhG). The use of robots or other automated means ... is strictly prohibited」とあり、`ClaudeBot`等を`Disallow: /`。要許諾(online-syndication@...)。https://perspective-daily.de/robots.txt 07:33 | 許諾必須 |
| 5 | **gutefrage.net** | ドイツ | **除外** | AGB§10「**Die Nutzung aller auf gutefrage veröffentlichten Inhalte für Text und Data Mining im Sinne von § 44 b Urheberrechtsgesetz (UrhG) ist untersagt.**」(=TDM全面禁止)。https://www.gutefrage.net/agb 07:34 | Q&A型。禁止明文 |
| 6 | **Naver 知識iN**(kin.naver.com) | 韓国 | **除外** | robots.txt「`# BOT ACCESS FOR THE PURPOSES OF AI TRAINING AND RETRIEVAL-AUGMENTED GENERATION (RAG) IS STRICTLY PROHIBITED.`」、`Yeti`にも`/qna/detail`をDisallow、ClaudeBot等を全面Disallow。利用規約は投稿者に権利、Naverへ広い許諾(二次的著作物は翻訳に限る)。https://kin.naver.com/robots.txt 07:34 / https://policy.naver.com/rules/service.html | 質問回答は`/qna/detail`の自動取得が不可 |
| 7 | **Zhihu(知乎)** | 中国 | **未確認** | 利用規約(https://www.zhihu.com/term/zhihu-terms 07:34)に「**使用任何自动化程序、软件或类似工具接入知乎，收集或处理其中信息、内容**」を禁止する条項(a)。AI・商用の個別許諾は見当たらない。手動閲覧のみでの利用可否は規約から断定できず、本文はログイン壁(bot遮断)が通常で取得は試みていない。中国語で量産時の確認コストも高い | 自動収集は禁止。手動閲覧の代替は未検証のため未確認 |
| 8 | **The Straits Times / SPH Media** | シンガポール | **除外** | SPH Media利用条件「You may not reproduce, modify, adapt, ... exploit **for any commercial or other purposes**, any portion of ... any SPH Media Content」「you agree not to ... provide access to ... Third Party User Content ... through ... spidering, scraping」「You may **for your personal, non-commercial use**: retrieve and display ...」。https://www.sph.com.sg/tnc/website 07:42 | 読者投稿等の第三者ユーザーコンテンツも同条項の対象(Forumページ自体は未確認) |
| 9 | **Rappler** | フィリピン | **未確認** | robots.txtが`GPTBot`/`anthropic-ai`/`ClaudeBot`/`CCBot`を`Disallow: /`。利用規約の所在(/terms-of-use/は404)を確認できず。https://www.rappler.com/robots.txt 07:42 | 規約未確認 |
| 10 | **Carers UK フォーラム**(Carers Connect) | 英国 | **除外** | 公開面はヘルプ類のみで投稿の大半は会員限定(カテゴリ一覧は「Feedback」のみ)。T&C「**You may not automate access to the forum, or monitor the forum, such as with a web crawler**」「Content you submit ... belongs to you」(他者への再利用許諾なし)。https://forum.carersuk.org/tos 07:43 | 会員契約下。介護テーマは魅力的だが不可 |
| 11 | **Doctissimo フォーラム** | フランス | **未確認** | CGUのURL(/html/cgu.htm)は404、規約を特定できず。robots.txtはCCBotにCrawl-delay 2。https://www.doctissimo.fr/robots.txt 07:43 | 規約未特定 |
| 12 | **世界経済フォーラム(WEF)** | スイス | **未確認(アクセス遮断)** | 利用規約ページがAkamaiで`403 Access Denied`。回避せず | 論点整理(△候補)だったが規約読めず |
| 13 | **OECD**(terms and conditions) | フランス | **未確認(アクセス遮断)** | `403`("Just a moment..."、Cloudflare)。回避せず | 同上 |
| 14 | **Decidim Barcelona** | スペイン | **未確認(アクセス遮断)・国固有寄り** | robots.txt・規約ともに`403 Forbidden`(nginx)。回避せず。バルセロナ市の自治体参加が主題(サイト名・用途からの理解で、本文は未確認) | 自治体制度が主題=国固有除外にも該当する可能性が高い |
| 15 | **Citizens' Assembly(アイルランド)** | アイルランド | **未確認** | サイトは「© 2026 Citizens' Assembly. ... **All rights reserved.**」で、利用許諾の記載はなくPrivacy Policyのみ。アーカイブ(ジェンダー平等・薬物・生物多様性等の報告書)は公開。https://citizensassembly.ie/ 07:37 | 権利留保。ライセンス明示なし |
| 16 | **EU Have Your Say**(欧州委員会) | EU | **未確認(第三者投稿)・国固有除外寄り** | 欧州委員会サイトの委員会所有コンテンツは**CC BY 4.0**(https://commission.europa.eu/legal-notice_en「content owned by the EU ... is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence」「You may be required to clear additional rights if a specific content ... includes third-party works」)。ただし**市民・団体の意見(フィードバック)は第三者コンテンツ**でHave Your Say個別の規約を取得できず(JSアプリ)。EU立法案への意見募集で、EU制度が主題の案件が多いと見られる(一般的な理解。JSアプリで本文は未確認)。https://ec.europa.eu/info/law/better-regulation/have-your-say_en 07:37 | EU制度が主題=国固有除外寄り |
| 17 | **openDemocracy** | 英国 | **未確認** | 到達できる範囲(トップ・/about/)にライセンス・転載規約の記載が見つからず、republishページは404。推測で判断しない。https://www.opendemocracy.net/ 07:41 | |
| 18 | **Make.org** | フランス | **未確認** | robots.txtは制限なし(`/beta/*`のみ)だが、規約・オープンデータ条項の所在を特定できず(/FR/legalは404)。https://make.org/ 07:41 | 市民提案プラットフォームで有望だが規約不明 |
| 19 | **Le Drenche**(仏) | フランス | **到達不能** | 推測URL3本(ledrenche.fr / www.ledrenche.com / le-drenche.fr)がいずれも名前解決不可。サイトの実在を確認できず(推測で評価しない) | |

## 4. テーマ候補(原文§7Bの9項目。実際に確認した主張とAI構成のPersona案を分離)

表記: 【確認】=原文で実際に読んだ主張(短い原語引用+agent訳)。【AI案】=AIが構成するPersona(実在ではない)。「3軸確認済み」=実際の発言で3つの立場を確認できた場合のみ。

### TH-B1. 「自家用車を手放せるか」──都市と地方で答えが変わる(車依存と環境政策)

1. **問い**: 公共交通が整えば車を手放すか。それとも自分の暮らしには車が必要か。誰がその負担を負うのか。
2. **主な情報源**: P(オーストリア気候市民会議のPolis会話、独語)+G(仏Grand Débat「環境」設問、仏語)。
3. **原文URL**:
   - オーストリア: https://github.com/compdemocracy/openData/tree/master/austria-climate.5tzfrp5eaa.2022-07-07 (`comments.csv`、2,138件。取得2026-10-29 07:44)。
   - フランス: https://static.data.gouv.fr/resources/donnees-ouvertes-du-grand-debat-national/20200611-173104/la-transition-ecologique.csv (先頭約700KBのみ、取得07:39。参照ID `2-8`・`2-17`・`2-23`・`2-30`)。
4. **商用利用Status**: P=◎(CC BY 4.0)、G=◎(Licence Ouverte 2.0)。
5. **Family Y適性**: **○**(テーマ・3軸は良好。Personaの具体性は別情報源で補完が要る)。
6. **実際に確認した主張**(オーストリアはコメントIDと同意/反対数、いずれもagent訳):
   - **A 地方・車必須(確認)**: 「議論は都市ばかりで、バスが数分おきに来る前提。**地方では車が必要**」(#1123, 同意86/反対49)/「あなたは地方に住んでいない。最寄りバス停は8km先」(#1121)/「村に住んでいて半径3kmに公共交通がない」(#1080)/「地方で冬に自転車で医者へ? いいえ」(#1731)。フランスでは「**農村地域で公共交通は無い**。残念ながら」(`2-17`)。
   - **B 条件付きで手放す(確認)**: 「**居住地が公共交通でよく行ける場所なら、自家用車を手放す用意がある**」(#27, 同意889/反対651)。「通勤手当は代替の公共交通が本当に無い人だけに」(#32, 956/504)。フランスの自転車通勤者は「**仕事に行くのに命を危険にさらさないための自転車道を**」(`2-8`)。
   - **C 選択の自由・指図されたくない(確認)**: 「**市内を今後も車で走れる選択肢を持ち続けたい**」(#170, 581/588=ほぼ拮抗)/「**どの交通手段を使うか指図されたくない**」(#181, 502/378)。フランス: 「**エコ転換は、痛みがほぼ無い場合にしか受け入れられない。あらゆる課税をやめ、罰でなく前向きに促せ**」(`2-30`)。
   - 補助(確認): ラストマイルの解(ルフバス・相乗りタクシー・カーシェア、#267, 532/113)。
   - **3軸確認済み**(地方の生活必需・都市の条件付き協力・自由/コスト感の反発。いずれも実在の市民の一文で確認)。ただし発言者は**匿名の一文**で、職業・家族・年齢は書かれていない(フランスは郵便番号上2桁と短い回答文脈のみ)。
7. **Persona構成案【AI案】**: ①地方の交代勤務者(家から最寄りバス停8km、冬の早朝・深夜に通勤。「都会の人は簡単に言う」) ②都市の共働き通勤者(車を手放してもいいが「駅から保育園までのラストマイルが解決するなら」という条件付き) ③車の運転が生活の自由と感じる人(家族の送迎・親の通院を一人で担い、「指図されたくない」「でも本当は一番コストを払っている」)。ここに**職業・家族構成・感情は実在の発言からは確認できていない**(AIの構成)。
8. **面白さ・普遍性**: 日本の地方の車依存・免許返納・ライドシェア議論と直結。「環境のために」と「暮らしの現実」が対立する構図が共感を呼ぶ。英語学習では条件文(`if ... I would`)・譲歩・比較の表現が自然に使える。
9. **追加で必要な体験談**: 地方の通勤・通院・送迎の具体場面(体験談系の補強)。Grand Débatの自由記述(`Contributions libres`)から生活場面を拾える可能性があるが、**自由記述の本文は未取得**。国内情報源(ガルちゃん・ママスタ等、条件付き)の補強は別Lane/委任_02で判断。

### TH-B2. 「ライドシェアは歓迎か、既存タクシーの生計を脅かすか」(Uber)

1. **問い**: 一般ドライバーの有償送迎を解禁すべきか。利用者の安全・タクシー運転手の生計・ドライバーの権利をどう守るか。
2. **主な情報源**: P(vTaiwan Uber会話、繁体中国語。2015年)。
3. **原文URL**: https://github.com/compdemocracy/openData/tree/master/vtaiwan.uberx (`comments.csv`、197件。取得2026-10-29 07:36)。
4. **商用Status**: ◎(CC BY 4.0)。
5. **Family Y適性**: **△〜○**(3軸は強い。人物の具体性は薄いが、自己申告の一文が少数ある)。
6. **実際に確認した主張**(ID・同意/反対、agent訳):
   - **A 乗客・利用者(確認)**: 「Uberは評価制度があり、点数が低い運転手は停止・再教育される。タクシーは免許があれば悪質でも走れる。**だからUberの方が安心**」(#95)/「Uber運転手は降りる客のために静かに路肩へ寄る。タクシーは強引に車線変更」(#66, 404/77)/「Uberの評価制度で低評価の運転手が淘汰されるので消費者には保障がある」(#169, 73/21)。
   - **B 既存タクシー・規制擁護(確認)**: 「Uberxは違法・不公平で**職業タクシー運転手の就業生存権を侵害**している」(#86)/「タクシー運転手は試験が年々難しくなるのに、Uberは職業運転免許だけで足りる。事故の責任は誰が取るのか」(#27)/「税金を払わないのに政府は何をしているのか」(#36)。
   - **C 運転手の権利(確認)**: 「**私はUber試乗の運転手。会社の管理に失望**。新車に酔客が嘔吐、数日休業。その後事故に遭っても緊急直通電話がなく、会社は『まず自分の保険で』と言うだけ」(#176)/「運転手の収入はタクシーの方が良い。Uber運転手の収入は運賃の6割」(#162, 38/19)。
   - **D 先読み(確認)**: 「自動運転が来る。タクシー運転手の雇用はどうなるのか」(#94, 294/108、#93)。
   - 自己申告の短文として「私はUber運転手」(#2)、「私はタクシー運転手」(#1)あり(いずれも賛否票は低く、内容はこの一文のみ)。
   - **3軸確認済み**(乗客/既存タクシー・規制/Uber運転手。D先読みを加えて4立場)。
7. **Persona構成案【AI案】**: ①Uberを選ぶ夜勤明けの会社員(乗客。評価制度で安心するが、事故が起きたら誰の責任かは考えていない) ②個人タクシーを30年続ける運転手(試験・保険・税を払ってきた。「同じ土俵なら良い」) ③副業でプラットフォームの運転手になった人(嘔吐の清掃・事故後の放置。会社に守られていない感覚)。**職業・年齢・家族は実在の発言から確認できていない**(AI案)。②の運転手本人の声は一文(#1)しかなく、人物像は薄い。
8. **面白さ・普遍性**: 日本のライドシェア解禁議論と直結。「安心して乗れる新しいサービス」と「長年の免許・規制を守った人の生計」という、価値観・利害が異なる立場がそろう。
9. **追加で必要な体験談**: タクシー運転手・副業運転手の実体験(国内の掲示板=条件付き、またはGlobal Voicesのギグワーカー記事)。**2015年・台湾の制度(黄牌・白牌)前提のデータで古い**ため、現在の議論(自動運転・日本のライドシェア制度)の事実確認は別途。

### TH-B3. 「子どものSNSを16歳未満禁止にすべきか」

1. **問い**: 16歳未満のSNSアカウント作成を法律で禁止すべきか。それとも別の方法(プラットフォーム設計・親の支援・教育)が効くのか。
2. **主な情報源**: U(英国議会請願700086+Westminster Hall討論)。
3. **原文URL**: 請願 https://petition.parliament.uk/petitions/700086 (JSON `.../700086.json`、署名132,102、取得07:46)/討論 https://hansard.parliament.uk/commons/2025-02-24/debates/E10FCC57-9169-4D7A-A90A-76FE1BD9309E/SocialMediaUseMinimumAge (全69発言ブロックを取得、冒頭とキーワード周辺を確認、主要発言は本文、2026-10-29 07:46)。
4. **商用Status**: ◎(OGL v3.0 / OPL v3.0)。
5. **Family Y適性**: **△**(議題は◎級。発言者が議員で評論家化しやすい)。
6. **実際に確認した主張**(Hansard発言。agent訳。「発言N」は取得した発言ブロックの番号):
   - **A 禁止すべき(確認)**: 請願「We believe social media companies should be banned from letting children under 16 create social media accounts」(いじめ・偽情報・暴力的コンテンツを理由)。議員(親)「**スマホを上の2人に買ったことを後悔している**。子ども4人。3人目が同じ権利を求めてくる。毎日が親の戦い」(発言22)。「**親を責めるのは不公平**。アルゴリズムは子どもが抗えない。16歳になったばかりの息子はGCSE(受験)中でもスマホから目を離せない」(発言38)。
   - **B 全面禁止ではなく設計・親の支援(確認)**: 「**無限スクロールなし・夜間通知なし・保護者が明示的に有効にしない限り中毒的アルゴリズムなし**」「オンライン安全の単独教育」「子どもの『安全な第三の場所(居場所)』を増やす」(発言51)。「スマホメーカーも親の支援機能を直感的に作る責任がある」(発言22)。
   - **C 禁止は実効性がない・子どもを危険な場へ(確認)**: 「NSPCCの立場: **禁止は子どもを規制されていないより危険なオンライン空間へ押しやる**。ソフトもデバイスも変えずに禁止だけでは執行不能」(発言7)。「**恣意的な年齢での一律規制が最も効果的とは思わない**。13歳未満の約40%が既に使っている。年齢制限だけでは限界がある」(発言37)。
   - 自由主義の立場(確認): 「**私は自由党員として本能的に禁止に反対。だが酒・たばこ・運転には最低年齢がある**。SNSも同じ視点で考えるべきでは」(発言24。問いかけの形)。
   - 豪州モデルの参照(発言26、44)。生徒本人の声は「議員が会った生徒がこう言った」の伝聞が中心。
   - **3軸確認済み**(禁止/プラットフォーム設計+親支援/禁止は実効性なし・居場所を奪う)。
7. **Persona構成案【AI案】**: ①十代の子3人の母親(夜に子どものスマホを巡って毎日衝突。「親だけが責められる」「法律があれば学校も動ける」) ②高校教員(スマホ禁止の校則はあるが敷地外で使う。「禁止するだけでは隠れて使う」) ③15歳の高校生(SNSは友達との連絡手段でもあり、いじめも見た。「一律禁止は孤立する子を増やす」)。**子ども本人の実在の発言は確認できていない**(議員経由の伝聞のみ)。人物像は全てAI案。
8. **面白さ・普遍性**: 日本の子どものスマホ・SNS規制(豪州の16歳未満禁止の報道含む)と直結。親・教員・子どもという立場の違いが自然に出る。
9. **追加で必要**: 子ども・十代本人の声(強い補強が要る。商用確認済みの体験談系で、年齢の低い当事者が書いた足は見つかっていない)。議員の発言を「親の体験」の型として使う場合、**政治家の発言のため評論的になりやすい点に留意**。

### TH-B4. 「学校を週4日(1日1時間長く)にすべきか」

1. **問い**: 学校を週4日にし、1日を1時間延ばす案をどう考えるか(生徒の休息・教員の定着・共働き家庭の保育)。
2. **主な情報源**: U(請願727514+討論2026-01-05)。
3. **原文URL**: 請願 https://petition.parliament.uk/petitions/727514 (署名126,014、取得07:40)/討論 https://hansard.parliament.uk/commons/2026-01-05/debates/19F9E3C3-4B57-4221-BC1F-38C236441355/LengthOfTheSchoolWeek (全8発言ブロックの冒頭を確認、先頭発言は本文まで、07:40)。
4. **商用Status**: ◎(OGL/OPL)。5. **Family Y適性**: **△**。
6. **実際に確認した主張**(agent訳):
   - **A 生徒・請願者(確認)**: 請願者は生徒で、教師の母がいる。「**教員の約3分の1が5年以内に辞める**ことを授業で知り、教員が家族と過ごす時間を増やせば残ると考えた」。生徒の調査では「15%以上が欠席が減る、4分の1以上がメンタルが改善すると回答」(議員の紹介)。
   - **B 生徒の懸念・疲労(確認)**: 「1日が長いと6限目に**脳が疲れて生産的でなくなる**」「宿題が増える」「冬は**暗い中を帰るので安全が心配**」(同)。
   - **C 特別な支援が要る子ども(確認)**: 「**追加の支援が必要な子ども**は、長い日と休みの日の学習支援をどうするか」(議員のFacebook投稿に約400コメント)。
   - **D 政府・親の就労(確認)**: 政府回答「週4日にすると**親は保育の手当や労働時間の削減、場合によっては離職を迫られ**、家計と経済に悪影響」。
   - **3軸確認済み**(生徒の休息/教員の定着、生徒・特別支援の負荷、共働き家庭の保育)。ただし**生徒・教員本人の直接の発言は確認できず**、議員の紹介と請願者の動機の伝聞。
7. **Persona構成案【AI案】**: ①受験を控える高校生(休みの日が欲しい。でも暗い帰り道が不安) ②小学校の教員(燃え尽き寸前。週4日なら続けられる) ③小学生2人を抱える共働きの母(金曜日の預け先がない)。全てAI案。
8. **面白さ・普遍性**: 週4日勤務の議論と同じ構図(休息 vs 家庭の就労)。日本の教員の長時間労働・学童保育とつながる。
9. **追加で必要**: 教員・保護者本人の体験談。英国の学校制度(GCSE等)の説明は削る。

### TH-B5. 「ベーシックインカムは必要か」(補助・弱い候補)

1. **問い**: 全員に無条件の基礎収入を支給すべきか。
2. **情報源**: P(NZ Scoop Hivemind UBI会話、英語)。https://github.com/compdemocracy/openData/tree/master/scoop-hivemind.ubi (71件、07:36)。
3. ◎(CC BY 4.0)。Family Y適性: **△**。
4. **実際に確認した主張**(英語原文の短い引用):
   - **擁護(確認)**: 「A UBI would better facilitate and recognise **unpaid work such as care** for the elderly, children, disabled people」(#5, 150/8)/「**improve the bargaining positions of the most vulnerable workers**」(#26, 144/6)/「With unemployment projected to reach 40% ... we need something in place」(#52・#64)。
   - **条件付き・慎重(確認)**: 「UBI ... **must not completely replace the current welfare system**」(#23, 117/24)/「We should not implement a UBI until we have a well funded 'Swedish style' social welfare system」(#30, 同意30/反対32 ほか多数が中立)/「cost ... should be offset by cuts to government funded services」(#6, 16/135=強く反対された)。
   - **懐疑(確認)**: 「Some people are simply lazy ... they would just stop working」(#18, 33/116=反対が大多数)/「So dumb really ... then i will just quit my job and do nothing all day」(#53, 1/0)。
   - **2軸+αを確認**(擁護と条件付き慎重は十分。**懐疑派の声は少数で薄い**)。第3のVoice(懐疑)は票の付かない一文に頼るため**「3軸確認済み」とは言えない**。
5. **Persona案【AI案】**: ①介護で離職した人(無給のケア労働の評価) ②零細事業主(財源と労働意欲への懸念) ③派遣・非正規労働者(交渉力)。実在の人物情報はなし。
6. **注意**: 声明の多くは主催者(Scoop・PEP)が用意した立場文で、参加者の自然発生的な声は少数。国固有(NZ福祉制度・マオリへの言及)あり。**補助的に論点を確認する用途にとどめる**。

### TH-B6(参考). 住宅価格の原因──投機・外国人購入・金融・供給(NZ)

- 情報源: P(`scoop-hivemind.affordable-housing`、165件、07:36、◎)。確認した異なる主張: 「**外国人による住宅所有**は住宅危機で短期思考」(#120, 43/13)/「**資産インフレは銀行の借入拡大**の結果」(同意35/反対16)/「**年間の土地税**を課し所得税を下げる」/「**100㎡・風呂1つ・車庫なし**の家を建てれば、人々は住んでから買う」/「1975年の介入策は機能した」(#143, 37/3)。
- 原因論として4立場は確認できる(外国人投機・金融・税制・小さい住宅の供給)が、**生活者の体験談は薄い**(Persona不能)。NZ固有の制度(政権批判)も混ざる。参考記録のみ(推奨しない)。

### テーマ候補の判定サマリ

| テーマ | 3軸 | 発言の質 | 主な弱点 |
|---|---|---|---|
| B1 車を手放せるか | 確認済み(独・仏の2データ) | 匿名の一文+短い自由記述 | 人物の職業・家族がない。地方の具体場面を補強 |
| B2 ライドシェア対タクシー | 確認済み(乗客/既存タクシー/運転手+先読み) | 匿名の一文、運転手の自己申告あり | 古い(2015)。台湾制度前提 |
| B3 子どものSNS禁止 | 確認済み(禁止/設計+親支援/実効性なし) | 議員(親)の演説 | 評論家化、子ども本人不在 |
| B4 学校週4日 | 確認済み(休息/保育) | 議員の紹介+請願 | 当事者の直接発言なし |
| B5 UBI | 2軸+α(3軸とは言えない) | 主催者用意の立場文が多い | 懐疑派が薄い |
| B6 住宅価格(参考) | 原因論4立場。Persona不能 | 匿名の一文 | 体験談なし |

## 5. 他Lane候補・所見(判断はFable)

### 5-1 他Laneの候補(調査していない。名前のみ)
- 01a(英語圏): Kialo、DebateArt、DebateWise、Intelligence Squared、Debating Matters、ProCon、CreateDebate、Quora、Hacker News(既登録=未確認)。本Laneで英国請願・Hansardを調べたため、**英国議会の別議題(請願)の追加発掘は01aと重複しうる**。
- 01c(国内): 国内の掲示板・熟議・市民意見。
- 未調査の追加候補(本Laneの範囲だが時間内に精査せず): Participedia(熟議事例ライブラリ)、idebate.org(Debatabase。英語圏の可能性)、欧州議会請願ポータル(PETI。JSアプリ)、独Bundestag e-Petition(セッションCookie必須で未読)、台湾Join(請願。国固有の可能性)、Healthwatch(英国の医療・介護の体験。国固有寄り)、Decidimの他インスタンス。

### 5-2 所見
1. **ライセンス明確なのは「公共/オープンデータ型」**(CC BY・OGL・Licence Ouverte)。掲示板型は、欧州では**TDM禁止(gutefrage)・AI botのrobots拒否(ZEIT・Rappler・Perspective Daily・Naver)・会員制(Carers UK)**が明確で、Family Y向けの「人物の具体性」と「商用の明確さ」がトレードオフになっている。
2. **役割分担の提案**: Debate系(本Laneの◎群=Polis/Hansard/Grand Débat)で**論点・対立軸・価値観の差**を発掘し、Personaの具体性(職業・家族・感情)は**商用条件が○以上の体験談系**(既存レジストリのガルちゃん・ママスタ等、条件付き)で補う。本Laneの中でPersona補強に使える足は、Grand Débatの自由記述とGlobal Voicesの当事者引用のみで限定的。
3. **規約上の残存リスク**: ①CC BY系の出典表示を音声ラジオでどう満たすか(概要欄の表記等)は新しい設計論点。②CC BY-ND(The Conversation)は翻案配布が不可。③Polisは「データ本体はCC BY 4.0だが、参加者の一文の権利は参加者に残る」構造。④Hansard/OGLは第三者の権利を除外。⑤Grand Débatは匿名化済みでも自由記述に個人情報が混ざる可能性。いずれも「法的保証ではない」。
4. **収集負荷・費用**(実測): Polis=CSV1ファイル5KB〜1.3MB、取得0.1秒・費用0円(読解のみ)。UK請願=JSON1回+Hansard HTML1回(0.1〜0.5MB)で1テーマ。Grand Débat=Range指定で数百KBを読めるが、設問を絞らないと数十MB〜GB。**量産時の費用は取得0円、主コストは読解(token)。LLM呼出は未計測**。
5. **未確認の最大の穴**: Climate Assembly UK報告書本文とGrand Débatの自由記述本文は精読していない(委任_02以降の検討事項)。
6. **Production採用前に本当に必要なユーザー判断(判断候補)**: (1) CC/OGL/Licence Ouverte系オープンデータを新しい情報源としてProduction素材に加えるか、およびその出典表示方式。(2) 本Laneでは◎のテーマの多くがFamily Y適性△のため、Debate系とPersona補強源の組合せ方式をどう採るか(新収集方式=ユーザー承認)。いずれも**分類D(新規判断)の候補**であり、本Laneでは決めない。
