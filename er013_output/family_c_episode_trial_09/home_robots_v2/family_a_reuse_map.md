# Family A流用表(v2)

| 項目 | 流用元 | 扱い |
|---|---|---|
| Intro(SFXジングル) | p9a.INTRO_MP3_PATH(C:/Users/tensh/sound/Intro.mp3) | そのまま流用(mp3読み込みのみ) |
| Outro(SFXジングル) | p9a.OUTRO_MP3_PATH(C:/Users/tensh/sound/outro.mp3) | そのまま流用 |
| Notification(通知音、3箇所) | p9a.NOTIFICATION_MP3_PATH(C:/Users/tensh/sound/notification.mp3) | Topic intro前/Preview前/Key phrases intro前の3箇所に挿入(A2と同一位置) |
| Welcome(Charon) | B1_SHARED_NAMES welcome_charon.wav(記事非依存共有資産) | そのまま流用(コピーのみ、追加TTSなし) |
| Preview intro(Charon) | B1_SHARED_NAMES preview_intro_charon.wav | 同上 |
| Key phrases intro(Charon) | B1_SHARED_NAMES key_phrases_intro_charon.wav | 同上 |
| Full story intro(Charon) | B1_SHARED_NAMES full_story_intro_charon.wav | 同上 |
| 番号読み上げ(One.〜Five.) | B1_SHARED_NAMES num_X_charon.wav(v1で既に採用済み) | そのまま流用 |
| Topic intro文言 | er003_v1_n3_01_tts_generate.py L813 "Today's topic is {title}." | 文言パターンをそのまま採用(v1は"Home Robots"単体のみでTitle読み上げ不足の一因だった) |
| Key Phrase構成・pause | er003_b1_p9a_audio.py::build_key_phrase_block、assemble_mod.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS | そのまま流用(v1も既に流用済み) |
| Comment前後pause(1.0秒 en→ja、0.8秒 ja→en) | er003_v1_n3_01_assemble.py::build_a2_timeline pause_1.0_en_to_ja/pause_0.8_ja_to_en | Comment1〜3(Comment4は恒久的に使用しない、2026-09-15)の前後遷移にそのまま適用(v1のsupport_1/2は0.6/0.8秒でFamily A値と不一致だった) |
| Outro直前pause(0.5秒) | build_a2_timeline pause_0.5(In One Line→Outro) | Story末尾→Outroの遷移にそのまま適用(Comment4削除後、既存Family A構成どおりpause→Outroとした) |
| Assembly/Gate/player | assemble_with_timeline/apply_headroom_safety_valve/verify_episode_audio_validation_gate/audio_review_player.py | そのまま流用(無変更) |

新規Family C専用演出・新規SFXは追加していない(禁止事項どおり)。
