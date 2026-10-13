# F1_M1_RUNTIME_EVIDENCE_03 (委任_03、Adv comment/preview TTS実run)

実行: `--level b1b --style-profile coffee_n01_r2_p3_e1 --stage tts --only-segments preview,comment_1,comment_2,comment_3,comment_4`(rc=0、費用JPY1.47、gemini-3.8-flash-lite-tts、backend speech_metadata_flash_lite)。
M1配線commit: `94fb0c03`(+`130e0133`)がmainに存在、`git status --porcelain er006_secondary_asr_01.py er006_m1_multi_candidate_01.py`=空(有料run前確認済み)。

| segment | status | audio_classification | attempts | F1/M1記録 |
|---|---|---|---|---|
| preview(E1) | OK | NORMALIZED_MATCH | 1 | connected_speech_info=None(通常ASR判定で合格、F1/M1層未起動) |
| comment_1 | OK | EXACT_MATCH | 1 | 同上 |
| comment_2 | OK | NORMALIZED_MATCH | 2 | 1回目 TRUE_CONTENT_MISMATCH(F1が`f1_version=F1-2026-10-13`を記録、`layer_judgment=EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE`)→2回目 NORMALIZED_MATCH |
| comment_3 | OK | NUMERIC_EQUIVALENCE_MATCH | 1 | 通常判定 |
| comment_4 | OK | EXACT_MATCH | 1 | 通常判定 |

- F1: `tts_generation_results.json`内に`f1_version: F1-2026-10-13`が6箇所記録(comment_2 attempt 1の連結発音層判定で実発火)。F1の自然発生evidenceは今回のAdv runで1件取得(OPEN-340)。
- M1: 新配線(OOV複数候補)は今回のsegmentでは発火条件(OOV差分)に至らず、`m1_layer_invoked`等の記録はなし(未発火=配線有無と無関係。M1自体の配線commitは存在)。
- Preview(E1) M4記録: `style_profile.profile_id=coffee_n01_r2_p3_e1, role=PREVIEW, expected_base_sha256==style_base_sha256=8862317ff76693ff...`、`style_prefix`=E1逐語、`instruction_type=english_style_prefix`(minimal_fallbackでない)。
- Comment 1〜4は main Style(`calm, conversational`、E0維持)で正式経路再生成(profile不変、Style正本確定はOPEN-350の未決として残る)。
