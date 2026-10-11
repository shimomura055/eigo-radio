# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04A(作業A: 既存Production不具合の是正、2026-10-12)
ユーザー承認2026-10-12「既存Production不具合の是正: 実装修正まで許可」。branch `fix/asr-tts-prodfix-01`(worktree eigo-radio-prodfix)。mainへ未merge(Fable Opusレビュー待ち)。

## diff要約(main比 19ファイル、+456/-15)
- OPEN-270: `er003_v1_n3_01_tts_generate.py` `generate_a2_segment_with_slowdown`(外側ループへ共有生成カウンタ、+残予算を内側へ)・新`count_tts_generations_in_result`(+35行)。
- OPEN-271/275: `er005_cost_logger.py` 新`azure_stt_cost_usd`(+24)、11 runnerの`compute_cost_jpy_so_far`各+2/-1(er012_b/e、er012_editorial_b_voices x7、er012_personalized_news_b1_rebuild、er019)。er019はreview_lock importも追加。
- 記録: `er011_human_review_lock_01.py` 新`style_prefix_record`/`build_attempts_detail`/`append_attempt_history_event`/`archive_prior_tts_results`+`record_outcome`へ`attempts_detail`(+84)、`er003_v1_repro01_main_generate.py`(標準entryにstyle_prefix/cascade_steps、minimalラベル置換+17)、`er003_v1_crosslevel_audio_02_common.py`(fallback cascade steps保持+12)、`er006_secondary_asr_01.py`/`er007_ja_secondary_asr_01.py`(queue重複時の転写をhistoryへ+5ずつ)、tts_generate/er019のresults上書き前退避(計4箇所)。
- test: `er058_asr_tts_prodfix_01_test_01.py` 17件。

## 結果
- 新規test 17 PASS(旧コードで10件FAIL)。関連suite 168ファイル: main=新=95 failed/8 errors(同一fail集合、差分は未commit差分起因/flakyのみ、新規failure 0)。
- runtime evidence: TTS生成 旧6回→新3回(`cap`)、Azure 13.6秒→0.605円計上(旧0.0円)、転写・Style・Secondary stepsがattempt_history.jsonlへ保存。詳細 `er058_output/asr_tts_prodfix_01/RUNTIME_EVIDENCE_01.md`、設計 `FIX_DESIGN_01.md`。
- 費用: 実課金 約0.6円(Azure 1回)、上限5円内。Gemini/OpenAI 0円。Production telemetry混入なし。
- Dangling Reference Check: 変更で孤立する参照なし(固定ラベル"minimal (not ENGLISH_STYLE_PREFIX)"の消費側なし。同ラベルは`er012_b_family_voices_production_01.py`L474・`er012_editorial_b_voices_trial_09_audio.py`L628に別関数として残存=未変更、報告のみ)。
- 既存承認仕様との衝突: STOPなし(CS L1692遵守方向。旧コメントの「内側を最大3回取り直す正当なretry」は総3回上限と矛盾していた点を是正)。
- 未実施/Fable判断: OPEN-275のSSOT反映(Coffee補正約31.03/50、tier未確認)、CURRENT_SPEC/DECISION_LOG反映はmerge後委任。実`--stage tts`再実行(TTS課金、results上書き退避は単体testのみ)。Azure契約tier(F0/S0)はユーザー確認事項。
