# BUDGET_LOG_01 (FZ-NARRATION-CHUNK-TTS-TRIAL-01)

上限: 30円(ユーザー承認、委任_02)。出典=`er026_output/family_z_dev_trials/fz_narration_chunk_01/raw_usage_log.jsonl`(cost logger、`er019 runner.compute_cost_jpy_so_far`)。実費確定は各armの`gen_result_<arm>.json`の`arm_cost_jpy`。

| 日時(JST) | 起動 | 内容 | 有料API | 費用(円) | 累計(円) | 上限 |
|---|---|---|---|---|---|---|
| 2026-10-25 10:56〜11:00 | B_r1 起動1(**自己停止**) | 初回chunk(k1)のみ生成後、自プロセスのaudit hookがHuggingFace model cache(`~/.cache/huggingface/.../faster-whisper-small/refs`)への書込みを検知して停止。同時に`TTS_EXECUTION_MODE`未設定でBATCHモードだった(Z production runnerの既定STANDARDと不一致)ことも判明 | NER(gpt-6-luna)1 / Gemini **batch** TTS 1 / OpenAI ASR 1 | 0.533 | 0.533 | 30 |
| 11:04〜11:05 | B_r1 起動2 | 6 chunk(78/63,69/49,74/74語) STANDARD | Gemini TTS 6 / OpenAI ASR 7(1回のhard-case再判定を含む) / NER 1 | 4.776 | 5.308 | 30 |
| 11:06〜11:09 | A_r2 起動1 | 3 clip(141/118/148語) 1 call通し(Aと同条件の別take)。part3_c1が2 attempt(既存retry cascade) | Gemini TTS 4 / OpenAI ASR 4 / **Azure STT 1**(既存cascade) / NER 1 | 8.499 | 13.807 | 30 |
| 11:10〜11:12 | B_fine 起動1 | 9 chunk | Gemini TTS 9 / OpenAI ASR 9 / NER 1 | 4.899 | 18.706 | 30 |
| 11:12〜11:14 | B_alt 起動1 | 4 chunk(手動plan) | Gemini TTS 4 / OpenAI ASR 4 / NER 1 | 3.161 | 21.868 | 30 |
| (post) | ローカル計測・mp3・ページ | faster-whisper small(ローカル)、ffmpeg。API呼出0 | なし | 0.00 | 21.868 | 30 |

- **有料run起動回数 5回**(B_r1 2回[うち1回は自己停止]、A_r2 1回、B_fine 1回、B_alt 1回)。B_r1の再起動は、自プロセスの許可dir設定の不備(HF cache)とTTS mode未設定を自己検知した後、前回終了(11:00:01)から150秒以上空けて(11:04:04起動、約243秒後)1回だけ実施。外部停止なし、原因不明のrc≠0なし。
- 合計 **21.868円 / 上限30円(73%)**。見積(DESIGN_01 §9: 約15.6円)に対し+6.3円(A_r2のpart3_c1 retry+Azure cascade 3.5円相当、Standardの実単価が見積より高め[B_r1が見積4.3→4.78]、初回自己停止0.53円)。予約方式(見積x1.5)の最大予約でも30円を超えず、上限到達なし。
- provider別(累計): Gemini(Standard TTS) 15.89 / OpenAI ASR 3.12 / Azure 2.39 / Gemini batch 0.38(初回自己停止分) / OpenAI(NER) 0.08。**Perplexityの呼出はraw_usage_logに0件**(Ledger事前計算が全chunkで空=research対象なし)。
- 日次開発費1,000円(JST、PM_GOVERNANCE 7-9)への本件の当日加算=21.87円(他Family・並行タスク分は別)。
- 使用モデル: `gemini-3.8-flash-lite-tts`(Aと同一。最新モデル原則25節の例外理由=A/B条件同一性、DESIGN_01 §4)/ ASR=`gpt-4o-mini-transcribe`+Azure(既存Gate cascadeそのまま)/ NER=`gpt-6-luna`(RET、既存配線そのまま)。
