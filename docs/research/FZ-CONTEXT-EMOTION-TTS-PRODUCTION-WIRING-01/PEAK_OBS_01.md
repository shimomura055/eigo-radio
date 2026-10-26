# PEAK_OBS_01 — ctx音声のpeak分布観測(E-1、新基準ではない)

出典=`peak_obs_01.json`(`tools/fzcw_peak_obs_01.py`が`run_fzcw_e1_01`の最終narration wavとattempt wavを読む)。`check_clip_audio_quality`の`peak_max=0.999`との比較のみ。

| level | 対象 | n | min | median | max | >0.999 | >=0.999 |
|---|---|---|---|---|---|---|---|
| a2 | ctx dialogue最終wav | 10 | 0.69992 | 0.69992 | 0.69992 | 0 | 0 |
| a2 | 非dialogue最終wav | 38 | 0.69214 | 0.69992 | 0.69992 | 0 | 0 |
| a2 | ctx attempt wav(生成直後) | 11 | 0.69992 | 0.69992 | 0.69992 | 0 | 0 |
| b1b | ctx dialogue最終wav(減速後) | 11 | 0.69882 | 0.69907 | 0.69989 | 0 | 0 |
| b1b | 非dialogue最終wav | 34 | 0.69992 | 0.69992 | 0.69992 | 0 | 0 |
| b1b | ctx attempt wav | 11 | 0.69992 | 0.69992 | 0.69992 | 0 | 0 |

- 観測: ctx音声のpeakは既存のpeak正規化(`normalize_pcm`、約0.70)に載り、`peak_max=0.999`超過は**0件**。ctx方式でpeakが従来より高くなる傾向は観測されなかった(非dialogue clipと同一分布)。
- 組立(assembly headroom): a2 `scalar=1.0`(applied=false, peak_before=0.9505, 原因piece=key_phrase_1)、b1b `scalar=1.0`(applied=false, peak_before=0.95, 原因piece=Intro)。ctx dialogueが原因pieceになっていない。
- 強制NG runのpeak観測は対象外(E-1のみ)。聴取評価は未実施(自動QAのみ)。
