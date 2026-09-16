# Family A流用表(Digital Twins A2、Trial-12)

| 項目 | 流用元 | 扱い |
|---|---|---|
| Intro/Outro/Notification(SFXジングル) | p9a.INTRO/OUTRO/NOTIFICATION_MP3_PATH | そのまま流用 |
| Welcome/Preview intro/Key phrases intro/Full story intro(Charon) | B1_SHARED_NAMES(共有ソース) | そのまま流用 |
| 番号読み上げ(One.〜Five.) | B1_SHARED_NAMES num_X_charon.wav | そのまま流用 |
| Topic intro(EN)/Japanese title/Preview(JA)/Key Phrase英語・日本語音声 | Trial-10 twins_a2/audio(コピー、再TTSなし) | 本文・テキスト不変のため再生成不要 |
| Story segment(22件、narrator/twin) | Trial-10 twins_a2/audio(byte-identicalコピー、再TTSなし) | 新旧segmentation完全一致のためreuse(本タスクの主要な発見、RESULT_PACKET参照) |
| Key Phrase選定・canonicalization | Trial-10 twins_a2/key_phrases(コピー) | 再選定なし |
| Comment 1〜3(日本語) | 新規生成(Trial-12 Comment Prompt、英文理解ガイド役割) | 本タスクの唯一の新規TTS対象 |
| Assembly/Gate/player | assemble_with_timeline/apply_headroom_safety_valve/verify_episode_audio_validation_gate/audio_review_player.py | そのまま流用(無変更) |
| Voice(narrator=Aoede、digital twin Echo=Erinome) | er012_b_family_voices_production_01 | Trial-10から無変更 |

新規Family C専用演出・新規SFXは追加していない(禁止事項どおり)。
