# Family C Future — Trial-03 vs Trial-04 比較

管理ID: EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04
同一テーマ(家庭用ロボットと家事)・同一Layer1 Ledger・同一Trial-02 World
Scaffold/Layer2-3を再利用(¥0)。v4はコード側で決定的に場面数を2へ絞り込み。

## 語数・場面数

| 項目 | Trial-03 A2 | Trial-04 A2 | 差分 | Trial-03 B1 | Trial-04 B1 | 差分 |
|---|---|---|---|---|---|---|
| word_count | 550 | 405 | -145語(-26%) | 744 | 484 | -260語(-35%) |
| target_range(Trial限定目安) | 450-600 | 380-520 | 目安自体を縮小 | 500-700 | 450-620 | 目安自体を縮小 |
| within_range | PASS(範囲内) | PASS(範囲内) | - | FAIL(44語=6.3%超過) | PASS(範囲内) | 超過解消 |
| [[IMAGINED]]場面数 | 3 | 2 | -1 | 3 | 2 | -1 |
| 段落数(##区切り内) | 3ブロック合計19段落 | 2ブロック+統合示唆1+締め1 | 削減 | 3ブロック合計20段落 | 2ブロック+統合示唆1(配置位置に課題)+締め1 | 削減 |

## Gate・QA結果

| 項目 | Trial-03 A2 | Trial-04 A2 | Trial-03 B1 | Trial-04 B1 |
|---|---|---|---|---|
| 編集Gate(数値/研究語/製品名/hedge密度/語数) | PASS | PASS | FAIL(製品名"Stretch"漏れ+語数超過) | PASS |
| imagined_hedge_density(枠内) | 0.0% | 0.0% | 2.3% | 0.0% |
| Fact Checker A'(Layer1) | REVIEW_REQUIRED | REVIEW_REQUIRED(不変、本Trialの診断対象外) | REVIEW_REQUIRED | REVIEW_REQUIRED(不変、本Trialの診断対象外) |
| Ledger Deviation | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| Future Framing QA v2 | PASS | PASS | PASS | **REVIEW_REQUIRED(新規)** — 統合示唆段落が2場面の間に挿入され、"will"を含む未hedge断定文が複数検出された |
| overall_status | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED |

## 費用

Trial-04累積実費(a2+b1、Fact Checker A'・Ledger Deviation・Framing QA込み): ¥20.53
(Trial-03は¥13.55。Family C残額¥125.54から¥20.53消費、残り¥105.01)

## 記事本文

- Trial-03: `../family_c_future_trial_03/a2/reader_facing_article.txt` / `../family_c_future_trial_03/b1/reader_facing_article.txt`
- Trial-04: `a2/reader_facing_article.txt` / `b1/reader_facing_article.txt`

## 結論

構造診断で特定した主因(Layer2/3が事前に3場面を"完成品に近い台本"として
提供していたこと、および各場面が[[IMAGINED]]枠+枠外一般示唆段落+
期待/懸念対比を毎回繰り返す3点セット構造だったこと)への対処(場面数を
2へ決定的に削減、統合示唆段落を記事全体で1回のみに統合)は、語数超過を
実際に解消した(A2 -26%/B1 -35%、B1は目安超過も解消)。禁止表現
(数値・研究語・製品名)は両レベルとも0件、枠内hedge密度も0%を維持した。

一方、B1では統合示唆段落の配置(本来は"全場面のあと"の指示だったが、
実際は場面1と場面2の間に挿入された)とhedging(“will”を含む複数の
未hedge断定文)がFuture Framing QA v2でREVIEW_REQUIREDとなり、新たな
課題として残った。また、Fact Checker A' verdict=REVIEW_REQUIREDは
Trial-03から不変であり、本Trialの診断・respec対象(語数構造)とは別の
既存の未解決事項として残る(本Trialでは変更していない)。
