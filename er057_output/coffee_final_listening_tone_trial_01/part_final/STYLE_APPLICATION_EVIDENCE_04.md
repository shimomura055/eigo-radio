# STYLE_APPLICATION_EVIDENCE_04(委任_04、Advanced KP英語へのK2適用)
委任_03の`STYLE_APPLICATION_EVIDENCE_03.md`に対する差分。Advanced Key Phrase英語5件のみ変更。Standard完成版・Advanced他role(A5/B5/E1/F5/既存承認)は委任_03から不変。
K2 style(prompts_B.md K2を逐語、共通guard含む)のsha256先頭12 = **9d905cfe6c04**(Standard分K2のstyleと一致、Standard K2 results_01B style sha先頭12=9d905cfe6c04)。model要求=`gemini-3.8-flash-lite-tts`、応答model_version=`gemini-3.8-flash-lite-tts`(実測。委任_03のStd K2は応答値未記録だったため、今回分で初めて応答値を記録)。speech_metadata方式、Voice Aoede、trim margin 0.30、音量正規化はassembler gain(委任_03と同一関数 `apply_family_x_b1_gain`)。
最終版に使った各wavのsha256 = 生成時記録(`generation_log_04.jsonl`)のwav sha256: **全5件一致**。

| role | level | Style | voice | style sha256先頭12 | model_version(応答実測) | 最終版wav sha先頭12 | 生成 | 生成記録とsha |
|---|---|---|---|---|---|---|---|---|
| KP英語1 `lag` | adv | K2 | Aoede | 9d905cfe6c04 | gemini-3.8-flash-lite-tts | 20b8b303e860 | 1.16秒 / call 1回 / retry 0 | 一致 |
| KP英語2 `price tag` | adv | K2 | Aoede | 9d905cfe6c04 | gemini-3.8-flash-lite-tts | a2f5660de5bb | 1.06秒 / call 1回 / retry 0 | 一致 |
| KP英語3 `show up` | adv | K2 | Aoede | 9d905cfe6c04 | gemini-3.8-flash-lite-tts | 197f7afff745 | 1.12秒 / call 1回 / retry 0 | 一致 |
| KP英語4 `come down` | adv | K2 | Aoede | 9d905cfe6c04 | gemini-3.8-flash-lite-tts | e7a616366bbf | 1.28秒 / call 1回 / retry 0 | 一致 |
| KP英語5 `come with` | adv | K2 | Aoede | 9d905cfe6c04 | gemini-3.8-flash-lite-tts | 58602a650987 | 0.98秒 / call 1回 / retry 0 | 一致 |

- Advanced KP英語の旧音声(既存承認)sha先頭12(参考): adb32702fd9c, 3a3add6db793, 1a72df7d1100, 2f92321ba8b0, 0de94a5104fa
- Advanced英語解説(`kpN_explanation_en`)は既存承認音声のまま(sha不変)。Advanced不変role数: 24。
- 費用: 実費 約JPY 0.15(事前概算 約JPY0.3)、call 5、prompt tokens 14、candidates tokens 152。請求画面は未確認。
- 共通Styleは`APPROVED_FOR_PRODUCTION`ではない。Trial限定。
