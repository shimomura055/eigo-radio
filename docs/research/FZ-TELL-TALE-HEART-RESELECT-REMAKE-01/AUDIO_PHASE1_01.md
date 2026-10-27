# AUDIO_PHASE1_01 本文音声の再制作 Phase 1(準備のみ、API 0)

結論: **本文音声のTTS生成は選定確定前には実行できないため未実行**。準備と検証までを実施。

## 理由(コード根拠)
- `stage_tts`(er026_family_z_fiction_production_runner_01.py:2504)→`load_level_inputs(for_tts=True)`(:2423)の先頭で`_assert_kp_review_consistent`(:1521、:2431)がKP Human Review未確定を`FamilyZKpReviewPending`(rc=4)で拒否する。さらに:2457でAdvの文法(Part 2)確定を要求し、:2449-2455でPart 1(Vocabulary & Expressions解説・訳)の存在を要求する。TTS計画(`a63.build_level_plan`)自体がKP音声clip(kp_en/kp_ja)を含み、同じ入力として一体で組まれる。
- 本文clipだけを先行させるには`--only-clips`でも上記入口を通る必要があり、runnerの承認済み機能だけでは分割できない。入口検査を迂回する独自経路は作らない(Gate/HR Lock迂回禁止)。
- 先行できる時間は本文TTS分(旧run_chunk_01実績 tts_b1b 179秒+tts_a2 201秒≒6.5分)程度で、全体最短化への寄与が小さいと判断。

## 準備・検証(API 0)
- 新run `run_reselect_01`: writer/segment_plan/dialogue_attribution/speaker_table/supportを`run_sf_prod_02`系からコピー済み(本文sha一致確認、FIXATION_01.md)。旧音声(a2/ b1b/)・旧KP・旧audit/HR Lockは持ち込まず → Style記録は`NEW_RUN`扱いで課金前STOPに抵触しない(er063 `assert_run_style_record`)。
- Voice割当(`voice_assignment.json`、APPROVED_FOR_PRODUCTION 2026-10-23): Narrator=Aoede、old_man=Algieba、officer=(男性pool)ほか決定論再計算。
- Chunk計画(`chunk_tts.plan_z_level`、API 0で再計算): Adv=full_story_part2_c1[58,62]・part3_c1[65,61](旧run_chunk_01と同一)。**Std(a2)も[60,69]・[68,71]に分割される**(Std Chunk配線CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01適用後の現行仕様。旧公開版のStdは非分割)。
- 現行仕様の適用(セリフ文脈感情TTS fz_ctx_v1、統一TTS retry/Fallback/LR、Primary/Secondary ASR、速度仕様v2、Style actual gate)はrunnerのTTS stage内で自動適用される。有料前の再確認項目: stop_scope_check、`--tts-execution-mode STANDARD`、`--stages kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`を**1起動**(OPEN-480、provision_shell必須)、`--pages-dir`を新規dirに指定(既定は公開dir `user_test/family_z_tell_tale_heart_01`を上書きするため**必ず別dir**)。
- 実行結果(ASR/Style/速度/Chunk/Gate/retry/LR): **未生成のため該当なし**。Local Rewrite採用: **0(未実行)**。
- 見積り(Phase 2): 本文TTS約16.5円+KP/解説音声・Part 1・retry余裕 → 約25〜35円(BUDGET_PLAN_01)。
