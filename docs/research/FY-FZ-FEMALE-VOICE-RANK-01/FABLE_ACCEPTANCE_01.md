# FABLE_ACCEPTANCE_01 FY-FZ-FEMALE-VOICE-RANK-01 (2026-10-29)

## 受入記録:
### (1) ユーザー原文(`docs/pm/delegation_log/2026-10-29_FY-FZ-FEMALE-VOICE-RANK-01_USER.md` §4)
- :92 「**Family Y／Family Z、Standard／Advancedの全4組み合わせ。**」
- :98-102 順位 1 Leda / 2 Erinome / 3 Sulafat / 4 Kore / 5 Zephyr
- :104 「**男性Voice候補は一切変更しません。**」
- :113 「既存の完成音声・ユーザー承認済みVoice割当は無断変更しない。」
- :115 「特定Voiceを明示指定する既存の配役仕様は、単なる順位変更を理由に上書きしない。」
- :132 「**全4組み合わせで確認できた場合のみPRODUCTION_WIREDとしてください。**」

### (2) 最終成果物
- 実装: `er121_family_y_structure_01.py:58-66,76-130`(Y女性表・FIXED_VOICE_SLOTS・resolve_voice_slots/voice_assignment_record)、`er062_family_z_structure_01.py:49-52,105-135`(Z女性表・STORY_VOICE_PINS)、run dirの`voice_assignment.json`記録優先、既存Y16run・Z46run不変(`evidence/api0_unchanged_check_01.json`、diff 0)、『藪の中』(in_a_grove)ほか既存4作品の女性は旧Voice(Zephyr/Kore)pin(制作中・既存記事の混在防止、Fable承認)。commit ef740d530・dfebe17aa+本委任commit。
- 失敗経路: 委任_01のscratch copy-run自己誘発RESTART_STORM STOP(API 0、Fable権限で`--clear-stop`解除済み、`evidence/y/run_launch_log.jsonl` CLEARED行)。既存記事・公開物・完成音声は無変更。

### (3) 証拠
| 組合せ | tts_voice_sent | model_id | Style/routing | 費用 | 出典 |
|---|---|---|---|---|---|
| Z Std | Leda | gemini-2.5-pro-preview-tts | er063 dialogue既定 STANDARD | 約0.5円 | evidence/z/cost_log.jsonl |
| Z Adv | Leda | gemini-2.5-pro-preview-tts | slowdown 6% | 約2円 | 同上 |
| Y Std | Leda | gemini-3.8-flash-lite-tts | speech_metadata_flash_lite, STANDARD | 約1.56円 | evidence/y/cost_log.jsonl 1行目(2026-10-29T09:16:29Z)、ASR一致 |
| Y Adv | Leda | gemini-3.8-flash-lite-tts | speech_metadata_flash_lite | 約1.39円(Y累計2.94円) | evidence/y/cost_log.jsonl 4行目(09:20Z台)、ASR一致 |
- test: 関連294+新規9 PASS(他要因失敗3件は本件無関係、EVIDENCE_01参照)。
- FIXED_VOICE_SLOTS=候補表からの導出(a): `er121_family_y_structure_01.py`の`verify_voice_assignment`が`assign_dialogue_voices(ROSTER, pool=Y_DIALOGUE_VOICE_POOL)`との一致を強制(明示配役仕様ではない)。Z明示pin(メロス・告げ口心臓Narrator)は不変。

### (4) 項目ごと一致
| 項目 | 結果 |
|---|---|
| 全4組合せ(Y/Z x Std/Adv)実送信 | 一致(全てLeda) |
| 順位 | 一致 |
| 男性不変 | 一致(test固定) |
| 既存記事Voice不変 | 一致(api0_unchanged_check_01、Y16/Z46) |
| 明示pin維持 | 一致(Z melos/告げ口心臓) |
| retry/resume整合 | 一致(voice_assignment記録優先・input sha変更でprovenance STOP→regenerate) |
| SSOT | OPEN-606/ACTIVE_TASK/DECISION_LOG更新 |

### (5) 判定
4組合せのevidenceが揃い、本件起因の失敗なし(自己誘発STOPはAPI 0・解除済み)。**ACCEPTED=PRODUCTION_WIRED**。
Y run_fvr_ev_01はscratch copy-run(公開物でなくgit管理外)。

判定整合: 重大NG=なし / 主因=なし / 是正対象=なし / STOP理由=[RESTART_STORM(自起動・解除済み)] / 提示=可
