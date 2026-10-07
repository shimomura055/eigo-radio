# PM-CRASH-DATA-INTEGRITY-CHECK-02 結果(read-only調査、費用0円)

1. 結論: INTEGRITY_ISSUE_FOUND(軽微・Trial出力のみ)。Git本体・SSOT・重要ファイルは無傷。破損は未追跡のer052_output/open233_b3_trial_01配下(クラッシュ直前に書込み中だったTrial出力)に限定。
2. Git: fsck --full --no-dangling 出力なし(rc=0)。HEAD=418d9b61=origin/main(ls-remote一致)。未push commitなし。stashなし。.git内*.lockなし。HEAD/refs/heads/mainにNULなし(.git/indexのNULはバイナリ形式として正常)。reflog連続(15件、欠落なし)。
3. 作業ツリー: 変更550件(追跡変更12/未追跡538)。追跡変更12件は全て古いmtime(09-29〜10-07 14:43、最終commit前)で既存差分(er006/er011/er012/er021/er030/er052 budget_state)=クラッシュ起因でない。最終commit(14:58:50)以降に更新されたファイルは721件、全て er052_output/open233_b3_trial_01/ 配下(未追跡)=管理ID OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 段階2(Writer phase1->phase2、tools/driver_stage2.py、15:00-15:04)。docs/pm配下の未追跡md/jsonと root直下 .json は既存の過去タスク由来で今回更新なし。
4. 破損・部分書込み疑い(全て er052_output/open233_b3_trial_01/runs/ 配下、15:03:56-57書込み):
   - NUL埋め(全バイトNUL、NTFSクラッシュ時の典型): space_weapons/nb/V1/b2/w1/cost.json(203B)、meta/nb/V1/b3/w1/nb_provenance_phase2.json、meta/nb/V1/b3/w1/entry_point.json、hormuz/nb/V0/b2/w1/nb_provenance_phase2.json、hormuz/nb/V0/b2/w1/entry_point.json、space_weapons/nb/V3/b1/w1/b1b/audit/deviation_checks/advanced_attempt1.json(30312B)。
   - 末尾NUL混入jsonl: hormuz/nb/V0/b3/w1/raw_usage_log.jsonl(3行目)、space_weapons/nb/V3/b1/w1/raw_usage_log.jsonl(8行目)。
   - 0バイト: runs/ 配下37件(主に runs/_logs/*_phase1_a1.log・phase2_a1.log=起動直後のログ、hormuz/nb/V3/b2/w1/raw_usage_log.jsonl)。起動のみで未完了のrunを示す。
   - 補足: 上記以外の.json/.jsonlは全てparse OK。重要ファイル(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/HISTORY_INDEX/PM_GOVERNANCE/PM_BRIEF/ACTIVE_TASK/RESULT_PACKET/CLAUDE.md/.claude/agents/*.md)は全てNULなし・末尾切断なし。.venv python起動OK。
5. クラッシュ時刻: System log Kernel-Power 41 = 2026/10/07 15:04:14、EventLog 6008(予期せぬシャットダウン)= 15:04:24。前回は10/01 19:09:11(CHECK-01の件)。最終書込みは15:03:57付近。
6. 進行中作業: あり。根拠: (a)最終commit 14:58:50のあと15:00:25にdriver_stage2.py、15:00:46-15:03:57に721ファイル更新、(b)er052_output/open233_b3_trial_01/logs/driver_stage2.log末尾に OSError WinError 1455(ページングファイルが小さすぎる)=並列プロセス過多でメモリ枯渇、これがフリーズ原因の可能性大(推定)、(c)run_stage2_b3.sh(xargs -P 8)+driver_stage2(スレッド並列)の二重並列、(d)最新delegation(OPEN-238 WIRING-01 _03、14:58)は完了済みでcommit済み、RESULT_PACKET.mdは14:42のA2のままで古い(段階2の報告は未作成)。段階2は60 run計画のうちcost.jsonが取れたrunは20(解析可能分の累計約68.27円、記録上の全体予算との照合は未実施)、約40 runは未完了または未開始。V1 b1/b4、V2、V6等はcostなし。上記破損ファイルのrunは再実行対象。未コミットのTrial出力が残っておりcommit・push・ACTIVE_TASK更新は未実施。再開に必要: 段階2の再開(破損run/部分runの特定と同枠再実行、並列度を下げる、MAXRERUN=8の残り枠をdriver stateは持たないため再計算が必要)。Fable判断事項。なお Production変更は無し。
7. 残存プロセス: python* なし。
8. check_delegation_prompt.py: FAIL(必須セクション欠落: 管理ID/事前指定Read一覧/事前指定Grep一覧+手順/実行コマンド全文)。本委任は調査のみで、前例CHECK-01も同じFAIL。結果json: docs/pm/delegation_log/2026-10-07_PM-CRASH-DATA-INTEGRITY-CHECK-02_check.json
9. 推奨次アクション:
   Fable判断: (a)段階2再開可否・並列度(WinError 1455対策でP数削減、pagefile確認)、(b)破損8ファイル+0バイト37件のrunを再実行対象と扱うか、(c)driver_stage2のrerun枠(MAXRERUN)再設定、(d)予算(合計費用の再集計)確認、(e)RESULT_PACKET/ACTIVE_TASK更新。
   ユーザー判断: 段階2を再開する費用承認(予算上限内なら不要の可能性、管理IDの予算に従う)、PCメモリ/ページファイル設定の変更。
   修復候補(未実施): 破損json/jsonlの当該run単位の削除・再実行。
