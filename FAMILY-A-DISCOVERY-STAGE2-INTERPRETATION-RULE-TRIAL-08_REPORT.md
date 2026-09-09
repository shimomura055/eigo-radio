# FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08 — Report

管理ID: FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08(Lane A Discovery
再改善、D2-UDR-1再改善)。実施日: 2026-09-09。実施者: Sonnet(sonnet-worker、
Fable委任)。**Trial(Production実装ではない)**。Production/Prompt/共有module/
registry/SSOT編集・Ledger改変・Fact Checker緩和・Git操作は一切行っていない。
TTSは実行していない(text-only)。Role文字列のヒューリスティック分類は行って
いない(D-2=(a)、Point本文の目視比較へ切り替え)。

## Part A: 既存断定回避規則が効いていない理由の分析(¥0、机上)

### A.1 Trial-07 REVIEW_REQUIRED 10 claim(discovery_focus)+baseline 2 claim
の分類

対象規則: `er011_open112_a_family_4layer_prompt_trial_05.DISCOVERY_FOCUS_MODULE_BLOCK`
内、断定回避段落(現行版:161-165相当、「Evidenceが支持する範囲を超えて...
「自動的」「不随意的」「必ず」のような断定表現は使わないでください」)。
Trend Synthesis Focus Module(`er003_v1_n3_01_articles_generate.py:385-393`、
「証拠が一部の当事者・一部の期間・一部の地域にしか及ばない場合は、その範囲を
実際より広く一般化しないでください」)を対称比較対象とした。

| # | 条件/run | claim要旨 | 誘発文言 | 該当規則 | 遵守有無 | 分類 |
|---|---|---|---|---|---|---|
|1|focus a2/run1 FAIL|柑橘類(オレンジ)高湿度の一括分類|なし(Ledger FACT-03の直接転記)|適用外|遵守(断定語未使用)|**Ledger起因**(v4で解消見込み)|
|2|focus a2/run2 REVIEW|柑橘類高湿度「may prefer」|なし(Ledger FACT-03直接転記)|適用外|遵守(hedge語"may")|**Ledger起因**(v4で解消見込み)|
|3|focus b1b/run1 c1|イチゴ/柑橘90-95%「can favor」|なし(Ledger FACT-03直接転記)|適用外|遵守(hedge語"can")|**Ledger起因**(v4で解消見込み)|
|4|focus b1b/run1 c2|エチレン影響を「他の果物・野菜」全般へ一般化|Point角度指示(仕組み探求、157-159)|161-165はscope一般化を名指ししていない|部分遵守(hedge語"may"はあるが対象範囲は無限定)|**規則の具体性不足**|
|5|focus b1b/run2 c1|りんご/洋梨/バナナ/トマト「generally」低湿度に一括|Point角度指示(仕組み探求)|同上|部分遵守(hedge語"generally"、ただし後段のFACT-04区分と矛盾)|**規則の具体性不足**|
|6|focus b1b/run2 c2|イチゴ/柑橘「some fruits prefer」|なし(Ledger FACT-03直接転記)|適用外|遵守|**Ledger起因**|
|7|focus b1b/run2 c3|クリスパー「2種類の保存スペース」を無条件断定|Point角度指示(仕組み探求)|同上|不遵守寄り(hedge語なし、Ledgerの「多くの場合」を落として断定)|**規則の具体性不足+一部不徹底**|
|8|focus b1b/run3 c1|柑橘類「favor high humidity」無hedge|なし(Ledger FACT-03直接転記)|適用外|不遵守寄り(hedge語なし)|**Ledger起因+軽微な不徹底**|
|9|focus b1b/run3 c2|ケール/ブロッコリーを「葉物」と誤分類|なし|適用外(certainty問題ではなく事実分類ミス)|該当なし|**別のfailure mode**(分類ミス、断定回避規則の対象外)|
|10|focus b1b/run3 c3|「換気要/保水要」判定テストの一般化|Point角度指示(意外な詳細)|161-165はheuristic一般化を名指ししていない|部分遵守(hedge語なし、適用範囲を限定せず)|**規則の具体性不足**|
|baseline-1|baseline b1b/run1 c1|柑橘類「prefer high humidity」無hedge|(Focus Module不使用)|適用外|N/A|**Ledger起因**(現行Production記事と同一パターン)|
|baseline-2|baseline b1b/run1 c2|じゃがいも/さつまいも/玉ねぎ/にんにく4品目一括|(Focus Module不使用)|適用外|N/A|**Ledger自体(FACT-04)のscope一般化**、Focus Module非依存|

(baseline条件はa2/run3 FAILの単独contradiction[柑橘類]を含め計2 claim
[b1b/run1]。委任文の「baseline条件の1 claim」は実データでは2 claimだった
ため、両方を分類対象とした。)

### A.2 規則が効いていない理由・最小調整案

3要因を特定した。
1. **位置**: 断定回避段落(161-165)はPoint One/Two角度指示(157-159)の
   *後*に独立した段落として置かれ、角度指示と分離している。Trend
   Synthesisの対応する抑制文言は、対象段落(Main Story/Point Two)内に
   直接埋め込まれている(375-377、385-393)。
2. **具体性**: 161-165は「断定」を3つの例示語(自動的/不随意的/必ず)+
   「why-exceeds-evidence」でのみ定義し、**scope一般化**(ある品目・条件で
   成り立つ仕組み説明を、Ledgerが名指ししていない他の品目・条件へ広げる
   こと)を禁止対象として明示していない。Trend Synthesis 389-390は
   このscope一般化を明示的に禁止している。
3. **強度の非対称**: Point角度指示(157-159)は「仕組み」探求を強い命令形で
   指示する一方、断定回避規則は語彙選択のみを制約し、範囲(scope)を
   制約していない。

**最小調整候補**(未承認候補、Production実装ではない):
- **案1(本Trialでトライアル)**: 断定回避段落の末尾へ、Trend Synthesis
  389-390と同型の1文を追加する(scope一般化の明示禁止)。新原則の追加
  ではなく既存承認済み文言の再利用。単一insert(機械assert済み)。
- **案2(未トライアル、参考)**: 断定回避段落を、位置(157-159の直後)へ
  移動する(内容不変)。案1と併用可能だが、本Trialでは案1のみを検証した
  (委任文の指定どおり)。

### A.3 FACT-03 v4除外後の「真のREVIEW_REQUIRED」再集計(Trial-07データ)

Household Ledger v4(`HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01`
[OPEN-138]、2026-09-09、柑橘類・イチゴの「高湿度ドロワーを好む」家庭用
設定を`usable: no`化)を前提に、Trial-07の12本から**柑橘類(FACT-03)の
みが原因だった**FAIL/REVIEW_REQUIREDを除外して再集計した。

| 条件 | v4前(REVIEW+FAIL) | 純粋FACT-03起因(v4で解消見込み) | v4後の「真のREVIEW_REQUIRED」 |
|---|---|---|---|
| baseline | 2/6(33%) | 1/6(a2/run3 FAIL) | 1/6(17%、b1b/run1、FACT-04起因) |
| discovery_focus | 5/6(83%) | 2/6(a2/run1 FAIL、a2/run2) | 3/6(50%、b1b/run1〜3、非FACT-03の指摘を含む) |

v4適用後もdiscovery_focus条件の「真のREVIEW」率(50%)はbaseline(17%)の
約3倍で残存する。この残差が案1(scope一般化禁止)の主なターゲットである。

## Part B: 最小Trial(N=2、費用実測¥70.8、上限¥100以内)

### 実行概要・費用縮小の判断

`er011_discovery_stage2_interpretation_rule_trial_08.py`(root、新規)。
Gate 4(Production無変更、静的diff)PASS
(`er011_output/discovery_stage2_interpretation_rule_trial_08/gate4_static_check.json`、
current_focus/adjusted_focus各々がbaseline[block=""]への単一insertである
ことを機械確認。current対adjusted本体差分も単一insert)。Household Ledger
v4を使用(`prod_gen.THEMES`経由、独立コピーなし)。

run1(4本、current_focus×adjusted_focus×A2×B1B)完了時点で実測¥35.9
(平均¥8.98/本)。12本(N=3)完走時の投影費用は約¥108でBUDGET_JPY=¥100を
超過見込みのため、**N=2(8本)へ縮小**した(Trial-07の費用超過時対応
[N=3→N=2]と同一プロトコル)。実測合計**¥70.8**(current_focus ¥32.2 /
adjusted_focus ¥38.6)。ログ:
`er011_output/discovery_stage2_interpretation_rule_trial_08/raw_usage_log.jsonl`、
`cost_summary.json`。

### 結果表(8本)

| 条件 | Lv | run | status | fact_verdict | unsupported | ledger | cross_point_overlap(P1↔P2) | word_count | word overflow |
|---|---|---|---|---|---|---|---|---|---|
| current_focus | A2 | 1 | OK | PASS | 0 | COMPLIANT | 0.107/0.154 | 348 | P1,P2とも超過 |
| current_focus | A2 | 2 | **NG_REVIEW_REQUIRED**(Overlap QA、非Fact) | None | - | - | 0.200/0.146 | 327 | P2超過 |
| current_focus | B1B | 1 | OK | PASS | 0 | COMPLIANT | 0.154/0.171 | 300 | なし |
| current_focus | B1B | 2 | OK | PASS | 0 | COMPLIANT | 0.194/0.184 | 376 | なし |
| adjusted_focus | A2 | 1 | OK | REVIEW_REQUIRED | 2 | COMPLIANT | 0.135/0.179 | 343 | P1超過 |
| adjusted_focus | A2 | 2 | OK | PASS | 0 | COMPLIANT | 0.184/0.206 | 342 | なし |
| adjusted_focus | B1B | 1 | OK | PASS | 0 | COMPLIANT | 0.116/0.156 | 321 | P1,P2とも超過 |
| adjusted_focus | B1B | 2 | OK | REVIEW_REQUIRED | 2 | COMPLIANT | 0.098/0.093 | 319 | P1,P2とも超過 |

blocking(FAIL)=**0/8**。Ledger Deviation=0/8。Local Rewrite=0/8。
cross_point_overlap flagged=**0/8**(全run、Point One/Two分化は両条件で
維持)。全生データ:
`er011_output/discovery_stage2_interpretation_rule_trial_08/{a2,b1b}/{current_focus,adjusted_focus}/run{1,2}/`。

### 予期しない発見(STOP条件該当、Ledger側の追加課題)

adjusted_focus/a2/run1のREVIEW_REQUIRED 2 claimは、**Household Ledger v4
のFACT-03修正時に追加された文言**「りんご・洋梨・バナナ・トマトなど
エチレンを多く放出する食品は低湿度ドロワーが適する」が、**同一Ledger内の
FACT-04**(トマト・バナナは冷蔵不適・常温保存推奨)と内容上緊張関係にある
ことを独立Fact Checkerが指摘したものだった(「バナナ・トマトを低湿度
ドロワー適合と読める記述と、冷蔵不要という記述が両立しない」)。この
パターンは`current_focus/a2/run1`(PASS)・`adjusted_focus/b1b/run1`(PASS)
の本文にも同一の文言("Apples, pears, bananas, and tomatoes release...")
が存在しており、Focus Module条件差ではなく**Ledger v4本文自体に起因**
し、Fact Checkerの実行間ばらつきでたまたま今回顕在化したものと判断する
(Trial-07 §4の柑橘類non-determinismと同型)。本Trialの権限では
Ledger改変はできないため、**USER_DECISION_REQUIRED**として報告する
(Ledger v5でFACT-03のりんご・洋梨・バナナ・トマト列挙とFACT-04の
整合を取る要否)。

`adjusted_focus/b1b/run2`のREVIEW_REQUIRED 2 claimは、記事が「商業RH
90-95%は家庭用設定に自動的には対応しない」と正しく書いた箇所へ、Fact
Checkerが「理由の詳細・具体的メーカー名を示していない」という**説明不足
指摘**(事実の誤りではなく厚みの要求)であり、Trial-07で見られたような
Ledger外の断定的一般化ではない。

### D-2目視artifact

`er011_output/discovery_stage2_interpretation_rule_trial_08/comparison.html`
(file:///C:/Users/tensh/eigo-radio/er011_output/discovery_stage2_interpretation_rule_trial_08/comparison.html)。
Household原本(2026-08-17承認)・Trial-07 baseline(参考、Ledger v3)・
current_focus/adjusted_focus各run1・2のPoint One/Two本文を、条件×level×run
で並置し、各Pointにcross_point_overlap・Fact結果を併記した。Role文字列の
ヒューリスティック分類は行っていない(D-2=(a))。多様性の最終判断は
Fable/ユーザーの目視に委ねる。

## Gate 1分類: **USER_DECISION_REQUIRED**

VALIDATED/REJECTEDいずれも推奨しない。理由:
1. 費用上限により**N=2(8本)へ縮小**しており、条件間差(current_focus
   REVIEW 0/4[fact到達3本中0] vs adjusted_focus REVIEW 2/4)を統計的に
   結論づけるにはサンプルが小さすぎる。
2. Ledger v4のFACT-03修正で追加された文言が、既存FACT-04と緊張関係を
   持つという**新しいLedger側の課題**を発見した(STOP条件「Fact Checker・
   Ledger側の変更が必要」に該当。本Trialの権限では修正しない)。
3. 安全側の指標(blocking、Ledger Deviation、Local Rewrite、Point Overlap
   flagged)は両条件・全8本で0件であり、案1(scope一般化禁止の1文追加)
   による新規安全性リスクは確認されなかった。

## STOP条件該当

該当: **Ledger側の変更が必要な新規課題を発見**(FACT-03/FACT-04の内部
緊張関係、上記参照)。非該当: 費用¥70.8(上限¥100以内、N縮小で対応)、
blocking系統的発生なし、Fact Checker・共有module側の変更は行っていない。

## 禁止事項の遵守

Production/Prompt/共有module/registry/SSOT編集なし。Ledger改変なし(v4を
読み取り専用で使用しただけ)。Fact Checker緩和なし。Git操作なし。TTS未実行。
Role文字列分類は実施していない。バックグラウンド実行はBashツールの
120秒タイムアウトによる自動退避のみで、各combo完了を都度確認しながら
逐次進行した(意図的な放置待機ではない)。完了後の自動復帰はしない。

## 成果物一覧

- `er011_discovery_stage2_interpretation_rule_trial_08.py`(root、新規)
- `er011_discovery_stage2_interpretation_rule_trial_08_comparison.py`(root、新規、D-2目視artifact生成)
- `FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08_REPORT.md`(本ファイル)
- `er011_output/discovery_stage2_interpretation_rule_trial_08/`
  - `gate4_static_check.json` / `audit_current_focus_block.txt` /
    `audit_adjusted_focus_block.txt` / `audit_current_vs_adjusted_diff.txt`
  - `run_metadata.json` / `cost_summary.json` / `raw_usage_log.jsonl`
  - `all_results_so_far.json` / `_combo_results/*.json`(8本分)
  - `{a2,b1b}/{current_focus,adjusted_focus}/run{1,2}/`(article.md、
    run_summary.json、analysis.json、fact_qa.json、point_overlap_qa.json等)
  - `comparison.html`(D-2目視artifact)
