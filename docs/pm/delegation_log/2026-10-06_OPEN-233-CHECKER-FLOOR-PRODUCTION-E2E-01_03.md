## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_03: ユーザー決定[APPROVED_FOR_PRODUCTION 2点]のSSOT逐語記録・ACTIVE_TASK更新・計画doc等のcommit/push。¥0)。並行タスク: Opus条件Aレビュー(read-only)、委任_02(集計script、`er052_output/open233_prod_e2e_01/`・`docs/pm/RESULT_PACKET_AGG.md`のみ書込、git操作なし)。**本委任は委任_02のファイルを読まない・addしない。** 本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

**作業方式(必須)**: 追記は`Edit`/`Write`で小分け(1回30行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2〜3分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: 記録のみ。Status: 本管理ID=**APPROVED_FOR_PRODUCTION(ユーザー承認済み2点)・PRODUCTION_WIRED未**(実装・E2E・runtime evidence・SSOT確認後にFable/ユーザーが判定)。
- 禁止: コード・Prompt変更/有料API/`CURRENT_SPEC.md`の仕様本文変更(本委任では「承認済み・配線中」の注記のみ追記可。正式な仕様文の書き換えは実装完了後の委任で行う)/`docs/pm/PM_GOVERNANCE.md`編集/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_AGG.md`・`RESULT_PACKET_FLOOR.md`のadd。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当(計画docに対して別途実施中)。本委任は記録のみ。

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

## ユーザー指示(原文、逐語でDECISION_LOGへ記録する)

> 管理ID：OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01
> 目的: ユーザー承認済みの以下2点をProduction正式経路へ反映し、新仕様で20 run E2Eをやり直す。
> 1. 今回TrialでVALIDATEDになったChecker仕様を正式採用 - 「Ledgerに書いていない」だけでは候補にしない - Ledgerとの食い違い、具体的新事実の追加を候補とする - 主体・相手先/対象・範囲・限定条件も照合する
> 2. 後段の機械判定を縮小 - 数字に関する機械判定のみ残す - 主体・否定・比較・時期・因果など、それ以外の「AI判定を強制的に重大へ上書きする機械判定」は廃止する
> 両方ともユーザー承認済みのため APPROVED_FOR_PRODUCTION。ただし、E2E・runtime evidence・SSOT等まで確認するまでは PRODUCTION_WIRED としない。
> まず作業開始前に報告すること: 実装・必要test・最初の9 run E2E完了までに必要な時間の見込みを先に報告する。可能なら、実装/test/9 run E2E/集計・報告の大まかな時間内訳も示すこと。その報告後、ユーザーの追加回答を待たず作業を継続してよい。
> E2Eの進め方: 旧仕様で完了済みの9 runは、新仕様の正式Evidenceには使用しない。新仕様で20 runを最初からやり直す。今回はまず、新仕様 9/20 runまで実行 → 集計 → 報告で一旦区切る。残り11 runは、その9 run報告をユーザーが確認した後に進める。
> 9 run中のSTOPルール: 品質問題・重大Fact見逃し・Human Reviewが発生しても、そこでSTOPしない。9 runは最後まで走らせ、結果をまとめて報告すること。重要：問題を見つけても、その場で勝手に仕様変更・Prompt変更・追加対策を実装しない/問題を記録したまま、同じ条件で9 runを最後まで完走する/Human Reviewが発生しても同様に完走する。ただし、API障害・実行不能・データ破損など、物理的に9 runを継続できない技術障害だけは例外として報告する。
> 報告で必ず出す数値: A. Checker(AI判定: 候補にした件数/真に問題があった件数/不要に候補化した件数。機械判定: 同。AI＋機械の関係: AIのみ/機械のみ/両方重複/重複除外前の延べ/重複除外後のChecker総候補)。B. 後段判定(後段AI: 重大/軽微/問題なしの件数、事後評価: 真に重大/不要に重大判定/真に重大なのに軽微・問題なし。後段の機械判定[数字のみ]: 発火/AI判定との重複/真に重大/不要に重大化)。C. Rewrite(発生件数/発生run数/必要/不要/再修正要)。D. Human Review(目標0件、発生時は対象英文/Ledger Fact/Checker AI判定/Checker機械判定/後段AI判定/後段機械判定/Rewrite内容/Recheck結果/直接原因)。E. Safety・Cost(真の重大Fact見逃し/重大Fact検出/1 run費用/合計/平均/Rewrite関連・Checker関連・後段判定関連の費用分離)。
> Production Wiring確認: 初回Production経路だけでなく、Rewrite後Recheck/retry/fallback/regeneration/最終出口確認でも矛盾がないことを確認する。旧仕様の「数字以外の機械的強制重大化」が後段経路に残っていないことも確認する。必要なRegression/integration testを実施し、runtime evidenceを残す。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS等は実態に合わせて更新する。ただし、9/20 run時点では全E2E未完了なので、PRODUCTION_WIRED完了扱いにはしない。
> 9 run終了時: 9 runを最後まで完走したうえで報告する。その報告をもとに、Checker改善が実運用でも機能しているか/後段機械判定を数字だけにしたことでSafetyを損なっていないか/不要Rewriteが十分減ったか/Human Review 0を維持できているか/残り11 runへそのまま進めてよいか、をユーザーと総合レビューする。9 run終了後は残り11 runを勝手に開始せず、報告して待つこと。

## Fable判断(記録する内容、逐語)

「Fable判断(2026-10-06、委任_01スコーピング後、ユーザーへ時間見込み報告済み): (a)`precheck_floor`の数字以外4種(date/actor/negation/comparison marker)はユーザー指示『数字以外の強制重大化は廃止』に含まれると解釈しnumber_mismatchのみ残す。(b)`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`(AI重大判定の降格禁止)はAI判定を重大へ上書きする機構ではないため維持。(c)『Production初回経路』は従来どおりer052 runner(Production候補経路)、量産経路接続(SELF-RECOVERY-PRODUCTION-WIRING-01、配線STOP中)は含まない。(d)E2E停止は技術障害のみ。既承認の1 run上限¥20は暴走guardとして維持(超過runはabort記録して次runへ継続)。Human Review・品質問題・見逃しでは停止しない。(e)Checker新仕様の実装はVALIDATEDと同一処理(Stage 1候補の再分類post-filter)を初回・Recheck・出口の3経路へ配線、r3/r5 prompt不変。数字以外の`changed_*`フラグは生成維持・floor不使用、時期verifyはoff(コード休眠)。(f)9 run費用Guardrail `--budget-jpy 60`(見積low¥30/mid¥39/high¥50)。(g)時間見込み合計約4.5〜6.5時間(Opusレビュー30〜45/実装60〜90/test 40〜60/集計script 30〜40/9 run E2E 55〜75/集計・報告50〜70分)。(h)実装前にOpus条件Aレビュー(計画doc対象)を実施し、Fable照合後に実装へ進む。」

## KPI provenance欄

該当なし(記録のみ)。

## Opus台帳更新

該当なし(Opusレビュー結果は実装委任で記録)。

## 事前指定Read一覧

1. `docs/pm/ACTIVE_TASK.md`: 全文。
2. `docs/pm/plan_open233_checker_floor_production_e2e_01.md`: Grep `^## ` →見出し一覧のみ(存在確認)。
3. `docs/pm/RESULT_PACKET.md`: L1-L30(委任_01の要約、転記用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

(本節は委任文の手順記述。要点のみ逐語保存: DECISION_LOG.md=最新エントリ直後に本管理IDの新エントリを3回のEdit[見出し+Status/ユーザー指示原文/Fable判断全文+計画doc参照+時間・費用見込み]。OPEN_ITEMS.md=`OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01`行直後に新規1行[POST_USER_VALIDATION、Status=APPROVED_FOR_PRODUCTION(配線中・PRODUCTION_WIRED未)]+`OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02`行末・`OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01`行末[U1=数字のみ残し他は廃止、U2=線引きA1-PROD変更承認、Status→CLOSED]・`OPEN-233-A1-PROD`行末[旧線引きSUPERSEDED]へ追記。CURRENT_SPEC.md=最上位1箇所へ注記1行のみ[仕様本文不変]。docs/pm/REPORT_LEDGER.md=末尾1行。ACTIVE_TASK.md=固定ヘッダ上書き25行以内。RESULT_PACKET.md=冒頭に委任_03結果追記。)

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_03.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_03.md_check.json`
2. 上記Edit(小分け)。
3. `git status --porcelain`→明示add→commit→push。

## Git

明示add対象のみ: 計画doc、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log `_01.md`(+`_check.json`)・`_03.md`(+`_check.json`)。委任_02のファイル・`ACTIVE_TASK.md`・`RESULT_PACKET.md`はaddしない。
SSOT編集権: あり。push前に`git status --porcelain`で混入確認。

## 報告(RESULT_PACKET項目)

1. T-0結果。2. 追記したファイルと箇所。3. commit hash・push結果・raw URL。4. 一覧外Read理由。最終報告は10行以内。

