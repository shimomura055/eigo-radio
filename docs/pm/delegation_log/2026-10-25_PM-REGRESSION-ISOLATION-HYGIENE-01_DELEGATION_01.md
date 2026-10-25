PM-REGRESSION-ISOLATION-HYGIENE-01 委任_01(HEADで失敗している隔離系test 8件のうち、DEV Trial scriptのimportに起因する5件の是正)+FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 Fable受入のSSOT反映。あなたはsonnet-worker。Fable(PM)からの委任。API 0。

## A. 回帰test隔離系の是正(Production挙動の変更なし)
背景: `docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/ACCEPTANCE_CHECK_01.md`(委任_05、clean worktree再現)で、HEAD内commit起因の失敗8件が確定。内訳と方針:
1. unittest er053 `test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2` / er095 `TestIsolation.test_not_imported_by_any_production_py_in_c1`: DEV Trial script `er115_fx_numeric_retention_trial_01.py`(FX-CORE-NUMERIC Trial、DEV専用)がer053をimport。
2. pytest er104 `test_AST_attempt_ctx_vote_flag_is_forwarded_from_strict_only`: `er103_ret_baseline_signature_01.py`が許可リスト外(commit 78a2c7c6e、ASR-QUALITY PN 委任_04)。
3. pytest er109 isolation `test_importers_of_scope_module_are_a_fixed_production_list` / `test_m3_scope_entry_call_sites_are_fixed_and_literal`: DEV Trial script `er113_fx_paragraph_chunk_trial_01.py`・`er114_fz_narration_chunk_trial_02.py`がscope moduleをimport・呼出。
4. pytest er109 golden ×3: 既知OPEN-501(帰属未特定)→**本委任では触らない**(現状記録のみ)。

方針(Fable決定): これらの隔離testは「Production moduleを想定外のファイルがimportしていないか」を検知する目的。DEV Trial script(`er113_*`/`er114_*`/`er115_*`、`docs/research`外のroot直下DEV runner)は意図的な再利用であり、Production到達経路ではない。是正は**testの許可リスト側**で行う: 各testに「DEV/Trial専用scriptの明示的allow-list」(ファイル名を列挙、`# DEV/Trial-only, not production-reachable` の注記と、該当scriptがProduction moduleから参照されていないことを同testで確認するassertを追加)を加える。er104のer103_ret_baselineは、当該commitの意図(ASR-QUALITY PN)を確認のうえ、Production経路の一部なら許可リストへ正式追加、DEV専用ならDEV allow-listへ。**Production module・Prompt・閾値は一切変更しない**。testの意図(検知力)を弱めない: 列挙は具体ファイル名のみ、globやワイルドカードで広げない。
- 実施: 該当test 5件を修正→当該testと関連test群を`py`(無料)で実行しPASS→全回帰(`run_project_regression.py`+pytest群)を実行し、残る失敗がer109 golden×3(OPEN-501)と既知fixture(`er003_test_bad`)のみであることを確認(他agentの未commit差分起因はclean worktreeで区別; `git worktree add`→`remove`、autocrlf注意=ACCEPTANCE_CHECK_01 §3参照)。
- 並行agent注意: Part 1配線(`er054_family_z_story_pool_trial_02_test_01.py`/`er053_cost_aggregate_01_test_01.py`等のrouting testを編集中の可能性)、中核数値配線(er019/er053/Writer系Production+test)。同一test fileに他者差分があれば一時index方式でcommit、編集前に`git status`確認。
- 新規OPEN登録: `PM-REGRESSION-ISOLATION-HYGIENE-01`として1件(11-8分類=修正へ進む→完了で解消、OPEN-501は別件のまま)。DECISION_LOG 1件(DEV script allow-list方針)。

## B. FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 Fable受入のSSOT反映(docsのみ)
Fable判定(2026-10-25): 案A配線=**PRODUCTION_WIRED**(Fable受入完了)。根拠: 初回経路配線(W1〜W6+CP規則)、retry/fallback/regeneration/resume整合(Seed必須化・REVISE置換・既存run dirのS-1受容)、正式runtime evidence(RUNTIME_EVIDENCE_02: 4段prompt sha一致・Narration行各段1・in third person 0)、旧固定指示はMelos専用経路のみ残置(原作三人称、記録済み)、自案件test 38 PASS、既存4作品Prompt byte一致16/16、公開Std/Adv本文・音声の正当性確認(ACCEPTANCE_CHECK_01)。留意: 全回帰のHEAD内失敗8件は他DEV script起因(本委任Aで是正中)+OPEN-501、Z writer起因0。
- OPEN-508: `WIRED_PENDING_FABLE`→`PRODUCTION_WIRED`(上記根拠を1〜2文で)。OPEN-503: 『告げ口心臓』run_sf_prod_02=`COMPLETE_USER_LISTENING_PENDING`のまま(Std平均文長WARNの位置づけ=Adv短文化による閾値低下でStdは旧版より平易、ACCEPTANCE_CHECK_01 §2参照、を1文追記)。UDR #193に「Fable受入PRODUCTION_WIRED 2026-10-25、最終試聴待ち」追記。DECISION_LOGに1件。
- 編集直前に再Read・scratchpadバックアップ・最小Edit・`git diff --stat`。

## C. 記録・Git
- `docs/pm/RESULT_PACKET_PMRIH1.md`、ACTIVE_TASK自行。委任文逐語保存: `--index 540`で`docs/pm/delegation_log/2026-10-25_PM-REGRESSION-ISOLATION-HYGIENE-01_DELEGATION_01.md`(冒頭「PM-REGRESSION-ISOLATION-HYGIENE-01 委任_01」で照合、不一致なら±6)。
- Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`(Production fileが含まれないこと)→`git commit --only`→`git push origin HEAD:main`。secret grep 0件。test修正とSSOTは別commit。

## 報告(Fableへ)
(1)test別の是正内容と、検知力を弱めていない根拠 (2)全回帰の結果(残失敗の一覧と帰属) (3)SSOT反映の差分要約 (4)commit・raw URL (5)RESULT_PACKET 4行+「判定整合」1行。