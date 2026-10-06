## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_03e: 設計・Opusレビュー・Trial計画・Fable判定のSSOT反映)。並列委任_03a(設計doc修正・Trial計画)、_03b〜d(Opus逐語)が同時進行(`docs/pm/ledger_clarity/`・`opus_l2_review_lc_*`には触れない)。書込先: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§87-2〜7)、`DECISION_LOG.md`((c))、`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-059)、`OPEN_ITEMS.md`(OPEN-237進捗)、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET_LC_03E.md`、`docs/pm/delegation_log/`。CURRENT_SPEC不変。git操作なし。
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: LEDGER-CLARITY-DESIGN-01=USER_DECISION_REQUIRED(Trial計画承認待ち。設計検討中・Production採用扱いではない)。禁止: Trial実行/Production実装/CURRENT_SPEC更新/S1等採否変更/有料API/「決定」の創作。Opus Gate: 条件A実施済み(記録)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を本ファイルへ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外(本管理ID¥0)。

## ユーザー指示(原文、要点)
> DECISION_LOG・OPEN_ITEMSには設計検討中・ユーザー判断待ちとして正確に記録する。Closeoutで未決事項・未配線の承認済み仕様を報告する。今回の設計は未承認の新仕様でありProduction採用扱いしない。

## 記録する事実
E1 既存仕様(委任_01a【確認】): 台帳=Researcher(gpt-5.6-luna、web_search)→独立AI Verification(VERIFIED/AMBIGUOUS/REJECTED)→決定論`build_verified_ledger_text`でtxt化(`er003_v1_en_direct_vfl_01_generate.py` L275)。原資料=Web検索結果、source quote欄なし。台帳生成費≈¥28.7/run(総額¥44.66の64%)。既存ルール=Researcher promptに4観点(scope/適用条件/数値内訳/因果区別)、時系列・主体・多義語ルールなし。fail-safe位置=Verification直後〜txt化。ID参照=HC-012だけで23ファイル65箇所。
E2 事例(委任_01b【確認】): HC-012「機能を当面ロールバックした」=テスト中機能の取り下げ(原文照合未了)。HF-009=途中「上げ幅縮小」+最終「高水準へ戻る」。曖昧度高3(HC-012/HF-009/HF-012)・中14・低10。held-out候補8。台帳3種(meta 15/hormuz 12/small_bag 17)。
E3 設計(委任_02、Opus反映後=委任_03a): 比較=案P'(Researcherスキーマ・prompt拡張+Verification観点追加、追加callなし、<¥1)/案C+V(Verification後に台帳全体1回の明確化call+意味一致検証、ID不変・events構造・2段fail-safe、+¥2)/案C+V+B(多義語factにWeb再Verification+¥14)/案S(子ID分割、不採用)。Opus反映後の推奨=本番はP'、案Cは既存台帳のoffline適用(Trial用)。必須の決定論検査(fact_id集合・数値・日付・固有名・否定語・因果語の集合一致)、txt書式制約(claim行に否定語・因果語・番号・括弧を入れない、否定ガイドはnotes_for_writerへ、phaseは英字タグ行)、phase定義は台帳側に一本化。
E4 Opus条件Aレビュー: 総合=条件付きで進める(M1〜M6)。主要指摘: HF-009の「Writer誤読例」は合成文で本番Writerは正しかった(HF-009はChecker側課題)/HC-012はJA R0で発生、WriterはB3 briefを読む(台帳を直接読まない)/Vは多義語の確定正誤を原理上判定できない→原資料参照工程(P')で確定/明確化文の否定語・因果語・番号が既存Checker決定論検査を誤爆させる/Quality: 括弧・番号の逐語コピー経路/Checker改善とは両立(台帳=予防、Checker=検出)、台帳eventsをCheckerの基準に凍結共有すればChecker側Ledger抽出を廃止可。
E5 Trial計画案(委任_03a、承認待ち): Phase 0 ¥0(基準発生率集計)/Phase 1 ¥3〜6(3台帳へ案C offline適用+決定論diff+offline照合)/Phase 2 上限¥60(B3+JA R0〜R2+ENのみ、台帳A/B×3テーマ×8 seed、HC-012型曖昧訳 A≥6/8 vs B≤1/8、held-out悪化なし、Quality基準)/Phase 3 任意上限¥30(承認済みChecker構成でA/B各2 run)。合計上限¥100。過学習防止(固有名をpromptに入れない、基準・held-out事前固定)。要DEV経路(台帳パス差替え、Production既定は従来)。
E6 Fable判定: USER_DECISION_REQUIRED。Opus判定はSonnet案の訂正・精緻化で対立ではない。新Product仕様候補(台帳スキーマ拡張・Writer向け出力形式・本番経路P' vs C+V・検証強度)は選択肢として提示、採用はユーザー判断。費用¥0。
E7 PM Gate: Production未変更/Trial未実行/残11 E2E停止/TRIAL-04未開始/S1等採否不変(S1-FACT-CHECK-01はUSER_DECISION_REQUIREDのまま)/CURRENT_SPEC未更新/Dangling Reference(委任_03aで確認)。未配線の承認済み仕様=CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・PRODUCTION_WIRED未)。Open Items=OPEN-235/236/237。

## 作業内容
1. REPORT: Grep `§87-2|§87-3|§87-4|§87-5|§87-6|§87-7|委任_04で追記` →各プレースホルダをE1/E2/E3/E4/E5/E6+E7で置換(各8行以内)。
2. DECISION_LOG: Grep `OPEN-233-LEDGER-CLARITY-DESIGN-01` →(c)をE3〜E7要点で置換(「決定したのはFableのStatus判定のみ。設計・Trial計画はユーザー承認待ち」明記)。
3. OPUS_FINDINGS_LEDGER: Grep `OF-058` →直後にOF-059(E4要点、採否=Fable照合: 整合・反映、USER_DECISION_REQUIRED)。
4. OPEN_ITEMS: Grep `OPEN-237` →進捗へ「設計完了・Opus条件A済み(M1〜M6反映)、本番推奨P'/Trial用C、Trial計画(上限¥100・4 Phase)承認待ち=USER_DECISION_REQUIRED」を短く追記。
5. ACTIVE_TASK 全面更新: LEDGER-CLARITY=USER_DECISION_REQUIRED(判断事項: Trial実施可否・予算¥100・本番経路P'/C+V・2段Trial・F1方針)、S1-FACT-CHECK=USER_DECISION_REQUIRED、TRIAL-03=REJECTED次方針待ち、E2E-01=停止、9-8自己確認欄。
6. `docs/pm/RESULT_PACKET_LC_03E.md`: 追記位置、T-0。

## 事前指定Read一覧
`docs/pm/ACTIVE_TASK.md` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記1〜4のGrep→該当範囲Read(各30行以内)→Edit。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_03e.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_03e.md_check.json`

## SSOT追記文
上記1〜4。

## Git
なし(委任_04でcommit)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_LC_03E.md`。最終報告4行以内。
