# DESIGN_Z_01 — Z Standard(a2) への B_r1 Chunk分割(+0.2秒)配線 設計(Opus M2/M3/R6/R7反映)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03(2026-10-26)。前提=ユーザー正式承認(APPROVED_FOR_PRODUCTION 2026-10-26。Standard除外不可)。
基準HEAD=`21b6034ca`。設計の元=`DESIGN_01.md` §6、Opus所見=`OPUS_REVIEW_01.md`(M2/M3/R6/R7)。分割規則・減速率・ポーズ長は変更しない(B_r1: 100語超・k=ceil(語数/100)・等分割・最小25語、6%減速、0.2秒)。

## 1. 合成方式(X/Y Stdと同一)
chunkごとに既存の `n3_tts.generate_a2_segment_with_slowdown`(TTS→atempo 6%→減速後ASR再検証、通算TTS3回)を適用 → 減速後chunk wavを減速対象外の0.2秒(4800サンプル@24kHz)で連結。連結後減速は採らない。新規後処理・閾値・補正係数なし。

## 2. 変更点(M3 = 同一commitで一括)
| # | 場所 | 内容 |
|---|---|---|
|1|`er117:plan_z_clip`|`level != "b1b"` 条件を撤去(Std/Adv同一規則。`CHUNK_PLANNER_VERSION`不変。Advのplan出力はバイト同一)|
|2|`er063:build_level_plan`|chunk展開条件 `level == "b1b"` → `level in ("b1b","a2")`(`kind == "narrator"` は維持=dialogueは対象外)|
|3|`er063:_run_tts_stage_impl` attach|`attach_chunk_meta(..., level=spec.level)`。a2のみ `chunk_tts.level`/`std_slowdown_composition` を追記。b1bはバイト不変|
|4|`er063:_z_chunk_parent_display`|a2のみ `std_parent_slowdown_fields` で集約(全chunk減速済みのとき `slowdown_applied=True`、1つでも欠ければFalse。明示True/Falseなので親`_original.wav`の弱証拠に落ちない)。b1bは `None` のまま(`verify_z_speed_profile` のAdv Narrator「速度処理なし」検査を維持)|
|5|`er063:build_entry`|Std chunk entryにだけ `slowdown_info`(減速前後長)を記録(R2の厳格検査の根拠。Z entryは従来 `slowdown_info` を持たなかった)。非chunk・Advは不変|
|6|`er063:_run_tts_stage_impl` cache|`drop_cached_std_chunks_without_slowdown` を `load_results` 直後(+checkpoint統合後)に適用(a2のみ)。`--only-clips` で選ばれなかったclipの再利用経路(`generate_or_reuse_z`を通らない)でも減速証跡なしchunkを持ち込まない|

## 3. 速度Gate厳格化(M2)
- `_CLIP_ID_RE` で絞っていた2箇所(`verify_std_english_slowdown` 内、`run_audio_gate` 呼出側)を `_CLIP_OR_CHUNK_ID_RE` へ。入力検証(`build_level_plan` のstory clip id)・`comment_after_segment_ids`・`part_to_clip_id` は厳密な `_CLIP_ID_RE` のまま。
- chunk idは新設 `_std_chunk_slowdown_check` で `chunk_tts.std_chunk_slowdown_violations`(`slowdown_applied is True`・減速前後長の記録あり・比∈[1.03,1.09])を厳格に要求。`_original.wav` の長さ比による救済は使わない。planに無い・planが渡されないchunk idも1chunk擬似planで同じ検査(抜け道なし)。planのchunk entry欠落はNG。
- 非chunkのStd narrator(従来経路)は従来どおり(`slowdown_applied=True` または `_original.wav` 比)。dialogueはStd減速禁止のまま(`verify_z_speed_profile`、無変更)。
- 親は対象idに入らない(planのclip id=chunk id)ため、親の集約値はこのGateには届かず、chunk entryの個別検査が正。親集約は共有Gate(`verify_episode_audio_validation_gate`)・表示用。

## 4. 不変の保証
- Z Adv: plan(ClipSpec列)・chunk plan・親display・`attach_chunk_meta`・reuse_keyが凍結HEAD golden(`measure_z/z_adv_golden_01.json`、melos e1_01 b1b / tell_tale run_chunk_01 b1b)とバイト一致(`er063_z_std_chunk_test_01.py::AdvInvarianceGoldenTests`)。`_z_chunk_parent_display` b1b=None、`er063` Adv検査(`e.get("slowdown_applied") is True` → 「Adv Narratorに速度後処理」)維持。
- Zセリフ経路(R6): 変更ファイル=`er063`/`er117`のみ。`er122_fz_ctx_policy_01.py`/`er122_fz_ctx_notes_01.py`/`er012_b_*`/`er003_v1_n3_01_tts_generate.py` の差分0。Stdでchunk展開したplanに `story_clips_from_plan` を掛けると非chunk時と同一(畳み戻し)→ 文脈抽出入力・dialogue `reuse_key` 不変 → 旧planのdialogueはcache再利用(TTS 0回)。
- legacy: 本方式導入前のStd結果(親entryのみ)は `effective_plan`(gate/assemble/pages = `for_tts=False`)で従来経路。tts stageは常にchunk化。

## 5. Local Rewrite(R7)
`generate_a2_segment_with_slowdown` 内でLR(再TTS)は減速前の `generate_english_segment_with_fallback` に含まれ、その出力に6%減速が掛かる(`apply_a2_slowdown_postprocess` は `out_path` 全体を処理)。`_handle_local_rewrite`(er063)は監査記録のみで音声を触らない。→ LR経由のchunkでも `slowdown_applied=True`/`slowdown_info` が残り厳格Gateを通る。減速が漏れたLR出力は厳格Gateが止める(test固定)。

## 6. FZ evidence runの再開注意(R6記録)
FZ(文脈TTS)のStd evidence runを後からTTS resumeすると、100語超のnarratorは親ClipSpecでなくchunkで再生成される(reuse_keyにchunk項目)。旧Std非chunkのnarrator親音声は再利用されない。dialogue・短narrator・KP等は不変(再利用)。

## 7. 実Z Std対象(B_r1の実行結果、Phase 2 plan)
melos a2: part2_c1(134語)→76/58語(段落境界)。tell_tale a2: part2_c1→60/69、part3_c1→68/71(段落境界)。Adv実績(58/62、65/61、74/50)と同じ規則。71〜100語のclipは分割しない(Advと同じ)。
