# FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10 — Report

管理ID: FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10(Lane A、D-4派生)。
実施日: 2026-09-09。実施者: Sonnet(sonnet-worker、Fable委任、前担当が
バックグラウンド待機で停止したため引き継ぎ)。**Trial(Production実装ではない)**。
Production/Prompt/共有module/registry/SSOT編集・Ledger改変・Fact Checker緩和・
Git操作は一切行っていない。TTSは実行していない(text-only)。Role文字列の
ヒューリスティック分類は行っていない(D-2=(a)を踏襲)。バックグラウンド待機・
二重起動なし(引き継ぎ時点で全12本のcombo runは前担当により既に完了しており、
実行中プロセスも残っていなかったことを`tasklist`と出力ファイルで確認した上で、
集計・分析作業のみを同期実行した)。

## 前提・比較条件

Household Verified Fact Ledger **v5**(無変更)を`prod_gen.THEMES`経由で参照
(Gate 4で`ledger_has_v5_marker`を機械確認)。

- **current_focus(Before)**: 現行Discovery Focus Module本体(Trial-05/07/08/09と
  一字一句同一)。
- **cautionary_constrained(After)**: 未承認候補(Part B案1)。既存の断定回避段落の
  末尾へ、以下の1文のみ追加(他は現行版と一字一句同一)。

> 「また、PointやIn One Lineの締めくくりとして、聞き手に「取扱説明書」「メーカーの
> 案内」「専門家」など、記事の外にある情報源を確認するよう呼びかける、独立した
> 注意喚起・保険的な一文を書かないでください。事実に限界がある場合(情報源同士で
> 見解が分かれている、条件によって結果が異なる、等)は、聞き手に別の場所を確認
> させるのではなく、その限界がどこにあるかを本文の説明の一部として自然に書く
> ところで止めてください。ただし、Verified Fact Ledgerが、その注意喚起自体を記事の
> 発見の一部として明示している場合はこの限りではありません(この例外は、直前の
> 断定回避の原則と同じく、Ledgerの記述を優先します)。」

harness: `er011_discovery_stage4_cautionary_language_trial_10.py`(root、前担当が
新規作成、Trial-09のharnessを再利用)。Gate 4静的diff(Production関数再定義なし、
baseline/current/cautionaryの差分が単一insertのみ、Ledger v5マーカー確認)**PASS**
(`er011_output/discovery_stage4_cautionary_language_trial_10/gate4_static_check.json`)。

N=3 × A2/B1B × 2条件 = **12本(text-only)完走**(縮小なし、追加runは不要だった)。

## 費用(実測、Fact Checker分離)

合計 **¥100.5**(上限¥130以内)。今回の引き継ぎ作業(集計・Part A/B/C分析・
comparison.html生成)は全て既存データのregex静的走査のみで追加API呼び出し
**¥0**(追加上限¥60以内)。内訳:
`er011_output/discovery_stage4_cautionary_language_trial_10/cost_summary.json`
(条件別: current_focus ¥52.8 / cautionary_constrained ¥47.7)。Fact Checker費用は
`web_search_call_count>0`のログレコードで分離: **Fact Checker ¥73.1(11件)** /
それ以外(writer・Evidence Compression・ledger逸脱チェック・directional
precheck等)¥27.4(71件)。ログ: `raw_usage_log.jsonl`。

## Part A: 保険文の発生源・頻度

検出規則(静的regex、$0、`part_a_insurance_sentence_summary.json`/
`part_a_insurance_sentence_detail.json`): 動詞(check/consult/ask/see/refer to/
look at/read/follow)+外部情報源名詞(instructions/manual/guide/manufacturer/
maker/professional/expert/label/packaging)が80文字以内で共起する文
(BROAD)。うち`instead of`/`rather than`等の対比句を伴うもの(D-4実例
"check your own refrigerator's guide instead of relying on a simple category
rule"と同型)をSTRICTとして区別。

| 対象 | 条件 | runs_with_hit | 検出文 |
|---|---|---|---|
| Trial-10(本Trial) | current_focus | 2/6 | A2 run3, B1B run3 |
| Trial-10(本Trial) | cautionary_constrained | 0/6 | なし |
| Trial-09(既存、$0再集計) | current_focus | 2/6 | A2 run2("follow your…guidance"、BROADのみ), A2 run3(STRICT) |
| Trial-09(既存、$0再集計) | adjusted_focus | 0/6 | なし |
| Trial-07(既存、$0再集計、別トピック) | baseline / discovery_focus | 0/6, 0/6 | なし |

**発生源**: 保険文は、Household Ledger v5が持つ「商業保管条件(相対湿度
90〜95%)は家庭用ドロワー設定と直結せず、家電メーカー間でも見解が割れる」
という争いのある事実(FACT-03系)を記事が明示的に取り上げた回(current_focus
条件でこの争点に触れた4本中3本、75%)にのみ出現した。この争点に触れなかった
runでは、両条件・全Trialを通じて一度も出現しなかった(0/16)。すなわち、
Discovery Focus Module本体が汎用的に保険文を誘発しているのではなく、Writerが
「事実の限界の書き方」を自由裁量に委ねられた状態で、争いのある事実に遭遇した
ときの既定の逃げ道(default completion)として選びやすい表現だと分かった。

## Part B: 最小制約文言とProduction原則との照合

適用文言は上記(全文)。Gate 4で確認した性質: (1) 既存の断定回避段落への
単一insertのみ(`current_vs_cautionary_body_diff_op_count`=1)、(2) 事実の限界を
書くこと自体は禁止せず、書き方(独立した外部参照の呼びかけ)のみを制約、
(3) Verified Fact Ledgerが注意喚起自体を発見として明示する場合は例外とし、
Trial-08/09で承認候補となった「断定回避の原則はLedgerの記述を優先する」という
既存パターンと同じ設計。Production側(`er003_v1_n3_01_articles_generate.py`)を
grepした限り、外部情報源への確認を促す既存の安全要件は見当たらず、本文言と
矛盾する既存Production原則は確認されなかった。Fact Checker側の緩和は一切なし
(無変更)。

## Part C: Before/After比較(N=3×A2/B1B)

| 条件 | Lv | run | fact_verdict | ledger | word_count | 保険文(BROAD) |
|---|---|---|---|---|---|---|
| current_focus | A2 | 1 | PASS | COMPLIANT(0) | 292 | 0 |
| current_focus | A2 | 2 | PASS | COMPLIANT(0) | 323 | 0 |
| current_focus | A2 | 3 | PASS | COMPLIANT(0) | 289 | **1** |
| current_focus | B1B | 1 | PASS | COMPLIANT(1件, MINOR) | 268 | 0 |
| current_focus | B1B | 2 | PASS | COMPLIANT(0) | 314 | 0 |
| current_focus | B1B | 3 | PASS | COMPLIANT(0) | 312 | **1** |
| cautionary_constrained | A2 | 1 | PASS | COMPLIANT(0) | 309 | 0 |
| cautionary_constrained | A2 | 2 | **未到達(NG_REVIEW_REQUIRED)** | - | 301 | 0 |
| cautionary_constrained | A2 | 3 | PASS | COMPLIANT(0) | 290 | 0 |
| cautionary_constrained | B1B | 1 | PASS | COMPLIANT(0) | 343 | 0 |
| cautionary_constrained | B1B | 2 | **REVIEW_REQUIRED** | COMPLIANT(0) | 384 | 0 |
| cautionary_constrained | B1B | 3 | PASS | COMPLIANT(0) | 289 | 0 |

- **保険文**: Before 2/6(33%)→After 0/6(0%)。出現していた2本と同じ争点
  (ストロベリー/オレンジの家庭用不一致)をAfterでも3本(A2 run2, B1B run2,
  B1B run3)が扱ったが、いずれも「限界を本文の説明として書く」形へ置き換わり、
  外部参照の呼びかけは一度も出なかった(狙いどおりの挙動)。
- **REVIEW率**: Before 0/6(0%)→After 2/6(33%、A2 run2はPoint-vs-Story類似度
  0.474で既存Point Overlap安全機構がPoint単独regenerationを禁止
  [ER-008-N8-FINAL-QA-HARDENING-21]しFact Checker未到達のままNG、
  B1B run2はFact Checkerが「バナナ冷蔵可能期間の一般化」「エチレン感受性の
  一般化」という2件の非関連claimを指摘)。**両件とも内容が本Part Bの追加文言
  (保険文の禁止)とは無関係**(不当な一般化・overlapという既存QA機構の指摘で
  あり、Trial-09のadjusted_focusで見られた「追加文言がLedgerのあいまいさを
  より積極的に書かせた結果REVIEWが増えた」という因果関係とは異なる)。N=3は
  小さく、偶然のrun間ばらつきと区別できないため、この上振れをPart Bの副作用と
  断定はしない。
- **overlap**: cross_point_overlap flagged=0/12(全run)。Point One/Two分化は
  両条件で維持。
- **語数・A2の不自然な簡略化**: current_focus A2平均301.3語、cautionary_
  constrained A2平均300.0語(NG判定のrun2含む)でほぼ同水準。目視でも
  cautionary_constrained A2の3本(`comparison.html`)は現行版と同程度の
  具体性・自然さを保っており、不自然な簡略化・情報量の欠落は確認されなかった。
- **安全側指標**: blocking(FAIL)=0/12、創作(Local Rewrite human review)=
  0/12。Fact Safety・Ledger Deviation機構はPart Bにより緩和・変更されていない。

## D-2目視artifact

`er011_output/discovery_stage4_cautionary_language_trial_10/comparison.html`
(file:///C:/Users/tensh/eigo-radio/er011_output/discovery_stage4_cautionary_language_trial_10/comparison.html)。
Before/After(current_focus/cautionary_constrained)をA2/B1B・run1〜3で並置し、
記事全文をそのまま掲載、保険文検出regex一致箇所を`<mark>`でハイライトした
(Source列なし、標準規則に準拠)。12本の`fact_verdict`/`ledger_status`/
`word_count`/保険文検出数の一覧表も同ページ冒頭に掲載。生成スクリプト:
`er011_discovery_stage4_cautionary_language_trial_10_comparison.py`(root、
新規、$0、閲覧用HTML生成のみ)。

## Gate 1分類: **VALIDATED**(Trial範囲。Production採用は未承認)

1. Part Bの最小制約文言は、この文言が過去2回(Trial-09/10)で実際に保険文を
   誘発した争点(争いのある家庭用ガイド)を扱った全runで保険文を0件に抑え、
   狙った効果を確認した。争点を扱わないrunへの副作用(過度な簡略化・overlap
   悪化)も確認されなかった。
2. Fact Safety自体は両条件・全12本で維持(blocking 0件、Ledger Deviation
   0件、創作0件)。cautionary_constrained側でREVIEW率が上振れした2件は、
   内容的にPart Bの追加文言とは無関係な既存QA機構(Point Overlap安全機構、
   Fact Checkerの一般化precision指摘)による判定であり、Part B自体が新規の
   fabricationリスクや安全低下を生んだ証跡はない。
3. ただしN=3(合計12本)は小さく、REVIEW率の上振れ(0%→33%)が本当に無関係かは
   本Trialだけでは断定できない。VALIDATEDはTrial範囲の効果確認までであり、
   Production採用(`APPROVED_FOR_PRODUCTION`)・`editorial_mode="discovery_why"`の
   正式登録には別途ユーザー承認とより大きいNでの追試を要する。

## USER_DECISION_REQUIRED候補

- Part B文言をProduction Discovery Focus Moduleへ正式採用するか(現時点では
  未承認候補のまま)。
- 採用する場合、`editorial_mode="discovery_why"`の正式registry登録が別途必要
  (本Trialでは未登録の想定名のまま使用)。

## Household一本化候補(記事→Support→Audio)へ進めて良いかの所見

**現時点では推奨しない(条件付き)。** 根拠:
- 良好な点: 保険文問題(D-4で見つかった実例そのもの)への対処は本Trialの
  N=3範囲で機能し、Fact Safety・overlap・語数のいずれにも悪化は見られない。
- 不成立/保留の根拠: (1) Part B文言はまだ「未承認候補」でありProduction
  Prompt側は無変更のまま(現状のHousehold一本化はcurrent_focus=Beforeの
  ままになり、D-4の問題は未解決で流れる)。(2) After条件でREVIEW率が0%→33%へ
  上振れした事象の因果関係が本Trialのみでは断定できていない(3項目で述べた
  通り内容的には無関係と見えるが、N=3のため統計的に確認とは言えない)。
- 推奨: Part BをProduction採用するかどうかをユーザーに諮った上で、(a)採用
  する場合はもう1ラウンド(N=5程度)の追試でREVIEW率上振れの再現性を確認して
  からHousehold一本化へ進む、(b)採用しない場合はcurrent_focus(Before)のまま
  Household一本化を進め、D-4の保険文問題は別途Human Reviewでの目視修正に
  委ねる、のいずれかをFable/ユーザーに判断してもらう。

## STOP条件該当

非該当: Fact Checker/Ledger側の変更は不要(v5は無変更のまま使用)。新原則の
追加はしていない(既存の断定回避段落への1文追加のみ)。費用は前担当実測分
¥100.5(上限¥130以内)+本引き継ぎ作業¥0(追加上限¥60以内)。新規failure mode
なし。Production・共有module変更は行っていない。

## 禁止事項の遵守

Fact Checker緩和なし(無変更)。Ledger改変なし(v5を読み取り専用で使用)。
Production/Prompt/共有module/registry/SSOT編集なし。Git操作なし。TTS未実行。
Role文字列分類は実施していない。バックグラウンド待機・二重起動なし
(引き継ぎ時点で全runは完了済みであることを`tasklist`と出力ファイルで確認して
から同期作業のみ実施)。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集して
いない。Household完成版の再生成は行っていない。

## 成果物一覧

- `er011_discovery_stage4_cautionary_language_trial_10.py`(root、前担当作成、
  harness、無変更のまま流用)
- `er011_discovery_stage4_cautionary_language_trial_10_comparison.py`(root、
  本引き継ぎで新規作成、D-2目視artifact生成)
- `FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10_REPORT.md`(本ファイル)
- `er011_output/discovery_stage4_cautionary_language_trial_10/`
  - `gate4_static_check.json` / `audit_current_focus_block.txt` /
    `audit_cautionary_focus_block.txt` / `audit_current_vs_cautionary_diff.txt`
  - `run_metadata.json` / `cost_summary.json` / `raw_usage_log.jsonl`
  - `all_results_so_far.json` / `_combo_results/*.json`(12本分)
  - `{a2,b1b}/{current_focus,cautionary_constrained}/run{1,2,3}/`(article.md、
    run_summary.json、analysis.json、fact_qa.json、point_overlap_qa.json、
    ledger_deviation.json等)
  - `part_a_insurance_sentence_summary.json` /
    `part_a_insurance_sentence_detail.json`(本引き継ぎで新規作成、Part A集計)
  - `part_c_combined_table.json`(本引き継ぎで新規作成、Part C集計中間出力)
  - `comparison.html`(D-2目視artifact)
