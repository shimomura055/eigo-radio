# TOPIC-SELECTION-CHATGPT-REPRO-01 REPORT

管理ID: TOPIC-SELECTION-CHATGPT-REPRO-01
実行: Sonnet(claude-sonnet-5)、2026-09-24
出力先: `er016_output/topic_selection_chatgpt_repro_01/`
スクリプト: `er016_topic_selection_chatgpt_repro_01.py`(新規、Production非該当)

**再現判定: [Fable判定待ち]**

参考事実(Sonnetは判定せず、以下を事実として提示する):
- Luna最終選定は8件(目標20件に対し8件、40%)。
- Reference20件中、Luna最終8件と「同一話題」1件(#3米中首脳会談)、
  「類似話題」1件(#2 AI・国連)、「無関係」6件。Reference20件中18件は
  Luna最終8件に対応候補が無い。
- Step A生プール(114件、20候補×8サブレーン相当)の段階でも、Reference20件
  のうち文字列一致で確認できた同一話題は1件(#3)のみ。
- Phase 4(a)診断(Reference20件を直接検索クエリとして使用)では11/20
  (55%)を発見できており、**API web_search自体の検索能力の問題というより、
  Step Aの広域探索(未指定query・広いカテゴリ指示)がこれらの素材を
  拾いきれなかったこと**、および**Step Dのurl_in_citations機械除外
  (40件中31件=78%失格)** が主要因である可能性が高い(詳細はD節)。

---

## FIX-01: Step D検証ルール訂正(2026-09-24)

初回run(以下A〜H節の本文)のStep D検証で使用した除外ルール
`url_in_citations=false→失格`(Fable設計)が、Responses APIで
`text.format=json_schema`(構造化出力)を使用した場合にモデルが本文中の
`url_citation`アノテーションを返さないケースが多いという技術的挙動により、
**Lunaの探索・選定・Hook生成の判断とは無関係に、Step C 40件中31件
(78%)を機械除外していた**ことが判明した(詳細な発生経緯はG節参照)。
これはFableのオーケストレーション(工程設計)側のミスであり、Step A〜C
(検索・選定・Hook生成)自体はLunaが独立判断で行った結果である。

本FIX-01では**Step A〜C(`stepA_1〜8.json`/`stepB_selected.json`/
`stepC_hooks.json`)を一切変更せず**、Step Dの失格理由から
`url_in_citations`条件のみを削除して再検証し(値自体は`url_in_citations`
フィールドとして記録は継続)、Step E(最終選定)を1回だけ再実行した。
Prompt文言(developer/user固定部分)は初回のStep E Promptと完全一致を
確認済み(候補リスト部分のみ差分、diff確認方法はRESULT_PACKET_TSCR.md
FIX-01節0項参照)。

初回8件の結果(以下「初回(検証ルール不備あり)」)は履歴としてそのまま残し、
訂正後の結果を別表・別節として追加する(B節・C節)。

**結果概要**: Step D fix01通過35件(失格5件、全てoutside_window)。
Step E fix01最終選定20/20件(目標20件を達成)。

---

## A. 条件差分(ChatGPT vs 前回Trial-01 vs 今回)

全文は`er016_output/topic_selection_chatgpt_repro_01/phase1_audit.md`。
要旨(15項目の3列表):

| 項目 | ChatGPT実行 | 前回Trial-01 | 今回 |
|---|---|---|---|
| 検索基準時刻 | 2026-09-23 21:05 JST | 実行時刻(2026-09-24T07:48 JST) | 2026-09-23 21:05 JST固定 |
| 検索期間 | 不明 | T_now−24h(スライド窓) | 2026-09-22T21:05〜09-23T21:05 JST固定窓 |
| Search backend | ChatGPT Web Search(非公開) | OpenAI API web_search tool | 同左 |
| 探索カテゴリ | ユーザー列挙(均等化否定) | 5レーン | 8サブレーン(ユーザー列挙に近づけた細分化) |
| Candidate pool規模 | 不明 | 約50〜75件 | 114件(8×12〜17件) |
| Topic選定/Hook/Ranking | Step B/C/Eの3工程(ユーザー指示) | Hook生成とRanking相当を1 Promptに混在 | Step B(選定)/C(Hook)/E(Ranking)を3工程に分離 |
| Hook生成の例示 | 台風停電・Meta Muse例 | 例示なし、条件文のみ | 例2つを明示追加 |
| 検証の位置 | 不明 | Ranking後に検証 | Ranking(Step E)**前**に検証(Step D)して機械除外 |
| モデル/effort | 不明 | gpt-5.6-luna/medium | 同左(Phase4(d)のみhigh、(c)は条件未達で未実施) |

(全15項目の詳細・限界説明は`phase1_audit.md`参照)

### 時刻窓の再現限界
OpenAI `web_search`ツールに日付フィルタ引数は無い。Promptへの窓明記+
候補時刻申告+Step Dでのメタ時刻実取得、の3段で近似実現した。検索
インデックスは2026-09-24時点のものであり、2026-09-23当時にChatGPT Web
Searchが「見えていた」結果集合を完全再現することは技術的に不可能。
SNS/Trendアーカイブ(Phase 0)も同様の限界がある。

---

## B. Phase 0/Step A〜E件数推移

| 段階 | 件数 |
|---|---|
| Phase 0(アーカイブSignal取得) | 17テーマ(閾値10、1回で達成) |
| Step A合計(8サブレーン) | 114件(sublane別12〜17件) |
| Step B選定(最大40) | 40件 |
| Step C Hook生成 | 40件(not_covered 0) |
| Step D検証通過 | 9件(失格31件: url_not_in_citations 31、outside_window 5、重複あり) |
| Step E最終選定 | **8件**(目標20件) |

## B. Luna最終選定の表

### 初回(検証ルール不備あり、8件)

| Rank | 素材概要 | Hook(ja) | Category | Source | published(申告/検証) | 窓内判定 | 距離 | answer_in_source要約 |
|---|---|---|---|---|---|---|---|---|
| 1 | AIチャットボットが露制裁対象メディアの内容を警告なしに要約(RSF調査) | AIにニュースを要約させるとき、制裁対象メディアの情報も混ざる？ | AI/Tech | Euronews | 2026-09-23 11:21 GMT+2 / 未検証(fetch失敗) | unverifiable | 中 | RSF調査で複数AIチャットボットが警告なしにロシア国営メディア内容を要約・引用 |
| 2 | 米・イラン協議進展で原油価格下落 | 外交協議の進展観測だけで、原油価格はどこまで動く？ | Business/Economy | Euronews | 09-23 07:38 GMT+2 / 09-23 05:38 UTC(検証済) | within_window | 中 | トランプ氏の協議「非常に生産的」発言等で北海ブレントが一時$100割れ |
| 3 | MIT昆虫サイズ飛行ロボットがAI制御で450%高速化 | 昆虫サイズの飛行ロボットは、AIでどこまで機敏になった？ | AI/Tech | ScienceDaily | 2026-09-22 / 未検証(メタ情報無し) | unverifiable | 遠い | 速度約450%・加速度約250%向上、11秒間に10回宙返り |
| 4 | 国連の場でAI規制をめぐりTrump氏とGuterres氏らが対立 | AIに命に関わる判断を任せる前に、各国は何をめぐって対立している？ | AI/Tech | Euronews | 09-23 10:40 GMT+2 / 09-23 08:40 UTC(検証済) | within_window | 中 | Trump氏はAI規制に否定的、Guterres氏は生命判断を機械に委ねるべきでないと警告 |
| 5 | AlibabaがAI・クラウド基盤を欧州へ拡大 | AI競争は、アプリだけでなくデータセンターの場所まで変える？ | AI/Tech | Euronews | 09-23 10:29 GMT+2 / 09-23 08:29 UTC(検証済) | within_window | 中 | フィンランド・オランダ・トルコに新クラウドリージョン、独仏でデータセンター拡張 |
| 6 | EUカラス氏、ホルムズ海峡等の自由航行を要求 | 二つの海峡の航行が止まると、外交は何を動かそうとする？ | Hard News | Euronews | 09-23 11:32 GMT+2 / 09-23 09:32 UTC(検証済) | within_window | 遠い | カラス氏がホルムズ・バブエルマンデブ海峡の自由航行を要求、米イラン外交も議題 |
| 7 | 米中首脳会談が欧州の関税・AI・レアアースに波及 | 米中首脳会談の結果は、なぜ欧州の関税やAIにも響く？ | Business/Economy | Euronews | 09-23 08:00 GMT+2 / 09-23 06:00 UTC(検証済) | within_window | 中 | 関税・AI・レアアース・貿易休戦等が欧州経済に与える影響を解説 |
| 8 | トルコの投資ファンド不正で約45万人に影響 | 投資ファンドの問題は、なぜ数十万人規模に広がった？ | Business/Economy | Euronews | 09-23 12:33 GMT+2 / 09-23 10:33 UTC(検証済) | within_window | 遠い | Tera Yatirim会長逮捕、131ファンド・約45万人・180億ドル超が清算対象 |

全文(候補ID・URL等)は`stepE_final.json`参照。

### 訂正後(FIX-01、20件)

Step D fix01検証: 通過35件、失格5件(全てoutside_window)。通過35件を
Step Eの入力とし、Lunaが20/20を選定(unresolved 0)。

| Rank | 素材概要 | Hook(ja) | Hook(en) | Category | Source | published(申告/検証) | 窓内判定 | 距離 | answer_in_source要約 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 台風通過後も周辺河川から印旛沼へ水が流れ込み、排水が追いつかない中で堤防決壊と冠水が起きた経緯を伝えています。 | 台風が去った後も、水害が広がるのはなぜ？ | Why can flooding continue to spread even after a typhoon has passed? | Hard News | FNNプライムオンライン | 2026年9月23日 水曜 午後6:19 / 2026-09-23T09:19:00+00:00 | within_window | 近い | 台風通過後も周辺河川から印旛沼へ水が流れ込み、排水が追いつかない中で堤防決壊と冠水が起きた |
| 2 | 国境なき記者団が6つのAIチャットボットを調査したところ、ChatGPT、Claude、Grokなどが、EU制裁対象メディアの内容を含めて要約したと報じています。 | AIにニュースを要約させるとき、制裁対象メディアの情報も混ざる？ | When AI summarizes the news, can it also include information from sanctioned media? | AI/Tech | Euronews | Published on 23/09/2026 - 11:21 GMT+2 / 2026-09-23T09:21:16+00:00 | within_window | 中 | 国境なき記者団の調査では、複数のAIチャットボットがEU制裁対象のロシア国営メディアの内容 |
| 3 | 香り付きの清掃製品から放出される成分が、室内のオゾンと反応してナノ粒子を形成する可能性を研究が示した。 | 香りのよい掃除用品が、室内で別の粒子を生むことがある？ | Can scented cleaning products create different particles indoors? | Health | ケアネット（HealthDay News） | 公開日：2026/09/23 / 2026-09-22T19:00:00+00:00 | within_window | 遠い | 香り付き清掃製品の成分が室内オゾンと反応してナノ粒子を形成し、粒子が肺の奥まで到達する可能 |
| 4 | 新大阪から東京へ向かう史上初の夜行新幹線「東海道ルミエールエクスプレス」が、9月22日夜に運行されました。 | 夜行新幹線は、移動時間を旅の体験に変えられる？ | Can an overnight bullet train turn travel time into part of the experience? | Lifestyle | FNNプライムオンライン | 2026年9月23日 水曜 午前11:55 / 2026-09-23T02:55:00+00:00 | within_window | 近い | 夜行新幹線は新富士駅で夜を明かし、乗客が明け方の富士山を眺める行程で運行された。 |
| 5 | 研究者らが、約1,500人から得た630万個超の脳細胞の解析をもとに、ヒト前頭前皮質の遺伝子活動を大規模に地図化した。 | 脳細胞の遺伝子活動を地図にすると、病気の理解はどう変わる？ | How could mapping gene activity in brain cells change our understanding of disease? | Science | Nature | 23 September 2026 / 2026-09-23T00:00:00+00:00 | within_window | 遠い | 約1,500人から得た630万個超の脳細胞を解析し、前頭前皮質の遺伝子活動を大規模に地図化 |
| 6 | 久米島を代表する樹齢200年以上の「久米の五枝のマツ」が、松くい虫の被害で枯死した経緯を追った。 | 200年以上の樹齢を持つ地域の象徴が枯れた後、何を残せる？ | What can be preserved after a local symbol more than 200 years old dies? | Environment | QAB NEWS Headline | 2026年9月23日 / 未検証 | unverifiable | 近い | 久米の五枝のマツは松くい虫で枯死したが、久米島町は3Dデータの記録や後継木の育成を進めてい |
| 7 | セガがソニックシリーズ全体の終了を検討していたものの、映画第1作の成功がシリーズ継続を後押ししたという発言が紹介された。 | 映画の成功が、終わりかけたゲームシリーズを救うことはある？ | Can a successful film save a game series that was close to ending? | Entertainment | Game News Round-Up | Wednesday, 23 September 2026 / 2026-09-22T21:11:20.839000+00:00 | within_window | 中 | セガがソニックシリーズ全体の終了を検討していたものの、映画第1作の成功がシリーズ継続を後押 |
| 8 | トルコ当局が、投資ファンド問題の中心となっている証券会社Tera Yatirimの会長を逮捕しました。 | 投資ファンドの問題は、なぜ数十万人規模に広がった？ | Why did the investment-fund crisis affect hundreds of thousands of people? | Business/Economy | Euronews | Published on 23/09/2026 - 12:33 GMT+2・Updated 13:32 / 2026-09-23T10:33:15+00:00 | within_window | 遠い | Tera Yatirimの会長が逮捕され、131のファンドに投資する約45万人が影響を受け |
| 9 | トランプ大統領が米国とイランの代表団による協議を「非常に生産的」と説明したことを受け、原油価格が下落しました。 | 外交協議の進展観測だけで、原油価格はどこまで動く？ | How far can oil prices move on signs of diplomatic progress? | Business/Economy | Euronews | Published on 23/09/2026 - 7:38 GMT+2・Updated 9:24 / 2026-09-23T05:38:13+00:00 | within_window | 中 | トランプ大統領が米国とイランの協議を「非常に生産的」と説明したことなどを受け、北海ブレント |
| 10 | シンガポール国立大学の研究者が、ルテチウム原子を使った光原子時計を開発し、従来の最高精度の時計を上回った。 | 時計の精度が上がると、将来の「1秒」の定義も変わる？ | Could greater clock precision eventually change the definition of one second? | Science | Nature | 23 September 2026 / 2026-09-23T00:00:00+00:00 | within_window | 遠い | ルテチウム原子を使う光原子時計が従来の最高精度を上回り、将来の秒の再定義や衛星測位、基礎物 |
| 11 | MITの昆虫サイズの飛行ロボットが、AIベースの制御システムによって速度を約450%、加速度を約250%向上させた。 | 昆虫サイズの飛行ロボットは、AIでどこまで機敏になった？ | How agile did an insect-sized flying robot become with AI? | AI/Tech | ScienceDaily | September 22, 2026 / 未検証 | unverifiable | 遠い | MITの昆虫サイズの飛行ロボットは、AIベースの制御で速度が約450%、加速度が約250% |
| 12 | 富士山頂を約17年間にわたって職場であり住まいとしてきた写真家、上田めぐみさんを紹介。 | 観光客が訪れる富士山頂で、17年間暮らすとはどんな生活？ | What is life like after living for 17 years at the summit of Mount Fuji, where most people only visit? | Lifestyle | Euronews | 11:17 / 2026-09-23T09:17:56+00:00 | within_window | 近い | 写真家の上田めぐみさんは、富士山頂を約17年間、職場であり住まいとして撮影活動を続けてきた |
| 13 | 体長約2メートルのエミューが逃走しましたが、その後確保されたと報じています。 | 街中で突然、身長2メートル級の鳥に出会ったら？ | What happens when a nearly two-meter-tall bird suddenly appears in town? | Other | 関西テレビ | 09/23 10:44 / 未検証 | unverifiable | 近い | 体長約2メートルのエミューが逃走したが、その後確保され、目撃者がダチョウと見間違えるほどの |
| 14 | J:COMのインターネットサービスで大規模な通信障害が発生し、利用者がネットに接続しづらい状態になったと報じています。 | ネットが突然使えなくなったとき、通信障害はどこまで広がっていた？ | When the internet suddenly stops working, how widespread can a service outage be? | Consumer | 関西テレビ | 09/23 16:00 / 未検証 | unverifiable | 近い | J:COMのインターネットサービスで大規模な通信障害が発生し、利用者が接続しづらい状態にな |
| 15 | オーストラリアの研究者らが、片頭痛治療・管理におけるショウガの有効性を、ランダム化比較試験の系統的レビューとメタ解析で検討した。 | ショウガは片頭痛の治療を補う選択肢になりうる？ | Could ginger become an option to complement migraine treatment? | Health | ケアネット | 公開日：2026/09/23 / 2026-09-22T19:00:00+00:00 | within_window | 遠い | 研究では、ショウガ単独または補助療法としての片頭痛への効果を、プラセボや複数の治療薬と比較 |
| 16 | 地球の1日の長さが数十年単位で数ミリ秒変化する現象について、地球内部の重力トルクと電磁・機械的トルクの競合が関与するとされる。 | 地球の内部で綱引きが起きると、1日の長さまで変わる？ | Can a tug-of-war inside Earth change the length of a day? | Science | Nature | 23 September 2026 / 2026-09-23T00:00:00+00:00 | within_window | 遠い | 地球内部の重力トルクと電磁・機械的トルクの競合が、数十年単位で数ミリ秒変化する地球の自転速 |
| 17 | 2029年完成予定のうるま市総合体育館を題材に、高校生が利用者目線のアイデアを考えるワークショップに参加した。 | 未来の体育館は、AIで混雑や移動の不便をどう減らす？ | How could AI help a future sports arena reduce crowding and travel barriers? | AI/Tech | QAB NEWS Headline | 2026年9月23日 / 未検証 | unverifiable | 近い | 高校生が生成AIも活用し、混雑状況を確認できるアプリや、誰もが利用しやすいシャトルバスを提 |
| 18 | 国連総会で、トランプ米大統領がAI規制に否定的な姿勢を示す一方、グテーレス国連事務総長は生命・死に関わる判断を機械に委ねるべきでないと警告した。 | AIに命に関わる判断を任せる前に、各国は何をめぐって対立している？ | Before entrusting life-or-death decisions to AI, what are countries divided over? | AI/Tech | Euronews | Published on 23/09/2026 - 10:40 GMT+2 / 2026-09-23T08:40:08+00:00 | within_window | 中 | トランプ大統領がAI規制に否定的な姿勢を示す一方、グテーレス国連事務総長は生命や死に関わる |
| 19 | 高市総理大臣が、国民民主党との連立について「必要な対応は常に考えている」と述べ、連立拡大に含みを持たせました。 | 連立の組み替えは、次の国会で何を実現するためなのか？ | What would a possible coalition reshuffle aim to achieve in the next Diet session? | Hard News | テレビ朝日 | 2026年9月23日 18:50 / 2026-09-23T09:50:00+00:00 | within_window | 近い | 高市総理は国民民主党との連立に含みを持たせ、臨時国会で消費税減税関連法案などの成立を目指す |
| 20 | EUの外交・安全保障上級代表カラス氏が、イラン外相との会談後、ホルムズ海峡とバブ・エル・マンデブ海峡の航行を自由に保つよう求めました。 | 二つの海峡の航行が止まると、外交は何を動かそうとする？ | When passage through two straits is threatened, what is diplomacy trying to keep moving? | Hard News | Euronews | Published on 23/09/2026 - 11:32 GMT+2・Updated 11:44 / 2026-09-23T09:32:03+00:00 | within_window | 遠い | EUのカラス氏はホルムズ海峡とバブ・エル・マンデブ海峡の自由で妨げのない航行を求め、米国と |

全文(候補ID・URL等)は`stepE_final_fix01.json`参照。C027(米中首脳会談、
初回Rank7)は今回もStep D通過(35件中)したが、Step Eの最終20件には
Lunaの判断で含まれなかった(dedupe_groupの重複が原因ではなく単独
グループ、詳細はRESULT_PACKET_TSCR.md FIX-01節4項)。

### Step C 40件の一覧(Step A〜Cは無変更、Step D/E再検証の母集団)

| candidate_id | 素材概要 | hook_ja | answer_in_source | sublane | 距離 |
|---|---|---|---|---|---|
| C001 | 台風25号の影響で、千葉県と神奈川県で合わせて7人が死亡し、5人が行方不明となっていると報 | 台風の浸水被害は、現場でどうやって復旧が始まる？ | 有 | 1 | 近い |
| C002 | 台風25号による豪雨で、千葉県が管理する北印旛沼の堤防約100メートルなどが決壊し、周辺で | 堤防が約100メートル決壊した地域で、次に進められる対策は？ | 有 | 1 | 近い |
| C003 | 千葉県の印旛沼で堤防の決壊が確認され、管理開始以降で最高となる水位5.04メートルを観測し | 過去最高水位の沼で、住民はどこへ避難した？ | 有 | 1 | 近い |
| C004 | 台風通過後も周辺河川から印旛沼へ水が流れ込み、排水が追いつかない中で堤防決壊と冠水が起きた | 台風が去った後も、水害が広がるのはなぜ？ | 有 | 1 | 近い |
| C005 | 台風25号による千葉県・神奈川県の被害で、新たに4人の死亡が確認され、死者は計10人となっ | 大規模水害で鉄道が止まると、復旧にはどれほど時間がかかる？ | 有 | 1 | 近い |
| C006 | 山形県酒田市飛島の海岸で、身元不明の遺体が見つかったと報じています。行方不明になっている6 | 海岸で見つかった遺体は、行方不明の子どもと確認されたのか？ | 有 | 1 | 近い |
| C007 | 高市総理大臣が、国民民主党との連立について「必要な対応は常に考えている」と述べ、連立拡大に | 連立の組み替えは、次の国会で何を実現するためなのか？ | 有 | 1 | 近い |
| C008 | 高市総理大臣が国連総会の一般討論演説で、安全保障理事会改革の必要性を訴えたと報じられていま | 日本の首相は国連で、国際秩序のどこを変えるべきだと訴えた？ | 有 | 1 | 近い |
| C009 | 新大阪から東京へ向かう史上初の夜行新幹線「東海道ルミエールエクスプレス」が、9月22日夜に | 夜行新幹線は、移動時間を旅の体験に変えられる？ | 有 | 1 | 近い |
| C013 | 体長約2メートルのエミューが逃走しましたが、その後確保されたと報じています。目撃者がダチョ | 街中で突然、身長2メートル級の鳥に出会ったら？ | 有 | 1 | 近い |
| C014 | J:COMのインターネットサービスで大規模な通信障害が発生し、利用者がネットに接続しづらい | ネットが突然使えなくなったとき、通信障害はどこまで広がっていた？ | 有 | 1 | 近い |
| C105 | J:COMは9月23日、全国でインターネット接続が利用できない、または利用しづらい状況と、 | 通信障害のとき、ネットだけでなく問い合わせ窓口にも起きることは？ | 有 | 8 | 近い |
| C015 | 北海道の観光列車「富良野・美瑛ノロッコ号」がラストランを迎え、全国から訪れた人々が別れを惜 | 長年愛された観光列車の最後の日、沿線の人々はどう見送った？ | 有 | 1 | 近い |
| C016 | 北海道紋別市沖で漁船とプレジャーボートが衝突し、ボートが大きく損傷したと報じています。救助 | 海上で船同士が衝突したとき、救助の後に何が確認される？ | 有 | 1 | 近い |
| C017 | エチオピア北部ティグライ州の反政府勢力が州都メケレの空港を掌握し、アファール州でも政府軍と | 空港をめぐる戦闘は、地域の移動手段をどう変える？ | 有 | 2 | 遠い |
| C018 | トルコ当局が、投資ファンド問題の中心となっている証券会社Tera Yatirimの会長を逮 | 投資ファンドの問題は、なぜ数十万人規模に広がった？ | 有 | 2 | 遠い |
| C019 | EUの外交・安全保障上級代表カラス氏が、イラン外相との会談後、ホルムズ海峡とバブ・エル・マ | 二つの海峡の航行が止まると、外交は何を動かそうとする？ | 有 | 2 | 遠い |
| C020 | 国境なき記者団が6つのAIチャットボットを調査したところ、ChatGPT、Claude、G | AIにニュースを要約させるとき、制裁対象メディアの情報も混ざる？ | 有 | 2 | 中 |
| C023 | 国連総会で、トランプ米大統領がAI規制に否定的な姿勢を示す一方、グテーレス国連事務総長は生 | AIに命に関わる判断を任せる前に、各国は何をめぐって対立している？ | 有 | 2 | 中 |
| C025 | アリババは、フィンランド、オランダ、トルコに初のクラウドリージョンを設け、ドイツやフランス | AI競争は、アプリだけでなくデータセンターの場所まで変える？ | 有 | 2 | 中 |
| C027 | トランプ米大統領と中国の習近平国家主席による首脳会談を前に、関税、AI、レアアースなどの議 | 米中首脳会談の結果は、なぜ欧州の関税やAIにも響く？ | 有 | 2 | 中 |
| C028 | トランプ大統領が米国とイランの代表団による協議を「非常に生産的」と説明したことを受け、原油 | 外交協議の進展観測だけで、原油価格はどこまで動く？ | 有 | 2 | 中 |
| C030 | ロイター通信によると、イラン側は米国が軍事的圧力を緩和し港湾封鎖を解除すれば、7日以内にホ | ホルムズ海峡の開放は、どんな条件のもとで提案された？ | 有 | 2 | 遠い |
| C032 | MITの昆虫サイズの飛行ロボットが、AIベースの制御システムによって速度を約450%、加速 | 昆虫サイズの飛行ロボットは、AIでどこまで機敏になった？ | 有 | 3 | 遠い |
| C033 | 研究者らが、約1,500人から得た630万個超の脳細胞の解析をもとに、ヒト前頭前皮質の遺伝 | 脳細胞の遺伝子活動を地図にすると、病気の理解はどう変わる？ | 有 | 3 | 遠い |
| C034 | 地球の1日の長さが数十年単位で数ミリ秒変化する現象について、地球内部の重力トルクと電磁・機 | 地球の内部で綱引きが起きると、1日の長さまで変わる？ | 有 | 3 | 遠い |
| C035 | シンガポール国立大学の研究者が、ルテチウム原子を使った光原子時計を開発し、従来の最高精度の | 時計の精度が上がると、将来の「1秒」の定義も変わる？ | 有 | 3 | 遠い |
| C040 | コーネル大学などの研究チームが、周囲の温度を感知し、互いに通信しながら液体を動かす微小ロボ | 微小ロボットは、環境を感じるだけでなく周囲を変えられる？ | 有 | 3 | 遠い |
| C041 | 韓国KAIST系の四足歩行ロボット「RAIBO2」が、1回の充電でフルマラソンを4時間19 | ロボット犬が長距離を走る鍵は、電池の大きさではない？ | 有 | 3 | 遠い |
| C044 | オーストラリアの研究者らが、片頭痛治療・管理におけるショウガの有効性を、ランダム化比較試験 | ショウガは片頭痛の治療を補う選択肢になりうる？ | 有 | 4 | 遠い |
| C047 | 香り付きの清掃製品から放出される成分が、室内のオゾンと反応してナノ粒子を形成する可能性を研 | 香りのよい掃除用品が、室内で別の粒子を生むことがある？ | 有 | 4 | 遠い |
| C056 | 慢性不眠症の人がメラトニンを長期使用した場合、5年間の心不全発症リスクが約90%高かったと | メラトニンの長期使用と心不全リスクは、どこまで確かめられている？ | 有 | 4 | 遠い |
| C073 | 富士山頂を約17年間にわたって職場であり住まいとしてきた写真家、上田めぐみさんを紹介。多く | 観光客が訪れる富士山頂で、17年間暮らすとはどんな生活？ | 有 | 6 | 近い |
| C076 | ミラノで開催されたVogue World 2026のフィナーレを飾った、6000個超の紙製 | 舞台を埋めた6000個の紙のオブジェは、何から生まれた？ | 有 | 6 | 遠い |
| C081 | 久米島を代表する樹齢200年以上の「久米の五枝のマツ」が、松くい虫の被害で枯死した経緯を追 | 200年以上の樹齢を持つ地域の象徴が枯れた後、何を残せる？ | 有 | 6 | 近い |
| C083 | 2029年完成予定のうるま市総合体育館を題材に、高校生が利用者目線のアイデアを考えるワーク | 未来の体育館は、AIで混雑や移動の不便をどう減らす？ | 有 | 6 | 近い |
| C084 | 4人組バンドのcinema staffが、2027年9月12日の豊洲PIT公演を最後に正式 | 人気アニメの曲を担ったバンドは、なぜ解散を選んだ？ | 有 | 7 | 近い |
| C097 | セガがソニックシリーズ全体の終了を検討していたものの、映画第1作の成功がシリーズ継続を後押 | 映画の成功が、終わりかけたゲームシリーズを救うことはある？ | 有 | 7 | 中 |
| C100 | アジア大会のバドミントン女子団体で、日本が韓国に勝利したと報じられた。韓国側ではアン・セヨ | 個人の勝利だけでは決まらない団体戦で、日本はどう韓国を上回った？ | 有 | 7 | 中 |
| C103 | 『原神』のVer.7.1アップデートが9月23日に実施され、新キャラクターや第七章の第三幕 | 6周年を迎えたゲームは、アップデートで何が変わった？ | 有 | 8 | 中 |

全40件で`answer_in_source`が"NOT_IN_SOURCE"となったものは0件
(Step C not_covered 0、初回B節と同じ)。

---

## C. Reference比較

### 初回(検証ルール不備あり、8件版)

詳細は`er016_output/topic_selection_chatgpt_repro_01/phase3_compare.md`
(自動計算`phase3_compare.json`+Sonnet手動確認)。要旨:

- **Reference非混入検査**: プロンプト内キーワードヒット2件検出も、手動
  確認によりいずれも「注入」ではなく「Lunaが独立に類似/同一話題を発見」
  したことによるもの(コードレベルでも`REFERENCE_20`定数はStep A〜Eの
  prompt構築関数から未参照)。**注入によるcontaminationは無し。**
- **Topic重複**: Luna最終8件×Reference20件で、同一話題1件(#3米中首脳
  会談)、類似話題1件(#2 AI・国連、但し具体的会議体は異なる)、無関係6件。
- **Step A生プール(114件)内包含**: 手動キーワード照合でReference20件中
  文字列一致は#3のみ(1/20)。自動ヒューリスティック(閾値0.3)は誤マッチ
  多数につき不採用(詳細はphase3_compare.md参照)。
- **Hook形式判定**(委任文定義ルール、「でしょうか」終止+共通名詞率>50%):
  Luna最終8件8/8・Reference20件20/20・Phase4(b)固定入力20/20・
  Phase4(d)固定入力(high)20/20が、いずれも`reinterpretation`
  (`question_ification`は全カテゴリで0件)。**このルールでは両者を
  判別できない**(Luna・Referenceとも「〜？」の口語疑問形が大半で
  「でしょうか」終止はどちらにも出現しないため)。
- **分布**: Lunaカテゴリ=AI/Tech4・Business/Economy3・Hard News1、距離=
  中5・遠い3(近い0)。俗っぽさ件数はLuna0/8、Reference4/20。Reference
  距離・source情報は原文に無いため比較不可(不明のまま記録)。

### 訂正後(FIX-01、20件版)

詳細は`er016_output/topic_selection_chatgpt_repro_01/phase3_compare_fix01.md`
(自動計算`phase3_compare_fix01.json`+Sonnet手動確認)。要旨:

- **Reference非混入検査**: 3件ヒット(初回2件+FIX-01のStep E入力
  プロンプトにC027が含まれたことによる1件追加)。手動確認の結果、
  いずれも注入ではない(C027はStep A段階でLunaが独立発見した実在候補)。
  **注入によるcontaminationは無し(結論は初回と同じ)。**
- **Topic重複**: Luna最終20件×Reference20件で、同一話題0件、類似話題
  1件(#2 AI・国連、C023)、無関係19件。**C027(米中首脳会談)はStep D
  fix01を通過した(35件中)がStep Eの最終20件には選ばれなかった**
  (Lunaの判断。dedupe_group上の重複制約は無し)。初回は「同一1件+
  類似1件」だったが、FIX-01では「同一0件+類似1件」に減少。
- **Step A生プール(114件)内包含**: Step A〜Cを再実行していないため、
  初回と同一(Reference20件中、文字列一致確認できるのは#3の1件のみ)。
- **Hook形式判定**: Luna最終20件20/20・Reference20件20/20とも
  `reinterpretation`(`question_ification`0件)。初回(8/8)から
  分類結果に変化なし。
- **分布**: Lunaカテゴリ=AI/Tech4・Hard News3・Science3・Health2・
  Lifestyle2・Business/Economy2・Environment1・Entertainment1・
  Other1・Consumer1(10種類に分散)、距離=近い8・中4・遠い8。俗っぽさ
  件数はLuna3/20、Reference4/20(初回0/8から改善)。**初回はStep D
  url_in_citations除外によりsublane 2・3由来に偏っていたが、FIX-01では
  8サブレーン中より多くのsublane由来の候補が最終選定に残り、カテゴリ・
  俗っぽさともに多様化した。**

---

## D. 差分切り分け(Phase 4)

**(a) 検索段階の到達性**(Luna+web_search、1 call): Reference20件を
直接検索クエリとして与えた場合、**11/20(55%)を発見**(published_time
申告付き)。未発見9件の主因は「該当ページは見つかったが公開日が窓外」
(#5,#8,#11,#18,#19,#20)または「窓内の該当記事が確認できず」(#7,#12,#14)。
→ API web_search自体は多くのReference素材に到達可能。窓内公開分の
取りこぼしは一部あるが、Step Aの広域・未指定query探索(0/20〜1/20相当)
より遥かに高い発見率であり、**「素材を直接指定して探す」のと「広く
探して後で選ぶ」のとでは、後者が大幅に取りこぼしている**ことを示す。

**(b) Hook生成段階の固定入力比較**(Luna、web_searchなし、1 call):
Reference20件の素材(Hook無し)をStep C同等Promptに入力した結果、
Lunaが生成したHookは20/20とも`reinterpretation`形式(Referenceと同じ
分類)。個別ペア比較でも、内容面でReference Hookと近い抽象化・再解釈が
行われている(例: #20クラゲ水槽→「職場に人工クラゲの水槽を置くサービスは、
何を生み出す？」、Reference原文「オフィスに"偽物のクラゲ"を置くと、
本当に癒やされる？」)。→ **素材が同じであれば、Lunaは同等の抽象化・
再解釈スタイルのHookを生成できる**(Hook生成能力自体は再現できている
可能性が高い)。

**(c) モデル差(gpt-5.6-sol)**: 条件(委任文Phase4(c): (b)のquestion_
ification判定が過半数)を満たさなかったため(0/20)、**未実施**。
`phase4_diag_c.json`に理由を記録。

**(d) reasoning effort差**(Luna、`effort=high`、1 call): (b)と同一
Prompt・入力で`high`を実行した結果、Hook形式は20/20とも
`reinterpretation`で`medium`と同一分類。個別文面はより説明的になる
傾向が見られたが、機械判定ルール上の差は無し。

### 観察事実の整理(結論はFableが行う)

| 切り分け対象 | 観察事実 |
|---|---|
| 検索backend/tool | Reference素材を直接指定すればAPI web_searchで55%発見可能(D-a) |
| 広域探索(Step A)のquery/カテゴリ設計 | 素材直接指定と比べ、広域探索での同一話題捕捉率は大幅に低い(Step A生プールでの一致は1/20) |
| Hook生成能力 | 同一素材を与えればReferenceと同形式(reinterpretation)のHookを生成できる(D-b) |
| モデル差(Luna/Sol) | 条件未達のため未検証 |
| reasoning effort | medium/highでHook形式・分類に差なし(D-d) |
| Step D検証ルール(url_in_citations) | 8サブレーン中2つのみが`url_citation`注釈を返し、40件中31件(78%)が機械除外された。structured JSON output(json_schema形式)を使う場合にAPIの`url_citation`注釈が付与されないケースが多いという技術的挙動が観察された(詳細はG節) |

---

## E. 結論

`[Fable記入]`

---

## F. コスト

| 項目 | 値 |
|---|---|
| 総額 | ¥117.4(上限¥400以内) |
| 総OpenAI呼び出し数 | 15 |
| 明示web_search付き呼び出し | 10 / 予算11(probe1+StepA8+diag_a1) |
| 内部web_search_call合計(記録のみ) | 55 |
| 全call model実値 | 全て`gpt-5.6-luna`(diag_cは未実施のためSol呼び出し無し) |
| effort | Phase0/2/4(a)(b)=medium、Phase4(d)=high |

詳細: `er016_output/topic_selection_chatgpt_repro_01/cost.json`

---

## G. 制約・逸脱

1. **時刻窓の完全再現不可**(A節・phase1_audit.md参照): 検索インデックスが
   現在時点のものであり、2026-09-23当時にChatGPT Web Searchが見ていた
   結果集合の完全再現は技術的に不可能。
2. **url_in_citations機械除外による大幅な取りこぼし**(想定外の技術的
   挙動): Step A 8サブレーン中、sublane 2・3のみが`url_citation`注釈を
   含む応答を返し(各14件・13件)、残り6サブレーン(1,4,5,6,7,8)は0件
   だった。すべての候補は実際にはHTTP到達可能(status_class="ok"が
   大半)であり、URLの捏造は確認されなかった。これは**structured JSON
   output(`text.format=json_schema`)使用時に、モデルが本文中に
   inline citation(`url_citation`アノテーション)を生成しない場合が
   多いという、Responses APIの技術的挙動**と考えられる(仮説、未確定)。
   委任文で指定された除外ルールをそのまま適用したため、Step D通過が
   40件中9件、Step E最終選定が8件に留まった。この点は委任文の想定
   (「除外ルール(機械): ...url_in_citations=false」)通りに実行した結果で
   あり、Sonnet側で独自にルールを緩和・回避することはしていない。
   将来のRun設計変更の要否はFable/ユーザー判断を仰ぐ(下記「提案」参照)。
3. **SNS/Trendアーカイブアクセス**: Phase 0プローブは17テーマを1回で
   取得でき、閾値(10件)をクリア。ただしStep D検証で、sublane 8(SNS)
   由来候補も他レーン同様`url_citation`注釈が0件となり、最終的に
   Step Eへは到達しなかった(sublane 8由来の最終選定候補は0件)。
4. **git**: 初回run実行時点ではcommit/push/addを一切実行していない
   (`git status --porcelain`確認済み、Production対象ファイル
   `er011_*.py`/`er014_*.py`/`er015_*.py`/
   `er016_topic_selection_luna_api_trial_01.py`/`routing.py`は無変更)。
   **FIX-01完了後、委任文の指示により本Trial一式(スクリプト・出力・本
   REPORT)をcommit・pushした**(コミットSHA・URLはRESULT_PACKET_TSCR.md
   FIX-01節6項参照)。

### FIX-01: Step D検証ルール不備の発生経緯(事実記載、Fableのオーケスト
レーション設計ミス)

上記2.で記載した`url_in_citations`機械除外は、Fableが委任文でStep Dの
失格条件として明記した「`url_in_citations=false`→失格」というルールを
Sonnetがそのまま実装・適用した結果として発生した。ルール自体は委任文の
指示通りに実装されており、Sonnet側の実装ミスや独自の緩和・回避は無い。
一方で、このルールが依拠する`url_citation`アノテーションは、Step Aで
使用した`text.format=json_schema`(構造化出力)とweb_searchツールを
併用する場合に、モデルが本文中へinline citationを生成しないケースが
多いという、Responses APIの技術的挙動(仮説)の影響を強く受ける。この
挙動は委任文設計時点では想定されておらず、結果としてLunaの探索・選定・
Hook生成能力とは無関係に、8サブレーン中6サブレーン(1,4,5,6,7,8)由来の
候補がStep Dでほぼ全滅し、Step E最終選定がsublane 2・3の2レーンに
偏った8件に歪められた。FableはこれをFable側のオーケストレーション
(工程設計)ミスと判断し、Step Dの当該条件のみを削除したFIX-01の実行を
Sonnetへ委任した。FIX-01ではStep A〜C(Lunaによる探索・選定・Hook生成)
は一切変更せず、Step D以降のみを訂正している。

### 設計変更提案(Sonnetからの提案、勝手に実装はしていない)

- Step Dの`url_in_citations=false`除外ルールについて、上記の技術的挙動
  (structured output時にannotationが付与されないケースがある)を踏まえ、
  次回Run以降は(a)freeform text応答+事後JSON抽出方式に変更する、
  (b)`url_in_citations`を除外条件ではなく参考フラグに格下げする、
  (c)HTTP到達性(status_class="ok")を主たる実在確認手段とする、等の
  選択肢が考えられる。どれを採用するかはFable/ユーザー判断を仰ぐ
  (Production/Trial双方の設計に関わるため、Sonnet単独では変更しない)。

---

## H. DECISION_LOG追記候補

`[Fable分類待ち]`

参考(Sonnetが把握した事実、分類はFableが行う):
- 本Trialは広域探索→選定→Hook生成の枠組みでは一定の再現性を示した
  (Hook形式・スタイルはD-b/D-dで同等、検索到達性もD-aで55%)。
- 一方、広域探索(Step A)段階での同一話題捕捉率が低く(1/20)、かつ
  Step D検証ルール(url_in_citations)の技術的挙動により最終候補が
  8件に留まった。これらは「探索・選定・Hook生成の質」そのものより、
  「広域探索のquery設計」と「実装上の検証ルール」に起因する可能性が
  高いという観察事実がある(結論・分類はFableへ)。
