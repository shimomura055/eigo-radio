# B_LIGHT_PREREGISTERED_01(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B、2026-10-25。評価実行前に凍結。API 0・Production変更0)
評価対象=`b_light_proto_01.py`(DEV専用、sha256 `5b715f8e55a6c4583e74c267283fd6ed4c402d15592f4e90ff5c174da7236f76`。評価前に凍結。評価で不合格なら**変更せず**v2として再凍結して再評価する=手順は`PREREGISTERED_CRITERIA_02.md`§1と同じ)。設計=`B_LIGHT_DESIGN_01.md`(推奨=案β `allow_explained_garble=True`、比較=案α `False`)。
評価スクリプト=`eval_b_light_api0_01.py`(保存済み転写のみ・socket guard・LLM判定なし・2回実行で出力一致)。比較基準のProduction=**pin commit `89b630bd1086a638b2fec1f00d69bfae8722b665` の top-level `*.py` スナップショット**(07Aが`er078_*`/`er007_*`を並行編集中のため、作業ツリーのProductionには依存しない)。F1+F2適用後の姿は`proto_value_gate_fix_04.apply_in_process`(v4、07A適用の元になる凍結proto)で再現する。

## 0. 評価する構成(4列)
| 列 | 内容 |
|---|---|
| base | 上記pin時点のProduction(Primary層+SCG許容集合[EXACT/NORMALIZED]) |
| +v2 | base + `proto_reading_compare_02`(v2、Primary層差替え+A4(a)。**VALIDATED(限定)**) |
| +F | +v2 + F1+F2(OPEN-517、v4。07A適用予定)。**これが07A適用後のProductionの代表** |
| +B | +F + 本タスクの`composite_judge`(案β)。Primary NG[P1=`p1_value_diff`/最終ゲート`final_gate_value_diff`/`secondary_not_accepted`]かつSecondary転写がある対にだけ適用 |
救済の判定は『その列でPASS系(PASS/PASS_WITH_WARNING)か』。composite は **追加のみ**(他列のPASSを落とさない)なので、回帰は「+F がPASSで +B がNG」の件数で確認する。

## 1. 合格基準(厳格化のみ可・緩和禁止)
| # | 基準 | 合格 | 不合格時 |
|---|---|---|---|
| 1a | **増分誤PASS(実Secondary転写あり)**: N-3 30clip(実TTS→実OpenAI+実Azure、音声は意図的な誤読)で、+F がNGなのに +B がPASSになった件 | **0** | REJECTED → 原因修正→再凍結→再評価 |
| 1b | **増分誤PASS(最悪ケース被覆)**: N-1 150の確定負例で、Secondary=『原稿そのもの(=Azureが最悪の場合に台本通りの値を返す)』と仮定して composite を適用し、+B で新たにPASSになる件(**露出**) | 露出は『Primaryの数値表記が位取り断片崩れ(8000900型)で、読みも一致』の型に**限る**。それ以外の型(値違い・桁違い・近音・わ脱落・助詞違い・否定・不規則読み・助数詞違い・同形異音)は **0**。型内の露出は1件ずつ列挙して審査し、残余リスクとして開示する | 型外の露出が1件でもあれば REJECTED |
| 1c | **合成負例**(SecondaryだけPrimaryだけ・両方違い・矛盾等のマトリクス。値: 8,800/89,000/8,090/9,900/千九百/八万九千/8000800/8000句800、読み: すわ/しば/し/巣は/しわし、不規則: 三日/二十歳/一日、否定反転) | PASS **0**(矛盾・読み違い・不規則・否定は全てNG) | REJECTED |
| 1d | 実Production履歴のP-S対(`ng_pool_cases_01.json`のSecondary記録あり54件など)で +F がNGのもの | composite がPASSにする件は**全件を列挙して個別審査**(基準: 原稿と実音声の値・読みが一致していると文脈上言えるか)。誤PASS疑いが出れば REJECTED | REJECTED |
| 2 | **回帰**: +F がPASS系の対(月題・N-3・実履歴対・Melos preview)で +B がNG | **0**(追加のみのため構造的に0。実測で確認) | REJECTED |
| 3 | **月題の救済**(12転写: attempt1〜3 × {保存転写 + OpenAI再転写3}。+Fの月題PASS数に対する +B の増分) | 報告。**目標**=attempt1〜3の各attempt全転写を安定して救済(=効果の上限)。増分1以上で『効果あり』、増分0で『効果なし』 | 効果なし → 採用提案しない(Status=NOT_EFFECTIVE) |
| 4 | **Melos副作用**: Melos preview(`三日目`、Primary PASS_WITH_WARNING)の判定が +B で変化 | 変化**0**(不規則読み値のため composite は適用外) | REJECTED |
| 5 | **評価不能の件数開示**: Primary×Secondary の対が揃わない母集団(P-4の421ユニーク[Secondary未記録]、N-1[音声なし]等)を件数で明記 | 開示 | 開示漏れ=不合格 |
| 6 | 決定性・隔離: 2回実行で出力一致/Production fileを変更しない/Productionが`b_light_proto_01`をimportしない(test) | 満たす | REJECTED |
| 7 | 追加Azure呼出の見積: composite の事前判定(`composite_judge(C,P,S:=C)`)が真になり、現行はP1/最終ゲートでAzureを呼ばない対 | 件数と費用を開示(判定基準ではない) | — |

## 2. Status写像(機械的。最終Statusは Fable)
- 基準1a・1b・1c・1d・2・4・6のいずれか不合格 → **REJECTED**。
- 全て合格 かつ 基準3の増分≥1 → **VALIDATED(限定)**(限定の中身=評価母集団の狭さ・同一データでの再評価・合成データの比率を併記)。**VALIDATEDを上限とする**(Production採用はユーザー判断、本タスクで自動開始しない)。
- 全て合格 かつ 基準3の増分0 → **NOT_EFFECTIVE**(安全だが効果なし=採用提案しない。方式の再検討へ)。
- 案α(`allow_explained_garble=False`)は同じ基準で並行評価し、βとの差を示す(αは構造上 v2 とほぼ同じ集合を返す=救済増分0が予想)。

## 3. 事前に開示する既知の限界(結果で隠さない)
1. 月題の数詞崩れは attempt ごとに型が違う(8000句800=復号不能、千九百=桁欠落、8000900/8000九百=断片連結)。**断片連結型だけ**が composite の対象になる。2エンジンが異なる値を出し、かつ断片説明も成立しない対は『矛盾』として救済しない設計であり、その救済は第3の独立証拠(ローカルWhisper等)が無い限り不可(=UDR #136・2026-10-11安全条件に触れるためユーザー判断。`B_LIGHT_DESIGN_01.md`案γ)。
2. 実データでの断片連結崩れは月題の2転写型のみ(n=2〜3)。**汎化は未確認**(合成の正例は自作であり実頻度の証拠ではない)。追加の有料Trial(別題材のTTS→ASR)が必要な場合は`B_LIGHT_BUDGET_PLAN_01.md`に見積のみ記載し、本委任では実行しない。
3. Secondary(Azure)が台本通りの値を誤って返す確率はN-3 30clipの値違い・桁違い(3件: 8,800/89,000/Azure`8800`・`8万9千`)で0/3(Azureは音声に忠実)。母数が小さいため統計的保証ではない。
