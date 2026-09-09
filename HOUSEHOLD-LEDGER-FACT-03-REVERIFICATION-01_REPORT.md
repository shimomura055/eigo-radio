# HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01(OPEN-138)

管理ID: HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01(Sonnet、Fable委任)。
ユーザーDecision D2-UDR-2(2026-09-09)により、Household Verified Fact
Ledger FACT-03(柑橘類の高湿度保存記載)を既存Research正式経路で再検証
した。新Fact policyは作成していない。SSOT編集・Git操作・Production/
Prompt編集・完成audio/記事本文の修正は一切行っていない。

## 1. Reconciliation(所在・原文・Trial-07の指摘内容)

- Ledger本体: `er003_output/n3_01/household/research/verified_fact_ledger.txt`
  (A2/B1共通source of truth、`ER-003-A2-B1-N3-01`)。
- FACT-03原文(修正前、v3): 「使い分けの基本は『果物か野菜か』ではなく
  『エチレンを多く放出するか』『水分をすぐ失ってしおれやすいか』であ
  る…ただし例外があり、イチゴ・柑橘類(オレンジ等)のような果物は高湿度
  を好む(UC Davisはイチゴ・オレンジの最適湿度をいずれも90〜95%として
  いる)」。source: Iowa State Extension、Whirlpool、KitchenAid、UC Davis
  Postharvest Research and Extension Center。
- 公開済み記事への反映箇所: A2記事(`a2/article.md`)は柑橘類・イチゴに
  言及せず対象外。B1記事(`b1b/article.md`、2026-08-17承認)33行目に
  「Strawberries and citrus fruits, including oranges, prefer high
  humidity. UC Davis lists an ideal humidity of 90 to 95 percent for
  both.」として反映されている。
- Trial-07(`er011_output/discovery_layer3_focus_trial_07/`、12本)の
  独立Fact Checker判定: PASS 5 / REVIEW_REQUIRED 5 / **FAIL 2**
  (`a2/baseline/run3`、`a2/discovery_focus/run1`)。FAIL 2本はいずれも
  「イチゴ・柑橘類(オレンジ)は高湿度を好む」という家庭用クリスパー
  設定の断定を、GE Appliances公式案内(オレンジ・イチゴを低湿度側
  Fruit Binに分類)・UC San Diego・Illinois Extensionと明確に矛盾する
  として指摘した。REVIEW_REQUIRED 5本も同一論点(柑橘類の家庭用設定の
  一般化)を非blocking advisoryとして指摘していた。

## 2. 再検証(既存Research正式経路のFact Checker関数を実呼び出し)

`er002_ja_web_research_r3.py`の`make_fact_checker_fn`/
`run_fact_checker_with_gates`(Production同一関数、Trial-07・
`er003_v1_n3_01_articles_generate.py`でも使用)を、公開済みB1記事の
FACT-03由来段落(一字一句改変なし)に対してそのまま1回実行した
(`er012_open138_household_fact03_reverify_01.py`)。

- 結果: **verdict = FAIL**(3回目の独立確認としてTrial-07の2 FAILと
  一致)。web_search 6回。
- 根拠: UC Davisの90〜95%という数値自体は正確(商業的・ポストハーベスト
  貯蔵条件の最適相対湿度)。しかしこれを家庭用冷蔵庫クリスパードロワー
  の「高湿度設定」に直接対応づける記述は、GE Appliances公式案内
  (イチゴ・オレンジとも低湿度側Fruit Bin)と明確に矛盾し、家電メーカー
  間でも一致しない(Samsungはイチゴを高湿度側に分類)。
- 判定: **条件付き(不正確)**。中心的な仕組み(エチレン/水分保持)の
  説明は正確。イチゴ・柑橘類を「高湿度ドロワーを好む」家庭用設定の
  断定として書く部分のみが、商業貯蔵RHと家庭用ドロワー分類の混同に
  よる誤り。
- 証跡: `er012_output/open138_household_fact03_reverify_01/
  fact_check_result.json`、`raw_usage_log.jsonl`。

## 3. Ledger修正

FACT-03を修正(v3→v4)。仕組みベースの中心主張(エチレン放出/水分保持)
は無変更。イチゴ・柑橘類の「高湿度ドロワーを好む」という家庭用設定の
断定のみを`usable: no`とし、UC Davis数値は商業貯蔵RHとしてのみ有効・
家庭用設定の裏付けには不可と明記。GE/Samsungのメーカー間不一致を
source欄に追記。改訂履歴にv4エントリを追加(過去のv2/v3履歴は監査証跡
として無変更のまま保持)。他FACT(FACT-01/02/04)は無変更。

## 4. Downstream影響

- 完成記事本文(A2/B1、2026-08-17承認)は既存policyにより遡及修正しない。
  B1記事33行目のみがFACT-03由来の該当文。
- Trial-07の12本: FAIL 2本・REVIEW_REQUIRED 5本(計7/12)が同一論点を
  指摘していた。v4 Ledgerを使えば、当該文言自体が生成されなくなる想定
  のため、次回Discovery再実行時はこれらの指摘は発生しない見込み。
- 今後のDiscovery Trial再実行・記事再生成は、v4版
  (`verified_fact_ledger.txt`、2026-09-09時点最新)を使用すべき。

## 5. コスト・Gate 4

再検証コスト実測: 入力55,228 / 出力4,254トークン、`gpt-5.6-luna`、
約¥2.6(予算¥40以内)。ログ: `er012_output/
open138_household_fact03_reverify_01/raw_usage_log.jsonl`。Ledger修正
による将来コストの増減なし(既存Fact Safety経路の再利用のみ)。新Fact
policyの追加はゼロ、既存仕様の適用のみ。
