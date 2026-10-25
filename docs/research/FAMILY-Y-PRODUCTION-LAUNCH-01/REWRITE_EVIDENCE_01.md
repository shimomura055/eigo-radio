# REWRITE_EVIDENCE_01: M-2(Closing局所書換え経路)のruntime evidence

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A / 2026-10-25(JST)。新規生成なし。過去にLeakage判定でFAILした本文を入力に、**Production版`run_gate`**(判定→局所書換え→再判定→`check_closing`)を実APIで通した。
実行: `er121_family_y_calibration_01.py rewrite`。生データ: `er110_output/family_y_production_launch_01/rewrite_evidence_01/`(最終版)・`rewrite_evidence_01_v1_without_scope_guard/`(範囲保全guard追加前の初回run)。
モデル: 判定=`gpt-6-luna` high(`FAMILY_Y_LEAK_JUDGE`)、書換え=`gpt-6.1-sol` medium(`FAMILY_Y_CLOSING_REWRITE`。新規追加key=02Bへ引継ぎ)。いずれも最新世代(Charter 25節)。

## 0. 結論

1. **書換え経路は実APIで動作した**: R2宅配H2(旧FAIL)で、判定FAIL→局所書換え→再判定→…→PASS、書換え後`check_closing`ok・記号検査ok(`rewrite_evidence_table.json`)。書換えpromptはPrompt 02の【最終パートの書き方】節(sha固定Promptから逐語切り出し)+選定済み切り口(`new_view`+`evidence_quotes`)+指摘情報。旧B骨格は使っていない。
2. **R1宅配gen_1は、M-1修正後の最初の判定でPASS(旧FAILの原因=定義欠落による過剰判定)のため書換え経路を通らなかった**(書換え0回=Fable指定の2入力のうち1入力では経路が発火しない。これ自体が較正結果の一部)。書換え経路の発火確認はH2の1件(2回の書換えを含む)で取った。
3. **発見した不具合と対策(初回runで発見→修正→再run)**: 初回run(guardなし)では、書換えが**指摘箇所以外の文まで書き換え、語りの出所(誰の言葉か)を変えた**(第1文『…と、営業所を使う受取人は言う』→『…と配達員は言う』)。M-2の『指摘箇所だけ直す』を、promptの強調に加えて**決定論guard**(`rewrite_scope_check`: 判定器が引用した箇所を含む文以外は、書換え後も一字違わず同順で残ること。違反は`REWRITE_SCOPE_VIOLATION`→2回続けば`REWRITE_STOP`)で強制した。再runでは第1〜3文が一字違わず保存された。

## 1. R2宅配H2(旧FAIL: `leak_discovery_syntax`『見えてくる』+`leak_tension_reverts_to_research`)

入力(旧FAIL稿 `er110_output/family_y_closing_general_02/redelivery_fee/gen_high_2/closing_final.txt`):

> 「受け取り方を考えて手間をかけている」と、営業所を使う受取人は言う。時間を指定して待っても、営業所で受け取ろうとしても、予定通りにいかないことがある。再配達になったかどうかという結果だけでは、受け取ろうとした手間までは分からない。受け取るためにかけた手間も認めてほしいという思いが、料金の話から見えてくる。あなたが最近荷物を受け取った場面なら、再配達料を決める人にどんな手間を伝えたい？

### 初回run(範囲保全guardなし): 判定2回(FAIL→書換え1回→PASS)

> 配り直す手間を、料金全体で受け止めたいと配達員は言う。時間を指定して待っても、営業所で受け取ろうとしても、予定通りにいかないことがある。再配達になったかどうかという結果だけでは、受け取ろうとした手間までは分からない。料金の話には、受け取る側の手間も認めてほしい思いが重なるのかもしれない。あなたが最近荷物を受け取った場面なら、再配達料を決める人にどんな手間を伝えたい？

- 第1文の出所が『営業所を使う受取人』→『配達員』に変わり、第4文も大きく変わった(指摘は第5文『…見えてくる』のみ)。**採用しない**(guard追加の根拠)。実費 2.641円。

### 最終run(guardあり、現行コード): 判定3回(FAIL→書換え→FAIL→書換え→PASS)

> 「受け取り方を考えて手間をかけている」と、営業所を使う受取人は言う。時間を指定して待っても、営業所で受け取ろうとしても、予定通りにいかないことがある。再配達になったかどうかという結果だけでは、受け取ろうとした手間までは分からない。配るきつさに、待った手間や受け取り方を選んだ手間が重なる。どの手間を料金で受け止めてほしいかが、違う答えにつながっていそうだ。あなたが最近荷物を受け取った場面なら、再配達料を決める人にどんな手間を伝えたい？

| 判定 | 結果 | 書換え |
|---|---|---|
| 1回目 | `leak_discovery_syntax` FAIL(引用『…思いが、料金の話から見えてくる。』) | 1回目の書換え: guard checked=true, 対象文idx=[3], 違反0 |
| 2回目 | `leak_tension_reverts_to_research` FAIL(『受取人一人の手間と読者への問いにとどまり…』) | 2回目の書換え: 対象文idx=[3,4], 違反0 |
| 3回目 | PASS | — |

- 書換え後`check_closing`: ok(違反0)。最終sha `2cfc6f38…`、旧稿sha `9312bb60…`。`closing_record`に書換え有無・生成時sha・最終shaを記録する設計(`produce_closing`、testで固定)。
- 注意(開示): 1回目の書換えで『見えてくる』は消えたが、書換え文が**1人(営業所を使う受取人)の話に寄った**ため2回目に`leak_tension_reverts_to_research`でFAILした。3判定(上限)の最後でPASS=**余裕のないPASS**。『一人の語りに寄る』傾向は一般化Closingの既知課題(Round 2のSNS M1型)と同系。判定は3回の上限内(承認範囲)。実費 5.737円。

## 2. R1宅配gen_1(旧FAIL: `leak_evidence_subject` =『〜という声があった』)

- 入力sha `229ee99b…`。M-1修正後prompt(Production版)の**最初の判定でPASS**(書換え0回、`n_judgements=1`)。GATE_CALIBRATION_01の通り、同稿は新promptで0/3 FAIL(定義補完で解消)。
- 結果: 経路は『判定のみ』で完了。`check_closing`ok。書換え経路の追加evidenceは不要(H2で取得済み)。

## 3. 範囲保全guardの性質(Fable確認事項)

- 新規の品質検査を足したわけではなく、**M-2『指摘箇所だけ直す』(Opus指摘・Fable確定)の機械的強制**。承認済みGate基準・Prompt 02の文言には触れていない。
- 副作用: 書換えが引用箇所以外を変えると`REWRITE_STOP`が増えうる。引用箇所を本文中に特定できないとき(`checked=false`)は検査せず、書換え後の再判定+`check_closing`に委ねる。
- 解除条件: 運用実績で偽の`REWRITE_STOP`が多いとFableが判断した場合に、対象文の判定を緩める(要Fable判断。本委任では緩めない)。

## 4. 実費

- `rewrite_evidence_01`(最終run)5.737円 + `rewrite_evidence_01_v1_without_scope_guard`(初回run)2.641円 = **8.378円**。
