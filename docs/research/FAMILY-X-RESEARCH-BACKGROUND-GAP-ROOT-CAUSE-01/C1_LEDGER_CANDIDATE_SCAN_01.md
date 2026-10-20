# C1_LEDGER_CANDIDATE_SCAN_01(既存Ledgerからの陽性対照候補探索。FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02、API 0)

- 走査対象: `er019_output/**/research_ledger/verified_fact_ledger.txt` 全件(重複除外後に**8種類のLedger**。同一Ledgerを使う複数runは同一視。`sha`はLedger本文)。
- 照合したB3実績: 各run `storyline_b3/fact_selection_evidence.json` の `selected_fact_ids`・`selected_storyline`・`fact_tests[].reason`(B3自身が不採用理由で「背景」と認識していたか)。読取のみ。
- 走査手順: 本書末尾の機械生成リスト(Fact ID・状態・先頭32字・採用印)を作成後、下の**事前固定の定義**で判定。

## 1 事前固定の判定基準(走査前に固定)

**背景Factの定義**: 中心事象(採用Storyline)の「誰が/なぜ/何の前提で」を与え、無いと初見の読者が中心事象の意味を**誤解または理解不能**になるFact。対義=周辺数値・補足統計・追加事例・「あると詳しくなる」情報。
**ユーザー4条件**(§3): ①主要ストーリーの理解に必要な背景Factが実在 ②そのFactがLedger内に記録 ③通常のB3ではそのFactが選ばれない可能性 ④追加すべきFactを事後評価で明確に判定できる(期待ID集合を事前に固定できる)。
**判定の手順**: ①は「Storyline文だけを読む読者」を想定し、Storyline文が前提を既に内包している(例: 電話機能の説明が文中にある)場合は×/△(欠落が成立しない)とする。③は同一Ledgerの複数run・B3の不採用reasonで確認する。
○=充足、△=限定付き、×=不充足、−=判定対象外。

## 2 候補表(Ledger×4条件)

| Ledger | 採用ID(B3実績) | ① 必要な背景Factが実在 | ② Ledger内に記録 | ③ 通常B3で選ばれない | ④ 事後判定が明確 | 判定 |
|---|---|---|---|---|---|---|
| L1 boredom_aggression(bape_01) | F05,F06 | △ F01(論文の出所)・F04(退屈の操作法)は補助的。StorylineがStudy 7/8の条件・効果を自己完結で述べており「理解不能」にはならない | ○ | ○ B3が明示除外(F01=「論文全体の構成は背景情報で不要」、F04=「別の実験的証拠」、F08=曖昧Factのため不採用) | × 必要性が主観的で期待集合を固定できない | 不適格(参考) |
| L2 coffee_prices(fxpw_01) | F02,F07,F09,F11 | × 採用Factが原因・価格・関税を自己完結で含む | ○ | − | − | 陰性対照候補 |
| L3 coffee_prices(l3_01他3run、同一Ledger) | COFFEE-003,009,010,014,015 | × 採用5件が高騰の原因(010)・下落(009)・転嫁の遅れ(014)・CPI(015)を含み自己完結 | ○ | −(追加が不要な場面) | ○ 期待追加=0と固定できる。未採用に背景風Fact(005/006/007/011/012/013)が多数あり過剰補完を誘う | **陰性対照NC1に採用** |
| **L4 hormuz(diversity_trial_01他、同一Ledger 8run)** | HF-002,HF-007,HF-009(8 run全て同一) | ○ HF-006(7/13にBrentが9.59%上昇、翌日開始予定の米国の対イラン海上封鎖とホルムズ経由のエネルギー輸送への懸念に関連付け)。Storylineの「撤回後Brentは一時上げ幅を縮めただけで高値に戻った」の『高値』『上げ幅』の前提を与え、無いと上昇を通航料提案の効果と誤解しうる | ○ | ○ 8 runで一度も採用されず、B3が「7月13日の大幅上昇とその背景は市場環境の補足」と明示除外 | ○ 期待core=HF-006、期待外=数値系(HF-004/005/010/011)・HF-012(WTI) | **陽性対照PC1に採用**(限界は§4) |
| L5 small_bag(diversity_trial_01) | F004,F006,F007 | × 英語Fact中心で、未採用は対立事例・統計。理解に不可欠な前提なし | ○ | ○ | × | 不適格 |
| L6 meta/Muse(b3_production_wiring_01他、同一Ledger) | MUSE-HC-006,010,012 | △ MUSE-HC-001(Museの発表)・004(電話機能の内容)・013(テスト目的)は製品背景。ただしStoryline文が「AIエージェント「Muse」の電話機能で一部の通話を人間契約スタッフに担わせる実験」と前提を内包し、欠落が成立しない | ○ | ○ B3が明示除外(HC-001=背景説明、HC-004=背景として有用だが006で足りる、HC-013=会社側の補足的見解) | △ | 補欠(陽性にしない) |
| L7 middle_east_yemen_saudi(run_mey_01=前Trial er083の7 callのLedger) | F04,F11(sample間でF05↔F04) | × **背景Fact自体がLedgerに無い**(攻撃主体の帰属・動機・流れの直接記述が11件中0件。前Trial TRIAL_DESIGN_01 §1) | × | − | − | **このLedgerのままでは陽性対照にならない**(前Trialで追加0件は能力の証拠にならない。W3で実在Fact追加→PC2) |
| L8 semiconductor_earnings(devconfirm_01) | F1,F2,F3,F4,F6 | × 未採用はF5(次四半期見通しの詳細)のみで背景Factではない。企業・期間はF1で採用済み | ○ | − | − | 不適格(未採用1件で過剰補完の誘因も弱い) |

## 3 結論
- **適格な既存Ledgerは1件(L4 hormuz)**。ユーザー4条件を全て満たす(限界あり、§4)。
- 委任文の規則「適格な既存Ledgerが無い、または1件しか無い場合に構成を追加」に従い、`middle_east_yemen_saudi`のLedgerを基礎に**実在する一次資料のFactを追加したテスト用Ledger**(PC2)を構成した(`er083_output/c1_positive_control_01/test_ledgers/test_ledger_mey_positive_01.{txt,json}`、構成記録=`C1_POSITIVE_CONTROL_DESIGN_01.md` §3)。
- 陰性対照はL3(coffee)。採用IDが既に自己完結で、追加が起きれば過剰補完と事後判定できる。
- 前Trial(er083)の7 callのLedger(L7)は**背景Factが無い**ため陽性対照にならない(追加0件は「必要なときに追加する能力」の証拠にも反証にもならない)。

## 4 限界・注意
- L4: テーマ文が「撤回と市場反応」で、HF-006(背景)がテーマの周辺に位置する。期待core(HF-006)を追加するかは判断の幅がある(Writerが焦点を失わず追加できるかが試験点)。HF Factの元出典URLは当該run dirに保存されていない(`verified_fact_ledger.txt`のみ)。既存Ledgerを無改変で使うため新規出典確認は行わない。
- 同一テーマ内の判定の主観性を減らすため、期待core/期待外は実走前に`c1_posctrl_matrix_01.json`で固定した。
- **委任_01への参照(重要)**: L7(中東)のF01の出典(国連DPPA発表、同一URL)とF11の出典(OSESGY特使声明 2026-10-11、同一URL)の原文は、いずれもサウジ施設への攻撃主体を「Ansar Allah」と明記している(F11出典は『continuing attacks against civilian infrastructure in the Kingdom of Saudi Arabia **by Ansar Allah**, including the latest attack on 10 October against King Khalid International Airport in Riyadh』と、Ledgerが採用した10月10日リヤド空港攻撃の文中)。一方、Ledgerの F01・F11 は主体名を含まない。前Trialが『Ledger欠落(補完不能)』とした「誰が」は、**一次資料には存在し、Research/Ledger化の段階で欠落した**。原因の特定は委任_01の範囲(本委任は事実と取得記録のみ提供。取得記録=`test_ledger_mey_positive_01.json` の sources S1〜S4)。

## 5 機械生成リスト(全Ledger、* =採用、状態 V=VERIFIED / A=AMBIGUOUS、先頭32字)

### L1 boredom_aggression
- 採用ID(B3実績): F05, F06
- Storyline: 2021年の二つの無作為割付実験では、短時間の退屈による他者の報酬減額の増加は、増額も選べる課題では特性サディズムが高い参加者でのみ認められ、増額できない別の課題では特性の高低にかかわらず認められた。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   F01 [V] 査読付き論文「On the Relation of Boredo
  -   F02 [V] 同論文のStudies 1A–1Fは、日常生活での退屈傾向とサデ
  -   F03 [V] 同論文のStudies 2–5は、オンライン・トローリング、米軍
  -   F04 [V] Study 6では、ドイツの大学実験室で参加者を退屈条件または対
  - * F05 [V] Study 7では、参加者が動画を見ている間、別の参加者の報酬を
  - * F06 [V] Study 8では、別の参加者の報酬を減らす選択肢のみを設けた実
  -   F07 [V] Study 9は事前登録されたオンライン実験で、退屈条件と対照条
  -   F08 [A] Studies 6–9の実験で著者らが用いた退屈操作は短期的なも
  -   F09 [V] 2022年の中国の大学生研究では、閉鎖的管理下の参加者719人に
  -   F10 [V] 2022年の中国の大学生研究では、単純相関分析で状態退屈と攻撃行
  -   F11 [V] 2004年の大学生研究では、大学生ボランティア224人が退屈傾向

### L2 coffee_prices(fxpw_01)
- 採用ID(B3実績): F02, F07, F09, F11
- Storyline: 天候による供給懸念とアラビカ相場の記録的高騰を背景に、2025年の米国では挽いたコーヒーが値上がりし、小売価格上昇の大部分は夏の関税以前からの供給不足と生豆高によるものと報じられた。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   F01 [V] 2024年11月29日、ICEのアラビカ先物は一時3.3545米
  - * F02 [V] 2025年2月、ニューヨークのアラビカ先物は1ポンド当たり4.3
  -   F03 [V] ICOの総合指標価格（I-CIP）は2026年9月に平均262.
  -   F04 [V] 2026年9月のICOグループ別月平均価格は、ブラジリアン・ナチ
  -   F05 [V] ICOは、2026年9月の価格下落要因として、ブラジルの収穫によ
  -   F06 [V] ICOは、2021/22～2024/25年度の4年度のうち3年度
  - * F07 [A] 2024年のブラジルの干ばつは次期作の回復見通しを弱め、ブラジル
  -   F08 [V] 2025年12月のICO報告によると、ブラジル・レアルの対米ドル
  - * F09 [V] Reutersは、2025年夏に米国がコーヒー生産国を含む輸入品
  -   F10 [V] Reutersは、2025年11月に米国がコーヒーなど一部輸入品
  - * F11 [V] 米国の平均的な挽いたコーヒー1ポンドの価格は、2025年9月に9
  -   F12 [A] BLSの米国CPIでは、コーヒー価格指数は2025年9月に前年同
  -   F13 [V] BLSによると、米国都市平均のコーヒーCPIは2026年9月に前
  -   F14 [V] APが紹介したToastのデータでは、米国の飲食店におけるレギュ
  -   F15 [V] 米国のカフェMomentum Coffeeの共同経営者は、202
  -   F16 [A] 【予測】USDAは2026/27年度の世界コーヒー生産を過去最高
  -   F17 [A] 【予測】USDAは、2026/27年度の世界生産増をブラジル、エ

### L3 coffee_prices(l3_01/stdregen/v5_ms_01、同一Ledger sha a2146bc5)
- 採用ID(B3実績): COFFEE-003, COFFEE-009, COFFEE-010, COFFEE-014, COFFEE-015
- Storyline: 2025年初めの悪天候や供給制約などで高騰したコーヒー相場は2026年に下落したものの、生豆価格の小売への転嫁には時間差があるとの見積もりがあり、米国のコーヒーCPIは2026年8月にも前年を上回っていた。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   COFFEE-001 [V] ICO Composite Indicator Price（I-
  -   COFFEE-002 [V] 2026年9月のICOグループ指標平均は、コロンビア・マイルド3
  - * COFFEE-003 [V] ICEのアラビカ先物は2025年1月29日に一時369.45米セ
  -   COFFEE-004 [A] Reutersによると、2025年1月時点でブラジルの当該アラビ
  -   COFFEE-005 [V] USDAは、ブラジルの2020/21～2024/25年度にアラビ
  -   COFFEE-006 [V] USDAはブラジルでアラビカ生産が5年間低調だった背景として、干
  -   COFFEE-007 [V] USDAの2026/27年度見通しでは、ブラジルのコーヒー生産は
  -   COFFEE-008 [V] USDAは2026/27年度の世界コーヒー生産を過去最高の1億8
  - * COFFEE-009 [V] USDAはICOの月次複合価格指数を指標として、コーヒー価格が2
  - * COFFEE-010 [V] USDAのブラジル現地報告は、2025年初頭の高価格について、ブ
  -   COFFEE-011 [V] ICOの2026年1月報告は、ブラジルレアルが米ドルに対して上昇
  -   COFFEE-012 [V] USDAのブラジル現地報告によると、米国は2025年4月にブラジ
  -   COFFEE-013 [V] Reutersは、2025年11月21日に米国がブラジル産農産物
  - * COFFEE-014 [V] Reutersが2025年12月に取材した市場関係者・専門家は、
  - * COFFEE-015 [V] BLSの2026年8月CPIでは、米国の「Coffee」項目の指
  -   COFFEE-016 [V] APが報じたBLS政府統計によると、米国の挽いたコーヒー1ポンド
  -   COFFEE-017 [V] APによると、Toastの決済データでは、米国の通常のホットコー
  -   COFFEE-018 [V] APが2025年10月に取材したシカゴのカフェ運営者は、4店舗で
  -   COFFEE-019 [V] Reutersは2025年12月時点の米国小売コーヒー価格につい

### L4 hormuz(diversity_trial_01 他8 run、同一Ledger sha 83b2a09b)
- 採用ID(B3実績): HF-002, HF-007, HF-009
- Storyline: トランプ氏は7月13日に提案したホルムズ海峡貨物への20％償還料を、中東指導者との協議を受けて翌日、湾岸諸国の対米貿易・投資案件に置き換えたが、撤回後のBrent原油先物は一時上げ幅を縮めただけで高値に戻った。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   HF-001 [V] 国際海事機関（IMO）理事会は、第137回会合で、ホルムズ海峡の
  - * HF-002 [V] ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏
  -   HF-003 [V] 7月13日の20％償還料の投稿および同日の発言では、徴収主体、支
  -   HF-004 [V] 20％を貨物価値に適用すると仮定した試算では、約200万バレルを
  -   HF-005 [V] Financial TimesのBrent先物ヒストリカル表は、
  -   HF-006 [V] Brent原油先物は7月13日に7.29ドル、9.59％上昇し、
  - * HF-007 [V] トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％
  -   HF-008 [V] トランプ大統領は7月14日、記者団に対し、ホルムズ海峡を通航する
  - * HF-009 [V] Yahoo Financeは、7月14日の撤回・投資案件への置換
  -   HF-010 [V] Financial TimesのBrent先物ヒストリカル表は、
  -   HF-011 [V] Brent原油先物は7月14日に1.43ドル、1.7％上昇し、1
  -   HF-012 [V] Reutersは7月14日、トランプ氏が海峡をイラン以外の船舶に

### L5 small_bag(diversity_trial_01、sha 3e7aade8)
- 採用ID(B3実績): F004, F006, F007
- Storyline: 2026年のファッション報道・ランウェイではミニバッグが再び目立っているが、実用的大型バッグに取って代わる復権ではなく、収納力よりも装いの視覚的インパクトや場面性を担う小型アイテムとして大容量バッグと併存している。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   F001 [V] Vogue reported that most handbag
  -   F002 [V] Vogue's Spring/Summer 2025 handb
  -   F003 [V] Vogue documented the simultaneou
  - * F004 [V] Vogue's Summer 2026 handbag cove
  -   F005 [V] For Fall 2026, Vogue highlighted
  - * F006 [V] ELLE presented mini bags as a ma
  - * F007 [V] ELLE linked the appeal of very s
  -   F008 [V] A January 2026 Vogue feature on 
  -   F009 [V] Marie Claire's Fall 2026 trend r
  -   F010 [V] Harper's Bazaar's Fall/Winter 20
  -   F011 [V] ELLE reported that Moda Operandi
  -   F012 [V] The same ELLE report said petite
  -   F013 [V] Trendalytics reported that overs
  -   F015 [V] Who What Wear reported that Fash
  -   F016 [V] Vogue's Spring 2026 celebrity-ba
  -   F017 [V] Vogue documented a small group o
  -   F018 [V] Marie Claire reported that Coach

### L6 meta/Muse(b3_production_wiring_01 他、sha 6e271bb2)
- 採用ID(B3実績): MUSE-HC-006, MUSE-HC-010, MUSE-HC-012
- Storyline: MetaはAIエージェント「Muse」の電話機能で一部の通話を訓練済みの人間契約スタッフに担わせる実験を行ったが、ユーザー情報がスタッフに共有され得る懸念や適切な開示の不足を受けてミスと認め、機能を当面ロールバックした。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   MUSE-HC-001 [V] Metaは2026年9月8日、個人向けAIエージェント「Muse
  -   MUSE-HC-002 [V] Metaの説明では、Museは専用のクラウド仮想マシン「Muse
  -   MUSE-HC-003 [V] Metaの公式説明では、Muse Secure VMではユーザー
  -   MUSE-HC-004 [V] Museの電話機能では、ユーザーが米国内の企業・店舗へ電話をかけ
  -   MUSE-HC-005 [V] MetaはMuseの電話発信機能を、2026年8月から従業員にテ
  - * MUSE-HC-006 [V] MetaはMuse経由の電話の一部について、AIではなく訓練を受
  -   MUSE-HC-007 [V] 人間コンシェルジュ機能は、2026年9月22日のReuters報
  -   MUSE-HC-008 [V] Metaの社内投稿では、人間が電話を担当した一部テストで、成功率
  -   MUSE-HC-009 [V] 社内投稿では、MuseがAIだと認識した相手側から電話を切られる
  - * MUSE-HC-010 [V] Meta従業員は、人間の契約スタッフが電話を担当すると、電話中に
  -   MUSE-HC-011 [V] Museにインターネット・ケーブル料金の交渉を依頼した従業員は、
  - * MUSE-HC-012 [V] MetaのSuperintelligence Labs部門の副社
  -   MUSE-HC-013 [V] Metaの広報担当者Daniel Robertsは、従業員の反応
  -   MUSE-HC-014 [V] Metaは、電話機能について、商業者との改善を続け、準備が整い、
  -   MUSE-HC-015 [V] Metaは公式説明で、Museについて、ユーザーが接続アプリとア

### L7 middle_east_yemen_saudi(run_mey_01、sha 0b3005d6、前Trial er083の7 call)
- 採用ID(B3実績): F04, F11
- Storyline: サウジの民間インフラへの攻撃が続き、10月10日のリヤド空港攻撃では多数が死傷し、国連イエメン担当特使は継続攻撃が地域の安全保障を脅かし、イエメンの和平努力を難しくすると警告した。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  -   F01 [V] 2026年10月9日、国連イエメン担当特使ハンス・グルンドベルグ
  -   F02 [V] サウジアラビア民間航空総局（GACA）は、10月6日・7日にアブ
  -   F03 [V] GACAは、2026年10月8日にリヤドのキング・ハーリド国際空
  - * F04 [V] GACAは、10月10日のキング・ハーリド国際空港への攻撃につい
  -   F05 [V] GACAは、10月11日午後にリヤドのキング・ハーリド国際空港が
  -   F06 [V] イエメンで活動する連合軍の報道官は、10月11日、キング・ハーリ
  -   F07 [V] GACAは、10月11日夜に東部州ダンマームのキング・ファハド国
  -   F08 [V] サウジ・エネルギー省の関係者は、10月13日夜、東部州ダーランに
  -   F09 [V] イエメン政府系SABA通信は、マリブ県メディア局の報告として、1
  -   F10 [V] アデン首都治安局は、10月16日にフーシ派が発射したミサイル2発
  - * F11 [V] 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続

### L8 semiconductor_earnings(devconfirm_01、sha f45eb25b)
- 採用ID(B3実績): F1, F2, F3, F4, F6
- Storyline: Broadcomの2026年度第3四半期決算では連結売上高が295億9,100万ドル、AI半導体売上高が167億ドルとなり、CEOはAI関連需要が非常に強いと述べ、次四半期の連結売上高を約348億ドルと見込んだ。ただし、この発表が「最も最近」かはLedger上確定できない。
- Fact一覧(*=採用 / 状態 V=VERIFIED A=AMBIGUOUS / 先頭32字):
  - * F1 [A] 対象企業はBroadcom Inc.。同社は2026年9月2日、
  - * F2 [V] Broadcomの第3四半期の純売上高は295億9,100万ドル
  - * F3 [V] Broadcomの第3四半期のAI半導体売上高は167億ドル。C
  - * F4 [V] Broadcomは次の四半期の連結売上高を約348億ドルと見込ん
  -   F5 [V] BroadcomのCEOは、次の四半期のAI半導体売上高を217
  - * F6 [V] BroadcomのCEOは、カスタムAIアクセラレーターとネット
