# 任意A(故障注入)結果 01(RLCT 委任_12)

Status: OPTIONAL_A_PARTIAL_PENDING_FABLE(Coffee再利用+inbound実施。streaming_priceは残枠不足の恐れで未実施、Fable判断待ち)。Trial専用。Production・harness(`er082_*.py`)変更0。
使用モデル: B3=gpt-6.1-sol / Verifier=gpt-6-luna(harness既定、最新・旧モデルなし)。実行entry=`er082_rlct_trial_01_inject.py`(Coffee実施時と同じ。委任文の`run.py --stage optA`は存在せず置換)。

## 1. 結果表(期待=全て REJECTED)

| 記事 | 注入Fact | 種別/改変 | 上限なし | 上限付き | 検出漏れ(VERIFIED通過) |
|---|---|---|---|---|---|
| coffee_prices(再利用) | INJ_F02_numeric_1 | 数値 4.30->5.89 | REJECTED | REJECTED | なし |
| coffee_prices(再利用) | INJ_F07_date_2 | 年 2024->2023 | REJECTED | REJECTED | なし |
| coffee_prices(再利用) | INJ_F09_direction_3 | 方向語 上昇->下落 | REJECTED | REJECTED | なし |
| inbound_tourism | INJ_F01_numeric_1 | 数値 3,098,900->4,245,493 | REJECTED | REJECTED | なし |
| inbound_tourism | INJ_F02_date_2 | 年 2026->2025 | REJECTED | REJECTED | なし |
| inbound_tourism | INJ_F05_direction_3 | 最多->最少(見出し句のみ) | AMBIGUOUS | AMBIGUOUS | なし(未VERIFIED) |
| streaming_price | - | 未実施 | - | - | - |

- 注入n=6件(Coffee3+inbound3)×2方式=12判定。**VERIFIEDで通った検出漏れ=0件**(critical_ng=False、両result.json)。元draft不変=True。integrity(inbound)identical=True。
- inbound F05は改変が見出し句(「年間過去最少・確定発表」)のみで、本文の「年間過去最多と発表した」は元のまま=Fact内部が矛盾する弱い注入。Verifierは矛盾の旨を指摘せず「推計値/確定値の差」を理由にAMBIGUOUSとした。REJECTEDではないが、通過(VERIFIED)はさせていない(partial扱い)。方式差(上限なし/付き)は全注入で同一verdict。
- 限界: 件数が少なく、検出率の保証にはならない(ユーザー§5)。

## 2. 費用(`lib.cost_by_stage_tag`、raw_usage_log実測)

| 項目 | JPY |
|---|---|
| inbound 上限なし(検索5回) | 8.929 |
| inbound 上限付き(検索7回) | 12.415 |
| inbound 計 | 21.344 |
| Coffee(既存) | 10.882 |
| 任意A合計 | 32.226 / 54 (残21.774) |
| Trial累計 | 477.158 / 1,040 |
| 当日(daily_dev_cost採用値348.36+21.344、重複計上の可能性あり) | 約369.70 / 1,000 |

## 3. streaming_price未実施の理由
inbound 1記事で21.344(Coffeeの約2倍)かかり、残枠は21.774。streamingの2呼出が同程度(11〜21)だと、Budgetガードのcheck(est 10)を通過しても実費が54を超える可能性がある(ガードは1呼出10見込みのみ検査)。委任文「2記事分が残枠に収まらない見込みならinboundのみ」に従い未実施。実施するなら(a)任意A上限の小幅引上げ(Trial全体1,040内)をFableが判断、または(b)未実施のまま打切り、のいずれか。
