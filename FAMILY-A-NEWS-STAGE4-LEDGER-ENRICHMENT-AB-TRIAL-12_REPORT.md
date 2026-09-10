# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12 報告書

管理ID: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`(News Ledger
拡充A/B Trial、Hanshin型、Sonnet委任)。**Trial(Production実装ではない)**。
Production/Prompt/QA/Validator/retryコード・SSOT(`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`CURRENT_SPEC.md`・`ARTIFACT_REGISTRY.md`)・
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`・Git操作は一切行っていない。
出力: `er011_output/news_ledger_enrichment_ab_trial_12/`。script:
`er011_news_ledger_enrichment_ab_trial_12_run.py`(root)。

---

## エグゼクティブサマリー(用語: Ledger=記事が使ってよい検証済み事実の一覧)

Hanshin型(単一試合結果・box-score型)記事で、Ledgerのfact供給量を
5件→12件(条件A→条件B)へ増やすA/B Trialを実施した。**予算¥200の大半
(¥148.6)が新規fact調査(Web検索)1回に消費され、計画N=6/条件(合計12本)
のうち各条件1本ずつ(合計4本)を実行した時点で予算上限に接近したため
STOPした**。この極小N(N=1/条件/レベル)でも、4本全てが一貫して同一方向
を示した: 条件A(fact5件)は2本とも最終NG(Loop Budget上限まで再試行)、
条件B(fact12件)は2本ともOK(retry1回で解消)。Point One/Two間のfact
重複(anchor衝突)は条件Aで1〜2件、条件Bで0件だった。統計的に確定的な
結論を出せる標本数ではないが、方向性は論点H(fact供給量仮説)を支持する
極めて一貫した結果であり、追加予算での本実施(N=6到達)を推奨する。
¥0並行分析(a)〜(d)は別途完了(6節)。

---

## 1. Reconciliation Check(PM_GOVERNANCE 2-1)の実施結果

- 既存SSOT確認: `FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01_REPORT.md`・
  `FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`を読了。
  両報告は本Trial設計(候補A「Ledger拡充Trial A/B、Hanshin型、N=6」)を
  次Trial候補として明記しており、`APPROVED_FOR_PRODUCTION`/
  `PRODUCTION_WIRED`済みの重複対策・競合機構は存在しない
  (Overlap閾値0.40・Loop Budget=2・Point Role Planningはいずれも
  無変更のまま使用、cross_point_overlapのretry統合[OPEN-133]も
  無変更=DEFERREDのまま)。
- **UDR状態との関係**: 両報告時点では「主軸を論点Hへ移すか」(UDR候補a)は
  `Deferred`(ユーザー未承認)だった。本委任の冒頭で示された「ユーザー
  確定事項(2026-09-10)」は、UDR候補a全体の承認ではなく、**この1件の
  Trial実施(候補A設計)のみ**を承認するもの(委任文に明記)。本報告は
  この限定承認の範囲内で実施した。UDR候補a自体(主軸移行の可否)は
  引き続き別途ユーザー判断が必要。
- 重複・競合: なし(既存14仕組み・4Trial系譜のいずれとも出力先・
  対象ファイルが重ならない独立実行)。

---

## 2. 設計

- **変数**: Verified Fact Ledger(阪神対広島、2026-08-16)のfact供給量
  のみ。条件A=現行Ledger(既存ファイル`er003_output/n3_01/hanshin/
  research/verified_fact_ledger.txt`、無変更)、条件B=条件Aの全文+
  新規fact追記(新規ファイル`er011_output/news_ledger_enrichment_ab_
  trial_12/hanshin_ledger_condition_b_enriched.txt`)。
- **固定**: `editorial_type_module_block=""`・`point_role_hint_block=""`
  (Production既定のbaseline、Focus Module/hintなし、Trial-06の
  focus_hint条件とは無関係)。Overlap閾値0.40・Loop Budget=2(`POINT_
  OVERLAP_ARTICLE_RETRY_MAX`)は無変更。
- **N定義**: 「N=6」は条件ごとのrun数(A2×3+B1B×3)、条件A/B合計で
  計画12 run。**実績はN=1/条件/レベル(A2×1+B1B×1=条件ごと2本、合計
  4本)**、予算上限接近によるSTOPのため未達(4節参照)。
- **再利用(import・無変更)**: `er011_point_role_planning_focus_
  connection_trial_03`(`run_one_pattern_connected`・`HANSHIN_LEDGER_
  PATH`・`HANSHIN_TOPIC_JA`)、`er011_daily_news_focus_layer_
  comparison_trial_04`(`analyze_run`・`LEVELS`・`load_role_planning_
  used`)、`er003_v1_n3_01_articles_generate`(`build_common_block`・
  `build_prompt`)、`er005_cost_logger`。

---

## 3. 拡充Ledger(条件B、新規fact一覧)

新規fact取得は`er002_ja_web_research_r3.py`(既存、無改変)と同一メカニズム
(OpenAI Responses API、`tools=[{"type": "web_search"}]`、model=
`gpt-5.6-sol`、reasoning effort=high)を新規スクリプトから直接呼び出し
(実際に12回のWeb検索を実行)。既存FACT-01〜07は無変更、以下7件
(FACT-08〜14、いずれもSUPPORTING、confidence記載は「中」— 理由は下記
限界を参照)を追記した。全文は`hanshin_ledger_condition_b_enriched.txt`
参照。

| Fact ID | 内容(要約) | 主な出典 |
|---|---|---|
| FACT-08 | チーム安打阪神13・広島3、広島の失策は9回表(小園) | NPB公式投打成績 |
| FACT-09 | 伊原降板後、木下・ドリス・岩崎・及川が4回1安打無失点で継投 | NPB公式投打成績 |
| FACT-10 | 広島救援陣(辻・菊地・塹江・黒原)の各回・失点内訳 | NPB公式投打成績・日刊スポーツ |
| FACT-11 | 佐藤輝の28号は森の3球目ツーシームをバックスクリーンへ | デイリースポーツ・日刊スポーツ |
| FACT-12 | 伊原が打者として2打数2安打(プロ初の複数安打) | NPB公式・日刊スポーツ |
| FACT-13 | モンテロ10号は来日2年目で自身初のシーズン2桁本塁打 | デイリースポーツ |
| FACT-14 | 阪神は連敗を2で止め首位・+2.0ゲーム差を維持、広島は3連勝を逃す | NPB公式試合結果 |

条件B usable(ANCHOR+SUPPORTING)fact数 = 5(既存)+7(新規)= **12件**
(条件A=5件、Theme2実績8件・CAR-T実績14件の中間に位置)。

**確認方法の限界(重要、正直に報告)**: 新規factはWeb検索ツールに
よる自動調査1回の結果であり、既存FACT-01〜07で行われたような「人間が
Source間の矛盾を発見・解消する」プロセスは経ていない。`response.output`
内の`url_citation`annotationとして機械的に確認できたsourceは4件のみ、
残り15件のURLはモデルの本文中の自由記述(text mention)であり、Trial
実施者(Sonnet)による個別URL再訪問確認は行っていない。このためLedger
ファイル側にも全entryの`confidence`を「中」と明記し、Production採用
可否は別途人間によるURL再確認が必要である旨を記載した(USER_DECISION_
REQUIRED候補、8節参照)。

---

## 4. 結果(条件A vs 条件B、N=1/条件/レベル、合計4本)

| 指標 | 条件A(fact5件) | 条件B(fact12件) |
|---|---|---|
| n | 2(A2×1、B1B×1) | 2(A2×1、B1B×1) |
| 初期attempt flag率 | 100%(2/2) | 100%(2/2) |
| 最終NG率 | **100%(2/2)** | **0%(0/2)** |
| retry回数平均 | 2.0(Loop Budget上限まで消化) | 1.0 |
| Point対Full Story overlap平均(最大値、Gate指標) | **0.4525** | **0.299** |
| Point One overlap平均 | 0.4525 | 0.273 |
| Point Two overlap平均 | 0.333 | 0.294 |
| anchor衝突数平均(P1∩P2共有fact数) | **1.5** | **0.0** |
| fact利用率(参照fact数/usable fact数) | 0.9(4.5/5) | 0.25(3/12) |
| Ledger Deviation件数平均 | (未計測、NG_REVIEW_REQUIREDで到達前に終了) | 0.0(2本ともLEDGER_COMPLIANT) |
| Fact Checker verdict | (未計測、同上) | PASS×2 |

個別run値(全4本、丸めなし):

| run | 条件 | レベル | status | retry | P1 overlap | P2 overlap | anchor衝突 | 参照fact |
|---|---|---|---|---|---|---|---|---|
| 1 | A | A2 | NG_REVIEW_REQUIRED | 2 | 0.429 | 0.273 | FACT-01,02(2件) | FACT-01,02,03,04,05 |
| 1 | A | B1B | NG_REVIEW_REQUIRED | 2 | 0.476 | 0.393 | FACT-04(1件) | FACT-02,03,04,05 |
| 1 | B | A2 | OK | 1 | 0.250 | 0.240 | なし | FACT-12,13 |
| 1 | B | B1B | OK | 1 | 0.296 | 0.348 | なし | FACT-03,04,12,13 |

**注目点**: 条件Bでは、Point Role Planningが新規追加fact(FACT-12・
FACT-13)を実際に選択し、Point One/Twoで異なるfactへ自然に分散した
(anchor衝突0件)。条件Aでは、既存5 factのうち中心的な2件
(FACT-01最終スコア、FACT-02先制HR)がPoint One/Two双方で重複参照
された。これは既存監査(anchor衝突→語彙重複、r=0.46)が示した機序を、
相関ではなく条件操作(Ledger拡充)によって直接再現した結果である。

**解釈上の注意(N=2の限界)**: Fisherの正確検定(参考値、有意性主張
ではない)では最終NG率2/2 vs 0/2はp≈0.33で統計的有意ではない。4本
全てが同一方向を示したことは方向性としては強いシグナルだが、標本数が
極小(既存Trial-08のN=6より更に少ない)であり、断定的な結論を出せる
段階にはない。

---

## 5. 連続量評価(overlap_ratio、NG群/OK群比較)

条件A(NG群、n=2)の`Gate指標(Point対Full Story overlap最大値)`平均
0.4525、条件B(OK群、n=2)平均0.299、**差0.154**。既存Trial-08(N=6、
`FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`)のNG群/
OK群差0.084より大きい差が観測されたが、これはN=2ずつという極小標本
かつ条件（Ledger差）そのものが直接NG/OKを分けているため単純比較は
できない(Trial-08は同一Ledgerでの診断分岐条件比較、本Trialは
Ledgerそのものを条件化しているため、比較対象の性質が異なる)。
UDR候補d(連続量評価への切替)を支持する追加の傍証として位置づける
(断定的な検出力の主張ではない)。

---

## 6. ¥0並行分析(a)〜(d)

### (a) threshold 0.40の妥当性

**現時点評価: 判断材料不足(既存STATUS-REPORT-01・Trial-08 Part Bの
結論を維持、本Trialは追加の反証も追加の強い支持も提供しない)**。
根拠: 本Trialの4観測のうち、条件A・A2のPoint One overlap=0.429は
既存監査で特定された境界帯(±1語、[0.363, 0.437])に該当する
(Trial-08 Part Bの「25%が境界帯」という既存知見と整合する1件の
追加サンプル)。条件A・B1Bのoverlap=0.476は境界帯より明確に上、
条件Bの4値(0.25/0.24/0.296/0.348)はいずれも境界帯より下または
境界帯直下だった。この4件だけでは0.35/0.45再校正時の判定変化を
論じるには少なすぎる(既存240件データでの感度分析結果を維持する
のが適切)。

### (b) Overlap Checker(lexical overlap coefficient)

**現時点評価: 要見直しの兆候は維持だが、本Trialにより「fact供給側の
原因」という新たな解釈が追加された**。条件Aで重複anchorとなった
FACT-01(最終スコア「8-1」)・FACT-02(佐藤輝明の2ランHR)・FACT-04
(モンテロのソロHR)はいずれも数値・固有名詞を含む中心factであり、
5 factしかない状況ではPoint One/Twoが同じ中心factを再利用せざるを
得ない(fact利用率90%は「選択の余地がほとんどない」ことを直接示す)。
これはOverlap Checker自体が厳しすぎるのではなく、**Ledgerが薄い
ときにChecker以前の生成過程(Point Role Planning)が構造的に重複を
生みやすい**という、既存の「entity/数値混在で目視分離できない」
知見(REDESIGN-INVENTORY §3-1)を補強する具体例と位置づける。

### (c) retry(Loop Budget・retry責務競合)

**現時点評価: Loop Budget=2自体の妥当性は本Trialでは検証していない
(判断材料不足、既存評価を維持)。ただし「fact供給を増やすとretryへの
依存度自体が下がる」という追加の傍証を得た**。条件Aは2本ともLoop
Budget上限(2回)まで再試行しても解消せず、条件Bは2本とも1回の
再試行で解消した。これはretry機構自体の改修ではなく、**retryが
必要になる頻度を根本原因(fact供給)側で減らせる可能性**を示す
初期証拠であり、既存の「Role Planningは診断結果を見ない盲目の
再抽選」という構造的懸念(6節(d))とも整合する(fact不足下では
何度再抽選しても同じ5 factから選ぶしかないため、盲目性の影響が
増幅されやすい)。

### (d) 連続量評価の検出力

**現時点評価: UDR候補dの追加支持材料あり(5節参照)、統計的な最終
結論には至らない**。二値NG率(2/2 vs 0/2)と連続量(0.4525 vs
0.299)は本Trialでは同じ方向を示したが、N=2ずつのため二値・連続量
いずれの検出力優位性も本Trial単独では実証できない。既存Trial-08の
結論(連続量の方が閾値近傍での識別力が高い)を維持する。

---

## 7. 費用(段階別実測)

| 段階 | 内容 | 実測費用 |
|---|---|---|
| 1. Ledger拡充調査 | web_search tool 12回(gpt-5.6-sol、reasoning=high、input 110,837 token・output 8,494 token[うちreasoning 6,000]) | **¥148.6**(1回限りの費用、条件Bファイルは今後の追加Trialで再利用可能) |
| 2. 記事生成(条件A、NG_REVIEW_REQUIRED終了×2本) | Writer×3+Evidence Compression×3+Overlap/Value QA×3+Role Planning×3(Fact Checker未到達) | ¥4.8 + ¥4.8 = ¥9.6 |
| 3. 記事生成(条件B、OK終了×2本) | 同上+Fact Checker+Ledger Deviation+Directional Precheck | ¥14.9 + ¥11.5 = ¥26.4 |
| **合計** | | **¥184.6** |

**予算上限¥200に対する評価**: 見込み¥60〜150に対し実測¥184.6と
上振れした。主因は段階1(Ledger拡充調査)が単独で¥148.6(予算の
74%)を消費したこと(12回のWeb検索で約11万tokenの検索結果本文が
入力tokenとして計上されたため)。段階2・3(記事生成、実施4本)は
¥36.0で、これはTrial-06実績(N=3×2条件×2レベル=12本で¥85.6、
1本あたり約¥7.1)とおおむね整合する単価だった。**段階1のコスト見積り
(¥60〜150という当初見込みに軽量Web調査として算入されていなかった
可能性)がこのTrialの費用超過の主因であり、記事生成パイプライン自体の
単価は既存実績と乖離していない。**

---

## 8. STOP(予算上限接近)

計画N=6/条件(合計12本)のうち4本(条件A/B各2本、A2×1+B1B×1)を実施
した時点で残予算¥15.4となり、次の1本(特に条件Bで再びOK終了し
Fact Checker以降まで到達する場合、実測¥11.5〜14.9/本)を実行すると
¥200を超過する見込みが高いため、ここでSTOPした(委任文の「超過の
兆候でSTOP」に従う)。二重起動はしていない(全て前面同期・逐次実行、
バックグラウンド待機なし)。

---

## 9. 判明したこと/棄却されたこと/残った有力候補

**判明したこと(N=2の限界付き)**: (1) Ledger fact供給量を5→12へ
増やすと、本Trialの4本全てで同一方向(NG率100%→0%、anchor衝突
1.5→0.0、retry 2.0→1.0、overlap 0.4525→0.299)の改善が観測された。
(2) anchor衝突の直接原因は、fact不足下でPoint One/Twoが同じ中心
factを再利用せざるを得ないこと(fact利用率90%)であり、これは
既存の相関ベース監査(r=0.46)を条件操作で直接支持する結果。
(3) Ledger拡充調査自体のコスト(¥148.6/回)は記事生成本体より
高く付く可能性があり、Production化する場合はこのコストも評価対象に
含める必要がある(PM_GOVERNANCE 2-2該当)。

**棄却されたこと**: なし(本Trialは新たな棄却材料を提供していない、
既存の「候補4棄却寄り」「候補1/2/3条件付き保留」等の評価は維持)。

**残った有力候補**: 論点H(Ledger fact供給量仮説)の優先度が本Trialに
より明確に上昇した。ただしN=2×2条件という極小標本のため、
「効果が確認された」と断定はできず、追加予算でのN積み増し
(最低でも計画どおりN=6/条件到達)が望ましい。

---

## 10. 次Trial候補(Fable側で実施可、小規模)

- **候補X(本Trialの継続、追加予算¥50〜80見込み)**: 条件B Ledger
  ファイルは既に作成済み・再利用可能なため、追加のLedger調査費用
  (¥148.6)は発生しない。残りA2×2+B1B×2(条件Aのみ)・A2×2+B1B×2
  (条件Bのみ、計8本)を追加実行すればN=6/条件へ到達できる。1本あたり
  単価(条件A NG終了¥4.8、条件B OK終了¥11.5〜14.9)から見込み
  ¥60〜100程度。**Fable側で実施可**(既存条件・スクリプトの再実行の
  みで新規仕様判断を伴わない)。
- **候補Y(条件B Ledgerの人間検証)**: 3節の限界(url_citation
  annotation確認済みは4件のみ)を踏まえ、新規7 factのURLを人間が
  再訪問し内容一致を確認する(¥0、人手作業)。Production Ledgerとして
  正式採用する場合は必須(8節参照)。

---

## 11. ユーザー判断が必要な項目

1. **候補X(N積み増し)への追加予算¥50〜100の承認可否**: 承認すれば
   計画どおりN=6/条件へ到達可能。非承認の場合、本Trialの結論はN=2の
   極小標本止まりとする。
2. **拡充Ledger(条件B、FACT-08〜14)をProduction Ledgerへ反映するか**:
   反映する場合は9節候補Yの人間検証(URL再訪問)が前提となる
   (Fact Safety最上位原則、本Trialでは実施していない)。反映しない
   場合、条件Bファイルは本Trial専用のまま維持する。
3. **UDR候補a(News方針の主軸を論点Hへ移すか)**: 本Trialは部分的な
   追加支持材料を提供したが、極小標本のため単独で主軸移行を正当化
   する材料ではない。既存`FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01_
   REPORT.md` 8節の他のDeferred項目とあわせて判断されたい。

小さな次Trial(10節候補X・候補Y)自体はユーザー判断化せず、上記1の
予算承認が得られればFable側で実施可能。

---

## 12. Dangling Reference Check

- 本報告で参照した全ファイルの実在確認: `er003_output/n3_01/hanshin/
  research/verified_fact_ledger.txt`(既存、無変更)・
  `er011_output/news_ledger_enrichment_ab_trial_12/`配下の全ファイル
  (`hanshin_ledger_condition_b_enriched.txt`・`research_raw_result.
  json`・`cost_summary.json`・`final_analysis_summary.json`・
  `all_results_so_far.json`・`_combo_results/*.json`・`raw_usage_log.
  jsonl`・`run_metadata.json`・`a2/`・`b1b/`配下の各run成果物)は
  いずれも本Trial実行により実在を確認済み。
- 参照した既存Report(`FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01_REPORT.
  md`・`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`・
  `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`・
  `FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06_REPORT.
  md`)はいずれもroot直下に実在確認済み。
- SSOT(`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`・
  `ARTIFACT_REGISTRY.md`)・`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.
  md`は本Trialで編集していない(委任文の並列条件どおり)。

---

## 13. QCD(Quality / Cost / Delivery)

- **Quality**: 到達点は6節参照。N=2×2条件のため統計的確証はなし、
  方向性の一貫性(4/4本が同一方向)のみ。拡充Ledgerの3節記載の限界
  (URL再訪問未実施)は既知の残課題。
  Overlap閾値0.40・Loop Budget=2・Overlap Checker自体はいずれも
  無変更(Trial harness内のみの条件比較、Production影響なし)。
- **Cost**: 実測¥184.6(段階1: Ledger調査¥148.6、段階2・3: 記事生成
  4本¥36.0)、予算¥200以内でSTOP。今後の追加Trial(候補X)は
  Ledger再利用によりLedger調査費用¥148.6が発生しないため、¥50〜100
  程度で計画N=6/条件へ到達可能と見込む。
- **Delivery**: 次の1手はユーザーによる11節項目1(追加予算承認)の
  判断。承認が得られれば候補X(N積み増し)をFable側で即日実施可能。

---

## 継続実行(Fable継続指示1回目)

管理ID: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`(Fableからの
継続指示1回目)。Fable判断により追加上限¥120で残りrun(条件A: A2×2+
B1B×2、条件B: A2×2+B1B×2、計8 run)を実行し、各条件N=6(A2×3/B1B×3)
まで揃えた。拡充Ledger(条件B、FACT-08〜14)は前回作成済みファイルを
無変更のまま再利用し、Research再実行(¥148.6)は発生していない。script
(`er011_news_ledger_enrichment_ab_trial_12_run.py`)は無変更のまま、
既存の`combo`サブコマンドへ新しいrun_idx(2・3)を渡して実行した(run1は
再実行していない)。並列条件(SSOT・`docs/pm/`・Production Prompt/コード/
QA閾値・Git操作)は前回同様、一切触れていない。実行前に既存python.exe
プロセスを確認し、走っていたのは無関係な別タスクの`run_project_
regression.py`のみで、本Trial自体の二重起動はなかった。8 runはすべて
前面同期・逐次実行(1本ずつ完了を確認してから次を開始)。

### 1. 完走したN・費用

- 完走: **N=12**(条件A=6本[A2×3+B1B×3]、条件B=6本[A2×3+B1B×3])。
- 費用(このセッションのみ、実測、`cost_summary.json`より): 条件A追加
  4本 ¥4.2+¥4.3+¥5.3+¥11.3=**¥25.1**、条件B追加4本 ¥3.9+¥10.5+
  ¥16.3+¥7.9=**¥38.6**、合計**¥63.7**(追加上限¥120以内、超過兆候なし
  のためSTOPなし)。1本ごとの実測費用をrun後に都度`compute_cost_so_
  far_jpy()`で確認しながら進行(累計¥22.92→¥55.90→¥63.77の順で推移、
  いずれの時点でも上限接近の兆候なし)。
- 累計(前回¥184.6+今回¥63.7〜63.8、丸め差): **総額¥248.4**
  (`cost_summary.json`の`total_jpy`、実測)。

### 2. 条件A vs 条件B(各N=6、合計12本)

| 指標 | 条件A(fact5件、n=6) | 条件B(fact12件、n=6) |
|---|---|---|
| 初期attempt flag率 | 100%(6/6) | 66.7%(4/6) |
| 最終NG率 | **83.3%(5/6)** | **33.3%(2/6)** |
| retry回数平均 | 1.833 | 0.833 |
| Point対Full Story overlap(Gate指標)平均 | 0.4497 | 0.370 |
| 同・NG群平均 | 0.478(n=5) | 0.4675(n=2) |
| 同・OK群平均 | 0.308(n=1) | 0.3212(n=4) |
| cross_point_overlap(Point One/Two直接重複)平均 | 0.169 | 0.144 |
| 同・NG群平均 | 0.15(n=5) | 0.112(n=2) |
| 同・OK群平均 | 0.265(n=1) | 0.16(n=4) |
| anchor衝突数平均(P1∩P2共有FACT-ID) | **1.5** | **0.0** |
| Point Oneへ割当てられたfact数平均 | 3.33 | 2.0 |
| Point Twoへ割当てられたfact数平均 | 2.83 | 1.33 |
| fact利用率(参照fact数/usable fact数) | 93.3% | 27.8% |
| Ledger Deviation(到達分のみ、いずれも0件) | 0件(到達1本) | 0件(到達5本) |
| Fact Checker verdict | PASS×1・未到達×5 | PASS×4・FAIL×1・未到達×1 |
| Directional Fact Precheck | PASS×1(到達1本) | PASS×1・DIRECTION_REVIEW_REQUIRED×3(到達4本) |

**最終NG率の内訳(新規、N=4時点では未分解)**: 条件Aの5NGのうち
lexical overlap(語彙重複)起因4件・value_qa起因のみ1件。条件Bの2NGの
うちlexical overlap起因1件・**Fact Checker FAIL起因1件(Overlap Gate
自体はretry1回で解消済みだった、条件A側には出現しなかった新しいNGモード)**。
「Overlap(lexical)起因NG率」だけで見ると条件A 66.7%(4/6)→条件B
16.7%(1/6)。

**統計参考値(Fisher正確検定・Welch t検定・Mann-Whitney U、いずれも
参考値であり有意性の断定ではない)**:
- 最終NG率(5/6 vs 2/6): Fisher p=0.242(有意でない)。
- lexical起因NG率(4/6 vs 1/6): Fisher p=0.242(有意でない)。
- 初期attempt flag率(6/6 vs 4/6): Fisher p=0.455(有意でない)。
- Gate指標(条件A vs 条件B、連続量): Welch t検定p=0.223、
  Mann-Whitney p=0.173(有意でない)。
- cross_point_overlap(条件A vs 条件B、連続量): Welch t検定p=0.669
  (有意差なし)。

### 3. 連続量評価(overlap_ratio、NG群・OK群、N=12で更新)

条件を混合したpooled NG群(n=7、条件A5本+条件B2本)とOK群(n=5、
条件A1本+条件B4本)でGate指標(Point対Full Story overlap最大値)を
比較すると、NG群平均**0.475**・OK群平均**0.3186**・差**0.156**、
Welch t検定**p=0.0039**、Mann-Whitney U検定**p=0.0073**と、本Trial
系列で初めて統計的有意水準に達した(参考値、以下の限界に留意)。

**限界(正直な報告)**: この二群比較は条件(Ledger fact供給量)とNG/OK
判定が直接連動しているため(条件Bはfact供給を増やしたことでNGが
減った側)、Trial-08のような「同一Ledgerでの診断分岐条件比較」とは
性質が異なり、単純な「連続量評価の検出力が高い」という結論の直接証拠
にはできない。ただし、同じデータでcross_point_overlap(Point-Point
直接重複)をNG/OK群で比較すると条件Aで0.15 vs 0.265・条件Bで0.112 vs
0.16と、**Gate指標(Point対Full Story overlap)ほど明確にNG/OKを
分離しない**ことが分かった。これは「連続量評価一般」ではなく、
「Point対Full Story overlapという特定の連続指標」がNG/OK判定と
強く結び付いている可能性を示す、より限定的だが有用な追加知見。

### 4. ¥0並行分析(a)〜(d)、N=12データで更新

**(a) threshold 0.40の妥当性**: 現時点評価は変わらず**判断材料不足**。
本Trial(N=12、p1/p2個別値24件)のうち既存監査の境界帯[0.363,0.437]
に該当したのは5件(20.8%)で、既存Trial-08の「約25%が境界帯」という
知見とおおむね整合する1追加サンプル群であり、閾値再校正(0.35/0.45)
の当否を判断する材料はなお不足している(既存240件データでの感度分析
結果を維持するのが適切)。

**(b) Overlap Checker(lexical overlap coefficient)**: **新知見あり**。
本Trialのfact利用率(条件A 93.3% vs 条件B 27.8%)・anchor衝突数
(1.5 vs 0.0)は条件間で明確に分離した一方、cross_point_overlap(本文
同士の直接lexical重複)は条件間(p=0.669)・NG/OK間のいずれでも明確な
分離を示さなかった。これは、**「テキスト表層の語彙重複」より
「Point Role Planning段階でどのFACT-IDを両Pointに割り当てたか」
という構造的指標の方が、fact供給量操作の効果を鋭敏に捉える**ことを
示唆する(既存r=0.46相関知見の精緻化)。Overlap Checker自体の改修
可否を判断する材料としては、引き続き判断材料不足。

**(c) retry(Loop Budget・retry責務競合)**: 既存評価(Loop Budget=2
自体の妥当性は本Trialでは未検証)を維持しつつ、**新たな限界が判明**。
条件Bの2NGのうち1件(enriched A2 run3)は、Overlap Gate自体はretry
1回で解消済み(lexical_flagged=False, value_qa_flagged=False)にも
かかわらず、その後段のFact Checkerでverdict=FAILとなり最終NGに
なった。fact供給を増やすとOverlap由来のretry依存は明確に下がる
(retry平均1.833→0.833)が、**増やしたfact自体の正確性(3節の
URL未検証の限界)が、Overlap/Loop Budgetとは独立した新しいNGモード
として表面化し得る**ことがN=12で初めて観測された。

**(d) 連続量評価の検出力**: 3節の結果により**UDR候補dへの支持材料が
明確化**。ただし「連続量評価一般が優れている」のではなく、「Point対
Full Story overlapという特定の連続指標」がNG/OKと強く結び付く
(pooled p=0.0039〜0.0073)一方、「cross_point_overlap(Point-Point
直接重複)」という別の連続指標は同程度の分離を示さなかった(p=0.669)。
連続量評価への切替を検討する場合、**どの連続指標を採用するかまで
含めて設計する必要がある**という、より具体的な示唆が得られた。

### 5. 判明したこと/棄却されたこと/残った有力候補(N=12で更新)

**判明したこと**:
1. Ledger fact供給量5→12件で、最終NG率83.3%→33.3%、lexical起因NG率
   66.7%→16.7%、retry回数平均1.833→0.833、anchor衝突平均1.5→0.0、
   fact利用率93.3%→27.8%——N=4(前回)からN=12(今回)へ拡大しても
   全指標で同一方向の改善が一貫して観測された。
2. ただし統計的有意性は指標により異なる。二値指標(最終NG率、Fisher
   p=0.242)は有意でない。一方、Gate指標(Point対Full Story overlap)
   の連続量でNG群/OK群を比較すると本Trial系列で初めて統計的有意水準
   (pooled p=0.0039〜0.0073)に達した(3節の限界に留意、条件操作と
   NG/OKが交絡しているため因果の強い主張はできない)。
3. 条件Bで唯一新たに観測されたNGモード(Fact Checker FAIL、Overlap
   Gateとは無関係)は、拡充Ledgerのfact精度検証(3節の限界、URL人手
   再確認未実施)がProduction採用の前提条件であることを実データで
   裏付けた。
4. cross_point_overlap(Point-Point直接lexical重複)は条件差・NG/OK差
   いずれも統計的に確認できず、構造的指標(anchor衝突数)の方が本
   Trialの操作効果を鋭敏に捉えることが分かった。
5. Ledger Deviation(LEDGER_COMPLIANT)は測定できた全run(条件A1本・
   条件B5本)で0件・完全遵守であり、両条件で差が見られなかった唯一の
   下流指標だった。

**棄却されたこと**: 前回同様、明確な棄却材料はなし。ただし
cross_point_overlapを診断・retry判定の主指標として使う案は、本Trialの
データ(条件差p=0.669、NG/OK差も不明瞭)では支持されず、優先度を
下げる方向の傍証を得た。

**残った有力候補**: 論点H(Ledger fact供給量仮説)は、N=12まで拡大
しても一貫した方向性を維持し、Overlap起因NG率という新しい切り口でも
支持された(66.7%→16.7%)。ただし最終NG率という最も単純な二値指標
では統計的有意性に達しておらず(p=0.242)、「効果が確定した」と
断定できる段階にはない。

### 6. 次Trial候補(N=12を踏まえて更新)

- **Fable側で実施可**: (1) cross_point_overlap(表層lexical重複)では
  なくanchor衝突数(Point Role Planningの構造的指標)をOverlap
  Checkerの補助シグナルとして使う設計の予備検討(コード変更なし、
  既存run成果物の追加分析のみ、¥0)。(2) 条件Bで発生したFact Checker
  FAIL 1件(enriched A2 run3)の内容を人間が精査し、拡充Ledgerの
  fact精度問題か記事生成側のfact誤用かを切り分ける(¥0、人手作業、
  Production採用判断[11節項目2]の前提材料になる)。
- **ユーザー判断が必要な項目(更新)**:
  1. 拡充Ledger(FACT-08〜14)のProduction採用可否(URL人手再検証が
     前提、11節項目2の内容は変わらず未着手)。
  2. UDR候補a(News方針の主軸を論点Hへ移すか): N=12でも一貫した
     方向性は維持されたが、最終NG率という主要二値指標は統計的有意
     水準に達していない(p=0.242)。単独で主軸移行を正当化する材料
     としては依然として不十分。
  3. UDR候補d(連続量評価への切替)を正式な検討フェーズへ進めるか:
     4節(d)のとおり、「Point対Full Story overlap」という特定指標
     では初めて統計的有意な分離(pooled p=0.0039〜0.0073)が観測
     されたが、「どの連続指標を採用するか」を含めた設計判断が必要で
     あり、既存Trial-08系譜との統合評価と合わせてユーザー判断を
     仰ぎたい。

### 7. Dangling Reference Check(継続実行分)

- 本節で参照した全ファイルの実在確認: `er011_output/news_ledger_
  enrichment_ab_trial_12/{a2,b1b}/{current,enriched}/run{2,3}/`配下の
  各`analysis.json`・`point_overlap_article_retry_log.json`・
  `run_summary.json`、`_combo_results/*_run{2,3}.json`、更新後の
  `all_results_so_far.json`(12件)・`final_analysis_summary.json`
  (条件ごとn=6)・`cost_summary.json`(total_jpy=248.4)は、いずれも
  本継続実行で実在を確認済み。script(`er011_news_ledger_enrichment_
  ab_trial_12_run.py`)は無変更。SSOT・`docs/pm/`・Production
  Prompt/コード/QA閾値は本継続実行でも一切編集していない。
