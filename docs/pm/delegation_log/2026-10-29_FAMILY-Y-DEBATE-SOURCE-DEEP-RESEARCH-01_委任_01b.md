Fableからの委任_01b(管理ID: FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01。Lane b=**欧州・アジア・非英語圏のDebate/Discussion、市民討論・公開討論・熟議プラットフォーム、CC/オープンライセンス系の多様意見メディア**。調査のみ、API(LLM)0、Production変更なし)。

## 0. 開始手順
- 本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_委任_01b.md` に逐語保存(heredoc失敗時はpy)。
- `tools/stop_scope_check_01.py --managed-id FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/stop_check_01b.json`(rc=3で停止)。
- ユーザー原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`(並行Workerが保存中。着手後に必ず全文読み、§2〜§5・§9の要件で再確認)。
- 既存成果の再利用(重複調査禁止): `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/{SOURCE_REGISTRY_01.md,TERMS_REVIEW_01.md,OVERSEAS_SOURCES_01.md,OVERSEAS_THEMES_01.md,METHOD_01.md}` を先に読み、既判定(除外/契約必須/Reddit API見送り=ユーザー決定・回避禁止/未確認)のサイトは再調査せず参照のみ。
- 並行Worker: 01a(英語圏Debateプラットフォーム: Kialo/DebateArt/DebateWise/Intelligence Squared/Debating Matters/ProCon/CreateDebate/Quora/HN等)、01c(国内)。担当外サイトは調査せず「他Lane候補」として名前のみ記録。ACTIVE_TASK・SSOT・SOURCE_REGISTRY_01.mdは編集しない(統合は委任_02)。

## 1. 担当範囲(Lane b)
出発点: Debating Europe。**新規発掘**: 例=EU市民パネル/European Citizens' Panels、Decidim各インスタンス(Barcelona等)、vTaiwan/Join.gov.tw、Pol.is活用事例の公開レポート、Munk Debates(加)、Le Drenche(仏)、独のStreit/Pro-Contra系(ZEIT「Streit」、Perspective Daily、SWR/ARD討論番組の公開論点)、北欧の熟議(Folkemødet等)、韓国(Naver知識iN、国民請願の公開意見)、中国語圏(Zhihu等は規約厳格の可能性=規約確認で判定)、インド・東南アジア英語メディアの読者討論、The Conversation(CC BY-ND: 想定用途との関係を規約で判定)、Wikimedia系・Open license系の論点集、OECD/世界経済フォーラム等の公開討論テーマ集(意見ではなく論点整理=△候補)、国際的なオンライン熟議(Deliberative polling公開資料)、実体験討論コミュニティ(介護・子育て・移民・働き方の欧州フォーラム)等。目安=評価対象10〜15サイト、中身を確認した推奨候補5〜8。数合わせ不要、品質優先。
- **言語**: 非英語サイトは原文を読んで要旨を日本語で記録(機械翻訳に頼る場合はその旨)。英語学習ラジオでの利用可否は統合時に判断するので、テーマ・主張の普遍性を優先して記録。

## 2. 必須ルール(ユーザー原文§2〜§5の要点。原文が正本)
- 国固有除外: 特定国の政党・選挙区・自治体制度・行政手続・国内対立を**主に**扱うサイトは対象外。背景が国固有でも議論の中身が普遍(世代間負担・家族の責任・働き方等)なら除外しない。判断理由を書く(EU政策系・自治体熟議系は特にこの区別を明確に)。
- 商用利用Status(想定用途=「公開されている実在の意見・議論・経験を読み取り、論点・立場・価値観を参考に、独自の3 Persona・一人称原稿をAIで生成し、商用の英語学習ラジオとして提供する」。逐語転載・有料コンテンツ再利用は想定しない): ◎=想定用途の商用・二次利用が明示的に許容 / ○=関連規約を確認し明確な禁止・契約・許諾必須が確認されない(法的保証ではない) / 除外=明確禁止または契約・許諾必須 / 未確認=規約が読めない・条項不明確。**未確認を○にしない。**確認事項=商用・二次利用・翻案条件/投稿者と運営者の著作権/AI入力・AI生成への利用制限/自動収集・スクレイピング・API条件/robots.txt/引用・要約・転載/プライバシー/契約要否。「閲覧」と「取得・AI処理・商用利用」を区別し、自動収集だけ禁止なら手動閲覧等の代替で使えるかを検討(禁止方法の実行・制限回避は厳禁)。**根拠URL・該当条項の逐語(短く、原語+日本語要旨)・確認日(2026-10-29)を必ず記録。**個別投稿の著作権とサイト規約を区別。CC系はライセンス名・版・ND/SA/NCの含意を明記。
- 実テーマ確認: 実際の討論ページを**本文まで読んで**確認(読めなければ「見出しのみ」と明記)。「実際に確認した異なる主張」と**AI構成のPersona案を明確に分離**。3立場を実際に確認できた場合のみ「3軸確認済み」。2軸なら「2軸確認+第3はAI構成案」。不足Persona要素と補強用体験談系(商用確認済みのみ)。
- Family Y適性 ◎/○/△(原文§4の5項目で理由)。人物が評論家化する情報源は高評価しない。
- 取得方法: 規約・robots.txt・討論ページの単発の手動閲覧相当のcurl(クロール・ログイン・一括収集なし)。読んだURLと日時を記録。LLM API呼出なし。

## 3. 成果物
`docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/LANE_B_EUROPE_ASIA_CIVIC_01.md`:
§1 探索方法・範囲 / §2 サイト評価表(列: サイト|国・地域|言語|商用利用|規約URL・条項逐語・確認日|Family Y適性|主なテーマ|3軸の取りやすさ|Personaの作りやすさ|注意事項|国固有除外判定) / §3 除外・未確認一覧(理由) / §4 テーマ候補(原文§7Bの9項目。目安5〜8件) / §5 他Lane候補・所見(判断はFable)。
報告=`docs/pm/RESULT_PACKET_FYD1b.md`(整合/未承認機能/成果物と目的適合/判断候補[停止根拠file:line]/費用0/commit、`判定整合:`行)。commit=自分のLANE_B・stop_check・委任文のみ明示`git add`→`git push origin HEAD:main`(index.lock衝突は数秒待って再試行)。最終回答は短く(サイト数・◎/○件数・テーマ件数・commit)。
