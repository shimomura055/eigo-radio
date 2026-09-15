# Family A流用表(memory A2、Trial-11)

| 項目 | 流用元 | 扱い |
|---|---|---|
| Intro(SFXジングル) | p9a.INTRO_MP3_PATH | そのまま流用(mp3読み込みのみ) |
| Outro(SFXジングル) | p9a.OUTRO_MP3_PATH | そのまま流用 |
| Notification(通知音、3箇所) | p9a.NOTIFICATION_MP3_PATH | Topic intro前/Preview前/Key phrases intro前の3箇所に挿入(Trial-10と同一位置) |
| Welcome(Charon) | Trial-10 memory_a2/audio/welcome.wav(コピー、再TTSなし) | そのまま流用 |
| Preview intro(Charon) | B1_SHARED_NAMES preview_intro_charon.wav | 同上 |
| Key phrases intro(Charon) | B1_SHARED_NAMES key_phrases_intro_charon.wav | 同上 |
| Full story intro(Charon) | B1_SHARED_NAMES full_story_intro_charon.wav | 同上 |
| 番号読み上げ(One.〜Five.) | B1_SHARED_NAMES num_X_charon.wav | そのまま流用 |
| Topic intro(EN)音声/Japanese title音声/Preview(JA)音声/Key Phrase英語・日本語音声 | Trial-10 memory_a2/audio(コピー、再TTSなし) | 本文・テキストは無変更のため再生成不要。再TTS対象はStory segment全件+Comment 1〜3のみ |
| Key Phrase選定・canonicalization | Trial-10 memory_a2/key_phrases(コピー) | 再選定なし |
| Comment前後pause(1.0秒 en→ja、0.8秒 ja→en) | er003_v1_n3_01_assemble.py::build_a2_timeline pause_1.0_en_to_ja/pause_0.8_ja_to_en | Comment1〜3の前後遷移にそのまま適用(Trial-10と同一) |
| Outro直前pause(0.5秒) | build_a2_timeline pause_0.5(In One Line→Outro) | Story末尾→Outroの遷移にそのまま適用 |
| Assembly/Gate/player | assemble_with_timeline/apply_headroom_safety_valve/verify_episode_audio_validation_gate/audio_review_player.py | そのまま流用(無変更) |
| Voice(Charon=装置、Algieba=兄) | er012_b_family_voices_production_01/er003_v1_sing01_voice01_generate | Trial-11変更点: 兄voiceのみErinome→Algiebaへ変更(既存承認Voice候補の範囲内、ピッチ推定に基づく選定)。装置Voice(Charon)は無変更 |

新規Family C専用演出・新規SFXは追加していない(禁止事項どおり)。
