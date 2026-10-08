# 委任_04 全文保存(要旨を欠落なく保存)
管理ID: PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(委任_04: 完走E2E evidenceの追加取得+新規Open Item[予算ガードのweb_search未計上]記録)。並行タスクあり: FACTLOCK系3 agent(er052_output/factlock_writer_trial_01/配下、git・SSOT権なし)。本委任は触れない。
性質: Production配線のruntime evidence補完(Production code変更なし)。到達上限Status: APPROVED_FOR_PRODUCTION(配線完了・完走E2E evidence取得・Fable受入待ち)。PRODUCTION_WIRED宣言はしない(Fable判定)。
禁止: Production code編集。git add -A・破壊的git禁止。TTS実行禁止(本文生成まで)。FACTLOCK配下への書込禁止。
費用: 上限¥50(Guardrail、E2E 2本分)。到達・接近時は承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的/QCD上の便益が明らか、であれば超過を記録して継続。暴走疑い時のみSTOPし原因・既使用額・想定追加額・残作業を報告。
メモリ配慮: 実行前に空き物理メモリ確認(Get-CimInstance Win32_OperatingSystem FreePhysicalMemory)。4GB未満なら10分待って再確認(最大60分)。
STOP条件: 2本ともEN deviation STOP→3本目は実行せず報告(O3トリガー観測)。ModelContractViolation/単価未登録例外/5.6残存→即報告。
Opus独立技術レビューGate: 非該当(条件C済み)。時間見込み: 40〜60分。
固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTSなし、費用上限はGuardrail)。
ユーザー指示(原文): 「判断7(新規): 全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」(2026-10-08)。PRODUCTION_WIRED確定には完走1本のruntime evidence(standard/KP解説段含む全工程model_id実測)が必要。1本目(委任_03)はEN deviation Gateで正規STOP。
KPI provenance: E2E実測 fresh / production_formal_path。E2E自己確認: Yes(TTS段除く)。
Opus台帳: OF(M3)を完走evidence取得時にEVIDENCED→CLOSEOUT_CONFIRMED候補へ(確定はFable)。
事前指定Read: RESULT_PACKET.md、E2E_EVIDENCE.md、Family X runner入力候補(別テーマ優先、新規テーマ選定なし)、runner argparse部。
SSOT: OPEN_ITEMS新規 OPEN-242 BUDGET-GUARD-WEB-SEARCH-COST-GAP-01 [POST_USER_VALIDATION](compute_cost_jpy_so_farがweb_search課金を計上せず表示6.68円に対し実費19.48円。修正は別タスク)。OPEN-241行末に完走evidence結果+O3観測カウント追記。DECISION_LOG委任_04エントリ。REPORT_LEDGER更新。ACTIVE_TASK更新。
実行コマンド: 0.委任文保存+check_delegation_prompt。1.メモリ確認→E2E 1本(別テーマ、--stage all、--budget-jpy 20、TTSなし)。完走なら2本目不要。EN deviation STOPならもう1本。2.evidence er052_output/gpt6_wiring_e2e_01/run_02/(必要ならrun_03/)+E2E_EVIDENCE.md追記。3.SSOT反映→commit(明示add)→push。メッセージ: 「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_04: 完走E2E evidence[結果1行]、O3観測[EN STOP x/本]、OPEN-242起票、実費¥X/¥50」。
Git: 編集権 DECISION_LOG.md/OPEN_ITEMS.md/docs/pm/REPORT_LEDGER.md/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/ACTIVE_TASK.md。git add -A禁止。
報告: RESULT_PACKET.md上書き(1.完走有無+全stage model_id表+cost.json+予算ガード+所要秒 2.STOP内容+O3 3.OPEN-242 4.PRODUCTION_WIRED判定材料表a-e 5.問題・check結果・一覧外Read 6.raw URL)。推奨は書かない。
