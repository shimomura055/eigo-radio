# OVERSEAS_METHOD_01(海外実在意見の低コスト収集手順案。**提案であり正式仕様ではない。Production採用ではない**)

根拠は委任_01Bで実測した取得可否(`sources_overseas/*.json`、`scripts_overseas/fetch_01B.py`)。LLM呼出は一切使わない(要約・意見の補完は禁止)。

## 1. 手順(1テーマあたり)
1. **候補発見(HN Algolia)**: `https://hn.algolia.com/api/v1/search?tags=story&numericFilters=num_comments>100&query=<語>`。語例: caregiving, retirement age, social media kids, tourism, rent。タイトル・コメント数・日付を一覧化(約1分)。
2. **本文取得**: `https://hn.algolia.com/api/v1/items/<id>` を取得し、長文コメント上位5〜8件を保存(スパム・宣伝の語、極端に短い/自社製品誘導のコメントを除外)。
3. **補完(生活者の声)**: Mumsnet(`/talk/<board>/`のHTMLから投稿日時`datePublished`とコメント)、Guardian(記事の`shortUrlId`→discussion API `orderBy=mostRecommended`)。同一テーマを2〜3ソースで照合し、**3つ以上の立場の根拠投稿を人が(agentが)本文で確認**する。
4. **Reddit**: robots.txtが全面Disallow、JSONは403のため、**自動の恒常収集は行わない**。必要なら公式Data API/研究者向け申請(r/reddit4researchers)を経てから。個別スレッドのRSSを手動で数件のみ取得する程度に留める。
5. **記録**: URL・取得日時・投稿日時・短い抜粋(1件260字以内)を`sources_overseas/<site>_<n>.json`形式で残す。全文は転載しない(`local_full/`は非commit)。

## 2. 所要時間・費用(実測ベース)
- 本調査: HTTP約130回、取得対象9サイト、実作業約1時間強。**API費0円・LLM費0円**。
- 1テーマ(候補発見1〜2分+取得3〜5分+読解は別): 取得部分は数分・0円。読解(agentのtoken)が主コスト。70円/記事セットの収集枠は、取得0円+読解数千token程度に収まる見込み(未計測)。

## 3. 信頼性・偏り・規約上の注意
- **偏り**: HN=IT職・男性・米国/欧州、Guardian=英国左派寄り、Mumsnet=女性・英国、Reddit=母集団はサブレディット依存(r/japanlifeは在日外国人)。**日本人の声ではない**ため、日本のリスナーの自分事化には国内情報源(委任_01A)との併用が必須。
- **汚染**: HNに暗号資産詐欺コメント(hn_2)と自社製品宣伝(hn_7)を確認。除外ルールが必要。AI生成コメントの検出は本調査では未実施(未確認)。
- **規約**: Reddit=robots全面Disallow・Public Content Policy、Stack Exchange=robots に ai-train=no、CC BY-SA(帰属表示が必要)、HN=Crawl-delay 30(Algolia公開APIを使用)、Guardian=discussion APIは無認証で応答するが商用再利用条件は未精読。引用は短く、**逐語コピーでなく複数投稿を材料に独自構成**(委任の設計思想どおり)。投稿者名は保存しない。
- **プライバシー**: Mumsnetは家庭事情が詳細。個人特定につながる固有情報は使わず、パターンのみ利用。
- **取得不可サイト**(Quora, MetaFilter, NYT, Japan Today, TheStudentRoom, Fark): bot遮断。回避しない。

## 4. 今後の判断候補(いずれも本委任では決めない)
- Reddit公式APIの利用申請を行うか(日本在住者の声の価値と規約リスクのトレードオフ)。→ 判断候補(分類D: 真に新しい判断、承認範囲外)。
- 収集スクリプト(`scripts_overseas/fetch_01B.py`)を正式な量産ツール化するか。→ 現時点では調査用の試作で、正式仕様ではない。
