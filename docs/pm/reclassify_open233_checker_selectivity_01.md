# OPEN-233 CHECKER-SELECTIVITY-RECLASSIFY-01 Trial記録(委任_A2、2026-10-06)

性質: Trial(Production採用ではない)。到達上限VALIDATED。判定: **gold残存100%に未達(A4-0 sample3が全経路で消失)=VALIDATED未達【確認】**。
provenance: Before=reuse(`er052_output/open233_stage1_stageA_01/`の42 run保存候補)。After=fresh(分類call 42回、gpt-6-luna/effort=medium、`er052_output/open233_reclassify_01/runs/`)。Checker本体再実行なし。集計=`reclassify_aggregate.json`。

## 1. 候補数 Before→After(件/run、2方向和集合 all=model+決定論+coverage_gap、llm=model由来のみ)
| 群 | run数 | 和集合all | 和集合llm | r3 all | r5 all |
|---|---|---|---|---|---|
| SC(6×3) | 18 | 18.17→10.11 | 14.28→5.94 | 17.94→10.00 | 5.89→4.33 |
| B2_hormuz(WATCH) | 3 | 14.33→10.67 | 7.00→3.33 | 14.00→10.33 | 3.33→2.00 |
| NORMAL(6×2) | 12 | **24.17→9.83** | 19.92→5.33 | 23.50→9.83 | 9.00→3.42 |
| hold-out | 9 | 1.0→1.0 | 1.0→1.0 | 1.0→1.0 | 1.0→1.0 |
| ALL | 42 | 15.93→8.12 | 12.52→4.52 | 15.62→8.05 | 5.55→3.19 |
通常記事(NORMAL)の件/記事: 24.17→9.83(約59%減)。決定論・coverage_gap分(NORMAL 4.25件)は不変。

## 2. gold 6件(run別、3 sample)
| gold | Before候補run | After(any) | After(model由来) | r3 | r5 |
|---|---|---|---|---|---|
| B3 | 3 | 3 | 3 | 3 | 3 |
| B4-a | 3 | 3 | 3 | 3 | 3 |
| B3-same@neg5 | 3 | 3 | 3 | 3 | 2(Beforeも2) |
| A2A3-0 | 3 | 3 | 3 | 3 | 3 |
| **A4-0** | 3 | **2** | 1 | 2 | 1 |
| A5-0 | 3 | 3 | 3 | 3 | 3 |
**落ち: A4-0(safety_A4)**
- sample3: 全経路で消失(any=false)。claim=「Through Muse, trained human contract workers made some calls and completed the exchanges with users.」r3/r5ともSUPPORTED(tag number,proper_noun)。理由:「訓練を受けた人間の契約スタッフがMuse経由の一部の電話を担当し、やり取りを完了させたというLedgerと一致する」。
- sample2: model由来はr5のみSUPPORTEDへ(同claim、MUSE-HC-004/006)、r3と決定論側で残存(any=true)。
- Ledger原文: MUSE-HC-006 `[VERIFIED] MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。 scope: Muse経由で発信された電話の一部 / notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。` / MUSE-HC-004(米国内企業・店舗への発信、Reuters報道)。
- **【Fable確認、委任_B3で追記・上の【推測】を訂正】** A4-0 goldの正式な違反内容は限定語"some"ではなく**「やり取りの相手(カウンターパート)の取り違え」**: Ledger MUSE-HC-006の電話の相手先=企業・店舗、記事は"completed the exchanges with users"(Museのユーザー)。根拠: `er052_open233_self_recovery_stage2_calibration_01.py` L363-368(Ledgerのissue逐語)。新しい問いは主体の取り違えを「Ledger一致」と誤読して候補から外した=Safety上の本物の見逃し(主体/固有名のFactリスク)。A4-0は過去にもV2 false downgrade・r5-V 0/3と脆弱。
- 【推測】当該claim文面自体は"some calls"で限定済みでLedgerと整合して読める。goldの本質はこの文を含む記事での別のFact(例: 発信範囲・テスト性の限定)であり、文単位の分類で「Ledger一致」と判断されると落ちる。gold定義との照合はFable判断。

## 3. 監視項目
- hold-out 9種: 全9件残存(1→1)。
- A4-0: 上記(2/3)。neg5(B3-same): 3/3残存。HF-011: Before/Afterとも候補なし(Before=0、SAFETY_CRITICAL外の監視項目)。K19: 3/3残存(ユーザー決定で軽微扱い)。

## 4. 2方向
r3: 15.62→8.05、r5: 5.55→3.19、和集合: 15.93→8.12(all)。和集合でのgold残存=5/6(A4-0が3sample中2sample)。

## 5. 実費
42 call、入力206,966 tok/出力91,916 tok(reasoning含む)、**¥10.46**(見積low¥11.5/mid¥13.7/high¥16.5より低い、midとの差−¥3.3)。上限¥17内。欠損run=0、fail-closed=0、retry=0。

## 6. 分類内訳
verdict(全42run、526 claim): CANDIDATE 190 / NO_FACT_CLAIM 177 / SUPPORTED 159。CANDIDATEのFact種別タグ: comparison 82, causality 70, negation 48, number 34, proper_noun 33, none 29, date 13。SUPPORTED側: none 203, comparison 52, negation 43, date 29, proper_noun 26, causality 20, number 18。
【確認】CANDIDATEのうちtag=noneが29件(具体的Factタグ無しの候補)は「Ledger食い違い」理由が主で、新問い(比喩・つなぎ除外)の適用が不完全な可能性。

## 7. 例(NORMAL)
NO_FACT_CLAIMへ落ちた10例: "Ring, ring."(効果音) / "It was like someone took off an AI costume."(比喩) / "But this was where the problem began."(つなぎ) / "Here was the reveal." / "We must also know, at the start, who is on the other end."(規範) / "Some are so small that you might ask, “Can you really fit anything in that?”"(修辞的問い) / "The season’s picture becomes clearer when we look at what appeared beside them." / "If they step onto the stage, they should give their name first." / "But the picture changed once people looked behind the stage." / "Oil-price news sometimes gets its biggest twist not from a policy announcement, but from what prices do after..."。全て比喩・つなぎ・一般論・規範で【確認】妥当に見える。
SUPPORTEDへ落ちた5例: "They add a special feeling."(ELLE記述の言い換え) / "Large bags are the luggage crew, carrying what we need." / "The test had begun without clearly telling users."(negation、Ledger一致) / "Large bags had not disappeared."(negation、F004) / "They do not challenge roomy bags on storage."(negation+comparison)。negation/comparisonを含む文がSUPPORTED判定されている点は、重大Factを落とさないかの観点で注視要。
境界例3件(CANDIDATE維持): "A call came from an AI agent."(発信主体がLedgerと不一致) / "A call seemed to come from an AI agent."(印象がLedger未記載、Ledger未記載のみ→旧問いに近い判定) / "People who asked Muse to make a call might think AI was doing it."(Ledgerに記載なしの推測、同上)。後者2件は「Ledgerに明示されていないだけ」で候補化されており新方針と緊張。

## 8. 【確認】/【推測】所見(結論は出さない)
- 【確認】候補は大幅に減る(NORMAL 24.2→9.8件/記事、llm分は19.9→5.3)。費用は実測¥10.46で見積内。
- 【確認】gold 6件のうちA4-0が1 sampleで全経路消失。合否基準(gold残存100%)に未達。他5件とhold-out 9種は全残存。
- **【Fable確認、委任_B3追記】** gold落ち(A4-0 sample3)の原因は限定語("some")ではなく主体/相手先(カウンターパート)の取り違えの見逃し(§2のFable確認参照)。以下の【推測】のうち限定語に関する部分はこの確認で置き換わる。次Trialの観点は「主体・相手先・範囲・限定語のLedger一致確認」を明示する方向が候補(判断はユーザー)。
- 【推測】減少の大半は比喩・つなぎ・規範文のNO_FACT_CLAIM化(妥当)。一方、限定表現("some")を含む既出Ledger一致文のSUPPORTED化がgold落ちの原因。決定論/coverage_gap分(約4件/記事)は下限として残る。
- 【推測】次Trial(fresh実行)へ進むなら、プロンプトに「限定語・範囲(scope/some/test)が一致するかを確認する」観点の追加、または1方向でもCANDIDATEなら残す等を検討する余地。ただしCheckerのprompt変更はscope外のため実施せず、Fable判断。
