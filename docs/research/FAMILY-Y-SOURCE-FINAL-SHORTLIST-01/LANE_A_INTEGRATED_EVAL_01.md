# LANE_A_INTEGRATED_EVAL_01 (FAMILY-Y-SOURCE-FINAL-SHORTLIST-01 委任_01a: 既存候補の統合・同一基準での再評価)

作成: 2026-10-29(Lane a)。調査のみ・LLM API 0・費用0円・Production変更0・SSOT/SOURCE_REGISTRY/ACTIVE_TASK未編集(統合は委任_02)。ユーザー原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-SOURCE-FINAL-SHORTLIST-01_USER.md`(§3の評価基準①〜④を本書の基準とする)。
**本書は「情報源候補としての評価記録」であり、Production継続利用の承認ではない(登録≠継続利用承認=ユーザー決定③)。◎/○は調査者の規約読み取りで法的保証ではない。判断・最終選定はFable。**

## 0. 凡例・取得規則・件数

- 商用AI利用: **◎**=商用利用・翻案が規約/ライセンスで明示許容(CC BY・OGL・PDL1.0等)。ただし「AI入力」の個別明文があるものは一つもない(翻案・商用の包含解釈)。出典表示義務は別途の設計論点。 **○**=明示許可はないが、明確な禁止も確認されない(「AI利用が許可されている」という意味ではない)。 **除外**=禁止・契約/個別許諾必須・適法な取得ができない。 **未確認**=規約が読めない・条項不明確・運営の意思表示(robots等)との衝突があり判定できない(最終一覧に載せない)。運営者規約と投稿者の著作権は区別して記載する。
- テーマ選定性/ペルソナ性: ◎/○/△(ユーザー原文§3)。ペルソナ性は**実際に読んだ投稿**に基づく。読んだ投稿の無いサイト(robots/規約で今回取得しなかったもの)は「前回の読了記録の引用」と明記し、今回の再読を装わない。
- 量産適性: ◎=軽い(単発GETまたはJSON API・制限なし)/○=実用的だが手間・制約あり/△=重大な制約(取得拒否・低速・固定データ・単発)。費用は全サイトHTTP取得のみでLLM費用0(ここでの評価は取得工数中心)。
- 確認日: 特記なき限り**2026-10-29**(今回取得)。「前回逐語」は`TERMS_REVIEW_01.md`等の2026-10-28逐語記録の再利用で、今回再取得できなかったもの(robots/403等)。
- 取得規則の遵守: UA=`eigo-radio-research/1.0`(自己申告型)、robots/Crawl-delay遵守(自作fetcherで取得前にrobots判定、最短3秒間隔、Lemmy 60秒・Global Voices 10秒・EA Forum 2秒を遵守)、手動相当の単発取得、ログイン不要範囲のみ。**逸脱1件を自己申告**: Grand Débat CSVの資源URLにRangeで約400KBを1回取得したが、同ホストrobotsは`Disallow: /resources`(`*`)に該当していた。内容は評価に使わず破棄(`lane_a_evidence/deviations_01a.md`)。
- 件数: §1統合一覧=94行(グループ行を展開すると約110サイト)。**§2で同一基準の再評価を行ったのは30件**(国内16・海外14)。判定内訳(§2-0): **◎=8 / ○=8 / 除外=9 / 未確認=5**。最終一覧の候補になり得る(◎/○)のは16件(国内7・海外9)。30件のうち、今日取得した一次資料(規約・robots・実投稿)で確認し直したのは25件前後で、残りはユーザー決定(発言小町・Reddit)・前回逐語の維持(Guardian・Mumsnet・HN)。§3は残りの除外・未確認(§1の約65件)の理由。
- 取得記録: `lane_a_evidence/fetch_log_01a.tsv`(約100行。ページ取得約68・robots約30)。

## 1. 統合一覧(全件。サイト|種別|国|前回判定|前回根拠 file:line)

前回判定は、`SOURCE_REGISTRY_01.md`(§1〜§5)の区分と、`FINAL_REPORT_01.md`・`LANE_A/B/C`の判定をそのまま転記。ユーザー決定(発言小町=除外[決定①]、Reddit=対象外[決定②]、登録≠採用[決定③])は維持。

| # | サイト | 種別 | 国 | 前回判定 | 前回根拠(file:line) |
|---|---|---|---|---|---|
| 1 | ガールズちゃんねる | 匿名掲示板(生活全般) | 日本 | 条件付き利用可能(02A) | SOURCE_REGISTRY_01.md:54 |
| 2 | ママスタBBS | 匿名掲示板(子育て・家族) | 日本 | 条件付き利用可能(02A) | SOURCE_REGISTRY_01.md:66 |
| 3 | note | 個人ブログ(体験談・論考) | 日本 | 条件付き利用可能・補助(02A)/低優先度 | SOURCE_REGISTRY_01.md:78 |
| 4 | はてな匿名ダイアリー(増田) | 匿名ブログ(長文一人称) | 日本 | 未確認(02A) | SOURCE_REGISTRY_01.md:90 |
| 5 | Yahoo!知恵袋 | Q&A | 日本 | 規約上の禁止(02A)=除外候補 | SOURCE_REGISTRY_01.md:102 |
| 6 | 5ちゃんねる | 匿名掲示板 | 日本 | 規約上の禁止(許諾要、02A) | SOURCE_REGISTRY_01.md:114 |
| 7 | 発言小町 | 掲示板(相談) | 日本 | 除外(ユーザー決定①) | SOURCE_REGISTRY_01.md:126 |
| 8 | Reddit(日本語含む) | 掲示板 | 国際 | 対象外(ユーザー決定②) | SOURCE_REGISTRY_01.md:138 |
| 9 | 価格.com クチコミ | 製品口コミ掲示板 | 日本 | 低優先度(規約未精読) | SOURCE_REGISTRY_01.md:40 |
| 10 | OKWAVE | Q&A | 日本 | 低優先度(robotsがAI bot個別禁止) | SOURCE_REGISTRY_01.md:41 |
| 11 | Togetter | まとめ(X二次転載) | 日本 | 低優先度 | SOURCE_REGISTRY_01.md:42 |
| 12 | 転職会議 / OpenWork | 就職口コミ | 日本 | アクセス不能(会員壁) | SOURCE_REGISTRY_01.md:43 |
| 13 | Yahoo!ニュース コメント | ニュースコメント | 日本 | アクセス不能(Lane cが除外寄りを提案) | SOURCE_REGISTRY_01.md:154 |
| 14 | X(旧Twitter) / Threads | SNS | 日本 | アクセス不能(ログイン壁) | SOURCE_REGISTRY_01.md:155 |
| 15 | 教えて!goo | Q&A | 日本 | サービス終了(2025-09-17) | SOURCE_REGISTRY_01.md:46 |
| 16 | ウィメンズパーク | 掲示板(子育て) | 日本 | アクセス不能(DNS解決不可) | SOURCE_REGISTRY_01.md:47 |
| 17 | e-Govパブリック・コメント(結果公示)+厚労省・こども家庭庁 | 公的意見募集 | 日本 | 条件付き利用可能(PDL1.0)・補助 | SOURCE_REGISTRY_01.md:161 |
| 18 | 内閣府・他府省(文科省・国交省・経産省等) | 公的機関サイト | 日本 | 未確認 | SOURCE_REGISTRY_01.md:176 |
| 19 | 東京都・横浜市(市民意見) | 自治体の意見募集 | 日本 | 利用不可(許可要) | SOURCE_REGISTRY_01.md:178 |
| 20 | 国民生活センター 相談事例 | 公的相談事例 | 日本 | 未確認(実質は許可要) | SOURCE_REGISTRY_01.md:50 |
| 21 | 国会会議録検索システム(NDL) | 国会議事録(参考人質疑含む) | 日本 | ○(Lane c) | SOURCE_REGISTRY_01.md:286 |
| 22 | 厚生労働省 審議会議事録 | 審議会議事録 | 日本 | ◎(Lane c。D-10の新種別) | SOURCE_REGISTRY_01.md:289 |
| 23 | 気候市民会議さっぽろ2020 報告書 | 市民会議報告書 | 日本 | ○・要注意(Lane c) | SOURCE_REGISTRY_01.md:292 |
| 24 | 世田谷版 気候市民会議 報告書 | 市民会議報告書 | 日本 | 除外(区規約が無断二次利用禁止) | LANE_C_DOMESTIC_01.md:53 |
| 25 | NHK みんなでプラス | 意見募集企画 | 日本 | サービス終了 | LANE_C_DOMESTIC_01.md:39 |
| 26 | Quora 日本語 | Q&A | 日本 | 未確認(Cloudflare 403・robotsがAI学習拒否) | LANE_C_DOMESTIC_01.md:41 |
| 27 | Surfvote(Polimill) | 賛否投票+理由コメントSNS | 日本 | 未確認(503) | LANE_C_DOMESTIC_01.md:42 |
| 28 | PoliPoli | 政策プラットフォーム | 日本 | 未確認(JS描画)・国固有除外 | LANE_C_DOMESTIC_01.md:43 |
| 29 | 加古川市版Decidim | 自治体の市民参加 | 日本 | 除外(営利目的の行為を禁止) | LANE_C_DOMESTIC_01.md:44 |
| 30 | デジタル民主主義2030(いどばた/広聴AI) | 熟議ツール | 日本 | 未確認・国固有除外 | LANE_C_DOMESTIC_01.md:17 |
| 31 | ディベート甲子園/NADE | ディベート論題 | 日本 | 除外(CC BY-NC-ND) | LANE_C_DOMESTIC_01.md:46 |
| 32 | アゴラ | 論壇ブログ | 日本 | 除外(CC BY-NC) | LANE_C_DOMESTIC_01.md:47 |
| 33 | SYNODOS | 論壇・解説 | 日本 | 未確認 | LANE_C_DOMESTIC_01.md:48 |
| 34 | 朝日新聞(声など読者投稿) | 新聞 | 日本 | 除外(無断翻案・蓄積禁止) | LANE_C_DOMESTIC_01.md:49 |
| 35 | STORYS.JP | 体験談投稿 | 日本 | 除外(書面許諾必須) | LANE_C_DOMESTIC_01.md:50 |
| 36 | Change.org 日本 | 署名キャンペーン | 日本 | 未確認 | LANE_C_DOMESTIC_01.md:51 |
| 37 | こども若者★いけんぷらす | 公的意見反映 | 日本 | 未確認(403) | LANE_C_DOMESTIC_01.md:52 |
| 38 | ABEMA TIMES(ABEMA Prime等) | 討論番組記事 | 日本 | 未確認 | LANE_C_DOMESTIC_01.md:54 |
| 39 | サイボウズ式 | 企業メディア | 日本 | 未確認 | LANE_C_DOMESTIC_01.md:55 |
| 40 | はてなブックマーク | ニュースへの短文コメント | 日本 | 未評価 | LANE_C_DOMESTIC_01.md:56 |
| 41 | Hacker News | 技術系掲示板 | 米国 | 除外(2026-10-29。旧=未確認) | SOURCE_REGISTRY_01.md:189 |
| 42 | The Guardian コメント欄 | 新聞コメント | 英国 | 規約上の禁止(02A) | SOURCE_REGISTRY_01.md:190 |
| 43 | Mumsnet | 子育て・家族掲示板 | 英国 | 規約上の禁止(02A) | SOURCE_REGISTRY_01.md:191 |
| 44 | Stack Exchange(Workplace等) | Q&A | 国際 | 条件付き利用可能・補助のみ(02A) | SOURCE_REGISTRY_01.md:193 |
| 45 | Lemmy(lemmy.world) | フェデレーション型掲示板 | 国際 | 低優先度(§2-1)→○(§5 X-8) | SOURCE_REGISTRY_01.md:280 |
| 46 | MoneySavingExpert フォーラム | 消費者掲示板 | 英国 | 低優先度 | SOURCE_REGISTRY_01.md:195 |
| 47 | Mastodon | SNS | 国際 | 低優先度(不適) | SOURCE_REGISTRY_01.md:196 |
| 48 | Ask MetaFilter / NYTコメント / Japan Today / TheStudentRoom / Fark | 掲示板・コメント | 英米 | アクセス不能(403) | SOURCE_REGISTRY_01.md:197 |
| 49 | BBC Have Your Say / Japan Timesコメント | コメント | 英・日 | アクセス不能(実質終了/不在) | SOURCE_REGISTRY_01.md:198 |
| 50 | Slashdot | 技術系掲示板 | 米国 | 未取得 | SOURCE_REGISTRY_01.md:199 |
| 51 | UK議会 請願サイト+Hansard | 公的請願+議事録 | 英国 | ◎(Lane b) | SOURCE_REGISTRY_01.md:259 |
| 52 | 仏 Grand Débat National 公開データ | 市民討論データ | フランス | ◎(Lane b) | SOURCE_REGISTRY_01.md:262 |
| 53 | Polis オープンデータ | 熟議ツールデータ | 国際 | ◎(Lane b) | SOURCE_REGISTRY_01.md:265 |
| 54 | EA Forum | 討論フォーラム | 国際 | ◎(Lane a) | SOURCE_REGISTRY_01.md:268 |
| 55 | Climate Assembly UK | 市民会議報告書 | 英国 | ◎(Lane b) | SOURCE_REGISTRY_01.md:271 |
| 56 | Global Voices | 市民メディア(翻訳報道) | 国際 | ◎(Lane b) | SOURCE_REGISTRY_01.md:274 |
| 57 | Tildes | 小規模討論コミュニティ | カナダ(英語) | ○(Lane a) | SOURCE_REGISTRY_01.md:277 |
| 58 | Parlia | 論点整理(For/Against) | 英国 | ○(Lane a) | SOURCE_REGISTRY_01.md:283 |
| 59 | Kialo | 構造化討論 | 国際 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:46 |
| 60 | Intelligence Squared | 討論イベント | 英国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:47 |
| 61 | Substack | ブログ基盤 | 米国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:49 |
| 62 | NYT | 新聞コメント | 米国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:50 |
| 63 | Pew Research Center | 世論調査 | 米国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:51 |
| 64 | AgingCare | 介護掲示板 | 米国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:52 |
| 65 | AllSides | ニュース偏向格付け | 米国 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:53 |
| 66 | IDEA Debatabase | 討論論点集 | 国際 | 除外(Lane a) | LANE_A_OVERSEAS_EN_01.md:54 |
| 67 | LessWrong | 討論フォーラム | 国際 | 未確認(Lane a) | LANE_A_OVERSEAS_EN_01.md:55 |
| 68 | Ask a Manager | 職場Q&A | 米国 | 未確認(Lane a)。robotsがAI学習拒否 | LANE_A_OVERSEAS_EN_01.md:56 |
| 69 | Medium | ブログ基盤 | 米国 | 未確認(Lane a) | LANE_A_OVERSEAS_EN_01.md:57 |
| 70 | DebateWise | 討論 | 国際 | 未確認(Lane a) | LANE_A_OVERSEAS_EN_01.md:58 |
| 71 | Munk Debates | 討論イベント | カナダ | 未確認(Lane a/b) | LANE_A_OVERSEAS_EN_01.md:59 |
| 72 | Oxford Union | 討論イベント | 英国 | 未確認(Lane a) | LANE_A_OVERSEAS_EN_01.md:60 |
| 73 | Debating Matters / ProCon.org / DebateArt / CreateDebate / DebateGraph | 討論サイト群 | 英米 | 未確認(アクセス不能・実質終了・規約不明) | LANE_A_OVERSEAS_EN_01.md:61 |
| 74 | Metafilter / Bogleheads / Living Room Conversations | 掲示板 | 米国 | 未確認(403) | LANE_A_OVERSEAS_EN_01.md:66 |
| 75 | Mr. Money Mustache forum / Alzheimer's Society forum | 家計・介護フォーラム | 米英 | 未確認(Lane a) | LANE_A_OVERSEAS_EN_01.md:67 |
| 76 | BabyCenter / Netmums | 子育て掲示板 | 米英 | 未確認(規約URL不明) | LANE_A_OVERSEAS_EN_01.md:70 |
| 77 | Pol.is公式サイト / Arguman / Debate Island / Opposing Views | 熟議・討論 | 国際 | 未確認 | LANE_A_OVERSEAS_EN_01.md:72 |
| 78 | Debating Europe | EU市民討論 | EU | 未確認(公開討論なし) | LANE_B_EUROPE_ASIA_CIVIC_01.md:50 |
| 79 | ZEIT ONLINE 読者討論 | 新聞コメント | ドイツ | 未確認(強い否定シグナル) | LANE_B_EUROPE_ASIA_CIVIC_01.md:52 |
| 80 | Perspective Daily | 建設的ジャーナリズム | ドイツ | 除外(Lane b) | LANE_B_EUROPE_ASIA_CIVIC_01.md:53 |
| 81 | gutefrage.net | Q&A | ドイツ | 除外(TDM全面禁止) | LANE_B_EUROPE_ASIA_CIVIC_01.md:54 |
| 82 | Naver 知識iN | Q&A | 韓国 | 除外(RAG/AI学習を厳禁) | LANE_B_EUROPE_ASIA_CIVIC_01.md:55 |
| 83 | Zhihu(知乎) | Q&A | 中国 | 未確認 | LANE_B_EUROPE_ASIA_CIVIC_01.md:56 |
| 84 | The Straits Times / SPH Media | 新聞 | シンガポール | 除外 | LANE_B_EUROPE_ASIA_CIVIC_01.md:57 |
| 85 | Rappler | 報道 | フィリピン | 未確認 | LANE_B_EUROPE_ASIA_CIVIC_01.md:58 |
| 86 | Carers UK フォーラム | 介護フォーラム | 英国 | 除外(Lane b。Lane aは未確認) | LANE_B_EUROPE_ASIA_CIVIC_01.md:59 |
| 87 | Doctissimo フォーラム | 健康・家族フォーラム | フランス | 未確認 | LANE_B_EUROPE_ASIA_CIVIC_01.md:60 |
| 88 | WEF / OECD | 国際機関 | スイス・仏 | 未確認(403) | LANE_B_EUROPE_ASIA_CIVIC_01.md:61 |
| 89 | Decidim Barcelona | 自治体参加 | スペイン | 未確認(403)・国固有寄り | LANE_B_EUROPE_ASIA_CIVIC_01.md:63 |
| 90 | Citizens' Assembly(アイルランド) | 市民会議 | アイルランド | 未確認(All rights reserved) | LANE_B_EUROPE_ASIA_CIVIC_01.md:64 |
| 91 | EU Have Your Say | 公的意見募集 | EU | 未確認(第三者投稿) | LANE_B_EUROPE_ASIA_CIVIC_01.md:65 |
| 92 | openDemocracy | 論壇 | 英国 | 未確認 | LANE_B_EUROPE_ASIA_CIVIC_01.md:66 |
| 93 | Make.org | 市民提案 | フランス | 未確認 | LANE_B_EUROPE_ASIA_CIVIC_01.md:67 |
| 94 | The Conversation | 学術系解説記事 | 国際 | 未確認(CC BY-NDのため○から変更) | SOURCE_REGISTRY_01.md:300 |

## 2. 再評価表(同一基準。30件)

### 2-0 サマリ表(公式URL・種別・国・三軸+量産)

凡例追記: 商用欄の「*」は注記あり(§2-1以降参照)。ペルソナ欄の「†」は今回再読できず前回の読了記録を引用したもの。

| # | サイト | 公式URL | 種別 | 国 | 商用AI利用 | テーマ選定性 | ペルソナ性 | 量産適性 | 前回からの変更点(要約) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ガールズちゃんねる | https://girlschannel.net/ | 匿名掲示板 | 日本 | ○* | ○ | ◎* | ◎ | 条件付き→○(用語整理)。ペルソナ○→◎(今回の通読で上方修正、トピ選別前提) |
| 2 | ママスタBBS | https://mamastar.jp/bbs/ | 匿名掲示板(子育て) | 日本 | ○* | ○ | ○ | ○ | 条件付き→○。評価は維持 |
| 3 | note | https://note.com/ | 個人ブログ | 日本 | ○* | ○ | ◎* | ○ | 補助/低優先度→○。ペルソナ素材の厚みは◎(ただし1記事=1視点)に上方修正 |
| 4 | 国会会議録検索システム(NDL) | https://kokkai.ndl.go.jp/ | 国会議事録 | 日本 | ○* | ◎ | ○* | ◎ | テーマ△→◎、ペルソナ△→○(2026-06-16参院厚労委参考人質疑を通読。会議選別が前提) |
| 5 | e-Govパブコメ(結果公示)+厚労省・こども家庭庁 | https://public-comment.e-gov.go.jp/ | 公的意見募集 | 日本 | ◎* | ○ | △ | ○ | 条件付き(補助)→商用◎(PDL1.0の商用・翻案明文)。テーマ○。ペルソナ△は維持 |
| 6 | 厚生労働省 審議会議事録 | https://www.mhlw.go.jp/stf/shingi/ | 審議会議事録 | 日本 | ◎* | ○ | △† | ○ | 維持(◎)。議事録本文の再読は今回できず(§2-6) |
| 7 | 気候市民会議さっぽろ2020 報告書 | https://www.env.go.jp/council/06earth/y0620-3b/900425001.pdf | 市民会議報告書 | 日本 | ○* | △ | △ | △ | 商用○(要注意)維持。テーマ○→△(単発・継続性なし)、ペルソナ△維持 |
| 8 | はてな匿名ダイアリー(増田) | https://anond.hatelabo.jp/ | 匿名ブログ | 日本 | 未確認 | (○)† | (◎)† | — | 未確認維持。robotsのAI bot全面拒否を今日再確認し本文は再取得せず |
| 9 | Yahoo!知恵袋 | https://chiebukuro.yahoo.co.jp/ | Q&A | 日本 | 除外 | — | — | — | 除外維持(LY規約14条+robots `/detail/q*`禁止+AI bot全面拒否) |
| 10 | 5ちゃんねる | https://5ch.io/ | 匿名掲示板 | 日本 | 除外 | — | — | — | 除外維持(運営告知「使用許諾を得る必要」を今日再確認) |
| 11 | 発言小町 | https://komachi.yomiuri.co.jp/ | 掲示板 | 日本 | 除外(ユーザー決定①) | — | — | — | 維持(再調査せず) |
| 12 | 価格.com クチコミ | https://kakaku.com/ | 製品口コミ | 日本 | 除外* | — | — | — | **変更**: 低優先度(規約未精読)→除外(第4条で営利目的の利用を禁止、今日逐語取得) |
| 13 | Yahoo!ニュース コメント | https://news.yahoo.co.jp/ | ニュースコメント | 日本 | 除外* | — | — | — | **変更**: アクセス不能→除外(Lane cの提案を採用。robotsがコメントURLとAI botを拒否+LY規約準用) |
| 14 | OKWAVE | https://okwave.jp/ | Q&A | 日本 | 未確認 | — | — | — | 低優先度→未確認(規約URL未特定、robotsがAI botを多数拒否) |
| 15 | Togetter | https://togetter.com/ | まとめ | 日本 | 未確認 | — | — | — | 低優先度→未確認(規約URLが404で未取得) |
| 16 | Surfvote | https://surfvote.com/ | 賛否投票+理由 | 日本 | 未確認 | — | — | — | 維持(今日もrobots.txtがHTTP 503=メンテ継続。再確認1回済み) |
| 17 | Tildes | https://tildes.net/ | 小規模討論コミュニティ | カナダ(英語) | ○* | ○ | ○ | ○ | 維持(○)。通読で自己開示つきの長文を確認 |
| 18 | Lemmy(lemmy.world) | https://lemmy.world/ | 掲示板(フェデレーション) | 国際 | ○* | ○ | ○ | △ | 維持(○)。Crawl-delay 60秒を遵守して通読 |
| 19 | EA Forum | https://forum.effectivealtruism.org/ | 討論フォーラム | 国際 | ◎* | △ | ○ | ○ | 商用◎維持(CC BY 4.0の規約条文を再取得)。ペルソナ△→○(育児と仕事の個人記+類似体験コメントを通読) |
| 20 | UK議会 請願サイト+Hansard | https://petition.parliament.uk/ | 公的請願+議事録 | 英国 | ◎* | ○ | △ | ◎ | 維持。Hansardはrobots 403で今回未取得 |
| 21 | Polis オープンデータ | https://github.com/compdemocracy/openData | 熟議データ | 国際 | ◎* | ○ | △ | △ | 維持。データ自体は固定で新規題材は増えない |
| 22 | 仏 Grand Débat National 公開データ | https://www.data.gouv.fr/datasets/donnees-ouvertes-du-grand-debat-national | 市民討論データ | フランス | ◎* | △ | ○† | △* | **変更**: 取得経路がrobots拒否(`Disallow: /resources`)と判明。量産適性に重大な制約。テーマ○→△(固定データ) |
| 23 | Global Voices | https://globalvoices.org/ | 市民メディア(翻訳報道) | 国際 | ◎* | △ | △ | ○ | 維持(◎)。記事を通読し人物像△を確認 |
| 24 | Climate Assembly UK | https://www.climateassembly.uk/ | 市民会議報告書 | 英国 | ◎* | △ | △ | △ | 維持。公開ページは集計・要約のみで個人の声なし |
| 25 | Parlia | https://www.parlia.com/ | 論点整理 | 英国 | ○* | △ | △ | ○ | 維持。トピックを通読し体験談なしを確認 |
| 26 | Stack Exchange(Workplace・Parenting等) | https://stackexchange.com/ | Q&A | 国際 | 未確認* | △ | △ | △ | **変更**: 条件付き(補助)→未確認(AUPのgenerative AI目的の自動収集禁止条項の適用範囲が不明、今日はrobots 418で規約再取得不可) |
| 27 | Hacker News | https://news.ycombinator.com/ | 技術系掲示板 | 米国 | 除外 | — | — | — | 維持(2026-10-29の除外) |
| 28 | The Guardian コメント欄 | https://www.theguardian.com/ | 新聞コメント | 英国 | 除外 | — | — | — | 維持(02A) |
| 29 | Mumsnet | https://www.mumsnet.com/ | 子育て掲示板 | 英国 | 除外 | — | — | — | 維持(02A) |
| 30 | Reddit | https://www.reddit.com/ | 掲示板 | 国際 | 除外(ユーザー決定②) | — | — | — | 維持(回避禁止) |

判定内訳(30件): **◎=8**(#5・6・19・20・21・22・23・24)/**○=8**(#1・2・3・4・7・17・18・25)/**除外=9**(#9・10・11・12・13・27・28・29・30)/**未確認=5**(#8・14・15・16・26)。**最終一覧の候補になり得る(商用◎/○)のは16件**(国内7・海外9)。20件を超えないため本Laneでは絞込み不要。そのうち、テーマ・ペルソナとも○以上は6件(#1・2・3・4・17・18)。

### 2-1 ガールズちゃんねる(#1)

- **商用AI利用: ○**(明示許可なし・明確な禁止なし。「AI利用が許可されている」ではない)。
- 規約(https://girlschannel.net/agreement.html、今回再取得、2026-10-29): 第13条2項「本サイトにコメント等の情報を投稿したユーザーは、本サイトの運営者および運営者が許諾した第三者に対し、自身が投稿したコメント等の情報の二次利用（引用、転載、複製、翻案、研究・開発・調査のための利用等）を許諾するものとします」/ 第13条1項「…権利（著作権および著作者人格権等の周辺権利）は、創作したユーザーに帰属します」。第9条の禁止事項に自動収集・スクレイピング・AI入力・商用二次利用の明文はない(今回の機械検索: クローラ/スクレイ/ロボット/自動/AI/人工知能/機械学習/営利/商用は0件、解析はアクセス解析の案内のみ。広告投稿・勧誘・サーバーに負担をかける行為・個人情報投稿は禁止)。robots=`User-agent: *` / `Disallow: /admins/`のみ(AI bot個別拒否なし、Crawl-delayなし)。
- 運営者規約と投稿者著作権の区別: 著作権は各投稿者。運営者が許諾を受けるのは「運営者および運営者が許諾した第三者」だけで、一般の閲覧者への許諾条項はない。**複製・翻案(逐語・固有の言い回しの再利用)はリスク**で、論点・事情の傾向を自分の言葉で再構成する範囲に限る。
- テーマ選定性: **○**。当日ランキング上位は芸能・ニュース転載が多い(2026-10-29朝: 1位 芸能人の報道、2位 婚活、4位 芸能人の子の発言…)が、生活・家族・お金・仕事のトピックが常に混在(例 7位「子供が勉強が出来ない」580件、30位「育児しない夫がやばい」234件、17位「パート主婦の語り場」、13位「1000万円貯めたことがある方に…」)。議論性のあるトピは日替わりで継続的に出る。日本のリスナー適合は高い。女性・主婦層に偏る。
- ペルソナ性: **◎(トピ選別前提)**。読んだ投稿: ① https://girlschannel.net/topics/6319760/「子供が勉強が出来ない」(580件・全件1ページ、2026-10-29取得)。長文(110字超)は22件だが、異なる家庭が具体的に出る: (a)中1の長男だけ出来ず、夫婦とも大卒で全部教えている母「教えてる私のせいでもあるし…泣けてきます」(b)子が発達障害・凸凹が大きく「期待はしないけど希望は持って…Fランでいいから大学も行かせる」(c)長男は偏差値51〜52の高校→美容専門学校→美容師「毎日楽しそうに生きてるからそれで良かった」(d)中3受験生を夫婦で教科分担「親の方は身も心も限界」(e)「生まれつき頭が良い子は塾に行かなくても」派と「母親からガッカリされてヤル気を出す子はいない」派。→3立場(伴走して引き上げる/進路の多様性を認める/生まれつきの差を認める)と、職業・家族構成・感情・判断理由が1コメント内で読める。② https://girlschannel.net/topics/6320163/「水商売に戻りたい私に喝を入れてください。」(370件): 長文は少なく人物素材は薄い(スナックのママの実体験の引用程度)→**トピによって差が大きい**ため選別が必須。匿名のため釣り・創作の混入を排除できない。
- 量産適性: **◎**。HTML 1GET=1トピ全コメント(0.8〜1.1MB)、間隔1.6〜3秒で十分、検索`/topics/search/?q=`・ランキング・新着あり、更新は秒〜分単位。1テーマの取得は2〜4GET(ランキング+トピ1〜2+隣接トピ)。費用0。制約: 第9条「サーバーに負担をかける行為」禁止=低頻度を維持。
- 利用範囲の制約メモ(内部記録): 論点・事情の傾向の参考まで。逐語転載・固有表現の再利用は避ける。ニュース転載トピ(投稿者の声が薄い)、荒らし・AI生成文貼付は素材にしない。運営への書面照会は未実施(前回のまま)。
- 前回との差分: 区分名のみ「条件付き利用可能」→「○」。ペルソナを上方修正(今回の通読)。規約・robotsは前回と同一内容を再確認。

### 2-2 ママスタBBS(#2)

- **商用AI利用: ○**。
- 規約(https://mamastar.jp/info/rule、2026年4月8日改定、今回再取得): 第12条1項「…著作権その他の知的財産権…は、原則、投稿したユーザー本人に帰属する」/ 2項は運営(当社)が投稿を自社及び提携媒体で利用できる許諾/ 3項「本サービスに掲載されている記事、ニュース、漫画およびコラムの著作権等は当社または当社にその利用を許諾した第三者に帰属します。…当社の事前の承諾なしに、転載、複製、出版、放送および公衆送信等…をおこなうこと…はできません」。第11条(12)「他人の個人情報を収集、蓄積する行為」禁止、(9)(10)は掲載する側の商業行為。AI入力・自動収集の明文なし(今回の機械検索: クローラ/スクレイ/ロボット/AI/人工知能/解析/機械学習は0件、『自動』は月額契約の自動更新のみ)。robots=`User-agent: *`は`/mypage/bbs/`・`/v1/api/`のみ禁止、ClaudeBotに`Crawl-Delay: 1`(許可)。
- 運営者規約と投稿者著作権: 投稿は投稿者の著作権。運営の記事・コラム等は運営の著作物で転載禁止(素材にしない)。投稿そのものの第三者利用の許諾はない。
- テーマ選定性: **○**。カテゴリ=旦那・家族/仕事・お金/妊活・育児/小学生/中学生以上/シンママ等(子育て・家族・家計に特化し、幅はGCより狭い)。当日の新着にも「妹に生活費を借りていたら着信拒否」「扶養内パートの年末調整」等の具体的な生活相談がある。日本適合は高いが母親視点に偏る。
- ペルソナ性: **○**。読んだ投稿: https://mamastar.jp/bbs/topic/4652542「『普通の男性』ってどんな感じの人なのか」(119件、2026-10-29取得)。トピ主=年収700万・理系大卒の30歳の妹の婚活相談。コメントは1〜2文が中心(長文は少ない)で、人物像は断片的: 「私も理科大なので妹さんに親近感。理科大の女子はモテる…男女比10:1」「婚活に疲れて一休みした時に職場の同僚の夫と出会った」「みんな40過ぎてから結婚相談所でバタバタと結婚していく」。3立場(条件は絞れ/条件を緩めて性格重視/独身で自由に生きる)は実在するが、1コメントの背景情報はGCより薄い。
- 量産適性: **○**。1トピ約360KB・1GET、更新頻繁。コメントがページ分割される場合の追加GETは今回未確認。ClaudeBot以外のUAにはCrawl-delay指定なし(礼儀的に1秒以上)。
- 利用範囲の制約メモ: GCと同じ(論点・事情の参考まで、逐語を避ける、個人情報を取り込まない)。運営のセレクト記事・コラム・記事付随のコメントスレッドは素材にしない。
- 前回との差分: 区分名のみ。評価内容は維持。

### 2-3 note(#3)

- **商用AI利用: ○**(注意が必要な○)。
- 規約(https://terms.help-note.com/hc/ja/articles/44943817565465、今回再取得): 「クリエイターの承諾があるものを除き、デジタルコンテンツを複製、販売、出版、貸与、放送、公衆送信（送信可能化を含みます）、上映、改変、翻案する等、購読契約の範囲を超えて利用すること」を禁止事項として列挙/「当社は、クリエイターのデジタルコンテンツの収益化を支援するため、…デジタルコンテンツおよびこれに付随する情報…を、機械学習等の学習データとして第三者に無償または有償で提供することができる」(運営の権利。利用者の権利ではない)。著作権は各クリエイター(今回の機械検索: クローラ/スクレイ/ロボット/生成AI/営利は0件、『解析』は運営の推薦機能の記述のみ)。robots=`/api/*`・`/search`・`/*/followers`等のみ禁止(記事ページ・ハッシュタグページは禁止対象外、AI bot個別拒否なし)。
- 運営者規約と投稿者著作権: クリエイター(投稿者)が著作権を持ち、複製・改変・翻案は「クリエイターの承諾」が要る(購読契約の範囲)。運営の機械学習提供条項は運営→第三者の話で、読者側の許諾ではない。→**逐語の複製・翻案は不可、論点・経験の傾向を自分の言葉で再構成する範囲に限る**(ここまでは明確な禁止に当たらないと読めるが、「翻案」の射程は不確実)。
- テーマ選定性: **○**。題材の幅は無制限(「介護」タグだけで278,399件)で継続性も高い(数時間おきに新着)。ただし**1記事=1視点**のため、3立場を揃えるには別筆者の記事を束ねる必要があり、検索はrobotsで禁止のためハッシュタグ・ランキング経由の発見になる。
- ペルソナ性: **◎(素材の厚み)**。読んだ投稿: ① https://note.com/clear_loris3610/n/n896a0ab03503 — 義父の介護・育児・仕事の両立を振り返る一人称(「義父の介護も、子どもたちの育児も、仕事との両立も、そのときの自分なりに精いっぱいやってきたつもりです」「誰かのために時間を使っているうちに、自分の人生まで誰かの都合で埋まってしまうのは、少し違う気がする」)=職業・家族状況・感情・判断理由が1人分そろう。② https://note.com/firm_kalmia8942/n/nc9cabb79b47a — 八潮市議会議員の「夜勤規制を求める請願」への賛成討論(反対意見の論点[財源・配置基準・ICT]と入院した市民の声を整理)=立場が異なる論点が1記事で読めるが、政治家の演説色が強い。
- 量産適性: **○**。記事ページは0.2〜0.3MBの単発GET、ハッシュタグ一覧は0.6MB。`/api/*`と検索は使えないため発見はタグ・ランキング経由。1テーマ3記事で3〜6GET。
- 利用範囲の制約メモ: 公開(無料)記事のみ。逐語転載なし。実名・固有の表現の再利用を避ける。単独では3視点にならないため複数記事の束ね方が前提(組合せの評価は単独サイトの評価に含めない)。
- 前回との差分: 「補助のみ/低優先度」→○のまま、ただしペルソナ素材の厚みを今回の通読で◎に引き上げ(単独視点の制約は維持)。

### 2-4 国会会議録検索システム(#4)

- **商用AI利用: ○**(解釈依存)。
- 規約(https://kokkai.ndl.go.jp/api.html §4、今回再取得): 「その他の発言の著作権は個々の発言者に帰属し、その利用については、原則として、著作権者の許諾が必要となります。ただし、…著作権法の権利制限規定が適用される場合（私的使用のための複製、引用、政治上の演説又は陳述に該当する箇所の利用、報道、電子計算機による情報解析等）には、著作権法の定める条件に従って、著作権者の許諾を得ることなくご利用いただけます」/「負荷のかかる利用（短時間での大量アクセス等）はご遠慮ください」/「機械的なアクセスを行う場合、多重リクエストは避けて」。APIの利用に手続き不要(前回)。商用利用の明示許諾も明示禁止もない。
- 運営者規約と発言者の著作権: DBとNDL職員の発言はNDL、その他の発言の著作権は発言者(原則許諾要)。NDLは情報解析等の権利制限規定を案内するのみ(許諾そのものではない)。
- テーマ選定性: **◎**。少子化・介護保険・AI・年金・移民等、日本のリスナーに直結する公共政策が常に更新される。参考人質疑・公聴会では立場が割れる。
- ペルソナ性: **○(会議の選別が前提)**。読んだ会議: 2026-06-16 参議院厚生労働委員会 第13号(介護保険法改正案の参考人質疑、https://kokkai.ndl.go.jp/txt/122114260X01320260616、API `meeting`で取得)。参考人4名=大学教授(法学)/連合の政策局長/民間研究所の上席研究員/認知症の人と家族の会の志田参考人。志田参考人は「山形県に住み、仕事では介護職、生活相談員、ケアマネジャーを経て…東京で暮らしていた両親を呼び寄せ、十六年前に認知症の父を、昨年はこれまた認知症の母親のみとりを終えたばかりの介護家族」と一人称で語る=職業・家族・経験・判断理由が読める。他の3名は専門家・団体の立場で、3系統(当事者/労働側/研究者)は揃う。当事者参考人が混じらない会議は人物像が薄い。実名の公人のため、人物化せず別人格として再構成する前提。
- 量産適性: **◎**。公式API(JSON、手続き不要)。1会議のJSONは約185KB。間隔を置けば制限なし。会議の選別(当事者参考人の有無)は`speakerPosition`で機械判別できる見込み。費用0。
- 利用範囲の制約メモ: 論点・立場の参考。逐語利用せず、実名の参考人は別人格にする。NDLへの確認が望ましい(前回のまま)。
- 前回との差分: テーマ△→◎、ペルソナ△→○(実会議の通読による)。

### 2-5 e-Govパブリック・コメント結果公示+厚労省・こども家庭庁(#5)

- **商用AI利用: ◎**(出典表示・第三者権利の条件つき。AI入力の個別明文はない)。
- 規約(今回再取得): e-Gov https://public-comment.e-gov.go.jp/contents/terms「権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）が適用されます」/ PDL1.0 https://www.digital.go.jp/resources/open_data/public_data_license_v1.0「複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます…商用利用も可能です」/ 1.1「本コンテンツを利用する際は出典を記載してください」/ 1.2「第三者の権利を侵害しないようにしてください」/ 厚労省 https://www.mhlw.go.jp/chosakuken/index.html「「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます」。
- 運営者規約と投稿者著作権: PDL1.0は国の作成物に対する許諾。提出意見の元の著作権は提出者に残りうる(PDL1.0 1.2は第三者権利は利用者責任)。公示は行政機関が作成した「要旨」。
- テーマ選定性: **○**。年金・介護保険・保育・労働・年収の壁など生活に直結する制度案件が常時公示される。立場(利用者・事業者・保険者・自治体)は実在。ただし生活者の一人称が中心のテーマは限られ、Family Yの身近なテーマに直結する案件は少ない。
- ペルソナ性: **△**。読んだ資料: 案件`495250242`(介護保険法施行令改正案、PDF `seqNo=0000303955`、3頁、2026-10-29取得・pypdfで抽出)。提出意見の要旨のうち一人称の生活者の声は1件のみ「私の親もそのような収入層にあたり、今回の改正で保険料の負担がどうなるのか、不安を感じています」。他は制度の公平性・自治体の事務負担。人物像を作る材料にはならない(前回の約420件調査でも一人称は約1件)。
- 量産適性: **○**。robots.txtなし(404)。一覧・詳細はPOSTフォーム経由で自動化に手間、PDFはGETで取得可。PDFのテキスト抽出はpdftotextでは文字化け・空になり、pypdfが必要(今回確認)。案件単位で指定して取得する運用。
- 利用範囲の制約メモ: 制度・事実関係の裏取り、立場の対立軸の公的記録。要旨の逐語利用を避ける。出典表示(案件URL・利用日)の方式は設計論点。
- 前回との差分: 区分「条件付き(補助)」→商用◎(PDL1.0の商用・翻案の明文に基づく)。ペルソナ△維持。

### 2-6 厚生労働省 審議会議事録(#6)

- **商用AI利用: ◎**(PDL1.0。上記#5と同条文を今回再取得: https://www.mhlw.go.jp/chosakuken/index.html)。
- テーマ選定性: **○**(労働・年金・介護・障害等。労使公益の三者構成が制度上固定され、対立軸の公的記録が継続的に出る。日本適合は高いが制度説明化しやすい)。
- ペルソナ性: **△†**(Lane cの記録: 委員は団体代表で個人の生活背景は出ない)。今回は`mhlw.go.jp/stf/shingi/`から1会議の議事録本文まで到達できず(アルコール健康障害対策関係者会議の開催案内2ページまで確認したが議事録リンクを特定できなかった)、**本文の再読はしていない**。robotsは`/cgi-bin/`・`/images/`等のみ禁止で議事録パスは制限なし(今回確認)。
- 量産適性: **○**(1URL取得だが、会議体ごとのページ構造が異なり議事録リンクの辿り方に工数)。
- 利用範囲の制約メモ: 論点・対立軸の裏取り用。Personaの主材料にしない。
- 前回との差分: 維持。本文再読は今回未実施(次委任で必要なら実施)。

### 2-7 気候市民会議さっぽろ2020 報告書(#7)

- **商用AI利用: ○**(要注意)。
- 規約: 掲載元の環境省サイトはPDL1.0適用(https://www.env.go.jp/mail.html、前回確認)だが、当該PDF(https://www.env.go.jp/council/06earth/y0620-3b/900425001.pdf、今回取得、54頁・2.5MB)は北大・阪大・環境研等の「気候市民会議さっぽろ2020実行委員会」の報告書で、本文中に「著作権」「転載」「無断」「ライセンス」の語は**0件**(今回機械検索)=権利者・転載条件の記載なし。PDL1.0が第三者作成物に及ぶかは不明。
- テーマ選定性: **△**(脱炭素の「痛み」の許容度に価値観の割れ方が出るが、単発の報告書で継続的に新題材が出ない)。
- ペルソナ性: **△**。読んだ内容: 参加者コメントは匿名・投票点つきの短文(例「ある程度の規制がないと、なくなっていかないと思う」「困窮者が出ないタイミングで規制が出されることを望みます」「ガソリンスタンド並みのインフラ数は整備できない。なかなか難しいと思う」)で、年代・職業・家族の背景は出ない。
- 量産適性: **△**(単発資料)。
- 前回との差分: テーマ○→△(継続性なし)、ペルソナ△維持。

### 2-8 はてな匿名ダイアリー(増田)(#8) — 未確認

- 規約: 明文の禁止なし(前回逐語、`TERMS_REVIEW_01.md:69-84`)。**今日再取得したrobots.txtは`CCBot`・`GPTBot`・`ClaudeBot`・`anthropic-ai`・`Claude-Web`・`PerplexityBot`等を`Disallow: /`**(https://anond.hatelabo.jp/robots.txt、2026-10-29)。運営のAI取得拒否の意思表示として尊重し、**今回は本文を再取得していない**。
- 判定: **未確認**(「規約上の禁止」ではなく「運営の意思表示との衝突」。○にするか除外にするかは意思表示の扱いに依存=Fable判断の材料)。Lane aの推奨は「除外扱い(意思表示を尊重)」。
- 実コンテンツ†: 前回(01A)が実投稿を読了(`https://anond.hatelabo.jp/20250605163449`「東京転勤を命じられたので会社辞めた」と鏡像`.../20231203220904`「田舎に転勤になって死ぬほど辛い」)。長文の一人称で品質は国内最良級。ただし今回の再読はしていない。

### 2-9 Yahoo!知恵袋・5ちゃんねる・発言小町・価格.com・Yahoo!ニュース(#9〜#13) — 除外

- **知恵袋(#9)**: 前回逐語(LINEヤフー共通利用規約14条「サービスやそれらを構成するデータを、その提供目的を超えて利用することができません」ほか、`TERMS_REVIEW_01.md:36-51`)を維持。今回再確認: robots(https://chiebukuro.yahoo.co.jp/robots.txt、2026-10-29)は`GPTBot`・`ClaudeBot`等に`Disallow: /`、全UAに`/detail/q*`・`/search`等を禁止=質問ページの取得経路自体が拒否。`lycorp.co.jp`のrobotsはHTTP 403で今日は規約再取得不可。除外維持。
- **5ch(#10)**: 今回再取得(https://www.5ch.io/matome.html)「5ちゃんねる（5ch.io）のコンテンツを用いてWEBサイトを運営している方は、5ch.io の所有者である Loki Technology, Inc. からコンテンツの使用許諾を得る必要があります。コンテンツの使用許諾を得ずに 5ch.io のスレッド内容等を使用することは、複製権や公衆送信権などの著作権侵害や商標権の侵害となり…」。除外維持。
- **発言小町(#11)**: ユーザー決定①。再調査せず維持(再利用不可)。
- **価格.com(#12、変更)**: 今回取得 https://help.kakaku.com/kiyaku_site.html(価格.com利用規約、最終改定2025年6月30日)第1編第4条「本サービスはお客様の私的かつ非営利目的でのご利用に限定して提供しています。当社が事前に承諾した場合を除き、…営業活動その他の営利を目的としたご利用またはそれに準ずる行為、そのための準備行為に利用してはならないものとします」。→除外。
- **Yahoo!ニュースコメント(#13、変更)**: 今回再確認 https://news.yahoo.co.jp/robots.txt はClaudeBot・anthropic-ai・Claude-Web・GPTBot等を拒否し、`*`に`Disallow: /articles/*/comments`(前回記録どおり)。規約はLINEヤフー共通利用規約(#9と同じ)を準用。Lane cの除外寄り提案を採用して**除外**とする(前回「アクセス不能」から変更)。

### 2-10 OKWAVE・Togetter・Surfvote(#14〜#16) — 未確認

- OKWAVE: robots(https://okwave.jp/robots.txt、2026-10-29)が`/answer`・`/ai`を禁止し、多数のAI bot(AI2Bot、Amazonbot等)を個別拒否。規約URLの推測(`/guide/terms.html`)は404で未取得。Q&A形式で生の意見が薄い(前回)。未確認(低優先度)。
- Togetter: 規約URL(`/terms`)404で未取得。Xの二次転載のため権利整理が複雑(前回)。未確認(低優先度)。
- Surfvote: 今日(2026-10-29)もrobots.txtがHTTP 503=メンテ継続。Lane cが推奨した「メンテ明け後に1回の手動再確認」を1回実施、結果は未解消。以後自動再試行は作らない。未確認。

### 2-11 Tildes(#17)

- **商用AI利用: ○**(明示許諾なし。「データは掘り出して売るためのものではない」意思表示あり)。
- 規約(https://docs.tildes.net/policies/terms-of-use、今回再取得): 「You should recognize that by submitting anything to the site, it may be archived, copied, or otherwise duplicated by any other user or automatic system that is able to access it.」/「You retain copyright and ownership of any of your own content that you submit to Tildes… However, you grant us a non-exclusive license to store, display and distribute that content in the context of operating the site」。AI・スクレイピング・商用の禁止条項なし(今回の機械検索: scrap/crawl/commercial/AI/machine learning/data miningは0件、automatは上記『automatic system』の注意文のみ)。robots(https://tildes.net/robots.txt)冒頭「In general, scrapers are welcome if they are collecting data for informational uses (such as search engines) and maintain a reasonable rate of scraping.」「Scrapers from SEO/marketing-type services will be blocked. Tildes data is not a resource to be mined and sold.」/`User-agent: *`は`Disallow: /login`のみ。
- 運営者規約と投稿者著作権: 投稿者が著作権を保持。利用者(第三者)への許諾は規約にない。→逐語利用は避け論点・経験の参考に。
- テーマ選定性: **○**。生活・仕事・メディア・SNS・人生相談など(~talk等のグループ)。ただし小規模で、~talkの7日間上位ページに表示されたトピックは2件のみ(2026-10-29)、新題材の量は少ない。
- ペルソナ性: **○**。読んだ投稿: https://tildes.net/~talk/1wm9/how_do_you_handle_being_around_other_people(53コメント、2026-10-29取得)。「I got a divorce, lost all my 'friends'…turns out I didn't suffer from anxiety. I was just spending time around the wrong people」「negative socialization is worse than no socialization」等、離婚経験・人間関係の価値観を一人称で長文に語る。立場の割れも読める。
- 量産適性: **○**。単純HTML、1スレッド約120KB、Crawl-delayなし(礼儀的に3秒以上)。新題材が少ないのがボトルネック。
- 前回との差分: 維持(通読による再確認)。

### 2-12 Lemmy(lemmy.world)(#18)

- **商用AI利用: ○**(規約にAI・スクレイピング・商用・著作権許諾の条項なし)。
- 規約(https://legal.lemmy.world/tos/、今回再取得、約2万字): scrap/crawl/AI/machine learning/data miningは0件(今回の機械検索)。『Bot Usage and Guidelines』は投稿用botアカウント(広告禁止・bot表示義務・投票禁止)の規則で、閲覧・取得の規則ではない。『commercial』は「extensive commercial advertising」を投稿する側の制限のみ。copyright/licenseは侵害コンテンツへのリンク禁止等の無関係箇所。robots(https://lemmy.world/robots.txt)=`Disallow: /search/`等+**`Crawl-delay: 60`**(今回60秒間隔で遵守)。投稿の著作権は各投稿者。フェデレーション先インスタンスは別規約。
- テーマ選定性: **○**(コミュニティ依存。asklemmy@lemmy.mlの週間上位は電球・電動歯ブラシ等の雑談が多いが、AIと職・SNS規制・子を持つ条件など議論になる題材もある)。
- ペルソナ性: **○**(断片)。読んだ投稿: lemmy.world API `post/list`(asklemmy@lemmy.ml, TopWeek)で一覧を取得し、post 53472061「Tech & Cybersecurity folks: What is your long-term plan given the AI explosion?」(11コメント)を`comment/list`で全件取得。「Non-profit sector…I work for a small member org and I get to write all the policies around everything tech. We have literally no use case for AI…my job is not at risk」/「LLMs and the ai industry…are doing things that aren't compatible with my principles so I'm looking to learn a different skill set. Currently applying to schools」/「it's overhyped…eventually it will quiet down」。職業+立場+理由は読めるが、1人あたり2〜4文で背景は薄い。
- 量産適性: **△**。Crawl-delay 60秒=1スレッド(一覧1+コメント1)で約2分。20テーマ分の取得で40分超。
- 前回との差分: 維持(○)。取得規則違反(前回)は今回60秒間隔で遵守。

### 2-13 EA Forum(#19)

- **商用AI利用: ◎**(CC BY 4.0。ただしEVF一般Terms[effectivealtruism.org/terms-and-conditions]の自動取得条項は今回も未読)。
- 規約(https://forum.effectivealtruism.org/termsOfUse、今回再取得): 2.2「When you upload Your Content to the EA Forum, you agree that you are doing so in accordance with, and on the basis that it will be made available to users on, the terms of the Creative Commons — Attribution 4.0 International — CC BY 4.0」/2.1「(Licensed Rights and Adapted Material are as defined in the Creative Commons — Attribution 4.0 International — CC BY 4.0 License)」。robots=`Crawl-Delay: 2`、`Disallow: /allPosts?*`等。
- テーマ選定性: **△**(EA内輪の前提が強い。育児と仕事・子を持つ決断・気候と出産など生活テーマの投稿もあるが、日本のリスナーには説明コストが高い。投稿は継続的に出る)。
- ペルソナ性: **○**。読んだ投稿: https://forum.effectivealtruism.org/posts/5zKfuzDxf9pjvcHxA/my-experience-of-returning-to-work-after-having-a-baby(2026-10-29取得)。筆者=2021-01出産、9か月の休業後に0.5FTEで復帰。「Context matters a lot. I'm the main carer for my child…I took 9 months off work completely…I am financially well-off, and I have a strong EA network」と属性を自己開示。コメントにも一人称の類似体験(「コロナで保育者が来られず仕事できなかった」「親の責任1000%と仕事100%を両立するのは不可能と悟った」)。ただし書き手は英語圏の裕福なEA層に偏る。
- 量産適性: **○**。SSR HTMLから本文取得可(0.3〜0.5MB)、Crawl-Delay 2秒を遵守。
- 前回との差分: 商用◎維持。ペルソナ△→○(個人記を通読)。

### 2-14 UK議会 請願サイト+Hansard(#20)

- **商用AI利用: ◎**(OGL v3.0)。
- 規約(https://petition.parliament.uk/help、今回再取得): 「© UK Parliament 2026 All content is available under the Open Government Licence v3.0, except where otherwise stated」。Hansardの複製・翻案・商用はOpen Parliament Licence(前回逐語、`FINAL_REPORT_01.md`:22)。第三者権利・動画音声は対象外。AI入力の個別明文なし。
- テーマ選定性: **○**(請願は公共政策全般[子どものSNS・学校・労働・AI教育]で常時更新。請願者/政府回答/議員発言で3系統。日本適合は普遍論点に限る)。
- ペルソナ性: **△**。読んだ資料: 請願700086「Introduce 16 as the minimum age for children to have social media」(署名132,102、2025-02-24討論)のJSON。背景は1文「We believe social media companies should be banned from letting children under 16 create social media accounts.」+政府回答のみ。請願者個人の背景は出ない。Hansard(議員の演説)は今日の`robots.txt`がHTTP 403で読めないため**今回は取得せず**(前回の記録[議員の子育て体験の引用等]を引用するのみ)。
- 量産適性: **◎**(請願JSON API・robots許可・軽量)。Hansardはrobots 403で不確実。
- 前回との差分: 維持。

### 2-15 Polis オープンデータ(#21)

- **商用AI利用: ◎**(CC BY 4.0、データに限る)。規約(https://raw.githubusercontent.com/compdemocracy/openData/master/README.md、今回再取得): 「All Polis data is licensed CC By 4.0」「All Polis data is licensed under a Creative Commons Attribution 4.0 International license」。帰属表示の定型文あり。一部データセットは出所不明で対象外(前回)。参加者の一文の権利は参加者に残りうる(CDPがCC BYで再許諾)。
- テーマ選定性: **○**(自家用車・ライドシェア・UBI・住宅・気候など。賛否票つきで拮抗する文を発掘できる。配布データは固定で新規題材は増えにくい)。
- ペルソナ性: **△**。読んだデータ: `austria-climate.5tzfrp5eaa.2022-07-07/comments.csv`(2,138件、2026-10-29取得)。賛否上位は「Klimarat: Ich bin für eine Geschwindigkeitsbegrenzung von 30km/h im Ortsgebiet…」(賛成1022/反対836)等の政策提案文で、自己開示(職業・家族・体験)はほぼ無い(前回精読0.9%)。
- 量産適性: **△**(固定データ。再取得の価値は新規データセット追加時のみ)。
- 前回との差分: 維持。

### 2-16 仏 Grand Débat National(#22) — 取得経路に重大な制約

- **商用AI利用: ◎**(Licence Ouverte 2.0。前回逐語: 「la reproduction, la redistribution, l'adaptation et l'exploitation commerciale des données」、出典表示義務。`FINAL_REPORT_01.md`:23)。
- **新事実(今回確認): `https://static.data.gouv.fr/robots.txt`の`User-agent: *`に`Disallow: /resources`・`/datasets/r/`・`/api/1/datasets/r/`がある**(2026-10-29)。前回は「robotsは資源ファイルを制限しない」と記録(`CLOSE_READING_02.md`:9)していたが誤りの可能性が高く、資源CSVの機械取得はrobotsが拒否している(ブラウザからの手動ダウンロードはライセンス上可でもrobots対象外とは言えず、判断はFable)。本書はこの意思表示を尊重し、今回はCSVを評価に使っていない(取得逸脱は§0・`deviations_01a.md`)。
- テーマ選定性: **△**(2019年の固定データ。環境転換の負担[通勤・暖房]は日本の地方とも共通だが、新題材は増えない)。
- ペルソナ性: **○†**(前回精読の引用: 638件中3要素以上18件=2.8%、断片は1〜3文。今回の再読はなし)。
- 量産適性: **△**(上記robots拒否+ファイル64MB〜)。
- 前回との差分: 取得経路の制約を新規に記録。テーマ○→△。

### 2-17 Global Voices(#23)

- **商用AI利用: ◎**。規約(https://globalvoices.org/about/global-voices-attribution-policy/、今回再取得): 「Unless otherwise stated, all content created by Global Voices is published under a Creative Commons Attribution-Only license…Adapt — remix, transform, and build upon the material for any purpose, even commercially」。第三者の画像・動画・埋込は別許諾。robots=`Crawl-delay: 10`(遵守)。
- テーマ選定性: **△**(世界の社会問題で幅・更新頻度は高いが、討論ではなく報道で、国固有色が強い)。
- ペルソナ性: **△**。読んだ記事: 2026-10-26「Vote young yet govern much later: West African youth's struggle for power」(https://globalvoices.org/2026/10/26/vote-young-yet-govern-much-later-west-african-youths-struggle-for-power/)。制度比較(被選挙権年齢)中心で、当事者の肉声は少ない。当事者の経験を伝える記事は別途選別が必要。
- 量産適性: **○**(RSS・記事HTML。10秒間隔)。
- 前回との差分: 維持。

### 2-18 Climate Assembly UK(#24)

- **商用AI利用: ◎**。規約(https://www.climateassembly.uk/、今回再取得): 「The content on Climate Assembly UK is licensed under the Open Government Licence v3.0 except where otherwise stated.」
- テーマ△・ペルソナ△: 読んだ`recommendations/index.html`は報告書の構成説明と集計で、個人の声や生活背景は掲載されていない(「Chapters 2 -11 …assembly members' views on the advantages and disadvantages」の要約のみ)。量産適性△(静的アーカイブで新規題材なし)。
- 前回との差分: 維持(未精読→公開ページは精読済み。報告書PDF本文は未読)。

### 2-19 Parlia(#25)

- **商用AI利用: ○**。規約(https://www.parlia.com/terms-of-service、2026-06更新、今回再取得): 「You own what you post. By posting on Parlia you grant us a worldwide, non-exclusive, royalty-free license to display, distribute, and store your contributions…」「The Parlia name, design, and aggregate datasets are ours. You may link to and quote Parlia pages freely with attribution.」。AI・スクレイピング・商用の禁止条項なし。robots=`Allow: /`、`Disallow: /search`。
- テーマ△・ペルソナ△: 読んだ投稿: https://www.parlia.com/o/voting-should-be-mandatory。For/Against/Mixed構造のエッセイ形式(例「It is a privilege to be able to vote…」)で体験談・人物背景なし。投稿は約2021年中心。量産適性○(単純HTML、制限なし)。
- 前回との差分: 維持。

### 2-20 Stack Exchange(#26)

- **商用AI利用: 未確認**(前回「条件付き利用可能(補助)」から変更)。内容はCC BY-SA 4.0(商用・翻案可、帰属・ShareAlike必須)だが、AUPが「generative AI/LLM/MLツールのdeveloping, building, training, testing, indexing, benchmarking, or improving」目的の自動収集を禁止し、書面同意で免除(前回逐語、`TERMS_REVIEW_01.md:179-194`)。想定用途(原稿生成での参考)がこの禁止に当たるか不明で、今日は`stackoverflow.com/robots.txt`がHTTP 418のため規約を再取得できなかった(回避しない)。→「明確な禁止も未確認」とは言えないため○にしない。
- 実コンテンツ: 公式API(api.stackexchange.com、robots.txtはHTTP 400=未設置扱いで1回のみ)で parenting.stackexchange.com の票上位質問3件を取得。質問者が家族構成を書く(「My wife and I still haven't let our 5 year old do much with our desktop PC…」)が、回答は助言型で人物像は薄い=ペルソナ△。テーマ△(助言Q&A)。量産適性△(API鍵・AUP要確認)。
- 前回との差分: 条件付き(補助)→未確認(AUP適用範囲が不明で、○の定義[明確な禁止も未確認]に合わないため)。

### 2-21 維持した除外(HN・Guardian・Mumsnet・Reddit)

- HN: YC利用規約Commercial Use「you agree not to display, distribute, license … create derivative works from … for any commercial purposes」、Site Content「you will not engage in or use any data mining, robots, scraping or similar data gathering or extraction methods」(`LANE_A_OVERSEAS_EN_01.md`:48、2026-10-29)。維持。
- Guardian: 機械学習・データ解析・商用は事前の書面承認が必要(`TERMS_REVIEW_01.md:148-163`、2026-10-28)。維持。
- Mumsnet: 1.c/1.e/1.a(コピー・AI/テキストマイニング・複製禁止)(`TERMS_REVIEW_01.md:164-178`)。維持。
- Reddit: ユーザー決定②(Data API申請見送り・回避禁止)。維持。再調査せず。


## 3. 除外・未確認(理由)

§2で再評価した除外9・未確認5を除く、§1の残りの扱い。**前回「除外」でユーザー決定・規約逐語が明確なものは再調査せず維持**した。今回の再取得で新規に確認できたものは「(今回確認)」と記す。いずれも最終一覧には載せない。

### 3-1 除外(維持。再調査せず)

| サイト | 理由(逐語は前回記録) | 根拠 |
|---|---|---|
| Kialo | 「Please don't use other means to monitor or copy any material on Kialo, either manually or through automated means (i.e., scraping), without prior written consent」+robots `*`が`Disallow: /` | `LANE_A_OVERSEAS_EN_01.md:46` |
| Intelligence Squared | 「for your personal, non-commercial use only」「not to use automated means…」 | 同:47 |
| Substack / NYT / Pew / AgingCare / AllSides / IDEA Debatabase | 手動を含むクロール禁止/個人・非商用+生成AI禁止/スクレイピング禁止/個人利用+商用禁止/AI入力を明示拒否+独占権/書面許諾必須 | 同:49-54(2-2表) |
| Perspective Daily / gutefrage.net / Naver 知識iN / The Straits Times(SPH) / Carers UK フォーラム | TDM・AI・RAG・商用・自動アクセスの明示禁止 | `LANE_B_EUROPE_ASIA_CIVIC_01.md` §3 #4-6, 8, 10 |
| 加古川市版Decidim / NADE(CC BY-NC-ND) / アゴラ(CC BY-NC) / 朝日新聞 / STORYS.JP / 世田谷版気候市民会議 | 営利禁止/非営利・改変禁止/非営利/無断翻案蓄積禁止/書面許諾必須/無断二次利用禁止 | `LANE_C_DOMESTIC_01.md` §2-2・§3 |
| 東京都・横浜市(市民意見) | 「無断で複製・転用することはできません」(引用のみ) | `PUBLIC_SOURCES_CHECK_01.md` §1(b-5) |
| Hacker News / The Guardian / Mumsnet / Reddit | §2-21参照 | — |

### 3-2 未確認(規約が読めない・条項不明確・運営の意思表示との衝突)

| 区分 | サイト | 理由 | 次の扱い(Lane aの所見。判断はFable) |
|---|---|---|---|
| 運営の意思表示と衝突 | はてな匿名ダイアリー(増田)、Ask a Manager、ZEIT ONLINE、Quora(日本語)、OKWAVE | robotsがAI botを名指しで拒否(Ask a Manager・Quoraは`ai-train=no`/AI学習の契約許諾なし利用を禁止する旨)。規約に明文の禁止は無いか、規約を読めない | 意思表示を尊重し、運営への許諾照会が得られるまで採用しない(除外扱いを推奨) |
| 規約を読めない/特定できない | LessWrong、Medium、DebateWise、Munk Debates、Oxford Union、DebateGraph、Mr. Money Mustache forum、Alzheimer's Society forum、BabyCenter / Netmums(今回も規約URLが404/403)、MoneySavingExpert(今回403)、Zhihu、Rappler、Doctissimo、Make.org、openDemocracy、Togetter、SYNODOS、サイボウズ式、Change.org日本、はてなブックマーク | 規約URL不明・403/404・条項が曖昧。Change.org日本は「スクレイピングは明示的に禁止…robots.txtの条項に従い実施される場合にはクロールは認める」旨(`LANE_C_DOMESTIC_01.md` §2-2)で部分許容だが商用AIの記載なし | 今回の範囲では○にできる材料なし。適性が高いものだけ照会価値あり(Ask a Manager、Make.org、ABEMA TIMES等) |
| アクセス不能(規約の評価ではない) | Surfvote(503)、こども若者★いけんぷらす(403)、PoliPoli(JS描画)、ABEMA TIMES(規約JS描画)、Metafilter/Ask MetaFilter・Bogleheads・Living Room Conversations・NYTコメント・Japan Today・TheStudentRoom・Fark・Debating Matters・ProCon.org・WEF・OECD・Decidim Barcelona(403)、転職会議/OpenWork(会員壁)、X/Threads(ログイン壁) | Cloudflare/Akamai等の遮断・メンテ・ログイン壁。回避しない | 遮断の解除や公式データ提供の有無を待つ(Surfvoteはメンテ明けに1回の手動再確認) |
| 内容が目的外/国固有 | Debating Europe(公開討論なし)、デジタル民主主義2030(政党・自治体運用)、EU Have Your Say(第三者投稿・国固有寄り)、Citizens' Assembly(アイルランド、All rights reserved)、The Conversation(CC BY-ND) | 公開討論なし、国固有、権利留保、NDで翻案が不明 | The Conversationは翻案が想定用途に当たらないと断定できず○にしない(前回のFable所見のまま) |
| 内閣府・他府省・国民生活センター | 内閣府、文科省・国交省・経産省等、国民生活センター相談事例 | 規約ページ取得不能または許可要(`PUBLIC_SOURCES_CHECK_01.md` §1(b-3)(b-4)(c)) | 他府省の規約確認は別途(PDL1.0準拠なら◎化の余地) |

### 3-3 サービス終了・実質不在

教えて!goo(2025-09-17終了)、ウィメンズパーク(DNS解決不可)、NHK みんなでプラス(2026-09-30終了)、BBC Have Your Say・Japan Timesコメント(実質終了/不在)、DebateArt(カジノ広告へ転送)、CreateDebate(ドメインパーキング)、IDEA Debatabase現行サイト(接続不能)、Le Drenche(名前解決不可)。


## 4. Lane aの所見(判断はFable。事実と観測値のみ)

1. **種別の偏り(今回の◎/○16件)**: 掲示板・コミュニティ型4(ガルちゃん、ママスタ、Tildes、Lemmy)/個人発信1(note)/公的記録・議事録・報告書7(国会会議録、e-Gov+厚労省、厚労省審議会、気候市民会議さっぽろ、UK請願+Hansard、Grand Débat、CAUK)/データ・論点整理2(Polis、Parlia)/討論フォーラム1(EA Forum)/市民メディア1(Global Voices)。国内7・海外9。Debate型に置き換わったのではなく、前回の掲示板型3(ガルちゃん・ママスタ・note)は全て維持されている。
2. **構造的なトレードオフ(観測)**: 規約で◎(商用・翻案の明示許諾)が取れる源は公的/オープンライセンス系(e-Gov、厚労省、UK請願、Polis、EA Forum、Global Voices、CAUK、Grand Débat)に集中し、人物像はペルソナ△〜○と薄い(○はEA Forum・Grand Débat†のみ)。人物像が厚い源(ガルちゃん◎、note◎、国会会議録○)は商用が○止まり(明示許可なし)。◎×ペルソナ◎の組合せは今回のLane aの範囲では存在しなかった。
3. **国内の生活密着型は実質3源に集約**: 知恵袋・発言小町・5ch・価格.com・OKWAVE・増田・Yahoo!ニュースは規約上の禁止、許諾必須、またはrobotsのAI bot拒否で◎/○にできない(価格.comは今回の規約取得で除外へ変更)。残るのはガルちゃん・ママスタ・noteで、ガルちゃんとママスタは「AI入力・自動収集に明文の許諾も禁止もない」同じ不確実性を共有し、運営照会の結果次第で同時に失われる(前回§3の横断リスクと同じ)。
4. **前回記録の訂正事項(委任_02で反映案)**: (a) Grand Débatの資源ファイルはrobotsで拒否されている(前回は「対象外」と記録)ため、量産適性△・自動取得は不可。(b) 価格.comを除外へ、Yahoo!ニュースコメントを除外へ、Stack Exchangeを未確認へ変更。(c) Hansardのrobotsは今日HTTP 403で読めず取得していない(前回は取得できていた)。(d) 前回のLemmy `Crawl-delay: 60`違反は今回遵守して再調査。
5. **量産適性の差**: ◎=ガルちゃん・国会会議録・UK請願(軽量・制限なし)。△=Lemmy(60秒/呼出)、Polis・CAUK・さっぽろ(固定データ)、Grand Débat(robots拒否)。note・EA・e-Gov・厚労省は○(発見や抽出に手間)。取得費用はLLM費用0で、差は工数のみ。
6. **今回の実コンテンツ読了の範囲**: ガルちゃん2トピ、ママスタ1トピ、note2記事、国会1会議(参考人4名)、e-Gov PDF1件、Tildes1スレッド(53件)、Lemmy1スレッド(11件)、EA Forum1記事+コメント、Parlia1トピ、Polis1データセット、Global Voices1記事、UK請願1件、気候市民会議さっぽろ報告書、CAUK1ページ、Stack Exchange3質問。**読めていない**: 厚労省審議会議事録本文、Hansard本文、Grand Débat(取得を逸脱として破棄)、増田・知恵袋(robotsのAI bot拒否により再取得せず、前回記録を引用)。
7. **新規候補の記録(担当外、名前のみ)**: 今回の作業中に新規に探索はしていない(Lane 01b/01cの担当)。

## 5. 取得記録と逸脱

- 取得記録: `docs/research/FAMILY-Y-SOURCE-FINAL-SHORTLIST-01/lane_a_evidence/fetch_log_01a.tsv`(時刻・URL・HTTPステータス・サイズ)。robots判定で未取得にしたもの(Hansard 403、lycorp 403、stackoverflow 418、surfvote 503)も記録。
- 逸脱: `lane_a_evidence/deviations_01a.md`(Grand Débat資源CSVへのRange取得1回。内容破棄・評価未使用)。
- 前回のrobots記録の誤り(Grand Débat)は§2-16と§4-4(a)に記載。

