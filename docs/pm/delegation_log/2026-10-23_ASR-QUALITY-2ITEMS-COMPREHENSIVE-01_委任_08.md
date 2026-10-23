FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_08-OPEN-WINDOW-CLEAR-STOP-GATE-ASSEMBLE-PAGES-20261023

# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_08: 『開いた窓』run_sf_prod_01 の RESTART_STORM STOPをFable権限で解除→provision_shell,gate,assemble,pages,page_verify を1起動で実行(API 0見込み)→試聴ページ差替え→SSOT(①②Z判定材料、事故記録)→Git→最終報告(A/B/C/D)。費用上限3円(Gateで再生成が必要になった場合は実行せずFableへ)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、ASR行、FAMILY-Z-SOURCE-FIDELITY行)、`.claude/agents/sonnet-worker.md`(有料run・停止・再起動節)、`docs/pm/PM_GOVERNANCE.md` 26節のSTOPセンチネル項(行3480〜3500付近: 解除はFable/ユーザーのみ、RESTART_STORMは`--clear-stop --reason`必須、違反は事故記録)、`docs/pm/RESULT_PACKET_ASRQ_B7.md`、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_03.md`、`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_07.md`(制約継承)、ユーザー原文 `..._USER_02.md` §3(完成要件: 正式Gate通過、Std/Adv組立、試聴ページ更新、全体再生・個別再生・スクリプト整合、完成版URLと品質検査結果)。

## 1. Fable判断・権限行使
- RESTART_STORM(`run_sf_prod_01/STOP`+`RESTART_STORM_LOCK.json`)は、委任_07の実行層がc14再生成後にAPI 0段(gate→provision_shell未実行でrc=2→provision_shell追加で再起動)を5分内に3起動したことが原因。外部停止・品質問題・費用暴走ではない。**Fableは解除を承認する**: `--clear-stop --reason "RESTART_STORM: operator relaunched non-paid stages (gate without provision_shell) 3x/5min after c14 regen; no quality/cost issue; released by Fable 2026-10-23 per PM_GOVERNANCE 26 (委任_08)"`。`audit_stop_sentinel.jsonl`への記録を確認。
- 事故記録: 委任_07の再起動は許可回数(1回)を超えた運用違反として、OPEN新規(軽微・運用)+DECISION_LOG 1行で記録(原因=段指定の誤り[provision_shell欠落]、影響=なし[API 0段、出力更新なし確認]、再発防止=Z完成段は`provision_shell,gate,assemble,pages,page_verify`を1起動で指定する旨をsonnet-worker.mdの該当節末尾に1行追記)。影響範囲はread-onlyで確認(出力更新時刻・lock)。

## 2. 作業
### T-0 記録(API 0)
委任文逐語保存(抽出tool、MARKER先頭一致、`..._委任_08.md`)。ACTIVE_TASK ASR行=委任_08 Status=`OPEN_WINDOW_FINALIZE_IN_PROGRESS`、報告=`docs/pm/RESULT_PACKET_ASRQ_B8.md`。当日累計確認(上限1,400円、現在約825円、他予約枠: Family Y 残334.25円、KP 30円)。
### T-1 解除→完成段(1起動)
1. 保全: run_sf_prod_01の現状(全clip OK状態)を `_preserve_20261023_b8/` へ(git未追跡)。
2. `--clear-stop --reason "..."`(上記文言)で解除→`--stages provision_shell,gate,assemble,pages,page_verify` を**1起動**で実行。rc≠0でも再起動しない(原因を記録してFableへ)。
3. 正式Gate(speed v2含む)の結果、Std/Adv全編組立、試聴ページ `user_test/family_z_open_window_01/` 差替え(旧版はバックアップ済み)。page_verify PASS、全体再生・個別再生・スクリプト整合を確認。ページ内または報告に最終試聴の確認点3つ(c12 `speciality`[Adv]の英式/米式の読み、c2 Bertie、c14 Bertie[Std/Adv])を明記。
4. 結果→`PHASE4_RESULT_04.md`(Gate結果表、組立物path/長さ、ページURL、page_verify結果)。
### T-2 SSOT・Git
- OPEN-465(『開いた窓』完成版提出・ユーザー試聴待ち)、OPEN-479(修正・実run結果・CLOSED候補[Fable確認後])、OPEN-471/472(Z evidence: ②=正式CLI実run c12発火、①=narrator実runで表構築+隔離case A ENTITY_ONLY_ACCEPT+会話経路の役割解決[case B]・実runはTier3先行受理でPNAP未到達、という事実を整理。「Fable最終判定待ち」表記)、新規OPEN(運用事故)、UDR #157更新(完成版試聴待ち・確認点3つ)。DECISION_LOG(STOP解除・事故)。REPORT_LEDGER。
- Git: secret scan(`Glob **/secret_scan*`、無ければcached差分のkey/tokenパターンGrep 0件)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。wav/raw_usage_log/STOP関連ファイル追跡禁止。raw URL添付(試聴ページindex、PHASE4_RESULT_04、OPEN_ITEMS)。
### T-3 最終報告 `docs/pm/RESULT_PACKET_ASRQ_B8.md`
(A)①②: X/Z別の実装・test・回帰・runtime evidence要約(委任_04〜07の結果を1表に)、残リスク(①会話経路でのPNAP受理寄与は未観測、②pron_differs対の読み、CLI入口での①自然発火は次回X記事で追認)。(B)『開いた窓』: 修正音声の検証結果(Bertie c2/c14、c12 speciality)、Std/Adv完成状況、最終試聴URL、ユーザー確認点。(C)費用(本委任+B工程累計[委任_05 10.6円+委任_06 0円+委任_07 5.8円+本委任]、出典)、時間。(D)Closeout(手段/目的の区別、撤去・残置、事故記録)。使用model名。

## 3. 禁止・制約
委任_05〜07の禁止事項を継承(`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止、PIDは自分のもののみ、Gate/HR Lock迂回禁止、Ledger手動登録禁止、`TTS_EXECUTION_MODE=STANDARD`、秘密情報出力禁止)。Production code変更0(sonnet-worker.mdの運用注記1行のみ可)。**再起動禁止**(1起動のみ)。Gateで再生成が必要なclipが出た場合は実行せずFableへhandback。
## 4. handback
完了/rc≠0/Gate不通過/blocker のいずれかで。