# LANE_C_OVERSEAS_NEW_01: 海外の新規情報源の発掘(公的意見募集・当事者コミュニティ・オープンライセンス系)

管理ID: FAMILY-Y-SOURCE-FINAL-SHORTLIST-01 / 委任_01c / 作成: 2026-10-29(Sonnet Worker)/ 調査のみ・LLM API 0円・Production変更なし。
到達Status: 候補としての調査結果(VALIDATED前段)。採否・最終20件の選定はFable/ユーザー判断。
並行Lane: 01a(既存候補の再評価)・01b(国内新領域)。本Laneは両者と重複する対象を再評価しない(担当外は名前のみ)。

## 凡例(ユーザー原文§3の基準に準拠)

- 商用AI利用: ◎=商用利用が明示的に認められ、想定するAI利用(論点抽出・要約・翻案して独自原稿化)も規約上許容と判断できる / ○=明示許可なし、明確な禁止も確認していない(**「AI利用が許可されている」ではない**) / 除外=禁止・契約必須・適法取得不可。**運営者規約と投稿者著作権は分けて記載**。
- テーマ選定性・ペルソナ性: ◎/○/△。ペルソナ性は**実際に読んだ投稿・議事録・提出意見**に基づく(読んだURLを明記)。AIが想像で補えるという理由では評価しない。
- 取得規則: robots.txt/Crawl-delay遵守、手動相当の単発取得(各取得の間隔3秒以上、Crawl-delay指定時はその値)、自己申告UA(`eigo-radio-research/1.0`)、制限回避なし。403/チャレンジ/robots Disallowは回避せず「アクセス不能」または「取得不可」と記録。確認日はすべて2026-10-29。

## §1 発想した探索領域と方法(偏り点検)

### 1-1 方法と制約

- Web検索ツールが使えないため、「ライセンスが明確な公的・オープン系から逆引きする」「当事者の一人称が読める場所を領域として発想する」「アジアの現地語コミュニティを現地ルールで判定する」の3方針で領域を発想し、robots/規約/実投稿を直接取得して判定した。未知の優良サイトの取りこぼしがあり得る(後述の死角)。
- 既判定(Reddit・HN・Kialo・Quora・NYT・Substack・Pew・AllSides・IDEA・Naver・gutefrage・Straits Times、およびLane aが再評価するUK議会/Grand Débat/Polis/EA Forum/Climate Assembly/Global Voices/Tildes/Lemmy/Parlia/Stack Exchange/The Conversation等、Mumsnet、Carers UK)は再調査していない。

### 1-2 発想した探索領域(新規10領域)

| # | 探索領域 | 発想の理由 | 実際に当たったサイト |
|---|---|---|---|
| 1 | 議会が公開する「意見募集への市民の提出意見」の一括公開ファイル | 提出意見は一人称の当事者体験が多く、議会側がライセンスを明示することがある | Scottish Parliament(選定)、Oireachtas・Canada下院・NZ・豪州連邦議会・州議会 |
| 2 | 規制・諮問委員会の公開調査(inquiry)への市民提出意見 | 政策論争と生活者の声が同居し、CC BY明記の機関がある | 豪州Productivity Commission(選定)、Scottish Government Citizen Space |
| 3 | 議会公聴会の速記録(証人=当事者・専門家) | 米国連邦政府著作物は公有。証人の一人称証言が読める | GovInfo(選定) |
| 4 | オープンリサーチデータ(CC0の質的インタビュー逐語録) | 研究者が匿名化・公開した実在の一人称語りがCC0で置かれる | Harvard Dataverse(選定)、Zenodo(robotsで/api・/search禁止のため不使用)、OSF(/api禁止)、UK Data Service(登録要) |
| 5 | オープンライセンスの百科事典コミュニティ | CC BY-SAで商用可が明記 | Wikipedia/Wikimedia(補助) |
| 6 | 台湾・タイ・インドネシア・韓国の現地語コミュニティ | 生活密着型の掲示板を現地規約で判定 | PTT・Pantip(選定)、Kaskus(除外)、Dcard(403)、Clien/DCInside/Instiz/FMKorea/Pann |
| 7 | 患者・当事者体験プラットフォーム | 介護・医療の一人称体験 | Care Opinion(除外)、HealthUnlocked(除外)、Healthtalk/HEXI(未確認)、Mayo Clinic Connect/Inspire/Patient.info(403) |
| 8 | 消費者苦情データベース(公的オープンデータ) | 金融・債務の一人称苦情が公有データで出ると発想 | CFPB Consumer Complaint Database(本文が既に無く除外) |
| 9 | 開発者・技術者ブログ基盤 | 働き方・キャリアの一人称体験 | Dev.to(除外)、Hashnode(AI/マーケ記事混在で不適) |
| 10 | 市民提案・請願プラットフォーム | 公共政策の市民提案と省庁回答 | 台湾JOIN(未確認)、Your Priorities(JS描画で未確認) |

### 1-3 偏り点検と是正

- 初期の偏り: 公的・英語圏・ライセンス明確系に寄った(領域1〜3)。是正として領域6(アジア現地語)・7(当事者体験)・9(開発者ブログ)・10(請願)を追加した。
- 残る偏り(正直な開示): ◎/○が得られたのは「公的機関が公開する文書」「CC0のオープンデータ」に集中し、**自由参加型の英語圏生活密着掲示板には◎/○がゼロ**(Netmums・HealthUnlocked・Gransnet・MSE Forum・Care Opinion・Dev.to=除外、Student Room/Mayo Clinic Connect/Inspire=403)。生活密着型の確保には、現地語コミュニティ(PTT・Pantip)または運営者への個別許諾が現実的な選択肢になる。
- 死角(未調査・名前のみ記録): 米国各州議会の公聴コメント、自治体議会、Healthwatch(英)、Senedd(ウェールズ)、ICPSR/UKDS(登録必須)、Nordic協議(regjeringen.noは403)、EU Have Your Say(Lane B判定済)、Mass Observation、口述史アーカイブ(StoryCorps・LOCは403)、ラテンアメリカ・アフリカ・インド・中東のコミュニティ。
- AI生成投稿の混入(新しい所見): 評価中にAIが書いた投稿が実際に混在していた。Wikipedia Reference Deskの回答に"Compiled with automated assistance by Casper, an AI agent"、PTT Salary板で「這篇是AI生成的嗎?」の指摘、Hashnode #career記事は"her actual numbers"形式の架空事例記事。ペルソナ素材として使うには「実在の一人称か」の選別が必要。

### 1-4 取得実績・逸脱の開示

- 総HTTP取得は概算230回(大半はrobots.txtと規約ページ、実投稿は11サイトで合計約40ページ)。Bing/DuckDuckGoは未使用。
- 取得手順上の特記:
  1. MSE Forumの利用規約本体は`www.moneysavingexpert.com`が当UAに403を返したため、**Internet Archive(web.archive.org)の2026-07-22スナップショット**から読んだ。archive.orgは1回HTTP 429を返したため45秒待ってから再取得した(連打なし)。Harvard Dataverseの一般規約も同様にWayback経由(support.dataverse.harvard.eduは403)。
  2. CFPBの一括CSVは公式ダウンロードURLに**Range指定(先頭1.5MB)の単発取得**でヘッダ行のみ確認(全量は取得していない)。CFPB検索APIは単発で約6回。
  3. `assets.pc.gov.au`はrobots.txtが403のため、「robots取得不能=制限記述なし」として提出意見PDFを2本取得した(うち1本は403で取得できず再試行せず)。`pc.gov.au`本体のrobots(Crawl-delay 2、/how-to-make-a-submission等のみDisallow)は遵守。
  4. GovInfoの公聴会はサイトマップから抽出したIDで21本の見出しを取得(大きいHTMLを先頭のみ表示。各3秒間隔)。
  5. Scottish Parliamentの公開意見xlsx(3.76MB)を1回だけ取得してローカル解析した。Harvard Dataverseは検索API2回・データセットAPI1回・逐語録ファイル1回。
- 遵守事項: robots Disallowのパス(`consult.gov.scot`・`yourviews.parliament.scot`の`view_respondent`、Zenodo `/api` `/search` 等)は取得していない。PTTのGossiping板(18歳確認クッキーが必要)は取得していない。

## §2 評価表(◎/○のみ。9件)

### 2-1 一覧(概要)

| # | サイト | 公式URL | 国・言語 | 種別 | 商用AI利用 | テーマ選定性 | ペルソナ性 | 量産適性 |
|---|---|---|---|---|---|---|---|---|
| C1 | US Congressional hearings(GovInfo) | https://www.govinfo.gov/ | 米・英 | 議会公聴会速記録(証人の証言) | ◎(運営者=公有表示。証人提出資料の第三者著作権に注記) | ○ | ○(当事者証人の回は◎) | ○ |
| C2 | Productivity Commission(豪) 公開調査への提出意見 | https://www.pc.gov.au/ | 豪・英 | 諮問委員会の公開調査と市民提出意見 | ○(委員会作成物=CC BY 4.0 で◎、提出意見=著作権は提出者) | ○ | ◎(読んだ2本とも一人称の経験と立場) | ○ |
| C3 | Scottish Parliament 意見募集の公開回答・委員会記録 | https://www.parliament.scot/ | 英(スコットランド)・英 | 議会Call for Viewsの一括公開ファイル | ○(議会作成物=Scottish Parliament Copyright Licenceで商用可◎、回答=第三者著作権) | ○ | ◎(読んだ回答は当事者体験。ただし意見が一方に偏る) | ○ |
| C4 | Harvard Dataverse(CC0の質的インタビュー逐語録) | https://dataverse.harvard.edu/ | 米(世界の研究者)・主に英 | オープンリサーチデータ | ◎(CC0。参加者同意の範囲に注意) | △〜○(学術テーマ。選別が必要) | ◎(逐語の一人称語りを実読) | △ |
| C5 | PTT(批踢踢) | https://www.ptt.cc/ | 台湾・繁体字中国語 | 匿名掲示板(Marriage・Salary等の板) | ○(運営者規約に第三者利用条項なし。robotsは`ai-train=no, use=reference`) | ◎ | ◎(実読)。AI生成投稿が混在 | ○ |
| C6 | Pantip | https://pantip.com/ | タイ・タイ語 | Q&A/相談型掲示板 | ○(規約ページに著作権・商用・スクレイピング条項なし。robots制限は広告パスのみ。根拠は弱い) | ◎ | ○(質問者の一人称は実読。コメント欄は動的で未実読) | △ |
| C7 | gov.scot/Citizen Space 協議の分析報告 | https://consult.gov.scot/ | 英(スコットランド)・英 | 政府協議の分析報告(政府作成) | ◎(Open Government Licence v3.0)。個別回答は別問題(robots禁止) | ◎ | △(集計と少数の引用のみ) | ○ |
| C8 | Wikipedia/Wikimedia(議論ページ・Reference Desk) | https://en.wikipedia.org/ | 世界・英 | 百科事典の編集議論・質問回答 | ◎(CC BY-SA 4.0。商用可。派生はShare-Alike) | △ | △(Reference Deskは雑学Q&A。意見・議論は規則で禁止) | ○ |
| C9 | Hashnode | https://hashnode.com/ | 世界・英 | 開発者ブログ基盤 | ○(投稿者が所有。規約に商用禁止なし) | △(開発者・キャリア) | △(#careerの実読記事は架空事例のマーケ記事) | ○ |

読み方: C1〜C6は「ペルソナ素材が実際に読めた」もの。C7〜C9は商用AI利用の条件は良いがペルソナ性が低く、補助的位置づけ(最終20件に入れるかはFable判断)。

### 2-2 根拠の詳細(サイト別)

#### C1 US Congressional hearings(GovInfo)

- 規約: https://www.govinfo.gov/about/policies「Public Domain & Copyright Notice」(2026-10-29)。"Title 17, Section 105, United States Code, provides that: Copyright protection under this title is not available for any work of the United States Government" / "By virtue of the foregoing, public documents can generally be reprinted without legal restriction. However, Government publications may contain copyrighted material which was used with permission of the copyright owner. Publication in a Government document does not authorize any use or appropriation of such copyright material without consent of the owner."(要旨: 政府著作物は公有で制限なく再掲可能。ただし許諾を得て掲載された第三者著作物は別途同意が必要)。
- robots: https://www.govinfo.gov/robots.txt は`/search/`等の管理パスのみDisallow。`/content/pkg/CHRG-.../html/*.htm`は許可。サイトマップ(`/sitemap/CHRG_2024_sitemap.xml`、2024年分921件)を公式提供。
- ◎の根拠と範囲制約(内部記録): 運営者(GPO)側は公有と商用再掲可を明示。ただし**民間証人の提出陳述書は「政府職員が職務で作成した著作物」ではないため著作権が証人に残る可能性**がある。Family Yでは証言の逐語転載ではなく、論点・体験の事実の抽出と翻案原稿化に限るのが安全。
- テーマ選定性○: 2024年のサイトマップから等間隔に抽出した18見出し(`CHRG-118hhrg54711`等)は、中小企業基準、VA人事、COVID憲法、狩猟・釣り、AUKUS、予算、パイプライン安全、国土安全、NLRB、VA予約待ち、サイバー、山火事、イエメン、**公立学校教員の待遇(Senate HELP)**、**民間学生ローン**等。生活に直結する回は一部で、大半は予算・外交・規制。見出しだけでは選別できないため、タイトル/委員会で絞る前処理が必要。米国制度の文脈は強いが、教員不足・学生ローン・VA医療の待ち時間は日本のリスナーにも通じる。
- ペルソナ性○〜◎(実読): https://www.govinfo.gov/content/pkg/CHRG-118shrg57244/html/CHRG-118shrg57244.htm(Senate HELP委員会「公立学校教員の短期・長期の課題」)。証人John Arthur(ユタ州の2021 Teacher of the Year、Title I校の担任)の陳述書は一人称で、"A few years ago, my mother was diagnosed with terminal cancer... even facing death, my mother still didn't want her daughter dating a teacher."(母が末期がんでも、娘が教員と付き合うことは望まなかった=職業への敬意の低さの体験談)。証人Keyes(パラプロフェッショナル)の質疑応答は賃金・教員養成プログラムの実体験。Cassidy上院議員の冒頭陳述は個人の学校体験("one of them kept me afterwards and drove me home")と、読解力・欠席率という別の立場(データ志向)。同一会議内に「待遇と敬意を訴える現場教員」「賃金に悩む支援職」「学力・出席データを重視する議員」の3立場が取れる。別会議(`CHRG-118shrg62265`、民間学生ローン)は証人が専門家(政策担当・研究者・法学教授)中心で当事者の語りは薄く、**回により当事者性に大きな差**がある。
- 量産適性○: 静的HTML、サイトマップ、バルクデータあり。1会議が10万〜20万字級のため、取得後の要約・抽出が前提。更新頻度は議会開会中は日次。取得費用0円。
- 制約メモ: 国固有除外の対象外(政党・選挙区でなく教育・労働・医療・金融が主題の回に限る)。

#### C2 Productivity Commission(豪州) 公開調査への提出意見

- 規約: https://www.pc.gov.au/copyright/(2026-10-29)。"The copyright work is licensed under a Creative Commons Attribution 4.0 International licence, with the exception of the Commonwealth Coat of Arms, the Productivity Commission logo, and content supplied by third parties. You may download, copy, communicate and adapt the material, as long as you attribute the work to the Productivity Commission..." / "Copyright in submissions made to Commission public inquiries and studies resides with the author, not the Commission and will remain on the Commission's website indefinitely as public documents."(要旨: 委員会作成物はCC BY 4.0で翻案可。提出意見の著作権は提出者に残り、公文書として恒久公開)。
- robots: https://www.pc.gov.au/robots.txt `Crawl-delay: 2`、`/how-to-make-a-submission`等のみDisallow。提出意見PDFのホスト`assets.pc.gov.au`はrobots.txtが403(§1-4に開示)。
- ◎/○の整理: 委員会作成の報告書=◎(CC BY 4.0)。**提出意見は○**(運営者は公開を明示するが再利用許諾はなく、著作権は提出者)。総合は○。
- テーマ選定性○: 調査「Childcare and early childhood learning」には初回提出468件(https://www.pc.gov.au/inquiries/completed/childcare/submissions)。PCの調査は育児・高齢者ケア・メンタルヘルス・住宅・働き方等、生活に近い題材が多いが、1調査=1テーマで題材の入れ替わりは年数件。
- ペルソナ性◎(実読): sub006(Bindi Mira-Bateman、2013-12-16、https://assets.pc.gov.au/inquiries/completed/childcare/submissions/initial/submission-counter/sub006-childcare.pdf)は自営業の母親で、ナニー/オーペア/ファミリーデイケア/保育所を使い分けた経験を語り、"The common perception that only the very wealthy have nannies is simply not true in our case."と述べてナニーへの給付がないことを訴える。sub012(幼児教育教員かつ将来の親、https://assets.pc.gov.au/inquiries/completed/childcare/submissions/initial/submission-counter/sub012-childcare.pdf)は"Certificate III educators earn less on average than cleaners with no qualifications."と、提供者側の立場から賃金と質基準を主張。利用者(親)・従事者(教員)・事業者(提出一覧に施設名義の提出も多数)という**異なる3立場が同一調査から取れる**。
- 量産適性○: 静的HTMLの一覧とPDF(pypdfで抽出可)。1調査に数百件。提出の公開期間後の追加は少なく、継続的な新題材の供給は調査の開始頻度に依存。
- 制約メモ: 提出意見は固有名・個人情報を含む。**著作権は提出者**のため、逐語転載せず、論点・体験の事実の再構成に限る。読んだ提出意見は2013年のもので、題材の鮮度は調査ごとに確認が必要。

#### C3 Scottish Parliament(意見募集の公開回答・委員会記録)

- 規約: https://www.parliament.scot/about/copyright「Scottish Parliament Copyright Licence」(2026-10-29)。"You are free to: copy, publish, distribute and transmit the information; adapt the information; exploit the Information commercially and non-commercially, for example, by combining it with other Information, or by including it in your own product or application." / Exemptions: "This licence does not cover: personal data in the Information ... third-party rights the SPCB is not authorised to license"(要旨: 議会作成情報は商用・翻案可。ただし個人データと議会が許諾する権限のない第三者の権利は対象外)。
- robots: `/sitecore`等の管理パスのみDisallow。
- ◎/○の整理: 議会が作成した記録・分析=◎。**市民の提出意見=第三者権利のため○**。意見募集システムの規約 https://yourviews.parliament.scot/terms_and_conditions/ は「投稿者に権利が残り、議会とDelibには掲載目的の限定ライセンス」(By submitting Content to the Service, you grant us and the operator of the Service (Delib Ltd) a world-wide, royalty-free, and non-exclusive license to reproduce, modify, adapt and publish the Content solely for the purpose of displaying, distributing and promoting the Service)。総合は○。
- 実投稿(一括公開ファイル): 「Assisted Dying for Terminally Ill Adults (Scotland) Bill」の公開回答7,236行のxlsx(https://www.parliament.scot/-/media/files/committees/health-social-care-and-sport-committee/assisted-dying-for-terminally-ill-adults/published-responses-to-the-assisted-dying-for-terminally-ill-adults-scotland-bill-consultation-(1).xlsx)。賛否の内訳(Q1a): Strongly oppose 6,672 / Fully support 387 / Partially support 63 / Neutral 58 / Partially oppose 55。読んだ回答の例: 賛成側「私は退職した緩和ケア看護師。3年前にパートナーを癌で看取った。最高の緩和ケアでも最後の1週間は苦しかった。緩和ケアは苦痛を和らげるが無くせない」(I am a retired palliative care nurse. 3 Years ago my partner died of cancer in my care...)/ 賛成側「母を看取った経験から…」(Having gone through this with my mother...)/ 反対側「2002年に母がステージ4の大腸癌で余命6か月未満と言われたが、緩和ケアで自然な最期まで周囲に必要とされた」(In 2002 my mother was terminally ill with stage four bowel cancer...)、反対側「94歳の父が病院で死にたいと言ったが、水分補給と休養ケアで気持ちが変わった」。**同じ題材で、当事者体験に基づく賛成・反対・慎重の3立場を実在の声で構成できる**。ただし回答の約92%が反対(組織的な呼びかけの影響とみられる)で、母集団を代表しない。
- 署名・個人情報: 回答には名前列があり、議会側で`[REDACTED]`処理済みの箇所もある。Family Yでは実名・属性を使わず匿名化する前提。
- テーマ選定性○: 議会のCall for Viewsは安楽死、介護者の休息権、学校の携帯電話制限等、普遍的な題材が多い。スコットランド固有の制度が前提の回もあるが、題材が普遍的なら可。
- 量産適性○: 1回のCall for Viewsにつき1つのxlsx/PDFが公開され、静的ダウンロード可。頻度は委員会ごとに年数件〜十数件。個別回答のWeb閲覧(`view_respondent`)はrobotsで禁止されているため、**議会が公式に置く一括ファイルのみを使う**。
- 制約メモ: 提出者の権利は残る。逐語引用でなく事実・論点の再構成。センシティブな主題(安楽死・死別)の取り扱い方針は別途の注意事項。

#### C4 Harvard Dataverse(CC0の質的インタビュー逐語録)

- 規約: https://support.dataverse.harvard.edu/harvard-dataverse-general-terms-use(Wayback 2026-09版経由。直接取得は403)。"Unrestricted User Submissions – Any User Submissions that are published with a default CC0 default public domain dedication waiver agreement." / "As both a registered User and an unregistered Guest, you are able to download publicly available Content from Harvard Dataverse."(要旨: 制限なしの投稿は既定でCC0。登録なしでも公開コンテンツをダウンロード可能)。API利用は別規約(https://dataverse.org/best-practices/harvard-api-tou)で、**取得が403のため本文未読**。
- ライセンス実確認: データセット`doi:10.7910/DVN/GDUOVS`(COVID-19初期のリスク認識インタビュー、18本)のAPIで`license: CC0 1.0`、ファイルはすべて非制限。
- ペルソナ性◎(実読): `GDUOVS`のファイル6360583(Levi、31歳、フィラデルフィアの救急医・研修医)。「最初はパンデミックとは思わず自分の関心事ではなかった(I never expected it to become a pandemic)。イタリアの状況を知って医療体制への負荷を悟り、強い不安を覚えた」という時系列の一人称の語り。質問者(研究者)と回答者の問答形式でタイムコード付き。
- テーマ選定性△〜○: 学術研究の副産物のため題材は研究テーマ次第(移民の患者の視点、宗教教育教員の恐れと希望、介護者、COVID等)。生活・仕事題材は一部。継続的に新しい題材は出るが、探索と選別が要る。
- 量産適性△: 検索APIで`transcripts`等の語で絞れる(例: `"transcripts" AND (parents OR teachers OR workers) AND interviews` が328件)。データセットごとにライセンス欄の確認が必要(CC0以外のカスタム条件もあり得る)。ファイルはdocx/pdf。
- 制約メモ(重要): **CC0は著作権の放棄であり、インタビュー参加者の同意範囲とは別**。研究目的の同意の下で匿名化された語りを商業ラジオ原稿の素材にする点は、倫理審査上の同意範囲を超え得る。逐語引用は避け、匿名化の維持・個人特定の回避を前提とする。

#### C5 PTT(批踢踢)

- 規約: https://www.ptt.cc/index.ua.html「使用者條款 2.0.1」(2026-10-29)。1-2「資料一經上載或輸入本站(除私人信件、水球紀錄外),視為您已同意本站為非營利無償使用、修改、重製、公開播送、散布、發行、公開發表,並得轉授權為非營利使用。」(要旨: 投稿者は**サイトに**非営利の無償利用と非営利での転授権を与える。第三者による商用利用・機械的収集の可否には言及なし)/ 1-4「在不涉及攻訐、侮辱、商業用途、假冒他人、扭曲文義或違反法規條件下,您同意本站其他回覆您文章之作者,可於本站內引用您所刊登之內容」(要旨: 引用はサイト内の返信者が対象)。https://www.ptt.cc/about.html に「非營利開放社群平台」「絕不商業化、絕不營利」。
- robots: https://www.ptt.cc/robots.txt は`User-agent: *`に`Content-Signal: search=yes,ai-train=no,use=reference`と`Allow: /`。ClaudeBot・anthropic-ai・Claude-Web・GPTBot・CCBot・Google-Extended・Bytespider等のAI学習系を名指しで`Disallow: /`(Cloudflare管理設定)。「EU DSM指令第4条に基づく権利留保」の注記あり。
- ○の理由と注意: 運営者規約に第三者の商用・AI利用を禁止/許諾する条項はなく、投稿の著作権は投稿者に残る。robotsは**AI学習(ai-train)を拒否**し、参照利用(use=reference)を許す書き方だが、`use`の公式定義は未確認。原稿への取り込みは「論点・体験の事実の抽出と再構成」に限り、学習用途には使わない運用が前提。名指しされたAI botのUAを名乗る取得は不可(自己申告UAで`*`の許可に従う)。
- テーマ選定性◎: 板が細分化(Marriage=夫婦・育児・家計、Salary=転職・賃金・退職、WomenTalk、MomBaby等)。生活課題が毎日更新される。
- ペルソナ性◎(実読):
  - https://www.ptt.cc/bbs/marriage/M.1793123683.A.CFD.html(2026-10-28「Re: 老公藉育嬰假期間去讀書」)。投稿者は自身の結婚経験から「私は妻に理解されないのが前提。理解を求めるより、自分が何を望むかを問え。実家に戻り育児を手伝ってもらい…」と助言。推・噓欄には「それは夫が中年の独身生活を手に入れるだけ(離婚と変わらない)」という懐疑、「妻の安心感は自分で得るもの」という反論、「意志の固い方の方法で暮らすことになる」など、**夫婦の役割・安心感・離婚リスクをめぐる3つ以上の立場**がID付きで読める。
  - https://www.ptt.cc/bbs/Salary/M.1791960251.A.61A.html(2026-10-14「37歲大齡女考研究所失利」への返信)は投資のすすめに傾いた長文で、噓・「這篇是AI生成的嗎?」と指摘されている。**板と時期により実在の語りとAI生成が混在**。
- 量産適性○: 静的HTML、取得が軽い。Cloudflare管理のため頻度過多で遮断され得る(自己申告UA・3秒間隔で通常取得は可能だった)。言語は繁体字中国語のため翻訳・要約の工程が必要。18禁板(Gossipingなど)は18歳確認が必要で対象外。
- 制約メモ: 投稿者権利は残る。プライバシー(台湾個資法)に配慮し、IDや特定情報は使わない。

#### C6 Pantip

- 規約: https://pantip.com/about/tos(「กฎ กติกา และมารยาท」)、/about/privilege(会員の権限)、/about/privacy(2026-10-29に3ページとも読了)。内容は投稿禁止事項・運用ルールで、**著作権の帰属・商用利用・スクレイピング・第三者利用に関する条項は見つからなかった**。フッターは「© 2026 Internet Marketing co., ltd」。
- robots: https://pantip.com/robots.txt は広告パス`/ads.php`と一部SEO botのみDisallow。
- ○の理由と注意: 明確な禁止を確認できない状態のみ(積極的許諾はない)。著作権表示は運営会社名のみで、投稿者との関係は条文で確認できていない。○の中でも根拠が弱い。
- テーマ選定性◎: 実読した一覧の題名は、健康保険の請求トラブル(https://pantip.com/topic/44264553)、退職時の積立基金(https://pantip.com/topic/44270069)、家族の遺伝性疾患への不安(https://pantip.com/topic/44264996)など、生活実務の相談が広い。
- ペルソナ性○: https://pantip.com/topic/44264996 は質問者が家族の死の経緯と結婚前の不安を一人称で詳細に語る(タイ語)。**コメント欄は動的読み込みで未実読**のため、立場の異なる3人の声は未検証。
- 量産適性△: タイ語。コメントはJavaScript経由のため静的取得では本文のみ。
- 制約メモ: 現地語の翻訳誤差、個人情報(健康・家族)の扱い。

#### C7 gov.scot/Citizen Space 協議の分析報告

- 規約: https://www.gov.scot/crown-copyright/ "You may use and re-use the information featured on this website (not including logos) free of charge in any format or medium, under the terms of the Open Government Licence."。各ページのフッター"All content is available under the Open Government Licence v3.0, except for graphic assets and where otherwise stated"(政府作成物はOGL v3.0で商用再利用可)。
- 実読: 協議「Unpaid carers - right to breaks...」の分析報告(2026-10-23公開、https://www.gov.scot/publications/unpaid-carers-right-breaks-timescales-support-plans-consultation-analysis/pages/4/)。回答総数427(個人343・第三者機関62・法定機関22)。個人の回答の多数が定義を「明確」としたのに対し、組織の多数は「不明確」とし、**個人と組織で見解が割れる構図**が分かる。引用は短いもの("The proposed definition is a strong and welcome starting point...")で人物像は立ち上がらない。
- 個別回答は取得不可: `consult.gov.scot`のrobots.txtは`Crawl-delay: 5`と`Disallow: /*view_respondent`。この協議の公開回答は377件あるが個別閲覧URLが`view_respondent`のためrobotsで禁止されており、**個別回答は使えない**。Scottish Parliamentが同じシステムで公開する場合は、議会が置く一括xlsx(C3)を使う。
- テーマ選定性◎/ペルソナ性△: 協議の題材は介護者の休息、学校の携帯電話制限、住宅、価格統制など生活に近く、鮮度も高い(閉鎖後に分析が出る)。ただし集計中心。
- 量産適性○: 静的HTML、OGL。協議の入れ替わりは頻繁。

#### C8 Wikipedia/Wikimedia

- 規約: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use(2026-10-29)。"you agree to license it under: Creative Commons Attribution-ShareAlike 4.0 International License ('CC BY-SA 4.0'), and GNU Free Documentation License..." / "Please note that these licenses do allow commercial uses of your contributions, as long as such uses are compliant with the terms of the respective licenses." / 禁止: "Engaging in automated uses of the Project Websites that are abusive or disruptive of the services..."(要旨: 投稿はCC BY-SA 4.0で商用可。迷惑な自動利用は禁止)。robots.txtは悪質botのみ個別Disallow。
- ◎の範囲制約: 翻案物はShare-Alikeの対象。クレジット表示が必要。
- 実読: Reference Desk(Miscellaneous、https://en.wikipedia.org/wiki/Wikipedia:Reference_desk/Miscellaneous)は「建物の銘板の人物」「米国の銀行名の由来」など雑学Q&A。ガイドに"We don't answer requests for opinions, predictions or debate."(意見・予測・討論の依頼には答えない)。記事のTalkページ(例: https://en.wikipedia.org/wiki/Talk:Four-day_week)も"This is not a forum for general discussion of the subject of the article."と明記され、出典に基づく編集議論。投稿の一つに"(Compiled with automated assistance by Casper, an AI agent...)"。ペルソナ性△、テーマ選定性△(背景知識源として限定的)。

#### C9 Hashnode

- 規約: https://hashnode.com/terms(Effective 2026-02-15)。4.1 "You retain full ownership of all content you create, publish, or share through the Service" / 禁止行為 "Scrape, crawl, or use automated means to access the Service in a manner that exceeds reasonable use or violates these Terms."(要旨: 投稿者が所有。過度/規約違反の自動取得は禁止だが商用・AI利用の禁止条項はない)。robots: `/api/`等の管理パスのみDisallow。
- 実読: #career(https://hashnode.com/n/career)から取った記事 https://sherdilitacademy.hashnode.dev/cloud-computing-worth-it-career-switcher-30s は、"Running her actual numbers"形式の**架空の個人の費用試算**(PKR、30代のキャリア転換)で、ITスクール運営者のマーケ記事。実在人物の経験談としては読めない。一覧の見出しにも求人ボット・面接質問集などの宣伝色が強い。
- 評価: 商用AI利用○だがペルソナ性△・テーマ選定性△。推奨しない(同種のdev blog基盤Dev.toは除外)。

## §3 除外・未確認(理由)

### 3-1 除外(10件)

| サイト | URL | 理由(規約逐語[原語]+日本語要旨。確認日2026-10-29) | 前回からの変更 |
|---|---|---|---|
| Netmums(英) | https://www.netmums.com/ | https://www.netmums.com/info/terms-conditions §11「Except where stated, none of the material may be copied, reproduced, distributed, republished, downloaded, displayed, posted, or transmitted in any form by any means ... without the prior written permission of Netmums. Permission is granted to access, download, or print such material for your personal, non-commercial use only」。サイト利用条件(a)「Netmums is to be used by you for your personal use only and may not be used for commercial purposes ... without prior written permission」(複製・再掲は事前の書面許諾が必要、個人・非商用のみ) | Lane aは「規約URLが404で未確認」→**確定除外** |
| HealthUnlocked | https://healthunlocked.com/ | https://policies-notices.healthunlocked.com/article/349-healthunlocked-terms-of-use §6「The Site is for the use of individuals for non-commercial purposes only. To use information gathered from HealthUnlocked commercially ... is strictly prohibited」/ §8「Uses automated means, including spiders, robots ... without express permission」/ コンテンツ条項「may not be ... extracted, re-utilized, recopied, reproduced or otherwise redistributed, including being used for training a Large Language Model or AI Model」(商用利用厳禁、自動収集禁止、LLM利用も明記禁止) | 新規 |
| Kaskus(インドネシア) | https://www.kaskus.co.id/ | https://bantuan.kaskus.co.id/hc/id/articles/226392548-Syarat-dan-Ketentuan「Anda (yang bukan pemilik KONTEN) tidak boleh, tanpa persetujuan tertulis dari kami: Memberikan lisensi, menjual, mentransfer, mengalihkan, mendistribusikan, atau mengeksploitasi LAYANAN atau KONTEN untuk tujuan komersial; Memodifikasi, membuat karya turunan...」(運営者の書面承諾なしに商用利用・派生物作成を禁止) | 新規 |
| Dev.to | https://dev.to/ | https://dev.to/terms §2「Permission is granted to temporarily download one copy of the materials ... for personal, non-commercial transitory viewing only ... you may not: modify or copy the materials; use the materials for any commercial purpose, or for any public display」(個人・非商用の閲覧のみ) | 新規 |
| Participedia | https://participedia.net/ | トップがCC BY-NC-SA 3.0にリンク(https://creativecommons.org/licenses/by-nc-sa/3.0/)。本文"The Participedia platform is published under a Creative Commons license"(NC=非商用限定)。内容も事例の概説で実在人物の語りではない | Lane bの「未調査」→除外 |
| Care Opinion(英) | https://www.careopinion.org.uk/ | https://www.careopinion.org.uk/info/api「feedback on Care Opinion is licensed for re-use under this Creative Commons licence: Attribution-NonCommercial-ShareAlike 4.0 This is a licence for non-commercial use. Please contact us if you require a licence for commercial use.」(商用は別途ライセンス要。当事者体験の質は高いが除外) | 新規 |
| Canada下院(議事録・委員会) | https://www.ourcommons.ca/ | https://www.ourcommons.ca/en/important-notices「Reproduction of the proceedings of the House of Commons and its Committees, in whole or in part and in any medium, is hereby permitted provided that the reproduction is accurate and is not presented as official. This permission does not extend to reproduction, distribution or use for commercial purpose of financial gain.」(商用目的の複製・利用は対象外) | 新規 |
| MoneySavingExpert Forum(英) | https://forums.moneysavingexpert.com/ | T&C(Wayback 2026-07-22: https://web.archive.org/web/20260722000328/https://www.moneysavingexpert.com/site/terms-conditions/)§2「Our Site is provided to you free of charge for your own personal and non-commercial use only.」。「Site」はForumを含む(§1.1)。投稿者はcopyrightを保持するがMSEに広いライセンスを与える(§7.1)。**ただしrobotsは正反対**: www側`Content-Signal: ai-train=yes, search=yes, ai-input=yes`(CCBot・ClaudeBot・GPTBot・Claude-User等を名指しで許可)、forum側もClaude-User等に`Allow: /`。規約本文と運営者のrobots意思が矛盾 | 新規。**判断候補(運営者への許諾照会)あり**(§4) |
| Gransnet(英) | https://www.gransnet.com/ | https://www.gransnet.com/info/terms-of-use「This website and its contents are copyright Gransnet, all rights reserved. Reproduction of all or any substantial part of the contents in any form is prohibited. No part of the site may be distributed, scraped or copied for any purpose without express approval.」(目的を問わず無許可のスクレイピング・複製禁止。Mumsnetの姉妹サイト) | 新規 |
| CFPB Consumer Complaint Database(米) | https://www.consumerfinance.gov/data-research/consumer-complaints/ | 運営者は"All complaint data we publish is freely available for anyone to use, analyze, and build on."と明示するが、**公開データに消費者の本文(narrative)が無い**: 一括CSV(https://files.consumerfinance.gov/ccdb/complaints.csv.zip、先頭のみ取得)のヘッダは`Date received,Product,Sub-product,Issue,Sub-issue,Company public response,Company,State,ZIP code,Tags,Submitted via,Date sent to company,Company response to consumer,Timely response?,Complaint ID`のみ。APIの`has_narrative=true`でも本文欄は空(2022〜2026の3系統で確認)。ペルソナ素材が無いため除外(ライセンスは◎相当だった) | 新規 |

### 3-2 未確認(9件)

| サイト | 理由 |
|---|---|
| 台湾JOIN(公共政策網路參與平臺) https://join.gov.tw/ | フッター「國家發展委員會 Copyright © 2015 版權所有 All rights reserved.」で利用許諾なし。プライバシー頁にも再利用条件の記載なし。robotsは`/idea/detail/*`等のみAllowして他は`Disallow: /`。実読した提案2件(動物虐待の厳罰化 https://join.gov.tw/idea/detail/777296da-28d1-484a-9399-36744cd02309 、チケット転売規制 https://join.gov.tw/idea/detail/c603e476-2e81-4ad3-8f4d-8115c17be660 )は主張型の文書と機関回答で、一人称の人物像は薄い(ペルソナ△)。未確認(All rights reserved)。Lane Bの「Citizens Assembly Ireland」と同じ扱い |
| Oireachtas(アイルランド議会) https://www.oireachtas.ie/ | https://www.oireachtas.ie/en/open-data/license/「Licence incorporating the Creative Commons Attribution 4.0 International License」だが"Rights enjoyed by third persons which the Licensor is not authorized to license"は対象外。議事録HTML(/en/debates/debate/...)は当UAに**HTTP 405**。実投稿未読のため評価不可 |
| Healthtalk/HEXI(Oxford) https://healthtalk.org/ | 「Copyright © University of Oxford. All rights reserved.」、"Ownership Liability and Use"頁は取得できず。当事者インタビューの質は高いとみられるが、規約未読のため未確認 |
| Your Priorities / Better Reykjavik https://yrpri.org/ | トップが4.5KBのJS描画のみで規約・投稿が取得できない |
| Clien(韓国) https://www.clien.net/ | robotsに`anthropic-ai`等AI学習系の名指しDisallow。利用約款(/service/cs/policy)は本文を取得できず(87バイト) |
| DC Inside・Instiz・FMKorea(韓国) | robotsにAI学習系botの名指しDisallowがあり、規約未読。DC InsideはGPTBot等を「AI学習クローラ遮断」として明示 |
| Pann(Nate, 韓国) https://pann.nate.com/ | robotsが`User-agent: *`に`Disallow: /`で一般取得不可(検索エンジン等のみ例外) |
| Senedd(ウェールズ議会) | robots・サイトとも到達可能だが規約本文と投稿は未精査(名前のみ) |
| Mastodon・Medium・EU Have Your Say・Citizens Assembly(Ireland) | 前回Lane判定済みのため再調査せず(名前のみ) |

### 3-3 アクセス不能(回避せず記録。16件)

| サイト | 状況(2026-10-29) |
|---|---|
| オーストラリア連邦議会 https://www.aph.gov.au/ | robots.txtがHTTP 403 |
| NZ議会 https://www.parliament.nz/ | robotsは`Allow: /`だが、ページはRadwareのボット検証画面(HTTP 200・本文なし) |
| 米regulations.gov | robots.txtがHTTP 403 |
| Patient.info | robots.txtがHTTP 403 |
| Mayo Clinic Connect | connect.mayoclinic.orgのrobotsがHTTP 403(community.mayoclinic.orgは名前解決不可) |
| Inspire | robots.txtがHTTP 403 |
| Dcard(台湾) | トップがHTTP 403 |
| Metaculus | トップがHTTP 403 |
| StoryCorps Archive | archive.storycorps.orgがHTTP 403(規約URLも403)。robotsは`ai-train=no` |
| This I Believe | トップがHTTP 403 |
| Library of Congress(コレクション頁) | www.loc.gov/collections/...がHTTP 403(法務頁のみ到達) |
| regjeringen.no(ノルウェー政府の公聴) | HTTP 403 |
| The Student Room(英) | HTTP 403 |
| NSW/QLD/WA州議会(豪) | robots.txtがHTTP 403 |
| Essential Baby(豪) | 名前解決不可 |
| Zenodo(API/検索) | robots.txtが`/api` `/search`をDisallow(CC BYデータの宝庫だが規約上の取得経路が使えないため不使用) |

## §4 所見(判断はFable)

### 4-1 件数サマリ

- 評価対象28サイト = ◎/○ 9(◎相当4: C1・C4・C7・C8、○5: C2・C3・C5・C6・C9)+ 除外10 + 未確認9(JOIN・Oireachtas・HEXI・Your Priorities・Clien・DC Inside・Instiz・FMKorea・Pann)。別にアクセス不能16件、名前のみ記録5件。
- 規約本文まで確認: 約20サイト。実投稿・実文書まで確認: 11サイト(C1〜C9、MSE Forum、JOIN)。
- 発想した新領域: 10(§1-2)。

### 4-2 所見

1. **ライセンスが明確で当事者の声が読める組合せは、公的機関が公開する文書に集中**する。GovInfo公聴会(運営者側◎)、豪州PC提出意見(委員会作成物CC BY 4.0+提出意見○)、Scottish Parliamentの一括公開回答(議会作成物は商用可+回答○)、Harvard Dataverse(CC0)。この4つはペルソナ素材を**実際に読んで**当事者の一人称と異なる立場の存在を確認した。ただし著作権は提出者・証人・研究参加者側に残る(またはCC0でも参加者同意の範囲の問題)ため、**逐語転載ではなく論点・体験の事実の再構成に限る**のが前提(内部記録であり、実装・Prompt変更の提案ではない)。
2. 生活密着型の掲示板は、英語圏で◎/○がゼロ(Netmums・HealthUnlocked・Gransnet・MSE Forum・Care Opinion・Dev.to=除外、Student Room/Mayo Clinic Connect/Inspire=403)。**現地語コミュニティのPTT(台湾)・Pantip(タイ)が○で残る**が、(a)PTTはrobotsに`ai-train=no`、Pantipは規約に条項自体が無く○の根拠が弱い、(b)翻訳工程が必要、(c)AI生成投稿の混入がある。
3. **MSE Forumは運営者の意思が矛盾**している(T&Cは"personal and non-commercial use only"、robotsは名指しでAI学習・AI入力を許可)。生活者の題材・ペルソナ性は高い。2026-10-29の実スレッド https://forums.moneysavingexpert.com/discussion/6688362/disability-and-banking は、障害のある当事者による「銀行の現金配達がなぜ無いのか」と、「現金がなぜ必要か」を問う返信など立場が割れる。許諾が得られれば最有力の生活密着型になり得る。
4. 運用上の注意: robotsが名指しでAI botを拒否するサイト(PTT・StoryCorps・Clien等)が多い。一般UAで通る場合でも、**運営者の意思を迂回しない設計**(自己申告UA・robots準拠・参照利用に限定)を前提にする。
5. GovInfo・PC・Scottish Parliamentは「会議/調査/協議ごと」に題材が決まるため、**先に題材を決め、その題材の提出意見・証言を探す**形になる(掲示板のように毎日新しい題材が流れ込むのとは性質が違う)。継続的なテーマ供給源と、深いペルソナ素材源は分けて評価した方がよい。
6. AI生成投稿の混入は、Wikipedia Reference Desk・PTT・Hashnodeの3か所で実測した。実在性の選別(投稿の一人称の具体性、日時、返信の人間性)を取得後の工程に置く必要がある。

### 4-3 判断候補(Fable判断。区分はPM_GOVERNANCE 27-3に準じLaneの案)

- (a) `Content-Signal: ai-train=no, use=reference`を出す運営者(PTT)を「○」とする線引き。区分案B(ユーザー原文§3の「○=明確な禁止未確認」の範囲内。ai-train=noは学習の拒否であり原稿化の禁止ではないが、線引きの確認が望ましい)。
- (b) MSE Forumへの運営者許諾照会。区分案D(調査範囲外の外部連絡を伴うため新規判断)。
- (c) CC0研究データ(C4)を「参加者同意の範囲外の商業利用」としてどう扱うか。区分案D(倫理判断を伴う)。
- (d) 公的機関系(C1〜C3)を、最終20件の枠内で掲示板型・生活密着型とどう配分するか。区分案B(固定比率を置かない既判断=ユーザー原文§5。Fableが内容評価で選抜)。

### 4-4 前回候補からの変更点

Netmums(未確認→除外)、Participedia(未調査→除外)、MSE Forum・Gransnet・Care Opinion・HealthUnlocked・Kaskus・Dev.to・Canada下院・CFPB(新規→除外)。Mumsnet・Carers UK・Mastodon・Medium・EU Have Your Say・Citizens Assembly Irelandは再評価せず(Lane a/b)。

### 4-5 内部証跡の所在

取得したrobots.txt・規約・実投稿の要点は本ファイルに逐語引用した。取得ツール(自己申告UA・robots確認・3秒間隔)は作業用スクラッチで実行し、成果物ファイルへは含めていない。stop_check結果は`docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01/stop_check_01c.json`(rc=0・非停止)。
