# TERMS_REVIEW_01 (FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02A: 候補情報源の利用規約・ポリシー精査と用途適合判定)

確認日: 2026-10-28(全規約を同日に取得)。LLM不使用・API費用0円。取得は`terms_evidence/fetch_log_*.json`(URL・取得時刻・本文sha256)、逐語抜粋は`terms_evidence/excerpts_verified_02A.json`(56件、取得本文との機械照合 56/56一致)。全文は`terms_evidence/cache/`にローカル保存のみ(commitしない)。本書の「抜粋」は上記JSONの`site/cache/loc`で引ける。**本書は法的助言ではない。**

## 0. 想定用途と判定基準

- Family Yの想定用途: 実際の投稿から意見・経験・価値観を読み取り、それを参考に独自のPersona・一人称原稿をAIで生成し、商用の英語学習ラジオで提供する(USER_02 §4)。
- 重要な前提: 調査・制作で投稿本文を読むのは人間ではなくAI(Claude)であり、「読む」=**AIへの入力**になる。規約が「人が読む」ことしか想定していないサイトは、AI入力について実質未確認になる。
- 判定区分: 利用可能 / 条件付き利用可能(条件明記) / 未確認 / 利用不可。判断が割れる場合は未確認または条件付きに倒した。「禁止条文が見つからない」=「可」とは書かない(その場合は「該当条文なし」と記す)。
- 日本法の一般的事実(法的助言ではない): 著作権法30条の4は、情報解析のための利用を、権利者の利益を不当に害する場合等を除いて著作権者の許諾なく認める。32条は公表された著作物の引用を一定要件で認める。ただし(a)30条の4は契約(利用規約)による制限を排除する規定ではなく、規約が自動収集・解析を禁止していれば契約上の問題は別に残る、(b)海外サイトは当該国の法・規約が問題になる。以下、規約が30条の4相当の利用を明示的に制限している箇所は「契約で制限」と記した。
- 以下の「区別」: 【規約上の禁止】=規約・ライセンスが想定用途と明確に抵触。【アクセス不能】=bot遮断等で規約本文または投稿本文を取得できない。【低優先度】=規約上は支障が見えないが品質上の優先度が低い。

## 1. 判定一覧(結論)

| サイト | 判定 | 区別 | 決め手(逐語はJSON参照) |
|---|---|---|---|
| 発言小町 | 利用不可(ユーザー決定①) | 規約上の禁止+ユーザー決定 | 判定不要。01A§0の第7条(テキストマイニング・自動収集・生成AI・営利を禁止)とUSER_02①で除外。本書は再判定しない |
| Reddit | 対象外(ユーザー決定②) | ユーザー決定 | 公式Data API申請見送り・自動収集対象外。再判定しない |
| Yahoo!知恵袋 | **利用不可**(自動収集・AI入力)。人手のみの閲覧は未確認 | 規約上の禁止 | LINEヤフー共通利用規約14条「サービスやそれらを構成するデータを、その提供目的を超えて利用することができません」、8.3、robots.txtで`/detail/q*`等をDisallow |
| ガールズちゃんねる | **条件付き利用可能**(AI入力・自動収集は明文なし=重大な不確実性が残る) | — | 規約に自動収集・AI・商用の禁止条文なし、robotsは`/admins/`のみ。一方、第13条で二次利用を許諾されるのは「運営者および運営者が許諾した第三者」のみ(著作権は投稿者に帰属) |
| 増田(はてな匿名ダイアリー) | **未確認**(採用しない) | 規約は明文禁止なしだが、robots.txtがAI crawlerを明示Disallow | robots.txtがClaudeBot・anthropic-ai・GPTBot等を全面Disallow(運営の意思表示)。はてな規約は機械的アクセス者も規約の適用対象と定め、匿名ダイアリーヘルプは「無断での転載等」への注意を明記 |
| ママスタBBS | **条件付き利用可能**(AI入力・自動収集は明文なし=重大な不確実性が残る) | — | 第12条1項で投稿の著作権は投稿者に帰属、第3項の転載・複製禁止は運営の記事・コラム等。robotsはClaudeBotにCrawl-Delay 1を指定(許可、遅延遵守が条件) |
| 5ちゃんねる | **利用不可**(許諾未取得) | 規約上の禁止(ライセンス要) | 運営者告知「5ch.io のスレッド内容等を使用することは、複製権や公衆送信権などの著作権侵害」、使用許諾が必要(広告設置・リンク等のルールあり) |
| note | **条件付き利用可能**(補助素材のみ) | 低優先度(筆者1人の体験) | 記事の著作権は各クリエイターに帰属、運営は機械学習用に第三者へ提供する権利を持つが、第三者の利用許諾条項はなし。robotsは`/api/*`等のみDisallow |
| Hacker News | **未確認**(採用しない) | 重大な不確実性 | Y Combinator利用規約「data mining, robots, scraping or similar data gathering or extraction methods」を禁止、商用の複製・派生物作成を禁止(「expressly authorized herein or in the Site」を除く)。公式Firebase API・Algolia APIの利用条件文書は取得できず(Algolia側はJS描画のみ) |
| The Guardian | **利用不可**(現状。商用ライセンスで条件付きに転じる可能性) | 規約上の禁止(ライセンス要) | 利用規約「machine learning ... or artificial intelligence-related purposes」「text and data aggregation, analysis or mining」「any commercial use」を事前の書面承認なしに禁止、robots.txtより規約が優先と明記。Open Platformは商用鍵(有料・価格は利用量次第)で生成AI・テキストマイニング用途を許可 |
| Mumsnet | **利用不可**(自動収集・AI入力。人手の閲覧のみ条件付き) | 規約上の禁止 | 1.c「scraped or copied for any purpose without express approval and a licence」、1.e AI/テキストマイニング禁止、1.a「Reproduction ... is prohibited」。2025-07-22改定 |
| Stack Exchange | **条件付き利用可能**(補助素材。解釈リスクあり) | 低優先度(回答は助言中心) | 投稿はCC BY-SA 4.0(帰属・ShareAlike)。API経由は公式経路だがAUPが「generative AI ... improving」目的の自動収集を禁止(書面同意で免除)。HTMLはbot遮断(HTTP 418)でアクセス不能 |

**利用可能(無条件)はゼロ。** 条件付き=ガールズちゃんねる・ママスタBBS・note・Stack Exchange。

## 2. サイト別確認表

凡例: 「抜粋」の出典は`excerpts_verified_02A.json`の`cache`名+`loc`。「該当条文なし」は、該当語(クロール/スクレイピング/ボット/自動/解析/AI/機械学習/営利/商用/転載/複製/引用/許諾/ライセンス)で取得本文を検索して見つからなかった意味であり、「禁止がない=可」の意味ではない。

### 2-1 Yahoo!知恵袋(LINEヤフー共通利用規約 + 知恵袋利用のルール)

URL: `https://www.lycorp.co.jp/ja/company/terms/`(sha256 `7c194966…`)、`https://chiebukuro.yahoo.co.jp/topic/guide/rule/`、`https://chiebukuro.yahoo.co.jp/robots.txt`(2026-10-28取得)。知恵袋ガイドラインのヘルプ記事(support.yahoo-net.jp)はJS描画のみで本文取得不可、`policies.yahoo.co.jp/agreement/`は接続不能。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 規約上は「BOT、チートツール、その他の技術的手段を利用して当社サービスを不正に操作する行為」を禁止(15条(5))。さらに14条でサービスを構成するデータの目的外利用を禁止。robotsは`/detail/q*`,`/search`,`/tag`等をDisallow(01Aで`detail.chiebukuro.yahoo.co.jp`側も確認) | ly_terms 14条/15条(5)、chie_robots robots |
| 文章解析・AI入力 | 該当条文なし(解析の語はない)。ただし14条の「提供目的を超えて利用」に該当しうる(AI生成への投入は知恵袋の提供目的ではない)。robotsはClaudeBot・GPTBot等を明示Disallow | ly_terms 14条、chie_robots |
| AI原稿の参考素材 | 明文なし。14条により不確実(未確認寄り) | — |
| 商用 | 15条(11)「営業、宣伝、広告、勧誘、その他営利を目的とする行為」を禁止(LY「当社の認めたものを除く」)。ユーザーの商用二次利用を許可する条文はなし | ly_terms 15条(11) |
| 引用・要約・翻案・転載 | 本コンテンツの複製・送信・転載・改変は「当社サービスが予定している利用態様を超えて」禁止(8.3)。投稿の著作権は投稿者側に残る(9.2)が、第三者への許諾はLYにのみ(9.2第2段落) | ly_terms 8.3/9.2 |
| 個人情報・プライバシー | 個人情報等の公開を禁止(chie_rule 禁止事項)。取得側の扱いについて個別条文なし | chie_rule |
| 必要なライセンス・許諾 | 該当なし(許諾窓口の記載なし)。LYに利用許諾を照会する以外に経路なし | — |

判定: **利用不可(自動収集・AI入力)**。人手のみの着想利用は「未確認」(14条の射程が不明)。【規約上の禁止】。01A/OPINION_BASED_02で取得済みの知恵袋素材は、本判定により再利用の根拠にならない(是正要否はFable判断)。

### 2-2 ガールズちゃんねる

URL: `https://girlschannel.net/agreement.html`(sha256 `9ec17479…`)、`https://girlschannel.net/robots.txt`(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 該当条文なし。robotsは`Disallow: /admins/`のみ | girls_robots robots |
| 文章解析・AI入力 | 該当条文なし(未確認) | — |
| AI原稿の参考素材 | 該当条文なし(未確認) | — |
| 商用 | 該当条文なし。第9条の禁止事項は広告・勧誘コメント等で、サイト利用者の商用二次利用への言及なし | — |
| 引用・要約・翻案・転載 | 投稿の著作権は投稿者に帰属。投稿者が二次利用(引用、転載、複製、翻案、研究・開発・調査のための利用等)を許諾する相手は「運営者および運営者が許諾した第三者」のみ。一般の閲覧者への許諾条項はなし | girls_terms 第13条 |
| 個人情報・プライバシー | 名誉毀損・プライバシー侵害を禁止(第8〜9条)。個人情報の取得側の扱いは個別条文なし | — |
| robots・アクセス制限 | robotsは上記のみ。アクセス過多は免責条項に言及(第14条) | girls_robots |
| 必要なライセンス・許諾 | 運営者への二次利用許諾の照会が確実な手段(未実施) | girls_terms 第13条 |

判定: **条件付き利用可能**。条件: (1)投稿の逐語転載・固有の言い回しの再利用をしない(意見の傾向・論点・事情のみを自分の言葉でPersona化する。引用するなら32条要件を満たし出典明示)、(2)低頻度・低負荷の取得(1.6秒以上間隔)、(3)個人が特定できる情報・他者のプライバシーは取り込まない、(4)AI入力・自動収集に明文の許諾も禁止もないため、量産前に運営へ照会して書面回答を得るのが望ましい。残る不確実性: 規約が第三者の利用を許諾していないため、著作権法30条の4・32条など法定の範囲を超える利用は許諾が要る。契約で30条の4を制限する条文はなし。

### 2-3 増田(はてな匿名ダイアリー)

URL: `https://policies.hatena.ne.jp/rule`(はてな利用規約、sha256 `afcda844…`)、`https://policies.hatena.ne.jp/laborule`(はてラボ利用規約)、`https://anond.hatelabo.jp/help`、`https://anond.hatelabo.jp/robots.txt`(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 禁止条文なし。ただし機械的アクセス者も規約の適用対象(ゲストユーザー)と定義 | hatena_terms 第2条4項 |
| 文章解析・AI入力 | 該当条文なし。**robots.txtがClaudeBot・anthropic-ai・Claude-Web・GPTBot・Google-Extended・CCBot・PerplexityBot等を全面Disallow**(運営のAI取得拒否の意思表示) | hatena_robots |
| AI原稿の参考素材 | 該当条文なし(未確認)。robotsの意思表示と衝突する疑い | — |
| 商用 | 利用者の「宣伝や商用を目的とした広告・勧誘その他の行為」を禁止(本サービス内の行為) | hatena_terms 第6条3項a |
| 引用・要約・翻案・転載 | 著作権は投稿者が保有。匿名でも著作権は放棄されておらず「無断での転載等を行わないよう」注意。運営は投稿を学術研究データとして提供できる権利を持つが第三者へのそれは書かれていない | anond_help、hatelabo_rule 第6条3項、hatena_terms 第8条4項 |
| 個人情報・プライバシー | 他人の個人情報を収集・蓄積する行為を禁止(第6条の列挙) | hatena_terms |
| 必要なライセンス・許諾 | 照会窓口あり(はてな問い合わせ)。未実施 | — |

判定: **未確認**(5テーマの根拠に採用しない)。理由: 規約に明文の禁止はないが、robots.txtが想定用途(AI入力)と同種の取得を明示拒否しており、規約上も機械的アクセスが規約対象。AI用途の許諾が確認できない。【規約上の禁止ではなく、運営の意思表示との衝突=解釈不確実】。

### 2-4 ママスタBBS

URL: `https://mamastar.jp/info/rule`(ママスタ利用規約、sha256 `1ff8063d…`)、`https://mamastar.jp/info/privacy`、`https://mamastar.jp/robots.txt`(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 禁止条文なし(第11条の禁止事項は不正アクセス・有害プログラム等)。robotsは`/mypage/bbs/`,`/v1/api/`をDisallow、ClaudeBotにCrawl-Delay 1(許可、遅延指定) | mamasta_robots |
| 文章解析・AI入力 | 該当条文なし(未確認) | — |
| AI原稿の参考素材 | 該当条文なし(未確認) | — |
| 商用 | 第11条(10)「営利を目的とした書き込み等」を禁止(サイト内の行為)。利用者の商用二次利用への言及なし | mamasta_terms |
| 引用・要約・翻案・転載 | 投稿の著作権は投稿者に帰属(第12条1項)。運営は投稿を提携媒体等で利用でき(第12条2項)、運営コンテンツ(記事・ニュース・漫画・コラム)の転載・複製は禁止(同3項)。投稿そのものの第三者利用許諾はなし | mamasta_terms 第12条 |
| 個人情報・プライバシー | 第11条(12)「他人の個人情報を収集、蓄積する行為」を禁止 | mamasta_terms 第11条(12) |
| 必要なライセンス・許諾 | 運営への照会が確実(未実施) | — |

判定: **条件付き利用可能**。条件: ガールズちゃんねると同じ(逐語転載なし・低負荷でCrawl-Delay遵守・個人情報を取り込まない・量産前に運営照会が望ましい)。追加条件: 運営の記事・コラム・ニュース・漫画は素材にしない(第12条3項)。残る不確実性: AI入力の明文なし、第三者への許諾なし。

### 2-5 5ちゃんねる(5ch.io / 5ch.net)

URL: `https://www.5ch.io/matome.html`(まとめ・アプリ運営者向け使用許諾案内、sha256 `da9dc27a…`)、`https://5ch.net/`のフッター、`https://5ch.io/robots.txt`、`https://kizuna.5ch.io/robots.txt`(取得2026-10-28)。**利用規約本体(5ch.net/5ch.io共通の利用規約)の本文は、探索したURLが404または到達不能で取得できていない**(未取得)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 条文は未取得。robots.txtは`Disallow: *.dat`と`/test/bbs.cgi`(kizuna.5ch.io) | 5ch_io_robots_kizuna |
| 文章解析・AI入力 | 該当条文なし(規約本体未取得のため未確認) | — |
| AI原稿の参考素材 | 同上 | — |
| 商用 | 運営者の使用許諾が必要(下記) | 5ch_matome |
| 引用・要約・翻案・転載 | 「コンテンツの無断複写、転載を禁じます」「5ch.ioにおけるコンテンツの権利はLoki Technology, Inc. に帰属します」。コンテンツを用いてWEBサイトを運営する者は使用許諾が必要、許諾なしの使用は複製権・公衆送信権の侵害 | 5ch_top フッター、5ch_matome |
| 必要なライセンス・許諾 | Loki Technology, Inc.の使用許諾(まとめサイト向けルール: 引用元リンク・指定広告の設置等。ラジオ制作向けの許諾枠は記載なし) | 5ch_matome |

判定: **利用不可**(現状)。想定用途(スレッド内容を素材にした商用コンテンツ)は、運営が「使用許諾を得る必要がある」と明示する範囲に該当する。【規約上の禁止(ライセンス要)】。許諾を得る場合の条件(広告設置等)がラジオ形態に適合するかも不明で、新規の外部交渉になる。

### 2-6 note

URL: `https://terms.help-note.com/hc/ja/articles/44943817565465`(note ご利用規約、sha256 `8fff0476…`)、`https://terms.help-note.com/hc/ja/articles/44948981050649`(プライバシー)、`https://note.com/robots.txt`(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 該当条文なし。robotsは`/api/*`,`/search`,`/*/followers`等のDisallow(記事ページはDisallowではない) | note_robots |
| 文章解析・AI入力 | 運営が「機械学習等の学習データとして第三者に…提供する」権利を持つ旨の条項はあるが、第三者(利用者)自身がAI解析する権利は書かれていない | note_terms 機械学習 |
| AI原稿の参考素材 | 該当条文なし(未確認) | — |
| 商用 | デジタルコンテンツを「購読契約の範囲を超えて利用すること」を禁止(購入記事)。無料公開記事の商用二次利用への言及なし | note_terms 禁止事項 |
| 引用・要約・翻案・転載 | 著作権はクリエイターに帰属。複製・翻案は「クリエイターの承諾があるもの」を除き購読契約の範囲を超えて禁止 | note_terms 著作権 |
| 個人情報・プライバシー | 利用者のメッセージ等は運営の検知対象。公開記事の取り込みに関する個別条文なし | — |
| 必要なライセンス・許諾 | クリエイター個別の承諾(逐語利用する場合) | — |

判定: **条件付き利用可能(補助素材のみ)**。条件: 公開(無料)記事のみ、逐語転載なし、意見・事情のみを自分の言葉でPersona化、API(`/api/*`)は使わず記事ページを低頻度で取得。品質上、筆者1人の体験談で3視点の主材料にならない(01A§3-7)ため【低優先度】。

### 2-7 Hacker News(news.ycombinator.com / Y Combinator)

URL: `https://www.ycombinator.com/legal/`(Terms of Use、sha256 `18e7b772…`)、`https://news.ycombinator.com/newsguidelines.html`、`https://news.ycombinator.com/robots.txt`、`https://github.com/HackerNews/API`(公式APIのREADME)、`https://hn.algolia.com/api`(JS描画のみ、規約本文は取得できず)(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 規約は「data mining, robots, scraping or similar data gathering or extraction methods」を禁止(Site/Site Content)。robotsはCrawl-delay 30。公式Firebase APIは「There is currently no rate limit.」と記すが、APIの利用条件・商用可否の記載なし | hn_terms Site Content、hn_robots、hn_api |
| 文章解析・AI入力 | 該当条文なし(AI/解析の語は規約に見つからない)。ただしscraping・data miningを一般に禁止 | hn_terms |
| AI原稿の参考素材 | 該当条文なし(未確認) | — |
| 商用 | 「Unless otherwise expressly authorized herein or in the Site」、Siteのいかなる部分も商用目的で複製・派生物作成等しないと同意 | hn_terms Commercial Use |
| 引用・要約・翻案・転載 | ユーザーは自身の投稿の権利を保有し、YCに広いライセンスを付与。第三者向けライセンス条項なし | hn_terms User Content |
| 個人情報・プライバシー | HNのユーザー名・投稿はPersonal Informationに含まれない旨(privacy policy)。個人プロフィール(about欄)は別 | hn_terms privacy節 |
| 必要なライセンス・許諾 | 公式APIがこの「Siteにおける明示の許可(expressly authorized ... in the Site)」に当たるかは不明。YCへの照会(api@ycombinator.com / hn@ycombinator.com)が必要 | — |

判定: **未確認**(5テーマの根拠に採用しない)。重大な不確実性: (a)規約はスクレイピング・データマイニングと商用の派生物作成を禁止、(b)公式APIが許諾の根拠になるかは書かれていない、(c)Algolia検索APIの条件は取得不能。**01Bの「規約上扱いやすい」(OVERSEAS_SOURCES_01 §0)は、本精査により訂正する(扱いやすいとは言えない)。**【アクセス不能(Algolia条件)+規約上の重大な不確実性】。

### 2-8 The Guardian(theguardian.com / Open Platform)

URL: `https://www.theguardian.com/help/terms-of-service`(sha256 `40930f7f…`)、`https://open-platform.theguardian.com/access/`、`https://www.theguardian.com/robots.txt`(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 事前の書面承認なしにscrape・collect・mine・extractを禁止、robot/bot/spider/crawlerも禁止。robots.txtより規約が優先と明記 | guardian_terms Guardian Content、ToS robots |
| 文章解析・AI入力 | 「(a) any machine learning ... or artificial intelligence-related purposes」「(b) text and data aggregation, analysis or mining」「(c) with any machine learning and/or artificial intelligence technologies to generate any data or content」を事前の書面承認なしに禁止(EU 2019/790 4条(3)の権利留保を明記)=**契約で情報解析を制限** | guardian_terms |
| AI原稿の参考素材 | 上記(c)に該当 | guardian_terms |
| 商用 | 通常のサイト利用は「personal and non-commercial use only」。Open Platformのdeveloper鍵は非商用のみ、商用鍵は「training models for generative artificial intelligence services, text and data mining solutions, sentiment analysis where content is not reproduced」等を含む有料枠 | guardian_terms、guardian_api_terms |
| 引用・要約・翻案・転載 | 規約上、記事の複製等を禁止(personal/non-commercial以外)。読者投稿は投稿者が著作権を保持、Guardianが第三者に再許諾できる権利を持つ | guardian_terms user content |
| 個人情報・プライバシー | 読者コメントは公開投稿(個別の取得側条文なし) | — |
| 必要なライセンス・許諾 | 商用鍵(Commercial)または書面承認(licensing@theguardian.com)。価格は利用量次第で非公開。商用鍵が読者コメント(discussion)を含むかは文面から未確認 | guardian_api_terms |

判定: **利用不可**(現状)。商用鍵契約で条件付きに転じる可能性はあるが、コメント欄が対象か未確認で、有料・新規契約。【規約上の禁止(ライセンス要)】。

### 2-9 Mumsnet

URL: `https://www.mumsnet.com/info/terms-of-use`(2025-07-22改定、sha256 `0dcbccd8…`)、`https://www.mumsnet.com/robots.txt`(取得2026-10-28。`/info/talk-guidelines`は404でTalk guidelinesは未取得)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | 「No part of the Website may be distributed, scraped or copied for any purpose without express approval and a licence」。robotsはGPTBot等をDisallow | mumsnet_terms 1.c、mumsnet_robots |
| 文章解析・AI入力 | AI/ML学習・ファインチューニング・検証目的のテキストデータマイニング・自動抽出を禁止、またはWebsiteの内容を複製・競合するデータセット作成を禁止。例外=検索インデックス・抜粋・出典表示(substantial portionsを複製しない場合) | mumsnet_terms 1.e(1)(2) |
| AI原稿の参考素材 | 明文は学習目的の禁止が中心だが、1.cの「for any purpose」禁止が適用されるため不可 | mumsnet_terms 1.c |
| 商用 | 該当条文なし(商用ライセンス窓口の記載あり) | — |
| 引用・要約・翻案・転載 | 「Reproduction of all or any part of the Website in any form is prohibited」。ユーザーの著作権は投稿者に残る | mumsnet_terms 1.a/User Content |
| 必要なライセンス・許諾 | Mumsnetへの照会(licence) | mumsnet_terms 1.c |

判定: **利用不可**(自動収集・AI入力)。人手による閲覧のみ条件付き。【規約上の禁止】。

### 2-10 Stack Exchange(workplace.stackexchange.com等)

URL: `https://stackoverflow.com/legal/terms-of-service/public`(Public Network Terms、sha256 `53031184…`)、`https://stackoverflow.com/legal/acceptable-use-policy`(AUP)、`https://stackoverflow.com/legal/api-terms-of-use`(API規約)。`robots.txt`は私のUAでHTTP 418(bot遮断)、HTMLは取得不能=【アクセス不能】(APIが公式経路)(取得2026-10-28)。

| 項目 | 結果 | 抜粋 |
|---|---|---|
| 自動収集・スクレイピング | AUPはautomated system(spider/bot/scraper等)での収集を、(i)類似・競合サービスの構築、(ii)generative AI/LLM/MLツールの「developing, building, training, testing, indexing, benchmarking, or improving」の目的では禁止。書面同意で免除(商用ライセンス等) | se_aup |
| 文章解析・AI入力 | 上記(ii)に該当しうる(原稿生成は生成AIツールの運用であり、モデルの開発・訓練・改善ではない=解釈が分かれる。**重大ではないが不確実**) | se_aup |
| AI原稿の参考素材 | 同上 | se_aup |
| 商用 | 投稿はCC BY-SA 4.0(商用利用・翻案可、帰属表示とShareAlike必須)。API/データダンプ経由の内容は個人・非商用限定から除外されている | se_terms 6 |
| 引用・要約・翻案・転載 | CC BY-SA 4.0の要件(帰属: 質問への直接リンクと著者名リンク等)。翻案するとShareAlikeが波及。API利用はStack Exchangeが出典であることの視覚表示義務 | se_terms 6、se_api API Attribution、se_attr |
| 個人情報・プライバシー | AUPで個人を特定しうる情報の公開を禁止。投稿者名の取扱いは帰属表示が必要 | se_aup |
| 必要なライセンス・許諾 | 書面同意(AUP免除)またはStack Data Licensing。API規約上は鍵の取得 | se_aup |

判定: **条件付き利用可能(補助素材のみ・要書面確認が望ましい)**。条件: API経由のみ、逐語利用せず意見・事情の着想のみ(ShareAlike回避)、帰属表示、量産前にAUPの「generative AI ... improving」適用外であることをStack Exchangeに書面確認。回答は助言が中心でVoiceの主観体験が薄い(01B§5)ため【低優先度】。

## 3. 判定の取りまとめ

### 3-1 利用可能・条件付きのサイト一覧

- 利用可能(無条件): なし。
- 条件付き利用可能: ガールズちゃんねる、ママスタBBS(国内の主材料)。note、Stack Exchange(補助のみ)。共通条件=逐語転載なし・低負荷・個人情報を取り込まない・量産前に運営へAI入力の可否を書面照会(推奨)。
- 未確認(採用しない): 増田、Hacker News。
- 利用不可: Yahoo!知恵袋、5ちゃんねる、The Guardian、Mumsnet、発言小町(ユーザー決定①)。
- 対象外: Reddit(ユーザー決定②)。

### 3-2 5テーマの根拠資料に使えるサイト

使えるのは「ガールズちゃんねる」「ママスタBBS」(主)と「note」「Stack Exchange」(補助)のみ。01A/01Bのテーマ候補を規約面だけで照合すると次のとおり(テーマの最終選定自体は本委任の範囲外):

- 規約面で成立し得る国内テーマ: T3 田舎の裕福さ(ガルちゃん)、T6 共感される弱者の演出(ガルちゃん)、T9 令和ネーム(ガルちゃん)、T7 3号年金(ママスタ)。いずれも根拠が単一サイトに偏る点が品質上の注意。
- 成立しない国内テーマ: T4・T5・T8・T10(小町のみ=除外)、T1(知恵袋・小町・note中心。noteは補助)、T2(増田・知恵袋・5ch中心)。
- 海外テーマ10件: 主材料がHN・Guardian・Mumsnet・Reddit・SEのため、HNが書面確認されるまで採用可能なものは実質ない(SEとMozilla日本語コミュニティ系は補助)。
- ガルちゃん・ママスタの2サイトだけで5テーマに届くか(4テーマ)は品質面の別検討。不足分は別の国内情報源の規約確認(本書に載せていない: 価格.com、OKWAVE、Togetter等は01Aで低評価)か、運営照会による解禁待ち。

### 3-3 残る不確実性

1. ガルちゃん・ママスタ・note: 規約はAI入力・自動収集・商用二次利用を許諾も禁止もしていない(第三者への許諾なし)。日本法30条の4で解析自体は許される可能性があるが、契約上の確認は未実施。
2. HN: 公式API・Algolia APIの利用条件を取得できず、YC規約はscraping/data miningを禁止。
3. 増田: robots.txtのAI crawler拒否と想定用途の関係。
4. Stack Exchange: AUPのgenerative AI目的規定の適用範囲。
5. 5ch規約本体・知恵袋ガイドライン本文・SE robots・Mumsnet Talk guidelines・LY policies.yahoo.co.jpは本文未取得。

### 3-4 既存調査との整合(参考)

OPINION_BASED_02(宅配再配達)の素材(小町16件・知恵袋38件・はてなブックマークコメント3件)は、本判定では小町=除外、知恵袋=利用不可のため、そのまま次回制作の根拠にならない。既存Trialの是正要否は本委任の範囲外(Fable判断)。

## 4. 取得できなかった・未取得の資料

`policies.yahoo.co.jp/agreement/`(接続不能)、知恵袋ガイドライン(support.yahoo-net.jp、JS描画)、5ch利用規約本体(探索URL全て404)、Mumsnet Talk guidelines(404)、`workplace.stackexchange.com/robots.txt`・`stackoverflow.com/robots.txt`(HTTP 418)、Algolia HN Search API条件(JS描画のみ)。これらは「未確認」として扱い、可否の根拠にしていない。
