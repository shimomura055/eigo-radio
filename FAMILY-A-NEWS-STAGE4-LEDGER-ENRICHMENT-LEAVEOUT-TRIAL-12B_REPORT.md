# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B 報告書

管理ID: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B`(Trial-12
の子Trial、Hanshin型、Sonnet委任)。上位管理ID
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14`の段階1
成果物として作成。**Trial(Production実装ではない)**。Production/Prompt/
QA/Validator/retryコード・SSOT・`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`・
Git操作は一切行っていない。出力:
`er011_output/news_ledger_enrichment_ab_trial_12/{leaveout_c,twofact_d,
reaggregation}/`。script(記事生成、既存・無変更):
`er011_news_ledger_enrichment_leaveout_trial_12b_run.py`。本報告書作成の
ために新規に集計コードを実行したが(¥0、新規API呼び出しなし)、
Production/Trialいずれのコードも変更していない。

---

## 経緯(script冒頭コメントL5-13、Opus 1回目レビューの要旨・転記)

Trial-12(条件A=現行Ledger5件 vs 条件B=拡充Ledger12件)に対するOpus L2
レビュー(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-
REVIEW-01`、報告書ファイルはroot直下には存在せず、本script冒頭にのみ
記録)の所見を検証するための追試として、本Trial-12bが設計された。
Opus優先1〜3(script L6-13、原文どおり):

> 優先1: 効果が「fact数」ではなく特定fact(FACT-12=伊原の2打数2安打、
> 次いでFACT-09/13/14)の有無に帰属できるか、抜き取り対照で確認する。
> 優先2: 周辺fact2件(FACT-12/13)だけで条件Bに近い効果が出るか確認する。
> 優先3: 唯一の交絡なし・非トートロジーな有意差だった「初回attemptの
> Point Value QA判定(PASS/NG)」を主要エンドポイントとして追跡する。

条件C(leaveout_c、抜き取り対照): 条件A全文(FACT-01〜07、無変更) +
条件Bの追加分からFACT-12とFACT-13を除いたFACT-08/09/10/11/14の5件
=usable 10件。
条件D(twofact_d、2件のみ追加): 条件A全文 + FACT-12/FACT-13の2件のみ
=usable 7件。
両条件のFACT-08〜14ブロックは、Trial-12で既に生成済みの
`hanshin_ledger_condition_b_enriched.txt`(既存、無変更・再利用のみ)
から正規表現でブロック単位に抽出し、文言を一切変更せずそのまま連結した
(機械的抜粋、新規WebSearchなし=Trial-12bでは追加research費用¥0)。

**本報告書作成時点までの経緯(重要)**: 条件C/Dの記事生成12本自体は
以前のセッションで完走済みだった(artifactは実在)が、`reaggregation/`
には`run_metadata_12b.json`のみが存在し、集計・報告書化が未実施のまま
残っていた。この状態でOpus 2回目のレビュー
(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-
INTERPRETATION-01_REPORT.md`)がartifactを直読して「fact数説はほぼ否定
される」との解釈を示し、この解釈がユーザーへ提示され、ユーザーが
Trial-14(本委任)の実施を承認した。本報告書は、その解釈の根拠となった
C/D生データを正式に集計・確定させるものである(Opusの解釈と本報告書の
再集計結果は完全に一致することを2節で確認した)。

---

## 1. 集計結果(条件A/B/C/D、各N=6、同一指標)

既存Trial-12の条件A(current)/条件B(enriched)の`all_results_so_far.json`
と、本Trial-12bの条件C(leaveout_c)/条件D(twofact_d)の
`reaggregation/all_results_cd.json`を同一ロジックで再集計した
(`reaggregation/trial14_stage1_full_summary.json`、¥0・新規API呼び出し
なし)。

| 指標 | A(fact5) | D(fact7=A+FACT-12/13) | C(fact10=A+FACT-08/09/10/11/14) | B(fact12=全部) |
|---|---|---|---|---|
| usable fact数 | 5 | 7 | 10 | 12 |
| n | 6 | 6 | 6 | 6 |
| 初回attempt Value QA flag | 6/6 | 0/6 | 0/6 | 0/6 |
| 初回attempt lexical flag | 6/6 | 4/6 | 4/6 | 4/6 |
| anchor衝突数平均 | 1.5 | 0.0 | 0.167 | 0.0 |
| retry回数平均 | 1.833 | 0.833 | 0.833 | 0.833 |
| fact利用率平均 | 0.933 | 0.524 | 0.267 | 0.278 |
| Gate指標(Point対Full Story overlap)平均 | 0.4497 | 0.348 | 0.336 | 0.370 |
| Fact Checker到達数(元パイプラインのみ) | 1/6 | 5/6 | 5/6 | 5/6 |
| うちPASS | 1 | 4 | 0 | 4 |
| うちFAIL | 0 | 1 | 4 | 1 |
| 最終NG率 | **83.3%(5/6)** | **33.3%(2/6)** | **83.3%(5/6)** | **33.3%(2/6)** |
| 最終NG内訳(lexical起因/value_qa起因/FactCheckerFAIL起因) | 4/1/0 | 1/0/1 | 1/0/4 | 1/0/1 |

上記の数値は委任文冒頭の背景表(Opus解釈の要旨)と完全に一致した
(独立再計算による確認済み)。

**FACT-ID別利用(anchor割当された記事数、n=6中)**:
- 条件A: FACT-01(4)・FACT-02(6)・FACT-03(6)・FACT-04(6)・FACT-05(6)
- 条件D: FACT-03(4)・FACT-04(6)・**FACT-12(6)**・**FACT-13(6)**
- 条件C: FACT-01(1)・FACT-02(2)・FACT-03(1)・**FACT-08(5)**・**FACT-09(6)**・FACT-11(1)
- 条件B: FACT-03(5)・FACT-04(1)・FACT-08(2)・FACT-09(3)・**FACT-12(6)**・FACT-13(2)・FACT-14(1)

条件D・Bでは新規fact中FACT-12が全run(6/6)で必ず参照されている一方、
条件Cでは既存FACT-01〜05への依存が大きく減り、新規fact中FACT-09
(救援投手陣の人名を含むfact)が中心的に参照されている点が対照的。

---

## 2. 判定(最終NG率という二値指標では「fact数が多いほど良い」は棄却)

fact 5→7件で最終NG率83.3%→33.3%(改善)、7→10件で33.3%→83.3%(悪化)、
10→12件で83.3%→33.3%(改善)——**最終NG率はusable fact数に対して単調
ではない**。fact数そのものではなく、FACT-12/13(伊原の2打数2安打・
モンテロの2桁本塁打)の有無が最終NG率の低さと一致し、FACT-09/10
(救援投手陣の人名・回別失点内訳)の有無が最終NG率の高さ(条件C)と
一致する。これはOpus解釈(委任文冒頭)と一致する。

一方、初回attemptのPoint Value QA flag(6/6 vs 0/18)・anchor衝突数
(1.5→0〜0.167)・retry回数(1.833→0.833)は、条件C/D/Bのいずれでも
条件Aから明確に改善しており、こちらは「fact供給量を増やすとPoint
Role Planningの構造的逼迫が緩和される」という、より限定的だが一貫した
効果として支持される(Fact Checker以降の合否とは別経路)。

---

## 3. Dangling Reference Check

- 参照した全ファイルの実在確認: `er011_output/news_ledger_enrichment_ab_
  trial_12/{leaveout_c,twofact_d}/{a2,b1b}/run{1,2,3}/`配下の
  `analysis.json`・`fact_qa.json`・`point_overlap_article_retry_log.json`、
  `_combo_results/*.json`、`reaggregation/{run_metadata_12b.json,
  all_results_cd.json,trial14_stage1_full_summary.json}`はいずれも本
  作業で実在・整合性を確認済み。
- `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`・
  `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-
  INTERPRETATION-01_REPORT.md`は実在確認済み。
- SSOT・`docs/pm/`は本作業で編集していない。Git操作は行っていない。

---

## 4. Close判定

**`VALIDATED`(Trial仮説の判定として、以下の限定範囲でのみ)**:
「fact供給量(usable fact数)が多いほど最終NG率が下がる」という単純な
単調仮説は、本Trial-12bのC/D実測により**明確に反証された**(fact10件
[条件C]がfact5件[条件A]と同じ最終NG率83.3%)。これは委任文冒頭・
Opus解釈と一致する確定結果である。

一方、「非headline角度の周辺fact(FACT-12/13、またはFACT-11/14=段階3
条件E参照)がPointごとに供給されることが、Point生成段階の構造的逼迫
(Value QA flag・anchor衝突・retry回数)を緩和する」という、より限定的な
副仮説は、本Trial-12bのN=6×2条件でも一貫して支持された。ただし
**Fact Checker以降の合否(最終NG率)への効果は、fact供給量ではなく
個別factの種類(固有名詞の多寡)に強く依存する**ことが判明したため、
「fact供給量仮説」を主軸に据えることは`REJECTED`とする。

Production仕様としての採用可否は判断していない(候補に留める、
ユーザー判断が必要な場合は上位報告書
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_
REPORT.md`で扱う)。
