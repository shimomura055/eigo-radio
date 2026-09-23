# TOPIC-SELECTION-LUNA-API-TRIAL-01 実行報告

Status: [Fable分類待ち]

## 0. 概要

API経由`gpt-5.6-luna`(`er006_model_routing_contract_01.WRITER_MODEL`と同値)
が、直近24時間の話題から「聞きたくなるNews候補」20件を自力で
発見(Discovery)→Hook生成(Hooks)→Ranking・最終選定(Rank)できるかを
検証する1 runのTrial。Topic発見・Hook生成・Ranking・最終選定はすべて
Lunaが行い、Sonnetは (a) 複数レーンの生出力をcandidate_idで機械的に
結合、(b) Lunaが出したrank値でソートして表示、(c) スクリプトによる
URL到達性・公開時刻検証(Phase 4)、(d) 集計(Phase 5)のみを行った。
候補の追加・救済・Hook書き直し・順位の手修正は一切行っていない。
Production module・Prompt・config・SSOTは無変更。

実行日時(T_now): 2026-09-24T07:48:25.677927+09:00(JST)
基準時刻(T_cut、T_now−24h): 2026-09-23T07:48:25.677927+09:00(JST)
Model実値(全8 call共通): `gpt-5.6-luna`
Reasoning effort: 全step `medium`

## 1. 設計(Phase 0〜5)

- Phase 0: SNS/Trendレーンのアクセス可否プローブ(Luna+web_search、
  最大2回)。根拠URL付きテーマが3件以上取得できればPASS、Phase 1へ進む。
- Phase 1: Discovery(Luna+web_search、レーンごと1回、計5回)。
  レーン: general/everyday/scitech/light/sns。各レーン10〜15件。
- Phase 2: Hook生成(Luna、web_searchなし、1回)。候補全件に
  hook_ja/hook_en/answer_sketch/beyond_article/beyond_evidence_url/
  category/distance_to_japan/dedupe_groupを付与。
- Phase 3: Ranking・最終選定(Luna、web_searchなし、1回)。最大20件を
  rank付きで選定。dedupe_group重複排除・beyond_article条件・
  time_uncertain明記はLuna自身の判断に委ねた(Sonnetは事後フィルタ
  していない)。
- Phase 4: 検証(スクリプトのみ、LLMなし)。最終選定の各URLへHTTP GET
  (timeout 15秒)、published_time系メタ(article:published_time/
  JSON-LD datePublished/`<time datetime>`/meta pubdate等)を抽出し、
  T_cut〜T_nowの範囲かを判定。older_than_24h/http_errorは失格として
  記録(補充なし)。unverifiableは失格にせずLuna申告時刻のみと明記。
  beyond_evidence_url・confirm_source_urlの到達性も同様に記録。
- Phase 5: 集計(スクリプトのみ)。Source distribution(ルールベース分類、
  分類表をJSONに保持)、Category/Lane/distance_to_japan分布、
  Phase 1→2→3→4のfunnel件数。

## 2. Phase 0結果(SNS/Trendアクセス可否)

判定: **PASS**(アクセスできたテーマ23件、3件以上の基準を満たす)。
inaccessible_sources: なし(0件)。

取得元ページ: Twittrend(ついっトレンド)、トレンドカレンダー(X/Yahoo!/
Googleトレンドワードランキング)、Google トレンド日本(急上昇)。
代表例: 「台風26号」(Google トレンド、2時間前)、「緊急着陸・那覇空港・
ANA那覇」(Google トレンド、6時間前)、「jcom 障害」(Google トレンド、
22時間前)、「ドジャース 対 パドレス」(Google トレンド、21時間前)、
「大谷翔平」(トレンドカレンダー、2026/09/24 07:15更新)ほか計23件。
全件のURL・時刻表記は`er016_output/topic_selection_luna_api_trial_01/
phase0_probe.json`に保存。

Phase 0で検知された「緊急着陸・那覇空港・ANA那覇」「jcom 障害」は、
後述Phase 1 sns レーンで実際に候補化され(C053/C052)、最終18件にも
選定された(1位・2位)。

## 3. Phase 1結果(レーン別件数・重複)

| レーン | 件数 | time_uncertain件数 |
|---|---|---|
| general | 13 | 11 |
| everyday | 14 | 11 |
| scitech | 13 | 13 |
| light | 11 | 4 |
| sns | 11 | 0(snsレーンはtime_uncertainフィールド自体はbase schemaにあるが、
  11件全件false) |

Phase 1総候補数(重複URLも含めそのまま結合): **62件**。
sns レーンのうち、`confirm_source_url: null`(実体未確認のまま)の候補:
**7件/11件**(#乃木坂46ANN、Clara、Lila、#スノからのありがとう、
#安養寺姫芽生誕祭2026、#名探偵THREE、プレミアムパス特典/ガシャ関連)。

## 4. 最終選定(18件、20件には未達)

Phase 3でLunaが選定したのは**18件**(20件には届かなかった)。Sonnetは
補充・追加をしていない。

| Rank | 元News概要 | Hook(ja) | Hook(en) | Category | Source・published time(申告/検証) | 選定理由 |
|---|---|---|---|---|---|---|
| 1 | J:COMの全国ネット接続障害、原因調査中・復旧時期未定(ライブドアニュース/共同通信) | J:COMの全国的なネット障害は、原因と復旧時期が判明したのでしょうか？ | Have the cause and restoration time of J:COM's nationwide internet outage been determined? | AI/Tech | ライブドアニュース(共同通信)・申告2026-09-23 14:28 JST/検証2026-09-23T14:16:03Z(within_24h、json-ld) | 全国的な通信障害は生活・仕事に直結する身近な話題。原因・復旧時期という実用的焦点。 |
| 2 | ANA機エンジントラブルで那覇空港へ緊急着陸、乗客はスライドで避難(テレ朝NEWS) | ANA機はなぜ那覇空港に引き返し、乗客はどう避難したのでしょうか？ | Why did the ANA aircraft return to Naha, and how did passengers evacuate? | Hard News | テレ朝NEWS・申告2026-09-24 05:50 JST/検証2026-09-23T20:50:00Z(within_24h、meta date) | 国内線緊急着陸・乗客避難は心理的距離が近く、音声で説明しやすい。 |
| 3 | 猛暑下、日本の農家が高温耐性のコメ品種へ転換(The Guardian) | 猛暑に耐えるコメ品種への転換は、日本の食料価格と食料安全保障をどう支えるのでしょうか？ | How could heat-resistant rice varieties support Japan's food prices and food security? | Environment | The Guardian・申告Tue 22 Sep 2026 23:23 EDT/検証2026-09-23T03:23:13Z(within_24h、article:published_time) | 猛暑とコメの品質・価格は食卓と家計に直結。気候変動への農業適応という大きなテーマ。 |
| 4 | 落語家・立川談春のなりすましアカウントが投資話を持ちかけ、本人が注意喚起(テレ朝NEWS) | 立川談春の名を使った投資話が届いたら、なぜ無視すべきなのでしょうか？ | Why should people ignore investment offers made through accounts impersonating Danshun Tatekawa? | Consumer | テレ朝NEWS・申告2026-09-23 18:03 JST/検証2026-09-23T09:03:00Z(within_24h、meta date) | 著名人なりすまし投資詐欺は誰にでも起こりうる消費者被害として実用的。 |
| 5 | 在宅勤務は睡眠を伸ばす一方、静的時間(座位)も増やす(フィンランドの研究、ConsumerAffairs) | 在宅勤務は睡眠を約14分増やす一方、なぜ静的な時間を約44分増やしたのでしょうか？ | Why did remote work add about 14 minutes of sleep but roughly 44 minutes of sedentary time? | Health | ConsumerAffairs・申告Sep. 23, 2026(time_uncertain)/検証**http_error(403)** | 在宅勤務の睡眠・活動対比は働き方に関係する人が多い身近な話題。※Phase4でhttp_error判定(失格、下記5節参照) |
| 6 | AI依存が記憶・推論に与える影響と批判的思考の維持法(Nature特集) | AIを使うほど、人間の記憶や推論力は弱くなるのでしょうか？ | Does using AI more often weaken human memory and reasoning? | AI/Tech | Nature・申告23 SEP 2026(time_uncertain)/検証2026-09-23T00:00:00Z(within_24h、time datetime) | AI利用と認知への影響は現在の利用者に広く関係する国際テーマ。 |
| 7 | レシピを2倍にしても仕上がりが変わる理由(The Spokesman-Review) | レシピを2倍にしたのに味や仕上がりが変わるのは、なぜなのでしょうか？ | Why can doubling a recipe change the taste and texture instead of simply doubling the result? | Lifestyle | The Spokesman-Review・申告Wed., Sept. 23, 2026(time_uncertain)/検証2026-09-23T14:00:00Z(within_24h、json-ld) | 家庭料理ですぐ役立つ身近な疑問で音声向き。 |
| 8 | 65歳以上の就業者943万人で過去最多、職場・地域サービスへの影響(Japan.co.jp) | 65歳以上の就業者が943万人に達した日本で、職場や地域サービスはどう変わるのでしょうか？ | With 9.43 million people aged 65 and over working in Japan, how must workplaces and local services change? | Business/Economy | Japan.co.jp・申告2026-09-24(time_uncertain)/検証2026-09-23T15:00:00Z(within_24h、json-ld)※URL注記は5節参照 | 高齢者就労の過去最多更新は働き方・地域サービスに直結する社会性の高い話題。 |
| 9 | ソフトバンクG、OpenAI投資に関連し外貨建て債券募集(Japan.co.jp) | ソフトバンクGはOpenAI投資を、外貨建て債券の利払いに耐えながら続けられるのでしょうか？ | Can SoftBank Group continue investing in OpenAI while managing the interest burden of foreign-currency bonds? | Business/Economy | Japan.co.jp・申告2026-09-24(time_uncertain)/検証2026-09-23T15:00:00Z(within_24h、json-ld)※URL注記は5節参照 | AIブームの資金調達リスクを考える材料。 |
| 10 | 地球内部の重力の綱引きが1日の長さを変える(Nature) | 地球内部のコアと月・海洋の力は、なぜ1日の長さをわずかに変えるのでしょうか？ | Why do Earth's core, the Moon and the oceans slightly change the length of a day? | Science | Nature・申告23 SEP 2026(time_uncertain)/検証**http_error(404)** | 地球の自転を複数の力が左右するという驚き。※Phase4でhttp_error判定(失格、下記5節参照) |
| 11 | 約1500人分の脳の遺伝子活動地図、加齢・アルツハイマー病の手がかりに(Nature) | 約1500人分の脳の遺伝子活動地図は、加齢やアルツハイマー病の理解をどう変えるのでしょうか？ | How could a gene-activity map from about 1,500 brains change our understanding of aging and Alzheimer's? | Health | Nature・申告23 SEP 2026(time_uncertain)/検証2026-09-23T00:00:00Z(within_24h、time datetime) | 加齢・アルツハイマー病への関心と結びつく大型研究。 |
| 12 | 高圧下の特殊なホウ素が予想の100万倍の電気伝導性(Nature) | 高圧下の特殊なホウ素は、なぜ予想を100万倍も上回る電気伝導性を示したのでしょうか？ | Why did a high-pressure form of boron conduct electricity a million times better than expected? | Science | Nature・申告23 SEP 2026(time_uncertain)/検証**http_error(404)** | 数字に強いフックがある基礎科学ニュース。※Phase4でhttp_error判定(失格、下記5節参照) |
| 13 | ISS乗員がAR・AIを使った超音波検査技術を試験(NASA) | 宇宙飛行士は、地上の専門医なしでAIと拡張現実を使って超音波検査できるのでしょうか？ | Can astronauts perform ultrasound exams using AI and augmented reality without a specialist on Earth? | AI/Tech | NASA・申告September 23, 2026 3:22PM(time_uncertain)/検証2026-09-23T19:22:07Z(within_24h、meta parsely-pub-date) | 宇宙医療技術と遠隔医療への応用を想像しやすい。 |
| 14 | 東芝、移動に応じて無線網を制御し通信性能を平均21%改善(Japan.co.jp) | 東芝の無線制御で通信性能は平均21%改善、実際の通信網に導入できるのでしょうか？ | Toshiba improved wireless performance by an average of 21%—can the technology be deployed in real networks? | AI/Tech | Japan.co.jp・申告2026-09-24(time_uncertain)/検証2026-09-23T15:00:00Z(within_24h、json-ld)※URL注記は5節参照 | スマホ・通信品質に直結、実用化課題も含め宣伝的でない。 |
| 15 | 面接にアイスコーヒー持参は失礼か、職場文化の議論(ABC News/GMA) | 面接にアイスコーヒーを持ち込むのは失礼なのか、それとも職場文化の違いなのでしょうか？ | Is bringing iced coffee to a job interview rude, or just a difference in workplace culture? | Lifestyle | ABC News/Good Morning America・申告September 22, 2026(time_uncertain)/検証**unverifiable** | 軽い話題で日本の面接にも置き換えやすい。※Phase4でunverifiable(下記5節参照) |
| 16 | 綾瀬はるか、大阪で主演映画舞台挨拶・長ぜりふの覚え方を紹介(テレ朝NEWS) | 綾瀬はるかが長いせりふを覚えるために実践している方法とは？ | What method does Haruka Ayase use to memorize long lines? | Entertainment | テレ朝NEWS・申告2026-09-23 17:48 JST/検証2026-09-23T08:48:00Z(within_24h、meta date) | 著名人の体験談を入口に記憶・睡眠という実生活に近い話題へ。 |
| 17 | 日本人ネイリストが手掛けた「イタリアン・マニキュア」がVOGUE WORLD 2026 MILANOで話題(Vogue Japan) | 日本人ネイリストが手掛けた「イタリアン・マニキュア」とは、どんな表現なのでしょうか？ | What is the "Italian manicure" style created by a Japanese nail artist? | Lifestyle | Vogue Japan・申告2026-09-23(time_uncertain)/検証2026-09-23T02:37:16Z(within_24h、article:published_time) | 日本人ネイリストの海外活躍で日本との接点があり美容トレンドとして軽く楽しめる。 |
| 18 | INI、新曲「1NA RIDE」PVでストリートスタイルのパフォーマンス公開(ORICON NEWS) | INIの「1NA RIDE」は、夜のドライブ感をストリート演出でどう表現したのでしょうか？ | How does INI's "1NA RIDE" express a night-drive feeling through its street-style visuals? | Entertainment | ORICON NEWS・申告2026-09-23 21:53 JST/検証2026-09-23T21:53:00Z(within_24h、time datetime) | 硬いニュースが続く中で音楽・映像表現として番組に変化をつけられる軽い話題。 |

(各候補のsummary_ja・distance_to_japan理由・expected_listener_reaction
全文は`er016_output/topic_selection_luna_api_trial_01/phase3_ranked.json`
に保存。表内の日本人との距離: 近い9件/中1件/遠い8件。)

## 5. Phase 4検証結果

検証対象: 18件。**失格3件・unverifiable 1件・通過14件**
(スクリプトの`passed_count`定義はdisqualified以外の15件だが、うち1件
[C022]はunverifiableで失格ではないため、両方の見方を明記する:
`disqualified_count=3`、`unverifiable_count=1`、
`passed_count(非disqualified)=15`)。

失格(older_than_24h/http_error、補充なし):
- Rank 5 (C016, ConsumerAffairs、在宅勤務記事): HTTP 403(アクセス拒否)。
  ボット対策によるブロックの可能性があり、「記事が実在しない」ことを
  意味するとは限らない。ただし本Trialの検証仕様(older_than_24h/
  http_error/unverifiable/http_errorの4分類)では非200応答は一律
  http_error=失格として扱った(下記10節「所見」参照)。
- Rank 10 (C028, Nature、地球の自転記事): HTTP 404(該当URLは存在せず)。
- Rank 12 (C029, Nature、ホウ素の電気伝導性記事): HTTP 404(該当URLは
  存在せず)。

unverifiable(失格にせず記録のみ):
- Rank 15 (C022, ABC News、面接コーヒー記事): HTTP 200だが
  published_time系メタが検出できず、Luna申告時刻のみ。

beyond_evidence_url到達性: 最終18件は全件`beyond_article: false`
(beyond_evidence_urlを要する候補はゼロ)。
confirm_source_url到達性: sns起点の最終2件(Rank1・2)はいずれも
confirm_source_urlが存在し到達性True(`unconfirmed_sns_entity_count=0`)。

## 6. 集計

Funnel: Phase 1総数62 → Phase 2 dedupe_group数57(Lunaが付与した
グループID) → Phase 3選定18 → Phase 4通過(非disqualified)15。

Source distribution(ルールベース分類、最終18件対象):
国内一般媒体5、海外一般媒体1(The Guardian)、その他12
(Nature 4・NASA・ABC News・ConsumerAffairs・The Spokesman-Review・
Vogue Japan・Japan.co.jp 3件、いずれも既定キーワード表に未登録の
専門媒体・分類外媒体)。分類ルール表は`phase5_aggregate.json`の
`source_classification_rules`に保存。

Category distribution(最終18件): AI/Tech 4、Lifestyle 3、
Business/Economy 2、Health 2、Science 2、Entertainment 2、
Hard News 1、Environment 1、Consumer 1。

Lane distribution(最終18件): scitech 5、everyday 4、light 4、
general 3、sns 2。

distance_to_japan distribution(最終18件): 近い9、遠い8、中1。

time_uncertain件数(最終18件): 12件。beyond_article件数: 0件。

## 7. コスト

| Phase | JPY | call数 | 明示web_search |
|---|---|---|---|
| phase0_probe | 6.3 | 1 | 1(内部web_search_call=3) |
| phase1_general | 8.4 | 1 | 1(内部4) |
| phase1_everyday | 10.5 | 1 | 1(内部5) |
| phase1_scitech | 8.4 | 1 | 1(内部4) |
| phase1_light | 11.7 | 1 | 1(内部6) |
| phase1_sns | 6.6 | 1 | 1(内部3) |
| phase2_hooks | 2.7 | 1 | 0 |
| phase3_rank | 1.2 | 1 | 0 |
| **合計** | **55.9円** | **8** | **6(内部合計25)** |

token合計: input 275,124 / cached 0 / output 37,168。単価は
`compute_topic_cost.py`の`price()`方式(`pricing_snapshot.json`、
gpt-5.6-luna: input $0.2/M、cached $0.02/M、output $1.2/M、
web_search $10/1000 call、USD→JPY=160)。委任文の想定¥150〜250・
上限¥600を大幅に下回った。

## 8. STOP条件該当有無(委任文§21の6項目)

1. Lunaからweb探索不可: **非該当**(Phase 0/1で全call web_search実行済、
   response.model=gpt-5.6-luna確認済)。
2. SNS・Trend探索sourceへアクセス不可: **非該当**(Phase 0で23件取得、
   inaccessible_sourcesは0件)。
3. 24時間フィルタを信頼できる形で実現不可: **非該当**(Phase 4で
   スクリプトによる独立検証を実施、18件中15件を実際に確認)。
4. actual model_idがLunaでない: **非該当**(全8 callでresponse.model=
   "gpt-5.6-luna"を確認、`call_luna()`内でfail-closedチェック実装済)。
5. コスト想定以上: **非該当**(実測¥55.9、上限¥600の約1/10)。
6. capability制約で人間側Trialと同等の探索不可: **非該当と判断**
   (5レーン・62候補を取得できたが、10節に所見あり)。

## 9. Production・SSOT無変更確認

`git status --porcelain -- er011_*.py er014_*.py er015_*.py routing.py
er006_model_routing_contract_01.py` は空(本Trialで生成された
er016系ファイル以外に該当なし)。`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/
`DECISION_LOG.md`/`PM_GOVERNANCE.md`は未変更。Daily runner等への
配線は行っていない。

## 10. Sonnet所見と設計変更提案(実行はしない、報告のみ)

- **Japan.co.jp URLの疑義**: 最終18件中3件(Rank 8・9・14)が
  `source_name: "Japan.co.jp"`、`url: "https://www.japan.co.jp/"`
  (トップページと同一URL)を返した。Phase 4は当該トップページへGETし
  JSON-LDのdatePublishedを検出できたためwithin_24h判定となったが、
  これは個別記事ページのURLではなく、記事の実在・公開時刻の検証として
  実質的な意味を持たない可能性が高い。Lunaのweb_search機能が個別記事の
  正確なpermalinkを取得できなかった(または存在しないドメインの
  トップページを代表URLとして返した)可能性がある。Sonnetは指示通り
  候補を修正・除外していないが、Fableの分類判断ではこの3件を
  「published_time_verified事実上未確認」として扱うことを検討する
  余地があると考える。
- **HTTP 403の扱い**: Rank 5(ConsumerAffairs)はHTTP 403(アクセス拒否)
  だった。委任文の設計は「older_than_24hおよびhttp_error(存在しない)の
  候補は失格」としており、本スクリプトも403を含む非200応答を一律
  http_error=失格とした。403はボット対策等による一時的アクセス拒否の
  可能性もあり、必ずしも「記事が存在しない」ことを意味しない。設計上の
  定義に忠実に従ったが、この区別(404=存在しない vs 403=アクセス拒否)を
  分けて記録すべきだったかもしれない、という点を提案として残す
  (実装は変更していない)。
- **Nature記事URLの404多発**: scitechレーン由来のNature記事5件中2件が
  404(存在しないURL)だった。Natureの記事IDをLunaが自己流に生成した
  可能性がある(パターン`d41586-026-0293X-Y`が連番的)。
- **source_classification_rulesの限界**: 実行中に自分で作成した
  ルール表に2つの誤りを発見し、実行順序の早い段階(Phase 5実行前)で
  修正した: (1) 「共同通信/Kyodo」を誤って「海外通信社」に分類して
  いたため「国内一般媒体」へ修正、(2) 英字キーワード"AP"が
  "Japan.co.jp"へ部分一致してしまう実装バグを、英字キーワードのみ
  単語境界一致に変更して修正。両修正は集計スクリプトの機械的ロジック
  修正であり、Luna側の候補・Hook・順位には一切触れていない。修正後の
  数値がPhase 5・本REPORTに反映されている。

## 11. DECISION_LOG追記候補(Status: [Fable分類待ち])

```
TOPIC-SELECTION-LUNA-API-TRIAL-01(2026-09-24、Status: [Fable分類待ち])
API経由gpt-5.6-lunaが直近24時間の話題から「聞きたくなるNews候補」を
自力で発見・Hook生成・Ranking選定するTrialを1 run実施。Phase 0
(SNS/Trendアクセス可否)は23件取得でPASS。Phase 1で5レーン計62件discovery、
Phase 2で全62件にHook付与、Phase 3でLunaが18件(20件中、20件には未達)を
自律選定。Phase 4(スクリプトによる独立URL検証)で18件中3件が
older_than_24h/http_error相当で失格、1件がunverifiable、15件が
within_24h相当で通過。コスト実測¥55.9(上限¥600)。Sonnetは候補追加・
救済・Hook書き直し・順位手修正を一切行っていない。詳細:
TOPIC-SELECTION-LUNA-API-TRIAL-01_REPORT.md、
er016_output/topic_selection_luna_api_trial_01/。Production変更なし。
Fableによる分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)待ち。
```
