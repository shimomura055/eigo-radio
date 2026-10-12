# WIRING_CHECKLIST_V5_01 (判定はFable。`PRODUCTION_WIRED`は付けない)

| # | 項目 | 結果 | 理由・根拠 |
|---|---|---|---|
| 1 | 初回経路実装 | **充足(コード+test)** | `FAMILY_X_A2_COMMENT_4_ROLE`にTrial-03の2文を追加(Prompt sha22feebde…、prompt_trial_03.mdと逐語一致をtest固定)。profile `coffee_final_v5`(FULL_STORY=P8維持/SUPPORT_JA=R2[a2のみ]/KP_EXPLANATION_EN=P3[b1bのみ])を`er019_family_x_style_profile_01.py`へ追加し、runnerの単一解決関数(`resolve_role_style`)経由でStd preview/comment_1〜4とAdv KP解説に配線。記録(`audit/style_profile.json`、segment/KP解説の`style_profile.style_base_sha256`)、M2/M3/M4/M5を拡張。default・coffee_p8の動作はバイト同一(test)。 |
| 2 | retry/fallback/Local Rewrite整合 | **部分充足(BLOCK実動作は実測なし)** | retry: Std comment_1でattempt1がASR不合格→attempt2が同一R2で再送(実測)。fallback: Std JAのminimal instruction fallbackはR2を落とす→M3 Gate(`JA_FALLBACK_USED_OR_UNKNOWN`)でBLOCK(test、実発生は0件=BLOCK実動作は未実測)。Adv KP解説はfallback経路なし(失敗=STOPPED=M3 BLOCK、test)。Local Rewrite: 対象roleに経路なし。OPEN-312(Full Story側のLR再TTSでStyle脱落)は未解決(Full Storyはv4音声流用)。 |
| 3 | 正式runtime発火証拠 | **充足(両level)** | Std: 実TTS 6 attempt全てinstruction sha=R2。Adv(委任_02の再実行1回、rc=0): KP解説5件すべてinstruction sha=P3(`a8aaec59…`)、gemini-3.8-flash-lite-tts/Aoede/BATCH、ASR gpt-4o-mini-transcribe全NORMALIZED_MATCH、各attempt=1(retry 0)、results recordあり、`style_profile`記録(profile coffee_final_v5/KP_EXPLANATION_EN)、fallback/Local Rewrite 0。M3 pre-assembly Gate: KP解説5件はBLOCKなし(full_story_part1〜3のみNO_SEGMENT_RECORD=v4音声流用でruntime生成なし、意図通り)。`STYLE_APPLICATION_EVIDENCE_V5.md`/`style_application_evidence_v5.json`。 |
| 4 | Regression/integration PASS | **充足(既知の既存失敗1件を除く)** | style_profile test 49件(既存32+新17)OK。runner test 49、er019関連(flash_lite_role_style 8/ja_recheck 4/kp_structure 36/new_structure/opus_l2_fixes 24/pointless 10/variable_role_style/b3 30/entertainment 20/section_segmentation 15/an3_t0 18/ja_writer 7/writer_run_summary 8)、er003 standard_a2 27/advanced 28、er021 wiring 62、er026 post-slowdown 11、er053 c3 33/c5 10、er058 27、er063 47、er030 32 OK。er025 phase3 b1b 29件中1件ERROR(`KeyError: 'part2'`テスト固定データ不備、変更前から既存。ROOT-CAUSE-01報告でも記録済み)。 |
| 5 | 実model_id | **充足** | TTS gemini-3.8-flash-lite-tts(raw_usage_log、BATCH)、ASR gpt-4o-mini-transcribe、文章 gpt-6-luna、RF guard gpt-6-luna/gemini-3.5-flash-lite。 |
| 6 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新 | **充足(本時点の状態を記録)** | 下記SSOT節。委任_02でAdv反映・試聴版完成を記録。 |
| 7 | Git | **充足(委任_01 d43ba59c、委任_02 commitは最終報告)** | 対象のみ明示add、secret scan PASSをcommit前に実施。 |
| 8 | Dangling Reference Check | **充足** | 変更したStyle定数(P8/R2/P3)・`FAMILY_X_A2_COMMENT_4_ROLE`・`_generate_key_phrase_segments_b1`(新引数は既定"default"、他callerなし)・`overridden_segment_names`(新引数既定None)・`evaluate_segment_evidence`(新引数既定=従来)・`m3_assembly_gate`の参照元をgrep確認。`FAMILY_X_A2_COMMENT_4_ROLE`の他参照はTrial script(er057 comment4_trial)のみ。Family Z(er063)はXの`_generate_or_reuse`を呼ばない。 |
| 9 | ユーザー承認内容との一致 | **充足** | A(Comment4 2文追加のみ)、B(P3逐語)、C(R2逐語)。Full Story=P8維持(v4音声流用)、Std 6%減速、IOL=v4維持、他Role不変。新Style・別Trial案の混入なし。 |
| 10 | Production採用(APPROVED_FOR_PRODUCTION) | **ユーザー承認済み(A: Comment4 Prompt)/Style(B,C)はCoffee限定** | 全記事共通展開はOPEN-298(未決)。`FAMILY_X_A2_COMMENT_4_ROLE`はFamily X Std共通定数のため、全Std記事のComment 4に適用される(ユーザー承認A、Production定数変更)。 |
| 11 | Opus独立レビュー | **未実施** | profile機構のrole拡張は既存設計(OPEN-300条件A済み)の延長で新構造ではないと判断。`--only-segments`(生成対象絞り込みCLI)とCommentのProduction Prompt採用(条件C)のレビュー要否はFable判断。 |

## 実行層が出す所見(判定ではない)
- 試聴版(Std/Adv)は完成。Adv: 組立315.71s、peak 0.97995、clipping 0、medium/high異音(非固定)0、Playwright実再生は`PLAY_EVIDENCE_V5_01.md`。
- Gate 3の残り: 初回経路は両levelで実測済みだが、**resume(再開)経路・Master Store reuse判定・Full StoryのLocal Rewrite経路(OPEN-312)は本件で未検証**。Full Storyはv4音声流用でv5 runner経由ではない。`PRODUCTION_WIRED`判定はFable/ユーザー(Opus独立レビュー=項目11も未実施)。
