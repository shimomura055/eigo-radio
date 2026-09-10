# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14 報告書

管理ID: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14`
(News Ledger拡充Trial系譜の曖昧性解消Trial、Hanshin型、Sonnet委任)。
**Trial(Production実装ではない)**。Production/Prompt/QA/Validator/retry
コード・SSOT(`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`・
`ARTIFACT_REGISTRY.md`)・`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`・
Git操作は一切行っていない。monkeypatch・グローバル書き換えなし。
Production Ledgerへの拡充fact追加は行っていない。A/BのN増しは行って
いない。新規script(root、既存Production/Trialコードをimportして
無改変で呼び出すのみ): `er011_news_ledger_enrichment_disambiguation_
trial_14_run.py`。出力: `er011_output/news_ledger_enrichment_ab_trial_12/
{factcheck_censored,twofact_e,reaggregation}/`(新規サブディレクトリの
み)。既存Trial-12/12bの成果物は読み取り専用で一切変更していない。

## 要点(5行)

1. 「fact数が多いほど良い」仮説は**REJECTED**(既存C/D artifactの正式
   集計により再確認、fact10件[条件C]がfact5件[条件A]と同じ最終NG率
   83.3%)。
2. 打ち切り記事8本(見込み7本、実数8本)へFact Checker単独適用した結果、
   条件Aの「真のfact誤り率」(FAIL率33.3%、2/6)が判明し、これは条件B
   (16.7%)・D(16.7%)より高く、条件C(66.7%)より低い。FAILの77.8%
   (9件中7件)は人名ローマ字誤りであり、**全条件(A含む)で発生する
   Ledger非依存の基礎的な弱点**であることが確認された。
3. 条件E(A+FACT-11/14の2件のみ、Dと同数usable7件)はN=6で最終NG率
   16.7%(1/6)、fact数だけでなく「非headline角度の周辺factが1〜2件
   供給されること」自体が改善に寄与する可能性を示したが、N=6のため
   統計的有意性はない(Fisher p=0.08、A比較)。
4. 仮説「Pointごとに異なる非headline角度のEvidenceが供給されることが
   重要」は、**部分的にVALIDATED**(Point生成段階の構造指標では一貫して
   支持)だが、**Fact Checker以降の合否は依然としてfact固有の性質
   [固有名詞の多寡]に強く依存し、単一仮説では説明しきれない**
   (`USER_DECISION_REQUIRED`寄りの限定的支持)。
5. 費用実績: 段階1(12b集計)¥0、段階2(打ち切り記事8本FC単独適用)
   ¥65.3、段階3(条件E、N=6)¥82.0、**合計¥147.3**(上限¥150以内)。

---

## 0. Reconciliation Check + 費用確認

- 既存harness(`er011_news_ledger_enrichment_ab_trial_12_run.py`・
  `er011_news_ledger_enrichment_leaveout_trial_12b_run.py`)を無改変で
  import・再利用した。Production関数(`er003_v1_n3_01_articles_
  generate.build_common_block/build_prompt`・`er002_ja_web_research_r3.
  build_fact_check_prompt/make_fact_checker_fn/run_fact_checker_with_
  gates`)はすべて無改変で直接呼び出した(パラメータもProduction既定
  どおり、retry上限[Fact Checker最大2 attempt、Loop Budget=2]は無変更)。
- **費用見積りの修正(重要、正直な報告)**: 委任文の段階2見込み(¥15〜25、
  7本想定)は、過去のTrial-12実測から本Sonnetが再計算した結果、
  1回あたりのFact Checker単独呼び出し実測平均が約¥9(既存16件の
  web_search付き呼び出しの実測平均)であることが判明し、対象記事数も
  実数8本(7本ではない、1節参照)だったため、より現実的な見積りは
  約¥65〜110と大幅に上振れすると判断した。段階3(¥70〜100見込み)と
  合算すると合計見込みが¥150に接近・超過し得る状況だったため、
  段階2単独(¥150以内であることは確実)を先に実行し、実測を確認して
  から段階3の続行可否を判断する方針に切り替えた(委任文の趣旨
  [実行前に見積り、合計¥150超ならSTOP]を、実測を都度確認しながら
  段階ごとに検証する形で運用した)。
- 実測結果: 段階2実測¥65.3(見積りの妥当性を確認)、段階3実測¥82.0
  (委任文の見込み¥70〜100の範囲内)、合計¥147.3で上限¥150以内に収まった。
  段階3の最終run(条件E、B1B run3)を開始する時点での累計は¥134.17
  (残枠¥15.8)であり、過去の同型run実測(¥8.1〜¥19.2)を踏まえると
  残枠を超える可能性があったが、平均的な見込み(約¥13.5)は残枠内で
  あったため実行し、結果として合計¥147.3(上限内)に収まった。**この
  判断の余地(平均的見積りでは上限内だが最悪ケースでは上限を超え得た)
  は、事後の透明性のためここに明記する**。
- 二重起動なし(全て前面同期・逐次実行、combo単位で都度cost_so_farを
  確認)。バックグラウンド待機は個別のAPI呼び出し完了待ち(タイムアウト
  120秒超過時の自動background化)のみで、ポーリングによる新規処理の
  仕掛けはしていない。

---

## 1. 段階1: Trial-12b(条件C/D)集計結果(確定、新規API呼び出しなし¥0)

独立の報告書`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B_
REPORT.md`を作成した(経緯・詳細表・Close判定はそちらを参照)。要旨:

| 指標 | A(fact5) | D(fact7) | C(fact10) | B(fact12) |
|---|---|---|---|---|
| 最終NG率 | 83.3%(5/6) | 33.3%(2/6) | 83.3%(5/6) | 33.3%(2/6) |
| Fact Checker到達(元パイプライン) | 1/6 | 5/6 | 5/6 | 5/6 |

**Close判定: `REJECTED`(fact数単調仮説)**。fact10件(C)がfact5件(A)と
同じ最終NG率であり、fact数と最終NG率は単調でない。一方、初回attempt
Value QA flag(6/6→0/18)・anchor衝突(1.5→0〜0.167)は条件C/D/Bいずれも
一貫して改善しており、これは`VALIDATED`(限定範囲: Point生成段階の
構造的指標のみ)。

**「打ち切り記事」実数の確定(委任文の見込み7本との差異)**: `final_ng=
True`かつ`fact_verdict=None`(Fact Checker未到達)の行を機械的に抽出した
結果、**実数は8本**だった(条件A5本[A2×3+B1B×2]・条件B1本[A2 run2]・
条件C1本[A2 run1]・条件D1本[A2 run3])。委任文の見込み(条件A5本・C1本・
B/D各1本=計7本)との差異は「条件Bにも1本、打ち切り記事が存在する」点
(委任文はB/D「各1本」としていたが、これ自体は正しく、合計が7ではなく
8になったのは元の暗算誤りと判断される)。実数8本を対象として段階2を
実施した。

---

## 2. 段階2: 打ち切り記事8本へのFact Checker単独適用(確定、実測¥65.3)

対象8本(全てProduction既定のFact Checker関数を無改変で単独適用、
Web検索回数も既存設定のまま、最大2 attempt):

| 条件 | レベル | run | 元status | Fact Checker verdict(新規) | 主な指摘 |
|---|---|---|---|---|---|
| A(current) | A2 | 1 | NG_REVIEW_REQUIRED | **FAIL** | 代打選手名「Tora Fushimi」誤り(正: Torai Fushimi=伏見寅威) |
| A(current) | A2 | 2 | NG_REVIEW_REQUIRED | PASS | — |
| A(current) | A2 | 3 | NG_REVIEW_REQUIRED | **FAIL** | 代打選手名「Tai Fushimi」誤り(正: Torai Fushimi) |
| A(current) | B1B | 1 | NG_REVIEW_REQUIRED | REVIEW_REQUIRED | スコア推移の記述不正確・評価的表現(non-blocking) |
| A(current) | B1B | 2 | NG_REVIEW_REQUIRED | PASS | — |
| B(enriched) | A2 | 2 | NG_REVIEW_REQUIRED | PASS | — |
| C(leaveout_c) | A2 | 1 | NG_REVIEW_REQUIRED | PASS | — |
| D(twofact_d) | A2 | 3 | NG_REVIEW_REQUIRED | PASS | — |

### 2-1. 「条件Aの真のfact誤り率」(打ち切りバイアス除去後、N=6完全観測)

元パイプラインで到達した1本(PASS)と本段階で新規に判定した5本を合算し、
条件A・B・C・DいずれもN=6完全観測(Fact Checker verdict分布)を確定
できた。

| 条件 | usable fact | PASS | REVIEW_REQUIRED | FAIL | **FAIL率** |
|---|---|---|---|---|---|
| A(現行、fact5) | 5 | 3 | 1 | **2** | **33.3%** |
| B(全部、fact12) | 12 | 5 | 0 | **1** | **16.7%** |
| C(抜き取り、fact10) | 10 | 1 | 1 | **4** | **66.7%** |
| D(2件のみ、fact7) | 7 | 5 | 0 | **1** | **16.7%** |
| E(段階3、fact7) | 7 | 3 | 2 | **1** | **16.7%** |

**Fisher正確検定(参考値、N=6のため有意性の断定ではない)**: A(FAIL2/6)
vs C(FAIL4/6) p=0.567、A vs B/D/E(いずれもFAIL1/6) p=1.0、C vs D/E
p=0.242。**いずれも従来の有意水準に達しない**が、方向性としてはOpus
解釈(委任文冒頭)と一致する: fact数の多寡(5→7→10→12)ではなく、
**含まれる個別factの種類**(FACT-12/13/11/14=非headline角度の周辺fact
か、FACT-09/10=新規固有名詞[救援投手陣]を含むfactか)がFAIL率と
対応している。

### 2-2. Fact Checker指摘の類型タグ付け(手作業、全FAIL/REVIEW_REQUIRED
記事が対象、根拠引用付き)

全条件(A/B/C/D/E)の完全観測データから、FAILverdict9本・REVIEW_
REQUIRED verdict4本(計13本)の指摘内容を手作業で類型化した。

| 類型 | 該当記事数(FAILのみ) | 内訳 |
|---|---|---|
| (a) 人名ローマ字/表記ゆれ | **7/9(77.8%)** | A×2(伏見寅威→Tora/Tai Fushimi)、B×1(伊原陵人+岩崎優+及川雅貴の3名誤り)、C×4(伊原陵人×3+岩崎優/及川雅貴×1) |
| (b) 年次・序数 | 1/9(11.1%) | D×1(モンテロの来日年次を1年目→2年目と誤記) |
| (c) 数値・試合展開の事実誤認(Ledger外) | 1/9(11.1%) | E×1(9回裏の広島の得点機の有無を誤記述、Ledger記載fact自体とは無関係) |
| (d) 評価的表現(non-blocking、REVIEW_REQUIRED) | 4件(参考、FAILではない) | A×1・C×1・E×2(いずれも比喩・解釈表現の指摘、Fact Checker運用方針によりblockingとしない) |

**FACT-ID別FAIL寄与**: 伊原陵人(FACT-03、全条件で既存・共通)由来の
誤りはC(3件)・B(1件)で発生し、D・Eでは0件だった。岩崎優/及川雅貴
(FACT-09、条件B/Cのみに含まれる新規fact)由来の誤りはB(1件)・C(1件)
で発生し、FACT-09を含まないD・Eでは0件だった。**FACT-09を含む条件
(B・C)でのみ岩崎優/及川雅貴の誤りが発生している**ことは、Opus解釈
(委任文冒頭「FACT-09/10固有のリスク」)を直接裏付ける新規証拠である。
一方、伏見寅威(代打選手、既存の固定記事内容と推測されるが本Ledgerの
FACT-01〜07には明示IDがなく、Writerの一般知識または元記事本文からの
言及と考えられる)の誤りは**条件Aのみ**で発生しており、Ledger拡充の
有無とは無関係な、Writer側の基礎的な人名ローマ字化の弱さを示す
独立証拠である。

**結論(2節)**: Opus解釈の中心的主張「Fact Checker FAILは拡充の副作用
ではなく、条件A記事にも元々存在する潜在欠陥の露出(打ち切りバイアスの
解除)」は、**本段階の実測により支持された**。ただし、Opusが具体的に
予測した欠陥(伊原陵人のローマ字誤り)がそのまま条件A記事に現れた
わけではなく(条件Aの実際の誤りは伏見寅威の表記)、「人名ローマ字誤り
という類型が、Ledger拡充の有無によらず全条件で発生し得る」という、
より一般化された形で確認された。

---

## 3. 段階3: 条件E Trial(確定、実測¥82.0、上限¥150以内)

条件E: 条件A(FACT-01〜07)+FACT-11(佐藤輝28号の球種)+FACT-14(順位・
ゲーム差)の2件のみ(usable 7件、条件Dと同数)。Ledgerは既存Trial-12
条件Bファイルからの機械抜粋(新規research¥0)。N=6(A2×3+B1B×3)、
既存harness(Trial-12b)と同一関数を再利用。

| run | レベル | status | retry | 初回Value QA | Fact Checker verdict |
|---|---|---|---|---|---|
| 1 | A2 | OK | 1 | NG | PASS |
| 2 | A2 | OK | 2 | NG | REVIEW_REQUIRED |
| 3 | A2 | OK | 1 | PASS | PASS |
| 1 | B1B | OK | 0 | PASS | REVIEW_REQUIRED |
| 2 | B1B | OK | 0 | PASS | PASS |
| 3 | B1B | **NG_REVIEW_REQUIRED** | 1 | PASS | **FAIL** |

- 最終NG率: **16.7%(1/6)**(FAILはB1B run3、9回裏の広島の得点機の有無
  についての事実誤認、2-2節参照。FACT-11/14自体の誤用ではない)。
- anchor衝突数平均: 0.0(6本とも0)。retry回数平均: 0.833。fact利用率
  平均: 0.476。Gate指標平均: 0.2775(全条件中で最も低い)。
- Fact Checker到達: **6/6(100%)**、うちPASS 3・REVIEW_REQUIRED 2・
  FAIL 1。

### 3-1. 判定基準(委任文の目安、参考)との照合

委任文の目安: 「最終NG率33%前後→周辺fact2件があることが本質」
「83%前後→FACT-12/13固有」。実測は**16.7%**であり、いずれの目安値
よりも良好だった(むしろ条件D[33.3%]・条件B[33.3%]より低い)。
**N=6での統計的有意性はない**(Fisher正確検定、参考値):
- 最終NG率: A[5/6]vs E[1/6] p=0.080、D[2/6]vs E[1/6] p=1.0、
  C[5/6]vs E[1/6] p=0.080。いずれも従来の有意水準(p<0.05)に達しない
  (A vs Eのp=0.080が最も小さいが、これも有意ではない)。
- 「真のfact誤り率」(2-1節、FC FAIL率): A[2/6]vs E[1/6] p=1.0、
  C[4/6]vs E[1/6] p=0.242。

**解釈(断定は避ける)**: 実測値だけを見れば「非headline角度の周辺fact
が2件供給されること」自体が(FACT-12/13という特定の組み合わせに限らず)
最終NG率の改善に寄与する可能性を示す一貫した方向性(D 33.3%・E 16.7%
はいずれもA 83.3%・C 83.3%より低い)だが、**N=6×2条件では統計的に
確定できない**。また、条件Eで唯一発生したFAIL(2-2節(c))はFACT-11/14
自体の誤用ではなく試合展開の一般的な事実誤認であり、条件Dの唯一の
FAIL(モンテロ年次誤り)とは異なる原因である。

### 3-2. 保険文(hedging)・ローマ字誤りの観測(Gate化しない、参考記録)

条件E全6本の記事本文・Fact Checker指摘を確認した限り、新規に導入した
FACT-11(佐藤輝の球種)・FACT-14(順位・ゲーム差)に起因する固有名詞の
ローマ字誤りは0件だった(いずれも人名を新規に増やさないfactだった
ため、2-2節のFACT-09固有リスクとも整合)。一方、REVIEW_REQUIRED
(2件、A2 run2・B1B run1)はいずれも「試合の転機」「機運」等の評価的
表現(hedging寄りの解釈的言い回し)への指摘であり、他条件と同様の
傾向だった。

---

## 4. 総合Close判定

**仮説「Pointごとに異なる非headline角度のEvidenceが供給されることが
重要」に対する判定: `USER_DECISION_REQUIRED`寄りの部分的`VALIDATED`**
(全面的なVALIDATEDでもREJECTEDでもない、以下の理由による)。

### 4-1. 新規結果(本Trial-14で新たに確定)

1. 段階1(12b集計): 「fact数単調仮説」は`REJECTED`(fact10件[C]が
   fact5件[A]と同じ最終NG率83.3%)。
2. 段階2(打ち切り記事8本): 打ち切りバイアス除去後の「真のfact誤り率」
   はA 33.3%・B 16.7%・C 66.7%・D 16.7%(3節のE 16.7%と合わせ5条件
   完全観測)。FAILの77.8%(9件中7件)が人名ローマ字誤りであり、
   **全条件で発生する、Ledger拡充とは独立したWriter/Ledger転写の
   基礎的弱点**であることが確認された(Opus解釈と整合、ただし具体的な
   誤り対象人物は予測と異なった=より一般化された証拠)。
3. 段階2(FACT-ID別寄与): 岩崎優/及川雅貴のローマ字誤りはFACT-09を
   含む条件(B・C)でのみ発生し、FACT-09を含まない条件(D・E)では0件
   だった。これは「特定factの追加が特定の新規誤りリスクを線形に
   増やす」というOpus解釈の直接的な追加証拠である。
4. 段階3(条件E、N=6): 最終NG率16.7%は委任文の両判定目安(33%/83%)
   のいずれも下回り、「周辺fact2件供給」自体の効果を示す最も良好な
   結果だったが、N=6のため統計的に確定できない(4-2節参照)。

### 4-2. 過去再掲(本Trial-14の新規結果ではない)

- Trial-12(N=12、条件A/B比較)の最終NG率83.3%→33.3%(Fisher p=0.242、
  非有意)は`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_
  REPORT.md`の既存結果であり、本Trial-14では再検証していない。
- 「初回attempt Value QA flagが完全分離(6/6 vs 0/18)」は、Opus
  L2解釈(`...OPUS-L2-INTERPRETATION-01_REPORT.md`)による既存artifact
  の直読結果であり、本Trial-14の段階1集計により独立に再確認した
  (数値は完全一致)。

### 4-3. 進行中/未着手(本Trial-14でも解消していない)

- 拡充Ledger(FACT-08〜14)のURL人手再検証は未着手のまま
  (Trial-12報告書8節候補Y、Production Ledger採用の前提条件)。
- 「非headline角度の周辺fact」という条件の一般化可能性(Hanshin型
  以外の題材、FACT-11/14・FACT-12/13以外の周辺factの組み合わせ)は
  未検証。条件EはN=6・単一題材(Hanshin)・単一の周辺fact2件パターン
  のみであり、Opus解釈が示した「代替1案(¥250前後、別題材での
  A'/D'比較)」は実施していない。
- 人名ローマ字誤りを検出・防止する仕組み(Fact Checker側の観測項目
  拡充、Ledgerへの英語表記併記等)はすべて**候補**であり、いずれも
  Production実装・採用判断は行っていない。

### 4-4. ユーザー判断が必要な項目(候補、採用可否は判断していない)

1. 「非headline角度の周辺fact2件供給」という副仮説を、News Stage4の
   次Trial(別題材での一般化検証、見込み¥250前後)として継続するか。
2. Ledgerへの主要人名の英語表記併記(Ihara→Takato Ihara等)を、Fact
   Checker FAILの構造的抑制策として次Trialで検証するか(Opus提案、
   Production Prompt変更を伴うため、既存`docs/pm/PM_GOVERNANCE.md`の
   承認手続きが必要)。
3. 拡充Ledger(FACT-08〜14)のURL人手再検証(Trial-12から継続、未着手)。

---

## 5. 費用実績(段階別、JPY、実測)

| 段階 | 内容 | 実測費用 |
|---|---|---|
| 0 | Reconciliation・既存artifact確認 | ¥0 |
| 1 | Trial-12b(条件C/D)集計 | ¥0(新規API呼び出しなし) |
| 2 | 打ち切り記事8本へFact Checker単独適用 | **¥65.3** |
| 3 | 条件E Trial(N=6) | **¥82.0** |
| **合計** | | **¥147.3**(上限¥150以内) |

---

## 6. Dangling Reference Check

- 本報告で参照した全ファイルの実在確認: `er011_output/news_ledger_
  enrichment_ab_trial_12/{factcheck_censored,twofact_e,reaggregation}/`
  配下の全ファイル(`fact_qa.json`・`fact_check_attempts.json`・
  `cost_summary_censored.json`・`cost_summary_e.json`・
  `all_results_e.json`・`hanshin_ledger_condition_e_twofact.txt`・
  `trial14_stage1_full_summary.json`)、および段階2/3で生成した
  `twofact_e/{a2,b1b}/run{1,2,3}/`配下の各`analysis.json`・
  `run_summary.json`はいずれも本作業で実在・整合性を確認済み。
- `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`・
  `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-
  INTERPRETATION-01_REPORT.md`・`FAMILY-A-NEWS-STAGE4-LEDGER-
  ENRICHMENT-LEAVEOUT-TRIAL-12B_REPORT.md`(本Trialで新規作成)は
  いずれも実在確認済み。
- SSOT(`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`・
  `ARTIFACT_REGISTRY.md`)・`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`
  は本Trial-14で編集していない。Git操作(add/commit/push)は行って
  いない。Production/Prompt/QA/Validator/retryコードは無変更
  (新規script`er011_news_ledger_enrichment_disambiguation_trial_14_
  run.py`は既存Production/Trial関数をimportして無改変で呼び出す
  だけの薄いラッパーであり、呼び出し先の内部ロジックは一切変更して
  いない)。Production Ledgerへの拡充fact追加は行っていない。A/Bの
  N増しは行っていない。
