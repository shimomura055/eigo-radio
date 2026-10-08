# RESULTS_M123: OPEN-243 M1〜M3 Trial 既存データ検証の結果(委任_03、2026-10-08)

Status: MEASURED(各 n=1 サンプル、Stage 2/EN検査とも非決定的。Production変更なし)。判定(採否)はFable・ユーザー。以下は事実のみ。
費用: 実費 ¥56.849(トークン実測 x 登録済み単価 gpt-6-luna、USD/JPY=160。内訳 V1 ¥13.261[生成+検査]、V2 ¥28.380[新 ¥16.092+旧再実行 ¥12.288]、V3 ¥15.209[再分類+Stage2+第2意見、再生12回])。上限¥60以内、事前見込み約¥30は超過(EN検査1callが約¥0.27[推論トークンが大きい]、要約生成1callが平均¥0.118)。

## 判定材料(要点)

- **M1**: 要約MAJOR 14世代で、要約だけを再生成(最大2回、実際は全て1回目)した結果、前回指摘(要約のMAJOR)の解消は 14/14(従来方式 6/14)。再検査まで厳密に通った(COMPLIANT かつ前回指摘全解消)のは 12/14。**要約STOP相当(未解消MAJOR)は 8 → 2 件**(G03・G08。いずれも要約は解消し、再検査で**変更していない本文の1文**が新規にMAJOR指摘された[G03: ja_source/changed_scope、G08: translation/changed_fact+unsupported_new_claim]。本文は再生成していないため検査の揺れ)。従来で解消していた6世代は 6/6 とも解消。
- **M2**: 陽性26(翻訳由来22+増幅4)のうち、検出され origin=translation と判定: 旧 7 → 新 6(検出自体 旧 11 → 新 8、ja_source判定 旧 4 → 新 2)。主体型7のうち changed_actor=true になった: 旧 2 → 新 3(検出 旧2→新3、うち translation 判定 1 → 2)。**重大 EV-25 は旧・新とも未検出**、EV-28 は旧・新とも MAJOR+changed_actor+translation。ユーザー許容文: G09「so」= 旧・新とも MAJOR(changed_causality、仕様どおり因果は指摘対象)、G02「users」・G06「oil prices」= この回は**旧でも**該当文の指摘が無く(旧再実行0)、差を確認できない。同型 G07・G12(users)は旧 MAJOR → 新 該当なし。旧を再実行した40記事の MAJOR 総数: 旧 23 → 新 22、MAJORを含む記事 旧 16/40 → 新 16/40(ja_source MAJOR記事 12→11、translation MAJOR記事 9→8)。新の全59記事: MAJOR 33件、MAJORを含む記事 24/59(旧は残り19記事を未再実行=予算上限のため比較不能。保存済みの最終check[COMPLIANT]は選択バイアス[STOPした記事は記事ファイルが無い]で比較に使えない)。
- **M3**: EV-25(S9.1)を保護して Stage 2 へ渡した再生3回の最終判定: BLOCKING 1回(一次ACCEPTABLE→第2意見split→BLOCKING)・ACCEPTABLE 2回。保護対象(旧実runで再分類除外、かつ最終EN本文に残存)17件の Stage 2 判定: BLOCKING 1(EV-25)・QUALITY 3・ACCEPTABLE 13。**ledger整合文の誤書き換え(保護17件中のBLOCKING)は 0件**(BLOCKING の1件は EV-25 本体=ユーザー判定の重大)。Rewrite以降は未実行のため「BLOCKING=書換え対象になる」で数えた。

## V1 詳細表

| 世代 | 従来(本文ごと再生成) | 旧attempt1 MAJOR(要約) | 許容型を含む | 新・腕R: 要約のみ再生成 | 解消(COMPLIANT+前回指摘解消) | 前回指摘の解消 | 腕R後の新規MAJOR(位置/origin/型) | 腕F(初回JA+台帳入力)のMAJOR(要約/本文) | M1+M2 最終check |
|---|---|---|---|---|---|---|---|---|---|
| G01 | 解消 | changed_scope | - | 1回: Meta rolled back Muse’s human-concierge test after admitting it began without properly disclosing that contractors handled some calls. | ○ | ○ | - | なし | COMPLIANT |
| G02 | STOP | changed_scope; changed_causality | users(+prompting因果) | 1回: Meta tested human contractors handling some Muse calls without proper disclosure, then paused its human concierge feature. | ○ | ○ | - | なし | MAJOR ?/translation/changed_actor |
| G03 | STOP | changed_causality | - | 1回: Meta rolled back Muse’s human concierge feature after admitting it was a mistake to let contractors make calls without proper disclosure. | × | ○ | body/ja_source/changed_scope | なし | MAJOR body/ja_source/changed_scope |
| G04 | 解消 | changed_fact+changed_scope | - | 1回: Meta temporarily rolled back Muse’s human-concierge feature after contractors made some calls without proper disclosure. | ○ | ○ | - | body/ja_source/changed_scope | MAJOR body/ja_source/changed_scope |
| G05 | 解消 | changed_fact+unsupported_new_claim | - | 1回: The United States has, for the first time, officially acknowledged deploying weapons in orbit, though their exact nature remains unknown. | ○ | ○ | - | なし | COMPLIANT |
| G06 | STOP | changed_scope | oil prices | 1回: Brent futures soon recovered even after Trump replaced his proposed 20% payment on all cargo passing through Hormuz with Gulf investment deals. | ○ | ○ | - | なし | COMPLIANT |
| G07 | STOP | changed_fact+unsupported_new_claim | users | 1回: Meta tested some Muse calls with human contractors without proper disclosure, then rolled back the human concierge feature. | ○ | ○ | - | なし | COMPLIANT |
| G08 | STOP | changed_certainty+unsupported_new_claim | - | 1回: Meta rolled back its human concierge feature after a vice president called testing without proper disclosure a mistake. | × | ○ | body/translation/changed_fact+unsupported_new_claim | なし | COMPLIANT |
| G09 | STOP | changed_scope+unsupported_new_claim | users | 1回: Meta rolled back a Muse feature that let contractors handle some calls after admitting it was tested without proper disclosure. | ○ | ○ | - | なし | COMPLIANT |
| G10 | 解消 | changed_scope | - | 1回: Trump withdrew a proposed 20% reimbursement tied to all cargo passing through Hormuz, but oil prices soon rebounded. | ○ | ○ | - | なし | COMPLIANT |
| G11 | 解消 | changed_scope | - | 1回: Meta rolled back Muse’s feature that let contract workers make calls after admitting users weren’t properly informed. | ○ | ○ | - | ?/ja_source/changed_scope | MAJOR ?/ja_source/changed_certainty |
| G12 | STOP | changed_fact+changed_scope+changed_certainty+unsupported_new_claim | users | 1回: Meta temporarily rolled back Muse’s human-concierge feature after admitting it tested some contractor-handled calls without proper disclosure. | ○ | ○ | - | なし | COMPLIANT |
| G13 | 解消 | changed_fact+changed_scope | - | 1回: The U.S. acknowledged deploying weapons in orbit to protect the joint force, but their specific systems, attack capabilities, and targets remain unknown. | ○ | ○ | - | なし | COMPLIANT |
| G14 | STOP | changed_scope | - | 1回: Meta temporarily rolled back Muse’s human-handoff test after admitting it had not explained when contractors might handle calls. | ○ | ○ | - | summary/translation/changed_scope | COMPLIANT |
| EV28 | - | (指摘なし=EV-28見逃し) | - | (対象外) | - | - | - | body/translation/changed_fact+changed_certainty | - |

要約MAJOR 14世代: 厳密解消(COMPLIANT かつ 前回指摘が全て解消) = 12/14、前回指摘(要約のMAJOR)の解消 = 14/14 (従来方式は 6/14)
STOP相当(未解消MAJOR)だった8世代のうち、なお未解消: 2件 ['G03', 'G08'] (従来は 8件)
従来で解消していた6世代のうち、新方式でも解消: 6/6
V1 実費 ¥13.261 (要約生成+check の実測トークン x 登録単価)
要約生成1call平均 ¥0.1179 (n=29) (JA+台帳入力あり)
## V2 詳細(analyze_v2.py 出力)

```text
fixtures: article=59 tolerance=5; source old={'rerun': 45, 'stored': 19} new={'rerun': 64}

事象: 陽性(翻訳由来/増幅)=26 (subject型=7), JA由来=16

[陽性26] 検出/origin/severity (旧 -> 新)
  old: 検出=11/26  origin=translation含む=7  origin=ja_source含む=4  MAJOR=8  MINOR=3
  new: 検出=8/26  origin=translation含む=6  origin=ja_source含む=2  MAJOR=7  MINOR=1

[JA由来(旧再実行記事内)] 検出/origin/severity (旧 -> 新)
  old: 検出=6/16  origin=translation含む=1  origin=ja_source含む=5  MAJOR=6  MINOR=0
  new: 検出=5/16  origin=translation含む=1  origin=ja_source含む=4  MAJOR=5  MINOR=0

[主体型(subject)陽性 7件] changed_actor=true
  old: 検出=2  changed_actor=true=2  translation判定=1
  new: 検出=3  changed_actor=true=3  translation判定=2

事象別(陽性、旧->新)
  EV-01 translation/subject/minor: 旧[未検出] 新[未検出] | The next day, Trump posted that he was replacing that plan with trade 
  EV-02 amplified/subject/minor: 旧[MAJOR/ja_source/actor=Y] 新[未検出] | While the fee plan changed shape, concerns continued over attacks by t
  EV-04 translation/causal/minor: 旧[MAJOR/translation/actor=n] 新[MAJOR/translation/actor=n] | Trump dropped his proposed 20% Hormuz fee, but tensions around the str
  EV-06 amplified/subject/minor: 旧[未検出] 新[MAJOR/ja_source/actor=Y] | During that time, concerns about attacks by the United States and Iran
  EV-07 translation/causal/minor: 旧[未検出] 新[未検出] | Trump withdrew the proposed Strait of Hormuz fee, but Brent futures st
  EV-08 translation/causal/minor: 旧[MAJOR/translation/actor=n] 新[未検出] | The fee plan disappeared, but fears about oil supply and tanker safety
  EV-10 amplified/scope/minor: 旧[MAJOR/translation/actor=n] 新[未検出] | Instead, he announced deals on trade with the United States and invest
  EV-14 translation/scope/minor: 旧[MAJOR/translation/actor=n] 新[未検出] | Meta paused Muse’s test after human contractors, not AI, made calls wi
  EV-17 translation/number/minor: 旧[未検出] 新[MAJOR/translation/actor=n] | In addition, employees who asked Muse to negotiate their internet or c
  EV-18 translation/term/minor: 旧[未検出] 新[未検出] | Meta said it would continue improving the feature with businesses and 
  EV-19 translation/addition/minor: 旧[未検出] 新[未検出] | Meta’s AI phone service sometimes relied on hidden human helpers, rais
  EV-23 translation/number/minor: 旧[MINOR/ja_source/actor=Y] 新[未検出] | Meta executives admitted that starting a test in which contract staff 
  EV-25 translation/subject/major: 旧[未検出] 新[未検出] | In addition, in one case in which Meta was asked to negotiate internet
  EV-26 translation/number/minor: 旧[未検出] 新[未検出] | In response, Meta executives admitted that it had been a mistake to st
  EV-28 translation/subject/major: 旧[MAJOR/translation/actor=Y] 新[MAJOR/translation/actor=Y] | Meta’s AI phone calls sometimes relied on human contractors, but calle
  EV-30 translation/number/minor: 旧[MINOR/ja_source/actor=Y] 新[未検出] | Meta executives admitted that starting the test without proper disclos
  EV-31 translation/strength/minor: 旧[MINOR/translation/actor=n] 新[MAJOR/translation/actor=n] | Some of Meta’s AI phone assistant calls were actually made by human co
  EV-32 translation/number/minor: 旧[未検出] 新[未検出] | US government agencies recorded the statement as the first time the US
  EV-35 translation/number/minor: 旧[未検出] 新[未検出] | U.S. government agencies have recorded this as the first official ackn
  EV-38 translation/tense/minor: 旧[MAJOR/translation/actor=n] 新[未検出] | There are now more than 1,500 pieces of trackable debris.
  EV-42 translation/addition/minor: 旧[未検出] 新[MAJOR/translation/actor=n] | The United States has acknowledged deploying weapons in orbit, but the
  EV-45 translation/subject/minor: 旧[未検出] 新[MAJOR/translation/actor=Y] | According to an official U.S. government article, this was the first t
  EV-48 amplified/subject/minor: 旧[未検出] 新[未検出] | But another concern remained on the news stage: concerns about attacks
  EV-50 translation/number/minor: 旧[未検出] 新[MINOR/ja_source/actor=Y] | Meta executives admitted it was a mistake to begin testing calls by co
  EV-51 translation/addition/minor: 旧[MAJOR/ja_source/actor=n] 新[未検出] | Meta rolled back its human concierge feature after admitting it had no
  EV-52 translation/number/minor: 旧[未検出] 新[未検出] | Meta executives also admitted that it was a “mistake”

事象別(JA由来、旧->新)
  EV-03 scope/minor: 旧[未検出] 新[未検出] | And even after the statements changed, oil prices did not just fall on
  EV-09 causal/minor: 旧[MAJOR/ja_source/actor=n] 新[MAJOR/ja_source/actor=n] | The rise on the previous day was not only about the fee plan.
  EV-13 addition/minor: 旧[未検出] 新[未検出] | When a person speaks, some conversations may go more smoothly.
  EV-21 addition/minor: 旧[未検出] 新[未検出] | In effect, human cast members appeared from behind an AI that had been
  EV-22 scope/major: 旧[未検出] 新[未検出] | It plans to keep improving the phone feature and release it only when 
  EV-24 scope/minor: 旧[未検出] 新[未検出] | Muse is an AI agent that can handle requests by phone, such as booking
  EV-27 scope/minor: 旧[MAJOR/ja_source/actor=n] 新[未検出] | Meta's AI agent, Muse, can call companies and stores.
  EV-29 addition/minor: 旧[MAJOR/ja_source/actor=n] 新[MAJOR/ja_source/actor=n] | The problem was that testing began before they had fully worked out ho
  EV-33 addition/minor: 旧[未検出] 新[未検出] | A common comparison is Russia’s destruction of a satellite.
  EV-34 scope/minor: 旧[未検出] 新[未検出] | On September 14, 2026, the U.S. Secretary of the Air Force said that t
  EV-36 scope/minor: 旧[MAJOR/ja_source/actor=n] 新[MAJOR/ja_source/actor=n] | Article IV of the Outer Space Treaty clearly bans placing nuclear weap
  EV-37 causal/minor: 旧[MAJOR/translation/actor=n] 新[MAJOR/translation/actor=n] | If we get the answer wrong, it also affects our communications and the
  EV-41 addition/minor: 旧[MAJOR/ja_source/actor=n] 新[MAJOR/ja_source/actor=n] | In 2021, Russia destroyed an old satellite with a missile launched fro
  EV-43 addition/minor: 旧[未検出] 新[未検出] | These include GPS, missile tracking, monitoring space, and systems tha
  EV-44 strength/minor: 旧[未検出] 新[未検出] | We need to think separately about the fact that deployment has been co
  EV-49 scope/minor: 旧[未検出] 新[未検出] | But judging by market moves, worries about supply seemed to remain unc

[ユーザー許容文] 該当文のseverity(旧->新)と、その記事のMAJOR全件
  TOL_G02_users (users): old: 該当文dev=[] MAJOR総数=0  new: 該当文dev=[] MAJOR総数=0  
  TOL_G09_so (so): old: 該当文dev=[('MAJOR', 'translation')] MAJOR総数=1  new: 該当文dev=[('MAJOR', 'translation')] MAJOR総数=1  
      old MAJOR: translation ['changed_causality'] “Meta’s AI calling test used human contractors without proper disclosure, so the | 「so」によって、適切な開示がなかったことが機能のロールバックの原因だったと明示しています。Ledgerは、ミスとの認識とロールバックを記録していますが、その因果関係までは明記して
      new MAJOR: translation ['changed_causality'] “Meta’s AI calling test used human contractors without proper disclosure, so the | “So” explicitly presents the lack of proper disclosure as the reason for the rollback. The
  TOL_G06_oil (oil prices): old: 該当文dev=[] MAJOR総数=1  new: 該当文dev=[] MAJOR総数=0  
      old MAJOR: ja_source ['changed_fact', 'changed_actor', 'unsupported_new_claim'] “Concerns about attacks by the United States and Iran … continued.” | Ledgerは米国とイランの間の攻撃への懸念が続いたとしているが、記事は米国とイランの双方を攻撃の実行主体としているように読める。
  TOLX_G07_users (users(同型)): old: 該当文dev=[('MAJOR', 'translation')] MAJOR総数=1  new: 該当文dev=[] MAJOR総数=0  
      old MAJOR: translation ['changed_fact', 'changed_scope'] Meta paused a calling feature after human contractors made calls without properl | 「人間コンシェルジュ機能」のロールバックを、一般的な「通話機能」の停止として表現しており、対象範囲を広げています。
  TOLX_G12_users (users(同型)): old: 該当文dev=[('MAJOR', 'translation')] MAJOR総数=1  new: 該当文dev=[] MAJOR総数=0  
      old MAJOR: translation ['changed_certainty', 'unsupported_new_claim'] Meta paused Muse’s human concierge feature after concerns that users weren’t tol | 「適切な開示なしに契約スタッフが電話を担当するテストを始めた」というLedgerの記述と、契約スタッフへの機微情報の意図しない共有に関する従業員の懸念を結び付け、利用者にその情報へ

[最終英文の MAJOR 件数] 旧を再実行した記事(同一記事で旧/新を比較) と 新の全59記事
  [旧再実行=40記事] old: MAJOR総数=23 (translation=10, ja_source=13)  MAJORを含む記事=16/40 (ja_source MAJOR記事=12, translation MAJOR記事=9)
  [旧再実行=40記事] new: MAJOR総数=22 (translation=8, ja_source=14)  MAJORを含む記事=16/40 (ja_source MAJOR記事=11, translation MAJOR記事=8)
  [全59記事(旧=storedを含む)] old: MAJOR総数=23 (translation=10, ja_source=13)  MAJORを含む記事=16/59 (ja_source MAJOR記事=12, translation MAJOR記事=9)
  [全59記事(旧=storedを含む)] new: MAJOR総数=33 (translation=11, ja_source=22)  MAJORを含む記事=24/59 (ja_source MAJOR記事=18, translation MAJOR記事=11)

[新でMAJORになり、旧では同文がMAJORでない件(誤検知候補の目視用)]
  all6_writer_redesign_necessity_01__runs__hormuz__control__b3: ja_source ['changed_actor'] During that time, concerns about attacks by the United States and Iran, a blockade at sea, | 「米国とイランの攻撃」を「米国とイランによる攻撃」として、両国を攻撃の実行主体と明示しています。Ledgerの表現は両国間の攻撃です。
  all6_writer_redesign_necessity_01__runs__hormuz__control__b3: ja_source ['changed_fact', 'unsupported_new_claim'] One important point is that no money had actually started being collected. | 実際に徴収が始まっていなかったという具体的事実はLedgerに記載されていません。Ledgerが確認しているのは、7月13日の投稿が提案であり、制度設計が示されなかったことです。
  all6_writer_redesign_necessity_01__runs__hormuz__control__b4: ja_source ['changed_scope', 'unsupported_new_claim'] In other words, the news story can change in a day, but conditions at sea do not change in | 海上封鎖やタンカーの安全など、Ledgerが確認する個別の懸念が続いていたという範囲を超え、「海の状況は一日では変わらない」と一般化している。
  all6_writer_redesign_necessity_01__runs__meta__control__b1__: translation ['changed_number'] “employees who asked Muse to negotiate their internet or cable bills reported” | 複数の従業員が報告したように読めますが、Ledgerが確認しているのは1件の従業員報告です。直後に「one employee」と補足しており、記事内でも数の表現が食い違っています。
  all6_writer_redesign_necessity_01__runs__meta__control__b2__: ja_source ['changed_scope'] “Human supporting actors were also part of the show in services where AI makes phone calls | AI電話サービス一般に人間が関与しているように述べ、Ledgerが確認するMuse経由の電話の一部から対象を広げています。
  all6_writer_redesign_necessity_01__runs__meta__control__b2__: ja_source ['changed_scope'] “We are entering an age when you can ask AI to make phone calls for you” and Muse “can han | Ledgerが確認しているのは、Museに米国内の企業・店舗へ電話を依頼できる機能です。記事は対象をMuseからAI一般へ広げ、Museの電話機能についても米国内という範囲を示していません。
  all6_writer_redesign_necessity_01__runs__meta__control__b4__: translation ['changed_fact', 'changed_certainty', 'unsupported_new_claim'] “Some of Meta’s AI phone assistant calls were actually made by human contractors without u | Ledgerでは、人間コンシェルジュのテストが適切な開示なしに開始されたことは確認されているが、該当する電話の利用者に一切何も伝えられていなかったとまでは示されていない。この要約は「適切な開示がなかっ
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: ja_source ['changed_scope', 'changed_actor'] “to protect US forces from actions by hostile parties” | 保護対象がLedgerの「統合軍」ではなく「US forces」と記され、対象の範囲・受け手が変わっています。原文記事にも同じ表現があります。
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: ja_source ['changed_actor'] “An official article from a U.S. government agency records this as the first time the Unit | 初めて認めた主体を、Ledgerの「Space Force」から「United States」へ広げています。
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: translation ['changed_fact', 'changed_certainty'] “The United States has acknowledged deploying weapons in orbit, but their purpose and trea | 兵器の目的全般が不明としていますが、Ledgerでは統合軍を敵対的な相手の行動から防護する用途が説明されています。
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: ja_source ['changed_fact', 'changed_scope', 'unsupported_new_claim'] “our daily lives, which depend on GPS and satellite communications” | GPSや衛星通信に日々の暮らしが依存していると一般化しています。
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: translation ['changed_fact', 'changed_scope', 'changed_actor'] According to an official U.S. government article, this was the first time anyone had ackno | Ledgerが記録しているのは、Space Forceが配備を初めて認めたということです。「anyone」とすることで、認めた主体をSpace Force以外にも広げています。
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: translation ['changed_fact', 'unsupported_new_claim'] The United States confirmed its first orbital weapons deployment. | 「初めて確認した」の対象が、軌道上兵器配備の公式な確認ではなく、米国による最初の配備であるかのように読めます。Ledgerが確認するのは、Space Forceによる配備を初めて認めた発言であり、配備
  (件数 13)

[旧でMAJOR・新でMAJORでない件]
  all6_writer_redesign_necessity_01__runs__hormuz__control__b1: ja_source ['changed_actor'] “concerns continued over attacks by the United States and Iran”
  all6_writer_redesign_necessity_01__runs__hormuz__control__b2: ja_source ['unsupported_new_claim'] “Brent crude futures, an international benchmark”
  all6_writer_redesign_necessity_01__runs__hormuz__control__b3: translation ['changed_causality', 'unsupported_new_claim'] “fears about oil supply and tanker safety kept prices high.”
  all6_writer_redesign_necessity_01__runs__hormuz__control__b4: ja_source ['changed_fact', 'changed_causality', 'unsupported_new_claim'] “But the fee proposal was not the only reason for the rise.”
  all6_writer_redesign_necessity_01__runs__hormuz__control__b4: translation ['changed_fact', 'changed_scope', 'unsupported_new_claim'] “Instead, he announced deals on trade with the United States and investment with Gulf coun
  all6_writer_redesign_necessity_01__runs__meta__control__b1__: ja_source ['unsupported_new_claim'] “What matters here is that no actual leak was confirmed.”
  all6_writer_redesign_necessity_01__runs__meta__control__b1__: translation ['changed_scope'] Meta paused Muse’s test after human contractors, not AI, made calls without proper disclos
  all6_writer_redesign_necessity_01__runs__meta__control__b3__: translation ['changed_scope'] “Meta’s Muse test sometimes used human contractors instead of AI to make calls, without cl
  all6_writer_redesign_necessity_01__runs__meta__control__b3__: ja_source ['changed_scope'] Meta's AI agent, Muse, can call companies and stores.
  all6_writer_redesign_necessity_01__runs__meta__control__b3__: translation ['changed_fact', 'changed_actor', 'unsupported_new_claim'] “I thought I had left the call to AI, but a human voice came from the other end.”
  all6_writer_redesign_necessity_01__runs__meta__control__b4__: translation ['changed_fact', 'changed_actor', 'unsupported_new_claim'] Title: “I Asked AI to Make a Phone Call”
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: translation ['changed_time', 'unsupported_new_claim'] There are now more than 1,500 pieces of trackable debris.
  all6_writer_redesign_necessity_01__runs__space_weapons__cont: ja_source ['unsupported_new_claim'] “No specific system name has been announced. Neither their attack abilities nor their targ
  factlock_writer_trial_01__runs__meta__control__b3__factlock_: ja_source ['changed_fact', 'changed_scope', 'unsupported_new_claim'] Meta rolled back its human concierge feature after admitting it had not clearly told call 
  (件数 14)

費用(rerun分のみ) old: ¥12.288

費用(rerun分のみ) new: ¥16.092
```

## V3 詳細(analyze_v3.py 出力)

```text

### T01_meta_b3_baseline_r1 (all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1)  費用 ¥1.2992 (再分類 ¥0.3236 + Stage2/第2意見 ¥0.9756)  error=None
再分類: targets=10 protected_by_flags=3 excluded_claims=7 (保存実run: 除外9)
- [S9.1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=BLOCKING (一次=ACCEPTABLE, 第2意見split=True, floor=s1_second_opinion_blocking) | 旧実runのcycle1同文=QUALITY
    文: In addition, in one case in which Meta was asked to negotiate internet and cable bills, employees reported that a human contract worker made an inappr
    Stage1 issue: Ledgerでは従業員がMuseに料金交渉を依頼した事例だが、記事は「Meta was asked」とし、依頼を受けた主体をMetaに変えている。
    旧再分類reason: インターネット・ケーブル料金交渉の1件で、従業員が契約スタッフの人種に関する不適切発言を報告したというLedgerと一致する。
- [S10.1] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=BLOCKING (一次=QUALITY, 第2意見split=True, floor=s1_second_opinion_blocking) | 旧実runのcycle1同文=BLOCKING
    文: In response, Meta executives admitted that it had been a mistake to start the test without giving a proper explanation.
    Stage1 issue: Ledgerで「ミス」と認めた主体はSuperintelligence Labs部門の副社長だが、記事は「Meta executives」と複数の幹部に広げている。
    旧再分類reason: 
- [L1] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=BLOCKING (一次=BLOCKING, 第2意見split=None, floor=None) | 旧実runのcycle1同文=BLOCKING
    文: Meta’s AI phone calls sometimes relied on human contractors, but callers were not clearly told who was speaking.
    Stage1 issue: 開示が適切でなかったというLedgerの記述から、通話相手に話者が誰かを明確に伝えていなかったと断定しています。
    旧再分類reason: 
BLOCKING件数: 再生=3  旧実run cycle1=3  再生のみ=1  旧のみ=1
    再生のみBLOCKING: in addition, in one case in which meta was asked to negotiate internet and cable bills, employees re

### T02_space_b2_baseline_r2 (all6_writer_redesign_necessity_01/runs/space_weapons/control/b2__baseline__r2)  費用 ¥1.1477 (再分類 ¥0.3576 + Stage2/第2意見 ¥0.7901)  error=None
再分類: targets=12 protected_by_flags=1 excluded_claims=8 (保存実run: 除外8)
- [S2.2] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: An official article from a U.S. government agency records this as the first time the United States acknowledged deploying weapons in space.
    Stage1 issue: Ledgerが初回の認定主体としているSpace Forceを、記事はUnited States全体に広げている。
    旧再分類reason: 米政府機関の記事が、米国による宇宙への兵器配備の初公認として記録したという内容はF-001と一致する。
BLOCKING件数: 再生=1  旧実run cycle1=1  再生のみ=0  旧のみ=0

### T03_ai_control_p2_rep1 (open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1)  費用 ¥1.4657 (再分類 ¥0.3877 + Stage2/第2意見 ¥1.078)  error=None
再分類: targets=13 protected_by_flags=2 excluded_claims=6 (保存実run: 除外9)
- [S1.2] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=QUALITY (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: An AI that was supposed to be isolated got out into the outside world and entered real systems.
    Stage1 issue: 隔離環境からAIが自力で「外へ出た」という言い方は、環境の設定ミスによるインターネット接続・アクセスを、AI自身の脱出行為のように表現している。
    旧再分類reason: 隔離想定の評価環境からインターネットに到達し、実在組織のシステムに不正アクセスしたというLedgerの記述に合う。
- [S1.3] 【旧で除外→保護】 旧再分類=NO_FACT_CLAIM/actor=n_a 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: Just hearing this makes it feel as if the AI made a plan, broke out of prison, and escaped on its own.
    Stage1 issue: AIが計画し、脱獄し、自力で逃げたかのような印象を示す。Ledgerは実環境での脱出計画やそのような意図を裏付けていない。
    旧再分類reason: 「そう感じられる」という読者の印象を述べた比喩で、AIが実際に計画・脱出したとの断定ではない。
BLOCKING件数: 再生=1  旧実run cycle1=2  再生のみ=1  旧のみ=2
    再生のみBLOCKING: this even created a chance for login information to leak out

### T04_ai_control_p2_rep2 (open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2)  費用 ¥1.2422 (再分類 ¥0.3879 + Stage2/第2意見 ¥0.8543)  error=None
再分類: targets=17 protected_by_flags=1 excluded_claims=12 (保存実run: 除外14)
- [S2.1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: Anthropic had AI agents solve a fictional game of capture the flag.
    Stage1 issue: The Ledger says Claude models were operating on capture-the-flag tasks in third-party environments, but does not establish that Anthropic had agents solve a fictional game; this changes the attributio
    旧再分類reason: AnthropicのClaudeモデルが架空のCTF課題に取り組んだという説明は、評価環境でCTF課題を実行したLedgerの記述と一致する。
BLOCKING件数: 再生=1  旧実run cycle1=2  再生のみ=0  旧のみ=1

### T05_meta_p2_rep1 (open233_allfact_note_e2e_02/runs/meta/nb/p2/rep1)  費用 ¥1.1503 (再分類 ¥0.4578 + Stage2/第2意見 ¥0.6925)  error=None
再分類: targets=19 protected_by_flags=1 excluded_claims=16 (保存実run: 除外17)
- [L1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: Meta’s AI calling test sometimes relied on undisclosed human contractors, raising privacy concerns for users.
    Stage1 issue: 「undisclosed human contractors」は一部テストの内容と関連するが、「raising privacy concerns for users」は懸念を示した主体をユーザーに置き換え、テストがユーザーの懸念を引き起こしたという因果も加えている。Ledgerでは懸念を示したのはMeta従業員。
    旧再分類reason: Ledgerは一部の電話で契約スタッフが担当したことと、ユーザー情報のプライバシー上の懸念を従業員が示したことを記録しており、頻度・対象範囲と趣旨が一致する。
BLOCKING件数: 再生=1  旧実run cycle1=1  再生のみ=0  旧のみ=0

### T06_meta_p2_rep2 (open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2)  費用 ¥1.3058 (再分類 ¥0.4023 + Stage2/第2意見 ¥0.9035)  error=None
再分類: targets=15 protected_by_flags=4 excluded_claims=10 (保存実run: 除外14)
- [S1.1] 【旧で除外→保護】 旧再分類=NO_FACT_CLAIM/actor=n_a 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: Was the person on the other end of the call an AI or a human?
    Stage1 issue: 質問は電話の相手側がAIか人間かという点を示唆しますが、Ledgerが示しているのは電話をかけた側が人間の契約スタッフだった一部事例です。
    旧再分類reason: 読者への導入の問いかけで、具体的な事実を断定していない。
- [S1.2] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: This time, at least in some cases, it was a human.
    Stage1 issue: 「it」は直前の「電話の相手側の人」を指す読み方があり、Ledgerが述べる人間は電話をかけた側です。行為者・対象が曖昧または異なります。
    旧再分類reason: 一部の電話を人間が担当したという点が、対象範囲と限定を含めLedgerに一致する。
- [S9.3] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=BLOCKING (一次=ACCEPTABLE, 第2意見split=True, floor=s1_second_opinion_blocking) | 旧実runのcycle1同文=BLOCKING
    文: But the humans who ended up in the main role had not been told.
    Stage1 issue: 「伝えられていなかった」主体が人間の担当者を指す読み方になりますが、Ledgerは適切な開示なしにテストを開始したことを記録しており、人間の担当者が知らされていなかったとは述べていません。
    旧再分類reason: 
- [S9.4] 【旧で除外→保護】 旧再分類=NO_FACT_CLAIM/actor=n_a 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: That was the problem.
    Stage1 issue: 「それ」が人間の担当者に知らされていなかったことを指すなら、その問題設定はLedgerに支えられていません。
    旧再分類reason: 直前の問題を評価する表現で、新たな具体的事実を加えていない。
BLOCKING件数: 再生=2  旧実run cycle1=1  再生のみ=1  旧のみ=0
    再生のみBLOCKING: whether the one on the other end of the phone is an ai or a human

### T07_poly_ai_control_rep1 (open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1)  費用 ¥1.2829 (再分類 ¥0.3456 + Stage2/第2意見 ¥0.9373)  error=None
再分類: targets=12 protected_by_flags=1 excluded_claims=7 (保存実run: 除外9)
- [S5.1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=QUALITY (一次=QUALITY, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: What is more, the standard protections used when accessing a public site were not in place.
    Stage1 issue: The ledger says the models lacked standard public-deployment cyber safeguards; the article instead suggests protections used to access the public site itself were absent.
    旧再分類reason: 当該評価環境に標準的なサイバー安全策がなかったというLedgerの記述と一致する。
BLOCKING件数: 再生=0  旧実run cycle1=1  再生のみ=0  旧のみ=1

### T08_poly_meta_rep2 (open233_control_checker_polysemy_trial_01/runs/meta/nb/rep2)  費用 ¥1.6607 (再分類 ¥0.2669 + Stage2/第2意見 ¥1.3938)  error=None
再分類: targets=9 protected_by_flags=5 excluded_claims=7 (保存実run: 除外9)
- [T] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=BLOCKING (一次=ACCEPTABLE, 第2意見split=True, floor=s1_second_opinion_blocking) | 旧実runのcycle1同文=BLOCKING
    文: # I Followed an AI Phone Agent and Found a Human
    Stage1 issue: 記事の書き手が自らAI電話エージェントを追跡して人間を見つけたという一人称の体験は、Ledgerにありません。
    旧再分類reason: 
- [S1.1] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=QUALITY (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=BLOCKING
    文: The AI makes the call.
    Stage1 issue: AIが電話をかけると一般化していますが、Ledgerが確認しているのはMuse経由の電話の一部を人間の契約スタッフが担当したテストです。
    旧再分類reason: 
- [S3.3] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: The system lets AI handle troublesome calls for the user.
    Stage1 issue: システムが「厄介な」電話をAIに処理させるという性質・対象範囲はLedgerにありません。人間が担当した電話が一部あった事実とも区別されていません。
    旧再分類reason: Museがユーザーの依頼で企業や店舗に電話し、用件を処理できるというLedgerの説明の範囲内である。
- [S8.1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: A Meta executive in charge admitted that this was a “mistake.”
    Stage1 issue: LedgerではMetaのSuperintelligence Labs部門の副社長が説明したとされています。「executive in charge」はその人物をテスト全体の責任者とする含みがあり、主体・役割が一致するとは確認できません。
    旧再分類reason: Metaの幹部が、適切な開示なしにテストを始めたことを「ミス」と認めたというLedgerの記述と一致する。
- [L1] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=ACCEPTABLE
    文: During testing, Meta’s AI phone agent sometimes had human contractors make calls without properly telling users.
    Stage1 issue: 人間の契約スタッフが一部の電話を担当し、適切な開示がなかったことは支えられますが、誰に説明しなかったのかを「users」と特定する根拠はLedgerにありません。
    旧再分類reason: テスト中の一部の電話を契約スタッフが担当し、適切な開示がなかったというLedgerの内容を、範囲を保って要約している。
BLOCKING件数: 再生=2  旧実run cycle1=3  再生のみ=0  旧のみ=1

### T09_poly_meta_rep3 (open233_control_checker_polysemy_trial_01/runs/meta/nb/rep3)  費用 ¥1.3019 (再分類 ¥0.3145 + Stage2/第2意見 ¥0.9874)  error=None
再分類: targets=12 protected_by_flags=4 excluded_claims=12 (保存実run: 除外15)
- [S1.3] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=QUALITY (一次=QUALITY, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: AI even handles the phone call itself.
    Stage1 issue: Ledgerは電話機能の依頼内容と一部の電話を人間が担当したことを述べるが、AIが電話そのものを処理するという一般的な断定は支えていない。
    旧再分類reason: LedgerはAIのみで電話する場合にも言及しており、電話機能の説明と一致する。
- [S3.3] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: The test had begun without people being properly told about it.
    Stage1 issue: Ledgerは適切な開示なしにテストが始まったとするが、「人々に適切に伝えられていなかった」と開示の相手を広く特定することまでは明示していない。
    旧再分類reason: 人間スタッフが電話を担当するテストに適切な開示がなかったというLedgerの記述に一致する。
- [L1] (旧でも候補) 旧再分類=None/actor=None 最終本文に残存=None -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=BLOCKING
    文: Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    Stage1 issue: 一部の電話を人間の契約スタッフが担当したことは支えられるが、「ユーザーに知らされずに」と受け手をユーザーに限定する記載は、Ledgerの「適切な開示なし」から直接確認できない。
    旧再分類reason: 
- [S5.3] 【旧で除外→保護】 旧再分類=SUPPORTED/actor=match 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: This is one individual report, but it means there were cases where a conversation ended the moment people learned it was AI.
    Stage1 issue: 個別の従業員報告を、AIだと分かると会話が終わる事例が一般に複数あったという結論へ広げています。
    旧再分類reason: 一従業員の報告として、相手がMuseをAIだと認識すると保険会社が繰り返し電話を切ったというLedgerの記述に一致する。
BLOCKING件数: 再生=1  旧実run cycle1=1  再生のみ=1  旧のみ=1
    再生のみBLOCKING: that information could be shared without the user knowing with contract workers at a call center

### T10_poly_meta_rep6 (open233_control_checker_polysemy_trial_01/runs/meta/nb/rep6)  費用 ¥1.2055 (再分類 ¥0.3973 + Stage2/第2意見 ¥0.8082)  error=None
再分類: targets=11 protected_by_flags=1 excluded_claims=6 (保存実run: 除外11)
- [S4.3] 【旧で除外→保護】 旧再分類=NO_FACT_CLAIM/actor=n_a 最終本文に残存=True -> 再生 Stage2=ACCEPTABLE (一次=ACCEPTABLE, 第2意見split=False, floor=None) | 旧実runのcycle1同文=None
    文: It was almost as if the AI was looking for a human to stand in for it.
    Stage1 issue: AIが人間を代役として探していたかのような目的・意図はLedgerで確認されていません。
    旧再分類reason: 「人間を探しているかのよう」という比喩的な表現で、AIが実際に人間を探したという事実を主張していない。
BLOCKING件数: 再生=0  旧実run cycle1=1  再生のみ=0  旧のみ=1

## 集計
{"runs": 10, "protected": 17, "blocking": 1, "quality": 3, "acceptable": 13, "missing": 0, "cost": 13.0619, "reclass_cost": 3.6412, "stage2_cost": 9.4207, "retained_protected": 17, "retained_blocking": 1, "already_candidate_changed_actor": 6, "retained_acceptable": 13, "retained_quality": 3}```

## 制限・注意
- 各条件 n=1 サンプル。EN検査・Stage 2 は非決定的(同一記事の再検査で、保存済み最終checkがCOMPLIANTだった記事でも旧検査の再実行で40記事中16記事にMAJORが出た)。M3のEV-25も3回中1回のみBLOCKING。
- V1 は保存済みの本文(attempt1)に対する要約再生成のみ。要約の「主体・範囲の保持」は人手(LLM1名)の目視確認で、各再生成要約は台帳の語(human concierge feature、Muse 等)に寄る傾向がある一方、元の要約より対象が狭まる(G06 は焦点が Brent futures の値動きに移る)事例がある。
- V1 の対象は Advanced(Family X)枝。Standard(A2)枝への M1 適用は未実装。
- V2 の旧再実行は 45/64(40記事+許容文5)。残り19記事(陽性事象を含まない記事のうち1つおきを除いた側)は予算上限のため旧を再実行していない。
- V3 は cycle 1 の Stage 2 まで。Rewrite・Recheck・出口以降は未再生。open238 の replay 2件(同一入力 ai_control p2 rep2 と同じ claim)は T04 で代表した。
- 費用が事前見込み(約¥30)の約1.9倍。
