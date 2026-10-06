# labels_w3 ノート(委任_06-W3、担当: bgroup_B3 / neg2_meta_refresh_a2 / neg3_hormuz_prodrunner_b1b、48 claim)

性質: Sonnet推測ラベル(label_source=sonnet_w3_2026-10-06、confirmed_by空欄=Fable/ユーザー確認前)。判定前にfloor/AI判定列は見ていない(claim_text/fact_id/run/cycleのみの作業用シート)。Ledgerはs2c `build_eval_groups()`のfixture ledger_text(各instanceの初回article)を使用。

運用メモ: rewrite_neededは「Rewrite対象だったか」の列が判定列側にしかないため、基準書§1-2に従い「重大/軽微ならY、問題なしならN」で記入(実際のRewrite対象との突合は集計script/Fable側)。bgroup_B3 cycle2の同一文(HF-011/HF-007の2行)はキー衝突のため片方に`|dup`接尾辞を付与。

## run別集計
| run | claim | 重大 | 軽微 | 問題なし | UNDECIDABLE | true_problem Y | true_problem N | true_critical Y |
|---|---|---|---|---|---|---|---|---|
| bgroup_B3 | 15 | 1 | 0 | 14 | 0 | 1 | 14 | 1 |
| neg2_meta_refresh_a2 | 14 | 0 | 0 | 12 | 2 | 0 | 12 | 0 |
| neg3_hormuz_prodrunner_b1b | 19 | 1 | 0 | 18 | 0 | 1 | 18 | 1 |
| 合計 | 48 | 2 | 0 | 44 | 2 | 2 | 44 | 2 |

## 重大Y・UNDECIDABLE全件
1. bgroup_B3 cycle1 / HF-007 / 重大 Y/Y
   claim: "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day."
   Ledger: HF-007 conditions「トランプ氏は、中東指導者との『非常に生産的な協議』に基づく決定だと説明」/HF-001 notes「撤回の原因として記述しない」/HF-011 conditions「撤回は同日、供給懸念は継続」。
   理由: 継続する懸念を撤回の原因とする因果で、Ledgerの説明理由と食い違う。**gold B3該当(so + flashy 20% plan)=true_critical Y**。
2. neg3 cycle1 / HF-009 / 重大 Y/Y
   claim: "The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned."
   Ledger: HF-009 conditions「撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた」/notes「観測されたのは一時的な上げ幅縮小と、その後の回復」。
   理由: 継続していた出来事を「戻った」と読ませる(見本B: 継続→消えて戻った)。価格の回復だけならHF-009と整合。時期gold(「prices began to fall」型の上げ幅縮小の変形)ではなく見本B型。
3. neg2 cycle1 / MUSE-HC-013 / UNDECIDABLE: "They enjoyed the ease of AI."(cycle2も同文、fact_id空)
   Ledger: HC-013は従業員反応が「圧倒的に肯定的」(広報担当者の説明)のみ。ユーザーがAIの手軽さを楽しんだ旨の記載なし。
   理由: 修辞的描写(問題なし)か、ユーザー感情の未確認Fact追加(軽微)かが曖昧。cycle1・cycle2の2行。

## gold該当文
- B3(bgroup_B3 cycle1 row1): 重大Y/Y(上記1)。cycle2/cycle3の「and the flashy 20% plan」版(3行)は因果接続語でなくtext_pattern非該当、HF-011 conditionsと整合のため問題なしN。
- neg3 HF-009型(prices began to fall等への変形): 該当文なし(「prices themselves quickly returned」はHF-009そのまま、問題なしN)。cycle1の「events ... returned」は上記2のとおり別型で重大。

## 境界例の所感【推測】
- neg3 cycle3 "On July 13, Trump posted that all cargo ... should provide a 20 percent reimbursement." は見本Bで同文がY/Y。現Ledger HF-002(すべての貨物に20%の率で償還を求める)とscope・主体・日付が一致するためNとしたが、見本との不一致なのでFable確認推奨。
- neg2 "It said that human staff made inappropriate comments about race..." は見本B(meta_run03_standard)と近い文だが、本文は「report from an employee」「only one report」で帰属を保持するため文脈を見てN。1 claim単位で「It said」のみで足りるかの運用判断はFable確認推奨。
- neg2 "they did not know that a human was on the other end" は線引き例A4-1に準じN。ユーザー全般への軽い拡張はあり、厳格に見れば軽微の可能性。
