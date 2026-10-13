## 管理ID

ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_02(修正1回目: Opus条件Aレビューの必須修正1〜4・推奨の反映、音素基準でのread-only再評価、SSOT更新。¥0、Production無変更)。並行タスク: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_01(`er071_*`、SSOT編集権なし)が稼働中。本委任はSSOT編集権あり(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`は編集しない)。SSOT編集直前に`git status --porcelain`で他agentの未commit変更を確認し、あれば60秒×5回待ち、残っていても自分の変更行のみ追記・自分の変更ファイルのみ明示add。一時ファイル: `docs/pm/ACTIVE_TASK_ASRGEN.md`/`docs/pm/RESULT_PACKET_ASRGEN.md`(委任_01に追記)。`.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項

- 性質: 設計草案の改訂(DESIGN_DRAFT_02)+Trial隔離プロトタイプの改訂と既存データでの再評価(OFFLINE_EVAL_02)+SSOT。Production code・Validator・Gateは変更しない。
- 到達上限Status: 設計=`DESIGN_REVISED(Opus必須修正反映済み)`、検証=`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。Production採用宣言禁止。
- 費用: 上限¥0(有料API禁止)。
- 禁止: 委任_01と同じ(Production経路ファイル編集、`er065_*`既存test編集、共有telemetry/attempt_history/Master Store/HR/run_e2e配下への書込、Melos専用hardcode、CURRENT_SPECへの仕様記載、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`、秘密値出力、wav/log/telemetryのadd、ACTIVE_TASK/RESULT_PACKETのcommit、外部プロセス再起動、監督ループ/timeoutラッパ)。**既存回帰のうち共有ファイルへ追記するtest(`er026_post_slowdown_cascade_rescue_01_test_01.py`、`run_project_regression --pattern er011*`)は本委任では実行しない**(委任_01で副作用が確認済み。必要なら`append_telemetry_log`をstub化したrunner経由のみ)。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 条件Aレビュー済み(本委任は反映)。内容が変われば再レビューはFableが判断。
- 時間見込み: 60〜80分。並列化: 他agentと並列。本委任内は直列(設計改訂→再評価→SSOT)。

(以降、固定ブロック・ユーザー指示・Opusレビュー結果・事前指定Read/Grep・作業内容A〜D・実行コマンド・Git・報告項目は委任文本文のとおり。本ファイルは受領本文の保存であり、長大な後半部は委任文原文を参照: 必須1=綴りから音素へ/必須2=受理理由をEXACT・NORMALIZED_MATCH・Pattern A/B/Cに限定(HIGH_SIMILARITY_SAFE 8件・NUMERIC 3件除外)/必須3=M1はPrimary#1判定直後・Tier3前、fallbackはSecondary同意またはHR、P2/S1/S2にも/必須4=V2は暫定保守ゲート、末尾欠損は別OPEN-341/推奨=所有格正規化・PASS_WITH_WARNING+audit trail・対象限定・flag依存・OPEN-308範囲外/Q5 F1は別OPEN-340/Q6 R1>F1>M1/Q7 Eq Layer非統合、ユーザー判断候補4件。作業A=DESIGN_DRAFT_02.md、B=offline.py改訂+OFFLINE_EVAL_02.md(既存word_phones再利用、pip install禁止)、C=SSOT(OPEN-339更新/340〜342新規/OPEN-318/328追記、DECISION_LOG、OPUS台帳、UDR#41、REPORT_LEDGER)、D=FINAL_SUMMARY_01.md(10項目)。Git: コミット2つ、trailer Managed-ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01、push。)
