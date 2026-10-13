# FIX2_DESIGN_01: 再利用segmentの検証状態引継ぎ(Adv正式assemble Gate BLOCK、OPEN-346②)の原因と修正設計(2026-10-13、JPY0)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_01 / Status: FIXED_PENDING_PRODUCTION_RUN / **Opus条件A(Gate入力の処理フロー変更)レビュー対象**

## 1. 原因(既存記録で確認)
Gate(`er003_v1_n3_01_assemble.py` の `verify_episode_audio_validation_gate` / `_segment_gate_status`)は `audit/tts_generation_results.json` の `segments[name]` だけを正とし、entryが無い/`status!="OK"` はUNVALIDATED(fail-closed)。以下2経路で、元の正式Validation済みsegmentがGateから見えなくなる。

A. **`--only-segments` による上書き**(runner `_generate_or_reuse` / `_generate_or_reuse_kp`): 非選択labelは、前回resultsに有効なOK entryがあっても **cacheを見る前に** `{"status":"SKIPPED_NOT_SELECTED"}` を返し、その辞書が今回のresultsへ書かれて前回entryを消す。Std R2 seed(preview/comment_1-4、entryごとseed済み・sha256あり)がこれで消えた(EVIDENCE_01のSTYLE_BASE_SHA_MISMATCH_OR_MISSINGの原因。wav自体は無傷)。
B. **別run由来のseed**: Adv(b1b)の再利用7 segment(topic_intro/preview/comment_1-4/in_one_line)は、`audit/seed_provenance_03_assemble.json` でwavだけがcopyされ、**results entry自体が存在しない**(`SKIPPED_NOT_SELECTED`が書かれたのは上記Aの結果)。元の検証記録は `eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/b1b/audit/tts_generation_results.json` にある(全segment `status=OK`・`asr_verified=True`、ただし**entryにsha256キー無し**)。

実測(現在のCoffee Adv): topic_intro/comment_1-4 の現在wav sha256 = 元run(e_tone_01)の検証済みwav sha256 = seed provenance記録sha256(3者一致)。**preview と in_one_line は不一致**: seedされたwavはTrial生成raw(`er057_output/coffee_final_listening_tone_trial_01/part_AEF/raw/E1.wav`、`er057_output/coffee_final_audio_assembly_01/segments/adv_in_one_line_raw.wav`)であり、e_tone_01でProduction検証されたwav(別take)とsha256が異なる。=Production Validation記録の無いwav。

## 2. 修正設計(Gate無変更)
新module `er019_family_x_validation_inheritance_01.py`(標準ライブラリのみ、API呼出なし)。引継ぎ条件(すべて満たす場合のみ、fail-closed):
1. 元entry `status=="OK"` かつ `asr_verified is True`
2. 現在wavの同一性証拠: (a) 元entryに `sha256` があれば現在wav sha256と一致 / (b) 無い場合はwitness2つ(seed provenanceのcopy時sha256 **かつ** 元runに残る元wavの現在sha256)がともに現在wav sha256と一致 / どちらも無ければ引継ぎしない
3. `expected_text` 指定時は元entry `canonical_text` と完全一致

引継ぎ結果: 元entryの深いcopy(status=OK・元のASR/QA/style_profile等は無変更)+ `path`/`sha256`=現在wav + `reused_from_previous_run=True` + `validation_inheritance{label:"REUSED_VALIDATED", evidence, wav_sha256, source_entry_fingerprint_sha256, source_ref, inherited_at}`(元記録へのポインタ)。entry.sha256が入るためGate既存の `ASSET_HASH_MISMATCH`(stale検知)が引継ぎ後も有効。Gateは status=="OK" を従来どおり受理するだけで、`REUSED_VALIDATED`ラベルは受理条件に使わない(Gate判定コードは変更しない)。

適用箇所:
- A対策(runner自動): `_generate_or_reuse` / `_generate_or_reuse_kp` の `--only-segments` 非選択分岐で `try_inherit_from_cached`。**同一out_dirの前回entryがsha256を持ち**、style_version一致(通常reuseと同じガード)、wav sha一致、canonical_text一致のときだけ引継ぎ。それ以外は従来どおり `SKIPPED_NOT_SELECTED`(Gate BLOCK維持)。引継ぎentryにはcaller側の現行style_profile再付与を行わない(4か所の条件に `not validation_inheritance` を追加)=元の記録をそのまま保持し、M3等が真の記録で判定する。
- B対策(明示CLI、既定dry-run): `rebuild_state` / `apply_state`(CLI `er019_family_x_validation_inheritance_01.py`)。`--apply`時は既存resultsを `.pre_inherit_<ts>.json` にバックアップし、既存entryが `SKIPPED_NOT_SELECTED`/無し のlabelのみ書込み(既にOK/STOPPED等のentryは上書きしない)。

通常経路(`--only-segments`なし、既存reuse)・Gate・M3 Gate・ASR Gateは無変更。

## 3. 安全性の論点(Opusレビュー依頼点)
- 「同一性の証拠」が十分か: sha256一致(entry自身、またはseed provenance+元wav実体)。ASR結果ハッシュ等の弱い識別子は採用していない。
- style_version: runner自動引継ぎは通常reuseと同じ一致条件。CLI(B)は元runの `style_version` が現行と異なる(`v5_j2_e2upbeat_f15_tone_refresh_fallback_style_retention` vs `v3_j3_kp_meaning_and_explanation_guard`)ことを `validation_state_rebuilt_01.json` に記録するが**ブロックしない**(この版は可変role[KP japanese_meaning/explanation]向けで、対象のAdv英語/support segmentには該当しない、との判断)。要レビュー。
- 引継ぎ対象外の扱い: 証拠不一致は理由コード(`WITNESS_SHA256_MISMATCH`等)付きでUNVALIDATEDのまま。

## 4. 検証(API 0円)
- 新規test `er019_test_family_x_validation_inheritance_01.py` 21件PASS: 引継ぎOK / 記録なしBLOCK / status非OK・ASR未検証BLOCK / entry sha不一致BLOCK / text不一致BLOCK / witness不一致BLOCK / 旧style_version BLOCK / `--only-segments`非選択で既存OK entryが保持される(上書きされない)/ 記録が無ければSKIPPEDのまま / wav変更後は引継ぎしない / 実Gate(`asm.verify_episode_audio_validation_gate`)で 引継ぎentry通過・SKIPPED BLOCK・引継ぎ後のwav改変でASSET_HASH_MISMATCH BLOCK / apply時に既存OKを上書きしない+バックアップ生成。
- 既存: er019 378/378 PASS(新規21含む)、er030 108/108、er003_v1_n3_01 55/55。
- dry-run(`completion_01/fix2_gate_sim_01.json`、実results未変更): 現状=7 segmentすべてUNVALIDATED -> 引継ぎ後=**topic_intro/comment_1-4の5件は引継ぎ(Gate通過)、preview/in_one_lineの2件はUNVALIDATEDのまま(BLOCK維持)**。再構築結果: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/b1b/validation_state_rebuilt_01.json`(新規ファイル)。

## 5. 重要所見(委任_02の前提、判断に影響)
Adv再利用のうち **preview と in_one_line は、Production Validation記録のあるwavではない**(Trial生成raw)。Gateを緩めない限りAdv正式assembleは通らない。選択肢(委任_02、いずれもGate無変更):
- (a) runner `--only-segments preview,in_one_line --level b1b` で正式経路(TTS+ASR+disfluency QA)により2 segmentを生成(Production TTS 2 call、数円程度)。**音声がv5 Adv完成版(視聴・承認済みのtake)から別takeに変わる**。承認済みtoneスタイル・同一textでの再生成のためtone仕様上の変更ではないが、聴感は変わりうる。
- (b) e_tone_01でProduction検証済みの別take(preview/in_one_line、`eigo-radio-tone`側)をseedして引継ぐ。v5完成版とは別takeを使うことになり、(a)と同様に聴感が変わる。
- (c) 現wav(Trial raw)に対する検証のみ(ASR+disfluency QAの既存関数による再検証)を行い、結果を新たにentry化する。音声不変だが、既存runnerには「既存wavだけを検証する」経路が無く新機能(新規実装)。
どれを採るかは、承認済み音声の同一性を重視するか、Production検証経路の標準性を重視するかのトレードオフ。(a)(b)はtake変更=ユーザー聴感への影響があるため、Fable/ユーザー判断の候補(開発側責任の範囲か否かの切り分けはFable判断)。
