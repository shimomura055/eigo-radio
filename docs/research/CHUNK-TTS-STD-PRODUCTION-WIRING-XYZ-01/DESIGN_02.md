# DESIGN_02 — Opus条件Aレビュー(OPUS_REVIEW_01.md)のM/R対応表とZ側実装指示

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02(2026-10-26)。Opus所見は承認済み仕様(APPROVED_FOR_PRODUCTION: Std/Adv双方)内の不具合修正・設計反映で、ユーザー判断事項なし(Fable照合済み)→ **M1・R1〜R5を全件採用して実装済み**。Z側(M2/M3/R6/R7)は`er063`をFZ Phase 2(Z文脈TTS evidence)が使用中のため**次委任へ引継ぎ**(本委任は`er063`未編集)。

## 1. 対応表(X/Y側、本委任で実装・test済み)
| ID | Opus所見 | 実装 | 場所 | test(新規) |
|---|---|---|---|---|
| M1 | 旧方式Std(Adv)結果へ『本文以外』の`--only-segments` retryで検証済み本文が失われる | 親もそのchunk idも`_ONLY_SEGMENTS`に含まれず、前回cacheが`is_legacy_unchunked`の親は従来経路(親名で`_generate_or_reuse`=検証済みentryの引継ぎ)に残す。本文を含む通常resumeはchunk化して再生成(現行維持) | `er117_chunk_tts_production_01.py` `legacy_partial_retry_parents`/`apply_legacy_partial_retry`、`er019…runner` `generate_family_x_b1_segments`/`generate_family_x_a2_segments`(cache取得直後) | `er019_x_std_chunk_opus_test_01.py` `M1LegacyStdPartialRetryTests`(4)・`M1LegacyAdvPartialRetryTests`(1)。**mutation確認**: `apply_legacy_partial_retry`を無効化すると2件FAIL |
| R1 | 減速証跡検査をstage関数だけでなくload関数にも置く | X: `load_family_x_a2_sources`(整合検査の直後)、Y: `_load_y_body_chunks(out_dir, level)`(`level=="a2"`のとき)。Advは検査を追加しない(既定level=b1b) | `er019:load_family_x_a2_sources`、`er121_family_y_audio_01.py:_load_y_body_chunks` | `R1LoadFunctionHasSlowdownCheckTests`(3)・Y `test_r1_*`(2)。『親の集約値だけTrueに偽装』しても直接呼出でBLOCK |
| R2 | `slowdown_info`の`src/dst_duration_seconds`欠損が素通し | 欠損(または0)をchunk違反`STD_CHUNK_SLOWDOWN_DURATION_RECORD_MISSING`に。正規生成は両方を記録するため誤ブロックなし(test) | `er117:std_chunk_slowdown_violations` | `R2MissingDurationRecordTests`(3)・Y `test_r2_*` |
| R3(a) | 集約値Falseの親が古い親`_original.wav`の弱い証拠で救済されない | 既存Gate`_segment_missing_mandatory_a2_slowdown`は`slowdown_applied is False`のとき`_original.wav`を見ない(コード変更なし)。回帰固定test | — | `R3Tests.test_a_…` |
| R3(b) | 減速後NG→HR承認chunkで親OK・集約True・組立PASS | 実装は既存(`refresh_parent_status`+`std_parent_slowdown_fields`)。回帰固定test | — | `R3Tests.test_b_…` |
| R3(c) | planに無いchunk id指定は素通り | `unknown_chunk_ids_in_selection`で課金前に拒否(X: `ChunkIntegrityError`、Y: `YAudioStop FAMILY_Y_CHUNK_ID_NOT_IN_PLAN`)。X/Y・Adv/Std共通 | `er117`、`er019`(両generate)、`er121:_record_chunk_decision` | `R3Tests.test_c_*`(2)・Y `test_r3c_*` |
| R4 | Adv不変の補強 | (a)`git diff bb578265c`の各hunkを関数単位で機械分類(`tools/adv_hunk_classifier_01.py`、UNCLASSIFIED=0をtestで固定)、(b)mock生成器でAdv generate+assembleを旧(bb578265c worktree)・新で実行しバイト比較(`tools/adv_invariance_driver_01.py`/`_compare_01.py`、X Adv・Y Adv単一/複数段落)、(c)Y b1b `chunk_tts_decision.json`をgolden化(`golden/y_b1b_chunk_tts_decision_golden_01.json`、差分=`approval_ref`/`note`の注記文言のみ) | `tools/`・`adv_invariance/`・`golden/` | `R4HunkClassifierTest`・Y `TestAdvDecisionGolden`(2) |
| R5 | `er121_family_y_audio_01.py`の凡例『(今回はありません)』が固定文言 | `n_chunked>0`のとき『今回は分割があるsegmentにのみ出ます』へ出し分け | `er121:page_legend_html` | Y `test_r5_*` |

付随(Y structure matchの許可リスト): `chunk_tts.apply_legacy_partial_retry`(Y-NO-LEGACY=Opus M1はX限定の指摘。Yの正式runに旧方式[複数段落]結果は無く、Yのgate/assembleは旧方式effective_planを持たない)と`chunk_tts.ChunkIntegrityError`(Yは`YAudioStop`で同等に停止)を`ALLOWED_X_ONLY`へ追加(`er121_family_y_structure_match_test_01.py`)。

## 2. 既知事項(SSOT記録文案)
- 本文を含む通常のresume(`--only-segments`に本文part/本文chunkを含む、または全再実行)は、前回結果が旧方式でも**chunk化して再生成する**。承認文『resumeへ一貫して反映』に合致。旧方式の検証済み本文を残したい場合は、本文以外を`--only-segments`で指定する(M1)。
- FZのStd evidence run(Z)は、後でTTSをresumeすると100語超のnarratorがchunkで再生成される(R6)。

## 3. Z側(次委任)の実装指示 — DESIGN_01 §6 を以下で置換
Z実装は**並行Agent(FZ)のcommit後**に行う(`er063`は同Agentが編集中)。次の4束を**同一commit**で入れる。
1. **M3(レベル条件の同時撤去)**: `er117_chunk_tts_production_01.py:156-157`(`plan_z_clip`の`level != "b1b"`)と`er063:598`(`level == "b1b"`)を同時に撤去し`level in ("b1b","a2")`相当にする(片方だけだとplanだけ発火/Specへ展開されない)。`er063:1561`の`attach_chunk_meta(..., level=spec.level)`。`_z_chunk_parent_display`(`er063:636`)は**a2のときだけ**`std_parent_slowdown_fields`で集約し、b1bは`slowdown_applied: None`のまま(バイト不変・`er063:1805`の検査維持)。`drop_cached_std_chunks_without_slowdown`は`load_results`の直後(`er063:1525-1528`の並び)に置く(`--only-clips`で選ばれなかったclipの再利用[`er063:1540-1545`]が`generate_or_reuse_z`を通らないため)。
2. **M2(速度Gate)**: `_CLIP_ID_RE`の絞り込みは**2か所**(関数内`er063:1731`と呼出側`er063:1865`)。**両方**を広げ、chunk idについては `chunk_tts.std_chunk_slowdown_violations(chunk_plans_from_specs(plan), segments)` で`slowdown_applied is True`と比率(1.03〜1.09)を**厳格**に要求する。`_original.wav`による弱い証拠の救済は使わない。『親は集約値で判定』(旧§6-4)は**撤回**(親は速度Gateの対象idに入っておらず`er063:1672-1673`、集約値は届かない)。test: 減速の無いStd chunkで`FamilyZSlowdownGateStop`が出ること。
3. **R6**: Stdでchunk展開したplanに`story_clips_from_plan`(`er122_fz_ctx_notes_01.py:170-188`)を掛けると非chunk時と同一(猿の手Std15・メロスStd10のTrialとの一致、dialogueのTTS 0回)になるtest。FZのStd evidence runに後でTTS resumeを掛けると100語超narratorがchunkで再生成される旨を記録。
4. **R7**: Std chunkでLocal Rewrite(`er063:1553-1555`)を経た出力に減速が掛かっていることのtest(M2の厳格Gateで止まる前に確認できるように)。
5. 旧§6の他項(dialogue不変・`build_reuse_key`のchunk追加・`for_tts=False`の`effective_plan`・test書換え`er117_z_chunk_wiring_test_01.py:130-132,202`・golden追加)は有効。
6. 約70語の件: Opusが『承認済みの規則はB_r1そのもの(閾値100語・k=ceil(語数/100)・等分割・最小25語)。対象Std clip[122〜139語]では約61〜70語×2でAdv実績[58/62、65/61、74/50語]とも合う。ユーザー再確認不要。71〜100語のclipを分割しないのはAdvのB_r1と同じ』と判定。Phase 2で実chunk語数を記録する。

## 4. Z Phase 2 起動計画(DESIGN_01 §7のZ行を置換)
Opus指摘どおり旧計画のstage列(`provision_shell,gate,assemble,pages,page_verify`)には**tts stageが無かった**。Zは**TTS実行を含めて**次の2段にする:
1. TTS(Std narratorのみ): `--stages tts_a2`(Z runnerのstage名は`er026`の定数で確認)に **`--only-clips <親id>`**(例 `the_tell_tale_heart`の129/139語narrator clipの親id、1〜2 clip)を付ける。dialogueはTTS 0回であること、chunk語数、厳格速度Gateの判定を記録する。
2. 完成段: `--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**(OPEN-480、provision_shell欠落でgateがrc=2→再起動でRESTART_STORMを自行発動するため)。公開pageは上書きしない(候補dir)。
- 費用: BUDGET_PLAN_01のZ行(≤17円)。当日の他案件の進行(Y Trial Cap250・Z Phase 2 Cap200等)を考慮し、起動前に`daily_dev_cost_01.py`で確認する。

## 5. 不変事項
- 分割規則・閾値・減速率・ポーズ長・合成方式は変更していない(Opus論点1『合成方式は妥当』)。`CHUNK_PLANNER_VERSION`不変。
- `er063`は本委任で未編集(`git diff --stat -- er063_family_z_audio_01.py` = 本委任由来0)。
- 共有module(`er003_v1_n3_01_assemble.py`等)は無編集(Opus論点2『共有moduleを変えなかった判断は妥当』)。
