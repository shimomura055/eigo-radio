## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_01: 着手前スコーピング=実装範囲・test計画・E2E計画・時間見込み・費用見積の作成。¥0、read-only+計画doc作成のみ)。並行タスクなし。git操作・SSOT編集はしない(実装委任で実施)。

**作業方式(必須)**: 書き出しは`Write`/`Edit`ツールで§単位に小分け(1回30〜40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2〜3分割して逐語保存。説明・思考は最小限、事実と見積に集中。目標所要時間: 20〜30分。

## 性質/到達上限Status/禁止事項

- 性質: 計画(¥0)。到達上限: 計画doc完成(`PLAN_READY`)。実装・test・E2Eは本委任ではしない。
- 前提(ユーザー決定、2026-10-06): 以下2点は**APPROVED_FOR_PRODUCTION**(人間ユーザー承認済み)。ただしE2E・runtime evidence・SSOT確認までは**PRODUCTION_WIRED**としない。
  1. Checker仕様(RECLASSIFY-02でVALIDATED): 「Ledgerに書いていない」だけでは候補にしない/Ledgerとの食い違い・具体的新事実の追加を候補とする/主体・相手先(対象)・範囲・限定条件も照合する。
  2. 後段の機械判定(deterministic floor)を縮小: **数字(changed_number)に関する機械判定のみ残す**。主体・否定・比較・時期・因果など、それ以外の「AI判定を強制的に重大へ上書きする機械判定」は**廃止**(追加確認トリガーとしても残さない。時期のverifyも廃止対象)。
- 禁止: コード・Prompt・SSOTの変更(本委任は計画のみ)/有料API/gold・Safety-critical定義の変更/E2E開始。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **条件A該当(Production初回経路+後続経路の処理構造変更、実装前)**。本計画docがOpusレビュー対象になる(Sonnetは依頼しない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文、要点)

> 目的: ユーザー承認済みの以下2点をProduction正式経路へ反映し、新仕様で20 run E2Eをやり直す。1. 今回TrialでVALIDATEDになったChecker仕様を正式採用(「Ledgerに書いていない」だけでは候補にしない/Ledgerとの食い違い、具体的新事実の追加を候補とする/主体・相手先/対象・範囲・限定条件も照合する)。2. 後段の機械判定を縮小(数字に関する機械判定のみ残す/主体・否定・比較・時期・因果など、それ以外の「AI判定を強制的に重大へ上書きする機械判定」は廃止する)。両方ともユーザー承認済みのため APPROVED_FOR_PRODUCTION。ただし、E2E・runtime evidence・SSOT等まで確認するまでは PRODUCTION_WIRED としない。
> まず作業開始前に報告すること: 実装・必要test・最初の9 run E2E完了までに必要な時間の見込みを先に報告する。可能なら、実装/test/9 run E2E/集計・報告の大まかな時間内訳も示すこと。その報告後、ユーザーの追加回答を待たず作業を継続してよい。
> E2Eの進め方: 旧仕様で完了済みの9 runは、新仕様の正式Evidenceには使用しない。新仕様で20 runを最初からやり直す。今回はまず、新仕様 9/20 runまで実行 → 集計 → 報告で一旦区切る。残り11 runは、その9 run報告をユーザーが確認した後に進める。
> 9 run中のSTOPルール: 品質問題・重大Fact見逃し・Human Reviewが発生しても、そこでSTOPしない。9 runは最後まで走らせ、結果をまとめて報告すること。問題を見つけても、その場で勝手に仕様変更・Prompt変更・追加対策を実装しない。API障害・実行不能・データ破損など、物理的に9 runを継続できない技術障害だけは例外として報告する。
> 報告で必ず出す数値: A. Checker(AI判定: 候補件数/真に問題/不要候補化。機械判定: 同。AI+機械: AIのみ/機械のみ/両方重複/延べ/重複除外後総候補)。B. 後段判定(後段AI: 重大/軽微/問題なし件数、事後評価: 真に重大/不要に重大/真に重大なのに軽微・問題なし。後段機械判定[数字のみ]: 発火/AI判定との重複/真に重大/不要に重大化)。C. Rewrite(発生件数/発生run数/必要/不要/再修正要)。D. Human Review(目標0、発生時は対象英文・Ledger Fact・Checker AI/機械判定・後段AI/機械判定・Rewrite内容・Recheck結果・直接原因)。E. Safety・Cost(真の重大見逃し/重大検出/run別費用/合計/平均/Rewrite・Checker・後段判定の費用分離)。
> Production Wiring確認: 初回経路だけでなくRewrite後Recheck/retry/fallback/regeneration/最終出口確認でも矛盾がないこと。旧仕様の「数字以外の機械的強制重大化」が後段経路に残っていないこと。必要なRegression/integration testを実施しruntime evidenceを残す。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS等は実態に合わせて更新する。9/20 run時点ではPRODUCTION_WIRED完了扱いにしない。9 run終了後は残り11 runを勝手に開始せず、報告して待つ。

## KPI provenance欄

本委任は計画のみ。計画docに、9 run E2Eの各KPIのprovenance(すべてfresh・Production初回path含むE2E=Yes)と、事後評価ラベル(真に問題/不要)の付け方(Ledger原文照合、Sonnet推測ラベルはFable/ユーザー確認前提)を定義する。

## Opus台帳更新

参照のみ: `docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `OF-04[3-8]` →FLOOR分析のOpus指摘(特に「時期は承認済みverify維持」「hold-outでneg3 gold[時期]をfloorが拾っていた」)を計画docの「リスク」節に、ユーザー決定(時期floor廃止)との関係として記す(台帳編集なし)。

## 事前指定Read一覧

1. `docs/pm/reclassify_open233_checker_selectivity_02.md`: 全文(VALIDATED仕様の問い・4観点・schema・結果)。
2. `er052_output/open233_reclassify_02/reclassify_candidates_02.py`: Grep `PROMPT|SYSTEM|schema|actor_match` →prompt本文とschemaの範囲(Production checkerへ移植する正本)。
3. Stage 1 coverage checker `er052_open233_stage1_coverage_checker_01.py`: Grep `def |PROMPT|SYSTEM|changed_|r3|r5|union|schema` →構造(r3/r5 prompt定義・出力schema・`changed_*`フラグ生成・∪統合・決定論検査)の範囲のみ。全文Read禁止。
4. runner `er052_open233_self_recovery_flow_runner_01.py`: Grep `def apply_floor|apply_floor_cited|FLOOR_FLAGS|FLOOR_VERIFY_MODE|FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS|floor_verify_target|changed_number|tier0|CAUSAL_FLOOR|deterministic_floor` →各±30行(floorの適用箇所を初回/Recheck/retry/fallback/regen/出口の全経路で列挙)。Grep `def run_instance|def main|--stage|--budget-jpy|e2e` →E2E実行のエントリと引数。
5. `docs/pm/e2e_plan_open233_stage1_loop2_01.md`: 全文(前回E2E 20 runの構成・順序・費用実績・閾値)。
6. `docs/pm/e2e_stop_analysis_open233_01.md`: Grep `費用|¥|run別` →前回9 runのrun別費用(見積の基準)。
7. `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`: 全文(68行、リスク転記用)。
8. 既存テスト `er052_open233_self_recovery_flow_runner_01_test_01.py`: Grep `floor|Floor|changed_` →floor関連テストの件数・クラス名のみ(変更が必要なテストの見積)。`er052_open233_stage1_coverage_checker_01_test*.py`(Globで特定): Grep `class |def test_` →件数のみ。
9. `CURRENT_SPEC.md`: Grep `OPEN-233|deterministic floor|FLOOR_VERIFY|Stage 1 coverage|coverage checker` →該当行±5行(更新が必要な仕様箇所の特定)。
10. `OPEN_ITEMS.md`: Grep `OPEN-233-A1-PROD|OPEN-233-KPI-RECOVERY|RECLASSIFY-02` →行頭ID・Statusのみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 旧仕様の「数字以外の機械的強制重大化」残存箇所: runner全体をGrep `changed_actor|changed_negation|changed_comparison|changed_time|changed_causality|tier0` →BLOCKING上書きに使われている箇所を全列挙(初回/Recheck/retry/fallback/regen/exit/Stage 3 ladder/T/STAGE4理由)。計画docに「変更箇所一覧(ファイル:行:現挙動→新挙動)」として記す。
- Checker側: coverage_checkerのr3/r5 promptに新しい問い+4観点を入れる場合の変更箇所、出力schema追加(`actor_match`等)、`changed_*`フラグ生成(数字以外のフラグは生成を止めるか・生成はするがfloorで使わないか=**設計判断として両案を併記、推奨を1つ**。記録・分析用に生成維持が有利な点とProduction単純化の点を比較)。
- 事後評価(真に問題/不要)の付け方: Ledger原文+notes_for_writerとの逐語照合手順、判断不能の扱い、Fable/ユーザー確認の位置。
- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_01.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_01.md_check.json`
2. 計画doc `docs/pm/plan_open233_checker_floor_production_e2e_01.md` を§単位で作成: §0前提(ユーザー決定2点、APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED未)/§1 変更箇所一覧(Checker: prompt・schema・フラグ/floor: `apply_floor`と全経路の残存箇所/設定フラグ既定値)/§2 設計判断(数字以外のフラグ生成の扱い、時期verify廃止の扱い、Stage 2(後段AI)は不変であることの確認、S1の扱い)/§3 test計画(変更・追加・削除するテスト、integration test、runtime evidenceの残し方、回帰の基準件数)/§4 E2E計画(新仕様20 run構成と順序[前回計画を踏襲し9 runで区切る]、`--budget-jpy`、技術障害のみSTOP、Human Review等では止めない設定、run別出力の保存先、集計script[A〜Eの数値を出す]の有無と作成要否)/§5 時間見込み(実装/test/9 run E2E/集計・報告の内訳、委任回数の目安)/§6 費用見積(9 run: low/mid/high、前回実績ベース+新仕様での候補減・Rewrite減の仮定を明記)/§7 リスク(Opus指摘との関係: 時期floor廃止でhold-out neg3 gold型を拾えるかはStage 1新仕様+Stage 2依存、E2Eで測定/4観点追加によるCheckerコスト増[01→02で+¥0.09/run]/境界例・予測文の過検出)/§8 Existing Spec Check(A/B/C)とCURRENT_SPEC更新箇所/§9 Opus条件Aレビューに渡す論点案。
3. `docs/pm/RESULT_PACKET.md`へ要約(T-0結果、時間見込み、費用見積、変更箇所件数、リスク、一覧外Read理由)を上書き。
4. git操作なし。

## SSOT追記文

なし(計画のみ)。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

1. T-0結果。2. 時間見込み(実装/test/9 run E2E/集計・報告、合計)。3. 費用見積(9 run low/mid/high、根拠)。4. 変更箇所一覧の要約(ファイル・箇所数)。5. 設計判断の推奨(フラグ生成の扱い等)。6. リスク要約。7. 一覧外Read理由。8. 計画docの絶対パス。最終報告は15行以内。

