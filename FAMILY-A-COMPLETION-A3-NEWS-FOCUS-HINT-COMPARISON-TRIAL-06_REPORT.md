# FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06 報告書

管理ID: `FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06`(Lane A
Step A3)。**Trial(生成実行の再比較)。Production/Prompt/SSOT編集・Git操作は
一切行っていない。monkeypatch・グローバル書き換えなし。TTSは実行していない
(text-onlyまで)。** 並列稼働中のA2 Trend end-to-end(`er011_output/family_a_
completion_a2_*`)・A4 Discovery設計・Lane B 3V Trial(`er012_*`)の成果物は
参照していない。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。

ユーザー決定根拠: A3-UDR-1=(i)(Point Role hint[Trial-03、VALIDATED]+News
Focus Module[Trial-01設計/Trial-02文言]+G1修正済みProduction
[`OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01`、PRODUCTION_
WIRED]で、Hanshin Ledger固定・N=3の再比較)。A3-UDR-2=(i)(手動Mode判定+手動
Ledger供給、Trend Synthesisと同じ機構)。閾値0.40・Loop Budget 2は変更して
いない。

新規ファイル(Production未編集): `er011_news_focus_hint_comparison_trial_
06.py`、`_stats.py`、`er011_output/news_focus_hint_comparison_trial_06/`一式。

---

## 1. 14本の結果一覧

| run | 条件 | Level | status | retry | P1 overlap | P2 overlap | P1 role | P2 role | 語数 | 秒 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | baseline | A2 | NG | 2/2 | 0.462(F) | 0.464 | mechanism | other | 220 | 230 |
| 2 | baseline | A2 | NG | 2/2 | 0.433(F) | 0.556(F) | other | other | 290 | 207 |
| 3 | baseline | A2 | NG | 2/2 | 0.370 | 0.500(F) | other | other | 240 | 222 |
| 1 | baseline | B1B | NG | 2/2 | 0.457(F) | 0.303 | other | mechanism | 268 | 235 |
| 2 | baseline | B1B | NG | 2/2 | 0.440(F) | 0.483(F) | other | other | 269 | 217 |
| 3 | baseline | B1B | NG | 2/2 | 0.414(F) | 0.444(F) | beyond_headline | other | 250 | 235 |
| 1 | focus_hint | A2 | **OK** | 2 | 0.393 | 0.148 | other | other | 260 | 226 |
| 2 | focus_hint | A2 | NG | 2/2 | 0.357 | 0.258 | mechanism | other | 292 | 225 |
| 3 | focus_hint | A2 | NG | 2/2 | 0.400(F) | 0.455 | other | other | 277 | 256 |
| 1 | focus_hint | B1B | NG | 2/2 | 0.500(F) | 0.323 | mechanism | other | 276 | 149 |
| 2 | focus_hint | B1B | **OK** | 0 | 0.297 | 0.314 | other | other | 279 | 102 |
| 3 | focus_hint | B1B | **OK** | 1 | 0.394 | 0.226 | other | mechanism | 251 | 133 |
| 1(bonus) | hint_only | A2 | **OK** | 1 | 0.333 | 0.258 | mechanism | beyond_headline | 233 | 180 |
| 1(bonus) | hint_only | B1B | NG | 2/2 | 0.333 | 0.375 | mechanism | other | 259 | 252 |

閾値0.40(既存Production既定、変更なし)、(F)=flagged。詳細:
`{a2,b1b}/{baseline,focus_hint,hint_only}/run{N}/analysis.json`。

---

## 2. 集計(条件別、`stats_summary.json`)

| 指標 | baseline(N=6) | focus_hint(N=6) | hint_only(N=2、bonus) |
|---|---|---|---|
| NG率 | **100%(6/6)** | 50%(3/6) | 50%(1/2) |
| retry平均 | 2.0 | 1.5 | 1.5 |
| P1 overlap平均(flag数) | 0.429(5件) | 0.390(2件) | 0.333(0件) |
| P2 overlap平均(flag数) | 0.458(5件) | 0.287(1件) | 0.317(0件) |
| 語数平均 | 256.2語 | 272.5語 | 246.0語 |
| P1 role分類率(mechanism/beyond/limitation) | 33.3%(2/6) | 33.3%(2/6) | 100%(2/2) |
| P2 role分類率 | 16.7%(1/6) | 16.7%(1/6) | 50%(1/2) |
| 本文がroleを体現(キーワード一致) | **0/9 classifiable** | **0/9 classifiable** | 0/9 |

レベル別(3本中OK数): baseline A2=0/3・B1B=0/3(**両レベルとも全滅**)。
focus_hint A2=1/3・B1B=2/3。**Focus Module+hintのfocus_hint条件は、
baselineに対して両レベルで一貫してNG率が低い**(Trial-04で見られた
「レベル間で逆方向」という弱点は今回は再現しなかった)。

役割再現率(キーワード機械分類、簡易ヒューリスティック): mechanism/
beyond_the_headline/limitationへの分類ヒット率はbaseline/focus_hintで
同水準(P1 33.3%、P2 16.7%)、hint_onlyのみP1が100%(N=2と極小)。「本文が
roleを体現しているか」のキーワード一致は、分類できた9件全てで0件
(baseline3+focus_hint3+hint_only3の内訳)。人手による抜粋読み(§4参照)
では、focus_hint条件のPointは意味的にはmechanism/beyond-the-headline寄り
の設計が多く見られたが、キーワード一致ベースの機械判定では検出できな
かった(Trial-04と同じ限界、キーワードリストの語彙が実際のWriter出力の
言い回しと一致しにくい)。

---

## 3. Trial-04との比較(G1修正の効果とhint接続の効果の切り分け)

| 指標 | Trial-04 baseline(**G1修正前**、N=6) | 本Trial baseline(**G1修正後**、N=6) | Trial-04 focus(N=6) | 本Trial focus_hint(N=6) |
|---|---|---|---|---|
| NG率 | 66.7%(4/6) | **100%(6/6)** | 50%(3/6) | 50%(3/6) |
| retry平均 | 1.67 | 2.0 | 1.50 | 1.5 |
| P1 overlap平均 | 0.389 | 0.429 | 0.331 | 0.390 |
| P2 overlap平均 | 0.339 | 0.458 | 0.301 | 0.287 |

**観察(参考データ、OPEN-134関連、正式Production run扱いではない)**:
G1修正後のbaselineは、G1修正前のTrial-04 baselineよりNG率・overlap平均が
**悪化**しているように見える。ただし各NGは全て既存の安全装置(Point
Overlap/Value QA、閾値0.40、Loop Budget 2)が正しく作動した結果であり、
原因不明の新規failure modeではない(全NGでlexical_flagged/value_qa_
flaggedのいずれかが明示的に記録されている)。N=3/レベルは統計的に弱く、
この悪化がG1修正自体に起因するのか、単なるサンプリング変動か(OPEN-134の
既存記載どおり「G1配線だけでは解消しないNG要因が一定割合で存在する」)は
本Trialだけでは切り分けられない。**focus_hint条件のNG率はTrial-04と同一
(50%)で、focus_hint条件は今回もbaselineより一貫して良好**(baseline
100%→focus_hint50%)であり、hint接続がFocus Module本文注入と組み合わさっ
た効果自体は今回もbaselineに対して悪化していない。

本Trialの結果は`er011_output/point_overlap_observation_log.jsonl`(OPEN-134
正式観測ログ、20 run Exit条件カウント対象)へは追記していない(本Trialは
`run_writer_for_theme`経由の正式Production runではなくtrial harness実行の
ため、Exit条件の正式カウントを汚染しないため)。上表は参考比較としてのみ
本レポートに記載する。

---

## 4. 副作用・観測ノート

- 新規failure modeの発生: なし。既存の安全装置(Point Overlap retry上限
  2回・Fact Checker FAIL時停止・Local Rewrite cycle上限・Directional Fact
  Precheck)はいずれもそのまま作動した。
- `hint_only A2 run1`でdirectional_fact_precheck_status=
  `DIRECTION_REVIEW_REQUIRED`が1件観測された(既存`er008_directional_
  fact_precheck_08.py`が定義する4状態の1つ、non-blocking advisory、
  status="OK"のまま完了しており新規状態ではない)。
- 4/14本で本文に`## Main Story`という表記ゆれの見出しが挿入され、
  Trial-04由来の`section_word_counts`ヘルパーがintro語数を0と計上する
  既知の限界を確認した(Production自体の不具合ではなく、Trial側の分析
  ヘルパーの限界。`metrics.json`の総語数は別途正しく計算されている)。
  baseline/focus_hint双方で発生しており、hint条件固有ではない。
- 自然さ(簡易・抜粋読み): focus_hint/hint_onlyのOK例(`a2/focus_hint/
  run1`、`b1b/focus_hint/run2,3`、`a2/hint_only/run1`)を読んだ限り、
  不自然な語彙混入・機械的な言い回しは見られず、baseline同様の流暢な
  成人向けニュース英語だった。
- baselineへの副作用: baseline条件自体はhint="" ・Focus Moduleなしの
  Production既定と同一設定であり、本Trialの実行がbaseline自体の挙動を
  変えたわけではない(§3の悪化は「G1修正済みProductionを新たに実測した
  結果」であり、本Trialのコードが新たな副作用を注入したものではない)。

---

## 5. 費用・latency(実測)

**費用**: 合計**¥85.6**(上限¥150以内、N=2縮小・STOPは不要だった)。
`cl.install()`は`setup`ステージ冒頭で1回有効化し、以降のcombo単位の
別プロセス実行でも同一`raw_usage_log.jsonl`へ正しく追記された(append
モード、`er005_cost_logger.init_logger`の既存挙動を利用)。

| 内訳 | 費用 |
|---|---|
| baseline(N=6) | ¥29.3 |
| focus_hint(N=6) | ¥41.7 |
| hint_only(N=2、bonus) | ¥14.6 |
| run1(4本) | ¥42.0 |
| run2(4本) | ¥20.0 |
| run3(4本) | ¥23.6 |

**latency**: 101.6秒(focus_hint B1B run2、retry0)〜255.6秒(focus_hint
A2 run3、retry2)。focus_hint条件はOK例でretry0-1が多く相対的に短い。

---

## 6. Gate 4 / Gate 1分類 / Production配線に必要な判断

**Gate 4**: PASS。`gate4_g1_freshness_check.json`で機械確認済み:
`t3.run_one_pattern_connected`は`build_diagnostic_retry_prompt`自体を
別途コピーしておらず、`prod_gen.build_diagnostic_retry_prompt(...)`を
直接呼び出している(=G1修正はimport時点のProductionモジュールから常に
反映される)。現在importされている`prod_gen.build_diagnostic_retry_
prompt`のソースにG1修正マーカー(`OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-
REGRESSION-FIX-01`)が存在することも確認した。`er003_v1_n3_01_articles_
generate.py`/`er011_point_role_value_planning_01.py`/Trial-02/03/04は
いずれもimportのみで無編集(diff行数200行、Trial-03ヘッダー記載の4種類の
既知の変更[関数名/新規引数/呼び出し置換/prod_gen.修飾]のみに由来する
ことを`gate4_run_one_pattern_diff.txt`で確認)。

**Gate 1分類: USER_DECISION_REQUIRED**。理由:
1. focus_hint条件はbaselineに対し両レベル一貫してNG率・overlap平均が
   良好(Trial-04で見られたレベル間の逆方向傾向は今回出なかった)ものの、
   focus_hint自体のNG率は50%と依然として高く、「効果が十分」とまでは
   言えない。
2. G1修正後のbaselineがTrial-04(G1修正前)より悪化して見える観測(§3)
   は、既存安全装置の正常作動によるものであり新規failure modeではない
   が、原因(G1修正の副次効果かサンプリング変動か)を本Trialだけでは
   切り分けられない。
3. 役割再現(role文言のhint語彙反映)は今回もキーワード機械判定では
   低水準(P1 33%、P2 17%)で、Trial-04と同程度に留まった。
4. 新規failure mode・重大な副作用は観測されなかった(§4)。

**Production配線に必要な判断項目(実装しない、次段階向け)**:
1. Focus Module最終文言(`MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK`)の確定。
2. Point Role hint文言(`MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK`)の確定
   (反映率の低さを踏まえ、JSON schema自体へrole候補enumを追加する等の
   強化要否)。
3. mode名`major_daily_news`を`EDITORIAL_TYPE_MODULE_BLOCKS`辞書へ登録
   するか否か(現状未登録、Trial限定の直接注入のみ)。
4. Point Role hint接続の共有Writer配線範囲(Trend側は`point_role_hint_
   block=""`を維持する前提)。
5. baseline NG率100%(本Trial)の扱い: G1修正後の正式Production観測
   (OPEN-134 Exit条件の20 run)を優先し、本Trialの参考データだけで
   Production側の追加対策要否を判断しないことの確認。
6. N数不足の解消要否: baseline/focus_hintはN=3/レベル、hint_onlyは
   N=1/レベル(bonus)に留まる。

---

## 7. 新規ファイル一覧

- `er011_news_focus_hint_comparison_trial_06.py`(生成本体、CLI分割実行
  対応: `setup`/`combo <condition> <A2|B1B> <run_idx>`/`cost`/`aggregate`)
- `er011_news_focus_hint_comparison_trial_06_stats.py`(条件別・レベル別
  集計)
- `er011_output/news_focus_hint_comparison_trial_06/`(`{a2,b1b}/
  {baseline,focus_hint,hint_only}/run{N}/`各記事一式、`_combo_results/`、
  `all_results_so_far.json`、`stats_summary.json`、`cost_summary.json`、
  `gate4_g1_freshness_check.json`、`gate4_run_one_pattern_diff.txt`、
  `run_metadata.json`、`run_config.json`、`raw_usage_log.jsonl`)
- `FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06_REPORT.md`
  (本ファイル)

Git操作・Production/Prompt/SSOT編集は一切行っていない。
