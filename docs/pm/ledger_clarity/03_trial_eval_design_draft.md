# 03 Trial評価設計ドラフト(OPEN-233-LEDGER-CLARITY-DESIGN-01 委任_01c、¥0、2026-10-06)
性質: 計画ドラフト。Trial未実行・API未呼出。新しい重大基準は作らず、既存の重大Fact誤り基準(`er052_output/open233_prod_e2e_01/labeling_guide_01.md` §1-1)で評価する。Fableが設計案確定後に統合。

## 0. 再利用資産の確認結果
- runner `er052_open233_self_recovery_flow_runner_01.py`: 引数は`--groups/--n_runs/--resume/--s1u/--instance_ids`等。**台帳(Ledger)パス差替え引数は無い**(Grep確認)。fixtureは`stage1_fixtures/*frozen.json`(Stage1入力=既存記事)。
- 重要【要確認】: runnerの実費¥3.5/run(新9 run平均3.502円、合計31.519円、`open233_prod_e2e_02/report_final/report_abcde.md`)は**Checker+後段+Rewrite**の費用。Writer初稿生成の費用はこの内訳に含まれない(内訳列にWriter無し)。Writerを台帳条件別に回す経路(Production Writer呼出+台帳差替え)は別途Trial用のDEV経路が必要。Production経路へ混入させない。
- ラベル基準: labeling_guide_01.md(重大/軽微/問題なし、true_problem/true_critical/rewrite_needed)。集計: `aggregate_report_abcde_01.py`(A〜E指標)。
- 記事Quality評価の既存手段: er0*.pyに`naturalness/readability/pairwise/diversity`のQuality専用判定は見当たらない(該当はStage2 downgrade系の別目的script)。**新規に簡易rubric(4軸pairwise)が必要**。
- Writer揺れの実績: 新9 runは同fixtureの複数条件で、費用が¥1.97〜¥5.66とrun間で2.9倍ばらつく(Rewrite有無が主因)。揺れは無視できない前提で設計。

## 1. 共通設計
- 比較条件: 従来台帳(A) vs 明確化台帳(B)。fixture・seed数・Writer model・Checker構成(承認構成固定)・温度を同一。差は台帳のみ。
- 過学習防止: (1)評価fixtureを3群に事前固定=開発例(HC-012,HF-009、明確化prompt設計に使用)/検証例(未使用の既存事例)/held-out(設計時に見ない新規事例、合否はこれ中心)。(2)明確化promptへHC-012/HF-009の文言・固有名を直接埋め込まない(一般規則のみ)。(3)Trial開始前に本ファイルの合格基準を固定、結果を見て基準を動かさない。
- 揺れ対策: 同条件を複数seed、件数でなく率+区間(件数小のためWilson区間または生の「k/n」併記)で示す。1件の差で合否を決めない。labelは別workerで重大判定のみ二重化(guide§53)。

## 2. 品質① Writerの重大Fact誤認が減るか
- 測定: Writer初稿(Rewrite前)に対し(a)現行Checker+後段の重大判定数、(b)Fable/Sonnet offline読解ラベル(labeling_guide準拠)の重大数。(b)を正とし(a)は参考。
- 指標: 重大誤り件数/run、HC-012型・HF-009型の発生率(k/n)、軽微件数/run(副作用監視)。
- 合格基準案: 明確化台帳で重大件数/runが従来以下、かつ開発例型の再発0、かつ検証例・held-outで従来比悪化なし(重大件数/runが従来を超えない)。改善を主張するには従来側でベースライン重大が1件以上出ていることが前提(従来側0件なら「悪化なしのみ確認、改善は未証明」と書く)。
- 件数案: low/mid/high は§5。high=fixture 4(開発2+検証1+held-out1)×2条件×3 seed、mid=3×2×2、low=2×2×2。

## 3. 品質② Checker精度(Checker構成固定)
- 測定: ①と同一runで、重大見逃し(ラベル重大かつ最終BLOCKINGなし)と不要重大判定(ラベル問題なし/軽微なのにBLOCKING/Rewrite)を条件別に集計(aggregate_report_abcde流用、A〜E指標)。
- 指標: 重大見逃し件数、不要重大判定件数、Rewrite件数/run、Stage1検出率。
- 合格基準案: 重大見逃し=0維持または減少、不要重大判定増加なし、Rewrite件数/runが従来以下。
- 注意: 明確化台帳で初稿の重大が減ると分母(重大数)が減り、検出率が見かけ悪化しうる。件数とあわせ分母併記。Checker自体の精度比較が主目的なら、既存の注入型(changed_number/actor等)対照fixtureを両台帳で流す補助比較を推奨(¥追加は下記)。
- 件数: ①のrunを共用(追加run無し)。補助対照は2 fixture×2条件×1 run。

## 4. 品質③ 記事の自然さ・面白さを損なわないか
- 測定: 同fixture・同seedの従来版/明確化版Writer出力を対で比較。
  (a)決定論指標(¥0): 文数、語彙多様性(type-token比)、文長分布(平均/標準偏差)、台帳文の逐語コピー率(明確化で台帳が冗長になり記事が台帳の丸写しになる副作用の検出)。
  (b)LLM pairwise(別prompt、新規rubric): 読みやすさ/自然さ/ストーリー性/多様性の4軸で「どちらが良いか+理由」。A/B順序を入替えて2回(位置バイアス対策)。2回で判定が割れた軸は「引き分け」。
  (c)Fable抜粋確認: 劣る判定の全件と無作為2対を人間可読で確認。
- 合格基準案: 明確化版が「劣る」判定の割合≤25%(4軸合算、引き分け除外前の全判定)、かつ4軸いずれも「劣る」が過半数でない、かつ逐語コピー率の上昇≤+5pt、文長・語彙多様性が従来の±20%以内。
- 件数: 対数=fixture×seed(mid 3×2=6対×順序2=12 call)。多様性軸は同条件seed間の分散(同一台帳内の記事の似通い)も別途見る。
- 注意: LLM判定は同一model相関・冗長性選好バイアスあり。(a)(c)と併用し、(b)単独で合否を決めない。

## 5. 費用式・時間
- 式: run数×(Writer初稿C_w + 承認構成flow ¥3.5) + 台帳明確化call(fact数×1、¥0.1〜0.3/fixture) + pairwise call数×¥0.2(全文比較のためStage2単価¥0.06より高めと仮定【推定】) + 補助対照(2fx×2条件×¥3.5=¥14、任意)。
- C_wは未実測【要確認】。Trial前に1 run実測。下表はC_w=¥1.5仮置き(括弧内はC_wがflow内包の場合)。
| 案 | 構成 | run数 | 概算 |
|---|---|---|---|
| low | 2fx×2条件×2seed(開発1+held-out1) | 8 | ¥42(¥30) |
| mid | 3fx×2条件×2seed(開発+検証+held-out) | 12 | ¥64(¥46) |
| high | 4fx×2条件×3seed(開発2+検証1+held-out1) | 24 | ¥127(¥90) |
- 上限案: 実行前に合計見積を出し、mid実費見積の1.5倍(目安¥100)を上限とする。low/mid/high選択はユーザー判断。補助対照は+¥14。
- 時間(3並列、run≈8分): low 8run≈25分/mid 12run≈35分/high 24run≈70分。+評価(ラベル・集計・pairwise)30分+SSOT/報告20分。合計 mid≈約1.5時間。台帳明確化は事前に1回生成し両条件で固定(seed間で台帳を変えない)。

## 6. STOP条件案
- 実費が事前見積の1.5倍/上限到達、API失敗率が高い(fail-closed連発)、明確化台帳で重大件数/runが従来を上回る、held-outで開発例型以外の新種重大が出た(過学習・副作用疑い)、Production経路(承認構成)へのTrial混入が見つかった場合はSTOPしUSER_DECISION_REQUIRED。
- Trialの`VALIDATED`はProduction仕様ではない。Production採用はユーザー承認+条件C Opusレビューが前提。

## 7. 未決(Fable/ユーザー判断)
1. Writer初稿生成のDEV経路(台帳差替え)の有無と実費C_w。2. 従来側で重大が出ない場合の「改善証明不能」の扱い。3. low/mid/high選択。4. 補助対照の要否。5. pairwise判定modelをWriter/Checkerと別系統にするか(コスト増)。
