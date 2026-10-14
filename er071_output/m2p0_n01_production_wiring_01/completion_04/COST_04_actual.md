# COST_04_actual (委任_04、承認予算JPY25、run dir累計 上限JPY80/--budget-jpy 62)
| step | 内容 | JPY |
|---|---|---|
| Std TTS | `--stage tts --level a2 --only-segments full_story_part2,japanese_title,kp1-5_english,kp1-5_japanese_meaning`(runner実測、run dir累計 30.01 -> 34.45) | 4.44 |
| Std assemble | `--stage assemble --level a2`(API呼出なし) | 0 |
| gloss再整合(Coffee Std 記録適用) | 1呼出(gpt-6-luna、Productionの費用ログ未計測のため推定) | 約0.4 |
| gloss census replay | 5ユニークitem 1呼出(推定) | 約0.5 |
| in-line runtime evidence | `sc.run_key_phrase_canonicalization` 実LLM 1回(canonicalization+再整合、推定) | 約0.8 |
| WPM/ポーズ・Playwright・試聴ページ | ローカル/無料 | 0 |
| 合計 | 委任_04 | 約6.1(runner実測4.44 + 推定1.7)。承認予算JPY25の範囲内 |
run dir累計(runner実測): 34.45 JPY(openai 4.9 / gemini 11.5 / openai_asr 4.55 / azure 11.81 / gemini_batch 1.69)。
