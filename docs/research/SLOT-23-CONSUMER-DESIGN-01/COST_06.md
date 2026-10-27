# COST_06 F班(委任_06F)費用(実測。各runnerの累計表示−ベースrun時点の累計)
上限=Fable自律枠¥60(7-7: 承認済みScope内・案件見積300円以下)。日次1,000円枠に対する当日分は下記合計のみ(他委任分は別)。
| Family | ベース累計 | 最終累計 | 本委任の増分 | 主な内訳 |
|---|---|---|---|---|
| Y | ¥1.5892 | ¥7.9955 | **¥6.41** | KP候補抽出2level+gloss整合+確定Redundancy QA+Rescue再判定、kp_expl_b1b(Adv KP英語解説)、Part 1生成(Adv/Std+T1訳)、KP音声TTS(+ASR/Azure検証)=gemini 11呼出(Std5/Adv6)、`kp_part1_a2`再生成¥0.105 |
| Z | ¥8.3515 | ¥13.9498 | **¥5.60** | 同上(kp_part1が3回[Adv1+Std2]、T1訳)、KP音声TTS(gemini 11呼出)、`kp_part1_a2`再生成¥0.099。完成段(provision_shell/gate/assemble/pages/page_verify)は増分0 |
| X | ¥1.2595 | ¥13.49 | **¥12.23** | scaffold(KP候補+Part 1+T1訳: openai系 ¥4.81)、tts: gemini ¥4.18+ASR ¥1.63+Azure ¥1.61=¥7.42(うち**Std Full Story chunk 9呼出の再生成が約¥3.9**=逸脱1。KP音声分は約¥3.5)、assemble/player/study_text再実行=¥0 |
| 合計 | | | **約¥24.2** | Fable自律枠¥60の約40%。見積300円以下 |
- 区分: ①KP候補・解説・Part 1・T1訳(OpenAI `gpt-6-luna`)約¥14.2 / ②TTS+ASR/Azure検証 約¥10.0(Y KP音声¥1.24[b1b 0.76+a2 0.48]・Z ¥1.35[0.88+0.47]・X ¥7.42。Xは上記逸脱1を含む)。
- 呼出数(`evidence_runs/40_llm_calls_by_stage.json`): Y 52行・Z 49行・X 67行(ベース以降の増分)。`finalize`(part2_*)・`pages`・`page_verify`・dev pages・pages再実行・player再実行の増分LLM/TTS=0(cost_log行数不変で確認)。
- STOP/RESTART_STORM/Cap超過の発火なし。Y L2で予算guard(approved=10、見積5円+累計)がSTOP(API 0・承認枠をY=30/Z=40へ設定。Yの実増分は¥6.41で上限内)。
- Z L1のlegacy判定STOP、各regenerate連鎖のSTOPはAPI 0。
- 逸脱1(X Std Full Story再生成≈¥3.9)は事後報告。再発防止=TTS前に`--dry-run`で再生成対象を確認、または`--only-segments`で範囲限定。
