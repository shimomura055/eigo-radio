Fableからの委任_08(FAMILY-Z-IN-A-GROVE-PRODUCTION-01: run Cap引上げ(Fable判断)→tts_a2→完成段→候補公開→SSOT)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_委任_08.md` に逐語保存してから開始。前提=`docs/pm/RESULT_PACKET_FZIG7.md`、`docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/RUNTIME_EVIDENCE_01.md`、委任_07文(`…_委任_07.md`。§2〜§5の手順・範囲は本委任でも有効)。

## Fable判断(費用)
BUDGET_PLAN_01.md:32のとおり上限70円はユーザー承認値ではなくFable委任文の起動例に由来する計画上限。本作は台詞中心でpro TTS呼出が多く、Adv実績¥20.19からStd同規模(¥17〜21)を見込むと累計約¥77〜81。案件合計は300円以下・当日1,000円内・承認済みScope内のため、**run Capを¥90へ引上げ**(PM_GOVERNANCE 7-7の自律範囲。ユーザー承認事項ではない)。`BUDGET_PLAN_01.md`末尾に「2026-10-29 Fable判断: Cap 70→90円(理由・根拠7-7・実績)」を追記。起動は `--approved-budget-jpy 90`(既存run_dirでの引上げ方法は`_run.sh`/runnerのhelpで確認。再計上・二重計上に注意)。累計¥90超過見込みなら停止して報告。量産単価70円目標との乖離は報告事項として記録(台詞中心作品のTTS pro呼出=原価低減の検討対象、新仕様候補であり本作では実施しない)。

## 手順
1. `tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --out docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/stop_check_08.json`(rc=3で停止。各有料起動前に再実行)。
2. **並行Worker(I)との競合回避**: `git status --porcelain -- er007_ja_secondary_asr_01.py er078_*.py er078_ja_v2beta_01.py er109_xz_scope_01.py er063_family_z_audio_01.py er026_family_z_fiction_production_runner_01.py er121_family_y_runner_01.py` に未commit差分がある間はtts_a2を起動しない。2分間隔で最大60分待つ(待機中にBUDGET_PLAN追記・SOURCE_FIDELITYのStd TTS入力確認準備等の無料作業)。60分経っても残る場合は未実施のまま報告。差分なしなら`git log -1`のHEADを記録して起動(HEADにJA-ASR v2+β配線が含まれていればその旨と`judge_rule_version`等の記録有無をRUNTIME_EVIDENCEに書く)。
3. `--stages tts_a2`(1起動)。rc・費用・ASR判定(PASS/PASS_W/HR、PASS_Wは対象音声・理由・警告を列挙)・速度Gate・LR発火・Voice送信パラメータを記録。HR Lockで止まったら内容を記録して停止(迂回禁止)。
4. 起動間隔≥150秒で `--stages provision_shell,gate,assemble,pages,page_verify`(1起動)。
5. 候補公開: 正式経路どおり `user_test/family_z_in_a_grove_01/`(pages出力の正規先を確認)→push→live検証(index+全mp3 HTTP 200・Content-Length>0・byte一致)+page_verify local(全音声再生・console error 0・4xx 0)。ページ冒頭の状態文言はZ標準生成に無いため追加しない(前例どおり)。
6. SOURCE_FIDELITY_CHECK_01.mdにStd実TTS入力での確認を追記(7証言順序・3矛盾証言・結末・評決なし・非グラフィック化)。RUNTIME_EVIDENCE_01.mdに委任_08分を追記(費用: stage別・累計/Cap90)。
7. SSOT: `OPEN_ITEMS.md`新規OPEN(FAMILY-Z-IN-A-GROVE-PRODUCTION-01、Status=COMPLETE_USER_LISTENING_PENDING、URL・sha・費用累計・Cap引上げの記録)、`DECISION_LOG.md` 1件、`docs/pm/USER_DECISION_REGISTER_01.md`新規UDR(記事単位の試聴PASS/公開承認待ち、分類D)、ACTIVE_TASK(H)行(Re-Read)。commit(編集ファイル明示`git add`、run出力はgitignore規則)→`git push origin HEAD:main`(FF)。
8. `docs/pm/RESULT_PACKET_FZIG8.md`: 整合/未承認機能/成果物(URL・sha)と目的適合(成功・失敗経路)/撤去・残置/判断候補(停止根拠file:line)/費用(stage別・累計/Cap)/commit。`判定整合:`行。最終回答は短く(URL・stage rc・ASR/HR/PASS_W・費用累計・commit・判断候補)。

## 範囲(11-8)
範囲内=承認済みZ仕様での再開・組立・候補公開・記録・Fable承認済みCap引上げ。範囲外=本文/Seed/Prompt変更、新Voice、Gate緩和、HR Lock迂回、er063等のコード変更、正式公開承認(試聴PASSはユーザー)、Family A/B/C。
