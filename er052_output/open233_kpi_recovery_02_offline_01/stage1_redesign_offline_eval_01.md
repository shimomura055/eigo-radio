# Stage 1再設計案 ¥0事前評価(委任_03、既存データのみ・API 0・実装なし)

出典: `stage1_redesign_offline_eval_01.py`/同名json。案4の決定論pre-checkは**設計レベルの簡易模擬**(日英辞書約40語・アンカー照合)で本実装ではない。数値は模擬の性質上、設計判断の材料(採否の確定根拠ではない)。

## (a) 案4 決定論pre-check模擬: Safety-critical gold文(7件)が候補に入るか

- L0(カテゴリ語マーカーがあれば候補。alignmentなし): 6/7
- L1(マーカー+緩いalignment[アンカー1つ共有のfact全部]+不一致): 0/7
- L2(マーカー+厳格alignment[最多アンカーfactのみ]+不一致): 1/7
- gold文が関連factにalignされた数: 緩い6/7、厳格(L2)5/7
- 既存`run_precheck`(Ledger×本文の機械照合)が24 fixture(A15+er009合成9)で立てた候補合計: 1(er009_changed_numberの1件のみ)

| instance | sub | L0 | L1 | L2 | 関連factにalign(緩/厳) | カテゴリ(L0) |
|---|---|---|---|---|---|---|
| bgroup_B3 | B3 | ○ | × | × | ○/× | causal,comparison,negation,number,time |
| bgroup_B4 | B4-a | ○ | × | × | ×/× | actor |
| safety_A2A3 | A2A3-0 | × | × | × | ○/○ |  |
| safety_A4 | A4-0 | ○ | × | ○ | ○/○ | actor,number |
| safety_A5 | A5-0 | ○ | × | × | ○/○ | actor,comparison,time |
| bgroup_B2_hormuz | HF-011 | ○ | × | × | ○/○ | causal,comparison,negation |
| neg5_hormuz_div_a2 | B3-same@neg5 | ○ | × | × | ○/○ | causal,number |

## (a') 負例/NORMAL 6 instanceの候補文数(平均本文文数26.7)

| 方式 | 平均候補文数 | ≥1文立つinstance |
|---|---|---|
| L0 | 20.33 | 6/6 |
| L1 | 2.33 | 5/6 |
| L2 | 8.5 | 6/6 |

現行A単発のMAJOR出現率は7/12(58.3%)。L0/L2は全instanceで候補が立つため、候補を全てStage 2へ渡す設計はStage 2発動率100%・候補8〜20文/記事となる。

## (a'') B4非SC(frozenが拾いfresh 2runが拾わなかったMAJOR 4件)の文が候補に入るか

- MUSE-HC-004: 文特定=False / L0=False / L2=False / “As AI makes calls and reservations, useful features make people want to know whether AI o
- MUSE-HC-010: 文特定=True / L0=True / L2=False / People feel differently when they think they are speaking to a machine and when they know 
- MUSE-HC-010: 文特定=True / L0=True / L2=False / As AI makes calls and reservations, useful features make people want to know whether AI or
- MUSE-HC-004: 文特定=True / L0=True / L2=False / In the AI age, making a voice sound human is not enough: people must first be told who is 

## (b)(d) 費用見込み(円/記事、gpt-6-luna単価、A単発実測平均0.357=6244tok in/3741tok out)

| 案 | 費用/記事(円) | 備考 |
|---|---|---|
| 案1/案2(n=1) | 0.357 | 実測 |
| 案2 n=2 / n=3 | 0.714 / 1.070 | 単純倍(実測平均×n) |
| 案3 候補対LLM分類(1 call、対48.0件) | 0.727〜1.669 | 対あたり出力150〜400tok仮定(推測) |
| 案3' 文ID強制1 call分類 | 0.476〜0.622 | reasoning 1.0〜1.5倍仮定(推測) |
| 案4 | 0 | 機械照合のみ。ただしStage 2費用が増える(下記) |
| 案5 fact群batch(3facts/call, 4.5 call) | 0.694〜0.841 | 出力は担当fact比例×1.0〜1.5仮定(推測) |
| 案5 fact群batch(5facts/call, 3.0 call) | 0.566〜0.713 | 同上 |
| 案6 最終安全確認(+1 call) | +0.178〜+0.357 | A単発の0.5〜1.0倍と仮定(推測。S1-Uは約14.6%増の記録) |

Stage 2(rep30実測の比例推定): cycle1 Stage 2費用 ≒ 0.099 + 0.073×Stage 1 MAJOR件数(r=0.78, n=30 instance、MAJOR件数範囲[0, 10])。
負例/NORMAL 1記事あたりStage 2費用: 現行A単発 0.107円 → 候補(L2)全件投入 0.722円 → 候補(L0)全件投入 1.590円(件数がfit範囲外のため外挿・過小評価の可能性)。

## (c) 案2 Stage 1複数回∪(RCA既出の再掲)

| claim | A単発 | 2回∪ | 全run∪ |
|---|---|---|---|
| B3 | 2/2 | 検出 | 検出 |
| B4-a | 2/2 | 検出 | 検出 |
| A2A3-0 | 2/2 | 検出 | 検出 |
| A4-0 | 2/4 | 検出 | 検出 |
| A5-0 | 2/2 | 検出 | 検出 |
| B3-same@neg5 | 0/2 | 見逃し | 見逃し |
| HF-011 | 0/2 | 見逃し | - |

負例/NORMAL MAJOR率: 単発58.3% → 2回∪66.7%(RCA既出)。neg5 B3-sameとHF-011は∪でも見逃し(n=2)。

## 限界(推測の明示)

- 案4模擬の辞書・マーカーは小辞書で、Ledger/本文が日英であることの辞書依存が大きい。精度が低いのは模擬の粗さの影響も含む(本実装の上限ではない)。ただし『Ledger factのcausal_strengthが記事の因果表現の原因側まで保証しない(B3: HF-007は因果stated)』『A2A3-0のような主体差替えはマーカー語を持たない』は構造上の限界【確認: 該当fixture】。
- 費用は単価と実測tokensからの算術。案3/5/6の出力tokensは仮定(推測)。実測ではない。n=24〜32のfixture/runの小標本。
- Stage 2費用fitはn=30、MAJOR件数0〜10の範囲。候補20件は外挿。
- 本評価は検出率の保証ではない。E2E(fresh)でのみKPI判定できる。
