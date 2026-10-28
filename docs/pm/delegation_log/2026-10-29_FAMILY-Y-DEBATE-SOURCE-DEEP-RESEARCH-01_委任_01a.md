Fableからの委任_01a(管理ID: FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01。Lane a=**海外・英語圏のDebate/Discussionプラットフォーム**。調査のみ、API(LLM)0、Production変更なし)。

## 0. 開始手順
- 本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_委任_01a.md` に逐語保存(heredoc失敗時はpy)。
- `tools/stop_scope_check_01.py --managed-id FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/stop_check_01a.json`(rc=3で停止)。
- ユーザー原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`(並行Workerが保存中。数分後に読めるので、着手後に必ず全文読み、§2〜§5・§9の要件で自分の作業を再確認)。
- 既存成果の再利用(重複調査禁止): `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/{SOURCE_REGISTRY_01.md,TERMS_REVIEW_01.md,OVERSEAS_SOURCES_01.md,OVERSEAS_THEMES_01.md,METHOD_01.md}` を先に読み、既に「除外/契約必須/API見送り(Reddit)/未確認」と判定済みのサイトは再調査せず参照のみ(Reddit API申請見送りはユーザー決定=回避策禁止)。
- 並行Worker: 01b(欧州・アジア・非英語圏・市民討論/公開討論・CC系メディア)、01c(国内)。自分の担当外サイトを見つけたら調査せず「他Lane候補」として名前だけ記録。ACTIVE_TASK・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/UDR)・SOURCE_REGISTRY_01.mdは編集しない(統合は委任_02)。

## 1. 担当範囲(Lane a)
出発点: Kialo / DebateArt / DebateWise / Intelligence Squared / Debating Matters(Debating Europeは01b)。**この5件で終えず新規発掘**: 例=ProCon.org(Britannica)、CreateDebate、IDEA Debatabase、Munk Debates、Oxford Union、The Conversation(CC BY-ND=01bと重複しないよう本Laneでは扱わない)、Hacker News(前回未確認→規約再確認は可)、Stack Exchange系(CC BY-SA)、Quora、Pol.is公開レポート、Ethics Bowl/Philosophy case collections、Opposing Views、AllSides、Debate Island、Argüman、The Guardian Opinion/Comment is Free、NYT Opinion(有料)、Medium、Substack公開討論、Metafilter、実体験討論コミュニティ(例: 介護・子育て・働き方・AIの実務者フォーラム)等。候補数の目安=評価対象10〜15サイト、推奨(◎/○)候補として実際に中身を確認したもの5〜8サイト。数合わせ不要、品質優先、十分になった時点で止める。

## 2. 必須ルール(ユーザー原文§2〜§5の要点。原文が正本)
- 国固有除外: 特定国の政党・選挙区・自治体制度・行政手続・国内対立を**主に**扱うサイトは対象外。背景が国固有でも議論の中身が普遍(世代間負担・家族の責任・働き方等)なら除外しない。判断理由を書く。
- 商用利用Status(想定用途=「公開されている実在の意見・議論・経験を読み取り、論点・立場・価値観を参考に、独自の3 Persona・一人称原稿をAIで生成し、商用の英語学習ラジオとして提供する」。逐語転載・有料コンテンツ再利用は想定しない): ◎=想定用途の商用・二次利用が明示的に許容 / ○=関連規約を確認し明確な禁止・契約・許諾必須が確認されない(法的保証ではない) / 除外=明確禁止または契約・許諾必須 / 未確認=規約が読めない・条項不明確。**未確認を○にしない。**確認事項=商用・二次利用・翻案条件/投稿者と運営者の著作権/AI入力・AI生成への利用制限/自動収集・スクレイピング・API条件/robots.txt/引用・要約・転載/プライバシー/契約要否。「閲覧」と「取得・AI処理・商用利用」を区別し、自動収集だけ禁止なら手動閲覧等の代替取得で使えるかを検討(禁止された方法の実行・制限回避は厳禁)。**根拠URL・該当条項の逐語(短く)・確認日(2026-10-29)を必ず記録。**個別投稿の著作権とサイト規約を区別。
- 実テーマ確認: サイト名列挙で終えず、実際の討論ページを**本文まで読んで**確認(検索スニペットや見出しだけで「本文確認」と書かない。読めなかったら「見出しのみ」と明記)。各テーマで「実際に確認した異なる主張」(投稿者属性が分かれば付記、短い要旨)を、**AIが考えたPersona構成案と明確に分離**。3つの立場を実際に確認できた場合のみ「3軸確認済み」。2軸しかなければ「2軸確認+第3はAI構成案」と書き、AI創作で3軸化しない。不足Persona要素(職業・家族・感情等)と、補強に使える体験談系(商用Status確認済みのもののみ)を記す。
- Family Y適性 ◎/○/△(原文§4の5項目で採点理由)。論理的賛否は豊富でも人物が評論家化する情報源は高評価しない。
- 取得方法: 規約・robots.txt・該当討論ページの**単発の手動閲覧相当のcurl**(クロール・ログイン・一括収集・レート超過なし)。読んだURLと日時を記録。LLM API呼出なし。

## 3. 成果物
`docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/LANE_A_OVERSEAS_EN_01.md`:
§1 探索方法・範囲(発掘経路、評価対象サイト数、読んだページ数) / §2 サイト評価表(列: サイト|国・地域|商用利用(◎/○/除外/未確認)|規約URL・条項逐語・確認日|Family Y適性|主なテーマ|3軸の取りやすさ|Personaの作りやすさ|注意事項|国固有除外判定) / §3 除外・未確認一覧(理由) / §4 テーマ候補(原文§7Bの9項目を各テーマに。目安5〜8件、品質優先) / §5 他Lane候補・所見(判断はFable)。
報告=`docs/pm/RESULT_PACKET_FYD1a.md`(整合/未承認機能/成果物と目的適合/判断候補[停止根拠file:line]/費用0/commit、`判定整合:`行)。commit=自分のLANE_A・stop_check・委任文のみ明示`git add`→`git push origin HEAD:main`(index.lock衝突は数秒待って再試行)。最終回答は短く(サイト数・◎/○件数・テーマ件数・commit)。
