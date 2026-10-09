# RESULT_TABLE_01: 結果表(委任_02、事前登録 PREREGISTRATION_01.md 0-R の式を機械適用。自動生成 aggregate_01.py)

Model A=gpt-6-luna(主評価者)、Model B=gpt-5.6-luna(同じLuna系の参考第2評価者。別vendorではない)。各セルは `label / misread_type / reason(先頭34字)`。

## 表1: ケース別判定

| K | case_id | Fact(短縮) | Writer文(短縮) | Model A rep1 | Model A rep2 | Model B rep1 | Model B rep2 | 人間既知 | Checker参考 | A-B一致(rep1 / rep2) | 期待との照合(Model A rep1/rep2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K01 | y84g5r | MetaのSuperintelligence Labs部門の副社長は、適切な開示 | The company also restored the human concierge feature to the | B / その他 / ロールバックの言い換えは妥当だが、「human concierge  | A / なし / 機能を当面ロールバックしたことを、以前の状態に戻したと言い換えている | A / なし / 機能を以前の状態に戻し、当面継続したという内容で台帳Factと一致す | A / なし / 機能を当面ロールバックしたという事実を、以前の状態に戻したと自然に言 | ユーザー確認済み(C、2026-10-09) | 見逃し: 機械候補(negation_polarity_mi | 不一致(B-A) / 一致(A) | 期待C: B/A |
| K02 | ur5649 | Anthropic reported that a review of 141, | Nor has anyone reported that an AI got out of the test envir | B / その他 / 「テスト環境から出た」の意味が曖昧で、報告がないとの断定も台帳にはな | B / その他 / 「外に出た」の意味が曖昧で、報告がないという断定も台帳では確認できな | B / その他 / 台帳は意図的な脱出否定であり、誰も報告していないとの不在断定は支えな | B / その他 / 脱出の報告がないという不在を断定しており、台帳の「脱出を試みなかった | ユーザー確認済み | 見逃し: Stage1 dev=MAJOR(scope拡大・ | 一致(B) / 一致(B) | 期待C: B/B |
| K03 | hdr8y4 | MetaのSuperintelligence Labs部門の副社長は、適切な開示 | They also temporarily put back the feature in which humans h | B / その他 / ロールバックの対象や復元内容は台帳に明記されず、人間対応機能の復活と | B / その他 / ロールバックを「人間が通話を担当する機能」と具体化しており、その説明 | C / 肯定否定方向反転 / 台帳は機能を一時ロールバックしたとしており、対象文は一時的に復活させ | C / 肯定否定方向反転 / 台帳は人間が電話する機能をロールバックしたと述べるが、対象文は一時的 | ユーザー確認済み(C、2026-10-09) | Checkerではなく旧Deviation Check: v | 不一致(B-C) / 不一致(B-C) | 期待C: B/B |
| K04 | yjjmk8 | MetaのSuperintelligence Labs部門の副社長は、適切な開示 | Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻し | B / その他 / 「人間コンシェルジュ機能」という特定は台帳に明記されていない。 | B / その他 / 「人間コンシェルジュ機能」という具体的な機能名は台帳Factにありま | A / なし / 幹部への一般化は許容範囲で、ミスの認定と機能の当面のロールバックも一 | A / なし / 副社長を幹部とし、機能名を補っているが、ミスの認定とロールバックの内 | Sonnet暫定(未ラベル) | なし(JA R0はChecker未適用) | 不一致(B-A) / 不一致(B-A) | 期待B?: B/B |
| K06 | 7b6trp | 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行 | But the name of the device and exactly what it can do in an  | B / その他 / 名称や攻撃能力が公表されていないとの断定は台帳Factにない。 | B / その他 / 兵器の名称や攻撃時の能力が公表されていないとの断定は台帳にない。 | B / その他 / 兵器の名称や攻撃能力が未公表という点は台帳に記載されていない。 | B / その他 / 兵器名や攻撃能力が未公表とは台帳に記載されておらず、不在・非公開を追 | Sonnet暫定(ユーザー未裁定) | 最終EN本文に残存(residual_miss。Checke | 一致(B) / 一致(B) | 期待B?: B/B |
| K08 | 6urnmg | トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、 | Trump announced that he would drop the 20 percent fee plan a | A / なし / 投稿内容を「発表」と言い換え、償還料を貿易・投資案件に置き換える意味 | A / なし / 20％の料を貿易・投資案件に置き換える投稿の内容を保っている。 | A / なし / 20％の料金を湾岸諸国との貿易・投資案件に置き換える内容で、台帳の言 | A / なし / 20％の料を取りやめ、湾岸諸国と米国の貿易・投資案件に置き換える内容 | ユーザー確認済み(A、2026-10-09)。履歴: Sonnet暫定( | 当該文は候補化されず(local_contextとして登場の | 一致(A) / 一致(A) | 期待A: A/A |
| K09 | sq5c2g | ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホ | On July 13, Trump posted that all cargo passing through the  | A / なし / 海峡を通る全貨物に20％の償還を求めるという内容を保っている。 | B / その他 / 費用の償還を求めたという文脈が省かれ、20％の算定対象が曖昧。 | A / なし / 全貨物に対し20％の償還を求めるという内容を概ね正確に言い換えている | A / なし / 米国が全貨物に20％の償還を求める内容を、貨物が償還すると言い換えて | ユーザー確認済み(A、2026-10-09)。履歴: Sonnet暫定( | 未確認(参考なし) | 一致(A) / 不一致(B-A) | 期待A: A/B |
| K10 | 7suvyn | Anthropic reported that a review of 141, | But because of a setup mistake, it was able to connect to th | A / なし / 設定ミスで外部インターネットに到達したという要約は、環境の誤設定と整 | A / なし / 環境設定の不備によりモデルが外部インターネットへ接続したという範囲内 | A / なし / 設定ミスによりモデルが外部インターネットへ接続したという事実に沿って | A / なし / 設定ミスでモデルが外部インターネットに接続したという内容は台帳Fac | Sonnet暫定(因果語を含むため境界へ移動) | Stage1で候補化(causal_not_in_fact, | 一致(A) / 一致(A) | 期待B?: A/A |
| K11 | z63yng | 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行 | 宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。 | B / その他 / 統合軍の防護を、宇宙・通信・地上設備の防護と具体化しており、範囲の拡 | B / その他 / 公に認めた点は合うが、宇宙・通信・地上設備を守るとの対象は台帳にない | B / その他 / 兵器の配備を、宇宙・通信・地上設備を守る仕組みと広げて表現している。 | B / その他 / 公に認めた点は一致するが、保護対象を宇宙・通信・地上設備へ広げている | ユーザー判断(C寄り・Bの余地あり、2026-10-09) | JA文のためChecker評価対象外(Checkerはなし  | 一致(B) / 一致(B) | 期待C or B: B/B |
| K12 | 9ywt6e | MetaのSuperintelligence Labs部門の副社長は、適切な開示 | The human concierge feature was then put on hold for the tim | A / なし / 機能を当面ロールバックしたことを「当面保留」と言い換えている。 | A / なし / 機能を当面ロールバックしたという内容と、当面保留にしたという表現は同 | A / なし / 機能を当面ロールバックしたという台帳の内容を、保留したと自然に言い換 | A / なし / 機能を当面ロールバックしたという事実を、言い換えて表現している。 | ユーザー確認済み(A、2026-10-09)。履歴: Sonnet暫定( | 記事は最終PASS系(当該文でCheckerが候補化したかは | 一致(A) / 一致(A) | 期待A: A/A |

(人間既知・Checker参考の全文は `CASES_01.md`。Checkerは正解扱いしない。)

## 表2: 事前登録指標

| 指標 | gpt-6-luna(主・判定に使用) | gpt-5.6-luna(参考集計) |
|---|---|---|
| M1 K01,K02,K03 x rep1,rep2 (K01r1,r2,K02r1,r2,K03r1,r2) | B,A,B,B,B,B -> REJECTED | A,A,B,B,C,C -> REJECTED |
| M2 K08,K09,K12 x rep1,rep2 (K08r1,r2,K09r1,r2,K12r1,r2) | A,A,A,B,A,A: B/C=1, C=0 -> PASS | A,A,A,A,A,A: B/C=0, C=0 -> PASS |
| M4 自己一致(rep1=rep2, 10ケース) | 8/10, 不一致: K01,K09 | 10/10, 不一致: なし |
| 実効temperature | unspecified(rejected) | unspecified(rejected) |

## 表3: 2評価者の不一致(M3、参考)と人間確認対象(定義1=不一致のみ、定義2=不一致+両B)

| 比較 | M3 不一致件数(case_id) | C不一致(片方がC他方C以外) | 両B件数(case_id) | 確認対象 定義1 | 確認対象 定義2 |
|---|---|---|---|---|---|
| rep1(6luna-vs-5.6luna) | 3/10 (K01,K03,K04) | 1 (K03) | 3 (K02,K06,K11) | 3/10 | 6/10 (K01,K02,K03,K04,K06,K11) |
| rep2(6luna-vs-5.6luna) | 3/10 (K03,K04,K09) | 1 (K03) | 3 (K02,K06,K11) | 3/10 | 6/10 (K02,K03,K04,K06,K09,K11) |
| 6luna rep1-vs-rep2 | 2/10 (K01,K09) | 0 (-) | 5 (K02,K03,K04,K06,K11) | 2/10 | 7/10 (K01,K02,K03,K04,K06,K09,K11) |
| 5.6luna rep1-vs-rep2 | 0/10 (-) | 0 (-) | 3 (K02,K06,K11) | 0/10 | 3/10 (K02,K06,K11) |

## 表4: ラベル分布(各10判定)

- gpt-6-luna rep1: A=4 B=6 C=0 N/A=0
- gpt-6-luna rep2: A=4 B=6 C=0 N/A=0
- gpt-5.6-luna rep1: A=6 B=3 C=1 N/A=0
- gpt-5.6-luna rep2: A=6 B=3 C=1 N/A=0

## 表5: 事前登録式のStatus(機械割当)

- (主) M1/M2/M4: M1段階=REJECTED、M2=PASS、gpt-6-luna M4=8/10 -> **REJECTED**
- (参考) 元3節の表にM3(6luna vs 5.6luna、rep別の大きい方=3件)を当てはめた場合 -> **REJECTED**
- いずれもProduction採用ではない。大規模Writer比較Trialへ直行しない。最終Status判定はFable。

## 表6: 任意ブロック(合否外、gpt-6-luna 1rep、方式A、22文)

| case_id | idx | 対応Fact | 対応品質 | 文(短縮) | label / misread_type / reason |
|---|---|---|---|---|---|
| ob01 | 2 | F-001 | weak | But the key to understanding this news is not how powerf | B / その他 / 兵器の威力が理解の鍵ではないという解釈は、台帳Factには示されていない。 |
| ob02 | 3 | F-001 | weak | It is its address. | B / その他 / 「It is its address」は意味が不明瞭で、兵器の配備場所を述べてい |
| ob03 | 5 | F-011 | weak | Once we make that distinction, the story becomes much ea | B / その他 / 区別によって話が追いやすくなるという評価は台帳Factに記載されていない。 |
| ob04 | 6 | F-001 | direct | The U.S. Secretary of the Air Force said that the U.S. i | A / なし / 軌道上への宇宙管制兵器の配備と、敵対的行動から米軍を守る目的を保っている。 |
| ob05 | 7 | F-001 | direct | An official U.S. government article describes this state | B / その他 / 「初めて認めた」は合うが、「公に」は台帳に明記されていない。 |
| ob06 | 8 | F-001 | partial | But the name of the device and exactly what it can do in | B / その他 / 台帳にない「名称や攻撃時の能力は公表されていない」と断定している。 |
| ob07 | 9 | F-001 | partial | So we know the weapon’s address, but its details are sti | B / その他 / 軌道上への配備は述べられているが、兵器の具体的な所在が判明しているとは記されてい |
| ob08 | 10 | F-003 | partial | There is a past example of a weapon that destroys satell | A / なし / 衛星を破壊した兵器の過去例という内容で、台帳Factの範囲内。 |
| ob09 | 11 | F-003 | direct | In 2021, Russia launched a missile from the ground and d | A / なし / 地上発射ミサイルで衛星を破壊したという事実の範囲内で、詳細を省略している。 |
| ob10 | 12 | F-003 | direct | This was a case of a weapon based on the ground being fi | A / なし / 地上発射型の兵器が発射されたという意味で、台帳Factの範囲内。 |
| ob11 | 13 | F-001 | direct | The statement this time is about weapons themselves bein | A / なし / 軌道上に宇宙管制兵器を配備したとの発言を述べている。 |
| ob12 | 14 | F-003 | partial | “A weapon that destroys satellites” and “a weapon in orb | A / なし / 衛星を破壊する兵器と軌道上の兵器は同一とは限らないという区別は、台帳Factと矛 |
| ob13 | 15 | F-011 | partial | Also, the phrase “operations to counter actions in space | A / なし / counterspace operationsの意味が広いという要約で、台帳の定 |
| ob14 | 16 | F-011 | direct | The U.S. Space Force says it includes not only activity  | A / なし / 軌道・リンク（衛星との通信）・地上の各セグメントを含むという内容の言い換え。 |
| ob15 | 17 | F-012 | partial | In other words, whether or not there are weapons in spac | A / なし / 軌道上の攻撃だけでなく通信への妨害や地上攻撃も含むというFactの範囲内。 |
| ob16 | 18 | F-015 | direct | GPS, missile tracking, watching what is happening in spa | A / なし / 任務の列挙は台帳Factの内容を言い換えた範囲内。 |
| ob17 | 19 | F-015 | partial | We need to think about the work of using and protecting  | A / なし / 衛星の運用・保護と攻撃用兵器の軌道上配備を区別しており、台帳の趣旨に沿う。 |
| ob18 | 22 | F-016 | direct | It bans putting nuclear weapons and other weapons of mas | B / その他 / 禁止対象の列挙から「宇宙兵器全般は禁止されない」とするのは台帳にない断定。 |
| ob19 | 23 | F-017 | partial | That does not mean this deployment has been ruled legal, | B / その他 / 特定の配備が合法と判断されていないという情報は、台帳Factにはない。 |
| ob20 | 24 | F-017 | partial | This rule alone does not let us make a judgment about th | B / その他 / 台帳は国際法に従う義務を述べるが、この規定だけで個別事案を判断できないとは述べて |
| ob21 | 26 | F-001 | weak | Rather than deciding what happened in space right away,  | A / なし / 事実の内容を変えず、用語から読み始めるという編集上の提案にとどまる。 |
| ob22 | 27 | F-001 | direct | The U.S. says it has placed weapons in orbit, though wha | B / その他 / 兵器の目的は台帳に記されており、「何ができるか不明」は不明さを言い過ぎる可能性が |

- 件数: A=12 B=10 C=0 N/A=0 (計22)
- 記事1本あたりの確認対象数: C+B(+N/A) = 10 文 / 22文 (45%)
- 対応品質別(A/B/C/N/A): direct=6/3/0/0; partial=5/4/0/0; weak=1/3/0/0
- A文への過剰B率: 対応品質direct 9文中B=3 (33%)。参考: 全22文中B=10 (45%)
- partial/weakでのB/Cは『対応付け不良由来』か『文の逸脱』か区別が必要(reasonを人が確認する)。

## 表7: 実費(usage実測x登録単価)・形式違反・再呼び出し

| run | 試行数 | 採用(例外除く) | 形式違反数 | API例外試行 | input tok | output tok | reasoning tok | 実費(円) | temperature |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna rep1 | 10 | 10 | 0 | 0 | 10537 | 2859 | 2292 | 0.397 | unspecified(rejected) |
| gpt-6-luna rep2 | 10 | 10 | 0 | 0 | 10537 | 2365 | 1805 | 0.250 | unspecified(rejected) |
| gpt-5.6-luna rep1 | 10 | 10 | 0 | 0 | 10537 | 1559 | 969 | 0.637 | unspecified(rejected) |
| gpt-5.6-luna rep2 | 10 | 10 | 0 | 0 | 10537 | 1853 | 1242 | 0.478 | unspecified(rejected) |
| optional_block_gpt-6-luna rep1 | 22 | 22 | 0 | 0 | 23360 | 4015 | 2798 | 0.695 | unspecified(rejected) |

- 実費合計: 約 JPY 2.458(本体 1.763 / 任意ブロック 0.695。登録単価x実usage。見積: 本体 4.7-23.2円 + 任意 1.57-7.55円)。
