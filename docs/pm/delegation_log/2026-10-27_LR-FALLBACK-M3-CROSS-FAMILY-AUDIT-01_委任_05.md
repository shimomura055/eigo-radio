# 委任_05: 分類A(承認済み仕様からの実装逸脱)の是正 F1/F2/OPEN-564(実装+test、API 0)

管理ID: LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01(Fable→sonnet-worker、2026-10-27)。共通事項=`…_委任_00_COMMON.md`(参照所在)。ただし本委任は**実装委任**なので「編集禁止」のうちProductionコード・testの編集は本委任で指定した範囲に限り可。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)はFableが同期するので編集しない。
根拠: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W2_SIX_ROUTES_01.md` §5 F1/F2・§6 P1/P2、`W1_LR_DATAFLOW_01.md` F-3、`W3_M3_LR_HR_01.md` J-3(OPEN-564)。Fable判定: 3件とも承認済み仕様どおりへの是正(PM_GOVERNANCE 11-8)=ユーザー承認不要・API 0。Gate判定(M3/Y gate/HR Lock)・音声・resume正当性・Prompt・閾値は**一切変えない**。

## 是正対象(この3件のみ。範囲拡大禁止)
1. **F1(er127 `BlockProgress` LR block記録保全)**: 実LR経路(③未closeのまま`lr_recover`→LR block depth1→`finish`)で`blocks["1"]`が消え、NGだった③が`verified:true`になる。原因候補=`finish()`(`er127:473-480`付近)が`mark_done`のmerge前にdepth0 stateをfile書込。是正案P1=`lr_recover`入口で未closeの③を`done(open,False)`で閉じ、`finish_attempt`/`_write`をdepth別blockのmerge書込にする(または書込順序の修正)。**実経路を再現するtest**(③未close→LR block→finish→fileに`blocks["0"]`③verified:false と`blocks["1"]`の①'記録が残る)を`er127_tts_block_policy_01_test_01.py`へ追加。既存test`test_mark_done_keeps_depth1_lr_block_record`は実経路を再現していないので、実経路版へ置換または追加。resume判定(消費済みattempt再実行なし・残り待機のみ)が不変であることを既存testで確認。golden(A/B/C byte同一)不変。
2. **F2(Std L4経路の`LR_REWRITTEN`警告欠落)**: `er003_v1_n3_01_tts_generate.py:148,151`の`_post_slowdown_unified_judge`が`script_version="v0"`固定。`CURRENT_SPEC.md:2925`「PASSなら必ず`LR_REWRITTEN`警告」に反する。是正案P2=`apply_a2_slowdown_postprocess`/`_post_slowdown_unified_judge`へscript_version(LR block内=v1)を伝播し、Std LR採用entryの最終`asr_judgement`と`pass_with_warning_listening_list.json`に`LR_REWRITTEN`が付くようにする。判定結果(PASS/NG)は不変、警告付与のみ。test追加(Std LR採用→最終judgeにLR_REWRITTEN)。AI島a2の保存データを**書き換えない**(過去runの事後修正は行わない。読取での再現確認は可)。
3. **OPEN-564(`er003_v1_crosslevel_audio_02_common.py:477`付近 `_merge`がLR成功時に無条件`fallback_used=True`)**: Std側だけ記録が非対称。是正=LR採用attemptが①'(元role Style)で成功した場合は`fallback_used`を実際の採用attempt種別に従って記録する(③'採用ならTrue)。**M3のBLOCK結果は`LOCAL_REWRITE_RECOVERY`で変わらない**(Gate緩和ではない)ことをtestで固定(`er019_family_x_style_profile_01_test_01.py`等にケース追加: LR成功+fallback_used=False→なおBLOCK)。

## 検証
- 変更module関連test全件: `er127_tts_block_policy_01_test_01.py`(golden含む)、`er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py`、`er020_*test*`、`er019_family_x_style_profile_01_test_01.py`、`er121_family_y_style_profile_test_01.py`、`er078_asr_unified_backcompat_07_test_01.py`、`er117_z_chunk_wiring_test_01.py`、その他変更関数のcaller test。実行コマンドと結果(件数・失敗0)を記録。既存失敗(OPEN-543管理)は差分がないことを示す。
- 有料runは起動しない(API 0)。runtime evidenceは「次回のLR自然発生run」で採取する旨を記録(未観測を実証済みと書かない)。
- 変更の影響範囲: X/Y/Z 6経路のうち各修正がどの経路に効くかを表にする。Dangling reference・旧記述のGrep。
- **注意**: 同時刻に別worker(FZ-TELL-TALE-HEART-RESELECT-REMAKE-01)がFamily Z正式runnerで有料TTSを実行中の可能性がある。Productionモジュールの編集は**ファイル単位で一括保存**(途中状態を残さない)し、編集前後でtestを通す。`er026_output/`配下・Z runの状態ファイルには触れない。

## 成果物・報告
- `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/FIX_A_01.md`(変更点・file:line・test結果・影響表・未観測)。
- Git: 本委任で変更したファイルのみ`git add`(`git add -A`禁止)、commit message「LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 委任_05: F1/F2/OPEN-564是正(API 0)」+末尾に`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、pushまで。test失敗や競合時はcommitせずFableへ報告。
- 最終応答: FIX_A_01.mdのパス+要約10行(各修正の内容/test件数/Gate不変の確認/未観測/commit hash)。
