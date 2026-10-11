# FALLBACK_MOCK_PROBE_01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_06、API課金0)

生成: 2026-10-11 / `.venv` `python er003_fallback_style_retention_probe_01.py` / worktree `eigo-radio-tone-fb`(branch feature/coffee-new-tone-fallback-01)

方法: TTS境界(`er033...make_speech_metadata_batch_call_fn`/`..._call_fn`)のみモック。Family X audio runner(`generate_family_x_a2_segments`/`generate_family_x_b1_segments`)の実コード・実の下位関数(crosslevel/n3/voice01/news_tail_fix/repro01/review_lock)をそのまま実行し、各TTS呼び出しの `payload=(text, style)` の style(=`speech_metadata.style`)を捕捉した。ASR・Cascade判定・Local Rewrite・発音resolverはモック(スクリプト化した合否で各経路を強制発火)。`socket.connect`を遮断して実ネットワーク呼び出し0を確認。使用モデル名: 実API未使用(記録上のmodel_idは `gemini-3.8-flash-lite-tts`)。

## 結果サマリ: 全194行中 style不一致 = **0**

経路定義: A2(Standard)=標準2回(ASR不合格で次attempt)→fallback1回(承認style維持=本件)→Local Rewrite再TTS。B1B(Advanced)=同一style最大3回retry+TTS例外時のみ技術的fallback+Local Rewrite再TTS。JA(A2)にはLocal Rewrite再TTSは存在しない(英語のみ)ため regeneration 行は英語segmentのみ。

| level | 経路 | segment | phase | 対象 | 捕捉style(長い場合は先頭44字…末尾40字) | 期待一致 |
|---|---|---|---|---|---|---|
| a2 | first | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | first | japanese_title | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | preview | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | comment_1 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | comment_2 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | comment_3 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | comment_4 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | first | full_story_part1 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | first | full_story_part2 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | first | full_story_part3 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | first | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | std_retry | topic_intro | 標準retry | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | std_retry | japanese_title | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | japanese_title | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | preview | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | preview | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_1 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_1 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_2 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_2 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_3 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_3 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_4 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | comment_4 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | std_retry | full_story_part1 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | full_story_part1 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | full_story_part2 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | full_story_part2 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | full_story_part3 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | full_story_part3 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | std_retry | in_one_line | 標準retry | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | fallback | topic_intro | 標準retry | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | fallback | topic_intro | fallback | 対象外 | `natural, clear, conversational` | OK |
| a2 | fallback | japanese_title | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | japanese_title | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | japanese_title | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | preview | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | preview | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | preview | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_1 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_1 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_1 | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_2 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_2 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_2 | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_3 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_3 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_3 | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_4 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_4 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | comment_4 | fallback | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | fallback | full_story_part1 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part1 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part1 | fallback | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part2 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part2 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part2 | fallback | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part3 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part3 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | full_story_part3 | fallback | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | in_one_line | 標準retry | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | fallback | in_one_line | fallback | 対象外 | `natural, clear, conversational` | OK |
| a2 | regeneration | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | regeneration | topic_intro | 標準retry | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| a2 | regeneration | topic_intro | fallback/第3attempt | 対象外 | `natural, clear, conversational` | OK |
| a2 | regeneration | topic_intro | regeneration(Local Rewrite再TTS) | 対象外 | `natural, clear, conversational` | OK |
| a2 | regeneration | japanese_title | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | japanese_title | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | japanese_title | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | preview | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | preview | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | preview | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_1 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_1 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_1 | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_2 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_2 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_2 | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_3 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_3 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_3 | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_4 | 初回 | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_4 | 標準retry | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | comment_4 | fallback/第3attempt | JA_J2_BRIGHT | `明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽…ください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。` | OK |
| a2 | regeneration | full_story_part1 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part1 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part1 | fallback/第3attempt | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part1 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part2 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part2 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part2 | fallback/第3attempt | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part2 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part3 | 初回 | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part3 | 標準retry | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part3 | fallback/第3attempt | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | full_story_part3 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5(+減速連結) | `warm, gently upbeat and engaging; natural, f…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | in_one_line | 標準retry | 対象外 | `concise, clear, landing naturally as a settl…xaggerate pauses or sound instructional.` | OK |
| a2 | regeneration | in_one_line | fallback/第3attempt | 対象外 | `natural, clear, conversational` | OK |
| a2 | regeneration | in_one_line | regeneration(Local Rewrite再TTS) | 対象外 | `natural, clear, conversational` | OK |
| b1b | first | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | first | preview | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | first | comment_1 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | first | comment_2 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | first | comment_3 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | first | comment_4 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | first | full_story_part1 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | first | full_story_part2 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | first | full_story_part3 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | first | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | std_retry | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | std_retry | topic_intro | 標準retry | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | std_retry | preview | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | preview | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_1 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_1 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_2 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_2 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_3 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_3 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_4 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | comment_4 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | std_retry | full_story_part1 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | full_story_part1 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | full_story_part2 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | full_story_part2 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | full_story_part3 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | full_story_part3 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | std_retry | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | std_retry | in_one_line | 標準retry | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | fallback | topic_intro | 初回(標準・TTS例外) | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | fallback | topic_intro | fallback(技術的) | 対象外 | `natural, clear, conversational` | OK |
| b1b | fallback | preview | 初回(標準・TTS例外) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | preview | fallback(技術的) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_1 | 初回(標準・TTS例外) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_1 | fallback(技術的) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_2 | 初回(標準・TTS例外) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_2 | fallback(技術的) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_3 | 初回(標準・TTS例外) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_3 | fallback(技術的) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_4 | 初回(標準・TTS例外) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | comment_4 | fallback(技術的) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | fallback | full_story_part1 | 初回(標準・TTS例外) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | full_story_part1 | fallback(技術的) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | full_story_part2 | 初回(標準・TTS例外) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | full_story_part2 | fallback(技術的) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | full_story_part3 | 初回(標準・TTS例外) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | full_story_part3 | fallback(技術的) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | fallback | in_one_line | 初回(標準・TTS例外) | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | fallback | in_one_line | fallback(技術的) | 対象外 | `natural, clear, conversational` | OK |
| b1b | regeneration | topic_intro | 初回 | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | regeneration | topic_intro | 標準retry | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | regeneration | topic_intro | fallback/第3attempt | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | regeneration | topic_intro | regeneration(Local Rewrite再TTS) | 対象外 | `brief, clear, engaging news topic introducti…ral emphasis on the topic; not dramatic.` | OK |
| b1b | regeneration | preview | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | preview | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | preview | fallback/第3attempt | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | preview | regeneration(Local Rewrite再TTS) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_1 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_1 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_1 | fallback/第3attempt | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_1 | regeneration(Local Rewrite再TTS) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_2 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_2 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_2 | fallback/第3attempt | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_2 | regeneration(Local Rewrite再TTS) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_3 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_3 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_3 | fallback/第3attempt | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_3 | regeneration(Local Rewrite再TTS) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_4 | 初回 | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_4 | 標準retry | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_4 | fallback/第3attempt | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | comment_4 | regeneration(Local Rewrite再TTS) | EN_COMMENT_E2_UPBEAT | `warm, upbeat and engaging; friendly conversa…very with lively but natural intonation.` | OK |
| b1b | regeneration | full_story_part1 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part1 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part1 | fallback/第3attempt | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part1 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part2 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part2 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part2 | fallback/第3attempt | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part2 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part3 | 初回 | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part3 | 標準retry | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part3 | fallback/第3attempt | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | full_story_part3 | regeneration(Local Rewrite再TTS) | EN_FULLSTORY_F1_5 | `warm, gently upbeat and engaging; natural, f…ining clear and credible news narration.` | OK |
| b1b | regeneration | in_one_line | 初回 | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | regeneration | in_one_line | 標準retry | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | regeneration | in_one_line | fallback/第3attempt | 対象外 | `concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.` | OK |
| b1b | regeneration | in_one_line | regeneration(Local Rewrite再TTS) | 対象外 | `TTS the following complete story in natural,…sports commentator or movie trailer.\n\n` | OK |

### 期待style(正本=標準経路に実際に渡したstyle)
- JA_J2_BRIGHT: 明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。
- EN_COMMENT_E2_UPBEAT: warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.
- EN_FULLSTORY_F1_5: warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.(A2は末尾に `\n` + A2_SLOWER_PACE_INSTRUCTION を連結)
- 対象外roleのfallback: `natural, clear, conversational`(従来のFALLBACK style、変更なし)

## resume(同一out_dirの再実行)
- 保存されるstyle_version: `v5_j2_e2upbeat_f15_tone_refresh_fallback_style_retention`
- 初回run TTS呼び出し数=11 → 同一version(v5)で再実行: TTS呼び出し数=**0**(全segment reuse、期待0)
- cacheのstyle_versionを旧v4へ書換えて再実行: TTS呼び出し数=**11**(旧cacheを黙って再利用せず再生成)、全styleが承認値かつ期待一致=True、再生成segment=comment_1, comment_2, comment_3, comment_4, full_story_part1, full_story_part2, full_story_part3, in_one_line, japanese_title, preview, topic_intro

## Standard KP日本語意味(J2)・KP英語(Master Store経由)
- first: KP日本語意味 style列=['明るく、温かみのある親しみやすい話し方で。聞き手'](全てJ2逐語: True)、KP英語(shared_narration)へ渡るkwargs=['tts_backend'](fallback_style_prefixを含まない=不変)
- std_retry: KP日本語意味 style列=['明るく、温かみのある親しみやすい話し方で。聞き手', '明るく、温かみのある親しみやすい話し方で。聞き手'](全てJ2逐語: True)、KP英語(shared_narration)へ渡るkwargs=['tts_backend'](fallback_style_prefixを含まない=不変)
- fallback: KP日本語意味 style列=['明るく、温かみのある親しみやすい話し方で。聞き手', '明るく、温かみのある親しみやすい話し方で。聞き手', '明るく、温かみのある親しみやすい話し方で。聞き手'](全てJ2逐語: True)、KP英語(shared_narration)へ渡るkwargs=['tts_backend'](fallback_style_prefixを含まない=不変)

## ¥0統計(Opus B4(ii))

### 統計A: Tone Trial 2件(新tone承認時のDEV実測、Flash-Lite、speech_metadata方式)

| Trial | sample数 | status=OK | 技術retry発生(retry_count>0) | 400/空応答 | ASR不合格(EXACT/NORMALIZED以外) |
|---|---|---|---|---|---|
| tts_voice_tone_brightness_trial_01(JA J0-J3 / EN E0-E3) | 8 | 8 | 0 | 0 | 0 |
| tts_full_story_tone_trial_01(Full Story F0/F1/F1.5/F2) | 4 | 4 | 0 | 0 | 0 |

sample別(sample_id/role/voice/style種別/status/call_count/retry_count/asr_classification): 12件すべて status=OK・call_count=1・retry_count=0・ASR EXACT_MATCH or NORMALIZED_MATCH(J2_BRIGHT/E2_UPBEAT/F1.5=承認3 styleを含む)。

### 統計B: 既存Flash-Lite era記録(2026-09-27以降のreview_lock_state.json last_attempts_log、git管理分)

注意: last_attempts_logは各segmentの最終部分のみ保持。旧style(J3/E2等・承認前)での実績であり、新tone標準経路の本番runは未実施。role別の『Style起因(400/空応答/ASR不合格)の系統的失敗の兆候』の下限観測であり、完全な母集団ではない。

| level/role | segments | attempts | ASR/QA不合格 | TTS 400 | TTS 空応答 | TTS他/STOPPED | fallback発火 | HRL |
|---|---|---|---|---|---|---|---|---|
| a2/FULL_STORY | 27 | 32 | 8 | 0 | 0 | 0 | 0 | 2 |
| a2/IN_ONE_LINE | 9 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| a2/JA:meaning | 35 | 38 | 4 | 0 | 0 | 0 | 0 | 1 |
| a2/JA:preview/comment | 41 | 44 | 3 | 0 | 0 | 0 | 0 | 0 |
| a2/JA:title | 8 | 10 | 3 | 0 | 0 | 0 | 0 | 1 |
| a2/KEY_PHRASE | 37 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| a2/TOPIC_INTRO | 9 | 10 | 1 | 0 | 0 | 0 | 0 | 0 |
| a2/固定phrase/見出し/その他(Master・Heading・KP等) | 15 | 16 | 1 | 0 | 0 | 0 | 0 | 0 |
| b1b/COMMENT | 52 | 62 | 11 | 0 | 0 | 0 | 0 | 1 |
| b1b/FULL_STORY | 39 | 54 | 16 | 0 | 0 | 0 | 0 | 1 |
| b1b/IN_ONE_LINE | 13 | 15 | 2 | 0 | 0 | 0 | 0 | 0 |
| b1b/JA:preview/comment | 15 | 16 | 1 | 0 | 0 | 0 | 0 | 0 |
| b1b/KEY_PHRASE | 26 | 29 | 3 | 0 | 0 | 0 | 0 | 0 |
| b1b/PREVIEW | 13 | 15 | 2 | 0 | 0 | 0 | 0 | 0 |
| b1b/TOPIC_INTRO | 13 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| b1b/固定phrase/見出し/その他(Master・Heading・KP等) | 54 | 63 | 10 | 0 | 0 | 17 | 1 | 2 |

### 読み取り(Style起因の系統的失敗の兆候)
- 新tone標準経路(J2/E2_UPBEAT/F1.5)のTone Trial 12/12件は初回で成功(retry 0、400/空応答 0、ASR不合格 0)。承認styleそのものが標準経路で400・空応答・ASR不合格を系統的に誘発する兆候は、この少数サンプルでは観測されない。
- 既存Flash-Lite era(2026-09-27以降、a2/b1bのみ)のlast_attempts_logでは、Style起因が疑われる400 INVALID_ARGUMENT・空応答は全roleで0件(記録されたreason欄に限る)。ASR/QA不合格はrole別に存在するが(例: b1b/FULL_STORY 16/54 attempt、a2/FULL_STORY 8/32)、旧style時代の値で内容(数詞・固有名詞等)起因が主であり、新tone styleとの因果は本データからは判別不能。=『Style起因の系統的失敗の兆候』は既存データ上は観測されないが、新tone styleでの本番標準runは未実施のため確定的ではない。
- 既存Flash-Lite eraの集計(統計B)はstyle別ではなくrole別の下限観測。role別の400/空応答/ASR不合格の件数は上表。fallback発火自体が極めて少ない(設計書§1-4と一致)ため、承認style維持fallbackの救済率は**実測不能**のまま(設計書の条件付きGate『強制fallback実測probe』は別委任・少額実測の対象。本probeは¥0のstyle伝播検証のみ)。
