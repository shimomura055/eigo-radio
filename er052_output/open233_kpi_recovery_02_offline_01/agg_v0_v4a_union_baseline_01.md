# V0∪V4A基準線(委任_05 事前作業5、¥0、採用提案ではない)

- V0記録=Production V0実記録 n=1 / V0@6luna n=2(cell_v0_6luna) / V4A=A構成fresh n=2 / 候補@5.6 n=1。既存保存データのみ(新規API 0)

## 正式SC 6件の検出(MAJOR claimがtext_pattern/substringに一致)

| SC | V0記録(n=1) | V0@6luna | V4A fresh | V0@6luna∪V4A(run対応) | V0記録∪V4A | 候補@5.6 |
|---|---|---|---|---|---|---|
| B3 | True | 1/2 | 2/2 | **2/2** | **2/2** | 1/1 |
| B4-a | True | 1/2 | 2/2 | **2/2** | **2/2** | 0/1 |
| A2A3-0 | True | 2/2 | 2/2 | **2/2** | **2/2** | 1/1 |
| A4-0 | True | 1/2 | 1/2 | **2/2** | **2/2** | 0/1 |
| A5-0 | True | 2/2 | 2/2 | **2/2** | **2/2** | 1/1 |
| B3-same@neg5 | False | N/A | 0/2 | **N/A** | **0/2** | N/A |

## 候補数(MAJOR claim数/記事・run、neg=誤検出側、NORMAL=本来0が望ましい)

| instance | 種別 | V0記録 | V0@6luna/run | V4A/run | ∪(V0@6luna,V4A)/run | ∪(V0記録,V4A)/run |
|---|---|---|---|---|---|---|
| neg1_meta_b3prod_a2 | neg | 0 | [1, 1] | [1, 2] | [1, 2] | [1, 2] |
| neg2_meta_refresh_a2 | neg | 0 | [1, 0] | [1, 1] | [1, 1] | [1, 1] |
| neg3_hormuz_prodrunner_b1b | neg | 0 | [1, 0] | [0, 1] | [1, 1] | [0, 1] |
| hormuz_run02_advanced | NORMAL/B群 | 1 | [None, None] | [0, 0] | [None, None] | [1, 1] |
| hormuz_run03_advanced | NORMAL/B群 | 0 | [None, None] | [0, 0] | [None, None] | [0, 0] |
| meta_run03_advanced | NORMAL/B群 | 0 | [None, None] | [1, 1] | [None, None] | [1, 1] |
| meta_run03_standard | NORMAL/B群 | 1 | [None, None] | [2, 1] | [None, None] | [2, 2] |

注: 基準線のみ。採用提案ではない。n=1〜2のため見逃しゼロの証明ではない。neg5はV0実記録(fixture.baseline_parsed、Productionで流出した出力)が見逃し、V0@6luna/候補@5.6のrunは存在しない(N/A)。V0@6luna cellにはNORMAL群のrunが無い。
