## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_01: 先行報告の誤り訂正をREPORT/DECISION_LOGへ反映、ユーザー決定[E2E 9/20停止・残11 run待機・本設計管理IDの起票]の逐語記録、ACTIVE_TASK更新、commit/push。¥0)。並行タスク: 委任_02(設計+¥0反実仮想。`docs/pm/design_open233_directional_misread_safety_01.md`・`er052_output/open233_directional_misread_offline_01/`・`docs/pm/RESULT_PACKET_DESIGN.md`のみ書込、git操作なし)。**本委任は委任_02のファイルを読まない・addしない。** 本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

**作業方式**: `Edit`/`Write`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを3分割して逐語保存。説明は最小限。時間目安15分。

## 性質/到達上限Status/禁止事項

- 性質: 記録のみ。本管理IDのStatus: 設計段階(到達上限 DESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED)。OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 9/20 run完了で一旦停止(ユーザー決定)、PRODUCTION_WIRED未。
- 禁止: コード・prompt変更/有料API/残11 run/`CURRENT_SPEC.md`の仕様本文変更(注記のみ可)/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET*.md`のadd。
- Opus Gate: 非該当(記録のみ。設計のOpus条件Aレビューは委任_02の成果物に対して別途)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は`--porcelain`/`--short`で最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、逐語記録)

> 管理ID：OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01
> 目的: E2Eは 9/20で一旦停止する。残り11 runは実行しない。今回発見した重大見逃しについて、全体を一律に厳しくするのではなく、AIが特定種類の意味関係を系統的に読み違えるケースだけを狙って補強するSafety設計を行う。Production変更・有料E2Eはまだ行わない。
> 今回事実として確認できたこと: 対象例「The company also restored the human concierge feature to the way it had been before, at least for now.」Ledgerでは、対象機能・テストを当面rollbackした＝撤回した。記事では「human concierge featureを以前の状態へrestoreした」と読め、撤回→復元という方向反転が起きている。重要: Checkerの決定論検査は negation_polarity_mismatch として正しく候補化した/Stage 1 AIはSUPPORTEDと誤読/後段AIもACCEPTABLE/第2意見もACCEPTABLE/旧floorを全部ONにしても、changed_* flagが全falseだったため防げなかった/したがって、今回の見逃しは「数字以外floorを廃止したこと」が直接原因ではない/同型は過去gold A5-0等でも既知。この訂正を既存REPORT / Decision Log等へ反映すること。
> 今回やらないこと: 残り11 E2E/Production変更/全機械floor復活/一律にCheckerを厳格化/goldの変更/KPI変更/Human Reviewへの安易な振替、は禁止。
> Status: 今回到達してよいのは DESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED まで。まだVALIDATEDにもPRODUCTION_WIREDにも進めない。
> E2E残11 runは、ユーザーが再開を明示するまで待機。
> (設計課題1〜5・設計仮説・¥0検証・Opusレビュー観点・報告内容は委任_02の委任文に逐語収録。本委任では上記要点を記録。)

## Fable訂正(逐語で記録)

「Fable訂正(2026-10-06): 9/20 run報告(REPORT §81、DECISION_LOG同日エントリ)で『HC-012見逃しは旧仕様なら否定floorが強制BLOCKINGにした可能性がある型/数字のみ縮小の代償として現れた最初の実例』と記述したが、run出力(`er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` L331-L400)の実測で訂正する。当該claimのStage 1フラグは`changed_number/actor/negation/comparison/time/causality`すべてfalse、候補化は決定論検査`negation_polarity_mismatch`(routes=r3、Stage 1 AIはSUPPORTED判定)による。旧floorは`changed_*`フラグtrueでのみ発火するため、旧仕様全ONでも`floor_reason=None`=発火しない(`floor_cited_materiality`もACCEPTABLE)。したがって見逃しの直接原因は『数字以外floorの廃止』ではなく、Stage 1 AI・Stage 2・S1の3段階が同じ読み(restored…to the way it had been before=ロールバックと同義)をしたこと(系統的な読み癖+同rubric再サンプルの相関)と、決定論検査の信号を後段AIが消す構造。同型は正式gold A5-0(HC-012)として既知。」

## 事前指定Read一覧

1. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## §81|§81-` →§81の見出し一覧と、Grep `否定floor|数字のみ縮小の代償|旧仕様なら` →訂正対象の記述箇所(±3行)。
2. `DECISION_LOG.md`: Grep `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` →最新エントリ末尾(e)の該当記述(Grep `否定floor|代償`)。
3. `docs/pm/ACTIVE_TASK.md`: 全文。
4. `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01|OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01` →行頭・末尾のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- REPORT §81: 訂正対象の記述の直後に「訂正(2026-10-06、委任_01 of DIRECTIONAL-MISREAD): …」として上記Fable訂正を併記(旧記述は消さない)。§81末尾に「§81-10 ユーザー決定: E2E 9/20で一旦停止、残11 runは明示再開まで待機、見逃し対策はOPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01で設計(Production変更・有料E2Eなし)」を追記。
- DECISION_LOG: (1)CHECKER-FLOOR-PRODUCTION-E2E-01エントリ末尾に「(f) Fable訂正」全文+「(g) ユーザー決定2026-10-06: 9/20停止・残11 run待機」。(2)末尾に新エントリ `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`(ユーザー指示要点逐語[上記]、Status=設計段階、到達上限、禁止事項、Fable訂正参照、委任_02[設計]・Opus条件Aレビュー予定)。
- OPEN_ITEMS: (1)CHECKER-FLOOR-PRODUCTION-E2E-01行末尾へ「2026-10-06 ユーザー決定: 9/20で一旦停止、残11 run待機、HC-012見逃し原因のFable訂正(floor廃止は直接原因でない)→REPORT §81訂正」。(2)新規行 `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`(POST_USER_VALIDATION、Status=IN_PROGRESS[設計段階、到達上限DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIRED]、要約: 方向反転等の系統的読み違いを狙い撃つSafety設計、決定論検査=センサー→専用独立確認の仮説評価+代替案、¥0反実仮想、Opus条件Aレビュー必須、禁止事項列挙)。CHECKER-FLOOR-PRODUCTION-E2E-01行の直後に挿入。
- `CURRENT_SPEC.md`: 既存注記(L2372付近)に「E2Eは9/20で一旦停止(2026-10-06ユーザー決定)、PRODUCTION_WIRED未。見逃し対策設計=OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01」を追記のみ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID: DIRECTIONAL-MISREAD-SAFETY-DESIGN-01[設計中、委任_02並行]/CHECKER-FLOOR-PRODUCTION-E2E-01[9/20停止、残11 run待機、PRODUCTION_WIRED未]。UDR-blocking: 残11 run再開はユーザー明示待ち。UDR-deferred: U2ラベル確認(重大4+UNDECIDABLE 1)、U3除外84件確認、STAGE4ラベル(低)。STOP条件: 設計のSTOP=新Safety原則・gold変更・有料Trial・Production変更が必要な場合。次アクション: 委任_02完了→Opus条件A→報告)。
- `docs/pm/RESULT_PACKET.md`: 冒頭に委任_01結果を追記。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_01.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_01.md_check.json`
2. 上記Edit。
3. `git status --porcelain`→明示add→commit→push(index.lock競合時は5秒待って最大3回再試行)。

## SSOT追記文

上記のとおり。

## Git

明示add対象のみ: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_01.md`(+`_check.json`)。委任_02のファイル・`ACTIVE_TASK.md`・`RESULT_PACKET*.md`はaddしない。
コミットメッセージ: `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01: HC-012見逃し原因のFable訂正(旧floor全ONでも不発火=changed_*全false、直接原因はAI3段階の同一誤読+決定論信号の喪失)をREPORT §81/DECISION_LOGへ反映、ユーザー決定(E2E 9/20停止・残11 run待機・系統的読み違い専用Safety設計の起票)を逐語記録(委任_01、¥0)`
SSOT編集権: あり。

## 報告(RESULT_PACKET項目)

1. T-0結果。2. 訂正・追記箇所(ファイル・行)。3. commit hash・push結果・raw URL。4. 一覧外Read理由。最終報告は8行以内。

