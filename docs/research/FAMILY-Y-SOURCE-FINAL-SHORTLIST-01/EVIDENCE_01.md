# EVIDENCE_01 (FAMILY-Y-SOURCE-FINAL-SHORTLIST-01 委任_02: 最終一覧の内部証跡)

作成: 2026-10-29。統合・選抜・記録のみ(新規サイトの調査なし)。API 0・費用0円・Production変更0。ユーザー向け一覧=`SHORTLIST_01.md`。
**本書は「情報源候補としての記録」で、Production継続利用の承認ではない(登録≠継続利用承認、ユーザー決定③)。◎/○は調査者の規約読み取りで法的保証ではない。**
入力(逐語・実投稿の一次記録): `LANE_A_INTEGRATED_EVAL_01.md`(以下LA)、`LANE_B_DOMESTIC_NEW_01.md`(LB)、`LANE_C_OVERSEAS_NEW_01.md`(LC)、`lane_a_evidence/`(取得ログ・逸脱)。規約逐語は各Laneに全文があり、本書は要点の逐語と所在(Lane§)を示す。確認日は全て2026-10-29(例外は個別に記載)。

## 0. 統合の方法とFable裁定の反映

選抜基準=商用◎/○(必須)→テーマ選定性×ペルソナ性×量産適性の総合(原文§3・§5)。評価は各Laneの実コンテンツ確認に基づく値をそのまま使い、組合せ前提で単独評価を上げていない。

| Fable裁定 | 反映 |
|---|---|
| 1 robotsがAI拒否→規約が○でも非掲載 | §2-1。はてな匿名ダイアリー・PTT・弁護士ドットコム・おーぷん2ちゃんねる等を非掲載(「○(規約)だがrobotsでAI拒否→非掲載」と「規約未確認+robotsでAI拒否→非掲載」を区別して記録) |
| 2 Grand Débat=◎維持・手動DL限定・量産△ | 掲載(海外9)。注記済み |
| 3 Stack Exchange/The Conversation=未確認で非掲載、HN/価格.com/Yahoo!ニュースコメント/MSE=除外 | §2-3・§2-2。MSE運営照会=新UDR #215(任意) |
| 4 Harvard Dataverse=◎・量産△・倫理注記・総合適性で判定 | 掲載(◎×ペルソナ◎、テーマ△〜○、量産△)。倫理注記済み |
| 5 内閣府(www8)のPDL1.0適用範囲を規約文言で確認 | 下記。**不明=○のまま** |
| 6 掲示板・生活密着型を維持、○を「許可」と書かない | ガルちゃん・ママスタ・note掲載。○の説明は原文§3どおり |
| 7 20件以下・適性低は載せない | 19件。§2-4に「適性低で非掲載」の○/◎を理由付きで全件記録 |
| 8 取得逸脱の開示+レジストリに共通fetcher規則の明文化 | §4、`SOURCE_REGISTRY_01.md`冒頭 |

### 内閣府(www8.cao.go.jp)のPDL1.0適用範囲の確認(裁定5。本委任で実施。robots確認つき単発GET3回、UA=`eigo-radio-research/1.0`、間隔3秒、確認日2026-10-29)
- `https://www.cao.go.jp/notice/rule.html`(令和7年3月25日現在)逐語「当ウェブサイトで公開している情報（以下「コンテンツ」という。）の著作権は、特記されていない限り内閣府に帰属し、権利表記の記載がない限り公共データ利用規約（第1.0版）（デジタル庁）が適用されます。」。別ルール適用の一覧(政府広報オンライン・世論調査・地方創生等)に障害者週間の体験作文はない。
- **規約本文はドメイン(www/www8)を明示していない**。`www8.cao.go.jp`の募集要領(`.../kou-kei/boshu_r08.html`)・作品ページ(`.../r07sakuhinshu/sakubun/sy_kuriu.html`)には、利用規約ページへのリンクも権利表記(PDL1.0の言及)もない(リンクは内閣府ホームと政策ページのみ、フッター「© Cabinet Office, Government of Japan」。規約ページ側のフッターと同一文言)。募集要領は「内閣府に推薦のあった作品の著作権は、内閣府に帰属します。」。
- 判定: 適用範囲がwww8に及ぶと**断定できない**ため、裁定5に従い**○のまま**。内閣府への照会で◎確定の可能性が高い(任意。UDR #212の付随事項)。robots.txtはwww・www8とも404(制限なし扱い)。

## 1. 掲載19件の証跡

凡例: 前回=`SOURCE_REGISTRY_01.md`(§1〜§5)の区分。LA/LB/LC=各Laneの該当節に逐語と読んだURLの全文がある。

### 国内(10)

#### 1-1 ガールズちゃんねる ○ / テーマ○ / ペルソナ◎ / 量産◎(LA §2-1)
- 規約: https://girlschannel.net/agreement.html(2026-10-29)。第13条2項「…自身が投稿したコメント等の情報の二次利用（引用、転載、複製、翻案、研究・開発・調査のための利用等）を許諾するものとします」(許諾先は運営者および運営者が許諾した第三者)/ 第13条1項 著作権は創作ユーザーに帰属。第9条に自動収集・スクレイピング・AI入力・商用二次利用の禁止明文なし(「サーバーに負担をかける行為」は禁止)。robots=`Disallow: /admins/`のみ。
- ○の根拠: 明示許可なし・明確な禁止なし。運営者規約(運営と許諾先第三者のみ)と投稿者著作権(各投稿者)を区別=逐語・固有表現の再利用はリスクで、論点・事情の傾向の再構成に限る。
- 実題材: https://girlschannel.net/topics/6319760/「子供が勉強が出来ない」(580件)=中1長男に教える母/発達障害の子の進路/美容専門学校→美容師/中3受験の夫婦分担/生まれつき派と声かけ派の3立場+職業・家族・感情・判断理由が読める。https://girlschannel.net/topics/6320163/(370件)は長文少なく人物素材が薄い=**トピにより差が大きい**。
- 取得制約・量産: 1GET=1トピ全コメント(0.8〜1.1MB)、間隔1.6〜3秒、検索/ランキングあり、更新は秒〜分。低頻度維持。匿名のため釣り・創作・ニュース転載トピは素材にしない。運営への書面照会は未実施(UDR #208)。
- 前回→今回: 条件付き利用可能→○(用語整理)。ペルソナ○→◎(通読・トピ選別前提)。

#### 1-2 ママスタBBS ○ / ○ / ○ / 量産○(LA §2-2)
- 規約: https://mamastar.jp/info/rule(2026-04-08改定)第12条1項「…著作権その他の知的財産権…は、原則、投稿したユーザー本人に帰属する」/ 3項(運営の記事・コラムの転載禁止)。第11条(12)「他人の個人情報を収集、蓄積する行為」禁止。AI入力・自動収集の明文なし。robots=`*`は`/mypage/bbs/`・`/v1/api/`のみ禁止、ClaudeBotにCrawl-Delay 1(許可)。
- ○の根拠: 明示許可なし・禁止なし。投稿の第三者利用の許諾はない。
- 実題材: https://mamastar.jp/bbs/topic/4652542「『普通の男性』ってどんな感じの人なのか」(119件)=婚活の3立場(条件を絞る/性格重視/独身)は実在、コメントは1〜2文中心で人物像は断片的。
- 取得制約: 1トピ約360KB・1GET、ページ分割時の追加GETは未確認、礼儀的に1秒以上。母親視点に偏る。
- 前回→今回: 条件付き→○(評価維持)。

#### 1-3 note ○ / ○ / ◎ / 量産○(LA §2-3)
- 規約: https://terms.help-note.com/hc/ja/articles/44943817565465「クリエイターの承諾があるものを除き、デジタルコンテンツを複製、販売、出版、貸与、放送、公衆送信…改変、翻案する等、購読契約の範囲を超えて利用すること」を禁止。運営の「機械学習等の学習データとして第三者に…提供することができる」は運営の権利で読者の許諾ではない。robots=`/api/*`・`/search`等のみ禁止(記事ページは対象外、AI bot個別拒否なし)。
- ○の根拠: 明確な禁止に当たらないと読めるが「翻案」の射程は不確実=逐語の複製・翻案は不可、傾向の再構成に限る。
- 実題材: https://note.com/clear_loris3610/n/n896a0ab03503(義父の介護・育児・仕事の両立の一人称)、https://note.com/firm_kalmia8942/n/nc9cabb79b47a(市議の請願賛成討論。政治家の演説色が強い)。
- 取得制約: 記事0.2〜0.3MBの単発GET。検索とAPIがrobotsで使えず、発見はタグ・ランキング経由。1記事=1視点で、3立場は複数記事の束ねが前提(組合せの評価は単独に含めない)。公開(無料)記事のみ。
- 前回→今回: 補助/低優先→○。ペルソナ素材の厚みを◎に上方修正(単一視点の制約は維持)。

#### 1-4 国会会議録検索システム ○ / ◎ / ○ / 量産◎(LA §2-4)
- 規約: https://kokkai.ndl.go.jp/api.html §4「その他の発言の著作権は個々の発言者に帰属し、その利用については、原則として、著作権者の許諾が必要となります。ただし、…電子計算機による情報解析等）には、著作権法の定める条件に従って、著作権者の許諾を得ることなくご利用いただけます」「負荷のかかる利用（短時間での大量アクセス等）はご遠慮ください」。商用の明示許諾も明示禁止もない。
- ○の根拠: 解釈依存(権利制限規定の案内は許諾そのものではない)。NDLへの確認が望ましい。
- 実題材: 2026-06-16 参院厚労委 第13号(介護保険法改正案の参考人質疑、https://kokkai.ndl.go.jp/txt/122114260X01320260616)。参考人4名(大学教授・連合・研究所・認知症の人と家族の会[介護家族の一人称])。当事者が混じらない会議は人物像が薄い。
- 取得制約: 公式API(JSON・手続不要)、1会議約185KB、間隔を置く。実名公人は人物化せず別人格で再構成。
- 前回→今回: テーマ△→◎、ペルソナ△→○(実会議の通読)。

#### 1-5 ひきこもりVOICE STATION(厚労省) ◎ / △ / ◎ / 量産△(LB B-1)
- 規約: フッターのリンク先 https://www.mhlw.go.jp/chosakuken/index.html「…特記されていない限り厚生労働省に帰属し、権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます。」PDL1.0(https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)「複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます…。商用利用も可能です。」例外一覧に本サイトの記載なし。
- ◎の根拠: 運営者規約で商用・翻案が明示。**投稿者(応募者)の権利**: 一般公募で「こちらで読みやすく改変した部分もございます」とあり、応募要項の権利処理は取得できず未確認(PDL1.0 1.2「第三者の権利を侵害しないように」)。AI入力の個別明文なし。
- 実コンテンツ: https://hikikomori-voice-station.mhlw.go.jp/story/ の13本を読了(40〜50代男性[いじめ→退職→通信制大学→発達障害の診断]、40歳の息子の母、うつからの居場所づくり、社交不安と美大受験 等)。
- 取得制約: 静的HTML、robots 404。総量が少なく更新は年数回=単独では量産不足。逐語使用は避け論点・経験構造の参考に。
- 前回→今回: 新規(Lane b)。

#### 1-6 内閣府「心の輪を広げる体験作文」 ○ / △〜○ / ◎ / 量産○(LB B-3、本書§0の確認)
- 規約: 募集要領 https://www8.cao.go.jp/shougai/kou-kei/boshu_r08.html「内閣府に推薦のあった作品の著作権は、内閣府に帰属します。」「入賞作品の使用、編集等に当たっては、作品の趣旨を損なわない範囲で一部修正することがあります。」+内閣府規約(§0)。
- ○の根拠: **PDL1.0の適用範囲がwww8に及ぶか規約文言から確認できない(§0)**ため◎にしない。作品の著作権は内閣府。
- 実コンテンツ: 令和7年度一般区分最優秀賞「日常」https://www8.cao.go.jp/shougai/kou-kei/r07sakuhinshu/sakubun/sy_kuriu.html(発達障害のある年長の息子の就学先を親として決める葛藤)。優秀賞「私は障害とともに生きていく」等、当事者本人の語りもある。
- 取得制約: 7年分公開、令和7年度だけで36本。HTMLで取得容易、募集は毎年夏・発表は年末。特定作品に密着した翻案は避ける。氏名・都道府県掲載あり。
- 前回→今回: 新規(Lane b)。SOURCE_REGISTRYの「内閣府=未確認」のうち、規約ページを特定(PDL1.0)、体験作文はwww8の適用が未確定で○。

#### 1-7 平和祈念展示資料館 労苦体験手記 ◎ / △ / ◎ / 量産△(LB B-2)
- 規約: https://www.heiwakinen.go.jp/policy-index/「上記で公開している情報（以下「コンテンツ」といいます。）は、どなたでも以下の 1. ～ 6. に従って、複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます。商用利用も可能です。」「本利用ルールは、政府標準利用規約（第1.0版）に準拠しています。」
- ◎の根拠: 運営者規約で商用・翻案が明示。**第三者の権利**: 同ポリシー「コンテンツの中には、第三者…が著作権その他の権利を有している場合があります」。手記の個々の著者との権利関係は未確認。AI入力の個別明文なし。
- 実コンテンツ: 引揚編第3巻 https://www.heiwakinen.go.jp/wp-content/uploads/archive/library/roukunote/hikiage/03/H_03_024_1.pdf「夫は召集、子供二人は誘拐され」(満鉄社員の妻が子を探し続ける一人称)。同巻は50本近い手記。
- 取得制約: 兵士編19巻+抑留編+引揚編のPDF。更新はほぼなし。pdftotextで文字化けする例あり(pypdfで抽出可)。戦前〜戦後直後の語り口で現代日本語への翻案作業が必要。実名・遺族・歴史認識への配慮。
- 前回→今回: 新規(Lane b)。

#### 1-8 インターエデュ掲示板 ○ / ○ / △ / 量産◎(LB B-6)
- 規約: https://www.inter-edu.com/tos.php に生成AI・自動収集・二次利用許諾の条項なし(投稿の著作権の帰属条項も取得できず)。サイト表示「掲載の記事・写真・イラスト・独自調査データなど、すべてのコンテンツの無断複写・転載・公衆送信等を禁じます。」(掲示板投稿への適用は明記なし)。robots=AmazonbotとPetalBotを拒否、`*`にAI bot拒否なし、bingbotにCrawl-delay 10。
- ○の根拠: 明確な禁止未確認だが許可でもない。逐語転載は不可と解する。
- 実題材: https://www.inter-edu.com/forum/thread/7844045「留学や行き過ぎた英語教育のメリットが良くわからない２」(1226コメント)=「英語は低学年からが命」「小学校で英語より国語・算数を」「AIは英語の思考様式で作られている」の3立場。**個々の書き手の経験・背景はほぼ書かれていない**(ペルソナ△)。別スレは短文の応酬・揶揄中心。
- 取得制約: 静的HTML、日次更新で量産容易、スレは最大150ページ超。固有名詞(学校・個人)は持ち込まない。受験ネタに偏る。
- 前回→今回: 新規(Lane b)。

#### 1-9 e戸建て ○ / ○ / △ / 量産容易(LB B-7)
- 規約: https://www.e-kodate.com/information/kiyaku.html「投稿内容の著作権は、 ミクル株式会社 に帰属します。」「当サイトへの投稿内容は、弊社の裁量で自由に保存し、弊社運営サイトまたは他社のWEBサイト、その他あらゆる用途で利用すること（第三者への利用許諾を含む）ができるものとします。」生成AI・自動収集の禁止条項は見当たらない。robots=AI botに対して`/bbs/search/`・`/search/`のみ拒否(スレッドページは拒否なし)。
- ○の根拠: 禁止未確認。**著作権が運営者に帰属し再許諾権も運営者が持つ**ため無許諾の逐語利用は不可(事業モデル上、データ提供の商談がある可能性。公表は見つからず)。
- 実題材: https://www.e-kodate.com/bbs/thread/571868/「流山おおたかの森の開発(周辺住民専用)その2」(47,000件超)=学区・中学受験率の数字比較、居住者像への言及など。居住地と価値観の断片のみ(ペルソナ△)。
- 取得制約: 1スレHTML約430KB、日次更新。論点・立場の抽出に限る。
- 前回→今回: 新規(Lane b)。

#### 1-10 e-Govパブリック・コメント(結果公示) ◎ / ○ / △ / 量産○(LA §2-5)
- 規約: https://public-comment.e-gov.go.jp/contents/terms「権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）が適用されます」。PDL1.0 1.1「本コンテンツを利用する際は出典を記載してください」/1.2「第三者の権利を侵害しないようにしてください」。厚労省 https://www.mhlw.go.jp/chosakuken/index.html もPDL1.0準拠。
- ◎の根拠: 商用・翻案の明文あり。提出意見の元の著作権は提出者に残りうる(公示は行政機関作成の「要旨」)。AI入力の個別明文なし。
- 実コンテンツ: 案件495250242(介護保険法施行令改正案、PDF `seqNo=0000303955`、3頁)の意見要旨のうち一人称の生活者の声は1件のみ「私の親もそのような収入層にあたり、今回の改正で保険料の負担がどうなるのか、不安を感じています」。前回の約420件調査でも一人称は約1件(ペルソナ△)。
- 取得制約: robots.txtなし(404)。一覧・詳細はPOSTフォーム経由、PDFテキスト抽出はpypdfが必要。案件単位で指定して取得。
- 前回→今回: 条件付き(補助)→商用◎(PDL1.0の明文)。
- 備考: 同じPDL1.0の厚労省審議会議事録は§2-4(適性低で非掲載)。

### 海外(9)

#### 1-11 Productivity Commission(豪州) ○ / ○ / ◎ / 量産○(LC C2)
- 規約: https://www.pc.gov.au/copyright/ "The copyright work is licensed under a Creative Commons Attribution 4.0 International licence, with the exception of … content supplied by third parties." / "Copyright in submissions made to Commission public inquiries and studies resides with the author, not the Commission and will remain on the Commission's website indefinitely as public documents." robots: pc.gov.auはCrawl-delay 2。提出意見PDFのホスト`assets.pc.gov.au`はrobots.txtがHTTP 403(§4に開示)。
- ○の根拠: 委員会作成物はCC BY 4.0(◎相当)だが、**提出意見は運営者が公開を明示するだけで再利用許諾はなく著作権は提出者**のため総合○。
- 実題材: 調査 Childcare and early childhood learning(初回提出468件)。sub006(自営業の母親、ナニー/オーペア/デイケアを使い分けた経験)、sub012(幼児教育教員、"Certificate III educators earn less on average than cleaners with no qualifications.")。利用者・従事者・事業者の3立場が同一調査から取れる。
- 取得制約: 静的HTMLとPDF(pypdf)。1調査=1テーマで入れ替わりは年数件。読んだ提出意見は2013年で鮮度は調査ごとに確認。逐語転載せず再構成。
- 前回→今回: 新規(Lane c)。

#### 1-12 Scottish Parliament(意見募集の公開回答) ○ / ○ / ◎ / 量産○(LC C3)
- 規約: https://www.parliament.scot/about/copyright "You are free to: copy, publish, distribute and transmit the information; adapt the information; exploit the Information commercially and non-commercially…" / 対象外 "personal data in the Information … third-party rights the SPCB is not authorised to license"。回答システム https://yourviews.parliament.scot/terms_and_conditions/ は投稿者に権利が残り、議会とDelibには掲載目的の限定ライセンス。
- ○の根拠: 議会作成物は◎相当だが**市民回答は第三者権利**のため総合○。
- 実題材: Assisted Dying for Terminally Ill Adults (Scotland) Bill の公開回答7,236行のxlsx(議会公式の一括ファイル)。賛否Q1a=Strongly oppose 6,672 / Fully support 387 / Partially support 63 / Neutral 58 / Partially oppose 55(約92%が反対=組織的呼びかけの影響とみられる)。退職した緩和ケア看護師(パートナーを看取った経験)、母の看取り経験(賛成)、母がステージ4の大腸癌だった経験(反対)など当事者体験で3立場が構成できる。
- 取得制約: 議会が置く一括ファイルのみ使用(個別回答の`view_respondent`はrobotsで禁止)。頻度は委員会ごとに年数件〜十数件。名前列あり([REDACTED]処理済み箇所も)=匿名化前提。安楽死・死別など敏感な主題の扱い方針が別途必要。
- 前回→今回: 新規(Lane c)。

#### 1-13 US Congressional hearings(GovInfo) ◎ / ○ / ○(当事者証人の回は◎) / 量産○(LC C1)
- 規約: https://www.govinfo.gov/about/policies "Title 17, Section 105 … Copyright protection under this title is not available for any work of the United States Government" / "public documents can generally be reprinted without legal restriction. However, Government publications may contain copyrighted material which was used with permission of the copyright owner. Publication in a Government document does not authorize any use or appropriation of such copyright material without consent of the owner."
- ◎の根拠(範囲制約): 運営者(GPO)側は公有を明示。**民間証人の提出陳述書は政府職員の職務著作物でなく著作権が証人に残る可能性**=逐語転載でなく論点・体験の事実の抽出と翻案原稿化に限る。AI入力の個別明文なし。
- 実コンテンツ: https://www.govinfo.gov/content/pkg/CHRG-118shrg57244/html/CHRG-118shrg57244.htm(Senate HELP「公立学校教員の短期・長期の課題」)=ユタ州Teacher of the Yearの一人称陳述、パラプロの賃金の実体験、議員の学力・出席データ重視という3立場。別会議 CHRG-118shrg62265(民間学生ローン)は証人が専門家中心で当事者の語りが薄い=回により大差。
- 取得制約: 静的HTML・サイトマップ・バルクデータあり。1会議10万〜20万字級で取得後の要約・抽出が前提。大半は予算・外交・規制で、生活題材はタイトル/委員会で絞る前処理が必要。
- 前回→今回: 新規(Lane c)。

#### 1-14 Tildes ○ / ○ / ○ / 量産○(LA §2-11)
- 規約: https://docs.tildes.net/policies/terms-of-use "by submitting anything to the site, it may be archived, copied, or otherwise duplicated by any other user or automatic system that is able to access it." / "You retain copyright and ownership of any of your own content … non-exclusive license to store, display and distribute that content in the context of operating the site"。robots冒頭 "scrapers are welcome if they are collecting data for informational uses … and maintain a reasonable rate" "Tildes data is not a resource to be mined and sold."
- ○の根拠: AI・スクレイピング・商用の禁止条項なし(機械検索0件)。明示許可でもない。投稿者が著作権を保持=逐語利用は避ける。
- 実題材: https://tildes.net/~talk/1wm9/how_do_you_handle_being_around_other_people(53件)=離婚経験・人間関係の価値観の長文自己開示、立場の割れ。
- 取得制約: 単純HTML、1スレ約120KB、礼儀的に3秒以上。小規模で、~talk週間上位は2件のみ=新題材が少ない。
- 前回→今回: 維持(○)。

#### 1-15 Lemmy(lemmy.world) ○ / ○ / ○(断片) / 量産△(LA §2-12)
- 規約: https://legal.lemmy.world/tos/(約2万字)にscrap/crawl/AI/machine learning/data miningの語0件。Bot規則は投稿用botの規則。robots=`Disallow: /search/`等+`Crawl-delay: 60`(60秒間隔を遵守して取得)。フェデレーション先は別規約。
- ○の根拠: 禁止条項なし、明示許可なし。
- 実題材: asklemmy@lemmy.mlの週間上位から post 53472061「Tech & Cybersecurity folks: What is your long-term plan given the AI explosion?」(11コメント全件)=職業+立場+理由は読めるが1人2〜4文。
- 取得制約: 1スレ(一覧1+コメント1)で約2分、20テーマで40分超。コミュニティ依存でテーマ品質が変動。
- 前回→今回: 維持(○)。前回の`Crawl-delay: 60`違反は今回遵守。

#### 1-16 EA Forum ◎ / △ / ○ / 量産○(LA §2-13)
- 規約: https://forum.effectivealtruism.org/termsOfUse 2.2 "…agree that you are doing so in accordance with, and on the basis that it will be made available to users on, the terms of the Creative Commons — Attribution 4.0 International — CC BY 4.0" / 2.1 Adapted Material。robots=`Crawl-Delay: 2`。
- ◎の根拠: CC BY 4.0(出典表示が必要)。EVF一般Terms(effectivealtruism.org/terms-and-conditions)の自動取得条項は未読。
- 実コンテンツ: https://forum.effectivealtruism.org/posts/5zKfuzDxf9pjvcHxA/my-experience-of-returning-to-work-after-having-a-baby(出産後の復帰記と類似体験コメント)。書き手は英語圏の裕福なEA層に偏る。
- 取得制約: SSR HTMLから本文取得(0.3〜0.5MB)、2秒間隔。EA内輪の前提で日本のリスナーには説明コスト高(テーマ△)。
- 前回→今回: ◎維持。ペルソナ△→○。

#### 1-17 Harvard Dataverse(公開インタビュー逐語録) ◎ / △〜○ / ◎ / 量産△(LC C4)
- 規約: https://support.dataverse.harvard.edu/harvard-dataverse-general-terms-use(Wayback 2026-09版経由。直接取得は403) "Unrestricted User Submissions – Any User Submissions that are published with a default CC0 default public domain dedication waiver agreement." / "As both a registered User and an unregistered Guest, you are able to download publicly available Content from Harvard Dataverse."。API利用規約 https://dataverse.org/best-practices/harvard-api-tou は取得が403で**本文未読**。
- ◎の根拠: データセット doi:10.7910/DVN/GDUOVS のAPIで `license: CC0 1.0`、ファイルは非制限。**CC0は著作権の放棄で、インタビュー参加者の同意の範囲とは別**(研究目的の同意の下で匿名化された語りを商業ラジオ原稿の素材にする点は倫理審査上の同意範囲を超え得る)。
- 実コンテンツ: GDUOVS(COVID-19初期のリスク認識インタビュー18本)のファイル6360583=31歳のフィラデルフィアの救急医・研修医の時系列の一人称語り。
- 取得制約: 検索APIで絞れる(例: 328件)がデータセットごとにライセンス欄の確認が必要(CC0以外もあり得る)。ファイルはdocx/pdf。固定データで継続性が弱い。逐語引用は避け、匿名化維持・個人特定回避を前提。
- 前回→今回: 新規(Lane c)。

#### 1-18 UK議会 請願サイト+Hansard ◎ / ○ / △ / 量産◎(LA §2-14)
- 規約: https://petition.parliament.uk/help "© UK Parliament 2026 All content is available under the Open Government Licence v3.0, except where otherwise stated"。Hansardの複製・翻案・商用はOpen Parliament Licence(前回逐語、FINAL_REPORT_01:22)。第三者権利・動画音声は対象外。
- ◎の根拠: OGL v3.0。AI入力の個別明文なし。
- 実コンテンツ: 請願700086「Introduce 16 as the minimum age for children to have social media」(署名132,102)のJSON=背景は1文+政府回答のみで請願者個人の背景は出ない(ペルソナ△)。**Hansardは今回のrobots.txtがHTTP 403のため本文を取得せず**、議員の子育て体験の引用等は前回記録の引用のみ。
- 取得制約: 請願JSON API・robots許可・軽量(量産◎)。Hansardはrobots 403で不確実。
- 前回→今回: 維持(◎)。

#### 1-19 フランス Grand Débat National(公開データ) ◎ / △ / ○(前回精読) / 量産△(LA §2-16)
- 規約: Licence Ouverte 2.0(前回逐語「la reproduction, la redistribution, l'adaptation et l'exploitation commerciale des données」、出典表示義務、FINAL_REPORT_01:23)。
- ◎の根拠: ライセンスは商用・翻案を明示。AI入力の個別明文なし。
- **取得制約(新事実・裁定2)**: `https://static.data.gouv.fr/robots.txt` の `User-agent: *` に `Disallow: /resources`・`/datasets/r/`・`/api/1/datasets/r/` がある(2026-10-29)。前回は「資源ファイルを制限しない」と記録(CLOSE_READING_02:9)していたが誤りの可能性が高い。→**資源CSVの自動取得は不可、ブラウザからの手動ダウンロード限定**。ファイルは64MB〜。
- 実コンテンツ: 今回は読んでいない(取得逸脱[§4]のため破棄)。ペルソナ○は前回精読の引用(638件中3要素以上18件=2.8%、断片1〜3文)。テーマは2019年の固定データで新題材が増えない(△)。
- 前回→今回: ◎維持。取得経路の制約を新規に記録、テーマ○→△。

## 2. 非掲載の全件

### 2-1 運営がrobots等でAI利用を明示拒否→非掲載(裁定1)
運営の意思表示を尊重し、本文を評価・素材に使わない。区分は「○(規約)だがrobotsでAI拒否→非掲載」と「規約未確認+robotsでAI拒否→非掲載」を区別する。

| サイト | 区分・根拠 |
|---|---|
| はてな匿名ダイアリー(増田) | **○(規約)だがrobotsでAI拒否→非掲載**。規約に明文の禁止なし(前回逐語、TERMS_REVIEW_01:69-84)だが、2026-10-29のrobots.txtが`CCBot`・`GPTBot`・`ClaudeBot`・`anthropic-ai`・`Claude-Web`・`PerplexityBot`等を`Disallow: /`。本文は再取得せず(LA §2-8)。実コンテンツは前回(01A)が読了:「東京転勤を命じられたので会社辞めた」等、長文の一人称で国内最良級。 |
| PTT(台湾) | **○(規約)だがrobotsでAI拒否→非掲載**。規約1-2「…非営利無償使用…転授権」は投稿者→サイトの許諾で、第三者の商用・機械収集の条項なし。robotsが`Content-Signal: search=yes,ai-train=no,use=reference`とClaudeBot等の名指し`Disallow: /`、EU DSM第4条の権利留保。テーマ◎・ペルソナ◎(marriage板の実読)だがAI生成投稿の混入あり。LC C5。 |
| 弁護士ドットコム(法律相談Q&A) | 規約未到達+robotsが`/questions/`をClaude-User・Claude-SearchBot・Meta-ExternalAgent等に`Disallow`(LB §3-1)。 |
| おーぷん2ちゃんねる | 規約本文未取得+robots `Content-Signal: search=yes,ai-train=no,use=reference`・ClaudeBot・Bytespider・CCBot等`Disallow: /`(LB §3-1)。 |
| Yahoo!知恵袋 | 除外。LINEヤフー共通利用規約14条「サービスやそれらを構成するデータを、その提供目的を超えて利用することができません」+robotsがGPTBot・ClaudeBot等を`Disallow: /`、全UAに`/detail/q*`禁止(LA §2-9) |
| Yahoo!ニュース コメント | 除外。robotsがClaudeBot・anthropic-ai・Claude-Web・GPTBot等を拒否+`Disallow: /articles/*/comments`、規約はLINEヤフー共通(LA §2-9) |
| OKWAVE | 未確認。robotsが`/answer`・`/ai`を禁止し多数のAI botを個別拒否、規約URL未特定(LA §2-10) |
| Ask a Manager / ZEIT ONLINE / Quora(日本語) | 未確認。robotsがAI botを名指し拒否(Ask a Manager・Quoraは`ai-train=no`/AI学習の契約許諾なし利用の禁止旨)。規約に明文の禁止は無いか読めない(LA §3-2。Ask a Manager照会=既存UDR #214は任意) |
| Clien / DC Inside / Instiz / FMKorea / Pann(韓国) | 未確認。robotsにAI学習系botの名指し`Disallow`(Pannは`*`に`Disallow: /`)。規約未読(LC §3-2) |

### 2-2 除外(規約・ライセンス・契約・取得不可)
確認日2026-10-29(前回逐語の維持は「前回」と記載)。逐語は各Lane参照。

- **ユーザー決定**: 発言小町(決定①、再調査せず)・Reddit(決定②、回避禁止)。
- **既存除外(維持)**: 5ちゃんねる(運営告知「使用許諾を得る必要」、LA §2-9)、Hacker News(YC規約 Commercial Use / data mining禁止)、The Guardianコメント(機械学習・解析・商用は書面承認要)、Mumsnet(1.c/1.e/1.a=コピー・AI/テキストマイニング禁止)、Kialo、Intelligence Squared、Substack、NYT、Pew、AgingCare、AllSides、IDEA Debatabase、Perspective Daily、gutefrage.net、Naver 知識iN、The Straits Times、Carers UKフォーラム、加古川市版Decidim、NADE(CC BY-NC-ND)、アゴラ(CC BY-NC)、朝日新聞、STORYS.JP、世田谷版気候市民会議、東京都・横浜市(市民意見)(LA §3-1)。
- **今回の変更で除外**: 価格.com クチコミ(第1編第4条「…私的かつ非営利目的でのご利用に限定…営利を目的としたご利用…してはならない」、https://help.kakaku.com/kiyaku_site.html。前回低優先→除外)、Yahoo!ニュースコメント(§2-1)、Hacker News(2026-10-29更新)。
- **Lane b(国内)**: DIPEx-Japan(sitepolicy「生成AI・機械学習への利用の禁止…クローリング、スクレイピング、データセット化」)、労働政策研究・研修機構(無断複製・引用・転載を営利・非営利問わず禁止)、ジモティー(「クロール等で自動的に収集、解析する行為」禁止)、爆サイ.com(AI開発企業向けの有償提供=契約必須)、読売・毎日の投書欄(無断転載禁止)、国立長崎原爆死没者追悼平和祈念館(「無断転用はできません」)、福岡市「市民の声」(無断複製・転用不可)、日本財団(私的使用の範囲を超える使用は禁止)、JICA(私的使用以外の転載・複製等不可)、Talk(第13条: クローリングを含む無断利用禁止)、まちBBS(robots `*`に`Disallow: /`)(LB §3-1)。弁護士ドットコム・おーぷん2ちゃんねるは§2-1。
- **Lane c(海外)**: Netmums(§11・サイト利用条件「personal use only…not … commercial purposes」。前回「未確認」→確定除外)、HealthUnlocked(§6 non-commercial、§8 automated禁止、LLM利用も明記禁止)、Kaskus(書面承諾なしの商用利用・派生物作成禁止)、Dev.to(personal non-commercial viewing only)、Participedia(CC BY-NC-SA 3.0。前回「未調査」→除外)、Care Opinion(CC BY-NC-SA 4.0、商用は別ライセンス)、Canada下院(商用目的の複製・利用は対象外)、**MoneySavingExpert Forum(T&C §2 "Our Site is provided to you free of charge for your own personal and non-commercial use only."。Wayback 2026-07-22経由。robotsは`ai-train=yes, search=yes, ai-input=yes`でAI botを名指し許可=規約本文と運営のrobots意思が矛盾。除外のまま、運営への許諾照会を任意UDR #215として起票)**、Gransnet("distributed, scraped or copied for any purpose without express approval"禁止)、CFPB Consumer Complaint Database(運営者はfreely availableと明示するが公開データに消費者の本文[narrative]がなく、ペルソナ素材なし。ライセンスは◎相当)(LC §3-1)。
- **その他**: Stack Exchange・The Conversationは§2-3(未確認)。

### 2-3 未確認(規約が読めない・条項が不明確)— 最終一覧に載せない
- **Stack Exchange**(Workplace・Parenting等): 内容はCC BY-SA 4.0(商用・翻案可、帰属・ShareAlike)だが、AUPが「generative AI/LLM/MLツールのdeveloping, building, training, testing, indexing, benchmarking, or improving」目的の自動収集を禁止し書面同意で免除(前回逐語、TERMS_REVIEW_01:179-194)。想定用途がこの禁止に当たるか不明、2026-10-29は`stackoverflow.com/robots.txt`がHTTP 418で規約を再取得できず。実コンテンツ(parenting.stackexchange.com 票上位3件)は助言型でペルソナ△・テーマ△。前回「条件付き(補助)」→未確認。
- **The Conversation**: CC BY-ND 4.0。NDにより翻案配布が禁止され、想定用途が翻案に当たらないと断定できず○にしない(前回のFable所見のまま)。
- 規約を読めない/特定できない(LA §3-2): LessWrong、Medium、DebateWise、Munk Debates、Oxford Union、DebateGraph、Mr. Money Mustache forum、Alzheimer's Society forum、BabyCenter(規約URLが404/403)、Zhihu、Rappler、Doctissimo、Make.org、openDemocracy、Togetter(規約URL 404)、SYNODOS、サイボウズ式、Change.org日本(スクレイピング明示禁止+robots準拠のクロールは認める旨だが商用AIの記載なし)、はてなブックマーク。
- Lane c: 台湾JOIN(All rights reserved、ペルソナ△)、Oireachtas(CC BY 4.0だが第三者権利対象外、議事録HTMLは当UAにHTTP 405)、Healthtalk/HEXI(Oxford、All rights reserved、規約頁未取得)、Your Priorities / Better Reykjavik(JS描画)、Senedd(未精査)、Mastodon・Medium・EU Have Your Say・Citizens Assembly Ireland(All rights reserved)は再調査せず。
- Lane b: J-STAGE(個別記事のCC次第。質的研究の実記事を探せず保留)、Zenn(スクレイピング・AIの禁止条項は見当たらず、技術系で実投稿を精読せず○にしない)、移住・交流情報ガーデンJOIN(利用規約ページが見つからず)、イクメンプロジェクト体験談(JS描画)、国立国語研究所の自然会話コーパス(HTTP 403)、ベビカム(メンテナンス)、阿修羅掲示板(規約に到達できず)、したらば掲示板(規約URL 404)、NHK・TBSラジオのリスナー投稿(規約に到達できず)、Mastodon(mstdn.jp)・Misskey.io(短文・検索不能で評価対象外)、認知症の本人ガイド(PDL1.0だが個別の人物像が読めず見送り)。
- Lane a: Surfvote(robots.txt HTTP 503=メンテ継続。再確認1回済み)。内閣府は§0で確認(体験作文は○として掲載)。他府省(文科省・国交省・経産省等)・国民生活センター相談事例は規約ページ取得不能/許可要で未確認のまま(LA §3-2)。

### 2-4 ◎/○だが適性が低い、または利用範囲の制約が重大なため非掲載(裁定7・5・4)
| サイト | 判定 | 非掲載の理由(実コンテンツに基づく評価) |
|---|---|---|
| 法務省 全国中学生人権作文コンテスト(LB B-4) | ○(除外寄り) | 省規約(PDL1.0)の対象外で、別ルールjinken111.htmlは有償出版を原則不可・一部抜粋不可、第45回実施要領「応募作文の著作権（…第２７条及び第２８条に規定する権利を含む。）は、主催者に帰属」=**翻案権が主催者に帰属し利用範囲に重大制約**(裁定5)。書き手が中学生に限られ年齢層が単一、未成年の実名・学校名掲載、法務省への書面確認が必要になる可能性が高い。テーマ○・ペルソナ○(実作文2本読了)。総合適性は低い。 |
| 厚生労働省 審議会議事録(LA §2-6) | ◎ | PDL1.0。ペルソナ△†(団体代表で個人の生活背景が出ない。前回記録の引用、**今回は本文を再読できず**)、制度説明化しやすい。論点・対立軸の裏取り用で、e-Gov(PDL1.0同系)と国会会議録で足りるため非掲載。 |
| 気候市民会議さっぽろ2020 報告書(LA §2-7) | ○ | 単発資料でテーマ△・ペルソナ△(匿名・投票点つきの短文で背景が出ない)・量産△。PDF(北大等の実行委員会作成)に権利・転載条件の記載なし。 |
| 総務省 行政相談の解決事例(LB B-5) | ◎ | 事例が2〜3文に匿名化・要約されペルソナ△、掲載は数件で更新も少なく供給源にならない(Lane bも非推奨)。 |
| 裁判所 裁判例情報(LB B-8) | ○ | 三人称の事実認定でペルソナ△、検索がJS描画で絞り込めず、民事の長文は読み解きコスト高。 |
| ミルクカフェ(LB B-9) | ○ | 更新が細く内容が薄い(最新スレは短文1件、確認した別スレは2004年)。テーマ△・ペルソナ△。 |
| Polis オープンデータ(LA §2-15) | ◎ | CC BY 4.0だがペルソナ△(自己開示0.9%、政策提案文が中心)、固定データ。論点・賛否分布の参照のみ。 |
| Climate Assembly UK(LA §2-18) | ◎ | OGL v3.0。公開ページは集計・要約のみで個人の声なし(テーマ△・ペルソナ△)、静的アーカイブ。 |
| Global Voices(LA §2-17) | ◎ | CC BY。報道で討論ではなく、読んだ記事は制度比較中心で当事者の肉声が少ない(テーマ△・ペルソナ△)。 |
| Parlia(LA §2-19) | ○ | エッセイ形式のFor/Against、体験談・人物背景なし(テーマ△・ペルソナ△)。 |
| gov.scot / Citizen Space 協議の分析報告(LC C7) | ◎ | OGL v3.0。テーマ◎だが集計と少数の引用のみでペルソナ△。個別回答は`Disallow: /*view_respondent`で使えない(議会の一括ファイルはScottish Parliament行で掲載)。 |
| Wikipedia/Wikimedia(LC C8) | ◎ | CC BY-SA 4.0。Reference Deskは雑学Q&Aで意見・議論は規則で禁止、Talkは編集議論。テーマ△・ペルソナ△。Share-Alikeの対象。AI生成投稿の混入あり。 |
| Hashnode(LC C9) | ○ | 実読した#career記事は"her actual numbers"形式の架空事例のマーケ記事。テーマ△・ペルソナ△(推奨しない)。 |
| Pantip(LC C6) | ○(根拠弱) | 規約に著作権・商用・スクレイピングの条項自体が無く、○の根拠が弱い。コメント欄は動的で未実読、タイ語、量産△。 |

### 2-5 アクセス不能(回避せず記録。規約の評価ではない)
- Lane a: こども若者★いけんぷらす(403)、PoliPoli(JS描画)、ABEMA TIMES(規約JS描画)、Metafilter/Ask MetaFilter・Bogleheads・Living Room Conversations・NYTコメント・Japan Today・TheStudentRoom・Fark・Debating Matters・ProCon.org・WEF・OECD・Decidim Barcelona(403)、転職会議/OpenWork(会員壁)、X/Threads(ログイン壁)。
- Lane c: オーストラリア連邦議会(robots 403)、NZ議会(ボット検証画面)、regulations.gov・Patient.info・Inspire・Dcard・Metaculus・This I Believe・StoryCorps Archive(`ai-train=no`)・Library of Congress・regjeringen.no・The Student Room・NSW/QLD/WA州議会(403)、Mayo Clinic Connect(robots 403)、Essential Baby(名前解決不可)、Zenodo(robotsが`/api` `/search`をDisallow=不使用)。
- 内容が目的外/国固有(LA §3-2): Debating Europe、デジタル民主主義2030、EU Have Your Say、Citizens' Assembly Ireland。
- サービス終了・実質不在(LA §3-3): 教えて!goo、ウィメンズパーク、NHKみんなでプラス、BBC Have Your Say、Japan Timesコメント、DebateArt、CreateDebate、IDEA Debatabase現行サイト、Le Drenche。

## 3. 前回候補からの変更点(前回判定→今回)

| 項目 | 前回 | 今回 |
|---|---|---|
| ガルちゃん・ママスタ | 条件付き利用可能 | ○(区分名の整理)。ガルちゃんのペルソナ○→◎。**掲載** |
| note | 補助のみ/低優先度 | ○、ペルソナ素材◎(1記事=1視点)。**掲載** |
| 国会会議録 | ○(テーマ△・ペルソナ△) | テーマ◎・ペルソナ○。**掲載** |
| e-Gov+厚労省 | 条件付き(補助) | 商用◎(PDL1.0明文)。e-Govを**掲載**、厚労省審議会は適性低で非掲載 |
| 内閣府 | 未確認 | 規約ページ特定(PDL1.0)、体験作文はwww8適用未確定で○。**掲載** |
| 価格.com | 低優先度 | **除外**(営利目的利用禁止) |
| Yahoo!ニュースコメント | アクセス不能(Lane cが除外提案) | **除外** |
| Stack Exchange | 条件付き(補助) | **未確認**(AUPの適用範囲不明) |
| Grand Débat | ◎・robotsは資源を制限しない | ◎維持・**robotsが`/resources`の自動取得を拒否=手動DL限定**・量産△・テーマ△。掲載 |
| Netmums | 未確認(規約404) | **除外**(確定) |
| Participedia | 未調査 | **除外**(CC BY-NC-SA) |
| MoneySavingExpert Forum | (新規) | **除外**(T&C非商用、robotsは許可=矛盾。運営照会は任意UDR #215) |
| Hacker News | 除外(2026-10-29更新済) | 維持 |
| 増田 | 未確認 | 未確認維持。robotsのAI bot拒否により**非掲載** |
| EA Forum | ◎、ペルソナ△ | ◎維持、ペルソナ○。**掲載** |
| UK議会請願 / Polis / CAUK / Global Voices / Parlia | ◎/◎/◎/◎/○ | 判定維持。UK請願のみ掲載、他は適性低で非掲載 |
| Tildes / Lemmy | ○ | ○維持。**掲載**(Lemmyは60秒遵守で再調査) |
| 新規掲載 | — | ひきこもりVOICE・平和祈念・内閣府体験作文・インターエデュ・e戸建て(国内)、Productivity Commission・Scottish Parliament・GovInfo・Harvard Dataverse(海外) |

## 4. 取得手順の逸脱の開示

- **Lane a**: (1) Grand Débat CSV(`static.data.gouv.fr/resources/.../la-transition-ecologique.csv`)にRange `bytes=30000000-30400000`で約400KBを1回GET。同ホストrobotsは`Disallow: /resources`に該当し、取得前に`can_fetch=False`を表示で確認したが、自作fetcherを経由せず直接urllibを使ったため停止せず続行した。内容は評価・成果物に使わず破棄(`lane_a_evidence/deviations_01a.md`)。(2) Stack Exchange API(api.stackexchange.com)を1回(parenting、3件)直接取得。同APIのrobots.txtがHTTP 400で自作fetcherは「読取不能」判定だったが、RFC 9309の「4xx=未設置」と解釈して続行。解釈に疑義がある(裁定8で「共通fetcher経由のみ」と明文化)。(3) 前回(DEBATE調査)のGrand Débat精読(Range 2回・計約1.2MB)も同じ拒否に該当する可能性が高い。
- **Debate調査(FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01)**: Kialo規約ページ3件の取得、Lemmy.world `Crawl-delay: 60`違反(`FINAL_REPORT_01.md` §D-2に開示済み。レジストリ冒頭に既記載)。
- **Lane c**: assets.pc.gov.auのrobots.txtが403のため「robots取得不能=制限記述なし」として提出意見PDFを2本取得(うち1本は403)。MSE ForumとHarvard Dataverseの規約本体は403のため**Internet Archive(Wayback)のスナップショット**から読んだ(archive.orgの429は45秒待って再取得)。CFPB一括CSVは先頭1.5MBのRange単発(ヘッダ行のみ確認)。いずれもrobots Disallowのパス(`view_respondent`、Zenodo `/api`・`/search`等)は取得していない。
- **Lane b**: 検索エンジンはrobots.txtで禁止(Bing・Google)またはbot確認画面(DuckDuckGo)のため使用せず。全取得は自作robots判定付きスクリプトで約375リクエスト(403 2件・メンテ・JS描画は回避せず「到達不能」)。
- **本委任(統合)**: 内閣府の規約確認のため、robots確認つき単発GET3回(`www.cao.go.jp/notice/rule.html`、`www8.cao.go.jp`の2ページ。両ホストのrobots.txtは404)。逸脱なし。fetcherは作業用スクラッチ(コミットしない)で、取得前にrobotsを機械確認する。
- **運用の明文化(新Gateではない)**: 今後の取得は「取得前にrobots/Content-Signalを機械確認する共通fetcher経由のみ(直接urllib禁止)」とし、`SOURCE_REGISTRY_01.md`冒頭の取得運用注記に追記した。

## 5. 探索の限界

- 検索エンジンが使えない(Bing・Googleはrobotsで禁止、DuckDuckGoはbot確認で回避せず)。探索は、各省庁サイトの規約ページからの辿り、Wikipedia日本語版の一覧記事、PDL1.0等の適用範囲からの逆引き、ライセンスが明確な公的・オープン系からの逆引き、現地語コミュニティの個別確認で行った。**既知の候補の延長に偏った可能性があり、「存在しない」の証明ではない**。
- 国内の生活密着型で、規約と実投稿の両方を満たす新規候補(育児・介護・仕事・健康・恋愛・地域の掲示板)は発見できなかった(LB §1-3、§4-2)。
- 未探索(名前のみ): 学術OA論文の質的研究(J-STAGEの記事単位CC)、地域SNS・自治会・PTA・介護者会の公開掲示板(多くはログイン壁)、企業・団体の公開座談会(サイボウズ式は未確認)、大学・図書館のオーラルヒストリー、米国各州議会の公聴コメント、自治体議会、Healthwatch(英)、Senedd、ICPSR/UKDS(登録必須)、Nordic協議、Mass Observation、ラテンアメリカ・アフリカ・インド・中東のコミュニティ(LB §4-5、LC §1-3)。
- 実コンテンツを今回読めていない掲載対象: Grand Débat(取得せず前回の引用)、UK Hansard本文(robots 403)。厚労省審議会は非掲載。読めなかった範囲は各項に明記した。
- AI生成・創作投稿の混入: Wikipedia Reference Desk・PTT Salary板・Hashnodeで実測(LC §1-3)。匿名掲示板は創作の可能性を排除できない。取得後に実在の一人称かを選別する工程が必要。
- ◎×ペルソナ◎の存在: ひきこもりVOICE STATION・平和祈念展示資料館・Harvard Dataverseの3件。いずれもテーマ△(〜○)で、単一テーマまたは固定データ(量産△)。Lane aの範囲では存在しなかったが(LA §4-2)、Lane b/cの新規候補で存在した。
