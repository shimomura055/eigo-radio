# EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04

## ユーザー指示(原文)
> 前回のFable推奨「別テーマでもう1本Trial」は採用しません。次の記事・次テーマには進まないでください。理由は、今回の550語/744語という長さが、単なる軽微な超過ではなく、Family C仕様そのものが文章を膨らませている可能性を疑うべき水準だからです。したがって、まず同一テーマ・同一記事で長文化原因を是正してください。重要なのは、単にWriter Promptへ「もっと短く」と追記することではありません。まず費用ゼロで、なぜFamily Cが長くなるのかを構造的に診断してください。(中略)そのうえで、必要なら…仕様を再設計してください。(中略)目標は、研究・データ解説感0+Fact Safety維持+感情強度維持+Futureらしい没入感維持+A2/B1の標準分量内です。「少し長いが許容」とする前提では進めません。特に今回のような大幅超過を次テーマへ持ち越すのは禁止です。まず診断を行い、仕様原因を特定してください。その後、同一Ledger・同一テーマで最小再Trialが必要なら、Family C残額内で実施して構いません。ただし、別テーマTrialには進まないでください。Trial終了時はREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかに分類してください。Family CもまだProduction採用承認ではありません。

## 0. 実測の訂正(重要、最初に報告)
ユーザー原文は「550語/744語という長さが…大幅超過」という前提だったが、
実測ではTrial-03当時の目安(A2: 450-600語、B1: 500-700語。いずれも
CURRENT_SPEC正式値ではなくTrial限定の例示値)に対し、**A2=550語は範囲内
(PASS)、B1=744語は44語=6.3%の超過**であり、「大幅超過」という前提とは
一致しなかった。この点はまず訂正して報告する。ただし、後述の構造診断
(時点数×場面必須要素の積が語数をほぼ決定していた)は、超過の大小に
かかわらず、テーマが変わればさらに悪化しうる構造的リスクであり、respec
の必要性自体は妥当と判断した。

## 1. 構造診断(¥0、根拠付き)

### 1-1. 最大の要因: Layer2/3が"完成品に近い3場面"を事前生成していた
Trial-02で生成され、Trial-03/04で無変更のまま再利用しているLayer2/3
成果物(`er013_output/family_c_future_trial_02/research/layer23_v2_result.json`)
は、本テーマに対し`[IMAGINED_FUTURE]`を**3件**(scene_id/timeframe/
scene_summary付き)生成していた。Writer Prompt(v2/v3)自体は「機械的に
3時点へ当てはめる必要はない」と明記していたが、実際のTrial-02/03は
両方とも、この3件をそのまま1対1で3つの`[[IMAGINED]]`ブロックへ展開して
いた。**Writer Promptの文言ではなく、Layer2/3が渡す"材料の数"が実質的な
時点数を決めていた**、というのが本診断の最大の発見である(事前指定Grep
一覧外の追加確認。理由: Writer Prompt自体には3時点を強制する記述が
なく、原因を特定するために`er013_family_c_future_ledger_02.py`を追加で
確認した)。

### 1-2. 第2の要因: 場面あたりの3点セット構造の反復
Trial-03実記事(A2=550語/B1=744語)を段落単位で実測すると、各時点は
ほぼ均等に次の3要素を繰り返していた。
- `[[IMAGINED]]`枠(場面+反応+選択、約150-250語)
- 枠外の一般示唆パラグラフ(hedge付き、約30-75語)
- 期待/希望 vs 不安/懸念の対比文(Promptは「記事のどこかで1回」だったが、
  実際はほぼ毎場面で重複、約25-60語)

実測: A2は3ブロックで188+166+194=548語(実測550語とほぼ一致)、B1は
245+245+244+7(タイトル)=741語(実測744語とほぼ一致)。**時点数×この
3点セット構造の積が、総語数をほぼそのまま説明していた**。

### 1-3. 副次的要因: World Scaffoldの入力量
World Scaffold(25件の生statement)は全てWriterへ渡っていたが、実記事で
直接言及されたのは各記事とも数テーマのみで、25件を網羅する圧力は
確認できなかった(主要因ではない)。ただし入力トークン量削減の観点で
絞り込みを行う価値はあると判断した。

### 1-4. 想像/事実区別の指示: 既にv3で解消済み
v3で「場面直結の反応・選択まで[[IMAGINED]]枠内に含める」よう変更した
結果、枠内hedge密度はTrial-03実測でA2=0%/B1=2.3%(閾値内)であり、
この設計は既に有効に機能していた(v2時点の問題であり、v3で解消済み。
v4でも無変更で維持)。

## 2. 仕様変更(v3→v4契約差分)
新規ファイル`er013_family_c_future_writer_04.py`
(既存`_01/_02/_03`は無編集のまま保持)。
1. **場面数を2へ決定的に削減**: Layer2/3出力(無変更のまま再利用、
   追加LLM呼び出し費用¥0)から、コード側の決定的ルール
   (`select_scenes_for_v4`、3件以上なら最初と最後を採用)で2場面のみ
   Writerへ渡す。
2. **各場面の役割整理**: 1つ目=変化の始まりと期待寄り、2つ目=定着後の
   葛藤・懸念寄り、と明示。
3. **場面あたりの感情を1つに限定**(v3は「最低1回」で複数感情が重なり
   やすかった)。
4. **期待/希望 vs 不安/懸念の対比は、全場面終了後の統合示唆段落の中で
   1回だけ**とし、各場面の枠外パラグラフでの重複を明示的に禁止。
5. **場面ごとの枠外パラグラフを廃止**し、単一の統合示唆段落に統一。
6. **World Scaffold/FUTURE_ASSUMPTIONを、採用した2場面のgrounded_inで
   参照される項目のみに決定的にフィルタ**(`build_trimmed_world_
   package_text`、追加LLM呼び出し費用¥0、本テーマで25件→14件に削減)。
7. **語数目安を調整**(Trial限定、CURRENT_SPEC正式値ではない):
   A2 450-600→380-520、B1 500-700→450-620。
8. 禁止表現・FACT例外・IMAGINED/META構文・枠内hedging免除はv3から無変更。

編集Gate(`er013_family_c_future_qa_03.py`の`scan_editorial_gate_v3`)は
無編集のまま再利用(word_count_target_rangeのみv4値を渡す汎用設計の
ため、新規qa_04は作成不要と判断)。

## 3. offline検証(¥0)
- 新規ファイルのみ追加(`er013_family_c_future_writer_04.py`、
  `er013_family_c_future_trial_04_run.py`)。既存`_01/_02/_03`・
  Production経路・Discovery成果物は無編集。
- `reuse_research`ステージ実行(¥0): 場面3→2、Scaffold項目25→14
  (11件削減)を確認。
- `run_project_regression.py --pattern "er013*"`: **67/67 PASS**
  (既存`_02`24件・`_03`21件を含む、無変更で全PASS)。
- `run_project_regression.py`(default全件): **collected=2557
  passed=2554 failed=3**。3件は本タスクと無関係(1件は回帰harness自身の
  自己診断用フィクスチャ`er003_test_bad`の意図的な失敗ケース、2件は
  `er003_test_p2j_investigate.py`の既存P2I/P2J関連調査テストで、本タスク
  で一切触れていないファイル。事前diffにも含まれない無関係な既存差分)。

## 4. 最小再Trial(同一テーマ・同一Ledger・同一World Scaffold再利用)
`er013_family_c_future_trial_04_run.py`実行(実費計¥20.53、Family C
残額¥125.54→¥105.01)。

| 項目 | Trial-03 A2 | Trial-04 A2 | Trial-03 B1 | Trial-04 B1 |
|---|---|---|---|---|
| word_count | 550(範囲内) | **405(範囲内)** | 744(44語=6.3%超過) | **484(範囲内)** |
| [[IMAGINED]]場面数 | 3 | 2 | 3 | 2 |
| 編集Gate | PASS | PASS | FAIL(製品名漏れ+語数) | **PASS** |
| 枠内hedge密度 | 0.0% | 0.0% | 2.3% | 0.0% |
| Fact Checker A' | REVIEW_REQUIRED | REVIEW_REQUIRED(不変) | REVIEW_REQUIRED | REVIEW_REQUIRED(不変) |
| Ledger Deviation | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| Future Framing QA v2 | PASS | PASS | PASS | **REVIEW_REQUIRED(新規)** |

詳細比較・記事全文リンクは`er013_output/family_c_future_trial_04/
comparison.md`・`index.html`(Trial-03と並置)。

### 研究解説感0・Fact Safety・感情強度・没入感の維持状況
- 数値・研究語・製品名の混入: A2/B1とも**0件**(編集Gate実測、fail_reasons
  空)。研究解説感0を維持。
- Fact Safety: Ledger Deviation Checkerは両レベルとも
  `LEDGER_COMPLIANT`を維持。Fact Checker A' verdictは`REVIEW_REQUIRED`
  のままだが、これはTrial-03から不変であり、本Trialの変更(語数構造)
  が原因ではない(**本Trialの診断・対処対象外の既存事項**、別途調査が
  必要)。
- 感情強度・没入感: 引用(A2)「"It is not only a vacuum," she says.」
  「"I still have to guard the difficult parts," she says.」、
  (B1)「"I wanted fewer decisions," she says」など、行動・台詞による
  感情提示は場面ごとに1つに整理されても維持されていた(主観評価で
  Trial-03と同等、目立った低下は確認できなかった)。

## 5. まだ残る構造問題(新規、respecが生んだ副作用)
B1でFuture Framing QA v2が`REVIEW_REQUIRED`となった。原因は、v4契約が
「統合示唆段落は全場面を描き終えたあとに1つだけ」と指示したにもかかわらず、
実際の生成では**場面1と場面2の"間"に**この段落が挿入され、かつ
"Residents prepare the floor..."「The robot takes the routine route;
the person remains the final judge…」「the quiet house **will** still
be waiting for a human choice」のように、hedging("might"/"could")を
使わない断定的な文が複数含まれていた。A2側では同種の問題は発生しな
かった(Framing QA PASS)。これはv3から持ち越された問題ではなく、**v4の
「単一の統合示唆段落」設計が新たに生んだ副作用**であり、次の追加修正が
必要と考えられる: (a)統合示唆段落の配置を「2つ目の[[IMAGINED]]ブロックの
直後、記事の最後の見出しの中でのみ」と、より具体的に固定する、
(b)締めの一行を含め、統合示唆段落内で"will"のような断定助動詞を使わない
よう明示的に禁止する一文をPromptへ追加する。この2点は本Trialでは未実装
(追加のSonnet往復が必要)。

## 6. 実費(API別+5区分)
- 作業A(構造診断・respec設計・offline検証): ¥0(既存成果物のread-only
  再利用+コードのみ、追加API呼び出しなし)。
- 作業B(Trial-04 A2+B1生成・Gate・Fact Checker A'・Ledger Deviation・
  Local Rewrite・Future Framing QA v2、OpenAI): ¥20.53
  (内訳は`er013_output/family_c_future_trial_04/cost_summary.json`・
  `raw_usage_log.jsonl`)。
- 合計本Trial実費: ¥20.53(Family C残額¥125.54→¥105.01)。
- 5区分: Research/Scaffold/Layer2-3=¥0(再利用)、Writer生成=Writer呼び出し分、
  Fact Checker A'=fact_check呼び出し分、Ledger Deviation/Local
  Rewrite=deviation_check呼び出し分(rewrite cycle実行なし、0回)、
  Future Framing QA v2=framing_qa呼び出し分。詳細金額はraw_usage_log.jsonl
  の各`logging_context`ラベル別に集計可能(本REPORTでは概算合計のみ記載)。

## 7. Gate 1判定材料(Fableへの提供情報)
- 診断: ¥0で完了、根拠(実データの段落別語数表・Layer2/3出力の実物)付きで
  主因を特定できた。
- respec: 実装完了、offline回帰PASS(67/67 + 全体2554/2557、無関係3件
  除き問題なし)。
- 効果: 語数超過は解消(A2 -26%/B1 -35%、B1の6.3%超過も解消)。研究解説感0・
  Fact Safety(Ledger Deviation)・数値/製品名混入0は維持。
- 新規課題: B1でFuture Framing QA v2がREVIEW_REQUIRED(統合示唆段落の
  配置とhedging不足、respecの副作用)。
- 既存未解決事項(本Trial対象外): Fact Checker A' verdict=REVIEW_REQUIRED
  がA2/B1ともTrial-03から不変(本Trialの診断・修正範囲外)。

## 8. ユーザー判断事項
1. B1のFuture Framing QA v2 REVIEW_REQUIRED(§5)を、追加のSonnet往復
   (Prompt微修正+再生成、Family C残額¥105.01内、小額)で解消するか。
2. Fact Checker A' verdict=REVIEW_REQUIRED(A2/B1ともTrial-03から不変、
   本Trialでは変更していない)を、別タスクとして調査するか。
3. 本Trialの分類判断(下記)への同意。

## 9. Trial分類
**USER_DECISION_REQUIRED**
(理由: 本タスクの主目的であった「語数構造の診断・respec」は、実測根拠
付きで原因特定→契約変更→語数超過解消[A2/B1とも目安内]まで到達し、
研究解説感0・Fact Safety[Ledger Deviation]・数値/製品名混入0は維持
された。一方で、respecの副作用としてB1でFuture Framing QA v2の新規
REVIEW_REQUIREDが発生し、Fact Checker A' REVIEW_REQUIREDも[本Trial範囲
外ながら]両レベルで残っており、「安全に完全にPASS」の状態には未到達
のため、REJECTEDでもVALIDATEDでもなくUSER_DECISION_REQUIREDとした。
別テーマへは一切進んでいない。)

## 10. SSOT追記文案(編集は行っていない、案のみ)
`OPEN_ITEMS.md`または`ER-013`系REPORTへの追記案:
> Family C(Future)の長文化原因は、Writer Prompt自体よりも、Layer2/3が
> 事前生成する[IMAGINED_FUTURE]場面数(本テーマでは3件)が実質的な時点数を
> 決めていたことが最大要因と判明した(EDITORIAL-FUTURE-FAMILY-C-LENGTH-
> DIAGNOSIS-AND-RESPEC-TRIAL-04)。場面数をコード側で決定的に2へ絞り込み、
> 統合示唆段落を記事全体で1回に統合するv4契約により、同一テーマでの
> 語数超過は解消した(A2 -26%/B1 -35%)が、B1で統合示唆段落の配置・
> hedging不足によるFuture Framing QA v2の新規REVIEW_REQUIREDが発生して
> おり、追加修正が必要(USER_DECISION_REQUIRED)。Fact Checker A'
> verdict=REVIEW_REQUIREDはTrial-03から不変で本Trial範囲外の既存事項。
> Family CはまだAPPROVED_FOR_PRODUCTIONではない。

## 変更ファイル一覧
- 新規: `er013_family_c_future_writer_04.py`、
  `er013_family_c_future_trial_04_run.py`、
  `er013_output/family_c_future_trial_04/**`(生成物一式)、
  `docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04.md`、
  同`_check.json`、`docs/pm/RESULT_PACKET_FC4.md`、本REPORT。
- 無編集: 既存`er013_*_01/_02/_03`全て、Production経路、SSOT本文
  (`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`等)。
- Git操作: 行っていない(別途Fableが統合)。
