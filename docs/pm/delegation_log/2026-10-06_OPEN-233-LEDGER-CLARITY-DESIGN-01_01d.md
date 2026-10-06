## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_01d: ACTIVE_TASK更新+SSOT先行起票(設計検討中・ユーザー判断待ち)。結果欄はプレースホルダ)。並列委任_01a/01b/01cが`docs/pm/ledger_clarity/`を作成中(触れない)。書込先: `docs/pm/ACTIVE_TASK.md`、`OPEN_ITEMS.md`(新規項目1行)、`DECISION_LOG.md`(同日エントリ新設)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§87骨子)、`docs/pm/RESULT_PACKET_LC_01D.md`、`docs/pm/delegation_log/`。CURRENT_SPECには触れない。git操作なし。
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: LEDGER-CLARITY-DESIGN-01=設計検討中(到達上限USER_DECISION_REQUIRED)。禁止: 結果の予測/Production変更/CURRENT_SPEC更新/S1等の採否変更/有料API/「決定」の創作。Opus Gate: 条件A必須(設計後に実施)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を本ファイルへ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、逐語要点)
> 管理ID OPEN-233-LEDGER-CLARITY-DESIGN-01。目的: WriterがFact台帳の意味を誤解することで重大な事実誤りを生む問題について、記事生成後の検査を複雑化するだけでなく、Fact台帳そのものを改善する上流対策を検討する。今回: 既存仕様・Production経路の確認/設計案作成/Opus独立レビュー/必要に応じた設計修正/Trial実施計画・費用・時間見積り。Trial実行・Production実装は禁止。Status: USER_DECISION_REQUIRED(Trial計画のユーザー承認待ち)を到達点。
> 基本方針: A. Factは明確に記述(何が起きたか/誰が何を/何がどう変化/どの時点/因果確認の有無)、複数解釈の表現を避ける。B. 複雑なFactは適切に分割(例① HC-012「機能を当面ロールバックした」→「人間コンシェルジュ機能を当面取り下げた」、原資料との意味一致を必ず確認。例② ホルムズ原油価格: 途中の上昇幅縮小と最終的な高水準を取り違えないよう必要なら2文に分割)。C. Writerに不要な推測をさせない(ただし表現・構成まで台帳で過度に拘束しない)。
> 必須条件: ①事実を追加・改変しない ②Fact同士の関係を維持 ③記事Qualityを維持 ④量産可能な自動処理(人間が毎回編集する運用は不採用、既存機構を優先活用)。
> Opusレビュー7観点: 1.Meta・ホルムズの問題を本当に予防できるか 2.同種の曖昧表現にも一般化できるか 3.誤った具体化・因果捏造を招かないか 4.分割による情報欠落・意味変化・後段への悪影響 5.記事Quality低下リスク 6.既存設計の活用・簡素化・費用削減の余地 7.従来のChecker改善と比べ効果・費用・保守性で合理的か。大きな設計変更や新Product仕様が必要な場合は選択肢として報告。
> Trial計画: 品質①Writer重大Fact誤認/②Checker精度(構成固定)/③記事Quality、各々測定方法・合格基準・件数・揺れ対策を事前定義、費用上限案・所要時間。
> PM Gate: 未承認の新仕様でありProduction採用扱いしない/Trialはユーザー承認後のみ/良好でも自動配線しない/残11 E2E停止継続/TRIAL-04も開始しない/S1等の採否を変更しない/CURRENT_SPEC正式部分を勝手に更新しない/Dangling Reference Check/DECISION_LOG・OPEN_ITEMSに設計検討中・ユーザー判断待ちとして正確に記録/Closeoutで未決事項・未配線の承認済み仕様を報告。最終報告は★ブロック8項目(結論/現行仕様との差/設計案Before-After/Opusレビュー/Trial計画/QCD/ユーザー判断事項/PM Gate確認)。

## Fable計画(記録用)
所要見込み約90〜100分(¥0)。Phase A(4本並列、約25分): 既存仕様調査/事例収集/Trial評価設計ドラフト/SSOT先行起票。B(約25分、直列): 設計案作成。C(約15分): Opus条件Aレビュー。D(約20分): 設計修正+Trial計画確定+Dangling+SSOT+commit→報告→STOP。

## 作業内容
1. `docs/pm/ACTIVE_TASK.md` 全面更新: LEDGER-CLARITY-DESIGN-01(進行中、Phase A)/S1-FACT-CHECK-01(USER_DECISION_REQUIRED、判断3点待ち)/TRIAL-03(REJECTED、次方針待ち)/CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・残11待機・PRODUCTION_WIRED未)。到達上限、禁止事項、Opus 7観点、9-8自己確認欄、UDR-blocking=残11 run・S1等採否・TRIAL-03次方針(いずれもユーザー待ち、本件で変更しない)、UDR-deferred=U2/U3/STAGE4、OPEN-235/236。
2. `OPEN_ITEMS.md`: Grep最大番号→新規「OPEN-237 Fact台帳の明確化(上流対策)設計: LEDGER-CLARITY-DESIGN-01、2026-10-06起票、Status=設計検討中(USER_DECISION_REQUIRED到達予定)、Trial未実行・Production未変更、関連OPEN-233」(既存書式、500文字以内)。
3. `DECISION_LOG.md`: 最後のエントリ直後に新エントリ「2026-10-06 OPEN-233-LEDGER-CLARITY-DESIGN-01」: (a)ユーザー指示(方針A〜C・必須条件①〜④・PM Gate)(b)Fable計画(c)設計・Opus・Trial計画・Status「(委任_04で追記)」。「設計検討中・ユーザー判断待ち。Production採用扱いではない」を明記。
4. REPORT: 末尾に「## §87 Fact台帳の明確化(上流対策)設計: OPEN-233-LEDGER-CLARITY-DESIGN-01(2026-10-06)」骨子: §87-1〜§87-8(8-1 目的・方針・必須条件/2 既存仕様/3 事例・Before-After/4 設計案/5 Opusレビュー/6 Trial計画/7 Status・判断(各「委任_04で追記」)/8 参照`docs/pm/ledger_clarity/`)。
5. `docs/pm/RESULT_PACKET_LC_01D.md`: 追記位置(行)、採番、プレースホルダ位置、T-0。

## 事前指定Read一覧
`docs/pm/ACTIVE_TASK.md` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
OPEN_ITEMS: Grep最大番号行→末尾にEdit。DECISION_LOG: Grep→最後のエントリ末尾→直後にEdit。REPORT: Grep `^## §8[0-9]`→末尾Edit。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01d.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01d.md_check.json`

## SSOT追記文
上記2〜4。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_LC_01D.md`。最終報告4行以内。
