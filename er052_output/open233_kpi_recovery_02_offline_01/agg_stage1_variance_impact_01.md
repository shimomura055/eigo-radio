# Stage 1非決定性の影響分析(委任_10 CORRECTION-02、0円・既存データのみ)

**本資料はユーザー判断の材料(事実の集計)であり、採用提案ではない。Fable/Claudeは新Checker仕様を新設・選定していない。**
出典: `a_frozen_fresh_01/`(A構成fresh、n=2、A4はn=4)、rep30 frozen記録、V0記録(Production記録n=1)。集計: `agg_stage1_variance_impact_01.py`、数値は同名json。

## (a) Safety-critical 6 claim + B2_hormuz HF-011 の検出有無

| claim | A単発(run別) | A 2回和集合(run1∪run2) | A run1∪V0記録 | V0記録(n=1) | frozen(rep30実使用) |
|---|---|---|---|---|---|
| B3 | 2/2 (○/○) | 検出 | 検出 | 検出 | 検出/検出 |
| B4-a | 2/2 (○/○) | 検出 | 検出 | 検出 | 検出 |
| A2A3-0 | 2/2 (○/○) | 検出 | 検出 | 検出 | 検出/検出 |
| A4-0 | 2/4 (×/○/×/○) | 検出 | 検出 | 検出 | 検出 |
| A5-0 | 2/2 (○/○) | 検出 | 検出 | 検出 | 検出 |
| B3-same@neg5 | 0/2 (×/×) | 見逃し | 見逃し | 見逃し | 検出 |
| B2_hormuz HF-011 | 0/2 (×/×) | 見逃し | 検出(V0記録を足したため) | 検出 | 検出(V0差替え) |

注: A4-0はn=4(和集合はrun1∪run2で表記、全run和集合はjson `A_union_all_runs`)。V0記録が当該instanceに存在しない場合は`-`。

## (b) 負例/NORMAL群(neg1〜3+NORMAL3)のMAJOR出現率

| 方式 | MAJOR出現率 |
|---|---|
| A単発(run単位) | 7/12 (58.3%) |
| A 2回和集合(instance単位) | 4/6 (66.7%) |
| frozen(rep30、run単位) | 6/11 (54.5%) |
| V0記録(instance単位) | 1/6 (V0記録のあるinstanceのみ) |
| A run1∪V0(instance単位) | 4/6 (V0記録のあるinstanceのみ) |

和集合の率は単発以上になる(各runのMAJORの和)。instance別内訳はjson `neg.per_instance`。

## (c) 1記事あたりStage 1追加費用の推定

| 方式 | 円/記事 |
|---|---|
| A単発(1 call、実測平均 n=32) | 0.357 |
| A 2回和集合(2 call) | 0.714 |
| A単発+V0(2 call) | 0.892 |
| frozen再利用 | 0(ただしfrozen出力は新記事には存在しない) |

V0@gpt-5.6-luna 1 call単価の推定=0.5351円。V0@5.6単価はer050 V0 prompt記録(gpt-5.6-luna)のusage tokensをRATES(0.20/0.02/1.20 USD per 1M、156.88円/USD)で換算した推定(委任_05 cell_cand_56luna実測0.728は候補promptのため不使用)。n=15

## 限界(確認/推測)
- 確認: 上記数値は既存jsonの機械集計。n=2(A4のみ4)でサンプルが小さく、率の差は統計的に確定的ではない。
- 確認: V0記録はn=1で、V0自体のrun間変動は本資料では測っていない(V0が安定だとは言えない)。
- 推測: run数を増やせば検出が増える可能性とMAJOR誤検出が増える可能性の双方がある。
