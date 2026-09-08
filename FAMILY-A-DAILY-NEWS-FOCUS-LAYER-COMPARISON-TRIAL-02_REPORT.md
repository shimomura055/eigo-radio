# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02 報告書

管理ID: FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02(Lane A-1)。
**Trial(生成実行)。Production配線・Productionコード/Prompt/SSOT編集・Git操作は
一切行っていない。TTSは実行していない(text-onlyまで)。**
並列稼働中のLane A SSOT統合タスク・Lane B(`er012_*`)の成果物は参照していない。
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。

ユーザー決定根拠: 2026-09-08 A-UDR-8(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-
TRIAL-01_REPORT.md`の設計案を承認。同じHanshin Ledgerを固定し、Focus Module
なし/ありでA2/B1を比較しNews固有編集層の効果を切り分ける。最大Status=
VALIDATED。Production採用・配線はユーザー判断前に行わない)。

---

## 0. 使用したスクリプトとProduction path無変更の説明(Gate 4)

新規ファイル:
- `er011_daily_news_focus_layer_comparison_trial_02.py`(生成本体)
- `er011_daily_news_focus_layer_comparison_trial_02_cost_compute.py`(費用集計補助)

`er006_pool_pilot_01_writer.py::run_writer_for_theme`は、(1) `editorial_mode`
文字列を`EDITORIAL_TYPE_MODULE_BLOCKS`という**登録済み辞書**からのみ解決する
(`resolve_editorial_type_module_block()`、未登録文字列はfail-closedで
`ValueError`。本Major/Daily variantは未登録のため意図的に安全装置が働く。
回避していない)、(2) 出力先を常に`{out_dir}/b1b`・`{out_dir}/a2`に固定してお
り本Trialが要求する`{a2,b1b}/{baseline,focus}`ネスト構造を作れない、という
2点で本Trialの要件に合わない。そのため`run_writer_for_theme`の内部ループ
(28-89行)が呼んでいるのと**全く同じ順序・同じ引数**で、下位の公開関数
(`gen.build_common_block` → `gen.build_prompt` → `gen.run_one_pattern`、いず
れも`er003_v1_n3_01_articles_generate.py`の既存公開関数、monkeypatchなし・
`.replace()`等のテンプレート文字列置換なし)を本Trialスクリプトから直接呼ん
だ。baseline条件は`editorial_type_module_block=""`(既定値、`run_writer_for_
theme`に`editorial_mode=None`を渡した場合とバイト単位で同一prompt)、focus条
件は`editorial_type_module_block=MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK`
(DESIGN-TRIAL-01 §1.3ドラフトを無改変で使用)。`EDITORIAL_TYPE_MODULE_BLOCKS`
辞書へは登録していない(Productionコードは無変更)。Fact Checker・Ledger
Deviation Checker(Hook-aware)・Local Rewrite Loop・Point Overlap QA・
Diagnostic Full Retry・Point Role Planning・Evidence Compression Editor
(Numeric Precision含む)はいずれも`run_one_pattern()`の既定引数のまま(変更
なし)。Discovery Layer3・Reference Digest等のTrial-only仕様は混入していな
い。Household/Trend Synthesis系の内容も参照していない。

---

## 1. Major/Daily Gate 6項目の再確認(Hanshin)

`er011_daily_news_focus_layer_comparison_trial_02.py`内`MAJOR_DAILY_GATE_
CHECKLIST`として記録(詳細はスクリプト本体参照)。6項目すべてPASS、
**判定: MAJOR_DAILY**(DESIGN-TRIAL-01 §2.2の既存判定と一致、単一試合・単一
起点イベント、Ledgerだけでmechanism/beyond-the-headline factorの2つの異な
る意味づけを支える)。

---

## 2. 生成結果(4本、text-only)

Ledger: `er003_output/n3_01/hanshin/research/verified_fact_ledger.txt`
(承認済み、baseline/focus共通・完全同一)。出力: `er011_output/daily_news_
focus_layer_comparison_trial_02/{a2,b1b}/{baseline,focus}/`。

| 条件 | Level | status | fact_verdict | ledger_status | Point Overlap article retry | Point One overlap(flagged) | Point Two overlap(flagged) | 語数(概算) |
|---|---|---|---|---|---|---|---|---|
| baseline | A2 | **NG_REVIEW_REQUIRED** | (未到達) | (未到達) | 2/2(上限到達) | 0.448(**flagged**) | 0.314 | 283 |
| baseline | B1B | **NG_REVIEW_REQUIRED** | (未到達) | (未到達) | 2/2(上限到達) | 0.407(**flagged**) | 0.259 | 268 |
| focus | A2 | **NG_REVIEW_REQUIRED** | (未到達) | (未到達) | 2/2(上限到達) | 0.333 | 0.577(**flagged**) | 269 |
| focus | B1B | **OK** | REVIEW_REQUIRED(non-blocking advisory) | LEDGER_COMPLIANT(deviation 0件) | 1/2(1回で解消) | (最終report解消済み) | (最終report解消済み) | 217 |

閾値はいずれも0.4(既存Production既定、変更していない)。「NG_REVIEW_
REQUIRED」はPoint-only regenerationがER-008-N8-FINAL-QA-HARDENING-21で
Production自動経路から外されているという既存の安全装置(Fact fabrication事
例があったため)によるもので、本Trialが新たに発生させたものではなく、既存
Diagnostic Full Retry(記事全体再生成、上限2回)を尽くしてもなお解消しなかっ
た**実際のProduction QA結果**として記録する(自動続行・上限回避は行ってい
ない)。focus B1Bのみ全QAチェーン(Fact Checker→Ledger Deviation→
Directional Fact Precheck)まで到達し、`directional_fact_precheck_status=
DIRECTION_REVIEW_REQUIRED`(「8-1」表記の桁順チェックに関する既知の非
blocking advisory、Focus Moduleとは無関係の既存汎用チェック)も記録された
が、いずれもnon-blockingでstatus=OKに影響しない。

費用(実測、`er005_output/cost_baseline_01/pricing_snapshot.json`基準):
baseline ¥10.3(24 calls)、focus ¥13.8(22 calls)、**合計¥24.1**(上限¥80
以内)。baseline/focusとも4本中2本がPoint Overlap NGで早期終了したため
(Fact Checker以降のAPI callが発生しない)、当初想定(¥30〜80)より低額だっ
た。詳細: `er011_output/daily_news_focus_layer_comparison_trial_02/cost_
summary.json`。

---

## 3. 焦点構造(Point Role)比較

| 記事 | Point One | Point Two |
|---|---|---|
| 現行Production Hanshin A2(2026-08-17公開) | 「早いホームランが試合全体を変えた」= mechanism | 「阪神は隙を見せなかった」= beyond-the-headline factor |
| 現行Production Hanshin B1B(同上) | 「Sato's Home Run Changed the Shape of the Game」= mechanism | 「The Late Runs Showed Hanshin's Full Strength」= beyond-the-headline factor |
| **baseline** A2(本Trial) | 「Hiroshima answered once, but could not build a comeback」= 相手の反応の限界(certainty/limitation caveat寄り) | 「The win belonged to more than one bat」= beyond-the-headline factor |
| **baseline** B1B(本Trial) | 「The moment the game could have changed」= 同上(限界・緊張点の明示) | 「More than one answer at the plate」= beyond-the-headline factor |
| **focus** A2(本Trial) | 「The win came from more than one hitter」= beyond-the-headline factor | 「One home run, but no rally」= 限界(同上ロール、位置が入替) |
| **focus** B1B(本Trial) | 「More than one bat carried the offense」= beyond-the-headline factor | 「One home run, but no lasting attack」= 限界(同上ロール、位置が入替) |

**観察1(共通)**: baseline/focus 4本すべてで、現行Production記事とは異なる
2つのRole(「beyond-the-headline factor(他選手の貢献)」+「相手の反応が限
界的だったことの明示」)が採用され、現行記事のPoint One役割だった
「mechanism(先制点が投手を楽にした)」は4本のいずれにも現れなかった。

**観察2(Focus Moduleの効果として観測できたこと)**: baseline→focusで、
Point One/Twoの**役割の入れ替え**(beyond-the-headline factorが先、限界の
明示が後)が両Levelで一貫して起きた。B1Bでは、この入れ替えが起きたrunで
Point Overlap QAが解消(retry 1回でOK)。A2では同じ入れ替えが起きたが、
Point Two側(「限界の明示」役)の語彙が試合終盤の描写(Ihara/five innings/
Montero等)とFull Storyに強く重複し、baselineのPoint One(0.448)より高い
0.577まで悪化してNG_REVIEW_REQUIREDのまま残った。

**観察3(重要な限界・アーキテクチャ上の発見)**: `run_one_pattern()`内の
Point Role Planning呼び出し(`point_planning.run_point_role_planning(client,
topic, verified_ledger_text, ...)`)は**`editorial_type_module_block`を一
切受け取っていない**(baseline/focus共通の同一シグネチャ)。実際に
`point_role_planning_initial.json`をbaseline/focusで比較すると、role文言
はcondition間で毎回異なる(例: A2 baselineのPoint One roleは「Hanshin's
early leverage」、A2 focusのPoint One roleは「two-stage game」)。これは
LLM呼び出しの確率的変動によるものであり、Focus Module文言がPoint Role
Planning自体を直接誘導した結果ではない可能性が高い(Focus Moduleが実際に
影響できるのは、Point Role Planningの計画結果が既にprompt末尾へ挿入された
**後**の最終Writer本文生成呼び出しのみ)。したがって、観察2で見えた
Point One/Two役割の入れ替えを「Focus Moduleが役割選択を明確化した効果」と
断定することはできない。**N=1(各条件A2/B1B各1本)では、Focus Moduleの因
果効果とrun-to-runの確率的変動を統計的に分離できない**(本Trialの構造的
限界として明記する)。

---

## 4. 副作用の有無

- **Retry回数**: baseline(A2=2, B1B=2)→focus(A2=2, B1B=1)。B1Bはretry減、
  A2は変化なし(共に上限到達)。Focus Moduleによる系統的なretry増加は観測
  されなかった。
- **Overlap悪化**: A2ではfocus条件の方がPoint Two overlapがbaselineの
  Point One overlapより高い(0.577 > 0.448)。ただしこれはPoint One/Twoの
  役割入替に伴う結果であり、「Focus Moduleが常にoverlapを悪化させる」と
  一般化できるサンプル数ではない(§3観察3参照)。
- **事実逸脱**: focus B1B(唯一Ledger Deviation Checkerまで到達した記事)
  は`LEDGER_COMPLIANT`(deviation 0件)。baseline/focus A2・baseline B1Bは
  Point Overlap NGでLedger Deviation Checker自体に到達していないため比較
  不能。
- **Numeric Precision/Evidence Compression**: 4本すべてで
  `evidence_compression_applied: true`(既定どおり適用、Focus Moduleの有無
  で挙動変化なし)。
- **新規失敗パターンの発生**: なし。既存の安全装置(Point-only regeneration
  無効化、Diagnostic Full Retry上限2回、fail-closedなeditorial_mode解決)
  はいずれも回避せず、そのまま機能した。

---

## 5. Gate 4観点(再確認)

- Production Writer正式path(`gen.build_common_block`/`build_prompt`/
  `run_one_pattern`)は無変更で利用し、Trialスクリプトから直接呼んだ理由
  (raw block非対応・出力先固定の2点)を§0で明記した。monkeypatch・
  テンプレート文字列置換は使用していない。
- `EDITORIAL_TYPE_MODULE_BLOCKS`辞書・`resolve_editorial_type_module_
  block()`・`er003_v1_n3_01_articles_generate.py`本体はいずれも編集して
  いない(grep差分なし、本Trialはimport only)。
- Discovery Layer3・Reference Digest(Trend Synthesis施策2、DEFERRED)・
  Household/Trend Synthesis固有仕様は混入していない。
- Lane A SSOT統合タスク・Lane B(`er012_*`)の成果物は参照していない。
- 費用¥24.1(実測)は上限¥80以内。TTSは実行していない。Git操作なし。

**結果: PASS(Trial-only仕様・未承認仕様の混入なし)。**

---

## 6. Gate 1分類・USER_DECISION_REQUIRED

**Gate 1分類: USER_DECISION_REQUIRED**(4本中2本[A2 baseline/focus]が
Point Overlap QAで`NG_REVIEW_REQUIRED`のまま終了しており、Focus Module
単体の効果を「VALIDATED」と結論づけるだけの安定した合格サンプルが揃わな
かった。B1Bはfocus条件のみ完全PASSだが、baseline B1Bとの対比が
retry回数減少という間接指標に留まり、Point構造の役割入替がFocus Module
の因果効果かrun-to-run変動かを§3観察3の理由で切り分けられない。設計自体
[DESIGN-TRIAL-01]はVALIDATEDのままだが、本比較実行の結果は採用判断の材料
としてはまだ不十分)。

採用判断・次段階に向けた論点:

1. **Point Role Planningへのeditorial_type_module_block未接続**(§3観察3、
   本Trialで新たに発見): Focus Module文言がPoint Role Planning自体には
   届いていない。Major/Daily variantを本格導入する場合、Point Role
   Planningへも同様のNews固有ガイダンスを渡す設計に拡張するか、それとも
   現状どおり最終Writer呼び出しのみに留めるかは未決定。
2. **Focus Module文言の確定**: §1.3ドラフト(DESIGN-TRIAL-01由来、本
   Trialで無改変使用)をそのまま採用するか、A2側のoverlap悪化(観察2)を
   踏まえた語彙調整を行うかは未決定。
3. **mode名`"major_daily_news"`の登録可否**: DESIGN-TRIAL-01 §1.4候補の
   まま。今回は`EDITORIAL_TYPE_MODULE_BLOCKS`辞書へ未登録(Trial限定の直
   接注入のみ)。
4. **Gate記録機構の流用**: 本Trialは`MAJOR_DAILY_GATE_CHECKLIST`をTrend
   Gate同様の手動記録形式でスクリプト内に持たせたのみで、`trend_gate_
   checklist`引数のようなrun_metadata.json記録経路への統合は行っていな
   い。Major/Daily Gate専用の同型記録経路を`run_writer_for_theme`へ追加
   するかは未決定。
5. **N数不足の解消要否**: 本比較はA2/B1B各1本(baseline/focus)。Point
   Overlap QAの確率的変動が結果を大きく左右したため(§3観察3)、採用判断
   の前に複数run(同一Ledger・同一条件での再試行)によるrun-to-run変動の
   定量化が必要かどうか。
6. **A2でのoverlap悪化への対応要否**: focus A2のPoint Two overlapが
   baseline A2のPoint One overlapを上回った(観察2)。これがFocus Module
   語彙(特に「distinct layer of meaning」「what remains unconfirmed」等)
   由来の系統的な副作用かどうかは未確認であり、対応(語彙修正/Point Role
   Planningとの接続改善)が必要かは今回の範囲外。

以上、いずれも実装せず提案・列挙のみ。本Trialでの追加API呼び出し・コード
変更・SSOT編集・Git操作は行っていない。
