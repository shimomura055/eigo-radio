# CURRENT_STATE_01 — Y Voice定義の所在(変更前の事実、API 0)
- 構造: **固定3 Voiceのみ**(候補表構造なし)。`er121_family_y_structure_01.py:53` `FIXED_VOICE_SLOTS={"voice_1":"Algieba","voice_2":"Zephyr","voice_3":"Schedar"}`、ROSTER(同:54-)。ナレーター=Aoede(`er003_b1_p9a_audio.VOICE_NAME`を実行時に読む)。
- 整合確認: `verify_voice_assignment()`(同:68-75)が**Z表**(`er062 assign_dialogue_voices(ROSTER)`、Z男性1=Algieba)と固定割当の一致を要求していた = Z表Algiebaに依存(Puckへ変えるとSTOPする構造)。
- 呼出: runner `er121_family_y_runner_01.py:292,1390`、audio `segment_voice_map()`(`er121_family_y_audio_01.py:82`)→`voice_of_segment`。
- Algieba参照(Production経路): structure_01.py:11(コメント)/:53(値)、audio_01.py:13(コメント)。testは runner_01_test_01.py:231,534、structure_match_test_01.py:239、audio_chunk_test_01.py:323(旧Voiceキャッシュ破棄の入力値=fixture、変更不要)。
- DEV Trial(`er110_family_y_*`)・docs/research履歴・`user_test`はTrial成果物=履歴(変更しない)。Z(`er062`:50,95 / `er063`)はAlgiebaを維持(変更禁止)。
- evidence slug: `redelivery_fee`(公開済み、run_01あり)。
