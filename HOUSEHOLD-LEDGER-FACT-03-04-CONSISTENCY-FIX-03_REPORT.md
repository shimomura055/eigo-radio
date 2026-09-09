# HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03(OPEN-138継続)

管理ID: HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03(Sonnet、Fable委任、
OPEN-138継続、「自明な修正は自律」の範囲)。SSOT・Git操作は一切行っていない。
Production関数・Prompt・共有moduleの編集なし。記事再生成なし。

## 1. 矛盾の特定

対象: `er003_output/n3_01/household/research/verified_fact_ledger.txt`
(A2/B1共通source of truth)。

- **FACT-03(v4、修正前)原文**: 「りんご・洋梨・バナナ・トマトなどエチレンを
  多く放出する食品は低湿度ドロワーが適する」(=冷蔵庫の低湿度ドロワーに
  置くべき例としてバナナ・トマトを列挙)。
- **FACT-04(v2確定、無変更)原文**: 「トマトとバナナは冷蔵保存に適さず、
  常温(カウンター等)での保存が推奨される」。
- 両者は同一Ledger内で、同一2品目(バナナ・トマト)について「冷蔵[低湿度
  ドロワー]を勧める」(FACT-03)と「非冷蔵[常温保存]を勧める」(FACT-04)
  という直接矛盾する指示を与えていた。この矛盾はFACT-03のv3→v4修正(2026-
  09-09、HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01)がイチゴ・柑橘類の例
  のみを是正し、v3から無変更だったバナナ・トマトの列挙をそのまま残したこと
  に起因する。Discovery段階2 Trial-08が独立Fact Checkerの指摘として非決定的
  に顕在化させた。

## 2. v5修正(最小、削る方向のみ)

- FACT-03の低湿度ドロワー適合例から**バナナ・トマトを削除**し、りんご・
  洋梨のみに絞り込んだ。バナナ・トマトを除外した理由(FACT-04参照)を
  同文中に明記。
- `confidence`・`usable`欄・`notes_for_writer`に、バナナ・トマトを低湿度
  ドロワーの例として書かないことを明記(v5追加note)。
- 改訂履歴にv5エントリを新規追加(v2〜v4は監査証跡として無変更保持)。
- **FACT-04は無変更**(diff未検出をgrepで確認)。新しい事実主張は追加せず、
  v4のsource(Iowa State Extension等)で裏付けられる範囲で削るのみ。

## 3. Fact Checker確認(既存Production経路、2 claimのみ)

新規薄いスクリプト`er012_open138_household_fact0304_consistency_fix_03.py`
(既存`er002_ja_web_research_r3.make_fact_checker_fn`/
`run_fact_checker_with_gates`をそのまま呼び出し、Production同一関数)で、
FACT-03(v5)「りんご・洋梨などのエチレン排出食品は低湿度ドロワーが適する」
とFACT-04「トマト・バナナは冷蔵に適さず常温推奨」の2 claimのみを検証。

- run1(過度に絶対的な言い回し"not suited at all"/"any drawer"で表現): 
  **verdict=FAIL**。ただしFAILの内容はFACT-03/04間の矛盾ではなく、私の
  paraphraseがFACT-04本来の言い回しより絶対的すぎたことに対する外部情報
  (完熟バナナ・カットトマトは短期冷蔵可)との齟齬。
- run2(Ledger原文に忠実な言い回しへ修正): **verdict=PASS**、
  contradictions=[]。「りんご・洋梨=低湿度ドロワー」と「バナナ・トマト=
  常温推奨」は両立すると判定。
- 証跡: `er012_output/open138_household_fact0304_consistency_fix_03/
  fact_check_result.json`(run1)、
  `.../run2_literal_ledger_wording/fact_check_result.json`(run2、PASS)。
- 費用実測: run1 ¥1.60 + run2 ¥1.71 = **合計¥3.31**(上限¥15以内)。
  `pricing_snapshot.json`単価・1USD=160円で計算。ログ: 各run配下の
  `raw_usage_log.jsonl`。

## 4. Downstream影響

### Discovery段階2 Trial-08(8本、再生成せず本文を目視・grep確認のみ)

`er011_output/discovery_stage2_interpretation_rule_trial_08/{a2,b1b}/
{current_focus,adjusted_focus}/run{1,2}/article.md`全8本を確認した結果、
FACT-03(v4)/FACT-04矛盾を含む本文は**4/8**:
- `a2/current_focus/run1`(未flagged、非決定的に見逃されPASS判定だった)
- `a2/adjusted_focus/run1`(Trial-08レポートでREVIEW_REQUIRED済み)
- `b1b/adjusted_focus/run1`(未flagged、PASS判定だった)
- `b1b/adjusted_focus/run2`(Trial-08レポートでREVIEW_REQUIRED済み)

残り4/8(`a2/current_focus/run2`、`a2/adjusted_focus/run2`、
`b1b/current_focus/run1`、`b1b/current_focus/run2`)は元々バナナ・トマトを
低湿度ドロワー例に含めておらず矛盾なし。**再生成は行っていない**(指示
どおり列挙のみ)。今後のDiscovery段階2再実行はv5 Ledgerを使用すること。

### Household FACT-03最小修正(revision3a、B1B point_one)

`er003_output/n3_01/household/fact03_fix_02/b1b/article.md`を確認した結果、
低湿度ドロワーの例は「apples and pears」のみ(19行目)、バナナ・トマトは
常温保存の文脈でのみ言及(37行目)であり、v5と**矛盾しない**
(revision3aはFACT-03のイチゴ・柑橘類部分[point_one]のみを修正対象とし、
元々バナナ・トマトを低湿度ドロワー例に含めていなかったため)。

## 5. Gate 4 / 禁止事項の遵守

新policyの追加なし。Production関数・Prompt・共有module・SSOT・Gitは
一切変更していない。他FACT(FACT-01/02/04)は無変更(FACT-04はgrep差分
ゼロで確認)。記事の再生成は行っていない。バックグラウンド待機なし。

## 6. 変更/新規ファイル一覧

- 変更: `er003_output/n3_01/household/research/verified_fact_ledger.txt`
  (FACT-03 v4→v5、FACT-04は無変更)
- 新規: `er012_open138_household_fact0304_consistency_fix_03.py`(root)
- 新規: `er012_output/open138_household_fact0304_consistency_fix_03/`
  (`raw_usage_log.jsonl`・`fact_check_result.json`[run1、FAIL、
  paraphrase起因]・`run2_literal_ledger_wording/`[run2、PASS])
- 新規: 本ファイル`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03_REPORT.md`
