# E1_item_alignment: 元評価⑤b 82項目 対 再採点JSON の1件ずつの突合(OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_C2、¥0)

Opus任意レビューの追加証拠E1。元⑤b(STAGEWISE⑤b=JA/EN最終残存、重大+軽微。従来21+P2 61=82項目)の各項目を、同一記事の再採点JSON(`er052_output/open233_ng_root_cause_01/eval/articles/*.json`)の ng_items / pending と1件ずつ突き合わせた。API無し、評価JSON・元台帳は未修正。突合は単独LLM(Sonnet実行層)判断で人間確認なし。

## 0. 方法と定義

- 対象82件の抽出: `stagewise_*.json`のng_itemsのうち「s5が残存」または「s1=JA発生かつs3=EN修正済(JAのみ残存)」(従来20+1、P2 57+4。STAGEWISE_SUMMARY §1の⑤b 21/61と一致)。元記事15本はMAP(開封済み)で再採点の匿名コードへ対応付け(例: meta P2 rep1=a5te)。
- 分類(各項目に1つ): **再採点でNG**=同じ文・同じ誤りが再採点のng_itemsにある(重大/軽微の別は問わず。降格は備考) / **保留として記録**=再採点のpendingに同じ文・同じ論点がある(NG未満と評価者が明示判断した=NG/保留の線引き) / **未検出**=ng_itemsにもpendingにも対応がない / **対象外**=再採点に含まれない記事・工程(**0件**: 15記事とも再採点に含まれ、全82項目の引用句は再採点パックの記事JA R2またはENの本文に存在することを文字列照合で確認、82/82一致)。
- **曖昧**列(別列): 対応付けが一意でない(文は共有するが論点が異なる/同系統の因果主張を1項目に束ねた可能性/一部のみ対応)もの。分類欄は最善の判断を置き、曖昧=○を付した。曖昧8件を別方向に倒した場合の幅も3節に示す。
- **性質ラベル**(未検出のみ、私見・人間未確認): D=台帳にない事実/因果/数値/主体・対象の付加や不一致寄り(B3 rubricの軽微NGに該当しうる=見落とし寄り)、K=比喩・評価語・修辞・曖昧読みが中心(NG未満と判断されうる=線引き寄り)、U=本文だけでは判別不能。再採点はNGでもpendingでもない文について「見て問題なしとした」記録を残さないため、**未検出は『線引き』か『見落とし』かを証拠上は区別できない**。性質ラベルは目安に過ぎない。

## 1. 結果サマリ(82項目)

| 分類 | 件数 | 割合 |
|---|---|---|
| 再採点でNG | 13 | 15.9% |
| 保留として記録 | 5 | 6.1% |
| 未検出 | 64 | 78.0% |
| 対象外 | 0 | 0.0% |
| 計 | 82 | 100% |

### 出所別

| 出所 | 項目数 | 再採点でNG | 保留として記録 | 未検出 | 曖昧(再掲) |
|---|---|---|---|---|---|
| 従来(Note無) | 21 | 2/21(10%) | 1/21(5%) | 18/21(86%) | 2 |
| P2(全fact Note) | 61 | 11/61(18%) | 4/61(7%) | 46/61(75%) | 6 |
| 計 | 82 | 13/82(16%) | 5/82(6%) | 64/82(78%) | 8 |

### テーマ別

| テーマ | 項目数 | NG | 保留 | 未検出 |
|---|---|---|---|---|
| meta | 16 | 2 | 1 | 13 |
| hormuz | 17 | 1 | 3 | 13 |
| sewer | 19 | 4 | 1 | 14 |
| ai_control | 18 | 1 | 0 | 17 |
| space_weapons | 12 | 5 | 0 | 7 |

### 記事別

| 記事(再採点コード) | 元出所 | 項目数 | NG | 保留 | 未検出 | 再採点側のその記事のNG件数(全工程)/保留件数 |
|---|---|---|---|---|---|---|
| meta/a5te | p2 | 5 | 0 | 1 | 4 | 0/2 |
| meta/475j | p2 | 7 | 1 | 0 | 6 | 1/1 |
| meta/7aqr | control | 4 | 1 | 0 | 3 | 1/1 |
| hormuz/h3rq | p2 | 8 | 0 | 1 | 7 | 1/1 |
| hormuz/j7gv | p2 | 8 | 1 | 2 | 5 | 1/3 |
| hormuz/byz5 | control | 1 | 0 | 0 | 1 | 1/2 |
| sewer/87tc | p2 | 6 | 0 | 0 | 6 | 0/1 |
| sewer/g8qg | p2 | 6 | 4 | 0 | 2 | 1/1 |
| sewer/4hgy | control | 7 | 0 | 1 | 6 | 1/1 |
| ai_control/b3ux | p2 | 6 | 0 | 0 | 6 | 1/1 |
| ai_control/cupe | p2 | 7 | 1 | 0 | 6 | 1/1 |
| ai_control/cfqm | control | 5 | 0 | 0 | 5 | 1/0 |
| space_weapons/bcgj | control | 4 | 1 | 0 | 3 | 3/0 |
| space_weapons/493w | p2 | 2 | 0 | 0 | 2 | 0/0 |
| space_weapons/89wf | p2 | 6 | 4 | 0 | 2 | 3/0 |

- 元⑤b項目を持つ15記事のうち、元項目に1件もNG一致がない記事は8本(meta/a5te, hormuz/h3rq, hormuz/byz5, sewer/87tc, sewer/4hgy, ai_control/b3ux, ai_control/cfqm, space_weapons/493w)。

### 元の重大4件の扱い

| 元ID | 内容 | 再採点での扱い |
|---|---|---|
| meta-p2r2-02 | JA「ただし、主役になった人間が知らされていなかった。」「問題は、その事実を相手に十分知らせないまま… | 再採点でNG → meta-475j-01(軽微へ降格) |
| ai-p2r1-01 | JA「いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。」/EN「In other … | 未検出 |
| sw-p2r2-01 | JA「宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」/… | 再採点でNG → space_weapons-89wf-01(重大) |
| sw-p2r2-02 | JA「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初め… | 再採点でNG → space_weapons-89wf-01(重大) |

重大4件の内訳: 再採点で重大として一致2(sw-p2r2-01/02→89wf-01、1件に統合)、軽微へ降格して一致1(meta-p2r2-02→475j-01)、未検出1(ai-p2r1-01、比喩)。

## 2. 機序別集計(元評価での残存の型)

| 型 | 項目数 | NG | 保留 | 未検出 |
|---|---|---|---|---|
| JA+EN共通残存 | 61 | 8 | 5 | 48 |
| JAのみ残存(EN修正済) | 10 | 4 | 0 | 6 |
| EN新規(JA該当なし) | 11 | 1 | 0 | 10 |

未検出64件の性質ラベル(私見): D(台帳付加・不一致寄り) 32件 / K(比喩・評価語・曖昧読み寄り) 16件 / U(判別不能) 16件。

| 出所 | 未検出 | D | K | U |
|---|---|---|---|---|
| 従来 | 18 | 6 | 3 | 9 |
| P2 | 46 | 26 | 13 | 7 |

## 3. 線引き由来 対 見落とし由来(ドラフト§1へ反映する数値)

- **再採点側が元項目を『問題あり/要判断』と認識していた**: NG 13 + 保留 5 = 18/82(22%)。うち**記録上確実に線引き由来(NG未満と明示判断した保留)**は5件(6%)。
- **記録上は区別不能(未検出)**: 64/82(78%)。これが線引き由来(評価者が見て非NGとした)か見落とし由来(気づかなかった)かは、再採点が非NG判断を記録しないため**証拠上は判別できない**。性質ラベル(私見)では、D 32件(50%)は台帳との不一致・付加寄りでB3 rubricの軽微NGに当たりうる(見落とし寄り)、K 16件(25%)は比喩・評価語・曖昧読み中心(線引き寄り)、U 16件(25%)は判別不能。
- **曖昧の影響**: 曖昧8件(NG 3、保留 1、未検出 4)。曖昧なNG・保留をすべて未検出へ倒すとNG 10(12%)・保留 4(5%)・未検出 68(83%)、逆に曖昧な未検出をすべて一致側へ倒しても未検出は60(73%)で、**未検出が大多数という結論は動かない**。
- 読み方(Fable判断用の材料): (a) Opusの仮説『差の相当部分はNG/保留の線引き』のうち、**記録された保留が元項目に対応する割合は6%**(再採点のpending全23件のうち元⑤b項目と対応したのは5件、残り18件は別の論点)。(b) 82項目の約8割は再採点がNGにも保留にもしていない。これが評価者の暗黙の線引きなのか見落としなのかは、**人間判定(E2)なしには分けられない**。(c) 逆方向: 再採点の⑤b相当NG 11件のうち9件(82%)は元項目と対応する(対応なし2件: bcgj-01 ロシア因果、b3ux-01 認証情報流出の範囲。b3ux-01は元ai-p2r1-03と近接文で曖昧)。再採点は元評価の部分集合に近く、再採点だけが拾った別種のNGは少ない。

## 4. 再採点側 → 元項目の逆引き(⑤b相当NG 11件)

| 再採点項目 | 重大/軽微 | 対応する元項目 |
|---|---|---|
| meta-475j-01 | 軽微 | meta-p2r2-02 |
| meta-7aqr-01 | 軽微 | meta-c-04 |
| hormuz-j7gv-01 | 軽微 | hor-p2r2-01 |
| sewer-g8qg-01 | 軽微 | sewer-p2r2-01, sewer-p2r2-02, sewer-p2r2-03, sewer-p2r2-04 |
| ai_control-cupe-01 | 軽微 | ai-p2r2-06 |
| space_weapons-bcgj-03 | 軽微 | sw-ctl-02 |
| space_weapons-89wf-01 | 重大 | sw-p2r2-01, sw-p2r2-02 |
| space_weapons-89wf-03 | 軽微 | sw-p2r2-03 |
| space_weapons-89wf-02 | 軽微 | sw-p2r2-05 |
| space_weapons-bcgj-01(F-002ロシア因果、JA+EN) | 軽微 | 対応なし(元⑤bに無い) |
| ai_control-b3ux-01(EVID-009 認証情報流出の範囲) | 軽微 | 対応なし(近接文ai-p2r1-03が曖昧) |

(再採点の⑤b相当NGはJA R2またはEN残存。R0のみ存在するNG(hormuz-h3rq-01、hormuz-byz5-01、sewer-4hgy-01、ai_control-cfqm-01、space_weapons-bcgj-02)は⑤b対象外のため除く。)

## 5. 82項目の突合表

再採点の記号: NG=ng_items、保留=pending。曖昧=○は対応付けが一意でない。性質=未検出のみ(D/K/U、私見)。

| # | 元ID | 記事 | 元重/軽 | 元fact | 型 | 分類 | 再採点側の対応 | 曖昧 | 性質 | 元項目(抜粋) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | meta-p2r1-01 | meta/a5te | 軽微 | MUSE-HC-010 | EN新規 | 未検出 | - |  | D | EN one-liner「Meta’s AI calling test sometimes relied on un… |
| 2 | meta-p2r1-02 | meta/a5te | 軽微 | MUSE-HC-006 | JAのみ残存 | 未検出 | - |  | D | JA「AIが仕事を受け取り、困ったところは人間のプロがさっと解決する。そんな華やかな舞台裏にも見えます。」/EN「A… |
| 3 | meta-p2r1-03 | meta/a5te | 軽微 | MUSE-HC-006 | JA+EN共通残存 | 未検出 | - |  | D | JA「AIにお願いしたはずの電話に、人間の助っ人が登場していたわけです。」/EN「a human helper ha… |
| 4 | meta-p2r1-04 | meta/a5te | 軽微 | MUSE-HC-006 | JA+EN共通残存 | 未検出 | - |  | D | JA「AIの画面を見ているつもりが、その先で人間が仕事をしている。」/EN「You may think you ar… |
| 5 | meta-p2r1-05 | meta/a5te | 軽微 | MUSE-HC-012 | JA+EN共通残存 | 保留として記録 | meta-a5te-P2 |  | - | JA「問題は、そうした可能性があるのに、利用者へ十分な説明がないままテストが始まったことでした。」/EN「The p… |
| 6 | meta-p2r2-01 | meta/475j | 軽微 | MUSE-HC-006 | JA+EN共通残存 | 未検出 | - |  | K | JA「電話の相手はAIか、それとも人間か。今回の答えは、少なくとも一部では人間でした。」/EN「Was the pe… |
| 7 | meta-p2r2-02 | meta/475j | 重大 | MUSE-HC-012 | JA+EN共通残存 | 再採点でNG | meta-475j-01(軽微へ降格) |  | D | JA「ただし、主役になった人間が知らされていなかった。」「問題は、その事実を相手に十分知らせないまま、テストを始めた… |
| 8 | meta-p2r2-03 | meta/475j | 軽微 | MUSE-HC-012 | JA+EN共通残存 | 未検出 | - |  | D | JA「Metaはその説明を忘れて、いったん舞台の幕を下ろしたわけです。」/EN「Meta forgot to giv… |
| 9 | meta-p2r2-04 | meta/475j | 軽微 | MUSE-HC-012 | EN新規 | 未検出 | - |  | D | EN one-liner「Meta’s AI phone test used undisclosed human c… |
| 10 | meta-p2r2-05 | meta/475j | 軽微 | MUSE-HC-006 | JA+EN共通残存 | 未検出 | - |  | D | JA「AIが電話をかけてくれると思ったら、舞台裏では人間のスタッフが登場する。」/EN「You think AI i… |
| 11 | meta-p2r2-06 | meta/475j | 軽微 | MUSE-HC-008(根拠… | JA+EN共通残存 | 未検出 | - |  | D | JA「ややこしい話なら、人間が対応したほうが自然に進むこともあります。」/EN「If the matter is c… |
| 12 | meta-p2r2-07 | meta/475j | 軽微 | MUSE-HC-014 | JA+EN共通残存 | 未検出 | - |  | K | JA「Metaは、電話の相手となる事業者との改善を続け、準備が整い、適切な説明ができる場合にだけ、広く公開するとして… |
| 13 | meta-c-01 | meta/7aqr | 軽微 | MUSE-HC-012 | JA+EN共通残存 | 未検出 | - |  | D | JA「Metaの幹部は、この始め方を「ミス」だったと認めました。そして9月22日までに…ロールバックしました。」/E… |
| 14 | meta-c-02 | meta/7aqr | 軽微 | MUSE-HC-010 | JAのみ残存 | 未検出 | - |  | D | JA「Metaの従業員が心配したのは、まさにそこでした。」/EN「That was exactly what wor… |
| 15 | meta-c-03 | meta/7aqr | 軽微 | MUSE-HC-010 | EN新規 | 未検出 | (7aqr-01と同句型) | ○ | D | EN one-liner「Meta tested having human workers handle some … |
| 16 | meta-c-04 | meta/7aqr | 軽微 | MUSE-HC-012 | JA+EN共通残存 | 再採点でNG | meta-7aqr-01 |  | D | JA「その出演者が誰なのか、利用者に十分伝わっていなければ…」「適切な開示がないまま始まっていました」/EN「if … |
| 17 | hor-p2r1-01 | hormuz/h3rq | 軽微 | HF-003 | JA+EN共通残存 | 未検出 | - |  | D | JA「言い換えると、海峡を通る荷物に、広く同じ割合で費用を負担してもらう案です。」/EN「In other word… |
| 18 | hor-p2r1-02 | hormuz/h3rq | 軽微 | HF-003 | JAのみ残存 | 未検出 | - |  | D | JA「貨物に直接料金をかける方法と、…」/EN b1b「One is to charge cargo directl… |
| 19 | hor-p2r1-03 | hormuz/h3rq | 軽微 | HF-007 | JA+EN共通残存 | 未検出 | - |  | D | JA題名「海峡の請求書が、翌日には商談になった」/「相手国との協議を通じて貿易や投資につなげる方法」/EN「beco… |
| 20 | hor-p2r1-04 | hormuz/h3rq | 軽微 | HF-007/HF-008 | JA+EN共通残存 | 未検出 | - |  | K | JA「料金を集めるという発想そのものが、別の舞台へ移ったことです。」/EN「It is that the very … |
| 21 | hor-p2r1-05 | hormuz/h3rq | 軽微 | HF-007 | JA+EN共通残存 | 未検出 | - |  | D | JA「相手国との協議」/EN「talks with the other country」(台帳は湾岸諸国=複数。単数… |
| 22 | hor-p2r1-06 | hormuz/h3rq | 軽微 | HF-007 | JA+EN共通残存 | 未検出 | - |  | D | JA「今回の投稿は、その切り替えが一日で起きたことを示しました。」/EN「This post showed that… |
| 23 | hor-p2r1-07 | hormuz/h3rq | 軽微 | HF-003 | JA+EN共通残存 | 保留として記録 | hormuz-h3rq-p1 |  | - | JA「もし実施されれば、通る貨物すべてが対象になる大きな仕組みでした。」/EN「it would have been… |
| 24 | hor-p2r1-08 | hormuz/h3rq | 軽微 | HF-002/HF-007 | JA+EN共通残存 | 未検出 | - |  | K | JA「同じ安全確保をめぐる話でも、入り口は二つあります。」/EN「Even when the issue is ab… |
| 25 | hor-p2r2-01 | hormuz/j7gv | 軽微 | HF-003 | JAのみ残存 | 再採点でNG | hormuz-j7gv-01 |  | D | JA「船が通るたびに、アメリカの安全対策費を払う。」/EN b1b「Every time a ship passed… |
| 26 | hor-p2r2-02 | hormuz/j7gv | 軽微 | HF-002/HF-003 | JAのみ残存 | 未検出 | - |  | D | JA「…費用を、通過する貨物に負担してもらう考えです。」/EN b1b「The idea was to have p… |
| 27 | hor-p2r2-03 | hormuz/j7gv | 軽微 | HF-003 | JA+EN共通残存 | 未検出 | (j7gv-P3と文共有) | ○ | D | JA「通行する貨物に直接料金をかける話が、湾岸諸国との商談に変わったわけです。」/EN「A plan to char… |
| 28 | hor-p2r2-04 | hormuz/j7gv | 軽微 | HF-007 | JA+EN共通残存 | 保留として記録 | hormuz-j7gv-P3 |  | - | JA題名「…翌日には商談会になった」/EN「…the Next Day It Became a Business M… |
| 29 | hor-p2r2-05 | hormuz/j7gv | 軽微 | HF-009 | JA+EN共通残存 | 未検出 | - |  | D | JA「なぜ原油価格は大きく下がらなかったのでしょうか」/EN one-liner「…oil prices staye… |
| 30 | hor-p2r2-06 | hormuz/j7gv | 軽微 | HF-007 | JA+EN共通残存 | 未検出 | - |  | D | JA「その料金表は一日で姿を消し」/EN「that fee schedule disappeared in one … |
| 31 | hor-p2r2-07 | hormuz/j7gv | 軽微 | HF-002 | JA+EN共通残存 | 保留として記録 | hormuz-j7gv-P1(料金所比喩) | ○ | - | JA「かなり大きな料金所です。」/EN「It would be quite a large toll booth.」… |
| 32 | hor-p2r2-08 | hormuz/j7gv | 軽微 | HF-009 | JA+EN共通残存 | 未検出 | - |  | K | JA「第三幕で原油市場が見せた反応は、もっと冷静でした。」/EN「…the reaction from the oi… |
| 33 | hor-c-01 | hormuz/byz5 | 軽微 | HF-009 | JA+EN共通残存 | 未検出 | (byz5-P2と文共有) | ○ | D | JA「記事の時点では二点六パーセント高の一バレル八十五ドル超」/EN「they were up 2.6 percen… |
| 34 | sewer-p2r1-01 | sewer/87tc | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | U | JA「地下の管で全員をつなぐ作戦から、地域によっては家ごとに処理する作戦へ。」/EN「The strategy is… |
| 35 | sewer-p2r1-02 | sewer/87tc | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | K | JA「町の形に合わせて、汚水のルートを組み替えたわけです。」/EN「In other words, the city… |
| 36 | sewer-p2r1-03 | sewer/87tc | 軽微 | F-007 | JA+EN共通残存 | 未検出 | - |  | U | JA「家々を地下の管でつなぎ、まとめて処理する集合処理。」/EN「One is collective treatme… |
| 37 | sewer-p2r1-04 | sewer/87tc | 軽微 | F-007/F-012 | EN新規 | 未検出 | - |  | U | EN In one line「Towns are rethinking wastewater treatment b… |
| 38 | sewer-p2r1-05 | sewer/87tc | 軽微 | F-007 | EN新規 | 未検出 | - |  | U | EN「In areas where homes are spread out, septic tanks insta… |
| 39 | sewer-p2r1-06 | sewer/87tc | 軽微 | F-001 | JA+EN共通残存 | 未検出 | - |  | D | JA「下水道管路の総延長は…約五十万キロ。そのうち…約四万キロ、約七パーセント」/EN「The total leng… |
| 40 | sewer-p2r2-01 | sewer/g8qg | 軽微 | F-010 | JA+EN共通残存 | 再採点でNG | sewer-g8qg-01 |  | - | JA「そこで松山市が考えたのは、街全体を同じ方法で処理するのではなく、家の集まり方に合わせて作戦を変えることです。」… |
| 41 | sewer-p2r2-02 | sewer/g8qg | 軽微 | F-007/F-010 | JA+EN共通残存 | 再採点でNG | sewer-g8qg-01 |  | - | JA「街の人口密度が、汚水の進路を決めるわけです。」/EN「The population density of th… |
| 42 | sewer-p2r2-03 | sewer/g8qg | 軽微 | F-007/F-010 | JA+EN共通残存 | 再採点でNG | sewer-g8qg-01(同系統の因果主張) | ○ | - | JA「トイレを流すたびに、街の形と人口の変化が、地下の仕組みにまで影響している。」/EN「Every time we… |
| 43 | sewer-p2r2-04 | sewer/g8qg | 軽微 | F-010 | EN新規 | 再採点でNG | sewer-g8qg-01(one-liner同主張) | ○ | - | EN In one line「Matsuyama City will choose shared sewers or… |
| 44 | sewer-p2r2-05 | sewer/g8qg | 軽微 | F-007 | JA+EN共通残存 | 未検出 | - |  | U | JA「汚水を街の地下に張りめぐらせた管で集める」「みんなの汚水を一つの流れに乗せる」/EN「collected th… |
| 45 | sewer-p2r2-06 | sewer/g8qg | 軽微 | F-005/F-010 | EN新規 | 未検出 | - |  | D | JA「合併処理浄化槽」→EN「household wastewater treatment tanks」「septi… |
| 46 | sewer-ctl-01 | sewer/4hgy | 軽微 | F-012 | JA+EN共通残存 | 保留として記録 | sewer-4hgy-p1(見出し引っ越し) |  | - | JA「下水道に、引っ越し作戦が持ち上がっています。」/EN「A move is being planned for … |
| 47 | sewer-ctl-02 | sewer/4hgy | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | K | JA「古くなった管に向き合いながら、地域に合う仕組みへ組み替える。」/EN「As communities deal … |
| 48 | sewer-ctl-03 | sewer/4hgy | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | U | JA「合併処理浄化槽を使う個別処理区域にします。浄化槽の設置費には、上乗せ補助を行う方針です。」/EN「the ci… |
| 49 | sewer-ctl-04 | sewer/4hgy | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | U | JA「背景には、地下で働く管の高齢化があります。」/EN「The reason is that the pipes … |
| 50 | sewer-ctl-05 | sewer/4hgy | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | U | JA「福島県喜多方市」/EN「Kitakata City in Fukushima Prefecture」 |
| 51 | sewer-ctl-06 | sewer/4hgy | 軽微 | F-012/F-007 | JA+EN共通残存 | 未検出 | - |  | U | JA「集合処理区域では、地下の管を通して汚水をまとめて処理します。」/EN「In areas with shared… |
| 52 | sewer-ctl-07 | sewer/4hgy | 軽微 | F-001 | JA+EN共通残存 | 未検出 | - |  | D | JA「全国の下水道管路は、およそ五十万キロ」/EN「Japan’s sewer pipes total about … |
| 53 | ai-p2r1-01 | ai_control/b3ux | 重大 | EVID-008 | JAのみ残存 | 未検出 | - |  | K | JA「いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。」/EN「In other words, i… |
| 54 | ai-p2r1-03 | ai_control/b3ux | 軽微 | EVID-009 | JA+EN共通残存 | 未検出 | (b3ux-01と同EVID-009・近接文) | ○ | U | JA「プログラムの部品を公開しました。ところが、その部品は現実の公開場所に、およそ一時間置かれました。」/EN「it… |
| 55 | ai-p2r1-04 | ai_control/b3ux | 軽微 | CONTROL-002 | JA+EN共通残存 | 未検出 | - |  | D | JA/EN「確認すべきなのは、AIに十分な能力があるか。有害な目的で使う傾向があるか。そして、実際に使える道と機会が… |
| 56 | ai-p2r1-05 | ai_control/b3ux | 軽微 | EVID-008/011 | JA+EN共通残存 | 未検出 | - |  | K | JA「今回示されたのは、条件がそろうとAIがかなり遠くまで進めることです。」/EN「What this showed… |
| 57 | ai-p2r1-06 | ai_control/b3ux | 軽微 | EVID-008 | JA+EN共通残存 | 未検出 | - |  | D | JA「自分から世界征服を考えたわけでも、評価環境から逃げようと計画したわけでもありません。」/EN「It did n… |
| 58 | ai-p2r1-07 | ai_control/b3ux | 軽微 | EVID-008/011 | JA+EN共通残存 | 未検出 | - |  | K | JA「でも、この事件の意外な主役は、AIではありません。舞台装置です。」「…問われているのは、AIの賢さだけでなく、… |
| 59 | ai-p2r2-01 | ai_control/cupe | 軽微 | EVID-008 | JAのみ残存 | 未検出 | - |  | D | JA「AIは、用意された世界の中で敵を探し、課題をクリアするつもりでした。」/EN(Rewrite前)「The AI… |
| 60 | ai-p2r2-02 | ai_control/cupe | 軽微 | なし(EVID-008のCT… | JA+EN共通残存 | 未検出 | - |  | K | JA「これは、ネット上に隠された情報を探す宝探しのような競技です。」/EN「It is a treasure hun… |
| 61 | ai-p2r2-03 | ai_control/cupe | 軽微 | EVID-008 | JA+EN共通残存 | 未検出 | - |  | K | JA「ところが、ゲーム会場の設計に穴がありました。」/EN「There was a hole in the desi… |
| 62 | ai-p2r2-04 | ai_control/cupe | 軽微 | EVID-008 | JA+EN共通残存 | 未検出 | - |  | K | JA「世界征服の始まりというより、ゲーム会場の扉を閉め忘れた事件です。」/EN「So this was less t… |
| 63 | ai-p2r2-05 | ai_control/cupe | 軽微 | EVID-008 | JA+EN共通残存 | 未検出 | - |  | D | JA「その結果、ゲームの中で動いているはずのAIが、三つの組織の実際のシステムに不正に触れられる状態になりました。」… |
| 64 | ai-p2r2-06 | ai_control/cupe | 軽微 | CONTROL-003 | JA+EN共通残存 | 再採点でNG | ai_control-cupe-01 |  | D | JA「関連する評価では、最新の内部テストモデルが標的を実在すると認識した時点で停止しました。」/EN「In a re… |
| 65 | ai-p2r2-08 | ai_control/cupe | 軽微 | EVID-008 | EN新規 | 未検出 | - |  | D | EN最終「There was a hole in the design of the game site. It a… |
| 66 | ai-ctl-01 | ai_control/cfqm | 軽微 | EVID-011 | EN新規 | 未検出 | - |  | D | JA「主に関わったのは、内部だけで使う研究用プロトタイプでした。」/EN「The main actors were … |
| 67 | ai-ctl-02 | ai_control/cfqm | 軽微 | CONTROL-002/EV… | JA+EN共通残存 | 未検出 | - |  | U | JA「特に、AIが有害な行動を取る傾向まで実証された、という意味ではありません。」/EN「In particular… |
| 68 | ai-ctl-03 | ai_control/cfqm | 軽微 | EVID-010/011 | EN新規 | 未検出 | - |  | U | EN In one line「The AI did not rebel; it bypassed isolated … |
| 69 | ai-ctl-04 | ai_control/cfqm | 軽微 | EVID-010 | JA+EN共通残存 | 未検出 | - |  | U | JA「壁の中に通路を見つけ、掲示板で攻略情報を交換していた」/EN「exchanged tips on a mess… |
| 70 | ai-ctl-05 | ai_control/cfqm | 軽微 | EVID-011 | JA+EN共通残存 | 未検出 | - |  | K | JA「隔離したつもりの部屋に、通路と鍵が残っていた」/EN「a passage and keys being lef… |
| 71 | sw-ctl-01 | space_weapons/bcgj | 軽微 | F-011 | JA+EN共通残存 | 未検出 | - |  | U | JA「第二は、衛星と地上の間で情報を運ぶ通信リンクです。」/ EN「The second is the commun… |
| 72 | sw-ctl-02 | space_weapons/bcgj | 軽微 | F-011 | JAのみ残存 | 再採点でNG | space_weapons-bcgj-03 |  | - | JA「第三は、衛星に指示を出す地上の設備です。」/ EN(Rewrite前)「The third is the gr… |
| 73 | sw-ctl-03 | space_weapons/bcgj | 軽微 | F-012 | JA+EN共通残存 | 未検出 | - |  | K | JA「通信を邪魔したり、地上の設備に影響を与えたりしても、衛星の力を使いにくくできる可能性があります。」/ EN「I… |
| 74 | sw-ctl-04 | space_weapons/bcgj | 軽微 | F-001 | JA+EN共通残存 | 未検出 | - |  | U | JA「ただし、正体はまだベールの中です。兵器の名前は分かりません。攻撃できるのかどうかも、何を標的にするのかも確認さ… |
| 75 | sw-p2r1-01 | space_weapons/493w | 軽微 | F-012/F-013 | JA+EN共通残存 | 未検出 | - |  | K | JA「そして、守る側のメニューはさらに幅広い。」/ EN「The defense menu is even wide… |
| 76 | sw-p2r1-02 | space_weapons/493w | 軽微 | F-001 | EN新規 | 未検出 | - |  | D | JA「敵対的な相手から統合軍を守る」→ EN「to protect joint forces from hostil… |
| 77 | sw-p2r2-01 | space_weapons/89wf | 重大 | F-001 | JAのみ残存 | 再採点でNG | space_weapons-89wf-01(重大) |  | - | JA「宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」/ EN(Rewr… |
| 78 | sw-p2r2-02 | space_weapons/89wf | 重大 | F-001 | JAのみ残存 | 再採点でNG | space_weapons-89wf-01(重大) |  | - | JA「今回の見どころは、宇宙戦争が始まったことではありません。宇宙の戸締まりをするための備えが、初めて表に出たことで… |
| 79 | sw-p2r2-03 | space_weapons/89wf | 軽微 | F-001/F-002 | JA+EN共通残存 | 再採点でNG | space_weapons-89wf-03 |  | - | JA「では、なぜ今この話が出てきたのでしょうか。背景には、米国が見ているロシアの対衛星能力があります。」/ EN「S… |
| 80 | sw-p2r2-04 | space_weapons/89wf | 軽微 | F-001/F-011 | JA+EN共通残存 | 未検出 | - |  | D | JA/EN「ここで重要なのが、スペースコントロールという言葉です。…でも、カウンタースペースという考え方は、もっと広… |
| 81 | sw-p2r2-05 | space_weapons/89wf | 軽微 | F-001 | JA+EN共通残存 | 再採点でNG | space_weapons-89wf-02(EN one-liner分のみ) | ○ | - | JA「今回の見どころは、宇宙戦争が始まったことではありません。」/ EN本文「What is noteworthy … |
| 82 | sw-p2r2-06 | space_weapons/89wf | 軽微 | F-001 | JA+EN共通残存 | 未検出 | - |  | U | JA「米国が今回認めた発表でも、具体的なシステム名や標的、攻撃能力までは明らかにされていません。」/ EN「Even… |

## 6. 限界

- 突合は単独LLM判断(人間未確認)。『同じ文・同じ誤り』の同定、曖昧8件、性質ラベル(D/K/U)は私見。
- 元評価の項目粒度(1文1項目)と再採点の粒度(同一誤りを束ねる、例 g8qg-01=元4項目)が異なるため、NG件数の比(82→11)にはこの粒度差も含まれる。項目単位の一致13/82は『再採点NGが元項目を覆う割合』であり、『元項目が正しいかどうか』を示さない。
- 元評価の項目が正当なNGか否か(どちらの物差しが真値に近いか)は本表では判定していない。人間判定(E2: 重大候補5件+不一致約10件)が必要。
- 再採点の保留23件のうち元項目と対応したのは5件(保留分類)。残りの保留18件は元⑤bに対応項目がない別論点(元に無い項目、またはR0のみ)。
