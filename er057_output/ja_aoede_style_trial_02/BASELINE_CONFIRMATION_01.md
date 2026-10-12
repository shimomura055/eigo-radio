# BASELINE_CONFIRMATION_01 (2026-10-12)

前回(FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01)でFinal v2に採用された日本語Style(ユーザー選択)を既存記録から確認した結果。

出典: `er057_output/coffee_final_listening_tone_trial_01/part_final/STYLE_APPLICATION_EVIDENCE_03.md`/`_04.md`、`part_BCD/prompts/prompts_C.md`・`prompts_D.md`(Prompt全文)、`part_BCD/results_01B.jsonl`(生成記録)、`part_final/FINAL_BUILD_PLAN_03.md`/`SEGMENT_PROVENANCE_03.md`。

## 適用範囲(Final v2のStandard日本語Aoede)
| role | Style | Voice | style sha256先頭12 | 最終版wav sha先頭12(本Trial基準音声のsha256と一致) |
|---|---|---|---|---|
| preview | P2 | Aoede | 4ade87385824 | 9e54868b1342 (一致) |
| comment_1 | P2 | Aoede | 4ade87385824 | 8b2248d7a82d (一致) |
| comment_2 | P2 | Aoede | 4ade87385824 | d94da2084ffb (一致) |
| comment_3 | P2 | Aoede | 4ade87385824 | b9496509481b (一致) |
| comment_4 | P2 | Aoede | 4ade87385824 | 237d2c7f584b (一致) |
| KP日本語意味1〜5 | M2 | Aoede | e7617e15c29e | 940b4b6e6a56 / 0dfb3f67ac4c / 537554529bdc / 27bc00ef2d20 / ae7bb24c93ea (全一致) |
| japanese_title | 対象外(既存承認音声のまま、sha 6e2d14e2b51b。FINAL_BUILD_PLAN_03「既存承認」) | - | - | - |

- 実測: 本Trialの `build_manifest_01.json` の `wav_sha256`(基準P2/M2は01B既存raw wavを直接参照、再TTSなし)が、上記STYLE_APPLICATION_EVIDENCE_03の最終版wav sha先頭12と全10件一致。
- model=gemini-3.8-flash-lite-tts、speech_metadata方式、Standard同期(DEV)、trim margin(日本語)0.35、language_code=ja-JP。※01B生成時はAPI応答model_versionを記録していない(STYLE_APPLICATION_EVIDENCE_03注記)。
- 原稿: Final v2 Standardのpreview/comment_1〜4とKP日本語意味5件は01B生成時と同一原稿(`a2_support_texts.json`・`keywords_canonicalized.json`を逐語、tts_safe後)。

## 基準Prompt全文(逐語)
### P2(Preview/Comment、J2+追記、166文字、sha256=4ade87385824...全体はprompts/prompt_sha256.json)
```
明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。句読点の記号そのものに反応して声の高さを変えないでください。読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。
```
### M2(KP日本語意味、67文字、sha256先頭12=e7617e15c29e)
```
一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。
```
- 参考: J2(現行Production Style JA_J2_BRIGHT)はP2の土台部分(前半約100文字)。

## 注意
- P2/M2は`APPROVED_FOR_PRODUCTION`ではなくTrial採用(Final v2はTrial限定の組立)。
