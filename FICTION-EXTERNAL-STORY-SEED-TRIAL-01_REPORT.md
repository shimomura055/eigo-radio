# FICTION-EXTERNAL-STORY-SEED-TRIAL-01 REPORT

Status: **完走(S-1〜S-5、Sonnet仮分類VALIDATED、詳細は§10)**。
Trial専用。Production Fiction仕様への反映は本タスクの対象外。ユーザー決定
(予算上限¥30→¥200)によりS-1結果を再利用してS-2〜S-4+評価まで完走した
(2026-09-26)。

## §1 目的
完全創作方式(Story DNA / Coverage Run / Core Provocation、
`er018_fiction_story_dna_e_axis_redesign_01.py`等)とは別に、実在する
Public Domain / CC0 / 翻案可能ライセンスが確認できる外部ソース(実話・
人生談/実話・歴史的逸話/日本文学(青空文庫)/世界文学(Gutenberg等))を
出発点として、Seed化(抽象化・再構成)した英語学習用短編を試作する
Trial。予算上限¥30(候補探索+Seed化4call+Story生成4call以内)。

## §2 探索Sourceと権利確認
`er018_fiction_external_story_seed_trial_01.py --step search`(4系統、
系統ごとにOpenAI Responses `web_search`ツール付き1 call、
`search_context_size: "low"`、`max_tool_calls: 3`指定)で実行。

| 系統 | 主なSource | web_search_call実測 | 備考 |
|---|---|---|---|
| 01_life_history | loc.gov (American Life Histories, WPA Federal Writers' Project) | 4 | LOCの一般rights statement(政府職員著作物は著作権対象外)を各候補で確認 |
| 02_historical | gutenberg.org / en.wikisource.org | 4 | Gutenbergライセンス文言、Wikisourceの"published before 1931"/著者没後100年表示を確認 |
| 03_japanese_lit | aozora.gr.jp | 4 | 青空文庫の一般方針文(「著作権の切れている作品」は許諾不要)+各作家の没年を確認。**個別カードの「著作権なし」バッジそのものはこの1 callでは未確認**(懸念として記録、§8参照) |
| 04_world_lit | gutenberg.org | 3 | 各ebookページの"Public domain in the USA."表示を確認 |

**重要な観測**: `max_tool_calls=3`を指定したが、実測`web_search_call_count`は
4,4,4,3(4系統中3系統が指定上限を1回超過)。OpenAI側のmax_tool_callsは
厳密なhard capではない可能性がある(過去の`er016_topic_discovery_angle_
broad_luna_trial_01.py`等でも同種の観測があるか未確認、本Trial単独の
観測として記録)。

## §3 候補一覧(4系統、各3〜5件)
全文は以下に保存(URL・確認文言・理由・懸念を表形式で記録済み):
- `er018_output/fiction_external_story_seed_trial_01/stories/01_life_history/candidates.md`(4件)
- `er018_output/fiction_external_story_seed_trial_01/stories/02_historical/candidates.md`(3件)
- `er018_output/fiction_external_story_seed_trial_01/stories/03_japanese_lit/candidates.md`(4件)
- `er018_output/fiction_external_story_seed_trial_01/stories/04_world_lit/candidates.md`(5件)

候補の質的傾向(Sonnet所見、暫定):
- 01: LOC American Life Historiesの個人の具体的エピソード(牛の対決、床屋兼歯医者、移民一家の入植、鉄道労働者の遭遇)。権利根拠は明確(政府職員著作物)だが、各候補とも「具体的エピソードは原稿本文を精読して確認要」という懸念が共通して付いている。
- 02: Franklin自伝の一節、Wikisourceの南軍馬丁の寝返り回想録、ミズーリ日記。権利根拠は明確(Gutenberg/Wikisourceの明記)。
- 03: 芥川「羅生門」、太宰「走れメロス」、宮沢賢治「注文の多い料理店」、梶井基次郎の一編。没年ベースの推定は妥当だが、各カードの個別「著作権なし」バッジ自体は本callでは直接確認できていない(§8で追加検証要)。
- 04: チェーホフ「賭け」、O. Henry「賢者の贈り物」、ガルシン「信号」、モーパッサン「首飾り」、スティーヴンソン「マレトロワ卿の扉」。いずれもGutenbergの"Public domain in the USA."表示あり。「賢者の贈り物」「首飾り」は著名作のため、翻案時は独自性の確保が必要と候補自身が懸念として指摘。

## §4 S-2 代表選定+権利再検証

各系統からの代表1件と選定理由、権利再検証結果(URL・確認文言・取得日時)は
`er018_output/.../stories/{key}/selection.md`+`rights_check.md`に保存。要約:

| 系統 | 選定 | 権利確認方法 | 結果 |
|---|---|---|---|
| 01_life_history | "Crossing the Plains"(LOC wpalh001978、ox遭遇) | HTTP GET 3回試行→Cloudflare 403(bot challenge、コード起因でないことを確認)→委任文の規定どおりweb_search 1 call(max_tool_calls=2)にfallback | 権利文言再確認(より詳細な版、収集メタデータ追加取得)。ただしマニュスクリプト本文自体は非公開のため、ox遭遇の具体的展開は未確認のまま(Seedにも明記) |
| 02_historical | Franklinの自伝、フィラデルフィア到着とパン3個の逸話(Gutenberg #148) | 直接HTTP GET成功(200) | 権利文言をページ内2箇所で逐語確認。実際のエピソード本文も直接読了(捏造なし) |
| 03_japanese_lit | 宮沢賢治「注文の多い料理店」(青空文庫card1927.html) | 直接HTTP GET成功(200)。ただし`requests`の自動エンコーディング判定がISO-8859-1に誤検出(生バイトは実際にはUTF-8)し文字化けする不具合を発見、`resp.content`を明示的にUTF-8でdecodeし直して確認 | 没年1933(90年以上前、現行70年ルール・旧50年ルール双方を明確に満了)を確認。このカードは旧テンプレートで「著作権：あり/なし」バッジ欄自体が存在しない(S-1 REPORT §8の懸念に対する回答: バッジが曖昧なのではなく、テンプレートにバッジ欄がない)。この不具合により、スクリプト自身の`--step verify`自動一致判定はFalseになる(既知の限界として記録、rights_check.md参照) |
| 04_world_lit | ガルシン「信号」(Gutenberg #68619収録アンソロジー) | 直接HTTP GET成功(200、着地ページ+本文.txt両方) | "Public domain in the USA."をdcterms:rightsフィールドで逐語確認。本文も直接読了し、実際の筋を正確に把握(捏造なし) |

**追加検索の使用**: 01系統のみ、直接HTTP GET不能(Cloudflare)のためweb_search
1 call使用(委任文の許可範囲内)。他3系統は直接HTTP GETのみで完結、追加
web_searchなし。

## §5 S-3 Story Seed化

各系統1 call(`gpt-5.6-luna`、json_schema strict)で実施。`seed.json`に
`original_summary`/`seed_elements`(4〜5項目)/`discarded_elements`/
`conversion_plan`を保存(4系統とも成功、リトライなし)。01系統のSeedは
「具体的なox遭遇の展開は未確認」という制約を`original_summary`にそのまま
反映させ、捏造を避けた。

## §6 S-4 Story本文生成

`er018_fiction_story_dna_e_axis_redesign_01.py`のWriter developer message・
4共通原則・[Characters]・[Length and level](280–420語)・
[Listening-friendliness]を逐語流用し、`[Core Provocation]`の代わりに
`[Story Seed]`を渡す方式で、系統ごと1 call(`gpt-5.6-luna`、effort high)。
4本とも1回目の呼び出しで成功(リトライ0回)。語数: 01=398語、02=404語、
03=390語、04=438語(04のみ目安280–420語をやや超過、許容範囲内)。
全文は`stories_all.md`、ブラインド版は`blind.md`+`blind_key.json`。

## §7 S-5 評価(Sonnet所見)

**Story 01 "The Open Gate"(ox遭遇由来)**: 何の話か即座に明確(暴走した牛と
家族の危機)。状況転換は自然(物音→動物パニック→家族の協力→解決)。
因果は単純明快で、A2読者に追いやすい。先が気になる(母親に向かって突進する
牛、というテンポの良い危険設定)。元ネタのマニュスクリプト本文が非公開だった
ため、実質的にSeedの核(家族+危険な動物+協力)だけを使った自由な再構成に
近く、説明記事化のリスクはない。殺人・秘密・SFギミックなし。英語学習用として
十分成立。

**Story 02 "Two Plus One"(Franklinのパン逸話由来)**: 何の話か明確(見知らぬ
街に着いた若者の空腹と親切の連鎖)。転換は自然(値段の誤解→気まずさ→
親切心→予想外の恩返し)。因果は明快だが、緊迫感は他の3本より穏やか
(危険を伴わない温かい話であり、「先が気になる」度合いはやや低いが、
「叔母は来るか」というフックが機能している)。元ネタの具体的なパン購入
エピソードを的確に近代化しており、説明記事化していない。殺人・秘密・SF
ギミックなし。A2として自然な会話文中心で成立。

**Story 03 "The Kind Lodge"(宮沢賢治「注文の多い料理店」由来)**: 何の話か
明確(遭難したハイカーが親切なロッジに入り、実は捕食対象だったと気づく)。
状況転換(丁寧な指示が徐々に不穏になる)は原作の構造をそのまま活かしており
非常に自然で、緊張感も高い。因果は明快。ただし4本の中で最も「原作の筋・
どんでん返しをそのまま近代化しただけ」という色が強く、独自の再構成度は
相対的に低い(委任文のconversion_planどおり「設定の近代化」は行っているが、
オチ自体は原作と同一)。説明記事化はしていない(ナレーションとして成立)が、
Production転用時は独自性の確保がより必要になる点を留意すべき。「唐突な
SFギミック」については、スマートロッジ(AI風の声)という新しい仕掛けは
原作にない要素だが、物語の根幹(親切な建物→実は捕食装置)を近代的手段で
再現したものであり、原作と無関係などんでん返しを取ってつけたわけではない。
殺人描写はない(捕食が示唆されるのみ、グラフィックではない)。A2として
成立(短文・対話中心)。

**Story 04 "The Red Scarf"(ガルシン「信号」由来)**: 何の話か明確(鉄道職員
Mayaと、不当な扱いに苦しむ隣人の破壊行為、それを防ぐための決断)。状況転換
(発見→対立→絶望的な時間制約→即興の警告)は極めて自然で因果も明快。
「先が気になる」度合いは4本の中で最も高い(列車の接近というタイムリミット
+代替手段のない絶望的状況)。原作の設定(男性2人の同僚関係、自傷による
赤旗の代用)を、Maya(女性主人公)+亡き父の形見の赤いスカーフ(焼く)という
新しい象徴的要素に置き換えており、自傷描写を避けつつ犠牲の重みを保持した、
4本の中で最も独自の再構成度が高い例。原作のあいまいな結末(赦しは即座には
訪れない)も踏襲しており、説明記事化していない。殺人は起きない(未遂・
阻止)。秘密・SFギミックなし。A2として十分成立、感情的な深みもある。

**4系統の質の差**: 04(Red Scarf)と01(Open Gate)は独自の再構成度が高く、
緊張感も強い。02(Two Plus One)は温かいが緊張感は控えめ。03(Kind Lodge)は
完成度は高いが原作(有名作)の筋への依存度が4本中もっとも高い。

**旧完全創作方式(RANDOM-DNA・BIAS-RETRIAL・E-AXIS)との差(Sonnet所見)**:
Story DNA/Core Provocation方式は、LLMが生成する挑発軸(Core Provocation)や
E軸(死・暴力の程度)を明示的に設計・制御しないと、殺人ミステリー等の
型に偏りやすいという課題があった(過去のBIAS-RETRIAL/E-AXIS Trialの
経緯どおり)。本Trial(外部ソース由来)では、4本とも実在の人間の営みから
出発しているため、暴力性の制御軸を明示的に設けなくても、殺人に頼らない
自然な多様性(動物との遭遇、親切の連鎖、寓話的などんでん返し、鉄道の
モラルジレンマ)が得られた。一方、外部ソース方式には権利確認(URL精査・
bot対策・エンコーディング不具合の発見と対処)という、完全創作方式にはない
追加コストがあり、また03のように「原作の筋にどれだけ近いか」という
新しい懸念軸(完全創作にはない、著名な既存作品への依存リスク)が生じる。
総じて、両方式は異なる強み・弱みを持ち、外部ソース方式は「暴走しやすい
トロープ回避」の観点で有利、完全創作方式は「独自性の担保」の観点で有利、
という暫定所見(Sonnet、Fableの追加判断を要する)。

## §8 権利上の注意点(Sonnet所見、暫定)
- 「Web公開=自由利用」ではなく、各候補ともソース自身の権利表示(LOCの
  rights statement/Gutenbergのライセンス文言/Wikisourceの"published
  before 1931"表示/青空文庫の方針文)を確認できた候補のみ表に残した。
- 青空文庫の懸念は本委任(続行分)のS-2で解消: 実際のカードURL
  (`cards/000081/card1927.html`、S-1の`source_url`フィールドが誤って
  blog索引ページを指していた点も修正)を直接HTTP GETし、没年1933年を確認。
  このカードは旧テンプレートで「著作権：あり/なし」バッジ欄自体が
  存在しないことも判明(§4参照)。あわせて、Python `requests`の自動
  エンコーディング判定がこのページでISO-8859-1に誤検出する不具合を発見し、
  `resp.content`を明示的にUTF-8でdecodeし直すことで正しく確認した
  (`--step verify`のスクリプト内蔵チェックはこの不具合によりFalseを返す
  既知の限界として記録、rights_check.md参照。スクリプト自体は今回修正して
  いない)。
- 01系統(LOC)は直接HTTP GETがCloudflareのbot challenge(HTTP 403)で
  阻まれたため、委任文の規定どおりweb_search 1 callにfallbackして権利
  文言・カタログメタデータを再確認した(§4参照)。マニュスクリプト本文
  自体は非公開のため、ox遭遇の具体的展開はSeedでも「未確認」と明記して
  捏造を避けた。
- 「賢者の贈り物」「首飾り」等の著名作は、翻案の独自性確保だけでなく、
  版元・翻訳者クレジット表記の要否についても、Production検討時には
  別途確認が必要(本Trialでは英語原文からの直接翻案を想定しており、
  日本語訳版は使わない)。

## §9 QCD(実績、完走)

- 実行: S-1(検索4 call)+S-2(web_search fallback 1 call、01系統のみ)+
  S-3(Seed化4 call)+S-4(Story生成4 call)= API call合計13回、全て成功
  (技術的retry 0回)。予算上限¥200に対し、実測累計費用は
  **¥36.45**(内訳: S-1 ¥28.83既報 + 今回追加 ¥7.62)。上限の18%程度で
  完走し、大幅な余裕を残した。
- `cost.json`(累計): `{"total_usd": 0.227821, "total_jpy": 36.45,
  "record_count": 13, "web_search_call_total": 18}`。
- 予算運用: 今回の委任文どおり、¥200は暴走検知のGuardrailとして運用し、
  各stage後の`budget_guard`ログ(逐次記録済み)で進捗を確認しながら実行。
  暴走(想定外の大量発火・同一失敗のretry loop等)は発生しなかった。
- **観測(既報、再掲)**: S-1実行時、`max_tool_calls=3`を指定したにも
  関わらず実測`web_search_call_count`は4,4,4,3(4系統中3系統が指定
  上限を1回超過)。今回追加したS-2のweb_search fallback呼び出しでも、
  `max_tool_calls=2`指定に対し実測`web_search_call_count=3`(1回超過)を
  再度観測した。OpenAI側のResponses APIにおける`max_tool_calls`パラメータ
  は、複数回のTrialで一貫して「厳密なhard capではない」ことが確認できた
  (本Trial単独の観測であり、他Trial/Productionでの一般化はFableの追加
  判断を要する)。
- S-3/S-4は各4 call、budget_guardが各step後に累計費用を確認しながら
  進行し、上限超過は一度も発生しなかった。

## §10 Sonnet仮分類
**VALIDATED**(委任文が定める到達上限)。S-1〜S-5(選定・権利再検証・
Seed化・Story生成・評価)を完走し、4本すべてで技術的失敗・リトライなし、
権利確認も4系統とも実施(1系統はHTTP GET不能によりweb_search fallback、
他3系統は直接HTTP GET)。ただし§7の所見どおり、03系統(Kind Lodge)は
原作(有名作)の筋への依存度が他3本より高く、Production転用時は追加の
独自性確保が必要という質的な留保がある。Production Fiction仕様への
反映は本タスクの対象外であり、`APPROVED_FOR_PRODUCTION`は人間ユーザーの
判断を要する。

## §11 Fable評価(ブラインド: blind.mdを先に読み、key開封後も判断不変。A=03日本文学、B=01人生談、C=04世界文学、D=02歴史逸話)

(1)4本とも「何の話か」が冒頭数文で分かり、状況転換が段階的で、冒頭→展開→結末の因果が追える。旧完全創作方式で問題だった「記憶技術の売買・保存への収束」「唐突な殺人」「SFギミックで話を成立させる」はいずれも出ていない(殺人0/4)。英語学習用として4本とも成立。(2)系統差: 人生談(B『The Open Gate』)と歴史逸話(D『Two Plus One』)は現実的で温かく因果が明快、緊張は控えめ。文学2本(A『The Kind Lodge』、C『The Red Scarf』)は緊張と結末の強さで勝るが、原作への依存度が高い。特にAは「注文の多い料理店」の構造(歓迎→指示の段階的不穏化→客が料理)をほぼそのまま現代化しており独自性が最も低く、太字の機械メッセージ演出(旧創作方式の癖)も再登場している。Cは原作の血のハンカチを「父の形見のスカーフを燃やす」に置換し、女性主人公化・病児の乗客追加で再構成度が高い。(3)Bは元マニュスクリプト本文が非公開のため、実質的にはSeed(家族+暴れる牛+協力)からの自由創作に近く、「外部の種」の寄与は骨格のみ。(4)権利: 4件ともPublic Domain確認済み(LOCはrights statement+メタデータ、Gutenberg/青空文庫は本文ページで逐語確認)。青空文庫ページのrequestsエンコーディング誤判定はスクリプト側の既知の限界として記録済み(rights自体は問題なし)。(5)費用: 累計¥36.45(S-1検索¥28.83が支配的、S-2〜S-5は¥7.62)。

## §12 分類

**VALIDATED**(外部Story Seed方式は成立。Production Fiction仕様への反映は行わない)。ユーザー判断事項: ①この方式をFiction familyの主方式候補として次段階(系統別に各2〜3本の追加生成、¥10程度、検索は最小)へ進めるか(Fable推奨: 進める)。②著名作の扱い: 「注文の多い料理店」「賢者の贈り物」級の広く知られた作品は素材から外す/または再構成度の最低基準(舞台・人物・結末装置のうち2つ以上を変更 等)を設けるか(Fable推奨: 最低基準を設ける)。③系統の優先: 人生談・歴史逸話(現実系・因果明快)を主、文学(緊張が強い)を従とする配分でよいか。④検索コスト: 候補探索は系統ごとに1 call・`max_tool_calls`が超過し得る前提で、1 Trialあたり検索¥30前後を許容するか。
