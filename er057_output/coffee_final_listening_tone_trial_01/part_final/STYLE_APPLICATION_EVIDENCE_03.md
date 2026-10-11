# STYLE_APPLICATION_EVIDENCE_03(委任_03、role×Style×prompt sha256×model_version)

最終版組立てに使った各wavのsha256(`assembly_manifest_03_final.json` provenance)が、生成時記録(01A `cost_actual_01A.json`/01B `results_01B.jsonl`/03 `generation_log_03.jsonl`)のwav sha256と一致することを確認(下表の全行 sha一致=True、Full StoryはF5 prompt sha一致)。

| role | level | Style | voice | style(prompt) sha256先頭12 | model_version | 最終版に使ったwav sha先頭12 | 由来 |
|---|---|---|---|---|---|---|---|
| Welcome | std | A5 | Charon | 2c530b21d351 | gemini-3.8-flash-lite-tts | 44f6ceb9255b | T(01A) |
| Preview intro | std | B5 | Charon | 5e28dd287f20 | gemini-3.8-flash-lite-tts | 199327468779 | T(01A) |
| Welcome | adv | A5 | Charon | 2c530b21d351 | gemini-3.8-flash-lite-tts | 44f6ceb9255b | T(01A) |
| Preview intro | adv | B5 | Charon | 5e28dd287f20 | gemini-3.8-flash-lite-tts | 199327468779 | T(01A) |
| Advanced Preview | adv | E1 | Charon | 8862317ff766 | gemini-3.8-flash-lite-tts | c7a8bb97f77d | T(01A) |
| KP英語1 | std | K2 | Aoede | 9d905cfe6c04 | (要求model=gemini-3.8-flash-lite-tts; 応答model_version未記録) | 7b667d9542b8 | T(01B) |
| KP日本語意味1 | std | M2 | Aoede | e7617e15c29e | (同上) | 940b4b6e6a56 | T(01B) |
| KP英語2 | std | K2 | Aoede | 9d905cfe6c04 | (要求model=gemini-3.8-flash-lite-tts; 応答model_version未記録) | 5b4363e66554 | T(01B) |
| KP日本語意味2 | std | M2 | Aoede | e7617e15c29e | (同上) | 0dfb3f67ac4c | T(01B) |
| KP英語3 | std | K2 | Aoede | 9d905cfe6c04 | (要求model=gemini-3.8-flash-lite-tts; 応答model_version未記録) | 46b00c613503 | T(01B) |
| KP日本語意味3 | std | M2 | Aoede | e7617e15c29e | (同上) | 537554529bdc | T(01B) |
| KP英語4 | std | K2 | Aoede | 9d905cfe6c04 | (要求model=gemini-3.8-flash-lite-tts; 応答model_version未記録) | b36b606098d2 | T(01B) |
| KP日本語意味4 | std | M2 | Aoede | e7617e15c29e | (同上) | 27bc00ef2d20 | T(01B) |
| KP英語5 | std | K2 | Aoede | 9d905cfe6c04 | (要求model=gemini-3.8-flash-lite-tts; 応答model_version未記録) | fd13e6ea5671 | T(01B) |
| KP日本語意味5 | std | M2 | Aoede | e7617e15c29e | (同上) | ae7bb24c93ea | T(01B) |
| Std preview | std | P2 | Aoede | 4ade87385824 | (同上) | 9e54868b1342 | T(01B) |
| Std comment_1 | std | P2 | Aoede | 4ade87385824 | (同上) | 8b2248d7a82d | T(01B) |
| Std comment_2 | std | P2 | Aoede | 4ade87385824 | (同上) | d94da2084ffb | T(01B) |
| Std comment_3 | std | P2 | Aoede | 4ade87385824 | (同上) | b9496509481b | T(01B) |
| Std comment_4 | std | P2 | Aoede | 4ade87385824 | (同上) | 237d2c7f584b | T(01B) |
| Full Story part3 | std | F5+6%減速 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | 178e13cdabef | R(03) |
| Full Story part1 | std | F5+6%減速 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | 590c61604404 | R(03) |
| Full Story part3 | adv | F5 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | fa1f978f68ea | R(03) |
| Full Story part1 | adv | F5 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | 5b711b91e99a | R(03) |
| Full Story part2 | std | F5+6%減速 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | 9e18c8acf88a | R(03) |
| Full Story part2 | adv | F5 | Aoede | 9228209bec75 | gemini-3.8-flash-lite-tts | 2d7c291b5abb | R(03) |
| Std topic_intro(再生成1回) | std | 既存TOPIC_INTRO(変更なし) | Aoede | d16e099cb4f6 | gemini-3.8-flash-lite-tts | 5c3de348b373 | R(03) |

一致確認: 全26項目 True

注: 01Bの生成(K2/M2/P2)はAPI応答の`model_version`を記録していない(要求modelは`gemini-3.8-flash-lite-tts`、APIが当該modelで応答した事実のみ)。01A(A5/B5/E1)と03(F5/topic)は応答`model_version=gemini-3.8-flash-lite-tts`を実測記録。