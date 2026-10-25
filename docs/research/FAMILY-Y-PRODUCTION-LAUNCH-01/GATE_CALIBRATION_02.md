# GATE_CALIBRATION_02: `leak_discovery_syntax` 判定定義の補足(ユーザー正式承認 USER_03 §2)の較正

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05 / 2026-10-25(JST)。有料=判定のみ(gpt-6-luna high、生成・書換えなし)。実費は§6。
実行: `er121_family_y_calibration_02.py run|table`(証跡用runner。Production経路から参照されない)。生データ: `er110_output/family_y_production_launch_01/calibration_02/`(`judgements/`=v1、`judgements_v2/`、`judgements_v0/`、`calibration_table_02.json`、`raw_usage_log*.jsonl`、`stop_check_*.json`)。変更前データは`calibration_01`を再利用。

## 0. 結論(先に)

1. **採用した補足文言はユーザー承認原文の一文だけ**: 「Prompt指示に基づく『〜から見えてくる』という提示表現は解釈語と見なさない。」(Tension判定promptの`leak_discovery_syntax`定義の末尾。Closing判定のみ。Voice判定・Lead/人物紹介の補助判定・DEV・他Familyは不変。Prompt 02は1バイトも変えていない)。
2. **委任文にあった後半「ただし、3人の語りに根拠がない解釈、不要な一般化、研究・調査の説明への逆戻りは引き続きFAIL。」は採用しなかった**(v1)。較正で、この後半を足すと`leak_discovery_syntax`判定が「一般化」を理由に広がり、**案B(承認本文)が3回すべて`leak_discovery_syntax`でFAIL**(v0=補足なしでは0/3、v2では0/3)になった。これは USER_03 §1 の救済条件(FAIL項目が`leak_evidence_memorable`のみ)を満たさず、案Bが**STOP**する。無関係な本文の誤FAILも増えた(過去本文のdiscovery FAIL: v0 4/42 → v1 10/42 → v2 2/42)。「引き続きNG」の担保は文言ではなく、既存の他項目(不変)が判定すること(§3-3)。ユーザー承認原文の補足一文は「必要最小限の定義変更」(USER_03 §2)にも合致する。
3. **狙いの効果は出た**: 過去の「見えてくる」型FAIL(R2宅配H2)は`leak_discovery_syntax` FAIL 3/3(補足なし・今回対照も3/3)→ **0/3**。R2宅配medium_1(1/3)→ 0/3。合成正例(根拠ある『見えてくる』)は 補足なし2/3 FAIL → 0/3。
4. **「表現だけでPASSしない」**: 『見えてくる』を使った合成負例(根拠なし一般化N1・調査説明N2)は補足後も**3/3 FAIL**。N2・N3は`leak_discovery_syntax`でも3/3 FAIL。N1は`leak_discovery_syntax`のFAILが消えるが、`leak_evidence_memorable`/`leak_tension_reverts_to_research`で3/3 FAIL(補足は『見えてくる』という表現そのものを減点しないだけで、根拠なし一般化を通さない)。
5. **残る懸念(隠さない)**: 補足あり(v1・v2とも)では、補足なしで安定して0 FAILだった本文に、別項目のFAILが散発的に出た(v2: R2宅配high_1 `leak_discovery_syntax` 2/3(『ありそうだ』)、案A最終 `leak_tension_reverts_to_research` 2/3、R1宅配gen1 `leak_binary_camp_split` 1/3、案B `leak_evidence_memorable` 2/3)。補足なし対照(v0)で同じ12本が 0/36 FAIL なのに対し v2 は 7/36(§4)。判定器の揺らぎと補足による判定の摂動を分けるには n が足りない。ただし**FAILの総数は過去本文42回で v0 4 → v2 7(H2の誤FAIL3回分が消えた上で)**であり、一貫した悪化とは言えない。n=3のため統計的な断定はしていない。Closing本文のFAILは局所書換え(判定<=3)で扱われる既存機構の範囲。

## 1. 方法

- 変更後の判定prompt: `er121_family_y_text_core_01.build_leak_prompt('tension')`(補足を`leak_discovery_syntax`定義の末尾に付加)。prompt shaは判定ファイルに記録(v2の判定promptのshaがProduction `build_leak_prompt('tension')` と一致することを案B判定ファイルで実測確認)。
- 対象18本(各3回): 過去Closing 14本(Round 1/2の10本・案A初回・案A最終・案B・案C)+手書き合成4本(生成していない短文: 負例3=N1根拠なし一般化『見えてくる』・N2調査説明『見えてくる』・N3『明らかになった』型発見報告、正例1=P1根拠ある『見えてくる』)。判定器はClosing本文だけを見る(本番と同じ。Voice本文は渡さない)。
- 比較: 変更前=`calibration_01`の判定(再利用、補足なしのM-1 prompt)/ **v0=補足なしを今回同時期に再判定した対照**(判定器の揺らぎ・時間差と補足の効果を分ける)/ v1=委任文の文言 / v2=ユーザー承認原文の一文(採用)。
- 使用モデル: 判定=`gpt-6-luna`(effort high。既存`FAMILY_Y_LEAK_JUDGE`。Charter 25節: 評価ではなく本番判定器の較正であり、Production判定器と同一である必要があるため最新世代下位系を維持)。

## 2. 前後比較表(`leak_discovery_syntax`のFAIL数をdiscで併記。FAIL=いずれかの項目FAIL)

| 本文 | 種別 | 「見えて」 | 変更前(補足なし)旧データ calibration_01 | 補足なし 今回対照(v0) | v1(委任文の文言) | v2(採用: ユーザー承認一文) |
|---|---|---|---|---|---|---|
| R1_redelivery_fee_gen1 | past | あり | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 2/3(disc 2) | FAIL 1/3(disc 0) |
| R1_redelivery_fee_gen2 | past | - | FAIL 2/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| R1_sns_age_limit_gen1 | past | あり | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| R1_sns_age_limit_gen2 | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 1/3(disc 1) | FAIL 0/3(disc 0) |
| R2_redelivery_fee_high_1 | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 2/3(disc 2) |
| R2_redelivery_fee_high_2 | past | あり | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 2/3(disc 2) | FAIL 0/3(disc 0) |
| R2_redelivery_fee_medium_1 | past | あり | FAIL 1/3(disc 1) | FAIL 0/3(disc 0) | FAIL 1/3(disc 1) | FAIL 0/3(disc 0) |
| R2_sns_age_limit_high_1 | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| R2_sns_age_limit_high_2 | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| R2_sns_age_limit_medium_1 | past | - | FAIL 0/3(disc 0) | FAIL 1/3(disc 1) | FAIL 1/3(disc 0) | FAIL 0/3(disc 0) |
| A_v1_initial | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| B_fixed | past | - | FAIL 2/7(disc 0) | FAIL 0/3(disc 0) | FAIL 3/3(disc 3) | FAIL 2/3(disc 0) |
| A_final | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 1/3(disc 1) | FAIL 2/3(disc 0) |
| C_final | past | - | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |
| SYN_N1_ungrounded_generalization | negative | あり | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 0) |
| SYN_N2_research_reversion | negative | あり | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) |
| SYN_N3_discovery_report | negative | - | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) | FAIL 3/3(disc 3) |
| SYN_P1_grounded_presentation | positive | あり | FAIL 1/3(disc 1) | FAIL 2/3(disc 2) | FAIL 0/3(disc 0) | FAIL 0/3(disc 0) |

## 3. 読み方

1. **目的(過去の「見えてくる」型FAILの再判定)**: R2宅配H2 disc 3/3(変更前・v0対照とも)→ v2 0/3。medium_1 1/3 → 0/3。R1宅配gen1(『という声があった』型、`leak_discovery_syntax`で外側から報告する構文としてFAILし得る)はv1で2/3 FAILに悪化、v2は0/3(別項目1/3)。案A初回はFAILが消えている(変更前から0/3、元の記録のtension_reverts FAIL1回は揺らぎ)。
2. **根拠ある表現が表現だけでFAILしない**: 合成正例P1(根拠として人物の経験[不在票・料金への違和感]を示した上での『見えてくる』)は v0 2/3 FAIL(『見えてくる』が発見を報じる構文と判定された)→ v2 0/3。
3. **根拠なし解釈・Research逆戻りは引き続きFAIL**: N1=3/3(v2は`leak_evidence_memorable`+`leak_tension_reverts_to_research`)、N2=3/3(5項目)、N3=3/3(4項目)。補足はこれらを通さない。**限界**: N1は`leak_discovery_syntax`では捕捉されなくなる(『見えてくる』を解釈語と見なさない補足の意図どおり)。根拠なし一般化の捕捉は`leak_evidence_memorable`/`leak_tension_reverts_to_research`に依存する。判定器はこれらの項目で3/3 FAILしたが、合成1本・n=3の確認にとどまる。
4. **v1(委任文の後半付き)が不適切な理由**: 案B 3/3で`leak_discovery_syntax` FAIL(判定理由『語り手の根拠を示さず一般化しています』)=USER_03 §1の前提(案BのFAIL項目は`leak_evidence_memorable`のみ)を壊す。R1宅配gen1 2/3、R1 SNS gen2 1/3、案A最終 1/3 も同じ『一般化』理由で`leak_discovery_syntax`が増えた。判定器はVoice本文を見ないため『3人の語りに根拠がない』を検証できず、後半の追加は一般論の文を広くFAILさせる方向に働く。

## 4. 既存の正例・負例への影響(Regression)

- 過去本文14本×(3回、案Bは変更前7回): 任意項目のFAIL回数 変更前8/46、v0 4/42、v1 11/42、**v2 7/42**。`leak_discovery_syntax`のFAIL回数 変更前4/46、v0 4/42、v1 10/42、**v2 2/42**。
- 補足なし対照(v0)で0 FAILだった12本(36回): v0 0(定義上)、v1 8、**v2 7**。選択バイアス(0 FAILの本文を選んでから再測定すると増えて見える)を除いても、別日時の変更前データで0 FAILだった10本(30回)では v0 1 / v1 5 / v2 5。補足あり側が出やすい傾向があるが、**n=3では判定器の揺らぎと区別できない**(変更前でも案BのFAILは2/7、R1宅配gen2は2/3→対照0/3のように同一本文で大きく振れる)。
- v2で増えたFAILの内訳(R2宅配high_1の『ありそうだ』のdisc 2、案A最終のtension_reverts 2、R1宅配gen1のbinary_camp 1)は、補足の対象表現(『見えてくる』)を含まない本文・無関係な項目であり、補足の意図した効果ではない摂動。**補足を足したことによる判定の摂動の可能性は否定できない(未確認)**。これ以上の較正(n増、2桁円の追加費用)は「必要十分な較正で終了」(USER_03 §3)の範囲を超えると判断し、実走(E-1/E-3の蓄積したgate_history)での確認を推奨する。
- Closing Gateの既存機構(判定<=3+局所書換え、残存FAILは公開しない)は不変。FAILが散発した場合は書換えで吸収される範囲(一般Closing)、案Bは再判定<=3回→Human承認条件(HUMAN_APPROVAL_CASE_B_01)。

## 5. 案B(承認本文)への影響

- 案Bの判定(v2): 3回中 PASS 1 / `leak_evidence_memorable`のみFAIL 2。`leak_discovery_syntax` FAIL 0/3。案Bは補足の対象表現を含まないので、補足の直接効果ではなく揺らぎ/摂動の範囲。
- 3回連続でFAILし、かつFAILが`leak_evidence_memorable`だけなら、USER_03 §1の個別Human承認で採用される(HUMAN_APPROVAL_CASE_B_01)。途中でPASSすれば承認不要。`leak_discovery_syntax`等が1回でも混ざればSTOP(承認の対象外)。

## 6. 実費

`calibration_02`(判定のみ・計180 call) = **17.644円**(v1 72 call=8.454円[変更前データを再利用できない案A最終・案C・合成4本の補足なし18 callを含む]、v2 54 call=5.436円、v0対照54 call=3.754円。`raw_usage_log*.jsonl`を`er053_cost_aggregate_01`で集計)。Y立上げ累計 129.137 + 17.644 = **146.781円**(Cap 170円、残23.2円。超過なし)。本日(JST 10/25)の日次累計は`daily_dev_cost_01.py`で別途確認(報告に記載)。
起動前の`tools/stop_scope_check_01.py`はrc=0(非停止)を各batchで確認。並列は別process(範囲分割、同一jobの重複なし)で実行し、cost loggerのcontext共有の制約から1process内の並列は避けた。
