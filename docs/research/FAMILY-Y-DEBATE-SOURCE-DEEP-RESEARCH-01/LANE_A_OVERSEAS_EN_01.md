# LANE_A_OVERSEAS_EN_01(Lane a: 海外・英語圏のDebate/Discussionプラットフォーム。調査のみ・提案であり正式仕様/Production採用ではない)

管理ID: FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 / 委任_01a / 作成・確認日: 2026-10-29。LLM(API)呼出0・費用0円(取得はHTTP GETのみ、本文は調査者が通読。LLMによる要約・補完なし)。
ユーザー原文(`docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`)§2〜§5・§9を全文読んだうえで作成。
商用利用Statusは「想定用途(公開された実在の意見を読み取り、論点・立場・価値観を参考に独自3 Persona・一人称原稿をAIで生成し、商用英語学習ラジオとして提供。逐語転載なし)」に対する調査者の読み取りであり、法的保証ではない。**新サイト・新収集方式のProduction採用はユーザー判断待ち**(登録≠承認)。

## 0. 結論(先に)

- 評価対象は約35サイト(規約本文を読んだ15、robots/到達性のみ約15、前回判定済みで参照のみ5)。**◎ 1件・○ 3件**。◎/○の4サイトはすべて討論本文まで読んだ。
- **Family Y適性が◎の情報源は本Laneにはなかった**(○=Tildes・Lemmy、△=EA Forum・Parlia)。実際の討論で3軸を確認できたのは「若者のSNS禁止」(T1)と「"なんとかなる"で子どもを持ってよいか」(T2)の2テーマ。UBI(T3)・保育無償化(T4)は議論が評論家寄り/エッセイ形式でPersonaの職業・家族・感情が薄い。
- 大手の商用フォーラム/メディア(Hacker News・Substack・NYT・Pew・AgingCare・Kialo・Intelligence Squared・AllSides)は、「個人・非商用のみ」「自動収集/AI利用禁止」「書面同意必須」のいずれかを明記しており、**禁止・契約必須サイトで数を補っていない**。商用で使える見込みがあるのは小規模・非営利/オープンライセンス運営のコミュニティに集中していた。
- 前回(`docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/{OVERSEAS_SOURCES_01,TERMS_REVIEW_01}.md`)との差: Hacker Newsは「未確認」→今回「除外」(YC利用規約のCommercial Use・scraping・derivative works禁止を逐語確認)。Lemmyは前回「低評価(雑談中心)」→今回「○」で、社会ニュース連動スレッドと価値観スレッドに良質な長文あり(スレッドにより差が大きく、通読による選別が必要)。

| 推奨(◎/○) | 商用 | Family Y適性 | 一言 |
|---|---|---|---|
| EA Forum | ◎ | △ | 投稿がCC BY 4.0(翻案可)。ただし書き手がEAコミュニティ内の分析者で、Personaが評論家化しやすい |
| Tildes | ○ | ○ | 長文・自己開示つき。SNS禁止スレッドで3軸確認。コミュニティが小さく新議題は少なめ |
| Lemmy(lemmy.world等) | ○ | ○(スレッド依存) | 100〜300件規模の議論。親の実体験断片が出る。口調が荒い/政治化/話題が逸れるスレッドあり |
| Parlia | ○ | △ | For/Against/Mixedの論点整理に便利。投稿は学生エッセイ中心で体験談は薄い |

## 1. 探索方法・範囲

- 発掘経路: (1)委任文の出発点(Kialo/DebateArt/DebateWise/Intelligence Squared/Debating Matters)、(2)委任文の例示(ProCon.org、CreateDebate、IDEA Debatabase、Munk Debates、Oxford Union、Hacker News再確認、Stack Exchange系[前回判定参照]、Quora、Pol.is、Ethics case、Opposing Views、AllSides、Debate Island、Argüman、Guardian[参照]、NYT、Medium、Substack、Metafilter、実体験コミュニティ[AgingCare・Alzheimer's Society forum・Carers UK・Bogleheads・MMM forum・Ask a Manager・BabyCenter・Netmums])、(3)調査者の既知知識からの新規発掘(Tildes、EA Forum、LessWrong、Lemmy.world、Parlia、DebateGraph、Braver Angels、Living Room Conversations、Pew)。Web検索ツールは使えないため、発掘は既知サイトのrobots.txt/規約/到達性プローブで行った(**発掘が既知サイトに偏る限界あり**)。
- 取得量: 総取得168件(単発curl)。うち討論本文を通読したのは14スレッド(Tildes 3、EA Forum 3、Lemmy 5、Parlia 2、DebateWise 1)。全URL・時刻は§6。
- 取得方法: 規約・robots.txt・該当ページの単発curl(クロール・ログイン・一括収集・回避なし)。UAはブラウザ互換文字列に`research-manual-read`を付与。Lemmyのみ公式の公開JSON API(認証なし、読取のみ)。Cloudflare等のbot遮断(Debating Matters/ProCon/Metafilter/Quora/Bogleheads/Living Room Conversations/ev.org)は**回避せず「アクセス不能=未確認」**とした。
- **規約・robots上の逸脱(自己申告)**: (a)Kialoのrobots.txtは`User-agent: *`で`Disallow: /`(列挙botのみ許可)。規約確認のため`/tos`(404)・`/terms`・トップの3ページを単発取得した(討論ページは取得していない)。(b)Lemmy.worldのrobots.txtは`Crawl-delay: 60`。API 20回のうち大半を60秒間隔より速く実行した(07:43〜07:50、5スレッド分+検索)。以後Lemmy呼出は停止。(c)Ask a Manager等はrobotsのContent-SignalでAI学習不可・ClaudeBot拒否を示す。調査者は規約確認のためトップ/about/privacyの数ページを取得したが、そのコンテンツは評価対象にせず推奨にも載せていない。
- 前回成果の再利用(再調査せず参照のみ): Reddit(ユーザー決定により対象外)・Guardian・Mumsnet・Stack Exchange・Mastodon。

## 2. サイト評価表

商用Statusの凡例はユーザー原文§3。確認日はすべて2026-10-29。引用は短く原文英語のまま。

### 2-1 推奨(◎/○)

| サイト | 国・地域 | 商用 | 規約URL・条項逐語・確認日 | Family Y適性(原文§4の5項目) | 主なテーマ | 3軸の取りやすさ | Personaの作りやすさ | 注意事項 | 国固有除外判定 |
|---|---|---|---|---|---|---|---|---|---|
| **EA Forum**<br>forum.effectivealtruism.org | 国際(英語。運営EVFは英国法人) | **◎** | https://forum.effectivealtruism.org/termsOfUse (EA Forum Addendum, 2022-10-31) 2.2: "you agree that you are doing so in accordance with, and on the basis that it will be made available to users on, the terms of the Creative Commons — Attribution 4.0 International — CC BY 4.0." 2.1: license "to produce, reproduce and share Adapted Material for any purposes". robots.txt: `Crawl-Delay: 2`、AI botの個別拒否なし | **△**: テーマ○(子を持つか・気候・寄付・動物・AI) / 3軸独立性△〜○ / Persona具体性△(個人体験の投稿はあるが少数) / 実在意見の豊富さ○(1投稿数十件) / ラジオ適性△(功利主義的な枠組みの分析口調) | 子どもを持つ決断、気候と出産、育児と仕事復帰、動物福祉、AIリスク | △〜○ | △(投稿者の生活は具体的だが、コメント投稿者は分析者) | 帰属表示(CC BY)が必要。EVF一般Terms(effectivealtruism.org/terms-and-conditions、ev.org)は本文を取得できず(JS描画/Cloudflare)、自動取得条項は**未読**。AddendumはTermsに優先すると明記。EA内輪の前提が強く日本人リスナーには説明コストが高い | 除外せず(議論の中身は普遍) |
| **Tildes**<br>tildes.net | カナダ(非営利法人Spectria)・英語 | **○** | https://docs.tildes.net/policies/terms-of-use 「You retain copyright and ownership of any of your own content … you grant us a non-exclusive license to store, display and distribute that content in the context of operating the site」「it may be archived, copied, or otherwise duplicated by any other user or automatic system that is able to access it」。AI/スクレイピング/商用の禁止条項なし。https://tildes.net/robots.txt 冒頭コメント "In general, scrapers are welcome if they are collecting data for informational uses (such as search engines) and maintain a reasonable rate of scraping." "Tildes data is not a resource to be mined and sold."(User-agent *は`/login`のみDisallow、GPTBot等は個別Disallow) | **○**: テーマ○ / 3軸○(SNS禁止で確認) / Persona△〜○(親・職業・国の自己開示あり) / 豊富さ○(40〜100件/スレッド) / ラジオ適性○(IT・プライバシー寄りの語り) | SNS禁止、プライバシーと年齢確認、人生相談、AI、仕事 | ○(T1で3軸確認) | △〜○ | robots冒頭の"mined and sold"は規約本文ではないが運営の意図。想定用途(読取と独自原稿化。データを売る/マイニングする用途ではない)との線引きが必要。会員制投稿で規模が小さく、新議題の頻度は低い。投稿者はハンドル名のみ | 除外せず |
| **Lemmy(lemmy.world)** | 国際(フェデレーション型。運営=Fedihosting Foundation) | **○** | https://legal.lemmy.world/tos/ を通読: AI・スクレイピング・商用・著作権許諾の条項なし(Bot規定=自作bot運用ルールのみ)。robots.txt: `Disallow: /search/`等、**`Crawl-delay: 60`**、AI bot個別拒否なし。投稿の著作権は規約に規定がなく、投稿者に残ると解するのが自然だが明文はない。フェデレーション先(sopuli.xyz、lemmus.org等)は別規約 | **○**(スレッド依存): テーマ○ / 3軸○ / Persona○(親の実体験の断片) / 豊富さ◎(100〜300件) / ラジオ適性△〜○(罵倒語・政治化・話題の逸脱あり) | SNS禁止、子どもを持つ条件、UBI、AI、職場、スマホ規制 | ○(T1・T2で3軸確認) | ○(断片的) | 規約が「何も言わない」型の○で**許諾が明示されているわけではない**。Crawl-delay 60のためAPI取得は1スレッド約3呼出=3分以上かかる設計。ニュース連動スレッドはオフトピックへ流れやすい(T5)。c/childfree、c/fuck_ai等コミュニティによる偏り | 除外せず |
| **Parlia**<br>parlia.com | 英国(Jadala社) | **○** | https://www.parlia.com/terms-of-service (2026-06更新) 「You own what you post. By posting on Parlia you grant us a worldwide, non-exclusive, royalty-free license to display, distribute, and store your contributions as part of operating the service」「The Parlia name, design, and aggregate datasets are ours. You may link to and quote Parlia pages freely with attribution.」AI/スクレイピング/商用の禁止条項なし。robots.txt: `Allow: /`、`/settings/`・`/search`のみDisallow | **△**: テーマ○(715トピック) / 3軸○(For/Against/Mixed構造) / Persona×(体験談なし、学生エッセイ形式) / 豊富さ△(1論点4〜7件) / ラジオ適性△ | 動物園、保育無償化、投票義務、ジェンダー等(米英の文化戦争系が多い) | ○(3区分の構造はあるが、独立した利害の3軸とは限らない) | ×〜△ | 投稿は約5年前(2021頃)が中心。UK/US色の強いトピックあり。**論点整理・価値観分布の参照用**。票の属性別集計(性別・政治・世代)はログイン要で未取得 | 個別判断(UK保育制度は固有背景だが議論軸=費用負担・親の責任は普遍→除外せず) |

### 2-2 除外・未確認・参照のみ(理由の要約は§3)

| サイト | 商用 | 根拠(要点・逐語は短く) | 調査内容 |
|---|---|---|---|
| Kialo | 除外 | https://www.kialo.com/terms "you may use our export functionality to download debates for private use. Please don't use other means to monitor or copy any material on Kialo, either manually or through automated means (i.e., scraping), without prior written consent." robotsは`*`が`Disallow: /` | 規約のみ(討論ページ未取得) |
| Intelligence Squared | 除外 | https://www.intelligencesquared.com/terms-conditions "The Site, the App and the Content are for your personal, non-commercial use only" / "not to use automated means, including spiders, robots, crawlers, data mining tools … to download data". robots: ClaudeBot等Disallow、`ai-train=no`。議論者は専門家=評論家型。なお当該ページ本文に医薬品販売URLの混入あり(サイト改ざん・流用の疑い、運用品質も不安) | 規約・robots |
| Hacker News | 除外(前回=未確認から変更) | https://www.ycombinator.com/legal/ Commercial Use: "you agree not to display, distribute, license … create derivative works from … for any commercial purposes"; Site Content: "you will not engage in or use any data mining, robots, scraping or similar data gathering or extraction methods"。公式API(GitHub README)に商用許諾の記載なし | 規約・robots・API README |
| Substack | 除外 | https://substack.com/tos '"Crawls," "scrapes," or "spiders" any page … (through use of manual or automated means)' / "Copies or stores any significant portion of the content" | 規約 |
| NYT | 除外 | https://help.nytimes.com/hc/en-us/articles/115014893428-Terms-of-Service 2.1 "intended for your personal, non-commercial use"; 生成AI・RAGへのContent利用を禁止 | 規約 |
| Pew Research Center | 除外 | https://www.pewresearch.org/terms-and-conditions/ "engage in unauthorized spidering, "scraping," or harvesting of content"; Contentの再公表は書面許諾要 | 規約 |
| AgingCare(A Place for Mom) | 除外 | https://www.agingcare.com/aboutus/termsofuse "solely for your personal use"; 禁止行為に "Using the Sites for commercial purposes." | 規約(Eldercare Forum含む) |
| AllSides | 除外 | https://www.allsides.com/terms-of-use 原文コンテンツは会社の排他的財産。robots: `Content-Signal: search=yes, ai-train=no, ai-input=no`(AI入力を明示拒否)。ニュース偏向格付けで個人の声ではない | 規約・robots |
| IDEA Debatabase | 除外(2023アーカイブ規約) | idebate.orgは2026-10-29時点で接続タイムアウト(旧サイトはアーカイブ、idebate.netが現行)。アーカイブ版T&C(web.archive.org/web/20231206194819/https://idebate.org/terms-conditions) "you may not copy, reproduce, distribute, modify, display, republish, transmit, repost, or otherwise use the content … without prior written permission"。debatabase.orgは無関係のカジノ広告サイト | アーカイブT&C |
| LessWrong | 未確認 | 利用規約はPDF(MIRI)で本調査では未読。FAQ内の利用者コメントは「ユーザーは著作権を保持」と解釈(公式根拠ではない)。Family Yは抽象議論中心で優先度低 | robots・FAQ |
| Ask a Manager | 未確認 | 独立した利用規約なし(`/terms-of-use`は403)、フッター"Copyright © 2007 - 2026 Ask A Manager. All rights reserved."。robotsはCloudflare Content Signal(`ai-train=no`)とClaudeBot拒否。**職場テーマの品質は高い見込みだが、規約から許諾を読み取れず本文は評価していない**。運営照会の対象(Fable判断) | robots・トップ・about・privacy |
| Medium | 未確認 | https://policy.medium.com/medium-terms-of-service-9db0094a1e0f "Please don't copy, upload, download, or share content unless you have the right to do so."(条項不明確)。robotsはClaudeBot等のAI botをDisallow。1記事=1視点でPersona補助程度 | 規約・robots |
| DebateWise | 未確認 | 利用規約ページなし(`/terms-of-use`404)。フッター"Copyright © 2026. DebateWise. All Rights Reserved."。robotsは全許可 | 規約探索・討論1本読了(T6) |
| Munk Debates | 未確認 | 利用規約を発見できず(フッター"© 2026 Munk Debates. All rights reserved.")。専門家ディベートで評論家型 | トップ・privacy・robots |
| Oxford Union | 未確認 | 規約URLが特定できず(推測URL1回のみ)。登壇者=評論家型 | 簡易 |
| Debating Matters | 未確認(アクセス不能) | robots/トップがHTTP 403(bot遮断)。回避せず | 到達性のみ |
| ProCon.org(Britannica) | 未確認(アクセス不能) | `britannica.com/procon`へ転送、Cloudflareチャレンジ(HTTP 403)。回避せず | 到達性のみ |
| DebateArt | 未確認(実質終了) | debateart.comは2026-10-29時点で無関係のイタリア語カジノ比較サイトへ301転送 | 到達性のみ |
| CreateDebate | 未確認(実質終了) | トップが`/lander`(GoDaddyパーキング)へ転送、規約ページなし | 到達性のみ |
| DebateGraph | 未確認 | 規約を発見できず。robotsがGPTBot/ClaudeBot等のAI botをDisallow | robots・トップ |
| Metafilter / Ask MetaFilter / Quora / Bogleheads / Living Room Conversations | 未確認(アクセス不能) | いずれもCloudflare等でHTTP 403(bot遮断)。回避せず | 到達性のみ |
| Mr. Money Mustache forum | 未確認 | 規約未取得。robotsにCloudflare Content Signal(`ai-train=no`)+ClaudeBot拒否 | robots |
| Alzheimer's Society forum | 未確認(推奨不可) | robots.txtがClaude-User等ほぼ全AI botを明示Disallow。規約は未読 | robots |
| Carers UK forum | 未確認 | forum.carersuk.orgの規約は未取得 | robots・トップ |
| BabyCenter / Netmums | 未確認 | 推測した規約URLが404で特定できず | 簡易 |
| Slashdot / Ethics Bowl・Philosophy case collections | 未調査 | Slashdotはコメント中心でIT偏重(HNと重複見込み)。事例集は実在発言者を含まずFamily Yの構造に合わない(推測URL1回は不達) | — |
| Pol.is | 未確認 | トップ/規約がJS描画のみ(2,180バイト)。公開レポートは市民討論=01bの範囲 | robots・トップ |
| Argüman / Debate Island / Opposing Views | 未確認 | Argümanはトルコ語(01b候補)。Debate Island=HTTP 401、Opposing Views=HTTP 403 | 到達性のみ |
| (参照のみ) Reddit / The Guardian / Mumsnet / Stack Exchange / Mastodon | 前回判定 | Reddit=ユーザー決定により対象外、Guardian・Mumsnet=規約上の禁止、Stack Exchange=条件付き(補助・低優先)、Mastodon=不適。再調査せず | `TERMS_REVIEW_01.md`等 |

## 3. 除外・未確認の理由(まとめ)

1. **除外(明確な禁止・書面同意必須)**: Kialo(コピー/スクレイピングは書面同意)、Intelligence Squared(個人・非商用のみ+自動取得禁止)、Hacker News(商用・派生物作成・スクレイピング禁止)、Substack(手動を含むクロール/コピー禁止)、NYT(個人・非商用+AI利用禁止)、Pew(スクレイピング禁止+再公表は書面)、AgingCare(個人利用+商用禁止)、AllSides(AI入力を明示拒否+独占権)、IDEA(書面許諾が必要)。
2. **未確認(規約が読めない・条項不明確・アクセス不能)**: DebateWise、Munk、Oxford Union、LessWrong、Ask a Manager、Medium、DebateGraph、Debating Matters、ProCon、Metafilter、Quora、Bogleheads、Living Room Conversations、MMM forum、Alzheimer's Society forum、Carers UK、BabyCenter、Netmums、Pol.is、Debate Island、Opposing Views。**いずれも○にしていない**。Ask a Managerは職場テーマの品質が高そうだが、許諾が読めずAI系robotsが拒否的なため運営照会が先(判断はFable)。
3. **実質終了・乗っ取り**: DebateArt(カジノ広告へ転送)、CreateDebate(ドメインパーキング)、IDEA Debatabase(現行サイト接続不能、debatabase.orgは無関係のカジノ広告)。
4. **自動収集だけ禁止かの検討(代替取得)**: Kialo・Substackは手動コピー/閲覧中のコピーも禁止のため、代替取得でも解消しない。HN・NYT・AgingCareは閲覧は許容でもAI入力・商用・派生物作成が禁止のため解消しない。

## 4. テーマ候補(実際に本文まで読んだもののみ)

凡例: 「確認」=実在投稿を読んだ事実(投稿者はハンドルでなくコメントID/属性で記録、逐語は短く)。「AI案」=調査者のPersona構成案で実在意見ではない。

### T1 16歳未満のSNS利用を法律で禁止すべきか(3軸確認済み)
1. 問い: 子どものSNS利用を年齢で一律に法律禁止するか、親の同意・プラットフォーム設計規制・親用ツールで対処するか。
2. 情報源: Tildes(○)・Lemmy(○)。
3. 原文: Tildes https://tildes.net/~tech/1rn3/how_europe_is_gearing_up_to_follow_australias_teen_social_media_ban (2025-12-09、50件取得) / https://tildes.net/~tech/1uzn/fines_doubled_as_teens_outsmart_australias_world_first_social_media_ban (2026-07-05、42件) / Lemmy https://lemmy.world/post/39943391 (2025-12-09、287件中240件取得)。
4. 商用Status: Tildes ○ / Lemmy.world ○。
5. Family Y適性: ○(テーマ◎、3軸○、Persona△〜○、豊富さ◎、ラジオ適性○。論理的賛否に加え、親の実体験の断片がある)。
6. **実際に確認した異なる主張**:
   - A(親・禁止支持/条件付き容認): Tildes #gx9t「親が個々に判断すると同調圧力が生じる。同僚の子が親の禁止に反してSnapchatを作っていた。禁止は"拒む親"に根拠を与える」(親)/ #gx97「禁止も親同意制も悩ましい。親同意制だと子が内集団/外集団に分かれ、親も流される」(迷う当事者)/ #gxhq「小2の娘に通話・テキスト・音声本だけのスマホを渡し、SNSは高校以降に」(親、段階制)/ Lemmy「(豪州の親)子どもは学校・iMessage・FaceTime・公園で友達と過ごし、禁止の影響はほぼない」(score 0、2025-12-10)/ Lemmy「15歳の娘が、友達がSnapchatで18歳と判定されたため仲間外れになりそう」を伝えるGuardian引用コメント(score 7)。
   - B(自由・プライバシー派): Lemmy score 27「"子どものため"は建前で、実名・生体情報を当局に預ける慣行を正常化する口実」/ Tildes #gx93「親の同意を法で要求する意味は何か、13歳確認チェックは既にある。世論をなだめつつ監視を強める立法」/ Tildes tt1は豪州の通信会社Optusの身分証漏えいを例に、ID提出の危険を論じる書き手が複数。
   - C(設計・規制・親ツール派): Tildes #gx9c「年齢制限でなく中毒性そのものを規制(線形フィード強制・透明性)」/ #gxf7「端末側のペアレンタルコントロールを標準化」/ #gxa8「問題は子どもが"村"(親・親戚)の目から離れる設計」/ Lemmy score 15「既に親用ガードレールはある。政府は無料のペアレンタルツールを」。
   - D(経験世代): Lemmy score 36「監視のないネットで育ったが、今のアルゴリズム漬けとは別物。今の子どもにあの環境はもう無い」。
7. **3 Voice Persona構成案(AI案)**: ①共働きで小学生高学年〜中学生を育てる親(同調圧力に悩み禁止を歓迎する、または豪州で"影響は小さい"と実感する側) ②プライバシー重視の30代IT職(ID提出を警戒し禁止を管理強化の入口と見る) ③設計派(元教育関係者などで、年齢でなくアルゴリズムと親ツールの問題とみる)。
8. 面白さ・普遍性: 日本でもSNS年齢規制・学校のスマホルールが議論になり自分事化しやすい。「善意の規制が監視の入口になるか」という価値観の対立が成立。
9. 追加で必要: 10代本人の声(今回ほぼ確認できず)、日本の親の実感(国内Lane)、禁止後の実運用(年齢確認の具体)。Lemmyは罵倒語の除外前処理が必要。

### T2 「なんとかなる」で子どもを持ってよいか(3軸確認済み)
1. 問い: 経済基盤・保育が整わないまま子どもを持つのは無責任か、「なんとかなる」の覚悟でよいか、問題は個人でなく制度か。
2. 情報源: Lemmy(○、価値観スレッド)+EA Forum(◎、計画型の決断記)。
3. 原文: Lemmy https://lemmy.world/post/51969913 (c/childfree、2026-09-16、197件中139件取得) / EA Forum https://forum.effectivealtruism.org/posts/YYnjHt5YzuHSH7oRR/kids-or-no-kids (2023-11-12、31件、投稿本文の冒頭+コメント読了) / https://forum.effectivealtruism.org/posts/p8gnRNLxDDp7Bc5Mu/should-you-have-children-despite-climate-change (2022-05-03、コメント3件抜粋のみ)。
4. 商用Status: Lemmy ○ / EA Forum ◎。
5. Family Y適性: ○(テーマ◎、3軸○、Persona○、豊富さ○、ラジオ適性○)。Lemmyは感情的、EAは分析的という温度差がそのまま対比に使える。
6. **実際に確認した異なる主張**:
   - A(責任・事前準備派): Lemmy score 7「子どもは任意で、最も重い障害の子が生まれても100%支えられないなら持つべきでない」/ EA本文(夫婦とも週50〜60時間労働。2年・計数百時間をかけ30分刻みの1日の時間割まで作り、「Yes if xyz」で合意、結論は"持つ"、乳児4か月)。
   - B(「なんとかなる」・経験派): Lemmy score 0「親が"なんとかなる"と産んでくれたから今の私がいる。裕福さを資格にするのはエリート主義」/ Lemmy score 0(母親)「妊娠中に夫の会社が大量解雇、業界を離れ見習いになり厳しい数年だったが子どもは元気。"なんとかする"姿勢が一番大事」/ Lemmy score 7(母親・子が遺伝学者)「若い頃と30代後半の子が各々いて、健康・知能に差は感じない。年上の子は私が学校に通い転職する様子を見て育った」。
   - C(制度・個人責任論への反発/社会変革): OP追記「貧しい人は産むなという話ではなく、誰にも基本的な保育が賄われる制度が必要」/ Lemmy「生殖は基本的人権。3〜6か月で困窮する社会を放置して個人を責めるな」(score -2)/ 反論「宗教的理由等で意図して多産する貧困家庭もあり、貧困が世代間で再生産される」(score 2、2026-09-18)/ EAコメント「親の転居が多く愛着の問題が残った。転居の際に子の意向を考慮しない影響は大きい」「フルタイムのナニー/オペアに育てられたのは自分にとって良い経験だった」「子の福祉が"功利主義では小さな考慮"というなら前提が不自然では」。
7. **Persona構成案(AI案)**: ①計画型の共働き夫婦の片方(家計・時間割を作ってから決める) ②「なんとかなる」で産んだ母親(夫の転職・見習い期間を経て今は安定) ③制度変革を求める20〜30代の子無し志向(個人責任論に違和感)。
8. 面白さ・普遍性: 少子化・教育費・保育という日本の中心課題に直結。「準備できるまで待つ」vs「やってみて道を作る」の価値観の対立が自然。
9. 追加で必要: 日本の具体(教育費・待機児童・実家の支援)。国内Laneの子育て投稿で補強(商用Statusは別途確認)。c/childfreeは出産に否定的な偏りがあり、「親の声」はコメントで補う必要。

### T3 ベーシックインカムは必要か(AIによる雇用代替を含む)(3軸確認済み、ただし評論家寄り)
1. 問い: UBIは将来の仕組みになるか。AIで仕事が減ったとき収入をどう支えるか。
2. 情報源: Lemmy(○)。
3. 原文: https://lemmy.world/post/50982979 (c/asklemmy、2026-08-22、196件中165件取得)。別スレ https://lemmy.today/post/53191782 (AI代替と収入、126件)は**見出しのみ**(本文未読)。
4. 商用Status: Lemmy ○。
5. Family Y適性: △〜○(テーマ◎、3軸○、Persona△、豊富さ◎、ラジオ適性△。**登場人物が評論家になりやすい**)。
6. **確認した異なる主張**: 賛成(行政コスト削減・起業の解放、score 2)/ 財政懐疑(UK福祉総額との試算で総額が国内総生産の約半分に達し、財政破綻か極めて低額になる、score 2)/ 「UBIよりユニバーサルサービス(無料の医療・法律支援・修理など)が先」(score 21)/ インフレ懸念(10人の顧客の例、score 1)/ 左派からの不安(労組・ストを弱め消費経済を延命、score 1)/ 米国在住者の視点(2027年にメディケイド要件で低所得層が脱落する見通し、score 1)。
7. **Persona構成案(AI案)**: ①福祉の制約で働き方を選べない非正規の人 ②財政に懐疑的な自営業者 ③AIで仕事が変わると感じる中堅会社員(職業・家族の具体は実在意見に乏しく、AI創作に頼る部分が大きい)。
8. 面白さ・普遍性: 日本でもAI・賃金・年金の関心が高い。ただし語りが理念寄り。
9. 追加で必要: 給付/失業/介護離職を経験した人の体験談(商用Status確認済みの別源)。このテーマ単独でのPersona構築は非推奨。

### T4 保育は無料にすべきか(3区分確認、体験談なし)
1. 問い: 保育は無償にすべきか、有償で所得制限か、親が準備すべきか。
2. 情報源: Parlia(○)。
3. 原文: https://www.parlia.com/o/childcare-should-be-free (4件、約5年前)。構造確認のため https://www.parlia.com/o/zoos-should-be-closed (7件)も読了。
4. 商用Status: ○。 5. Family Y適性: △。
6. **確認した異なる主張**: Against(「親は養育費を準備してから産むべき。無料でなく安く」)/ Mixed(「必要性の高い人に所得制限つきで。保育士の待遇を下げない」)/ For(「英国の保育費は年6,000〜7,000ポンドで家計を圧迫」)。いずれも学生エッセイ形式で、職業・家族・感情の具体は薄い。
7. Persona案: 作らない(AI創作で3軸化しない)。T2の補助論点としてのみ使用。
8. 普遍性: 費用負担と親の責任はT2と同じ軸。 9. 追加で必要: 保育利用者の体験談。

### T5(参考・失敗例) 学校のスマホ禁止/職場の出社義務(Lemmyニュース連動スレッド)
- https://lemmy.world/post/41056130 (NYの学校スマホ禁止後、アナログ時計が読めない生徒。172件取得)はコメントが時計の歴史・物理・雑談へ流れ、教師・保護者・生徒の具体的な意見はほぼ出なかった。https://lemmy.world/post/42600323 (Ubisoft解雇+出社義務。136件取得)はゲーム推薦と企業批判が大半で、出社義務への職場の意見は数件(score 90のリモート勤務者の1件など)。**見出し・コメント数だけで「3軸確認」としてはならない例**。Family Y素材には不採用。

### T6(参考・不採用) 職場でのSNS禁止(DebateWise)
- https://debatewise.org/3574-social-networking-sites-should-be-banned-at-the-workplaces/ を読了。Yes/Noの短い反論の連鎖で2軸のみ(AI創作による3軸化はしない)。規約も未確認。採用不可。

### 補強用の体験談系(商用Status確認済みのもの)
- Tildes(○)の人生相談 https://tildes.net/~life/1s22/advice_needed_getting_an_elderly_parent_set_up_with_a_home_health_aide (2026-01-06、18件、米国の退役軍人向け保険Tricare前提で制度説明が多い)。介護の場面に使える具体: 「母が介助者を拒んだが、父が"私が母を助けるために助けが要る"と言い換えて受け入れた」(#h39q)、「ホスピスの介助者リストを活用し、自費で在宅介護も追加」(#h3is)。介護テーマの**体験談の補強**には使えるが、討論の対立軸はない。
- EA Forum(◎)の育児タグ(https://forum.effectivealtruism.org/topics/parenting)に「My experience of returning to work after having a baby」「Parenting things I wish I could tell my past self」等の個人体験投稿がある(前者はコメントのみ読了で本文は未取得、後者は**見出しのみ**)。

## 5. 他Lane候補・所見(判断はFable)

- 他Lane候補(名前のみ。調査せず): 01b=Argüman(トルコ語の議論構造サイト、2026-10-29に到達可)、Pol.is公開レポート、Braver Angels、Living Room Conversations(bot遮断)、The Conversation/Aeon(CC BY-ND)、Global Voices(CC)、regulations.gov等の公開コメント、Debating Europe。01c=該当なし。
- 所見1: 商用で読める見込みがあるのは**大手でなく小規模・非営利・オープンライセンス運営**の場に偏る。大手の商用サイトは規約が揃って個人・非商用+自動収集/AI禁止。
- 所見2: 「3軸が実際に出る」のは、**社会ニュースに親・当事者が自己開示しながらコメントするスレッド**(T1)と**価値観を問うスレッド**(T2)。UBIのような理念テーマは評論家化し、ニュース連動スレッドはオフトピックへ逸れる(T5)。本文通読による選別が必須で、見出し・コメント数での自動選別は危険。
- 所見3: 10代本人・日本の当事者・職業の細部(Persona要素)は、本Laneの○源でも薄い。国内Lane(体験談系)との併用が前提。
- 所見4(判断候補、分類D: 真に新しい判断): Ask a Manager(職場テーマの有力候補)の運営照会を行うか。→ Fableが委任_02で扱うか判断(本Laneは照会していない)。
- 所見5(既存SSOT整合): 本Laneの結果がSOURCE_REGISTRY_01.mdと食い違うのは「Hacker News: 未確認→除外」のみ。レジストリ更新は委任_02。
- 規約上の残存リスク: (a)Lemmy/Tildesは「何も禁じない」型の○で、AI利用の許諾は明示されていない。Tildes robots冒頭の"not a resource to be mined and sold"との整合(想定用途は読取と独自原稿化)。(b)EA Forumは一般Terms(自動取得条項)が未読。(c)Lemmyはフェデレーションにより他インスタンス規約がスレッドごとに異なる。(d)量産時の取得負荷: Lemmyは`Crawl-delay: 60`で1スレッド約3分以上、Tildes/Parliaは単純HTML、EA Forumは`Crawl-Delay: 2`でHTML内のRSCペイロード解析が必要。
- 将来の量産コスト感: いずれもHTTP取得0円。読解(token)が主コスト。Lemmy APIはコメント一覧が0.3〜2.2MB/スレッドと重い。

## 6. 取得URL一覧(2026-10-29 07:29〜07:50 JST、168件、単発curl)

規約・robots・到達性: kialo.com(robots, /tos, /terms, /)、debateart.com(robots, /terms, /)、debatewise.org(robots, /terms-of-use, /, /privacy-policy, /about-us, /contact-us)、intelligencesquared.com(robots, /terms-and-conditions, /terms-conditions, /privacy-policy, /)、debatingmatters.com(robots)、procon.org(robots)、createdebate.com(robots, llms.txt, /terms, /, /lander)、munkdebates.com(/terms-of-use, robots, /, /privacy/)、idebate.org(接続不能×3)、debatabase.org(/, robots)、archive.org wayback availability×2、web.archive.org idebate.org(トップ, /terms-conditions)、idebate.net、ycombinator.com/legal、news.ycombinator.com(robots, newsguidelines, newsfaq)、github HackerNews/API README、docs.tildes.net(terms-of-use, privacy-policy)、tildes.net/robots.txt、lesswrong.com(termsOfUse, robots, /, /faq, /tos, /privacy)、forum.effectivealtruism.org(termsOfUse, robots, /, topics/parenting, topics/veganism)、effectivealtruism.org/terms-and-conditions、ev.org(terms-of-use, terms)、askamanager.org(robots, /terms-of-use, /, /privacy-policy, /commenting-policy, /about, /faq)、pol.is(robots, /home, /tos)、allsides.com(robots, /terms-of-service, /terms-of-use)、agingcare.com(robots, /, /terms-of-use, /terms, /terms-and-conditions, /terms-of-service, /legal, /aboutus/termsofuse)、metafilter.com(robots, /faq.mefi, /)、forum.mrmoneymustache.com/robots.txt、bogleheads.org(robots, ucp terms)、lemmy.world(/legal, robots)、legal.lemmy.world/tos/、debateisland.com、arguman.org、opposingviews.com、debate.org(DNS不能)、policy.medium.com ToS、medium.com/robots.txt、substack.com/tos、quora.com/about/tos、pewresearch.org/terms-and-conditions、slashdot.org/faq、help.nytimes.com ToS、oxford-union.org/terms-and-conditions、babycenter.com/terms-of-use、netmums.com/terms-and-conditions、britannica.com/terms、scu.edu ethics cases、forum.alzheimers.org.uk/robots.txt、carersuk.org(robots, /)、parlia.com(/, robots, /terms, /privacy, /about, /topics, /t/childcare, /t/children)、debategraph.org(/, robots)、braverangels.org(/, robots)、livingroomconversations.org(/, robots)。

討論本文(読了): tildes.net/~tech/1uzn…、/~tech/1rn3…、/~life/1s22…、/~talk(一覧)+検索5件、forum.effectivealtruism.org/posts/YYnjHt5YzuHSH7oRR(本文+コメント)・/p8gnRNLxDDp7Bc5Mu(コメント抜粋)・/5zKfuzDxf9pjvcHxA(コメントのみ)、lemmy.world API(post 39943391・50982979・51969913・41056130・42600323のコメント一覧、検索12件)、parlia.com/o/zoos-should-be-closed・/o/childcare-should-be-free、debatewise.org/3574-social-networking-sites-should-be-banned-at-the-workplaces/。
(取得本文の全文は転載・commitしていない。調査者のローカル作業領域のみ。)
