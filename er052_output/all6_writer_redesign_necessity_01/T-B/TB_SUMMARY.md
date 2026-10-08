# T-B 集計(既知NG記事の再判定、n=2/モデル)
記録数: 92(items=23 x 2モデル x 2反復)。Fact Check=vfl01.run_deviation_check(同一prompt/schema)。

## 1. 検出率(試行単位=item x 反復)
| 区分 | 指標 | gpt-5.6-luna | gpt-6-luna |
|---|---|---|---|
| 重大(7件x2) | NG文に対応する逸脱がMAJOR | 1/14 (7%) | 4/14 (29%) |
| 重大(7件x2) | NG文に対応する逸脱がMAJOR/MINOR | 1/14 (7%) | 4/14 (29%) |
| 重大(7件x2) | 記事内にMAJORが1件でもある(記事単位) | 4/14 (29%) | 9/14 (64%) |
| 重大(7件x2) | 記事内に逸脱が1件でもある(記事単位) | 4/14 (29%) | 9/14 (64%) |
| 軽微(16件x2) | NG文に対応する逸脱がMAJOR | 2/32 (6%) | 4/32 (12%) |
| 軽微(16件x2) | NG文に対応する逸脱がMAJOR/MINOR | 3/32 (9%) | 4/32 (12%) |
| 軽微(16件x2) | 記事内にMAJORが1件でもある(記事単位) | 4/32 (12%) | 16/32 (50%) |
| 軽微(16件x2) | 記事内に逸脱が1件でもある(記事単位) | 9/32 (28%) | 16/32 (50%) |

## 2. 反復別(matched_major / matched_any)
| 区分 | 反復 | gpt-5.6-luna major | gpt-6-luna major | gpt-5.6-luna any | gpt-6-luna any |
|---|---|---|---|---|---|
| 重大 | r1 | 1/7 | 2/7 | 1/7 | 2/7 |
| 重大 | r2 | 0/7 | 2/7 | 0/7 | 2/7 |
| 軽微 | r1 | 2/16 | 3/16 | 2/16 | 3/16 |
| 軽微 | r2 | 0/16 | 1/16 | 1/16 | 1/16 |

## 3. item別(r1,r2の順。MAJ=MAJOR対応/MIN=MINOR対応/-=対応なし。括弧内=記事全体の最大severity)
| item | 種別 | 型 | 5.6 r1 | 5.6 r2 | 6 r1 | 6 r2 |
|---|---|---|---|---|---|---|
| PAST-meta-p2r2-02 | major | 主体(対象) | -(COM) | -(COM) | -(COM) | -(COM) |
| PAST-ai-p2r1-01 | major | 未提示断定/比喩 | -(COM) | -(COM) | -(COM) | -(COM) |
| PAST-sw-p2r2-01 | major | 主体(発表内容) | MAJ(MAJ) | -(COM) | MAJ(MAJ) | MAJ(MAJ) |
| PAST-sw-p2r2-02 | major | 範囲(初めての対象) | -(MAJ) | -(COM) | -(MAJ) | -(MAJ) |
| PAST-ai-p2r1-02 | major | 主体(入替) | -(COM) | -(COM) | MAJ(MAJ) | MAJ(MAJ) |
| PAST-hormuz-T0M0r2-01 | major | 範囲(20%の対象) | -(MAJ) | -(MAJ) | -(MAJ) | -(MAJ) |
| PAST-jb9k-03 | major | 否定/未提示断定 | -(COM) | -(COM) | -(MAJ) | -(COM) |
| meta-x5wg-n1 | minor | 方向/極性 | -(COM) | -(MIN) | -(MAJ) | -(MAJ) |
| meta-p9ng-n2 | minor | 未提示断定 | MAJ(MAJ) | MIN(MIN) | MAJ(MAJ) | MAJ(MAJ) |
| space_weapons-wyg2-n2 | minor | 未提示断定 | -(COM) | -(COM) | -(COM) | -(COM) |
| space_weapons-86u9-n1 | minor | 未提示断定 | -(COM) | -(COM) | -(COM) | -(COM) |
| space_weapons-637f-n2 | minor | 方向/極性 | -(COM) | -(MIN) | -(MAJ) | -(MAJ) |
| space_weapons-v3eg-n2 | minor | 範囲 | -(COM) | -(COM) | -(MAJ) | -(MAJ) |
| hormuz-cdwb-n1 | minor | 方向/極性 | -(COM) | -(COM) | -(COM) | -(COM) |
| space_weapons-rvz5-n1 | minor | 範囲 | -(COM) | -(COM) | -(COM) | -(COM) |
| space_weapons-wyg2-n1 | minor | 範囲 | -(COM) | -(COM) | -(COM) | -(COM) |
| meta-p9ng-n3 | minor | 主体 | MAJ(MAJ) | -(MIN) | MAJ(MAJ) | -(MAJ) |
| meta-x5wg-n2 | minor | 主体 | -(COM) | -(MIN) | -(MAJ) | -(MAJ) |
| meta-sccn-n1 | minor | 主体 | -(MAJ) | -(COM) | -(COM) | -(COM) |
| space_weapons-pbwd-n1 | minor | 範囲 | -(COM) | -(COM) | -(MAJ) | -(MAJ) |
| meta-hkgv-n1 | minor | 未提示断定 | -(COM) | -(COM) | -(COM) | -(COM) |
| meta-v6r6-n1 | minor | 方向/極性 | -(COM) | -(COM) | -(COM) | -(COM) |
| meta-rweb-n3 | minor | 主体 | -(MAJ) | -(COM) | MAJ(MAJ) | -(MAJ) |

## 4. MINOR->MAJOR非対称(6-lunaが5.6より重く判定/軽く判定した件数、item x 反復の同一rep比較)
6-luna がより重い判定: 5 / より軽い判定: 0 / 同じ: 41(item x rep比較)
参考: NG文に対応しないMAJOR逸脱の延べ数(記事内の別箇所の指摘。真偽は未確認): 5.6=10, 6=32

cost.json(既存集計関数、gpt-6-lunaはpricing表に無く0円計上の可能性あり): {'by_stage_jpy': {'tb_gpt-5.6-luna': 20.092, 'tb_gpt-6-luna': 5.241, 'UNTAGGED': 0.706}, 'total_jpy': 26.038}