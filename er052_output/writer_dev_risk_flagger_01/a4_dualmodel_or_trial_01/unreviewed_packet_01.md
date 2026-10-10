# 未評価Flag一覧(Blind packet、confidence・モデル名なし)

#### N01: U03 s18

- 記事: U03(space_weapons)
- 対象文: But these were tests fired from the ground.
- ±2文:
  - s16: “Haven’t there already been weapons that destroy satellites?” That’s right.
  - s17: Russia has destroyed satellites with ground-launched anti-satellite missiles.
  - s18(対象): But these were tests fired from the ground.
  - s19: “Firing from the ground into space” and “placing a weapon in orbit” both involve space, but they have different starting points and locations.
  - s20: The terminology needs care, too.
- Fact本文:
  - F-003: ロシアは2021年11月15日、地上発射型の直接上昇式ASATミサイルでロシアの衛星COSMOS 1408を破壊し、1,500個超の追跡可能な軌道デブリを発生させた。([spacecom.mil](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/?utm_source=openai))
  scope: 低軌道、COSMOS 1408および発生デブリ
  conditions: 米宇宙軍による公式発表
  numeric_value: >1,500個 (numeric_scope: 追跡可能な軌道デブリ)
  date_or_period: 2021年11月15日
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 地上から発射したASATミサイルによる破壊試験であり、兵器を軌道上に恒久配備した事例とは区別する。
- reason:
  - 「tests」という複数形は、台帳に記載された2021年の破壊試験1件より多い試験を示しているのではありませんか。

#### N02: U04 s21

- 記事: U04(small_bag)
- 対象文: What we see here is only the attention given by fashion media and on runways.
- ±2文:
  - s19: We cannot use the attention on mini bags as proof that micro bags in general are popular again.
  - s20: Even a glamorous story needs a note of caution.
  - s21(対象): What we see here is only the attention given by fashion media and on runways.
  - s22: It does not prove demand among all shoppers or that sales have actually risen.
  - s23: “Often seen in magazines” and “often sold at the checkout” are two different things.
- Fact本文:
  - MB-02: Who What Wearは2026年5月、Bottega VenetaのMini Andiamoについて、ニューヨークとロサンゼルスのファッション関係者に好まれていると報じ、SNS上の着用例を紹介した。同記事は同モデルが「前月」に発売されたとしている。([whowhatwear.com](https://www.whowhatwear.com/fashion/luxury/bottega-veneta-mini-andiamo-bag-trend-2026))
  scope: 同記事が取り上げた特定のバッグと、ニューヨーク／ロサンゼルスの着用例。
  conditions: ファッション媒体による編集者の観察とSNS投稿の紹介。地域全体や消費者全体の代表調査ではない。
  date_or_period: 2026年5月（記事掲載月。発売は記事によればその前月）
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 特定モデルの局所的な注目例。ミニバッグ全般の市場復調や、XLバッグからの広範な乗り換えを示す証拠として一般化しない。
- reason:
  - 「only the attention given by fashion media and on runways」という限定は、ニューヨークとロサンゼルスの着用例やSNS投稿も紹介したMB-02の範囲と食い違う可能性があるのではありませんか。

#### N03: U05 s10

- 記事: U05(byd_recall)
- 対象文: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
- ±2文:
  - s8: Often hidden behind showier features, this part started the trouble this time.
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10(対象): As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して一般的なリスクとして述べているのではありませんか。
  - 「there is a risk」と可能性を示す一方で、制動灯が点灯し続けるのは限位垫が脱落する極端な場合という条件が省かれているのではありませんか。

#### N04: U05 s11

- 記事: U05(byd_recall)
- 対象文: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
- ±2文:
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11(対象): In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
  - s13: But on the road, this is not something you can laugh off and correct.
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して、ペダルを踏んでいないときに常に点灯するように読めるのではありませんか。

#### N05: U05 s27

- 記事: U05(byd_recall)
- 対象文: BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- ±2文:
  - s25: On the road, we want cars to be good at getting the message across, not just good at talking.
  - s26: ## In one line
  - s27(対象): BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- Fact本文:
  - BYD-RECALL-06: 規制当局公告は、製造上の問題により制動ペダルの限位垫（brake pedal stopper pad／ペダルストッパーパッド）の材料にロット単位の異常が生じたと説明している。長期間使用すると、当該部品がひび割れ・破損する可能性がある。
  scope: 召回対象の唐系・秦系車両に取り付けられた制動ペダル限位垫
  conditions: 公告は材料異常を製造上の問題に帰属させ、長期間使用後の破損可能性を記載。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 対象部品は制動ペダルの限位垫。公告が説明する不具合はこの部品の材料異常・ひび割れ・破損であり、ブレーキそのものの制動不能とは記載していない。
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫の材料異常に続いてひび割れ・破損の可能性があり、脱落する「極端な場合」に制動灯が点灯し続けるとされていますが、この文はその条件を外して部品が直接点灯を引き起こすように述べているのではありませんか。
  - 「may keep the brake lights on」と述べていますが、公告が示すのは限位垫が脱落する極端な場合に限った可能性ではありませんか。

#### N06: U06 s1

- 記事: U06(streaming_price)
- 対象文: # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
- ±2文:
  - s1(対象): # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
  - s2: The news that “Disney+ is raising its prices” may have made tense background music start playing in your mental household budget.
  - s3: Before you clutch your wallet and think, “Not my subscription fees again...,” pause here.
- Fact本文:
  - F01: 2026年10月8日までに今回のWeb調査で確認できた主要な米国向け動画ストリーミング価格改定のうち、最も新しい発表としてDisney+の2026年9月23日の改定を選定した。
  scope: 米国向け動画ストリーミングサービスの価格改定発表として調査で確認した範囲
  conditions: 「最も新しい」は調査時点までにWeb検索で確認できた発表に基づく選定。
  date_or_period: 発表日：2026-09-23。調査基準日：2026-10-08
  ambiguity_note: 全世界・全地域の小規模サービスを網羅した比較ではなく、検索で確認できた主要サービスの発表からの選定。
  notes_for_writer: 対象はDisney+の当該発表に限定する。他サービスとの比較はしない。
  - F05: Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。
  scope: Disney+ Help Centerの米国向け価格ページに掲載された価格
  conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。
  date_or_period: 2026-09-23掲載の価格情報
  notes_for_writer: 確認した価格を全世界共通価格として記述しない。
- reason:
  - 「Disney+ Prices Are Going Up」は、確認対象の米国向け価格改定だけでなく全地域・全プランの値上げを示す表現ではありませんか。

#### N07: X11 s28

- 記事: X11(openai_copyright)
- 対象文: Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- ±2文:
  - s26: For now, all we know is that demands have been made that cannot be summed up as “pay and it’s over.” How much of that bill will be accepted remains to be seen.
  - s27: ## In one line
  - s28(対象): Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- Fact本文:
  - F2: 訴状に記載された原告は14の法人・事業体で、USA TODAY Co., Inc.、Gannett Satellite Information Network, LLC、Gannett GP Media, Inc.、The Courier-Journal, Inc.、Des Moines Register and Tribune Company、Detroit Free Press, Inc.、Detroit Newspaper Partnership, L.P.、CA Florida Holdings, LLC、Scripps NP Operating, LLC、CA North Carolina Holdings, Inc.、GateHouse Media Oklahoma Holdings, Inc.、Journal Sentinel Inc.、GateHouse Media Ohio Holdings II, Inc.、Phoenix Newspapers, Inc.である。訴状は、これらをUSA TODAY Co., Inc.傘下の原告らとしている。
  scope: 本件訴状に名を連ねる法人・事業体
  conditions: 訴状に記載された当事者名。各出版物そのものがすべて別個の法人原告だという意味ではない。
  numeric_value: 14 (numeric_scope: 訴状の共同原告として記載された法人・事業体数)
  date_or_period: 2026-10-08時点の訴状
  notes_for_writer: 原告数14と、訴状が対象として挙げる出版物数19を混同しない。
  - F6: 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。
  scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載
  conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。
  numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)
  date_or_period: 2026-10-08に提出された訴状
  notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- reason:
  - s28で「Fourteen news companies」とありますが、台帳F2では14の法人・事業体、F3では19出版物とされていますが、これらはすべて純粋な「news companies（報道企業）」であると断定して問題ありませんか？

