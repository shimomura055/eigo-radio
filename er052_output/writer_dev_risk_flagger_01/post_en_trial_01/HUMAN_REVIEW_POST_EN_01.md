# HUMAN_REVIEW_POST_EN_01: ユーザー確認用一覧(記事→Union Flag→該当英文/対応Fact(日本語台帳原文)/理由/Known or New)

Risk FlaggerはCheckerではない(STOPしない・PASS/FAILしない・自動Rewriteしない)。『人間が見る場所』の候補一覧。有用/不要の判断は未確定(ユーザー確認用)。STOP稿(U07/U08/X11)は完成記事ではない。Hormuz X09/Space X10/OpenAI X11はB1回復前の旧稿(既知例用に追加)。

## U01 meta(採用稿(ADOPTED。Advanced checker RESOLVED_ST)

Union 1件 / 問題単位 1件。

### U01 s18(A3 なし / A4 主体対象入替 0.35)

- 該当英文: We cannot assume from this story that any information was shared.
- 対応Fact(日本語台帳原文): **MUSE-HC-010** Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。   scope: 人間の契約スタッフがMuse経由の電話を担当するテスト   conditions: 電話の遂行にユーザー情報が必要となる場合   date_or_period: 2026年9月中旬〜2026年9月22日   causal_strength: OBSERVED_REPORTED   notes_for_writer: 懸念の存在を示す事実。実際の大規模な情報漏えいが発生したと断定しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
- 理由(A3): -
- 理由(A4): 「any information was shared」は、台帳が未確認としている「機微情報の意図しない共有」から「情報共有全般」へと範囲を広げているのではありませんか。
- New issue(提案): (旧Check指摘なし)

## U02 hormuz(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRAD)

Union 1件 / 問題単位 1件。

### U02 s18(A3 その他 0.72 / A4 その他 0.50)

- 該当英文: So Brent futures did not suddenly plunge.
- 対応Fact(日本語台帳原文): **HF-009** Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。   scope: 国際指標Brent原油先物の短時間の値動き   conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。   numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)   date_or_period: 2026-07-14、撤回発表後の取引時間中   causal_strength: CAUSAL_STATED_BY_SOURCE   notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。 / **HF-011** Brent原油先物は7月14日に1.43ドル、1.7％上昇し、1バレル84.73ドルで清算された。これは2営業日連続で6月12日以来の高い清算値だった。   scope: Brent原油先物の当日清算値と前日比   conditions: 20％償還料案は同日の取引時間中に撤回されたが、海上封鎖、米・イラン間の攻撃、タンカー被害などの供給懸念は継続していた。   numeric_value: $84.73/バレル、前日比 +$1.43、+1.7% (numeric_scope: 7月14日のBrent原油先物清算値。日中高値ではない)   date_or_period: 2026-07-14清算時点   causal_strength: OBSERVED_REPORTED   notes_for_writer: 7月14日は撤回があったにもかかわらず日次清算値は上昇した。これだけから撤回が価格を上昇させた、または下落させなかったと因果推論しない。
- 理由(A3): 「So Brent futures did not suddenly plunge」は置換発表によって急落が起きなかったという因果関係と急落の不在を示唆しますが、台帳が示すのは「一時的な上げ幅縮小とその後の回復」であり、因果関係や急落の不在までは確認できないのではありませんか
- 理由(A4): 「So Brent futures did not suddenly plunge」は、台帳の「一時的な上げ幅縮小とその後の回復」という観測を超えて、償還料案の置換が急落を防いだという未確認の因果関係を示す表現ではありませんか。
- New issue(提案): (旧Check指摘なし。U02は旧CheckでCOMPLIANT)

## U03 space_weapons(採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DO)

Union 5件 / 問題単位 2件。

### U03 s1(A3 その他 0.72 / A4 その他 0.35)

- 該当英文: # Space Weapons: Their Special Attack Is Secret, but Their “Address” Was Made Public
- 対応Fact(日本語台帳原文): **F-001** 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mil](https://www.vandenberg.spaceforce.mil/News/Article-Display/Article/4601219/secaf-announces-on-orbit-space-control-weapons/))   scope: 米空軍・米宇宙軍   conditions: 敵対的な相手の行動から統合軍を防護する用途と説明   date_or_period: 2026年9月14日発言、2026年9月15日公式掲載   causal_strength: OBSERVED_REPORTED   notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。
- 理由(A3): 見出しの「Their Special Attack Is Secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」よりも強く、特定の攻撃能力が存在し秘密扱いされていると述べる表現ではありませんか
- 理由(A4): 見出しの「Their Special Attack Is Secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きよりも強く、攻撃能力の存在とその機密扱いを断定しているのではありませんか。
- Known issue(提案): Known系統 — 能力の秘匿・不在断定系(旧Check: b1b_prev_b1 attempt1『has not explained what they can do』= changed_fact/unsupported_new_claim, translation)。ただし最終稿U03自体は旧CheckがCOMPLIANT

### U03 s5(A3 その他 0.83 / A4 その他 0.40)

- 該当英文: The details of the system’s performance remain secret, while the U.S.
- 対応Fact(日本語台帳原文): **F-001** 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mil](https://www.vandenberg.spaceforce.mil/News/Article-Display/Article/4601219/secaf-announces-on-orbit-space-control-weapons/))   scope: 米空軍・米宇宙軍   conditions: 敵対的な相手の行動から統合軍を防護する用途と説明   date_or_period: 2026年9月14日発言、2026年9月15日公式掲載   causal_strength: OBSERVED_REPORTED   notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。
- 理由(A3): 「the system’s performance remain secret」は、台帳で具体的な性能が示されていないことを、性能が秘密扱いされているという事実に置き換えているのではありませんか
- 理由(A4): 「the system’s performance remain secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」とは異なり、性能の詳細が機密扱いであると断定しているのではありませんか。
- Known issue(提案): Known系統 — 同上(能力・性能が秘密/非開示という断定)。文がU.S.の位置で分割されており途中で切れている

### U03 s13(A3 不在断定 0.70 / A4 不在断定 0.35)

- 該当英文: But no specific system names or attack capabilities have been given.
- 対応Fact(日本語台帳原文): **F-001** 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mil](https://www.vandenberg.spaceforce.mil/News/Article-Display/Article/4601219/secaf-announces-on-orbit-space-control-weapons/))   scope: 米空軍・米宇宙軍   conditions: 敵対的な相手の行動から統合軍を防護する用途と説明   date_or_period: 2026年9月14日発言、2026年9月15日公式掲載   causal_strength: OBSERVED_REPORTED   notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。
- 理由(A3): 「no specific system names or attack capabilities have been given」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」を超えて、それらが一切公表されていないと断定しているのではありませんか
- 理由(A4): 「no specific system names or attack capabilities have been given」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きを、具体名や攻撃能力の公表がないという未確認の断定に広げているのではありませんか。
- Known issue(提案): Known系統 — 同上(『no specific system names or attack capabilities have been given』)

### U03 s17(A3 数量時系列 0.76 / A4 数量時系列 0.40)

- 該当英文: Russia has destroyed satellites with ground-launched anti-satellite missiles.
- 対応Fact(日本語台帳原文): **F-003** ロシアは2021年11月15日、地上発射型の直接上昇式ASATミサイルでロシアの衛星COSMOS 1408を破壊し、1,500個超の追跡可能な軌道デブリを発生させた。([spacecom.mil](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/?utm_source=openai))   scope: 低軌道、COSMOS 1408および発生デブリ   conditions: 米宇宙軍による公式発表   numeric_value: >1,500個 (numeric_scope: 追跡可能な軌道デブリ)   date_or_period: 2021年11月15日   causal_strength: CAUSAL_STATED_BY_SOURCE   notes_for_writer: 地上から発射したASATミサイルによる破壊試験であり、兵器を軌道上に恒久配備した事例とは区別する。
- 理由(A3): 「has destroyed satellites」という複数形は、台帳に記載された「COSMOS 1408」という1基の破壊を、複数の衛星を破壊した実績へ広げているのではありませんか
- 理由(A4): 「Russia has destroyed satellites」という複数形は、台帳が記録する「COSMOS 1408」という1基の破壊を、複数の衛星を破壊した実績に広げているのではありませんか。
- Known issue(提案): Known系統 — 旧Check: space a2稿attempt1/2が『Russia has destroyed satellites』複数形を翻訳由来MAJOR(changed_number等)と指摘。b1b稿には旧Check指摘なし

### U03 s33(A3 不在断定 0.68 / A4 不在断定 0.35)

- 該当英文: The United States has publicly acknowledged deploying space-control weapons in orbit, but has not disclosed their capabilities.
- 対応Fact(日本語台帳原文): **F-001** 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mil](https://www.vandenberg.spaceforce.mil/News/Article-Display/Article/4601219/secaf-announces-on-orbit-space-control-weapons/))   scope: 米空軍・米宇宙軍   conditions: 敵対的な相手の行動から統合軍を防護する用途と説明   date_or_period: 2026年9月14日発言、2026年9月15日公式掲載   causal_strength: OBSERVED_REPORTED   notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。
- 理由(A3): 「has not disclosed their capabilities」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」より範囲が広く、防護用途の説明はあるにもかかわらず能力全般が非開示であると断定しているのではありませんか
- 理由(A4): 「has not disclosed their capabilities」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きとは異なり、能力が公表されていないと断定しているのではありませんか。
- Known issue(提案): Known系統 — 同上(『has not disclosed their capabilities』。E2E EVALが最終Adv『In one line』に残存と記録した文)

## U04 small_bag(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRAD)

Union 2件 / 問題単位 1件。

### U04 s7(A3 主体対象入替 0.45 / A4 主体対象入替 0.42)

- 該当英文: In other words, the point is not just “What can I fit inside?” but also “How does it look as part of an outfit?” Rather than a helper working behind the scenes to carry things, a mini bag is a little star that catches the eye.
- 対応Fact(日本語台帳原文): **MB-05** Who What WearのFall 2026ランウェイまとめは、Dior、Chanel、Chloéに小さなミノディエールが登場したと報じる一方、それらを実用性より芸術性の強い小型クラッチとして説明した。同まとめでは大型・ゆったりした形も複数の主要傾向として扱っている。([whowhatwear.com](https://www.whowhatwear.com/fashion/runway/fall-winter-bag-trends-2026))   scope: Who What Wearが取り上げた複数ブランドのランウェイ。   conditions: ファッション編集者によるコレクションの観察と解釈。   date_or_period: Fall 2026コレクション   causal_strength: OBSERVED_REPORTED   notes_for_writer: 小型バッグは装飾的・コレクション上のアクセントとして存在するが、日常使い向けの主流形状と同一視しない。
- 理由(A3): 「a mini bag」を荷物を運ぶ役割より装いのアクセントとして説明している点は、台帳の「実用性より芸術性の強い小型クラッチ」という特定の形状への評価を、ミニバッグ全般へ広げているのではありませんか。
- 理由(A4): 台帳の「実用性より芸術性の強い小型クラッチ」という特定のランウェイ上の形状についての説明が、本文の「a mini bag」によってミニバッグ全般の役割についての説明へ広がっているのではありませんか？
- New issue(提案): (旧Check指摘なし)

### U04 s15(A3 主体対象入替 0.30 / A4 なし)

- 該当英文: It’s a showcase of choices: go small for decoration, or carry a big bag.
- 対応Fact(日本語台帳原文): **MB-03** Vogueの2026年6月のSummer 2026バッグ特集は、ランウェイで大型化した「roomy totes」を取り上げる一方、beaded mini toteやpetite pouchなど小型バッグも掲載した。([vogue.com](https://www.vogue.com/article/spring-2026-handbag-trends))   scope: Vogueが紹介したSpring/Summer 2026のデザイナーコレクションおよび商品例。   conditions: 編集記事によるトレンド整理。掲載数は市場の販売比率や消費者需要の比率を表さない。   date_or_period: 2026年6月10日（Summer 2026）   causal_strength: OBSERVED_REPORTED   notes_for_writer: 2026年春夏を小型バッグ一色と描写しないための根拠。特集には大型・実用的な形と小型の装飾的／用途限定の形が併存する。 / **MB-05** Who What WearのFall 2026ランウェイまとめは、Dior、Chanel、Chloéに小さなミノディエールが登場したと報じる一方、それらを実用性より芸術性の強い小型クラッチとして説明した。同まとめでは大型・ゆったりした形も複数の主要傾向として扱っている。([whowhatwear.com](https://www.whowhatwear.com/fashion/runway/fall-winter-bag-trends-2026))   scope: Who What Wearが取り上げた複数ブランドのランウェイ。   conditions: ファッション編集者によるコレクションの観察と解釈。   date_or_period: Fall 2026コレクション   causal_strength: OBSERVED_REPORTED   notes_for_writer: 小型バッグは装飾的・コレクション上のアクセントとして存在するが、日常使い向けの主流形状と同一視しない。
- 理由(A3): 「go small for decoration, or carry a big bag」という用途の分け方は、台帳の特定の小型クラッチについての装飾性の説明を、小型バッグ全般は装飾用で大型バッグは荷物を運ぶためのものという区分に広げているのではありませんか。
- 理由(A4): -
- New issue(提案): (旧Check指摘なし)

## U05 byd_recall(採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DO)

Union 3件 / 問題単位 3件。

### U05 s1(A3 その他 0.35 / A4 なし)

- 該当英文: # A Car’s Red Lights Say “Braking!” Even When No One Is Pressing the Pedal—A Surprising Solo Play-by-Play
- 対応Fact(日本語台帳原文): **BYD-RECALL-07** 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。   scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合   conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。   causal_strength: CAUSAL_STATED_BY_SOURCE   notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- 理由(A3): 見出しの「Red Lights Say “Braking!” Even When No One Is Pressing the Pedal」は現に起きている現象と読めますが、台帳の「極端な場合」に「点灯し続ける可能性がある」という条件付きの説明より強い断定ではありませんか
- 理由(A4): -
- Known issue(提案): Known関連 — BYD In One Lineの条件落ち(旧Check A2稿 changed_scope)と同系統の『極端な場合』条件落ちだが、Flagされたのは見出し文。In One Line文(s27)自体は未Flag

### U05 s4(A3 なし / A4 その他 0.28)

- 該当英文: But the driver has no idea why.
- 対応Fact(日本語台帳原文): (Flaggerが対応Factを特定していない = 台帳にない主張の疑い)
- 理由(A3): -
- 理由(A4): 「the driver has no idea why」は運転者が原因を知らないとの断定ですが、運転者の認識については台帳に記載がなく、確認できない主張ではありませんか
- New issue(提案): (旧Check指摘なし。Fact無し=台帳にない主張)

### U05 s6(A3 主体対象入替 0.88 / A4 数量時系列 0.94)

- 該当英文: A recall notice in China named 183,211 cars from BYD’s Tang and Qin lines.
- 対応Fact(日本語台帳原文): **BYD-RECALL-01** 中国国家市场监督管理総局欠陥製品召回技術センターの2026年9月18日付の2件の召回公告では、唐系が142,895台、秦系が40,316台。両公告の台数を合算すると183,211台となる。   scope: 中国国内の2件の召回公告に記載された対象車両   conditions: 183,211台は、2件の公告に記載された対象台数を合算した数値。   numeric_value: 183,211台（唐系142,895台＋秦系40,316台） (numeric_scope: 2件の公告の対象車両の合計。単一の車種群の台数ではない。)   date_or_period: 公告日：2026-09-18。召回実施期間：2026-09-18～2028-09-18   notes_for_writer: 183,211台は中国の当該召回公告の対象台数として扱う。他市場の対象台数を示す数字ではない。
- 理由(A3): 「A recall notice」が183,211台を記載したという表現は、台帳の「2件の召回公告」の対象台数を合算して183,211台となるという集計範囲と食い違うのではありませんか
- 理由(A4): 「A recall notice」に183,211台が記載されたという表現は、台帳の「2件の公告の対象台数を合算した183,211台」と公告数および数値の集計範囲が食い違うのではありませんか
- New issue(提案): (旧Check指摘なし。台帳BYD-RECALL-01は『2件の公告の合算』)

## U06 streaming_price(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRAD)

Union 5件 / 問題単位 4件。

### U06 s8(A3 数量時系列 0.35 / A4 主体対象入替 0.40)

- 該当英文: The monthly ad-supported plan by itself will go from $11.99 to $12.49, a difference of $0.50.
- 対応Fact(日本語台帳原文): **F02** Disney+の広告付きスタンドアロン月額プランは、月額11.99ドルから12.49ドルに改定された。   scope: 米国のDisney+スタンドアロン月額プラン   conditions: Disney+の米国価格ページは、2026-09-23より前に契約した利用者には2026-10-21以降の請求サイクルで価格変更が適用されると記載。第三者請求経由では価格が異なる場合がある。   numeric_value: 月額11.99ドルから12.49ドル（0.50ドル増） (numeric_scope: 広告付きスタンドアロン月額プラン1種)   date_or_period: 新規契約者向け新価格：2026-09-23から。既存契約者：2026-10-21以降の請求サイクルから。   notes_for_writer: Disney+単体プランの価格。バンドル価格は含めない。 / **F05** Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。   scope: Disney+ Help Centerの米国向け価格ページに掲載された価格   conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。   date_or_period: 2026-09-23掲載の価格情報   notes_for_writer: 確認した価格を全世界共通価格として記述しない。 / **F06** Disney+の米国価格ページは、新規契約者向け価格を2026年9月23日開始とし、それ以前に契約した利用者には2026年10月21日以降の請求サイクルで価格変更が適用されるとしている。   scope: 米国向けDisney+契約者   conditions: 既存契約者への適用日は、各利用者の請求サイクルにより異なる。第三者請求パートナー経由では価格や適用条件が異なる場合がある。   numeric_value: 2026-09-23；2026-10-21以降 (numeric_scope: 新規契約価格の開始日；既存契約者の価格変更が始まる請求サイクルの基準日)   date_or_period: 新規契約者：2026-09-23から。既存契約者：2026-10-21以降の請求サイクル。   notes_for_writer: 既存契約者全員が10月21日に同時に請求されるという意味ではない。
- 理由(A3): 「will go from」は値上げが今後始まる意味に読めますが、台帳では新規契約者には2026年9月23日から新価格が適用され、既存契約者には10月21日以降の請求サイクルから適用されるという区別ではありませんか
- 理由(A4): 「will go from $11.99 to $12.49」は対象を限定せず一律の改定と読めますが、台帳では米国向け価格であり「第三者請求経由では価格が異なる場合がある」とされているのではありませんか。
- New issue(提案): (旧Check指摘なし)

### U06 s9(A3 数量時系列 0.35 / A4 主体対象入替 0.40)

- 該当英文: The monthly Premium plan by itself will go from $18.99 to $21.49, a difference of $2.50.
- 対応Fact(日本語台帳原文): **F03** Disney+ Premiumの広告なしスタンドアロン月額プランは、月額18.99ドルから21.49ドルに改定された。   scope: 米国のDisney+ Premiumスタンドアロン月額プラン   conditions: Disney+の米国価格ページは、2026-09-23より前に契約した利用者には2026-10-21以降の請求サイクルで価格変更が適用されると記載。第三者請求経由では価格が異なる場合がある。   numeric_value: 月額18.99ドルから21.49ドル（2.50ドル増、約13%増） (numeric_scope: 広告なしスタンドアロン月額プラン1種)   date_or_period: 新規契約者向け新価格：2026-09-23から。既存契約者：2026-10-21以降の請求サイクルから。   notes_for_writer: Disney+ Premiumは月額プランとして扱う。第三者請求の例外に注意。 / **F05** Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。   scope: Disney+ Help Centerの米国向け価格ページに掲載された価格   conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。   date_or_period: 2026-09-23掲載の価格情報   notes_for_writer: 確認した価格を全世界共通価格として記述しない。 / **F06** Disney+の米国価格ページは、新規契約者向け価格を2026年9月23日開始とし、それ以前に契約した利用者には2026年10月21日以降の請求サイクルで価格変更が適用されるとしている。   scope: 米国向けDisney+契約者   conditions: 既存契約者への適用日は、各利用者の請求サイクルにより異なる。第三者請求パートナー経由では価格や適用条件が異なる場合がある。   numeric_value: 2026-09-23；2026-10-21以降 (numeric_scope: 新規契約価格の開始日；既存契約者の価格変更が始まる請求サイクルの基準日)   date_or_period: 新規契約者：2026-09-23から。既存契約者：2026-10-21以降の請求サイクル。   notes_for_writer: 既存契約者全員が10月21日に同時に請求されるという意味ではない。
- 理由(A3): 「will go from」は値上げが今後始まる意味に読めますが、台帳では新規契約者には2026年9月23日から新価格が適用され、既存契約者には10月21日以降の請求サイクルから適用されるという区別ではありませんか
- 理由(A4): 「will go from $18.99 to $21.49」は対象を限定せず一律の改定と読めますが、台帳では米国向け価格であり「第三者請求経由では価格が異なる場合がある」とされているのではありませんか。
- New issue(提案): (旧Check指摘なし)

### U06 s16(A3 なし / A4 その他 0.20)

- 該当英文: So the headline about the price increase is a preview sent to everyone.
- 対応Fact(日本語台帳原文): (Flaggerが対応Factを特定していない = 台帳にない主張の疑い)
- 理由(A3): -
- 理由(A4): 「a preview sent to everyone」は比喩だけでなく全員への通知送付とも読めますが、全員に送付されたという事実は台帳では確認できないのではありませんか。
- New issue(提案): (旧Check指摘なし。Fact無し)

### U06 s17(A3 主体対象入替 0.64 / A4 数量時系列 0.55)

- 該当英文: But the day the main story begins on your bill is different for each person.
- 対応Fact(日本語台帳原文): **F06** Disney+の米国価格ページは、新規契約者向け価格を2026年9月23日開始とし、それ以前に契約した利用者には2026年10月21日以降の請求サイクルで価格変更が適用されるとしている。   scope: 米国向けDisney+契約者   conditions: 既存契約者への適用日は、各利用者の請求サイクルにより異なる。第三者請求パートナー経由では価格や適用条件が異なる場合がある。   numeric_value: 2026-09-23；2026-10-21以降 (numeric_scope: 新規契約価格の開始日；既存契約者の価格変更が始まる請求サイクルの基準日)   date_or_period: 新規契約者：2026-09-23から。既存契約者：2026-10-21以降の請求サイクル。   notes_for_writer: 既存契約者全員が10月21日に同時に請求されるという意味ではない。
- 理由(A3): 「is different for each person」は全員の適用日がそれぞれ異なるという断定に読めますが、台帳の「各利用者の請求サイクルにより異なる」は同じ日に適用される利用者もあり得るという意味ではありませんか
- 理由(A4): 「is different for each person」は全員の適用日が互いに異なると読めますが、台帳の「各利用者の請求サイクルにより異なる」は同じ日に適用される利用者もいることを排除していないのではありませんか。
- New issue(提案): (旧Check指摘なし)

### U06 s21(A3 なし / A4 その他 0.35)

- 該当英文: The price list tells you “how much.” When you look at it together with when you signed up and your billing cycle, you can see when the change starts for you.
- 対応Fact(日本語台帳原文): **F05** Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。   scope: Disney+ Help Centerの米国向け価格ページに掲載された価格   conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。   date_or_period: 2026-09-23掲載の価格情報   notes_for_writer: 確認した価格を全世界共通価格として記述しない。 / **F06** Disney+の米国価格ページは、新規契約者向け価格を2026年9月23日開始とし、それ以前に契約した利用者には2026年10月21日以降の請求サイクルで価格変更が適用されるとしている。   scope: 米国向けDisney+契約者   conditions: 既存契約者への適用日は、各利用者の請求サイクルにより異なる。第三者請求パートナー経由では価格や適用条件が異なる場合がある。   numeric_value: 2026-09-23；2026-10-21以降 (numeric_scope: 新規契約価格の開始日；既存契約者の価格変更が始まる請求サイクルの基準日)   date_or_period: 新規契約者：2026-09-23から。既存契約者：2026-10-21以降の請求サイクル。   notes_for_writer: 既存契約者全員が10月21日に同時に請求されるという意味ではない。
- 理由(A3): -
- 理由(A4): 「when you signed up and your billing cycle」で適用時期を確定できるという記述は、台帳の「第三者請求パートナー経由では価格や適用条件が異なる場合がある」という条件を落として断定しているのではありませんか。
- New issue(提案): (旧Check指摘なし。台帳F05の第三者請求条件の脱落)

## U07 openai_copyright(【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQ)

Union 4件 / 問題単位 4件。

### U07 s1(A3 なし / A4 主体対象入替 0.30)

- 該当英文: # More Than $250 Million—and a Demand to “Destroy the Models,” Too: AI Lawsuits Are About More Than Money
- 対応Fact(日本語台帳原文): **F6** 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。   scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載   conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。   numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)   date_or_period: 2026-10-08に提出された訴状   notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- 理由(A3): -
- 理由(A4): 見出しの「AI Lawsuits Are About More Than Money」は、台帳の「本件訴状で求められた救済」をAI訴訟一般へ広げた表現ではありませんか。
- Known issue(提案): Known — 旧Check: 見出し『AI Lawsuits Are About More Than Money』のscope拡張(changed_scope, origin=ja_source, F6)= U07がSTOPした直接原因。A3は未Flag、A4のみ

### U07 s5(A3 主体対象入替 0.62 / A4 主体対象入替 0.65)

- 該当英文: Their list of demands also includes the “destruction” of models such as GPT.
- 対応Fact(日本語台帳原文): **F6** 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。   scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載   conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。   numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)   date_or_period: 2026-10-08に提出された訴状   notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- 理由(A3): 「models such as GPT」は、台帳の「原告らのコンテンツを組み込んだGPTその他の大規模言語モデル」という限定を欠き、破棄請求の対象をGPTなどのモデル全般へ広げて読める表現ではありませんか。
- 理由(A4): 「destruction of models such as GPT」は、台帳の「原告らのコンテンツを組み込んだ」という対象限定がなく、GPTなどのモデル全般の破棄を求めていると読める表現ではありませんか。
- New issue(提案): (旧Check指摘なし)

### U07 s21(A3 なし / A4 不在断定 0.30)

- 該当英文: At the time of Reuters’ report, OpenAI had not yet responded to a request for comment.
- 対応Fact(日本語台帳原文): **F7** Reutersは2026-10-08の報道で、OpenAIの広報担当者は訴状についてのコメント依頼に直ちには応じなかったと報じた。これは報道時点での取材状況であり、OpenAIによる訴状への実体的な回答や法廷上の答弁を示すものではない。   scope: Reutersが報じたコメント依頼への応答状況   conditions: 「直ちには応じなかった」という報道時点の記述。以後の対応の有無はこのFactでは扱わない。   date_or_period: 2026-10-08（Reuters報道時点）   notes_for_writer: 本件に関するOpenAIの実体的な反論が確認された、と書かない。
- 理由(A3): -
- 理由(A4): 「had not yet responded」は、台帳の「直ちには応じなかった」より強く、Reutersの報道時点まで応答が一切なかったと断定する表現ではありませんか。
- New issue(提案): (旧Check指摘なし)

### U07 s22(A3 なし / A4 その他 0.20)

- 該当英文: In AI news, performance and convenience often take center stage.
- 対応Fact(日本語台帳原文): (Flaggerが対応Factを特定していない = 台帳にない主張の疑い)
- 理由(A3): -
- 理由(A4): 「performance and convenience often take center stage」というAI報道全般の傾向は、台帳のどのFactにも対応する根拠がなく、別途確認が必要な主張ではありませんか。
- New issue(提案): (旧Check指摘なし。Fact無し)

## U08 semiconductor_earnings(【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQ)

Union 1件 / 問題単位 1件。

### U08 s25(A3 不在断定 0.68 / A4 不在断定 0.35)

- 該当英文: But even if the company’s forecast appears beside that line, we cannot say, “AI demand is strong, so revenue will be about $34.8 billion.” This announcement alone does not explain how the two are connected.
- 対応Fact(日本語台帳原文): **F4** Broadcomは次の四半期の連結売上高を約348億ドルと見込んだ。同社は前年比93％増に相当すると説明した。   scope: Broadcom Inc.全体の次四半期連結売上高   conditions: 2026年9月2日時点の会社見通し。会社は見通しを推定値とし、実績は異なり、差が重要となる可能性があると記載。   numeric_value: 約348億ドル。前年同期比+93％。 (numeric_scope: 2026年度第4四半期の連結売上高見通しと前年同期比)   date_or_period: 2026年度第4四半期（2026年11月1日終了予定）   notes_for_writer: 会社の見通しとして記載し、確定した実績値として扱わない。 / **F6** BroadcomのCEOは、カスタムAIアクセラレーターとネットワーキングへの需要が引き続き非常に強いと述べた。   scope: 同社のカスタムAIアクセラレーターおよびネットワーキングに対する需要についてのCEOの説明   conditions: 経営陣による定性的な評価。   date_or_period: 2026年9月2日発表の2026年度第3四半期決算リリース   causal_strength: OBSERVED_REPORTED   notes_for_writer: 会社CEOの評価として帰属を明記し、独立に確認された市場全体の需要事実として一般化しない。
- 理由(A3): 文中の「This announcement alone does not explain how the two are connected」は、台帳の「連結売上高見通し」と「CEOによる需要評価」からは確認できない、発表内に両者の関連説明がないという断定ではありませんか。
- 理由(A4): 「This announcement alone does not explain how the two are connected」という説明の不在の断定は、台帳の「連結売上高見通し」と「需要についてのCEOの説明」だけでは、決算発表全体に両者の関係の説明がないことまで確認できないのではありませんか。
- Known issue(提案): Known(境界例) — 旧Check: unsupported_new_claim(F6)。ユーザー判断は『ベストではないが問題視するほどではない』= 過剰Flagを見る境界例

## X09 hormuz(【追加・既知例用】B1回復前の英語稿(ja_source MAJORでSTOPし)

Union 2件 / 問題単位 2件。

### X09 s8(A3 主体対象入替 0.65 / A4 主体対象入替 0.83)

- 該当英文: Trump’s “20% plan.” It called for a 20% payment on all cargo passing through the Strait of Hormuz, as reimbursement for the cost of ensuring U.S.
- 対応Fact(日本語台帳原文): **HF-002** ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。   scope: ホルムズ海峡を通じて輸送される「すべての貨物」   conditions: 米国が海峡の安全と警備を提供するための費用の償還として提示。投稿は手続きと体制づくりを直ちに開始するとした。   numeric_value: 20% (numeric_scope: 投稿上の償還率。課税標準または算定基礎は明記されていない。)   date_or_period: 2026-07-13 10:16 EDT   notes_for_writer: 7月13日の提案が先で、7月14日の撤回・置換が後。7月14日の出来事を7月13日の価格上昇の原因として扱わない。
- 理由(A3): 「the cost of ensuring U.S.」は米国自体の安全確保に要する費用とも読めますが、台帳の「米国がホルムズ海峡の安全と警備を提供するための費用」とは安全確保の対象が異なるのではありませんか
- 理由(A4): 「the cost of ensuring U.S.」は米国自体の安全確保の費用と読めますが、台帳の「米国がホルムズ海峡の安全と警備を提供するための費用」とは安全確保の対象が異なるのではありませんか。
- New issue(提案): (旧Check指摘なし。『U.S.』で文が分割され『ensuring U.S.』で切れた分割アーティファクトの可能性)

### X09 s10(A3 なし / A4 その他 0.28)

- 該当英文: The size of the figure and the broad scope of the plan were enough to grab the headlines.
- 対応Fact(日本語台帳原文): (Flaggerが対応Factを特定していない = 台帳にない主張の疑い)
- 理由(A3): -
- 理由(A4): 「The size of the figure and the broad scope」が「grab the headlines」の理由だったという説明は、台帳に対応する記述がなく、確認できない因果関係を加えているのではありませんか。
- New issue(提案): (旧Check指摘なし。Fact無し)

## X10 space_weapons(【追加・既知例用】B1回復前の英語稿(attempt2でdev-check CO)

Union 1件 / 問題単位 1件。

### X10 s5(A3 なし / A4 その他 0.30)

- 該当英文: The main subject here is not a weapon that can blow up Earth, but the line around what counts as a “space weapon.” This is news where the label matters more than flashy sound effects.
- 対応Fact(日本語台帳原文): **F-001** 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。([vandenberg.spaceforce.mil](https://www.vandenberg.spaceforce.mil/News/Article-Display/Article/4601219/secaf-announces-on-orbit-space-control-weapons/))   scope: 米空軍・米宇宙軍   conditions: 敵対的な相手の行動から統合軍を防護する用途と説明   date_or_period: 2026年9月14日発言、2026年9月15日公式掲載   causal_strength: OBSERVED_REPORTED   notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。具体的なシステム名・攻撃能力・標的は推測で補わない。
- 理由(A3): -
- 理由(A4): 「not a weapon that can blow up Earth」は兵器の能力を否定する断定にも読めますが、台帳では具体的な攻撃能力は示されず「攻撃能力を推測で補わない」とされており、台帳で確認できる範囲を超えているのではありませんか。
- Known issue(提案): Known — 旧Check: space a2_prev_b1 Standard attempt1『The main subject is not a weapon that can blow up Earth.』(unsupported_new_claim, ja_source)と同一文。A3は未Flag、A4のみ

## X11 openai_copyright(【追加・最重要既知例用・STOP稿】B1回復前に翻訳後Hard STOP Che)

Union 4件 / 問題単位 3件。

### X11 s4(A3 主体対象入替 0.42 / A4 主体対象入替 0.36)

- 該当英文: The plaintiffs are also asking for models such as GPT that they say contain problematic content, as well as training sets, to be destroyed.
- 対応Fact(日本語台帳原文): **F6** 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。   scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載   conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。   numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)   date_or_period: 2026-10-08に提出された訴状   notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- 理由(A3): 「contain problematic content」は、台帳の「原告らのコンテンツを組み込んだ」と異なり、破棄請求の対象を原告らのコンテンツ以外にも広げて読める表現ではありませんか。
- 理由(A4): 「contain problematic content」は、台帳の「原告らのコンテンツを組み込んだ」という破棄請求の対象を、原告らのコンテンツに限らない「問題のあるコンテンツ」を含むモデルへ広げて読める表現ではありませんか。
- New issue(提案): (旧Check指摘なし)

### X11 s7(A3 主体対象入替 0.96 / A4 主体対象入替 0.94)

- 該当英文: They also say the models’ output copied or put articles together in new ways, and removed copyright management information.
- 対応Fact(日本語台帳原文): **F4** 訴状は、OpenAIが原告側の報道コンテンツを許可なく取得・複製してAIモデルの訓練に使用し、モデル出力でそのコンテンツを複製または再構成したと主張する。また、OpenAIが著作権管理情報を除去したとも主張する。いずれも原告側の主張であり、本件で確定した事実ではない。   scope: 原告らの報道コンテンツ、AIモデルの訓練データおよびモデル出力   conditions: 著作権侵害や著作権管理情報の除去は、訴状上の主張として扱う。   numeric_value: 数十万件の報道記事その他の資料（訴状の表現） (numeric_scope: OpenAIが訓練に使ったと原告が主張する対象コンテンツの規模。裁判所が確認した件数ではない。)   date_or_period: 訴状が対象とする期間。具体的な開始・終了日は本Factでは特定しない。   notes_for_writer: 「OpenAIが無断使用した」ではなく「原告らは、OpenAIが無断使用したと主張」とする。
- 理由(A3): 「the models’ output ... removed copyright management information」は、台帳で除去の主体とされている「OpenAI」を「モデル出力」に置き換えているのではありませんか。
- 理由(A4): 「the models’ output ... removed copyright management information」は、台帳では著作権管理情報を除去したと主張されている主体が「OpenAI」であるのに、その主体を「モデル出力」に入れ替えた記述ではありませんか。
- Known issue(提案): Known — 旧Check: changed_actor(MAJOR, ja_source, F4)『They also say the models' output … removed copyright management information.』= OpenAI actor drift

### X11 s17(A3 主体対象入替 0.35 / A4 なし)

- 該当英文: It is like seeing the total on a bill and being shocked, then turning to the next page and finding an item called “how to handle models and data.” “Please pay for using the articles” and “Please also destroy what we claim you made using those articles” are different demands.
- 対応Fact(日本語台帳原文): **F6** 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。   scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載   conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。   numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)   date_or_period: 2026-10-08に提出された訴状   notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- 理由(A3): 「what we claim you made using those articles」は、台帳の「原告らのコンテンツを組み込んだモデルおよび訓練セット」よりも広く、記事を利用して作ったもの全般を破棄請求の対象にしているように読めるのではありませんか。
- 理由(A4): -
- New issue(提案): (旧Check指摘なし)

### X11 s25(A3 不在断定 0.35 / A4 なし)

- 該当英文: At the time of Reuters’ report, OpenAI had not commented right away.
- 対応Fact(日本語台帳原文): **F7** Reutersは2026-10-08の報道で、OpenAIの広報担当者は訴状についてのコメント依頼に直ちには応じなかったと報じた。これは報道時点での取材状況であり、OpenAIによる訴状への実体的な回答や法廷上の答弁を示すものではない。   scope: Reutersが報じたコメント依頼への応答状況   conditions: 「直ちには応じなかった」という報道時点の記述。以後の対応の有無はこのFactでは扱わない。   date_or_period: 2026-10-08（Reuters報道時点）   notes_for_writer: 本件に関するOpenAIの実体的な反論が確認された、と書かない。
- 理由(A3): 「OpenAI had not commented right away」は、台帳の「広報担当者がコメント依頼に直ちには応じなかった」という取材状況を、OpenAIによるコメント全般の不在に広げているのではありませんか。
- 理由(A4): -
- New issue(提案): (旧Check指摘なし)

