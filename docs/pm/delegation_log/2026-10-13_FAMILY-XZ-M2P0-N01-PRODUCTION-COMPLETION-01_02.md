# FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02 (要点保存、T-0)
ユーザー指示原文は委任_01保存分 `2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_01.md` 参照。
## 性質/上限
承認済み仕様(M2P0・N01・Coffee限定Style profile coffee_n01_r2_p3)の正式Production完成。到達上限Status=PRODUCTION_WIRED(Checklist 12項目充足かつDangling Reference Check済みのみ)。費用上限 JPY35(ハードストップ38)、Coffee run dir累計上限JPY80(現26.77)→ --budget-jpy 61。見積はCOST_PLAN_02.md。
## 禁止
Rule7/Audio Validation Gate/M3/M4/ASR Gate緩和迂回、未検証segment機械PASS、承認済みPrompt/Style実質変更、HR Lock迂回、承認捏造、STOPPED等の自己承認、不要segment再生成、Family Z変更、er006_*/er011_*編集、git add -A/-f、amend/rebase/force push、stash/clean/reset --hard、.env、wav/telemetry/log/words add、ACTIVE_TASK/RESULT_PACKET commit、外部プロセス再起動、有料runのkill、監督ループ、既存artifact削除。
## STOP条件
canonicalization REVIEW_REQUIRED/INVALID再発、TTS STOPPED/HUMAN_REVIEW_LOCKED/ASR_VALIDATION_UNCERTAIN、M3/M4 BLOCK、予算/retry上限超過、Adv style承認状態確定不可、新しい許容ルールが必要。
## Opusレビュー反映 (OF-X1〜X13)
是正①: X1 左端ガード(拡張span内一致開始が元span内)/X2 \b regex/追加test(3語停止、span_corrected_in_restore、role=topic)/X3 expansion_census_02.md/X13 japanese_gloss整合確認。
是正②: X4 --apply時expected_text必須(自動導出)/X5 source_style_version+cross_version_accepted_by記録/X6 F1後再判定(offline)/X7 trimmed_duration witness/X8 Std a2 8 segment復元計画/X9 明示無効化CLI er019_family_x_segment_invalidate_01.py(INVALIDATED_FOR_REGENERATION)/X11 非選択は status問わずsha一致で持ち越し/X12 追加test。
Adv(X10): Adv style事実確認→(i)e_tone_01 style承認一致→seed+引継ぎ (ii)不一致かつmain承認一致→再生成 (iii)両不一致→STOP。ADV_STYLE_FACTCHECK_02.md。
## 有料run手順
0 results復元+Part2無効化+Gate dry-run / 1 Std KP canonicalization(--scaffold-only kp) / 2 Std a2 --only-segments key_phrases,full_story_part2 / 3 Adv b1b / 4 両level assemble / 5 試聴ページ user_test/coffee_m2p0_n01_final_02/ / 6 Checklist12+Dangling Check。
SSOT最後: CURRENT_SPEC/OPEN-343,346,310,347/DECISION_LOG/UDR #47,#49,#50/REPORT_LEDGER/OPUS_FINDINGS_LEDGER。
Managed-ID trailer必須。報告10項目はRESULT_PACKET_XZC.md。
