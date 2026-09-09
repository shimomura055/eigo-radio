# FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07 — Report

管理ID: FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07(Lane A、D2)
実施日: 2026-09-09。実施者: Sonnet(sonnet-worker、Fable委任)。
**Trial(Production実装ではない)**。Production/Prompt/SSOT編集・Git操作は
一切行っていない。

## 0. 前提・ユーザー決定(委任文どおり)

- D2=(b): Household Ledger再利用でN=3のArticle-only Trialを実施し、その
  結果でProduction配線判断(ユーザー)。D1=(a)2軸判定採用・Discovery=Pool型
  正式化(SSOT反映は別タスク)。D3=保留(Point Role hint接続はしない)。
- Discovery/Why Layer3 Focus Module本体(段落)は
  `er011_open112_a_family_4layer_prompt_trial_05.DISCOVERY_FOCUS_MODULE_BLOCK`
  (VALIDATED、Article-only N=1)から一字一句変更せずそのまま再利用。見出し
  行のみ、Trend Synthesis Focus Moduleの前例(Trial-09暫定見出し→
  WIRING-01正式見出し)と同型の書式へ改稿(VALIDATED/Production採用は
  偽って主張していない、`er011_discovery_layer3_focus_trial_07.py`内で
  機械assertによりbyte一致を確認済み)。
- Household Ledger(`er003_output/n3_01/household/research/verified_fact_ledger.txt`)・
  Topic(`prod_gen.THEMES`の`household`エントリ)を独立に書き写さず、そのまま
  参照。
- G1修正済みProduction(`er003_v1_n3_01_articles_generate.py`、
  `editorial_type_module_block`パラメータ方式)をimportのみで使用。

## 1. Gate 4(Production無変更、静的diff) — PASS

`er011_output/discovery_layer3_focus_trial_07/gate4_static_check.json`:
Production関数の再定義・monkeypatchなし、`COMMON_BLOCK_TEMPLATE`の
`{editorial_type_module_block}` placeholder存在確認、baseline条件
(block="")が旧来テンプレートとbyte完全一致、baseline↔focus差分が
単一のinsert(diff_op_count=1)であることを機械確認した。

## 2. 実行概要

N=3(当初計画どおり、費用超過による縮小なし)。2条件(baseline/
discovery_focus)×2レベル(A2/B1B)×3run=**12本**、全て完走(text-only、
TTS未実施)。手動Mode判定=`DISCOVERY_WHY`(2軸判定、
`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md`§2.1の既決A-UDR-9を
再確認・転記、新規判定なし)。詳細:
`er011_output/discovery_layer3_focus_trial_07/run_metadata.json`。

費用実測: **¥137.6**(上限¥150以内、縮小不要)。内訳:
baseline ¥61.5 / discovery_focus ¥76.1。詳細:
`er011_output/discovery_layer3_focus_trial_07/cost_summary.json`。

## 3. 結果表(12本、要約)

| 条件 | Lv | run | status | fact_verdict | unsupported件数 | ledger | retry | word_count | avg/max文長 |
|---|---|---|---|---|---|---|---|---|---|
| baseline | A2 | 1 | OK | PASS | 0 | COMPLIANT | 1 | 285 | 11.0/17 |
| baseline | A2 | 2 | OK | PASS | 0 | COMPLIANT | 1 | 297 | 11.6/23 |
| baseline | A2 | 3 | **NG** | **FAIL** | 0 | - | 1 | 329 | 11.9/27 |
| baseline | B1B | 1 | OK | REVIEW_REQUIRED | 2 | COMPLIANT | 0 | 311 | 11.4/35 |
| baseline | B1B | 2 | OK | PASS | 0 | COMPLIANT | 1 | 339 | 11.9/25 |
| baseline | B1B | 3 | OK | PASS | 0 | COMPLIANT | 0 | 321 | 13.2/37 |
| discovery_focus | A2 | 1 | **NG** | **FAIL** | 1 | - | 2 | 291 | 13.2/50 |
| discovery_focus | A2 | 2 | OK | REVIEW_REQUIRED | 1 | COMPLIANT | 0 | 256 | 12.3/37 |
| discovery_focus | A2 | 3 | OK | PASS | 0 | COMPLIANT | 1 | 294 | 14.1/50 |
| discovery_focus | B1B | 1 | OK | REVIEW_REQUIRED | 2 | COMPLIANT | 2 | 319 | 14.2/52 |
| discovery_focus | B1B | 2 | OK | REVIEW_REQUIRED | 3 | COMPLIANT | 0 | 299 | 12.6/28 |
| discovery_focus | B1B | 3 | OK | REVIEW_REQUIRED | 3 | COMPLIANT | 0 | 308 | 10.8/21 |

全12本の生詳細: `er011_output/discovery_layer3_focus_trial_07/all_results_so_far.json`
(各run配下に`article.md`/`analysis.json`/`fact_qa.json`/`ledger_deviation.json`等)。

## 4. Blocking(最重要指標)

**blocking(FAIL) 2/12(baseline 1/6・discovery_focus 1/6、同率)**。

両件とも原因は同一: Household Ledger FACT-03「イチゴ・柑橘類(オレンジ等)
のような果物は高湿度を好む」という**既存承認済みLedger記載自体**を記事が
そのまま書いたところ、独立Fact CheckerがWeb検索で「GE Appliances公式は
オレンジを低湿度側に分類している」等、別の公式情報源との不一致を検出し
FAILと判定したもの(`fact_qa.json`の`contradictions`参照)。baseline側の
FAILでも同一の柑橘類記述が原因であり、**Focus Module条件で新たに発生した
blockingではない**(発生率も両条件で1/6ずつと対称)。

この論点は、現行Production承認済み記事(2026-08-17、B1B)にも同一文言
「Strawberries and citrus fruits, including oranges, prefer high
humidity」がそのまま存在しており、当時のFact Checkerはこれを問題視して
いない。したがって本Trialで観測されたFAILは、**Fact Checker判定の
実行間ばらつき(non-determinism)により今回たまたま顕在化した、Household
Ledger FACT-03の既存の事実精度リスク**であり、Discovery/Why Layer3 Focus
Module自体の欠陥ではないと判断する。ただし、このLedger記載自体の是非は
本Trialのスコープ外であり、**別途USER_DECISION_REQUIRED**として報告する
(Household Ledger v4改訂の要否)。

## 5. Fact Checker(REVIEW_REQUIRED)詳細とclaim→evidence対応表

REVIEW_REQUIRED率: baseline 1/6(17%、平均unsupported claims 0.33件/本)、
discovery_focus 4/6(67%、平均unsupported claims 1.67件/本、FAIL 1本の
1件を含めると10件/6本)。Focus Module条件でFact Checker指摘が増える
傾向はTrial-05(N=1、A2 0→3、B1 3→5)と整合する。

**人間確認用対応表(discovery_focus条件、claim→evidence id→判定、機械
分類・簡易ヒューリスティック)**: 全10件のunsupported_specific_claims
(FAIL 1本の1件を含む)のうち、8件はキーワード一致でLedger evidence id
(FACT-01×1、FACT-02×1、FACT-03×6)へ機械的に紐付いた。残り2件は
キーワード一致が0件(`LEDGER_OUTSIDE_OR_NO_LEXICAL_MATCH`)と機械判定
されたが、人間が読むと(1)「エチレンに晒された果物・野菜が早く傷む」は
Ledger FACT-02の一般化議論であり(機械分類漏れは、Fact Checkerの指摘文が
「エチレン」を含むためだったが、本Trialのキーワード一致は英語表記
"ethylene"のみを見ておりカタカナ表記を拾えていなかった、既知の
ヒューリスティック限界)、(2)「見慣れない食品はエチレン感受性か水分保持性
かで判断する」という一般化テストはFACT-01+FACT-03の仕組みから導いた
記事側の敷衍であり、新しいFactの創作ではない。**したがって人間読解では
discovery_focus条件の10件全てがLedgerのいずれかのFactの解釈・敷衍として
説明可能であり、Ledger外の事実創作は確認されなかった**(Opus提案の成功
基準「人間が解釈のLedger内包を確認できること」を満たす)。

対応表の全文・生データ:
`er011_output/discovery_layer3_focus_trial_07/{a2,b1b}/discovery_focus/run{1,2,3}/analysis.json`
の`claim_to_evidence_table`キー。

## 6. LDC(Ledger Deviation Checker)+Local Rewrite

12本全てで`ledger_deviation_count=0`(MAJORなし、blocking 2本は判定前に
FAILで打ち切り)。Local Rewrite発火は**0回**(全12本)。Fact Checkerの
指摘とLedger Deviationは完全に分離しており(Fact Checker=独立Web検索との
整合性、LDC=記事とLedger自体の整合性)、混同していない。

## 7. Point Role分類(機械分類、簡易ヒューリスティック)と役割再現率

Point Role Planning出力の`role`文言を、mechanism/myth-correction(myth_correction)/
certainty-limitation(certainty_limitation)/broader-dimension(broader_dimension)/
otherへキーワード一致分類(12本×2Point=24枠)。

| 条件 | mechanism | myth_correction | certainty_limitation | broader_dimension | other |
|---|---|---|---|---|---|
| baseline(12枠) | 4 | 3 | 0 | 4 | 1 |
| discovery_focus(12枠) | 6 | 6 | 0 | 0 | 0 |

Focus Module条件では**mechanism/myth_correctionのみに100%収束**し、
baselineで見られたbroader_dimension/otherが消滅した。これはFocus Module
本文が「現象のなぜ」「一括分類の例外・訂正」という2方向をPoint One/Twoの
差別化軸として明示的に指示していることと整合する狙いどおりの効果と読める
一方、baseline側が持っていた「日常生活での意味づけ」的なPointの多様性が
失われた可能性も示唆する(role再現率という点では、Focus Module指示した
2方向は12/12=100%再現、ただしcertainty-limitation方向のPoint単独化は
今回0件で再現されなかった。これは仕様上、certainty-limitationはPoint
単位ではなく本文全体のhedging原則として書かれているためと考えられる)。

## 8. 副作用

- **語数超過**: discovery_focus条件のみ2/6本でPoint Oneがtolerance上限
  (70語)をわずかに超過(A2 run3=76語、B1B run2=71語)。baseline条件は
  0/6本。Trial-05で観測された「Point Two 81語超過」と同種・同方向の副作用
  だが、今回は上限超過幅が小さい(+1〜6語)。
- **近似重複文(簡易ヒューリスティック)**: SequenceMatcher比率0.55以上の
  文ペア検出は、baseline平均1.67件/本・discovery_focus平均1.67件/本と
  **両条件でほぼ同率**だった。実際に検出されたペアを読むと、多くは
  "A low-humidity drawer has more ventilation. / A high-humidity drawer
  is more sealed."のような**対比構造(意図した対句)**であり、Trial-05が
  指摘した「同義文の意味的重複」とは異なる。**本ヒューリスティックは
  誤検出(対比文を重複と誤認)が多く、今回のN=3では深刻な同義文重複の
  実例は確認できなかった**(人間の目視確認: 各discovery_focus記事本文を
  通読し、Trial-05のような明確な意味的重複は検出せず)。
- **文長**: discovery_focus条件でavg_sentence_length(平均約12.9語)・
  max_sentence_length(最大50〜52語)がbaseline(平均約11.8語、最大35〜37語)
  よりやや長い。簡易な自然さ指標として、機構説明・例外訂正を1文に
  詰め込む傾向がわずかに増えている可能性がある(hard capではないため
  blockingではない)。

## 9. Household現行記事(2026-08-17)との焦点構造の差(定性)

現行B1B記事のPoint One「The slider is really a small air door」・Point
Two「Some produce should skip the refrigerator」は、仕組み説明1つ+
保存場所の例外1つという構成。discovery_focus条件の生成記事(例:
`b1b/discovery_focus/run3/article.md`)はPoint One/Twoの両方が仕組み・
例外訂正(mechanism/myth_correction)に寄る傾向が強く、現行記事が持っていた
「トマト・バナナは冷蔵に向かない」という**保存場所という別次元の話題**が
Point構成から後退し、Main Story/例外注記側に吸収される記事が複数見られた
(例: A2 run2はPoint Twoで保存場所ではなく分類の誤解訂正を扱った)。

## 10. Gate 1分類(推奨、最終判断はユーザー)

**VALIDATED(Focus Module自体について)**を推奨する。根拠: (1)blocking
2/12はいずれもFocus Module起因ではなく、baseline側にも同率で発生する
既存Household Ledger FACT-03の事実精度リスクに起因する(§4)。(2)
discovery_focus条件のREVIEW_REQUIRED増加(10件)は全て人間読解で
Ledgerのいずれかの解釈・敷衍として説明可能(§5)。(3)副作用(語数超過・
文長増)は軽微でhard capを大きく超えない(§8)。

ただし以下2点は**本Trialのスコープ外の別件としてUSER_DECISION_REQUIRED**:
(a) Household Ledger FACT-03の柑橘類(オレンジ)高湿度記載の事実精度
(Fact Checkerが複数回、独立に矛盾を指摘している。Ledger改訂または
記事側での断定回避の要否)。(b) 見出し改稿版文言・`editorial_mode`名
`discovery_why`の正式登録、role分類のcertainty-limitation方向の扱い。

## 11. Production配線判断に必要な項目

- mode名: `discovery_why`(Production `EDITORIAL_TYPE_MODULE_BLOCKS`へ
  未登録、本Trialで登録していない)。
- 見出し改稿版文言: 本ファイル冒頭・
  `er011_discovery_layer3_focus_trial_07.py`の`REVISED_HEADER_LINE`
  (本文段落はTrial-05とbyte一致、見出しのみ改稿)。
- `EDITORIAL_TYPE_MODULE_BLOCKS`追加: Trend Synthesis配線
  (WIRING-01)と同一パターンで`{"discovery_why": DISCOVERY_FOCUS_MODULE_BLOCK}`
  を追加するだけ(Gate 4確認済み、baseline既定挙動は無変更)。
- Discovery Gate記録欄: 本Trialの`run_metadata.json`
  (`two_axis_determination`)をひな形として、Trend Gate 6項目・Major/Daily
  Gate 6項目と同型の「2軸判定結果+タイブレーク適用有無」記録欄を追加する
  案(2軸判定自体はD1で未承認)。
- 回帰テスト案: (1)baseline条件(block="")がbyte不変であることの単体
  テスト(Gate 4相当を恒久テスト化)、(2)Household以外のDiscovery候補
  (POOL_TOPIC_MASTER該当記事)でのN=1確認。
- コスト影響: Prompt長増のみ(baseline↔focus共通ブロックdiff
  約2200byte、`gate4_baseline_vs_focus_diff.txt`)。実測費用は
  baseline ¥61.5→discovery_focus ¥76.1(N=6ずつ、+約24%、主にfocus
  条件での複数回retryに起因)。Human Review負荷の実測: REVIEW_REQUIRED率
  17%→67%(+50pt)、平均unsupported claims 0.33→1.67件/本(約5倍)。

## 12. STOP条件該当

いずれも非該当: 費用¥137.6(上限¥150以内)、blockingは系統的ではない
(両条件で同率・同一原因)、新規failure modeなし(Fact Checker既存機構内の
判定)、Production/共有ファイル変更は行っていない。

## 13. 成果物一覧

- `er011_discovery_layer3_focus_trial_07.py`(root、新規)
- `FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07_REPORT.md`(本ファイル)
- `er011_output/discovery_layer3_focus_trial_07/`
  - `gate4_static_check.json` / `gate4_baseline_vs_focus_diff.txt`
  - `run_metadata.json`
  - `cost_summary.json` / `raw_usage_log.jsonl`
  - `all_results_so_far.json`
  - `_combo_results/*.json`(12本分)
  - `{a2,b1b}/{baseline,discovery_focus}/run{1,2,3}/`(article.md、
    run_summary.json、analysis.json、fact_qa.json、ledger_deviation.json、
    metrics.json、length_report.json、audit/等)
