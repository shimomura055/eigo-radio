Fableからの委任_01c(管理ID: FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01。Lane c=**国内のDebate/Discussion系・市民討論・意見投稿プラットフォーム**(掲示板・相談サイトの延長ではないもの)。調査のみ、API(LLM)0、Production変更なし)。

## 0. 開始手順
- 本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_委任_01c.md` に逐語保存(heredoc失敗時はpy)。
- `tools/stop_scope_check_01.py --managed-id FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/stop_check_01c.json`(rc=3で停止)。
- ユーザー原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01_USER.md`(並行Workerが保存中。着手後に必ず全文読み、§2〜§5・§9の要件で再確認)。
- 既存成果の再利用(重複調査禁止): `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/{SOURCE_REGISTRY_01.md,TERMS_REVIEW_01.md,DOMESTIC_SOURCES_01.md,DOMESTIC_THEMES_01.md,PUBLIC_SOURCES_CHECK_01.md,THEME_FINAL_01.md,METHOD_01.md}` を先に読み、既判定(発言小町=除外[ユーザー決定]、Yahoo!知恵袋/ガルちゃん/ママスタ等の既評価、e-Gov PDL1.0等)は再調査せず参照のみ。**今回は掲示板・相談サイトを増やす調査ではない**(原文§1)。
- 並行Worker: 01a(海外英語圏)、01b(欧州・アジア・市民討論)。担当外は「他Lane候補」として名前のみ記録。ACTIVE_TASK・SSOT・SOURCE_REGISTRY_01.mdは編集しない(統合は委任_02)。

## 1. 担当範囲(Lane c)
国内の「異なる立場から議論している」情報源の発掘。例=Surfvote(Polimill)、PoliPoli、Decidim国内自治体インスタンス(加古川等)、NHK「みんなでプラス」等の意見募集企画、Yahoo!ニュース「みんなの意見」/コメント(規約で判定)、Quora日本語、note/はてな等の公開討論(規約確認)、ディベート甲子園・全国教室ディベート連盟の論題集(論点整理=△候補)、国会会議録・審議会議事録(公的、意見の実在性高いが制度説明化の懸念)、パブリックコメント結果(既存PDL1.0の延長=参照のみ)、新聞社の読者投稿・賛否企画(著作権・規約)、SYNODOS/アゴラ等の論壇系、企業・団体の公開討論企画、実体験討論コミュニティ(介護・子育て・働き方の当事者フォーラムで掲示板型でないもの)等。目安=評価対象8〜12サイト、中身を確認した推奨候補4〜6。数合わせ不要、品質優先、十分になった時点で止める。

## 2. 必須ルール(ユーザー原文§2〜§5の要点。原文が正本)
- 国固有除外: 日本固有の制度・政治事情そのものが主題のサイト(特定政党・選挙区・自治体制度だけ)は対象外。背景が制度でも議論の中身が普遍(世代間負担・家族の責任・働き方等)なら除外しない。判断理由を書く。
- 商用利用Status(想定用途=「公開されている実在の意見・議論・経験を読み取り、論点・立場・価値観を参考に、独自の3 Persona・一人称原稿をAIで生成し、商用の英語学習ラジオとして提供する」。逐語転載・有料コンテンツ再利用は想定しない): ◎=想定用途の商用・二次利用が明示的に許容 / ○=関連規約を確認し明確な禁止・契約・許諾必須が確認されない(法的保証ではない) / 除外=明確禁止または契約・許諾必須 / 未確認=規約が読めない・条項不明確。**未確認を○にしない。**確認事項=商用・二次利用・翻案条件/投稿者と運営者の著作権/AI入力・AI生成への利用制限/自動収集・スクレイピング・API条件/robots.txt/引用・要約・転載/プライバシー/契約要否。「閲覧」と「取得・AI処理・商用利用」を区別し、自動収集だけ禁止なら手動閲覧等の代替で使えるかを検討(禁止方法の実行・制限回避は厳禁)。**根拠URL・該当条項の逐語(短く)・確認日(2026-10-29)を必ず記録。**個別投稿の著作権とサイト規約を区別。公的サイトは利用規約の種類(PDL1.0/CC BY等)を明記。
- 実テーマ確認: 実際の討論ページを**本文まで読んで**確認(読めなければ「見出しのみ」と明記)。「実際に確認した異なる主張」と**AI構成のPersona案を明確に分離**。3立場を実際に確認できた場合のみ「3軸確認済み」。2軸なら「2軸確認+第3はAI構成案」。不足Persona要素と補強用体験談系(商用確認済みのみ。既存レジストリの条件付きサイトを参照してよい)。
- Family Y適性 ◎/○/△(原文§4の5項目で理由)。人物が評論家化する情報源は高評価しない。
- 取得方法: 規約・robots.txt・討論ページの単発の手動閲覧相当のcurl(クロール・ログイン・一括収集なし)。読んだURLと日時を記録。LLM API呼出なし。

## 3. 成果物
`docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/LANE_C_DOMESTIC_01.md`:
§1 探索方法・範囲 / §2 サイト評価表(列: サイト|種別|商用利用|規約URL・条項逐語・確認日|Family Y適性|主なテーマ|3軸の取りやすさ|Personaの作りやすさ|注意事項|国固有除外判定) / §3 除外・未確認一覧(理由) / §4 テーマ候補(原文§7Bの9項目。目安4〜6件) / §5 既存レジストリとの関係(新規/既登録/既除外)・他Lane候補・所見(判断はFable)。
報告=`docs/pm/RESULT_PACKET_FYD1c.md`(整合/未承認機能/成果物と目的適合/判断候補[停止根拠file:line]/費用0/commit、`判定整合:`行)。commit=自分のLANE_C・stop_check・委任文のみ明示`git add`→`git push origin HEAD:main`(index.lock衝突は数秒待って再試行)。最終回答は短く(サイト数・◎/○件数・テーマ件数・commit)。
