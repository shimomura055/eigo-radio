# 課題① 集計(ラベル=docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_04/fable_labels_04.json)

## F層 (KP=41)

| arm | n出力 | PASS | 薄 | FAIL(字義 FAIL_LIT/その他) | 未ラベル | FAIL_LIT KP数 |
|---|---|---|---|---|---|---|
| B0 | 82 | 74 | 1 | 7 (6/1) | 0 | 3 |
| C | 82 | 79 | 0 | 3 (1/2) | 0 | 1 |
| M | 82 | 77 | 1 | 4 (4/0) | 0 | 3 |
| Cp | 41 | 40 | 1 | 0 (0/0) | 0 | 0 |

## N標本 (KP=20)

| arm | n出力 | PASS | 薄 | FAIL(字義 FAIL_LIT/その他) | 未ラベル | FAIL_LIT KP数 |
|---|---|---|---|---|---|---|
| B0 | 40 | 39 | 0 | 1 (0/1) | 0 | 0 |
| C | 40 | 39 | 0 | 1 (0/1) | 0 | 0 |
| M | 40 | 40 | 0 | 0 (0/0) | 0 | 0 |
| Cp | 20 | 19 | 1 | 0 (0/0) | 0 | 0 |

## 全体 (KP=61)

| arm | n出力 | PASS | 薄 | FAIL(字義 FAIL_LIT/その他) | 未ラベル | FAIL_LIT KP数 |
|---|---|---|---|---|---|---|
| B0 | 122 | 113 | 1 | 8 (6/2) | 0 | 3 |
| C | 122 | 118 | 0 | 4 (1/3) | 0 | 1 |
| M | 122 | 117 | 1 | 4 (4/0) | 0 | 3 |
| Cp | 61 | 59 | 2 | 0 (0/0) | 0 | 0 |

## C(flag項目のみ再生成)の flag項目内 Before->After (出力単位)

flag(再生成)された出力 19件: {'improve': 5, 'same': 14}

| KP | rep | Before | label | After | label |
|---|---|---|---|---|---|
| an unseen clock | 1 | 目に見えない時計 | FAIL_LIT | 目に見えない時間の流れ | PASS |
| an unseen clock | 2 | 目に見えない時計 | FAIL_LIT | 見えない時間の流れ | PASS |
| behind the curtain | 1 | 舞台裏に | PASS | 陰で関わっている | PASS |
| behind the curtain | 2 | 舞台裏に | PASS | 陰で動いている | PASS |
| greener grass | 1 | より青々とした芝生 | FAIL_LIT | 自分のものよりよく見える他人の暮らし | PASS |
| greener grass | 2 | より青々とした芝生 | FAIL_LIT | 自分より良く見える他人の暮らし | PASS |
| grow lighter | 1 | 軽くなる | PASS | 胸の重苦しさが和らぐ | PASS |
| grow lighter | 2 | 軽くなる | PASS | 胸の重苦しさが和らぐ | PASS |
| move in the other direction | 1 | 反対の方向に動く | PASS | 逆の傾向を示す | PASS |
| move in the other direction | 2 | 反対の方向に動く | PASS | 逆の傾向を示す | PASS |
| on paper | 1 | 書面上では | PASS | 理屈の上では | PASS |
| on paper | 2 | 書面上では | PASS | 理屈の上では | PASS |
| pump one's fist | 1 | こぶしを突き上げて喜ぶ | PASS | うれしくてガッツポーズをする | PASS |
| pump one's fist | 2 | 自分の拳を突き上げる | THIN | 自分の拳を突き上げて喜ぶ | PASS |
| question shaped like a trophy | 2 | トロフィーの形をした問い | FAIL_LIT | 成果や地位を誇示するような問い | FAIL |
| take off an ai costume | 1 | AIの衣装を脱ぐ | PASS | AIのふりをやめる | PASS |
| take off an ai costume | 2 | AIの着ぐるみを脱ぐ | PASS | AIのふりをやめて、人間の姿を現す | PASS |
| take the wheel | 1 | ハンドルを握る | PASS | 主導権を握る | PASS |
| take the wheel | 2 | ハンドルを握る | PASS | 主導権を握る | PASS |

- PASS->FAIL(新規悪化、flag項目内): 0件 []
- 検査器(V2_inv) vs ラベル(FAIL_LIT): TP=5 FP=14 FN=1 TN=102 (recall=5/6, precision=5/19)
