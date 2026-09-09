# FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09 — Report

管理ID: FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09(Lane A、D-3=(a))。
実施日: 2026-09-09。実施者: Sonnet(sonnet-worker、Fable委任)。**Trial
(Production実装ではない)**。Production/Prompt/共有module/registry/SSOT
編集・Ledger改変・Fact Checker緩和・Git操作は一切行っていない。TTSは実行
していない(text-only)。Role文字列のヒューリスティック分類は行っていない
(D-2=(a)を踏襲)。バックグラウンド待機は、Bashツールの120秒タイムアウトに
よる自動退避、および進行状況確認のための`sleep`単独コマンドのみで、意図的な
放置待機ではない(各combo完了を都度確認しながら逐次進行した)。完了報告後の
自動復帰はしない。

## 前提・比較条件

Household Verified Fact Ledger **v5**
(`er003_output/n3_01/household/research/verified_fact_ledger.txt`、
`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03_REPORT.md`でFACT-03の
低湿度ドロワー適合例からバナナ・トマトを除外しFACT-04との矛盾を解消済み)を
`prod_gen.THEMES`経由でそのまま参照した(独立コピーなし、Gate 4で
`ledger_has_v5_marker`を機械確認)。

- **current_focus**: Trial-05/07/08と一字一句同一の現行Discovery Focus
  Module本体(見出しのみ改稿)。
- **adjusted_focus**: Trial-08 Part A案1と完全同一文言(断定回避段落末尾へ
  Trend Synthesis Focus Module:389-390と同型のscope一般化禁止文を追加。
  案2[位置移動]は不使用)。

harness: `er011_discovery_stage3_rule_adjustment_trial_09.py`(root新規、
Trial-08のharnessを再利用)。Gate 4静的diff(Production関数再定義なし、
baseline/current/adjustedの差分が単一insertのみ、Ledger v5マーカー確認)
**PASS**(`er011_output/discovery_stage3_rule_adjustment_trial_09/gate4_static_check.json`)。

N=3 × A2/B1B × 2条件 = **12本(text-only)完走**(縮小なし)。

## 費用(実測、Fact Checker分離)

合計 **¥127.3**(上限¥130以内)。内訳:
`er011_output/discovery_stage3_rule_adjustment_trial_09/cost_summary.json`
(条件別: current_focus ¥63.0 / adjusted_focus ¥64.3)。Fact Checker費用は
`web_search_call_count>0`のログレコード(本パイプラインでweb検索を使うのは
Fact Checkerのみ)で分離: **Fact Checker ¥96.6(12件)** / それ以外(writer・
Evidence Compression・ledger逸脱チェック・directional precheck等)¥30.7
(80件)。`cost_fact_checker_split.json`。ログ: `raw_usage_log.jsonl`。

## 12本結果表

| 条件 | Lv | run | status | fact_verdict | unsupported | claim→evidence | ledger | cross_point_overlap(P1↔P2) | word_count | word overflow(P1/P2) |
|---|---|---|---|---|---|---|---|---|---|---|
| current_focus | A2 | 1 | OK | PASS | 0 | - | COMPLIANT | 0.115/0.182 | 338 | 超過/超過 |
| current_focus | A2 | 2 | OK | PASS | 0 | - | COMPLIANT | 0.138/0.138 | 288 | なし/なし |
| current_focus | A2 | 3 | OK | **REVIEW_REQUIRED** | 1 | FACT-03 | COMPLIANT | 0.163/0.174 | 305 | 超過/超過 |
| current_focus | B1B | 1 | OK | PASS | 0 | - | COMPLIANT | 0.109/0.140 | 345 | 超過/超過 |
| current_focus | B1B | 2 | OK | PASS | 0 | - | COMPLIANT | 0.088/0.107 | 285 | なし/なし |
| current_focus | B1B | 3 | OK | PASS | 0 | - | COMPLIANT | 0.167/0.200 | 309 | なし/なし |
| adjusted_focus | A2 | 1 | OK | **REVIEW_REQUIRED** | 1 | FACT-03(keyword)/非Ledger起因(後述) | COMPLIANT | 0.226/0.233 | 272 | なし/なし |
| adjusted_focus | A2 | 2 | OK | **REVIEW_REQUIRED** | 3 | 未マッチ×3(後述でFACT-03起因と判定) | COMPLIANT | 0.182/0.140 | 298 | 超過/超過 |
| adjusted_focus | A2 | 3 | OK | PASS | 0 | - | COMPLIANT | 0.156/0.194 | 319 | 超過/超過 |
| adjusted_focus | B1B | 1 | OK | PASS | 0 | - | COMPLIANT | 0.100/0.088 | 280 | なし/なし |
| adjusted_focus | B1B | 2 | OK | PASS | 0 | - | COMPLIANT | 0.139/0.167 | 328 | なし/なし |
| adjusted_focus | B1B | 3 | OK | PASS | 0 | - | COMPLIANT | 0.091/0.086 | 309 | 超過/超過 |

blocking(FAIL)=**0/12**。Ledger Deviation=**0/12**。Local Rewrite=
**0/12**(創作0)。cross_point_overlap flagged=**0/12**(全run、Point One/
Two分化は両条件で維持)。全生データ:
`er011_output/discovery_stage3_rule_adjustment_trial_09/{a2,b1b}/{current_focus,adjusted_focus}/run{1,2,3}/`。

補足(主要指標外の別QA機構): `current_focus/A2/run2`のみ、既存の比較方向Fact
事前チェック(ER-008-DIRECTIONAL-FACT-PRECHECK-08、fact_verdictとは別機構)が
`DIRECTION_REVIEW_REQUIRED`を返した(fact_verdict自体はPASS)。本Trialの
主要指標(fact_verdict)には算入していない。

## FACT-03/04起因かどうかの判定(claim単位)

機械分類(英語キーワード一致)はFact Checker出力(日本語)の一部claimで
イチゴ/柑橘の日本語表記("イチゴ""柑橘")を拾えず`LEDGER_OUTSIDE_OR_NO_
LEXICAL_MATCH`と誤分類した。Ledger v5本文(FACT-03、114-147行)を直接
参照して手動で再判定した。

1. **current_focus A2 run3(1 claim)**: 「商業保管の相対湿度90〜95%だけ
   では家庭用引き出しの最適設定は決まらない」。**FACT-03(v5)起因**
   ——Ledger自身が明記する内容(商業条件と家庭用設定は同一視できない、
   メーカー間で見解が割れる)をほぼそのまま転記したものだが、記事本文に
   直接の出典を示していないためFact Checkerが指摘。Ledgerとの矛盾では
   なく、Ledgerが元々含むあいまいさの引用元不足。
2. **adjusted_focus A2 run1(1 claim)**: 「Leafy greens such as kale and
   broccoli」という表現(ブロッコリーは厳密には葉物野菜に分類されない)。
   機械分類はキーワード一致でFACT-03と判定したが、**実質はFACT-03/04
   非起因**——高湿度ドロワーへの分類自体はLedgerと矛盾せず、単なる
   カテゴリー名称の精度指摘(taxonomy nitpick)。
3. **adjusted_focus A2 run2(3 claims)**: いずれもイチゴ・柑橘の家庭用
   ガイド不一致、および「多くの冷蔵庫に2設定」という一般化の裏付け
   不足。**FACT-03(v5)起因**——(1)と同様、Ledgerが元々明記する
   あいまいさを記事が明示的に取り上げた結果、引用元不足としてFact
   Checkerが指摘した。scope一般化禁止文がこのあいまいさをより積極的に
   書かせた可能性がある(後述の観察)。

## FACT-03/04起因除外後の「真のREVIEW_REQUIRED」率

| 条件 | raw REVIEW+FAIL | FACT-03/04起因のみのrun(除外) | 真のREVIEW_REQUIRED |
|---|---|---|---|
| current_focus | 1/6(17%) | 1/6(A2 run3、claim全てFACT-03起因) | **0/6(0%)** |
| adjusted_focus | 2/6(33%) | 1/6(A2 run2、claim全てFACT-03起因) | **1/6(17%、A2 run1、非Ledger起因のtaxonomy指摘)** |

raw REVIEW率・真のREVIEW率のいずれでも、adjusted_focusはcurrent_focusを
**下回らなかった**(raw: 33%>17%、真: 17%>0%)。本Trialの主目的(REVIEW
削減)はN=3の範囲では達成が確認できなかった。

## 観察(目視評価用artifactに委ね、短く記録)

- 安全側指標(blocking・Ledger Deviation・Local Rewrite・cross_point_overlap
  flagged)は両条件・全12本で0件。scope一般化禁止文の追加によるFact
  Safety・重複面での新規リスクは確認されなかった。
- adjusted_focus条件のPoint本文(特にA2)は、イチゴ・柑橘の「家庭用ガイドが
  一致しない」という限定文言をcurrent_focusより頻繁に明示的に書く傾向が
  見えた(A2 run2・run3)。scope一般化禁止文が意図どおり「Ledgerが名指し
  していない範囲への一般化」を避けさせている可能性はあるが、その結果
  Fact Checkerが「本文中に出典引用がない」と指摘する頻度が上がった。
- Point One/Two語数・cross_point_overlap比率のレンジは両条件でおおむね
  重なっており(cross_point_overlap 0.086〜0.233)、本Trialのサンプルからは
  分化度の系統差は見えなかった。
- Discoveryらしさ・Pointの深さ・多様性・型にはまりすぎていないかの評価は
  目視判断に委ねる(`comparison.html`参照)。

## D-2目視artifact

`er011_output/discovery_stage3_rule_adjustment_trial_09/comparison.html`
(file:///C:/Users/tensh/eigo-radio/er011_output/discovery_stage3_rule_adjustment_trial_09/comparison.html)。
Household原本(2026-08-17承認、Ledger v5適用前、参考)・current_focus/
adjusted_focus各run1〜3のPoint One/Two本文を、条件×level×runで並置し、
各Pointにcross_point_overlap・Fact結果(directional precheckを含む)を
併記した。Role文字列のヒューリスティック分類は行っていない(D-2=(a))。
多様性・深さ・型感の最終判断はFable/ユーザーの目視に委ねる。

## Gate 1分類: **REJECTED**(主目的[REVIEW削減]は未達成、安全性は維持)

1. raw REVIEW率・FACT-03/04起因除外後の「真のREVIEW率」のいずれでも、
   adjusted_focusはcurrent_focusを上回った(削減どころか同等〜悪化)。
   ユーザー決定の目的「REVIEW_REQUIREDを減らせるか」はN=3の範囲で
   **達成されなかった**。
2. Fact Safety自体は両条件で維持(blocking 0件、Ledger Deviation 0件、
   創作0件)——adjusted_focusが危険というわけではないが、意図した効果
   (REVIEW削減)も確認できなかった。
3. N=6/条件は小さく、この1回のTrialのみで完全に否定するには弱いが、
   方向性が「削減」ではなく「同等〜微増」で一貫していたため、Production
   配線候補としては推奨しない。
4. Discoveryらしさ・深さ・多様性・型感はFable/ユーザーの目視判断
   (`comparison.html`)に委ねる——これらの軸でadjusted_focusに明確な
   優位性が確認されれば、REVIEW率の結果と合わせて再検討の余地はある
   (その場合はユーザー判断次第でUSER_DECISION_REQUIRED相当として
   再考可能)。

Production配線に必要な項目(未承認候補のまま): Focus Module文言変更
(scope一般化禁止の1文追加)、`editorial_mode="discovery_why"`の正式登録。
いずれも本Trialの結果からは推奨されない。

## STOP条件該当

非該当: Fact Checker/Ledger側の変更は不要(Ledger v5は既に確定済みで
無変更のまま使用)。新原則の追加はしていない(既存文言の再利用のみ)。
費用¥127.3(上限¥130以内、縮小なし)。新規failure modeなし(FACT-03の
商業/家庭差あいまいさはLedger自身に既に記載済みの既知事項)。Production・
共有module変更は行っていない。

## 禁止事項の遵守

Fact Checker緩和なし(Fact Checker関数・閾値は無変更、Trial-07/08と同一
参照元)。Ledger改変なし(v5を読み取り専用で使用しただけ、書き込みなし)。
Production/Prompt/共有module/registry/SSOT編集なし。Git操作なし。TTS
未実行。Role文字列分類は実施していない。バックグラウンド待機は各combo
完了確認のための`sleep`単独コマンド・120秒タイムアウト自動退避のみ
(意図的な放置待機ではなく、進行を都度確認しながら逐次進行した)。完了後の
自動復帰はしない。

## 成果物一覧

- `er011_discovery_stage3_rule_adjustment_trial_09.py`(root、新規、harness)
- `er011_discovery_stage3_rule_adjustment_trial_09_batch_runner.py`(root、
  新規、複数comboを1プロセスで逐次実行する一時ヘルパー)
- `er011_discovery_stage3_rule_adjustment_trial_09_comparison.py`(root、
  新規、D-2目視artifact生成)
- `FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09_REPORT.md`(本ファイル)
- `er011_output/discovery_stage3_rule_adjustment_trial_09/`
  - `gate4_static_check.json` / `audit_current_focus_block.txt` /
    `audit_adjusted_focus_block.txt` / `audit_current_vs_adjusted_diff.txt`
  - `run_metadata.json` / `cost_summary.json` / `cost_fact_checker_split.json`
    / `raw_usage_log.jsonl` / `batch_runner_log.txt`
  - `all_results_so_far.json` / `_combo_results/*.json`(12本分)
  - `{a2,b1b}/{current_focus,adjusted_focus}/run{1,2,3}/`(article.md、
    run_summary.json、analysis.json、fact_qa.json、point_overlap_qa.json等)
  - `comparison.html`(D-2目視artifact)
