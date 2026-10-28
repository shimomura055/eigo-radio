# LANE_C_DOMESTIC_01 (FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 委任_01c: 国内のDebate/Discussion系・市民討論・意見投稿プラットフォーム)

確認日: 2026-10-29(全URLを同日 07:30〜07:47 JSTに取得)。調査のみ・LLM API呼出0・費用0円・Production変更なし。ユーザー原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`(§2〜§5・§9で再確認済み)。本書は法的助言ではない。
**登録≠採用承認**。新サイト・新収集方式のProduction採用はユーザー判断待ち(原文§8)。`SOURCE_REGISTRY_01.md`・ACTIVE_TASK・SSOTは編集していない(統合は委任_02)。
前提(既存02Aと同じ): 本調査でページ本文を読んだのはAI(Claude)であり、「読む」=AI入力でもある。規約が人の閲覧しか想定していないサイトは、AI入力について実質「未確認」側に倒した。

## 結論(先に)

- 国内に「異なる立場が議論し、商用で使え、人物像まで取れる」民間Debate/市民討論サイトは**見つからなかった**。民間プラットフォームは (a)終了・メンテ・JS描画・ログインでアクセス不能 (b)規約が営利・無断転載・許諾必須 (c)政治/自治体政策特化=国固有除外 のいずれか。禁止・未確認サイトで数は補っていない。
- ◎/○で推奨できるのは**公的な議論記録の3系統**: ①国会会議録(参考人質疑。○) ②厚労省 審議会議事録(PDL1.0。◎。既登録D-10の新コンテンツ種別) ③気候市民会議さっぽろ2020報告書(環境省council資料。○・要注意)。いずれも規約面は民間より明確だが、**発言者が専門家・団体代表中心**で、Family Y適性は△〜○。
- 中身を本文まで読んで確認した実テーマ=推奨3件+参考1件(§4)。**実発言で3軸を確認できたのはT1(両立支援)とT2(気候市民会議)の2件**で、いずれも当事者/市民の一人称発言を含む。T3は専門家発言のみ。
- 取得は全て単発の手動閲覧相当のGETと、NDL公式API(規約で手続不要・間隔配慮が条件)の少量利用のみ。禁止された取得・アクセス制限の回避は行っていない(§1)。

## §1 探索方法・範囲

- 既存成果は参照のみ(`SOURCE_REGISTRY_01.md` §0・D-5・D-9・D-10・D-11、`TERMS_REVIEW_01.md` §2-1、`DOMESTIC_SOURCES_01.md`、`PUBLIC_SOURCES_CHECK_01.md`)。既判定(発言小町=除外[ユーザー決定①]、知恵袋・ガルちゃん・ママスタ・5ch・増田・note、e-Gov PDL1.0)は再調査していない。掲示板・相談サイトは増やしていない(原文§1)。
- 探索の起点=委任_01c §1の例示(Surfvote/PoliPoli/Decidim国内/NHKみんなでプラス/Yahoo!ニュース/Quora日本語/note・はてな/ディベート甲子園/国会・審議会/パブコメ/新聞読者投稿/SYNODOS・アゴラ/企業・団体の討論企画/当事者コミュニティ)+発見した市民討論(気候市民会議)・こども意見反映・デジタル民主主義2030・Change.org・STORYS.JP。
- 手段: 規約・robots.txt・討論ページを`curl`相当のrequests GETで1ページずつ取得(UA=`Mozilla/5.0 (compatible; eigo-radio-research/1.0)`の自己申告型、間隔1.6秒以上、クロール・ログイン・一括収集なし)。国会会議録のみNDL公式API(`api/meeting`・`api/speech`、計15リクエスト・最大10件/回)。サイト発見用にBing検索を9回(異なる検索語は6)・DuckDuckGoを1回(DDGは結果を得られず)実行。全取得URLと時刻=末尾の付録。全文キャッシュは権利上commitしない(scratchpad)。
- 規約根拠の逐語は取得本文との機械照合を実施(59/59一致。サイト規約・robots・国会発言・札幌報告書PDF・活動報告書PDFを含む)。
- アクセス制限の扱い: Quora(Cloudflare 403「Just a moment...」)・Surfvote(503メンテナンス)・ikenplus.cfa.go.jp(403メンテナンス)・PoliPoli(JS描画のみ)は回避せず「アクセス不能」で止めた。NHK・Yahoo!ニュース・加古川DecidimのrobotsがClaudeBot等を拒否している点は意思表示として尊重し、それらの本文は取得していない(NHKはサービス終了ページ、Yahoo!は`robots.txt`のみ、加古川は`robots.txt`・規約・トップのみ取得)。
- 評価した対象: 規約・robotsまで確認 21件(推奨3系統+非推奨18。うちアクセス不能等で一次判定のみ7件)。本文まで読んで実テーマを確認したのは国会会議録・審議会議事録・気候市民会議報告書(§4)。

## §2 サイト評価表

商用利用Statusの基準=原文§3(◎/○/除外/未確認)。「○」は法的保証ではなく「明確な禁止・個別契約・許諾必須の規定が確認されない」の意味。確認日はすべて2026-10-29。

### §2-1 推奨候補(◎/○のみ。3系統)

| サイト | 種別 | 商用利用 | 規約URL・条項逐語・確認日 | Family Y適性 | 主なテーマ | 3軸の取りやすさ | Personaの作りやすさ | 注意事項 | 国固有除外判定 |
|---|---|---|---|---|---|---|---|---|---|
| **国会会議録検索システム(NDL)** https://kokkai.ndl.go.jp/ | 公的議事録(公式API) | **○**(解釈依存。下記) | API利用条件 https://kokkai.ndl.go.jp/api.html §4: 「その他の発言の著作権は個々の発言者に帰属し、その利用については、原則として、著作権者の許諾が必要となります」/「著作権法の権利制限規定が適用される場合（…電子計算機による情報解析等）には、…許諾を得ることなくご利用いただけます」/「APIの利用には、手続き等は必要ありません。」/「機械的なアクセスを行う場合、多重リクエストは避けてください」。DB自体=NDLコンテンツ利用規約 https://www.ndl.go.jp/jp/sitepolicy/terms.html「公共データ利用規約（第1.0版）…に準拠した利用条件の下で、利用することができます」。robots.txt=なし(SPAのトップが返る)。2026-10-29 | **△**(論点整理・当事者1名の補強。人物はほぼ専門家) | 少子化・両立支援・AI・移民・年金等、委員会ごとの参考人質疑・公聴会 | ○(参考人質疑は立場が割れる。例: §4-T1は実発言で3系統) | △(参考人は大学教授・研究員・団体代表が大半。当事者参考人が混ざる会議だけPersona化できる) | 発言の著作権は発言者(公的人物)。**逐語利用せず論点・立場のみ**が条件。公式APIは手続不要・間隔配慮。「許諾が必要」と「情報解析等は不要」の併記のため残存リスクあり(NDLへ確認推奨)。議員の政争・法案の技術的細部は素材にしない | 非該当(議論の中身は個別に判断。法案の条文・手数料などは国固有で除外=§4で例示) |
| **厚生労働省 審議会議事録**(労働政策審議会ほか)https://www.mhlw.go.jp/stf/shingi/ ※既登録D-10の新コンテンツ種別 | 公的議事録(労使公益の三者構成) | **◎**(PDL1.0。第三者権利は別) | https://www.mhlw.go.jp/chosakuken/index.html「…権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます」。PDL1.0本文 https://www.digital.go.jp/resources/open_data/public_data_license_v1.0「複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます」(営利制限の記載なし)。robots=`/cgi-bin/`等のみDisallow(議事録パスは対象外)。2026-10-29 | **△**(論点の対立軸の記録。体験談なし) | 労働時間・家事使用人・両立支援・年金等 | ○(労側・使側・公益の3者構成が制度上固定) | ×〜△(委員は団体代表。個人の生活背景は出ない) | 登録簿D-10は「条件付き(AI入力の個別明文なし)」と判定済み。本Laneでは「翻案等の自由利用が明示」を理由に◎と記すが、**D-10の既判定を変更する提案ではない**(判断はFable)。出典・加工の記載が条件。制度説明化しやすい=Persona主材料にしない | 灰色(労基法の適用範囲など法令論は国固有。§4-T4) |
| **気候市民会議さっぽろ2020 報告書**(環境省council資料として掲載)https://www.env.go.jp/council/06earth/y0620-3b/900425001.pdf | 市民討論(無作為抽出市民20人)の報告書 | **○**(要注意) | 環境省サイトの規約 https://www.env.go.jp/mail.html「…「公共データ利用規約（第1.0版）」（PDL1.0）が適用されています」。ただし本PDFは「気候市民会議さっぽろ2020実行委員会」(北大等)の作成物で、PDF本文に権利・転載条件の記載なし(「転載」「著作」「無断」「ライセンス」で検索して該当なし)。PDL1.0が第三者作成資料に及ぶかは未確認→○止まり。2026-10-29 | **○**(一人称の発言が実在し、3系統の価値観が確認できる。属性は年代・性別比のみ) | 脱炭素の「痛み」(生活水準 vs 次世代)、行動指針の不足 | **◎**(§4-T2で実発言3系統を確認) | △(発言者は匿名・年代のみ。職業・家族は出ない) | 札幌ローカルな文脈+2020年。**世田谷版は区の規約で無断二次利用禁止=除外(§2-2)**のように、同種報告書は掲載元の規約次第。使う場合は北大/実行委員会への確認が望ましい | 非該当(札幌市の施策文脈はあるが議論は「どこまで自分が負担するか」で普遍) |

### §2-2 評価したが推奨しない(除外/未確認)

| サイト | 種別 | 商用利用 | 規約URL・条項逐語・確認日 | Family Y適性 | 主なテーマ/特徴 | 国固有除外判定 | 判定理由(要約) |
|---|---|---|---|---|---|---|---|
| NHK みんなでプラス https://www.nhk.or.jp/minplus/ | 意見募集企画 | 未確認(評価不能) | ページ本文「「みんなでプラス」は9月30日でサービスを終了しました。」(2026-10-29)。NHK robots.txt=ClaudeBot・anthropic-ai等を`Disallow: /` | — | 体験談の投稿フォーム→番組取材 | — | **サービス終了**。後継NHK ONEは討論サイトではない |
| Yahoo!ニュース コメント https://news.yahoo.co.jp/ | ニュースコメント | **除外**(02A準用) | robots.txt: `User-agent: ClaudeBot`…`Disallow: /`、`*`に`Disallow: /articles/*/comments`(2026-10-29)。規約はLINEヤフー共通利用規約14条を02A `TERMS_REVIEW_01.md` §2-1で判定済み(「提供目的を超えて利用することができません」) | — | 短文コメント(評論家化しやすい) | — | 既登録「アクセス不能・規約未評価」→**02A準用で除外寄り**に更新を提案(個別規約の再精読はしていない)。人手閲覧は未確認 |
| Quora 日本語 https://jp.quora.com/ | Q&A | 未確認 | robots.txt冒頭: 「All crawlers and bots…are strictly prohibited from using Quora platform content for the purposes of training AI models or similar machine learning systems, except where explicit prior permission has been granted by Quora through a contractual licensing agreement.」。トップはCloudflare 403、`/about/tos`は「問題が発生しました」(2026-10-29) | — | 質問回答 | — | ToS本文を取得できず(回避せず)。AI系利用に契約許諾を要求する意思表示あり=採用不可寄り |
| Surfvote https://surfvote.com/ (Polimill) | 賛否投票+理由コメントSNS | 未確認 | 全URLが503「メンテナンス中です」(07:30・07:43の2回、規約`/terms`含む)。運営社サイト https://polimill.jp/services/surfvote/ には「専門家や…が執筆する論点記事＝イシューを読み、あなたの立場に近い選択肢へ投票し、理由をコメントできます」(2026-10-29) | 未評価 | 社会課題の論点記事+投票+理由(**設計は本Laneの目的に最も近い**) | 未評価 | **アクセス不能(メンテ中)**。規約・討論本文を確認できず。再確認を推奨(§3) |
| PoliPoli https://polipoli-web.com/ | 政策プラットフォーム | 未確認 | robots=`Allow: /`。ただしJS描画のみで本文・規約を取得不能(`/terms`等も同一シェルを返す)。meta description「政治家や政党が掲げるテーマに意見を投稿し、政策立案をサポートできる」(2026-10-29) | — | 政治家・政党のテーマ | **国固有除外**(政治家・政党特化) | アクセス不能+国固有 |
| 加古川市版Decidim https://kakogawa.diycities.jp/ | 自治体の市民参加(Decidim) | **除外** | 利用規約 https://kakogawa.diycities.jp/pages/terms-of-service「営業、宣伝、広告、勧誘、その他営利を目的とする行為（本市の認めたものを除きます。）」を禁止。robots.txt: `User-agent: ClaudeBot`…`Disallow: /`(AI学習Bot拒否の意思表示)(2026-10-29) | — | 駅周辺・総合計画・LINE活用など | **国固有除外**(自治体施策) | 営利禁止+AI拒否+自治体施策特化 |
| デジタル民主主義2030(いどばた/広聴AI)https://dd2030.org/ | 政党・自治体向け熟議ツール | 未確認 | 利用規約ページ https://dd2030.org/policies/terms/ は本文が空(345文字)。活用事例=「チームみらいが運営する「みらいいどばた会議」」等(2026-10-29) | — | 政党政策集・総合計画のAI論点整理 | **国固有除外**(政党・自治体政策の運用ツール) | 掲示される意見は政党運営の場に紐づく。規約も未確認 |
| ディベート甲子園/NADE https://nade.jp/ | ディベート論題・勉強会 | **除外** | https://nade.jp/copyrights/「当サイト内の情報は クリエイティブ・コモンズ 表示 – 非営利 – 改変禁止 3.0 非移植 ライセンスの下に提供されています」(2026-10-29) | △(論点整理のみ) | 年度論題 | 非該当 | **非営利・改変禁止**=商用不可 |
| アゴラ https://agora-web.jp/ | 論壇ブログ | **除外** | https://agora-web.jp/sitepolicy「表示 – 非営利 2.1 日本 (CC BY-NC 2.1 JP)」「あなたは営利目的でこの資料を利用してはなりません」(2026-10-29) | △(評論家) | 政治・経済・IT | 灰色 | **非営利(NC)**=商用不可 |
| SYNODOS https://synodos.jp/ | 論壇・解説 | 未確認 | 規約ページなし。フッターは「Copyright © SYNODOS.Inc. All rights reserved.」のみ。robots=`/wp/wp-admin/`のみDisallow(2026-10-29) | △(評論家) | 社会・AI・働き方の論考 | 灰色 | 利用条件の記載がなく**未確認**。論考は評論家的で3 Voice向きでない |
| 朝日新聞(声など読者投稿) https://www.asahi.com/ | 新聞 | **除外** | https://www.asahi.com/policy/copyright.html「…無断で複製、転載、公衆送信、翻案、蓄積その他の利用をすることはできません」+AI生成物の権利帰属条項。robots.txt: GPTBot・ClaudeBot等を個別拒否(2026-10-29) | — | 読者の声 | — | **無断翻案・蓄積禁止**。他紙は同種と見込むが個別未確認 |
| STORYS.JP https://storys.jp/ | 体験談(ストーリー)投稿 | **除外** | https://www.storys.jp/terms「…本サービス以外の目的で利用しようとする場合には、利用者は当社の事前の書面による許諾を求めるものとします」。robots=`Content-Signal: search=yes,ai-train=no,use=reference`+ClaudeBot等拒否(2026-10-29) | — | 当事者の体験談(Persona補強候補だった) | — | **書面許諾必須** |
| Change.org 日本 https://www.change.org/ | 署名キャンペーン+賛同コメント | 未確認 | https://www.change.org/policies/terms-of-service「…サービス、プラットフォームおよびデータベースのスクレイピングは明示的に禁止されて(います)」/「robots.txtファイルの条項に従い実施される場合には、Change.orgサイトをクロールすることは認められます」(2026-10-29)。AI入力・商用の個別条項は確認できず | △未満(請願は一方向の主張で、討論でない) | 請願+賛同コメント | — | スクレイピング禁止(書面合意除く)=手動閲覧のみ。AI/商用は条項不明確で**未確認**。賛否が割れる構造でなく適性も低い |
| こども若者★いけんぷらす https://www.cfa.go.jp/policies/iken-plus | こども・若者の意見反映 | 未確認 | こども家庭庁 https://www.cfa.go.jp/copyright-policy「…権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）が適用されています」。意見の本体を載せる https://ikenplus.cfa.go.jp/ は403「メンテナンス中」。活動報告書PDFは運営受託企業の報告書で各頁に「Copyright © 2025 Accenture. All rights reserved.」(2026-10-29) | 未評価 | 「SNSもネット動画も、安心して楽しみたい！スマホ時間のモヤモヤ、聴かせて！」(2025-05)など20テーマ | 非該当 | 意見本体にアクセスできず、報告書は**権利表記あり**でPDL1.0の前提(権利表記なし)を満たさない→未確認。**ユーザー例示「子どものSNS」に近い実テーマが存在**する点は記録 |
| 世田谷版気候市民会議 https://www.city.setagaya.lg.jp/ | 市民討論の報告書 | **除外** | https://www.city.setagaya.lg.jp/02002/7723.html「…無断での使用・転載、二次利用を禁じます」(オープンデータとして公開したものを除く)(2026-10-29) | — | 区の気候施策 | 灰色 | 自治体規約が無断二次利用を禁止(登録簿D-11の東京都・横浜市と同種)。同種の市民会議報告書は**掲載元の規約次第** |
| ABEMA TIMES(ABEMA Prime等)https://times.abema.tv/ | 討論番組の記事化 | 未確認 | 規約本文を取得できず(`abema.tv/about/terms`はJS描画で空)。robots.txtはSemrush等のみDisallow(2026-10-29) | 未評価 | 当事者を交えた討論番組 | 未評価 | 規約未確認。**当事者討論という形式は目的に近く**、規約確認の価値はある(判断はFable) |
| サイボウズ式 https://cybozushiki.cybozu.co.jp/ | 企業メディア(働き方・家族と仕事) | 未確認 | 規約・著作権ページを確認できず(フッターは「Copyright(c) Cybozu,Inc.」のみ)(2026-10-29) | 未評価 | 一人称の働き方コラム・対談 | 非該当 | 編集記事であり討論ではない。規約未確認 |
| はてなブックマーク https://b.hatena.ne.jp/ | ニュースへの短文コメント | 未評価 | robots.txtのみ確認(`Crawl-delay: 5`、一部API/`jsonlite`をDisallow)。規約は02Aのはてな共通規約(増田=未確認)を準用、個別精読なし(2026-10-29) | △見込み(短文=評論) | ニュース論評 | — | 未評価。既存調査で使用済みの旨が登録簿に記載 |

## §3 除外・未確認の一覧と次の扱い

| 区分 | サイト | 理由の要点 | 再確認の価値 |
|---|---|---|---|
| 規約上の除外(商用不可/許諾必須) | NADE(CC BY-NC-ND)、アゴラ(CC BY-NC)、朝日新聞(無断翻案・蓄積禁止)、STORYS.JP(書面許諾必須)、加古川Decidim(営利禁止)、世田谷区報告書(無断二次利用禁止)、Yahoo!ニュースコメント(02A準用) | 原文§3「禁止・契約必須は最初から採用候補にしない」 | なし(条件が変わらない限り) |
| アクセス不能(規約の評価ではない) | Surfvote(503)、ikenplus(403)、PoliPoli(JS描画)、Quora(403)、NHK(終了)、ABEMA(規約JS描画) | 取得制限は回避しない | **Surfvote**=目的に最も近い。メンテ明け後に**1回**の手動再確認(自動再試行は作らない)。ABEMA TIMESは規約本文の入手経路を別途確認 |
| 国固有除外 | PoliPoli(政治家・政党)、加古川Decidim(自治体施策)、dd2030(政党・自治体運用) | 原文§2-2「特定政党・自治体制度だけを議論するサイト」 | なし |
| 未確認(条項不明確) | SYNODOS、Change.org、サイボウズ式、dd2030、はてブ(未評価) | 未確認は○にしない(原文§3) | 低(適性も低い) |

**ユーザー例示テーマの国内取得可能性**(メタ情報のみ確認、本文未読): 「ベーシックインカム」=国会参考人発言あり(2024-03-26 衆院厚労委 原田泰ほか)、「生成AI×雇用」=国会参考人発言あり(2026-03-11 参院国民生活調査会 大内伸哉、2025-05-22 参院内閣委 大屋雄裕ほか)、「週休3日」=国会参考人発言0件(API検索`any=週休3日`)。いずれも発言者は大学教授等の専門家で、当事者の一人称は確認していない。

## §4 テーマ候補(原文§7B 9項目。実確認済み3件+参考1件)

凡例: 【実】=本文を読んで確認した実在の主張(短い逐語は引用符、機械照合済み)。【AI案】=AIが組んだPersona案(実在発言ではない)。「3軸確認済み」は実発言で3つの異なる価値観・利害を確認できた場合のみ。

### T1(推奨) 仕事と家族ケアの両立: 「休業を長くすれば救われるのか」

1. **テーマ名・問い**: 子どもや親のケアを担いながら働き続けるために、休業や短時間勤務をもっと長く認めるべきか、それとも別の仕組みが要るのか。
2. **主な情報源**: 国会会議録(参議院 厚生労働委員会 2024-05-21、育児・介護休業法改正法案の参考人質疑)。
3. **原文URL**: 会議 https://kokkai.ndl.go.jp/txt/121314260X01520240521 / 発言 池田心豪 `…/2`、矢島洋子 `…/4`、川内潤 `…/6`、工藤さほ `…/8`(同URL形式)。API: https://kokkai.ndl.go.jp/api/meeting?issueID=121314260X01520240521&recordPacking=json
4. **商用利用Status**: ○(国会会議録。§2-1)。
5. **Family Y適性**: ○(当事者1名の具体性が高い。他は専門家=評論家寄り。3立場の価値観は独立)。
6. **実際に確認した異なる主張【実】**(**3軸確認済み**):
   - **当事者(工藤さほ、障がい児・医療的ケア児を育てる親の会会長)**: 現行制度は子の年齢で区切られ「終わりのない育児」には足りない。「重度の知的障害のある自閉症の娘を育てる私は」「親亡き後の子の経済的な蓄えも考えて働く必要がある私たちにとって、就労を継続できるかどうかは死活問題です」。制度の延伸・個別対応を強く求める。
   - **家族介護の支援者(川内潤、NPO法人となりのかいご代表、「年間に大体七百件ぐらいの個別の介護相談」)**: 逆に「休暇、休業の延伸、実家での無期限のテレワークは離職を後押しするのでおやめになられた方がいいと正直思っています」「家族が直接介護することを親孝行だと多くの方が思っているかもしれません」。「仕事と介護は絶対両立ができます」=抱え込まず、辞めないための体制づくりを重視。
   - **研究者(矢島洋子・池田心豪)**: 柔軟な働き方の拡充に賛成しつつ副作用を指摘。「働きやすさだけを配慮していくと働きがいやキャリア形成の視点が落ちてしまう」、利用が女性に偏る、「大企業と中小企業の差が開いているという状況」(矢島)/「新しい発想の下、新しいステージにこの両立支援は進んでいかなきゃいけない」(池田)。
7. **3 Voice構成案【AI案】**: V1=子の年齢で区切られない育児を続けながら働く母親(工藤の発言の論点・感情に基づく。実在人物の経歴は使わず別人格化)/V2=親の介護が始まった共働きの会社員で「辞めるのが親孝行か」と迷う人(川内の観察する「隠れ介護」「辞めるのが親孝行という誤解」に基づく。**実在の当事者発言ではない**)/V3=中小企業で両立支援の制度運用を回す人事・現場責任者(矢島の指摘する中小企業の差・マミートラックに基づく。**当事者発言は未確認**)。
8. **面白さ・普遍性**: 高い。「休めるようにするほど離職が進む」という逆説が3 Voiceの対立に直結。ケアと仕事は世界共通。法案名・制度名は前面に出さず生活語で語れる。
9. **追加で必要な体験談**: 介護中の会社員の生活感(ガルちゃん・ママスタ=条件付きの既登録源で補強可)、中小企業の運用側の声(未確保。V3は現状AI案)。工藤以外の当事者(上記3軸のうち実在当事者は1名のみ)。

### T2(推奨) 脱炭素の「不便」をどこまで自分事として引き受けるか

1. **テーマ名・問い**: 暮らしの不便や費用が増えても、社会は脱炭素を急ぐべきか。市民はどこまで自分でやるのか。
2. **主な情報源**: 気候市民会議さっぽろ2020 報告書(速報版、2021年1月、実行委員会作成。環境省council資料として掲載)。
3. **原文URL**: https://www.env.go.jp/council/06earth/y0620-3b/900425001.pdf (3.2「会議を振り返って〜参加者の感想〜」p.42〜43)。
4. **商用利用Status**: ○(要注意。§2-1)。
5. **Family Y適性**: ○(一人称の肉声で価値観が割れる。属性は年代のみ)。
6. **実際に確認した異なる主張【実】**(**3軸確認済み**。無作為抽出の札幌市民20人[10代〜70代、男性12・女性8]の発言):
   - **生活水準を守りたい派**: 「どんなやり方でも生活水準を下げるようなやり方は避けてほしいなと思いました」(行政・企業が主体で足りるとする考えが支配的だったとの記述もある)。
   - **次世代のために不便を受け入れる派(10代)**: 「多少の不便を強いられることがあっても、次世代へ」の影響を緩和するため2050年までの完全移行が望ましい。ただし同派の別の参加者は性急な再エネ開発の副作用を警戒し「2050年までに微調整もふくめて、脱炭素化を完了することだ」と主張。
   - **何をやればいいか分からない派**: 「わたしたち何をやればいいんだろう」「どこまで市民がやればいいの」。会議後に「EVやFCVが自分が思っていたほどには高くない」と気づき購入を考える人もいる(自分事化)。
7. **3 Voice構成案【AI案】**: V1=家計と暮らしの快適さを守りたい世帯主、V2=将来世代への責任を重く見る10代〜20代(ただし性急さのリスクも自覚)、V3=自分に何ができるか分からない会社員(会議で知識を得て態度が変わる)。**職業・家族・生活の具体は報告書に無く、全てAI構成**。
8. **面白さ・普遍性**: 高い。「痛みの許容度に個人差がある」という実感、説明の欠如による当事者意識の薄さは世界共通。札幌の施策名は不要。
9. **追加で必要な体験談**: 光熱費・車・住宅断熱など生活の具体(ガルちゃん・ママスタの光熱費トピ等=既登録・条件付き)、報告書の元になった発言者の属性(報告書は匿名)。

### T3(推奨・専門家のみ) 少子化対策: 「お金を配れば子どもは増えるのか」

1. **テーマ名・問い**: 児童手当や支援金で少子化は止まるのか。誰がどう負担し、現金とサービスのどちらに使うべきか。
2. **主な情報源**: 国会会議録(参議院 内閣委員会 2024-05-23、子ども・子育て支援法改正案の参考人質疑)。
3. **原文URL**: 会議 https://kokkai.ndl.go.jp/txt/121314889X01620240523 / 発言 権丈英子 `…/159`、奥山千鶴子 `…/161`、池本美香 `…/163`、八代尚宏 `…/165`。
4. **商用利用Status**: ○。
5. **Family Y適性**: △(参考人は全員専門家・団体代表=評論家化しやすい)。
6. **実際に確認した異なる主張【実】**(専門家4名の実発言。**立場は3系統**、Personaは専門家):
   - 再分配に賛成(権丈英子、労働経済学): 「子ども・子育て支援のための新しい再分配制度を創設するということは、とても望ましいと考えております」。
   - 財源・効果に疑問(八代尚宏、経済学): 「社会保険料に依存する、健康保険料に上乗せするということは、実は給付と負担がリンクするという前提の社会保険の原則に反するものでもあり」「児童手当等の金銭給付を増やすことによる少子化対策効果というのは実は乏しいんではないか」。真のコストは女性のキャリア喪失とする。
   - 現場・サービス重視(奥山千鶴子、子育てひろば全国連絡協議会): 「私は、現場の方から発言をさせていただきたいと思います」「誰でも使える普遍的なサービスが必要だというふうに思っています」。池本美香は海外制度との比較で保育・子どもコミッショナー等を論じる(別軸の可能性。本文の主張は未精査)。
7. **3 Voice構成案【AI案】**: V1=負担と給付に納得できない子育て前の共働き世帯、V2=産後の孤立を経験した母親、V3=保育・育児を担う現場の人。**実在の当事者発言は未確認**(全員専門家のため)。
8. **面白さ・普遍性**: 高い。ただし「支援金」「健康保険料上乗せ」は日本の制度名で、国固有の度合いが強い。生活語へ翻訳する前提(判定=灰色)。
9. **追加で必要な体験談**: 当事者の生活感(ガルちゃん・ママスタ=条件付き)、子を持たない/持てない側の声(未確保)。

### T4(参考のみ・推奨せず) 家事使用人は労働基準法で保護すべきか

- 情報源: 厚労省 労働政策審議会 労働条件分科会 第191回(2024-03-18)議事録 https://www.mhlw.go.jp/stf/newpage_39781.html(商用=◎・PDL1.0)。
- 【実】委員の発言: 鈴木委員「家事使用人の保護の必要性は理解しておりますが、法技術的な論点や実務上の難しさもあると認識しており」/同「西尾委員からの御発言は、労働基準法上の労働者に含めるべきとの御示唆だと思います」(=労働側の保護強化と、実務上の慎重論の対立)。個人の生活背景は無し。
- 判定: 労基法の適用範囲という**法令論が主題で国固有寄り**、委員は団体代表で人物像が出ない→**Family Y適性△・推奨せず**。審議会議事録の性格(労使公益の三者構成・個人の語りなし)を示す例として記録。

## §5 既存レジストリとの関係・他Lane候補・所見(判断はFable)

### 既存レジストリとの関係

| 区分 | 項目 |
|---|---|
| 既登録を更新提案 | Yahoo!ニュースコメント(D-9「アクセス不能・規約未評価」→02A準用で「規約上の除外寄り」+robots全面拒否を追記)。Quora(海外項「アクセス不能」→日本語版も403、robotsのAI学習禁止の意思表示を追記)。厚労省(D-10「パブコメ結果」→審議会議事録を同サイト・同PDL1.0の新コンテンツ種別として追記) |
| 既登録・再調査せず | 発言小町(除外)・知恵袋・ガルちゃん・ママスタ・5ch・増田・note・e-Govパブコメ(PDL1.0)・東京都/横浜市(許可要)。本書の補強案で「条件付き」源を参照しただけ |
| 新規(本Lane) | 国会会議録(NDL)、気候市民会議さっぽろ2020(環境省掲載)、Surfvote、PoliPoli、加古川Decidim、デジタル民主主義2030、NHKみんなでプラス(終了)、NADE、アゴラ、SYNODOS、朝日新聞、STORYS.JP、Change.org、こども若者★いけんぷらす、世田谷版気候市民会議、ABEMA TIMES、サイボウズ式、はてブ(未評価) |
| 新規除外(Lane内で確定) | NADE、アゴラ、朝日、STORYS、加古川、世田谷、Yahoo!ニュースコメント(準用) |

### 他Lane候補(名前のみ。本Laneでは調査せず)

台湾 JOIN / vTaiwan / Pol.is(市民討論)、Decidim海外インスタンス(Barcelona等)、気候市民会議の欧州事例(Lane b想定)、Kialo / DebateArt / DebateWise / Debating Europe / Debating Matters / Intelligence Squared(原文§2-3の例示。Lane a/b)。

### 所見

1. **国内の民間Debate系は商用で使える形で存在しない**: 目的に最も近い設計はSurfvote(論点記事→立場投票→理由コメント)だが、現在503で規約も討論本文も確認不能。メンテ明け後の1回再確認を推奨。NHKみんなでプラスは終了済み。PoliPoli・dd2030・Decidim国内は政治/自治体施策に特化(国固有除外)。
2. **規約が最も明確なのは公的記録**: 国会会議録(公式API・手続不要・解析等の権利制限を運営自ら例示)、厚労省(PDL1.0)、環境省掲載資料(PDL1.0、ただし第三者作成物は要確認)。民間の論壇・新聞・体験談サイトは営利禁止/無断翻案禁止/書面許諾のいずれかで落ちた。自治体報告書は掲載元次第(世田谷=禁止、札幌=環境省掲載で○)。
3. **公的記録の弱点=発言者が専門家**: 国会の参考人・公述人は大学教授・研究員・団体代表が大半(AI/ベーシックインカム/年金/介護の各検索で確認)。T1のように当事者参考人(障害児の親)を含む会議を選べば、実在の一人称が1名取れる。T2のように市民討論の報告書は肉声が取れるが属性が匿名。**人物の具体性(職業・家族・生活)は既登録の体験談系(ガルちゃん・ママスタ・note=条件付き)で補強する組合せが現実的**で、Debate系=論点・対立軸/体験談系=生活背景、の役割分担が有効。
4. **「3軸確認済み」**: T1(両立支援)とT2(気候市民会議)の2件のみ。T3は専門家発言のみ(Persona化は困難)。ユーザー例示テーマのうち、国内で実発言の3軸まで確認できたものはなく、「子どものSNS」は`いけんぷらす`に実テーマがあるが本体にアクセスできない。
5. **将来の量産での収集負荷・費用**: 国会会議録はAPI(無料・JSON)で`meeting`単位に全発言取得可能(1テーマ数リクエスト、間隔数秒)。審議会議事録・環境省PDFは1URL取得。収集費用は実質0円で、費用の本体は選別・Persona化のLLM工程(本調査では未測定)。
6. **規約上の残存リスク**: (a)国会会議録は「発言者に著作権・原則許諾要」と「情報解析等は不要」が併記=解釈依存(NDLへの確認推奨)。(b)PDL1.0源は「AI入力」の個別明文がない(登録簿D-10と同じ)。(c)札幌報告書は第三者作成物でPDL1.0が及ぶか未確認。(d)いずれも「逐語転載せず論点・立場のみ」運用が前提。
7. **Production採用前に必要なユーザー判断**(原文§7C・§8): 今回の判断候補は無し(新サイト・新収集方式は採用判断待ちとして記録のみ。登録簿の更新・採用可否は委任_02/Fable)。A=既判断: 登録≠継続利用承認(`SOURCE_REGISTRY_01.md` 冒頭、ユーザー決定③)。

## 付録 取得URL一覧(全件。時刻は2026-10-29 JST)

全文キャッシュはcommitしていない(権利上)。他に`curl`でPDF2本を取得: 07:40:30 こども家庭庁 活動報告書(令和7年度) `…/20260402_policies_iken-plus_katsudo-hokokusho_07.pdf`(200, 6.5MB)、07:41:35 気候市民会議さっぽろ2020報告書(200, 2.5MB)。HTTP=ERRはDNS解決失敗(推測URLが存在しない)。

| 時刻(JST,2026-10-29) | HTTP | URL |
|---|---|---|
| 07:30:18 | ERR | https://surfvote.polimill.jp/robots.txt |
| 07:30:20 | 200 | https://polimill.jp/ |
| 07:30:22 | ERR | https://polipoli-web.jp/robots.txt |
| 07:30:28 | 200 | https://polimill.jp/ |
| 07:30:31 | 200 | https://polimill.jp/ |
| 07:30:37 | 503 | https://surfvote.com/robots.txt |
| 07:30:39 | 503 | https://surfvote.com/ |
| 07:30:45 | 200 | https://polimill.jp/services/surfvote/ |
| 07:30:48 | 200 | https://polimill.jp/services/surfvote/ |
| 07:30:55 | 503 | https://surfvote.com/terms |
| 07:30:57 | 503 | https://surfvote.com/terms-of-service |
| 07:30:59 | 503 | https://www.surfvote.com/ |
| 07:31:01 | 503 | https://surfvote.com/issues |
| 07:31:09 | ERR | https://polipoli.jp/ |
| 07:31:11 | 200 | https://polipoli-web.com/ |
| 07:31:13 | ERR | https://www.polipoli.jp/ |
| 07:31:15 | 200 | https://www.nhk.or.jp/minplus/ |
| 07:31:17 | 200 | https://www.nhk.or.jp/robots.txt |
| 07:31:20 | 200 | https://jp.quora.com/robots.txt |
| 07:31:22 | 200 | https://www.nade.jp/ |
| 07:31:24 | ERR | https://kakogawa.decidim.jp/ |
| 07:31:32 | 200 | https://www.nhk.or.jp/minplus/ |
| 07:31:40 | 200 | https://polipoli-web.com/robots.txt |
| 07:31:42 | 200 | https://polipoli-web.com/terms |
| 07:31:44 | 200 | https://polipoli-web.com/rules |
| 07:31:56 | 200 | (検索・発見用) DuckDuckGo: Decidim+加古川 |
| 07:32:03 | ERR | https://decidim.kakogawa.jp/ |
| 07:32:05 | ERR | https://kakogawa-decidim.jp/ |
| 07:32:07 | ERR | https://www.decidim-kakogawa.jp/ |
| 07:32:09 | ERR | https://decidim.city.kakogawa.lg.jp/ |
| 07:32:11 | ERR | https://digital-democracy2030.go.jp/ |
| 07:32:13 | 200 | https://dd2030.org/ |
| 07:32:15 | 200 | https://www.city.kakogawa.lg.jp/ |
| 07:32:22 | 200 | https://dd2030.org/ |
| 07:32:29 | 200 | https://dd2030.org/ |
| 07:32:31 | 200 | https://dd2030.org/robots.txt |
| 07:32:37 | 200 | https://dd2030.org/idobata/case |
| 07:32:39 | 200 | https://dd2030.org/kouchou-ai/case |
| 07:33:11 | 200 | (検索・発見用) Bing: Decidim+加古川市 |
| 07:33:18 | 200 | (検索・発見用) Bing: Decidim+加古川市 |
| 07:33:28 | 200 | (検索・発見用) Bing: kakogawa.diycities.jp Decidim 議論 提案 |
| 07:33:31 | 200 | https://kakogawa.diycities.jp/ |
| 07:33:39 | 200 | https://kakogawa.diycities.jp/robots.txt |
| 07:33:42 | 200 | https://kakogawa.diycities.jp/pages/terms-of-service |
| 07:33:44 | 200 | https://kakogawa.diycities.jp/pages/terms-and-conditions |
| 07:33:58 | 403 | https://www.quora.com/about/tos |
| 07:34:07 | 200 | https://jp.quora.com/about/tos |
| 07:34:09 | 403 | https://jp.quora.com/ |
| 07:34:11 | 403 | https://www.quora.com/about/tos |
| 07:34:19 | 200 | https://news.yahoo.co.jp/robots.txt |
| 07:34:26 | 200 | https://www.change.org/robots.txt |
| 07:34:29 | 200 | https://www.change.org/policies/terms-of-service |
| 07:34:31 | 404 | https://www.change.org/l/jp/policies/terms-of-service |
| 07:34:52 | 200 | https://nade.jp/ |
| 07:34:54 | 200 | https://nade.jp/robots.txt |
| 07:35:01 | 200 | https://nade.jp/copyrights/ |
| 07:35:03 | 200 | https://nade.jp/news/archives/4410/ |
| 07:35:12 | 200 | https://kokkai.ndl.go.jp/robots.txt |
| 07:35:15 | 200 | https://kokkai.ndl.go.jp/ |
| 07:35:23 | 200 | https://kokkai.ndl.go.jp/api.html |
| 07:35:39 | 404 | https://www.ndl.go.jp/jp/use/web_rules.html |
| 07:35:41 | 404 | https://www.ndl.go.jp/jp/use/web_rules.html |
| 07:35:47 | 200 | https://kokkai.ndl.go.jp/api.html |
| 07:35:53 | 200 | https://kokkai.ndl.go.jp/api.html |
| 07:35:55 | 200 | https://kokkai.ndl.go.jp/api.html |
| 07:36:03 | 200 | https://www.ndl.go.jp/jp/sitepolicy/terms.html |
| 07:36:18 | 200 | https://kokkai.ndl.go.jp/api/meeting_list?any=ヤングケアラー 参考人&maximumRecords=5&recordPacking=json |
| 07:36:31 | 200 | https://kokkai.ndl.go.jp/api/speech?any=ヤングケアラー&speakerRole=参考人&maximumRecords=8&recordPacking=json |
| 07:36:45 | 200 | https://kokkai.ndl.go.jp/api/meeting?issueID=121314889X01620240523&recordPacking=json |
| 07:36:59 | 200 | https://agora-web.jp/robots.txt |
| 07:37:01 | 200 | https://synodos.jp/robots.txt |
| 07:37:07 | 200 | https://agora-web.jp/ |
| 07:37:10 | 200 | https://synodos.jp/ |
| 07:37:16 | 200 | https://agora-web.jp/sitepolicy |
| 07:37:23 | 200 | https://synodos.jp/about/ |
| 07:37:26 | 200 | https://synodos.jp/privacy-policy/ |
| 07:37:28 | 200 | https://synodos.jp/ |
| 07:37:42 | 200 | https://www.asahi.com/robots.txt |
| 07:37:45 | 404 | https://www.asahi.com/shimbun/about/info/terms.html |
| 07:37:47 | 200 | (検索・発見用) Bing: 朝日新聞 声 投稿 読者 利用規約 生成AI 禁止 |
| 07:37:55 | 200 | https://www.asahi.com/ |
| 07:38:03 | 200 | https://www.asahi.com/policy/copyright.html |
| 07:38:29 | 200 | (検索・発見用) Bing: site:mhlw.go.jp 労働政策審議会 労働条件分科会 議事録 連続勤務 労働者代表 使用者代表 |
| 07:38:37 | 200 | https://www.mhlw.go.jp/stf/shingi/shingi-rousei_126969.html |
| 07:38:39 | 200 | https://www.mhlw.go.jp/stf/shingi/shingi-rousei_126969.html |
| 07:38:46 | 200 | https://www.mhlw.go.jp/stf/newpage_39781.html |
| 07:39:03 | 200 | https://times.abema.tv/robots.txt |
| 07:39:05 | 200 | https://storys.jp/robots.txt |
| 07:39:13 | 200 | https://storys.jp/ |
| 07:39:21 | 200 | https://storys.jp/terms |
| 07:39:29 | 200 | https://b.hatena.ne.jp/robots.txt |
| 07:39:54 | 200 | https://www.cfa.go.jp/policies/iken-plus |
| 07:40:01 | 200 | https://www.cfa.go.jp/policies/iken-plus |
| 07:40:09 | 200 | https://www.cfa.go.jp/policies/iken-plus/katsudo-hokokusho |
| 07:40:12 | 200 | https://www.cfa.go.jp/policies/iken-plus/katsudo-hokokusho |
| 07:40:21 | 200 | https://www.cfa.go.jp/copyright-policy |
| 07:40:54 | 403 | https://ikenplus.cfa.go.jp/ |
| 07:41:05 | 200 | (検索・発見用) Bing: 気候市民会議 報告書 市民の意見 無作為抽出 日本 |
| 07:41:15 | 200 | (検索・発見用) Bing: 気候市民会議 報告書 参加者の意見 無作為抽出 |
| 07:41:26 | 200 | (検索・発見用) Bing: 気候市民会議 報告書 参加者の意見 無作為抽出 |
| 07:41:51 | 200 | https://www.env.go.jp/ |
| 07:42:00 | 200 | https://www.env.go.jp/ |
| 07:42:07 | 200 | https://www.env.go.jp/mail.html |
| 07:42:30 | 200 | https://www.city.setagaya.lg.jp/ |
| 07:42:33 | 404 | https://www.city.setagaya.lg.jp/robots.txt |
| 07:42:39 | 200 | https://www.city.setagaya.lg.jp/02002/7723.html |
| 07:43:13 | 200 | https://times.abema.tv/ |
| 07:43:19 | 200 | https://abema.tv/about/terms |
| 07:43:21 | 404 | https://abema.tv/about/terms-of-use |
| 07:43:23 | 404 | https://times.abema.tv/about/terms |
| 07:43:31 | 503 | https://surfvote.com/ |
| 07:43:33 | 200 | https://note.com/surfvote |
| 07:44:06 | 200 | https://kokkai.ndl.go.jp/api/meeting?issueID=121314260X01520240521&recordPacking=json |
| 07:44:39 | 200 | https://kokkai.ndl.go.jp/api/meeting?issueID=122105206X00620260421&recordPacking=json |
| 07:44:54 | 200 | https://kokkai.ndl.go.jp/api/speech?any=子ども SNS 規制&speakerRole=参考人&maximumRecords=10&recordPacking=json |
| 07:45:04 | 200 | https://kokkai.ndl.go.jp/api/speech?any=生成AI 雇用&speakerRole=参考人&maximumRecords=12&recordPacking=json |
| 07:45:07 | 200 | https://kokkai.ndl.go.jp/api/speech?any=AI 規制 参考人&speakerRole=参考人&maximumRecords=12&recordPacking=json |
| 07:45:10 | 200 | https://kokkai.ndl.go.jp/api/speech?any=ベーシックインカム&speakerRole=参考人&maximumRecords=12&recordPacking=json |
| 07:45:12 | 200 | https://kokkai.ndl.go.jp/api/speech?any=週休3日&speakerRole=参考人&maximumRecords=12&recordPacking=json |
| 07:45:15 | 200 | https://kokkai.ndl.go.jp/api/speech?any=選択的週休3日&speakerRole=参考人&maximumRecords=12&recordPacking=json |
| 07:45:28 | 200 | (検索・発見用) Bing: 賛成 反対 理由 意見 投票 社会問題 議論プラットフォーム 日本 市民 |
| 07:45:39 | 404 | https://policies.hatena.ne.jp/terms |
| 07:45:52 | 200 | https://cybozushiki.cybozu.co.jp/ |
| 07:45:54 | 200 | https://cybozushiki.cybozu.co.jp/robots.txt |
| 07:45:56 | 200 | https://greenz.jp/ |
| 07:46:03 | 200 | https://cybozushiki.cybozu.co.jp/ |
| 07:46:05 | 200 | https://cybozushiki.cybozu.co.jp/ |
| 07:46:14 | 200 | https://cybozushiki.cybozu.co.jp/ |
| 07:46:20 | 200 | https://cybozushiki.cybozu.co.jp/ |
| 07:46:31 | 200 | https://dd2030.org/policies/terms |
| 07:46:46 | 200 | https://www.mhlw.go.jp/chosakuken/index.html |
| 07:46:48 | 200 | https://www.mhlw.go.jp/robots.txt |
| 07:46:57 | 200 | https://www.digital.go.jp/resources/open_data/public_data_license_v1.0 |
| 07:47:44 | 200 | https://kokkai.ndl.go.jp/api/speech?any=介護&speakerRole=公述人&maximumRecords=12&recordPacking=json |
| 07:47:46 | 200 | https://kokkai.ndl.go.jp/api/speech?any=子育て&speakerRole=公述人&maximumRecords=12&recordPacking=json |
| 07:47:48 | 200 | https://kokkai.ndl.go.jp/api/speech?any=非正規&speakerRole=公述人&maximumRecords=12&recordPacking=json |
| 07:47:51 | 200 | https://kokkai.ndl.go.jp/api/speech?any=年金&speakerRole=公述人&maximumRecords=12&recordPacking=json |
