# HR_APPROVAL_STD_PREVIEW_01 — Std preview Take 1 のHuman Review PASS確定(委任_06)
管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_06。実施: 2026-10-27(JST 09:03)。
## 1. 承認(原文)
`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_03.md` §1(逐語): 「Standard Previewについて、Take 1を承認します。対象音声 std_hr/std_preview_take1.mp3 … 原稿『思いどおりに』とASR『思い通りに』の差異を確認したうえで、ユーザーは当該音声を問題なしと判断しました。この1 segmentをHuman Review PASSとして正式確定してください。」
## 2. 対象
level=a2(Standard) / segment=`preview`(日本語要約) / take 1(route `custom_06ec49ff` = 承認Style S3)。
- 採用wav sha256 `ac3f7467…2f3a`(`attempts/preview_attempt1_custom06ec49ff.wav`、attemptsの記録shaと一致)。公開試聴mp3 `std_hr/std_preview_take1.mp3`(sha先頭 5a85d1ba)。
- canonical_text_sha256 `dc4068f8…1afb08`。
- 原稿「…思いどおりに届かない…」 / OpenAI ASR「…思い通りに届かない…」(読みは同じ表記ゆれのみ。Azureも同様、HR_PACKET_STD_PREVIEW_01 根拠(1))。attempt判定 `ASR_VALIDATION_UNCERTAIN`(=人間判断対象)。
## 3. 実施手順(正規経路のみ。Gate緩和・Lock直接編集なし)
1. `tools/hr_adopt_style_fix_01.py --level a2 --segment preview --take 1 --dry-run`: adoptable=true、lock `HUMAN_REVIEW_REQUIRED`、preview entry `SKIPPED_NOT_SELECTED`をattemptsから復元予定(OPEN-552)、API 0。
2. 同 `--apply --user-statement-ref docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_03.md`(rc=0)。
結果: `a2/audit/human_approved_segments.json` に preview(approved_by=user、2026-10-27T09:03:59)、`review_lock_state.json` preview=RESOLVED/HUMAN_APPROVED、`tts_generation_results.json` preview entry復元(Style実測・adopted_*)、記録 `a2/audit/ysp5_user_approval_record_preview.json`(scope=this single segment/this take only、一般ASR免除ではない)。旧preview.wavは`preview.pre_ysp5_adopt.wav`、lock/resultsはbackup(`*.pre_ysp5_adopt_backup.json`)に退避。
## 4. y_voice_1(Voice 1) 状態
take 4(Fable許可再生成、承認Style PD06、OpenAI `was`)+6%減速後ASR PASS。lock `y_voice_1`=RESOLVED/OK(自動PASS、HR不要)。今回変更なし。
## 5. 判定
PASS理由=ユーザーの明示承認(1 segment・1 take限定)。TTS/ASR API呼出 0。
