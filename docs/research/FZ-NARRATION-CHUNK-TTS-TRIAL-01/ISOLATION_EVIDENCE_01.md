# ISOLATION_EVIDENCE_01 (FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_02)

正本evidence=`er026_output/family_z_dev_trials/fz_narration_chunk_01/{gen_result_<arm>.json, measure_01.json, preflight_01.json, module_set_01.json, aborted_01/}`。

## 1. N1(X M1〜M3の引継ぎ)
- `er113.redirect_production_sinks`を**再利用**(コピー実装なし): sink4種(attempt_history、HR queue、ASR telemetry、entity telemetry)を`<OUT>/sinks/<arm>/`へ、Pronunciation Ledgerは開始時の現行`ledger.json`のコピー(`sinks/<arm>/ledger_copy/`)へ(negative_cacheも追随)、`run_local_rewrite_recovery`はwrapperでout_dirをDEV化(発火0: `local_rewrite_events=[]`全arm)。cwd==ROOT assertあり。
- **Ledger事前計算**(Z TTS入力[run scope Z内の`_norm_for_tts`]・Z Style[NARRATOR_FULL_STORY_ADV]で全19項目[A_r2 3 + B_r1 6 + B_fine 9 + B_alt 4のうち、(clip, TTS入力)が同一のものを除いた数]): hint(medium+)・低confidence research対象・ASR cascade ledger phrase **すべて空**(`all_empty=true`、`ledger_unchanged_by_preflight=true`、ledger sha256 `90633657…`)。Aの記録(hints_applied=False)と同条件。**条件差なし**。各起動の直前にも再計算し空であることを確認(空でなければSTOPする実装)。
- TTS入力同値: B(chunk結合)のTTS入力がA(clip全体)のTTS入力と空白差を除き**全8組で同一**(`tts_input_equivalence`)。Style sha(`3a680861e4d9…`)・Voice(Aoede)・model(gemini-3.8-flash-lite-tts)・tts_backend・style version(`z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012`)がAの3 clipと一致(`style_voice_identity.all_equal=true`)。生成後のgen_resultでも全chunk `style_equals_A_style=true`・`instruction_type=english_style_prefix_wide_margin`・`local_rewrite_recovery=null`・`condition_diff=[]`・`minimal_fallback_used=false`。
- **TTS実行mode**: 初回起動で`TTS_EXECUTION_MODE`未設定→BATCH(既定)だったことを自己検知。Z production runnerの既定(`--tts-execution-mode STANDARD`、er026:2315)に合わせ、runnerが`TTS_EXECUTION_MODE=STANDARD`を明示設定するよう修正して再起動(`gen_result_*.json`の`tts_execution_mode=STANDARD`)。初回のbatch生成物はTrial成果物へ含めず`aborted_01/`へ隔離。

## 2. N2(並行案件下の検知)
- **audit hook**(`sys.addaudithook`、`_audit_hook`): 自プロセスの書込みopen/remove/rename/mkdir/rmdir/copyfile等を記録し、許可dir外は`PermissionError`で阻止+即STOP。許可root=`OUT`(gen)、post=`OUT`+`PAGE_DIR`+HF cache+temp。ffmpeg等のPopenは記録。
  - 全arm(gen 4起動+post): **violations=0**(再起動後)。`writes_by_event_dir`は許可dir(OUT配下・temp・HF cache)のみ。**Production store・Production run dir・`run_sf_prod_02`・公開ページへの自プロセス書込み0**。
  - 初回起動(B_r1起動1)は許可rootが`OUT`のみで、Production secondary ASRのfaster-whisper small読込がHF cache(`models--systran--faster-whisper-small/refs`: 公開モデルのlocal cache、repo/Production状態ではない)を触ったためhookが阻止・停止(`aborted_01/gen_result_B_r1_aborted_01.json`)。以後HF cacheを許可rootに追加(理由をコードコメントに記録)。他の許可dir外書込みの試みは発生せず(hookが阻止するため、無ければ0)。
- **保護store sha比較**(補助。X.PROTECTED_STORES[attempt_history、HR queue x2、telemetry x2、master_audio_store manifest/reuse_telemetry、ledger.json、cost_summary.json、negative_cache.json]+tree[1b_s1、`er011_output/local_rewrite_recovery`、`run_sf_prod_01`、Xの公開ページ]): 各armの前後と`post`の前後で**`protected_changed=[]`**(全起動)。※並行案件`run_sf_prod_02`は別agentが書込み中の領域のため監視対象外(自プロセスは書かない=audit hookが証明)。
- **mtime走査**(情報のみ): 各runで開始以降に更新されたrepo内ファイルは13〜118件(他agentのOPEN-508/Trial-06/SSOT更新を含む)。判定には使わず(誤検知源のため)、自プロセスの書込みはaudit hookで判定。件数・先頭40件は`gen_result_<arm>.json`の`mtime_scan_info_only`。
- **module同一性**: 起動時にimportされるrepo module(133〜135、`module_set_01.json`にsha256記録)について、(1)起動前に`git status`で未commit差分なしを確認(待機ログ: `gen_result_<arm>.json`の`module_identity_start.clean_wait`)、(2)起動直後にsha256が記録と一致、(3)終了時に再確認。**全arm: 未commit差分なし・sha変化なし**。生成中に遅延importされた追加module(`er033_tts_flash_lite_family_x_styles_01`、A_r2は+`er109_asr_orthographic_equivalence_01`・`er109_ukus_spelling_01`)も終了時にclean。Aの生成(2026-10-25 08:14)以降、loaded setのProduction moduleはgit log上変更なし(本Trialのcommit以外)。OPEN-508の案A配線commit(`53ce7b397`)はWriter側(`er062_family_z_writer_01.py`等)で、TTS/組立経路moduleは含まれない。
- **他Z TTSとの直列化**: 最初の起動試行(10:5x)は他agentのZ production run(`er026_family_z_fiction_production_runner_01.py … run_sf_prod_02`、real)稼働中のため`other_z_tts_processes`で自己STOP(API 0)。同runの終了(10:56)を待ってから起動。以後の各起動前にも稼働なしを確認。`tools/stop_scope_check_01.py`は全起動rc=0(STOP非適用)。

## 3. N3(DEV assembler)
- target_rms=`1b_s1/b1b/assembly/timeline.json` gain_report.target_rms=**0.07332に固定**(再計算でchunkのRMSを使わない)。参考: A側の(preview+part1_c1)/2再計算=0.073318(差<2e-6)。
- Aのみ再組立して**オリジナルのtimeline(全長273.789秒、全piece start差0.0)に一致**することを確認(DEV assemblerの忠実性)。
- 展開後の並び: `…, Comment 1, full_story_part1_c1_k1, _silence_0.2, full_story_part1_c1_k2, _silence_0.5, _silence_1.0, Comment 2, …`(既存のnarrator後0.5秒とComment前1.0秒は最後のchunkの後に1回だけ)をassert。全B系armでPASS。
- A_r2 sha256≠A(3 clip全て新take: A `61957c46…`/`9aa17d01…`/`84cb2233…`に対しA_r2 `3156bb82…`/`0be61d7f…`/`5cfbde37…`)。Master Audio Store/reuse経路を通らず直接generatorを呼んでいる。
- ヘッドルーム弁: 全arm `applied=false`(peak ≤0.88)。

## 4. 1b_s1 Adv音声(A)のGate/HR状態(未確認事項の確認)
- 3 clip(part1_c1/part2_c3/part3_c1): `status=OK`、`z_adoption=adopted`、`asr_judgement.state=PASS(primary_pass)`、attempts=1、review_lock_state=`RESOLVED`(final_status OK)、`gate_result_04C.json`: `m2_complete=true`・`z_speed_profile`全clip ok(adv_narrator_none)・`audio_text_deviation_clips=[]`、`pass_with_warning_listening_list.count=0`。Production HR queueへの記録はsink隔離のため本Trialでは書かない(AはProductionの`run_sf_prod_01`ではなくTrial run `1b_s1`の記録)。→ Aとして使える。
