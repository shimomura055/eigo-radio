# 05 Fact台帳 明確化 Trial計画(案)(OPEN-233-LEDGER-CLARITY-DESIGN-01 委任_03a、¥0、2026-10-06)
性質: Trial計画の【案】。Opus条件Aレビュー(M1〜M6)を反映した確定案。すべて承認待ち(Status=USER_DECISION_REQUIRED)。実行・API・Production変更なし。基準は`04_design.md`(§3末尾・§13)と`03_trial_eval_design_draft.md`(§2〜§7)。

## 0 前提(Opus反映)
- Trial対象は本番推奨P'そのものではなく、既存台帳へ案C(明確化)をoffline適用した台帳B。P'の新規生成効果は別Trial(本計画の合格後、ユーザー判断)。
- Writerは台帳を直接読まずB3 briefを読む(M2)。よって測定は台帳→B3 brief→JA R0→R1/R2→ENの各段。
- 全フローChecker runは使わない(Phase 3のみ)。C_w(Writer初稿費)は未実測、Phase 2の最初の1 chainで実測。
- fixture: 開発例=meta(HC-012)・hormuz(HF-009)、held-out=HF-012・HC-014・small_bag方向語fact。事前固定しsha256凍結。

## 1 品質評価の事前定義
| 品質 | 測定方法 | 合格基準 | 検証件数 |
|---|---|---|---|
| ①重大Fact誤認 | 対象factの決定論語彙判定(例: 復元系語の有無)+各段(B3 brief/R0/R2/EN)の二重ラベル(Fable/Sonnet、labeling_guide準拠) | HC-012型の曖昧訳: Aで6/8以上に対しBで1/8以下。held-out(HF-012・HC-014・small_bag方向語fact)でB悪化なし(重大/runがA以下)。Aで基準発生0なら「悪化なしのみ、改善未証明」 | 3テーマ×台帳A/B×8 seed=48 chain |
| ②Checker精度 | Phase 1の決定論検査(既存SUPPORTED unitを新ブロックで再判定、¥0)+Phase 3で承認済み構成のA/B各2 run | 誤爆増0件、重大見逃し0維持、不要Rewrite/runがA以下 | Phase 1=3台帳全unit、Phase 3=A/B各2 run |
| ③自然さ・面白さ | (a)決定論指標: 文数・type-token比・文長・台帳逐語コピー率 (b)LLM pairwise(順序入替2回) (c)Fable抜粋確認 | 逐語コピー率+5pt以内、文長・語彙多様性が従来の±20%以内、pairwise「劣る」≤25%かつ4軸いずれも過半数でない | Phase 2の同fixture・同seed対 |
- (b)単独で合否を決めない。判定が割れた軸は引き分け。pairwise modelはWriter/Checkerと別系統にするか(コスト増)はユーザー判断。
- 第4指標(明確化の正確性): M3決定論diff通過率、変更fact全件のoffline照合NG件数。

## 2 Phase計画
### Phase 0(¥0・約20分)
- 既存の全R0/R2/ENから、HC-012・HF-009・HF-012・HC-014の言い換え方の基準発生率を集計(Meta R0は4系統中4で曖昧)。
- 目的: Aの基準発生率が低すぎれば、Phase 2で改善が測れないため計画見直し(STOP、USER_DECISION_REQUIRED)。
### Phase 1(約¥3〜6・約30分)
- meta・hormuz・small_bagの3台帳に案Cをoffline適用(元は不変、別名保存、sha256記録、`--ledger_path`はDEV限定)。
- M3決定論diff(fact_id集合・fact数・数値・日付・固有名・否定語・因果語。Checker正規表現`er052_open233_stage1_coverage_checker_01.py` L437-526再利用)。
- 変更fact全件をFable/Sonnetがoffline照合(原資料はURL再取得が別委任のため、原文未確認の多義語は「判定保留」)。
- 合格基準: 追加情報0件/意味確定の誤り0件/Checker決定論検査の誤爆増0件(既存SUPPORTED unitを新ブロックで再判定、¥0)。txt書式制約(M4)違反0件。
### Phase 2(上限¥60・約60分)
- B3+JA R0〜R2+ENのみ。台帳A(従来)/B(明確化)×3テーマ×各8 seed。
- 評価は上記①③。C_wは最初の1 chainで実測し、上限超過見込みならSTOP。
- 評価の台帳Bは事前に1回生成し全seedで固定。
### Phase 3(必要時、上限¥30・約30分)
- Phase 1・2合格後のみ。承認済みChecker構成でA/B各2 run、誤爆・見逃し確認。
- Production経路(承認構成)の挙動を変えずDEV経路で実行。

## 3 費用上限・所要時間(案)
| Phase | 上限 | 時間 |
|---|---|---|
| 0 | ¥0 | 20分 |
| 1 | 約¥3〜6(上限¥10案) | 30分 |
| 2 | ¥60 | 60分 |
| 3 | ¥30 | 30分 |
| 合計 | ¥100(上限案) | 約2.3時間+評価・SSOT約50分 |
- 見積は実行前に再提示。実費が見積の1.5倍または上限到達でSTOP。並列は台帳A/B・テーマ間のchainを3並列まで(条件同一、seed固定)。

## 4 揺れ対策・過学習防止
- seed 8、二重ラベル(別model/別prompt、順序入替)、LLM判定と決定論判定の併用。
- prompt規則に固有名・個別事例を入れない。合格基準・held-out・fixtureを事前固定しsha256凍結。held-outを調整に使わない。
- 台帳Bは事前生成・固定。seed間・条件間で台帳を変えない。

## 5 必要なDEV経路(Productionへ混入させない)
- B3およびJA Writerへ台帳パスを差し替えるDEV限定引数(`--ledger_path`等、未実装の【案】)。Production既定は従来(引数なし=従来動作)。
- 案C適用スクリプト、M3決定論diff、Phase 0集計スクリプト、pairwise評価script(いずれも新規DEV、Production無影響)。
- B3 briefへのphase/uncertainty引継ぎは本Trialでは変更しない(台帳変更の効果のみ測る)。

## 6 STOP条件
- 実費が見積の1.5倍/上限到達、API失敗率高(fail-closed連発)。
- Phase 0でA基準発生率が低く改善測定不能。
- Bで重大件数/runがAを上回る、held-outで新種重大が出た(過学習・副作用疑い)。
- Phase 1で追加情報・意味確定の誤りが1件でも出た(台帳Bを採用せず設計見直し)。
- Production経路へのTrial混入が見つかった。
- 上記はSTOPしUSER_DECISION_REQUIRED。

## 7 Status分類とユーザー判断
- Status: VALIDATED / REJECTED / USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない(採用は人間ユーザー承認+条件Cレビュー)。
- 判断事項: (1)Trial計画承認(上限¥100、Phase別承認か一括か) (2)Aで基準発生0の場合の扱い (3)pairwise別系統model (4)新Product仕様候補: P'採用・台帳スキーマ拡張・F1(Checker比較基準共有) (5)DEV経路`--ledger_path`追加実装の承認。

## 8 Dangling Reference(Glob/Grepで確認)
- 実在: `er019_output/meta/run_03/storyline_b3/selected_brief.md`(11行)、`.../ja_writer/original.md`(14行)、`.../b1b/article.md`(21行)、`er019_family_x_storyline_b3_fact_selection_01.py`、`er052_open233_self_recovery_precheck_01.py`の`TAG_LINE`(L60)・`parse_ledger_text`(L65)、`er052_open233_stage1_coverage_checker_01.py`の`numbers_not_in_facts`(L478)・`facts_have_causal`(L492)。
- 未確認: 各ファイル内の個別行番号(brief L4/L11、original L13、article L17、B3 py L78、Checker L437-526、precheck L92-96/L177/L3012)は委任文引用のまま本委任では再照合せず。
- 作成済み: `docs/pm/opus_l2_review_lc_design_01.md`(作成済み(2026-10-06、委任_03f、セッション記録から機械抽出・改変なし))。
- 新提案名(`--ledger_path`、`statement`/`events[]`等)は未実装の【案】。
