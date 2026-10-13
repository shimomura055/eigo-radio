# F1_IMPACT_CENSUS_01 F1是正の既存データ影響事前集計(read-only・API 0・JPY0)

script: `er075_m1_f1_production_wiring_01_census.py` / 実行: `--out-dir er075_output/m1_f1_production_wiring_01 --no-telemetry` / 生ログ: `census_stdout_01.txt` / 詳細: `f1_census_01.json`
方法: Production `val.classify_asr_match`(segment_id=full_story_part1)を現行と、`csv3.classify_connected_speech` をF1案へ**プロセス内のみ差替え**した場合で比較。共有telemetryへは書かない(er068 import時no-op)。

## A. 実データ(canonical/ASRペア)
| 項目 | 値 |
|---|---|
| 対象ペア数(重複除去) | 674(HR queue 187 / er021 telemetry 434 [7156-9153行・9178-9180行除外] / er069 results_02 53) |
| `er011_output/attempt_history.jsonl` | 12,891行だが転写本文を持つ行は3件のみ(件数・状態のみ記録)→ペア集計には寄与せず |
| 現行でPattern A/B/C(連結発音)によりPASSだったペア | 10(全て短いclip: `Brontes→Bronte/Bront` 8、`Melos→Melo` 2、単一差分) |
| **現行PASS→F1後に非PASS** | **0** |
| 非PASS→PASS(緩和) | **0** |
| 分類のみ変化 | 0 |
| エラー | 0 |
注意: 実データのうち連結発音PASSは10件で、いずれも1か所差分のため影響なし。**長文Production実績(Family X/Z本編)の連結発音PASSは本データに含まれず**、F1の実害頻度はこの集計では測れない(下記Bで真値付き合成/窓データを補完)。

## B. 真値付き既存データ(er068のread-onlyローダ)
| データ | 真値 | n | 現行PASS | F1後PASS |
|---|---|---|---|---|
| cs_sweep(18固有名詞×次語) | 正常想定 | 222 | 114 | 114 |
| cs_synthetic | 正常想定 | 19 | 10 | 10 |
| cs_synthetic | 欠陥 | 6 | 0 | 0 |
| defect_text(反例セット) | 欠陥 | 41 | 4 | **3** |
| normal_text | 正常 | 20 | 13 | 13 |
| general_2word | 正常 | 324 | 162 | 162 |
| real_diff(HR/telemetryの実窓) | 仮ラベル正常(目視未実施) | 124 | 36 | **32** |

- 誤PASS解消: `The studies suggest cats today.` ↔ `The study suggests dogs today.`(`multi_diff_masking_existing_hole`)が非PASS化。残る欠陥PASS 3件(`walked→walk`(Pattern B)・`asked→ask`(Pattern B)・`bus→bu`(Pattern A))は**単一差分で承認済みPattern自体の範囲**であり、F1では解消しない(OPEN-330等、F1とは別論点・変更せず)。
- 正常→非PASS(誤NG)件数: normal_text 0 / cs_sweep 0 / general 0 / cs_synthetic正常 0。**real_diffの4件**(`a US sea blockade` 窓:`a U S se blockade`/`a U S blockade`/`planned U S blockade`/`a U S C blockade`)が現行PASS→非PASS。内容は `sea` の欠落またはASRの文字読み(`C`)で、連結発音では説明できない。仮ラベル「正常」とは食い違うが、音声未聴取のため「真の誤NG」とは断定しない=**確認要(確認方法: 4窓の元clipを人が聴く。API不要)**。受入条件「正常な連結発音を不必要にNGにしない」に対し、真に正常な連結発音の誤NGは**確認できた範囲で0**、未確認4件を明記。

## C. 反例セット(ユーザー例を含む。`f1_census_01.json` の counterexamples)
現行PASS→F1後非PASS(期待どおり。11件):
- `The studies suggest cats today.`/`The study suggests dogs today.`(ユーザー例)
- `…that cats sleep.`/`…that dogs sleep.`・`…cats sleep more.`・`…cats sleep.`(that欠落)・`…cats slept.`(時制)・`…Rex sleeps.`→`Max`(固有名詞)・`…cats.`(語欠落)
- Pattern B: `The company opened…closed…`/`open…closes…`(時制)・`…closed to the people.`(語置換)
- Pattern C: `The survey suggests that cats sleep.`/`The surveys suggest that dogs sleep.`
- 複数箇所: `Their studies suggest cats and their survey suggests cats.`/`…surveys suggest dogs.`
現行PASS→F1後もPASS(正常な連結発音、不必要NGなし。6件): `The study suggests cats today.`/`The study suggest cats today.`(単一/複数の連結発音)/`…that cats sleep.`(`studies suggest`→`study suggests`)/Pattern B `open…closed`/Pattern C `surveys suggest`(PASS_WITH_WARNING維持)/複数箇所の正常連結(`Their study suggests…surveys suggest cats.`、RESEGMENTATIONを含むためPASS_WITH_WARNING)。
元から非PASS(変化なし): 数値(`5`→`6`)・否定の追加(`did not sleep`)。

## D. 結論と注意
- F1是正は**厳格化のみ**(緩和0件)。既存実データ674件でPASS→非PASSは0件、真値付きデータの正常側の誤NGは確認範囲で0件、未確認候補4件。
- 受入条件「誤NG=0」は、4件(`US sea blockade`)の目視で全て「真の欠落/誤読」と確認されれば満たされる。確認前に`PRODUCTION_WIRED`とは言えない(判断はFable/ユーザー)。
- Family X/Z長文の実PASS履歴を拡張集計するには、各`attempt`の転写を保存した成果物(`audit/raw_usage_log.jsonl`等)が必要。追加集計は既存データのread-onlyで可能(費用0)だが、本委任の範囲では未実施。
