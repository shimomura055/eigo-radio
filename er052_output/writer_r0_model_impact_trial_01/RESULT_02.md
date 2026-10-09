# RESULT_02: R0モデル比較の再Closeout表(Disney+を完全台帳F01-F07で再評価後、FIX01-A、2026-10-10)

性質: Trial/DEV。Production変更なし、採用判断なし。**モデル優劣は確定しない。人間確認前に最良・優劣の結論を出さない。** RESULT_01.mdは上書きせず残す(Disney+の旧値はn_facts=5入力の評価で、評価には使わない)。宇宙兵器・BYDはRESULT_01の値をそのまま使用(台帳欠落なし、再実行なし)。

## 1. 比較表(Flag総数 = D0rb ∪ D2、事前登録定義)
| テーマ | Luna | Sol | Astra |
|---|---|---|---|
| Disney+(完全台帳7 Fact、今回再実行) | 0 | 0 | 0 |
| 宇宙兵器 | 0 | 0 | 0 |
| BYD | 0 | 0 | 0 |
| **合計** | **0** | **0** | **0** |
(参考: 旧Disney+は 4 / 1 / 0、旧合計 4 / 1 / 0。F01・F07欠落入力のため評価には使わない。)
D0 gate_only(許可禁止反転ルール、総数に含めない既存規約): 宇宙兵器 Luna 2 / Sol 2 / Astra 3(RESULT_01のまま、Disney+・BYDは0)。Flagger入力Fact数: Disney+ 7/7、宇宙兵器 22/22、BYD 11/11。

## 2. D2 confidence統計(D2のみ)
| 項目 | Luna | Sol | Astra |
|---|---|---|---|
| D2 Flag数(全3テーマ) | 0 | 0 | 0 |
| min / max / mean / median | - | - | - |
全Flag保存済みだが対象Flagが0件のため統計値は算出不能。

## 3. Flag種類別件数(Flaggerの既存type)
| 種類 | Luna | Sol | Astra |
|---|---|---|---|
| D2: 全type | 0 | 0 | 0 |
| D0(gate_only): その他/許可禁止反転 | 2 | 2 | 3 |

## 4. 具体Flag(提示)
- 総数に入るFlag(D0rb∪D2)は全9セルで0件。D2が出すFlagは0件(Disney+再評価後)。
- 参考のD0 gate_only 7件(宇宙兵器、ルール由来、総数に含めず)の全文は FLAG_LIST_01.md。Sonnet暫定: 条約の『禁じる/禁止するものではない』文脈で語彙一致由来に見える(未確定)。
- 人間確認候補(RESULT_01 4.のSonnet暫定・未確定、Flagger未検出): 宇宙兵器 Sol/Astraの不在系記述、BYD Lunaの『公告の対象は』単数的表現と制動灯の一般説明。これらは変更なし。

## 5. 解釈上の注意(結論ではない)
- 3モデルともFlagger総数が0となった。Flagger 0件は「問題がない」の保証ではない(Flaggerは台帳外断定の検出補助。上記の人間確認候補は未検出のまま残る)。
- R0モデル間の差は、Flagger総数・confidenceからは現時点で示されない。モデル優劣は確定せず、人間確認(ユーザー)待ち。
- R0費用・処理時間はRESULT_01記載のまま(Luna ¥1.24 / Sol ¥22.07 / Astra ¥127.08、R0合計)。Flagger再実行費 ¥3.39。本Trial累計 ¥169.36。
- Status: WRITER-R0-MODEL-IMPACT-TRIAL-01 = USER_DECISION_REQUIRED のまま(Fableが統合時に確定)。

詳細: FIX01_DISNEY_RERUN_01.md
