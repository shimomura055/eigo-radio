## 管理ID

FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03(修正2回目: ユーザー追加決定の反映[N-2判断済み・Z-1 Trial承認・M2 Fallback承認+必須ユーザー報告]、Fallback通知経路の確認・実装、Coffee Standardの完走[KP再生成1回]、assemble経路、Checklist再照合、SSOT)。並行タスク: FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01(別sonnet-worker、`er073_*`/`er073_output/`、Family Z Trial、SSOT編集権なし、`er030_key_phrase_db_hybrid_m2_supply_01.py`は読み取り・importのみ)。本委任はSSOT編集権あり(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)。SSOT編集は最終工程、直前に`git status --porcelain`で他agentの未commit変更を確認(あれば60秒×5回待ち、残っていても自分の変更行のみ追記・自分の変更ファイルのみ明示add)。一時ファイル: `docs/pm/ACTIVE_TASK_XZW.md`/`docs/pm/RESULT_PACKET_XZW.md`(追記)。`.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。**全commitに`Managed-ID: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01` trailerを付ける**(委任_02で2件欠落。amendはしない)。

## 性質/到達上限Status/禁止事項

- 性質: Production実装(承認済み範囲)+Coffee Standard完走(Family X 音声化GO・記事再生成は必要に応じてGO)。
- 到達上限Status: Family X=`PRODUCTION_WIRED`(Checklist 1〜12全充足時のみ。未確認が1つでもあれば「配線済み・未完了」)。Family Z=「配線済み・runtime未確認」。
- 費用: 上限¥30(Guardrail。soft ¥20。内訳見込み: Std KP再生成1 job約¥1+KP音声Std約¥3+assemble/ASR数円)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**Std KP再生成は本委任で1 job(既存retry 2回込み)まで**。再度`CANONICALIZATION_INVALID`なら再実行せずSTOP(OPEN-310/346に記録、USER_DECISION_REQUIRED)。**Std Full Story part2は再生成しない**(ユーザー判断待ち: fallback take[N01でない]の人間承認か再生成か)。
- 禁止: 委任_02と同じ(未承認の仕様変更、Gate緩和、N01以外のPrompt、Family Zの記事再生成・音声化・KP再生成、Z側M2P0のProduction実装[Trialは別ID]、未承認ASR改善ロジック混入、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`、秘密値出力、wav/telemetry/logのadd、ACTIVE_TASK/RESULT_PACKETのcommit、Melos run_e2e_02配下・Master Store手動編集・HR Lock操作、外部プロセス再起動、監督ループ/timeoutラッパ、有料runのkill、Batch TTS)。**N-2(「true story」文言)をユーザー判断事項に戻さない**(判断済み)。
- STOP条件: 承認範囲超の仕様変更/Fallback通知が既存機構で実現できず新通知仕様が必要(→未実装と明示してSTOP)/Std KP再INVALID/予算暴走疑い/`STOP_NOTICE`/`STOP`/`STOP_ALL`。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`・Coffee run dir配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 条件A/Cレビュー済み(委任_01)。Fallback通知を既存パターン(run dir内notice file+summary)で実装する範囲なら再レビュー不要。新構造が必要ならSTOP。
- 時間見込み: 90〜120分。並列化: Z移行Trialと並列。本委任内はKP再生成→KP音声→assembleの順序依存で直列。
- T-2: `TTS_EXECUTION_MODE=STANDARD`明示。差分再生成(Std KPのみ)の可否・Master Store再利用・`--budget-jpy 30`明示・全再生成と判明したらAPI前STOP。

(以下、固定ブロック E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3、ユーザー指示原文[2026-10-13 追加決定§1〜§10]、Fable補足、KPI provenance、Opus台帳、事前指定Read/Grep一覧、作業内容A〜D、実行コマンド全文、SSOT追記文、Git、報告項目は、委任文本体に記載のとおり。本ファイルは委任文の管理ID〜T-2までを全文保存し、以降は下記に要点を保存する。)

## 固定ブロック要点
E-1同一ファイル再読しない/D-1 Grep→範囲Read/G-1 git出力最小化/F-1 transcript退避不要/T-0 委任文保存+check_delegation_prompt実行/T-2 STANDARD明示・差分再生成確認・budget明示/T-3 Cap=Guardrail。

## ユーザー指示(2026-10-13追加決定)要旨
§1 M2P0/N01はFamily X・Zで正式採用(APPROVED_FOR_PRODUCTION)、実装・test・runtime・SSOT・Git完了までPRODUCTION_WIREDと判定しない。§2 N01文言不変、"true story"は変更不要と判断済み(再度ユーザー判断に戻さない)、Std 6%減速・ASR再検証・既存Gate/retry/fallback維持。§3 Family X DB HybridにM2P0をProduction実装、Trial module非依存、P0不変、正式経路で発火runtime evidence。§4 Family ZのDB Hybrid+M2P0移行はTrial承認(Production実装は移行方式のユーザー採用判断後)。§5 M2構築失敗時はStrategy L Fallback許可、ただし検知・記録(family/記事/段階/理由/結果)、Fallback時は必ずユーザー報告、Fallback成功≠M2P0正常動作、Gate緩和禁止、通知は内部ログのみでは不十分でProductionでもユーザーが把握できることが受入条件、既存機構で不可なら未実装明示・新通知仕様が必要ならSTOP。§6 Family X: Production実装/N01/Regression/記事再生成必要に応じGO/音声化GO。Family Z: 記事再生成・音声化STOP、N01配線とTrialのみ。§7 連結発音・ASR改善は別ID、未承認ASR仕様を混ぜない。§8 Checklist 12項目(1正式初回経路 2retry/fallback整合 3Trial非依存 4test PASS 5正式経路runtime発火 6actual model_id等 7CURRENT_SPEC 8DECISION_LOG 9OPEN_ITEMS 10commit/push 11承認と挙動の一致 12Dangling Referenceなし)、未確認1つでもPRODUCTION_WIREDにしない。§9 STOP条件。§10 最終報告10項目。
Fable補足: Coffee Std KPの CANONICALIZATION_INVALID に対しKP job再生成を1回許可。Std part2(fallback take, M3 Gate BLOCK)は再生成せずユーザー判断事項。

## 作業内容要旨
A. Fallback通知: M2_SUPPLY_EXCEPTION等→Strategy L fallback時にrun summaryへm2_fallback記録、run dir直下にM2_FALLBACK_NOTICE.md、runner終了時stdout/最終レポートに明示、Fable報告義務はCURRENT_SPEC/OPEN_ITEMSに記録、Family Z(er063)にもsummaryキー契約をtest化(挙動不変)、mock testで3点固定、委任_02 CoffeeでのM2 fallback発生有無を確認。
B. Coffee Std完走: Std KP再生成1 job→KP音声→part2はfallback take掲載(再生成しない)→Adv assemble正式経路→Std assemble不可記録→試聴ページ+Playwright→速度ポーズ更新。
C. CHECKLIST_02.md。D. FINAL_REPORT_02.md+SSOT。
Git: 明示add、コミット3つ、先頭「FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03: …」、trailer必須、secret_scan、push。
