Fableからの委任_07(FAMILY-Z-IN-A-GROVE-PRODUCTION-01: ユーザーKP/文法選定の確定→kp再開→TTS→完成候補ページ→SSOT。費用: run累計Cap¥70、現在約¥38.6、残り約¥31。超過見込みで停止)。

## 0. 最初に
(a) `docs/pm/delegation_log/2026-10-29_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_USER_02.md` を作成し、1行目 `# ユーザー選定原文(逐語、2026-10-29受領。選定フォームV3のreadable出力)` の後に`<<<USER>>>`〜`<<<END>>>`間を一字一句そのまま保存(heredoc失敗時はpy)。
(b) 本プロンプト全文を `docs/pm/delegation_log/2026-10-29_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_委任_07.md` に逐語保存。
(c) `tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --out docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/stop_check_07.json`(rc=3で停止。有料stage起動前にも再実行)。
(d) 経緯=`docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/RESUME_06.md`、`docs/pm/RESULT_PACKET_FZIG6.md`(残っていれば)、`_run.sh`/`_run5.sh`(起動コマンドの正本)。ユーザー原文(制作指示)=`docs/pm/delegation_log/2026-10-28_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_USER.md`。

## 1. 選定の確定(API 0)
- er119 CLI `confirm --from-readable`(または同等の正式手順。`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/`のDATA_CONTRACT/CLI docを確認)で、Std(a2)とAdv(b1b)の選定を確定。**照合コード**(`AIF1-in_a_grove__a2__prod-…-f48b5251-8ec5e76f-…`/`…b1b__prod-…-941647eb-ee543393-…`)が現行候補sha(Std candidates f48b5251…・本文8ec5e76f…)とフォームdata JSONに一致することを検証し、不一致なら停止して報告。
- Std: KP=on silent feet/constable/drown、追加解説=なし、本文意味表示=through a medium/sink into the darkness/dagger/bandit、文法=選定なし。Adv: KP=cold contempt/on soft feet/medium、追加解説=sink for ever/constable、本文意味表示=The thicket fell silent/trampled/veiled/seize、文法=選定なし。確定ファイル(confirmed_*.json等)のpath・shaを記録。意味文言はユーザー記載どおり(変更しない)。

## 2. 再開(起動間隔≥150秒・300秒窓で2起動以内。RESTART_STORMを再発させない。各stage 1起動)
順序: (1)`--stages kp`(両level)→rc=0確認 (2)`--stages tts_b1b`(Adv、英語のみ) (3)**tts_a2の前に** `git status --porcelain -- er007_ja_secondary_asr_01.py er078_*.py er078_ja_v2beta_01.py er109_xz_scope_01.py er063_family_z_audio_01.py er026_family_z_fiction_production_runner_01.py` を確認。並行Worker(I)がJA-ASR配線でer007/er078を編集中のため、**これらに未commit差分がある間はtts_a2を起動せず**、2分間隔で最大40分待つ(待機中にSOURCE_FIDELITY_CHECK等の無料作業を進める)。40分経っても残る場合はtts_a2未実施のまま報告(判断候補)。差分なし(=commit済みHEAD)ならHEADのコードで `--stages tts_a2`。 (4)`--stages provision_shell,gate,assemble,pages,page_verify`(1起動)。
- 各stageのrc・費用(raw_usage_log集計)・ASR判定(PASS/PASS_W/HR)・速度Gate・Local Rewrite発火の有無を記録。HR Lock(rc=4等)で止まった場合は内容を記録して停止(自動解除・回数超過の迂回禁止)。既存STOP/LOCKの解除は行わない(Fable権限)。

## 3. 完成候補の公開・検証
- Pagesの正式経路どおり `user_test/family_z_in_a_grove_01/` に候補ページ(Std/Adv)を配置→push→live検証(index+全mp3 HTTP 200・Content-Length>0・byte一致、page_verify local: 全音声再生・console error 0・4xx 0)。ページ冒頭の状態文言は「正式完成候補・ユーザー試聴待ち」。
- `docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/SOURCE_FIDELITY_CHECK_01.md`: 最終Std/Adv本文(TTS入力)で7証言の順序・3つの矛盾する証言・結末(見えない手が小刀を抜く→闇へ沈む)・評決/真犯人/決定的証拠の創作なし・Std性表現の非グラフィック化維持、を本文引用で確認。Preview/Commentの先取りなし。
- `RUNTIME_EVIDENCE_01.md`: Voice割当(narrator Aoede/woodcutter Algieba/monk Schedar/constable Fenrir/old_woman Zephyr/tajomaru Orus/masago Kore/takehiro Puck)が送信パラメータで実証、ASR/速度Gate/LR結果、費用内訳、各stage rc、PASS_W一覧(あれば対象音声・理由・警告)。

## 4. SSOT・報告
- `OPEN_ITEMS.md`新規OPEN(FAMILY-Z-IN-A-GROVE-PRODUCTION-01、Status=COMPLETE_USER_LISTENING_PENDING、URL・sha・費用)、`DECISION_LOG.md` 1件、`docs/pm/USER_DECISION_REGISTER_01.md`に新規UDR(記事単位の試聴PASS/公開承認待ち、分類D)、ACTIVE_TASK(H)行更新(Re-Read、他行不変)。commit(編集ファイル明示`git add`、run出力はgitignore規則に従う)→`git push origin HEAD:main`(FF)。
- `docs/pm/RESULT_PACKET_FZIG7.md`: 整合/未承認機能/成果物(URL・sha)と目的適合(成功・失敗経路)/撤去・残置/判断候補(停止根拠file:line)/費用(stage別・累計/Cap)/commit。`判定整合:`行。最終回答は短く(URL・各stage rc・ASR/HR結果・費用累計・commit・判断候補)。

## 5. 範囲(11-8)
範囲内=承認済みZ仕様での再開・組立・候補公開・記録。範囲外=本文/Seed/Prompt変更、新Voice、Gate緩和、HR Lock迂回、正式公開承認(試聴PASSはユーザー)、Family A/B/C。

(以下、ユーザー選定原文は USER_02.md に保存済み。委任文中の<<<USER>>>〜<<<END>>>ブロックは同一内容。)
